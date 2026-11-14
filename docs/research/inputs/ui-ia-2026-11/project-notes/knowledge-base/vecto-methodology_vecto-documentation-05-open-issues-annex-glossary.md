# VECTO / HDV CO2 Certification Methodology — Part 5: Work Program Status, Open Issues (incl. Hybrid/Advanced-Technology Roadmap), Summary, Literature, Glossary, and Annex Declaration Data

*(Source: same LOT 3 report, Report No. I 07/14/Rex EM, 25.06.2014, Sections 7–11, pages 136–170 of 170 — the final chapters of the document)*

## 7. Overview on Work Performed (Chapter 7)

The report reviews four planned tasks (verbatim task numbers/descriptions):

**Task 1 — Develop software tools** (evaluate component tests + simulate CO2 for the entire HDV): VECTO delivered with "declaration mode" + "engineering mode"; VECTO-CSE delivered in engineering version. Main open work: field-testing by industry, bug fixes; buses' auxiliaries and Automatic Transmission (AT) systems not originally foreseen in LOT3 scope but developed anyway with Daimler, EvoBus, ZF, VOITH, Allison support — a first AT release was committed for before summer 2014.

**Task 2 — "Proof of concept phase"** with limited vehicle testing: performed on two vehicles (Daimler, DAF, supported by JRC/TUG); ongoing tests on a city bus (EvoBus) and 12t delivery truck (Iveco); sensitivity analysis completed for three generic HDV categories (see Part 3). Main open work items (verbatim):
- Cd×A test procedure: on-board anemometer calibration option and tire-RRC speed-dependency (drop from 88→15 km/h) may need amendment after further experience; a separate measurement campaign to test mitigation options was recommended.
- Auxiliary generic data/default values/simulation methods (gear-shift curves for all gearbox types, alternator, air compressor) may need amendment after future testing.
- Methodologies still needing development/testing: a "quality management procedure" to validate declared CO2 (draft "ex-post" procedure exists = the SiCo test, needing further testing); the bus-auxiliary simulation approach (HVAC, air compressor, alternator) not yet in VECTO, led by AEA-Ricardo based on ACEA's prior work; decision on whether/how to integrate CFD into certification (e.g., for generic sidewind correction, and later for assessing small design changes against a measured "parent truck" — noting an assumed ±2% measurement uncertainty would not justify measuring aero effects smaller than ~3%, where simulation could help).

**Task 3 — Support JRC's "Pilot Phase"** (apply the full draft procedure + software with type approval authorities): design discussions ongoing; not executed with TAAs within LOT3 — TUG instead performed vehicle tests directly with Daimler/EvoBus. Main open work: define responsibilities of each stakeholder organization before TAA involvement can proceed.

**Task 4 — Write the final draft text** for the CO2 test procedure / finalize software: draft text available; main open work is collecting/discussing/implementing post-LOT3 feedback.

### Table 38 (Overview of Actions) — Key Status Items Reproduced

| Task | Topic | Status | Comment |
|---|---|---|---|
| 1.1.1 | VECTO-CSE (Constant Speed Evaluator) | Version 2.0 delivered | To be validated by external partners after LOT3 |
| 1.1.2 | Evaluation tool for coast-down tests | Version 1 finalized | No update needed |
| 1.1.3 | WHTC correction factor tool | Included in current VECTO release | Accuracy of engine tests needs further discussion; EURO VI regulation may be insufficient for CO2 purposes |
| 1.1.4 | Prototype "HDV CO2 simulation tool" | VECTO declaration mode finalized | To be validated externally |
| 2.1 | Default input data approaches | Auxiliary models, gear-shift/driver model implemented | Yaw-angle correction does not yet distinguish between HDV classes |
| 2.2 | Full default input data sets | Three generic vehicle models established | To be tested/validated post-LOT3 |
| 2.5 | Test cycles per mission profile | Draft cycle available per profile | ACEA to add more long-haul cycle data |
| 2.6 | Standard bodies/trailers | Defined with CLCCR and VDA | — |
| 4 | Verification procedure (SiCo) | Draft developed, tested on one HDV | Needs more physical-test application |

### Stakeholder Consultation Log (selected — this is a long chronological list in the source; representative entries reproduced to show the breadth and cadence of engagement)

