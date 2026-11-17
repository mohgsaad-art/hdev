# Annex VIII — Verifying Air Drag Data: Overview, Definitions, Determination Approach, Test Track & Ambient Conditions, Vehicle Installation

**Source document:** Commission Regulation (EU) 2017/2400 laying down a methodology for determining the CO2 emissions and fuel consumption of heavy-duty vehicles (consolidated text, EUR-Lex)
**CELEX number:** 02017R2400
**Consolidation date:** 01.01.2026 (consolidated version 007.001)
**Range covered in this file:** Annex VIII, Introduction, Sections 1–3.3 (source lines 13477–13764 of the extracted text; page markers 02017R2400 — EN — 01.01.2026 — 007.001 — 329 to 334)
**Amendment markers used in the source:** ►B = original 2017 baseline; ►M1 = Reg (EU) 2019/318; ►M2 = Reg (EU) 2020/1181; ►M3 = Reg (EU) 2022/1379; ►M4 = Reg (EU) 2025/258. Markers are reproduced next to the provisions exactly as they appear in the source (▼ marks the start of a version block, ► marks an inline amendment insertion within a paragraph).

> **Note on transcription:** This Annex is reproduced from an OCR text extraction of the consolidated PDF. Standard prose is transcribed verbatim. Mathematical formulas containing special symbols (√, ≤, ≥, Σ, etc.) are handled in the companion file `09c-annex-viii-input-data-and-validity-criteria.md` with an explicit methodology note, because the OCR extraction garbled those symbols into unrelated characters. No formulas appear in the range covered by this particular file.

---

## 1. Introduction

**▼M3**

> This Annex sets out the test procedures for the determination of air drag data.

---

## 2. Definitions

**▼B** (baseline 2017 text, except item 18 which is ►M4)

For the purposes of this Annex the following definitions shall apply:

1. **'Active aero device'** means measures which are activated by a control unit to reduce the air drag of the total vehicle.
2. **'Aero accessories'** mean optional devices which have the purpose to influence the air flow around the total vehicle.
3. **'A-pillar'** means the connection by a supporting structure between the cabin roof and the front bulkhead.
4. **'Body in white geometry'** means the supporting structure incl. the windshield of the cabin.
5. **'B-pillar'** means the connection by a supporting structure between the cabin floor and the cabin roof in the middle of the cabin.
6. **'Cab bottom'** means the supporting structure of the cabin floor.
7. **'Cabin over frame'** means distance from frame to cabin reference point in vertical Z. Distance is measured from top of horizontal frame to cabin reference point in vertical Z.
8. **'Cabin reference point'** means the reference point (X/Y/Z = 0/0/0) from the CAD coordinate system of the cabin or a clearly defined point of the cabin package e.g. heel point.
9. **'Cabin width'** means the horizontal distance of the left and right B-pillar of the cabin.
10. **'Constant speed test'** means measurement procedure to be carried out on a test track in order to determine the air drag.
11. **'Dataset'** means the data recorded during a single passing of a measurement section.
12. **'EMS'** means the European Modular System (EMS) in accordance with Council Directive 96/53/EC.
13. **'Frame height'** means distance of wheel center to top of horizontal frame in Z.
14. **'Heel point'** means the point which is representing the heel of shoe location on the depressed floor covering, when the bottom of shoe is in contact with the undepressed accelerator pedal and the ankle angle is at 87°. (ISO 20176:2011)
15. **'Measurement area(s)'** means designated part(s) of the test track consisting of at least one measurement section and a preceded stabilisation section.
16. **'Measurement section'** means a designated part of the test track which is relevant for data recording and data evaluation.
17. **'Roof height'** means distance in vertical Z from cabin reference point to highest point of roof w/o sunroof.

**▼M4**

18. **'CFD'** means computational fluid dynamic simulation.

---

## 3. Determination of air drag

### 3.0.1 — Mandatory constant speed test procedure (▼B)

The constant speed test procedure as set out in points 3.1 to 3.7 shall be applied to determine the air drag characteristics. During the constant speed test, the main measurement signals **driving torque, vehicle speed, air flow velocity and yaw angle** shall be measured at two different constant vehicle speeds (low and high speed) under defined conditions on a test track.

