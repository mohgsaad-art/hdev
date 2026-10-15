"""Cycle energy estimate WITHOUT a driver model (Method M2).

We do NOT use driver_model.py (open audit bugs). Instead we take the VECTO .vdri
target-speed/grade/distance trace at face value and build a transparent energy
balance per segment using Bob's force_engine:

  P_wheel = m*k_lin + m^beta*k_roll + k_rot + rho*CdxA_eff*L     (force_engine header)

For each segment between cycle points i and i+1:
  - v1 = target speed at i, v2 = target speed at i+1  (m/s)
  - idealised constant acceleration over the segment distance ds:
        a = (v2**2 - v1**2) / (2*ds)            (ds > 0 driving segments)
    => dt = ds / v_avg,  v_avg = (v1+v2)/2
  - call force_engine(g, Crr, v1, a, dt, grade, r_dyn, theta_red=0)
  - traction energy for the segment  E = P_wheel * dt   (only the POSITIVE part;
    negative P_wheel means the wheels are being driven by the vehicle -> braking)
  - split: E_drive = sum of positive P*dt ; E_brake = sum of negative P*dt (regen
    candidate).  "no driver model; acceleration idealised" (per prompt M2).

Stops: a row with stop_s>0 adds dwell time only (no traction energy). We ignore
PTO and aux here (handled separately in the aux/PTO item).

beta = 1, theta_red = 0 (force_engine neutral defaults -> simple road-load eqn;
VECTO's per-axle load-dependent RRC with exponent 0.9 is NOT applied -- stated).

Battery side (Method M3): E_batt_drive = E_drive / ETA_CHAIN ;
recovered at battery = E_brake_recovered * ETA_CHAIN, where E_brake_recovered is
the braking energy times a regen capture fraction (default: all of it, capped so
net never goes negative -- see regen_fraction).
"""
import numpy as np

from vecto_data import (G, RHO_VECTO, ETA_CHAIN, crosswind_engine, force_engine,
                        CROSSWIND_COEFFS, DH, DPHI_DEG, WIND_EXP)


def cdxa_eff_curve(cdxa0, coeff_set, veh_h, v_ref_mps, h_ref, v_veh_kmh_grid,
                   clamp):
    """Return CdxA_eff for each vehicle speed on v_veh_kmh_grid, at one wind speed.
    VECTO behaviour: computed 60-105 km/h; below 60 use the 60 value."""
    a1, a2, a3 = CROSSWIND_COEFFS[coeff_set]
    grid = np.clip(v_veh_kmh_grid, 60.0, 105.0)  # VECTO: <60 uses 60, no extrapolate >105
    if np.isscalar(v_ref_mps) and v_ref_mps == 0.0:
        return np.full_like(grid, cdxa0, dtype=float)
    W1, W2 = crosswind_engine(veh_h, np.atleast_1d(v_ref_mps), h_ref,
                              a1, a2, a3, WIND_EXP, DH, DPHI_DEG, grid, clamp)
    return cdxa0 * W1[0] + W2[0]


