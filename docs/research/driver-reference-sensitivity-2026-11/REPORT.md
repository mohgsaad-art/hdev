# What does the driver's fixed reference vehicle cost? (10 Nov 2026)

**Short answer for Bob:** running the driver once at the reference vehicle changes battery kWh/km by **at most about 0.4 % on RegionalDelivery and about 1.3 % on UrbanDelivery** for realistic E2 loads (empty to TPMLM, −10 to +30 °C, 0 to 8 m/s). Including the two "impossible" masses (0.5 × and 1.5 × m_ref) the worst case is 0.40 % / 1.89 %. **Mass is the input that matters.** Air density and wind are each below 0.25 %.

Everything below is produced by `run_sensitivity.py` (`VECTO_SRC=... python run_sensitivity.py`). Raw data: `results_one_factor.csv`, `results_corners.csv`, `timing.csv`, `gate.csv`, `run_log.txt`.

## 1. Gate and the section 4 re-run

Gate = `run_steps.py` run unchanged (Chain S, variant V1 E2 drag table, reference load). Tolerance ±0.0005.

| Cycle | Target | `run_steps.py` result | Gate |
|---|---|---|---|
| RegionalDelivery | 0.9749 | **0.9749** | PASS |
| UrbanDelivery | 0.8502 | **0.8502** | PASS |

Target values are from `docs/research/drag-default-test-2026-11/step3_kwh_per_km.csv` lines 3 and 15. After running, `git status` showed no change to that folder, so every CSV `run_steps.py` writes is identical to the committed one.

**Section 4 edit.** In my copy `_driver_dragtable.py`, `coast_distance` line 60 now reads `interp1(v, drag_v, drag_F)` (it was `v_avg`). That is the only line that differs (`diff` against the original). Re-run through the same `run_steps.py` functions:

| Cycle | Before (drag at v_avg) | After (drag at v) | Change |
|---|---|---|---|
| RegionalDelivery | 0.9749 | **0.9746** | −0.0003 |
| UrbanDelivery | 0.8502 | **0.8498** | −0.0004 |

All sensitivity runs use the edited driver. The reference case of my own energy step (driver A, m_ref, T_ref, 3 m/s) gives 0.9746 and 0.8498, the same as the edited `run_steps.py` run. So the sensitivity energy step ties back to the gate chain.

## 2. Headline tables

Columns: A = reference driver, B = matched driver ("truth"), error = (A − B)/B. "Largest single input" = which one-at-a-time driver (B_mass, B_rho, B_cdxa) moves the answer most; the three numbers in brackets are the error of A against each of them (mass / rho / cdxa). C = no-coasting driver, C vs B = (C − B)/B.

Rows with the reference value (m_ref, T_ref, 3 m/s) are the reference case and are exactly 0 by construction.

### RegionalDelivery

| case | A kWh/km | B kWh/km | error A vs B % | largest single input (mass / rho / cdxa) | C vs B % | note |
|---|---|---|---|---|---|---|
| mass 0.5 × m_ref (4795 kg) | 0.8477 | 0.8506 | −0.340 | mass (−0.340 / 0.000 / 0.000) | −0.063 | physically impossible for E2 (below empty mass) |
| mass empty (6570 kg) | 0.8944 | 0.8967 | −0.260 | mass (−0.260 / 0.000 / 0.000) | −0.169 | |
| mass m_ref (9590 kg) | 0.9746 | 0.9746 | 0.000 | none (reference) | −0.186 | |
| mass TPMLM (11990 kg) | 1.0394 | 1.0430 | −0.344 | mass (−0.344 / 0.000 / 0.000) | −0.704 | |
| mass 1.5 × m_ref (14384 kg) | 1.1050 | 1.1080 | −0.275 | mass (−0.275 / 0.000 / 0.000) | −0.788 | physically impossible for E2 (above TPMLM) |
| temp −10 °C | 1.0322 | 1.0326 | −0.034 | rho (0.000 / −0.034 / 0.000) | −0.167 | |
| temp T_ref (23.98 °C) | 0.9746 | 0.9746 | 0.000 | none (reference) | −0.186 | |
| temp +30 °C | 0.9658 | 0.9658 | +0.001 | rho (0.000 / +0.001 / 0.000) | −0.193 | |
| wind 0 m/s | 0.9395 | 0.9399 | −0.043 | cdxa (0.000 / 0.000 / −0.043) | −0.276 | |
| wind 3 m/s | 0.9746 | 0.9746 | 0.000 | none (reference) | −0.186 | |
| wind 8 m/s | 1.0890 | 1.0897 | −0.071 | cdxa (0.000 / 0.000 / −0.071) | −0.147 | |

