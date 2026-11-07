# Testing the VECTO E2 drag table as HDEV's default drag

**Owner:** Bob. **Repo:** `mohgsaad-art/hdev`. **Branch:** `drag-default-test-2026-11`.
**Date:** 3 November 2026. **Author:** Kiro (AI).
**VECTO source read:** `mohgsaad-art/VECTO` at commit **`b8d6126`** (branch `IEPC-experiments`).
**Authoritative prior test:** commit **`18940ab`** on `driver-model-review-2026-11`
(the "F4 redo" driver-model drag test, not merged into `main`).

**Tag key:** `[VECTO file:line]` read in VECTO source at `b8d6126`;
`[REG annex/point]` regulation; `[VMOD]`/`[VSUM]` read from Bob's VECTO 5.1.6-RC run;
`[OEM + link]`; `[STUDY + link]`; `[TEST script]` a test in
`docs/research/drag-default-test-2026-11/`; `[ASSUMPTION]`. An untagged number is a
defect. **Facts** and **inferences** are on separate, labelled lines.

---

## Answer for Bob (read this first)

1. **Yes, the E2 component files reproduce VECTO's drag.** Built the right way (2 motors,
   motor drag from the `.vemd`, gearbox/axle loss read at the torque the drag puts
   through, axle on the wheel side), the E2 table is **1.31 → 1.92 kN** (45 → 85 km/h)
   and matches the `.vmod` to **within 9 % in every 10 km/h band** `[TEST step1]`. (The
   `.vmod` itself is 1.43 → 2.05 kN.)
2. **The drag choice is small but real.** V1 (E2 drag) vs V0 (no drag) changes kWh/km by
   **+2.2 % to +6.0 %** (Regional +3.1 %, Urban +5.1 %, Municipal +6.0 %, Chain S)
   `[TEST step3]`. In the driver it cuts Regional coast from **7.8 % → 1.9 %** (VECTO
   1.46 %), overspeed seconds from **180 → 0** (VECTO 0), speed RMS **1.28 → 0.46 km/h**
   `[TEST step2]`.
3. **Both V0 and V2 underestimate energy vs V1.** V0 (no drag) is 2–6 % low; V2 (EU
   standard-value drag, correctly on the wheel side, 0.67–0.84 kN) is ~1–2 % low because
   its drag is about half the E2 drag `[TEST step2/step3]`. By Bob's "must not
   underestimate" rule, **V1 (the E2 table) is the safe default**; V0 and V2 both
   under-read.
4. **HDEV sits in the real-truck cloud, but it is not a like-for-like match.** HDEV V1
   Regional ref = **0.975 kWh/km** (Chain S) / 1.047 (Chain E); real figures for similar
   (but not identical) trucks run 0.66–1.14 kWh/km `[OEM/STUDY, 22 Oct §2]`. Only MAN eTGL
   (0.69) shares the E2's 11.99 t GVW, and even that is a spec-sheet "up to" number with
   an unknown route — **not validation**.
5. **The drag choice is small next to `Tmax_in`.** Drag V0→V1 is +3.1 % on Regional.
   `Tmax_in` 1940 → 5500 Nm moved Regional **0.947 → 1.150 (+21 %)** `[22 Oct §3]` — about
   **7× bigger**. So: ship the E2 drag table as the default, but `Tmax_in` is the input to
   get right.

---

## 1. What was tested and why

**Fact.** Bob's users will not know drivetrain data (gear ratios, `Tmax_in`, the motor
drag curve), so there is no way to build a per-truck drag table from user inputs
`[22 Oct §9, 3 Nov close-out §7]`. The proposal under test: use **one drag table for all
trucks**, built from VECTO's generic **E2** component files, labelled "VECTO example" in
reports; a user with their own drivetrain data replaces it. The questions (Step 5) are how
much this choice changes results versus no drag (V0) and versus a corrected EU
standard-value drag (V2), and how HDEV lands against real trucks.

