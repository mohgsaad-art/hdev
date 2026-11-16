# VECTO-map shape x one scale, a physics-free baseline, and the DAF cause

16 Nov 2026. Owner: Bob. Branch `shape-direct-daf-2026-11`, from `group5-class-numbers-2026-11` (PR #38, head c80200b).
Folder: `docs/research/drivetrain-shape-direct-daf-2026-11/`. Analysis only; no notebook, `src/` or harness edit. Settings as PR #37/#38: `P3.set_bounds()`, `HN.AIRDRAG_MODE = "range_mid"`, 254 group 5 configs, 2,958 certified results, batches of 30, every command under 10 minutes.

Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA. [DATA]

Terms. **Width** = P90 minus P10 of the held-out models' mean errors (PR #38 definition, one value per model). **Held-out model** = all configs of one model name removed from the donors; the class P50 of the other models is applied with the target's own fitted CdxA, as in PR #38 Part 4 (the "own" rule). **Worst model** = largest absolute model mean error. **Worst result** = largest single-result error. Every method is calibrated on certified VECTO results; this is not independent validation. [ASSUMPTION / terminology]

---

# Tables

## Table 1. Group 5, C, L4b and shape x scale (Part 2.3). [TEST `p2_g5_summary.csv`, `final_bootstrap.csv`]

L1 = drive losses shape x s and regen losses same shape x same s. L1b = separate s_drive and s_regen. Shape S3b = VECTO GenericIEPC 3-speed, S3a = GenericIEPC 1-speed, S2 PSM / ASM = bus-generic IEPC normalised map de-normalised the VECTO way (`GenericBusIEPCData.cs`). `arch` = the PR #37 rule (wheel-motor IEPC -> S3c, one gear -> S3a, more gears -> S3b). Every L1/L1b fit also fits the declared CdxA inside its range where air drag was measured, like C and L4b.
Headline shape for L1/L1b: **S3b** (see "Choices I made"). All other shapes are shown; none was selected by its error.

| method | fitted values | in-sample mean abs err % | in-sample worst % | class-P50 config width pp | held-out mean % | P10 % | P50 % | P90 % | **P90-P10 pp** | 95 % interval of width (bootstrap over models) | worst model mean abs err % | worst single result % | results too low |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 3 | 1.49 | 6.6 | 14.7 | -2.64 | -10.6 | -2.7 | +5.3 | 15.8 | 11.6 to 19.7 | 27.0 | 38.0 | 49 % |
| L4b | 3 | 1.69 | 7.8 | 14.7 | -1.58 | -9.7 | -1.0 | +6.1 | 15.8 | 11.3 to 20.0 | 26.2 | 36.2 | 45 % |
| L1[S3b_IEPC_3speed] | 1 | 2.73 | 17.9 | 15.2 | +0.41 | -8.6 | +0.2 | +8.4 | 17.0 | 11.0 to 21.1 | 24.8 | 34.5 | 32 % |
| L1b[S3b_IEPC_3speed] | 2 | 1.86 | 11.9 | 15.9 | -0.40 | -10.1 | -0.8 | +8.6 | 18.7 | 12.3 to 21.5 | 26.0 | 35.9 | 35 % |
| L1[arch] | 1 | 2.78 | 17.9 | 15.4 | +1.47 | -8.6 | +0.2 | +10.6 | 19.2 | 11.6 to 32.3 | 35.9 | 66.5 | 31 % |
| L1b[arch] | 2 | 1.86 | 11.9 | 17.1 | +0.57 | -10.1 | -0.8 | +10.8 | 20.9 | 13.0 to 31.6 | 32.8 | 64.3 | 33 % |
| L1[S3a_IEPC_1speed] | 1 | 3.15 | 15.7 | 14.4 | +0.81 | -9.0 | +0.2 | +9.7 | 18.7 | 11.5 to 22.6 | 24.9 | 35.3 | 30 % |
| L1b[S3a_IEPC_1speed] | 2 | 2.03 | 11.0 | 15.1 | -0.59 | -10.3 | -0.9 | +8.1 | 18.4 | 11.4 to 22.2 | 26.1 | 35.4 | 35 % |
| L1[S2_busIEPC_PSM] | 1 | 3.29 | 16.1 | 14.3 | +0.88 | -8.8 | +0.2 | +9.6 | 18.4 | 11.1 to 22.2 | 24.8 | 35.6 | 29 % |
| L1b[S2_busIEPC_PSM] | 2 | 2.02 | 10.5 | 15.1 | -0.65 | -10.2 | -1.0 | +7.9 | 18.0 | 11.1 to 21.9 | 26.0 | 35.4 | 35 % |
| L1[S2_busIEPC_ASM] | 1 | 2.63 | 19.1 | 15.3 | +0.46 | -7.9 | +0.2 | +8.5 | 16.3 | 10.5 to 19.7 | 24.5 | 34.9 | 32 % |
| L1b[S2_busIEPC_ASM] | 2 | 1.79 | 13.6 | 15.5 | -0.23 | -9.8 | -0.5 | +8.8 | 18.6 | 13.1 to 21.8 | 26.1 | 36.5 | 33 % |

The 95 % interval comes from 5,000 bootstrap resamples of the 38 models (seed 20261116). A width from 38 models carries about +-4 pp of sampling noise.

Paired differences of width against C (same resamples) [TEST `final_bootstrap.csv`]:

| models | comparison | width difference pp | 95 % interval |
|---|---:|---:|---:|
| all 38 models | B0 median of all other models **minus** C [CdxA own] | +14.3 | +9.3 to +18.9 |
| all 38 models | B1 median of 3 nearest models (mass, kW) **minus** C [CdxA own] | +7.9 | -1.0 to +21.3 |
| all 38 models | B1 median of 5 nearest models (mass, kW) **minus** C [CdxA own] | +10.9 | +1.7 to +23.4 |
| all 38 models | L1[S2_busIEPC_ASM] [CdxA own] **minus** C [CdxA own] | +0.5 | -2.0 to +2.9 |
| all 38 models | L1[S2_busIEPC_PSM] [CdxA own] **minus** C [CdxA own] | +2.6 | -1.6 to +5.7 |
| all 38 models | L1[S3a_IEPC_1speed] [CdxA own] **minus** C [CdxA own] | +2.9 | -1.2 to +6.0 |
| all 38 models | L1[S3b_IEPC_3speed] [CdxA own] **minus** C [CdxA own] | +1.2 | -1.7 to +4.7 |
| all 38 models | L1b[S3b_IEPC_3speed] [CdxA own] **minus** C [CdxA own] | +2.9 | -0.2 to +5.6 |
| all 38 models | L4b [CdxA own] **minus** C [CdxA own] | -0.1 | -0.7 to +0.7 |
| all 38 models | class-P50 L1[S3b_IEPC_3speed] (CdxA mid) **minus** C [CdxA own] | +1.9 | -1.3 to +4.8 |
| all 38 models | class-P50 L1b[S3b_IEPC_3speed] (CdxA mid) **minus** C [CdxA own] | +2.2 | -0.7 to +5.1 |
| without DAF (32 models) | class-P50 L1[S3b_IEPC_3speed] (CdxA mid) **minus** class-P50 C [CdxA own] | -0.9 | -3.4 to +2.9 |
| without DAF (32 models) | class-P50 L1[S3b_IEPC_3speed] [CdxA own] **minus** class-P50 C [CdxA own] | -1.5 | -4.0 to +2.7 |
| without DAF (32 models) | class-P50 L1b[S3b_IEPC_3speed] (CdxA mid) **minus** class-P50 C [CdxA own] | -0.7 | -3.0 to +2.8 |
| without DAF (32 models) | class-P50 L1b[S3b_IEPC_3speed] [CdxA own] **minus** class-P50 C [CdxA own] | -0.0 | -2.3 to +3.4 |
| without DAF (32 models) | class-P50 L4b [CdxA own] **minus** class-P50 C [CdxA own] | -1.2 | -1.5 to +0.0 |

## Table 2. Without DAF (Part 1.4 and the same for L1). [TEST `p1_without_daf.csv`, `p2_g5_summary_without_daf.csv`]

PR #38 numbers reproduced in row A. B removes DAF from donors and targets (231 configs, 32 models). C removes DAF from the donors only and still evaluates DAF.

| method | case | configs | models | class-band width pp (P90-P10 of config mean error) | held-out-model width pp | worst model mean abs err % | worst single result % |
|---|---:|---:|---:|---:|---:|---:|---:|
| C | A all configs | 254 | 38 | 14.71 | 15.84 | 27.0 | 38.0 |
| C | B DAF removed (donors and targets) | 231 | 32 | 13.05 | 15.51 | 11.9 | 23.8 |
| C | C DAF removed from donors, DAF still evaluated | 254 | 38 | 14.59 | 17.16 | 27.2 | 38.2 |
| L4b | A all configs | 254 | 38 | 14.73 | 15.79 | 26.2 | 36.2 |
| L4b | B DAF removed (donors and targets) | 231 | 32 | 12.71 | 14.27 | 11.4 | 22.5 |
| L4b | C DAF removed from donors, DAF still evaluated | 254 | 38 | 14.53 | 16.23 | 26.8 | 36.8 |

Same split for the shape methods (case B):

| method | class-P50 width, all 254 configs | without DAF (231) | held-out width, 38 models | without DAF (32 models) | worst model mean abs err %, all | without DAF | worst single result %, all | without DAF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 14.7 | 13.0 | 15.8 | 15.5 | 27.0 | 11.9 | 38.0 | 23.8 |
| L4b | 14.7 | 12.7 | 15.8 | 14.3 | 26.2 | 11.4 | 36.2 | 22.5 |
| L1[S3b_IEPC_3speed] | 15.2 | 13.4 | 17.0 | 14.0 | 24.8 | 11.0 | 34.5 | 24.2 |
| L1b[S3b_IEPC_3speed] | 15.9 | 14.4 | 18.7 | 15.5 | 26.0 | 11.8 | 35.9 | 24.3 |
| L1[arch] | 15.4 | 20.5 | 19.2 | 14.6 | 35.9 | 33.1 | 66.5 | 61.6 |
| L1[S3a_IEPC_1speed] | 14.4 | 13.3 | 18.7 | 14.2 | 24.9 | 12.8 | 35.3 | 26.7 |
| L1[S2_busIEPC_PSM] | 14.3 | 13.1 | 18.4 | 14.0 | 24.8 | 12.9 | 35.6 | 27.1 |
| L1[S2_busIEPC_ASM] | 15.3 | 13.1 | 16.3 | 13.5 | 24.5 | 10.9 | 34.9 | 23.4 |

## Table 3. Physics-free baselines against class-P50 physics, held-out models (Part 3). [TEST `p3_summary.csv`, `p3_pairwise.csv`]

B0 = median of the certified kWh/km of all other models at the same mission and payload. B1 = median of the k nearest other models by test mass and rated kW (k = 5 headline, k = 3 shown; z-scored Euclidean distance; test mass = TotalVehicleMass at Regional Delivery 12,900 kg). "CdxA of the target": PR #38 gives the held-out truck its own fitted CdxA, which uses that truck's certified results. A truly unseen truck has only its published range, so the "middle of range" rows are the fair comparison with B0 and B1.

| models | method | CdxA of the target | **P90-P10 pp** | 95 % interval | mean of model mean err % | worst model mean abs err % | worst single result % | results too low |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all 38 | B0 median of all other models | n/a | 30.2 | 25.0 to 34.5 | +1.7 | 25.4 | 33.1 | 43 % |
| all 38 | B1 median of 5 nearest models (mass, kW) | n/a | 26.8 | 17.4 to 38.7 | +0.9 | 29.3 | 52.8 | 39 % |
| all 38 | B1 median of 3 nearest models (mass, kW) | n/a | 23.7 | 15.0 to 37.4 | +0.2 | 25.1 | 52.8 | 38 % |
| all 38 | class-P50 C | own fitted CdxA (PR #38) | 15.8 | 11.6 to 19.7 | -2.6 | 27.0 | 38.0 | 49 % |
| all 38 | class-P50 C | middle of published range | 15.7 | 11.4 to 19.3 | -3.0 | 27.5 | 38.7 | 52 % |
| all 38 | class-P50 L1[S3b_IEPC_3speed] | own fitted CdxA (PR #38) | 17.0 | 11.0 to 21.1 | +0.4 | 24.8 | 34.5 | 32 % |
| all 38 | class-P50 L1[S3b_IEPC_3speed] | middle of published range | 17.7 | 11.3 to 21.0 | +0.6 | 25.3 | 35.2 | 31 % |
| no DAF (32) | B0 median of all other models | n/a | 31.9 | 24.5 to 34.6 | +3.2 | 27.1 | 42.9 | 42 % |
| no DAF (32) | B1 median of 5 nearest models (mass, kW) | n/a | 24.9 | 16.3 to 37.3 | +0.2 | 25.1 | 52.8 | 38 % |
| no DAF (32) | B1 median of 3 nearest models (mass, kW) | n/a | 24.8 | 13.8 to 37.1 | -0.0 | 25.1 | 52.8 | 37 % |
| no DAF (32) | class-P50 C | own fitted CdxA (PR #38) | 15.5 | 11.0 to 19.3 | -1.6 | 11.9 | 23.8 | 48 % |
| no DAF (32) | class-P50 C | middle of published range | 14.9 | 10.7 to 18.7 | -1.9 | 11.9 | 23.8 | 51 % |
| no DAF (32) | class-P50 L1[S3b_IEPC_3speed] | own fitted CdxA (PR #38) | 14.0 | 9.3 to 19.0 | +0.7 | 11.0 | 24.2 | 35 % |
| no DAF (32) | class-P50 L1[S3b_IEPC_3speed] | middle of published range | 14.6 | 9.8 to 19.4 | +0.9 | 11.7 | 24.2 | 34 % |

Model-by-model (absolute model mean error), physics with the CdxA range middle [TEST `p3_pairwise.csv`]:

| models | physics | baseline | physics median abs model err % | baseline median | physics mean abs model err % | baseline mean | physics closer on |
|---|---:|---:|---:|---:|---:|---:|---:|
| all 38 models | C (CdxA mid) | B0 median of all other models | 4.74 | 10.65 | 5.66 | 10.27 | 29 / 38 |
| all 38 models | C (CdxA mid) | B1 median of 3 nearest models (mass, kW) | 4.74 | 4.17 | 5.66 | 7.26 | 18 / 38 |
| all 38 models | C (CdxA mid) | B1 median of 5 nearest models (mass, kW) | 4.74 | 5.48 | 5.66 | 8.06 | 16 / 38 |
| all 38 models | L1[S3b_IEPC_3speed] (CdxA mid) | B0 median of all other models | 4.87 | 10.65 | 5.74 | 10.27 | 28 / 38 |
| all 38 models | L1[S3b_IEPC_3speed] (CdxA mid) | B1 median of 3 nearest models (mass, kW) | 4.87 | 4.17 | 5.74 | 7.26 | 20 / 38 |
| all 38 models | L1[S3b_IEPC_3speed] (CdxA mid) | B1 median of 5 nearest models (mass, kW) | 4.87 | 5.48 | 5.74 | 8.06 | 23 / 38 |
| without DAF (32 models) | C (CdxA mid) | B0 median of all other models | 5.31 | 10.56 | 5.24 | 10.7 | 26 / 32 |
| without DAF (32 models) | C (CdxA mid) | B1 median of 3 nearest models (mass, kW) | 5.31 | 3.74 | 5.24 | 7.18 | 15 / 32 |
| without DAF (32 models) | C (CdxA mid) | B1 median of 5 nearest models (mass, kW) | 5.31 | 7.02 | 5.24 | 7.82 | 16 / 32 |
| without DAF (32 models) | L1[S3b_IEPC_3speed] (CdxA mid) | B0 median of all other models | 3.77 | 10.56 | 5.04 | 10.7 | 26 / 32 |
| without DAF (32 models) | L1[S3b_IEPC_3speed] (CdxA mid) | B1 median of 3 nearest models (mass, kW) | 3.77 | 3.74 | 5.04 | 7.18 | 17 / 32 |
| without DAF (32 models) | L1[S3b_IEPC_3speed] (CdxA mid) | B1 median of 5 nearest models (mass, kW) | 3.77 | 7.02 | 5.04 | 7.82 | 19 / 32 |

## Table 4. The 10 trucks of Appendix B, leave-one-result-out (Part 2.4). [TEST `p2_ten_summary.csv`]

Same 88 certified results, same fits and same definitions as PR #37 Part 3 (C and L4b reproduce PR #37 exactly: 5 and 4 trucks within 5 %, worst 12.7 % and 14.2 %).

| method (leave-one-result-out) | fitted values | trucks all within 5 % | predictions within 5 % | too low | largest under % | largest over % | median abs err % | worst truck % | median of truck worst % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 3 | 5 | 86 % | 51 % | -12.0 | +12.7 | 1.23 | 12.7 | 5.3 |
| L4b | 3 | 4 | 89 % | 47 % | -14.2 | +12.5 | 1.33 | 14.2 | 5.3 |
| L1[arch] | 1 | 4 | 81 % | 48 % | -19.6 | +16.4 | 2.23 | 19.6 | 6.4 |
| L1b[arch] | 2 | 4 | 88 % | 55 % | -16.0 | +13.3 | 1.78 | 16.0 | 6.7 |
| L1[S3a_IEPC_1speed] | 1 | 4 | 84 % | 44 % | -19.6 | +15.7 | 2.23 | 19.6 | 7.6 |
| L1b[S3a_IEPC_1speed] | 2 | 4 | 86 % | 56 % | -16.0 | +13.3 | 1.89 | 16.0 | 7.0 |
| L1[S3b_IEPC_3speed] | 1 | 4 | 85 % | 49 % | -19.8 | +16.7 | 2.05 | 19.8 | 6.3 |
| L1b[S3b_IEPC_3speed] | 2 | 4 | 88 % | 55 % | -14.9 | +13.3 | 1.64 | 14.9 | 6.7 |
| L1[S2_busIEPC_PSM] | 1 | 4 | 81 % | 44 % | -19.5 | +15.1 | 2.12 | 19.5 | 8.3 |
| L1b[S2_busIEPC_PSM] | 2 | 4 | 86 % | 56 % | -16.3 | +12.9 | 1.98 | 16.3 | 7.3 |
| L1[S2_busIEPC_ASM] | 1 | 3 | 84 % | 50 % | -18.1 | +15.9 | 1.81 | 18.1 | 6.9 |
| L1b[S2_busIEPC_ASM] | 2 | 4 | 86 % | 51 % | -13.3 | +12.2 | 1.38 | 13.3 | 6.8 |

## Table 5. Which shape fits which group 5 make (Part 2.5). [TEST `final_by_make_best_shape.csv`]

Post hoc and per make, not per truck. [ASSUMPTION: any choice of VECTO shape for a truck is a hypothesis.] The held-out figure is the mean over the make's models of |model mean error|.

| make | method | models | configs | in-sample MAE % S3a | S3b | S2 PSM | S2 ASM | lowest in-sample | held-out mean abs model err % S3a | S3b | S2 PSM | S2 ASM | lowest held-out |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DAF | L1 | 6 | 23 | 4.28 | 4.71 | 4.17 | 4.74 | S2_busIEPC_PSM | 9.6 | 9.5 | 9.4 | 9.2 | S2_busIEPC_ASM |
| DAF | L1b | 6 | 23 | 2.59 | 2.74 | 2.50 | 2.88 | S2_busIEPC_PSM | 10.2 | 10.3 | 10.0 | 10.5 | S2_busIEPC_PSM |
| Iveco | L1 | 1 | 2 | 1.57 | 2.02 | 1.53 | 2.43 | S2_busIEPC_PSM | 15.2 | 12.0 | 15.3 | 9.8 | S2_busIEPC_ASM |
| Iveco | L1b | 1 | 2 | 1.35 | 1.26 | 1.32 | 1.28 | S3b_IEPC_3speed | 12.0 | 10.7 | 11.7 | 9.4 | S2_busIEPC_ASM |
| MAN | L1 | 10 | 22 | 2.19 | 1.88 | 2.34 | 1.87 | S2_busIEPC_ASM | 6.0 | 5.6 | 5.8 | 5.5 | S2_busIEPC_ASM |
| MAN | L1b | 10 | 22 | 1.97 | 1.78 | 1.96 | 1.71 | S2_busIEPC_ASM | 5.4 | 5.7 | 5.3 | 6.1 | S2_busIEPC_PSM |
| Mercedes-Benz | L1 | 1 | 27 | 3.15 | 2.77 | 3.23 | 2.61 | S2_busIEPC_ASM | 9.1 | 7.3 | 9.0 | 6.3 | S2_busIEPC_ASM |
| Mercedes-Benz | L1b | 1 | 27 | 2.32 | 2.09 | 2.31 | 1.94 | S2_busIEPC_ASM | 7.3 | 6.9 | 7.0 | 6.6 | S2_busIEPC_ASM |
| Renault | L1 | 2 | 30 | 3.75 | 3.07 | 3.94 | 2.87 | S2_busIEPC_ASM | 4.3 | 3.1 | 4.2 | 2.6 | S2_busIEPC_ASM |
| Renault | L1b | 2 | 30 | 1.97 | 1.80 | 1.94 | 1.69 | S2_busIEPC_ASM | 3.1 | 3.3 | 2.8 | 3.4 | S2_busIEPC_PSM |
| Scania | L1 | 15 | 66 | 2.13 | 1.80 | 2.29 | 1.71 | S2_busIEPC_ASM | 4.1 | 4.1 | 3.8 | 3.8 | S2_busIEPC_PSM |
| Scania | L1b | 15 | 66 | 2.05 | 1.76 | 2.12 | 1.65 | S2_busIEPC_ASM | 4.8 | 5.2 | 4.7 | 5.4 | S2_busIEPC_PSM |
| Volvo | L1 | 3 | 84 | 3.70 | 3.04 | 3.90 | 2.90 | S2_busIEPC_ASM | 4.9 | 3.8 | 4.8 | 3.4 | S2_busIEPC_ASM |
| Volvo | L1b | 3 | 84 | 1.82 | 1.69 | 1.79 | 1.62 | S2_busIEPC_ASM | 3.8 | 4.0 | 3.5 | 4.3 | S2_busIEPC_PSM |

## Shapes used: efficiency against load fraction, from VECTO's own maps (Part 2.1) [TEST `p2_shape_scatter_per_bin.csv`, `partA_shapes.csv`]

Method (KIT way, VECTO maps): the VECTO generic truck is driven over the five VECTO declaration cycles, two loadings, with the notebook driver and force engine; every 1 s wheel-power row goes through `drivetrain` (Appendix A) with the VECTO map of each chain. x = |P_wheel| / P_rated of the chain (S3a and S2: 315.3 kW, S3b: 318.5 kW). Bin edges: 0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.80, 1.0, 1.5. Fine bins at low load because efficiency changes fastest there and the trucks spend most of their time there; the share of wheel energy per bin is printed so a reader sees which bins matter. Efficiency per bin = wheel energy / electric energy (drive) or electric / wheel energy (regen), energy-weighted. The bracket is the P10-P90 of the 1 s row efficiencies in the bin (the scatter). The re-run of `partA_shapes.py` in this session gives files identical to PR #37's. The shapes come from one generic vehicle on the declaration cycles, so a bin's share of energy is not the share of any group 5 truck.

Drive:

| x = abs(P_wheel) / P_rated | S3a GenericIEPC 1-speed: eta (P10-P90 of 1 s rows) | % of wheel energy | S3b GenericIEPC 3-speed: eta (P10-P90 of 1 s rows) | % of wheel energy | S2 bus IEPC PSM: eta (P10-P90 of 1 s rows) | % of wheel energy | S2 bus IEPC ASM: eta (P10-P90 of 1 s rows) | % of wheel energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0-0.01 | 0.390 (0.13-0.78) | 0.3 | 0.555 (0.23-0.87) | 0.3 | 0.266 (0.08-0.63) | 0.3 | 0.367 (0.14-0.60) | 0.3 |
| 0.01-0.02 | 0.494 (0.25-0.81) | 0.6 | 0.626 (0.42-0.80) | 0.6 | 0.335 (0.15-0.73) | 0.6 | 0.456 (0.28-0.74) | 0.6 |
| 0.02-0.03 | 0.518 (0.29-0.79) | 0.6 | 0.656 (0.47-0.82) | 0.6 | 0.367 (0.16-0.76) | 0.6 | 0.540 (0.33-0.74) | 0.6 |
| 0.03-0.04 | 0.585 (0.34-0.84) | 0.9 | 0.711 (0.54-0.84) | 0.9 | 0.444 (0.21-0.81) | 0.9 | 0.605 (0.40-0.74) | 0.9 |
| 0.04-0.06 | 0.607 (0.40-0.84) | 2.4 | 0.741 (0.59-0.86) | 2.4 | 0.473 (0.25-0.81) | 2.4 | 0.640 (0.47-0.77) | 2.4 |
| 0.06-0.08 | 0.634 (0.46-0.84) | 2.9 | 0.763 (0.65-0.85) | 2.9 | 0.513 (0.31-0.81) | 2.9 | 0.684 (0.56-0.78) | 2.9 |
| 0.08-0.1 | 0.644 (0.51-0.86) | 3.4 | 0.771 (0.68-0.86) | 3.5 | 0.532 (0.36-0.82) | 3.4 | 0.713 (0.63-0.79) | 3.4 |
| 0.1-0.125 | 0.637 (0.54-0.83) | 6.7 | 0.774 (0.72-0.86) | 6.8 | 0.535 (0.41-0.80) | 6.7 | 0.741 (0.69-0.80) | 6.7 |
| 0.125-0.15 | 0.637 (0.58-0.82) | 10.2 | 0.782 (0.75-0.86) | 10.5 | 0.535 (0.46-0.79) | 10.2 | 0.773 (0.74-0.81) | 10.2 |
| 0.15-0.2 | 0.663 (0.61-0.82) | 23.0 | 0.799 (0.77-0.86) | 23.4 | 0.548 (0.48-0.79) | 23.0 | 0.780 (0.76-0.81) | 23.0 |
| 0.2-0.25 | 0.717 (0.65-0.84) | 16.9 | 0.827 (0.79-0.87) | 16.6 | 0.600 (0.52-0.80) | 16.9 | 0.767 (0.74-0.80) | 16.9 |
| 0.25-0.3 | 0.756 (0.68-0.83) | 11.9 | 0.846 (0.82-0.87) | 11.8 | 0.642 (0.54-0.81) | 11.9 | 0.763 (0.73-0.81) | 11.9 |
| 0.3-0.4 | 0.780 (0.72-0.84) | 13.2 | 0.857 (0.83-0.88) | 12.9 | 0.671 (0.57-0.81) | 13.2 | 0.765 (0.72-0.81) | 13.2 |
| 0.4-0.5 | 0.793 (0.75-0.84) | 4.6 | 0.863 (0.85-0.88) | 4.4 | 0.691 (0.59-0.81) | 4.6 | 0.767 (0.71-0.81) | 4.6 |
| 0.5-0.6 | 0.803 (0.77-0.84) | 1.8 | 0.867 (0.86-0.88) | 1.7 | 0.738 (0.65-0.81) | 1.8 | 0.795 (0.75-0.82) | 1.8 |
| 0.6-0.8 | 0.805 (0.79-0.85) | 0.7 | 0.868 (0.86-0.88) | 0.6 | 0.756 (0.73-0.80) | 0.7 | 0.824 (0.81-0.84) | 0.7 |
| 0.8-1 | 0.819 (0.81-0.82) | 0.1 | 0.873 (0.87-0.87) | 0.1 | 0.735 (0.73-0.74) | 0.1 | 0.804 (0.79-0.82) | 0.1 |

Regeneration (a negative efficiency means the drivetrain draws electric power while the wheel recovers a little energy; this happens in the lowest bins):

| x = abs(P_wheel) / P_rated | S3a GenericIEPC 1-speed: eta (P10-P90 of 1 s rows) | % of wheel energy | S3b GenericIEPC 3-speed: eta (P10-P90 of 1 s rows) | % of wheel energy | S2 bus IEPC PSM: eta (P10-P90 of 1 s rows) | % of wheel energy | S2 bus IEPC ASM: eta (P10-P90 of 1 s rows) | % of wheel energy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0-0.01 | -3.580 (-25.24-0.28) | 0.3 | -1.366 (-12.02-0.50) | 0.3 | -6.163 (-42.29--0.05) | 0.3 | -3.000 (-23.38-0.09) | 0.3 |
| 0.01-0.02 | -0.489 (-2.18-0.69) | 0.6 | 0.149 (-0.73-0.76) | 0.7 | -1.023 (-3.94-0.52) | 0.6 | -0.296 (-2.06-0.59) | 0.6 |
| 0.02-0.03 | 0.241 (-0.87-0.96) | 1.1 | 0.488 (-0.12-0.83) | 1.2 | 0.048 (-1.62-0.86) | 1.1 | 0.268 (-0.81-0.72) | 1.1 |
| 0.03-0.04 | 0.478 (-0.22-0.93) | 1.5 | 0.614 (0.16-0.86) | 1.5 | 0.407 (-0.49-0.92) | 1.5 | 0.469 (-0.19-0.83) | 1.5 |
| 0.04-0.06 | 0.608 (0.06-0.93) | 3.9 | 0.701 (0.34-0.89) | 4.0 | 0.576 (0.05-0.92) | 3.9 | 0.596 (0.08-0.86) | 3.9 |
| 0.06-0.08 | 0.689 (0.24-0.93) | 4.1 | 0.765 (0.51-0.90) | 4.1 | 0.636 (0.22-0.89) | 4.1 | 0.677 (0.31-0.88) | 4.1 |
| 0.08-0.1 | 0.738 (0.34-0.94) | 4.5 | 0.808 (0.61-0.90) | 4.6 | 0.677 (0.31-0.89) | 4.5 | 0.722 (0.42-0.88) | 4.5 |
| 0.1-0.125 | 0.742 (0.36-0.93) | 7.7 | 0.816 (0.64-0.90) | 7.9 | 0.695 (0.34-0.89) | 7.7 | 0.726 (0.46-0.86) | 7.7 |
| 0.125-0.15 | 0.781 (0.46-0.92) | 9.0 | 0.844 (0.73-0.90) | 9.1 | 0.721 (0.40-0.88) | 9.0 | 0.757 (0.55-0.86) | 9.0 |
| 0.15-0.2 | 0.830 (0.63-0.92) | 19.0 | 0.868 (0.80-0.90) | 19.2 | 0.756 (0.50-0.86) | 19.0 | 0.804 (0.68-0.87) | 19.0 |
| 0.2-0.25 | 0.840 (0.72-0.91) | 18.4 | 0.877 (0.83-0.90) | 18.6 | 0.777 (0.58-0.86) | 18.4 | 0.821 (0.73-0.87) | 18.4 |
| 0.25-0.3 | 0.868 (0.81-0.91) | 12.7 | 0.887 (0.87-0.90) | 12.3 | 0.815 (0.75-0.86) | 12.7 | 0.846 (0.81-0.87) | 12.7 |
| 0.3-0.4 | 0.870 (0.83-0.90) | 13.1 | 0.888 (0.87-0.90) | 12.9 | 0.815 (0.77-0.85) | 13.1 | 0.847 (0.82-0.87) | 13.1 |
| 0.4-0.5 | 0.873 (0.84-0.90) | 3.0 | 0.893 (0.88-0.90) | 2.9 | 0.819 (0.77-0.85) | 3.0 | 0.843 (0.82-0.86) | 3.0 |
| 0.5-0.6 | 0.863 (0.80-0.90) | 0.7 | 0.887 (0.87-0.90) | 0.7 | 0.803 (0.73-0.84) | 0.7 | 0.838 (0.82-0.85) | 0.7 |
| 0.6-0.8 | 0.868 (0.83-0.90) | 0.3 | 0.891 (0.88-0.90) | 0.3 | 0.798 (0.74-0.83) | 0.3 | 0.826 (0.80-0.84) | 0.3 |

---

# Cause of the DAF split (Part 1)

## 1. Re-check of the 16 Nov statements about PR #38 [TEST `p0_recheck_claims.csv`]

| Statement | Result of this run |
|---|---|
| 201 BEV group 5 configs are `E-IEPC`, 26 blank | **Not reproduced.** The harness has 254 group 5 configs: 227 `E-IEPC` and 27 `E-IEPC-wheel` (wheel-motor design, 27 Mercedes-Benz configs). In the join file the group 5 ZEV vehicles are 1,826 `E-IEPC` and 1,192 blank. The conclusion "architecture cannot split group 5" holds for `E-IEPC` vs others; the wheel-motor flag is one split the PR #38 report did not use. |
| 12-gear = Volvo 84 + Renault 30; 3-gear = DAF only | Holds (DAF g3 x 23, Renault g12 x 30, Volvo g12 x 84). |
| C drivetrain value at a bound 90/254; L4b 166/254; F0 = 0 on 87; c = 0 on 160 | Holds (90, 166, 87, 160). |
| CdxA at the upper edge on 124 C fits; lower edge on 121 of 146 L4b fits | Holds. 121 of the L4b fits are at the lower edge and 25 at the upper edge (146 at an edge of 184 measured configs). |
| Held-out class P50 width about 16 pp, worst model 36-38 % | Holds (15.84 / 15.79 pp; worst single result 38.0 / 36.2 %). |
| Four worst held-out models are all DAF (G0200A -27, G0100A -12, XD 350 -12, XF 350 -9) | **Partly.** By mean error the three worst are DAF (G0200A -27.0, XD 350 FT -12.0, G0100A -11.7); the 4th is Scania G 230E A4x2NB (-10.9), the 5th Scania P 230E A4x2NB (-10.5); DAF XF 350 FT is 6th (-9.0). By worst single result the five largest are all DAF (38.0, 35.6, 35.1, 34.3, 24.6 %). |
| Dropping fits with a drivetrain bound hit does not narrow the width (15.6 / 15.5 pp) | The result "does not narrow" holds. Numbers differ: bound-hit fits removed from the donors only: **15.7 pp (C), 16.0 pp (L4b)**. Removed from donors and targets: 34.6 pp (C, 20 models left) and 20.3 pp (L4b, 25 models left); too few models to read. |
| DAF C fits fall in two groups: F0 about 1,600 N with eta_d 0.87-0.89, or F0 = 0 with eta_d about 0.92 | Holds for 8 configs (F0 1,370-1,675 N, eta_d 0.87-0.89) and 11 configs (F0 = 0, eta_d 0.91-0.93). Four DAF configs sit between: C0007 (944 N, eta_d 0.77), C0033 (575 N, 0.80), C0055 (388 N, 0.79), C0047 (261 N, 0.75). |

## 2. Inputs per config and mission next to VECTO (Part 1.1) [DATA / VECTO]

Full per-mission table: `p1_daf_inputs_per_mission.csv` (one row per certified result: mission, cycle file, payload, test mass, trailer codes, delta CdxA, CdxA range with trailer delta, CdxA start and both fitted values, total rolling-resistance coefficient, wheel reduced mass, r_dyn, ES / PS / HVAC / condenser watts, aux share of the certified energy, axle shares, gears, rated kW, axle ratio, harness E_A and wheel energy). Per config: `p1_daf_inputs_per_config.csv`. VECTO file and line for each input: `p1_daf_vecto_refs.csv` (every line was found by reading the fork: `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`, version 4.3.4).

Per-config summary of the 23 DAF configs:

| config | model | F0 cluster | IEPC rated, gears, lowest total ratio | axle gear ratio (EEA) | tyres, specific RRC, twin | CdxA range [lo-hi) m2 -> C fit m2 | test mass Regional 12,900 kg | VECTO version | results |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0004 | G0100A | HIGH | 366.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00400 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.75 | 31033.0 | 4.2.5 | 12 |
| C0005 | G0100A | LOW | 361.0 kW, g3, r7.71900 | 2.38 | a2 315/70  0.00400 twin true; a1 385/55  0.00400 twin false | A12 [4.88-5.12) -> 5.03 | 31253.0 | 4.2.7 | 12 |
| C0006 | G0200A | HIGH | 328.0 kW, g3, r7.18600 | 2.21 | a1 315/80  0.00480 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.88 | 30363.0 | 4.0.3.3330 | 10 |
| C0007 | G0200A | HIGH | 366.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00400 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.88 | 31303.0 | 4.2.5 | 12 |
| C0030 | XD  270 FT | LOW | 293.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00490 twin false; a2 315/70  0.00600 twin true | A12 [4.88-5.12) -> 5.12 | 29523.0 | 4.2.7 | 8 |
| C0032 | XD  310 FT | LOW | 328.0 kW, g3, r7.71900 | 2.38 | a2 315/70  0.00680 twin true; a1 385/55  0.00450 twin false | A12 [4.88-5.12) -> 5.12 | 30423.0 | 4.2.7 | 12 |
| C0033 | XD  310 FT | LOW | 328.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00490 twin false; a2 315/70  0.00600 twin true | A12 [4.88-5.12) -> 5.12 | 31463.0 | 4.2.5 | 12 |
| C0034 | XD  310 FT | LOW | 328.0 kW, g3, r7.71900 | 2.38 | a2 315/70  0.00490 twin true; a1 385/65  0.00500 twin false | A13 [5.12-5.38) -> 5.32 | 31503.0 | 4.2.7 | 12 |
| C0041 | XD  350 FT | LOW | 361.0 kW, g3, r7.18600 | 2.21 | a2 315/70  0.00390 twin true; a1 385/55  0.00400 twin false | A11 [4.65-4.88) -> 4.88 | 31453.0 | 4.2.7 | 12 |
| C0042 | XD  350 FT | HIGH | 366.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00400 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.88 | 31173.0 | 4.0.3.3330 | 10 |
| C0043 | XD  350 FT | LOW | 361.0 kW, g3, r7.71900 | 2.38 | a2 315/70  0.00400 twin true; a1 385/55  0.00400 twin false | A11 [4.65-4.88) -> 4.88 | 31383.0 | 4.2.7 | 12 |
| C0044 | XD  350 FT | HIGH | 366.0 kW, g3, r7.71900 | 2.38 | a2 315/70  0.00400 twin true; a1 385/55  0.00400 twin false | A12 [4.88-5.12) -> 5.12 | 31133.0 | 4.0.2.3275 | 10 |
| C0045 | XD  350 FT | LOW | 361.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00400 twin false; a2 315/70  0.00490 twin true | A12 [4.88-5.12) -> 5.05 | 30323.0 | 4.2.7 | 12 |
| C0046 | XD  350 FT | LOW | 361.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00400 twin false; a2 315/70  0.00490 twin true | A12 [4.88-5.12) -> 5.10 | 31313.0 | 4.2.7 | 12 |
| C0047 | XD  350 FT | LOW | 366.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00450 twin false; a2 315/70  0.00680 twin true | A12 [4.88-5.12) -> 5.12 | 31433.0 | 4.2.5 | 12 |
| C0048 | XD  350 FT | HIGH | 366.0 kW, g3, r8.03100 | 2.47 | a1 385/55  0.00400 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.88 | 31203.0 | 4.0.2.3275 | 10 |
| C0049 | XD  350 FT | HIGH | 366.0 kW, g3, r8.03100 | 2.47 | a2 315/70  0.00400 twin true; a1 385/55  0.00400 twin false | A9 [4.22-4.43) -> 4.43 | 31123.0 | 4.0.3.3330 | 10 |
| C0051 | XF  350 FT | LOW | 361.0 kW, g3, r7.18600 | 2.21 | a1 385/55  0.00400 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.81 | 31263.0 | 4.2.7 | 12 |
| C0052 | XF  350 FT | HIGH | 350.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00400 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.88 | 31203.0 | 4.0.1.3217 | 10 |
| C0053 | XF  350 FT | HIGH | 366.0 kW, g3, r7.71900 | 2.38 | a2 315/70  0.00400 twin true; a1 385/55  0.00400 twin false | A11 [4.65-4.88) -> 4.88 | 31203.0 | 4.0.2.3275 | 10 |
| C0054 | XF  350 FT | LOW | 361.0 kW, g3, r7.71900 | 2.38 | a2 315/70  0.00600 twin true; a1 385/55  0.00490 twin false | A11 [4.65-4.88) -> 4.84 | 31313.0 | 4.2.7 | 12 |
| C0055 | XF  350 FT | LOW | 366.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00400 twin false; a2 315/70  0.00400 twin true | A11 [4.65-4.88) -> 4.88 | 31443.0 | 4.2.5 | 12 |
| C0056 | XF  350 FT | LOW | 361.0 kW, g3, r7.71900 | 2.38 | a1 385/55  0.00450 twin false; a2 315/70  0.00680 twin true | A15 [5.65-5.93) -> 5.93 | 31403.0 | 4.2.7 | 12 |

VECTO source for the inputs (file : line in the fork, all verified by reading the line):

| Input | VECTO file : line |
|---|---|
| Group 5 4x2 tractor segment: payload pairs, trailer ST1 / STT1 / EMS ST1+T2, axle shares, CdxA default 8.7, construction 7.2 | `Resources/Declaration/SegmentTable.csv` : 17 |
| Tyre 315/70 R22.5, 385/55 R22.5, 315/80 R22.5, 385/65 R22.5 (r_dyn, inertia) | `Resources/Declaration/Wheels.csv` : 41, 50, 42, 51 |
| Trailers ST1 (delta CdxA 0 / 2.1), STT1 (0 / 0), T2 (1.5 / 1.5) | `Resources/Declaration/Body_Trailers_Weights.csv` : 17, 20, 16 |
| Declared CdxA replaced by the default on Construction | `InputData/Reader/DataObjectAdapter/SimulationComponents/AirdragDataAdapter.cs` : 147; trailer delta added at 152 |
| Trailer list per mission; default CdxA | `Models/Declaration/TruckSegments.cs` : 198, 255 |
| ES standard technology; PS "Large Supply + AMS + elec. driven"; HVAC Default group 5; condenser | `Resources/Declaration/VAUX/ES-Tech.csv` : 2; `PS-Table.csv` : 38; `HVAC-Table.csv` : 27; `Cond-Table.csv` : 2 |
| g, air density, alternator efficiency 0.7, HVAC factor 0.8, trailer RRC 0.0055 and test load 37,500 N | `Models/Declaration/DeclarationData.cs` : 72, 74, 123, 126, 837, 839 |
| Rolling resistance and wheel inertia of the vehicle | `Models/SimulationComponent/Data/VehicleData.cs` : 166 (call), method `ComputeRollResistanceAndReducedMassWheels` |
| Cycles | `Resources/Declaration/MissionCycles/{RegionalDelivery,UrbanDelivery,LongHaul,Construction}.vdri` |
| Construction mission added for non-vocational vehicles in 4.1.0 | `CHANGES.md` : 229 (CodeEU-577) |
| Standard-values IEPC is wrapped and given two fake voltage levels; its map comes from the input XML | `InputData/Reader/DataObjectAdapter/SimulationComponents/ElectricMachinesDataAdapter.cs` : 263-266, 647-649, 739; `InputData/FileIO/XML/Declaration/DataProvider/XMLElectricMotorDeclarationInputDataProvider.cs` : 490 |

`NO SOURCE`: the truck-specific declaration XML (the VECTO job and component files of these DAF trucks) is in neither the fork nor the EEA data. EEA gives certification number, digest, rated power, gear count and lowest total ratio for the IEPC. The per-truck inputs above are the EEA values; the VECTO files give the defaults and rules the harness applied to them. FzISO (tyre test load) is a declared VECTO input that EEA does not publish; the harness uses a 31,300 N stand-in (`run_hdev.py` `FZISO_STANDIN`, label [BOB]).

## 3. What separates the two clusters (Part 1.2) [TEST `p1_daf_cluster_compare.csv`]

Cluster definition [ASSUMPTION]: HIGH = PR #38 C fit with F0 >= 800 N (9 configs); LOW = the other 14.

Compared on every input: VECTO version, Construction mission present, IEPC certificate, digest, rated kW, lowest ratio, gears, axle config, axle ratio, CdxA range, air-drag method, model, pneumatic / HVAC / steering labels, sleeper cab, battery kWh, TPMLM, tyre dimensions, vehicle count, and per mission test mass, rolling resistance, wheel inertia, r_dyn, aux watts, trailer delta CdxA, CdxA start, aux share, harness wheel energy. **No numeric input or label separates the clusters** except the IEPC digest (each digest sits in one cluster). The inputs that look like a cause and are not:

- Missing Construction mission. 7 of 9 HIGH configs have none, but so do 21 Volvo, 5 Renault and 2 Mercedes-Benz configs, with ordinary F0. Dropping the Construction rows from every group 5 config that has them leaves F0 unchanged (median 0 -> 0 N for DAF, 2 of 16 DAF above 800 N, none for the other six makes). [TEST `p1_construction_drop_all.csv`]

| make | configs with Construction | median F0 N, all missions | median F0 N, Construction rows dropped | configs with F0 >= 800 N after dropping |
|---|---:|---:|---:|---:|
| DAF | 16 | 0 | 0 | 2 |
| Iveco | 2 | 601 | 581 | 0 |
| MAN | 22 | 0 | 0 | 0 |
| Mercedes-Benz | 25 | 137 | 134 | 0 |
| Renault | 25 | 142 | 135 | 0 |
| Scania | 66 | 0 | 14 | 0 |
| Volvo | 63 | 172 | 184 | 0 |

- VECTO version. HIGH has 4.0.1, 4.0.2, 4.0.3 and also two 4.2.5 configs (C0004, C0007); LOW has 4.2.5 and 4.2.7. Three 4.2.5 standard-values configs (C0033, C0047, C0055) have F0 261-575 N. The version does not split the cluster.
- Rated kW, gear ratios, tyres, RRC, CdxA range, aux labels: all values occur in both clusters.

What does separate them is how the IEPC was declared. The EEA `iepc_cert_method` and the certificate number split the DAF configs:

| IEPC | configs | certificate | C: F0 | C: eta_d | certified / harness E_A |
|---|---:|---|---|---|---|
| Measured (VECTO component certificate 2017/2400) | 11 | `e1*2017/2400*2022/1379*I*00743*00` | 0 N on all 11 | 0.91-0.93 | 1.005-1.029 |
| Standard values (certificate number in UN R85 format; my reading of the format, not checked against a register) | 12 | `E1*85R00/11*4203*00` | 944-1,675 N on 9 (same digest ZmaBYbxf on 8); 261-575 N on 3 | 0.75-0.89 | 1.31-1.61 |

(C0033 is labelled `Measured` at config level by EEA because its 6 vehicles differ; its median-mass vehicle, the one used here, carries the R85 standard-values IEPC. Vehicle-level data: `p1_daf_level_by_config.csv`.) [DATA `hdv_2024_iepc.csv`; TEST]

| config | model | IEPC method | IEPC digest (first 8) | VECTO version | C F0 N | C eta_d | certified / E_A |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0030 | XD  270 FT | Measured | Vyicho0Q | 4.2.7 | 0.0 | 0.9074 | 1.029 |
| C0005 | G0100A | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.928 | 1.012 |
| C0041 | XD  350 FT | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.9237 | 1.018 |
| C0043 | XD  350 FT | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.9273 | 1.019 |
| C0045 | XD  350 FT | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.9197 | 1.018 |
| C0046 | XD  350 FT | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.926 | 1.014 |
| C0051 | XF  350 FT | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.9262 | 1.012 |
| C0054 | XF  350 FT | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.9223 | 1.01 |
| C0056 | XF  350 FT | Measured | eRN5zWbT | 4.2.7 | 0.0 | 0.9211 | 1.01 |
| C0032 | XD  310 FT | Measured | uO1XqJKd | 4.2.7 | 0.0 | 0.9074 | 1.014 |
| C0034 | XD  310 FT | Measured | uO1XqJKd | 4.2.7 | 0.0 | 0.9214 | 1.005 |
| C0033 | XD  310 FT | StandardValues | Ec/CV4sh | 4.2.5 | 574.5 | 0.7966 | 1.308 |
| C0047 | XD  350 FT | StandardValues | X4gNV7V2 | 4.2.5 | 261.1 | 0.7537 | 1.32 |
| C0055 | XF  350 FT | StandardValues | X4gNV7V2 | 4.2.5 | 388.3 | 0.788 | 1.331 |
| C0004 | G0100A | StandardValues | ZmaBYbxf | 4.2.5 | 1582.8 | 0.874 | 1.54 |
| C0007 | G0200A | StandardValues | ZmaBYbxf | 4.2.5 | 943.7 | 0.7702 | 1.551 |
| C0042 | XD  350 FT | StandardValues | ZmaBYbxf | 4.0.3.3330 | 1637.6 | 0.89 | 1.556 |
| C0044 | XD  350 FT | StandardValues | ZmaBYbxf | 4.0.2.3275 | 1612.1 | 0.8913 | 1.54 |
| C0048 | XD  350 FT | StandardValues | ZmaBYbxf | 4.0.2.3275 | 1651.9 | 0.8694 | 1.587 |
| C0049 | XD  350 FT | StandardValues | ZmaBYbxf | 4.0.3.3330 | 1674.8 | 0.8727 | 1.607 |
| C0052 | XF  350 FT | StandardValues | ZmaBYbxf | 4.0.1.3217 | 1604.9 | 0.8908 | 1.548 |
| C0053 | XF  350 FT | StandardValues | ZmaBYbxf | 4.0.2.3275 | 1610.0 | 0.8912 | 1.548 |
| C0006 | G0200A | StandardValues | cVODMXrB | 4.0.3.3330 | 1369.5 | 0.8761 | 1.47 |

The standard-values DAF trucks need 37-46 % more energy than the measured-IEPC DAF trucks at the same mission, mass (+159 to +321 kg) and payload, while the harness physics gives the same energy for both (E_A differs by -0.03 to +0.004 kWh/km):

| DAF group | mission (2,600 kg payload) | results | certified kWh/km | E_A kWh/km | test mass kg | certified / E_A (or ratio SV / measured) |
|---|---:|---:|---:|---:|---:|---:|
| SV/R85 | Construction | 5 | 1.416 | 1.033 | 19635 | 1.372 |
| SV/R85 | Long Haul | 12 | 1.438 | 0.949 | 20873 | 1.519 |
| SV/R85 | Regional Delivery | 12 | 1.364 | 0.93 | 20873 | 1.469 |
| SV/R85 | Urban Delivery | 12 | 1.271 | 0.846 | 20873 | 1.505 |
| measured/2017-2400 | Construction | 11 | 1.035 | 1.029 | 19314 | 1.006 |
| measured/2017-2400 | Long Haul | 11 | 0.986 | 0.98 | 20714 | 1.007 |
| measured/2017-2400 | Regional Delivery | 11 | 0.945 | 0.96 | 20714 | 0.985 |
| measured/2017-2400 | Urban Delivery | 11 | 0.917 | 0.864 | 20714 | 1.061 |
| difference SV minus measured | Construction |  | 0.381 | 0.004 | 321 | 1.368 |
| difference SV minus measured | Long Haul |  | 0.452 | -0.031 | 159 | 1.458 |
| difference SV minus measured | Regional Delivery |  | 0.419 | -0.03 | 159 | 1.443 |
| difference SV minus measured | Urban Delivery |  | 0.354 | -0.018 | 159 | 1.386 |

The extra certified energy is 0.35 kWh/km (Urban) to 0.45 kWh/km (Long Haul). A force of 1,600 N acting over the distance costs 0.444 kWh/km at the wheel (1,600 N x 1,000 m / 3.6e6), so method C reproduces this with F0, which is distance-proportional. That is why C can use F0 ~ 1,600 N: it stands in for the standard-values loss. [CALC]

The same level ratio over all of group 5, by make and IEPC method [TEST `p1_level_by_make_and_iepc_method.csv`]:

| make | IEPC method (EEA) | certificate | results | certified kWh/km | harness E_A kWh/km | certified / E_A | range | test mass kg | C eta_d (mean) | C F0 N (mean) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DAF | Measured | 2017/2400 number | 44 | 0.971 | 0.958 | 1.015 | 0.977 to 1.073 | 20364 | 0.921 | 0 |
| DAF | StandardValues | R85 number | 41 | 1.365 | 0.924 | 1.482 | 1.279 to 1.653 | 20722 | 0.841 | 1183 |
| Iveco | Measured | 2017/2400 number | 8 | 1.109 | 1.042 | 1.064 | 1.038 to 1.1 | 21518 | 0.966 | 601 |
| MAN | Measured | 2017/2400 number | 40 | 0.957 | 0.978 | 0.98 | 0.949 to 1.012 | 20290 | 0.935 | 7 |
| MAN | StandardValues | other | 48 | 1.033 | 0.962 | 1.076 | 1.037 to 1.18 | 20220 | 0.875 | 9 |
| Mercedes-Benz | Measured | 2017/2400 number | 88 | 0.974 | 0.966 | 1.01 | 0.966 to 1.107 | 20786 | 0.95 | 113 |
| Mercedes-Benz | StandardValues | none | 18 | 1.37 | 1.126 | 1.223 | 1.142 to 1.329 | 20539 | 0.776 | 78 |
| Renault | Measured | 2017/2400 number | 115 | 1.075 | 1.009 | 1.069 | 0.993 to 1.216 | 20476 | 0.933 | 115 |
| Scania | Measured | 2017/2400 number | 60 | 1.161 | 1.157 | 1.004 | 0.976 to 1.054 | 20673 | 0.902 | 1 |
| Scania | StandardValues | other | 204 | 1.304 | 1.164 | 1.125 | 1.049 to 1.272 | 20937 | 0.839 | 30 |
| Volvo | Measured | 2017/2400 number | 315 | 1.085 | 1.025 | 1.063 | 0.995 to 1.209 | 20518 | 0.948 | 176 |

Standard-values IEPC lifts the certified/E_A ratio for every make that has it (MAN 1.08, Scania 1.13, Mercedes-Benz 1.22, DAF 1.48) against 0.98-1.07 for measured IEPCs. The DAF lift is the largest, and only DAF gets F0 ~ 1,600 N. [DATA / CALC]

## 4. Refits with F0 fixed (Part 1.2) [TEST `p1_daf_refits.csv`, `p1_daf_mission_error.csv`]

C refitted with F0 = 0 and F0 = 1,600 N (this value is the median F0 of the DAF fits above 800 N, read off the fits, not from a source). eta_d, eta_r and the declared CdxA stay free.

| cluster | C fit | mission | results | mean err % | mean abs err % | worst abs err % |
|---|---:|---:|---:|---:|---:|---:|
| HIGH_F0 | free F0 (PR #38) | Construction | 4 | -1.1 | 1.4 | 2.7 |
| HIGH_F0 | free F0 (PR #38) | Long Haul | 18 | -1.3 | 1.9 | 4.0 |
| HIGH_F0 | free F0 (PR #38) | Long Haul EMS | 18 | -0.4 | 1.6 | 2.2 |
| HIGH_F0 | free F0 (PR #38) | Regional Delivery | 18 | +0.4 | 0.6 | 1.6 |
| HIGH_F0 | free F0 (PR #38) | Regional Delivery EMS | 18 | +1.1 | 1.1 | 2.2 |
| HIGH_F0 | free F0 (PR #38) | Urban Delivery | 18 | +0.1 | 5.2 | 6.0 |
| HIGH_F0 | F0 = 0 | Construction | 4 | -2.0 | 2.0 | 4.6 |
| HIGH_F0 | F0 = 0 | Long Haul | 18 | -7.5 | 7.5 | 16.1 |
| HIGH_F0 | F0 = 0 | Long Haul EMS | 18 | +0.3 | 5.7 | 6.7 |
| HIGH_F0 | F0 = 0 | Regional Delivery | 18 | -4.6 | 4.7 | 10.2 |
| HIGH_F0 | F0 = 0 | Regional Delivery EMS | 18 | +3.2 | 3.9 | 7.8 |
| HIGH_F0 | F0 = 0 | Urban Delivery | 18 | +4.0 | 4.0 | 6.0 |
| HIGH_F0 | F0 = 1600 N | Construction | 4 | -0.8 | 1.9 | 2.8 |
| HIGH_F0 | F0 = 1600 N | Long Haul | 18 | -1.2 | 1.7 | 3.6 |
| HIGH_F0 | F0 = 1600 N | Long Haul EMS | 18 | -0.6 | 1.7 | 2.2 |
| HIGH_F0 | F0 = 1600 N | Regional Delivery | 18 | +0.5 | 0.7 | 2.2 |
| HIGH_F0 | F0 = 1600 N | Regional Delivery EMS | 18 | +0.9 | 1.0 | 2.0 |
| HIGH_F0 | F0 = 1600 N | Urban Delivery | 18 | +0.1 | 5.4 | 7.1 |
| LOW_F0 | free F0 (PR #38) | Construction | 28 | -0.1 | 0.4 | 1.8 |
| LOW_F0 | free F0 (PR #38) | Long Haul | 28 | -1.5 | 1.5 | 3.7 |
| LOW_F0 | free F0 (PR #38) | Long Haul EMS | 26 | -1.7 | 1.7 | 2.4 |
| LOW_F0 | free F0 (PR #38) | Regional Delivery | 28 | +1.8 | 1.8 | 3.4 |
| LOW_F0 | free F0 (PR #38) | Regional Delivery EMS | 26 | +1.4 | 1.4 | 2.1 |
| LOW_F0 | free F0 (PR #38) | Urban Delivery | 28 | -0.2 | 3.5 | 6.6 |
| LOW_F0 | F0 = 0 | Construction | 28 | -0.2 | 0.4 | 1.2 |
| LOW_F0 | F0 = 0 | Long Haul | 28 | -1.9 | 2.0 | 8.5 |
| LOW_F0 | F0 = 0 | Long Haul EMS | 26 | -1.6 | 1.8 | 4.0 |
| LOW_F0 | F0 = 0 | Regional Delivery | 28 | +1.4 | 2.0 | 4.3 |
| LOW_F0 | F0 = 0 | Regional Delivery EMS | 26 | +1.5 | 1.5 | 4.2 |
| LOW_F0 | F0 = 0 | Urban Delivery | 28 | +0.1 | 3.3 | 8.2 |
| LOW_F0 | F0 = 1600 N | Construction | 28 | +13.2 | 13.7 | 22.9 |
| LOW_F0 | F0 = 1600 N | Long Haul | 28 | +19.4 | 19.7 | 31.7 |
| LOW_F0 | F0 = 1600 N | Long Haul EMS | 26 | +11.3 | 13.0 | 22.0 |
| LOW_F0 | F0 = 1600 N | Regional Delivery | 28 | +20.7 | 20.7 | 31.4 |
| LOW_F0 | F0 = 1600 N | Regional Delivery EMS | 26 | +12.0 | 12.8 | 21.9 |
| LOW_F0 | F0 = 1600 N | Urban Delivery | 28 | +0.8 | 9.8 | 13.4 |

- HIGH cluster with F0 = 0: eta_r goes to its 0.999 bound and eta_d to 0.65-0.69 (the fit pushes all the missing energy into the drive efficiency). Mean error: Long Haul -7.5 % (worst -16.1 %), Regional Delivery -4.6 % (worst -10.2 %), Regional EMS +3.2 %, Urban +4.0 %.
- LOW cluster with F0 = 1,600 N: eta_d and eta_r go to their bounds on 11 of 14 configs. Regional Delivery +20.7 % (worst +31.4 %), Long Haul +19.4 % (worst +31.7 %), Construction +13.2 %, EMS missions +11 to +12 %. Urban +0.8 % on average but 9.8 % mean absolute.
- With F0 wrong in either direction, Long Haul carries the largest error and Urban a smaller one. The standard-values extra is 0.35 kWh/km on Urban and 0.45 on Long Haul, so one F0 value does not fit both.
- In the HIGH cluster the CdxA fit sits at the upper range edge on 8 of 9 configs. [OPEN] I did not test whether this is real or the fit absorbing part of the extra energy.

F0 is not identified inside the standard-values group. Same digest ZmaBYbxf: F0 = 944 N (C0007) to 1,675 N, certified/E_A 1.54-1.61 for all eight. The fits trade F0 against eta_d and CdxA with similar in-sample error (1.9-2.2 % mean absolute for these eight).

## 5. eCanter C0059 (Part 1.3) [TEST `p1_ecanter.csv`, `p1_ecanter_ratio.csv`]

The eCanter has the level signature but not the F0 pattern. Its IEPC is standard values (vehicle-level EEA field `StandardValues`, no certificate number), and certified/E_A is 1.49 and 1.47 (Regional), 1.37 and 1.34 (Urban), the DAF standard-values range. But the free C fit gives F0 = 106 N, eta_d 0.69 and eta_r at its bound 1.0, and fixing F0 = 0 changes nothing (mean error 7.81 vs 7.83 %). F0 = 1,600 N makes Urban worse (+19.0 / +15.5 %). The error sits in Regional (-10.1 / -8.7 %) and Urban (+4.9 / +7.7 %). With 4 results and 3 fitted values (1 degree of freedom) the fit is not reliable. [TEST]

| C fit of C0059 | eta_d | F0 N | at bound | mean abs err % | worst % | Regional 333 kg % | Regional 1664 kg % | Urban 333 kg % | Urban 1664 kg % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| free F0 | 0.6887 | 105.9 | regen | 7.83 | 10.07 | -10.07 | -8.68 | 4.89 | 7.7 |
| F0 = 0 | 0.6636 | 0.0 | regen | 7.81 | 10.15 | -10.15 | -8.59 | 4.48 | 8.0 |
| F0 = 1600 N | 1.0 | 1600.0 | eta;regen | 11.03 | 19.01 | -4.79 | -4.86 | 19.01 | 15.45 |

## 6. Cause (Part 1.5)

**Finding.** The F0 ~ 1,600 N cluster is the group of DAF configs whose IEPC is declared with VECTO standard values (EEA `iepc_cert_method` = StandardValues, certificate `E1*85R00/11*4203*00` (R85 format)). Their certified energy is 1.31-1.61 times the harness physics for the same mission, mass, payload, tyres, aux and CdxA range, against 1.00-1.03 for DAF configs with a measured IEPC. The extra is 0.35-0.45 kWh/km. Method C fits it with F0 because the extra is nearly proportional to distance. Not the cause: missing Construction mission, VECTO version, kW, tyres, aux labels, CdxA range. [TEST / DATA; sources: `p1_daf_level_by_config.csv`, `hdv_2024_iepc.csv`, `ElectricMachinesDataAdapter.cs`:263-266]

**Not shown.** Why the standard-values loss of this DAF component is so much larger than for other makes' standard-values IEPCs (Scania x1.13, MAN x1.08), and what the loss map looks like. The standard-values map is part of the component's input XML; neither the fork nor EEA holds it. [OPEN]

**Diagnostic test of a hypothesis.** If the standard-values IEPC were described better by VECTO's standard-values shape (S4 = Annex Xb App. 8 ASM + standard gearbox + generic axle, from PR #37), L1[S4] would fit the 12 standard-values DAF configs better than L1[S3b]. It does, slightly, and still poorly: in-sample mean absolute error 6.24 % vs 6.87 % (L1) and 3.07 % vs 3.44 % (L1b), against 2.0 % for C. For the 11 measured DAF configs S4 is worse than S3b (2.66 vs 2.35 %). A shape x scale cannot represent a distance-proportional extra of this size. [TEST `final_daf_shape_diagnostic.csv`]

| DAF group | configs | method | in-sample mean abs err % |
|---|---:|---:|---:|
| R85 standard-values IEPC | 12 | C | 2.02 |
| R85 standard-values IEPC | 12 | L4b | 1.99 |
| R85 standard-values IEPC | 12 | L1[S3b_IEPC_3speed] | 6.87 |
| R85 standard-values IEPC | 12 | L1[S4_std_ASM] | 6.24 |
| R85 standard-values IEPC | 12 | L1b[S3b_IEPC_3speed] | 3.44 |
| R85 standard-values IEPC | 12 | L1b[S4_std_ASM] | 3.07 |
| VECTO-certified IEPC (2017/2400) | 11 | C | 1.68 |
| VECTO-certified IEPC (2017/2400) | 11 | L4b | 1.55 |
| VECTO-certified IEPC (2017/2400) | 11 | L1[S3b_IEPC_3speed] | 2.35 |
| VECTO-certified IEPC (2017/2400) | 11 | L1[S4_std_ASM] | 2.66 |
| VECTO-certified IEPC (2017/2400) | 11 | L1b[S3b_IEPC_3speed] | 1.97 |
| VECTO-certified IEPC (2017/2400) | 11 | L1b[S4_std_ASM] | 2.07 |

**Share of the group 5 spread that is DAF** (Table 2): removing DAF cuts the held-out width by 0.3 pp (C: 15.8 to 15.5), 1.5 pp (L4b: 15.8 to 14.3) and 3.0 pp (L1[S3b]: 17.0 to 14.0). It cuts the worst model error from 27.0 % to 11.9 % (C) and the worst single result from 38.0 % to 23.8 %. The class-band width falls from 14.7 to 13.0 (C) and 12.7 pp (L4b). The width left without DAF, 14-15.5 pp, comes from other models: five Scania models (G 230E, P 230E, S 450E) are 8-12 % too low and four MAN models 6-10 % too high.

---

# One page of answers

**Does a VECTO-map shape x one scale beat C and L4b on unseen models (width in pp)?**
No. With the GenericIEPC 3-speed shape L1 gives 17.0 pp (95 % interval 11.0-21.1) against C 15.8 (11.6-19.7) and L4b 15.8 (11.3-20.0). The paired difference to C is +1.2 pp (-1.7 to +4.7), so L1 is not shown narrower and not shown wider. The other three requested L1 shapes give 16.3 (S2 ASM), 18.4 (S2 PSM) and 18.7 pp (S3a); L1b gives 18.0-20.9 pp. Without DAF L1[S3b] is 14.0 pp against C 15.5 and L4b 14.3 (difference to C -1.5 pp, interval -4.0 to +2.7). L1 has one fitted value, removes the mean bias (+0.4 % vs -2.6 % for C and -1.6 % for L4b) and the share of results predicted too low (32 % vs 49 % and 45 %). Its in-sample fit is worse (mean absolute error 2.7 % vs 1.5 % and 1.7 %, worst config 17.9 % vs 6.6 % and 7.8 %). Worst single result 34.5 % vs 38.0 % and 36.2 %. On the 10 trucks (leave-one-result-out) L1 is worse than C and L4b: 4 trucks within 5 % (C 5, L4b 4), worst truck 19.8 % vs 12.7 % and 14.2 %; L1b[S2 ASM] has the smallest worst-truck error of the shape methods, 13.3 % (C 12.7 %).

**Does physics beat the physics-free baseline?**
Against B0 (median of all other models): yes. Width 30.2 pp vs 15.7-17.7 pp; median model error 10.7 % vs 4.1-4.9 %; physics is closer on 28-30 of 38 models. Against B1 (nearest models): mixed. Width 26.8 (k = 5) and 23.7 pp (k = 3) vs 15.7-17.7, but the k = 3 interval for the width difference includes zero (-1.0 to +21.3), and the median model error is 4.2 % for B1 k = 3 against 4.1-4.9 % for physics; physics is closer on 16-23 of 38 models (about half). Physics is better in the tails: worst single result 34.5-38.7 % vs 52.8 % for B1, mean model error 5.4-5.7 % vs 7.3 % (k = 3) and 8.1 % (k = 5). Physics also wins when the target keeps only its published CdxA range (PR #38's rule gives the target a CdxA fitted on its own results). Without DAF the worst model error is 11-12 % for physics against 25-27 % for the baselines. With DAF included the worst model error is 25-29 % for every method (B0 25.4, B1 25.1-29.3, physics 24.8-27.5): DAF G0200A is the worst model for C, L4b and L1 (-24.8 to -27.0 %) and is also -24.8 % for B1 with k = 3. [TEST]

**How much of the group 5 spread is DAF?**
Little of the P10-P90 width, most of the extremes. Removing DAF takes the held-out width from 15.8 to 15.5 pp (C), 15.8 to 14.3 pp (L4b) and 17.0 to 14.0 pp (L1[S3b]); the worst model error from 27.0 % to 11.9 %; the worst single result from 38.0 % to 23.8 %. 14-15.5 pp remains. The DAF part traces to 12 standard-values IEPC configs whose certified energy is 31-61 % above the harness physics (config means); the standard-values IEPCs of MAN, Scania and Mercedes-Benz average 8-22 % above, and those of other makes did not produce an F0 near 1,600 N.

**Kiro's recommendation (Bob decides).** If a class-level number is wanted, quote the width for the 32 non-DAF models (14-15.5 pp) next to the all-model width, and treat "IEPC declared with standard values" as its own input, because that energy level did not come from any fitted shape.

---

# Lists

**NO SOURCE**
- Loss map or standard-values data of the DAF IEPC (certificate `E1*85R00/11*4203*00`, digests ZmaBYbxf, cVODMXrB, X4gNV7V2, Ec/CV4sh).
- Truck-specific declaration XML of the DAF trucks (job file with tyres, aux, CdxA as declared to VECTO).
- FzISO per tyre (not in EEA; harness stand-in 31,300 N, [BOB]).
- Per-version differences in VECTO results between 4.0.x and the 4.3.4 fork. Not examined; the 4.2.5 configs that share the digest show the same level as the 4.0.x ones.
- IEPC standard-values formula of Reg. (EU) 2017/2400. I did not read it in this run (a web search did not return the Annex text). [OPEN]

**BLOCKED**: nothing in the runs. No config was skipped (254 of 254 fitted, 2,958 records, 0 skipped).

**Bob to fetch**
1. The standard-values IEPC data for the DAF digests above (or the Reg. (EU) 2017/2400 Annex Xb text for IEPC standard values; consolidated text at https://eur-lex.europa.eu/eli/reg/2017/2400).
2. FzISO of the DAF tyres 315/70 R22.5 and 385/55 R22.5.
3. One DAF standard-values job simulated in VECTO with the standard-values map and with a measured map, to confirm the 0.35-0.45 kWh/km difference.

**Choices I made** (unclear -> the option that changes least)
1. Part 0: the cache was rebuilt (git-ignored). `g5_fits.csv` is identical between two runs here. It differs from the committed file only at optimiser tolerance (max 6.1e-4 W in a, 1.3e-4 N in F0, 2e-8 in eta; bound hits and errors identical). I did not overwrite the committed PR #38 files.
2. Shapes: PR #37's `partA_shapes.py` was re-run. Its output files are identical to the committed ones. Bin edges of x = |P_wheel| / P_rated: 0, .01, .02, .03, .04, .06, .08, .10, .125, .15, .20, .25, .30, .40, .50, .60, .80, 1.0, 1.5; fine at low load where efficiency changes fastest and the trucks spend most time. Scatter per bin (P10 and P90 of the 1 s rows): `partA_shapes.csv`. Drive and regen are separate. Shapes: S3a, S3b, S2 PSM and S2 ASM as asked; S4, S1 and S3c exist from PR #37 (S3c only through `arch`, S4 only as the DAF diagnostic).
3. Headline L1/L1b shape = S3b, chosen because it is the VECTO example with the same layout as 252 of the 254 trucks (multi-gear IEPC) and was the PR #37 default for that layout. I chose it before comparing the widths. The `arch` rule is reported but fails for transfer: a class median of s only means something inside one shape; with `arch` the donors use S3b (s about 0.5-2.4), S3a (0.33) and S3c (0.37), and Iveco S-eWay and Mercedes-Benz eActros reach +36 % and +24 % mean error (worst single result 66.5 %).
4. Cluster threshold 800 N and the 1,600 N value: both from the PR #38 DAF fits, not from a source.
5. B1: k = 5 (and k = 3 shown), z-scored Euclidean distance on (reference test mass, rated kW) at model level, fixed before the run.
6. "Without DAF": case B (donors and targets) is the headline; case C is in Table 2.
7. Added to the requested set: the "middle of range" CdxA rule for held-out targets (PR #38's own-CdxA rule favours physics); bootstrap intervals; the S4 diagnostic for DAF.
8. Per-make shape table uses in-sample mean absolute error and held-out mean absolute model error; both are post hoc and not used to choose a shape for a truck.
9. Python packages were installed in a virtual environment outside the repo (`/projects/sandbox/.venv`) because the system site-packages are read-only.

---

# Per-make shape result (Part 2.5)

S2 ASM has the lowest L1 in-sample error for 5 of 7 makes (MAN, Mercedes-Benz, Renault, Scania, Volvo) and S2 PSM for DAF and Iveco. The spread between the four shapes inside one make is 0.5-1.1 pp in-sample (L1) and 0.1-0.5 pp (L1b). On held-out error S2 ASM is lowest for 6 of 7 makes with L1 and S2 PSM for 5 of 7 with L1b; no shape wins everywhere. A make-level shape pick is a hypothesis at the size of the noise in Table 1. [CALC]

# How to run

```bash
cd docs/research/drivetrain-curve-library-2026-11 && bash setup_v2_worktree.sh      # creates ../hdev-v2 and ../VECTO
for i in 0 1 2 3 4 5 6 7 8; do python g5_build_records.py $i; done                  # cache, git-ignored
cd ../drivetrain-shape-direct-daf-2026-11
python p0_recheck_claims.py
python p1_daf_inputs.py; python p1_daf_refits.py; python p1_daf_level.py; python p1_ecanter.py; python p1_without_daf.py
for s in arch S3a_IEPC_1speed S3b_IEPC_3speed S2_busIEPC_PSM S2_busIEPC_ASM S4_std_ASM; do python p2_fit_g5.py $s; done
python p2_eval_g5.py; python p2_ten_loro.py; python p3_baselines.py; python p3_pairwise.py
python final_tables.py; python build_report_tables.py; python assemble_report.py
```
