# VECTO / HDV CO2 Certification Methodology — Part 1: Document Overview, Definitions, and General Approach

> **Source document identification (exact, as printed in the PDF):**
> - **Title:** "Development and validation of a methodology for monitoring and certification of greenhouse gas emissions from heavy duty vehicles through vehicle simulation"
> - **Subtitle on title page:** "Final Report" (note: the second title page, p.2, is headed "Draft Final Report" — the document is internally inconsistent between "Final Report" and "Draft Final Report"; treat it as the **LOT 3 (Draft) Final Report**)
> - **Client / commissioning body:** European Commission, DG CLIMA
> - **Service contract:** CLIMA.C.2/SER/2012/0004
> - **Report number:** I 07/14/Rex EM-I 2012/08 699, dated 25.06.2014
> - **Total length:** 170 pages (page footers read "IVT n of 170")
> - **Elaborated by:** a consortium of TU Graz (TUG) – Institute for Internal Combustion Engines and Thermodynamics (IVT), TÜV-Nord Mobilität, Heinz Steven, and TNO
> - **Authors listed:** Raphael Luz, Martin Rexeis, Stefan Hausberger, Dalibor Jajcevic, Wolfgang Lang (TUG/IVT/ses-tec); Leif-Erik Schulte, Jan Hammer, Lutz Lessmann (TÜV-NORD Mobilität); Mensch van Pim, Ruud Verbeek (TNO); Heinz Steven
> - **Rights notice (verbatim):** "This report must be published in its entirety without any additions or modifications. No extracts may be published or reprinted without the written consent of the author."
> - **Project lineage:** This is the "LOT 3" final report of the project "Reduction and Testing of Greenhouse Gas Emissions from Heavy Duty Vehicles." It builds on "LOT 2" (final report: "Development and testing of a certification procedure for CO2 emissions and fuel consumption of HDV", tender ENV.C.3/SER/2009/0038).
>
> **IMPORTANT SCOPE NOTE (assumption/simplification stated explicitly, not invented):** This 2014 LOT 3 report describes VECTO as it existed for **conventional (internal-combustion-engine) heavy-duty vehicles** — diesel/CNG engines, mechanical transmissions, and conventional auxiliaries. It does **not** contain detailed simulation methodology for battery-electric, fuel-cell, or plug-in-hybrid HDV component models (batteries, e-motors, DC/DC converters, fuel cells). Hybrid HDVs ("HDH") are explicitly named as **out of scope / open future work** (see Part 5 of this knowledge base, "open topics" and "advanced technologies" sections). If the project needs the electrified-VECTO methodology (VECTO versions ≥ 3.x, which added BEV/PHEV/FCEV component models circa 2019+), that is a **different, later document** not present in this PDF — do not assume this report covers it.

---

## 1. Abbreviations (as given in the document, Chapter 1)

| Abbreviation | Meaning |
|---|---|
| A | Cross sectional area [m²] |
| a | Acceleration [m/s²] |
| BSFC | Brake specific fuel consumption [g/kWh] |
| Cx | Concentration of a component x in the exhaust gas [ppm] |
| CSE | Constant Speed Evaluator (evaluation tool for aerodynamic drag tests) |
| EMS | European Modular System |
| EGR | Exhaust gas recirculation |
| GVM | Gross vehicle mass (weight of truck and trailers and eventual payload) |
| GVW | Gross vehicle weight = GVM |
| HDV | Heavy duty vehicle (here above 7.5t max weight) |
| HDE | Heavy duty engine |
| LDV | Light Duty Vehicle |
| Pwheel | Power at the wheel of a vehicle, i.e. sum of driving resistances [W] |
| p | Pressure [bar] |
| Pe | Effective power of the engine [kW] |
| Prated | Rated engine power [kW] |
| RRC | Rolling resistance coefficient |
| SOC | State of charge of the battery [kWh] |
| t [°C] | Temperature [°C] |
| T | Temperature [°K] |
| v | Vehicle velocity [km/h] or [m/s] if specified |
| w | Work over the cycle, usually given in [kWh] |
| WCF | WHTC correction factor |
| WHSC | World Heavy duty steady state test cycle |
| WHTC | World Heavy duty transient test cycle |
| WLTP | Worldwide harmonized Light duty Test procedure |
| ρ | Density [kg/m³] |
| ∆FC | Extra fuel consumption (unit as stated in equation) |

