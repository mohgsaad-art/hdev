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

{{T1}}

The 95 % interval comes from 5,000 bootstrap resamples of the 38 models (seed 20261116). A width from 38 models carries about +-4 pp of sampling noise.

Paired differences of width against C (same resamples) [TEST `final_bootstrap.csv`]:

{{DIFF1}}

## Table 2. Without DAF (Part 1.4 and the same for L1). [TEST `p1_without_daf.csv`, `p2_g5_summary_without_daf.csv`]

PR #38 numbers reproduced in row A. B removes DAF from donors and targets (231 configs, 32 models). C removes DAF from the donors only and still evaluates DAF.

{{T3b}}

Same split for the shape methods (case B):

{{T3}}

## Table 3. Physics-free baselines against class-P50 physics, held-out models (Part 3). [TEST `p3_summary.csv`, `p3_pairwise.csv`]

B0 = median of the certified kWh/km of all other models at the same mission and payload. B1 = median of the k nearest other models by test mass and rated kW (k = 5 headline, k = 3 shown; z-scored Euclidean distance; test mass = TotalVehicleMass at Regional Delivery 12,900 kg). "CdxA of the target": PR #38 gives the held-out truck its own fitted CdxA, which uses that truck's certified results. A truly unseen truck has only its published range, so the "middle of range" rows are the fair comparison with B0 and B1.

{{T4}}

Model-by-model (absolute model mean error), physics with the CdxA range middle [TEST `p3_pairwise.csv`]:

{{PAIR}}

## Table 4. The 10 trucks of Appendix B, leave-one-result-out (Part 2.4). [TEST `p2_ten_summary.csv`]

Same 88 certified results, same fits and same definitions as PR #37 Part 3 (C and L4b reproduce PR #37 exactly: 5 and 4 trucks within 5 %, worst 12.7 % and 14.2 %).

{{T5}}

## Table 5. Which shape fits which group 5 make (Part 2.5). [TEST `final_by_make_best_shape.csv`]

Post hoc and per make, not per truck. [ASSUMPTION: any choice of VECTO shape for a truck is a hypothesis.] The held-out figure is the mean over the make's models of |model mean error|.

{{T6}}

## Shapes used: efficiency against load fraction, from VECTO's own maps (Part 2.1) [TEST `p2_shape_scatter_per_bin.csv`, `partA_shapes.csv`]

Method (KIT way, VECTO maps): the VECTO generic truck is driven over the five VECTO declaration cycles, two loadings, with the notebook driver and force engine; every 1 s wheel-power row goes through `drivetrain` (Appendix A) with the VECTO map of each chain. x = |P_wheel| / P_rated of the chain (S3a and S2: 315.3 kW, S3b: 318.5 kW). Bin edges: 0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.80, 1.0, 1.5. Fine bins at low load because efficiency changes fastest there and the trucks spend most of their time there; the share of wheel energy per bin is printed so a reader sees which bins matter. Efficiency per bin = wheel energy / electric energy (drive) or electric / wheel energy (regen), energy-weighted. The bracket is the P10-P90 of the 1 s row efficiencies in the bin (the scatter). The re-run of `partA_shapes.py` in this session gives files identical to PR #37's. The shapes come from one generic vehicle on the declaration cycles, so a bin's share of energy is not the share of any group 5 truck.

Drive:

{{T15_drive}}

Regeneration (a negative efficiency means the drivetrain draws electric power while the wheel recovers a little energy; this happens in the lowest bins):

{{T15_regen}}

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

{{T14}}

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

{{T13}}

- VECTO version. HIGH has 4.0.1, 4.0.2, 4.0.3 and also two 4.2.5 configs (C0004, C0007); LOW has 4.2.5 and 4.2.7. Three 4.2.5 standard-values configs (C0033, C0047, C0055) have F0 261-575 N. The version does not split the cluster.
- Rated kW, gear ratios, tyres, RRC, CdxA range, aux labels: all values occur in both clusters.

What does separate them is how the IEPC was declared. The EEA `iepc_cert_method` and the certificate number split the DAF configs:

| IEPC | configs | certificate | C: F0 | C: eta_d | certified / harness E_A |
|---|---:|---|---|---|---|
| Measured (VECTO component certificate 2017/2400) | 11 | `e1*2017/2400*2022/1379*I*00743*00` | 0 N on all 11 | 0.91-0.93 | 1.005-1.029 |
| Standard values (certificate number in UN R85 format; my reading of the format, not checked against a register) | 12 | `E1*85R00/11*4203*00` | 944-1,675 N on 9 (same digest ZmaBYbxf on 8); 261-575 N on 3 | 0.75-0.89 | 1.31-1.61 |

(C0033 is labelled `Measured` at config level by EEA because its 6 vehicles differ; its median-mass vehicle, the one used here, carries the R85 standard-values IEPC. Vehicle-level data: `p1_daf_level_by_config.csv`.) [DATA `hdv_2024_iepc.csv`; TEST]

{{T9}}

The standard-values DAF trucks need 37-46 % more energy than the measured-IEPC DAF trucks at the same mission, mass (+159 to +321 kg) and payload, while the harness physics gives the same energy for both (E_A differs by -0.03 to +0.004 kWh/km):

{{T8}}

