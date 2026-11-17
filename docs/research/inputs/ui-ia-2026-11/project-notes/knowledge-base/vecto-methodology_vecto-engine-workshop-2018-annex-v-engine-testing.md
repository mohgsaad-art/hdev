# VECTO Engine — 2018 VECTO Workshop (JRC, Ispra, November 2018)

## Document Metadata

- **Title (as printed on document):** "VECTO Engine" — presentation for the **2018 VECTO Workshop**
- **Publisher/Author:** The European Commission's science and knowledge service — **Joint Research Centre (JRC)**
- **Location/Date:** Ispra, November 2018
- **Source filename in project:** `201811_engine_en.pdf`
- **Document type:** Workshop presentation slide deck (47 slides), not a full regulatory text itself — it explains and summarizes **Annex V to Commission Regulation (EU) 2017/2400**, and the associated **VECTO Engine pre-processing tool**.
- **Primary regulatory references named in the document:**
  - **Commission Regulation (EU) 2017/2400** (EU CO2/fuel-consumption certification of heavy-duty vehicles) — specifically its **Annex V** ("engine test procedure") and its **Appendices 1–8**
  - **UN/ECE Regulation No. 49 (UN/ECE R49)** — EURO VI pollutant emissions type-approval for heavy-duty engines
  - A **draft Commission Regulation amending Regulation (EU) 2017/2400** (referenced regarding the NG reference fuel "GR")
- No named individual authors or personal contact points appear in the extracted text. Publisher is identified only as "The European Commission's science and knowledge service, Joint Research Centre."

## Full Content Coverage Note

The project_read tool returned the complete text content of the PDF inline (all 47 slides, page markers 1–47 visible in the source). This file reproduces that content in full, slide by slide, reorganized under topical headers per the deck's own table of contents. Nothing was extrapolated beyond what is printed; slide numbers are preserved for traceability. Figures/diagrams that are visual-only (torque-speed grids, GUI screenshots, XML screenshots) are described in words since only their labels/annotations were extracted as text, not the visual layout itself.

---

## Agenda / Table of Contents (Slide 2)

1. Basic principles of engine test procedure
2. Overview of content of engine test procedure (Annex V to Commission Regulation (EU) 2017/2400)
3. Details of engine test procedure
4. Engine pre-processing tool (VECTO Engine)
   - Description of tool and input data
   - Steps of data evaluation
   - VECTO Engine software demonstration
5. Common mistakes
6. Special topic: from measured FC to certified CO2
7. Q&A (ca. 15 min)

---

## 1. Basic Principles of Engine Test Procedure (Slide 4)

- Close link to emission testing for type approval (**EURO VI / UN/ECE R49**) — the goal is **minimum additional testing effort** while ensuring compliance with emission limits (framed as a trade-off between emissions and fuel consumption).
- **Overview of necessary test runs:**
  - Engine full load curve
  - Engine motoring curve
  - **WHTC** (World Harmonized Transient Cycle) — cold + hot
  - **WHSC** (World Harmonized Stationary Cycle) — for Conformity of Production (CoP) only
  - **Engine fuel-flow map**: fuel-flow = f(speed, torque) — described as a **dedicated new test run created specifically for CO2 declaration** (i.e., not part of the pre-existing UN/ECE R49 emissions testing regime)
- **Boundary conditions for the engine fuel-flow map:**
  - Stationary measurement of fuel-flow at a predefined grid of operating points
  - Defined sequence of measured points
  - Compliance with emission limits is checked according to **extended WNTE/OCE requirements** (World-harmonized Not-To-Exceed / Off-Cycle Emissions)
  - The fuel-flow map is valid for the **whole engine CO2-family** (not just the single tested engine)
- All test runs except the fuel-flow map are per **UN/ECE R49** (unchanged); the fuel-flow map is the new addition.

---

## 2. Overview of Content of Annex V to Commission Regulation (EU) 2017/2400 (Slides 6–7)

