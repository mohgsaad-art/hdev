# HDEV session close-out: crosswind done, payload designed (6–8 Oct 2026)

> Bundle note (12 Oct): **section 4 (payload schedule by distance) is SUPERSEDED** by the 8 Oct design (`2026-10-08_session-closeout-payload-force.md` section 2 and `docs/design/payload-stop-rows-then-fill.md`). The rules "VECTO templates constant only" and "VDRI never altered" were also relaxed on 8 Oct. Sections 2, 3, 5, 6 still stand.

Hand-over for a new chat. Marked **Decided**, **Open**, **Assumption** (not sourced), **Suggestion** (Claude's proposal).
Related notes: crosswind verification, payload-resolver design (superseded), VECTO declaration defaults, previous close-out (precompute architecture).

---

## 1. Where we are

Precompute order (at that time): F crosswind → G driver model → H payload → I `force_coeffs` → W `weather_for_rows`.

- **F crosswind_engine: DONE and verified against VECTO.**
- **H payload_engine: design settled, function written and tested** (section 4 — superseded).
- **Next:** I `force_coeffs`. G driver model audit (6 known bugs) still pending; Bob chose to do payload first.

---

## 2. Crosswind (step F) — DONE

### Settled from VECTO source (user manual, `AirDrag.cs`, `VCDV_parameters.csv`, `CrosswindCorrection*.cs`, `Cdv_Generator_VECTO3.2.xlsx`)
- Yaw polynomial a1–a3 gives ΔCdxA in **m²** (`.SI<SquareMeter>()`), β in **degrees**.
- **CdxA_eff = CdxA(0)·W1 + W2.** Only the product CdxA(0) is needed, not Cd and A separately.
- Wind profile exponent 0.2; VECTO declaration wind 3 m/s at h_ref 4 m.
- VECTO: 10 height slices at midpoints, 0–180° in 10° steps (trapezoid), speeds 60–105 km/h, below 60 km/h use 60 km/h value, linear interpolation by speed, error on extrapolation.
- VECTO does **not** clamp yaw; with 3 m/s it never exceeds ~10.3°.
- `VCDV_parameters.csv` coefficient sets: RigidSolo, RigidTrailer, TractorSemitrailer, CoachBus (= SR7 Table 10) + MediumLorriesRigid (−0.0015, 0.0086, −0.00029), MediumLorriesVan (0.0032, 0.00532, −0.00028).

### Decided: yaw clamp at 10° (must be in every client report)
- Polynomial only valid 0–10° (SR7); for tractor-semitrailer it peaks ~13° and goes negative >19.9° (fit artefact). Danish wind (DMI 5.028 m/s at 10 m) pushes yaw past 10° at low speed.
- **Decision (Bob):** clamp β at 10° via argument `beta_limit_deg` (None = VECTO behaviour).
- Report wording: "Above 10° yaw, ΔCdxA is held at its 10° value. VECTO's polynomial is only valid 0–10° and no sourced curve with coefficients exists above that. CFD (Askerdal et al. 2024) indicates drag keeps rising, so this likely underestimates air drag in strong wind at low speed."
- Drag still rises with wind under the clamp (tractor-semitrailer, CdxA(0) 5.8, h 4 m, wind at 10 m): 60 km/h → 6.752 / 7.558 / 8.380 m² at 3 / 5 / 8 m/s; 100 km/h → 6.226 / 6.752 / 7.496 m².
- Alternatives examined, not adopted: linear continuation (slope at 10° = 0.207 m²/°), regression in wind speed. At 60 km/h, 7 m/s: clamp 8.11, linear 8.68, regression 9.52 m² (none sourced).
- Literature: Askerdal, Fredriksson, Laine (2024) Vehicle System Dynamics (CFD to 60°, drag rises, no coefficients; check Fig. 3b); NASA TM-2006-213489 (only ±14°, plots only).

### Final function
See `src/engine/crosswind_engine.py` (tests passed: 0.006% vs VECTO Excel, runs instantly → no caching needed).
- Internally 4D (wind × speed × direction × height); direction and height are averaged away. Output is 2D. Vehicle height is an input → new height = rerun (cheap).
- Ranges are call arguments: speeds 60–105 km/h (VECTO); wind range/step is HDEV's choice (top must cover DMI max, never extrapolate).
- Works with a range (lookup table) or a single value (direct call) → weather step can later call it with each day's actual wind instead of interpolating (**Open**, decide at step W).

---

## 3. VECTO declaration data found (repo `VectoCore/VectoCore/Resources/Declaration/`, stable branch)

- **Mission cycles** (`MissionCycles/`): trucks LongHaul, RegionalDelivery, UrbanDelivery, MunicipalUtility, Construction; buses HeavyUrban, Urban, Suburban, Interurban, Coach. Plus MunicipalUtility PTO files (.vptoc/.vptol/.vptoel; meaning of endings not checked). Matches SR7.
- **`SegmentTable.csv`**, **`Payloads.csv`**, **`Body_Trailers_Weights.csv`**: full detail in `2026-10-07_vecto-declaration-defaults.md`.

### Mission cycle analysis (Bob's Colab script)
| Cycle | km | usable stops (excl. start/end) | median / max stop [s] |
|---|---|---|---|
| LongHaul | 100.2 | 3 | 10 / 45 |
| RegionalDelivery | 100.0 | 10 (8 in first 23 km) | 20 / 314 |
| UrbanDelivery | 100.0 | 104 | 15 / 305 |
| MunicipalUtility | 11.2 | 101 (96 with PTO) | 2 / 38 |
| Construction | 99.9 | 39 | 15 / 200 |
- No stop is longer than ~5 min → stops are traffic-length; duration cannot identify deliveries.
- Columns: s, v, grad, stop (+ `hw` in LH/RD — Bob: highway flag, unverified; + `pto` in MU).

---

## 4. Payload (step H) — SUPERSEDED on 8 Oct (kept for history)

The 7 Oct design used a *payload schedule* (distance, payload) pairs written by a resolver, and `payload_engine(row_distance, change_distance, payload_kg)` using `np.searchsorted` to give every driver-model row its payload after the driver model ran. It was replaced on 8 Oct by the "write payload on stop rows of the waypoints, forward-fill before the driver model" design.

### Resolver rules noted (step C, written last) — still valid
- A waypoint with stop time > 0 must have target speed 0 (VECTO rule, `DistanceBasedDrivingCycle.cs` throws otherwise).
- Don't count the depot stop at distance 0 as a payload change.
- Dwell default 45 min/stop is Bob's own default (unsourced, flag).
- Report must state: in-cycle payload variation is an HDEV addition beyond VECTO.

---

## 5. Driver model notes (from Bob's `DriverModel` code)
- Rows are dicts: `time, distance, speed, accel, grade, dt_s`. Stop rows: speed 0, distance = stop's distance.
- Should use VECTO's official `Truck.vacc` (`Resources/Declaration/VACC/`).
- Six audit bugs still open (infinite loop risk; segment vs step acceleration; braking-distance division by zero; `vacc_lookup` returns None; missing early exit; dead logic).
- Earlier decision: store rows as numpy arrays per column (not list of dicts) for vectorised steps.

---

## 6. Ideas parked (not now)
- **AI route adapter** (4th input path): AI turns coordinates/descriptions/call-out lists into the standard waypoint JSON; validated + user-confirmed; guesses flagged. Real road distance via routing service (OSRM, OpenRouteService, GraphHopper, Google/Mapbox — check limits/licences); elevation from a terrain model (e.g. Danish height model). GDPR question for call-out coordinates.
- **GPS adapter**: must output the same row columns as the driver model (time, distance, speed, accel, grade); may need distance from coordinates or speed×time; stop detection is its own task. Wait for a real sample file.