The extra certified energy is 0.35 kWh/km (Urban) to 0.45 kWh/km (Long Haul). A force of 1,600 N acting over the distance costs 0.444 kWh/km at the wheel (1,600 N x 1,000 m / 3.6e6), so method C reproduces this with F0, which is distance-proportional. That is why C can use F0 ~ 1,600 N: it stands in for the standard-values loss. [CALC]

The same level ratio over all of group 5, by make and IEPC method [TEST `p1_level_by_make_and_iepc_method.csv`]:

{{T7}}

Standard-values IEPC lifts the certified/E_A ratio for every make that has it (MAN 1.08, Scania 1.13, Mercedes-Benz 1.22, DAF 1.48) against 0.98-1.07 for measured IEPCs. The DAF lift is the largest, and only DAF gets F0 ~ 1,600 N. [DATA / CALC]

## 4. Refits with F0 fixed (Part 1.2) [TEST `p1_daf_refits.csv`, `p1_daf_mission_error.csv`]

C refitted with F0 = 0 and F0 = 1,600 N (this value is the median F0 of the DAF fits above 800 N, read off the fits, not from a source). eta_d, eta_r and the declared CdxA stay free.

{{T10}}

- HIGH cluster with F0 = 0: eta_r goes to its 0.999 bound and eta_d to 0.65-0.69 (the fit pushes all the missing energy into the drive efficiency). Mean error: Long Haul -7.5 % (worst -16.1 %), Regional Delivery -4.6 % (worst -10.2 %), Regional EMS +3.2 %, Urban +4.0 %.
- LOW cluster with F0 = 1,600 N: eta_d and eta_r go to their bounds on 11 of 14 configs. Regional Delivery +20.7 % (worst +31.4 %), Long Haul +19.4 % (worst +31.7 %), Construction +13.2 %, EMS missions +11 to +12 %. Urban +0.8 % on average but 9.8 % mean absolute.
- With F0 wrong in either direction, Long Haul carries the largest error and Urban a smaller one. The standard-values extra is 0.35 kWh/km on Urban and 0.45 on Long Haul, so one F0 value does not fit both.
- In the HIGH cluster the CdxA fit sits at the upper range edge on 8 of 9 configs. [OPEN] I did not test whether this is real or the fit absorbing part of the extra energy.

F0 is not identified inside the standard-values group. Same digest ZmaBYbxf: F0 = 944 N (C0007) to 1,675 N, certified/E_A 1.54-1.61 for all eight. The fits trade F0 against eta_d and CdxA with similar in-sample error (1.9-2.2 % mean absolute for these eight).

## 5. eCanter C0059 (Part 1.3) [TEST `p1_ecanter.csv`, `p1_ecanter_ratio.csv`]

The eCanter has the level signature but not the F0 pattern. Its IEPC is standard values (vehicle-level EEA field `StandardValues`, no certificate number), and certified/E_A is 1.49 and 1.47 (Regional), 1.37 and 1.34 (Urban), the DAF standard-values range. But the free C fit gives F0 = 106 N, eta_d 0.69 and eta_r at its bound 1.0, and fixing F0 = 0 changes nothing (mean error 7.81 vs 7.83 %). F0 = 1,600 N makes Urban worse (+19.0 / +15.5 %). The error sits in Regional (-10.1 / -8.7 %) and Urban (+4.9 / +7.7 %). With 4 results and 3 fitted values (1 degree of freedom) the fit is not reliable. [TEST]

{{T11}}

## 6. Cause (Part 1.5)

**Finding.** The F0 ~ 1,600 N cluster is the group of DAF configs whose IEPC is declared with VECTO standard values (EEA `iepc_cert_method` = StandardValues, certificate `E1*85R00/11*4203*00` (R85 format)). Their certified energy is 1.31-1.61 times the harness physics for the same mission, mass, payload, tyres, aux and CdxA range, against 1.00-1.03 for DAF configs with a measured IEPC. The extra is 0.35-0.45 kWh/km. Method C fits it with F0 because the extra is nearly proportional to distance. Not the cause: missing Construction mission, VECTO version, kW, tyres, aux labels, CdxA range. [TEST / DATA; sources: `p1_daf_level_by_config.csv`, `hdv_2024_iepc.csv`, `ElectricMachinesDataAdapter.cs`:263-266]

**Not shown.** Why the standard-values loss of this DAF component is so much larger than for other makes' standard-values IEPCs (Scania x1.13, MAN x1.08), and what the loss map looks like. The standard-values map is part of the component's input XML; neither the fork nor EEA holds it. [OPEN]

**Diagnostic test of a hypothesis.** If the standard-values IEPC were described better by VECTO's standard-values shape (S4 = Annex Xb App. 8 ASM + standard gearbox + generic axle, from PR #37), L1[S4] would fit the 12 standard-values DAF configs better than L1[S3b]. It does, slightly, and still poorly: in-sample mean absolute error 6.24 % vs 6.87 % (L1) and 3.07 % vs 3.44 % (L1b), against 2.0 % for C. For the 11 measured DAF configs S4 is worse than S3b (2.66 vs 2.35 %). A shape x scale cannot represent a distance-proportional extra of this size. [TEST `final_daf_shape_diagnostic.csv`]

{{T12}}

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
