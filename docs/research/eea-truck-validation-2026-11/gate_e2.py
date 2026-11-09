"""Section 4 GATE: reproduce the 3 Nov E2 result with the v2 harness BEFORE any certified
truck. TEST-ONLY.

Runs the v2 chain = hdev_test_module.driver_model (notebook copy) + force_engine + the 3 Nov
_chain.electric_power (Chain E = E2 own maps) + the 3 Nov _e2_drag table, on the VECTO E2
example cycles and masses the 3 Nov matrix used, then compares kWh/km to
docs/research/drag-default-test-2026-11/step3_kwh_per_km.csv (Chain E, V1 E2 table).

Pass rule (section 4 step 3): v2 within 1% of the 3 Nov 'own maps' (Chain E V1) on every cycle.
If it fails, the cause is investigated and (if possible) fixed; otherwise every Job 3 number is
labelled GATE FAILED (per Bob's instruction).
"""
import csv, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hdev_test_module as H

_ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(_ROOT, "drag-default-test-2026-11"))
sys.path.insert(0, os.path.join(_ROOT, "drivetrain-inputs-fallbacks-2026-11"))
import _e2_drag as E2DRAG
import _chain as CHAIN

VSRC = os.environ.get("VECTO_SRC", "/projects/sandbox/VECTO")
G = 9.80665
RHO = 1.188
BETA = 0.9

# E2 example geometry/mass from the 3 Nov close-out (reused via _chain constants)
R_DYN = CHAIN.R_DYN
M_EMPTY = 6570.0                 # close-out: empty mass
LOADINGS = {"reference": 3019.5882, "low": 603.9176}   # close-out loadings

# E2 reference cycles (the 3 Nov matrix used the VECTO test 1 Hz BEV E2 cycles). Those are not
# in the public Resources tree; fall back to the declaration MissionCycles for the same mission
# shape (RegionalDelivery.vdri, UrbanDelivery.vdri). The gate compares the SAME v2 chain run on
# the SAME cycle file the comparison target used; if the 3 Nov target used the 1 Hz test cycle
# we note any cycle-source difference in the report.
CYC = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "MissionCycles")
MISSION_FILE = {"RegionalDelivery": "RegionalDelivery.vdri", "UrbanDelivery": "UrbanDelivery.vdri"}

# aux electric W the 3 Nov matrix used (its E2 .vmod own aux)
AUX_W = {"RegionalDelivery": 1983.0, "UrbanDelivery": 1769.0}


def load_cycle(mission):
    s, v, g, stop = [], [], [], []
    with open(os.path.join(CYC, MISSION_FILE[mission])) as fh:
        for i, ln in enumerate(fh):
            if i == 0:
                continue
            p = ln.strip().split(",")
            if len(p) < 4:
                continue
            s.append(float(p[0])); v.append(float(p[1])); g.append(float(p[2])); stop.append(float(p[3]))
    return s, v, g, stop


def load_vacc():
    vv, aa, dd = [], [], []
    with open(os.path.join(VSRC, "Generic Vehicles", "Declaration Mode", "PEV",
                           "GenericVehicleE2", "Truck.vacc"), encoding="latin-1") as fh:
        for i, ln in enumerate(fh):
            if i == 0:
                continue
            p = ln.strip().split(",")
            if len(p) >= 3:
                vv.append(float(p[0])); aa.append(float(p[1])); dd.append(float(p[2]))
    return vv, aa, dd


# Reproduce the 3 Nov E2 set-up EXACTLY (so the gate tests my v2 driver+force path, not a
# different vehicle set-up): the velocity-dependent crosswind CdxA table and reduced wheel mass
# the 3 Nov used. These come from the repo reference module tests/driver_model/_vecto_vehicle.py
# (VV.CDXA_V/CDXA_REF, VV.M_RED_WHEELS, VV.crr_total_vecto) which is itself sourced from VECTO.
_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, _REPO)
from tests.driver_model import _vecto_vehicle as VV   # noqa: E402

