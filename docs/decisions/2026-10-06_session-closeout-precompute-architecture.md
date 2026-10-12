# HDEV session close-out: precompute architecture, weather, crosswind (30 Sep – 6 Oct 2026)

> Bundle note (12 Oct): the crosswind function in section 7 is an OLD loop version. The current numpy version is in `src/engine/crosswind_engine.py` (verified 7 Oct). The pipeline in section 2 has since changed for payload (payload now runs on waypoints BEFORE the driver model, see 8 Oct close-out). Everything else in this file still stands unless a newer file says otherwise.

Purpose: hand-over so a new chat can continue without re-deriving anything. Items are marked **Decided**, **Open**, **Assumption** (simplification, not sourced fact) or **Suggestion** (Claude's proposal, not sourced).

Flow diagram page (published artifact): "HDEV data flow", version 2. It shows every step's inputs, work and outputs, the rerun table and open items.

---

## 1. Current focus and next step

- Bob is writing the **precompute layer first** (pure functions): F (crosswind), G (driver model), H (payload resolver), I (`force_coeffs`), then W (`weather_for_rows`).
- **Next action:** finish `crosswind_engine` (version in section 7), run old vs new for one `v_ref`, and confirm the new values are about `dh/h` lower (≈2.5% for h = 4 m, dh = 0.1 m). That difference is the height-grid bug fix.
- Then check the `cdxa_eff` formula against the VECTO source (see section 7, open check).

---

## 2. Pipeline (Decided)

```
A Inputs (project JSON) → B Validate (Pydantic, later) → C Resolve (defaults.py, write last)
→ D Calendar → E Group
→ F crosswind_engine   (W1, W2 table: wind × vehicle speed)
→ G driver model       (1 s Rows, once per day-type)
→ H payload resolver   (row.payload)
→ I force_coeffs       (K-parts, L, speed index per row; no mass, no ρ)
→ W weather_for_rows   (rho_rows, cdxa_rows)            ← added this session
→ J force_engine       (P_wheel per row)
→ consumption          (efficiency by sign + P_aux, sum → kWh)
→ L battery sizing → M charging week → N sweep → O costs/CO₂/report
```

- Weather enters at **W**, mass enters at **J**. Everything above W is computed once and reused.
- Naming note: "K" is the force coefficient. The consumption step is called "consumption" (not K) to avoid confusion.

---

## 3. Force and consumption decisions

- Per row: `P_wheel = m·K + ρ·CdxA_eff·L` (**Decided**). P_wheel is linear in m and ρ.
- Consumption per row: P_wheel > 0 → `P_wheel / η`; P_wheel < 0 → `P_wheel × η_regen`; plus P_aux; then sum (**Decided**).
- **Why battery kWh is not linear in m or ρ:** a change in m or ρ can flip a row's sign (regen ↔ pushing), which switches the efficiency formula. So mass and ρ must go into each row **before** the efficiency step. You cannot compute a day's kWh once and scale it. Wheel energy (before efficiency) does separate exactly; battery kWh does not.
- Efficiency and P_aux must be set before computing kWh; changing them means recomputing consumption (cheap, K and L reused).
- Earlier "closed-form battery sizing" is corrected: because of the regen switch, energy is only piecewise linear in mass. Mode B battery sizing iterates until the size stops changing (**Suggestion**).

### VECTO resistance equations vs current model (LOT 3 report, eqs. 2–12)
Only two preprocessing differences were found:
1. **Rolling resistance (eq. 2–3):** VECTO's RRC is a load-weighted mean over all axles (truck + trailer), with load dependency `β = 0.9`, per-axle `RRC_ISO`, `Fz_ISO`, tyres per axle `w(i)`, load share `s(i)`. With `s(i)` fixed, rolling force ∝ **m^0.9**. It still separates: split K into `K_lin` (grade + accel, × m), `K_roll` (× m^0.9), `K_rot`.
2. **Rotating mass (eq. 10–11):** `F_acc = (m + Θ_red / r_dyn²)·a`. The rotating part doesn't scale with payload, so it gets its own mass-free column `K_rot = (Θ_red / r_dyn²)·a·v`.
- **Decided approach (motto):** include VECTO parameters as arguments, with neutral defaults that give the simpler equation back (`β = 1` → single Crr; `Θ_red = 0` → no rotating mass). VECTO defaults (e.g. `β = 0.9`) are cited separately. Both live in `defaults.py` with sources, and whichever was used goes in the assumptions list. Later, compare one route with VECTO values vs neutral to see if it matters.
- Size of effect: no sourced numbers. Arithmetic only: at 2× the reference mass, m^0.9 gives ~7% less **rolling** force than a single Crr. Rotating mass matters mainly in stop-start driving.
- VECTO also holds the crosswind factor constant below 60 km/h (Table 55), matching the 60 km/h lower clamp.
- **Open:** paste current `force_coeffs` to check which of these it already covers.

### Gaps outside preprocessing (consumption step, Open)
Motor/inverter efficiency fixed (literature: speed-dependent, Zacharof et al. 2024); gearbox/axle fixed 0.98 vs VECTO loss maps; P_aux = 0; no battery internal-resistance loss while driving; no regen power cap; driver doesn't react to vehicle power limits (**Assumption**). The project's VECTO docs (2014/2016) are diesel-only; VECTO 3.x electric documentation or source (code.europa.eu) is needed to ground these. Note: Regulation 2017/2400 consolidated text (incl. Annex Xb electric components) has since been added to the project knowledge base.

---

## 4. Weather (Decided unless marked)

- **Temperature:** only affects ρ = P/(R·T) (T in K inside the calculation). Computed **inline**, no table, no range needed; any value works. P and R are arguments (P fixed = **Assumption**; defaults with sources in `defaults.py`).
- Integer °C is fine: a 0.5 °C rounding moves ρ by at most ~0.2% (from ρ ∝ 1/T), drag share only.
- **Wind:** effect of integer rounding must be checked by comparison (CdxA is non-linear in wind). Store real floats in the weather table; round or interpolate only at lookup.
- **Daily vs hourly:** same function, different data. Start with **daily values (option A)**. Option B = mean over drive hours (needs hourly DMI data + drive hours; done in `build_weather`). Option C = each row uses its own hour's T and wind (needs departure clock time). Compare on one year before switching. Hourly doesn't add multiplications, it only removes reuse between identical days.
- **Don't average by calendar day across years** (removes extremes; crosswind non-linear). Keep the real daily series per year, T and wind paired by date. Several years = more samples / year-to-year spread. Worst day kept as its own case for sizing.
- **Ranges vs history:** ranges are for building the CdxA table (physics). History gives each date's T and wind for the year analysis. Single-scenario/slider questions need no history.
- **Sensitivity** (e.g. +X °C all year, or harshest day −X °C) is applied to the date table, then recomputed/looked up.

### DMI code (Bob's draft) — to change
- Split into `fetch_dmi(...)` (download once, save raw file named by arguments) and `build_weather(...)` (pure: time zones, align T and wind by date, drop days missing either, coverage check per year → date table).
- `concat` currently leaves unaligned NaNs; `min_days=300` over 10 years is weak; daily mean includes night (**Assumption**); check each station's wind measurement height vs `h_ref`; return station distance for the assumptions list.

---

## 5. Lookup tables and speed (Decided)

- K, L per row: once per route/day-type (one day-type for consumption if every working day drives the same route; weekends = 0; a half day = its own route).
- **CdxA_eff:** depends on wind and vehicle speed only. Table rows = wind speeds (`v_ref` list), columns = 60–100 km/h (41). E.g. 10 winds → 410 values.
- Per row: `idx = v_kmh_clamped − 60` (computed once in `force_coeffs`); `cdxa_row = table[wind_row, idx]` (numpy indexing, no loop).
- Wind between table rows: **linear interpolation** between rows (or nearest row). No regression. Outside the range: widen the range or raise an error, never extrapolate.
- A kWh lookup table over (T, wind, mass) is only an optional speed-up; first write the direct per-day calculation and time it.
- **Vectorize:** store rows as numpy arrays per column (not lists of Row objects). Row-wise steps (`force_coeffs`, W, J, consumption) vectorize (e.g. `np.where(P>0, P/eta, P*eta_regen)`). The driver model and charging env stay loops (each step depends on the previous).

(Bundle note: the speed range was later corrected to **60–105 km/h** per VECTO, and the speed clamp moved from the force engine into the weather step — see 8 Oct close-out section 5.)

---

## 6. Caching, scenarios, functions (Decided)

- Each step's result is cached by a key built from **all** its inputs; reruns only start at the first step whose inputs changed. Add the caching layer **after** engines are correct.
- Write engines cache-ready now: all inputs as arguments, return results, no globals, no in-place mutation, same input → same output. Network/disk access is the exception → separate fetch from pure processing.
- User's original project JSON is never overwritten. A scenario = base project + small list of changes. Same mechanism serves interactive edits, sweeps and Monte Carlo.
- Rerun table (from the flow diagram page): route → G; wind → W (new F row) then J; Cd/A → `cdxa_eff` then W, J; vehicle height / group / h_ref → F; payload/mass → J; temperature → W then J; efficiencies/P_aux → consumption; battery size → J (mode B) then M; arrival/departure, charger kW, policy, site limit → M; prices → M (cheapest-first), O.
- Certainty: not "100 minus uncertainty". Input uncertainty → Monte Carlo ranges (JCGM 101:2008); model uncertainty → validation against VECTO runs or measured data.

---

## 7. Crosswind function (in progress at the time — SUPERSEDED by src/engine/crosswind_engine.py)

### What it does (plain)
Averages the airflow over all wind directions (0–359°, equal likelihood, VECTO eq. 6) and over the truck's height (ground to roof, wind profile `v_ref·(h/h_ref)^wind_exp`). For each direction and height: `v_air² = (v_veh + v_wind·cosφ)² + (v_wind·sinφ)²` (VECTO eq. 7); yaw angle β; extra drag `a1·β + a2·β² + a3·β³` (VECTO's Δcd(β), generic per vehicle type; current a1–a3 are tractor-semitrailer).

