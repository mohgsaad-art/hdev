# ANNEX Xa — Conformity of Simulation Tool Operation and of CO2 Emissions and Fuel Consumption Related Properties of Components, Separate Technical Units and Systems: Verification Testing Procedure

**Source document:** Commission Regulation (EU) 2017/2400 of 12 December 2017 implementing Regulation (EC) No 595/2009 of the European Parliament and of the Council as regards the determination of the CO2 emissions and fuel consumption of heavy-duty vehicles and amending Regulation (EU) No 582/2011 of the European Parliament and of the Council
**CELEX number:** 02017R2400
**Consolidated text as of:** 01.01.2026 (consolidation version "007.001")
**Exact range covered by this file:** Lines 17297–18784 of the extracted OCR text = Annex Xa in full (Introduction through Appendix 1, Part B), i.e. pages 02017R2400 — EN — 01.01.2026 — 007.001 — 417 through 447.
**Amendment markers visible in this range:** ►B (2017 baseline — note: almost the entirety of Annex Xa in this consolidated text carries ►M3 or ►M4 markers; no unmarked/pure ►B text was found in this range), ►M3 (Reg (EU) 2022/1379), ►M4 (Reg (EU) 2025/258). No ►M1 or ►M2 markers appear in this specific range.

## Transcription / OCR notes (read first)

This file is a faithful transcription of the source text extracted via OCR from the consolidated EUR-Lex PDF. The OCR process corrupted mathematical/typographic symbols throughout the formula-heavy sections (Annex Xa points 5.7, 7.2.2, 7.3 and Appendix 1). Based on context and standard VECTO/EU regulatory typesetting conventions, the following character substitutions are evident:

| OCR artifact | Evident meaning |
|---|---|
| `¼` | `=` (equals sign) |
| `þ` | `+` (plus sign) |
| `Ä` | `–` / `-` (minus sign or en-dash, context dependent) |
| `ð` `Ò` / `Þ` | `(` and `)` (parentheses) |
| `Ê` `Ì` `Í` `Î` `Ö` `É` | fraction-bar / bracket rendering artifacts |
| `X2 i¼1`, `Ptend tstart`, `Pn i¼1` | summation symbol **Σ** with sub/superscript bounds, rendered sequentially instead of stacked |
| `•` / `·` | `×` (multiplication) |
| `π` | π (pi) — rendered correctly |

For every formula below, the **raw OCR string is quoted first** in a code block (for audit traceability against the source PDF), followed by a **reconstructed, cleaned equation**. The reconstruction is a direct, mechanical un-garbling of OCR artifacts using the variable list the Regulation itself provides immediately under each equation — it introduces no new values, assumptions or substantive content. Nonetheless, per project instructions, this is flagged explicitly as an OCR reconstruction and should be checked against the primary PDF (page images) before being relied upon for implementation in the sizing tool.

Figures referenced in the source text but not present as actual images in this text-only OCR extraction are flagged inline as: *[Figure referenced in source but not visually extracted from this text-only OCR]*.

---

## 1. Introduction (point 1) ▼M4 / ▼M3

This Annex sets out the **verification testing procedure (VTP)** — the test procedure for verifying the CO2 emissions of **new** heavy-duty vehicles after they have entered production (i.e., it is a post-production conformity check, distinct from the type-certification simulation performed under Annex III/other Annexes before market placement).

Key structural facts (▼M4):
- The VTP consists of an **on-road test** to verify the CO2 emissions of new vehicles after production.
- It is **carried out by the vehicle manufacturer** and **supervised by the approval authority** that granted the licence to operate the simulation tool.
- For **heavy buses**, the VTP is performed by the manufacturer of the **primary vehicle** (i.e., the chassis/incomplete-vehicle manufacturer, not necessarily the bodybuilder of the completed vehicle).
- During the VTP, the following are measured: torque and speed at the driven wheels, engine speed, fuel consumption, pollutant emissions, and other relevant parameters listed in point 6.1.6 (Table 4).
- The measured data are used as **input to the simulation tool**, together with the vehicle-related input data and the input information from the original CO2/fuel-consumption determination of the vehicle.
- For the VTP simulation specifically, the **instantaneously measured wheel torque and rotational speed of the wheels**, as well as **engine speed**, are used as simulation inputs (this is a "backward"-style simulation driven by measured wheel/engine signals, not by a driving cycle).
- **Pass condition:** the CO2 emissions calculated from the measured fuel consumption must be within the tolerances set out in point 7 (see Section 7 below), compared to the CO2 emissions from the VTP simulation.
- **Figure 1** — "Schematic picture of the verification testing procedure method" — is referenced in the source (▼M3) immediately after the introduction text. *[Figure referenced in source but not visually extracted from this text-only OCR]*
- The detailed evaluation steps performed by the simulation tool in the VTP simulation are set out in **Appendix 1** to this Annex (see Section 9 below).

**▼M3 addition:** As part of the VTP, the **correctness of the vehicle input data set** from the original CO2/fuel-consumption certification of components, separate technical units (STUs) and systems is also reviewed, to check the data and the data-handling process. The correctness of input data relating to components/STUs/systems relevant for **air drag** and for **rolling resistance** of the vehicle is verified in accordance with point 6.1.1.

---

## 2. Definitions (point 2) ▼M3/▼M4

For the purposes of this Annex:

1. **"verification test relevant data set"** — a set of input data for components, STUs and systems, and input information, used for CO2 determination of a verification-testing-procedure-relevant vehicle.
2. **"verification testing procedure relevant vehicle"** — a new vehicle for which a value of CO2 emissions and fuel consumption was determined and declared in accordance with **Article 9**.
3. **"corrected actual mass of the vehicle"** — as defined in **Annex III, point 2(4)**.
4. **"actual mass of the vehicle for VTP"** (▼M4) — the actual mass of the vehicle as defined in **Article 2(6) of Regulation (EU) 2021/535**, but with a **full tank** plus the **additional measurement equipment** set out in point 5, plus the actual mass of the trailer or semitrailer in accordance with point 6.1.4.1.
5. **"actual mass of the vehicle for VTP with payload"** — the actual mass of the vehicle for VTP with the payload applied in the VTP as set out in point 6.1.4.2.
6. **"wheel power"** — the total power at the driven wheels of a vehicle to overcome all driving resistances at the wheel, computed in the simulation tool from the **measured torque and rotational speed of the driven wheels**.
7. **"controller area network signal" / "CAN signal"** — a signal from the connection with the vehicle electronic control unit as referred to in point 2.1.5 of Appendix 1 to Annex II to **Regulation (EU) No 582/2011**.
8. **"urban driving"** — total distance driven during the fuel consumption measurement at speeds **not exceeding 50 km/h**.
9. **"rural driving"** — total distance driven during the fuel consumption measurement at speeds **exceeding 50 km/h but not exceeding 70 km/h**.
10. **"motorway driving"** — total distance driven during the fuel consumption measurement at speeds **above 70 km/h**.
11. **"crosstalk"** — the signal at the main output of a sensor (My) produced by a measurand (Fz) acting on the sensor, which is different from the measurand assigned to that output; the coordinate system assignment is defined in accordance with **ISO 4130**.

---

## 3. Vehicle selection (point 3) ▼M3/▼M4

**Governing principle:** the number of new vehicles tested per production year must ensure that the relevant variations of components/STUs/systems used are covered by the VTP.

**(a)** Vehicles for the verification test are selected from the production line, from among vehicles for which a CO2/fuel-consumption value has already been determined and declared under Article 9. Components/STUs/systems mounted on the vehicle must be **out of series production** and correspond to those mounted at the vehicle's production date.

**(b)** (▼M4) Vehicle selection is made by the **approval authority** that granted the licence to operate the simulation tool, **based on proposals from the vehicle manufacturer**. For heavy buses, selection is made by the approval authority that granted the licence to the **primary vehicle manufacturer**.

**(c)** (▼M4) **Only vehicles with one driven axle shall be selected.** 

> **★ Key exclusion for electrified powertrains ★** — "**Hybrid electric, pure electric and fuel cell hybrid vehicles shall not be selected for the verification test.**" This is an explicit, unconditional carve-out: Annex Xa's on-road VTP regime, as drafted through amendment M4 (Reg 2025/258), **does not apply to BEVs, HEVs (hybrid electric), or fuel-cell hybrid vehicles.** No alternative electric-specific verification procedure is specified anywhere in this Annex range. See the "Flags for the HDEV project" section at the end of this file for the implications.

