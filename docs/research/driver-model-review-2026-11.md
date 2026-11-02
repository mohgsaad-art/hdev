# Driver-model review — audit, tests, VECTO comparison, research

**Owner:** Bob. **Repo:** `mohgsaad-art/hdev`. **Date:** 2 November 2026.
**Author:** Kiro (AI). **Scope:** the "code of record" driver model (Appendix 1 of
the job prompt), copied verbatim to `tests/driver_model/reference_copy.py`.

**VECTO version read for the audit:** v5.1.3, stable branch, commit
`d16ba783c1d8af0ea68797f5d7ed6cf01877d402`. No `5.1.6` tag exists in
`mohgsaad-art/VECTO` (tags checked: none above `milestones/2.2`; the `stable` branch
HEAD is the v5.1.3 merge). The prompt named `d16ba783c` as the fallback, and the
local `reference/vecto/cs/` copies are **byte-identical** to this commit for
`DefaultDriverStrategy.cs`, `DistanceBasedDrivingCycle.cs`, `Constants.cs` and
`DeclarationData.cs` (verified with `diff`). **Bob's `.vmod` runs used 5.1.6**, which
was not available to read — every line number below is v5.1.3 and must be
re-confirmed against 5.1.6 before any client-facing claim. The constants that were
checkable (Appendix 2) all matched; nothing suggests the driver logic changed, but
this is **not proven** for 5.1.6.

Tag key: `[VECTO]` read in VECTO source (file + lines + v5.1.3); `[REG]` regulation;
`[SOURCE]` external doc; `[CALC]` my arithmetic from sourced inputs; `[TEST]` a test I
ran; `[ASSUMPTION]` an HDEV choice with no source; `[SIMPLIFICATION]` a deliberate
simplification; `[OPEN]` unresolved.

---

## 0. Summary (read this first)

### What is right (matches VECTO, confirmed from source)
- `interp1`, `decel_distance`, `coast_distance` are faithful re-implementations of
  their VECTO counterparts. `decel_distance` matches VECTO's exact segment integral
  term-for-term, including the clamp-to-table behaviour above the top `.vacc` point
  `[VECTO][TEST]`.
- The decision-factor tables (`df_vtarget`, `df_vdrop`) and the constants
  `df_offset=2.5`, `df_scaling=1.5`, `lac_dist_factor=10`, `lac_min_v=50`,
  `os_min_v=50`, `os_allowed=2.5`, `brake_margin=0.1`, `v_min_coast=5`, `rho=1.188`
  are **exactly** VECTO's declaration values `[VECTO]`.
- Altitude-from-grade, the first-waypoint 1 s stop rule, the start speed, the
  `DoCoast` speed cap `max(target, v)`, and the energy mass
  `TotalMass + ReducedMassWheels` all match VECTO `[VECTO]`.
- **Q3 is settled:** VECTO does **not** apply `atan` in the coasting rolling term; it
  uses `cos(rise/run)` with rise/run treated directly as a radian. The code of record
  does the same. The proposed "atan fix" (D4) would make HDEV *deviate* from VECTO
  `[VECTO]`.

### What is wrong or deviates (ranked by measured/known effect)
1. **`g = 9.81` vs VECTO `9.80665`** — a flat ~0.034 % bias on every rolling, slope
   and coasting force. Trivially fixable, sourced, zero-risk. `[VECTO]`
2. **Coasting at a fixed reference mass / CdxA, no wind** — the largest *assumption*.
   Measured "wrong-mass trace" braking-energy error up to **+8.4 % (Regional, full
   load)** and **+17.7 % (LongHaul, full load)** on the ILLUSTRATIVE vehicle `[TEST]`.
   Traction-energy error stays ≤ 1.7 %. **Decision for Bob**, numbers provided.
3. **Instantaneous air drag in `coast_acc`** vs VECTO's step-average — known small
   energy leftover; not re-measured against VECTO (BLOCKED). `[SIMPLIFICATION]`
4. **Mode mapping to VECTO `DriverAction` is now verified** and is *not* identity:
   HDEV mode 2 (cruise) has no VECTO code, and VECTO splits free-rolling into
   `Coast` (4) and `Roll` (2) which HDEV folds into mode 3. Any coast-share
   comparison must use this mapping. `[VECTO]`
5. **New finding:** on steep downhills (−6.9 %, −7.5 % on Construction) the coast
   acceleration can exceed the `.vacc` accel limit (2 rows measured). This matches
   VECTO (free-rolling Coast is not limited by the driver accel curve) but is worth
   recording. `[TEST][VECTO]`
6. **Back-to-back stops:** HDEV aims for the next *positive* target; VECTO aims for
   the *immediate* next waypoint's target (which may be 0). Confirmed from source.
   `[VECTO]`
7. **Repo mismatch:** `src/engine/driver_model.py` in the repo is the **old pre-21-Oct
   class-based model** (no coasting, no overspeed, flat grade) — completely different
   from the code of record. See A.0.

