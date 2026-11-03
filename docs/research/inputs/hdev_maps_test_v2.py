# =====================================================================================
# HDEV loss-map test v2 (22 Oct 2026) -- runs in Claude's workspace, NOT in Colab
#   v1 + EU STANDARD-VALUE components (what a user without OEM files would get):
#     gearbox : Reg. 2017/2400 Annex VI Appendix 8   T_loss,in = Td0 + Td1000*n/1000 + fT*|T_in|
#               AMT (tooth shift clutches): Td0 = Td1000 = 0.005 * Tmax_in ; fT = 0.04 indirect gear, 0.01 direct
#     axle    : Annex VII Appendix 3, single reduction: eta 0.98, Td0 = 70 + 20*i (wheel side)
#               loss at output = Td0 + |T_out|/eta - |T_out|, moved to input side the way VECTO does it
#               for its own generic axle (GenericTransmissionComponentData.cs 101-108, 139-152)  [ASSUMP: OCR of the
#               regulation formula is garbled; structure taken from VECTO's generic-axle code]
#     motor   : Annex Xb Appendix 8 step 6, k_mn table for ASM (the E2 motor type in GenericEMotor_125kW_485Nm.vem),
#               T_max 485 Nm, rated speed 2461 rpm (highest speed at max torque, .vemp), x0.96 factor
#   Same HDEV rows, same gears from VECTO by distance as v1.
# =====================================================================================
import sys, os, math
import numpy as np
import pandas as pd
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
E2 = os.path.join(BASE, "vecto/Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/")
HDEV = os.path.join(BASE, "hdev_out/")
VMOD = {"RegionalDelivery": os.path.join(BASE, "data/RD.vmod"), "UrbanDelivery": os.path.join(BASE, "data/UD.vmod")}

I_AXLE, I_GEAR, I_ADC, N_EM = 2.59, {1: 3.86, 2: 1.93}, 2.0, 2            # [VECTO] AMT.vgbx, BatteryElectricVehicle.vveh
R_DYN = 0.867 * 3.05 / (2 * math.pi)                                       # [VECTO] Wheels.csv, Wheels.cs 74
RPM = 60 / (2 * math.pi)
V_NO_REGEN = 5 / 3.6
T_EM_MAX, N_RATED = 485.0, 2461.158914                                     # [VECTO] .vemp per motor
TMAX_IN_E2 = N_EM * T_EM_MAX * I_ADC                                       # [ASSUMP] gearbox max input torque = what the motors can send (1940 Nm)
REFS = {"MAN eTGL (OEM, 11.99 t)": 0.69, "Danish fit at 11.99 t": 0.796, "Liimatainen fit at 11.99 t": 0.855}

def csv(f): return np.genfromtxt(E2 + f, delimiter=",", skip_header=1)

class Loss:
    """loss map, VECTO way: points (n_in, T_in - loss) -> loss  [TransmissionLossMap.cs 77, 94]"""
    def __init__(self, m, ratio):
        self.ratio = ratio; pts = np.c_[m[:, 0], m[:, 1] - m[:, 2]]
        self.lin = LinearNDInterpolator(pts, m[:, 2]); self.near = NearestNDInterpolator(pts, m[:, 2])
    def input_side(self, n_out_rpm, T_out):
        n_in, T = n_out_rpm * self.ratio, T_out / self.ratio
        loss = self.lin(n_in, T); bad = np.isnan(loss); loss[bad] = self.near(n_in[bad], T[bad])
        return n_in, T + loss, loss

class EMap:
    def __init__(self, m):   # m: n, T per motor (+ drive), P_el W (+ drawn)
        self.lin = LinearNDInterpolator(m[:, :2], m[:, 2]); self.near = NearestNDInterpolator(m[:, :2], m[:, 2])
    def __call__(self, n, T):
        p = self.lin(n, T); bad = np.isnan(p); p[bad] = self.near(n[bad], T[bad]); return p

# ---------- VECTO example components ----------
AXLE_EX = Loss(csv("Axle_4x2_Tractor.vtlm"), I_AXLE)
GEAR_EX = {g: Loss(csv(f"Gear_{g}.vtlm"), I_GEAR[g]) for g in (1, 2)}
_em = csv("GenericMap_125kW_485Nm.vemo"); EM_EX = EMap(np.c_[_em[:, :2], _em[:, 2] * 1000])
fld = csv("GenericEMotor_125kW_485Nm.vemp"); fld = fld[np.argsort(fld[:, 0])]
def t_gen_max(n): return np.interp(n, fld[:, 0], np.abs(fld[:, 2]))

