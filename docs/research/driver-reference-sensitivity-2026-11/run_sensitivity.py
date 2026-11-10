"""What does the driver's fixed reference vehicle cost?  (10 Nov 2026)

HDEV runs driver_model ONCE per route at a fixed reference vehicle (coast mass, rho = 1.188,
CdxA at declaration wind). The energy step then uses the true mass / temperature / wind.
This script measures how much kWh/km (battery terminals) changes because of that.

For every case the SAME energy step is applied to
  A  reference driver (coast_mass = m_ref, rho = 1.188, cdxa = declaration wind)
  B  matched driver   (all three coasting inputs = the case values)   <- "truth"
  C  no-coasting driver (coast_mass = None)
  B_mass / B_rho / B_cdxa : only that one coasting input at the case value, rest at reference
Error = (A - B) / B * 100 %.

Run:  VECTO_SRC=/path/to/VECTO python run_sensitivity.py
Writes results_one_factor.csv, results_corners.csv, timing.csv, gate.csv, report_tables.md
next to this file. Nothing outside this folder is written or edited.

Sources (file: line) for the constants re-used here:
  docs/research/vecto/hdev_test_harness_v1.7.py  55 P_AIR,R_AIR; 61 RHO_VECTO; 63 V_DECL,H_DECL,HELLMANN;
      95-101 crr_total_vecto, crr_eff, CRR_EFF; 213-214 W1_DECL/CDXA_REF; 215 T_VECTO_EQ; 69 tpmlm;
      206-211 cdxa_table (dh = height/10, 10 deg step; called with beta_limit None at line 213)
  tests/driver_model/_vecto_vehicle.py : the same constants, transcribed from the harness
  docs/research/drag-default-test-2026-11/run_steps.py : AUX_W 41, LOADINGS 51, e2_table 82,
      wheel_power 157, kwh_per_km 172
"""
import csv
import importlib.util
import os
import platform
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD = os.path.join(os.path.dirname(HERE), "drag-default-test-2026-11")
for p in (REPO, OLD):
    if p not in sys.path:
        sys.path.insert(0, p)

from tests.driver_model import _vecto_data as D          # noqa: E402
from tests.driver_model import _vecto_vehicle as VV      # noqa: E402
from src.engine.force_engine import force_engine         # noqa: E402
from src.engine.crosswind_engine import crosswind_engine  # noqa: E402
import run_steps as RS                                    # noqa: E402  (original driver, unchanged)
ORIG_DRIVER = RS.driver_model
import _chain as C                                        # noqa: E402

# the edited driver copy (section 4) is loaded under its own name; run_steps keeps the original
_spec = importlib.util.spec_from_file_location("driver_edited", os.path.join(HERE, "_driver_dragtable.py"))
DRV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DRV)

# ------------------------------------------------------------------ constants
P_AIR, R_AIR = 101325.0, 287.05                      # harness line 55
RHO_VECTO = VV.RHO_VECTO                             # 1.188, harness line 61 / DeclarationData.cs 74
T_REF = P_AIR / (R_AIR * RHO_VECTO) - 273.15         # harness line 215 (T_VECTO_EQ)
WIND_REF = VV.V_DECL                                 # 3 m/s at H_DECL = 4 m
H_REF = VV.H_DECL
BETA_LIMIT = None                                    # harness line 213 (cdxa_table(..., None)): VECTO yaw behaviour, no clamp
M_VEH = VV.M_VEHICLE
PAYLOAD_REF = RS.LOADINGS[("RegionalDelivery", "reference")]     # 3019.5882
M_REF = M_VEH + PAYLOAD_REF
TPMLM = VV.TPMLM
CRR_EFF = VV.crr_eff()
BETA = VV.BETA
CDXA_V = list(VV.CDXA_V)
V_NO_REGEN = RS.V_NO_REGEN

CYCLES = ["RegionalDelivery", "UrbanDelivery"]
GATE = {"RegionalDelivery": 0.9749, "UrbanDelivery": 0.8502}
GATE_TOL = 0.0005


