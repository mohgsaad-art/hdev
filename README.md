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

**Tab bar (§5.6).** The results panel has ten tabs, in order: **Inputs, Overview, Energy, Charging, Grid & flexibility, Costs (TCO), CO₂, Scenarios, Report, Audit trail**. All ten are wired now: Inputs, Overview, Energy, Charging, Grid & flexibility, Costs (TCO) and CO₂ in Step 5; **Scenarios** and **Audit trail** in Step 7; and **Report** in Step 8 (its two Download buttons call `/api/report`).

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
| Save as scenario | `save_scenario` | Scenarios | — (persists via `/api/scenarios`, Step 7) |
| Show me the inputs | `show_inputs` | Inputs | — (operation card expanded) |
| Show the audit trail | `show_audit` | Audit trail | — (counts-only source table + run log, Step 7) |
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

## Scenarios, audit trail & run log — Step 7

Step 7 adds a **server-side project store**, saved **scenarios**, the counts-only **audit trail** source table and the append-only **run log**, all behind thin FastAPI routes over pure chokepoints. As always the JS client is dumb: it renders only server JSON, does no maths and hard-codes no counts/names/numbers.

### Project store (runtime JSON, gitignored)

The mutable project state (the monotonic run counter, the append-only run log, and the saved scenarios) is persisted to **one JSON file on a gitignored runtime path**:

- Default location: **`.hdev_runtime/project.json`** (under the repo root; `.hdev_runtime/` is gitignored, so the populated file is **never committed**).
- Override with the env var **`HDEV_PROJECT_STORE`** (an absolute path, or a path relative to the repo root).
- It is **runtime-only, disposable state** — writes are atomic (temp file + `os.replace`), the directory is created lazily on first write, and in **demo mode each fresh app launch resets it** so a new session starts with run numbering at **1** and an empty run log/scenarios list. (This is what lets each `TestClient(create_app())` test start clean.)

### Unified run counter

There is **one** monotonic run number `N`, owned by `hdev/run_api.build_run_payload`. **Every** genuine demo run — a scenario-bar `/api/run`, an assistant rerun button, and the shift-end field edit — allocates exactly one `N` from the project store and appends exactly one run-log entry. The shift-edit reply ("Logged as run #N in the audit trail.") simply **reads back** the number the run returned, so there is a single increasing sequence with **no double-counting**. Quote-only reruns (used to source a number for a no-rerun reply) pass `log_run=False` and neither consume a number nor append an entry. Every successful `/api/run` now also returns `results["run_number"]` (the audit `N`) alongside the deterministic string `results["run_id"]` hash.

### `GET` / `POST /api/scenarios` (save · list · compare)

Demo-mode only (real mode returns `404 {"available": false, ...}`).

- **`POST /api/scenarios`** — save the current run as a named scenario. Body: `{"name": "...", "results": <current §3.3 results>}` (or `{"name": "...", "run_id": <N>}`). When a `results` body is sent, the saved scenario's `run_id` is read from `results["run_number"]` so it matches the run log — **send the whole current results payload** so the two line up.
  Response: `{"ok": true, "scenario": <row>}`.
- **`GET /api/scenarios`** — the saved-scenarios table with the mock-up columns:
  `{"scenarios": [{name, run_id, settings: {trucks, charging_approach, electricity_price, weather}, battery_kwh, depot_peak_kw, tco_saving_dkk, co2_saved_t_per_year}], "count": N}`. All names are **client-facing** (`Lowest cost` / `Grid-friendly` / `Ready earliest`, `Normal year` / `Cold winter`, `Low` / `Expected` / `High`) — never an internal lever key.
- **`POST /api/scenarios/compare`** — a §4.2 side-by-side diff. Body `{"names": [...]}` or `{"run_ids": [...]}`; with **no** ids/names it compares **all** saved scenarios. Response: `{"scenarios": [rows], "diff": [{field, values: [...], same: bool}], "count": N}`.

The **Save scenario** button in the scenario bar and the assistant **Save as scenario** action both persist through this endpoint and then refresh the Scenarios table.

### `GET /api/audit` (source counts + run log)

Demo-mode only (real mode returns `404 {"available": false, ...}`). Response:

