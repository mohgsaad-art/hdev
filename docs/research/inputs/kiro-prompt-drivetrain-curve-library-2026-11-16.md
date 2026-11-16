# Kiro prompt: drivetrain efficiency curves from VECTO shapes, calibrated per truck on EEA certified results (16 Nov 2026)

Owner: Bob. Repo: `mohgsaad-art/hdev`. **Today's date is 16 November 2026.** When you research, look for material up to this date (VECTO releases, regulation amendments, papers and open-source code from 2023–2026).

**Run the whole job in one uninterrupted pass.** Do not stop to ask Bob anything. If something is unclear, choose the option that changes the least, write it under "Choices I made", and carry on. Open **one PR** at the end.

**Branch:** create `drivetrain-curve-library-2026-11` from `main`. First commit: copy this prompt to `docs/research/inputs/kiro-prompt-drivetrain-curve-library-2026-11-16.md`. Put everything new in `docs/research/drivetrain-curve-library-2026-11/` and `tests/drivetrain_curves/`. Open the PR from this branch to `main`.

---

## 0. The question in one paragraph

HDEV must size truck batteries **before a truck is chosen**, and check offers **once a truck is chosen**. Users never have drivetrain loss maps, gear ratios or motor curves. Drivetrain losses change energy by about 30 % (fixed 0.95/0.95/0.98 gives 0.712 kWh/km on VECTO's E2 Regional vs 0.947–0.971 with VECTO's maps). On 7 Nov, calibrating three numbers per truck (Method C: drive efficiency, regen efficiency, a drag force F0) to that truck's EEA certified results predicted a held-out mission within 5 % for **7 of 10** trucks; the misses were mostly Urban, which points to losses that depend on load. **This job tests whether a load-dependent efficiency curve, whose shape comes from VECTO's own maps and which is stretched to each truck with 1–2 fitted numbers, beats Method C.** If it does, the fitted curves for every EEA truck and the median curve per weight class become HDEV's drivetrain library.

---

## 1. Rules for this job (read first)

