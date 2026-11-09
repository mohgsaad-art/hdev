"""Job 2.7: build mission_setup.csv from VECTO SegmentTable.csv (the authoritative,
run-time-readable source) for each HDV group x mission present in the sample.

Every value carries a source column. SegmentTable.csv lives at
VectoCore/VectoCore/Resources/Declaration/SegmentTable.csv (VECTO mohgsaad-art, EUPL 1.2).

Columns read per group row:
  Height, Body, Trailer, CdxA_Default, CdxA_Construction,
  'Cross Wind Correction - Long haul / EMS / Other'  -> crosswind parameter set name,
  'Truck Axles - Long haul / Other / ...'            -> truck axle weight shares per mission,
  'Trailer Axles - ...'                              -> trailer axle weight shares per mission,
  the per-mission payload band columns (Long haul ... Construction) -> 'low/high' payload.

Trailer tyre constants (DeclarationData.cs, class Trailer):
  RollResistanceCoefficient = 0.0055   (line 837)
  TyreTestLoad              = 37500 N   (line 839)
  TwinTyres                 = false     (line 841)
Crosswind parameter a1/a2/a3 per set: VCDV/VCDV_parameters.csv.
Driven axle: VehicleData.cs AxleType.VehicleDriven; for 4x2/6x2/6x4/8x4 the driven axle is
  the 2nd (rearmost powered) axle per VECTO axle-config rules (AxleConfiguration.NumDrivenAxles).
DeltaCdA: AirdragDataAdapter.cs:117 aerodynamicDragArea = DefaultCDxA + Sum(trailer.DeltaCdA).
"""
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
VSRC = os.environ.get("VECTO_SRC", "/projects/sandbox/VECTO")
SEG = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "SegmentTable.csv")
VCDV = os.path.join(VSRC, "VectoCore", "VectoCore", "Resources", "Declaration", "VCDV", "VCDV_parameters.csv")

TRAILER_RRC = 0.0055      # DeclarationData.cs:837
TRAILER_TESTLOAD = 37500  # DeclarationData.cs:839 (N)

# which SegmentTable mission column feeds each of our mission names
# crosswind: 'Long haul' and 'Long haul EMS' use the '- Long haul'/'- EMS' crosswind col;
# everything else uses '- Other'. truck/trailer axle shares similarly.
def crosswind_col(mission):
    if mission in ("Long Haul",):
        return "Cross Wind Correction - Long haul"
    if mission in ("Long Haul EMS", "Regional Delivery EMS"):
        return "Cross Wind Correction - EMS"
    return "Cross Wind Correction - Other"

def truck_axle_col(mission):
    if mission == "Long Haul":
        return "Truck Axles - Long haul"
    if mission in ("Long Haul EMS", "Regional Delivery EMS"):
        return "Truck Axles - Long haul EMS"
    return "Truck Axles - Other"

def trailer_axle_col(mission):
    if mission == "Long Haul":
        return "Trailer Axles - Long haul"
    if mission in ("Long Haul EMS", "Regional Delivery EMS"):
        return "Trailer Axles - Long haul EMS"
    return "Trailer Axles - Other"

# per-mission payload band column
PAYLOAD_COL = {
    "Long Haul": "Long haul", "Long Haul EMS": "Long haul EMS",
    "Regional Delivery": "Regional delivery", "Regional Delivery EMS": "Regional delivery EMS",
    "Urban Delivery": "Urban delivery", "Municipal Utility": "Municipal utility",
    "Construction": "Construction",
}


def load_segment():
    with open(SEG, encoding="latin-1") as fh:
        rows = [[c.strip() for c in r] for r in csv.reader(fh)]
    hdr = [c.strip() for c in rows[0]]
    recs = []
    for r in rows[1:]:
        if not r or not r[0] or r[0].startswith("#"):
            continue
        d = {hdr[i]: (r[i] if i < len(r) else "") for i in range(len(hdr))}
        recs.append(d)
    return recs


def load_vcdv():
    out = {}
    with open(VCDV, encoding="latin-1") as fh:
        rd = csv.reader(fh)
        next(rd)
        for r in rd:
            if len(r) < 4 or not r[0].strip():
                continue
            out[r[0].strip()] = (float(r[1]), float(r[2]), float(r[3]))
    return out