**(d)** (▼M3) It is **recommended** to include in each VTP relevant data sets of the components of interest with the **highest sales numbers per manufacturer**. Components/STUs/systems may be verified all in one vehicle or in different vehicles. Apart from the "highest sales numbers" criterion, the approval authority (per (b)) decides whether other vehicles with relevant engine/axle/transmission data sets should be included.

**(e)** (▼M4) Vehicles which **do not use standard values** for CO2 certification of their transmission and axle losses (i.e., use **measured** values instead) shall be **preferably tested**. If no vehicles comply with requirements (a)–(c), **only the verification of input information/input data and data handling** is performed (per point 6.1.1) — i.e., no physical on-road test is mandated in that edge case.

**(f)** (▼M3) Minimum number of vehicles per year, based on manufacturer sales volumes:

**Table 1 — Determination of the minimum number of vehicles to be tested by the vehicle manufacturer**

| Number of vehicles to be tested | Schedule | Verification testing procedure relevant vehicles produced / year (**) |
|---|---|---|
| 0 | — | ≤ 25 |
| 1 every 3 years (*) | — | 26 – 250 |
| 1 every 2 years | — | 251 – 5 000 |
| 1 every year | — | 5 001 – 25 000 |
| 2 every year | — | 25 001 – 50 000 |
| 3 every year | — | 50 001 – 75 000 |
| 4 every year | — | 75 001 – 100 000 |
| 5 every year | — | more than 100 000 |

*(*) The VTP shall be performed within the first two years. (▼M4)*
*(**) The total of all heavy lorries, medium lorries and primary buses produced by a manufacturer falling within the scope of this Regulation is to be considered, and medium lorries, heavy lorries and heavy buses need to be covered by the VTP over a six-year time span. (▼M4)*

**(g)** (▼M3) The vehicle manufacturer must **finalize the verification test within 10 months** after the date of selection of the vehicle for the verification test.

---

## 4. Vehicle conditions (point 4) ▼M3/▼M4

Each vehicle for the verification test shall be in the condition resembling its **intended placing on the market**. No changes in hardware (e.g. lubricants) or software (e.g. auxiliary controllers) are allowed. Tyres **may** be replaced by measurement tyres of a diameter not exceeding **± 10 %** of the original tyre diameter.

The provisions of points 3.3 to 3.6 of Annex II to Regulation (EU) 582/2011 apply.

### 4.1 Vehicle run-in
- Run-in of the vehicle is **not mandatory**.
- If total mileage of the test vehicle is **less than 15 000 km**, an **evolution coefficient** is applied by the simulation tool to the test result (defined in Appendix 1 — see formula H in Section 9 below).
- Total mileage of the test vehicle = odometer reading at start of the fuel consumption measurement.
- **Maximum mileage at start of the warm-up: 20 000 km.**

### 4.2 Fuel and lubricants
- All lubricants must be the same as used when placing the vehicle on the market.
- Fuel used for the measurement (point 6.1.5) shall be the fuel **available on the market**; in case of dispute, the fuel shall be the appropriate **reference fuel** per Annex IX to Regulation (EU) No 582/2011.
- Fuel tank must be **full** at start of vehicle warm-up. **Refuelling between start of warm-up and end of fuel consumption measurement is not allowed.**
- Net calorific value (NCV) of the fuel used shall be determined per point 3.2 of Annex V. The fuel batch is taken from the tank **after vehicle warm-up**.
- For dual-fuel engines, this procedure applies to **both fuels**.

---

## 5. Measurement equipment (point 5) ▼M3/▼M4

Calibration laboratory facilities must comply with **IATF 16949**, **ISO 9000 series**, or **ISO/IEC 17025**. All laboratory reference measurement equipment used for calibration and verification must be **traceable to national or international standards**.

### 5.1 Wheel torque
Direct torque at all driven axles measured with one of:
(a) hub torque meter; (b) rim torque meter; (c) half-shaft torque meter — each fulfilling Table 2 requirements.

- **Drift** is measured during the test by zeroing the torque measurement system (per 6.1.5.4) after vehicle warm-up (per 6.1.5.3), by lifting the axle and measuring torque at the lifted axle directly after the test (per 6.1.5.6).
- **Valid-test drift limit:** maximum drift (sum of absolute values of both wheels) of **1,5 % of the calibrated range** of a single torque meter over the VTP.

### 5.2 Vehicle speed
Recorded vehicle speed is based on the **CAN signal**.

### 5.3 Gear engaged
- **SMT/AMT transmissions:** engaged gear is **calculated by the simulation tool** from measured engine speed, vehicle speed, tyre dimensions and transmission ratios (per Appendix 1). Engine speed is taken from input data per point 5.4.
- **APT transmissions:** engaged gear **and** torque-converter status (active/not active) must be **provided from CAN signals**.

### 5.4 Rotational speed of the engine
Recorded from CAN, OBD, or alternative measurement systems meeting Table 2 requirements.

### 5.5 Rotational speed of the wheels at the driven axle
Left and right wheel speeds recorded from CAN or alternative systems meeting Table 2.

### 5.6 Rotational speed of fan
- **Non-electrically driven cooling fans:** rotational speed recorded (CAN signal or external sensor per Table 2).
- **Electrically driven cooling fans:** current and voltage recorded at the DC input terminal of the electric motor/inverter; electrical power at the terminal calculated by multiplication, available as a **time-resolved signal**. For multiple electric fans, the **sum** of electrical power at the terminals is used.
- **Heavy buses (▼M3):** pneumatic-system compressor status is recorded (phases delivering pressurised air to the reservoir are labelled per Table 4). Monitored via system pressure recording or available CAN signals.

### 5.7 Fuel measurement system (▼M3)
On-board measurement via one of:
- **Fuel mass measurement** — device meeting Table 2 accuracy for fuel mass measurement system.
- **Fuel volume measurement + thermal expansion correction** — fuel volume device and fuel temperature device meeting Table 2 accuracy; measured fuel volume flow converted to fuel mass flow per the following equations.

**Formula — fuel volume-to-mass conversion**

Raw OCR text:
```
mfuel,i = Vfuel,i·ρi
ρi ¼ ρ0
1 þ βðtiþ1 Ä t0Þ
```

Reconstructed equations:
```
m_fuel,i = V_fuel,i × ρ_i

ρ_i = ρ0 / [1 + β × (t_i − t0)]
```
Where:
- **m_fuel,i** = Fuel mass flow at sample i [g/h]
- **ρ0** = Density of the fuel used for the verification test [g/dm³]; determined per Annex IX to Regulation (EU) No 582/2011. If diesel fuel is used, the **average value of the density interval for reference fuel B7** (per Annex IX, Reg 582/2011) may also be used.
- **t0** = Fuel temperature corresponding to density ρ0 for the reference fuel [°C]
- **ρ_i** = Density of the test fuel at sample i [g/dm³]
- **V_fuel,i** = Fuel volume flow at sample i [dm³/h]
- **t_i** = Measured fuel temperature at sample i [°C]
- **β** = 0,001 [K⁻¹] (Temperature correction factor) ▼M4

For dual-fuel vehicles, fuel flow is measured for each of the two fuels **separately**.

### 5.8 Vehicle mass
Measured with Table 2-compliant equipment:
(a) actual mass of the vehicle for VTP;
(b) actual mass of the vehicle for VTP with payload.

### 5.9 General requirements for on-board measurements (5.1–5.8) ▼M4
- Input data per Table 4 (point 6.1.6) must come from the measurements.
- All data recorded at **≥ 2 Hz**, or at the equipment maker's recommended frequency if higher.
- Input data may come from different recorders, but torque and rotational speed at the wheels must be recorded in **one** data-logging system. If different loggers are used for other signals, a common signal (e.g. vehicle speed) must be recorded in all loggers to time-align them; time alignment is chosen to maximise the **correlation coefficient** of the common signal across loggers.
- Accuracy requirements of Table 2 apply to all equipment used; equipment not listed in Table 2 must meet Table 2 of **Annex V** instead.

**Table 2 — Requirements of measurement systems**

