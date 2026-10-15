# Shared VECTO-sourced inputs + Bob's engine imports for the pitch estimates.
#
# PURPOSE: one place for every number that goes into the pitch estimate scripts,
# each with its source (VECTO file:line / Bob's prompt / ASSUMPTION). Nothing here
# is invented. See docs/pitch/estimates-2026-10.md for the write-up.
#
# VECTO stable branch v5.1.3 (commit d16ba783c). Files cited either from the HDEV
# reference bundle (reference/vecto/...) or from a fresh VECTO clone (paths noted).
#
# Run any script with the workspace venv:
#   /projects/sandbox/.venv/bin/python scratch/pitch_estimates/<script>.py
import os
import sys

import numpy as np

# --- make Bob's engines importable (use them exactly as-is) --------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))          # .../hdev
sys.path.insert(0, os.path.join(_REPO, "src", "engine"))

from crosswind_engine import crosswind_engine   # noqa: E402  verified vs VECTO (0.006%)
from force_engine import force_engine            # noqa: E402
from payload_engine import payload_engine, fill_payload  # noqa: E402

# Where the mission-cycle .vdri files live (reference bundle = authoritative copy)
MISSIONS_DIR = os.path.join(_REPO, "reference", "vecto", "resources", "MissionCycles")

# =============================================================================
# PHYSICAL CONSTANTS (VECTO)
# =============================================================================
# DeclarationData.cs:74  GravityAccelleration = 9.80665 m/s^2
G = 9.80665
# DeclarationData.cs:76  AirDensity = 1.188 kg/m^3  (VECTO "standard" / good-day density)
RHO_VECTO = 1.188

# Ideal-gas-law density for the weather scenarios (dry air, sea-level pressure).
# ASSUMPTION (Bob's prompt §3): standard sea-level pressure, dry air.
P_SEA_LEVEL = 101325.0     # Pa  (ISA standard sea-level pressure)
R_DRY_AIR = 287.05         # J/(kg K)  specific gas constant, dry air


def air_density(temp_c, pressure_pa=P_SEA_LEVEL):
    """Dry-air density from the ideal gas law. rho = p / (R * T)."""
    return pressure_pa / (R_DRY_AIR * (temp_c + 273.15))


# =============================================================================
# WEATHER SCENARIOS (Bob's prompt §3) -- these are scenarios, not frequencies.
# wind speeds are at 10 m height.
# =============================================================================
WEATHER = {
    # name: (temp_C, wind_10m_mps, note)
    "good":    (None, 0.0,    "VECTO standard density 1.188, no wind"),
    "typical": (0.0,  5.028,  "0 C + 5.028 m/s (Bob's DMI average)"),
    "bad":     (-12.0, 10.8,  "-12 C (DS 418:2011 worked example) + 10.8 m/s (Beaufort 6 lower bound)"),
    "severe":  (-12.0, 13.9,  "-12 C + 13.9 m/s (Beaufort 7 lower bound)"),
}

# VECTO wind-profile handling (crosswind verification doc + crosswind_engine.py):
WIND_EXP = 0.2          # wind profile exponent (power law), VECTO
WIND_H_REF = 10.0       # m -- Bob's scenario winds are quoted at 10 m
DH = 0.4                # height-slice thickness [m] used in the verified test
DPHI_DEG = 1.0          # yaw-direction step [deg] used in the verified test
BETA_CLAMP = 10.0       # Bob's 10 deg yaw clamp (HDEV decision, must be stated)

# =============================================================================
# CROSSWIND COEFFICIENT SETS  (reference/vecto/resources/VCDV_parameters.csv)
# =============================================================================
CROSSWIND_COEFFS = {
    #                     a1          a2          a3
    "RigidSolo":          (0.013526,  0.017746,  -0.000666),
    "RigidTrailer":       (0.017125,  0.072275,  -0.004148),
    "TractorSemitrailer": (0.030042,  0.040817,  -0.00213),
    "MediumLorriesRigid": (-0.0015,   0.0086,    -0.00029),
}

