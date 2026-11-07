"""Job 3 v2 graphs 1-5. Writes PNGs into this folder. One idea per graph, plain titles,
axis units, legend. CdxA basis named in every title: 'VECTO standard-value CdxA' (2.4 [BOB];
no bin edges), Municipal excluded from error stats (R12).

GATE status is read from gate_e2.csv and stamped on the figures.
"""
import csv
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VARIANTS = ["V-A", "V-B", "V-C", "V-D"]
ARCH_COLOR = {"E2": "#1f77b4", "E3": "#ff7f0e", "E-IEPC": "#2ca02c", "E-IEPC-wheel": "#d62728"}
CDXA_LABEL = "VECTO standard-value CdxA"


def load():
    return list(csv.DictReader(open(os.path.join(HERE, "hdev_vs_certified.csv"))))


def gate_status():
    try:
        for r in csv.reader(open(os.path.join(HERE, "gate_e2.csv"))):
            if r and r[0] == "GATE":
                return "GATE %s (worst %s%%)" % (r[1], r[3])
    except FileNotFoundError:
        pass
    return "GATE status unknown"


def fval(r, key):
    try:
        return float(r[key])
    except (ValueError, KeyError, TypeError):
        return None


def nonmun(rows):
    return [r for r in rows if r.get("municipal_excluded") == "no"]


def graph1_parity(rows):
    gs = gate_status()
    fig, axes = plt.subplots(2, 2, figsize=(12, 11))
    for ax, v in zip(axes.ravel(), VARIANTS):
        plotted = 0
        for r in nonmun(rows):
            cert = fval(r, "certified_kwh_km")
            y = fval(r, "%s_batt_kwh_km" % v)
            if cert is None or y is None:
                continue
            ax.scatter(cert, y, s=12, alpha=0.5,
                       color=ARCH_COLOR.get(r["arch"], "#888"))
            plotted += 1
        lims = [0, 3.5]
        ax.plot(lims, lims, "k-", lw=1, label="y = x")
        ax.plot(lims, [l * 1.05 for l in lims], "k--", lw=0.6, alpha=0.6, label="+/-5%")
        ax.plot(lims, [l * 0.95 for l in lims], "k--", lw=0.6, alpha=0.6)
        ax.plot(lims, [l * 1.10 for l in lims], "k:", lw=0.6, alpha=0.6, label="+/-10%")
        ax.plot(lims, [l * 0.90 for l in lims], "k:", lw=0.6, alpha=0.6)
        ax.set_xlim(0, 3.5); ax.set_ylim(0, 3.5)
        ttl = v + (" (cannot run from EEA data - R7)" if plotted == 0 else " (n=%d)" % plotted)
        ax.set_title(ttl)
        ax.set_xlabel("certified kWh/km"); ax.set_ylabel("HDEV kWh/km (battery terminal)")
        ax.legend(fontsize=7, loc="upper left")
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=a) for a, c in ARCH_COLOR.items()]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8)
    fig.suptitle("Graph 1 - Parity: certified vs HDEV kWh/km (%s). %s. Municipal excluded." % (CDXA_LABEL, gs))
    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
    fig.savefig(os.path.join(HERE, "graph1_parity.png"), dpi=110)
    plt.close(fig)


def _box(rows, keyfn, v, ax):
    groups = {}
    for r in nonmun(rows):
        e = fval(r, "%s_pcterr_terminal" % v)
        if e is None:
            continue
        groups.setdefault(keyfn(r), []).append(e)
    if not groups:
        ax.text(0.5, 0.5, "%s: no valid runs\n(cannot run from EEA - R7)" % v, ha="center", va="center")
        ax.set_title(v); return
    labels = list(groups)
    ax.boxplot([groups[k] for k in labels], tick_labels=labels, showfliers=False)
    ax.axhline(0, color="k", lw=0.6)
    ax.axhline(10, color="r", ls=":", lw=0.6); ax.axhline(-10, color="r", ls=":", lw=0.6)
    ax.set_title(v); ax.set_ylabel("% error vs certified")
    ax.tick_params(axis="x", rotation=30, labelsize=7)


