# 01 — Electric machine (EM / inverter / overload / regen limits)

VECTO source: clone of `mohgsaad-art/VECTO`, branch `stable`, commit `d16ba783c` (v5.1.3). All paths below are relative to that clone unless noted. Tags: **[VECTO]** = read directly from the source; **[INFERRED]** = my interpretation.

> Grounding note: the HDEV `reference/vecto/cs/` bundle does **not** contain the EM files; everything here is from the full stable clone. For HDEV code, cite the clone path + commit. The Annex Xb *regulation extract* is still **missing** from `reference/regulation/` — this file cites VECTO **code** for the standard-value path, not the regulation text.

---

## 1. What VECTO does

A battery-electric lorry's traction comes from one `ElectricMotor` component (file `VectoCore/VectoCore/Models/SimulationComponent/Impl/ElectricMotor.cs`). The motor is **not** a fixed-efficiency multiplier. For every simulation step it:

1. Computes max drive / max recuperation torque at the current speed (full-load curve ∩ battery power limit ∩ thermal de-rating). [VECTO] `ElectricMotor.cs` `GetMaxDriveTorque` / `GetMaxRecuperationTorque`.
2. Asks the strategy/controller how much mechanical torque to apply (`Control.MechanicalAssistPower`). [VECTO] `ElectricMotor.cs:Request`/`DoHandleRequest`.
3. Looks up the **electrical** power that mechanical operating point costs, from a 2-D efficiency map (speed × torque → electrical power), interpolated between voltage levels. [VECTO] `ElectricMotorData.cs:LookupElectricPower`, `EfficiencyMap.cs:LookupElectricPower`.
4. Requests that electrical power from the electric system / battery; if the battery can't supply/absorb it, the operating point is reduced or declared invalid. [VECTO] `ElectricMotor.cs:DoHandleRequest`, calls `ElectricPower.Request(...)`.

So the EM path is **map-based**, exactly the Annex Xb concept the HDEV docs flag as "not yet grounded". The HDEV placeholder 0.95/0.95/0.98 is a scalar stand-in for this map.

### Electric machine positions / types [VECTO]
`PowertrainPosition` values relevant to BEV lorries: `BatteryElectricE2`, `BatteryElectricE3`, `BatteryElectricE4`, plus `IHPC`, `IEPC` (integrated electric powertrain). For a pure BEV lorry the EM is `BatteryElectricE2/E3/E4` (position after/at the gearbox or axle). IEPC/IHPC are integrated machine+gearbox variants (see 02-transmission-axle.md). The EM machine type is `ElectricMachineType` = ASM (asynchronous) or PSM (permanent-magnet synchronous) — this selects the normalized generic map (see §5).

---

## 2. The efficiency / loss map — format, interpolation, power→loss

### 2.1 Map format and units [VECTO]
Reader: `VectoCore/VectoCore/InputData/Reader/ComponentData/ElectricMotorMapReader.cs`.

Columns (header names, lines ~ `Fields` block near end of file):
```
n     = motor speed   [rpm]      (parsed via .RPMtoRad(), stored in rad/s)
T     = torque        [Nm]
P_el  = electrical power [W]      (CreateEntry: row.ParseDouble(Fields.PowerElectrical).SI<Watt>())
```
`ElectricMotorMapReader.CreateEntry`:
```csharp
speed:  row.ParseDouble(Fields.MotorSpeed).RPMtoRad(),
torque: row.ParseDouble(Fields.Torque).SI<NewtonMeter>(),
powerElectrical: row.ParseDouble(Fields.PowerElectrical).SI<Watt>());
```
Note the commented-out `.SI(Unit.SI.Kilo.Watt)` line directly above — i.e. `P_el` is read as **W**, not kW. [VECTO]

Sign convention (from the map build + `EfficiencyMapNew`): **torque < 0 = drive/propulsion, torque > 0 = generation/recuperation** on the mechanical side; the Delaunay z-value stores loss as electrical-minus-mechanical. The point is added as `AddPoint(-entry.Torque * count, speed, z * count)`. `count` = number of identical machines in parallel (scales torque and power linearly). [VECTO] `ElectricMotorMapReader.Create`.

