# STATUS: THESIS TESTER (uses maddpg). Kept for reference: jit_setpoint, refresh_feasibility, site_target, plotting.
# The 21 h fixed episode is the known problem for multi-day sessions (see docs/design/year-and-day-simulation-problem.md).

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# JIT site setpoint (kW) helper
# -----------------------------
def jit_setpoint(env):
    """
    Compute the physics-only JIT site target (kW) from the *current* env state.
    Does NOT modify the env—caller sets env.station_capacity explicitly.
    """
    present = env.present
    need_kwh = np.where(present, np.maximum(env.power_needed, 0.0), 0.0)
    t_left   = np.where(present, np.maximum(env.time_left, env.dt), env.dt)  # hours
    per_ev_avg_kw = np.minimum(need_kwh / t_left, env.max_charging_rate)
    # Cap by physics
    return float(min(per_ev_avg_kw.sum(), env.feasible_import, env.max_station_capacity))

# --- helpers for testing (unchanged semantics) ---
def refresh_feasibility(env):
    """Recompute env.feasible_import/export from CURRENT state (pre-step)."""
    # Charge (import) cap
    per_ev_need_kwh = np.where(env.present, np.maximum(env.power_needed, 0.0), 0.0)
    cap_charge_kw_per_ev = np.minimum(per_ev_need_kwh / env.dt, env.max_charging_rate)
    Pmax = float(min(np.sum(cap_charge_kw_per_ev), env.max_station_capacity))  # ≥ 0

    # Discharge (export) cap
    v2g_mask = env.present & env.v2g_capable & (env.soc_current > env.min_soc_v2g)
    v2g_headroom_kwh = np.where(
        v2g_mask,
        np.maximum((env.soc_current - env.min_soc_v2g) * env.battery_capacity, 0.0),
        0.0
    )
    cap_discharge_kw_per_ev = np.minimum(v2g_headroom_kwh / env.dt, env.max_charging_rate)
    Pmin = -float(min(np.sum(cap_discharge_kw_per_ev), env.max_station_capacity))  # ≤ 0

    env.feasible_import = Pmax
    env.feasible_export = Pmin
    return Pmin, Pmax

def build_obs_from_env(env):
    """Build the 6-feature observation per EV to match Actor(obs_dim=6)."""
    # Signed time
    time_to_arrival = np.maximum(0.0, env.arrival_time - env.time_now)
    time_to_depart  = np.maximum(0.0, env.depart_time  - env.time_now)
    signed_time = np.where(env.present, +time_to_depart, -time_to_arrival) / env.max_time
    signed_time = signed_time.astype(np.float32)

    # Other features
    need_norm = np.where(env.present, env.power_needed / env.max_battery_capacity, 0.0).astype(np.float32)
    station_norm = np.full(env.number_evs, env.station_capacity / env.max_station_capacity, dtype=np.float32)
    v2g_float = env.v2g_capable.astype(np.float32)

    # Make sure feasibility is up-to-date for THIS state
    refresh_feasibility(env)
    feas_imp_norm = np.full(env.number_evs, env.feasible_import / env.max_station_capacity, dtype=np.float32)
    feas_exp_norm = np.full(env.number_evs, env.feasible_export / env.max_station_capacity, dtype=np.float32)

    obs_2d = np.stack(
        [need_norm, signed_time, station_norm, feas_imp_norm, feas_exp_norm, v2g_float],
        axis=-1
    )
    return obs_2d.flatten().astype(np.float32)

# -----------------------------
# Site target selector (JIT/ASAP)
# -----------------------------
def site_target(env, mode="JIT"):
    """
    mode = "JIT"  -> jit_setpoint()
    mode = "ASAP" -> charge as fast as physics allows (import cap, non-negative)
    """
    refresh_feasibility(env)
    mode = (mode or "JIT").upper()
    if mode == "ASAP":
        return float(max(0.0, env.feasible_import))
    return float(jit_setpoint(env))

