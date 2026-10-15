# STATUS: NEW (PR 4, Bob to review). the DEMO scenario engine - run_scenario(project, levers).
#
# this module ports the "ILLUSTRATIVE NUMBERS ONLY" <script> block of
# docs/design/ui-mockup/fleet-assistant-demo.html (the authoritative mock-up materialized in FEAT-001)
# into Python, VERBATIM. the mock-up's scen()/model() maths is the exact source of every formula and
# constant here - no new formulas are invented. the figures are placeholders; do NOT read any output
# as a real engineering number.
#
# §0 / §7 illustrative rule: every results dict carries illustrative=True and mode="demo", and every
# number in it is an illustrative stand-in. the real engine (§6) lands in Step 9; real mode never calls
# this module (hdev/run_api.py returns a not-yet-available payload instead).
#
# §8 method-hiding, enforced AT THE BOUNDARY of this module:
#   - the mock-up's internal priority keys cost / grid / early live ONLY inside this file. they are
#     mapped to the CLIENT-FACING names lowest_cost / grid_friendly / ready_earliest on the way in
#     (settings) and on the way out (settings.charging_priority and every strategies[].priority).
#   - verdict/plan/headline text uses PLAIN words only: no coefficient, parameter, physics-source or
#     technical-strategy name (ASAP/JIT/EDF/ES/cost-based) ever appears in a client-facing string.
#   - owner is referred to only as "Bob" (none appears in the output; noted for completeness).
#
# purity: run_scenario is a pure, deterministic, offline function of (project, levers). no network, no
# AI provider, no hidden globals, no clock-dependence except an explicit ISO timestamp field (which is
# derived deterministically from the resolved settings so repeated runs with the same inputs match).
#
# §3.3 additive extension (FEAT-002): the results dict carries two extra top-level fields,
# working_days (the working-days-per-truck count the illustrative maths already uses, 250) and
# truck_days_simulated (fleet_size * working_days). these feed the §5.3 state-4 run screen's
# "N truck-days simulated" line so the browser never hard-codes 250. §3.3 is otherwise intact:
# nothing is removed or reordered, this is purely additive.
import hashlib
import math
from typing import Any, Dict, List, Mapping, Optional

# ---------------------------------------------------------------------------
# §8 boundary mapping: internal priority key <-> client-facing name.
# the internal keys (cost/grid/early) are the mock-up's; they NEVER leave this module.
# ---------------------------------------------------------------------------
_CLIENT_TO_INTERNAL = {
    "lowest_cost": "cost",
    "grid_friendly": "grid",
    "ready_earliest": "early",
}
_INTERNAL_TO_CLIENT = {v: k for k, v in _CLIENT_TO_INTERNAL.items()}

# available charger sizes (kW), smallest first - verbatim from the mock-up SIZES.
SIZES = (22, 40, 50, 60, 90, 120, 150)

# lever -> internal factor tables (verbatim from the mock-up).
_PRICE_F = {"low": 0.8, "expected": 1.0, "high": 1.25}      # price factor; client values low|expected|high
_PRIO_F = {"cost": 0.85, "grid": 0.92, "early": 1.0}        # priority cost factor
_COINC = {"cost": 0.95, "grid": 0.75, "early": 1.0}         # coincidence factor

# demo defaults when a lever is absent from the request body.
_DEFAULT_FLEET_SIZE = 6          # the sample case is a 6-truck municipal refuse fleet
_DEFAULT_PRIORITY = "lowest_cost"
_DEFAULT_PRICE = "expected"
_DEFAULT_WEATHER = "normal"
_DEFAULT_YEARS = 10
_DEFAULT_SHIFT_END_HOUR = 15     # fixture shift_end "15:00" -> hour 15 (mock-up default se=15)

