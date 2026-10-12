---
inclusion: manual
---

# Status — current state of HDEV (12 Oct 2026)

Built only from the docs and code. References, not copies. Primary source: #[[file:docs/design/status-and-known-contradictions.md]].

## Reference material
- **VECTO source + resources — present.** Every file listed in #[[file:reference/vecto/ADD_THESE_FILES.md]] has been copied into `reference/vecto/` (`cs/`, `cs/declaration/`, `resources/` with `MissionCycles/`, `VACC/`, `VAUX/`) from the VECTO repo branch `stable`, commit `d16ba783c` (v5.1.3). None missing. READ-ONLY. See `vecto-grounding.md`.
- **Regulation extracts — still missing.** `reference/regulation/` holds only `ADD_THESE_FILES.md`; the Regulation (EU) 2017/2400 markdown extracts are not yet present.

## Done (verified or tested)
- **F crosswind_engine** — verified vs VECTO Excel (0.006 %). #[[file:src/engine/crosswind_engine.py]], #[[file:docs/decisions/2026-10-06_crosswind-verification.md]].
- **H payload_engine + fill_payload** — tested. #[[file:src/engine/payload_engine.py]], #[[file:docs/design/payload-stop-rows-then-fill.md]].
- **I force_engine** (per-row coefficients) — tested. #[[file:src/engine/force_engine.py]], #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §4.

## In progress
- **G driver model** — exists, under audit. #[[file:src/engine/driver_model.py]], #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §6.
- **M charging** — env + EDF/ES + JIT/ASAP exist (thesis code), with a fixed 21 h horizon and randomised reset. #[[file:src/charging/ev_charging_env.py]], #[[file:src/charging/allocators_edf_es.py]], #[[file:src/charging/flexibility_setpoints.py]], #[[file:src/charging/run_allocator_21h.py]].
- **DMI weather fetch** — DRAFT; see known contradictions. #[[file:src/data_fetch/dmi_weather_climatology.py]].

## Not started (design decided)
- **P_aux** — VECTO BEV logic fully traced; function not written; design decisions pending. #[[file:src/engine/p_aux.py]], #[[file:docs/decisions/2026-10-08_session-closeout-paux.md]].
- **W weather_for_rows** — design decided. 6 Oct §4–5, 8 Oct §5.
- **J power step** — equation decided, no separate function. 8 Oct §4.
- **consumption** — older code in Bob's notebook, not in bundle; placeholder efficiencies.
- **C resolver / typed input** — Sept version exists; payload part superseded; not in bundle.
- **defaults.py** — values collected in #[[file:docs/decisions/2026-10-07_vecto-declaration-defaults.md]].
- **L battery sizing** — modes A and B decided. 6 Oct §8.
- **Charging physics (OCV + Ri)** — decided to replace exponential taper. #[[file:src/deprecated/charging_physics_engine_exponential.py]].
- **UI step-by-step** and **local server → FastAPI** — not built. #[[file:docs/context/input-layer-and-json.md]].

## Pending decisions
- P_aux design (default technologies; blank-cell handling; function structure; whether to add non-VECTO DC/DC loss, cabin heating, charging-time aux). #[[file:docs/decisions/2026-10-08_session-closeout-paux.md]] §10.
- Weather daily vs hourly (options A/B/C) — start daily, compare before switching. #[[file:docs/design/year-and-day-simulation-problem.md]] §2.
- Year/day/week structure (per-date vs bins vs representative weeks). #[[file:docs/design/year-and-day-simulation-problem.md]] §4–5.
- Does a real VDRI end with a `stop > 0` row (affects linear payload end). #[[file:docs/design/payload-stop-rows-then-fill.md]].
- Where UI state lives between steps (browser vs server-saved). #[[file:docs/context/input-layer-and-json.md]].

## Known bugs — driver model audit (all open)
From #[[file:docs/design/status-and-known-contradictions.md]] §3 and #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §6:
- 2 red: infinite-loop risk; segment-level vs step-level acceleration.
- 2 orange: division by zero in braking distance; `vacc_lookup` can return `None`.
- 2 yellow: missing early exit; dead logic in braking distance.
- On arrival sets `speed = target_speed` and drops overshoot `ds` (speed jump without matching accel).
- Stores unclamped accel when new speed is clamped to 0 (force engine compensates by clamping v2).
- PTO stop time missing for MunicipalUtility (+23 s per PTO stop; 96 stops ≈ 36.8 min).
- Power limit at high mass not modelled (check `Driver.cs`).
- Waypoint with stop 0 but target speed 0 → brakes to 0 and pulls away.
- `'payload'` not yet added to rows.
- Grade uses flat per-segment `grade_pct`; VECTO interpolates altitude and derives grade as a secant (step-size dependent) — pending `DrivingCycleData.cs`.
- Should use VECTO's official `Truck.vacc`.

## Known contradictions
Listed in `open-design-problems.md` and in full in #[[file:docs/design/status-and-known-contradictions.md]] §4.

## Known model gaps (flag in reports; not bugs)
#[[file:docs/design/status-and-known-contradictions.md]] §5 and `vecto-grounding.md`: placeholder efficiencies; no battery internal-resistance loss while driving; no regen power cap; no cabin heating; single-Crr rolling resistance; rotating mass off; the 10° yaw clamp (non-VECTO).