CDXA_V = list(VV.CDXA_V)        # km/h grid (60..130 step 5) [VECTO Constants.cs]
CDXA_REF = list(VV.CDXA_REF)    # crosswind-corrected CdxA m2 per speed [VECTO AirdragDataAdapter]
M_RED_WHEELS = VV.M_RED_WHEELS  # ~220 kg reduced wheel mass (R2)


def run(mission, load):
    mass = M_EMPTY + LOADINGS[load]
    crr = VV.crr_total_vecto(mass)     # plain VECTO rrc_total (used with mass*k_roll below)
    s, v, g, stop = load_cycle(mission)
    vv, va, vd = load_vacc()
    v_kmh, F, _ = E2DRAG.build_drag_table(130.0)
    drag = (v_kmh / 3.6, F)
    # drive with my v2 notebook driver, using the SAME crosswind CdxA table + m_red the 3 Nov used
    T, S, V, A, grade, M = H.driver_model(s, v, stop, g, vv, va, vd,
                                          coast_mass=mass, m_red_wheels=M_RED_WHEELS,
                                          cdxa_v=CDXA_V, cdxa=CDXA_REF, Crr=crr, rho=RHO, g=G,
                                          drag_v=drag[0], drag_F=drag[1], P_max=None)
    dt = np.ones(len(T))
    k_lin, k_roll, k_rot, L, v_avg = H.force_engine(G, crr, V, A, dt, grade, R_DYN, 0.0)
    cdxa_row = np.interp(v_avg * 3.6, CDXA_V, CDXA_REF)   # velocity-dependent CdxA (R10 style)
    # 3 Nov wheel power uses LINEAR mass on the roll term (mass*k_roll) with the plain rrc_total.
    P_wheel = mass * k_lin + mass * k_roll + k_rot + RHO * cdxa_row * L
    use = (M != 0) & (M != 3) & ~((M == 4) & (V <= 5 / 3.6))
    P_use = np.where(use, P_wheel, 0.0)
    axle, gears, emap = CHAIN.make_chain("E")
    res = CHAIN.electric_power(v_avg, P_use, use, axle, gears, emap, gear_fixed=2)
    P_el = res["P_el"]   # 3 Nov sums P_el (incl. negative regen) directly, no nan_to_num needed
    P_batt = P_el + AUX_W[mission]
    km = S[-1] / 1000.0
    E = float(np.sum(P_batt * dt) / 3.6e6)
    return E / km


def main():
    ref = {}
    with open(os.path.join(_ROOT, "drag-default-test-2026-11", "step3_kwh_per_km.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["chain"] == "E" and r["variant"] == "V1 E2 table":
                ref[(r["cycle"], r["load"])] = float(r["kwh_km"])
    rows = []
    worst = 0.0
    for mission in ("RegionalDelivery", "UrbanDelivery"):
        for load in ("reference", "low"):
            v2 = run(mission, load)
            r3 = ref.get((mission, load))
            dpct = 100 * (v2 - r3) / r3 if r3 else float("nan")
            worst = max(worst, abs(dpct))
            rows.append([mission, load, round(v2, 4), round(r3, 4), round(dpct, 2)])
            print("%s %s: v2=%.4f  3Nov ChainE V1=%.4f  diff=%+.2f%%" % (mission, load, v2, r3, dpct))
    passed = worst <= 1.0
    with open(os.path.join(HERE, "gate_e2.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cycle", "load", "v2_kwh_km", "ref_3nov_chainE_V1", "diff_pct"])
        for r in rows:
            w.writerow(r)
        w.writerow([])
        w.writerow(["GATE", "PASS" if passed else "FAIL", "worst_abs_diff_pct", round(worst, 2), ""])
    print("\nGATE:", "PASS" if passed else "FAIL", "(worst |diff| = %.2f%%, threshold 1.0%%)" % worst)
    return passed


if __name__ == "__main__":
    main()
