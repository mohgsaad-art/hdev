# Kiro prompt: `consumption_engine` full review, plus how to structure the parser, defaults, data fetch and run layer (13 Nov 2026)

Owner: Bob. Repo: `mohgsaad-art/hdev`. **Today's date is 13 November 2026.** When you research, look for documents up to this date (VECTO releases, regulation amendments, standards, papers, open-source code from 2023–2026), not only older ones.

**Run the whole job in one uninterrupted pass.** Do not stop to ask Bob anything. If something is unclear, choose the option that changes the least, write it under "Choices I made", and carry on. Open **one PR** at the end.

**Branch:** create `consumption-review-2026-11` from `main`. Copy this prompt to `docs/research/inputs/kiro-prompt-consumption-engine-review-2026-11-13.md` as the first commit. Put everything new in `docs/research/consumption-review-2026-11/`, `tests/consumption/` and `docs/explainers/consumption-explained.md`. Open the PR from this branch to `main`.

---

## 0. Rules for this job (read first)

1. **Do not edit Bob's engine code.** Bob writes all engine code himself. Do not change the notebook or anything under `src/`. You may copy functions into `docs/research/consumption-review-2026-11/reference_copy.py` and make experimental variants there, clearly named (e.g. `consumption_engine_v_split_eff`, `consumption_engine_v_step6_searchsorted`). Every proposed change goes into the report as a **before / after snippet with its measured effect**.
2. **No invented numbers.** Every value you use or propose must come from a named source: VECTO source/resource file + line, Regulation (EU) 2017/2400 (incl. amendments up to 2025), an ISO/EN/SAE/UN/JRC/NREL/EPA document, or a peer-reviewed paper or official report, with a link. If there is no source, write `NO SOURCE` and leave it open. Illustrative test values are allowed only inside tests and must be labelled `ILLUSTRATIVE` in the test and the report.
3. **No silent fallbacks.** If an input is missing, do not fill it with a guess. Mark the part `BLOCKED: <what is missing>` and keep going.
4. **Tag every statement in the report:** `[VECTO]` (file, lines, branch, commit), `[REG]` (annex/point), `[STD]` (number, year, clause, full text or summary), `[SOURCE]` (link, date, full text or abstract/snippet), `[CALC]` (show inputs), `[TEST]` (test file + function), `[ASSUMPTION]`, `[SIMPLIFICATION]`, `[OPEN]`. Never pass an assumption or inference off as fact. A number seen only in a search snippet is `[SOURCE, snippet]` and must not be used as a model input.
5. **VECTO version.** Bob's `.vmod` files were written by **VECTO 5.1.6-RC**. Read VECTO source in `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`. Clone with `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/VECTO`. Re-check every VECTO line number in this prompt; they are leads, not facts.
6. **VECTO cannot run in your sandbox.** Anything needing a new VECTO run is Bob's job. Write the exact steps for him instead (Part J).
7. **Engine purity rule (Bob's architecture, decided).**
   - Engine functions are pure maths: every parameter is an argument, nothing hard-coded, no I/O, **everything in SI units inside, no unit conversion inside** (no km/h, no °C: temperatures are in **kelvin** inside the engine since 13 Nov).
   - **All calculations belong in the engine.** The parser only cleans, formats, selects inputs, looks up, converts units, fills gaps and **does all input checks** so the engine doesn't break (decided 12 Nov).
   - **All default values live in a separate defaults module (`defaults.py`)**, not in engine function signatures and not in the parser (decided 13 Nov).
   - Judge every proposed change against this rule and say for each one: **engine**, **parser**, **defaults** or **fetch layer**.
8. **Bob's validation rule.** Matching VECTO exactly is **not** validation. VECTO is the audit reference. Validation means comparison with several independent sources. A change that only swaps one assumption for another, with no standard or validation behind it, is not worth making. Say so when that is the case.
9. **Bob's modelling stance.** HDEV must not underestimate energy. Where the physics is uncertain, show which choice is the conservative one. Accuracy target: HDEV kWh/km within 5 % (decided 7 Nov).
10. **Inputs users can actually give.** No features that need inputs fleet users can't realistically give. For every input, say: can a fleet user give it? If not, what is the best **sourced** default?
11. **Speed matters.** `consumption_engine` runs for every vehicle × every operating date of a year (decided 12 Oct). Keep it vectorised (numpy over rows). Any loop over rows is a performance bug unless proven cheap (Part K).
12. **Plain English** in the report. Short sentences. Define every technical term the first time. Refer to the owner only as "Bob".
13. **Never decide an open design choice for Bob.** Show evidence; if you recommend, label it "Kiro's recommendation".

### 0.1 Pitfalls from earlier Kiro PRs (do not repeat them)
- Re-implementing Bob's function in the harness instead of calling it (PR for EEA validation v1, `_drivetrains.py` lines 199–205). **Always call the loaded notebook function.**
- A "gate" that compares hard-coded numbers instead of running the code.
- Results that change between runs. Run each main script twice; confirm identical CSVs.
- Claiming "done" without evidence. Every summary claim points to a CSV, test or file line.
- PDFs not opened and values left as `NOT FOUND`. Try every route to the full text; otherwise add to "Bob to fetch" with link/DOI and exactly which table/figure/value.
- Mixing up VECTO's sign conventions (VECTO often reports power as negative when it flows into the battery). State the sign convention of every VECTO column you use.

### 0.2 Scope

**In scope:**
1. `consumption_engine` in full: signature, steps 1–7, return values (Appendix 1).
2. The **contract** between `consumption_engine` and every function that feeds it: `driver_model`, `force_engine`, `payload_engine`, `crosswind_engine`, `P_aux`, `SP_power_helper`, `HVAC_thermal`, `pto_engine` (Appendix 2). Read-only: shapes, units, names, indexing. Do not review those functions' maths; they are final.
3. **Architecture question (Part L):** what is the professional, industry-standard way to structure the layers around the engine: data fetch (e.g. DMI weather, later prices), parser, `defaults.py`, project JSON, scenario changes, and the run layer (harness now, `main.py` / FastAPI later). Includes "where does live data come from" (Part L, Q-L4).

**Out of scope (later jobs):** the battery model (OCV + Ri loss, SOC), charging, the driver model's maths, the drivetrain loss maps themselves (motor/gearbox maps), PTO transmission drag (parked until Bob's VECTO run 2), cold-tyre / wet-road factors. If you notice something there, list it under "Seen in passing (out of scope)" with file and line only.

