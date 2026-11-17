# Payload resolver (step H) — design notes (7 Oct 2026)

## Purpose
Give every 1 s row from the driver model a payload [kg] so step J can use m = vehicle mass + payload per row. Payload only; legal mass check and rolling resistance elsewhere.

## Decided (Bob, 7 Oct 2026)
- Payload changes only at stops (flat between stops, jump during the stop).
- Shapes: constant, linear (start → end, even steps per stop), custom per stop. No curvature exponent (old `payload_shape` exponent 2 dropped — unsourced). Add more only if needed.
- Default payload: VECTO reference payload from `SegmentTable.csv` / `Payloads.csv`, in `defaults.py` (supersedes earlier "default 0").
- UI unit: tonnes. (Suggestion: convert to kg once in the resolver; engine sees kg only.)
- VECTO .vdri files are NEVER altered. Choosing a VECTO cycle = accepting its distance, stops and stop times.
- **VECTO template → payload follows VECTO: constant over the whole cycle** (no in-cycle variation on VECTO cycles). The user may still change the constant value (e.g. VECTO reference, VECTO 10% load, or own tonnes) for sensitivity. No snapping/placement rule → no extra assumption.
- **Payload variation only for the user's own routes**: hand-typed, GPS/telemetry, or (future) AI route adapter. There the stops are real, so payload-change stops = the user's stops.
- Payload function inputs: row `'distance'` [m] (driver model dict key), payload-change stop distances [m] (from waypoints with stop > 0, depot start excluded), payload per stretch [kg] (N stops → N+1 values). Output: payload per row. Change values come from the resolver, the function only fills every row. Constant payload = zero stops, one value.
- Snapping rule (spread by distance, snap to nearest free VECTO stop) was discussed and parked; add later only if clients ask.

## VECTO mission cycle analysis (Bob's Colab run, stable branch, 7 Oct 2026)
| Cycle | km | stops (incl. start/end) | inner stops | stop time median / max [s] | notes |
|---|---|---|---|---|---|
| LongHaul | 100.19 | 5 | 3 (2.9, 62.0, 62.1 km) | 10 / 45 | columns s,v,grad,stop,hw |
| RegionalDelivery | 100.00 | 12 | 10 | 20 / 314 | 8 of 10 inner stops in first 23.2 km; none from 23.2 to 96.8 km |
| UrbanDelivery | 100.00 | 105 | 104 (no end stop) | 15 / 305 | ~1 stop/km, spread through cycle |
| MunicipalUtility | 11.24 | 103 | 101 | 2 / 38 | 96 stops with PTO active (collection part 2.6–5.5 km, 20 m/40 m spacing); column `pto` |
| Construction | 99.89 | 41 | 39 | 15 / 200 | clustered, last inner stop at 65.6 km |
- No VECTO stop is longer than 314 s → stop duration cannot separate delivery from traffic stops.
- `hw` column in LongHaul/RegionalDelivery: Bob believes it is the highway flag (not verified from source).
- MunicipalUtility PTO stops show stop time 2 s; VECTO adds the PTO cycle duration on top (`StoppingTime + IdleController.Duration` in `DistanceBasedDrivingCycle.cs`) — consistent with SR7's ~25 s collection stops (inference).
- 2014 VECTO doc quoted urban delivery as 27.8 km; current file is 100 km — cycle has been updated since.
