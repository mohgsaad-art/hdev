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


def driver_kwargs(coast_mass=None):
    """kwargs for the code-of-record driver_model matching the harness run_chain call
    (coast on at the reference vehicle). coast_mass defaults to M_REF."""
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
