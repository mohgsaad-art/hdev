# HDEV session close-out: P_aux (BEV auxiliary power), traced through VECTO (8 Oct 2026)

Hand-over for a new chat. Every statement is tagged:

- **[VECTO]**: read directly from VECTO source code or a VECTO resource file pasted by Bob in this session (file named).
- **[REG]**: read from Regulation (EU) 2017/2400 (consolidated 01.01.2026) in the project knowledge base.
- **[ARITH]**: arithmetic done on VECTO values. The numbers are checkable; no interpretation.
- **[INFERRED]**: Claude's reading of why VECTO does something. Not stated in the code or documents.
- **[OPEN]**: not resolved.
- **[DECISION PENDING]**: Bob's call. **No HDEV design decisions were taken in this session.**

Scope: VECTO **Declaration Mode**, **heavy and medium lorries**, **battery-electric vehicle (PEV/BEV)**. Buses, conventional, hybrid and FCHV paths are only noted where they help explain the BEV path.

---

## 0. Summary

[VECTO] For a BEV lorry, VECTO's auxiliary power at each simulation step is:

```
P_aux(t) = P_ES + P_HVAC + P_PS + P_SP · [vehicle moving] + P_cond · [electric motor on]
```

- All five terms are **electric** power, drawn **directly from the traction battery (REESS)**. They are not routed through the motor, inverter or gearbox.
- DC/DC efficiency in Declaration Mode = **1.0** (no converter loss).
- **No engine cooling fan** for a BEV.
- All five values are **constants per vehicle × mission**. They only switch on and off by vehicle state (moving, motor on).
- **No ambient temperature dependence and no cabin-heating model** anywhere in the truck path read so far.

This resolves the open memory item "P_aux = 0.0 pending DC/DC efficiency research" **for VECTO-auditable mode**: VECTO uses DCDCEfficiency = 1.0 [VECTO]. Whether HDEV adds a non-VECTO DC/DC loss later is a [DECISION PENDING].

---

## 1. Source files read this session (all VECTO Sim repo, code.europa.eu, pasted by Bob unless noted)

| File | Path (as given / as shown in repo) | Used for |
|---|---|---|
| `ElectricSystem.cs` | in project files | battery request equation, aux subtraction |
| `ElectricAuxiliaries.cs` | in project files | which aux run when (standstill / ICE-off filters) |
| `Conditioning.cs` (simulation component) | in project files; namespace `Models.SimulationComponent.Impl.Auxiliaries` | conditioning on/off rule |
| `VectoRunData.cs` | `VectoCore/VectoCore/Models/Simulation/Data/` | `AuxData` class, DCDC default |
| `DeclarationData.cs` | `VectoCore/VectoCore/Models/Declaration/` | efficiency constants |
| `HeavyLorryAuxiliaryDataAdapter.cs` | `VectoCore/VectoCore/InputData/Reader/DataObjectAdapter/SimulationComponents/AuxiliaryDataAdapter/` | how each aux becomes electric power for BEV |
| `AuxiliaryDataAdapter.cs` | same folder | `CreateConditioningAux` |
| `HVAC.cs` (`HeatingVentilationAirConditioning`) | `VectoCore/VectoCore/Models/Declaration/` | HVAC lookup |
| `ElectricSystem.cs` (declaration lookup) | `VectoCore/VectoCore/Models/Declaration/Auxiliaries/` | ES lookup |
| `PneumaticSystem.cs` | `.../Models/Declaration/Auxiliaries/` | PS lookup, electric columns |
| `AbstractAuxiliaryVehicleArchitectureLookup.cs` | `.../Models/Declaration/Auxiliaries/` | applicability per vehicle architecture |
| `SteeringPump.cs` | `.../Models/Declaration/Auxiliaries/` | steering pump calculation |
| `Conditioning.cs` (declaration lookup) | `.../Models/Declaration/Auxiliaries/` | conditioning lookup |
| `Constants.cs` | `VectoCore/VectoCore/Configuration/` | aux IDs |
| `AuxSupplyPowerReader.cs` | `.../Models/SimulationComponent/Data/` | `Aux_` columns in cycle files |
| `LorryAuxDataAdapterTests.cs` | `Testing/UnitTests/.../DataAdapter/Declaration/Components/` | expected behaviour, cross-check |
| CSVs in `VectoCore/VectoCore/Resources/Declaration/VAUX/` | `HVAC-Table.csv`, `ES-Tech.csv`, `ES-Tech_Medium.csv`, `PS-Table.csv`, `SP-Table.csv`, `SP-Tech.csv`, `SP-Axles.csv`, `Cond-Table.csv`, `PTO-tech.csv` | all values |

