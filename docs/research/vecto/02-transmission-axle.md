# 02 — Transmission & axle losses for BEV lorries

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**.

---

## 1. Driveline topologies for BEV lorries  [VECTO]
`PowertrainPosition.BatteryElectricE2/E3/E4` = EM position (E2 before gearbox, E3/E4 nearer the axle). Gearbox classes used:
- **Single-speed** / **multi-speed AMT** (`AMT.vgbx` in the generic job) — standard `Gearbox`/`CycleGearbox` with a per-gear `TransmissionLossMap`.
- **APT-N** (`APTNGearbox.cs`) — automatic planetary (torque-converter-less N variant).
- **IEPC** (integrated electric powertrain): `IEPCGearboxSingleSpeed.cs`, `IEPCGearboxMultipleGears.cs`, `IEPCGearbox.cs` — the gearbox is part of the integrated machine.
- **BEVCycleGearbox** (`BEVCycleGearbox.cs`): subclass of `CycleGearbox` used in **measured-speed / cycle (time-run)** BEV simulations — selects the next gear ratio when disengaged. [VECTO] class header.

Axle gear (`Axlegear`) sits between gearbox and wheels (`Axle_4x2_LH.vtlm` / `.vtlm` loss map in the generic job).

---

## 2. How losses are applied  [VECTO]
Every transmission stage (gearbox gear, axle gear, EM-ADC) carries a **`TransmissionLossMap`** that converts torque in↔out with a torque loss that depends on (input speed, input torque). The EM applies it via `ConvertEmTorqueToDrivetrain` / `ConvertDrivetrainTorqueToEm` (see 01 §5); gearbox/axle components do the same in their `Request`. The loss map is a 2-D grid (speed × torque → torque loss) interpolated like other maps. [VECTO] `TransmissionLossMapReader.cs`, `ElectricMotor.cs`.

**BEV gearbox/axle losses use the SAME loss-map machinery as diesel** — there is no BEV-specific loss model. A BEV job just supplies `.vtlm` loss maps for its gears/axle. [INFERRED from the generic BEV job using ordinary `.vgbx` + `.vtlm` files.]

---

## 3. Constant-efficiency fallback  [VECTO]
When a stage is given a single **efficiency** instead of a measured map, `TransmissionLossMapReader.Create(efficiency, gearRatio, gearName)` builds a flat loss map: torque loss = `(1 − efficiency)·|T|` (constant fraction), with validation that `0 < efficiency ≤ 1` (else throws). [VECTO] `TransmissionLossMapReader.cs:203-227`.
```
lossTorque = (1 − η)·T    (same fraction in drive and over-run)
```
This is the structure behind the HDEV placeholder gearbox efficiency **0.98**.

---

## 4. Generic / standard values  [VECTO]
- EM mechanical transmission (ADC) efficiency: **1.0** if no ADC (`ElectricMachineDefaultMechanicalTransmissionEfficiency`, `DeclarationData.cs:119`); generic bus EM ADC: **0.98** (ratio==1) / **0.96** (ratio≠1) (`GenericBusElectricMotorData.cs`). (See 01 §5.)
- IEPC generic **axle-gear efficiency = 0.96** (`GenericBusIEPCData.cs:23 GenericAxleGearEfficiency`). [VECTO]
- Gear/axle measured loss maps are vehicle-specific (`.vtlm`); there is no single shipped "standard gearbox efficiency" constant for lorries other than these generic/IEPC values. [INFERRED by grep.]

---

## 5. What HDEV needs to replicate
1. A transmission-loss stage per driveline element (gearbox + axle), either a 2-D loss map or the constant-efficiency fallback `loss = (1−η)·|T|`.
2. For the placeholder path: gearbox η = 0.98 (HDEV placeholder, labelled a gap), axle per the generic value if modelled.
3. IEPC/single-speed vs multi-speed only matters for ratio selection; loss handling is identical.
4. The EM-ADC loss (01 §5) is separate from gearbox/axle loss — keep distinct.

---

## 6. Open questions
- Does the HDEV reference BEV use a measured axle `.vtlm` (from the generic job) or a constant efficiency? If grounding to the generic job, read `Axle_4x2_LH.vtlm`.
- Is HDEV modelling a gearbox at all, or folding driveline loss into the single 0.98 placeholder? (Decision for Bob; docs treat 0.98 as a placeholder gap.)

---

## 7. Unblocks spec task(s)
- **req §1.5.4 / gap list** — the gearbox placeholder 0.98 maps to VECTO's constant-efficiency loss map `(1−η)·|T|`; axle generic efficiency 0.96 (IEPC) available if a real value is wanted.
- **M0.21 (consumption)** — confirms driveline loss is torque-based, applied before the EM map; informs where HDEV should place the gearbox/axle efficiency in the power→energy chain.
- **M0.19 (power_step)** — transmission losses feed the wheel→EM power path.
