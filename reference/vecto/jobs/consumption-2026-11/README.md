# VECTO runs for Bob: consumption review (13 Nov 2026)

Kiro cannot run VECTO. Only ONE question in the consumption review cannot be closed from the existing E2 `.vmod` files.
Everything else (order of losses, sign decisions, rotor inertia, regen speed limit, Cond/SP rules) was closed from the source code plus
the six E2 `.vmod` files (see the report, Part A and C).

## Run 1: mechanical drive PTO while the truck coasts  [OPEN, report Q6 / Q9]

**Question.** A drive PTO on the motor shaft (sweeper, mechanical body) keeps running while the truck coasts or rolls. VECTO's controller
switches the motor OFF in `Coast` and `Roll` (`BatteryElectricMotorController.cs` 44-47). Who then pays for the PTO power?
Option A: nothing (the PTO load is a drag on the drivetrain and the truck decelerates faster). Option B: the motor is switched on for the PTO.
HDEV's proposal (`consumption_engine_v_proposed`) assumes option B (conservative: it never under-counts the PTO energy).

**Steps (VECTO 5.1.6-RC, engineering mode, as in the PR #31 job (branch `aux-pto-review-2026-11`, folder `reference/vecto/jobs/aux-pto-2026-11/`)):**
1. Copy `reference/vecto/jobs/aux-pto-2026-11/BEV_G4_PTO_clean.vecto` and `.vveh` (PTO type: drive PTO with a constant power cycle).
   If the E2 generic vehicle (`Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2`, commit b8d6126) is preferred: copy `BatteryElectricVehicle_PTO.vveh`
   and set `PTO.CycleDriving` to a `.vptoc` with one constant line (ILLUSTRATIVE 3000 W) for the whole cycle.
2. Use a cycle with a long downhill (`LongHaul.vdri` has coasting rows; the Regional/Urban `.vmod` show `DriverAction` 4 = Coast).
3. Run TWICE: PTO off and PTO on, same cycle, same loading.
4. Output columns to read (both runs, `.vmod`, 1 Hz): `DriverAction`, `EM_E2_off`, `P_E2-em_el`, `P_E2-em_mech`, `P_gbx_in`, `P_wheel_in`, `v_act`, `P_REESS_T`.
   Sign convention: `P_REESS_T` negative = battery discharges; `P_E2-em_el` negative = motor draws electricity.
5. Rows to compare: those with `DriverAction` 4 (Coast) or 2 (Roll) and `EM_E2_off` = 1 in the PTO-off run.
   Option B is true if `EM_E2_off` becomes 0 and `P_E2-em_el` < 0 in the PTO-on run on those rows; Option A is true if the motor stays off and `v_act` falls faster.
6. Send back the two `.vmod` files and the `.vsum`.

## Not needed
* Lower regen limit run: the E2 generating limit (`P_E2-em_gen_max`, 24-250 kW) never binds on the six runs (report Part C, cause d). A run with a smaller motor would be a new vehicle, not a model question.
* Rotor inertia run: `P_E2-em_inertia_loss` in the six `.vmod` files already gives J = 0.4500 kg m2 (fit, report Part C).
