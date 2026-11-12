"""EXPERIMENTAL VARIANTS for the aux / PTO review (12 Nov 2026).  NOT Bob's engine code.

Rule 0.1 of the prompt: nothing under src/ and nothing in the notebook is changed.  Every function here
is a clearly named variant or a clearly marked copy.  Bob writes the real engine code himself.

Contents
  aux_row_current(...)                copy of the step-6 aux formula of the code of record (Appendix 1.4).  The test
                                      tests/aux_pto/test_step6_copy_matches_notebook.py runs the REAL notebook
                                      consumption_engine against this copy so the copy cannot drift.
  aux_row_variant(...)                Part C rule variants (a) SP on V>0.01, (b) Cond only when motor not off,
                                      (c) Cond during stop PTO (VECTO rule), (d) everything always on.
  P_aux_v_bob_intended                P_aux with the checks Bob says his intended version has.
  P_aux_v_checks                      ... plus finite / shape / PTO_eff<=1 checks (Kiro proposal).
  SP_power_helper_v_checks            SP_power_helper plus shape / finite / sign checks (Kiro proposal).
  parser_check_pto                    what the PARSER must check before pto_engine (whole seconds, increasing, ...).
  pto_engine_v_checks                 pto_engine behind parser_check_pto + efficiency guard.
  consumption_step6_v_pto1nov         PTO on rows for the 1 Nov pto_engine outputs (stop + drive part).
  consumption_step6_current_loop      COPY of the PTO loop of the code of record (timing only).
Engine-or-parser tag is given in each docstring ("ENGINE" / "PARSER").
"""
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from _load_notebook import NS  # noqa: E402

_pto_engine_nb = NS["pto_engine"]
_SP_nb = NS["SP_power_helper"]

# =============================================================================================
# Part C: aux on rows
# =============================================================================================


def aux_row_current(V, pto_active, ES, PS, HVAC_row, SP, cond, PTO_always_on, pto_row):
    """COPY of the step-6 aux sum of consumption_engine (Appendix 1.4).  ENGINE.
    SP only when V > 0, Cond when moving OR stop-PTO active, everything else always on."""
    moving = np.asarray(V) > 0
    return (ES + PS + HVAC_row + SP * moving + cond * (moving | np.asarray(pto_active)) + PTO_always_on + pto_row)


def aux_row_variant(rule, V, pto_active, ES, PS, HVAC_row, SP, cond, PTO_always_on, pto_row, motor_off=None, v_eps=0.01):
    """Part C rule variants, one at a time (the other aux rules stay as in the code of record).  ENGINE (the inputs are rows).
    rule 'current' : code of record
    rule 'a'       : SP on when V > v_eps (VECTO VehicleStopped = |v| <= 0.01 m/s, Vehicle.cs 262)
    rule 'b'       : Cond on only when the motor is not off (motor_off bool array, one per row)   [VECTO Conditioning.cs 85-91]
    rule 'c'       : Cond also on during stop PTO (this is already in 'current'; here: Cond = ~motor_off | pto_active)
    rule 'a+b+c'   : all three together = the closest to VECTO
    rule 'd'       : everything always on (conservative bound: SP and Cond on every row)
    """
    V = np.asarray(V)
    pto_active = np.asarray(pto_active)
    if rule == "current":
        return aux_row_current(V, pto_active, ES, PS, HVAC_row, SP, cond, PTO_always_on, pto_row)
    sp_on = V > 0
    cond_on = (V > 0) | pto_active
    if rule in ("a", "a+b+c"):
        sp_on = V > v_eps
    if rule in ("b", "c", "a+b+c"):
        if motor_off is None:
            raise ValueError("rules b/c need a motor_off array (BLOCKED: no motor-off signal given)")
        cond_on = (~np.asarray(motor_off, dtype=bool)) | pto_active
    if rule == "d":
        sp_on = np.ones(len(V), dtype=bool)
        cond_on = np.ones(len(V), dtype=bool)
    return ES + PS + HVAC_row + SP * sp_on + cond * cond_on + PTO_always_on + pto_row


