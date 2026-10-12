# STATUS: CURRENT RUNNER (EDF/ES/MARL selectable; MARL path is legacy). Fixed 21 h horizon = known limitation.

import numpy as np
import matplotlib.pyplot as plt

# Optional tiny wrapper so MARL matches the same call
class MARLController:
    def __init__(self, maddpg): self.maddpg = maddpg
    def select_actions(self, obs): return self.maddpg.select_actions(obs, add_noise=False)

def run_allocator_21h(env, *, allocator="EDF", baseline="JIT",
                      custom_params=None, maddpg=None, time_in_hours=False):


    # --- bind allocator ---
    alloc_name = (allocator or "EDF").upper()
    if alloc_name == "MARL":
        assert maddpg is not None, "MARL selected but maddpg=None"
        controller = MARLController(maddpg)
    elif alloc_name == "EDF":
        controller = "EDF"
    elif alloc_name == "ES":
        controller = "ES"
    else:
        raise ValueError("allocator must be EDF, ES or MARL")

    # --- day horizon ---
    day_steps = int(round(21.0 / env.dt))
    env.max_steps= day_steps
    env.max_time= 21.0

    # --- reset + (optional) overwrite with custom sampler params ---
    obs, _ = env.reset(seed=42)
    if custom_params:
        env.time_now  = float(custom_params.get('time_now', 0.0))
        env.arrival_time = np.array(custom_params['arrival_time'],dtype=np.float32)
        env.depart_time = np.array(custom_params['depart_time'], dtype=np.float32)
        env.soc_arrival= np.array(custom_params['soc_arrival'],dtype=np.float32)
        env.soc_required= np.array(custom_params['soc_required'], dtype=np.float32)
        env.battery_capacity= np.array(custom_params['battery_capacity'],dtype=np.float32)
        env.v2g_capable = np.array(custom_params['v2g_capable'], dtype=bool)
        env.soc_current = env.soc_arrival.copy()
        env.power_needed= (env.soc_required - env.soc_current) * env.battery_capacity
        env.inital_power_needed = env.power_needed.copy()

    # anchor earliest arrival at t=0
    shift = max(0.0, -float(np.min(env.arrival_time)))
    env.arrival_time+= shift
    env.depart_time += shift
    env.time_now = 0.0
    env.present   = (env.arrival_time <= env.time_now) & (env.time_now < env.depart_time)
    env.time_left = np.where(env.present, env.depart_time - env.time_now, 0.0).astype(np.float32)
    env.current_step = 0

    # keep absolute hours for plotting
    arrivals_h   = env.arrival_time.copy()
    departures_h = env.depart_time.copy()

    # initial setpoint + obs
    env.station_capacity = site_target(env, baseline)
    obs = build_obs_from_env(env)

    # --- traces ---
    n = env.number_evs
    soc_traces   = [[env.soc_current[i]] for i in range(n)]
    power_traces = [[] for _ in range(n)]
    reward_tr    = []
    net_kw_tr    = []
    sp_kw_tr     = []
    times        = [0]
    dep_step     = [None]*n
    soc_arrival_plot  = env.soc_arrival.copy()
    soc_required_plot = env.soc_required.copy()

    # --- loop ---
    t, done = 0, False
    while not done and t < day_steps:
        env.station_capacity = site_target(env, baseline)

        if alloc_name == "MARL":
            actions = controller.select_actions(obs).flatten()
        elif alloc_name == "EDF":
            actions = edf_actions(env).flatten()
        else:
            actions = es_actions(env).flatten()

        next_obs, reward, terminated, truncated, info = env.step(actions)
        obs, done = next_obs, (terminated or truncated)
        t += 1
        times.append(t)

        # logs
        reward_tr.append(reward)
        net_kw_tr.append(info["net_exec_kw"])
        sp_kw_tr.append(env.station_capacity)
        for i in range(n):
            power_traces[i].append(info["power_delivered"][i])
            if dep_step[i] is None and bool(info["departed_flag"][i]):
                dep_step[i] = t
            soc_traces[i].append(env.soc_current[i])

    # --- plots ---
    plot_hdev_day(times, soc_traces, power_traces,
                  net_kw_tr, sp_kw_tr, reward_tr,
                  soc_arrival_plot, soc_required_plot,
                  arrivals_h, departures_h,
                  env.max_station_capacity, env.dt, time_in_hours=time_in_hours)