def graph2_box(rows):
    gs = gate_status()
    for split, name, fn in (("mission", "graph2a_box_mission.png", lambda r: r["mission"]),
                            ("arch", "graph2b_box_arch.png", lambda r: r["arch"])):
        fig, axes = plt.subplots(2, 2, figsize=(13, 10))
        for ax, v in zip(axes.ravel(), VARIANTS):
            _box(rows, fn, v, ax)
        fig.suptitle("Graph 2 - %% error by %s (%s). %s. Municipal excluded." % (split, CDXA_LABEL, gs))
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(os.path.join(HERE, name), dpi=110)
        plt.close(fig)


def graph3_certmethod(rows):
    gs = gate_status()
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    for ax, v in zip(axes.ravel(), VARIANTS):
        _box(rows, lambda r: r.get("comp_method", "?"), v, ax)
    fig.suptitle("Graph 3 - %% error by component certification method (%s). %s." % (CDXA_LABEL, gs))
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(HERE, "graph3_box_certmethod.png"), dpi=110)
    plt.close(fig)


def graph4_threeway():
    try:
        rows = list(csv.DictReader(open(os.path.join(HERE, "three_way.csv"))))
    except FileNotFoundError:
        return
    makes = [r["make"] + "\n" + r["config_id"] for r in rows]
    cert = [fval(r, "certified_kwh_km") for r in rows]
    hdev = [fval(r, "hdev_VA_mid") for r in rows]
    oem = [fval(r, "oem_kwh_km") for r in rows]
    x = np.arange(len(rows)); w = 0.27
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.bar(x - w, [c or 0 for c in cert], w, label="certified")
    ax.bar(x, [h or 0 for h in hdev], w, label="HDEV V-A (terminal)")
    ax.bar(x + w, [o or 0 for o in oem], w, label="OEM stated/derived")
    ax.set_xticks(x); ax.set_xticklabels(makes, fontsize=7, rotation=45, ha="right")
    ax.set_ylabel("kWh/km"); ax.legend()
    ax.set_title("Graph 4 - Three-way: certified vs HDEV V-A vs OEM (%s). %s. Blank OEM = [BOB] no derivable figure." % (CDXA_LABEL, gate_status()))
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "graph4_threeway.png"), dpi=110)
    plt.close(fig)


def graph5_summary(rows):
    cell = []
    for v in VARIANTS:
        errs = [fval(r, "%s_pcterr_terminal" % v) for r in nonmun(rows)]
        errs = [e for e in errs if e is not None]
        if not errs:
            cell.append([v, "cannot run (R7)", "-", "-", "-", "-"]); continue
        errs.sort(); n = len(errs)
        med = statistics.median(errs); p10 = errs[int(.1 * n)]; p90 = errs[int(.9 * n)]
        w5 = round(100 * sum(1 for e in errs if abs(e) <= 5) / n)
        w10 = round(100 * sum(1 for e in errs if abs(e) <= 10) / n)
        cell.append([v, "%d" % n, "%.1f%%" % med, "%.0f / %.0f" % (p10, p90), "%d%%" % w5, "%d%%" % w10])
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.axis("off")
    t = ax.table(cellText=cell,
                 colLabels=["variant", "n valid", "median %err", "P10 / P90", "within 5%", "within 10%"],
                 loc="center")
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.6)
    ax.set_title("Graph 5 - Error summary per variant (terminal basis, Municipal excluded).\n%s. %s" % (CDXA_LABEL, gate_status()))
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "graph5_summary_table.png"), dpi=110)
    plt.close(fig)


def main():
    rows = load()
    graph1_parity(rows)
    graph2_box(rows)
    graph3_certmethod(rows)
    graph4_threeway()
    graph5_summary(rows)
    print("wrote graphs 1-5")


if __name__ == "__main__":
    main()
