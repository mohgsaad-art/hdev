"""TEST-ONLY copy of the HDEV code-of-record functions
(docs/research/inputs/HDEV_NEW_code_of_record_2026-11-07.ipynb, Bob, 7 Nov 2026).

This module exists so the EEA truck validation (section 5) can import the
code-of-record engines without editing the notebook or src/. The functions are
copied verbatim from the notebook cells, EXCEPT for the four fixes listed below
(Claude's known-issues list, 7 Nov). Nothing else is changed.

FIXES APPLIED IN THIS TEST COPY (and nowhere else):
  FIX 1  driver_model accelerate branch: the notebook joins
           `v_cap = math.sqrt(...)` and `a = max(min(a, (v_cap - v)/dt), 0.0)`
         on one physical line -> SyntaxError. Split onto two lines. (no logic change)
  FIX 2  drag-table change (agreed 3 Nov, session-closeout-2026-11-03-driver-model-review):
         `coast_distance` already takes (drag_v, drag_F), but `driver_model` still
         declared `P_drag_loss` and passed it in, and `coast_acc` still used
         `P_drag_loss / v`. In this copy: driver_model takes `drag_v=None, drag_F=None`
         instead of `P_drag_loss`, passes them to coast_distance, and coast_acc uses
         `interp1(v, drag_v, drag_F)` for the drivetrain drag force.
  FIX 3  g default is 9.81 in the notebook; the agreed value is 9.80665. We do NOT edit
         the defaults; every call in the test harness passes g=9.80665 explicitly.
  FIX 4  the pto_engine test cell uses an old signature; PTO is not used here, so that
         cell is ignored. pto_engine itself is copied unchanged.

Every other line is the notebook's. Comments are kept.
"""
import bisect
import math

import numpy as np


# ===== CELL 2: crosswind_engine (verbatim) =====
def crosswind_engine(vehicle_height, v_ref, h_ref, a1, a2, a3, wind_exp, dh, dphi_deg, v_veh_kmh, beta_limit_deg):
    v_ref = np.atleast_1d(np.asarray(v_ref, dtype=float))
    v_veh_kmh = np.atleast_1d(np.asarray(v_veh_kmh, dtype=float))
    v_veh = v_veh_kmh / 3.6  # convert from km/h to m/s

    n_slices = round(vehicle_height / dh)
    slice_heights = (np.arange(n_slices) + 0.5) * dh
    phi = np.radians(np.arange(0, 360, dphi_deg))

    v_wind = v_ref[:, None, None, None] * (slice_heights[None, None, None, :] / h_ref) ** wind_exp
    v_air_x = v_veh[None, :, None, None] + v_wind * np.cos(phi)[None, None, :, None]
    v_air_y = v_wind * np.sin(phi)[None, None, :, None]
    v_air_sq = v_air_x ** 2 + v_air_y ** 2

    beta_deg = np.abs(np.degrees(np.arctan2(v_air_y, v_air_x)))
    if beta_limit_deg is not None:
        beta_deg = np.minimum(beta_deg, beta_limit_deg)
    delta_CdxA = a1 * beta_deg + a2 * beta_deg ** 2 + a3 * beta_deg ** 3

    W1 = v_air_sq.mean(axis=(2, 3)) / v_veh ** 2
    W2 = (delta_CdxA * v_air_sq).mean(axis=(2, 3)) / v_veh ** 2
    return W1, W2


# ===== CELL 4: payload_engine (verbatim) =====
def payload_engine(stop, shape, payload_start, payload_end=None, payload_custom=None):
    stop = np.asarray(stop, dtype=float)
    is_stop = stop > 0
    is_stop[0] = False
    n_stops = int(is_stop.sum())

    if shape == "constant":
        values = np.full(n_stops + 1, float(payload_start))
    elif shape == "linear":
        if n_stops == 0:
            raise ValueError("linear needs at least one stop")
        values = np.linspace(payload_start, payload_end, n_stops + 1)
    elif shape == "custom":
        values = np.asarray(payload_custom, dtype=float)
        if len(values) != n_stops + 1:
            raise ValueError(f"custom needs {n_stops + 1} values, got {len(values)}")
    else:
        raise ValueError(f"unknown shape: {shape}")

    if np.any(values < 0):
        raise ValueError("payload cannot be negative")

    payload = np.full(len(stop), np.nan)
    payload[0] = values[0]
    payload[is_stop] = values[1:]
    return payload


