# HDEV master plan — requirements

**Spec type:** planning only. No `src/` code is written or changed by this spec. No tasks are run. Bob writes all the code; Kiro plans, explains, reviews, and (only when asked) writes tests. (`working-style.md`.)

**Scope and grounding:** VECTO Declaration Mode, heavy/medium lorries, BEV. Every physics value or formula must cite a file and must never be invented. Source order and allowed deviations are governed by `vecto-grounding.md`. The regulation markdown extracts are still **missing** from `reference/regulation/`; any requirement that needs one names the file and marks it missing. (`vecto-grounding.md`, `status.md`.)

**Status tags on every requirement:**
- **Decided** — stated in a cited doc; implement as written.
- **Open** — needs Bob's decision before it can be built.
- **Suggestion** — Kiro's proposal; Bob decides.

The goal of the whole plan: take HDEV from today's state to (1) a correct engine (consumption → battery → charging) and (2) a step-by-step local UI talking to a small local Python server, designed so FastAPI can replace the server later with the **same JSON** (`tech.md`, `product.md`).

---

## 1. Engine correctness

### 1.1 Driver-model audit fixes
The audit list is `docs/design/status-and-known-contradictions.md` §3 (and `2026-10-08_session-closeout-payload-force.md` §6, `status.md`). Each item below is one requirement.

**User story:** As the engine author, I want the driver model to produce physically consistent 1 s rows so that every downstream step (force, weather, power, consumption) is fed correct speed/accel/grade/payload.

Acceptance criteria — the fixed `DriverModel.driver_model(vacc, dt_s=1.0)` must:

