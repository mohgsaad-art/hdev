# Group 5 class numbers for Method C and L4b

16 Nov 2026. Owner: Bob. Analysis only. Branch parent: PR #37 (`drivetrain-curve-library-2026-11`, commit `13db70c`).
No other vehicle group was run. No library was built.

Data files and scripts: `docs/research/drivetrain-curve-library-2026-11/`.

## Plain answer

More data changes the evidence from 4 trucks to **254 Group 5 configs, 38 model names and 2,958 certified results**. [DATA `g5_fits.csv`; `g5_build_batch_*.csv`]

The model-weighted class middle has a **14.7 pp P10–P90 width** in the configs' mean error for both methods. Holding out a whole model gives **15.8 pp** width and an individual-model worst error of **38.0 %** for C, or **36.2 %** for L4b. [TEST `g5_class_band_summary.csv`, `g5_holdout_model_summary.csv`]

So the Group 5 class middle is numerically well defined, but the observed held-out-model band is not narrow. The numbers do not support claiming a single Group 5 class value has a narrow band.

The narrowest reliable subgroup in the in-sample cross-check is **Volvo**: 3.00 pp for C and 3.30 pp for L4b. It has 84 configs but only 3 model names. Gears also narrow the result: 12-speed gives 3.71 / 3.87 pp and 6-speed 5.41 / 5.56 pp. [TEST `g5_subgroup_widths.csv`]

The best subgroup grouping selected by that in-sample result is make. In the held-out-model test, make-specific parameters reduce the P10–P90 width only from 15.8 pp to **14.3 pp (C)** and **13.4 pp (L4b)**. It is reliable for 31 of 38 model names; 5 have fewer than 3 donor models and 2 have no donor model. [TEST `g5_holdout_model_summary.csv`, `g5_holdout_model.csv`]

| Result | C | L4b |
|---|---:|---:|
| Full-fit mean absolute error, average across configs | 1.49 % | 1.69 % |
| Full-fit worst absolute error, worst config | 6.64 % | 8.02 % |
| Class P50 cross-check, P10–P90 width of config mean error, model weighted | 14.71 pp | 14.73 pp |
| Held-out-model class P50, P10–P90 width of model mean error | 15.84 pp | 15.79 pp |
| Held-out-model class P50, largest individual-model error | 38.05 % | 36.25 % |
| Held-out-model make P50, P10–P90 width | 14.34 pp | 13.44 pp |

[TEST `g5_fits.csv`, `g5_class_band_summary.csv`, `g5_holdout_model_summary.csv`]

---

## Starting settings and scope

The run uses exactly the Part 3 settings from PR #37. [TEST scripts below]

