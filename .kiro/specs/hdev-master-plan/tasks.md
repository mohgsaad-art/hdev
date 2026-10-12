# HDEV master plan — tasks

**Bob writes all code.** Each task is one function or one fix. Tasks are dependency-ordered inside milestones; milestones are ordered M0 → M5. Format: **what · file · done-when · depends-on**. 🔒 = **needs a decision from Bob first** (see requirements/design). Kiro writes tests only when asked.

> Blocking inputs not in the bundle (ask Bob before the tasks that need them): consumption code, Waypoint/vacc parser, Sept resolver, dashboard HTML, VDRI analysis script, and the **missing** regulation extracts (Annex Xb map, Annex VIII air-drag). (`working-style.md`, requirements self-check A.)

---

## M0 — Engine correctness

Driver-model audit fixes (`DriverModel` is canonical; `simulate_driver` is reference only — contradiction §4(4)). Never rename Bob's variables.

- **M0.1** Guard against the infinite-loop risk in `driver_model` · `src/engine/driver_model.py` · done-when: bounded-iteration run over all five VECTO `.vdri` cycles terminates · depends: Waypoint/vacc parser (ask Bob).
- **M0.2** Fix segment-level vs step-level acceleration · `driver_model.py` · done-when: stored `accel` matches `(v2−v1)/dt` per row except the two clamp cases · depends: M0.1.
- **M0.3** Remove div-by-zero in `get_breaking_distance` · `driver_model.py` · done-when: `v0==v1` and zero-decel raise/return defined, not inf/nan · depends: M0.1.
- **M0.4** Make `vacc_lookup` raise out-of-range instead of returning `None` · `driver_model.py` · done-when: out-of-range speed raises · depends: M0.1.
- **M0.5** Add the missing early exit + delete dead braking-distance logic · `driver_model.py` · done-when: no unreachable branch; reference-cycle behaviour unchanged · depends: M0.3.
- **M0.6** Fix the arrival `speed = target_speed` / dropped-`ds` jump (fix now) · `driver_model.py` · done-when: energy change on reference cycle is bounded + rule recorded (carry `ds` vs sub-step) · depends: M0.2 · (decided: fix in M0 — req §1.1.6).
- **M0.7** Keep the clamp-to-0 accel/`v2` interaction consistent with the force engine · `driver_model.py` · done-when: documented clamp preserved + asserted · depends: M0.2.
- **M0.8** Fix/define the `stop==0 & target_speed==0` momentary-stop behaviour (fix now) · `driver_model.py` · done-when: rule recorded + tested · depends: M0.1 · (decided: fix in M0 — req §1.1.8).
- **M0.9** Add `'payload'` to every emitted row · `driver_model.py` · done-when: no row lacks numeric payload · depends: M0.1, H already done.
- **M0.10** Record MunicipalUtility PTO stop-time as a flagged gap (deferred, not implemented in M0) · assumptions report + `status.md` known-gaps intent · done-when: the +~23 s/stop PTO gap is listed as a flagged gap, no code change · depends: — · (decided: defer, record — req §1.1.10).
- **M0.11** Record the high-mass power limit as a flagged gap (deferred, not modelled in M0) · assumptions report + known gaps · done-when: the power-limit gap is listed, no code change · depends: — · (decided: defer, record — req §1.1.11).
- **M0.12** 🔒 Grade from VECTO altitude-secant vs flat `grade_pct` · `driver_model.py` · done-when: matches VECTO secant on reference cycle, or difference recorded · depends: M0.1 · decision: `DrivingCycleData.cs` — req §1.1.12.
- **M0.13** 🔒 Switch to official `Truck.vacc` · `driver_model.py` (+ loader) · done-when: reference run uses `reference/vecto/resources/VACC/Truck.vacc`; loader tested · depends: M0.1 · decision: confirm replacement — req §1.1.13.
- **M0.14** Row-storage adapter: driver-model output → numpy arrays per column · `src/server/runner.py` (or helper) · done-when: downstream steps receive arrays; driver model internals unchanged · depends: M0.9 · design §4.

P_aux:
- **M0.15** Implement `p_aux(ES,HVAC,PS,SP,Cond, moving, motor_on)` · `src/engine/p_aux.py` · done-when: three states reproduce 2938.9/2537/1937 W (paux §5); default BEV technologies carry the **HDEV ASSUMPTION** label; blank/`"---"` cells **raise** (mirror VECTO) · depends: M1.1 · (decisions resolved: flagged HDEV defaults, VECTO-error on blanks — req §1.2.6; function structure is the §1.2.7 Suggestion).
- **M0.16** Define the `motor_on`/`EmOffPrev` rule in the driver-model audit · `driver_model.py` + `p_aux.py` · done-when: rule recorded during the audit + Cond term toggles on it · depends: M0.2, M0.15 · (decided: define during driver audit — req §1.2.5; couples G and P_aux).

