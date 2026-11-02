# =====================================================================================
# HDEV TEST HARNESS v1.7 (22 Oct 2026)
# Run in Colab AFTER the cells that define your engine functions:
#   crosswind_engine, payload_engine, pto_engine, driver_model, force_engine,
#   P_aux, SP_power_helper, consumption_engine (with p_air, R_air in the signature)
# The harness calls YOUR functions; it does not contain copies of them.
#
# NEW IN v1.6/1.7
#   - Aux technologies now match the VECTO job BEV_E2.vecto (harness error in v1.5 fixed):
#       PS  "Vacuum pump + elec. driven"   (was "Small + elec. driven": 750 -> 200 W Regional, 813 -> 162 W Urban)
#       STP "Full electric steering gear"  (was "Electric driven pump": 203 -> 23 W Regional)
#   - HVAC thermal (reference) now also on RegionalDelivery, so both VECTO-compared cycles show it
#   - 7e: T19 exports HDEV outputs only (1 Hz rows with wheel-power split + parts table, base and with VECTO's
#         trip-average efficiencies, monthly HVAC table) and zips them -> hdev_outputs.zip. The VECTO comparison is done outside Colab.
#
# Tags used in comments and printouts:
#   [VECTO]   value/rule read from VECTO source (file + line given)
#   [ASSUMP]  HDEV or test choice with no VECTO source -> results depend on it
#   [ILLUS]   illustrative test value, NOT sourced (change in CONFIG)
#   [TEST]    test-only glue that stands in for the parser (not production code)
# =====================================================================================
 
import time, math, traceback, os, io, urllib.request, urllib.parse, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
 
# -------------------------------------------------------------------------------------
# 0. CONFIG  (everything you may want to change is here)
# -------------------------------------------------------------------------------------
VECTO_RAW = "https://raw.githubusercontent.com/mohgsaad-art/VECTO/IEPC-experiments/"   # your repo, branch IEPC-experiments
VECTO_LOCAL = None             # or a local path to the repo root (then no download)
OUT_DIR = "/content/hdev_test_out" if os.path.isdir("/content") else "./hdev_test_out"
 
COMPARE_CYCLES = ["RegionalDelivery", "UrbanDelivery"]   # cycles exported for the VECTO comparison
 
WEATHER_SOURCE = "dmi"         # "dmi" (real hourly data) or "synthetic" (offline smoke test only)
DMI_BASE = "https://opendataapi.dmi.dk/v2/climateData/collections"   # key-less climateData API (same as your DMI code)
SITE_LAT, SITE_LON = 55.6800, 12.4500                  # your DMI code's default point (Copenhagen)
YEAR = 2025                                            # weather year to fetch
MIN_HOURS_PER_YEAR = 8000                              # a station must have at least this many hourly values of a parameter
MAX_STATIONS = 80                                      # how many nearest stations to try per parameter
 
DAY = "2025-01-15"             # day for the full one-day graphs (nearest complete day is used if incomplete)
DAY_CYCLE = "MunicipalUtility"  # cycle for the one-day graphs ("UrbanDelivery", "RegionalDelivery", "MunicipalUtility" incl. refuse PTO, ...)
YEAR_CYCLE = "RegionalDelivery"  # cycle run on every day of the year
DEPART_LOCAL = "07:00"         # departure time (local) for weather runs [ILLUS]
 
# drivetrain efficiencies: UNSOURCED placeholders (memory says "Annex Xb placeholders"; not traced) [ILLUS]
MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF = 0.95, 0.95, 0.98
REGEN_EFF = MOTOR_EFF * INVERTER_EFF * GEARBOX_EFF     # [ASSUMP] regen uses the same chain efficiency as driving
V_NO_REGEN = 5 / 3.6                                   # [VECTO] Constants.cs line 323 (E3/E4 value; E2 derives it from gear ratios)
BETA = 0.9                                             # [VECTO] Physics.cs line 51 RollResistanceExponent
BETA_LIMIT_YEAR = 10.0                                 # HDEV crosswind yaw clamp decision (6 Oct) for real-wind runs; None = VECTO
P_AIR, R_AIR = 101325.0, 287.05                        # [ASSUMP] ISO 2533 sea-level pressure + dry-air gas constant (VECTO has fixed rho only)
 
# -------------------------------------------------------------------------------------
# 1. SOURCED CONSTANTS AND VEHICLE  (VECTO generic E2 BEV, group 2 rigid truck)
# -------------------------------------------------------------------------------------
G = 9.80665                    # [VECTO] DeclarationData.cs line 72
RHO_VECTO = 1.188              # [VECTO] DeclarationData.cs line 74
ALT_EFF = 0.7                  # [VECTO] DeclarationData.cs line 123 AlternatorEfficiency (also applied to electric steering, see AUX)
V_DECL, H_DECL, HELLMANN = 3.0, 4.0, 0.2   # [VECTO] Physics.cs 56-66 declaration wind
H_DMI = 10.0                   # DMI wind measured at 10 m (your 6 Oct note)
CDXA_V = np.arange(60, 131, 5.0)           # [VECTO] Constants.cs 355-357: 60..130 km/h step 5
 
VEH = dict(                    # [VECTO] Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BatteryElectricVehicle.vveh
    curb=4670.0,               # CurbWeight [kg]
    tpmlm=11990.0,             # MassMax 11.99 t
    CdxA0=4.83,                # CdA [m2]
    axles_rrc=[0.0065, 0.0075], axles_fz=[20850.0, 20850.0], axles_wheels=[2, 4],   # RRCISO, FzISO, twin rear
    wheel_inertia=6.5,         # per wheel [kg m2]
    em_count=2, em_ratio=2.0, em_mech_eff=0.97,
)
SEG = dict(                    # [VECTO] SegmentTable.csv row 8: group 2, RigidTruck 4x2, 10-12 t
    body_mass=1900.0,          # body B2, Body_Trailers_Weights.csv
    height=3.75,               # vehicle height used for crosswind (AirdragDataAdapter.cs 126 uses mission.VehicleHeight)
    axle_share=[0.45, 0.55],   # "Truck Axles - Other" 45/55
    a123=(0.013526, 0.017746, -0.000666),   # VCDV_parameters.csv RigidSolo
)
# reference payload: 50 % column of Payloads.csv interpolated at TPMLM (Payloads.cs 54-57)  [VECTO]
def vecto_payload_50(tpmlm):
    gvw = [3500, 7400, 7500, 16000]; p50 = [420, 1210, 1250, 4600]
    return float(np.interp(tpmlm, gvw, p50))
PAYLOAD_REF = vecto_payload_50(VEH["tpmlm"])
M_VEHICLE = VEH["curb"] + SEG["body_mass"]           # vehicle without payload [kg]
# [ASSUMP] VECTO may also limit payload to the available capacity; not checked here (6570 + 3020 < 11990 anyway)
 
# tyre radius + wheel inertia  [VECTO] Wheels.csv 265/70 R19.5: d = 867 mm, F = 3.05; Wheels.cs line 74 r = d*F/(2*pi)
R_DYN = 0.867 * 3.05 / (2 * math.pi)
THETA_WHEELS = VEH["wheel_inertia"] * sum(VEH["axles_wheels"])   # VehicleData.cs 307: sum of wheel inertias
M_RED_WHEELS = THETA_WHEELS / R_DYN**2                           # [ASSUMP] reduced mass = I / r_dyn^2 (motor rotor inertia ignored)
 
# rolling resistance  [VECTO] VehicleData.cs 292-311
def crr_total_vecto(m):        # VECTO's mass-dependent total coefficient
    s = np.array(SEG["axle_share"]); rrc = np.array(VEH["axles_rrc"]); fz = np.array(VEH["axles_fz"]); n = np.array(VEH["axles_wheels"])
    return float(np.sum(s * rrc * (s * m * G / fz / n) ** (BETA - 1)))
def crr_eff(beta):             # constant so that F_roll = Crr_eff * g * m**beta reproduces VECTO exactly (parser item)
    s = np.array(SEG["axle_share"]); rrc = np.array(VEH["axles_rrc"]); fz = np.array(VEH["axles_fz"]); n = np.array(VEH["axles_wheels"])
    return float(G ** (beta - 1) * np.sum(s * rrc * (s / fz / n) ** (beta - 1)))
CRR_EFF = crr_eff(BETA)
 
# aux inputs per mission, group 2 BEV  [VECTO] VAUX tables; technologies = the ones in BEV_E2.vecto (Aux list):
#   STP "Full electric steering gear", AC "Default", ES "Standard technology", PS "Vacuum pump + elec. driven"
# ES:   ES-Tech.csv "Standard technology" mech W; your P_aux applies x0.7 -> 1000 W electric (VECTO .vmod shows 1000 W)
# PS:   PS-Table.csv line 39 "Vacuum pump + elec. driven", _el columns (electric W, used as-is for a fully electric PS:
#       HeavyLorryAuxiliaryDataAdapter.cs 139-143); LH 237, RD 200, UD 162, MU 162, Constr 162
# HVAC: HVAC-Table.csv "Default" group 2 (x 1.25 inside your P_aux -> 250 / 187.5 W, VECTO .vmod shows the same)
# SP:   SP-Table.csv group 2 (U+F / B / S) x SP-Tech.csv line 9 "Full electric steering gear" (0 / 0.143 / 1.429),
#       electric W = that x 0.7 (HeavyLorryAuxiliaryDataAdapter.cs 220) -> 23.0 W Regional (VECTO .vmod shows 23.0 W while moving)
# Cond: Cond-Table.csv Lorry (600 / 550 W)
AUX = {
    "LongHaul":         dict(ES=1714.2857, PS=237, HVAC=200, SP=(340, 30, 0),  cond=600),
    "RegionalDelivery": dict(ES=1428.5714, PS=200, HVAC=200, SP=(290, 30, 20), cond=600),
    "UrbanDelivery":    dict(ES=1428.5714, PS=162, HVAC=150, SP=(260, 20, 30), cond=550),
    "MunicipalUtility": dict(ES=1428.5714, PS=162, HVAC=150, SP=(260, 20, 30), cond=550),  # [ASSUMP] HVAC + SP use UD values (MU not a group-2 mission)
    "Construction":     dict(ES=1428.5714, PS=162, HVAC=200, SP=(290, 30, 20), cond=600),  # [ASSUMP] RD values (not a group-2 mission)
}
SP_AXLE_SHARES = [[100, 100, 100]]
SP_TECH = [[0.0, 0.143, 1.429]]   # [VECTO] SP-Tech.csv line 9 "Full electric steering gear" (U+F / B / S)
 
MODE_NAMES = {0: "stop", 1: "accelerate", 2: "cruise", 3: "coast", 4: "brake"}
 
# -------------------------------------------------------------------------------------
# 2. RESULT BOOK-KEEPING
# -------------------------------------------------------------------------------------
os.makedirs(OUT_DIR, exist_ok=True)
RESULTS = []
def check(tid, name, ok, detail=""):
    if isinstance(ok, (bool, np.bool_)):
        ok = bool(ok)
    status = "PASS" if ok is True else ("FAIL" if ok is False else ok)   # ok may be "INFO"/"WARN"
    RESULTS.append(dict(test=tid, check=name, status=status, detail=detail))
    print(f"  [{status:4}] {tid} {name}  {detail}")
def run_test(tid, title, fn):
    print(f"\n=== {tid}: {title}")
    t0 = time.time()
    try:
        fn()
    except Exception as e:
        RESULTS.append(dict(test=tid, check=title, status="ERROR", detail=f"{type(e).__name__}: {e}"))
        print(f"  [ERROR] {type(e).__name__}: {e}")
        traceback.print_exc(limit=3)
    print(f"  ({time.time()-t0:.2f} s)")
def show(df, name, max_rows=40):
    df.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    with pd.option_context("display.width", 200, "display.max_columns", 30, "display.float_format", "{:.4g}".format):
        print(f"\n--- table: {name}  (full table saved to {name}.csv)")
        print(df.head(max_rows).to_string(index=False))
 
