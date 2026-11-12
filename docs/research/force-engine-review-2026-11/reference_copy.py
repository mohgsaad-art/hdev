"""Reference copy of Bob's wheel-power code + clearly named experimental variants (12 Nov 2026).

RULE: nothing here is used by the engine. The first two functions are VERBATIM copies of the code of record
(force_engine = notebook cell 8; wheel_power_steps_1_to_4 = steps 1-4 of consumption_engine, notebook cell 16).
Everything below the marker "VARIANTS" is an experiment, named so it cannot be mistaken for Bob's code.
Every variant states: engine or parser, and which source it is based on.
"""
import numpy as np


# ======================================================================================= VERBATIM COPIES
def force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red):
  speed = np.asarray(speed, dtype=float) # speed at start of the step
  accel = np.asarray(accel, dtype=float) # acceleration of the vehicle
  dt_s = np.asarray(dt_s, dtype=float)  # time step, s
  grade = np.asarray(grade, dtype=float) # gradient

  grade = np.arctan(grade / 100) # turns gradient in % into an angle in radians
  v1 = speed
  v2 = np.maximum(speed + accel * dt_s, 0.0) # speed cannot go below 0, as in the driver model
  v_avg = (v1 + v2)/2  #speed in m/s

  k_lin = (g * np.sin(grade) + accel) * v_avg
  k_roll = Crr * g * np.cos(grade) * v_avg
  k_rot = (theta_red / r_dyn**2) * accel * v_avg if theta_red > 0 else np.zeros_like(v_avg) # no rotating mass unless given
  L = (v1 + v2) * (v1**2 + v2**2) / 8 # exact average of 0.5*v^3 over the step as VECTO CrosswindCorrectionCdxALookup

  return k_lin, k_roll, k_rot, L, v_avg # we are taking out v_avg so we can use it to look up CdxA


