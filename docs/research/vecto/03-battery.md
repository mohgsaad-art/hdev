# 03 — Battery / REESS model (OCV, Ri, limits, losses, SOC)

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** read from source, **[INFERRED]** interpretation.

> This file directly serves **task M3.3** (OCV + internal-resistance battery model) and the **"no battery loss while driving" gap**. The HDEV `reference/vecto/cs/Battery.cs` is the *same* file; here I quote it with the full data layer (`BatteryData.cs`) and readers that the bundle lacks.

---

## 1. What VECTO does (equivalent-circuit model)

VECTO's REESS is a **0th-order equivalent circuit**: an open-circuit voltage source `U0(SoC)` in series with an internal resistance `Ri(SoC, t_pulse)`. There is **no RC branch, no diffusion, no temperature dynamics** (temperature is only a stored metadata number). File: `Models/SimulationComponent/Impl/Battery.cs`; data: `.../Data/ElectricComponents/Battery/BatteryData.cs`.

Per step, given a requested **terminal power** `P` (sign: **positive = charging**, negative = discharging — see §4):

```
P = U_terminal · I = (U0 + I·Ri) · I          // quadratic in current I
```
Solved as a quadratic for current `I`:
```csharp
solutions = VectoMath.QuadraticEquationSolver(Ri.Value(), U0.Value(), -powerDemand.Value());
current  = SelectSolution(solutions, powerDemand.Value());   // pick root with matching sign & within max current
```
[VECTO] `Battery.cs:Request`. If `Ri ≈ 0` it falls back to the linear `I = P/U0`.

Then:
```
batteryLoss = I · Ri · I          // = I²·Ri  (ohmic loss, always ≥ 0)
SoC(t+dt)   = (Capacity·SoC + I·dt) / Capacity    // Coulomb counting; +I charges
```
[VECTO] `Battery.cs:Request`.

**Key fact for the HDEV gap:** VECTO **always** computes `batteryLoss = I²·Ri` every step, in **both drive and regen**, and reports it as `P_reess_loss`. The HDEV "no battery loss while driving" note is a description of HDEV's *current* simplification, **not** of VECTO. VECTO has the loss; HDEV must add it to match. [VECTO] `Battery.cs:Request`, `DoWriteModalResults` (`ModalResultField.P_reess_loss`).

---

## 2. OCV — open-circuit voltage vs SoC  [VECTO]

`SOCMap` in `BatteryData.cs`:
- Entries `(SOC ∈ [0,1], BatteryVolts)`; `Lookup(soc)` = **linear interpolation** between bracketing SoC points, **clamped** at the ends (`FindIndex` returns first/last segment, no extrapolation; out-of-table **throws**). [VECTO] `BatteryData.cs:SOCMap`.
- `InternalVoltage => SOCMap.Lookup(PreviousState.StateOfCharge)` — U0 uses the **previous** step's SoC. [VECTO] `Battery.cs:InternalVoltage`.
- `NominalVoltage => SOCMap.Lookup(0.5)`. `StoredEnergy = SoC · Capacity · U0(SoC)`. [VECTO] `Battery.cs`.

**File format / units** (reader `BatterySOCReader.cs`, generic example `GenericBattery_243kWh.vbatv`):
```
SOC, V          <- header; SOC in PERCENT (reader divides by 100), V in volts
0, 673.5
10, 700.2
...
90, 742.2
100, 750.2
```
`SOC = row.ParseDouble("SoC") / 100; BatteryVolts = row.ParseDouble("V").SI<Volt>()`. [VECTO] `BatterySOCReader.cs:41-42,64,66`.

---

## 3. Internal resistance Ri — incl. pulse-duration dependence  [VECTO]

`InternalResistanceMap` in `BatteryData.cs`: entries per SoC, each holding a **list of (t_pulse, Ohm)** pairs. `Lookup(SoC, tPulse)`:
1. Interpolate linearly over SoC between bracketing entries;
2. Within each entry, interpolate linearly over **pulse duration** `t_pulse` (clamped at ends).
[VECTO] `BatteryData.cs:InternalResistanceMap.Lookup`, `InterpolateResistance`.

**Pulse duration `t_pulse`** is the *continuous time the battery has been charging/discharging in the same direction*. It resets to 0 whenever the sign of power demand flips:
```csharp
var tPulse = PreviousState.PowerDemand.Sign() == powerDemand.Sign()
    ? PreviousState.PulseDuration : 0.SI<Second>();
...
CurrentState.PulseDuration = tPulse + simulationInterval;   // accumulates in DoCommitSimulationStep
```
[VECTO] `Battery.cs:Request`, `DoCommitSimulationStep`. So Ri rises the longer a sustained pulse lasts (standard pulse-resistance behaviour).

