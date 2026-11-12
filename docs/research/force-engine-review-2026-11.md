# Wheel-power deep dive: `force_engine` and `consumption_engine` steps 1-4

*Review for Bob, 12 Nov 2026. Branch `force-engine-review-2026-11`. Engine code was **not** changed (notebook and `src/` untouched).*
*Code of record: `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb` (loaded unchanged by `_load_notebook.py`).*
*VECTO source read: `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126ab0bc2ab8beb3eaee878f7198126b600a`. The `.vmod` files say VECTO 5.1.6-RC.*

**Tags used:** `[VECTO]` read in VECTO source · `[REG]` Regulation (EU) 2017/2400 · `[SOURCE]` outside document · `[CALC]` my arithmetic from sourced inputs ·
`[TEST]` a test or script I ran · `[ASSUMPTION]` HDEV choice, no source · `[SIMPLIFICATION]` deliberate · `[OPEN]` not resolved · `ILLUSTRATIVE` test value, not data.
Everything in `docs/research/force-engine-review-2026-11/` can be regenerated with `python run_all.py` there. Tests: `pytest tests/force_engine`.

---

## 0. Summary (one page)

**What is right.**
1. `[TEST]` With VECTO's own speed trace as input, `force_engine` + the step-4 equation reproduce VECTO's wheel terms on all six `.vmod` runs (Regional, Urban, LongHaul × ReferenceLoad, LowLoading).
   Positive wheel energy is off by only **-0.002 % (Regional), -0.011 % (Urban), -0.001 % (LongHaul)** (file `partC_terms.csv`). Every single term is within 0.08 %; rolling is within 0.002 %.
2. `[TEST]` The β rolling form `Crr_eff·g·m^0.9` is exact: rolling energy error is +0.0001 % (Regional LowLoading) and +0.0002 % (ReferenceLoad). It also works for LongHaul with the trailer (axles 3 and 4, Crr 0.0055). `[CALC]` I rebuilt VECTO's total rolling coefficient from the axle data for all six runs and it equals the `.vsum` value to 10 digits.
3. `[VECTO]` Slope (`atan`), air (`ρ·CdxA(v_avg)·(v1+v2)(v1²+v2²)/8`) and wheel inertia (`θ/r²·a·v_avg`) are the same equations as VECTO's. `[TEST]` Inertia energy telescopes to the kinetic energy to machine precision (residual 2e-16 kWh).
4. `[TEST]` 37 pytest tests pass (`tests/force_engine`).

**What is wrong or risky.**
1. **The remaining difference to VECTO is the driver, not the force engine.** `[TEST]` With the 12 Nov notebook driver, positive wheel energy is **+0.27 % (Regional), +2.55 % (Urban), +0.43 % (LongHaul)** above VECTO at ReferenceLoad. The force maths accounts for less than 0.02 % of that (Part D4). Time step matters: Urban positive wheel energy changes by 0.96 % between dt = 1 s and 0.25 s (Part E).
2. **Reading a `.vmod` speed column as "speed at start of step" is wrong** (`v_act` is the interval mean, Q7). `[TEST]` Doing it adds **+0.57 % (Regional) / +3.8 % (Urban)** positive wheel energy. This is a parser rule.
3. **BUG (minor, silent):** `force_engine` drops the wheel inertia silently if `theta_red` is negative or NaN, crashes if it is an array, and divides by zero when `r_dyn = 0`. **BUG (latent):** a row with `S` a hair below `wp_s[0]` gets the **last** payload (step 1). Neither triggers on driver rows today.
4. `[VECTO]` Motor rotor inertia is **not** in VECTO's wheel power; VECTO applies it at the motor shaft (E2). HDEV ignores it. Size: **0.228 / 1.22 kWh** positive at the shaft, i.e. **+0.30 % / +1.49 %** of positive wheel energy if reflected to the wheel (Regional / Urban).
5. `[VECTO]` Above 130 km/h VECTO **stops with an error**; HDEV holds the 130 km/h value. No effect on the tested cycles (max 87.5 km/h).

**Ranked proposed changes** (details in section 6; "swap" = only replaces one assumption by another)

| # | change | effect (E2, Regional / Urban) | where | basis | swap? |
|---|---|---|---|---|---|
| 1 | Parser rule: feed `force_engine` the **start** speed of each row | avoids +0.57 % / +3.8 % positive wheel energy | parser | `[VECTO]` + `[TEST]` | no, fixes a trap |
| 2 | Remove `if theta_red > 0`; accept scalar or per-row `theta_red`; checks in parser | 0 on today's numbers; removes silent drop and enables per-gear rotor inertia | engine (pure maths) + parser checks | `[TEST]` | no |
| 3 | Add rotor inertia as a **motor-side** term in the drivetrain step (later job); `J_rotor` from the certification XML field `RotationalInertia` | +0.2 / +1.2 kWh wheel-side-equivalent (+0.30 % / +1.49 %) | later drivetrain job | `[VECTO]` | no, VECTO has it |
| 4 | Parser checks: `S ≥ wp_s[0]`, hour arrays long enough and continuous, `W1/W2` one row per hour, CdxA grid in m/s | 0 | parser | `[TEST]` | no |
| 5 | Optional hourly rolling factor (cold tyres) | +6.2 % (10 °C) to +18.7 % (-10 °C) of positive wheel energy, Regional | consumption step 4, factor from parser | `[SOURCE]` model end points only | **Not recommended yet** (rule 9: only one model source, no warm-up time constant) |
| 6 | Air density: pressure from route altitude (ISO 2533), humidity (CIPM-2007) | altitude 1000 m: **-6.1 % / -1.75 %**, 2000 m: **-11.6 % / -3.3 %** of positive wheel energy (15 °C); humidity ≤ 0.25 % | parser | `[SOURCE]` | no, new physics |

**Open items.** Raw (non-1 Hz) VECTO output to settle the stop/start-row alignment (Run A, `reference/vecto/jobs/force-engine-2026-11/`); ISO 28580 / UN R117 temperature constant `K` (documents blocked, "Bob to fetch"); measured truck road-load data to validate the formulas (nothing usable found, Part H); no VECTO 5.1.6 tag exists in the fork (equations for the wheel terms are identical in `official/main` of 14 Jun 2024, `[VECTO]` by diff).

---

## 1. Gates

| Gate | Result |
|---|---|
| 1 Environment (`drag-default-test-2026-11/run_steps.py`, unchanged) | **PASS** `[TEST]` Chain S, V1, reference load: Regional **0.9749**, Urban **0.8502** kWh/km (tolerance ±0.0005). Its CSVs were regenerated and are byte-identical to the committed ones (`git status` clean). File: `gates_1_2.csv`. Needs `VECTO_SRC=<VECTO checkout>`. |
| 2 Code of record vs `src/engine/force_engine.py` | **PASS** `[TEST]` The function statements are identical. Differences are only the 8 header comment lines and `import numpy`, which the repo copy has and the notebook does not (the notebook imports numpy in cell 0). |
| 3 VECTO wheel identities | **PASS** `[VECTO]+[TEST]` `P_trac = P_roll + P_air + P_slope + P_veh_inertia` (`Vehicle.cs` 178-181, 195-199) and `P_wheel_in = P_trac + P_wheel_inertia` (`Wheels.cs` 82-95: wheel torque = force·r + inertia torque, both times mean wheel speed). Residual over all six files: max **0.2 W**, RMS 0.05 W. That is the rounding of the `.vmod` (kW with 4 decimals). File: `partC_gate3_identity.csv`. |

---

## 2. Part A: line-by-line audit

### 2.1 `force_engine` (Appendix 1.1)

| line | what it does | VECTO | verdict |
|---|---|---|---|
| `speed, accel, dt_s, grade = np.asarray(..., float)` | makes arrays, integers allowed | - | OK `[TEST]` (ints ok, shape mismatch raises, NaN stays in its row, empty arrays ok) |
| `grade = np.arctan(grade/100)` | % → angle | `DistanceBasedDrivingCycle.cs` 125-126 calls `VectoMath.InclinationToAngle` = `Math.Atan` (`VectoMath.cs` 266-268) | **MATCH** |
| `v1 = speed`, `v2 = max(speed + accel*dt, 0)` | start/end speed, no negative speed | `Vehicle.cs` 158-162 (`v = v_prev + a*dt`, snapped to 0 inside 2e-3 m/s) | **MATCH** for rows the driver makes; see B4 for rows that would clamp |
| `v_avg = (v1+v2)/2` | mean speed (constant acceleration) | `Vehicle.cs` 191 | **MATCH** |
| `k_lin = (g sin θ + a) v_avg` | slope + vehicle inertia power per kg | `Vehicle.cs` 195, 198, 225-237 (both use `TotalVehicleMass`, no wheel mass) | **MATCH** |
| `k_roll = Crr g cos θ v_avg` | rolling power per kg^β | `Vehicle.cs` 214-223 (`cos(gradient)·M·g·rrc(M)`), `VehicleData.cs` 292-311 | **MATCH** (with β and `Crr_eff`, Q2) |
| `k_rot = (θ/r²)·a·v_avg if θ > 0 else 0` | wheel inertia power | `Wheels.cs` 72-95, 98; `Formulas.cs` 65-75 | **MATCH** for θ > 0. **BUG-1** below for θ ≤ 0, NaN, array |
| `L = (v1+v2)(v1²+v2²)/8` | exact mean of ½v³ | `CrosswindCorrectionCdxALookup.cs` 73-77 | **MATCH** |
| `return ..., v_avg` | for CdxA lookup | lookup at `vAverage` (`CrosswindCorrectionCdxALookup.cs` 70-71) | **MATCH** |

**BUG-1 (`force_engine`, line `k_rot = ...`)** `[TEST]` `test_robust_*`: (a) `theta_red` negative or NaN → `k_rot = 0` with no message (rule 3, silent fallback); (b) `theta_red` array → `ValueError: truth value of an array is ambiguous`; (c) `r_dyn = 0` with `theta_red > 0` → `ZeroDivisionError` for Python floats, `inf` for numpy floats. Minimal input: `force_engine(9.80665, 0.0055, [10], [1], 1, [0], 0.4, -39.0)` returns `k_rot = 0`.
**Not a bug but a trap** `[TEST]`: negative `speed` gives negative `L` and `v_avg` (no guard; parser must check). `v2 = max(v + a·dt, 0)` with a row that would go below zero keeps `accel` unchanged: the inertia power is then **2×** the kinetic-energy change (ILLUSTRATIVE v = 2 m/s, a = -4 m/s², `partB_v2_clamp.csv`). `[TEST]` The driver never makes such a row: scanned 5 cycles × coast on/off, min of `v + a·dt` is exactly 0 (`partB_v2_clamp_driver_scan.csv`).

### 2.2 `consumption_engine` steps 1-4 (Appendix 1.2)

| step / line | what it does | verdict |
|---|---|---|
| 1 `has_pl`, `k_pl = searchsorted(wp_s[has_pl], S, side="right") - 1`, `m_row = m_vehicle + payload` | last payload waypoint at or before each row | OK for rows with `S ≥ wp_s[0]`. A row **exactly at** a stop gets the new payload `[TEST]`. **BUG-2** `[TEST]` `test_step1_row_before_first_waypoint_wraps_to_last_payload_BUG`: `S = -1e-9` gives `k_pl = -1` → the **last** payload (200 kg instead of 1000 kg in the test). Driver rows start exactly at `wp_s[0]`, so it is latent. |
| 2 `hour = ((t_start + T)//3600).astype(int)` | weather hour index | OK `[TEST]`: `T_amb_h` too short → `IndexError` (loud, good); a trip across midnight needs one continuous array (hour 24, 25 …); non-whole-hour `t_start` works. |
| 3 `rho_row = p_air/(R_air (T+273.15))` | dry ideal gas, fixed pressure | OK. At 15 °C: 1.22501 vs ISO 2533 1.2250 `[TEST]`. `[OPEN]` ISO 2533 has no sea-level density table at -20/0/30 °C (temperature at sea level is fixed to 15 °C), so only the 15 °C point is a standard anchor. |
| 3 `cdxa_tab = CdxA0*W1 + W2` | CdxA_eff per hour × speed | OK. `[TEST]` shape contract: `W1`, `W2` must have **one row per weather hour** (same row count as `T_amb_h`, columns = the CdxA grid). One row for all hours → `IndexError` for hour ≥ 1. |
| 3 `v_kmh = clip(v_avg*3.6, cdxa_v[0], cdxa_v[-1])`, `j`, `w`, interpolation | linear interpolation, ends held | equals `np.interp` per hour `[TEST]`. Below 60 km/h **MATCH** VECTO (first table entry is copied from the 60 km/h entry, `AirdragDataAdapter.cs` 88). Above 130 km/h **DEVIATION (new, flag it)**: VECTO throws `VectoException("CrossWindCorrection Extrapolation …")` (`CrosswindCorrectionCdxALookup.cs` 80-87; the catch in `Vehicle.cs` 169-174 calls the same function again, so the run fails). |
| 4 `P_wheel = m*k_lin + m**beta*k_roll + k_rot + rho*cdxa*L` | sum | **MATCH** (Part C) |