```
{
  "available": true,
  "mode": "demo",
  "source_table": {
    "rows": [ {"source_type": "fuel_log_2025.xlsx", "count": 7, "status": "From your files"}, ... ],
    "total": 106
  },
  "note": "Every value can be changed. Changes are logged with who and when.",
  "run_log": [ <§3.4 entries, newest-first> ]
}
```

**Counts-only, never field names (§8).** The "Where every input came from" table lists **source types and counts only** — one row per file name, plus *Your message*, *Standard Danish values* and *Missing* — each with a plain-word status. The client computes **no total** (the `total` is a server number) and **no registry field id or label ever appears** anywhere in the audit payload. (`tests/test_scenarios_audit.py` proves this by iterating every registry field id and label and asserting none appears in the audit JSON.)

### §3.4 run-log entry shape

Each run-log entry is:

```
{
  "run_id": N,                       # the audit run number (monotonic)
  "timestamp": "<ISO>",             # deterministic in demo (from the results)
  "settings_summary": {              # client-facing names + plain words
    "trucks", "charging_approach", "electricity_price", "weather", "years_kept", "shift_end"
  },
  "changed_from_previous": [ {"field", "from", "to"}, ... ],   # plain-word diff vs the previous run ([] for the first)
  "key_result_summary": {            # the four Scenarios KPIs
    "battery_kwh", "depot_peak_kw", "tco_saving_dkk", "co2_saved_t_per_year"
  },
  "mode": "demo",
  "engine_version": "demo"           # stub constant; the real engine version lands in Step 9
}
```

`charging_approach` uses the client-facing labels **Lowest cost / Grid-friendly / Ready earliest**; no internal lever key or method/parameter name ever appears.

### Demo acceptance & the Playwright test

Two Step-7 tests cover the whole flow:

- **`tests/test_demo_acceptance_flow.py`** — a fully **offline** `TestClient` drive of the entire path (inputs → intake → use standard values → run → every suggestion button → shift edit → save scenario → audit → report), asserting no error and `illustrative: true` throughout. This is the browser-free guarantee and always runs.
- **`tests/test_demo_acceptance_playwright.py`** — a real headless-Chromium **click-through** of the same flow (add sample files, send, use standard values, click each suggestion button, change the shift-end select, Save scenario, open Audit, open Report), asserting the **"illustrative values"** pill stays visible and no uncaught page error.

**Running the Playwright test.** It is **optional** and auto-skips when the browser is absent, so the core suite stays green without it. To run it:

```bash
.venv/bin/pip install playwright
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest tests/test_demo_acceptance_playwright.py -q
```

The skip-guard lives **inside** the test module: `pytest.importorskip("playwright.sync_api")` skips if playwright is not installed, and the browser launch is wrapped so a missing browser binary (or any launch error) becomes a `pytest.skip`, never a failure. The core suite never imports playwright at collection time, and `playwright` is **not** a core `requirements.txt` dependency (it is listed there only as a commented optional note).

---

## Report export (Step 8)

The Report tab builds a full report **server-side** and hands the browser a file to save. The JS does no maths and assembles no report content: it POSTs the current results and the server returns the finished bytes.

### `GET` / `POST /api/report?format=pdf|excel`

- `format=pdf` returns a PDF; `format=excel` maps to `xlsx` server-side.
- The two formats return their own Content-Types:
  - PDF: `application/pdf`
  - Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Each response carries `Content-Disposition: attachment; filename=hdev-report.pdf` (or `hdev-report.xlsx`).
- An unknown `?format=` returns `400` with `{"ok": false, ...}`.
- `POST` accepts a JSON body `{"results": <the §3.3 results payload>, "levers": {...}}`. The Report tab POSTs the results it already holds, so the report matches what is on screen. When no `results` are sent the server runs a fresh default demo scenario (and does **not** consume a run number or write to the audit log).

The browser trigger is a plain `fetch` → `response.blob()` → object URL → a temporary `<a download=...>` click → `URL.revokeObjectURL`. The filename is read from the `Content-Disposition` header when present, else it falls back to `hdev-report.pdf` / `hdev-report.xlsx`. The buttons do nothing until a run exists.