# plotting style: thin lines, recessive grid, fixed categorical colour order, one y-axis per panel
PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
plt.rcParams.update({"axes.prop_cycle": plt.cycler(color=PAL), "lines.linewidth": 1.5, "axes.grid": True,
                     "grid.color": "#d9d8d4", "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 110, "font.size": 9, "legend.frameon": False})
def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(OUT_DIR, f"{name}.png"), dpi=130); plt.show()
 
# -------------------------------------------------------------------------------------
# 3. FILE LOADERS  [TEST]
# -------------------------------------------------------------------------------------
def _get(rel):
    if VECTO_LOCAL:
        with open(os.path.join(VECTO_LOCAL, rel), "rb") as f:
            return f.read()
    url = VECTO_RAW + urllib.parse.quote(rel)
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()
DECL = "VectoCore/VectoCore/Resources/Declaration/"
def read_csv_numeric(rel, enc="utf-8-sig"):
    text = _get(rel).decode(enc, errors="replace").replace("﻿", "")
    lines = [l for l in text.splitlines() if l.strip()]
    header = [h.strip() for h in lines[0].split(",")]
    rows = []
    for l in lines[1:]:
        try:
            rows.append([float(x) for x in l.split(",")])
        except ValueError:
            continue
    return header, np.array(rows)
def load_cycle(name):
    h, a = read_csv_numeric(DECL + f"MissionCycles/{name}.vdri")
    col = {k: i for i, k in enumerate(h)}
    cyc = dict(name=name, s=a[:, col["<s>"]], v=a[:, col["<v>"]], grad=a[:, col["<grad>"]], stop=a[:, col["<stop>"]],
               pto=a[:, col["<PTO>"]] if "<PTO>" in col else np.zeros(len(a)))
    return cyc
_, VACC = read_csv_numeric(DECL + "VACC/Truck.vacc", enc="latin-1")          # [VECTO] header has a superscript 2
_, PTO_PROF = read_csv_numeric(DECL + "MissionCycles/MunicipalUtility_PTO_generic.vptoel")
PTO_T, PTO_W = PTO_PROF[:, 0], PTO_PROF[:, 1] * 1000.0                       # kW -> W
_, EM_FLD = read_csv_numeric("Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/GenericEMotor_125kW_485Nm.vemp")
CYCLES = {n: load_cycle(n) for n in ["LongHaul", "RegionalDelivery", "UrbanDelivery", "MunicipalUtility", "Construction"]}
print(f"Loaded: {list(CYCLES)}, Truck.vacc {VACC.shape}, PTO profile {len(PTO_T)} rows, EM full-load {EM_FLD.shape}")
print(f"Vehicle: m_vehicle {M_VEHICLE:.0f} kg, ref payload {PAYLOAD_REF:.1f} kg, r_dyn {R_DYN:.4f} m, "
      f"m_red_wheels {M_RED_WHEELS:.1f} kg, Crr_eff(beta={BETA}) {CRR_EFF:.6g}, Crr_total(ref mass) {crr_total_vecto(M_VEHICLE+PAYLOAD_REF):.6g}")
 
# -------------------------------------------------------------------------------------
# 4. TEST-ONLY GLUE (stands in for the parser)  [TEST]
# -------------------------------------------------------------------------------------
def extend_stops(stop, pto_flag, pto_dur, mode="vecto"):
    # parser rule (21 Oct): VECTO = stop + PTO duration where PTO is on; "max" = max(stop, PTO duration) [ASSUMP]
    stop = np.asarray(stop, float).copy(); is_stop = stop > 0; is_stop[0] = False
    on = is_stop & (np.asarray(pto_flag) > 0)
    stop[on] = stop[on] + pto_dur if mode == "vecto" else np.maximum(stop[on], pto_dur)
    return stop, on
 
def cdxa_table(v_ref_list, h_ref, beta_limit):
    # calls YOUR crosswind_engine; dh = height/10 and 10 deg steps match VECTO's grid (AirdragDataAdapter.cs 30-60)
    a1, a2, a3 = SEG["a123"]
    W1, W2 = crosswind_engine(SEG["height"], np.asarray(v_ref_list, float), h_ref, a1, a2, a3, HELLMANN,
                              SEG["height"] / 10, 10, CDXA_V, beta_limit)
    return np.asarray(W1), np.asarray(W2)
 
W1_DECL, W2_DECL = cdxa_table([V_DECL], H_DECL, None)
CDXA_REF = VEH["CdxA0"] * W1_DECL[0] + W2_DECL[0]                 # reference CdxA table for the driver (21 Oct)
T_VECTO_EQ = P_AIR / (R_AIR * RHO_VECTO) - 273.15                 # temperature giving rho = 1.188 with ISO p, R
 
def aux_values(mission):
    a = AUX[mission]
    sp_raw = SP_power_helper(a["SP"], SP_AXLE_SHARES, SP_TECH)
    mech = float(np.sum(np.asarray(a["SP"], float) * np.asarray(SP_TECH[0], float)))   # VECTO steering demand before x0.7
    sp_eff = ALT_EFF if abs(sp_raw - mech) < 1e-6 * max(mech, 1) else 1.0   # detects whether your helper already applies x0.7
    out = P_aux(a["ES"], a["PS"], a["HVAC"], sp_raw, a["cond"], 0.0, SP_alteff=sp_eff)
    ES, PS, HVAC, SP, cond, PTO_on = [float(np.asarray(x)) for x in out]
    return dict(ES=ES, PS=PS, HVAC=HVAC, SP=SP, cond=cond, PTO_always_on=PTO_on, sp_helper_raw=float(sp_raw), sp_eff_used=sp_eff)
 
def run_chain(cyc, payload_mode=("constant", None, None, None), stop_mode="vecto", pto_on=True,
              weather=None, coast=True, P_regen_max=None, PTO_always_on=0.0, mission=None, pto_profile=None, hvac_W=None):
    """Full chain: stop extension -> payload_engine -> pto_engine -> driver_model -> force_engine -> consumption_engine.
    weather = dict(T_amb_h, W1, W2, t_start) or None (= VECTO-equivalent: rho 1.188, declaration wind, every hour)
    hvac_W  = None -> VECTO constant HVAC (HVAC-Table.csv x 1.25); or electric W from HVAC thermal (number or one value per weather hour)"""
    mission = mission or cyc["name"]
    pto_t, pto_w = (PTO_T, PTO_W) if pto_profile is None else pto_profile
    pto_dur = (pto_t[-1] - pto_t[0]) if len(pto_t) else 0.0
    flag = cyc["pto"] if pto_on else np.zeros(len(cyc["s"]))
    stop_final, on_mask = extend_stops(cyc["stop"], flag, pto_dur, stop_mode)
    is_stop = stop_final > 0; is_stop[0] = False
    shape, p0, p1, pcustom = payload_mode
    payload_wp = payload_engine(stop_final, shape, PAYLOAD_REF if p0 is None else p0, p1, pcustom)
    pto_1s, pto_on_col, pto_start_col = pto_engine(stop_final, on_mask[is_stop].astype(float), pto_t, pto_w)
    m_ref = M_VEHICLE + PAYLOAD_REF
    t0 = time.time()
    T, S, V, A, Gr, M = driver_model(cyc["s"], cyc["v"], stop_final, cyc["grad"], VACC[:, 0], VACC[:, 1], VACC[:, 2],
                                     coast_mass=(m_ref if coast else None), m_red_wheels=M_RED_WHEELS,
                                     cdxa_v=CDXA_V, cdxa=CDXA_REF, Crr=crr_total_vecto(m_ref), rho=RHO_VECTO, g=G)
    t_drv = time.time() - t0
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, CRR_EFF, V, A, 1.0, Gr, R_DYN, THETA_WHEELS)
    if weather is None:
        nh = int(T[-1] // 3600) + 2
        weather = dict(T_amb_h=np.full(nh, T_VECTO_EQ), W1=np.repeat(W1_DECL, nh, 0), W2=np.repeat(W2_DECL, nh, 0), t_start=0.0)
    aux = dict(aux_values(mission))
    if hvac_W is not None:
        aux["HVAC"] = np.asarray(hvac_W, dtype=float) if np.ndim(hvac_W) else float(hvac_W)   # already electric W (HVAC_eff = 1.0)
    hour = ((weather["t_start"] + T) // 3600).astype(int)
    HVAC_row = aux["HVAC"][hour] if np.ndim(aux["HVAC"]) else np.full(len(T), aux["HVAC"])
    t0 = time.time()
    P_wheel, P_trac, P_aux_row, P_battery, E_battery = consumption_engine(
        T=T, S=S, V=V, M=M, dt=1.0, k_lin=k_lin, k_roll=k_roll, k_rot=k_rot, L=L, v_avg=v_avg,
        m_vehicle=M_VEHICLE, wp_s=cyc["s"], payload_wp=payload_wp, beta=BETA,
        t_start=weather["t_start"], T_amb_h=weather["T_amb_h"], W1=weather["W1"], W2=weather["W2"], cdxa_v=CDXA_V,
        CdxA0=VEH["CdxA0"], p_air=P_AIR, R_air=R_AIR,
        ES=aux["ES"], PS=aux["PS"], HVAC=aux["HVAC"], SP=aux["SP"], cond=aux["cond"], PTO_always_on=PTO_always_on,
        pto_1s=pto_1s, pto_on_col=pto_on_col, pto_start_col=pto_start_col,
        motor_eff=MOTOR_EFF, inverter_eff=INVERTER_EFF, gearbox_eff=GEARBOX_EFF, regen_effeiciency=REGEN_EFF,
        v_no_regen=V_NO_REGEN, P_regen_max=P_regen_max)
    t_con = time.time() - t0
    return dict(cyc=cyc, stop_final=stop_final, payload_wp=payload_wp, pto_1s=pto_1s, pto_on_col=pto_on_col,
                pto_start_col=pto_start_col, T=T, S=S, V=V, A=A, G=Gr, M=M, k_lin=k_lin, k_roll=k_roll, k_rot=k_rot,
                L=L, v_avg=v_avg, P_wheel=P_wheel, P_trac=P_trac, P_aux_row=P_aux_row, P_battery=P_battery,
                E_battery=E_battery, aux=aux, t_drv=t_drv, t_con=t_con, weather=weather, PTO_always_on=PTO_always_on, HVAC_row=HVAC_row)
 
def split_energy(r):
    """Energy per component [kWh]; aux parts recomputed with the agreed on-rules (independent of consumption_engine)."""
    V, a, n = r["V"], r["aux"], len(r["T"])
    pto_row = np.zeros(n); pto_act = np.zeros(n, bool)
    for i in np.where(r["pto_on_col"] == 1)[0]:
        at = np.where((V == 0) & np.isclose(r["S"], r["cyc"]["s"][i], rtol=0, atol=1e-3))[0]
        k0 = at[0] + int(r["pto_start_col"][i]); pto_row[k0:k0 + len(r["pto_1s"])] = r["pto_1s"]; pto_act[k0:k0 + len(r["pto_1s"])] = True
    moving = V > 0
    comp = dict(traction=np.maximum(r["P_trac"], 0), regen=np.minimum(r["P_trac"], 0),
                ES=np.full(n, a["ES"]), PS=np.full(n, a["PS"]), HVAC=r["HVAC_row"],
                SP=a["SP"] * moving, Cond=a["cond"] * (moving | pto_act), PTO_stop=pto_row, PTO_always=np.full(n, r["PTO_always_on"]))
    return {k: float(np.sum(v) / 3.6e6) for k, v in comp.items()}, comp
 
def seg_target(cyc):           # [TEST] the speed the driver aims for in each waypoint segment (same rule as driver_model)
    v = cyc["v"] / 3.6; out = np.zeros(len(v)); nxt = 0.0
    for i in range(len(v) - 1, -1, -1):
        out[i] = v[i] if v[i] > 0 else nxt
        if v[i] > 0: nxt = v[i]
    return out
 
def typed_route(total_km, n_stops, stop_s, v_kmh, grade_amp=0.0, hill_len_m=2000.0, depot_dwell=60.0):
    """[TEST] simple waypoint builder standing in for the typed-input resolver: evenly spaced stops,
    one road speed, optional sine hills (grade_amp in %). Waypoint every 100 m, VECTO .vdri layout."""
    L = total_km * 1000; s = np.arange(0, L + 1, 100.0)
    v = np.full(len(s), float(v_kmh)); stop = np.zeros(len(s))
    v[0] = 0; stop[0] = depot_dwell
    if n_stops > 0:
        idx = np.unique(np.round(np.linspace(0, len(s) - 1, n_stops + 2)[1:-1]).astype(int))
        v[idx] = 0; stop[idx] = stop_s
    grad = grade_amp * np.sin(2 * np.pi * s / hill_len_m)
    return dict(name=f"typed_{total_km}km_{n_stops}stops", s=s, v=v, grad=grad, stop=stop, pto=np.zeros(len(s)))
 
# -------------------------------------------------------------------------------------
# 5. TESTS
# -------------------------------------------------------------------------------------
STORE = {}
 
def t00():
    need = ["crosswind_engine", "payload_engine", "pto_engine", "driver_model", "force_engine", "P_aux", "SP_power_helper", "consumption_engine"]
    missing = [f for f in need if f not in globals()]
    check("T00", "your functions are defined", not missing, f"missing: {missing}" if missing else "all 8 found")
    import inspect
    params = list(inspect.signature(consumption_engine).parameters)
    check("T00", "consumption_engine has p_air, R_air", ("p_air" in params and "R_air" in params), str(params[16:24]))
    for c in COMPARE_CYCLES:
        a = aux_values(c)
        check("T00", f"aux W used for {c} (electric)", "INFO",
              f"ES {a['ES']:.1f}, PS {a['PS']:.1f}, HVAC {a['HVAC']:.1f}, SP {a['SP']:.2f}, Cond {a['cond']:.1f}  (SP helper raw {a['sp_helper_raw']:.2f}, x{a['sp_eff_used']})")
run_test("T00", "setup", t00)
 
def t01():
    # VECTO declaration crosswind curve, transcribed from AirdragDataAdapter.cs 20-87 (reference implementation)
    a1, a2, a3 = SEG["a123"]; H = SEG["height"]; ref = []
    for spd in CDXA_V:
        vv = spd / 3.6; tot = 0.0
        for hp in range(5, 100, 10):
            vw = V_DECL * (hp / 100 * H / H_DECL) ** HELLMANN
            for al in range(0, 181, 10):
                vx = vv + vw * math.cos(math.radians(al)); vy = vw * math.sin(math.radians(al))
                b = math.degrees(math.atan(vy / vx)); cda = VEH["CdxA0"] + a1 * b + a2 * b * b + a3 * b ** 3
                share = (5 if al in (0, 180) else 10) / 180
                tot += 0.1 * share * cda * (vx * vx + vy * vy) / (vv * vv)
        ref.append(tot)
    ref = np.array(ref); rel = np.max(np.abs(CDXA_REF / ref - 1)) * 100
    check("T01", "crosswind_engine == VECTO declaration CdxA curve", rel < 0.01, f"max diff {rel:.4f} % (60-130 km/h)")
    show(pd.DataFrame(dict(v_kmh=CDXA_V, cdxa_vecto=ref, cdxa_yours=CDXA_REF)), "T01_cdxa_curve", 15)
    W1, W2 = cdxa_table([0.0], H_DMI, None)
    check("T01", "no wind -> W1 = 1, W2 = 0", bool(np.allclose(W1, 1) and np.allclose(W2, 0)), f"W1 {W1.min():.6f}..{W1.max():.6f}, W2 max {np.abs(W2).max():.2e}")
run_test("T01", "crosswind engine vs VECTO", t01)
 
def t02():
    cyc = CYCLES["MunicipalUtility"]
    pto_dur = PTO_T[-1] - PTO_T[0]
    stop_final, on = extend_stops(cyc["stop"], cyc["pto"], pto_dur)
    is_stop = stop_final > 0; is_stop[0] = False
    pto_1s, pto_on_col, pto_start_col = pto_engine(stop_final, on[is_stop].astype(float), PTO_T, PTO_W)
    e = pto_1s.sum() / 3.6e6
    check("T02", "PTO profile duration (VECTO 23 s)", pto_dur == 23 and len(pto_1s) == 23, f"{pto_dur:.0f} s, {len(pto_1s)} values")
    check("T02", "PTO energy per stop = 0.14993 kWh", abs(e - 0.14993) < 5e-6, f"{e:.5f} kWh")
    check("T02", "PTO stops = 96 (VECTO cycle flags)", int(np.nansum(pto_on_col == 1)) == 96, f"{int(np.nansum(pto_on_col == 1))}")
    st = pto_start_col[pto_on_col == 1]
    check("T02", "standing 25 s -> PTO starts at 1 s (VECTO 1/23/1)", bool(np.all(st == 1)), f"unique starts {np.unique(st)}")
    sf2, on2 = extend_stops(cyc["stop"], cyc["pto"], pto_dur, mode="max")
    check("T02", "option max(stop, PTO): standing = 23 s", bool(np.all(sf2[on2] == 23)), f"unique {np.unique(sf2[on2])}  [ASSUMP non-VECTO]")
run_test("T02", "PTO engine on VECTO Municipal", t02)
 
def t03():
    rows = []
    for name, cyc in CYCLES.items():
        r = run_chain(cyc); STORE[name] = r
        T, S, V, A, M = r["T"], r["S"], r["V"], r["A"], r["M"]
        sf = r["stop_final"]; n_stand_exp = int(np.sum(np.round(sf))) + (1 if (cyc["v"][0] == 0 and sf[0] == 0) else 0)
        segv = seg_target(cyc); k = np.searchsorted(cyc["s"], S, side="right") - 1
        over = V - (segv[k] + np.where(segv[k] > 50 / 3.6, 2.5 / 3.6, 0));
        acc_max = np.interp(V * 3.6, VACC[:, 0], VACC[:, 1]); dec_max = np.interp(V * 3.6, VACC[:, 0], VACC[:, 2])
        acc_viol = (A > acc_max + 1e-6) & (M != 3)
        dec_ratio = np.where(M == 4, A / dec_max, 0)
        sp, sa = split_energy(r)
        rows.append(dict(cycle=name, km=S[-1] / 1000, rows=len(T), h=T[-1] / 3600, stand_rows=int(np.sum(M == 0)), stand_exp=n_stand_exp,
                         v_over_max_kmh=over.max() * 3.6, acc_viol=int(acc_viol.sum()), brake_rows=int(np.sum(M == 4)),
                         brake_gt_1x=int(np.sum(dec_ratio > 1.0 + 1e-6)), brake_max_x=dec_ratio.max(), coast_rows=int(np.sum(M == 3)),
                         E_kWh=r["E_battery"], kWh_km=r["E_battery"] / (S[-1] / 1000), regen_kWh=-sp["regen"],
                         aux_kWh=sum(v for k2, v in sp.items() if k2 not in ("traction", "regen")), t_driver_s=r["t_drv"], t_cons_s=r["t_con"]))
        check("T03", f"{name}: reaches route end", cyc["s"][-1] - S[-1] < max(V[-1] + 1, 1.5), f"end gap {cyc['s'][-1]-S[-1]:.2f} m")
        check("T03", f"{name}: standing rows = stop times", int(np.sum(M == 0)) == n_stand_exp, f"{int(np.sum(M==0))} vs {n_stand_exp}")
        n_over = int(np.sum(over > 1e-6))
        check("T03", f"{name}: speed <= target (+2.5 km/h overspeed)",
              True if n_over == 0 else ("WARN" if over.max() * 3.6 < 1.01 else False),
              f"max over {over.max()*3.6:.3f} km/h on {n_over} rows" + (" (1 s row crosses waypoints a few m apart; see note)" if n_over else ""))
        check("T03", f"{name}: P_aux_row == sum of components", bool(np.allclose(r["P_aux_row"], sum(v for k2, v in sa.items() if k2 not in ("traction", "regen")))), "")
        check("T03", f"{name}: no traction power on stop rows (mode 0)", bool(np.all(r["P_trac"][M == 0] == 0)), "")
        cb = (M == 3) & (r["P_wheel"] < -1000)              # 'coast' rows where the wheels need braking (speed cap active)
        lost = -np.sum(np.minimum(r["P_wheel"], 0)[M == 3]) / 3.6e6
        check("T03", f"{name}: no braking hidden in coast rows (mode 3)", True if cb.sum() == 0 else "WARN",
              f"{int(cb.sum())} rows, {lost:.2f} kWh wheel braking energy not recuperated (VECTO brakes here: DefaultDriverStrategy.cs 1000-1006)")
    show(pd.DataFrame(rows), "T03_vecto_cycles")
run_test("T03", "all VECTO truck cycles, full chain (VECTO-equivalent weather)", t03)
 
def t04():
    r = STORE["MunicipalUtility"]; sp, sa = split_energy(r)
    check("T04", "stop PTO energy = 96 x 0.14993 kWh", abs(sp["PTO_stop"] - 96 * 0.14993) < 1e-3, f"{sp['PTO_stop']:.4f} kWh")
    V = r["V"]; pto_rows = sa["PTO_stop"] > 0
    check("T04", "Cond on during stop PTO", bool(np.all(sa["Cond"][pto_rows] > 0)), f"{int(pto_rows.sum())} PTO rows")
    check("T04", "SP off when standing", bool(np.all(sa["SP"][V == 0] == 0)), "")
    r2 = run_chain(CYCLES["MunicipalUtility"], stop_mode="max"); sp2, _ = split_energy(r2)
    check("T04", "option max(stop,PTO): same PTO energy, shorter day", abs(sp2["PTO_stop"] - sp["PTO_stop"]) < 1e-6 and r2["T"][-1] < r["T"][-1],
          f"day {r['T'][-1]:.0f} s -> {r2['T'][-1]:.0f} s")
    r3 = run_chain(CYCLES["MunicipalUtility"], pto_on=False); sp3, _ = split_energy(r3)
    check("T04", "PTO off: no PTO energy", sp3["PTO_stop"] == 0, f"E {r3['E_battery']:.3f} vs {r['E_battery']:.3f} kWh")
    r4 = run_chain(CYCLES["MunicipalUtility"], pto_profile=(np.array([]), np.array([])))
    check("T04", "empty PTO profile runs", True, f"E {r4['E_battery']:.3f} kWh")
    r5 = run_chain(CYCLES["MunicipalUtility"], PTO_always_on=2000.0)   # [ILLUS] 2 kW always-on PTO
    d = r5["E_battery"] - r["E_battery"]; exp = 2000 * len(r["T"]) / 3.6e6
    check("T04", "always-on PTO 2 kW adds 2 kW x day", abs(d - exp) < 1e-6, f"+{d:.4f} kWh (exp {exp:.4f})")
run_test("T04", "Municipal PTO cases", t04)
 
def t05():
    cyc = CYCLES["UrbanDelivery"]; rows = []
    sf, _ = extend_stops(cyc["stop"], cyc["pto"], 0); n_st = int(np.sum(sf[1:] > 0))
    cases = {"empty (0 kg)": ("constant", 0.0, None, None), "VECTO ref (constant)": ("constant", PAYLOAD_REF, None, None),
             "max allowed (constant)": ("constant", VEH["tpmlm"] - M_VEHICLE, None, None),
             "linear ref -> 0 (deliveries)": ("linear", PAYLOAD_REF, 0.0, None),
             "custom: drop half at stop 50": ("custom", None, None, np.r_[np.full(50, PAYLOAD_REF), np.full(n_st - 49, PAYLOAD_REF / 2)])}
    for lab, pm in cases.items():
        if pm[0] == "custom": pm = ("custom", PAYLOAD_REF, None, pm[3])
        r = run_chain(cyc, payload_mode=pm, coast=True); STORE[f"payload::{lab}"] = r
        sp, _ = split_energy(r)
        rows.append(dict(case=lab, payload_start=r["payload_wp"][0], payload_end=r["payload_wp"][~np.isnan(r["payload_wp"])][-1],
                         E_kWh=r["E_battery"], traction=sp["traction"], regen=sp["regen"], kWh_km=r["E_battery"] / 100))
    df = pd.DataFrame(rows); show(df, "T05_payload")
    e = df.E_kWh.values
    check("T05", "energy rises with constant payload (0 < ref < max)", e[0] < e[1] < e[2], f"{e[0]:.2f} < {e[1]:.2f} < {e[2]:.2f} kWh")
    check("T05", "linear ref->0 between empty and ref", e[0] < e[3] < e[1], f"{e[3]:.2f}")
    # beta = 0.9 rolling force equals VECTO's formula at any mass (VehicleData.cs 292-311)
    ms = np.array([M_VEHICLE, M_VEHICLE + PAYLOAD_REF, VEH["tpmlm"]])
    ours = CRR_EFF * G * ms ** BETA; vecto = np.array([crr_total_vecto(m) for m in ms]) * ms * G
    check("T05", "F_roll = Crr_eff*g*m^0.9 matches VECTO at 3 masses", bool(np.allclose(ours, vecto, rtol=1e-12)), f"{np.round(ours,2)} N")
run_test("T05", "payload variation (UrbanDelivery)", t05)
 
def t06():
    # energy identity: sum(k_lin*dt) = g*dh + (v_end^2 - v_0^2)/2 (driver + force engine consistency)
    for name in ["RegionalDelivery", "UrbanDelivery", "LongHaul"]:
        r = STORE[name]; cyc = r["cyc"]
        alt = np.concatenate(([0], np.cumsum(np.diff(cyc["s"]) * cyc["grad"][:-1] / 100)))
        s_end = r["S"][-1] + (r["V"][-1] + max(r["V"][-1] + r["A"][-1], 0)) / 2
        dh = np.interp(s_end, cyc["s"], alt) - np.interp(r["S"][0], cyc["s"], alt)
        v_end = max(r["V"][-1] + r["A"][-1], 0)
        lhs = np.sum(r["k_lin"]); rhs = G * dh + (v_end ** 2 - r["V"][0] ** 2) / 2
        pos = np.sum(np.abs(r["k_lin"]))
        check("T06", f"{name}: sum(k_lin) = g*dh + dKE/m", abs(lhs - rhs) / pos < 0.005, f"{lhs:.1f} vs {rhs:.1f} J/kg (err {abs(lhs-rhs)/pos*100:.3f} % of |k_lin|)")
run_test("T06", "energy identity driver + force engine", t06)
 
def t07():
    # regen rules and cap from the generic VECTO motor (.vemp drag column = max generating torque)
    r = STORE["UrbanDelivery"]; M, V, Pt, Pw = r["M"], r["V"], r["P_trac"], r["P_wheel"]
    check("T07", "coast rows draw 0 traction", bool(np.all(Pt[M == 3] == 0)), f"{int(np.sum(M==3))} coast rows")
    lo = (M == 4) & (V <= V_NO_REGEN)
    check("T07", "no regen when braking <= 5 km/h", bool(np.all(Pt[lo] == 0)), f"{int(lo.sum())} rows")
    n, Tq = EM_FLD[:, 0], np.abs(EM_FLD[:, 2])
    P_gen_mech = float(np.max(Tq * n * 2 * np.pi / 60) * VEH["em_count"])     # per motor x count, motor shaft
    rows = []
    for name in ["UrbanDelivery", "RegionalDelivery", "MunicipalUtility"]:
        a = STORE[name]; b = run_chain(CYCLES[name], P_regen_max=P_gen_mech)
        ra, rb = -np.sum(np.minimum(a["P_trac"], 0)) / 3.6e6, -np.sum(np.minimum(b["P_trac"], 0)) / 3.6e6
        rows.append(dict(cycle=name, regen_no_cap=ra, regen_capped=rb, overstated_pct=(ra / rb - 1) * 100 if rb > 0 else np.nan,
                         E_no_cap=a["E_battery"], E_capped=b["E_battery"], rows_at_cap=int(np.sum(b["P_trac"] <= -P_gen_mech + 1e-6))))
    show(pd.DataFrame(rows), "T07_regen_cap")
    check("T07", "regen cap from generic VECTO motor", "INFO", f"P_gen_max = {P_gen_mech/1000:.1f} kW (2 x {P_gen_mech/2000:.1f} kW at the shaft) [ASSUMP used as electric cap; battery limit ignored]")
run_test("T07", "regen rules + how much an uncapped regen overstates (generic VECTO motor)", t07)
 
def t08():
    rows = []
    cases = {"typed 50 km, 20 stops, 50 km/h, flat": typed_route(50, 20, 300, 50),
             "typed 80 km, 0 stops, 80 km/h, flat": typed_route(80, 0, 0, 80),
             "typed 30 km, 60 stops, 30 km/h, hills +-4 %": typed_route(30, 60, 120, 30, grade_amp=4.0),
             "typed 40 km, 10 stops, 80 km/h, hills +-6 %": typed_route(40, 10, 600, 80, grade_amp=6.0)}   # [ILLUS] all test routes
    for lab, cyc in cases.items():
        r = run_chain(cyc, payload_mode=("linear", PAYLOAD_REF, 0.0, None) if np.sum(cyc["stop"][1:] > 0) else ("constant", PAYLOAD_REF, None, None),
                      mission="RegionalDelivery"); STORE[f"typed::{lab}"] = r
        sp, _ = split_energy(r); n_st = int(np.sum(cyc["stop"][1:] > 0))
        rows.append(dict(case=lab, km=r["S"][-1] / 1000, stops=n_st, stand_s=int(np.sum(r["M"] == 0)), exp_stand_s=int(np.sum(cyc["stop"])),
                         h=r["T"][-1] / 3600, E_kWh=r["E_battery"], kWh_km=r["E_battery"] / (r["S"][-1] / 1000), regen=sp["regen"],
                         coast_rows=int(np.sum(r["M"] == 3)), v_max_kmh=r["V"].max() * 3.6))
        check("T08", f"{lab}: standing time = stops", int(np.sum(r["M"] == 0)) == int(np.sum(cyc["stop"])), "")
    show(pd.DataFrame(rows), "T08_typed_routes")
run_test("T08", "created waypoints (typed-route stand-in)", t08)
 
def t09():
    def expect_error(lab, fn):
        try:
            fn(); check("T09", lab, False, "no error raised")
        except Exception as e:
            check("T09", lab, True, f"{type(e).__name__}: {str(e)[:80]}")
    base = typed_route(5, 3, 60, 50)
    # back-to-back stops
    c = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in base.items()}
    i = int(np.where(c["stop"][1:] > 0)[0][0]) + 1; c["v"][i + 1] = 0; c["stop"][i + 1] = 30
    r = run_chain(c, mission="UrbanDelivery"); check("T09", "back-to-back stops reach the end", c["s"][-1] - r["S"][-1] < r["V"][-1] + 1.5, f"end gap {c['s'][-1]-r['S'][-1]:.2f} m, {int(np.sum(r['M']==0))} standing rows")
    # route starting at speed (no depot stop)
    c = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in base.items()}; c["v"][0] = 50; c["stop"][0] = 0
    r = run_chain(c, mission="UrbanDelivery"); check("T09", "route starting at 50 km/h", abs(r["V"][0] * 3.6 - 50) < 1e-9, f"first V {r['V'][0]*3.6:.1f} km/h")
    # steep downhill: overspeed limit holds, regen happens
    c = typed_route(5, 0, 0, 80); c["grad"][:] = -6.0
    r = run_chain(c, mission="RegionalDelivery"); over = r["V"].max() * 3.6 - 82.5
    check("T09", "-6 % downhill: speed <= 82.5 km/h", over < 1e-6, f"v max {r['V'].max()*3.6:.2f} km/h, regen {np.sum(np.minimum(r['P_trac'],0))/3.6e6:.3f} kWh")
    # all-zero speed route must raise
    c = typed_route(2, 0, 0, 50); c["v"][:] = 0
    expect_error("all-zero speed route raises", lambda: run_chain(c, mission="UrbanDelivery"))
    # PTO longer than stop WITHOUT stop extension must raise in consumption_engine
    def no_ext():
        cyc = CYCLES["MunicipalUtility"]; is_stop = cyc["stop"] > 0; is_stop[0] = False
        on = is_stop & (cyc["pto"] > 0)
        pto_1s, oc, sc = pto_engine(cyc["stop"], on[is_stop].astype(float), PTO_T, PTO_W)
        T, S, V, A, Gr, M = driver_model(cyc["s"], cyc["v"], cyc["stop"], cyc["grad"], VACC[:, 0], VACC[:, 1], VACC[:, 2], g=G)
        k = force_engine(G, CRR_EFF, V, A, 1.0, Gr, R_DYN, THETA_WHEELS); nh = int(T[-1] // 3600) + 2
        consumption_engine(T=T, S=S, V=V, M=M, dt=1.0, k_lin=k[0], k_roll=k[1], k_rot=k[2], L=k[3], v_avg=k[4], m_vehicle=M_VEHICLE,
                           wp_s=cyc["s"], payload_wp=payload_engine(cyc["stop"], "constant", PAYLOAD_REF), beta=BETA, t_start=0,
                           T_amb_h=np.full(nh, 20.0), W1=np.ones((nh, len(CDXA_V))), W2=np.zeros((nh, len(CDXA_V))), cdxa_v=CDXA_V,
                           CdxA0=VEH["CdxA0"], p_air=P_AIR, R_air=R_AIR, ES=1000, PS=0, HVAC=0, SP=0, cond=0, PTO_always_on=0,
                           pto_1s=pto_1s, pto_on_col=oc, pto_start_col=sc, motor_eff=MOTOR_EFF, inverter_eff=INVERTER_EFF,
                           gearbox_eff=GEARBOX_EFF, regen_effeiciency=REGEN_EFF, v_no_regen=V_NO_REGEN)
    expect_error("PTO longer than stop (no extension) raises", no_ext)
    # list inputs (as a parser might hand them over)
    def lists():
        r = STORE["MunicipalUtility"]; w = r["weather"]
        consumption_engine(T=r["T"], S=r["S"], V=r["V"], M=r["M"], dt=1.0, k_lin=r["k_lin"], k_roll=r["k_roll"], k_rot=r["k_rot"], L=r["L"],
                           v_avg=r["v_avg"], m_vehicle=M_VEHICLE, wp_s=list(r["cyc"]["s"]), payload_wp=list(r["payload_wp"]), beta=BETA,
                           t_start=0, T_amb_h=list(w["T_amb_h"]), W1=w["W1"], W2=w["W2"], cdxa_v=list(CDXA_V), CdxA0=VEH["CdxA0"],
                           p_air=P_AIR, R_air=R_AIR, ES=1000, PS=0, HVAC=0, SP=0, cond=0, PTO_always_on=0, pto_1s=list(r["pto_1s"]),
                           pto_on_col=list(r["pto_on_col"]), pto_start_col=list(r["pto_start_col"]), motor_eff=MOTOR_EFF,
                           inverter_eff=INVERTER_EFF, gearbox_eff=GEARBOX_EFF, regen_effeiciency=REGEN_EFF, v_no_regen=V_NO_REGEN)
    try:
        lists(); check("T09", "plain-list inputs accepted", True, "")
    except Exception as e:
        check("T09", "plain-list inputs accepted", False, f"{type(e).__name__}: {e}  -> add the np.asarray lines")
    # trip longer than the hourly weather arrays must fail loudly
    def short_weather():
        r = STORE["RegionalDelivery"]; w = dict(r["weather"]); w["T_amb_h"] = w["T_amb_h"][:1]
        consumption_engine(T=r["T"], S=r["S"], V=r["V"], M=r["M"], dt=1.0, k_lin=r["k_lin"], k_roll=r["k_roll"], k_rot=r["k_rot"], L=r["L"],
                           v_avg=r["v_avg"], m_vehicle=M_VEHICLE, wp_s=r["cyc"]["s"], payload_wp=r["payload_wp"], beta=BETA,
                           t_start=0, T_amb_h=w["T_amb_h"], W1=w["W1"][:1], W2=w["W2"][:1], cdxa_v=CDXA_V, CdxA0=VEH["CdxA0"],
                           p_air=P_AIR, R_air=R_AIR, ES=0, PS=0, HVAC=0, SP=0, cond=0, PTO_always_on=0, pto_1s=r["pto_1s"],
                           pto_on_col=r["pto_on_col"], pto_start_col=r["pto_start_col"], motor_eff=MOTOR_EFF,
                           inverter_eff=INVERTER_EFF, gearbox_eff=GEARBOX_EFF, regen_effeiciency=REGEN_EFF, v_no_regen=V_NO_REGEN)
    expect_error("trip longer than weather arrays raises", short_weather)
run_test("T09", "edge cases", t09)
 
def t10():
    rows = []
    for Tc in [-10.0, 0.0, T_VECTO_EQ, 30.0]:
        nh = 4; w = dict(T_amb_h=np.full(nh, Tc), W1=np.repeat(W1_DECL, nh, 0), W2=np.repeat(W2_DECL, nh, 0), t_start=0.0)
        r = run_chain(CYCLES["RegionalDelivery"], weather=w)
        rows.append(dict(T_amb_C=Tc, rho=P_AIR / (R_AIR * (Tc + 273.15)), E_kWh=r["E_battery"]))
    df = pd.DataFrame(rows); show(df, "T10_temperature")
    check("T10", "rho = 1.188 at the VECTO-equivalent temperature", abs(df.rho[2] - RHO_VECTO) < 1e-9, f"T = {T_VECTO_EQ:.2f} C")
    check("T10", "colder air -> more energy (same wind)", bool(np.all(np.diff(df.E_kWh.values) < 0)), f"{np.round(df.E_kWh.values,3)} kWh")
run_test("T10", "temperature -> air density -> energy", t10)
 
def t13():
    # VECTO's own result files for a 12 t rigid truck: VectoCoreTest/TestData/Integration/DeclarationMode/12t Truck (VECTO 2.2, 2015, diesel).
    # Wheel-side physics is the same for any powertrain, so the wheel energies (air, roll, grade, brake) can be compared.
    # Vehicle values below are READ BACK from that .vmod (not invented): Crr = P_roll/(m g cos v), CdxA_eff(v) = P_air/(rho L),
    # reduced wheel mass = P_wheel_inertia/(a v). m = 7750 kg + 4150 kg loading (.vsum row 'LongHaul FullLoading').
    D = "VectoCore/VectoCoreTest/TestData/Integration/DeclarationMode/12t Truck/"
    vm = pd.read_csv(io.BytesIO(_get(D + "12t Delivery Truck_LongHaulFullLoading.vmod")), encoding="utf-8-sig")
    sm = pd.read_csv(io.BytesIO(_get(D + "12t Delivery Truck.vsum")), encoding="utf-8-sig").iloc[1]
    m = float(sm["Mass [kg]"] + sm["Loading [kg]"])
    v = vm["v_act [km/h]"] / 3.6; a = vm["acc [m/s^2]"]; dt = vm["dt [s]"]; gr = np.arctan(vm["grad [%]"] / 100)
    mv = v > 1; v1 = v - a * dt / 2; v2 = v + a * dt / 2; Lv = (v1 + v2) * (v1 ** 2 + v2 ** 2) / 8
    Crr = float(np.median((vm["P_roll [kW]"] * 1000 / (m * G * np.cos(gr) * v))[mv]))
    mred = float(np.median((vm["P_wheel_inertia [kW]"] * 1000 / (a * v))[mv & (a.abs() > 0.05)]))
    cda = vm["P_air [kW]"] * 1000 / (RHO_VECTO * Lv); vk = vm["v_act [km/h]"]
    tv = np.array([x for x in np.arange(60, 86, 5.0) if np.any((vk - x).abs() < 0.5)])
    tc = np.array([np.median(cda[(vk - x).abs() < 0.5]) for x in tv])
    rdyn = 0.4069297; theta = mred * rdyn ** 2      # rdyn from 12t Delivery Truck.vveh (406.9297 mm)
    check("T13", "values read back from VECTO .vmod", "INFO", f"m {m:.0f} kg, Crr {Crr:.6f}, m_red_wheels {mred:.1f} kg, CdxA {dict(zip(tv, tc.round(3)))}")
    cyc = CYCLES["LongHaul"]
    T, S, V, A, Gr, M = driver_model(cyc["s"], cyc["v"], cyc["stop"], cyc["grad"], VACC[:, 0], VACC[:, 1], VACC[:, 2],
                                     coast_mass=m, m_red_wheels=mred, cdxa_v=tv, cdxa=tc, Crr=Crr, rho=RHO_VECTO, g=G)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(G, Crr, V, A, 1.0, Gr, rdyn, theta)
    air = RHO_VECTO * np.interp(np.clip(v_avg * 3.6, tv[0], tv[-1]), tv, tc) * L
    Pw = m * k_lin + m * k_roll + k_rot + air
    E = lambda p: float(np.sum(p) / 3.6e6)
    rows = [("time [s]", sm["time [s]"], T[-1] + 1), ("E_air [kWh]", sm["E_air [kWh]"], E(air)), ("E_roll [kWh]", sm["E_roll [kWh]"], E(m * k_roll)),
            ("E_grad [kWh]", sm["E_grad [kWh]"], E(m * G * np.sin(np.arctan(Gr / 100)) * v_avg)), ("E_brake [kWh]", sm["E_brake [kWh]"], -E(np.minimum(Pw, 0))),
            ("wheel positive [kWh]", sm["P_wheel_in_pos [kW]"] * sm["time [s]"] / 3600, E(np.maximum(Pw, 0)))]
    df = pd.DataFrame(rows, columns=["quantity", "VECTO_2.2", "HDEV"]); df["diff_pct"] = (df.HDEV / df["VECTO_2.2"] - 1) * 100
    show(df, "T13_vs_vecto22_12t_longhaul")
    d_air, d_roll, d_pos = df.diff_pct[1], df.diff_pct[2], df.diff_pct[5]
    check("T13", "rolling energy vs VECTO", abs(d_roll) < 1 or "WARN", f"{d_roll:+.2f} %")
    check("T13", "air energy vs VECTO", abs(d_air) < 3 or "WARN", f"{d_air:+.2f} %")
    check("T13", "positive wheel energy vs VECTO", abs(d_pos) < 5 or "WARN", f"{d_pos:+.2f} %  [ASSUMP] VECTO 2.2 (2015) driver + cycle version may differ from today's")
run_test("T13", "wheel energy vs VECTO's own 12 t truck result (LongHaul)", t13)
 
# -------------------------------------------------------------------------------------
# 6. WEATHER: DMI hourly temperature, wind, radiation for a full year + coverage report
# -------------------------------------------------------------------------------------
def _dmi_json(path, params):
    url = f"{DMI_BASE}/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read())
def _haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2); dp, dl = p2 - p1, math.radians(lon2 - lon1)
    return 2 * 6371 * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))