def _vveh_check():
    """TPMLM from the .vveh (MassMax) must equal the harness value."""
    path = os.path.join(C.E2, "BatteryElectricVehicle.vveh")
    with open(path, encoding="latin-1") as fh:
        for line in fh:
            if '"MassMax"' in line:
                mm = float(line.split(":")[1].strip().rstrip(",")) * 1000.0
                return mm, path
    raise RuntimeError("MassMax not found in " + path)


# ------------------------------------------------------------------ inputs
_V1 = RS.e2_table()                                   # variant V1: E2 drag table (km/h, N)
DRAG_V = [x / 3.6 for x in _V1[0]]
DRAG_F = list(_V1[1])
VACC = D.load_vacc()
_CYC = {}
for _c in CYCLES:
    _CYC[_c] = D.load_cycle(D.list_cycles()[_c])      # (s, v, grad, stop)
AXLE, GEARS, EMAP = C.make_chain("S")                 # Chain S (EU standard-value maps)

_cdxa_cache = {}


def cdxa_table(wind):
    """CdxA(v) = CdxA0 * W1 + W2 at the given wind (m/s at 4 m), via crosswind_engine, same call as harness cdxa_table."""
    key = float(wind)
    if key not in _cdxa_cache:
        a1, a2, a3 = VV.A123
        W1, W2 = crosswind_engine(VV.VEH_HEIGHT, np.asarray([key]), H_REF, a1, a2, a3, VV.HELLMANN,
                                  VV.VEH_HEIGHT / 10, 10, VV.CDXA_V, BETA_LIMIT)
        _cdxa_cache[key] = VV.CDXA0 * np.asarray(W1)[0] + np.asarray(W2)[0]
    return _cdxa_cache[key]


def rho_of(T):
    return P_AIR / (R_AIR * (T + 273.15))


# ------------------------------------------------------------------ driver
_drv_cache = {}


def run_driver(cyc, coast_mass, rho, wind, driver=None, cache=True):
    """One driver_model call. coast_mass None = no coasting. Crr (driver form) = crr_total_vecto(coast_mass)."""
    drv = driver or DRV.driver_model
    key = (cyc, None if coast_mass is None else round(float(coast_mass), 6), round(float(rho), 9),
           round(float(wind), 6), id(drv))
    if cache and key in _drv_cache:
        return _drv_cache[key]
    s, v, grad, stop = _CYC[cyc]
    kw = dict(m_red_wheels=VV.M_RED_WHEELS, g=VV.G, drag_v=DRAG_V, drag_F=DRAG_F)
    if coast_mass is None:
        out = drv(s, v, stop, grad, *VACC, coast_mass=None, rho=rho, **kw)
    else:
        out = drv(s, v, stop, grad, *VACC, coast_mass=coast_mass, cdxa_v=CDXA_V, cdxa=list(cdxa_table(wind)),
                  Crr=VV.crr_total_vecto(coast_mass), rho=rho, **kw)
    if cache:
        _drv_cache[key] = out
    return out


# ------------------------------------------------------------------ energy step (same for A, B, C)
def energy_step(cyc, out, mass, T_c, wind):
    """force_engine + wheel power + Chain S + aux -> metrics. True mass, true rho(T), true wind.
    Rolling: force_engine with CRR_EFF, P_roll = mass**BETA * k_roll (harness consumption form).
    theta_red = 0 as in run_steps.wheel_power (wheel inertia is only in the driver, via m_red_wheels)."""
    Tm, S, V, A, grade, M = out
    dt = np.diff(Tm, append=Tm[-1] + 1.0)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(VV.G, CRR_EFF, V, A, dt, grade, VV.R_DYN, 0.0)
    rho_row = np.full(len(V), rho_of(T_c))
    cdxa = np.interp(v_avg * 3.6, CDXA_V, cdxa_table(wind))
    P_wheel = mass * k_lin + mass ** BETA * k_roll + k_rot + rho_row * cdxa * L
    use = (M != 0) & (M != 3) & ~((M == 4) & (V <= V_NO_REGEN))
    P_use = np.where(use, P_wheel, 0.0)
    r = C.electric_power(v_avg, P_use, use, AXLE, GEARS, EMAP, gear_fixed=2)
    km = S[-1] / 1000.0
    E_batt = float(np.sum(r["P_el"] * dt) / 3.6e6) + RS.AUX_W[cyc] * len(M) / 3.6e6
    E_regen = -float(np.sum(np.minimum(r["P_el"], 0) * dt) / 3.6e6)
    mov = M != 0
    nmov = max(int(mov.sum()), 1)
    return dict(kwh_km=E_batt / km, km=km, regen_kwh=E_regen,
                coast_pct=float((M == 3).sum()) / nmov * 100, brake_pct=float((M == 4).sum()) / nmov * 100,
                trip_s=float(len(M)))


