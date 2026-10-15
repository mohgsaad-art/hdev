# HDEV — workspace bundle for Kiro (12 Oct 2026)

**What this is about:** HDEV (working name; final name undecided) is a physics-based, VECTO-auditable simulation tool for battery-electric fleet and depot electrification sizing, starting in Denmark — "PVsyst for EVs". It simulates a vehicle's working day second by second (driving, payload, weather, auxiliaries), turns that into energy use, then sizes batteries and chargers, simulates depot charging (ASAP, JIT, EDF/ES) and flexibility, and later TCO and CO₂. Users: fleet operators, municipalities, housing associations, CPOs, OEMs. Current goal: finish the engine and a step-by-step local UI; FastAPI, a self-serve website and an AI input chatbot come later. Full detail: `docs/context/product-and-scope.md`.

Open this folder as a Kiro workspace. Then paste `KIRO_PROMPT_1_STEERING.md` into Kiro **chat** (not Spec mode).

---

## Running the local UI (Step 2)

The local UI is a FastAPI server that serves the static shell **and** a registry-derived `/api/inputs` endpoint from one process. It binds **`127.0.0.1` only** (loopback), so it is never reachable from the network.

**One-time setup** (the global site-packages is read-only here, so a virtualenv is required):

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**One start command:**

```
make run
# equivalently:
.venv/bin/python -m hdev.app
```

Then open <http://127.0.0.1:8000/>. The port can be overridden with `HDEV_PORT` (default `8000`); the host is fixed to `127.0.0.1` and cannot be widened.

**Mode switch — `HDEV_MODE=demo|real` (default `demo`):** read once at startup and returned in `/api/inputs` as `mode` so the UI can show the demo pill.

- `demo` (default): the sample-case walkthrough with illustrative values (built in later steps).
- `real`: the real engine pipeline (wired in later steps).

```
HDEV_MODE=real make run
```

**Sections and counts are registry-driven.** All section names, subgroup names, per-section counts and the `total_inputs` header counter come from `/api/inputs`, which derives everything from the registry (`src/registry`). Nothing about the sections or any count is hard-coded in JS — the browser is a dumb client that draws only what the server sends. Per method-hiding, `/api/inputs` never emits a field's internal mapping, never names a counted-only (`collapsed`) field, and never includes hidden fields; only `open` fields expose a label.

**Tests** (offline, no network): `make test` or `.venv/bin/python -m pytest tests/ -q`.

---

## Demo intake (Step 3)

In **demo mode** the assistant walks through a sample case: a municipal refuse fleet (6 trucks, ~120 km/day, shift 06:00–15:00, Mon–Fri). The flow is:

1. **Add sample files** attaches the two illustrative sample files (`fuel_log_2025.xlsx`, `collection_routes.pdf`).
2. **Send** posts the dropped message and calls `GET /api/intake`.
3. The assistant shows **"Reading…"**, then the section cards fill in registry order with a two-colour meter (blue = from your data, amber = standard) and a per-card **"N missing"** line.
4. The assistant posts **"I found N of M inputs… K are missing"** followed by two buttons: **Use standard values** and **I'll add them myself**.

**Everything is illustrative.** The sample case lives in `demo/sample_case/` — `message.txt`, the two placeholder files (Step 3 does **not** parse them), and `extracted.json` (the machine-readable fixture). Every value is made up for the demo and labelled illustrative; `standard`-source fields are illustrative stand-ins sourced from the fixture itself, **not** the (not-yet-sourced) defaults table.

**Offline and server-driven.** `/api/intake` is **demo-mode only** (in real mode it returns `404` with `{"available": false}`), calls **no AI provider** and touches no network — it only reads `demo/sample_case/`. All counts are **registry + fixture derived, never hard-coded**: the JS client does no maths and hard-codes no section names, counts, defaults or missing count. The `missing` count, the meter widths and the header counter target are all server numbers; `total_inputs` matches `/api/inputs` (`open + collapsed`).

**`/api/intake` JSON shape** (demo mode) — the browser renders only what this sends:

```
{
  "available": true, "mode": "demo", "illustrative": true, "note": "...",
  "tool_name": "[TOOL NAME]",
  "total_inputs": int,            # equals /api/inputs total_inputs (open+collapsed)
  "found": int, "missing": int,   # registry+fixture derived, never literals
  "totals": {"from_data": int, "standard": int, "missing": int, "total": int},
  "message_text": "...", "sample_files": ["fuel_log_2025.xlsx", "collection_routes.pdf"],
  "assistant": {"opening": "...", "reading": "Reading…",
                "found_line": "I found N of M inputs… K are missing"},
  "sections": [ {"id", "display_name", "from_data", "standard", "missing", "total",
                 "fields": [ /* OPEN fields only: id,label,value,unit,source,class,illustrative */ ]} ]
}
```

Per method-hiding, `/api/intake` never emits a field's internal mapping, never names or values a `collapsed` field (collapsed fields are **counted** only), and never includes hidden fields; only `open` fields expose id + label + value.

---

## Scenario run (Step 4)

`POST /api/run` runs a scenario and returns the §3.3 results JSON. It is **demo-mode only**: in real mode it returns `404` with `{"available": false, "mode": "real", "reason": "..."}` ("Not yet available") because the real engine pipeline lands in Step 9 — the demo engine is **never** called in real mode.

In **demo mode** the server validates the submitted levers (via `src/validate`), then calls `demo/demo_engine.py` `run_scenario(project, levers)` and returns the results. **Every demo result is illustrative:** it carries `"illustrative": true` and `"mode": "demo"`, and every number is a stand-in. The formulas are ported **verbatim** from the illustrative mock-up at `docs/design/ui-mockup/fleet-assistant-demo.html` (the block marked `ILLUSTRATIVE NUMBERS ONLY`); no new formulas are invented. All logic lives in Python — the browser is a dumb client that draws only what the server sends.

**Accepted levers** (anything else, or an out-of-range value, is rejected with a `400` and a plain-language message, no results):

| Lever | Values |
|---|---|
| `fleet_size` | whole number ≥ 1 (max from the project when given) |
| `charging_priority` | `lowest_cost` \| `grid_friendly` \| `ready_earliest` |
| `electricity_price` | `low` \| `expected` \| `high` |
| `weather_year` | `normal` \| `cold_winter` |
| `ownership_years` | `8` \| `10` \| `12` |
| `operation.schedule.shift_end` | the editable shift-end time, e.g. `"18:00"` |

Per method-hiding (§8), the client-facing `charging_priority` names and every `strategies[].priority` use **only** `lowest_cost` / `grid_friendly` / `ready_earliest`; the internal strategy keys and technical names never appear in the results JSON, and the `verdict` / `plan` / `headline` text uses plain words only.

**Request body** (the levers may be nested under `"levers"` or passed at the top level; an optional `"project"` gives the fleet-size bound):

```bash
curl -s -X POST http://127.0.0.1:8000/api/run \
  -H 'Content-Type: application/json' \
  -d '{"levers": {"fleet_size": 6, "charging_priority": "lowest_cost",
                  "electricity_price": "expected", "weather_year": "normal",
                  "ownership_years": 10}}'
```

The response contains `run_id`, `timestamp`, `mode`, `illustrative`, `settings`, `verdict`, `kpis`, `energy` (monthly 12-long, per-vehicle), `charging` (SoC profile + strategy comparison), `grid` (24h load/flex), `tco` (6 categories: Owning, Running, Infrastructure, Policy & taxes, Hidden costs, Climate — plus cumulative curves and break-even year), `co2`, `plan`, and `inputs_summary` (reused from the intake tallies). The `tco_diff_dkk` KPI is **electric minus diesel** over the ownership period (negative = the electric fleet costs less in total).

**Additive §3.3 fields (Step 5): `working_days` and `truck_days_simulated`.** On top of the fields above, the results JSON now carries two extra top-level numbers: `working_days` (the working-days-per-truck count the illustrative maths already uses, 250) and `truck_days_simulated` (`fleet_size * working_days`). They exist so the run screen can read the real truck-days count from the server instead of the browser hard-coding 250. The addition is purely additive: nothing in §3.3 is removed or reordered, and both fields carry the same illustrative stand-in values as the rest of the demo payload.

---

## Results UI (Step 5)

The results UI extends the same single-page shell. Start the app and walk through the demo the same way as before:

```
make run
# equivalently:
.venv/bin/python -m hdev.app
```

Then open <http://127.0.0.1:8000/> (or the `HDEV_PORT` you set). In demo mode:

