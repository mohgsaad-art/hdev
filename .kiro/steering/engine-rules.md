---
inclusion: fileMatch
fileMatchPattern: "src/engine/**/*.py"
---

# Engine rules — how every engine function must be written

Applies to the pure engine functions in `src/engine/`. Source: `KIRO_PROMPT_1_STEERING.md`, #[[file:docs/decisions/2026-10-06_session-closeout-precompute-architecture.md]], #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]], #[[file:docs/decisions/2026-10-08_session-closeout-paux.md]]. These rules exist so the engine stays country-agnostic, cache-ready and VECTO-auditable.

## 1. Every parameter is an argument
- Every physics parameter — coefficients, `Crr`, `v_ref`, `h_ref`, heights, efficiencies, `g`, pressure, `r_dyn`, `theta_red`, etc. — is **passed in as an argument**. Nothing physical is hard-coded inside an engine.
- **Why:** the tool must work for any country and any vehicle. A value baked into a function cannot be swapped per scenario or recorded in the assumptions list. This is already the pattern in #[[file:src/engine/crosswind_engine.py]] and #[[file:src/engine/force_engine.py]].

## 2. Every default lives in defaults.py, labelled
- Every default value lives in **`defaults.py`** (not yet written) with its **source** and a **label**: **VECTO / REG / literature / HDEV ASSUMPTION**.
- **Why:** the assumptions list in every report must be able to state which value was used and where it came from. A default anywhere else (JS, schema, inside an engine) is untraceable. Values are collected in #[[file:docs/decisions/2026-10-07_vecto-declaration-defaults.md]].

## 3. VECTO parameters with neutral defaults
- VECTO's extra parameters are included as **arguments with neutral defaults that reduce exactly to the simpler equation** when data is missing. Examples from #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §4:
  - rolling-resistance load exponent `beta = 1` → single `Crr` (VECTO LOT 3 value is 0.9);
  - reduced rotating inertia `theta_red = 0` → no rotating-mass term.
- The force engine already does this: with `beta = 1`, `theta_red = 0` and a single `Crr`, `P_wheel` matches the old simple K (#[[file:src/engine/force_engine.py]]).
- **Why:** HDEV stays a strict superset of the simple physics. When VECTO data is absent, results fall back exactly, and the richer VECTO path is opt-in and recorded.

## 4. Variable names and comments
- Variable names **follow VECTO notation or are plain and intuitive**.
- **Never rename Bob's existing variables.** Keep his comment style (lower-case running comments, as in the current engine files).
- **Why:** continuity for the author and auditability against VECTO source.

## 5. Units
- **SI units inside engines** (m, m/s, s, kg, W, m², K). **km/h and tonnes only at the UI boundary**, converted once before calling (payload tonnes→kg; speed km/h→m/s, as the engines already do).
- **Why:** mixing units inside the physics is the classic source of silent errors; the conversion belongs at the edge.

## 6. Fail loudly — no silent defaults, no extrapolation
- Raise errors on **missing or invalid inputs**. No silent defaulting inside an engine (silent defaults happen only in the resolver, which records them).
- **Lookup tables never extrapolate** — raise an error instead. VECTO's own behaviour: below 60 km/h it uses the 60 km/h value, interpolates linearly within range, and raises on extrapolation; the CdxA speed range is 60–105 km/h (#[[file:docs/decisions/2026-10-06_crosswind-verification.md]], #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §5). Wind outside the table range → widen the range or raise, never extrapolate.
- `payload_engine` already fails loudly: negative payload, wrong custom length, and linear with zero stops all raise; `fill_payload` raises if row 0 is NaN (#[[file:src/engine/payload_engine.py]]).
- **Why:** a wrong number that is auditable is far less dangerous than a plausible number invented by a silent default or an extrapolated curve.

## 7. Purity (cache-ready)
- All inputs as arguments; return results; **no globals, no in-place mutation; same input → same output**. The allocators are explicitly written as pure functions of env state that do not mutate the env (#[[file:src/charging/allocators_edf_es.py]]).
- **Network and disk access live in separate fetch functions, never inside an engine** (see the DMI fetch/build split required in `structure.md`).
- **Why:** caching is added later keyed on all inputs; impurity breaks that and breaks reproducibility.

## 8. Non-VECTO deviations are explicit
- Any deviation from VECTO is an **optional argument, clearly labelled non-VECTO, and listed in the assumptions report** — e.g. the 10° yaw clamp `beta_limit_deg` (`None` = VECTO behaviour) in #[[file:src/engine/crosswind_engine.py]]. Full list and rules: `vecto-grounding.md`.
