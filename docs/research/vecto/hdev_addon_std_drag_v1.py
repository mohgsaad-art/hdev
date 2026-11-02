# =====================================================================================
# HDEV ADD-ON v1 (22 Oct 2026): EU standard-value drivetrain + coasting drag + regen cap
# Run in Colab AFTER harness v1.7 (same session; uses its CONFIG, constants, CYCLES, run_chain, _get, OUT_DIR).
# Calls YOUR driver_model / force_engine / consumption_engine. Nothing in your engine is changed.
#
# What it does, per cycle (RegionalDelivery, UrbanDelivery, MunicipalUtility incl. refuse PTO):
#   A  HDEV as now (fixed 0.95/0.95/0.98, no coasting drag)
#   B  same speed trace, drivetrain = EU standard values (gearbox, axle, motor) + motor regen torque cap
#   C  B + coasting drag in the driver model (drag from the same standard values) -> new speed trace
# Exports HDEV results only -> hdev_addon_outputs.zip (Claude compares with VECTO / OEM outside Colab).
#
# Sources (all values below are read from these, nothing invented):
#   gearbox : Reg. 2017/2400 Annex VI App. 8 (AMT): T_loss,in = Td0 + Td1000*n/1000 + fT*|T_in|, Td = 0.005*Tmax_in, fT 0.04 (indirect)
#   axle    : Annex VII App. 3, single reduction: eta 0.98, Td0 = 70 + 20*i_axle (wheel side)
#   motor   : Annex Xb App. 8 step 6 (loss map, k_mn for ASM, x0.96) and step 7 (drag curve)
#   loss-map lookup like VECTO: TransmissionLossMap.cs 77, 94 ; EfficiencyMap.cs 23 (Delaunay, linear)
#   E2 truck: AMT.vgbx (3.86 / 1.93, axle 2.59), BatteryElectricVehicle.vveh (2 motors, ADC 2.0), .vem (ASM), .vemp (485 Nm, rated 2461 rpm)
# Flags:
#   [ASSUMP] gearbox max input torque Tmax_in = what the two motors can send = 2 x 485 x 2.0 = 1940 Nm (spec sheets do not give it)
#   [ASSUMP] axle formula: regulation text is OCR-garbled; built like VECTO's generic axle (GenericTransmissionComponentData.cs 101-152)
#   [ASSUMP] gear rule (not VECTO's 956-line PEVAMTShiftStrategy): gear 2 unless the motors cannot give the torque in gear 2 -> gear 1
#            (VECTO used gear 2 for >99 % of driving on both cycles in your run)
#   [ASSUMP] coasting drag uses gear 2; ADC (motor->gearbox) loss 0 as in your .vmod; motor rotor inertia ignored
#   [TEST]   the drag is handed to your driver_model through P_drag_loss as a number that returns drag FORCE(v) when divided by v
#            (your coast_acc uses P_drag_loss / v). Check D0 below prints how coast_distance uses it.
# =====================================================================================
import functools, inspect, shutil
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
 
_need = ["OUT_DIR", "run_chain", "CYCLES", "check", "run_test", "show", "split_energy", "read_csv_numeric", "R_DYN", "V_NO_REGEN"]
_miss = [x for x in _need if x not in globals()]
if _miss:
    raise RuntimeError(f"harness v1.7 has not run in this Colab session (missing: {_miss}). "
                       "Run your engine cells, then harness v1.7 (at least sections 0-4), then this cell.")
STORE = globals().get("STORE", {})
 
ADD_DIR = os.path.join(os.path.dirname(OUT_DIR), "hdev_addon_out"); os.makedirs(ADD_DIR, exist_ok=True)
ADD_CYCLES = ["RegionalDelivery", "UrbanDelivery", "MunicipalUtility"]
I_AXLE, I_GEAR, I_ADC, N_EM = 2.59, {1: 3.86, 2: 1.93}, 2.0, 2       # [VECTO] AMT.vgbx, .vveh
T_EM_MAX, N_RATED, N_EM_MAX = 485.0, 2461.158914, 9845.0             # [VECTO] .vemp / .vemo (per motor)
TMAX_IN = N_EM * T_EM_MAX * I_ADC                                     # [ASSUMP] 1940 Nm
RPM = 60 / (2 * math.pi)
 