Read but **not relevant to BEV lorries** (do not use for HDEV trucks):
- `BusAuxDemandESSAlternatorTypeTests.cs`: bus auxiliaries. Its `DCDCEfficiency = 0.97` is a **test constant**, not the declaration value.
- SSM HVAC model screenshots: bus Steady-State Model (temperature, solar, heat pumps).
- A completed-bus XML declaration example.
- VECTO documentation 2014 (LOT3) Tables 7–12 / 47–52: conventional diesel, mechanical power. **Superseded by the repo CSVs**, and values differ (e.g. ES 1240 W in the doc vs. 1714.2857/0.7-based values in the CSV).

---

## 2. Runtime: how aux power hits the battery [VECTO]

### 2.1 `ElectricSystem.cs`, `Request()`
```
totalPowerDemand = powerDemand + chargePower + fcPower − auxDemand − connectorLoss
auxDemand        = Σ consumers.PowerDemand(absTime, dt, dryRun)
connectorLoss    = I_est² · ConnectionSystemResistance,  I_est = (powerDemand + fcPower) / Battery.InternalVoltage
```
- Aux power is subtracted at battery level (sign convention: propelling demand is negative). It is logged as `P_Aux_el_HV`.
- No DC/DC efficiency is applied in this file.

### 2.2 `ElectricAuxiliaries.cs` (class comment: "Auxiliaries which are connected to the DCDC system")
- Constant aux return `aux.PowerDemandElectric`. Dynamic aux return `PowerDemandDataBusFunc(dataBus, false)` or an `IAuxDemand.PowerDemand`.
- **Steering pump (ID `"STP"`) is excluded when `VehicleInfo.VehicleStopped`.**
- Fan (ID `"FAN"`) is excluded when `EngineInfo != null && !EngineOn`. Not relevant: a BEV has no fan entry (see 3.1).
- Engineering-mode IDs (`ENG_AUX_BASE`, `ENG_AUX_FAN`, `ENG_AUX_STP`) are ignored.
- The sum is logged as `P_aux_el`.

### 2.3 `Constants.cs`, `Auxiliaries.IDs`
```
Fan = "FAN";  SteeringPump = "STP";  SteeringPump_el = "STP";  ElectricSystem = "ES";
HeatingVentilationAirCondition = "AC";  PneumaticSystem = "PS";  Cond = "COND";
PTOTransmission = "PTO_TRANSM";  PTOConsumer = "PTO_CONSUM";
```
- **`SteeringPump_el` has the same string as `SteeringPump`**, so the standstill filter in 2.2 also removes the BEV's electric steering pump. Verified from `Constants.cs`.
- This is consistent with `LorryAuxDataAdapterTests.cs`, which finds the BEV electric pump by `ID == SteeringPump`.

### 2.4 `Conditioning.cs` (simulation component), BEV branch
```
GetPEV_SHEV_PowerDemand: if any electric motor has !EmOffPrev, or EPTO is on → PowerDemandElectric, else 0
```
- Applies to `BatteryElectricVehicle`, `IEPC_E`, `SerialHybridVehicle`, `IEPC_S`, `Multiple_PEV`, `Multiple_SHEV`.
- [OPEN] When a BEV motor counts as "off" (`EmOffPrev`) is not traced: standstill? coasting? Parked for the driver-model audit.

### 2.5 Other
- `VectoRunData` has a field `ElectricAuxDemand` (Watt). [OPEN] Its use was not traced.
- `AuxSupplyPowerReader.cs`: cycle files may carry columns prefixed `AUX_` (values in **kW**, converted to W). This lets a drive cycle carry per-row aux power. It is a cycle-input feature, not the declaration tables.

---

## 3. Data adapter: which aux exist for a BEV, and how each becomes electric power [VECTO]

### 3.1 Which components
`HeavyLorryPEVAuxiliaryDataAdapter` (inherits `HeavyLorryAuxiliaryDataAdapter`) overrides the required set to **exactly four**:
`ElectricSystem, HVAC, PneumaticSystem, SteeringPump`. **No Fan.**

- Declaring any other set throws: "In Declaration Mode exactly 4 Auxiliaries must be defined for battery electric vehicles".
- The unit test `PEV PneumaticSystemTest Fail 1` confirms that adding a fan technology for a PEV fails.
- `HeavyLorryFCHVAuxiliaryDataAdapter` inherits the same set.

