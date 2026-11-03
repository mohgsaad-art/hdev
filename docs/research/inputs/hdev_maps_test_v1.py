# =====================================================================================
# HDEV loss-map test v1 (22 Oct 2026) -- runs in Claude's workspace, NOT in Colab
#   Question: do VECTO-style loss maps (motor + gearbox + axle) and the motor regen
#   torque cap move HDEV's kWh/km to where real trucks are?
#   Test-only: gear per row is taken from VECTO's .vmod by distance (option C).
#   Coasting drag (fix 3) is NOT in this test: it changes the speed trace -> needs the driver model.
#
# Inputs
#   HDEV_rows_<cycle>_base.csv   from harness v1.7 (T19): 1 Hz rows incl. v, a, mode, P_wheel, P_aux
#   BEV_E2_<cycle>_ReferenceLoad_1Hz.vmod   Bob's VECTO 5.1.6-RC run
#   E2 component files from mohgsaad-art/VECTO (IEPC-experiments), Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2
#
# Rules used (VECTO source, file + line):
#   gearbox/axle loss: Delaunay map over (input speed, input torque - loss), looked up at
#       (omega_out*ratio, T_out/ratio)                               TransmissionLossMap.cs 77, 94
#   motor: Delaunay map of electric power over (torque, speed)       EfficiencyMap.cs 23
#   2 identical motors, ADC ratio 2.0                                BatteryElectricVehicle.vveh
#   gear ratios 3.86 / 1.93, axle 2.59                               AMT.vgbx
#   r_dyn = 0.867 m * 3.05 / (2 pi)                                  Wheels.csv 265/70 R19.5, Wheels.cs 74
#   regen cap = motor generating torque curve (.vemp T_drag column) per motor
# Tags: [ASSUMP] test/HDEV choice, [VECTO] read from VECTO, [CALC] own arithmetic
# =====================================================================================
import sys, os, math
import numpy as np
import pandas as pd
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
E2 = os.path.join(BASE, "vecto/Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/")
HDEV = os.path.join(BASE, "hdev_out/")
VMOD = {"RegionalDelivery": os.path.join(BASE, "data/RD.vmod"), "UrbanDelivery": os.path.join(BASE, "data/UD.vmod")}

I_AXLE, I_GEAR, I_ADC, N_EM = 2.59, {1: 3.86, 2: 1.93}, 2.0, 2            # [VECTO] AMT.vgbx, .vveh
R_DYN = 0.867 * 3.05 / (2 * math.pi)                                       # [VECTO] Wheels.csv / Wheels.cs 74
RPM = 60 / (2 * math.pi)
V_NO_REGEN = 5 / 3.6                                                       # HDEV rule (Constants.cs 323)
REFS = {"MAN eTGL (OEM, 11.99 t)": 0.69, "Danish fit at 11.99 t": 0.796, "Liimatainen fit at 11.99 t": 0.855}

# ---------- maps ----------
def csv(f):
    return np.genfromtxt(E2 + f, delimiter=",", skip_header=1)

class Loss:
    """gearbox/axle loss map, VECTO way: points (n_in, T_in - loss) -> loss  [TransmissionLossMap.cs 77]"""
    def __init__(self, f, ratio):
        m = csv(f); self.ratio = ratio
        pts = np.c_[m[:, 0], m[:, 1] - m[:, 2]]
        self.lin = LinearNDInterpolator(pts, m[:, 2]); self.near = NearestNDInterpolator(pts, m[:, 2])
        self.n_max = m[:, 0].max()
    def input_side(self, n_out_rpm, T_out):
        """returns n_in, T_in for a given output speed/torque  [TransmissionLossMap.cs 94]"""
        n_in, T = n_out_rpm * self.ratio, T_out / self.ratio
        loss = self.lin(n_in, T)
        bad = np.isnan(loss)                       # outside the map: VECTO extrapolates; here nearest point [ASSUMP]
        loss[bad] = self.near(n_in[bad], T[bad])
        self.extrap = int(bad.sum())
        return n_in, T + loss, loss

