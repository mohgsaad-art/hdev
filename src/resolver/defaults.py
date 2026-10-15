# STATUS: NEW (Step 9, item 2 / M1.1, Bob to review). The single source of defaults for the resolver.
# PIPELINE ROLE: engines never hard-code numbers; raw project models default to None; ONLY the resolver
#   fills a value, and it pulls it from here so the assumptions list can report every default used
#   (docs/context/input-layer-and-json.md: "Defaults live only in Python (defaults.py)").
#
# Every entry is a dict {value, source, label}:
#   value  - the number (SI / native unit noted in a comment), or None when there is no source
#   source - the actual file or document the value came from (e.g. 'SegmentTable.csv', 'ES-Tech.csv x0.7')
#   label  - provenance, one of LABELS below
#
# LABELS:
#   VECTO           - read from a VECTO resource file / source (transcribed in the two decision notes)
#   REG             - read from Regulation (EU) 2017/2400
#   literature      - from an external cited source
#   HDEV ASSUMPTION - Bob's judgement value, no authoritative source (must be flagged in results)
#
# NO INVENTED NUMBERS (engine rule, master prompt §0): a value with no source is value=None and the
#   label/source string says why. 🔒 M1.1: the CdxA_Default values are LOCKED - the Annex VIII Appendix 7
#   extract that would confirm them is MISSING, so CdxA_Default stays value=None and is flagged. The
#   SegmentTable CdxA numbers are NOT copied in as a usable default (the note says "to verify before use").
#
# Sources transcribed from:
#   docs/decisions/2026-10-07_vecto-declaration-defaults.md  (payloads, heights, design speed, body/trailer masses, CdxA)
#   docs/decisions/2026-10-08_session-closeout-paux.md        (p_aux electric values, HVAC/SP/PS/Cond, DCDC, efficiencies)

VECTO = "VECTO"
REG = "REG"
LITERATURE = "literature"
HDEV_ASSUMPTION = "HDEV ASSUMPTION"
LABELS = {VECTO, REG, LITERATURE, HDEV_ASSUMPTION}


def _d(value, source, label):
    # build one default entry and check the label is one of the allowed provenance labels (fail loudly).
    if label not in LABELS:
        raise ValueError("defaults: unknown provenance label %r" % (label,))
    return {"value": value, "source": source, "label": label}


# ---------------------------------------------------------------------------
# VECTO neutral physics parameters (power step J)
# ---------------------------------------------------------------------------
# beta=1 and theta_red=0 reduce the power equation to the simple form (see force_engine.py header).
# M1.2: VECTO's own declared beta is 0.9 - cited SEPARATELY so the neutral default is never confused
# with the VECTO value. Which one is used is a modelling choice recorded by the resolver.
NEUTRAL_PARAMS = {
    "beta": _d(1.0, "neutral default (reduces P_wheel to the simple equation)", HDEV_ASSUMPTION),
    "beta_vecto": _d(0.9, "VECTO declared rolling-resistance mass exponent (M1.2)", VECTO),
    "theta_red": _d(0.0, "neutral default (no rotational-inertia reduction)", HDEV_ASSUMPTION),
}


# ---------------------------------------------------------------------------
# Design speed and reference .vacc curve (SegmentTable.csv / VACC/)
# ---------------------------------------------------------------------------
DESIGN_SPEED_KMH = _d(85.0, "SegmentTable.csv (design speed 85 km/h, all trucks)", VECTO)
VACC_FILE = _d("Truck.vacc", "Resources/Declaration/VACC/Truck.vacc (official accel/decel curve, all trucks)", VECTO)