# =============================================================================
# VEHICLE V2 -- Group 5 4x2 tractor-semitrailer, BEV
# Specs from the generic Group-5 PEV job (VECTO clone):
#   "Generic Vehicles/Declaration Mode/xEV XML Jobs/Lorries/Group5_ PEV_E4.xml"
#     line 14  CorrectedActualMass (tractor curb)      = 10143 kg
#     line 15  TechnicalPermissibleMaximumLadenMass     = 18000 kg (tractor)
#     line 2133 tyre dimension 315/70 R22.5
#     line 2134 RRCDeclared (non-driven axle)          = 0.0034
#     line 2161 RRCDeclared (driven axle)              = 0.0040
#     line 2135/2162 FzISO                             = 33350 N
#     line 2203 CdxA_0 (tractor-only air drag)         = 4.31 m^2
# Declaration defaults (reference/vecto/resources/SegmentTable.csv group 5 row, line 17):
#     CdxA_Default (whole tractor+semitrailer combo)   = 8.7 m^2
#     height                                           = 4.0 m
#     RegionalDelivery payload low/reference           = 2600 / 12900 kg
#     crosswind set                                    = TractorSemitrailer
# Semitrailer ST1 (reference/vecto/resources/Body_Trailers_Weights.csv):
#     curb mass                                        = 7500 kg
#     combination fully-loaded GVM                     = 40000 kg
# Tyre dynamic radius (reference/vecto/resources/Wheels.csv row 315/70 R22.5):
#     d = 1014 mm -> r_dyn = 0.507 m
# =============================================================================
V2 = {
    "name": "Group 5 4x2 tractor-semitrailer (BEV)",
    "tractor_curb_kg": 10143.0,
    "trailer_curb_kg": 7500.0,           # ST1
    "cdxa_combo_m2": 8.7,                 # SegmentTable CdxA_Default group 5
    "cdxa_tractor_only_m2": 4.31,         # measured tractor CdxA (for reference)
    "height_m": 4.0,                      # SegmentTable group 5
    "rrc_nondriven": 0.0034,
    "rrc_driven": 0.0040,
    "fz_iso_n": 33350.0,
    "r_dyn_m": 0.507,
    "crosswind_set": "TractorSemitrailer",
    "payload_low_kg": 2600.0,             # RegionalDelivery low loading
    "payload_ref_kg": 12900.0,            # RegionalDelivery reference loading
    "combo_gvm_kg": 40000.0,
    "cycle": "RegionalDelivery.vdri",
}


def v2_rrc_simple():
    """Single representative RRC for V2 (ASSUMPTION: arithmetic mean of the two
    declared axle RRCs; VECTO's per-axle load-dependent weighting is not applied).
    Values 0.0034 / 0.0040 -> 0.0037."""
    return (V2["rrc_nondriven"] + V2["rrc_driven"]) / 2.0


# =============================================================================
# VEHICLE V1 -- Municipal refuse truck, Group 4 4x2 rigid, MunicipalUtility
# Declaration defaults (SegmentTable.csv group 4 row, line 12):
#     CdxA_Default                                     = 8.4 m^2
#     height                                           = 4.0 m
#     MunicipalUtility payload low/reference           = 600 / 3000 kg
#     body MU4, crosswind "Other" set                  = RigidSolo
# Refuse body MU4 curb (Body_Trailers_Weights.csv)    = 6000 kg
# NO BEV curb mass exists in VECTO for a >16 t Group-4 rigid refuse truck.
#   -> MISSING. We run three ASSUMPTION chassis curb masses.
# For tyres/RRC we have no Group-4 BEV refuse file either; we ASSUME the same
#   315/70 R22.5 heavy-truck tyres and the Group-5 declared RRCs (0.0034/0.0040),
#   flagged. (The generic BEV E2 rigid uses 265/70 R19.5 at RRC 0.0065/0.0075,
#   but it is an 11.99 t vehicle, lighter class than a refuse truck.)
# =============================================================================
V1 = {
    "name": "Municipal refuse truck (Group 4 4x2 rigid, MunicipalUtility)",
    "cdxa_m2": 8.4,                       # SegmentTable CdxA_Default group 4
    "height_m": 4.0,
    "body_curb_kg": 6000.0,               # MU4 rear collector body
    "rrc_nondriven": 0.0034,              # ASSUMPTION (reuse Group-5 heavy RRC)
    "rrc_driven": 0.0040,                 # ASSUMPTION
    "r_dyn_m": 0.507,                     # 315/70 R22.5 ASSUMPTION
    "crosswind_set": "RigidSolo",         # group 4 "Other" mission set
    "payload_low_kg": 600.0,              # MunicipalUtility low loading
    "payload_ref_kg": 3000.0,             # MunicipalUtility reference loading
    "cycle": "MunicipalUtility.vdri",
    # chassis curb mass is MISSING in VECTO -> ASSUMPTION sweep (kg):
    "chassis_curb_assumptions_kg": [9000.0, 11000.0, 13000.0],
}