### 2.3 Hard-coded numbers that are not arguments

| number | where | kind |
|---|---|---|
| `/100` | force_engine grade | unit definition (% → ratio) |
| `0.0` in `np.maximum(..., 0.0)` | force_engine v2 | physical limit (speed ≥ 0); VECTO has a 2e-3 m/s halt tolerance (`Constants.cs` 327) `[VECTO]` |
| `/2`, `/8`, `**2` | v_avg, L | maths; `/8` = ½ × ¼ from the mean of v³ (`CrosswindCorrectionCdxALookup.cs` 76) |
| `0` in `theta_red > 0`, `zeros_like` | force_engine | HDEV choice "no rotating mass unless given" (see BUG-1) |
| `3600` | step 2 | unit definition (s per hour) |
| `273.15` | step 3 | unit definition (°C → K) |
| `3.6` | step 3 | unit conversion **inside an engine function**, against Bob's rule. It converts `v_avg` to km/h for the CdxA grid. |
| `- 1`, `side="right"`, `0`, `len-2`, `1 - w` | steps 1, 3 | index/interpolation mechanics |

**Parser item on `3.6`:** the driver now takes its CdxA grid in m/s (decided 10 Nov) but step 3 takes `cdxa_v` in km/h. `[TEST]` Both work, but the parser must hold two copies of the same grid. **Kiro's recommendation:** pass the grid in m/s to step 3 as well and clip `v_avg` directly. Numerical effect: none.

### 2.4 Robustness list (all tests in `test_force_engine.py`)
`if theta_red > 0` with array → ValueError (LIMITATION) · `r_dyn = 0` with θ > 0 → ZeroDivisionError/inf (BUG) · negative θ, NaN θ → silently 0 (BUG) · `dt_s` scalar vs array → identical · NaN in grade or speed → stays in its row (speed NaN poisons all five outputs of that row) · empty arrays → empty outputs · negative speed → negative `L`, `v_avg` (parser must check) · integers → fine · shape mismatch → ValueError.

---

## 3. Questions answered from the VECTO source (Q1-Q10)

All `[VECTO]` = `mohgsaad-art/VECTO`, `IEPC-experiments`, commit `b8d6126`, paths under `VectoCore/VectoCore/`. **Version note `[OPEN]`:** the fork has no 5.1.6 tag. I diffed the six files that carry the wheel terms against `official/main` (14 Jun 2024, `ab76d59`): the equations in `Vehicle.cs` (roll, slope, air, inertia, output), `Wheels.cs`, `CrosswindCorrectionCdxALookup.cs`, `ModalData1HzFilter.cs` and the `atan` in `DistanceBasedDrivingCycle.cs` are the same; the differences are refactoring and electric-machine support. `Physics.cs` and `Formulas.cs` have identical blobs.