### Main body structure of Annex V (Slide 6)
1. Introduction
2. Definitions
3. General requirements (for all test runs)
4. Testing procedure
   - 4.3.1 Full load curve
   - 4.3.2 Motoring curve
   - 4.3.3 WHTC
   - 4.3.4 WHSC
   - 4.3.5 Fuel consumption mapping cycle (FCMC)
5. Post-processing of measurement data
6. Application of engine pre-processing tool

(Noted as "mainly relevant for engine testing, data evaluation, certification issues.")

### Appendices to Annex V (Slide 7)
1. Model of certificate
2. Engine Information Document
3. Engine CO2-Family
4. Conformity of the certified CO2 emissions and fuel consumption related properties
5. Determination of power consumption of engine components
6. Markings
7. Input parameters for the simulation tool
8. Important evaluation steps and equations of the engine pre-processing tool

(Also noted as "mainly relevant for engine testing, data evaluation, certification issues.")

---

## 3. Details of Engine Test Procedure

### 3.1 General Information about the Engine Test Procedure (Slides 9–10)

Close link to the emission test procedure (EURO VI / UN/ECE R49); minimum additional testing effort. **Amendments of Commission Regulation (EU) 2017/2400 to UN/ECE R49:**

- **Stricter limits for ambient conditions** [Point 3.1.1 of Annex V]
- Engine installation according to UN/ECE R49, with **correction of AUX** — special provisions for additional electric auxiliaries and fan (see Appendix 5) [Point 3.1.2 of Annex V]
- **Special provisions for the engine cooling system on the testbed** [Point 3.1.5 of Annex V]:
  - A thermostat (or simulated equivalent behavior on the testbed) shall be used
  - The in-vehicle situation shall be reproduced (temperatures, flow rates)
  - Extra rules for WHTC cold-start
- **Reference fuels of the EURO VI regulation** are used for testing [Point 3.2 of Annex V]:
  - Procedure and standards for determination of **Net Calorific Value (NCV)** are defined
  - The exact same reference fuel shall be used for all test runs of one engine CO2-family, with exceptions for gas fuels (handled in smaller amounts in gas cylinders)
- **Special provisions for lubricants used** [Point 3.3 of Annex V]: regular market oils only; no special (e.g., low-friction) oils allowed
- **More stringent requirements on accuracy of measurement equipment** [Point 3.5 of Annex V]

### 3.2 Selection of Engine to be Tested (Slides 11–12)

**Engine CO2-family concept:**
- An engine emission family definition already exists for EURO VI (per UN/ECE R49)
- The **engine CO2-family is a (smaller) subset** of the engine emission family
- The engine CO2-family is defined by fuel-consumption-affecting parts (hardware and controls)
- If any of these parts change, a **different family** is created

[Figure, Slide 11 description]: A hierarchy diagram — one "engine emission family (per UN/ECE R49)" splits into multiple CO2-families ("CO2-family 1" ... "CO2-family n"), and each CO2-family contains multiple member engines at different power ratings (example shown: CO2-family 1 contains engines C1.1/C1.2/C1.3 at 300kW/250kW/200kW; CO2-family n contains engines Cn.1/Cn.2/Cn.3 at 350kW/300kW/250kW).

**Selection rules (Slide 12):**
- For each CO2-family, **only one engine has to be measured: the highest power rating**
- All lower ratings of a family use the **same measured fuel-flow map**
- The highest rating **defines the grid size** of the fuel-flow map
- On OEM request, additional members of a CO2-family may be measured separately

[Figure, Slide 12 description]: Torque-speed chart showing the fuel-flow map grid for the engine with the highest power in the family; example grid spacing shown as Δ = 85 Nm.

### 3.3 Engine Installation on Testbed (Slide 13)

Compares power demand handling of auxiliaries between the VECTO vehicle simulation and the UN/ECE R49 testbed FC-mapping setup:

