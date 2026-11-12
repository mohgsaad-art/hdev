# VECTO runs for Bob: force-engine review (12 Nov 2026)

**Status: written, NOT run.** VECTO cannot run in the review sandbox. The job files below were not validated by a VECTO run, so build them
in the GUI with the steps given (the hand-written `.vecto` JSON route was judged too risky).
VECTO version for all runs: **5.1.6-RC** (same as the existing `.vmod` files), generic E2 BEV
(`Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BEV_E2.vecto` in `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`).

Command-line switches (from `VectoConsole/Program.cs` lines 100-102 and 314-316 at b8d6126):
`-mod` writes modal data, `-1Hz` converts it to 1 Hz, `-act` writes the **actual** (un-averaged, variable-step) modal data, `-eng` = engineering mode.

Only three runs are asked for. Each closes one open item that the review could not close from files alone.

## Run A: raw (non-1 Hz) modal data. Closes [OPEN] "stop / start rows" (report Q7, Q8, Part C)
Why: in the 1 Hz `.vmod`, the `P_*` columns are time-averages of the internal steps, but `v_act`, `acc`, `dist` are rebuilt by `ModalData1HzFilter`
(`OutputData/ModFilter/ModalData1HzFilter.cs` lines 46-180). In the seconds around a stop, `P_veh_inertia` and the speed columns do not match each other
(example: Regional ReferenceLoad, t = 184 s: `P_veh_inertia` = -4943 W but `M*acc*v_act` = -1260 W; the segment sums are still 0). The raw file shows which side is right.
Steps (declaration mode, same job as before):
1. Open `BEV_E2.vecto`, run Regional + Urban, **ReferenceLoad** only (VECTO declaration run gives all missions; keep only these two `.vmod`).
2. Console: `VectoCmd.exe -mod -act "BEV_E2.vecto"` (do **not** add `-1Hz`).
3. Keep the files as `BEV_E2_RegionalDelivery_ReferenceLoad_ACT.vmod` and `..._UrbanDelivery_..._ACT.vmod`.
Columns needed: `time, dt, dist, v_act, acc, grad, altitude, Gear, P_trac, P_veh_inertia, P_roll, P_air, P_slope, CdxA_eff, P_wheel_in, P_wheel_inertia, P_E2-em_inertia_loss`.
Expected if the review is right: summing `P_*` x `dt` over the raw rows gives the same trip energies as the 1 Hz file (to 1e-4 kWh); raw rows allow a 0.5 s force_engine test (Part E).

## Run B: rotor inertia set to 0. Closes Q5 (where the rotor term lives)
Why: source says the rotor term is applied on the motor side (`ElectricMotor.cs` lines 97-98, 186-196, 297, 615), not in `P_wheel_in`. A run without it proves it.
Steps (engineering mode, because the declared motor file is hashed):
1. Copy the folder `GenericVehicleE2` to a work folder. In `GenericEMotor_125kW_485Nm.vem` set `"Inertia": 0.225` -> `"Inertia": 0.0`.
2. Open `BEV_E2.vecto` in the VECTO GUI, **File > Convert to engineering mode** (or load the vehicle in engineering mode), cycle: `RegionalDelivery.vdri` and `UrbanDelivery.vdri` from `reference/vecto/resources/MissionCycles`, loading = the ReferenceLoad value (3019.5882 kg), same auxiliaries as the declaration job.
3. Run with `-eng -mod -1Hz` (engineering mode implies `-mod`).
Expected: `P_wheel_in`, `P_trac`, `P_wheel_inertia` identical to the declaration run (to rounding); `P_E2-em_inertia_loss` = 0; battery energy lower by roughly the rotor-inertia share (the review sizes the rotor term at 0.228 kWh positive Regional, 1.22 kWh Urban at the motor shaft).
If `P_wheel_in` changes, the review's Q5 answer is wrong. Please report that.

## Run C: steep grade. Closes Q1 (angle conversion)
Why: at the E2 cycles the grade conversion `sin(atan(G))` vs `G` is below 0.01 % of wheel energy; a 10 % hill makes it visible (0.5 %).
Steps (engineering mode as in Run B, original motor file):
1. Cycle: `steep_grade_pm10.vdri` in this folder (3 km at +10 %, 3 km at -10 %, 50 km/h target).
2. Loading 3019.5882 kg, `-eng -mod -1Hz`.
Expected [CALC, g = 9.80665, M = 9589.5882 kg]: on a cruising second at +10 %, `P_slope / (M*g*v*0.10)` = 0.99504 (`sin(atan 0.1) / 0.1`), not 1.000; `P_roll / (Crr_eff*g*M^0.9*v)` = 0.99504 (`cos(atan 0.1)`).
Also expected: `grad` column prints 10.000 (it is `tan(angle) * 100`, `DistanceBasedDrivingCycle.cs` line 60).
