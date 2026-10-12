# HDEV master plan — design

**Planning only.** No `src/` code changes; no tasks run. This design keeps every existing file name and variable; where it suggests a change, that is a diff for Bob to apply, not an edit Kiro makes (`working-style.md`). Every physics value cites a file; nothing is invented (`vecto-grounding.md`).

Tags: **Decided** (cited), **Open** (needs Bob), **Suggestion** (Kiro's).

---

## 1. Architecture — the full pipeline A→O

Order is the **Decided 8 Oct** order: payload runs on the waypoints **before** the driver model (`structure.md`, contradiction §4(1)). Letters are the step labels from the close-outs. "Precompute" = everything above W, computed once and reused; weather enters at W, mass at J (6 Oct §2).

```
A  Inputs — project JSON { vehicles, routes, assignments(count), calendar/environment }
            │                                    (equipment data | operational data kept separate)
            ▼
B  Validate (Pydantic) ............................ LATER, with FastAPI — not now
            │
C  Resolve (defaults.py; typed/GPS/AI → waypoints) . WRITTEN LAST (fields come from what engines read)
            │
            ▼   waypoints = list of {distance_m, target_speed_kmh, altitude/grade, stop_s, payload}
      ┌─────┴───────────────────────────────────────────────┐
      │ H  payload_engine(stop, shape, start, end, custom)   │  value on row0 + stop>0 rows, NaN elsewhere
      │        → UI stop table (shows stop>0, user edits)     │  edits write back into the same waypoint rows
      │        → fill_payload(payload)  forward-fill          │  every waypoint now has a payload
      └─────┬───────────────────────────────────────────────┘
            │
F  crosswind_engine(height, v_ref, h_ref, a1..a3, wind_exp, dh, dphi, v_veh_kmh, beta_limit_deg)
            │        → W1, W2 tables (rows = winds, cols = 60–105 km/h)   [once per vehicle, route-independent]
            ▼
G  driver_model(waypoints).driver_model(vacc, dt_s=1)   → 1 s rows {time, distance, speed, accel, grade, dt_s, payload}
            │        [loop — each step depends on previous; copies grade & payload from waypoints]
            │        >>> ROW STORAGE CONVERSION POINT: list-of-dicts  →  numpy arrays per column  <<<
            ▼
I  force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red)  → k_lin, k_roll, k_rot, L, v_avg
            │        [vectorised; no mass, no ρ; neutral β=1, θ_red=0 ⇒ simple K]
            ▼
W  weather_for_rows(rows, departure_time, temps_by_hour, winds_by_hour, cdxa_table) → rho_rows, cdxa_rows
            │        [ρ = P/(R·T) inline; CdxA_eff = CdxA(0)·W1 + W2; clamp 60–105 km/h, raise on extrapolation]
            ▼
J  power_step: P_wheel = m·k_lin + m^β·k_roll + k_rot + ρ·CdxA_eff·L        [m = vehicle+body+payload]
            │                                   ┌─ p_aux(ES,HVAC,PS,SP,Cond, moving, motor_on) → P_aux per row
            ▼                                   ▼
   consumption: P_batt = np.where(P_wheel>0, P_wheel/η, P_wheel·η_regen) + P_aux ; Σ·dt → kWh per row/day
            │
            ▼
D/E Calendar (one row/date: operating?, day-type, T, wind) + Group (unique day-type × weather bins) → annual totals
            │        [consumption does NOT read the calendar; calendar feeds weather lookups, charging sequence, totals]
            ▼
L  battery sizing — mode A (datasheet, no loop) | mode B (glider + kWh/kg + payload, iterate)
            │
            ▼
M  charging — per plug-in session (arrival→next departure); OCV+Ri battery; ASAP/JIT setpoint;
            │   EDF / ES split of site target; site cap couples vehicles; SOC carries over
            ▼
N  sweep (battery × charger kW × policy × site limit, finite real lists, skip impossible)
            │
            ▼
O  costs / CO₂ / report (LATER; COWI Excel reference) + assumptions report (defaults, deviations, gaps)
```

Rerun entry points (6 Oct §6, "rerun table"): route→G; wind→W (new F row) then J; Cd/A→cdxa_eff then W,J; height/group/h_ref→F; payload/mass→J; temperature→W then J; efficiencies/P_aux→consumption; battery→J (mode B) then M; arrival/departure, charger kW, policy, site limit→M; prices→M, O.

---

## 2. Module / folder layout for `src/`

Keeps every existing file and name. **Bold** = new file Bob would create. Nothing under `reference/` is ever touched (read-only).

```
src/
  engine/
    crosswind_engine.py      F   DONE (verified)            — keep as-is
    payload_engine.py        H   DONE (payload_engine + fill_payload)
    force_engine.py          I   DONE (coefficients: k_lin,k_roll,k_rot,L,v_avg)
    driver_model.py          G   under audit (DriverModel class) — audit fixes only
    p_aux.py                 P_aux stub → implement p_aux(...)
    **power_step.py**        J   NEW (multiply-add). Named power_step, NOT force_engine (avoid collision)
    **weather_for_rows.py**  W   NEW (ρ inline + CdxA_eff lookup, 60–105 clamp)
    **consumption.py**       consumption (sign-dependent η + P_aux → kWh)
    **mass.py**              Suggestion: assemble m = vehicle+body+payload with GVWR/40t/60t cap (SR7)
  data_fetch/
    dmi_weather_climatology.py  DRAFT → SPLIT into fetch + build (below)
    **fetch_dmi.py**         Suggestion: network only (download once, save raw by args)
    **build_weather.py**     Suggestion: pure (align T & wind by date, per-year series, coverage check)
    dmi_wind_plot_old.py     OLD — leave
  resolver/                  **NEW folder** (resolve is written LAST)
    **defaults.py**          every default, each with source + label (VECTO/REG/literature/HDEV ASSUMPTION)
    **resolve_typed.py**     typed summary → waypoints (even stop spacing = Assumption, flagged)
    **vdri_adapter.py**      VDRI row → waypoint (constant VECTO reference payload default)
    **gps_adapter.py**       telemetry → waypoints (stop on first zero-speed row; threshold = Open)
    **resolve.py**           field list derived from what engines read; "skip a step" override lives here
    **calendar.py**          build_calendar (one row/date) + group_runs (unique day-type × weather)
  charging/
    ev_charging_env.py       physics env — remove 21 h cap & random reset (keep as env)
    flexibility_setpoints.py JIT/ASAP setpoints + feasibility — keep
    allocators_edf_es.py     EDF + ES split (pure fns of env state) — keep
    run_allocator_21h.py     runner — generalise horizon to real session length
    tester_21h_maddpg.py     THESIS legacy — leave (helpers/plots only)
    **battery_ocv_ri.py**    NEW: OCV + internal-resistance model (replaces exponential taper)
    **sizing.py**            L: mode A / mode B
    **sweep.py**             N: finite option grid → site peak
  server/                    **NEW folder** (thin transport; FastAPI drop-in later)
    **app_local.py**         local HTTP server: receives project JSON, calls a runner, returns results JSON
    **runner.py**            orchestration: JSON → resolve → engine pipeline → results JSON (pure-ish)
  ui/                        **NEW folder** (dumb form; no maths in JS)
    **pages/**               one page per JSON section (vehicles/routes/assignments/calendar)
    **static/**              JS that only collects fields + posts JSON (+ filters stop>0 for display)
  deprecated/                history only — never imported by current code
    charging_physics_engine_exponential.py
    simulate_driver_alt.py
```

Why `power_step.py` and not reusing `force_engine.py`: `force_engine` is already Bob's step I (coefficients); the step-J multiply-add is a different function. Using a new name avoids the documented 6 Oct/8 Oct naming collision (contradiction §4(2)).

---

## 3. Data contract table (per step)

Units are **SI inside engines** (`engine-rules.md` §5). Shapes: `[N]` = numpy array over the N one-second rows; `scalar`; `table[W×S]` = winds × speed columns. "Cached by" is the key the later cache layer uses (keys added after engines are correct — 6 Oct §6).

| Step | Inputs (name : unit) | Outputs (name : unit : shape) | Called by | Cached by |
|---|---|---|---|---|
| **F crosswind_engine** | vehicle_height m; v_ref m/s (list); h_ref m; a1,a2,a3 (–); wind_exp (–); dh m; dphi_deg °; v_veh_kmh km/h (list); beta_limit_deg ° or None | W1 : – : table[W×S]; W2 : m² : table[W×S] | runner (once/vehicle) | height, v_ref range, h_ref, a1–a3, wind_exp, dh, speed range, beta_limit_deg |
| **H payload_engine** | stop : s : [waypts]; shape : str; payload_start,payload_end : kg; payload_custom : kg[] | payload : kg : [waypts] (value on row0 & stop>0, NaN else) | runner (per route) | stop column, shape, start/end/custom |
| **H fill_payload** | payload : kg : [waypts] (NaN gaps) | payload : kg : [waypts] (filled; raises if row0 NaN) | runner, before G | same as payload_engine |
| **G driver_model** | waypoints (distance_m, target_speed_kmh, grade/alt, stop_s, payload_kg); vacc (Truck.vacc); dt_s s | rows: time s, distance m, speed m/s, accel m/s², grade (–/°), dt_s s, payload kg — **arrays per column [N]** (target end-state) | runner (per route/day-type) | waypoints, vacc, dt_s |
| **I force_engine** | g m/s²; Crr –; speed m/s [N]; accel m/s² [N]; dt_s s; grade [N]; r_dyn m; theta_red kg·m² | k_lin, k_roll, k_rot : W·?/kg-terms; L : m³/s³ ·s form; v_avg m/s — [N] each | runner (per route/day-type) | speed, accel, grade arrays, g, Crr, r_dyn, theta_red |
| **W weather_for_rows** | rows (needs v_avg [N]); departure_time; temps_by_hour K; winds_by_hour m/s; cdxa_table (W1,W2) | rho_rows kg/m³ [N]; cdxa_rows m² [N] | runner (per day-type×weather) | rows id, temps, winds, cdxa_table, P, R |
| **J power_step** | m kg; β –; k_lin,k_roll,k_rot [N]; rho_rows [N]; cdxa_rows [N]; L [N] | P_wheel : W : [N] | runner (per day-type×weather×mass) | m, β, coeff arrays, rho, cdxa, L |
| **P_aux p_aux** | ES,HVAC,PS,SP,Cond : W; moving : bool [N]; motor_on : bool [N] | P_aux : W : [N] | consumption / runner | aux constants, moving, motor_on |
| **consumption** | P_wheel W [N]; η –; η_regen –; P_aux W [N]; dt_s s | P_batt W [N]; kWh scalar (and per row) | runner | P_wheel, η, η_regen, P_aux, dt_s |
| **D/E calendar+group** | per-date operating?, day-type, T, wind | calendar table; group counts (day-type×weather → count) | runner | dates, day-types, weather bins |
| **L sizing** | mode; datasheet mass+kWh (A) \| glider mass, pack kWh/kg, payload (B); annual/worst-day kWh | battery kWh; (B) iterate to fixpoint | runner | mode + its inputs |
| **M charging** | sessions (arrival,departure,need); battery OCV+Ri params; charger kW; policy; site cap | SOC traces; power traces; site peak kW | runner / sweep | sessions, battery, charger, policy, site cap, prices |

> Open units to pin when the real code arrives: the exact dimensional form of `k_lin/k_roll/k_rot/L` as returned by `force_engine.py` (they already multiply to W when combined with m/ρ) — take them verbatim from the file, do not re-derive (`working-style.md`).

---

## 4. Row storage: list-of-dicts → numpy-arrays-per-column

**Target end-state (Decided, not yet done):** rows are numpy arrays per column (one array per field), so I, W, J, consumption vectorise with no Python loop (tech.md, contradiction §4(3)).

**Least-disruptive conversion point (Suggestion):** keep `DriverModel.driver_model` producing its rows as it does today, and add **one adapter at the driver-model boundary** that turns the emitted rows into a dict of numpy arrays (`{"speed": np.array([...]), ...}`) *after* the loop finishes. The driver model stays a loop (it must — each step depends on the last); everything downstream (I, W, J, consumption) consumes arrays. This changes **one** seam, not the driver model's internals, and keeps Bob's variable names.

- The driver model keeps emitting the same fields, now including `'payload'` (audit item §1.1.9).
- The adapter is where the audit's "arrays per column" lands with the smallest diff; it can live in `runner.py` or as a 3-line helper. **Suggestion** — Bob confirms where it sits.
- `force_engine.py` already accepts arrays ("All rows in one call by passing columns as arrays", payload-force §4), so no change there.

---

## 5. Keeping the local server thin (FastAPI drop-in later)

Rule (tech.md): the FastAPI swap must touch **only the transport layer, never the engine**.

- `server/runner.py` owns orchestration: it takes **project JSON**, runs resolve → pipeline, returns **results JSON**. It imports engines; it knows nothing about HTTP.
- `server/app_local.py` is a tiny HTTP shell: parse request body → `runner.run(project_json)` → write response. It is the **only** file that knows about the transport. FastAPI later is a second shell (`app_fastapi.py`) calling the **same** `runner.run` with the **same** JSON. No engine import changes.
- The JSON in and out is fixed by the contracts in §3 and §6, so both shells speak the identical contract.
- Validation (Pydantic, step B) is deliberately **not** in the engine; it arrives with FastAPI and sits in the transport shell, so the local server can run without it now.

```
UI (dumb form) ──project JSON──▶ app_local.py ──▶ runner.run(json) ──▶ engines ──▶ results JSON ──▶ UI
                                   (swap for app_fastapi.py later; runner & engines unchanged)
```

---

## 6. Design hooks that keep future items unblocked (hooks only, no features)

From product.md implications 1–10 and business-model doc. These are **shapes**, not built features.

1. **Scenario = base + change-set.** The runner accepts `{base: project_json, changes: [...]}`; with an empty change-set it runs the base. One fixed operational base + one change-set per bidder = bid comparison (implication 1). Hook: `runner.run(base, changes=None)`. No sweep/compare feature now.
2. **Operational vs equipment data separated** in the JSON: `routes` + `calendar` (operational) vs `vehicles` + `chargers` (equipment), so a bidder swaps equipment without touching the operation (implication 2). Hook: the section split in §(JSON) below; nothing enforces roles yet.
3. **Source + date metadata per input and per default.** Field shape `{value, source, date, label}` where `label ∈ {VECTO, REG, literature, HDEV ASSUMPTION}` (defaults) or a provenance string (inputs). The report reads these (implications 3/7). Hook: the field shape is defined and `defaults.py` uses the label; wiring every input to carry it is **Open/Suggestion** (requirements §2.5).
4. **Reproducible reports from (project JSON + data versions + code version).** The results JSON carries a `provenance` block `{project_hash, data_versions, code_version}` (implications 8/10). Hook: an empty-but-present `provenance` object in the results JSON; external data (prices, tariffs) lives in versioned dated files fetched outside engines (implication 8). No TCO/price feature now.

These hooks cost nothing to carry and avoid a JSON redesign later. They are not implemented as behaviour in M0–M5 beyond being present/plumbed where cheap.

### Project JSON shape (Decided sections; field detail is Suggestion where the docs don't fix it)
```jsonc
{
  "vehicles":   [ { /* equipment: group, height, CdxA, masses, battery, aux technologies */ } ],
  "chargers":   [ { /* equipment: kW, count */ } ],              // separate from vehicles (impl. 2) — Suggestion placement
  "routes":     [ { /* operational: source (vdri|typed|gps|ai), waypoints or typed summary */ } ],
  "assignments":[ { "vehicle": id, "route": id, "count": n } ],  // count for identical vehicles (Decided)
  "calendar_environment": { /* operational: per-date operating?, day-type, weather source */ },
  "provenance": { "project_hash": null, "data_versions": {}, "code_version": null }  // hook (impl. 10)
}
```
Reusable libraries are **separate files**: VDRI templates `data/cycles/standard/` (read-only); saved user routes `data/cycles/user/` as JSON (**Suggestion**, not decided); vehicle library (input-layer-and-json.md, tech.md).

---

## 7. Testing strategy

Kiro writes tests **only when Bob asks** (`working-style.md`); this is the plan for when he does.

**Unit tests per engine** (each a pure function):
- `crosswind_engine`: reproduce the verified VECTO Excel case (0.006 %); zero wind → `W1 = 1`, `W2 = 0`.
- `payload_engine`/`fill_payload`: the Decided example `stop=[0,0,1,0,0,1,0,0,1,1,1]`, linear 10→20 → `[10,nan,12,nan,nan,14,nan,nan,16,18,20]`; `fill_payload` raises if row0 is NaN; negative payload / wrong custom length / linear-with-zero-stops all raise (payload design).
- `force_engine`: the two Decided cases — `v=20,a=0,flat,Crr=0.0055 → (0,1.0791,0,4000,20)`; `v=10,a=1 → (10.5,0.56653,0,580.125,10.5)` (payload-force §4).
- `p_aux`: the three states reproduce 2938.9 / 2537 / 1937 W for the illustrative Group 5 RD config (paux §5); blank/`"---"` cell raises.
- `weather_for_rows`: ρ matches a hand value; 60–105 clamp (below-60 uses 60, interpolate within, **raise** outside); `CdxA_eff = CdxA(0)·W1 + W2`.
- `power_step`: matches a loop reference on arrays.
- `consumption`: matches a loop reference; the sign switch flips at `P_wheel = 0`.

**Property-based tests** (the ones the task names + a few more):
- **Neutral defaults reproduce the simple equation:** for random speed/accel/grade arrays, with `β=1`, `θ_red=0`, single Crr, `power_step` equals the simple-K formula (`engine-rules.md` §3).
- **`fill_payload` never leaves NaN** (given a non-NaN row0): for any `stop` pattern, output has no NaN.
- **Zero wind → `W1=1`, `W2=0`** for any vehicle height / speed grid.
- Additional: `p_aux ≥ 0`; `P_aux(moving) ≥ P_aux(stopped)` for the same config (SP only adds while moving); CdxA lookup is monotone-safe (never extrapolates — raises instead).

**VECTO reference comparisons:**
- Crosswind vs VECTO Excel (existing, 0.006 %).
- End-to-end VECTO-equivalent run (3 m/s at 4 m, constant reference payload, neutral params) vs a VECTO consumption output — **blocked** until Bob supplies a VECTO reference number and the consumption code (requirements §7.3, §6). State the tolerance when the reference exists.
- Each run's assumptions report lists every deviation used (yaw clamp, in-cycle payload, DMI wind, edited-VDRI) and the flagged gaps.

---

## Part 3 — the year / day / week problem

Source: `year-and-day-simulation-problem.md`. This is the least-settled area; below are concrete options, a resolution of its §4 inconsistencies, and one recommended option marked **Suggestion** for Bob.

### 3A. What is fixed before any option (Decided)
- Compute each quantity at the frequency it changes (year/day §2 table). Crosswind once per vehicle; 1 s rows once per route/day-type; ρ inline per row; CdxA_eff per row; `power_step`/battery per (day-type × weather × mass).
- kWh is **not** a single scaling factor: a mass/ρ change can flip a row regen↔pushing, switching the efficiency formula, so mass and ρ enter each row before the efficiency step (6 Oct §3). Wheel energy scales exactly; battery kWh does not.
- Keep each real year's daily (T, wind) series paired by date; **never average a calendar date across years**; keep the worst day as its own sizing case (year/day §2). This fixes the DRAFT DMI code, which currently averages across years and must be split into `fetch_dmi` + a pure `build_weather` (6 Oct §4, contradiction §4(9)).
- Charging is per plug-in session (arrival→next departure), SOC carries over; the fixed 21 h episode and random `reset()` are removed (year/day §3).
- No invented numbers: every bin count / step size / threshold is a labelled choice or sourced (year/day §6).
- The VECTO-equivalent case stays exactly reproducible (year/day §6).

### 3B. Three concrete options

For each: how consumption feeds charging, SOC carry-over, how annual totals / worst day / P10–P50–P90 come out, cache keys, and what must be **timed first**.

#### Option 1 — Compute every operating date directly (no grouping)
- **Consumption → charging:** for each real operating date, run G/I/W/J/consumption with that date's (T, wind) and the day's mass, giving that date's kWh and a per-session energy need. Feed the dated sequence of sessions straight into the charging simulation.
- **SOC carry-over:** natural — the charging simulation walks the real date sequence; each session starts at the previous session's ending SOC. Weekends and overnight are just longer sessions.
- **Annual totals:** sum over all operating dates. **Worst day:** the max-kWh date (already its own case). **P10/P50/P90:** percentiles over the per-date kWh distribution directly (no reconstruction).
- **Cache keys:** per date = (route/day-type id, T, wind, mass). Dates with identical (day-type, T-rounded, wind-rounded, mass) hit the same cache entry — grouping becomes an *implementation detail of the cache*, not a modelling choice.
- **Timed first:** the per-year cost of ~250 vectorised date-runs. If cheap, this is the simplest correct option and needs no bin choices. year/day §5 explicitly asks whether (a) computing every date directly beats binning.

#### Option 2 — Bin by weather (day-type × temperature × wind bins)
- **Consumption → charging:** run the pipeline once per unique (day-type × T-bin × wind-bin), multiply by how many dates fall in that bin for annual totals (year/day §2 "group").
- **SOC carry-over:** **this is the weak point** — binning throws away the real date order, so SOC cannot carry across the real sequence. Charging then needs a representative structure (Option 3) layered on top; binning alone does not give correct cross-day SOC.
- **Annual totals:** Σ (bin kWh × bin count). **Worst day:** must keep the extreme date(s) *outside* the bins (year/day §2 "worst day kept as its own case") or binning hides them. **P10/P50/P90:** percentiles over the bin distribution weighted by counts — **approximate**, resolution set by bin width.
- **Cache keys:** (day-type, T-bin, wind-bin, mass). Fewer runs than Option 1.
- **Timed first:** nothing to time for cost (it is cheaper by construction); instead the open question is **how to choose bins defensibly without inventing numbers** (year/day §5). Bin edges must be a labelled choice or sourced — there is no VECTO source for weather bins, so they are HDEV ASSUMPTION. Also: hourly weather (option C) breaks binning because almost no two days are identical (year/day §4(2)).

#### Option 3 — Hybrid: exact extremes + binned rest + representative charging weeks (Suggestion)
- **Consumption → charging:** compute the **worst day(s)** and any extreme days exactly (Option 1 style, for sizing); bin the remaining ordinary days (Option 2 style, for annual totals); and for **charging**, simulate one **representative week per temperature bin** (year/day §3 Claude suggestion: 2,016 steps at 5 min, run two weeks, keep the second so Monday starts at a realistic SOC).
- **SOC carry-over:** handled inside each representative week (7-day sequence incl. weekend); the only rollover is a real shortfall at departure (year/day §3, May-2026 "representative week not representative day"). Ending SOC ≠ starting SOC is reported as a real finding.
- **Annual totals:** binned ordinary days (Σ bin kWh × count) + exact extreme days. **Worst day:** exact, from the extreme set. **P10/P50/P90:** from the binned distribution for the bulk, with exact tails for the extremes.
- **Cache keys:** extremes keyed per date (as Option 1); bins keyed per (day-type, T-bin, wind-bin, mass); charging keyed per (T-bin, week-pattern, battery, charger, policy, site cap).
- **Timed first:** (i) the per-date cost (shared with Option 1, to know if "exact for extremes" is cheap); (ii) one representative-week charging run at 5 min (year/day §5: "is one continuous year-long run cheap enough, or representative weeks scaled up?"). "2,016 steps", "5 min", "two weeks" are the **Suggestion's** numbers from the doc — labelled Claude's suggestion, not sourced; Bob chooses.

### 3C. Consumption-days → charging-weeks hand-over (year/day §4(3))
The hand-over object (Suggestion): per plug-in session, `{arrival_time, departure_time, energy_need_kWh, arrival_SOC}`. Consumption produces `energy_need_kWh` per session (from the day's kWh split at depot returns); charging consumes the session list and produces ending SOC, which becomes the next session's `arrival_SOC`. This is the same object under all three options; what differs is whether sessions come from real dates (Opt 1), bins + representative weeks (Opt 3), or are undefined (Opt 2 alone — why Opt 2 needs Opt 3 for charging).

### 3D. Resolution of year/day §4 inconsistencies
| § | Inconsistency | Resolution |
|---|---|---|
| 4(1) | Per-date vs bins vs representative weeks don't combine into one annual number | **Resolved by choosing an option.** Opt 1 uses per-date throughout; Opt 3 defines the combination explicitly (binned bulk + exact extremes for totals/worst-day; representative weeks for charging). Opt 2 alone is **rejected** for charging (no SOC carry-over). The recommendation (3E) is one consistent story. |
| 4(2) | Hourly weather breaks binning | **Resolved as a dependency:** if hourly (option C) is chosen, binning for consumption stops working, so Option 1 (compute every date directly) is the consistent partner for hourly. Decide B vs C by timing one year both ways (year/day §2). **Open** until timed. |
| 4(3) | Consumption-days vs charging-weeks hand-over not designed | **Resolved by 3C** (the session hand-over object). **Suggestion** — Bob confirms the fields. |
| 4(4) | Monte Carlo placement | **Listed Open.** MC draws sit *above* the structure: each draw perturbs inputs (payload, coincidence) then reruns from the first changed step via the rerun table. MC suits coincidence factor / peak charging more than payload (year/day §4(4)). Not designed further here — **Open**, needs Bob. |
| 4(5) | Departure clock time missing | **Resolved as a schema hook:** add an optional `departure_time` to routes/calendar; option C and JIT/EDF need it; daily (option A) ignores it. **Open** whether to add now — tie to the B-vs-C decision. |

### 3E. Recommendation (Suggestion — Bob decides)
**Start with Option 1 (compute every operating date directly), time it, and only fall back to Option 3 (hybrid) if Option 1 is too slow for sweeps/Monte Carlo.** Reasoning:
- Option 1 is the only one that needs **no invented bin numbers** and gives correct SOC carry-over and exact percentiles for free — it best fits the "no invented numbers" and "worst day is its own case" rules (year/day §6, §2).
- It is also the consistent partner if hourly weather (option C) is later chosen, which binning cannot support (§4(2)).
- The one risk is cost; year/day §5 explicitly says to time "compute every date directly" first. If ~250 vectorised date-runs × scenarios × MC draws is too slow, Option 3 adds binning for the ordinary-day bulk while keeping extremes exact — a smaller, numbers-labelled step, not a redesign.
- Under all options the VECTO-equivalent case is a **single** day-type with declaration weather, so it is reproduced identically regardless (year/day §6).

What to **time first** (the deciding measurement, no numbers assumed): one year of per-date vectorised runs (Option 1 cost) and one representative-week charging run at 5-min steps (Option 3 charging cost). The result of these two timings picks Option 1 vs Option 3 and B vs C. This is marked **Open** pending Bob running the timing.
