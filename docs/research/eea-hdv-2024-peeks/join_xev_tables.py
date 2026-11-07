# Colab cell: join the EEA HDV RP 2024-25 tables for electric/hybrid vehicles
# Output: a few small CSVs you can download and send back (or push to the repo).
#
# Before running:
#   - Put each file location in PATHS below.
#     Either a path in your mounted Drive ("/content/drive/MyDrive/...csv")
#     or a Drive sharing link ("https://drive.google.com/...") set to "Anyone with the link".
#   - Big files (vehicle 2 GB, missionprofile 9.5 GB, memberstate 0.5 GB) are read in chunks,
#     so they never load fully into memory. They are slow: the missionprofile pass is the longest.
#
# Nothing here averages vehicles into one value. Every vehicle keeps its own row (vehicles_xev.csv).
# The config and mission summaries only GROUP identical configurations and report min/median/max.

PATHS = {
    "vehicle":                     "PASTE_PATH_OR_LINK",
    "battery":                     "PASTE_PATH_OR_LINK",
    "electricmachine":             "PASTE_PATH_OR_LINK",
    "iepc":                        "PASTE_PATH_OR_LINK",
    "voltagelevel_electricmachine":"PASTE_PATH_OR_LINK",
    "voltagelevel_iepc":           "PASTE_PATH_OR_LINK",
    "capacitor":                   "PASTE_PATH_OR_LINK",
    "missionprofile":              "PASTE_PATH_OR_LINK",
    "memberstate_vehicle":         "PASTE_PATH_OR_LINK",
}

MOUNT_DRIVE = True        # True if any path above is a /content/drive/... path
CHUNK = 500_000           # rows per chunk for the big files
OUT = "xev_join_out"      # output folder

import os
import pandas as pd

if MOUNT_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")

try:
    import gdown
except ImportError:
    os.system("pip install -q gdown")
    import gdown

os.makedirs(OUT, exist_ok=True)
NULLS = ["", "NULL", "null", "N.A.", "N/A", "-"]
YES = {"true", "1", "yes", "y"}


def local(path_or_link, name):
    # download a Drive link once; a plain path is used as it is
    if path_or_link.startswith("http"):
        target = f"downloads/{name}.csv"
        os.makedirs("downloads", exist_ok=True)
        if not os.path.exists(target):
            gdown.download(path_or_link, output=target, fuzzy=True, quiet=False)
        return target
    return path_or_link


def read_small(name):
    # the small tables are read in full, everything as text
    return pd.read_csv(local(PATHS[name], name), dtype=str, encoding="utf-8-sig",
                       na_values=NULLS, keep_default_na=False)


def to_num(series):
    return pd.to_numeric(series, errors="coerce")


def is_yes(series):
    return series.fillna("").str.strip().str.lower().isin(YES)


# ---------------------------------------------------------------- 1. small electric tables
print("reading small tables ...")
bat = read_small("battery")
em = read_small("electricmachine")
iepc = read_small("iepc")
vl_em = read_small("voltagelevel_electricmachine")
vl_iepc = read_small("voltagelevel_iepc")
cap = read_small("capacitor")

for df in [bat, em, iepc, vl_em, vl_iepc, cap]:
    print(f"  rows {len(df):>7,}   vehicles {df['Vehicle_id'].nunique():>6,}")

# all vehicles that have any electric component record
electric_ids = set(bat.Vehicle_id) | set(em.Vehicle_id) | set(iepc.Vehicle_id) | set(cap.Vehicle_id)
print("vehicles with any electric component record:", len(electric_ids))

# ---------------------------------------------------------------- 2. per-vehicle summaries
# battery: one row per pack -> sum per vehicle, keep pack details as text
bat["inst"] = to_num(bat.TotalStorageCapacity)
bat["use"] = to_num(bat.TotalUsableCapacityInSimulation)
bat["pack"] = bat.TotalStorageCapacity.astype(str) + "/" + bat.TotalUsableCapacityInSimulation.astype(str)
bat_v = bat.groupby("Vehicle_id").agg(
    bat_packs=("Id", "size"),
    bat_installed_kwh=("inst", "sum"),
    bat_usable_sim_kwh=("use", "sum"),
    bat_packs_inst_use=("pack", lambda s: ";".join(sorted(s))),
    bat_nominal_v=("NominalVoltage", lambda s: ";".join(sorted(set(s.dropna())))),
    bat_cert_method=("CertificationMethod", lambda s: ";".join(sorted(set(s.dropna())))),
).reset_index()

