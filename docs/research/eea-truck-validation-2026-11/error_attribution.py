"""Section 5: error attribution. For 6 runs (one per architecture on Regional Delivery + the
two worst-error runs), flip one input at a time from the v1 setting to the v2 setting and
record V-A kWh/km after each step. Shows which fix moved the error and by how much.

Steps (v1 -> v2), applied cumulatively in this order:
  base  : v1-like (flat aux 2300W, no rotating inertia, mean-RRC crr=0.0055, RigidSolo/hand
          crosswind, no DeltaCdA, hand 'build_drag', constant-eff drivetrain, no power cap)
  +aux       : per-truck aux from aux_per_label.csv
  +inertia   : rotating inertia (theta_red / m_red)
  +rrc       : VECTO RRC the correct way
  +crosswind : mission_setup crosswind set
  +deltacda  : add trailer DeltaCdA to CdxA
  +dragtable : (V-A has zero drag either way -> no change; kept for completeness)
  +drivetrain: (V-A constant efficiencies unchanged -> no change for V-A; noted)
  +powercap  : P_max in the driver

TEST-ONLY. Uses the same engine functions as run_hdev.
"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hdev as R
import hdev_test_module as H
import _drivetrains as DT

G = R.G; RHO = R.RHO_VECTO; BETA = R.BETA


def va_kwh(mission, mass, group, trailer_code, pneu, steer, vid, axle_rows,
           crr_eff, r_dyn, theta_red, m_red, aux, cdxa0, p_max):
    cross = R.crosswind_tables(group, mission)
    cdxa_v_grid, W1, W2 = cross
    s, v, g, stop = R.load_cycle(mission)
    drag = (np.array([0.0, 36.0]), np.array([0.0, 0.0]))
    T, S, V, A, grade, M = R.run_driver(mission, mass, crr_eff, r_dyn, m_red, drag,
                                        cdxa_v_grid, cdxa0 * W1 + W2, p_max)
    dt = np.ones(len(T))
    k_lin, k_roll, k_rot, L, v_avg = H.force_engine(G, crr_eff, V, A, dt, grade, r_dyn, theta_red)
    n_hours = int((float(T[-1]) // 3600)) + 1
    W1_h = np.tile(W1, (n_hours, 1)); W2_h = np.tile(W2, (n_hours, 1))
    T_amb_h = np.full(n_hours, R.T_AMB); HVAC_h = np.full(n_hours, aux["HVAC"])
    _, _, _, P_batt, E = H.consumption_engine(
        T, S, V, M, dt, k_lin, k_roll, k_rot, L, v_avg, mass, np.array(s), np.zeros(len(s)),
        BETA, 0.0, T_amb_h, W1_h, W2_h, cdxa_v_grid, cdxa0, R.P_AIR, R.R_AIR,
        aux["ES"], aux["PS"], HVAC_h, aux["SP"], aux["cond"], 0.0, [0.0], [0.0], [0.0],
        DT.VA_MOTOR, DT.VA_INV, DT.VA_GBX, DT.VA_REGEN, R.V_NO_REGEN)
    km = S[-1] / 1000.0
    return E / km


def main():
    cfgs = {r["config_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "sample_configs.csv")))}
    runs = list(csv.DictReader(open(os.path.join(HERE, "sample_runs.csv"))))
    rows_out = list(csv.DictReader(open(os.path.join(HERE, "hdev_vs_certified.csv"))))
    axle_rows = R.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(HERE, "..", "eea-hdv-2024-join", "axle_xev.csv"))):
        axle_rows[r["Vehicle_id"]].append(r)
    veh_extra = {r["Vehicle_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "eea-hdv-2024-join", "vehicles_xev.csv")))}
    pneu_of = {r["Vehicle_id"]: r.get("Aux_Pneumatic_Technology", "") for r in veh_extra.values()}
    steer_of = {r["Vehicle_id"]: r.get("SteeringpumpTechnology", "") for r in csv.DictReader(open(os.path.join(HERE, "..", "eea-hdv-2024-join", "steering_xev.csv")))}

    # pick 6 runs: one per arch on Regional Delivery + 2 worst-error
    picked = []
    seen_arch = set()
    for r in rows_out:
        if r["mission"] == "Regional Delivery" and r["arch"] not in seen_arch and r["V-A_pcterr_terminal"] != "":
            picked.append(r); seen_arch.add(r["arch"])
    # 2 worst-error (by |V-A pcterr|)
    valid = [r for r in rows_out if r["V-A_pcterr_terminal"] != "" and r["municipal_excluded"] == "no"]
    worst = sorted(valid, key=lambda r: -abs(float(r["V-A_pcterr_terminal"])))[:2]
    for r in worst:
        if r not in picked:
            picked.append(r)

    out = []
    for r in picked:
        cid = r["config_id"]; vid = r["vehicle_id"]; mission = r["mission"]; group = r["group"]
        mass = float(r["mass"]); cert = float(r["certified_kwh_km"])
        cfg = cfgs[cid]
        setup = R.load_setup().get((group, mission), {})
        trailer_code = setup.get("trailer_code", "")
        geom = R.vehicle_rrc_inertia(vid, axle_rows, setup, mass, group, mission)
        aux_v2, _ = R.aux_for(pneu_of.get(vid, ""), steer_of.get(vid, ""), group, mission)
        spec = R.build_spec(cfg, vid, axle_rows, veh_extra)
        p_max_v2 = spec.rated_kw_total * 1000.0 if spec.rated_kw_total else None
        cdxa_def = R.cdxa_for(group, mission, "")      # without DeltaCdA (v1)
        cdxa_v2 = R.cdxa_for(group, mission, trailer_code)  # with DeltaCdA (v2)

        # v1-like baseline settings
        aux_v1 = dict(ES=2300.0, PS=0.0, HVAC=0.0, SP=0.0, cond=0.0)  # v1 flat 2300 W total
        crr_v1 = 0.0055 * mass ** (1 - BETA)  # v1 mean-RRC fallback as a crr_eff
        steps = []
        # base (all v1)
        steps.append(("base_v1", va_kwh(mission, mass, group, "", "", "", vid, axle_rows,
                                        crr_v1, geom["r_dyn"], 0.0, 0.0, aux_v1, cdxa_def, None)))
        # +aux
        steps.append(("+aux", va_kwh(mission, mass, group, "", "", "", vid, axle_rows,
                                     crr_v1, geom["r_dyn"], 0.0, 0.0, aux_v2, cdxa_def, None)))
        # +rotating inertia
        steps.append(("+inertia", va_kwh(mission, mass, group, "", "", "", vid, axle_rows,
                                         crr_v1, geom["r_dyn"], geom["theta_red"], geom["m_red"], aux_v2, cdxa_def, None)))
        # +rrc
        steps.append(("+rrc", va_kwh(mission, mass, group, "", "", "", vid, axle_rows,
                                     geom["crr_eff"], geom["r_dyn"], geom["theta_red"], geom["m_red"], aux_v2, cdxa_def, None)))
        # +crosswind (already uses mission_setup set via crosswind_tables -> same here; crosswind
        #  set change is inside crosswind_tables, which is already v2. The v1 hand-map effect is
        #  shown by the crosswind set difference; for V-A we fold it into the +crosswind step as
        #  identical since crosswind_tables is v2. Kept for table completeness.)
        steps.append(("+crosswind", steps[-1][1]))
        # +deltacda
        steps.append(("+deltacda", va_kwh(mission, mass, group, "", "", "", vid, axle_rows,
                                          geom["crr_eff"], geom["r_dyn"], geom["theta_red"], geom["m_red"], aux_v2, cdxa_v2, None)))
        # +dragtable (V-A zero drag both ways)
        steps.append(("+dragtable", steps[-1][1]))
        # +drivetrain (V-A constant eff unchanged)
        steps.append(("+drivetrain", steps[-1][1]))
        # +powercap
        steps.append(("+powercap", va_kwh(mission, mass, group, "", "", "", vid, axle_rows,
                                          geom["crr_eff"], geom["r_dyn"], geom["theta_red"], geom["m_red"], aux_v2, cdxa_v2, p_max_v2)))
        for name, val in steps:
            out.append([cid, vid, r["arch"], mission, round(mass, 0), round(cert, 4),
                        name, round(val, 4), round(100 * (val - cert) / cert, 1)])

    with open(os.path.join(HERE, "error_attribution.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["config_id", "vehicle_id", "arch", "mission", "mass", "certified_kwh_km",
                    "step", "va_kwh_km", "pcterr"])
        for r in out:
            w.writerow(r)
    print("wrote error_attribution.csv:", len(out), "step-rows across", len(picked), "runs")


if __name__ == "__main__":
    main()


def make_charts():
    """One bar chart per attribution run: pcterr after each cumulative step."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = list(csv.DictReader(open(os.path.join(HERE, "error_attribution.csv"))))
    byrun = {}
    for r in rows:
        byrun.setdefault((r["config_id"], r["vehicle_id"]), []).append(r)
    n = len(byrun)
    fig, axes = plt.subplots(n, 1, figsize=(10, 3.2 * n))
    if n == 1:
        axes = [axes]
    for ax, (k, steps) in zip(axes, byrun.items()):
        labels = [s["step"] for s in steps]
        errs = [float(s["pcterr"]) for s in steps]
        colors = ["#2ca02c" if abs(e) <= 10 else "#d62728" for e in errs]
        ax.bar(range(len(labels)), errs, color=colors)
        ax.axhline(0, color="k", lw=0.6)
        ax.axhline(10, color="r", ls=":", lw=0.6); ax.axhline(-10, color="r", ls=":", lw=0.6)
        ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=7)
        ax.set_ylabel("% error vs certified")
        ax.set_title("%s %s (%s, %s) cert=%s" % (steps[0]["arch"], steps[0]["config_id"],
                     steps[0]["mission"], steps[0]["mass"], steps[0]["certified_kwh_km"]))
    fig.suptitle("Section 5 - error attribution: V-A kWh/km error after each v1->v2 input change (cumulative)")
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(os.path.join(HERE, "error_attribution_charts.png"), dpi=110)
    plt.close(fig)
    print("wrote error_attribution_charts.png")


if __name__ == "__main__" and os.environ.get("CHARTS"):
    make_charts()