The report lists ~40 meetings/telcos from **Sept 2012 (LOT3 kick-off) through March 2014**, covering: ACEA, tire manufacturers (ETRTO), Bosch (alternators), ZF/Voith/Allison/Daimler (automatic transmissions), DG CLIMA/DG ENTR/DG MOVE, TÜV, and one specific entry of note:

> **"2014.02.11 Audioweb with ACEA on options to include hybrid HDV"**

This is the **only explicit hybrid-related meeting** logged in the consultation history, confirming that hybrid/electrified-HDV methodology was at a very preliminary, exploratory discussion stage as of the report date (June 2014) — not yet an implemented VECTO capability.

### International Cooperation

Contacts established with: **US EPA** (Michael Olechiw, Cleophas Jackson), **JASIC, Japan** (Mr. Osaki, Mr. Morita), University of São Paulo/Brazil (Francisco Nigro), **Cummins USA** (Morgan Andreae), **ICCT** (Ben Sharpe). Discussions covered both conventional HDV CO2 procedures and options for treating Heavy Duty Hybrids (HDH) in a CO2 test procedure, partly via the **HDH expert group for the GTR (Global Technical Regulation) on HDH test procedures**. A dedicated international-harmonization workshop was held 29–30 May 2013 in Varese, organized by JRC.

## 8. Main Open Work for Follow-Up Activities After LOT 3 (Chapter 8) — Including Hybrids

This chapter is the report's own roadmap of what remains unresolved. The most relevant items for an electrified-HDV modelling project are reproduced in detail below (Table 39 in the source, "List of open topics after LOT 3").

### 8.1 General Framing (verbatim intent)

LOT3 was expected to deliver an (almost) complete conventional-truck CO2 test procedure + VECTO software. Coaches were expected to remain partly open (HVAC simulation, since the ACEA proposal was seen as too complex for type approval). **Trucks below 7.5t and bodies/trailers were explicitly out of scope.** Special vehicles (city buses w/ complex equipment, garbage trucks, road sweepers) were flagged as needing case-by-case decisions on inclusion, given rising marginal effort for shrinking marginal CO2 coverage.

### 8.2 Selected Open Topics Table (reproduced, most relevant rows)

| Task/Category | Description | Actions Necessary |
|---|---|---|
| Cd×A test (all HDV) | Validation of RRC change 88→15 km/h not completable within LOT3; may need evaluation-method adaptation and RRC-drum-tested tires prescribed | Funding for RRC tests needed in 2014 |
| Cd×A test (all HDV) | Calibration/evaluation parameter details (torque-signal stability criteria, number of measurement sections) still need verification | Industry-announced 2014 air-drag test series; TUG support via VECTO-CSE |
| Cd×A test (all HDV) | CFD as method for relative Cd×A differences — code/settings harmonization still needed | Decision if CFD is adopted for 2017 legislation or a later phase |
| Engine map | EURO VI accuracy demands (torque/rpm/fuel flow) insufficient for HDV-CO2 certification | Decide: amend EURO VI test procedure, or add a stricter clause in the technical annex |
| Engine map | Test-fuel carbon content/energy density affects results; correction to reference values possible | Suggest following the (then-emerging) WLTP LDV approach; adapting VECTO would be low-effort |
| Transmission testing | Torque-sensor accuracy, error-analysis concept, possible oil-family concept | Ongoing industry activity; review final method |
| Axle testing | Verify generic table values; define worst-case-oil reference test cycle; handle mid-production design changes | Ongoing industry activity |
| Auxiliaries (trucks) | Pneumatic system, steering pump (missing technologies), alternator (missing technologies/power-saving list) tables incomplete | Ongoing ACEA activity; review final numbers |
| Auxiliaries (trucks) | Review options for component-specific (vs. generic) modeling, to harmonize with bus approach | Decide after bus-auxiliary project concludes |
| **VECTO tool** | (a) Update crosswind parameters per newer ACEA data; (b) fine-tune driver-model parameters after industry testing; (c) define reference test cases for future model development; (d) bus-related topics | Perform updates; review final parameters |
| Driver assistance systems (Eco-Roll, Start-Stop, Acceleration Management) | Functionality implemented in VECTO 2.0 code per ACEA description; open: final testing vs. OEM data, criteria for declaring the feature (technical description, verification, driver-deactivation check), decision on generic vs. OEM-specific function parameters | Industry discussion and decision on methods |
| **VECTO mid-/long-term strategy** | Decision needed on: **(i)** Scope 2017 — more professional software design/versioning/support; **(ii)** Scope 2020 (or earlier) — **shift to forward simulation(?)**; **HILS option to be investigated for hybrids and for smart controllers in conventional HDV** | Decision on general strategy needed (possibly early LOT4 focus); may require a feasibility study on switching to forward simulation; ACEA activities already started |
| HDV classes with small sales numbers | Decide: (a) simplified approach (specific values only for weight/transmission ratios/engine) or (b) exclude from certification | Industry discussion |
| Buses/coaches — Automatic transmission with torque converter | Basic model available; feedback update planned June 2014 | Validation with bus measurements still open |
| Buses/coaches — HVAC, air compressor, electric system | Apply ACEA tools to identify relevant model parameters; simplify the complex approach | Study ongoing at AEA-Ricardo |
| Trucks <7.5t (not in LOT3) | Analyze applicability of the HDV framework; make amendments (e.g., engine-test-vs-vehicle-test choice at smallest category) | Many OEM/multistage-production decisions needed |
| Special vehicles (not in LOT3) | Garbage trucks, road sweepers, etc. — decide if PTO power demand should be modeled | Decide which categories to cover; timeline/budget |
| Bodies and trailers | Current procedure gives no incentive for body/trailer manufacturers to improve aero/weight, nor customer-facing info on non-standard bodies | Decide: mandatory or optional coverage; harmonize with standard-HDV procedure |