Weather, power, consumption:
- **M0.17** Implement `weather_for_rows` (ρ inline + CdxA_eff lookup, 60–105 clamp, raise on extrapolation) · `src/engine/weather_for_rows.py` · done-when: ρ hand-value test; clamp/interp/extrapolation tests; `CdxA_eff=CdxA(0)·W1+W2` · depends: F done, M0.14.
- **M0.18** 🔒 Decide `DeltaAirDragAreaIMC` handling (default 0 vs ground from `IMC-Tech.csv`) · `weather_for_rows.py` · done-when: argument present with chosen default · depends: M0.17 · decision: req §1.3.5.
- **M0.19** Implement `power_step` (multiply-add, vectorised) · `src/engine/power_step.py` · done-when: matches loop reference; neutral β=1/θ_red=0 reproduces simple K · depends: I done, M0.17.
- **M0.20** Mass assembly `m = vehicle+body+payload` with GVWR/40t/60t cap · `src/engine/mass.py` · done-when: cites SegmentTable/Body_Trailers; cap test · depends: M1.1.
- **M0.21** 🔒 Implement `consumption` (sign-dependent η + P_aux → kWh) · `src/engine/consumption.py` · done-when: matches loop reference; sign switch at P_wheel=0; fixes `regen_effeiciency` typo · depends: M0.19, M0.15 · decision: Bob pastes the notebook consumption code or confirms rewrite — req §1.5.3.

---

## M1 — Data contracts + defaults.py

- **M1.1** Write `defaults.py` with every default + source + label (VECTO/REG/literature/HDEV ASSUMPTION) · `src/resolver/defaults.py` · done-when: transcribes the 7 Oct defaults doc + paux tables with per-value file citations; label-set test · depends: — · 🔒 for CdxA-default values (req §5.7, Annex VIII extract **missing**).
- **M1.2** Encode neutral VECTO params (β=1, θ_red=0, single Crr) with VECTO values (β=0.9) cited separately · `defaults.py` · done-when: review · depends: M1.1.
- **M1.3** Define the project-JSON section shapes (vehicles, chargers, routes, assignments+count, calendar_environment, provenance) · design doc / `src/resolver/` docstrings · done-when: every §3/§6 field has name+unit+shape; equipment/operational split present · depends: —.
- **M1.4** 🔒 Define the `{value, source, date, label}` input-metadata field shape (design hook) · `src/resolver/` · done-when: shape defined; defaults use the label · depends: M1.1 · decision: req §2.5.
- **M1.5** Define the "skip a step" resolver override (user kWh/km bypasses F–J, flagged) · `src/resolver/resolve.py` · done-when: override path specified + flagged in assumptions · depends: M1.3.
- **M1.6** Split the DRAFT DMI code into `fetch_dmi` (network) + `build_weather` (pure) · `src/data_fetch/fetch_dmi.py`, `build_weather.py` · done-when: per-year daily (T,wind) series by date, no cross-year averaging; coverage check; station distance returned · depends: — · fixes contradiction §4(9).
- **M1.7** Assumptions-report builder (lists defaults used, deviations applied, flagged gaps) · `src/server/runner.py` or `report.py` · done-when: a reference run lists the four deviations + §5 gaps **+ the deferred PTO stop-time and high-mass power-limit gaps (M0.10–M0.11)** · depends: M1.1, M0.10, M0.11.

---

## M2 — Year / day / week

**Structure is Decided: Option 1 (every operating date directly); Option 3 is a fallback used only if the timing gate (M2.1) fails. The timing gate runs FIRST, before any structure code.** (req §3.6/§3.6a, design §3E/§3F.)

