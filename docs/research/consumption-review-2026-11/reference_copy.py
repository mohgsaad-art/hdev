"""Variants of consumption_engine for the 13 Nov 2026 review.  NOTHING here replaces Bob's code.

Every function has a clear name.  The unchanged notebook function is `consumption_engine` (loaded from the
notebook by _load_notebook.py) and is used as the reference.

    consumption_engine_v_signature_only   Gate 3 adapter.  Renames only; calls the unchanged notebook function.
    pto_rows                              PTO placement on rows (searchsorted, no loop over rows).  Adapted from PR #31
                                          (consumption_step6_v_pto1nov); now returns stop and drive rows separately.
    consumption_engine_v_step6_searchsorted   Appendix 1 with ONLY step 6 replaced (used for the speed test, Part K).
    consumption_engine_v_split_eff        Part C/D test bench: the proposed engine with switches, so every cause can be
                                          turned on/off one at a time.
    consumption_engine_v_proposed         Part I: ONE clean, readable proposal (no switches).

Units: SI inside the proposed functions.  Temperatures in kelvin, speed grid for CdxA in m/s (13 Nov decisions).
Tags in comments: [VECTO] file + lines of mohgsaad-art/VECTO branch IEPC-experiments commit b8d6126.
"""
import numpy as np

from _load_notebook import NS

consumption_engine = NS["consumption_engine"]      # the code of record, unchanged


# ------------------------------------------------------------------------------------------------------------
# Gate 3 adapter: rename only
# ------------------------------------------------------------------------------------------------------------
def consumption_engine_v_signature_only(T, S, V, M, dt,
                                        k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg,
                                        m_vehicle, wp_s, payload_wp, beta,
                                        t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,
                                        ES, PS, HVAC, SP, cond, PTO_always_on,
                                        is_on, pto_start, stop_1s, drive_1s,
                                        motor_eff, inverter_eff, gearbox_eff, regen_effeiciency, v_no_regen,
                                        P_regen_max=None):
    """Names of the final producers (force_engine 6 outputs, pto_engine 4 outputs) -> names of the old consumption_engine.

    RENAME ONLY.  Two things cannot be renamed, so they are refused loudly (rule 3: no silent fallback):
      * k_rot_rotor has no place in the old function  -> must be all zero
      * drive_1s (drive PTO) has no place in the old function -> must be empty
    """
    if np.any(np.asarray(k_rot_rotor) != 0):
        raise ValueError("old consumption_engine has no k_rot_rotor input: it would be dropped silently")
    if np.size(drive_1s) > 0:
        raise ValueError("old consumption_engine has no drive-PTO input: it would be dropped silently")
    return consumption_engine(T, S, V, M, dt, k_lin, k_roll, k_rot_wheel, L, v_avg,
                              m_vehicle, wp_s, payload_wp, beta,
                              t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,
                              ES, PS, HVAC, SP, cond, PTO_always_on,
                              stop_1s, is_on, pto_start,
                              motor_eff, inverter_eff, gearbox_eff, regen_effeiciency, v_no_regen, P_regen_max)


# ------------------------------------------------------------------------------------------------------------
# PTO placement on rows (step 6a).  Vectorised: searchsorted per stop, no scan over all rows per stop.
# ------------------------------------------------------------------------------------------------------------
def _standing_rows(S, M, s_wp, tol_m):
    """Rows of one stop = driver mode M == 0 and |S - s_wp| <= tol.  [TEST] PR #31: V == 0 gives stop + 1 rows,
    because the first accelerating row of the driver also has V == 0 (speed at START of the step)."""
    lo = int(np.searchsorted(S, s_wp - tol_m, side="left"))
    hi = int(np.searchsorted(S, s_wp + tol_m, side="right"))
    return lo + np.where(M[lo:hi] == 0)[0]