def _dmi_hourly(station, param, start, end):
    d = _dmi_json("stationValue/items", dict(stationId=station, parameterId=param, timeResolution="hour",
                                              datetime=f"{start}/{end}", limit=300000))
    f = d.get("features", [])
    if not f: return pd.Series(dtype=float)
    s = pd.Series({pd.Timestamp(x["properties"]["from"]): x["properties"]["value"] for x in f}, dtype=float)
    s.index = pd.DatetimeIndex(s.index).tz_convert("UTC")
    return s.sort_index()[~s.index.duplicated()]
 
def get_weather():
    idx = pd.date_range(f"{YEAR}-01-01", f"{YEAR+1}-01-02", freq="h", tz="Europe/Copenhagen", inclusive="left").tz_convert("UTC")
    if WEATHER_SOURCE == "synthetic":   # offline smoke test only, NOT real weather
        h = np.arange(len(idx)); doy = h / 24
        df = pd.DataFrame(dict(temp=8 - 8 * np.cos(2 * np.pi * (doy - 15) / 365) + 3 * np.sin(2 * np.pi * (h % 24 - 9) / 24),
                               wind=4 + 2 * np.sin(2 * np.pi * doy / 7) ** 2, radiation=np.clip(400 * np.sin(2 * np.pi * (h % 24 - 6) / 24), 0, None)), index=idx)
        return df, dict(temp="synthetic", wind="synthetic", radiation="synthetic")
    st = _dmi_json("station/items", dict(status="Active", bbox="7,54,16,58", limit=10000))["features"]
    stations = sorted([(_haversine(SITE_LAT, SITE_LON, f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0]),
                        f["properties"]["stationId"], f["properties"].get("name")) for f in st])
    start, end = f"{YEAR-1}-12-31T00:00:00Z", f"{YEAR+1}-01-02T00:00:00Z"
    seen, uniq = set(), []
    for dist, sid, nm in stations:                        # station list repeats ids (history entries) -> keep the first
        if sid not in seen:
            seen.add(sid); uniq.append((dist, sid, nm))
    chosen, data = {}, {}
    for key, param in [("temp", "mean_temp"), ("wind", "mean_wind_speed"), ("radiation", "mean_radiation")]:
        # each parameter from the nearest station that has a full year of it (stations may differ per parameter)
        for dist, sid, nm in uniq[:MAX_STATIONS]:
            try:
                ser = _dmi_hourly(sid, param, start, end)
            except Exception as e:
                print(f"  {param}: {nm} ({sid}) failed: {e}"); continue
            if len(ser):
                print(f"  {param}: {nm} ({sid}) {dist:.1f} km -> {len(ser)} h")
            if len(ser) >= MIN_HOURS_PER_YEAR:
                data[key] = ser; chosen[key] = f"{nm} ({sid}), {dist:.1f} km"; break
        if key not in data:
            data[key] = pd.Series(dtype=float); chosen[key] = f"none within {MAX_STATIONS} stations"
    if len(data["temp"]) == 0 or len(data["wind"]) == 0:
        raise RuntimeError(f"no full year of hourly temp and/or wind: {chosen}")
    df = pd.DataFrame({k: v.reindex(idx) for k, v in data.items()}, index=idx)   # missing hours stay NaN (no filling)
    return df, chosen
 
