# Drivetrain: fixed numbers (Method C) vs a fitted loss equation (L4), on 10 EEA trucks, with real air-drag ranges

16 Nov 2026. Owner: Bob. Prompt: `docs/research/inputs/kiro-prompt-drivetrain-c-vs-equation-2026-11-16.md`.
Scripts, CSVs and graphs: `docs/research/drivetrain-curve-library-2026-11/`. Tests: `tests/drivetrain_curves/`.

All results below are **calibration on VECTO certified results**, not validation against measured trucks.
EEA data: CC BY 4.0 (attribution line in every CSV holding EEA values).

---

## Summary (one page)

**1. The air-drag range fix removes most of the mission bias.** [TEST `part1_airdrag.py`]
Before, every truck ran on VECTO's *standard* CdxA, even where EEA says air drag was *measured*. Now measured trucks use
the middle of their published range (Reg. (EU) 2018/956 Annex I Part C), and every mission follows VECTO's own CdxA
rule (declared value except on Construction; trailer ΔCdA only where VECTO adds a trailer). With today's fixed
drivetrain (Method A), the spread of the error across missions on the same truck fell:

| Truck | air drag | spread before | spread after |
|---|---|---|---|
| MAN eTGX | measured A12 | 30.0 pp | 10.6 pp |
| Mercedes eActros 600 | measured A12 | 33.2 pp | 11.3 pp |
| DAF XB | measured A11 | 32.6 pp | 6.4 pp |
| Renault D | measured A13 | 26.1 pp | 8.5 pp |
| IVECO S-eWay | measured A14 | 20.4 pp | 5.7 pp |
| Volvo FM | measured A23 | 14.6 pp | 1.2 pp |
| Mercedes Econic | standard A23 | 16.5 pp | 2.3 pp |

The Econic also improved although its air drag is standard: the old harness added a trailer ΔCdA on rigid-truck missions
that have no trailer in VECTO (a set-up error, fixed). What is left is mostly **Urban vs the rest**. Within a truck, the
Method A error falls by about 10 pp per unit of (braking energy / driving energy at the wheel) (r = −0.52). Urban has
the most braking. That is a drivetrain/regen effect, which is what the fits below are meant to capture. [CALC
`part1_regen_share_correlation.csv`]

**2. C vs L4a vs L4b, leave one certified result out (main view).** [TEST `part3_loo.py`, `part3_summary.csv`]

| | A (fixed, reference) | **C** (η_d, η_r, F0) | **L4a** (a + b·P²) | **L4b** (a + c·v + b·P²) |
|---|---|---|---|---|
| trucks with every prediction within 5 % | 2/10 | **5/10** | **5/10** | 4/10 |
| predictions within 5 % | 50 % | 86 % | 80 % | **89 %** |
| worst error on any truck | 32.5 % | **12.7 %** | 22.0 % | 14.2 % |
| share of predictions too low | 81 % | 51 % | 56 % | **47 %** |
| largest underestimate | −32.5 % | **−12.0 %** | −22.0 % | −14.2 % |

Leave one *mission* out (only folds with at least 1 degree of freedom): C 2/10, L4a 4/10, L4b 2/10 trucks within 5 %.
Largest underestimate: C −13.6 %, L4a −15.2 %, L4b −12.7 %.

**3. How much C and L4 differ.** Per prediction, |C − L4b| is **0.59 % of certified (median)**, 2.1 % (P90) and 5.4 %
(max). |C − L4a| is 1.6 % (median), 8.4 % (P90) and 17.3 % (max). On a cycle no method was fitted on (Municipal
without PTO), L4b stays within −4.0 to +8.4 % of C. L4a is **+10 to +50 %** above C, because its constant loss `a` runs
on every second of a slow stop-and-go cycle. [TEST `part3_method_differences.csv`, `part3_unseen_mission.csv`]

**Bottom line.** C and L4b give nearly the same numbers. C has the smaller worst case and the most trucks fully within
5 %. L4b has the most single predictions within 5 % and the fewest underestimates. L4a extrapolates badly. Neither
method gets the Fuso eCanter (worst 12.7–22 %) or the eActros 600 (9.8–11.9 %) within 5 %.

**Open items:** many fitted values sit on a bound (CdxA on a range edge in 16 of 18 fits of the 6 measured trucks; C's η_r = 1.0 on 3
trucks); the eCanter needs a speed loss larger than any VECTO generic map; two trucks have only 1 degree of freedom
(eCanter, eDaily); battery Ri loss (0.7–1.3 %) and VECTO's motor-off rows (up to 3.5 % on Urban) are absorbed into the
drivetrain values. See "Open / BLOCKED / Bob to fetch".