1. **Add sample files** then **Send** to post the message and run the intake fill animation (§5.3 states 1–3).
2. End the missing flow with **Use standard values** (or Send) to trigger a run.
3. The **run screen** (§5.3 state 4) ticks through nine checklist lines in order behind a progress bar, then shows the end line **"Done in X s · N truck-days simulated"**. The `X` is the real measured `/api/run` round-trip time and the `N` is the server-provided `truck_days_simulated`; the browser never computes either number itself.

**Tab bar (§5.6).** The results panel has ten tabs, in order: **Inputs, Overview, Energy, Charging, Grid & flexibility, Costs (TCO), CO₂, Scenarios, Report, Audit trail**. Fully wired now: Inputs, Overview, Energy, Charging, Grid & flexibility, Costs (TCO) and CO₂. The remaining three are shells that fill in later steps: **Scenarios** (Step 7), **Report** (Step 8) and **Audit trail** (Step 7).

**Charts are hand-drawn inline SVG.** Every chart is drawn directly from the server numbers using inline SVG. There is no chart library and no external asset: the browser only draws the values the server sends.

**Scenario bar (§5.5).** Below the results sits a scenario bar with six controls:

| Control | Choices |
|---|---|
| Trucks | slider over the fleet size |
| Charging priority | Lowest cost / Grid-friendly / Ready earliest |
| Electricity price | Low / Expected / High |
| Weather | Normal year / Cold winter |
| Ownership period | 8 / 10 / 12 years |
| Save scenario | button (stub until Step 7) |

Changing **any** control POSTs the full lever set to `/api/run` and shows a **recalculation overlay** over the results panel while the new numbers arrive; the panel redraws from the fresh response. The human labels above map to the client-facing lever values described in the Scenario run section (for example `lowest_cost` / `grid_friendly` / `ready_earliest`). **Save scenario** is a stub for now and starts working in Step 7.

As everywhere else, the browser does no maths: it only draws the numbers the server sends.

---

## Assistant (demo mode) — Step 6

In **demo mode** the assistant becomes interactive once results exist. It answers the eight suggestion buttons, typed questions, and the shift-end field edit. Everything is server-decided: the browser posts only raw text or an action identifier and renders the server's reply plus any action it returns. **The JS does no keyword matching, generates no reply text and computes no number** — all replies come from the `explain/` templates and the §4.3 number-check, and all routing/lever decisions come from the server.

**`POST /api/chat`** is **demo-mode only** (real mode returns `404` with `{"available": false, ...}`; the real LLM assistant is Step 10). It **never** calls an AI provider and touches no network.

**Request shape:**

```
{
  "message": "...",            # a raw typed question (optional)
  "action": "...",             # a suggestion-button id or "edit_field" (optional)
  "target": "operation.schedule.shift_end",   # for action == "edit_field"
  "value": "18:00",            # for action == "edit_field" (raw HH:MM)
  "levers": { ... },           # the current client-facing lever set
  "current_results": { ... }   # the current §3.3 results payload
}
```

**Response shape:**

```
{
  "reply": "...",              # the assistant text (from explain/ templates; number-checked)
  "action": {                   # optional
    "open_tab": "charging",     # a tab to open (maps 1:1 to the UI tab ids)
    "lever": { ... },           # a lever the assistant changed (echoed)
    "results": { ... },         # fresh §3.3 results after a rerun
    "expand_section": "operation",  # (Show me the inputs) open Inputs with the operation card visible
    "run_id": 7                 # the audit run number for a shift-end edit
  },
  "run_id": 7                   # mirrored for a shift-end edit
}
```

**The eight suggestion buttons** (fixed UI labels), the action id each posts, and the tab/lever each drives:

| Button label | Action id | Opens tab | Lever change |
|---|---|---|---|
| Compare charging strategies | `compare_strategies` | Charging | — (no rerun) |
| What if electricity costs more? | `price_up` | Costs (TCO) | `electricity_price = high` |
| Add 4 more trucks | `more_trucks` | Grid & flexibility | `fleet_size = base + 4` |
| Cold winter | `cold_winter` | Energy | `weather_year = cold_winter` |
| Save as scenario | `save_scenario` | Scenarios | — (persistence is Step 7) |
| Show me the inputs | `show_inputs` | Inputs | — (operation card expanded) |
| Show the audit trail | `show_audit` | Audit trail | — (full audit is Step 7) |
| Make the report | `make_report` | Report | — (export is Step 8) |