- The measurement data recorded during the constant speed test shall be processed in accordance with point 3.8, and
- entered into the **air drag pre-processing tool** in accordance with point 3.9,
- which determines the product of drag coefficient by cross sectional area for zero-crosswind conditions, **Cd·Acr(0)**.

The criteria to obtain valid results during the constant speed test procedure are described in point 3.10.

> **Important structural note for the modelling tool:** the regulation text does **not** spell out the internal road-load / torque-balance equations used by the "air drag pre-processing tool" to convert torque, speed, yaw angle and wind data into Cd·Acr(0). That derivation lives inside the (externally distributed) pre-processing tool software referenced in point 3.9, not in the regulation text itself. The Annex only specifies: (a) what signals must be fed into that tool, (b) the tool's acceptance/validity criteria (point 3.10), and (c) tolerances applied to the tool's output (point 3.0.3). If an auditable re-implementation of Cd·Acr(0) calculation is needed for the HDEV tool, the actual pre-processing tool source/technical documentation referenced in 3.9 must be obtained separately — flagging this as a genuine gap in the regulation text itself, not an omission in this extraction.

### 3.0.2 — Combining constant speed test with CFD (▼M4)

Air drag characteristics may also be determined by combining the Cd·Acr(0) from a constant speed test with an incremental difference **ΔCd·Acr(0)_CFD** obtained by means of CFD. Requirements:

(a) The applied CFD method shall be approved in accordance with **Appendix 10**. For all subsequent applications of the approved CFD method, the boundary conditions set out in point 1, subpoint (i) of subpoint (c) of Appendix 10 shall be complied with.

(b) The application shall only be carried out for vehicles in which the vehicle configuration tested with a constant speed test and the vehicle configuration analysed using CFD are permitted to be within the same air drag family as set out in point 4 of Appendix 5 (medium and heavy lorries) or point 6 of Appendix 5 (heavy buses). The special cases in point 2 of Appendix 5 shall also be taken into account.

(c) The application of CFD shall be limited to **positive** values of ΔCd·Acr(0)_CFD.

(d) A Cd·Acr(0) value generated using CFD shall **not be higher** than the highest value certified with the method set out in point 3.0.1 for a vehicle meeting the same family criteria as set out in point 4.1 of Appendix 5 (medium/heavy lorries) or point 6.1 of Appendix 5 (heavy buses).

### 3.0.3 — Declared value and tolerance (▼B)

The applicant for a certificate shall declare a value **Cd·Adeclared** in a range from equal up to a maximum of **+ 0,2 m²** higher than the air drag characteristics determined in accordance with points 3.0.1 and 3.0.2, if applicable.

- This tolerance accounts for uncertainties in the selection of the parent vehicle as the worst case for all testable members of the family.
- Cd·Adeclared is the reference value for conformity-of-production (CO2/fuel consumption) testing.
- Several declared values Cd·Adeclared can be created based on a single measured Cd·Acr(0), as long as the family provisions in point 4.1 of Appendix 5 (lorries) / point 6.1 of Appendix 5 (buses) are fulfilled.

### 3.0.4 — Standard values when not a family member (▼B)

Vehicles which are not members of a family shall use the standard values for Cd·Adeclared as described in **Appendix 7**. In this case no input data on air drag shall be provided; the allocation of standard values is done automatically by the simulation tool.

---

## 3.1 Test track requirements (▼B)

### 3.1.1 Track geometry

The test track geometry shall be either:

**i. Circuit track, drivable in one direction(\*):**
Two measurement areas, one on each straight part, with a maximum deviation of less than 20 degrees.

> (\*) At least for the misalignment correction of the mobile anemometer (see 3.6), the test track has to be driven in both directions.

**or**

**ii. Circuit or straight-line track, drivable in both directions:**
One measurement area (or two, with the same maximum-20-degree-deviation rule); two sub-options: (a) alternating driving direction after each test section, or (b) after a selectable set of test sections, e.g. ten times driving direction 1 followed by ten times driving direction 2.

