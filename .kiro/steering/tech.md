---
inclusion: always
---

# Tech — stack, transport, JSON contract, defaults, caching, vectorisation

Source: `KIRO_PROMPT_1_STEERING.md` tech facts, #[[file:docs/context/input-layer-and-json.md]], #[[file:docs/decisions/2026-10-06_session-closeout-precompute-architecture.md]], #[[file:docs/context/product-and-scope.md]]. Anything beyond those is labelled **Inferred**.

## Stack
- **Python**, **numpy**, **dataclasses**.
- **Pydantic validation comes later**, together with FastAPI. Raw input models default to `None`; only the resolver fills values and records them.

## Transport: local now, FastAPI later
- **Now:** a small local Python server on Bob's machine. The UI posts the project JSON; it returns results JSON.
- **Planned:** FastAPI replaces that local server later, with the **same JSON**.
- **Rule:** design every interface so this swap touches **only the transport layer, never the engine**. Why: the engine must not care how the JSON arrives, so moving from a local server to FastAPI (and later a website) is a transport change, not an engine change.

## The JSON contract
- **One project JSON** with sections: `vehicles`, `routes`, `assignments` (with a `count` field for identical vehicles), `calendar/environment`. Each section has its own schema (Pydantic later). A chatbot can fill one section using that section's schema.
- Keep **operational data** (routes, calendar) separate from **equipment data** (vehicles, chargers) so equipment can be swapped without touching the operation (see `product.md`, implication 2).
- Reusable libraries are **separate files**: VDRI templates (`data/cycles/standard/`, read-only), saved user routes (`data/cycles/user/` as JSON — **Suggestion**, not decided), vehicle library.
- The user's **original project JSON is never overwritten**. A **scenario = base project + a small list of changes**. The same mechanism serves interactive edits, sweeps and Monte Carlo.
- **"Skip a step"** (e.g. a user-supplied kWh/km) is a resolver override that bypasses steps F–J and is flagged in the assumptions list.
- **Resolve is written last**: its field list comes from what the engines actually read.
- **Inferred (business doc):** each input value should carry source + date metadata, not just a value; this is not yet reflected in any schema in the bundle.

## Defaults rule
- **Defaults live only in Python, in `defaults.py`** — never in JavaScript and never as schema/Pydantic field defaults. Why: the assumptions list must know every default that was actually used, so a default hidden in JS or a schema would be untraceable.
- Each default carries a **source** or an **ASSUMPTION** label. Labels used in the docs: VECTO / REG / literature / HDEV ASSUMPTION. See `engine-rules.md` and `vecto-grounding.md`.
- `defaults.py` is **not written yet**; the values are collected in #[[file:docs/decisions/2026-10-07_vecto-declaration-defaults.md]].

## Caching rule
- Caching comes **later**, after the engines are correct. Each step's result is cached by a key built from **all** its inputs; a rerun starts at the first step whose inputs changed (rerun table in #[[file:docs/decisions/2026-10-06_session-closeout-precompute-architecture.md]] §6).
- Engines must already be **cache-ready now**: all inputs as arguments, return results, **no globals, no in-place mutation, same input → same output**.
- **Network and disk access live in separate fetch functions, never inside engines** (e.g. the DMI code must split into `fetch_dmi(...)` and a pure `build_weather(...)` — see `structure.md`).

## Vectorisation rule
- The engine is a set of **pure functions**. Row-wise steps are **vectorised with numpy** — store rows as numpy arrays per column (not lists of `Row` objects), so steps like `force_engine` (step I), weather, the power step and consumption run with no Python loop (e.g. `np.where(P>0, P/eta, P*eta_regen)`).
- The **driver model** and the **charging simulation** stay loops, because each step depends on the previous one.
- **Row storage — target end-state (Decided, not yet done):** rows are stored as **numpy arrays per column**. The driver model currently returns a **list of dicts**; converting it to arrays-per-column is agreed but **not yet implemented**. See `structure.md` and #[[file:docs/design/status-and-known-contradictions.md]] §4(3).