# ===== CELL 7: interp1 (verbatim) =====
def interp1(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    i = bisect.bisect_right(xs, x)
    return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])


# ===== CELL 8: decel_distance (verbatim) =====
def decel_distance(v_from, v_to, vacc_v, vacc_dec):
    if v_to >= v_from:
        return 0.0
    dist = 0.0
    for i in range(1, len(vacc_v)):
        v_lo, v_hi = vacc_v[i - 1], vacc_v[i]
        a_lo, a_hi = vacc_dec[i - 1], vacc_dec[i]
        v1 = min(v_from, v_hi)
        v2 = max(v_to, v_lo)
        if v2 >= v1:
            continue
        if math.isclose(a_lo, a_hi):
            dist += (v1 ** 2 - v2 ** 2) / (2 * -a_lo)
        else:
            k = (a_lo - a_hi) / (v_lo - v_hi)
            d = a_lo - k * v_lo
            t = math.log((v2 * k + d) / (v1 * k + d)) / k
            m = v1 + d / k
            dist += m / k * math.exp(k * t) - d / k * t - m / k
    return dist


# ===== CELL 9: coast_distance (verbatim; already uses drag_v, drag_F) =====
def coast_distance(v, v_target, h_now, h_target, s_now, s_target,
                   coast_mass, m_red_wheels, cdxa_v, cdxa, Crr, rho, g, drag_v, drag_F,
                   df_offset, df_scaling, df_vtarget, df_vdrop):
    m_eff = coast_mass + m_red_wheels
    dE = m_eff * g * (h_now - h_target) + m_eff * (v ** 2 - v_target ** 2) / 2
    v_avg = (v + v_target) / 2
    cda = interp1(v_avg, cdxa_v, cdxa)
    F_air = rho / 8 * cda * (v + v_target) * (v ** 2 + v_target ** 2) / v_avg
    grad = (h_target - h_now) / (s_target - s_now)
    F_roll = math.cos(grad) * coast_mass * g * Crr
    F_loss = interp1(v, drag_v, drag_F)
    f_vt = interp1(v_target * 3.6, df_vtarget[0], df_vtarget[1])
    f_vd = interp1((v - v_target) * 3.6, df_vdrop[0], df_vdrop[1])
    DF = df_offset - df_scaling * f_vt * f_vd
    return dE / (DF * (F_air + F_roll + F_loss))


# ===== CELL 10: force_engine (verbatim) =====
def force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red):
    speed = np.asarray(speed, dtype=float)
    accel = np.asarray(accel, dtype=float)
    dt_s = np.asarray(dt_s, dtype=float)
    grade = np.asarray(grade, dtype=float)

    grade = np.arctan(grade / 100)
    v1 = speed
    v2 = np.maximum(speed + accel * dt_s, 0.0)
    v_avg = (v1 + v2) / 2

    k_lin = (g * np.sin(grade) + accel) * v_avg
    k_roll = Crr * g * np.cos(grade) * v_avg
    k_rot = (theta_red / r_dyn ** 2) * accel * v_avg if theta_red > 0 else np.zeros_like(v_avg)
    L = (v1 + v2) * (v1 ** 2 + v2 ** 2) / 8

    return k_lin, k_roll, k_rot, L, v_avg


