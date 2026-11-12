"""Builds markdown tables for the report from the CSVs written by the run_part_*.py scripts.

Run:  python make_tables.py      -> writes report_tables.md (used by hand when assembling docs/research/force-engine-review-2026-11.md)
"""
import pandas as pd

from _common import *


def md(df, floatfmt=None):
    df = df.copy()
    df.columns = [str(c) for c in df.columns]
    floatfmt = {str(k): v for k, v in (floatfmt or {}).items()}
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                f = (floatfmt or {}).get(c, "{:.4g}")
                cells.append("" if pd.isna(v) else f.format(v))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    out_md = []
    t = pd.read_csv(out("partC_terms.csv"))
    short = {"RegionalDelivery": "Regional", "UrbanDelivery": "Urban", "LongHaul": "LongHaul", "ReferenceLoad": "Ref", "LowLoading": "Low"}
    t["case"] = t.cycle.map(short) + " " + t.load.map(short)

    # C1: energy per term, variant i
    a = t[(t.variant == "i_table") & t.term.isin(["P_roll", "P_air", "P_slope", "P_veh_inertia", "P_wheel_inertia", "P_wheel_in(sum)"])]
    a = a.assign(vecto_pos_kWh=a.vecto_pos, hdev_pos_kWh=a.hdev_pos, d_pos_kWh=a.d_pos_kwh, d_pos_pct=a.d_pos_pct, d_net_kWh=a.d_net_kwh,
                 rms_W=a.rms_W, max_W=a.max_abs_W, flagged=a.n_flagged.astype(str) + "/" + a.n_rows.astype(str))
    out_md.append("### C1. Trip energy per term, HDEV (table CdxA) minus VECTO\n\n" +
                  md(a[["case", "term", "vecto_pos_kWh", "hdev_pos_kWh", "d_pos_kWh", "d_pos_pct", "d_net_kWh", "rms_W", "max_W", "flagged"]],
                     {"d_pos_kWh": "{:+.4f}", "d_pos_pct": "{:+.4f}", "d_net_kWh": "{:+.4f}", "vecto_pos_kWh": "{:.3f}", "hdev_pos_kWh": "{:.3f}", "rms_W": "{:.1f}", "max_W": "{:.0f}"}))

    # C2: variant ii (VECTO CdxA) for P_air and total
    b = t[t.term.isin(["P_air", "P_wheel_in(sum)"])].pivot_table(index=["case", "term"], columns="variant", values="d_pos_pct").reset_index()
    out_md.append("### C2. CdxA variants (positive-part error, %)\n\n" + md(b, {"i_table": "{:+.4f}", "ii_vecto_cdxa": "{:+.4f}"}))

    cd = t[(t.variant == "i_table") & (t.term == "P_air")][["case", "cdxa_rms_moving", "cdxa_max_moving"]]
    out_md.append("### C3. CdxA_eff table vs VECTO's column (moving rows, m2)\n\n" + md(cd, {"cdxa_rms_moving": "{:.4f}", "cdxa_max_moving": "{:.4f}"}))

    # causes isolated: P_wheel_in(sum) positive error by variant
    k = pd.read_csv(out("partC_causes_isolated.csv"))
    k["case"] = k.cycle.map(short) + " " + k.load.map(short)
    kk = k[k.term == "P_wheel_in(sum)"].pivot_table(index="variant", columns="case", values="d_pos_pct", sort=False).reset_index()
    out_md.append("### C4. Cause isolation: error of positive wheel energy [%] when one assumption is changed\n\n" + md(kk, {c: "{:+.4f}" for c in kk.columns[1:]}))

    # flagged classes
    c = pd.read_csv(out("partC_flagged_rows_classes.csv"))
    c = c[c.load == "ReferenceLoad"]
    pv = c.pivot_table(index=["cycle", "term"], columns="cause_class", values="n_flagged", aggfunc="sum").reset_index()
    out_md.append("### C5. Flagged rows (|diff| > 0.1 kW and > 1 % of the row value), ReferenceLoad: count by cause class\n\n" + md(pv))

    # gate 3
    g = pd.read_csv(out("partC_gate3_identity.csv"))
    out_md.append("### Gate 3. VECTO identity residuals (W)\n\n" + md(g[["cycle", "load", "n_rows", "max_abs_W_trac_identity", "rms_W_trac_identity", "max_abs_W_wheel_identity", "rms_W_wheel_identity"]]))

    # D
    d = pd.read_csv(out("partD_driver_vs_force_split.csv"))
    d["case"] = d.cycle.map(short) + " " + d.load.map(short)
    dd = d[(d.part == "pos") & d.term.isin(["P_roll", "P_air", "P_slope", "P_wheel_inertia", "P_wheel"])]
    out_md.append("### D4. Driver split, positive part: error vs VECTO in % (total = HDEV driver + force_engine; force only = VECTO trace + force_engine)\n\n" +
                  md(dd[["case", "term", "vecto_kWh", "hdev_driver_force_kWh", "err_total_pct", "err_force_only_pct", "driver_share_kWh"]],
                     {"err_total_pct": "{:+.3f}", "err_force_only_pct": "{:+.4f}", "driver_share_kWh": "{:+.3f}", "vecto_kWh": "{:.3f}", "hdev_driver_force_kWh": "{:.3f}"}))
    r = pd.read_csv(out("partD_coast_rows_residual.csv"))
    out_md.append("### D2. Coast-row residual (kWh)\n\n" + md(r.T.reset_index().rename(columns={"index": "item", 0: "Regional", 1: "Urban", 2: "LongHaul"}) if False else r))
    out_md.append("### D3. Stop-arrival rows\n\n" + md(pd.read_csv(out("partD_stop_arrival_rows.csv"))))
    out_md.append("### D standing rows\n\n" + md(pd.read_csv(out("partD_standing_rows.csv"))))

    # E
    e = pd.read_csv(out("partE_timestep_energy.csv"))
    ee = e[e.term.isin(["P_roll", "P_air", "P_slope", "P_veh_inertia", "P_wheel"])].pivot_table(index=["cycle", "term"], columns="dt", values="pos_kWh").reset_index()
    out_md.append("### E1. Positive energy per term (kWh) vs time step\n\n" + md(ee, {c: "{:.3f}" for c in ee.columns[2:]}))
    ee2 = e[e.term == "P_wheel"][["cycle", "dt", "rows", "pos_kWh", "neg_kWh", "pos_vs_dt0p25_pct", "coast_pct"]]
    out_md.append("### E2. Positive wheel energy vs dt\n\n" + md(ee2, {"pos_kWh": "{:.3f}", "neg_kWh": "{:.3f}", "pos_vs_dt0p25_pct": "{:+.3f}", "coast_pct": "{:.2f}"}))

    # F
    f = pd.read_csv(out("partF_effects_wheel_energy.csv"))
    ff = f[~f.item.str.startswith(("F4", "F7"))][["item", "cycle", "scenario", "dE_pos_kWh", "dE_pos_pct", "tag"]]
    out_md.append("### F (excluding density and grade noise)\n\n" + md(ff, {"dE_pos_kWh": "{:+.3f}", "dE_pos_pct": "{:+.3f}"}))
    f4 = f[f.item.str.startswith("F4") & (f.cycle == "RegionalDelivery")][["item", "scenario", "dE_pos_kWh", "dE_pos_pct", "note"]]
    out_md.append("### F4 density, Regional\n\n" + md(f4, {"dE_pos_kWh": "{:+.3f}", "dE_pos_pct": "{:+.3f}"}))
    f7 = f[f.item.str.startswith("F7")][["cycle", "scenario", "dE_pos_kWh", "dE_pos_pct", "note"]]
    out_md.append("### F7 grade noise\n\n" + md(f7, {"dE_pos_kWh": "{:+.3f}", "dE_pos_pct": "{:+.3f}"}))
    open(out("report_tables.md"), "w").write("\n\n".join(out_md) + "\n")
    print("wrote", os.path.relpath(out("report_tables.md"), REPO))


if __name__ == "__main__":
    main()
