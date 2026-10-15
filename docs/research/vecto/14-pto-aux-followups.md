# 14 — PTO & auxiliaries follow-ups for BEV lorries

VECTO source: full clone `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Paths are relative to that clone unless noted. Tags: **[VECTO]** read from source, **[INFERRED]** interpretation, **[NOT FOUND]** does not exist, **[ARITH]** arithmetic on read values. Nothing invented; owner referred to as **Bob**.

> Builds on `07-pto-all.md` and `06-auxiliaries-all.md`. **What of `07` I confirmed vs corrected is stated per bullet.** Short version: `07` is correct on file formats, `P_PTO_el` = kW, EPTO as an aux consumer, and Cond staying on with EPTO. It is **incomplete** on (a) the exact `PTOActive` gating (there are **4** PTO-activity states, not just stop-based), (b) that a **PTO-while-driving** path exists (RoadSweeper), and (c) the exact stop-duration = `StoppingTime + PTO cycle Duration` rule. Those are detailed below.

---

## PART A — PTO

### A1. PTO file types, columns, units  [VECTO]
- **`.vptol`** — PTO **idle loss map** (mechanical). 2 columns `Engine speed [rpm], PTO Torque [Nm]`. Reader `InputData/Reader/ComponentData/PTOIdleLossMapReader.cs:60-85`:
  ```csharp
  if (data.Columns.Count != 2) throw ...;            // exactly 2 cols
  EngineSpeed = row.ParseDouble("Engine speed").RPMtoRad(),
  PTOTorque   = row.ParseDouble("PTO Torque").SI<NewtonMeter>()
  ```
  Field names `Fields.EngineSpeed = "Engine speed"` [rpm], `Fields.PTOTorque = "PTO Torque"` [Nm] (`PTOIdleLossMapReader.cs:88-97`). Confirms `07` (which labelled it rpm/Nm). ✅
- **`.vptoc`** — PTO **(mechanical) activation cycle**. Columns `<t> [s], <Engine speed> [rpm], <PTO Torque> [Nm]`. Parser `DrivingCycleDataReader.cs:869-895` (`PTOCycleDataParser`): `Time`, `AngularVelocity = EngineSpeedFull.RPMtoRad()`, `Torque = PTOTorque.SI<NewtonMeter>()`. **Corrects `07`**, which left `.vptoc` columns as "cycle rows" — they are **t / engine speed / PTO torque**.
- **`.vptoel`** — PTO **electric** activation cycle (BEV). Columns `<t> [s], <P_PTO_el> [kW]`. Parser `DrivingCycleDataReader.cs:837-845` (`EPTOCycleDataParser`): `PTOElectricalPowerDemand = (ParseDouble("P_PTO_el") * 1000).SI<Watt>()` — i.e. **input column is kW**, stored W. Confirms `07`. ✅
- **`PTO-tech.csv`** — mechanical PTO transmission/idle losses per PTO technology. Columns `Technology, Power Loss [W], Torque Loss [Nm]` (`Resources/Declaration/VAUX/PTO-tech.csv`). Full table in `07` §3; values 0–3100 W / 0–24.7 Nm. ✅
- **`PTO_Power` column** inside a drive cycle — a 4th PTO input, for **PTO during driving** (not a separate file): `Fields.PTODuringDrivePower = "PTO_Power"` [kW] (`DrivingCycleDataReader.cs:370`), parsed `PTOPowerDemandDuringDrive = ParseDouble("PTO_Power").SI(Kilo.Watt)` (`DrivingCycleDataReader.cs:1079`). See A5.
- **[NOT FOUND]** any other PTO file type (no `.vpto`-variant beyond the three; no separate crane/mixer/refrigeration file format). The drive-cycle `PTO` column (activity flag) and `PTO_Power` column are the only in-cycle PTO inputs.

### A2. BEV PTO → electrical energy from the REESS — full path  [VECTO]
1. **Reader → data:** the declaration default electric PTO cycle is `MunicipalUtility_PTO_generic.vptoel` (`DeclarationData.cs:1795 DefaultE_PTOActivationCycle`), parsed by `EPTOCycleDataParser` into `DrivingCycleEntry.PTOElectricalPowerDemand` [W].
2. **Cycle controller:** `EPTOCycleController` (`PTOCycleController.cs:120-...`) holds the cycle; `CycleData.LeftSample` exposes `PTOElectricalPowerDemand` only while `_ptoActive` (else an empty entry). It advances the iterator **only when active** (`CommitSimulationStep` → `if(_ptoActive) CycleIterator.MoveNext()`).
3. **Simulation component:** `EPTO : IAuxDemand` (`EPTO.cs:15,27-33`):
   ```csharp
   public Watt PowerDemand(IDataBus dataBus) {
       if (dataBus.DrivingCycleInfo.PTOActive)
           return _ptoCycleController.CycleData.LeftSample.PTOElectricalPowerDemand ?? 0.SI<Watt>();
       return 0.SI<Watt>();
   }
   ```
   `AuxID = Constants.Auxiliaries.IDs.PTOConsumer` (`EPTO.cs:42`); `EPTOOn = !PowerDemand(dataBus).IsEqual(0)` (`EPTO.cs:36-39`).
4. **Wiring to the battery (BEV):** `PowertrainBuilderBase.cs:254-264` — when `dataPTO?.PTOCycle != null`, VECTO builds an `EPTO` and adds it to the electric-aux list: `elAux.AddAuxiliary(eptoAux)`. The electric-aux bus (`ElectricAuxiliaries`, 06 §2) sums all consumers → DC/DC (eff 1.0) → `ElectricSystem.Request` → battery `REESS`. So the EPTO power is drawn **directly from the REESS as an electric aux**. Confirms `07` §6. ✅
5. **During stops, driving, or both?** For the **declaration MunicipalUtility BEV** the electric PTO plays during **stops** (A3). A separate **PTO-while-driving** path exists for RoadSweeper (A5). So: **both are possible in VECTO, by PTOActive state** — but the generic refuse BEV job uses the **stop** case.
6. **Idle/transmission loss for electric PTO?** **[NOT FOUND]** for electric PTO. `PTO-tech.csv` (`Power Loss`/`Torque Loss`) and the `.vptol` idle map are **mechanical-PTO** quantities (torque/Nm applied to the engine drivetrain via `PTOCycleController`/`PEVPtoTransm`). For a BEV electric PTO the only energy is `∫ P_PTO_el dt` from the `.vptoel` cycle; no extra idle/transmission loss term is applied to it in `EPTO.cs`. [INFERRED: the mechanical idle/transmission losses model an engine-driven PTO shaft; an electric PTO's losses are already inside its measured `P_PTO_el`.]

### A3. Stop duration ↔ PTO cycle  [VECTO]
- For a stop row with `PTOActive == PTOActivityDuringStop`, the **total stop time = file `StoppingTime` + PTO-cycle `Duration`** (`DistanceBasedDrivingCycle.cs:226-227`):
  ```csharp
  var stopTime = Left.PTOActive == PTOActivity.PTOActivityDuringStop && IdleController != null
      ? Left.StoppingTime + IdleController.Duration
      : Left.StoppingTime;
  ```
  `IdleController.Duration = last.Time − first.Time` of the PTO cycle (`PTOCycleController.cs:67` / `EPTOCycleController` ctor). For the generic `.vptoel` that Duration = **23 s** (t = 0…23).
- The vehicle is **standing still** throughout: a stop requires `VehicleTargetSpeed == 0`, else VECTO throws "Stopping Time only allowed when target speed is zero!" (`DistanceBasedDrivingCycle.cs:234-237`).
- The stop is split into phases around the PTO burst (`GetStopTimeInterval`, `DistanceBasedDrivingCycle.cs:248-310`): **3-phase** if `StoppingTime ≤ 6·TargetTimeInterval` (idle / PTO-active / idle), **7-phase** if longer; during the PTO phase `PTOActive = true; IdleController.ActivatePTO()`, otherwise `PTOActive = false; IdleController.ActivateIdle()`.
- **Which aux run during the PTO phase:** `PTOActive == true` → `EPTO.PowerDemand` returns `P_PTO_el` → **EPTOOn = true**. Via `Conditioning.GetPEV_SHEV_PowerDemand` (`Auxiliaries/Conditioning.cs:85-91`): `if (oneEmOn || EPTOOn) return _electricPowerDemand;` → **Cond ON** even though the vehicle is stopped and the EM is off. ✅ confirms the plan's `Cond·(motor_on OR pto_on)`.
- **SP during the stop:** steering pump is excluded while stopped (06 §1; `ElectricAuxiliaries` removes `STP` when `VehicleStopped`). The vehicle is stationary during a PTO stop → **SP = 0 W**. ✅ confirms the plan's `SP·moving`.

### A4. Which vehicle types / missions / bodies have PTO; which generic files ship  [VECTO]
- **Mission:** **MunicipalUtility** is the PTO declaration mission; defaults are `MunicipalUtility_PTO_generic.{vptol,vptoc,vptoel}` (`DeclarationData.cs:1790-1795`). ✅ confirms `07`.
- **Bodies:** municipal/refuse bodies (`MU4/MU9/MU11`) and construction tipper bodies (`BT1-3`) in `Body_Trailers_Weights.csv` (09 §4). Construction uses a tipper body but **the generic PTO files are the refuse ones** — there is no separate tipper PTO cycle shipped.
- **Generic PTO files that ship:** declaration = the three `MunicipalUtility_PTO_generic.*` only. Engineering mode also ships a **RoadSweeper** example (`Generic Vehicles/Engineering Mode/Class9_RigidTruck_6x2_Roadsweeper/PTO-cycle.vptoc` + `.vptol`) and a generic PTO job (`.../Group9_RigidTruck_6x2_PTO/`), plus BEV `EPTO-idle.vptoel` under `PEV/GenericVehicleE2/`.
- **Crane, concrete mixer, refrigeration, dedicated tipper PTO files: [NOT FOUND].** VECTO ships only **refuse/municipal** (declaration) and **road-sweeper** (engineering) generic PTO cycles. No crane/mixer/reefer PTO files exist in the repo.

### A5. PTO during driving  [VECTO]
- **Yes, VECTO models PTO load while moving**, via two PTOActivity states (`DrivingCycleData.cs:321-326`):
  ```csharp
  public enum PTOActivity { Inactive = 0, PTOActivityDuringStop = 1, PTOActivityRoadSweeping = 2, PTOActivityWhileDrive = 3 }
  ```
- **RoadSweeping (while moving):** `RoadSweeperAuxiliary.cs:30-40` returns `PTOPowerDemandDuringDrive` interpolated over distance when `left.PTOActive == PTOActivityRoadSweeping`:
  ```csharp
  if (left.PTOActive == PTOActivity.PTOActivityRoadSweeping)
      powerDemand = ... VectoMath.Interpolate(left.Distance, right.Distance,
                        left.PTOPowerDemandDuringDrive, right.PTOPowerDemandDuringDrive, MileageCounter.Distance);
  ```
- **WhileDrive:** `PTODriveAuxiliary.cs:5-38` returns a demand when `LeftSample.PTOActive == PTOActivityWhileDrive`, integrating `PTOPowerDemandDuringDrive` over the step.
- Both read the drive-cycle `PTO_Power` column [kW] (`DrivingCycleDataReader.cs:370,1079`).
- **But:** this is driven by the **cycle's `PTO` activity column + `PTO_Power` column**, which the **declaration mission cycles do not carry** for a BEV lorry (the generic declaration PTO case is `PTOActivityDuringStop`). So VECTO *can* model mixer/reefer-style PTO-while-driving **if the cycle supplies the `PTO`/`PTO_Power` columns** — the physics exists; **no generic declaration BEV file uses it** ([NOT FOUND] a shipped declaration BEV PTO-while-driving case; the RoadSweeper example is engineering mode).
- Whether the RoadSweeper `PTOPowerDemandDuringDrive` is routed to the REESS for a BEV specifically was not traced to a battery request in this pass — the RoadSweeper generic job is a diesel Class-9. **[INFERRED]** for a BEV the equivalent would be the `PTO_Power` column feeding an electric aux, analogous to EPTO, but no generic BEV job exercises it.

### A6. Numbers to reproduce the generic refuse BEV PTO energy  [VECTO]/[ARITH]
Files: `Resources/Declaration/MissionCycles/MunicipalUtility_PTO_generic.vptoel` (the electric PTO cycle, = `DefaultE_PTOActivationCycle`).

Cycle values (`P_PTO_el` [kW] at t = 0…23 s) [VECTO]:
```
t 0–4   : 8.42
t 5–8   : 33.69
t 9–23  : 25.92
```
Energy of **one PTO activation** (VECTO uses `LeftSample` each 1-s step, 23 steps t=0→23) [ARITH]:
```
E = Σ P_left·1s = 5·8.42 + 4·33.69 + 14·25.92   (steps t=0..22, left-sample)
  = 42.10 + 134.76 + 362.88  =  539.74 kJ  =  0.14993 kWh    (per activation)