# ---------- standard-value components ----------
class _Loss:
    def __init__(self, m, ratio):
        self.ratio = ratio; pts = np.c_[m[:, 0], m[:, 1] - m[:, 2]]
        self.lin = LinearNDInterpolator(pts, m[:, 2]); self.near = NearestNDInterpolator(pts, m[:, 2])
    def input_side(self, n_out, T_out):
        n_in, T = n_out * self.ratio, T_out / self.ratio
        l = self.lin(n_in, T); b = np.isnan(l); l[b] = self.near(n_in[b], T[b])
        return n_in, T + l, l
 
def std_gearbox(ratio, tmax_in, fT=0.04):
    td = 0.005 * tmax_in
    n = np.array([0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000], float)
    N, TT = np.meshgrid(n, np.linspace(-1.1 * tmax_in, 1.1 * tmax_in, 45)); N, TT = N.ravel(), TT.ravel()
    return _Loss(np.c_[N, TT, td + td * N / 1000 + fT * np.abs(TT)], ratio)
 
def std_axle(ratio, T0=70.0, T1=20.0, eta=0.98):
    td0 = T0 + T1 * ratio
    n_out = np.array([0, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000], float)
    T_out = np.r_[-np.geomspace(250, 500000, 25)[::-1], 0, np.geomspace(250, 500000, 25)]
    N, TT = np.meshgrid(n_out, T_out); N, TT = N.ravel(), TT.ravel()
    lo = td0 + np.abs(TT) / eta - np.abs(TT)
    return _Loss(np.c_[N * ratio, (TT + lo) / ratio, lo / ratio], ratio), td0
 
K_ASM = {(2, 0): 0.1, (2, 1): 0.03, (2, 2): 0.03, (1, 0): 0.01, (1, 2): 0.001, (0, 0): 0.003, (0, 2): 0.001, (0, 3): 0.001}
def _std_eff(Tn, Wn):
    pl = sum(c * np.abs(Tn) ** m * np.abs(Wn) ** n for (m, n), c in K_ASM.items()); pm = Tn * Wn
    return np.maximum(np.where(Tn > 0, pm / (pm + pl), (pm + pl) / pm) * 0.96, 0)
def std_motor():
    wn = np.r_[0.02, np.arange(0.2, 4.0001, 0.2)]
    tn = np.r_[-np.arange(1.0, 0.0499, -0.05), -0.01, 0.01, np.arange(0.05, 1.0001, 0.05)]
    W, Tn = np.meshgrid(wn, tn); W, Tn = W.ravel(), Tn.ravel()
    n, T = W * N_RATED, Tn * T_EM_MAX; Pm = T * n / RPM
    Pel = (1 - _std_eff(Tn, W)) * np.abs(Pm) + Pm
    lin, near = LinearNDInterpolator(np.c_[n, T], Pel), NearestNDInterpolator(np.c_[n, T], Pel)
    def f(nn, TT):
        p = lin(nn, TT); b = np.isnan(p); p[b] = near(nn[b], TT[b]); return p
    return f
def std_motor_drag(n_rpm):
    """Annex Xb App. 8 step 7: drag torque (per motor, magnitude) at Tn = 0.01, wn = 1 and 4, linear in between/outside"""
    d1, d4 = [(1 - _std_eff(np.array(0.01), np.array(wn))) * 0.01 * T_EM_MAX for wn in (1.0, 4.0)]
    return d1 + (d4 - d1) * (np.asarray(n_rpm, float) - N_RATED) / (3 * N_RATED)   # straight line through both points (step 7 b, c)
 
GB = {g: std_gearbox(I_GEAR[g], TMAX_IN) for g in (1, 2)}
AX, AX_TD0 = std_axle(I_AXLE)
EMF = std_motor()
_, _fld = read_csv_numeric("Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/GenericEMotor_125kW_485Nm.vemp")
_fld = _fld[np.argsort(_fld[:, 0])]
t_drive_max = lambda n: np.interp(n, _fld[:, 0], _fld[:, 1]); t_gen_max = lambda n: np.interp(n, _fld[:, 0], np.abs(_fld[:, 2]))
 
