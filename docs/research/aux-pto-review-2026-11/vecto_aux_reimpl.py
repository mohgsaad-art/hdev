"""Independent re-implementation of VECTO's declaration-mode battery-electric (PEV) lorry
auxiliary lookups, written from the C# source at mohgsaad-art/VECTO @ IEPC-experiments b8d6126.
It deliberately does NOT import or look at the notebook (_load_notebook) or src/.

C# files this follows (paths under VectoCore/VectoCore/):
  InputData/Reader/DataObjectAdapter/SimulationComponents/AuxiliaryDataAdapter/HeavyLorryAuxiliaryDataAdapter.cs
      50 alternatorEfficiency = DeclarationData.AlternatorEfficiency
      78 HVAC factor        = 1/DeclarationData.HVACElectricEfficiencyFactor
      118-120 ES            = ElectricSystem.Lookup(...).PowerDemand * alternatorEfficiency
      136-146 PS            = fully electric -> PneumaticSystem.GetElectricPowerDemand (the *_el column), else mech*0.7
      161-165 HVAC          = HVAC-Table value * (1/0.8)
      188-190 steered axles = technologies count must equal number of steered axles
      194, 220 SP           = SteeringPump.Lookup(...).electricPumps * alternatorEfficiency
      106     COND          = Conditioning.LookupPowerDemand(hdvClass, mission)  (no factor)
  Models/Declaration/Auxiliaries/SteeringPump.cs 58-114 (SP lookup), 127-148 (SP-Table /100), 150-168, 60-83 (SP-Axles)
  Models/Declaration/Auxiliaries/ElectricSystem.cs 24-36 (heavy vs medium table), 91-110 ("---" cells skipped)
  Models/Declaration/Auxiliaries/PneumaticSystem.cs 51-69, 78-90, 123-153
  Models/Declaration/Auxiliaries/Conditioning.cs 15-20, 27-46 (Cond-Table, key = mission only)
  Models/Declaration/HVAC.cs 53-68 (blank cell -> not in dictionary -> lookup error)
  Models/Declaration/Auxiliaries/AbstractAuxiliaryVehicleArchitectureLookup.cs (BEV -> 'pev' column)
  Models/Declaration/DeclarationData.cs 123 (0.7), 124 (DCDC 1.0), 126 (HVAC 0.8)

Everything returns plain Python floats in W. Errors are raised as LookupError with a clear message
(this is what VECTO does: it throws VectoException on a missing cell).
"""
import csv
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
RES = os.path.join(REPO, "reference", "vecto", "resources")
VAUX = os.path.join(RES, "VAUX")

# --- constants: DeclarationData.cs lines 123, 124, 126 (b8d6126) --------------------------
ALTERNATOR_EFFICIENCY = 0.7
DCDC_EFFICIENCY = 1.0
HVAC_ELECTRIC_EFFICIENCY_FACTOR = 0.8

MISSIONS = ["Long haul", "Regional delivery", "Urban delivery", "Municipal utility", "Construction"]


def _norm(s):
    return " ".join(str(s).split()).lower()


def _read(path):
    """Read a VECTO csv: '#' lines are comments, cells trimmed, header names normalised."""
    with open(path, encoding="latin-1", newline="") as fh:
        rows = [r for r in csv.reader(fh) if r and not r[0].strip().startswith("#") and any(c.strip() for c in r)]
    header = [_norm(c) for c in rows[0]]
    return header, [[c.strip() for c in r] for r in rows[1:]]


def _num(s):
    s = s.strip()
    if s == "" or s in ("---", "n.a.", "-"):
        return None
    return float(s)


