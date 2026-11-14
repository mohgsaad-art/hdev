# Kiro prompt: wheel-power deep dive: `force_engine` + wheel-power part of `consumption_engine` (12 Nov 2026)

Owner: Bob. Repo: `mohgsaad-art/hdev`. **Today's date is 12 November 2026.** When you research, look for documents up to this date (VECTO releases, regulation amendments, papers and reports from 2024–2026), not only older ones.

**Run the whole job in one uninterrupted pass.** Do not stop to ask Bob anything. If something is unclear, choose the option that changes the least, write it under "Choices I made", and carry on. Open **one PR** at the end.

**Branch:** work on the existing branch `force-engine-review-2026-11` (it already holds Bob's latest notebook and this prompt). Put everything new in `docs/research/force-engine-review-2026-11/`, `tests/force_engine/` and `docs/explainers/force-engine-explained.md`. Open the PR from this branch to `main`.

---

## 0. Rules for this job (read first)

1. **Do not edit Bob's engine code.** Bob writes all engine code himself. Do not change the notebook or anything under `src/`. You may copy functions into `docs/research/force-engine-review-2026-11/reference_copy.py` and make experimental variants there, clearly named (e.g. `force_engine_v_asin`, `force_engine_v_rotor`). Every proposed change goes into the report as a **before / after snippet with its measured effect**.
2. **No invented numbers.** Every value you use or propose must come from a named source: VECTO source/resource file + line, Regulation (EU) 2017/2400 (incl. amendments), an ISO/SAE/UN/NREL/JRC/EPA document, or a peer-reviewed paper or official report, with a link. If there is no source, write `NO SOURCE` and leave it as an open item. Illustrative test values are allowed only inside tests and must be labelled `ILLUSTRATIVE` in the test and the report.
3. **No silent fallbacks.** If an input is missing, do not fill it with a guess or a default. Mark the part `BLOCKED: <what is missing>` and keep going with the rest.
4. **Tag every statement in the report:**
   - `[VECTO]` read in VECTO source: give file, line numbers, branch and commit hash;
   - `[REG]` from Regulation (EU) 2017/2400 or its amendments: give annex/point;
   - `[SOURCE]` external document: link, date, and whether you read the full text or only an abstract;
   - `[CALC]` your own arithmetic from sourced inputs (show the inputs);
   - `[TEST]` result of a test you ran (name the test file and function);
   - `[ASSUMPTION]` an HDEV choice with no source;
   - `[SIMPLIFICATION]` a deliberate simplification;
   - `[OPEN]` not resolved.
   Never pass an assumption or inference off as fact. If you are not sure you read something correctly, say so.
5. **VECTO version.** Bob's `.vmod` files were written by **VECTO 5.1.6-RC** (header line of every `.vmod`). Read VECTO source in `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126` (HDEV notes cite this commit). If you also find a 5.1.6 tag, say whether the relevant code differs. Clone with `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/VECTO` (sparse checkout is fine). Re-check every VECTO line number in this prompt; they are leads, not facts.
6. **VECTO cannot run in your sandbox.** Anything needing a new VECTO run is Bob's job. Write the exact job/GUI steps for him instead (Part I).
7. **Engine purity rule (Bob's architecture).** Engine functions are pure maths: every parameter is an argument, nothing hard-coded, no I/O, no unit conversion inside. Checks, lookups, defaults and gap-filling belong in the parser (`defaults.py`, not written yet). Judge every proposed change against this rule and say for each one: **engine** or **parser**.
8. **`force_engine` must stay mass-free, temperature-free and CdxA-free** [DECIDED by Bob]. That is the whole point of it: the slow driver runs once, `force_engine` gives per-row coefficients once, and every payload × weather case is then a cheap multiply-add. Any proposal that breaks this must say so loudly and show the runtime cost.
9. **Bob's validation rule.** Matching VECTO exactly is **not** validation. VECTO is the audit reference. Validation means comparison with several independent sources (other models, standards, measured data), showing how far HDEV and each source differ. A change that only swaps one assumption for another, with no standard or validation behind it, is not worth making. Say so when that is the case.
10. **Bob's modelling stance.** HDEV must not underestimate energy. Where the physics is uncertain, show which choice is the conservative one.
11. Plain English in the report. Short sentences. Define every technical term the first time you use it. Refer to the owner only as "Bob".
12. **Never decide an open design choice for Bob.** Show evidence; if you recommend, label it "Kiro's recommendation".

### 0.1 Pitfalls from earlier Kiro PRs (do not repeat them)

These happened in PRs #21, #23 and #27. Avoid every one:
- Running LongHaul with the wrong vehicle. Group-2 LongHaul in VECTO is **truck + trailer** (different mass, axles, CdxA). Build it from the VECTO segment/trailer files or mark it `BLOCKED`.
- Comparing low-load results at reference mass, or against the wrong VECTO baseline.
- Filling missing values silently (e.g. rotating inertia = 0 without saying so).
- A "gate" test that compares hard-coded numbers instead of running the actual code.
- Results that change between runs. Every script must be deterministic; run each main script twice and confirm identical CSVs.
- Claiming "done" without evidence. Every claim in the summary points to a CSV, test or file line.

### 0.2 Scope

**In scope:**
- `force_engine` (notebook cell 8; Appendix 1.1).
- The **wheel-power part** of `consumption_engine` (notebook cell 16), steps 1–4 only: mass per row, weather hour per row, air density per row, CdxA_eff per row, `P_wheel` (Appendix 1.2).
- Consistency of these forces with the driver's own force model (`coast_acc` inside `driver_model`, and `coast_distance`; Appendix 1.3), because Bob decided both must use the same formulas: same `g`, same β rolling form, same grade handling, same wheel inertia.

**Out of scope (later Kiro jobs):** `consumption_engine` steps 5–7 (drivetrain efficiencies, regen, aux, PTO placement, battery). Do not review them. If you notice a bug there in passing, list it under "Seen in passing (out of scope)" with file and line only.

### 0.3 Inputs (all already in the repo)

| What | Path | Used in |
|---|---|---|
| Bob's latest notebook = **code of record** (12 Nov) | `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb` | everything |
| VECTO 5.1.6-RC runs, generic E2 BEV: Regional, Urban, LongHaul × ReferenceLoad, LowLoading (6 `.vmod`) + `BEV_E2.vsum` | `docs/research/vecto/` | C, D, E |
| HDEV test harness v1.7 (E2 vehicle set-up: masses, `crr_total_vecto`, `crr_eff`, `BETA`, `R_DYN`, `THETA_WHEELS`, `M_RED_WHEELS`, CdxA table, `P_AIR`, `R_AIR`) | `docs/research/vecto/hdev_test_harness_v1.7.py` | B–G |
| E2 drag table (`e2_table()`), Chain S, gate script | `docs/research/drag-default-test-2026-11/` (`run_steps.py`, `_chain.py`, `_e2_drag.py`) | gate, D |
| Older repo copy of the force engine | `src/engine/force_engine.py` | A (diff only) |
| VECTO source | `mohgsaad-art/VECTO`, branch `IEPC-experiments` | A, C |
| Open-source tools to read (Bob's forks) | `mohgsaad-art/fastsim`, `mohgsaad-art/dt-cargo`, `mohgsaad-art/eflips-depot`, `mohgsaad-art/spice_ev` | H |
| Earlier review docs (context, re-check numbers) | `docs/research/driver-model-review-2026-11.md`, `docs/research/drag-default-test-2026-11.md`, `docs/research/vecto/01…14-*.md` | context |

**How to load the notebook functions (do this exactly):** write `docs/research/force-engine-review-2026-11/_load_notebook.py`. It reads the `.ipynb` JSON, takes the **code cells only**, skips cell 0 (it imports `torch`, `gymnasium`, `requests` etc., which are not needed and must NOT be installed), and `exec`s the rest in one namespace that starts with `import math, bisect; import numpy as np`. Do not change any cell text. Print the list of function names loaded. All tests and scripts import functions from this loader, so they always test Bob's exact code.

---

## 1. What these functions do and where they sit

HDEV is a Python engine that sizes battery-electric trucks and depots. It is built to be auditable against VECTO (the EU certification simulator for heavy-duty vehicles, Regulation (EU) 2017/2400).

Pipeline: payload/PTO on waypoints → crosswind engine → driver model (1 s rows) → **force engine** → **consumption engine** → battery/charging → sizing.

`force_engine` takes the driver rows (speed at start of step, acceleration, grade in %, dt) and returns per-row coefficients that do **not** depend on mass, temperature or CdxA:
- `k_lin = (g·sin θ + a)·v_avg` → multiplied by mass: slope + vehicle inertia power;
- `k_roll = Crr·g·cos θ·v_avg` → multiplied by `m^β`: rolling power;
- `k_rot = (θ_red / r_dyn²)·a·v_avg` → wheel inertia power (mass-free already);
- `L = (v1+v2)(v1²+v2²)/8` → multiplied by `ρ·CdxA_eff`: air power (exact step average of ½v³ under constant acceleration);
- `v_avg` → used to look up CdxA_eff.

The consumption engine then computes, per row: `P_wheel = m·k_lin + m^β·k_roll + k_rot + ρ·CdxA_eff·L`.

### 1.1 Decisions already made by Bob (do not reopen; you may report evidence against them)

- β rolling form **everywhere**: `F_roll = Crr_eff·g·m^β·cos θ`, β = 0.9 (VECTO `Physics.cs` ~51). The parser passes `Crr_eff` (harness `crr_eff()`), which is claimed to reproduce VECTO's per-axle, load-dependent rolling resistance exactly for any mass. Default `beta = 1.0` gives the plain linear form.
- `g = 9.80665` (VECTO `DeclarationData.cs` ~72). The force engine takes `g` as an argument.
- Grade: the driver returns grade per row as an **altitude secant** (rise over row distance, in %). `force_engine` turns it into an angle with `atan`.
- Wheel inertia: `θ_red / r_dyn²` in `force_engine` must equal the driver's `m_red_wheels` (parser computes both from the same inputs). Motor rotor inertia is currently **ignored** (harness `[ASSUMP]`).
- CdxA_eff per row by speed from the crosswind table (`CdxA0·W1 + W2`), 60–130 km/h grid, held at the end values below 60 and above 130 km/h (like VECTO). The 10° yaw clamp is an HDEV decision for real-wind runs (`crosswind_engine` argument). `crosswind_engine` itself is final and out of scope.
- Air density per row from temperature: `ρ = p / (R·(T + 273.15))`, fixed pressure (VECTO uses a fixed 1.188).
- Hourly weather is held constant over each hour (no interpolation).
- Payload changes at stops only, matched to rows by distance in the consumption engine.
- Fixed 1 s rows.

### 1.2 History (from earlier HDEV sessions; treat as leads to re-check, not facts)

- 8 Oct: `force_engine` written. Two hand tests passed then (probably with `g = 9.81`): v = 20 m/s, a = 0, flat, Crr 0.0055 → `(0, 1.0791, 0, 4000, 20)`; v = 10, a = 1 → `(10.5, 0.56653, 0, 580.125, 10.5)`. Recompute with `g = 9.80665` and say what changes.
- 22 Oct, HDEV's own driver + force engine vs VECTO 5.1.6 E2, trip totals: rolling exact; air −0.1 % (Regional) / −2.2 % (Urban); positive wheel energy −2.3 % / −1.3 %. **Driver and force effects were never separated.** Part C separates them.
- Earlier T13 test vs a VECTO 2.2 12 t truck: rolling +0.02 %, air +1.1 %, positive wheel energy −2.0 %.
- Driver: coast rows use instantaneous air drag; the force engine uses the step average. Leftover estimated at 0.02–0.29 kWh per cycle of braking hidden in coast rows.
- Stop arrival: the driver snaps distance onto the stop point, so on that row distance ≠ `v_avg·dt` (max ~0.18 m per stop; Municipal +9.4 m over 11.24 km).
- **New lead [CALC by Claude, 12 Nov, from the two ReferenceLoad `.vmod` files, sum of positive values × dt]:**

  | kWh, positive part | Regional | Urban |
  |---|---|---|
  | `P_veh_inertia` | 8.60 | 45.46 |
  | `P_wheel_inertia` | 0.197 | 1.044 |
  | `P_E2-em_inertia_loss` (motor rotor) | 0.228 | 1.219 |
  | `P_gbx_inertia` | 0.000 | 0.000 |
  | `P_trac` | 67.04 | 78.57 |

  So VECTO's motor rotor inertia is about the same size as wheel inertia (about 1.5 % of positive traction on Urban), and HDEV ignores it. Verify this, then answer Q5.
- **Second lead [CALC by Claude]:** in the Regional `.vmod`, `v_act` equals the distance moved in that row in 83 % of rows. That suggests `v_act` is the **interval-average** speed, not the start speed. `force_engine` expects the **start** speed. Confirm from VECTO source (Q7) before any row-level comparison, and reconstruct v1/v2 correctly.
- Winter leads (from Bob's status file; re-check each): Chalmers/Volvo simulation (Ramesh Babu 2025) uses Crr 0.007 at 20 °C rising to 0.014 at −20 °C; Mercedes eActros 600 winter tour 2025 (OEM press text) about +25 % at −2 °C, of which rolling + air about 15 points; Öko-Institut ELV-LIVE measured −0.13 kWh/km per +10 °C at a mean of 0.96 kWh/km; HDEV's earlier cold-tyre test used an ISO 28580 temperature coefficient outside its stated range.

---

## 2. Gates (must pass before anything else)

**Gate 1, environment:** run `docs/research/drag-default-test-2026-11/run_steps.py` unchanged. Confirm Chain S, variant V1 (E2 drag table), reference load: RegionalDelivery **0.9749** and UrbanDelivery **0.8502** kWh/km (from its own `step3_kwh_per_km.csv`, regenerated by your run, ±0.0005). If it fails, STOP everything except Part A and report what differs.

**Gate 2, code of record:** load the notebook with `_load_notebook.py`. Diff `force_engine` (notebook) against `src/engine/force_engine.py` and report every difference. The notebook is the code of record.

**Gate 3, VECTO wheel terms:** for each of the 6 `.vmod` files, check that per row `P_trac ≈ P_slope + P_air + P_roll + P_veh_inertia + P_wheel_inertia` (or find the exact identity VECTO uses, from source). Report the identity and the residual. This tells you which columns to compare against.

---

## 3. Questions to answer from the VECTO source (Part A)

Answer each with `[VECTO]` file + lines + commit, and a verdict: **MATCH**, **DEVIATION (already flagged)**, **DEVIATION (new, flag it)** or **BUG**. Quote the exact C# lines.

- **Q1 Slope.** How does VECTO get the gradient for a simulation step (from altitude: rise over road distance? over horizontal distance?), how is it turned into an angle (`atan`, `asin`, or used directly), and what is the slope force formula (`Vehicle.cs`, `DrivingCycleData`, `DistanceBasedDrivingCycle.cs`)? Which mass: vehicle mass only, or including reduced wheel mass? Compare with `force_engine` (`atan` of the row secant). Give the numeric difference between `sin(atan(G))`, `asin(G)` and `G` at 2, 6, 10, 20 %. Also: the driver's `coast_distance` uses `cos(rise/run)` with no `atan` (Bob decided this matches VECTO's `ComputeCoastingDistance`). Is it consistent for VECTO to use an angle in one place and the plain ratio in another? Report, don't change.
- **Q2 Rolling.** Exact VECTO formula (`Vehicle.cs` rolling resistance; `VehicleData.cs` ~292–311 total coefficient per axle; `Physics.cs` ~51 exponent). Which mass, which `cos`. Prove algebraically whether `Crr_eff·g·m^β` equals VECTO's sum over axles for **any** mass when axle load shares are fixed (show the derivation), and confirm that VECTO keeps axle load shares fixed when payload changes. Then test it on LowLoading vs ReferenceLoad (Part C). For LongHaul (truck + trailer): does the same single `Crr_eff` still work when the trailer axles are included?
- **Q3 Air.** Exact VECTO air-drag power for a step (`CrosswindCorrectionCdxALookup.cs`, `AirdragDataAdapter.cs` ~59–87, `Vehicle.cs`): the average form used, which speed CdxA_eff is looked up at (start, end, average), how it interpolates, what happens below 60 and above 130 km/h, and in declaration mode which ρ. Compare with `L` in `force_engine` and step 3 of `consumption_engine`.
- **Q4 Vehicle and wheel inertia.** Exact VECTO formulas for `P_veh_inertia` and `P_wheel_inertia`, how reduced wheel mass is built (`Wheels.cs`, `VehicleData.cs` ~307), and `r_dyn` (`Wheels.cs` ~74, `Wheels.csv`). Compare with `k_lin` (inertia part) and `k_rot`.
- **Q5 Motor rotor and gearbox inertia.** Where and how VECTO applies `P_E2-em_inertia_loss` and `P_gbx_inertia` for a BEV (E2 layout, `ElectricMotor.cs`, gearbox classes). What inputs it needs (rotor inertia in `.vemo`, ratios). Is it applied at the wheel side (so it belongs in wheel power) or on the motor side (so it belongs in the later drivetrain step)? State which, from source. Then size it (Part C) and answer: what would an HDEV term look like (e.g. `J_rotor·i_total²/r_dyn²` as an extra reduced mass, gear dependent), and where would `J_rotor` come from for a user truck (Annex Xb standard values? EEA data? `NO SOURCE`?). Do not decide; show numbers.
- **Q6 Constant acceleration within a step.** Confirm that VECTO assumes constant acceleration within a simulation interval and computes power as force × average speed. Confirm the identity `a·v_avg·dt = ½(v2² − v1²)`, so inertia energy telescopes exactly over a trip.
- **Q7 `.vmod` output definitions.** For every column you use (`v_act`, `acc`, `grad`, `altitude`, `dist`, `dt`, `P_*`, `CdxA_eff`): is it the value at the start, the end, or the average over the output interval? How does VECTO aggregate its variable internal steps (~0.5 s) into 1 Hz rows (`ModalDataContainer` or similar)? This decides how you feed the `.vmod` trace into `force_engine`.
- **Q8 Standing rows and the last braking step.** What VECTO writes for the second the truck stops and the second it starts. Compare with `force_engine`'s `v2 = max(v + a·dt, 0)` and the driver's stop snapping.
- **Q9 Sign conventions and units** of every `P_*` column used.
- **Q10 Anything else** VECTO adds to wheel power that HDEV has no term for (e.g. wheel-end friction savings `P_wheelEnd_*`, brake losses, any road-surface or temperature terms). List each, with size on the E2 runs.

---

## 4. The parts

### Part A: line-by-line audit
Go through Appendix 1.1 and 1.2 line by line. For each line: what it does in plain words; the VECTO lines it stands in for; verdict. Answer Q1–Q10. List every hard-coded number that is not an argument (`/100`, `/8`, `273.15`, `3.6`, `3600`, `1e-3`, `0.0` …) and say whether each is a unit definition, a VECTO constant (source), a numerical tolerance, or an HDEV choice. Flag any unit conversion inside an engine function (Bob's rule: none; the `3.6` in step 3 of `consumption_engine` converts `v_avg` to km/h for the CdxA grid; say whether the parser should pass the grid in m/s instead).

Also check robustness, each as a short test (Part B): `if theta_red > 0` with an array `theta_red`; `r_dyn = 0` with `theta_red > 0`; negative `theta_red`; `dt_s` as array vs scalar; NaN in grade or speed; empty arrays; negative speed in; integer inputs.

### Part B: unit and analytic tests (`tests/force_engine/test_force_engine.py`, runnable with `pytest`)
1. Neutral defaults (β = 1, θ_red = 0) reproduce the simple road-load equation exactly; the two 8 Oct hand tests (recomputed with `g = 9.80665`).
2. `L` equals a fine numerical integral of ½v³ over a constant-acceleration step, for random v1 ≥ 0 and a (including steps that end at v2 = 0).
3. **Energy closure over a whole trip** (exactness tests, using rows from the notebook's `driver_model` on a route with stops and ±grades; route values `ILLUSTRATIVE`):
   - Σ m·a·v_avg·dt = ½m(v_end² − v_start²) to machine precision;
   - Σ m·g·sin θ·v_avg·dt vs m·g·Δh (altitude change from the driver's altitude): report the gap and split it into (i) `sin(atan(G))` vs G, (ii) row distance ≠ `v_avg·dt` at stop arrivals;
   - Σ k_rot·dt over a stop-to-stop trip = 0.
4. The v2 clamp: rows where `v + a·dt < 0` (inputs not from the driver). Show what the inertia term then gives vs ½(v2² − v1²)/dt, and confirm the driver never produces such rows (scan all its rows on all 6 VECTO cycles).
5. Mass-free property: `P_wheel(m)` from the coefficients equals a direct force × speed calculation at m for 5 masses and β ∈ {1, 0.9}.
6. Wheel-power part of `consumption_engine` (steps 1–4), with ILLUSTRATIVE inputs:
   - payload mapping: constant, linear and custom payloads from `payload_engine`; a row exactly at a stop distance (`side="right"`), a row a hair before `wp_s[0]` (float error: does `k_pl = -1` wrap to the **last** payload? that would be a bug), a route with no stops;
   - hour index: `t_start + T` past the end of `T_amb_h` (IndexError?), a trip crossing midnight, `t_start` not a whole hour;
   - CdxA interpolation: equals `np.interp` per hour; below 60 / above 130 km/h held; check the shape contract between `crosswind_engine` outputs (`W1`, `W2`) and the `cdxa_tab[hour, j]` indexing (one row per weather hour?) and say what the parser must pass;
   - ρ: equals ISO 2533 values at sea level for −20, 0, 15, 30 °C (source the ISO values).

### Part C: row-level reproduction of VECTO (the main part)
**Purpose:** isolate the force maths from the driver. Feed VECTO's **own** speed trace into `force_engine` + the `P_wheel` equation and compare each term with VECTO, row by row.

For each of the 6 `.vmod` files (Regional, Urban, LongHaul × ReferenceLoad, LowLoading):
- Inputs from the `.vmod`: speed, acceleration, grade/altitude, dt, reconstructed correctly per Q7 (start speed v1 and end speed v2 of each row).
- Vehicle from VECTO files via harness v1.7: mass (curb + body + payload for that loading; **trailer for LongHaul**), `Crr_eff` and β, `R_DYN`, `THETA_WHEELS`, ρ = 1.188, CdxA table from `crosswind_engine` at declaration wind (3 m/s at 4 m, Hellmann 0.2, no yaw clamp, as harness v1.7). Cite every value.
- Two CdxA variants: (i) HDEV CdxA from the crosswind table; (ii) VECTO's own `CdxA_eff` column. The difference between them isolates the crosswind/lookup part from the `L` part.

Report per file and per term (`P_roll`, `P_air`, `P_slope`, `P_veh_inertia`, `P_wheel_inertia`, sum): trip energy (net, positive part, negative part), difference in % and kWh, row RMS difference, max row difference and where, and `CdxA_eff` RMS difference. **Explain every row-level difference larger than 1 % of that term or 0.1 kW** (find the cause; do not just report it). Then isolate the causes one at a time: (a) v1/v2 reconstruction; (b) grade conversion `atan` vs `asin` vs none (per Q1); (c) CdxA lookup speed (per Q3); (d) mass in the slope term with/without reduced wheel mass (per Q1/Q4); (e) motor rotor inertia added as an extra reduced mass (per Q5, `J_rotor` from the E2 `.vemo`, gear from the `.vmod` `Gear` column).

Then the driver split: compare the 22 Oct totals (HDEV driver + force engine vs VECTO) with this part (VECTO trace + force engine vs VECTO). The difference is the driver's share of the earlier error. Give it per term.

LowLoading vs ReferenceLoad is the direct test of the β mass scaling: report the rolling error at both loadings. If `Crr_eff·g·m^β` is exact, both errors must be ~0.

### Part D: consistency with the driver model
Bob decided `coast_acc`/`coast_distance` (inside the driver) and `force_engine` must use the same physics.
1. Code check, term by term (Appendix 1.1 vs 1.3): `g`, β form and which mass, grade (`atan` in `coast_acc`, plain ratio in `coast_distance`, `atan` in `force_engine`), wheel inertia (`m_red_wheels` vs `θ_red/r_dyn²`), air (instantaneous in `coast_acc` vs step average). Table: term | driver form | force-engine form | same? | effect.
2. Numeric check: run the notebook's `driver_model` with coasting on (E2 reference vehicle, E2 drag table from `e2_table()`, ρ 1.188, reference CdxA) on Regional and Urban. Compute `P_wheel` for the same rows with `force_engine` at the **same** mass, ρ and CdxA. On coast rows (mode 3), wheel power with no motor torque should equal minus the drivetrain drag power: residual = `P_wheel + F_drag(v)·v_avg`. Report the residual energy (kWh) per cycle and split it between instantaneous-vs-average air and anything else you find. On standing rows (mode 0) every coefficient must be exactly 0.
3. Stop-arrival rows: total distance error and energy effect per cycle.

### Part E: time step
Run the notebook's driver at `dt = 1.0, 0.5, 0.25` on Regional and Urban (same route, same vehicle) and push each through `force_engine` + `P_wheel`. Show convergence of each term (kWh) and of positive wheel energy. Say whether 1 s is good enough for the force part (within what %), and the runtime cost of going finer. Do not repeat the driver-behaviour metrics already done in PR #21; only energy terms.

### Part F: physics beyond VECTO (research + measured effect; candidates, not changes)
For each item: what the physics is; the best sources (standards first, then measured studies, then models); typical size for a 12–40 t electric truck; how HDEV could include it **without breaking rule 8** (usually a per-hour or per-route factor applied in the consumption engine, supplied by the parser); what extra user input it needs (Bob does not want inputs users can't realistically provide; prefer inputs derived from data already asked for, e.g. weather); and the measured effect on E2 Regional and Urban using `reference_copy.py` variants. Mark clearly which are conservative.

1. **Tyre temperature and cold rolling resistance.** ISO 28580 temperature correction (and its stated valid range), UN R117, SAE J2452, measured cold-tyre and tyre warm-up studies for trucks (Crr high at trip start, falling as the tyre warms), the Chalmers/Volvo and Mercedes winter leads above. Test at −10, 0, +10, +25 °C.
2. **Road surface.** Wet, snow, slush rolling resistance and road texture (look for VTI (Sweden) and other Nordic road-research reports, and peer-reviewed tyre/road papers). Could hourly precipitation from DMI drive a factor? Size the effect.
3. **Speed dependence of Crr** for truck tyres (measured evidence only; VECTO uses constant Crr).
4. **Air density details.** Humidity (e.g. CIPM-2007 moist-air formula), station pressure vs fixed 101325 Pa, altitude (the tool is meant for any country). Size each for Danish and Alpine conditions.
5. **Motor rotor / drivetrain inertia** (from Q5), as a wheel-side term.
6. **Curve (cornering) resistance** for trucks: any sourced magnitude. If only models, say so.
7. **Road grade quality.** Grade from GPS or elevation models is noisy and inflates energy if not smoothed (look for NREL road-grade work and similar). HDEV will take GPS routes later. What smoothing do established tools use, and what error does noise add? This belongs to the GPS adapter/parser, not the engine; say so.
8. **Coast-down road load as an input.** Many fleets or OEMs have coast-down results (`F0 + F1·v + F2·v²`, SAE J1263/J2263; EU constant-speed test, Regulation 2017/2400 Annex VIII). How would a parser map such data onto HDEV's `Crr`, β and CdxA inputs, and what is lost?

### Part G: how other tools do it (read the code where it is open)
Compare term by term with HDEV: slope (angle conversion, which distance), rolling (form, mass, load and temperature dependence), air (instantaneous vs step average, density), vehicle + wheel + rotor inertia, time step and average-speed handling, and any terms HDEV lacks.
- Read the code: NREL FASTSim (`mohgsaad-art/fastsim`), `dt-cargo`, `eflips-depot` and `spice_ev` (Bob's forks; say if a tool has no road-load model).
- Read the documentation (or code if public): US EPA GEM (Phase 2 greenhouse-gas model for heavy trucks), TU Graz PHEM, Argonne Autonomie, SUMO's electric-vehicle energy model, and any TUM truck-simulation tool you find.
Give one table: tool | each term's formula | source file/line or doc page | difference from HDEV | does it change HDEV's numbers (estimate only if sourced). Say for each tool whether you read code, full documentation, or only a summary.

### Part H: independent validation of the road-load model
Search for measured road-load data you can compare HDEV's force model with (Bob's rule 9):
- published coast-down or constant-speed road-load results for medium and heavy trucks (NREL, TNO, ICCT, TU Graz, JRC, OEM test reports);
- measured wheel or traction energy per km for trucks similar to the E2 (12 t rigid), split by term if anyone publishes it;
- certified CdxA and tyre values already in the repo (`docs/research/hdv_2024_*.csv`, EEA tables) only as inputs, not as validation of the formulas.
For every source: what was measured, conditions, how HDEV compares (set HDEV up with that vehicle's sourced values only; anything missing → `BLOCKED`, no guessing). If nothing measured exists for a term, write `NOT FOUND`. List every document you could not open in a **"Bob to fetch"** table with its link or DOI.

### Part I: VECTO runs Bob should do (write them, don't run them)
Only if they answer a question this job could not close (e.g. a run with rotor inertia set to 0 to confirm Q5; a run at a steep-grade cycle to test Q1). Exact GUI steps or job files for VECTO 5.1.6, generic E2, and which `.vmod` columns must be written. Put them in `reference/vecto/jobs/force-engine-2026-11/` with a README. If no run is needed, say so.

### Part J: performance
Time `force_engine` and steps 1–4 of `consumption_engine` on one Regional day and on 365 days × 3 payloads × hourly weather (mean of 5 runs; say the CPU). Report memory for the coefficient arrays. Say whether the coefficients should be cached per route (they are mass-free) and what the cache key would be.

### Part K: plain-English explainer
Write `docs/explainers/force-engine-explained.md`: what `force_engine` does, why it splits the forces into mass-free parts, each line in plain words with a small worked example (ILLUSTRATIVE numbers, labelled), how the consumption engine turns it into wheel power, and which VECTO lines each piece stands in for. Explain from scratch; define every term.

---

## 5. Deliverables

1. `docs/research/force-engine-review-2026-11.md`, in this order:
   - **Summary first (one page):** what is right, what is wrong, a ranked list of proposed changes (each with measured effect in kWh and %, source tag, engine or parser, VECTO / standard / HDEV assumption), and open items.
   - Gates 1–3.
   - Part A audit table + Q1–Q10 answers.
   - Parts B–E results (tables first; graphs under `docs/research/force-engine-review-2026-11/`).
   - Parts F, G, H tables.
   - **Proposed changes:** before/after snippet against Appendix 1, why (source tag), measured effect, engine or parser, and whether it only swaps one assumption for another.
   - **Deviation register:** every HDEV-vs-VECTO difference in wheel power, its size on E2 Regional/Urban, and the exact sentence to use in a client report.
   - **Parser jobs found** (new checks, lookups and inputs the parser must provide).
   - "Seen in passing (out of scope)", "Choices I made", "Bob to fetch", and the `BLOCKED` list.
2. `docs/research/force-engine-review-2026-11/`: `_load_notebook.py`, `reference_copy.py` with variants, one runnable script per part (`python run_part_c.py` etc.), all CSVs and graphs. Each script prints the files it wrote.
3. `tests/force_engine/`: Part B tests, runnable with `pytest`.
4. `reference/vecto/jobs/force-engine-2026-11/` (Part I, only if needed).
5. `docs/explainers/force-engine-explained.md` (Part K).
6. One PR to `main`. The description lists: what was done, how to run every script and the tests, the top 5 findings with numbers, every value with `NO SOURCE`, every `BLOCKED` item, and the "Bob to fetch" list.

## 6. Stop conditions
- If a test shows Bob's code crashes or gives a wrong number on a realistic input, report it as **BUG** with a minimal reproducing input, and keep going.
- Never edit the notebook or `src/`. Never decide an open design choice for Bob.

---

## Appendix 1: code of record (Bob's notebook, 12 Nov 2026; verbatim; load it from the notebook, do not retype it)

### 1.1 `force_engine` (notebook cell 8)
```python
##4 FORCE ENGINE
## takes in rows from the driver model and calculates the force coeff per row independent of mass and temp and CdxA_eff
def force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red):

  speed = np.asarray(speed, dtype=float) # speed at start of the step
  accel = np.asarray(accel, dtype=float) # acceleration of the vehicle
  dt_s = np.asarray(dt_s, dtype=float)  # time step, s
  grade = np.asarray(grade, dtype=float) # gradient

  grade = np.arctan(grade / 100) # turns gradient in % into an angle in radians
  v1 = speed
  #v2 = speed + accel * dt_s
  v2 = np.maximum(speed + accel * dt_s, 0.0) # speed cannot go below 0, as in the driver model
  v_avg = (v1 + v2)/2  #speed in m/s

  #K = ((Crr * g * np.cos(grade)) + (g * np.sin(grade)) + accel) * v_avg
  # the K equation is the same with the added term of rotational force, if theta red and rdyn are 0 we get back the simple equation.
  k_lin = (g * np.sin(grade) + accel) * v_avg
  k_roll = Crr * g * np.cos(grade) * v_avg
  k_rot = (theta_red / r_dyn**2) * accel * v_avg if theta_red > 0 else np.zeros_like(v_avg) # no rotating mass unless given
  L = (v1 + v2) * (v1**2 + v2**2) / 8 # exact average of 0.5*v^3 over the step as VECTO CrosswindCorrectionCdxALookup

  return k_lin, k_roll, k_rot, L, v_avg # we are taking out v_avg so we can use it to look up CdxA
```

### 1.2 `consumption_engine` (notebook cell 16): **only steps 1–4 are in scope**
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

  # ... steps 5-7 (drivetrain, aux/PTO, battery) are OUT OF SCOPE for this job ...
```
Note: `cdxa_v` here is in km/h (the CdxA grid), while the driver now takes its CdxA grid in m/s (decided 10 Nov). Report this as a parser item.

### 1.3 Driver force model, for Part D (from notebook cell 4 `driver_model` and cell 7 `coast_distance`)
```python
  def coast_acc(v, k):
      th = math.atan(gr_l[k] / 100)
      F = (rho / 2 * interp1(v, cv, cc) * v * v        # air drag, instantaneous (HDEV: VECTO uses the step average)
           + coast_mass**beta * g * Crr * math.cos(th)       # rolling resistance, mass without wheel inertia like VECTO
           + coast_mass * g * math.sin(th)             # slope force
           + interp1(v, drag_v, drag_F) )      # motor/gearbox drag while rolling
      return -F / m_eff         # m_eff = coast_mass + m_red_wheels

# coast_distance (cell 7):
  m_eff = coast_mass + m_red_wheels
  dE = m_eff * g * (h_now - h_target) + m_eff * (v**2 - v_target**2) / 2
  v_avg = (v + v_target) / 2
  cda = interp1(v_avg, cdxa_v, cdxa)
  F_air = rho / 8 * cda * (v + v_target) * (v**2 + v_target**2) / v_avg
  grad = (h_target - h_now) / (s_target - s_now)       # no atan: VECTO uses cos(rise/run) [DECIDED 3 Nov]
  F_roll = math.cos(grad) * coast_mass**beta * g * Crr
  F_loss = interp1(v, drag_v, drag_F)
```
Also note: `dE` in `coast_distance` uses `m_eff` (incl. wheel inertia) for the potential-energy term `m·g·Δh`. Check against VECTO `ComputeCoastingDistance` whether that mass is right (Q1/Q4); report only.