- `P3.set_bounds()` sets the same C and L4b bounds and starts. [TEST `part3_loo.py`, `methods_lib.py`]
- `HN.AIRDRAG_MODE = "range_mid"`. Measured air-drag configs use CdxA inside their Regulation (EU) 2018/956 Annex I Part C range. Standard-value configs retain VECTO's standard CdxA. [REG `cdxa_ranges.py`; TEST `harness.py`]
- One vehicle per config: the median-mass vehicle selected by existing `harness.config_runs()`. [TEST `harness.py`; ASSUMPTION inherited from PR #37]
- C fits η_d, η_r and F0. L4b fits a, b and c. Measured-air-drag configs fit their declared CdxA too. [TEST `methods_lib.py`]
- Full fits use all certified missions except Municipal, and keep EMS, exactly as Part 3. [TEST `harness.MISSIONS_BASE`]
- This is calibration on certified VECTO results. It is not independent validation. [ASSUMPTION / terminology]

## Part 1 — Cached records and per-config fits

### Records and runtime

Nine batches of at most 30 configs built the 2,958 per-mission records. The slowest batch was 30.43 seconds. No command exceeded 10 minutes. [TEST `g5_build_records.py`; `g5_build_batch_00.csv` … `g5_build_batch_08.csv`]

| Item | Count |
|---|---:|
| Group 5 configs requested | 254 |
| Configs with usable records | 254 |
| Certified result records | 2,958 |
| Configs skipped | 0 |
| Model names | 38 |
| Makes | 7 |

[DATA `truck_configs.csv`, filter `VehicleGroup == 5`; TEST `g5_fits.csv`, `g5_skipped.csv`]

All Group 5 configs are `E-IEPC`. Gear counts: 1-speed 2, 2-speed 10, 3-speed 23, 4-speed 58, 6-speed 47, 12-speed 114. [DATA `g5_fits.csv` columns `architecture`, `gears`]

### Own fit quality and bound hits

| Method | configs fitted | mean of config MAE | median config MAE | worst in-sample config error | fits with ≥1 bound hit |
|---|---:|---:|---:|---:|---:|
| C | 254 | 1.49 % | 1.48 % | 6.64 % | 182 |
| L4b | 254 | 1.69 % | 1.68 % | 8.02 % | 189 |

[TEST `g5_fits.csv`]

C bound patterns: declared CdxA only 92, F0 only 57, F0+CdxA 30, regen+CdxA 2, regen only 1. L4b patterns: c+CdxA 118, c only 42, CdxA only 23, a+CdxA 5, a only 1. [TEST `g5_fits.csv` column `at_bound`]

A bound hit means the fitted value is constrained by the permitted range. It is not a measured physical result. [ASSUMPTION / interpretation]

## Part 2 — Group 5 class band

### Parameter bands

The **unweighted** result makes each config one observation. The **model-weighted** result first averages each model's configs and then gives each of 38 models one observation. [ASSUMPTION: model weighting was proposed by Claude and is not yet agreed by Bob]

| Method | weight | percentile | η_d | η_r | F0 (N) | a (W) | b (1/W) | c (W per m/s) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| C | config | P10 | 0.8365 | 0.7024 | 0.0 | | | |
| C | config | P50 | 0.9265 | 0.7973 | 114.3 | | | |
| C | config | P90 | 0.9679 | 0.8805 | 249.3 | | | |
| C | model | P10 | 0.8375 | 0.7459 | 0.0 | | | |
| C | model | P50 | 0.8879 | 0.8460 | 13.6 | | | |
| C | model | P90 | 0.9378 | 0.8901 | 600.8 | | | |
| L4b | config | P10 | | | | 3,545 | 2.83e-7 | 0.0 |
| L4b | config | P50 | | | | 7,344 | 3.50e-7 | 0.0 |
| L4b | config | P90 | | | | 9,093 | 5.00e-7 | 486.5 |
| L4b | model | P10 | | | | 3,190 | 2.98e-7 | 0.0 |
| L4b | model | P50 | | | | 5,258 | 4.03e-7 | 149.5 |
| L4b | model | P90 | | | | 8,623 | 5.33e-7 | 707.6 |

[TEST `g5_class_parameters.csv`]

### Applying low / middle / high to every config

Each target config uses its **own fitted CdxA**. Therefore this checks drivetrain-parameter transfer while holding the Part 1 air-drag value fixed. [ASSUMPTION requested by Bob's "as in Claude's cross-check" instruction]

| Method | weight | set | mean of config mean error | P10 | P50 | P90 | P90−P10 width | worst config mean error |
|---|---|---|---:|---:|---:|---:|---:|---:|
| C | config | P10 | +10.43 | +1.81 | +12.76 | +19.59 | 17.79 pp | 23.29 % |
| C | config | P50 | −3.26 | −10.52 | −0.93 | +4.27 | 14.79 pp | 30.23 % |
| C | config | P90 | −8.60 | −15.36 | −6.31 | −1.78 | 13.58 pp | 34.23 % |
| C | model | P10 | +8.77 | +0.43 | +11.23 | +17.65 | 17.23 pp | 21.34 % |
| C | model | **P50** | −1.81 | −8.96 | +0.57 | +5.74 | **14.71 pp** | 29.35 % |
| C | model | P90 | +1.88 | −6.31 | +4.44 | +9.82 | 16.13 pp | 26.23 % |
| L4b | config | P10 | −9.33 | −15.56 | −7.71 | −2.78 | 12.78 pp | 35.43 % |
| L4b | config | P50 | −2.83 | −9.48 | −0.92 | +4.63 | 14.11 pp | 30.46 % |
| L4b | config | P90 | +13.06 | +4.22 | +15.21 | +22.04 | 17.82 pp | 25.96 % |
| L4b | model | P10 | −9.32 | −15.58 | −7.70 | −2.76 | 12.81 pp | 35.44 % |
| L4b | model | **P50** | −0.88 | −7.90 | +1.10 | +6.83 | **14.73 pp** | 29.02 % |
| L4b | model | P90 | +17.73 | +8.27 | +19.96 | +27.22 | 18.94 pp | 31.32 % |

[TEST `g5_class_band_summary.csv`; detail by config: `g5_class_band.csv`; histogram: `g5_class_band_hist.png`]

The difference between config weighting and model weighting at P50 is small for band width: 14.79 vs 14.71 pp for C, and 14.11 vs 14.73 pp for L4b. The P50 middle shifts toward zero with model weighting. [CALC table above]

### Parameter swaps

For every target config, every other config's drivetrain values were applied, while keeping the target's CdxA. The median range from the minimum to maximum **mean** error is 47.79 pp for C and 46.92 pp for L4b. The P90 ranges are 51.76 and 51.91 pp. [TEST `g5_swap.csv`]

| Method | mean range | median range | P90 range | largest range |
|---|---:|---:|---:|---:|
| C | 46.79 pp | 47.79 pp | 51.76 pp | 54.10 pp |
| L4b | 46.07 pp | 46.92 pp | 51.91 pp | 54.41 pp |

This shows the full member-to-member spread, not the P10/P50/P90 class band. [ASSUMPTION / interpretation]

## Part 3 — What explains the spread

The table gives **model-weighted P50** parameters applied inside each subgroup. A subgroup needs at least 3 distinct model names to be labelled reliable. [ASSUMPTION: reliability threshold specified in the prompt]

| Grouping | subgroup | C configs / models | C width | L4b configs / models | L4b width | reliability |
|---|---|---:|---:|---:|---:|---|
| Architecture | IEPC | 254 / 38 | 14.71 pp | 254 / 38 | 14.73 pp | reliable |
| Gears | g12 | 114 / 5 | 3.71 pp | 114 / 5 | 3.87 pp | reliable |
| Gears | g6 | 47 / 9 | 5.41 pp | 47 / 9 | 5.56 pp | reliable |
| Gears | g4 | 58 / 16 | 9.16 pp | 58 / 16 | 8.56 pp | reliable |
| Gears | g2 | 10 / 4 | 20.67 pp | 10 / 4 | 21.71 pp | reliable |
| Gears | g3 | 23 / 6 | 37.66 pp | 23 / 6 | 36.75 pp | reliable |
| Continuous kW | 400–<500 | 176 / 15 | 11.92 pp | 176 / 15 | 11.15 pp | reliable |
| Continuous kW | 200–<300 | 11 / 7 | 16.93 pp | 11 / 7 | 17.67 pp | reliable |
| Continuous kW | 300–<400 | 62 / 20 | 31.34 pp | 62 / 20 | 31.30 pp | reliable |
| Make | Volvo | 84 / 3 | **3.00 pp** | 84 / 3 | **3.30 pp** | reliable, minimum allowed model count |
| Make | MAN | 22 / 10 | 10.32 pp | 22 / 10 | 9.56 pp | reliable |
| Make | Scania | 66 / 15 | 14.74 pp | 66 / 15 | 14.35 pp | reliable |
| Make | DAF | 23 / 6 | 37.66 pp | 23 / 6 | 36.75 pp | reliable |

[TEST `g5_subgroup_widths.csv`]

Not-reliable subgroups: g1 (2 configs, 1 model), ≥500 kW (2, 1), Iveco (2, 1), Mercedes-Benz (27, 1), Renault (30, 2). Their widths are in `g5_subgroups.csv`, but they are not evidence of a transferable subgroup band. [TEST `g5_subgroups.csv`]

The grouping with the smallest reliable observed width is make, through Volvo. The gear grouping provides the narrowest results with more than 3 model names: g12 (5) and g6 (9). [CALC table above]

Continuous-kW bins are fixed at <200, 200–<300, 300–<400, 400–<500 and ≥500 kW. [ASSUMPTION: fixed 100 kW bins chosen before inspecting errors; `g5_part3_subgroups.py`]

## Part 4 — Held-out model test

For every one of the 38 model names, all its configs were removed before fitting the model-weighted P50.
The target config retains its own fitted CdxA. The comparison is therefore for drivetrain transfer only. [ASSUMPTION requested cross-check]

The "best subgroup" is make, selected from Part 3's smallest reliable in-sample subgroup width. It uses only the other models of the target's make. [TEST `g5_part4_holdout_models.py`]

| Method | source | models tested | reliable donor sets | mean of model mean error | P10 | P50 | P90 | P90−P10 width | worst individual-model error |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C | class | 38 | 38 | −2.64 % | −10.59 % | −2.66 % | +5.25 % | 15.84 pp | 38.05 % |
| C | make subgroup | 36 | 31 | +0.27 % | −6.48 % | −0.29 % | +7.86 % | 14.34 pp | 30.05 % |
| L4b | class | 38 | 38 | −1.58 % | −9.74 % | −1.01 % | +6.05 % | 15.79 pp | 36.25 % |
| L4b | make subgroup | 36 | 31 | +0.43 % | −5.75 % | +0.03 % | +7.68 % | 13.44 pp | 27.97 % |

[TEST `g5_holdout_model_summary.csv`; per-model rows: `g5_holdout_model.csv`]

The largest held-out class errors occur on DAF XD 350 FT: C mean −11.98 %, worst 38.05 %; L4b mean −10.92 %, worst 36.25 %. Scania G0100A and G0200A also exceed 34 % worst error. [TEST `g5_holdout_model.csv`]

For the make-subgroup test, two target models have no other model of the same make and are `BLOCKED`. Five target models have fewer than 3 donor models and are `not_reliable`. [TEST `g5_holdout_model.csv`]

## Runtime and reproducibility

| Step | Result |
|---|---|
| Record build | 9 batches, 16.5–30.4 s each, 250.6 s total wall time |
| Per-config fits | 3.9–7.4 s per 30-config batch |
| Class band + 253-per-target swap | 56.6 s after fixing a CSV-schema BUG |
| Subgroups | 14.6 s |
| Held-out models | 8.2 s |

[TEST command outputs and `g5_build_batch_*.csv`]

**BUG (fixed, output-only).** The first Part 2 run completed its calculations but failed while writing `g5_class_parameters.csv`: the CSV writer took C's parameter columns as its schema and rejected L4b's `a_W`, `b_perW`, `c_W_per_mps`. `g5_part2_class_band.write()` now writes the union of row fields. No harness physics, bounds, records or fit logic changed. The rerun used the cached records and completed in 56.6 s. [TEST terminal output; `g5_part2_class_band.py`]

All record batches are compressed `.npz` caches ignored by Git. [TEST `harness.load_or_build`; folder `.gitignore`]

## Skipped configs

No Group 5 config or certified result was skipped. [TEST `g5_skipped.csv`; `g5_build_batch_*_skipped.csv`]

## How to run

```bash
cd docs/research/drivetrain-curve-library-2026-11
# First create the v2 harness/VECTO worktrees if they do not exist.
bash setup_v2_worktree.sh
# Cached batches (0 through 8), then full fits.
for i in {0..8}; do python g5_build_records.py "$i"; done
for i in {0..8}; do python g5_part1_fits.py "$i"; done
python g5_part1_fits.py combine
python g5_part2_class_band.py
python g5_part3_subgroups.py
python g5_part4_holdout_models.py
```

## Assumptions

- [ASSUMPTION] Model-weighted class parameters: average a model's configs before calculating P10/P50/P90. The unweighted result is also reported.
- [ASSUMPTION] One median-mass vehicle represents each exact config, inherited unchanged from PR #37.
- [ASSUMPTION] Applying a class/subgroup drivetrain set with each target's own fitted CdxA isolates drivetrain transfer. It does not test the CdxA range uncertainty.
- [ASSUMPTION] Continuous-power bins are fixed 100 kW bands as listed in Part 3.
- [ASSUMPTION] Three distinct model names is the reliability threshold, as set in the prompt.
- [ASSUMPTION] `a`, `b`, `c`, η and F0 are fitted effective values. They are not direct measurements of components.

## Open items

- [OPEN] 182 C fits and 189 L4b fits hit at least one bound. The transfer results include the effect of these constrained fits.
- [OPEN] Group 5 has only E-IEPC. Architecture cannot explain its within-group spread in this sample.
- [OPEN] Make is the narrowest in-sample subgroup because of Volvo, but it has exactly 3 models. The held-out make test remains 13.4–14.3 pp wide.
- [OPEN] CdxA is held at each target's fitted value in Parts 2–4. A future test could propagate CdxA ranges separately.
