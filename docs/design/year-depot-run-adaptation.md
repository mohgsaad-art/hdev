# Adaptation plan: year-long depot charging run (item 14 / M3.9)

Status: **planned here first, then implemented as a NEW pure wrapper** (`src/charging/year_depot_run.py`).
Written for Step 9, item 14. The thesis env (`src/charging/ev_charging_env.py`) is **not changed in
place** - it imports `gym` and carries MARL/training legacy we do not want on the pure pipeline.

## Why the thesis env cannot be used as-is

The thesis `EVChargingEnv` was built for MADDPG training, and that shows up in four places that are
wrong for a real depot year:

1. **Fixed 21-hour horizon.** `run_allocator_21h` / `tester_21h_maddpg` end the episode at 21 h and the
   observation normalises `signed_time` by a hard-coded `/21`. A real session runs **arrival to next
   departure** and can cross midnight and whole weekends. 21 h cuts long overnight/weekend sessions.
2. **Random reset.** `reset()` draws arrivals, departures, SOC, battery sizes and the site target from
   `rng.uniform(...)`. A real run must walk the **deterministic, dated session sequence** the calendar +
   consumption produced (`src/resolver/session_handover.build_sessions`), not random draws.
3. **No SOC carry-over across dates.** Each episode starts from a fresh random SOC. In a real year the
   **ending SOC of one session is the arrival SOC of the next** (same truck). Weekend carry-over matters.
4. **`gym` dependency + MARL reward/observation.** The reward shaping and the 6-feature observation only
   exist for the RL agent, which is no longer part of HDEV. The pure path must not import `gym`.

## What the new wrapper does instead

`run_year_depot(sessions, chargers, site_limit_kw, dt, battery_params, ...)` is a **new pure function**
(no `gym`, no I/O, no in-place edit of the thesis env):

- **Real session length, not 21 h.** Each session runs for its own `(departure - arrival)` dwell.
- **Deterministic sequence, not random reset.** It walks `sessions` in the given chronological order (the
  `ChargingSession` list from `build_sessions`).
- **SOC carries date-to-date.** The ending SOC of a session becomes the arrival SOC of that truck's next
  session; `build_sessions` lays out a neutral carry-over and this run **overwrites it with the real
  ending SOC** from the OCV+Ri simulation.
- **Chargers shared under a site cap.** Concurrent sessions share the chargers and the whole site is held
  under `site_limit_kw`. The per-session target power is the JIT-style minimum (`energy / dwell`, capped
  by the charger rate), and when concurrent demand exceeds `site_limit_kw` the site target is split by the
  **pure equal-share / EDF allocators** we already have (`allocators_edf_es.py`,
  `flexibility_setpoints.py`) - reused as **pure arithmetic**, NOT by importing the gym env.

## Reuse without `gym`

`allocators_edf_es.py` and `flexibility_setpoints.py` take an `env` object and read attributes off it;
they do **not** import `gym`. The wrapper reuses the *math* (equal-share water-filling, `E/t` setpoint)
directly on plain arrays, so no `gym` import ever reaches the pure path. The per-session physics uses
`src/charging/charging_sim.simulate_session` (OCV + Ri), with `dt` a required argument.

## Flags / open items

- `dt` is Energinet-sourced and has no default (item 13). The caller passes it.
- The site-sharing policy here is the **JIT minimum-power + equal-share** baseline; cheapest-first needs
  an hourly price series (Energidataservice) that is not written. Flagged.
- This wrapper deliberately keeps the thesis env file untouched so the gym-dependent training code still
  works off-pipeline for whoever needs it.
