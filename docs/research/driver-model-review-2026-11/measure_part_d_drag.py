"""Build the VECTO drivetrain coasting-drag table two ways and compare (F3 redo).

(1) From the .vmod Coast/Roll rows: -P_wheel_in / v, per 10 km/h band. Cross-checked
    against P_gbx_in + P_gbx_loss + P_axle_loss (the exact identity).
(2) Independently from the E2 component files at ZERO driver torque in gear 2:
    motor drag curve (GenericDrag_125kW_485Nm.vemd) reflected through EM ratio x gear2 x
    axle, plus gearbox torque loss (Gear_2.vtlm) x axle, plus axle torque loss
    (Axle_4x2_Tractor.vtlm), all / r_dyn.

Reports how close (1) and (2) are. (They are NOT close — (2) underestimates by ~2x;
see the review text for why.)

Needs the VECTO clone at /projects/sandbox/VECTO (component files). If absent, only (1)
is reported.

Run: python docs/research/driver-model-review-2026-11/measure_part_d_drag.py
"""
import os
import sys
import csv
import math
import collections

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model import _vmod as VM

VECTO_E2 = "/projects/sandbox/VECTO/Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2"
R_DYN, AXLE, GEAR2, EM = 0.4209, 2.59, 1.93, 2.0
BANDS = [(40, 50), (50, 60), (60, 70), (70, 80), (80, 90)]


def from_vmod():
    runs = VM.run_files()
    pw_pts = collections.defaultdict(list)
    comp_pts = collections.defaultdict(list)
    for run in ("BEV_E2_RegionalDelivery_ReferenceLoad_1Hz",
                "BEV_E2_UrbanDelivery_ReferenceLoad_1Hz",
                "BEV_E2_LongHaul_ReferenceLoad_1Hz"):
        if run not in runs:
            continue
        c = VM.load_vmod(runs[run])
        v = VM.col(c, "v_act") / 3.6
        da = VM.col(c, "DriverAction").astype(int)
        pw = VM.col(c, "P_wheel_in")

        def g(n):
            try:
                return VM.col(c, n)
            except KeyError:
                return np.zeros_like(v)
        comp = np.abs(g("P_gbx_in")) + np.abs(g("P_gbx_loss")) + np.abs(g("P_axle_loss"))
        m = ((da == 4) | (da == 2)) & (v > 1)
        for vv, fw, fc in zip(v[m] * 3.6, -pw[m] / v[m], comp[m] / v[m]):
            lo = int(vv // 10) * 10
            pw_pts[lo].append(fw)
            comp_pts[lo].append(fc)
    return pw_pts, comp_pts


def from_components():
    """Drag force [N] at the wheel vs speed, from the E2 files at zero torque, gear 2."""
    drag_file = os.path.join(VECTO_E2, "GenericDrag_125kW_485Nm.vemd")
    gbx_file = os.path.join(VECTO_E2, "Gear_2.vtlm")
    axle_file = os.path.join(VECTO_E2, "Axle_4x2_Tractor.vtlm")
    if not os.path.isfile(drag_file):
        return None
    # motor drag curve
    dn, dT = [], []
    for r in csv.reader(open(drag_file, encoding="latin-1")):
        try:
            dn.append(float(r[0])); dT.append(float(r[1]))
        except (ValueError, IndexError):
            continue
    # gearbox loss at input torque ~0 vs input speed
    gsp = collections.defaultdict(list)
    for r in csv.reader(open(gbx_file, encoding="latin-1")):
        try:
            sp, tq, ls = float(r[0]), float(r[1]), float(r[2])
        except (ValueError, IndexError):
            continue
        if abs(tq) < 1:
            gsp[sp].append(ls)
    gn = sorted(gsp); gL = [float(np.mean(gsp[s])) for s in gn]
    # axle loss near zero torque vs input speed
    asp = collections.defaultdict(list)
    for r in csv.reader(open(axle_file, encoding="latin-1")):
        try:
            sp, tq, ls = float(r[0]), float(r[1]), float(r[2])
        except (ValueError, IndexError):
            continue
        if abs(tq) < 30:
            asp[sp].append(ls)
    an = sorted(asp); aL = [float(np.mean(asp[s])) for s in an]

    out = {}
    for lo, hi in BANDS:
        vk = (lo + hi) / 2
        v = vk / 3.6
        n_wheel = v / R_DYN * 60 / (2 * math.pi)
        n_axle_in = n_wheel * AXLE
        n_gbx_in = n_axle_in * GEAR2
        n_motor = n_gbx_in * EM
        Tm = abs(np.interp(n_motor, dn, dT))
        F_motor = Tm * EM * GEAR2 * AXLE / R_DYN
        Tg = float(np.interp(n_gbx_in, gn, gL))
        F_gbx = Tg * AXLE / R_DYN
        Ta = float(np.interp(n_axle_in, an, aL)) if an else 8.0
        F_axle = Ta / R_DYN
        out[lo] = F_motor + F_gbx + F_axle
    return out


def main():
    pw, comp = from_vmod()
    comps = from_components()
    print("VECTO drivetrain coasting drag — two independent builds (F3)\n")
    print(f"  {'band':9s} {'.vmod -Pwheel/v':>16s} {'.vmod comp-sum':>15s} {'E2 files 0-torque':>18s}")
    for lo, hi in BANDS:
        a = np.median(pw[lo]) if pw.get(lo) else float("nan")
        cc = np.median(comp[lo]) if comp.get(lo) else float("nan")
        cf = comps[lo] / 1000 if comps and lo in comps else float("nan")
        n = len(pw.get(lo, []))
        print(f"  {lo}-{hi:<4d} {a:10.2f} kN (n{n:3d}) {cc:10.2f} kN {cf:13.2f} kN")
    print()
    print("Reading: the .vmod -P_wheel_in/v and the .vmod component sum agree (same identity).")
    print("The E2-file zero-torque build is ~2x LOWER — the zero-torque component maps do not")
    print("reproduce VECTO's simulated coast drag (the drag torque itself loads the gearbox,")
    print("and the BEV motor controller's coast behaviour is not the bare drag curve). So the")
    print(".vmod-measured table (1.43-2.05 kN) is the authoritative one for D2.")


if __name__ == "__main__":
    main()
