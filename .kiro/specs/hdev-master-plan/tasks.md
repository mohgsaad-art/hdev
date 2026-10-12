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
