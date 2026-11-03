"""Generate speed-vs-distance graphs for the review (Part D visual, D1 vs coast-on).

Because VECTO .vmod files were NOT supplied (BLOCKED), these graphs show the code
of record with coasting OFF (D1-style, coast_mass=None) vs coasting ON (ILLUSTRATIVE
E2). They illustrate the three representative stretches the prompt asks for:
a downhill overspeed stretch, a look-ahead coast before a speed drop, and a stop.
The VECTO trace overlay is left as a TODO for Bob once the .vmod files exist.

Run: MPLCONFIGDIR=/tmp/mpl python docs/research/driver-model-review-2026-11/make_graphs.py
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from tests.driver_model.reference_copy import driver_model
from tests.driver_model import _vecto_data as D

HERE = os.path.dirname(os.path.abspath(__file__))


def run_both(name):
    s, v, grad, stop = D.load_cycle(D.list_cycles()[name])
    off = driver_model(s, v, stop, grad, *D.load_vacc())
    on = driver_model(s, v, stop, grad, *D.load_vacc(), **D.coasting_kwargs())
    return off, on, (s, v, grad, stop)


def plot_stretch(name, off, on, cyc, s0, s1, tag, title):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    for out, lbl, c in [(off, "D1 coast OFF", "tab:blue"), (on, "coast ON (illustrative)", "tab:orange")]:
        T, S, V, A, gr, M = out
        mask = (S >= s0) & (S <= s1)
        ax1.plot(S[mask], V[mask] * 3.6, label=lbl, color=c, lw=1.2)
    s, v, grad, stop = cyc
    s = np.asarray(s, float)
    # grade on lower axis
    mask = (s >= s0) & (s <= s1)
    ax2.plot(s[mask], np.asarray(grad, float)[mask], color="tab:green", lw=0.8)
    ax1.set_ylabel("speed [km/h]")
    ax2.set_ylabel("grade [%]")
    ax2.set_xlabel("distance [m]")
    ax1.set_title(f"{name}: {title}")
    ax1.legend(loc="best", fontsize=8)
    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(HERE, f"{name}_{tag}.png")
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def find_downhill(cyc, win=400):
    s, v, grad, stop = cyc
    s = np.asarray(s, float)
    grad = np.asarray(grad, float)
    i = int(np.argmin(grad))
    return max(0.0, s[i] - win), s[i] + win


def find_speeddrop(cyc, win=500):
    s, v, grad, stop = cyc
    s = np.asarray(s, float)
    v = np.asarray(v, float)
    dv = np.diff(v)
    i = int(np.argmin(dv))
    return max(0.0, s[i] - win), s[i] + win


def find_stop(cyc, win=400):
    s, v, grad, stop = cyc
    s = np.asarray(s, float)
    stop = np.asarray(stop, float)
    idx = np.where(stop > 0)[0]
    i = idx[len(idx) // 2] if len(idx) else 0
    return max(0.0, s[i] - win), s[i] + win


def main():
    outputs = []
    for name in ("RegionalDelivery", "UrbanDelivery"):
        off, on, cyc = run_both(name)
        for finder, tag, title in [
            (find_downhill, "downhill", "downhill overspeed stretch"),
            (find_speeddrop, "coast", "look-ahead coast before a speed drop"),
            (find_stop, "stop", "approach to a stop"),
        ]:
            s0, s1 = finder(cyc)
            outputs.append(plot_stretch(name, off, on, cyc, s0, s1, tag, title))
    for p in outputs:
        print("wrote", os.path.relpath(p, os.path.dirname(HERE)))


if __name__ == "__main__":
    main()
