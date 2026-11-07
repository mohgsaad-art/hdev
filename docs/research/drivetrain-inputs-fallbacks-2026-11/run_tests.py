"""Part D fallback tests for drivetrain inputs (3 Nov 2026). TEST-ONLY.

Produces the D1-D6 CSVs in this directory and prints a summary. No engine file is
touched; everything runs the code-of-record driver model + the standard-value
drivetrain (_stdval) + the repo force_engine.

Run:
  cd docs/research/drivetrain-inputs-fallbacks-2026-11
  VECTO_SRC=/path/to/VECTO python run_tests.py

Cycles: RegionalDelivery, UrbanDelivery, MunicipalUtility. Reference load, VECTO E2.
P_aux is set to 0 here on purpose: this study isolates the DRIVETRAIN inputs, so the
kWh/km figures are drivetrain-only and run a little below the 22 Oct full-chain numbers
(which included auxiliaries). The DIRECTION and RELATIVE effects are what matter.
"""
import csv
import os

import numpy as np

import _stdval as S
import _harness as H

OUT = os.path.dirname(os.path.abspath(__file__))
CYCLES = H.CYCLES


def _write_csv(name, rows, fields):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    return path


# ---------------------------------------------------------------- D1 + D2 + D3
def d1_d2_d3():
    """D1 baselines, D2 drag-table fix, D3 axle-formula effect."""
    rows = []
    drag_rows = []
    for axle in ("reg70", "vecto"):
        dt = S.Drivetrain(axle_formula=axle)
        v_old, f_old = dt.drag_table("old")
        v_fix, f_fix = dt.drag_table("fixed")
        # record the drag tables (N vs km/h) for the report
        for vk, nf_old, nf_fix in zip(v_fix * 3.6,
                                      np.interp(v_fix, v_old, f_old), f_fix):
            drag_rows.append(dict(axle=axle, v_kmh=round(float(vk), 1),
                                  drag_N_old=round(float(nf_old), 1),
                                  drag_N_fixed=round(float(nf_fix), 1)))
        for c in CYCLES:
            r_nod = H.battery_kwh_per_km(c, dt, drag=None)
            r_old = H.battery_kwh_per_km(c, dt, drag=(v_old, f_old))
            r_fix = H.battery_kwh_per_km(c, dt, drag=(v_fix, f_fix))
            rows.append(dict(
                axle=axle, cycle=c,
                kwh_km_nodrag=round(r_nod["kwh_km"], 4),
                kwh_km_olddrag=round(r_old["kwh_km"], 4),
                kwh_km_fixeddrag=round(r_fix["kwh_km"], 4),
                coast_nodrag=round(r_nod["coast_pct"], 2),
                coast_olddrag=round(r_old["coast_pct"], 2),
                coast_fixeddrag=round(r_fix["coast_pct"], 2),
                pct_old_vs_nodrag=round((r_old["kwh_km"] / r_nod["kwh_km"] - 1) * 100, 2),
                pct_fixed_vs_nodrag=round((r_fix["kwh_km"] / r_nod["kwh_km"] - 1) * 100, 2),
            ))
    _write_csv("D1_D2_D3_baselines_drag_axle.csv", rows, list(rows[0]))
    _write_csv("D2_drag_tables.csv", drag_rows, list(drag_rows[0]))
    return rows, drag_rows


# -------------------------------------------------------------------- D4 + D6
# Fallback rungs per input (truth = E2 component value). Each entry maps a label to
# the Drivetrain kwarg override. "derived"/"example"/"assumption" rungs are sourced
# in the report. The TRUTH run uses the VECTO axle formula (A1 result).
def fallback_variants():
    truth = dict(axle_formula="vecto")

    def dt(**ov):
        kw = dict(truth)
        kw.update(ov)
        return S.Drivetrain(**kw)

    variants = {
        # Tmax_in: derived (motor*count*adc=1940), half (user only knows 1 motor),
        # double (conservative high), VECTO-example-like low (1000)
        "Tmax_in: truth=derived 1940": dt(),
        "Tmax_in: 1 motor assumed 970": dt(tmax_in=970.0),
        "Tmax_in: conservative x2 3880": dt(tmax_in=3880.0),
        "Tmax_in: low guess 1000": dt(tmax_in=1000.0),
        # gear ratios: truth, single-speed fallback (only top gear), different set
        "gears: truth 3.86/1.93": dt(),
        "gears: single-speed 1.93": dt(i_gear={1: 1.93, 2: 1.93}),
        "gears: single-speed 10.0": dt(i_gear={1: 10.0, 2: 10.0}),
        # axle ratio: truth 2.59, typical-low 2.6 example, high 4.0
        "axle_ratio: truth 2.59": dt(),
        "axle_ratio: example 3.08": dt(i_axle=3.08),
        "axle_ratio: high 4.0": dt(i_axle=4.0),
        # motor count: truth 2, single-motor fallback
        "motor_count: truth 2": dt(),
        "motor_count: 1 motor": dt(n_em=1),
        # ADC ratio: truth 2.0, no ADC (1.0), 3.0
        "adc: truth 2.0": dt(),
        "adc: none 1.0": dt(i_adc=1.0),
        "adc: 3.0": dt(i_adc=3.0),
        # r_dyn: truth 0.4209 (265/70 R19.5), bigger tyre, smaller tyre
        "r_dyn: truth 0.4209": dt(),
        "r_dyn: 315/70 R22.5 ~0.481": dt(r_dyn=0.4807),
        "r_dyn: small ~0.39": dt(r_dyn=0.39),
    }
    return variants