# ---------- EU standard-value components ----------
def std_gearbox(ratio, tmax_in, direct=False):
    """Annex VI App. 8, AMT: Td0 = Td1000 = 0.005*Tmax_in; fT 0.01 direct / 0.04 indirect"""
    td = 0.005 * tmax_in; fT = 0.01 if direct else 0.04
    n = np.array([0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000], float)
    T = np.linspace(-1.1 * tmax_in, 1.1 * tmax_in, 45)
    N, TT = np.meshgrid(n, T); N, TT = N.ravel(), TT.ravel()
    return Loss(np.c_[N, TT, td + td * N / 1000 + fT * np.abs(TT)], ratio)

def std_axle(ratio, T0=70.0, T1=20.0, eta=0.98):
    """Annex VII App. 3 single reduction: Td0 = T0 + T1*i (wheel side); output loss = Td0 + |T|/eta - |T|;
    input map built like VECTO's generic axle (GenericTransmissionComponentData.cs 139-152)"""
    td0 = T0 + T1 * ratio
    n_out = np.array([0, 50, 100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000], float)
    T_out = np.r_[-np.geomspace(250, 500000, 25)[::-1], 0, np.geomspace(250, 500000, 25)]
    N, TT = np.meshgrid(n_out, T_out); N, TT = N.ravel(), TT.ravel()
    loss_out = td0 + np.abs(TT) / eta - np.abs(TT)
    return Loss(np.c_[N * ratio, (TT + loss_out) / ratio, loss_out / ratio], ratio)

def std_motor(t_max, n_rated):
    """Annex Xb App. 8 step 6, k_mn for ASM/ESM/RM (non-PSM); eta x 0.96; per motor, P_el in W"""
    k = {(2, 0): 0.1, (2, 1): 0.03, (2, 2): 0.03, (1, 0): 0.01, (1, 2): 0.001, (0, 0): 0.003, (0, 2): 0.001, (0, 3): 0.001}
    wn = np.r_[0.02, np.arange(0.2, 4.0001, 0.2)]
    tn = np.r_[-np.arange(1.0, 0.0499, -0.05), -0.01, 0.01, np.arange(0.05, 1.0001, 0.05)]
    W, Tn = np.meshgrid(wn, tn); W, Tn = W.ravel(), Tn.ravel()
    pl = sum(c * np.abs(Tn) ** m * np.abs(W) ** n for (m, n), c in k.items())
    pm = Tn * W
    eta = np.where(Tn > 0, pm / (pm + pl), (pm + pl) / pm) * 0.96
    eta = np.maximum(eta, 0)
    n_rpm, T = W * n_rated, Tn * t_max
    P_mech = T * n_rpm / RPM
    P_loss = (1 - eta) * np.abs(P_mech)
    P_el = P_loss + P_mech
    return EMap(np.c_[n_rpm, T, P_el])

def chain(v_ms, P_axle_out, gear, axle, gears, emap):
    n = len(v_ms); out = {k: np.zeros(n) for k in ["axle_loss", "gbx_loss", "em_loss", "P_el"]}
    w = v_ms / R_DYN; on = (w > 1e-3) & (gear > 0) & (P_axle_out != 0)
    n_ax, T_ax, l_ax = axle.input_side(w[on] * RPM, P_axle_out[on] / w[on])
    g = gear[on]; n_gb = np.zeros(on.sum()); T_gb = np.zeros(on.sum()); l_gb = np.zeros(on.sum())
    for kk, L in gears.items():
        s = g == kk
        if s.any(): n_gb[s], T_gb[s], l_gb[s] = L.input_side(n_ax[s], T_ax[s])
    n_em = n_gb * I_ADC; T_em = np.maximum(T_gb / I_ADC / N_EM, -t_gen_max(n_gb * I_ADC))   # regen cap (never hit in v1)
    P_el = emap(n_em, T_em) * N_EM; P_mech = T_em * N_EM * n_em / RPM
    out["axle_loss"][on] = l_ax * n_ax / RPM; out["gbx_loss"][on] = l_gb * n_gb / RPM
    out["em_loss"][on] = P_el - P_mech; out["P_el"][on] = P_el
    return out

