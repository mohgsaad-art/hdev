# Session closeout, 7 Nov 2026 (morning): Kiro PR #27 review, HDEV vs EEA certified trucks, drivetrain fallbacks, calibration to EEA

Paste this at the start of the next chat. Project: HDEV sizing & Modelling Tool ("EV Scope"). Bob builds and codes; Claude helps. Standing rules: state assumptions, no invented numbers, sources for every value, one step at a time unless asked. Kiro output must be spot-checked.

Repo: `mohgsaad-art/hdev`. VECTO: `mohgsaad-art/VECTO` (EUPL 1.2). Claude had **read-only** repo access this session. Nothing was pushed to the repo.

---

## 1. What happened (in order)

1. Reviewed Kiro's PR #27 (EEA truck validation, v1). Found the Job 3 results unusable (section 2).
2. Wrote a detailed v2 Kiro prompt (`claude/kiro-prompt-eea-truck-validation-v2-2026-11-07.md`).
3. Reviewed Kiro's v2 progress mid-run and sent corrections (section 3).
4. Ran our own comparison on real certified trucks with Bob's notebook code (section 4).
5. Compared drivetrain fallbacks (section 5).
6. Tested calibrating HDEV to EEA certified values on 10 trucks (section 6).

PR #27 was **merged into `main`** before the review. Its Job 3 numbers (e.g. "V-C best, −14 % median") are on `main` and must not be used.

---

## 2. Kiro PR #27 (v1) review — confirmed from the code at commit `49ac911`

Usable: Job 1 counts (4,603 vehicles, 835 configs, 2,658 configs incl. curb mass); 355 Canter/S-eWay rows have `DifferentialIncluded = true`.

Not usable — Job 3 harness bugs (file + line at `49ac911`):
- `_drivetrains.py`: `std_gearbox` (l.88) and `vecto_axle` (l.98) defined but never called. V-B and V-C = motor map × constant 0.96 only.
- `_drivetrains.py` l.182: E2/E3 total ratio = axle ratio only; gearbox ignored (EEA has no gear ratios).
- `_drivetrains.py` l.64–84: points outside the motor map filled with the nearest map value → demand above the map is capped → energy reads low.
- `_drivetrains.py` l.187–195: `n_rated = 3000 rpm` invented.
- `run_hdev.py` l.74–78: aux 2600/2300/2100 W, no arithmetic.
- `run_hdev.py` l.335–344: drag formula invented (`52.5 + 15·(ratio/3) + 2·v`).
- `run_hdev.py` l.48–53 and 63–68: CdxA table hand-typed; tractors (groups 5, 10, 12) given `RigidTrailer` crosswind; `TractorSemitrailer` defined but unused; trailer ΔCdA never added.
- `run_hdev.py` l.156–182: plain mean RRC, fallback Crr 0.0055, r_dyn from the **last** axle, default 0.489 m.
- `run_hdev.py` l.229: driver cache key rounds mass to 250 kg, ignores drag table and CdxA.
- `run_hdev.py` l.237, 294: rotating inertia set to 0.
- V-A re-implemented instead of calling Bob's `consumption_engine`.
- Grid basis: constant ÷0.995; battery internal losses missing.
- Municipal Utility −64 to −73 % (PTO missing; same error as the 3 Nov PR).
- CdxA bins ±10 % around VECTO default: unsourced.
- Job 4: only 10 OEM entries (prompt asked 15–25); some values from trade press/snippets.

Extra checks by Claude: `docs/research/HDV-tabledefinition (1).xlsx` has only `AirDrag_CdxA_range | nvarchar(20)` (no bin edges). `metadata-22fd286c-…pdf` confirms licence CC-BY 4.0, no bins.

## 3. Kiro v2 (in progress) — what it found and what was corrected

Kiro v2 is working on the same branch. PR #27 is merged, so Kiro will open a **new PR** titled "EEA truck validation v2 (supersedes #27 Job 3)". Bob told Kiro to do the whole prompt in one pass, not stop at the gate, label results "GATE FAILED" if the gate can't be fixed, and mark missing items `[BOB]` without stopping.

