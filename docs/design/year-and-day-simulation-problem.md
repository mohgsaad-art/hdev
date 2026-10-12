# Design problem: simulating a full day and a full year when weather changes hourly

Status: **partly decided, partly open.** This is the area where we most want outside ideas.
Sources: close-out 6 Oct (sections 2–6, 9), chats "Reading previous chats" (6 Oct), "FastAPI implementation roadmap" (27 Sep), "Architecture design for multi-vehicle battery simulation engine" (9 May) and "Next steps for current project" (6 May). Tags: **Decided**, **Open**, **Assumption**, **Suggestion** (Claude's proposal, not decided). Where an older chat conflicts with a newer one, the newer one is listed as current and the older one is noted.

---

## 1. The problem in plain words
- The driver model produces **one row per second** for a working day (tens of thousands of rows).
- Weather (temperature → air density ρ; wind → effective drag area CdxA_eff) changes **every hour**, and from day to day across a year.
- Mass (payload, battery size) changes per scenario.
- Charging is a different time scale again: sessions run from arrival to next departure, can cross midnight and weekends, and the battery's state of charge (SOC) carries over.
- We want: (a) correct daily kWh, (b) correct annual kWh and cost, (c) a correct **worst day** for sizing, (d) correct charging behaviour across days/weekends, (e) fast enough for sweeps and Monte Carlo — without precomputing everything for every hour of every year.

## 2. What is already decided (the computation split)
**Principle (Decided): compute each thing at the frequency it actually changes.**

| Quantity | Changes with | Computed |
|---|---|---|
| W1, W2 crosswind tables | vehicle height, wind range | once per vehicle (step F), runs instantly |
| 1 s rows (speed, accel, grade, payload) | route / day-type | once per route/day-type (step G) |
| k_lin, k_roll, k_rot, L, v_avg | route / day-type | once per route/day-type (step I) |
| ρ per row | temperature | inline `ρ = P/(R·T)`, no table (step W) |
| CdxA_eff per row | wind × vehicle speed | table lookup + interpolation (step W) |
| P_wheel per row | mass, ρ, CdxA_eff | multiply-add over all rows (step J) |
| battery power per row | sign of P_wheel | `np.where(P>0, P/η, P·η_regen)` + P_aux (consumption step) |

- **Why kWh cannot simply be scaled (Decided):** a change in mass or ρ can flip a row from pushing to regenerating, which switches the efficiency formula. So mass and ρ must go into each row *before* the efficiency step. Wheel energy scales exactly; battery kWh does not. Consequence: every distinct (day-type × weather × mass) combination needs its own row-wise multiply-add — cheap with numpy, but it cannot be a single scaling factor.
- **Daily vs hourly is the same function, different data (Decided).** `weather_for_rows(rows, departure_time, temps_by_hour, winds_by_hour, cdxa_table) → rho_rows, cdxa_rows`. Daily = fill all 24 hours with the day's mean.
  - Option A: one T and wind per day (start here — Decided).
  - Option B: mean over the drive hours (needs hourly DMI data + drive hours).
  - Option C: each row uses its own hour's T and wind (needs a **departure clock time** on the route; rows currently only have time since start of drive).
  - Hourly does not add multiplications; it only removes reuse between days with identical weather. Decide B vs C by running one year both ways and comparing annual kWh and worst day (**Open**).
- **Weather history rules (Decided):**
  - Do **not** average the same calendar date across years (removes extremes; crosswind is non-linear). Keep each real year's daily series, T and wind paired by date. Several years = more samples / spread.
  - Keep the worst day as its own sizing case.
  - "Ranges" (for building the CdxA table) and "history" (which T and wind happened on which date) are different jobs.
  - Sensitivity (+X °C all year, harshest day −X °C) is applied to the date table, then recomputed.
- **Calendar and grouping (Decided 6 Oct):**
  - Calendar = one row per date: operating yes/no, which route/day-type, T, wind.
  - Consumption does not read the calendar; it is used for weather lookups, the charging sequence and annual totals.
  - "Group" = count unique combinations instead of simulating every date. Illustrative example (not data): 250 operating days might collapse to 2 day-types × 5 temperature bins = 10 runs, each multiplied by how many days it occurs.
  - **How many temperature bins (and how to bin wind) is Open.**
- **Caching (Decided):** each step cached by a key of all its inputs; reruns start at the first changed step. Added only after engines are correct. Engines are written cache-ready now.

## 3. Charging over days and weeks
- **Decided (6 Oct):** charging is simulated per **plug-in session** (arrival → next departure), not per calendar day. The env stops at departure or when need is met; JIT/EDF use real departure times.
- **Known problem:** the current testers/runners force a **21-hour episode** (`run_allocator_21h`, `test_policy_21h_with_logging`), which cuts long sessions (overnight + weekend). The env's `reset()` also randomises everything (thesis training legacy).
- **Suggestion (Claude, 6 Oct, not sourced):** simulate one **representative week per temperature bin** (2,016 steps at 5 min). Run two weeks and keep the second so Monday starts from a realistic SOC; the only rollover is a real shortfall at departure.
- **Older decisions (May 2026, earlier architecture):** "representative week, not representative day" (weekend SOC carry-over needs the 7-day sequence; ending SOC should equal starting SOC, otherwise that is a real finding); "day object as the fundamental unit" so a full year is just a calendar of day objects; "Phase 1 = representative week scaled to annual totals". The seasonal question was left open then.
- Cheapest-first policy needs an hourly price series (Energidataservice spot + tariffs) — not written.

## 4. Things that are NOT consistent yet (please flag, don't resolve silently)
1. **Full year per date vs grouping into bins vs representative weeks.** The 6 Oct notes keep a real per-date weather history for the year analysis, but also group dates into day-type × temperature bins, and the charging suggestion uses a representative week per temperature bin. How these three fit together for one consistent annual number is not written down.
2. **Hourly weather vs grouping.** If weather is hourly (option C), almost no two days are identical, so grouping by bins stops working for consumption. Then either every operating date is computed directly (cost unknown, must be timed) or hours/days are binned in some other way.
3. **Consumption days vs charging weeks.** Consumption is per day-type × weather; charging is per session/week with SOC carry-over. The hand-over (energy needed per session, arrival SOC) between the two is not designed.
4. **Monte Carlo.** Decided that input uncertainty → Monte Carlo ranges (JCGM 101:2008) and model uncertainty → validation against VECTO/measured data; also noted that Monte Carlo suits coincidence factor and peak charging better than payload. How MC draws sit on top of the year/day structure is not designed.
5. **Departure clock time.** Option C needs it; routes don't carry it yet; the calendar may need a per-date departure time.

## 5. Questions where we want outside ideas
- What is a clean, standard way to structure **day → week → year** simulation where: per-second physics is expensive-ish, weather varies hourly, SOC must carry over across sessions, and annual totals + worst-day + P10/P50/P90 are all needed?
- Is it better to (a) compute every operating date directly with vectorised numpy and skip grouping, (b) group into weather bins, or (c) a hybrid (exact for extreme days, binned for the rest)? What should be timed first to decide?
- How should the charging simulation consume the consumption results: one continuous year-long charging run at 5-min steps (is that cheap enough?), or representative weeks per bin scaled up?
- What are sensible, defensible ways to choose temperature/wind bins (if binning), without inventing numbers?
- How to structure the cache keys so a change in one input (e.g. payload) reruns only the minimum?

## 6. Hard constraints for any proposal
- Engines stay pure functions; all parameters as arguments; no globals; no in-place mutation.
- No invented numbers. Any bin count, threshold or resolution must be labelled a choice/assumption or come from a source.
- Must stay VECTO-auditable: the VECTO-equivalent case (one cycle, VECTO declaration weather 3 m/s at 4 m, constant reference payload) must be reproducible exactly.
- Logic in Python only. The UI only sends JSON.
