# VECTO runs for the aux / PTO review (12 Nov 2026) – for Bob to run

**Kiro cannot run VECTO in the sandbox.** These runs close open items 6 and 4 of the review
(`docs/research/aux-pto-review-2026-11.md`, §1.2): there is no MunicipalUtility `.vmod` in the repo, and the size of
the PTO-transmission torque loss for a BEV has only been *calculated*, never *seen* in a VECTO output.

- **VECTO version:** 5.1.6-RC (the version your six E2 `.vmod` files were written with).
- **Source read for the review:** `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`.
- **None of the files below has been opened in VECTO.** They are edits of the VECTO generic files
  (`Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/`), made with a JSON library so they are valid JSON.
  If VECTO refuses one, the error text tells you which field to change; see "If VECTO refuses" at the end.

## Why group 4 and not the E2 vehicle itself

`SegmentTable.csv` gives HDV group 2 only the missions Long haul, Regional delivery and Urban delivery. The E2
generic vehicle (`MassMax` 11.99 t) is group 2, so VECTO never runs **MunicipalUtility** for it, and the default
refuse PTO (`MunicipalUtility_PTO_generic.vptoel`) is only attached on that mission
(`DeclarationModeHeavyLorryRunDataFactory.cs:251`). Municipal exists for groups 4, 9 and 11 only. The smallest change
that reaches it is to raise `MassMax` to 18 t, which makes the same rigid 4x2 truck **group 4** (rigid 4x2, 16–99 t).
Everything else (axles, motors, battery, gearbox files) stays the E2 generic set.
Group 4 also gets the Municipal body weight (`MU4`) from `Body_Trailers_Weights.csv` automatically.

## Files in this folder

| File | What it is |
|---|---|
| `BEV_G4_PTO_clean.vveh` / `.vecto` | E2 PTO vehicle with `MassMax` = 18.0 and PTO type **None**. Use this for the stop-PTO placement and energy check (Run 1). |
| `BEV_G4_PTO_oilpump.vveh` / `.vecto` | Same, but keeps the generic file's mechanical PTO type "only the drive shaft of the PTO - multi-disc clutch, oil pump" (23.9 Nm in `PTO-tech.csv`). Use this for Run 2 (the PTO drag term, review Q10). |

## Setup (both runs)

1. Copy the whole VECTO folder `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/` to a working folder.
2. Copy the four files of this folder into it (they sit next to `AMT.vgbx`, `GenericBattery_243kWh_750V.vbat`, ...).
3. Open the `.vecto` job in the VECTO 5.1.6 GUI (Declaration mode). In the job window the "Cycles" list is fixed in
   declaration mode; VECTO runs every mission group 4 has: Long haul, Regional delivery, Urban delivery,
   **Municipal utility**, Construction (each Reference and Low loading). If you only want Municipal, untick the others in the
   "Missions / loadings" selection of the GUI if your build offers it; otherwise run all and use the Municipal file.
4. In the GUI options enable the **modal output** exactly as for your six E2 files (they carry `DriverAction`,
   `EM_E2_off` and `P_aux_*_el` columns, so those are already in the default list), and run twice:
   once with the **1 Hz** modal option (as for the E2 files) and once **without it** (native time steps).
   The native-step file shows the 3-phase stop (1 s idle / 23 s PTO / 1 s idle) un-smeared; the 1 Hz file averages
   inside each second.

## Run 1 – stop PTO on MunicipalUtility (declaration mode)  → `BEV_G4_PTO_clean.vecto`

What to check in the `MunicipalUtility` `.vmod` (both versions):

1. Number of stops with PTO: expect **96** (the `PTO` column of `MunicipalUtility.vdri` has 96 rows with value 1).
2. Standing time per PTO stop: expect **25 s** (2 s stop + 23 s PTO), PTO in the middle (1 s idle, 23 s PTO, 1 s idle).
3. Column that shows the PTO power: expect **`P_aux_PTO_CONSUM_el [kW]`** (the aux ID is `PTO_CONSUM`, `Constants.cs:65`, plus the
   `_el` suffix that `ElectricAuxiliaries.Initialize` adds, `ElectricAuxiliaries.cs:58`; the `P_aux_` prefix is what the other aux
   columns have). *This column name is inferred from the code, not seen – check the header.* Its sum in kWh should be
   `96 × 0.14993 = 14.393 kWh` (`partD1_municipal_summary.csv`).
