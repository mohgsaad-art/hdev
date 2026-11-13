# `consumption_engine` review, 13 Nov 2026 (Kiro, for Bob)

Branch `consumption-review-2026-11`. Code of record: `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-13.ipynb` (loaded unchanged by `docs/research/consumption-review-2026-11/_load_notebook.py`).
VECTO version of the `.vmod` files: 5.1.6-RC. VECTO source read: `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126ab0bc2ab8beb3eaee878f7198126b600a` (see "Choices I made" for how the files were fetched).
Nothing under `src/` and nothing in the notebook was changed. Every proposed change lives in `reference_copy.py` as a named variant.

Tags: `[VECTO]` `[REG]` `[STD]` `[SOURCE]` `[CALC]` `[TEST]` `[ASSUMPTION]` `[SIMPLIFICATION]` `[OPEN]`. Sign convention of VECTO columns: see "Sign conventions" in Part A.

---------------------------------------------------------------------------------------------------------------------

## 0. Summary (one page, plain English)

**What is right.** The way the engine puts the pieces together is right. When I feed VECTO's own rows (speed, acceleration, grade, gear) into the real `force_engine` and the proposed `consumption_engine`, and I give it the efficiencies VECTO actually had on each row, the battery energy matches VECTO's terminal energy within **−0.12 % to +0.31 %** on the six E2 runs (Regional, Urban, LongHaul × two loadings). The code of record with the same VECTO efficiencies is **0.4 % to 1.2 % low** `[TEST partC_vecto_rows.py, partC_columns.csv]`. So the assembly logic is sound; the difference to VECTO is almost all in the efficiency numbers.
Gate 1 and Gate 2 pass. The code of record is byte-identical to Appendix 1.

**What is wrong (ranked by size).**
1. **The fixed efficiencies (0.95 / 0.95 / 0.98) put the result 23 % to 33 % below VECTO** (Regional reference load 0.722 vs 1.050 kWh/km, −31.3 %; Urban 0.598 vs 0.840, −28.8 %; LongHaul −23.4 %). VECTO's E2 chain is far less efficient than 0.884 wheel-to-battery: energy-weighted, driving is **0.64 (Regional) / 0.73 (Urban)**, because the axle and gearbox have a no-load loss that does not shrink with power `[TEST partD_scalar_eta_fit.csv]`. This is not a logic bug. It is the known placeholder problem, now measured. The HDEV result is the non-conservative side (rule 9).
2. **The function cannot take the final producers** (Gate 3). `force_engine` now returns 6 values, the function expects 5, the keyword is `k_rot` not `k_rot_wheel`/`k_rot_rotor`, and `pto_engine` returns 4 values in a different order. Minimal adapter written and checked (bit-identical numbers when `k_rot_rotor = 0` and PTO is off).
3. **Step 6 (PTO) has six defects** (minimal reproducing inputs in Part B): `V == 0` gives stop + 1 rows; a 0 s marker waypoint raises; `is_on = 1` with only a drive profile crashes on `int(NaN)`; drive PTO is silently dropped; no slot for constants; and the loop makes a **year in one array take 69 s instead of 0.25 s** `[TEST partK]`. `PTO_always_on` as an hourly array is not hour-indexed (it is added as-is and crashes).
4. **Rotor inertia is missing** and the sign is decided once at the wheel. Measured effect with VECTO's efficiencies: +0.4 % to +1.1 % of trip energy for the sign split, +0.05 % to +0.4 % for the rotor (together 0.4 % to 1.2 %, the whole gap of the code of record) `[TEST partC_causes.csv]`.
5. **Regen speed limit:** VECTO's source gives **10 km/h for an AMT E2**, not 5 km/h (`GearboxData.cs` 90–99, `Constants.cs` 321). The 1 Hz data agree (no motor-off braking row above 10 km/h). Effect ≤ 0.1 %.
6. **BUG-2 (re-confirmed) and unit conversions:** the `np.clip(...,0,None)` fix works; `+273.15` and `*3.6` can go with zero numerical effect.
7. Empty route returns `0.0 kWh` without error; NaN passes through silently (parser jobs).

**Ranked list of proposed changes** (effect on trip energy of E2 Regional / Urban; engine / parser / defaults; basis; new user input):

| # | Change | Effect | Layer | Basis | New user input |
|---|---|---|---|---|---|
| 1 | Replace placeholders with sourced losses (maps from EU standard values; later) | +31 % / +29 % toward VECTO | defaults + parser (lookup); engine already takes arrays | VECTO E2 `.vmod`; Gate 1 shows Chain S (EU standard values) already gets −7.2 % / +1.2 % `[TEST]` | no (drivetrain type chosen; maps from defaults) |
| 2 | Split step 5: gearbox → (+rotor, +mech. PTO) at motor shaft → motor × inverter; sign per component | +0.4…1.1 % (VECTO-like losses); +0.07 / +0.35 % (scalar) | engine | `ElectricMotor.cs` 186–188, 297, 304–308 | no |
| 3 | `k_rot_rotor` at the motor shaft | +0.05…0.4 % | engine | `ElectricMotor.cs` 186–188, 297; J = 0.4500 kg m² fitted from `.vmod` | `J_rotor` (OEM spec; default from motor type) |
| 4 | `v_no_regen` from gearbox type (AMT 10 km/h, AT 5 km/h) | ≤ 0.1 % | defaults (+ parser picks by type) | `GearboxData.cs` 90–99, `Constants.cs` 321/323 | no |
| 5 | Step 6 rebuilt: `M == 0` standing rows, `searchsorted`, stop/drive profile and constant, mech/electric drive PTO | removes +1 row; 69 s → 0.25 s per year | engine | PR #31 rules; `PTODriveAuxiliary.cs` 38–41 | "does the body have its own electric motor?" (decided) |
| 6 | Cond on when a motor is on (`M` not 0/3) or stop PTO | ≤ 0.02 % | engine | `Conditioning.cs` 83–91 | no |
| 7 | `PTO_always_on` indexed by hour | fixes crash | engine | rule 13 | no |
| 8 | BUG-2 `np.clip`; kelvin and m/s inside | 0 | engine | PR #30; Q12 | no |
| 9 | Return per-part energies (drive, regen, aux, PTO) | 0 (cost < 5 % of run time) | engine | battery engine needs them | no |