| Measurement system | Accuracy | Rise time (1) |
|---|---|---|
| Balance for vehicle weight | 50 kg or < 0,5 % of max. calibration, whichever is smaller | — |
| Rotational speed wheels | < 0,5 % of reading at 80 km/h | ≤ 1 s |
| Fuel mass flow for liquid fuels (2) | < 1,0 % of reading or < 0,2 % of max. calibration, whichever is larger | — |
| Fuel mass flow for gaseous fuels (2) | < 1,0 % of reading or < 0,5 % of max. calibration, whichever is larger | — |
| Fuel volume measurement system (2) | < 1,0 % of reading or < 0,5 % of max. calibration, whichever is larger | — |
| Temperature of the fuel | ± 1 °C | ≤ 2 s |
| Sensor for rotational speed of cooling fan | < 0,4 % of reading or < 0,2 % of max. calibration of speed, whichever is larger | ≤ 1 s |
| Voltage | < 2 % of reading or < 1 % of max. calibration of speed, whichever is larger | ≤ 1 s |
| Current | < 2 % of reading or < 1 % of max. calibration of speed, whichever is larger | ≤ 1 s |
| Engine speed | As set out in Annex V. In the case of vehicles with engine stop-start, it shall be verified that the engine speed is also recorded correctly for speeds below idle. | — |
| Wheel torque (▼M4) — for 10 kNm calibration (over entire calibration range): i. Non-linearity (3): < ±40 Nm (heavy lorries & heavy buses) / < ±30 Nm (medium lorries); ii. Repeatability (4): < ±20 Nm (heavy lorries & heavy buses) / < ±15 Nm (medium lorries); iii. Crosstalk: < ±20 Nm (heavy lorries & heavy buses) / < ±15 Nm (medium lorries) (rim torque meters only); iv. Measurement rate ≥ 20 Hz | < 0,1 s |

*(1) Rise time = difference in time between the 10 % and 90 % response of the final analyser reading (t90 – t10).*
*(2) Accuracy met for the integral fuel flow over 100 minutes.*
*(3) Non-linearity = maximum deviation between ideal and actual output signal characteristics relative to the measured value, in a specific measuring range.*
*(4) Repeatability = closeness of agreement between results of successive measurements of the same measured value, under the same measurement conditions.*

Additional rules:
- Maximum calibration values = maximum expected values during all test runs for the respective measurement system, **multiplied by an arbitrary factor >1 and ≤2**. For the torque measurement system, maximum calibration **may be limited to 10 kNm**.
- Dual-fuel engines: maximum calibration value for fuel mass/volume flow determined per point 3.5 of Annex V; for fuel volume, divide the max calibration value for fuel mass flow by ρ0 (per 5.7).
- Where more than one measurement scale is used, the accuracy requirement must be met by the **sum of all single accuracies**.

### 5.10 Engine torque
Recorded during the VTP for evaluating pollutant emissions. Signal must meet the provisions for the engine torque signal in Table 1 of point 2.2 of Appendix 1 to Annex II to Regulation (EU) 582/2011.

### 5.11 Pollutant emissions
- Instrumentation/procedures per Appendices 1–4 of Annex II to Regulation (EU) 582/2011.
- Data evaluation provides **instantaneous emission mass flows** (Table 4, point 6.1.6) as simulation tool input.
- The simulation tool **automatically** calculates the brake-specific pollutant emissions measured in the verification test (**BSEM**) per **Part B of Appendix 1** (see Section 9.2 below); results are automatically written to simulation tool output per point 8.13.14.
- Additional Regulation (EU) 582/2011 requirements on data evaluation (work-based windows, moving-average windows, test start, trip definitions) **do not apply** here.
- **(▼M3) In the VTP, pass/fail criteria regarding pollutant emissions shall not apply.** (I.e., pollutant emissions are measured/reported but are not a VTP pass/fail gate — only CO2/fuel consumption is gated; see Section 7.)

### 5.12 Distance travelled (▼M4)
If the vehicle has an OBFCM-type on-board device (per point (b) of Article 5c of Regulation (EC) No 595/2009), mileage is recorded from that device.

### 5.13 Engine fuel rate (▼M4)
Same OBFCM device condition: instantaneous engine fuel rate and total fuel consumed at test start/end are recorded from the device.

### 5.14 Vehicle total mass (▼M4)
Same OBFCM-type condition (on-board mass-monitoring device): instantaneous vehicle total mass recorded from the device.

---

## 6. Test procedure (point 6) ▼M3/▼M4

### 6.1 Vehicle preparation
Vehicle taken from series production, selected per Section 3.

#### 6.1.1 Verification of input information and input data and data handling
- The **manufacturer's records file** and the **customer information file** for the selected vehicle are the basis for verifying input data.
- The selected vehicle's **VIN** must match the VIN in both files.
- Upon request by the approval authority, the manufacturer must provide, **within 15 working days**, the manufacturer's records file, input information/data needed to run the simulation tool, and the certificates of CO2/fuel-consumption-related properties for all relevant components/STUs/systems.
- (▼M4) **Heavy buses:** the primary vehicle manufacturer provides the input information/data + manufacturer's records file; the **completed** vehicle manufacturer provides the vehicle information file and customer information file.

##### 6.1.1.1 Verification of components, STUs or systems and input data/information (▼M3/▼M4)
Checks performed on components/STUs/systems mounted on the vehicle:

**(a) Simulation tool data integrity:** the cryptographic hash of the manufacturer's records file (per Article 9(3)), **re-calculated during the VTP with the hashing tool**, is verified against the cryptographic hash in the **certificate of conformity**.

**(b) Vehicle data:** VIN, axle configuration, selected auxiliaries and power-take-off technology, disabled gears (per Annex III point 6.2), and requirements on active aero devices (per Annex VIII point 3.3.1.5) must match the selected vehicle.

**(c) Engine torque limitation verification** (▼M4):
- Declared engine torque limitations in the simulation tool input are subject to VTP verification **if** declared for any of the **highest 50 % of the gears** (e.g. gears 7–12 of a 12-gear transmission) **and** one of the following applies:
  (i) torque limit declared at vehicle level (Annex III point 6.1); or
  (ii) torque limit declared in the transmission component input per parameter **P157** (Table 2, Appendix 12, Annex VI) **and** the declared value does **not exceed 90 %** of engine maximum torque.
- **Pass requirement:** for any torque limit subject to verification, it must be demonstrated that the **99 % percentile of the engine torque** recorded during the fuel consumption measurement in the relevant gear does **not exceed the declared torque limit by more than 5 %.** The verification test must cover phases of full throttle in the respective gears, based on recorded engine torque (per 5.10).
- This engine-torque-limitation verification **may be performed as a separate, dedicated test** (full-load accelerations only), with no other VTP test-evaluation obligations.

**(d) Component/STU/system data:** certification number and model type imprinted on the certificate of CO2/fuel-consumption-related properties must match the component/STU/system installed in the selected vehicle.

**(e) Hash matching:** the hash of the simulation tool input data/information must match the hash imprinted on the certificate of CO2 emissions/fuel-consumption-related properties for:
(i) engines; (ii) transmissions; (iii) torque converters; (iv) other torque-transferring components; (v) additional drivetrain components; (vi) axles; (vii) air drag (▼M4); (viii) tyres.

##### 6.1.1.2 Verification of the vehicle mass (▼M4)
If requested by the approval authority, mass determination by the manufacturer is verified per **point 2 of Section G of Part 2 of Annex VIII of Regulation (EU) 2021/535**. If that verification fails, the **corrected actual mass** (Annex III point 2(4)) is determined instead. For heavy buses, the mass of the **completed vehicle** is verified.

##### 6.1.1.3 Actions to be taken — [NON-CONFORMITY CONSEQUENCE] (▼M3)
- **If discrepancies** are found in the certification number or cryptographic hash of one or more files for components/STUs/systems listed in subpoints (1)–(8) of point 6.1.1.1(e): the **correct input data file** (meeting the 6.1.1.1/6.1.1.2 checks) **replaces** the incorrect data for all further actions. Same treatment applies to any other incorrect information identified under 6.1.1.1(b) and (c).
- **If the verification of the manufacturer's records file / customer information file fails**, or **no complete input data set with correct certificates is available** for components/STUs/systems listed in subpoints (1)–(8) of 6.1.1.1(e): **the verification test ends and the vehicle fails the verification testing procedure.**

#### 6.1.2 Run-in phase
- A run-in phase up to **maximum 15 000 km** odometer reading may take place.
- **If a listed component/STU/system (per 6.1.1.1) is damaged**, it may be **replaced by an equivalent component/STU/system with the same certification number**; the replacement must be **documented in the test report**.
- All relevant components/STUs/systems are checked before measurement to exclude unusual conditions (e.g. incorrect oil fill levels, plugged air filters, OBD warnings).

#### 6.1.3 Set-up of measurement equipment
- All measurement systems calibrated per the equipment maker's provisions (or recommendations, if no provisions exist).
- After run-in, the vehicle is equipped with the measurement systems of Section 5.

