# VECTO reference files — add these yourself (read-only source of truth)

I could not copy the VECTO source into this bundle (the project copies only open as text, and many files are large). Get them from your VECTO download / code.europa.eu/vecto/vecto (stable branch). Keep file names unchanged. Kiro is told never to edit anything in `reference/`.

## `cs/` — C# source (BEV-relevant)
Already in your claude.ai project files (download or copy from there):
- Driver.cs, DefaultDriverStrategy.cs, DistanceBasedDrivingCycle.cs, DrivingCycleEnumerator.cs, MeasuredSpeedDrivingCycle.cs
- Vehicle.cs, Wheels.cs, WheelEnd.cs
- Battery.cs, BatteryElectricMotorController.cs, PWheelBatteryElectricMotorController.cs
- ElectricSystem.cs, ElectricSystemDrivingCycle.cs, ElectricAuxiliaries.cs, Conditioning.cs
- PTOCycleController.cs, BEVCycleGearbox.cs

Pasted in chats, not in project files — get from the VECTO repo:
- CrosswindCorrectionCdxALookup.cs, AirDrag.cs, VectoRunData.cs, DeclarationData.cs, Constants.cs
- HeavyLorryAuxiliaryDataAdapter.cs, AuxiliaryDataAdapter.cs
- `cs/declaration/`: HVAC.cs, PneumaticSystem.cs, SteeringPump.cs, ElectricSystem.cs (declaration lookup), Conditioning.cs (declaration lookup), AbstractAuxiliaryVehicleArchitectureLookup.cs
  (two of these share names with simulation-component files above — keep them in this subfolder)
- Still to check later: DrivingCycleData.cs (grade vs altitude), IMC-Tech.csv / DeltaAirDragAreaIMC

Skip ICE-only files: VTPCombustionEngine.cs, EngineAuxiliary.cs, EngineFanAuxiliary.cs, FuelCellSystem.cs, ShiftStrategyFactory.cs, Retarder.cs, RoadSweeperAuxiliary.cs, DummyGearboxInfo.cs.

## `resources/` — from `VectoCore/VectoCore/Resources/Declaration/`
- MissionCycles/: LongHaul, RegionalDelivery, UrbanDelivery, MunicipalUtility, Construction `.vdri`; MunicipalUtility_PTO_generic `.vptoc`, `.vptol`, `.vptoel`
- VACC/Truck.vacc
- SegmentTable.csv, Payloads.csv, Body_Trailers_Weights.csv, Wheels.csv
- VAUX/: HVAC-Table.csv, ES-Tech.csv, ES-Tech_Medium.csv, PS-Table.csv, SP-Table.csv, SP-Tech.csv, SP-Axles.csv, Cond-Table.csv, PTO-tech.csv
- VCDV_parameters.csv and Cdv_Generator_VECTO3.2.xlsx (crosswind)