### 0.3 Decisions already made by Bob (do not reopen; you may report evidence against them)

Force / rotor inertia (12 Nov, Kiro PR #30):
1. `force_engine` returns `k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg`. Wheel power is `P_wheel = m·k_lin + m^β·k_roll + k_rot_wheel + ρ·CdxA_eff·L`.
2. **`k_rot_rotor` is NOT part of wheel power.** It is added at the motor side in step 5, after the gearbox efficiency, like VECTO (`ElectricMotor.cs` 186–188, 297, 615).
3. Unknown gear → lowest gear (highest ratio) as the safe default for `i_total` (parser).

PTO (12 Nov, Kiro PR #31; details in Appendix 2.6):
4. Stop PTO profile: from the first standing row of that stop + `pto_start`. Use `M == 0` for standing rows, not `V == 0` (PR #31: `V == 0` gives stop + 1 rows, +4 % on a 25 s stop).
5. Stop constant: on all standing rows of that stop. Drive profile: from the first moving row after the stop, keeps running past the next stop (VECTO). Drive constant (sweeper): on all moving rows until the next stop; one sweeping power per route (flagged deviation).
6. **Mechanical vs electric drive PTO:** one yes/no input "does the body have its own electric motor?". **No (mechanical):** drive-PTO W is added in **step 5 at the motor shaft**, before motor × inverter efficiency (same place as `k_rot_rotor`). **Yes (electric):** added in **step 6** straight to battery power. `drive_pto_eff` stays 1.0.
7. Always-on PTO stays in `P_aux` (`PTO_always_on / PTO_eff`); it may be a per-hour array later (fridge).
8. A new drive-PTO part while one still runs → error (VECTO throws, `PTODriveAuxiliary.cs:26`).
9. PTO transmission drag: parked.

Aux (decided earlier):
10. ES, PS, HVAC always on; SP on only when moving; Cond on while moving or stop-PTO active (HDEV rule; PR #31 recommended keeping it). No aux power during depot charging (13 Oct).
11. `P_aux` returns electric W per aux, already multiplied by its factor. HVAC from the thermal model enters with `HVAC_eff = 1.0`.
12. HVAC: scalar (VECTO table) or one value per weather hour (thermal model).

Weather / air (6 Oct, 13 Nov):
13. Air density per row from the hour's temperature, fixed pressure (`ρ = p/(R·T)`, T in kelvin). One `W1`, `W2` row per weather hour. Weather hour index `hour = (t_start + T) // 3600`, one continuous array across midnight.
14. Yaw angle clamped at 10° in `crosswind_engine` (6 Oct).

Units (12–13 Nov):
15. Everything in SI inside the engine; temperatures in kelvin. So in step 3: `+ 273.15` goes, and `* 3.6` goes (Kiro PR #30 recommended passing `cdxa_v` in m/s; numerical effect none).

Known bugs already found (fix proposals expected, re-test them):
16. Step 1 BUG-2 (PR #30): a row with `S` a hair before `wp_s[0]` gets `k_pl = −1` → the **last** payload. Proposed fix: `np.clip(..., 0, None)`.
17. Step 3 (PR #30): above 130 km/h HDEV holds the last CdxA value; VECTO throws (`CrosswindCorrectionCdxALookup.cs` 80–87). Flag only.
18. Step 6 (PR #31): cannot take the final `pto_engine` outputs; 0 s marker waypoint raises "no standing rows"; `is_on = 1` with only a drive profile gives `int(NaN)`; drive profile dropped silently; no slot for constants; `V == 0` off-by-one; per-stop `np.where` scan is O(rows × stops) (~120 s for a year in one array vs 0.6 s with `searchsorted`); `PTO_always_on` per hour is not hour-indexed.

Drivetrain (3–22 Nov):
19. Fixed efficiencies (motor 0.95, inverter 0.95, gearbox 0.98) are placeholders, flagged; loss maps from EU standard values come later (input question, not a blocker). The engine must be **ready** for maps later without a rewrite, but do not build maps in this job.

### 0.4 Inputs (in the repo or the VECTO fork)

| What | Path | Used in |
|---|---|---|
| **Code of record, 13 Nov** (Bob uploads before you start) | `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-13.ipynb` | everything |
| If the 13 Nov file is missing | use `HDEV_NEW_code_of_record_2026-11-12.ipynb` (on branches `force-engine-review-2026-11` / `aux-pto-review-2026-11`) **plus** Appendix 1–2 of this prompt, and say so in Gate 2 | |
| Force review (PR #30) | `docs/research/force-engine-review-2026-11.md` + folder, `tests/force_engine/` (branch `force-engine-review-2026-11`) | context, step 1–4 tests |
| Aux / PTO review (PR #31) | `docs/research/aux-pto-review-2026-11.md` + folder, incl. `reference_copy.py: consumption_step6_v_pto1nov` (branch `aux-pto-review-2026-11`) | step 6 |
| HVAC review (PR #32) | `docs/research/hvac-review-2026-11.md` (branch `hvac-review-2026-11`) | HVAC shape contract |
| Drag / drivetrain test (Chain S, maps) | `docs/research/drag-default-test-2026-11/`, `docs/research/drivetrain-inputs-fallbacks-2026-11/` | Gate 1, Part C |
| E2 `.vmod` runs + `.vsum` | `docs/research/vecto/` | Part C |
| Test harness v1.7 | `docs/research/vecto/hdev_test_harness_v1.7.py` | E2 set-up |
| Existing layer code (Kiro's earlier scaffolding) | `src/resolver/` (`defaults.py`, `resolve_typed.py`, `waypoint_parser.py`, `calendar.py`, `session_handover.py`), `src/registry/` (slot, fields, levers), `src/data_fetch/` (`dmi_weather_climatology.py`, DRAFT), `src/engine/consumption.py`, `src/validate/`, `src/server/` | Part L |
| Kiro specs | `.kiro/specs/` | Part L |
| VECTO powertrain source | `VectoCore/VectoCore/Models/SimulationComponent/Impl/`: `ElectricMotor.cs`, `BatteryElectricMotorController.cs`, `PEVGearbox*.cs` / `Gearbox*.cs`, `AxleGear.cs`, `Wheels.cs`, `Brakes.cs`, `PEVPTO.cs`, `ElectricSystem.cs`, `Battery*.cs`, `DCDCConverter*.cs`, `ElectricAuxiliaries.cs`, `Conditioning.cs`; `Models/Declaration/DeclarationData.cs`; `Configuration/Constants.cs`; `OutputData/ModalDataContainer.cs` and `ModalResultField.cs` (`.vmod` column definitions) | Parts A, C |
| Open-source tools (Bob's forks) | `mohgsaad-art/fastsim`, `mohgsaad-art/blast-lite`, `mohgsaad-art/eflips-depot`, `mohgsaad-art/spice_ev`, `mohgsaad-art/dt-cargo`, `mohgsaad-art/acnportal` | Parts H, L |

**How to load the notebook functions (do exactly this):** write `docs/research/consumption-review-2026-11/_load_notebook.py`. It reads the `.ipynb` JSON, takes the **code cells only**, skips cell 0 (it imports `torch`, `gymnasium`, `requests` etc., which must NOT be installed) and any cell that only runs examples or plots, and `exec`s the function cells in one namespace that starts with `import math, bisect; import numpy as np`. Do not change any cell text. Print the list of function names loaded. All tests and scripts import from this loader.

---

## 1. What `consumption_engine` does (context)

HDEV is a Python engine that sizes battery-electric trucks and depots, built to be auditable against VECTO (the EU CO₂ certification simulator, Regulation (EU) 2017/2400). The pipeline is:

`crosswind_engine` → `payload_engine` (on waypoints) → `driver_model` (1 s rows, run once per route at a reference mass) → `force_engine` (mass-free coefficients per row) → **`consumption_engine`** → battery (later) → charging.

`consumption_engine` takes the 1 s rows and turns them into battery power. Most of it is **putting finished pieces together** (mass per row, weather per row, aux per row, PTO per row). Step 5 is where the real powertrain logic sits (where each loss applies, which way the power flows, when regeneration is allowed). Steps:

1. Mass per row: vehicle mass + payload, carried forward by distance from the waypoints where `payload_engine` wrote it.
2. Weather hour of each row.
3. Air density and `CdxA_eff` per row (from the hour's temperature and the hour's crosswind table, interpolated by speed).
4. Wheel power per row.
5. Wheel power → electric traction power (drivetrain efficiencies, regen rules, regen cap).
6. Aux power per row (ES, PS, HVAC, SP, Cond, always-on PTO, stop PTO).
7. Battery terminal power per row and net trip energy.

---

## 2. Gates (must pass before anything else)

**Gate 1, environment:** run `docs/research/drag-default-test-2026-11/run_steps.py` unchanged. Confirm Chain S, variant V1, reference load: RegionalDelivery **0.9749** and UrbanDelivery **0.8502** kWh/km (±0.0005). If it fails, stop everything except Parts A and L and report what differs.

**Gate 2, code of record:** load the notebook. Confirm `consumption_engine` is byte-identical to Appendix 1, and that `force_engine`, `pto_engine`, `P_aux`, `ssm_total_w`, `climate_lookup`, `HVAC_thermal` match Appendix 2. Report every difference. Where they differ, the **13 Nov notebook wins**; say which version you tested. Diff against `src/engine/consumption.py` and report how stale it is.

**Gate 3, the function runs at all with the final producers:** call the real `driver_model` → `force_engine` → `pto_engine` → `P_aux` → `consumption_engine` chain on E2 Regional, Urban and the VECTO MunicipalUtility (refuse) cycle. Expected today (from Appendix 1 vs Appendix 2): it will **fail** (names `k_rot` vs `k_rot_wheel, k_rot_rotor`; old PTO input names). Report exactly where. Then write the **minimal adapter** in `reference_copy.py` (`consumption_engine_v_signature_only`: rename only, no logic change) so the rest of the job can run, and confirm it reproduces the old function's numbers when `k_rot_rotor = 0` and PTO is off.

---

## 3. Questions to answer from the VECTO source (Part A)

Answer each with `[VECTO]` file + lines + commit, quote the exact C# lines, and give a verdict: **MATCH**, **DEVIATION (already flagged)**, **DEVIATION (new, flag it)** or **BUG**.

**Step 5 (drivetrain): the main part.**
- **Q1 Order of losses.** Write out VECTO's power chain for a PEV E2 (battery-electric, central motor + gearbox) from wheel to battery terminals, component by component (wheels → brakes → axle → (angle drive) → (retarder) → gearbox → PTO → motor → inverter/"electric system" → (DC/DC for aux) → battery), with the file/line where each component adds its loss or inertia. Which `.vmod` column belongs to each point?
- **Q2 Sign decision per component.** For each loss, does VECTO decide "driving or recovering" by the sign at **that** component (e.g. gearbox by gearbox torque, motor by motor torque), or once at the wheel? HDEV currently decides once, on `P_wheel`, and applies one combined efficiency. Show with `.vmod` rows where the two give different answers (e.g. a row with small negative wheel power but positive motor power because of `k_rot_rotor` or mechanical drive PTO).
- **Q3 Rotor inertia.** Exactly where VECTO adds rotor inertia torque, and whether it passes through the motor efficiency (it should, it is on the motor shaft). Confirm HDEV's plan (`k_rot_rotor` added after gearbox efficiency, before motor × inverter) and give its size per mission.
- **Q4 Regeneration rules.** VECTO's conditions for recuperation on a PEV: (a) below which speed there is no regen (`Constants.cs` ~323, 5 km/h?), and is it vehicle speed at step start, end, or average; (b) coasting (motor off, `BatteryElectricMotorController.cs` 44–46): confirm 0 traction power; (c) braking: how VECTO splits braking between motor and mechanical brakes (`Brakes.cs`, `BatteryElectricMotorController.cs` 62–69); (d) the regen limit: motor full-load/drag curve (generator side), battery max charge power/current, inverter limit. Which one usually binds for E2? What should `P_regen_max` stand for, and is a single W number a fair proxy?
- **Q5 HDEV's `regen_effeiciency`.** HDEV multiplies negative wheel power by one `regen_effeiciency`. What is the VECTO equivalent: gearbox × motor × inverter in generator mode? Is a separate number needed at all once the chain is split (Q1)? If HDEV keeps one number, what value matches VECTO's E2 maps on average (from `.vmod`, Part C) and is it the conservative side?
- **Q6 Motor on/off.** HDEV's `M` modes from the driver: 0 standing, 1 accelerating, 2 cruising, 3 coasting, 4 braking (verify in `driver_model`). For each mode, what does VECTO do with the motor (on, off, drag only, generator)? Is `M == 3 → P_trac = 0` right when the truck coasts **uphill** or with drive PTO running?
- **Q7 Aux path.** VECTO: do electric aux draw from the high-voltage battery directly, via a DC/DC with efficiency 1.0 (`DeclarationData.cs` ~124), or via the inverter? Confirm HDEV's `P_battery = P_trac + P_aux_row`.

**Step 6 (aux and PTO).**
- **Q8 Aux activity.** Confirm in source: ES, PS, HVAC always on; SP only when moving (ID "STP", `ElectricAuxiliaries.cs`); Cond when an EM is on or E-PTO is on (`Conditioning.cs` ~86). What exactly is "moving" for SP in VECTO (speed > 0 at start, end, average, or a halt tolerance `Constants.cs` 327)? Compare with HDEV's `V > 0` (start speed) and count the rows where they differ on Urban.
- **Q9 Cond with drive PTO.** HDEV rule: `cond × (moving | pto_active)`. For drive PTO (mechanical and electric), what does VECTO do with Cond? Give the rule HDEV should use for the drive-PTO case.
- **Q10 PTO placement.** Re-confirm `pto-knowledge` (Appendix 2.6): stop PTO centred in the stop, left-hold sampling, standing time = stop + PTO; drive PTO time-weighted average per step, applied only while the shaft turns.

**Step 7 (battery).**
- **Q11 What VECTO reports as "battery energy".** Terminal energy vs internal (after Ri loss) vs grid energy. Which `.vmod`/`.vsum` columns (e.g. `P_reess_terminal`, `P_reess_int`, `P_reess_loss`, `E_REESS...`)? HDEV's `E_battery` = net terminal energy (drive − regen). Which VECTO number is the like-for-like comparison?

**Steps 1–4 (already reviewed in PR #30; short re-check only).**
- **Q12** Re-run PR #30's step 1–4 tests against the 13 Nov code. Confirm BUG-2 and the `np.clip` fix, the kelvin change, the m/s `cdxa_v` change (zero numerical effect), and that `k_rot_wheel` replaces `k_rot` with no other change.

---

## 4. The parts

### Part A: line-by-line audit
Go through Appendix 1 line by line. For each line: what it does in plain words; the VECTO lines it stands in for; verdict. Answer Q1–Q12. List every hard-coded number (`3600`, `273.15`, `3.6`, `3`, `4`, `1e-3`, `3.6e6`, `0.0` …) and say whether it is a unit definition, a VECTO constant (source), or an HDEV choice. List every **unit conversion inside the function** (against rule 7). List every `raise` inside the function and say: can the parser check this before the driver model runs, or can it only be known after the driver model? (This decides where such checks live, see Part L Q-L3.)

### Part B: unit and analytic tests (`tests/consumption/`, `pytest`)
All tests call the loaded notebook function (or a clearly named variant in `reference_copy.py`).
1. **Energy bookkeeping:** with all efficiencies 1, no regen limits, no aux, `E_battery` equals the sum of `P_wheel·dt` (+ rotor term) to machine precision.
2. **Each aux term alone:** turn on one aux at a time; energy = W × the number of rows where its rule says on × dt. Count rows by `M` mode and by `V`; show the SP and Cond row counts.
3. **Sign tests for step 5:** rows with positive, negative, zero wheel power; coasting; braking above and below `v_no_regen`; `P_regen_max` binding; rotor term flipping the sign at the motor; mechanical drive PTO flipping the sign at the motor.
4. **Payload:** constant / linear / custom; a row exactly at a stop; a row a hair before `wp_s[0]` (BUG-2 and fix); a route with no stops.
5. **Weather:** hour index across midnight; `T_amb_h` too short (`IndexError`, loud: good); HVAC scalar vs per-hour; `PTO_always_on` scalar vs per-hour (currently not hour-indexed: show the bug); `W1/W2` one row per hour.
6. **PTO (step 6), using the final `pto_engine` outputs:** stop profile, stop constant, drive profile, drive constant (sweeper), a 0 s marker waypoint with only a drive part, `is_on` with only a drive profile, a drive profile running past the next stop, overlap → error, standing rows by `M == 0` vs `V == 0` (show the +1 row), stop at the last waypoint, two stops at one distance (parser should reject), refuse cycle 14.393 kWh (96 stops × 0.14993 kWh, PR #31) reproduced exactly.
7. **Shapes and types:** scalar vs array for every power input; empty route; integer inputs; NaN in any input (what happens? the parser must stop it: list it as a parser job).

### Part C: row-level reproduction of VECTO (the main part)
**Purpose:** prove the *assembly logic* is right, separately from the *efficiency assumptions*.
For each E2 `.vmod` (Regional, Urban, LongHaul × ReferenceLoad, LowLoading) and the MunicipalUtility refuse `.vmod` if available:
1. Feed VECTO's **own** rows (speed, acceleration, grade, dt, gear, mode/standstill) into `force_engine` + `consumption_engine` (as in PR #30 Part C), with VECTO's mass, ρ = 1.188, VECTO's CdxA, `J_rotor` and `i_total` per row from the `.vmod` `Gear` column, aux values from the `.vmod`.
2. Variant **"VECTO efficiencies"**: in `reference_copy.py`, replace the fixed efficiencies with the **per-row efficiencies VECTO actually had** (computed from the `.vmod` power columns at each component, e.g. motor el ÷ motor mech). This isolates the logic: with VECTO's own efficiencies, HDEV's assembly should reproduce VECTO's battery terminal power row by row. Any remaining gap is a logic difference (order of losses, sign decision, regen rule, aux rule, inertia), not an efficiency assumption.
3. Variant **"HDEV placeholders"**: 0.95 / 0.95 / 0.98, `regen_effeiciency` as the 3 Nov matrix used it (cite file + line), `v_no_regen` = 5 km/h (cite). This shows the size of the efficiency assumption.
4. Report per file and per column (wheel, gearbox in, motor mech, motor el, aux, battery terminal): trip energy (net, positive part, negative part), difference in % and kWh, row RMS, max row difference and where. **Explain every row difference larger than 1 % of that column or 0.1 kW** (find the cause). Then isolate causes one at a time: (a) one sign decision vs per-component; (b) rotor term placement; (c) regen speed limit; (d) regen cap; (e) SP/Cond activity rule; (f) coasting rule.

### Part D: sensitivity
On E2 Regional and Urban (HDEV's own driver rows, reference load): one-at-a-time effect on kWh/km of `motor_eff`, `inverter_eff`, `gearbox_eff`, `regen_effeiciency` (or its replacement), `v_no_regen`, `P_regen_max`, `J_rotor` / gear choice (lowest gear default vs `.vmod` gears), the SP/Cond rules, drive-PTO mechanical vs electric, each only over a **sourced** range (else `NO SOURCE`, skip). Tornado chart. Which are inside the 5 % target, which are not.

### Part E: deviation register
Every HDEV-vs-VECTO difference in `consumption_engine`, its size on E2 Regional/Urban and refuse, and the exact plain sentence to use in a client report.

### Part F: physics beyond VECTO (research only; candidates, not changes)
Short notes, each with sources and size, and whether it fits without breaking rule 11 (vectorised rows):
1. Real-world regenerative braking share of heavy BEVs (measured: e.g. Öko-Institut ELV-LIVE, ICCT, NREL Fleet DNA, OEM data) vs what HDEV's rule gives.
2. Battery terminal vs internal energy: how big the Ri loss is on E2 (report only, the battery engine is later).
3. Aux power while standing with the truck "on" vs "off" (driver breaks, waiting at a stop): does VECTO keep ES/HVAC on during long standstills? Is it realistic for refuse/urban?
4. Anything else in VECTO's PEV chain that HDEV has no term for (e.g. inverter losses at zero torque, motor drag when not coasting, gear-shift losses, clutch). Size each.

### Part G: how other tools assemble consumption
Read the code: FASTSim (`mohgsaad-art/fastsim`, the vehicle power-chain step: where each efficiency applies, regen limits, aux), `blast-lite`, `eflips-depot` (consumption model), `dt-cargo`, `spice_ev` (say if a tool has no such step). Also the documentation of TU Graz PHEM, Argonne Autonomie, US EPA GEM. One table: tool | order of losses | sign rule | regen limit | aux path | rotor inertia | file/line or doc page | difference from HDEV. Say for each whether you read code, full docs, or a summary.

### Part H: independent validation
Measured BEV truck kWh/km with enough detail to set HDEV up for **that** vehicle using sourced values only (missing → `BLOCKED`): e.g. Öko-Institut eActros, ICCT 2023 real-world HDV BEV, VTT/HSY e-refuse (2.3 kWh/km in collection), Mercedes eActros 600 tests, Volvo/Scania published tests, Nordic trials. Re-use the EEA validation set-up (`docs/research/eea-truck-validation-2026-11/`) where it helps. HDEV vs each source, difference in %.

### Part I: proposed new `consumption_engine` structure (not code for `src/`, a variant in `reference_copy.py`)
Write **one** clean variant `consumption_engine_v_proposed` that includes all decided changes (0.3) and the fixes you recommend, so Bob can read the whole thing at once. Constraints: pure, SI, no defaults in the signature, no checks that the parser can do, vectorised, ready for motor/gearbox maps later (e.g. efficiency as a scalar **or** a per-row array, so a map lookup can be added before the call without rewriting the function). For **every** change versus Appendix 1, a before/after snippet, why (source tag), measured effect (kWh and %), and engine/parser/defaults. Also propose the **return values**: what downstream (battery engine, charging session list, report) will need from this function (e.g. per-row battery power, trip energy, energy by part: traction, regen, each aux, PTO) and the cost of returning them.

### Part J: VECTO runs Bob should do (write them, don't run them)
Only if a question here cannot be closed from the existing `.vmod` files (e.g. a PEV run with drive PTO, or with a lower regen limit). Exact steps for VECTO 5.1.6 and which output columns to read. Put them in `reference/vecto/jobs/consumption-2026-11/` with a README. If none is needed, say so.

### Part K: performance
Time the current function, the step-6 fix, and `consumption_engine_v_proposed` on one day and on a full year (one call per operating date, ~250 dates, and also one long array), mean of 5 runs, state the CPU. Say what should be cached (e.g. the hour index, the CdxA table per weather year) and the cache key.

### Part L: the layers around the engine: industry-standard structure (Bob asked for this)
Bob's code today: engine functions in one notebook; parser and `defaults.py` not written yet (Kiro's earlier scaffolding exists in `src/resolver/`, `src/registry/`, `src/data_fetch/`, `src/validate/`); one project JSON planned (sections: vehicles, routes, assignments, calendar), UI posts raw JSON, all logic in Python; scenario = base + a list of changes; the original JSON is never overwritten. Decided split for weather (6 Oct): `fetch_dmi(...)` downloads once and saves raw; `build_weather(...)` is pure.

Answer, with evidence from real open-source projects (read their code/structure, give links): **pvlib-python** (closest analogue: HDEV aims to be "PVsyst for EVs"; look at `pvlib.iotools` for data fetch, `ModelChain` for orchestration, how defaults and "infer" steps are handled), FASTSim, `spice_ev`, `eflips-depot`, PyPSA, OpenModelica/FMI conventions if relevant, and general practice (pydantic models for config validation, "functional core, imperative shell", ports-and-adapters). Then:
- **Q-L1 Layers and order.** What layers should HDEV have and in what order (e.g. fetch → raw store/cache → parse/validate → resolve defaults (layered: base defaults → input-source defaults → OEM/spec values → user override, each value carrying its origin) → engine → results/report)? Where does each existing file in `src/` fit, and what is redundant?
- **Q-L2 `defaults.py`.** How to store defaults so each has value, unit, source, label, and per input source which fields it provides and which it locks (e.g. VDRI stop distances locked). Review the existing `src/resolver/defaults.py` and `src/registry/slot.py` against that.
- **Q-L3 Checks that can only happen after the driver model.** Some checks need driver rows (e.g. "every PTO stop has standing rows", "driver `S` matches `wp_s`"). The parser runs before the driver. Where should these live so the engine stays free of checks (e.g. a small "post-driver contract check" in the run layer)? What do other projects do?
- **Q-L4 Live data.** When a user picks "live" or "latest" data (e.g. DMI weather for the depot location, later Energidataservice prices, Eloverblik site load), **which function fetches it**, when, and where is it stored? Kiro's recommendation should cover: fetch functions in their own layer (no maths, only I/O), called by the run layer (not by the parser, not by the engine), raw response saved with query + date (reproducible reports), cache rules, what happens offline, and how the report shows which data version was used. Review `src/data_fetch/dmi_weather_climatology.py` (DRAFT; known issue: averages across years) against this.
- **Q-L5 Run layer now and later.** A test harness now (one JSON in, results out), `main.py` / FastAPI later. What is the minimal, clean harness that will not need rewriting when FastAPI comes? How should one call loop over vehicles × dates efficiently (driver once per route, force once, consumption per date)?
- **Q-L6 Project JSON.** A schema sketch (pydantic or JSON Schema) for the sections above, how scenarios (base + changes) are applied, and versioning of the schema.
Give **one** recommended structure as a folder tree with one line per file, labelled "Kiro's recommendation", plus the main alternative and why not. Keep it simple: Bob wants simple, readable, modular code, no thin helpers for logic that fits in a few lines.

### Part M: plain-English explainer
Write `docs/explainers/consumption-explained.md` in **very simple English** (Bob asked for this): what each step does, with a tiny worked example for one row (ILLUSTRATIVE numbers, labelled), why mass and air density must go in before the efficiency step (a change can flip a row from driving to regenerating), how a wheel power becomes battery power, what regen is and when it is allowed, how aux and PTO are added, and which VECTO lines each piece stands in for. Define every term (wheel power, regen, efficiency, terminal power, rotor inertia, mode).

---

## 5. Deliverables
1. `docs/research/consumption-review-2026-11.md`, in this order:
   - **Summary first (one page, plain English):** what is right, what is wrong (bugs with a minimal reproducing input), a ranked list of proposed changes (measured effect in kWh and %, source tag, engine/parser/defaults/fetch, VECTO / standard / HDEV assumption, new user input yes/no), and open items.
   - Gates 1–3.
   - Part A audit + Q1–Q12.
   - Parts B–E (tables first; graphs in the folder).
   - Parts F, G, H.
   - Part I: the proposed function, with every change explained.
   - Part L: the layer recommendation and Q-L1–Q-L6.
   - **Input table for the UI:** every input of `consumption_engine` | unit | who produces it (which function, parser, defaults, user) | can a fleet user give it | sourced default | conservative end.
   - **Parser jobs found**, **defaults.py entries found** (value, unit, source), **post-driver checks found**.
   - "Seen in passing (out of scope)", "Choices I made", "Bob to fetch" (link/DOI + exactly what), `BLOCKED` list.
2. `docs/research/consumption-review-2026-11/`: `_load_notebook.py`, `reference_copy.py` with variants, one runnable script per part, all CSVs and graphs. Each script prints the files it wrote.
3. `tests/consumption/`: Part B tests (`pytest`).
4. `reference/vecto/jobs/consumption-2026-11/` (Part J, only if needed).
5. `docs/explainers/consumption-explained.md` (Part M).
6. One PR to `main`. The description lists: what was done, how to run every script and the tests, the top 5 findings with numbers, every `NO SOURCE`, every `BLOCKED` item, and the "Bob to fetch" list.

## 6. Stop conditions
- A crash or wrong number on a realistic input → report as **BUG** with a minimal reproducing input, and keep going.
- Never edit the notebook or `src/`. Never decide an open design choice for Bob.

---

## Appendix 1: `consumption_engine`, code of record (Bob's paste, 13 Nov 2026, verbatim)
```python
def consumption_engine(T, S, V, M, dt,                                     # driver_model rows
                       k_lin, k_roll, k_rot, L, v_avg,                  # force_engine
                       m_vehicle, wp_s, payload_wp, beta,               # mass; payload_wp from payload_engine
                       t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,         # weather per hour + crosswind tables
                       ES, PS, HVAC, SP, cond, PTO_always_on,           # P_aux outputs (HVAC scalar or per hour)
                       pto_1s, pto_on_col, pto_start_col,               # pto_engine outputs
                       motor_eff, inverter_eff, gearbox_eff, regen_effeiciency, v_no_regen, P_regen_max=None):

  T, S, V, M = (np.asarray(x) for x in (T, S, V, M))                              # driver rows
  wp_s, payload_wp = np.asarray(wp_s, dtype=float), np.asarray(payload_wp, dtype=float)
  T_amb_h, cdxa_v = np.asarray(T_amb_h, dtype=float), np.asarray(cdxa_v, dtype=float)
  pto_1s, pto_on_col, pto_start_col = (np.asarray(x, dtype=float) for x in (pto_1s, pto_on_col, pto_start_col))

    # --- 1. mass per row: payload forward-filled by distance (payload_engine writes it on start + stop waypoints only)
  has_pl = ~np.isnan(payload_wp)                                   # waypoints where payload is set
  k_pl = np.searchsorted(wp_s[has_pl], S, side="right") - 1        # last payload waypoint at or before each row
  m_row = m_vehicle + payload_wp[has_pl][k_pl]                     # vehicle + payload [kg]

    # --- 2. weather hour of each row; hourly arrays start at hour 0 = t_start reference
  hour = ((t_start + T) // 3600).astype(int)                      # index into T_amb_h, W1, W2, HVAC (if per hour)

    # --- 3. air density and CdxA_eff per row
  rho_row = p_air / (R_air * (T_amb_h[hour] + 273.15))             # ideal gas, fixed pressure (HDEV; VECTO fixed 1.188)

  cdxa_tab = CdxA0 * np.asarray(W1) + np.asarray(W2)               # CdxA_eff table: one row per weather hour x speed grid (VECTO AirdragDataAdapter.cs 59-87)
  v_kmh = np.clip(v_avg * 3.6, cdxa_v[0], cdxa_v[-1])              # hold end values: below 60 km/h uses the 60 value like VECTO
  j = np.clip(np.searchsorted(cdxa_v, v_kmh, side="right") - 1, 0, len(cdxa_v) - 2)  # grid cell of each row
  w = (v_kmh - cdxa_v[j]) / (cdxa_v[j+1] - cdxa_v[j])              # position inside the cell
  cdxa_row = cdxa_tab[hour, j] * (1 - w) + cdxa_tab[hour, j+1] * w  # linear interpolation by speed, at the hour's own wind

    # --- 4. wheel power per row [W]: positive = driving, negative = braking/coasting
  P_wheel = m_row * k_lin + m_row**beta * k_roll + k_rot + rho_row * cdxa_row * L

    # --- 5. wheel power -> electric traction power [W]; positive = drawn, negative = recovered
  drivetrain_effeiciency = motor_eff * inverter_eff * gearbox_eff
  P_trac = np.where(P_wheel > 0, P_wheel / drivetrain_effeiciency, P_wheel * regen_effeiciency)  # Bob's old rule
  P_trac = np.where(M == 3, 0.0, P_trac)                           # coasting/rolling: no motor torque (VECTO BatteryElectricMotorController.cs 44-46)
  P_trac = np.where((M == 4) & (V <= v_no_regen), 0.0, P_trac)     # braking below v_no_regen: brakes only (same file 62-69; 5 km/h Constants.cs 323)
  if P_regen_max is not None:
      P_trac = np.maximum(P_trac, -P_regen_max)                    # regen cap; the rest goes to mechanical brakes


        # --- 6. aux power per row [W]; all inputs already electric W from P_aux / pto_engine
  n = len(T)
  pto_row = np.zeros(n)                                            # stop PTO W per row
  pto_active = np.zeros(n, dtype=bool)                             # True while a stop PTO profile runs
  for i in np.where(pto_on_col == 1)[0]:                           # loop over stops with PTO on (not over rows)
      at_stop = np.where((V == 0) & np.isclose(S, wp_s[i], rtol=0, atol=1e-3))[0]  # standing rows of this stop
      if len(at_stop) == 0:
          raise ValueError(f"no standing rows found for stop at {wp_s[i]} m")       # guard only
      k0 = at_stop[0] + int(pto_start_col[i])                      # PTO start inside the stop (middle, from pto_engine)
      k1 = k0 + len(pto_1s)
      if k1 > at_stop[-1] + 1:
          raise ValueError(f"PTO does not fit in stop at {wp_s[i]} m")             # guard only; parser extends stops
      pto_row[k0:k1] = pto_1s
      pto_active[k0:k1] = True

  moving = V > 0                                                   # SP on only when moving (VECTO ElectricAuxiliaries.cs, ID "STP")
  HVAC_row = np.asarray(HVAC, dtype=float)[hour] if np.ndim(HVAC) else float(HVAC)  # one number, or one per weather hour
  P_aux_row = (ES + PS + HVAC_row                                  # always on
               + SP * moving
               + cond * (moving | pto_active)                      # HDEV rule, see flags
               + PTO_always_on
               + pto_row)

    # --- 7. power at the battery terminals and trip energy
  P_battery = P_trac + P_aux_row                                   # [W]; aux via DC/DC eff 1.0 like VECTO (DeclarationData.cs line 124); battery Ri loss is in the battery engine
  E_battery = np.sum(P_battery * dt) / 3.6e6                       # net trip energy [kWh]

  return P_wheel, P_trac, P_aux_row, P_battery, E_battery
```
Driver modes (from `driver_model`, verify): `M` 0 standing, 1 accelerating, 2 cruising, 3 coasting, 4 braking (incl. holding speed downhill with brakes).

## Appendix 2: final producers (contract check only; load them from the notebook, these copies are for Gate 2)

### 2.1 `force_engine` (final 12 Nov, PR #30)
```python
def force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red, J_rotor, i_total):
  speed = np.asarray(speed, dtype=float)
  accel = np.asarray(accel, dtype=float)
  dt_s = np.asarray(dt_s, dtype=float)
  grade = np.asarray(grade, dtype=float)
  grade = np.arctan(grade / 100)
  v1 = speed
  v2 = np.maximum(speed + accel * dt_s, 0.0)
  v_avg = (v1 + v2)/2
  k_lin = (g * np.sin(grade) + accel) * v_avg
  k_roll = Crr * g * np.cos(grade) * v_avg
  k_rot_wheel = (theta_red  / r_dyn**2) * accel * v_avg
  k_rot_rotor = (J_rotor * i_total**2 / r_dyn**2) * accel * v_avg
  L = (v1 + v2) * (v1**2 + v2**2) / 8
  return k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg
```
`i_total` scalar or per row (gear); `J_rotor = 0` gives the old result.

### 2.2 `P_aux` (final 12 Nov, PR #31; exact VECTO for all 68,040 aux combinations)
```python
def P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on, ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0):
  powers = [np.asarray(p, dtype=float) for p in (ES_power, PS_power, HVAC_power, SP_power, cond_power)]
  effs = (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff)
  PTO_always_on = np.asarray(PTO_always_on, dtype=float)
  ES_power, PS_power, HVAC_power, SP_power, cond_power = (p * e for p, e in zip(powers, effs))
  PTO_always_on = PTO_always_on / PTO_eff
  return ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on
```
Note: the defaults in this signature are due to move to `defaults.py` (13 Nov decision). Report it; do not change it.

### 2.3 `pto_engine` (final 12 Nov, PR #31)
```python
def pto_engine(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff):
  stop = np.asarray(stop, dtype=float)
  is_on = np.array(is_on, dtype=float)
  stop_pto_t = np.asarray(stop_pto_t, dtype=float)
  stop_pto_w = np.asarray(stop_pto_w, dtype=float)
  drive_pto_w = np.asarray(drive_pto_w, dtype=float)
  drive_pto_t = np.asarray(drive_pto_t, dtype=float)
  is_on[0] = 0
  stop_steps = np.diff(stop_pto_t).astype(int)
  stop_1s = np.repeat(stop_pto_w[:-1], stop_steps)
  drive_steps = np.diff(drive_pto_t).astype(int)
  drive_1s = np.repeat(drive_pto_w[:-1], drive_steps)
  pto_dur = len(stop_1s)
  is_stop = stop > 0
  stop_on = is_stop & (is_on > 0) & (pto_dur > 0)
  pto_start = np.full (len(stop),np.nan)
  pto_start[stop_on] = np.floor((stop[stop_on] - pto_dur) / 2)
  stop_1s = stop_1s / stop_pto_eff
  drive_1s = drive_1s / drive_pto_eff
  return is_on, pto_start, stop_1s, drive_1s
```
Open contract point for you to resolve with evidence: the 30 Oct design allows each PTO part to be **either a constant (fills the whole stop, or the whole drive to the next stop) or a profile**. `pto_engine` only handles profiles. Say how constants should reach `consumption_engine` with the least change (e.g. a separate constant W per part from the parser), without editing `pto_engine`.

### 2.4 `payload_engine` (final): returns `payload` per waypoint, value on the start waypoint and on stop waypoints, NaN elsewhere.

### 2.5 HVAC set (final 13 Nov, PR #32): `HVAC_thermal` returns `HVAC_el` (W electric, one per weather hour) and `fuel_heat` (not used here). Enters `P_aux` with `HVAC_eff = 1.0`. All temperatures in kelvin. `ssm_total_w` and `climate_lookup` as in the 13 Nov notebook.

### 2.6 PTO placement rules (Bob's knowledge file `pto-knowledge-2026-11-12`, summary)
- Stop E-PTO (`.vptoel`, electric W): VECTO attaches it only to MunicipalUtility in declaration mode; standing time = stop + PTO; PTO in the middle (idle S/2, PTO, idle S/2); left-hold sampling; HDEV floors the start to a whole second.
- Drive PTO / road sweeping: engineering mode only; torque on the motor shaft (`PowertrainBuilderBase.cs` 343–345, `PEVPTO.cs`), electric power from the motor map; only while a gear is engaged and the shaft turns; time-weighted average per step (`PTODriveAuxiliary.cs`); second activation while one runs → error; a profile still running at the next stop keeps running.
- Cond on when an EM is on or the E-PTO is on (`Conditioning.cs` ~86).
- Refuse check: 96 PTO stops × 0.14993 kWh = 14.393 kWh.