#### 6.1.4 Set-up of the test vehicle for the fuel consumption measurement ▼M3/▼M4

##### 6.1.4.1 Vehicle configuration
- **Tractors** (vehicle groups of Tables 1 & 2, Annex I): tested with any type of semitrailer, provided the payload (below) can be applied.
- **Rigid lorries** (Tables 1 & 2, Annex I): tested with trailer if a trailer connection is mounted; any body type/device carrying the payload (6.1.4.2) may be used; bodies of rigid lorries may differ from standard bodies (Annex VIII, Appendix 4, point 2).
- **Vans** (Table 2, Annex I): tested with the **final bodies** of the complete/completed vehicle.
- **Heavy buses** (▼M4) (Tables 4, 5, 6, Annex I): tested with the final bodies of the complete/completed vehicle.

##### 6.1.4.2 Vehicle payload ▼M3/▼M4
- **Heavy lorries, groups 4 and higher:** payload set **at minimum** to a mass giving a total test weight of **90 % of the maximum authorised weight** per **Directive 96/53/EC** for the specific vehicle/combination.
- **Heavy lorries groups 1s, 1, 2, 3; medium lorries; heavy buses (▼M4):** payload in the range **55 % to 75 %** of the maximum authorised weight per 96/53/EC.

##### 6.1.4.3 Tyre inflation pressure
- Set to manufacturer recommendation, max deviation **< 10 %**.
- Semitrailer tyres may differ from the standard tyres in Table 2 of Part B of Annex II to Regulation (EC) No 661/2009 used for tyre CO2 certification.

##### 6.1.4.4 Settings for auxiliaries (▼M4)
- All settings influencing auxiliary energy demand set to **minimum reasonable energy consumption** where applicable.
- **Air conditioning switched off**; cabin/driver-compartment venting set **lower than medium mass flow**.
- Additional energy consumers not necessary to run the vehicle switched off.
- External on-board energy devices (e.g. external batteries) allowed **only** to power the extra VTP measurement equipment (Table 2) — **not** to power vehicle equipment present at market placement.
- Heavy buses: **door opening and kneeling at stops are not considered** in the verification test.

##### 6.1.4.5 Particle filter regeneration
A particle filter regeneration shall, if applicable, be initiated **before** the verification test (per Regulation (EU) 582/2011, Annex II, point 4.6.10).

#### 6.1.5 Verification test ▼M3/▼M4

##### 6.1.5.1 Route selection
Route must fulfil Table 3 requirements; may include both public and private tracks.

##### 6.1.5.2 Vehicle pre-conditioning
No pre-conditioning allowed other than the warm-up pre-condition (6.1.5.3).

##### 6.1.5.3 Vehicle warm up
- Vehicle driven for warm-up per Table 3; warm-up phase **not** considered in test evaluation.
- Before warm-up starts, PEMS analysers checked/calibrated per Appendix 1 of Annex II to Regulation (EU) 582/2011.

##### 6.1.5.4 Zeroing of the torque measurement equipment
1. Bring vehicle to standstill.
2. Lift instrumented wheels off the ground so they rotate freely with no external torque on the sensor.
3. Zero the amplifier reading of the torque meters.
- **Zeroing must finish within less than 20 minutes.**

##### 6.1.5.5 Fuel consumption measurement and recording of pollutant emission signals ▼M3/▼M4
- Fuel consumption measurement starts **directly after zeroing** of wheel-torque equipment, at vehicle standstill.
- Driving style must avoid unnecessary braking, gas-pedal pumping, aggressive cornering. Advanced driver assistance systems set as activated automatically at key-on; gear shifts by the automated system (AMT/APT); cruise control used if applicable.
- Duration of the fuel consumption measurement within tolerances of **Table 3**.
- Measurement ends at vehicle standstill, directly before the torque-drift measurement.
- Pollutant-emission signal recording starts **no later than** fuel consumption measurement start, ends together with it.
- Input to the simulation tool = the **entire test sequence**, from the last 0,5 s time step of the standstill phase after torque-meter zeroing, to the first 0,5 s time step of the final standstill phase.
- (▼M4) If the vehicle has **fuel-powered auxiliary heaters**, only the fuel consumption of the **internal combustion engine** is measured.
- Where applicable (OBFCM): vehicle total mass and engine fuel rate signal recording start no later than fuel-consumption-measurement start and end together with it; lifetime mileage and total fuel consumption values (from OBFCM) recorded at start and end of the OBFCM fuel consumption measurement.

##### 6.1.5.6 Measurement of the drift of the torque measurement equipment
- Directly after fuel consumption measurement, drift recorded under same conditions as zeroing.
- If measurement ends before the drift-measurement stop, vehicle must be stopped for drift measurement **within 5 minutes**.
- Drift of each torque meter = average of a **minimum sequence of 10 seconds**.
- Directly thereafter, emission-measurement verification performed per point 2.7 of Appendix 1 to Annex II to Regulation (EU) 582/2011.

##### 6.1.5.7 Boundary conditions for the verification test ▼M3/▼M4
- Boundary conditions for a valid VTP are set in **Tables 3 to 3d**.
- **(▼M3) Conditional validity override:** If the vehicle **passes** the verification test per point 7.3, the test is **still set valid** even if the following are not met:
  - undercut of minimum values for parameters No 1, 2, 6 and 9;
  - exceedance of maximum values for parameters No 3, 4, 5, 7, 8, 10 and 12;
  - exceedance of the maximum value for parameter No 7, **if** total testing time not in standstill exceeds **80 minutes**.
  
  (I.e., these boundary-condition breaches do not themselves invalidate an otherwise-passing test — they are secondary data-quality bounds, not independent pass/fail gates, as long as the primary CVTP pass criterion in point 7.3 is met.)

**Table 3 — Parameters for a valid verification test for all vehicle groups**

| No. | Parameter | Min. | Max. |
|---|---|---|---|
| 1 | Warm up [minutes] | — | 60 |
| 2 | Average velocity at warm up [km/h] | 70 (1) | 100 |
| 3 | Fuel consumption measurement duration [minutes] | 80 | 120 |
| 8 | Average ambient temperature | 5 °C | 30 °C |
| 9 | Road condition dry | 100 % | — |
| 10 | Road condition snow or ice | — | 0 % |
| 11 | Sea level of the route [m] | — | 800 |
| 12 | Duration of continuous idling at standstill [minutes] | — | 3 |

*(1) Where maximum vehicle speed < 80 km/h, the average velocity in warm-up shall exceed (maximum vehicle speed − 10 km/h).*

Note: parameters No. 4–7 are not in Table 3 itself (they vary per vehicle group — see Tables 3a–3d below).

**Table 3a — Parameters for a valid verification test for vehicle groups 4, 5, 9, 10**

| No. | Parameter | Min. | Max. |
|---|---|---|---|
| 4 | Distance based share urban driving | 2 % | 8 % |
| 5 | Distance based share rural driving | 7 % | 13 % |
| 6 | Distance based share motorway driving | 79 % | — |
| 7 | Time share of idling at standstill | — | 5 % |

**Table 3b — Parameters for a valid verification test for other heavy and medium lorries**

| No. | Parameter | Min. | Max. |
|---|---|---|---|
| 4 | Distance based share urban driving | 10 % | 50 % |
| 5 | Distance based share rural driving | 15 % | 25 % |
| 6 | Distance based share motorway driving | 25 % | — |
| 7 | Time share of idling at standstill | — | 10 % |

**Table 3c — Parameters for a valid verification test for high floor heavy buses**

| No. | Parameter | Min. | Max. |
|---|---|---|---|
| 4 | Distance based share urban driving | 12 % | 40 % |
| 5 | Distance based share rural driving | 10 % | 30 % |
| 6 | Distance based share motorway driving | 30 % | — |
| 7 | Time share of idling at standstill | — | 10 % |

**Table 3d — Parameters for a valid verification test for low floor heavy buses**

| No. | Parameter | Min. | Max. |
|---|---|---|---|
| 4 | Distance based share urban driving | 75 % | 90 % |
| 5 | Distance based share rural driving | 10 % | 25 % |
| 6 | Distance based share motorway driving | — | 0 % |
| 7 | Time share of idling at standstill | — | 10 % |

#### 6.1.6 Data reporting ▼M3/▼M4
- Data recorded during the VTP reported to the approval authority as constant **2 Hz** signals (Table 4).
- Data recorded at higher frequency converted to 2 Hz by **averaging the time intervals around the 2 Hz nodes**. Example: at 10 Hz sampling, first 2 Hz node = average of seconds 0,1–0,5; second node = average of seconds 0,6–1,0. Time stamp per node = the **last** time stamp in that interval (i.e. 0,5; 1,0; 1,5 …).

