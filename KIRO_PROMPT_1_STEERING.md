# Kiro prompt 1 — steering only (paste into Kiro CHAT, not Spec mode)

Do NOT write or change any code. Do NOT create a spec. Do NOT try to solve the design problems yet. Your only job in this session is to read this workspace and create steering files in `.kiro/steering/`.

## Read first, in this order
1. `README.md` — what every file in this workspace is and why it is here.
2. `docs/decisions/` — dated session close-outs. These are the source of truth for design decisions. They use tags: Decided / Open / Assumption / Suggestion, and [VECTO] [REG] [ARITH] [INFERRED] [OPEN] [DECISION PENDING]. When two files conflict, the newer date wins, and any "Bundle note" at the top of a file says what is superseded.
3. `docs/design/` — the payload design, the open year/day simulation problem, and the current status + known contradictions list.
4. `docs/context/` — product scope, input layer / project JSON / UI decisions, and what the reference Excel files are for.
5. `src/` — current code. Every file starts with a STATUS header (current / done / draft / deprecated). `src/deprecated/` is history only.
6. `reference/` — VECTO C# source, VECTO resource files, Regulation (EU) 2017/2400 extracts, and three Excel tools. READ-ONLY. Never edit anything in `reference/`. The Excel files are for later phases only.

## Project context (use for product.md — add nothing beyond this and the docs)
- Working name: HDEV. The final product name is undecided — do not use any other name.
- What it is: a physics-based, VECTO-auditable simulation engine for battery-electric vehicle fleet and depot electrification sizing, starting in Denmark. Vehicle-agnostic by design (trucks first; vans, buses, cars later).
- Target users: fleet operators, municipalities, housing associations, CPOs, OEMs. Vendor-neutral, independent analysis.
- Outputs (now → later): energy consumption, battery sizing, charger sizing and depot charging simulation (ASAP, JIT, EDF/ES; cheapest-first planned), flexibility, then TCO, CO₂ and an optimiser.
- Current scope: finish the engine and a step-by-step UI, running locally, with the project JSON handled locally.
- Out of scope now, but the design must not block them: FastAPI backend, self-serve website, an AI chatbot that fills input sections from messy uploaded data, Eloverblik/MitID data import, subscriptions.

## Tech facts (use for tech.md)
- Python, numpy, dataclasses. Pydantic validation comes later, together with FastAPI.
- Engine = pure functions. Row-wise steps are vectorised with numpy. The driver model and the charging simulation stay loops, because each step depends on the previous one.
- One project JSON with sections (vehicles, routes, assignments, calendar/environment), each with its own schema. Defaults live only in Python (`defaults.py`), never in JavaScript or as schema field defaults. The user's original project JSON is never overwritten; a scenario = base project + a small list of changes.
- UI: step-by-step flow. It is a dumb form: it only collects inputs and sends raw JSON. No maths or resolver logic in JavaScript (filtering rows for display is allowed).
- Transport now: a small local Python server on my machine — the UI posts the project JSON and gets results JSON back.
- PLANNED: FastAPI replaces that local server later, with the same JSON. Design every interface so this swap touches only the transport layer, never the engine.
- Caching comes later, after the engines are correct. Engines must already be cache-ready: all inputs as arguments, return results, no globals, no in-place mutation, same input → same output. Network and disk access live in separate fetch functions, never inside engines.

## Create these steering files
1. `product.md` (inclusion: always) — purpose, users, outputs, current scope vs out of scope, and the design implications from `docs/context/business-model-and-design-implications.md` (no prices).
2. `tech.md` (inclusion: always) — stack, local-now / FastAPI-later, JSON contract, defaults rule, caching rule, vectorisation rule.
3. `structure.md` (inclusion: always) — folder layout as it actually exists, and the pipeline: order of steps, what each step takes in and returns, and which steps are done / partly done / not started. Build it from `docs/design/status-and-known-contradictions.md`, the close-outs and the code; cite files with #[[file:...]] references instead of copying them.
4. `engine-rules.md` (inclusion: fileMatch, pattern "src/**/*.py"):
   - Every parameter (coefficients, Crr, v_ref, h_ref, heights, efficiencies, etc.) is passed in as an argument. Nothing hard-coded inside an engine, so it works for any country.
   - Every default value lives in `defaults.py` with its source and a label: VECTO / REG / literature / HDEV ASSUMPTION.
   - VECTO parameters are included as arguments with neutral defaults that reduce exactly to the simpler equation when data is missing (e.g. β = 1, Θ_red = 0).
   - Variable names follow VECTO notation or are plain and intuitive. Never rename my existing variables. Keep my comment style.
   - SI units inside engines; km/h and tonnes only at the UI boundary.
   - Fail loudly: raise errors on missing or invalid inputs. No silent defaults inside engines. Lookup tables never extrapolate — raise an error instead.
5. `vecto-grounding.md` (inclusion: always):
   - Scope: VECTO Declaration Mode, heavy and medium lorries, battery-electric.
   - Source order: VECTO C# source and resource files > Regulation 2017/2400 > VECTO documentation (the 2014 LOT3 report is diesel-era; where it differs from the repo files, the repo wins) > peer-reviewed literature > HDEV assumption.
   - Always cite the file name. Never invent a physics value or formula. If a needed VECTO file is not in `reference/`, say which file is needed and stop — do not guess.
   - Deviations from VECTO are allowed only as optional arguments, clearly labelled non-VECTO, and listed in the assumptions report. Collect the already-decided deviations from `docs/` into a table (what, why, source file). Do not add any deviation that is not in the docs.
6. `working-style.md` (inclusion: always):
   - I write the code myself. You plan, explain, review and write tests only when asked. Never edit files in `src/` unless I explicitly ask.
   - One step at a time. Do not dump full plans unless asked.
   - Plain English, short sentences, lead with the answer, define any jargon. Explain functions from scratch — do not assume I know the method.
   - Always separate verified facts (with source) from inference. Label every assumption. Never invent numbers — every suggested value must be traceable to an authentic source.
   - When you need code lines, files or VECTO source, ask for them.
7. `status.md` (inclusion: manual) — current state built only from the docs and code: done, in progress, open items, pending decisions, known bugs, known contradictions. Use #[[file:...]] references instead of copying.
8. `open-design-problems.md` (inclusion: manual) — a short index pointing to `docs/design/year-and-day-simulation-problem.md` and `docs/design/payload-stop-rows-then-fill.md`, with one line per open question. Do not answer the questions here.

## Rules for writing the steering
- State only what is in the docs, the code or this prompt. If you infer something, label it "Inferred".
- No numbers that are not in the docs or `reference/`.
- If the docs and the code disagree, do NOT pick one — list it.
- Keep each file focused on one topic. Explain why a rule exists, not just what it is.

## When done, reply with exactly these four sections
1. Files created (one line each).
2. Contradictions found: doc vs doc, and doc vs code (cite files and lines). Include any not already listed in `docs/design/status-and-known-contradictions.md`.
3. Gaps: code with no matching decision doc, and decisions with no matching code.
4. Questions for me (numbered, max 10).
