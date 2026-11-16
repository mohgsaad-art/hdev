"""PART 1 -- air-drag ranges into the harness, and Method A before/after on the 10 trucks.

Before = v2 harness CdxA (SegmentTable standard CdxA + delta CdA of the mission_setup trailer code, every mission).
After  = VECTO rule (harness.vecto_cdxa, AirdragDataAdapter.cs 140-152 + TruckSegments.cs 280-306/359-362/394-407):
         measured air drag -> midpoint of the EEA range (Reg. 2018/956 Annex I Part C) on every mission except
         Construction; standard values -> SegmentTable default; + summed trailer delta CdA of the trailers VECTO uses.

Outputs: part1_range_counts.csv, part1_methodA_before_after.csv, part1_mission_pattern.csv,
         part1_linearity_check.csv, part1_methodA_by_mission.png
"""
import csv
import os
from collections import Counter, defaultdict

import numpy as np

import harness as HN
import methods_lib as ML

HERE = os.path.dirname(os.path.abspath(__file__))
TEN = ["C0059", "C0091", "C0371", "C0116", "C0153", "C0218", "C0712", "C0206", "C0070", "C0001"]
NAMES = {"C0059": "Fuso eCanter", "C0091": "IVECO S-eWay", "C0371": "Scania R 400E", "C0116": "MAN eTGX",
         "C0153": "Mercedes eActros 600", "C0218": "Renault D", "C0712": "Volvo FM", "C0206": "Mercedes Econic",
         "C0070": "IVECO eDaily", "C0001": "DAF XB"}
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")


def write(path, rows, attr=True):
    with open(path, "w", newline="") as fh:
        if attr:
            fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return path


def records(mode):
    HN.AIRDRAG_MODE = mode
    recs, sk = HN.load_or_build(TEN, "ten", processes=8)
    return {(r["config_id"], r["mission"], round(r["payload"])): r for r in recs}, sk