### Biggest open items
- All VECTO `.vmod` comparisons (Parts D, most of E, F's VECTO side) are **BLOCKED**:
  no `.vmod`/`.vsum`, no harness v1.7, no std-drag add-on, no E2 component files were
  supplied. See the BLOCKED list at the end.
- Whether Regulation (EU) 2025/258 changed the driver model specifically `[OPEN]`.

### Proposed changes, ranked (detail in §"Proposed changes")
| # | Change | Source tag | Measured effect | Engine or parser? |
|---|---|---|---|---|
| P1 | `g = 9.80665` | `[VECTO]` | ~0.034 % force bias removed | engine arg / parser default |
| P2 | step-average air drag in `coast_acc` | `[VECTO]` D6 | small; BLOCKED vs VECTO | engine |
| P3 | drivetrain coasting-drag table (replace scalar `P_drag_loss`) | `[REG]`/`[VECTO]` | BLOCKED (needs D2/D3) | parser builds table, engine consumes |
| P4 | reconsider fixed-mass assumption | `[ASSUMPTION]` | up to +17.7 % braking-energy error | design call (Bob) |
| — | `atan` in `coast_distance` (D4) | — | **do NOT** — deviates from VECTO | — |

---

## Part A — line-by-line audit

### A.0 Code of record vs the repo's `src/engine/driver_model.py`

**The two are different programs.** `src/engine/driver_model.py` is a class
`DriverModel` with methods `get_breaking_distance`, `vacc_lookup`, `driver_model`.
It has **no** look-ahead coasting, **no** overspeed, copies the **flat waypoint grade**
onto each row (not the altitude secant), emits **dict rows**, and documents six
different known bugs (its own F1–F5 fixes). The code of record (Appendix 1) is a
**functional** `driver_model(...)` with full look-ahead coasting + overspeed, altitude
interpolation, and tuple-array output. Verdict: the repo file is the **old pre-21-Oct
version**; Appendix 1 is newer and canonical. **This file is stale and should be
replaced by the code of record** (flagged; not done — Kiro must not edit engine code).

### A.1 Hard-coded numbers that are not arguments (engine-purity rule)

| Literal | Where | What it is | Keep in engine? |
|---|---|---|---|
| `3.6` | km/h↔m/s everywhere | unit conversion | yes (pure maths constant) |
| `1e-6` | `s >= s_end - 1e-6`, `rem > 1e-6`, stop snap | numerical tolerance | yes (tolerance) |
| `1e-9` | `mode = 3 if a >= ca - 1e-9`, `v < target - 1e-9` | numerical tolerance | yes (tolerance) |
| `0.5` | `max_steps = ... /0.5`, `ds=(v+v_new)/2` | loop guard / trapezoid avg | guard = HDEV choice; avg = maths |
| `10000` | `max_steps` padding | loop guard (HDEV) | HDEV choice, fine |
| `1.2` | `look = max(..., 1.2*decel_distance+...)` | **VECTO constant** `1.2 * stopDistance` | `[VECTO]` GetNextDrivingAction line 672 — matches |
| `2 * v * dt` | `look`, `rem < 2*v*dt` | **VECTO** `2*ds` lower bound | `[VECTO]` line 672 — matches |
| `100` | `gr/100`, `grade*100` | grade % ↔ ratio | yes (maths) |
| `1.0` | first-waypoint stop | **VECTO** 1 s rule | `[VECTO]` DrivingCycleDataReader ~220 |

Everything that is a *physical* VECTO constant (`1.2`, `2*ds`, the 1 s stop) is
sourced and correct. The remaining literals are tolerances or loop guards, which are
legitimately internal to a pure function (they are not physical inputs). **No
hard-coded number needs to move to the parser.** The only purity nit: the `0.5` in
`max_steps` encodes an assumption ("the truck averages > 0.5 m/s"); it is a guard, not
physics, so it is acceptable, but a route that genuinely averages slower would raise
the `RuntimeError` guard. `[ASSUMPTION]`

### A.2 Answers to Q1–Q13

**Q1 — `ComputeCoastingDistance` (VECTO `DefaultDriverStrategy.cs` 741–779).**
VECTO formula, term by term, and HDEV's `coast_distance`:

| Term | VECTO | HDEV `coast_distance` | Verdict |
|---|---|---|---|
| mass for energy | `TotalMass + ReducedMassWheels` (line 751) | `coast_mass + m_red_wheels` | **MATCH** |
| rotor/gearbox inertia in energy mass | **not** added (only reduced wheels) | not added | **MATCH** |
| energy difference | `currentKE − KEatTarget`, KE = m·g·h + m·v²/2 | same | **MATCH** |
| air drag | `AirDragResistance(v, targetSpeed)` → average form (Vehicle.cs) | `rho/8·CdA·(v1+v2)(v1²+v2²)/v_avg` | **MATCH** (step-average form) |
| CdA read at | average of v and target (AverageAirDragPowerLoss) | `interp1(v_avg, ...)` | **MATCH** |
| rolling resistance | `RollingResistance(rise/run as radian)` = `cos(rise/run)·m·g·Crr` | `cos(grad)·coast_mass·g·Crr`, `grad=rise/run` | **MATCH** (see Q3) |
| rolling mass | total vehicle mass (no reduced wheels) | `coast_mass` (no reduced wheels) | **MATCH** |
| drivetrain loss | `(gbxLoss + axleLoss + emDrag − iceDrag)/v` (lines 762–766) | scalar `P_drag_loss / v` | **DEVIATION (flagged 1.2d/4)** |
| decision factor | `LookAheadDecisionFactor.Lookup(targetSpeed_incl_overspeed, v − targetSpeed)` | `df_offset − df_scaling·f(v_t)·f(v−v_t)` | **MATCH** (see Q2) |
| final | `energyDiff / (DF · resistForce)` | same | **MATCH** |

The only substantive difference is the **drivetrain loss term**: VECTO computes it
from the actual gearbox + axle + electric-motor drag maps at the operating point and
divides by speed; HDEV uses a single scalar `P_drag_loss` (default 0). This is the
agreed-but-not-yet-done drag-table change (1.1a). `[VECTO]`

**Q2 — Decision-factor tables.** Read from
`VectoCore/Resources/Declaration/LAC-DF-Vtarget.csv` and `LAC-DF-Vdrop.csv` (v5.1.3):

```
LAC-DF-Vtarget.csv:  (0, 0) (48, 0) (52, 1) (100, 1)   [km/h, factor]
LAC-DF-Vdrop.csv:    (-100, 1) (9, 1) (11, 0) (100, 0)  [km/h, factor]
```

HDEV defaults `df_vtarget=((0,48,52,100),(0,0,1,1))` and
`df_vdrop=((-100,9,11,100),(1,1,0,0))` are **EXACT**. `df_offset=2.5`,
`df_scaling=1.5` match `DeclarationData.cs` lines 787–788. VECTO looks the factor up
with the **overspeed-adjusted** target speed (ComputeCoastingDistance lines 744–746);
HDEV passes `v_target` which is already the overspeed-adjusted `vt` in the look-ahead
call. **MATCH.** Units: both tables are in km/h; HDEV converts `v_target*3.6` and
`(v−v_target)*3.6` before the lookup. **MATCH.** `[VECTO]`

**Q3 — Slope in rolling resistance. SETTLED.** `Vehicle.RollingResistance(Radian
gradient)` (`Vehicle.cs` line 278) returns `Math.Cos(gradient.Value())·m·g·Crr`. In
`ComputeCoastingDistance` the gradient passed in is
`((targetAltitude − vehicleAltitude)/(targetDistance − currentDistance)).Value().SI<Radian>()`
— i.e. **rise/run treated directly as radians, no `atan`** (lines 757–759). So VECTO
uses `cos(rise/run)`, and HDEV's `coast_distance` uses `math.cos(grad)` with
`grad = rise/run` — **identical**. Verdict: **MATCH**. The earlier note claiming VECTO
applies `atan` is **wrong**; the note claiming it does not is **right**.
Numeric size of the (rejected) atan change in the rolling term `[CALC][TEST]`:

| grade | `cos(g)` (VECTO) | `cos(atan(g))` (rejected) | relative diff |
|---|---|---|---|
| 2 % | 0.999800 | 0.999800 | 2.0e-7 |
| 6 % | 0.998201 | 0.998205 | 3.6e-6 |
| 10 % | 0.995004 | 0.995037 | 3.3e-5 |

The difference is < 0.004 % even at 10 %. (`coast_acc`, a *different* function, does
use `atan` — see Q8.)

**Q4 — Look-ahead (`GetNextDrivingAction` 668–703).** Distance:
`max(2·ds, v_kmh·10, 1.2·stopDistance + ds)` (lines 671–672) — HDEV `look` is
identical. Change points: VECTO scans every look-ahead cycle entry whose target
speed (incl. overspeed, line 680–682) is **below** current speed (lines 683–685);
HDEV pre-filters to `chg` waypoints where the target drops and applies the same
`vt >= v: continue`. When several slowdowns are in range: VECTO orders candidates by
`BrakingStartDistance` and by `CoastingStartDistance`, takes the braking action
**unless** the earliest coasting action has the same `TriggerDistance`, in which case
it takes the coasting action (lines 697–701). HDEV's `best_b`/`best_c`/`coast_ok`
reproduces this: `coast_ok = best_c[0]==i and c_start < b_start`. **MATCH** in intent.
`CheckSwitchingToBraking`: HDEV's `b_new < b_cur` switch stands in for VECTO's
`SetNextDrivingAction`/`DoHandleRequest` nearer-action logic (lines 614–620, 334–343).
**MATCH (approximate — see 1 s timing, Part F).** `[VECTO]`

**Q5 — Coasting phase.** `DoCoast` (lines 1457+) requests
`DrivingActionCoast(..., Max(targetVelocity, VehicleSpeed), ...)` — HDEV cap
`(max(target, v) − v)/dt` **MATCHES**. Coasting harder than `.vacc` dec → VECTO gets
an `Underload`/`SpeedLimitExceeded` response and switches to `Brake`; HDEV clamps
`a = max(a, dec_max)` and relabels mode 4. **MATCH in effect.** Below
`MinVelocityForCoast` (5 km/h): `DoBrake` sets `targetDistance = TriggerDistance`
(brake straight to the point, line 1302); HDEV guards coasting with `v >= v_min_c`.
**MATCH.** `[VECTO]`

**Q6 — Overspeed / `FirstAccelerateOrCoast` (1114–1223).** VECTO: if overspeed is
allowed and `VehicleSpeed >= targetVelocity`, it tries `Coast`; if the coast response
decelerates and would drop below target, it `Accelerate`s at target (lines 1131–1137,
the `[DMD.FAOC-2]` branch); for a BEV an `Overload` also leads to `Accelerate`
(`[DMD.FAOC-4]`). HDEV's overspeed branch: `ca >= 0` (downhill) → roll up to
`v_os = target+2.5` then hold (mode 3/4); `v + ca·dt > target` → roll down (mode 3);
else hold target (mode 2). This captures the **outcome** of VECTO's response chain
but via kinematics, not VECTO's iterative powertrain search. **DEVIATION
(approximation, already flagged 1.2b).** VECTO's real logic is a multi-branch
Coast→Underload→Brake/Accelerate search (HandleRequestEngaged, 977–1095); HDEV cannot
reproduce the per-branch powertrain responses without a powertrain model. `[VECTO]`

**Q7 — Braking phase.** `DoBrake` (1285+) brakes to `BrakeTrigger.NextTargetSpeed`
with `targetDistance = TriggerDistance − BrakingSafetyMargin` when the next target is
0 (lines 1305–1307). `AdaptDecelerationToTargetDistance`: VECTO shortens the step to
land exactly on the point; HDEV's last-steps formula `a = (v_t² − v²)/(2·rem)` is the
constant-acceleration kinematic equivalent of landing on `v_t` over the remaining
distance `rem`. **MATCH in intent**, but on a fixed 1 s step it can exceed `.vacc`
(the ~1.78× artefact — see Part F). `TargetSpeedReachedDriveAlong` (1631+): drive
along at target — HDEV mode 2 branch `0 < v <= v_t`. **MATCH.** Braking safety margin
0.1 m matches. `[VECTO]`

**Q8 — Coasting acceleration in a BEV coast step.** VECTO forces acting during a
Coast (clutch closed): air drag (step average), rolling, slope, wheel inertia (via
`ReducedMassWheels` in the inertia), **electric-motor drag curve**
(`CalculateElectricMotorDragLoss`, DefaultDriverStrategy 779–787; `ElectricMotor.cs`
drag), motor **rotor inertia reflected through the gears**, and gearbox + axle loss
maps at ~zero torque. HDEV's `coast_acc` includes air drag (instantaneous, not
average), rolling (`cos(atan)`), slope (`sin(atan)`), and a scalar `P_drag_loss`.
**Missing / different in `coast_acc`:** (a) step-average air drag → **D6 / P2**;
(b) electric-motor drag curve + gearbox/axle loss maps → the drag table (P3);
(c) rotor inertia reflected through the gears in the effective mass → **D7**.
Note `coast_acc` uses `atan(grade/100)` for the slope angle, which is the
geometrically exact angle and differs very slightly from VECTO's raw-ratio treatment
in the *main* Vehicle.cs resistance (Q3). This is an internal HDEV inconsistency
(exact angle in `coast_acc`, raw ratio in `coast_distance`) — tiny in magnitude
(< 0.004 % at 10 %) but worth noting. `[VECTO][OPEN: not measured vs VECTO — BLOCKED]`