# electric machines: type, position, count, rated kW per vehicle
em["rated"] = to_num(em.RatedPower)
em["count"] = to_num(em.CountAtPosition).fillna(1)
em["desc"] = ("P" + em.Position.astype(str) + "x" + em.CountAtPosition.astype(str)
              + ":" + em.ElectricMachineType.astype(str) + ":" + em.RatedPower.astype(str) + "kW")
em_v = em.groupby("Vehicle_id").agg(
    em_rows=("ElectricMachine_id", "size"),
    em_desc=("desc", lambda s: ";".join(sorted(s))),
    em_rated_kw_total=("rated", lambda s: (s * em.loc[s.index, "count"]).sum()),
    em_cert_method=("CertificationMethod", lambda s: ";".join(sorted(set(s.dropna())))),
).reset_index()

# max continuous power per machine (voltage-level table has duplicates; keep the max per machine)
vl_em["p"] = to_num(vl_em.MaxContinuousPower)
vl_em_v = (vl_em.groupby(["Vehicle_id", "ElectricMachineId"]).p.max()
           .groupby("Vehicle_id").agg(lambda s: ";".join(str(int(x)) for x in sorted(s.dropna())))
           .rename("em_max_cont_kw").reset_index())

# IEPC
iepc["desc"] = (iepc.RatedPower.astype(str) + "kW:g" + iepc.NrOfGears.astype(str)
                + ":r" + iepc.LowestTotalTransmissionRatio.astype(str)
                + ":wheel=" + iepc.DesignTypeWheelMotor.astype(str)
                + ":diff=" + iepc.DifferentialIncluded.astype(str))
iepc_v = iepc.groupby("Vehicle_id").agg(
    iepc_rows=("Pk_Vehicle", "size"),
    iepc_desc=("desc", lambda s: ";".join(sorted(s))),
    iepc_cert_method=("CertificationMethod", lambda s: ";".join(sorted(set(s.dropna())))),
).reset_index()

vl_iepc["p"] = to_num(vl_iepc.MaxContinuousPower)
vl_iepc_v = (vl_iepc.groupby(["Vehicle_id", "IEPCId"]).p.max()
             .groupby("Vehicle_id").agg(lambda s: ";".join(str(int(x)) for x in sorted(s.dropna())))
             .rename("iepc_max_cont_kw").reset_index())

cap_v = cap.groupby("Vehicle_id").agg(
    cap_rows=("Pk_Vehicle", "size"),
    cap_capacitance_f=("Capacitance", lambda s: ";".join(sorted(set(s.dropna())))),
).reset_index()

# ---------------------------------------------------------------- 3. vehicle table (2 GB, chunked)
VEH_COLS = [
    "Vehicle_id", "Make", "Model", "Manufacturer", "VehicleCategory", "VehicleGroup", "VehicleGroupCO2",
    "CorrectedActualMass", "TechnicalPermissibleMaximumLadenMass", "TechnicalPermissibleMaximumLadenMass_unit",
    "ZeroEmissionVehicle", "HybridElectricHDV", "VocationalVehicle", "AxleConfiguration", "SleeperCab",
    "ClassBus", "BodyworkCode", "VehicleLength", "HEVArchitecture", "PEVArchitecture",
    "OffVehicleChargingCapability", "OffVehicleChargingMaxPower", "OffVehicleChargingMaxPower_unit",
    "Transmission_Type", "Transmission_NrOfGears", "Transmission_PowerTakeOff",
    "Axlegear_CertificationMethod", "Axlegear_AxleType", "Axlegear_Ratio",
    "AirDrag_CertificationMethod", "AirDrag_CdxA_range",
    "Aux_Pneumatic_Technology", "Aux_HVAC_SystemConfiguration",
    "Aux_HVAC_HeatPumpTypeDriverCompartment_Heating", "Aux_HVAC_HeatPumpTypeDriverCompartment_Cooling",
    "Aux_HVAC_HeatPumpTypePassengerCompartment_Heating", "Aux_HVAC_HeatPumpTypePassengerCompartment_Cooling",
    "Aux_HVAC_AuxiliaryHeaterPower", "Aux_HVAC_WaterElectricHeater", "Aux_HVAC_AirElectricHeater",
    "Aux_Electric_ElectricStorageCapacity", "SimulationToolVersion", "SimulationDate",
]

print("reading vehicle table in chunks ...")
kept = []
total = 0
for chunk in pd.read_csv(local(PATHS["vehicle"], "vehicle"), usecols=VEH_COLS, dtype=str,
                         encoding="utf-8-sig", na_values=NULLS, keep_default_na=False, chunksize=CHUNK):
    total += len(chunk)
    keep = (is_yes(chunk.ZeroEmissionVehicle) | is_yes(chunk.HybridElectricHDV)
            | chunk.Vehicle_id.isin(electric_ids))
    kept.append(chunk[keep])
    print(f"  {total:,} rows read")