# ===== CELL 6: driver_model (verbatim EXCEPT FIX 1 + FIX 2) =====
def driver_model(wp_s, wp_v, wp_stop, wp_grade,
                 vacc_v, vacc_acc, vacc_dec, dt=1.0,
                 coast_mass=None, m_red_wheels=0.0, cdxa_v=None, cdxa=None, Crr=None, rho=1.188, g=9.81,
                 drag_v=None, drag_F=None, P_max=None,          # FIX 2: drag_v, drag_F replace P_drag_loss
                 lac_min_v=50.0, lac_dist_factor=10.0, df_offset=2.5, df_scaling=1.5,
                 df_vtarget=((0, 48, 52, 100), (0, 0, 1, 1)), df_vdrop=((-100, 9, 11, 100), (1, 1, 0, 0)),
                 os_min_v=50.0, os_allowed=2.5, brake_margin=0.1, v_min_coast=5.0):

    # ---------- A. once, before the loop ----------
    s_wp = [float(x) for x in wp_s]
    v_wp = [float(x) / 3.6 for x in wp_v]
    stop_wp = [float(x) for x in wp_stop]
    gr_wp = np.asarray(wp_grade, dtype=float)
    n = len(s_wp)

    rise = np.diff(np.asarray(s_wp)) * gr_wp[:-1] / 100
    alt_wp = np.concatenate(([0.0], np.cumsum(rise)))
    alt_l = alt_wp.tolist()
    gr_l = gr_wp.tolist()

    if v_wp[0] == 0 and stop_wp[0] == 0:
        stop_wp[0] = 1.0

    seg_v = [0.0] * n
    nxt = 0.0
    for i in range(n - 1, -1, -1):
        seg_v[i] = v_wp[i] if v_wp[i] > 0 else nxt
        if v_wp[i] > 0:
            nxt = v_wp[i]
    chg = [i for i in range(1, n) if v_wp[i] != seg_v[i - 1]]
    chg_s = [s_wp[i] for i in chg]

    vv = [x / 3.6 for x in vacc_v]
    va = [float(x) for x in vacc_acc]
    vd = [float(x) for x in vacc_dec]

    coast_on = coast_mass is not None
    if coast_on:
        if cdxa_v is None or cdxa is None or Crr is None:
            raise ValueError("coasting needs cdxa_v, cdxa and Crr")
        m_eff = coast_mass + m_red_wheels
        cv = [x / 3.6 for x in cdxa_v]
        cc = [float(x) for x in cdxa]

    lac_min = lac_min_v / 3.6
    os_min = os_min_v / 3.6
    os_add = os_allowed / 3.6
    v_min_c = v_min_coast / 3.6

    def coast_acc(v, k):                                 # acceleration with no motor torque at speed v on segment k [m/s^2]
        th = math.atan(gr_l[k] / 100)
        F = (rho / 2 * interp1(v, cv, cc) * v * v
             + coast_mass * g * Crr * math.cos(th)
             + coast_mass * g * math.sin(th)
             + (interp1(v, drag_v, drag_F) if (drag_v is not None and v > 0) else 0.0))  # FIX 2: drag force from table
        return -F / m_eff

    T, S, V, A, M = [], [], [], [], []
    t = 0.0
    s = s_wp[0]
    v = v_wp[0]
    s_end = s_wp[-1]

    def add_stop(i, t):
        for _ in range(int(round(stop_wp[i] / dt))):
            T.append(t); S.append(s_wp[i]); V.append(0.0); A.append(0.0); M.append(0)
            t += dt
        return t

    if v_wp[0] == 0:
        t = add_stop(0, t)
        v = 0.0

    trig = None
    max_steps = int(sum(stop_wp) / dt + (s_end - s_wp[0]) / 0.5 + 10000)

    # ---------- B. each 1 s step ----------
    for _ in range(max_steps):
        if s >= s_end - 1e-6:
            break
        k = bisect.bisect_right(s_wp, s) - 1
        target = seg_v[k]
        v_os = target + os_add if target > os_min else target

        if trig is not None and s >= trig[1] - 1e-6:
            trig = None

        look = max(2 * v * dt, v * 3.6 * lac_dist_factor, 1.2 * decel_distance(v, 0.0, vv, vd) + v * dt)
        j0 = bisect.bisect_right(chg_s, s)
        j1 = bisect.bisect_right(chg_s, s + look)
        best_b = None
        best_c = None
        for j in range(j0, j1):
            i = chg[j]
            vt = v_wp[i] + os_add if v_wp[i] > os_min else v_wp[i]
            if vt >= v:
                continue
            b_start = s_wp[i] - (decel_distance(v, vt, vv, vd) + brake_margin)
            c_start = b_start
            if coast_on and v > lac_min:
                cd = coast_distance(v, vt, interp1(s, s_wp, alt_l), alt_l[i], s, s_wp[i],
                                    coast_mass, m_red_wheels, cv, cc, Crr, rho, g, drag_v, drag_F,  # FIX 2
                                    df_offset, df_scaling, df_vtarget, df_vdrop)
                if cd > 0:
                    c_start = s_wp[i] - cd
            if best_b is None or b_start < best_b[1]:
                best_b = (i, b_start, c_start, vt)
            if best_c is None or c_start < best_c[2]:
                best_c = (i, b_start, c_start, vt)
        action = None
        if best_b is not None:
            i, b_start, c_start, vt = best_b
            coast_ok = best_c[0] == i and c_start < b_start
            action = (i, s_wp[i], vt, coast_ok, min(b_start, c_start))

        if trig is None and action is not None and s + v * dt >= action[4]:
            trig = [action[0], action[1], action[2], action[3], False]
        elif trig is not None and action is not None and action[1] != trig[1]:
            b_new = action[1] - (decel_distance(v, action[2], vv, vd) + brake_margin)
            b_cur = trig[1] - (decel_distance(v, trig[2], vv, vd) + brake_margin)
            if b_new < b_cur:
                trig = [action[0], action[1], action[2], False, True]

        # ---------- choose acceleration ----------
        acc_max = interp1(v, vv, va)
        dec_max = interp1(v, vv, vd)
        if trig is not None:
            i_t, s_t, v_t, coast_ok, braking = trig
            b_start = s_t - (decel_distance(v, v_t, vv, vd) + brake_margin)
            if 0 < v <= v_t:
                a = max(dec_max, min(acc_max, (v_t - v) / dt)); mode = 2
            elif coast_on and coast_ok and not braking and s + v * dt < b_start and v >= v_min_c:
                ca = coast_acc(v, k)
                a = min(ca, (max(target, v) - v) / dt)
                a = max(a, dec_max)
                mode = 3 if a >= ca - 1e-9 else 4
            elif not braking and s < b_start:
                frac = (s + v * dt - b_start) / (v * dt) if v > 0 else 1.0
                a = dec_max * min(max(frac, 0.0), 1.0); mode = 4
                trig[4] = True
            else:
                rem = s_t - s
                if rem < 2 * v * dt and v > v_t:
                    a = (v_t ** 2 - v ** 2) / (2 * rem) if rem > 1e-6 else dec_max
                else:
                    a = max(dec_max, (v_t - v) / dt)
                mode = 4
                trig[4] = True
        else:
            if v < target - 1e-9:
                a = min(acc_max, (target - v) / dt)
                if P_max is not None and coast_on:
                    F_res = -coast_acc(v, k) * m_eff
                    a = min(a, (P_max / max(v, 1.0) - F_res) / m_eff)
                if action is not None:
                    room = action[1] - s - v * dt - brake_margin
                    v_cap = math.sqrt(max(action[2] ** 2 + 2 * -dec_max * max(room, 0.0), 0.0))  # FIX 1: split line
                    a = max(min(a, (v_cap - v) / dt), 0.0)                                        # FIX 1: split line
                mode = 1
            elif coast_on and target > os_min:
                ca = coast_acc(v, k)
                if ca >= 0:
                    a = max(dec_max, min(ca, (v_os - v) / dt))
                    mode = 3 if a >= ca - 1e-9 else 4
                elif v + ca * dt > target:
                    a = ca; mode = 3
                else:
                    a = (target - v) / dt; mode = 2
            elif v > target + 1e-9:
                a = max(dec_max, (target - v) / dt); mode = 4
            else:
                a = 0.0; mode = 2

        # ---------- move one step ----------
        v_new = v + a * dt
        if v_new < 0:
            ds = v * v / (2 * -a) if a < 0 else 0.0
            v_new = 0.0
        else:
            ds = (v + v_new) / 2 * dt
        if trig is not None and trig[2] == 0 and (v_new <= 0 or s + ds >= trig[1]):
            ds = max(trig[1] - s, 0.0)
            v_new = 0.0
        T.append(t); S.append(s); V.append(v); A.append((v_new - v) / dt); M.append(mode)
        t += dt
        s += ds
        v = v_new

        if trig is not None and trig[2] == 0 and v == 0:
            s = trig[1]
            t = add_stop(trig[0], t)
            trig = None
    else:
        raise RuntimeError("driver_model did not reach the end of the route")

    # ---------- C. after the loop: arrays + grade from altitude ----------
    T = np.asarray(T); S = np.asarray(S); V = np.asarray(V); A = np.asarray(A); M = np.asarray(M, dtype=int)
    s_next = np.append(S[1:], s)
    ds_row = s_next - S
    h1 = np.interp(S, s_wp, alt_wp)
    h2 = np.interp(s_next, s_wp, alt_wp)
    k_row = np.searchsorted(s_wp, S, side="right") - 1
    grade = np.where(ds_row > 1e-9, (h2 - h1) / np.where(ds_row > 1e-9, ds_row, 1.0) * 100, gr_wp[k_row])
    return T, S, V, A, grade, M