| Auxiliary system | VECTO vehicle simulation | Testbed (per UN/ECE R49) FC mapping |
|---|---|---|
| Fuel pump(s), water pump, oil pump | No additional consideration (already included in FC map) | Installed (included in FC map) |
| Generator (supply of electrical system) | Generic power demand per vehicle class/mission profile added in simulation* | Not installed (or power correction) — not included in FC map |
| Fan, steering pump, air compressor, AC compressor | Generic power demand per vehicle class/mission profile added in simulation* | Not installed (or power correction) — not included in FC map |

\* Detailed simulation of auxiliary power demand applies specifically for buses.

Key logic: power demand of auxiliaries **already installed** during fuel-flow mapping is already embedded in the FC map and needs no further vehicle-simulation adjustment. Power demand of auxiliaries **not installed** during mapping is added back generically per vehicle class/mission profile in the VECTO vehicle simulation.

### 3.4 Overview of Test Runs to Be Performed (Slide 14)

- **5 test runs in total.**
- **2 of those can be skipped** for "child" engines within the same engine CO2-family (only the CO2-parent engine needs the full set).
- All test runs except one are per UN/ECE R49 unchanged; the exception is the **fuel consumption mapping cycle (FCMC)**, a dedicated new test run for CO2 declaration.

| Test run | Reference paragraph | Required for CO2-parent engine | Required for other engines within CO2-family |
|---|---|---|---|
| Engine full load curve | 4.3.1 | yes | yes |
| Engine motoring curve | 4.3.2 | yes | no |
| WHTC test | 4.3.3 | yes | yes |
| WHSC test | 4.3.4 | yes | yes |
| Fuel consumption mapping cycle | 4.3.5 | yes | no |

### 3.5 Fuel Consumption Mapping Cycle (FCMC) — Details (Slides 15–18)

#### FCMC (1/4) — Target engine speed setpoints [Point 4.3.5.2.1 of Annex V] (Slide 15)

1. **4 base speeds:**
   - n_idle
   - n_A
   - n_B
   - n_95h
2. **6 additional speeds**, equidistant between the base speeds.
- Standard distribution is **4/4 equidistant sections** between the base speed pairs, but this can change to **3/5 or 5/3** depending on the shape of the full load curve.

[Figure 15 description]: Torque (y-axis, 0 to Tmax_overall) vs. engine speed (x-axis) chart, with vertical markers at n_idle, n_A, n_B, n_95h. Two groups of "4 equidistant sections" are shown between n_idle–n_A and between n_B–n_95h (example of the 4/4 distribution).

#### FCMC (2/4) — Target torque setpoints [Point 4.3.5.2.2 of Annex V] (Slide 16)

- **10 equidistant intervals** between 0 Nm and the highest torque value that occurs in the full load curve.
- Points located above the full-load line are replaced by the full-load value itself — but points at full load are only measured once (sets of points converge to a single full-load target torque point).

[Figure 16 description]: Torque-speed chart showing 10 equidistant horizontal torque sections from 0 to Tmax_overall, with example sets of points near/above the full-load curve being combined into single full-load target points.

#### FCMC (3/4) — Target torque setpoints, tolerance replacement [Point 4.3.5.2.2 of Annex V] (Slide 17)

- Points located above a **tolerance limit defined as "full load torque minus 5% of Tmax_overall"** (shown as a red dotted line) are replaced by the full-load value.
- Again, points at full load are only measured once.

[Figure 17 description]: Same torque-speed chart as slide 16, with an added red dotted line at "full load torque − 5% Tmax_overall," illustrating which near-full-load points get replaced by the full-load curve value.

#### FCMC (4/4) — Test sequence [Point 4.3.5.5 of Annex V] (Slide 18)

- **Preconditioning:** 20 minutes at WHSC preconditioning mode 9.
- **Ramp time:** 20 seconds for a load change at constant speed (20–46 seconds for combined speed-and-load changes).
- **Stabilization time:** 55 seconds at each point.
- **Averaging (measurement) time:** 30 seconds at each point.