### Libraries

- **PDF: `reportlab`** (pure Python, runs fully offline in-sandbox).
- **Excel: `openpyxl`** (pure Python, runs fully offline in-sandbox).

Both are pinned in `requirements.txt` and install offline. Neither needs any system library, so both the PDF render and the Excel build run offline in the sandbox.

### The 9 sections (both formats, in order)

Both the PDF and the Excel contain all nine §5.6 sections, in this exact order:

1. Summary
2. Your fleet & inputs
3. Energy
4. Charging
5. Grid & flexibility
6. Total cost
7. CO₂
8. Plan
9. Inputs & sources

In the PDF each section is a block of pages; in the Excel each section is its own named sheet. Every number is read from the results JSON / audit data. When a value is null or absent the report prints the literal **"Not yet available"** and never invents a number.

### Demo watermark

In demo mode the report is illustrative, so it carries the exact watermark text **"Illustrative values - sample case"** on **every** PDF page and on **every** Excel sheet. Real mode omits the watermark.

### Inputs & sources (§8 rule)

Section 9 lists the **source types and counts** (plus the server total) and the **open fields by name** with their values and source. It **never** names a `collapsed` or `hidden` field: those fields contribute to the counts only, and neither their id, their label nor their value ever appears. This is enforced by a programmatic §8 guard in `report/builder.py` that scans the assembled section content against every registry field id and label.

### Real-mode degradation

In real mode the endpoint does not 404: it still returns a report, but with `illustrative=False` (no watermark) and every unavailable field reading **"Not yet available"** until the real engine pipeline lands in Step 9.

---

## Engine functions (Step 9)

Step 9 builds the §6 engine functions behind the demo surface and wires **real mode** to a real pipeline. Every engine function is **pure**: every physics parameter is an argument, there is no hard-coded constant, and no engine does any I/O, disk or network. The neutral VECTO defaults reduce the equations to their simple form (`beta=1`, `theta_red=0`). Functions fail loudly on missing or invalid input, and lookup tables never extrapolate (they raise). SI units live inside the engines; km/h and tonnes only at the UI edge. Where a value has no source it is left `None` and **flagged**, never invented. The real-mode results keep the **same** client-facing names and plain words as demo (method-hiding, §8): engine-internal names (coefficients, formula names, physics/VECTO source names, charging-strategy names, per-row intermediate values) never reach a client surface.

### The engine pipeline A → O

The pipeline is the Decided-8-Oct order from `.kiro/specs/hdev-master-plan/design.md` §1. Payload runs on the waypoints **before** the driver model. "Precompute" is everything above the weather stage, computed once and reused; weather enters at W and mass enters at J.

| Stage | What it does |
|---|---|
| **A - Inputs** | the project JSON: vehicles, routes, assignments (count), calendar / environment (equipment and operational data kept separate) |
| **B - Validate** | Pydantic validation (lands later, with FastAPI) |
| **C - Resolve** | `defaults.py` plus a typed / GPS / AI resolver turns inputs into waypoints `{distance_m, target_speed_kmh, grade, stop_s, payload}` |
| **H - Payload** | `payload_engine` writes payload on the start and stop rows, then `fill_payload` forward-fills so every waypoint has a payload |
| **F - Crosswind** | `crosswind_engine` builds the W1 / W2 effective-drag tables (winds x 60-105 km/h), once per vehicle, route-independent |
| **G - Driver model** | `driver_model` expands the waypoints into one-second rows `{time, distance, speed, accel, grade, dt_s, payload}`; this is the list-of-dicts -> numpy per-column conversion point |
| **I - Force** | `force_engine` gives the mass-, temperature- and drag-independent per-row coefficients `k_lin, k_roll, k_rot, L, v_avg` |
| **W - Weather** | `weather_for_rows` builds `rho_rows` (air density inline) and `cdxa_rows` (`CdxA_eff = CdxA(0)*W1 + W2`), clamping 60-105 km/h and raising on extrapolation |
| **J - Power step** | `P_wheel = m*k_lin + m^beta*k_roll + k_rot + rho*CdxA_eff*L`, with `m = vehicle + body + payload` |
| **Consumption** | battery power by sign (`P_batt = P_wheel/eta` when driving, `P_wheel*eta_regen` when regenerating) plus `P_aux`, summed over `dt` to kWh per row and per day |
| **D/E - Calendar / Group** | one row per date (operating?, day-type, temperature, wind), then group unique day-type x weather bins into annual totals (consumption does not read the calendar) |
| **L - Battery sizing** | mode A (datasheet, no loop) or mode B (glider + kWh/kg + payload, iterate) |
| **M - Charging** | per plug-in session (arrival -> next departure); OCV + Ri battery; setpoint; EDF / equal-share split of the site target; the site cap couples vehicles and SOC carries over |
| **N - Sweep** | battery x charger kW x policy x site limit over finite real lists, skipping impossible combinations |
| **O - Costs / CO₂ / report** | TCO category sums, CO₂, and the assumptions report (defaults, deviations, gaps) |

