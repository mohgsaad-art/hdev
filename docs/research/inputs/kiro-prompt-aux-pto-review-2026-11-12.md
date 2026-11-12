# Kiro prompt: auxiliaries and PTO deep dive: `P_aux`, `SP_power_helper`, `pto_engine` + aux/PTO part of `consumption_engine` (12 Nov 2026)

Owner: Bob. Repo: `mohgsaad-art/hdev`. **Today's date is 12 November 2026.** When you research, look for documents up to this date (VECTO releases, regulation amendments, papers and reports from 2024–2026), not only older ones.

**Run the whole job in one uninterrupted pass.** Do not stop to ask Bob anything. If something is unclear, choose the option that changes the least, write it under "Choices I made", and carry on. Open **one PR** at the end.

**Branch:** work on the existing branch `aux-pto-review-2026-11` (it already holds Bob's latest notebook and this prompt). Put everything new in `docs/research/aux-pto-review-2026-11/`, `tests/aux_pto/` and `docs/explainers/aux-and-pto-explained.md`. Open the PR from this branch to `main`.

**Another Kiro job runs at the same time** on branch `force-engine-review-2026-11` (force engine and wheel power). Do not touch that branch, its folders (`docs/research/force-engine-review-2026-11/`, `tests/force_engine/`) or any shared file. Do not edit existing files anywhere in the repo; copy what you need into your own folder.

---

## 0. Rules for this job (read first)

1. **Do not edit Bob's engine code.** Bob writes all engine code himself. Do not change the notebook or anything under `src/`. You may copy functions into `docs/research/aux-pto-review-2026-11/reference_copy.py` and make experimental variants there, clearly named (e.g. `P_aux_v_checks`, `consumption_step6_v_pto1nov`). Every proposed change goes into the report as a **before / after snippet with its measured effect**.
2. **No invented numbers.** Every value you use or propose must come from a named source: VECTO source/resource file + line, Regulation (EU) 2017/2400 (incl. amendments), an ISO/SAE/UN/EN/NREL/JRC document, an OEM datasheet (tag it as an OEM claim), or a peer-reviewed paper or official report, with a link. If there is no source, write `NO SOURCE` and leave it as an open item. Illustrative test values are allowed only inside tests and must be labelled `ILLUSTRATIVE` in the test and the report.
3. **No silent fallbacks.** If an input is missing, do not fill it with a guess or a default. Mark the part `BLOCKED: <what is missing>` and keep going with the rest.
4. **Tag every statement in the report:**
   - `[VECTO]` read in VECTO source: give file, line numbers, branch and commit hash;
   - `[REG]` from Regulation (EU) 2017/2400 or its amendments: give annex/point;
   - `[SOURCE]` external document: link, date, and whether you read the full text or only an abstract;
   - `[OEM]` manufacturer claim (datasheet, press text);
   - `[CALC]` your own arithmetic from sourced inputs (show the inputs);
   - `[TEST]` result of a test you ran (name the test file and function);
   - `[ASSUMPTION]` an HDEV choice with no source;
   - `[SIMPLIFICATION]` a deliberate simplification;
   - `[OPEN]` not resolved.
   Never pass an assumption or inference off as fact. If you are not sure you read something correctly, say so.
5. **VECTO version.** Bob's `.vmod` files were written by **VECTO 5.1.6-RC** (header line of every `.vmod`). Read VECTO source in `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126` (HDEV notes cite this commit). Clone with `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/VECTO` (sparse checkout is fine). The earlier research docs (`docs/research/vecto/06-*`, `07-*`, `14-*`) used v5.1.3 `d16ba783c`. Re-check every line number they and this prompt cite; report mismatches.
6. **VECTO cannot run in your sandbox.** Anything needing a new VECTO run is Bob's job. Write the exact job files or GUI steps for him (Part I).
7. **Engine purity rule (Bob's architecture).** Engine functions are pure maths: every parameter is an argument, nothing hard-coded, no I/O, no unit conversion inside. Lookups in the VECTO tables, checks, defaults and gap-filling belong in the parser (`defaults.py`, not written yet). The engine takes a W value and does not care whether it came from VECTO or from the user. Judge every proposed change against this rule and say for each one: **engine** or **parser**.
8. **Bob's validation rule.** Matching VECTO exactly is **not** validation. VECTO is the audit reference. Validation means comparison with several independent sources (measured fleet data, studies, standards, OEM figures), showing how far HDEV and each source differ. A change that only swaps one assumption for another, with no standard or validation behind it, is not worth making. Say so when that is the case.
9. **Bob's modelling stance.** HDEV must not underestimate energy. Where the physics or the timing rule is uncertain, show which choice is the conservative one.
10. **No hard-to-get user inputs.** Bob does not want features that need inputs users can't realistically provide. Prefer inputs derived from data already asked for (vehicle type, mission, weather, body type).
11. Plain English in the report. Short sentences. Define every technical term the first time you use it. Refer to the owner only as "Bob".
12. **Never decide an open design choice for Bob.** Show evidence; if you recommend, label it "Kiro's recommendation".

### 0.1 Pitfalls from earlier Kiro PRs (do not repeat them)

These happened in PRs #21, #23 and #27:
- **Municipal results without PTO power** (PR #23). Any refuse/Municipal energy number must include the stop PTO, and say so.
- Running a cycle with the wrong vehicle (e.g. LongHaul without the trailer), or comparing low-load results at reference mass.
- Filling missing values silently.
- A "gate" test that compares hard-coded numbers instead of running the actual code.
- Results that change between runs. Every script must be deterministic; run each main script twice and confirm identical CSVs.
- Claiming "done" without evidence. Every claim in the summary points to a CSV, test or file line.
- **Repeating research that is already done.** `docs/research/vecto/06-auxiliaries-all.md`, `07-pto-all.md`, `14-pto-aux-followups.md` and `docs/decisions/2026-10-08_session-closeout-paux.md` already trace much of VECTO's aux and PTO logic. Read them first. Re-verify their key claims at `b8d6126` (list each as CONFIRMED / CORRECTED / NOT FOUND), then spend your time on what they did not cover.

### 0.2 Scope

**In scope:**
- `P_aux` (notebook cell 9; Appendix 1.1).
- `SP_power_helper` (notebook cell 10; Appendix 1.2).
- `pto_engine` (notebook cell 14; Appendix 1.3).
- The **aux and PTO part** of `consumption_engine` (notebook cell 16), steps 6 and 7: placing stop and drive PTO on rows, the on/off rules for each aux, and the sum at the battery terminals (Appendix 1.4).

**Out of scope (other Kiro jobs):**
- `HVAC_thermal`, `ssm_total_w`, `climate_lookup` (a separate job). Here HVAC is only an input W value (VECTO HVAC-Table mode, or the thermal model's output with `HVAC_eff = 1.0`).
- `force_engine` and wheel power (the parallel job).
- Drivetrain efficiencies, regen, battery losses (step 5, later job).
If you notice a bug there in passing, list it under "Seen in passing (out of scope)" with file and line only.

### 0.3 Inputs (all already in the repo)

| What | Path | Used in |
|---|---|---|
| Bob's latest notebook = **code of record** (12 Nov) | `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb` | everything |
| VECTO 5.1.6-RC runs, generic E2 BEV: Regional, Urban, LongHaul × ReferenceLoad, LowLoading (6 `.vmod`) + `BEV_E2.vsum`. Per-row aux columns: `P_aux_ES_el`, `P_aux_AC_el`, `P_aux_PS_el`, `P_aux_STP_el`, `P_aux_COND_el`, `P_aux_el`, `P_aux_el_HV`, `P_DC/DC_In/Out`, `EM_E2_off`, `DriverAction` | `docs/research/vecto/` | C |
| HDEV test harness v1.7 (E2 aux set-up per mission, lines ~103–130: ES, PS, HVAC, SP values and their VECTO sources) | `docs/research/vecto/hdev_test_harness_v1.7.py` | gates, C |
| VECTO aux tables and PTO files (copies) | `reference/vecto/resources/VAUX/` (ES-Tech, ES-Tech_Medium, PS-Table, SP-Table, SP-Axles, SP-Tech, HVAC-Table, Cond-Table, PTO-tech), `reference/vecto/resources/MissionCycles/MunicipalUtility.vdri`, `MunicipalUtility_PTO_generic.vptoel/.vptoc/.vptol` | A, B, D |
| VECTO C# copies (convenience; re-check against `b8d6126`) | `reference/vecto/cs/` (`ElectricAuxiliaries.cs`, `HeavyLorryAuxiliaryDataAdapter.cs`, `AuxiliaryDataAdapter.cs`, `PTOCycleController.cs`, …) | A |
| Earlier aux/PTO research (read first) | `docs/research/vecto/06-auxiliaries-all.md`, `07-pto-all.md`, `14-pto-aux-followups.md`, `docs/decisions/2026-10-08_session-closeout-paux.md`, branch `research/pto-aux-followups` | A, E |
| Gate script | `docs/research/drag-default-test-2026-11/run_steps.py` | gate 1 |
| Source PDFs already fetched | `docs/research/electric-truck-mixer-etm.pdf`, `Carrier_Transicold_Vector_eCool_ENG.pdf`, `E_Produktblatt_eEconic_ENG_screen.pdf`, `BEV_BATTERY_ELECTRIC_VEHICLE.pdf` and others in `docs/research/` | E, F |
| Open-source tools to read (Bob's forks) | `mohgsaad-art/fastsim`, `mohgsaad-art/eflips-depot`, `mohgsaad-art/spice_ev`, `mohgsaad-art/dt-cargo` | G |

**How to load the notebook functions (do this exactly):** write `docs/research/aux-pto-review-2026-11/_load_notebook.py`. It reads the `.ipynb` JSON, takes the **code cells only**, skips cell 0 (it imports `torch`, `gymnasium`, `requests` etc., which are not needed and must NOT be installed), and `exec`s the rest in one namespace that starts with `import math, bisect; import numpy as np`. Do not change any cell text. Print the list of function names loaded. All tests and scripts import functions from this loader, so they always test Bob's exact code.

---

## 1. What these functions do and where they sit

HDEV is a Python engine that sizes battery-electric trucks and depots. It is built to be auditable against VECTO (the EU certification simulator for heavy-duty vehicles, Regulation (EU) 2017/2400).

Pipeline: payload/**PTO on waypoints** → crosswind engine → driver model (1 s rows) → force engine → **consumption engine** (wheel power, drivetrain, **aux + PTO on rows**, battery terminals) → battery/charging → sizing.

- `P_aux` turns one W value per auxiliary (from a VECTO table via the parser, or a custom user value) into electric W, using a factor per aux. Works for a scalar or an hourly array.
- `SP_power_helper` reproduces VECTO's steering pump: baseline table × axle shares × technology factors → mechanical W (then × 0.7 in `P_aux`).
- `pto_engine` works on the **waypoints** (one row per waypoint, stop durations), before the driver: it expands the stop and drive PTO profiles to one value per second, divides by their efficiencies, and finds where the stop PTO starts inside each stop (centred, like VECTO).
- `consumption_engine` step 6 places the PTO and aux power on the 1 s driver rows; step 7 adds them to traction power at the battery terminals.

### 1.1 Decisions already made by Bob (do not reopen; you may report evidence against them)

**Aux (P_aux):**
- Lookups happen in the parser; the engine takes W values. Each aux has a VECTO dropdown and a custom-value override labelled non-VECTO.
- `P_aux` multiplies each aux by a factor because VECTO does. Defaults: ES 0.7, PS 1.0, HVAC 1.25, SP 0.7, Cond 1.0. Always-on PTO is **divided** by `PTO_eff` (default 1.0 = already electric). These reproduce the E2 `.vmod`: ES 1428.57 W × 0.7 = 1000 W; HVAC 200 W × 1.25 = 250 W; SP 32.87 W × 0.7 = 23.0 W (re-check).
- Bob's intended code of record has checks for `PTO_always_on < 0` and `PTO_eff <= 0`. **The notebook version does not yet** (Appendix 1.1). Test both and report.
- `HVAC_eff` must be 1.0 when HVAC comes from the thermal model (parser job).
- `PTO_always_on` must accept a per-hour array (for a later fridge model). `P_aux` already works with arrays.
- No aux power during depot charging (decided; out of scope).

**SP:** `SP_power_helper` matches VECTO `SteeringPump.cs` (58–114, /100 at 142) and `HeavyLorryAuxiliaryDataAdapter.cs` (188–190, 220). One technology dropdown applied to all steered axles. VECTO switches the BEV electric steering pump off when stopped (`ElectricAuxiliaries.PowerDemand` drops "STP"; `SteeringPump` and `SteeringPump_el` share the ID "STP", `Constants.cs` 59–60, so this looks incidental). HDEV reports this as "follows VECTO's current behaviour".

**PTO design (final 31 Oct):**
- No VECTO 0/1/2/3 labels. Each waypoint has one on/off flag (`is_on`). If on, there can be a **stop part** (while standing at that stop) and/or a **drive part** (from leaving that stop until the next stop).
- Each part is **one number** (fills its whole window: whole stop, or whole drive to the next stop, e.g. a sweeper) or a **`t`/`W` profile** played once (e.g. bin lift, compaction).
- A drive profile still running at the next stop **keeps running** (matches VECTO).
- A 0 s marker row can start a drive part where there is no real stop.
- One sweeping power per route (flagged deviation for VECTO sweeper files).
- Always-on PTO stays in `P_aux`; constants skip `pto_engine`.
- One efficiency field per PTO kind (stop / drive / always-on), default 1.0; electric = entered ÷ efficiency.
- **Stop timing (VECTO default):** standing time = stop time + PTO duration, PTO in the **middle** of the stop, floor for odd seconds (HDEV choice). Optional route-level "use stop time as PTO time" gives standing = max(stop, PTO), flagged non-VECTO. Done in the parser before the driver.
- Profile times must be whole seconds (parser check); `np.repeat` builds the 1 s profile; per-second averaging for fractional times is parked.
- Same PTO power at every stop.
- `pto_engine` is **final on the engine side** (returns `is_on, pto_start, stop_1s, drive_1s`).

**Consumption side (agreed):** payload and stop PTO are placed in the consumption engine by distance (and `V == 0` for stops), not carried through the driver.

### 1.2 What is known to be open or broken (leads to re-check, not facts)

1. `consumption_engine` still takes the **old** `pto_engine` outputs (`pto_1s, pto_on_col, pto_start_col`). It has no drive part, no stop constants, no overlap check. It is not yet wired to the 1 Nov outputs (`is_on, pto_start, stop_1s, drive_1s`).
2. Aux timing differs from VECTO: HDEV runs SP only while moving (`V > 0`) and Cond only while moving **or** stop PTO is active. VECTO aux are `DemandType.Constant` and Cond is Dynamic (`HeavyLorryAuxiliaryDataAdapter.cs` 61–110). VECTO's Cond rule: on whenever any electric motor is not `EmOff` (`Conditioning.cs` 83–91); so it is 0 when standing and when coasting. Earlier note says "stopped" means |v| ≤ 0.01 m/s (`Vehicle.cs` 262). After the harness fix, HDEV aux totals were +0.7 % (Regional) / +1.9 % (Urban) vs VECTO.
3. VECTO refuse profile (`MunicipalUtility_PTO_generic.vptoel`): 23 s, **0.14993 kWh per stop** (re-check).
4. For a BEV, VECTO's electric PTO (`EPTO`) is an electric aux with no extra idle/transmission loss; the mechanical `PTO-tech.csv` losses apply only with a gearbox-driven PTO (from `14-pto-aux-followups.md`; re-check).
5. VECTO drive PTO / sweeper (`PTO_Power` cycle column, `.vptor`) exists in engineering mode only (`PowertrainBuilderBase.cs` ~325, 339, 321–349).
6. There is **no MunicipalUtility `.vmod`** in the repo. So VECTO's stop-PTO placement and energy have never been checked against a VECTO output row by row.
7. The DC/DC converter is 1.0 efficient in VECTO declaration mode (`DeclarationData.cs` ~124); HDEV adds aux straight to the battery terminals.

---

## 2. Gates (must pass before anything else)

**Gate 1, environment:** run `docs/research/drag-default-test-2026-11/run_steps.py` unchanged. Confirm Chain S, variant V1, reference load: RegionalDelivery **0.9749** and UrbanDelivery **0.8502** kWh/km (from the `step3_kwh_per_km.csv` your run writes, ±0.0005). If it fails, STOP everything except Parts A and B and report what differs.

**Gate 2, VECTO aux values from the tables:** using only the VECTO tables in `reference/vecto/resources/VAUX/` (parsed by your own script, not hard-coded) and the notebook's `SP_power_helper` + `P_aux`, reproduce the E2 per-aux electric W in the `.vmod` for Regional, Urban and LongHaul: ES, AC (HVAC), PS, STP, COND. Report each: table value → HDEV electric W → `.vmod` W → difference.

**Gate 3, code of record:** list every difference between the notebook's `P_aux` and `pto_engine` and the versions in `src/engine/` (if present) and the versions in Appendix 1. The notebook is the code of record.

---

## 3. Questions to answer from the VECTO source (Part A)

Answer each with `[VECTO]` file + lines + commit, and a verdict: **MATCH**, **DEVIATION (already flagged)**, **DEVIATION (new, flag it)** or **BUG**. Quote the exact C# lines.

- **Q1 Meaning of each table value and factor, for a PEV (battery-electric) lorry.** For ES, PS, HVAC (table mode), SP and Cond: is the table value mechanical W or electric W? What factor does VECTO apply for a PEV, in which direction (× or ÷), and why (e.g. the ES "alternator efficiency" 0.7 for a vehicle that has no alternator)? Does HDEV's `P_aux` (multiply ES/PS/HVAC/SP/Cond, divide only always-on PTO) reproduce VECTO's electric W for **every** group × mission × technology a PEV can have? Build the full table (Part B).
- **Q2 When each aux is on, for a PEV.** For each aux: on while standing? accelerating? cruising? coasting? braking? when the motor is `EmOff`? at the start/stop seconds? Read `ElectricAuxiliaries.PowerDemand`, `Conditioning.cs`, the `DemandType` handling and the "STP" stop rule. Confirm or correct the leads in §1.2 item 2. Say whether the STP-off-when-stopped behaviour is deliberate or a side effect of the shared ID, from source and from any VECTO changelog or issue you can find.
- **Q3 Cond.** What "Cond" (conditioning) stands for in VECTO for a BEV (cooling/heating of electric components?), what `Cond-Table.csv` values mean, by which keys they are looked up, and how they depend on motor activity. What does VECTO do with Cond while an electric PTO runs at a stop?
- **Q4 SP.** Full `SteeringPump.cs` logic: baseline table (U+F / B / S parts), axle shares, technology factors per steered axle, averaging, which technologies are allowed for a PEV, max steered axles, empty table cells (groups with no Municipal/Construction; groups 6–8). Any mission or speed dependence?
- **Q5 PS.** `PS-Table.csv`: which columns a fully electric PS uses (`_el` columns; `HeavyLorryAuxiliaryDataAdapter.cs` ~139–143), which technologies are allowed for a PEV, mission dependence.
- **Q6 HVAC table mode.** `HVAC-Table.csv` "Default" for trucks: what the value means and why × 1.25 (re-check the factor and its source line).
- **Q7 Electric path to the battery.** HV vs LV aux (`P_aux_el_HV`), the DC/DC converter (efficiency, where applied, `P_DC/DC_missing`), and whether any aux power is reduced or shifted (e.g. supplied by regen first). Does HDEV's "sum of aux W added to traction W at the battery terminals" match?
- **Q8 Stop PTO timing.** Re-verify at `b8d6126`: standing time = stop + PTO duration (`DistanceBasedDrivingCycle.cs` ~218–220); exact rule for where the PTO sits inside the stop (centred? rounding?); the 4 PTO-activity states (`PTOActive`) from `14-pto-aux-followups.md`; how VECTO samples the `.vptoel` profile within its variable time steps (step-hold, linear interpolation, or averaging) vs HDEV's `np.repeat` per second; what happens if two PTO stops are back to back, or the stop is shorter than the profile.
- **Q9 Drive PTO.** Sweeper (`PTO_Power` column), `.vptor`, and any other drive-PTO path for a BEV: when it starts and stops, whether it continues through a stop, overlap rules (VECTO raises an error for overlapping drive jobs?), and on which shaft it acts for a BEV (motor shaft, so motor losses apply?). Confirm whether these are engineering-mode only.
- **Q10 Anything VECTO models for aux/PTO that HDEV has no term for** (e.g. PTO shaft idle losses for gearbox PTO, Padd_hv, aux during engine-off, electric idle losses). List each with size on E2 runs where measurable.

---

## 4. The parts

### Part A: line-by-line audit
Go through Appendix 1.1–1.4 line by line. For each line: what it does in plain words; the VECTO lines it stands in for; verdict. Answer Q1–Q10. List every hard-coded number that is not an argument and classify it (unit definition, VECTO constant with source, numerical tolerance, HDEV choice).

### Part B: unit tests (`tests/aux_pto/`, runnable with `pytest`)
1. **`P_aux`:** scalars, lists, per-hour arrays (incl. `PTO_always_on` per hour); every aux 0; negative power for each input (incl. `PTO_always_on`: the notebook does **not** check it, so report what happens); efficiency 0 or negative for each (incl. `PTO_eff = 0`: report what happens: division by zero, inf, silent?); NaN inputs; mixed scalar and array shapes; the stale comment "undo the multiply above".
2. **VECTO table sweep (the main `P_aux` + SP test):** parse the VECTO VAUX tables yourself. For **every** vehicle group × mission × technology combination a PEV lorry can have, compute HDEV electric W (notebook `SP_power_helper` + `P_aux` with VECTO factors) and VECTO electric W from an **independent re-implementation of the VECTO C#** (`SteeringPump.cs`, `HeavyLorryAuxiliaryDataAdapter.cs`, etc.), written from the C# without looking at Bob's code. Report every mismatch. Also list every combination where the table is empty or invalid, so the parser can give a clear error.
3. **`SP_power_helper` edge cases:** 1–4 steered axles; 5 axles (VECTO max is 4?); wrong shapes; technology rows ≠ axle rows; empty arrays; NaN cells.
4. **`pto_engine`:**
   - the VECTO refuse profile from `MunicipalUtility_PTO_generic.vptoel` (convert kW → W in your test, as the parser will): `stop_1s` length 23 s? energy per stop 0.14993 kWh?
   - centring: even and odd `stop − pto_dur`; stop exactly equal to the profile; stop 1 s shorter (must raise);
   - `is_on[0]` forced to 0; `is_on` length ≠ waypoints; `is_on` with values other than 0/1;
   - **fractional profile times** (e.g. `t = [0, 1.5, 3]`): `np.diff(t).astype(int)` truncates silently; show the energy error and confirm the parser must reject it;
   - non-increasing times; a one-point profile (empty `stop_1s`); zero-length drive profile; negative W;
   - efficiency 0 or negative; efficiency > 1;
   - `pto_start` NaN on non-PTO waypoints: does anything downstream break on NaN?
5. **Old vs new interface:** call the notebook's `consumption_engine` with the 1 Nov `pto_engine` outputs passed into the old argument slots (`pto_1s = stop_1s`, `pto_on_col = is_on`, `pto_start_col = pto_start`). Show exactly what breaks (e.g. `is_on == 1` on a waypoint that has no stop → "no standing rows found"), with a minimal input.

### Part C: aux timing vs VECTO, row by row
For each of the 6 `.vmod` files (Regional, Urban, LongHaul × ReferenceLoad, LowLoading; LongHaul is **truck + trailer**, set it up from VECTO files or mark `BLOCKED`):
1. From the `.vmod`, for each aux column (`P_aux_ES_el`, `P_aux_AC_el`, `P_aux_PS_el`, `P_aux_STP_el`, `P_aux_COND_el`): W level and on/off state per row, broken down by driving state (standing / accelerating / cruising / coasting / braking, using `v_act`, `acc`, `DriverAction`, `EM_E2_off`). Find the exact `DriverAction` enum in source for the labels. This is the ground truth for Q2.
2. Apply HDEV's current rules (Appendix 1.4) to **the same VECTO rows** (so the driver is not part of the comparison): per aux, kWh per cycle, difference vs VECTO in kWh and %, and on which row types the differences sit.
3. Test rule variants in `reference_copy.py`, one at a time: (a) SP on when `V > 0.01 m/s`; (b) Cond on only when the motor is not off (needs a motor-off proxy from HDEV data: e.g. mode 3 coasting and standing rows; say which proxy matches VECTO best); (c) Cond during stop PTO (VECTO rule from Q3); (d) everything always on (conservative bound). For each: kWh per cycle vs VECTO, and which is conservative.
4. Then with HDEV's own driver rows (notebook `driver_model`, E2 reference set-up as harness v1.7): the same totals, so Bob sees the combined effect. **Pass the driver thresholds in m/s** (`lac_min_v=50/3.6`, `os_min_v=50/3.6`, `os_allowed=2.5/3.6`, `v_min_coast=5/3.6`): the notebook defaults are km/h-sized numbers, so with defaults coasting and overspeed never switch on (found in PR #30). Use the same driver set-up as PR #30, Part D.

### Part D: PTO on rows: the missing consumption-engine part
Bob will write this code himself. Your job is to build a **test variant** in `reference_copy.py` (`consumption_step6_v_pto1nov`) that follows the decided design in §1.1 exactly, test it hard, and give Bob a before/after snippet.
1. Inputs: the 1 Nov `pto_engine` outputs (`is_on, pto_start, stop_1s, drive_1s`) plus the constants (stop constant W, drive constant W, each with its efficiency).
2. Placement rules (decided):
   - stop profile: starts at the first standing row of that stop + `pto_start`;
   - stop constant: on all standing rows of that stop;
   - drive profile: starts at the first moving row after the stop; keeps running past the next stop if longer than the drive;
   - drive constant: on all moving rows until the next stop;
   - a 0 s marker waypoint can start a drive part;
   - constants divided by their efficiency when placed;
   - overlap: what happens when a drive profile from stop *k* is still running when stop *k+1* starts its own drive part (follow VECTO per Q9; if VECTO raises an error, show the HDEV equivalent);
   - matching stop rows to waypoints: `V == 0` and distance within 1e-3 m (as the current code); check what happens with two stops at the same distance (parser should reject) and with float drift in `S`.
   - Cond rule while a PTO part runs (from Q3 and Bob's open item).
3. Tests: MunicipalUtility VDRI with the VECTO refuse profile on every stop VECTO uses it on (find which stops from source/cycle): total PTO energy = number of PTO stops × 0.14993 kWh? standing time per stop = stop + 23 s? centred? A sweeper case (drive constant, ILLUSTRATIVE W). A mixed refuse case (stop profile + drive profile). Edge cases: PTO on the last waypoint; drive part with no next stop; drive profile longer than the rest of the route; PTO on a waypoint with stop 0 (marker).
4. Runtime: the current loop is over PTO stops, not rows. Time it on MunicipalUtility (all stops) and on a year (365 days).
5. Report each rule as VECTO / HDEV decision / new proposal.

### Part E: physics and data beyond VECTO (research; candidates, not changes)
Do not repeat what `06`, `07`, `14` already cover; extend them. For each item: best sources (standards, measured studies, OEM data, then models), typical size for 12–40 t electric trucks, how HDEV could include it **without hard-to-get inputs** (rule 10), engine or parser, and whether VECTO's value is likely low or high (rule 9).
1. **Measured auxiliary consumption of battery-electric trucks and buses.** Base electric load (ES), electric air compressor duty cycle (PS), electric steering, and component conditioning (battery/motor thermal management, cold and hot climate; the Dollinger 2021 lead: battery heating ≈ 4 %). Fleet trials (e.g. Öko-Institut ELV-LIVE, NREL Fleet DNA and NREL truck evaluations, Nordic/Swedish e-truck trials, e-bus aux-share studies). Compare with VECTO's constants.
2. **Aux while standing at stops.** BEV aux keep running at stops (no engine idle). What do measurements show for standing aux power, and does VECTO's standstill rule (SP off, Cond off) underestimate it?
3. **PTO energy by body type, measured:** refuse collection (leads: Ban & Stipetić 2019; MDPI Applied Sciences 11(7) 3033; VTT refuse ≈ 2.3 kWh/km; check each), concrete mixer drum (`docs/research/electric-truck-mixer-etm.pdf`), refrigerated body / TRU (`Carrier_Transicold_Vector_eCool_ENG.pdf`; ATP K-value method), crane, tipper, tail lift, sweeper. For each: kWh per stop / per hour / per km, conditions, source type (measured / simulated / rating), licence. This feeds Bob's planned **PTO profile library** (every entry cited and tagged).
4. **Fridge body (parked HDEV model, research only):** heat load K = W/(S·ΔT) from the ATP certificate or the ATP class limits, COP of electric TRUs vs outside temperature, door-opening uplift evidence. Say what a minimal, sourced model would need (it would feed `PTO_always_on` per hour). Do not build it.
5. **Weather dependence of aux** (other than cab HVAC, which is the other job): conditioning and compressor duty in cold weather.

### Part F: independent validation
Compare HDEV's aux and PTO totals (E2 Regional/Urban; refuse case from Part D) with measured or published figures from Part E: aux share of total energy, kWh per stop for refuse PTO, kWh per hour for mixers/fridges. Set HDEV up with that vehicle's sourced values only; anything missing → `BLOCKED`. Show the spread: HDEV vs each source vs VECTO. If nothing measured exists, write `NOT FOUND`.

### Part G: how other tools do it (read the code where it is open)
FASTSim (`mohgsaad-art/fastsim`), `eflips-depot`, `spice_ev`, `dt-cargo` (Bob's forks), plus documentation of Autonomie, TU Graz PHEM, US EPA GEM, and any e-bus/e-truck aux model you find. Per tool: how aux is modelled (constant, per state, weather-dependent, per body), how PTO/body equipment is modelled, and what HDEV can learn. Say whether you read code, full documentation, or only a summary.

### Part H: parser jobs
List every check, lookup and conversion the parser must do for aux and PTO (start from the lists in §1.1 and add what you found): table lookups by group/mission/technology, kW → W, whole-second and increasing profile times, `is_on` length, stop extension, rejecting two stops at the same distance, rejecting fractional profile times, `HVAC_eff = 1.0` in thermal mode, PEV-allowed technologies only, empty table cells, efficiency > 0, custom-value labelling. One table: job | why | source.

### Part I: VECTO runs Bob should do (write them, don't run them)
At least: a **MunicipalUtility BEV run with the generic refuse PTO** (declaration mode), so the stop-PTO placement and energy can be checked row by row; if VECTO has no generic PEV refuse vehicle, find the closest VECTO generic vehicle and say exactly what Bob must change. If useful: an engineering-mode sweeper run (`PTO_Power` column) and a `.vptor` drive-PTO run. Give exact job files or GUI steps for VECTO 5.1.6, and the `.vmod` columns that must be written (`P_aux_*`, PTO columns, `DriverAction`, `EM_*_off`). Put them in `reference/vecto/jobs/aux-pto-2026-11/` with a README.

### Part J: plain-English explainer
Write `docs/explainers/aux-and-pto-explained.md`: what each aux is (ES, PS, HVAC, SP, Cond, PTO kinds), where VECTO's numbers come from, what `P_aux`, `SP_power_helper` and `pto_engine` do line by line, how aux and PTO land on the driver rows, with small worked examples (ILLUSTRATIVE, labelled). Define every term; explain from scratch.

---

## 5. Deliverables

1. `docs/research/aux-pto-review-2026-11.md`, in this order:
   - **Summary first (one page):** what is right, what is wrong, a ranked list of proposed changes (each with measured effect in kWh and %, source tag, engine or parser, VECTO / standard / HDEV assumption), and open items.
   - Re-verification of `06`, `07`, `14` (CONFIRMED / CORRECTED / NOT FOUND per key claim).
   - Gates 1–3.
   - Part A audit table + Q1–Q10 answers.
   - Parts B–D results (tables first; graphs under `docs/research/aux-pto-review-2026-11/`).
   - Parts E, F, G tables; the **PTO profile library candidates** table (source, tag, licence, values).
   - **Proposed changes:** before/after snippet against Appendix 1, why (source tag), measured effect, engine or parser, and whether it only swaps one assumption for another.
   - **Deviation register:** every HDEV-vs-VECTO difference in aux and PTO, its size, and the exact sentence to use in a client report.
   - Part H parser jobs.
   - "Seen in passing (out of scope)", "Choices I made", "Bob to fetch" (links/DOIs for everything you could not open), and the `BLOCKED` list.
2. `docs/research/aux-pto-review-2026-11/`: `_load_notebook.py`, `reference_copy.py` with variants, the independent VECTO aux re-implementation, one runnable script per part (`python run_part_c.py` etc.), all CSVs and graphs. Each script prints the files it wrote.
3. `tests/aux_pto/`: Part B tests, runnable with `pytest`.
4. `reference/vecto/jobs/aux-pto-2026-11/` (Part I).
5. `docs/explainers/aux-and-pto-explained.md` (Part J).
6. One PR to `main`. The description lists: what was done, how to run every script and the tests, the top 5 findings with numbers, every value with `NO SOURCE`, every `BLOCKED` item, and the "Bob to fetch" list.

## 6. Stop conditions
- If a test shows Bob's code crashes or gives a wrong number on a realistic input, report it as **BUG** with a minimal reproducing input, and keep going.
- Never edit the notebook, `src/` or any existing file. Never decide an open design choice for Bob.

---

## Appendix 1: code of record (Bob's notebook, 12 Nov 2026; verbatim; load it from the notebook, do not retype it)

### 1.1 `P_aux` (notebook cell 9)
```python
##5.1 Electrical system - finalized
def P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on, ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0): #get rid of hardcoding later
  # pure: electric W per aux = input W * efficiency factor
  # works for one number or an array using numpy
  # PTO_always_on = always-on PTO only (chiller, mixer); stop PTO comes from pto_engine and is laid on rows in the consumption engine

  powers = [np.asarray(p, dtype=float) for p in (ES_power, PS_power, HVAC_power, SP_power, cond_power)] # convert first so lists work
  effs = (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff)
  PTO_always_on = np.asarray(PTO_always_on, dtype=float)

  for p in powers:
      if np.any(p < 0):
          raise ValueError("aux power cannot be negative")
  for e in effs:
      if e <= 0:
          raise ValueError("efficiency must be > 0")

  ES_power, PS_power, HVAC_power, SP_power, cond_power = (p * e for p, e in zip(powers, effs))
  PTO_always_on = PTO_always_on / PTO_eff  # undo the multiply above, then divide: shaft W / efficiency = electric W --> rewrite this better later

  return ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on
```
Bob's intended version also checks `PTO_always_on < 0` and `PTO_eff <= 0` (loops over `powers + [PTO_always_on]` and `effs + (PTO_eff,)`), and drops the "undo the multiply" comment.

### 1.2 `SP_power_helper` (notebook cell 10)
```python
# returns mechanical W, goes into P_aux as SP_power gets multiplied by 0.7 for electrical W

def SP_power_helper(SP_baseline, SP_axle_shares, SP_tech_factors):

  SP_baseline = np.asarray(SP_baseline, dtype=float)         # (UF, B, S) in W, from SP-Table.csv
  SP_axle_shares = np.asarray(SP_axle_shares, dtype=float)   # one (UF, B, S) row in % per steered axle, from SP-Axles.csv
  SP_tech_factors = np.asarray(SP_tech_factors, dtype=float) # one (UF, B, S) row per steered axle, from SP-Tech.csv or custom

  if SP_axle_shares.ndim != 2 or SP_axle_shares.shape[1] != 3 or len(SP_axle_shares) == 0:
      raise ValueError("SP_axle_shares needs one (UF, B, S) row per steered axle")
  if SP_tech_factors.shape != SP_axle_shares.shape:
      raise ValueError("need one technology (UF, B, S) per steered axle") # VECTO throws here too

  parts = SP_baseline * SP_axle_shares.sum(axis=0) / 100 # each part summed over the steered axles
  parts = parts * SP_tech_factors.mean(axis=0)           # VECTO: average technology factor over all steered axles
  return float(parts.sum())                  # add the 3 parts,
```

### 1.3 `pto_engine` (notebook cell 14)
```python
#PTO engine
def pto_engine(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff):

  stop = np.asarray(stop, dtype=float) # stop time of every waypoint/row in s, 0 means no stop; this is just the stop column from vecto or custom inputs this also includes PTO usage time
  is_on = np.array(is_on, dtype=float)       # 1 = PTO on at this waypoint, 0 = off
  stop_pto_t = np.asarray(stop_pto_t, dtype=float) #pto time profile
  stop_pto_w = np.asarray(stop_pto_w, dtype=float) #pto power profile
  drive_pto_w = np.asarray(drive_pto_w, dtype=float) #drive power profile
  drive_pto_t = np.asarray(drive_pto_t, dtype=float) #drive time profile


  is_on[0] = 0 # the first waypoint is the depot: never PTO there

  # turn each profile into one power value per second
  stop_steps = np.diff(stop_pto_t).astype(int) # how many seconds each value lasts
  stop_1s = np.repeat(stop_pto_w[:-1], stop_steps) # stop PTO, W per second

  drive_steps = np.diff(drive_pto_t).astype(int)
  drive_1s = np.repeat(drive_pto_w[:-1], drive_steps) # drive PTO, W per second

  pto_dur = len(stop_1s)   # stop profile length [s]

  #assigning stop pto profiles to waypoints
  is_stop = stop > 0 # true where the vehicle stops
  stop_on = is_stop & (is_on > 0) & (pto_dur > 0) # its a stop & stop pto is on & it has stop profile

  # putting the stop PTO in the center of stops same as VECTO
  pto_start = np.full (len(stop),np.nan) # NaN = no stop profile here
  pto_start[stop_on] = np.floor((stop[stop_on] - pto_dur) / 2) # floor for odd seconds = HDEV assumption

  too_short = np.where(pto_start < 0)[0]
  if len(too_short) > 0:
      raise ValueError(f"PTO ({pto_dur} s) is longer than the stop at waypoint(s) {too_short.tolist()}; the parser must extend these stops")

  #apply the effeciencies
  stop_1s = stop_1s / stop_pto_eff
  drive_1s = drive_1s / drive_pto_eff

  return is_on, pto_start, stop_1s, drive_1s
```

### 1.4 `consumption_engine` (notebook cell 16): **only steps 6–7 are in scope**
```python
def consumption_engine(T, S, V, M, dt,                                     # driver_model rows
                       k_lin, k_roll, k_rot, L, v_avg,                  # force_engine
                       m_vehicle, wp_s, payload_wp, beta,               # mass; payload_wp from payload_engine
                       t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,         # weather per hour + crosswind tables
                       ES, PS, HVAC, SP, cond, PTO_always_on,           # P_aux outputs (HVAC scalar or per hour)
                       pto_1s, pto_on_col, pto_start_col,               # pto_engine outputs
                       motor_eff, inverter_eff, gearbox_eff, regen_effeiciency, v_no_regen, P_regen_max=None):

  # ... steps 1-5 (mass, weather hour, air, wheel power, drivetrain) are OUT OF SCOPE for this job ...
  # (step 2 sets: hour = ((t_start + T) // 3600).astype(int))

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
Note: if `PTO_always_on` is a per-hour array, it is added here without `[hour]` indexing (unlike `HVAC`). Test what happens and report.
