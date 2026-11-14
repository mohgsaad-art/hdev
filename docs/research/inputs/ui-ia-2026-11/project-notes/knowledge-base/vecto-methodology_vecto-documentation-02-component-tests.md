# VECTO / HDV CO2 Certification Methodology — Part 2: Component Test Procedures

*(Source: same document as Part 1 — LOT 3 Final/Draft Final Report, Report No. I 07/14/Rex EM, 25.06.2014, Chapter 4.2, pages 11–41 of 170)*

This part covers **Section 4.2 "Development of Component test procedures"**, covering the engine, tires, aerodynamic drag, transmission, axle, and auxiliaries. These are all **conventional internal-combustion-engine driveline** component tests — there is no battery, e-motor, or fuel-cell component test procedure in this document (see the scope note in Part 1).

## 4.2.1. Engine Test

The specific fuel consumption is calculated in VECTO by **interpolation from an engine map**: fuel flow [g/h] over engine speed [rpm] and engine torque [Nm]. Approximately **100 measured points** are requested in the map for good accuracy. The engine test is **mandatory** — no default values are permitted for the engine fuel map.

The engine test procedure consists of three parts:
- (A) Fuel consumption (FC) map
- (B) WHTC test
- (C) Set-up of WHTC correction factors

### 4.2.1.1. Fuel Consumption Map

The procedure follows the **EURO VI WHSC/WHTC test procedure (UN/ECE, 2013)** wherever possible, with additional load points beyond the regulated pollutant-emissions certification test.

**Test conditions (verbatim):**
- Stabilization time of each mode: 60 sec.
- Fuel flow measurement over 30 sec → total mode length 90 sec.
- Ramp time between modes for each speed sweep: 20 sec.
- Ramp time between speed steps: 45 sec.
- Lowest load for mapping: 0 Nm (no fuel flow measurement below 0 Nm).