**Q9 — Acceleration limits beyond `.vacc`.** VECTO limits acceleration by the motor
full-load torque/power through the powertrain operating-point search: an `Accelerate`
request that the motor cannot meet returns `ResponseOverload`, and the driver falls
back to a lower acceleration (HandleRequestEngaged). For the E2 BEV with 2×125 kW this
happens at low speed / high load. HDEV has an **optional** `P_max` cap (a crude
`P_max/v − F_res` limit), off by default, and the comment flags it as "not VECTO's
motor search". Whether the E2 `.vmod` shows motor-limited rows is **BLOCKED** (no
`.vmod`). **DEVIATION (simplification, flagged 1.2 / known #2 of the old model).**
`[VECTO]`

**Q10 — Cycle handling.** Altitude from grade: `altitude += (dist_i − dist_{i-1})·
grade_{i-1}/100` (`DrivingCycleDataReader.cs` line 236) — HDEV `rise = diff(s_wp)·
gr_wp[:-1]/100`. **MATCH.** First-waypoint 1 s stop (line ~220): **MATCH.** Target
after a stop (lines 246–253): VECTO duplicates the stop entry with
`VehicleTargetSpeed = entries[i+1].VehicleTargetSpeed` (the *immediate* next entry) —
HDEV takes the next *positive* target. **DEVIATION (new wording — see Q-note &
deviation register).** Start speed: `DistanceBasedDrivingCycle.cs` starts at the first
entry's target (HDEV `v = v_wp[0]`). **MATCH.** Step slope from altitude: VECTO's
per-step gradient is the altitude secant over the step — HDEV recomputes `grade` from
`alt` in Part C the same way. **MATCH.** `[VECTO]`

**Q11 — Stop handling & the ~1 s standing-time difference.** VECTO lands on a stop by
shortening the step so the vehicle reaches v=0 exactly at the trigger distance, then
holds for `StoppingTime`. Its 1 Hz `.vmod` output is produced by averaging the
simulation over each 1-second window; the seconds in which the truck *decelerates to
rest* and *pulls away* are partially-moving windows that VECTO's 1 Hz averaging counts
differently from HDEV, which snaps v=0 and emits exactly `round(stop/dt)` standing
rows. HDEV's standing rows equal the cycle stop times **exactly** (Regional 746 s,
Urban 3349 s `[TEST]`); the prompt reports VECTO 736 / 3245 s, i.e. HDEV is ~10/~104 s
higher, ≈ +1 s per stop region. **Root cause (from source + arithmetic, not
guessed):** HDEV counts the whole stop duration as discrete standing rows, whereas
VECTO's 1 Hz modal output blends the fractional first/last stopped second into the
adjacent moving window — so VECTO reports slightly fewer *fully-standing* 1 Hz rows.
Confirming the exact per-stop figure needs the `.vmod` (**BLOCKED**). `[VECTO][TEST]`

