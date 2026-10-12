# STATUS: DONE and tested (step I). Pasted by Bob 12 Oct 2026.
# Checked against VECTO Vehicle.cs and CrosswindCorrectionCdxALookup.cs (8 Oct close-out section 4).
# Returns mass-, temperature- and CdxA-independent per-row coefficients. The power step (J, not yet written) is:
#   P_wheel = m*k_lin + m**beta * k_roll + k_rot + rho * CdxA_eff * L
# Neutral defaults (beta = 1, theta_red = 0) reproduce the simple equation.
# Tests passed: v=20, a=0, flat, Crr 0.0055 -> (0, 1.0791, 0, 4000, 20); v=10, a=1 -> (10.5, 0.56653, 0, 580.125, 10.5).
import numpy as np

##4 FORCE ENGINE
## takes in rows from the driver model and calculates the force coeff per row independent of mass and temp and CdxA_eff
def force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red):

  speed = np.asarray(speed, dtype=float) # speed at start of the step
  accel = np.asarray(accel, dtype=float) # acceleration of the vehicle
  dt_s = np.asarray(dt_s, dtype=float)  # time step, s
  grade = np.asarray(grade, dtype=float) # gradient

  grade = np.arctan(grade / 100) # turns gradient in % into an angle in radians
  v1 = speed
  #v2 = speed + accel * dt_s
  v2 = np.maximum(speed + accel * dt_s, 0.0) # speed cannot go below 0, as in the driver model
  v_avg = (v1 + v2)/2  #speed in m/s

  #K = ((Crr * g * np.cos(grade)) + (g * np.sin(grade)) + accel) * v_avg
  # the K equation is the same with the added term of rotational force, if theta red and rdyn are 0 we get back the simple equation.
  k_lin = (g * np.sin(grade) + accel) * v_avg
  k_roll = Crr * g * np.cos(grade) * v_avg
  k_rot = (theta_red / r_dyn**2) * accel * v_avg if theta_red > 0 else np.zeros_like(v_avg) # no rotating mass unless given
  L = (v1 + v2) * (v1**2 + v2**2) / 8 # exact average of 0.5*v^3 over the step as VECTO CrosswindCorrectionCdxALookup

  return k_lin, k_roll, k_rot, L, v_avg # we are taking out v_avg so we can use it to look up CdxA
