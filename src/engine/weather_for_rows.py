# STATUS: NEW (Step 9 item 5 / M0.17, Bob to review). The weather step (pipeline step W).
# PIPELINE ROLE: between the force engine (gives per-row v_avg) and the power step. For each row it
#   produces two weather-dependent arrays:
#     rho_rows   - air density [kg/m^3], computed INLINE from the ideal-gas law rho = P/(R*T)
#     cdxa_rows  - effective air-drag area CdxA_eff [m^2] = CdxA(0)*W1 + W2 (VECTO AirDrag.cs),
#                  looked up from the crosswind W1/W2 tables at the row speed.
#
# PURITY (engine rules 1 + 7): every physics parameter is an ARGUMENT - the pressure P and the gas
#   constant R are passed in, nothing is hard-coded, and there is no file/disk/network I/O here.
# SI inside the engine (rules 5): temperatures in kelvin, P in Pa, R in J/(kg*K), speeds in km/h ONLY
#   at the lookup edge (the crosswind tables are keyed by km/h), everything physical in SI.
# FAIL LOUDLY + NEVER EXTRAPOLATE (rule 6): the CdxA speed lookup is defined over 60-105 km/h (VECTO,
#   LOT3 Table 55 / crosswind verification note). BELOW 60 km/h -> use the 60 value; WITHIN 60-105 ->
#   linear interpolation by speed; ABOVE 105 km/h -> RAISE (never extrapolate).
#
# NOTE on the 60-105 clamp living HERE: Bob's old clamp was 60-100 and sat in the force engine. The
#   close-out (payload-force section 5) moves it to 60-105 AND into this weather step, because the
#   clamp is a property of the CdxA air-drag lookup, not of the mass/accel force coefficients.
import numpy as np

# the CdxA air-drag lookup speed range (VECTO computes 60-105 km/h in 5 km/h steps).
CDXA_SPEED_MIN_KMH = 60.0
CDXA_SPEED_MAX_KMH = 105.0


def _hour_series(departure_time, n_rows, dt_s, by_hour, what):
  # map each per-row second onto the hour-of-day it falls in and pull that hour's value.
  # by_hour is a length-24 sequence (index = hour 0..23). departure_time is the hour-of-day the
  # trip starts (float hours, e.g. 7.5 = 07:30). dt_s is the per-row time step [s].
  by_hour = np.asarray(by_hour, dtype=float)
  if by_hour.shape[0] != 24:
    raise ValueError("weather_for_rows: %s must have 24 hourly values, got %d" % (what, by_hour.shape[0]))
  if np.any(np.isnan(by_hour)):
    raise ValueError("weather_for_rows: %s has a missing (NaN) hourly value" % what)
  # elapsed hours since midnight for each row, wrapped into 0..23
  row_idx = np.arange(n_rows, dtype=float)
  hours = (departure_time + row_idx * dt_s / 3600.0) % 24.0
  hour_of_day = np.floor(hours).astype(int)
  return by_hour[hour_of_day]