**Conditioning** is added on top: `AuxiliaryDataAdapter.CreateConditioningAux(jobType)` returns `false` **only** for `ConventionalVehicle`, and `true` for all other types, including BEV.

So for a BEV lorry: **4 declared aux + Conditioning = 5 terms.**

### 3.2 EMS missions
[VECTO] Inside the loop, `mission = mission.GetNonEMSMissionType();`. EMS missions (e.g. LongHaulEMS) use the non-EMS aux tables.

### 3.3 Constants used (`DeclarationData.cs`)
| Constant | Value | Used by |
|---|---|---|
| `AlternatorEfficiency` | 0.7 | ES, SP (and Fan, PS for non-electric) |
| `HVACElectricEfficiencyFactor` | 0.8 | HVAC, passed as `1/0.8` |
| `DCDCEfficiency` | 1.0 | `VectoRunData` constructor → `DCDCData` |

### 3.4 Per component (code excerpts paraphrased exactly)

**Electric system** (`AddElectricSystem`)
```
PowerDemandMech     = ElectricSystem.Lookup(hdvClass, mission, technology).PowerDemand
PowerDemandElectric = PowerDemandMech × AlternatorEfficiency (0.7)
ConnectToREESS      = true for BEV (and SHEV, IEPC, FCHV, Multiple_*; or batteryOnlyHybridMode)
DemandType          = Constant
```

**HVAC** (`AddHVAC`, called with `efficiency = 1/HVACElectricEfficiencyFactor`)
```
PowerDemandMech     = HeatingVentilationAirConditioning.Lookup(mission, technology, hdvClass).PowerDemand
PowerDemandElectric = PowerDemandMech × (1/0.8) = PowerDemandMech × 1.25
ConnectToREESS      = true for BEV
DemandType          = Constant
```

**Pneumatic system** (`AddPneumaticSystem`)
```
if !PneumaticSystem.IsApplicable(jobType, technology) → throw
PowerDemandMech  = PneumaticSystem.Lookup(mission, technology).PowerDemand        (mechanical columns)
IsFullyElectric  = PneumaticSystem.IsFullyElectric(technology)
if IsFullyElectric: PowerDemandElectric = PneumaticSystem.GetElectricPowerDemand(mission, technology)   (_el columns)
else:               PowerDemandElectric = PowerDemandMech × 0.7
ConnectToREESS   = IsFullyElectric && (BEV or other electric architectures)
```
For a BEV only fully-electric technologies are applicable (see 4.3), so the `_el` columns are always the source. They are **not** computed from mechanical values.

**Steering pump** (`AddSteeringPumps`)
```
if !SteeringPump.IsApplicable(technologies, jobType) → throw
if numSteeredAxles given && technologies.Count != numSteeredAxles → throw
(mechanicalPumps, electricPumps) = SteeringPump.Lookup(mission, hdvClass, technologies)
spMech:     ID "STP", PowerDemandMech = mechanicalPumps, IsFullyElectric = false     → added only if > 0
spElectric: ID "STP" (SteeringPump_el), IsFullyElectric = true, ConnectToREESS = true,
            PowerDemandElectric = electricPumps × 0.7, PowerDemandMech = electricPumps  → added if electricPumps > 0 (non-conventional)
```
For a BEV both allowed technologies are fully electric, so `mechanicalPumps = 0` and only `spElectric` exists.

**Conditioning** (`AddConditioning`)
```
ID "COND", IsFullyElectric = true, ConnectToREESS = true, DemandType = Dynamic,
PowerDemandElectric = Conditioning.LookupPowerDemand(hdvClass, jobType, mission)
```

---

## 4. Lookups and tables [VECTO unless tagged]

### 4.1 Electric system (`Declaration/Auxiliaries/ElectricSystem.cs`)
- Key: **mission × technology**. No vehicle-group dependency within heavy lorries.
- `vehicleClass.IsMediumLorry()` → `ES-Tech_Medium.csv`, otherwise `ES-Tech.csv`.
- Blank technology → `"Standard technology"`.
- Cells `"---"` are skipped, so looking them up gives a lookup error.