1. **Do not edit Bob's engine code** (the notebook or anything under `src/`). Copy functions into `docs/research/drivetrain-curve-library-2026-11/reference_copy.py` and make clearly named variants there. Every proposed engine change goes into the report as a before/after snippet with its measured effect.
2. **No invented numbers.** Every value you use comes from a named source: VECTO source/resource file + line (fork `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`; re-check every line number in this prompt), Regulation (EU) 2017/2400 incl. amendments, an ISO/EN/UN/JRC/NREL/EPA document, the EEA data, or a peer-reviewed paper or official report with a link. No source → write `NO SOURCE` and leave it open. Illustrative values only inside tests, labelled `ILLUSTRATIVE`.
3. **No silent fallbacks.** Missing input → `BLOCKED: <what>` and keep going. Never fill a field from a row that differs in any other key field (7 Nov rule).
4. **Tag every statement:** `[VECTO]` (file, lines, commit), `[REG]`, `[DATA]` (EEA file, column, row filter), `[SOURCE]` (link, date, full text or abstract only), `[CALC]` (inputs shown), `[TEST]` (script + function), `[ASSUMPTION]`, `[OPEN]`. A number seen only in a search snippet is `[SOURCE, snippet]` and is never a model input.
5. **Data licence.** Use only the official EEA data (CC-BY 4.0) and VECTO (EUPL 1.2). **Do not use Bob's other large VECTO-input file** (source and licence unknown, 6 Nov note). Every output file that holds EEA-derived values carries a CC-BY attribution line.
6. **Validation meaning (Bob's rule).** Matching VECTO certified results is calibration, not validation. Validation needs independent measured data (Part F). Say clearly which is which.
7. **Conservative side.** HDEV must not underestimate energy. For every method, report the share of predictions that are too low, and how far.
8. **Accuracy target:** HDEV kWh/km within 5 % (decided 7 Nov).
9. **Inputs users can give.** A method that needs inputs a fleet user cannot give is only allowed in the per-truck (OEM/EEA) path, never in the sizing path. Say for each method which path it can serve.
10. **Reproducible.** Run every main script twice; confirm identical CSVs. Fix random seeds.
11. **Plain English** in the report. Short sentences. Define technical terms. Refer to the owner only as "Bob". Never decide an open design choice for Bob; label recommendations "Kiro's recommendation".

### 1.1 Pitfalls from earlier Kiro PRs (do not repeat)
- Re-implementing Bob's functions instead of calling them (PR #27, `_drivetrains.py`).
- A gate that compares hard-coded numbers instead of running the harness (v2 mid-run).
- Inventing rated speed (`n_rated = 3000`), drag formulas, aux constants or CdxA tables (PR #27 list in `claude/session-closeout-2026-11-07-validation-fallbacks-calibration.md` §2, copied in `docs/research/inputs/` if present; otherwise use the v2 report).
- Fitting as many parameters as data points (DAF on 7 Nov had 4 results for 4 parameters: weak test). Report degrees of freedom for every fit.
- Reading a fitted value as a physical truth (a fitted CdxA of 8.25 m² vs the known 7.1 m² on the Canter). Fitted values are **effective** values.

---

## 2. What exists (inputs)

| What | Where |
|---|---|
| EEA truck validation **v2** harness (gate passed 0.03 %): `run_hdev.py`, `hdev_test_module.py`, `mission_setup.csv`, `aux_per_label.csv`, `truck_configs.csv`, `truck_missions.csv`, `truck_vehicles.csv`, `report.md` (incl. "certified kWh/km is grid-side, energy ÷ η ≈ 0.995; usable window 0.855") | branch `eea-truck-validation-2026-11`, commit `73990f0`, folder `docs/research/eea-truck-validation-2026-11/` |
| EEA 2024–25 joined tables (4,603 BEV trucks, 835 configs) | `main`, `docs/research/eea-hdv-2024-join/` (`vehicles_xev.csv`, `missions_xev.csv`, `configs_xev.csv`, `axle_xev.csv`) |
| Code of record (notebook) | `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-13.ipynb` (branch `consumption-review-2026-11` / `inputs-code-of-record-2026-11-13`). Load code cells only, skip cell 0 (it imports torch/gymnasium/requests). |
| Consumption review (step 5 variants, Chain S, drag tables) | branch `consumption-review-2026-11`, `docs/research/consumption-review-2026-11/` |
| Drag default test (Chain S, E2 drag table, `run_steps.py`) | `main`, `docs/research/drag-default-test-2026-11/` |
| VECTO `.vmod` / `.vsum` of BEV_E2 (Regional, Urban, LongHaul × Reference, Low) | `main` or `consumption-review-2026-11`, `docs/research/vecto/` |
| **New `drivetrain` function** (wheel → axle → gearbox → mech. PTO → ADC → rotor → motor limits → motor map) | **Appendix A** of this prompt (verbatim). Copy it into `reference_copy.py`. |
| VECTO generic maps | fork: `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/` (axle `.vtlm`, `Gear_1/2.vtlm`, `.vemo`, `.vemp`, `.vemd`), `Generic Vehicles/Declaration Mode/PEV/GenericIEPC/`, `VectoCore/VectoCore/Models/GenericModelData/GenericBusIEPCData.cs` + IEPC normalised maps, `VectoCoreTest/TestData/BatteryElectric/GenericVehicleB2*`; EU standard-value formulas in Annex Xb App. 8–9 (motor), Annex VI App. 8 (gearbox), Annex VII App. 3 (axle) (knowledge-base extracts under `claude/knowledge-base/eu-regulation-2017-2400/`, or read the regulation) |
| Other tools' curves (read only) | `mohgsaad-art/fastsim` (`electric_machine.rs`, efficiency vs fraction of rated power), T3CO demo CSV, KIT thesis (shape only, no numbers) — see `claude/findings-other-tools-review-2026-11-09.md` |

### 2.1 Facts Claude checked on 15–16 Nov (re-verify, do not trust blindly)
- VECTO declaration mode **ignores** the `.vveh` ADC `MechanicalEfficiency` and uses **1.0** (`DeclarationData.cs` 114 `ElectricMachineDefaultMechanicalTransmissionEfficiency = 1`; used in `ElectricMachinesDataAdapter.cs` 118). With 0.97 the E2 electric energy came out +2.6 to +4.7 % high.
- E2 has **2 motors** × 0.225 kg m² = 0.45 kg m² total rotor inertia (`GenericEMotor_125kW_485Nm.vem` `Inertia`, `.vveh` `Count = 2`).
- `.vemo` sign convention: positive torque = motoring, positive `P_el` = drawn (e.g. 1969 rpm, +194 Nm → +43.7 kW; −194 Nm → −36.5 kW).
- Loss rule: `in = out / ratio + loss(in_speed, out / ratio)` (`AxleGear.cs`, `TransmissionLossMap.cs` 53, 94; Delaunay interpolation; extrapolation flagged line 97).
- One efficiency → VECTO flat 6-point map, loss = (1 − η)·|T| (`TransmissionLossMapReader.cs` 203–227).
- `drivetrain` fed VECTO's own `.vmod` rows (power at axle output, speed, gear, rotor power) reproduces VECTO's electric energy at **−0.35 % / −0.56 % / −0.41 %** (Regional / Urban / LongHaul, reference load). Gearbox loss is **−2 to −3 %** low (cause not found; suspicion: VECTO looks the loss up at a different speed than the step average — **find it**, Part A4).
- Gear rule "highest gear the motor can manage" matches VECTO's gear on 99.5–100 % of E2 rows (energy within 0.3 % of VECTO-gear runs). Fixed lowest gear is +46 to +71 % (motor over max speed).

---

## 3. Gates (must pass before anything else)

**Gate 1 — v2 harness:** run the v2 harness gate (`gate_e2.py`) unchanged on this branch. Expect the four E2 numbers in the v2 report within 0.1 %. If it fails, stop everything except Part A and report.

**Gate 2 — `drivetrain` reproduction:** feed `drivetrain` (Appendix A) the E2 `.vmod` rows exactly as described in §2.1 and reproduce Claude's three numbers (−0.35 / −0.56 / −0.41 %) within 0.05 percentage points. Script: `gate_drivetrain.py`. Use `eta_adc = 1.0`.

**Gate 3 — Method C reproduction:** re-run the 7 Nov Method C leave-one-out on the 10 trucks (table in Appendix B) with the v2 harness. Reproduce "7 of 10 trucks with every prediction within 5 %" and the worst-error column within ±1 percentage point per truck. If the v2 harness gives different numbers, report both, explain the difference, and use the v2 harness as the baseline from here on.

---

## 4. The parts

### Part A — Build the shapes (curves from VECTO maps)

A1. **What a "shape" is.** Efficiency as a function of **load fraction** x = |P| / P_rated, separately for **driving** (motor pushes) and **recovering** (regen). Do this for the whole chain (axle + gearbox + motor incl. inverter) **and** per part, so Bob can see where the losses sit.

A2. **How to build it** (the KIT method, `claude/findings-other-tools-review-2026-11-09.md` §12.1, but with VECTO data so every point traces to a file): run `drivetrain` with VECTO maps over the VECTO declaration cycles (`MissionCycles/*.vdri`: Regional, Urban, LongHaul, Municipal, Construction where applicable) using Bob's `driver_model` + `force_engine` at the matching vehicle mass. Record per 1 s row: x, chain efficiency, gear, motor speed. Bin by x (state the bin edges and why) and take the energy-weighted efficiency per bin. Report the scatter around each bin (it shows how much a 1-D curve throws away).

A3. **Which shapes.** At least:
- S1: VECTO generic E2 (central motor + 2-speed AMT, `GenericVehicleE2`).
- S2: VECTO bus-generic IEPC (`GenericBusIEPCData.cs`), scaled per VECTO's normalisation.
- S3: VECTO `GenericIEPC` 1-speed and 3-speed examples.
- S4: EU standard-value motor (Annex Xb App. 8, PSM and ASM) + standard gearbox and axle — **only** where its inputs come from a source; the 7 Nov finding was that EEA lacks the full-load curve, so state exactly what you had to assume, or mark `BLOCKED`.
- Compare with FASTSim's and T3CO's curve (passenger-car origin, Brooker 2015) as a plot only, not as an input.

A4. **Gearbox loss −2 to −3 %.** Find in VECTO source why `drivetrain` gives a lower gearbox loss than the `.vmod` (which speed and torque VECTO uses for the lookup; whether shift rows or inertia add to `P_gbx_loss`). Give the file and line, the size of the effect, and a before/after snippet for `drivetrain`.

A5. **Is the shape the same for all?** Overlay the normalised shapes (each divided by its own peak). Report where they differ (low-load drop, peak position, regen side) and by how much in efficiency points. Recommend whether HDEV needs one shape, one per architecture (E2/E3 vs E-IEPC vs E-IEPC wheel-motor), or one per motor type (PSM/ASM). Evidence first, then "Kiro's recommendation".

### Part B — The calibration methods to compare

Same vehicle physics for all (v2 harness: driver, forces, tyres, aux, crosswind, ρ 1.188, grid-side ÷ 0.995). Only the drivetrain differs.

| Method | Drivetrain | Fitted per truck | Fitted values |
|---|---|---|---|
| A | today's fixed 0.95·0.95·0.98, regen 0.95 | none | 0 |
| C | separate drive and regen efficiency + drag force F0 at the wheel (+ CdxA if EEA air drag is measured) | yes | 3–4 |
| D | bus IEPC map + loss scale (+ CdxA) | yes, single-gear IEPC only | 1–2 |
| **L1** | **shape (Part A) × one scale factor** on losses, same for drive and regen | yes | 1 (+CdxA) |
| **L2** | **shape × drive scale + regen scale** | yes | 2 (+CdxA) |
| **L3** | **shape × scale + one low-load term** (e.g. a constant loss power, sourced form) | yes | 2 (+CdxA) |
| **G** | class-median curve from Part D, **no per-truck fit** (the sizing path) | no | 0 |

For each L-method, write the exact formula, which shape it uses for which architecture, and the fit bounds with the reason for each bound (7 Nov bounds: eta 0.5–1.0, regen 0.3–1.0, F0 0–3,000 N, CdxA 3–11 m²; keep them unless you show a reason to change).

Use `drivetrain` in numbers/curve mode where it fits (efficiency as a scalar **or** a curve vs load fraction; propose the minimal change to `drivetrain` or to `consumption_engine` step 5 that accepts a curve, as a before/after snippet).

### Part C — Leave-one-out on the 10 trucks (the main test)

- The 10 trucks of 7 Nov (Appendix B). Each certified result is predicted with a fit made **without** it.
- For every method: worst error per truck, error per mission and payload, share of predictions within 5 %, share too low and the largest underestimate, and degrees of freedom (results minus fitted values).
- **Pass mark:** a method "beats C" only if it has **more trucks with every prediction within 5 %** than C **and** its worst underestimate is not larger than C's. Say plainly whether any L-method beats C.
- Graphs: worst error per truck per method (bar), predicted vs certified (parity), error by mission (Urban vs others).

### Part D — Go wider: every usable EEA truck, and the class curves

D1. **Usable set.** From the 4,603 trucks / 835 configs: which configs have enough certified results for a leave-one-out fit with the best method (results ≥ fitted values + 2)? Count by group (weight class), axle configuration, architecture and make. Duplicates collapsed per the 7 Nov rules (one row per exact config; curb mass as a range).

D2. **Fit every usable config** with C and with the best L-method. Leave-one-out stats as in Part C, now per group and per architecture.

D3. **Class curves (the sizing path, method G).** Per VECTO group (and architecture where Part A5 says so): the median fitted curve and its spread (P10/P90 of the predicted kWh/km on each VECTO mission). Weight by how common each config is (registration counts in the EEA data) and say whether weighting changes the result. Then test G honestly: predict each truck's certified results with the class curve of **its own class built without that truck** (leave-one-truck-out). Report the error band per class. This band is what a sizing user would get.

D4. **Library file.** Write `curve_library.csv` (one row per config: EEA config key, make, model, group, axle config, architecture, method, fitted values, fit quality, number of results used, CC-BY attribution) and `class_curves.csv` (one row per class: curve points, spread, number of trucks). Write `library_schema.md` describing every column, unit and source. Do **not** put anything in `src/`.

### Part E — What the certified numbers include
Check, from VECTO source, everything inside a certified kWh/km that HDEV will later model separately (battery Ri loss, charging efficiency 0.995, aux constants, PTO for Municipal) so the fitted drivetrain values do not secretly absorb them. State, for each, whether the v2 harness models it or the fit absorbs it, and the likely size. If the fit absorbs battery loss, say how the library must be corrected once HDEV's battery model (OCV + Ri) exists.

### Part F — Independent validation (measured, not VECTO)
Find measured BEV truck energy data where the truck can be matched to an EEA config or set up from sourced values: Öko-Institut ELV-LIVE / eActros measurements, NREL Fleet DNA or NREL truck reports, ICCT real-world BEV truck studies, VTT/HSY e-refuse, Mercedes eActros 600 test reports, Volvo/Scania/MAN published tests, Nordic trials. For each: what was measured (battery side or grid side, route, temperature, payload), and HDEV's prediction with (a) C, (b) the best L-method, (c) G. Unmatched or missing data → `BLOCKED` with what is missing. Anything behind a paywall → "Bob to fetch" with the link and exactly what to read.

### Part G — Performance
Time the fits (per truck and for the whole set) and the curve lookup inside a year run (≈ 250 dates × 1 truck). State the CPU.

---

## 5. Deliverables

1. `docs/research/drivetrain-curve-library-2026-11.md`, in this order:
   - **Summary first (one page, plain English):** does any L-method beat C (yes/no, numbers), the error band a sizing user would get per class (method G), how many EEA configs the library covers, the conservative-side check, and open items.
   - Gates 1–3.
   - Part A (shapes, the gearbox-loss cause, one shape or several).
   - Parts B–C (tables first, graphs in the folder).
   - Part D (coverage, per-class results, the library files).
   - Parts E–G.
   - **Proposed changes** to `drivetrain` / `consumption_engine` step 5 (before/after snippets, measured effect, engine or `defaults.py` or reader).
   - "Choices I made", `NO SOURCE` list, `BLOCKED` list, "Bob to fetch" (link + exactly what).
2. `docs/research/drivetrain-curve-library-2026-11/`: `reference_copy.py`, one runnable script per part, all CSVs (incl. `curve_library.csv`, `class_curves.csv`, `library_schema.md`) and graphs. Each script prints the files it wrote.
3. `tests/drivetrain_curves/` (`pytest`): shapes rebuild identically; a flat curve equals the scalar-efficiency result; the curve at x = 1 matches the map at rated power; fits are deterministic.
4. One PR to `main`. The description lists what was done, how to run every script and the tests, the top 5 findings with numbers, and every `NO SOURCE`, `BLOCKED` and "Bob to fetch" item.

## 6. Stop conditions
- A crash or a wrong number on a realistic input → report as **BUG** with a minimal reproducing input, and keep going.
- Never edit the notebook or `src/`. Never decide an open design choice for Bob.

---

## Appendix A — `drivetrain` (written 15–16 Nov 2026, not yet in Bob's notebook; copy verbatim)

The code block for Appendix A is copied verbatim into
`docs/research/drivetrain-curve-library-2026-11/reference_copy.py` (function `drivetrain`).
It is not repeated in this copy of the prompt.

Gear rule tested with it ("highest gear the motor can manage", ~8 lines; not yet decided by Bob): call `drivetrain` once per gear with all rows in that gear; a gear is OK on a row if motor speed ≤ max speed of the `.vemp` and `over_limit` is False; pick the highest OK gear.

## Appendix B — the 10 trucks of 7 Nov (EEA config IDs)

| Truck | EEA ID | Type | Method C worst error (7 Nov) |
|---|---|---|---|
| Fuso eCanter | C0059 | 7 t rigid, 1-gear IEPC | 11.6 % |
| IVECO S-eWay | C0091 | 40 t tractor, 1-gear IEPC | 2.3 % |
| Scania R 400E | C0371 | tractor, 6-gear | 5.5 % |
| MAN eTGX | C0116 | tractor, 4-gear | 7.9 % |
| Mercedes eActros 600 | C0153 | 4-gear | 8.3 % |
| Renault D | C0218 | 4x2 rigid, 2-speed E2 | 4.6 % |
| Volvo FM | C0712 | 6x2 rigid, 12-gear | 1.9 % |
| Mercedes Econic | C0206 | 6x2 refuse, 2-gear | 0.9 % |
| IVECO eDaily | C0070 | group 53, E3 | 0.7 % |
| DAF XB | C0001 | 6x2 rigid, 3-gear | 2.6 % |

Method C misses above 5 % on 7 Nov: Canter (Urban 1.7 t +11.6 %, Urban 0.3 t +5.7 %, Regional 1.7 t −9.1 %, Regional 0.3 t −10.8 %); Scania (Urban 12.9 t −5.5 %); MAN (Urban 12.9 t −7.9 %, Urban 2.6 t +7.2 %); eActros 600 (Urban 12.9 t −8.3 %, Urban 2.6 t +7.0 %). The 7 Nov scripts were in Claude's workspace and are **not** in the repo; rebuild Method C on the v2 harness (Gate 3).

---

Note: this is a copy kept for the record. Appendix A code is stored in `reference_copy.py` instead of being repeated here.
