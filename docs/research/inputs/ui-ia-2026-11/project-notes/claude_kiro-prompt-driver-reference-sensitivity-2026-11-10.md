# Kiro prompt: what does the driver's fixed reference vehicle cost? (10 Nov 2026)

Do the whole task in one uninterrupted pass. Do not stop to ask; if something is unclear, choose the option that changes the least, write it down under "Choices I made", and carry on.

## 1. Background (read, do not change)

HDEV runs `driver_model` ONCE per route at a fixed reference vehicle, then computes energy for every payload and weather case with the true values. Inside the driver, look-ahead coasting (`coast_acc`, `coast_distance`) uses three fixed reference inputs:

1. `coast_mass` = reference mass (E2 empty + reference payload);
2. `rho` = 1.188 kg/m³ (VECTO, `DeclarationData.cs` line 74);
3. `cdxa` = `CdxA0 · W1 + W2` from `crosswind_engine` at VECTO declaration wind, 3 m/s at 4 m, Hellmann 0.2 (`hdev_test_harness_v1.7.py` lines 61–65, 214).

The energy step (`force_engine` + `consumption_engine`) always uses the true mass, the true air density from temperature, and the true wind.

**Question Bob wants answered:** how much does total energy (kWh/km at the battery terminals) change because the driver uses these reference values instead of the true ones, across a sensitivity range? This tells us the maximum error of the "run the driver once" design.

## 2. What to reuse (do not rewrite)

Repo `mohgsaad-art/hdev`, branch from `main`. New branch: `driver-reference-sensitivity-2026-11`. New folder: `docs/research/driver-reference-sensitivity-2026-11/`.

- Driver: `docs/research/drag-default-test-2026-11/_driver_dragtable.py` (copy into the new folder; it is the code of record with the drag table).
- E2 drag table: `docs/research/drag-default-test-2026-11/_e2_drag.py` and `e2_table()` in `run_steps.py` (variant V1).
- Energy chain: `_chain.py`, **Chain S** (EU standard-value maps), plus `src.engine.force_engine.force_engine`.
- Vehicle, cycles, aux, masses: `run_steps.py` (`VV`, `D`, `VM`, `LOADINGS`, aux per mission), `tests/driver_model/_vecto_vehicle.py`, and `docs/research/vecto/hdev_test_harness_v1.7.py` (crosswind table function, `P_AIR`, `R_AIR`, `T_VECTO_EQ`, `CDXA_REF`, `M_RED_WHEELS`, `crr_total_vecto`, `CRR_EFF`, `BETA`, TPMLM).
- VECTO source for any value you need: repo `mohgsaad-art/VECTO` (env `VECTO_SRC`).

Do NOT edit any file outside the new folder. Do NOT touch Bob's notebook or `src/`.

## 3. Gate (must pass before anything else)

Run `run_steps.py` unchanged and confirm Chain S, variant V1 (E2 drag table), reference load:
- RegionalDelivery = **0.9749** kWh/km
- UrbanDelivery = **0.8502** kWh/km
(from `step3_kwh_per_km.csv`). Must match to ±0.0005. If it does not, STOP the sensitivity work, write down what differs and why, and only report that.

## 4. One edit to the copied driver (then re-run the gate and report both numbers)

In your copy of `_driver_dragtable.py`, `coast_distance` line 60 reads the drag at `v_avg`. Bob's code of record reads it at the current speed `v` (decided 3 Nov, matches VECTO `DefaultDriverStrategy.cs` ComputeCoastingDistance). Change it to `interp1(v, drag_v, drag_F)`. Re-run the reference case and report the new Regional and Urban kWh/km next to the gate numbers. Use this edited copy for all runs below.

## 5. The two drivers compared in every case

For each case (§6) compute energy TWICE with the SAME energy step (same true mass, true temperature, true wind, Chain S, E2 drag table, same aux):

- **A. Reference driver:** `driver_model` with `coast_mass = m_ref`, `rho = 1.188`, `cdxa = CDXA_REF` (3 m/s at 4 m). This is one single driver run per cycle, reused for all cases.
- **B. Matched driver:** `driver_model` rerun with the case's own values: `coast_mass = case total mass`, `rho = P_AIR / (R_AIR · (T_case + 273.15))`, `cdxa = CdxA0 · W1 + W2` at the case wind.