def max_dv_kmh(outX, outB):
    """max |speed difference| on a 10 m distance grid (same grid idea as run_steps.rms_vs_vecto)."""
    SX, VX = outX[1], outX[2]
    SB, VB = outB[1], outB[2]
    smax = min(SX[-1], SB[-1])
    grid = np.arange(0, smax, 10.0)
    return float(np.max(np.abs(np.interp(grid, SX, VX) * 3.6 - np.interp(grid, SB, VB) * 3.6)))


# ------------------------------------------------------------------ a case
def run_case(cyc, mass, T_c, wind):
    rho_c = rho_of(T_c)
    ref = dict(mass=M_REF, rho=RHO_VECTO, wind=WIND_REF)
    outA = run_driver(cyc, M_REF, RHO_VECTO, WIND_REF)
    outB = run_driver(cyc, mass, rho_c, wind)
    outC = run_driver(cyc, None, RHO_VECTO, WIND_REF)
    outBm = run_driver(cyc, mass, RHO_VECTO, WIND_REF)
    outBr = run_driver(cyc, M_REF, rho_c, WIND_REF)
    outBc = run_driver(cyc, M_REF, RHO_VECTO, wind)
    res = {}
    for name, o in (("A", outA), ("B", outB), ("C", outC), ("Bmass", outBm), ("Brho", outBr), ("Bcdxa", outBc)):
        m = energy_step(cyc, o, mass, T_c, wind)
        m["maxdv"] = max_dv_kmh(o, outB)
        res[name] = m
    kB = res["B"]["kwh_km"]
    row = dict(cycle=cyc, mass_kg=round(mass, 4), temp_C=round(T_c, 3), wind_mps=wind)
    for n in ("A", "B", "C", "Bmass", "Brho", "Bcdxa"):
        row["kwh_" + n] = round(res[n]["kwh_km"], 5)
    row["err_A_vs_B_pct"] = round((res["A"]["kwh_km"] - kB) / kB * 100, 4)
    for n in ("Bmass", "Brho", "Bcdxa"):
        row["err_A_vs_" + n + "_pct"] = round((res["A"]["kwh_km"] - res[n]["kwh_km"]) / res[n]["kwh_km"] * 100, 4)
    errs = {n: abs(row["err_A_vs_" + n + "_pct"]) for n in ("Bmass", "Brho", "Bcdxa")}
    row["main_input"] = "none (reference)" if max(errs.values()) < 5e-5 else \
        {"Bmass": "mass", "Brho": "rho", "Bcdxa": "cdxa"}[max(errs, key=errs.get)]
    row["err_C_vs_B_pct"] = round((res["C"]["kwh_km"] - kB) / kB * 100, 4)
    for n in ("A", "B", "C"):
        row[n + "_coast_pct"] = round(res[n]["coast_pct"], 3)
        row[n + "_brake_pct"] = round(res[n]["brake_pct"], 3)
        row[n + "_regen_kwh"] = round(res[n]["regen_kwh"], 4)
        row[n + "_trip_s"] = int(res[n]["trip_s"])
        row[n + "_maxdv_vs_B_kmh"] = round(res[n]["maxdv"], 4)
        row[n + "_km"] = round(res[n]["km"], 4)
    impossible = []
    if mass < M_VEH - 1e-6:
        impossible.append("below empty mass")
    if mass > TPMLM + 1e-6:
        impossible.append("above TPMLM")
    row["flag"] = ("physically impossible for E2 (" + ", ".join(impossible) + ")") if impossible else ""
    return row


