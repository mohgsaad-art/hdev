# STATUS: NEW (Step 9 item 6 / M0.19, Bob to review). The power step (pipeline step J).
# NAME: this file is power_step.py, NOT force_engine.py. The split is deliberate (design §2): the
#   force engine produces the mass-/temperature-/CdxA-independent per-row COEFFICIENTS; the power step
#   multiplies them by the actual mass, rolling-mass exponent and air term to get wheel power. Keeping
#   them in two files avoids the documented name collision (two different "force"/"power" steps).
#
# FORMULA (exactly the header comment of force_engine.py and close-out payload-force section 4):
#   P_wheel = m*k_lin + m**beta * k_roll + k_rot + rho_rows * cdxa_rows * L
# where k_lin, k_roll, k_rot, L are the per-row coefficients from force_engine, rho_rows and cdxa_rows
# are the per-row air density and effective drag area from weather_for_rows, m is the vehicle mass [kg].
#
# NEUTRAL DEFAULTS reduce to the simple K equation (force_engine header): beta = 1 (and the force
#   engine's theta_red = 0, which already zeros k_rot) give P_wheel = m*(k_lin + k_roll) + rho*CdxA*L,
#   i.e. the simple multiply-add with no rolling-mass exponent and no rotating inertia.
#
# PURITY (engine rules 1 + 7): everything is an ARGUMENT (mass, beta, the coefficients, the air arrays),
#   nothing physical is hard-coded, and there is no I/O. Vectorised over rows like force_engine.py.
import numpy as np

##J POWER STEP
## multiplies the per-row force coefficients by mass/beta and adds the air term -> wheel power per row.
def power_step(m, beta, k_lin, k_roll, k_rot, rho_rows, cdxa_rows, L):

  k_lin = np.asarray(k_lin, dtype=float)      # linear (slope + accel) coefficient, x mass
  k_roll = np.asarray(k_roll, dtype=float)    # rolling coefficient, x mass**beta
  k_rot = np.asarray(k_rot, dtype=float)      # rotational-inertia coefficient, not x mass
  rho_rows = np.asarray(rho_rows, dtype=float)  # air density per row [kg/m^3]
  cdxa_rows = np.asarray(cdxa_rows, dtype=float)  # effective drag area per row [m^2]
  L = np.asarray(L, dtype=float)              # air-power shape term (v1+v2)(v1^2+v2^2)/8

  if m is None or beta is None:
    raise ValueError("power_step: mass m and exponent beta are required arguments")
  if m < 0:
    raise ValueError("power_step: mass m must be non-negative, got %r" % (m,))

  # P_wheel = m*k_lin + m**beta * k_roll + k_rot + rho * CdxA_eff * L
  P_wheel = m * k_lin + m ** beta * k_roll + k_rot + rho_rows * cdxa_rows * L
  return P_wheel