4. `P_aux_COND_el [kW]` should be **0.55 kW during the 23 s PTO** (Cond stays on with the electric PTO,
   `Conditioning.cs:86`), and `EM_E2_off` ≈ 1 in that window. If Cond is 0 there, the review's rule (c) is wrong.
5. `P_aux_STP_el [kW]` must be 0 while standing (including the PTO window).
6. Send back both `.vmod` files and the `.vsum`. The review's `reference_copy.py: consumption_step6_v_pto1nov` is then compared to
   them row by row (script to be written once the file exists; the rows to compare are listed in `partD1_municipal_per_stop.csv`).

## Run 2 – PTO transmission torque loss  → `BEV_G4_PTO_oilpump.vecto`

Same job but with the mechanical PTO type. In this version of VECTO a BEV that declares a PTO type gets a constant torque loss in front of the
motor (`PowertrainBuilderBase.cs:352-356`, `PEVPTO.cs`), on every mission, whenever a gear is engaged and the shaft turns.
The review calculates 15.8 kWh per 100 km (≈ 15 % of the Regional battery energy) for the 23.9 Nm type, **if** the torque acts at motor speed
(`partA_q10_unmodelled_terms.csv`). What to check: the column that VECTO writes for this loss is
`P_PTO_TRANSM` (ID `PTO_TRANSM`, `Constants.cs:55`; prefix `P_` per `Constants.cs:51`; header not seen, check it); compare Regional-delivery battery energy (`P_REESS_T` sum) of Run 2 against Run 1
(same mission, same group-4 vehicle): the difference is the real size of the term. Report it per mission in kWh/100 km.
If the difference is near 0, the calculation in the review was wrong and the term can be dropped.

## Run 3 (optional) – drive PTO / road sweeper, engineering mode

Engineering mode only (`PowertrainBuilderBase.cs:325, 339`). Needed only if you want to see VECTO's drive-PTO rows.

1. Engineering-mode job from the E2 BEV vehicle (GUI: new job, Engineering mode, same components).
2. Vehicle file keys: `"GearDuringPTODrive": 1` and `"EngineSpeedDuringPTODrive": <rpm>` (both are required when the cycle has road-sweeping rows,
   `EngineeringModeVectoRunDataFactory.cs:183-190`, `JSONVehicleData.cs:409,411`).
3. Cycle: a `.vdri` with columns `<s>, <v>, <grad>, <stop>, <PTO>, <PTO_Power>` where `PTO` = 2 (road sweeping) on the rows that sweep and `PTO_Power`
   in **kW** (`DrivingCycleDataReader.cs:370, 1044`). Make a short route (a few km, two stops) so the file is easy to read.
4. For a **time-based drive profile** (`PTO` = 3, "while drive") put a csv with columns `<t>` and `<PTO_Power>` [kW] in the vehicle's
   `PTO.CycleDriving` field (`JSONVehicleData.cs:603-611`). The file extension is not constrained in the source (`.vptor` is not found in the code).
   Make **two** `PTO` = 3 rows closer together than the profile length to see the error
   "Additional PTO activation during drive requested while PTO still active!" (`PTODriveAuxiliary.cs:26`).
5. Columns to look at in the `.vmod`: the road-sweeping / drive PTO power columns (IDs `PTO_RoadSweeping`, `PTO_DuringDrive`, `Constants.cs:56-57`, written with the prefix `P_` (`Constants.cs:51`) – column header not seen, check it) and the
   motor columns `P_E2-em_el`, `P_E2-em_mech`, to see that the drive PTO is a **mechanical** load on the motor shaft (so motor losses apply).

## If VECTO refuses

- "…does not match any vehicle class / missions" → check `MassMax` (must be ≥ 16 t for group 4) and that `AxleConfig` is still 4x2.
- Start-up / power validation error with 18 t → raise the motor `Count` in the `ElectricMachines` block of the `.vveh`
  (E2: 2 × 125 kW) – note what you changed in the review.
- PTO errors: declaration mode does not accept PTO cycle files (that is why `BatteryElectricVehicle_PTO_invalid.vveh` in the VECTO folder is called "invalid");
  the cycle comes from the built-in `MunicipalUtility_PTO_generic.vptoel` (`PTODataAdapter.cs:46-68`). Keep `Cycle`, `CycleEPTO`, `CycleDriving` empty.