# working days per truck per year baked into the illustrative energy/cost maths (the literal 250 the
# mock-up used in energy_yr = n * mean * 250 and diesel_l = n * 120 * 250 * 0.55). named here so there
# is a single source of truth; it also feeds the additive working_days / truck_days_simulated fields.
_WORKING_DAYS_PER_YEAR = 250


def _round_half_up(x: float) -> int:
    # JS Math.round is round-half-up (ties go to +infinity); Python's round() is banker's rounding, which
    # would flip some ported values by one. this helper matches the mock-up so values AND direction agree.
    return int(math.floor(x + 0.5))


def _first_size_ge(need: float) -> int:
    # first charger size that covers `need`, else the biggest (mock-up: SIZES.find(x => x >= need) || 150).
    for size in SIZES:
        if size >= need:
            return size
    return 150


def _shift_end_hour(project: Optional[Mapping[str, Any]], levers: Mapping[str, Any]) -> int:
    # resolve the shift-end hour (se). the editable registry field operation.schedule.shift_end carries a
    # "HH:MM" string ("15:00" in the fixture). accept it from the levers body (lever target) or the
    # project, else fall back to the demo default 15. an int is accepted as-is.
    raw = None
    if "operation.schedule.shift_end" in levers:
        raw = levers["operation.schedule.shift_end"]
    elif "shift_end" in levers:
        raw = levers["shift_end"]
    elif project:
        raw = project.get("shift_end")
    if raw is None:
        return _DEFAULT_SHIFT_END_HOUR
    if isinstance(raw, bool):
        return _DEFAULT_SHIFT_END_HOUR
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.strip():
        # "HH:MM" or "HH" -> hour integer.
        head = raw.strip().split(":", 1)[0]
        try:
            return int(head)
        except ValueError:
            return _DEFAULT_SHIFT_END_HOUR
    return _DEFAULT_SHIFT_END_HOUR


def _resolve_settings(project: Optional[Mapping[str, Any]], levers: Mapping[str, Any]) -> Dict[str, Any]:
    # pull the levers off the request body with demo defaults (mirrors the mock-up scen()). values are
    # CLIENT-FACING here; the internal priority key is derived separately.
    project = project or {}
    levers = levers or {}

    fleet_size = levers.get("fleet_size", project.get("fleet_size", _DEFAULT_FLEET_SIZE))
    if isinstance(fleet_size, bool) or not isinstance(fleet_size, int) or fleet_size < 1:
        fleet_size = _DEFAULT_FLEET_SIZE

    priority = levers.get("charging_priority", _DEFAULT_PRIORITY)
    if priority not in _CLIENT_TO_INTERNAL:
        priority = _DEFAULT_PRIORITY

    price = levers.get("electricity_price", _DEFAULT_PRICE)
    if price not in _PRICE_F:
        price = _DEFAULT_PRICE

    weather = levers.get("weather_year", _DEFAULT_WEATHER)
    if weather not in ("normal", "cold_winter"):
        weather = _DEFAULT_WEATHER

    years = levers.get("ownership_years", _DEFAULT_YEARS)
    if years not in (8, 10, 12):
        years = _DEFAULT_YEARS

    se = _shift_end_hour(project, levers)

    return {
        "fleet_size": fleet_size,
        "charging_priority": priority,     # client-facing
        "electricity_price": price,
        "weather_year": weather,
        "ownership_years": years,
        "shift_end": f"{se:02d}:00",
        "_se": se,                          # internal hour, stripped before output
    }


def _inputs_summary() -> Dict[str, int]:
    # inputs_summary is registry/fixture-derived, NOT a literal: reuse the intake tallies so the four
    # numbers agree with /api/intake and /api/inputs. imported lazily to avoid an import cycle at
    # module load (hdev.intake_api imports from src.registry only, but keep this local and cheap).
    from hdev.intake_api import build_intake_payload

    totals = build_intake_payload("demo")["totals"]
    return {
        "from_data": totals["from_data"],
        "standard": totals["standard"],
        "missing": totals["missing"],
        "total": totals["total"],
    }


