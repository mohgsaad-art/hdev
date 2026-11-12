# Appendix 1 of the Kiro prompt, typed in as delivered (used only by Gate 2 to compare with the notebook).
HVAC_THERMAL = '''def HVAC_thermal(T_amb, solar, A_surface, U, N_persons, A_window, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points,
                 hp_share_points, eh_share_points, fuel_share_points, max_heating_power, max_cooling_power, cab_volume, vent_rate, vent_rate_heating,
                 eh_eff=0.93, spec_vent_power=0.56, heat_per_person=(50.0, 80.0), clouding=(0.65, 0.8), T_boundary=17.0, g=0.95, solar_factor=0.25,
                 waste_heat=0.0, T_heat=18.0, T_cool=23.0, T_cool_off=17.0, Q=0.0, p=101325.0, R=287.05, cp=1005.0):
  # Tcalc just becomes the two setpoints for heating and cooling
  T_amb = np.asarray(T_amb, dtype=float)

  # step 1: run ssm total i.e. total heat balance at 18 and 23 C, and get the heating or cooling demand
  run1 = ssm_total_w(T_amb, solar, T_heat, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)
  run2 = ssm_total_w(T_amb, solar, T_cool, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)

  losing_heat = (run1 < 0) & (run2 < 0)
  heating_demand = np.where(losing_heat, np.abs(np.maximum(run1, run2))-waste_heat,0.0)
  heating_demand = np.maximum(heating_demand, 0.0)

  #step 2: how this heat is split between heat pump, electrical heater, and fuel heater and their caps at diff temps SSMCalculate.cs lines 215-245
  cop_heat, cop_cool, hp_share, eh_share, fuel_share = climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points)

  fuel_heat = heating_demand * fuel_share                                            # fuel heater part, not capped here
  sum_heat = np.minimum(max_heating_power, heating_demand * (hp_share + eh_share))   # cap on heat pump + electric heater only

  rest = np.where(np.isclose(fuel_share, 1.0), 1.0, 1 - fuel_share)  # heat pump + el. heater's part; 1.0 if fuel does everything
  scale = sum_heat / rest                                                    # getting a scaling factor to downside but keep ratio
  hp_heat = scale * hp_share                                                 # heat delivered by heat pump [W]
  eh_heat = scale * eh_share                                                 # heat delivered by electric heater [W]

  #step 3: heating W to what it costs the batery W
  if np.any((hp_heat > 0) & np.isnan(cop_heat)):
    raise ValueError("heat pump COP missing for this temperature")  # HDEV: VECTO silently gives 0 W here
  HP_el = np.where(hp_heat > 0, hp_heat / cop_heat, 0.0)             # heat pump: heat ÷ COP
  EH_el = eh_heat / eh_eff                                           # battery W for el heating

  #step 4: cooling
  gaining_heat = (run1 > 0) & (run2 > 0) & (T_amb >= T_cool_off)            # gaining heat at both 18 and 23 setpoint, and Tamb greater than 17
  cooling_demand = np.where(gaining_heat, np.minimum(run1, run2), 0.0)      # cooling demand / heat to remove W, smaller of the two = cool to 23C
  cooling_demand = np.minimum(cooling_demand, max_cooling_power)            # cap at AC max cooling power
  if np.any((cooling_demand > 0) & np.isnan(cop_cool)):
      raise ValueError("cooling COP missing for this temperature")
  AC_el = np.where(cooling_demand > 0, cooling_demand / cop_cool, 0.0)                # battery W for cooling

  #step 5; ventilation fan, VECTO SSMCalculate.cs lines 270-295, 376-397, 399-428; VentPower (SSMInputs.cs:88)
  ventillation_status = ((T_amb < T_cool_off) & (run1 > 0) & (run2 > 0)) | ((run1 > 0) & (run2 < 0))
  fan_rate = np.where(losing_heat, vent_rate_heating, np.where(gaining_heat | ventillation_status, vent_rate, 0.0)) # air changes per hour
  fan_el = cab_volume * fan_rate * spec_vent_power  #m³ × 1/h × Wh/m³ = W

  #step 6: total battery W for HVAC (goes into P_aux as HVAC_power with HVAC_eff = 1.0)
  HVAC_el = HP_el + EH_el + AC_el + fan_el    # heat pump + electric heater + AC + fan [W electric]
  return HVAC_el, fuel_heat                   # fuel_heat = heat from the diesel heater [W heat], not battery'''
SSM_TOTAL_W = '''# this is a helper for HVAC thermal
# step 1: cabin heat balance, VECTO SSMRun.TotalW (SSMRun.cs lines 48-64)
def ssm_total_w(T_amb, solar, T_calc, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q):
#ambient Temp, Cabin temp target, surface area cabin, heat dissapation , num of people, surface area of windows, heat per person, clouding low or high, Temp switch for body heat and clouding, solar allowance of windows, soalr factor is unknown?
  T_amb = np.asarray(T_amb, dtype=float) # outside temp per weather hour [°C]
  solar = np.asarray(solar, dtype=float) # sunlight per weather hour [W/m²]
  rho = p / (R * (T_amb + 273.15)) # density of outside air

  q_wall = (T_amb - T_calc) * A_surface * U    #heat thru walls, diff in amb temp and cabin temp * surface area of cabin and heat permissivity
  q_people = N_persons * np.where(T_amb < T_boundary, heat_per_person[0], heat_per_person[1]) # heat thru people, no of people * their body heat based on amb Temp
  q_solar = solar * A_window * g * np.where(T_amb < T_boundary, clouding[0], clouding[1]) * solar_factor # heat from the sun passing thru windows based on clouding
  q_freshair = rho * cp * Q / 3600 * (T_amb - T_calc)
  return q_wall + q_people + q_solar + q_freshair'''
CLIMATE_LOOKUP = '''#This is a helper for HVAC thermal
def climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points):
  # abm temp,5 VECTO heat points
  T_amb = np.asarray(T_amb, dtype=float)

  cop_heat = np.interp(T_amb, T_heat_points, cop_heat_points)  # heat pump heating COP per hour
  cop_cool = np.interp(T_amb, T_cool_points, cop_cool_points)  # cooling COP per hour

  dist = np.abs(T_amb[..., None] - np.asarray(T_heat_points, dtype=float))  # distance from each hour to each heating point
  idx = np.argmin(dist, axis=-1)                          # nearest point; on a tie argmin takes the first = colder

  hp_share = np.asarray(hp_share_points, dtype=float)[idx]     # heat pump part of the heat
  eh_share = np.asarray(eh_share_points, dtype=float)[idx]     # electric heater part
  fuel_share = np.asarray(fuel_share_points, dtype=float)[idx] # fuel heater part

  return cop_heat, cop_cool, hp_share, eh_share, fuel_share'''
