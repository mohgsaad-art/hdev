"""F8 — speed-vs-distance graphs with the VECTO v_act overlay.

Three representative stretches per cycle (downhill overspeed, look-ahead coast before a
speed drop, approach to a stop), VECTO vs D1 (no drag) vs D2 (VECTO drag) vs D8 (D2+g).

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
from tests.driver_model.driver_model_v_dragtable import driver_model_dragtable
from tests.driver_model import _vecto_data as D
from tests.driver_model import _vecto_vehicle as VV
from tests.driver_model import _vmod as VM

HERE = os.path.dirname(os.path.abspath(__file__))
VACC = D.load_vacc()
D2_V = [0, 45, 55, 65, 75, 85, 130]
D2_F = [1431, 1431, 1534, 1635, 1935, 2055, 2055]


def runs_for(cyc):
    s, v, grad, stop = D.load_cycle(D.list_cycles()[cyc])
    kw = VV.cycle_driver_kwargs(cyc, "reference")
    d1 = driver_model(s, v, stop, grad, *VACC, P_drag_loss=0.0, **kw)
    d2 = driver_model_dragtable(s, v, stop, grad, *VACC, drag_v_kmh=D2_V, drag_f=D2_F, **kw)
    kw8 = dict(kw); kw8["g"] = 9.80665
    d8 = driver_model_dragtable(s, v, stop, grad, *VACC, drag_v_kmh=D2_V, drag_f=D2_F, **kw8)
    return (s, v, grad, stop), d1, d2, d8


def vecto_trace(cyc):
    run = f"BEV_E2_{cyc}_ReferenceLoad_1Hz"
    runs = VM.run_files()
    if run not in runs:
        return None, None
    c = VM.load_vmod(runs[run])
    return VM.col(c, "dist"), VM.col(c, "v_act")


def plot_stretch(cyc, cyc_data, d1, d2, d8, vdist, vspeed, s0, s1, tag, title):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    if vdist is not None:
        m = (vdist >= s0) & (vdist <= s1)
        ax1.plot(vdist[m], vspeed[m], label="VECTO", color="black", lw=1.6)
    for out, lbl, c in [(d1, "D1 no drag", "tab:blue"),
                        (d2, "D2 VECTO drag", "tab:orange"),
                        (d8, "D8 D2+g", "tab:green")]:
        T, S, V, A, gr, M = out
        mk = (S >= s0) & (S <= s1)
        ax1.plot(S[mk], V[mk] * 3.6, label=lbl, lw=1.1, alpha=0.9)
    s, v, grad, stop = cyc_data
    s = np.asarray(s, float)
    m = (s >= s0) & (s <= s1)
    ax2.plot(s[m], np.asarray(grad, float)[m], color="tab:red", lw=0.8)
    ax1.set_ylabel("speed [km/h]"); ax2.set_ylabel("grade [%]"); ax2.set_xlabel("distance [m]")
    ax1.set_title(f"{cyc}: {title}")
    ax1.legend(loc="best", fontsize=8); ax1.grid(alpha=0.3); ax2.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(HERE, f"{cyc}_{tag}.png")
    fig.savefig(path, dpi=110); plt.close(fig)
    return path


def find_downhill(cyc_data, win=400):
    s, v, grad, stop = cyc_data
    s = np.asarray(s, float); grad = np.asarray(grad, float)
    i = int(np.argmin(grad))
    return max(0.0, s[i] - win), s[i] + win


def find_speeddrop(cyc_data, win=500):
    s, v, grad, stop = cyc_data
    s = np.asarray(s, float); v = np.asarray(v, float)
    i = int(np.argmin(np.diff(v)))
    return max(0.0, s[i] - win), s[i] + win


def find_stop(cyc_data, win=400):
    s, v, grad, stop = cyc_data
    s = np.asarray(s, float); stop = np.asarray(stop, float)
    idx = np.where(stop > 0)[0]
    i = idx[len(idx) // 2] if len(idx) else 0
    return max(0.0, s[i] - win), s[i] + win


def main():
    out = []
    for cyc in ("RegionalDelivery", "UrbanDelivery"):
        cyc_data, d1, d2, d8 = runs_for(cyc)
        vdist, vspeed = vecto_trace(cyc)
        for finder, tag, title in [
            (find_downhill, "downhill", "downhill overspeed stretch"),
            (find_speeddrop, "coast", "look-ahead coast before a speed drop"),
            (find_stop, "stop", "approach to a stop"),
        ]:
            s0, s1 = finder(cyc_data)
            out.append(plot_stretch(cyc, cyc_data, d1, d2, d8, vdist, vspeed, s0, s1, tag, title))
    for p in out:
        print("wrote", os.path.relpath(p, os.path.dirname(HERE)))


if __name__ == "__main__":
    main()