Note: the document explicitly notes that abbreviations tied to specific equations are defined in-text below each formula rather than in this master list. "SOC" (state of charge of the battery, kWh) appears in this general abbreviation list even though the main body of the report does not otherwise develop a battery/SOC model — this is a residual sign that a battery-related feature was anticipated but not elaborated in this LOT3 deliverable.

## 2. Definitions (Chapter 2, verbatim structure)

| Term | Definition (as given) |
|---|---|
| CO2 test cycles | Target speed cycles for 5 HGV mission profiles and for 5 bus mission profiles which are implemented in VECTO to calculate the certification values for HDV |
| SiCo-test | Simplified Constant Speed test (predefined test cycle in VECTO consisting of constant speeds for optional later validation of the CO2 result produced for a HDV) |
| standard bodies | HDV body with generic dimensions and construction designs which have to be used for the aerodynamic drag test for HDV chassis |
| standard trailers | Trailers with generic dimensions and construction designs which have to be used for the aerodynamic drag test for truck-trailer combinations |
| standard semi-trailers | Semi-trailers with generic dimensions and construction designs which have to be used for the aerodynamic drag test for tractor-trailer combinations |
| Vehicle specific data | Input data for the certification procedure which is gained from components used in the vehicle which is certified |
| Generic data | Input data for the certification procedure which is defined similarly for all vehicles which are certified within a HDV class (can be technology specific) |
| Default data | Input data for the certification procedure where the manufacturer can choose if he wants to use the generic data set or if he wants to use vehicle specific test data |

## 3. Introduction (Chapter 3)

- LOT 2 of the project "Reduction and Testing of Greenhouse Gas Emissions from Heavy Duty Vehicles" resulted in a proposal based on **component testing combined with a simulation tool** to calculate CO2 emissions of the entire vehicle.
- LOT 3 further tested and improved this procedure. A "proof of concept" phase in 2013 showed good accuracy for all steps.
- Work was performed in close cooperation with **ACEA** (European Automobile Manufacturers' Association) and supply industry, and with **JRC** (the European Commission's Joint Research Centre).
- **Deliveries of LOT 3 (verbatim list):**
  1. A "draft technical annex" describing the test procedure step by step, as input into future regulatory text (delivered as a **separate document**, not included in this PDF).
  2. The software **"VECTO"** to calculate HDV CO2 emissions from component test data — LOT3 release includes a "declaration mode" with automatic allocation of generic data to the selected HDV class.
  3. The software **"VECTO-CSE"** ("Constant Speed Evaluator") for evaluating aerodynamic drag test data — completely redesigned during LOT 3.
  4. A "draft certification report" describing roughly how the certification process may look.
  5. The report itself (this document), giving background on methods for component tests, evaluation, and simulation, plus an overview of generic data and default values used in VECTO's certification mode.
- The report states it is a **draft** with some incomplete chapters due to time pressure before submission.

## 4. General Description (Chapter 4)

### 4.1. Overall Approach

VECTO is described as a **"vehicle longitudinal dynamics simulation tool."** It calculates actual engine power and engine speed over a test cycle from:
- driving resistances,
- losses in the transmission,
- power demand from auxiliaries.

A **driver model** organizes gear-shift maneuvers, acceleration, and braking behaviour.

**[Figure 1 description]:** "Overview on the VECTO method to calculate representative CO2 and fuel consumption values from component test data." A flow diagram showing how component test data (vehicle mass, tires, engine map, transmission, aerodynamic drag) plus generic data (auxiliaries, body/trailer mass, payload, test cycle) feed into VECTO to output CO2/fuel consumption results.

**Vehicle-specific input data required from standardised component tests** (verbatim list):
- Vehicle mass
- Tires (dimensions and rolling resistance coefficients)
- Engine (fuel flow map, fuel consumption in the WHTC, full-load curve, drag curve)
- Transmission (transmission ratios, loss maps for gearbox and axle, default values optional)
- Aerodynamic drag (Cd×A; generic values usable for some classes)

**Generic values allocated automatically by VECTO** (depending on vehicle class and mission profile; some have different data sets per "technology level"):
- Auxiliaries (alternator, air compressor, steering pump, cooling fan, HVAC) — footnote: "Some of the generic values may be replaced optional later by component specific test data. This needs an agreement on the component test procedure first."
- Mass of the standard bodies and trailers
- Vehicle payload or passenger weight (bus)
- Test cycle

**Default values** (manufacturer may choose default vs. component-specific test data; defaults represent "rather components with worse efficiency," i.e., a conservative/pessimistic fallback that discourages using defaults for components with big fuel-consumption impact):
- Cd×A for low-speed mission profiles
- Losses in the transmission

