---
inclusion: always
---

# Structure — folder layout and the pipeline

Built from #[[file:docs/design/status-and-known-contradictions.md]], the dated close-outs and the code. Files are cited, not copied. "Inferred" marks anything not stated in a doc or the code.

## Folder layout (as it actually exists)
```
hdev/
  README.md                         index of the whole bundle
  KIRO_PROMPT_1_STEERING.md         the steering-build prompt
  docs/
    decisions/                      dated session close-outs (source of truth; newer wins)
    design/                         payload design, year/day problem, status + contradictions
    context/                        product scope, input layer/JSON, business model, reference Excels
  reference/                        READ-ONLY. Never edit.
    excel/                          3 Excel tools (later TCO/CO2/coincidence phases)
    vecto/                          VECTO C# + resource files (PRESENT; cs/, cs/declaration/, resources/)
    regulation/ADD_THESE_FILES.md   Reg. 2017/2400 + methodology extracts to add (NOT yet present)
  src/
    engine/
      crosswind_engine.py           step F
      payload_engine.py             step H (payload_engine + fill_payload)
      force_engine.py               step I (per-row coefficients)
      p_aux.py                      P_aux (stub, not written)
      driver_model.py               step G (DriverModel class)
    charging/
      ev_charging_env.py            gym-style depot env (physics only)
      flexibility_setpoints.py      JIT/ASAP setpoints + import/export feasibility
      allocators_edf_es.py          EDF + equal-share site-target split
      run_allocator_21h.py          runner + plots (fixed 21 h horizon)
      tester_21h_maddpg.py          thesis MADDPG tester (legacy; kept for helpers/plots)
    data_fetch/
      dmi_weather_climatology.py    DMI daily wind + temp (DRAFT; see contradictions)
      dmi_wind_plot_old.py          older wind-only script
    deprecated/                     history only, never used as current
      charging_physics_engine_exponential.py
      simulate_driver_alt.py
```
`reference/vecto/` now holds the VECTO source and resources (copied from branch `stable`, commit `d16ba783c`, v5.1.3 — in `cs/`, `cs/declaration/`, `resources/`). `reference/regulation/` still holds **only** `ADD_THESE_FILES.md` — the regulation extracts are **still missing** (see `vecto-grounding.md`).

## The pipeline (order, inputs → outputs, status)
Order per the 8 Oct decisions in #[[file:docs/design/status-and-known-contradictions.md]] §1 — **Decided**: payload runs on the waypoints before the driver model. Letters are the step labels from the close-outs.

```
A  Inputs (project JSON: vehicles, routes, assignments, calendar/environment)
B  Validate (Pydantic) ............................ later, with FastAPI
C  Resolve (defaults.py; typed input -> waypoints) . written last
   Waypoints (VDRI rows / typed / GPS / AI)
H  payload_engine on waypoints -> UI stop table -> fill_payload
F  crosswind_engine (W1, W2 per vehicle; independent of route)
G  driver model (1 s rows; copies grade and payload from waypoints)
I  force_engine (k_lin, k_roll, k_rot, L, v_avg)   [6 Oct notes call this "force_coeffs"]
W  weather_for_rows (rho_rows, cdxa_rows; 60-105 km/h clamp lives here)
J  power_step: P_wheel = m*k_lin + m^beta*k_roll + k_rot + rho*CdxA_eff*L  [name = power_step; 6 Oct notes called this "force_engine"]
   P_aux (5 VECTO BEV terms, state-switched)
   consumption: battery power by sign (P/eta or P*eta_regen) + P_aux -> kWh
D/E Calendar + group (day-type x weather) -> annual totals
L  battery sizing (mode A datasheet / mode B iterate)
M  charging (plug-in sessions; ASAP/JIT setpoint; EDF/ES split; cheapest-first planned)
N  sweep (battery x charger kW x policy x site limit)
O  costs / CO2 / report (later; COWI Excel as reference)
```