`ES-Tech.csv` (heavy lorries), table value [W]:
| Technology | LH | RD | UD | MU | Constr |
|---|---|---|---|---|---|
| Standard technology | 1714.2857 | 1428.5714 | 1428.5714 | 1428.5714 | 1428.5714 |
| Standard technology - LED headlights, all | 1642.8571 | 1357.1429 | 1357.1429 | 1357.1429 | 1357.1429 |

`ES-Tech_Medium.csv` (medium lorries), table value [W]:
| Technology | LH | RD | UD | MU | Constr |
|---|---|---|---|---|---|
| Standard technology | 1028.571429 | 857.1428571 | 857.1428571 | --- | --- |
| Standard technology - LED headlights, all | 942.8571428 | 785.7142857 | 785.7142857 | --- | --- |

[ARITH] Electric power for BEV = table × 0.7:
| | LH | RD / UD / MU / Constr |
|---|---|---|
| Heavy, standard | **1200 W** | **1000 W** |
| Heavy, LED headlights | **1150 W** | **950 W** |
| Medium, standard | **720 W** | **600 W** (RD, UD only) |
| Medium, LED headlights | **660 W** | **550 W** (RD, UD only) |

[INFERRED] The table stores electric demand ÷ 0.7 (alternator shaft power), and ×0.7 gives back the electric demand. The round results support this, but the intent is not stated in the code.

### 4.2 HVAC (`Declaration/HVAC.cs`, `HVAC-Table.csv`)
- Key: **mission × technology × vehicle group**. Constant W.
- Blank cells are not stored (parsed as NaN and skipped), so looking them up gives a lookup error.
- Technologies: `None`, `Default`. [REG] Annex IX Table 12 (P185) allows exactly these two for medium and heavy lorries.

`HVAC-Table.csv`, technology **Default**, table value [W] (`None` = 0 for all listed groups and missions):
| Group | LH | RD | UD | MU | Constr |
|---|---|---|---|---|---|
| 1s, 1 | 200 | 150 | 150 | – | – |
| 2, 3 | 200 | 200 | 150 | – | – |
| 4 | 350 | 200 | 150 | 300 | 200 |
| 5 | 350 | 200 | 150 | **0** | 200 |
| 9 | 350 | 200 | 150 | 300 | 200 |
| 10 | 350 | 200 | 150 | **0** | 200 |
| 11 | 350 | 200 | 150 | 300 | 200 |
| 12, 16 | 350 | 200 | 150 | – | 200 |
| 51–56 | 200 | 150 | 150 | – | – |

- "–" = blank → lookup error. Groups 6, 7, 8 are not in the table at all.
- Groups 5 and 10 Municipal utility hold an explicit **0**, not a blank. [OPEN] Why is not known.

[ARITH] BEV electric = table × 1.25: 150 → 187.5 W; 200 → 250 W; 300 → 375 W; 350 → 437.5 W.

[INFERRED] The table is mechanical A/C compressor power; an electric compressor drive at 0.8 efficiency needs table ÷ 0.8 as electric input. Not stated in the code.

[INFERRED, from 2014 VECTO doc §4.2.6.5] The truck HVAC value is A/C compressor demand only (ventilation is counted in the electric system). **No heating component.** [REG] for lorries offers only None/Default, with no heating technology parameters (the heat-pump/heater parameters P318–P330 are bus-only).

### 4.3 Pneumatic system (`Declaration/Auxiliaries/PneumaticSystem.cs`, `PS-Table.csv`)
CSV layout: `Technology`, then 4 applicability columns (`conventional, P-HEV, S-HEV, PEV`), then `fully electric`, then 5 mechanical mission columns, then 5 `_el` mission columns.

- Applicability (`AbstractAuxiliaryVehicleArchitectureLookup`): reads columns 2–5. Mapping: `BatteryElectricVehicle → "pev"` (also `IEPC_E`, `FCHV`, `FCHV_IEPC`, `Multiple_PEV`, `Multiple_FCHV` → `"pev"`). Unknown technology → throw.
- **Only the 9 "+ elec. driven" rows have PEV = 1 and fully electric = 1.** All mechanical technologies are not applicable for a BEV, and VECTO throws.
- Electric lookup key: **mission × technology**. No vehicle-group dependency.
- [REG] Annex III Table 3 (P184): "For PEV or FCHV only 'elec. driven' technologies are allowed values." Consistent.

