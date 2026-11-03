"""VECTO generic-E2 reference vehicle, reconstructed from harness v1.7.

Every value here is sourced from `docs/research/vecto/hdev_test_harness_v1.7.py`
(which cites the VECTO files). This lets the Part D/E/F comparison use VECTO's
*actual* reference vehicle (masses, Crr, reduced wheels, r_dyn, and the declaration
CdxA table) WITHOUT needing the live Colab notebook's engine functions — the CdxA
reference curve is reproduced from the harness's own independent transcription of
VECTO AirdragDataAdapter.cs (harness test T01), not from the notebook crosswind_engine.

VECTO version of the .vmod/.vsum: 5.1.6-RC (22 Oct 2026). Source audit was v5.1.3.
"""
import math

import numpy as np

# --- sourced constants (harness v1.7) ---
G = 9.80665               # [VECTO] DeclarationData.cs
RHO_VECTO = 1.188         # [VECTO]
BETA = 0.9                # [VECTO] Physics.cs RollResistanceExponent
CURB = 4670.0             # [VECTO] BatteryElectricVehicle.vveh
BODY_MASS = 1900.0        # [VECTO] Body_Trailers_Weights.csv B2
TPMLM = 11990.0           # [VECTO] MassMax
CDXA0 = 4.83              # [VECTO] CdA
AXLE_SHARE = [0.45, 0.55]
AXLES_RRC = [0.0065, 0.0075]
AXLES_FZ = [20850.0, 20850.0]
AXLES_WHEELS = [2, 4]
WHEEL_INERTIA = 6.5       # per wheel kg m^2
V_DECL, H_DECL, HELLMANN = 3.0, 4.0, 0.2   # declaration wind
VEH_HEIGHT = 3.75
A123 = (0.013526, 0.017746, -0.000666)     # VCDV_parameters RigidSolo
CDXA_V = np.arange(60, 131, 5.0)           # [VECTO] Constants.cs 60..130 step 5


def payload_ref():
    """50 % column of Payloads.csv interpolated at TPMLM [VECTO]."""
    gvw = [3500, 7400, 7500, 16000]
    p50 = [420, 1210, 1250, 4600]
    return float(np.interp(TPMLM, gvw, p50))


M_VEHICLE = CURB + BODY_MASS          # 6570 kg
PAYLOAD_REF = payload_ref()           # ~3019.6 kg
M_REF = M_VEHICLE + PAYLOAD_REF       # ~9589.6 kg

R_DYN = 0.867 * 3.05 / (2 * math.pi)  # [VECTO] Wheels.csv 265/70 R19.5
THETA_WHEELS = WHEEL_INERTIA * sum(AXLES_WHEELS)   # 39.0
M_RED_WHEELS = THETA_WHEELS / R_DYN ** 2           # ~220 kg [ASSUMP]


def crr_total_vecto(m):
    """VECTO's mass-dependent total rolling coefficient [VECTO] VehicleData.cs 292-311."""
    s = np.array(AXLE_SHARE)
    rrc = np.array(AXLES_RRC)
    fz = np.array(AXLES_FZ)
    n = np.array(AXLES_WHEELS)
    return float(np.sum(s * rrc * (s * m * G / fz / n) ** (BETA - 1)))


def crr_eff(beta=BETA):
    """Constant so F_roll = crr_eff * g * m^beta reproduces VECTO (force-engine form)."""
    s = np.array(AXLE_SHARE)
    rrc = np.array(AXLES_RRC)
    fz = np.array(AXLES_FZ)
    n = np.array(AXLES_WHEELS)
    return float(G ** (beta - 1) * np.sum(s * rrc * (s / fz / n) ** (beta - 1)))


