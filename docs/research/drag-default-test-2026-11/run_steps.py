"""Steps 2 + 3: driver model with drag (V0/V1/V2) and kWh/km through Chains S and E.

TEST-ONLY. No engine file touched. Driver = test-only _driver_dragtable copy of the
code of record. Energy = repo force_engine + _chain (sourced ports of the 22 Oct maps
tests). VECTO .vmod/.vsum for the reference.

Variants:
  V0 = no drag (drag_F all 0)
  V1 = E2 drag table (Step 1, from the component files)
  V2 = corrected EU standard-value drag (wheel-side axle 70+20*i)

Run:
  cd docs/research/drag-default-test-2026-11
  VECTO_SRC=/path/to/VECTO python run_steps.py
"""
import csv
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from tests.driver_model import _vmod as VM
from src.engine.force_engine import force_engine

import _e2_drag as E2
import _chain as C
from _driver_dragtable import driver_model

# ---- aux: constant electric W per mission, read directly from the VECTO .vmod
# P_aux_el column [VMOD] (ES 1000 + AC/HVAC 250 + PS 200 + STP 20 + COND ~513 = ~1983 W
# Regional; ~1769 W Urban). This is the E2 reference truck's own aux, so it is the right
# like-for-like constant. Municipal has no group-2 .vmod -> use the Urban value + PTO.
AUX_W = {
    "RegionalDelivery": 1983.0,
    "UrbanDelivery":    1769.0,
    "MunicipalUtility": 1769.0,     # [ASSUMPTION] Urban aux (no group-2 Municipal .vmod)
}
PTO_MUNICIPAL_W = 2000.0        # [ASSUMPTION/ILLUS] 2 kW always-on refuse PTO (22 Oct S5)

V_NO_REGEN = 5 / 3.6

# masses [VECTO/close-out]: empty 6570; reference +3019.59; low +603.92 (Regional/Urban)
LOADINGS = {
    ("RegionalDelivery", "reference"): 3019.5882,
    ("RegionalDelivery", "low"): 603.9176,
    ("UrbanDelivery", "reference"): 3019.5882,
    ("UrbanDelivery", "low"): 603.9176,
    ("MunicipalUtility", "reference"): 3019.5882,
    ("MunicipalUtility", "low"): 603.9176,
}
RUNFILE = {
    ("RegionalDelivery", "reference"): "BEV_E2_RegionalDelivery_ReferenceLoad_1Hz",
    ("RegionalDelivery", "low"): "BEV_E2_RegionalDelivery_LowLoading_1Hz",
    ("UrbanDelivery", "reference"): "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz",
    ("UrbanDelivery", "low"): "BEV_E2_UrbanDelivery_LowLoading_1Hz",
}
VSUM = {"RegionalDelivery": 1.050, "UrbanDelivery": 0.840}     # [VSUM] battery terminals


def vehicle_params(load):
    mass = VV.M_VEHICLE + LOADINGS[("RegionalDelivery", load)]
    return dict(mass=mass, Crr=VV.crr_total_vecto(mass), r_dyn=VV.R_DYN,
                cdxa_v=np.array(VV.CDXA_V), cdxa=np.array(VV.CDXA_REF), rho=VV.RHO_VECTO)


def driver_kwargs(load):
    p = vehicle_params(load)
    return dict(coast_mass=p["mass"], m_red_wheels=VV.M_RED_WHEELS,
                cdxa_v=list(VV.CDXA_V), cdxa=list(VV.CDXA_REF),
                Crr=p["Crr"], rho=VV.RHO_VECTO, g=VV.G)


# ---- drag tables ----
def e2_table():
    v, F, _ = E2.build_drag_table()
    return list(v), list(F)


