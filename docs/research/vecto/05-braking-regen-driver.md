# 05 — Braking, regen split, driver model (coast/roll, EcoRoll/PCC, EmOffPrev, high-mass power limit, .vacc)

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**.

---

## 1. Driver actions and the regen-vs-mechanical-brake split

### 1.1 Driver actions [VECTO]
`Driver.cs` enum `DrivingAction`: `Accelerate (1)`, `Roll (2)`, `Coast (4)`, `Brake (-5)`. The driver issues a target speed/accel for each cycle segment; the strategy (`DefaultDriverStrategy`) picks the action. [VECTO] `Driver.cs:50-56`.

### 1.2 Where regen happens [VECTO]
Regenerative braking is produced by the **electric motor controller**, not the driver. `BatteryElectricMotorController.MechanicalAssistPower(...)` decides the EM torque on the drivetrain:
```csharp
// Roll with gear disengaged: only cancel inertia
if (!gearbox.GearEngaged && DrivingAction == Roll) return -inertiaTorqueLoss;
// Coast or Roll: EM contributes nothing (null = EM off)
if (DrivingAction == Coast || DrivingAction == Roll) return null;
// low-speed braking guard (see 1.4)
if (CannotProvideRecuperationAtLowSpeed(outTorque)) return null;
if (maxDriveTorque == null) return null;
// otherwise: provide -outTorque, limited to [maxDriveTorque, maxRecuperationTorque]
return (-outTorque).LimitTo(maxDriveTorque, maxRecuperationTorque ?? Max(maxDriveTorque, 0));
```
[VECTO] `BatteryElectricMotorController.cs:MechanicalAssistPower`.

So: during an **Accelerate** or **Brake** action the EM provides torque; the request is **clamped to the regen limit** `maxRecuperationTorque`, which itself is capped by the battery charge-acceptance power and SoC (see 01 §3.4 and 03 §4). During **Coast/Roll** the EM is **off** (returns `null`) — no regen, free rolling.

### 1.3 Where the mechanical (service) brake makes up the rest [VECTO]
When the EM alone cannot decelerate the vehicle enough (regen capped, or battery full), the driver's `DrivingActionBrake` runs `SearchBrakingPower(...)` to find the **additional service-brake power** needed to hit the target deceleration. The service brake is `DataBus.Brakes.BrakePower` [W]; if the search returns negative brake power it is an overload (EM/powertrain already over-decelerating). [VECTO] `Driver.cs` brake branch (~lines 773-890), `DataBus.Brakes.BrakePower`.

**Split rule [INFERRED from the two components above]:** total required braking = regen (EM, up to its SoC/charge-limited cap) **+** mechanical service brake (`Brakes.BrakePower`, the remainder). Regen is taken first; mechanical covers whatever regen can't. This is exactly the split HDEV must reproduce: regen energy returns to the battery (minus EM + battery losses), service-brake energy is lost as heat.

### 1.4 Low-speed regen cutoff [VECTO]
`CannotProvideRecuperationAtLowSpeed`: when the driver is **braking** and vehicle speed ≤ `GearboxData.DisengageWhenHaltingSpeed` (or `Constants.SimulationSettings.ATGearboxDisengageWhenHaltingSpeed`) **and** `outTorque < 0`, the EM returns `null` (no regen) — mechanical brake handles the final stop. [VECTO] `BatteryElectricMotorController.cs:CannotProvideRecuperationAtLowSpeed`.

### 1.5 Regen limits summary [VECTO]
- EM generation full-load curve (`FullGenerationTorque`), 01 §3.1.
- Thermal de-rating → `ContinuousTorqueGen`, 01 §4.
- Battery charge-acceptance power `MaxChargePower` (→ 0 when SoC at `MaxSOC`), 03 §4. **Battery full ⇒ no regen ⇒ all braking is mechanical.**
- Low-speed cutoff, §1.4.

---

## 2. Coasting / roll / eco-roll / PCC for BEVs [VECTO]