def cdxa_ref_table():
    """Reference CdxA table (one value per CDXA_V speed), reproduced from the harness's
    independent transcription of VECTO AirdragDataAdapter.cs 20-87 (declaration wind
    3 m/s at 4 m, Hellmann 0.2, 10-degree yaw grid). This is the table the driver model
    reads at the fixed reference vehicle."""
    a1, a2, a3 = A123
    out = []
    for spd in CDXA_V:
        vv = spd / 3.6
        tot = 0.0
        for hp in range(5, 100, 10):
            vw = V_DECL * (hp / 100 * VEH_HEIGHT / H_DECL) ** HELLMANN
            for al in range(0, 181, 10):
                vx = vv + vw * math.cos(math.radians(al))
                vy = vw * math.sin(math.radians(al))
                b = math.degrees(math.atan(vy / vx))
                cda = CDXA0 + a1 * b + a2 * b * b + a3 * b ** 3
                share = (5 if al in (0, 180) else 10) / 180
                tot += 0.1 * share * cda * (vx * vx + vy * vy) / (vv * vv)
        out.append(tot)
    return np.array(out)


CDXA_REF = cdxa_ref_table()

# --- per-cycle masses, taken directly from BEV_E2.vsum (VECTO's own output) ---
# Regional/Urban (RigidSolo, no trailer): curb 4670 + body 1900 = 6570 vehicle.
#   reference loading 3019.6 -> total 9589.6 ; low loading 603.9 -> total 7173.9
# LongHaul (RigidTrailer): curb 4670 + body B2 1900 + trailer T1 3400 = 9970 vehicle.
#   reference loading 9841.2 -> total 19811.2 ; low loading 1303.9 -> total 11273.9
VSUM_MASS = {
    ("RegionalDelivery", "reference"): 9589.5882,
    ("RegionalDelivery", "low"): 7173.9176,
    ("UrbanDelivery", "reference"): 9589.5882,
    ("UrbanDelivery", "low"): 7173.9176,
    ("LongHaul", "reference"): 19811.1765,
    ("LongHaul", "low"): 11273.9176,
}
# VECTO's own total RRC per run (mass-dependent), straight from the .vsum "total RRC" col.
VSUM_RRC = {
    ("RegionalDelivery", "reference"): 0.00724754853356735,
    ("RegionalDelivery", "low"): 0.00746097336455379,
    ("UrbanDelivery", "reference"): 0.00724754853356735,
    ("UrbanDelivery", "low"): 0.00746097336455379,
    ("LongHaul", "reference"): 0.00657418317124784,
    ("LongHaul", "low"): 0.00695545173240238,
}


def driver_kwargs(coast_mass=None):
    """kwargs for the code-of-record driver_model matching the harness run_chain call
    (coast on at the RigidSolo reference vehicle). coast_mass defaults to M_REF."""
    m = M_REF if coast_mass is None else coast_mass
    return dict(
        coast_mass=m,
        m_red_wheels=M_RED_WHEELS,
        cdxa_v=list(CDXA_V),
        cdxa=list(CDXA_REF),
        Crr=crr_total_vecto(m),
        rho=RHO_VECTO,
        g=G,
    )


# ============================================================================
# LongHaul group-2 vehicle = truck + trailer (F1 fix).
# Source: SegmentTable.csv group-2 RigidTruck 4x2 row — Body B2, Trailer T1,
# crosswind "RigidTrailer". Body_Trailers_Weights.csv: T1 curb 3400 kg, 2 axles,
# 235/75 R17.5, delta CdxA +1.3 m^2 for trailer operation. VCDV_parameters.csv
# RigidTrailer a1/a2/a3. Masses, total RRC and r_dyn taken from BEV_E2.vsum.
# [VECTO] all; the exact payload-table derivation is not reproduced — the .vsum
# loading is used directly (so no invented number).
# ============================================================================
LH_TRAILER_CURB = 3400.0          # [VECTO] Body_Trailers_Weights.csv T1
LH_TRAILER_DELTA_CDXA = 1.3       # [VECTO] T1 "delta CdxA for trailer operation"
LH_TRAILER_AXLES = 2
LH_TRAILER_WHEELS = 4             # 2 axles, twin? T1 single -> 4 wheels (2 per axle) [ASSUMP: single tyres]
LH_TRAILER_WHEEL_INERTIA = 4.5    # [VECTO] Wheels.csv 235/75 R17.5 Inertia
LH_CDXA0 = CDXA0 + LH_TRAILER_DELTA_CDXA   # 6.13 m^2 (matches .vsum Declared CdxA)
LH_CROSSWIND = (0.017125, 0.072275, -0.004148)  # [VECTO] VCDV_parameters.csv RigidTrailer
LH_M_VEHICLE = M_VEHICLE + LH_TRAILER_CURB       # 9970 kg (curb+body+trailer)