def std_table():
    """Corrected EU standard-value drag (V2): wheel-side axle 70+20*i, gearbox
    0.005*Tmax_in, motor Annex Xb drag, gear 2. Built with the same outward method as
    the E2 table but with the standard-value component formulas."""
    v_kmh = np.arange(0.0, 131.0, 1.0)
    v = v_kmh / 3.6
    w_wheel = np.maximum(v / C.R_DYN, 1e-9)
    n_axle_in = w_wheel * C.I_AXLE * C.RPM
    w_axle_in = w_wheel * C.I_AXLE
    n_gbx_in = n_axle_in * C.I_GEAR[2]
    w_gbx_in = w_axle_in * C.I_GEAR[2]
    n_motor = n_gbx_in * C.I_ADC
    # motor drag (standard value, Annex Xb App.8 step 7): drag torque per motor at
    # Tn=0.01, wn=1 and 4, linear. Reuse the same coefficients as the std motor eff.
    k = {(2, 0): 0.1, (2, 1): 0.03, (2, 2): 0.03, (1, 0): 0.01, (1, 2): 0.001,
         (0, 0): 0.003, (0, 2): 0.001, (0, 3): 0.001}

    def eff(Tn, Wn):
        pl = sum(c * np.abs(Tn) ** m * np.abs(Wn) ** nn for (m, nn), c in k.items())
        pm = Tn * Wn
        return np.maximum(np.where(Tn > 0, pm / (pm + pl), (pm + pl) / pm) * 0.96, 0)

    wn = n_motor / C.N_RATED
    d1 = (1 - eff(np.array(0.01), np.array(1.0))) * 0.01 * C.T_EM_MAX
    d4 = (1 - eff(np.array(0.01), np.array(4.0))) * 0.01 * C.T_EM_MAX
    T_motor = d1 + (d4 - d1) * (n_motor - C.N_RATED) / (3 * C.N_RATED)
    T_motor = np.abs(T_motor)
    T_drag_gbx_in = C.N_EM * T_motor * C.I_ADC
    em_power = T_drag_gbx_in * w_gbx_in
    # gearbox std loss torque at the drag torque
    td = 0.005 * C.TMAX_IN
    gbx_loss_torque = td + td * n_gbx_in / 1000.0 + 0.04 * np.abs(T_drag_gbx_in)
    gbx_power = gbx_loss_torque * w_gbx_in
    T_axle_in = (T_drag_gbx_in + gbx_loss_torque) * C.I_GEAR[2]
    # axle std loss WHEEL SIDE: Td0 = 70 + 20*i applied at n_out (wheel), + (1/eta-1)|T_out|
    T_axle_out = T_axle_in * C.I_AXLE
    td0_axle = 70.0 + 20.0 * C.I_AXLE
    axle_loss_torque_out = td0_axle + np.abs(T_axle_out) / 0.98 - np.abs(T_axle_out)
    axle_power = axle_loss_torque_out * w_wheel
    F = (em_power + gbx_power + axle_power) / np.maximum(v, 1e-9)
    return list(v_kmh), list(F)


# ---- driver run + metrics ----
def run_driver(cyc, load, drag):
    s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
    vacc = D.load_vacc()
    kw = driver_kwargs(load)
    kw["drag_v"] = [x / 3.6 for x in drag[0]]        # table in m/s for the variant
    kw["drag_F"] = list(drag[1])
    return driver_model(s, v, stop, grad, *vacc, **kw)


def coast_pct(M):
    return float(np.mean(M == 3) * 100)


def secs_over(V, kmh=85.0):
    return int(np.sum(np.asarray(V) * 3.6 > kmh))


def rms_vs_vecto(S, V, cols):
    dist_v = VM.col(cols, "dist")
    v_v = VM.col(cols, "v_act")
    s_max = min(S[-1], dist_v[-1])
    grid = np.arange(0, s_max, 10.0)
    diff = np.interp(grid, S, V) * 3.6 - np.interp(grid, dist_v, v_v)
    return float(np.sqrt(np.mean(diff ** 2)))


def wheel_power(T, S, V, A, grade, load):
    p = vehicle_params(load)
    dt = np.diff(T, append=T[-1] + 1.0)
    k_lin, k_roll, k_rot, L, v_avg = force_engine(VV.G, p["Crr"], V, A, dt, grade, p["r_dyn"], 0.0)
    cdxa = np.interp(v_avg * 3.6, p["cdxa_v"], p["cdxa"])
    P = p["mass"] * k_lin + p["mass"] * k_roll + k_rot + p["rho"] * cdxa * L
    return P, v_avg, dt


def wheel_energy(T, S, V, A, grade, load):
    P, v_avg, dt = wheel_power(T, S, V, A, grade, load)
    E = P * dt
    return E[E > 0].sum() / 3.6e6, E[E < 0].sum() / 3.6e6


def kwh_per_km(cyc, load, out, chain_kind):
    T, S, V, A, grade, M = out
    P_wheel, v_avg, dt = wheel_power(T, S, V, A, grade, load)
    use = (M != 0) & (M != 3) & ~((M == 4) & (V <= V_NO_REGEN))
    P_use = np.where(use, P_wheel, 0.0)
    axle, gears, emap = C.make_chain(chain_kind)
    r = C.electric_power(v_avg, P_use, use, axle, gears, emap, gear_fixed=2)
    km = S[-1] / 1000.0
    aux_w = AUX_W[cyc] + (PTO_MUNICIPAL_W if cyc == "MunicipalUtility" else 0.0)
    E_batt = float(np.sum(r["P_el"] * dt) / 3.6e6) + aux_w * len(M) / 3.6e6
    E_regen = -float(np.sum(np.minimum(r["P_el"], 0) * dt) / 3.6e6)
    return dict(kwh_km=E_batt / km, km=km, E_batt=E_batt, E_regen=E_regen,
                E_axle=float(np.sum(r["axle_loss"] * dt) / 3.6e6),
                E_gbx=float(np.sum(r["gbx_loss"] * dt) / 3.6e6),
                E_motor=float(np.sum(r["em_loss"] * dt) / 3.6e6))