**Q12 — DriverAction codes.** Enum `DrivingAction` (`Driver.cs` line 50, v5.1.3):
`Halt = 0`, `Roll = 2`, `Coast = 4`, `Accelerate = 6`, `Brake = −5`. The behaviour
enum `DrivingBehavior` (`IDriverInfo.cs` line 37): `Halted, Accelerating, Driving,
Coasting, Braking`. **Verified mapping to HDEV modes:**

| HDEV mode | VECTO DriverAction | Notes |
|---|---|---|
| 0 stop | `Halt` (0) | match |
| 1 accelerate | `Accelerate` (6) | match |
| 2 cruise | **no direct code** | VECTO holds speed via Accelerate/Brake at the target; HDEV has a dedicated cruise mode |
| 3 coast | `Coast` (4) **and** `Roll` (2) | HDEV folds both; `Roll` = clutch open (free), `Coast` = clutch closed (drivetrain drag) |
| 4 brake | `Brake` (−5) | match |

**VECTO actions with no HDEV equivalent:** `Roll` (distinct from `Coast`), and
brake-to-standstill / `Halt`-transition sub-behaviours. **The earlier assumed
mapping was therefore incomplete**: a VECTO coast-share must sum `Coast` + `Roll`,
and HDEV's cruise (mode 2) rows map onto VECTO Accelerate/Brake-hold rows. This is a
likely contributor to the coast-share gap in 2.2 (hypothesis h3). `[VECTO]`

**Q13 — Constants.** All checkable against Appendix 2:

| Constant | VECTO v5.1.3 | file:line | HDEV | Verdict |
|---|---|---|---|---|
| gravity | 9.80665 | DeclarationData.cs **74** | 9.81 | **MISMATCH** (prompt said line 72 — it is 74) |
| air density | 1.188 | DeclarationData.cs **76** | 1.188 | MATCH |
| MinVelocityForCoast | 5 km/h | Constants.cs **305** | 5 | MATCH (prompt said 301 — it is 305) |
| BrakingSafetyMargin | 0.1 m | DefaultDriverStrategy.cs 60 | 0.1 | MATCH |
| LookAheadDistanceFactor | 10 | DeclarationData.cs 789 | 10 | MATCH |
| LAC MinimumSpeed | 50 km/h | DeclarationData.cs 790 | 50 | MATCH |
| Overspeed MinSpeed | 50 km/h | DeclarationData.cs (OverSpeed) | 50 | MATCH |
| AllowedOverSpeed | 2.5 km/h | DeclarationData.cs 796 | 2.5 | MATCH |
| DF offset / scaling | 2.5 / 1.5 | DeclarationData.cs 787–788 | 2.5 / 1.5 | MATCH |
| LowerBoundTimeInterval | 0.25 s | Constants.cs 291 | (n/a — HDEV fixed dt) | — |
| DriverActionDistanceTolerance | 0.25 m | Constants.cs 329 | (n/a) | — |

**Declaration mode turns LAC + overspeed on for the E2:** confirmed in the generic
job `BEV_E2.vecto` (`OverSpeedEcoRoll: {Mode: Overspeed, MinSpeed: 50, OverSpeed:
2.5}`). Two line-number corrections to the prompt's notes: gravity is **line 74** (not
72) and MinVelocityForCoast is **Constants.cs line 305** (not 301). `[VECTO]`

---

## Part B — helper unit tests (`tests/driver_model/test_helpers.py`)

25 tests, **all passing** `[TEST]`. Run: `pytest tests/driver_model/test_helpers.py`.

- **`interp1`** — matches `np.interp` on 200 random points; both ends held; exact
  knot values; repeated x values (no div/0 when querying inside a segment); single
  segment. All pass.
- **`decel_distance`**
  - vs a fine numerical integration of `v/|a(v)|` over Truck.vacc + 2 synthetic
    curves (relative error < 0.2 %): pass.
  - vs an independent Python re-implementation of VECTO's
    `ComputeAccelerationSegmentDistance` within the table (relative error < 1e-6):
    pass — **the two formulas are the same maths**.
  - edge cases: `v_to ≥ v_from` → 0; constant-dec segment → closed form; equal
    adjacent `vacc_v` (zero-width segment) → skipped, no div/0; `v_from` below first
    point → finite. All pass.
  - **`v_from` above the last `.vacc` point:** `decel_distance` and the VECTO
    re-implementation **agree** and both equal the result clamped at the top table
    speed. So the "skips the range above the table" behaviour in the code of record
    is **not a bug vs VECTO** — VECTO clamps the same way (FindIndex + `Min(v1,
    rightKey)`). This resolves the open sub-item in 2.3. `[VECTO][TEST]`
  - a deliberately **invalid** dec curve that crosses zero is documented as degenerate
    (never produced by a real `.vacc`, which is strictly negative per the VECTO
    `SIRange(-20, -0.05)` on Deceleration).
- **`coast_distance`**
  - vs a hand re-implementation of VECTO's formula for 6 cases (flat/uphill/downhill ×
    small/large drop): relative error < 1e-9: pass.
  - uphill with negative `dE` → negative result; confirmed the driver_model ignores
    it (uses `cd` only when `> 0`), which matches VECTO treating `coastingDistance < 0`
    as braking-only (`GetDrivingBehaviorEntry` line 713). `[VECTO]`
  - `cos(grad)` vs `cos(atan(grad))` quantified (see Q3 table).
  - `P_drag_loss/v` is finite/positive at realistic coasting speed; confirmed
    `coast_distance` is only called above 50 km/h in the model (guarded by
    `coast_on and v > lac_min`), so `v` is never small on that path.

## Part C — behaviour tests on the real VECTO cycles (`tests/driver_model/test_cycles.py`)

90 tests, **all passing** `[TEST]`. Cycles present in the repo: **RegionalDelivery,
UrbanDelivery, LongHaul, Construction, MunicipalUtility** (5 of the 10 the prompt
lists; HeavyUrban/Urban/Suburban/Interurban/Coach are **not** in
`reference/vecto/resources/MissionCycles` — **BLOCKED** for those). `.vacc` used is
the real VECTO `Truck.vacc`. Coasting set-up is **ILLUSTRATIVE** (harness v1.7 not
supplied), so these are **internal-invariant** checks, not VECTO comparisons.

Per-cycle results (coasting ON; mode shares = stop/accel/cruise/coast/brake %):

| Cycle | rows | stand s | shares (0/1/2/3/4) | worst dec ÷ .vacc |
|---|---|---|---|---|
| RegionalDelivery | 5905 | 746 | 12.6/7.3/61.3/9.4/9.4 | 1.67 |
| UrbanDelivery | 13645 | 3349 | 24.5/21.5/28.8/5.7/19.5 | 1.69 |
| LongHaul | 4499 | 67 | 1.5/3.2/84.5/5.8/5.1 | 1.75 |
| Construction | 7918 | 1074 | 13.6/14.7/49.0/8.3/14.4 | 1.62 |
| MunicipalUtility | 2203 | 272 | 12.3/24.1/34.7/5.2/23.7 | 1.68 |