[Figure 18 description]: Timeline diagram of one FCMC test point cycle: "Phase start" → Transition period (ramp) → **Stabilization period: 55±1 seconds** → **Measurement period (Data recording): 30±1 seconds** → Post-processing period: 10±1 seconds → Transition period (ramp) → "Phase end," with a total phase duration annotated as **95±3 seconds**. Also shown separately: a torque-speed chart with a path from "Start" to "Finish" tracing across the full-load curve region as the sequence of setpoints is executed.

### 3.6 Data Post-Processing (Slides 19–23)

**VECTO-Engine pre-processing tool is mandatory for post-processing of measurements.**

#### Overview table of test-run purposes (Slide 19)

| Test run | Input for VECTO Engine | Input for VECTO vehicle simulation | Other purpose |
|---|---|---|---|
| Full load curve (per UN/ECE R49) | Generation of input file for VECTO; full-load curve for simulation of WHTC (calculation of WHTC-CF) | Full-load curve for vehicle simulation | Generation of reference cycle for testbed |
| Motoring curve (per UN/ECE R49 Annex 4, paragraph 7.4.7 option (b)) | Generation of input file for VECTO; motoring curve for simulation of WHTC (calculation of WHTC-CF) | Motoring curve for vehicle simulation | — |
| WHTC (cold + hot) (per UN/ECE R49) | Specific FC in g/kWh for calculation of correction factors: (1) measured g/kWh FC over 3 separate parts of hot WHTC; (2) measured g/kWh FC over total cold+hot WHTC; (3) CF for periodically regenerating DPFs | Correction factors (WHTC-CFs, cold-hot balancing, periodically regenerating DPFs) | Check compliance with emission limits |
| Fuel-flow mapping (FCMC) | Generation of input file for VECTO; fuel-flow map for simulation of WHTC (calculation of WHTC-CF) | Fuel-flow map for vehicle simulation | — |
| WHSC (per UN/ECE R49) | — | — | For conformity of CO2 emissions and fuel consumption related properties purpose only (Appendix 4 of Annex V) |

#### Data post-processing (2/5) — WHTC correction factors [Points 5.1–5.3.1 of Annex V] (Slide 20)

- **Purpose:** to correct the stationary fuel-flow map in simulation for (1) transient engine operation, and (2) inconsistencies in fuel consumption between the WHTC (hot part) and the stationary fuel-flow map (e.g., due to optimization at the cost of higher pollutant emissions, or heating strategies).
- **Input data format:** FC in g/kWh as an integrated value over 3 different WHTC parts (urban, rural, motorway).
- **3 WHTC correction factors** (urban, rural, motorway) are calculated automatically in the pre-processing tool:

**Formula:**
```
WHTC-CF_i = (g/kWh measured) / (g/kWh interpolated from map)
```
where *i* denotes each of the three WHTC parts (urban, rural, motorway).

#### Data post-processing (3/5) — Cold-hot balancing factor [Point 6 of Appendix 8 to Annex V] (Slide 21)

**Formula:**
```
BF_cold-hot = 1 + 0.1 × (g/kWh measured,cold − g/kWh measured,hot) / g/kWh measured,hot
```
- Purpose: balancing of FC between cold and hot WHTC — a **penalty factor** to avoid shifting pollutant emissions to the cold test in exchange for lower FC in the hot test.
- Calculated automatically in the pre-processing tool.
- **Lower limit for BF_cold-hot is set to 1** (i.e., the factor cannot reduce FC below the hot-test value).

#### Data post-processing (4/5) — Correction factor for periodically regenerating DPFs [Point 5.4 of Annex V] (Slide 22)

- WHTC tests are repeated until a regeneration event occurs; additional FC for periodically regenerated DPFs must be accounted for.
- Definition of "periodically regenerated DPFs" per UN/ECE R49.

**Formula:**
```
CFRegPer = [ n × (avg g/kWh all WHTC w/o_reg) + n_r × (avg g/kWh all WHTC with_reg) ] / (n + n_r)
```
where:
- **n** = number of WHTC hot-start tests without regeneration
- **n_r** = number of WHTC hot-start tests with regeneration (minimum number is 1)

