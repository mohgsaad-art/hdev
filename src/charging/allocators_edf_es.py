# STATUS: CURRENT. EDF (earliest deadline first) and ES (equal share, water-filling) split the site target between vehicles.
# Pure functions of env state (do not mutate env).

import numpy as np

# --- EDF: earliest-deadline-first (import/export symmetric) ---
def edf_actions(env):
    """
    Return normalized actions in [-1,1] (non-V2G clipped to [0,1]) for all EVs.
    Uses env.* only; does not mutate env.
    """
    dt = float(env.dt)
    n  = env.number_evs
    present = env.present

    # per-EV import/export bounds (kW)
    need_kwh = np.where(present, np.maximum(env.power_needed, 0.0), 0.0)
    pmax_imp = np.minimum(need_kwh / dt, env.max_charging_rate)              # ≥ 0
    v2g_mask = present & env.v2g_capable & (env.soc_current > env.min_soc_v2g)
    v2g_head = np.where(v2g_mask,
                        np.maximum((env.soc_current - env.min_soc_v2g) * env.battery_capacity, 0.0),
                        0.0)
    pmax_exp = -np.minimum(v2g_head / dt, env.max_charging_rate)             # ≤ 0

    target_kw = float(env.station_capacity)
    alloc_kw  = np.zeros(n, dtype=float)

    if target_kw >= 0.0:
        # IMPORT: serve smallest time_left first
        order = np.argsort(np.where(present, env.time_left, np.inf))
        rem = target_kw
        for i in order:
            if not present[i] or rem <= 1e-9: break
            take = min(pmax_imp[i], rem)
            alloc_kw[i] = max(0.0, take)
            rem -= take
    else:
        # EXPORT: among V2G-capable with headroom, serve smallest time_left first
        valid = v2g_mask & (pmax_exp < -1e-9)
        order = np.argsort(np.where(valid, env.time_left, np.inf))
        rem = target_kw  # negative
        for i in order:
            if not valid[i] or rem >= -1e-9: break
            give = max(pmax_exp[i], rem)   # both ≤ 0
            alloc_kw[i] = min(0.0, give)
            rem -= give

    # kW -> normalized action
    a = alloc_kw / env.max_charging_rate
    a = np.where(env.v2g_capable, np.clip(a, -1.0, 1.0), np.clip(a, 0.0, 1.0))
    a = np.where(present, a, 0.0)
    return a.astype(np.float32)

# --- ES: equal-share with saturation (“water-filling”) ---
def es_actions(env):
    """
    Return normalized actions in [-1,1] (non-V2G clipped to [0,1]) for all EVs.
    """
    dt = float(env.dt)
    n  = env.number_evs
    present = env.present

    need_kwh = np.where(present, np.maximum(env.power_needed, 0.0), 0.0)
    pmax_imp = np.minimum(need_kwh / dt, env.max_charging_rate)              # ≥ 0
    v2g_mask = present & env.v2g_capable & (env.soc_current > env.min_soc_v2g)
    v2g_head = np.where(v2g_mask,
                        np.maximum((env.soc_current - env.min_soc_v2g) * env.battery_capacity, 0.0),
                        0.0)
    pmax_exp = -np.minimum(v2g_head / dt, env.max_charging_rate)             # ≤ 0

    target_kw = float(env.station_capacity)
    alloc_kw  = np.zeros(n, dtype=float)

    if target_kw >= 0.0:
        S = {i for i in range(n) if present[i] and pmax_imp[i] > 1e-9}
        rem = target_kw
        while S and rem > 1e-9:
            share = rem / len(S)
            gained = 0.0
            done = []
            for i in list(S):
                head = pmax_imp[i] - alloc_kw[i]
                inc  = min(share, max(0.0, head))
                alloc_kw[i] += inc
                gained += inc
                if alloc_kw[i] >= pmax_imp[i] - 1e-12:
                    done.append(i)
            rem = max(0.0, rem - gained)
            for i in done: S.discard(i)
    else:
        S = {i for i in range(n) if v2g_mask[i] and pmax_exp[i] < -1e-9}
        rem = target_kw  # negative
        while S and rem < -1e-9:
            share = rem / len(S)  # negative
            gained = 0.0
            done = []
            for i in list(S):
                # move alloc_kw[i] toward pmax_exp[i] (more negative), not beyond
                inc = max(share, pmax_exp[i] - alloc_kw[i])  # both ≤ 0
                alloc_kw[i] += inc
                gained += inc
                if abs(alloc_kw[i] - pmax_exp[i]) <= 1e-12:
                    done.append(i)
            rem = rem - gained
            for i in done: S.discard(i)

    a = alloc_kw / env.max_charging_rate
    a = np.where(env.v2g_capable, np.clip(a, -1.0, 1.0), np.clip(a, 0.0, 1.0))
    a = np.where(present, a, 0.0)
    return a.astype(np.float32)