### UrbanDelivery

| case | A kWh/km | B kWh/km | error A vs B % | largest single input (mass / rho / cdxa) | C vs B % | note |
|---|---|---|---|---|---|---|
| mass 0.5 × m_ref (4795 kg) | 0.6287 | 0.6377 | −1.413 | mass (−1.413 / 0.000 / 0.000) | −0.096 | physically impossible for E2 (below empty mass) |
| mass empty (6570 kg) | 0.7075 | 0.7135 | −0.834 | mass (−0.834 / 0.000 / 0.000) | −0.225 | |
| mass m_ref (9590 kg) | 0.8498 | 0.8498 | 0.000 | none (reference) | −0.255 | |
| mass TPMLM (11990 kg) | 0.9712 | 0.9665 | +0.491 | mass (+0.491 / 0.000 / 0.000) | −0.249 | |
| mass 1.5 × m_ref (14384 kg) | 1.0976 | 1.0847 | +1.187 | mass (+1.187 / 0.000 / 0.000) | +0.092 | physically impossible for E2 (above TPMLM) |
| temp −10 °C | 0.8718 | 0.8729 | −0.123 | rho (0.000 / −0.123 / 0.000) | −0.224 | |
| temp T_ref (23.98 °C) | 0.8498 | 0.8498 | 0.000 | none (reference) | −0.255 | |
| temp +30 °C | 0.8464 | 0.8462 | +0.030 | rho (0.000 / +0.030 / 0.000) | −0.250 | |
| wind 0 m/s | 0.8320 | 0.8312 | +0.108 | cdxa (0.000 / 0.000 / +0.108) | −0.287 | |
| wind 3 m/s | 0.8498 | 0.8498 | 0.000 | none (reference) | −0.255 | |
| wind 8 m/s | 0.8964 | 0.8985 | −0.240 | cdxa (0.000 / 0.000 / −0.240) | −0.170 | |

What this says:
- Mass dominates. A driver run at m_ref over-coasts a light truck and under-coasts a heavy one, so the sign flips between cycles (Regional always slightly negative, Urban negative when light, positive when heavy).
- Temperature (rho) and wind (cdxa) each stay below 0.25 % on their own.
- Regional errors are not smooth in mass (−0.26, −0.34, −0.28 for empty, TPMLM, 1.5 ×). The driver is a rule-based simulation, and a small shift in a coast or brake start point moves a few seconds of the trip. Treat differences of about 0.1 % as noise.
- The no-coasting driver C is within 0.8 % of B everywhere. In this model, with the E2 drag table, coasting is only 1.7–4.1 % of moving time on these cycles, so it is worth little energy.

## 3. Worst corners

16 corners per cycle (mass × temperature × wind), full list in `results_corners.csv`.

| Cycle | Worst of all 16 | Worst with realistic masses (empty, TPMLM) |
|---|---|---|
| RegionalDelivery | 0.5 × m_ref / −10 °C / 8 m/s: **−0.401 %** (A 1.0363, B 1.0405), physically impossible for E2 | empty / −10 °C / 8 m/s: **−0.388 %** |
| UrbanDelivery | 0.5 × m_ref / −10 °C / 8 m/s: **−1.888 %** (A 0.7039, B 0.7175), physically impossible for E2 | empty / −10 °C / 8 m/s: **−1.311 %** |