**Table 4 — Data reporting format for measured data for the simulation tool in the verification test** (▼M4)

| Quantity | Unit | Heading input data | Comment |
|---|---|---|---|
| time node | [s] | `<t>` | |
| vehicle speed | [km/h] | `<v>` | |
| engine speed | [rpm] | `<n_eng>` | |
| engine cooling fan speed | [rpm] | `<n_fan>` | non-electrically driven fans |
| engine cooling fan electrical power | [W] | `<Pel_fan>` | electrically driven fans |
| torque left wheel | [Nm] | `<tq_wh_left>` | |
| torque right wheel | [Nm] | `<tq_wh_right>` | |
| wheel speed left | [rpm] | `<n_wh_left>` | |
| wheel speed right | [rpm] | `<n_wh_right>` | |
| gear | [-] | `<gear>` | mandatory for APT transmissions |
| Torque converter active | [-] | `<TC_active>` | 0 = not active (locked); 1 = active (unlocked); mandatory for AT transmissions, not relevant for other transmission types |
| fuel flow | [g/h] | `<fc_X>` | Fuel mass flow per 5.7(1). "X" = fuel type per Table 2 of Appendix 7 of Annex V, e.g. `<fc_Diesel CI>`. Dual-fuel: separate column per fuel. |
| Compressor pneumatic system status | [-] | `<PS_comp_active>` | 1 = active (compressor delivering to pneumatic system), 0 = not active; relevant for heavy buses only |
| Engine torque | [Nm] | `<tq_eng>` | per point 5.10 |
| CH4 mass flow | [g/s] | `<CH4>` | only if required per point 1, Appendix 1, Annex II, Reg 582/2011 |
| CO mass flow | [g/s] | `<CO>` | |
| NMHC mass flow | [g/s] | `<NMHC>` | only if required per point 1, Appendix 1, Annex II, Reg 582/2011 |
| NOx mass flow | [g/s] | `<NOx>` | |
| THC mass flow | [g/s] | `<THC>` | only if required per point 1, Appendix 1, Annex II, Reg 582/2011 |
| PM number flow | [#/s] | `<PN>` | |
| CO2 mass flow | [g/s] | `<CO2>` | ▼M4 |
| OBFCM mileage | [km] | `<ml_obfcm>` | per 5.12, if applicable |
| OBFCM engine mass fuel rate | [g/s] | `<fcm_obfcm>` | per 5.13, if applicable |
| OBFCM engine volume fuel rate | [l/s] | `<fcv_obfcm>` | per 5.13, if applicable |
| OBFCM vehicle total mass | [kg] | `<m_obfcm>` | per 5.14, if applicable |

*(1) Correction of fuel flow to standard NCV is performed automatically by the simulation tool, based on the NCV input of the fuel used in the test, per Table 4a.*

**Table 4a — Data reporting format for further information for the simulation tool in the verification test**

| Quantity | Unit | Comment |
|---|---|---|
| NCV measured | [MJ/kg] | NCV of the fuel used in the VTP, determined per point 3.2 of Annex V. Provided for all fuel types, including Diesel CI engines (1). Dual-fuel: values for both fuels. |
| Run-in distance | [km] | Per point 6.1.2. Used by simulation tool to correct measured fuel consumption per Appendix 1. |
| Diameter fan | [mm] | Diameter of the engine cooling fan; not relevant for electrically driven fans. |
| Torque meter drift left wheel | [Nm] | Average torque meter readings per point 6.1.5.6. |
| Torque meter drift right wheel | [Nm] | — |

*(1) In the VTP test, the vehicle may be operated with market diesel fuel. Contrary to reference diesel fuel (B7), the variation of NCV for market fuel is assessed to be greater than the measuring accuracy when determining NCV.*

This data is entered **directly into the graphical user interface (GUI)** of the simulation tool when evaluating the verification test procedure.

### 6.2 Additional verifications (heavy buses) (▼M4)
Correspondence of the tested vehicle with the following is verified:
i. Technical Permissible Maximum Laden Mass
ii. Vehicle code
iii. Class of vehicle
iv. Low entry (if applicable)
v. Number of passenger seats
vi. Height of the integrated body

---

## 7. Test evaluation (point 7) — PASS/FAIL CRITERIA AND NON-CONFORMITY ▼M3/▼M4

### 7.1 Input to the simulation tool (▼M4)
Inputs that must be made available:

**(a) Medium and heavy lorries:**
(i) Manufacturer's records file; (ii) Customer information file; (iii) Processed measurement data per Table 4; (iv) Further information per Table 4a.

**(b) Heavy buses:**
(v) Input data/input information defined for the primary heavy bus; (vi) Manufacturer's records file for the primary heavy bus; (vii) Vehicle information file for the primary vehicle; (viii) Customer information file for the completed vehicle; (ix) Vehicle information file for the completed vehicle; (x) Processed measurement data per Table 4; (xi) Further information per Table 4a.

### 7.2 Evaluation steps performed by the simulation tool

#### 7.2.1 Verification of the data handling process
The simulation tool **re-simulates** the CO2 emissions and fuel consumption based on the point-7.1 inputs, and verifies the corresponding results in the manufacturer's records file and customer information file as provided by the manufacturer. For heavy buses, the vehicle information file and customer information file of the **completed** vehicle are also verified.

> **[NON-CONFORMITY CONSEQUENCE]** — "In the case of **any deviations**, the **remedial measures referred to in Article 23** shall apply." (Article 23's full text is not within this extracted range — it is the Regulation's general remedial-measures/enforcement article. This is the primary cross-reference point by which Annex Xa data-handling or re-simulation deviations feed into the Regulation's broader non-conformity/enforcement regime.)

#### 7.2.2 Determination of the CVTP ratio
Test evaluation compares measured vs. simulated CO2 emissions via the **CVTP ratio** (ratio of measured to simulated brake-specific CO2 emissions for the total verification-test-relevant trip).

Raw OCR text:
```
CVTP ¼
Pn 
Pi¼1 BSFCmÄc;i Ü CO2i
n 
i¼1 BSFCsim;i Ü CO2i
```

Reconstructed equation:
```
          Σ(i=1 to n) [ BSFCm-c,i × CO2i ]
CVTP  =  ───────────────────────────────────
          Σ(i=1 to n) [ BSFCsim,i × CO2i ]
```
Where:
- **CVTP** = ratio of CO2 emissions measured and simulated in the VTP ("CVTP ratio") [-]
- **n** = number of fuels (2 for dual-fuel engines, else 1)
- **CO2i** = generic CO2 emission factor (grams CO2 per gram fuel) for the specific fuel type, as implemented in the simulation tool
- **BSFCm-c** = brake specific fuel consumption, measured and corrected for a run-in phase, calculated per point 2 of Part A, Appendix 1 [g/kWh] (see Section 9.1 below)
- **BSFCsim** = brake specific fuel consumption determined by the simulation tool, per point 3 of Part A, Appendix 1 [g/kWh] (see Section 9.1 below)

### 7.3 Pass/Fail check — THE CENTRAL NON-CONFORMITY / TOLERANCE PROVISION (▼M4)

**Pass condition:** the vehicle passes the verification test if the **CVTP ratio ≤ the tolerance in Table 5**.

**Comparison with the declared CO2 emissions (Article 9):**
```
CO2verified = CVTP × CO2declared
```
Where:
- **CO2verified** = verified CO2 emissions of the vehicle, in **[g/tkm]** for medium and heavy lorries, **[g/pkm]** for heavy buses
- **CO2declared** = declared CO2 emissions of the vehicle, same units

**Retest provision:** If a first vehicle does **not** meet the pass criterion of Table 5:
- **up to two additional tests** may be performed on the **same vehicle**, **or**
- **two more similar vehicles** may be tested, **on request of the vehicle manufacturer**.
- For the pass-criterion evaluation, the **arithmetic average of the CVTP ratios from all tests performed** is used.
- **If the pass criterion is still not reached, the vehicle fails the verification testing procedure.**

**Table 5 — Pass criterion for the verification test**

| Pass criterion for the verification testing procedure |
|---|
| CVTP ratio ≤ 1,075 |

**Low-CVTP reporting trigger:** "Where CVTP is lower than **0,925**, the results need to be reported to the **Commission** for further analysis to determine the cause." (This is an asymmetric provision: on the high side, CVTP > 1,075 is an outright fail; on the low side, there is no explicit "fail" at CVTP < 0,925, but a mandatory reporting-to-Commission trigger for investigation — i.e. a materially *lower*-than-expected measured CO2 relative to simulated also draws regulatory scrutiny, not just higher-than-expected.)

---

## 8. Reporting procedures (point 8) ▼M3/▼M4

The vehicle manufacturer establishes a test report for **each vehicle tested**, including at least:

### 8.1 General
8.1.1. Name and address of the vehicle manufacturer (1) *(1) For heavy buses, only primary vehicle manufacturer.*
8.1.2. Address(es) of assembly plant(s)
8.1.3. Name, address, telephone/fax, e-mail of the vehicle manufacturer's representative
8.1.4. Type and commercial description
8.1.5. Selection criteria for vehicle and CO2-relevant components (text)
8.1.6. Vehicle owner
8.1.7. Odometer reading at test start of the fuel consumption measurement (km)

### 8.2 Vehicle information
8.2.1. Vehicle model / Commercial Name
8.2.2. Vehicle identification number (VIN)
8.2.2.1. Where the test followed a first-vehicle-test failure (per 7.3), the VIN of the vehicle tested first
8.2.3. Vehicle category (N2, N3, M3)
8.2.4. Axle configuration
8.2.5. Technically permissible maximum laden mass (t)
8.2.6. Vehicle group
8.2.7. Corrected actual mass of the vehicle (kg)
8.2.8. Cryptographic hash of the manufacturer's records file
8.2.9. Vehicle combination's gross combined weight in the verification test (kg)
8.2.10. Mass in running order

### 8.3 Main engine specifications
8.3.1. Engine model; 8.3.2. Engine certification number; 8.3.3. Engine rated power (kW); 8.3.4. Engine capacity (l); 8.3.5. Engine reference fuel type (diesel/LPG/CNG…); 8.3.6. Hash of the fuel map file/document

### 8.4 Main transmission specifications
8.4.1. Transmission model; 8.4.2. Transmission certification number; 8.4.3. Main option used for generation of loss maps (Option1/Option2/Option3/Standard values); 8.4.4. Transmission type; 8.4.5. Number of gears; 8.4.6. Transmission ratio final gear; 8.4.7. Retarder type; 8.4.8. Power take off (yes/no); 8.4.9. Hash of the efficiency map file/document

### 8.5 Main retarder specifications
8.5.1. Retarder model; 8.5.2. Retarder certification number; 8.5.3. Certification option used for generation of a loss map (standard values/measurement); 8.5.4. Hash of the retarder efficiency map file/document

### 8.6 Torque converter specification
8.6.1. Torque converter model; 8.6.2. Torque converter certification number; 8.6.3. Certification option (standard values/measurement); 8.6.4. Hash of the efficiency map file/document

### 8.7 Angle drive specifications
8.7.1. Angle drive model; 8.7.2. Axle certification number; 8.7.3. Certification option (standard values/measurement); 8.7.4. Angle drive ratio; 8.7.5. Hash of the efficiency map file/document

### 8.8 Axle specifications
8.8.1. Axle model; 8.8.2. Axle certification number; 8.8.3. Certification option (standard values/measurement); 8.8.4. Axle type (e.g. standard single driven axle); 8.8.5. Axle ratio; 8.8.6. Hash of the efficiency map file/document

### 8.9 Aerodynamics
8.9.1. Model; 8.9.2. Certification option used for generation of CdxA (standard values/measurement); 8.9.3. CdxA Certification number (if applicable); 8.9.4. CdxA value; 8.9.5. Hash of the efficiency map file/document

### 8.10 Main tyre specifications
8.10.1. Tyre certification number on all axles; 8.10.2. Specific rolling resistance coefficient of all tyres on all axles

### 8.11 Main auxiliary specifications
8.11.1. Engine cooling fan technology; 8.11.1.1. Engine cooling fan diameter; 8.11.2. Steering pump technology; 8.11.3. Electric system technology; 8.11.4. Pneumatic system technology

### 8.12 Test conditions
8.12.1. Actual mass of the vehicle for VTP (kg); 8.12.2. Actual mass of the vehicle for VTP with payload (kg); 8.12.3. Warm up time (minutes); 8.12.4. Average velocity at warm up (km/h); 8.12.5. Fuel consumption measurement duration (minutes); 8.12.6. Distance based share urban driving (%); 8.12.7. Distance based share rural driving (%); 8.12.8. Distance based share motorway driving (%); 8.12.9. Time share of idling at stand still (%); 8.12.10. Average ambient temperature (°C); 8.12.11. Road condition (dry, wet, snow, ice, others — specify); 8.12.12. Maximum sea level of the route (m); 8.12.13. Maximum duration of continuous idling at stand still (minutes)

### 8.13 Results of the verification test
8.13.1. Average fan power calculated for the VTP by the simulation tool (kW)
8.13.2. Positive wheel work over the VTP calculated by the simulation tool (kWh)
8.13.3. Positive wheel work over the VTP measured (kWh)
8.13.4. NCV of the fuel(s) used in the VTP (MJ/kg)
8.13.5. Fuel consumption value(s) in the VTP measured (g/kWh); 8.13.5.1. CO2 emission value(s) in the VTP measured (g/kWh)
8.13.6. Fuel consumption value(s) in the VTP measured, corrected (g/kWh); 8.13.6.1. CO2 emission value(s) in the VTP measured, corrected (g/kWh)
8.13.7. Fuel consumption value(s) in the VTP simulated (g/kWh); 8.13.7.1. CO2 emission value(s) in the VTP simulated (g/kWh)
8.13.8. Fuel consumption in the VTP simulated (g/kWh); 8.13.8.1. CO2 emission in the VTP simulated (g/kWh)
8.13.9. Mission profile (long haul / long haul (EMS) / regional / regional (EMS) / urban / municipal / construction)
8.13.10. **Verified CO2 emissions of the vehicle (g/tkm)**
8.13.11. **Declared CO2 emissions of the vehicle (g/tkm)**
8.13.12. **Ratio of fuel consumption measured and simulated in the VTP (CVTP) (-)**
8.13.13. **Passed the verification test (yes/no)**
8.13.14. Pollutant emissions in the verification test:
  8.13.14.1. CO (mg/kWh); 8.13.14.2. THC (**) (mg/kWh); 8.13.14.3. NMHC (***) (mg/kWh); 8.13.14.4. CH4 (***) (mg/kWh); 8.13.14.5. NOx (mg/kWh); 8.13.14.6. PM number (#/kWh); 8.13.14.7. Positive engine work (kWh); 8.13.14.8. CO2 (g/kWh)
8.13.15. OBFCM values in the verification test (if applicable):
  8.13.15.1. OBFCM mileage reading at test start of fuel consumption measurement (km); 8.13.15.2. OBFCM mileage reading at test end (km); 8.13.15.3. OBFCM total mass fuel consumed, lifetime signal, at measurement start (kg); 8.13.15.4. same at measurement end (kg); 8.13.15.5. OBFCM total volume fuel consumed, lifetime signal, at start (l); 8.13.15.6. same at end (l); 8.13.15.7. OBFCM accumulated engine mass fuel rate values, instantaneous signal (kg); 8.13.15.8. OBFCM accumulated engine volume fuel rate values, instantaneous signal (l); 8.13.15.9. OBFCM average total mass, instantaneous signal (kg); 8.13.15.10. odometer reading at test end of fuel consumption measurement (km); 8.13.15.11. total mass fuel consumption value measured (kg); 8.13.15.12. total volume fuel consumption value measured (l)

*(**) Only if this component needs to be measured in accordance with point 1 of Appendix 1 to Annex II to Regulation (EU) 582/2011.*
*(***) For positive ignition engines.*

### 8.14 Software and user information
8.14.1. Simulation tool version (X.X.X)
8.14.2. Date and time of the simulation

### 8.15 Input to the simulation tool
As set out in point 7.1.

### 8.16 Simulation output data
8.16.1. **Aggregated simulation results**: a `.vsum` CSV file (same name as the job file) with aggregated results of the simulated VTP, generated by the simulation tool GUI ("sum exec data file").
8.16.2. **Time-resolved simulation results**: a `.vmod` CSV file (name comprising the VIN + measurement data file name) with time-resolved results of the simulated VTP, generated by the simulation tool GUI ("mod data file").

---

## 9. Appendix 1 — Main evaluation steps and equations performed by the simulation tool in a VTP simulation ▼M4/▼M3

### 9.1 PART A: Determination of the CVTP factor

**9.1.1 Calculation of wheel power**

Torque data (per Table 4) is first corrected for torque-meter drift:

Raw OCR text:
```
TcorrÄiðtÒ ¼ TiðtÒ Ä TdriftÄi · t Ä tstart
tend Ä tstart
```
Reconstructed equation:
```
T_corr,i(t) = T_i(t) − T_drift,i × [ (t − t_start) / (t_end − t_start) ]
```
Where: i = index for left/right wheel of the driven axle; T_corr = drift-corrected torque signal [Nm]; T = torque signal before drift correction [Nm]; T_drift = torque meter drift recorded during drift check at the end of the VTP [Nm]; t = time node [s]; t_start = first time stamp in Table 4 processed data [s]; t_end = last time stamp in Table 4 processed data [s].

Wheel power per wheel:

Raw OCR text:
```
PwheelÄiðtÒ ¼ 2 · π · nwheelÄiðtÒ · TcorrÄiðtÒ
60000
```
Reconstructed equation:
```
P_wheel,i(t) = [ 2 × π × n_wheel,i(t) × T_corr,i(t) ] / 60000
```
Where: i = index for left/right wheel; t = time node [s]; P_wheel = wheel power [kW]; n_wheel = rotational wheel speed [rpm]; T_corr = drift-corrected torque signal [Nm].

Total wheel power (sum of left + right):

Raw OCR text:
```
PwheelðtÒ ¼ X2 
i¼1
PwheelÄiðtÒ
```
Reconstructed equation:
```
P_wheel(t) = Σ(i=1 to 2) P_wheel,i(t)
```

**9.1.2 Determination of the measured brake specific fuel consumption (BSFCm-c)**

Step 1 — raw measured BSFC:

Raw OCR text:
```
BSFCm ¼
Ptend 
tstart FCmðtÒ · Δt 
Wwheel;pos;m
```
Reconstructed equation:
```
          Σ(t=t_start to t_end) [ FC_m(t) × Δt ]
BSFC_m = ──────────────────────────────────────
                     W_wheel,pos,m
```
Where: BSFC_m = raw measured brake specific fuel consumption in the VTP [g/kWh]; FC_m(t) = instantaneous fuel mass flow measured during the VTP [g/s]; Δt = time increment duration = 0,5 [s]; W_wheel,pos,m = positive wheel work measured in the VTP [kWh].

Positive wheel work measured:

Raw OCR text:
```
Wwheel;pos;m ¼ Xtend
tstart
max ðPwheelðtÒ; 0Ò · Δt
3600
```
Reconstructed equation:
```
                Σ(t=t_start to t_end) [ max(P_wheel(t), 0) × Δt ]
W_wheel,pos,m = ────────────────────────────────────────────────
                                    3600
```

Step 2 — NCV correction:

Raw OCR text:
```
BSFCm;corr ¼ BSFCm · NCV meas 
NCV std
```
Reconstructed equation:
```
BSFC_m,corr = BSFC_m × ( NCV_meas / NCV_std )
```
Where: BSFC_m,corr = measured BSFC in the VTP, corrected for NCV influence [g/kWh]; NCV_meas = NCV of the fuel used in the VTP, per point 3.2 of Annex V [MJ/kg]; NCV_std = standard NCV per Table 5 in point 5.4.3.1 of Annex V [MJ/kg]. This correction is applied for **all fuel types, including Diesel CI engines** (per Table 4a footnote).

Step 3 — run-in correction:

Raw OCR text:
```
BSFCmÄc ¼ BSFCm;corr · minð1;
Ê
ef þ mileage · 1 Ä ef 
15000
Ì
Þ ½g=kWhâ
```
Reconstructed equation:
```
BSFC_m-c = BSFC_m,corr × min[ 1 ,  ef + mileage × (1 − ef)/15000 ]     [g/kWh]
```
Where: BSFC_m-c = brake specific fuel consumption measured and corrected for a run-in phase; **ef = evolution coefficient = 0,98**; mileage = run-in distance [km].
(Note: this is the formula referenced from point 4.1 — it caps the correction at 1 once mileage ≥ 15 000 km, matching the "less than 15 000 km → evolution coefficient applied" rule in point 4.1.)

For **dual-fuel vehicles**, all three steps are performed **separately for both fuels**.

**9.1.3 Determination of the brake specific fuel consumption simulated by the simulation tool (BSFCsim)** ▼M4

- In VTP mode, the measured wheel power is applied as input to the **backward simulation algorithm**.
- Gears engaged during the VTP are determined by calculating engine speeds per gear at the measured vehicle speed, selecting the gear giving the engine speed **closest to the measured engine speed**. For APT transmissions with active torque converter, the **actual gear signal from measurement** is used instead.
- Loss models for axle gear, angle drive, retarders, transmissions, PTOs are applied similarly to the declaration-mode simulation.
- Auxiliary power demand (steering pump, pneumatic system, electric system, HVAC) uses the **generic values implemented per technology** in the simulation tool. Heavy buses: the recorded pneumatic-compressor-status signal is also taken into account.

**Engine cooling fan power demand:**

**Case (a) — non-electrically driven fans:**

Raw OCR text:
```
PfanðtÒ ¼ C1•AÍnfanðtÒ
C2
Î3
•
ÍDfan
C3
Î5
!
•C4
```
Reconstructed equation:
```
P_fan(t) = C1 × [ (n_fan(t)/C2)^3 × (D_fan/C3)^5 ] × C4
```
Where: P_fan = power demand of engine cooling fan [kW]; t = time node [s]; n_fan = measured rotational speed of the fan [rpm]; D_fan = diameter of the fan [mm]; **C1 = 7,32 kW**; **C2 = 1 200 rpm**; **C3 = 810 mm**; **C4** = for heavy buses, the factor from **Table 6**; for other vehicle categories, **C4 = 1**.

**Table 6 — C4 factors for calculation of engine cooling fan power demand for heavy buses**

| Fan drive cluster | Fan control | C4 |
|---|---|---|
| Crankshaft mounted | Electronically controlled visco clutch | 1,05 |
| Crankshaft mounted | Bimetalic controlled visco clutch | 1,05 |
| Crankshaft mounted | Discrete step clutch coupling, 2 stages (0 % / stage 1 / stage 2) | 1,05 |
| Crankshaft mounted | Discrete step clutch coupling, 3 stages (0 % / stage 1 / stage 2 / stage 3) | 1,05 |
| Crankshaft mounted | On/off clutch | 1,05 |
| Belt driven or via transmission | Electronically controlled visco clutch | 1,11 |
| Belt driven or via transmission | Bimetalic controlled visco clutch | 1,11 |
| Belt driven or via transmission | Discrete step clutch coupling, 2 stages (0 % / stage 1 / stage 2) | 1,11 |
| Belt driven or via transmission | Discrete step clutch coupling, 3 stages (0 % / stage 1 / stage 2 / stage 3) | 1,11 |
| Belt driven or via transmission | On/off clutch | 1,11 |
| Hydraulically driven | Variable displacement pump | 1,75 |
| Hydraulically driven | Constant displacement pump | 2,25 |

**Case (b) — electrically driven fans:**

Raw OCR text:
```
Pfan(t) = Pel(t) . 1,43
```
Reconstructed equation (already clean in source):
```
P_fan(t) = P_el(t) × 1,43
```
Where: P_fan = power demand engine cooling fan [kW]; t = time node [s]; P_el = electrical power at the terminals of the engine cooling fan(s), measured per point 5.6.1 *(note: source text references "point 5.6.1"; the enumerated sub-point structure within 5.6 is not separately numbered in this extracted range beyond the single point 5.6 — flagged for cross-check against the primary PDF)*.

- For vehicles with **engine stop-start events** during the VTP, corrections for auxiliary power demand and energy to restart the engine are applied **similarly to the declaration-mode simulation**.
- Simulation of instantaneous fuel consumption **FCsim(t)**, per 0,5 s interval:
  - Interpolated from the **engine fuel map**, using measured engine speed and the resulting engine torque from the backward calculation (including engine rotational inertia calculated from measured engine speed).
  - Engine torque demand is **limited to the certified engine full-load capability**; for those intervals, the backward-simulated wheel power is reduced accordingly (this reduced trace, **Pwheel,sim(t)**, is what feeds into the BSFCsim calculation below).
  - A **WHTC correction factor** is applied, corresponding to the allocation of urban/rural/motorway driving (per definitions 2(8)–2(10)) and the measured vehicle speed.

**BSFCsim formula:**

Raw OCR text:
```
BSFCsim ¼
Ê Ptend
tstart FCsimðtÒ • Δt
Ì
þ FCESS;corr
Wwheel;pos;sim
```
Reconstructed equation:
```
          [ Σ(t=t_start to t_end) FC_sim(t) × Δt ]  +  FC_ESS,corr
BSFCsim = ─────────────────────────────────────────────────────────
                             W_wheel,pos,sim
```
Where: BSFCsim = brake specific fuel consumption determined by the simulation tool for the VTP [g/kWh]; t = time node [s]; FCsim = engine's instantaneous fuel consumption [g/s]; Δt = 0,5 [s]; FCESS,corr = correction of fuel consumption regarding auxiliary power demand resulting from engine stop-start (ESS), as applied in declaration mode [g]; Wwheel,pos,sim = positive wheel work determined by the simulation tool for the VTP [kWh].

Positive wheel work (simulated):

Raw OCR text:
```
Wwheel;pos;sim ¼ Ptend
tstart
maxÄPwheel;simðtÒ;0
Ö
3600 • fs
```
Reconstructed equation:
```
                 Σ(t=t_start to t_end) max( P_wheel,sim(t), 0 )
W_wheel,pos,sim = ──────────────────────────────────────────────
                                  3600 × fs
```
Where: **fs = Simulation rate = 2 [Hz]**; P_wheel,sim = simulated wheel power for the VTP [kW].

For **dual-fuel engines**, BSFCsim is determined **for both fuels separately**.

### 9.2 PART B: Determination of the brake specific pollutant emissions ▼M3/▼M4

Engine power, from measured engine speed and torque:

Raw OCR text:
```
Peng;mðtÒ ¼ 2 · π · nengðtÒ · Teng;mðtÒ
60000
```
Reconstructed equation:
```
P_eng,m(t) = [ 2 × π × n_eng(t) × T_eng,m(t) ] / 60000
```
Where: P_eng,m = measured engine power in the VTP [kW]; t = time node [s]; n_eng = measured rotational engine speed [rpm]; T_eng = measured engine torque [Nm].

Positive engine work measured:

Raw OCR text:
```
Weng;pos;m ¼ Xtend
tstart
max ðPeng;mðtÒ; 0Ò
3600 · fs
```
Reconstructed equation:
```
                Σ(t=t_start to t_end) max( P_eng,m(t), 0 )
W_eng,pos,m  =  ─────────────────────────────────────────
                               3600 × fs
```
Where: W_eng,pos,m = positive engine work measured in the VTP [kWh]; fs = sampling rate = 2 [Hz]; t_start/t_end = first/last time stamp in Table 4 processed data [s].

Brake specific pollutant emissions measured (BSEM):

Raw OCR text:
```
BSEM ¼
Ptend 
tstart EMðtÒ
Weng;pos;m · fs
```
Reconstructed equation:
```
         Σ(t=t_start to t_end) EM(t)
BSEM  =  ───────────────────────────
              W_eng,pos,m × fs
```
Where: BSEM = brake specific pollutant emissions measured in the VTP [g/kWh]; EM = instantaneous pollutant emission mass flow measured during the VTP [g/s].

**Footnotes to Annex Xa (consolidated at end of source range):**
- *(\*) Council Directive 96/53/EC of 25 July 1996 laying down for certain road vehicles circulating within the Community the maximum authorised dimensions in national and international traffic and the maximum authorised weights in international traffic (OJ L 235, 17.9.96, p. 59).*
- *(\*\*) Only if this component needs to be measured in accordance with point 1 of Appendix 1 to Annex II to Regulation (EU) 582/2011.*
- *(\*\*\*) For positive ignition engines.*

---

## 10. Consolidated non-conformity / failure consequence map

Annex Xa does **not** contain a single standalone "penalties/non-conformity" section in this extracted range; the consequences are distributed across the procedure. For audit-tool purposes, here is every point in this range where a failure, deviation or discrepancy triggers a defined consequence:

| Trigger point | Condition | Consequence |
|---|---|---|
| 6.1.1.3 | Discrepancy in certification number or cryptographic hash for a listed component/STU/system file | The **correct** input data file replaces the incorrect one for all further actions |
| 6.1.1.3 | Verification of manufacturer's records file / customer information file **fails**, or **no complete input data set** with correct certificates exists for listed components/STUs/systems | **Verification test ends; vehicle fails the VTP** |
| 7.2.1 | Re-simulation (data-handling verification) finds **any deviation** vs. manufacturer's records file / customer information file results | **Remedial measures referred to in Article 23 apply** *(Article 23 text not in this extracted range — cross-reference only)* |
| 7.3 / Table 5 | **CVTP ratio > 1,075** (after averaging up to 3 tests if retested) | **Vehicle fails the verification testing procedure** |
| 7.3 | **CVTP ratio ≤ 1,075** | **Vehicle passes** |
| 7.3 | **CVTP ratio < 0,925** | No fail declared, but result **must be reported to the Commission** for further analysis to determine the cause |
| 7.3 | First vehicle fails the pass criterion | Manufacturer may request **up to 2 additional tests on same vehicle**, or **2 more similar vehicles tested**; final pass/fail based on **arithmetic average of all CVTP ratios obtained** |
| 6.1.1.1(c) | 99th-percentile engine torque in a declared-limit gear exceeds the declared torque limit by **more than 5 %** (where the limit was subject to verification) | Implicit failure of that specific input-data check (not an independently stated "fail the VTP" sentence in this range, but a failed verification check feeding into the overall input-data verification outcome) |

Because Article 23 (the general "remedial measures" article of the Regulation) is **not within the extracted line range for this file**, its substantive content (e.g., whether it empowers type-approval withdrawal, fines, extended tolerances, or other measures) could not be transcribed here and would need to be sourced from wherever Article 23 appears in the main body of the consolidated text, outside Annex Xa.

---

## Flags for the HDEV sizing/modelling project — read before using this Annex in the tool

1. **Electric and hybrid powertrains are explicitly excluded from the VTP as drafted.** Point 3(c) (▼M4) states unambiguously: *"Hybrid electric, pure electric and fuel cell hybrid vehicles shall not be selected for the verification test."* This means Annex Xa's entire on-road re-verification/tolerance regime (CVTP ratio, Table 5 pass criterion of ≤1,075, the <0,925 Commission-reporting trigger, the fuel-flow/torque/engine-speed measurement chain) is built around and legally scoped to **conventional (ICE) powertrains only**, within this consolidated text as of 01.01.2026. There is no equivalent post-production on-road verification test defined for BEVs/FCEVs/HEVs anywhere in this Annex. If a compliance-verification feature is built into the sizing tool mirroring the EU VTP, it should **not** be presented as applicable to BEV/FCEV/HEV HDVs — that would misrepresent the regulation. Whether a separate instrument (amendment, proposal, or different regulation) establishes an analogous verification regime for electric/fuel-cell HDVs is **unverified from this extracted range** and would need to be checked separately (e.g., later amendments, or Regulation (EU) 2019/1242 CO2 standards machinery, which is a different act).
2. **Only one driven axle vehicles are eligible for VTP selection** (point 3(c)) — another structural scope limit worth noting if the sizing tool ever models VTP applicability by axle configuration.
3. **The core auditable "tolerance" number for ICE HDVs is CVTP ≤ 1,075** (i.e., ±7.5% on the high side) with a secondary ~-7.5% (CVTP < 0,925) trigger for mandatory Commission reporting (not an automatic fail). These two numbers (1,075 and 0,925) are the master tolerance band for "declared vs. verified" CO2/fuel consumption under this Regulation and are highly relevant to any "auditability" claims the HDEV tool wants to make for diesel/gas HDVs.
4. **Run-in/mileage correction**: the evolution coefficient ef = 0,98 and the 15 000 km linear ramp (point 9.1.2, Step 3 above) is the only vehicle-ageing/mileage correction factor defined in this range — it is a straight-line interpolation from 0,98 (at zero km) to 1,0 (at ≥15 000 km) applied as a multiplier on corrected measured BSFC.
5. **Article 23 cross-reference is unresolved in this extraction** — flagged above; needed if the user wants the full non-conformity/remedial-measures text.
6. Several formulas in Section 9 depend on OCR-reconstructed symbols (see the transcription notes at the top). These are mechanical reconstructions from context, not independent derivations, but should still be checked against the primary PDF page images before being encoded into any calculation engine, per project instructions on verifiable sourcing.