# =============================================================================================
# Part B / H: checks (what Bob says his intended version has + Kiro proposals)
# =============================================================================================


def P_aux_v_bob_intended(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on,
                         ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0):
    """Bob's intended version (prompt Appendix 1.1, last paragraph): loops over powers + [PTO_always_on] and
    effs + (PTO_eff,), no 'undo the multiply' comment.  ENGINE."""
    powers = [np.asarray(p, dtype=float) for p in (ES_power, PS_power, HVAC_power, SP_power, cond_power)]
    effs = (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff)
    PTO_always_on = np.asarray(PTO_always_on, dtype=float)
    for p in powers + [PTO_always_on]:
        if np.any(p < 0):
            raise ValueError("aux power cannot be negative")
    for e in effs + (PTO_eff,):
        if e <= 0:
            raise ValueError("efficiency must be > 0")
    ES_p, PS_p, HVAC_p, SP_p, cond_p = (p * e for p, e in zip(powers, effs))
    return ES_p, PS_p, HVAC_p, SP_p, cond_p, PTO_always_on / PTO_eff


def P_aux_v_checks(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on,
                   ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0):
    """Bob's intended checks PLUS: NaN/inf rejected, array shapes must be scalar or equal, PTO_eff must be in (0, 1].
    ENGINE (cheap input guards, no table lookups).  Kiro proposal, not a decision."""
    ps = [np.asarray(p, dtype=float) for p in (ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on)]
    for p in ps:
        if not np.all(np.isfinite(p)):
            raise ValueError("aux power must be finite (no NaN / inf)")
        if np.any(p < 0):
            raise ValueError("aux power cannot be negative")
    shapes = {p.shape for p in ps if p.ndim > 0}
    if len(shapes) > 1:
        raise ValueError(f"array inputs must all have the same shape, got {sorted(shapes)}")
    for e in (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff, PTO_eff):
        if not (np.isscalar(e) and math.isfinite(e) and e > 0):
            raise ValueError("efficiency must be a finite number > 0")
    if PTO_eff > 1:
        raise ValueError("PTO_eff is an efficiency and cannot be > 1")
    out = [p * e for p, e in zip(ps[:5], (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff))]
    out.append(ps[5] / PTO_eff)
    return tuple(out)


def SP_power_helper_v_checks(SP_baseline, SP_axle_shares, SP_tech_factors):
    """SP_power_helper (unchanged maths) behind input guards.  ENGINE for shape/finite/sign; the maximum number of
    steered axles (VECTO SP-Axles.csv has rows 1-4) is a PARSER check because it comes from a table."""
    b = np.asarray(SP_baseline, dtype=float)
    a = np.asarray(SP_axle_shares, dtype=float)
    f = np.asarray(SP_tech_factors, dtype=float)
    if b.shape != (3,):
        raise ValueError("SP_baseline must be exactly (UF, B, S)")
    for name, x in (("SP_baseline", b), ("SP_axle_shares", a), ("SP_tech_factors", f)):
        if not np.all(np.isfinite(x)):
            raise ValueError(f"{name} must be finite")
        if np.any(x < 0):
            raise ValueError(f"{name} cannot be negative")
    if np.any(a > 100):
        raise ValueError("SP_axle_shares are percent, must be <= 100")
    return _SP_nb(b, a, f)


# =============================================================================================
# Part H: parser-side checks for pto_engine inputs
# =============================================================================================


