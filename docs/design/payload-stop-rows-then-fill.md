# Design: payload written on stop points only, then inflated to every second

Status: **Decided and coded** (8 Oct 2026). Code: `src/engine/payload_engine.py`. Full history: `docs/decisions/2026-10-08_session-closeout-payload-force.md` section 2.
Tags: **Decided**, **Open**, **Assumption** (unsourced), **Suggestion** (not decided).

## The idea in one paragraph
Payload only changes at stops (a delivery or pickup happens when the vehicle stands still). So the payload engine does not work on the second-by-second rows at all. It works on the short **waypoint list** (the VDRI rows, or the waypoints built from typed input). It writes a payload value on **row 0** (start payload) and on **every waypoint with `stop > 0`**, and leaves every other waypoint blank (NaN). A tiny separate step, `fill_payload`, forward-fills the blanks just before the driver model. The driver model then copies the payload of the current waypoint onto each 1-second row it generates — exactly the same way it already copies grade. Result: a few dozen numbers are decided by the user/engine, and they get "inflated" to tens of thousands of per-second rows for free.

## Data flow
```
waypoints (VDRI / typed / GPS / AI)      stop column
        │                                   │
        │                     payload_engine(stop, shape, start, end, custom)
        │                                   │  → payload column: value on row 0 and stop rows, NaN elsewhere
        │                                   ▼
        │                     UI stop table (shows only stop > 0 rows; user edits payload / stop time)
        │                                   │  edits written straight back into the same waypoint rows
        ▼                                   ▼
                       fill_payload(payload)   → every waypoint has a payload
                                    │
                         driver model (1 s rows)  → each row copies its waypoint's payload (like grade)
                                    │
                         force step J: P_wheel = m·k_lin + m^β·k_roll + k_rot + ρ·CdxA_eff·L,  m = vehicle + body + payload
```

## Why this shape (decisions behind it)
- **One rule for every source:** `stop > 0` marks a stop for VDRI, typed and GPS alike (GPS adapter writes the stop duration on the first zero-speed row of each stop). No special cases per source.
- **UI can edit before anything runs:** the user sees and edits the stop table before the driver model runs; no sync step, because the table *is* the stop rows.
- **No maths in the UI:** the UI only filters `stop > 0` for display.
- **Cheap sweeps:** a "+10 % payload" sweep multiplies the payload column without rerunning the driver model. A different payload *shape* needs a driver-model rerun (cheap; time it).
- **Driver model stays payload-blind:** it only copies the value. (Limitation: in VECTO a heavier truck can be power-limited when accelerating; the current driver model ignores this — **Open**, audit item.)

## Rules (Decided)
- Row 0 = depot start, never counted as a payload change even if it has a stop time.
- Each `stop > 0` row is one stop; consecutive stop rows are never merged (VDRI MunicipalUtility has genuine stops 20–40 m apart).
- Shapes: `constant`, `linear` (equal steps start→end — **Assumption**), `custom` (start + one value per stop). Negative payload → error; wrong custom length → error; linear with zero stops → error.
- Units: kg inside the engine, tonnes in the UI (convert once at the boundary).
- VDRI default: constant VECTO reference payload (`SegmentTable.csv`, by vehicle group × mission). Variation allowed. Any edit relabels the cycle as a user route; the original VECTO file is never changed.
- Removing a stop from payload changes = give it the same payload as before (it remains a stop for driving).
- Editable per source: VDRI → payload + stop duration (distance locked); typed → everything; GPS → payload only.
- Reports must state that in-cycle payload variation is an HDEV addition beyond VECTO.

## Tests already passed
`stop = [0,0,1,0,0,1,0,0,1,1,1]`, linear 10 → 20 → `[10, nan, 12, nan, nan, 14, nan, nan, 16, 18, 20]` (5 stops). `fill_payload` forward-fills and raises if row 0 is NaN.

## Open
- Does a real VDRI file end with a `stop > 0` row? If so, linear puts `payload_end` on the final stop and the truck never drives with it. Count the end stop or ignore it like row 0?
- GPS speed-zero threshold for "stopped" — unsourced.
- Driver model still needs `'payload'` added to its row dicts (`current.payload` on driving rows, `target.payload` on stopped rows, `waypoints[0].payload` in the first-stop loop).
- App layer: where the edited waypoint list lives between UI steps (browser vs server-saved file).

## What we'd like a second opinion on
- Is forward-fill-on-waypoints then copy-in-driver-model the cleanest place for the "inflation", or should the 1 s payload column be produced by a vectorised lookup after the driver model (e.g. `np.searchsorted` on row distance — the 7 Oct design that was dropped)? Constraint: the UI must be able to show and edit stop payloads *before* the driver model runs, and no logic may live in JavaScript.
- Property-based tests worth writing for these two functions.