Kiro v2 findings checked by Claude:
- Correct: usable window 0.855 (MaxSOC 92.75 %, MinSOC 7.25 %, `BatteryDataAdapter.cs` 62–67, `GenericSOC.csv` PEV 5/95/5). v1's 0.85375 was an arithmetic error.
- Correct: Reg. 2018/956 Annex I reports the actual CdxA (field 23, point 1.8.4). The A1–A24 bin edges are not in the regulation → `[BOB]`.
- Correct: groups 5/10/12 use `TractorSemitrailer` (SegmentTable). Trailer ΔCdA: T1 1.3, T2 1.5/1.5, ST1 0/2.1. Trailer RRC 0.0055, FzISO 37,500 N (`DeclarationData.cs` 837, 839). Truck axle standard loss corrected to 70 + 20·i (Annex VII App. 3).
- Correct: aux constants — alternator 0.7 (`DeclarationData.cs` 123), HVAC factor 0.8 → ×1.25 (l.126), PS electric demand 5600 W / 325 NL/min (l.355). EEA `Aux_HVAC_SystemConfiguration` is blank for all 4,603 trucks.
- Correct: PTO flag — 4,100 blank, 503 false, 0 true.

Corrections sent to Kiro:
1. **2.1 explanation is algebraically wrong.** `deltaEPSel` sits in D13, which is in both kWh/km (D21 = D13/η) and range (D16 = D15/D13 × distance), so it cancels. The ratio = (D15 / published usable) / η. A ratio below 1 means D15 < published usable (string-min aggregation, `BatteryData.cs` 42–49). Only 4 vehicles have the ≈0.5 parallel-string signature; 8.1 % of rows still sit at 0.99–1.0 and need another cause or "not found".
2. **Gate passed only for a gate script** that loaded the 3 Nov setup (`VV.CDXA_REF`, m_red 220 kg). It must be re-run through `run_hdev.py`'s own functions, and gate step 4 (V-A…V-D on E2) is missing.
3. **FzISO stand-in** ("ETRTO rated load") needs a cited table per tyre size, or `[BOB]` + two bounds.
4. **2.6 PTO** contradicts itself (mission-triggered vs per-vehicle declared). Quote `TruckSegments.cs` ~316 and the PTO-cycle reader.
5. Report must say V-B/V-C ran on 0 certified trucks (no full-load curve in EEA).

Status: Kiro was mid-run (full harness) at the time of this closeout. Review its new PR when it arrives.

---

## 4. Claude's own comparison: HDEV vs EEA certified vs OEM (2 trucks)

