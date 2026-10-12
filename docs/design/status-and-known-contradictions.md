# Pipeline status, missing code and known contradictions (as of 12 Oct 2026)

Compiled by Claude from the close-outs, project memory, past chats and the code Bob pasted on 12 Oct. Where this file says "Claude's reading", it is an interpretation to confirm, not a decision.

## 1. Pipeline — current order (Claude's reading of the 8 Oct decisions; Bob to confirm)
```
A  Inputs (project JSON: vehicles, routes, assignments, calendar/environment)
B  Validate (Pydantic) ............................ later, with FastAPI
C  Resolve (defaults.py; typed input → waypoints) . written last
   Waypoints (VDRI rows / typed / GPS / AI)
H  payload_engine on waypoints → UI stop table → fill_payload
F  crosswind_engine (W1, W2 per vehicle; independent of route)
G  driver model (1 s rows; copies grade and payload from waypoints)
I  force_engine (k_lin, k_roll, k_rot, L, v_avg)     ← called "force_coeffs" in the 6 Oct notes
W  weather_for_rows (rho_rows, cdxa_rows; 60–105 km/h clamp lives here)
J  power step: P_wheel = m·k_lin + m^β·k_roll + k_rot + ρ·CdxA_eff·L   ← called "force_engine" in the 6 Oct notes
   P_aux (5 VECTO BEV terms, state-switched)
   consumption: battery power by sign (P/η or P·η_regen) + P_aux → kWh
D/E Calendar + group (day-type × weather) → annual totals
L  battery sizing (mode A datasheet / mode B iterate)
M  charging (plug-in sessions; ASAP/JIT setpoint; EDF/ES split; cheapest-first planned)
N  sweep (battery × charger kW × policy × site limit)
O  costs / CO₂ / report (later; COWI Excel as reference)
```

## 2. Status per step
| Step | Status | Where |
|---|---|---|
| F crosswind_engine | DONE, verified vs VECTO Excel (0.006 %) | src/engine/crosswind_engine.py |
| H payload_engine + fill_payload | DONE, tested | src/engine/payload_engine.py |
| I force_engine (coefficients) | DONE, tested | src/engine/force_engine.py |
| P_aux | VECTO logic fully traced; function not written; design decisions pending | src/engine/p_aux.py (stub), docs/decisions/2026-10-08_session-closeout-paux.md |
| G driver model | EXISTS, under audit: 6 known bugs + extra items | src/engine/driver_model.py |
| W weather_for_rows | NOT WRITTEN (design decided) | 6 Oct close-out §4–5, 8 Oct §5 |
| J power step | NOT WRITTEN as a separate function (equation decided) | 8 Oct close-out §4 |
| consumption | older code exists in Bob's notebook (not in this bundle); placeholder efficiencies 0.95/0.95/0.98; a `regen_effeiciency` typo noted 6 Oct | ask Bob |
| C resolver / typed input | Sept version (TableLeg, ResolvedDay, resolve, HTML harness) exists; payload part superseded | not in bundle — ask Bob |
| defaults.py | NOT WRITTEN (values collected in 2026-10-07_vecto-declaration-defaults.md) | — |
| DMI weather fetch | DRAFT; violates the "don't average across years" decision; needs fetch/build split | src/data_fetch/ |
| L battery sizing | NOT WRITTEN (two modes decided) | 6 Oct close-out §8 |
| M charging env + EDF/ES + JIT/ASAP | EXISTS (thesis code); 21 h episode limit; random reset; MARL legacy | src/charging/ |
| Charging physics (OCV + Ri) | DECIDED to replace exponential taper; NOT WRITTEN | src/deprecated/charging_physics_engine_exponential.py |
| UI step-by-step | NOT BUILT (design rules decided) | docs/context/input-layer-and-json.md |
| Local server → FastAPI | NOT BUILT | — |