**Two VECTO operating modes:**
1. **"Declaration mode":** automatically computes fuel consumption and CO2 emissions for all CO2-test cycles allocated to the vehicle, for average payload, full load, and empty driving. Results in g/km and g/ton-km (or g/pass-km for buses). *(Note: the report states "which of these values will be used in a final certification process is not finally decided yet" — i.e., an explicit open question at time of writing.)*
2. **"Engineering mode":** all model parameters can be specified by the user, for extensive testing and comparison with non-standard conditions (e.g., recalculating on-board fuel tests with VECTO).

### HDV Classification System

The HDV class is defined by **category** (rigid, tractor, city bus, coach), **axle configuration**, and **maximum gross weight**.

**Table 1 (Schema of HDV classification for rigid trucks and tractors)** — reproduced:

| Vehicle class | Axles | Axle config | Chassis config | Max GVW [t] | Standard body | Standard trailer | Standard semi-trailer |
|---|---|---|---|---|---|---|---|
| 0**) | 2 | 4x2 | Rigid | >3.5–7.5 | R | | |
| 1 | 2 | 4x2 | Rigid or Tractor | 7.5–10 | R | | |
| 2 | 2 | 4x2 | Rigid or Tractor | >10–12 | R | | B2 (per body table) |
| 3 | 2 | 4x2 | Rigid or Tractor | >12–16 | R | | |
| 4 | 2 | 4x2 | Rigid | >16 | R+T | | T1 |
| 5 | 2 | 4x2 | Tractor | >16 | T+S | | S1 |
| 6 | 3 | 4x4 | Rigid | 7.5–16 | R | (B3) | |
| 7 | 3 | 4x4 | Rigid | >16 | R | (B5) | |
| 8 | 3 | 4x4 | Tractor | >16 | T+S | (S1) | |
| 9 | 3 | 6x2/2-4 | Rigid | all weights | R+T | | T1 |
| 10 | 3 | 6x2/2-4 | Tractor | all weights | T+S | | S2 |
| 11 | 3 | 6x4 | Rigid | all weights | R | (B7) | |
| 12 | 3 | 6x4 | Tractor | all weights | R | (S2) | |
| 13 | 3 | 6x6 | Rigid | all weights | R | (B7) | |
| 14 | 3 | 6x6 | Tractor | all weights | R | (S2) | |
| 15 | 4 | 8x2 | Rigid | all weights | R | (B8) | |
| 16 | 4 | 8x4 | Rigid | all weights | R | (B9) | |
| 17 | 4 | 8x6 & 8x8 | Rigid | all weights | R | (B9) | |

Legend: R = Rigid & Body; R+T = Rigid & Body & Trailer*; T+S = Tractor & Semitrailer; () = no (Cd×A) measurement, only vehicle weight and frontal area.
Footnotes: *) whether the full truck-trailer combination needs a full aero test (vs. simulating from Rigid&Body Cd×A) was "to be clarified." **) suitability of cycles/process for <7.5t GVW "to be evaluated."

**Table 2 (Schema of HDV classification for buses)** — reproduced (partially reconstructed from OCR; structure preserved):
- Classification approach 1: per EU registration (2001/85/EU) — Class I/II/III, and Urban/Suburban/Interurban/Coach categorization
- Classification approach 2 (if vehicle can be registered as): B1 City (Class I, Low Floor / Low Entry def. minimum 2 doors low entrance / Double decker w/o luggage) → cycles Heavy Urban (HU), Urban (UR), Suburban (SU); B2 Interurban (Class II, luggage compartment, floor height ≤900mm) → Interurban (IU); B3 Coach (Class III, floor height >900mm, Double decker) → Coach (CO).

**Table 3 (Schema of the EMS classification for HDV)** — for European Modular System combinations with additional trailers; whether such combinations need to be measured for CdxA, or whether the baseline HDV Cd×A (with a generic correction factor) can be used, was described as still **open**.

### Component Test Procedure Summary (leads into Part 2)

The relevant components requiring **vehicle-specific data** as VECTO input:
- Vehicle mass
- Tires (dimensions, rolling resistance coefficients)
- Engine (fuel flow map, WHTC test results)
- Transmission (transmission ratios, loss maps, optional defaults)
- Aerodynamic drag (Cd×A)

Details of each of these component test procedures are covered in Part 2 of this knowledge base.

---

*(Continued in Part 2: Component Test Procedures — engine, tires, aerodynamics, transmission, axle, auxiliaries)*