Scripts (Claude workspace, not in repo): `run_compare.py`, `nbmod.py` (Bob's notebook functions with fixes 1–2; g = 9.80665 passed explicitly), `sens.py`, `ext.py`, `plot.py`. Data: `results.csv`, `results_ext.csv`. Graphs: `hdev_vs_eea_abs.png`, `hdev_vs_eea_pct.png`.

Why these trucks: the only EEA trucks where the full wheel-to-motor ratio is published are **single-gear IEPC** trucks (Fuso Canter, IVECO S-eWay). Every other e-truck has a multi-speed gearbox, and EEA gives no gear ratios.

Trucks:
- **Fuso eCanter, EEA C0059** (group 1, 8.55 t). IEPC 1 gear, ratio 19.528, differential included, **standard-value IEPC**, **standard-value air drag** → CdxA = SegmentTable default 7.1 m² exactly. OEM ([fuso-trucks.com ?p=19280](https://www.fuso-trucks.com/?p=19280), [brochure](https://www.fuso-trucks.com/wp-content/uploads/sites/2/2022/08/221013_THE-NEW-eCANTER_Broschure_EN_RZ.pdf)): 430 Nm / 129 kW peak, 250 Nm / 110 kW continuous, PSM, max 15,000 rpm; L pack 123.9 kWh, 94 % usable, up to 200 km (50 % payload, box body, 20 °C).
- **IVECO S-eWay tractor, EEA C0091** (group 5). IEPC 1 gear, ratio 25.101, differential included, **measured IEPC**, **measured CdxA (bin A14, value unknown)** → 8.7 m² standard value used. OEM ([iveco.com press release 15 Nov 2023](https://www.iveco.com/global/Press/PressReleases/2023/IVECO-supports-customers-on-the-road-of-electro-mobility-with-its-IVECO-S-eWay-and-eDaily-ranges)): 9 × 82 = 738 kWh, 480 kW continuous, 1,800 Nm, "up to 500 km", no conditions. The newer [S-eWay brochure](https://edge.sitecorecloud.io/gatespa1-sitecoregate-preprod-0d09/media/Project/Gate/Gate/Rebranding-Shared-Images/File-PDF-Brochure/IVECO-S-eWay_EN.pdf) (603 kWh LFP) is a different generation → no match.

Set-up (all sourced):
- Cycles: VECTO `MissionCycles/*.vdri`; vacc `Truck.vacc`. HDEV driver average speeds match EEA within 1 % (e.g. Urban 26.4 vs 26.7 km/h).
- Crosswind: `crosswind_engine(H, [3.0], 4.0, a1, a2, a3, 0.2, 0.1·H, 10, 60…130 km/h, None)` = VECTO declaration grid (`AirdragDataAdapter.cs` 20–90; `Physics.cs` 56–66).
- Air density 1.188 (`DeclarationData.cs` 74): `consumption_engine` gets p_air = 1.188 × 287.058 × 293.15 Pa at 20 °C.
- RRC and wheel inertia per `VehicleData.cs` 275–314; trailer axles from SegmentTable and `VehicleDataAdapter.cs` 168.
- Aux per technology label via Bob's `P_aux` and `SP_power_helper` with VAUX tables (ES-Tech, PS-Table `_el`, SP-Table/Axles/Tech, HVAC-Table Default, Cond-Table).
- Driver `P_max` = EEA R85 rated power.

Variants:
- **V-A** Bob's `consumption_engine`, 0.95/0.95/0.98, regen 0.95 (3 Nov values).
- **V-B** EU standard values, Annex Xb App. 9 Option 1: App. 8 motor map (PSM/ASM k-tables), App. 9(2) gearbox (Td0 = Td1000 = 0.0025·Tmax_in; fT = 1 − 0.995·0.986), App. 9(3) differential (spur, Td0 = 25 + 5·i_diff).
- **V-C** VECTO bus-generic IEPC (`GenericBusIEPCData.cs`, IEPC normalised maps; gear and axle eff 0.96·0.96; map columns are output-shaft per `IEPCMapReader.cs` 292).
- **V-D** VECTO E2 example maps as-is (2 × 125 kW ASM, ADC 2.0, gear 2 1.93, axle 2.59).
- **V-E** VECTO GenericIEPC `IEPC_Gbx1Speed+Axle` example map as-is (250 kW PSM, 12.276).

Rated point: n_rated = R85 rated power ÷ OEM max torque [D]. This matches VECTO's corner-point rule (`ElectricMotorRatedSpeedHelper.cs` 35–49) for a constant-torque / constant-power curve.

### kWh/km results

Fuso eCanter (OEM: 116.5 kWh usable / 200 km = **0.58**, battery side):

| Mission, payload | EEA certified | V-A | V-B | V-C | V-D |
|---|---|---|---|---|---|
| Urban, 0.3 t | 0.72 | 0.50 | 0.74 | 0.70 | 0.78 |
| Urban, 1.7 t | 0.76 | 0.54 | 0.78 | 0.75 | 0.83 |
| Regional, 0.3 t | 1.22 | 0.80 | 1.19 | 1.14 | 1.17 |
| Regional, 1.7 t | 1.24 | 0.83 | 1.21 | 1.17 | 1.20 |

IVECO S-eWay (OEM: 738 kWh installed / "up to 500 km" = **≤ 1.48**, upper bound):

| Mission, payload | EEA certified | V-A | V-B (PSM–ASM) | V-C (PSM–ASM) | V-D |
|---|---|---|---|---|---|
| Urban, 2.6 t | 0.99 | 1.02 | 1.73–1.80 | 1.46–1.58 | 1.19* |
| Urban, 12.9 t | 1.25 | 1.29 | 2.09 | 1.89–1.93 | 1.25* |
| Regional, 2.6 t | 1.12 | 1.29 | 2.24–2.48 | 1.61–2.09 | 1.56* |
| Regional, 12.9 t | 1.30 | 1.49 | 2.44–2.67 | 1.87–2.32 | 1.71* |
| Long Haul, 2.6 t | 1.19 | 1.38 | 2.41–2.69 | 1.69–2.28 | 1.66* |
| Long Haul, 19.3 t | 1.46 | 1.68 | 2.71–2.97 | 2.06–2.59 | 1.93* |

\* E2 motor too small (out of map on 19–77 % of drive energy) → not usable.

Key points:
- **Canter V-B within ±3.3 %.** The Canter was certified with the same standard-value IEPC method, so this checks HDEV's driver, forces, tyres, aux and crosswind against VECTO on a real certified truck. With the right drivetrain data, the engine is about ±3 % (E2 example 3 Nov: −0.3 % / −1.6 %).
- **V-A** is −30 to −34 % on the Canter (same as 3 Nov E2).
- **S-eWay V-B/V-C overshoot +38 to +126 %** for any rated speed from 3,000 to 10,000 rpm. Standard maps are conservative; this truck has a measured map.
- **S-eWay V-A** moves about 6–7 % per 1 m² CdxA; real CdxA unknown.
- **OEM figures are not a validation reference.** Canter OEM is 20–53 % below certified (milder, unstated route). S-eWay OEM is installed basis, no conditions.
- Sensitivity: Canter gearbox/diff ratio split moves V-B ±1 %.

---

## 5. Fallback scorecard (no drivetrain data)

Includes the 3 Nov VECTO example trucks (E2 12 t; group-5 tractor E2 layout; group-5 B2 APTN tractor), compared with their own maps (E2 with VECTO).

Typical (median) error vs reference:

| Truck | Constant eff. (V-A) | EU std (V-B) | Bus method (V-C) | E2 example (V-D) | IEPC example (V-E) |
|---|---|---|---|---|---|
| Fuso eCanter | −32 % | 0 % | −4 % | +3 % | −10 % |
| VECTO E2 12 t | −32 % | −5 % | +3 % | (reference) | – |
| VECTO tractor E2 | −3 % | +6 % | +5 % | – | – |
| VECTO tractor B2 | −6 % | +30 % | +15 % | – | – |
| IVECO S-eWay | +14 % | +83 % | +41 % | unusable | unusable |

Why EU std is +30 % on B2 but +6 % on tractor E2 (3 Nov data): B2 has 2 motors, a 3-speed gearbox and a very efficient own drivetrain (drag 0.26 kN vs std 0.70 kN at 55 km/h), plus low CdA 4.31 m² and low RRC. The total energy is small, so standard losses weigh more. Tractor E2: own drag 0.56 kN vs std 0.55 kN.

Conclusion: no fallback stays within ±10 % on all trucks. Bus method is the most even and rarely underestimates. EU std is best only when EEA says the component used standard values.

---

## 6. Calibrating HDEV to EEA certified values

Idea: EEA gives certified kWh/km for every mission × payload (4–10 results per truck). Keep HDEV's vehicle physics and tune the unknown drivetrain (and CdxA where it was measured) to those results. Then predict the user's route.

### First attempts (fitted on 1–2 missions)
- One efficiency, fitted on 1 mission → Urban 20–34 % off. Fails.
- Efficiency + fixed loss per hour → unphysical fit, up to 13 % off. Fails.
- Bus-map shape + loss scale + CdxA, fitted on Regional + Urban → Canter 0.4 %, S-eWay 5–6 %.
- Bob's simple reverse idea (efficiency + drag force at wheel + CdxA, fitted on 3 runs) on 5 trucks → Long Haul/Regional/EMS within ±5 % on all four tractors; Urban light payload +5 to +13 %; fails on Canter; some fitted values unphysical (CdxA hit the 3.0 m² floor; Scania drag negative).

### Final test: leave-one-out on 10 trucks (`robust.py`, `final.py`)
Each certified result is predicted with a fit made **without** it.

Methods (same vehicle physics for all):
- **A** Today's code, no calibration (0.95·0.95·0.98, regen 0.95, CdxA default).
- **B** 1 efficiency (drive = regen) + drivetrain drag force F0 at the wheel (+ CdxA if EEA air drag is measured).
- **C** Separate drive and regen efficiency + F0 (+ CdxA if measured).
- **D** VECTO bus-generic IEPC map with a fitted loss scale (+ CdxA if measured). Single-gear IEPC only.

Fit bounds: eta 0.5–1.0 (regen 0.3–1.0), F0 0–3,000 N, CdxA 3–11 m².

Worst error vs EEA certified (leave-one-out):

| Truck | A today | B | C | D |
|---|---|---|---|---|
| Fuso eCanter, 7 t rigid, 1-gear | 34.3 % | 13.3 % | 11.6 % | **1.5 %** |
| IVECO S-eWay, 40 t tractor, 1-gear | 16.4 % | 3.5 % | 2.3 % | **2.1 %** |
| Scania R 400E (C0371), tractor, 6-gear | 25.9 % | 5.6 % | 5.5 % | – |
| MAN eTGX (C0116), tractor, 4-gear | 29.1 % | 8.9 % | 7.9 % | – |
| Mercedes eActros 600 (C0153), 4-gear | 37.8 % | 11.1 % | 8.3 % | – |
| Renault D (C0218), 4x2 rigid, 2-speed E2 | 24.9 % | 6.9 % | **4.6 %** | – |
| Volvo FM (C0712), 6x2 rigid, 12-gear | 3.1 % | 1.5 % | 1.9 % | – |
| Mercedes Econic (C0206), 6x2 refuse, 2-gear | 6.0 % | 1.2 % | 0.9 % | – |
| IVECO eDaily (C0070), group 53, E3 | 14.5 % | 2.0 % | 0.7 % | – |
| DAF XB (C0001), 6x2 rigid, 3-gear | 4.4 % | 3.3 % | 2.6 % | – |

kWh/km, Regional Delivery at the heavier payload (predicted without that run):

| Truck | EEA certified | A | B | C | D |
|---|---|---|---|---|---|
| Fuso eCanter | 1.24 | 0.83 | 1.09 | 1.13 | 1.23 |
| IVECO S-eWay | 1.30 | 1.49 | 1.31 | 1.31 | 1.31 |
| Scania R 400E | 1.59 | 1.44 | 1.60 | 1.60 | – |
| MAN eTGX | 1.23 | 1.44 | 1.24 | 1.24 | – |
| Mercedes eActros 600 | 1.07 | 1.39 | 1.09 | 1.09 | – |
| Renault D | 1.17 | 1.10 | 1.16 | 1.17 | – |
| Volvo FM | 1.24 | 1.21 | 1.24 | 1.25 | – |
| Mercedes Econic | 1.17 | 1.12 | 1.17 | 1.17 | – |
| IVECO eDaily | 0.75 | 0.68 | 0.75 | 0.75 | – |
| DAF XB | 1.11 | 1.12 | 1.09 | 1.09 | – |

Method C misses above 5 %:
- Fuso eCanter: Urban 1.7 t +11.6 %, Urban 0.3 t +5.7 %, Regional 1.7 t −9.1 %, Regional 0.3 t −10.8 %.
- Scania: Urban 12.9 t −5.5 %.
- MAN: Urban 12.9 t −7.9 %, Urban 2.6 t +7.2 %.
- Mercedes eActros 600: Urban 12.9 t −8.3 %, Urban 2.6 t +7.0 %.

Conclusions:
- **C is the best method that works on every truck.** 7 of 10 trucks have every predicted result within 5 %. Misses are Urban (both directions) and the Canter.
- **D is the most accurate (≤ 2 %)** but needs the gear ratio → only single-gear trucks in EEA.
- **Today's code (A)** is 3 % to 38 % off.
- The miss pattern says losses must depend on speed/load (D's map shape fixes this on the Canter).

Limits:
- DAF has 4 certified results for 4 fitted values → weak test.
- Fitted CdxA / drag / efficiencies are effective values, not physical truths (e.g. Canter bus-map fit gave CdxA 8.25 m² vs known 7.1 m²).
- Only VECTO cycles tested; real routes not tested. HDEV can only be as good as VECTO vs reality (JRC, Bitsanis et al. 2023, SAE 2023-01-0485: VECTO electric energy within 2.5 % of measured — from the 3 Nov notes).
- Truck tyre FzISO not in EEA → assumed wheel load = test load (base^(β−1) = 1).
- Driven axle assumed = axle 2 (EEA axle table has no axle type).
- HVAC = "Default" row (EEA HVAC config blank); ES = "Standard technology"; group 51–56 use ES-Tech_Medium.
- HDEV has no battery-loss model; certified includes REESS and charging losses (EEA ratio 1.016 Canter, ~1.000 S-eWay). In calibration these are absorbed into the fitted efficiency.

### Possible default rule (Bob to decide; not decided)
- Truck in the EEA library → calibrate to its certified results. Use **C** for all trucks; use **D** where the truck is single-gear IEPC.
- Truck not in EEA → uncalibrated bus method (V-C) with a stated error band; ask for the motor type.
- Next test proposed: C + a loss term that grows with motor speed (EEA lowest total ratio as speed proxy) to fix the Urban misses.

---

## 7. Issues found in Bob's notebook (`HDEV_NEW_code_of_record_2026-11-07.ipynb`)

Already known (Kiro fixes 1–3 in test copies only):
1. `driver_model` accelerate branch: `v_cap = …` and `a = max(min(a, (v_cap - v) / dt), 0.0)` on one line → SyntaxError.
2. Drag table change half done: `P_drag_loss` still in `driver_model`, passed to `coast_distance` (TypeError) and used in `coast_acc`.
3. `g` default 9.81 (agreed 9.80665).
4. `pto_engine` test cell uses old signature.

New this session:
5. **Rolling resistance inconsistent:** `driver_model` / `coast_distance` use Crr·m·g (linear in mass); `consumption_engine` uses Crr·g·m^β. One Crr can't satisfy both. In the runs: driver got VECTO's total RRC, consumption got RRC·m^(1−β).
6. **`P_max` only works with coasting on:** `if P_max is not None and coast_on:`.
7. **Aux timing differs from VECTO:** `consumption_engine` applies SP only while moving and cond only while moving or PTO active; VECTO aux are `DemandType.Constant` (cond is Dynamic) (`HeavyLorryAuxiliaryDataAdapter.cs` 61–110).

---

## 8. Files

Project (`claude/`):
- `kiro-prompt-eea-truck-validation-v2-2026-11-07.md` — v2 Kiro prompt (not yet in the repo; Bob to push to `docs/research/inputs/`).
- `findings-hdev-vs-eea-2-trucks-2026-11-07.md` — running findings note.
- `session-closeout-2026-11-07-validation-fallbacks-calibration.md` — this file.

Claude workspace only (sent to Bob in chat; not in repo): `run_compare.py`, `nbmod.py`, `sens.py`, `ext.py`, `calib*.py`, `robust.py`, `final.py`, `results*.csv`, `calibration_kwh_km.csv`, graphs (`hdev_vs_eea_abs.png`, `hdev_vs_eea_pct.png`, `fallback_scorecard_v2.png`, `reverse_calibration.png`, `calibration_worst_error.png`). The workspace is not permanent; re-run scripts need the VECTO sparse checkout and the hdev clone.

---

## 9. Next steps (in order)

1. Bob: push the v2 Kiro prompt to the repo; review Kiro's v2 PR when it arrives (check items in section 3).
2. Bob: decide the default drivetrain rule (section 6).
3. Claude: test C + speed-dependent loss term on the same 10 trucks (aim: Urban ≤ 5 %).
4. Claude: test calibration on more trucks (buses out of scope), incl. more urban-heavy configs.
5. Bob: fix notebook issues 1–3 and decide on 5–7.
6. Open: CdxA bin edges `[BOB]`; truck FzISO `[BOB]`; motor type for IEPC trucks (not in EEA).