### 3.1.2 Measurement sections

Measurement section(s) of a length of **250 m** with a tolerance of **± 3 m** shall be defined on the test track.

### 3.1.3 Measurement areas

A measurement area shall consist of at least one measurement section and a stabilisation section.

- The first measurement section of a measurement area shall be **preceded by a stabilisation section** to stabilise speed and torque.
- Stabilisation section minimum length: **25 m**.
- The test track layout shall enable the vehicle to enter the stabilisation section already at the intended maximum vehicle speed during the test.
- Latitude and longitude of start and end point of each measurement section shall be determined with an accuracy of **better than or equal to 0,15 m, 95 % Circular Error Probable** (DGPS accuracy).

### 3.1.4 Shape of the measurement sections (▼M4)

The measurement section and the stabilisation section have to be a **straight line**.

### 3.1.5 Longitudinal slope (▼M4)

The average longitudinal slope of each measurement and stabilisation section shall not exceed **± 1 per cent**. Slope variations within the measurement section shall not lead to velocity and torque variations above the thresholds specified in 3.10.1.1 items vii and viii.

### 3.1.6 Track surface

The test track shall consist of **asphalt or concrete**. Each measurement section shall have one surface; different measurement sections are allowed to have different surfaces.

### 3.1.7 Standstill area

There shall be a standstill area on the test track to stop the vehicle for zeroing and drift-checking the torque measurement system.

### 3.1.8 Distance to roadside obstacles and vertical clearance

- No obstacles within **5 m** of either side of the vehicle.
- Safety barriers up to **1 m** height are permitted if they are **more than 2,5 m** from the vehicle.
- Bridges or similar structures over the measurement sections are **not allowed**.
- The track must have enough vertical clearance for the anemometer installation specified in 3.4.7.

### 3.1.9 Altitude profile

The manufacturer decides whether altitude correction is applied in the evaluation. If applied, for each measurement section the altitude profile shall meet:

i. Measured at a grid distance **≤ 50 m** in driving direction.
ii. For each grid point, longitude/latitude/altitude measured at least at one point ("altitude measurement point") on each side of the lane centre line, then averaged per grid point.
iii. Grid points provided to the pre-processing tool shall be **< 1 m** from the centre line of the measurement section.
iv. Positioning of altitude measurement points relative to the lane centre line (perpendicular distance, number of points) shall be chosen so the resulting profile is representative of the gradient actually driven.
v. Altitude profile accuracy: **± 1 cm or better**.
vi. Measurement data shall not be older than **10 years**; a resurfacing of the measurement area requires a new altitude profile measurement.

---

## 3.2 Requirements for ambient conditions (▼B, with ►M4/►M3 inline amendments)

### 3.2.1
Ambient conditions shall be measured with the equipment specified in 3.4.

### 3.2.2 — Ambient temperature (►M4 amended)
**Ambient temperature shall be in the range of 5 °C to 25 °C.** This criterion is checked by the air drag pre-processing tool based on the vehicle-measured ambient temperature signal. It applies only to datasets recorded in the low-speed–high-speed–low-speed sequence, not to the misalignment test or warm-up phases.

### 3.2.3 — Ground temperature
Ground temperature shall **not exceed 40 °C**, checked by the pre-processing tool from the vehicle IR sensor signal. Applies only to the low-high-low sequence datasets, not misalignment/warm-up.

### 3.2.4 — Road surface
The road surface shall be **dry** during the low-high-low speed sequence, to provide comparable rolling resistance coefficients.

### 3.2.5 — Wind conditions

Wind conditions shall be within the following range:

**▼M4**
i. Average wind speed: **≤ 4 m/s**
ii. Gust wind speed (1 s central moving average): **≤ 7 m/s**

**▼B**
iii. Average yaw angle (β):
 - **≤ 3 degrees** for datasets recorded in the high speed test
 - **≤ 5 degrees** for datasets recorded during misalignment calibration test

Validity of wind conditions is checked by the pre-processing tool based on signals recorded at the vehicle **after application of the boundary layer correction**. Measurement data collected outside these limits is automatically excluded from the calculation.