Also, per case, run three **one-input-at-a-time** drivers (B_mass, B_rho, B_cdxa): only that one coasting input set to the case value, the other two at reference. This shows which input causes the difference.

Plus one extra driver for every case:
- **C. No coasting:** `coast_mass = None` (pure kinematic driver).

**Error = (A − B) / B × 100 %.** B is treated as the "truth" for this test. Also report (C − B) / B.

Energy step for a case (identical for A, B, C):
- mass per row = case total mass (constant payload);
- `T_amb_h` = constant at the case temperature; `rho` row-wise from `P_AIR`, `R_AIR`;
- `W1`, `W2` = crosswind table at the case wind, `h_ref` 4 m, Hellmann 0.2, the same crosswind function and yaw clamp setting the harness uses (state which);
- rolling: use the harness functions exactly as they are now (`crr_total_vecto` for the driver, `CRR_EFF`/`BETA` for energy). Do NOT unify them; this is a known open item. Just state in the report which form each side uses.
- aux: the constant per-mission value in `run_steps.py`.

## 6. Cases

Cycles: RegionalDelivery and UrbanDelivery (reference-load VDRI as in `run_steps.py`).

Reference values: m_ref = `VV.M_VEHICLE` + reference payload (3019.5882 kg); T_ref = `T_VECTO_EQ` (the temperature that gives ρ = 1.188 with ISO p and R); wind_ref = 3 m/s at 4 m.

**6a. One factor at a time** (others at reference):

| Factor | Levels |
|---|---|
| Total mass | 0.5 × m_ref, empty (`VV.M_VEHICLE`), m_ref, TPMLM (from the `.vveh` / harness `VEH["tpmlm"]`), 1.5 × m_ref |
| Temperature | −10 °C, T_ref, +30 °C |
| Wind at 4 m | 0, 3, 8 m/s |

Note in the report: 0.5 × m_ref is below the empty mass and 1.5 × m_ref may be above TPMLM. Run them anyway as Bob asked (pure sensitivity), but mark them **"physically impossible for E2"** where that is true. Empty and TPMLM are the realistic bounds.

**6b. Corners (worst-case combinations):** every combination of mass ∈ {0.5 × m_ref, empty, TPMLM, 1.5 × m_ref} × temperature ∈ {−10, +30} × wind ∈ {0, 8}. That is 16 corners per cycle. Report the largest |error| and which corner gives it.

## 7. Timing

Time one `driver_model` call per cycle (reference driver, coasting on): mean of 5 runs, wall-clock seconds, and say the machine (CPU). Also time one energy step (force + consumption chain) per cycle the same way. Bob needs this to judge whether rerunning the driver per day is affordable (a year ≈ 250–365 driving days per vehicle).

## 8. Also report per run (A, B, C)

- kWh/km at battery terminals;
- coast share (% of moving time in mode 3);
- braking share (mode 4) and regen energy (kWh);
- trip time (s) and max |speed difference| vs B (km/h), as a sanity check that the routes are the same length and the driver changes are small.

## 9. Outputs

In `docs/research/driver-reference-sensitivity-2026-11/`:
1. `run_sensitivity.py`: one script, runs everything, `VECTO_SRC=... python run_sensitivity.py`.
2. `results_one_factor.csv`, `results_corners.csv`, `timing.csv`.
3. `REPORT.md`, short and plain English, in this order:
   - Gate result and the §4 re-run numbers.
   - **One headline table per cycle:** case | A kWh/km | B kWh/km | error A vs B % | which input matters most (largest of B_mass, B_rho, B_cdxa) | C vs B %.
   - Worst corner per cycle.
   - Timing.
   - "Choices I made" and "Not done / could not do" lists.
   - Every number you did not compute yourself must cite its file and line. No invented values. No fallbacks without saying so.

Open a PR to `main` with the report as the description summary. Refer to the person only as "Bob".