Each button posts a user bubble with its label, shows a typing-indicator bubble, posts its action id to `/api/chat`, and renders the returned reply + applies the returned action (open the tab, update the scenario bar for a changed lever, redraw the results). A lever change from the assistant is **visible** in the scenario bar: for example *Add 4 more trucks* moves the trucks slider by 4, *What if electricity costs more?* activates the **High** electricity-price segment, and *Cold winter* activates the **Cold winter** weather segment.

**Typed-question keyword router** (server-side only — the JS sends the raw text and matches nothing):

| Keywords (substring, lower-cased) | Behaviour |
|---|---|
| `strategy` / `compare` / `charg` | same as *Compare charging strategies* (open Charging, no rerun) |
| `price` / `cost` / `expens` | same as *What if electricity costs more?* |
| `truck` / `add` / `more` | same as *Add 4 more trucks* (`fleet_size + 4`) |
| `cold` / `winter` / `weather` | same as *Cold winter* |
| a method/how/why question | the method-deflection reply, no action |
| anything else | the exact unmatched-fallback reply, no action |

**Shift-end field edit.** The Inputs tab surfaces an editable shift-end `<select>` (HH:MM) in the operation input card. Changing it posts `{"action": "edit_field", "target": "operation.schedule.shift_end", "value": "<HH:MM>", ...}` to `/api/chat`. The server validates the value, reruns, updates the scenario bar and shows a reply that ends with **"Logged as run #N in the audit trail."** with a concrete `N` (also returned as `run_id`). An invalid value returns `400` with a plain-language reply (no results). **Step 7's run log aligns with this same run counter** so run numbers stay consistent across the audit trail. The browser computes nothing from the new value — it posts the raw string and renders only the server reply/action.

**`explain/` templates and the §4.3 number-check.** Every reply is built by the `explain/` templates **from the results JSON** (and the registry only for a field label); no number is computed in a template. The §4.3 number-check then scans each reply: any number that is **not** present in the current results JSON or the registry is blocked and the reply is replaced by the safe fallback template, so a drifting reply can never surface an invented figure. Per method-hiding (§8), no parameter/coefficient/formula/physics-source/internal-strategy name and no collapsed/hidden field name ever appears in a reply; charging approaches use only the three client-facing labels **Lowest cost / Grid-friendly / Ready earliest**, and the owner is referred to only as **Bob**.

**Demo mode never calls an AI provider**, and the JS does no maths or keyword logic: all of that lives in Python (`hdev/chat_api.py` + `explain/`), and the browser is a dumb client that posts raw text/action ids and draws the server's strings and actions.

---

Every file below says what it is and **why it is here**. Status words: DONE (verified/tested), CURRENT (in use), DRAFT, DEPRECATED (history only), NOT WRITTEN.

---

## Top level
| File | Intent |
|---|---|
| `README.md` | This index. Read first. |
| `KIRO_PROMPT_1_STEERING.md` | Prompt 1: Kiro builds steering files only. No code, no spec. |

## `src/` — Bob's current code (pasted 12 Oct 2026)
Each file starts with a STATUS header. Notebook cells were split into files; imports may be missing.

| File | Status | Intent |
|---|---|---|
| `src/engine/crosswind_engine.py` | DONE, verified vs VECTO (0.006 %) | Step F. W1/W2 tables for effective drag area by wind × vehicle speed. Has the 10° yaw clamp argument (HDEV decision). |
| `src/engine/payload_engine.py` | DONE, tested | Step H. Writes payload on start + stop waypoints; `fill_payload` forward-fills before the driver model. |
| `src/engine/force_engine.py` | DONE, tested | Step I. Mass-, temperature- and drag-independent per-row coefficients (k_lin, k_roll, k_rot, L, v_avg). |
| `src/engine/p_aux.py` | NOT WRITTEN (stub) | Auxiliary power. VECTO logic fully traced in the P_aux close-out. |
| `src/engine/driver_model.py` | CURRENT, under audit | Step G. `DriverModel` class → 1 s rows. 6 known bugs + extra audit items. |
| `src/charging/ev_charging_env.py` | CURRENT (thesis) | Gym-style depot charging env (physics only). MARL parts are legacy. |
| `src/charging/flexibility_setpoints.py` | CURRENT | JIT / ASAP site setpoints + import/export feasibility (flexibility headroom). |
| `src/charging/allocators_edf_es.py` | CURRENT | EDF and equal-share splitting of the site target between vehicles. |
| `src/charging/run_allocator_21h.py` | CURRENT | Runner + plots. Fixed 21 h horizon = known limitation. |
| `src/charging/tester_21h_maddpg.py` | THESIS legacy | Tester using MADDPG; kept for helpers and plots. |
| `src/data_fetch/dmi_weather_climatology.py` | DRAFT | DMI daily wind + temperature. Conflicts with the "don't average across years" decision. |
| `src/data_fetch/dmi_wind_plot_old.py` | OLD | Earlier wind-only exploration script. |
| `src/deprecated/charging_physics_engine_exponential.py` | DEPRECATED | Exponential CC-CV taper; to be replaced by VECTO OCV + Ri model. |
| `src/deprecated/simulate_driver_alt.py` | ALTERNATIVE / older | A variant of the earlier VECTO driver port. Bob to confirm; useful to compare fixes during the audit. |