---

## 3.3 Installation of the vehicle (▼M3, section header)

### 3.3.1 General installation requirements

**3.3.1.1.** The tested vehicle shall represent the vehicle placed on the market, in accordance with type-approval requirements under **Regulation (EU) 2018/858**. Equipment necessary to execute the test (e.g. overall vehicle height including anemometer) is excluded from this provision.

**3.3.1.2.** Tyre requirements:
- Best or second-best label for fuel efficiency available at the time of test.
- **▼B** Maximum tread depth of **10 mm** on all tyres of the complete vehicle, including the trailer (if applicable).
- Tyres inflated within **± 20 kPa** of the pressure marked on the tyre sidewall, in accordance with Article 3 of **UN Regulation No. 54** (footnote: Regulation No 54 of the UNECE — pneumatic tyres for commercial vehicles and trailers, OJ L 183, 11.7.2008, p. 41).

**3.3.1.3.** Axle alignment shall be within the manufacturer's specifications.

**3.3.1.4.** No active tyre pressure control systems may be used during the low-high-low speed test measurements.

**3.3.1.5.** Active aero devices may remain active during the constant speed test **only if**:
- it has been demonstrated to the approval authority that the device is always activated and effective to reduce air drag at vehicle speeds higher than **60 km/h** (medium and heavy lorries) or **80 km/h** (heavy buses);
- the device is installed and effective in a similar manner on all vehicles of the family.

In all other cases the active aero device must be **fully deactivated** during the constant speed test.

**3.3.1.6.** The vehicle shall not carry provisional features, modifications or devices not representative of real-world use that are aimed at reducing air drag during the test (e.g. sealed bodywork gaps). Modifications aligning the tested vehicle's aerodynamics with the parent vehicle's specification **are** allowed.

**▼M4**
**3.3.1.7.** Aftermarket parts not covered by the vehicle type approval under Regulation (EU) 2018/858 (e.g. sun visors, horns, additional head lights, signal lights, bull bars, ski-boxes) are **not considered** for air drag under this Annex.

**▼M3**
**3.3.1.8.** The vehicle shall be measured **without payload**.

**▼M4**
**3.3.1.9.** Vehicle equipment designed for dynamic charging, as defined in point 3(38) of Annex III, shall be set to the **'retracted'** state if both 'extended' and 'retracted' states are possible.

### 3.3.2 Installation requirements for medium and heavy rigid lorries (▼M3)

**3.3.2.1.** The vehicle chassis shall fit the dimensions of the standard body or semi-trailer defined in **Appendix 4**.

**3.3.2.2.** The vehicle height determined per 3.5.3.1 item vii shall be within the limits specified in **Appendix 3**.

**3.3.2.3.** The minimum distance between the cabin and the box body or semi-trailer shall be in accordance with the manufacturer's requirements and body builder's instructions.

**3.3.2.4.** The cabin and aero accessories shall be adapted to best fit the defined standard body or semi-trailer. Installation of aero accessories (e.g. spoiler) shall follow the manufacturer's instructions.

**3.3.2.5.** The semi-trailer setup shall be as defined in **Appendix 4**.

---

## Cross-references used in this section

- Appendix 3 — Vehicle height requirements for rigid lorries and tractors (see file `09d`)
- Appendix 4 — Standard body and semi-trailer configurations (see file `09d`)
- Appendix 5 — Air drag family definitions and parent vehicle selection (see file `09e`)
- Appendix 7 — Standard values for Cd·Adeclared (see file `09f`)
- Appendix 10 — Approval of the CFD method (see file `09f`)
- Annex III, point 3(38) — definition of dynamic charging equipment states (not in this extraction range — flag for cross-check against Annex III extraction)
- Regulation (EU) 2018/858 — vehicle type-approval framework (external, not reproduced)
- UN Regulation No. 54 — pneumatic tyres for commercial vehicles and trailers (external, not reproduced)

## Figures referenced but not visually extracted

None in this file's range (Figure 1 "Family definition" appears in Appendix 5, covered in file `09e`).
