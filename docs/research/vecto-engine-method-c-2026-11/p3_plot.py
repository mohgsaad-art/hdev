import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(l for l in open(os.path.join(HERE, "p2_per_result.csv")) if not l.startswith("#")))
fig, axs = plt.subplots(1, 2, figsize=(14, 4.6), gridspec_kw=dict(width_ratios=[3, 1.6]))
for ax, cid, title in zip(axs, ("C0091", "C0059"), ("IVECO S-eWay (C0091), 12 results", "Fuso eCanter (C0059), 4 results")):
    r = [x for x in rows if x["truck"] == cid]
    lab = ["%s\n%s kg" % (x["mission"].replace(" Delivery", "").replace("Long Haul", "LH").replace("Regional", "Reg").replace("Construction", "Constr"), x["payload_kg"]) for x in r]
    xs = np.arange(len(r)); w = 0.38
    ax.bar(xs - w / 2, [float(x["HDEV_hide_one_err_pct"]) for x in r], w, label="HDEV engine (PR #37)")
    ax.bar(xs + w / 2, [float(x["VECTO_hide_one_err_pct"]) for x in r], w, label="VECTO engine")
    ax.axhline(0, color="k", lw=.8); ax.axhline(5, color="k", ls=":", lw=.8); ax.axhline(-5, color="k", ls=":", lw=.8)
    ax.set_xticks(xs); ax.set_xticklabels(lab, fontsize=6.5); ax.set_ylabel("hide-one error vs certified [%]"); ax.set_title(title, fontsize=10); ax.grid(axis="y", alpha=.3)
axs[0].legend(fontsize=8)
fig.suptitle("Method C, hide-one-result test: same certified results, two engines (calibration on VECTO certified results, not validation)", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "p3_hide_one.png"), dpi=110)
print("wrote p3_hide_one.png")
