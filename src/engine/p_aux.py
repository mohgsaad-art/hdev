# STATUS: WRITTEN (Step 9 item 7 / M0.15, Bob to review). Pipeline step: auxiliary electric power.
# VECTO BEV lorry auxiliary logic fully traced in docs/decisions/2026-10-08_session-closeout-paux.md:
#   P_aux(t) = P_ES + P_HVAC + P_PS + P_SP * [vehicle moving] + P_cond * [electric motor on]
# All five terms are electric power drawn from the traction battery; DC/DC efficiency = 1.0 in
# Declaration Mode (no converter loss), and there is no engine cooling fan for a BEV.
#
# DECIDED PARTS ONLY (close-out sections 0 and 5): this implements the five-term sum. The five
#   constants are ARGUMENTS (engine rule 1) - the resolver looks them up from defaults.py at the
#   boundary and passes them in; nothing is hard-coded here, and the function is vehicle-agnostic.
#   moving and motor_on are per-row boolean arrays (close-out suggested structure in section 10).
#
# BLANK / '---' CELLS: VECTO raises a lookup error on a blank or '---' table cell (close-out section 6).
#   In HDEV those cells are value=None in defaults.py; p_aux FAILS LOUDLY if any of the five constants
#   is None, so a missing cell can never silently become 0 W.
#
# NO AUX DURING DEPOT CHARGING (close-out section 7, open item): there is no "charging" branch here -
#   the charging engine simply does NOT call p_aux while the truck is parked on a depot charger. This
#   is a caller contract, not a flag inside the function.
#
# 🔒 WEATHER LAYER ON AUX - STUBBED: cabin heating / a W-per-degC temperature dependence on the
#   auxiliaries is NOT decided (close-out sections 7, 9.3, 10 - needs an authentic non-VECTO W/degC
#   source from Bob). The aux_weather_fn hook below lets a future caller request weather-dependent aux;
#   until the source exists it raises NotImplementedError('blocked by p_aux weather layer ...').
import numpy as np


def p_aux(P_ES, P_HVAC, P_PS, P_SP, P_Cond, moving, motor_on, aux_weather_fn=None):
  # per-row auxiliary electric power [W] for a BEV lorry.
  #   P_ES, P_HVAC, P_PS - always-on electric aux [W] (electric system, HVAC, pneumatic system)
  #   P_SP               - steering-pump electric power [W], applied only while the vehicle is moving
  #   P_Cond             - conditioning electric power [W], applied only while the electric motor is on
  #   moving             - per-row bool: True when the vehicle is moving (speed > 0)
  #   motor_on           - per-row bool: True when the electric motor is on
  #   aux_weather_fn     - 🔒 reserved hook for a weather-dependent aux layer; must stay None for now
  if aux_weather_fn is not None:
    # weather-on-aux (cabin heating, W/degC) is not decided - do not silently guess a number.
    raise NotImplementedError(
      "blocked by p_aux weather layer - needs Bob W/degC source")

  # the five constants come from the defaults boundary; a blank/'---' VECTO cell is None there.
  for name, val in (("P_ES", P_ES), ("P_HVAC", P_HVAC), ("P_PS", P_PS),
                    ("P_SP", P_SP), ("P_Cond", P_Cond)):
    if val is None:
      raise ValueError(
        "p_aux: %s is None (blank/'---' table cell) - VECTO raises on a missing aux cell" % name)

  moving = np.asarray(moving, dtype=bool).astype(float)      # [moving] indicator, 0/1 per row
  motor_on = np.asarray(motor_on, dtype=bool).astype(float)  # [motor on] indicator, 0/1 per row

  # P_aux = P_ES + P_HVAC + P_PS + P_SP*[moving] + P_cond*[motor on]
  P_aux_rows = P_ES + P_HVAC + P_PS + P_SP * moving + P_Cond * motor_on
  return P_aux_rows