def d4_d6():
    """One-at-a-time sensitivity: swap each input, report kWh/km vs truth, with drag."""
    truth_dt = S.Drivetrain(axle_formula="vecto")
    rows = []
    truth = {}
    for c in CYCLES:
        vt, ft = truth_dt.drag_table("fixed")
        truth[c] = H.battery_kwh_per_km(c, truth_dt, drag=(vt, ft))["kwh_km"]
    for label, dt in fallback_variants().items():
        vt, ft = dt.drag_table("fixed")
        for c in CYCLES:
            r = H.battery_kwh_per_km(c, dt, drag=(vt, ft))
            base = truth[c]
            pct = (r["kwh_km"] / base - 1) * 100
            rows.append(dict(
                input=label.split(":")[0], variant=label, cycle=c,
                kwh_km=round(r["kwh_km"], 4),
                truth_kwh_km=round(base, 4),
                pct_vs_truth=round(pct, 2),
                direction="UNDER" if pct < -0.05 else ("over" if pct > 0.05 else "~equal"),
            ))
    _write_csv("D4_D6_sensitivity.csv", rows, list(rows[0]))
    return rows, truth


# -------------------------------------------------------------------------- D5
def d5(truth):
    """All fallbacks together: fleet owner knows make/model, motor power+torque,
    tyre size only. => derived Tmax_in (motor torque*count*adc, but count & adc are
    themselves fallbacks), single-speed gearbox guess, example axle ratio, r_dyn from
    tyre. Motor count: assume 1 unless stated; ADC: assume none (1.0)."""
    # "knows only make/model + motor power/torque + tyre": we do NOT know count, adc,
    # gears, axle ratio or Tmax_in. Fallback rungs:
    fleet = S.Drivetrain(
        axle_formula="vecto",
        tmax_in=485.0 * 1 * 1.0,        # torque known, count=1 fallback, adc=1.0 fallback
        i_gear={1: 1.93, 2: 1.93},      # single-speed example
        i_axle=3.08,                    # example axle ratio (VECTO-like generic)
        n_em=1,                         # count fallback
        i_adc=1.0,                      # adc fallback
        r_dyn=S.R_DYN,                  # DERIVED from the known tyre size 265/70 R19.5 (correct)
    )
    rows = []
    vt, ft = fleet.drag_table("fixed")
    for c in CYCLES:
        r = H.battery_kwh_per_km(c, fleet, drag=(vt, ft))
        base = truth[c]
        rows.append(dict(cycle=c, kwh_km=round(r["kwh_km"], 4),
                         truth_kwh_km=round(base, 4),
                         pct_vs_truth=round((r["kwh_km"] / base - 1) * 100, 2),
                         direction="UNDER" if r["kwh_km"] < base else "over"))
    _write_csv("D5_all_fallbacks.csv", rows, list(rows[0]))
    return rows


def main():
    print("=" * 72)
    print("Part D fallback tests — drivetrain inputs (3 Nov 2026)")
    print("E2 reference vehicle, reference load, P_aux=0 (drivetrain-only).")
    print("=" * 72)

    print("\n--- D1/D2/D3: baselines, drag-table fix, axle formula ---")
    rows, drag_rows = d1_d2_d3()
    for r in rows:
        print(f"  [{r['axle']:5s}] {r['cycle']:16s} no-drag {r['kwh_km_nodrag']:.3f}  "
              f"old-drag {r['kwh_km_olddrag']:.3f} ({r['pct_old_vs_nodrag']:+.1f}%)  "
              f"fixed-drag {r['kwh_km_fixeddrag']:.3f} ({r['pct_fixed_vs_nodrag']:+.1f}%)  "
              f"coast {r['coast_nodrag']:.1f}->{r['coast_fixeddrag']:.1f}%")
    print("\n  Drag tables (N at the wheel), vecto axle:")
    for d in drag_rows:
        if d["axle"] == "vecto" and int(d["v_kmh"]) in (40, 50, 60, 70, 80, 90):
            print(f"    {d['v_kmh']:5.0f} km/h: old {d['drag_N_old']:7.1f} N  "
                  f"fixed {d['drag_N_fixed']:7.1f} N")

    print("\n--- D4/D6: one-at-a-time sensitivity (with fixed drag) ---")
    srows, truth = d4_d6()
    cur = None
    for r in srows:
        if r["variant"] != cur:
            cur = r["variant"]
        flag = "  <<< UNDERESTIMATES" if r["direction"] == "UNDER" else ""
        print(f"  {r['variant']:32s} {r['cycle']:16s} {r['kwh_km']:.3f}  "
              f"{r['pct_vs_truth']:+6.2f}% vs truth{flag}")

    print("\n--- D5: all fallbacks together (fleet owner minimal knowledge) ---")
    for r in d5(truth):
        flag = "  <<< UNDERESTIMATES" if r["direction"] == "UNDER" else ""
        print(f"  {r['cycle']:16s} {r['kwh_km']:.3f}  truth {r['truth_kwh_km']:.3f}  "
              f"{r['pct_vs_truth']:+6.2f}%{flag}")

    print("\nCSVs written to", OUT)


if __name__ == "__main__":
    main()