### 2.1 Coast vs Roll
- **Coast**: accelerator released, gear engaged, EM off (null) — vehicle decelerates on drag + grade + EM drag. [VECTO] `Driver.cs:DrivingActionCoast` → `CoastOrRollAction(..., false)`.
- **Roll**: gear disengaged / freewheel — EM off, only inertia cancelled. [VECTO] `Driver.cs:DrivingActionRoll` → `CoastOrRollAction(..., true)`, `BatteryElectricMotorController` roll branch.

### 2.2 Declaration driver defaults (apply to BEV lorries) [VECTO] `DeclarationData.cs:780-895`, enabled in `DriverDataAdapter.cs:41-75`
| feature | default | value |
|---|---|---|
| **Look-ahead coasting (LAC)** | **Enabled = true** | min speed 50 km/h; `DecisionFactorCoastingOffset 2.5`, `Scaling 1.5`, `LookAheadDistanceFactor 10` |
| **Overspeed** | **Enabled = true** | min speed 50 km/h; allowed overspeed **2.5 km/h** |
| **EcoRoll** | configured | min speed 60 km/h; activation delay 2 s; accel window 0 … 0.1 m/s² |
| **PCC** (predictive cruise) | configured | enable speed 80 km/h; min 50 km/h; preview 1500 m / 1000 m; underspeed 8 km/h; overspeed (UC3) 5 km/h |
| **Engine stop/start** (lorry) | — | activation delay 2 s; max off 120 s; utility factor 0.8 |

The **heavy-lorry declaration adapter uses these base values unchanged** — only bus adapters override (`PrimaryBus` keeps LAC on; `CompletedBus*` disable LAC + overspeed). So a **BEV lorry gets the same LAC / overspeed / EcoRoll / PCC defaults as a diesel lorry**. [VECTO] `DriverDataAdapter.cs:140-175` (overrides are bus-only).

### 2.3 Does the HDEV driver model need these?
HDEV's current `driver_model.py` uses a `.vacc`-based accel/decel with simpler coast/roll. The LAC/EcoRoll/PCC machinery is substantial and declaration-mode-specific; the HDEV reference run can reasonably **omit LAC/EcoRoll/PCC and flag it** (it changes energy on hilly cycles). [INFERRED] — must be listed as a simplification; VECTO defaults above let the report state exactly what is skipped.

---

## 3. EmOffPrev — "the motor is off" (task M0.16) [VECTO]

Defined in `ElectricMotor.cs` (see 01 §6):
```csharp
public bool EmOffPrev => PreviousState.EMTorque == null ? true : false;
```
**EM off ⇔ `EMTorque == null`** = the controller returned `null` from `MechanicalAssistPower`, i.e. the step was Coast/Roll, or low-speed-braking cutoff, or no drive torque available. It is **not** `EMTorque == 0` (that line is commented out). Modal flag `EM_Off_` = 1 in those steps. [VECTO] `ElectricMotor.cs`.

**For M0.16:** `motor_on` should be `not EmOffPrev` = "the EM supplied a non-null torque in the previous step". The P_aux `Cond` term should toggle on this. This matches the VECTO rule exactly; HDEV can cite `ElectricMotor.cs:EmOffPrev` + `BatteryElectricMotorController.cs` (the null-returning branches) as the authoritative definition of when the motor is off.

---

## 4. High-mass acceleration / power limitation (task M0.11) [VECTO]

VECTO does **not** pre-compute a "max acceleration vs power-to-mass" curve for BEVs. Instead the limitation is **emergent**:
1. The `.vacc` curve requests a target acceleration for the current speed.
2. The powertrain tries to deliver it; if the EM/battery can't (torque capped by full-load curve, thermal de-rating, or `MaxDischargePower`), the response is `ResponseOverload`.
3. The driver's `SearchOperatingPoint`/`DrivingActionAccelerate` then **reduces the acceleration** to the maximum the powertrain can actually provide, and re-requests. [VECTO] `Driver.cs:DrivingActionAccelerate` (lines ~159-345, the `ResponseOverload` → re-search branch), coupling to `ElectricMotor.cs:GetMaxDriveTorque` + `Battery.cs:MaxDischargePower`.