**Three drag variants, one fixed everything-else:**
- **V0** — no drivetrain drag (today's `P_drag_loss = 0`).
- **V1** — the E2 drag table (this report, Step 1).
- **V2** — corrected EU standard-value drag (wheel-side axle `70 + 20·i`, gearbox
  `0.005·Tmax_in`, motor Annex Xb drag).

**E2 vehicle** `[VECTO BatteryElectricVehicle.vveh]`: legislative class **N3**, VECTO
group 2 (4×2 rigid medium lorry), chassis curb 4670 kg + body 1900 kg = **6570 kg**,
**GVW 11.99 t**; reference payload **3019.6 kg** (total 9589.6 kg), low payload **603.9 kg**
(total 7173.9 kg) `[VECTO; 22 Oct §2; close-out loadings]`. Two motors, 2 × 125 kW /
2 × 485 Nm, ADC 2.0, gear 2 = 1.93, axle 2.59, tyre 265/70 R19.5 (r_dyn 0.4209 m)
`[VECTO AMT.vgbx, .vveh, Wheels.cs]`.

---

## 2. Step 1 — the E2 drag table from the component files

**Fact.** Commit `18940ab` built the E2 table **at zero torque** and got 0.63–0.93 kN —
about half VECTO's drag — and concluded (wrongly) that the files could not reproduce
VECTO `[TEST 18940ab measure_part_d_drag.py]`. The 3 Nov close-out (§4.2) shows the files
**do** reproduce VECTO when the gearbox and axle loss are read **at the torque the drag
itself puts through them** (not at zero torque), with **2 motors** and the motor drag from
`GenericDrag_125kW_485Nm.vemd` `[close-out §4.2]`.

**Method used here** (`_e2_drag.py`, built outward from the motor, gear 2):
`drag force at wheel = (motor-drag power + gearbox-loss power + axle-loss power) / v`,
the same identity VECTO's coasting resistance uses,
`−P_wheel_in/v = (P_gbx_in + P_gbx_loss + P_axle_loss)/v`
`[VECTO DefaultDriverStrategy.cs:764-769; close-out §4.1]`. Gearbox/axle loss from
`Gear_2.vtlm` / `Axle_4x2_Tractor.vtlm`, read at the drag operating point; **axle loss on
the wheel side** at `n_out` (the PR #22 error put it on the input shaft — see Corrections).
**ADC (motor→gearbox) loss ignored** `[ASSUMPTION]`: I searched VECTO for a coasting ADC
loss and `CalculateElectricMotorDragLoss` sums only the EM drag power
`[VECTO DefaultDriverStrategy.cs:778-787]`; the ADC loss map is applied in the powertrain
request path, not in the driver's coasting-resistance estimate, and the `.vmod` identity
closes without it — so leaving it out is consistent with the `.vmod`.

**Result — band check vs the `.vmod`** (Regional + Urban reference) `[TEST step1_band_check.csv]`:

| band | E2 files | `.vmod` −P_wheel_in/v | `.vmod` component sum | diff |
|---|---|---|---|---|
| 40–50 | 1306 N | 1431 N | 1431 N | −8.8 % |
| 50–60 | 1454 N | 1534 N | 1539 N | −5.2 % |
| 60–70 | 1608 N | 1635 N | 1673 N | −1.6 % |
| 70–80 | 1763 N | 1796 N | 1796 N | −1.8 % |
| 80–90 | 1923 N | 2097 N | 2097 N | −8.3 % |

**Worst band 8.8 %, every band < 10 %** — the check passes. The `.vmod` `−P_wheel_in/v`
and the component sum agree to the digit (same identity). **Gear on the `.vmod` Coast/Roll
rows is gear 2** (Regional 86/86, Urban 283/292) `[TEST step1]`, confirming the gear-2
assumption. **[INFERENCE]** The residual at the band edges (my build ~8 % below the `.vmod`
at 40–50 and 80–90) is in how the gearbox/axle loss is read at the drag torque; the
close-out's own build (1.42 → 2.07 kN) is a touch higher than mine and closer to the
`.vmod`. The full 0–130 km/h table is in `step1_drag_table.csv`.

Because the worst band (8.8 %) is **more than the 5 % reuse threshold**, I did **not**
reuse the `18940ab` driver numbers directly — I re-ran the driver model with my Step-1
table and the agreed edits (Step 2). The conclusions match `18940ab` closely.

---

## 3. Step 2 — driver model with drag (V0/V1/V2) vs VECTO

**Fact.** Driver = a test-only copy of the code of record with the agreed edits
(`drag_v`/`drag_F` table in `coast_acc` and `coast_distance`, `g = 9.80665`);
`_driver_dragtable.py`. `[TEST step2_driver_metrics.csv]`:

| Cycle / load | variant | coast % | secs > 85 | speed RMS vs VECTO | VECTO coast % / secs>85 |
|---|---|---|---|---|---|
| Regional ref | V0 | 7.80 | 180 | 1.28 | 1.46 / 0 |
| Regional ref | **V1** | **1.90** | **0** | **0.46** | |
| Regional ref | V2 | 4.77 | 52 | 0.71 | |
| Regional low | V0 | 5.54 | 79 | 1.10 | 1.21 / 0 |
| Regional low | **V1** | **1.21** | **0** | **0.38** | |
| Urban ref | V0 | 5.17 | 4 | 2.00 | 2.16 / 11 |
| Urban ref | **V1** | **2.46** | **11** | **0.97** | |
| Urban ref | V2 | 3.63 | 13 | 1.46 | |
| Urban low | V0 | 4.63 | 13 | 1.75 | 1.31 / 0 |
| Urban low | **V1** | **1.61** | **3** | **0.82** | |

**Reading.** V1 pulls coast share and overspeed onto VECTO (Regional 7.8 → 1.9 % vs 1.46 %;
180 → 0 secs; RMS 1.28 → 0.46 km/h). This matches `18940ab`'s result with the `.vmod` table
(coast 7.80 → 1.60 %, 180 → 0, RMS 1.28 → 0.35) — my table is slightly weaker at the band
edges so V1 lands at 1.9 % rather than 1.6 %, but the picture is the same. **V2 (standard
values) under-corrects** — its drag is about half V1's, so HDEV still coasts (4.77 %) and
overspeeds (52 s) more than VECTO.

---

## 4. Step 3 — kWh/km through the consumption chain

**Fact.** V0/V1/V2 driver traces run through two fixed chains so only the drag changes:
- **Chain S** — EU standard-value maps (gearbox Annex VI App. 8, `Tmax_in` 1940 Nm
  `[ASSUMPTION]`; axle `70 + 20·i` wheel side; motor Annex Xb App. 8), as in
  `hdev_maps_test_v2.py`.
- **Chain E** — E2 component maps, as in `hdev_maps_test_v1.py`.

**Auxiliaries** are the E2 reference truck's own, read from the `.vmod` `P_aux_el` column
`[VMOD]`: **Regional 1983 W, Urban 1769 W** (ES 1000 + HVAC 250 + PS 200 + steering 20 +
Cond ~513). Municipal uses the Urban aux `[ASSUMPTION — no group-2 Municipal `.vmod`]`
plus a 2 kW always-on refuse PTO `[ASSUMPTION/ILLUS, 22 Oct §5]`. `P_aux` is **not** 0.

**Baseline check (Chain S, no drag):** Regional **0.946** (22 Oct target 0.947), Urban
**0.809** (target 0.815) — within 0.1 % / 0.7 %, so the setup reproduces the 22 Oct baseline
`[TEST step3]`.

**kWh/km at the battery terminals** `[TEST step3_kwh_per_km.csv]`:

| Cycle / load | chain | V0 | V1 | V1 vs V0 | V2 | VECTO `.vsum` |
|---|---|---|---|---|---|---|
| Regional ref | S | 0.946 | **0.975** | +3.1 % | 0.969 | 1.050 |
| Regional ref | E | 1.011 | **1.047** | +3.6 % | 1.038 | 1.050 |
| Regional low | S | 0.893 | 0.912 | +2.2 % | 0.909 | — |
| Urban ref | S | 0.809 | **0.850** | +5.1 % | 0.836 | 0.840 |
| Urban ref | E | 0.782 | **0.827** | +5.7 % | 0.812 | 0.840 |
| Urban low | S | 0.707 | 0.740 | +4.8 % | 0.732 | — |
| Municipal ref (PTO) | S | 0.977 | 1.036 | +6.0 % | 1.017 | — (no VECTO mission) |
| Municipal ref (PTO) | E | 0.949 | 1.011 | +6.6 % | 0.989 | — |

**Reading.**
- The drag choice is worth **+2.2 % to +6.6 %** on kWh/km, always in the **safe (higher)**
  direction. It matters more on stop-start cycles (Urban, Municipal) than on Regional.
- **V0 and V2 both underestimate vs V1.** V2 (correct standard-value drag) is ~0.6 % (Regional)
  to ~1.7 % (Urban) below V1.
- Chain E (E2 maps) with V1 lands essentially on VECTO (Regional 1.047 vs 1.050; Urban 0.827
  vs 0.840). Chain S (standard maps) is a bit lower on Regional (0.975) because the EU standard
  motor map is more efficient than VECTO's example motor `[22 Oct §6]`.

---

## 5. Step 4 — compare with real trucks

**E2:** N3, 11.99 t GVW, 9.59 t at reference load, VECTO declaration Regional/Urban cycles.
Real-truck rows are the sourced figures from the 22 Oct close-out §2 (each with its link in
`step4_real_trucks.csv`). **This is not validation where truck, mass or cycle differ.**

| Source | kWh/km | Mass | Basis | Like-for-like? |
|---|---|---|---|---|
| **HDEV V0, Chain S, Regional ref** | **0.946** | 9.59 t | HDEV, no drag | — |
| **HDEV V1, Chain S, Regional ref** | **0.975** | 9.59 t | HDEV, E2 drag (default) | — |
| **HDEV V1, Chain S, Urban ref** | **0.850** | 9.59 t | HDEV, E2 drag | — |
| MAN eTGL (OEM) | 0.69 | 11.99 t GVW | spec "up to", route unknown | same GVW only |
| Renault E-Tech D12 [CALC] | 0.80 | 12 t | 176 kWh / 220 km | near GVW, cycle unknown |
| Renault E-Tech D16 [CALC] | 1.14 | 16.7 t | 375 kWh / 330 km | heavier |
| DAF XB Electric [CALC] | 0.81 | 12–19 t | 282 kWh / 350 km | heavier variants |
| Fuso eCanter [CALC] | 0.66 | 7.49 t | 66 kWh / ~100 km | lighter |
| Volvo FL heat test | 0.73 | 15 t | measured, > 35 °C | heavier, hot |
| Öko-Institut eActros (measured) | 0.67–0.72 | 19 t | measured medians | much heavier |
| MAN fleet average (measured) | 0.90 | mixed | on-road | mixed |
| NREL Smith Newton (measured) | 0.79–0.87 | ~10 t | measured fleet | older tech |
| Danish fit at 11.99 t | 0.796 | 11.99 t | cross-truck regression | regression, not one truck |
| Liimatainen fit at 11.99 t | 0.855 | 11.99 t | cross-truck regression | regression |

**Reading.** HDEV V0/V1 (0.85–0.98) sit inside the spread of real figures and close to the
two regressions at 11.99 t (0.80 / 0.86). The only same-GVW OEM point (MAN eTGL 0.69) is a
best-case spec number. **[INFERENCE]** HDEV is in the right range, but no row is a true
like-for-like test, so this is a plausibility check, not validation. The drag choice
(V0→V1, +3 % Regional) is smaller than the scatter between these sources.

---

## 6. Step 5 answers (the five questions)

1. **Does the E2 table reproduce VECTO's drag?** Yes — 1.31 → 1.92 kN, within 9 % of the
   `.vmod` in every band `[TEST step1]`.
2. **How much does V1 change coast %, overspeed and kWh/km vs V0 (and V2)?** Coast 7.8 → 1.9 %
   (Regional), overspeed 180 → 0 s, kWh/km **+3.1 % Regional / +5.1 % Urban / +6.0 % Municipal**
   (Chain S). V2 sits between V0 and V1 `[TEST step2/step3]`.
3. **Does V0 or V2 underestimate vs V1?** **Both do.** V0 by 2–6 %, V2 by ~1–2 %. V1 is the
   safe default under Bob's no-underestimate rule.
4. **Where do HDEV V0/V1 sit against real trucks?** Inside the 0.66–1.14 kWh/km real-truck
   cloud and near the 11.99 t regressions; but truck/mass/cycle differ, so **not validation**.
5. **Is the drag choice big or small next to `Tmax_in`?** **Small.** Drag V0→V1 = +3.1 %
   (Regional); `Tmax_in` 1940 → 5500 Nm = **+21 %** (0.947 → 1.150) `[22 Oct §3]`. `Tmax_in`
   is ~7× the lever. **Recommendation:** adopt the E2 drag table as the default (labelled
   "VECTO example"), and focus on getting `Tmax_in` right.

---

## Corrections to the PR #22 report (`drivetrain-inputs-fallbacks-2026-11.md`)

A short note was added to that report. The three errors (do **not** reuse PR #22's
`drag_force_fixed()` or its D2/D3/D7 numbers):

1. **Axle drag put on the wrong shaft.** PR #22's `_stdval.py` `drag_force_fixed()` applied
   the axle `Td0` on the axle **input** shaft at input speed. The regulation (Annex VII
   App. 3 Table 1, "drag torque (wheel side)") and VECTO's generic axle put it on the
   **wheel side** at `n_out`. The error inflates the axle drag by ×2.59 (and its
   speed-dependent half by ×2.59²). Corrected single-reduction-axle totals: **0.67 / 0.75 /
   0.84 kN at 45 / 65 / 85 km/h** `[REG Annex VII App. 3]`.
2. **Wrong axle standard value.** The truck single-reduction standard value is
   `Td0 = 70 + 20·i`, η 0.98 `[REG 2017/2400 consolidated 01.01.2026, Annex VII App. 3
   Table 1, p. 306]`. PR #22 used `52.5 + 15·i`, which is VECTO's **completed-bus generic**
   data, not the truck standard value.
3. **Withdrawn benchmark.** PR #22 compared against "VECTO 2.0–3.4 kN", which **includes air
   and rolling**. That figure was withdrawn (3 Nov close-out §4.4). VECTO **drivetrain-only**
   drag is **1.43 kN (≈45 km/h) → 2.05 kN (≈85 km/h)** `[VMOD, close-out §4.1]`.

PR #22 was not re-run.

---

## Bob to fetch

| Document | Why | Link |
|---|---|---|
| Reg. (EU) 2017/2400 **Annex VII App. 3 Table 1** (axle standard torque loss, per type, wheel side) | the clean per-type axle constants (single reduction / hub / portal) and the exact wheel-side definition | https://circabc.europa.eu/sd/a/2d14d59c-7180-4026-98d0-db0f2a61f8d6/HDV%20CO2%20certification%20ISC%20Annexes%207-11%20FINAL.pdf |
| Reg. (EU) 2017/2400 **Annex VI App. 8** (gearbox standard torque loss) | exact `fT` direct/indirect split and the `Tmax_in` definition | https://circabc.europa.eu/sd/a/7e669890-a263-4908-8605-f83e32a893fb/HDV%20CO2%20certification%20Annex%206%20post%20BRP.pdf |
| A VECTO **engineering-mode** Municipal + PTO run for group 2 | so the Municipal kWh/km has a VECTO reference (there is no group-2 Municipal declaration mission) | Bob's VECTO install |
| Like-for-like **11.99 t** measured kWh/km with stated cycle + mass | to turn the Step 4 plausibility check into real validation | fleet telematics / OEM VECTO file |

## How to run

```bash
python -m venv .venv && . .venv/bin/activate && pip install numpy scipy
cd docs/research/drag-default-test-2026-11
VECTO_SRC=/path/to/VECTO python step1_drag_check.py   # -> step1_drag_table.csv, step1_band_check.csv
VECTO_SRC=/path/to/VECTO python run_steps.py          # -> step2_driver_metrics.csv, step3_kwh_per_km.csv
python step4_real_trucks.py                           # -> step4_real_trucks.csv
```
`VECTO_SRC` is a VECTO checkout at `b8d6126` (the E2 component files are read from it).
The `.vmod`/`.vsum` are already in `docs/research/vecto/`. No `src/engine/` file is
imported or changed; the driver is the code-of-record copy in
`tests/driver_model/reference_copy.py` plus the test-only `_driver_dragtable.py`.