BEV electric power, `_el` columns [W]:
| Technology | LH | RD | UD | MU | Constr |
|---|---|---|---|---|---|
| Small + elec. driven | 750 | 750 | 813 | 813 | 750 |
| Small + AMS + elec. driven | 675 | 675 | 732 | 732 | 675 |
| Medium Supply 1-stage + elec. driven | 750 | 687 | 687 | 687 | 750 |
| Medium Supply 1-stage + AMS + elec. driven | 675 | 618 | 618 | 618 | 675 |
| Medium Supply 2-stage + elec. driven | 875 | 813 | 750 | 750 | 1000 |
| Medium Supply 2-stage + AMS + elec. driven | 788 | 732 | 675 | 675 | 900 |
| Large Supply + elec. driven | 1000 | 1000 | 875 | 875 | 1125 |
| Large Supply + AMS + elec. driven | 900 | 900 | 788 | 788 | 1013 |
| Vacuum pump + elec. driven | 237 | 200 | 162 | 162 | 162 |

- [ARITH] For non-AMS electric rows, `_el ≈ mech × 0.70`. For **AMS rows it does not hold**.
- Unit test `PEV PneumaticSystemTest Pass 1` expects 675 W for "Small + AMS + elec. driven", LH, BEV. Consistent.
- **Rule for HDEV: read `_el` directly, never derive it.**

[REG] Definitions (Annex IX point 2): ESS (19), AMS (22), size of air supply (§3.4.1.1, Table 8: Small ≤ 250 cm³; Medium 250–500 cm³ 1-/2-stage; Large > 500 cm³), fuel-saving combinations (Table 9: for electrically driven compressors only combination 8 (none) and 9 (+AMS)), vacuum (§3.4.2).

### 4.4 Steering pump (`Declaration/Auxiliaries/SteeringPump.cs`)

`SP-Table.csv`: baseline per group × mission, format `UF/B/S` (UnloadedFriction / Banking / Steering).
| Group | LH | RD | UD | MU | Constr |
|---|---|---|---|---|---|
| 1s, 1 | 290/25/0 | 240/20/20 | 220/20/30 | – | – |
| 2 | 340/30/0 | 290/30/20 | 260/20/30 | – | – |
| 3 | 420/60/0 | 310/30/30 | 280/30/40 | – | – |
| 4 | 510/100/0 | 490/40/40 | 430/40/50 | 430/30/50 | 580/30/70 |
| 5 | 600/120/0 | 540/90/40 | 480/80/60 | 480/80/60 | 640/50/80 |
| 6, 7, 8 | – | – | – | – | – |
| 9 | 600/120/0 | 490/60/40 | 440/50/50 | 430/30/50 | 640/50/80 |
| 10 | 450/120/0 | 440/90/40 | 390/80/50 | 430/30/50 | 640/50/80 |
| 11 | 600/120/0 | 490/60/40 | 370/60/50 | 430/30/50 | 640/50/80 |
| 12 | 450/120/0 | 440/90/40 | 390/80/50 | – | 640/50/80 |
| 16 | 490/100/0 | 550/90/40 | 490/80/60 | – | 640/50/80 |
| 51–56 | 255/20/0 | 200/20/20 | 180/20/30 | – | – |

`SP-Axles.csv` (percent, `UF/B/S`, same for all missions): axle 1 100/100/100; 2 100/70/70; 3 100/50/50; 4 100/50/50.

`SP-Tech.csv` (factors UF/B/S): Fixed displacement 1/1/1; Fixed displacement with elec. control 0.95/1/1; Dual displacement 0.85/0.85/0.85; Dual displacement with elec. control 0.80/0.85/0.85; Variable displacement mech. controlled 0.75/0.75/0.75; Variable displacement elec. controlled 0.6/0.6/0.6; **Electric driven pump (PEV allowed) 0.857/0.857/0.857**; **Full electric steering gear (PEV allowed) 0/0.143/1.429**.
- [REG] Annex III Table 3 (P182): for PEV, FCHV or S-HEV only "Electric driven pump" or "Full electric steering gear" are allowed. One entry per steered axle.

**Calculation** (`SteeringPump.Lookup`). For each steered axle *i* (1…n) with technology *tᵢ*, and k ∈ {UF, B, S}:
```
part_k(i)  = SP-Table(mission, group)_k / 100 × SP-Axles(mission, i)_k        [W]
bucket     = electric if tᵢ fully electric, else mechanical
bucket_k  += part_k(i)
avg_k      = Σᵢ SP-Tech(tᵢ)_k / n                                              (average over ALL axles, both buckets)
bucket_k  *= avg_k                    (only if the bucket has ≥1 axle)
return (Σ_k mech_k, Σ_k el_k)
```
The adapter then sets `PowerDemandElectric = electricPumps × 0.7`.

