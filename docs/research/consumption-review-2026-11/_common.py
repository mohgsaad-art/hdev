"""Shared helpers for the consumption-engine review (13 Nov 2026).

Copied from the force-engine review (PR #30, docs/research/force-engine-review-2026-11/_common.py) and adapted
to the 13 Nov force_engine signature (6 return values, J_rotor / i_total inputs).

(Original header follows.) Shared helpers for the force-engine review (12 Nov 2026).

Everything here is TEST/REVIEW glue. No engine code is changed. Engine functions are taken
from Bob's notebook through _load_notebook.load() (code of record, 12 Nov 2026).

Vehicle values are read from VECTO files (commit b8d6126 of mohgsaad-art/VECTO, branch
IEPC-experiments) and from the repo copy of the declaration resources in
reference/vecto/resources. Every constant carries its source in a comment.
"""
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))   # docs/research/<folder> -> repo root
if REPO not in sys.path:
    sys.path.insert(0, REPO)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from _load_notebook import load as _load                      # noqa: E402
from tests.driver_model import _vmod as VM                      # noqa: E402
from tests.driver_model import _vecto_data as D                 # noqa: E402

NS = _load()
force_engine_nb = NS["force_engine"]
crosswind_engine = NS["crosswind_engine"]
driver_model = NS["driver_model"]
consumption_engine = NS["consumption_engine"]
payload_engine = NS["payload_engine"]

OUT = HERE                       # CSVs/graphs go next to the scripts


def out(name):
    return os.path.join(OUT, name)