def pto_rows(S, M, wp_s, wp_stop, is_on, pto_start, stop_1s, drive_1s, stop_const_W, drive_const_W, tol_m=1e-3):
    """Stop and drive PTO power on rows.  Pure.  Returns stop_row [W], drive_row [W], stop_active, drive_active.

    Rules (Bob, 12 Nov): stop profile = first standing row of the stop + pto_start; stop constant = all standing rows;
    drive profile = from the first moving row after the stop, may run past the next stop (VECTO PTODriveAuxiliary.cs);
    drive constant = all rows from leaving the stop to the first standing row of the next stop; a drive profile that
    starts while the previous one still runs -> error (VECTO PTODriveAuxiliary.cs 25-27).
    Constants are SHAFT/ELECTRIC W already divided by their efficiency by the caller (parser).
    """
    S, M = np.asarray(S, dtype=float), np.asarray(M)
    wp_s, wp_stop, is_on = (np.asarray(x, dtype=float) for x in (wp_s, wp_stop, is_on))
    pto_start = np.asarray(pto_start, dtype=float)
    stop_1s, drive_1s = np.asarray(stop_1s, dtype=float), np.asarray(drive_1s, dtype=float)
    n = len(S)
    stop_row, drive_row = np.zeros(n), np.zeros(n)
    stop_act, drive_act = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    stops = np.where(wp_stop > 0)[0]
    standing = {i: _standing_rows(S, M, wp_s[i], tol_m) for i in stops}
    drive_end = -1
    for i in np.where(is_on == 1)[0]:
        rows = standing.get(i)
        if rows is not None:
            if len(rows) == 0:
                raise ValueError(f"no standing rows for stop at {wp_s[i]} m")
            if len(stop_1s):                                                    # stop profile
                k0 = int(rows[0] + pto_start[i]); k1 = k0 + len(stop_1s)
                if k1 > rows[-1] + 1:
                    raise ValueError(f"stop PTO does not fit in stop at {wp_s[i]} m")
                stop_row[k0:k1] += stop_1s; stop_act[k0:k1] = True
            elif stop_const_W:                                                  # stop constant
                stop_row[rows] += stop_const_W; stop_act[rows] = True
        if len(drive_1s) or drive_const_W:                                      # drive part
            k_start = int(rows[-1]) + 1 if rows is not None else int(np.searchsorted(S, wp_s[i] - tol_m, side="left"))
            nxt = stops[stops > i]
            k_end = int(standing[nxt[0]][0]) if len(nxt) else n
            if k_start >= n:
                continue
            if len(drive_1s):
                if k_start < drive_end:
                    raise ValueError("drive PTO profile starts while the previous one still runs (VECTO throws too)")
                k1 = min(k_start + len(drive_1s), n)
                drive_row[k_start:k1] += drive_1s[:k1 - k_start]; drive_act[k_start:k1] = True
                drive_end = k1
            else:
                drive_row[k_start:k_end] += drive_const_W; drive_act[k_start:k_end] = True
    return stop_row, drive_row, stop_act, drive_act


# ------------------------------------------------------------------------------------------------------------
# Part K: Appendix 1 with ONLY step 6 replaced by the searchsorted version (identical numbers)
# ------------------------------------------------------------------------------------------------------------
def consumption_engine_v_step6_searchsorted(T, S, V, M, dt,
                                            k_lin, k_roll, k_rot, L, v_avg,
                                            m_vehicle, wp_s, payload_wp, beta,
                                            t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,
                                            ES, PS, HVAC, SP, cond, PTO_always_on,
                                            pto_1s, pto_on_col, pto_start_col,
                                            motor_eff, inverter_eff, gearbox_eff, regen_effeiciency, v_no_regen,
                                            P_regen_max=None):
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
        lo = int(np.searchsorted(S, wp_s[i] - 1e-3, side="left"))              # <- only change: searchsorted window,
        hi = int(np.searchsorted(S, wp_s[i] + 1e-3, side="right"))             #    same V == 0 rule as the original
        at_stop = lo + np.where(V[lo:hi] == 0)[0]
        if len(at_stop) == 0:
            raise ValueError(f"no standing rows found for stop at {wp_s[i]} m")
        k0 = at_stop[0] + int(pto_start_col[i]); k1 = k0 + len(pto_1s)
        if k1 > at_stop[-1] + 1:
            raise ValueError(f"PTO does not fit in stop at {wp_s[i]} m")
        pto_row[k0:k1] = pto_1s; pto_active[k0:k1] = True
    moving = V > 0
    HVAC_row = np.asarray(HVAC, dtype=float)[hour] if np.ndim(HVAC) else float(HVAC)
    P_aux_row = ES + PS + HVAC_row + SP * moving + cond * (moving | pto_active) + PTO_always_on + pto_row
    P_battery = P_trac + P_aux_row
    E_battery = np.sum(P_battery * dt) / 3.6e6
    return P_wheel, P_trac, P_aux_row, P_battery, E_battery