**File format / units** (reader `BatteryInternalResistanceReader.cs`): three accepted shapes:
- 2 columns `SoC, Ri` → single resistance applied at all pulse durations (stored as `(0 s, Ri)` and `(1e9 s, Ri)`), i.e. **pulse-independent**. (Generic example `GenericBattery_243kWh.vbatr`: `SoC, Ri` with constant `0.04` Ω.) [VECTO] reader lines ~31-52.
- 4 columns `SoC, Ri-2, Ri-10, Ri-20` → pulse durations **2 / 10 / 20 s**. [VECTO] `col1`.
- 5 columns `SoC, Ri-2, Ri-10, Ri-20, Ri-120` → **2 / 10 / 20 / 120 s**. [VECTO] `col2`.
- `SoC` column is **percent** (÷100). Resistance may be in Ω or mΩ (`inputInMilliOhm` → `factor = 1000`). [VECTO] `BatteryInternalResistanceReader.cs:46,93, Fields`.

---

## 4. Current / power limits  [VECTO]

### Sign convention
**Positive current/power = charging; negative = discharging.** Confirmed by `SoC = (Capacity·SoC + I·dt)/Capacity` (positive I raises SoC) and the modal comment *"adding both terms because pos. current charges the battery!"* [VECTO] `Battery.cs:Request`, `DoWriteModalResults`.

### Max current (SoC-dependent)  [VECTO]
`MaxCurrentMap` (`BatteryData.cs`), reader `BatteryMaxCurrentReader.cs`:
```
SoC, I_charge, I_discharge     <- SoC percent; I_discharge stored NEGATIVE (×-1)
```
Linear interpolation over SoC, clamped. [VECTO] `BatteryMaxCurrentReader.cs:36-38, Fields` (`I_charge`, `I_discharge`).

### Max charge / discharge **current** per step  [VECTO]
Also limited by the SoC window and `dt`:
```csharp
MaxChargeCurrent(dt)    = Min( (MaxSOC − SoC)·Capacity/dt , MaxCurrent.LookupMaxChargeCurrent(SoC) )
MaxDischargeCurrent(dt) = Max( ((MinSOC − SoC)·Capacity/dt).LimitTo(...) , MaxCurrent.LookupMaxDischargeCurrent(SoC) )
```
So near the SoC limits the per-step current shrinks to not overshoot the window. [VECTO] `Battery.cs:MaxChargeCurrent/MaxDischargeCurrent`.

### Max charge / discharge **power**  [VECTO]
```csharp
MaxChargePower(dt)    = U0·I_ch + I_ch·Ri·I_ch
MaxDischargePower(dt) = Max( U0·I_dis + I_dis·Ri·I_dis ,  −U0/(4·Ri)·U0 )
```
The `−U0²/(4·Ri)` term is the **theoretical max power transfer** of a source+series-R (matched load) — caps discharge power even if current limit would allow more. [VECTO] `Battery.cs:MaxChargePower/MaxDischargePower`.

If a requested power exceeds these, VECTO returns an **overload** (`RESSOverloadResponse`) or **underload** (`RESSUnderloadResponse`) rather than clipping silently — the EM then re-limits torque (see 01 §3.3/3.4). [VECTO] `Battery.cs:PowerDemandExceeded`.

---

## 5. SOC window  [VECTO]
- `MinSOC`, `MaxSOC` ∈ [0,1] on `BatteryData`. Generic example `GenericBattery_243kWh_750V.vbat`: `SOC_min=10.0`, `SOC_max=90.0` (percent in file). [VECTO] `.vbat` body quoted below.
- `Initialize(initialSoC)` **throws** if initial SoC outside `[MinSOC, MaxSOC]`. [VECTO] `Battery.cs:Initialize`.
- `UseableStoredEnergy = CalculateBatteryEnergy(MinSOC, MaxSOC)` integrates `U0(SoC)·Capacity` over the usable window; `TotalStoredEnergy` over [0,1]. [VECTO] `BatteryData.cs:CalculateBatteryEnergy`.

Generic `.vbat` body:
```json
"Capacity": 324.0,  "SOC_min": 10.0,  "SOC_max": 90.0,
"MaxCurrentMap": "MaxCurrent.vimax",
"InternalResistanceCurve": "GenericBattery_243kWh.vbatr",
"SoCCurve": "GenericBattery_243kWh.vbatv",
"TestingTemperature": 20.0, "JunctionboxIncluded": false, "ConnectorsSubsystemsIncluded": false
```
`Capacity` is in **Ah** (stored as `AmpereSecond` after ×3600 in the reader). [VECTO]

---

## 6. Connection / system resistance  [VECTO]
`BatterySystemData.ConnectionSystemResistance` [Ω] (default 0). It is **not** applied inside `Battery.cs`; it is applied in the **ElectricSystem** between the battery and the consumers:
```csharp
var connectorLoss = currentEst * (ModelData?.ConnectionSystemResistance ?? 0) * currentEst;   // I²·R connector loss
```
[VECTO] `ElectricSystem.cs:67,97`. For a single generic battery it is 0 unless the pack declares junction-box / connector subsystems (`JunctionboxIncluded`, `ConnectorsSubsystemsIncluded`). [INFERRED from the `.vbat` flags both being `false` in the generic file.]

---