### Per-function status (§6 items 1 → 20)

Status words: **WRITTEN with tests** (pure function, VECTO or hand-checked tests); **STUB blocked-by-&lt;item&gt;** (interface only, raises `NotImplementedError("blocked by <item>")`, surfaces as `null`); **WRAPPED-existing** (a pure function over existing thesis logic); **ALREADY-DONE-at-app-layer** (built in an earlier step).

| §6 item | File | Status |
|---|---|---|
| 1. Waypoint + `.vacc` parser | `src/resolver/waypoint_parser.py` | WRITTEN with tests |
| 2. `defaults.py` | `src/resolver/defaults.py` | WRITTEN with tests (CdxA default left empty + flagged, 🔒 M1.1) |
| 3. Typed-input resolver | `src/resolver/resolve_typed.py` | WRITTEN with tests |
| 4. Driver model audit | `src/engine/driver_model.py` | WRITTEN with tests (fixes listed below; grade handling 🔒 M0.12, untouched) |
| 5. `weather_for_rows` | `src/engine/weather_for_rows.py` | WRITTEN with tests |
| 6. Power step | `src/engine/power_step.py` | WRITTEN with tests |
| 7. `p_aux` | `src/engine/p_aux.py` | WRITTEN with tests (weather-on-aux layer is a STUB until the W/°C source arrives) |
| 8. Consumption | `src/engine/consumption.py` | WRITTEN with tests (HDEV placeholder efficiencies `0.95 / 0.95 / 0.98` flagged, 🔒 M0.21) |
| 9. Calendar expand | `src/resolver/calendar.py` | WRITTEN with tests |
| 10. Session hand-over | `src/resolver/session_handover.py` | WRITTEN with tests |
| 11. Battery sizing | `src/charging/sizing.py` | WRITTEN with tests (mode A full; mode B structure, source-flagged 🔒 M3.2) |
| 12. AI waypoint adapter | `src/resolver/ai_waypoint_adapter.py` | STUB blocked (map provider not chosen) |
| 13. Charging sizing + simulation | `src/charging/charging_sim.py` + `src/charging/battery_ocv_ri.py` | WRITTEN with tests (`dt` required, no default; cheapest-first price series flagged 🔒 M3.8) |
| 14. Year-long depot run | `src/charging/year_depot_run.py` | WRITTEN with tests (pure wrapper; adaptation planned in `docs/design/year-depot-run-adaptation.md`) |
| 15. `runner.run(base, changes)` | `src/server/runner.py` | WRITTEN with tests |
| 16. Flexibility per-hour | `src/charging/flexibility.py` | WRAPPED-existing (pure function over `flexibility_setpoints`) |
| 17. TCO | `src/server/tco.py` | WRITTEN with tests (data model + category sums only; coefficients to-be-sourced 🔒 M6.24) |
| 18. CO₂ | `src/server/co2.py` | STUB blocked-by-M6.25 |
| 19. `explain/` templates | `explain/templates.py` | ALREADY-DONE-at-app-layer (Step 6) |
| 20. `audit/` source tracking + run log | `audit/sources.py` + `audit/run_log.py` | ALREADY-DONE-at-app-layer (Step 7) |