# ===== CELL 12: P_aux (verbatim) =====
def P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on,
          ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0):
    powers = [np.asarray(p, dtype=float) for p in (ES_power, PS_power, HVAC_power, SP_power, cond_power)]
    effs = (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff)
    PTO_always_on = np.asarray(PTO_always_on, dtype=float)

    for p in powers:
        if np.any(p < 0):
            raise ValueError("aux power cannot be negative")
    for e in effs:
        if e <= 0:
            raise ValueError("efficiency must be > 0")

    ES_power, PS_power, HVAC_power, SP_power, cond_power = (p * e for p, e in zip(powers, effs))
    PTO_always_on = PTO_always_on / PTO_eff

    return ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on


# ===== CELL 13: SP_power_helper (verbatim) =====
def SP_power_helper(SP_baseline, SP_axle_shares, SP_tech_factors):
    SP_baseline = np.asarray(SP_baseline, dtype=float)
    SP_axle_shares = np.asarray(SP_axle_shares, dtype=float)
    SP_tech_factors = np.asarray(SP_tech_factors, dtype=float)

    if SP_axle_shares.ndim != 2 or SP_axle_shares.shape[1] != 3 or len(SP_axle_shares) == 0:
        raise ValueError("SP_axle_shares needs one (UF, B, S) row per steered axle")
    if SP_tech_factors.shape != SP_axle_shares.shape:
        raise ValueError("need one technology (UF, B, S) per steered axle")

    parts = SP_baseline * SP_axle_shares.sum(axis=0) / 100
    parts = parts * SP_tech_factors.mean(axis=0)
    return float(parts.sum())