**Net engine torque** is determined similarly to the EURO VI emission certification method (**Regulation 582/2011**) — i.e., power consumption of oil pump, coolant pump, fuel delivery pump, fuel high-pressure pump, and alternator (covering the engine's own electricity demand) is already included in the fuel map.

**Grid of test points (minimum requirements):**
- Minimum 10 speed steps and minimum 10 load steps at maximum-torque speed.
- From zero torque, the same load-step distance is used for all speeds until maximum torque is exceeded; fuel flow at maximum torque measured for all speeds.
- Four base speeds are defined: `nidle`, `npref − npref·0.04`, `npref + npref·0.04`, `n95`.
- Remaining ≥6 speeds added by inserting ≥3 equidistant speeds in two ranges:
  - Range (1), from `nidle` to `{npref − npref·0.04}`: `ni = ni-1 + {(npref − npref·0.04) − nidle}·0.25`
  - Range (2), from `{npref + npref·0.04}` to `n95`: `ni = ni-1 + {n95 − (npref + npref·0.04)}·0.25`
- Vertical mapping is applied (per **[Figure 2 description]:** a schematic showing the engine fuel-flow map grid and vertical test-point sequence over the torque axis for each fixed engine speed).

### CO2 from Carbon Balance

To calculate CO2 emissions, complete oxidation of Carbon to CO2 is assumed:

```
m_CO2 = m_Fuel × m%C × (44/12)
```
where: m_CO2 = CO2 mass flow [kg/h]; m_Fuel = fuel mass flow [kg/h]; m%C = mass fraction of Carbon in the fuel.

If mechanical work and engine efficiency over the cycle are treated as fixed for a given engine/fuel combination:

```
CO2 [g] = (W_w-pos / Efficiency_Engine) × (kgC/kWh)_fuel × (44/12)
```
where: W_w-pos = positive engine work [kWh].

**Fuel-property correction concept (proposed, not finalized):**
```
ΔCO2_f = (kgC/kWh)_reference / (kgC/kWh)_test fuel
```
```
Δṁ_f = (kg_fuel/kWh)_reference / (kg_fuel/kWh)_test fuel
```
The document notes these corrections require mandatory measurement of the test fuel's carbon mass fraction and energy density — **not mandatory at the time of writing**. VECTO therefore implements a **variable "mCO2/mfuel" input parameter** to allow future flexibility; as of the report date it is fixed in declaration mode pending a decision aligned with the (then-forthcoming) WLTP LDV regulation approach.

### 4.2.1.2. WHTC Correction Procedure

Three shortcomings of using a simple steady-state fuel map (verbatim):
1. No assurance of consistency between regulated-emissions/fuel-consumption results in the WHTC test vs. the steady-state map — described as "one of the most important requirements for an appropriate HDV CO2 certification method."
2. Modern engines' fuel consumption is influenced by many parameters (e.g., SCR temperature level), which can differ between the steady-state map conditions and mission-profile-representative conditions.
3. Transient engine behaviour (e.g., turbo lag reducing air-to-fuel ratio during transient load increase) is not captured by a steady-state map.

**Solution: mission-profile-specific "WHTC correction factor" (WCF).** Concept: interpolate WHTC fuel consumption from the measured steady-state fuel map, compare to actually measured WHTC fuel consumption; the ratio gives a correction factor. Separate WCFs are produced for the **Urban, Road (Rural), and Motorway** parts of the WHTC, then mixed by mission-profile-specific weights.

**Measurement of WHTC:** per **Regulation 582/2011**, same engine as fuel map; must meet WHTC emission limits; fuel flow recorded at minimum 1 Hz. Target uncertainty discussed: not more than 1% total uncertainty for brake specific fuel consumption [g/kWh] (aspirational — "feasible accuracy needs to be further evaluated").

**Interpolation basis:** the WHTC fuel-flow interpolation is based on **target (not measured) engine speed and torque**, using the same Delaunay-triangulation interpolation method used elsewhere in VECTO (see Part 3). Reason: highly transient WHTC phases can have high torque-signal measurement uncertainty on some test stands, risking extrapolation bias. To prevent gaming (running lower power than target), **WCFs are calculated from brake-specific [g/kWh] results** using measured/target engine work as the respective denominators — integral (cycle-total) values are robust even though instantaneous target-vs-measured torque/speed differ.

**Formulas:**
```
BsFc_intpol-Urban [g/kWh] = (Σ FCi_WHTC-Urban) / (Target positive engine work_WHTC-Urban)
BsFc_intpol-Road  [g/kWh] = (Σ FCi_WHTC-Road)  / (Target positive engine work_WHTC-Road)
BsFc_intpol-MW    [g/kWh] = (Σ FCi_WHTC-MW)    / (Target positive engine work_WHTC-MW)
```
```
BsFc_meas-Urban [g/kWh] = (Σ FCmi_WHTC-Urban) / (Measured positive engine work_WHTC-Urban)
BsFc_meas-Road  [g/kWh] = (Σ FCmi_WHTC-Road)  / (Measured positive engine work_WHTC-Road)
BsFc_meas-MW    [g/kWh] = (Σ FCmi_WHTC-MW)    / (Measured positive engine work_WHTC-MW)
```
```
WCF_Urb  = BsFc_meas-Urban / BsFc_intpol-Urban
WCF_Road = BsFc_meas-Road  / BsFc_intpol-Road
WCF_MW   = BsFc_meas-MW    / BsFc_intpol-MW
```
Total correction factor per mission profile *i*:
```
WCF_Tot-i = WCF_Urb × WF_Urb-i + WCF_Rur × WF_Rur-i + WCF_MW × WF_MW-i
```

**Table 4 (Weighting factors for WHTC road-category correction factors, final values from HDH GTR work)** — reproduced:

| Index | Mission profile | WF_MW | WF_Road | WF_Urb |
|---|---|---|---|---|
| 1 | Long haul | 89% | 0% | 11% |
| 2 | Regional delivery | 53% | 30% | 17% |
| 3 | Urban delivery | 4% | 27% | 69% |
| 4 | Municipal utility | 2% | 0% | 98% |
| 5 | Construction | 6% | 32% | 62% |
| 6 | Citybus | 0% | 0% | 100% |
| 7 | Interurban bus | 19% | 36% | 45% |
| 8 | Coach | 78% | 22% | 0% |

These generic weighting factors were derived from VECTO pre-processing simulations (matching mission-profile kinematics like power, engine speed and their 2-second derivatives) rather than vehicle-by-vehicle recomputation, because the weights were found to depend mainly on the test cycle, not the specific vehicle. Reference: this approach traces to a document on the Heavy Duty Hybrid-HILS test procedure (Hausberger, 2012).

**Overall engine-test outputs (VECTO inputs), verbatim list:**
1. Engine make/model with main data to de-normalize the WHTC (nidle, npref, n95, rated power/speed)
2. Reference fuel properties (m%-C, kg/kWh) — future option
3. Engine fuel flow map
4. Full-load curve and motoring curve
5. WHTC road-category correction factors: WCF_Urb, WCF_Road (extra-urban), WCF_MW (motorway)

### 4.2.1.3. Proof of Concept for Engine Fuel Consumption Approach

Two engines tested:
- **Engine#1:** EURO III, rated power 2290kW at 1800 1/min *(note: this figure appears anomalously high for a EURO III engine — likely an OCR/typesetting artifact in the source table; reproduced as printed but flagged **[unclear from source]**)*, max net torque 1850Nm at 1080 1/min, max permitted speed 2300 1/min, capacity 12 litres.
- **Engine#2:** EURO VI prototype (confidential specs), measured per ACEA proposal dated 26 Feb 2013.

**[Figure 4 description]:** WHTC correction factors for Engine#1 — bar chart by mission profile (urban delivery, regional delivery, long haul); urban delivery correction factor = 1.016, regional/long-haul close to 1.0.

**[Figure 5 description]:** Comparison of measured vs. simulated fuel consumption for Engine#1 — grey bars (pre-WHTC-correction) vs. green bars (final, corrected); deviation only a few tenths of a percent.

**[Figure 6 description]:** WHTC correction factors for Engine#2 (EURO VI prototype) — higher spread (0.994–0.997) between urban and motorway parts of a split long-haul cycle (first/last 500s = "off-motorway"; remaining 4300s = "motorway"), reflecting higher sensitivity of the more complex EURO VI engine.

**[Figure 7 description]:** Measured vs. simulated fuel consumption, Engine#2 — simulation slightly underestimates; max deviation 1.2% for the off-highway part of long-haul, "within the range of stated repeatability for fuel consumption measurement at the engine test bed (approx. +/-1.5%)."

Key conclusion (verbatim intent): the WHTC correction factor serves not only to improve simulation accuracy but also to **assure consistency of regulated emissions and fuel consumption** between the WHTC test and the steady-state fuel map — called "one of the most important requirements for an appropriate HDV CO2 certification method."

## 4.2.2. Rolling Resistance Tyres

Rolling resistance coefficient definition:
```
RRC = -F₀ / Fz    [dimensionless ratio of rolling resistance force to vertical force]
```
Total vehicle rolling resistance = sum over all axles:
```
F = Σᵢ Fz,i × RRC_i
```
RRC depends on: vertical force on the axle (higher load → lower RRC, due to higher tire temperature/pressure), ambient temperature and sun radiation, tread depth, and road pavement.

Because pavement/ambient conditions during the road-load (aero) test cannot be tightly controlled, **RRC from the road test is NOT used as VECTO input.** Instead:

- The **EU tire labelling directive (EC 122/2009 and 1235/2011)** allocates a label "A" to "G" per RRC value on a standardized test drum.
- Test procedure per **ISO 28580**; RRC determination per **EC Regulation 117**.
- Inter-laboratory alignment procedure established by tire manufacturers to correct for test-stand differences.
- **[Figure 8 description]:** schematic of the source and handling flow of tire RRC data — from drum test → label alignment → VECTO input.
- Comparisons in the proof-of-concept phase found aligned drum RRC values match road-test RRC values well, without further correction (citing Fontaras, 2014; supported by ACEA, 2014).
- Tolerance for RRC declared label: **±0.3 [kg/ton]**. Example: Label class A covers tires up to RRC 5 [kg/ton] +0.3; Class B up to 6 [kg/ton] +0.3.
- **Decision as of 03/2014** (agreed among Commission, ETRMA, ACEA): use the **RRC value of the actual tire mounted on the vehicle as delivered to the customer** (not the label average or upper limit), for higher accuracy and to incentivize incremental RRC improvements.

**Open points (verbatim):** tolerances to be applied to RRC values of single tires; how a Conformity of Production (CoP) is introduced and responsibilities allocated.

## 4.2.3. Air Drag Test (Constant Speed Test Procedure)

### 4.2.3.1. Method Overview

Goal: determine Cd×Afr (drag coefficient × frontal area) at **zero-wind conditions (yaw angle β=0)**.

**Measured simultaneously:** wheel torque of driven wheels, vehicle velocity, actual air-flow velocity (vehicle speed + wind), air-flow direction — over straight motion on a test track, at two constant speeds:
- **V_low:** 10–15 km/h
- **V_high:** target 85–90 km/h (or maximum achievable if the vehicle cannot reach this)

**Key assumptions (explicitly stated as "qualified assumptions," verbatim):**
- Rolling resistance force (and gradient force) independent of vehicle speed — **footnoted as later found not fully valid** (see Open Issues below).
- Air drag force increases quadratically with air velocity.

**[Figure 9 description]:** "Key points of the constant speed testing methodology" — likely a force/velocity diagram illustrating the low-speed vs. high-speed measurement points and the derivation of Cd×A from the difference.

**[Figure 10 description]:** "Types of testing grounds and definition of measurement sections" — schematic of different track geometries (e.g., oval, straight-with-turnaround), showing measurement sections and stabilization straights before each.

### Test Sequence (four phases)
1. **Warm-up phase incl. calibration run:** vehicle driven 90 minutes at V_high for tire/powertrain/drivetrain thermal stabilization; used also to calibrate vehicle-speed, air-speed, and yaw-angle signals. Ends with a controlled stop; torque sensors checked for drift and zeroed.
2. **First low-speed run:** after re-stabilizing (≥2 km at V_high), V_low test performed; straight-line, constant-speed driving through measurement sections required.
3. **High-speed run:** after re-stabilizing (≥2 km at V_high), V_high test performed under same straight-line/constant-speed conditions.
4. **Second low-speed run:** performed directly after the high-speed run.

Beginning/end of measurement sections identified via trigger signal (opto-electronic barriers + GPS) or recorded DGPS data. Additional quality checks include a post-test torque-sensor drift check.

### Post-Processing
- Average vehicle speed corrected using optical barrier or high-precision GPS data.
- Mobile anemometer air-flow signal corrected in three steps: (1) instrument error per calibration report, (2) position error (accelerated flow due to vehicle shape), (3) boundary-layer effect and yaw-angle misalignment.
- Invalid-condition data removed (excess wind, excess yaw angle, unstable torque).
- **Main evaluation: linear regression of traction force vs. squared air speed** — the quadratic term isolates the air-resistance contribution, giving Cd×A. Done per measurement-section/driving-direction combination, then averaged and corrected for average cross-wind using a generic body-type-dependent function.
- A standardized software tool, **VECTO-CSE**, was developed in LOT3 for this evaluation (see Part 4 of this knowledge base).

### 4.2.3.2. Repeatability, Reproducibility, Robustness

**Table 6 (Repeatability and reproducibility standard deviation of the method)** — reproduced:

| | Veh#1 Tests JRC | Veh#1 Tests OEM | Veh#2 Tests JRC | Veh#2 Tests OEM |
|---|---|---|---|---|
| Standard deviation | 1.6% | 1.8% | 1.1% | 1.4% |
| Repeatability std dev (σr) | 2.4% | | 1.8% | |
| Between-labs std dev | 1.7% | | 1.3% | |
| Reproducibility std dev (σR) | 2.9% | | 2.2% | |

Repeatability standard deviation range: **1.8%–2.4%**; reproducibility: **2.2%–2.9%**; the resulting **repeatability limit (r)** — value below which two results under repeatability conditions should differ with 95% probability — is estimated at **4.9%–6.7%** of the measured Cd×A value (Fontaras, 2014). Data were from an earlier, less refined version of the procedure; results were expected to improve with later refinements.

### 4.2.3.3. Open Issues (Air Drag Test)

1. **Influence of tire rolling-resistance behaviour on constant-speed test results:** the assumption of speed-independent RRC (10–90 km/h) at constant tire temperature was found **not fully valid** per data from tire OEMs and independent labs (Pflug, 2014; ETRTO, 2013). This affects both reproducibility and possibly biases the absolute Cd×A values.
   - Interim 2014 measures: (a) an "interim solution" test procedure — testing with empty vehicles (not standard-laden) to reduce RRC influence, possibly minimum-tread tires or a standardized tire model; (b) a special on-road RRC test rig (operated by CVE, Prof. Pflug); (c) an ACEA aero-group proposal for tire-drum testing (via ETRTO) to check drum-vs-track comparability.
2. **Family concepts** to reduce test burden — ACEA proposal existed but was not yet implemented in the Technical Annex.
3. **CFD (Computational Fluid Dynamics)** as a method to determine relative Cd×A differences between design variants — ongoing ACEA work; more code/settings harmonization needed before certification use (see Part 3 CFD sections).
4. **Vehicle-class-specific default Cd×A rules** discussed, e.g., default table values for class 16 (8x4 construction vehicles), where aero has minor fuel-consumption impact and vehicles have highly customer-specific bodies.

## 4.2.4. Transmission Test

Three options for assessing transmission losses (verbatim):
- **Option 1:** Fall-back values based on the maximum rated torque of the transmission.
- **Option 2:** Measured torque-independent losses, calculated torque-dependent losses — electric machine and torque sensor before transmission (output shaft free-rotating).
- **Option 3:** Measurement of total torque loss — electric machines and torque sensors in front of and behind the transmission.

*(Note: "electric machine" here refers to a dynamometer/electric motor used as **test-bench equipment** for measuring mechanical transmission losses — this is not an EV powertrain component. It should not be confused with vehicle traction e-motors.)*

The applicant may switch options per gear, even within one transmission. Details in the (separate) Technical Annex.

**Open issues:** family concept (proposed by ACEA, not yet implemented); possible oil-family concept; torque-sensor accuracy / error-analysis-concept definition.

## 4.2.5. Axle Test

Two options for axle losses:
- **Option 1:** Torque-loss table values (default values) based on generic constant efficiency and torque loss.
- **Option 2:** Test-bench measurement of torque-loss maps for each individual axle and ratio.

**Open issues:** family concept; verification of generic standard table values; reference test cycle to find "worst case oil" (for oil-family concept); handling design changes during an axle type's production cycle to reduce test effort.

## 4.2.6. Auxiliaries

Auxiliary systems provide energy for functions other than propulsion. In conventional vehicles they are driven mechanically by the ICE.

**Auxiliaries already implicitly covered by the engine fuel map** (not modeled separately): engine oil pump, coolant pump, fuel delivery pump, fuel high-pressure pump.

**Auxiliaries requiring individual modeling:** engine cooling fan, alternator, air compressor, steering pump, A/C compressor.

**Power take-off (PTO)** — not addressed in LOT3; relevant for e.g. garbage trucks, street cleaners; inclusion undecided.

### General Auxiliary Modeling Approach (Two-Step)
1. **Consumer demand ("supply power")** — e.g., electrical power required by electrical consumers.
2. **Efficiency of the auxiliary unit itself** (e.g., alternator efficiency map).

This structure was chosen specifically to allow future replacement of generic efficiency values with **component-specific test data**, once test procedures for individual auxiliaries are agreed. For trucks, auxiliaries were assessed to have secondary importance overall; simple methods (constant added power to the ICE) were used. For **buses**, auxiliary performance (especially HVAC) was found far more significant and complex — covered in a **separate parallel project** (not detailed in this report).

### 4.2.6.1. Engine Cooling Fan

Power demand determined as function of mission profile and fan technology (data from ACEA, checked by LOT3 consortium). No scaling with engine size (rated power) — ACEA recommendation, justified because fan contribution to overall FC is "smaller than 1% in most truck mission profiles."

**Table 7 (Power demand for the engine cooling fan, mechanical power [W])** — reproduced:

| Fan technology | Long haul | Regional delivery | Urban delivery | Municipal utility | Construction |
|---|---|---|---|---|---|
| Crankshaft mounted – Electronically controlled visco clutch | 618 | 671 | 516 | 566 | 1037 |
| Crankshaft mounted – Bimetallic controlled visco clutch | 818 | 871 | 676 | 766 | 1277 |
| Crankshaft mounted – Discrete step clutch | 668 | 721 | 616 | 616 | 1157 |
| Crankshaft mounted – On/Off clutch | 718 | 771 | 666 | 666 | 1237 |
| Belt driven or via transm. – electronically controlled visco clutch | 889 | 944 | 733 | 833 | 1378 |
| Belt driven or via transm. – bimetallic controlled visco clutch | 1089 | 1144 | 893 | 1033 | 1618 |
| Belt driven or via transm. – discrete step clutch | 939 | 994 | 883 | 883 | 1498 |
| Belt driven or via transm. – on/off clutch | 989 | 1044 | 933 | 933 | 1578 |
| Hydraulic driven – variable displacement pump | 738 | 955 | 632 | 717 | 1672 |
| Hydraulic driven – constant displacement pump | 1000 | 1200 | 800 | 900 | 2100 |
| Hydraulic driven – electronically controlled | 700 | 800 | 600 | 600 | 1400 |

### 4.2.6.2. Electric System / Alternator

Two characteristic numbers determine electric-system power demand:
1. **Power consumption of electric consumers** (generic table by mission profile & vehicle technology).
2. **Average electric efficiency of the alternator.**

**Table 8 (Draft table values for electric consumers [W])** — reproduced:

| | Long haul | Regional delivery | Urban delivery | Municipal utility | Construction |
|---|---|---|---|---|---|
| Baseline electric power consumption | 1240 | 1055 | 974 | 974 | 975 |
| Electric power saving tech 1: LED lights | -50 | -50 | -50 | -50 | -50 |
| Electric power saving technology 2 | t.b.d. | t.b.d. | t.b.d. | t.b.d. | t.b.d. |
| Additional consumer type 1 | t.b.d. | t.b.d. | t.b.d. | t.b.d. | t.b.d. |
| **Total average electric load (example)** | **1190** | **1005** | **924** | **924** | **925** |

**Alternator efficiency:** LOT3 received efficiency maps from **BOSCH** for "typical average" alternator technology; VECTO simulations of typical HDV configurations across mission profiles led to a suggested **average efficiency of 70%** for standard alternator technology. Bosch indicated alternator efficiency is not well predicted by design type alone; an alternative is a component-specific test (e.g., a "9-point test" adapted from **ISO 8854:2012**, weighted by a typical operation profile).

**Open issues (verbatim):** supplementation of the electrical-consumer/power-saving/additional-consumer table; finalization of standard alternator efficiency table; agreement on method for crediting higher alternator efficiency.

### 4.2.6.3. Air Compressor

Method largely adapted from an ACEA-published bus/coach model; LOT3 developed a simpler truck-specific approach.

**General method concept (buses, per ACEA, described for background):**
1. Compute flow-rate demand [m³/min] for pressurized-air consumers over the cycle (braking, suspension events) from generic table values (technology-dependent). **[Figure 11 description]:** schematic of generic pressurized-air consumption values (left table) and bus technology definitions.
2. Compute average compressor delivery rate from a characteristic line (volume flow = f(rpm)), using a first VECTO run to get average engine speed/rpm.
3. Compute **duty time** = air demand / delivery rate — the fraction of cycle time the compressor must run.
4. Split duty time into overrun (no extra FC) vs. traction phases (FC-relevant); smart compressors treated differently (more active during motoring).
5. Compute average compressor power from idling/full-load characteristic lines (**[Figure 12 description]:** schematic showing compressor power-demand curves — idling vs. full load — as a function of engine speed, source ACEA).

**Truck-specific simplified formula (LOT3, TUG):**
```
Mechanical power consumption of compressor [kW] = duty time [%] × power at full load [kW] + (100% − duty time) × power at idling [kW]
```
- Baseline air consumption [sl/min, standard litres/min] from **Table 9** (by HDV class × mission profile).
- Mechanical power = baseline air consumption × generic specific power demand of **0.02 [kW/(sl/min)]** (standard compressor technology).
- Worked example: a class 5 vehicle on long-haul mission → power consumption of compressors = **1.34 kW**.

**Table 9 (Baseline air consumption [sl/min])** — reproduced (dashes = not applicable/no data; "n.a." = not available for that class/mission combination):

| HDV class | Long haul | Regional delivery | Urban delivery | Municipal utility | Construction |
|---|---|---|---|---|---|
| 1 (Rigid/Tractor 7.5–10t) | — | 65 | 62 | — | — |
| 2 (Rigid/Tractor >10–12t) | 59 | 64 | 66 | — | — |
| 3 (Rigid/Tractor >12–16t) | — | 68 | 69 | — | — |
| 4 (Rigid >16t) | 65 | 67 | — | n.a. | — |
| 5 (Tractor >16t) | 67 | 91 | — | — | — |
| 9 (Rigid, all weights, 6x2/2-4) | 67 | 77 | — | n.a. | — |
| 10 (Tractor, all weights, 6x2/2-4) | 67 | 91 | — | — | — |

(Classes 6, 7, 8, 11–17: baseline air consumption not calculable — "no representative vehicle masses were available.")

**Open issues:** Table 9 values need consolidation with industry data and completion for missing classes; specific power demand (0.02 kW/(sl/min)) needs industry verification, possibly supplemented per compressor technology.

### 4.2.6.4. Steering Pump

Power demand split into four components (verbatim):
- **U(nloaded):** pumping oil without steering-pressure demand
- **F(riction):** pump friction (e.g., bearing)
- **B(anking):** steer correction due to road banking or side wind
- **S(teering):** power demand from cornering/manoeuvring

**Equation 1:**
```
Ptot = PU·CFU + PF·CFF + PB·CFB + PS·CFS
```
where: Ptot = total mechanical power demand [W]; Pi = power demand per component (Table 10, generic per vehicle class/mission profile, source ACEA Whitebook); CFi = technology-dependent scaling factor (Table 11; two technologies' numbers not finalized at report date).

### 4.2.6.5. A/C Compressor

Average power consumption allocated by HDV class × mission profile (ACEA data, verified by LOT3 using MAC-project methodology for LDV, Hausberger 2013; gaps filled by LOT3 adjustment from other classes).

**Table 12 (Average power demand of the A/C compressor, [W])** — reproduced:

| HDV class | Long haul | Regional delivery | Urban delivery | Municipal utility | Construction |
|---|---|---|---|---|---|
| 1 | — | 150 | 150 | — | — |
| 2 | 200 | 200 | 150 | — | — |
| 3 | — | 200 | 150 | — | — |
| 4 | 350 | 200 | — | 300 | — |
| 5 | 350 | 200 | — | — | — |
| 6 | — | — | — | 300 | 200 |
| 7 | — | — | — | — | 200 |
| 8 | — | — | — | — | 200 |
| 9 | 350 | 200 | — | 300 | — |
| 10 | 350 | 200 | — | — | — |
| 11 | — | — | — | — | 200 |
| 12 | — | — | — | — | 200 |
| 13 | — | — | — | — | 200 |
| 14 | — | — | — | — | 200 |
| 15 | — | — | — | — | 200 |
| 16 | — | — | — | — | 200 |
| 17 | — | — | — | — | 200 |

Note: A/C ventilation-system power demand is included under the electric-system power consumption (Table 8), not in Table 12.

---

*(Continued in Part 3: CO2 Test Cycles, Standard Bodies/Trailers, CFD Aerodynamics Studies, SiCo Validation Test, Sensitivity Analysis, and Proof of Concept)*
