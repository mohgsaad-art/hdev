# HDEV session close-out: payload engine + force engine (8 Oct 2026)

Hand-over for a new chat. Marked **Decided**, **Open**, **Assumption** (not sourced), **Suggestion** (Claude's proposal).
Previous close-outs: crosswind-payload (7 Oct), precompute architecture (6 Oct).
Related: crosswind verification, payload-resolver design (payload part now SUPERSEDED by this file).

---

## 1. Where we are

Precompute layer status:
- F crosswind_engine — DONE (verified vs VECTO Excel, 0.006%).
- H payload_engine + fill_payload — DONE (section 2).
- I force_engine — DONE, tested (section 4).
- **Left:** P_aux (next), then driver model audit/rebuild (6 known bugs + items in section 6). Weather step (W, `weather_for_rows`) also still to write.

---

## 2. Payload design — final (Decided, 8 Oct 2026)

Supersedes the 7 Oct schedule/lookup design and all earlier variants discussed today.

**Four route inputs only:** VDRI, GPS, typed user input, AI adapter (AI must output a waypoint template).

**Core rule:** the payload engine writes payload **only on row 0 (start payload) and on rows with `stop > 0`**. All other rows stay blank (NaN). A separate forward-fill fills the blanks just before the driver model. The driver model copies payload into its per-second rows exactly like grade (driving rows `current.payload`, stopped rows `target.payload`, first-waypoint stop loop `self.waypoints[0].payload`).

- One row with `stop > 0` = one stop. The engine never merges consecutive stop rows (VDRI MunicipalUtility has genuine stops 20/40 m apart).
- Row 0 (depot start) is never counted as a payload change, even if it has a stop time.
- Start payload is always on row 0, so forward-fill has a starting value.
- Payload in kg inside the engine; UI in tonnes (convert before calling).
- Shapes: `constant`, `linear` (equal steps start→end, **Assumption**, unsourced), `custom` (start + one value per stop). `payload_per_stretch` was dropped; shape logic is inside `payload_engine`.
- Linear with zero stops → error. Custom with wrong length → error. Negative payload → error.
- Driver model does not read payload; it only copies it. A % payload sweep can multiply the row column without rerunning the driver model; a different shape needs a rerun (cheap; time it).
- Payload does not affect driving in the current driver model (it uses only `.vacc`). In VECTO a heavier truck can be power-limited when accelerating — limitation of the current driver model, to check in `Driver.cs`/`DefaultDriverStrategy.cs` during the audit (**Open**).

**Per source:**
- **VDRI:** full file, every row is a waypoint, no shrinking. Default = constant VECTO reference payload (`SegmentTable.csv`, by group × mission) → only row 0 gets a value. Variation allowed, not blocked; it works for free on VDRI stop rows.
- **Typed input:** waypoint builder (`resolve_typed`) turns the user summary (total distance, number of stops, avg stop duration, start/end payload) into waypoints. Even stop spacing = **Assumption**, flagged.
- **GPS (parked):** rows are NOT collapsed (the force/consumption engines need the stopped seconds; aux power keeps running; time matters for charging). The GPS adapter writes the stop duration on the **first** zero-speed row of each stop, `stop = 0` on the rest. Then the same `stop > 0` rule works. Traffic stops: user gives them the same payload as before → no change. Speed-zero threshold for GPS = unsourced, **Open**. Check later how VECTO handles measured data (probably a time-based measured-speed cycle type, e.g. `MeasuredSpeedDrivingCycle` — not checked).

**UI table (Decided):** one table of stop rows (distance, stop duration, payload). UI only filters `stop > 0` for display, does no maths. Edits go straight into the stop rows of the waypoint list (no sync/apply step).

| Source | Editable |
|---|---|
| VDRI | payload + stop duration (distance locked). Any edit → labelled a user route, not the VECTO template; original file untouched |
| GPS | payload only |
| Typed | everything |

Removing a stop from payload changes = give it the same payload as before (it stays a stop for driving).

**Open:** do real VDRI files end with a row with `stop > 0`? If yes, linear would put `payload_end` on the final stop and the truck never drives with it. Decide: count the end stop or ignore it like row 0.

**Open (app layer, later):** server-side state between UI calls; whether VDRI passes through the resolver (27 Sep "one path for everything" rule vs. reading VDRI directly).

### Code
See `src/engine/payload_engine.py` (`payload_engine` + `fill_payload`).
Test: `[0,0,1,0,0,1,0,0,1,1,1]`, linear 10→20 → `[10, nan, 12, nan, nan, 14, nan, nan, 16, 18, 20]` (5 stops). Hook-in: `w.payload = p` per waypoint, then driver model adds `'payload'` to each `rows.append`.

Driver model check (Bob's code): on arrival it sets `distance = target_distance`, so stopped rows carry exactly the waypoint distance.

---

## 3. PTO / MunicipalUtility stop time (Open, parked for driver model audit)

From `DistanceBasedDrivingCycle.cs` + `PTOCycleController.cs`:
- For rows marked `PTOActivityDuringStop`: real stop time = file `StoppingTime` + PTO cycle `Duration` (`Duration = last t − first t` of the PTO cycle file).
- Short stops (≤ 6 × TargetTimeInterval) run in 3 phases: idle StoppingTime/2 → PTO cycle → idle StoppingTime/2.
- Declaration file `Resources/Declaration/MissionCycles/MunicipalUtility_PTO_generic.vptoc`: t = 0…23 → **Duration 23 s**. File stop 2 s → **25 s per collection stop**, matches SR7 ~25 s. (The 31 s `PTO-cycle.vptoc` Bob found first is an Engineering Mode example, not declaration.)
- Bob's driver model uses only `target.stop` → misses 96 × 23 s = 2,208 s ≈ 36.8 min on MunicipalUtility. Does not affect payload placement or driving energy; affects time (charging) and PTO energy.
- BEV PTO energy: sibling file `MunicipalUtility_PTO_generic.vptoel` (not yet seen). VECTO docs list `P_PTO_el` with unit [Nm] — looks like a docs error, check against the C# reader.
- Why VECTO keeps PTO separate (Claude's reading of code/formats, not documented): VDRI is distance-based and can't hold a time profile during a stop; one drive cycle with swappable PTO files (.vptoc/.vptoel/.vptol); stop time follows PTO length automatically.

---

## 4. Force engine (I) — DONE, tested

Checked against `Vehicle.cs` and `CrosswindCorrectionCdxALookup.cs`.
- Rolling `cos(grad)·m·g·RRC`, slope `m·g·sin(grad)`, accel `m·a`; each power = force × `averageVelocity = (v1+v2)/2` (exact, forces constant over the step).
- Air (Declaration CdxA lookup mode): `P_avg = ρ/8 · CdA · (v1+v2)·(v1²+v2²)` — exact average of v³ over a linear-speed step. So **L = (v1+v2)(v1²+v2²)/8**, not 0.5·v_avg³. CdA looked up at `vAverage`, plus `DeltaAirDragAreaIMC`.
- grade % → angle: `arctan(grade/100)` (VECTO `InclinationToAngle`).
- `v2` clamped at 0 (driver model clamps new speed but stores unclamped accel; VECTO also falls back to Max(0, v)).

**K split (Decided 6 Oct, implemented 8 Oct):** neutral defaults reproduce the simple equation; VECTO values in `defaults.py` with source.
```
K_lin  = (g·sin θ + a)·v_avg          # × m
K_roll = Crr·g·cos θ·v_avg            # × m^β   (β applied in the power step; 1 = simple, 0.9 = VECTO LOT 3 eq. 3)
K_rot  = (Θ_red / r_dyn²)·a·v_avg     # not × mass (Θ_red = reduced rotating inertia, kg·m²)
P_wheel = m·K_lin + m^β·K_roll + K_rot + ρ·CdxA_eff·L
```
- Current settings: β = 1, Θ_red = 0, single Crr → results identical to the old K.
- VECTO axle-weighted Crr (per axle RRC_ISO, Fz_ISO, tyres w, load share s, β) = separate per-vehicle step, later. Load-dependency effect on rolling force (arithmetic): tyre load/Fz_ISO 0.85 → +1.6%, 0.7 → +3.6%, 0.5 → +7.2%, 0.3 → +12.8% vs fixed label Crr. Output effect ≈ rolling share × that (approximation); rolling share not yet measured — get it from Bob's model.
- r_dyn: from tyre datasheet rolling circumference / 2π, or VECTO `Declaration/Wheels.csv` (columns not yet seen — **Open**). Θ_red needs wheel inertia (Wheels.csv?) + motor/gearbox inertia (OEM) — **Open**.

Code: `src/engine/force_engine.py`. Tests passed: v=20, a=0, flat, Crr 0.0055 → (0, 1.0791, 0, 4000, 20); v=10, a=1 → (10.5, 0.56653, 0, 580.125, 10.5). All rows in one call by passing columns as arrays.

---

## 5. Weather step (W) — notes for when it's written

- CdxA_eff speed range: VECTO computes **60–105 km/h** (5 km/h steps), **below 60 km/h uses the 60 value**, linear interpolation by speed, error on extrapolation (crosswind verification note; LOT 3 Table 55). Bob's old clamp 60–100 must be **60–105**, and the clamp belongs in the weather step, not the force engine. Rounding v to whole km/h (6 Oct table idea) is a small approximation; VECTO interpolates.
- `DeltaAirDragAreaIMC`: extra ΔCdxA in VECTO's CdxA lookup; meaning unknown (maybe `Declaration/IMC-Tech.csv`). **Open** — Bob to search the repo. Argument, default 0.
- `VAirBeta` mode (measured air speed + yaw per cycle row) — relevant later for telemetry with wind. Parked.
- Lookup uses `v_avg` from the force engine.

---

## 6. Driver model audit — items added today (Open)

- Existing: 6 bugs (2 red: infinite loop risk, segment- vs step-level accel; 2 orange: div/0 in braking distance, vacc_lookup None; 2 yellow).
- New: on arrival it sets `speed = target_speed` directly and drops the overshoot `ds` — speed jump without matching accel.
- Stores unclamped `acc` when new speed is clamped to 0 (handled in force engine by clamping v2).
- PTO stop time missing (section 3).
- Power limit at high mass (VECTO) — check `Driver.cs`.
- A waypoint with stop 0 but target speed 0 → brakes to 0 and pulls away (momentary stop).
- Add `'payload'` to rows (section 2).

---

## 7. Next step (at that time)

**P_aux** (then 0.0 pending research into DC/DC converter efficiency for BEV; cabin heating unmodelled). Ground in VECTO BEV auxiliary handling before choosing values. Then driver model audit. (P_aux was traced on 8 Oct — see `2026-10-08_session-closeout-paux.md`.)