def v1_rrc_simple():
    return (V1["rrc_nondriven"] + V1["rrc_driven"]) / 2.0


# =============================================================================
# BATTERY (VECTO generic 243 kWh / 750 V pack, GenericVehicleE2)
# Files (VECTO clone, "Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/"):
#   GenericBattery_243kWh_750V.vbat : Capacity 324 Ah, SOC_min 10, SOC_max 90
#   GenericBattery_243kWh.vbatv     : OCV(SoC%) table below
#   GenericBattery_243kWh.vbatr     : Ri = 0.04 ohm, constant over SoC
#   MaxCurrent.vimax                : I_charge = I_discharge = 1620 A, flat over SoC
# Battery.cs: P = (U0 + I*Ri)*I ; SoC += I*dt/Capacity ; MaxChargeCurrent(dt) =
#   min((MaxSOC-SoC)*Cap/dt, I_charge_lookup).  (reference/vecto/cs/Battery.cs)
# =============================================================================
BATTERY = {
    "capacity_Ah": 324.0,
    "soc_min": 0.10,
    "soc_max": 0.90,
    "Ri_ohm": 0.04,                       # constant
    "I_charge_max_A": 1620.0,             # constant over SoC
    # OCV table: (SoC fraction, pack volts)
    "ocv_soc": np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) / 100.0,
    "ocv_V": np.array([673.5, 700.2, 715.4, 723.6, 727.7,
                       730.0, 731.6, 733.8, 737.1, 742.2, 750.2]),
}


def ocv(soc_frac):
    """Open-circuit pack voltage, linear interpolation of the VECTO OCV table,
    clamped at the ends (VECTO BatteryData.SOCMap.Lookup)."""
    return np.interp(soc_frac, BATTERY["ocv_soc"], BATTERY["ocv_V"])


# =============================================================================
# HDEV drivetrain placeholders (Method M3) -- NO VECTO equivalent.
# docs/decisions/2026-10-08_session-closeout-payload-force.md and HDEV notes.
# =============================================================================
ETA_CHAIN = 0.95 * 0.95 * 0.98   # motor * inverter * gearbox placeholder = 0.88445


def read_vdri(filename):
    """Read a VECTO .vdri distance cycle into arrays.
    Columns: s [m], v [km/h], grad [%], stop [s], (+HW or PTO flag).
    Returns dict of numpy arrays. Header line starts with '<s>'."""
    path = os.path.join(MISSIONS_DIR, filename)
    s, v, grad, stop, flag = [], [], [], [], []
    with open(path, encoding="utf-8-sig") as fh:   # utf-8-sig strips a BOM
        for line in fh:
            line = line.strip().lstrip("\ufeff")
            if not line or line.startswith("<") or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            s.append(float(parts[0]))
            v.append(float(parts[1]))
            grad.append(float(parts[2]))
            stop.append(float(parts[3]))
            flag.append(float(parts[4]) if len(parts) > 4 and parts[4] != "" else 0.0)
    return {
        "s": np.array(s), "v_kmh": np.array(v), "grad_pct": np.array(grad),
        "stop_s": np.array(stop), "flag": np.array(flag),
    }