- **M2.1** **Timing gate (runs first):** measure one year of consumption per date **and** one year of charging **at a coarse `dt` and a fine `dt`** · scratch script (not an engine) · done-when: both consumption and coarse/fine charging timings reported; a go/fallback note recorded · depends: M0.21, and the pulled-forward charging basics M3.0 (`dt` arg), M3.3 (OCV+Ri), M3.4 (de-capped session env) · (decided: timing-gate-first — req §3.6a, §4.3; design §3F/§3G).
- **M2.2** Lock Option 1 (or trigger Option 3 fallback) from the gate result · design note · done-when: Option 1 confirmed proceed, or Option 3 fallback recorded with reasons · depends: M2.1 · (decided: Option 1, fallback only — req §3.6).
- **M2.3** Build the daily (option A) weather path first; defer B vs C to the gate · uses `weather_for_rows` · done-when: daily path works; B-vs-C decision deferred to M2.1 comparison, not pre-chosen · depends: M0.17, M2.1 · (decided: start daily, decide B/C after timing — req §3.5).
- **M2.4** `build_calendar` (one row/date: operating?, day-type, T, wind) · `src/resolver/calendar.py` · done-when: calendar table built from JSON + weather · depends: M1.6, M2.2.
- **M2.5** `group_runs` (unique day-type × weather → count) — **only if the Option 3 fallback is triggered**; not built under Option 1 · `src/resolver/calendar.py` · done-when: unique combos + counts, extremes kept separate — or skipped under Option 1 · depends: M2.2, M2.4.
- **M2.6** 🔒 Define the session hand-over object `{arrival, departure, energy_need_kWh, arrival_SOC}` · `src/resolver/calendar.py` or `charging/` · done-when: consumption produces it; charging consumes it · depends: M2.4 · decision: confirm fields — req §3.7, design §3C.
- **M2.7** 🔒 Add optional `departure_time` to routes/calendar (needed for option C / JIT / EDF) · `src/resolver/` schema · done-when: field present + ignored by daily path · depends: M2.3 · decision: tie to B-vs-C — req §3.8, design §3D(4(5)).
- **M2.8** Annual totals + worst-day + **daily-result weather-spread percentiles** (labelled weather spread, **not** result P10/P90) from Option 1 · `src/server/runner.py` · done-when: totals/worst-day/weather-spread computed per §3B Option 1; Monte Carlo result P-values kept separate · depends: M2.2, M2.4 · (decided: separate the two spreads — req §3 user story).

---

## M3 — Battery + charging

> **Cross-milestone note:** the M2.1 timing gate needs a working charging stepper with the `dt` argument, so **M3.0, M3.3 and M3.4 are pulled forward** to run before M2.1. Everything else in M2 waits on the gate. This is the one deliberate M3-before-M2 dependency.

- **M3.0** Make the charging time step `dt` an **argument** of the env/runner (not fixed 5 min / 300 s); add the two-resolution hook (`dt_base`, `dt_fine`, activation/event window list; neutral default `dt_fine==dt_base`, no windows) · `src/charging/ev_charging_env.py` (+ runner) · done-when: nothing hard-codes 5 min; `dt_fine==dt_base` reproduces a plain fixed-`dt` run; window definitions/resolutions are marked **"from Energinet product specs, to be sourced"** · depends: — · (decided: `dt` argument + finer-step-in-windows — req §4.3, design §3G).
- **M3.1** Battery sizing mode A (datasheet mass+kWh, no loop) · `src/charging/sizing.py` · done-when: mode-A run uses datasheet directly · depends: M0.21.
- **M3.2** 🔒 Battery sizing mode B (glider + kWh/kg + payload, iterate to fixpoint) · `sizing.py` · done-when: converges on reference; GVW legal check separate · depends: M3.1 · decision: glider mass + pack kWh/kg sources needed — req §4.1.3.
- **M3.3** OCV + internal-resistance battery model (replaces exponential taper) · `src/charging/battery_ocv_ri.py` · done-when: matches `Battery.cs` behaviour on a charge-curve test · depends: — · uses `reference/vecto/cs/Battery.cs`.
- **M3.4** Remove the fixed 21 h episode cap + random `reset()`; session = arrival→departure · `src/charging/ev_charging_env.py` · done-when: a two-session (overnight) run is not cut; steps at the `dt` argument from M3.0 · depends: M3.0 · (note: pulled forward before M2.1; session-object detail M2.6 can follow).
- **M3.5** Wire JIT/ASAP setpoints + feasibility to the de-capped env · `src/charging/flexibility_setpoints.py` · done-when: setpoints use real departure times · depends: M3.4 · keep pure.
- **M3.6** Keep EDF/ES split as pure functions of env state against the de-capped env · `src/charging/allocators_edf_es.py` · done-when: purity test (no env mutation) · depends: M3.4.
- **M3.7** Generalise the runner horizon to real session length; step at the `dt` argument · `src/charging/run_allocator_21h.py` · done-when: runs an overnight+weekend sequence at a chosen `dt` · depends: M3.4, M3.0.
- **M3.8** 🔒 Cheapest-first policy (needs hourly price series) · `src/charging/` · done-when: policy uses a versioned dated price file · depends: M3.5 · decision: Energidataservice price source — req §4.2.5.
- **M3.9** SOC carry-over across sessions (Option 1: continuous real date sequence; two-weeks-keep-second only if the Option 3 fallback is used) · `charging/` · done-when: ending SOC feeds next arrival_SOC; shortfall reported · depends: M2.2, M3.4 · (Option 1 carry-over is Decided; representative-week variant only on fallback — req §4.2.6).
- **M3.10** Depot sweep (battery × charger kW × policy × site limit, skip impossible) → site peak · `src/charging/sweep.py` · done-when: small grid returns site peak per combo · depends: M3.1, M3.5.