def write_csv(name, rows, fieldnames=None):
    rows = list(rows)
    fieldnames = fieldnames or list(rows[0].keys())
    with open(out(name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print("wrote", os.path.relpath(out(name), REPO))


# ---------------------------------------------------------------- constants [VECTO]
G = 9.80665          # [VECTO] DeclarationData.cs:72  GravityAccelleration
RHO_VECTO = 1.188    # [VECTO] DeclarationData.cs:74  AirDensity
BETA = 0.9           # [VECTO] Physics.cs:51 RollResistanceExponent
CDXA_V = np.arange(60, 131, 5.0)   # [VECTO] Constants.cs:355-357 (km/h)
V_DECL, H_DECL, HELLMANN = 3.0, 4.0, 0.2    # [VECTO] Physics.cs:56-66
R_DYN = 0.867 * 3.05 / (2 * np.pi)          # [VECTO] Wheels.csv 265/70 R19.5: d=867 mm, F=3.05 -> 0.4209 m (also .vsum "r_dyn")
HEIGHT = 3.75                               # [VECTO] SegmentTable.csv row group 2 4x2 10-12 t

# ---------------------------------------------------------------- vehicle sets
# Truck (all missions): BatteryElectricVehicle.vveh (CurbWeight 4670, CdA 4.83, axle RRC/FzISO, wheel inertia 6.5)
TRUCK_RRC = [0.0065, 0.0075]
TRUCK_FZ = [20850.0, 20850.0]
TRUCK_WHEELS = [2, 4]            # axle 2 has twin tyres
TRUCK_WHEEL_INERTIA = 6.5        # kg m2 per wheel, Wheels.csv 265/70 R19.5
CURB = 4670.0
BODY_B2 = 1900.0                 # Body_Trailers_Weights.csv B2
TRAILER_T1 = 3400.0              # Body_Trailers_Weights.csv T1 curb mass
CDXA0_SOLO = 4.83
CDXA_DELTA_T1 = 1.3              # Body_Trailers_Weights.csv T1 delta CdxA (long haul)
A123 = {"RigidSolo": (0.013526, 0.017746, -0.000666),      # VCDV_parameters.csv rows 2-3
        "RigidTrailer": (0.017125, 0.072275, -0.004148)}

# Trailer axle data [VECTO] Declaration.Trailer (DeclarationData.cs:835-844): RRC 0.0055, FzISO 37500 N, single tyres.
# T1 has 2 axles with 235/75 R17.5 (Body_Trailers_Weights.csv row T1; Wheels.csv inertia 4.5 per wheel).
TRAILER_RRC, TRAILER_FZ, TRAILER_WHEEL_INERTIA = 0.0055, 37500.0, 4.5

# axle weight shares: SegmentTable.csv row "2 / RigidTruck / 4x2 / 10-12 t"
SHARES = {
    "solo": dict(truck=[0.45, 0.55], trailer=[]),                 # "Truck Axles - Other" 45/55
    "longhaul": dict(truck=[0.225, 0.325], trailer=[0.225, 0.225]),  # "Truck Axles - Long haul" 22.5/32.5 + "Trailer Axles - Long haul" 45 /2 axles
}

# loadings [kg] from BEV_E2.vsum (Loading column), one per job
LOADING = {
    ("LongHaul", "LowLoading"): 1303.9176, ("LongHaul", "ReferenceLoad"): 9841.1765,
    ("RegionalDelivery", "LowLoading"): 603.9176, ("RegionalDelivery", "ReferenceLoad"): 3019.5882,
    ("UrbanDelivery", "LowLoading"): 603.9176, ("UrbanDelivery", "ReferenceLoad"): 3019.5882,
}
# total vehicle mass as printed in BEV_E2.vsum (check column)
VSUM_TOTAL_MASS = {
    ("LongHaul", "LowLoading"): 11273.9176, ("LongHaul", "ReferenceLoad"): 19811.1765,
    ("RegionalDelivery", "LowLoading"): 7173.9176, ("RegionalDelivery", "ReferenceLoad"): 9589.5882,
    ("UrbanDelivery", "LowLoading"): 7173.9176, ("UrbanDelivery", "ReferenceLoad"): 9589.5882,
}
VSUM_TOTAL_RRC = {
    ("LongHaul", "LowLoading"): 0.00695545173240238, ("LongHaul", "ReferenceLoad"): 0.00657418317124784,
    ("RegionalDelivery", "LowLoading"): 0.00746097336455379, ("RegionalDelivery", "ReferenceLoad"): 0.00724754853356735,
    ("UrbanDelivery", "LowLoading"): 0.00746097336455379, ("UrbanDelivery", "ReferenceLoad"): 0.00724754853356735,
}


class Vehicle:
    """One VECTO declaration vehicle (truck, or truck + trailer for LongHaul)."""

    def __init__(self, cycle, loading):
        self.cycle, self.loading = cycle, loading
        longhaul = cycle == "LongHaul"
        self.key = (cycle, loading)
        sh = SHARES["longhaul" if longhaul else "solo"]
        self.shares = np.array(sh["truck"] + sh["trailer"])
        self.rrc = np.array(TRUCK_RRC + [TRAILER_RRC] * len(sh["trailer"]))
        self.fz = np.array(TRUCK_FZ + [TRAILER_FZ] * len(sh["trailer"]))
        self.nwheels = np.array(TRUCK_WHEELS + [2] * len(sh["trailer"]))
        self.theta_red = TRUCK_WHEEL_INERTIA * sum(TRUCK_WHEELS) + (
            TRAILER_WHEEL_INERTIA * 2 * len(sh["trailer"]))      # VehicleData.cs:308 sum(nWheels * inertia)
        self.m_empty = CURB + BODY_B2 + (TRAILER_T1 if longhaul else 0.0)
        self.m_payload = LOADING[self.key]
        self.mass = self.m_empty + self.m_payload
        self.cdxa0 = CDXA0_SOLO + (CDXA_DELTA_T1 if longhaul else 0.0)
        self.a123 = A123["RigidTrailer" if longhaul else "RigidSolo"]
        self.r_dyn = R_DYN
        self.m_red_wheels = self.theta_red / R_DYN ** 2

    def crr_total_vecto(self, mass=None, beta=BETA):
        """VECTO TotalRollResistanceCoefficient at a total mass [VECTO] VehicleData.cs:292-311."""
        m = self.mass if mass is None else mass
        base = self.shares * m * G / self.fz / self.nwheels
        return float(np.sum(self.shares * self.rrc * base ** (beta - 1)))

    def crr_eff(self, beta=BETA):
        """Mass-free constant: F_roll = crr_eff * g * m**beta  (harness crr_eff, extended to any axle set)."""
        return float(G ** (beta - 1) * np.sum(self.shares ** beta * self.rrc * (1.0 / self.fz / self.nwheels) ** (beta - 1)))

    def cdxa_table(self, beta_limit=None):
        """CdxA_eff on CDXA_V from Bob's crosswind_engine at declaration wind (3 m/s at 4 m, Hellmann 0.2)."""
        a1, a2, a3 = self.a123
        W1, W2 = crosswind_engine(HEIGHT, np.array([V_DECL]), H_DECL, a1, a2, a3, HELLMANN,
                                  HEIGHT / 10, 10, CDXA_V, beta_limit)
        return self.cdxa0 * np.asarray(W1)[0] + np.asarray(W2)[0]


def load_vmod_run(cycle, loading):
    runs = VM.run_files()
    return VM.load_vmod(runs[f"BEV_E2_{cycle}_{loading}_1Hz"])


def vmod_rows(cols):
    """Per-row inputs for force_engine, reconstructed per Q7 (v_act is the interval mean).
    Returns dict with v1, v2 (acc-based), v1c, v2c (chain), v_act (m/s), acc, dt, grad %, etc."""
    c = lambda n: VM.col(cols, n)
    dt = c("dt")
    v_act = c("v_act") / 3.6
    acc = c("acc")
    return dict(t=c("time"), dt=dt, dist=c("dist"), v_act=v_act, acc=acc, grad=c("grad"),
                altitude=c("altitude"),
                v1=v_act - acc * dt / 2, v2=v_act + acc * dt / 2)


def trace_for_engine(r, how="acc"):
    """Return (speed_start, accel) to feed force_engine for a given reconstruction.
    how: 'acc'  -> v1 = v_act - acc*dt/2 (local, no drift)           [default]
         'chain'-> v1[0]=0, v2 = 2*v_act - v1, v1[k+1] = v2[k]
         'naive'-> start speed taken as v_act (what happens if the column is read as the start speed)"""
    if how == "acc":
        return np.maximum(r["v1"], 0.0), r["acc"]
    if how == "naive":
        return r["v_act"], r["acc"]
    if how == "chain":
        n = len(r["v_act"])
        v1 = np.zeros(n)
        v2 = np.zeros(n)
        for k in range(n):
            v1[k] = v2[k - 1] if k else 0.0
            v2[k] = max(2 * r["v_act"][k] - v1[k], 0.0)
        return v1, (v2 - v1) / r["dt"]
    raise ValueError(how)


def vecto_terms(cols):
    c = lambda n: VM.col(cols, n) * 1000.0     # kW -> W
    return dict(P_roll=c("P_roll"), P_air=c("P_air"), P_slope=c("P_slope"),
                P_veh_inertia=c("P_veh_inertia"), P_wheel_inertia=c("P_wheel_inertia"),
                P_trac=c("P_trac"), P_wheel_in=c("P_wheel_in"),
                cdxa=VM.col(cols, "CdxA_eff"))


def cdxa_interp(v_avg_ms, tab, v_kmh=CDXA_V):
    """HDEV rule: linear in km/h, ends held (np.interp does exactly this)."""
    return np.interp(v_avg_ms * 3.6, v_kmh, tab)


def hdev_terms(veh, v_start, acc, dt, grad_pct, cdxa_row=None, tab=None, rho=RHO_VECTO,
               theta_red=None, beta=BETA, mass=None, extra_theta=0.0, grade_mode="atan", cdxa_speed="avg"):
    """Wheel-power terms with Bob's force_engine (called unchanged) + the P_wheel equation (step 4).

    grade_mode: 'atan' (Bob) | 'asin' | 'none' (use the % as sin directly) -- variants are applied by changing
    the grade INPUT so force_engine itself stays untouched:
        asin: we want sin(theta)=G -> pass grade_pct such that sin(atan(x))=G, i.e. x = G/sqrt(1-G^2)
        none: want sin(theta)=G and cos(theta)=1 is NOT reachable through force_engine -> handled below by recomputation
    """
    m = veh.mass if mass is None else mass
    th = veh.theta_red + extra_theta if theta_red is None else theta_red
    g_in = np.asarray(grad_pct, float)
    if grade_mode == "asin":
        G_ = g_in / 100.0
        g_in = 100.0 * G_ / np.sqrt(1.0 - G_ ** 2)
    k_lin, k_roll, k_rot, _k_rotor, L, v_avg = force_engine_nb(G, veh.crr_eff(beta), v_start, acc, dt, g_in, veh.r_dyn, th, 0.0, 1.0)
    if grade_mode == "none":      # sin(theta) -> G, cos -> 1 : recompute the two grade-dependent coefficients
        Gr = np.asarray(grad_pct, float) / 100.0
        k_lin = (G * Gr + acc) * v_avg
        k_roll = veh.crr_eff(beta) * G * v_avg
    if cdxa_row is None:
        sp = v_avg if cdxa_speed == "avg" else (np.asarray(v_start) if cdxa_speed == "start" else
                                                  np.maximum(np.asarray(v_start) + np.asarray(acc) * np.asarray(dt), 0.0))
        cdxa_row = cdxa_interp(sp, tab)
    # split k_lin into slope and inertia parts for per-term reporting (same formulas, no change of Bob's maths)
    if grade_mode == "atan":
        s = np.sin(np.arctan(np.asarray(grad_pct, float) / 100.0))
    elif grade_mode == "asin":
        s = np.asarray(grad_pct, float) / 100.0
    else:
        s = np.asarray(grad_pct, float) / 100.0
    P_slope = m * G * s * v_avg
    P_inertia = m * acc * v_avg
    P_roll = m ** beta * k_roll
    P_air = rho * cdxa_row * L
    P_rot = k_rot
    assert np.allclose(m * k_lin, P_slope + P_inertia, rtol=1e-9, atol=1e-6)
    return dict(P_roll=P_roll, P_air=P_air, P_slope=P_slope, P_veh_inertia=P_inertia, P_wheel_inertia=P_rot,
                P_trac=P_roll + P_air + P_slope + P_inertia, P_wheel=m * k_lin + P_roll + k_rot + P_air,
                cdxa=cdxa_row, v_avg=v_avg, L=L)


def energy_kwh(P, dt):
    E = np.asarray(P) * np.asarray(dt) / 3.6e6
    return dict(net=float(E.sum()), pos=float(E[E > 0].sum()), neg=float(E[E < 0].sum()))


# ---------------------------------------------------------------- driver runs (Part B/D/E)
def e2_drag_table():
    """E2 motor+gearbox+axle drag force table (km/h list, N list) from the drag-default test (Step 1)."""
    sys.path.insert(0, os.path.join(REPO, "docs", "research", "drag-default-test-2026-11"))
    import _e2_drag as E2
    v, F, _ = E2.build_drag_table()
    return list(v), list(F)


_DRAG_CACHE = {}


def run_driver(cycle, loading="ReferenceLoad", coast=True, dt=1.0, beta=BETA, drag=True, cycle_arrays=None):
    """Bob's notebook driver_model on a VECTO cycle for the E2 reference vehicle.

    Units follow the notebook header: waypoint speeds, .vacc speeds and the CdxA grid in m/s (parser /3.6).
    coast_mass = the vehicle mass of this loading (Bob: coasting runs at a fixed reference vehicle).
    Rolling: beta form with Crr_eff (Bob's decision), g = 9.80665, rho = 1.188.
    """
    veh = Vehicle("RegionalDelivery" if cycle != "LongHaul" else "LongHaul", loading)
    if cycle_arrays is None:
        s, v_kmh, grad, stop = D.load_cycle(D.list_cycles()[cycle])
    else:
        s, v_kmh, grad, stop = cycle_arrays
    vv, va, vd = D.load_vacc()
    kw = {}
    if coast:
        if "drag" not in _DRAG_CACHE:
            _DRAG_CACHE["drag"] = e2_drag_table()
        dv, dF = _DRAG_CACHE["drag"]
        cd = veh.cdxa_table()
        # NOTE (seen in passing): the notebook defaults lac_min_v=50, os_min_v=50, os_allowed=2.5, v_min_coast=5 are
        # km/h-sized numbers but are compared with speeds in m/s. They are passed here in m/s (value/3.6), as the
        # header comment says the parser must do. With the defaults left alone, coasting and overspeed never switch on.
        kw = dict(coast_mass=veh.mass, m_red_wheels=veh.m_red_wheels, cdxa_v=list(CDXA_V / 3.6), cdxa=list(cd),
                  Crr=veh.crr_eff(beta), beta=beta, rho=RHO_VECTO, g=G,
                  lac_min_v=50.0 / 3.6, os_min_v=50.0 / 3.6, os_allowed=2.5 / 3.6, v_min_coast=5.0 / 3.6)
        if drag:
            kw.update(drag_v=[x / 3.6 for x in dv], drag_F=list(dF))
    return driver_model(s, [x / 3.6 for x in v_kmh], stop, grad, [x / 3.6 for x in vv], va, vd, dt=dt, **kw), veh