def cycle_energy(cycle, mass_kg, cdxa_m2, crr, r_dyn,
                 rho=RHO_VECTO, cdxa_wind=None, v_ref_mps=0.0, coeff_set=None,
                 veh_h=4.0, wind_h_ref=10.0, beta_clamp=10.0,
                 regen_fraction=1.0, mass_eff_factor=1.0):
    """Energy over a distance-based cycle. Returns a dict of kWh and diagnostics.

    mass_kg       : total vehicle mass (curb+body+payload) [kg]
    cdxa_m2       : still-air drag area [m^2]
    crr           : single rolling resistance coefficient [-]
    r_dyn         : dynamic tyre radius [m] (only used if theta_red>0; here 0)
    rho           : air density [kg/m^3]
    cdxa_wind     : if True, apply crosswind CdxA_eff using v_ref_mps/coeff_set
    regen_fraction: fraction of braking (negative wheel) energy captured at wheel
    mass_eff_factor: multiplier on mass for kinetic term (rotating inertia proxy;
                     1.0 = translational only, matches theta_red=0)
    """
    s = cycle["s"]
    v = cycle["v_kmh"] / 3.6          # m/s
    grad = cycle["grad_pct"]

    ds = np.diff(s)                   # segment distances [m]
    v1 = v[:-1]
    v2 = v[1:]
    grade_seg = grad[:-1]            # grade at start of segment (VECTO reads grad directly)

    drive = ds > 0                    # driving segments (skip duplicated stop points ds=0)
    ds_d = ds[drive]
    v1_d = v1[drive]
    v2_d = v2[drive]
    gr_d = grade_seg[drive]
    v_avg = (v1_d + v2_d) / 2.0
    # avoid divide-by-zero where both speeds are 0 over a positive distance
    safe = v_avg > 1e-6
    a = np.zeros_like(ds_d)
    a[safe] = (v2_d[safe] ** 2 - v1_d[safe] ** 2) / (2.0 * ds_d[safe])
    dt = np.zeros_like(ds_d)
    dt[safe] = ds_d[safe] / v_avg[safe]

    # force_engine per segment (vectorised). theta_red=0 -> k_rot=0.
    k_lin, k_roll, k_rot, L, vavg_out = force_engine(
        G, crr, v1_d, a, dt, gr_d, r_dyn, theta_red=0.0)

    # CdxA per segment
    if cdxa_wind:
        # build on a speed grid then map each segment's v_avg (km/h) onto it
        grid_kmh = np.arange(0.0, 106.0, 1.0)
        cd_grid = cdxa_eff_curve(cdxa_m2, coeff_set, veh_h, v_ref_mps,
                                 wind_h_ref, grid_kmh, beta_clamp)
        cdxa_seg = np.interp(np.clip(vavg_out * 3.6, 0, 105), grid_kmh, cd_grid)
    else:
        cdxa_seg = np.full_like(vavg_out, cdxa_m2)

    m = mass_kg
    # P_wheel per segment (W).  k_lin already contains accel term; multiply mass.
    P = (m * k_lin) + (m * k_roll) + k_rot + (rho * cdxa_seg * L)
    # kinetic-energy correction for the rotating-inertia proxy is folded into the
    # accel term via mass; mass_eff_factor adjusts ONLY the accel contribution.
    if mass_eff_factor != 1.0:
        # accel part of k_lin is 'a*v_avg'; grade part is 'g*sin*v_avg'
        grade_rad = np.arctan(gr_d / 100.0)
        accel_power = m * a * vavg_out
        P = P + (mass_eff_factor - 1.0) * accel_power

    E = P * dt                        # J per segment (signed)
    E_drive = E[E > 0].sum()          # J wheel traction (positive)
    E_brake = -E[E < 0].sum()         # J wheel braking (positive magnitude)

    # wheel-level net (what the road demands, before any regen accounting):
    E_wheel_net_norecover = E_drive                     # a model with NO regen
    E_wheel_net_recover = E_drive - regen_fraction * E_brake

    # battery-level (Method M3): drive divided by chain, regen multiplied by chain
    E_batt_drive = E_drive / ETA_CHAIN
    E_batt_recover = regen_fraction * E_brake * ETA_CHAIN
    E_batt_net = E_batt_drive - E_batt_recover

    J2KWH = 1.0 / 3.6e6
    dist_km = ds_d.sum() / 1000.0
    return {
        "dist_km": dist_km,
        "E_drive_wheel_kWh": E_drive * J2KWH,
        "E_brake_wheel_kWh": E_brake * J2KWH,
        "E_wheel_net_norecover_kWh": E_wheel_net_norecover * J2KWH,
        "E_wheel_net_recover_kWh": E_wheel_net_recover * J2KWH,
        "E_batt_drive_kWh": E_batt_drive * J2KWH,
        "E_batt_recover_kWh": E_batt_recover * J2KWH,
        "E_batt_net_kWh": E_batt_net * J2KWH,
        "regen_fraction": regen_fraction,
    }


def steady_state_power_kW(mass_kg, cdxa_m2, crr, v_kmh, rho=RHO_VECTO,
                          grade_pct=0.0):
    """Method M1: constant speed, flat (or fixed grade), accel=0.
    Returns wheel power [kW] and the breakdown."""
    v = v_kmh / 3.6
    grade_rad = np.arctan(grade_pct / 100.0)
    f_roll = crr * mass_kg * G * np.cos(grade_rad)
    f_grade = mass_kg * G * np.sin(grade_rad)
    f_air = 0.5 * rho * cdxa_m2 * v ** 2
    f_total = f_roll + f_grade + f_air
    P = f_total * v
    return {
        "P_wheel_kW": P / 1000.0,
        "P_roll_kW": f_roll * v / 1000.0,
        "P_grade_kW": f_grade * v / 1000.0,
        "P_air_kW": f_air * v / 1000.0,
        "wh_per_km_wheel": P / v * (1.0 / 3600.0) * 1000.0 / 1000.0,  # Wh/km
    }