---

## M4 — Local server + UI

- **M4.1** `runner.run(base, changes=None)` orchestration (JSON → resolve → pipeline → results JSON + provenance block) · `src/server/runner.py` · done-when: a reference project JSON returns results JSON · depends: M0.21, M1.3, M2.8.
- **M4.2** Thin local HTTP server (parse body → `runner.run` → response) · `src/server/app_local.py` · done-when: posts project JSON, gets results JSON; no engine import of transport · depends: M4.1.
- **M4.3** `resolve_typed` (typed summary → waypoints; even stop spacing = flagged Assumption) · `src/resolver/resolve_typed.py` · done-when: a typed summary builds an editable waypoint table · depends: M1.1 · ask Bob for Sept resolver code.
- **M4.4** VDRI adapter (every row → waypoint; constant VECTO reference payload default; edit → user route) · `src/resolver/vdri_adapter.py` · done-when: a `.vdri` loads to waypoints; edit relabels, original untouched · depends: M1.1.
- **M4.5** 🔒 GPS adapter (stop on first zero-speed row of each stop) · `src/resolver/gps_adapter.py` · done-when: stops marked; threshold recorded · depends: M1.1 · decision: zero-speed threshold unsourced — req open, payload design.
- **M4.6** `resolve.py` field list derived from what engines read (written last) · `src/resolver/resolve.py` · done-when: fields map to engine signatures · depends: M0.*, M4.3–M4.5.
- **M4.7** Dumb-form UI pages, one per JSON section; Advanced toggle; defaults in terracotta · `src/ui/pages/` · done-when: pages post raw JSON; no maths in JS · depends: M4.2.
- **M4.8** Payload stop-table page (filters stop>0; editable columns per source) · `src/ui/pages/` · done-when: edits write back into waypoint rows; display-only filtering · depends: M4.7, H.
- **M4.9** UI state = **server-saved `projects/<id>.json` behind the thin transport layer** (engine stays stateless; same store contract for the FastAPI swap) · `src/server/` · done-when: server reads/writes `projects/<id>.json`; engine never reads it · depends: M4.2 · (decided — req §6.5).

---

## M5 — Validation vs VECTO

- **M5.1** Keep the crosswind verification test green (0.006 % vs VECTO Excel) · `src/engine/crosswind_engine.py` test · done-when: passes · depends: —.
- **M5.2** Build the VECTO-equivalent reference run (one cycle, 3 m/s @ 4 m, constant reference payload, neutral β=1/θ_red=0, VECTO aux) · `src/server/runner.py` config · done-when: pipeline runs end-to-end with declaration inputs · depends: M4.1.
- **M5.3** 🔒 Compare M5.2 output to a VECTO consumption reference within a stated tolerance · test · done-when: within tolerance · depends: M5.2 · decision: Bob supplies a VECTO reference number + consumption code; Annex Xb map **missing** — req §7.3.
- **M5.4** Assert the reference run's assumptions report lists every deviation used + flagged gaps · test · done-when: report lists yaw clamp, in-cycle payload, DMI wind, edited-VDRI, §5 gaps · depends: M1.7, M5.2.
- **M5.5** Property tests: neutral defaults reproduce simple equation; `fill_payload` never leaves NaN; zero wind → W1=1,W2=0 · tests · done-when: all pass · depends: M0.19, H, F · (write only when Bob asks).

---

## M5 addendum — VECTO full reference (off-sandbox)

