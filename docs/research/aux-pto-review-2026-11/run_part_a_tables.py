"""Part A tables: (1) re-verification of the key claims of docs/research/vecto/06, 07, 14 at VECTO b8d6126 (line numbers found by grep
in the actual source, so they cannot be mistyped); (2) the list of hard-coded numbers in Appendix 1.1-1.4; (3) Q10 terms with sizes.
Deterministic.   Run: python run_part_a_tables.py   (VECTO_SRC defaults to /projects/sandbox/vecto-src)"""
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _load_notebook import REPO  # noqa: E402

SRC = os.environ.get("VECTO_SRC", "/projects/sandbox/vecto-src")
CORE = os.path.join(SRC, "VectoCore", "VectoCore")


def commit():
    return subprocess.run(["git", "-C", SRC, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def find(rel, pattern, nth=1):
    p = os.path.join(CORE, rel)
    n = 0
    with open(p, encoding="utf-8-sig", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if re.search(pattern, line):
                n += 1
                if n == nth:
                    return i, line.strip()
    return None, ""


E_ = "Models/SimulationComponent/Impl/Auxiliaries/ElectricAuxiliaries.cs"
CO = "Models/SimulationComponent/Impl/Auxiliaries/Conditioning.cs"
CLAIMS = [
    # (doc, claim, file, regex, cited_line_in_old_doc, status_if_found, comment)
    ("06", "AlternatorEfficiency = 0.7", "Models/Declaration/DeclarationData.cs", r"AlternatorEfficiency = 0\.7", 128, "CONFIRMED (value) / line moved", "value same; v5.1.3 cited :128"),
    ("06", "DCDCEfficiency = 1.0", "Models/Declaration/DeclarationData.cs", r"DCDCEfficiency = 1\.0", 129, "CONFIRMED (value) / line moved", "value same; v5.1.3 cited :129"),
    ("06", "HVACElectricEfficiencyFactor = 0.8", "Models/Declaration/DeclarationData.cs", r"HVACElectricEfficiencyFactor = 0\.8", 131, "CONFIRMED (value) / line moved", "value same; v5.1.3 cited :131"),
    ("06", "HVAC multiplied by 1/0.8 (=1.25)", "InputData/Reader/DataObjectAdapter/SimulationComponents/AuxiliaryDataAdapter/HeavyLorryAuxiliaryDataAdapter.cs", r"1/DeclarationData\.HVACElectricEfficiencyFactor", None, "CONFIRMED", "factor is 1/0.8 = 1.25, direction multiply"),
    ("06", "SteeringPump (ID STP) dropped when VehicleStopped", E_, r"VehicleInfo\.VehicleStopped", None, "CONFIRMED", "ElectricAuxiliaries.PowerDemand"),
    ("06", "SteeringPump and SteeringPump_el share ID 'STP'", "Configuration/Constants.cs", r"SteeringPump_el = \"STP\"", None, "CONFIRMED", "Constants.cs 59-60"),
    ("06", "Cond on when EM on or EPTO on", CO, r"oneEmOn \|\| EPTOOn", 85, "CONFIRMED / line moved", "v5.1.3 cited :85-91"),
    ("06", "Cond table by mission only (no group key)", "Models/Declaration/Auxiliaries/Conditioning.cs", r"Data\[col\.Caption\.ParseEnum<MissionType>\(\)\]", None, "CONFIRMED", ""),
    ("06", "VehicleStopped = |v| <= 0.01 m/s on PreviousState", "Models/SimulationComponent/Impl/Vehicle.cs", r"VehicleStopped =>", None, "CONFIRMED (new detail: PreviousState.Velocity = start-of-step speed)", "prompt cites :262"),
    ("06", "EmOff = PreviousState.EMTorque == null", "Models/SimulationComponent/Impl/ElectricMotor.cs", r"EmOff => PreviousState\.EMTorque == null", 59, "CORRECTED line (now :32); named EmOff, not EmOffPrev", "earlier docs: ElectricMotor.cs:59 EmOffPrev"),
    ("06", "BEV declares exactly ES, HVAC, PS, SP (+Cond)", "InputData/Reader/DataObjectAdapter/SimulationComponents/AuxiliaryDataAdapter/HeavyLorryAuxiliaryDataAdapter.cs", r"class HeavyLorryPEVAuxiliaryDataAdapter", None, "CONFIRMED", ""),
    ("07", "P_PTO_el parsed as kW -> W (x1000)", "InputData/Reader/ComponentData/DrivingCycleDataReader.cs", r"ParseDouble\(Fields\.PTOElectricalPowerDemand\) \* 1000", 845, "CONFIRMED / line moved", "v5.1.3 cited :845; now :841"),
    ("07", "EPTO is an IAuxDemand, AuxID PTOConsumer", "Models/SimulationComponent/Impl/EPTO.cs", r"AuxID => Constants\.Auxiliaries\.IDs\.PTOConsumer", None, "CONFIRMED", ""),
    ("07", "default E-PTO cycle = MunicipalUtility_PTO_generic.vptoel", "Models/Declaration/DeclarationData.cs", r"DefaultE_PTOActivationCycle", 1795, "CONFIRMED / line moved", "v5.1.3 cited :1795; now :1676"),
    ("14", "stop time = StoppingTime + PTO duration", "Models/SimulationComponent/Impl/DistanceBasedDrivingCycle.cs", r"Left\.StoppingTime \+ IdleController\.Duration", 226, "CONFIRMED / line moved", "v5.1.3 cited :226-227; now :218-220 (prompt: ~218-220)"),
    ("14", "3-phase stop (StoppingTime <= 6 x 0.5 s): idle StoppingTime/2, PTO, idle StoppingTime/2", "Models/SimulationComponent/Impl/DistanceBasedDrivingCycle.cs", r"GetStopTimeIntervalThreePhasesPTO\(\)$", 264, "CONFIRMED / line moved", "v5.1.3 cited :248-310; now :242-304"),
    ("14", "7-phase stop for StoppingTime > 3 s", "Models/SimulationComponent/Impl/DistanceBasedDrivingCycle.cs", r"GetStopTimeIntervalSevenPhasesPTO\(\)$", 281, "CONFIRMED / line moved", "idle on each side is also StoppingTime/2 (0.5+(S/2-1)+0.5)"),
    ("14", "PTOActivity enum 0..3", "Models/SimulationComponent/Data/DrivingCycleData.cs", r"PTOActivityWhileDrive = 3", 321, "CONFIRMED / line moved", "v5.1.3 cited :321-326; now :306-312"),
    ("14", "road sweeping / while-drive PTO only in Engineering mode", "Models/Simulation/Impl/PowertrainBuilderBase.cs", r"ExecutionMode\.Engineering", 325, "CONFIRMED / line moved", "now :325 and :339 (prompt ~325, 339)"),
    ("14", "SP: x0.7 in HeavyLorryAuxiliaryDataAdapter (v5.1.3 :239)", "InputData/Reader/DataObjectAdapter/SimulationComponents/AuxiliaryDataAdapter/HeavyLorryAuxiliaryDataAdapter.cs", r"powerDemand\.electricPumps \* alternatorEfficiency", 239, "CONFIRMED / line moved", "now :220 (prompt cites 220)"),
    ("14", "steered axle count check", "InputData/Reader/DataObjectAdapter/SimulationComponents/AuxiliaryDataAdapter/HeavyLorryAuxiliaryDataAdapter.cs", r"auxData\.Technology\.Count != numSteeredAxles", 212, "CONFIRMED / line moved", "now :188-190 (prompt cites 188-190)"),
    ("14", "SteeringPump.Lookup 58-114", "Models/Declaration/Auxiliaries/SteeringPump.cs", r"public \(Watt mechanicalPumps, Watt electricPumps\) Lookup", 58, "CONFIRMED", "starts :58 in both; ends :115"),
    ("14", "ElectricAuxDemand is 0 in Declaration (PowertrainBuilder 642/778)", "Models/Simulation/Impl/PowertrainBuilder.cs", r"data\.ElectricAuxDemand = 0\.SI<Watt>\(\)", 642, "CORRECTED lines", "only ONE assignment found, at the serial-hybrid builder (:599); BEV builders do not zero it. Declaration inputs have no such value (E2 .vmod column P_aux_P_aux_el_el = 0 [TEST])"),
    ("14", "'no idle/transmission loss for electric PTO' (14 A2.6)", "Models/Simulation/Impl/PowertrainBuilderBase.cs", r"pto\.AddConstant\(Constants\.Auxiliaries\.IDs\.PTOTransmission", None, "CORRECTED", "WRONG for a BEV that declares a mechanical PTO type: GetPEVPTO adds a constant TORQUE loss (PTO-tech.csv Torque Loss) on the shaft in front of the EM whenever a gear is engaged and the shaft turns; see partA_q10_unmodelled_terms.csv"),
    ("14", "PTO cycle only on MunicipalUtility; other missions only the transmission loss", "InputData/Reader/Impl/DeclarationMode/HeavyLorryRunDataFactory/DeclarationModeHeavyLorryRunDataFactory.cs", r"mission\.MissionType == MissionType\.MunicipalUtility", None, "NEW (not in 06/07/14)", "line :251: MunicipalUtility -> CreatePTOCycleData, else CreatePTOTransmissionData (drag only)"),
    ("14", "drive PTO overlap throws", "Models/SimulationComponent/Impl/PTODriveAuxiliary.cs", r"Additional PTO activation during drive requested while PTO still active", None, "NEW", "VectoSimulationException when a second PTO=3 row starts while the profile runs"),
    ("14", "EPTO profile sampling = left sample (step hold) per file row", "Models/SimulationComponent/Impl/PTOCycleController.cs", r"LeftSample = _ptoActive \? CycleIterator\.LeftSample", None, "NEW", "each .vptoel row is held until the next row; last row only marks the end"),
]
rows = []
c = commit()
for doc, claim, rel, rx, cited, status, comment in CLAIMS:
    ln, text = find(rel, rx)
    st = ("NOT FOUND at " + c) if ln is None else status
    if ln is not None and cited is not None and ln == cited and status.startswith("CONFIRMED / line moved"):
        status = "CONFIRMED"
    rows.append(dict(doc=doc, claim=claim, file=rel, vecto_commit=c, line_found=ln, line_cited_in_old_doc=cited, status=st, code_line=text[:150], comment=comment))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(HERE, "partA_reverification_06_07_14.csv"), index=False)

hard = [
    ("P_aux", "ES_alteff=0.7", "VECTO constant", "DeclarationData.cs:123 AlternatorEfficiency; HeavyLorryAuxiliaryDataAdapter.cs:118-120", "default argument, parser should pass it (engine purity)"),
    ("P_aux", "PS_alteff=1.0", "VECTO constant (identity)", "HeavyLorryAuxiliaryDataAdapter.cs:140-143 (_el columns used as is)", "valid only for fully-electric PS (always the case for a PEV)"),
    ("P_aux", "HVAC_eff=1.25", "VECTO constant", "DeclarationData.cs:126 (0.8) + HeavyLorryAuxiliaryDataAdapter.cs:78 (1/0.8)", "must be 1.0 for thermal-model HVAC"),
    ("P_aux", "SP_alteff=0.7", "VECTO constant", "HeavyLorryAuxiliaryDataAdapter.cs:220", ""),
    ("P_aux", "cond_eff=1.0", "VECTO constant (identity)", "HeavyLorryAuxiliaryDataAdapter.cs:106 (no factor)", ""),
    ("P_aux", "PTO_eff=1.0", "HDEV choice", "no VECTO equivalent (E-PTO W taken as electric)", "parser input; default 1.0 = already electric"),
    ("P_aux", "< 0, <= 0 limits", "numerical/validity guard", "", "unit-less guards"),
    ("SP_power_helper", "/ 100", "unit definition", "SteeringPump.cs:142 (/100) combined with raw axle shares", "percent -> fraction; equivalent form"),
    ("SP_power_helper", "shape[1] != 3", "VECTO structure (UF, B, S)", "SteeringPump.cs 87-99", ""),
    ("pto_engine", "is_on[0] = 0", "HDEV decision", "no VECTO equivalent", "depot never PTO"),
    ("pto_engine", "astype(int) on np.diff(t)", "numerical (truncation)", "", "BUG for fractional seconds; parser must enforce whole seconds"),
    ("pto_engine", "/ 2 and floor", "VECTO rule (centred) + HDEV rounding", "DistanceBasedDrivingCycle.cs:264-304 (StoppingTime/2 each side)", "floor for odd seconds is an HDEV choice (VECTO uses half seconds)"),
    ("pto_engine", "stop > 0, is_on > 0, pto_dur > 0, pto_start < 0", "numerical comparisons", "", "is_on > 0 here vs == 1 in consumption_engine"),
    ("consumption_engine 6", "V == 0", "numerical tolerance (exact zero)", "driver_model sets V = 0.0 exactly", "VECTO uses |v| <= 0.01 m/s on PreviousState (Vehicle.cs:262)"),
    ("consumption_engine 6", "atol=1e-3 (m)", "numerical tolerance", "", "driver sets S = waypoint exactly, so 0 would work; 1e-3 guards float drift"),
    ("consumption_engine 6", "pto_on_col == 1", "HDEV choice", "", "pto_engine accepts any > 0"),
    ("consumption_engine 6", "moving = V > 0", "HDEV choice (close to VECTO)", "Vehicle.cs:262 uses > 0.01 m/s", "0.01 m/s version is a one-line change; effect < 0.001 %"),
    ("consumption_engine 7", "/ 3.6e6", "unit definition", "", "W*s -> kWh"),
    ("consumption_engine 7", "DC/DC eff 1.0 (comment only)", "VECTO constant", "DeclarationData.cs:124", "not a parameter: aux is added 1:1"),
]
pd.DataFrame(hard, columns=["function", "number / rule", "class", "source", "note"]).to_csv(os.path.join(HERE, "partA_hardcoded_numbers.csv"), index=False)

# Q10: terms VECTO has that HDEV has no term for
from _rows import read_vmod  # noqa: E402
q10 = []
for cyc in ("RegionalDelivery", "UrbanDelivery", "LongHaul"):
    d = read_vmod(cyc, "ReferenceLoad")
    w = d["n_E2-em_avg [1/min]"].abs() * 2 * np.pi / 60
    e_batt = -d["P_REESS_T [kW]"].sum() / 3600.0
    for tech, T in (("shift claw/synchronizer (0.4 Nm)", 0.4), ("multi-disc clutch (2.8 Nm)", 2.8), ("multi-disc clutch + oil pump (23.9 Nm)", 23.9)):
        e = (T * w).sum() / 3.6e6
        q10.append(dict(term="PTO transmission torque loss on the EM-side shaft (PEVPtoTransm, only if a mechanical PTO type is declared)",
                        case=f"E2 {cyc} ReferenceLoad, PTO type {tech}", size_kWh=e, size_pct_of_battery_energy=e / e_batt * 100, size_kWh_per_km=e / (d["dist [m]"].iloc[-1] / 1000),
                        tag="[CALC] torque (PTO-tech.csv) x |n_E2-em_avg| from the .vmod; assumes the torque acts at EM speed (PEVPto sits between gearbox input and EM, PowertrainBuilder.cs 971-980); NEEDS the VECTO run in reference/vecto/jobs/aux-pto-2026-11 to confirm"))
for k, v in [("Padd_hv (cycle column PowerAdditonalHighVoltage)", "0 in all six E2 .vmod (P_aux_Padd_hv_el = 0) [TEST]; only used if the cycle carries a column"),
             ("ElectricAuxDemand (engineering 'P_aux_el' constant)", "0 in all six E2 .vmod (P_aux_P_aux_el_el = 0) [TEST]; engineering-mode user input"),
             ("DC/DC converter loss", "0: efficiency 1.0 (DeclarationData.cs:124); DCDCConverter.PowerDemand uses 1/eff for demand, eff for charging (DCDCConverter.cs 45)"),
             ("Aux power when the battery cannot supply it (P_DC/DC_missing)", "VECTO sets the aux power to 0 and records the missing energy (DCDCConverter.cs 59-68); HDEV has no limit [OPEN]"),
             ("Aux during engine-off / fan", "not applicable to a BEV (Fan excluded from the PEV aux set, HeavyLorryAuxiliaryDataAdapter.cs 270-275)"),
             ("Idle loss of the electric PTO", "none for EPTO (EPTO.cs returns the cycle value only)")]:
    q10.append(dict(term=k, case="", size_kWh=np.nan, size_pct_of_battery_energy=np.nan, size_kWh_per_km=np.nan, tag=v))
pd.DataFrame(q10).to_csv(os.path.join(HERE, "partA_q10_unmodelled_terms.csv"), index=False, float_format="%.4f")
print(df[["doc", "claim", "line_found", "line_cited_in_old_doc", "status"]].to_string(index=False))
print("\nfiles written:")
for f in ("partA_reverification_06_07_14.csv", "partA_hardcoded_numbers.csv", "partA_q10_unmodelled_terms.csv"):
    print("  ", os.path.relpath(os.path.join(HERE, f), REPO))
