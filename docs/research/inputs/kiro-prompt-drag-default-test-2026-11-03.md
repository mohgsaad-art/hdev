# Kiro prompt: test the VECTO E2 drag table as HDEV's default (3 Nov 2026, v2)

Repo: `mohgsaad-art/hdev`. Work on branch **`drag-default-test-2026-11`** (already exists; the input files below are committed on it). VECTO source: `mohgsaad-art/VECTO` at commit `b8d6126`.
Write for Bob in plain English, short sentences. Bob is the only person named.

## 0. Read first

On this branch, `docs/research/inputs/`:
- `session-closeout-2026-11-03-driver-model-review.md` (sections 4 and 6–7)
- `session-closeout-2026-10-22-validation-drivetrain-winter.md` (sections 2–4)
- `hdev_maps_test_v1.py` (E2 component maps → kWh/km) and `hdev_maps_test_v2.py` (EU standard-value maps → kWh/km)

Already in the repo: `docs/research/vecto/hdev_test_harness_v1.7.py`, `docs/research/vecto/hdev_addon_std_drag_v1.py`, the six `.vmod` files and `BEV_E2.vsum`.

**Important:** the correct driver-model drag test from PR #21 is commit **`18940ab`** on branch `driver-model-review-2026-11` ("F4 redo"). It was **not merged** into `main`. `main`'s `docs/research/driver-model-review-2026-11.md` still carries the withdrawn "VECTO drag 2.0–3.4 kN" figure. Read `18940ab`'s `measure_part_d_drag.py`, `variants.py` and review doc before starting.

## 1. Background

- Bob's users will not know drivetrain data (ratios, `Tmax_in`, motor drag curve). There is no sourced way to build a drag table for "any truck".
- Proposal under test: **one drag table for all trucks**, from VECTO's generic E2 component files, labelled "VECTO example" in reports. A user with their own drivetrain data replaces it.
- Question: **how much does this choice change results**, compared with no drag and with real published kWh/km for similar trucks?
- PR #22 has errors. Do **not** reuse its `drag_force_fixed()` or its D2/D3/D7 numbers:
  1. `_stdval.py` `drag_force_fixed()` lines 305–311 apply the axle `Td0` on the axle **input** shaft at input speed. The regulation (Annex VII App. 3, Table 1: "Drag torque (wheel side)") and VECTO's generic axle put it on the **wheel side** at `n_out`. Effect: axle drag inflated ×2.59, its speed-dependent half ×2.59². Corrected totals (SR axle): 0.67 / 0.75 / 0.84 kN at 45 / 65 / 85 km/h.
  2. The truck standard value is `Td0 = 70 + 20·i`, η 0.98 for a single-reduction axle (Reg. 2017/2400 consolidated 01.01.2026, Annex VII App. 3 Table 1, p. 306). `52.5 + 15·i` is VECTO's completed-bus generic data, not the truck standard value.
  3. The benchmark "VECTO 2.0–3.4 kN" includes air and rolling. It was withdrawn. VECTO drivetrain-only drag is 1.43 kN (≈45 km/h) → 2.05 kN (≈85 km/h).
- Add a short "Corrections" note to the PR #22 report with points 1–3. Do not rerun PR #22.

## 2. Rules

- No invented numbers. Tag every value: `[VECTO file:line]`, `[REG annex/point]`, `[OEM doc + link]`, `[STUDY + link]`, `[TEST script]`, `[ASSUMPTION]`.
- Facts and inferences in separate, labelled lines.
- Do not change `src/engine/*`. Test-only copies.
- A source you cannot open goes on a "Bob to fetch" list with the link. No gaps filled from memory.

## 3. Step 1 — E2 drag table from the component files