### 2.2 Interpolation [VECTO]
The map is a **Delaunay triangulation** over (torque, speed) → z, interpolated barycentrically. `EfficiencyMap._efficiencyMapMech2El.Interpolate(torque, angularSpeed)`; extrapolation only `if (allowExtrapolation)` which is **true only outside Declaration mode** (`DataBus.ExecutionMode != ExecutionMode.Declaration`, see `ElectricMotor.cs:DoHandleRequest` call to `LookupElectricPower(... DataBus.ExecutionMode != ExecutionMode.Declaration)`). So **in Declaration mode VECTO never extrapolates the EM map** — an out-of-map point returns `null` → invalid operating point. [VECTO] `EfficiencyMap.cs:LookupElectricPower`, `EfficiencyMapNew.LookupElectricPower`.

Two map classes:
- `EfficiencyMap` (legacy): z = electrical power directly (`result.ElectricalPower = value.SI<Watt>()`).
- `EfficiencyMapNew` (current): z = a loss-torque term; electrical power reconstructed as `z·ω + ω·T` i.e. `P_el = ω·(T + z)`. `GetDelaunayZValue = -((P_el − ω·T)/ω)`. [VECTO] `EfficiencyMap.cs`.

### 2.3 power→loss and the inverse lookup [VECTO]
- Forward (mech→elec): `LookupElectricPower(volt, avgSpeed, torque, gear)` with voltage interpolation between `VoltageLevels` (`ElectricMotorData.cs:VoltageLevelData.LookupElectricPower`).
- Inverse (elec→mech torque, needed when the battery limits power): `EfficiencyMap.LookupTorque(batPower, avgSpeed, maxEmTorque)` runs a **line search** (`SearchAlgorithm.Search`) to find the torque whose electrical power matches the available battery power. Tolerance `Constants.SimulationSettings.InterpolateSearchTolerance`. [VECTO] `EfficiencyMap.cs:LookupTorque`, `SearchTorqueForElectricPower`.
- Modal loss output: `P_EM_electricMotorLoss = T_map·ω − P_el`, transmission loss and inertia loss reported separately. [VECTO] `ElectricMotor.cs:DoWriteModalResults` (`ModalResultField.P_EM_electricMotorLoss_`, `P_EM_TransmissionLoss_`, `P_EM_electricMotorInertiaLoss_`, `P_EM_loss_`).

### 2.4 Efficiency sanity clamp [VECTO]
`ElectricMotorMapReader.Create`: any map entry with implied efficiency > 2 in **Declaration mode throws**; entries with efficiency > 1 are clamped to `DeclarationData.ElectricMachineDefaultEfficiencyFallback = 0.98` (drive: `P_el = T·ω / 0.98`; gen: `P_el = T·ω · 0.98`). [VECTO] `ElectricMotorMapReader.cs`, `DeclarationData.cs:141`.

---

## 3. Max / drag torque, and how the EM limits acceleration & regen

### 3.1 Full-load curve [VECTO]
`ElectricMotorFullLoadCurve.cs`. Columns per voltage level: motor speed (rpm→rad/s), `FullDriveTorque` (negative = drive), `FullGenerationTorque` (positive = gen). Linear interpolation between speed points (`FullLoadDriveTorque`, `FullGenerationTorque`), **clamped** at the ends (`FindIndex` returns first/last segment outside range — no extrapolation). `MaxPower`, `RatedSpeed`, `NP80low` computed from the curve (quadratic solve for the speed of max power). [VECTO]

### 3.2 Drag curve [VECTO]
When the EM is "off" or coasting, a **drag torque** is applied: `ElectricMotorData.DragCurveLookup(emSpeed, gear)` → `EMDragCurve.Lookup(emSpeed)` (IEPC has per-gear drag curves). This drag is applied forward onto the drivetrain when `ElectricPower == null` or the EM is off. [VECTO] `ElectricMotorData.cs`, `ElectricMotor.cs:DoHandleRequest` (`emTorque = DragCurveLookup(...) + inertiaTorqueEm`).