(The coast-off shares match the prompt's 2.2 figures closely, e.g. Regional
12.7/7.6/72.9/0/6.9 — confirming the harness-independent behaviour is faithful. The
coast-on coast-share differs from the prompt's "7.8 % no drag" because the CdxA/Crr
here are ILLUSTRATIVE, not VECTO's reference vehicle.)

Checks that **pass** for every cycle, both coast off and on:
- reaches the end, no `RuntimeError`, runtime < 60 s (all ≪ a few seconds);
- standing time = cycle stop time (+1 s first-waypoint rule where it applies);
- speed never more than 1 km/h above target+2.5 (above 50) / target (below 50) —
  **zero violations** on all 5 cycles (the prompt's "up to 1 km/h over on 6 rows" was
  not reproduced here with these waypoints — it may be cycle/vehicle specific; re-run
  once harness v1.7 is supplied);
- powered acceleration (mode 1) never exceeds `.vacc`;
- deceleration never beyond ~2× `.vacc` (worst 1.62–1.77×, the known 1 s artefact);
- distance monotone, time step uniform, altitude along rows = cycle altitude.

**New finding (mode 3 over `.vacc` accel).** On **Construction** with coasting on,
**2 rows** (at 17 163 m, grade −6.87 %, 53.7 km/h; and 49 336 m, grade −7.52 %,
68.5 km/h) have a coast acceleration exceeding the `.vacc` accel limit by up to
0.054 m/s² `[TEST]`. Both are steep downhills in mode 3 (coast). This matches VECTO:
the free-rolling `Coast` action is driven by gravity and is **not** limited by the
driver's `.vacc` accel curve (only powered `Accelerate` is). So it is **correct
behaviour**, now documented and guarded by a test (`test_coast_mode_overspeed_rows_are_downhill`).

**Edge routes** (synthetic, ILLUSTRATIVE): one waypoint, all-zero speeds, back-to-back
stops, < 1 m / 1–5 m spacing, ±10 % grade, 1 km/h target change, start-at-speed,
`dt=0.5`, `dt=2.0` — **all terminate cleanly** and pass their assertions. The all-zero
route terminates (does not hang); the single-waypoint route is documented.

**No crash / BUG found in the code of record on any realistic route** (stop condition
6 not triggered). `[TEST]`

## Part D — comparison with VECTO `.vmod` — **BLOCKED**

The required inputs were not supplied: `BEV_E2_RegionalDelivery_ReferenceLoad_1Hz.vmod`,
`BEV_E2_UrbanDelivery_ReferenceLoad_1Hz.vmod`, the `.vsum`, harness v1.7, the
std-drag add-on, and the E2 component files. **All of Part D (metrics 1–7, cases
D1–D8, graphs vs VECTO, hypotheses h1–h7 ranking) is BLOCKED.** What I could do
without VECTO:
- The D1-vs-coast-on speed-vs-distance graphs for the 3 representative stretches are
  generated (no VECTO overlay) for Regional and Urban — see
  `docs/research/driver-model-review-2026-11/*.png`. Bob can overlay the `.vmod` once
  it exists; `make_graphs.py` is written to take it.
- The experimental variants D4 (`atan`), D6 (step-average drag) are implemented in
  `tests/driver_model/variants.py` ready to measure once a VECTO baseline exists.
- **h-ranking I can give now from source (not measurement):** h2 (wrong DF tables) is
  **ruled out** — the tables are exact (Q2). h3 (mode-mapping Coast vs Roll) is
  **confirmed as a real mechanism** (Q12) and likely explains part of the coast-share
  gap. h4 (missing hold-speed branch) is partly real (Q6 — HDEV approximates it). h1
  (drag magnitude) and h6/h7 (inertia, instantaneous air drag) remain **open, need
  D2/D6/D7**. This ranking is provisional until the `.vmod` arrives.

## Part E — fixed reference mass: how much does it matter? `[TEST]` (ILLUSTRATIVE vehicle)

Driver run at `coast_mass` = empty (6570 kg), reference (9590 kg), full (16000 kg);
wheel energy via the repo `force_engine`. The **"wrong-mass trace" error** = driver
trace built at the reference mass but energy evaluated at the actual mass, vs driver
+ energy both at that mass.

| Cycle | mass | coast % | E_traction (kWh) | E_braking (kWh) |
|---|---|---|---|---|
| Regional | empty | 6.2 | 50.7 | −4.4 |
| Regional | reference | 9.4 | 58.5 | −7.7 |
| Regional | full | 10.6 | 76.7 | −16.0 |
| Urban | empty | 5.1 | 53.6 | −29.1 |
| Urban | reference | 5.7 | 72.6 | −43.6 |
| Urban | full | 6.4 | 113.6 | −74.8 |
| LongHaul | empty | 3.2 | 53.4 | −1.3 |
| LongHaul | reference | 5.8 | 59.0 | −2.3 |
| LongHaul | full | 10.2 | 72.3 | −5.9 |

**Wrong-mass trace error** (driver@reference, energy@actual):

| Cycle | mass | traction err | braking err |
|---|---|---|---|
| Regional | empty | +0.28 % | +2.12 % |
| Regional | full | +1.66 % | **+8.43 %** |
| Urban | empty | −0.54 % | −0.64 % |
| Urban | full | +1.26 % | +1.83 % |
| LongHaul | empty | +0.07 % | −0.32 % |
| LongHaul | full | +1.29 % | **+17.71 %** |

**Reading (numbers only — the decision is Bob's):** using one fixed reference-mass
trace for all payloads costs **< 1.7 % on traction energy** in every case, but the
**braking-energy error grows with mass mismatch**, reaching +8 % (Regional, full) and
+18 % (LongHaul, full). LongHaul is worst because its absolute braking energy is tiny
(−5.9 kWh), so a small absolute mismatch is a large percentage. Whether this is
acceptable depends on how much braking/regen energy matters to the final result and
how the payload scenarios are weighted — **I am not deciding it.** With VECTO
LowLoading `.vmod` (Part G R3/R4), these can be anchored to VECTO. Numbers are
**ILLUSTRATIVE** (vehicle not the certified E2); the *mechanism and ordering* are
robust, the exact % are not. `[TEST][ASSUMPTION]`
Reproduce: `python docs/research/driver-model-review-2026-11/measure_part_e.py`.

## Part F — the 1 s step `[TEST]`

dt = 1.0 / 0.5 / 0.25, coasting on, reference mass (ILLUSTRATIVE):

| Cycle | dt | rows | trip time s | stand s | coast % | E_trac (Δ%) | E_brake (Δ%) | worst dec÷.vacc |
|---|---|---|---|---|---|---|---|---|
| Regional | 1.00 | 5905 | 5905.0 | 746 | 9.38 | 58.53 (—) | −7.67 (—) | 1.674 |
| Regional | 0.50 | 11795 | 5897.5 | 746 | 9.82 | 58.41 (−0.21) | −7.52 (−1.95) | 1.985 |
| Regional | 0.25 | 23587 | 5896.8 | 746 | 10.04 | 58.35 (−0.31) | −7.46 (−2.75) | 2.874 |
| Urban | 1.00 | 13645 | 13645.0 | 3349 | 5.70 | 72.59 (—) | −43.61 (—) | 1.686 |
| Urban | 0.50 | 27169 | 13584.5 | 3349 | 6.00 | 71.79 (−1.10) | −42.78 (−1.89) | 2.075 |
| Urban | 0.25 | 54295 | 13573.8 | 3349 | 6.14 | 71.36 (−1.70) | −42.33 (−2.92) | 2.378 |

Reading:
- **Trip time** converges: the 1 s step adds **+0.1 % (Regional) / +0.5 % (Urban)**
  trip time vs dt=0.25.
- **Traction energy** error at dt=1.0 is **≤ 0.3 % (Regional) / ≤ 1.7 % (Urban)**.
- **Braking energy** error at dt=1.0 is **≤ ~2.9 %**. For energy, **dt = 1.0 is good
  to within ~3 % of its own dt→0 limit** on these cycles.
- **Surprising:** the `worst dec ÷ .vacc` ratio **grows** as dt shrinks (1.67 → 2.87
  on Regional). The last-step landing formula `(v_t²−v²)/(2·rem)` produces a sharper
  peak over a shorter remaining distance at small dt. So the 1 s deceleration-peak
  artefact (deviation 1) is **not monotone in dt** — refining dt does not fix it and
  can make the peak ratio worse. This is a **new finding** about the artefact's
  behaviour. `[TEST]`
- **Standing time is identical at every dt** (746 / 3349 s) — confirming the ~1 s per
  stop gap vs VECTO (2.3) is in VECTO's 1 Hz output averaging (Q11), **not** in HDEV's
  step size.
- **Runtime cost of finer dt:** rows scale ~1/dt (Urban 13.6k → 54.3k at dt=0.25);
  pure-Python runtime scales roughly linearly, still < a few seconds per cycle, so
  going to dt=0.5 for an energy sanity check is cheap. The per-stop standing-time
  difference vs VECTO is explained in Q11.

Reproduce: `python docs/research/driver-model-review-2026-11/measure_part_f.py`.

---

## Part H — independent research (not VECTO)

Bob's rule: validate against independent sources. "Read" = I read the full text;
"snippet" = I saw only a search snippet/abstract. _Content below was summarised and
rephrased for compliance with source licensing._

### H.1 VECTO validation vs measured traces; driver-model changes after 5.1.6 / regulation

| Source | Date | Read? | What it is / relevance |
|---|---|---|---|
| [Commission Regulation (EU) 2025/258](https://eur-lex.europa.eu/eli/reg/2025/258/oj/eng/pdf) | 7 Feb 2025 | snippet | Amends 2017/2400 for medium/heavy lorries, heavy buses, hydrogen and new tech. **Exists** (confirms the prompt's lead). Whether it changes the *driver model / LAC* specifically is **not confirmed from the snippet** — Bob to check the Annex text. `[REG][OPEN]` |
| [Commission Regulation (EU) 2022/1379](http://data.europa.eu/eli/reg/2025/258/oj/eng/xhtml) (cited inside 2025/258) | 2022 | snippet | Expanded 2017/2400 scope to medium lorries & heavy buses and **added hybrid & pure-electric vehicles** — this is the regulation that introduced the BEV path HDEV targets. `[REG]` |
| [Consolidated 2017/2400, in force 2026-01-01](http://data.europa.eu/eli/reg/2017/2400/2026-01-01/eng/xhtml) | 2026 | snippet | Current consolidated text; the Annex with the driver/LAC parameters lives here. Bob to fetch the driver-behaviour Annex for the authoritative DF/overspeed/LAC definitions. |
| [JRC — HDV CO₂ monitoring, experimental proof of concept (JRC91415)](https://publications.jrc.ec.europa.eu/repository/handle/JRC91415) | 2015 | snippet | Early VECTO validation against measurements; the basis for VECTO's claimed accuracy. Old, but the methodology reference. |
| [JRC104993 — ex-post verification test campaign](https://publications.jrc.ec.europa.eu/repository/handle/JRC104993) | 2017 | read (abstract) | Four Euro VI trucks, chassis-dyno + on-road; VECTO used to simulate; concludes on-road transient verification is feasible but needs defined acceptance/rejection margins, and that systematic sim-vs-real deviation must be quantified. Supports Bob's "VECTO is reference, not ground truth" stance. `[SOURCE]` |
| [JRC SAE 2019-01-1280 (JRC116081)](https://publications.jrc.ec.europa.eu/repository/bitstream/JRC116081/sae_paper_jrc116081_final_green.pdf) | 2019 | snippet | VECTO history/structure; HDV common characteristics by mission. Context. |
| [TU Graz IVT dissertation (Kies, 2017)](http://diglib.tugraz.at/download.php?id=5aa2481a0be19&location=aleph) | 2017 | snippet | Fuel-efficiency measures for HDVs from the VECTO authors' institute (Hausberger et al.). Likely contains driver-model rationale; Bob to fetch. |
| [TU Graz ITNA generic PEV result files](https://www.itna.tugraz.at/assets/files/vecto/CIF2PDF/pev-e2-heavylorry.rslt-customer.pdf) | 2024 | snippet | VECTO 4.0.2 customer result files for generic PEV E2 (RRC 0.0038, PCC yes). Useful to sanity-check the E2 set-up numbers; not a driver-trace comparison. |

**Finding for H.1:** I could **not confirm** any change to the VECTO *driver model*
after 5.1.6 from these sources (snippets only). 2025/258 and 2022/1379 are real and
relevant to the BEV scope, but the driver-behaviour Annex details need the full
consolidated text (Bob-to-fetch). `[OPEN]`

### H.2 Measured heavy-truck driver behaviour (coasting, deceleration, eco-driving)

| Source | Date | Read? | Relevance |
|---|---|---|---|
| [NREL Fleet DNA](https://www.nlr.gov/transportation/fleettest-fleet-dna) | ongoing | snippet | Commercial-fleet operating data (speed/accel distributions by vocation). The natural independent source for real coasting share & deceleration rates by duty cycle. No single coasting-share number in the snippet — Bob to pull the vocation summaries. |
| [NREL Fleet DNA bucket-truck summary](https://www.nlr.gov/media/docs/libraries/transportation/fleet_dna_bucket_trucks_report.pdf) | — | snippet | Example vocation report format (kinetic intensity, stops/mile). |
| [FHWA/NTL commercial-truck naturalistic driving study](https://rosap.ntl.bts.gov/view/dot/57153/dot_57153_DS1.pdf) | — | snippet | 3.8 M miles, 225 vehicles — distraction/drowsiness focus, but the dataset underlies deceleration-behaviour work. |
| [NCST eco-driving for HDVs](https://rosap.ntl.bts.gov/view/dot/67237/dot_67237_DS1.pdf) | — | snippet | Eco-driving programmes; coasting/decel behaviour change magnitudes. |
| [Connected eco-driving HDV field trial (arXiv 1908.00541)](https://arxiv.org/pdf/1908.00541.pdf) | 2019 | snippet | Measured speed-profile smoothing of a real HD diesel truck approaching signals — look-ahead/coasting behaviour in the field. |

**Finding for H.2:** No single published "coasting share for a BEV regional-delivery
truck = X %" was found in the snippets. Fleet DNA is the right place but needs the
per-vocation extract (Bob-to-fetch). So HDEV's coasting share **cannot yet be
validated against measured data** — only against VECTO (which is the audit reference,
not validation). `[OPEN / NOT FOUND in snippets]`

### H.3 How other models handle trace-following & coasting

| Source | Date | Read? | Relevance |
|---|---|---|---|
| [NREL FASTSim validation report 2021](https://www.nlr.gov/docs/fy22osti/81097.pdf) | 2021 | snippet | FASTSim follows a prescribed drive cycle with a simple "aux load + road load" balance; it does **not** simulate a look-ahead coasting driver the way VECTO does — it tracks the cycle speed directly. Different philosophy from HDEV/VECTO. `[SOURCE]` |
| [FASTSim overview (NREL 71126)](https://www.nlr.gov/docs/fy18osti/71126.pdf) | 2018 | snippet | Light/medium/heavy; cycle-following, fast. |
| [FASTSim calibration via real-world data (SAE 2022-01-0661)](https://www.sae.org/publications/technical-papers/content/2022-01-0661/) | 2022 | snippet | Calibrates FASTSim vehicle models against real trips. |
| [Autonomie model validation via chassis-dyno (arXiv 2503.21057)](http://arxiv.org/pdf/2503.21057v1) | 2025 | snippet | Validates/reduces Autonomie models against chassis-dyno data; a 2025 example of independent energy-model validation methodology. |

**Finding for H.3:** FASTSim/Autonomie are **cycle-following** (they track the target
speed directly), so they do **not** provide an independent cross-check of VECTO's
*look-ahead coasting driver logic* — they would not coast ahead of a slowdown the way
VECTO/HDEV do. PHEM and SUMO were not found in the snippets. So among mainstream
models, VECTO's predictive-driver logic is somewhat unusual, and an independent
validation of *that specific logic* is scarce. `[SOURCE]`

### H.4 Measured coasting drag of electric-truck drivetrains

| Source | Date | Read? | Relevance |
|---|---|---|---|
| [MDPI — Driveline efficiency in EVs: architectures & gearbox losses](https://www.mdpi.com/2075-1702/14/9/1008/pdf?version=1788518021) | 2026 | snippet | Review of EV/e-truck driveline & gearbox power losses; relevant to the magnitude of drivetrain coasting drag. No single kN-vs-speed curve in the snippet. |
| [MDPI — lubricant effects on e-transaxle gear loss](https://www.mdpi.com/2075-4442/14/10/386) | 2026 | snippet | Measured gear-friction loss drops fast up to ~10 m/s then plateaus — shape of the drivetrain drag-vs-speed curve. |
| [ResearchGate — detailed gearbox loss modelling](https://www.researchgate.net/publication/228579066_Detailed_Loss_Modelling_of_Vehicle_Gearboxes) | 2009 | snippet | Drag torque varies strongly with speed/operating point — supports using a drag **table**, not a scalar. |

**Finding for H.4:** No measured "coasting drag force in kN vs speed for an electric
heavy truck" was found in the snippets to put the EU standard-value 0.63–0.85 kN or
the VECTO example 1.43–2.05 kN against real measurement. The literature supports the
*shape* (drag falls to a plateau, varies with speed) and the use of a **table over a
scalar**, but a direct numeric validation is **NOT FOUND**. `[NOT FOUND]`

**H overall:** the independent literature supports (a) VECTO being a reference rather
than ground truth, (b) using a speed-dependent drag table rather than a scalar, and
(c) the general plausibility of look-ahead coasting; but it did **not** yield a
measured coasting-share or coasting-drag number to validate HDEV against. The strong
validation sources (Fleet DNA extracts, the consolidated-regulation Annex, the TU
Graz dissertation) need full-text fetches — listed in "Bob to fetch".

---

## Proposed changes

Each change is prototyped in `tests/driver_model/variants.py` or stated as a
one-line edit. **Kiro did not edit any engine file.** "Swaps one assumption for
another" is called out per Bob's rule 7.

### P1 — gravity constant `g = 9.80665` (not 9.81) — `[VECTO]`, recommended

VECTO uses `9.80665` (`DeclarationData.cs` line 74). HDEV default `g=9.81`.

```python
# before (code of record signature)
def driver_model(..., rho=1.188, g=9.81, ...):
# after
def driver_model(..., rho=1.188, g=9.80665, ...):
```

**Effect:** a flat ~0.034 % reduction in every rolling, slope and coasting force term
`[CALC]`. **Not** a swap of assumptions — it is matching the sourced VECTO constant.
**Where:** `g` is already an argument (engine stays pure); set the VECTO value as the
**parser default**. Zero risk. **Recommended (Kiro's recommendation).**

### P2 — step-average air drag in `coast_acc` — `[VECTO]` (D6), BLOCKED magnitude

`coast_acc` uses instantaneous `rho/2·CdA·v²`; VECTO and the HDEV force engine use the
step average. Prototype `coast_acc_avgdrag` in `variants.py`.

```python
# before
F = rho/2 * interp1(v, cv, cc) * v*v + ...
# after (uses previous-step speed v_prev; L = (v1+v2)(v1^2+v2^2)/8)
L = (v + v_prev) * (v**2 + v_prev**2) / 8
F = rho * interp1(v_avg, cv, cc) * L / v_avg + ...
```

**Effect:** the known 0.02–0.29 kWh/cycle leftover (2.3 item 3); **magnitude vs VECTO
BLOCKED** (needs D6 on a VECTO baseline). **Not** an assumption swap — it matches
VECTO's drag form. **Where:** engine (it is pure maths; needs the previous-step speed
threaded in, a small engine change Bob must make).

### P3 — drivetrain coasting-drag **table** instead of scalar `P_drag_loss` — `[VECTO]`/`[REG]`, BLOCKED

VECTO's coasting resistance uses `(gbxLoss + axleLoss + emDrag − iceDrag)/v` from the
component maps (Q1, Q8); HDEV uses a single scalar. Replace `P_drag_loss` (a number)
with a drag-force-vs-speed table consumed in both `coast_acc` and `coast_distance`.

**Effect:** this is the main lever on the coasting-share / overspeed gap (2.2), but
its size is **BLOCKED** until D2 (VECTO's own example drag) and D3 (EU standard-value
drag) can be run against a `.vmod`. **Where:** the **parser** builds the table (from
the EU standard-value maps — gearbox Annex VI App. 8, axle Annex VII App. 3, motor
drag Annex Xb App. 8, IEPC Annex Xb App. 9 — or from uploaded component files); the
**engine** just interpolates it. This respects the purity rule. **Not** a pure
assumption swap *if* the table comes from the regulation/measured maps; it **would** be
an assumption swap if the table were invented — so it must be sourced. Flagged.

### P4 — reconsider the fixed reference-mass assumption — `[ASSUMPTION]`, decision for Bob

Part E shows the fixed-mass trace costs ≤ 1.7 % traction energy but up to **+8.4 %
(Regional) / +17.7 % (LongHaul)** braking energy at full load. **This is Bob's design
call** (run-once-per-vehicle speed vs per-scenario accuracy). I am **not** deciding
it. If kept, the deviation register wording below must go into client reports. If
changed, it breaks the "driver runs once per vehicle" architecture — a big change.

### Rejected — `atan` in `coast_distance` (D4)

VECTO does **not** apply `atan` (Q3). Adding it (`coast_distance_v_atan` in
`variants.py`) would make HDEV **deviate** from VECTO by < 0.004 % in the rolling
term. **Do not make this change.** It is a pure assumption swap with no source behind
the new assumption, and it moves *away* from VECTO.

---

## Deviation register (HDEV vs VECTO)

Updated from section 1.2 + Part A. "Client wording" = how it must be stated in a
client-facing report.

| # | Deviation | Size | Source | Client wording |
|---|---|---|---|---|
| D-01 | Fixed 1 s rows (VECTO ~0.5 s variable, snaps to brake/stop) | trip time +0.1–0.5 %; braking-energy within ~3 % of dt→0; dec-peak up to 1.78× .vacc (and grows at smaller dt) | `[VECTO][TEST]` | "Speeds are computed on a fixed 1-second grid; energy agrees with a finer grid to within ~3 %." |
| D-02 | Coasting/overspeed at a **fixed reference mass/CdxA, no wind** | braking-energy error up to +8 % (Regional) / +18 % (LongHaul) at full load | `[ASSUMPTION][TEST]` | "The coasting driver is computed once at a reference load; per-load energy is then scaled, which can bias braking energy on heavy loads." |
| D-03 | Instantaneous air drag in `coast_acc` (VECTO step average) | 0.02–0.29 kWh/cycle (prior); vs VECTO BLOCKED | `[SIMPLIFICATION]` | "A minor air-drag averaging simplification in coast steps." |
| D-04 | Scalar drivetrain drag (default 0), no motor power cap | coasting-share/overspeed gap; BLOCKED size | `[SIMPLIFICATION]` | "Drivetrain drag during coasting is approximated." |
| D-05 | Back-to-back stops aim for next **positive** target; VECTO aims for the **immediate** next waypoint target (may be 0) | affects only consecutive-stop sequences | `[VECTO]` | "Behaviour at consecutive stops differs slightly from VECTO." |
| D-06 | Acceleration pre-capped before slowdowns (stand-in for `CheckRequestDoesNotExceedNextAction`) | small | `[VECTO]` | n/a (internal) |
| D-07 | Stop arrival distance snapped (≤ 0.18 m/stop; Municipal +9.4 m/11.24 km) | < 0.1 % distance | `[VECTO]` | "Stop positions are rounded by < 0.2 m per stop." |
| D-08 | `g = 9.81` vs 9.80665 | ~0.034 % force bias | `[VECTO]` | fixable (P1); state only if unfixed |
| D-09 | Mode 2 "cruise" has no VECTO code; VECTO splits free-roll into Coast(4)/Roll(2), HDEV folds to mode 3 | affects mode-share comparison | `[VECTO]` (new, from Q12) | "HDEV's mode labels differ from VECTO's action codes; coast comparisons sum VECTO Coast+Roll." |
| D-10 | Mode-3 coast can exceed `.vacc` accel on steep downhills | 2 rows on Construction (≤ 0.054 m/s²) | `[VECTO][TEST]` (new) | n/a — matches VECTO free-rolling |
| D-11 | Overspeed/`FirstAccelerateOrCoast` approximated kinematically (VECTO iterates powertrain responses) | BLOCKED vs VECTO | `[VECTO]` | "The overspeed/coast decision is a kinematic approximation of VECTO's powertrain search." |
| D-12 | Standing time = exact cycle stop time; VECTO 1 Hz output averages the stop/start second (~+1 s/stop region) | +10 s (Regional) / +104 s (Urban) total | `[VECTO][TEST]` | "Standing time matches the cycle definition; VECTO's 1 Hz output reports it ~1 s/stop lower." |
| D-13 | `decel_distance` ignores distance above the top `.vacc` point | **none** — VECTO clamps identically | `[VECTO][TEST]` | n/a — **not** a deviation (was an open worry; resolved) |
| D-14 | Repo `src/engine/driver_model.py` is the stale pre-21-Oct model | n/a | — | n/a — housekeeping; replace with code of record |

---

## BLOCKED items (inputs not supplied — Part 0.1)

| Blocked | Needs | Affects |
|---|---|---|
| `BLOCKED: reference/vecto/runs/BEV_E2_RegionalDelivery_ReferenceLoad_1Hz.vmod` | Bob's VECTO run (Part G) | Part D, E (VECTO anchor), F (VECTO side) |
| `BLOCKED: reference/vecto/runs/BEV_E2_UrbanDelivery_ReferenceLoad_1Hz.vmod` | Bob's VECTO run | Part D, E, F |
| `BLOCKED: reference/vecto/runs/*.vsum` | Bob's VECTO run | Part D totals |
| `BLOCKED: tests/harness/hdev_test_harness_v1.7.py` | Bob | the certified E2 set-up for C/D/E (used ILLUSTRATIVE instead) |
| `BLOCKED: tests/harness/hdev_addon_std_drag_v1.py` | Bob | D3 (EU standard-value drag) |
| `BLOCKED: E2 component files (.vveh/.vemo/.vemd/.vtlm/Truck.vacc)` | from the VECTO repo folder | D2 (VECTO example drag), D7 |
| `BLOCKED: cycles HeavyUrban/Urban/Suburban/Interurban/Coach` | not in resources/MissionCycles | Part C coverage of those cycles |

(Note: the E2 component files **do** exist in the cloned VECTO repo at
`Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/`; they are just not in the
`hdev` repo. Part G R-runs will produce the drag numbers directly, which is cleaner
than re-deriving them from the `.vtlm` maps.)

## Bob to fetch

| Document | Why | Link |
|---|---|---|
| Consolidated 2017/2400 driver-behaviour Annex (in force 2026-01-01) | authoritative LAC/DF/overspeed definitions, and whether 2025/258 changed the driver model | http://data.europa.eu/eli/reg/2017/2400/2026-01-01/eng/xhtml |
| Reg (EU) 2025/258 full PDF | confirm/deny driver-model changes | https://eur-lex.europa.eu/eli/reg/2025/258/oj/eng/pdf |
| NREL Fleet DNA per-vocation extracts | measured coasting share / deceleration for regional & urban trucks (H.2 validation) | https://www.nlr.gov/transportation/fleettest-fleet-dna |
| TU Graz IVT dissertation (Kies 2017) | VECTO driver-model rationale from the authors' institute | http://diglib.tugraz.at/download.php?id=5aa2481a0be19&location=aleph |
| JRC104993 ex-post verification report (full) | sim-vs-measured deviation margins | https://publications.jrc.ec.europa.eu/repository/handle/JRC104993 |
| VECTO 5.1.6 source (exact tag/commit) | re-confirm every line number in this review | the VECTO 5.1.6 release Bob used for the .vmod runs |

## How to run everything

```bash
# from the repo root, in a venv with numpy, pytest, matplotlib
pip install numpy pytest matplotlib          # or: uv pip install ...
pytest tests/driver_model -q                 # Part B (25) + Part C (90) = 115 tests
export MPLCONFIGDIR=/tmp/mpl
python docs/research/driver-model-review-2026-11/measure_part_e.py   # Part E numbers
python docs/research/driver-model-review-2026-11/measure_part_f.py   # Part F convergence
python docs/research/driver-model-review-2026-11/make_graphs.py      # graphs
```

Everything in `tests/driver_model/` imports the **code of record** from
`reference_copy.py`; no engine file was touched.
