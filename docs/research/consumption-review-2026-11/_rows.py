"""(Copied from the aux/PTO review, PR #31; unchanged except where noted.)
Helpers: read VECTO .vmod rows, read .vdri with its PTO column, and run Bob's notebook driver_model on the
E2 reference set-up (same recipe as the drag-default test PR #23 / driver thresholds in m/s from PR #30 Part D).

Nothing here edits engine code.  Deterministic.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("VECTO_SRC", "/projects/sandbox/vecto-src")
from _load_notebook import NS, REPO  # noqa: E402

sys.path.insert(0, REPO)
from tests.driver_model import _vecto_data as D  # noqa: E402
from tests.driver_model import _vecto_vehicle as VV  # noqa: E402

VMOD_DIR = os.path.join(REPO, "docs", "research", "vecto")
CYCLES = os.path.join(REPO, "reference", "vecto", "resources", "MissionCycles")
LOADINGS = {"ReferenceLoad": 3019.5882, "LowLoading": 603.9176}           # kg, from the drag-default test (VECTO close-out)
DRIVER_THRESHOLDS_MS = dict(lac_min_v=50.0 / 3.6, os_min_v=50.0 / 3.6, os_allowed=2.5 / 3.6, v_min_coast=5.0 / 3.6)

# DriverAction enum, VectoCore/.../Driver.cs 51-58 (b8d6126)
DRIVER_ACTION = {0: "Halt", 2: "Roll", 4: "Coast", 6: "Accelerate", -5: "Brake"}


def read_vmod(cycle, loading):
    f = os.path.join(VMOD_DIR, f"BEV_E2_{cycle}_{loading}_1Hz.vmod")
    d = pd.read_csv(f, skiprows=1, encoding="utf-8-sig")
    return d


def read_vdri(name):
    """returns dict(s, v_kmh, grad, stop, pto) from a .vdri (5 columns: s, v, grad, stop, PTO)."""
    rows = []
    with open(os.path.join(CYCLES, name + ".vdri"), encoding="utf-8-sig", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("<"):
                continue
            p = [x.strip() for x in line.split(",")]
            if len(p) < 4:
                continue
            rows.append([float(x) for x in p[:4]] + [float(p[4]) if len(p) > 4 and p[4] != "" else 0.0])
    a = np.array(rows)
    return dict(s=a[:, 0], v_kmh=a[:, 1], grad=a[:, 2], stop=a[:, 3], pto=a[:, 4])


_DRAG = {}


def e2_drag():
    if "d" not in _DRAG:
        sys.path.insert(0, os.path.join(REPO, "docs", "research", "drag-default-test-2026-11"))
        import _e2_drag as E2
        v, F, _ = E2.build_drag_table()
        _DRAG["d"] = ([x / 3.6 for x in v], list(F))
    return _DRAG["d"]


def run_driver_e2(cyc, loading="ReferenceLoad", stop_override=None, coast=True):
    """Notebook driver_model on the E2 reference vehicle.  cyc = dict from read_vdri (or any dict with the same keys).
    stop_override = FINAL standing times per waypoint (PTO time already added by the parser)."""
    stop = cyc["stop"] if stop_override is None else stop_override
    vacc = D.load_vacc()
    mass = VV.M_VEHICLE + LOADINGS[loading]
    kw = {}
    if coast:
        dv, dF = e2_drag()
        kw = dict(coast_mass=mass, m_red_wheels=VV.M_RED_WHEELS, cdxa_v=[x / 3.6 for x in VV.CDXA_V], cdxa=list(VV.CDXA_REF),
                  Crr=VV.crr_total_vecto(mass), rho=VV.RHO_VECTO, g=VV.G, drag_v=dv, drag_F=dF, **DRIVER_THRESHOLDS_MS)
    T, S, V, A, G, M = NS["driver_model"](cyc["s"], [x / 3.6 for x in cyc["v_kmh"]], stop, cyc["grad"],
                                          [x / 3.6 for x in vacc[0]], vacc[1], vacc[2], **kw)
    return T, S, V, A, G, M