WX, WX_SRC = None, None
def t11():
    global WX, WX_SRC
    WX, WX_SRC = get_weather()
    check("T11", "weather source", "INFO", str(WX_SRC))
    loc = WX.index.tz_convert("Europe/Copenhagen")
    cov = WX.notna().groupby(loc.date).sum()
    hours = WX.groupby(loc.date).size()
    cov["hours_in_day"] = hours.values                       # 23 / 25 on DST days
    cov.index.name = "date"
    full = cov.copy()
    for c in ["temp", "wind", "radiation"]:
        full[c] = cov[c] == cov["hours_in_day"]
    cov = cov[cov.index < pd.Timestamp(f"{YEAR+1}-01-01").date()]; full = full.loc[cov.index]
    for c in ["temp", "wind", "radiation"]:
        n_full = int(full[c].sum()); miss = int((cov["hours_in_day"] - cov[c]).sum())
        check("T11", f"{c}: complete days", n_full == len(cov) or "WARN", f"{n_full}/{len(cov)} days complete, {miss} hours missing")
    rng = WX.describe().T[["count", "min", "mean", "max"]]
    print(rng.to_string())
    check("T11", "radiation range plausible for W/m2", "INFO", f"min {WX.radiation.min():.1f}, max {WX.radiation.max():.1f}  (used later by HVAC_thermal; not in consumption yet)")
    bad = cov[(cov.temp < cov.hours_in_day) | (cov.wind < cov.hours_in_day)]
    show(bad.reset_index(), "T11_incomplete_days_temp_wind", 30)
    STORE["coverage"] = cov
run_test("T11", "DMI weather year + coverage", t11)
 
_DW_CACHE = {}
def day_weather(date_str, hours=48):
    if (date_str, hours) in _DW_CACHE: return _DW_CACHE[(date_str, hours)]
    _DW_CACHE[(date_str, hours)] = _day_weather(date_str, hours); return _DW_CACHE[(date_str, hours)]
def _day_weather(date_str, hours=48):
    """[TEST] hourly arrays from local midnight of date_str; t_start = departure seconds after local midnight (elapsed, DST-safe)."""
    mid = pd.Timestamp(date_str, tz="Europe/Copenhagen"); dep = pd.Timestamp(f"{date_str} {DEPART_LOCAL}", tz="Europe/Copenhagen")
    i0 = WX.index.searchsorted(mid.tz_convert("UTC"))
    win = WX.iloc[i0:i0 + hours]
    if len(win) < hours or win[["temp", "wind"]].isna().any().any():
        return None
    W1, W2 = cdxa_table(win.wind.values, H_DMI, BETA_LIMIT_YEAR)
    return dict(T_amb_h=win.temp.values, W1=W1, W2=W2, t_start=(dep - mid).total_seconds(), wind_h=win.wind.values, rad_h=win.radiation.values, i0=i0)
 