## 7. Battery system (multiple packs)  [VECTO]
`BatterySystemData`: series index + parallel `BatteryData`. System `Capacity` / stored energy aggregate across the string groups (min within a parallel group, sum across series). `BatterySystem.cs` wraps multiple `Battery` instances. `ChargeDepletingBattery` / `ChargeSustainingBatterySystem` = an **"infinity battery"** mode where SoC is held fixed (`soc = PreviousState.StateOfCharge`) — used for charge-sustaining / test configs. [VECTO] `BatteryData.cs`, `Battery.cs:Request` (`if (ModelData.ChargeDepletingBattery) soc = PreviousState...`).

---

## 8. Temperature handling  [VECTO]
- `TestingTemperature` is stored (e.g. 20 °C) but **not** used to modify Ri, U0, or limits in Declaration mode. There is **no temperature-dependent battery behaviour** in the lorry path — matches the HDEV gap note "No temperature or solar dependence for trucks". [VECTO] `.vbat` `TestingTemperature`; absence of any temperature term in `Battery.cs`/`BatteryData.cs`. [INFERRED: exhaustive read of both files shows no T dependence.]

---

## 9. SuperCap (for completeness)  [VECTO]
`SuperCapData` (`BatteryData.cs`) + `SuperCap.cs`: capacity [F], single Ri [Ω], min/max voltage, max charge/discharge current. Used by some hybrid/bus configs, not pure BEV lorries. [VECTO]

---

## 10. Modal outputs (battery)  [VECTO] (`Battery.cs:DoWriteModalResults`)
| field | meaning |
|---|---|
| `U0_reess` | OCV = `SOCMap.Lookup(SoC)` [V] |
| `U_reess_terminal` | `U0 + I·Ri` [V] |
| `I_reess` | current [A] (+ charge) |
| `REESSStateOfCharge` | SoC [-] |
| `P_reess_terminal` | terminal power = requested [W] |
| `P_reess_int` | `U0·I` [W] |
| `P_reess_loss` | `I²·Ri` [W] |
| `P_reess_charge_max`, `P_reess_discharge_max` | per-step limits [W] |

---

## 11. What HDEV needs to replicate this (M3.3)

Replace the exponential-taper charge model with:
1. **OCV map** `U0(SoC)` — linear interp, clamped, from `(SoC%, V)` table.
2. **Ri map** `Ri(SoC, t_pulse)` — linear interp over SoC and over pulse duration; support the 2/10/20(/120) s columns; track `t_pulse` and reset on sign flip.
3. **Quadratic solve** `P = (U0 + I·Ri)·I` for current; pick the sign-matching root within max current. Fall back to linear when Ri≈0.
4. **Coulomb counting** `SoC += I·dt/Capacity` (I>0 charges).
5. **Loss** `P_loss = I²·Ri` **every step, drive and regen** — closes the "no battery loss while driving" gap.
6. **Limits**: SoC-dependent max current map; per-step current clamped by `(MaxSOC−SoC)·Cap/dt`; max discharge power capped by `−U0²/(4·Ri)`; raise/flag on overload/underload.
7. **SoC window** `[MinSOC, MaxSOC]`; initial-SoC bounds check.
8. (Optional) connection-system resistance `I²·R` as a separate ElectricSystem-level loss.
9. Keep temperature **out** (match VECTO) — or add as a flagged non-VECTO layer if Danish-winter battery derating is wanted.

For a validation anchor, use `GenericBattery_243kWh.*` (324 Ah, 10–90% SoC, Ri 0.04 Ω const, OCV 673.5→750.2 V) from `PEV/GenericVehicleE2`. See 11-validation-data.md.

---

## 12. Open questions
- Does HDEV need the pulse-duration Ri dimension, or is a single Ri(SoC) acceptable for declaration-equivalent runs? (Generic files use constant Ri; the 2/10/20/120 s columns are for measured packs.)
- The `−U0²/(4·Ri)` discharge-power cap: does HDEV ever hit it in practice? Likely not with Ri=0.04 Ω and realistic currents, but needed for correctness near low SoC.
- Charging physics while **plugged in** (not driving) — does `Battery.cs` even run during charging? → see 04-charging.md (VECTO does not simulate depot charging; the same `Request` would apply if it did).

---

## 13. Unblocks spec task(s)
- **M3.3** — complete OCV + Ri + quadratic-current + Coulomb-counting spec, with exact file formats/units and the generic validation pack.
- **"no battery loss while driving" gap** — confirms VECTO *does* compute `I²·Ri` always; HDEV must add it (not a VECTO gap, an HDEV gap). Feeds the assumptions report wording and **M0.21 consumption**.
- **M3.1 / M3.2 (battery sizing)** — `Capacity` [Ah], `UseableStoredEnergy`, SoC window definitions.
- **M3.0 / M3.4 / M2.1 (charging stepper, dt argument)** — the `Request(absTime, dt, power)` signature and per-step current/power limits are the stepper HDEV charging must emulate.
- **M5.3 (validation)** — generic 243 kWh pack as a numeric anchor.