# ---------------------------------------------------------------------------
# Reference vehicle height [m] by vehicle group (SegmentTable.csv)
# ---------------------------------------------------------------------------
REFERENCE_HEIGHT_M = {
    "1": _d(3.6, "SegmentTable.csv reference vehicle height", VECTO),
    "1s": _d(3.6, "SegmentTable.csv reference vehicle height", VECTO),
    "2": _d(3.75, "SegmentTable.csv reference vehicle height", VECTO),
    "3": _d(3.9, "SegmentTable.csv reference vehicle height", VECTO),
    "4": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "5": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "6": _d(3.75, "SegmentTable.csv reference vehicle height", VECTO),
    "7": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "8": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "9": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "10": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "11": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "12": _d(4.0, "SegmentTable.csv reference vehicle height", VECTO),
    "13": _d(3.6, "SegmentTable.csv reference vehicle height", VECTO),
    "14": _d(3.6, "SegmentTable.csv reference vehicle height", VECTO),
    "15": _d(3.6, "SegmentTable.csv reference vehicle height", VECTO),
    "16": _d(3.6, "SegmentTable.csv reference vehicle height", VECTO),
    "17_8x6": _d(3.6, "SegmentTable.csv reference vehicle height (8x6)", VECTO),
    "17_8x8": _d(4.0, "SegmentTable.csv reference vehicle height (8x8)", VECTO),
    "51": _d(3.5, "SegmentTable.csv reference vehicle height (medium rigid)", VECTO),
    "53": _d(3.5, "SegmentTable.csv reference vehicle height (medium rigid)", VECTO),
    "55": _d(3.5, "SegmentTable.csv reference vehicle height (medium rigid)", VECTO),
    "52": _d(2.9, "SegmentTable.csv reference vehicle height (van)", VECTO),
    "54": _d(2.9, "SegmentTable.csv reference vehicle height (van)", VECTO),
    "56": _d(2.9, "SegmentTable.csv reference vehicle height (van)", VECTO),
}


# ---------------------------------------------------------------------------
# 🔒 M1.1 - CdxA_Default [m^2] by vehicle group: LOCKED, NO SOURCE.
# ---------------------------------------------------------------------------
# The SegmentTable.csv shows CdxA numbers (group 1/1s 7.1, 2 7.2, 3 7.4, 4 8.4, 5 8.7, 9 8.5, 10 8.8,
# 11 8.5, 12 8.8, 16 9.0, medium rigid 5.8, van 2.5; a separate CdxA_Construction column e.g. group 5
# 7.2) but the 2026-10-07 note marks them "to verify before use": they are "likely" the standard values
# for vehicles without a measured air-drag certificate (Reg. 2017/2400 Annex VIII Appendix 7), and the
# Annex VIII Appendix 7 extract that would confirm them is MISSING. So every CdxA default is None and
# flagged. The SegmentTable numbers are deliberately NOT transcribed as usable values here.
_CDXA_NO_SOURCE = "no source - Annex VIII Appendix 7 extract missing (SegmentTable CdxA 'to verify before use')"
_CDXA_GROUPS = ["1", "1s", "2", "3", "4", "5", "9", "10", "11", "12", "16",
                "medium_rigid", "van"]
CDXA_DEFAULT_M2 = {g: _d(None, _CDXA_NO_SOURCE, HDEV_ASSUMPTION) for g in _CDXA_GROUPS}
# construction column also locked (same reason)
CDXA_DEFAULT_CONSTRUCTION_M2 = {"5": _d(None, _CDXA_NO_SOURCE, HDEV_ASSUMPTION)}


# ---------------------------------------------------------------------------
# Payload defaults [kg], low / reference, by vehicle group x mission (SegmentTable.csv)
# ---------------------------------------------------------------------------
# shape: {"low": kg, "ref": kg}. groups 1/1s/2/3 and medium lorries 51-56 use percentage-of-GVW
# functions from Payloads.csv instead (see PAYLOADS_PCT_BY_GVW below), not a fixed kg pair.
def _pl(low, ref, mission):
    return _d({"low": low, "ref": ref}, "SegmentTable.csv payload (low/reference, %s)" % mission, VECTO)