[ARITH] Effective electric factors: Electric driven pump 0.6/0.6/0.6; Full electric steering gear 0/0.1/1.0.
[ARITH] Worked examples, 1 steered axle (**illustrative only, technologies chosen by Claude**): Group 5 RD Electric driven pump → 401.9 W; Group 5 LH Electric driven pump → 431.9 W; Group 5 RD Full electric steering gear → 49.0 W.

Runtime: **0 W while the vehicle is stopped** (sections 2.2 and 2.3).

### 4.5 Conditioning (`Declaration/Auxiliaries/Conditioning.cs`, `Cond-Table.csv`)
- Lorry, non-FCHV: `VAUX/Cond-Table.csv`. Key: **mission only**. Value already electric.

| Category | LH | RD | UD | MU | Constr |
|---|---|---|---|---|---|
| Lorry | 600 | 600 | 550 | 550 | 600 |

Runtime: on only while an electric motor is on, or an electric PTO is on (section 2.4).
[OPEN] What "conditioning" physically covers (battery/e-motor thermal conditioning) is not stated in the code read.

---

## 5. Illustrative total (not a default; technologies chosen by Claude for arithmetic only)

Group 5, Regional Delivery, BEV: standard ES, Default HVAC, "Medium Supply 1-stage + elec. driven", 1 axle with "Electric driven pump".

| State | ES | HVAC | PS | SP | Cond | Total |
|---|---|---|---|---|---|---|
| Moving, motor on | 1000 | 250 | 687 | 401.9 | 600 | **2938.9 W** |
| Stopped, motor on | 1000 | 250 | 687 | 0 | 600 | 2537 W |
| Stopped, motor off | 1000 | 250 | 687 | 0 | 0 | **1937 W** |

---

## 6. Validation / error behaviour in VECTO worth mirroring or deciding on [VECTO]

- BEV must declare exactly ES, HVAC, PS, SP. A fan is not allowed.
- Steering: number of technologies must equal the number of steered axles. Each technology must be applicable to the architecture.
- Pneumatic: technology must be applicable to the architecture (BEV → elec. driven only).
- Blank or "---" table cells → lookup error (ES medium lorries MU/Constr; several HVAC and SP cells; groups 6, 7, 8 entirely).

---

## 7. What VECTO does NOT provide for BEV lorry auxiliaries (gaps)

- **No cabin heating.** HVAC is one constant per group × mission, with no ambient temperature input. Danish winter operation is therefore not represented by VECTO declaration values.
- **No temperature or solar dependence** for trucks. That exists only in the bus SSM model.
- **No DC/DC loss** (efficiency fixed at 1.0).
- **No aux during depot charging.** [OPEN] For the charging engine.

---

## 8. PTO (touched only)

- `PTO-tech.csv`: mechanical PTO transmission losses by PTO technology. [OPEN] Applicability to BEV not checked.
- Default files `MunicipalUtility_PTO_generic.vptol / .vptoc / .vptoel` (the `.vptoel` is the electric PTO activation cycle).

---

## 9. Open items (consolidated)

1. [OPEN] `EmOffPrev` for BEV — when is the motor "off".
2. [OPEN] Aux during depot charging.
3. [OPEN] Cabin heating source for Danish conditions (needs authentic non-VECTO source, flagged non-VECTO).
4. [OPEN] `VectoRunData.ElectricAuxDemand` use.
5. [OPEN] HVAC group 5/10 MU = 0; AMS `_el` values.
6. [OPEN] Electric PTO (`.vptoel`) for refuse BEVs.

## 10. Decisions pending (Bob)

- HDEV default technologies for a BEV (user input vs flagged HDEV default).
- Blank-cell handling: mirror VECTO (error) or allow user-entered values (labelled non-VECTO).
- Structure of the P_aux function (Claude suggestion only: precompute constant part per vehicle × mission, apply SP and Cond via per-row flags `moving`, `motor_on`).
- Whether HDEV adds non-VECTO extras (DC/DC loss, heating, charging-time aux) as optional flagged layers with neutral defaults.
- Later chat (8 Oct): Bob wants P_aux vehicle-agnostic and pure physics; considered reusing VECTO's bus SSM heat-balance physics per row with DMI temperature/solar data. Two sub-decisions open: how to map VECTO's 11 climate points to continuous temperature; how to handle a heat-pump COP gap at −20 °C.