# ===== CELL 15: ssm_total_w (HVAC helper, verbatim) =====
def ssm_total_w(T_amb, solar, T_calc, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q):
    T_amb = np.asarray(T_amb, dtype=float)
    solar = np.asarray(solar, dtype=float)
    rho = p / (R * (T_amb + 273.15))
    q_wall = (T_amb - T_calc) * A_surface * U
    q_people = N_persons * np.where(T_amb < T_boundary, heat_per_person[0], heat_per_person[1])
    q_solar = solar * A_window * g * np.where(T_amb < T_boundary, clouding[0], clouding[1]) * solar_factor
    q_freshair = rho * cp * Q / 3600 * (T_amb - T_calc)
    return q_wall + q_people + q_solar + q_freshair


# ===== CELL 16: climate_lookup (HVAC helper, verbatim) =====
def climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points):
    T_amb = np.asarray(T_amb, dtype=float)
    cop_heat = np.interp(T_amb, T_heat_points, cop_heat_points)
    cop_cool = np.interp(T_amb, T_cool_points, cop_cool_points)
    dist = np.abs(T_amb[..., None] - np.asarray(T_heat_points, dtype=float))
    idx = np.argmin(dist, axis=-1)
    hp_share = np.asarray(hp_share_points, dtype=float)[idx]
    eh_share = np.asarray(eh_share_points, dtype=float)[idx]
    fuel_share = np.asarray(fuel_share_points, dtype=float)[idx]
    return cop_heat, cop_cool, hp_share, eh_share, fuel_share


