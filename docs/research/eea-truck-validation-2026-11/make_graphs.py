"""Job 3 graphs. Writes PNGs into this folder. One idea per graph, plain titles,
axis units, legend."""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VARIANTS = ["V-A", "V-B", "V-C", "V-D"]
ARCH_COLOR = {"E2": "#1f77b4", "E3": "#ff7f0e", "E-IEPC": "#2ca02c", "E-IEPC-wheel": "#d62728"}


def load():
    return list(csv.DictReader(open(os.path.join(HERE, "hdev_vs_certified.csv"))))


def gridvals(r, v):
    out = []
    for c in ("lo", "hi"):
        x = r["%s_%s_grid" % (v, c)]
        try:
            out.append(float(x))
        except (ValueError, TypeError):
            pass
    return out


def arch_label(r):
    a = r["arch"]
    return a


def graph1_parity(rows):
    fig, axes = plt.subplots(2, 2, figsize=(12, 11))
    for ax, v in zip(axes.ravel(), VARIANTS):
        for r in rows:
            gv = gridvals(r, v)
            if not gv:
                continue
            cert = float(r["certified_kwh_km"])
            mid = sum(gv) / len(gv)
            col = ARCH_COLOR.get(r["arch"], "gray")
            ax.errorbar(cert, mid, yerr=[[mid - min(gv)], [max(gv) - mid]], fmt="o",
                        ms=3, color=col, ecolor=col, alpha=0.5, capsize=2, lw=0.6)
        lim = 3.5
        xs = np.linspace(0, lim, 10)
        ax.plot(xs, xs, "k-", lw=1, label="y = x")
        ax.plot(xs, xs * 1.05, "k--", lw=0.6, alpha=0.6, label="+/-5%")
        ax.plot(xs, xs * 0.95, "k--", lw=0.6, alpha=0.6)
        ax.plot(xs, xs * 1.10, "k:", lw=0.6, alpha=0.6, label="+/-10%")
        ax.plot(xs, xs * 0.90, "k:", lw=0.6, alpha=0.6)
        ax.set_xlim(0, lim); ax.set_ylim(0, lim)
        ax.set_xlabel("certified kWh/km (grid)")
        ax.set_ylabel("HDEV kWh/km (grid)")
        ax.set_title("Parity, variant %s (error bar = CdxA low..high)" % v)
        ax.legend(loc="upper left", fontsize=8)
    handles = [plt.Line2D([0], [0], marker="o", ls="", color=c, label=a) for a, c in ARCH_COLOR.items()]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=9, title="architecture")
    fig.suptitle("Graph 1: HDEV vs certified kWh/km, per drivetrain variant", fontsize=13)
    fig.tight_layout(rect=[0, 0.04, 1, 0.97])
    fig.savefig(os.path.join(HERE, "graph1_parity.png"), dpi=110)
    plt.close(fig)


def _box_by(rows, key, title, fname):
    cats = sorted({r[key] for r in rows})
    fig, ax = plt.subplots(figsize=(max(9, 1.2 * len(cats) * len(VARIANTS) / 2), 6))
    data = []
    labels = []
    positions = []
    colors = []
    varcol = {"V-A": "#8888ff", "V-B": "#44aa44", "V-C": "#ff8844", "V-D": "#aa44aa"}
    pos = 1
    for cat in cats:
        for v in VARIANTS:
            errs = []
            for r in rows:
                if r[key] != cat:
                    continue
                gv = gridvals(r, v)
                if not gv:
                    continue
                cert = float(r["certified_kwh_km"])
                mid = sum(gv) / len(gv)
                errs.append(100 * (mid - cert) / cert)
            data.append(errs if errs else [0])
            labels.append("%s\n%s" % (cat, v))
            positions.append(pos)
            colors.append(varcol[v])
            pos += 1
        pos += 1
    bp = ax.boxplot(data, positions=positions, widths=0.7, patch_artist=True, showfliers=False)
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c); patch.set_alpha(0.7)
    ax.axhline(0, color="k", lw=1)
    ax.axhline(10, color="gray", ls="--", lw=0.6); ax.axhline(-10, color="gray", ls="--", lw=0.6)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=6, rotation=90)
    ax.set_ylabel("% error vs certified")
    ax.set_title(title)
    ax.set_ylim(-100, 60)
    handles = [plt.Line2D([0], [0], marker="s", ls="", color=c, label=v) for v, c in varcol.items()]
    ax.legend(handles=handles, fontsize=8, ncol=4)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, fname), dpi=110)
    plt.close(fig)