def run_scenario(project: Optional[Mapping[str, Any]], levers: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    # port of the mock-up model(scen()). pure/deterministic/offline. returns the §3.3 results dict with
    # illustrative=True, mode="demo", and the internal priority keys mapped to client-facing names.
    settings = _resolve_settings(project, levers or {})
    n = settings["fleet_size"]
    prio = _CLIENT_TO_INTERNAL[settings["charging_priority"]]   # internal key, used for the maths only
    price = settings["electricity_price"]
    weather = settings["weather_year"]
    years = settings["ownership_years"]
    se = settings["_se"]
    Y = years

    # ----- seasonal monthly shape (12 months); cold winter raises the winter months -----
    month_f = [1.18, 1.16, 1.08, 1.0, 0.95, 0.92, 0.92, 0.93, 0.96, 1.02, 1.1, 1.16]
    if weather == "cold_winter":
        for i in range(12):
            if i < 2 or i > 9:
                month_f[i] *= 1.08

    avg = 180
    months = [avg * f for f in month_f]
    mean = sum(months) / 12
    worst = max(months) * 1.15

    # battery sizing (kWh), rounded up to nearest 10.
    battery = math.ceil(worst * 1.25 / 10) * 10

    # charging window hours by priority.
    hours = {"cost": 7, "grid": (30 - se) - 2, "early": 4}[prio]
    need = worst / hours * 1.1
    kw = _first_size_ge(need)

    coinc = _COINC[prio]
    base = 30     # base site load (kW)
    limit = 400   # grid connection limit (kW)
    peak = _round_half_up(base + n * kw * coinc)

    price_f = _PRICE_F[price]
    prio_f = _PRIO_F[prio]
    elec_day = 1.6 * price_f * prio_f

    # annual energy and costs.
    energy_yr = n * mean * _WORKING_DAYS_PER_YEAR
    elec_cost_yr = energy_yr * elec_day
    diesel_l = n * 120 * _WORKING_DAYS_PER_YEAR * 0.55
    diesel_cost_yr = diesel_l * 12
    maint_e = n * 45000
    maint_d = n * 70000

    # ----- six TCO categories IN ORDER (name, diesel total, electric total) -----
    cats = [
        {"name": "Owning", "diesel": n * 2.2e6, "electric": n * 3.4e6},
        {"name": "Running", "diesel": (diesel_cost_yr + maint_d) * Y, "electric": (elec_cost_yr + maint_e) * Y},
        {"name": "Infrastructure", "diesel": 0, "electric": n * (kw * 1800) + (900000 if peak > limit else 0)},
        {"name": "Policy & taxes", "diesel": n * 30000 * Y, "electric": n * 8000 * Y - n * 250000},
        {"name": "Hidden costs", "diesel": n * 15000 * Y, "electric": n * 10000 * Y},
        {"name": "Climate", "diesel": diesel_l * 2.65 / 1000 * 750 * Y, "electric": energy_yr * 0.1 / 1000 * 750 * Y},
    ]
    tot_d = sum(c["diesel"] for c in cats)
    tot_e = sum(c["electric"] for c in cats)

    # cumulative cost curves (DKK millions) and break-even year, verbatim from the mock-up.
    cd = cats[0]["diesel"]
    ce = cats[0]["electric"] + cats[2]["electric"]      # owning + infrastructure up front
    yr_d = (tot_d - cats[0]["diesel"]) / Y
    yr_e = (tot_e - cats[0]["electric"] - cats[2]["electric"]) / Y
    cum_d: List[float] = []
    cum_e: List[float] = []
    break_even: Optional[int] = None
    for y in range(Y + 1):
        cum_d.append(cd / 1e6)
        cum_e.append(ce / 1e6)
        if break_even is None and y > 0 and ce <= cd:
            break_even = y
        cd += yr_d
        ce += yr_e

    # co2 (tonnes/year).
    co2_d = diesel_l * 2.65 / 1000
    co2_e = energy_yr * 0.1 / 1000

    # ----- 24h site load profile (kW) -----
    load: List[int] = []
    for h in range(24):
        ch = 0.0
        if prio == "cost" and (h >= 22 or h < 5):
            ch = n * kw * coinc
        if prio == "grid" and (h >= se + 1 or h < 5):
            ch = n * kw * coinc * 0.85
        if prio == "early" and se <= h < se + 4:
            ch = n * kw
        day_bump = 10 if (6 <= h < se + 1) else 0
        load.append(_round_half_up(base + day_bump + ch))

    # 24h flexibility (shiftable load, kW).
    flex = [max(0, _round_half_up((load[h] - base) * 0.6)) for h in range(24)]
    # illustrative unit conversion: sum of hourly shiftable kW over the day, expressed in MWh (kW*1h/1000).
    flex_mwh_per_day = sum(flex) / 1000

    # ----- state of charge profile, half-hour steps -----
    used = worst / battery * 100
    start = {"cost": 22, "grid": se + 0.5, "early": se + 0.5}[prio]
    rate = kw / battery * 100
    floor = 100 - used
    soc: List[List[float]] = []
    t = 0.0
    # iterate 0..24 inclusive in 0.5 steps (49 points) without float drift.
    for step in range(49):
        t = step * 0.5
        if 6 <= t <= se:
            pct = 100 - used * (t - 6) / (se - 6)
        else:
            after = t if t > se else t + 24
            pct = floor if after < start else min(100, floor + rate * (after - start) * 0.95)
        soc.append([t, pct])

    # ----- strategy comparison across all three priorities -----
    strategies: List[Dict[str, Any]] = []
    for p in ("cost", "grid", "early"):
        hrs = {"cost": 7, "grid": (30 - se) - 2, "early": 4}[p]
        nd = worst / hrs * 1.1
        k = _first_size_ge(nd)
        pk = _round_half_up(base + n * k * _COINC[p])
        cy = energy_yr * 1.6 * price_f * _PRIO_F[p]
        fits = pk <= limit
        if p == "early":
            ready = f"{se + 4}:00"
        elif p == "grid":
            ready = "04:30"
        else:
            ready = "05:00"
        strategies.append({
            # §8: emit the CLIENT-FACING name only. the internal key p never leaves this module.
            "priority": _INTERNAL_TO_CLIENT[p],
            "charger_kw": k,
            "peak_kw": pk,
            "cost_per_year_dkk": cy,
            "fits_grid": fits,
            "ready_by": ready,
        })

    # ready_by for the KPIs is the active (chosen) priority's strategy ready_by.
    chosen_ready_by = next(s["ready_by"] for s in strategies if s["priority"] == settings["charging_priority"])

    # ----- per-truck energy (illustrative per-truck factors; cycle the 12-long list if n > 12) -----
    truck_f = [0.92, 1.05, 0.98, 1.1, 0.95, 1.0, 1.03, 0.9, 1.07, 0.97, 1.02, 0.94]
    per_vehicle: List[Dict[str, Any]] = []
    for i in range(n):
        f = truck_f[i % len(truck_f)]   # cycle the factor list for fleets larger than 12
        per_vehicle.append({"id": f"T{i + 1}", "avg": mean * f, "hardest": worst * f})

    # cumulative co2 saved over ownership (tonnes).
    co2_saved = [(co2_d - co2_e) * y for y in range(Y + 1)]

    # ----- verdict / headline / plan: PLAIN words only (§8) -----
    grid_fits = peak <= limit
    can_electrify = grid_fits and (break_even is not None)
    # tco_diff sign convention: electric minus diesel over the ownership period. negative => the electric
    # fleet costs less in total (good); positive => it costs more. documented in findings and the README.
    tco_diff = tot_e - tot_d

    if can_electrify:
        headline = "This fleet can go electric."
        if tco_diff <= 0:
            reason = (
                "The electric fleet fits the site's power connection and ends up cheaper over the "
                "years you plan to keep it."
            )
        else:
            reason = (
                "The electric fleet fits the site's power connection, though over these years it "
                "costs a little more than staying on diesel."
            )
    elif not grid_fits:
        headline = "The site's power connection is the limit."
        reason = (
            "With these choices the fleet asks for more power than the site can draw. Spreading the "
            "charging out or a larger connection would help."
        )
    else:
        headline = "The savings do not catch up in time."
        reason = (
            "The fleet fits the site's power connection, but over the years you plan to keep it the "
            "costs do not come back."
        )

    plan = [
        {"when": "Now", "text": "Confirm the trucks and the daily routes with Bob."},
        {"when": "Soon", "text": "Pick the charging approach that fits the site and the shift."},
        {"when": "Before delivery", "text": "Check the site's power connection covers the busiest day."},
        {"when": "Day one", "text": "Charge overnight so every truck is ready for the morning."},
    ]

    # ----- deterministic run id / timestamp (so repeated runs with identical inputs match) -----
    seed = "|".join(str(settings[k]) for k in (
        "fleet_size", "charging_priority", "electricity_price", "weather_year", "ownership_years", "shift_end"
    ))
    run_id = "demo-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    # a fixed illustrative timestamp - the demo is deterministic and must not depend on the wall clock.
    timestamp = "2026-01-01T00:00:00Z"

    settings_out = {
        "fleet_size": settings["fleet_size"],
        "charging_priority": settings["charging_priority"],   # client-facing
        "electricity_price": settings["electricity_price"],
        "weather_year": settings["weather_year"],
        "ownership_years": settings["ownership_years"],
        "shift_end": settings["shift_end"],
    }

    return {
        "run_id": run_id,
        "timestamp": timestamp,
        "mode": "demo",
        "illustrative": True,
        # additive §3.3 fields (FEAT-002): feed the §5.3 state-4 run screen's "N truck-days simulated"
        # line. server-provided so the UI never hard-codes 250. working_days is the illustrative
        # working-days-per-truck constant already used by the energy/cost maths above.
        "working_days": _WORKING_DAYS_PER_YEAR,
        "truck_days_simulated": n * _WORKING_DAYS_PER_YEAR,
        "settings": settings_out,
        "verdict": {
            "can_electrify": can_electrify,
            "headline": headline,
            "reason": reason,
        },
        "kpis": {
            "battery_kwh": battery,
            "charger_kw": kw,
            "charger_count": n,                 # one charge point per truck in the demo (illustrative)
            "ready_by": chosen_ready_by,
            "grid_peak_kw": peak,
            "grid_limit_kw": limit,
            "grid_fits": grid_fits,
            "tco_diff_dkk": tco_diff,
            "break_even_year": break_even,
            "co2_saved_t_per_year": co2_d - co2_e,
        },
        "energy": {
            "monthly_avg_kwh": months,
            "avg_day_kwh": mean,
            "hardest_day_kwh": worst,
            "per_vehicle": per_vehicle,
        },
        "charging": {
            "soc_profile": soc,
            "strategies": strategies,
        },
        "grid": {
            "load_24h_kw": load,
            "limit_kw": limit,
            "flex_24h_kw": flex,
            "flex_mwh_per_day": flex_mwh_per_day,
        },
        "tco": {
            "years": Y,
            "categories": cats,
            "cumulative": {"diesel": cum_d, "electric": cum_e},
            "break_even_year": break_even,
        },
        "co2": {
            "diesel_t_per_year": co2_d,
            "electric_t_per_year": co2_e,
            "cumulative_saved_t": co2_saved,
        },
        "plan": plan,
        "inputs_summary": _inputs_summary(),
    }
