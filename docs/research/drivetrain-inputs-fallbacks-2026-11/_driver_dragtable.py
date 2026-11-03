"""TEST-ONLY copy of the code-of-record driver model with the AGREED driver-model
edits for the drag table (Part D7). Bob's engine is NOT touched; this file exists so
the drag-table-in-the-driver comparison can run.

Agreed edits vs reference_copy.driver_model (and ONLY these):
  1. drag_v=(0.0,), drag_F=(0.0,) default arguments (a drag FORCE vs speed table),
     replacing the scalar P_drag_loss.
  2. coast_acc and coast_distance read the drag FORCE directly as
     interp1(v, drag_v, drag_F)  (N), instead of P_drag_loss / v.
  3. g default = 9.80665 (VECTO), not 9.81.
  4. inputs already in m/s for the drag table (drag_v in m/s).

Everything else is byte-for-byte the code of record. The diff is annotated with
### EDIT markers.
"""
import math
import bisect

import numpy as np


def interp1(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    i = bisect.bisect_right(xs, x)
    return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])


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


def coast_distance(v, v_target, h_now, h_target, s_now, s_target,
                   coast_mass, m_red_wheels, cdxa_v, cdxa, Crr, rho, g,
                   drag_v, drag_F,                                   ### EDIT: table not scalar
                   df_offset, df_scaling, df_vtarget, df_vdrop):
    m_eff = coast_mass + m_red_wheels
    dE = m_eff * g * (h_now - h_target) + m_eff * (v ** 2 - v_target ** 2) / 2
    v_avg = (v + v_target) / 2
    cda = interp1(v_avg, cdxa_v, cdxa)
    F_air = rho / 8 * cda * (v + v_target) * (v ** 2 + v_target ** 2) / v_avg
    grad = (h_target - h_now) / (s_target - s_now)
    F_roll = math.cos(grad) * coast_mass * g * Crr
    F_loss = interp1(v_avg, drag_v, drag_F)                         ### EDIT: drag FORCE at v_avg
    f_vt = interp1(v_target * 3.6, df_vtarget[0], df_vtarget[1])
    f_vd = interp1((v - v_target) * 3.6, df_vdrop[0], df_vdrop[1])
    DF = df_offset - df_scaling * f_vt * f_vd
    return dE / (DF * (F_air + F_roll + F_loss))


def driver_model(wp_s, wp_v, wp_stop, wp_grade,
                 vacc_v, vacc_acc, vacc_dec, dt=1.0,
                 coast_mass=None, m_red_wheels=0.0, cdxa_v=None, cdxa=None, Crr=None,
                 rho=1.188, g=9.80665,                              ### EDIT: VECTO gravity
                 drag_v=(0.0,), drag_F=(0.0,), P_max=None,          ### EDIT: drag table
                 lac_min_v=50.0, lac_dist_factor=10.0, df_offset=2.5, df_scaling=1.5,
                 df_vtarget=((0, 48, 52, 100), (0, 0, 1, 1)),
                 df_vdrop=((-100, 9, 11, 100), (1, 1, 0, 0)),
                 os_min_v=50.0, os_allowed=2.5, brake_margin=0.1, v_min_coast=5.0):

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

    dv = list(drag_v)                                               ### EDIT: drag table in m/s
    dF = list(drag_F)

    def coast_acc(v, k):
        th = math.atan(gr_l[k] / 100)
        F = (rho / 2 * interp1(v, cv, cc) * v * v
             + coast_mass * g * Crr * math.cos(th)
             + coast_mass * g * math.sin(th)
             + interp1(v, dv, dF))                                  ### EDIT: drag FORCE at v
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
                                    coast_mass, m_red_wheels, cv, cc, Crr, rho, g,
                                    dv, dF,                         ### EDIT: pass table
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
                    v_cap = math.sqrt(max(action[2] ** 2 + 2 * -dec_max * max(room, 0.0), 0.0))
                    a = max(min(a, (v_cap - v) / dt), 0.0)
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

    T = np.asarray(T); S = np.asarray(S); V = np.asarray(V); A = np.asarray(A)
    M = np.asarray(M, dtype=int)
    s_next = np.append(S[1:], s)
    ds_row = s_next - S
    h1 = np.interp(S, s_wp, alt_wp)
    h2 = np.interp(s_next, s_wp, alt_wp)
    k_row = np.searchsorted(s_wp, S, side="right") - 1
    grade = np.where(ds_row > 1e-9, (h2 - h1) / np.where(ds_row > 1e-9, ds_row, 1.0) * 100, gr_wp[k_row])
    return T, S, V, A, grade, M