- **W1** = average(v_air²) / v_veh²
- **W2** = average(extra_cd(β)·v_air²) / v_veh²
- Two averages because Cd is constant across directions (comes out of the average), while extra_cd(β) varies (stays inside).
- (Resolved 7 Oct: `CdxA_eff = CdxA(0)·W1 + W2`, polynomial gives ΔCdxA in m².)

### Bug fixed
Old `heights = np.arange(0, h + dh, dh)` → 41 slices for 40 → inflates by dh/h (~2.5%). Fix: midpoints, exactly `round(h/dh)` slices.

- All inputs are arguments (pure maths, works for any country): `v_ref` list, `h_ref`, `vehicle_height`, a1–a3, `wind_exp` (was hard-coded 0.2), `dh`, speed range. Values come from `defaults.py` with sources.
- Bob wants variable names that follow VECTO or are plainly intuitive, and explanations that assume no prior knowledge of the function.
- Still open from before: the `v_ref` conflict; removal of the old `vehicle.T` reference.

---

## 8. Input JSON and data flow (Decided)

- One project JSON with sections (vehicles, routes, assignments, calendar/environment), each with its own Pydantic schema. A chatbot can fill one section using that section's schema. Reusable libraries (VDRI templates, saved routes, vehicle library) are separate files.
- "Skip a step" (e.g. user-supplied kWh/km) is a resolver override that bypasses F–J and is flagged in the assumptions list.
- Validate (Pydantic) comes with FastAPI later. Resolve is written last: its field list comes from what the engines read.
- Calendar = one row per date (operating yes/no, day-type, T, wind). Consumption doesn't read it; it's used for weather lookups, the charging week sequence and annual totals.
- Battery: mode A = real vehicle (datasheet mass + kWh, no loop); mode B = size it (glider mass + kWh ÷ pack kWh/kg + payload, iterate). Max GVW is a legal check, not the vehicle mass. Sources for glider mass and pack density still needed. Vehicle group (Reg. 2017/2400 Annex I) selects crosswind coefficients and defaults; vans (N1) are outside VECTO HDV scope.

---

## 9. Charging (Decided unless marked)

- Charging is simulated per **plug-in session** (arrival → next departure), not per calendar day. Sessions of different lengths are fine.
- Bob's env already stops at departure and when need is met; JIT/EDF use real `depart_time`, so no false midnight deadline. The problem is only the **episode end** (tester fixed at 21 h) cutting long sessions.
- **Suggestion:** simulate one representative week per temperature bin (2,016 steps at 5 min; easy). Run two weeks, keep the second, so Monday starts at a realistic SOC. The only rollover is a real shortfall at departure.
- Policies (ASAP, JIT, planned cheapest-first using Energidataservice hourly prices) live outside the env; the env enforces physics only. MADDPG is no longer part of HDEV (the hard-coded `/21` normalization only affected it).
- Simulate as a depot (site cap couples vehicles). Order: battery → charger power → policy → site peak. Sweep over finite real option lists, skipping impossible combinations. OCPP cost and ramp-up times need supplier data.

---

## 10. Working preferences (from this session)

- One step at a time; lock minimal correct versions first; don't change established plans mid-explanation.
- Plain, simple explanations; no unexplained new variable names; show mapping to Bob's existing names.
- Ground in VECTO sources; flag assumptions; no invented numbers.
