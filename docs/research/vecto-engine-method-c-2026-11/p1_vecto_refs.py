"""File + line in the VECTO fork (mohgsaad-art/VECTO, IEPC-experiments, b8d6126) for every VECTO rule used by the job files. Lines are found by reading the file."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.environ.get("VECTO_SRC", os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "VECTO")))
CORE = os.path.join(V, "VectoCore", "VectoCore")
DEC = os.path.join(CORE, "Resources", "Declaration")
ATTR = ("# Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 "
        "(https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA.")


def line(path, needle, nth=1):
    k = 0
    for i, ln in enumerate(open(path, encoding="latin-1"), 1):
        if needle in ln:
            k += 1
            if k == nth:
                return i, " ".join(ln.split())[:150]
    raise SystemExit("not found: %s in %s" % (needle, path))


ITEMS = [
    ("loss map: points are stored at (input speed, input torque - torque loss) -> constant loss torque is a constant column", os.path.join(CORE, "Models/SimulationComponent/Data/Gearbox/TransmissionLossMap.cs"), "AddPoint(entry.InputSpeed.Value()", "F0 as axle loss: constant Torque Loss column"),
    ("loss map: loss is read at (out speed x ratio, out torque / ratio) and is a torque at the input side", os.path.join(CORE, "Models/SimulationComponent/Data/Gearbox/TransmissionLossMap.cs"), "var torqueLoss = _lossMap.Interpolate(", "axle ratio 1.0, so input side = wheel side: T0 = F0 x r_dyn"),
    ("loss map: Torque Loss must be between 0 and 1,000,000 Nm", os.path.join(CORE, "Models/SimulationComponent/Data/Gearbox/TransmissionLossMap.cs"), "SIRange(0, 1000000)]", "F0 = 0 gives loss 0, allowed"),
    ("IEPC power map reader: lowest speed entries are copied to 0 rpm by clustering the lowest two speeds", os.path.join(CORE, "InputData/Reader/ComponentData/IEPCMapReader.cs"), "var speeds = new MeanShiftClustering()", "map speed grid starts 0, 3.37, 33.7 rpm like the VECTO generic IEPC"),
    ("IEPC power map reader: map is triangulated on (-torque, speed) with the electric power as value", os.path.join(CORE, "InputData/Reader/ComponentData/IEPCMapReader.cs"), "delaunayMap.AddPoint(-entry.Torque.Value() * count,", "interpolation is linear between grid points"),
    ("IEPC power map reader: map is extended to 1.2 x the full-load torque by scaling", os.path.join(CORE, "InputData/Reader/ComponentData/IEPCMapReader.cs"), "var extrapolationfactor", "map covers +-T_cap"),
    ("standard-values IEPC gets two fake voltage levels (1 V, 10e9 V)", os.path.join(CORE, "InputData/Reader/DataObjectAdapter/SimulationComponents/ElectricMachinesDataAdapter.cs"), "Fake one very low voltage level", "our IEPC uses 100 V and 2000 V levels with the same map"),
    ("electric energy of the declaration result = (-integral P_reess_int) / charging efficiency", os.path.join(CORE, "OutputData/ModDataPostprocessing/Impl/BatteryElectricPostprocessingCorrection.cs"), "ElectricEnergyConsumption_Final =", "EC_el_final includes the battery internal loss"),
    ("result written to the declaration report = ElectricEnergyConsumption_Final", os.path.join(CORE, "OutputData/XML/XMLDeclarationReport.cs"), "ElectricEnergyConsumption = data.CorrectedModalData.ElectricEnergyConsumption_Final", "EEA field is most likely this one; not verified in the EEA file"),
    ("charging efficiency of the battery (depot charging)", os.path.join(CORE, "Models/Declaration/DeclarationData.cs"), "public static double CalculateChargingEfficiencyPEV", "depends on the real battery"),
    ("segment group 5 tractor 4x2, vocational 0", os.path.join(DEC, "SegmentTable.csv"), "5         , 0          , 1     , Tractor", "payloads, trailers, axle shares, CdxA default"),
    ("segment group 1 rigid 4x2 (7.5-10 t)", os.path.join(DEC, "SegmentTable.csv"), "1         , 0          , 1     , RigidTruck", "body B1, payload pc10/pc50"),
    ("payload of group 1: 10 % and 50 % payload by gross vehicle weight (7,500 t row)", os.path.join(DEC, "Payloads.csv"), "7500                 , 250", "333 kg and 1,664 kg for 8,550 kg by linear interpolation to the 16,000 row"),
    ("payload of group 1 (16,000 row)", os.path.join(DEC, "Payloads.csv"), "16000                , 920", "interpolation partner"),
    ("body B1 curb mass 1,600 kg", os.path.join(DEC, "Body_Trailers_Weights.csv"), "B1     , 1600", "total mass of the eCanter = CurbWeight + 1,600 + payload"),
    ("semitrailer ST1 7,500 kg, delta CdxA 0 / 2.1", os.path.join(DEC, "Body_Trailers_Weights.csv"), "ST1    , 7500", "total mass of the S-eWay"),
    ("wheel data 315/70 R22.5 (r_dyn, inertia)", os.path.join(DEC, "Wheels.csv"), "315/70 R22.5 , 312.00", "inertia 14.9 kgm2"),
    ("wheel data 385/55 R22.5", os.path.join(DEC, "Wheels.csv"), "385/55 R22.5 , 386.00", "inertia 15.9 kgm2"),
    ("wheel data 225/70 R19.5", os.path.join(DEC, "Wheels.csv"), "225/70 R19.5", "inertia 6.4 kgm2"),
    ("declared CdxA replaced by the default on the construction mission", os.path.join(CORE, "InputData/Reader/DataObjectAdapter/SimulationComponents/AirdragDataAdapter.cs"), "mission.MissionType == MissionType.Construction", "same rule in the harness"),
    ("PEV auxiliaries: ES standard technology", os.path.join(DEC, "VAUX/ES-Tech.csv"), "Standard technology", "same as harness aux_per_label.csv"),
    ("steering pump technology 'Full electric steering gear' factor", os.path.join(DEC, "VAUX/SP-Tech.csv"), "Full electric steering gear", "gives 32 W in the vmod (UF 0 but base share), the harness uses 0 W"),
    ("alternator efficiency 0.7", os.path.join(CORE, "Models/Declaration/DeclarationData.cs"), "AlternatorEfficiency = 0.7", "aux conversion"),
    ("distance-based runs use a target time interval of 0.5 s (vmod column dt)", os.path.join(CORE, "Configuration/Constants.cs"), "TargetTimeInterval = 0.5", "step size is a VECTO engine feature (HDEV uses 1 s)"),
]


def main():
    rows = []
    for what, path, needle, note in ITEMS:
        try:
            i, txt = line(path, needle)
        except SystemExit as e:
            rows.append(dict(rule=what, file=os.path.relpath(path, V), line="NOT FOUND", text=needle, use_in_this_study=note)); continue
        rows.append(dict(rule=what, file=os.path.relpath(path, V), line=i, text=txt, use_in_this_study=note))
    with open(os.path.join(HERE, "p1_vecto_refs.csv"), "w", newline="") as fh:
        fh.write(ATTR + "\n")
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows:
        print(r["line"], r["file"][-70:], "|", r["rule"][:70])


if __name__ == "__main__":
    main()
