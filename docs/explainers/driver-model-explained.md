# The driver model, explained from scratch

**For Bob. Written 2 November 2026.** Plain English, no assumed background. Every
technical word is defined the first time it appears. The code being explained is
the "code of record" (Appendix 1 of the driver-model prompt), copied verbatim into
`tests/driver_model/reference_copy.py`.

VECTO line references are to **VECTO v5.1.3, stable branch, commit `d16ba783c`**
(the version in `reference/vecto/cs/` and cloned for this review). Bob's `.vmod`
comparison runs were made with **VECTO 5.1.6**, which may differ slightly — see the
review document for where.

---

## 1. What problem does the driver model solve?

A **route** is a list of **waypoints**. Each waypoint says: at this distance along
the road (metres), the speed limit is this (km/h), the road tilts this much (grade,
in %), and the truck stands still here for this many seconds (a stop).

The force engine and consumption engine that come later need something finer than
waypoints. They need a **speed trace**: one row per second (or per `dt` seconds)
telling them, at each moment, how fast the truck is going, how hard it is
accelerating or braking, and what the road grade is right there.

The driver model is the thing that turns the coarse waypoints into that
second-by-second trace. It is, in effect, a **simulated driver**: it decides when to
press the accelerator, when to lift off and roll, and when to brake, so the truck
follows the speed limits of the route without overshooting corners or stops.

It copies the logic of VECTO's own simulated driver (VECTO calls it the
`DefaultDriverStrategy`), because HDEV has to be auditable against VECTO.

**Output** — six arrays, one entry per row:

| Array | Meaning |
|---|---|
| `T` | time at the start of the row (s) |
| `S` | distance along the route at the start of the row (m) |
| `V` | speed at the start of the row (m/s) |
| `A` | acceleration during the row (m/s²) |
| `grade` | road grade during the row (%) |
| `M` | mode: 0 = standing still, 1 = accelerating, 2 = cruising, 3 = coasting, 4 = braking |

**Coasting** = rolling with the motor producing no drive torque (the truck slows
down on its own from air drag, rolling resistance, and gravity). **Cruising** =
holding a steady speed. **Braking** = actively slowing with the brakes (and, for an
electric truck, the motor acting as a generator).

---

## 2. The three helper functions

The driver model leans on three small maths helpers. Understand these first.

### 2.1 `interp1(x, xs, ys)` — read a value off a table

**What it does.** You have a table: a list of x-values `xs` (increasing) and a
matching list of y-values `ys`. You want the y for some x that falls *between* two
rows of the table. `interp1` draws a straight line between the two neighbouring
table points and reads the y off that line. This is called **linear interpolation**.

If x is below the first row it returns the first y; if above the last row it returns
the last y (it "holds" the ends flat). It behaves exactly like NumPy's `np.interp`,
but it is written to be fast when called millions of times inside the main loop.

**Worked example (ILLUSTRATIVE numbers).** Table: at 0 km/h the limit acceleration
is 1.0 m/s², at 50 km/h it is 0.64 m/s². Ask for the limit at 25 km/h:

```
interp1(25, [0, 50], [1.0, 0.64]) = 1.0 + (0.64 - 1.0) * (25 - 0) / (50 - 0)
                                   = 1.0 - 0.36 * 0.5 = 0.82 m/s²
```

Halfway between the two table speeds, so halfway between the two accelerations.

**Why it exists.** The truck's acceleration and deceleration limits, and its air-drag
area, are all given as tables against speed. `interp1` reads them at the exact
current speed.

### 2.2 `decel_distance(v_from, v_to, vacc_v, vacc_dec)` — how far to brake

**What it does.** Given a current speed `v_from` and a slower target speed `v_to`,
it returns the distance (metres) the truck needs to slow from one to the other,
**braking exactly as hard as the `.vacc` curve allows at each speed**.

The **`.vacc` curve** is a table that says, for each speed, the maximum comfortable
acceleration and the maximum comfortable deceleration a driver uses. (`vacc_v` are
the speeds, `vacc_dec` the decelerations — negative numbers, because decelerating.)