PAYLOAD_KG = {
    "4": {"LH": _pl(1900, 14000, "LH"), "RD": _pl(900, 4400, "RD"), "UD": _pl(900, 4400, "UD"),
          "MU": _pl(600, 3000, "MU"), "Constr": _pl(900, 4400, "Constr")},
    "5": {"LH": _pl(2600, 19300, "LH"), "LH_EMS": _pl(3500, 26500, "LH EMS"),
          "RD": _pl(2600, 12900, "RD"), "RD_EMS": _pl(3500, 17500, "RD EMS"),
          "UD": _pl(2600, 12900, "UD"), "Constr": _pl(2600, 12900, "Constr")},
    "9": {"LH": _pl(2600, 19300, "LH"), "LH_EMS": _pl(3500, 26500, "LH EMS"),
          "RD": _pl(1400, 7100, "RD"), "RD_EMS": _pl(3500, 17500, "RD EMS"),
          "MU": _pl(1200, 6000, "MU"), "Constr": _pl(1400, 7100, "Constr")},
    "10": {"LH": _pl(2600, 19300, "LH"), "LH_EMS": _pl(3500, 26500, "LH EMS"),
           "RD": _pl(2600, 12900, "RD"), "RD_EMS": _pl(3500, 17500, "RD EMS"),
           "Constr": _pl(2600, 12900, "Constr")},
    # group 11 is as group 9 (MU 1200/6000); group 12 is as group 10
    "11": {"LH": _pl(2600, 19300, "LH"), "LH_EMS": _pl(3500, 26500, "LH EMS"),
           "RD": _pl(1400, 7100, "RD"), "RD_EMS": _pl(3500, 17500, "RD EMS"),
           "MU": _pl(1200, 6000, "MU"), "Constr": _pl(1400, 7100, "Constr")},
    "12": {"LH": _pl(2600, 19300, "LH"), "LH_EMS": _pl(3500, 26500, "LH EMS"),
           "RD": _pl(2600, 12900, "RD"), "RD_EMS": _pl(3500, 17500, "RD EMS"),
           "Constr": _pl(2600, 12900, "Constr")},
    "16": {"LH": _pl(2600, 19300, "LH"), "LH_EMS": _pl(3500, 26500, "LH EMS"),
           "RD": _pl(1400, 7100, "RD"), "RD_EMS": _pl(3500, 17500, "RD EMS"),
           "Constr": _pl(2600, 12900, "Constr")},
}

# groups 1,1s,2,3 and medium lorries 51-56: payload is a %-of-GVW function from Payloads.csv.
# rows seen (GVW kg -> 10% / 50% / 75% payload kg); the note warns this may be incomplete and the
# interpolation method is not yet confirmed from code, so it is transcribed as the raw table only.
PAYLOADS_PCT_BY_GVW = _d(
    {3500: {"pc10": 80, "pc50": 420, "pc75": 630},
     7400: {"pc10": 240, "pc50": 1210, "pc75": 1840},
     7500: {"pc10": 250, "pc50": 1250, "pc75": 1900},
     16000: {"pc10": 920, "pc50": 4600, "pc75": 6900}},
    "Payloads.csv (GVW -> 10/50/75% payload; may be incomplete, interpolation unconfirmed)",
    VECTO,
)


# ---------------------------------------------------------------------------
# Body / trailer curb masses [kg] (Body_Trailers_Weights.csv)
# ---------------------------------------------------------------------------
BODY_TRAILER_MASS_KG = {
    "B-II": _d(800, "Body_Trailers_Weights.csv curb mass", VECTO),
    "B1": _d(1600, "Body_Trailers_Weights.csv curb mass", VECTO),
    "B2": _d(1900, "Body_Trailers_Weights.csv curb mass", VECTO),
    "B3": _d(2000, "Body_Trailers_Weights.csv curb mass", VECTO),
    "B4": _d(2100, "Body_Trailers_Weights.csv curb mass", VECTO),
    "B5": _d(2200, "Body_Trailers_Weights.csv curb mass", VECTO),
    "BT1": _d(2000, "Body_Trailers_Weights.csv curb mass (tipper body, construction)", VECTO),
    "BT2": _d(3230, "Body_Trailers_Weights.csv curb mass (tipper body, construction)", VECTO),
    "BT3": _d(4355, "Body_Trailers_Weights.csv curb mass (tipper body, construction)", VECTO),
    "MU4": _d(6000, "Body_Trailers_Weights.csv curb mass (refuse body)", VECTO),
    "MU9": _d(6750, "Body_Trailers_Weights.csv curb mass (refuse body)", VECTO),
    "MU11": _d(6750, "Body_Trailers_Weights.csv curb mass (refuse body)", VECTO),
    "T1": _d(3400, "Body_Trailers_Weights.csv curb mass (max 10500)", VECTO),
    "T2": _d(5400, "Body_Trailers_Weights.csv curb mass (max 18000)", VECTO),
    "ST1": _d(7500, "Body_Trailers_Weights.csv curb mass (max 24000; GVM combination 40000)", VECTO),
    "Dolly": _d(2500, "Body_Trailers_Weights.csv curb mass (EMS only)", VECTO),
    "STT1": _d(6100, "Body_Trailers_Weights.csv curb mass (tipper semitrailer)", VECTO),
    "STT2": _d(5600, "Body_Trailers_Weights.csv curb mass (tipper semitrailer)", VECTO),
}