def drivetrain_el(v_avg, P_wheel, use):
    """wheel power -> electric power of both motors [W], standard values, gear rule, regen cap"""
    n = len(v_avg); P_el = np.zeros(n); parts = dict(axle=np.zeros(n), gearbox=np.zeros(n), motor=np.zeros(n), friction_brake=np.zeros(n))
    gear_used = np.zeros(n, int)
    w = v_avg / R_DYN; on = use & (w > 1e-3) & (P_wheel != 0)
    if not on.any(): return P_el, parts, gear_used
    n_ax, T_ax, l_ax = AX.input_side(w[on] * RPM, P_wheel[on] / w[on])
    res = {}
    for g, L in GB.items():
        n_gb, T_gb, l_gb = L.input_side(n_ax, T_ax); res[g] = (n_gb, T_gb, l_gb, n_gb * I_ADC, T_gb / I_ADC / N_EM)
    ok2 = (res[2][4] <= t_drive_max(res[2][3])) & (res[2][3] <= N_EM_MAX)
    ok1 = res[1][3] <= N_EM_MAX
    g_sel = np.where(ok2 | ~ok1, 2, 1)
    pick = lambda k: np.where(g_sel == 2, res[2][k], res[1][k])
    n_gb, l_gb, n_em, T_em = pick(0), pick(2), pick(3), pick(4)
    cap = -t_gen_max(n_em); low = T_em < cap
    brake = np.where(low, (cap - T_em) * N_EM * n_em / RPM, 0.0)       # torque the motors cannot take -> friction brakes
    T_em = np.maximum(T_em, cap)
    pe = EMF(n_em, T_em) * N_EM; pm = T_em * N_EM * n_em / RPM
    P_el[on] = pe; gear_used[on] = g_sel
    parts["axle"][on] = l_ax * n_ax / RPM; parts["gearbox"][on] = l_gb * n_gb / RPM; parts["motor"][on] = pe - pm
    parts["friction_brake"][on] = np.abs(brake)
    return P_el, parts, gear_used
 
# ---------- coasting drag at the wheels (gear 2), from the same standard values ----------
V_TAB = np.arange(0.0, 131.0, 1.0) / 3.6
def drag_force(v):
    v = np.asarray(v, float); n_ax = v / R_DYN * RPM * I_AXLE; n_gb = n_ax * I_GEAR[2]; n_em = n_gb * I_ADC
    td = 0.005 * TMAX_IN
    T_gb_in = td + td * n_gb / 1000 + N_EM * std_motor_drag(n_em) * I_ADC        # gearbox drag + motor drag at gearbox input [Nm]
    return (T_gb_in * I_GEAR[2] * I_AXLE + AX_TD0) / R_DYN                          # [N] at the wheels
F_TAB = drag_force(V_TAB)
 
class DragPower(float):
    """[TEST] a number whose division by a speed gives the drag FORCE at that speed (your coast_acc does P_drag_loss / v)"""
    def __new__(cls): return float.__new__(cls, float(np.interp(70 / 3.6, V_TAB, F_TAB) * 70 / 3.6))   # plain value = drag power at 70 km/h
    def __truediv__(self, v): return float(np.interp(float(v), V_TAB, F_TAB))
DRAG = DragPower()
 
def run_case(cname, drag):
    global driver_model
    orig = driver_model
    try:
        if drag: driver_model = functools.partial(orig, P_drag_loss=DRAG)
        r = run_chain(CYCLES[cname])
    finally:
        driver_model = orig
    v_avg = np.maximum(r["V"] + r["A"] / 2, 0); M = r["M"]
    use = (M != 0) & (M != 3) & ~((M == 4) & (r["V"] <= V_NO_REGEN))      # same on/off rules as your consumption_engine
    P_el, parts, gear = drivetrain_el(v_avg, np.where(use, r["P_wheel"], 0.0), use)
    return r, P_el, parts, gear
 