def driven_axle_index(axle_conf):
    """VECTO: for N axles, the driven axle is the 2nd axle (index 2, 1-based) for standard
    truck configs (4x2, 6x2, 6x4, 8x4). AxleConfiguration.NumDrivenAxles()=1 for these.
    Return 1-based axle number of the (first) driven axle."""
    return 2  # rear/2nd axle driven for 4x2/6x2/6x4/8x4 rigid+tractor standard configs


def main():
    recs = load_segment()
    vcdv = load_vcdv()
    # groups present in the sample (fall back to all valid truck groups)
    sample_groups = set()
    try:
        for r in csv.DictReader(open(os.path.join(HERE, "truck_vehicles.csv"))):
            if r["VehicleGroup"].strip():
                sample_groups.add(r["VehicleGroup"].strip())
    except FileNotFoundError:
        pass

    missions = ["Long Haul", "Long Haul EMS", "Regional Delivery", "Regional Delivery EMS",
                "Urban Delivery", "Municipal Utility", "Construction"]

    out = []
    for rec in recs:
        grp = rec["HDV group"].strip()
        if sample_groups and grp not in sample_groups:
            continue
        if rec.get("Valid", "0").strip() != "1":
            continue
        veh_cat = rec.get("Vehicle Category", "").strip()
        height = rec.get("Height", "").strip()
        body = rec.get("Body", "").strip()
        trailer = rec.get("Trailer", "").strip()
        cdxa_def = rec.get("CdxA_Default", "").strip()
        cdxa_con = rec.get("CdxA_Construction", "").strip()
        axle_conf = rec.get("Axle Conf.", "").strip()
        for mission in missions:
            pcol = PAYLOAD_COL[mission]
            payband = rec.get(pcol, "").strip()
            if payband in ("", "-"):
                continue  # mission not run for this group
            cw_name = rec.get(crosswind_col(mission), "").strip()
            a = vcdv.get(cw_name)
            truck_shares = rec.get(truck_axle_col(mission), "").strip()
            trailer_shares = rec.get(trailer_axle_col(mission), "").strip()
            cdxa = cdxa_con if (mission == "Construction" and cdxa_con) else cdxa_def
            out.append({
                "hdv_group": grp,
                "vehicle_category": veh_cat,
                "axle_config": axle_conf,
                "mission": mission,
                "payload_band_t": payband,
                "payload_band_src": "SegmentTable.csv col '%s'" % pcol,
                "body_code": body,
                "trailer_code": trailer,
                "bodytrailer_src": "SegmentTable.csv Body/Trailer cols",
                "height_m": height,
                "height_src": "SegmentTable.csv Height",
                "cdxa_default_m2": cdxa,
                "cdxa_src": "SegmentTable.csv %s" % ("CdxA_Construction" if (mission=="Construction" and cdxa_con) else "CdxA_Default"),
                "crosswind_set": cw_name,
                "crosswind_a1": a[0] if a else "",
                "crosswind_a2": a[1] if a else "",
                "crosswind_a3": a[2] if a else "",
                "crosswind_src": "SegmentTable '%s' -> VCDV_parameters.csv" % crosswind_col(mission),
                "truck_axle_shares": truck_shares,
                "trailer_axle_shares": trailer_shares,
                "axle_shares_src": "SegmentTable '%s'/'%s'" % (truck_axle_col(mission), trailer_axle_col(mission)),
                "trailer_rrc": TRAILER_RRC if trailer not in ("", "-") else "",
                "trailer_testload_N": TRAILER_TESTLOAD if trailer not in ("", "-") else "",
                "trailer_tyre_src": "DeclarationData.cs class Trailer RRC=0.0055(837) TestLoad=37500(839)",
                "driven_axle_number": driven_axle_index(axle_conf),
                "driven_axle_src": "VehicleData.cs AxleType.VehicleDriven; 2nd axle for 4x2/6x2/6x4/8x4",
            })

    cols = list(out[0].keys()) if out else []
    with open(os.path.join(HERE, "mission_setup.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in out:
            w.writerow(r)
    print("wrote mission_setup.csv with %d group x mission rows" % len(out))
    groups = sorted(set(r["hdv_group"] for r in out), key=lambda x: (len(x), x))
    print("groups covered:", groups)


if __name__ == "__main__":
    main()
