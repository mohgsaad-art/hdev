# Kiro prompt: fixed drivetrain numbers vs a fitted loss equation, on EEA certified trucks, with real air-drag ranges (16 Nov 2026, v2)

Owner: Bob. Repo: `mohgsaad-art/hdev`. Today's date is 16 November 2026.

**This replaces `kiro-prompt-drivetrain-curve-library-2026-11-16.md`** (the previous run was stopped after one command ran for 40 minutes). Narrower scope, hard runtime limits, and one new input (the CdxA range table) that removes the main error seen in that run.

**Run in one uninterrupted pass. Do not ask Bob anything.** Unclear → choose the option that changes the least, write it under "Choices I made", carry on. Open **one PR** at the end.

**Branch:** `drivetrain-curve-library-2026-11` from `main`. If you still have that branch locally from the stopped run, continue on it and reuse `reference_copy.py`, `harness.py`, `methods_lib.py`, `shapes_lib.py`, the cache and the gate scripts; otherwise rebuild them. First commit: copy this prompt to `docs/research/inputs/`. Everything new goes in `docs/research/drivetrain-curve-library-2026-11/` and `tests/drivetrain_curves/`.

---

## 0. The question

Users of HDEV have no drivetrain maps. EEA publishes, for 4,603 real battery-electric trucks, certified kWh/km per VECTO mission and payload, plus most other inputs. From those few certified results we fit a few drivetrain numbers per truck. **Which works better when predicting a result the fit has not seen, and by how much do the two differ:**
- **Method C:** fixed numbers: one drive efficiency, one regen efficiency, one drag force F0 at the wheel;
- **Method L4:** a loss **equation** whose 2–3 coefficients are fitted per truck, giving a load-dependent (and optionally speed-dependent) efficiency every second?

Nothing else is the bar. **Do not use or cite any "7 Nov" result** (those scripts were never in the repo; Bob has dropped them).

---

## 1. Rules

1. **Runtime (new, strict).** No single command may run longer than **10 minutes**. Before any loop over trucks × methods × folds, time **one** truck and extrapolate; if the full loop would exceed 10 minutes, split it, run it in the background in chunks that each write their own CSV, and parallelise (`multiprocessing`, all cores). Cache every per-run record (`.npz`, git-ignored) so nothing is recomputed. Commit and **push** after every part (`git push` each time), so a stopped run loses nothing.
2. **Do not edit Bob's engine code** (notebook, `src/`). Variants go in `reference_copy.py`. Proposed engine changes = before/after snippet + measured effect in the report.
3. **No invented numbers.** Every value from a named source (VECTO fork `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`, file + line; regulation + annex/point; EEA file + column; paper + link). No source → `NO SOURCE`. Missing input → `BLOCKED: <what>`, keep going. No silent fallbacks.
4. **Tag every statement:** `[VECTO]`, `[REG]`, `[DATA]`, `[SOURCE]`, `[CALC]`, `[TEST]`, `[ASSUMPTION]`, `[OPEN]`.
5. **VECTO-equivalent mode for every fit (Bob, 16 Nov).** The fitted drivetrain values must hold the drivetrain and nothing else. HDEV runs with all its deliberate deviations from VECTO off: ρ 1.188, declaration crosswind, VECTO aux table values (no `HVAC_thermal`, no fresh air), VECTO reference payloads, VECTO cycles, `.vacc` and driver constants, η_charge 0.995 as in the certified number. Report every remaining HDEV-vs-VECTO difference with its size on the E2 `.vmod` runs.
6. **Air drag must not be absorbed by the drivetrain fit.** Use the CdxA ranges of §2.1 (next section). Never use a standard CdxA for a truck whose EEA record says air drag was measured.
7. **Few fitted values.** Report degrees of freedom (certified results − fitted values) for every truck and fit. No neural networks or many-parameter models. Every fitted value must have a physical meaning and be checked for plausibility.
8. **Conservative side.** HDEV must not underestimate energy: report the share of predictions that are too low and the largest underestimate, per method.
9. **Scope: the 10 trucks of Appendix B only** (no wider EEA runs, no library files).
10. EEA data CC-BY 4.0 only (attribution line in every output file holding EEA values). Do **not** use Bob's other large VECTO-input file (unknown source and licence).
11. Plain English, short sentences, refer to the owner only as "Bob". Never decide an open design choice for Bob; label recommendations "Kiro's recommendation".

