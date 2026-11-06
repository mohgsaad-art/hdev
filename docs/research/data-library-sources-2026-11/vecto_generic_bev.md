# VECTO generic BEV / PEV values (section 4.2)

Source: the `mohgsaad-art/VECTO` repository, cloned fresh for this pass.
Licence: **EUPL-1.2** — confirmed in `LICENSE.txt` (line 1:
"EUROPEAN UNION PUBLIC LICENCE v. 1.2") and `publiccode.yml` (`license: EUPL-1.2`).
EUPL-1.2 is an OSI-approved copyleft licence; the generic data files below are
fine to read and reuse under its terms (attribution + share-alike on derivatives).

All values are `[V]` (I opened the file). File paths are relative to the VECTO
repo root. The generic vehicles are VECTO's own defaults, i.e. *simulated/standard*
values, not OEM or measured — tag them `basis = VECTO generic/standard`.

---

## 4.2a Generic BEV / PEV vehicles

### Engineering-mode generic BEV E2 (rigid truck)
Folder: `Generic Vehicles/Engineering Mode/GenericVehicleE2/`

Vehicle `BatteryElectricVehicle_PTO.vveh`:
- PowertrainConfiguration: BatteryElectric; VehCat RigidTruck
- CurbWeight 4670 kg; CurbWeightExtra 1900 kg; MassMax 11.99 t; Loading 3020 kg
- rdyn 421 mm; VehicleHeight 3.0 m; InitialSoC 80%
- PTO type: "only the drive shaft of the PTO - multi-disc clutch, oil pump";
  ePTO cycle `EPTO-idle.vptoel`

E-motor `GenericEMotor_125kW_485Nm.vem` (lines cited):
- Inertia 0.225 kg·m² (line 11); ThermalOverloadRecoveryFactor 0.9 (line 12)
- **ContinuousTorque 450 Nm @ 2460 rpm** (lines 17–18)
- **OverloadTorque 485 Nm @ 2460 rpm, OverloadTime 120 s** (lines 19–21)
- Two voltage levels (0 V and 1e9 V sentinel) carry the same curve → voltage-
  independent in the generic file
- DragCurve `GenericDrag_125kW_485Nm.vemd`; FullLoadCurve
  `GenericEMotor_125kW_485Nm.vemp` (peak torque 485 Nm at 0 rpm, falling with
  speed); EfficiencyMap `GenericMap_125kW_485Nm.vemo`
- Name implies ~125 kW rated / 485 Nm peak. Continuous ≈ 450 Nm × 2460 rpm ≈ 116 kW.
- Keeps continuous (450 Nm) and peak/overload (485 Nm, 120 s) on separate fields.

Battery `GenericBattery_243kWh_750V.vbat`:
- Capacity **324** (Ah; 324 Ah × ~750 V ≈ 243 kWh, matching the file name)
- SOC_min 10, SOC_max 90 (lines 13–14) → **SoC window 10–90%**
- InternalResistanceCurve `GenericBattery_243kWh.vbatr`: **Ri = 0.04 Ω, flat**
  over SoC 0→100
- SoCCurve `GenericBattery_243kWh.vbatv`: **OCV curve**, SoC→V:
  0%→673.5, 10→700.2, 20→715.4, 30→723.6, 40→727.7, 50→730.0, 60→731.6,
  70→733.8, 80→737.1, 90→742.2, 100→750.2 V (nominal ≈ 730 V at 50% SoC)
- MaxCurrentMap `MaxCurrent.vimax`: **I_charge = I_discharge = 1620 A**, flat

Gearbox `AMT.vgbx` (+ `Gear_1.vtlm`, `Gear_2.vtlm`): 2-gear AMT.
Axle `Axle_4x2_Tractor.vtlm`: 4x2.

ePTO cycle `EPTO-idle.vptoel` (electrical PTO power vs time):
- idle **8.42 kW**, active steps to **33.69 kW** (electrical, `P_PTO_el`)

### Engineering-mode generic BEV E4 (bus)
Folder: `Generic Vehicles/Engineering Mode/GenericVehicleE4/`
- Same 125 kW/485 Nm e-motor and 324 Ah / 750 V battery as E2.
- Vehicle `BatteryElectricVehicle.vveh`; bus accessory file `Bus.vacc`;
  cycles Interurban/Suburban.