veh = pd.concat(kept, ignore_index=True)
print("vehicle rows kept:", len(veh), " unique Vehicle_id:", veh.Vehicle_id.nunique())

# normalise flags and the max laden mass unit (seen as kg and as t)
veh["is_zev"] = is_yes(veh.ZeroEmissionVehicle)
veh["is_hev"] = is_yes(veh.HybridElectricHDV)
tpmlm = to_num(veh.TechnicalPermissibleMaximumLadenMass)
unit = veh.TechnicalPermissibleMaximumLadenMass_unit.fillna("").str.strip().str.lower()
veh["tpmlm_kg"] = tpmlm.where(unit != "t", tpmlm * 1000)
veh["powertrain_flag"] = "other"
veh.loc[veh.is_hev, "powertrain_flag"] = "HEV flag"
veh.loc[veh.is_zev, "powertrain_flag"] = "ZEV flag"

# ---------------------------------------------------------------- 4. join everything per vehicle
v = veh
for part in [bat_v, em_v, vl_em_v, iepc_v, vl_iepc_v, cap_v]:
    v = v.merge(part, on="Vehicle_id", how="left")

# join check: electric records that found no vehicle row
missing = electric_ids - set(veh.Vehicle_id)
print("electric component vehicles NOT found in vehicle table:", len(missing))

# ---------------------------------------------------------------- 5. registrations (memberstate, chunked)
print("reading memberstate_vehicle in chunks ...")
ms_cols = ["MS", "vehicle_id", "Electric", "Hybrid", "RegistrationDateClean", "NumberOfAxles",
           "TechnPermMaxLadenMass", "WMI"]
ms_parts = []
ids = set(v.Vehicle_id)
for chunk in pd.read_csv(local(PATHS["memberstate_vehicle"], "memberstate_vehicle"), usecols=ms_cols, dtype=str,
                         encoding="utf-8-sig", na_values=NULLS, keep_default_na=False, chunksize=CHUNK):
    ms_parts.append(chunk[chunk.vehicle_id.isin(ids)])
ms = pd.concat(ms_parts, ignore_index=True).rename(columns={"vehicle_id": "Vehicle_id"})
print("registration rows for these vehicles:", len(ms))

reg_v = ms.groupby("Vehicle_id").agg(
    reg_count=("MS", "size"),
    reg_countries=("MS", lambda s: ";".join(sorted(set(s.dropna())))),
    reg_first=("RegistrationDateClean", "min"),
    reg_last=("RegistrationDateClean", "max"),
    reg_dk=("MS", lambda s: int((s == "DK").sum())),
).reset_index()
v = v.merge(reg_v, on="Vehicle_id", how="left")

# ---------------------------------------------------------------- 6. mission results (9.5 GB, chunked)
print("reading missionprofile in chunks (longest step) ...")
mp_cols = ["Vehicle_id", "Mission", "Mode", "ResultType", "Distance", "TotalVehicleMass", "Payload",
           "ActualChargeDepletingRange", "ActualChargeDepletingRange_unit",
           "EquivalentAllElectricRange", "EquivalentAllElectricRange_unit",
           "ZeroCO2EmissionRange", "ZeroCO2EmissionRange_unit",
           "AverageSpeed", "ElectricEnergy_kwh_km", "ElectricEnergy_kwh_t_km", "ElectricEnergy_kwh_p_km",
           "FC_FuelType", "FC_l_100km", "CO2_g_km"]
mp_parts = []
total = 0
for chunk in pd.read_csv(local(PATHS["missionprofile"], "missionprofile"), usecols=mp_cols, dtype=str,
                         encoding="utf-8-sig", na_values=NULLS, keep_default_na=False, chunksize=CHUNK):
    total += len(chunk)
    mp_parts.append(chunk[chunk.Vehicle_id.isin(ids)])
    if total % 5_000_000 < CHUNK:
        print(f"  {total:,} rows read")
mp = pd.concat(mp_parts, ignore_index=True)
print("mission rows for these vehicles:", len(mp))

# ---------------------------------------------------------------- 7. save per-vehicle and per-mission tables
v.to_csv(f"{OUT}/vehicles_xev.csv", index=False)
mp.to_csv(f"{OUT}/missions_xev.csv", index=False)