# ===== CELL 14: HVAC_thermal (verbatim) =====
def HVAC_thermal(T_amb, solar, A_surface, U, N_persons, A_window, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points,
                 hp_share_points, eh_share_points, fuel_share_points, max_heating_power, max_cooling_power, cab_volume, vent_rate, vent_rate_heating,
                 eh_eff=0.93, spec_vent_power=0.56, heat_per_person=(50.0, 80.0), clouding=(0.65, 0.8), T_boundary=17.0, g=0.95, solar_factor=0.25,
                 waste_heat=0.0, T_heat=18.0, T_cool=23.0, T_cool_off=17.0, Q=0.0, p=101325.0, R=287.05, cp=1005.0):
    T_amb = np.asarray(T_amb, dtype=float)

    run1 = ssm_total_w(T_amb, solar, T_heat, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)
    run2 = ssm_total_w(T_amb, solar, T_cool, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)

    losing_heat = (run1 < 0) & (run2 < 0)
    heating_demand = np.where(losing_heat, np.abs(np.maximum(run1, run2)) - waste_heat, 0.0)
    heating_demand = np.maximum(heating_demand, 0.0)

    cop_heat, cop_cool, hp_share, eh_share, fuel_share = climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points)

    fuel_heat = heating_demand * fuel_share
    sum_heat = np.minimum(max_heating_power, heating_demand * (hp_share + eh_share))

    rest = np.where(np.isclose(fuel_share, 1.0), 1.0, 1 - fuel_share)
    scale = sum_heat / rest
    hp_heat = scale * hp_share
    eh_heat = scale * eh_share

    if np.any((hp_heat > 0) & np.isnan(cop_heat)):
        raise ValueError("heat pump COP missing for this temperature")
    HP_el = np.where(hp_heat > 0, hp_heat / cop_heat, 0.0)
    EH_el = eh_heat / eh_eff

    gaining_heat = (run1 > 0) & (run2 > 0) & (T_amb >= T_cool_off)
    cooling_demand = np.where(gaining_heat, np.minimum(run1, run2), 0.0)
    cooling_demand = np.minimum(cooling_demand, max_cooling_power)
    if np.any((cooling_demand > 0) & np.isnan(cop_cool)):
        raise ValueError("cooling COP missing for this temperature")
    AC_el = np.where(cooling_demand > 0, cooling_demand / cop_cool, 0.0)

    ventillation_status = ((T_amb < T_cool_off) & (run1 > 0) & (run2 > 0)) | ((run1 > 0) & (run2 < 0))
    fan_rate = np.where(losing_heat, vent_rate_heating, np.where(gaining_heat | ventillation_status, vent_rate, 0.0))
    fan_el = cab_volume * fan_rate * spec_vent_power

    HVAC_el = HP_el + EH_el + AC_el + fan_el
    return HVAC_el, fuel_heat


# ===== CELL 17: pto_engine (verbatim; FIX 4 = ignore the old-signature test cell 18) =====
def pto_engine(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff):
    stop = np.asarray(stop, dtype=float)
    is_on = np.array(is_on, dtype=float)
    stop_pto_t = np.asarray(stop_pto_t, dtype=float)
    stop_pto_w = np.asarray(stop_pto_w, dtype=float)
    drive_pto_w = np.asarray(drive_pto_w, dtype=float)
    drive_pto_t = np.asarray(drive_pto_t, dtype=float)

    is_on[0] = 0
    stop_steps = np.diff(stop_pto_t).astype(int)
    stop_1s = np.repeat(stop_pto_w[:-1], stop_steps)
    drive_steps = np.diff(drive_pto_t).astype(int)
    drive_1s = np.repeat(drive_pto_w[:-1], drive_steps)
    pto_dur = len(stop_1s)

    is_stop = stop > 0
    stop_on = is_stop & (is_on > 0) & (pto_dur > 0)

    pto_start = np.full(len(stop), np.nan)
    pto_start[stop_on] = np.floor((stop[stop_on] - pto_dur) / 2)

    too_short = np.where(pto_start < 0)[0]
    if len(too_short) > 0:
        raise ValueError(f"PTO ({pto_dur} s) is longer than the stop at waypoint(s) {too_short.tolist()}; the parser must extend these stops")

    stop_1s = stop_1s / stop_pto_eff
    drive_1s = drive_1s / drive_pto_eff
    return is_on, pto_start, stop_1s, drive_1s


