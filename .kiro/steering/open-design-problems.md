---
inclusion: manual
---

# Open design problems — index only (do not answer here)

Pointers to the two open-design docs, one line per open question. These are **not** resolved here. For the full status and the known-contradictions list see #[[file:docs/design/status-and-known-contradictions.md]].

## Year / day / week simulation — #[[file:docs/design/year-and-day-simulation-problem.md]]
- How full-year-per-date, grouping into weather bins, and representative weeks fit into one consistent annual number.
- Whether hourly weather (option C) breaks grouping, and if so whether every operating date is computed directly or binned another way.
- How consumption (per day-type × weather) hands over to charging (per session/week with SOC carry-over): energy per session, arrival SOC.
- Where Monte Carlo draws sit on top of the year/day structure.
- Whether routes/calendar need a per-date departure clock time (needed by option C).
- How to choose temperature/wind bins defensibly without inventing numbers.
- How to structure cache keys so one changed input reruns only the minimum.

## Payload: stop rows then fill — #[[file:docs/design/payload-stop-rows-then-fill.md]]
- Does a real VDRI file end with a `stop > 0` row — count the end stop or ignore it like row 0 (affects linear `payload_end`)?
- GPS speed-zero threshold for "stopped" (unsourced).
- Driver model still needs `'payload'` added to its row dicts.
- Where the edited waypoint list lives between UI steps (browser vs server-saved file).
- Whether forward-fill-then-copy or a vectorised post-driver lookup is the cleanest place for the "inflation" to per-second rows.
- Which property-based tests are worth writing for `payload_engine` and `fill_payload`.