AXLE = Loss("Axle_4x2_Tractor.vtlm", I_AXLE)
GEAR = {1: Loss("Gear_1.vtlm", I_GEAR[1]), 2: Loss("Gear_2.vtlm", I_GEAR[2])}
em = csv("GenericMap_125kW_485Nm.vemo")                                    # per motor: n, T (+ = drive), P_el kW (+ = drawn)
EM_LIN = LinearNDInterpolator(em[:, :2], em[:, 2] * 1000); EM_NEAR = NearestNDInterpolator(em[:, :2], em[:, 2] * 1000)
fld = csv("GenericEMotor_125kW_485Nm.vemp"); fld = fld[np.argsort(fld[:, 0])]
def em_el(n_rpm, T_per_motor):
    p = EM_LIN(n_rpm, T_per_motor); bad = np.isnan(p); p[bad] = EM_NEAR(n_rpm[bad], T_per_motor[bad]); return p
def t_gen_max(n_rpm):   return np.interp(n_rpm, fld[:, 0], np.abs(fld[:, 2]))   # per motor, magnitude
def t_drive_max(n_rpm): return np.interp(n_rpm, fld[:, 0], fld[:, 1])

def chain(v_ms, P_axle_out, gear, regen_cap):
    """wheel side -> electric. P_axle_out = power the axle must deliver to the wheels [W] (+ drive, - braking).
    Returns dict of per-row W: axle_loss, gbx_loss, em_loss, P_el (+ drawn, - recovered), brake_extra."""
    n = len(v_ms); out = {k: np.zeros(n) for k in ["axle_loss", "gbx_loss", "em_loss", "P_el", "brake_extra", "over_drive"]}
    w = v_ms / R_DYN
    on = (w > 1e-3) & (gear > 0) & (P_axle_out != 0)
    T_w = np.zeros(n); T_w[on] = P_axle_out[on] / w[on]
    n_ax, T_ax, l_ax = AXLE.input_side(w[on] * RPM, T_w[on])
    T_gb = np.zeros(on.sum()); n_gb = np.zeros(on.sum()); l_gb = np.zeros(on.sum())
    g = gear[on]
    for k, L in GEAR.items():
        s = g == k
        if s.any():
            n_gb[s], T_gb[s], l_gb[s] = L.input_side(n_ax[s], T_ax[s])
    n_em = n_gb * I_ADC; T_em = T_gb / I_ADC / N_EM                        # per motor; ADC loss 0 as in the .vmod [ASSUMP, see notes]
    over = T_em > t_drive_max(n_em)                                         # driver asks more than the motors can give
    brake = np.zeros(on.sum())
    if regen_cap:
        cap = -t_gen_max(n_em)
        low = T_em < cap
        # torque the motors cannot take goes to the friction brakes; move it back to the wheel side (approx. via ratios) [ASSUMP]
        brake[low] = (cap[low] - T_em[low]) * N_EM * I_ADC * n_em[low] / I_ADC / RPM
        T_em = np.maximum(T_em, cap)
    P_el = em_el(n_em, T_em) * N_EM
    P_mech = T_em * N_EM * n_em / RPM
    out["axle_loss"][on] = l_ax * n_ax / RPM; out["gbx_loss"][on] = l_gb * n_gb / RPM
    out["em_loss"][on] = P_el - P_mech; out["P_el"][on] = P_el; out["brake_extra"][on] = brake
    out["over_drive"][on] = over
    return out

def kwh(x): return float(np.sum(x) / 3.6e6)

def read_vmod(p):
    v = pd.read_csv(p, skiprows=1, encoding="utf-8-sig")
    v = v[~v.iloc[:, 0].astype(str).str.startswith("#")].apply(pd.to_numeric, errors="coerce").reset_index(drop=True)
    return v

# ---------- STEP 1: check our map use on VECTO's own rows ----------
print("STEP 1: maps applied to VECTO's own 1 Hz rows (same speed, gear, axle-output power) vs VECTO's columns")
rows1 = []
for c, p in VMOD.items():
    v = read_vmod(p)
    P_axle_out = ((v["P_axle_in [kW]"] - v["P_axle_loss [kW]"]) * 1000).to_numpy()
    r = chain((v["v_act [km/h]"] / 3.6).to_numpy(), P_axle_out, v["Gear [-]"].to_numpy().astype(int), regen_cap=False)
    km = v["dist [m]"].iloc[-1] / 1000
    for lab, ours, theirs in [("axle loss", kwh(r["axle_loss"]), v["P_axle_loss [kW]"].sum() / 3600),
                              ("gearbox loss", kwh(r["gbx_loss"]), v["P_gbx_loss [kW]"].sum() / 3600),
                              ("motor loss", kwh(r["em_loss"]), v["P_E2-em_loss [kW]"].sum() / 3600),
                              ("motor electric net", kwh(r["P_el"]), -v["P_E2-em_el [kW]"].sum() / 3600)]:
        rows1.append(dict(cycle=c, part=lab, VECTO_kWh=theirs, maps_kWh=ours, diff_pct=(ours / theirs - 1) * 100))