---

## 2. Inputs and what is already known

### 2.1 CdxA ranges (new: found by Claude, 16 Nov)
**Regulation (EU) 2018/956, Annex I, Part C, "Air drag value (CdxA) ranges for the purpose of publication"** (used for EEA's `AirDrag_CdxA_range` codes A1–A24). Rule: `CdxA ≥ min` and `CdxA < max`, in m². Read from the UK-retained copy (https://www.legislation.gov.uk/eur/2018/956/annex/I, Part C; only the heading was changed there). **Verify against the EU text on EUR-Lex** (https://eur-lex.europa.eu/eli/reg/2018/956/oj) and any later amendment; report any difference.

| Range | min | max | | Range | min | max |
|---|---|---|---|---|---|---|
| A1 | 0.00 | 3.00 | | A13 | 5.12 | 5.38 |
| A2 | 3.00 | 3.15 | | A14 | 5.38 | 5.65 |
| A3 | 3.15 | 3.31 | | A15 | 5.65 | 5.93 |
| A4 | 3.31 | 3.48 | | A16 | 5.93 | 6.23 |
| A5 | 3.48 | 3.65 | | A17 | 6.23 | 6.54 |
| A6 | 3.65 | 3.83 | | A18 | 6.54 | 6.87 |
| A7 | 3.83 | 4.02 | | A19 | 6.87 | 7.21 |
| A8 | 4.02 | 4.22 | | A20 | 7.21 | 7.57 |
| A9 | 4.22 | 4.43 | | A21 | 7.57 | 7.95 |
| A10 | 4.43 | 4.65 | | A22 | 7.95 | 8.35 |
| A11 | 4.65 | 4.88 | | A23 | 8.35 | 8.77 |
| A12 | 4.88 | 5.12 | | A24 | 8.77 | 9.21 |

Values above 9.21 m²: no range in this table → `[OPEN]`, report how many trucks.

**Must answer from VECTO source before using it (Part 1):** what does the declared CdxA (data entry 23 of Reg. 2018/956 Annex I) cover for each vehicle type, and how does VECTO build the CdxA used in each mission from it? In particular for tractors (groups 5, 10, 12): does the declared value already include the standard semi-trailer, or does VECTO add a trailer ΔCdA per mission (`SegmentTable`, `DeclarationData` trailer entries, `AirdragDataAdapter`)? And for rigid trucks on missions with a trailer (Long Haul, EMS). File + line for each.

### 2.2 Found in the stopped run (re-use, do not re-derive)
- **Gate 1 passed** (v2 harness reproduces VECTO E2 within 0.03 %).
- **Gate 2 passed** (`drivetrain` vs `.vmod`: −0.350 / −0.562 / −0.406 %) **with the mask "motor fully on" (`EM_E2_off == 0`)**. `EM_E2_off` takes fractional values; VECTO switches the motor off on some braking rows.
- **Gearbox loss cause found:** VECTO builds the loss-map triangulation on (input speed, input torque − loss) (`TransmissionLossMap`), not (input speed, input torque). Converting the map coordinates before calling `drivetrain` brings gearbox loss within 0.06 % on non-shift rows. Implement it as a **reader function** `vecto_loss_map()`; do not change `drivetrain`.
- E2 `R85RatedPower` 250 kW = 2 motors × 125 kW (FLD peak 485 Nm × 2461 rpm per motor).
- Using a standard CdxA for trucks with measured air drag produced a mission-dependent bias (Regional/Long Haul +8 to +25 %, Urban/Construction about −8 %) on the same truck (MAN C0116 etc.). The ranges of §2.1 are the expected fix; this job tests it.

### 2.3 Files
| What | Where |
|---|---|
| EEA v2 harness (`run_hdev.py`, `hdev_test_module.py`, `mission_setup.csv`, `aux_per_label.csv`, `truck_configs.csv`, `truck_missions.csv`, `truck_vehicles.csv`, `gate_e2.py`, `report.md`) | branch `eea-truck-validation-2026-11`, commit `73990f0` (use a git worktree) |
| EEA 2024–25 joined tables | `main`, `docs/research/eea-hdv-2024-join/` |
| Code of record (notebook; load code cells only, skip cell 0) | `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-13.ipynb` |
| VECTO E2 `.vmod`/`.vsum` | `docs/research/vecto/` |
| `drivetrain` function (verbatim) | Appendix A of `docs/research/inputs/kiro-prompt-drivetrain-curve-library-2026-11-16.md` (copy that prompt to `docs/research/inputs/` too if missing) |
| Annex Xb App. 8 k_mn loss tables (PSM; ASM/ESM/RM) | project extract `claude/knowledge-base/eu-regulation-2017-2400/12h-annex-xb-standard-values-and-simulation-input-parameters.md` (Bob will add it to `docs/research/inputs/`); verify against the regulation if reachable |

---

## 3. Parts

### Part 1 — Air drag ranges into the harness
1. Answer the §2.1 VECTO questions (file + line).
2. Join each truck's `AirDrag_CdxA_range` and its air-drag certification method (measured vs standard values) from the EEA tables. Count trucks per range and method.
3. In the harness copy: **standard values** → VECTO's standard CdxA (as now). **Measured** → CdxA bounded to its range `[min, max)` (plus any trailer ΔCdA VECTO adds per mission, per answer 1).
4. Re-run Method A (today's fixed 0.95/0.95/0.98) on the 10 trucks of Appendix B with the **range midpoint**. Table: kWh/km vs certified per truck × mission × payload, before (standard CdxA) and after (midpoint). Does the mission-dependent bias go away? If any truck still shows a mission pattern above 5 %, list every input per mission (CdxA, trailer, ΔCdA, payload, RRC/tyres, aux label, cycle) next to VECTO's declaration data for that truck and find the cause (file + line). Fix set-up errors in the harness copy; report each fix and its effect.

### Part 2 — The methods
All share the same vehicle physics (Part 1 harness). x = wheel power / EEA rated power (rated power from `RatedPower` per Reg. 2018/956 / UN R85; for multi-motor and wheel-motor trucks state whether it is per unit or total, and how you know).

| Method | Drivetrain per second | Fitted per truck |
|---|---|---|
| A | fixed 0.95·0.95·0.98, regen 0.95 | none (reference only) |
| **C** | drive: P_el = P / η_d; regen: P_el = P · η_r; plus F0·v at the wheel | η_d, η_r, F0 (+ CdxA within its range if measured) |
| **L4a** | loss equation, one axis: `P_loss = a + b·P²`; drive P_el = P + P_loss, regen P_el = P − P_loss (P < 0), P_loss only while the drivetrain is engaged (same masks as `consumption_engine`: no coasting rows, no regen below the gearbox's disengage speed) | a ≥ 0 [W], b ≥ 0 [1/W] (+ CdxA in range) |
| **L4b** | adds a speed term, following the form of Annex Xb App. 8 Step 6 (`P_loss = Σ k_mn |T|^m |ω|^n`, whose `k_0n` terms are speed-only losses): `P_loss = a + c·v + b·P²`, v = vehicle speed | a, b, c ≥ 0 (+ CdxA in range) |

- Cite the Annex Xb App. 8 form and explain in plain words how L4a/L4b relate to it (which k_mn terms they stand for, what they drop and why: no gear ratios for multi-speed trucks in EEA → no motor speed, so vehicle speed is the proxy).
- Optimiser: `scipy.optimize.least_squares`, relative residuals, bounds as stated, 3 fixed starting points, keep the best; fixed seeds. Bounds for C: η_d 0.5–1.0, η_r 0.3–1.0, F0 0–3,000 N (state the reason for each or mark `ASSUMPTION`). For L4: derive upper bounds for a, b, c from VECTO's generic maps (no-load loss at zero torque, losses at rated power) and state them.
- Plausibility per truck: the efficiency L4 implies at x = 0.1, 0.25, 0.5, 1.0, and `a` vs VECTO generic no-load losses for a similar rated power.
- **Optional, only if time allows after Parts 1–3:** L1/L2 from the stopped run (VECTO-map shapes × fitted scale). Not required.

**Scope (Bob, 16 Nov): this job is analysis on the 10 trucks of Appendix B only.** Do not fit, sweep or build a library for any other EEA truck, and do not write `curve_library.csv` / `class_curves.csv`. Bob decides after reading the results whether a full library is built.

### Part 3 — Leave-one-out on the 10 trucks (the main result)
- Missions: every certified mission except Municipal (PTO); keep EMS. State the list per truck.
- **Leave-one-result-out:** hide one certified result, fit on the rest, predict it; repeat for every result. Also report leave-one-mission-out (hide every payload of one mission) as a second view.
- Per method: worst error per truck, error per mission and payload, trucks with every prediction within 5 %, share too low and the largest underestimate, degrees of freedom.
- **Difference between methods:** per prediction, |C − L4| in % of certified; and per truck the kWh/km both methods give on a VECTO mission neither was fitted on. Bob wants to see how much the two approaches differ, not only which wins.
- Graphs: worst error per truck per method; predicted vs certified; error by mission.

### Part 4 — Battery-loss and motor-off check
- What the certified kWh/km contains that the fit will absorb (battery Ri loss, charging 0.995, aux, VECTO's motor-off braking rows): size each on the E2 `.vmod` runs (kWh and %). Especially: **energy difference between VECTO switching the motor off on braking rows and HDEV regenerating on them**, per mission.

---

## 4. Deliverables
1. `docs/research/drivetrain-c-vs-equation-2026-11.md`:
   - **Summary first (one page):** does the CdxA range fix remove the mission bias (numbers); C vs L4a vs L4b (trucks within 5 %, worst error, underestimates, how much they differ); open items.
   - Parts 1–4, tables first.
   - Proposed changes to `drivetrain` / `consumption_engine` step 5 / readers (before/after, effect).
   - "Choices I made", `NO SOURCE`, `BLOCKED`, "Bob to fetch" (link + exactly what).
2. Scripts (one per part, each prints the files it wrote), CSVs, graphs in the folder; `tests/drivetrain_curves/` (`pytest`: L4 with a = b = c = 0 gives zero loss; C with η = 1, F0 = 0 equals Method A's wheel energy path; fits are deterministic; CdxA stays inside its range).
3. One PR to `main`: what was done, how to run, top 5 findings with numbers, `NO SOURCE` / `BLOCKED` / "Bob to fetch".

## 5. Stop conditions
- Crash or wrong number on a realistic input → **BUG** with a minimal reproducing input; keep going.
- Never edit the notebook or `src/`. Never decide an open design choice for Bob.

## Appendix B — the 10 trucks (EEA config IDs)
C0059 Fuso eCanter (7 t rigid, 1-gear IEPC) · C0091 IVECO S-eWay (40 t tractor, 1-gear IEPC) · C0371 Scania R 400E (tractor, 6-gear) · C0116 MAN eTGX (tractor, 4-gear) · C0153 Mercedes eActros 600 (4-gear) · C0218 Renault D (4x2 rigid, 2-speed E2) · C0712 Volvo FM (6x2 rigid, 12-gear) · C0206 Mercedes Econic (6x2 refuse, 2-gear) · C0070 IVECO eDaily (group 53, E3) · C0001 DAF XB (6x2 rigid, 3-gear).