[Figure 22 description]: Sequence diagram showing "1. WHTC," "2. WHTC," "3. WHTC," then "WHTC with reg." with "Reg. finished" marked, illustrating repeated hot-start WHTC runs until a regeneration event is captured.

#### Data post-processing (5/5) — Emission monitoring in the engine test procedure (Slide 23)

- **Part 1:** Tests in WHTC must comply with Euro VI limits for pollutant emissions.
- **Part 2:** Screening of the FCMC according to **extended WNTE/OCE** [Points 4.3.5.6 and 4.3.5.7 of Annex V]:
  - For each cell (grid point), the measured specific emissions in g/kWh for each FCMC point are averaged.
  - Each cell is evaluated independently.
  - Averaged emissions of each cell must comply with Euro VI WNTE/OCE emission limits.
  - The lower boundary of the control area is defined by the engine with the lowest rating in the CO2-family.

[Figure 23 description]: Torque-speed grid (numbered cells 1–9 visible in extracted labels) depicting the WNTE/OCE control-area screening grid over the FCMC operating map.

---

## 4. Engine Pre-Processing Tool (VECTO Engine)

### 4.1 Basic Features (Slide 25)

- Written in **VB.net**
- **Portable application** — no installation required
- **File format conventions** [Point 6 of Annex V]:
  - **CSV** (Comma Separated Values) file type
  - List separator is **Comma ","**
  - Decimal separator is **Dot "."**
- Per **Commission Regulation (EU) 2017/2400**, the use of VECTO Engine is **mandatory**.
- Output is **one single XML file**, already hashed, ready for use in the VECTO vehicle simulation for declaration.

### 4.2 Overview of Input Data (Slide 26)

**Input files required** [Point 6]:
- FC map of the CO2-parent engine
- Full load curve of the CO2-parent engine
- Full load curve of the actual engine to be certified
- Motoring curve of the CO2-parent engine

**Input values required in GUI** [Point 6]:

| Category | Fields |
|---|---|
| Manufacturer / identification | Manufacturer; Engine model name; Certification number |
| Fuel | Type of test fuel; NCV of test fuel |
| CO2-parent engine data | Idle speed of the CO2-parent engine; Engine idle speed; Engine displacement; Engine rated power; Engine rated speed |
| Correction data | Specific FC figures in g/kWh; CFRegPer |

(Note: table columns are as extracted; "Engine idle speed" and "Idle speed of the CO2-parent engine" both appear as distinct listed fields in the source slide.)

### 4.3 Input File Formats (Slides 27–28)

**Input file "FC map of CO2-parent engine"** [Point 6.1.4 of Annex V] — CSV file type:

| Signal | Unit | Number of decimal places | Remarks |
|---|---|---|---|
| Engine speed | [min⁻¹] | 2 | - |
| Engine torque | [Nm] | 2 | - |
| Fuel mass flow | [g/h] | 2 | - |

**Input files "Full load curve" and "Motoring curve"** [Points 6.1.1 to 6.1.3 of Annex V] — CSV file type:

| Signal | Unit | Number of decimal places | Remarks |
|---|---|---|---|
| Engine speed | [min⁻¹] | 2 | - |
| Engine torque | [Nm] | 2 | - |

(Both slides note "Example" alongside the table, referring to an illustrative CSV excerpt shown in the original slide but not reproduced as extractable text.)

### 4.4 Overview of Evaluation Algorithms (Slides 29–31)

**Step 1:** Reading of input files and automatic check of input data as set out in Annex V to Commission Regulation (EU) 2017/2400.

**Step 2:** Calculation of characteristic engine speeds (for denormalization of test cycles) from full load curves of the CO2-parent engine and the actual engine for certification.

**Step 3:** Processing of the fuel consumption (FC) map:
- Add FC values below n_idle to the map
- Add FC values above n_95h to the map
- Extrapolation of FC values to cover knees in the full load curve
- Adding of FC = 0 g/h at the motoring curve at all engine speed setpoints in the map
- Adding of FC = 0 g/h below the motoring curve at all engine speed setpoints in the map

