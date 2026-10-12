# STATUS: CURRENT (thesis gym-style depot env). Pasted by Bob 12 Oct 2026.
# Physics-only env: presence, need, charger rate, site cap. Policies (ASAP/JIT/cheapest-first) set the site target outside the env.
# MADDPG/MARL is no longer part of HDEV; reward + observation code is thesis legacy (only needed by MARL).
# Known: reset() randomises everything (thesis training); hard-coded /21 normalisation; 21 h episode end in testers.
# Needs `import gym, numpy as np, from gym import spaces`.

###----ENVIRONMENT-----############
class EVChargingEnv(gym.Env):

    def __init__(self,
                 number_evs,                 # number of agents
                 max_station_capacity,       # Station capacity (kW)
                 max_steps,                  # max number of time steps in an episode
                 max_charging_rate,          # Max charging rate per EV (kW)
                 max_battery_capacity,       # Max possible battery capacity (kWh)
                 v2g_probability,            # V2G distribution in fleet
                 min_soc_v2g,                # Min SOC for V2G
                 max_soc_v2g,                # Max SOC for V2G
                 max_time,                   # max time horizon in hours (e.g., 12h)
                 dt):                        # time step in hours, e.g., 5/60
        super().__init__()

        # Initialize fixed variables
        self.number_evs = number_evs
        self.max_station_capacity = max_station_capacity
        self.max_steps = max_steps
        self.max_charging_rate = max_charging_rate
        self.max_battery_capacity = max_battery_capacity
        self.v2g_probability = v2g_probability
        self.min_soc_v2g = min_soc_v2g
        self.max_soc_v2g = max_soc_v2g
        self.max_time = max_time                    # <-- fixed (was simulation_time)
        self.dt = dt

        # Initialize arrays for multi-agent variables - to be initialized in reset()
        self.soc_arrival = np.zeros(self.number_evs, dtype=np.float32)
        self.soc_current = np.zeros(self.number_evs, dtype=np.float32)
        self.soc_required = np.zeros(self.number_evs, dtype=np.float32)
        self.time_left = np.zeros(self.number_evs, dtype=np.float32)
        self.battery_capacity = np.zeros(self.number_evs, dtype=np.float32)
        self.power_needed = np.zeros(self.number_evs, dtype=np.float32)
        self.v2g_capable = np.zeros(self.number_evs, dtype=bool)   # v2g flag
        self.station_capacity = 0.0
        self.current_step = 0
        self.departed_flag = None
        self.activation_mask = None

        # NEW: arrivals / departures / presence / episode clock
        self.arrival_time = np.zeros(self.number_evs, dtype=np.float32)   # hours since episode start
        self.depart_time  = np.zeros(self.number_evs, dtype=np.float32)   # hours since episode start
        self.present      = np.zeros(self.number_evs, dtype=bool)         # plugged/inside window flag
        self.time_now     = 0.0
        self.feasible_import = 0.0
        self.feasible_export = 0.0
        self.schedule      = np.zeros(self.max_steps, dtype=np.float32)


        ## Observation space - flattened observation for ALL EVs
        # Per-EV features: [need_norm, signed_time, station_norm, feasible_import, feasible_export, v2g_flag]
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(self.number_evs * 6,), dtype=np.float32)

        ## Action space - flattened action for ALL EVs (normalized)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(self.number_evs,), dtype=np.float32)

    ###----RESET-----############
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        rng = np.random.default_rng(seed)


        ## Value assigning
        self.soc_arrival = rng.uniform(0.1, 0.99, size=self.number_evs).astype(np.float32)
        self.soc_current = self.soc_arrival.copy()
        self.soc_required = rng.uniform(self.soc_arrival, 1.0, size=self.number_evs).astype(np.float32)

        # Episode clock
        self.time_now = 0.0

        # Arrivals during this episode window; departures up to max_time
        abs_arrival_time = rng.uniform(0.0, 5.0, size=self.number_evs).astype(np.float32)
        abs_depart_time = rng.uniform(14.0, 18.0, size=self.number_evs).astype(np.float32)
        dwell = abs_depart_time - abs_arrival_time

        snippet_time = rng.uniform(0.0, 21.0-1.0)

        self.arrival_time = abs_arrival_time - snippet_time
        self.depart_time  = abs_depart_time  - snippet_time

        self.present = (self.arrival_time <= self.time_now) & (self.time_now < self.depart_time)

        # Presence at t=0 and time_left (only for present EVs)
        ##---self.present = (self.arrival_time <= self.time_now) & (self.time_now < self.depart_time)
        self.time_left = np.where(self.present, self.depart_time - self.time_now, 0.0).astype(np.float32) # used for book keeping i guess

        self.battery_capacity = rng.choice([380,480,600], size=self.number_evs).astype(np.float32)
        self.power_needed = (self.soc_required - self.soc_arrival) * self.battery_capacity
        self.inital_power_needed = self.power_needed.copy()

        #self.v2g_probability = rng.choice([0.0, 0.2 ,0.5, 0.75, 1.0])
        self.v2g_capable = rng.random(self.number_evs) < self.v2g_probability

       #--self.station_capacity = rng.uniform(-300, 300)  # kW

        self.current_step = 0

        #self.station_capacity = float(self.schedule[0]) if (self.activation_mask and self.schedule.size) else 0.0
        number_present_evs = np.sum(self.present)
        is_v2g_present = np.where(self.present & self.v2g_capable, 1.0, 0.0)
        number_v2g_present = np.sum(is_v2g_present)
        self.station_capacity = rng.uniform(-(number_v2g_present*self.max_charging_rate) ,self.number_evs * self.max_charging_rate)

        #Calculate feasible headrooms
        per_ev_power_need = np.where(self.present, np.maximum(self.power_needed,0.0), 0.0)
        capped_power_per_ev = np.minimum(per_ev_power_need/self.dt, self.max_charging_rate)
        sum_capped_power = np.sum(capped_power_per_ev)
        self.feasible_import = float( np.minimum(sum_capped_power, self.max_station_capacity))

        per_ev_headroom = np.where(self.present & self.v2g_capable & (self.soc_current > self.min_soc_v2g), (self.soc_current-self.min_soc_v2g) * self.battery_capacity, 0.0)
        capped_headroom_per_ev = np.minimum(per_ev_headroom/self.dt, self.max_charging_rate)
        sum_capped_headroom = np.sum(capped_headroom_per_ev)
        self.feasible_export = - float(np.minimum(sum_capped_headroom, self.max_station_capacity))

        # Signed time

        time_to_arrival = np.maximum(0.0, self.arrival_time - self.time_now)
        time_to_depart  = np.maximum(0.0, self.depart_time  - self.time_now)
        signed_time = np.where(self.present, time_to_depart, -time_to_arrival) / 21
        signed_time = signed_time.astype(np.float32)


        # Build observation
        normalized_power_needed = np.where(self.present, self.power_needed / self.max_battery_capacity, 0.0).astype(np.float32) #mask need for absent EVs
        normalized_station_capacity = np.full(self.number_evs, (self.station_capacity / self.max_station_capacity), dtype=np.float32)
        normalized_feasible_import = np.full(self.number_evs, (self.feasible_import / self.max_station_capacity), dtype=np.float32)
        normalized_feasible_export = np.full(self.number_evs, (self.feasible_export / self.max_station_capacity), dtype=np.float32)

        normalized_v2g = self.v2g_capable.astype(np.float32)


        obs_2d = np.stack([normalized_power_needed, signed_time, normalized_station_capacity, normalized_feasible_import, normalized_feasible_export, normalized_v2g], axis=-1)
        obs = obs_2d.flatten().astype(np.float32)

        return obs, {}

    ###----REWARD-----############
    def calculate_reward(self, power_delivered: np.array, net_exec_kw: np.array,overshoot_ev: np.array):

        weight_step_reward = 0.00
        weight_step_penalty = -1
        weight_terminal_reward = 0
        weight_terminal_penalty = -0
        cost_of_degradation = -0.125
        weight_grid_following = -2


        #grid following penalty
        feasible_tracking = np.clip (self.station_capacity, self.feasible_export, self.feasible_import)
        err_kw = max(0.0, abs(float(net_exec_kw) - float(feasible_tracking)) -0.125) #-0.5
        grid_following_penalty = weight_grid_following * err_kw
        #commented out -- grid_following_penalty = (np.abs(feasible_tracking - net_exec_kw) - 0.5) * weight_grid_following #deadnband of .5kW

        # over shoot penalty - overshoot SOC, overshoot raw more than whats feasible or legal prior to scaling
        overshoot_penalty = np.sum(overshoot_ev)
        #station_cap_penalty = np.clip(np.abs(np.sum(self.raw_power_delivered)) - np.abs(self.max_station_capacity), 0.0, None)
        step_penalty = ( overshoot_penalty) * weight_step_penalty

        # Cycling penalty
        #--cycling_penalty = cost_of_degradation * np.sum(np.abs(power_delivered))
        cycling_penalty = cost_of_degradation * np.sum(np.clip(power_delivered, 0.0, None)) + cost_of_degradation * (1.0 + float(feasible_tracking >= 0.0)) * np.sum(np.clip(-power_delivered, 0.0, None))

        #step rewards
        step_reward = np.sum(np.clip(power_delivered, 0.0, None)) * weight_step_reward # reward positive Kwh provided

        '''# Terminal rewards (kept as-is; based on time_left transitions) -- inactive for now
        success = np.isclose(self.power_needed, 0, atol=0.5)
        matches = self.departed_flag & success
        misses = self.departed_flag & ~success
        terminal_reward = np.sum(matches) * weight_terminal_reward
        terminal_penalty = np.sum(np.abs(self.power_needed[misses])) * weight_terminal_penalty  '''
        terminal_reward = 0.0
        terminal_penalty = 0.0

        total_reward = terminal_reward + terminal_penalty + step_reward + step_penalty + cycling_penalty + grid_following_penalty

        return total_reward, terminal_reward, terminal_penalty, step_reward, step_penalty, cycling_penalty,  grid_following_penalty

    ###----STEP-----############
    def step(self, action: np.array):

        #Presence BEFORE acting
        present_prev = self.present.copy()

        # Clip - no action if EV not present
        action = np.where(present_prev, action, 0.0)

        # Clip - action for V2G / non-V2G
        action = np.where(self.v2g_capable, np.clip(action, -1, 1), np.clip(action, 0, 1))

        # Clip - action if no time left
        action = np.where(self.time_left <= 0, 0, action)

        # SOC padding for V2G lower limit + full battery clamp
        action = np.where((self.soc_current <= self.min_soc_v2g) & (action < 0), 0, action)

        action = np.where((self.soc_current >= 1) & (action > 0), 0, action) # now blocks only charge not discharge
        #action = np.where(self.soc_current >= 1, 0, action)

        # Convert to kW
        action_kw = action * self.max_charging_rate

        prev_time_left = self.time_left.copy()

        # Energy delivered this step (kWh)
        raw_power_delivered = action_kw * self.dt

        # Raw charge and discharge delivered
        raw_charge_delivered = np.clip (raw_power_delivered, 0.0, None)
        raw_discharge_delivered = np.clip (-raw_power_delivered, 0.0 , None)

        charge_need = np.where(present_prev, np.clip(self.power_needed, 0.0, None), 0.0)
        charge_headroom = np.where(present_prev , np.clip((1-self.soc_current)*self.battery_capacity,0.0,None), 0.0)

        v2g_mask = present_prev & self.v2g_capable & (self.soc_current > self.min_soc_v2g)
        discharge_headroom = np.where(v2g_mask, np.clip ((self.soc_current-self.min_soc_v2g)*self.battery_capacity, 0.0,None),0.0)

        #effective charge delivered
        charge_delivered = np.minimum (raw_charge_delivered, np.minimum(charge_need, charge_headroom))
        discharge_delivered = np.minimum (raw_discharge_delivered, discharge_headroom)

        power_delivered = charge_delivered - discharge_delivered # constructing back the array after clips and giving discharge back the -ve sign
        overshoot_ev = (raw_charge_delivered - charge_delivered) + (raw_discharge_delivered - discharge_delivered)  # kWh ≥ 0: array containing overshoots for each EV

        #Calculate feasible headrooms + calculate each step as did in reset()
        per_ev_power_need = np.where(self.present, np.maximum(self.power_needed,0.0), 0.0)
        capped_power_per_ev = np.minimum(per_ev_power_need/self.dt, self.max_charging_rate)
        sum_capped_power = np.sum(capped_power_per_ev)
        self.feasible_import = float( np.minimum(sum_capped_power, self.max_station_capacity))

        per_ev_headroom = np.where(self.present & self.v2g_capable & (self.soc_current > self.min_soc_v2g), (self.soc_current-self.min_soc_v2g) * self.battery_capacity, 0.0)
        capped_headroom_per_ev = np.minimum(per_ev_headroom/self.dt, self.max_charging_rate)
        sum_capped_headroom = np.sum(capped_headroom_per_ev)
        self.feasible_export = - float(np.minimum(sum_capped_headroom, self.max_station_capacity))

        # Station capacity scaling
        net_action_kw = np.sum(power_delivered/self.dt)

        if abs(net_action_kw) > self.max_station_capacity:
            power_delivered = power_delivered * (self.max_station_capacity / abs(net_action_kw))

        #cache , power_delivered is in kWh ,net_action_kw is in kW total site usage, action_kw_per_ev is kW per ev,
        net_exec_kw = float(np.sum(power_delivered/self.dt))
        action_kw_per_ev = power_delivered / self.dt

        fi_used = self.feasible_import
        fe_used = self.feasible_export

        # Reward (unchanged interface) to be worked on next ignore for now
        reward, terminal_reward, terminal_penalty, step_reward, step_penalty, cycling_penalty, grid_following_penalty =  self.calculate_reward(power_delivered, net_exec_kw, overshoot_ev)

        # Update power need and SOC ; np.max helps tiny negative floating points i hope
        self.power_needed = np.maximum(self.power_needed - power_delivered, 0.0) # effective chagre reduces power_need, effective dischrge increase power_need
        self.soc_current = np.clip(self.soc_current + power_delivered / (self.battery_capacity + 1e-9), 0, 1.0)

        # Advance clock and recompute presence / time_left
        self.time_now += self.dt
        self.present = (self.arrival_time <= self.time_now) & (self.time_now < self.depart_time)
        self.time_left = np.where(self.present, self.depart_time - self.time_now, 0.0).astype(np.float32)

        # Who departed exactly this step
        self.departed_flag = (~self.present) & present_prev

        self.current_step += 1

        #Calculate feasible headrooms + calculate each step as did in reset()
        per_ev_power_need = np.where(self.present, np.maximum(self.power_needed,0.0), 0.0)
        capped_power_per_ev = np.minimum(per_ev_power_need/self.dt, self.max_charging_rate)
        sum_capped_power = np.sum(capped_power_per_ev)
        self.feasible_import = float( np.minimum(sum_capped_power, self.max_station_capacity))

        per_ev_headroom = np.where(self.present & self.v2g_capable & (self.soc_current > self.min_soc_v2g), (self.soc_current-self.min_soc_v2g) * self.battery_capacity, 0.0)
        capped_headroom_per_ev = np.minimum(per_ev_headroom/self.dt, self.max_charging_rate)
        sum_capped_headroom = np.sum(capped_headroom_per_ev)
        self.feasible_export = - float(np.minimum(sum_capped_headroom, self.max_station_capacity))

        # Build observation (same as in reset)
        normalized_power_needed = np.where(self.present, self.power_needed / self.max_battery_capacity, 0.0).astype(np.float32)

        time_to_arrival = np.maximum(0.0, self.arrival_time - self.time_now)
        time_to_depart = np.maximum(0.0, self.depart_time  - self.time_now)
        signed_time = np.where(self.present, +time_to_depart, -time_to_arrival) / 21.0
        signed_time = signed_time.astype(np.float32)


        normalized_station_capacity = np.full(self.number_evs, (self.station_capacity / self.max_station_capacity), dtype=np.float32)

        normalized_feasible_import = np.full(self.number_evs, (self.feasible_import / self.max_station_capacity), dtype=np.float32)
        normalized_feasible_export = np.full(self.number_evs, (self.feasible_export / self.max_station_capacity), dtype=np.float32)


        normalized_v2g = self.v2g_capable.astype(np.float32)

        obs_2d = np.stack([normalized_power_needed, signed_time, normalized_station_capacity, normalized_feasible_import, normalized_feasible_export, normalized_v2g], axis=-1)
        obs = obs_2d.flatten().astype(np.float32)

        # Termination: episode horizon only
        terminated = (self.current_step >= self.max_steps)
        truncated = False

        info = {
            "cycling_penalty": cycling_penalty,
            "soc_current": self.soc_current.copy(),
            "soc_arrival": self.soc_arrival.copy(),
            "soc_required": self.soc_required.copy(),
            "power_needed": self.power_needed.copy(),
            "battery_capacity": self.battery_capacity.copy(),
            "time_left": self.time_left.copy(),
            "arrival_time": self.arrival_time.copy(),
            "depart_time": self.depart_time.copy(),
            "present": self.present.copy(),
            "v2g_capable": self.v2g_capable.copy(),
            "station_capacity": self.station_capacity,
            "power_delivered": power_delivered.copy(),
            "terminal_reward": terminal_reward,
            "terminal_penalty": terminal_penalty,
            "step_reward": step_reward,
            "step_penalty": step_penalty,
            "reward": reward,
            "prev_time_left": prev_time_left.copy(),
            "departed_flag": self.departed_flag.copy(),
            "terminated": terminated,
            "grid_following_penalty": grid_following_penalty,
            "net_exec_kw": net_exec_kw,
            "feasible_import": self.feasible_import,
            "feasible_export": self.feasible_export,
            "fi_used": fi_used,
            "fe_used": fe_used,
            "overshoot_ev": overshoot_ev,


        }

        return obs, reward, terminated, truncated, info