Code that exists but is NOT in this bundle (listed in `docs/design/status-and-known-contradictions.md` §6): consumption step, Waypoint/vacc parser for `DriverModel`, Sept typed-input resolver + HTML harness, dashboard HTML, VDRI analysis script.

## `docs/decisions/` — dated close-outs (source of truth; newer wins)
| File | Intent |
|---|---|
| `2026-10-06_session-closeout-precompute-architecture.md` | The pipeline A→O, force/consumption maths, weather options (daily/hourly), lookup tables, caching, input JSON, charging per plug-in session. |
| `2026-10-06_crosswind-verification.md` | How the crosswind engine was verified against VECTO; the 10° yaw-clamp decision and its report wording. |
| `2026-10-07_vecto-declaration-defaults.md` | Sourced VECTO values for `defaults.py`: payloads, heights, crosswind coefficient sets, CdxA defaults, body/trailer masses. |
| `2026-10-07_session-closeout-crosswind-payload.md` | Crosswind done; VECTO mission-cycle analysis. Its payload section is SUPERSEDED (see note in file). |
| `2026-10-08_session-closeout-payload-force.md` | Final payload design, force engine, PTO stop time, weather-step notes, driver-model audit additions. |
| `2026-10-08_session-closeout-paux.md` | Full VECTO trace of BEV auxiliary power (5 terms, tables, rules, gaps, pending decisions). |

Not included: `payload-resolver-design-2026-10-07.md` (fully superseded by 8 Oct).

## `docs/design/` — written for Kiro (12 Oct)
| File | Intent |
|---|---|
| `payload-stop-rows-then-fill.md` | The payload idea: decide payload on stop points only, then inflate to every second. Why, rules, tests, open items, where we want a second opinion. |
| `year-and-day-simulation-problem.md` | The open problem: day → week → year with hourly weather, SOC carry-over, grouping/day-types, charging weeks. What is decided, what conflicts, questions for outside ideas, hard constraints. |
| `status-and-known-contradictions.md` | Pipeline order, status per step, driver-model audit list, known contradictions, model gaps, missing code. |

## `docs/context/` — background
| File | Intent |
|---|---|
| `product-and-scope.md` | What HDEV is, users, outputs, roadmap, current scope vs later (FastAPI, website, AI chatbot input). |
| `input-layer-and-json.md` | Four route inputs, Sept typed resolver (partly superseded), project JSON sections, defaults-in-Python rule, dumb-form UI rules. |
| `business-model-and-design-implications.md` | Who uses HDEV (incl. tender creation, bidder technical-fit, bid comparison) and what that means for the data design now. No prices. |
| `tco-and-reference-excels.md` | What each reference Excel contains, what is sourced vs unsourced, and which later phase it serves. |

## `reference/` — read-only sources
| Path | Intent |
|---|---|
| `reference/excel/eltiltrucks-beregner-ark.xlsx` | COWI electric-truck TCO/LCA calculator. Template for the later TCO/CO₂ phase. |
| `reference/excel/Elindsigt2.2.xlsx` | Eloverblik consumption/bill tool. Reference for later coincidence-factor work. |
| `reference/excel/ChargePointCalculator_v5.xlsx` | Municipal charge-point demand calculator. Validation reference only. |
| `reference/vecto/ADD_THESE_FILES.md` | List of VECTO C# and resource files to add (not bundled). |
| `reference/regulation/ADD_THESE_FILES.md` | List of regulation/VECTO-methodology markdown extracts to add from the claude.ai project. |

Tip: if the Excel files or the large PDF slow Kiro down, list them in `.kiroignore`.
