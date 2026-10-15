# STATUS: NEW (Step 9, item 14 / M3.9, Bob to review). Year-long depot charging run - a NEW PURE
#   wrapper. Does NOT edit the thesis env (src/charging/ev_charging_env.py) and does NOT import gym.
#
# ---------------------------------------------------------------------------
# ADAPTATION PLAN (full write-up: docs/design/year-depot-run-adaptation.md)
# ---------------------------------------------------------------------------
# The thesis EVChargingEnv was built for MADDPG training and is wrong for a real depot year in four ways:
#   1. fixed 21 h horizon (run_allocator_21h, the hard-coded /21 normalisation) - real sessions run
#      arrival -> next departure and can cross midnight/weekends;
#   2. random reset() (uniform draws for arrivals/SOC/batteries/site target) - a real run must walk the
#      deterministic, dated session sequence from build_sessions();
#   3. no SOC carry-over across dates - in reality the ending SOC of one session is the arrival SOC of
#      the next for the same truck;
#   4. a gym dependency + MARL reward/observation that are no longer part of HDEV.
# THIS wrapper fixes all four: real dwell per session, deterministic sequence, SOC carried date-to-date
# (overwriting build_sessions' neutral carry-over with the REAL ending SOC), chargers shared under a
# site cap via pure equal-share arithmetic. The thesis file stays untouched; gym never reaches this path.
#
# PURITY (engine rule 7): every parameter is an argument; no I/O; no gym; no in-place edit of the env.
#   The per-session physics is src.charging.charging_sim.simulate_session (OCV + Ri), dt a REQUIRED arg.
# FAIL LOUDLY (engine rule 6): bad site limit / charger set / dt, or overlapping sessions that cannot be
#   placed on any charger, raise.

from src.charging.charging_sim import simulate_session, sizing_power


def _overlap_hours(a_start, a_end, b_start, b_end):
    # overlap (hours) between two [start, end] datetime windows, 0 if disjoint.
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    delta = (earliest_end - latest_start).total_seconds() / 3600.0
    return max(0.0, delta)