- **M5.6** 🔒 **Bob runs VECTO off-sandbox** for the M5.3 anchor · (no HDEV code) · done-when: an official VECTO release runs `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BEV_E2.vecto` and Bob brings back per-mission **kWh/km** (+ kWh/t·km), **REESS_StartSoC/EndSoC**, **E_REESS_LOSS** from the `.vsum` (and `.vmod` SoC/`P_REESS_T`/`U_0_REESS`/`I_REESS` for a row check) · depends: — · decision/action: Bob (VECTO could not build in the sandbox — `13-followups.md` §4; feeds M5.3).

---

## M6 — Multi-party: stages, slots, comparison, TCO (contracts + hooks; engines untouched)

**All of M6 is resolver + runner + report work.** Engines stay pure (design §4J). Nothing here adds physics except where a candidate slot needs it (those are the existing M0–M3 engine tasks, cited). One function per task; dependency-ordered. 🔒 = needs a Bob decision first.

### M6.0 — Stage framework
- **M6.1** Define the **stage map** + stage enum (`consumption, charging, flexibility, tco`; `sizing`/`sweep` as operations) · design note / `src/server/stages.py` docstrings · done-when: the four stages + two operations are named and ordered per design §4A · depends: — · (Decided — req §8.1).
- **M6.2** Write the **entry-contract table** as data (`src/resolver/entry_contracts.py`): per stage, required fields + unit + shape + native resolution · done-when: every stage in design §4B is represented with required-field lists · depends: M6.1 · (Decided — req §8.2).
- **M6.3** `check_entry_contract(project, stage)` → list of missing fields · `src/server/runner.py` · done-when: a project missing a required field returns exactly that field; a complete one returns `[]` · depends: M6.2 · (Decided — req §8.4).
- **M6.4** `select_start_stage(project)` → earliest satisfiable stage · `runner.py` · done-when: a project with only a session list selects `charging`; a full project selects `consumption`; a non-contiguous (TCO+flex) selection is expressible · depends: M6.3 · (Decided — req §8.1).
- **M6.5** Wire `runner.run(base, changes)` to **select start + refuse on incomplete entry** (no silent default) · `runner.py` · done-when: incomplete start refuses with the missing list; complete runs from the chosen stage · depends: M6.4, M4.1 · (Decided — req §8.4).
- **M6.6** 🔒 **Resolution-mismatch handling** per stage (resample / reject / flag) · `entry_contracts.py` + `runner.py` · done-when: the chosen rule per stage is implemented and the report states resolution used · depends: M6.2 · decision: req §8.5 (opt-R1/R2/R3; design §4B recommends R2 charging↔flex, R1 energy-conserving for TCO).

### M6.1 — Slots + registry
- **M6.7** 🔒 Define the **slot schema** `{value,unit,source,date,label,provided_by,locked,version}` (extends the `{value,source,date,label}` hook) · `src/resolver/slots.py` · done-when: schema defined; a `defaults.py` entry is expressible as a slot; label/provided_by vocab test · depends: M1.1, M1.4 · decision: confirm the field shape (req §9.1; design §4D).
- **M6.8** Build the **slot registry** `STAGE_SLOTS` (each stage declares the slot keys it reads + unit + default-or-None) · `src/resolver/registry.py` · done-when: the §9A candidate slots are registered to their stages with units; adding a key is additive · depends: M6.1, M6.7 · (Decided — req §9.3).
- **M6.9** `classify_slots(project, selected_stages)` → `{used, defaulted, provided_unused, missing}` · `registry.py` · done-when: a supplied slot no stage reads lands in `provided_unused`; a needed empty slot with a default lands in `defaulted`, without a default in `missing` · depends: M6.8 · (Decided — req §9.3a–c).
- **M6.10** `resolve_slot(key, project)` → plain SI argument for the engine (default fallback or raise) · `registry.py`/`resolve.py` · done-when: fills from slot or `defaults.py`; raises (not silent) when needed-but-empty-and-no-default · depends: M6.8 · (Decided — req §9.3b; `engine-rules.md` §6).
- **M6.11** **Sanity checks** on supplied slots (non-negative, SoC∈[0,1], min≤max, units convertible, OCV monotone) — physical/logical only · `src/resolver/slot_checks.py` · done-when: a negative power / inverted min-max / non-convertible unit rejects with a clear message; an unusual-but-physical value is accepted · depends: M6.7 · (Decided — req §9.6; no invented ranges).