def t12():
    cyc = CYCLES[YEAR_CYCLE]
    base = run_chain(cyc)                                  # driver + force once; reused for every day
    dates = pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31", freq="D").strftime("%Y-%m-%d")
    rows, skipped = [], []
    t0 = time.time()
    for d in dates:
        w = day_weather(d)
        if w is None: skipped.append(d); continue
        r = dict(base); r["weather"] = w
        P_wheel, P_trac, P_aux_row, P_battery, E = consumption_engine(
            T=base["T"], S=base["S"], V=base["V"], M=base["M"], dt=1.0, k_lin=base["k_lin"], k_roll=base["k_roll"], k_rot=base["k_rot"],
            L=base["L"], v_avg=base["v_avg"], m_vehicle=M_VEHICLE, wp_s=cyc["s"], payload_wp=base["payload_wp"], beta=BETA,
            t_start=w["t_start"], T_amb_h=w["T_amb_h"], W1=w["W1"], W2=w["W2"], cdxa_v=CDXA_V, CdxA0=VEH["CdxA0"], p_air=P_AIR, R_air=R_AIR,
            ES=base["aux"]["ES"], PS=base["aux"]["PS"], HVAC=base["aux"]["HVAC"], SP=base["aux"]["SP"], cond=base["aux"]["cond"], PTO_always_on=0.0,
            pto_1s=base["pto_1s"], pto_on_col=base["pto_on_col"], pto_start_col=base["pto_start_col"], motor_eff=MOTOR_EFF,
            inverter_eff=INVERTER_EFF, gearbox_eff=GEARBOX_EFF, regen_effeiciency=REGEN_EFF, v_no_regen=V_NO_REGEN)
        r.update(P_wheel=P_wheel, P_trac=P_trac, P_aux_row=P_aux_row, P_battery=P_battery, E_battery=E)
        sp, _ = split_energy(r)
        hrs = ((w["t_start"] + base["T"]) // 3600).astype(int)
        rows.append(dict(date=d, E_kWh=E, **{f"{k}_kWh": v for k, v in sp.items()},
                         T_trip_C=float(np.mean(w["T_amb_h"][hrs])), wind_trip_ms=float(np.mean(w["wind_h"][hrs])),
                         rho_trip=float(np.mean(P_AIR / (R_AIR * (w["T_amb_h"][hrs] + 273.15)))),
                         rad_trip_Wm2=float(np.nanmean(w["rad_h"][hrs])) if np.any(~np.isnan(w["rad_h"][hrs])) else np.nan))
    dt_all = time.time() - t0
    df = pd.DataFrame(rows); STORE["year"] = df
    show(df.describe().T.reset_index().rename(columns={"index": "column"}), "T12_year_stats", 30)
    show(df, "T12_year_daily", 15)
    check("T12", "days simulated", len(df) > 0, f"{len(df)} days, {len(skipped)} skipped for missing weather, {dt_all:.2f} s total "
          f"({dt_all/max(len(df),1)*1000:.1f} ms/day; driver ran once in {base['t_drv']:.2f} s)")
    if len(df) > 2:
        c_t = np.corrcoef(df.T_trip_C, df.traction_kWh)[0, 1]; c_w = np.corrcoef(df.wind_trip_ms, df.traction_kWh)[0, 1]
        check("T12", "traction vs temperature: negative correlation expected", c_t < 0 or "WARN", f"r = {c_t:.3f}")
        check("T12", "traction vs wind: positive correlation expected", c_w > 0 or "WARN", f"r = {c_w:.3f}")
        check("T12", "aux energy constant through the year (VECTO-mode aux, no weather on aux yet)",
              bool(np.allclose(df[["ES_kWh", "PS_kWh", "HVAC_kWh", "SP_kWh", "Cond_kWh"]].std().values, 0)), "only traction/regen vary with weather now")
run_test("T12", f"year run: {YEAR_CYCLE} on every day of {YEAR}", t12)
 
# -------------------------------------------------------------------------------------
# 7. GRAPHS
# -------------------------------------------------------------------------------------
def pick_day():
    if WX is None: return None, None
    for k in range(0, 60):
        for d in [pd.Timestamp(DAY) + pd.Timedelta(days=s * k) for s in (1, -1)]:
            w = day_weather(d.strftime("%Y-%m-%d"))
            if w is not None: return d.strftime("%Y-%m-%d"), w
    return None, None
 
def g01():
    cyc = CYCLES[DAY_CYCLE]; s = cyc["s"] / 1000
    alt = np.concatenate(([0], np.cumsum(np.diff(cyc["s"]) * cyc["grad"][:-1] / 100)))
    fig, ax = plt.subplots(3, 1, figsize=(11, 6.5), sharex=True, gridspec_kw=dict(height_ratios=[2, 1, 1]))
    ax[0].step(s, cyc["v"], where="post", color=PAL[0], label="target speed"); st = cyc["stop"] > 0
    ax[0].plot(s[st], np.zeros(st.sum()), "v", color=PAL[1], ms=6, label=f"stops ({int(st[1:].sum())})")
    ax[0].set_ylabel("km/h"); ax[0].set_title(f"{DAY_CYCLE}: waypoints (VECTO .vdri)"); ax[0].legend(loc="upper right")
    ax[1].plot(s, alt, color=PAL[2]); ax[1].set_ylabel("altitude [m]\n(VECTO rule)")
    ax[2].step(s, cyc["grad"], where="post", color=PAL[6]); ax[2].set_ylabel("grade [%]"); ax[2].set_xlabel("distance [km]")
    save(fig, "G01_waypoints")
 
DAYRUN = {}
def g02():
    d, w = pick_day()
    if w is None:
        print("  no complete weather day found; using VECTO-equivalent weather"); w = None
    r = run_chain(CYCLES[DAY_CYCLE], weather=w); DAYRUN.update(r=r, date=d)
    cyc, S, V, T, M = r["cyc"], r["S"], r["V"], r["T"], r["M"]
    fig, ax = plt.subplots(3, 1, figsize=(11, 7.5))
    ax[0].step(cyc["s"] / 1000, cyc["v"], where="post", color="#9a9893", lw=1, label="waypoint target")
    ax[0].plot(S / 1000, V * 3.6, color=PAL[0], label="driver model speed")
    ax[0].set_xlabel("distance [km]"); ax[0].set_ylabel("km/h"); ax[0].set_title(f"{DAY_CYCLE} after the driver model ({d or 'VECTO-eq weather'})"); ax[0].legend(loc="upper right")
    zoom = S < min(S[-1], 5000)
    ax[1].step(cyc["s"][cyc["s"] < 5000] / 1000, cyc["v"][cyc["s"] < 5000], where="post", color="#9a9893", lw=1, label="target")
    for m in range(5):
        sel = zoom & (M == m)
        ax[1].plot(S[sel] / 1000, V[sel] * 3.6, ".", ms=3, color=PAL[m], label=MODE_NAMES[m])
    ax[1].set_xlabel("distance [km] (first 5 km)"); ax[1].set_ylabel("km/h"); ax[1].legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=6, markerscale=3, fontsize=7)
    ax[2].plot(T / 60, r["A"], color=PAL[6], lw=0.8); ax[2].set_xlabel("time [min]"); ax[2].set_ylabel("acceleration [m/s2]")
    save(fig, "G02_driver_model")
    tab = pd.DataFrame(dict(t_s=T, s_m=S, v_kmh=V * 3.6, a=r["A"], grade=r["G"], mode=M, P_wheel_kW=r["P_wheel"] / 1000,
                            P_trac_kW=r["P_trac"] / 1000, P_aux_kW=r["P_aux_row"] / 1000, P_bat_kW=r["P_battery"] / 1000))
    tab.to_csv(os.path.join(OUT_DIR, "G02_day_rows_full.csv"), index=False)
    show(tab.iloc[::120], "G02_day_rows_every_120s", 40)
 
def g03():
    r = DAYRUN["r"]; sp, comp = split_energy(r); T = r["T"] / 60
    fig, ax = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    ax[0].plot(T, r["P_wheel"] / 1000, color="#9a9893", lw=0.8, label="wheel power")
    ax[0].plot(T, r["P_trac"] / 1000, color=PAL[0], lw=0.9, label="electric traction power")
    ax[0].set_ylabel("kW"); ax[0].legend(loc="upper right"); ax[0].set_title(f"{DAY_CYCLE} {DAYRUN['date'] or ''}: power per row")
    keys = ["ES", "PS", "HVAC", "SP", "Cond", "PTO_stop", "PTO_always"]
    ax[1].stackplot(T, *[comp[k] / 1000 for k in keys], labels=keys, colors=PAL[:7], lw=0)
    ax[1].set_ylabel("aux kW"); ax[1].legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=7, fontsize=7)
    ax[2].plot(T, np.cumsum(r["P_battery"]) / 3.6e6, color=PAL[0], label="net battery energy")
    ax[2].plot(T, np.cumsum(comp["traction"]) / 3.6e6, color=PAL[1], label="traction")
    ax[2].plot(T, -np.cumsum(comp["regen"]) / 3.6e6, color=PAL[2], label="regen recovered")
    ax[2].plot(T, np.cumsum(sum(comp[k] for k in keys)) / 3.6e6, color=PAL[3], label="aux")
    ax[2].set_ylabel("cumulative kWh"); ax[2].set_xlabel("time [min]"); ax[2].legend(loc="upper left")
    save(fig, "G03_power_rows")
    fig, ax = plt.subplots(figsize=(8, 3.6))
    labels = list(sp.keys()); vals = [sp[k] for k in labels]
    ax.barh(labels, vals, color=PAL[0], height=0.6); ax.axvline(0, color="#52514e", lw=0.8)
    for i, v in enumerate(vals):
        ax.text(v + (0.3 if v >= 0 else -0.3), i, f"{v:.2f}", va="center", ha="left" if v >= 0 else "right", color="#52514e", fontsize=8)
    ax.invert_yaxis(); ax.set_xlabel("kWh"); ax.set_title(f"Consumption split, net {r['E_battery']:.2f} kWh ({r['E_battery']/(r['S'][-1]/1000):.3f} kWh/km)")
    ax.grid(axis="y", visible=False); save(fig, "G04_consumption_split")
    show(pd.DataFrame(dict(component=labels, kWh=vals, share_of_gross_pct=np.array(vals) / sum(v for v in vals if v > 0) * 100)), "G04_split_table")
 
def g05():
    labs = [k for k in STORE if k.startswith("payload::")]
    fig, ax = plt.subplots(2, 1, figsize=(11, 6))
    for i, k in enumerate(labs):
        r = STORE[k]; pw = r["payload_wp"]; has = ~np.isnan(pw)
        m_row = M_VEHICLE + pw[has][np.searchsorted(r["cyc"]["s"][has], r["S"], side="right") - 1]
        ax[0].plot(r["S"] / 1000, m_row / 1000, color=PAL[i], label=k.split("::")[1])
    ax[0].set_ylabel("vehicle mass [t]"); ax[0].set_xlabel("distance [km]"); ax[0].legend(loc="upper right", ncol=2)
    ax[0].set_title("Payload variation (UrbanDelivery): mass per row")
    E = [STORE[k]["E_battery"] for k in labs]
    ax[1].barh([k.split("::")[1] for k in labs], E, color=PAL[0], height=0.6)
    for i, v in enumerate(E): ax[1].text(v, i, f" {v:.2f} kWh", va="center", fontsize=8, color="#52514e")
    ax[1].invert_yaxis(); ax[1].set_xlabel("net battery energy [kWh]"); ax[1].grid(axis="y", visible=False)
    save(fig, "G05_payload_variation")
 