# trailer delta-CdxA for long haul (Body_Trailers_Weights.csv): T1 1.3; T2 1.5/1.5;
# ST1 0/2.1 (first/second trailer).
TRAILER_DELTA_CDXA_LH = {
    "T1": _d((1.3,), "Body_Trailers_Weights.csv trailer delta-CdxA, long haul", VECTO),
    "T2": _d((1.5, 1.5), "Body_Trailers_Weights.csv trailer delta-CdxA, long haul", VECTO),
    "ST1": _d((0.0, 2.1), "Body_Trailers_Weights.csv trailer delta-CdxA, long haul (first/second)", VECTO),
}


# ---------------------------------------------------------------------------
# Auxiliary efficiencies / constants (DeclarationData.cs, via the p_aux note)
# ---------------------------------------------------------------------------
AUX_EFFICIENCIES = {
    "alternator_efficiency": _d(0.7, "DeclarationData.cs AlternatorEfficiency (ES/SP table x0.7)", VECTO),
    "hvac_electric_efficiency_factor": _d(0.8, "DeclarationData.cs HVACElectricEfficiencyFactor (electric = table x 1/0.8)", VECTO),
    "dcdc_efficiency": _d(1.0, "DeclarationData.cs DCDCEfficiency (Declaration Mode, no converter loss)", VECTO),
}


# ---------------------------------------------------------------------------
# P_aux electric values [W] for a BEV lorry (2026-10-08 p_aux note).
# All already the ELECTRIC demand drawn from the traction battery (DC/DC = 1.0).
# ---------------------------------------------------------------------------
# Electric system ES = ES-Tech.csv x 0.7 (heavy lorries). key: mission; LH distinct, RD/UD/MU/Constr equal.
PAUX_ES_HEAVY_STANDARD_W = {
    "LH": _d(1200.0, "ES-Tech.csv Standard technology, LH x0.7", VECTO),
    "RD": _d(1000.0, "ES-Tech.csv Standard technology, RD x0.7", VECTO),
    "UD": _d(1000.0, "ES-Tech.csv Standard technology, UD x0.7", VECTO),
    "MU": _d(1000.0, "ES-Tech.csv Standard technology, MU x0.7", VECTO),
    "Constr": _d(1000.0, "ES-Tech.csv Standard technology, Constr x0.7", VECTO),
}
PAUX_ES_HEAVY_LED_W = {
    "LH": _d(1150.0, "ES-Tech.csv LED headlights, LH x0.7", VECTO),
    "RD": _d(950.0, "ES-Tech.csv LED headlights, RD x0.7", VECTO),
    "UD": _d(950.0, "ES-Tech.csv LED headlights, UD x0.7", VECTO),
    "MU": _d(950.0, "ES-Tech.csv LED headlights, MU x0.7", VECTO),
    "Constr": _d(950.0, "ES-Tech.csv LED headlights, Constr x0.7", VECTO),
}
# medium lorries (ES-Tech_Medium.csv x0.7; MU/Constr are blank -> no default, raise on lookup)
PAUX_ES_MEDIUM_STANDARD_W = {
    "LH": _d(720.0, "ES-Tech_Medium.csv Standard technology, LH x0.7", VECTO),
    "RD": _d(600.0, "ES-Tech_Medium.csv Standard technology, RD x0.7", VECTO),
    "UD": _d(600.0, "ES-Tech_Medium.csv Standard technology, UD x0.7", VECTO),
    "MU": _d(None, "ES-Tech_Medium.csv MU cell blank ('---') - lookup error in VECTO", VECTO),
    "Constr": _d(None, "ES-Tech_Medium.csv Constr cell blank ('---') - lookup error in VECTO", VECTO),
}
PAUX_ES_MEDIUM_LED_W = {
    "LH": _d(660.0, "ES-Tech_Medium.csv LED headlights, LH x0.7", VECTO),
    "RD": _d(550.0, "ES-Tech_Medium.csv LED headlights, RD x0.7", VECTO),
    "UD": _d(550.0, "ES-Tech_Medium.csv LED headlights, UD x0.7", VECTO),
    "MU": _d(None, "ES-Tech_Medium.csv MU cell blank ('---')", VECTO),
    "Constr": _d(None, "ES-Tech_Medium.csv Constr cell blank ('---')", VECTO),
}

