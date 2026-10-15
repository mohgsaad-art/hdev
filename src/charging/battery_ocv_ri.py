# STATUS: NEW (Step 9, item 13 / M3.0 + M3.3, Bob to review). OCV + internal-resistance battery step.
#
# REFERENCE BEHAVIOUR: reference/vecto/cs/Battery.cs. VECTO's Battery.Request(dt, powerDemand) solves,
#   for a requested TERMINAL power P, the current I from the quadratic
#       P = U0*I + I^2 * R
#   where U0 is the open-circuit (internal) cell/pack voltage looked up from the SOC map
#   (ModelData.SOCMap.Lookup(SoC)) and R is the internal resistance looked up from SoC (and pulse time).
#   The battery loss is I^2 * R, the terminal voltage is U0 + I*R (VECTO: "adding both terms because
#   pos. current charges the battery"), and SOC advances by charge:
#       SoC_next = (Q * SoC + I*dt) / Q
#   with Q the pack capacity in ampere-seconds. We reproduce that behaviour as a PURE step.
#
# SIGN CONVENTION (matches Battery.cs): positive power/current = CHARGING (SOC rises); negative =
#   discharging (SOC falls). The sign of I follows the sign of P (SelectSolution keeps the root whose
#   sign matches the demand).
#
# PURITY (engine rule 7): the OCV curve and the resistance are ARGUMENTS (ocv_table, r_internal). The
#   function returns the new state; it never mutates its inputs and does no I/O.
# FAIL LOUDLY (engine rule 6): the OCV lookup NEVER extrapolates (SOC outside the table range raises);
#   a power demand with no real-valued current solution raises; dt must be > 0.
# UNITS: SI inside - volts (V), amperes (A), ohms (ohm), watts (W), seconds (s), coulombs (A*s).

import math


def ocv_lookup(ocv_table, soc):
    # linear interpolation of open-circuit voltage from an SOC->voltage table.
    # ocv_table: sorted list of (soc, voltage) pairs, soc ascending, in [0,1]. NEVER extrapolates:
    #   an SOC below the first point or above the last raises (engine rule: lookups do not extrapolate).
    if not ocv_table or len(ocv_table) < 2:
        raise ValueError("ocv_lookup: ocv_table must have at least 2 (soc, voltage) points")
    pts = sorted(ocv_table, key=lambda p: p[0])
    lo_soc, lo_v = pts[0]
    hi_soc, hi_v = pts[-1]
    if soc < lo_soc - 1e-12 or soc > hi_soc + 1e-12:
        raise ValueError(
            "ocv_lookup: soc %r is outside the OCV table range [%r, %r] - lookups do not extrapolate"
            % (soc, lo_soc, hi_soc)
        )
    # clamp tiny float drift to the ends
    if soc <= lo_soc:
        return float(lo_v)
    if soc >= hi_soc:
        return float(hi_v)
    for i in range(1, len(pts)):
        s1, v1 = pts[i - 1]
        s2, v2 = pts[i]
        if s1 <= soc <= s2:
            if s2 == s1:
                return float(v1)
            frac = (soc - s1) / (s2 - s1)
            return float(v1 + frac * (v2 - v1))
    raise ValueError("ocv_lookup: failed to bracket soc %r" % (soc,))  # pragma: no cover


def solve_current_for_power(power_w, u0_v, r_ohm):
    # solve P = U0*I + I^2 * R for I, keeping the root whose sign matches P (VECTO SelectSolution).
    # R == 0 -> linear: I = P / U0 (VECTO's "quadratic solver would become unstable" branch).
    if u0_v <= 0:
        raise ValueError("solve_current_for_power: open-circuit voltage must be > 0, got %r" % (u0_v,))
    if power_w == 0.0:
        return 0.0
    if r_ohm is None or abs(r_ohm) < 1e-15:
        return power_w / u0_v
    # R*I^2 + U0*I - P = 0
    a = r_ohm
    b = u0_v
    c = -power_w
    disc = b * b - 4 * a * c
    if disc < 0:
        raise ValueError(
            "solve_current_for_power: no real current solution for P=%r W (U0=%r V, R=%r ohm) - "
            "power demand exceeds what the pack can source/sink" % (power_w, u0_v, r_ohm)
        )
    sq = math.sqrt(disc)
    roots = [(-b + sq) / (2 * a), (-b - sq) / (2 * a)]
    want = 1.0 if power_w > 0 else -1.0
    matching = [r for r in roots if (r > 0) == (want > 0) or r == 0.0]
    if not matching:
        raise ValueError(
            "solve_current_for_power: no sign-matching current root for P=%r W" % (power_w,)
        )
    # pick the smallest-magnitude matching root (VECTO uses .Min() of the valid magnitudes)
    return min(matching, key=abs)


def battery_step(soc, power_w, dt_s, ocv_table, r_internal, capacity_as):
    # one OCV + internal-resistance step (per Battery.cs behaviour). PURE: returns a new state dict.
    #
    #   soc         : state of charge at the start of the step, fraction in the OCV table range.
    #   power_w     : requested TERMINAL power, W. +charging / -discharging.
    #   dt_s        : step length in SECONDS. REQUIRED, must be > 0 (no default - see charging_sim).
    #   ocv_table   : SOC->voltage table (argument, never hard-coded).
    #   r_internal  : internal resistance, ohm. May be 0 (ideal) -> linear current.
    #   capacity_as : pack capacity in ampere-seconds (A*s = Q). SOC advances by I*dt / Q.
    #
    # returns {'soc', 'current_a', 'u0_v', 'terminal_v', 'loss_w', 'delivered_wh'}.
    if dt_s is None or dt_s <= 0:
        raise ValueError("battery_step: dt_s must be > 0 (seconds), got %r" % (dt_s,))
    if capacity_as is None or capacity_as <= 0:
        raise ValueError("battery_step: capacity_as must be > 0 (ampere-seconds), got %r" % (capacity_as,))

    u0 = ocv_lookup(ocv_table, soc)
    current = solve_current_for_power(power_w, u0, r_internal)
    loss = current * (r_internal if r_internal else 0.0) * current  # I^2 * R
    terminal_v = u0 + current * (r_internal if r_internal else 0.0)  # VECTO: U0 + I*R

    # SOC advance by charge moved: (Q*soc + I*dt) / Q  (NEVER extrapolates past the table on lookup, but
    # SOC itself may hit the physical [0,1] bounds; the caller/env enforces operational min/max SOC).
    soc_next = (capacity_as * soc + current * dt_s) / capacity_as
    delivered_wh = power_w * dt_s / 3600.0  # terminal energy this step, Wh

    return {
        "soc": soc_next,
        "current_a": current,
        "u0_v": u0,
        "terminal_v": terminal_v,
        "loss_w": loss,
        "delivered_wh": delivered_wh,
    }
