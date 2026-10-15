# STATUS: NEW (Step 9, item 16 / M3.5, Bob to review). PURE flexibility wrapper.
#
# WHAT THIS IS: a pure, numpy-based re-expression of the feasibility math that already lives in
#   src/charging/flexibility_setpoints.py (refresh_feasibility: the import/export heads). That module
#   reads its numbers OFF a live env object (env.present, env.power_needed, ...), so it cannot be called
#   without constructing the thesis env (which imports gym). This wrapper takes the SAME quantities as
#   PLAIN ARRAYS/scalars and computes the SAME feasible import/export heads, then rolls them up into a
#   per-hour energy-neutral up/down headroom. No gym, no env, no mutation - a pure function of its args.
#
#   We do NOT rewrite flexibility_setpoints.py: it stays as Bob's current code. This file re-expresses
#   its arithmetic (the min(sum(cap_imp), max_station_capacity) import head and the symmetric V2G export
#   head) so the pipeline has a gym-free entry point. The two are kept in step by construction - the
#   formulas here are the formulas there.
#
# §8 METHOD-HIDING: the internal setpoint-policy names (ASAP / JIT / EDF / ES / cost-based) stay INSIDE
#   flexibility_setpoints.py / the allocators. This wrapper's OUTPUT uses PLAIN words only:
#   up_kw / down_kw / up_kwh / down_kwh per hour. No strategy name reaches the result.
#
# PURITY (engine rule 7): every parameter is an argument; no I/O; works for any site.
# FAIL LOUDLY (engine rule 6): mismatched array lengths or a non-positive dt raise.
#
# UNITS: power in kW, energy in kWh, dt in HOURS (per-hour headroom is the natural output step here;
#   the caller passes dt=1.0 for a 1-hour grid). "energy-neutral" means the up and down headroom are
#   reported independently per hour - shifting load up in one hour and down in another nets to zero over
#   the window, which is exactly the thesis definition (headroom between feasible_export and
#   feasible_import).

import numpy as np


def feasible_heads(
    present,
    power_needed_kwh,
    max_charging_rate_kw,
    max_station_capacity_kw,
    dt_h,
    v2g_capable=None,
    soc_current=None,
    min_soc_v2g=None,
    battery_capacity_kwh=None,
):
    # PURE re-expression of flexibility_setpoints.refresh_feasibility, taking plain arrays instead of an
    # env. Returns (Pmin, Pmax): the feasible export (<=0) and import (>=0) heads in kW for one state.
    #
    #   present                 : bool array, EV plugged in this state.
    #   power_needed_kwh        : array, remaining energy need per EV, kWh.
    #   max_charging_rate_kw    : scalar or array, per-EV charger limit, kW.
    #   max_station_capacity_kw : scalar, site connection limit, kW.
    #   dt_h                    : timestep in HOURS (need_kWh / dt_h -> kW). Required, > 0.
    #   v2g_capable, soc_current, min_soc_v2g, battery_capacity_kwh : optional V2G inputs; when any is
    #     None the export head is 0 (no V2G), matching "no bidirectional capability".
    present = np.asarray(present, dtype=bool)
    power_needed_kwh = np.asarray(power_needed_kwh, dtype=float)
    if present.shape != power_needed_kwh.shape:
        raise ValueError("feasible_heads: present and power_needed_kwh must have the same shape")
    if dt_h is None or dt_h <= 0:
        raise ValueError("feasible_heads: dt_h must be > 0 hours, got %r" % (dt_h,))

    # import head: each present EV can draw up to min(need/dt, charger rate); the site caps the sum.
    per_ev_need_kwh = np.where(present, np.maximum(power_needed_kwh, 0.0), 0.0)
    cap_imp = np.minimum(per_ev_need_kwh / dt_h, max_charging_rate_kw)
    Pmax = float(min(np.sum(cap_imp), max_station_capacity_kw))

    # export head (V2G): only when all V2G inputs are supplied; else 0 (no bidirectional capability).
    if v2g_capable is None or soc_current is None or min_soc_v2g is None or battery_capacity_kwh is None:
        Pmin = 0.0
    else:
        v2g_capable = np.asarray(v2g_capable, dtype=bool)
        soc_current = np.asarray(soc_current, dtype=float)
        v2g_mask = present & v2g_capable & (soc_current > min_soc_v2g)
        v2g_head = np.where(
            v2g_mask,
            np.maximum((soc_current - min_soc_v2g) * battery_capacity_kwh, 0.0),
            0.0,
        )
        cap_exp = np.minimum(v2g_head / dt_h, max_charging_rate_kw)
        Pmin = -float(min(np.sum(cap_exp), max_station_capacity_kw))

    return Pmin, Pmax


def flexibility_per_hour(
    load_profile_kw,
    feasible_import_kw,
    feasible_export_kw,
    dt_h=1.0,
):
    # PURE per-hour up/down energy-neutral headroom.
    #
    #   load_profile_kw   : array, the committed site load per step, kW (one entry per step).
    #   feasible_import_kw: scalar OR array, the feasible import head per step, kW (>= load).
    #   feasible_export_kw: scalar OR array, the feasible export head per step, kW (<= 0, V2G down).
    #   dt_h              : step length in HOURS (default 1.0 = a 1-hour grid). > 0.
    #
    # up_kw   = how much MORE the site could draw this step  = feasible_import - load (clamped >= 0).
    # down_kw = how much LESS the site could draw this step  = load - max(feasible_export, 0 floor).
    #           down is bounded by the load itself (you cannot shed below zero draw) PLUS any V2G export
    #           head below zero. We report down as (load - feasible_export) clamped >= 0 so a V2G-capable
    #           site shows headroom below zero draw too.
    # up_kwh / down_kwh are the per-step energy versions (kW * dt_h).
    #
    # Returns {'up_kw', 'down_kw', 'up_kwh', 'down_kwh', 'dt_h', 'note'} with the four series as lists.
    if dt_h is None or dt_h <= 0:
        raise ValueError("flexibility_per_hour: dt_h must be > 0 hours, got %r" % (dt_h,))
    load = np.asarray(load_profile_kw, dtype=float)
    n = load.shape[0]

    imp = np.asarray(feasible_import_kw, dtype=float)
    exp = np.asarray(feasible_export_kw, dtype=float)
    if imp.ndim == 0:
        imp = np.full(n, float(imp))
    if exp.ndim == 0:
        exp = np.full(n, float(exp))
    if imp.shape[0] != n or exp.shape[0] != n:
        raise ValueError("flexibility_per_hour: feasible_import_kw / feasible_export_kw must match the "
                         "load profile length (%d)" % n)

    up_kw = np.maximum(imp - load, 0.0)
    down_kw = np.maximum(load - exp, 0.0)

    return {
        "up_kw": [float(x) for x in up_kw],
        "down_kw": [float(x) for x in down_kw],
        "up_kwh": [float(x * dt_h) for x in up_kw],
        "down_kwh": [float(x * dt_h) for x in down_kw],
        "dt_h": float(dt_h),
        "note": "per-step headroom to draw more (up) or less (down); energy-neutral over the window",
    }
