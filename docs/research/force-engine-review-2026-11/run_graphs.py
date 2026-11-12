"""Graphs for the review (matplotlib, Agg). Run after run_part_c.py / run_part_e.py / run_part_f.py.

Run:  python run_graphs.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from _common import *
import reference_copy as RC


def fig_row_diff():
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    for ax, cyc in zip(axes, ("RegionalDelivery", "UrbanDelivery")):
        veh = Vehicle(cyc, "ReferenceLoad")
        cols = load_vmod_run(cyc, "ReferenceLoad")
        r = vmod_rows(cols)
        vt = vecto_terms(cols)
        vs, ac = trace_for_engine(r, "acc")
        H = hdev_terms(veh, vs, ac, r["dt"], r["grad"], tab=veh.cdxa_table())
        d = (H["P_wheel"] - vt["P_wheel_in"]) / 1000
        ax.plot(r["t"], d, lw=0.5, color="tab:red", label="force_engine + P_wheel  minus  VECTO P_wheel_in")
        ax2 = ax.twinx()
        ax2.plot(r["t"], r["v_act"] * 3.6, lw=0.5, color="tab:gray", alpha=0.6)
        ax2.set_ylabel("speed [km/h]", color="gray")
        ax.set_ylabel("difference [kW]")
        ax.set_title(f"{cyc}, ReferenceLoad: row difference of wheel power (VECTO's own speed trace)")
        ax.legend(loc="upper right", fontsize=8)
    axes[-1].set_xlabel("time [s]")
    fig.tight_layout()
    fig.savefig(out("graph_partC_row_difference.png"), dpi=130)
    plt.close(fig)
    print("wrote", os.path.relpath(out("graph_partC_row_difference.png"), REPO))


def fig_energy_errors():
    t = pd.read_csv(out("partC_terms.csv"))
    t = t[(t.variant == "i_table") & (t.term.isin(["P_roll", "P_air", "P_slope", "P_wheel_inertia", "P_wheel_in(sum)"]))]
    t["case"] = t.cycle.str.replace("Delivery", "") + "\n" + t.load.str.replace("Loading", "").str.replace("Load", "")
    pv = t.pivot(index="case", columns="term", values="d_pos_pct")
    ax = pv.plot(kind="bar", figsize=(10, 4.5))
    ax.set_ylabel("error of positive-part energy [%]")
    ax.set_title("Part C: force_engine on VECTO's own trace vs VECTO (positive part of each term)")
    ax.axhline(0, color="k", lw=0.5)
    plt.tight_layout()
    plt.savefig(out("graph_partC_energy_errors.png"), dpi=130)
    plt.close()
    print("wrote", os.path.relpath(out("graph_partC_energy_errors.png"), REPO))


def fig_split():
    s = pd.read_csv(out("partD_driver_vs_force_split.csv"))
    s = s[(s.term == "P_wheel") & (s.part == "pos")]
    s["case"] = s.cycle.str.replace("Delivery", "") + "\n" + s.load.str.replace("Loading", "").str.replace("Load", "")
    ax = s.set_index("case")[["err_total_pct", "err_force_only_pct"]].plot(kind="bar", figsize=(9, 4.2))
    ax.set_ylabel("positive wheel energy vs VECTO [%]")
    ax.set_title("Part D: HDEV driver + force_engine (total) vs VECTO trace + force_engine (force only)")
    ax.axhline(0, color="k", lw=0.5)
    plt.tight_layout()
    plt.savefig(out("graph_partD_driver_vs_force.png"), dpi=130)
    plt.close()
    print("wrote", os.path.relpath(out("graph_partD_driver_vs_force.png"), REPO))


def fig_timestep():
    e = pd.read_csv(out("partE_timestep_energy.csv"))
    e = e[(e.term == "P_wheel")]
    fig, ax = plt.subplots(figsize=(7, 4))
    for cyc, g in e.groupby("cycle"):
        ax.plot(g.dt, g.pos_vs_dt0p25_pct, marker="o", label=cyc)
    ax.set_xlabel("driver time step dt [s]")
    ax.set_ylabel("positive wheel energy vs dt=0.25 s [%]")
    ax.set_title("Part E: time-step convergence")
    ax.legend()
    ax.invert_xaxis()
    plt.tight_layout()
    plt.savefig(out("graph_partE_timestep.png"), dpi=130)
    plt.close()
    print("wrote", os.path.relpath(out("graph_partE_timestep.png"), REPO))


def fig_f():
    f = pd.read_csv(out("partF_effects_wheel_energy.csv"))
    f = f[f.item.str.startswith(("F1", "F2", "F5", "F8")) | f.scenario.str.contains("T=10 C, RH=50 %, p=101325 Pa") | f.scenario.str.contains("T=-10 C, RH=50 %, p=101325 Pa")]
    f["label"] = f.item.str.split().str[0] + " " + f.scenario.str.slice(0, 28)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, cyc in zip(axes, ("RegionalDelivery", "UrbanDelivery")):
        g = f[f.cycle == cyc]
        ax.barh(g.label, g.dE_pos_pct)
        ax.set_title(cyc)
        ax.set_xlabel("change of positive wheel energy [%]")
    plt.tight_layout()
    plt.savefig(out("graph_partF_effects.png"), dpi=130)
    plt.close()
    print("wrote", os.path.relpath(out("graph_partF_effects.png"), REPO))


if __name__ == "__main__":
    fig_row_diff()
    fig_energy_errors()
    fig_split()
    fig_timestep()
    fig_f()
