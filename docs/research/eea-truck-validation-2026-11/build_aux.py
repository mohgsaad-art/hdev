"""Job 2.5: build aux_per_label.csv — the VECTO declaration ELECTRIC aux power [W] for a
PEV, per technology label x mission x HDV group, with the row and arithmetic shown.

Sources (all opened, VECTO mohgsaad-art, EUPL 1.2):
  VAUX/ES-Tech.csv        electric-system mechanical power per mission (Standard technology)
  VAUX/PS-Table.csv       pneumatic: PEV uses the *_el columns directly (GetElectricPowerDemand)
  VAUX/SP-Table.csv       steering-pump baseline per HDV group (UF/B/S)
  VAUX/SP-Axles.csv       steered-axle factor
  VAUX/SP-Tech.csv        steering-pump technology factor (UF/B/S); PEV: electric/full-electric
  VAUX/HVAC-Table.csv     HVAC mechanical power per group per mission (Default/None)
  VAUX/Cond-Table.csv     condenser (Lorry) per mission
Constants (DeclarationData.cs):
  AlternatorEfficiency = 0.7                      line 123  -> ES, mech PS, mech SP electric = mech*0.7
  HVACElectricEfficiencyFactor = 0.8              line 126  -> HVAC electric = mech/0.8
Adapter (HeavyLorryAuxiliaryDataAdapter.cs):
  ES  electric = mech * 0.7                        line 120
  HVAC electric = mech * (1/0.8)                   line 78,165
  PS (PEV elec-driven) electric = *_el column      line 140-143 (IsFullyElectric -> GetElectricPowerDemand)
  SP  electric pumps from SP-Table electric split  line 175-215

Mapping to consumption_engine args (P_aux):
  ES, PS, HVAC -> always-on terms (DemandType=Constant in VECTO)
  SP  -> SP (consumption_engine applies only while moving)
  cond (condenser) -> cond (applied while moving or PTO active)
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VSRC = os.environ.get("VECTO_SRC", "/projects/sandbox/VECTO")
VAUX = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "VAUX")

ALT_EFF = 0.7   # DeclarationData.cs:123 AlternatorEfficiency
HVAC_EFF = 0.8  # DeclarationData.cs:126 HVACElectricEfficiencyFactor

# mission name (our data) -> VAUX column header
MISSION_COL = {
    "Long Haul": "Long haul", "Long Haul EMS": "Long haul",
    "Regional Delivery": "Regional delivery", "Regional Delivery EMS": "Regional delivery",
    "Urban Delivery": "Urban delivery", "Municipal Utility": "Municipal utility",
    "Construction": "Construction",
}
# PS-Table has slightly different mission headers; map separately
PS_COL = {
    "Long Haul": "Long Haul", "Long Haul EMS": "Long Haul",
    "Regional Delivery": "Regional Delivery", "Regional Delivery EMS": "Regional Delivery",
    "Urban Delivery": "Urban  Delivery", "Municipal Utility": "Municipal utility",
    "Construction": "Construction",
}
COND_COL = PS_COL  # Cond-Table uses the same headers as PS-Table


def _read_csv(path):
    with open(path, encoding="latin-1") as fh:
        return [ [c.strip() for c in row] for row in csv.reader(fh) ]


def load_es():
    """ES-Tech.csv: Technology -> {mission_col: mech_W}."""
    rows = _read_csv(os.path.join(VAUX, "ES-Tech.csv"))
    hdr = rows[0]
    out = {}
    for r in rows[1:]:
        if not r or not r[0]:
            continue
        tech = r[0]
        out[tech] = {hdr[i]: r[i] for i in range(1, len(hdr))}
    return out, hdr


def load_ps():
    """PS-Table.csv: Technology -> {col: val}. PEV uses *_el columns."""
    rows = _read_csv(os.path.join(VAUX, "PS-Table.csv"))
    hdr = rows[0]
    out = {}
    for r in rows[1:]:
        if not r or not r[0]:
            continue
        out[r[0]] = {hdr[i]: r[i] for i in range(1, len(hdr))}
    return out


def load_hvac():
    """HVAC-Table.csv: (Technology, group) -> {mission_col: mech_W}."""
    rows = _read_csv(os.path.join(VAUX, "HVAC-Table.csv"))
    hdr = rows[0]
    out = {}
    for r in rows[1:]:
        if not r or not r[0] or r[0].startswith("#"):
            continue
        tech, grp = r[0], r[1]
        out[(tech, grp)] = {hdr[i]: r[i] for i in range(2, len(hdr))}
    return out


def load_cond():
    rows = _read_csv(os.path.join(VAUX, "Cond-Table.csv"))
    hdr = rows[0]
    for r in rows[1:]:
        if r and r[0] == "Lorry":
            return {hdr[i]: r[i] for i in range(1, len(hdr))}
    return {}


def fnum(s):
    s = (s or "").strip()
    if s in ("", "n.a.", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main():
    es, es_hdr = load_es()
    ps = load_ps()
    hvac = load_hvac()
    cond = load_cond()

    # labels present in the in-scope fleet (from build_aux_labels.py output or recomputed)
    # pneumatic + steering labels seen (2.5 counts)
    inscope = set(r["Vehicle_id"] for r in csv.DictReader(open(os.path.join(HERE, "truck_vehicles.csv"))))
    pneu = {}
    hvac_cfg = {}
    for r in csv.DictReader(open(os.path.join(HERE, "..", "eea-hdv-2024-join", "vehicles_xev.csv"))):
        if r["Vehicle_id"] in inscope:
            pneu[r["Vehicle_id"]] = r.get("Aux_Pneumatic_Technology", "")
            hvac_cfg[r["Vehicle_id"]] = r.get("Aux_HVAC_SystemConfiguration", "")
    steer = {}
    for r in csv.DictReader(open(os.path.join(HERE, "..", "eea-hdv-2024-join", "steering_xev.csv"))):
        steer[r["Vehicle_id"]] = r.get("SteeringpumpTechnology", "")

    pneu_labels = sorted(set(pneu.values()))
    steer_labels = sorted(set(steer.get(v, "") for v in inscope))

    missions = ["Long Haul", "Regional Delivery", "Urban Delivery", "Municipal Utility", "Construction"]

    out = []
    # ES: one standard-technology row per mission (electric = mech * 0.7)
    for mission in missions:
        col = MISSION_COL[mission]
        mech = fnum(es.get("Standard technology", {}).get(col))
        if mech is None:
            out.append(["ES", "Standard technology", mission, "", "", "no_row", ""])
            continue
        elec = mech * ALT_EFF
        out.append(["ES", "Standard technology", mission, "", round(mech, 1),
                    round(elec, 1), "ES-Tech.csv Standard technology [%s] mech=%.1f * AlternatorEff 0.7 = %.1f" % (col, mech, elec)])

    # PS (pneumatic): PEV uses *_el column directly (electric)
    for lbl in pneu_labels:
        if lbl == "":
            continue
        for mission in missions:
            base_col = PS_COL[mission]
            el_col = base_col + "_el" if (base_col + "_el") in ps.get(lbl, {}) else None
            # PS-Table _el headers are like 'Long Haul_el','Regional Delivery_el', etc.
            # match loosely
            row = ps.get(lbl, {})
            el_key = None
            for k in row:
                if k.strip().lower() == (base_col + "_el").strip().lower():
                    el_key = k
                    break
            if el_key is None:
                out.append(["PS", lbl, mission, "", "", "no_PEV_el_row_skip", ""])
                continue
            elec = fnum(row.get(el_key))
            if elec is None:
                out.append(["PS", lbl, mission, "", "", "na_skip", ""])
                continue
            out.append(["PS", lbl, mission, "", "", round(elec, 1),
                        "PS-Table.csv '%s' [%s]=%.1f (PEV electric, used directly)" % (lbl, el_key, elec)])

    # HVAC: config blank in EEA -> cannot pick Default vs None per truck; report Default as the
    # declaration standard for each group, electric = mech / 0.8. (EEA HVAC config 0% filled.)
    groups_present = sorted(set(
        r["VehicleGroup"] for r in csv.DictReader(open(os.path.join(HERE, "truck_vehicles.csv")))
        if r["Vehicle_id"] in inscope and r["VehicleGroup"].strip()
    ), key=lambda x: (len(x), x))
    for grp in groups_present:
        for mission in missions:
            col = MISSION_COL[mission]
            rec = hvac.get(("Default", grp))
            if rec is None:
                out.append(["HVAC", "Default", "%s|%s" % (grp, mission), "", "", "no_group_row", ""])
                continue
            mech = fnum(rec.get(col))
            if mech is None:
                out.append(["HVAC", "Default(grp %s)" % grp, mission, "", "", "no_value(blank)", ""])
                continue
            elec = mech / HVAC_EFF
            out.append(["HVAC", "Default(grp %s)" % grp, mission, "", round(mech, 1),
                        round(elec, 1), "HVAC-Table.csv Default grp %s [%s] mech=%.1f / 0.8 = %.1f" % (grp, col, mech, elec)])

    # Condenser (cond): Lorry per mission, applied while moving or PTO
    for mission in missions:
        col = COND_COL[mission]
        v = fnum(cond.get(col))
        if v is None:
            out.append(["cond", "Lorry", mission, "", "", "no_value", ""])
            continue
        out.append(["cond", "Lorry", mission, "", "", round(v, 1),
                    "Cond-Table.csv Lorry [%s]=%.1f (electric, moving/PTO)" % (col, v)])

    with open(os.path.join(HERE, "aux_per_label.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["aux_term", "label", "mission", "hdv_group", "mech_W", "electric_W", "source_and_arithmetic"])
        for r in out:
            w.writerow(r)

    # label counts file
    from collections import Counter
    pc = Counter(pneu.values()); sc = Counter(steer.get(v, "(no row)") for v in inscope)
    hc = Counter(hvac_cfg.values())
    with open(os.path.join(HERE, "aux_label_counts.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["dimension", "label", "vehicle_count"])
        for lbl, n in pc.most_common():
            w.writerow(["Aux_Pneumatic_Technology", lbl or "(blank)", n])
        for lbl, n in sc.most_common():
            w.writerow(["SteeringpumpTechnology", lbl or "(blank)", n])
        for lbl, n in hc.most_common():
            w.writerow(["Aux_HVAC_SystemConfiguration", lbl or "(blank)", n])
    print("wrote aux_per_label.csv (%d rows) and aux_label_counts.csv" % len(out))
    print("pneumatic labels:", dict(pc))
    print("steering labels:", dict(sc))
    print("HVAC config labels:", dict(hc))


if __name__ == "__main__":
    main()