# -------------------------------------------------
# MAIN TESTER: 21-hour baseline (JIT or ASAP) w/ logging
# -------------------------------------------------
def test_policy_21h_with_logging(env, maddpg, baseline_mode="JIT",
                                 n_days=1, custom_params=None):
    """
    Runs a *single 21-hour* episode per day. The tester computes the site target each step
    (JIT or ASAP) and writes env.station_capacity BEFORE env.step(...).
    Optional activation can be passed via custom_params:
        {'activate_at': int, 'A': float, 'activation_steps': int}
    All other custom_params fields match your previous tester.
    """
    # Force a 21h day (continuous episode)
    day_steps = int(round(21.0 / env.dt))
    env.max_steps = day_steps
    env.max_time  = 21.0

    for day in range(n_days):
        # Reset environment (random), then *anchor start-of-day at t=0*
        obs, _ = env.reset(seed=44 + day)

        # Optional: override with custom_params (same fields as before)
        if custom_params:
            # --- override core fields ---
            if 'time_now' in custom_params:
                env.time_now = float(custom_params['time_now'])

            if 'arrival_time' in custom_params:
                env.arrival_time = np.array(custom_params['arrival_time'], dtype=np.float32)
            if 'depart_time' in custom_params:
                env.depart_time  = np.array(custom_params['depart_time'], dtype=np.float32)

            if 'soc_arrival' in custom_params:
                env.soc_arrival = np.array(custom_params['soc_arrival'], dtype=np.float32)
                env.soc_current = env.soc_arrival.copy()
            if 'soc_required' in custom_params:
                env.soc_required = np.array(custom_params['soc_required'], dtype=np.float32)
            if 'battery_capacity' in custom_params:
                env.battery_capacity = np.array(custom_params['battery_capacity'], dtype=np.float32)
            if 'v2g_capable' in custom_params:
                env.v2g_capable = np.array(custom_params['v2g_capable'], dtype=bool)

            # derived
            env.power_needed = (env.soc_required - env.soc_current) * env.battery_capacity
            env.inital_power_needed = env.power_needed.copy()

        # Anchor the day so earliest arrival is at/after t=0
        shift = max(0.0, -float(np.min(env.arrival_time)))
        env.arrival_time += shift
        env.depart_time  += shift
        env.time_now = 0.0
        env.present   = (env.arrival_time <= env.time_now) & (env.time_now < env.depart_time)
        env.time_left = np.where(env.present, env.depart_time - env.time_now, 0.0).astype(np.float32)
        env.current_step = 0

        # Initial target & obs
        env.station_capacity = site_target(env, baseline_mode)
        obs = build_obs_from_env(env)

        # Activation knobs (optional)
        activate_at = None if not custom_params else custom_params.get('activate_at', None)
        A = 0.0 if not custom_params else float(custom_params.get('A', 0.0))
        activation_steps = 3 if not custom_params else int(custom_params.get('activation_steps', 3))
        act_left = 0

        # ---- day header ----
        print("="*60)
        print(f"Day {day+1}  (21h, baseline={baseline_mode})")
        print("V2G flags:            ", env.v2g_capable)
        print("Battery capacities:   ", np.round(env.battery_capacity, 1))
        print("Initial SOCs:         ", np.round(env.soc_arrival, 3))
        print("Requested SOCs:       ", np.round(env.soc_required, 3))
        print("Initial present:      ", env.present)
        print("Initial target (kW):  ", np.round(env.station_capacity, 2))
        print("-"*60)

        # ---- traces ----
        soc_traces = [[] for _ in range(env.number_evs)]
        power_traces = [[] for _ in range(env.number_evs)]
        timeleft_traces = [[] for _ in range(env.number_evs)]
        reward_traces = []
        net_power_traces = []
        setpoint_traces = []  # target each step
        reward_breakdowns = {k: [] for k in ["terminal_reward", "terminal_penalty", "step_reward", "step_penalty", "cycling_penalty", "grid_following_penalty"]}
        times = []
        departures = [None for _ in range(env.number_evs)]
        t = 0
        done = False

        # Store arrivals/targets for plotting
        soc_arrival_plot = env.soc_arrival.copy()
        soc_required_plot = env.soc_required.copy()

        # seed traces at t=0
        for i in range(env.number_evs):
            soc_traces[i].append(env.soc_current[i])
            timeleft_traces[i].append(env.time_left[i])
        times.append(0)

        # Print header for the table-like output
        header = [
            "Step", "Actions (Norm)", "Power Delivered (kWh)", "Net Power (kW)",
            "target_used(kW)", "Prev Time Left (h)", "Time Left (h)", "Departure Flag",
            "Terminated", "SOCs", "Total Reward", "Terminal Penalty", "Terminal Reward",
            "Step Penalty", "Step Reward", "Cycling Penalty", "grid_following_penalty",
            "fi_used", "fe_used"
        ]
        print(" | ".join(header))
        print("-" * (len(" | ".join(map(str, header))) + 2 * len(header)))  # separator line

        while not done and t < day_steps:
            # 1) Compute baseline site target
            refresh_feasibility(env)
            base_kw = site_target(env, baseline_mode)

            # 2) Optional activation
            if (activate_at is not None) and (env.current_step == int(activate_at)):
                act_left = int(activation_steps)
            desired_kw = np.clip(base_kw + (A if act_left > 0 else 0.0),
                                 env.feasible_export, env.feasible_import)
            act_left = max(0, act_left - 1)

            # 3) Feed the target into env BEFORE acting
            env.station_capacity = float(desired_kw)

            # 4) Policy acts (maddpg style)
            actions = maddpg.select_actions(obs, add_noise=False)
            action_vec = actions.flatten()

            # 5) Step
            next_obs, reward, terminated, truncated, info = env.step(action_vec)
            obs = next_obs
            done = terminated or truncated
            t += 1
            times.append(t)
            reward_traces.append(reward)

            # 6) Logs
            net_power_traces.append(info["net_exec_kw"])     # kW
            setpoint_traces.append(desired_kw)               # kW

            for k in reward_breakdowns:
                reward_breakdowns[k].append(info[k])

            for i in range(env.number_evs):
                power_traces[i].append(info['power_delivered'][i])
                if departures[i] is None and info["time_left"][i] <= 1e-8:
                    departures[i] = t
            for i in range(env.number_evs):
                soc_traces[i].append(env.soc_current[i])

            target_used = float(np.clip(env.station_capacity, info['fe_used'], info['fi_used']))

            # 7) Print row
            row_data = [
                t,
                np.round(action_vec, 3),
                np.round(info['power_delivered'], 3),
                np.round(net_power_traces[-1], 3),
                np.round(target_used, 3),
                np.round(info['prev_time_left'], 3),
                np.round(info['time_left'], 3),
                info['departed_flag'],
                info['terminated'],
                np.round(env.soc_current, 3),
                np.round(reward, 3),
                np.round(info['terminal_penalty'], 3),
                np.round(info['terminal_reward'], 3),
                np.round(info['step_penalty'], 3),
                np.round(info['step_reward'], 3),
                np.round(info['cycling_penalty'], 3),
                np.round(info['grid_following_penalty'], 3),
                np.round(info['fi_used'], 3),
                np.round(info['fe_used'], 3),
            ]
            print(" | ".join([str(item) for item in row_data]))

        # After 21h, plot results:
        plot_soc_power_reward_departure(
            times, soc_traces, power_traces, net_power_traces, setpoint_traces,
            reward_traces, soc_arrival_plot, soc_required_plot, departures,
            reward_breakdowns, env.max_station_capacity
        )
        print("="*60)
        print("Day finished (21h).")
        print("Final SOCs:        ", np.round(env.soc_current, 3))
        print("Final Power needed:", np.round(env.power_needed, 3))
        print("Arrival times (h):    ", np.round(env.arrival_time, 3))
        print("Departure times (h):  ", np.round(env.depart_time, 3))
        print("Present mask:         ", env.present)