def kwh(x): return float(np.sum(x) / 3.6e6)
def read_vmod(p):
    v = pd.read_csv(p, skiprows=1, encoding="utf-8-sig")
    return v[~v.iloc[:, 0].astype(str).str.startswith("#")].apply(pd.to_numeric, errors="coerce").reset_index(drop=True)

GB_STD = {g: std_gearbox(I_GEAR[g], TMAX_IN_E2) for g in (1, 2)}
GB_STD5500 = {g: std_gearbox(I_GEAR[g], 5500.0) for g in (1, 2)}
AX_STD = std_axle(I_AXLE)
EM_STD = std_motor(T_EM_MAX, N_RATED)
CASES = {
    "VECTO example maps (all three)":                 (AXLE_EX, GEAR_EX, EM_EX),
    "standard gearbox, example axle + motor":         (AXLE_EX, GB_STD, EM_EX),
    "standard gearbox + axle, example motor":         (AX_STD, GB_STD, EM_EX),
    "ALL standard values (user default)":             (AX_STD, GB_STD, EM_STD),
    "ALL standard, gearbox Tmax_in 5500 Nm (sens.)":  (AX_STD, GB_STD5500, EM_STD),
}

rows, parts = [], []
for c, p in VMOD.items():
    v = read_vmod(p); h = pd.read_csv(HDEV + f"HDEV_rows_{c}_base.csv"); km = h.s_m.iloc[-1] / 1000
    vg = v[v["Gear [-]"] > 0]
    gear = vg["Gear [-]"].to_numpy()[np.clip(np.searchsorted(vg["dist [m]"].to_numpy(), h.s_m.to_numpy()), 0, len(vg) - 1)].astype(int)
    v_avg = np.maximum(h.v_kmh.to_numpy() / 3.6 + h.a.to_numpy() / 2, 0)
    mode = h["mode"].to_numpy()
    use = (mode != 0) & (mode != 3) & ~((mode == 4) & (h.v_kmh.to_numpy() / 3.6 <= V_NO_REGEN))
    Pw = np.where(use, h.P_wheel_W.to_numpy(), 0.0); aux = kwh(h.P_aux_W)
    vecto = -v["P_REESS_T [kW]"].sum() / 3600 / (v["dist [m]"].iloc[-1] / 1000)
    res = {"HDEV before (0.95/0.95/0.98)": (kwh(h.P_trac_W) + aux) / km}
    for lab, (ax, gb, emm) in CASES.items():
        r = chain(v_avg, Pw, gear, ax, gb, emm); res[lab] = (kwh(r["P_el"]) + aux) / km
        parts.append(dict(cycle=c, case=lab, axle=kwh(r["axle_loss"]), gearbox=kwh(r["gbx_loss"]), motor=kwh(r["em_loss"]),
                          regen=-kwh(np.minimum(r["P_el"], 0))))
    res["VECTO (battery terminals)"] = vecto
    for lab, x in res.items():
        rows.append(dict(cycle=c, case=lab, kWh_km=x, vs_MAN_pct=(x / 0.69 - 1) * 100, vs_DK_fit_pct=(x / 0.796 - 1) * 100,
                         vs_VECTO_pct=(x / vecto - 1) * 100))
pd.set_option("display.width", 220)
print(pd.DataFrame(rows).round(3).to_string(index=False))
print("\nlosses per trip [kWh] (≈100 km)")
print(pd.DataFrame(parts).round(2).to_string(index=False))
# spot check of the standard motor map: efficiency at a few points (per motor)
for n_, T_ in [(2461, 100), (2461, 300), (5000, 100), (5000, -100), (1000, 50)]:
    pe = EM_STD(np.array([n_], float), np.array([T_], float))[0]; pm = T_ * n_ / RPM
    print(f"std motor n {n_} rpm T {T_} Nm: P_mech {pm/1000:.1f} kW, P_el {pe/1000:.1f} kW, eff {(pm/pe if T_>0 else pe/pm):.3f}")
for n_, T_ in [(2461, 100), (5000, 100), (5000, -100)]:
    pe = EM_EX(np.array([n_], float), np.array([T_], float))[0]; pm = T_ * n_ / RPM
    print(f"example motor n {n_} rpm T {T_} Nm: eff {(pm/pe if T_>0 else pe/pm):.3f}")