1. **(Decided — red)** Not be able to enter an infinite loop on any VDRI/typed/GPS waypoint list. Done-when: a bounded-iteration test over all five VECTO truck `.vdri` cycles terminates. Source: §3.
2. **(Decided — red)** Resolve the segment-level vs step-level acceleration inconsistency: acceleration used to advance a step must be the acceleration stored on that step's row. Done-when: for every row, re-deriving `a` from `(v2−v1)/dt` matches the stored `accel` within tolerance, except the two documented clamp cases (criteria 7, 8). Source: §3.
3. **(Decided — orange)** Never divide by zero in `get_breaking_distance`. Done-when: unit test with `v0==v1` and with zero deceleration raises a clear error or returns a defined value, not `inf`/`nan`. Source: §3.
4. **(Decided — orange)** `vacc_lookup` never silently returns `None`; out-of-range speed raises a loud error (no silent default inside an engine — `engine-rules.md` §6). Done-when: lookup of a speed outside the `.vacc` range raises. Source: §3.
5. **(Decided — yellow)** Add the missing early exit and remove the dead logic in braking distance. Done-when: code review confirms no unreachable branch; behaviour unchanged on the reference cycle. Source: §3.
6. **(Decided — Bob, this session: fix now)** On arrival the model sets `speed = target_speed` and drops the overshoot `ds` — a speed jump with no matching accel. Fix it in M0. Done-when: energy on the reference cycle changes by a documented, bounded amount and the chosen rule (carry `ds` into the next step, or sub-step to the waypoint) is recorded. Source: §3, payload-force §6; Bob's decision.
7. **(Decided)** When the new speed is clamped to 0, the row must not store an acceleration inconsistent with the clamp in a way the force engine cannot compensate. Current behaviour: driver stores unclamped accel, force engine clamps `v2` (`2026-10-08_session-closeout-payload-force.md` §4). Done-when: the documented clamp interaction is preserved and asserted by a test. Source: §3, payload-force §4.
8. **(Decided — Bob, this session: fix now)** A waypoint with `stop == 0` but `target_speed == 0` currently brakes to 0 and pulls away (a momentary stop). Fix/define it in M0. Done-when: rule recorded; test asserts it. Source: §3; Bob's decision.
9. **(Decided)** Add `'payload'` to every emitted row (driving rows `current.payload`, stopped rows `target.payload`, first-waypoint stop loop `waypoints[0].payload`), fed by `fill_payload` output. Done-when: no row lacks a numeric payload; integrates with H. Source: §3, payload-force §2, payload-stop-rows-then-fill.
10. **(Decided — Bob, this session: record as flagged gap, defer)** PTO stop time for MunicipalUtility is missing: real stop = file `StoppingTime` + PTO cycle `Duration` (declaration `MunicipalUtility_PTO_generic.vptoc` → Duration 23 s; 2 s file stop → 25 s per stop; 96 stops ≈ +36.8 min). Affects **time** (charging) and PTO energy, not driving energy or payload placement. **Not fixed in M0**; recorded as a flagged gap for later. Done-when: the gap is listed in the assumptions report and `status.md`'s known-gaps intent, not implemented. Source: §3, payload-force §3; Bob's decision.
11. **(Decided — Bob, this session: record as flagged gap, defer)** Power limit at high mass (VECTO can limit acceleration for a heavy vehicle) is not modelled; the driver model is payload-blind. **Not modelled in M0**; recorded as a flagged gap for later (needs `Driver.cs`/`DefaultDriverStrategy.cs` review — both present in `reference/vecto/cs/`). Done-when: the gap is listed in the assumptions report / known gaps, not implemented. Source: §3, payload-force §2/§6; Bob's decision.
12. **(Open — CONFIRMED by research, still needs Bob's decision)** Grade: the model uses the segment's flat `grade_pct`; VECTO uses an **altitude secant per step**, now **verified in the clone**: at load the `<grad>` column is integrated into an altitude profile (`DrivingCycleDataReader.cs:236`), then each step uses `grade = atan((altitude(prev+ds) − altitude(prev))/ds)` with altitude interpolated between the bracketing sample points (`DistanceBasedDrivingCycle.cs:412-433`, exceptions only when `ds==0` or left==right distance). That secant grade feeds `Vehicle.SlopeResistance`/`RollingResistance`. **This corrects research file `08`, which wrongly said "`<grad>` used directly, no secant needed" — see `docs/research/vecto/13-followups.md` §1.** M0.12 is **NOT resolved**. Decide whether to match VECTO's altitude-secant grade now. Done-when: either grade matches VECTO's secant derivation on a reference cycle, or the difference is recorded as a flagged gap. Needs Bob's decision. Source: §3; `13-followups.md` §1.
13. **(Open)** The model should use VECTO's official `Truck.vacc` (`reference/vecto/resources/VACC/Truck.vacc`). Done-when: the reference run uses `Truck.vacc` and the loader is tested. Needs Bob to confirm this replaces his current `.vacc`. Source: §3.

> **Note (Decided, `vecto-grounding.md` working-style):** the audit must **never rename Bob's existing variables** and must keep his comment style. Kiro proposes diffs; Bob applies them.

### 1.2 P_aux
**User story:** As the engine author, I want a pure `p_aux` function that reproduces VECTO's five BEV auxiliary terms so that consumption includes auxiliaries exactly as VECTO does.

VECTO formula (`2026-10-08_session-closeout-paux.md` §0): `P_aux(t) = P_ES + P_HVAC + P_PS + P_SP·[moving] + P_cond·[motor_on]`, all electric, drawn from the battery, DC/DC efficiency = 1.0.

Acceptance criteria:
1. **(Decided)** `p_aux` takes every value as an argument (ES, HVAC, PS, SP, Cond constants) plus per-row state flags `moving` and `motor_on`; nothing hard-coded (`engine-rules.md` §1). Done-when: signature review + a test with hand values.
2. **(Decided)** The four declared aux (ES, HVAC, PS, SP) + Conditioning = five terms; SP is 0 while stopped (`VehicleStopped`), Cond is on only while an electric motor is on. Done-when: tests assert the three states in paux §5 (moving/motor-on, stopped/motor-on, stopped/motor-off) reproduce 2938.9 / 2537 / 1937 W for the illustrative Group 5 RD config. Source: paux §2.2–2.4, §5.
3. **(Decided)** Values come from `defaults.py`, each labelled VECTO, with the per-mission/group tables transcribed from the paux doc (ES ×0.7, HVAC ×1.25, PS `_el` read directly, SP per-axle calc ×0.7, Cond direct). Done-when: the default tables match paux §4 and `ES-Tech.csv`, `HVAC-Table.csv`, `PS-Table.csv`, `SP-Table.csv`/`SP-Axles.csv`/`SP-Tech.csv`, `Cond-Table.csv` under `reference/vecto/resources/VAUX/`. Source: paux §4, defaults doc.
4. **(Decided)** Blank or `"---"` table cells raise a lookup error (no extrapolation; `engine-rules.md` §6). Done-when: a lookup of a blank cell (e.g. ES medium-lorry MU) raises. Source: paux §6.
5. **(Decided — Bob, this session)** `EmOffPrev` / `motor_on`: the rule for when a BEV motor counts as "off" (so the Conditioning term drops) is **defined during the driver-model audit** (M0.16), since the driver model emits the `motor_on` flag. Done-when: the audit records the rule and the Cond term toggles on it. Source: paux §2.4, §9(1); Bob's decision.
6. **(Decided — Bob, this session)** Default BEV technologies (ES, HVAC, PS, SP) are **flagged HDEV defaults labelled HDEV ASSUMPTION** in `defaults.py` (user can override). Blank/`"---"` table cells **mirror VECTO: raise a lookup error** (not a user-filled value). Done-when: the default technologies carry the HDEV ASSUMPTION label and a blank-cell lookup raises. Source: paux §6/§10; Bob's decision.
7. **(Open — Suggestion)** Function structure: precompute the constant part per vehicle × mission once, apply SP and Cond via per-row flags. Kiro's suggestion from paux §10; Bob decides.
8. **(Open)** Whether HDEV adds non-VECTO extras (DC/DC loss, cabin heating for Danish winter, charging-time aux) as **optional, flagged** layers with neutral defaults and an authentic non-VECTO source. These are listed as gaps, not deviations (`vecto-grounding.md`). Needs Bob's decision; no numbers until a source exists. Source: paux §7, §10.

### 1.3 weather_for_rows (step W)
**User story:** As the engine author, I want `weather_for_rows` to attach ρ and effective drag area to every 1 s row so the power step can run with no Python loop.

Signature (Decided): `weather_for_rows(rows, departure_time, temps_by_hour, winds_by_hour, cdxa_table) → rho_rows, cdxa_rows` (`year-and-day-simulation-problem.md` §2).

Acceptance criteria:
1. **(Decided)** ρ computed inline as `ρ = P/(R·T)`, T in K, P and R passed as arguments (P fixed = Assumption, in `defaults.py`). Done-when: a unit test matches a hand-computed ρ. Source: 6 Oct §4.
2. **(Decided)** CdxA_eff looked up from the crosswind table by (wind, vehicle speed); the speed clamp **60–105 km/h** lives here (below 60 uses the 60 value; linear interpolation within range; **raise on extrapolation**). Done-when: a test asserts the clamp, interpolation, and an extrapolation error. Source: payload-force §5, crosswind-verification, `engine-rules.md` §6.
3. **(Decided)** CdxA_eff per row = `CdxA(0)·W1 + W2` using the step-F tables. Done-when: a row with the VECTO declaration wind reproduces the verified crosswind case. Source: crosswind §7, `crosswind_engine.py`.
4. **(Decided)** Daily and hourly use the same function, different data (daily = fill 24 h with the day's mean). Start with daily (option A). Done-when: daily and option-C paths call the same function. Source: 6 Oct §4, year/day §2.
5. **(Open)** `DeltaAirDragAreaIMC` (extra ΔCdxA in VECTO's lookup) — meaning unknown; argument with default 0 until grounded (maybe `reference/vecto/resources/IMC-Tech.csv`). Needs Bob to confirm whether to ground it now. Source: payload-force §5.
6. **(Decided)** Pure function: no network, no disk, no globals (`engine-rules.md` §7). Done-when: review.

### 1.4 power_step (step J)
**User story:** As the engine author, I want a single `power_step` function that computes wheel power per row from the force coefficients, mass, ρ and CdxA_eff.

Equation (Decided, `2026-10-08_session-closeout-payload-force.md` §4, structure.md): `P_wheel = m·k_lin + m^β·k_roll + k_rot + ρ·CdxA_eff·L`.

Acceptance criteria:
1. **(Decided)** Vectorised multiply-add over numpy column arrays; no Python loop. Done-when: runs on array inputs and matches a loop reference. Source: 6 Oct §5, tech.md.
2. **(Decided)** With `β = 1`, `θ_red = 0`, single Crr the result equals the old simple-K `P_wheel` (strict superset). Done-when: a property test asserts neutral defaults reproduce the simple equation (force engine already satisfies this for its coefficients). Source: `engine-rules.md` §3, payload-force §4.
3. **(Decided)** `m = vehicle + body/trailer + payload`, payload capped per GVWR/40 t/60 t EMS (SR7 §4.3.5.4). Done-when: mass assembly cites `SegmentTable.csv`/`Body_Trailers_Weights.csv`; cap test. Source: defaults doc.
4. **(Decided — naming)** The function is named `power_step` (6 Oct notes called this "force_engine"; Bob's `force_engine` is step I = coefficients). Done-when: the name does not collide with `force_engine.py`. Source: contradiction §4(2).
5. **(Decided)** `L` is taken from the force engine (`L = (v1+v2)(v1²+v2²)/8`), not `0.5·v_avg³`. Done-when: matches `force_engine.py` output. Source: payload-force §4.

### 1.5 consumption
**User story:** As the engine author, I want a consumption step that turns per-row wheel power into battery kWh using sign-dependent efficiency plus P_aux.

Rule (Decided): `P_wheel > 0 → P_wheel/η`; `P_wheel < 0 → P_wheel·η_regen`; add P_aux; integrate over `dt` → kWh (6 Oct §3).

Acceptance criteria:
1. **(Decided)** Vectorised `np.where(P>0, P/η, P·η_regen)` + P_aux, summed. Done-when: matches a loop reference on the reference cycle. Source: 6 Oct §3, tech.md.
2. **(Decided)** η, η_regen, P_aux are arguments; efficiencies default to the **placeholder** 0.95/0.95/0.98 **labelled a model gap, not a VECTO value** (`vecto-grounding.md`, §5). Fix the `regen_effeiciency` spelling noted in the docs when the real code arrives. Done-when: review + a note in the assumptions output. Source: §2 consumption row, §5.
3. **(Open)** The consumption code exists in Bob's notebook but is **not in the bundle**. Kiro must not plan around unseen code; Bob pastes it (or confirms a clean rewrite) before M0 consumption tasks start. Needs Bob. Source: §6.
4. **(Decided — gaps to flag, not fix)** No motor/inverter/gearbox efficiency map, no battery internal-resistance loss while driving, no regen power cap — all flagged in the report, not invented. The efficiency gap wording is now fixed (research): the **0.95 motor / 0.95 inverter / 0.98 gearbox** placeholders have **no VECTO equivalent** — VECTO uses a **speed×torque → electrical-power map** for the electric machine (inverter folded in), not scalar efficiencies; VECTO's only EM-side scalars are the 0.98 efficiency-clamp fallback and the 0.98/0.96 ADC factors (`01-electric-machine.md` §2/§7, `13-followups.md` §5). The report must say "HDEV placeholder with no VECTO equivalent; VECTO uses a speed×torque electrical-power map". It stays a gap; adopting the map is a decision for Bob. Done-when: the assumptions report lists them with this wording. Source: §5, `vecto-grounding.md`, `13-followups.md` §5, `01-electric-machine.md`.

---

## 2. Data contracts

**User story:** As the engine author, I want every pipeline step's inputs and outputs pinned down (column names, units, shapes) and the project-JSON sections defined, so steps compose without guesswork and the FastAPI swap touches only transport.

Acceptance criteria:
1. **(Decided)** SI units inside every engine (m, m/s, s, kg, W, m², K); km/h and tonnes only at the UI boundary, converted once (`engine-rules.md` §5). Done-when: the design.md per-step contract table states units for every field.
2. **(Decided)** Each step's exact inputs/outputs are the ones already written in `structure.md` ("What each written step takes in and returns") for F, H, I, M, extended to P_aux, W, J, consumption using the cited docs. Done-when: design.md contract table covers F, H, I, G, W, J, P_aux, consumption, L, M with column name + unit + shape. Source: structure.md, this file §1.
3. **(Decided)** Project JSON = one object with sections `vehicles`, `routes`, `assignments` (with `count`), `calendar/environment`; equipment data (vehicles, chargers) kept separate from operational data (routes, calendar). Done-when: design.md documents each section's fields and the separation. Source: tech.md, input-layer-and-json.md, product.md implications 1–2.
4. **(Decided)** The user's original project JSON is never overwritten; a scenario = base + a small change-set. Done-when: design.md shows the base+change-set shape. Source: tech.md, product.md implication 1.
5. **(Inferred → Suggestion)** Each input value carries **source + date** metadata, not just a value. The docs call this "Inferred (business doc)" and note no schema reflects it yet. Done-when: design.md defines a `{value, source, date, label}` field shape as a **design hook** (not a built feature). Needs Bob to accept the shape. Source: tech.md ("Inferred"), product.md implications 3/7.
6. **(Decided)** "Skip a step" (user-supplied kWh/km) is a resolver override that bypasses F–J and is flagged in the assumptions list. Done-when: design.md shows where the override enters. Source: tech.md, input-layer-and-json.md.

---

## 3. Year/day/week simulation

**User story:** As the analyst, I want day → week → year simulation that produces correct annual kWh, a correct worst day for sizing, correct charging across days/weekends with SOC carry-over, and a **day-to-day distribution of daily results across the real weather year** — without precomputing every hour of every year.

> **(Decided — Bob, this session) Two different spreads, kept separate and never conflated:**
> - **Weather spread** = the distribution of daily results over the real operating dates of a weather year (natural day-to-day variation). Report it as *daily-result percentiles across the weather year* (e.g. "90th-percentile day"), **not** as "P10/P90 of the result".
> - **Monte Carlo input uncertainty** = JCGM 101:2008 ranges from perturbing uncertain inputs (payload, coincidence). Those are the P10/P50/P90 **of the result**.
> The two must never be labelled with the same term. Source: year/day §2, §4(4); Bob's decision.

This is the hardest, least-settled area. Full requirement detail and the three candidate options live in `design.md` Part 3 (per the task). Requirements here:

1. **(Decided)** Compute each quantity at the frequency it changes (crosswind once per vehicle; 1 s rows once per route/day-type; ρ inline per row; CdxA_eff per row; P_wheel/battery per (day-type × weather × mass)). Done-when: design matches the table in year/day §2.
2. **(Decided)** kWh cannot be scaled by a single factor: a mass/ρ change can flip a row regen↔pushing and switch the efficiency formula, so mass and ρ enter each row **before** the efficiency step. Done-when: design preserves this. Source: year/day §2, 6 Oct §3.
3. **(Decided)** Do **not** average the same calendar date across years; keep each real year's daily T/wind series paired by date; keep the worst day as its own sizing case. Done-when: the data_fetch design keeps per-year daily series (fixes the DRAFT DMI code which currently averages across years). Source: year/day §2, contradiction §4(9).
4. **(Decided)** Charging is per **plug-in session** (arrival → next departure), not per calendar day; the current fixed 21 h episode and randomised `reset()` are known limitations to remove. Done-when: design states the session boundary and removes the 21 h cap. Source: year/day §3, 6 Oct §9.
5. **(Decided — Bob, this session)** Daily vs hourly weather: **start daily (A)**; decide **B vs C after the timing comparison** (§3.6a), not before. Done-when: the daily path is built first; B vs C is deferred to the timing result. Source: year/day §2; Bob's decision.
6. **(Decided — Bob, this session)** Day → week → year structure: **Option 1 (compute every operating date directly)**. Option 3 (hybrid) is kept **only as a fallback if the timing task fails**. Done-when: the calendar/annual path computes every operating date directly; Option 3 is not built unless timing forces it. Source: year/day §4(1)/§5; design §3E; Bob's decision.
6a. **(Decided — Bob, this session) Timing gate first.** Before anything else in M2, a timing task measures **one year of consumption per date** and **one year of charging** (and, per §4.3, the year at a coarse and a fine charging step). Option 1 proceeds only if these are fast enough; otherwise fall back to Option 3. Done-when: both timings are reported before M2 structure code is written. Source: year/day §5; Bob's decision.
7. **(Open)** Consumption-days → charging-weeks hand-over (energy per session, arrival SOC) is not designed. Design proposes it; Bob confirms. Source: year/day §4(3).
8. **(Open)** Monte Carlo placement on top of the year/day structure, and departure clock time (option C needs it; routes/calendar don't carry it yet). Needs Bob's decision. Source: year/day §4(4), §4(5).
9. **(Decided)** No invented numbers: any bin count, step size or threshold is labelled a choice/assumption or sourced. Done-when: design has no bare numbers. Source: year/day §6.
10. **(Decided)** The VECTO-equivalent case (one cycle, declaration wind 3 m/s at 4 m, constant reference payload) stays exactly reproducible under whatever structure is chosen. Done-when: validation (§7) still passes. Source: year/day §6.
11. **(Decided — resolve §4 contradictions)** Each of the five inconsistencies in year/day §4 is either resolved in design.md or explicitly listed as Open with options. Done-when: design.md §(resolution table) addresses §4(1)–(5).

---

## 4. Battery sizing and charging

**User story:** As the analyst, I want battery sizing (modes A and B) and depot charging (plug-in sessions, ASAP/JIT, EDF/ES, OCV+Ri) so I can size packs and chargers and read site peak.

### 4.1 Battery sizing
1. **(Decided)** Mode A = real vehicle: datasheet mass + kWh, no loop. Done-when: a mode-A run uses the datasheet values directly. Source: 6 Oct §8.
2. **(Decided)** Mode B = size it: glider mass + (kWh ÷ pack kWh/kg) + payload, iterate until the size stops changing (because energy is only piecewise-linear in mass). Max GVW is a legal check, not the mass. Done-when: mode B converges on the reference case; the GVW check is a separate assertion. Source: 6 Oct §3/§8.
3. **(Open)** Sources for glider mass and pack energy density (kWh/kg) are **still needed**; no numbers until sourced. Needs Bob/source. Source: 6 Oct §8.

### 4.2 Charging
1. **(Decided)** Simulate per plug-in session; the env stops at departure or when need is met; JIT/EDF use real departure times. Done-when: a two-session run (overnight) is not cut by a fixed horizon. Source: 6 Oct §9, year/day §3.
2. **(Decided)** JIT and ASAP site setpoints + import/export feasibility (flexibility headroom) from `flexibility_setpoints.py`; EDF and equal-share (ES, water-filling) split of the site target from `allocators_edf_es.py`, kept as **pure functions of env state** (no env mutation). Done-when: existing functions reused; purity test. Source: structure.md, `engine-rules.md` §7, allocators header.
3. **(Decided)** Replace the exponential CC-CV taper (`src/deprecated/charging_physics_engine_exponential.py`) with a VECTO **OCV + internal-resistance (Ri)** battery model. Done-when: the new physics matches `Battery.cs` behaviour on a charge curve test. Needs `Battery.cs` (present in `reference/vecto/cs/`). Source: status.md, structure.md.
4. **(Decided)** Site cap couples vehicles (depot); order battery → charger power → policy → site peak; sweep over finite real option lists, skipping impossible combinations. Done-when: a sweep over a small option grid returns site peak per combination. Source: 6 Oct §9.
5. **(Open)** Cheapest-first policy needs an hourly price series (Energidataservice spot + tariffs) — not written; external, versioned, dated data file. Needs Bob/data. Source: 6 Oct §9, year/day §3, product.md implication 8.
6. **(Open)** SOC carry-over across sessions/weeks and the "two weeks, keep the second" idea are a **Suggestion** (Claude, 6 Oct, not sourced); bin/representative-week structure depends on Part 3. Needs Bob's decision. Source: year/day §3.
7. **(Decided — gap)** No aux power during depot charging in VECTO (Open for the charging engine); flag it. Source: paux §7.

### 4.3 Charging time resolution (Decided — Bob, this session)
**User story:** As the analyst, I want the charging time step to be an argument so I can run finer resolution for ancillary-service products later without touching the engine.

1. **(Decided)** The charging time step `dt` is an **argument** of the charging env/runner, **not fixed at 5 min**. Done-when: `dt` is passed in; nothing in the charging code hard-codes 5 min / 300 s. Source: Bob's decision.
2. **(Decided)** The design must state how a finer `dt` affects the year loop, and evaluate **one option: a base step for the full year, with a finer step only inside activation/event windows** (two-resolution charging). Done-when: design.md §3G covers it. Source: Bob's decision.
3. **(Decided — no invented numbers)** Product resolutions (how fine, which windows) are **not invented**: they are labelled **"from Energinet product specs, to be sourced"** until a source is added. Done-when: no bare resolution number appears; each is marked to-be-sourced. Source: Bob's decision, `vecto-grounding.md` no-invented-numbers rule.
4. **(Decided)** The timing task (§3.6a / design §3F) times **one year of charging at a coarse step and at a fine step**, so the cost of fine resolution over a full year is known before committing. Done-when: both timings reported. Source: Bob's decision.

---

## 5. defaults.py and the assumptions report

**User story:** As the author and the auditor, I want every default in one Python file with a source + label, and an assumptions report that lists every default used and a source + date on every input, so results are reproducible and tender-neutral.

1. **(Decided)** `defaults.py` is the **only** place defaults live — never in JavaScript, never as Pydantic/schema field defaults. Done-when: no default appears outside `defaults.py`. Source: tech.md, `engine-rules.md` §2, input-layer-and-json.md.
2. **(Decided)** Every default carries a **source** or an **ASSUMPTION** label from the fixed vocabulary: **VECTO / REG / literature / HDEV ASSUMPTION**. Done-when: every entry has a label; a test asserts the label set. Source: `engine-rules.md` §2, `vecto-grounding.md`.
3. **(Decided)** The values are the ones collected in `2026-10-07_vecto-declaration-defaults.md` and the paux tables: payloads, reference heights, crosswind coefficient sets, CdxA defaults, body/trailer masses, `Truck.vacc`, design speed 85 km/h, aux tables. Done-when: `defaults.py` transcribes those with per-value file citations. Source: defaults doc, paux §4.
4. **(Decided)** Neutral VECTO parameters default to the simpler equation (`β = 1`, `θ_red = 0`, single Crr), with the VECTO value (`β = 0.9` etc.) cited separately. Done-when: review. Source: `engine-rules.md` §3, payload-force §4.
5. **(Decided)** The assumptions report lists, for every run: every default used (with source + label), every non-VECTO deviation actually applied (10° yaw clamp, in-cycle payload variation, real DMI wind, edited-VDRI user route), and every flagged model gap. Done-when: a reference run's report lists all four deviations and the §5 gaps. Source: `vecto-grounding.md` deviations table + gaps, status.md §5.
6. **(Suggestion)** Each **input** (not just defaults) carries source + date metadata so the report can show provenance per field. Design hook only (see §2.5). Needs Bob. Source: product.md implications 3/7 (Inferred).
7. **(Open)** CdxA default values ("standard values for vehicles without a measured air-drag certificate", Annex VIII Appendix 7) are marked "to verify before use"; the regulation extract is **missing**. Needs the Annex VIII file or Bob's confirmation. Source: defaults doc, `vecto-grounding.md`.

---

## 6. Local server + step-by-step UI

**User story:** As Bob (local user), I want a small local Python server and a step-by-step dumb-form UI that posts the project JSON and shows results, built so FastAPI can later replace the server with the same JSON and no engine change.

1. **(Decided)** Transport now = a small local Python server: UI posts the project JSON, server returns results JSON. FastAPI replaces it later with the **same JSON**; the swap touches **only the transport layer, never the engine**. Done-when: the server is a thin adapter calling the engine; design.md shows the seam. Source: tech.md, product.md.
2. **(Decided)** The UI is a **dumb form**: it collects inputs and sends raw JSON; **no maths or resolver logic in JavaScript**. Filtering rows for display (e.g. show only `stop > 0`) is allowed. Done-when: review confirms no computation in JS. Source: input-layer-and-json.md, year/day §6.
3. **(Decided)** Step-by-step pages map one-to-one to JSON sections; basic fields up front, an "Advanced" toggle, pre-filled defaults shown in orange/terracotta. Done-when: pages correspond to `vehicles`/`routes`/`assignments`/`calendar` sections. Source: input-layer-and-json.md.
4. **(Decided)** The payload stop table shows only `stop > 0` rows (distance, stop duration, payload); edits write straight back into the waypoint rows; editable columns depend on source (VDRI: payload+stop; GPS: payload; typed: everything). Done-when: review against payload-stop-rows-then-fill rules. Source: payload design, input-layer-and-json.md.
5. **(Decided — Bob, this session)** UI state lives in a **server-saved `projects/<id>.json`**, kept **behind the thin transport layer** (so the FastAPI swap keeps the same store contract). The engine never reads it; only the transport/orchestration layer does. Done-when: the server reads/writes `projects/<id>.json` and the engine stays stateless. Source: input-layer-and-json.md, status.md; Bob's decision.
6. **(Decided)** The four route inputs (VDRI, typed, GPS, AI-later) all end as a waypoint list; `resolve` is written **last**, its field list taken from what the engines read. Done-when: resolver fields are derived from the engine signatures. Source: input-layer-and-json.md, tech.md.
7. **(Open — context)** How the existing static dashboard prototype relates to the step-by-step input UI once a local server exists. Needs Bob's decision. Source: contradiction §4(6), product.md.

---

## 7. Validation: reproduce the VECTO-equivalent case exactly

**User story:** As the auditor, I want the pipeline to reproduce a VECTO-equivalent case exactly so HDEV stays VECTO-auditable.

1. **(Decided)** With VECTO declaration inputs — one mission cycle, declaration wind **3 m/s at 4 m**, constant VECTO reference payload, neutral `β=1`/`θ_red=0`, VECTO aux defaults — the pipeline reproduces the VECTO-equivalent result; passing the VECTO values must reproduce the auditable case exactly. Done-when: a reference run matches the target within a stated tolerance (crosswind already verified to 0.006 %). Source: `vecto-grounding.md` deviations, crosswind-verification, year/day §6.
2. **(Decided)** The crosswind engine stays verified vs the VECTO Excel (0.006 %). Done-when: the existing verification test still passes. Source: crosswind-verification, status.md.
3. **(Open — task defined for Bob)** A full end-to-end VECTO consumption reference number to compare against (beyond crosswind) requires a VECTO run output; VECTO **could not be built in the sandbox** (NuGet restore blocked, `11-validation-data.md` §3). **Bob runs it off-sandbox** (official VECTO release) on `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BEV_E2.vecto` and brings back per-mission `kWh/km` (+ `kWh/(t·km)`), `REESS_StartSoC`/`EndSoC`, and `E_REESS_LOSS` from the `.vsum` (and `.vmod` SoC/`P_REESS_T`/`U_0_REESS`/`I_REESS` for a row-level check). Component-level anchors (battery SoC-step, usable energy, overload loss; EM-map torque) are usable **now** from the shipped `GenericBattery.vbat`/`GenericEMotor.vem` (`11` §2). The consumption code is still not in the bundle. Source: §5, §6, `vecto-grounding.md`, `11-validation-data.md`, `13-followups.md` §4.
4. **(Decided)** Every non-VECTO deviation used in a validation run is listed in that run's assumptions report (yaw clamp etc.). Done-when: §5.5 report check passes for the reference run. Source: `vecto-grounding.md`.

---

## Self-check: "analyze requirements" — ambiguities and gaps

Kiro's own review of the requirements above, per the task. These are the things that will block or wobble implementation.

### A. Missing inputs (code/files not in the bundle — can't plan around them; `working-style.md`)
1. **Consumption step** code is not in the bundle (§6, consumption §1.5.3). M0's consumption tasks cannot be finalised until Bob pastes it or confirms a clean rewrite.
2. **Waypoint / vacc data structures and parser** feeding `DriverModel` are not in the bundle. The driver-model audit (1.1) and the `'payload'` hook-in need them.
3. **Sept typed-input resolver** (`TableLeg`, `ResolvedDay`, `resolve()`) + HTML harness not in the bundle; §6 resolver tasks depend on it.
4. **Dashboard HTML prototype** not in the bundle; §6.7 depends on it.
5. **Colab VDRI analysis script** not in the bundle.
6. **Regulation extracts missing** entirely: Annex Xb electric-machine map (efficiencies), Annex VIII air-drag standard values (CdxA defaults). §1.5.4, §5.7, §7.3 are blocked on these; `vecto-grounding.md` says name the file and stop, do not guess.

### B. Decisions that gate design — now resolved (Bob, this session)
7. **Resolved.** Day/week/year structure = **Option 1** (every operating date directly), Option 3 fallback only if the **timing gate** (§3.6a, runs first) fails. Daily-vs-hourly = start **daily (A)**, decide **B vs C after the timing**. Weather spread and Monte Carlo result uncertainty are kept **separate** and never share the "P10/P90" label (§3 user story). The charging hand-over (§3.7) and departure clock time (§3.8) follow from Option 1 and stay as noted.
8. **Resolved.** P_aux `motor_on`/`EmOffPrev` rule is **defined during the driver-model audit** (M0.16), since the driver model emits the flag — decided once, used by both §1.1 and §1.2.
9. **Resolved.** UI state = **server-saved `projects/<id>.json` behind the thin transport layer**; the engine stays stateless, so the FastAPI seam (§6.1) is unaffected.
10. **New (Decided).** Charging `dt` is an argument (§4.3); the finer-step-in-windows option is designed (design §3G) and added to the timing gate (coarse vs fine over a full year). Product resolutions are "to be sourced from Energinet product specs", not invented.

### C. Internal ambiguities / naming traps
11. **Pipeline order contradiction**: 6 Oct put driver (G) before payload (H); 8 Oct runs payload on waypoints **before** the driver model. The 8 Oct order is the Decided one (`structure.md`); design.md must state this once and not reopen it. Source: contradiction §4(1).
12. **Function-name collision**: Bob's `force_engine` = step I (coefficients); the step-J multiply-add must be named `power_step`, not "force_engine". design.md must use `power_step` consistently. Source: §1.4.4, contradiction §4(2).
13. **Row storage**: steps are specified on numpy-arrays-per-column, but the driver model still returns a list of dicts. The conversion point (where list-of-dicts → arrays) must be pinned in design.md (target end-state Decided, not yet done). Source: tech.md, contradiction §4(3), §1.1.
14. **CdxA range** was 60–100 in 6 Oct, corrected to 60–105 in 8 Oct, with the clamp in the weather step. design.md must use 60–105 only. Source: contradiction §4(7), payload-force §5.
15. **Two driver models** exist (`DriverModel` canonical vs `simulate_driver` in `src/deprecated/`). The audit targets `DriverModel`; `simulate_driver` is reference only. design.md must say which is canonical. Source: contradiction §4(4).

### D. Gaps that must stay flagged, not filled
16. Placeholder efficiencies (0.95/0.95/0.98), no battery-resistance loss while driving, no regen cap, no cabin heating, single-Crr rolling resistance, rotating mass off, 10° yaw clamp — all flagged in reports, never silently "improved". Source: §5, `vecto-grounding.md`. **Now also includes PTO stop time and the high-mass power limit** (§1.1.10–11, deferred this session).
17. Any new non-VECTO extra (DC/DC loss, cabin heating, charging-time aux) must be an optional, flagged, neutral-default layer with an authentic non-VECTO source — not added without one. Source: paux §10, `vecto-grounding.md`.

### E. Things to time before deciding (no numbers invented)
18. The **timing gate** (runs first, before M2 structure code): one year of consumption per date + one year of charging **at a coarse step and a fine step** (§3.6a, §4.3; design §3F/§3G). Picks Option 1 vs the Option 3 fallback, informs B vs C, and sizes fine-`dt` charging cost.
19. Daily vs hourly weather (one year each way) — §3.5, decided after the timing gate.
20. Payload-shape rerun cost (a shape change needs a driver-model rerun) — payload design.

---

## 8. Requirement A — Stage entry points (multi-party, partial-chain runs)

**Product intent (Decided — Bob):** HDEV serves several parties on **one shared simulation**. A client defines its operation (routes, calendar, consumption, depot, grid limit, prices it pays); OEMs, charger makers, CPOs, aggregators, banks or consultants plug their **exact** data into the same project to show their product fits, or the client compares bids like-for-like. Users may want only part of the chain (only charging, only flexibility, only TCO, TCO + flexibility, …) without rerunning consumption. Nothing is built now; the **design and data contracts must make this possible without a later redesign**.

**User story:** As any party, I want to run any stage — or any combination of stages — of the chain **consumption → charging → flexibility → TCO/CO₂** (with sizing and sweep around them), fed either by the previous stage or by my own data in that stage's format, so I never recompute what I already have.

Acceptance criteria:
1. **(Decided)** The chain is **consumption → charging → flexibility → TCO/CO₂**, with **sizing** and **sweep** as cross-cutting operations around them. **Any stage, or any contiguous OR non-contiguous combination** (e.g. TCO + flexibility, skipping charging), can be run alone. Done-when: design.md's stage map lists each stage and shows that any subset can be selected. Source: Bob's intent.
2. **(Decided)** Each stage has a documented **ENTRY CONTRACT** (fields, units, shapes, time resolution). A stage can be fed by the previous stage **or** by user-supplied data in that format. Examples (not exhaustive): charging-only ← session list `{arrival, departure, energy_need_kWh, arrival_SOC}`; flexibility-only ← charging/load profile + equipment capabilities; TCO-only ← annual energy + peak power + equipment and price data. Done-when: design.md has an entry-contract table (stage → required fields/units/shape/resolution → what can feed it). Source: Bob's intent; ties to the existing session hand-over object (design §3C) and "skip a step" override (req §2.6).
3. **(Decided)** User-supplied stage inputs are labelled **"user-supplied"** with source + date in the assumptions report (this **generalises** the existing "skip a step" rule, req §2.6). The report must state **which stages were simulated and which were supplied**. Done-when: a run that starts mid-chain lists, per stage, simulated-vs-supplied with source+date. Source: Bob's intent; req §2.6, §5.
4. **(Decided)** `runner.run` **selects the start stage** from what the project provides, and **refuses with a clear message** if a stage's entry contract is incomplete — listing **exactly what is missing**. **No silent defaults for missing entry data** (consistent with `engine-rules.md` §6, no silent defaults in engines). Done-when: a project missing a required entry field gets a refusal naming that field; a complete one runs. Source: Bob's intent; `engine-rules.md` §6.
5. **(Open — options, pick after design)** Time resolution: each entry contract states its time step. When supplied data has a **different** resolution than the stage needs, the rule is **not invented** — design.md proposes options (resample / reject / flag) and marks this **Open**. Done-when: design.md lists the options with trade-offs and Bob picks one per stage. Source: Bob's intent; `vecto-grounding.md` no-invented-rules.

---

## 9. Requirement B — Open parameter slots (slot registry)

**User story:** As any party, I want every input to be an open, labelled **slot** I can fill or override, with the model telling me what it reads, what it ignores, and what is still missing, so I can plug my exact product data into a shared project without a schema redesign.

Acceptance criteria:
1. **(Decided)** Every input in every section (vehicles/battery, chargers, depot/grid, operation, prices/costs, markets) is a **SLOT**: `{value, unit, source, date, label, provided_by}`. `label ∈ {VECTO, REG, literature, HDEV ASSUMPTION, user-supplied, OEM-supplied, …}` (open vocabulary, extends the fixed defaults vocabulary of req §5.2); `provided_by ∈ {client, OEM, CPO, aggregator, consultant, Bob}`. Done-when: design.md defines the slot schema and shows it extends the existing `{value, source, date, label}` hook (design §6.3, req §2.5). Source: Bob's intent.
2. **(Decided)** Slots start as **labelled generic defaults** (from `defaults.py`) or **empty**. Any party's **change-set** can fill or override slots; results **rerun from the first affected stage** (the existing rerun table, design §1). Done-when: design.md ties slot overrides to the rerun entry points. Source: Bob's intent; design §1 rerun table, §6.1.
3. **(Decided)** The slot list is **OPEN-ENDED**, not a fixed spec-sheet list → a **slot registry**: each engine/stage **declares which slots it reads**. Consequences the design must handle:
   a. A supplied value for a slot **no stage reads** is accepted but reported **"provided, not used by any model"**.
   b. A slot a stage **needs but nobody filled** uses the labelled default, **or** the stage **refuses** (per A.4) if no default exists.
   c. Adding a new slot later = **registering it + giving a stage the physics to use it**; no schema redesign.
   Done-when: design.md specifies the registry (how a stage declares slots; how "not used" and "missing" are reported). Source: Bob's intent.
4. **(Decided — lock flag only; roles later)** **Operational** slots (routes, calendar, consumption, grid limit) are **LOCKED** for bidders in a bid-comparison run; **equipment and price** slots are open to them. Roles/permissions are out of scope; design only the **lock flag**. Done-when: design.md defines a per-slot (or per-section) `locked` flag and the bid-comparison semantics; no role system. Source: Bob's intent; ties to design §6.2 operational-vs-equipment split.
5. **(Decided + Suggestions)** **Capability flags are slots** and can **GATE** behaviour. **Decided rule:** a charger without smart-charging capability (no OCPP smart charging / no external setpoint) **restricts policy to ASAP**; JIT, cheapest-first and flexibility are **unavailable** for it, and the report says why. **Suggestion rules to evaluate:** bidirectional/V2G capability gates discharge/export; connector count gates simultaneous sessions; min-power gates deep modulation. Done-when: design.md lists the gating rules (ASAP-only Decided; others Suggestion) and how the report explains a restriction. Source: Bob's intent; charging policy set (req §4.2), `04-charging.md`.
6. **(Decided — physical/logical checks only)** Sanity checks on supplied values are **only physical/logical**: non-negative where physical, SoC window within 0–1, `min ≤ max`, units convertible. **No invented plausibility ranges.** Done-when: design.md lists the check set; a value failing a physical check is rejected with a clear message; an out-of-"typical"-but-physical value is **accepted**. Source: Bob's intent; `vecto-grounding.md` no-invented-numbers.

### 9A. Candidate slots — classification (used NOW / needs NEW physics / LATER), with research citation
**(Decided as the starting registry; open-ended per B.3.)** Each slot marked: **NOW** = an existing/planned M0–M3 engine already reads it; **NEW** = needs engine physics not yet planned; **LATER** = TCO/flexibility stage. Research file cited where VECTO covers it. `[no VECTO]` = HDEV/market data, not a VECTO quantity.

**Vehicle / battery:**
| slot | NOW/NEW/LATER | research |
|---|---|---|
| nominal & usable capacity, SoC window | NOW | `03-battery.md` §5 |
| OCV(SoC) table | NEW (M3.3) | `03-battery.md` §2 |
| Ri(SoC, pulse) table | NEW (M3.3) | `03-battery.md` §3 |
| max charge/discharge current or power (curve vs SoC) | NEW (M3.3) | `03-battery.md` §4 |
| OEM published charge curve | NEW (charging) | `03`/`04` (not a VECTO quantity; map to Ri+limits) |
| curb mass, GVW, axle config | NOW (M0.20) | `09-vehicle-data-and-defaults.md` §3–4 |
| CdxA | NOW | `09` §1 (`SegmentTable.csv`), `13-followups.md` §... (CdxA default verified) |
| tyre RRC & dimensions | NOW (single-Crr) / NEW (load-dependent) | `09` §5–6 |
| motor full-load & generation curves | NEW | `01-electric-machine.md` §3 |
| efficiency map (speed×torque→P_el) | NEW | `01` §2 (replaces 0.95/0.95 placeholder) |
| gearbox/axle losses | NOW (0.98 placeholder) / NEW (map) | `02-transmission-axle.md` |
| aux technologies (ES/HVAC/PS/SP/Cond) | NOW (M0.15) | `06-auxiliaries-all.md`, paux doc |
| PTO type/cycle | NEW (deferred, M0.10) | `07-pto-all.md` |
| battery mass | NOW (sizing) | `03`/sizing |
| warranty cycles / degradation data | LATER (TCO) | `[no VECTO]` |

**Charger:** rated power, min power, power per connector, connector count, ramp rate, efficiency (curve), standby power, voltage/current range, comms/OCPP version & smart-charging support, bidirectional capability, cable/plug type — **all NEW (charging) or capability-flag slots; `[no VECTO]`** (VECTO has no charger model — `04-charging.md` §1). The 500/250/100 kW OVC-HEV accounting values are **not** charger defaults (`13-followups.md` §3).

**Depot / grid:** connection limit (kW/A), existing site load profile, DSO, tariff structure, transformer limits, metering point — **NEW (charging/site cap) or LATER (TCO tariffs); `[no VECTO]`.**

**Prices & costs (TCO):** vehicle price, residual value, financing (rate/term), maintenance, insurance, charger hardware+installation, grid connection fee (DSO-specific), electricity spot series, grid tariffs (ToU), taxes/duties, road tax, subsidies, contract types, demand/capacity charges, diesel reference — **all LATER (TCO); `[no VECTO]`;** structure from `tco-and-reference-excels.md` (COWI), never its unsourced numbers.

**Flexibility / markets:** product parameters (resolution, activation duration, minimum bid), market prices/revenues, aggregator fees — **LATER (flexibility); `[no VECTO]`; all "from Energinet product specs, to be sourced", never invented** (req §4.3.3).

---

## 10. Requirement C — Comparison output (base vs change-sets, fit verdict)

**User story:** As a client (or bidder), I want the base run and each change-set shown side by side with identical metrics and a fit verdict built only from simulated results, so I can compare bids like-for-like without invented thresholds.

Acceptance criteria:
1. **(Decided)** Base run vs each change-set shown **side by side** with **identical metrics, units and assumptions lists**. Done-when: design.md defines the comparison output structure (one column per change-set, same rows). Source: Bob's intent; design §6.1 base+change-set hook.
2. **(Decided)** Each change-set shows a **FIT verdict with reasons, built only from simulated results**: shortfall at departure (yes/no, kWh), site peak vs grid limit, payload lost to battery mass, SoC-window violations, policy restrictions from capability flags (req B.5), TCO difference. **No invented thresholds** — the client sets any pass/fail limits as **slots**. Done-when: design.md lists the verdict fields, each traceable to a simulated quantity, and shows pass/fail limits are client-supplied slots. Source: Bob's intent.
3. **(Decided)** The report lists, per change-set, **which slots that party supplied and which defaults remained**. Done-when: the comparison output carries a per-change-set provenance list (ties to B.1 `provided_by`). Source: Bob's intent; req §5.
4. **(Suggestion)** Inverse question — **"what is the smallest battery / charger that fits this operation?"** via the existing sweep (design §2 `sweep.py`, req §4.4). Mark Suggestion. Done-when: design.md notes the sweep can be run as an inverse/fit search; Bob decides. Source: Bob's intent (Suggestion).

---

## 11. Requirement D — TCO data model (contract, not built now)

**User story:** As an analyst, I want TCO runnable from supplied energy/peak data with prices and tariffs as versioned slots, so costs can be compared without rerunning consumption or charging.

Acceptance criteria:
1. **(Decided)** Prices and tariffs are **slots** that can be **scalars OR time series**, each with **source + date + version** (ties to the versioned dated data-file rule, product.md impl. 8 / design §6.4). Done-when: design.md's TCO data model shows scalar-or-series slots with version metadata. Source: Bob's intent.
2. **(Decided)** TCO must be **runnable from supplied annual energy + peak** without running consumption/charging (this is Requirement A applied to the TCO stage). Done-when: the TCO entry contract (A.2) lists `{annual_energy_kWh, peak_power_kW, equipment, prices}` and `runner.run` can start at TCO. Source: Bob's intent; req §8.
3. **(Decided — reference only)** Reuse the **STRUCTURE** of `docs/context/tco-and-reference-excels.md` (COWI `eltiltrucks-beregner-ark.xlsx`) — sheet/formula method (PMT annuity + residual balloon, lost-production cost, breakeven, lademeter, DSO connection fee formula, ToU electricity method) — **never its unsourced numbers** (truck prices, interest, operating days, kWh/km, etc. are explicitly unsourced). Done-when: design.md's TCO model cites COWI structure and marks every number as a to-be-sourced slot. Source: Bob's intent; `tco-and-reference-excels.md`.
4. **(Open)** Which TCO outputs are the headline metrics (TCO/km, breakeven, monthly cost, CO₂) and how they combine with the fit verdict (C.2) — propose in design, Bob confirms. Source: Bob's intent.