def main():
    runs = VM.run_files()
    v1 = e2_table()
    v2 = std_table()
    v0 = ([0.0, 130.0], [0.0, 0.0])
    drags = {"V0 no drag": v0, "V1 E2 table": v1, "V2 std corrected": v2}

    # ---- Step 3 baseline reproduction (Chain S, no drag) ----
    print("=" * 74)
    print("BASELINE check: Chain S (EU std maps), no drag. Target 22 Oct: Regional 0.947, Urban 0.815")
    print("=" * 74)
    for cyc in ("RegionalDelivery", "UrbanDelivery"):
        out = run_driver(cyc, "reference", v0)
        r = kwh_per_km(cyc, "reference", out, "S")
        print(f"  {cyc:16s} Chain S no-drag = {r['kwh_km']:.3f} kWh/km")

    # ---- Step 2: driver metrics vs VECTO ----
    print("\n" + "=" * 74)
    print("STEP 2: driver model with drag (V0/V1/V2) vs VECTO")
    print("=" * 74)
    step2 = []
    for cyc, load in [("RegionalDelivery", "reference"), ("RegionalDelivery", "low"),
                      ("UrbanDelivery", "reference"), ("UrbanDelivery", "low")]:
        rf = RUNFILE.get((cyc, load))
        cols = VM.load_vmod(runs[rf]) if rf and rf in runs else None
        vc = vo = None
        if cols is not None:
            da = VM.col(cols, "DriverAction").astype(int)
            vv = VM.col(cols, "v_act")
            vc = float(((da == 4) | (da == 2)).mean()) * 100
            vo = int((vv > 85).sum())
        print(f"\n=== {cyc} {load} ===  VECTO coast {vc} %, secs>85 {vo}")
        for name, drag in drags.items():
            out = run_driver(cyc, load, drag)
            T, S, V, A, gr, M = out
            Ep, En = wheel_energy(T, S, V, A, gr, load)
            rms = rms_vs_vecto(S, V, cols) if cols is not None else float("nan")
            row = dict(cycle=cyc, load=load, variant=name,
                       coast_pct=round(coast_pct(M), 2), secs85=secs_over(V),
                       rms_vs_vecto=round(rms, 3), E_trac=round(Ep, 1), E_brake=round(En, 1),
                       vecto_coast=vc, vecto_secs85=vo)
            step2.append(row)
            print(f"  {name:18s} coast {row['coast_pct']:5.2f}%  secs>85 {row['secs85']:4d}  "
                  f"RMS {row['rms_vs_vecto']:5.2f}  E_trac {Ep:6.1f}  E_brake {En:6.1f}")
    _write("step2_driver_metrics.csv", step2)

    # ---- Step 3: kWh/km through both chains ----
    print("\n" + "=" * 74)
    print("STEP 3: kWh/km at battery terminals (aux on). V1 vs V0, vs VECTO .vsum")
    print("=" * 74)
    step3 = []
    cycles = [("RegionalDelivery", "reference"), ("RegionalDelivery", "low"),
              ("UrbanDelivery", "reference"), ("UrbanDelivery", "low"),
              ("MunicipalUtility", "reference")]
    for cyc, load in cycles:
        for chain_kind in ("S", "E"):
            res = {}
            for name, drag in drags.items():
                out = run_driver(cyc, load, drag)
                res[name] = kwh_per_km(cyc, load, out, chain_kind)
            v0k = res["V0 no drag"]["kwh_km"]
            v1k = res["V1 E2 table"]["kwh_km"]
            v2k = res["V2 std corrected"]["kwh_km"]
            vsum = VSUM.get(cyc)
            for name in drags:
                k = res[name]["kwh_km"]
                step3.append(dict(
                    cycle=cyc, load=load, chain=chain_kind, variant=name,
                    kwh_km=round(k, 4),
                    pct_vs_V0=round((k / v0k - 1) * 100, 2),
                    pct_vs_V1=round((k / v1k - 1) * 100, 2),
                    pct_vs_VECTO=round((k / vsum - 1) * 100, 2) if vsum else "",
                    E_regen=round(res[name]["E_regen"], 2),
                ))
            vs = f"{vsum:.3f}" if vsum else "n/a"
            print(f"  {cyc:16s} {load:9s} Chain {chain_kind}: "
                  f"V0 {v0k:.3f}  V1 {v1k:.3f} ({(v1k/v0k-1)*100:+.1f}% vs V0)  "
                  f"V2 {v2k:.3f}  VECTO {vs}")
    _write("step3_kwh_per_km.csv", step3)
    print("\nAux electric W (moving):", {k: round(v) for k, v in AUX_W.items()},
          "(+2000 W PTO on Municipal)")
    print("CSVs written to", _HERE)


def _write(name, rows):
    with open(os.path.join(_HERE, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