def wheel_power_steps_1_to_4(T, S, V, k_lin, k_roll, k_rot, L, v_avg, m_vehicle, wp_s, payload_wp, beta,
                             t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air):
  """Steps 1-4 of consumption_engine (cell 16), same statements, returns P_wheel only."""
  T, S, V = (np.asarray(x) for x in (T, S, V))
  wp_s, payload_wp = np.asarray(wp_s, dtype=float), np.asarray(payload_wp, dtype=float)
  T_amb_h, cdxa_v = np.asarray(T_amb_h, dtype=float), np.asarray(cdxa_v, dtype=float)

  has_pl = ~np.isnan(payload_wp)
  k_pl = np.searchsorted(wp_s[has_pl], S, side="right") - 1
  m_row = m_vehicle + payload_wp[has_pl][k_pl]

  hour = ((t_start + T) // 3600).astype(int)

  rho_row = p_air / (R_air * (T_amb_h[hour] + 273.15))

  cdxa_tab = CdxA0 * np.asarray(W1) + np.asarray(W2)
  v_kmh = np.clip(v_avg * 3.6, cdxa_v[0], cdxa_v[-1])
  j = np.clip(np.searchsorted(cdxa_v, v_kmh, side="right") - 1, 0, len(cdxa_v) - 2)
  w = (v_kmh - cdxa_v[j]) / (cdxa_v[j+1] - cdxa_v[j])
  cdxa_row = cdxa_tab[hour, j] * (1 - w) + cdxa_tab[hour, j+1] * w

  P_wheel = m_row * k_lin + m_row**beta * k_roll + k_rot + rho_row * cdxa_row * L
  return P_wheel


# ======================================================================================= VARIANTS
# ---- V1  force_engine_v_asin  [ENGINE]  Q1 candidate: treat the % grade as sin(theta), cos from sqrt(1-G^2)
def force_engine_v_asin(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red):
  """Only the grade line differs: arcsin instead of arctan. VECTO uses atan (DistanceBasedDrivingCycle.cs / VectoMath.InclinationToAngle),
  so this is NOT closer to VECTO. It is here to measure the size of the choice."""
  speed = np.asarray(speed, dtype=float); accel = np.asarray(accel, dtype=float)
  dt_s = np.asarray(dt_s, dtype=float); grade = np.asarray(grade, dtype=float)
  grade = np.arcsin(grade / 100)
  v1 = speed
  v2 = np.maximum(speed + accel * dt_s, 0.0)
  v_avg = (v1 + v2) / 2
  k_lin = (g * np.sin(grade) + accel) * v_avg
  k_roll = Crr * g * np.cos(grade) * v_avg
  k_rot = (theta_red / r_dyn**2) * accel * v_avg if theta_red > 0 else np.zeros_like(v_avg)
  L = (v1 + v2) * (v1**2 + v2**2) / 8
  return k_lin, k_roll, k_rot, L, v_avg


# ---- V2  force_engine_v_rotor  [ENGINE, pure maths]  theta_red may be an array (gear-dependent reflected rotor inertia)
def force_engine_v_rotor(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red):
  """Same as the code of record, but the `if theta_red > 0` branch is replaced by plain arithmetic, so theta_red can be a
  scalar or one value per row (e.g. theta_wheels + J_rotor * i_row**2). Checks (theta >= 0, r_dyn > 0) belong in the parser."""
  speed = np.asarray(speed, dtype=float); accel = np.asarray(accel, dtype=float)
  dt_s = np.asarray(dt_s, dtype=float); grade = np.asarray(grade, dtype=float)
  grade = np.arctan(grade / 100)
  v1 = speed
  v2 = np.maximum(speed + accel * dt_s, 0.0)
  v_avg = (v1 + v2) / 2
  k_lin = (g * np.sin(grade) + accel) * v_avg
  k_roll = Crr * g * np.cos(grade) * v_avg
  k_rot = (np.asarray(theta_red, dtype=float) / np.asarray(r_dyn, dtype=float)**2) * accel * v_avg
  L = (v1 + v2) * (v1**2 + v2**2) / 8
  return k_lin, k_roll, k_rot, L, v_avg


# ---- V3  step 4 with an hourly rolling-resistance factor  [CONSUMPTION ENGINE step 4; factor supplied by the PARSER]
def wheel_power_v_roll_factor(m_row, beta, k_lin, k_roll, k_rot, rho_row, cdxa_row, L, f_roll_row):
  """P_wheel = m*k_lin + f_roll * m**beta * k_roll + k_rot + rho*CdxA*L.   f_roll_row = f(T_amb[hour]) (parser gives one factor per weather hour).
  force_engine stays mass-, temperature- and CdxA-free (rule 8): the factor only multiplies a coefficient that already exists."""
  return m_row * k_lin + f_roll_row * m_row**beta * k_roll + k_rot + rho_row * cdxa_row * L


def f_roll_linear_between_sourced_points(T_c, T_hot=20.0, f_hot=1.0, T_cold=-20.0, f_cold=2.0):
  """ASSUMPTION: straight line between the two numbers printed in Ramesh Babu et al. 2025 (Thermal Sci. Eng. Progress 60, 103417, p.10):
  mean Crr 0.007 at 20 degC and 0.014 at -20 degC (a MODEL result built on Hyttinen et al. 2023, not a measurement).
  Held at f_hot above T_hot and at f_cold below T_cold. The paper's Fig. 14 (the real curve) is not in the text layer."""
  T_c = np.asarray(T_c, dtype=float)
  f = f_hot + (f_cold - f_hot) * (T_hot - T_c) / (T_hot - T_cold)
  return np.clip(f, min(f_hot, f_cold), max(f_hot, f_cold))


# ---- V4  air density variants  [PARSER computes rho per weather hour and hands it over; engine uses rho as before]
def rho_ideal_dry(T_c, p=101325.0, R=287.05):
  return p / (R * (np.asarray(T_c, dtype=float) + 273.15))


def rho_cipm2007(T_c, p, RH, xCO2=0.0004):
  """CIPM-2007 moist-air density, Picard et al., Metrologia 45 (2008) 149-155, eq. (5a) with Appendix A constants (full text read).
  Recommended validity: 600-1100 hPa and 15-27 degC; outside this range it is an extrapolation (still the best sourced formula)."""
  T_c = np.asarray(T_c, dtype=float); p = np.asarray(p, dtype=float); RH = np.asarray(RH, dtype=float)
  T = T_c + 273.15
  A, B, C, D = 1.2378847e-5, -1.9121316e-2, 33.93711047, -6.3431645e3
  psv = np.exp(A * T**2 + B * T + C + D / T)                       # saturation vapour pressure [Pa]
  f = 1.00062 + 3.14e-8 * p + 5.6e-7 * T_c**2                      # enhancement factor
  xv = RH * f * psv / p
  a0, a1, a2 = 1.58123e-6, -2.9331e-8, 1.1043e-10
  b0, b1 = 5.707e-6, -2.051e-8
  c0, c1 = 1.9898e-4, -2.376e-6
  d, e = 1.83e-11, -0.765e-8
  Z = 1 - (p / T) * (a0 + a1 * T_c + a2 * T_c**2 + (b0 + b1 * T_c) * xv + (c0 + c1 * T_c) * xv**2) + (p / T)**2 * (d + e * xv**2)
  Ma = (28.96546 + 12.011 * (xCO2 - 0.0004)) * 1e-3
  R = 8.314472
  return p * Ma / (Z * R * T) * (1 - xv * (1 - 18.01528e-3 / Ma))


def p_standard_atmosphere(h_m, p0=101325.0, T0=288.15, L=0.0065, g0=9.80665, R=287.05287):
  """Barometric formula of the ISO 2533 standard atmosphere below 11 km (constants as commonly quoted for ISO 2533; NOT re-read from the
  ISO text in this job -> [OPEN] verify)."""
  return p0 * (1 - L * np.asarray(h_m, dtype=float) / T0) ** (g0 / (R * L))


# ---- V5  motor rotor inertia as extra reduced mass  [wheel-side equivalent; VECTO applies it on the MOTOR side, see report Q5]
def theta_red_with_rotor(theta_wheels, J_rotor_total, i_total_row):
  """theta_red per row = wheels + J_rotor * i_total**2 (kg m2).  Use with force_engine_v_rotor."""
  return theta_wheels + J_rotor_total * np.asarray(i_total_row, dtype=float)**2