---

## Part 1 — Air-drag ranges into the harness

### 1.1 What VECTO does with the declared CdxA [VECTO, fork `mohgsaad-art/VECTO`, branch `IEPC-experiments`, `b8d6126`]

| Question | Answer | Where |
|---|---|---|
| Truck with **measured** air drag | VECTO uses the declared CdxA (data entry 23) on every mission **except Construction**, where it uses the SegmentTable default `CdxA_Construction` | `InputData/Reader/DataObjectAdapter/SimulationComponents/AirdragDataAdapter.cs` 140–149 |
| Truck with **standard values** (no air-drag input) | `DefaultCDxA` of the mission (SegmentTable `CdxA_Default`, or `CdxA_Construction` on Construction) | `AirdragDataAdapter.cs` 115–117; `Models/Declaration/TruckSegments.cs` 326–335 |
| Trailer | Both cases add the **sum of ΔCdA of all trailers of the mission** | `AirdragDataAdapter.cs` 117 and 151–152 |
| Which trailers | A trailer is used only if the SegmentTable column `Trailer Axles - <Long haul / Other>` is filled. EMS missions use the `EMS` column (e.g. `ST1+T2`, `D+ST1`) | `TruckSegments.cs` 280–306, 359–362 |
| Which ΔCdA value | First trailer: first number of `Body_Trailers_Weights.csv` "delta CdxA"; second and later trailers: second number | `TruckSegments.cs` 394–407 (`DeltaCrossWindArea[firstTrailer ? 0 : 1]`) |
| Tractors (groups 5, 10, 12) | ST1 first-trailer ΔCdA = **0** (`0/2.1`). So VECTO treats the declared tractor CdxA as already including the standard semi-trailer. EMS `ST1+T2` adds T2 as second trailer: +1.5 m² | `Resources/Declaration/Body_Trailers_Weights.csv` rows ST1, T2; `SegmentTable.csv` line 17 |
| Rigid trucks, Long Haul | Group 4 and 9 add trailer T2 (first trailer, +1.5 m²). Regional, Urban and Construction have **no trailer** | `SegmentTable.csv` lines 12, 19 |
| Rigid trucks, EMS (group 9) | `D+ST1`: dolly 0 + ST1 as second trailer 2.1 m² | `SegmentTable.csv` line 19; `Body_Trailers_Weights.csv` rows Dolly, ST1 |

**Set-up errors found in the v2 harness** (`run_hdev.cdxa_for` + `mission_setup.csv`; the harness itself was not edited, the fix is in the copy `harness.vecto_cdxa`):
1. The trailer ΔCdA of `trailer_code` was added on **every** mission, including rigid Regional, Urban and Construction, where VECTO has no trailer. Effect: group 4/9 rigid trucks ran with +1.5 m² (e.g. Volvo FM Regional 10.0 instead of 8.56 m²).
2. EMS used one trailer's first-trailer value. VECTO sums the EMS trailers (group 5 EMS: +1.5 instead of 0; group 9 EMS: +2.1 instead of +1.5).
3. Measured trucks ran on the standard CdxA (e.g. MAN eTGX 8.7 m² instead of 4.88–5.12 m²).