### 3.3 How acceleration is limited [VECTO]
`GetMaxDriveTorque(volt, dt, avgSpeed, gear)`:
```
maxEmTorque = Max( derated continuous torque (if de-rating active), FullLoadDriveTorque )
maxBatPower = electricSystemResponse.MaxPowerDrive − (MaxNominalFCRatedPower ?? 0)   // battery discharge limit
if maxBatPower >= 0  → return null   // battery below min SoC, no drive torque available
maxBatDriveTorque = EfficiencyMapLookupTorque(volt, maxBatPower, avgSpeed, maxEmTorque, gear)
maxTorqueDrive = Max(maxEmTorque, maxBatDriveTorque)   // most-negative wins the Max? note signs
```
So available tractive torque is the **more limiting** of (a) the full-load/thermal EM curve and (b) what the **battery** can discharge at the current SoC/voltage. Acceleration is capped by whichever binds. [VECTO] `ElectricMotor.cs:GetMaxDriveTorque`.

### 3.4 How regen is limited [VECTO]
`GetMaxRecuperationTorque(volt, dt, avgSpeed, gear)`:
```
maxEmTorque = Min( derated continuous gen torque, FullGenerationTorque )
maxBatPower = electricSystemResponse.MaxPowerDrag        // battery charge-acceptance limit
if maxBatPower <= 0 → return null   // battery full, no recuperation
maxBatRecuperationTorque = EfficiencyMapLookupTorque(volt, maxBatPower, avgSpeed, maxEmTorque, gear)
maxTorqueRecuperate = Min(maxEmTorque, maxBatRecuperationTorque)
```
So regen torque is capped by the **lower** of EM generation capability and the battery's charge-acceptance power (which itself depends on SoC, see 03-battery.md). When the battery is full, `MaxPowerDrag <= 0` → no regen → the driver must use the mechanical/service brake (see 05-braking-regen-driver.md). [VECTO] `ElectricMotor.cs:GetMaxRecuperationTorque`.

### 3.5 Speed limit [VECTO]
`GetMotorSpeedLimit` = min(gear max speed, EM `MaxSpeedDt`). Exceeding → `ResponseEngineSpeedTooHigh`. [VECTO] `ElectricMotor.cs`.

### 3.6 Inertia [VECTO]
Rotational inertia of the EM (`ModelData.Inertia`, scaled by `count`) adds an inertia torque `Formulas.InertiaPower(...) / avgEmSpeed` to drive torque (reduces available drive torque when accelerating, adds drag when recuperating). [VECTO] `ElectricMotor.cs:DoHandleRequest`.

---

## 4. Overload / thermal de-rating model [VECTO]

This is a **thermal buffer (energy) integrator**, not a temperature model.

- State: `ThermalBuffer` [J], `DeRatingActive` [bool]. [VECTO] `ElectricMotor.cs`.
- Each step (`DoCommitSimulationStep`): `losses = T_em·ω − P_el`; `contribution = (losses − ContinuousPowerLoss)·dt`; `ThermalBuffer += contribution` (clamped to `[0, OverloadBuffer]`). When losses exceed the continuous-loss level, the buffer fills; below it, drains. [VECTO] `ElectricMotor.cs:DoCommitSimulationStep`.
- Switching: de-rating turns **on** when `ThermalBuffer >= OverloadBuffer`; turns **off** when `ThermalBuffer <= OverloadBuffer · OverloadRecoveryFactor`. `OverloadRecoveryFactor = 0.9` (`DeclarationData.cs:135`). [VECTO]
- While de-rated, max torque is limited to `ContinuousTorque` / `ContinuousTorqueGen` (or `ContinuousPower/speed`). [VECTO] `ElectricMotor.cs:GetMaxDriveTorque/GetMaxRecuperationTorque`.
- The `OverloadData` (ContinuousTorque, ContinuousTorqueGen, ContinuousPower, OverloadBuffer [J], ContinuousPowerLoss) is **pre-computed** from the full-load curve + maps, not read directly. Generic/standard build uses an `OverloadTime = 3 s` peak-loss window. [VECTO] `ElectricMachinesDataAdapter.cs:CalculateOverloadBuffer` (lines ~480–700), `GenericBusElectricMotorData.cs:CalculateOverloadBuffer`.
- Modal output: `ElectricMotor_OvlBuffer_` = fraction of buffer used (0..1). [VECTO] `ElectricMotor.cs:DoWriteModalResults`.

---

## 5. Inverter / ADC (axle-drive / gear) losses and voltage [VECTO]