So a heavy, under-powered BEV simply accelerates slower than the `.vacc` target — VECTO finds the achievable accel each step. **HDEV currently does not model this reduction** (uses the `.vacc` target directly); M0.11 defers it as a flagged gap. This file documents the real mechanism so the gap wording can cite `GetMaxDriveTorque` + `MaxDischargePower` + the Driver overload re-search, i.e. HDEV omits the "reduce target accel when the EM/battery can't deliver" loop. [INFERRED from the overload-handling control flow.]

---

## 5. Which .vacc do BEVs use? (task M0.13) [VECTO]

**BEV lorries use the same `Truck.vacc` as diesel lorries.** Evidence:
- `md5sum` of `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/Truck.vacc` = `0ba44c5628ce1cd4763cdfacb37723be` — **identical** to:
  - `Generic Vehicles/Declaration Mode/Group5_Tractor_4x2_H2-ICE/Truck.vacc` (a non-BEV lorry), and
  - the HDEV reference bundle `reference/vecto/resources/VACC/Truck.vacc`.
- The PEV IEPC jobs reference `"VACC": "../Common/Truck.vacc"`. [VECTO] grep of `PEV/*.vecto`.

`Truck.vacc` content (format: `v [km/h], acc [m/s²], dec [m/s²]`):
```
v [km/h],acc [m/s²],dec [m/s²]
0,1,-1
25,1,-1
50,0.642857143,-1
60,0.5,-0.5
120,0.5,-0.5
```
[VECTO] file content quoted. (Note: one BEV job, `IMC_BEV_E2_Group5_2030/Truck.vacc`, has a **different** md5 `073ed7e92d...` — a special in-motion-charging case; the standard generic BEV lorry uses the common `Truck.vacc`.)

**M0.13 answer:** switching HDEV to `reference/vecto/resources/VACC/Truck.vacc` is correct and matches the generic BEV lorry — the reference-bundle file is byte-identical to the generic BEV one. The acc/dec curve is **not BEV-specific**.

---

## 6. What HDEV needs to replicate this

1. **Regen-first braking split**: compute EM regen torque capped by generation curve ∩ thermal ∩ battery charge-power(SoC); apply mechanical brake for the remainder; regen energy → battery (via EM+battery losses), brake energy → lost.
2. **Battery-full ⇒ no regen** (regen vanishes as SoC→MaxSOC) — ties to 03 §4.
3. **Low-speed regen cutoff** near standstill.
4. **Coast/Roll = EM off** (no regen, no drive, drag only).
5. The `.vacc` accel/decel curve from the common `Truck.vacc` (M0.13).
6. (Flagged simplifications) LAC/EcoRoll/PCC omitted; high-mass accel reduction omitted (M0.11) — both with VECTO citations.
7. `motor_on = not EmOffPrev`, EM off ⇔ no torque this step (M0.16).

---

## 7. Open questions
- HDEV's current driver model: does it already apply regen before mechanical brake, or treat all braking as one? (Needs read of `src/engine/driver_model.py` — out of scope for this read-only VECTO research; flag for M0 audit.)
- Does HDEV want to model LAC/EcoRoll/PCC at all, or keep the simpler coast model and flag it? (Decision for Bob.)
- The low-speed cutoff speed (`DisengageWhenHaltingSpeed`) value for the generic BEV gearbox — need to read the generic `.vgbx` (not yet done here).

---

## 8. Unblocks spec task(s)
- **M0.13** — confirmed: BEV lorries use the common `Truck.vacc` (reference bundle file is byte-identical to generic BEV job). Loader switch is correct.
- **M0.16 / EmOffPrev** — exact VECTO rule for `motor_on`/`Cond` toggle (`ElectricMotor.cs:EmOffPrev` + controller null branches).
- **M0.11 (high-mass power limit, deferred gap)** — documents the real emergent mechanism (overload → reduce accel) HDEV is choosing not to model yet; gives the gap wording a VECTO citation.
- **M0.21 (consumption)** — the regen/brake split determines when energy returns to the battery vs is lost; informs the sign-dependent efficiency path.
- **M0.1–M0.8 (driver-model audit)** — VECTO's Accelerate/Coast/Roll/Brake action set and the brake-power search are the reference behaviour for the audit fixes.
