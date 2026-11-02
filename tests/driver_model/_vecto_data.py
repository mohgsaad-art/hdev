"""Shared loaders for the driver-model tests.

Reads the real VECTO declaration resources that ARE in the repo
(reference/vecto/resources/...): the .vdri mission cycles and Truck.vacc.

It also builds a stand-in "generic E2" coasting set-up (mass / Crr / CdxA table).
IMPORTANT: harness v1.7 and the real generic-E2 component files were NOT supplied
(see Part 0.1 of the prompt). The numbers used for the coasting set-up below are
therefore either sourced from the VECTO files that ARE present (Truck.vacc) or are
clearly labelled ILLUSTRATIVE. No coasting metric computed with the ILLUSTRATIVE
vehicle is compared against VECTO .vmod output anywhere — those comparisons are
BLOCKED and reported as such.
"""
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
RES = os.path.join(_REPO, "reference", "vecto", "resources")
CYCLES_DIR = os.path.join(RES, "MissionCycles")


def load_vacc(path=None):
    """Return (vacc_v_kmh, vacc_acc, vacc_dec) from a .vacc CSV.

    Default: the VECTO declaration Truck.vacc (reference/.../VACC/Truck.vacc).
    """
    if path is None:
        path = os.path.join(RES, "VACC", "Truck.vacc")
    vs, acc, dec = [], [], []
    with open(path, encoding="latin-1") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.lower().startswith("v "):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue
            try:
                vs.append(float(parts[0]))
                acc.append(float(parts[1]))
                dec.append(float(parts[2]))
            except ValueError:
                continue
    return vs, acc, dec


# Truck.vacc, hard-coded as a fallback so helper tests do not depend on file IO.
# Source: reference/vecto/resources/VACC/Truck.vacc [VECTO v5.1.3].
TRUCK_VACC_V = [0.0, 25.0, 50.0, 60.0, 120.0]
TRUCK_VACC_ACC = [1.0, 1.0, 0.642857143, 0.5, 0.5]
TRUCK_VACC_DEC = [-1.0, -1.0, -1.0, -0.5, -0.5]


def list_cycles():
    """Return {name: path} for every .vdri in the repo."""
    out = {}
    if not os.path.isdir(CYCLES_DIR):
        return out
    for fn in sorted(os.listdir(CYCLES_DIR)):
        if fn.lower().endswith(".vdri"):
            out[fn[:-5]] = os.path.join(CYCLES_DIR, fn)
    return out


def load_cycle(path):
    """Parse a .vdri file into (s, v, grad, stop) lists.

    Columns: <s> [m], <v> [km/h], <grad> [%], <stop> [s]. Extra columns
    (HW, PTO) are ignored here. The grade column is the road gradient at the
    waypoint; VECTO's reader uses entries[i-1].RoadGradientPercent for the
    segment altitude rise, which is exactly how the code of record uses
    gr_wp[:-1] (see reference_copy.driver_model, 'rise =' line).
    """
    s, v, grad, stop = [], [], [], []
    with open(path, encoding="latin-1") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("<"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 4:
                continue
            try:
                s.append(float(parts[0]))
                v.append(float(parts[1]))
                grad.append(float(parts[2]))
                stop.append(float(parts[3]))
            except ValueError:
                continue
    return s, v, grad, stop


# ---------------------------------------------------------------------------
# Generic E2 coasting set-up.
#
# curb 4670 kg + body B2 1900 kg + reference payload 3019.6 kg  => ~9589.6 kg.
# These three numbers were quoted in the prompt Appendix 3 "from earlier sessions,
# re-check in the VECTO files"; the .vveh/Payloads.csv confirmation is partly
# BLOCKED (BatteryElectricVehicle.vveh not supplied). Treated as [ASSUMPTION]
# pending the component files. Crr and the CdxA table below are ILLUSTRATIVE
# (flat CdxA), chosen only so coasting-on code paths can be exercised; they are
# NOT VECTO's reference CdxA table (which needs the crosswind engine + .vveh).
# ---------------------------------------------------------------------------
E2_CURB = 4670.0
E2_BODY_B2 = 1900.0
E2_REF_PAYLOAD = 3019.6
E2_REF_MASS = E2_CURB + E2_BODY_B2 + E2_REF_PAYLOAD  # ~9589.6 kg  [ASSUMPTION]
E2_EMPTY_MASS = E2_CURB + E2_BODY_B2                  # ~6570 kg    [ASSUMPTION]
E2_GVW = 16000.0                                     # group 2 max  [ASSUMPTION / ILLUSTRATIVE]

E2_CRR = 0.0055            # ILLUSTRATIVE (typical regional-delivery Crr order of magnitude)
E2_M_RED_WHEELS = 200.0   # ILLUSTRATIVE stand-in for ReducedMassWheels
# Flat CdxA table, ILLUSTRATIVE. Real reference table needs the crosswind engine.
E2_CDXA_V = [0.0, 60.0, 90.0, 130.0]     # km/h
E2_CDXA = [4.83, 4.83, 4.83, 4.83]       # m^2 (CdA quoted in Appendix 3)


def coasting_kwargs(coast_mass=None, p_drag=0.0):
    """kwargs for driver_model to turn coasting ON with the ILLUSTRATIVE E2 set-up."""
    if coast_mass is None:
        coast_mass = E2_REF_MASS
    return dict(
        coast_mass=coast_mass,
        m_red_wheels=E2_M_RED_WHEELS,
        cdxa_v=E2_CDXA_V,
        cdxa=E2_CDXA,
        Crr=E2_CRR,
        P_drag_loss=p_drag,
    )