**Step 4:** Simulation of FC and cycle work over the WHTC and respective subparts for the actual engine for certification.

**Step 5:** Calculation of WHTC correction factors.

**Step 6:** Calculation of cold-hot emission balancing factor.

**Step 7:** Correction of FC values in the FC map to standard NCV:
```
FCcorrected = FCmeasured × NCVmeas / NCVstd
```
- **No correction is performed for Diesel fuel (B7).**

**Step 8:** Conversion of engine full load and motoring curve data to a logging frequency of engine speed of **8 min⁻¹** for the XML output (only performed if the average logging frequency of the input data is **< 6 min⁻¹**).

[Figure, Slide 31 description]: Example diagram illustrating data processing through VECTO Engine specifically for the FC map (visual example of before/after grid processing; text detail not extractable beyond the caption).

### 4.5 VECTO Engine — Software Demonstration (Slides 32–37)

**Slide 32 — Download package:**
- Content of the VECTO Engine package as downloaded from the JRC server can be copied to any location on a PC/server.
- Package contents: Demo dataset; User Manual; Executable (just double-click to start).

**Slide 33 — General GUI elements:**
- Message window
- Input fields for component data
- Input fields for component files
- Input fields for specific FC figures and CFRegPer
- Input field for output directory
- Control buttons

**Slide 34 — Test evaluation (1/3), workflow steps:**
1. Input all component data
2. Browse for input files
3. Input all values for specific FC figures and CFRegPer
4. Browse for output directory
5. Press the green "Start" button for full data evaluation (option: "Precalculate" — see next slide)
6. Status of evaluation displayed in message window; upon completion, a VECTO XML input file is created.

**Slide 35 — Test evaluation (2/3), Precalculate feature:**
- For precalculation of the grid for the fuel map **before** the FCMC test run, only 2 inputs are needed:
  - Idle speed of the CO2-parent engine
  - Full load curve of the CO2-parent engine
- Press the grey "Precalculate" button to precalculate the grid for the fuel map from the CO2-parent full-load curve; result is displayed in the message window.

**Slide 36 — Test evaluation (3/3), further remarks:**
- Messages displayed give clear explanations for all relevant errors (referencing the regulation or indicating the specific datapoint).
- **Warnings vs. Errors:**
  - A valid XML results file is **only created if no errors occur** (i.e., no non-conformity with regulation requirements).
  - Warnings give a hint that something might be wrong with the input data; the XML result file remains valid despite warnings, **but** warnings should be investigated together with the Type-Approval Authority (TAA) / technical service.
- Only one single XML file is created as output; it is already hashed and ready for use in the VECTO vehicle simulation for declaration.

**Slide 37 — Example XML input file for VECTO:**
- The XML file is already hashed by the VECTO Engine pre-processing tool.
- Sections referenced: "Beginning of section for full load and motoring data" and "Beginning of section for FC data" (example XML excerpt shown in original slide, not reproduced as extractable text beyond these section labels).

---

## 5. Common Mistakes (Slides 39–40)

### Common mistakes (1/2) — Slide 39
- The correct distribution of intervals for target engine speed setpoints [Point 4.3.5.2.1 of Annex V] is checked by VECTO-Engine using points at 0 Nm torque.
- Points outside the measurement tolerance range [Point 4.3.5.5 of Annex V] are not considered in this check.
- **Error message:** states that the "number of points located in interval 'n_idle – n_A' or 'n_B – n_95h' is incorrect" (with an additional hint to check the tolerance for 0 Nm points).

[Figure 39 description]: Same style torque-speed chart as slide 15 (4/4 distribution example), annotated with the "area where correct distribution of intervals is evaluated" and the "tolerance range for engine speed and torque" per subpoints 1(a) and 1(b) of point 4.3.5.5 to Annex V.

### Common mistakes (2/2) — Slide 40
- Correct location of measured FC map points is checked by VECTO-Engine [Point 4.3.5.2.2 of Annex V].
- Points located very close to full load (above the tolerance limit) are replaced by full load.
- **Error message:** otherwise states "invalid torque value in FC map (at xxx [rpm] yyy [Nm])" exists, and that the "expected torque value = full load."