- `18940ab` built it at zero torque and got 0.63–0.93 kN (~2× low). The 3 Nov close-out (section 4.2) shows the files do reproduce VECTO (1.42 → 2.07 kN) when: **2 motors** (`.vveh` `"Count": 2`), motor drag from `GenericDrag_125kW_485Nm.vemd`, and gearbox / axle loss read from `Gear_2.vtlm` / `Axle_4x2_Tractor.vtlm` **at the torque the drag itself puts through them**, each on its own shaft. Rebuild it that way.
- ADC loss: find what VECTO does when coasting (file:line). If not found, leave it out and tag `[ASSUMPTION]`.
- Table 0–130 km/h, 1 km/h steps, gear 2 (VECTO uses gear 2 > 99 % of driving per the 22 Oct close-out; confirm gear on Coast/Roll rows of the `.vmod`).
- **Check** against `.vmod` Coast/Roll rows, `−P_wheel_in / v`, median per 10 km/h band, Regional and Urban reference load. Report the difference per band. Stop and report if any band is off by more than 10 %.

## 4. Step 2 — Driver model: reuse, don't redo

- `18940ab` already ran the driver model with the `.vmod` drag table (Regional ref: coast 7.80 → 1.60 % vs VECTO 1.46 %; seconds > 85 km/h 180 → 0; RMS 1.28 → 0.35 km/h).
- If your Step 1 table is within 5 % of the `.vmod` table in every band, **reuse those driver results**. Only re-run (with the agreed edits: `drag_v=(0.0,), drag_F=(0.0,)` defaults, `coast_acc` and `coast_distance` read `interp1(v, drag_v, drag_F)`, `g = 9.80665`) if it is not.
- Add one variant: **V2 = corrected EU standard-value drag** (wheel-side axle, `70 + 20·i`), on Regional and Urban reference load. Report coast %, seconds > 85 km/h, speed RMS and wheel energy vs VECTO.
- Variants: V0 no drag, V1 E2 table, V2 standard-value corrected.

## 5. Step 3 — kWh/km through the consumption chain

- Run the V0, V1 and V2 driver outputs through the same consumption chain, held fixed, so only the drag changes:
  - **Chain S:** EU standard-value maps as in `hdev_maps_test_v2.py` (gearbox Annex VI App. 8, `Tmax_in` 1940 Nm `[ASSUMPTION]`; axle `70 + 20·i` wheel side; motor Annex Xb App. 8).
  - **Chain E:** E2 component maps as in `hdev_maps_test_v1.py`.
- Auxiliaries: VECTO BEV aux as in harness v1.7 (state the W values). Do **not** set `P_aux = 0`.
- First reproduce the 22 Oct baseline (Chain S, no drag: Regional 0.947, Urban 0.815 kWh/km). If off by more than 1 %, find out why before going on.
- Report kWh/km at the battery terminals per variant, cycle (Regional, Urban, Municipal with PTO) and load (reference, low); % V1 vs V0; % vs VECTO `.vsum` (Regional 1.050, Urban 0.840).

## 6. Step 4 — Compare with real trucks

- Give the E2 class, GVW, curb mass and payloads from the VECTO files.
- Start from the sourced values in the 22 Oct close-out, section 2. Add new ones only with a link (OEM data, VECTO CIF figures, independent tests such as Öko-Institut, ICCT, TNO, fleet trials).
- Use only sources that state the cycle or use type and the mass or payload (temperature/season if given). One row per source with these, plus how it differs from the E2 truck.
- Show HDEV V0 and V1 next to them. Do **not** call it validation where truck, mass or cycle differ.

## 7. Step 5 — Answer for Bob (top of report, max 10 lines)

1. Does the E2 table reproduce VECTO's drag?
2. How much does V1 change coast %, overspeed and kWh/km vs V0 (and V2)?
3. Does V0 or V2 underestimate energy vs V1? Bob's rule: HDEV must not underestimate.
4. Where do HDEV V0/V1 sit against real trucks, and how comparable are they?
5. Is the drag choice big or small next to `Tmax_in` (0.947 → 1.150 kWh/km on 22 Oct)?

## 8. Deliverables

- `docs/research/drag-default-test-2026-11.md` and `docs/research/drag-default-test-2026-11/` (scripts + CSVs).
- Corrections note in the PR #22 report.
- "Bob to fetch" list.
- PR from `drag-default-test-2026-11` against `main`, no changes to `src/engine/`.