**Driver model fixes (item 4).** The audit fixed the known bugs in `driver_model.py` and listed each fix in its commit; grade handling is **🔒 M0.12** and was left exactly as Bob wrote it and flagged, never rewritten silently.

### Live vs stubbed

**Live** (real numbers flow end to end): the resolver (items 1-3), the row pipeline (driver model, force, weather, power step, p_aux, consumption - items 4-8), calendar and session hand-over (items 9-10), battery sizing mode A (item 11), charging sizing + simulation (item 13), the year depot run (item 14), the runner (item 15), flexibility (item 16), and the TCO category sums (item 17, with coefficient slots empty).

**Stubbed** (interface present, returns `null` so the UI shows **"Not yet available"**): the AI waypoint adapter (item 12), battery sizing mode B's unsourced parts (item 11, 🔒 M3.2), the weather-on-aux layer inside `p_aux` (item 7), the TCO coefficients (item 17, 🔒 M6.24), and CO₂ (item 18, 🔒 M6.25).

### How to run real mode

Real mode is selected with the `HDEV_MODE` env var, read once at startup:

```
HDEV_MODE=real make run
# equivalently:
HDEV_MODE=real .venv/bin/python -m hdev.app
```

In real mode `POST /api/run` with a project base calls `runner.run(base, changes)` and returns the real **§3.3-shaped** results - the same client-facing shape the demo emits. `runner.run` selects the start stage from what changed and reruns only the downstream stages. A stage that is still a stub returns `null` fields, and the UI renders **"Not yet available"** for those. If the entry contract is incomplete, the run is **refused** with a plain-worded message that lists the missing project inputs (for example `vehicles`, `routes`, `calendar_environment`); no partial results are returned. **Demo mode is unchanged** - `HDEV_MODE=demo` (the default) still runs the illustrative sample case through `demo/demo_engine.py` and never touches the real pipeline.

### HDEV placeholder efficiencies (the consumption flag)

Consumption converts wheel power to battery kWh using three efficiencies - drive `0.95`, regen `0.95`, and auxiliary `0.98`. These are **HDEV placeholders with no VECTO equivalent**: VECTO has no single matching number, so HDEV supplies its own until a sourced value exists. They are passed as **explicit arguments** (never hard-coded in the engine), and every result that used them carries `placeholder_efficiencies=True` together with the message **"contains HDEV placeholder efficiencies (no VECTO equivalent)"**, so no efficiency-derived number is ever presented as if it were sourced. This is 🔒 M0.21: the structure is in place and flagged, the sourced value is pending.

### 🔒 Locked items touched, and how each was handled

Per the engine rules a locked item is **never decided**: it gets an interface plus a stub or an explicit flag, and where it surfaces to the UI the field is `null` so the UI shows "Not yet available".

| Item | How it was handled |
|---|---|
| **M0.12** - driver-model grade handling | left exactly as Bob wrote it, untouched, and flagged in the audit; no other fix changed grade behaviour |
| **M0.21** - consumption efficiencies | placeholder structure built, the three values passed as explicit arguments and flagged with `placeholder_efficiencies=True` (see above) |
| **M1.1** - CdxA default | `defaults.py` leaves the CdxA default **empty** and flagged; no number invented |
| **M2.6** - session hand-over object | the `{arrival, departure, energy_need_kWh, arrival_SOC}` object was written per the master-prompt "decided" note; `tasks.md` still marks it 🔒, which is recorded as a deviation to confirm |
| **M3.2** - battery sizing mode B | mode A is full; mode B's unsourced parts are a structure only, source-flagged, returning `null` where unsourced |
| **M3.8** - charging `dt` and price series | `dt` is a **required** argument with no default (the value must come from Energinet specs); the cheapest-first price series is flagged, pending a sourced price input |
| **M6.24** - TCO coefficients | the data model and category sums exist; every coefficient is a to-be-sourced `None` slot, surfaced as "Not yet available" |
| **M6.25** - CO₂ | interface + stub raising `NotImplementedError("blocked by M6.25")` |
| **M5.6** - full VECTO reference run | Bob's off-sandbox job (VECTO cannot build in the sandbox); tests use captured reference numbers where present (for example crosswind `0.006 %` and p_aux `2938.9 / 2537 / 1937 W`) and otherwise hand-checked cases with the arithmetic written into the test |