Because the allowed deceleration changes with speed, you cannot use the simple
schoolbook formula with one fixed deceleration. `decel_distance` splits the speed
range into the straight-line pieces of the table and adds up the distance for each
piece. Within a piece where the deceleration is constant it uses the schoolbook
formula; where the deceleration changes linearly with speed it uses an exact
integral (the log/exp lines in the code).

**Worked example (real Truck.vacc).** Slowing from 80 km/h to 0 on the VECTO
`Truck.vacc` curve takes about **372 m** (measured with the code of record). That is
long because `Truck.vacc` brakes gently at high speed (−0.5 m/s² above 60 km/h).

**Why it exists.** The driver must know *where* to start braking so it arrives at a
slower zone or a stop at exactly the right speed. "Start braking `decel_distance`
before the point" is the rule.

**It matches VECTO** term for term — it is a direct re-implementation of VECTO's
`AccelerationCurve.ComputeDecelerationDistance` (`AccelerationCurve.cs`, lines
119–181). One subtlety: if `v_from` is above the top of the `.vacc` table, both this
function and VECTO ignore the little bit of distance spent above the table and start
counting from the top table speed. So they agree.

### 2.3 `coast_distance(...)` — how far the truck can coast before a slowdown

**What it does.** Before a point where the truck must be slower, a good driver lifts
off early and lets the truck roll down to the new speed, saving energy. `coast_distance`
returns how far before the point the driver should lift off.

The idea is an **energy balance**. The truck has an amount of surplus energy to shed
(its extra kinetic energy from going faster, plus or minus the energy from going
down or up a hill). Dividing that surplus by the resisting force (air drag + rolling
resistance + drivetrain drag) gives the distance over which the resistance will
"use up" the surplus — i.e. the coasting distance.

There is one extra twist: a **decision factor** (`DF`). Real drivers do not coast the
theoretical maximum distance; they start a bit later. VECTO multiplies the resisting
force by a factor built from two small tables (how fast the target is, and how big
the speed drop is). HDEV copies those tables exactly.

**Worked example (ILLUSTRATIVE).** Truck at 85 km/h, target 80 km/h, flat road,
~9.6 t: the surplus kinetic energy is small, so the coasting distance is modest
(tens of metres). Target 55 km/h instead (a big drop): much more surplus, so the
truck can coast for a few hundred metres.

**Why it exists.** It decides *where coasting starts*. If the coasting start is
earlier than the braking start, the driver coasts; otherwise it just brakes.

**It matches VECTO** — it re-implements `DefaultDriverStrategy.ComputeCoastingDistance`
(`DefaultDriverStrategy.cs`, lines 741–779). Important detail settled in this review:
the rolling-resistance term uses `cos(rise/run)` where `rise/run` is treated directly
as an angle in radians — **this is exactly what VECTO does** (VECTO's
`Vehicle.RollingResistance` takes `cos` of the raw rise-over-run value). An earlier
HDEV note suggested applying `atan` first; the source shows VECTO does **not**, so
the code of record is right to leave `atan` out here.

---

## 3. The main function `driver_model(...)` block by block

The function has three parts: **A** set-up before the loop, **B** the per-second
loop, **C** tidy-up after the loop.

### Part A — set-up (run once)

1. **Convert units.** Waypoint speeds come in km/h; the maths wants m/s. Distances
   stay in metres.
2. **Build the altitude profile.** The route gives grade (%) at each waypoint. The
   code turns grade into height: over each segment, height change = segment length ×
   grade / 100, then it adds them up. This is exactly VECTO's method
   (`DrivingCycleDataReader.cs`, line 236).
3. **First-waypoint stop rule.** If the route starts at 0 km/h with no stop written,
   VECTO inserts a 1-second stop. The code copies this (VECTO line ~220).