# reduced wheel mass incl. trailer wheels
LH_THETA_WHEELS = THETA_WHEELS + LH_TRAILER_WHEEL_INERTIA * LH_TRAILER_WHEELS
LH_M_RED_WHEELS = LH_THETA_WHEELS / R_DYN ** 2


def lh_cdxa_ref_table():
    """LongHaul reference CdxA table: RigidTrailer crosswind params, CdxA0 = 6.13."""
    a1, a2, a3 = LH_CROSSWIND
    out = []
    for spd in CDXA_V:
        vv = spd / 3.6
        tot = 0.0
        for hp in range(5, 100, 10):
            vw = V_DECL * (hp / 100 * VEH_HEIGHT / H_DECL) ** HELLMANN
            for al in range(0, 181, 10):
                vx = vv + vw * math.cos(math.radians(al))
                vy = vw * math.sin(math.radians(al))
                b = math.degrees(math.atan(vy / vx))
                cda = LH_CDXA0 + a1 * b + a2 * b * b + a3 * b ** 3
                share = (5 if al in (0, 180) else 10) / 180
                tot += 0.1 * share * cda * (vx * vx + vy * vy) / (vv * vv)
        out.append(tot)
    return np.array(out)


LH_CDXA_REF = lh_cdxa_ref_table()


def longhaul_driver_kwargs(load="reference"):
    """kwargs for driver_model with the LongHaul truck+trailer vehicle.

    Uses the .vsum total mass and total RRC for the chosen load so no number is
    invented. CdxA table is the RigidTrailer declaration table."""
    m = VSUM_MASS[("LongHaul", load)]
    return dict(
        coast_mass=m,
        m_red_wheels=LH_M_RED_WHEELS,
        cdxa_v=list(CDXA_V),
        cdxa=list(LH_CDXA_REF),
        Crr=VSUM_RRC[("LongHaul", load)],
        rho=RHO_VECTO,
        g=G,
    )


def cycle_driver_kwargs(cyc, load="reference"):
    """Dispatch to the correct vehicle for a cycle + load (F1/F2).

    RigidSolo for Regional/Urban at the .vsum mass; truck+trailer for LongHaul.
    """
    if cyc == "LongHaul":
        return longhaul_driver_kwargs(load)
    m = VSUM_MASS[(cyc, load)]
    return dict(
        coast_mass=m,
        m_red_wheels=M_RED_WHEELS,
        cdxa_v=list(CDXA_V),
        cdxa=list(CDXA_REF),
        Crr=VSUM_RRC[(cyc, load)],
        rho=RHO_VECTO,
        g=G,
    )


def cycle_energy_params(cyc, load="reference"):
    """Mass, Crr, CdxA table and r_dyn for the wheel-energy evaluation of a cycle+load."""
    if cyc == "LongHaul":
        return dict(mass=VSUM_MASS[("LongHaul", load)], Crr=VSUM_RRC[("LongHaul", load)],
                    cdxa_v=CDXA_V, cdxa=LH_CDXA_REF, r_dyn=R_DYN, rho=RHO_VECTO)
    return dict(mass=VSUM_MASS[(cyc, load)], Crr=VSUM_RRC[(cyc, load)],
                cdxa_v=CDXA_V, cdxa=CDXA_REF, r_dyn=R_DYN, rho=RHO_VECTO)