Corner error ranges: Regional −0.401 % to −0.089 %; Urban −1.888 % to +1.295 %. In 31 of 32 corners the largest single input is mass; in one (Regional, 1.5 × m_ref / +30 °C / 8 m/s) it is cdxa.

## 4. Per-run checks (A, B, C)

Full columns for every case are in the CSVs (coast %, braking %, regen kWh, trip time, max |Δv| vs B). Ranges, and how they are defined:

| | RegionalDelivery | UrbanDelivery |
|---|---|---|
| Route length | 100.0 km (all runs) | 99.9996 km (all runs) |
| Trip time A (s) | 5885 | 13576 |
| Trip time B (s), over all cases | 5884–5887 | 13560–13586 |
| Trip time C (s) | 5887 | 13560 |
| Coast share A / C (% of moving time) | 1.65 / 0 | 2.70 / 0 |
| Braking share A / C (%) | 7.67 / 7.88 | 26.02 / 26.58 |
| Regen energy A at m_ref (kWh) | 5.08 | 31.42 |
| Max \|Δv\| A vs B (km/h), over all cases | 0 – 5.7 | 0 – 16.0 |
| Max \|Δv\| C vs B (km/h), over all cases | 2.2 – 6.4 | 2.6 – 16.0 |

- Coast share = rows in mode 3 divided by rows not in mode 0 (stop). Braking share = mode 4 the same way.
- Max |Δv| compares speed on a 10 m distance grid up to the shorter route. It is a single worst point, so one shifted brake or stop point can show 16 km/h while the energy barely moves. Trip times agree to within 0.2 %.
- Regen is the negative part of battery power from Chain S, aux not included.
- The coast share in B changes a lot with mass (Regional TPMLM: A 1.65 % vs B 4.13 %), but energy changes by only 0.34 %.

## 5. Timing

Machine: Intel Xeon Platinum 8488C, 8 logical CPUs (`/proc/cpuinfo`), Python 3.11.15, numpy 2.4.6, single thread, no warm-up run. Mean of 5 runs, wall clock (`time.perf_counter`). Chain S is built once before timing, so its set-up is not counted.

| Cycle | `driver_model`, reference, coasting on (s) | Energy step: force + wheel power + Chain S + aux (s) |
|---|---|---|
| RegionalDelivery | 0.056 (min 0.0545, max 0.0577) | 0.0015 |
| UrbanDelivery | 0.132 (min 0.1274, max 0.1344) | 0.0042 |

Rerunning the driver for every driving day, 250–365 days per vehicle, costs about 14–20 s (Regional) or 33–48 s (Urban) per vehicle per route on this machine (250 and 365 times the mean driver time). Run once, the driver is a one-off 0.06–0.13 s. The energy step is about 31–37 times cheaper than the driver. Whether the extra cost is worth it is for Bob to judge, given the errors above.

## 6. Choices I made