```
Then total PTO energy for a job = `0.14993 kWh × (number of PTO-active stops)`. The MunicipalUtility stop count comes from the `MunicipalUtility.vdri` mission (its stop rows) — not re-counted here (see 08 for the cycle). Only files read were used; no value invented. (`07` §8's "~23 s/stop" is the Duration, confirmed = 23 s.)

### A7. User-supplied PTO profile, in VECTO's format  [INFERRED]
To model a PTO type VECTO does not ship (crane, mixer, reefer), a Bob-supplied profile could reuse VECTO's **`.vptoel`** format so the same loader works:
```
<t> ,<P_PTO_el>        # time [s] , electric PTO power [kW]
0 , <kW>
1 , <kW>
...
```
- For a **during-stop** PTO: supply the activation-cycle `.vptoel`; its last-minus-first time = the activation Duration added to the stop (A3). A refrigeration unit that runs continuously could be a long flat `.vptoel`.
- For a **while-driving** PTO (mixer/reefer on the move): the drive cycle would need a `PTO` activity column set to `3` (WhileDrive) and a `PTO_Power` column [kW] (A5), per `DrivingCycleDataReader.cs:370,1079`.
- This is **[INFERRED]** (a reuse proposal), not a VECTO-stated capability for arbitrary PTO types. No values suggested.

---

## PART B — auxiliaries, remaining blockers

### B1. Mission mapping (how VECTO assigns LH/RD/UD/MU/Constr to a vehicle)  [VECTO]
- A vehicle's missions come from its **HDV group row in `SegmentTable.csv`**: `TruckSegments.CreateMissions` (`TruckSegments.cs:112,196-199`) iterates every declaration `MissionType` and **includes a mission iff that mission's column in the group's row is not `"-"`**:
  ```csharp
  m => m.IsDeclarationMission() && m != MissionType.ExemptedMission && row.Field<string>(m.ToString()) != "-"
  ```
  Columns 28–39 of `SegmentTable.csv` are the mission columns (`Long haul`, `Long haul EMS`, `Regional delivery`, …, `Municipal utility`, `Construction`, …) (09 §1). So the **vehicle group fixes which missions run**, each with its own payload/body/airdrag; aux tables are then keyed by `MissionType`.
- **HDEV mismatch (reported, not decided):** HDEV routes are **user routes**, not VECTO's fixed mission cycles. The aux CSVs (ES/HVAC/PS/SP/Cond) are keyed by `MissionType`, so HDEV needs a mission label to pick aux constants. **[INFERRED] options for Bob (do not pick):**
  1. **User picks a mission category** per route (LH/RD/UD/MU/Constr) → direct CSV lookup (matches the preprocessing plan already written).
  2. **Infer a mission from route character** (avg speed, stop density, distance) via a documented mapping — would be an HDEV ASSUMPTION with no VECTO basis.
  3. **Expose the five aux constants directly** as slots, defaulting to a chosen mission, letting the user override.
  None is sourced in VECTO; all are HDEV choices.

### B2. `motor_on` / `EmOffPrev` — exact condition  [VECTO] + [INFERRED]
- Definition (`ElectricMotor.cs:59`): `EmOffPrev => PreviousState.EMTorque == null` (the `|| EMTorque.IsEqual(0)` is commented out). `CurrentState.EMTorque = emOff ? null : emTorque` (`ElectricMotor.cs:530`).
- `emOff = emTorqueDt == null` (`ElectricMotor.cs:271`), i.e. the EM **controller returned no torque** this step. From `BatteryElectricMotorController.MechanicalAssistPower` (05 §1.2): it returns `null` during **Coast** and **Roll** actions, during the low-speed-braking cutoff, and when no drive torque is available; otherwise it returns a (non-null) torque during **Accelerate** and **Brake**. So **EMTorque == null ⇔ the step is a coast/roll (or low-speed brake cutoff)**.
- **[INFERRED] mapping to observable quantities** (HDEV has no motor torque yet): `motor_on` (= `!EmOffPrev`) corresponds to **the EM applying tractive or regen torque** — i.e. a step where the vehicle is **accelerating/holding speed under power (P_wheel > 0)** or **braking with regen (P_wheel < 0 and not pure coast)**. It is **off** during **free coast/roll** and at **standstill** (no torque). The cleanest HDEV observable proxy is likely **"not coasting and not stopped"**, but VECTO's exact trigger is the controller returning null, which depends on the driver action (coast/roll vs accelerate/brake), not directly on speed sign — so any HDEV speed/accel/P_wheel proxy is an approximation. No single observable reproduces it exactly; this stays [INFERRED].

### B3. HVAC group 5 / group 10 MU = 0  [VECTO]
- Confirmed from `Resources/Declaration/VAUX/HVAC-Table.csv` (Default technology): group **5** = `350/200/150/0/200` and group **10** = `350/200/150/0/200` (LH/RD/UD/**MU**/Constr) — the Municipal-utility cell is an **explicit 0**, not blank. ✅ confirms 06 §1 / `13-followups`.
- **Intended or a gap? [INFERRED]:** it is an **explicit numeric 0** (blank cells elsewhere parse to NaN and raise on lookup — 06 §1), so it is deliberately "0 W HVAC for group 5/10 MU", not a missing-cell gap. **Why** it is 0 (vs 300 W for groups 4/9/11) is **[NOT FOUND]** in code or release notes — the value is stated without rationale. (`06` §5 already lists this as an open "why".)

### B4. `VectoRunData.ElectricAuxDemand`  [VECTO]
- Field: `VectoRunData.cs:174 public Watt ElectricAuxDemand`.
- **Engineering mode only:** set from `AuxiliaryInputData.Auxiliaries.ElectricPowerDemand` (`EngineeringModeVectoRunDataFactory.cs:274,414,521,665,771`).
- **Declaration mode: forced to 0** — `PowertrainBuilder.cs:642` and `:778` set `data.ElectricAuxDemand = 0.SI<Watt>()`.
- It becomes an aux `PowerDemandElectric` (`PowertrainBuilderBase.cs:321`, aux ID `PowerAuxiliaryElectric`). For a **BEV declaration lorry it is 0** and therefore **adds nothing** to the five aux. ✅ resolves the `06` open item (ElectricAuxDemand use). It is an engineering-mode user constant, not part of the declaration five.

### B5. Aux during depot charging / parked outside the drive cycle  [NOT FOUND]
- No VECTO code applies auxiliary power outside the drive cycle. The aux (ES/HVAC/PS/SP/Cond/EPTO) are all `IAuxDemand` consumers summed **inside the simulation step** of a driving cycle (`ElectricAuxiliaries`, `ElectricSystem.Request`). There is **no charging phase** in VECTO at all (04 §1), hence **no aux-during-charging term**. **[NOT FOUND].** ✅ confirms the grounding gap "No aux during depot charging".

### B6. Technology lists for a BEV lorry (for the UI)  [VECTO]
Allowed values, read from the applicability code / tables:
- **ES (electric system):** `Standard technology`, `Standard technology - LED headlights, all` (`Resources/Declaration/VAUX/ES-Tech.csv`). (Blank → "Standard technology", 06 §1.)
- **HVAC:** `None`, `Default` (`HVAC-Table.csv`; the two allowed per Annex IX, 06 §1).
- **PS (pneumatic):** the 9 fully-electric rows with `PEV = 1` (`PS-Table.csv` applicability column): `Small + elec. driven`, `Small + AMS + elec. driven`, `Medium Supply 1-stage + elec. driven`, `Medium Supply 1-stage + AMS + elec. driven`, `Medium Supply 2-stage + elec. driven`, `Medium Supply 2-stage + AMS + elec. driven`, `Large Supply + elec. driven`, `Large Supply + AMS + elec. driven`, `Vacuum pump + elec. driven`. (Mechanical techs throw for a BEV — 06 §1.)
- **SP (steering pump):** the fully-electric techs from `SP-Tech.csv` (`SteeringPump.IsApplicable` → architecture table): **`Electric driven pump`** and **`Full electric steering gear`** are the PEV-allowed entries (the other six — Fixed/Dual/Variable displacement variants — are mechanical and not applicable to a BEV; 06 §4, paux doc §4.4). One technology per steered axle (`HeavyLorryAuxiliaryDataAdapter.cs:212-214` throws if count ≠ steered axles).

---

## PART C — efficiency-map mode blockers (short)

### C1. Wheels.csv  [VECTO]
- File `Resources/Declaration/Wheels.csv`. Columns: `Wheel, cross-sectional width [mm], tire aspect ratio [%], rim diameter [inch], d [mm], Inertia, F [-], comment`.
- Reader `Models/Declaration/Wheels.cs:19-35`:
  ```csharp
  Inertia           = row.ParseDouble("inertia").SI<KilogramSquareMeter>(),   // kg·m²
  WheelsDiameter    = row.ParseDouble("d").SI(Milli.Meter).Cast<Meter>(),      // d [mm] → m
  CircumferenceFactor = row.ParseDouble("f")                                   // F [-]
  DynamicTyreRadius => WheelsDiameter * CircumferenceFactor / (2 * Math.PI);   // r_dyn
  ```
- So **`r_dyn = d · F / (2π)`** (d = dynamic rolling diameter [mm→m], F the circumference factor, e.g. 3.05 for heavy tyres), and **wheel inertia = the `Inertia` column directly** [kg·m²]. (Corrects 09 §5, which called `d` the "dynamic rolling diameter" and did not give the r_dyn formula — now `r_dyn = d·F/(2π)`, note F≈3.05 ≈ π·(0.971) so r_dyn ≈ 0.971·d/2, i.e. slightly less than the geometric radius.)

### C2. BEV gear/axle ratio for the generic job  [VECTO]
- Gearbox ratios: `AMT.vgbx` → gears `"Ratio": 2.59, 1.93, …` (first two gears; `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/AMT.vgbx`). (3.86 is the axle in that excerpt context.)
- **EM axle-drive-converter (ADC) ratio:** the BEV vveh entry gives `"Ratio": 2.0` under the E2 electric-machine component with `MechanicalEfficiency: 0.97` (`BatteryElectricVehicle_PTO.vveh`, electric-machine block: `Count 2, Ratio 2.0, Position E2, MotorFile GenericEMotor_125kW_485Nm.vem, MechanicalEfficiency 0.97`). This `Ratio` is the EM `RatioADC` used by `ElectricMotor` (01 §5).
- So the generic BEV lorry's drivetrain ratio chain = EM ADC ratio **2.0** × gearbox gear ratio × (axle, if separate). Values read from the vveh/vgbx files only.

### C3. EM map format / interpolation / normalised-map scaling  [VECTO] — confirms `01`
- Format & interpolation: `01` §2 is correct — columns `n [rpm], T [Nm], P_el [W]` (`ElectricMotorMapReader.cs`), **Delaunay triangulation** over (torque, speed), **no extrapolation in Declaration mode**. ✅
- **Normalised-map scaling to the rated point** (01 §7) confirmed with file:line: `GenericBusElectricMotorData.cs:303-314` `DeNormalizeData`:
  ```csharp
  motorSpeed     = ParseDouble(MotorSpeedNorm) * ratedPoint.NRated;   // n = n_norm · N_rated
  torque         = ParseDouble(TorqueNorm)     * ratedPoint.TRated;   // T = T_norm · T_rated
  powerElectrical= ParseDouble(PowerElectricalNorm) * ratedPoint.PRated; // P_el = Pel_norm · P_rated
  ```
  i.e. the normalised `EfficiencyMap_{PSM,ASM}_normalized.vmap` (columns `n_norm,T_norm,Pel_norm`) is scaled by the machine's rated point `(N_rated, T_rated, P_rated)` (`DeNormalizeData` called from `GetElectricMotorVoltageLevelData`, `:263`). **No correction to `01` needed.** ✅

---

## PART D — SP and Conditioning: source, physics, weather

### D1. SP calculation for a BEV lorry (re-confirmed)  [VECTO]
- `SteeringPump.Lookup(mission, hdvClass, technologies)` (`Models/Declaration/Auxiliaries/SteeringPump.cs:58-114`):
  - Per steered axle, base demand per **UF/B/S** from `SP-Table.csv` (`SteeringPumpBaseLine`, values `/100`), × per-axle share from `SP-Axles.csv` (`_axleLookup`), accumulated into the **electric** bucket if the technology is fully electric else the **mechanical** bucket (`:86-97`).
  - The three component sums are each multiplied by the **technology scaling factor averaged over all steered axles** `factors.X / axleCount` (`:102-110`), from `SP-Tech.csv`.
  - Returns `(mechanicalPumps, electricPumps)` = sum of UF+B+S per bucket (`:112-113`). Method doc note: *"the power demand is mechanical also for the electric pumps"* (`:56`).
- **×0.7:** applied in `HeavyLorryAuxiliaryDataAdapter.AddSteeringPumps` (`HeavyLorryAuxiliaryDataAdapter.cs:239`): `PowerDemandElectric = powerDemand.electricPumps * alternatorEfficiency` where `alternatorEfficiency = DeclarationData.AlternatorEfficiency` (`:54`, = 0.7). For a BEV both allowed techs are fully electric, so `mechanicalPumps = 0` and only the electric pump exists.
- **UF / B / S meaning — [VECTO]** (release notes `ReleaseNotesVecto3x.md:426-428`): **U&F = "unloaded and friction", B = "banking", S = "steering"**. The baseline per cycle is scaled by technology-dependent scaling factors (CFs) for each (`:421-425`).
- **What the ×0.7 represents — [VECTO]**: it is the **"generic alternator efficiency of 0.7 used consistently throughout the whole VECTO auxiliary approach"** — mechanical (alternator-drive) power from the table is multiplied by 0.7 to get electric power (`ReleaseNotesVecto3x.md:367`). So for a fully-electric pump the table's mechanical figure × 0.7 = the electric REESS draw. (Not [INFERRED] — stated in the release notes.)

### D2. What Conditioning physically covers  [VECTO]
- The Conditioning aux ("COND") is **"conditioning power for electric propulsion components"** / **"electric components conditioning power"** (`ReleaseNotesVecto3x.md:345,408,413`). It is applied when **≥1 EM is on** (electric powertrain propelling/braking) **or E_PTO is on** (`:410`): *"values from table below are fully applied when at least one EM = on in simulation ... or when E_PTO = on"* — exactly the code in `Conditioning.GetPEV_SHEV_PowerDemand` (`:85-91`).
- So Conditioning = **thermal management of the electric drivetrain components (motor/inverter/battery conditioning)**, **not cabin HVAC** (cabin is the separate HVAC/AC aux). [VECTO] for "electric propulsion components"; the precise component split (motor vs inverter vs battery) is **[NOT FOUND]** — the docs say "electric components" / "electric propulsion components" without itemising, and the code only stores one constant W. (`06` §5 open "what Conditioning physically covers" is now answered at the "electric propulsion components" level; finer detail [NOT FOUND].)

### D3. Origin of SP-Table / SP-Axles / SP-Tech / Cond-Table values  [VECTO] + [NOT FOUND]
- The release notes frame these as the VECTO **declaration auxiliary approach** (ICE fan + conditioning + steering + electric board net + pneumatic), with the steering approach "foundation ... basic power demand per cycle × technology CFs" and the 0.7 alternator efficiency (`ReleaseNotesVecto3x.md:340-430`). The PS release-notes block cites **"acc. to Annex specifications"** for which technologies are allowed per architecture (`:365, :369`). The paux decision doc also ties PS/SP technology applicability to Regulation Annex III/IX tables (06 / paux §4).
- A **measurement study or specific regulation-annex table number** for the **numeric values** in `SP-Table.csv` / `SP-Axles.csv` / `SP-Tech.csv` / `Cond-Table.csv` is **[NOT FOUND]** in the repo (code, release notes, user-manual text). The release notes describe the *method* and reference "Annex specifications" for applicability, but no citation to a measurement campaign or a specific annex table for the W values. The underlying **Regulation (EU) 2017/2400 Annex IX** extract is **missing** from `reference/regulation/` (grounding note) — so the regulatory source cannot be quoted here; name it: *Regulation 2017/2400 Annex IX auxiliary tables — extract missing*.

### D4. Weather / temperature dependence of lorry aux

- **[VECTO] confirmation:** **no lorry auxiliary in VECTO depends on ambient temperature, speed, or load** beyond the on/off flags. The five aux are **constants per vehicle × mission**, toggled only by `moving` (SP) and `motor_on OR pto_on` (Cond). Grep of `Models/Declaration/Auxiliaries/` for any `Temperature`/`ambient` term → **none**. Temperature/solar/heat-pump physics exists **only in the bus SSM model** (`Models/BusAuxiliaries/...`), which is **not referenced by `HeavyLorryAuxiliaryDataAdapter.cs`**. ✅ confirms the grounding gaps "no cabin heating / no temperature dependence for trucks".

The rest of D4 is **ideas, clearly not decisions** — presented for Bob, no values without a source:

**(D4-idea-a) Physical/published basis for temperature dependence — [INFERRED], sources named only:**
- **(a) Steering pump power vs temperature:** no VECTO basis; hydraulic-fluid viscosity rises at low T, but VECTO's electric steering pump is a fixed W. Any T-dependence would need an external source (e.g. an OEM EPS datasheet or a published EPS-efficiency-vs-temperature study) — **none in the repo**; do not add a value without one.
- **(b) Battery/drivetrain conditioning vs temperature:** this is physically the most T-sensitive (battery pre-heat/cooling, cabin heat-pump draw). VECTO's Cond is a flat W. External bases exist in the literature (e.g. ICCT/JRC BEV-truck energy reports, OEM thermal-management data) — must be named and sourced before any number.
- **(c) Cabin heating/cooling for BEV lorries:** VECTO has **no lorry cabin-heating value** at all (HVAC is A/C-compressor only, no heater; 06 §3). The only VECTO temperature-dependent HVAC physics is the **bus SSM** (see below). Sources for a lorry cab would be the VECTO **bus SSM** method itself (`ReleaseNotesVecto3x.md:340-430` frames the declaration aux method; the SSM physics is in `Models/BusAuxiliaries/`), plus OEM/ICCT/JRC data for cab heat loads.

**(D4-idea-b) Reuse of the bus SSM for lorry cabin heating/cooling — [INFERRED]:**
- The bus SSM (`Models/BusAuxiliaries/DownstreamModules/Impl/HVAC/SSMCalculate.cs`) computes HVAC electrical/mechanical/heating power as a **weighted average over climate points**, with **heat-pump COP** per technology and electric/fuel-heater efficiencies. Climate data: `Resources/Declaration/Buses/DefaultClimatic.aenv` — 11 points from **−20 °C to 33 °C**, each with solar [W/m²], a weighting factor, a heating/cooling flag, and **heat-pump COP** per type (R-744 COP **1.80 at −20 °C**, rising to ~3.8 at 20.5 °C) plus heater efficiencies (0.93 electric, 0.80 fuel). `SSMCalculate` computes `HeatPumpPowerMech/El`, `ElectricHeaterPowerEl`, `RequiredHeatingPower` summed over points (`SSMCalculate.cs:149-165`).
- To reuse it for a **lorry cab**, the SSM needs lorry-cab inputs it currently only has for buses: cab/compartment volume & surface, insulation/U-values, target cabin temperature, occupancy, fresh-air rate, glazing/solar area, heat-pump type & max heating power, and the HVAC contribution split. **Which have NO VECTO lorry value: all of them** — VECTO ships **no lorry SSM inputs** ([NOT FOUND] any lorry `.aenv`/SSM parameter set). The climate map (`DefaultClimatic.aenv`) and COP table could be reused as-is (or replaced with **DMI hourly T + solar**), but every cab-geometry/thermal input would be an HDEV-supplied, sourced value — not a VECTO quantity.

**(D4-idea-c) Weather layer on top of VECTO constants — [INFERRED] shape only:**
- A weather layer could be a **multiplicative or additive adjustment** applied in preprocessing, with **neutral default = no effect**, so VECTO is reproduced exactly:
  - keep the VECTO constants ES/HVAC/PS/SP/Cond as today;
  - add optional functions `f_SP(T)`, `f_Cond(T)`, and a separate `P_cabin(T, solar)` term, **all passed as arguments** (engines stay pure), **defaulting to** `f(·)=1` / `P_cabin=0` → weather effect = 0 → identical to VECTO.
  - the cabin term, if enabled, would use the SSM `heatingDemand(T)/COP(type,T)` physics (06 §2) with DMI T/solar; its parameters are sourced slots (D4-idea-b), never defaulted to a number.
- This matches the grounding rule for non-VECTO extras: optional, flagged, neutral-default, source required (06 §4). **Not a decision — a shape for Bob.**

### D5. Is SP power tied to vehicle speed or steering activity beyond "0 W when stopped"?  [NOT FOUND] / [VECTO]
- **[NOT FOUND]** any dependence on vehicle speed or actual steering activity. The SP electric power is a **constant W** (per mission × group × technology, split UF/B/S), gated only by the `VehicleStopped` flag that zeroes it at standstill (06 §1). The "banking" and "steering" components (D1) are **fixed table shares averaged over axles**, not functions of instantaneous speed or steering angle. So beyond "0 W when stopped", **SP has no speed/activity dependence** in VECTO. ✅

---

## Confirmed / corrected vs `07-pto-all.md`
- **Confirmed:** file formats & units; `P_PTO_el` = kW; EPTO is an `IAuxDemand` drawn from the REESS (`AuxID = PTOConsumer`); Cond stays on while EPTO on; DC/DC = 1.0; MunicipalUtility is the PTO mission; Duration ≈ 23 s.
- **Corrected / completed:** `.vptoc` columns are **t / engine speed / PTO torque** (not just "cycle rows"); there are **4 PTOActivity states** incl. **PTO-while-driving** (RoadSweeper / WhileDrive, A5) — `07` only described the stop case; stop duration = **`StoppingTime + PTO-cycle Duration`** with 3-/7-phase splitting (A3), which `07` did not state; electric PTO has **no** idle/transmission-loss term (`PTO-tech.csv`/`.vptol` are mechanical-only, A2.6).

## Index of [INFERRED] and [NOT FOUND] items
**[INFERRED]:** A2.6 (electric PTO has no extra loss — reasoning); A5 (BEV while-driving PTO routing — no generic BEV job exercises it); A7 (user PTO profile reuse proposal); B1 (HDEV mission-mapping options); B2 (motor_on → observable-quantity mapping); B3 (MU=0 is deliberate, not a blank-cell gap); D4-idea-a/b/c (weather-layer ideas, sources named, no values).
**[NOT FOUND]:** A1 (no PTO file type beyond the three + in-cycle `PTO_Power`); A4 (no crane/mixer/reefer/dedicated-tipper generic PTO files — only refuse + road-sweeper); A5 (no shipped *declaration BEV* PTO-while-driving case); B3 (no stated rationale for group 5/10 MU HVAC = 0); B5 (no aux power outside the drive cycle / during charging); D2 (no itemised component split for Conditioning beyond "electric propulsion components"); D3 (no measurement-study/specific-annex-table citation for the SP/Cond numeric values; Regulation 2017/2400 Annex IX extract missing); D4-idea-b (no VECTO lorry SSM/cab inputs exist); D5 (no SP speed/steering-activity dependence).