def g06():
    df = STORE.get("year")
    if df is None or len(df) == 0: print("  no year data"); return
    x = pd.to_datetime(df.date)
    fig, ax = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
    ax[0].plot(x, df.E_kWh, color=PAL[0], label="net battery"); ax[0].set_ylabel("kWh / trip"); ax[0].legend(loc="upper right")
    ax[0].set_title(f"{YEAR_CYCLE} through {YEAR} (same driver trace every day, departure {DEPART_LOCAL})")
    ax[1].plot(x, df.traction_kWh, color=PAL[1], label="traction"); ax[1].plot(x, -df.regen_kWh, color=PAL[2], label="regen recovered")
    ax[1].set_ylabel("kWh / trip"); ax[1].legend(loc="upper right")
    for i, k in enumerate(["ES", "PS", "HVAC", "SP", "Cond"]):
        ax[2].plot(x, df[f"{k}_kWh"], color=PAL[3 + i if 3 + i < 8 else i], label=k)
    ax[2].set_ylabel("aux kWh / trip"); ax[2].legend(loc="upper right", ncol=5)
    ax[3].plot(x, df.T_trip_C, color=PAL[7]); ax[3].set_ylabel("trip mean temp [C]")
    save(fig, "G06_year_components")
    # wind and consumption: stacked panels on one time axis (no second y-axis)
    fig, ax = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
    ax[0].plot(x, df.wind_trip_ms, color=PAL[6]); ax[0].set_ylabel("trip mean wind\n[m/s, 10 m]")
    ax[0].set_title("Wind vs traction energy, same days")
    ax[1].plot(x, df.traction_kWh, color=PAL[1]); ax[1].set_ylabel("traction kWh")
    ax[2].plot(x, df.rho_trip, color=PAL[2]); ax[2].set_ylabel("air density\n[kg/m3]")
    save(fig, "G07_wind_vs_consumption")
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6))
    ax[0].plot(df.wind_trip_ms, df.traction_kWh, "o", ms=3, color=PAL[0]); ax[0].set_xlabel("trip mean wind [m/s]"); ax[0].set_ylabel("traction kWh")
    ax[1].plot(df.T_trip_C, df.traction_kWh, "o", ms=3, color=PAL[0]); ax[1].set_xlabel("trip mean temp [C]")
    ax[2].plot(df.rad_trip_Wm2, df.E_kWh, "o", ms=3, color=PAL[0]); ax[2].set_xlabel("trip mean radiation [W/m2] (not used yet)"); ax[2].set_ylabel("net kWh")
    save(fig, "G08_scatter_weather")
    cov = STORE.get("coverage")
    if cov is not None:
        fig, ax = plt.subplots(figsize=(11, 2.8))
        xx = pd.to_datetime(cov.index)
        for i, c in enumerate(["temp", "wind", "radiation"]):
            ax.plot(xx, cov[c], color=PAL[i], label=c, lw=1)
        ax.plot(xx, cov.hours_in_day, color="#9a9893", lw=0.8, ls="--", label="hours in day")
        ax.set_ylabel("hours with data"); ax.set_title(f"DMI data coverage per day ({WX_SRC})", fontsize=8); ax.legend(loc="lower left", ncol=4)
        save(fig, "G09_weather_coverage")
    if DAYRUN.get("r") is not None and DAYRUN["r"]["weather"].get("wind_h") is not None:
        r = DAYRUN["r"]; w = r["weather"]; hrs = ((w["t_start"] + r["T"]) // 3600).astype(int)
        fig, ax = plt.subplots(3, 1, figsize=(11, 6.5), sharex=True)
        ax[0].step(np.arange(48), w["wind_h"], where="post", color=PAL[6]); ax[0].axvspan(hrs[0], hrs[-1] + 1, color="#eeede9", zorder=0)
        ax[0].set_ylabel("wind [m/s]"); ax[0].set_title(f"{DAY_CYCLE} on {DAYRUN['date']}: hourly weather (shaded = trip hours)")
        ax[1].step(np.arange(48), w["T_amb_h"], where="post", color=PAL[7]); ax[1].set_ylabel("temp [C]")
        ax[2].plot((w["t_start"] + r["T"]) / 3600, r["P_battery"] / 1000, color=PAL[0], lw=0.7); ax[2].set_ylabel("battery kW"); ax[2].set_xlabel("hour of day (from local midnight)")
        save(fig, "G10_day_weather_and_power")
 
for gid, fn in [("G01", g01), ("G02", g02), ("G03", g03), ("G05", g05), ("G06", g06)]:
    run_test(gid, "graphs", fn)
 
 
# -------------------------------------------------------------------------------------
# 7b. HVAC THERMAL  (TEST-ONLY reference of the missing pieces, so the effect can be measured now)
#     ref_climate_lookup + ref_HVAC_thermal follow VECTO's bus SSM (SSMCalculate.cs). They are NOT your production
#     functions: write your own climate_lookup / HVAC_thermal and compare with these (same inputs -> same W).
#     If your notebook already defines ssm_total_w, the harness uses YOURS for section 1.
# -------------------------------------------------------------------------------------
CAB = dict(   # truck cab inputs. VECTO has NO lorry cab model -> every value is borrowed or a placeholder (see tags)
    A_surface=20.0,        # [PLACEHOLDER] cab outer surface m2 - 19 Oct illustrative test value, NOT sourced -> needed from you
    A_window=4.0,          # [PLACEHOLDER] glass area m2 - 19 Oct illustrative test value, NOT sourced -> needed from you
    U=3.0,                 # [VECTO bus] W/m2K, high-floor bus (DeclarationData.cs 553-563); bus->truck is an ASSUMPTION
    volume=6.5,            # [SOURCE, ASSUMP] m3, Scania 'topline' (sleeper) cab air volume, LiU MSc thesis 1999 p.17; a day cab is smaller
    N_persons=1,           # driver only [ASSUMP]
    max_heat=5000.0,       # [VECTO bus] W, driver-compartment max heating, HVACHeatingPowerDriver.csv config 2 (5 kW); ASSUMP for a truck cab
    max_cool=5000.0,       # [VECTO bus] W, driver-compartment max cooling, HVACCoolingPowerDriver.csv config 2 (5 kW); ASSUMP
    vent_rate_h=7.0, vent_rate_heat_h=7.0,   # [VECTO bus] 1/h LowVentilation for driver-only configs 1/2 (DeclarationData.cs 451-460, Constants.cs)
    spec_vent_Wh_m3=0.56,  # [VECTO bus] Constants.cs SpecificVentilationPower
    T_heat=18.0, T_cool=23.0, T_cool_off=17.0,  # [VECTO bus] Constants.cs Heating/CoolingBoundaryTemperature; SSMInputs.cs line 77
    heat_per_person=(50.0, 80.0), clouding=(0.65, 0.8), T_boundary=17.0, g_glass=0.95, solar_factor=0.25,  # [VECTO bus] SSM constants
    eh_eff=0.93,           # [VECTO bus] electric heater efficiency, DefaultClimatic.aenv
)
HVAC_MODES = {             # heating distribution case + heat pump type (VECTO bus HeatingDistribution.csv names)
    "VECTO constant": None,
    "thermal: electric heater only (HD9)": dict(hd="HD9", hp=None, cool="non R-744 2-stage"),   # cooling tech [ASSUMP] (HD9 has no heat pump)
    "thermal: R-744 heat pump (HD1)": dict(hd="HD1", hp="R-744", cool="R-744"),
}
HVAC_CYCLES = ["RegionalDelivery", "UrbanDelivery", "MunicipalUtility"]   # v1.6: Regional added (VECTO-compared cycle)
OEKO = dict(kwh_km=0.96, dT=-0.013, dm=0.018)           # Oeko-Institut 2024 real-world eActros (19 t GVW): 0.96 kWh/km mean at 11-18 t
                                                         # and 19-21 C (Sec 4.1.1); -0.013 kWh/km per C, +0.018 kWh/km per t (Table 2)
 
def _num(x):
    x = x.strip()
    return 0.0 if x in ("", "-") else float(x)
def load_climate_tables():
    txt = _get(DECL + "Buses/DefaultClimatic.aenv").decode("utf-8-sig")
    lines = [l for l in txt.splitlines() if l.strip()]
    hdr = [h.strip() for h in lines[0].split(",")]
    env = pd.DataFrame([[c.strip() for c in l.split(",")] for l in lines[1:]], columns=hdr)
    txt = _get(DECL + "Buses/HeatingDistribution.csv").decode("utf-8-sig")
    rows = [[c.strip() for c in l.split(",")] for l in txt.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("Heating")]
    hdr2 = [h.strip() for h in txt.splitlines()[0].split(",")]
    hd = pd.DataFrame(rows, columns=hdr2)
    return env, hd
CLIM_ENV, CLIM_HD = load_climate_tables()
 
def climate_points(mode):
    """[TEST] parser part: pick the VECTO columns for one heat-pump type + HD case -> small point arrays"""
    env = CLIM_ENV; h = env["heating/cooling"] == "h"; c = env["heating/cooling"] == "c"
    Th = env.loc[h, "EnvTemp"].astype(float).values; Tc = env.loc[c, "EnvTemp"].astype(float).values
    cop_h = env.loc[h, mode["hp"]].map(_num).values if mode["hp"] else np.zeros(h.sum())
    cop_c = env.loc[c, mode["cool"]].map(_num).values
    d = CLIM_HD[CLIM_HD["HeatingDistributionCase"] == mode["hd"]].set_index("Environmental ID").loc[env.loc[h, "ID"].values]
    hp_col = mode["hp"] or "R-744"
    hp_s = d[hp_col].map(_num).values / 100 if mode["hp"] else np.zeros(h.sum())
    eh_s = d["electric heater"].map(_num).values / 100; fu_s = d["fuel heater"].map(_num).values / 100
    uT, ui = np.unique(Th, return_index=True); uC, uc = np.unique(Tc, return_index=True)   # 8/8 and 14/14 differ only in solar (same COP/shares)
    return dict(T_heat=uT, cop_heat=cop_h[ui], T_cool=uC, cop_cool=cop_c[uc], hp=hp_s[ui], eh=eh_s[ui], fuel=fu_s[ui])
 
def ref_climate_lookup(T_amb, pts):
    """[TEST reference] COP by linear interpolation inside heating / cooling points (ends held) [ASSUMP, agreed 15 Oct];
    shares from the nearest heating point, tie -> colder point [ASSUMP suggestion 19 Oct]"""
    T = np.asarray(T_amb, float)
    cop_h = np.interp(T, pts["T_heat"], pts["cop_heat"]); cop_c = np.interp(T, pts["T_cool"], pts["cop_cool"])
    k = np.argmin(np.abs(T[:, None] - pts["T_heat"][None, :]), axis=1)
    return cop_h, cop_c, pts["hp"][k], pts["eh"][k], pts["fuel"][k]
 
def _ssm(T, solar, T_calc, cab):
    if "ssm_total_w" in globals():   # YOUR function (signature from the 19 Oct close-out)
        return np.asarray(ssm_total_w(T, solar, T_calc, cab["A_surface"], cab["U"], cab["N_persons"], cab["A_window"],
                                      cab["heat_per_person"], cab["clouding"], cab["T_boundary"], cab["g_glass"], cab["solar_factor"]), float)
    q_wall = (T - T_calc) * cab["A_surface"] * cab["U"]                                     # SSMRun.cs 48-64
    hot = T >= cab["T_boundary"]
    q_p = cab["N_persons"] * np.where(hot, cab["heat_per_person"][1], cab["heat_per_person"][0])
    q_s = solar * cab["A_window"] * cab["g_glass"] * np.where(hot, cab["clouding"][1], cab["clouding"][0]) * cab["solar_factor"]
    return q_wall + q_p + q_s
 
def ref_HVAC_thermal(T_amb, solar, cab, mode):
    """[TEST reference] electric HVAC W per weather hour, VECTO SSMCalculate.cs; driver share = 1 (truck cab) [ASSUMP]"""
    T = np.asarray(T_amb, float); sol = np.nan_to_num(np.asarray(solar, float))   # missing radiation hour -> 0 [ASSUMP]
    pts = climate_points(mode)
    cop_h, cop_c, hp_s, eh_s, fu_s = ref_climate_lookup(T, pts)
    run1 = _ssm(T, sol, cab["T_heat"], cab); run2 = _ssm(T, sol, cab["T_cool"], cab)
    # 1. heating demand (lines 744-773): both runs losing heat -> smaller loss; BEV waste heat 0
    heating = (run1 < 0) & (run2 < 0)
    demand = np.where(heating, np.abs(np.maximum(run1, run2)), 0.0)
    # 2. split + cap (lines 215-242): cap only on heat pump + electric heater
    hp, eh = demand * hp_s, demand * eh_s
    capped = np.minimum(cab["max_heat"], hp + eh)
    f = np.where(np.isclose(1 - fu_s, 0), capped, capped / np.where(np.isclose(1 - fu_s, 0), 1, 1 - fu_s))
    hp_ltd, eh_ltd = f * hp_s, f * eh_s
    # 3. heating electric power (lines 191-207)
    HP_el = np.where(hp_s > 0, hp_ltd / np.where(cop_h > 0, cop_h, np.nan), 0.0)
    if np.any(np.isnan(HP_el)):
        raise ValueError("heat pump share > 0 where VECTO has no COP (non-R-744 at -20 C): user must give a COP")
    EH_el = eh_ltd / cab["eh_eff"]
    fuel_heat = demand * fu_s                                    # returned separately (diesel, not battery)
    # 4. cooling (lines 337-374, 553-570): only T >= 17 C and both runs gaining heat
    cool_on = (T >= cab["T_cool_off"]) & (run1 > 0) & (run2 > 0)
    cool = np.where(cool_on, np.minimum(run1, run2), 0.0)
    COOL_el = np.minimum(cool, cab["max_cool"]) / cop_c
    # 5. ventilation fan (lines 272-296, 376-427): V * rate * 0.56 Wh/m3
    v_heat = cab["volume"] * cab["vent_rate_heat_h"] * cab["spec_vent_Wh_m3"]
    v_norm = cab["volume"] * cab["vent_rate_h"] * cab["spec_vent_Wh_m3"]
    inactive = ((T < cab["T_cool_off"]) & (run1 > 0) & (run2 > 0)) | ((run1 > 0) & (run2 < 0))
    VENT_el = np.where(heating, v_heat, 0.0) + np.where(cool_on | inactive, v_norm, 0.0)
    # 6. total electric
    total = HP_el + EH_el + COOL_el + VENT_el
    return dict(total=total, HP_el=HP_el, EH_el=EH_el, COOL_el=COOL_el, VENT_el=VENT_el, demand=demand, fuel_heat=fuel_heat,
                run1=run1, run2=run2, cop_h=cop_h, cop_c=cop_c)
 
HV = {}
def t14():
    if WX is None: raise RuntimeError("needs the weather year (T11)")
    # spot checks against the 19 Oct hand values (same made-up cab: A 20, U 3, 1 person, window 4)
    chk = ref_HVAC_thermal(np.array([-5.0, 17.0, 30.0]), np.array([0.0, 300.0, 800.0]), CAB, HVAC_MODES["thermal: electric heater only (HD9)"])
    check("T14", "heating demand at -5 C / 0 W/m2 = 1330 W (19 Oct hand value)", abs(chk["demand"][0] - 1330) < 1e-6, f"{chk['demand'][0]:.1f} W")
    check("T14", "source of section 1", "INFO", "YOUR ssm_total_w" if "ssm_total_w" in globals() else "harness reference (ssm_total_w not defined)")
    yr = {}
    for name, mode in HVAC_MODES.items():
        if mode is None: continue
        yr[name] = ref_HVAC_thermal(WX.temp.values, WX.radiation.values, CAB, mode)
    HV["year"] = yr
    rows = []
    for name, h in yr.items():
        for lo, hi in [(-10, -5), (-5, 0), (0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 35)]:
            sel = (WX.temp.values >= lo) & (WX.temp.values < hi)
            if sel.any():
                rows.append(dict(mode=name, T_band=f"{lo}..{hi} C", hours=int(sel.sum()), HVAC_el_W=h["total"][sel].mean(),
                                 heat_el_W=(h["HP_el"] + h["EH_el"])[sel].mean(), cool_el_W=h["COOL_el"][sel].mean(), vent_W=h["VENT_el"][sel].mean()))
    show(pd.DataFrame(rows), "T14_hvac_by_temperature", 20)
    vc = {c: aux_values(c)["HVAC"] for c in HVAC_CYCLES}
    check("T14", "VECTO constant HVAC used in all earlier runs (electric W)", "INFO", str({k: round(v, 1) for k, v in vc.items()}) + " = HVAC-Table.csv Default x 1.25")
run_test("T14", "HVAC thermal (reference) on the 2025 weather year", t14)
 
def hvac_for_day(d, mode_name):
    w = day_weather(d)
    if w is None: return None, None
    if HVAC_MODES[mode_name] is None: return w, None
    h = HV["year"][mode_name]["total"][w["i0"]:w["i0"] + len(w["T_amb_h"])]
    return w, h
 
def t15():
    d, _ = pick_day()
    rows = []
    for cname in HVAC_CYCLES:
        for mname in HVAC_MODES:
            w, h = hvac_for_day(d, mname)
            r = run_chain(CYCLES[cname], weather=w, hvac_W=h); HV[(cname, mname)] = r
            sp, _ = split_energy(r); km = r["S"][-1] / 1000
            rows.append(dict(cycle=cname, date=d, hvac=mname, km=km, h=r["T"][-1] / 3600, E_kWh=r["E_battery"], kWh_km=r["E_battery"] / km,
                             HVAC_kWh=sp["HVAC"], traction=sp["traction"], regen=sp["regen"], PTO=sp["PTO_stop"],
                             other_aux=sp["ES"] + sp["PS"] + sp["SP"] + sp["Cond"], T_trip=float(np.mean(w["T_amb_h"][((w["t_start"] + r["T"]) // 3600).astype(int)]))))
    df = pd.DataFrame(rows); show(df, "T15_day_hvac_compare")
    for cname in HVAC_CYCLES:
        sub = df[df.cycle == cname]; base = sub.E_kWh.iloc[0]
        for _, x in sub.iloc[1:].iterrows():
            check("T15", f"{cname} {d}: {x.hvac} vs VECTO constant", "INFO", f"{x.E_kWh:.2f} vs {base:.2f} kWh ({(x.E_kWh/base-1)*100:+.1f} %), HVAC {x.HVAC_kWh:.2f} kWh")
run_test("T15", "one cold day, all HVAC cycles: VECTO constant vs HVAC thermal", t15)
 
def year_run(cname, mname):
    cyc = CYCLES[cname]; base = run_chain(cyc)
    dates = pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31", freq="D").strftime("%Y-%m-%d"); out = []
    for d in dates:
        w, h = hvac_for_day(d, mname)
        if w is None: continue
        hv = base["aux"]["HVAC"] if h is None else h
        res = consumption_engine(T=base["T"], S=base["S"], V=base["V"], M=base["M"], dt=1.0, k_lin=base["k_lin"], k_roll=base["k_roll"],
            k_rot=base["k_rot"], L=base["L"], v_avg=base["v_avg"], m_vehicle=M_VEHICLE, wp_s=cyc["s"], payload_wp=base["payload_wp"], beta=BETA,
            t_start=w["t_start"], T_amb_h=w["T_amb_h"], W1=w["W1"], W2=w["W2"], cdxa_v=CDXA_V, CdxA0=VEH["CdxA0"], p_air=P_AIR, R_air=R_AIR,
            ES=base["aux"]["ES"], PS=base["aux"]["PS"], HVAC=hv, SP=base["aux"]["SP"], cond=base["aux"]["cond"], PTO_always_on=0.0,
            pto_1s=base["pto_1s"], pto_on_col=base["pto_on_col"], pto_start_col=base["pto_start_col"], motor_eff=MOTOR_EFF,
            inverter_eff=INVERTER_EFF, gearbox_eff=GEARBOX_EFF, regen_effeiciency=REGEN_EFF, v_no_regen=V_NO_REGEN)
        hrs = ((w["t_start"] + base["T"]) // 3600).astype(int); km = base["S"][-1] / 1000
        hv_row = hv[hrs] if np.ndim(hv) else np.full(len(hrs), hv)
        out.append(dict(date=d, cycle=cname, hvac=mname, E_kWh=res[4], kWh_km=res[4] / km, HVAC_kWh=float(np.sum(hv_row) / 3.6e6),
                        traction_kWh=float(np.sum(np.maximum(res[1], 0)) / 3.6e6), T_trip=float(np.mean(w["T_amb_h"][hrs])),
                        wind_trip=float(np.mean(w["wind_h"][hrs]))))
    return pd.DataFrame(out)
 
def t16():
    frames = [year_run(c, m) for c in HVAC_CYCLES for m in HVAC_MODES]
    df = pd.concat(frames, ignore_index=True); HV["yeardf"] = df
    rows = []
    for (c, m), g in df.groupby(["cycle", "hvac"], sort=False):
        slope_T = np.polyfit(g.T_trip, g.kWh_km, 1)[0]
        mild = g[(g.T_trip >= 19) & (g.T_trip <= 21)]; cold = g[g.T_trip < 0]
        rows.append(dict(cycle=c, hvac=m, mean_kWh_km=g.kWh_km.mean(), p95_kWh_km=g.kWh_km.quantile(0.95), max_kWh_km=g.kWh_km.max(),
                         cold_days_kWh_km=cold.kWh_km.mean() if len(cold) else np.nan, mild_19_21C_kWh_km=mild.kWh_km.mean() if len(mild) else np.nan,
                         n_mild=len(mild), slope_per_C=slope_T, oeko_slope_per_C=OEKO["dT"], HVAC_kWh_year_mean=g.HVAC_kWh.mean()))
    t = pd.DataFrame(rows); show(t, "T16_year_hvac_summary"); HV["summary"] = t
    for _, x in t.iterrows():
        check("T16", f"{x.cycle} / {x.hvac}: temperature slope vs measured", "INFO",
              f"{x.slope_per_C:+.4f} kWh/km per C (Oeko-Institut measured {OEKO['dT']:+.3f}); mean {x.mean_kWh_km:.3f}, 95th pct {x.p95_kWh_km:.3f} kWh/km")
    # payload slope for the measured comparison (kWh/km per tonne)
    prow = []
    for c in ["UrbanDelivery", "RegionalDelivery"]:
        e = [run_chain(CYCLES[c], payload_mode=("constant", p, None, None))["E_battery"] for p in (0.0, PAYLOAD_REF, VEH["tpmlm"] - M_VEHICLE)]
        km = CYCLES[c]["s"][-1] / 1000; m_t = np.array([0.0, PAYLOAD_REF, VEH["tpmlm"] - M_VEHICLE]) / 1000
        prow.append(dict(cycle=c, slope_kWh_km_per_t=np.polyfit(m_t, np.array(e) / km, 1)[0], oeko_slope=OEKO["dm"],
                         kWh_km_empty=e[0] / km, kWh_km_ref=e[1] / km, kWh_km_max=e[2] / km))
    HV["payload"] = pd.DataFrame(prow); show(HV["payload"], "T16_payload_slope")
run_test("T16", "year: VECTO constant vs HVAC thermal, slopes vs Oeko-Institut measured eActros", t16)
 
def g11():
    yr = HV.get("year"); df = HV.get("yeardf")
    if yr is None or df is None: return
    T = WX.temp.values
    fig, ax = plt.subplots(1, 2, figsize=(12, 3.8))
    for i, (m, h) in enumerate(yr.items()):
        ax[0].plot(T, h["total"] / 1000, ".", ms=1.5, color=PAL[i + 1], label=m)
    for i, c in enumerate(HVAC_CYCLES):
        ax[0].axhline(aux_values(c)["HVAC"] / 1000, color=PAL[0] if i == 0 else "#52514e", lw=1, ls="--", label=f"VECTO constant ({c})")
    ax[0].set_xlabel("outside temperature [C] (hourly 2025)"); ax[0].set_ylabel("HVAC electric power [kW]"); ax[0].legend(loc="upper right", fontsize=7, markerscale=6)
    ax[0].set_title("HVAC power vs temperature", fontsize=9)
    loc = WX.index.tz_convert("Europe/Copenhagen")
    for i, (m, h) in enumerate(yr.items()):
        ax[1].plot(pd.Series(h["total"], index=loc).resample("D").mean().index, pd.Series(h["total"], index=loc).resample("D").mean() / 1000, color=PAL[i + 1], label=m)
    ax[1].set_ylabel("daily mean HVAC [kW]"); ax[1].legend(loc="upper center", fontsize=7); ax[1].set_title("HVAC power through the year", fontsize=9)
    save(fig, "G11_hvac_thermal")
    for c in HVAC_CYCLES:
        sub = df[df.cycle == c]
        fig, ax = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
        for i, m in enumerate(HVAC_MODES):
            g = sub[sub.hvac == m]; x = pd.to_datetime(g.date)
            ax[0].plot(x, g.kWh_km, color=PAL[i], lw=1, label=m)
            ax[1].plot(x, g.HVAC_kWh, color=PAL[i], lw=1, label=m)
        ax[0].set_ylabel("kWh/km"); ax[0].legend(loc="upper center", ncol=3, fontsize=7); ax[0].set_title(f"{c}: every day of {YEAR}")
        ax[1].set_ylabel("HVAC kWh / trip")
        save(fig, f"G12_year_hvac_{c}")
 
def g13():
    df = HV.get("yeardf"); pl = HV.get("payload")
    if df is None: return
    for c in HVAC_CYCLES:
        sub = df[df.cycle == c]
        fig, ax = plt.subplots(1, 3, figsize=(13, 3.9))
        for i, m in enumerate(HVAC_MODES):
            g = sub[sub.hvac == m]
            ax[0].plot(g.T_trip, g.kWh_km, "o", ms=2.5, color=PAL[i], label=m)
            ax[1].plot(g.wind_trip, g.kWh_km, "o", ms=2.5, color=PAL[i], label=m)
        g = sub[sub.hvac == list(HVAC_MODES)[1]]; y20 = np.polyval(np.polyfit(g.T_trip, g.kWh_km, 1), 20)
        tt = np.array([g.T_trip.min(), g.T_trip.max()])
        ax[0].plot(tt, y20 + OEKO["dT"] * (tt - 20), "--", color="#52514e", lw=1.2, label="measured slope (Oeko-Institut),\nshifted to our 20 C value")
        ax[0].set_xlabel("trip mean temperature [C]"); ax[0].set_ylabel("kWh/km"); ax[0].legend(fontsize=6.5, markerscale=2); ax[0].set_title(f"{c}: temperature", fontsize=9)
        ax[1].set_xlabel("trip mean wind [m/s, 10 m]"); ax[1].set_title("wind (VECTO all-direction method)", fontsize=9)
        if pl is not None:
            for i, (_, p) in enumerate(pl.iterrows()):
                m_t = np.array([0.0, PAYLOAD_REF, VEH["tpmlm"] - M_VEHICLE]) / 1000
                ax[2].plot(m_t, [p.kWh_km_empty, p.kWh_km_ref, p.kWh_km_max], "o-", color=PAL[i + 3], label=f"{p.cycle} (VECTO-eq weather)")
                ax[2].plot(m_t, p.kWh_km_empty + OEKO["dm"] * m_t, "--", color=PAL[i + 3], lw=1, alpha=0.7, label=f"measured slope from {p.cycle} empty")
            ax[2].set_xlabel("payload [t]"); ax[2].legend(fontsize=6.5); ax[2].set_title("payload", fontsize=9)
        save(fig, f"G13_sensitivity_{c}")
 
def g14():
    rows = []
    for c in HVAC_CYCLES:
        for m in HVAC_MODES:
            r = HV.get((c, m))
            if r is None: continue
            sp, _ = split_energy(r); sp["cycle"] = c; sp["hvac"] = m; rows.append(sp)
    if not rows: return
    df = pd.DataFrame(rows)
    keys = ["traction", "regen", "ES", "PS", "HVAC", "SP", "Cond", "PTO_stop"]
    fig, ax = plt.subplots(1, len(HVAC_CYCLES), figsize=(5 * len(HVAC_CYCLES), 3.6))
    for j, c in enumerate(HVAC_CYCLES):
        sub = df[df.cycle == c].set_index("hvac")[keys]
        x = np.arange(len(keys)); wdt = 0.8 / len(sub)
        for i, (m, vals) in enumerate(sub.iterrows()):
            ax[j].bar(x + i * wdt, vals.values, width=wdt * 0.9, color=PAL[i], label=m)
        ax[j].set_xticks(x + wdt * (len(sub) - 1) / 2); ax[j].set_xticklabels(keys, rotation=30, fontsize=8)
        ax[j].axhline(0, color="#52514e", lw=0.8); ax[j].set_ylabel("kWh"); ax[j].set_title(f"{c} {DAYRUN.get('date') or ''}", fontsize=9)
        ax[j].legend(fontsize=7)
    save(fig, "G14_day_split_hvac")
 
for gid, fn in [("G11", g11), ("G13", g13), ("G14", g14)]:
    run_test(gid, "HVAC graphs", fn)
 
NEEDED = [
    "Cab outer surface area A_surface [m2] for the truck you want to model (now 20 m2 PLACEHOLDER)",
    "Cab glass area A_window [m2] (now 4 m2 PLACEHOLDER)",
    "Cab U-value [W/m2K] or a measured UA [W/K] (now VECTO high-floor BUS 3.0)",
    "Cab air volume [m3] (now 6.5 m3 Scania sleeper cab; a day cab is smaller)",
    "HVAC hardware: heat pump yes/no + type, electric heater yes/no, max heating and cooling power (now VECTO bus driver compartment 5 kW / 5 kW)",
    "Does the truck pre-heat / pre-cool at the depot while charging? (not modelled; 13 Oct decision: no aux during charging)",
    "Door-opening / ventilation losses at delivery stops (not in VECTO SSM, not modelled)",
    "Real drivetrain efficiencies or a motor map + gearbox loss map + battery Ri (now 0.95/0.95/0.98, no battery loss) - see T19: this is the main gap to VECTO",
    "Battery thermal conditioning in cold weather (Cond is VECTO constant 550-600 W)",
]
 
 
# -------------------------------------------------------------------------------------
# 7c. eActros-LIKE TRUCK vs Oeko-Institut MEASURED REGRESSION
#     Mercedes does not publish curb mass, CdxA, tyre RRC or drivetrain efficiencies -> VECTO group-4 values are used
#     where VECTO has them; the rest stays flagged. Weight follows Oeko: gross weight EXCLUDING body (11-18 t).
# -------------------------------------------------------------------------------------
EACTROS = dict(
    gvw=19000.0,                      # [SOURCE] 19 t two-axle (electrive.com 30 Jun 2021; Oeko-Institut p.6)
    group="4",                        # [VECTO] SegmentTable.csv row 12: RigidTruck 4x2, 16-99 t -> group 4
    CdxA0=8.4,                        # [VECTO] SegmentTable.csv group 4 'CdxA_Default' = standard value used when no measured air drag
                                      #         (AirdragDataAdapter.cs 115-117). NOT a measured eActros value
    height=4.0,                       # [VECTO] SegmentTable.csv group 4 height
    axle_share=[0.45, 0.55],          # [VECTO] SegmentTable.csv group 4 'Truck Axles - Other' 45/55
    body_mass=2100.0,                 # [VECTO] body B4, Body_Trailers_Weights.csv; [ASSUMP] Oeko trucks carry a similar body
    tyre_d=1.014, tyre_F=3.05, tyre_inertia=14.9,   # [VECTO] Wheels.csv 315/70 R22.5; tyre size itself [ASSUMP]
    axles_rrc=[0.0065, 0.0075], axles_fz=[20850.0, 20850.0], axles_wheels=[2, 4],   # [ASSUMP] generic E2 tyre RRC/FzISO reused (eActros tyres unknown)
    P_motor_peak=400e3,               # [SOURCE] 400 kW peak, 330 kW continuous (electrive.com) - not used as a cap here (no generating curve)
)
AUX_G4 = {  # [VECTO] VAUX tables, group 4; same technologies as BEV_E2.vecto [ASSUMP: eActros aux technologies unknown]
    "UrbanDelivery":    dict(ES=1428.5714, PS=162, HVAC=150, SP=(430, 40, 50), cond=550),
    "RegionalDelivery": dict(ES=1428.5714, PS=200, HVAC=200, SP=(490, 40, 40), cond=600),
}
def oeko_model(s_kmh, T_C, w_t, alt_m):
    """Oeko-Institut Eq.1 + Table 2: C = m1*exp(-k1*s) + m2*T + m3*w + m4*a + m5 [kWh/km]; w = gross weight excl. body.
    Fitted on 19 eActros, 11-18 t, R2 = 0.473 -> indicative only (authors' caveat)."""
    return 5.130 * np.exp(-0.17 * s_kmh) - 0.013 * T_C + 0.018 * w_t + 0.002 * alt_m + 0.709
 
def t17():
    global VEH, SEG, AUX, M_VEHICLE, PAYLOAD_REF, R_DYN, THETA_WHEELS, M_RED_WHEELS, CRR_EFF, W1_DECL, W2_DECL, CDXA_REF
    global MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF, REGEN_EFF
    saved = (VEH, SEG, AUX, M_VEHICLE, PAYLOAD_REF, R_DYN, THETA_WHEELS, M_RED_WHEELS, CRR_EFF, W1_DECL, W2_DECL, CDXA_REF)
    try:
        E = EACTROS
        VEH = dict(VEH, CdxA0=E["CdxA0"], axles_rrc=E["axles_rrc"], axles_fz=E["axles_fz"], axles_wheels=E["axles_wheels"], tpmlm=E["gvw"])
        SEG = dict(SEG, height=E["height"], axle_share=E["axle_share"], body_mass=E["body_mass"])
        AUX = dict(AUX, **AUX_G4)
        R_DYN = E["tyre_d"] * E["tyre_F"] / (2 * math.pi)
        THETA_WHEELS = E["tyre_inertia"] * sum(E["axles_wheels"]); M_RED_WHEELS = THETA_WHEELS / R_DYN ** 2
        CRR_EFF = crr_eff(BETA)
        W1_DECL, W2_DECL = cdxa_table([V_DECL], H_DECL, None); CDXA_REF = VEH["CdxA0"] * W1_DECL[0] + W2_DECL[0]
        T20 = 20.0
        rows = []
        for cname in ["RegionalDelivery", "UrbanDelivery"]:
            cyc = CYCLES[cname]
            alt = np.concatenate(([0], np.cumsum(np.diff(cyc["s"]) * cyc["grad"][:-1] / 100)))
            for w_t in [11.0, 14.5, 18.0]:                       # Oeko regression range (gross excl. body)
                M_VEHICLE = w_t * 1000 + E["body_mass"]; PAYLOAD_REF = 0.0   # whole mass carried as 'vehicle', payload 0
                nh = 6
                wx = dict(T_amb_h=np.full(nh, T20), W1=np.repeat(W1_DECL, nh, 0), W2=np.repeat(W2_DECL, nh, 0), t_start=0.0)
                for eta_lab, eff in [("placeholder 0.95/0.95/0.98", (0.95, 0.95, 0.98)), ("what-if 0.90/0.95/0.97", (0.90, 0.95, 0.97))]:
                    keep = (MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF, REGEN_EFF)
                    MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF = eff; REGEN_EFF = MOTOR_EFF * INVERTER_EFF * GEARBOX_EFF
                    try:
                        r = run_chain(cyc, weather=wx, mission=cname)
                    finally:
                        MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF, REGEN_EFF = keep
                    sp, _ = split_energy(r)
                    km = r["S"][-1] / 1000; s_avg = km / (r["T"][-1] / 3600)
                    ours = r["E_battery"] / km; theirs = float(oeko_model(s_avg, T20, w_t, alt[-1] - alt[0]))
                    rows.append(dict(cycle=cname, w_excl_body_t=w_t, total_mass_t=M_VEHICLE / 1000, effs=eta_lab, avg_kmh=s_avg,
                                     HDEV_kWh_km=ours, Oeko_model_kWh_km=theirs, diff_pct=(ours / theirs - 1) * 100,
                                     traction=sp["traction"] / km, regen=sp["regen"] / km, aux=(r["E_battery"] - sp["traction"] - sp["regen"]) / km,
                                     regen_share_pct=-sp["regen"] / sp["traction"] * 100))
        df = pd.DataFrame(rows); show(df, "T17_eactros_like_vs_oeko"); STORE["eactros"] = df
        for cname, g in df[df.effs.str.startswith("placeholder")].groupby("cycle", sort=False):
            slope = np.polyfit(g.w_excl_body_t, g.HDEV_kWh_km, 1)[0]
            check("T17", f"{cname}: HDEV vs Oeko measured model at 20 C", "INFO",
                  f"{g.HDEV_kWh_km.min():.3f}-{g.HDEV_kWh_km.max():.3f} vs {g.Oeko_model_kWh_km.min():.3f}-{g.Oeko_model_kWh_km.max():.3f} kWh/km; "
                  f"weight slope {slope:.4f} vs 0.018 kWh/km/t")
        # where does the weight slope come from? rolling part, analytic: dF/dm of Crr_eff*g*m^beta, at the battery
        rr = []
        for w_t in [11.0, 14.5, 18.0]:
            m = w_t * 1000 + E["body_mass"]
            dF = BETA * CRR_EFF * G * m ** (BETA - 1)
            rr.append(dict(total_mass_t=m / 1000, Crr_total=crr_total_vecto(m), rolling_slope_kWh_km_per_t=dF * 1000 * 1000 / 3.6e6 / REGEN_EFF))
        show(pd.DataFrame(rr), "T17_rolling_part_of_weight_slope")
    finally:
        (VEH, SEG, AUX, M_VEHICLE, PAYLOAD_REF, R_DYN, THETA_WHEELS, M_RED_WHEELS, CRR_EFF, W1_DECL, W2_DECL, CDXA_REF) = saved
run_test("T17", "eActros-like (VECTO group 4 values) vs Oeko-Institut measured model, Regional + Urban", t17)
 
def g15():
    df = STORE.get("eactros")
    if df is None: return
    fig, ax = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for j, c in enumerate(["RegionalDelivery", "UrbanDelivery"]):
        for i, (lab, g) in enumerate(df[df.cycle == c].groupby("effs", sort=False)):
            ax[j].plot(g.w_excl_body_t, g.HDEV_kWh_km, "o-", color=PAL[i], label=f"HDEV, effs {lab}")
        g = df[(df.cycle == c)].drop_duplicates("w_excl_body_t")
        ax[j].plot(g.w_excl_body_t, g.Oeko_model_kWh_km, "s--", color="#52514e", label="Oeko-Institut measured model (eActros)")
        ax[j].set_title(f"{c}, 20 C, VECTO declaration wind", fontsize=9); ax[j].set_xlabel("gross weight excl. body [t]")
        ax[j].legend(fontsize=7)
    ax[0].set_ylabel("kWh/km")
    save(fig, "G15_eactros_like_vs_measured")
run_test("G15", "eActros comparison graph", g15)
 
 
# -------------------------------------------------------------------------------------
# 7d. SENSITIVITIES ONLY: HDEV (eActros-like) vs Oeko-Institut regression coefficients
#     Compares slopes, not levels: kWh/km per C, per tonne, per metre of climb.
# -------------------------------------------------------------------------------------
def t18():
    global VEH, SEG, AUX, M_VEHICLE, PAYLOAD_REF, R_DYN, THETA_WHEELS, M_RED_WHEELS, CRR_EFF, W1_DECL, W2_DECL, CDXA_REF
    saved = (VEH, SEG, AUX, M_VEHICLE, PAYLOAD_REF, R_DYN, THETA_WHEELS, M_RED_WHEELS, CRR_EFF, W1_DECL, W2_DECL, CDXA_REF)
    try:
        E = EACTROS
        VEH = dict(VEH, CdxA0=E["CdxA0"], axles_rrc=E["axles_rrc"], axles_fz=E["axles_fz"], axles_wheels=E["axles_wheels"], tpmlm=E["gvw"])
        SEG = dict(SEG, height=E["height"], axle_share=E["axle_share"], body_mass=E["body_mass"]); AUX = dict(AUX, **AUX_G4)
        R_DYN = E["tyre_d"] * E["tyre_F"] / (2 * math.pi); THETA_WHEELS = E["tyre_inertia"] * sum(E["axles_wheels"])
        M_RED_WHEELS = THETA_WHEELS / R_DYN ** 2; CRR_EFF = crr_eff(BETA)
        W1_DECL, W2_DECL = cdxa_table([V_DECL], H_DECL, None); CDXA_REF = VEH["CdxA0"] * W1_DECL[0] + W2_DECL[0]
        w_t = 14.5; M_VEHICLE = w_t * 1000 + E["body_mass"]; PAYLOAD_REF = 0.0; nh = 6
        temps = np.arange(-5.0, 25.1, 5.0)
        rows, srows = [], []
        for cname in ["RegionalDelivery", "UrbanDelivery"]:
            cyc = CYCLES[cname]
            for mname, mode in HVAC_MODES.items():
                kk = []
                for Tc in temps:
                    wx = dict(T_amb_h=np.full(nh, Tc), W1=np.repeat(W1_DECL, nh, 0), W2=np.repeat(W2_DECL, nh, 0), t_start=0.0)
                    h = None if mode is None else ref_HVAC_thermal(np.full(nh, Tc), np.zeros(nh), CAB, mode)["total"]   # solar 0 [ASSUMP]
                    r = run_chain(cyc, weather=wx, mission=cname, hvac_W=h)
                    kk.append(r["E_battery"] / (r["S"][-1] / 1000))
                    rows.append(dict(cycle=cname, hvac=mname, T_C=Tc, kWh_km=kk[-1]))
                srows.append(dict(cycle=cname, quantity="temperature (all -5..25 C)", hvac=mname, HDEV=np.polyfit(temps, kk, 1)[0], Oeko=OEKO["dT"], unit="kWh/km per C"))
                cold = temps <= 10
                srows.append(dict(cycle=cname, quantity="temperature (-5..10 C only)", hvac=mname, HDEV=np.polyfit(temps[cold], np.array(kk)[cold], 1)[0], Oeko=OEKO["dT"], unit="kWh/km per C"))
            # weight: 11 / 14.5 / 18 t at 20 C, VECTO constant HVAC
            ek = []
            for wt in [11.0, 14.5, 18.0]:
                M_VEHICLE = wt * 1000 + E["body_mass"]
                wx = dict(T_amb_h=np.full(nh, 20.0), W1=np.repeat(W1_DECL, nh, 0), W2=np.repeat(W2_DECL, nh, 0), t_start=0.0)
                r = run_chain(cyc, weather=wx, mission=cname); ek.append(r["E_battery"] / (r["S"][-1] / 1000))
            M_VEHICLE = w_t * 1000 + E["body_mass"]
            srows.append(dict(cycle=cname, quantity="weight (11..18 t excl. body)", hvac="VECTO constant", HDEV=np.polyfit([11, 14.5, 18], ek, 1)[0], Oeko=OEKO["dm"], unit="kWh/km per t"))
        # climb: physics m*g*dh/eta spread over the trip; Oeko's term is per metre per driving event of unknown length
        m = w_t * 1000 + E["body_mass"]; eta = MOTOR_EFF * INVERTER_EFF * GEARBOX_EFF
        for L in [25.0, 50.0, 100.0]:
            srows.append(dict(cycle=f"any, trip {L:.0f} km", quantity="net climb (per m)", hvac="-", HDEV=m * G / eta / 3.6e6 / L, Oeko=0.002, unit="kWh/km per m"))
        df = pd.DataFrame(srows); df["HDEV/Oeko"] = df.HDEV / df.Oeko; show(df, "T18_sensitivities_vs_oeko", 40)
        STORE["sens_T"] = pd.DataFrame(rows); STORE["sens"] = df
        for _, x in df.iterrows():
            check("T18", f"{x.cycle}: {x.quantity}, {x.hvac}", "INFO", f"HDEV {x.HDEV:+.4f} vs measured {x.Oeko:+.4f} {x.unit} ({x['HDEV/Oeko']:.2f}x)")
    finally:
        (VEH, SEG, AUX, M_VEHICLE, PAYLOAD_REF, R_DYN, THETA_WHEELS, M_RED_WHEELS, CRR_EFF, W1_DECL, W2_DECL, CDXA_REF) = saved
run_test("T18", "sensitivities only: HDEV eActros-like vs Oeko-Institut coefficients", t18)
 
def g16():
    d = STORE.get("sens_T")
    if d is None: return
    fig, ax = plt.subplots(1, 2, figsize=(12, 3.8))
    for j, c in enumerate(["RegionalDelivery", "UrbanDelivery"]):
        sub = d[d.cycle == c]
        for i, (m, g) in enumerate(sub.groupby("hvac", sort=False)):
            ax[j].plot(g.T_C, g.kWh_km - g.kWh_km.iloc[-1], "o-", color=PAL[i], label=f"HDEV, {m}")
        tt = np.array([-5.0, 25.0])
        ax[j].plot(tt, OEKO["dT"] * (tt - 25), "--", color="#52514e", label="Oeko-Institut measured slope")
        ax[j].set_title(f"{c}: change vs 25 C (eActros-like, 14.5 t)", fontsize=9); ax[j].set_xlabel("outside temperature [C]")
        ax[j].legend(fontsize=7)
    ax[0].set_ylabel("extra kWh/km vs 25 C")
    save(fig, "G16_temperature_sensitivity_vs_measured")
run_test("G16", "temperature sensitivity graph", g16)
 
 
# -------------------------------------------------------------------------------------
# 7e. EXPORT HDEV OUTPUTS FOR THE VECTO COMPARISON (comparison itself is done outside Colab)
#     Writes one 1 Hz CSV per cycle + a parts table, for the base efficiencies and for a what-if with VECTO's
#     trip-average efficiencies, then zips everything in OUT_DIR -> download hdev_outputs.zip
# -------------------------------------------------------------------------------------
EXPORT_CYCLES = ["RegionalDelivery", "UrbanDelivery"]
# VECTO trip-average efficiencies from YOUR run BEV_E2.vsum (VECTO 5.1.6-RC, 22 Oct 2026, ReferenceLoad rows):
#   motor drive / motor gen = eta_EM_E2_drive / eta_EM_E2_gen; gearbox, axle = 'Average gearbox/axlegear efficiency'
VECTO_AVG_EFF = {
    "RegionalDelivery": dict(motor_drive=0.8228, motor_gen=0.8663, gearbox=0.819254395250361, axle=0.936118282231225),
    "UrbanDelivery":    dict(motor_drive=0.8675, motor_gen=0.9209, gearbox=0.885151888953216, axle=0.95247654198116),
}   # [ASSUMP] averages used as constants; inverter taken as included in VECTO's motor map -> 1.0
 
def run_with_effs(cyc, eff):
    global MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF, REGEN_EFF
    keep = (MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF, REGEN_EFF)
    MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF, REGEN_EFF = eff
    try:
        return run_chain(cyc)
    finally:
        MOTOR_EFF, INVERTER_EFF, GEARBOX_EFF, REGEN_EFF = keep
 
def rows_table(r):
    """1 Hz HDEV rows with the wheel power split out of YOUR P_wheel (constant payload):
    P_wheel = m*k_lin + m^beta*k_roll + k_rot + air  ->  air = P_wheel - the rest."""
    m = M_VEHICLE + PAYLOAD_REF
    P_lin, P_roll, P_rot = m * r["k_lin"], m ** BETA * r["k_roll"], r["k_rot"]
    P_grade = m * G * np.sin(np.arctan(r["G"] / 100)) * r["v_avg"]
    sp, comp = split_energy(r)
    return pd.DataFrame(dict(t_s=r["T"], s_m=r["S"], v_kmh=r["V"] * 3.6, a=r["A"], grade_pct=r["G"], mode=r["M"],
                             P_wheel_W=r["P_wheel"], P_air_W=r["P_wheel"] - P_lin - P_roll - P_rot, P_roll_W=P_roll,
                             P_grade_W=P_grade, P_inertia_W=P_lin - P_grade + P_rot, P_trac_W=r["P_trac"],
                             P_ES_W=comp["ES"], P_PS_W=comp["PS"], P_HVAC_W=comp["HVAC"], P_SP_W=comp["SP"], P_Cond_W=comp["Cond"],
                             P_aux_W=r["P_aux_row"], P_battery_W=r["P_battery"]))
 
def t19():
    import shutil
    summ = []
    for c in EXPORT_CYCLES:
        e = VECTO_AVG_EFF[c]; gbx = e["gearbox"] * e["axle"]
        runs = {"base": STORE[c], "vecto_avg_eff": run_with_effs(CYCLES[c], (e["motor_drive"], 1.0, gbx, e["motor_gen"] * gbx))}
        for lab, r in runs.items():
            tab = rows_table(r); tab.to_csv(os.path.join(OUT_DIR, f"HDEV_rows_{c}_{lab}.csv"), index=False)
            h = lambda col: float(tab[col].sum() / 3.6e6)
            on = tab.P_trac_W != 0
            summ.append(dict(cycle=c, run=lab, km=tab.s_m.iloc[-1] / 1000, time_s=len(tab), stand_s=int((tab["mode"] == 0).sum()),
                             wheel_pos=float(tab.P_wheel_W.clip(lower=0).sum() / 3.6e6), wheel_neg=float(-tab.P_wheel_W.clip(upper=0).sum() / 3.6e6),
                             air=h("P_air_W"), roll=h("P_roll_W"), grade=h("P_grade_W"), inertia=h("P_inertia_W"),
                             not_recuperated=float(-tab.P_wheel_W.clip(upper=0)[~on].sum() / 3.6e6),
                             trac_el=float(tab.P_trac_W.clip(lower=0).sum() / 3.6e6), regen_el=float(-tab.P_trac_W.clip(upper=0).sum() / 3.6e6),
                             drivetrain_loss=float((tab.P_trac_W - tab.P_wheel_W)[on].sum() / 3.6e6),
                             ES=h("P_ES_W"), PS=h("P_PS_W"), HVAC=h("P_HVAC_W"), SP=h("P_SP_W"), Cond=h("P_Cond_W"), aux=h("P_aux_W"),
                             E_battery=float(r["E_battery"]), kWh_km=float(r["E_battery"]) / (tab.s_m.iloc[-1] / 1000),
                             effs=f"{MOTOR_EFF}/{INVERTER_EFF}/{GEARBOX_EFF}" if lab == "base" else f"{e['motor_drive']}/1.0/{gbx:.4f}"))
    df = pd.DataFrame(summ); show(df, "HDEV_parts_for_vecto_compare", 20)
    for c in COMPARE_CYCLES if "COMPARE_CYCLES" in globals() else EXPORT_CYCLES:
        a = aux_values(c)
        check("T19", f"{c}: aux W exported", "INFO", f"ES {a['ES']:.1f}, PS {a['PS']:.1f}, HVAC {a['HVAC']:.1f}, SP {a['SP']:.2f}, Cond {a['cond']:.1f}")
    t = HV.get("yeardf")
    if t is not None:
        t = t.copy(); t["month"] = pd.to_datetime(t.date).dt.month
        mt = t.pivot_table(index=["cycle", "month"], columns="hvac", values="kWh_km", aggfunc="mean").reset_index()
        show(mt, "HDEV_monthly_kWh_km_by_hvac", 40)
    shutil.make_archive(os.path.join(os.path.dirname(OUT_DIR), "hdev_outputs"), "zip", OUT_DIR)
    check("T19", "export zip", "INFO", f"{os.path.join(os.path.dirname(OUT_DIR), 'hdev_outputs.zip')} -> download and send it")
run_test("T19", "export HDEV outputs for the VECTO comparison", t19)
 
# -------------------------------------------------------------------------------------
# 8. SUMMARY  (paste this block back into the chat)
# -------------------------------------------------------------------------------------
res = pd.DataFrame(RESULTS)
res.to_csv(os.path.join(OUT_DIR, "SUMMARY_checks.csv"), index=False)
print("\n" + "=" * 100)
print("SUMMARY  " + "  ".join(f"{k}: {v}" for k, v in res.status.value_counts().items()))
print("=" * 100)
with pd.option_context("display.width", 220, "display.max_colwidth", 110):
    print(res.to_string(index=False))
print(f"\nInputs: vehicle = VECTO generic E2 BEV (group 2), m_vehicle {M_VEHICLE:.0f} kg, ref payload {PAYLOAD_REF:.1f} kg, CdxA0 {VEH['CdxA0']}, "
      f"beta {BETA}, effs {MOTOR_EFF}/{INVERTER_EFF}/{GEARBOX_EFF} [ILLUS], regen {REGEN_EFF:.4f} [ASSUMP], weather {WEATHER_SOURCE} {WX_SRC}")
print(f"All tables (.csv) and graphs (.png) are in {OUT_DIR}")
print("\nINFORMATION NEEDED FROM YOU (HVAC thermal and absolute level):")
for i, n in enumerate(NEEDED, 1):
    print(f"  {i:2}. {n}")