### Note for Step 10 (the real AI assistant)

The real AI assistant will consume **the real §3.3 results JSON plus the `explain/` templates**. As in demo mode (§4.3), the assistant rephrases the template text with the LLM but takes **numbers only from the results JSON** - it never computes a figure and the §4.3 number-check still blocks any number that is not in the current results or registry. So Step 9's job for the assistant is done once real mode returns a §3.3 payload: Step 10 swaps the LLM in behind the same templates and the same number guard.

---

## Real AI assistant (Step 10)

Step 10 wires the real-mode assistant behind the same `/api/chat` chokepoint the demo uses. There is **one provider interface** (`ai/provider.py`) with **two interchangeable backends**, chosen by a single environment variable. Copy `.env.example` to `.env` at the repo root and fill in your values. The real `.env` is **gitignored** and must never be committed (a real key is a secret); only `.env.example` (placeholders only) is tracked.

**Switch backends with one line, no code change:**

```bash
AI_PROVIDER=gemini   # Google Gemini Developer API, free tier (default)
AI_PROVIDER=ollama   # a local, fully offline model
```

### Gemini (default backend)

- Get a free key from Google AI Studio and put it in `.env` as `GEMINI_API_KEY` (placeholder in `.env.example`). The key is sent in the `x-goog-api-key` request header only; it is never logged, printed, or placed in a URL or an error message.
- The model name is set by `GEMINI_MODEL` in `.env`. The default is **`gemini-2.0-flash`**, a Flash model that was on the Gemini free tier at build time. Change this line if Google renames or retires the free-tier Flash model.

### Ollama (local, offline backend)

- Set `OLLAMA_URL` (default `http://127.0.0.1:11434`) and `OLLAMA_MODEL` (for example `llama3.1`) in `.env`. Ollama runs on your machine, so nothing leaves it: it is the private, offline option.
- Ollama needs a local daemon running. If it is not reachable the assistant returns a clear "Ollama is not reachable" message (no key is involved).

### The data guard (free-tier Gemini)

The Gemini **free tier** may use the inputs it receives to improve Google's products. So every project carries a `client_data` flag (**default `true`**: a project is assumed to hold a client's data until told otherwise). Before any outbound call the server runs a hard, server-side guard:

- The server **refuses** to send a project with `client_data: true` to the **`gemini`** backend **unless** `ALLOW_CLIENT_DATA_ON_FREE_TIER=true` **or** `GEMINI_PAID=true` is set.
- `ollama` is **always allowed** (it is local, so nothing leaves the machine).
- When refused, no provider call is made. The UI shows the reason and suggests switching to `ollama` to keep the project's data local.
- Set `GEMINI_PAID=true` when you move to a paid Gemini key (the paid tier does not train on inputs); it lifts the guard. `ALLOW_CLIENT_DATA_ON_FREE_TIER=true` lifts it on the free tier if you accept the terms.

### Tools, methods, and numbers

- The assistant may only call the seven §4.2 tools (`run_scenario`, `compare_runs`, `save_scenario`, `build_report`, `set_inputs`, `ask_missing`, `apply_standard`). Each is wired to an existing server chokepoint and **validated server-side**: the LLM only chooses the tool and fills the arguments, and Python validates and executes it (a bad lever or patch, or an unknown tool, is rejected). If a backend lacks native tool calling, the model answers with a strict JSON schema that is validated in Python.
- All §4.3 rules apply in real mode too: **numbers come only from the results JSON**, the assistant explains **results, not methods** (a how/why/method question returns the exact line "That's the engineering side. The results and every input source are in the report."), and the §4.3 number-check plus an §8 term denylist run on the model's final reply. Any drifting number or forbidden method/physics/strategy term falls back to the safe template text.

### Demo mode and CI

- **Demo mode needs no key and no internet and never calls any AI provider.** The demo `/api/chat` path imports no provider; the provider is only reached through the lazily-imported real path.
- **Tests use a `FakeProvider`**, so **no real API call runs in CI** and no socket is opened. The whole real-mode flow (data guard, tool loop, output guards, error paths) is driven offline with scripted replies.

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