## 3. Driver-model audit list (all Open)
- 2 red: infinite-loop risk; segment-level vs step-level acceleration.
- 2 orange: division by zero in braking distance; `vacc_lookup` can return None.
- 2 yellow: missing early exit; dead logic in braking distance.
- On arrival sets `speed = target_speed` and drops the overshoot `ds` (speed jump without matching accel).
- Stores unclamped accel when new speed is clamped to 0 (force engine clamps v2 to compensate).
- PTO stop time missing for MunicipalUtility (+23 s per PTO stop; 96 stops ≈ 36.8 min).
- Power limit at high mass (VECTO can limit acceleration) not modelled — check `Driver.cs`.
- Waypoint with stop 0 but target speed 0 → brakes to 0 and pulls away.
- `'payload'` not yet added to rows.
- Grade: `DriverModel` uses the segment's `grade_pct` (flat per segment). VECTO interpolates **altitude** linearly between waypoints and derives grade as a secant, so grade is step-size dependent. Pending `DrivingCycleData.cs` review.
- Should use VECTO's official `Truck.vacc`.

## 4. Known contradictions / ambiguities to resolve (do not pick silently)
1. **Pipeline order:** 6 Oct says G (driver) before H (payload); 8 Oct runs payload on waypoints before the driver model.
2. **Function names:** Bob's `force_engine` = the 6 Oct "force_coeffs" (step I). The 6 Oct "force_engine" (step J, the multiply-add) has no function yet.
3. **Row storage:** memory lists dataclasses `Row`, `DayType`, `Vehicle`, `Electrical` (and `Row.payload = None` to fail loudly); 6 Oct decided "rows as numpy arrays per column, not lists of Row objects"; the driver model currently returns a list of dicts.
4. **Two driver models:** `DriverModel` class (canonical per 14 April) vs `simulate_driver` variant (in src/deprecated/, contains some fixes and grade interpolation).
5. **Backend:** older memory says Flask; decided 27 Sep → FastAPI (later). Now: small local server first.
6. **Dashboard vs input UI:** dashboard prototype is a static page with no dependencies; the step-by-step input UI needs to talk to Python. How they relate is open.
7. **CdxA speed range:** 6 Oct notes say 60–100 km/h (41 columns); corrected 8 Oct to 60–105 km/h per VECTO, with the clamp in the weather step.
8. **VDRI editing:** 7 Oct "VDRI never altered, constant payload only"; 8 Oct allows editing stop durations and payload (relabelled user route; file untouched).
9. **DMI code** averages calendar days across years — decided against on 6 Oct.
10. **`v_ref`:** an earlier "v_ref conflict in the crosswind engine" was flagged as next action; DMI gives 5.028 m/s at 10 m vs VECTO 3 m/s at 4 m. Both are now arguments; confirm whether anything is still open.
11. **Year/day/week structure:** see docs/design/year-and-day-simulation-problem.md §4.

## 5. Known model gaps (flag in reports; not bugs)
- Motor/inverter/gearbox efficiencies are placeholders (0.95 / 0.95 / 0.98, Annex Xb placeholders); VECTO has a map-based path for electric machines (Annex Xb — `12b-annex-xb-electric-machine-iepc-ihpc-testing.md` in the project knowledge base, not yet read for this).
- No battery internal-resistance loss while driving; no regen power cap.
- No cabin heating (VECTO truck path has none).
- Rolling resistance single Crr (β = 1); VECTO per-axle load-dependent model is later.
- Rotating mass off (Θ_red = 0) until r_dyn and inertias are sourced.
- Crosswind yaw clamp at 10° (HDEV decision, non-VECTO, must be in every report).

## 6. Code Bob still has that is not in this bundle (ask before planning around it)
- Consumption step (with efficiencies and regen).
- The Waypoint / vacc data structures and parser feeding `DriverModel`.
- The Sept typed-input resolver (`TableLeg`, `ResolvedDay`, `resolve()`) and its HTML test harness.
- Dashboard HTML prototype.
- The Colab script that analysed the five VECTO truck `.vdri` cycles.