print(pd.DataFrame(rows1).round(3).to_string(index=False))

# ---------- STEP 2: HDEV rows + maps (+ regen cap), gear from VECTO by distance ----------
print("\nSTEP 2: HDEV rows with loss maps; gear taken from VECTO by distance (test only)")
rows2, parts = [], []
for c, p in VMOD.items():
    v = read_vmod(p); h = pd.read_csv(HDEV + f"HDEV_rows_{c}_base.csv")
    km = h.s_m.iloc[-1] / 1000
    vg = v[v["Gear [-]"] > 0]                                              # gear 0 = standing / shifting -> nearest driving gear [ASSUMP]
    gear = vg["Gear [-]"].to_numpy()[np.clip(np.searchsorted(vg["dist [m]"].to_numpy(), h.s_m.to_numpy()), 0, len(vg) - 1)].astype(int)
    v_avg = np.maximum(h.v_kmh.to_numpy() / 3.6 + h.a.to_numpy() / 2, 0)  # HDEV power uses step-average speed
    mode = h["mode"].to_numpy(); Pw = h.P_wheel_W.to_numpy()
    use = (mode != 0) & (mode != 3) & ~((mode == 4) & (h.v_kmh.to_numpy() / 3.6 <= V_NO_REGEN))   # same on/off rules as consumption_engine
    Pw_used = np.where(use, Pw, 0.0)
    aux = kwh(h.P_aux_W)
    base = kwh(h.P_trac_W) + aux
    res = {"HDEV now (0.95/0.95/0.98)": base}
    for lab, cap in [("maps, no regen cap", False), ("maps + motor regen cap", True)]:
        r = chain(v_avg, Pw_used, gear, cap)
        res[lab] = kwh(r["P_el"]) + aux
        if cap:
            regen = -kwh(np.minimum(r["P_el"], 0)); brake_wheel = -kwh(np.minimum(Pw_used, 0))
            parts.append(dict(cycle=c, axle_loss=kwh(r["axle_loss"]), gbx_loss=kwh(r["gbx_loss"]), em_loss=kwh(r["em_loss"]),
                              regen_el=regen, regen_share_pct=regen / max(-kwh(np.minimum(Pw, 0)), 1e-9) * 100,
                              cap_hit_rows=int((r["brake_extra"] > 0).sum()), over_drive_rows=int(r["over_drive"].sum()),
                              VECTO_axle=v["P_axle_loss [kW]"].sum() / 3600, VECTO_gbx=v["P_gbx_loss [kW]"].sum() / 3600,
                              VECTO_em=v["P_E2-em_loss [kW]"].sum() / 3600))
    vecto = -v["P_REESS_T [kW]"].sum() / 3600 / (v["dist [m]"].iloc[-1] / 1000)
    for lab, e in res.items():
        rows2.append(dict(cycle=c, case=lab, kWh_km=e / km, vs_VECTO_pct=(e / km / vecto - 1) * 100,
                          vs_MAN_pct=(e / km / 0.69 - 1) * 100))
    rows2.append(dict(cycle=c, case="VECTO (battery terminals)", kWh_km=vecto, vs_VECTO_pct=0.0, vs_MAN_pct=(vecto / 0.69 - 1) * 100))
print(pd.DataFrame(rows2).round(3).to_string(index=False))
print("\nloss split, HDEV rows with maps + cap vs VECTO [kWh/trip]")
print(pd.DataFrame(parts).round(2).to_string(index=False))
print("\nreference points (kWh/km):", REFS)
print(f"extrapolated points (outside map, nearest used): axle {AXLE.extrap}, gear2 {GEAR[2].extrap}")