def _cdxa_eff_lookup(v_avg_kmh, cdxa_table, wind_kmh):
  # look up CdxA_eff = CdxA(0)*W1 + W2 per row from the crosswind W1/W2 tables.
  # cdxa_table carries:
  #   'cdxa0'       - CdxA(0), the still-air drag area [m^2] (scalar)
  #   'speeds_kmh'  - the vehicle-speed columns the W tables are defined at (ascending, 60..105)
  #   'w1', 'w2'    - the crosswind tables; shape (n_wind, n_speed) or (n_speed,) for a single wind row
  #   'winds_kmh'   - (optional) the wind-speed rows the W tables are defined at; required if w1/w2 2D
  cdxa0 = float(cdxa_table["cdxa0"])
  speeds = np.asarray(cdxa_table["speeds_kmh"], dtype=float)
  w1 = np.asarray(cdxa_table["w1"], dtype=float)
  w2 = np.asarray(cdxa_table["w2"], dtype=float)

  if speeds.ndim != 1 or speeds.shape[0] < 2:
    raise ValueError("weather_for_rows: cdxa_table speeds_kmh must be a 1-D grid with >= 2 points")

  v_avg_kmh = np.asarray(v_avg_kmh, dtype=float)
  wind_kmh = np.asarray(wind_kmh, dtype=float)

  # NEVER EXTRAPOLATE above the top of the lookup grid (rule 6).
  if np.any(v_avg_kmh > CDXA_SPEED_MAX_KMH + 1e-9):
    bad = float(np.max(v_avg_kmh))
    raise ValueError(
      "weather_for_rows: vehicle speed %.3f km/h is above the CdxA lookup range (max %.0f km/h) - "
      "the lookup never extrapolates" % (bad, CDXA_SPEED_MAX_KMH))

  # BELOW 60 km/h -> use the 60 value (clamp up); WITHIN -> interpolate by speed.
  v_clamped = np.clip(v_avg_kmh, CDXA_SPEED_MIN_KMH, CDXA_SPEED_MAX_KMH)

  if w1.ndim == 1:
    # single wind row: W tables are a function of vehicle speed only.
    if w1.shape[0] != speeds.shape[0] or w2.shape[0] != speeds.shape[0]:
      raise ValueError("weather_for_rows: 1-D w1/w2 must match speeds_kmh length")
    w1_row = np.interp(v_clamped, speeds, w1)
    w2_row = np.interp(v_clamped, speeds, w2)
  else:
    # 2-D W tables (wind rows x speed cols): interpolate in both wind and speed per row.
    winds = np.asarray(cdxa_table["winds_kmh"], dtype=float)
    if w1.shape != (winds.shape[0], speeds.shape[0]):
      raise ValueError("weather_for_rows: w1 shape must be (n_winds, n_speeds)")
    # clamp the wind onto the grid too (never extrapolate wind either).
    wind_c = np.clip(wind_kmh, winds.min(), winds.max())
    # interpolate each wind-row at the row speed, then interpolate across wind rows per row.
    # (vectorised: build per-wind-row speed interpolations, then combine with the wind weights.)
    w1_by_wind = np.vstack([np.interp(v_clamped, speeds, w1[j]) for j in range(winds.shape[0])])
    w2_by_wind = np.vstack([np.interp(v_clamped, speeds, w2[j]) for j in range(winds.shape[0])])
    w1_row = np.array([np.interp(wind_c[k], winds, w1_by_wind[:, k]) for k in range(v_clamped.shape[0])])
    w2_row = np.array([np.interp(wind_c[k], winds, w2_by_wind[:, k]) for k in range(v_clamped.shape[0])])

  return cdxa0 * w1_row + w2_row


def weather_for_rows(v_avg, departure_time, temps_by_hour, winds_by_hour, cdxa_table, P, R, dt_s=1.0):
  # per-row weather -> (rho_rows, cdxa_rows).
  #   v_avg          - per-row average speed [m/s] (from the force engine)
  #   departure_time - trip start hour-of-day [h], float (7.5 = 07:30)
  #   temps_by_hour  - 24 hourly air temperatures [K]
  #   winds_by_hour  - 24 hourly wind speeds [m/s]
  #   cdxa_table     - crosswind lookup (see _cdxa_eff_lookup)
  #   P              - air pressure [Pa] (ARGUMENT, not hard-coded)
  #   R              - specific gas constant for air [J/(kg*K)] (ARGUMENT)
  #   dt_s           - per-row time step [s]
  v_avg = np.atleast_1d(np.asarray(v_avg, dtype=float))
  n_rows = v_avg.shape[0]

  if P is None or R is None:
    raise ValueError("weather_for_rows: P (pressure) and R (gas constant) are required arguments")
  if R <= 0:
    raise ValueError("weather_for_rows: gas constant R must be positive, got %r" % (R,))

  # per-row temperature [K] and wind [m/s] by hour of day.
  T_rows = _hour_series(departure_time, n_rows, dt_s, temps_by_hour, "temps_by_hour")
  wind_rows_ms = _hour_series(departure_time, n_rows, dt_s, winds_by_hour, "winds_by_hour")

  if np.any(T_rows <= 0):
    raise ValueError("weather_for_rows: air temperature must be in kelvin and positive")

  # rho = P/(R*T), ideal gas law, computed INLINE per row (P and R are arguments).
  rho_rows = P / (R * T_rows)

  # CdxA lookup wants km/h; convert speeds only at this lookup edge.
  v_avg_kmh = v_avg * 3.6
  wind_rows_kmh = wind_rows_ms * 3.6
  cdxa_rows = _cdxa_eff_lookup(v_avg_kmh, cdxa_table, wind_rows_kmh)

  return rho_rows, cdxa_rows