- There is **no separate inverter efficiency map**: inverter + motor losses are **together** in the electrical-power map (P_el already includes inverter). This is why the HDEV placeholder uses one "inverter" factor (0.95) on top of motor (0.95) — VECTO folds them into one map. [INFERRED from map being "mechanical→electrical" with no distinct inverter block.]
- A **mechanical transmission (ADC) loss map** sits between EM rotor and drivetrain: `TransmissionLossMap` (`ConvertEmTorqueToDrivetrain` / `ConvertDrivetrainTorqueToEm`). For generic/standard machines the ADC efficiency is `0.98` if `RatioADC==1` else `0.96`; if no ADC, `ElectricMachineDefaultMechanicalTransmissionEfficiency = 1` (`DeclarationData.cs:119`). [VECTO] `GenericBusElectricMotorData.cs` (`adcLossMap = adcRatio.IsEqual(1) ? 0.98 : 0.96`), `ElectricMachinesDataAdapter.cs`.
- **Voltage dependence**: the map and full-load curve are given per voltage level; VECTO interpolates between levels using the battery's `InternalVoltage` each step. Standard-value machines are given a wide voltage span (1 V … 10e9 V) so interpolation is effectively flat. [VECTO] `ElectricMotorData.cs:VoltageLevelData.GetSection`, `ElectricMachinesDataAdapter.cs:StandardValuesEmInputData(... 1.SI<Volt>(), 10E9.SI<Volt>())`.
- **DC/DC**: `DcDcConverterIncluded` flag exists on the EM input, but in Declaration mode DC/DC efficiency is fixed at 1.0 (matches HDEV gap note "No DC/DC loss"). [VECTO] `ElectricMachinesDataAdapter.cs` (flag read, no loss applied in declaration).

---

## 6. EmOffPrev / motor-off (couples to task M0.16) [VECTO]

`ElectricMotor.cs`:
```csharp
public bool EmOffPrev => PreviousState.EMTorque == null ? true : false;
public bool? EmOffCurr => CurrentState == null ? null : CurrentState.EMTorque == null ? true : false;
```
So **"EM off" ⇔ `EMTorque == null`**, i.e. the controller supplied no torque this step (pure coast/drag), *not* `EMTorque == 0` (the `|| IsEqual(0)` is commented out). When off, VECTO applies only drag + inertia torque and `P_el = 0`. Modal flag `EM_Off_` = 1 when `EMTorque == null`. [VECTO] `ElectricMotor.cs` (`EmOffPrev`, `DoWriteModalResults` `EM_Off_`, the `emOff` branch in `DoHandleRequest`).

This is the exact VECTO rule M0.16 should mirror for the P_aux `Cond`/`motor_on` toggle: motor_on = (EM supplied non-null torque this step).

---

## 7. Standard / generic (Annex Xb) EM data shipped for declaration

**Where [VECTO]:**
- Normalized generic efficiency maps (embedded resources):
  - `VectoCore/VectoCore/Resources/Declaration/GenericBusData/EfficiencyMap_PSM_normalized.vmap`
  - `.../EfficiencyMap_ASM_normalized.vmap`
  - `.../EfficiencyMap_IEPC_PSM_normalized.vmap`, `.../EfficiencyMap_IEPC_ASM_normalized.vmap`
- Format (header + first rows of PSM): columns `n_norm, T_norm, Pel_norm` (dimensionless, normalized to rated point):
  ```
  "n_norm "," T_norm "," Pel_norm"
  "0.000","-1.100","0.002"
  "0.000","-1.000","0.002"
  "0.000","-0.900","0.002"
  ...
  ```
  Negative T_norm = drive. [VECTO] file head quoted above.
- **De-normalization** (how a standard machine gets a real map): `n = n_norm·NRated`, `T = T_norm·TRated`, `P_el = Pel_norm·PRated` at the machine's rated point. [VECTO] `GenericBusElectricMotorData.cs:DeNormalizeData`.
- Standard-value wrapper: `ElectricMachinesDataAdapter.cs:StandardValuesEmInputData` / `StandardValueIEPCInputData` (used when `CertificationMethod == StandardValues`).
- Standard IHPC/IEPC generic maps also exist: `EfficiencyMap_IEPC_*_normalized.vmap`.

**Fallback efficiency constants [VECTO] (`DeclarationData.cs`):**
| constant | value | line |
|---|---|---|
| `ElectricMachineDefaultEfficiencyFallback` | **0.98** | 141 |
| `ElectricMachineDefaultMechanicalTransmissionEfficiency` | **1.0** | 119 |
| `OverloadRecoveryFactor` | **0.9** | 135 |
| generic ADC loss (ratio==1 / ratio≠1) | **0.98 / 0.96** | `GenericBusElectricMotorData.cs` |