4. **Work out the "segment target" speed.** After passing a waypoint, what speed is
   the driver aiming for? Normally the waypoint's own speed. But if the waypoint is a
   stop (0 km/h), the driver aims for the **next moving speed** so it knows how fast
   to pull away afterwards. (HDEV takes the next *positive* speed; VECTO takes the
   *immediate* next waypoint's speed — a small difference when two stops sit back to
   back. See the review's deviation register.)
5. **Change points.** Only waypoints where the target drops matter for braking or
   coasting. The code lists those, so the look-ahead does not scan every waypoint.
6. **Coasting set-up.** If a coasting mass was given, coasting and overspeed are
   switched on; otherwise the model is pure kinematics (speeds only, no energy-based
   coasting).

`coast_acc(v, k)` is a small helper defined here: the acceleration (a negative
number — a slowing) of the truck when the motor is giving no torque, at speed `v` on
segment `k`. It adds air drag, rolling resistance, the slope force, and any
drivetrain drag, then divides by the mass. (It uses `atan` for the slope angle here,
which is the geometrically exact angle; this is a deliberate choice for the
free-rolling physics — see the review for how it relates to VECTO.)

### Part B — the per-second loop

Each pass through the loop is one row of output (one `dt`, normally 1 second). The
loop:

1. **Find which segment we are in** and the target speed there.
2. **Look ahead.** It scans the road ahead (how far depends on current speed) for the
   next place the truck must slow down. For each such place it works out two
   distances: where **braking** would have to start, and where **coasting** could
   start. It keeps the earliest of each. This mirrors VECTO's `GetNextDrivingAction`
   (lines 647–703).
3. **Decide whether to start slowing.** If the next step would carry the truck past
   the chosen start point, it arms a "slowdown" (the `trig` variable). If a *nearer*
   slowdown appears that needs earlier braking, it switches to that (VECTO calls this
   `CheckSwitchingToBraking`).
4. **Choose the acceleration for this row.** This is the heart of it:
   - If a slowdown is armed: either drive along at the target if already slow enough
     (mode 2), or **coast** if coasting is allowed and we are still before the brake
     point (mode 3), or **brake** (mode 4). The first braking step is split so braking
     begins exactly at the brake point; the last step or two are shaped so the truck
     lands on the target speed right at the point.
   - If no slowdown is armed: **accelerate** toward the target (mode 1), capped so the
     truck never goes so fast it cannot brake for the next slowdown in time; or, if
     already at target and overspeed is allowed (downhill), **coast/roll** up to
     target + 2.5 km/h and then hold; or **brake** down to target; or just **cruise**
     (mode 2).
5. **Move one step.** New speed = old speed + acceleration × `dt`. Distance covered =
   average speed × `dt`. If the truck would stop inside the step, it is snapped to
   stop exactly at the stop point. The row is recorded.
6. **Handle arrival at a stop.** If the truck has just reached a stop, the standing
   rows (mode 0) for the stop's duration are added.

If the loop somehow never reaches the end of the route, a guard raises an error
(this should never happen on a valid route).

### Part C — tidy-up

After the loop the lists become arrays. The grade for each row is recomputed from the
**altitude** at the start and end of the row (height difference ÷ distance), so the
grade the force engine sees is the true slope the truck rolled over in that row, not
just the waypoint's grade. Standing rows keep the waypoint grade.

---

## 4. The modes, and how they line up with VECTO

HDEV mode numbers and VECTO's `DriverAction` codes are **not** the same numbers:

| HDEV mode | Meaning | Closest VECTO `DriverAction` (`Driver.cs` line 50) |
|---|---|---|
| 0 | standing still | `Halt` (= 0) |
| 1 | accelerating | `Accelerate` (= 6) |
| 2 | cruising (hold speed) | *(no separate VECTO code — VECTO holds speed via Accelerate/Brake)* |
| 3 | coasting | `Coast` (= 4), and sometimes `Roll` (= 2) |
| 4 | braking | `Brake` (= −5) |

The important subtlety: VECTO has **two** free-rolling actions — `Coast` (clutch
closed, so the drivetrain drag still slows the truck) and `Roll` (clutch open, truck
rolls almost freely). HDEV folds both into mode 3. This matters when comparing
coasting shares against VECTO and is covered in the review.

---

## 5. Where to look next

- The full audit of every line, with VECTO line numbers and verdicts, is in
  `docs/research/driver-model-review-2026-11.md`.
- Runnable tests of all three helpers and the whole model are in
  `tests/driver_model/` (run with `pytest tests/driver_model`).
