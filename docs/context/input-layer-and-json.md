# Input layer, project JSON and UI — decisions so far

Sources: past chats "Reading recent messages" (2 Sep 2026), "FastAPI implementation roadmap" (27 Sep 2026), "Reading previous chats" (6 Oct 2026), 8 Oct payload close-out. Tags: **Decided**, **Open**, **Assumption** (unsourced), **Suggestion** (Claude's, not decided).

## Route input paths (Decided 8 Oct — supersedes the earlier "three paths")
Four route inputs, all ending as a **waypoint list** (VDRI-style: distance m, target speed km/h, altitude/grade, stop s, + payload):
1. **VDRI** (VECTO mission cycle): every VDRI row is a waypoint; goes straight into the driver model (no resolver needed). Defaults to constant VECTO reference payload. User may edit stop durations and payload; once edited it is labelled a **user route**, original file untouched.
2. **Typed input**: user gives a summary (total distance, number of stops, avg stop duration, start/end payload, road type…) → `resolve_typed` builds waypoints → table is fully editable. Even stop spacing = **Assumption**.
3. **GPS / telemetry** (parked): already time-based rows; adapter marks stop duration on the first zero-speed row of each stop. Only payload editable.
4. **AI adapter** (future): turns coordinates / descriptions / call-out lists into a waypoint template, using a routing API for real road distance. Must be validated and user-confirmed; guesses flagged.

## Earlier typed-input resolver (2 Sep 2026) — partly superseded
- Artefacts produced then: `TableLeg` dataclass, `ResolvedDay` dataclass, `resolve()` function, HTML test harness showing assumed values in orange.
- Rules then: day = one continuous waypoint sequence; stops default 0; dwell default 45 min/stop; default speeds 30/50/80 km/h deep urban/urban/non-urban; speed wins over end time; gradient flat by default. **The 45 min and 30/50/80 km/h are Bob's judgement values, unsourced — must be labelled assumptions.**
- Payload part (default 0, linear interpolation, curvature exponent 2) is **superseded** by the 7–8 Oct payload design.
- Open from then: per-leg time windows in the UI; `charger_available` has no producer at the input layer.

## Project JSON (Decided 27 Sep / 6 Oct)
- **One project JSON** with sections: `vehicles`, `routes`, `assignments` (with a `count` field for identical vehicles), `calendar/environment`. Each section has its own schema (Pydantic later, with FastAPI). A chatbot can fill one section using that section's schema.
- Reusable libraries are separate files: VDRI templates (`data/cycles/standard/`, read-only), saved user routes (`data/cycles/user/` as JSON — **Suggestion**), vehicle library.
- **Defaults live only in Python (`defaults.py`)**, never in JavaScript or as Pydantic field defaults — so the assumptions list knows every default that was used. Raw models default to `None`; only the resolver fills and records. Each default carries a source or an ASSUMPTION label.
- The user's original project JSON is never overwritten. A scenario = base project + a small list of changes.
- "Skip a step" (e.g. user-supplied kWh/km) = resolver override that bypasses F–J and is flagged.
- Resolve is written LAST: its field list comes from what the engines read.

## UI (Decided)
- Step-by-step pages that map one-to-one to JSON sections. Basic fields up front, "Advanced" toggle, pre-filled defaults shown in orange/terracotta.
- The UI is a **dumb form**: collects inputs, sends raw JSON. **No maths or resolver logic in JavaScript.** Filtering rows for display (e.g. show only `stop > 0`) is allowed.
- Stop table (payload): one table of stop rows (distance, stop duration, payload); edits go straight into the waypoint list. Editable columns depend on source (see payload design).
- **Open:** where UI state lives between steps (browser vs server-saved `projects/<id>.json` — Claude leaned server-saved as an audit record; not decided).

## Coding order suggested on 27 Sep (Claude's suggestion; Bob later chose engines-first)
`defaults.py` → `schemas.py` → `resolve_vehicle` → `resolve_route` + typed adapter → VDRI adapter + cycle library → `resolve_assignments` → `build_calendar` → `group_runs` → `to_waypoints` → FastAPI endpoints → UI pages. Test steps 1–9 with hand-written JSON before any server/UI.
Status 12 Oct: Bob is writing the pure engine functions first (precompute layer), resolver last.