# ===== CELL 20: consumption_engine (verbatim) =====
def consumption_engine(T, S, V, M, dt,
                       k_lin, k_roll, k_rot, L, v_avg,
                       m_vehicle, wp_s, payload_wp, beta,
                       t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,
                       ES, PS, HVAC, SP, cond, PTO_always_on,
                       pto_1s, pto_on_col, pto_start_col,
                       motor_eff, inverter_eff, gearbox_eff, regen_effeiciency, v_no_regen, P_regen_max=None):

    T, S, V, M = (np.asarray(x) for x in (T, S, V, M))
    wp_s, payload_wp = np.asarray(wp_s, dtype=float), np.asarray(payload_wp, dtype=float)
    T_amb_h, cdxa_v = np.asarray(T_amb_h, dtype=float), np.asarray(cdxa_v, dtype=float)
    pto_1s, pto_on_col, pto_start_col = (np.asarray(x, dtype=float) for x in (pto_1s, pto_on_col, pto_start_col))

    has_pl = ~np.isnan(payload_wp)
    k_pl = np.searchsorted(wp_s[has_pl], S, side="right") - 1
    m_row = m_vehicle + payload_wp[has_pl][k_pl]

    hour = ((t_start + T) // 3600).astype(int)
    rho_row = p_air / (R_air * (T_amb_h[hour] + 273.15))

    cdxa_tab = CdxA0 * np.asarray(W1) + np.asarray(W2)
    v_kmh = np.clip(v_avg * 3.6, cdxa_v[0], cdxa_v[-1])
    j = np.clip(np.searchsorted(cdxa_v, v_kmh, side="right") - 1, 0, len(cdxa_v) - 2)
    w = (v_kmh - cdxa_v[j]) / (cdxa_v[j + 1] - cdxa_v[j])
    cdxa_row = cdxa_tab[hour, j] * (1 - w) + cdxa_tab[hour, j + 1] * w

    P_wheel = m_row * k_lin + m_row ** beta * k_roll + k_rot + rho_row * cdxa_row * L

    drivetrain_effeiciency = motor_eff * inverter_eff * gearbox_eff
    P_trac = np.where(P_wheel > 0, P_wheel / drivetrain_effeiciency, P_wheel * regen_effeiciency)
    P_trac = np.where(M == 3, 0.0, P_trac)
    P_trac = np.where((M == 4) & (V <= v_no_regen), 0.0, P_trac)
    if P_regen_max is not None:
        P_trac = np.maximum(P_trac, -P_regen_max)

    n = len(T)
    pto_row = np.zeros(n)
    pto_active = np.zeros(n, dtype=bool)
    for i in np.where(pto_on_col == 1)[0]:
        at_stop = np.where((V == 0) & np.isclose(S, wp_s[i], rtol=0, atol=1e-3))[0]
        if len(at_stop) == 0:
            raise ValueError(f"no standing rows found for stop at {wp_s[i]} m")
        k0 = at_stop[0] + int(pto_start_col[i])
        k1 = k0 + len(pto_1s)
        if k1 > at_stop[-1] + 1:
            raise ValueError(f"PTO does not fit in stop at {wp_s[i]} m")
        pto_row[k0:k1] = pto_1s
        pto_active[k0:k1] = True

    moving = V > 0
    HVAC_row = np.asarray(HVAC, dtype=float)[hour] if np.ndim(HVAC) else float(HVAC)
    P_aux_row = (ES + PS + HVAC_row
                 + SP * moving
                 + cond * (moving | pto_active)
                 + PTO_always_on
                 + pto_row)

    P_battery = P_trac + P_aux_row
    E_battery = np.sum(P_battery * dt) / 3.6e6

    return P_wheel, P_trac, P_aux_row, P_battery, E_battery