[Figure 40 description]: Same torque-speed chart as slides 16/17 (10 equidistant sections, red dotted tolerance line at full-load torque minus 5% of Tmax_overall), illustrating points replaced by full load.

---

## 6. Special Topic: From Measured FC to Certified CO2 (Slides 42–45)

### From measured FC to certified CO2 (1/3) — Slide 42

Sequence: **Engine component certification (Measurement → VECTO-Engine automatically) → VECTO vehicle certification.**

**Step A — Standardization to reference NCV for engine test** (*not performed for Diesel fuel B7*):
```
FCcorr_1 = FCmeas × NCVmeas / NCVStdEngine
```

**Step B — Standardization to reference NCV for vehicle simulation:**
```
FCcorr_2 = FCcorr_1 × NCVStdEngine / NCVStdVECTO
```

Variable definitions:
- **NCVmeas** = Net calorific value of the fuel used during testing [Point 5.3.3.1 to Annex V]
- **NCVStdEngine** = Standard net calorific values of fuel types [Point 5.3.3.1 to Annex V]
- **NCVStdVECTO** = Net calorific value defined as the reference value for vehicle CO2 certification

### From measured FC to certified CO2 (2/3) — Slide 43

**Step C — Application of correction factors** (WHTC-CF weighted, cold-hot balancing, periodically regenerating DPFs):
```
FCcorr_3 = FCcorr_2 × CFi
```

**Step D — Application of CO2 factors** (kg CO2 per kg fuel used):
```
CO2final = FCcorr_3 × fCO2
```

Variable definitions:
- **CFi** = Combined correction factor (= WHTC-CF × BFcold-hot × CFRegPer)
- **fCO2** = Standard factors for kg CO2 per kg fuel combustion in VECTO

### From measured FC to certified CO2 — Details on WHTC correction factor (Slide 44)

- WHTC-CFs are calculated for the 3 different WHTC parts (urban, rural, motorway) automatically in VECTO-Engine (as described on slide 20).
- The **weighted WHTC correction factor** is calculated for each vehicle automatically in the VECTO vehicle simulation, using WHTC weighting factors defined per mission profile:

```
CFvehicle = CFurban × WFurban + CFrural × WFrural + CFmotorway × WFmotorway
```

**WHTC weighting factors by mission profile:**

| Mission profile | WFmotorway | WFrural | WFurban |
|---|---|---|---|
| Long haul | 89% | 0% | 11% |
| Regional | 53% | 30% | 17% |
| Urban | 4% | 27% | 69% |
| Municipal utility | 2% | 0% | 98% |
| Construction | 6% | 32% | 62% |
| City bus | 0% | 0% | 100% |
| Interurban bus | 19% | 36% | 45% |
| Coach | 78% | 22% | 0% |

### Annex: Fuel Properties (Slide 45)

**Table 4 of Annex V to Commission Regulation (EU) 2017/2400** — values noted as valid "in VECTO until V3.3.0.1250"; the slide notes figures "might be revised in release Dec 2018" and that "LNG to be added."

| Engine Fuel Type | Reference Fuel | Density [kg/m³] | CO2 content [g_CO2/g_Fuel] | Lower Heating Value [MJ/kg] |
|---|---|---|---|---|
| Diesel / CI | B7 | 836 | 3.13 | 42.7 |
| Ethanol / CI | ED95 | 820 | 1.83 | 25.7 |
| Petrol / PI | E10 | 750 | 3.04 | 41.5 |
| Ethanol / PI | E85 | 786 | 2.09 | 29.1 |
| LPG / PI | LPG Fuel B | not required | 3.02 | 46.0 |
| NG / PI | G25 (fuel for testing, representing typical CNG real-world fuel) | not required | 2.54 | 45.1 |