Where things enter the pipeline: **weather enters at W, mass enters at J.** Everything above W is computed once and reused (#[[file:docs/decisions/2026-10-06_session-closeout-precompute-architecture.md]] §2).

## What each written step takes in and returns
- **F `crosswind_engine`** — #[[file:src/engine/crosswind_engine.py]]. In: `vehicle_height, v_ref, h_ref, a1, a2, a3, wind_exp, dh, dphi_deg, v_veh_kmh, beta_limit_deg`. Out: `W1, W2` tables (rows = wind speeds, columns = vehicle speeds). `CdxA_eff = CdxA(0)*W1 + W2`.
- **H `payload_engine` + `fill_payload`** — #[[file:src/engine/payload_engine.py]]. `payload_engine(stop, shape, payload_start, payload_end, payload_custom)` → payload column (value on row 0 and stop rows, NaN elsewhere). `fill_payload(payload)` forward-fills; raises if row 0 is NaN. Design: #[[file:docs/design/payload-stop-rows-then-fill.md]].
- **G `driver_model`** — #[[file:src/engine/driver_model.py]]. `DriverModel(waypoints).driver_model(vacc, dt_s=1.0)` → row set `{time, distance, speed, accel, grade, dt_s}`. Payload column **not yet added**. **Row storage:** currently a list of dicts; the agreed **target end-state is numpy arrays per column** (one array per field) so the row-wise steps (I, W, J=`power_step`, consumption) vectorise. That conversion is **not yet done**. See `tech.md` and #[[file:docs/design/status-and-known-contradictions.md]] §4(3).
- **I `force_engine`** — #[[file:src/engine/force_engine.py]]. In: `g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red`. Out: `k_lin, k_roll, k_rot, L, v_avg`. Neutral defaults (`beta=1`, `theta_red=0`) reproduce the simple equation.
- **M charging** — env #[[file:src/charging/ev_charging_env.py]] (physics only); setpoints #[[file:src/charging/flexibility_setpoints.py]] (JIT/ASAP + feasibility); allocators #[[file:src/charging/allocators_edf_es.py]] (EDF, ES split); runner #[[file:src/charging/run_allocator_21h.py]].

## Status per step
From #[[file:docs/design/status-and-known-contradictions.md]] §2.

| Step | Status | Where |
|---|---|---|
| F crosswind_engine | **DONE**, verified vs VECTO Excel (0.006 %) | #[[file:src/engine/crosswind_engine.py]] |
| H payload_engine + fill_payload | **DONE**, tested | #[[file:src/engine/payload_engine.py]] |
| I force_engine (coefficients) | **DONE**, tested | #[[file:src/engine/force_engine.py]] |
| P_aux | VECTO logic fully traced; **function not written**; design decisions pending | #[[file:src/engine/p_aux.py]], #[[file:docs/decisions/2026-10-08_session-closeout-paux.md]] |
| G driver model | **EXISTS, under audit**: 6 known bugs + extra items | #[[file:src/engine/driver_model.py]] |
| W weather_for_rows | **NOT WRITTEN** (design decided) | 6 Oct §4–5, 8 Oct §5 |
| J `power_step` | **NOT WRITTEN** as a separate function (equation decided) | 8 Oct §4 |
| consumption | older code exists in Bob's notebook (not in bundle); placeholder efficiencies 0.95/0.95/0.98; `regen_effeiciency` typo noted | ask Bob |
| C resolver / typed input | Sept version exists; payload part superseded | not in bundle — ask Bob |
| defaults.py | **NOT WRITTEN** (values collected in the 7 Oct defaults doc) | #[[file:docs/decisions/2026-10-07_vecto-declaration-defaults.md]] |
| DMI weather fetch | **DRAFT**; violates "don't average across years"; needs fetch/build split | #[[file:src/data_fetch/dmi_weather_climatology.py]] |
| L battery sizing | **NOT WRITTEN** (two modes decided) | 6 Oct §8 |
| M charging env + EDF/ES + JIT/ASAP | **EXISTS** (thesis code); 21 h episode limit; random reset; MARL legacy | #[[file:src/charging/]] |
| Charging physics (OCV + Ri) | DECIDED to replace exponential taper; **NOT WRITTEN** | #[[file:src/deprecated/charging_physics_engine_exponential.py]] |
| UI step-by-step | **NOT BUILT** (design rules decided) | #[[file:docs/context/input-layer-and-json.md]] |
| Local server → FastAPI | **NOT BUILT** | — |

## Code that exists but is NOT in this bundle
Ask before planning around it (#[[file:docs/design/status-and-known-contradictions.md]] §6): the consumption step; the Waypoint/vacc data structures and parser feeding `DriverModel`; the Sept typed-input resolver (`TableLeg`, `ResolvedDay`, `resolve()`) + HTML harness; the dashboard HTML prototype; the Colab script that analysed the five VECTO `.vdri` cycles.