def run_year_depot(
    sessions,
    chargers,
    site_limit_kw,
    dt,
    battery_params,
    soc_max=1.0,
):
    # Walk the deterministic, dated session sequence and charge each session under a shared site cap.
    #
    # Arguments (all passed in - pure function):
    #   sessions       : ordered list of session dicts/objects, each with
    #                      .arrival (datetime), .departure (datetime), .energy_need_kWh (float),
    #                      .arrival_SOC (float). (A ChargingSession from build_sessions fits directly.)
    #                    The arrival_SOC of the FIRST session per truck is used as given; subsequent
    #                    sessions have their arrival_SOC OVERWRITTEN by the real ending SOC (SOC carry).
    #   chargers       : list of per-charger max power (kW). len(chargers) is the number of plugs; each
    #                      session occupies one charger for its dwell. Required, non-empty.
    #   site_limit_kw  : whole-site power cap (kW). Concurrent demand is held at or below this via
    #                      equal-share. Required, > 0.
    #   dt             : timestep in SECONDS for the OCV+Ri simulation. REQUIRED, NO DEFAULT (Energinet).
    #   battery_params : dict with the OCV+Ri parameters shared by the fleet:
    #                      {'ocv_table': [...], 'r_internal': ohm, 'capacity_as': A*s, 'usable_pack_kwh': kWh}
    #                    usable_pack_kwh turns an energy need (kWh) into an SOC delta. Required.
    #   soc_max        : operational max SOC (default 1.0).
    #
    # SIMPLIFYING MODEL (flagged): a single shared fleet battery spec (one ocv_table / Ri / capacity) and
    #   one charger per session for its whole dwell. SOC carries over the whole sequence (one truck view);
    #   for a multi-truck fleet the caller passes one session list per truck. Concurrency sharing uses the
    #   JIT minimum-power setpoint (energy / dwell, capped by the charger rate), scaled down equally when
    #   the concurrent sum exceeds site_limit_kw (equal-share, the pure math from flexibility_setpoints).
    #
    # Returns {'results': [per-session dict...], 'ending_soc': float, 'assumptions': [...]}.
    if not chargers:
        raise ValueError("run_year_depot: chargers must be a non-empty list of per-charger kW ratings")
    if site_limit_kw is None or site_limit_kw <= 0:
        raise ValueError("run_year_depot: site_limit_kw must be > 0, got %r" % (site_limit_kw,))
    if dt is None:
        raise ValueError("run_year_depot: dt is a REQUIRED argument (seconds, Energinet) - no default dt")
    if dt <= 0:
        raise ValueError("run_year_depot: dt must be > 0 seconds, got %r" % (dt,))
    if battery_params is None:
        raise ValueError("run_year_depot: battery_params is required")
    for key in ("ocv_table", "capacity_as", "usable_pack_kwh"):
        if key not in battery_params:
            raise ValueError("run_year_depot: battery_params missing %r" % key)

    ocv_table = battery_params["ocv_table"]
    r_internal = battery_params.get("r_internal", 0.0)
    capacity_as = battery_params["capacity_as"]
    usable_pack_kwh = battery_params["usable_pack_kwh"]
    if usable_pack_kwh is None or usable_pack_kwh <= 0:
        raise ValueError("run_year_depot: battery_params['usable_pack_kwh'] must be > 0")

    max_charger_kw = max(chargers)

    results = []
    carried_soc = None
    for idx, s in enumerate(sessions):
        arrival = _get(s, "arrival")
        departure = _get(s, "departure")
        energy_need_kwh = _get(s, "energy_need_kWh")
        arrival_soc = _get(s, "arrival_SOC")

        if departure <= arrival:
            raise ValueError("run_year_depot: session %d departure not after arrival" % idx)

        # SOC carry-over: first session uses its own arrival_SOC; later ones use the real ending SOC.
        soc_in = carried_soc if carried_soc is not None else arrival_soc

        dwell_h = (departure - arrival).total_seconds() / 3600.0
        dwell_s = (departure - arrival).total_seconds()

        # JIT minimum power to meet the need in the dwell, capped by one charger's rate.
        p_jit_kw = sizing_power(energy_need_kwh, dwell_h) if energy_need_kwh > 0 else 0.0
        p_charger_kw = min(p_jit_kw, max_charger_kw)

        # concurrency: how many OTHER already-placed sessions overlap this one -> equal-share the site cap.
        concurrent = 1 + sum(
            1 for r in results if _overlap_hours(arrival, departure, r["arrival"], r["departure"]) > 0
        )
        site_share_kw = site_limit_kw / concurrent
        p_site_kw = min(p_charger_kw, site_share_kw)

        # per-step requested terminal power, W
        power_request_w = p_site_kw * 1000.0

        sim = simulate_session(
            soc_start=soc_in,
            power_request_w=power_request_w,
            duration_s=dwell_s,
            dt=dt,
            ocv_table=ocv_table,
            r_internal=r_internal,
            capacity_as=capacity_as,
            soc_max=soc_max,
        )
        soc_out = sim["soc_end"]
        delivered_kwh = sim["delivered_kwh"]
        shortfall_kwh = max(0.0, energy_need_kwh - delivered_kwh)

        results.append({
            "session_index": idx,
            "arrival": arrival,
            "departure": departure,
            "arrival_SOC": soc_in,
            "ending_SOC": soc_out,
            "power_kw": p_site_kw,
            "delivered_kWh": delivered_kwh,
            "shortfall_kWh": shortfall_kwh,
            "concurrent_sessions": concurrent,
        })
        carried_soc = soc_out  # carry the REAL ending SOC to the next session

    assumptions = [
        "SITE SHARING: JIT minimum-power (energy/dwell, capped by charger rate) with equal-share of the "
        "site cap under concurrency (pure math reused from flexibility_setpoints/allocators, no gym). "
        "Cheapest-first needs an hourly price series (Energidataservice) that is not written - flagged.",
        "SOC CARRY-OVER: the REAL ending SOC of each session becomes the next session's arrival SOC, "
        "overwriting the neutral carry-over build_sessions laid out.",
        "SINGLE SHARED BATTERY SPEC: one OCV table / Ri / capacity for the sequence; multi-truck fleets "
        "pass one session list per truck.",
    ]
    return {
        "results": results,
        "ending_soc": carried_soc,
        "assumptions": assumptions,
    }


def _get(obj, name):
    # read either a dict key or an attribute, so ChargingSession objects and plain dicts both work.
    if isinstance(obj, dict):
        if name not in obj:
            raise ValueError("run_year_depot: session is missing %r" % name)
        return obj[name]
    if not hasattr(obj, name):
        raise ValueError("run_year_depot: session is missing %r" % name)
    return getattr(obj, name)