1. **Yaw clamp:** `beta_limit = None` (VECTO behaviour) for every wind level, the same setting the harness uses for the declaration table (`hdev_test_harness_v1.7.py` line 213). The harness uses 10° (`BETA_LIMIT_YEAR`, line 54) only for real-wind year runs. I used one setting everywhere so that 3 m/s is exactly the reference. It only matters for the 8 m/s cases.
2. **Crosswind function:** `src/engine/crosswind_engine.py` called as in harness `cdxa_table` (lines 206–211): `dh = height/10`, 10° steps, height 3.75 m, `h_ref` 4 m, Hellmann 0.2. For driver A this table equals `tests/driver_model/_vecto_vehicle.CDXA_REF` to 4e-15 m².
3. **Rolling resistance, not unified (open item, as asked):** the driver uses `crr_total_vecto(coast_mass)`. The energy step uses `force_engine` with `CRR_EFF` and `mass**BETA` (BETA 0.9). At a given mass the two give the same force. In the one-at-a-time driver B_mass, Crr follows the case mass together with `coast_mass` (it is a function of mass).
4. **`theta_red` = 0 in the energy step**, as in `run_steps.wheel_power`, so the reference case ties to the gate. Wheel inertia is in the driver only (`m_red_wheels`). The harness passes `THETA_WHEELS` to `force_engine` (line 246); I did not, to keep the gate link. This is the same for A, B and C, so it cannot create an A–B difference, but absolute kWh/km would be a little higher with it.
5. **Aux:** the constant per-mission value from `run_steps.py` line 41 (Regional 1983 W, Urban 1769 W), added for all rows of the trip. Not scaled with temperature.
6. **Energy step copy of `run_steps`:** same regen rule (`use` mask, 5 km/h no-regen limit, `run_steps.py` line 48), gear 2 fixed, dt from `np.diff(T)`.
7. **Temperature enters only through air density** (and nothing else: no HVAC, no battery). `rho = P_AIR / (R_AIR (T + 273.15))`, `P_AIR = 101325`, `R_AIR = 287.05` (harness line 55). `T_ref = 23.977 °C` gives rho 1.188 (checked in the log).
8. **Masses:** empty = `VV.M_VEHICLE` = 6570 kg (curb 4670 + body 1900); reference payload 3019.5882 kg from `run_steps.py` line 51; TPMLM = 11990 kg, checked equal to `MassMax` 11.99 t in `BatteryElectricVehicle.vveh` line 14 (VECTO commit b8d6126). 0.5 × m_ref and 1.5 × m_ref are run and marked impossible, as asked.
9. **Driver reuse:** runs with identical coasting inputs share one driver result (for example C is run once per cycle, A once per cycle). That is only caching; results are the same.
10. **Reference-load cycle files** as in `run_steps.py`. The case mass is applied as a constant payload, so the cycle file is the same for all cases.
11. **Dependencies:** numpy 2.4.6 and scipy 1.17.1 installed in a venv outside the repo (`/projects/sandbox/venv`), VECTO cloned to `/projects/sandbox/vecto-src`, branch IEPC-experiments, HEAD b8d6126 (same commit the earlier scripts cite).

## 7. Not done / could not do

- No comparison to VECTO `.vmod` output; B is the "truth" only inside this test.
- Real weather, real wind direction, solar and HVAC are not in the energy step.
- Only Chain S was run (Chain E not asked for). Only the E2 drag table (V1).
- MunicipalUtility and low-load cycles were not run (not requested).
- No sweep of the 10° yaw clamp at 8 m/s, and no sensitivity of the driver's other tuning parameters.
- The 0.1 % noise level in the driver output was not quantified with a perturbation study.
- Speed difference vs B is a worst-point number on a distance grid, not an RMS.
- Timing is from one machine, one run of 5, not a controlled benchmark; the sandbox may be shared.

## 8. Sources for numbers I did not compute

| Number | Source |
|---|---|
| Gate targets 0.9749 / 0.8502 | `docs/research/drag-default-test-2026-11/step3_kwh_per_km.csv` lines 3, 15 |
| Reference payload 3019.5882 kg | `docs/research/drag-default-test-2026-11/run_steps.py` line 51 |
| Aux 1983 W / 1769 W | `run_steps.py` line 41 |
| P_AIR 101325, R_AIR 287.05 | `docs/research/vecto/hdev_test_harness_v1.7.py` line 55 |
| rho 1.188 | harness line 61 (VECTO `DeclarationData.cs` line 74) |
| Declaration wind 3 m/s, 4 m, Hellmann 0.2 | harness line 63 |
| TPMLM 11990 kg | harness line 69; `BatteryElectricVehicle.vveh` line 14 |
| `T_VECTO_EQ` form | harness line 215 |
| `crr_total_vecto`, `CRR_EFF`, `BETA` | harness lines 95–101, 53 |
| Coast drag at current speed v | Bob's instruction of 10 Nov; VECTO `DefaultDriverStrategy.cs` `ComputeCoastingDistance` (not re-checked by me) |

Tables in sections 2–4 are copied from `results_*.csv` and `run_log.txt`. Nothing is filled in from memory.