### 8.3 Advanced Technologies (Not Included in LOT 3) — Full Verbatim Reproduction, Highest Relevance to This Project

> **"Waste heat recovery, hybrids, demand controlled auxiliaries[:] Several technologies which may enter the market in future cannot be treated correctly with the actual methodology (i.e. the technology is not reflected in the efficiency map of the actually measured components or in the power demand simulation from driving resistances and auxiliary energy demand). A method seems to be necessary which defines in future if, how, when, under which responsibility, new technologies can be added to the test procedure."**
> — Action necessary: "Decide responsibilities, timeline, general method to implement new components and technologies in VECTO."

> **"QuickInnovation[:] It is unlikely that new technologies can be integrated in the CO2 test procedure quickly on demand (develop component test procedure, integrate simulation in VECTO, test and validate results). Thus a method may be necessary, which allows a quick assessment of the CO2 benefit of new technologies. The method may e.g. be based on vehicle testing and a measured ratio with/without new technology or via interfaces in VECTO where values could be adapted (such as power demand from alternator if waste heat recovery produces electric energy)."**
> — Action necessary: "Decision if necessary. If yes: timeline, budget for development."

> **"Hybrids[:] In the actual VECTO approach heavy duty hybrid (HDH) vehicles are not foreseen. Since the outcome of the HDH-HILS Gtr. Is now clearer, options have been outlined in cooperation with the GTR HDH group:**
> **i) Coupling of VECTO with the HDH-Hils model**
> **ii) Integration of a generic HDH model in VECTO**
> **iii) Definition of look up tables for FC reduction rates as function of normalised battery capacity and normalised electric motor power.**
> **iv) Others not identified yet"**
> — Comment (verbatim): "Since the HDH HILS method proofed to be quite complex, several HDH may not use the HILS approach for type approval if they use a standard combustion engine which has already EURO VI type approval. Thus option i) may not be applicable to all future HDH models and the alternative options need to be further elaborated towards a certification procedure. This work may be part of a LOT 4."

> **"Predictive systems[:] Predictive systems may decide different operation modes for components depending on the future route characteristics anticipated by actual GPS position and defined destination. It is open if such systems could be considered without a HILS approach. Maybe also the curvature of the CO2-test cycles needs to be defined for such systems."**
> — Action necessary: "Discussion with industry if relevant. If yes, solutions have to be elaborated."

