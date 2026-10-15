# STATUS: NEW (Step 9, item 13 / M3.0 + M3.3, Bob to review). Charging in TWO modes.
#
#   SIZING MODE   - sizing_power(E, t): the MINIMUM constant power P_min = E / t needed to deliver
#                   energy E (kWh) over the available time t (hours). Used to size a charger / check
#                   whether a session can be served in the dwell window. No battery model, just E/t.
#
#   SIMULATION MODE - simulate_session(...): steps a session per timestep through the OCV + internal-
#                   resistance battery model (src.charging.battery_ocv_ri.battery_step), accumulating
#                   SOC and delivered energy. This is the physically detailed path.
#
# dt IS A REQUIRED ARGUMENT (NO DEFAULT). The timestep for depot charging must come from the Energinet
#   product specs (settlement/metering resolution), which are NOT sourced yet - so we refuse to invent a
#   default dt and force the caller to pass it. See the TWO-RESOLUTION HOOK below.
#
# PURITY (engine rule 7): every parameter is an argument; no I/O; the battery curve/resistance are
#   passed through to battery_step.
# FAIL LOUDLY (engine rule 6): non-positive E/t/dt, or a dt that does not evenly cover the window within
#   tolerance, raise.
# UNITS: energy in kWh at the sizing edge (that is how chargers are rated); the simulation uses SI
#   seconds/watts internally via battery_step and reports kWh back out.

from src.charging.battery_ocv_ri import battery_step


# ---------------------------------------------------------------------------
# TWO-RESOLUTION HOOK (dt_base / dt_fine / windows) - "from Energinet product specs, to be sourced"
# ---------------------------------------------------------------------------
# Depot charging may want a COARSE base resolution for the bulk of a long overnight session and a FINE
# resolution inside specific windows (e.g. around a price/tariff boundary or a peak). The hook lets the
# caller declare dt_base, dt_fine and a list of fine windows. Until the Energinet product specs are
# sourced, the NEUTRAL default is dt_fine == dt_base and NO windows, so the two-resolution logic reduces
# to a single uniform dt and changes nothing. The exact dt values and window definitions are FLAGGED as
# "from Energinet product specs, to be sourced".

def resolve_timestep_plan(dt_base, dt_fine=None, windows=None):
    # Return a (small) plan describing the timestep resolution. NEUTRAL when dt_fine is None/==dt_base
    # and windows is empty: a single uniform dt_base. dt_base is REQUIRED (no default - Energinet).
    if dt_base is None or dt_base <= 0:
        raise ValueError("resolve_timestep_plan: dt_base must be > 0 seconds (Energinet-sourced), got %r"
                         % (dt_base,))
    if dt_fine is None:
        dt_fine = dt_base
    if dt_fine <= 0:
        raise ValueError("resolve_timestep_plan: dt_fine must be > 0 seconds, got %r" % (dt_fine,))
    windows = list(windows or [])
    neutral = (abs(dt_fine - dt_base) < 1e-12) and not windows
    return {
        "dt_base": float(dt_base),
        "dt_fine": float(dt_fine),
        "windows": windows,
        "neutral": neutral,
        "flag": "timestep resolution (dt_base/dt_fine/windows) is from Energinet product specs, "
                "to be sourced; neutral until then (dt_fine == dt_base, no windows)",
    }


# ---------------------------------------------------------------------------
# SIZING MODE: P_min = E / t
# ---------------------------------------------------------------------------

def sizing_power(energy_kwh, available_hours):
    # minimum constant power (kW) to deliver energy_kwh over available_hours. P = E / t.
    if energy_kwh is None or energy_kwh < 0:
        raise ValueError("sizing_power: energy_kwh must be >= 0, got %r" % (energy_kwh,))
    if available_hours is None or available_hours <= 0:
        raise ValueError("sizing_power: available_hours must be > 0, got %r" % (available_hours,))
    return float(energy_kwh) / float(available_hours)


# ---------------------------------------------------------------------------
# SIMULATION MODE: per-timestep OCV + Ri stepping, dt REQUIRED
# ---------------------------------------------------------------------------

def simulate_session(
    soc_start,
    power_request_w,
    duration_s,
    dt,
    ocv_table,
    r_internal,
    capacity_as,
    soc_max=1.0,
):
    # Step a single plug-in session at a fixed requested terminal power, dt seconds per step, through the
    # OCV + Ri battery model. Stops early if SOC reaches soc_max (need met) while charging.
    #
    #   soc_start       : SOC at plug-in, fraction in the OCV table range.
    #   power_request_w : requested terminal power each step, W (+charge / -discharge). Required.
    #   duration_s      : session length in seconds (arrival -> departure). Required, > 0.
    #   dt              : timestep in SECONDS. REQUIRED, NO DEFAULT (must come from Energinet specs).
    #   ocv_table, r_internal, capacity_as : battery parameters, passed to battery_step.
    #   soc_max         : operational max SOC (default 1.0). Charging stops when reached.
    #
    # returns {'soc_end', 'delivered_kwh', 'loss_kwh', 'steps', 'soc_trace'}.
    if dt is None:
        # explicit, loud refusal rather than a silent default - dt must be Energinet-sourced.
        raise ValueError("simulate_session: dt is a REQUIRED argument (seconds, from Energinet specs) - "
                         "there is no default dt")
    if dt <= 0:
        raise ValueError("simulate_session: dt must be > 0 seconds, got %r" % (dt,))
    if duration_s is None or duration_s <= 0:
        raise ValueError("simulate_session: duration_s must be > 0, got %r" % (duration_s,))

    n_steps = int(round(duration_s / dt))
    if n_steps < 1:
        raise ValueError("simulate_session: duration_s %r is shorter than one dt %r" % (duration_s, dt))

    soc = float(soc_start)
    delivered_wh = 0.0
    loss_wh = 0.0
    trace = [soc]
    steps_done = 0
    for _ in range(n_steps):
        # if charging and already at/above soc_max, stop (need met)
        if power_request_w > 0 and soc >= soc_max - 1e-12:
            break
        step = battery_step(soc, power_request_w, dt, ocv_table, r_internal, capacity_as)
        new_soc = step["soc"]
        if power_request_w > 0 and new_soc > soc_max:
            new_soc = soc_max  # clamp the final partial step to the max SOC
        soc = new_soc
        delivered_wh += step["delivered_wh"]
        loss_wh += step["loss_w"] * dt / 3600.0
        trace.append(soc)
        steps_done += 1

    return {
        "soc_end": soc,
        "delivered_kwh": delivered_wh / 1000.0,
        "loss_kwh": loss_wh / 1000.0,
        "steps": steps_done,
        "soc_trace": trace,
    }
