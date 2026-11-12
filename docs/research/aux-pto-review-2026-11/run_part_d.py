"""Part D: PTO on rows.  Tests the variant consumption_step6_v_pto1nov (reference_copy.py) against
  D1  MunicipalUtility.vdri + the VECTO generic refuse profile on every stop VECTO uses it on
  D2  synthetic cases (all values ILLUSTRATIVE): sweeper, mixed refuse, edge cases
Writes deterministic CSVs.  Timing is in run_part_d_timing.py (machine dependent, not byte-identical between runs).

Run:  python run_part_d.py
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _rows import read_vdri, run_driver_e2, REPO  # noqa: E402
from _scenarios import build_route, VPTOEL_T, VPTOEL_W, VPTOEL_KWH  # noqa: E402
import reference_copy as RC  # noqa: E402
from _load_notebook import NS  # noqa: E402

pto_engine = NS["pto_engine"]
WRITTEN = []
V_NO_REGEN = 5 / 3.6
NONE_T, NONE_W = [0.0], [0.0]        # "no profile" = one point: np.diff -> empty -> zero-length profile (a 2-point [0,1],[0,0] is a 1 s zero profile!)


def out(name, df):
    p = os.path.join(HERE, name)
    df.to_csv(p, index=False, float_format="%.6f")
    WRITTEN.append(p)


def d1_municipal():
    cy = read_vdri("MunicipalUtility")
    pto_flag = cy["pto"] == 1
    n_pto = int(pto_flag.sum())
    pto_dur = 23                                                           # len(stop_1s), from the .vptoel
    stop_final = cy["stop"].copy()
    stop_final[pto_flag] += pto_dur                                        # parser: standing = stop + PTO duration (VECTO DistanceBasedDrivingCycle.cs 218-220)
    is_on = pto_flag.astype(float)
    is_on_, pto_start, stop_1s, drive_1s = pto_engine(stop_final, is_on, VPTOEL_T, VPTOEL_W, NONE_T, NONE_W, 1.0, 1.0)
    T, S, V, A, G, M = run_driver_e2(cy, "ReferenceLoad", stop_override=stop_final)
    pto_row, stop_act, drive_act, ev = RC.consumption_step6_v_pto1nov(S, V, cy["s"], stop_final, is_on_, pto_start, stop_1s, drive_1s, M=M)
    rows = []
    for e in ev:
        assert e["kind"] == "stop_profile"
        i = e["wp"]
        m0 = np.where((M == 0) & (V == 0) & (np.abs(S - cy["s"][i]) <= 1e-3))[0]
        v0 = np.where((V == 0) & (np.abs(S - cy["s"][i]) <= 1e-3))[0]
        rows.append(dict(waypoint=i, s_m=cy["s"][i], vdri_stop_s=cy["stop"][i], final_standing_s=stop_final[i], rows_M0=len(m0), rows_V0=len(v0),
                         idle_before_s=e["k0"] - m0[0], pto_rows=e["k1"] - e["k0"], idle_after_s=m0[-1] + 1 - e["k1"], pto_kWh=e["energy_kWh"]))
    df = pd.DataFrame(rows)
    out("partD1_municipal_per_stop.csv", df)
    assert len(df) == n_pto, (len(df), n_pto)
    # Cond during PTO (VECTO rule c).  HDEV current rule already has Cond on during stop PTO (moving | pto_active).
    cond_W = 550.0                                                         # Cond-Table.csv, Municipal utility (550 W)
    cond_pto_kwh = cond_W * stop_act.sum() / 3.6e6
    summ = [
        ("PTO stops flagged in MunicipalUtility.vdri (PTO column == 1)", n_pto, "[VECTO] vdri"),
        ("PTO profile length [s] (.vptoel t=0..23)", pto_dur, "[VECTO] vptoel"),
        ("stop time in vdri for these stops [s]", float(np.unique(cy["stop"][pto_flag])[0]), "[VECTO] vdri"),
        ("final standing time per PTO stop [s] = stop + PTO", float(np.unique(stop_final[pto_flag])[0]), "[CALC]"),
        ("energy of ONE activation, left-hold [kWh]", VPTOEL_KWH, "[CALC] 5*8.42+4*33.69+14*25.92 kJ"),
        ("PTO energy on rows, all stops [kWh]", float(pto_row.sum() / 3.6e6), "[TEST] step6 variant"),
        ("expected = stops x one activation [kWh]", n_pto * VPTOEL_KWH, "[CALC]"),
        ("difference [kWh]", float(pto_row.sum() / 3.6e6) - n_pto * VPTOEL_KWH, "[TEST]"),
        ("distinct idle_before_s values", str(sorted(set(df.idle_before_s.tolist()))), "[TEST]"),
        ("distinct idle_after_s values", str(sorted(set(df.idle_after_s.tolist()))), "[TEST]"),
        ("rows with V==0 minus rows with M==0 per stop (the accelerating row)", str(sorted(set((df.rows_V0 - df.rows_M0).tolist()))), "[TEST]"),
        ("Cond energy during stop PTO if Cond is ON there (550 W) [kWh]", cond_pto_kwh, "[CALC] Cond-Table + rows with PTO"),
        ("Cond energy during stop PTO if Cond is OFF there [kWh]", 0.0, "[CALC]"),
        ("route time with the 23 s extension [s]", float(T[-1] + 1), "[TEST] driver rows"),
        ("route time without the extension [s] (what a Municipal run would be if PTO time were forgotten)",
         float(run_driver_e2(cy, "ReferenceLoad")[0][-1] + 1), "[TEST] driver rows"),
    ]
    out("partD1_municipal_summary.csv", pd.DataFrame(summ, columns=["quantity", "value", "tag"]))
    return df, stop_final, summ


def case(name, route, is_on, stop_1s_w=None, drive_w=None, stop_const=0.0, drive_const=0.0, stop_eff=1.0, drive_eff=1.0, expect=""):
    r = route
    pt, pw = (VPTOEL_T, VPTOEL_W) if stop_1s_w is None else stop_1s_w
    dt_, dw = (NONE_T, NONE_W) if drive_w is None else drive_w
    try:
        is_on_, ps, s1, d1 = pto_engine(r["stop_wp"], is_on, pt if not stop_const else NONE_T, pw if not stop_const else NONE_W,
                                        dt_, dw, stop_eff, drive_eff)
        row, sa, da, ev = RC.consumption_step6_v_pto1nov(r["S"], r["V"], r["wp_s"], r["stop_wp"], is_on_, ps, s1, d1,
                                                         stop_const_W=stop_const, drive_const_W=drive_const,
                                                         stop_eff=stop_eff, drive_eff=drive_eff, M=r["M"])
        return dict(case=name, result="ok", energy_kWh=float(row.sum() / 3.6e6), stop_rows=int(sa.sum()), drive_rows=int(da.sum()),
                    events=str([(e["kind"], e["wp"], e["k0"], e["k1"]) for e in ev]), expected=expect)
    except Exception as e:                                                  # noqa: BLE001
        return dict(case=name, result=f"RAISES {type(e).__name__}: {e}", energy_kWh=np.nan, stop_rows=0, drive_rows=0, events="", expected=expect)


def d2_scenarios():
    rows = []
    # sweeper: ILLUSTRATIVE 6 kW shaft, efficiency 0.9; route 5 legs of 1 km, stops at wp 2 and 4 (30 s)
    r = build_route([1000] * 5, [10, 0, 30, 0, 30, 10])
    on = np.array([0, 1, 0, 0, 0, 0.0])                      # drive part starts at the 0 s marker waypoint 1 (no real stop)
    rows.append(case("sweeper, drive const 6000 W (ILLUSTRATIVE) from marker wp1 to next stop wp2", r, on,
                     drive_const=6000.0, drive_eff=0.9, expect="6000/0.9 W x rows between marker and first standing row of wp2"))
    on2 = np.array([0, 0, 0, 0, 0, 0.0])
    rows.append(case("no wp on -> nothing placed", r, on2, drive_const=6000.0, expect="0 kWh"))
    # refuse: stop profile at wp 2, 4 (VECTO profile, stop 2 s + 23)
    r = build_route([1000, 1000, 1000, 1000], [10, 0, 25, 0, 25])
    on = np.array([0, 0, 1, 0, 1.0])
    rows.append(case("refuse: VECTO profile at 2 stops (stop 2 s + 23 s)", r, on, expect=f"2 x {VPTOEL_KWH:.5f} kWh"))
    # mixed: stop profile + drive profile (ILLUSTRATIVE 4 kW for 60 s) after each stop
    rows.append(case("mixed: stop profile + drive profile 60 s x 4000 W (ILLUSTRATIVE)", r, on, drive_w=([0, 60], [4000, 0]),
                     expect=f"2 x ({VPTOEL_KWH:.5f} + {4000*60/3.6e6:.5f}) kWh"))
    # edge: PTO on last waypoint (stop profile ok; drive part has no rows)
    r2 = build_route([1000, 1000], [10, 25, 25])
    rows.append(case("PTO on the LAST waypoint: stop profile ok", r2, np.array([0, 0, 1.0]), expect=f"{VPTOEL_KWH:.5f} kWh"))
    rows.append(case("PTO on the LAST waypoint with a drive profile: no rows after it", r2, np.array([0, 0, 1.0]), drive_w=([0, 60], [4000, 0]),
                     expect="stop profile only; drive part has no moving rows"))
    # edge: drive part with no next stop -> window to the end of the route
    r3 = build_route([1000, 1000], [10, 25, 0])
    rows.append(case("drive const with NO next stop: runs to the end of the route", r3, np.array([0, 1, 0.0]), drive_const=3000.0,
                     stop_1s_w=(NONE_T, NONE_W), expect="3000 W x all moving rows after wp1"))
    # edge: drive profile longer than the rest of the route -> truncated
    rows.append(case("drive profile 600 s longer than the rest of the route -> truncated", r3, np.array([0, 1, 0.0]), drive_w=([0, 600], [3000, 0]),
                     stop_1s_w=(NONE_T, NONE_W), expect="truncated at the last row"))
    # edge: drive profile still running at next stop (keeps running)
    r4 = build_route([100, 100, 1000], [10, 20, 20, 10])
    rows.append(case("drive profile 60 s starting at wp1, next stop wp2 after only 10 rows: keeps running through the stop", r4,
                     np.array([0, 1, 0, 0.0]), drive_w=([0, 60], [4000, 0]), stop_1s_w=(NONE_T, NONE_W), expect="60 s x 4000 W = 0.06667 kWh, rows past the stop"))
    # overlap: wp1 and wp2 both start a 60 s drive profile; the second starts (after a 10-row leg + 20 s stop) while the first still runs
    r5 = build_route([100, 100, 1000], [10, 20, 20, 10])
    rows.append(case("OVERLAP: wp1 and wp2 both start a 60 s drive profile, second starts while first runs", r5, np.array([0, 1, 1.0, 0.0]),
                     drive_w=([0, 60], [4000, 0]), stop_1s_w=(NONE_T, NONE_W), expect="ValueError (VECTO PTODriveAuxiliary.cs 25-27 throws)"))
    r5b = build_route([100, 100, 1000], [10, 20, 20, 10])
    rows.append(case("no overlap: wp1 drive profile 20 s (ends before wp2's drive starts), wp2 starts its own 20 s", r5b, np.array([0, 1, 1.0, 0.0]),
                     drive_w=([0, 20], [4000, 0]), stop_1s_w=(NONE_T, NONE_W), expect="2 x 20 s x 4000 W = 0.04444 kWh"))
    # marker with stop 0 : stop profile cannot apply; drive part starts there
    r6 = build_route([1000, 1000], [10, 0, 25])
    rows.append(case("marker wp (stop 0) with a drive profile and a stop profile configured: stop profile ignored, drive starts",
                     r6, np.array([0, 1, 0.0]), drive_w=([0, 60], [4000, 0]), expect="drive 60 s x 4000 W only"))
    # constants with efficiency
    r7 = build_route([1000, 1000], [10, 25, 10])
    rows.append(case("stop constant 3000 W (ILLUSTRATIVE), eff 0.8 -> 3750 W on all M==0 rows of the stop", r7, np.array([0, 1, 0.0]),
                     stop_const=3000.0, stop_eff=0.8, expect="3750 W x 25 s = 0.02604 kWh"))
    # two stops same distance
    r8 = build_route([1000, 1000], [10, 25, 25])
    r8["wp_s"] = np.array([0.0, 1000.0, 1000.0])
    rows.append(case("two stop waypoints at the same distance", r8, np.array([0, 1, 1.0]), expect="ValueError (parser must reject)"))
    # float drift in S
    r9 = build_route([1000, 1000], [10, 25, 10])
    for drift in (5e-4, 2e-3):
        rr = dict(r9)
        rr["wp_s"] = r9["wp_s"] + np.array([0, drift, 0])
        rows.append(case(f"waypoint distance differs from driver S by {drift} m (tolerance 1e-3)", rr, np.array([0, 1, 0.0]),
                         expect="ok below 1e-3, ValueError above"))
    # stop shorter than the profile (pto_engine raises)
    r10 = build_route([1000, 1000], [10, 22, 10])
    rows.append(case("stop 22 s < PTO 23 s (parser did not extend)", r10, np.array([0, 1, 0.0]), expect="ValueError from pto_engine"))
    # PTO at the depot
    rows.append(case("is_on at waypoint 0 (depot) is forced to 0", build_route([1000], [10, 25]), np.array([1, 0.0]), expect="0 kWh"))
    # odd stop: centring floor
    r11 = build_route([1000, 1000], [10, 26, 10])
    c = case("odd standing time 26 s: PTO start floor((26-23)/2)=1 -> 1 s before, 2 s after", r11, np.array([0, 1, 0.0]), expect=f"{VPTOEL_KWH:.5f} kWh")
    rows.append(c)
    # row-matching by V==0 only (no M): off-by-one for constants
    r12 = build_route([1000, 1000], [10, 25, 10])
    try:
        is_on_, ps, s1, d1 = pto_engine(r12["stop_wp"], np.array([0, 1, 0.0]), NONE_T, NONE_W, NONE_T, NONE_W, 1, 1)
        row, sa, da, ev = RC.consumption_step6_v_pto1nov(r12["S"], r12["V"], r12["wp_s"], r12["stop_wp"], is_on_, ps, s1, d1, stop_const_W=3000.0)
        rows.append(dict(case="stop constant 3000 W, rows found by V==0 ONLY (current code's rule, no M)", result="ok",
                         energy_kWh=float(row.sum() / 3.6e6), stop_rows=int(sa.sum()), drive_rows=0, events=str(ev[0]["k1"] - ev[0]["k0"]) + " rows",
                         expected="25 rows expected, V==0 gives 26 (the first accelerating row)"))
    except Exception as e:                                                  # noqa: BLE001
        rows.append(dict(case="V==0 only", result=str(e)))
    df = pd.DataFrame(rows)
    out("partD2_scenarios.csv", df)
    return df


if __name__ == "__main__":
    df1, stop_final, summ = d1_municipal()
    print("D1 MunicipalUtility summary")
    for q, v, t in summ:
        print(f"  {q}: {v}   {t}")
    df2 = d2_scenarios()
    print("\nD2 scenarios")
    pd.set_option("display.width", 250, "display.max_colwidth", 95)
    print(df2[["case", "result", "energy_kWh", "stop_rows", "drive_rows"]].to_string(index=False))
    print("\nfiles written:")
    for p in WRITTEN:
        print("  ", os.path.relpath(p, REPO))