### M6.2 — Change-sets + locks
- **M6.12** `apply_change_sets(base, changes)` → merged project with per-slot `provided_by` recorded · `runner.py` · done-when: an empty change-set returns the base unchanged; a write fills/overrides the slot and records who · depends: M6.7, M4.1 · (Decided — req §9.2; design §6.1/§4E).
- **M6.13** Route a change-set to the **rerun entry point** (first affected stage) via the rerun table · `runner.py` · done-when: a `charger.rated_kW` write reruns charging-onward only; a `vehicle.CdxA` write reruns from weather/power · depends: M6.12, M6.5 · (Decided — design §1 rerun table).
- **M6.14** **Lock flag** enforcement: a change-set write to a `locked` slot is rejected · `runner.py` · done-when: in a bid-comparison base (operational slots locked) a bidder write to a route/calendar/grid-limit slot is rejected with a clear message; equipment/price writes pass · depends: M6.12 · (Decided — req §9.4; no role system).

### M6.3 — Capability gating
- **M6.15** **Capability gate: ASAP-only when no smart-charging** · `src/resolver/capability_gates.py` · done-when: a charger slot `smart_charging=false` narrows the policy set to ASAP and records the reason; `true` leaves all policies · depends: M6.8, M3.5 · (Decided — req §9.5).
- **M6.16** 🔒 Additional gates (bidirectional→no export; connectors→max simultaneous; min_power→no deep modulation) · `capability_gates.py` · done-when: each implemented gate narrows behaviour + records why · depends: M6.15 · decision: req §9.5 (Suggestions — Bob picks which to build).

### M6.4 — Assumptions report (stage-aware)
- **M6.17** Extend the assumptions report: **which stages were simulated vs supplied**, each supplied input labelled user-supplied with source+date · `src/server/report.py` · done-when: a mid-chain run lists simulated-vs-supplied per stage · depends: M1.7, M6.5, M6.9 · (Decided — req §8.3).
- **M6.18** Report the slot provenance lists (`used`/`defaulted`/`provided_unused`/`missing`) · `report.py` · done-when: the report carries all four lists per run · depends: M6.9, M6.17 · (Decided — req §9.3, §10.3).

### M6.5 — Comparison / fit
- **M6.19** `compare(base_result, change_results)` → side-by-side, identical metric keys/units · `src/server/compare.py` · done-when: base and each change-set share metric keys/units/assumptions structure · depends: M6.12, M4.1 · (Decided — req §10.1).
- **M6.20** 🔒 `fit_verdict(result, limits)` from simulated results only (shortfall, site-peak-vs-limit, payload-lost, SoC violations, policy restrictions, TCO diff); pass/fail limits are **client slots** · `compare.py` · done-when: every fit field traces to a simulated quantity; an empty limit slot yields `ok=null`; no invented threshold · depends: M6.19, M6.15 · decision: req §10.2 (confirm the fit-field set).
- **M6.21** 🔒 **Suggestion:** inverse/fit sweep — reuse `sweep.py` to find the smallest battery/charger that makes every fit field pass · `src/charging/sweep.py` wrapper · done-when: a sweep returns the minimal passing combo (or "none feasible") · depends: M6.20, M3.10 · decision: req §10.4 (Suggestion — Bob decides).

### M6.6 — TCO data model (contract; built LATER)
- **M6.22** TCO **entry contract** `{annual_energy_kWh, peak_power_kW, equipment, prices, tariffs}` registered as a stage · `entry_contracts.py`, `registry.py` · done-when: `runner.run` can start at `tco` from supplied energy+peak without consumption/charging · depends: M6.2, M6.8 · (Decided — req §11.2).
- **M6.23** Price/tariff **slot shape**: scalar OR time series, each with source+date+version · `slots.py` · done-when: a scalar price and a ToU time-series tariff are both expressible as slots with version metadata · depends: M6.7 · (Decided — req §11.1).
- **M6.24** 🔒 TCO **method skeleton** (PMT annuity + residual balloon, lost-production, breakeven, lademeter, DSO fee, cheapest-N-hours electricity) — **structure only, every coefficient a to-be-sourced slot** · `src/server/tco.py` (LATER) · done-when: the formula shapes exist with no COWI number as a default; outputs flagged to-be-sourced · depends: M6.22, M6.23 · decision: req §11.4 (confirm headline metrics + fit coupling; sources needed before any number).
- **M6.25** 🔒 CO₂/LCA **slot set** (vehicle/battery production, grid emission-factor time series) — structure from COWI LCA, numbers to-be-sourced · `tco.py` (LATER) · done-when: LCA factors are slots with source+date; grid factor is a time series; no number defaulted · depends: M6.24 · decision: req §11 (sources needed).