# --- compact plotting, side-by-side per HDEV; net power in separate fig ---
def plot_hdev_day(times, soc_traces, power_traces,
                  net_power_traces, setpoint_traces, reward_traces,
                  soc_arrival, soc_required, arrivals_h, departures_h,
                  max_station_capacity, dt, *, time_in_hours=False):


    x_soc  = np.asarray(times)      * (dt if time_in_hours else 1.0)
    x_step = np.asarray(times[1:])  * (dt if time_in_hours else 1.0)
    xlab   = "Hour" if time_in_hours else "Step"

    def hour_to_axis(h):
        return float(h) if time_in_hours else float(h)/float(dt)

    n = len(soc_traces)
    # CHANGE 1: Swapped (2, n) to (n, 2) and adjusted figsize for a vertical layout.
    fig, axs = plt.subplots(n, 2, figsize=(12, 4 * n), squeeze=False)

    for i in range(n):
        # CHANGE 2: Updated subplot index from [0, i] to [i, 0] for the SOC plot (left column).
        ax = axs[i, 0]
        ax.plot(x_soc, soc_traces[i], label=f'HDEV {i+1} SOC')
        ax.axhline(soc_arrival[i],  color='gray',   linestyle='--', label='Arrival SOC')
        ax.axhline(soc_required[i], color='orange', linestyle='--', label='Requested SOC')
        ax.axvline(hour_to_axis(arrivals_h[i]),  color='green', linestyle=':', label='Arrival')
        ax.axvline(hour_to_axis(departures_h[i]),color='red',   linestyle=':', label='Departure')
        ax.set_ylabel('SOC'); ax.set_xlabel(xlab)
        ax.set_title(f'HDEV {i+1} SOC ')
        ax.set_ylim(0, 1.05); ax.grid(True); ax.legend(loc='lower right')

        kw = np.asarray(power_traces[i]) / float(dt)
        # CHANGE 3: Updated subplot index from [1, i] to [i, 1] for the Power plot (right column).
        axp = axs[i, 1]
        axp.step(x_step, kw, where='post', color='green', label=f'HDEV {i+1} Power (kW)')
        axp.axvline(hour_to_axis(arrivals_h[i]),  color='green', linestyle=':')
        axp.axvline(hour_to_axis(departures_h[i]),color='red',   linestyle=':')
        axp.axhline(0.0, color='k', lw=0.8)
        axp.set_ylabel('kW'); axp.set_xlabel(xlab)
        axp.set_title(f'HDEV {i+1} Power per Step')
        axp.grid(True); axp.legend()
        axp.set_ylim(0,155)

    plt.tight_layout(); plt.show()

    # --- This part of the code remains unchanged ---
    plt.figure(figsize=(12,5))
    plt.step(x_step, net_power_traces, where='post', label='Net Power (kW)')
    plt.step(x_step, setpoint_traces,  where='post', linestyle='--', label='Target (kW)')
    for i in range(n):
        plt.axvline(hour_to_axis(arrivals_h[i]),  color='green', alpha=0.15, linestyle=':')
        plt.axvline(hour_to_axis(departures_h[i]),color='red',   alpha=0.15, linestyle=':')
    plt.axhline(0.0, color='k', lw=0.8)
    plt.ylabel('kW'); plt.xlabel(xlab)
    plt.title('Site Net Power vs. Target ')
    plt.ylim(-max_station_capacity, max_station_capacity*1.1)
    plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()

    plt.figure(figsize=(10,5))
    plt.plot(x_step, reward_traces, color='b', label='Total Reward')
    plt.xlabel(xlab); plt.ylabel('Reward'); plt.title('Per-step Reward')
    plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()