# ---- table loaders -------------------------------------------------------------------------
def load_tables(vaux=VAUX):
    T = {}
    # ES (heavy and medium)
    for key, fn in (("es_heavy", "ES-Tech.csv"), ("es_medium", "ES-Tech_Medium.csv")):
        h, rows = _read(os.path.join(vaux, fn))
        d = {}
        for r in rows:
            for j in range(1, len(h)):
                v = _num(r[j])
                if v is not None:                       # ElectricSystem.cs 100-102: "---" skipped
                    d[(h[j], r[0])] = v
        T[key] = d
    # HVAC (blank -> NaN -> not stored; HVAC.cs 59-60)
    h, rows = _read(os.path.join(vaux, "HVAC-Table.csv"))
    d = {}
    for r in rows:
        tech, grp = r[0], r[1].strip().lower()
        for j in range(2, len(h)):
            v = _num(r[j])
            if v is not None:
                d[(h[j], tech, grp)] = v
    T["hvac"] = d
    # PS: architecture flags, mech columns, *_el columns
    h, rows = _read(os.path.join(vaux, "PS-Table.csv"))
    i_pev = h.index("pev")
    i_fe = h.index("fully electric")
    # PneumaticSystem.cs 55-58: mech columns = after 'fullyelectric' up to first '*_el' column
    i_first_el = next(i for i, c in enumerate(h) if c.endswith("_el"))
    ps = {}
    for r in rows:
        tech = r[0]
        rec = {"pev": r[i_pev] == "1", "fully_electric": r[i_fe] == "1", "mech": {}, "el": {}}
        for j in range(i_fe + 1, i_first_el):
            v = _num(r[j])
            if v is not None:
                rec["mech"][h[j]] = v
        for j in range(i_first_el, len(h)):
            v = _num(r[j])
            if v is not None:
                rec["el"][h[j][:-3]] = v
        ps[tech] = rec
    T["ps"] = ps
    # SP-Table: 'U+F/B/S' in 1/100 W (SteeringPump.cs 141-142: ToDouble()/100); blank cells skipped (138)
    h, rows = _read(os.path.join(vaux, "SP-Table.csv"))
    sp = {}
    for r in rows:
        grp = r[0].strip().lower()
        for j in range(1, len(h)):
            if r[j] == "":
                continue
            p = [float(x) / 100.0 for x in r[j].split("/")]
            p = (p + [0.0, 0.0, 0.0])[:3] if len(p) < 3 else p[:3]
            sp[(h[j], grp)] = tuple(p)
    T["sp_base"] = sp
    # SP-Axles: row index = n-th steered axle (SteeringPump.cs 80: Lookup(mission, axleCount) with axleCount running 1..n)
    h, rows = _read(os.path.join(vaux, "SP-Axles.csv"))
    ax = {}
    for r in rows:
        n = int(r[0])
        for j in range(1, len(h)):
            if r[j] == "":
                continue
            p = [float(x) for x in r[j].split("/")]
            ax[(h[j], n)] = tuple((p + [0.0, 0.0, 0.0])[:3])
    T["sp_axle"] = ax
    # SP-Tech: columns conventional,P-HEV,S-HEV,PEV,fully electric, UF,B,S
    h, rows = _read(os.path.join(vaux, "SP-Tech.csv"))
    st = {}
    for r in rows:
        st[r[0]] = {"pev": r[h.index("pev")] == "1", "fully_electric": r[h.index("fully electric")] == "1",
                    "f": (float(r[h.index("uf")]), float(r[h.index("b")]), float(r[h.index("s")]))}
    T["sp_tech"] = st
    # Cond (key = mission only; Conditioning.cs 35-41)
    h, rows = _read(os.path.join(vaux, "Cond-Table.csv"))
    T["cond"] = {h[j]: float(rows[0][j]) for j in range(1, len(h))}
    return T


TABLES = load_tables()


def _m(mission):
    return _norm(mission)


# ---- the lookups ------------------------------------------------------------------------------
MEDIUM = {"51", "52", "53", "54", "55", "56"}


def es_electric_W(group, mission, tech=None, T=TABLES):
    tech = tech if tech and tech.strip() else "Standard technology"
    tab = T["es_medium"] if str(group).lower() in MEDIUM else T["es_heavy"]
    k = (_m(mission), tech)
    if k not in tab:
        raise LookupError(f"ES: no value for mission '{mission}', technology '{tech}', group {group}")
    return tab[k] * ALTERNATOR_EFFICIENCY


def hvac_electric_W(group, mission, tech, T=TABLES):
    k = (_m(mission), tech, str(group).lower())
    if k not in T["hvac"]:
        raise LookupError(f"HVAC: no value for mission '{mission}', technology '{tech}', group {group}")
    return T["hvac"][k] * (1.0 / HVAC_ELECTRIC_EFFICIENCY_FACTOR)


def ps_electric_W(mission, tech, T=TABLES):
    rec = T["ps"].get(tech)
    if rec is None:
        raise LookupError(f"PS: unknown technology '{tech}'")
    if not rec["pev"]:
        raise LookupError(f"PS: technology '{tech}' is not applicable for a battery electric vehicle")
    if rec["fully_electric"]:
        k = _m(mission)
        if k not in rec["el"]:
            raise LookupError(f"PS: no fully electric value for mission '{mission}', technology '{tech}'")
        return rec["el"][k]                                   # *_el column used as is (no x0.7)
    return rec["mech"][_m(mission)] * ALTERNATOR_EFFICIENCY   # unreachable for PEV techs in this table


def sp_electric_W(group, mission, techs, T=TABLES):
    """SteeringPump.Lookup + HeavyLorryAuxiliaryDataAdapter 220 for a PEV; techs = one entry per steered axle."""
    if not techs:
        raise LookupError("SP: no technology specified for steering pump")
    base = T["sp_base"].get((_m(mission), str(group).lower()))
    if base is None:
        raise LookupError(f"SP: no baseline for mission '{mission}', group {group}")
    p_el = [0.0, 0.0, 0.0]
    f = [0.0, 0.0, 0.0]
    n_axle = 0
    for tech in techs:
        if tech not in T["sp_tech"]:
            raise LookupError(f"SP: technology '{tech}' not found")
        rec = T["sp_tech"][tech]
        if not rec["pev"]:
            raise LookupError(f"SP: technology '{tech}' is not applicable for a battery electric vehicle")
        n_axle += 1
        ax = T["sp_axle"].get((_m(mission), n_axle))
        if ax is None:
            raise LookupError(f"SP: no axle share for mission '{mission}', steered axle number {n_axle}")
        for i in range(3):
            f[i] += rec["f"][i]
            # SP-Table cells are divided by 100 in ParseData (SteeringPump.cs 142) and the SP-Axles shares are used
            # as raw numbers (100, 70, 50 ... ; ParseData 78), so base[i]/100 * share == base_W * share_% / 100.
            p_el[i] += base[i] * ax[i]
    # SteeringPump.cs 107-111: scale by (sum of tech factors / axleCount)
    p_el = [p_el[i] * f[i] / n_axle for i in range(3)]
    return sum(p_el) * ALTERNATOR_EFFICIENCY


def cond_electric_W(mission, T=TABLES):
    k = _m(mission)
    if k not in T["cond"]:
        raise LookupError(f"Cond: no value for mission '{mission}'")
    return T["cond"][k]
