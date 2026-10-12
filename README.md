# HDEV — workspace bundle for Kiro (12 Oct 2026)

**What this is about:** HDEV (working name; final name undecided) is a physics-based, VECTO-auditable simulation tool for battery-electric fleet and depot electrification sizing, starting in Denmark — "PVsyst for EVs". It simulates a vehicle's working day second by second (driving, payload, weather, auxiliaries), turns that into energy use, then sizes batteries and chargers, simulates depot charging (ASAP, JIT, EDF/ES) and flexibility, and later TCO and CO₂. Users: fleet operators, municipalities, housing associations, CPOs, OEMs. Current goal: finish the engine and a step-by-step local UI; FastAPI, a self-serve website and an AI input chatbot come later. Full detail: `docs/context/product-and-scope.md`.

Open this folder as a Kiro workspace. Then paste `KIRO_PROMPT_1_STEERING.md` into Kiro **chat** (not Spec mode).

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
