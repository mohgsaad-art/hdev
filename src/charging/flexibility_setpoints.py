# STATUS: CURRENT ("my flexibility code", pasted by Bob 12 Oct 2026).
# Site setpoint policies (JIT, ASAP) + feasibility headroom (import/export). These live OUTSIDE the env (decided).
# Flexibility (thesis): energy-neutral up/down headroom between feasible_export and feasible_import.
# Planned: a cheapest-first setpoint using hourly prices (Energidataservice spot + tariffs) - not written.
# Note: overlaps with helpers in tester_21h_maddpg.py (duplicate definitions).
import numpy as np

# --- physics feasibility (import/export heads) ---
def refresh_feasibility(env):
    per_ev_need_kwh = np.where(env.present, np.maximum(env.power_needed, 0.0), 0.0)
    cap_imp = np.minimum(per_ev_need_kwh / env.dt, env.max_charging_rate)
    Pmax = float(min(np.sum(cap_imp), env.max_station_capacity))

    v2g_mask = env.present & env.v2g_capable & (env.soc_current > env.min_soc_v2g)
    v2g_head = np.where(v2g_mask,
                        np.maximum((env.soc_current - env.min_soc_v2g) * env.battery_capacity, 0.0),
                        0.0)
    cap_exp = np.minimum(v2g_head / env.dt, env.max_charging_rate)
    Pmin = -float(min(np.sum(cap_exp), env.max_station_capacity))

    env.feasible_import = Pmax
    env.feasible_export = Pmin
    return Pmin, Pmax

# --- build the 6-feature obs your Actor expects ---
def build_obs_from_env(env):
    time_to_arr = np.maximum(0.0, env.arrival_time - env.time_now)
    time_to_dep = np.maximum(0.0, env.depart_time  - env.time_now)
    signed_time = np.where(env.present, +time_to_dep, -time_to_arr) / env.max_time

    refresh_feasibility(env)  # make sure feas_* reflect THIS state
    need_norm  = np.where(env.present, env.power_needed / env.max_battery_capacity, 0.0).astype(np.float32)
    stat_norm  = np.full(env.number_evs, env.station_capacity / env.max_station_capacity, dtype=np.float32)
    feas_imp_n = np.full(env.number_evs, env.feasible_import / env.max_station_capacity, dtype=np.float32)
    feas_exp_n = np.full(env.number_evs, env.feasible_export / env.max_station_capacity, dtype=np.float32)
    v2g_float  = env.v2g_capable.astype(np.float32)

    obs_2d = np.stack([need_norm, signed_time.astype(np.float32), stat_norm, feas_imp_n, feas_exp_n, v2g_float], axis=-1)
    return obs_2d.flatten().astype(np.float32)

# --- baselines ---
def jit_setpoint(env):
    """Per-EV avg power to finish exactly by departure; cap by physics/site."""
    present = env.present
    need_kwh = np.where(present, np.maximum(env.power_needed, 0.0), 0.0)
    t_left   = np.where(present, np.maximum(env.time_left, env.dt), env.dt)
    per_ev   = np.minimum(need_kwh / t_left, env.max_charging_rate)  # kW
    refresh_feasibility(env)
    return float(min(per_ev.sum(), env.feasible_import, env.max_station_capacity))

def asap_setpoint(env):
    """Fast-as-possible import (no export)."""
    refresh_feasibility(env)
    return float(max(0.0, env.feasible_import))

def site_target(env, mode="JIT"):
    mode = (mode or "JIT").upper()
    return jit_setpoint(env) if mode == "JIT" else asap_setpoint(env)