### Declaration-mode PEV — IEPC generic
Folder: `Generic Vehicles/Declaration Mode/PEV/GenericIEPC/`
Variants: 1-speed and 3-speed gearboxes, ± integrated axle, ± wheel-motor.

`IEPC_Gbx1Speed/GenericIEPC_Gbx1.viepc`:
- ElectricMachineType **PSM**; Inertia 0.5 kg·m²; DifferentialIncluded false
- **Voltage-dependent torque** (VoltageLevels):
  - 500 V: ContinuousTorque **5412.6 Nm** @ 440.86 rpm; OverloadTorque
    **6450.02 Nm** @ 438.28 rpm; OverloadTime 312 s
  - 900 V: ContinuousTorque **5863.65 Nm** @ 445.16 rpm; OverloadTorque ~6765.75 Nm
  - (these are wheel-/output-side torques; IEPC includes the gear)
- Gears: Ratio 4.65 (1-speed variant)
- FullLoadCurves `IEPC_Gbx1_FLD_min/max.viepcp`; drag `IEPC_Gbx1_drag.viepcd`;
  PowerMaps `IEPC_Gbx1.viepco`

### Declaration-mode PEV — E2 generic
Folder: `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/`

Shared Declaration battery `.../GenericIEPC/Common/GenericBattery_243kWh_750V.vbat`:
- REESSType Battery; Capacity 324 Ah (line 12); SOC_min 10 / SOC_max 90
  (lines 13–14); **TestingTemperature 40 °C** (line 18);
  JunctionboxIncluded false; ConnectorsSubsystemsIncluded true

### Buses — generic IEPC efficiency maps
- `VectoCore/VectoCore/Resources/Declaration/GenericBusData/EfficiencyMap_IEPC_PSM_normalized.vmap`
  and `..._ASM_normalized.vmap`: normalized efficiency maps for PSM and ASM IEPC
  machines used to build bus standard values.

---

## 4.2b Reg. 2017/2400 Annex Xb standard values — where they live in the code

VECTO builds e-machine / IEPC standard values at runtime rather than from one flat
CSV. Key files (`[V]`):

- E-machine standard-value construction:
  `VectoCore/VectoCore/Models/GenericModelData/GenericBusElectricMotorData.cs`.
  Line 35–36: when `CertificationMethod == StandardValues`, it wraps the motor
  data in `StandardValuesInputData.StandardValuesEmInputData(...)` across a
  voltage range (1 V … 10e9 V). Lines 100–153 interpolate ContinuousTorque,
  ContinuousTorqueGen, ContinuousPower and losses between voltage levels, and
  derive peak vs continuous electrical power and the overload buffer
  (`overloadBuffer = (peakPwrLoss - continuousPowerLoss) * OverloadTime`).
- Declaration input providers for the three ZEV components:
  - e-machine: `.../XML/Declaration/DataProvider/XMLElectricMachinesDeclarationInputDataProvider.cs`
    and `XMLElectricMotorDeclarationInputDataProvider.cs`
  - REESS (battery/capacitor): `XMLElectricStorageSystemDeclarationInputData.cs`
- Manufacturer-report component writers (show the fields VECTO reports per ZEV):
  - `.../OutputData/XML/DeclarationReports/ManufacturerReport/.../Components/MRFElectricMachinesType.cs`
  - `.../Components/MRFREESSSpecificationsType.cs`
  - `.../VehicleInformationFile/.../PrimaryComponents/VIFElectricMotorTorqueLimitsType.cs`
- I did not find a single `AnnexXb.csv`; the standard values are generated in
  code from the declared component type + voltage, per the above classes. `[V]`

---

## 4.2c Resources/Declaration auxiliary tables — which apply to PEVs

All files under `VectoCore/VectoCore/Resources/Declaration/`. Values are the
VECTO declaration **standard** auxiliary demands (Watts unless noted). `[V]`

### Electric system — `VAUX/ES-Tech.csv`
Base electrical load, W, by mission (Long haul / Regional / Urban / Municipal / Construction):
- Standard technology: 1714.3 / 1428.6 / 1428.6 / 1428.6 / 1428.6
- Standard + LED headlights (all): 1642.9 / 1357.1 / 1357.1 / 1357.1 / 1357.1
Applies to all powertrains including PEV (it is the 24 V/base electrical demand).