# HVAC electric [W] = HVAC-Table.csv Default technology x 1.25, by vehicle group x mission.
# "None" technology = 0 for all groups/missions. blank cells (-) are a VECTO lookup error -> None.
def _hv(lh, rd, ud, mu, constr):
    def cell(x, m):
        if x is None:
            return _d(None, "HVAC-Table.csv Default blank cell (%s) - lookup error in VECTO" % m, VECTO)
        return _d(x, "HVAC-Table.csv Default technology (%s) x1.25" % m, VECTO)
    return {"LH": cell(lh, "LH"), "RD": cell(rd, "RD"), "UD": cell(ud, "UD"),
            "MU": cell(mu, "MU"), "Constr": cell(constr, "Constr")}


PAUX_HVAC_DEFAULT_W = {
    # table value 150->187.5, 200->250, 300->375, 350->437.5; "-" blank -> None; group 5/10 MU explicit 0.
    "1s": _hv(250.0, 187.5, 187.5, None, None),
    "1": _hv(250.0, 187.5, 187.5, None, None),
    "2": _hv(250.0, 250.0, 187.5, None, None),
    "3": _hv(250.0, 250.0, 187.5, None, None),
    "4": _hv(437.5, 250.0, 187.5, 375.0, 250.0),
    "5": _hv(437.5, 250.0, 187.5, 0.0, 250.0),
    "9": _hv(437.5, 250.0, 187.5, 375.0, 250.0),
    "10": _hv(437.5, 250.0, 187.5, 0.0, 250.0),
    "11": _hv(437.5, 250.0, 187.5, 375.0, 250.0),
    "12": _hv(437.5, 250.0, 187.5, None, 250.0),
    "16": _hv(437.5, 250.0, 187.5, None, 250.0),
    "51": _hv(250.0, 187.5, 187.5, None, None),
    "52": _hv(250.0, 187.5, 187.5, None, None),
    "53": _hv(250.0, 187.5, 187.5, None, None),
    "54": _hv(250.0, 187.5, 187.5, None, None),
    "55": _hv(250.0, 187.5, 187.5, None, None),
    "56": _hv(250.0, 187.5, 187.5, None, None),
}

# Pneumatic system electric [W], _el columns read DIRECTLY (never derived), by technology x mission.
def _ps(lh, rd, ud, mu, constr, tech):
    s = "PS-Table.csv _el columns (%s)" % tech
    return {"LH": _d(lh, s, VECTO), "RD": _d(rd, s, VECTO), "UD": _d(ud, s, VECTO),
            "MU": _d(mu, s, VECTO), "Constr": _d(constr, s, VECTO)}