Additional note on this slide: "GR" is proposed as a reference fuel for NG by a **draft Commission Regulation amending Regulation (EU) 2017/2400** (i.e., a proposed additional/alternative reference fuel for natural gas, beyond G25, under an amendment then in draft).

---

## 7. Q&A

Slide 46 repeats the full agenda list, and slide 47 is the closing "Q&A (ca. 15 min)" marker with no further extractable text content (end of deck).

---

## Cross-References Named in This Document (exact, as printed)

- Commission Regulation (EU) 2017/2400 — Annex V (all points/sub-points cited: 3.1.1, 3.1.2, 3.1.5, 3.2, 3.3, 3.5, 4.3.1–4.3.5, 4.3.5.2.1, 4.3.5.2.2, 4.3.5.5, 4.3.5.6, 4.3.5.7, 5, 5.1–5.3.1, 5.3.3.1, 5.4, 6, 6.1.1–6.1.4, Appendix 4, Appendix 5, Appendix 8 Point 6, Table 4)
- UN/ECE Regulation No. 49 (UN/ECE R49), including Annex 4, paragraph 7.4.7 option (b)
- Draft Commission Regulation amending Regulation (EU) 2017/2400 (referenced only regarding the "GR" NG reference fuel proposal — no further detail given)

## Organizations Named

- European Commission's science and knowledge service — **Joint Research Centre (JRC)** (document publisher; also the source of the VECTO Engine software download package, "JRC server")
- Type-Approval Authority (TAA) / technical service (referenced as the party warnings should be investigated with)

## Items Marked Unclear / Not Extractable as Text

- Exact visual layout/values of the example CSV excerpts on slides 27–28 [unclear from source — only column headers/units/decimal-place counts were extracted as text, not the numeric example rows]
- Exact visual content of the "example of data processing through VECTO Engine for FC map" diagram on slide 31 [unclear from source — caption only]
- Exact visual content of the example XML file screenshot on slide 37 beyond the two section-label callouts [unclear from source]
- Named individual presenter(s)/author(s) of the slide deck [unclear from source — not stated; only "Joint Research Centre" as institutional source]
- Full text of Annex V Introduction, Definitions, and full formal legal wording — this document is a workshop summary/presentation, not the regulation text itself; only the points explicitly referenced in the slides are covered here.

---

## Relevance to HDEV Sizing & Modelling Tool Project

This document is directly relevant to the project's goal of a realistic, auditable HDEV sizing/simulation tool ("PVsyst for EVs"), specifically for anyone building or interpreting **VECTO-style engine input data or fuel-consumption/CO2 methodology** as a reference point for conventional/hybrid HDV baselines or for methodological rigor in an analogous HDEV (electric) tool:

- Establishes the **official EU methodology** (Annex V to (EU) 2017/2400) for generating engine fuel-consumption maps, full-load/motoring curves, and correction factors (WHTC-CF, cold-hot balancing, DPF regeneration) that feed into VECTO's vehicle-level CO2/fuel-consumption simulation.
- Documents the **mission-profile-specific WHTC weighting factors** (long haul, regional, urban, municipal utility, construction, city bus, interurban bus, coach) — a precedent for how mission-profile-specific weighting could analogously be structured for an HDEV energy-consumption tool.
- Details the **auxiliary power handling convention** (which auxiliaries are embedded in the base map vs. added generically per vehicle class/mission profile in simulation) — directly relevant to how an HDEV tool should treat auxiliary loads (HVAC, compressors, etc.) distinctly from traction energy.
- Provides the **exact fuel property reference table** (density, CO2 content, LHV) for diesel, ethanol, petrol, LPG, and NG reference fuels — useful as an authoritative baseline if the HDEV tool needs to benchmark against or convert from conventional ICE HDV fuel consumption figures.
- All figures above are as explicitly stated in this JRC document; none have been extrapolated, and the note on slide 45 that fuel-property values "might be revised in release Dec 2018" and that LNG was still to be added should be flagged if these values are used for any current-year comparison — the actual current VECTO fuel property table should be re-verified against the live VECTO documentation before use, since this source is dated November 2018.