### 1.2 Ranges [REG, DATA]
- Table read from the UK-retained copy (https://www.legislation.gov.uk/eur/2018/956/annex/I, `data.xml`, fetched 16 Nov 2026). It matches the job table exactly (A1 0–3.00 … A24 8.77–9.21). The page notes that Part C was inserted by Delegated Regulation (EU) 2019/888. EUR-Lex returned an empty bot-check page from the sandbox → **Bob to fetch** (below). `cdxa_ranges.py`.
- All 4,603 in-scope trucks [DATA `truck_vehicles.csv` columns `AirDrag_CdxA_range`, `AirDrag_CertificationMethod`]: 3,390 measured, 1,212 standard values, 1 blank (range A1). **0 trucks have a range outside A1–A24**, so no truck is above 9.21 m² (`part1_range_counts.csv`).
- Standard-value trucks carry a range that contains VECTO's default (Fuso A19 ∋ 7.1; Scania/Econic A23 ∋ 8.7/8.5; eDaily A15 ∋ 5.8). [CALC]
- The 10 trucks: measured A11 (DAF), A12 (MAN, eActros), A13 (Renault), A14 (S-eWay), A23 (Volvo); standard A15 (eDaily), A19 (eCanter), A23 (Scania, Econic).

### 1.3 Method A before/after (range midpoint) — `part1_methodA_before_after.csv`, `part1_mission_pattern.csv`, `part1_methodA_by_mission.png`
Mean Method A error per mission, after the fix [TEST]:

| Truck | Urban | Regional | Long Haul | Constr. | Reg. EMS | LH EMS | spread |
|---|---|---|---|---|---|---|---|
| Fuso eCanter | −25.7 | −32.0 | | | | | 6.3 |
| IVECO S-eWay | −1.9 | −3.5 | −6.5 | −2.5 | −0.8 | −3.5 | 5.7 |
| Scania R 400E | −20.1 | −6.9 | −7.0 | −11.0 | −6.4 | −6.7 | 13.7 |
| MAN eTGX | −13.7 | −3.0 | −4.5 | −5.1 | −3.5 | −4.4 | 10.6 |
| Mercedes eActros 600 | −6.0 | +3.2 | +1.1 | +0.3 | +5.3 | +2.8 | 11.3 |
| Renault D | −30.6 | −27.2 | −22.1 | −26.4 | | | 8.5 |
| Volvo FM | | +1.6 | +1.2 | | +1.0 | +0.5 | 1.2 |
| Mercedes Econic | | −0.8 | −1.8 | −2.8 | −2.0 | −3.2 | 2.3 |
| IVECO eDaily | −5.7 | −5.9 | | | | | 0.3 |
| DAF XB | | −25.2 | −18.9 | −25.3 | | | 6.4 |

**Remaining patterns above 5 pp.** Every per-mission input for those trucks is listed in `part1_inputs_per_mission.csv`
(CdxA, trailers, ΔCdA, payload, total mass, effective RRC, wheel inertia, tyre dimension/RRC per axle, pneumatic aux
label, aux kWh/km, cycle, wheel driving and braking energy). Each matches VECTO's declaration rules above, and
masses and payloads are the EEA certified ones. No further set-up error was found. The pattern lines up with how much
the truck brakes: Urban has a braking/driving wheel-energy ratio of 0.65–0.70, Regional about 0.2. Method A's fixed
0.95 regen recovers more on Urban than VECTO's maps (and motor-off rows, Part 4) allow, so Urban comes out low. This is a
drivetrain effect. [CALC within-truck r = −0.52]

**Linearity check.** The fit moves CdxA inside its range by shifting P_wheel by ρ·L·W1(v)·ΔCdxA while keeping the driver
trajectory. Against a full re-run at the range maximum the result is −0.04 % (MAN Long Haul) and −0.03 % (S-eWay
Regional). [TEST `part1_linearity_check.csv`]

---

## Part 2 — The methods

**Shared physics.** v2 harness (`run_hdev.run_one` → notebook copies of `driver_model`, `force_engine`,
`consumption_engine`) with the Part 1 CdxA rule. [ASSUMPTION] The v2 harness is already in VECTO-equivalent mode:
ρ 1.188, declaration crosswind sets, VECTO aux table values (`aux_per_label.csv`, no `HVAC_thermal`), EEA certified
payloads and total masses, VECTO cycles and `.vacc`, grid-side ÷ 0.995. The remaining differences are in Part 4.

**Rated power** (x = |P_wheel| / P_rated) [DATA `hdv_2024_iepc.csv` / `hdv_2024_electricmachine.csv` column `RatedPower`; VECTO]:
- IEPC: VECTO writes `TotalRatedPowerCalculated` = maximum power of the full-load curve, counting both units of a wheel-motor IEPC (`InputData/FileIO/XML/Declaration/DataProvider/XMLElectricMotorDeclarationInputDataProvider.cs` 297–313, count 2 when `DesignTypeWheelMotor` and one unit measured; written by `MRFIEPCType.cs` 29). So for the eActros 600 (601 kW) and the Econic (407 kW) the value is the **total**. [ASSUMPTION: EEA `RatedPower` = MRF value]
- Central motor (E2/E3): VECTO writes `R85RatedPower` **per machine** (`MRFElectricMachinesType.cs` 40). All 10 trucks have `CountAtPosition` = 1, so per machine = total.
- [OPEN] The two definitions differ (IEPC: peak of the full-load curve; EM: R85 30-minute power), so x means slightly different things for E3/E2 and IEPC trucks.

**Methods** (`methods_lib.py`):

| Method | Per second, on rows where the drivetrain is engaged | Fitted | Bounds and source |
|---|---|---|---|
| A | P/(0.95·0.95·0.98) driving, P·0.95 braking | none | v2 `_drivetrains.VA_*` |
| C | P/η_d driving, P·η_r braking, plus F0·v at the wheel | η_d, η_r, F0 | 0.5–1.0, 0.3–1.0, 0–3,000 N: [ASSUMPTION, job prompt values] |
| L4a | P_el = P + P_loss, P_loss = a + b·P² | a, b | a ≤ 0.1848·P_rated, b ≤ 0.3615/P_rated |
| L4b | P_loss = a + c·v + b·P² | a, b, c | c ≤ 0.00626·P_rated per m/s |
| +CdxA | declared CdxA in [min, max) of the EEA range, measured air drag only, not on Construction | +1 | Reg. 2018/956 Annex I Part C |

Masks are the same as `consumption_engine`: coasting rows (M = 3) and braking at or below v_no_regen = 5 km/h get no
traction power and no loss. "Engaged" means M ≠ 0. [ASSUMPTION] On braking rows P_el = P + P_loss, so the recovered
magnitude is |P| − P_loss (the prompt's "P − P_loss" read as magnitudes).

**L4 bounds from VECTO's generic maps** [TEST `part2_methods.py`, `part2_noload_by_chain.csv`, `part2_L4_bounds.csv`].
Each VECTO chain (E2, bus-generic IEPC PSM and ASM, GenericIEPC 1-speed, 3-speed and wheel-motor, standard-value ASM)
was driven over the declaration cycles with zero torque at the wheel, then at full load:
- a: largest no-load electric power / P_rated at any cycle speed = 0.1848 (bus-generic PSM IEPC). Mean no-load is 0.016–0.067·P_rated.
- c: largest slope of no-load power against vehicle speed = 0.00626·P_rated per m/s (E2).
- b: largest loss per unit wheel power at x ≥ 0.6 = 0.3615 (bus-generic PSM); taking a = 0 at x = 1 gives b·P_rated = 0.3615.

**Link to Annex Xb App. 8.** [REG, form only] Regulation (EU) 2017/2400 Annex Xb Appendix 8 Step 6 builds standard-value
motor losses as P_loss = Σ k_mn·|T|^m·|ω|^n in normalised torque and speed (the ASM table transcribed on 3 Nov is in
`drivetrain-inputs-fallbacks-2026-11/_stdval.py` `K_ASM`: k_20, k_21, k_22, k_10, k_12, k_00, k_02, k_03).
- `a` stands for k_00 (a constant loss).
- `c·v` stands for the speed-only terms k_0n·|ω|^n (iron, friction, windage). Vehicle speed is the proxy for motor speed, because EEA has no gear ratios for multi-speed trucks. It is linear, where the regulation uses ω² and ω³.
- `b·P²` stands for k_20·|T|² (copper loss): at a fixed speed T ∝ P, so T² ∝ P².
- Dropped: the mixed terms k_21, k_22, k_12 and the speed dependence of the T² term, because there is no motor speed.
- [BLOCKED] The PSM k_mn table is not in the repo. The project extract `12h-annex-xb-...md` was not available, so the coefficients could not be checked against the regulation.

**Optimiser.** `scipy.optimize.least_squares` on relative residuals, bounded, 3 fixed starts, best kept, no random
numbers (`fit_v2`). One truck (MAN, 12 results) took 0.55–0.84 s CPU per method for a full leave-one-out, so all of
Part 3 needed about 9 s wall on 8 cores. [TEST `part2_timing_one_truck.csv`]

---

## Part 3 — Leave-one-out on the 10 trucks (main result)

Missions per truck: `part3_missions_per_truck.csv`. These are the median-mass vehicle's certified results, every mission
except Municipal, EMS kept: 4 to 12 results per truck.

### 3.1 Worst error per truck, leave one result out (LORO) [TEST `part3_worst_per_truck.csv`]

| Truck | A | C | L4a | L4b | dof C / L4a / L4b |
|---|---|---|---|---|---|
| DAF XB | 26.9 | 4.9 | 6.9 | 5.1 | 2 / 3 / 2 |
| Fuso eCanter | 32.5 | 12.7 | 22.0 | 14.2 | 1 / 2 / 1 |
| IVECO S-eWay | 8.6 | 3.7 | 12.1 | 4.6 | 8 / 9 / 8 |
| IVECO eDaily | 6.1 | 0.8 | 3.3 | 3.3 | 1 / 2 / 1 |
| MAN eTGX | 17.3 | 7.5 | **3.5** | 5.5 | 8 / 9 / 8 |
| Mercedes Econic | 4.0 | 2.3 | 3.1 | 1.9 | 7 / 8 / 7 |
| Mercedes eActros 600 | 9.6 | 9.8 | 11.5 | 11.9 | 8 / 9 / 8 |
| Renault D | 32.4 | 6.9 | 19.7 | 6.1 | 4 / 5 / 4 |
| Scania R 400E | 22.7 | 5.8 | **4.3** | 5.8 | 9 / 10 / 9 |
| Volvo FM | 2.2 | 1.5 | 1.6 | 1.4 | 4 / 5 / 4 |

dof = certified results − fitted values (full fit).

### 3.2 Leave one mission out (LOMO)
| Truck | A | C | L4a | L4b |
|---|---|---|---|---|
| DAF XB | 26.9 | 6.9 | 7.5 | 6.7 |
| Fuso eCanter* | 32.5 | 32.4 | 69.7 | 61.1 |
| IVECO S-eWay | 8.6 | 9.0 | 12.5 | 8.3 |
| IVECO eDaily* | 6.1 | 8.2 | 22.4 | 16.1 |
| MAN eTGX | 17.3 | 13.6 | 3.5 | 9.1 |
| Mercedes Econic | 4.0 | 2.5 | 3.7 | 1.9 |
| Mercedes eActros 600 | 9.6 | 11.2 | 11.3 | 12.7 |
| Renault D | 32.4 | 5.4 | 30.0 | 5.4 |
| Scania R 400E | 22.7 | 7.6 | 4.2 | 8.1 |
| Volvo FM | 2.2 | 1.8 | 2.9 | 2.5 |

\* Only 2 missions × 2 payloads. Hiding a mission leaves 2 results for 2–3 fitted values, so the fit is underdetermined.
They are flagged `underdetermined` in `part3_predictions.csv` and left out of the "LOMO_dof>=1" rows of `part3_summary.csv`.

### 3.3 Error by mission (LORO mean, min, max, %) [TEST `part3_predictions.csv`, `part3_error_by_mission.png`]

| Mission | C mean (min..max) | L4a | L4b |
|---|---|---|---|
| Urban | +1.0 (−9.8..+12.7) | +5.0 (−11.5..+19.7) | +0.6 (−11.9..+12.5) |
| Regional | −0.5 (−12.0..+2.8) | −3.9 (−22.0..+2.9) | −0.9 (−14.2..+2.9) |
| Long Haul | −0.7 (−5.5..+4.9) | −2.7 (−9.8..+1.2) | −0.8 (−4.2..+5.1) |
| Construction | −0.2 (−4.5..+1.3) | +0.5 (−8.3..+6.4) | +0.2 (−4.1..+2.1) |
| Regional EMS | +1.0 (−1.2..+3.2) | +0.9 (−2.3..+5.4) | +1.5 (−0.6..+5.4) |
| Long Haul EMS | −1.3 (−2.3..−0.2) | −1.5 (−5.3..+2.7) | −0.6 (−2.1..+2.7) |

The large misses are the eCanter (Urban over, Regional under, with every method) and the eActros 600 Urban.

### 3.4 How much C and L4 differ [TEST `part3_method_differences.csv`, `part3_unseen_mission.csv`]
- |C − L4b| per prediction: median 0.59 %, P90 2.14 %, max 5.35 % of certified (LORO); LOMO median 0.58 %, max 28.7 % (eCanter).
- |C − L4a|: median 1.62 %, P90 8.35 %, max 17.3 % (LORO); LOMO max 39.5 %.
- Unseen cycle, Municipal Utility **without PTO** (never fitted; EEA Municipal payload; groups 4 and 9 only):

| Truck | payload | C | L4a | L4b | L4a vs C | L4b vs C |
|---|---|---|---|---|---|---|
| Renault D | 3000 | 1.146 | 1.357 | 1.124 | +18.4 % | −1.9 % |
| Renault D | 600 | 1.065 | 1.246 | 1.045 | +17.0 % | −1.9 % |
| Volvo FM | 6000 | 1.172 | 1.312 | 1.148 | +11.9 % | −2.0 % |
| Volvo FM | 1200 | 1.048 | 1.186 | 1.024 | +13.2 % | −2.3 % |
| Mercedes Econic | 1200 | 1.012 | 1.126 | 0.971 | +11.3 % | −4.0 % |
| Mercedes Econic | 6000 | 1.141 | 1.260 | 1.097 | +10.4 % | −3.8 % |
| DAF XB | 1200 | 1.126 | 1.686 | 1.220 | +49.8 % | +8.4 % |
| DAF XB | 6000 | 1.254 | 1.816 | 1.336 | +44.9 % | +6.6 % |

  Groups 1, 5 and 53 have no Municipal mission → `BLOCKED` for those 6 trucks.

### 3.5 Fitted values and plausibility [TEST `part3_fitted_values.csv`, `part3_plausibility.csv`]
- **C**: η_d 0.69 (eCanter) to 0.97 (S-eWay, eActros 600). η_r = **1.0 on the eCanter, Renault and Volvo**, which is physically implausible (the fit uses regen to fix a level offset elsewhere). F0 0–961 N.
- **L4a/L4b implied drive efficiency** at x = 0.1 / 0.25 / 0.5 / 1.0: the large tractors are 0.84–0.89 / 0.90–0.92 / 0.90–0.92 / 0.85–0.89. That is a plausible shape: low at small load, peak at medium load, dropping at full load. The eCanter, Renault and DAF are much lower at x = 0.1 (0.52–0.67).
- **a vs VECTO no-load loss**: a/P_rated is 0–0.079. VECTO's generic no-load mean is 0.016–0.067, so most trucks sit inside VECTO's range. The DAF (L4a 0.079) is above it.
- **Fits on a bound** (within 0.1 % of the bound width):
  - CdxA on a range edge on **all 6 measured trucks**, with every method: S-eWay at max, MAN at max, eActros at min (L4) or max (C), Volvo at max (L4), DAF at min, Renault at max (L4).
  - b at its maximum on the eCanter, Renault (L4a) and eDaily (L4a).
  - c at its maximum on the eCanter.

  When the fit pushes CdxA to the edge of its published range, it is absorbing something that is not air drag. [OPEN]
- **eCanter**: certified Regional is 1.67 × Urban, against 1.1–1.3 × on the other trucks. A speed loss of c = 0.83 kW per m/s (at the VECTO bound) is not enough. Its IEPC is certified with **standard values** (EEA `iepc_cert_method`), whose losses may exceed VECTO's generic maps. [OPEN]

---

## Part 4 — What the certified number contains that the fit absorbs (E2 `.vmod`) [TEST `part4_absorbed_terms.py`]

| Run | battery Ri loss | cable loss | aux | charging (÷0.995) |
|---|---|---|---|---|
| Regional ref | 0.92 kWh = 0.87 % | 0.04 kWh | 3.06 % | +0.50 % |
| Regional low | 0.74 kWh = 0.74 % | 0.03 kWh | 3.25 % | +0.50 % |
| Urban ref | 1.03 kWh = 1.21 % | 0.05 kWh | 7.79 % | +0.50 % |
| Urban low | 0.66 kWh = 0.88 % | 0.03 kWh | 8.80 % | +0.50 % |
| LongHaul ref | 2.08 kWh = 1.34 % | 0.10 kWh | 1.84 % | +0.50 % |
| LongHaul low | 1.39 kWh = 1.02 % | 0.06 kWh | 2.08 % | +0.50 % |

(% of the battery-internal energy, from `.vmod` columns `P_REESS_loss`, `P_REESS_JB_Cables_loss`, `P_aux_el`, `P_REESS_int`.)

- **Modelled by the harness, not absorbed:** charging ÷ 0.995 and aux (VECTO table values).
- **Absorbed by the drivetrain values:** battery Ri and cable losses (0.8–1.4 %). Ri loss grows with current², i.e. roughly with P². So in L4 it lands mostly in `b`, in C in η_d/η_r. [CALC]
- **Correction once HDEV has OCV + Ri:** refit with the battery model switched on. Alternatively, subtract the battery model's own loss per run before fitting; the fitted values then hold the drivetrain only. [ASSUMPTION]

**Motor-off rows** (`EM_E2_off` > 0, `part4_motor_off.csv`). VECTO switches the motor off while coasting and rolling, and
when braking at low speed (`BatteryElectricMotorController.cs` 34–47, 62–70). HDEV instead regenerates on braking rows
above 5 km/h. Energy HDEV would recover on the braking rows where VECTO had the motor off:

| Run | braking rows with motor off | Method A rule | `drivetrain` with VECTO maps |
|---|---|---|---|
| Regional ref | 128 | −0.82 % | −0.34 % |
| Urban ref | 580 | **−3.50 %** | **−1.64 %** |
| Urban low | 478 | −2.49 % | −1.14 % |
| LongHaul ref | 120 | −0.90 % | −0.28 % |

(% of VECTO motor electric energy. Negative = HDEV lower than VECTO, i.e. an underestimate.) This is a mission-dependent
term, largest on Urban, and the drivetrain fit absorbs it.

**Remaining HDEV-vs-VECTO physics differences** (same E2 vehicle and cycles; wheel energy; `part4_physics_vs_vecto.csv`):
- Regional: +0.01 / −0.05 % (driving), +0.23 / −0.19 % (braking).
- Urban: +1.2 / +0.8 % driving, +2.3 / +1.8 % braking (HDEV cycle time 13,576 s vs VECTO 13,489 s: driver difference).
- Long Haul: `BLOCKED` (VECTO's E2 Long Haul run has a trailer: 11,274 / 19,811 kg, CdxA 6.13 m²; the E2 set-up used here has none).

Other known gaps (v2 report, unchanged here):
- FzISO stand-in 31,300 N for all truck tyres [v2 `BOB`].
- Steering pump electric = 0.
- HVAC default per group.
- EMS second-trailer tyres taken from the first trailer code.
- Motor/gearbox inertia not in EEA; v2 has none, so it is absorbed.

---

## Proposed changes (not applied to the notebook or `src/`)

**1. Reader: VECTO loss-map coordinates** (`reference_copy.vecto_loss_map`).
Effect on the E2 `.vmod` rows: gearbox loss −2.1 … −3.3 % → within 0.06 % on non-shift rows. [TEST `gate_drivetrain.py`, stopped run]
```python
# before: drivetrain(..., axle_map=read_vtlm(f), gear_maps=[read_vtlm(g) for g in G], ...)
# after (TransmissionLossMap.cs 76-77 triangulates on (n_in, T_in - loss)):
def vecto_loss_map(table):
    b = np.array(table, float); b[:, 1] = b[:, 1] - b[:, 2]; return b
drivetrain(..., axle_map=vecto_loss_map(read_vtlm(f)), gear_maps=[vecto_loss_map(read_vtlm(g)) for g in G], ...)
```

**2. Harness / reader: VECTO CdxA rule + published range** (`harness.vecto_cdxa`).
Effect: Method A mission spread 30 → 11 pp (MAN), 33 → 11 pp (eActros), 33 → 6 pp (DAF); C now has 5/10 trucks within 5 %.
```python
# before (v2 run_hdev.cdxa_for): cdxa0 = SegmentTable CdxA_Default + DeltaCdA(trailer_code)    # every mission, standard CdxA
# after:
base   = cdxa_declared if (measured and mission != "Construction") else segment_default(mission)  # AirdragDataAdapter.cs 147-149
cdxa0  = base + sum(delta_cda(t, first=(i == 0)) for i, t in enumerate(vecto_trailers(mission)))  # TruckSegments.cs 280-306, 404
cdxa_declared in [range_min, range_max)   # Reg. 2018/956 Annex I Part C; midpoint if not fitted
```

**3. `consumption_engine` step 5: optional loss equation** (only if Bob chooses L4b; Kiro's recommendation below).
```python
# before (lines 529-530)
P_trac = np.where(P_wheel > 0, P_wheel / drivetrain_effeiciency, P_wheel * regen_effeiciency)
# after (scalar path unchanged when loss_coeffs is None)
if loss_coeffs is None:
    P_trac = np.where(P_wheel > 0, P_wheel / drivetrain_effeiciency, P_wheel * regen_effeiciency)
else:
    a, b, c = loss_coeffs                    # W, 1/W, W per m/s (fitted per truck)
    P_trac = P_wheel + a + c * v_avg + b * P_wheel ** 2
```
Measured effect on the 10 trucks (LORO): see 3.1. L4b vs C: median 0.6 % apart.

**Kiro's recommendation** (Bob decides):
- Keep C as the per-truck baseline. It has the smallest worst case (12.7 %), the smallest underestimate (−12.0 %) and 5/10 trucks fully within 5 %.
- L4b is a close second. It gives almost the same numbers, has fewer underestimates (47 % vs 51 %), and produces a load-shaped efficiency that looks like VECTO's maps.
- Do not use L4a: it extrapolates badly on an unseen cycle (+10 to +50 %).
- Before any library, fix or explain the CdxA-at-range-edge pattern and the eCanter.

---

## Choices I made
1. Continued on the stopped run's branch. Kept `reference_copy.py`, `harness.py`, `methods_lib.py`, `shapes_lib.py`, the gate scripts and the VECTO shapes (Part A of the stopped run; now used only to derive the L4 bounds). Deleted the stopped run's Part D script and cache (out of scope), and its Part C outputs (standard CdxA; they also compared against 7 Nov).
2. v2 harness used unchanged from a git worktree of commit `73990f0`. VECTO from a shallow clone of `IEPC-experiments` at `b8d6126` (`setup_v2_worktree.sh`).
3. One vehicle per config: the median-mass vehicle (v2 `select_sample.py` rule).
4. LOMO "mission" = the exact EMS/non-EMS mission name (Regional EMS is its own mission).
5. Braking rows in L4: P_el = P + P_loss (|P_el| = |P| − P_loss).
6. CdxA moved by a linear shift of P_wheel (checked: 0.04 %), fitted only for measured air drag, and not moved on Construction (as VECTO).
7. L4 bounds scale with each truck's EEA rated power; derived from VECTO generic chains on the E2 body.
8. Unseen cycle = Municipal Utility without PTO (the only VECTO mission with a set-up and an EEA payload that is never fitted).
9. Optional L1/L2 (shape × scale) not re-run. In the stopped run with standard CdxA, none beat C.
10. Part 1 counts are for all 4,603 trucks (a data count, no fitting); all fitting is on the 10 trucks only. No library files.

## NO SOURCE
- C bounds η_d 0.5–1.0, η_r 0.3–1.0, F0 0–3,000 N (job prompt values, marked [ASSUMPTION]).
- FzISO stand-in 31,300 N (v2 harness, `[BOB]`).
- Tmax_in = 1,940 Nm for the standard-value gearbox chain S4 (3 Nov `[ASSUMP]`, only used for the L4 bounds).

## BLOCKED
- Annex Xb App. 8 k_mn tables (PSM; ASM/ESM/RM) not in the repo → L4 not checked against the regulation coefficients.
- Unseen-cycle check for groups 1, 5, 53 (no Municipal mission in VECTO's SegmentTable).
- HDEV vs VECTO Long Haul physics on E2 (the E2 set-up has no trailer).
- Verification of the range table against EUR-Lex (bot-check page from the sandbox).

## Bob to fetch
1. https://eur-lex.europa.eu/eli/reg/2018/956/oj and Delegated Regulation (EU) 2019/888: Annex I Part C. Check the 24 min/max values against `cdxa_ranges.py`, and check whether any later amendment changed them.
2. Regulation (EU) 2017/2400 (consolidated), Annex Xb Appendix 8 Step 6 (k_mn tables for PSM and ASM/ESM/RM): add the extract `12h-annex-xb-standard-values-and-simulation-input-parameters.md` to `docs/research/inputs/`.
3. For the eActros 600 and Econic: `NrOfDesignTypeWheelMotorMeasured` (not in EEA; decides whether VECTO doubled a single measured unit).

## OPEN
- CdxA on a range edge in 16 of 18 measured-truck fits: what non-air-drag error does it absorb?
- eCanter: Regional/Urban ratio of 1.67 is not reproducible with any VECTO-bounded loss.
- Rated-power definition differs between IEPC (FLD peak) and EM (R85).
- Battery Ri and motor-off terms are inside the fitted values (Part 4).

## How to run
```bash
bash docs/research/drivetrain-curve-library-2026-11/setup_v2_worktree.sh     # v2 worktree + VECTO fork next to the repo
cd docs/research/drivetrain-curve-library-2026-11
python gate1_v2_harness.py; python gate_drivetrain.py                         # gates (stopped run, still pass)
python partA_shapes.py          # VECTO shapes (input to the L4 bounds), ~15 s
python part1_airdrag.py         # ~30 s first time (builds the .npz cache), then ~3 s
python part2_methods.py         # ~8 s
python part3_loo.py             # ~10 s on 8 cores
python part4_absorbed_terms.py  # ~5 s
python -m pytest tests/drivetrain_curves -q    # from the repo root
```
Every script prints the files it wrote. Running Parts 1–3 twice gives identical CSVs, except the CPU-time column of
`part3_worst_per_truck.csv`. CPU: Intel Xeon Platinum 8488C, 8 cores.
