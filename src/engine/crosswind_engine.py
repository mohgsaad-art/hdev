# STATUS: DONE and verified (step F). Pasted by Bob 12 Oct 2026.
# Verified: max 0.006% difference vs VECTO Cdv_Generator Excel (docs/decisions/crosswind-verification-2026-10-06.md).
# Output: W1, W2 tables (rows = wind speeds v_ref, columns = vehicle speeds). CdxA_eff = CdxA(0)*W1 + W2 (VECTO AirDrag.cs).
# beta_limit_deg = 10 is an HDEV decision (NOT VECTO). None = VECTO behaviour. Must be stated in every client report.
import numpy as np

###PRE-COMPUTE
##1 Crosswind fucntion(also temperature?)
# pure physics calculates only W1, W2, CdxAeff comes in when we get historical data or something
# outputs W1, W2 lookup table for a given height based on vehicle speeds and wind speeds

def crosswind_engine(vehicle_height, v_ref, h_ref, a1, a2,a3, wind_exp, dh, dphi_deg, v_veh_kmh, beta_limit_deg):

  #check if wind speeds and vehicle speeds are a list or not
  v_ref = np.atleast_1d(np.asarray(v_ref, dtype=float))
  v_veh_kmh = np.atleast_1d(np.asarray(v_veh_kmh, dtype=float))
  v_veh = v_veh_kmh / 3.6 # convert from km/h to m/s

  n_slices = round(vehicle_height / dh) # number of equal heights based on dh
  slice_heights = (np.arange(n_slices) + 0.5) * dh # slide heights but the midpoint of each slice, avoids 0 wind at 0m issue.
  phi = np.radians(np.arange(0, 360, dphi_deg)) # converts 0 to 360 deg to radians

  #the None in brackets only maintain the shape i.e. give each list a dimension to run along so there is not collisions, easy for numpy this way
  v_wind = v_ref[:, None, None, None] * (slice_heights[None, None, None, :] / h_ref) ** wind_exp #Calculates the wind speed at each height slice, wind_exp is how wind grows with height
  v_air_x = v_veh[None, :, None, None] + v_wind * np.cos(phi)[None, None, :, None] # wind hitting the vehicle on the x axis
  v_air_y = v_wind * np.sin(phi)[None, None, :, None] # wind component hitting the vehicle on the y axis
  v_air_sq = v_air_x**2 + v_air_y**2 #total air speed squared

  beta_deg = np.abs(np.degrees(np.arctan2(v_air_y, v_air_x))) #yaw angle the angle between vehicle direction and wind direction, abs since vehicle is symmetric
  if beta_limit_deg is not None: # sets the 10deg clamp so it stays VECTO auditable,above 10 it breaks the curve following
      beta_deg = np.minimum(beta_deg, beta_limit_deg)
  delta_CdxA = a1 * beta_deg + a2 * beta_deg**2 + a3 * beta_deg**3 # extra drag m2 caused by that yaw angle

  W1 = v_air_sq.mean(axis=(2, 3)) / v_veh**2 #how much more air is hitting than with no wind
  W2 = (delta_CdxA * v_air_sq).mean(axis=(2, 3)) / v_veh**2 #how much extra drag the yawed airflow adds in m2
  return W1, W2
