# 08 — Cycles & missions (columns, distance/time/measured, grade vs altitude, stops)

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**. Serves **task M0.12** (grade/altitude).

> **⚠ CORRECTION (see `13-followups.md` §1):** §4's conclusion "declaration cycles use `<grad>` directly; no secant needed; M0.12 matches VECTO" is **WRONG**. The force balance uses an **altitude secant per step** (`DistanceBasedDrivingCycle.cs:412-433`): `<grad>` is integrated into an altitude profile at load, then grade is re-derived as `atan((altitude(prev+ds)−altitude(prev))/ds)` each step. **M0.12 is NOT resolved.** Read §4 and the Top-10 item with this correction.

---

## 1. Declaration mission cycles  [VECTO]
`Resources/Declaration/MissionCycles/*.vdri`:
- **Lorries**: `LongHaul`, `RegionalDelivery`, `UrbanDelivery`, `MunicipalUtility`, `Construction` (the 5 in the HDEV reference bundle).
- **Buses**: `HeavyUrban`, `Urban`, `Suburban`, `Interurban`, `Coach`.
All are **distance-based** (`<s>` first column). [VECTO] file list.

Header examples:
- `LongHaul.vdri`: `<s>,<v>,<grad>,<stop>,HW`
- `MunicipalUtility.vdri`: `<s>,<v>,<grad>,<stop>,<PTO>`
- `UrbanDelivery.vdri`: `<s>,<v>,<grad>,<stop>` (no HW/PTO)

Columns: `s` distance [m], `v` target speed [km/h], `grad` road gradient [%], `stop` stopping time [s], `HW` highway flag [0/1], `PTO` PTO-active flag. [VECTO]

---

## 2. All cycle column fields  [VECTO] (`DrivingCycleDataReader.cs:342-382`)
`s` distance, `t` time, `v` speed, `grad` gradient%, `stop` stop time, `n`/`n_eng` engine speed, `gear`, `Pwheel` wheel power [kW], `P_PTO` PTO power [kW], `P_PTO_el` electric PTO [kW] (07 §2), `Padd` additional aux [kW], `Padd_hv` HV additional [kW], `Pel_fan` fan [kW], `vair_res`/`vair_beta` crosswind air speed/yaw, `HW` highway, `PTO`/`PTO_Power` PTO-during-drive, plus emission columns (`CO2`, `NOx`, …).
**`AUX_<id>` prefix** (`Constants.Auxiliaries.Prefix = "AUX_"`, Constants.cs:51): per-row auxiliary supply power columns, parsed by `row.GetAuxiliaries()` (kW→W). These let a cycle carry per-row aux power (06 §1). [VECTO]

---

## 3. Cycle types — distance vs time vs measured speed  [VECTO]
`DrivingCycleDataReader.DetectCycleType` auto-detects by header (`CycleType`): `DistanceBased`, `PTO`, `EPTO`, `PTODuringDrive`, `PWheel`, `MeasuredSpeedGear`, `MeasuredSpeed`, `EngineOnly`, `VTP`. [VECTO] lines 54-88.

Required columns per type:
- **DistanceBased** (declaration): requires `s`, `v` (grad/stop/HW optional). [VECTO] `DistanceBasedCycleDataParser.ValidateHeader`.
- **MeasuredSpeed** (a GPS/measured run): requires only **`t`, `v`**; allowed: `Padd`, `grad`, `vair_res`, `vair_beta`, `Padd_hv`, `AUX_*`. **No distance, no gear needed** — VECTO integrates distance from speed×time. [VECTO] `MeasuredSpeedDataParser.ValidateHeader` (lines 741-763). Grade defaults to 0 if absent (`ParseDoubleOrGetDefault`).
- **MeasuredSpeedGear**: `t, v, n, gear` (+ optional `tc_active, grad, Padd, vair_*, AUX_*`). [VECTO]
- **PWheel**: wheel-power-prescribed cycle. [VECTO]

**What a GPS/measured cycle needs (for M4.5 GPS adapter):** minimally time + speed; grade optional (0 default); stops are implicit (v=0 rows). [VECTO]

---

## 4. Grade vs altitude handling (task M0.12)  [VECTO]
**VECTO reads road gradient DIRECTLY from the `<grad>` column** and uses it in the physics; **altitude is DERIVED from grade**, not the other way round.