### Steering pump — `VAUX/SP-Tech.csv` (which tech applies to PEV)
Columns include `PEV` and `fully electric` flags:
- Only "Electric driven pump" and "Full electric steering gear" have PEV = 1 and
  fully-electric = 1. All mechanical/engine-driven types are 0 for PEV.
- So for a BEV, steering is "electrically driven pump" or "full electric steering
  gear"; the mechanical SP technologies do not apply.
`VAUX/SP-Table.csv` gives the per-group mission demand triplets (e.g. group 5:
"600/120/0" long-haul = base/… split, W).

### Pneumatic system — `VAUX/PS-Table.csv` (electric-driven rows for PEV)
Columns `PEV` and `fully electric` are 1 only for the "... + elec. driven" rows.
The sheet adds dedicated electric-vehicle columns (`Long Haul_el`, `Regional
Delivery_el`, `Urban Delivery_el`, `Municipal utility_el`, `Construction_el`).
Examples (W, electric columns):
- "Large Supply + elec. driven": 1000 / 1000 / 875 / 875 / 1125
- "Large Supply + AMS + elec. driven": 900 / 900 / 788 / 788 / 1013
- "Vacuum pump + elec. driven": 237 / 200 / 162 / 162 / 162
These are the electric air-compressor demands for BEVs by mission.

### HVAC (lorries) — `VAUX/HVAC-Table.csv`
"None" = 0 for all groups; "Default" heating/cooling mech power by group/mission:
e.g. group 4: 350 (long-haul) / 200 / 150 / 300 (municipal) / 200 W. Group-
dependent; applies regardless of powertrain (it is the mechanical HVAC demand).

### Condenser (lorries) — `VAUX/Cond-Table.csv`
Lorry: 600 / 600 / 550 / 550 / 600 W by mission.

### PTO loss — `VAUX/PTO-tech.csv` (Power Loss W, Torque Loss Nm)
- None: 0 / 0
- "only the drive shaft of the PTO - multi-disc clutch, oil pump": **3000 W / 23.9 Nm**
  (this is the type the generic BEV E2 uses)
- "drive shaft and/or more than 2 gear wheels - multi-disc clutch, oil pump":
  3100 W / 24.7 Nm, etc. Full table has 12 technology rows.

### Buses — `Resources/Declaration/Buses/`
- `ElectricConsumers.csv`: per-consumer electrical loads (W) by duty
  (Heavy Urban / Urban / Suburban / Interurban / Coach), with Base/Default/Bonus
  flags and phase-idle factors. E.g. controllers & valves 25 W; radio 1–9 W;
  exterior lights (bulb) 7.4 W; LED bonuses negative. This is the bus base
  electrical demand used for all bus powertrains.
- `HVACHeatingPowerDriver.csv` / `HVACCoolingPowerDriver.csv`: driver-zone HVAC,
  **kW**, ~5 kW heating (configs 1–2) and up to 5 kW cooling.
- `HVACHeatingPowerPassenger.csv` / `HVACCoolingPowerPassenger.csv`: passenger-
  zone HVAC, **kW**, 0.25–0.55 kW per configuration/duty.

### Steering-pump bus factors — `Resources/Declaration/VAUXBus/`
`SP-Axles_Bus.csv`, `SP-AxleFactor.csv`, `SP-Factors_Bus.csv`, `Cond-Table.csv` —
bus-specific steering/condenser factors.

---

## What VECTO generic data CAN and CANNOT give EV Scope

CAN give (open, EUPL-1.2):
- Generic e-motor continuous vs peak torque/speed, overload time, inertia, drag,
  efficiency-map structure.
- Generic battery capacity (Ah), SoC window, OCV curve, flat Ri, max current.
- Standard auxiliary electrical demands for PEV (electric system, electric
  steering, electric air compressor, HVAC, condenser) by mission/group — in Watts.
- Standard PTO loss by PTO type (W and Nm).

CANNOT give:
- Real OEM battery kWh, chemistry, mass, warranty — these are per-vehicle inputs,
  not in the generic files.
- A single Annex Xb standard-value CSV — the values are generated in code.