def _profile_check(name, t, w):
    t = np.asarray(t, dtype=float)
    w = np.asarray(w, dtype=float)
    if t.ndim != 1 or w.ndim != 1 or len(t) != len(w):
        raise ValueError(f"{name}: t and W must be 1-D and the same length")
    if len(t) < 2:
        raise ValueError(f"{name}: needs at least 2 points (the last W is only an end marker)")
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(w))):
        raise ValueError(f"{name}: NaN / inf not allowed")
    if np.any(t != np.round(t)):
        raise ValueError(f"{name}: times must be whole seconds (np.diff(...).astype(int) would truncate)")
    if np.any(np.diff(t) <= 0):
        raise ValueError(f"{name}: times must be strictly increasing")
    if np.any(w < 0):
        raise ValueError(f"{name}: power cannot be negative")


def parser_check_pto(stop, is_on, stop_pto_t=None, stop_pto_w=None, drive_pto_t=None, drive_pto_w=None,
                     stop_pto_eff=1.0, drive_pto_eff=1.0, wp_s=None, tol_m=1e-3):
    """PARSER.  Everything pto_engine assumes but does not check."""
    stop = np.asarray(stop, dtype=float)
    is_on = np.asarray(is_on, dtype=float)
    if len(is_on) != len(stop):
        raise ValueError("is_on must have one value per waypoint")
    if not np.all(np.isin(is_on, (0.0, 1.0))):
        raise ValueError("is_on must be 0 or 1")
    if not np.all(np.isfinite(stop)) or np.any(stop < 0):
        raise ValueError("stop times must be finite and >= 0")
    for name, t, w in (("stop profile", stop_pto_t, stop_pto_w), ("drive profile", drive_pto_t, drive_pto_w)):
        if t is not None and w is not None and len(t) > 0:
            _profile_check(name, t, w)
    for name, e in (("stop_pto_eff", stop_pto_eff), ("drive_pto_eff", drive_pto_eff)):
        if not (math.isfinite(e) and 0 < e <= 1):
            raise ValueError(f"{name} must be in (0, 1]")
    if wp_s is not None:
        wp_s = np.asarray(wp_s, dtype=float)
        idx = np.where(stop > 0)[0]
        d = np.diff(wp_s[idx])
        if np.any(np.abs(d) <= tol_m):
            raise ValueError("two stop waypoints at the same distance (within tolerance): reject")
        if np.any(np.diff(wp_s) < 0):
            raise ValueError("waypoint distances must be non-decreasing")


def pto_engine_v_checks(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff):
    """parser_check_pto + the notebook pto_engine, unchanged.  (Efficiency guard is ENGINE, rest PARSER.)"""
    parser_check_pto(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff)
    return _pto_engine_nb(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff)


# =============================================================================================
# Part D: PTO on rows for the 1 Nov pto_engine outputs
# =============================================================================================


def _standing_rows(S, V, s_wp, tol_m, M=None):
    """Rows of one stop: V == 0 (and driver mode M == 0 if M is given) and |S - s_wp| <= tol.
    S is non-decreasing, so searchsorted finds the slice in O(log n).
    NOTE (measured, Part D): with the notebook driver the first ACCELERATING row of a stop also has V == 0 (speed at the
    START of the step), so 'V == 0' gives stop + 1 rows.  M == 0 gives exactly the stop time."""
    lo = int(np.searchsorted(S, s_wp - tol_m, side="left"))
    hi = int(np.searchsorted(S, s_wp + tol_m, side="right"))
    ok = (V[lo:hi] == 0)
    if M is not None:
        ok &= (M[lo:hi] == 0)
    return lo + np.where(ok)[0]