# ------------------------------------------------------------------------------------------------------------
# Part C/D test bench: the proposed engine with switches (every switch is one cause to isolate)
# ------------------------------------------------------------------------------------------------------------
def consumption_engine_v_split_eff(T, S, V, M, dt,
                                   k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg,
                                   m_vehicle, wp_s, payload_wp, beta,
                                   t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,
                                   ES, PS, HVAC, SP, cond, PTO_always_on,
                                   wp_stop, is_on, pto_start, stop_1s, drive_1s, stop_const_W, drive_const_W,
                                   drive_pto_mechanical,
                                   gearbox_eff, motor_eff, inverter_eff, v_no_regen, P_regen_max,
                                   *, split_sign=True, rotor_at_motor=True, coast_zero=True, low_speed_rule=True,
                                   cond_rule="moving", moving_rule="start_speed", return_parts=True,
                                   aux_row_override=None):
    """Switches (default = the proposal in consumption_engine_v_proposed):
       split_sign     True: gearbox sign decided at the wheel, motor sign decided at the motor shaft.
                      False: ONE sign decision on P_wheel (Appendix 1), rotor/PTO added AFTER on the electric side without efficiency.
       rotor_at_motor True: k_rot_rotor added at the motor shaft (through motor x inverter efficiency).  False: dropped (Appendix 1).
       coast_zero     M == 3 -> no traction power.            low_speed_rule  M == 4 and V <= v_no_regen -> brakes only.
       cond_rule      'moving' (Appendix 1: V>0 or stop PTO), 'em_on' (VECTO Conditioning.cs 83-91: motor on or E-PTO on)
       aux_row_override  array of electric aux W per row (e.g. the VECTO .vmod column) -> skips step 6 completely.
       gearbox_eff / motor_eff / inverter_eff / v_no_regen / P_regen_max: scalar or per-row array.
    """
    T, S, V, M = (np.asarray(x) for x in (T, S, V, M))
    wp_s, payload_wp = np.asarray(wp_s, dtype=float), np.asarray(payload_wp, dtype=float)
    T_amb_h, cdxa_v = np.asarray(T_amb_h, dtype=float), np.asarray(cdxa_v, dtype=float)
    # 1 mass (BUG-2 fix: clip so a row a hair before wp_s[0] takes the FIRST payload)
    has_pl = ~np.isnan(payload_wp)
    k_pl = np.clip(np.searchsorted(wp_s[has_pl], S, side="right") - 1, 0, None)
    m_row = m_vehicle + payload_wp[has_pl][k_pl]
    # 2 hour
    hour = ((t_start + T) // 3600).astype(int)
    # 3 air (kelvin and m/s inside: no conversion)
    rho_row = p_air / (R_air * T_amb_h[hour])
    cdxa_tab = CdxA0 * np.asarray(W1) + np.asarray(W2)
    v_c = np.clip(v_avg, cdxa_v[0], cdxa_v[-1])
    j = np.clip(np.searchsorted(cdxa_v, v_c, side="right") - 1, 0, len(cdxa_v) - 2)
    w = (v_c - cdxa_v[j]) / (cdxa_v[j + 1] - cdxa_v[j])
    cdxa_row = cdxa_tab[hour, j] * (1 - w) + cdxa_tab[hour, j + 1] * w
    # 4 wheel power
    P_wheel = m_row * k_lin + m_row ** beta * k_roll + k_rot_wheel + rho_row * cdxa_row * L
    # 6a PTO rows (need to be known before step 5 because mechanical drive PTO sits at the motor shaft)
    stop_row, drive_row, stop_act, drive_act = pto_rows(S, M, wp_s, wp_stop, is_on, pto_start, stop_1s, drive_1s,
                                                        stop_const_W, drive_const_W)
    P_pto_mech = drive_row if drive_pto_mechanical else 0.0
    # 5 wheel -> electric traction power
    eta_m = motor_eff * inverter_eff
    rotor = k_rot_rotor if rotor_at_motor else 0.0
    if split_sign:
        P_shaft = np.where(P_wheel > 0, P_wheel / gearbox_eff, P_wheel * gearbox_eff)        # gearbox/axle: sign at the wheel
        P_motor = P_shaft + rotor + P_pto_mech                                                # [VECTO] ElectricMotor.cs 186-188, 297
        if P_regen_max is not None:
            P_motor = np.maximum(P_motor, -P_regen_max)                                       # generator limit at the motor shaft
        P_trac = np.where(P_motor > 0, P_motor / eta_m, P_motor * eta_m)                      # motor + inverter: sign at the motor
    else:
        P_shaft = np.where(P_wheel > 0, P_wheel / gearbox_eff, P_wheel * gearbox_eff)
        P_motor = P_shaft
        P_trac = np.where(P_wheel > 0, P_wheel / (gearbox_eff * eta_m), P_wheel * (gearbox_eff * eta_m)) + rotor + P_pto_mech
        if P_regen_max is not None:
            P_trac = np.maximum(P_trac, -P_regen_max)
    if coast_zero:
        P_trac = np.where(M == 3, P_pto_mech / eta_m if np.ndim(P_pto_mech) else 0.0, P_trac)
    if low_speed_rule:
        P_trac = np.where((M == 4) & (V <= v_no_regen), 0.0, P_trac)
    # 6b aux
    if aux_row_override is not None:
        P_aux_row = np.asarray(aux_row_override, dtype=float)
    else:
        if moving_rule == "start_speed":
            moving = V > 0
        else:
            moving = M != 0
        if cond_rule == "moving":
            cond_on = moving | stop_act
        else:                                            # motor on: not standing, not coasting, or stop PTO
            cond_on = ((M != 0) & (M != 3)) | stop_act
        HVAC_row = np.asarray(HVAC, dtype=float)[hour] if np.ndim(HVAC) else float(HVAC)
        P_aux_row = ES + PS + HVAC_row + SP * moving + cond * cond_on + PTO_always_on + stop_row
        if not drive_pto_mechanical:
            P_aux_row = P_aux_row + drive_row
    P_battery = P_trac + P_aux_row
    E_battery = np.sum(P_battery * dt) / 3.6e6
    if not return_parts:
        return P_wheel, P_trac, P_aux_row, P_battery, E_battery
    return dict(P_wheel=P_wheel, P_shaft=P_shaft, P_motor=P_motor, P_trac=P_trac, P_aux_row=P_aux_row,
                P_battery=P_battery, E_battery=E_battery, m_row=m_row, rho_row=rho_row, cdxa_row=cdxa_row, hour=hour,
                stop_row=stop_row, drive_row=drive_row)


# ------------------------------------------------------------------------------------------------------------
# Part I: ONE clean proposal.  Read this top to bottom.
# ------------------------------------------------------------------------------------------------------------
def consumption_engine_v_proposed(T, S, V, M, dt,                                       # driver_model rows
                                  k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg,    # force_engine (final, 6 outputs)
                                  m_vehicle, wp_s, payload_wp, beta,                    # mass; payload from payload_engine
                                  t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,  # T_amb_h in KELVIN, cdxa_v in m/s
                                  ES, PS, HVAC, SP, cond, PTO_always_on,                # P_aux outputs [W electric]
                                  wp_stop, is_on, pto_start, stop_1s, drive_1s,         # pto_engine outputs + final stop time per waypoint
                                  stop_const_W, drive_const_W, drive_pto_mechanical,    # constants (parser) and the yes/no body question
                                  gearbox_eff, motor_eff, inverter_eff,                 # scalar OR one value per row (maps later)
                                  v_no_regen, P_regen_max):                             # P_regen_max: mechanical W at the motor shaft, or None
    T, S, V, M = (np.asarray(x) for x in (T, S, V, M))
    wp_s, payload_wp = np.asarray(wp_s, dtype=float), np.asarray(payload_wp, dtype=float)
    T_amb_h, cdxa_v = np.asarray(T_amb_h, dtype=float), np.asarray(cdxa_v, dtype=float)

    # --- 1. mass per row.  clip(...,0): a row a hair before wp_s[0] takes the FIRST payload (was: last payload, index -1)
    has_pl = ~np.isnan(payload_wp)
    k_pl = np.clip(np.searchsorted(wp_s[has_pl], S, side="right") - 1, 0, None)
    m_row = m_vehicle + payload_wp[has_pl][k_pl]

    # --- 2. weather hour of each row
    hour = ((t_start + T) // 3600).astype(int)

    # --- 3. air density and CdxA_eff per row (SI: kelvin in, m/s in: no unit conversion inside)
    rho_row = p_air / (R_air * T_amb_h[hour])
    cdxa_tab = CdxA0 * np.asarray(W1) + np.asarray(W2)
    v_c = np.clip(v_avg, cdxa_v[0], cdxa_v[-1])
    j = np.clip(np.searchsorted(cdxa_v, v_c, side="right") - 1, 0, len(cdxa_v) - 2)
    w = (v_c - cdxa_v[j]) / (cdxa_v[j + 1] - cdxa_v[j])
    cdxa_row = cdxa_tab[hour, j] * (1 - w) + cdxa_tab[hour, j + 1] * w

    # --- 4. wheel power [W], positive = driving
    P_wheel = m_row * k_lin + m_row ** beta * k_roll + k_rot_wheel + rho_row * cdxa_row * L

    # --- 5a. PTO on rows (stop and drive separately); mechanical drive PTO sits at the motor shaft, electric one in step 6
    stop_row, drive_row, stop_active, _ = pto_rows(S, M, wp_s, wp_stop, is_on, pto_start, stop_1s, drive_1s,
                                                   stop_const_W, drive_const_W)
    P_pto_mech = drive_row if drive_pto_mechanical else 0.0

    # --- 5b. wheel -> motor shaft: axle + gearbox, sign decided at the wheel
    P_shaft = np.where(P_wheel > 0, P_wheel / gearbox_eff, P_wheel * gearbox_eff)
    # --- 5c. rotor inertia and mechanical drive PTO are added at the motor shaft, after the gearbox  [VECTO ElectricMotor.cs 186-188, 297]
    P_motor = P_shaft + k_rot_rotor + P_pto_mech
    if P_regen_max is not None:
        P_motor = np.maximum(P_motor, -P_regen_max)                      # generator limit; the rest goes to the friction brakes
    # --- 5d. motor + inverter: sign decided at the motor shaft
    eta_m = motor_eff * inverter_eff
    P_trac = np.where(P_motor > 0, P_motor / eta_m, P_motor * eta_m)
    # --- 5e. motor off: coasting (M 3) and braking below v_no_regen (M 4).  A running mechanical PTO still needs the motor.
    pto_el = P_pto_mech / eta_m
    P_trac = np.where(M == 3, pto_el, P_trac)                            # [VECTO] BatteryElectricMotorController.cs 44-47
    P_trac = np.where((M == 4) & (V <= v_no_regen), 0.0, P_trac)         # [VECTO] same file 62-70; threshold = Constants.cs 321 for an AMT E2

    # --- 6. aux per row
    moving = V > 0                                                       # [VECTO] ElectricAuxiliaries.cs 105-116, Vehicle.cs 326: start speed
    motor_on = (M != 0) & (M != 3)                                       # [VECTO] Conditioning.cs 83-91: a motor is on, or E-PTO on
    HVAC_row = np.asarray(HVAC, dtype=float)[hour] if np.ndim(HVAC) else float(HVAC)
    PTO_always_row = np.asarray(PTO_always_on, dtype=float)[hour] if np.ndim(PTO_always_on) else float(PTO_always_on)
    P_aux_row = (ES + PS + HVAC_row + SP * moving + cond * (motor_on | stop_active) + PTO_always_row + stop_row
                 + (0.0 if drive_pto_mechanical else drive_row))

    # --- 7. battery terminal power and energies
    P_battery = P_trac + P_aux_row
    dt_h = dt / 3.6e6
    E_battery = np.sum(P_battery * dt_h)                                 # net trip energy [kWh]
    E_drive = np.sum(np.maximum(P_trac, 0.0) * dt_h)
    E_regen = np.sum(np.minimum(P_trac, 0.0) * dt_h)                     # negative number
    E_brake = np.sum(np.minimum(P_wheel, 0.0) * dt_h)                    # all wheel braking energy [kWh, negative]; E_regen is the part that reached the battery
    E_aux = np.sum(P_aux_row * dt_h)
    return dict(P_wheel=P_wheel, P_motor=P_motor, P_trac=P_trac, P_aux_row=P_aux_row, P_battery=P_battery,
                E_battery=E_battery, E_drive=E_drive, E_regen=E_regen, E_wheel_braking=E_brake, E_aux=E_aux,
                E_pto_stop=np.sum(stop_row * dt_h), E_pto_drive=np.sum(drive_row * dt_h))