# ---------------------------------------------------------
# Plotting (adds target trace to the Net Power subplot)
# ---------------------------------------------------------
def plot_soc_power_reward_departure(times, soc_traces, power_traces, net_power_traces, setpoint_traces,
                                    reward_traces, soc_arrival, soc_required, departures,
                                    reward_breakdowns, max_station_capacity):
    n_evs = len(soc_traces)
    fig, axs = plt.subplots(n_evs, 3, figsize=(21, 4 * n_evs))
    if n_evs == 1:
        axs = axs.reshape(1, -1)

    # Per-EV SOC and Power
    for i in range(n_evs):
        # SOC Progression
        axs[i,0].plot(times, soc_traces[i], label=f'EV {i+1} SOC')
        axs[i,0].axhline(y=soc_arrival[i], color='gray', linestyle='--', label="Arrival SOC")
        axs[i,0].axhline(y=soc_required[i], color='orange', linestyle='--', label="Requested SOC")
        if departures[i] is not None:
            axs[i,0].axvline(x=departures[i], color='red', linestyle=':', label="Departure Time")
        axs[i,0].set_ylabel('SOC')
        axs[i,0].set_title(f'EV {i+1} SOC Progression (21h)')
        axs[i,0].set_ylim(0, 1.05)
        #axs[i,0].set_xlim(0,24)
        axs[i,0].grid()
        axs[i,0].legend(loc="lower right")

        # Power Delivered per Step (kWh)
        axs[i,1].plot(times[1:], power_traces[i], color='green', label=f'EV {i+1} Power (kWh/step)')
        if departures[i] is not None:
            axs[i,1].axvline(x=departures[i], color='red', linestyle=':', label="Departure Time")
        axs[i,1].set_ylabel('kWh / step')
        axs[i,1].set_title(f'EV {i+1} Energy per Step')
        axs[i,1].grid()
        #axs[i,1].set_xlim(0,24)
        axs[i,1].legend()

    # Site Net Power vs. Target (kW)
    axs[0, 2].plot(times[1:], net_power_traces, label='Net Power (kW)')
    axs[0, 2].plot(times[1:], setpoint_traces, linestyle='--', label='Target (kW)')
    axs[0, 2].set_ylabel('kW')
    axs[0, 2].set_title('Site Net Power vs. Target (21h)')
    axs[0, 2].set_ylim(-max_station_capacity, max_station_capacity * 1.1)
    axs[0, 2].grid()
    axs[0, 2].legend()

    if n_evs > 1:
        fig.delaxes(axs[1, 2])  # remove extra axes if present

    # Total reward per step + breakdown
    plt.figure(figsize=(10, 5))
    plt.plot(times[1:], reward_traces, color='b', label='Total Reward')
    for k, trace in reward_breakdowns.items():
        plt.plot(times[1:], trace, linestyle='--', marker='.', label=k)
    plt.xlabel("Step")
    plt.ylabel("Reward")
    plt.title("Per-step Reward (Total & Components)")
    plt.legend(loc='best')
    plt.grid()
    plt.tight_layout()
    plt.show()

    plt.tight_layout()
    plt.show()

# -----------------------------------------
# Example calls
# -----------------------------------------
# 1) Full 21h with random reset, JIT baseline
# test_policy_21h_with_logging(env, maddpg, baseline_mode="JIT", n_days=1)

# 2) Full 21h with custom params, ASAP baseline, and a 15-min +300 kW activation at the start
custom_initial_params = {
    'time_now': 0.0,
     'arrival_time': [0.0, 0.0],
     'depart_time':  [2.0, 2.0],
     'soc_arrival':  [0.2, 0.2],
     'soc_required': [0.8, 0.8],
     'battery_capacity': [100, 100],
     'v2g_capable': [True, True],
     'activate_at':3,          # step index where activation begins
     'A': -300,                # kW delta during activation window
     'activation_steps': 3,     # 15 min if dt = 5 min
 }
test_policy_21h_with_logging(env, maddpg, baseline_mode="ASAP", n_days=1, custom_params=custom_initial_params)

# Or without custom params (random reset):
#test_policy_21h_with_logging(env, maddpg, baseline_mode="ASAP", n_days=1)