def consumption_step6_v_pto1nov(S, V, wp_s, stop_wp, is_on, pto_start, stop_1s, drive_1s,
                                stop_const_W=0.0, drive_const_W=0.0, stop_eff=1.0, drive_eff=1.0,
                                tol_m=1e-3, fast=True, M=None):
    """TEST VARIANT of the PTO part of step 6 for the 1 Nov design.  ENGINE (pure: only arrays and numbers in).

    Inputs
      S, V            driver rows: distance and speed at the START of each 1 s row (V==0 means standing)
      wp_s, stop_wp   waypoint distance [m] and FINAL stop time [s] per waypoint (stop_wp includes the PTO time)
      is_on, pto_start, stop_1s, drive_1s   outputs of pto_engine (stop_1s / drive_1s already divided by their efficiency)
      stop_const_W, drive_const_W           a constant instead of a profile (SHAFT W; divided by stop_eff / drive_eff here)
      M (optional)    driver mode per row (0 = standing).  If given, standing rows = V == 0 AND M == 0 (see _standing_rows)
    Rules (decided, §1.1 of the prompt)
      stop profile : starts at the first standing row of that stop + pto_start; must fit inside the stop
      stop constant: all standing rows of that stop
      drive profile: starts at the first moving row after the stop (or at the marker row if stop_wp == 0);
                     keeps running past the next stop; if the next drive part starts while it still runs -> ValueError
                     (VECTO PTODriveAuxiliary.cs 25-27 throws "Additional PTO activation during drive requested while PTO still active!")
      drive constant: every row from leaving the stop (or the marker) until the first standing row of the next stop
    Returns pto_row [W per row], stop_active (bool per row), drive_active (bool per row), events (list of dicts).
    """
    S = np.asarray(S, dtype=float)
    V = np.asarray(V, dtype=float)
    M = None if M is None else np.asarray(M)
    wp_s = np.asarray(wp_s, dtype=float)
    stop_wp = np.asarray(stop_wp, dtype=float)
    is_on = np.asarray(is_on, dtype=float)
    pto_start = np.asarray(pto_start, dtype=float)
    stop_1s = np.asarray(stop_1s, dtype=float)
    drive_1s = np.asarray(drive_1s, dtype=float)
    n = len(S)
    if len(stop_1s) > 0 and stop_const_W:
        raise ValueError("stop part: give a profile OR a constant, not both")
    if len(drive_1s) > 0 and drive_const_W:
        raise ValueError("drive part: give a profile OR a constant, not both")
    for nm, e in (("stop_eff", stop_eff), ("drive_eff", drive_eff)):
        if not e > 0:
            raise ValueError(f"{nm} must be > 0")
    if len(is_on) != len(wp_s) or len(stop_wp) != len(wp_s):
        raise ValueError("is_on, stop_wp and wp_s need one value per waypoint")
    if np.any(~np.isin(is_on, (0.0, 1.0))):
        raise ValueError("is_on must be 0 or 1")

    stop_idx = np.where(stop_wp > 0)[0]
    if len(stop_idx) > 1 and np.any(np.diff(wp_s[stop_idx]) <= tol_m):
        raise ValueError("two stop waypoints at the same distance: the parser must reject this")

    # standing rows per stop waypoint (needed for all stops: the next stop ends a drive window)
    standing = {}
    for i in stop_idx:
        if fast:
            rows = _standing_rows(S, V, wp_s[i], tol_m, M)
        else:
            ok = (V == 0) & np.isclose(S, wp_s[i], rtol=0, atol=tol_m)
            rows = np.where(ok & (M == 0) if M is not None else ok)[0]
        if len(rows) == 0:
            raise ValueError(f"no standing rows found for stop at {wp_s[i]} m (float drift in S or driver/waypoint mismatch)")
        if len(rows) > 1 and np.any(np.diff(rows) != 1):
            raise ValueError(f"standing rows of the stop at {wp_s[i]} m are not contiguous")
        standing[i] = rows

    pto_row = np.zeros(n)
    stop_active = np.zeros(n, dtype=bool)
    drive_active = np.zeros(n, dtype=bool)
    events = []
    has_stop_profile = len(stop_1s) > 0
    has_stop_const = bool(stop_const_W)
    has_drive_profile = len(drive_1s) > 0
    has_drive_const = bool(drive_const_W)
    drive_end_prev = -1                 # last row (exclusive) of the previous drive PROFILE

    for i in np.where(is_on == 1)[0]:
        if i == 0:
            continue                    # depot: never PTO (pto_engine forces is_on[0] = 0; guard here as well)
        rows = standing.get(i)
        # --- stop part ---------------------------------------------------------------------------
        if rows is not None and (has_stop_profile or has_stop_const):
            if has_stop_profile:
                if np.isnan(pto_start[i]):
                    raise ValueError(f"waypoint {i}: stop profile given but pto_start is NaN")
                k0 = int(rows[0] + pto_start[i])
                k1 = k0 + len(stop_1s)
                if k1 > rows[-1] + 1:
                    raise ValueError(f"stop PTO ({len(stop_1s)} s) does not fit in the stop at {wp_s[i]} m ({len(rows)} standing rows)")
                pto_row[k0:k1] += stop_1s
                stop_active[k0:k1] = True
                events.append(dict(wp=int(i), kind="stop_profile", k0=k0, k1=k1, energy_kWh=float(stop_1s.sum()) / 3.6e6))
            else:
                add = stop_const_W / stop_eff
                pto_row[rows] += add
                stop_active[rows] = True
                events.append(dict(wp=int(i), kind="stop_const", k0=int(rows[0]), k1=int(rows[-1]) + 1,
                                   energy_kWh=add * len(rows) / 3.6e6))
        # --- drive part --------------------------------------------------------------------------
        if has_drive_profile or has_drive_const:
            if rows is not None:
                k_start = int(rows[-1]) + 1                      # first row after the last standing row
            else:
                k_start = int(np.searchsorted(S, wp_s[i] - tol_m, side="left"))   # 0 s marker: first row at/after the marker
            nxt = [j for j in stop_idx if j > i]
            k_end = int(standing[nxt[0]][0]) if nxt else n       # window ends at the first standing row of the next stop
            if k_start >= n:
                events.append(dict(wp=int(i), kind="drive_no_rows", k0=k_start, k1=k_start, energy_kWh=0.0))
                continue
            if has_drive_profile:
                if k_start < drive_end_prev:
                    raise ValueError(f"drive PTO profile from waypoint {i} starts at row {k_start} while the previous drive profile "
                                     f"still runs until row {drive_end_prev} (VECTO raises the same error)")
                k1 = min(k_start + len(drive_1s), n)
                m = k1 - k_start
                pto_row[k_start:k1] += drive_1s[:m]
                drive_active[k_start:k1] = True
                drive_end_prev = k1
                events.append(dict(wp=int(i), kind="drive_profile", k0=k_start, k1=k1,
                                   energy_kWh=float(drive_1s[:m].sum()) / 3.6e6, truncated=bool(m < len(drive_1s)),
                                   runs_past_next_stop=bool(k1 > k_end)))
            else:
                add = drive_const_W / drive_eff
                pto_row[k_start:k_end] += add
                drive_active[k_start:k_end] = True
                events.append(dict(wp=int(i), kind="drive_const", k0=k_start, k1=k_end, energy_kWh=add * (k_end - k_start) / 3.6e6))
    return pto_row, stop_active, drive_active, events


def consumption_step6_current_loop(S, V, wp_s, pto_on_col, pto_start_col, pto_1s):
    """COPY of the PTO loop of the code of record (Appendix 1.4, step 6) for timing only.  Same logic, same guards."""
    n = len(S)
    pto_row = np.zeros(n)
    pto_active = np.zeros(n, dtype=bool)
    for i in np.where(np.asarray(pto_on_col) == 1)[0]:
        at_stop = np.where((V == 0) & np.isclose(S, wp_s[i], rtol=0, atol=1e-3))[0]
        if len(at_stop) == 0:
            raise ValueError(f"no standing rows found for stop at {wp_s[i]} m")
        k0 = at_stop[0] + int(pto_start_col[i])
        k1 = k0 + len(pto_1s)
        if k1 > at_stop[-1] + 1:
            raise ValueError(f"PTO does not fit in stop at {wp_s[i]} m")
        pto_row[k0:k1] = pto_1s
        pto_active[k0:k1] = True
    return pto_row, pto_active