def main():
    files = []
    # 1. counts per range and certification method (all 4,603 in-scope trucks, and the 10)
    cnt = Counter()
    for r in csv.DictReader(open(os.path.join(HN.V2_DIR, "truck_vehicles.csv"))):
        cnt[(r["AirDrag_CdxA_range"].strip() or "(blank)", r["AirDrag_CertificationMethod"].strip() or "(blank)")] += 1
    cfgs = {r["config_id"]: r for r in csv.DictReader(open(os.path.join(HN.V2_DIR, "truck_configs.csv")))}
    ten = Counter((cfgs[c]["AirDrag_CdxA_range"], cfgs[c]["AirDrag_CertificationMethod"]) for c in TEN)
    rows = []
    keys = sorted(set(cnt) | set(ten), key=lambda k: (int(k[0][1:]) if k[0][1:].isdigit() else 99, k[1]))
    for k in keys:
        rng = HN.CDXA_RANGES.get(k[0])
        rows.append(dict(range=k[0], certification=k[1], range_min_m2=rng[0] if rng else "NOT IN TABLE",
                         range_max_m2=rng[1] if rng else "NOT IN TABLE", trucks_all=cnt.get(k, 0), trucks_of_the_10=ten.get(k, 0)))
    files.append(write(os.path.join(HERE, "part1_range_counts.csv"), rows))
    not_in = sum(v for k, v in cnt.items() if k[0] not in HN.CDXA_RANGES)
    print("trucks whose range is not in A1-A24: %d of %d" % (not_in, sum(cnt.values())))

    # 2. Method A before / after
    before, _ = records("standard")
    after, sk = records("range_mid")
    A = ML.MethodA()
    ba = []
    for key in sorted(after, key=lambda k: (TEN.index(k[0]), k[1], k[2])):
        ra, rb = after[key], before[key]
        pa, pb = A.predict(ra), A.predict(rb)
        ba.append(dict(config_id=key[0], truck=NAMES[key[0]], group=ra["group"], mission=key[1], payload_kg=key[2],
                       airdrag=("measured " if ra["airdrag_measured"] else "standard ") + ra["cdxa_range"],
                       trailers_vecto=ra["cdxa_trailers"], cdxa_before_m2=round(rb["cdxa0"], 3), cdxa_after_m2=round(ra["cdxa0"], 3),
                       certified_kwh_km=round(ra["cert"], 4), A_before_kwh_km=round(pb, 4), A_after_kwh_km=round(pa, 4),
                       err_before_pct=round(100 * (pb / ra["cert"] - 1), 2), err_after_pct=round(100 * (pa / ra["cert"] - 1), 2)))
    files.append(write(os.path.join(HERE, "part1_methodA_before_after.csv"), ba))
    # 3. mission pattern: per truck, mean error per base mission; spread = max - min
    pat = []
    for cid in TEN:
        for tag in ("before", "after"):
            per = defaultdict(list)
            for r in ba:
                if r["config_id"] == cid:
                    per[r["mission"]].append(r["err_%s_pct" % tag])
            means = {m: float(np.mean(v)) for m, v in per.items()}
            row = dict(config_id=cid, truck=NAMES[cid], airdrag=next(r["airdrag"] for r in ba if r["config_id"] == cid), cdxa=tag)
            for m in ("Urban Delivery", "Regional Delivery", "Long Haul", "Construction", "Regional Delivery EMS", "Long Haul EMS"):
                row[m] = round(means[m], 1) if m in means else ""
            row["mission_spread_pp"] = round(max(means.values()) - min(means.values()), 1)
            pat.append(row)
    files.append(write(os.path.join(HERE, "part1_mission_pattern.csv"), pat))
    # 4. linearity of P_wheel in CdxA (fit moves CdxA inside its range; driver trajectory kept) -> check on 2 runs
    lin = []
    HN.AIRDRAG_MODE = "range_mid"
    for cid, mission in (("C0116", "Long Haul"), ("C0091", "Regional Delivery")):
        r = next(v for k, v in after.items() if k[0] == cid and k[1] == mission)
        full = HN.build_record(cid, r["vehicle_id"], mission, r["payload"], r["mass"], r["cert"], cdxa_override=r["cdxa_hi"])
        full = HN.compact(full)
        r_lin = dict(r); r_lin["P_wheel"] = r["P_wheel"] + r["aero_k"] * (r["cdxa_hi"] - r["cdxa0"])
        e_full, e_lin = A.predict(full), A.predict(r_lin)
        lin.append(dict(config_id=cid, mission=mission, cdxa_mid=r["cdxa0"], cdxa_hi=r["cdxa_hi"],
                        A_full_rerun_kwh_km=round(e_full, 5), A_linear_kwh_km=round(e_lin, 5),
                        diff_pct=round(100 * (e_lin / e_full - 1), 4)))
    files.append(write(os.path.join(HERE, "part1_linearity_check.csv"), lin))

    # 5. every input per mission for the trucks whose pattern is still > 5 pp, + regen share of wheel energy
    axles = defaultdict(list)
    for r in csv.DictReader(open(os.path.join(HN.JOIN, "axle_xev.csv"))):
        axles[r["Vehicle_id"]].append("%s:%s:%s" % (r["AxleNumber"], r["TyreDimension"], r["SpecificRRC"]))
    flagged = {p["config_id"] for p in pat if p["cdxa"] == "after" and p["mission_spread_pp"] > 5.0}
    inp, xs, ys, cids = [], [], [], []
    for key in sorted(after, key=lambda k: (TEN.index(k[0]), k[1], k[2])):
        r = after[key]
        Pw = r["P_wheel"]; pos = Pw[Pw > 0].sum(); neg = -Pw[Pw < 0].sum()
        e = A.predict(r) / r["cert"] - 1
        xs.append(neg / pos); ys.append(100 * e); cids.append(key[0])
        if key[0] not in flagged:
            continue
        inp.append(dict(config_id=key[0], truck=NAMES[key[0]], mission=key[1], cycle=HN.RH.MISSION_CYCLE[key[1]],
                        payload_kg=key[2], total_mass_kg=r["mass"], cdxa0_m2=round(r["cdxa0"], 3), trailers=r["cdxa_trailers"],
                        delta_cda_m2=r["cdxa_delta"], crr_eff=round(r["crr_eff"], 6), m_red_kg=round(r["m_red"], 1),
                        tyres_axle_dim_rrc=" ".join(axles.get(r["vehicle_id"], [])), aux_pneumatic_label=r["aux_pneu"],
                        aux_kwh_km=round(r["E_aux_Ws"] / 3.6e6 / r["km"], 4),
                        wheel_drive_kwh_km=round(pos / 3.6e6 / r["km"], 4), wheel_brake_kwh_km=round(neg / 3.6e6 / r["km"], 4),
                        brake_over_drive=round(neg / pos, 3), certified_kwh_km=round(r["cert"], 4), A_err_pct=round(100 * e, 2)))
    files.append(write(os.path.join(HERE, "part1_inputs_per_mission.csv"), inp))
    corr = float(np.corrcoef(xs, ys)[0, 1])
    xs_a, ys_a, c_a = np.array(xs), np.array(ys), np.array(cids)
    xd = np.concatenate([xs_a[c_a == c] - xs_a[c_a == c].mean() for c in TEN])
    yd = np.concatenate([ys_a[c_a == c] - ys_a[c_a == c].mean() for c in TEN])
    corr_w = float(np.corrcoef(xd, yd)[0, 1])
    slope = float(np.polyfit(xd, yd, 1)[0])
    print("within-truck (per-truck mean removed): r = %.2f, slope %.1f pp per unit brake/drive ratio" % (corr_w, slope))
    print("Method A error vs (wheel braking energy / wheel driving energy): Pearson r = %.2f over %d runs" % (corr, len(xs)))
    files.append(write(os.path.join(HERE, "part1_regen_share_correlation.csv"),
                       [dict(n_runs=len(xs), pearson_r=round(corr, 3), pearson_r_within_truck=round(corr_w, 3),
                             slope_within_truck_pp_per_unit=round(slope, 2),
                             note="Method A error [%] vs brake/drive wheel energy ratio, VECTO rule + range midpoint")], attr=False))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)
    ms = ["Urban Delivery", "Regional Delivery", "Long Haul", "Construction", "Regional Delivery EMS", "Long Haul EMS"]
    for a, tag in zip(ax, ("before", "after")):
        for cid in TEN:
            row = next(p for p in pat if p["config_id"] == cid and p["cdxa"] == tag)
            xs = [i for i, m in enumerate(ms) if row[m] != ""]
            a.plot(xs, [row[ms[i]] for i in xs], "-o", ms=3, label=NAMES[cid])
        a.axhline(0, color="k", lw=0.8); a.set_xticks(range(len(ms))); a.set_xticklabels([m.replace(" Delivery", "") for m in ms], rotation=20, fontsize=8)
        a.set_title("Method A error by mission, CdxA %s" % ("v2 standard" if tag == "before" else "VECTO rule + range midpoint"))
        a.grid(alpha=0.3)
    ax[0].set_ylabel("mean error vs certified [%]"); ax[1].legend(fontsize=7)
    fig.tight_layout(); f = os.path.join(HERE, "part1_methodA_by_mission.png"); fig.savefig(f, dpi=110); files.append(f)
    for p in pat:
        print("%-22s %-15s %-6s spread %5.1f pp" % (p["truck"], p["airdrag"], p["cdxa"], p["mission_spread_pp"]))
    for f in files:
        print("wrote", f)


if __name__ == "__main__":
    main()