- Distance-based (`FilterDrivingCycleEntries`, `DrivingCycleDataReader.cs:215-242`):
  ```csharp
  altitude += (entry.Distance − distance) · entries[i−1].RoadGradientPercent / 100.0;
  ```
  Grade is read directly (`RoadGradient = InclinationToAngle(grad/100)`); altitude is the running integral `Σ Δs·grad%/100` — for **reporting only**. [VECTO]
- Time-based (`ComputeAltitudeTimeBased`, lines 193-206):
  ```csharp
  altitude += v · (t − lastTime) · RoadGradient;
  ```
- `RoadGradientPercent = tan(RoadGradient)·100`; `RoadGradient = InclinationToAngle(grad/100)` i.e. `atan(grad/100)`. [VECTO] `DrivingCycleData.cs:193`, `DrivingCycleDataReader.cs`.

**M0.12 answer:** VECTO does **NOT** derive grade from an altitude secant in the declaration distance cycles — it reads `<grad>` (percent) directly and integrates it to altitude. The "VECTO altitude-secant" the task worries about applies when the *input* is altitude (some engineering cycles); but the **declaration `.vdri` cycles carry grade directly**, so HDEV using the flat `grade_pct` column matches VECTO on these cycles. If HDEV ever ingests an altitude profile, it must then differentiate altitude→grade (secant) to match. Difference on the reference `.vdri`: **none** (both read grade directly). [VECTO]

---

## 5. Stop handling + does any cycle end with stop>0?  [VECTO]
- A row with `v=0` and `stop>0` = the vehicle halts for `stop` seconds. `stop>0` with `v>0` → **throws** ("stop time specified but target-speed > 0"). [VECTO] `FilterDrivingCycleEntries`.
- First row with v=0 and stop=0 gets `stop=1 s` forced. [VECTO] line ~220.
- At each v=0 entry VECTO **duplicates** the distance point with 0 waiting time and the next segment's target speed (to model the drive-away). PTO stays active only for road-sweeping. [VECTO] lines 246-254.

**Do cycles end with a stop>0 row? YES.** [VECTO] tails:
- `LongHaul.vdri` ends: `100185,0,-0.257587,1` → **v=0, stop=1** (ends stopped).
- `MunicipalUtility.vdri` ends: `11240,0,-0.3,3,0` → **v=0, stop=3** (ends with a 3 s stop).
- `UrbanDelivery.vdri` ends: `100000,0,0,0` → v=0, stop=0 (ends at rest, no dwell).

This matters for the HDEV driver-model/payload "stop rows then fill" design: **the declaration cycles do end with a zero-speed row, and MunicipalUtility ends with a non-zero stop time.** [VECTO] — directly relevant to M0.8 (momentary-stop) and the payload stop-table.

---

## 6. What HDEV needs
1. Parse `.vdri` distance cycles: `s, v, grad%, stop, HW/PTO`; use grade directly (M0.12).
2. Support measured-speed (`t, v`) cycles for GPS input (M4.5): integrate distance, grade optional.
3. Handle `AUX_*` per-row aux columns if present (06).
4. Stop rows: v=0 + stop; reject stop>0 with v>0; handle the final stop row (LongHaul stop=1, MU stop=3).
5. Altitude is derived from grade for reporting; HDEV only needs grade for the force balance.

---

## 7. Open questions
- Does the HDEV reference `.vdri` loader already read `<grad>` directly? (It should; confirm in the M0 driver-model audit.)
- MunicipalUtility `<PTO>` column semantics (activity enum: inactive / road-sweeping) — ties to 07.
- The GPS zero-speed threshold for stop detection (M4.5) is unsourced in VECTO; measured-speed cycles just use v=0 rows. HDEV must pick/flag a threshold.

---

## 8. Unblocks spec task(s)
- **M0.12** — confirmed: declaration `.vdri` cycles carry grade directly; HDEV flat `grade_pct` matches VECTO (no secant needed for these). Secant only if ingesting altitude.
- **M0.8 (momentary stop)** — VECTO forces first v=0/stop=0 to stop=1 s and duplicates stop points; cycles end with v=0 rows (LongHaul stop=1, MU stop=3).
- **M4.4 / M4.5 (VDRI / GPS adapters)** — exact `.vdri` columns and measured-speed required columns (`t,v`).
- **payload stop-rows design** — confirmed cycles end with a zero-speed (and MU, a non-zero-stop) row.
- **M0.9 / 06 (AUX_ columns)** — per-row aux carried via `AUX_` prefix.