Items 2, 3, 4, 6 are small (≤ 1.3 %); by rule 8 only 2 and 3 are worth doing on their own (they follow VECTO's structure, and are needed for maps later). Item 1 is the one that matters for the 5 % target, and it is Bob's open input question.

**Open items** `[OPEN]`: mechanical drive PTO while coasting (Part J run); Municipal `.vmod` does not exist (refuse Part C is `BLOCKED`); independent validation (Part H) is `BLOCKED` for lack of vehicle set-ups.

---------------------------------------------------------------------------------------------------------------------

## 1. Gates

**Gate 1 (PASS).** `docs/research/drag-default-test-2026-11/run_steps.py`, unchanged, run with `VECTO_SRC` pointing at the E2 files of commit b8d6126. Chain S, V1, reference load: RegionalDelivery **0.9749**, UrbanDelivery **0.8502** kWh/km `[TEST step3_kwh_per_km.csv]`. The CSVs were rewritten byte-identically (`git status` clean after the run).

**Gate 2 (PASS).** `gate2_code_of_record.py` → `gate2_result.txt`. `consumption_engine` (notebook cell 16) is **byte-identical** to Appendix 1. `force_engine` has the same code as Appendix 2.1 (comments differ). `P_aux`, `pto_engine` match Appendix 2.2/2.3 (read side by side). `ssm_total_w`, `climate_lookup`, `HVAC_thermal` signatures are listed in the result file. Tested version: **13 Nov notebook**.
`src/engine/consumption.py` is **very stale**: a different function (`consumption(P_wheel, eta_drive=0.95, eta_regen=0.95, eta_dcdc=0.98, P_aux, dt_s)`, 62 lines). It has defaults in the signature, a DC/DC factor of 0.98 where VECTO has 1.0 (`DeclarationData.cs` 124), raises inside the engine, and none of steps 1–4 or 6. `src/engine/force_engine.py` is the old 8-argument version (no `J_rotor`, `i_total`, 5 outputs). Gate 1 still passes because the drag test uses these old files.

**Gate 3 (fails as predicted, adapter works).** `gate3_chain.py` → `gate3_chain.csv`. Real chain on E2 Regional, Urban, MunicipalUtility (refuse):

| Attempt | Result |
|---|---|
| N1 positional hand-over (`*force_engine_out`, 6 values into 5 slots) | `IndexError: too many indices for array: array is 0-dimensional` (everything shifts by one; payload array is read as a scalar) |
| N2 by name (`k_rot_wheel=`, `k_rot_rotor=`) | `TypeError: consumption_engine() got an unexpected keyword argument 'k_rot_wheel'` |
| N3 `pto_engine` outputs in return order into `(pto_1s, pto_on_col, pto_start_col)` | Regional, Urban: **runs silently with wrong meaning** (all-zero PTO, no error). Refuse: `IndexError: index 123 is out of bounds for axis 0 with size 23` |
| Adapter `consumption_engine_v_signature_only` (rename only) with `k_rot_rotor = 0`, PTO off | **bit-identical** to the old function on all 5 outputs, all three cycles |
| Adapter with real `k_rot_rotor` | refused: the rotor would be dropped silently (`ValueError`, by design) |
| Adapter with refuse stop PTO | 96 PTO stops found; PTO + Cond extension = 14.761 kWh (PTO alone is 96 × 0.14993 = 14.393 kWh, exact, see Part B test 6; the 0.368 kWh difference is Cond 600 W on the PTO rows) |

Finding: N3 shows why the contract needs checking by name, not only by position (parser job).
With the 13 Nov code and the placeholders the chain gives Regional **0.7220**, Urban **0.6010**, Municipal (no PTO) **0.7247** kWh/km (HDEV driver rows, VECTO-equivalent air density).

---------------------------------------------------------------------------------------------------------------------

## 2. Part A: line-by-line audit and Q1–Q12

Sign conventions of the `.vmod` columns used here (checked on rows, `partC_vecto_rows.py` header):
`P_wheel_in`, `P_wheelEnd_in`, `P_axle_in`, `P_gbx_in`: **positive = driving**. `P_E2-em_mech`, `P_E2-em_mech_map`, `P_E2-em_el`: **negative = motor drives / draws electricity, positive = generates**. `P_E2-em_inertia_loss`: positive while the rotor speeds up. `P_REESS_T`: **negative = battery discharges** (terminal). `P_aux_el`, `P_DC/DC_*`: positive = load. `EM_E2_off`: fraction of the second the motor was off (0…1). In this review everything is converted to the HDEV convention (positive = drawn from the battery) before it is compared.

### A.1 Line by line (Appendix 1)

| Line(s) | What it does | VECTO stand-in | Verdict |
|---|---|---|---|
| Signature | 37 parameters; efficiencies and `v_no_regen` are arguments; `P_regen_max=None` is the only default | – | OK for purity except the one default (move to `defaults.py` / explicit `None`). Names: `k_rot` is old; `regen_effeiciency` has a typo |
| 1 | `asarray` of inputs | – | OK. `np.asarray(x)` on `T,S,V,M` keeps ints |
| Step 1 | `k_pl = searchsorted(wp_s[has_pl], S, 'right') - 1`; `m_row = m_vehicle + payload` | VECTO has one payload per run | **BUG-2** when `S < wp_s[0]`: index −1 = last payload. Fix `np.clip(...,0,None)` `[TEST test_payload_row_a_hair_before_first_waypoint_BUG2_and_fix]`. Row exactly at a stop takes the NEW payload (`side='right'`) `[TEST]` |
| Step 2 | `hour = ((t_start + T)//3600).astype(int)` | – | OK. Across midnight needs one continuous weather array; too short → `IndexError` (loud) `[TEST]` |
| Step 3 | `rho_row = p/(R(T+273.15))`; CdxA table; `v_kmh = clip(v_avg*3.6, grid)`; linear interpolation | `AirdragDataAdapter.cs` 59–87; VECTO `rho` fixed 1.188 | DEVIATION (already flagged): ρ per hour. Two unit conversions inside (rule 7), see A.2 |
| Step 4 | `P_wheel = m k_lin + m^β k_roll + k_rot + ρ CdxA L` | PR #30 reproduces `P_wheel_in` to ≤ 0.003 % (Regional ref, `partC_columns.csv` column `wheel`: −0.003 %) | MATCH |
| Step 5a | `P_trac = where(P_wheel>0, P_wheel/(η_m η_i η_g), P_wheel*regen)` | VECTO decides at each component | DEVIATION (new, flag): one sign decision; Q2 |
| Step 5b | `M == 3 → 0` | `BatteryElectricMotorController.cs` 44–47 (motor off in Coast/Roll) | MATCH for electric power. VECTO still applies motor drag (`ElectricMotor.cs` 285–292), that is in the driver's drag table |
| Step 5c | `(M==4)&(V<=v_no_regen) → 0` | same file 62–70 | **DEVIATION (new)**: threshold for an AMT is 10 km/h, Q4 |
| Step 5d | `maximum(P_trac, -P_regen_max)` | motor generating curve `ElectricMotor.cs` 191, 211 | Cap is on the electric side here; VECTO caps the motor shaft torque. Never binds on the six runs (Q4) |
| Step 6 loop | PTO placement per stop | `DistanceBasedDrivingCycle.cs` ~226–308 (reference copy) | **BUG** ×6, Part B test 6 |
| Step 6 aux | `ES+PS+HVAC + SP*moving + cond*(moving|pto) + PTO_always_on + pto_row` | `ElectricAuxiliaries.cs` 105–116, `Conditioning.cs` 83–91 | SP MATCH; Cond DEVIATION (small), Q8/Q9 |
| Step 7 | `P_battery = P_trac + P_aux`; `E = Σ P dt / 3.6e6` | `DeclarationData.cs` 124 (DC/DC 1.0) | MATCH (Q7). Terminal energy, not internal (Q11) |

### A.2 Hard-coded numbers, unit conversions, `raise`s

`partA_hardcoded_numbers.csv`, `partA_unit_conversions.csv`, `partA_raises.csv` (AST scan of the cell).

| Number | Where | Class |
|---|---|---|
| `3600` | step 2 (`//3600`) | unit definition (s per h) |
| `273.15` | step 3 | **unit conversion inside the engine** (rule 7) → goes |
| `3.6` | step 3 (`v_avg*3.6`) | **unit conversion inside the engine** → goes |
| `3.6e6` | step 7 | unit definition (J per kWh) |
| `1e-3` | step 6 (`atol=1e-3` m) | HDEV choice: tolerance to find a stop's rows. Not a VECTO constant. A parser/defaults value (`stop_match_tol_m`) |
| `3`, `4` | step 5 | HDEV mode codes of `driver_model` (contract; M: 0 standing, 1 acc., 2 cruise, 3 coast, 4 brake — verified in `driver_model`, see `partA_q6_modes.csv`) |
| `0.0`, `1`, `2` | shapes / neutral | neutral |
| the 5 km/h in a comment | step 5 | VECTO `Constants.cs` 323, but not the E2 AMT value (Q4) |

Unit conversions inside: **two** (`+273.15`, `*3.6`).
`raise`s inside: **two**. (1) `no standing rows found` — can only be known after the driver has run (**post-driver check**; the parser can only check stop time > 0). (2) `PTO does not fit` — stop length and PTO length are known before the driver (**parser check**: standing time = stop + PTO duration).

### A.3 Q1 Power chain of a PEV E2, wheel → battery `[VECTO b8d6126]`

| Order | Component | Where it adds loss / inertia | `.vmod` column(s) |
|---|---|---|---|
| 1 | Wheels | `Wheels.cs` 94–95: `P_wheel_in = torque_in × avg ω`, `P_wheel_inertia = inertia torque × avg ω` | `P_wheel_in`, `P_wheel_inertia` |
| 2 | Brakes | `Brakes.cs` 59–81 (brake torque added to the request), 85–87 (`P_brake_loss`, `P_brake_in`) | `P_brake_loss` (friction brake power), `P_brake_in` |
| 3 | Wheel end | `WheelEnd.cs` (reference copy) | `P_wheelEnd_in` (= wheel + brake loss: e.g. −21.53 + 14.29 = −7.24 kW on an Urban braking row) |
| 4 | Axle gear | `AxleGear.cs` 69–75 (`P_axle_loss`, `P_axle_in`) | `P_axle_in`, `P_axle_loss` |
| – | Angle drive, retarder | not in the generic E2 | – |
| 5 | Gearbox (gear 1/2) | gearbox loss map (`Gear_*.vtlm`); wrapper `PEVGearbox.cs` is 17 lines, loss code not fetched `[OPEN]` | `P_gbx_in`, `P_gbx_loss`, `P_gbx_inertia` |
| 6 | PEV PTO (if any) | `PEVPTO.cs` 54–85: `outTorque + torqueLoss` passed on toward the motor; drive PTO built in `PowertrainBuilderBase.cs` 339–350 | `P_aux_PTO...` |
| 7 | Electric motor E2 (ADC ratio, rotor inertia, map) | `ElectricMotor.cs` 151–466: inertia 186–188, torque map 297, electric power 304–308, drag when off 285–292; modal columns 580–639 | `P_E2-em_mech`, `P_E2-em_inertia_loss` (615), `P_E2-em_mech_map` (600), `P_E2-em_el` (609), `P_E2-em_loss` (611), `EM_E2_off` (619) |
| 8 | Inverter | inside the motor's efficiency map (`LookupElectricPower`) | no separate column |
| 9 | DC/DC for aux | `DeclarationData.cs` 124 `DCDCEfficiency = 1.0` | `P_DC/DC_In = P_DC/DC_Out = P_aux_el` (max difference 0.0 W on all six runs) |
| 10 | Battery | `Battery.cs` / `BatterySystem.cs` | `P_REESS_T` (terminal), `P_REESS_int`, `P_REESS_loss` |

The ADC (`RatioADC = 2.0`) and a constant "MechanicalEfficiency 0.97" in `BatteryElectricVehicle.vveh` belong to the motor's own transmission map. `P_E2_transm_loss` is 0.0 in every row of the Urban file (checked; the others were not checked one by one), so it is not an extra loss here `[TEST]`.

### A.4 Q2 Sign decision per component `[VECTO]` `[TEST partA_q2_sign_decisions.csv]`

VECTO decides at each component: the transmission loss map is evaluated with that component's own torque (`ElectricMotor.cs` 568–577 for the motor-side ADC; `AxleGear.cs`/gearbox maps by their own torque), and the motor map with the motor torque after inertia (`emTorqueMap = emTorque − inertiaTorqueEm`, line 297; electric power from the map at lines 304–308). HDEV decides once on `P_wheel`.
Rows (motor on) where the signs disagree, Regional reference: wheel-end sign ≠ gearbox-in sign in **227 of 5071 rows (4.5 %)**; gearbox-in ≠ motor-map sign (rotor term) in **11 rows**; motor-map sign ≠ electric sign (motor loss larger than the power) in **36 rows**; wheel sign ≠ electric sign in **259 rows (5.1 %)**, carrying 1.18 kWh. Urban: 4.4 % of motor-on rows. Example (Urban row 1522, `.vmod` time 1523): wheel −5.08 kW (regen), axle −3.92, gearbox in **−0.96**, motor map **+0.96** (generating), electric **−0.71 kW (the battery is drained)**. At small regen power the no-load losses are larger than the power; a single multiply by a regen efficiency cannot do this.
The cost of ignoring it: in `partC_causes.csv` cause *a* (one sign decision, VECTO efficiencies) = **−0.67 … −0.96 kWh (−0.7 … −0.9 %)** on Regional, **−0.72 … −0.90 kWh** Urban, −0.34 … −0.83 kWh LongHaul. With scalar efficiencies the same switch costs only −0.07 % / −0.35 % (Part D). So the sign split matters in proportion to how non-proportional the losses are.

### A.5 Q3 Rotor inertia `[VECTO]` `[TEST partA_q3_rotor_size.csv]`

`ElectricMotor.cs` 186–188: `inertiaTorqueEm = Formulas.InertiaPower(emSpeed, prevEmSpeed, ModelData.Inertia, dt) / avgEmSpeed` at the **motor** speed; 194–196 add it to the drive and recuperation limits; 297: `emTorqueMap = emTorque − inertiaTorqueEm`, and the electric power is looked up at `emTorqueMap` (304–308): the rotor torque **goes through the motor efficiency**. `ModelData.Inertia = motorData.Inertia × count` (`ElectricMachinesDataAdapter.cs` 124).
Fit from the `.vmod` (`P_E2-em_inertia_loss = J ω dω/dt`, gear 2, 466 rows): **J = 0.4500 kg m²** (median; 0.225 × 2 motors) `[TEST]`. Total ratio wheel→motor at gear 2: 2.59 × 1.93 × 2.0 = 9.997 (`n_E2-em` check: 1890.3 rpm at the row tested, equal to the formula).
**HDEV's plan is right**: add `k_rot_rotor` after the gearbox efficiency and before motor × inverter. In my variant the sign check is `P_motor = P_shaft + k_rot_rotor` (+ mech. PTO). Size per mission (absolute rotor energy / positive wheel energy): Regional 0.68 %, **Urban 3.06 %**, LongHaul 0.22 %; net over a trip ≈ 0. Peak 3.5 kW (Regional), 17 kW (Urban), 34 kW (LongHaul). Effect on trip energy when it is left out: +0.05 … +0.4 % (Part C cause b; Part D: −0.08 % Regional, −0.44 % Urban).
Gear choice: VECTO runs gear 2 in 9832 of 13489 Urban rows (gear 0 in 3612, mostly standing; gear 1 in 45). Bob's "lowest gear default" (gear 1, i = 19.99) costs **+0.25 % Regional, +1.32 % Urban** vs gear 2 (Part D). That is the conservative side and inside 5 %.
Gear 0 (no gear engaged): VECTO ignores the motor's inertia and drag (`ElectricMotor.cs` 271–276). 254 Urban rows are moving with gear 0 (−0.70 kWh wheel energy, braking).

### A.6 Q4 Regeneration rules `[VECTO]` `[TEST partA_q4_regen_rules.csv]`

* **(a) Speed limit.** `BatteryElectricMotorController.cs` 62–70: no motor if the driver is braking (`DriverBehavior == Braking && DrivingAction == Brake`), **vehicle speed ≤ `GearboxModelData.DisengageWhenHaltingSpeed`** (fallback `Constants...ATGearboxDisengageWhenHaltingSpeed`, 5 km/h, `Constants.cs` 323) and the requested torque is negative. `GearboxData.cs` 90–99: if not set, an AT gets 5 km/h, **any other type (AMT, MT) gets `ClutchDisengageWhenHaltingSpeed` = 10 km/h (`Constants.cs` 321)**. It is only overridden for automatic transmissions and IEPC (`GearBoxDataAdapter.cs` 452–463, 574–583). **The E2 gearbox is an AMT (`AMT.vgbx`), so 10 km/h applies.** The comment in the harness (line 52, "E2 derives it from gear ratios") is not supported by this commit. `VehicleSpeed` is the speed at the **start** of the step (`Vehicle.cs` 326 uses `PreviousState.Velocity`), same as HDEV's `V`. Data: braking rows with the motor fully off have start speed up to **9.94 km/h** (Urban), 9.44 (Regional), 7.5 (LongHaul); **0 rows above 10 km/h**; rows between 5 and 10 km/h with the motor off: 73 Urban, 8 Regional. Motor-on braking rows with start speed < 10 km/h also exist (89 Urban): the other two conditions (driver behaviour) were not met in those, `[OPEN: not needed for HDEV]`. Effect of 5 instead of 10 km/h: −0.10 kWh Urban ref, −0.015 Regional (≤ 0.1 %).
* **(b) Coasting.** Lines 44–47: `Coast` or `Roll` → `null` = motor off, no electric power. MATCH for HDEV's `M == 3 → 0`. Evidence: Coast rows have the motor fully off in 64 of 86 rows (Regional), 207 of 281 (Urban); the rest are 1 Hz rows that mix actions. But in VECTO the motor is **still dragging** (`ElectricMotor.cs` 285–292: `emTorque = DragCurveLookup + inertia`); HDEV puts that in the driver's drag table (drag-default test).
  Not forcing `M == 3` to zero would credit regen on coasting rows: **−0.3 % Regional, −1.5 % Urban** (Part D). That is the non-conservative direction; keep the rule.
* **(c) Braking split.** The brake component (`Brakes.cs` 59–81) takes what the drivetrain cannot or may not take; motor first, friction brake for the rest. In the six runs the friction brake takes 0.083 kWh (Regional ref), **0.876 kWh (Urban ref)**, 0.075 kWh (LongHaul), all at low speed (low-speed rule), 410 Urban rows.
* **(d) Limits.** Motor generating curve (`ElectricMotor.cs` 191, 211; `.vmod` `P_E2-em_gen_max`: 1.2 kW at crawl … 250 kW), battery charge limit (`P_REESS_charge_max` = **1287.6 kW**), inverter (inside the map). Maximum mechanical regen power on the runs: 121 kW (Regional ref), 192 kW (Urban ref), 221 kW (LongHaul ref); electric 109 / 173 / 199 kW. **No row comes within 2 % of the generating limit** (0 rows on all six runs) and the battery limit is 6 times higher than the peak. So **on these declaration cycles nothing binds**; for E2 the motor curve would bind first on a harder mission. A single watt number is a poor proxy because the curve depends on speed (1.2 … 250 kW); `P_regen_max` should be a scalar **or** a per-row array. I propose it as *mechanical* W at the motor shaft (that is where VECTO limits it).

### A.7 Q5 `regen_effeiciency` `[TEST partD_scalar_eta_fit.csv]`

VECTO equivalent: gearbox/axle (regen direction) × motor map incl. inverter (generator mode). Once step 5 is split (Q1), HDEV does not need a separate regen number: the same loss factors apply on the other side of zero (that is what FASTSim does too, Part G). Energy-weighted from the `.vmod`:

| Run | axle+gearbox drive | axle+gearbox regen | motor drive | motor regen | wheel→battery drive | wheel→battery regen |
|---|---|---|---|---|---|---|
| Regional ref | 0.771 | 0.646 | 0.825 | 0.831 | 0.637 | 0.432 |
| Regional low | 0.748 | 0.621 | 0.814 | 0.823 | 0.609 | 0.405 |
| Urban ref | 0.844 | 0.823 | 0.878 | 0.886 | 0.733 | 0.711 |
| Urban low | 0.820 | 0.792 | 0.869 | 0.878 | 0.705 | 0.684 |

The harness value is `REGEN_EFF = 0.95 × 0.95 × 0.98 = 0.884` (`hdev_test_harness_v1.7.py` lines 50–51). VECTO's regen chain is **0.43 … 0.71**, far below 0.884, and below its own drive chain on Regional. A symmetric single number cannot be right for both missions: the asymmetry and the load dependence both come from the no-load loss. Using scalars **fitted to VECTO** (drive and regen separately) reproduces VECTO's own kWh/km within +0.01 % (Regional) and +1.9 % (Urban) on HDEV's driver rows, `[TEST partD_sensitivity.csv]`, but that is a calibration to VECTO, **not validation** (rule 8), and it would need different numbers per mission. The conservative side is the lower regen efficiency (less energy back).

### A.8 Q6 Motor on/off by mode `[TEST partA_q6_modes.csv]`

| HDEV `M` | VECTO `DriverAction` | Motor in VECTO (Regional ref rows) | HDEV today |
|---|---|---|---|
| 0 standing | 0 Halt | off (736 of 746 rows fully off) | P_trac = 0 because P_wheel = 0 |
| 1 acc./cruise | 6 Accelerate | on (4668 of 4684 rows fully on) | drive, or regen on downhill cruise (right: VECTO regenerates downhill in "Accelerate") |
| 3 coast/roll | 4 Coast, 2 Roll | Coast: off (64/86). **Roll: on** (11 Urban rows, EM_off = 0) | 0 |
| 4 braking | −5 Brake | on (334 of 369), off below 10 km/h | regen above `v_no_regen`, 0 below |

`M == 3 → P_trac = 0` is right for Coast. For `Roll` rows VECTO's motor is on (11 Urban rows, 4 LongHaul; 0.026 / 0.069 kWh), HDEV's driver maps Roll to `M == 3`: tiny, flag only. **Uphill coasting:** the driver coasts only when the vehicle is decelerating without power, so the motor stays off in VECTO; I found no row where it matters. **Drive PTO running while coasting:** VECTO's controller returns `null` for Coast/Roll (motor off) and the PTO load is in the torque request upstream (`PEVPTO.cs` 54–85), so what VECTO does is `[OPEN]` → Part J run. HDEV's proposal keeps the PTO power on (conservative).

### A.9 Q7 Aux path `[VECTO]` `[TEST partA_q7_battery_identity.csv]`

`DeclarationData.cs` 124: `DCDCEfficiency = 1.0`. In all six `.vmod` files `P_DC/DC_In = P_DC/DC_Out = P_aux_el` (difference 0.0 W). `P_REESS_T = P_E2-em_el − P_aux_el` holds with an rms residual of 19 … 107 W (max 292 W) from the 1 Hz averaging `[OPEN: the residual is not understood to the watt; it is < 0.1 % of the energy]`. So the aux go **straight to the battery**, not through the inverter. HDEV's `P_battery = P_trac + P_aux_row` is right.

### A.10 Q8 Aux activity `[VECTO]` `[TEST partA_q8_sp_cond_rows.csv]`

* ES, PS, HVAC always on (constants in the `.vmod`: ES 1000 W, PS 200 W, AC 250 W Regional; 162 / 187.5 W Urban). MATCH.
* **SP:** `ElectricAuxiliaries.cs` 105–116: SP (ID `STP`) is dropped when `DataBus.VehicleInfo.VehicleStopped`; `Vehicle.cs` 326: `VehicleStopped => |PreviousState.Velocity| ≤ 0.01 m/s` = **speed at the start of the step**, tolerance 0.01 m/s (`Constants.cs` 327 is a different tolerance, 2e-3 m/s, used elsewhere). HDEV's `V > 0` is the same rule. Rows that differ on Urban reference: **53 of 13489** (VECTO 1 Hz rows blend sub-steps). SP energy is only 0.089 kWh per 100 km (VECTO varies it with speed; HDEV takes one value). MATCH.
* **Cond:** `Conditioning.cs` 83–91 (`GetPEV_SHEVPowerDemand`): demand = `_electricPowerDemand` if **any EM is on or the E-PTO is on**, else 0. HDEV: `moving | pto_active`. Rows that differ on Urban reference: **426 (moving rule) vs 285 (motor-on rule, `M` not 0/3)** of 13489; HDEV on / VECTO off: 366, off / on: 60 (mostly coasting rows, and the first accelerating row with `V == 0`). Energy effect: **0.02 … 0.08 kWh per 100 km** (< 0.1 %). Verdict: small DEVIATION (new, flag); the motor-on rule is the VECTO rule.

### A.11 Q9 Cond with drive PTO `[ASSUMPTION]`

VECTO: mechanical drive PTO runs through the motor, so the motor is on → Cond on. For a body with its own motor, VECTO has no such case (`EPTO` is the stop PTO only, `Conditioning.cs` 33–36 in b8d6126). **Kiro's recommendation:** Cond on whenever a drive PTO (either type) or a stop PTO runs. This is not sourced for the electric-body case → `[ASSUMPTION]`, conservative, ≤ 600 W × PTO hours.

### A.12 Q10 PTO placement `[VECTO]` (re-check, `pto-knowledge`)

Confirmed in source: stop PTO standing time = stop + PTO duration, PTO centred (`DistanceBasedDrivingCycle.cs` ~226–308 in the repo copy; PR #31 quotes 218–220 — line numbers differ between file versions). Drive PTO: `PTODriveAuxiliary.cs` **38–41** throws "Additional PTO activation during drive requested while PTO still active!" (the prompt says line 26; in b8d6126 it is line 40). Engineering mode only (`PowertrainBuilderBase.cs` 325, 339). Torque is added to the motor shaft request (`PEVPTO.cs` 54–85), so Bob's decision 6 (mechanical → step 5 at the motor shaft; electric body → step 6) is consistent with the source.

### A.13 Q11 What VECTO calls "battery energy" `[TEST partA_q11_energy_columns.csv]`

Regional reference load, 100 km: `E_REESS_T_dischg` 109.744 − `E_REESS_T_chg` 4.710 = **105.034 kWh = terminal** (= 1.050 kWh/km, the number used as "VSUM" in PR #23). `E_REESS_int` 110.645 − 4.690 = 105.955 (= `EC_el_SoC` = −ΔE_REESS; internal, includes Ri loss 0.92 kWh = +0.88 %). `EC_el_final` = **106.203 kWh = 1.062 kWh/km** (SoC-corrected, `BatteryElectricPostprocessingCorrection.cs`). Urban reference: terminal 84.0 / internal 85.05 / `EC_el_final` 85.25.
**HDEV's `E_battery` (net terminal energy) is like-for-like with `E_REESS_T_dischg − E_REESS_T_chg` (`P_REESS_T`, sign flipped), not with `EC_el_final`.** `EC_el_final` is 1.1 % (Regional) and 1.5 % (Urban) above the terminal number; when the battery engine adds Ri loss, compare with `EC_el_SoC`/`EC_el_final`.

### A.14 Q12 Steps 1–4 re-check `[TEST]`

* BUG-2 and fix: `test_payload_row_a_hair_before_first_waypoint_BUG2_and_fix`. 
* Kelvin and m/s: `test_kelvin_and_ms_inside_give_the_same_numbers_as_celsius_and_kmh_inside` — identical to 1e-12 with the old function (zero rotor, ideal drivetrain, no PTO). 
* `k_rot_wheel` replaces `k_rot` with no other change: Gate 3 adapter is bit-identical.
* Above 130 km/h the CdxA value is held (decision 17): not tested further (flag only).

---------------------------------------------------------------------------------------------------------------------

## 3. Part B: tests (`tests/consumption/`, `pytest`, 39 tests, 0.6 s)

`python -m pytest tests/consumption -q` (needs `numpy`, `pytest`; the refuse test also needs the repo's `reference/vecto/resources`). All call the notebook function or a named variant. Illustrative inputs are marked `ILLUSTRATIVE` in `tests/consumption/_synth.py`.

| # | Requirement | Test(s) |
|---|---|---|
| 1 | Energy bookkeeping | `test_energy_equals_wheel_work_when_everything_is_ideal` (machine precision, rel 1e-12); `test_rotor_term_is_in_the_proposal...` (wheel work + rotor work) |
| 2 | Each aux alone | `test_always_on_aux_alone[ES/PS/HVAC/PTO_always_on]`; `test_sp_only_when_moving_and_cond_row_counts` (SP rows = rows with V>0; V>0 and M≠0 differ by 1 row); `test_cond_rule_variants_count_rows` |
| 3 | Signs | `test_sign_table_old_function` (positive, negative, zero, coasting, braking above/below `v_no_regen`); `test_coasting_rows_are_zero...`; `test_regen_cap_binds...`; `test_rotor_term_can_flip_the_sign_at_the_motor`; `test_mechanical_drive_pto_flips_the_sign_at_the_motor` |
| 4 | Payload | forward fill + row exactly at a stop; BUG-2 and fix; constant/linear/custom/no stops |
| 5 | Weather | hour across midnight (25 hours needed); too-short array → `IndexError`; HVAC scalar/per hour; **`PTO_always_on` hourly array: old function raises `ValueError` (not hour-indexed), proposal indexes it**; `W1/W2` one row per hour |
| 6 | PTO with final `pto_engine` outputs | stop profile (centred, floor), stop constant (25 rows), drive profile (runs through the next stop), drive constant (sweeper) + overlap `ValueError`, 0 s marker (old raises `no standing rows`), `is_on` with only a drive profile (old: `int(NaN)`), M==0 vs V==0 (**26 vs 25 rows; the old guard lets a 26 s profile into a 25 s stop**), stop at last waypoint, two stops at one distance (**silently doubled → parser must reject**), **refuse cycle 96 × 0.14993 = 14.393 kWh reproduced to 1e-9**, step-6 variant bit-identical |
| 7 | Shapes/types | scalars/arrays/ints; **empty route returns 0.0 kWh without error**; **NaN passes through silently** → parser jobs |

---------------------------------------------------------------------------------------------------------------------

## 4. Part C: row-level reproduction of VECTO

`partC_vecto_rows.py` → `partC_columns.csv` (per file, per column: net/positive/negative energy, %, RMS, max, flagged rows), `partC_causes.csv`, `partC_flagged_rows.csv`, `partC_extra.csv`. Inputs per row: VECTO's speed (start speed = `v_act − acc·dt/2`, PR #30 recipe), acceleration, grade, `dt`, gear → `i_total`, driver action → `M`, mass, ρ = 1.188 (T = p/(Rρ) = 297.2 K), VECTO-fitted CdxA from Bob's `crosswind_engine`, J = 0.45. MunicipalUtility: **BLOCKED: there is no group-2 Municipal `.vmod`** (refuse Part C cannot be done; the refuse PTO energy is checked in Part B).

**Variants (battery terminal energy vs VECTO `−P_REESS_T`, net, %):**

| Variant | Reg. ref | Reg. low | Urb. ref | Urb. low | LH ref | LH low |
|---|---|---|---|---|---|---|
| **C2** proposed logic + VECTO per-row efficiencies + VECTO aux rows + VECTO regen limit | **+0.01** | −0.02 | +0.31 | +0.12 | −0.12 | −0.12 |
| C2c code of record (13 Nov) with VECTO per-row efficiencies | −0.91 | −0.71 | −0.71 | −1.22 | −0.68 | −0.38 |
| **C3c code of record with HDEV placeholders** (0.95/0.95/0.98, regen 0.884, 5 km/h) | **−31.27** | −33.09 | **−28.79** | −31.47 | −23.36 | −26.38 |
| C3 proposed logic with placeholders | −31.17 | −33.01 | −27.83 | −30.58 | −23.32 | −26.36 |

kWh/km (ref load): C2 1.0505 / 0.8429 / 1.5236 vs VECTO 1.0503 / 0.8402 / 1.5255; C3c 0.7219 / 0.5983 / 1.1691.
Per-row efficiencies are computed from the `.vmod` columns per component (axle+gearbox: `P_wheelEnd_in`/`P_gbx_in`; motor: `P_E2-em_mech_map`/`P_E2-em_el`, signed — negative where the motor still draws power while generating). This makes C2 an **assembly test, not a model of the losses** (the answer is partly built in). What it shows: the logic of the proposal is within 0.3 %; the remaining gap of the code of record comes from the logic items below.

**Columns (C2, Regional ref, `partC_columns.csv`, net energy difference HDEV − VECTO):** wheel −0.003 % ; gearbox-in −0.031 % ; motor mechanical (map) −0.466 % (row RMS 1.8 kW) ; motor electric +0.054 % ; aux 0.000 % ; battery terminal +0.012 % (row RMS 5.7 kW). Flagged rows (> 0.1 kW and > 1 % of the VECTO value): wheel 88, gearbox 82, motor mech 199, motor electric 110, battery 110 of 5885. **Explanation of flagged rows** (`partC_flagged_rows.csv`, Regional / Urban / LongHaul ref): 61 / 322 / 26 rows are 1 Hz rows where the motor was on only part of the second (`EM_E2_off` between 0 and 1); 35 / 359 / 12 rows sit next to a driver-action change (1 Hz averaging of ~0.5 s steps); 3 / 32 / 4 are low-speed braking rows; 4 / 39 / 1 use the friction brake; 7 / 111 / 2 unexplained. Net energy of all flagged rows is +0.06 / +0.32 / −0.09 kWh: they cancel.

**Causes isolated one at a time** (change in trip energy vs C2, kWh; negative = lower than C2; `partC_causes.csv`):

| Cause (switch) | Reg. ref | Urb. ref | LH ref | Meaning |
|---|---|---|---|---|
| a one sign decision at the wheel | −0.955 | −0.715 | −0.832 | per-component sign |
| b rotor inertia dropped | −0.076 | −0.358 | −0.054 | rotor term |
| c regen limit 5 instead of 10 km/h | −0.015 | −0.102 | 0.000 | speed rule |
| d no regen cap | 0.000 | 0.000 | 0.000 | cap never binds |
| e Cond rule "moving" vs "motor on" (nominal aux) | +0.019 | +0.075 | +0.018 | aux rule |
| f coasting not forced to zero | −0.279 | −1.151 | −0.575 | non-conservative |

`[OPEN]` The 1 Hz VECTO rows are time averages; they cannot test an exact row-by-row rule below about ±1 s of every mode change. Nothing here depends on that.

---------------------------------------------------------------------------------------------------------------------

## 5. Part D: sensitivity (E2 Regional and Urban, HDEV's own driver rows, reference load)

`partD_sensitivity.py` → `partD_sensitivity.csv`, `graph_partD_tornado.png`. Baseline: proposed engine, scalar gearbox/motor efficiency = average of VECTO's drive and regen energy-weighted values (Regional 0.708 / 0.828; Urban 0.833 / 0.882), gear 2, 10 km/h, nominal aux. Ranges only where sourced (VECTO files / runs); `NO SOURCE` lines are skipped.

| Input | Setting (source) | Regional kWh/km (Δ %) | Urban kWh/km (Δ %) | Inside 5 %? |
|---|---|---|---|---|
| baseline | – | 1.136 (+8.1 % vs VECTO 1.050) | 0.862 (+2.7 % vs 0.840) | – |
| `gearbox_eff` | low / high of the 4 VECTO values | 1.303 (+14.8 %) / 1.038 (−8.6 %) | 0.936 (+8.5 %) / 0.844 (−2.1 %) | **no** |
| `motor_eff` | low / high of the 4 VECTO values | 1.156 (+1.8 %) / 1.131 (−0.4 %) | 0.884 (+2.6 %) / 0.857 (−0.7 %) | yes |
| asymmetric drive/regen (VECTO values) | – | 1.050 (−7.5 %) | 0.856 (−0.8 %) | – |
| `inverter_eff` separately | – | skipped, `NO SOURCE` (the VECTO map already holds it) | | |
| `v_no_regen` 5 km/h | `Constants.cs` 323 | −0.03 % | −0.60 % | yes |
| `P_regen_max` | VECTO per-row limit | 0.00 % | 0.00 % | yes |
| `P_regen_max` as one number | – | skipped, `NO SOURCE` (1.2 … 250 kW depending on speed) | | |
| gear 1 (parser default) | `AMT.vgbx` | +0.25 % | +1.32 % | yes |
| `J_rotor = 0` | – | −0.08 % | −0.44 % | yes |
| Cond rule "moving" | – | +0.01 % | +0.03 % | yes |
| coasting not forced to 0 | – | −0.32 % | −1.54 % | yes (wrong direction) |
| one sign decision | – | −0.07 % | −0.35 % | yes |
| **placeholders 0.95/0.95/0.98** | HDEV | **−36.3 %** | **−29.4 %** | **no** |

Drive PTO mechanical vs electric: one extra line per kW is (1/η_motor×inverter − 1) = +10.8 % of the PTO energy for the placeholders (0.9025), which is `[CALC]` from the placeholders. No sourced PTO power in this job, so no kWh/km line (`NO SOURCE`).
Tornado: the only inputs outside the 5 % target are the efficiencies (gearbox/axle and the placeholders). Logic items are all below 1.6 %.

---------------------------------------------------------------------------------------------------------------------

## 6. Part E: deviation register

| # | Difference (HDEV vs VECTO) | Size (E2) | Sentence for a client report (plain words, no method names) |
|---|---|---|---|
| E1 | Fixed drivetrain efficiencies 0.95/0.95/0.98 vs VECTO loss maps | −23 … −33 % energy | "Energy use is estimated with a simplified drivetrain model. In our checks against the EU reference simulation it comes out roughly 25–30 % lower, so treat it as a lower bound until detailed component data is added." |
| E2 | One sign decision at the wheel vs per component | +0.4 … +1.1 % with VECTO-like losses; +0.07 / +0.35 % scalar | "Small losses at low power are approximated." |
| E3 | Rotor inertia absent in Appendix 1 | 0.05 … 0.4 % | not needed (below 0.5 %) |
| E4 | Regen speed limit 5 km/h (AMT is 10 km/h) | ≤ 0.1 % | not needed |
| E5 | Cond rule (moving vs motor on) | < 0.1 % | not needed |
| E6 | Regen cap not modelled | 0 on the declaration cycles | "Braking energy recovery is assumed not to be power-limited." |
| E7 | Air density per hour vs VECTO 1.188 | PR #30 | existing wording |
| E8 | Aux: ES, PS, HVAC constant; SP one value | 0.03–0.09 kWh per 100 km for SP | not needed |
| E9 | Battery internal loss not in this function | +0.9 … +1.4 % (terminal → internal); +1.1 … +1.5 % to `EC_el_final` | "Battery heating losses are added in a separate step." |
| E10 | Standing aux: ES, PS, HVAC on at standstill (VECTO the same) | Urban 1.26 kWh per 100 km (1.5 %) | "Auxiliary loads are assumed to run all day, including stops." |
| E11 | Mechanical drive PTO while coasting: power kept on (conservative) | `[OPEN]` | "Equipment power is assumed to be drawn even while the truck coasts." |
| E12 | Gear 0 rows (no gear engaged) get no rotor term in VECTO | ≤ 0.7 kWh wheel energy, braking | not needed |

---------------------------------------------------------------------------------------------------------------------

## 7. Part F: physics beyond VECTO (candidates only)

1. **Real-world regen share.** VECTO E2 returns **57 % (Regional), 72.5 % (Urban), 52 % (LongHaul)** of the wheel braking energy at the motor terminals `[TEST partF_vmod_numbers.csv]`. HDEV's share was not computed separately in this job (it depends on the efficiency chosen: with placeholders 0.884 of what the rules let through). Measured values for heavy BEVs (Öko-Institut ELV-LIVE, ICCT, NREL Fleet DNA): **not opened** → "Bob to fetch". Earlier sessions found no independent measured regen share (22 Oct close-out `[SOURCE]` as quoted in `session-closeout-2026-11-03-driver-model-review.md` line 92). Fits vectorisation: yes (already in).
2. **Battery terminal vs internal energy.** Ri loss on E2: +0.88 % (Regional ref), +1.22 % (Urban ref), +1.36 % (LongHaul ref) of terminal energy (`partF_vmod_numbers.csv`). Report only; the battery engine is later.
3. **Aux while standing.** VECTO keeps ES, PS and AC on during `Halt` (P_aux_el = 1.35 kW at standstill on Urban; SP and Cond off). Standing time: 0.21 h Regional, **0.93 h Urban** (3349 s); standing aux energy 0.30 / **1.26** kWh per 100 km = 0.29 % / **1.5 %** of terminal energy. HDEV does the same (ES, PS, HVAC always on). Whether a refuse/urban truck switches ES off during long breaks: no data → decision 10 stays.
4. **Other terms in VECTO's chain that HDEV has no term for:** (a) motor and gearbox **no-load losses** (the dominant one: Part C/D/A.7); (b) inverter loss at zero torque: VECTO has none (EM off → 0 W); (c) gear-shift losses / gear 0: 254 moving gear-0 rows on Urban, −0.7 kWh wheel energy (braking), the effect on battery energy is below 0.1 %; (d) motor drag when off: in the driver's drag table; (e) mechanical efficiency 0.97 of the motor's own ADC (`.vveh`): its loss is inside the loss map and `P_E2_transm_loss` stays 0.

---------------------------------------------------------------------------------------------------------------------

## 8. Part G: how other tools assemble consumption

| Tool | Order of losses | Sign rule | Regen limit | Aux path | Rotor inertia | Where | Read |
|---|---|---|---|---|---|---|---|
| **VECTO** (b8d6126) | wheels → brake → wheel end → axle → gearbox → PTO → motor (ADC, map) → battery; aux via DC/DC 1.0 | each component by its own torque | motor curve (`ElectricMotor.cs` 191, 211), battery limit, low-speed rule | direct to HV battery | at motor shaft, through the map | see Part A | code |
| **FASTSim** (`mohgsaad-art/fastsim`) | transmission first (wheel side) → electric machine → battery (`fastsim-core/src/vehicle/bev.rs` 158–187) | `transmission.rs` 124–131: output power > 0 → `/eff`, else `*eff` = per component, like the proposal | `pwr_out_regen_max` from upstream limits (`transmission.rs` 62–72, `electric_machine.rs` 304–322) | `pwr_aux` computed in `vehicle/vehicle_model.rs` 1077–1205 (base + HVAC) and added at the battery | wheel inertia as a chassis parameter (`vehicle_model.rs` 1618, 0.815 kg m² per wheel); no rotor term found | files named | code (relevant parts) |
| **eflips-depot** (fork) | none: consumption by lookup table `(incline, t_amb, level_of_loading, mean_speed_kmh)` → kWh/km (`api/private/consumption.py` 92–175), interpolator cached per LUT id (lines ~41–60) | – | – | in the LUT | – | `consumption.py` | code (first 200 lines) |
| **spice_ev** (fork) | none: vehicle energy per trip is an input; battery `efficiency=0.95` is a constructor default (`battery.py` 7–8) | – | – | – | – | `battery.py`, `scenario.py` | code (headers) |
| **acnportal** (fork) | none: battery charging model only (`acnsim/models/battery.py`) | – | – | – | – | – | file names + class list |
| **blast-lite** (fork `BLAST-Lite`) | none: battery degradation models (`blast/models/*`) | – | – | – | – | – | file list |
| **dt-cargo** (fork) | none: recorded driving data and track metadata (`input/public/*.csv`, notebook) | – | – | – | – | – | file list |
| TU Graz **PHEM** | – | – | – | – | – | **NOT READ** | – |
| Argonne **Autonomie** | – | – | – | – | – | **NOT READ** (only landing pages seen: anl.gov/taps/autonomie-vehicle-system-simulation-tool) | summary only |
| US EPA **GEM** | – | – | – | – | – | **NOT READ** | – |

Difference from HDEV: FASTSim and VECTO both decide the sign per component and chain components; HDEV Appendix 1 collapses them. The proposal follows them. The other forks have no such step (they take energy per km or per trip as input) — which is the reason HDEV needs this engine.

---------------------------------------------------------------------------------------------------------------------

## 9. Part H: independent validation

**Status: `BLOCKED` for like-for-like comparison.** None of the sources below gives the full vehicle set-up (mass, payload, route/cycle, aux, HVAC, battery) needed to run HDEV for *that* vehicle. A difference in % without that would be invented. What I found (all `[SOURCE, snippet]`: search snippets only, **not model inputs**):

| Source | Value | What is missing to run HDEV |
|---|---|---|
| Vandijck eActros 600, 950-mile test, [fleetequipmentmag.com](https://www.fleetequipmentmag.com/eactros-600-trial-vandijck-transport/) (2025) | 96.3 kWh/100 km | mass, route profile, temperature, aux |
| Electrek, eActros 600 German winter, [electrek.co](https://electrek.co/2026/06/27/mercedes-posts-tesla-like-efficiency-hauling-36-tons-through-a-german-winter/) (27 Jun 2026) | ~100 kWh/100 km average Nov–Feb at 36 t | route, temperature series, tyre class |
| ADAC eActros 600 test, [adac.de](https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/mercedes-benz-eactros-600/) (2024) | ~88 kWh/100 km | route, mass |
| eActros 600 winter tests, [electriccarsreport.com](https://electriccarsreport.com/2025/02/mercedes-benz-eactros-600-completes-winter-tests/) (Feb 2025) | +25 % with tyre class B and winter vs class A | tyre Crr values |
| VTT electric refuse truck, [vttresearch.com](https://www.vttresearch.com/en/project_news/refuse-truck-future-hums-along-quietly-without-emissions) (2023) | 2.3 kWh/km in collection, 1.4 kWh/km driving | mass, cycle, PTO power, stops |
| Waste-collection vehicle study (TU Berlin), [trid.trb.org](https://trid.trb.org/View/1852414) (2021) | mean 1.85 kWh/km (eWCV) | route data |
| Earlier set (this repo): `docs/research/drag-default-test-2026-11/step4_real_trucks.csv` | 0.66 … 1.14 kWh/km for 7–19 t trucks, all marked "not like-for-like" there | same |

Context only: HDEV with the 13 Nov placeholders gives **0.72 (Regional) / 0.60 (Urban) kWh/km**, which sits *inside* the OEM and measured figures for similar-size trucks in the repo table (0.66–1.14), while VECTO's own E2 numbers are **1.05 / 0.84**. This is the point of rule 8: the placeholders look plausible against OEM figures but they are 23–33 % below the audit reference, and the independent figures are mostly best-case or different trucks. I cannot say from these sources which of 0.72 or 1.05 is closer to a real E2 truck. Conservative choice (rule 9): not to go below VECTO.
Searched for papers up to 13 Nov 2026; nothing newer than the items above gave a usable set-up. VECTO newer than 5.1.6-RC: not found in the search; the consolidated Regulation (EU) 2017/2400 of 01.01.2026 exists on EUR-Lex ([eur-lex.europa.eu](https://eur-lex.europa.eu/eli/reg/2017/2400/2026-01-01/eng/xhtml)) but is too large to open here (10 MB limit) → Bob to fetch.

---------------------------------------------------------------------------------------------------------------------

## 10. Part I: proposed `consumption_engine_v_proposed`

In `reference_copy.py` (read top to bottom; ~80 lines). Constraints met: pure; SI inside (kelvin, m/s); no defaults in the signature; no input checks; vectorised (the only loop is over stops with PTO inside `pto_rows`, with `searchsorted`); efficiencies are scalar **or** per-row arrays (checked in Part C with per-row VECTO arrays).
Tests: `tests/consumption/test_proposed.py` (the proposal equals the old function where it should and differs only where intended).

**Signature changes:** `k_rot` → `k_rot_wheel, k_rot_rotor`; `T_amb_h` in K; `cdxa_v` in m/s; PTO inputs → `wp_stop, is_on, pto_start, stop_1s, drive_1s, stop_const_W, drive_const_W, drive_pto_mechanical`; `regen_effeiciency` removed; `P_regen_max` (mechanical W at the motor shaft, scalar/array/None); no default values.

**Before / after, with measured effect (E2 Regional / Urban; "C" = Part C; "D" = Part D):**

1. **Step 1 (engine)** — `k_pl = np.searchsorted(...) - 1` → `k_pl = np.clip(np.searchsorted(...) - 1, 0, None)`. Why: BUG-2 `[TEST]`. Effect: 0 on realistic inputs.
2. **Step 3 (engine)** — `rho_row = p_air / (R_air * (T_amb_h[hour] + 273.15))` → `p_air / (R_air * T_amb_h[hour])`; `v_kmh = np.clip(v_avg * 3.6, ...)` → `v_c = np.clip(v_avg, cdxa_v[0], cdxa_v[-1])` with `cdxa_v` in m/s. Why: rule 7, decision 15. Effect: 0 (1e-12). The parser converts °C→K and km/h→m/s once.
3. **Step 4 (engine)** — `k_rot` → `k_rot_wheel`. Effect 0.
4. **Step 5 (engine)** — before:
   ```python
   P_trac = np.where(P_wheel > 0, P_wheel / (motor_eff*inverter_eff*gearbox_eff), P_wheel * regen_effeiciency)
   ```
   after:
   ```python
   P_shaft = np.where(P_wheel > 0, P_wheel / gearbox_eff, P_wheel * gearbox_eff)     # sign at the wheel
   P_motor = P_shaft + k_rot_rotor + P_pto_mech                                      # ElectricMotor.cs 186-188, 297
   P_motor = np.maximum(P_motor, -P_regen_max) if P_regen_max is not None else P_motor
   P_trac  = np.where(P_motor > 0, P_motor / eta_m, P_motor * eta_m)                 # sign at the motor
   ```
   Why: Q1–Q3, Q5. Effect: **+0.4 … +1.1 %** (sign split) and +0.05 … +0.4 % (rotor) with VECTO-like losses (C a, b), +0.07 / +0.35 % (+rotor +0.08 / +0.44 %) with scalars (D). New input: `J_rotor`, `i_total` (parser; default from motor/gear data). Layer: engine.
5. **Step 5e (engine + defaults)** — `v_no_regen` 5 → 10 km/h for an AMT. Effect ≤ 0.10 kWh (0.1 %). Layer: defaults (value by gearbox type), parser picks it.
6. **Coasting with a running mechanical PTO (engine)** — `np.where(M == 3, 0.0, P_trac)` → `np.where(M == 3, pto_el, P_trac)`; `pto_el = P_pto_mech / eta_m`. `[OPEN]` Part J. Effect 0 without drive PTO.
7. **Step 6a (engine)** — the per-stop `np.where` scan with `V == 0` → `pto_rows(...)` (`searchsorted`, `M == 0`, stop/drive, profile/constant, overlap error). Effect: removes the stop+1 row (one PTO second on the accelerating row, `[TEST]`); drive PTO now counted; **time per call on the refuse day 2.8 ms → 1.0 ms; year in one array 69.4 s → 0.30 s**.
8. **Step 6b (engine)** — `cond * (moving | pto_active)` → `cond * (motor_on | stop_active)`, `motor_on = (M != 0) & (M != 3)`; `PTO_always_on` indexed by hour; electric drive PTO added to aux. Effect: ≤ 0.02 %.
9. **Step 7 (engine)** — returns a dict: `P_wheel, P_motor, P_trac, P_aux_row, P_battery, E_battery, E_drive, E_regen, E_wheel_braking, E_aux, E_pto_stop, E_pto_drive`. What downstream needs: the **battery engine** needs `P_battery` per row (W, positive = discharge); **charging/session list** needs `E_battery` per route and per date and, for sizing, the peak of `P_battery`; the **report** needs energy by part (drive, regen, aux, each PTO). Cost: 6 extra reductions over the rows; at 4389 rows the whole function is 1.0 ms vs 0.9 ms without them (`partK`).

**Not changed:** the placeholders. Replacing them with sourced loss maps is the one change that moves the result more than 5 % and is the open input question.

---------------------------------------------------------------------------------------------------------------------

## 11. Part J: VECTO runs for Bob

One run is needed (`reference/vecto/jobs/consumption-2026-11/README.md`): drive PTO while the truck coasts (Q6/Q9). Everything else was closed from source and the six `.vmod` files.

## 12. Part K: performance

`partK_performance.py` → `partK_runtime_machine_dependent.csv` (machine dependent; mean of 5 runs, 3 for the year loops; CPU: Intel Xeon Platinum 8488C, 8 logical CPUs; Python 3.11.15, numpy 2.4.6). Refuse day: 4389 rows, 96 PTO stops.

| Case | Code of record | Step 6 `searchsorted` only | `consumption_engine_v_proposed` |
|---|---|---|---|
| one day, one call | 2.8 ms | 0.9 ms | 1.0 ms |
| year = 250 calls | 0.65 s | 0.23 s | 0.28 s |
| year = one array (1.1 M rows, 24 000 PTO stops) | **69.4 s** (one run) | 0.25 s | 0.30 s |

The step-6 variant is **bit-identical** to the code of record on the refuse day. One long array is **not faster** than 250 calls (0.30 s vs 0.28 s), so the loop over dates is the simpler choice. What to cache: the hour index (`(t_start+T)//3600`, key: route id + t_start), the CdxA table `cdxa_tab` (key: weather year id + vehicle CdxA0), `standing` row indices per stop (key: route id + driver version), and the `force_engine` outputs (key: route id + vehicle ref mass + gear).

---------------------------------------------------------------------------------------------------------------------

## 13. Part L: the layers around the engine

Evidence read for this part (code, not summaries): pvlib-python `pvlib/modelchain.py` and `pvlib/iotools/pvgis.py` ([github.com/pvlib/pvlib-python](https://github.com/pvlib/pvlib-python)); Bob's forks of FASTSim, spice_ev, eflips-depot (files named below); the repo's own `src/resolver`, `src/registry`, `src/data_fetch`, `src/server/runner.py`, `src/validate`. **Not read:** PyPSA, OpenModelica/FMI (not relevant enough to open, no claim made). General practice — *named, not opened in this job* `[SOURCE, not opened]`: pydantic ([docs.pydantic.dev](https://docs.pydantic.dev/)), "functional core, imperative shell" (Gary Bernhardt, *Boundaries*, 2012), ports-and-adapters (A. Cockburn, "Hexagonal architecture", 2005), JSON Patch (RFC 6902).

### Q-L1 Layers and order

What pvlib does `[pvlib]`: physics functions are separate and pure; `iotools` fetch/read data (`pvgis.get_pvgis_hourly`, line 46, does the HTTP call at line 231 with a `timeout` and then hands the text to `read_pvgis_hourly` (line 315), a pure reader of a file or stream; both return `(data, metadata)`, the metadata keeping the query); `ModelChain` (`modelchain.py` 248) is the orchestrator with presets (`with_pvwatts` 363, `with_sapm` 452), an **infer** step (`infer_dc_model` 580 picks the model from which parameters exist and raises a clear `ValueError` if it cannot), a **verify** step before running (`_verify_df` 1251, `prepare_inputs` 1342), and a result dataclass (`ModelChainResult` 97). FASTSim: one struct per component with its own `solve` (`vehicle/bev.rs` 158–187). spice_ev: the scenario is built from a plain dict (`Scenario(json_dict, dir_path)`, `scenario.py` 19–31) and `simulate(args)` accepts an `argparse.Namespace` **or a dict** (`simulate.py` 14–23). eflips-depot: consumption by lookup table with a cache keyed by table id (`api/private/consumption.py` 41–60, 92–175).

**Kiro's recommendation** (one structure):

```
fetch (I/O only)  ->  raw store (immutable, query + date)  ->  parser (clean, convert, look up, fill, CHECK)
   -> defaults (layered, origin kept)  ->  run layer (loops, caches, post-driver check)  ->  engine (pure SI maths)
   -> results (numbers + provenance)  ->  report
```
Order of value resolution inside the parser: **base defaults → input-source defaults (e.g. VDRI) → OEM/spec file → user override**. Each value keeps `{value, unit, origin: [layer, reference, date]}`; a later layer replaces an earlier one unless the earlier one is `locked` by an input source.

Where today's files fit:

| Existing | Role in the recommendation | Redundant / change |
|---|---|---|
| `src/engine/*.py` (stale copies) | replace by the notebook functions (code of record) | `consumption.py`, `power_step.py`, `force_engine.py` are stale; `weather_for_rows.py` (126 lines) not read — check whether `hour`-indexing belongs in the engine (it does, step 2) |
| `src/resolver/defaults.py` | becomes `defaults.py` (add unit and layer) | see Q-L2 |
| `src/resolver/waypoint_parser.py`, `resolve_typed.py` | parser (`Waypoint`, vdri/vacc text parsing; typed route summary → waypoints, with its own `raise`s and assumption list: a good pattern) | keep |
| `src/resolver/calendar.py`, `session_handover.py` | parser (calendar) and run-layer output (session list) | not read in detail |
| `src/registry/{slot,fields,levers,registry}.py` | UI-facing metadata and the stored value shape | `Slot.source` mixes "who" and "what kind"; overlaps `provided_by` |
| `src/validate/validator.py` | checks of UI patches (field ranges) | keep for the UI; the engine-input checks are a separate module `parser/checks.py` |
| `src/server/runner.py` | run layer: `apply_change_sets` (top-level keys only), `check_entry_contract`, `select_start_stage`, `run` (all engines still stubbed to null) | `apply_change_sets` cannot address "vehicle v1, mass"; see Q-L6 |
| `src/data_fetch/dmi_weather_climatology.py` | fetch layer, after the split | see Q-L4 |

### Q-L2 `defaults.py`

Reviewed: `src/resolver/defaults.py` has `_d(value, source, label)` with `label ∈ {VECTO, REG, literature, HDEV ASSUMPTION}` and a hard failure on an unknown label (good), and `value=None` where there is no source (good: rule 2). Missing: **a `unit` field** (units are in comments), a **structured reference** (document + line/table, instead of a free string), the **layer** (base / input-source / OEM), and the per-input-source **provides / locks**. `src/registry/slot.py`: 8 fields `{value, unit, source, date, label, provided_by, locked, version}` — it has the unit, `locked` and `version` (good), but no reference and no record of which layer overrode which; `label` is the client-facing text while the provenance label lives only in `defaults.py`.

Proposal:
```python
Default = {"value": 0.225, "unit": "kg m2", "ref": {"doc": "GenericEMotor_125kW_485Nm.vem", "where": "Inertia", "commit": "b8d6126"},
           "label": "VECTO", "layer": "base", "client_label": "motor rotor inertia"}
INPUT_SOURCES = {"vdri": {"provides": ["wp_s", "wp_v", "wp_grade", "wp_stop", "wp_pto"], "locks": ["wp_s", "wp_grade"]},
                 "typed": {"provides": ["total_distance_m", "n_stops", "avg_stop_duration_s", "cruise_speed"], "locks": []}}
```
Entries found in this review that belong there: Part "defaults.py entries found" below.

### Q-L3 Checks that only work after the driver model

Keep the engine free of checks: put them in **one pure function in the run layer**, `run/contract.py: check_rows(rows, waypoints, pto) -> list[str]`, called once per route right after `driver_model`/`force_engine`, before any `consumption_engine` call; any non-empty list stops the run with the list. What others do: pvlib verifies inputs in the orchestrator before the physics (`ModelChain._verify_df` 1251, `prepare_inputs` 1342), not inside the physics functions; spice_ev asserts inside `Scenario`'s loop (`scenario.py` 226–270), i.e. also in the orchestrator. List of post-driver checks: below.

### Q-L4 Live data (DMI now; prices, site load later)

* **Who fetches:** a function in its own layer, `fetch/fetch_dmi.py: fetch_dmi(station, parameter, resolution, start, end, store, now_utc) -> RawRecord`. It does HTTP and file writing and **no maths**. `now_utc` is passed in (no clock inside). It is called by the **run layer** in a "prepare data" step, **not by the parser, not by the engine**.
* **When:** only when the project says `weather.source = "live"` or `"latest"`. The run layer first resolves it to a concrete period (e.g. last 12 months to yesterday) and a concrete fetch; everything after works with that snapshot.
* **Where stored:** `data/raw/<provider>/<station>/<parameter>_<resolution>_<start>_<end>.json` plus `query.json` next to it: URL, parameters, `retrieved_at_utc`, provider API version, station id/name/distance, row count, `sha256` of the raw file. Raw files are never edited. `build_weather(raw, ...)` is pure (decided 6 Oct) and turns raw into hourly arrays in SI (K, m/s).
* **Reproducible reports:** the run record stores the snapshot id (hash). Re-running an old report reads the stored snapshot; it never re-fetches.
* **Cache rules:** key = provider + endpoint + station + parameter + resolution + period; a snapshot for a closed period is valid forever; "latest" always makes a new snapshot unless one younger than a TTL exists (TTL is a defaults.py value, `NO SOURCE`, Bob decides).
* **Offline:** use the newest stored snapshot that matches the key, mark it in the report as "stored data, age X days"; if there is none: **refuse with a `BLOCKED: no weather data` message** (no silent climatology).
* **Report shows:** provider, station name/id/distance, period, retrieval date, snapshot hash, data-layer version.
* **Review of `src/data_fetch/dmi_weather_climatology.py` (DRAFT):** (1) the last lines **run a network call when the file is imported** (`clim = get_wind_temp_climatology(55.68, 12.45)`) and print; (2) fetch and calculation are mixed (the decided split is not made); (3) it averages each calendar day across years (known; against the 6 Oct decision); (4) daily means, but the engine needs hourly arrays (`timeResolution="hour"`: `[OPEN]` check that DMI offers it for these parameters); (5) nothing is saved raw and no query/date is kept; (6) output is `month_day`, not a dated series, so a continuous array across midnight cannot be built; (7) °C and m/s without the kelvin step; (8) wind height versus `h_ref` is unchecked (noted in its own header); (9) period is hard-coded in the signature defaults.

### Q-L5 Run layer now and later

Minimal harness that does not need rewriting: **one function** `run/pipeline.py: run(project: dict, changes: list | None = None, *, fetch: bool = False) -> Result`, and a 20-line script `harness/run_project.py project.json [--changes changes.json] --out out/` that only reads files and calls it. FastAPI later is `@app.post("/run") def run_endpoint(body): return pipeline.run(body.project, body.changes)`. This is the spice_ev pattern (`simulate(args)` for Namespace **or** dict). The existing `runner.run(base, changes)` already has this shape.
Loop, efficient and simple:
```
for vehicle in vehicles:
  for route in assigned_routes(vehicle):
    rows = driver_model(route, reference_mass)          # once per route + vehicle drag/vacc
    fe   = force_engine(rows, vehicle)                  # once per route + vehicle + gear
    contract.check_rows(rows, route, pto)               # post-driver check, once
    for date in operating_dates(vehicle, route):
        out = consumption_engine(rows, fe, weather[date], payload, aux, pto, drivetrain)    # 1.1 ms per day (Part K)
```
Stacking all dates in one array is not faster (0.30 s vs 0.28 s for a year), so loop. Cache keys: Part K.

### Q-L6 Project JSON

```python
class Project(BaseModel):                      # pydantic v2
    schema_version: Literal["1.0"]
    vehicles: dict[str, Vehicle]               # id -> {type, mass_empty_kg, payload_max_kg, drivetrain{...}, body{has_own_motor: bool|None, ...}}
    routes: dict[str, Route]                   # id -> {source: "vdri"|"typed"|"gps", waypoints[...], pto[...]}
    assignments: list[Assignment]              # {vehicle_id, route_id, rule: CalendarRule}
    calendar: Calendar                         # operating dates, depot hours
    weather: WeatherSpec                       # {source: "year:2024"|"latest"|"file:..."}
class Change(BaseModel):
    path: str                                  # JSON Pointer, e.g. "/vehicles/v1/mass_empty_kg"
    op: Literal["set", "unset"]
    value: Any = None
    provided_by: str
```
Raw fields are `None` when the user gave nothing (the parser fills them from `defaults.py` and records the origin). **Scenario = base + `list[Change]`** applied to a deep copy; the base file is never written; the run record stores `sha256(base)`, the change list and the schema version. `runner.apply_change_sets` only writes top-level keys and cannot address "mass of vehicle v1": paths fix that. **Versioning:** `schema_version` string; one migration function per step (`migrate_1_0_to_1_1(dict) -> dict`), chained; an unknown major version is refused.

### Recommended structure (Kiro's recommendation)

```
hdev/
  engine/                  PURE maths, SI only, no defaults, no checks, no I/O (the notebook functions, one file each)
    crosswind_engine.py  payload_engine.py  driver_model.py  force_engine.py  p_aux.py  pto_engine.py  hvac_thermal.py
    consumption_engine.py  (battery_engine.py, charging later)   weather.py  <- build_weather (pure)
  defaults.py              every default: value, unit, ref, label, layer; INPUT_SOURCES provides/locks
  schema.py                pydantic models: Project, Change, Vehicle, Route ... + schema_version + migrations
  parser/
    resolve.py             layered fill (base -> input source -> OEM -> user), keeps origin per value
    checks.py              all input checks that can be made before the driver model
    to_engine.py           resolved project -> engine arguments (km/h->m/s, degC->K, gear->i_total ...)
  fetch/
    fetch_dmi.py           HTTP + raw file + query.json, nothing else (later: fetch_prices.py, fetch_eloverblik.py)
  run/
    pipeline.py            run(project, changes) -> Result   (the loops, the caches)
    contract.py            post-driver checks, pure
    scenario.py            apply Change list to a deep copy
    report.py              numbers + provenance (snapshot ids, assumptions list)
  api/                     later: FastAPI, thin (parse request, call run(), return JSON)
harness/run_project.py     now: project.json (+ changes.json) in, results out
data/raw/                  immutable fetched files + query.json (git-ignored)
tests/                     engine (analytic + VECTO rows), parser, run
```
**Main alternative:** a pvlib-style `ModelChain` class that holds the project, the rows and the results as attributes and has `.run()`. Why not: it hides what goes in and out of each step, makes caching by key harder, and Bob wants plain functions he can read top to bottom. **Second alternative:** keep the registry `Slot` as the core value type for everything. Why not: it has no origin chain and mixes "who" and "what kind"; it is fine as the UI-facing shape.

---------------------------------------------------------------------------------------------------------------------

## 14. Input table for the UI (every input of `consumption_engine`)

"Fleet user" = can a fleet customer realistically give it. "Default" = best sourced default; `NO SOURCE` where none. "Conservative end" = which direction gives more energy.

| Input | Unit | Who produces it | Fleet user can give? | Sourced default | Conservative end |
|---|---|---|---|---|---|
| `T, S, V, M, dt` | s, m, m/s, –, s | `driver_model` | no (computed) | – | – |
| `k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg` | W/kg … | `force_engine` | no | – | – |
| `m_vehicle` | kg | parser (user / OEM file) | yes (curb mass + body) | VECTO `Body_Trailers_Weights.csv` (B2 1900 kg), curb 4670 kg (generic E2 `.vveh`) | higher mass |
| `wp_s`, `payload_wp` | m, kg | route (vdri/typed/gps) + `payload_engine` | route: yes; payload: roughly | VECTO `Payloads.csv` 50 % column (E2: 3019.6 kg) | higher payload |
| `beta` | – | defaults | no | 0.9 (VECTO `Physics.cs`; used in PR #30) | – |
| `t_start` | s | calendar | yes (shift start) | – | cold hours |
| `T_amb_h` | K | `build_weather` | no (location) | live DMI / climate year | colder (denser air, more HVAC) |
| `W1, W2` | – | `crosswind_engine` | no | declaration wind 3 m/s at 4 m, Hellmann 0.2 (VECTO `Physics.cs` 56–66) | stronger wind |
| `cdxa_v` (m/s grid), `CdxA0` | m/s, m² | defaults / parser | CdxA: rarely | VECTO `Constants.cs` 355–357 grid; CdxA by vehicle class (`CdxA_Default` is locked `NO SOURCE` in `defaults.py`) | higher |
| `p_air, R_air` | Pa, J/(kg K) | defaults | no | 101325 Pa, 287.058: ISO 2533 `[STD, not opened here; Bob to confirm]` | – |
| `ES, PS, HVAC, SP, cond` | W electric | `P_aux` (+ `HVAC_thermal`) | HVAC: no; rest: no | VECTO aux tables (`DeclarationData.cs`); E2 values in the `.vmod` | higher |
| `PTO_always_on` | W (scalar or per hour) | parser | yes (fridge, mixer) | – (`NO SOURCE`) | higher |
| `wp_stop` (FINAL standing time), `is_on, pto_start, stop_1s, drive_1s` | s, –, s, W | parser + `pto_engine` | stop times: yes; PTO profile: sometimes | VECTO refuse profile `.vptoel` (0.14993 kWh per stop) | longer PTO |
| `stop_const_W, drive_const_W` | W | parser (user) | yes | – | higher |
| `drive_pto_mechanical` | yes/no | user ("does the body have its own electric motor?") | yes | – | mechanical (more energy: ÷ η) |
| `gearbox_eff, motor_eff, inverter_eff` | – (scalar **or** per row) | defaults (placeholders) → maps later | no (spec sheets, rarely) | 0.98 / 0.95 / 0.95 = **HDEV placeholder, flagged**; VECTO E2 energy-weighted: gearbox+axle 0.65–0.84, motor+inverter 0.82–0.89 `[TEST]` | lower |
| `v_no_regen` | m/s | defaults by gearbox type | no | AMT 10 km/h, AT 5 km/h (`Constants.cs` 321/323, `GearboxData.cs` 90–99) | higher |
| `P_regen_max` | W at motor shaft (or per row) / `None` | defaults / motor spec | rarely | E2 generic: speed-dependent 1.2…250 kW; single value `NO SOURCE` | lower |
| `J_rotor`, `i_total` (into `force_engine`) | kg m², – | parser (gear → ratio) | no | 0.225 kg m² per motor (generic `.vem`); gear ratios from `.vgbx`; unknown gear → lowest gear (decided) | gear 1 |

## 15. Parser jobs found

1. Convert °C → K (`T_amb_h`) and km/h → m/s (`cdxa_v` grid, waypoint speeds, `v_no_regen`) once.
2. Final standing time = stop time + PTO duration (`wp_stop`), `is_on[0] = 0` (pto_engine does it silently on a copy), and check the PTO fits into the stop **before** the driver (replaces `raise` "PTO does not fit").
3. Reject two stop waypoints at the same distance (otherwise the PTO is laid twice, test 6).
4. Reject empty routes (energy 0.0 without error) and any NaN/inf in any engine input (NaN propagates silently).
5. `pto_engine` turns time steps into whole seconds with `.astype(int)`: a fractional step length is truncated silently → check that PTO profile times are integer seconds (seen in passing, `pto_engine`).
6. `PTO_always_on`, `HVAC`, `T_amb_h`, `W1`, `W2` shapes: weather arrays must cover hours `0 … floor((t_start + T[-1])/3600)` and be one continuous array across midnight; `W1/W2` one row per hour; `PTO_always_on` scalar or per hour.
7. Efficiencies in (0, 1]; `v_no_regen` chosen from gearbox type; `i_total` per row from gear (unknown gear → lowest gear); `J_rotor` from motor data × count.
8. Name-based hand-over of producer outputs (Gate 3, N3 ran silently with wrong meaning).
9. The yes/no input "does the body have its own electric motor?" → `drive_pto_mechanical`.

## 16. `defaults.py` entries found (value, unit, source)

| Entry | Value | Unit | Source |
|---|---|---|---|
| `v_no_regen` AMT / AT | 10 / 5 | km/h → m/s in parser | `Constants.cs` 321 / 323, `GearboxData.cs` 90–99 |
| `dcdc_efficiency` | 1.0 | – | `DeclarationData.cs` 124 (already in `src/resolver/defaults.py`) |
| `motor_eff, inverter_eff, gearbox_eff` placeholders | 0.95, 0.95, 0.98 | – | **HDEV ASSUMPTION** (harness v1.7 line 50), flagged |
| `J_rotor` generic E2 | 0.225 per motor | kg m² | `GenericEMotor_125kW_485Nm.vem` Inertia; × count (`ElectricMachinesDataAdapter.cs` 124) |
| E2 gear ratios | axle 2.59; gear 1 3.86; gear 2 1.93; ADC 2.0 | – | `AMT.vgbx`, `BatteryElectricVehicle.vveh` |
| `stop_match_tol_m` | 1e-3 | m | HDEV choice (replaces the literal in step 6) |
| `p_air`, `R_air` | 101325; 287.058 | Pa; J/(kg K) | ISO 2533 `[STD, not opened]` |
| `beta` | 0.9 | – | VECTO `Physics.cs` (`beta_vecto` already in `defaults.py`) |
| `P_aux` efficiency factors (move out of the signature) | ES 0.7, PS 1.0, HVAC 1.25, SP 0.7, cond 1.0, PTO 1.0 | – | `DeclarationData.cs` 123 (alternator 0.7), 126 (HVAC factor 0.8 → 1/0.8) |
| weather snapshot TTL | – | s | `NO SOURCE` |

## 17. Post-driver checks found

1. Every stop with PTO has contiguous standing rows (`M == 0`, same `S` within `stop_match_tol_m`) and as many as the final stop time (replaces `raise` "no standing rows found").
2. Driver `S` increases and ends at `wp_s[-1]`; payload array length equals the waypoints; `T` has uniform `dt` and starts at 0.
3. `M` values in {0,…,4}; no NaN in `T,S,V,M,A`; `V ≥ 0`.
4. Weather array long enough for the last row's hour (the engine's `IndexError` is a loud last resort).
5. Warning when `v_avg` exceeds the CdxA grid (130 km/h): the value is held (decision 17, VECTO throws).
6. Drive-PTO profile overlap (error, mirrors VECTO) — can also be done earlier from the profile length and the stop pattern.

## 18. Seen in passing (out of scope)

* `pto_engine`: `.astype(int)` truncates fractional second steps (line `stop_steps = np.diff(...).astype(int)`).
* `P_aux` has defaults in its signature (decided to move).
* `driver_model` default thresholds `lac_min_v=50`, `os_min_v=50`, `os_allowed=2.5`, `v_min_coast=5` are km/h-sized numbers compared with m/s (PR #30 Part D); callers must pass m/s.
* `crosswind_engine` takes `v_veh_kmh` and converts inside (rule 7), outside this review.
* `PTODriveAuxiliary.cs`: the throw is at lines 38–41, not 26 (b8d6126).
* `harness v1.7` line 52 says the E2 `v_no_regen` "derives from gear ratios": not supported by `GearboxData.cs`/`GearBoxDataAdapter.cs` at b8d6126 for an AMT.
* `src/data_fetch/dmi_weather_climatology.py` runs a network call on import.

## 19. Choices I made

1. **The prompt copy is condensed** (the original was not available as a file): `docs/research/inputs/kiro-prompt-consumption-engine-review-2026-11-13.md` keeps rules, scope, parts, deliverables, and says so in its header. Appendix 1 and 2 are stored in `consumption-review-2026-11/appendix/` and compared with the notebook in Gate 2.
2. **VECTO source:** `git clone` of `mohgsaad-art/VECTO` was refused by the sandbox git gateway ("repository not found"). I fetched the files I needed one by one with `gh api` at commit `b8d6126…` (listed under `/projects/sandbox/vecto-src`, outside the repo). Files not fetched: `PEVGearbox`-related loss code, `Gearbox*.cs`, `TransmissionLossMap.cs` (so Q1 row 5 is `[OPEN]` for line numbers).
3. **Aux values for the VECTO-row tests** are read from the `.vmod` columns (ES, PS, AC constants; SP = mean over moving rows; Cond = maximum).
4. **Per-row efficiencies are signed** (negative where the motor or gearbox still needs power while the wheel regenerates). Without this the C2 test would blame the logic for a loss-map effect.
5. **`P_regen_max` in the proposal is mechanical power at the motor shaft** (VECTO limits torque at the motor), not electric power.
6. **Cond default in the test bench is the motor-on rule**; the Appendix 1 rule is a switch.
7. **MunicipalUtility Part C:** `BLOCKED` (no group-2 Municipal `.vmod`); Gate 3 and the refuse PTO test use HDEV's own driver rows and the Urban aux values `[ASSUMPTION]`.
8. Part H is `BLOCKED` rather than invented; Part G did not read PHEM, Autonomie or GEM.
9. Python venv with numpy 2.4.6, scipy, pandas, matplotlib, pytest at `/projects/sandbox/venv` (outside the repo; the sandbox home is read-only).
10. Part J: one run, described in the README, not executed.

## 20. `NO SOURCE`, `BLOCKED`, Bob to fetch

**`NO SOURCE`:** separate `inverter_eff`; one-number `P_regen_max`; `PTO_always_on` value; weather snapshot TTL; Cond rule for a body with its own motor (assumption); `p_air`/`R_air` (ISO 2533 cited from memory, not opened); a drive-PTO power for the sensitivity line.
**`BLOCKED`:** Part C for MunicipalUtility (no `.vmod`); Part H like-for-like (vehicle set-ups missing); Part G PHEM/Autonomie/GEM (not read); mechanical drive PTO while coasting (Part J run); the EU standard-value loss maps (Annex Xb) were not read in this job.
**Bob to fetch:**
1. Consolidated Regulation (EU) 2017/2400 of 01.01.2026, [eur-lex.europa.eu/eli/reg/2017/2400/2026-01-01/eng/xhtml](https://eur-lex.europa.eu/eli/reg/2017/2400/2026-01-01/eng/xhtml): Annex Xb standard values for electric machines, gearbox and axle (needed for loss maps); plus Regulation (EU) 2025/258 amendments ([eur-lex.europa.eu/eli/reg/2025/258/oj/eng/pdf](https://eur-lex.europa.eu/eli/reg/2025/258/oj/eng/pdf)). Too large for the 10 MB fetch limit here.
2. VECTO release notes after 5.1.6-RC (none found by search).
3. ICCT 2023/2024 real-world heavy-duty BEV report; Öko-Institut ELV-LIVE final report (repo link in `step4_real_trucks.csv`); NREL Fleet DNA: measured regen share and consumption **with** vehicle mass and route.
4. Vandijck eActros 600 test: truck mass, route, temperatures; Electrek 27 Jun 2026 article source data.
5. VTT electric refuse truck report: truck mass, battery, collection cycle, PTO energy ([vttresearch.com](https://www.vttresearch.com/en/project_news/refuse-truck-future-hums-along-quietly-without-emissions)).
6. TU Berlin waste-collection paper (Taube/Biedenbach et al., [trid.trb.org/View/1852414](https://trid.trb.org/View/1852414)): the per-route data behind 1.85 kWh/km.
7. DMI open data API: whether hourly `stationValue` exists for `mean_temp` / `mean_wind_speed` (`timeResolution="hour"`).
8. PHEM, Autonomie, EPA GEM documentation pages on BEV power chain and regeneration.

*Content from web pages above was rephrased for compliance with licensing restrictions; numbers marked `[SOURCE, snippet]` come from search snippets only and are not used as model inputs.*

## 21. How to run everything

```
python -m venv venv && venv/bin/pip install numpy scipy pandas matplotlib pytest
export VECTO_SRC=/path/to/VECTO_files     # needs Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2 at commit b8d6126
bash docs/research/consumption-review-2026-11/run_all.sh          # gates 2-3, parts A, C, D, F, K  (K takes ~1.5 min)
bash docs/research/consumption-review-2026-11/check_determinism.sh   # runs the CSV scripts twice and compares byte for byte
python -m pytest tests/consumption -q                              # Part B + proposal tests (39)
```
Gate 1: `cd docs/research/drag-default-test-2026-11 && VECTO_SRC=... python run_steps.py` (needs `scipy`).