**Analysis for this project (explicitly flagged as the drafting agent's own inference, not stated in the source):** As of this June-2014 report, VECTO's electrification roadmap was at the level of *named options*, not a specified methodology. Option (iii) — "look-up tables for FC reduction rates as a function of normalised battery capacity and normalised electric motor power" — is the closest analogue in this document to a simplified sizing heuristic for hybridized/electrified powertrains, but **no formula, table, or worked example for it is given anywhere in this report.** HILS refers to "Hardware-In-the-Loop Simulation," used in the parallel Heavy Duty Hybrid (HDH) Global Technical Regulation (GTR) work-stream referenced via Hausberger et al. (2012), not detailed here. **Do not treat any of this section as a specified electric-vehicle methodology** — it is a list of unresolved options as of 2014.

## 9. Summary (Chapter 9)

Key points restated by the source's own summary (condensed, not paraphrased beyond trimming repetition already covered in Parts 1–4):
- The HDV-CO2 procedure rests on two pillars: (1) physical component testing, (2) a standardized simulation tool (VECTO) computing FC/CO2 from that component data over standardized virtual test cycles.
- VECTO's physical basis is longitudinal-dynamics engineering; engine speed derives from tire dimensions + transmission ratios via the driver model (manual/AMT/AT support with generic shift strategies); driver model manages acceleration/deceleration wishes, look-ahead braking, over/under-speed, Eco-Roll.
- Generic auxiliary models exist for trucks (alternator, air compressor, steering pump, cooling fan) with technology-dependent selection; bus HVAC covered by a parallel, separate project.
- Component test methods are essentially complete for: engine, gearbox, axle, tire rolling resistance, air drag, vehicle mass.
- Mission-profile/CO2-cycle allocation and generic values depend on HDV class (axle config, vehicle type, max GVW). Separate cycles exist for HGV (long-haul, regional delivery, urban delivery, municipal utility, construction) and buses (heavy urban, urban, suburban, interurban, coach).
- FC is interpolated from the engine map at 1Hz, integrated over the cycle, then WHTC-corrected. Results reported for empty/average-load/full-load vehicles, in g/ton-km and g/km (g/passenger-km for buses).
- VECTO offers **declaration mode** (auto-allocated generic data + cycle once vehicle class is set) and **engineering mode** (fully user-specified, for model validation/recalculation).
- Proof-of-concept testing (2013) showed sufficient accuracy; open issues remain and are catalogued in Chapter 8 (Part 5 of this KB).
- **LOT 3 deliverables (final restated list):** draft technical annex; VECTO software; VECTO-CSE software; draft certification report; this background report.
- Explicit forward note: "the test procedure will have to be regularly updated in future to properly cover more advanced technologies which are assumed to penetrate the market in future" — i.e., the report itself anticipates that electrification (among other advances) will require future methodology extensions beyond what LOT3 delivered.

## 10. Literature (Chapter 10) — Full Reference List as Printed

1. ACEA: *White book on CO2 declaration procedure HDV*; ACEA Working group-CO2HDV; January 2014 (April 2014 version exists but was not used in this report).
2. Clasen D., Grahs T., Lenevu R., Manera J.: "Evaluation of Aerodynamic Noise Propagation", OpenSource CFD 2008 International Conference, Berlin, 5 Dec 2008.
3. Delaunay, Boris N.: *Sur la sphère vide*. Bulletin of Academy of Sciences of the USSR 7 (1934), Nr. 6, pp. 793–800.
4. UN/ECE: **Regulation No 49** of the Economic Commission for Europe of the United Nations (UN/ECE) — Uniform provisions concerning measures against emission of gaseous and particulate pollutants from compression-ignition and positive-ignition engines for use in vehicles; 24.6.2013.
5. ETRTO: *Tyre Rolling Resistance in context of HDV emissions*; presentation, HDV-CO2 meeting, Brussels, 24.04.2014.
6. FAT: *"Verbrauchsreduktion an Nutzfahrzeugkombinationen durch aerodynamische Maßnahmen"*, Forschungsvereinigung Automobiletechnik e.V., FAT Schriftenreihe FAT-237.
7. FAT: *"Aerodynamik von schweren Nutzfahrzeugen, Stand des Wissens"*, FAT Schriftenreihe FAT-241.
8. Fontaras G., Rexeis M., Hausberger S., Kies A., Hammer J., Schulte L., Anagnostopoulos K., Manfredi U., Carriero M., Dilara P.: *Development of a CO2 certification and monitoring methodology for Heavy Duty Vehicles – Proof of Concept report.* JRC report 87799, European Union 2014, ISBN 978-92-79-35146-4, doi: 10.2790/12582.
9. Fontaras G., Dilara P., Berner M., Volers T., Kies A., Rexeis M., Hausberger S.: *An Experimental Methodology for Measuring of Aerodynamic Resistances of Heavy Duty Vehicles in the Framework of European CO2 Emissions Monitoring Scheme*, SAE International Journal of Commercial Vehicles, Vol. 7, Issue 1 (May 2014).
10. Hausberger S., Silberholz G., Dekker H., et al.: *Report of the Research Program on an Emissions and CO2 Test Procedure for Heavy Duty Hybrids (HDH)*; TNO Report 2012 R10679; funded by DG Enterprise and Industry; Delft; 2012. *(This is the primary HDH/hybrid-methodology reference the LOT3 report points to — not itself included in this PDF.)*
11. Hausberger S., Geivanidis S., Vonk W., et al.: *MAC performance test procedure: Coordination of the pilot test phase and follow up towards the drafting of the regulatory text*; Final Report, Study for DG Enterprise; TNO 2013 R10235; Delft, 2013.
12. Islam M., Decker F., de Villiers E., Jackson A., Gines J., Grahs T., Gitt-Gehrke A., Comas J.: "Application of Detached-Eddy Simulation for Automotive Aerodynamics Development", SAE 2009-01-0333, 2009.
13. IVT: *Thermodynamic Script*; Institute for Internal Combustion Engines and Thermodynamics, TU-Graz; 2013.
14. MAC: Hausberger S., Vermeulen R., et al.: *Draft technical annex for a test procedure on air conditioning systems from LDV*; Version 2.6 (28-02-2014).
15. Michelin: *Der Reifen - Rollwiderstand und Kraftstoffersparnis*, Société de Technologie Michelin, F-Clermont-Ferrand, ISBN 2-06-711658-4, first German edition 2005.
16. Pflug H-C.: *Investigations of speed depending tyre rolling resistance in context with air drag tests*; CVE Nutzfahrzeugtechnik; presentation, HDV-CO2 meeting, Brussels, 29.01.2014.
17. Singh, R.: "CFD Simulation of NASCAR Racing Car Aerodynamics," SAE Technical Paper 2008-01-0659, 2008, doi:10.4271/2008-01-0659.
18. UN ECE: *Proposal for a new UN Global Technical Regulation on Worldwide harmonized Light vehicle test Procedures (WLTP)*; ECE/TRANS/WP.29/GRPE/2013/13; Draft, 17 Sept 2013.
19. Vincken D.: *Der Reifen. Rollwiderstand und Kraftstoffersparnis*; ISBN 2067116584; Michelin; 2005.
20. Xinke M.: "Numerical Simulations of the Flow around a Yawing Truck in Wind Tunnel", Master's thesis, Automotive Engineering, Chalmers University of Technology, 2011.

## Glossary of Key Technical Terms (compiled from usage across the document; source-defined terms per Chapter 2 are in Part 1)

| Term | Meaning as used in this document |
|---|---|
| VECTO | "Vehicle Energy consumption Calculation Tool" — the EU's backward-calculating, quasi-stationary longitudinal-dynamics simulation software for HDV CO2/fuel-consumption certification |
| VECTO-CSE | "Constant Speed Evaluator" — companion tool for evaluating Cd×A constant-speed test data |
| WHTC | World Harmonized Transient Cycle — engine dynamometer transient test cycle (per UN/ECE regulation) |
| WHSC | World Harmonized Steady-state Cycle |
| WCF / CF_WHTC | WHTC Correction Factor — corrects steady-state-map-interpolated FC to match measured transient-cycle FC |
| Cd×A (or CdxA) | Product of aerodynamic drag coefficient and frontal area — VECTO's aerodynamic-resistance input parameter |
| RRC | Rolling Resistance Coefficient (tire), per ISO 28580 |
| SiCo test | "Simplified Constant Speed" test — an independent ex-post validation test comparing on-road constant-speed measurements to VECTO's declared-mode predictions |
| HDH | Heavy Duty Hybrid |
| HILS | Hardware-In-the-Loop Simulation (used for HDH GTR type approval, not detailed in this report) |
| GTR | Global Technical Regulation (UN/ECE forum) |
| EMS | European Modular System (long combination vehicles) |
| PT1 | First-order lag (transfer function), used to model transient engine full-load torque build-up |
| Declaration mode | VECTO mode auto-allocating generic data/cycles by HDV class, for official CO2 certification output |
| Engineering mode | VECTO mode allowing full user-specified input, for model validation/recalculation, not for certification |
| Standard body / trailer / semi-trailer | Generic-dimension reference bodies/trailers mandated for the Cd×A test |
| Family concept | Proposed (not finalized in LOT3) approach to reduce test burden by grouping similar vehicle variants under one test |
| CoP | Conformity of Production |
| TAA | Type Approval Authority |
| TS | Technical Service |

## 11. ANNEX: Declaration Data (Chapter 11) — Generic Input Parameter Tables (status: 25 June 2014)

This annex documents VECTO's built-in generic parameter tables for **Declaration Mode**. Fields marked "N/A" in the source were not yet defined at the report date.

### Supported HDV Classes in Declaration Mode (Table 40)

Only these classes could be simulated in Declaration Mode as of 25 June 2014:

| Chassis | Axles | Axle config | Max GVW [t] | Vehicle class |
|---|---|---|---|---|
| Rigid | 2 | 4x2 | 7.5–10 | 1 |
| Rigid | 2 | 4x2 | 10–12 | 2 |
| Rigid | 2 | 4x2 | 12–16 | 3 |
| Rigid | 2 | 4x2 | >16 | 4 |
| Tractor | 2 | 4x2 | >16 | 5 |
| Rigid | 3 | 6x2/2-4 | all weights | 9 |
| Tractor | 3 | 6x2/2-4 | all weights | 10 |

*(Classes 0, 6–8, 11–17 and B1–B6 existed conceptually in the classification scheme, Part 1, but their declaration-mode data tables were still marked N/A at report date.)*

### HDV Class Selection Logic (Table 41, full — includes bus classes)

| Vehicle category | Axle config | GVW min [t] | GVW max [t] | HDV class |
|---|---|---|---|---|
| RigidTruck | 4x2 | 0 | 7.5 | 0 |
| RigidTruck | 4x2 | 7.5 | 10 | 1 |
| RigidTruck | 4x2 | 10 | 12 | 2 |
| RigidTruck | 4x2 | 12 | 16 | 3 |
| RigidTruck | 4x2 | 16 | 99 | 4 |
| Tractor | 4x2 | 16 | 99 | 5 |
| RigidTruck | 4x4 | 7.5 | 16 | 6 |
| RigidTruck | 4x4 | 16 | 99 | 7 |
| Tractor | 4x4 | 16 | 99 | 8 |
| RigidTruck | 6x2 | 0 | 99 | 9 |
| Tractor | 6x2 | 0 | 99 | 10 |
| RigidTruck | 6x4 | 0 | 99 | 11 |
| Tractor | 6x4 | 0 | 99 | 12 |
| RigidTruck | 6x6 | 0 | 99 | 13 |
| Tractor | 6x6 | 0 | 99 | 14 |
| RigidTruck | 8x2 | 0 | 99 | 15 |
| RigidTruck | 8x4 | 0 | 99 | 16 |
| RigidTruck | 8x6 | 0 | 99 | 17 |
| RigidTruck | 8x8 | 0 | 99 | 17 |
| CityBus | 4x2 | 0 | 18 | B1 |
| InterurbanBus | 4x2 | 0 | 18 | B2 |
| Coach | 4x2 | 0 | 18 | B3 |
| CityBus | 6x2 | 18 | 99 | B4 |
| InterurbanBus | 6x2 | 18 | 99 | B5 |
| Coach | 6x2 | 18 | 99 | B6 |

### Mission Profile Assignment (Table 42) — which cycles apply to which HDV class

| HDV Class | Long Haul | Regional Delivery | Urban Delivery | Municipal Utility | Construction | Heavy Urban | Urban | Suburban | Interurban | Coach |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | ✕ | ✕ | | | | | | | | |
| 1 | | ✕ | ✕ | | | | | | | |
| 2 | ✕ | ✕ | ✕ | | | | | | | |
| 3 | | ✕ | ✕ | | | | | | | |
| 4 | ✕ | ✕ | | ✕ | | | | | | |
| 5 | ✕ | ✕ | | | | | | | | |
| 6 | | | | ✕ | ✕ | | | | | |
| 7 | | | | | ✕ | | | | | |
| 8 | | | | | ✕ | | | | | |
| 9 | ✕ | ✕ | | ✕ | | | | | | |
| 10 | ✕ | ✕ | | | | | | | | |
| 11 | | | | | ✕ | | | | | |
| 12 | | | | | ✕ | | | | | |
| 13 | | | | | ✕ | | | | | |
| 14 | | | | | ✕ | | | | | |
| 15 | | | | | ✕ | | | | | |
| 16 | | | | | ✕ | | | | | |
| 17 | | | | | ✕ | | | | | |
| B1 | | | | | | ✕ | ✕ | ✕ | | |
| B2 | | | | | | | | | ✕ | |
| B3 | | | | | | | | | | ✕ |
| B4 | | | | | | ✕ | ✕ | ✕ | | |
| B5 | | | | | | | | | ✕ | |
| B6 | | | | | | | | | | ✕ |

**[Figure 86 description]:** graph of reference loading vs. GVW for HDV classes 1, 2, 3 — two lines: red = Long Haul reference loading, blue = other mission profiles' reference loading, both as a function of the vehicle's maximum GVW.

### Body/Trailer Curb Weights (Table 43, kg) — reproduced (non-blank cells only, by class/mission)

| Class | Long Haul | Regional Delivery | Urban Delivery | Municipal Utility |
|---|---|---|---|---|
| 0 | — | N/A | N/A | — |
| 1 | — | 1600 | 1600 | — |
| 2 | 1900 | 1900 | 1900 | — |
| 3 | — | 2000 | 2000 | — |
| 4 | 7500 | 2100 | — | 2100 |
| 5 | 7500 | 7500 | — | — |
| 9 | 7600 | 2200 | — | 2200 |
| 10 | 7500 | 7500 | — | — |

(Classes 6–8, 11–17, B1–B6: values marked N/A at report date.)

### Reference Loading / Payload (Table 44, kg) — reproduced (non-blank cells)

| Class | Long Haul | Regional Delivery | Urban Delivery | Municipal Utility | Construction |
|---|---|---|---|---|---|
| 0 | — | N/A | N/A | — | — |
| 1 | — | f | f | — | — |
| 2 | f | f | f | — | — |
| 3 | — | f | f | — | — |
| 4 | 14000 | 4400 | — | 4400 | — |
| 5 | 19300 | 12900 | — | — | — |
| 7 | — | — | — | — | 4300 |
| 9 | 17900 | 7100 | — | 7100 | — |
| 10 | 19000 | 12700 | — | — | — |
| 11 | — | — | — | — | 7600 |
| 12 | — | — | — | — | 12100 |
| 16 | — | — | — | — | 11600 |

"f" = payload computed as a function of the vehicle's specific GVW (see Figure 86) for classes 1–3.

### WHTC Weighting Factors (Table 45) — identical to Table 4 in Part 2, reproduced here for Annex completeness

| Mission profile | WF_MW | WF_Road | WF_Urb |
|---|---|---|---|
| Long haul | 89% | 0% | 11% |
| Regional delivery | 53% | 30% | 17% |
| Urban delivery | 4% | 27% | 69% |
| Municipal utility | 2% | 0% | 98% |
| Construction | 6% | 32% | 62% |
| Citybus | 0% | 0% | 100% |
| Interurban bus | 19% | 36% | 45% |
| Coach | 78% | 22% | 0% |

### Axle Load Distribution (Table 46) — format: percent per axle (rigid/truck) or percent-total/number-of-axles (trailer)

| Class | Rigid/Truck (Long haul) | Rigid/Truck (Other) | Trailer (Long haul) | Trailer (Other) |
|---|---|---|---|---|
| 1 | — | 45/55 | 0/0 | 0/0 |
| 2 | 40/60 | 45/55 | 0/0 | 0/0 |
| 3 | — | 40/60 | 0/0 | 0/0 |
| 4 | 20/30 | 45/55 | 50/2 (2 axles, 25% each) | 0/0 |
| 5 | 20/25 | 25/25 | 55/3 (3 axles, ~18.3% each) | 50/3 |
| 9 | 20/30/15 | 35/40/25 | 35/2 | 0/0 |
| 10 | 15/10/20 | 20/10/20 | 55/2 | 50/2 |

(Classes 6–8, 11–17, B1–B6: N/A at report date.)

### Auxiliary Power Consumption Tables (Annex versions — cross-reference to Part 2 for narrative context)

**Table 47 (Electric system):**

| | Long Haul | Regional Delivery | Urban Delivery | Municipal Utility | Construction |
|---|---|---|---|---|---|
| Baseline electric power consumption [W] | 1240 | 1055 | 974 | 974 | 975 |
| LED lights (power-saving) [W] | -50 | -50 | -50 | -50 | -50 |

(Bus classes: N/A.)

**Table 48 (Fan)** — identical to Table 7 in Part 2 (reproduced there in full).

**Table 49/50 (Steering pump power-demand shares and technology scaling factors)** — reproduced Equation 20:
```
P_SP = P_U·U + P_F·F + P_B·B + P_S·S     [W]
```
Scaling factors by technology (Table 50):

| Technology | U | F | B | S |
|---|---|---|---|---|
| Fixed displacement | 1 | 1 | 1 | 1 |
| Variable displacement | 0.6 | 0.6 | 0.6 | 0.6 |
| Hydraulic supported by electric | 0.7 | 1 | 0.9 | 0.9 |
| Dual displacement | N/A | N/A | N/A | N/A |
| Electric | N/A | N/A | N/A | N/A |

*(Note: an "Electric" steering-pump technology category exists in the table but its scaling factors were N/A — undefined — at report date; this is the closest this document comes to referencing an electrified auxiliary component, and even this was not yet quantified.)*

**Table 51 (HVAC power consumption, W)** and **Table 52 (Pneumatic/air compressor system, kW)** — truck values reproduced in Part 2 (Tables 12-adjacent and 9-adjacent respectively); bus values were N/A at report date.

### Wheel/Tire Data (Table 53) — dimensions, inertia [kg·m²], diameter [mm] (selected rows; full list has ~35 tire sizes)

| Tire size | Inertia [kg·m²] | Diameter [mm] |
|---|---|---|
| 9 R 22.5 | 8.9 | 970 |
| 9.00 R 20 | 10.5 | 1018 |
| 11 R 22.5 | 14.4 | 1050 |
| 12 R 22.5 | 16.8 | 1084 |
| 13 R 22.5 | 20 | 1124 |
| 16.00 R 20 | 47.5 | 1343 |
| 295/80 R 22.5 | 15.5 | 1043.5 |
| 315/70 R 22.5 | 14.9 | 1012.5 |
| 385/65 R 22.5 | 19.2 | 1072 |

**[Figure 87 description]:** diagram of how dynamic tire radius is calculated from the wheel/tire dimension code (used with Equation 13 for engine speed, and Equation 10/11 for rotational inertia).

### PT1 Time Constants (Table 54) and Drag Scaling Factors (Table 55) and Acceleration Limits (Table 56)

Fully reproduced already in Part 4 (sections 6.1.1.20 and 6.1.1.11) and Part 4 (section 6.1.1.1) respectively — included there alongside their governing equations for direct usability.

---

## Cross-Cutting Notes for This Project (explicitly flagged as the drafting agent's synthesis, not verbatim source text)

1. **This entire 170-page document is about conventional (ICE) HDVs.** There is no battery model, no e-motor efficiency map, no DC/DC converter model, no fuel-cell model, and no regenerative-braking energy-recovery equation anywhere in it. The word "electric" appears only in the context of the 12V/24V vehicle electrical system (alternator, electric consumers — lights, etc.) and the auxiliary "steering pump — Electric" technology placeholder (Table 50), which was itself undefined (N/A) at report date.
2. **Hybrids (HDH) are explicitly named as future/out-of-scope work** (Chapter 8), with only high-level options sketched (HILS coupling, generic HDH model, or normalized-battery-capacity/normalized-motor-power look-up tables) — none specified in usable detail here.
3. **What IS directly reusable for an electrified-HDV sizing tool from this document:** the vehicle **longitudinal-dynamics/resistance equations** (rolling, air, slope, acceleration resistance — Equations 2–14), the **1Hz backward quasi-static simulation architecture** (M1–M4 module structure), the **driver model concepts** (gear shift logic analog, Overspeed/Eco-Roll/Look-Ahead Coasting analogs for regen-braking strategy design), the **mission-profile/target-speed-cycle concept and the actual 5 HGV + 5 bus cycle validation methodology**, the **HDV classification scheme** (axle config × GVW × body/mission), and the **Cd×A/RRC component-test measurement methodology** (all powertrain-agnostic).
4. **What is NOT in this document and would need a different, later source:** any BEV/PHEV/FCEV component test procedure, battery/e-motor efficiency-map interpolation logic, energy-consumption-cycle definitions for electrified HDVs, or charging-related methodology. If the user has access to more recent VECTO documentation (VECTO 3.x Declaration Mode manuals, ~2019 onward, which added electric/hybrid component models), that would be the correct source for those topics — this LOT3 (2014) report predates that work by roughly 5 years.