# ---------------------------------------------------------------- 8. group identical configurations
CONFIG_KEYS = ["powertrain_flag", "Make", "Model", "VehicleCategory", "VehicleGroup", "AxleConfiguration",
               "PEVArchitecture", "HEVArchitecture", "Axlegear_Ratio", "Transmission_NrOfGears",
               "AirDrag_CdxA_range", "bat_packs_inst_use", "bat_nominal_v", "em_desc", "em_max_cont_kw",
               "iepc_desc", "iepc_max_cont_kw", "OffVehicleChargingMaxPower",
               "Aux_Pneumatic_Technology", "Aux_HVAC_SystemConfiguration"]
cfg = v[CONFIG_KEYS + ["Vehicle_id", "CorrectedActualMass", "tpmlm_kg", "reg_count", "reg_dk"]].copy()
cfg["CorrectedActualMass"] = to_num(cfg.CorrectedActualMass)
cfg = (cfg.fillna({k: "" for k in CONFIG_KEYS})
       .groupby(CONFIG_KEYS).agg(
           vehicles=("Vehicle_id", "nunique"),
           registrations=("reg_count", "sum"),
           registrations_dk=("reg_dk", "sum"),
           curb_mass_min=("CorrectedActualMass", "min"),
           curb_mass_max=("CorrectedActualMass", "max"),
           tpmlm_kg_min=("tpmlm_kg", "min"),
           tpmlm_kg_max=("tpmlm_kg", "max"),
       ).reset_index().sort_values("vehicles", ascending=False))
cfg.to_csv(f"{OUT}/configs_xev.csv", index=False)

# mission results per configuration, mission and payload (min / median / max, no single average)
mp2 = mp.merge(v[["Vehicle_id"] + CONFIG_KEYS].fillna(""), on="Vehicle_id", how="left")
for c in ["Payload", "ElectricEnergy_kwh_km", "ActualChargeDepletingRange", "EquivalentAllElectricRange", "ZeroCO2EmissionRange"]:
    mp2[c] = to_num(mp2[c])
mp_cfg = (mp2[mp2.ElectricEnergy_kwh_km.notna()]
          .groupby(["Make", "Model", "VehicleGroup", "PEVArchitecture", "bat_packs_inst_use",
                    "em_desc", "iepc_desc", "Mission", "Payload"], dropna=False)
          .agg(vehicles=("Vehicle_id", "nunique"),
               kwh_km_min=("ElectricEnergy_kwh_km", "min"),
               kwh_km_median=("ElectricEnergy_kwh_km", "median"),
               kwh_km_max=("ElectricEnergy_kwh_km", "max"),
               cd_range_km_min=("ActualChargeDepletingRange", "min"),
               cd_range_km_max=("ActualChargeDepletingRange", "max"))
          .reset_index())
mp_cfg.to_csv(f"{OUT}/missions_by_config_xev.csv", index=False)

# ---------------------------------------------------------------- 9. completeness report
lines = []
def say(t=""):
    print(t)
    lines.append(str(t))

say(f"vehicle rows kept: {len(v):,}")
say(v.powertrain_flag.value_counts().to_string())
say()
say("share of vehicles with each electric record (%), by powertrain flag:")
has = pd.DataFrame({
    "battery": v.bat_packs.notna(),
    "e_machine": v.em_rows.notna(),
    "iepc": v.iepc_rows.notna(),
    "capacitor": v.cap_rows.notna(),
    "mission_kwh_km": v.Vehicle_id.isin(mp.loc[mp.ElectricEnergy_kwh_km.notna(), "Vehicle_id"]),
    "registration": v.reg_count.notna(),
    "flag": v.powertrain_flag,
})
say((has.groupby("flag").mean() * 100).round(1).to_string())
say()
zev = v[v.is_zev]
say(f"ZEV-flag vehicles: {len(zev):,}. Non-empty share per field (%):")
say((zev.notna().mean() * 100).round(1).sort_values().to_string())
say()
say("ZEV-flag vehicles per make (top 30):")
say(zev.Make.value_counts().head(30).to_string())
say()
say(f"electric component vehicles not found in vehicle table: {len(missing):,}")
say(f"mission rows with kWh/km: {mp.ElectricEnergy_kwh_km.notna().sum():,}")
say("missions present for ZEV vehicles:")
say(mp[mp.Vehicle_id.isin(zev.Vehicle_id)].Mission.value_counts().to_string())

with open(f"{OUT}/join_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

for name in sorted(os.listdir(OUT)):
    print(f"{OUT}/{name}", round(os.path.getsize(f"{OUT}/{name}") / 1e6, 2), "MB")