**Relation to req §1.5.4 (placeholder 0.95/0.95/0.98):**
- VECTO's *only* scalar EM efficiency anywhere is the **0.98 clamp fallback** and the **0.98/0.96 ADC** factors. There is **no** VECTO constant equal to 0.95 for motor or inverter — those two numbers are **HDEV placeholders**, correctly labelled a model gap by the docs. [INFERRED by exhaustive grep of `DeclarationData.cs` + adapters.]
- The real VECTO standard-value path is the **normalized PSM/ASM map de-normalized to the machine's rated point** — not a scalar. HDEV could replicate this *shape* if it ships the normalized `.vmap` and the vehicle's PRated/TRated/NRated. The underlying *regulation* table (Annex Xb) that mandates these values is **still missing** from `reference/regulation/`; cite VECTO code (`EfficiencyMap_PSM_normalized.vmap` + `DeNormalizeData`) instead.

---

## 8. What HDEV needs to replicate this

Minimum to move beyond the 0.95/0.95/0.98 placeholder toward VECTO behaviour:
1. A **2-D map** (speed × torque → electrical power), with Delaunay (or bilinear) interpolation and **no extrapolation in the VECTO-equivalent mode**. Replace the single η/η_regen scalars.
2. Sign convention: drive = power out of battery, regen = power into battery; efficiency differs by direction (map already encodes this).
3. **Full-load curve** (drive/gen torque vs speed) to cap tractive & regen torque, with linear interp + end clamping.
4. **Battery-coupled torque limit**: available drive/regen torque must be re-limited by battery discharge/charge power at the current SoC/voltage (ties to 03-battery.md). This is what makes regen vanish at high SoC and acceleration fade at low SoC.
5. **Drag curve** for coast/off steps.
6. (Optional, later) thermal buffer de-rating (energy integrator, `OverloadBuffer` [J], `ContinuousPowerLoss`, recovery factor 0.9). Likely over-scope for a declaration-equivalent HDEV run; flag as a known simplification.
7. If reproducing the generic/standard path: ship `EfficiencyMap_PSM_normalized.vmap` / `_ASM_` and de-normalize by rated point.

---

## 9. Open questions

- Which generic BEV lorry jobs use **standard values** vs **measured maps**? (The `Group5_ PEV_IEPC_E_stdValues_v2.6.xml` job is a standard-value example; `GenericMap_125kW_485Nm.vemo` in `PEV/GenericVehicleE2` is a measured map.) Need to confirm which HDEV targets. → see 11-validation-data.md.
- Does the HDEV reference run even need the thermal buffer? For steady declaration cycles de-rating rarely triggers; likely safe to omit but must be flagged.
- The HDEV placeholder is applied as *scalars*; is the intent to keep scalars (gap) or to adopt the normalized map? (Decision for Bob; docs currently label scalars a gap, not a deviation.)
- Exact `OverloadTime` and `ContinuousPowerLoss` provenance for standard machines (code uses 3 s + map-derived loss) — regulation text missing.

---

## 10. Unblocks spec task(s)

- **req §1.5.4 / §5 gap list** — confirms 0.95/0.95 are HDEV placeholders (no VECTO equivalent); 0.98 is the only real VECTO scalar (clamp fallback). Lets the assumptions report cite VECTO code precisely instead of "unknown".
- **M0.16 / EmOffPrev** — the exact VECTO rule "EM off ⇔ EMTorque == null" (`ElectricMotor.cs:EmOffPrev`) for the `motor_on`/`Cond` toggle.
- **M0.11 (high-mass power limit, deferred gap)** — VECTO *does* model a power limit via `GetMaxDriveTorque` (battery-limited) + thermal de-rating; this documents what HDEV is choosing **not** to model yet, so the flagged-gap wording can cite the real mechanism.
- **M5.3 (validation vs VECTO)** — identifies the generic BEV lorry EM inputs (maps, full-load curves) needed to build a comparable reference; feeds 11-validation-data.md.
- **M0.21 (consumption, sign-dependent η)** — confirms VECTO's sign switch happens inside the EM map (drive vs gen), supporting the `P_wheel=0` sign switch in HDEV `consumption`.