**Q1 Slope.** `[VECTO]` `DistanceBasedDrivingCycle.cs` 107-129: for a step of road distance `ds`, altitude is interpolated at `distance + ds`; `gradient = InclinationToAngle((Altitude_now − Altitude_prev)/ds)`, i.e. **rise over the road distance of the cycle (the cycle's x-axis), then `atan`**. The cycle reader builds altitude from `grad` the same way (`DrivingCycleDataReader.cs` ~236: `altitude += Δs·grad/100`). The `.vmod` `grad` column is written back as `tan(angle)·100` (`DistanceBasedDrivingCycle.cs` 60-62), so it is exactly the secant in %. Slope force: `TotalVehicleMass·g·sin(angle)` (`Vehicle.cs` 232-237). Mass = curb + body/trailer + loading; **no** reduced wheel mass. Compare: `force_engine` does `atan(grade/100)` on the row secant = **MATCH**. `[TEST]` Variant (d) (adding the wheel mass to the slope term) would add +0.26 % / +0.26 % positive wheel energy and is **not** what VECTO does.
Numbers `[CALC]` (`partA_q1_grade_conversions.csv`), `sin(atan G)/G − 1`: 2 %: -0.0200 %; 6 %: -0.180 %; 10 %: -0.496 %; 20 %: -1.94 %. `asin(G)` would give exactly G (+0 %). `cos(atan G) − 1`: -0.020 %, -0.180 %, -0.496 %, -1.94 %; `cos(asin G) − 1`: -0.020 %, -0.180 %, -0.501 %, -2.02 %.
`[TEST]` Effect of the choice on the E2 runs (positive wheel energy): `asin` -0.001…+0.007 %, "no angle" +0.002…+0.009 % (`partC_causes_isolated.csv`, rows b1, b2). Negligible; `atan` is the VECTO form.
*Inconsistency inside VECTO (report, don't change):* `DefaultDriverStrategy.cs` 740-742 (`ComputeCoastingDistance`) passes the plain ratio `rise/run` as a `Radian` into `RollingResistance`, so it uses `cos(ratio)`, while `Vehicle.cs` uses `cos(atan(ratio))`. At 10 %: 0.995004 vs 0.995037 (3e-5); at 20 %: 0.980067 vs 0.980581 (5e-4). The HDEV `coast_distance` copies the VECTO line (**MATCH to VECTO**). A VECTO comment at lines 441-444 shows its authors noticed this.

**Q2 Rolling.** `[VECTO]` `Vehicle.cs` 214-223: `F_roll = cos(gradient)·M·g·rrc`, `M = TotalVehicleMass` (curb + body/trailer + loading, `VehicleData.cs` 196-205), and zero when `v_prev + v_cur ≈ 0` (166). `rrc = TotalRollResistanceCoefficient = Σ_i s_i·RRC_i·(s_i·M·g/(Fz_i·n_i))^(β−1)` (`VehicleData.cs` 292-311, β = 0.9 from `Physics.cs` 51; `s_i` axle weight share, `Fz_i` tyre test load, `n_i` tyres per axle).
**Proof** `[CALC]`: `M·rrc(M) = Σ s_i·RRC_i·(s_i·g/(Fz_i·n_i))^(β−1)·M·M^(β−1) = [Σ s_i^β·RRC_i·(g/(Fz_i·n_i))^(β−1)]·M^β`. Everything in the bracket is constant when the shares `s_i` are constant. So `F_roll = g·M·rrc(M)·cos θ = Crr_eff·g·M^β·cos θ` **exactly**, with **`Crr_eff = g^(β−1)·Σ s_i^β·RRC_i·(1/(Fz_i·n_i))^(β−1)`** (the same number as harness `crr_eff()`).
**Shares are fixed** `[VECTO]` `VehicleDataAdapter.cs` 147 (`AxleWeightShare = mission.AxleWeightDistribution[i]`, from `SegmentTable.csv`) and 168 (trailer: `TrailerAxleWeightShare / number of trailer axles`); loading does not enter.
**Trailer** `[VECTO]+[CALC]` LongHaul: shares 22.5/32.5 % (truck, "Truck Axles - Long haul") + 45 % over the 2 axles of trailer T1 (`SegmentTable.csv`, `Body_Trailers_Weights.csv`), trailer axle: RRC 0.0055, FzISO 37 500 N, single tyres (`DeclarationData.cs` 835-844). The same single `Crr_eff` form works; my rebuilt total RRC matches `.vsum` `total RRC` for LongHaul Low (0.0069554517) and Ref (0.0065741832) to 10 digits.
`[TEST]` Rolling energy error, HDEV vs VECTO: Regional Low +0.0001 %, Ref +0.0002 %; Urban Low -0.0016 %, Ref -0.0014 %; LongHaul Low -0.0001 %, Ref +0.0001 %. If the mass scaling were wrong, Low and Ref would differ by percent. **Verdict MATCH.**

**Q3 Air.** `[VECTO]` `CrosswindCorrectionCdxALookup.cs` 68-78: `P = ρ/(2·4)·CdxA(v_avg)·(v1+v2)(v1²+v2²)`, with the derivation in the comment (constant acceleration, mean of v³). `Vehicle.cs` 241-256 divides by `v_avg` to get a force and the output multiplies by `v_avg` again. **`CdxA` is looked up at the average speed** (70-71), linearly (`VectoMath.Interpolate`, 89-90). The table (`AirdragDataAdapter.cs` 20-90, `Constants.cs` 353-365): 60 to 130 km/h in 5 km/h steps, plus a point at 0 m/s that copies the 60 km/h value (88), so **below 60 km/h it is flat**; **above 130 km/h the lookup throws** (80-87). Declaration density: `AirDensity = 1.188` (`DeclarationData.cs` 74). `L = (v1+v2)(v1²+v2²)/8` and `ρ·CdxA·L` are the same thing. **MATCH**, with the >130 km/h **DEVIATION (new)**.
`[TEST]` Lookup speed: a start-speed lookup changes positive wheel energy by -0.010…+0.001 %, an end-speed lookup by -0.014…-0.002 % (variants c1, c2). `[TEST]` Using VECTO's own `CdxA_eff` column instead of Bob's table changes nothing material (Regional -0.0020 → -0.0021 %, Urban -0.0117 → -0.0118 %): the table is right. The `.vmod` `CdxA_eff` is time-averaged with standing sub-steps, so on a few moving rows it reads far below the table (max difference 4.6-6.2 m²; RMS 0.17-0.38 m²), a 1 Hz artefact (`partC_terms.csv`, columns `cdxa_*`).

**Q4 Vehicle and wheel inertia.** `[VECTO]` `P_veh_inertia = M·a·v_avg`, `M = TotalVehicleMass` (`Vehicle.cs` 195, 225-230). `P_wheel_inertia`: `Wheels.cs` 78-81, 95: inertia torque = `Formulas.InertiaPower(ω2, ω1, J, dt)/ω_avg`, where `InertiaPower = J·(Δω/dt)·ω_avg` (`Formulas.cs` 65-75); with `ω = v/r_dyn` this is `(J/r²)·a·v_avg` exactly = `k_rot`. `J = Σ n_wheels·inertia` over **all** axles including trailer (`VehicleData.cs` 308; Wheels.csv: 265/70 R19.5 = 6.5, 235/75 R17.5 = 4.5 kg·m²). `ReducedMassWheels = J/r²` (`Wheels.cs` 98). `r_dyn = d·F/(2π)` of the driven-axle tyre (`Wheels.cs`/`Declaration/Wheels.cs` 74; 0.867·3.05/(2π) = 0.4209 m = `.vsum` `r_dyn`). E2: J = 6.5 × 6 wheels = 39 kg·m² → 220.2 kg; **LongHaul J = 39 + 2×2×4.5 = 57 kg·m² → 321.8 kg** (the parser must include the trailer wheels for the driver's `m_red_wheels` too). `[TEST]` wheel-inertia energy error ≤ 0.0016 % on all six files. **MATCH.**

**Q5 Motor rotor and gearbox inertia.** `[VECTO]` For E2 the rotor term is a **motor-side** torque: `inertiaTorqueEm = Formulas.InertiaPower(ω_em, ω_em_prev, ModelData.Inertia, dt)/ω_em_avg` (`ElectricMotor.cs` 186-188); the motor must deliver it in addition to the drivetrain torque (`emTorqueMap = emTorque − inertiaTorqueEm`, 297); the electric power is looked up at the map torque (304-307); written as `P_E2-em_inertia_loss = InertiaTorqueLoss·ω_em_avg` (615). It is **not** in `P_wheel_in`, `P_trac` or `P_gbx_*`. So it belongs in the later **drivetrain** step, not in wheel power. Gearbox inertia: `P_gbx_inertia` is 0 on all six runs (AMT.vgbx `Inertia: 0.0`; engineering adapter takes gearbox inertia only for manual transmissions, `EngineeringDataAdapter.cs` 465) `[VECTO]+[TEST]`.
Inputs: `Inertia` in `.vem` = 0.225 kg·m² per motor, 2 motors → J = 0.45 (`GenericEMotor_125kW_485Nm.vem`; `ElectricMachinesDataAdapter.cs` 124); ratios ADC 2.0 × axle 2.59 × gear (1.93 in gear 2, 3.86 in gear 1) = 9.997 (gear 2) `[VECTO]`; I confirmed 9.9975 ± 0.01 from the `.vmod` (`n_E2-em_avg` / wheel speed).
**Sizing** `[TEST]` (variant e, `partC_*`): an HDEV term `J·i²/r_dyn²·a·v_avg` per row (gear from the `.vmod`) reproduces `P_E2-em_inertia_loss` to within 0.0012 % on Regional and Urban Low and Regional Ref; Urban Ref -0.10 % and LongHaul Ref +2.6 % (gear shifts at pull-away change motor speed with no vehicle acceleration, a feature of VECTO that a vehicle-speed term cannot see). Equivalent mass `J·i²/r²` = **253.9 kg** in gear 2 (wheels: 220.2 kg). Positive part: Regional **0.228 kWh**, Urban **1.22 kWh**, LongHaul 0.083 / 0.115 (your lead 0.228 / 1.219 confirmed). Relative to positive wheel energy: **+0.30 % (Regional), +1.49 % (Urban)**. If put on the wheel side it passes through the later drivetrain efficiency (1/η), which VECTO does not do (it is applied at the shaft); difference ≲ 5 % of 1.2 kWh. 
Where would `J_rotor` come from for a user truck? `[VECTO]` the declaration XML has a `RotationalInertia` element for each electric machine (test file `ElectricMachineSystem_StdValues.xml`, value 0.10 kg·m² there, test data only). The EEA 2024 public table `hdv_2024_electricmachine.csv` has **no inertia column** (checked its header) → for a fleet default: **NO SOURCE**. *Not decided; numbers shown.*

**Q6 Constant acceleration.** `[VECTO]` `Vehicle.cs` 158 `v = v_prev + a·dt`, 163 `s = s_prev + v_prev·dt + a·dt²/2`; power = force × average speed (191-199); the air derivation assumes `v(t) = v0 + a·t` (`CrosswindCorrectionCdxALookup.cs` 73-77). **Identity** `[CALC]`: `a·v_avg·dt = ((v2−v1)/dt)·((v1+v2)/2)·dt = ½(v2² − v1²)`, so Σ over a trip telescopes to `½(v_end² − v_start²)`. `[TEST]` Regional and Urban driver rows: residual 0.0 and -2e-16 kWh (`partB_energy_closure.csv`).

**Q7 `.vmod` output definitions.** `[VECTO]` Raw rows: `v_act = (v_prev + v_cur)/2` (`Vehicle.cs` 191-193): **interval mean, never the start speed**. `dist` = distance at the **end** of the step (`DistanceBasedDrivingCycle.cs` 57). `grad` = `tan(angle)·100` of the step (60-62), `altitude` = altitude at the end of the step (63). `P_*` = force × mean speed of the step.
**1 Hz aggregation** (`OutputData/ModFilter/ModalData1HzFilter.cs` 46-180): sub-steps are cut and merged to exactly 1 s; every column (all `P_*`, `acc`, `grad`, `altitude`, `CdxA_eff`, …) is the **time-weighted mean** over the second (`MultiplyRow` by `dt`, `AddRow`, lines 85, 143); `time` = end of the second; `dt` = 1 (the last row is written as 1 s although it can be shorter, 153-178); `dist` is integrated from the speed (`ds = v·dt + a/2·dt²`, 75, 108, 134) and is the end-of-second distance; `v_act` = `(v_end_of_second + v_end_of_previous_second)/2` (90, 122, 177). The speed is integrated from the *time-averaged `acc`* of each raw row, not read from VECTO.
**Reconstruction for `force_engine`** `[TEST]`: `v1 = v_act − acc·dt/2`, `v2 = v_act + acc·dt/2` (local, no drift) or chain `v1[k+1] = v2[k]`; both agree to 3e-5 m/s (rounding of the file) except the very last Urban row. Your second lead holds: `v_act·dt` equals the distance moved in 91.6 % of Regional ReferenceLoad rows (tolerance 2 mm; your 83 % used another tolerance); the rest are rows where the acceleration changes inside the second. **Never feed `v_act` as the start speed** (variant a2: +0.57 % / +3.8 % positive wheel energy).

**Q8 Standing rows and the last braking step.** `[VECTO]` `Vehicle.cs` 159-162: a speed within 2e-3 m/s of 0 is set to exactly 0; 166: rolling resistance is exactly 0 when `v_prev + v_cur ≈ 0`; 244-246: air drag is 0 when `v_avg ≈ 0`. So standing rows are all-zero, as for HDEV `[TEST]` (every coefficient exactly 0 on 746 / 3349 / 67 standing rows, Regional / Urban / LongHaul, `partD_standing_rows.csv`). The braking step that ends at 0 is the same as HDEV's clamp (`v2 = 0`, `v_avg = v1/2`). *Difference:* VECTO shortens the last step (time), HDEV snaps the **distance** onto the stop point (Part D3).
**`[OPEN]` stop / start rows in the 1 Hz file.** Around stops the 1 Hz `P_veh_inertia` and the speed columns do not agree: Regional Ref, t = 184 s: `P_veh_inertia` = -4 943 W, `M·acc·v_act` = -1 260 W; at t = 183 s: -8 874 vs -8 587 W. Over each complete moving segment VECTO's `P_veh_inertia` sums to 0 (|sum| ≤ 0.7 J over 11 segments) while the speed-based sum is off by tens of J. My reading: the `P_*` columns are exact time averages, but the speed columns are rebuilt by the 1 Hz filter from averaged `acc`, which is inexact in the second where the truck stops. **Not proven**; Run A (raw `-act` output) settles it. Effect on trip energy: none (net) and < 0.012 % (positive part).

**Q9 Signs and units.** `[VECTO]+[TEST]` All `P_*` columns in the `.vmod` are kW, positive = power the vehicle must supply at that point (driving), negative = released. `P_slope` > 0 uphill; `P_air`, `P_roll` ≥ 0 when moving; `P_veh_inertia`, `P_wheel_inertia` > 0 when speeding up. `acc` m/s², `v_act` km/h, `dist` m, `grad` %, `altitude` m, `CdxA_eff` m². `P_trac` = force at the vehicle × mean speed; `P_wheel_in` = `P_trac + P_wheel_inertia`.

**Q10 Anything else VECTO adds to wheel power?** `[VECTO]+[TEST]` Nothing else is in `P_wheel_in`. The columns `P_wheelEnd_in/saving` exist in the header, but no code in this branch writes `P_wheelEnd_saving` (no hit in the source) and it is **0.000 kWh** on all six runs (`partA_q10_other_terms.csv`). Friction-brake energy `P_brake_loss` is a *use* of negative wheel energy, not an extra term: 0.083 kWh Regional Ref, 0.876 kWh Urban Ref, 0.075 kWh LongHaul Ref. No road-surface, temperature or curve terms exist in VECTO.

---

## 4. Parts B-E: results

### 4.1 Part B: unit and analytic tests (`tests/force_engine/test_force_engine.py`, 37 tests, all pass, 2 s)
`[TEST]` Run: `pytest tests/force_engine -q`. "BUG/LIMITATION" tests pin down today's behaviour of Bob's code; if Bob fixes it, the test fails on purpose and should be flipped.

| # | what | result |
|---|---|---|
| B1 | neutral defaults (β = 1, θ = 0) = `(Crr g cos θ + g sin θ + a)·v_avg` | exact (random 200 rows, ILLUSTRATIVE) |
| B1 | 8 Oct hand tests with g = 9.80665 | test 1: `k_roll` **1.0787315** (was 1.0791 at g ≈ 9.81, -0.034 %); `k_lin` 0, `L` 4000, `v_avg` 20 unchanged. Test 2: `k_roll` **0.5663340** (was 0.56653), `k_lin` 10.5, `L` 580.125, `v_avg` 10.5 unchanged. (`partB_hand_tests_recomputed.csv`) |
| B2 | `L` = numeric integral of ½v³ over the step, random v1 ≥ 0, a (incl. steps ending at v2 = 0 and steps starting at 0) | agrees to 1e-6 relative (5 seeds × 50 steps) |
| B3 | Σ m·a·v_avg·dt = ½m(v_end² − v_start²) | Regional residual **0.0**, Urban **-2e-16 kWh** (m = 9589.6 kg, driver rows, coasting on) |
| B3 | Σ m g sin θ v_avg dt vs m g Δh | Regional: slope energy 0.19166 kWh, potential 0.19040, **gap +0.00126 kWh** = (i) `sin(atan G)` vs G **+0.00130** + (ii) row distance ≠ v_avg·dt **-0.00004**; residual 1e-16. Urban: 0.26055 vs 0.25771, gap **+0.00284** = (i) +0.00288 + (ii) -0.00005. Both are below 0.015 % of the positive slope energy (15.9 / 19.9 kWh). (`partB_energy_closure.csv`) |
| B3 | Σ k_rot·dt over a stop-to-stop trip = 0 | 7e-12 and 2e-11 J/kg·s (zero) |
| B4 | rows with `v + a·dt < 0`: inertia vs ½(v2² − v1²)/dt | ILLUSTRATIVE (v = 2, a = -4): engine gives -4 J/kg, kinetic change is -2 J/kg: **factor 2**. Driver scan: **0 rows** in 10 runs (5 cycles × coast on/off). |
| B5 | mass-free property: `P_wheel(m)` = force × speed at 5 masses, β = 1 and 0.9 | equal to 1e-9 |
| B6 | payload mapping constant / linear / custom; row at a stop; no stops | OK; **BUG-2** row before `wp_s[0]` gets last payload |
| B6 | hour index | too-short weather array → `IndexError`; midnight crossing and non-whole-hour start work |
| B6 | CdxA interpolation = `np.interp` per hour; held below 60 / above 130; shape contract | OK; one W1/W2 row per hour is required |
| B6 | ρ | at 15 °C: 1.22501 vs ISO 2533 1.2250 (diff 1e-5). Other temperatures: no ISO sea-level values exist `[OPEN]`; I compared with CIPM-2007 instead (Part F4). |

### 4.2 Part C: row-level reproduction of VECTO (VECTO's own trace → `force_engine` → compare)
Method `[TEST]` (`run_part_c.py`): for each of the six `.vmod` files, `v1 = v_act − acc·dt/2` (Q7), grade from the `grad` column, vehicle from VECTO files (mass = curb 4670 + body 1900 [+ trailer 3400] + loading from `.vsum`; `Crr_eff` and β = 0.9; `r_dyn` 0.4209 m; wheel inertia 39 kg·m² [57 with trailer]; ρ = 1.188; CdxA from Bob's `crosswind_engine` at 3 m/s / 4 m / Hellmann 0.2, no yaw clamp, `RigidSolo` / `RigidTrailer` coefficients `VCDV_parameters.csv`). Variant (i) = HDEV CdxA table; variant (ii) = VECTO's `CdxA_eff` column. Vehicle checks: total mass and total RRC equal the `.vsum` for all six runs.

| case | term | vecto_pos_kWh | hdev_pos_kWh | d_pos_kWh | d_pos_pct | d_net_kWh | rms_W | max_W | flagged |
|---|---|---|---|---|---|---|---|---|---|
| LongHaul Low | P_roll | 21.398 | 21.398 | -0.0000 | -0.0001 | -0.0000 | 13.2 | 466 | 11/4503 |
| LongHaul Low | P_air | 63.362 | 63.361 | -0.0009 | -0.0014 | -0.0009 | 17.7 | 393 | 1/4503 |
| LongHaul Low | P_slope | 16.054 | 16.054 | +0.0000 | +0.0002 | +0.0000 | 21.1 | 949 | 11/4503 |
| LongHaul Low | P_veh_inertia | 3.705 | 3.705 | +0.0000 | +0.0006 | +0.0000 | 190.1 | 6412 | 18/4503 |
| LongHaul Low | P_wheel_inertia | 0.106 | 0.106 | +0.0000 | +0.0007 | +0.0000 | 5.4 | 183 | 4/4503 |
| LongHaul Low | P_wheel_in(sum) | 87.561 | 87.560 | -0.0009 | -0.0010 | -0.0009 | 169.4 | 5167 | 28/4503 |
| LongHaul Ref | P_roll | 35.541 | 35.541 | +0.0000 | +0.0001 | +0.0000 | 24.5 | 742 | 17/4521 |
| LongHaul Ref | P_air | 63.003 | 63.003 | -0.0005 | -0.0008 | -0.0005 | 12.3 | 347 | 3/4521 |
| LongHaul Ref | P_slope | 28.210 | 28.210 | +0.0001 | +0.0005 | +0.0001 | 34.3 | 1237 | 19/4521 |
| LongHaul Ref | P_veh_inertia | 6.969 | 6.969 | +0.0001 | +0.0015 | -0.0000 | 351.2 | 10684 | 19/4521 |
| LongHaul Ref | P_wheel_inertia | 0.113 | 0.113 | +0.0000 | +0.0016 | -0.0000 | 5.7 | 174 | 5/4521 |
| LongHaul Ref | P_wheel_in(sum) | 106.095 | 106.095 | -0.0003 | -0.0003 | -0.0004 | 312.5 | 10396 | 23/4521 |
| Regional Low | P_roll | 14.578 | 14.578 | +0.0000 | +0.0001 | +0.0000 | 12.9 | 290 | 22/5885 |
| Regional Low | P_air | 39.490 | 39.488 | -0.0018 | -0.0046 | -0.0018 | 17.6 | 350 | 18/5885 |
| Regional Low | P_slope | 11.926 | 11.926 | -0.0003 | -0.0021 | +0.0000 | 18.0 | 403 | 20/5885 |
| Regional Low | P_veh_inertia | 6.439 | 6.439 | +0.0001 | +0.0011 | +0.0000 | 169.1 | 3701 | 62/5885 |
| Regional Low | P_wheel_inertia | 0.198 | 0.198 | +0.0000 | +0.0010 | +0.0000 | 5.2 | 114 | 2/5885 |
| Regional Low | P_wheel_in(sum) | 59.863 | 59.862 | -0.0012 | -0.0020 | -0.0018 | 170.1 | 3587 | 81/5885 |
| Regional Ref | P_roll | 18.930 | 18.930 | +0.0000 | +0.0002 | +0.0000 | 16.5 | 358 | 30/5885 |
| Regional Ref | P_air | 39.491 | 39.489 | -0.0018 | -0.0046 | -0.0018 | 17.5 | 283 | 12/5885 |
| Regional Ref | P_slope | 15.941 | 15.941 | -0.0002 | -0.0015 | +0.0002 | 23.0 | 537 | 24/5885 |
| Regional Ref | P_veh_inertia | 8.601 | 8.601 | +0.0000 | +0.0005 | +0.0000 | 228.3 | 4918 | 69/5885 |
| Regional Ref | P_wheel_inertia | 0.197 | 0.197 | +0.0000 | +0.0004 | +0.0000 | 5.2 | 113 | 2/5885 |
| Regional Ref | P_wheel_in(sum) | 67.209 | 67.208 | -0.0014 | -0.0020 | -0.0016 | 228.3 | 4794 | 88/5885 |
| Urban Low | P_roll | 14.577 | 14.577 | -0.0002 | -0.0016 | -0.0002 | 27.4 | 428 | 209/13482 |
| Urban Low | P_air | 16.528 | 16.515 | -0.0126 | -0.0764 | -0.0126 | 21.7 | 304 | 141/13482 |
| Urban Low | P_slope | 14.890 | 14.891 | +0.0006 | +0.0043 | +0.0016 | 88.1 | 3621 | 381/13482 |
| Urban Low | P_veh_inertia | 33.986 | 33.986 | -0.0000 | -0.0000 | +0.0013 | 344.3 | 5609 | 732/13482 |
| Urban Low | P_wheel_inertia | 1.043 | 1.043 | +0.0000 | +0.0000 | +0.0000 | 10.6 | 172 | 31/13482 |
| Urban Low | P_wheel_in(sum) | 63.547 | 63.541 | -0.0069 | -0.0109 | -0.0099 | 347.5 | 7455 | 875/13482 |
| Urban Ref | P_roll | 18.928 | 18.927 | -0.0003 | -0.0014 | -0.0003 | 34.9 | 504 | 234/13489 |
| Urban Ref | P_air | 16.497 | 16.484 | -0.0129 | -0.0781 | -0.0129 | 22.3 | 306 | 151/13489 |
| Urban Ref | P_slope | 19.911 | 19.911 | +0.0004 | +0.0020 | +0.0001 | 116.3 | 4644 | 458/13489 |
| Urban Ref | P_veh_inertia | 45.460 | 45.460 | +0.0001 | +0.0002 | +0.0008 | 454.6 | 6799 | 776/13489 |
| Urban Ref | P_wheel_inertia | 1.044 | 1.044 | +0.0000 | +0.0002 | +0.0000 | 10.4 | 156 | 35/13489 |
| Urban Ref | P_wheel_in(sum) | 79.586 | 79.577 | -0.0093 | -0.0117 | -0.0123 | 451.9 | 9471 | 912/13489 |

*Reading the table:* positive-part energies are the ones that matter (net inertia terms are ≈ 0 by telescoping). "flagged" = rows with |diff| > 0.1 kW **and** > 1 % of the VECTO row value (rule: stricter than "or", which would flag almost every row). Largest single-row difference 10.7 kW (LongHaul Ref, `P_veh_inertia`, a stop/start row).

**Why do rows differ at all when the trip totals agree to 0.01 %? (explanation of every flagged class)** `[TEST]` `partC_flagged_rows_classes.csv`, classes for ReferenceLoad:

| cycle | term | A_within_3s_of_standstill | B_accel_changes_in_second | C_other | G_grade_changes_in_second |
|---|---|---|---|---|---|
| LongHaul | P_air | 0 | 3 | 0 | 0 |
| LongHaul | P_roll | 14 | 3 | 0 | 0 |
| LongHaul | P_slope | 15 | 4 | 0 | 0 |
| LongHaul | P_veh_inertia | 17 | 2 | 0 | 0 |
| LongHaul | P_wheel_inertia | 5 | 0 | 0 | 0 |
| RegionalDelivery | P_air | 0 | 12 | 0 | 0 |
| RegionalDelivery | P_roll | 30 | 0 | 0 | 0 |
| RegionalDelivery | P_slope | 13 | 5 | 0 | 6 |
| RegionalDelivery | P_veh_inertia | 51 | 18 | 0 | 0 |
| RegionalDelivery | P_wheel_inertia | 2 | 0 | 0 | 0 |
| UrbanDelivery | P_air | 0 | 149 | 0 | 2 |
| UrbanDelivery | P_roll | 221 | 9 | 3 | 1 |
| UrbanDelivery | P_slope | 242 | 172 | 3 | 41 |
| UrbanDelivery | P_veh_inertia | 466 | 302 | 6 | 2 |
| UrbanDelivery | P_wheel_inertia | 33 | 0 | 2 | 0 |

* **A: within 3 s of a standstill** (a row with v < 0.05 m/s lies within ±3 rows): **90-100 % of the absolute row differences of rolling, vehicle inertia and wheel inertia, and 63-89 % of slope**. Cause: the 1 Hz file mixes exact time-averaged `P_*` columns with speed columns rebuilt by the filter; they disagree in the seconds before a stop and after a pull-away (Q8 `[OPEN]`). Example Regional Ref t = 182 s (3 s before the stop): VECTO `P_roll` = 1 009 W, while a mean speed of 1.90 m/s (the file's own `v_act`) would give 1 296 W. The net over each stop episode is 0 (VECTO's own `P_veh_inertia` sums to 0 over every moving segment), so trip energies are not affected.
* **B: acceleration changes within the second** (|Δa| to a neighbour row > 0.2 m/s²): 98-100 % of the flagged `P_air` rows and 1-26 % of slope / vehicle-inertia rows. Cause: VECTO averages sub-step values; `force_engine` assumes one constant acceleration per 1 s row, so `ρ·CdxA·L` and `CdxA(v_avg)` differ by up to 0.35 kW.
* **G: grade changes inside the second** (|Δgrade| > 0.2 % to a neighbour): 24 % of Regional and 5 % of Urban slope rows. Cause: the `grad` column is a time average of the sub-step grades, and `sin(atan(·))` times speed is not linear across a waypoint.
* **C: other**: **0 rows** for Regional and LongHaul; Urban has 3 (roll), 3 (slope), 6 (vehicle inertia), 2 (wheel inertia) of 13 489 rows (≤ 7 % of the absolute differences of those terms). Not explained one by one `[OPEN]`; at the file's precision (0.1 W) and with the 3 s zone these are most likely stop-zone effects of two very close stops.
The variant "roll with v = dist/dt" (a3) changes the roll error by at most 0.0002 percentage points, so the difference is not a matter of how the row speed is defined.

**C2. CdxA variants (positive-part error of `P_air` and of the wheel sum, %): (i) Bob's table, (ii) VECTO's own `CdxA_eff` column**

| case | term | i_table | ii_vecto_cdxa |
|---|---|---|---|
| LongHaul Low | P_air | -0.0014 | -0.0019 |
| LongHaul Low | P_wheel_in(sum) | -0.0010 | -0.0014 |
| LongHaul Ref | P_air | -0.0008 | -0.0011 |
| LongHaul Ref | P_wheel_in(sum) | -0.0003 | -0.0005 |
| Regional Low | P_air | -0.0046 | -0.0046 |
| Regional Low | P_wheel_in(sum) | -0.0020 | -0.0020 |
| Regional Ref | P_air | -0.0046 | -0.0046 |
| Regional Ref | P_wheel_in(sum) | -0.0020 | -0.0021 |
| Urban Low | P_air | -0.0764 | -0.0774 |
| Urban Low | P_wheel_in(sum) | -0.0109 | -0.0111 |
| Urban Ref | P_air | -0.0781 | -0.0790 |
| Urban Ref | P_wheel_in(sum) | -0.0117 | -0.0118 |

**C3. Bob's `CdxA_eff` table vs VECTO's `CdxA_eff` column on moving rows (m²).** The large maxima are rows where the 1 Hz column is averaged with standing sub-steps (value 0).

| case | cdxa_rms_moving | cdxa_max_moving |
|---|---|---|
| LongHaul Low | 0.1772 | 5.7736 |
| LongHaul Ref | 0.1607 | 6.2378 |
| Regional Low | 0.1782 | 4.6169 |
| Regional Ref | 0.1659 | 4.6683 |
| Urban Low | 0.3656 | 4.8902 |
| Urban Ref | 0.3802 | 4.9032 |

**Isolating the causes, one at a time** (`partC_causes_isolated.csv`; positive wheel-energy error in %):

| variant | LongHaul Low | LongHaul Ref | Regional Low | Regional Ref | Urban Low | Urban Ref |
|---|---|---|---|---|---|---|
| 0 baseline | -0.0010 | -0.0003 | -0.0020 | -0.0020 | -0.0109 | -0.0117 |
| a1 chain reconstruction | -0.0009 | -0.0004 | -0.0022 | -0.0020 | -0.0109 | -0.0117 |
| a2 v_act read as START speed (naive) | +0.1722 | +0.2005 | +0.5026 | +0.5681 | +3.6753 | +3.7851 |
| a3 roll with v = dist/dt | -0.0010 | -0.0003 | -0.0020 | -0.0019 | -0.0109 | -0.0116 |
| b1 grade asin | +0.0026 | +0.0066 | +0.0034 | +0.0056 | -0.0007 | -0.0003 |
| b2 grade none (sin=G, cos=1) | +0.0046 | +0.0089 | +0.0059 | +0.0081 | +0.0024 | +0.0028 |
| c1 CdxA at START speed | +0.0009 | +0.0013 | -0.0001 | -0.0003 | -0.0084 | -0.0097 |
| c2 CdxA at END speed | -0.0030 | -0.0019 | -0.0040 | -0.0039 | -0.0136 | -0.0138 |
| c3 VECTO's own CdxA_eff column | -0.0014 | -0.0005 | -0.0020 | -0.0021 | -0.0111 | -0.0118 |
| d slope mass incl. reduced wheel mass | +0.0953 | +0.1845 | +0.2160 | +0.2647 | +0.3137 | +0.2609 |
| e rotor inertia as extra wheel-side mass | +0.0776 | +0.0921 | +0.3290 | +0.2954 | +1.8450 | +1.4801 |

* (a) v1/v2 reconstruction: acc-based and chain agree within 0.0003 %. **Reading `v_act` as the start speed (a2) is wrong by +0.17 … +3.8 %.**
* (b) grade conversion: `atan` (Bob, VECTO) vs `asin` vs none differ by < 0.01 %. Keep `atan`.
* (c) CdxA lookup speed: start / average / end change energy by < 0.015 %. VECTO's own `CdxA_eff` column gives the same result as Bob's table: the crosswind table is right.
* (d) mass in the slope term: adding the reduced wheel mass to the slope force would add +0.1 … +0.3 %. VECTO does not (Q1).
* (e) motor rotor inertia added as an extra wheel-side mass: +0.08 … +1.8 % of positive wheel energy (Q5). **This is the only term where HDEV lacks something VECTO has**, and VECTO has it on the motor side.

**Rolling at both loadings (the β test).** Rolling error HDEV − VECTO, positive part: LowLoading / ReferenceLoad: Regional +0.0001 % / +0.0002 %, Urban -0.0016 % / -0.0014 %, LongHaul -0.0001 % / +0.0001 %. Exact for both loadings.

**Driver split (22 Oct totals vs today).** The 22 Oct comparison (HDEV driver + force vs VECTO: rolling exact, air -0.1 % / -2.2 %, positive wheel energy -2.3 % / -1.3 %, Regional / Urban) mixed the two effects. Today, with the 12 Nov driver and the Part-D set-up (β = 0.9, E2 drag table, coasting on), the numbers are in the table D4 in section 4.3: **VECTO trace + force_engine: -0.002 % / -0.012 % (Regional / Urban Ref) → the force engine's share of the 22 Oct positive-wheel-energy error is ≈ 0**; driver + force: **+0.27 % / +2.55 %**. The sign differs from 22 Oct because the driver and the set-up are different (so the old and new totals are not directly comparable); what is robust is that the force engine does not contribute. The old T13 test against a VECTO 2.2 12 t truck was not repeated (its `.vmod` files are not in the repo) `[OPEN]`.

### 4.3 Part D: consistency with the driver model

**D1 code check**

| term | driver (`coast_acc`, `coast_distance`) | `force_engine` / step 4 | same? | effect |
|---|---|---|---|---|
| `g` | argument `g` | argument `g` | yes if the parser passes one value | none |
| rolling form | `coast_mass**beta·g·Crr·cos θ` (`coast_acc`); `cos(grad)·coast_mass**beta·g·Crr` (`coast_distance`) | `Crr·g·cos θ·v_avg` × `m_row**beta` | same form, same `Crr_eff` if the parser passes it to both; driver uses the fixed **reference** mass, force engine the **row** mass (by design) | none |
| grade, `coast_acc` | `atan(gr_l[k]/100)`, **grade of the waypoint segment at the row start** | `atan(row secant/100)` (altitude change over the row) | **differs** when the row crosses a waypoint | D2: net ±0.003-0.005 kWh, gross 0.05-0.21 kWh per cycle on coast rows |
| grade, `coast_distance` | `cos(rise/run)`, no `atan` | `atan` | differs, but equals VECTO's `ComputeCoastingDistance` (`DefaultDriverStrategy.cs` 740-742) | 3e-5…5e-4 relative on `cos` (Q1) |
| mass in `dE` of `coast_distance` | `m_eff = coast_mass + m_red_wheels` for kinetic **and** potential energy | n/a | equals VECTO (`DefaultDriverStrategy.cs` 729-735 uses `TotalMass + ReducedMassWheels` for both) | **MATCH to VECTO** (physically the wheel mass belongs only to the kinetic term; VECTO does it this way) |
| wheel inertia | `m_eff = coast_mass + m_red_wheels` | `θ_red/r_dyn²·a·v_avg` | same if the parser computes `m_red_wheels = θ_red/r_dyn²` for both | none (LongHaul: 321.8 kg, includes trailer wheels) |
| air | **instantaneous** `ρ/2·CdxA(v)·v²` at the start speed | **step average** `ρ·CdxA(v_avg)·L` | differs (by design, Bob's note) | D2: -0.0037 / -0.0104 / -0.0033 kWh per cycle |
| motor/gearbox drag | `interp1(v, drag_v, drag_F)` at the start speed | not in wheel power (drivetrain step) | by design | - |

**D2 numeric check** (`partD_coast_rows_residual.csv`, `run_part_d.py`; E2 reference vehicle, E2 drag table `e2_table()`, ρ 1.188, reference CdxA, notebook `driver_model` with coasting on, **β = 0.9 and `Crr_eff`**). On coast rows (mode 3) the residual `P_wheel + F_drag(v)·v_avg` should be 0:

| cycle | coast rows | coast wheel energy kWh | residual kWh | = air avg vs inst | + CdxA at start vs avg | + grade (segment vs secant) |
|---|---|---|---|---|---|---|
| Regional | 85 | -0.593 | -0.00065 | -0.00370 | +0.00020 | +0.00285 |
| Urban | 276 | -1.755 | -0.01271 | -0.01042 | +0.00024 | -0.00253 |
| LongHaul | 117 | -1.363 | +0.00194 | -0.00329 | +0.00041 | +0.00483 |

The split closes exactly: with the driver's own segment grade the "other" part is 0 (max 3e-10 W) on Regional and LongHaul. The grade part is 0.053 / 0.214 / 0.069 kWh gross (sum of absolute row residuals) on 73 / 161 / 115 coast rows whose secant grade differs from the segment grade. Residual as share of positive wheel energy: -0.001 % / -0.016 % / +0.002 %.
**New finding (driver, out of scope):** on Urban 3 of 276 mode-3 rows (t = 2408, 8795, 8796 s) the driver sets `a = max(a, dec_max)` (Truck.vacc deceleration limit) and still labels the row mode 3 although `a` is **not** the coast acceleration (e.g. a = -0.50 vs coast -0.66 m/s²). Wheel residual up to 27.9 kW, 0.013 kWh. Consumption step 5 then sets `P_trac = 0` for mode 3.
**Standing rows (mode 0)** `[TEST]`: every coefficient is exactly 0 (746 / 3349 / 67 rows). 11 / 105 / 4 rows have `V = 0` but mode ≠ 0 (the start of a pull-away and the last braking row): they are not standing rows and correctly carry `L`, `v_avg` > 0 (`a > 0`).

**D3 stop-arrival rows** (`partD_stop_arrival_rows.csv`):

| cycle | rows with distance mismatch | total error m | max row m | share of route | roll energy effect kWh |
|---|---|---|---|---|---|
| Regional | 11 | +1.17 | 0.175 | 0.0012 % | -0.00022 |
| Urban | 104 | +8.78 | 0.170 | 0.0088 % | -0.00166 |
| LongHaul | 4 | +0.53 | 0.183 | 0.0005 % | -0.00019 |

(Total of `v_avg·dt − row distance`; "roll effect" = trip rolling energy if those rows used `ds/dt` as speed.) Negligible.

**D4 driver split** (positive part of each term, error vs VECTO in %; "total" = notebook driver rows through `force_engine`, "force only" = VECTO trace through `force_engine`). Driver = coasting at the Reference vehicle for both loadings (Bob's design), force terms at the loading's own mass.

| case | term | vecto_kWh | hdev_driver_force_kWh | err_total_pct | err_force_only_pct | driver_share_kWh |
|---|---|---|---|---|---|---|
| Regional Ref | P_roll | 18.930 | 18.930 | +0.001 | +0.0002 | +0.000 |
| Regional Ref | P_air | 39.491 | 39.475 | -0.041 | -0.0046 | -0.014 |
| Regional Ref | P_slope | 15.941 | 15.943 | +0.009 | -0.0015 | +0.002 |
| Regional Ref | P_wheel_inertia | 0.197 | 0.202 | +2.283 | +0.0004 | +0.005 |
| Regional Ref | P_wheel | 67.209 | 67.390 | +0.269 | -0.0020 | +0.182 |
| Regional Low | P_roll | 14.578 | 14.578 | +0.001 | +0.0001 | +0.000 |
| Regional Low | P_air | 39.490 | 39.475 | -0.038 | -0.0046 | -0.013 |
| Regional Low | P_slope | 11.926 | 11.927 | +0.002 | -0.0021 | +0.000 |
| Regional Low | P_wheel_inertia | 0.198 | 0.202 | +2.200 | +0.0010 | +0.004 |
| Regional Low | P_wheel | 59.863 | 59.908 | +0.075 | -0.0020 | +0.046 |
| Urban Ref | P_roll | 18.928 | 18.929 | +0.008 | -0.0014 | +0.002 |
| Urban Ref | P_air | 16.497 | 16.443 | -0.330 | -0.0781 | -0.042 |
| Urban Ref | P_slope | 19.911 | 19.933 | +0.113 | +0.0020 | +0.022 |
| Urban Ref | P_wheel_inertia | 1.044 | 1.092 | +4.586 | +0.0002 | +0.048 |
| Urban Ref | P_wheel | 79.586 | 81.616 | +2.550 | -0.0117 | +2.039 |
| Urban Low | P_roll | 14.577 | 14.578 | +0.008 | -0.0016 | +0.001 |
| Urban Low | P_air | 16.528 | 16.443 | -0.514 | -0.0764 | -0.072 |
| Urban Low | P_slope | 14.890 | 14.912 | +0.146 | +0.0043 | +0.021 |
| Urban Low | P_wheel_inertia | 1.043 | 1.092 | +4.654 | +0.0000 | +0.049 |
| Urban Low | P_wheel | 63.547 | 64.635 | +1.712 | -0.0109 | +1.095 |
| LongHaul Ref | P_roll | 35.541 | 35.541 | +0.001 | +0.0001 | +0.000 |
| LongHaul Ref | P_air | 63.003 | 63.387 | +0.608 | -0.0008 | +0.384 |
| LongHaul Ref | P_slope | 28.210 | 28.213 | +0.011 | +0.0005 | +0.003 |
| LongHaul Ref | P_wheel_inertia | 0.113 | 0.108 | -4.169 | +0.0016 | -0.005 |
| LongHaul Ref | P_wheel | 106.095 | 106.551 | +0.429 | -0.0003 | +0.456 |
| LongHaul Low | P_roll | 21.398 | 21.398 | +0.001 | -0.0001 | +0.000 |
| LongHaul Low | P_air | 63.362 | 63.387 | +0.040 | -0.0014 | +0.026 |
| LongHaul Low | P_slope | 16.054 | 16.055 | +0.008 | +0.0002 | +0.001 |
| LongHaul Low | P_wheel_inertia | 0.106 | 0.108 | +2.589 | +0.0007 | +0.003 |
| LongHaul Low | P_wheel | 87.561 | 87.327 | -0.267 | -0.0010 | -0.233 |

*The driver adds +0.27 % / +2.55 % / +0.43 % (Ref) of positive wheel energy; of the Urban +2.04 kWh, vehicle inertia and the extra braking/accelerating cycles dominate (HDEV driver `P_wheel_inertia` +4.6 %, i.e. more speed-up energy than VECTO).* This is a driver review item (PR #21 territory), listed here because it is 2-3 orders of magnitude bigger than anything in `force_engine`.

### 4.4 Part E: time step (`partE_timestep_energy.csv`)
`[TEST]` Notebook driver at dt = 1.0 / 0.5 / 0.25 s (same route, same E2 Reference vehicle), pushed through `force_engine` + step 4. Energy only.

**E1. Positive energy per term (kWh) by time step dt in s (columns)**

| cycle | term | 0.25 | 0.5 | 1.0 |
|---|---|---|---|---|
| RegionalDelivery | P_air | 39.490 | 39.488 | 39.475 |
| RegionalDelivery | P_roll | 18.930 | 18.930 | 18.930 |
| RegionalDelivery | P_slope | 15.954 | 15.950 | 15.943 |
| RegionalDelivery | P_veh_inertia | 8.641 | 8.693 | 8.797 |
| RegionalDelivery | P_wheel | 67.415 | 67.414 | 67.390 |
| UrbanDelivery | P_air | 16.497 | 16.480 | 16.443 |
| UrbanDelivery | P_roll | 18.928 | 18.928 | 18.929 |
| UrbanDelivery | P_slope | 20.066 | 20.027 | 19.933 |
| UrbanDelivery | P_veh_inertia | 45.986 | 46.563 | 47.545 |
| UrbanDelivery | P_wheel | 80.838 | 81.117 | 81.616 |
**E2. Positive and negative wheel energy by dt**

| cycle | dt | rows | pos_kWh | neg_kWh | pos_vs_dt0p25_pct | coast_pct |
|---|---|---|---|---|---|---|
| RegionalDelivery | 1 | 5885 | 67.390 | -8.794 | -0.037 | 1.44 |
| RegionalDelivery | 0.5 | 11763 | 67.414 | -8.805 | -0.001 | 1.63 |
| RegionalDelivery | 0.25 | 23524 | 67.415 | -8.803 | +0.000 | 1.74 |
| UrbanDelivery | 1 | 13576 | 81.616 | -45.983 | +0.962 | 2.03 |
| UrbanDelivery | 0.5 | 27018 | 81.117 | -45.448 | +0.345 | 2.21 |
| UrbanDelivery | 0.25 | 53992 | 80.838 | -45.153 | +0.000 | 2.33 |

* Rolling, air, slope converge fast (≤ 0.07 % Regional, ≤ 0.7 % Urban at 1 s). **Vehicle inertia (positive part) is the sensitive term: +1.8 % / +3.4 % at 1 s** (accelerate-then-brake inside one second cancels, so a coarse step *adds* positive energy in the driver's trace; it is the driver/step, not the force maths, which is exact per row).
* **Positive wheel energy: dt = 1 s is within 0.04 % (Regional) and 0.96 % (Urban) of dt = 0.25 s.** dt = 0.5 s: -0.001 % / +0.34 %. For the force part alone, 1 s is exact per row (B3, Part C); the 1 s choice costs < 1 % of positive wheel energy.
* Cost of going finer (`partE_runtime_machine_dependent.csv`, first call includes Python warm-up): driver 0.1-0.5 s per trip for all three steps; `force_engine` ≤ 2.2 ms (dt = 0.25 s, Urban, 54 k rows). Memory ×2 / ×4 for the coefficient arrays (1 s: 235 kB per Regional trip).

---

## 5. Parts F, G, H

### 5.1 Part F: physics beyond VECTO (candidates, not changes)
Method `[TEST]`: base case = VECTO's own 1 Hz trace of the E2 ReferenceLoad runs through `force_engine`; each variant lives in `reference_copy.py`. Effects are **wheel-level** (positive wheel energy, kWh and %); base positive wheel energy 67.21 kWh (Regional), 79.58 kWh (Urban). File `partF_effects_wheel_energy.csv`. All of these can be applied in the consumption engine or the parser **without touching rule 8** (`force_engine` stays free of mass, temperature, CdxA).

**F1 Tyre temperature and cold rolling resistance.**
*Physics:* rubber is stiffer and loses more energy when cold; the tyre warms up with use and speed, so Crr is high at trip start and falls.
*Sources:* `[SOURCE]` ISO 28580:2018 refers all results to 25 °C ambient and corrects other test temperatures (clause 5.5, 9.2); I could read only the table of contents and clause 5.5 of the iteh sample (full-text constant `K` **NO SOURCE**, "Bob to fetch"). `[SOURCE]` UN R117 snippet: ambient 20-30 °C acceptable (GRB-2012-10, search snippet only). `[SOURCE]` **Ramesh Babu et al. 2025**, *Thermal Sci. Eng. Progress* 60, 103417 (full text read, p. 10): in a **simulation** using the tyre model of Hyttinen et al. 2023, the cycle-mean Crr rises "steadily" from **0.007 at 20 °C to 0.014 at -20 °C** (so ×2.0). Your lead is confirmed; note it is a model result with only the two end points in the text (the curve is Fig. 14). `[SOURCE]` Hyttinen et al., Polymer Testing 122 (2023) 108004 and Energies 17 (2024) 6030: measured truck tyres show "a considerable increase" in rolling resistance at lower tyre and ambient temperature (abstract only; MDPI blocked, "Bob to fetch"). `[SOURCE]` Mercedes eActros 600 (+25 % at -2 °C, rolling + air ≈ 15 points): OEM press text, **not re-found** in this job `[OPEN]`.
*Test at -10, 0, +10, +25 °C* `[CALC]+[ASSUMPTION]` with a straight line between the two sourced end points (1.0 at ≥ 20 °C, 2.0 at ≤ -20 °C; the in-between values are my interpolation, not data), applied to the whole trip (no warm-up, which would lower the effect):

| T | factor | Regional Δ positive wheel energy | Urban Δ |
|---|---|---|---|
| -10 °C | 1.75 | +12.59 kWh (+18.7 %) | +9.82 kWh (+12.3 %) |
| 0 °C | 1.50 | +8.33 kWh (+12.4 %) | +6.50 kWh (+8.2 %) |
| +10 °C | 1.25 | +4.13 kWh (+6.2 %) | +3.23 kWh (+4.1 %) |
| +25 °C | 1.00 | 0 | 0 |

*Extra input:* none (ambient temperature per hour is already an input). *Where:* hourly factor `f_roll[hour]` multiplying `m_row**beta * k_roll` in step 4 (`reference_copy.wheel_power_v_roll_factor`); the factor array comes from the parser; **engine**-side change is one multiplication. *Conservative:* yes (more energy). *Evidence:* the only numbers I can use are model end points; there is no warm-up time constant and no sourced `K`. **Per rule 9 this is not worth building until a measured source supplies the curve.** `[OPEN]`
Cross-check from measurement: `[SOURCE]` Öko-Institut ELV-LIVE 2025 (full text read): real-world fleet, 800+ trips, consumption falls **0.13 kWh/km per +10 °C** around a mean of 0.96 kWh/km (11-18 t, 19-21 °C) = ±13.5 % per 10 °C, **all effects together** (heating, battery, tyres, air). It is the right order of magnitude next to F1 (+12.4 % of *wheel* energy at 0 °C) but cannot validate the tyre term alone.

**F2 Road surface (wet, snow, slush) and F3 speed dependence of Crr.**
*Sources:* `[SOURCE]` VTI report 971 "effect of water and snow on the road surface on rolling resistance" (review of ~50 reports 1970s-2018; TRID/ResearchGate abstract only: water and snow "can have a significant effect"; **numbers not read**, "Bob to fetch"). `[SOURCE]` **Askerdal et al. 2025**, *Vehicle System Dynamics* 63(6) 1137-1156 (full text read): roll-out tests of a 9 000 kg battery truck on **scraped ice, -12 °C**, Colmis (Arjeplog), fit `Crr(v) = c1 + c2·v + c3·v²` with c1 = 9.3e-3, c2 = 9.0e-4 s/m, c3 = -3.1e-5 s²/m² (valid to about 50 km/h) → **Crr 0.0093 at standstill, 0.0158 at 50 km/h**, rising with speed; they note tyre heat-up lowers it during operation. The paper's base model uses 0.007. The result mixes surface and tyre temperature.
*Test (ILLUSTRATIVE size only: different truck and tyres; value held above 50 km/h):* using this Crr(v) for the E2 trip: Regional **+19.9 kWh (+29.6 %)**, Urban **+14.5 kWh (+18.3 %)** positive wheel energy (mean Crr over moving rows 0.0156 / 0.0145 vs the E2's 0.0072).
*Can hourly precipitation drive a factor?* `[OPEN]` DMI precipitation is an hourly input, but I have **no readable source** that maps precipitation to a factor; so BLOCKED. *F3:* for dry summer truck tyres I found **no measured speed curve in the text I could read** (`NOT FOUND`); Askerdal gives the only speed dependence (ice, ≤ 50 km/h).

**F4 Air density: humidity, station pressure, altitude.**
*Formulas:* `[SOURCE]` CIPM-2007 (Picard et al., *Metrologia* 45 (2008) 149-155, full text read; constants in `reference_copy.rho_cipm2007`); recommended validity 600-1100 hPa and **15-27 °C** (outside = extrapolation; the formula is still the best sourced one). Altitude: barometric formula of ISO 2533 with sea-level 101 325 Pa, 288.15 K and the 6.5 K/km lapse rate (constants as commonly quoted, **not re-read from the ISO text** `[OPEN]`; it gives 89 875 Pa at 1000 m and 79 495 Pa at 2000 m).
`[CALC]` (`partF_air_density_table.csv`): VECTO's 1.188 equals dry air at **23.98 °C** (101 325 Pa, R = 287.05). HDEV's dry ideal gas vs CIPM-2007 at RH 50 %: **+0.18 % at 10 °C, +0.28 % at 15 °C, +0.56 % at 25 °C, +0.77 % at 30 °C** (HDEV higher = conservative).
Effect on **positive wheel energy** when VECTO's 1.188 is replaced by the weather-dependent ρ (RH 50 %, p = 101 325 Pa). Air is 59 % of Regional and 21 % of Urban positive wheel energy, so Regional reacts about three times as strongly:

| T | ρ kg/m³ | vs VECTO 1.188 | Regional Δ | Urban Δ |
|---|---|---|---|---|
| -10 °C | 1.3417 | +12.9 % | +4.60 kWh (+6.8 %) | +1.56 kWh (+1.95 %) |
| 0 °C | 1.2916 | +8.7 % | +3.09 kWh (+4.6 %) | +1.05 kWh (+1.32 %) |
| 10 °C | 1.2444 | +4.7 % | +1.68 kWh (+2.5 %) | +0.57 kWh (+0.72 %) |
| 20 °C | 1.1993 | +1.0 % | +0.34 kWh (+0.5 %) | +0.11 kWh (+0.14 %) |
| 30 °C | 1.1555 | -2.7 % | -0.97 kWh (-1.4 %) | -0.33 kWh (-0.41 %) |

* **Humidity** at 10 °C, 0 → 100 % RH: ρ -0.5 %, wheel energy -0.17 kWh (Regional, -0.25 %) / -0.06 kWh (Urban). Small; HDEV's dry-air value is on the conservative side. **Not worth modelling.**
* **Station pressure** ±3 kPa at 10 °C, RH 50 %: ±1.10 kWh (±1.6 %) Regional, ±0.37 kWh (±0.47 %) Urban. Pressure is not an input today (fixed 101 325 Pa).
* **Altitude** (15 °C, RH 50 %, vs sea level at the same temperature): 1000 m: **-4.11 kWh (-6.1 %) Regional, -1.40 kWh (-1.75 %) Urban**; 2000 m: **-7.78 kWh (-11.6 %) Regional, -2.65 kWh (-3.3 %) Urban**. Even 100 m (p -1.2 %) is about -0.7 % (Regional) / -0.25 % (Urban) of wheel energy `[CALC]`. Fixing p at 101 325 Pa is *conservative* for hilly or Alpine use.
*Where:* parser (per-hour ρ array; p from the route's own altitude profile, so no new user input). *Kiro's recommendation:* skip humidity; add altitude if routes above about 300 m are expected; leave the engine unchanged (it already takes `p_air`).

**F5 Motor rotor / drivetrain inertia.** See Q5. Wheel-side equivalent effect: Regional **+0.200 kWh (+0.30 %)**, Urban **+1.187 kWh (+1.49 %)** positive wheel energy; `[VECTO]` the true place is the motor shaft (drivetrain step). `J_rotor` for a user truck: declared XML field `RotationalInertia`; not in the EEA public table (NO SOURCE for a default). Not conservative to omit.

**F6 Curve (cornering) resistance for trucks.** `[SOURCE]` Only a model found: SUMO's electric-vehicle energy model adds a `radialDragCoefficient · m · v²/radius` term (`HelpersEnergy.cpp` 84-100, main branch, read). Its default value was not read. No measured truck cornering magnitude found (`NOT FOUND`). VECTO has none. Sizing needs route curvature, which the VECTO cycles do not have: **BLOCKED**. Omitting it is non-conservative.

**F7 Road-grade quality (belongs to the GPS adapter/parser, not the engine).** `[SOURCE]` abstract/snippet level only (PDFs blocked): NREL/NLR road-grade profile work for EPA GHG certification (docs.nlr.gov 63853, 64544), ORNL "Incorporating elevation in traffic-vehicle co-simulation" (raw elevation is noisy; smoothing and outlier removal), ORNL cubic smoothing spline on USGS DEM (λ trades noise against detail), INFORMS WSC 2025 paper con261 (noise and abrupt transitions removed while keeping geometry), ASCE paper (energy rises even at zero net climb, proportional to RMS grade). "Bob to fetch": details of the filters.
`[TEST]` ILLUSTRATIVE (no sourced noise level; σ chosen by me, clamp ±30 %): adding white noise to the 1 Hz altitude of the VECTO trace and recomputing the grade per row:

| cycle | scenario | dE_pos_kWh | dE_pos_pct | note |
|---|---|---|---|---|
| RegionalDelivery | altitude noise sigma=0.5 m, raw | +14.342 | +21.340 | mean |grade| noisy=3.31 % vs original 1.11 % |
| RegionalDelivery | altitude noise sigma=0.5 m, moving average over ~200 m | -0.120 | -0.179 | mean |grade| noisy=1.14 % vs original 1.11 % |
| RegionalDelivery | altitude noise sigma=1.0 m, raw | +43.346 | +64.496 | mean |grade| noisy=5.90 % vs original 1.11 % |
| RegionalDelivery | altitude noise sigma=1.0 m, moving average over ~200 m | +0.214 | +0.318 | mean |grade| noisy=1.31 % vs original 1.11 % |
| RegionalDelivery | altitude noise sigma=2.0 m, raw | +106.247 | +158.087 | mean |grade| noisy=10.53 % vs original 1.11 % |
| RegionalDelivery | altitude noise sigma=2.0 m, moving average over ~200 m | +1.536 | +2.286 | mean |grade| noisy=1.68 % vs original 1.11 % |
| UrbanDelivery | altitude noise sigma=0.5 m, raw | +32.759 | +41.167 | mean |grade| noisy=5.94 % vs original 1.43 % |
| UrbanDelivery | altitude noise sigma=0.5 m, moving average over ~200 m | -1.375 | -1.728 | mean |grade| noisy=1.14 % vs original 1.43 % |
| UrbanDelivery | altitude noise sigma=1.0 m, raw | +81.459 | +102.366 | mean |grade| noisy=9.65 % vs original 1.43 % |
| UrbanDelivery | altitude noise sigma=1.0 m, moving average over ~200 m | -0.860 | -1.081 | mean |grade| noisy=1.33 % vs original 1.43 % |
| UrbanDelivery | altitude noise sigma=2.0 m, raw | +154.305 | +193.907 | mean |grade| noisy=14.09 % vs original 1.43 % |
| UrbanDelivery | altitude noise sigma=2.0 m, moving average over ~200 m | +0.618 | +0.777 | mean |grade| noisy=1.73 % vs original 1.43 % |
Raw 1 Hz altitude noise of 0.5 m inflates positive wheel energy by +21 % (Regional) / +41 % (Urban) because noise enters as steep up- and downhill every second; a moving average over about 200 m brings it back to within ±2 %. So smoothing is not optional for GPS inputs. Which filter and window to use: **NO SOURCE** read.

**F8 Coast-down road load as an input.** `[SOURCE]` SAE J1263 / J2263 (referenced by 40 CFR 1066.310, read via search snippet): coast-down gives `F = A + B·v + C·v²`; ICCT "Comparison of aerodynamic drag determination procedures for HDV CO2 certification": coast-down vs the EU constant-speed procedure differ by **8.6 %** for an EU rigid truck (abstract). VECTO's constant-speed test is Annex VIII of 2017/2400 `[REG]` (I did not read the annex text).
*Mapping* `[CALC]`: `Crr·m·g ↔ A` (only at the one test mass), `½ρ·CdxA ↔ C`, `B` has no HDEV counterpart (it holds tyre speed dependence, drivetrain drag and the speed dependence of CdxA). Test: fit `A + B·v + C·v²` over 5-90 km/h to HDEV's own E2 road load (mass 9589.6 kg): A = 654 N, B = 8.30 N·s/m, C = 2.801 N·s²/m² → `Crr_eq` 0.00696, `CdxA_eq` 4.715 m²; mapping back with a constant `CdxA_eq` and an extra `B·v` drag changes positive wheel energy by only **+0.12 % (Regional), +0.05 % (Urban)** (max force error 5-90 km/h in the CSV note). **What is lost:** the mass dependence (one coast-down mass cannot give β), the split into tyre/air/driveline, and the CdxA wind curve (no crosswind correction). A parser could ask the user for A, B, C **and** the test mass and treat B as an extra speed-proportional drag (outside `force_engine`: it needs a new coefficient `k_B = v_avg²`).

### 5.2 Part G: how other tools do it

| tool | formulas (per step) | source (read how) | differs from HDEV | changes HDEV's numbers? |
|---|---|---|---|---|
| **VECTO** (reference) | slope `M g sin(atan(ΔH/ds))`; rolling `cos·M·g·Σ…M^0.9`; air `ρ/8·CdxA(v_avg)(v1+v2)(v1²+v2²)`; `M a`; wheel `J/r² a`; steps ~0.5 s, 1 Hz output | **code read**, `b8d6126` | - | - |
| **NREL FASTSim-3** (Bob's fork `mohgsaad-art/fastsim`, branch `fastsim-3`, commit `6a07d4d`) | `fastsim-core/src/simdrive/roadload.rs` 28-63: power balance at the **average speed**: air `½ρ·CdA·v_avg³` (expanded as 1/16 ρ CdA (v+v0)³), rolling `Crr·m·g·cos(atan G)·v_avg`, slope `m g sin(atan G)·v_avg`, inertia `½m(v²−v0²)/dt`, **wheel** `½·J·n_wheels/(r² dt)·(v²−v0²)` (same as `k_rot`); `simdrive/mod.rs` 360-380: `atan` for sin and cos, with an option to ignore grade; 545-575: **air density from ambient temperature and elevation per step** (`Air::get_density`) or constant 1.2; speed solved iteratively against max propulsion power | **code read** | air uses `v_avg³` instead of mean of `v³`; constant `Crr`, no β, no motor rotor term here; density from T **and elevation** | `[CALC]` air convention: -0.0025 % … -0.04 % of air energy, -0.0007 … -0.004 % of positive wheel energy (E2) |
| **SUMO** electric model | `src/utils/emissions/HelpersEnergy.cpp` 56-99 (main, read 12 Nov 2026): slope `m g sin(slope)·v`, inertia `½m(v²−v0²)/TS`, **rotating mass** `½·rotMass·(v²−v0²)/TS` (a constant equivalent mass, default 40 kg), air `½·1.2041·CdA·v³`, rolling `Crr·g·m·v`, all at the **end-of-step speed** `v`; optional `radialDragCoefficient·m·v²/radius/TS` for curves; ρ fixed 1.2041 | **code read**; the docs page `Models/Electric.md` lists the parameters | speeds taken at the END of the step; a rotating-mass parameter; a curve term; fixed ρ | `[CALC]` end-speed convention on identical inputs: +0.12 % (Regional), +0.56 % (Urban), +0.05 % (LongHaul) positive wheel energy (`partG_convention_effects.csv`) |
| **US EPA GEM** (Phase 2) | User Guide v3.5.1 (EPA-420-B-20-055): inputs only. Tyre Crr is combined with **fixed axle weights**: tractor `0.425·trailer + 0.425·drive + 0.15·steer`, vocational `0.7·drive + 0.3·steer`; ambient temperature fixed 25 °C | **user guide read in part** (text search); the road-load equations are in the Phase 2 regulation/RIA, **not read** | fixed weights are linear in mass (no β); fixed 25 °C | not estimated (equations not read) |
| **TU Graz PHEM, Argonne Autonomie, TUM truck tools** | - | **not read** (no document opened) | - | `NOT FOUND` / "Bob to fetch" |
| `dt-cargo` (fork) | a dataset of recorded truck tracks, `fleet.csv`/`tracks.csv` columns; **no road-load model** | README + notebook searched for rolling/drag/grade: no hits | - | - |
| `eflips-depot` (fork) | `eflips/depot/api/private/consumption.py`: consumption **look-up table** over (`incline`, `t_amb`, `level_of_loading`, `mean_speed_kmh`), 4-D linear interpolation, nearest-neighbour fallback; **no road-load model** | **code read** (lines 59-130) | HDEV could produce such a LUT from its engines | - |
| `spice_ev` (fork) | consumption given as mileage (kWh per 100 km) in input; **no road-load model** | grep read | - | - |

### 5.3 Part H: independent validation of the road-load model (rule 9)

| source | what was measured / done | conditions | HDEV comparison |
|---|---|---|---|
| Askerdal et al. 2025, *VSD* 63(6) (full text read) | roll-out Crr(v) and circle-test motion resistance of a 9 000 kg BEV truck | scraped ice, -12 °C, wind measured | **BLOCKED**: tyre RRC, CdxA and the exact vehicle set-up are not in the text; only structure (speed-dependent Crr; air drag with wind) can be compared |
| Ramesh Babu et al. 2025, *TSEP* 60 (full text read) | simulation (not measurement) | -20…+20 °C | not a validation |
| Öko-Institut ELV-LIVE 2nd report, 2025 (key findings read) | 800+ real trips, 11-18 t BEV trucks: 0.96 kWh/km at 19-21 °C, -0.13 kWh/km per +10 °C, +0.18 kWh/km per +10 t | fleet telematics, no speed profile | **BLOCKED** here: needs drivetrain, aux and battery steps (out of scope); a later job |
| JRC134746 (2024), VECTO hybrid truck experiment | VECTO within 2.5 % of measured electric energy in full-electric mode (abstract only) | one hybrid truck | validates VECTO, not HDEV; **Bob to fetch** |
| JRC91415 (2015) | VECTO within ±3 % of measured fuel on 2 trucks (abstract only) | - | same |
| ICCT, coast-down vs constant-speed (2021) | 8.6 % (EU rigid) difference of CdxA between methods (abstract) | - | sets the size of the CdxA input uncertainty, not a check of HDEV |
| PMC6198682 (EPA, SAE J1269/J1321 on Class 8 tractor-trailers) | tyre pressure ±5 % changes rolling resistance ≈ ±1 % (abstract) | track tests | not used |
| Measured wheel / traction energy per term for a 12 t rigid BEV truck | - | - | **NOT FOUND** |
| Published coast-down results for 12 t trucks (NREL, TNO, TU Graz) | - | - | **NOT FOUND** in my searches |

**Honest status:** the only independent comparisons I could make are *against VECTO* (Part C), which Bob said is not validation. No measured wheel-power split exists in the sources I could open, so the road-load model is **not independently validated** `[OPEN]`. The certified CdxA / tyre values in the repo (`hdv_2024_*.csv`) are inputs, not checks.

---

## 6. Proposed changes (each with before / after, measured effect, side)

**P1 Parser rule: row speeds for `force_engine` are start-of-row speeds** (parser). Before: `force_engine(g, Crr, V_act, ...)` with a `.vmod` `v_act`. After: `v1 = v_act − acc·dt/2`. Effect `[TEST]`: removes +0.57 % / +3.8 % positive wheel energy (Regional / Urban). Basis `[VECTO]` Q7. Not a swap. Applies to any external trace (VECTO, GPS speed: GPS speed is usually an instantaneous or averaged value too; check its definition).

**P2 `force_engine` accepts scalar or per-row `theta_red`; checks in the parser** (engine, pure maths).
```python
# before
k_rot = (theta_red / r_dyn**2) * accel * v_avg if theta_red > 0 else np.zeros_like(v_avg)
# after (reference_copy.force_engine_v_rotor)
k_rot = (np.asarray(theta_red, dtype=float) / np.asarray(r_dyn, dtype=float)**2) * accel * v_avg
```
Effect: 0 on today's numbers (identical for scalar θ > 0; `[TEST]` equal to the original on all driver rows); enables a per-gear rotor term and removes the silent drop of negative/NaN θ and the Python-float crash. Parser must check `theta_red ≥ 0`, `r_dyn > 0`, no NaN, `v ≥ 0`. Judged against the purity rule: no I/O, no defaults, no conversion → engine OK. Not a swap.

**P3 Rotor inertia as a motor-side term (later drivetrain job).** Before: ignored. After: `P_rotor = J_rotor·i_row²/r_dyn²·a·v_avg` reflected to the wheel (or applied at the motor shaft like VECTO, `ElectricMotor.cs` 186-196, 297). Effect `[TEST]`: **+0.20 kWh (+0.30 %) Regional, +1.19 kWh (+1.49 %) Urban** positive wheel energy; at the shaft 0.228 / 1.22 kWh. Basis `[VECTO]`. It needs `J_rotor` (XML `RotationalInertia`; NO SOURCE for fleet defaults) and the per-row gear ratio. Not a swap. *This is Bob's decision; evidence only.*

**P4 Parser contract checks** (parser): (a) `S ≥ wp_s[0]` for every row (else BUG-2 gives the last payload); (b) `len(T_amb_h) > max(hour)`, hourly arrays continuous across midnight, `W1`/`W2` with one row per weather hour and as many columns as `cdxa_v`; (c) speed ≥ 0; (d) CdxA grid in m/s for both driver and step 3 so that step 3 needs no `3.6` (engine side: `v_kmh = np.clip(v_avg, cdxa_v[0], cdxa_v[-1])`, numerically identical). Not a swap.

**P5 Hourly rolling factor** (step 4 + parser): see F1. +6.2 % … +18.7 % of positive wheel energy (Regional, 10 … -10 °C). **Do not build yet:** one model source, no warm-up time, no sourced `K`. It would swap "Crr constant" for "Crr from one model", which is exactly what rule 9 warns about. 

**P6 Air density from altitude** (parser), see F4: -6.1 % / -11.6 % (Regional) and -1.75 % / -3.3 % (Urban) of positive wheel energy at 1000 / 2000 m. New physics with a standard behind it (ISO 2533, constants to be re-read). Optional.

**Not recommended:** replacing `atan` by `asin` (< 0.01 %, further from VECTO); adding wheel mass to the slope term (+0.26 %, not VECTO); changing `L` (exact); humidity (≤ 0.1 %).

---

## 7. Deviation register (HDEV vs VECTO wheel power; E2 Regional / Urban, ReferenceLoad, positive wheel energy)

| # | deviation | size | sentence for a client report |
|---|---|---|---|
| 1 | Driver: 1 s fixed rows, own coasting, snapped stops (VECTO ~0.5 s variable steps) | **+0.27 % / +2.55 %** (dt effect alone: +0.04 % / +0.96 % vs 0.25 s) | "Driving behaviour is simulated on a 1-second grid; against VECTO's own result the wheel energy is within 0.3 % on regional and within 2.6 % on urban delivery." |
| 2 | Motor rotor inertia not modelled | wheel-side equivalent +0.30 % / +1.49 % (0.228 / 1.22 kWh at the shaft) | "Rotor inertia of the electric motor is not included; for the reference truck it is 0.3-1.5 % of the energy used to drive the wheels." *(until P3)* |
| 3 | Air density from hourly temperature instead of VECTO's fixed 1.188 | by design: +4.7 % ρ at 10 °C → +0.57 kWh (Urban) | "Air density follows the hourly temperature; VECTO's declaration value corresponds to 24 °C." |
| 4 | CdxA held at the 130 km/h value above 130 km/h (VECTO stops with an error) | 0 on tested cycles | "Above 130 km/h the air-drag area is held at its 130 km/h value." |
| 5 | Air power per 1 s row instead of ~0.5 s sub-steps | -0.005 % / -0.08 % of air energy | (not material) |
| 6 | Distance snapped onto stop points | +1.2 m / +8.8 m per 100 km, roll -0.0002 / -0.0017 kWh | (not material) |
| 7 | Coast rows: instantaneous air force in the driver vs step average in the force engine | -0.0037 / -0.0104 kWh per cycle | (not material) |
| 8 | Coast rows: driver uses waypoint-segment grade, force engine row secant | gross 0.05 / 0.21 kWh, net ≤ 0.005 kWh per cycle | (not material) |
| 9 | Tyre temperature, wet/snow surface, curves: neither VECTO nor HDEV | up to +6…+19 % (F1), up to +30 % (F2, ILLUSTRATIVE) in winter | "Wheel energy follows the declaration conditions (dry road, tyres at working temperature); cold or wet weather is not modelled and would increase it." |
| 10 | β rolling form, `atan` grade, wheel inertia, `L` | 0 (match) | - |

---

## 8. Parser jobs found

1. Pass `Crr_eff` (β form), `r_dyn`, `θ_red`, `g` to both the driver and `force_engine`; compute `m_red_wheels = θ_red/r_dyn²` once. For LongHaul include the trailer axles (`Crr_eff` over all axles, θ and trailer wheels).
2. Build the trailer axle data from the segment tables (shares, RRC 0.0055, FzISO 37 500 N, single tyres, wheel inertia from `Wheels.csv`).
3. Row speeds are start-of-row speeds (P1).
4. Validate: `θ_red ≥ 0`, no NaN, `r_dyn > 0`, `v ≥ 0`, `S ≥ wp_s[0]`.
5. Weather arrays: one entry per hour for `T_amb_h`, one row per hour for `W1`, `W2`; long enough for the trip and continuous across midnight.
6. CdxA grid: one copy in m/s for the driver and step 3.
7. Pass the driver's speed thresholds in m/s (`lac_min_v`, `os_min_v`, `os_allowed`, `v_min_coast`), see section 9.
8. (Later) rotor inertia and gear ratios per row; hourly rolling factor; ρ from altitude; grade smoothing for GPS routes.

---

## 9. Seen in passing (out of scope; file and place only)

1. **Notebook cell 4 (`driver_model`), arguments `lac_min_v=50.0, os_min_v=50.0, os_allowed=2.5, v_min_coast=5.0`:** km/h-sized numbers compared with speeds in m/s (`lac_min = lac_min_v`, `os_min = os_min_v`, `os_add = os_allowed`, `v_min_c = v_min_coast`). With the defaults left alone, look-ahead coasting and overspeed never switch on `[TEST]`: Regional coast share 0.0 % and max speed 85 km/h; with the values passed in m/s (÷ 3.6, as the header comment says for the other speeds) coast share is 1.44 % (`_common.run_driver`). The test copy `_driver_dragtable.py` divides by 3.6 inside, the notebook does not.
2. **Notebook cell 4, mode label:** a row is labelled mode 3 (coast) whenever `a >= ca − 1e-9`, also when `a` was limited by `dec_max` and is *larger* than the coast acceleration (3 Urban rows, t = 2408, 8795, 8796 s; Part D2). Consumption step 5 then sets `P_trac = 0` for mode 3.
3. **Notebook cell 16 step 5-7:** not reviewed. Cosmetic: argument and variable names `regen_effeiciency`, `drivetrain_effeiciency`.

## 10. Choices I made (least change, no questions asked)

1. VECTO source at the requested commit; the fork has no 5.1.6 tag, so I diffed the wheel-power files against `official/main` (14 Jun 2024): same equations.
2. Gate 1 was run with `VECTO_SRC=/projects/sandbox/vecto_src` (the scripts' default path is `/projects/sandbox/vecto-src`; I linked it).
3. v1/v2 from the `.vmod`: `v1 = v_act − acc·dt/2` as the main method; chain method and the wrong "start speed" reading are reported as variants.
4. "Explain every row-level difference larger than 1 % of that term or 0.1 kW": I flagged rows with **both** > 0.1 kW **and** > 1 % of the row value (an "or" flags almost every row).
5. Driver in Part D/E: β = 0.9 with `Crr_eff`, E2 drag table `e2_table()`, ρ 1.188, reference CdxA, speeds in m/s (including the four thresholds, see section 9), `coast_mass` = mass of the Reference loading for both loadings (Bob: fixed reference vehicle).
6. Part F base case = VECTO's own trace (clean physics), not the driver rows.
7. F1 factor: straight line between the two printed end points of the Chalmers paper (my interpolation, labelled); whole trip, no warm-up.
8. LongHaul vehicle from VECTO files: truck as E2, plus trailer T1 (3 400 kg, ΔCdxA 1.3 m², 2 axles 235/75 R17.5), shares 22.5/32.5/45 %, `RigidTrailer` crosswind coefficients, loadings from `.vsum`.
9. Tests pin today's behaviour for the BUG/LIMITATION cases (they pass now and fail when Bob fixes the code, which is intended).
10. ISO 2533 sea-level check: only the 15 °C point (1.2250) is a standard value; I did not invent others.
11. Weather and payloads in Part J are ILLUSTRATIVE (timing only).
12. For the 8 Oct hand tests I compared g = 9.81 (the 8 Oct values) with 9.80665.

## 11. NO SOURCE and BLOCKED

**NO SOURCE** (open items, nothing invented): ISO 28580 / UN R117 temperature constant `K`; warm-up time constant of truck tyres; precipitation → rolling-resistance factor; altitude-noise level of GPS routes and the right smoothing filter/window; fleet default for motor rotor inertia (`RotationalInertia` is a declared XML field, EEA table has no inertia column); ISO 2533 constants re-read from the standard; speed dependence of dry truck-tyre Crr.
**BLOCKED:**
* Part H direct comparison with measured truck data (no measured wheel-power split found; vehicle inputs of the found papers incomplete).
* F2 numbers from VTI (document not readable) – the Askerdal fit is used as an ILLUSTRATIVE size only.
* F6 curve resistance (no route curvature in the VECTO cycles; no measured truck magnitude).
* Part G: PHEM, Autonomie, TUM tools, GEM equations (documents not opened).
* The old T13 test against a VECTO 2.2 12 t truck (its `.vmod` files are not in the repo).
* Raw (non-1 Hz) VECTO output and the rotor-inertia-off run: Part I.

## 12. Bob to fetch (documents I could not open)

| document | link / identifier | what I need from it |
|---|---|---|
| UN Regulation No 117 (Annex 6, temperature correction `K`) | https://unece.org/sites/default/files/2023-12/R117r4a6e.pdf (HTTP 403 from the sandbox); EUR-Lex 42016X0812(01) | `K` for C3 tyres, valid ambient range |
| ISO 28580:2018, clauses 9.2-9.3 | https://cdn.standards.iteh.ai/samples/67531/21336b284db14a63978c2e4176dc953d/ISO-28580-2018.pdf (sample has TOC + 5.5 only) | temperature correction formula and constants |
| Hyttinen et al., *Truck tyre transient rolling resistance and temperature at varying vehicle velocities*, Polymer Testing 122 (2023) 108004 | doi 10.1016/j.polymertesting.2023.108004 | measured Crr vs tyre temperature and speed (master curve) |
| Hyttinen et al., *Investigating the influence of heat-insulated wheelhouses on truck tyre temperature and rolling resistance*, Energies 17(23) 6030 (2024) | https://www.mdpi.com/1996-1073/17/23/6030 (HTTP 403) | Crr at +5 °C, warm-up behaviour |
| "Modelling and experimental testing of truck tyre rolling resistance" (Hyttinen, KTH) | https://trid.trb.org/View/2388996 | stabilised and transient Crr vs ambient temperature |
| VTI report 971 (English translation) *The effect of water and snow on the road surface on rolling resistance* | https://www.researchgate.net/publication/350690120 ; https://trid.trb.org/View/1573759 | size of wet/snow factors |
| NREL/NLR road-grade reports | https://docs.nlr.gov/docs/fy15osti/63853.pdf ; https://www.nlr.gov/docs/fy16osti/64544.pdf (bot-gated) | smoothing method, error of raw grade |
| ORNL, *Incorporating elevation in traffic-vehicle co-simulation*; *Development of road grade data using the USGS DEM* | https://impact.ornl.gov/en/publications/incorporating-elevation-in-traffic-vehicle-co-simulation-issues-i/ | filters used |
| INFORMS WSC 2025 paper con261 | https://www.informs-sim.org/wsc25papers/con261.pdf | noise removal for elevation |
| EPA GEM Phase 2 documentation (road-load equations); 40 CFR 1037.520 | https://www.epa.gov/sites/production/files/2020-12/documents/420b20055.pdf (guide read in part) | rolling, air, inertia equations |
| ICCT, *Comparison of aerodynamic drag determination procedures for HDV CO2 certification* | https://theicct.org/publication/comparison-of-aerodynamic-drag-determination-procedures-for-hdv-co2-certification/ | full numbers behind 8.6 % |
| JRC134746, *Experimental evaluation of VECTO hybrid electric truck simulations* | https://publications.jrc.ec.europa.eu/repository/handle/JRC134746 | wheel/traction comparison, road-load inputs |
| Regulation (EU) 2017/2400 Annex VIII (constant speed test) and Annex Xb | EUR-Lex | how road load is declared |
| ISO 2533:1975 | https://www.iso.org/standard/7472.html | confirm barometric constants |
| Mercedes eActros 600 winter tour (OEM press text) | not re-found | +25 % at -2 °C claim |
| SUMO `radialDragCoefficient` default; PHEM; Autonomie; TUM tools | eclipse-sumo docs; TU Graz; Argonne | curve term, other tools' formulas |
| VECTO 5.1.6 release source/tag | not in the fork | confirm the wheel-term code is unchanged |

## 13. Part I, J, K and how to reproduce

* **Part I (VECTO runs for Bob, not run):** `reference/vecto/jobs/force-engine-2026-11/README.md` + `steep_grade_pm10.vdri`. Run A raw `-mod -act` output (closes the stop/start-row question), Run B rotor inertia 0 (closes Q5), Run C ±10 % grade (closes Q1).
* **Part J (performance, `partJ_performance.csv`; CPU Intel Xeon Platinum 8488C, Python 3.11.15, NumPy 2.4.6; mean of 5, the year loop mean of 2):** `force_engine` on one Regional trip (5 885 rows) **0.14 ms**; steps 1-4 on one trip **0.66 ms**; full `consumption_engine` (steps 1-7) 0.70 ms; **365 days × 3 payloads steps 1-4: 0.73 s** (6.4 M rows); `crosswind_engine` for 24 hourly wind speeds 3 ms, for 8 760 hours **1.1 s** in chunks of 500 hours (one call with all 8 760 would build four-dimensional arrays of 8 760 × 15 × 36 × 10 doubles = 378 MB each, so chunk it); memory of the coefficient arrays **235 kB per Regional trip** (5 arrays × 5 885 × 8 B); keeping all 1 095 `P_wheel` arrays: 52 MB.
  *Cache the coefficients per route?* They are mass-, temperature- and CdxA-free but **not vehicle-free**: `Crr_eff`, `r_dyn`, `θ_red`, `g` are arguments. Saving per case is only 0.14 of ~0.8 ms (~17 %), so caching is cheap but not important; if done, the key is *(driver rows identity = route/waypoints + driver inputs: coast_mass, m_red_wheels, β, Crr_eff, CdxA reference table, drag table, P_max, dt, thresholds) + (g, Crr_eff, r_dyn, θ_red)*. The expensive part to cache is the driver (0.1-0.5 s) and the hourly CdxA table (`crosswind_engine`).
* **Part K:** `docs/explainers/force-engine-explained.md`.
* **Reproduce:** `cd docs/research/force-engine-review-2026-11 && VECTO_SRC=<VECTO checkout> python run_all.py` (about 1 minute; needs numpy, pandas, scipy, matplotlib, openpyxl). Tests: `pytest tests/force_engine`. Determinism: I ran `run_all.py` twice; all 21 CSV/MD outputs have identical hashes (only `partE_runtime_machine_dependent.csv` and `partJ_performance.csv` hold timings and are machine dependent by nature). In `graph_partD_driver_vs_force.png` the 'force only' bars are invisible because they are ≈ 0.

| file | content |
|---|---|
| `_load_notebook.py` | loads the 12 Nov notebook, code cells only, skipping cell 0 |
| `_common.py` | vehicle sets (E2 and E2 + trailer), `.vmod` loaders, driver runner |
| `reference_copy.py` | verbatim copies + clearly named variants (`force_engine_v_asin`, `force_engine_v_rotor`, `wheel_power_v_roll_factor`, `rho_cipm2007`, …) |
| `run_gates_1_2.py`, `run_part_a_b_numbers.py`, `run_part_c.py` (Gate 3 + Part C), `run_part_d.py`, `run_part_e.py`, `run_part_f.py`, `run_part_g_conventions.py`, `run_part_j.py`, `run_graphs.py`, `make_tables.py`, `run_all.py` | one script per part |
| `partA_*.csv`, `partB_*.csv`, `partC_*.csv`, `partD_*.csv`, `partE_*.csv`, `partF_*.csv`, `partG_*.csv`, `partJ_*.csv`, `gates_1_2.csv`, `report_tables.md` | results |
| `graph_*.png` | row difference (Part C), term errors, driver vs force split, time step, Part F effects |