def d00():
    for fn in ("driver_model", "coast_distance"):
        if fn in globals():
            lines = [l.strip() for l in inspect.getsource(globals()[fn]).splitlines() if "P_drag_loss" in l and "def " not in l]
            check("D0", f"how {fn} uses P_drag_loss", "INFO", " | ".join(lines)[:300])
    bad = [l for fn in ("coast_distance",) if fn in globals()
           for l in inspect.getsource(globals()[fn]).splitlines() if "P_drag_loss" in l and "def " not in l and "/" not in l]
    check("D0", "P_drag_loss only used as power / speed", not bad, "; ".join(x.strip() for x in bad)[:200] or "ok")
    tab = pd.DataFrame(dict(v_kmh=[40, 50, 60, 70, 80, 90], drag_N=np.interp(np.array([40, 50, 60, 70, 80, 90]) / 3.6, V_TAB, F_TAB)))
    show(tab, "D0_coast_drag_standard_values")
    check("D0", "coast drag (standard values) vs VECTO example maps measured from your .vmod", "INFO",
          "VECTO example: 1.43 kN @40-50, 1.63 @60-70, 2.05 @80-90 km/h (22 Oct close-out)")
run_test("D0", "setup: standard-value drag table", d00)
 
ADD = {}
def d01():
    rows, parts_rows = [], []
    for c in ADD_CYCLES:
        base = STORE[c] if c in STORE else run_chain(CYCLES[c])
        km0 = base["S"][-1] / 1000; sp0, _ = split_energy(base); aux0 = sum(v for k, v in sp0.items() if k not in ("traction", "regen"))
        rows.append(dict(cycle=c, case="A HDEV now (0.95/0.95/0.98)", km=km0, kWh_km=base["E_battery"] / km0))
        for lab, drag in [("B standard drivetrain", False), ("C standard drivetrain + coast drag", True)]:
            r, P_el, parts, gear = run_case(c, drag)
            km = r["S"][-1] / 1000; aux = float(np.sum(r["P_aux_row"]) / 3.6e6); E = float(np.sum(P_el) / 3.6e6) + aux
            M = r["M"]; t = len(M)
            rows.append(dict(cycle=c, case=lab, km=km, kWh_km=E / km, trip_s=t,
                             stop_pct=np.mean(M == 0) * 100, accel_pct=np.mean(M == 1) * 100, cruise_pct=np.mean(M == 2) * 100,
                             coast_pct=np.mean(M == 3) * 100, brake_pct=np.mean(M == 4) * 100, v_max_kmh=r["V"].max() * 3.6,
                             regen_kWh=-float(np.sum(np.minimum(P_el, 0)) / 3.6e6), aux_kWh=aux, gear1_s=int(np.sum(gear == 1))))
            parts_rows.append(dict(cycle=c, case=lab, **{k: float(np.sum(x) / 3.6e6) for k, x in parts.items()}))
            ADD[(c, lab)] = (r, P_el)
            if drag:
                pd.DataFrame(dict(t_s=r["T"], s_m=r["S"], v_kmh=r["V"] * 3.6, a=r["A"], mode=M, gear=gear, P_wheel_W=r["P_wheel"],
                                  P_el_W=P_el, P_aux_W=r["P_aux_row"])).to_csv(os.path.join(ADD_DIR, f"ADD_rows_{c}_C.csv"), index=False)
    df = pd.DataFrame(rows); show(df, "ADD_results"); show(pd.DataFrame(parts_rows), "ADD_losses_kWh")
    df.to_csv(os.path.join(ADD_DIR, "ADD_results.csv"), index=False); pd.DataFrame(parts_rows).to_csv(os.path.join(ADD_DIR, "ADD_losses_kWh.csv"), index=False)
    for c in ADD_CYCLES:
        a, b = df[(df.cycle == c)].kWh_km.iloc[[1, 2]]
        check("D1", f"{c}: coast drag effect", "INFO", f"B {a:.3f} -> C {b:.3f} kWh/km ({(b/a-1)*100:+.1f} %)")
run_test("D1", "standard drivetrain + coast drag, all three cycles", d01)
 
shutil.make_archive(os.path.join(os.path.dirname(OUT_DIR), "hdev_addon_outputs"), "zip", ADD_DIR)
print("\nADD-ON done ->", os.path.join(os.path.dirname(OUT_DIR), "hdev_addon_outputs.zip"), " (download and send it, plus the D0/D1 printout)")
