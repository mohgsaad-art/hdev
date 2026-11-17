# Kiro task: EEA truck validation v2 — fix the PR #27 harness and re-run Job 3 (7 Nov 2026)

Write for Bob in plain English, short sentences. Bob is the only person named.
Repo: `mohgsaad-art/hdev`. Work on the **same branch** `eea-truck-validation-2026-11` (PR #27). New commits only. **Do not change `src/`. Do not edit the notebook.**
VECTO source: `mohgsaad-art/VECTO` (EUPL 1.2). Folder: `docs/research/eea-truck-validation-2026-11/`.

Read first: the v1 prompt `docs/research/inputs/kiro-prompt-eea-truck-validation-2026-11-07.md`. All its rules still apply (sections 2, 7, 8). This prompt adds to it and overrides it where they differ.

## 0. Why this re-run

Claude reviewed PR #27 at commit `49ac911`. Job 1 looks usable. Job 3 results are **not usable**. The harness breaks the v1 rules in at least 12 places (listed in section 3 with file and line). The −14 % median "V-C best" result may come from these bugs, not from the drivetrain methods.

So:
- Keep Job 1 outputs. Make only the one fix in section 1.
- Close the Job 2 gaps in section 2.
- Rebuild the Job 3 harness to the rules in section 3. Pass the gate in section 4 **before** running any certified truck.
- Re-run Job 3. Redo Job 4 to the v1 standard (section 6).

## 0.1 How you must work (process rules)

These are not optional. PR #27 broke them.

1. **No invented numbers.** You may not type a number into code unless it is (a) read from a file at run time, or (b) on a line with a comment giving its source: file + line, regulation annex + point, or URL + quote. "Representative", "approx", "flagged" and "[ASSUMP]" are **not** sources. If you have no source: skip the run and list it, or stop and write `[BOB]`.
2. **Never fall back silently.** No `except: pass` that leaves a default. No nearest-neighbour fill outside a map. No default tyre radius. Every fallback must raise, or write a flag column AND be counted in the report.
3. **Use the code of record.** Call the notebook functions in `hdev_test_module.py` as they are. Do not re-implement them. If a function can't do what you need, say so in the report. Don't write your own version.
4. **Reuse the 3 Nov code.** `docs/research/drivetrain-inputs-fallbacks-2026-11/` (`_stdval.py`, `_harness.py`) and `docs/research/drag-default-test-2026-11/` (`_chain.py`, `_driver_dragtable.py`, `_e2_drag.py`, `run_steps.py`). Import or parameterise them. Don't write new loss or drag formulas.
5. **Caches must be exact.** A cache key holds every input that changes the output. No rounding of mass, no power "buckets", no "has drag yes/no" keys.
6. **Determinism check.** Run the full harness twice. `diff` the two `hdev_vs_certified.csv` files. They must be byte-identical. Paste the diff command and its output into the report.
7. **Long runs.** Always `timeout <s> python -u script.py 2>&1 | tee run.log`. Print progress every 25 runs with elapsed time. If a run would take over 10 min, profile first and say what you found.
8. **"Done" needs evidence.** For each item in section 7, paste the command you ran and its output (or the file + line) into `report.md`. Don't write "✓" without evidence.
9. If you find a problem in Bob's notebook code, **don't fix it**. List it in the report under "For Bob: notebook issues" with the line and a short reason.

## 1. Job 1: one fix

`truck_missions.csv` has `Mode` values like `;Total` (an empty string joined with `Total` when collapsing). Fix the join of `Mode`/`ResultType` values: drop empty strings, keep a sorted unique list. Re-run `build_test_set.py`. Show that the vehicle, config and mission counts did not change.

## 2. Job 2: close these gaps in `certified_numbers_meaning.md`

Answer each from VECTO source (file + line) or regulation (annex + point). If you can't, write "not found" and what you searched.

**2.1 kWh/km basis: the ratio doesn't fit "1/η".**
v1 says certified kWh/km = SoC energy ÷ charging efficiency η, and the range uses SoC energy. Then `kWh/km × range / usable` should equal 1/η. Since η ≤ 1, the ratio should never be below 1. But the data runs from **0.992** to 1.017.
- Compute the ratio per row for all in-scope truck mission rows. Give the count below 1.000, with min, P10, median, P90 and max.
- Find out why it can be below 1. Check: rounding of the published fields; whether `ActualChargeDepletingRange` and kWh/km use different payload weighting or a different energy term (SoC vs SoC_corr, the pneumatic correction `deltaEPSel`); whether usable kWh in the range formula is the same field as `bat_usable_sim_kwh`. Quote `DoCalculateElectricRangesPEV` line by line (DeclarationData.cs) with each D-term.
- State plainly which energy each field is: battery terminal, REESS internal (incl. internal resistance losses), or grid (incl. charging losses).

**2.2 What HDEV must add to reach the certified basis.**
HDEV `consumption_engine` returns energy at the battery terminals. It has **no battery internal-loss model**. Certified kWh/km (per 2.1) includes REESS internal losses and charging losses. Bob's 3 Nov E2 work found `EC_el_final` is +1.1–1.6 % above terminal energy on the VECTO E2 example. Say:
- the VECTO code path that gives REESS internal loss (file + line), and the inputs it needs (internal resistance curve, etc.);
- whether EEA gives any of those inputs (it does not give resistance; confirm);
- how `CalculateChargingEfficiencyPEV` computes η (file + line) and whether EEA gives its inputs.
Then define the comparison in section 3, R11.

**2.3 Usable capacity: fix the arithmetic, then confirm the formula.**
v1 wrote effective MaxSOC = 0.92625. Using v1's own formula: MaxSOC = 0.95·(1 − 0.025) + 0.05·0.025 = 0.92625 + 0.00125 = **0.9275**. Window = 0.9275 − 0.0725 = **0.855**, not 0.85375.
- Open `BatteryDataAdapter.cs` and `GenericSOC.csv`. Quote the exact lines. Confirm or correct the formula.
- Note that this is a **SoC** window. Usable **kWh** is the energy integrated over the OCV curve (`BatteryData.cs`, `CalculateBatteryEnergy`). Say whether the two are equal only for a flat OCV curve, and whether the data median 0.8551 fits better with the SoC window or with an energy ratio.

**2.4 CdxA bins (v1 point 5): look harder.**
v1 fetched only Annex I **Part A** of Reg. 2018/956. Do this:
- Fetch the latest consolidated text of Reg. 2018/956 (EUR-Lex, CELEX 02018R0956, newest consolidation date). Read **all** of Annex I, incl. Part C, and every amending act listed on the consolidation page. Search for "CdxA", "air drag", "range" and a table of intervals.
- Bob already checked these, and they do **not** hold the edges: `docs/research/HDV-tabledefinition (1).xlsx` (only `AirDrag_CdxA_range | nvarchar(20)`), and `docs/research/metadata-22fd286c-9737-4b38-b2bb-1f7a7d3e9916.pdf` (licence CC-BY 4.0, no bins). Don't repeat these.
- Also check the EEA dataset page for the 2024–25 HDV release, and its READ_ME, for a bin table.
- If found: give the edges in m² with URL + quote.
- If not found: write "not found", list every URL you opened, and mark `[BOB]`. Section 3, R10 says what to run then.

**2.5 Auxiliaries per technology label (v1 point 6 was only partly done).**
v1 found the tables but the harness used one flat number per mission (`run_hdev.py` lines 74–78: 2600 / 2300 / 2100 W, no arithmetic). Do this:
- List every distinct value of `Aux_Pneumatic_Technology`, the steering-pump technology (from `steering_xev.csv`), `Aux_HVAC_SystemConfiguration` (and the heat-pump and heater columns 35–41 in `vehicles_xev.csv`), and the electric-system technology, across the 4,603 in-scope trucks. Give counts.
- For each label × mission × HDV group present in the sample, give the **electric** power in W for a PEV, from `ES-Tech.csv`, `PS-Table.csv`, `SP-Table.csv` + `SP-Axles.csv` + `SP-Tech.csv`, `HVAC-Table.csv`, `Cond-Table.csv`. Show the row and the arithmetic: alternator efficiency for ES; `HVACElectricEfficiencyFactor` for HVAC; the electric pump factor for SP; `PneumaticSystemElectricDemandPerAirGenerated` for electric pneumatics. Each constant needs file + line.
- If a label has no matching row, say so and skip runs for those trucks.
- Say which aux terms VECTO applies only while driving and which apply always (`HeavyLorryAuxiliaryDataAdapter.cs`, file + line). Map them to `consumption_engine`'s arguments `ES, PS, HVAC, SP, cond`. Note that `consumption_engine` applies `SP` only when moving and `cond` only when moving or PTO active. If VECTO differs, list it under "For Bob".

**2.6 Municipal Utility and PTO (new point 8).**
In v1, Municipal is −64 to −73 %. The same thing happened in the 3 Nov PR: Municipal results were missing PTO power.
- In VECTO declaration mode for a **PEV lorry** on Municipal Utility: is PTO energy simulated? Which files (`MunicipalUtility_PTO_generic.vpto*` etc.)? What triggers it (the PTO flag `Transmission_PowerTakeOff`, an ePTO declaration, or something else)? File + line.
- Give the PTO power profile and how it's placed in the cycle.
- Count how many in-scope trucks have each PTO flag value.
- If PTO is in the certified Municipal figure, Job 3 must include it (R12).

**2.7 Mission set-up per group (needed for R9 and R10).**
For each HDV group × mission in the sample, read from `SegmentTable.csv` / `TruckSegments.cs` (and the body/trailer weight CSV it uses):
- body and trailer type, body curb mass, trailer curb mass;
- `AxleWeightDistribution` (truck axles) and `TrailerAxleWeightShare` (trailer axles), number of trailer axles and wheels;
- trailer tyre RRC and test load (`DeclarationData.Trailer`, file + line);
- `DefaultCDxA`, trailer `DeltaCdA`, `CrossWindCorrectionParameters` (the parameter set name per mission), vehicle height;
- which axle is driven for each axle configuration.
Put this in a table `mission_setup.csv` with a source column per value.

## 3. Job 3: required harness changes

Each R-item names the v1 bug (file + line at commit `49ac911`) and what to do. Write a section in `report.md` for each R-item: what changed, and evidence.

**R1. V-A must call the notebook `consumption_engine`.**
v1 `_drivetrains.py` lines 199–205 re-implement it. Instead, call `H.consumption_engine(...)` for every run, for every variant. It returns `P_wheel, P_trac, P_aux_row, P_battery, E_battery`.
- V-A = `E_battery` as returned.
- V-B/C/D = take the returned `P_wheel` and `P_aux_row`. Compute `P_trac` with the variant's drivetrain from `P_wheel`. Then `P_battery = P_trac_variant + P_aux_row`. This is the v1 prompt rule.
- Arguments, each stated in the report with its source:
  - `m_vehicle = TotalVehicleMass`; `payload_wp` = zeros (`TotalVehicleMass` already includes body, trailer and payload; v1 Job 2 point 4).
  - `beta` = `Physics.RollResistanceExponent` (file + line).
  - Air density: `consumption_engine` computes ρ = p_air / (R_air · (T_amb + 273.15)). Find VECTO's declaration air density (`Physics.cs`, file + line). Choose `p_air`, `R_air`, `T_amb_h` so ρ equals it. Show the arithmetic. Don't change the function.
  - `W1, W2, cdxa_v` from `crosswind_engine`. Use the parameter set that VECTO uses for that group × mission (from 2.7), not a hand map (see R10).
  - `ES, PS, HVAC, SP, cond` per truck from 2.5.
  - PTO arguments per R12. Zero PTO only where 2.6 shows VECTO has none.
  - `motor_eff, inverter_eff, gearbox_eff, regen_effeiciency`: the notebook has no call cell with values. Use 0.95 / 0.95 / 0.98 / 0.95 and say they come from the 3 Nov matrix (`claude/results-drag-and-drivetrain-matrix-360km-2026-11-03.md` / `drivetrain-inputs-fallbacks-2026-11/`, give the file + line). `v_no_regen` from the same place.

**R2. Rotating inertia is missing.**
v1 `run_hdev.py` line 237 passes `m_red_wheels=0.0`. Line 294 passes `theta_red = 0.0` to `force_engine`. So the wheel and motor inertia are ignored. This makes urban and regional runs read low.
- Compute the reduced wheel mass the way VECTO does (`VehicleData.cs`, `ComputeRollResistanceAndReducedMassWheels`, file + line). Use `Wheels.csv` inertia per tyre dimension × number of wheels (twin tyres from `axle_xev.csv`), incl. trailer wheels from 2.7.
- Motor and gearbox inertia: EEA has none. Say so. If VECTO uses a standard value for standard-value motors, use it with file + line. Otherwise leave it out and list it as a known gap.
- Pass the result consistently to `driver_model` (`m_red_wheels`) and to `force_engine` (`theta_red`). Read both function signatures. Show that the units match what each function expects.

**R3. Tyres and RRC: do what VECTO does.**
v1 `run_hdev.py` lines 156–182: plain mean of axle RRC, fallback 0.0055, r_dyn from the **last** axle, default 0.489 m. All three break v1 rules.
- Total RRC per VECTO (`VehicleData.cs` lines ~271–313): for each axle, share × RRC × (share · m · g / test load / wheels)^(β−1). Sum over truck axles + trailer axles (2.7). Use `TotalVehicleMass` for m.
- `axle_xev.csv` has no test-load column. Find where VECTO gets `TyreTestLoad` in declaration mode (file + line). If it's from `Wheels.csv` or a standard, use it. Otherwise `[BOB]`.
- The notebook applies load dependence as `m_row ** beta * k_roll`, with `k_roll = Crr · g · cos(grade) · v_avg`. So pass `Crr_eff = F_roll_VECTO / (m^β · g)`, so the notebook force equals VECTO's at that mass. Show the arithmetic for one run.
- r_dyn from the **driven** axle (2.7). `axle_xev.csv` has `AxleNumber` but no axle type. Say how you identify the driven axle (axle configuration + VECTO rule, file + line).
- Any vehicle with missing RRC, `CertificationNumber` N/A, or a tyre dimension not in `Wheels.csv`: **skip and list**. No defaults.

**R4. Driver: drag table, cache key, power limit.**
- v1 `build_drag` (`run_hdev.py` lines 335–344) is invented (`52.5 + 15·(ratio/3)`, `+ 2.0·v`). Delete it. Build the drag table per variant with the 3 Nov builders: V-A zero drag (as the 3 Nov matrix did; cite it); V-B the EU standard drag table (`_stdval.py` / `_e2_drag.py` method), parameterised with the truck's own ratios; V-C built the same way from the V-C components; V-D the E2 drag table as is.
- **Each variant gets its own driver run**, because the drag table changes coasting.
- The driver cache key (v1 line 229) drops the drag table and CdxA and rounds the mass to 250 kg. It also uses the first truck's CdxA for coasting. The key must include mission, exact mass, Crr_eff, r_dyn, reduced mass, a hash of the drag table, and the CdxA table used.
- Run the driver at **each** CdxA corner (coasting depends on CdxA).
- Power limit: v1 runs the driver with no `P_max`. That's why 83 % of runs demand more wheel power than the motor's rated power. Pass `P_max`. Use the EEA rated power field (`em_rated_kw_total` or the IEPC rated kW). Say which Annex Xb definition it is (rated, continuous, or peak; v1 rule 8). Also report a second run with `em_max_cont_kw` / `iepc_max_cont_kw` (max continuous, from voltagelevel). Report how far the trace deviates from the cycle: time difference and share of rows below target speed.
- **For Bob:** in the notebook `driver_model`, `P_max` is only applied when `coast_on` is true (`hdev_test_module.py` ~line 309: `if P_max is not None and coast_on:`). Check whether coasting is on in your runs. If it's off, the cap does nothing. Report it. Don't change the code.

**R5. Drivetrain chains: the loss models are not used.**
v1 `_drivetrains.py` defines `std_gearbox` (line 88) and `vecto_axle` (line 98) but **never calls them**. `run_hdev.py` line 407 calls `_map_chain(..., axle=None, gears=None, adc_eff=0.96)`. So V-B and V-C are "motor map + a constant 0.96". That isn't the method the v1 prompt asked for.
- **V-B:** wheel → axle with the Annex VI / Annex VII standard loss (`_stdval.py`; cite the annex point) → gearbox with Annex VI App. 8 standard loss if a gearbox exists → motor standard map (Annex Xb App. 8). Same structure as the 3 Nov `_chain.py`.
- **V-C:** wheel → VECTO generic axle (`GenericTransmissionComponentData.cs`) → ADC 0.98/0.96 (`GenericBusElectricMotorData.cs` 42–49) → de-normalised PSM/ASM map. For IEPC: `GenericBusIEPCData.cs` and the IEPC normalised maps (`EfficiencyMap_IEPC_*_normalized.vmap`), with its gear efficiency and differential handling. Cite the lines. Say what you used and why.
- **V-D:** as v1, plus the E2 gearbox shift logic. v1 fixes gear 2 (`gear_fixed=2`). Say what VECTO's shift strategy would do, or run both gears and report both. Mark trucks above 250 kW as physically unsuitable, as v1 did.

**R6. Gear ratios that EEA doesn't have.**
EEA gives `Transmission_NrOfGears` and `Axlegear_Ratio`, but **no gear ratios** and no ADC ratio. v1 uses `total_ratio = axle_ratio` for E2/E3 (`_drivetrains.py` line 182). That ignores the gearbox and puts the motor at the wrong speed.
- Count sampled configs by architecture × `Transmission_NrOfGears`.
- Single-speed (gears = 1 or 0 with E3 single ratio): check whether `em_desc` or `hdv_2024_electricmachine.csv` gives an ADC ratio. If it does, use it with the column name. If it doesn't, say so.
- Multi-speed E2 with no ratios: **skip V-B and V-C and list them**. No made-up ratios. v1 rule.
- IEPC: use the IEPC ratio from `hdv_2024_iepc.csv`. For multi-gear IEPC, state which ratio the column holds (lowest total ratio per v1 findings). If the other gears are unknown, skip the run and list it.

**R7. Rated point: no 3000 rpm.**
v1 `_drivetrains.py` lines 187–195 assume `n_rated = 3000 rpm` for every motor. That's invented.
- Find what Annex Xb standard values need as declared inputs (rated speed? max speed? full-load curve?). Give annex + point.
- Find what `GenericBusElectricMotorData.cs` needs for the rated point (`GenericRatedPointHelper`, file + line). v1 found it uses the **full-load curve**, which EEA doesn't have.
- If EEA can't supply it: the main result for V-B and V-C is **"cannot run from EEA data"**. That's a valid finding. Say it plainly.
- Optional, clearly labelled **sensitivity only** (not a result): for configs where the OEM's own datasheet gives the motor's rated or base speed, run V-B/V-C with that value. Give URL + quote. Report it in a separate table.

**R8. Map edges: no silent clamping.**
v1 `_EMap.__call__` (`_drivetrains.py` lines 79–84) and `_Loss.input_side` (lines 64–70) fill every point outside the map with the nearest map value. When demand exceeds the map's torque, this caps the electric power → kWh/km reads low.
- Remove the nearest fill. For each run and variant, count the rows outside the motor map (torque or speed) and their share of positive wheel energy.
- Report both. Mark a run "out of map" if that share is above a threshold. **Propose** a threshold in the report and mark it `[proposal, Bob to decide]`. Don't silently choose.
- Out-of-map rows can't give an energy. Give the run's kWh/km only if no rows are out of map. Otherwise list it.

**R9. Aux per truck.** Replace `AUX_W` (lines 74–78) with the per-truck values from 2.5, passed into `consumption_engine`.

**R10. CdxA and crosswind.**
- v1 maps groups 5, 10 and 12 to `RigidTrailer` (`run_hdev.py` lines 63–68). Per Reg. 2017/2400 Annex I Table 1, groups 5, 10 and 12 are **tractors** (check and cite the table). `TractorSemitrailer` is defined (line 58) but never used. Read the crosswind parameter set per group × mission from 2.7. Don't hand-map.
- v1 `GROUP_CDXA` (lines 48–53) is hand-typed. Read `SegmentTable.csv` at run time. Add the trailer/body `DeltaCdA` per mission (`AirdragDataAdapter.cs`) to the vehicle CdxA. v1 does not add it.
- Vehicle height: from `SegmentTable.csv` per group (cite).
- Corners:
  - If 2.4 finds the bin edges: run the bin's low and high edge (+ DeltaCdA). Report both.
  - If not: **do not use ±10 %** (unsourced). Run one case with VECTO `DefaultCDxA` + DeltaCdA. Call it "VECTO standard-value CdxA" in every column name and graph. Note that certified trucks with a measured CdxA are likely below the default [INFERENCE], so this run is likely biased high on aero. Mark the bin edges `[BOB]`.

**R11. Same basis as the certified figure.**
v1 divides by a constant 0.995 (`run_hdev.py` line 482). After 2.1 and 2.2, do this:
- Always report HDEV battery-terminal kWh/km.
- Report the certified figure as published.
- If 2.1/2.2 give a sourced way to convert one to the other per vehicle, apply it and show it. If not, report the % difference on the terminal basis and state the known size of the missing terms (charging loss from 2.1; REESS internal loss from 2.2 and the 3 Nov E2 result) as a separate column. Don't fold an unsourced constant into the error.

**R12. Municipal and PTO.** Per 2.6. If the certified figure includes PTO, pass the VECTO PTO profile through `consumption_engine`'s PTO arguments. Read its PTO code first: it needs standstill rows at each PTO stop. If the cycle/driver output can't place it, say so and **exclude Municipal from the summary statistics** (report it separately with the reason).

**R13. Remove "follow_limit_flag" as written.** v1 `follow_limit_flag` (lines 350–364) compares wheel power with rated motor power. After R4 (P_max in the driver) and R8 (map edges), report instead: (a) cycle deviation from R4 and (b) out-of-map share from R8. Those are the "cannot follow" flags the v1 prompt asked for.

## 4. Gate: reproduce the 3 Nov result first

Before any certified truck:
1. Run the new harness on the **VECTO GenericVehicleE2 example** with its own component maps, the E2 drag table and its own mass, on the same cycles as the 3 Nov matrix.
2. Compare with the 3 Nov results (`claude/results-drag-and-drivetrain-matrix-360km-2026-11-03.md`; repo copy under `docs/research/drag-default-test-2026-11/step3_kwh_per_km.csv`). The 3 Nov finding: own maps + VECTO E2 drag within 1 % of VECTO.
3. If the new harness is not within 1 % of the 3 Nov "own maps" result on every cycle: **stop**. Write what differs and why. Don't run certified trucks.
4. Then run V-A, V-B, V-C, V-D on the E2 example. They must match the 3 Nov numbers for those options (state the tolerance you used and why). Same stop rule.

This proves the harness before it's used on real trucks.

## 5. Error attribution (new)

After the main run, take **6 runs**: one per architecture (E2, E3, E-IEPC, E-IEPC wheel) on Regional Delivery, plus the two worst-error runs. For each, change **one input at a time** from the v1 setting to the v2 setting and record kWh/km after each step: aux, rotating inertia, RRC, crosswind set, DeltaCdA, drag table, drivetrain losses, power cap. Output `error_attribution.csv` and one bar chart per run. This shows which fix moved the error and by how much.

## 6. Job 4: bring up to the v1 standard

v1 has 10 entries. The v1 prompt asked for 15–25 configs.
1. Re-check every v1 entry. The URL must be the **OEM's own** page or spec sheet. Record the page title, the access date, and a quote of ≤ 15 words for each value. Trade press, search snippets and dealer pages are leads only: if a value came from one (e.g. eActros 600 "~103 kWh/100 km testing tour", Volvo "1.1 kWh/km road test"), find the OEM page or remove it.
2. Add entries to reach at least 15 configs, covering every make with complete configs.
3. Matching rule from v1 (battery size **and** motor/architecture must agree). Record "no match" with the reason.
4. Keep v1's interpretation rules. Don't call any column "the truth".

## 7. Deliverables (update in place, same folder)

1. `truck_missions.csv` (section 1 fix).
2. `certified_numbers_meaning.md` (2.1–2.7 added).
3. `mission_setup.csv` (2.7), `aux_per_label.csv` (2.5).
4. `run_hdev.py`, `_drivetrains.py` rebuilt (section 3). Import the 3 Nov modules; don't copy-paste new formulas.
5. `gate_e2.csv` + gate section in the report (section 4).
6. `hdev_vs_certified.csv` with these columns added: `skip_reason`, `out_of_map_share`, `cycle_dev_s`, `cdxa_used`, `crr_eff`, `m_red`, `aux_ES/PS/HVAC/SP/cond`, `pto_W_avg`.
7. `skipped_runs.csv`: every skipped config × mission × payload × variant, with the reason.
8. `error_attribution.csv` + charts (section 5).
9. Graphs 1–5 as in v1, rebuilt. Graph titles must name the CdxA basis (bin edges or VECTO standard-value CdxA).
10. `three_way.csv` (section 6).
11. `report.md`, rewritten. Top (max 15 lines): same 5 questions as v1, plus "Did the gate pass?" and "Which v1 conclusions changed?". Then: one section per R-item with evidence; "For Bob: notebook issues"; `[BOB]` list.
12. Commit to PR #27. Update the PR description with a v1 → v2 change list.

## 8. Done when

- Gate (section 4) passed, with the numbers shown. Or stopped at the gate with the reason. Stopping at the gate is an acceptable result.
- Every number in `run_hdev.py` and `_drivetrains.py` is read from a file at run time or has a source comment. Paste `grep -nE "[0-9]+\.[0-9]+" run_hdev.py _drivetrains.py` output into the report with the source for each hit.
- No nearest-neighbour fills and no silent defaults remain. Paste a `grep` for `NearestND`, `except`, `0.0055`, `0.489`, `3000`, `0.995`, `AUX_W`, `build_drag` with output.
- Two full runs give byte-identical output (`diff` shown).
- Every skipped run is in `skipped_runs.csv`.
- 2.1–2.7 each have a sourced answer or "not found" with what was searched.
- Every OEM value has OEM URL, date, quote and tag.