PAUX_PS_EL_W = {
    "Small + elec. driven": _ps(750, 750, 813, 813, 750, "Small + elec. driven"),
    "Small + AMS + elec. driven": _ps(675, 675, 732, 732, 675, "Small + AMS + elec. driven"),
    "Medium Supply 1-stage + elec. driven": _ps(750, 687, 687, 687, 750, "Medium Supply 1-stage + elec. driven"),
    "Medium Supply 1-stage + AMS + elec. driven": _ps(675, 618, 618, 618, 675, "Medium Supply 1-stage + AMS + elec. driven"),
    "Medium Supply 2-stage + elec. driven": _ps(875, 813, 750, 750, 1000, "Medium Supply 2-stage + elec. driven"),
    "Medium Supply 2-stage + AMS + elec. driven": _ps(788, 732, 675, 675, 900, "Medium Supply 2-stage + AMS + elec. driven"),
    "Large Supply + elec. driven": _ps(1000, 1000, 875, 875, 1125, "Large Supply + elec. driven"),
    "Large Supply + AMS + elec. driven": _ps(900, 900, 788, 788, 1013, "Large Supply + AMS + elec. driven"),
    "Vacuum pump + elec. driven": _ps(237, 200, 162, 162, 162, "Vacuum pump + elec. driven"),
}

# Steering pump SP-Tech effective electric factors (UF/B/S), PEV-allowed technologies only.
# the adapter multiplies by alternator 0.7; the final W depends on group/axles (SP-Table/SP-Axles),
# so no single SP default W is stored - only the per-technology factors are transcribed here.
PAUX_SP_TECH_FACTORS = {
    "Electric driven pump": _d((0.857, 0.857, 0.857), "SP-Tech.csv Electric driven pump (PEV allowed) UF/B/S", VECTO),
    "Full electric steering gear": _d((0.0, 0.143, 1.429), "SP-Tech.csv Full electric steering gear (PEV allowed) UF/B/S", VECTO),
}

# Conditioning [W], already electric, key: mission only (Cond-Table.csv, Lorry row).
# on only while an electric motor / electric PTO is on.
PAUX_COND_W = {
    "LH": _d(600.0, "Cond-Table.csv Lorry, LH", VECTO),
    "RD": _d(600.0, "Cond-Table.csv Lorry, RD", VECTO),
    "UD": _d(550.0, "Cond-Table.csv Lorry, UD", VECTO),
    "MU": _d(550.0, "Cond-Table.csv Lorry, MU", VECTO),
    "Constr": _d(600.0, "Cond-Table.csv Lorry, Constr", VECTO),
}


# ---------------------------------------------------------------------------
# Typed-input resolver defaults (input-layer decisions, 2 Sep 2026).
# Bob's judgement values - UNSOURCED - must be labelled HDEV ASSUMPTION and reported.
# ---------------------------------------------------------------------------
TYPED_RESOLVER = {
    # default cruise speeds by road type [km/h]: 30 deep urban / 50 urban / 80 non-urban
    "cruise_speed_deep_urban_kmh": _d(30.0, "input-layer decision (2 Sep): Bob's judgement, unsourced", HDEV_ASSUMPTION),
    "cruise_speed_urban_kmh": _d(50.0, "input-layer decision (2 Sep): Bob's judgement, unsourced", HDEV_ASSUMPTION),
    "cruise_speed_non_urban_kmh": _d(80.0, "input-layer decision (2 Sep): Bob's judgement, unsourced", HDEV_ASSUMPTION),
    # default dwell per stop: 45 min
    "dwell_s": _d(45.0 * 60.0, "input-layer decision (2 Sep): 45 min/stop, Bob's judgement, unsourced", HDEV_ASSUMPTION),
    # default gradient: flat
    "grade_pct": _d(0.0, "input-layer decision (2 Sep): gradient flat by default", HDEV_ASSUMPTION),
    # even stop spacing when building waypoints from a typed summary
    "even_stop_spacing": _d(True, "input-layer decision (8 Oct): even stop spacing is an HDEV assumption", HDEV_ASSUMPTION),
}


# ---------------------------------------------------------------------------
# Accessors (test-friendly, fail loudly)
# ---------------------------------------------------------------------------

def get(table, key):
    # look up one entry in a dict-of-entries default table; raise if the key is absent (never extrapolate).
    if key not in table:
        raise KeyError("defaults: no entry for key %r" % (key,))
    return table[key]


def is_sourced(entry):
    # True when the entry carries an actual value (not a locked/missing-source placeholder).
    return entry.get("value") is not None