def graph2_mission(rows):
    _box_by(rows, "mission", "Graph 2a: % error by mission and variant", "graph2a_box_mission.png")
    _box_by(rows, "arch", "Graph 2b: % error by architecture and variant", "graph2b_box_arch.png")


def graph3_certmethod(rows):
    _box_by(rows, "comp_method", "Graph 3: % error by component certification method and variant",
            "graph3_box_certmethod.png")


def graph4_threeway(rows):
    # drawn after three_way.csv exists; here build a placeholder bar of a few configs
    path = os.path.join(HERE, "three_way.csv")
    if not os.path.exists(path):
        return
    tw = list(csv.DictReader(open(path)))
    if not tw:
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    labels = []
    x = 0
    width = 0.2
    for r in tw[:12]:
        cert = r.get("certified_kwh_km", "")
        oem = r.get("oem_kwh_km", "")
        try:
            cert = float(cert)
        except ValueError:
            cert = None
        try:
            oem = float(oem)
        except ValueError:
            oem = None
        hdev = r.get("hdev_VC_mid", "")
        try:
            hdev = float(hdev)
        except ValueError:
            hdev = None
        if cert is not None:
            ax.bar(x - width, cert, width, color="black", label="certified" if x == 0 else "")
        if hdev is not None:
            ax.bar(x, hdev, width, color="#2ca02c", label="HDEV V-C" if x == 0 else "")
        if oem is not None:
            ax.bar(x + width, oem, width, color="#d62728", label="OEM" if x == 0 else "")
        labels.append(r.get("config_id", "") + "\n" + r.get("make", ""))
        x += 1
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=6, rotation=90)
    ax.set_ylabel("kWh/km")
    ax.set_title("Graph 4: certified vs HDEV vs OEM per config")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "graph4_threeway.png"), dpi=110)
    plt.close(fig)


def graph5_table(rows):
    # summary table image
    import statistics
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.axis("off")
    header = ["variant", "median %", "10th %", "90th %", "within 5%", "within 10%"]
    tbl = []
    for v in VARIANTS:
        errs = []
        w5 = w10 = 0
        for r in rows:
            gv = gridvals(r, v)
            if not gv:
                continue
            cert = float(r["certified_kwh_km"])
            mid = sum(gv) / len(gv)
            e = 100 * (mid - cert) / cert
            errs.append(e)
            if abs(e) <= 5:
                w5 += 1
            if abs(e) <= 10:
                w10 += 1
        errs.sort()
        n = len(errs)
        tbl.append([v, "%.1f" % statistics.median(errs),
                    "%.1f" % errs[int(0.1 * (n - 1))], "%.1f" % errs[int(0.9 * (n - 1))],
                    "%.0f%%" % (100 * w5 / n), "%.0f%%" % (100 * w10 / n)])
    t = ax.table(cellText=tbl, colLabels=header, loc="center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(10); t.scale(1, 1.6)
    ax.set_title("Graph 5: error summary per variant (grid-side, CdxA-mid)", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "graph5_summary_table.png"), dpi=110)
    plt.close(fig)


def main():
    rows = load()
    graph1_parity(rows)
    graph2_mission(rows)
    graph3_certmethod(rows)
    graph5_table(rows)
    graph4_threeway(rows)
    print("graphs written")


if __name__ == "__main__":
    main()