def write_csv(name, rows):
    with open(os.path.join(HERE, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def cpu_name():
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


# ------------------------------------------------------------------ main
def main():
    print("=" * 78)
    mm, vpath = _vveh_check()
    print(f"TPMLM: harness/VV {TPMLM} kg ; .vveh MassMax {mm} kg ({vpath})")
    assert abs(mm - TPMLM) < 1e-6, "TPMLM mismatch"
    print(f"m_ref = {M_VEH} + {PAYLOAD_REF} = {M_REF:.4f} kg ; T_ref = {T_REF:.4f} C ; wind_ref = {WIND_REF} m/s at {H_REF} m")
    print(f"rho(T_ref) = {rho_of(T_REF):.6f} (must be {RHO_VECTO})")
    d_tab = np.max(np.abs(cdxa_table(WIND_REF) - np.asarray(VV.CDXA_REF)))
    print(f"CdxA ref table: crosswind_engine vs tests/driver_model/_vecto_vehicle.CDXA_REF, max |diff| = {d_tab:.3e} m2")

    # ---- gate: run_steps functions, ORIGINAL driver (Chain S, V1, reference load)
    print("\nGATE (run_steps.py functions, original driver, Chain S, V1 E2 table, reference load)")
    gate_rows = []
    for cyc in CYCLES:
        o0 = RS.run_driver(cyc, "reference", _V1)
        g0 = RS.kwh_per_km(cyc, "reference", o0, "S")["kwh_km"]
        ok = abs(g0 - GATE[cyc]) <= GATE_TOL
        # section 4: same run_steps functions, edited driver (monkeypatch only the driver name run_steps calls)
        RS.driver_model = DRV.driver_model
        o1 = RS.run_driver(cyc, "reference", _V1)
        g1 = RS.kwh_per_km(cyc, "reference", o1, "S")["kwh_km"]
        RS.driver_model = ORIG_DRIVER
        print(f"  {cyc:16s} gate {g0:.4f} (target {GATE[cyc]}, tol {GATE_TOL}) {'PASS' if ok else 'FAIL'} | "
              f"edited driver (drag at v) {g1:.4f} ({g1 - g0:+.4f})")
        gate_rows.append(dict(cycle=cyc, target=GATE[cyc], run_steps_original=round(g0, 4), pass_=ok,
                              run_steps_edited_driver=round(g1, 4), delta=round(g1 - g0, 4)))
        if not ok:
            write_csv("gate.csv", gate_rows)
            print("GATE FAILED - stopping, no sensitivity work done.")
            sys.exit(2)
    # my energy step at the reference case vs run_steps (edited driver)
    for cyc in CYCLES:
        m = energy_step(cyc, run_driver(cyc, M_REF, RHO_VECTO, WIND_REF), M_REF, T_REF, WIND_REF)
        r = [g for g in gate_rows if g["cycle"] == cyc][0]
        r["sens_script_ref_case_A"] = round(m["kwh_km"], 4)
        print(f"  {cyc:16s} sensitivity script, reference case, driver A = {m['kwh_km']:.4f} "
              f"(run_steps edited {r['run_steps_edited_driver']:.4f})")
    write_csv("gate.csv", gate_rows)

    # ---- 6a one factor at a time
    masses = [("0.5 x m_ref", 0.5 * M_REF), ("empty", M_VEH), ("m_ref", M_REF), ("TPMLM", TPMLM),
              ("1.5 x m_ref", 1.5 * M_REF)]
    one = []
    for cyc in CYCLES:
        for lab, m in masses:
            r = run_case(cyc, m, T_REF, WIND_REF)
            r = dict(factor="mass", case=lab, **r)
            one.append(r)
        for lab, t in (("-10 C", -10.0), ("T_ref", T_REF), ("+30 C", 30.0)):
            one.append(dict(factor="temperature", case=lab, **run_case(cyc, M_REF, t, WIND_REF)))
        for lab, w in (("0 m/s", 0.0), ("3 m/s", 3.0), ("8 m/s", 8.0)):
            one.append(dict(factor="wind", case=lab, **run_case(cyc, M_REF, T_REF, w)))
    write_csv("results_one_factor.csv", one)

    # ---- 6b corners
    corners = []
    cm = [("0.5 x m_ref", 0.5 * M_REF), ("empty", M_VEH), ("TPMLM", TPMLM), ("1.5 x m_ref", 1.5 * M_REF)]
    for cyc in CYCLES:
        for ml, m in cm:
            for t in (-10.0, 30.0):
                for w in (0.0, 8.0):
                    r = run_case(cyc, m, t, w)
                    corners.append(dict(corner=f"{ml} / {t:+.0f} C / {w:g} m/s", **r))
    write_csv("results_corners.csv", corners)

    # ---- timing
    print("\nTIMING")
    trows = []
    cpu = f"{cpu_name()} ({os.cpu_count()} logical CPUs)"
    sw = f"python {platform.python_version()}, numpy {np.__version__}"
    for cyc in CYCLES:
        s, v, grad, stop = _CYC[cyc]
        kw = dict(coast_mass=M_REF, m_red_wheels=VV.M_RED_WHEELS, cdxa_v=CDXA_V, cdxa=list(cdxa_table(WIND_REF)),
                  Crr=VV.crr_total_vecto(M_REF), rho=RHO_VECTO, g=VV.G, drag_v=DRAG_V, drag_F=DRAG_F)
        ts = []
        for _ in range(5):
            t0 = time.perf_counter()
            out = DRV.driver_model(s, v, stop, grad, *VACC, **kw)
            ts.append(time.perf_counter() - t0)
        trows.append(dict(cycle=cyc, step="driver_model (reference, coasting on)", runs=5,
                          mean_s=round(float(np.mean(ts)), 4), min_s=round(min(ts), 4), max_s=round(max(ts), 4),
                          machine=cpu, software=sw))
        ts = []
        for _ in range(5):
            t0 = time.perf_counter()
            energy_step(cyc, out, M_REF, T_REF, WIND_REF)
            ts.append(time.perf_counter() - t0)
        trows.append(dict(cycle=cyc, step="energy step (force_engine + wheel power + Chain S + aux)", runs=5,
                          mean_s=round(float(np.mean(ts)), 4), min_s=round(min(ts), 4), max_s=round(max(ts), 4),
                          machine=cpu, software=sw))
    write_csv("timing.csv", trows)
    for r in trows:
        print(f"  {r['cycle']:16s} {r['step']:58s} mean {r['mean_s']:.4f} s (min {r['min_s']}, max {r['max_s']})")
    print("  machine:", cpu, "|", sw)

    # ---- markdown tables for the report
    md = []
    for cyc in CYCLES:
        md.append(f"### {cyc}\n")
        md.append("| case | A kWh/km | B kWh/km | error A vs B % | largest single input (err % of A vs B_x: mass / rho / cdxa) | C vs B % | note |")
        md.append("|---|---|---|---|---|---|---|")
        for r in [x for x in one if x["cycle"] == cyc]:
            md.append(f"| {r['factor']}: {r['case']} ({r['mass_kg']:.0f} kg, {r['temp_C']:.1f} C, {r['wind_mps']:g} m/s) "
                      f"| {r['kwh_A']:.4f} | {r['kwh_B']:.4f} | {r['err_A_vs_B_pct']:+.3f} | {r['main_input']} "
                      f"({r['err_A_vs_Bmass_pct']:+.3f} / {r['err_A_vs_Brho_pct']:+.3f} / {r['err_A_vs_Bcdxa_pct']:+.3f}) "
                      f"| {(r['err_C_vs_B_pct']):+.3f} | {r['flag']} |")
        md.append("")
        cs = [x for x in corners if x["cycle"] == cyc]
        w = max(cs, key=lambda x: abs(x["err_A_vs_B_pct"]))
        real = [x for x in cs if not x["flag"]]
        wr = max(real, key=lambda x: abs(x["err_A_vs_B_pct"]))
        md.append(f"Worst corner (all 16): **{w['corner']}** error {w['err_A_vs_B_pct']:+.3f} % "
                  f"(A {w['kwh_A']:.4f}, B {w['kwh_B']:.4f}) {w['flag']}")
        md.append(f"Worst corner among realistic masses (empty, TPMLM): **{wr['corner']}** error {wr['err_A_vs_B_pct']:+.3f} %")
        md.append("")
    with open(os.path.join(HERE, "report_tables.md"), "w") as fh:
        fh.write("\n".join(md))
    print("\n".join(md))
    print("\nWrote CSVs to", HERE)


if __name__ == "__main__":
    main()
