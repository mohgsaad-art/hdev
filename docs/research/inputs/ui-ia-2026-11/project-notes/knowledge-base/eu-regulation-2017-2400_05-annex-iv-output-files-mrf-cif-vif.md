# Annex IV — Model of the Output Files of the Simulation Tool (MRF, CIF, VIF)

**Source document:** Commission Regulation (EU) 2017/2400 of 12 December 2017 implementing Regulation (EC) No 595/2009 of the European Parliament and of the Council as regards the determination of the CO2 emissions and fuel consumption of heavy duty vehicles and amending Directive 2007/46/EC of the European Parliament and of the Council and Commission Regulation (EU) No 582/2011 — **consolidated text**.
**CELEX number:** 02017R2400
**Consolidation date:** 01.01.2026 (consolidated version 007.001, per the EUR-Lex page footers in the extracted range)
**Range covered in this note:** lines 4316–4912 of the full OCR extraction = **ANNEX IV, "MODEL OF THE OUTPUT FILES OF THE SIMULATION TOOL"** in its entirety (Introduction, Definitions, and Parts I–III: Manufacturer's Records File, Customer Information File, Vehicle Information File for heavy buses), ending at the start of Annex V ("Verifying Engine Data").

**Amendment layers referenced in this Annex (per the task brief):**
- ►B = original 2017 baseline (Reg. (EU) 2017/2400)
- ►M1 = Reg. (EU) 2019/318
- ►M2 = Reg. (EU) 2020/1181
- ►M3 = Reg. (EU) 2022/1379
- ►M4 = Reg. (EU) 2025/258

> **Methodological note on amendment markers (read before relying on the "Amendment" columns below).** In the OCR text extraction, amendment state is signalled only by opening markers (`▼M3`, `▼M4`, etc.) with no machine-readable closing `◄` glyphs (the original consolidated PDF uses `►M3 … ◄M3` style brackets around amended passages; the OCR appears to have dropped the closing brackets). This transcription therefore reconstructs the amendment state of each numbered item by treating each `▼Mx` marker as opening a block that is assumed to continue until the next marker is encountered, and treats a marker immediately followed by a page-footer citation line (e.g. "02017R2400 — EN — 01.01.2026 — 007.001 — 9x") with no new content before the next identical marker as a page-break repetition of the *same* state, not a new amendment. **This is an interpretive reconstruction, not a verified legal boundary.** Where precision on exactly which Regulation introduced or last touched a specific field matters (e.g. for a compliance argument), the official consolidated PDF or the individual amending Regulations should be checked directly. Annex IV as a whole was substituted by ►M3 (Regulation (EU) 2022/1379); the markers below mostly track *where ►M4 (Regulation (EU) 2025/258) touched that ►M3 text*.

---

## 1. Introduction (Annex IV, point 1)

> "This Annex describes the models of the manufacturer's records file (MRF), the customer information file (CIF) and the vehicle information file (VIF)."

So Annex IV defines **three distinct output files** that the VECTO simulation tool must produce, each serving a different audience/purpose (established elsewhere in the Regulation's main body, and inferable from Parts I–III below):

| File | Full name | Produced for / contains |
|---|---|---|
| **MRF** | Manufacturer's records file | The manufacturer's complete internal record — essentially *all* input data, input information and results, including sensitive/proprietary component data, cryptographic hashes, and (per Part I heading) explicitly covers "Vehicle, component, separate technical unit and systems data" — i.e. the full technical dossier. |
| **CIF** | Customer information file | A pared-down, customer/certification-facing file — same general structure as the MRF but omitting manufacturer-name/model-identifying fields in favour of fields a customer or type-approval authority would need (e.g. drops "Name and address of manufacturer(s)" from §1.1 position, reorders fields, omits some internal hash cross-references). |
| **VIF** | Vehicle information file | Produced **only for heavy buses**, to carry input data, input information and simulation results **forward between successive stages of staged (multi-step) bus manufacturing** — i.e., from the primary vehicle manufacturer to the body/completing manufacturer(s) — "following the method as described in point 2 of Annex I" (see §4 below). |

---

## 2. Definitions (Annex IV, point 2)

| # | Term | Definition | Amendment |
|---|---|---|---|
| (1) | **'actual charge depleting range'** | The range that can be driven in charge depleting mode based on the usable amount of REESS energy, without any interim charging. | ▼M3 |
| (2) | **'equivalent all electric range'** | The part of the actual charge depleting range that can be attributed to the use of electric energy from the REESS, i.e. without any energy provided by the non-electric propulsion energy storage system. | ▼M3 |
| (3) | **'zero CO2 emissions range'** | The range that can be attributed to energy provided by propulsion energy storage systems considered with zero CO2 impact. | ▼M3 |
| (4) | **'hydrogen range'** | The range that can be driven based on the usable amount of hydrogen. | ▼M4 (Reg. 2025/258) — added, reflecting the addition of fuel-cell hydrogen vehicles to scope |

These four defined terms recur as reported *output ranges* in both the MRF and the CIF (see §3.1 "2.4 Electric and zero emission ranges" and §3.2 "2.5 Electric Ranges" below) and reflect the Regulation's extension over time from pure battery-electric/hybrid vehicles (►M3-era terms 1–3) to hydrogen fuel-cell heavy-duty vehicles (►M4 term 4).

---

## 3. Model of the Output Files (Annex IV, point 3) — structure

Point 3 is introduced under ▼M3 and is organised into three Parts:

- **PART I** — Vehicle CO2 emissions and fuel consumption – **Manufacturer's records file**
- **PART II** — Vehicle CO2 emissions and fuel consumption – **Customer information file**
- **PART III** — Vehicle CO2 emissions and fuel consumption – **Vehicle information file for heavy buses**

Each Part opens with an identical qualifying clause: the file "shall be produced by the simulation tool and shall at least contain the following information, **if applicable for the specific vehicle or manufacturing/certification step**" — i.e. the field lists below are a maximal/superset schema; any given vehicle's actual file only populates the fields relevant to its configuration (e.g. a conventional diesel truck will not populate the REESS, fuel-cell or electric-machine fields).

---

## PART I — Manufacturer's Records File (MRF)

### 1. Vehicle, component, separate technical unit and systems data

#### 1.1. Vehicle data

| # | Field | Amendment |
|---|---|---|
| 1.1.1 | Name and address of manufacturer(s) | ▼M3 |
| 1.1.2 | Vehicle model / Commercial Name | ▼M3 |
| 1.1.3 | Vehicle identification number (VIN) | ▼M3 |
| 1.1.4 | Vehicle category (N2, N3, M3) | ▼M3 |
| 1.1.5 | Axle configuration | ▼M3 |
| 1.1.6 | Technically Permissible Maximum Laden Mass (t) | ▼M3 |
| 1.1.7 | Vehicle group in accordance with Annex I | ▼M3 |
| 1.1.7a | Vehicle (sub-)group for CO2 | ▼M3 |
| 1.1.8 | Corrected actual mass (kg) | ▼M3 |
| 1.1.9 | *[deleted]* — shown in the consolidated text as `▼M4 __________`, i.e. the item formerly at this position was struck by ►M4 (Reg. 2025/258) | ▼M4 (deletion) |
| 1.1.10 | Zero emission heavy-duty vehicle (yes/no) | ▼M3 |
| 1.1.11 | Hybrid electric heavy-duty vehicle (yes/no) | ▼M3 |
| 1.1.12 | Dual-fuel vehicle (yes/no) | ▼M3 |
| 1.1.13 | Sleeper cab (yes/no) | ▼M3 |
| 1.1.14 | HEV architecture (e.g. P1, P2) | ▼M3 |
| 1.1.15 | PEV architecture (e.g. E2, E3) | ▼M3 |
| 1.1.15a | FCHV architecture (e.g. F2, F3) | ▼M4 (added — fuel-cell hybrid vehicle architecture) |
| 1.1.16 | Off-vehicle charging capability (yes/no) | ▼M3 |
| 1.1.17 | **–** (field left blank/reserved in the source text; no label given) | ▼M3 |
| 1.1.18 | *[deleted]* — `▼M4 __________` | ▼M4 (deletion) |
| 1.1.19 | Vehicle technology exempted according to Article 9 | ▼M3 |
| 1.1.20 | Class of bus (e.g. I, I+II etc.) | ▼M3 |
| 1.1.21 | Number passengers upper deck | ▼M3 |
| 1.1.22 | Number passengers lower deck | ▼M3 |
| 1.1.23 | Code for bodywork (e.g. CA, CB) | ▼M3 |
| 1.1.24 | Low Entry (yes/no) | ▼M3 |
| 1.1.25 | Height integrated body (mm) | ▼M3 |
| 1.1.26 | Vehicle length (mm) | ▼M3 |
| 1.1.27 | Vehicle width (mm) | ▼M3 |
| 1.1.28 | Door drive technology (pneumatic, electric, mixed) | ▼M3 |
| 1.1.29 | Tank system in the case of natural gas or hydrogen (e.g. compressed, liquified) | ▼M4 (added) |
| 1.1.30 | Sum net power (only for Article 9 exempted) (kW) | ▼M3 |
| 1.1.31 | Vehicle type approval number | ▼M4 (added) |
| 1.1.32 | Simulation tool licence number | ▼M4 (added) |

Note on 1.1.9/1.1.18: the consolidated text literally shows `▼M4 __________` at both positions — EUR-Lex's convention for "text deleted by this amending act, nothing remains here." The field numbering is **not renumbered** after deletion (gaps 1.1.9 and 1.1.18 are preserved), consistent with how the Official Journal keeps numbering stable across amendments.

#### 1.2. Main engine specifications

| # | Field | Amendment |
|---|---|---|
| 1.2.1 | Engine model | ▼M3 |
| 1.2.2 | Engine certification number | ▼M3 |
| 1.2.3 | Engine rated power (kW) | ▼M3 |
| 1.2.4 | Engine idling speed (1/min) | ▼M3 |
| 1.2.5 | Engine rated speed (1/min) | ▼M3 |
| 1.2.6 | Engine capacity (ltr) | ▼M3 |
| 1.2.7 | Fuel type (Diesel CI / CNG PI / LNG PI) | ▼M3 |
| 1.2.8 | Hash of the engine input data and input information | ▼M3 |
| 1.2.9 | Waste heat recovery system (yes/no) | ▼M3 |
| 1.2.10 | Waste heat recovery type(s) (mechanical/electrical) | ▼M3 |

#### 1.3. Main transmission specifications

| # | Field | Amendment |
|---|---|---|
| 1.3.1 | Transmission model | ▼M3 |
| 1.3.2 | Transmission certification number | ▼M3 |
| 1.3.3 | Main option used for generation of loss maps (Option1/Option2/Option3/Standard values) | ▼M3 |
| 1.3.4 | Transmission type (SMT, AMT, APT-S, APT-P, APT-N) | ▼M3 |
| 1.3.5 | No. of gears | ▼M3 |
| 1.3.6 | Transmission ratio final gear | ▼M3 |
| 1.3.7 | Retarder type | ▼M3 |
| 1.3.8 | Power take off (yes/no) | ▼M3 |
| 1.3.9 | Hash of the transmission input data and input information | ▼M3 |

#### 1.4. Retarder specifications

| # | Field | Amendment |
|---|---|---|
| 1.4.1 | Retarder model | ▼M3 |
| 1.4.2 | Retarder certification number | ▼M3 |
| 1.4.3 | Certification option used for generation of a loss map (standard values/measurement) | ▼M3 |
| 1.4.4 | Hash of the other torque transferring components input data and input information | ▼M3 |

#### 1.5. Torque converter specification

| # | Field | Amendment |
|---|---|---|
| 1.5.1 | Torque converter model | ▼M3 |
| 1.5.2 | Torque converter certification number | ▼M3 |
| 1.5.3 | Certification option used for generation of a loss map (standard values/measurement) | ▼M3 |
| 1.5.4 | Hash of the torque converter input data and input information | ▼M3 |

#### 1.6. Angle drive specifications

| # | Field | Amendment |
|---|---|---|
| 1.6.1 | Angle drive model | ▼M3 |
| 1.6.2 | Angle drive certification number | ▼M3 |
| 1.6.3 | Certification option used for generation of a loss map (standard values/measurement) | ▼M3 |
| 1.6.4 | Angle drive ratio | ▼M3 |
| 1.6.5 | Hash of the additional drivetrain components input data and input information | ▼M3 |

#### 1.7. Axle specifications

| # | Field | Amendment |
|---|---|---|
| 1.7.1 | Axle model | ▼M3 |
| 1.7.2 | Axle certification number | ▼M3 |
| 1.7.3 | Certification option used for generation of a loss map (standard values/measurement) | ▼M3 |
| 1.7.4 | Axle type (e.g. single reduction axle) | ▼M3 |
| 1.7.5 | Axle ratio | ▼M3 |
| 1.7.6 | Hash of the axle input data and input information | ▼M3 |

#### 1.8. Aerodynamics

| # | Field | Amendment |
|---|---|---|
| 1.8.1 | Model | ▼M3 |
| 1.8.2 | Certification option used for generation of CdxA (standard values/measurement) | ▼M3 |
| 1.8.3 | CdxA Certification number (if applicable) | ▼M3 |
| 1.8.3a | CFD method licence number (if applicable) | ▼M4 (added) |
| 1.8.3b | Delta CdxA from CFD (if applicable) | ▼M4 (added) |
| 1.8.4 | CdxA value | ▼M3 |
| 1.8.5 | Hash of the air drag input data and input information | ▼M3 |

Note: 1.8.3a/1.8.3b (CFD-based aerodynamic drag determination, "CFD" = computational fluid dynamics) are additions reflecting a CFD certification pathway introduced alongside standard values/measurement for CdxA.

#### 1.9. Main tyre specifications

| # | Field | Amendment |
|---|---|---|
| 1.9.1 | Tyre dimension axle 1 | ▼M3 |
| 1.9.2 | Tyre certification number axle 1 | ▼M3 |
| 1.9.3 | Specific RRC of all tyres on axle 1 | ▼M3 |
| 1.9.3a | Hash of the tyre input data and input information axle 1 | ▼M3 |
| 1.9.4 | Tyre dimension axle 2 | ▼M3 |
| 1.9.5 | Twin axle (yes/no) axle 2 | ▼M3 |
| 1.9.6 | Tyre certification number axle 2 | ▼M3 |
| 1.9.7 | Specific RRC of all tyres on axle 2 | ▼M3 |
| 1.9.7a | Hash of the tyre input data and input information axle 2 | ▼M3 |
| 1.9.8 | Tyre dimension axle 3 | ▼M3 |
| 1.9.9 | Twin axle (yes/no) axle 3 | ▼M3 |
| 1.9.10 | Tyre certification number axle 3 | ▼M3 |
| 1.9.11 | Specific RRC of all tyres on axle 3 | ▼M3 |
| 1.9.11a | Hash of the tyre input data and input information axle 3 | ▼M3 |
| 1.9.12 | Tyre dimension axle 4 | ▼M3 |
| 1.9.13 | Twin axle (yes/no) axle 4 | ▼M3 |
| 1.9.14 | Tyre certification number axle 4 | ▼M3 |
| 1.9.15 | Specific RRC of all tyres on axle 4 | ▼M3 |
| 1.9.16 | Hash of the tyre input data and input information axle 4 | ▼M3 |

RRC = rolling resistance coefficient. Note the asymmetric numbering as given in the source: axles 1–3 carry the "hash" field as a lettered sub-item (1.9.3a, 1.9.7a, 1.9.11a) immediately after the RRC field, but axle 4's hash field is plain-numbered **1.9.16** rather than "1.9.15a" — this inconsistency is transcribed exactly as it appears in the consolidated text, not corrected.

#### 1.10. Auxiliary specifications

| # | Field | Amendment |
|---|---|---|
| 1.10.1 | Engine cooling fan technology | ▼M3 |
| 1.10.2 | Steering pump technology | ▼M3 |
| 1.10.3 | Electric system | ▼M3 (header) |
| 1.10.3.1 | Alternator technology (conventional, smart, no alternator) | ▼M3 |
| 1.10.3.2 | Max alternator power (smart alternator) (kW) | ▼M3 |
| 1.10.3.3 | Electric storage capacity (smart alternator) (kWh) | ▼M3 |
| 1.10.3.4 | Day running lights LED (yes/no) | ▼M3 |
| 1.10.3.5 | Head lights LED (yes/no) | ▼M3 |
| 1.10.3.6 | Position lights LED (yes/no) | ▼M3 |
| 1.10.3.7 | Brake lights LED (yes/no) | ▼M3 |
| 1.10.3.8 | Interior lights LED (yes/no) | ▼M3 |
| 1.10.4 | Pneumatic system | ▼M3 (header) |
| 1.10.4.1 | Technology | ▼M3 |
| 1.10.4.2 | Compressor ratio | ▼M3 |
| 1.10.4.3 | Smart compression system | ▼M3 |
| 1.10.4.4 | Smart regeneration system | ▼M3 |
| 1.10.4.5 | Air suspension control | ▼M3 |
| 1.10.4.6 | Reagent dosing (exhaust after-treatment) | ▼M3 |
| 1.10.5 | HVAC system | ▼M3 (header) |
| 1.10.5.1 | System configuration number | ▼M3 |
| 1.10.5.2 | Heat pump type driver compartment cooling | ▼M4 (added) |
| 1.10.5.3 | Heat pump type driver compartment heating | ▼M4 (added) |
| 1.10.5.4 | Heat pump type passenger compartment cooling | ▼M4 (added) |
| 1.10.5.5 | Heat pump type passenger compartment heating | ▼M4 (added) |
| 1.10.5.6 | Auxiliary heater power (kW) | ▼M3 |
| 1.10.5.7 | Double glazing (yes/no) | ▼M4 (added) |
| 1.10.5.8 | Adjustable coolant thermostat (yes/no) | ▼M3 |
| 1.10.5.9 | Adjustable auxiliary heater | ▼M3 |
| 1.10.5.10 | Engine waste gas heat exchanger (yes/no) | ▼M3 |
| 1.10.5.11 | Separate air distribution ducts (yes/no) | ▼M3 |
| 1.10.5.12 | Water electric heater | ▼M3 |
| 1.10.5.13 | Air electric heater | ▼M3 |
| 1.10.5.14 | Other heating technology | ▼M3 |

#### 1.11. Engine torque limitations

| # | Field | Amendment |
|---|---|---|
| 1.11.1 | Engine torque limit at gear 1 (% of max engine torque) | ▼M3 |
| 1.11.2 | Engine torque limit at gear 2 (% of max engine torque) | ▼M3 |
| 1.11.3 | Engine torque limit at gear 3 (% of max engine torque) | ▼M3 |
| 1.11.4 | Engine torque limit at gear … (% of max engine torque) — pattern continues per gear | ▼M3 |

#### 1.12. Advanced driver assistance systems (ADAS)

| # | Field | Amendment |
|---|---|---|
| 1.12.1 | Engine stop-start during vehicle stops (yes/no) | ▼M3 |
| 1.12.2 | Eco-roll without engine stop-start (yes/no) | ▼M3 |
| 1.12.3 | Eco-roll with engine stop-start (yes/no) | ▼M3 |
| 1.12.4 | Predictive cruise control (yes/no) | ▼M3 |

#### 1.13. Electric machine system(s) specifications

| # | Field | Amendment |
|---|---|---|
| 1.13.1 | Model | ▼M3 |
| 1.13.2 | Certification number | ▼M3 |
| 1.13.3 | Type (PSM, ESM, IM, SRM) | ▼M3 |
| 1.13.4 | Position (GEN 1, 2, 3, 4) | ▼M3 |
| 1.13.5 | **–** (blank/reserved) | ▼M3 |
| 1.13.6 | Count at position | ▼M3 |
| 1.13.7 | Rated power (kW) | ▼M3 |
| 1.13.8 | Maximum continuous power (kW) | ▼M3 |
| 1.13.9 | Certification option for generation of electric power consumption map | ▼M3 |
| 1.13.10 | Hash of the input data and input information | ▼M3 |
| 1.13.11 | ADC model | ▼M3 |
| 1.13.12 | ADC certification number | ▼M3 |
| 1.13.13 | Certification option used for generation of an ADC loss map (standard values/measurement) | ▼M3 |
| 1.13.14 | ADC ratio | ▼M3 |
| 1.13.15 | Hash of the additional driveline components' input data and input information | ▼M3 |
| 1.13.16 | Boosting limitations | ▼M3 (marked with its own opening marker in the source, suggesting this specific line was inserted/amended distinctly within the M3 substitution) |

ADC = "additional drive component"/auxiliary drive component (per the gearbox/axle component family used elsewhere in VECTO methodology; the Regulation does not spell out the acronym in this Annex).

#### 1.14. Integrated electric powertrain system (IEPC) specifications

| # | Field | Amendment |
|---|---|---|
| 1.14.1 | Model | ▼M3 |
| 1.14.2 | Certification number | ▼M3 |
| 1.14.3 | Rated power (kW) | ▼M3 |
| 1.14.4 | Maximum continuous power (kW) | ▼M3 |
| 1.14.5 | Number of gears | ▼M3 |
| 1.14.6 | Lowest total transmission ratio (highest gear times axle ratio if applicable) | ▼M3 |
| 1.14.7 | Differential included (yes/no) | ▼M3 |
| 1.14.7a | Design type wheel motors (yes/no) | ▼M4 (added) |
| 1.14.8 | Certification option for generation of electric power consumption map | ▼M3 |
| 1.14.9 | Hash of the input data and input information | ▼M3 |

#### 1.15. Rechargeable Energy Storage Systems specifications – Battery

The heading itself ("… – Battery") is a ▼M4 addition/clarification (distinguishing this sub-section from the new 1.16 "– Capacitor" sub-section also added by ►M4); the constituent fields below are ▼M3 content except 1.15.6, which is a ▼M4 addition.

| # | Field | Amendment |
|---|---|---|
| 1.15.1 | Model | ▼M3 |
| 1.15.2 | Certification number | ▼M3 |
| 1.15.3 | Nominal voltage (V) | ▼M3 |
| 1.15.4 | Total storage capacity (kWh) | ▼M3 |
| 1.15.5 | Total usable capacity in simulation (kWh) | ▼M3 |
| 1.15.6 | Certification method (measured, standard values) | ▼M4 (added) |
| 1.15.7 | Hash of the input data and input information | ▼M3 |
| 1.15.8 | StringID (-) | ▼M3 |

#### 1.16. Rechargeable Energy Storage Systems specifications – Capacitor

Entire sub-section newly added by ▼M4.

| # | Field | Amendment |
|---|---|---|
| 1.16.1 | Model | ▼M4 (added) |
| 1.16.2 | Certification number | ▼M4 (added) |
| 1.16.3 | Capacitance (F) | ▼M4 (added) |
| 1.16.4 | Minimum voltage (V) | ▼M4 (added) |
| 1.16.5 | Maximum voltage (V) | ▼M4 (added) |
| 1.16.6 | Hash of the input data and input information | ▼M4 (added) |
| 1.16.7 | Certification method (measured, standard values) | ▼M4 (added) |

#### 1.17. Fuel Cell System(s) specifications

Entire sub-section newly added by ▼M4 — reflects the extension of the Regulation to fuel-cell hydrogen heavy-duty vehicles.

| # | Field | Amendment |
|---|---|---|
| 1.17.1 | Model | ▼M4 (added) |
| 1.17.2 | Certification number | ▼M4 (added) |
| 1.17.3 | Certification method (measured, standard values) | ▼M4 (added) |
| 1.17.4 | Rated power (kW) | ▼M4 (added) |
| 1.17.5 | Count | ▼M4 (added) |

### 2. Mission profile and loading dependent values

#### 2.1. Simulation parameters

Header text (▼M4 addition to the parenthetical scope): "(for each mission profile and loading combination, for OVC-HEVs separately for charge depleting mode, charge sustaining mode and weighted, for OVC-FCHV separately for charge depleting mode and charge sustaining mode)" — OVC = off-vehicle charging; OVC-HEV = off-vehicle-charging hybrid electric vehicle; OVC-FCHV = off-vehicle-charging fuel-cell hybrid vehicle (the latter category is itself evidence of ►M4's extension to fuel-cell vehicles).

| # | Field | Amendment |
|---|---|---|
| 2.1.1 | Mission profile | ▼M3 |
| 2.1.2 | Load (as defined in the simulation tool) (kg) | ▼M3 |
| 2.1.2a | Passenger count | ▼M3 |
| 2.1.3 | Total vehicle mass in simulation (kg) | ▼M3 |
| 2.1.4 | OVC mode (charge depleting, charge sustaining, weighted) | ▼M3 |
| 2.1.5 | Primary vehicle sub-group | ▼M4 (added) |

#### 2.2. Vehicle driving performance and information for simulation quality check

| # | Field | Amendment |
|---|---|---|
| 2.2.1 | Average speed (km/h) | ▼M3 |
| 2.2.2 | Minimum instantaneous speed (km/h) | ▼M3 |
| 2.2.3 | Maximum instantaneous speed (km/h) | ▼M3 |
| 2.2.4 | Maximum deceleration (m/s²) | ▼M3 |
| 2.2.5 | Maximum acceleration (m/s²) | ▼M3 |
| 2.2.6 | Full load percentage of driving time | ▼M3 |
| 2.2.7 | Total number of gear shifts | ▼M3 |
| 2.2.8 | Total driven distance (km) | ▼M3 |
| 2.2.9 | Average gearbox efficiency (%) | ▼M4 (added) |
| 2.2.10 | Average axle efficiency (%) | ▼M4 (added) |

#### 2.3. Fuel and energy consumption (per fuel type and electric energy) and CO2 results (total)

| # | Field | Amendment |
|---|---|---|
| 2.3.1 | Fuel consumption (g/km) | ▼M3 |
| 2.3.2 | Fuel consumption (g/t-km) | ▼M3 |
| 2.3.3 | Fuel consumption (g/p-km) | ▼M3 |
| 2.3.4 | Fuel consumption (g/m³-km) | ▼M3 |
| 2.3.5 | Fuel consumption (l/100km) | ▼M4 |
| 2.3.6 | Fuel consumption (l/t-km) | ▼M4 |
| 2.3.7 | Fuel consumption (l/p-km) | ▼M4 |
| 2.3.8 | Fuel consumption (l/m³-km) | ▼M4 |
| 2.3.9 | Energy consumption (MJ/km, kWh/km) | ▼M4 |
| 2.3.10 | Energy consumption (MJ/t-km, kWh/t-km) | ▼M4 |
| 2.3.11 | Energy consumption (MJ/p-km, kWh/p-km) | ▼M4 |
| 2.3.12 | Energy consumption (MJ/m³-km, kWh/m³-km) | ▼M4 |
| 2.3.13 | CO2 (g/km) | ▼M4 |
| 2.3.14 | CO2 (g/t-km) | ▼M4 |
| 2.3.15 | CO2 (g/p-km) | ▼M4 |
| 2.3.16 | CO2 (g/m³-km) | ▼M4 |
| 2.3.17 | Fuel and energy consumption of auxiliary heater in case of zero emission vehicle (g/km, g/p-km, l/100km, l/p-km, MJ/km, MJ/p-km) | ▼M4 (added) |
| 2.3.18 | CO2 of auxiliary heater in case of zero emission vehicle (g/km, g/p-km) | ▼M4 (added) |
| 2.3.19 | Utility factor | ▼M4 (added) |

> Note per the marker-tracking methodology above: fields 2.3.5–2.3.16 fall in a block opened by a ▼M4 marker in the source immediately after 2.3.4, before the list resumes with no further marker until 2.3.17's explicit "(added)" context; however, 2.3.5–2.3.16 (volumetric/energy/CO2 unit conversions) read as a stable reformatting of pre-existing metrics rather than wholly new fields, so this may reflect a renumbering/restructuring by ►M4 rather than new substantive fields — this is an interpretive flag, not a confirmed fact; verify against the official text if the distinction matters.

#### 2.4. Electric and zero emission ranges (for beginning and end of life)

| # | Field | Amendment |
|---|---|---|
| 2.4.1 | Actual charge depleting range (km) | ▼M3 |
| 2.4.2 | Equivalent all electric range (km) | ▼M3 |
| 2.4.3 | Zero CO2 emission range (km) | ▼M3 |
| 2.4.4 | Hydrogen range (km) | ▼M4 (added) |

### 3. Software information

| # | Field | Amendment |
|---|---|---|
| 3.1 | Simulation tool version (X.X.X) | ▼M3 |
| 3.2 | Date and time of the simulation | ▼M3 |
| 3.3 | Cryptographic hash simulation tool input information and input data of the primary vehicle (if applicable) | ▼M3 |
| 3.4 | Cryptographic hash of the manufacturer's record file of the primary vehicle (if applicable) | ▼M3 |
| 3.5 | Cryptographic hash of the vehicle information file as produced by the simulation tool (if applicable) | ▼M3 |
| 3.6 | Cryptographic hash of the simulation tool input information and input data | ▼M3 |
| 3.7 | Cryptographic hash of the manufacturer's records file | ▼M3 |

Fields 3.3–3.5 are the key cross-reference mechanism for **staged bus manufacturing** (see §4 below): a non-primary-vehicle manufacturer's MRF must carry forward the cryptographic hashes that trace back to the **primary vehicle's** input data/information, MRF, and VIF, so the full simulation chain across manufacturing stages is auditable.

---

## PART II — Customer Information File (CIF)

The CIF mirrors the MRF's structure closely but (a) drops manufacturer-identifying fields from the top of the vehicle-data block in favour of VIN/category/mass fields, (b) consolidates most component data into a single "1.2 Component, separate technical unit and systems data" block rather than per-component sub-sections, and (c) omits internal hash fields that are MRF-only (e.g. no per-component "hash of input data" fields — only top-level cryptographic hashes at the end, §3).

### 1. Vehicle, component, separate technical unit and systems data

#### 1.1. Vehicle data

| # | Field | Amendment |
|---|---|---|
| 1.1.1 | Vehicle identification number (VIN) | ▼M3 |
| 1.1.2 | Vehicle category (N2, N3, M3) | ▼M3 |
| 1.1.3 | Axle configuration | ▼M3 |
| 1.1.4 | Technically Permissible Maximum Laden Mass (t) | ▼M3 |
| 1.1.5 | Vehicle group in accordance with Annex I | ▼M3 |
| 1.1.5a | Vehicle (sub-)group for CO2 | ▼M3 |
| 1.1.5b | Total propulsion power relevant for subgroup allocation | ▼M4 (added) |
| 1.1.6 | Name and address(es) of manufacturer(s) | ▼M3 |
| 1.1.7 | Model | ▼M3 |
| 1.1.8 | Corrected actual mass (kg) | ▼M3 |
| 1.1.9 | *[deleted]* — `▼M4 __________` | ▼M4 (deletion) |
| 1.1.10 | Zero emission heavy-duty vehicle (yes/no) | ▼M3 |
| 1.1.11 | Hybrid electric heavy-duty vehicle (yes/no) | ▼M3 |
| 1.1.12 | Dual-fuel vehicle (yes/no) | ▼M3 |
| 1.1.12a | Waste Heat recovery (yes/no) | ▼M3 |
| 1.1.13 | Sleeper cab (yes/no) | ▼M3 |
| 1.1.14 | HEV architecture (e.g. P1, P2) | ▼M3 |
| 1.1.15 | PEV architecture (e.g. E2, E3) | ▼M3 |
| 1.1.15a | FCHV architecture (e.g. F2, F3) | ▼M4 (added) |
| 1.1.16 | Off-vehicle charging capability (yes/no) | ▼M3 |
| 1.1.17 | **–** (blank/reserved) | ▼M3 |
| 1.1.18 | *[deleted]* — `▼M4 __________` | ▼M4 (deletion) |
| 1.1.19 | Vehicle technology exempted from Article 9 | ▼M3 |
| 1.1.20 | Class of bus (e.g. I, I+II etc.) | ▼M3 |
| 1.1.21 | Total number of registered passengers | ▼M3 |
| 1.1.22 | Vehicle type approval number | ▼M3 |

Note: the CIF's 1.1.22 ("Vehicle type approval number") is marked ▼M3 here, whereas the equivalent field in the MRF (1.1.31, same label) is marked ▼M4 — i.e. this field was apparently already present in the CIF under the M3 restructuring but only added to the MRF later under M4; this discrepancy is transcribed as found, not reconciled, and is worth the user's attention if cross-checking field parity between the two files.

#### 1.2. Component, separate technical unit and systems data

| # | Field | Amendment |
|---|---|---|
| 1.2.1 | Engine rated power (kW) | ▼M3 |
| 1.2.2 | Engine capacity (ltr) | ▼M3 |
| 1.2.3 | Fuel type (Diesel CI/CNG PI/LNG PI) | ▼M3 |
| 1.2.4 | Transmission values (measured/standard) | ▼M3 |
| 1.2.5 | Transmission type (SMT, AMT, APT, none) | ▼M3 |
| 1.2.6 | No. of gears | ▼M3 |
| 1.2.7 | Retarder (yes/no) | ▼M3 |
| 1.2.8 | Axle ratio | ▼M3 |
| 1.2.9 | Average rolling resistance coefficient (RRC) of all tyres of the motor vehicle | ▼M3 |
| 1.2.10a | Tyre dimension for each axle of the motor vehicle | ▼M3 |
| 1.2.10b | Fuel efficiency class(es) of the tyres in accordance with Regulation (EU) 2020/740 for each axle of the motor vehicle | ▼M3 |
| 1.2.10c | Tyre certification number for each axle of the motor vehicle | ▼M3 |
| 1.2.11 | Engine stop-start during vehicle stops (yes/no) | ▼M3 |
| 1.2.12 | Eco-roll without engine stop-start (yes/no) | ▼M3 |
| 1.2.13 | Eco-roll with engine stop-start (yes/no) | ▼M3 |
| 1.2.14 | Predictive cruise control (yes/no) | ▼M3 |
| 1.2.15 | Electric machine system(s) total rated propulsion power (kW) | ▼M3 |
| 1.2.16 | Electric machine system total maximum continuous propulsion power (kW) | ▼M3 |
| 1.2.17 | REESS total storage capacity (kWh) | ▼M3 |
| 1.2.18 | REESS useable storage capacity in simulation (kWh) | ▼M3 |
| 1.2.19 | Fuel cell system(s) total rated power (kW) | ▼M4 (added) |

1.2.10b is a direct cross-reference to **Regulation (EU) 2020/740** (the EU tyre labelling regulation) — i.e. the CIF must report the tyres' EU fuel-efficiency label class, not merely their RRC value, giving the customer a regulatorily standardized comparator.

#### 1.3. Auxiliary configuration

| # | Field | Amendment |
|---|---|---|
| 1.3.1 | Steering pump technology | ▼M3 |
| 1.3.2 | Electric system | ▼M3 (header) |
| 1.3.2.1 | Alternator technology (conventional, smart, no alternator) | ▼M3 |
| 1.3.2.2 | Max alternator power (smart alternator) (kW) | ▼M3 |
| 1.3.2.3 | Electric storage capacity (smart alternator) (kWh) | ▼M3 |
| 1.3.3 | Pneumatic system | ▼M3 (header) |
| 1.3.3.1 | Smart compression system | ▼M3 |
| 1.3.3.2 | Smart regeneration system | ▼M3 |
| 1.3.4 | HVAC system | ▼M4 (header, added) |
| 1.3.4.1 | System configuration | ▼M4 (added) |
| 1.3.4.2 | Auxiliary heater power (kW) | ▼M4 (added) |
| 1.3.4.3 | Double glazing (yes/no) | ▼M4 (added) |

### 2. CO2 emissions and fuel consumption of the vehicle

Header text (▼M4 extension of scope, matching the MRF's §2.1 wording): "(for each mission profile and loading combination, for OVC-HEVs separately for charge depleting mode, charge sustaining mode and weighted, for OVC-FCHV separately for charge depleting mode and charge sustaining mode)"

#### 2.1. Simulation parameters

| # | Field | Amendment |
|---|---|---|
| 2.1.1 | Mission profile | ▼M3 |
| 2.1.2 | Payload (kg) | ▼M3 |
| 2.1.3 | Passenger information | ▼M3 (header) |
| 2.1.3.1 | Number of passengers in simulation (-) | ▼M3 |
| 2.1.3.2 | Mass of passengers in simulation (kg) | ▼M3 |
| 2.1.4 | Total vehicle mass in simulation (kg) | ▼M3 |
| 2.1.5 | OVC mode (charge depleting, charge sustaining, weighted) | ▼M3 |

#### 2.2. Average speed (km/h)

Single field, ▼M3.

#### 2.3. Fuel and energy consumption results (per fuel type and electric energy)

| # | Field | Amendment |
|---|---|---|
| 2.3.1 | Fuel consumption (g/km) | ▼M3 |
| 2.3.2 | Fuel consumption (g/t-km) | ▼M3 |
| 2.3.3 | Fuel consumption (g/p-km) | ▼M3 |
| 2.3.4 | Fuel consumption (g/m³-km) | ▼M3 |
| 2.3.5 | Fuel consumption (l/100km) | ▼M3 |
| 2.3.6 | Fuel consumption (l/t-km) | ▼M3 |
| 2.3.7 | Fuel consumption (l/p-km) | ▼M3 |
| 2.3.8 | Fuel consumption (l/m³-km) | ▼M3 |
| 2.3.9 | Energy consumption (MJ/km, kWh/km) | ▼M3 |
| 2.3.10 | Energy consumption (MJ/t-km, kWh/t-km) | ▼M3 |
| 2.3.11 | Energy consumption (MJ/p-km, kWh/p-km) | ▼M3 |
| 2.3.12 | Energy consumption (MJ/m³-km, kWh/m³-km) | ▼M3 |

#### 2.4. CO2 results (for each mission profile and loading combination)

| # | Field | Amendment |
|---|---|---|
| 2.4.1 | CO2 (g/km) | ▼M3 |
| 2.4.2 | CO2 (g/t-km) | ▼M3 |
| 2.4.3 | CO2 (g/p-km) | ▼M3 |
| *(2.4.4 — not present)* | **Gap in source numbering**: the list jumps from 2.4.3 directly to 2.4.5 with no 2.4.4 shown in the consolidated text. Transcribed exactly as the source reads; this may be a drafting/OCR artifact in the Official Journal's consolidated version itself — flagged for the user's attention, not corrected. | — |
| 2.4.5 | CO2 (g/m³-km) | ▼M3 |
| 2.4.6 | Fuel and energy consumption of auxiliary heater in case of zero emission vehicle (g/km, g/p-km, l/100km, l/p-km, MJ/km, MJ/p-km) | ▼M4 (added) |
| 2.4.7 | CO2 of auxiliary heater in case of zero emission vehicle (g/km, g/p-km) | ▼M4 (added) |
| 2.4.8 | Utility factor | ▼M4 (added) |

#### 2.5. Electric Ranges (for begin and end of life)

| # | Field | Amendment |
|---|---|---|
| 2.5.1 | Actual charge depleting range (km) | ▼M3 |
| 2.5.2 | Equivalent all electric range (km) | ▼M3 |
| 2.5.3 | Zero CO2 emission range (km) | ▼M3 |
| 2.5.4 | Hydrogen range (km) | ▼M4 (added) |

#### 2.6. Weighted results

| # | Field | Amendment |
|---|---|---|
| 2.6.1 | Specific CO2 emissions (g/t-km) | ▼M4 (added) |
| 2.6.2 | Specific electric energy consumption (kWh/t-km) | ▼M3 |
| 2.6.3 | Average payload value (t) | ▼M3 |
| 2.6.4 | Specific CO2 emissions (g/p-km) | ▼M4 (added) |
| 2.6.5 | Specific electric energy consumption (kWh/p-km) | ▼M3 |
| 2.6.6 | Average passenger count (p) | ▼M3 |
| 2.6.7 | Actual charge depleting range for beginning and end of life (km) | ▼M4 (added) |
| 2.6.8 | Equivalent all electric range for beginning and end of life (km) | ▼M4 (added) |
| 2.6.9 | Zero CO2 emission range for beginning and end of life (km) | ▼M4 (added) |
| 2.6.10 | Hydrogen range (km) | ▼M3 |
| 2.6.11 | CO2 (g/km) | ▼M3 |
| 2.6.12 | CO2 (g/m³-km) | ▼M3 |
| 2.6.13 | Fuel consumption (g/km) | ▼M3 |
| 2.6.14 | Fuel consumption (g/t-km) | ▼M3 |
| 2.6.15 | Fuel consumption (g/p-km) | ▼M3 |
| 2.6.16 | Fuel consumption (g/m³-km) | ▼M3 |
| 2.6.17 | Fuel consumption (l/100km) | ▼M3 |
| 2.6.18 | Fuel consumption (l/t-km) | ▼M3 |
| 2.6.19 | Fuel consumption (l/p-km) | ▼M3 |
| 2.6.20 | Fuel consumption (l/m³-km) | ▼M3 |
| 2.6.21 | Energy consumption (MJ/km, kWh/km) | ▼M3 |
| 2.6.22 | Energy consumption (MJ/t-km) | ▼M3 |
| 2.6.23 | Energy consumption (MJ/p-km) | ▼M3 |
| 2.6.24 | Energy consumption (MJ/m³-km, kWh/m³-km) | ▼M3 |

Note on 2.6.10 "Hydrogen range (km)" marked ▼M3 here despite hydrogen range being defined only under ▼M4 elsewhere (Annex IV point 2(4), and CIF 2.5.4): this field sits inside a block whose last explicit marker (per the tracked state) was ▼M4 at 2.6.9 reverting to ▼M3 — it is unclear from the OCR text whether 2.6.10 is genuinely M3-vintage (unlikely, since hydrogen range as a concept is M4) or whether the marker-tracking methodology has mis-assigned it due to a missed/dropped marker in the OCR. **Flagged as an ambiguity** — treat 2.6.10's amendment attribution as uncertain; the field itself (hydrogen range, weighted) is substantively a ►M4-era addition regardless of the exact marker placement.

### 3. Software information

| # | Field | Amendment |
|---|---|---|
| 3.1 | Simulation tool version | ▼M3 |
| 3.2 | Date and time of the simulation | ▼M3 |
| 3.3 | Cryptographic hash of the simulation tool input information and input data of the primary vehicle (if applicable) | ▼M3 |
| 3.4 | Cryptographic hash of the manufacturer's records file of the primary vehicle (if applicable) | ▼M3 |
| 3.5 | Cryptographic hash of the vehicle simulation tool input information and input data | ▼M3 |
| 3.6 | Cryptographic hash of the manufacturer's records file | ▼M3 |
| 3.7 | Cryptographic hash of the customer information file | ▼M3 |

As in the MRF, fields 3.3–3.4 are the staged-manufacturing cross-reference mechanism, tying the CIF back to the **primary vehicle's** simulation input data and MRF.

---

## PART III — Vehicle Information File (VIF) for Heavy Buses

> "The vehicle information file shall be produced in the case of **heavy buses** to transfer the relevant input data, input information and simulation results to subsequent certification steps following the method as described in **point 2 of Annex I**."

This Part's header/intro is marked ▼M4; its body splits into two cases: **(1) primary vehicle** and **(2) interim/complete/completed vehicle**, which maps directly onto the **staged manufacturing** concept for buses (chassis/primary-vehicle manufacturer → body builder(s)/completing manufacturer(s)) referenced in Annex I point 2.

The VIF "shall at least contain the following content":

### 1. In the case of a primary vehicle

| # | Field | Amendment |
|---|---|---|
| 1.1 | Input data and input information as set out in **Annex III** for the primary vehicle, **except**: engine fuel map; engine correction factors WHTC_Urban, WHTC_Rural, WHTC_Motorway, BFColdHot, CFRegPer; torque converter characteristics; loss maps for transmission, retarder, angle drive and axle; electric power consumption map(s) for electric motor systems and IEPC; electric loss parameters for REESS; fuel map for FCS | ▼M4 |
| 1.2 | For each mission profile and loading condition: | ▼M3 (header) |
| 1.2.1 | Total vehicle mass in simulation (kg) | ▼M3 |
| 1.2.2 | Number of passengers in simulation (-) | ▼M3 |
| 1.2.3 | Energy consumption (MJ/km) | ▼M3 |
| 1.3 | Software information | ▼M3 (header) |
| 1.3.1 | Simulation tool version | ▼M3 |
| 1.3.2 | Date and time of the simulation | ▼M3 |
| 1.4 | Cryptographic hashes | ▼M3 (header) |
| 1.4.1 | Cryptographic hash of the manufacturers records file of the primary vehicle | ▼M3 |
| 1.4.2 | Cryptographic hash of the vehicle information file | ▼M3 |

**Interpretation of 1.1 (the exclusion list):** the VIF for a primary vehicle passes forward *most* of the Annex III (type-approval input data) record, but deliberately **withholds** the most granular/proprietary component maps and correction factors — the raw engine fuel map, the WHTC-cycle correction factors (urban/rural/motorway, cold/hot balancing factor, regeneration period correction factor), torque converter characteristics, transmission/retarder/angle-drive/axle loss maps, electric machine and IEPC power-consumption maps, REESS electric loss parameters, and the fuel-cell-system (FCS) fuel map. This is consistent with protecting the primary-vehicle manufacturer's confidential component-level test data from the downstream body-builder, while still giving that downstream manufacturer everything it needs to run its own simulation step (vehicle mass, passenger counts, energy consumption per mission profile) and to verify the chain of custody via the cryptographic hashes.

WHTC = World Harmonized Transient Cycle (engine-level emissions test cycle referenced for its correction factors here). FCS = Fuel Cell System.

### 2. For each interim, complete or completed vehicle

| # | Field | Amendment |
|---|---|---|
| 2.1 | Input data and input information as set out for the complete or completed vehicle in **Annex III** and which was provided by the particular manufacturer | ▼M3 |
| 2.2 | Software information | ▼M3 (header) |
| 2.2.1 | Simulation tool version | ▼M3 |
| 2.2.2 | Date and time of the simulation | ▼M3 |
| 2.3 | Cryptographic hashes | ▼M3 (header) |
| 2.3.1 | Cryptographic hash of the vehicle information file | ▼M3 |

Note that case 2 does **not** list a cryptographic hash of a "manufacturer's records file" field analogous to 1.4.1 — only the VIF's own hash (2.3.1) is specified. Each subsequent manufacturer in the staged-build chain thus re-stamps the VIF with its own input data/information (per Annex III, for whatever stage of completion it performs) and its own VIF hash, chaining forward from the primary vehicle's VIF.

---

## 4. How MRF, CIF and VIF relate to each other and to the staged-manufacturing process (Annex I, point 2)

Based strictly on what this Annex's text itself states (no outside assumption beyond connecting its own cross-references):

1. **MRF** is the manufacturer's complete internal record (all component data, all hashes, all mission-profile results) — the audit trail of record for the manufacturer's own compliance file.
2. **CIF** is derived from/parallel to the MRF but trimmed for the customer/certification-facing audience — it still carries forward hashes of the *primary vehicle's* simulation input data and MRF (CIF §3.3–3.4) so that a customer or authority receiving a CIF for a staged (multi-manufacturer) vehicle can cryptographically verify that the completed vehicle's numbers trace back to a specific, unaltered primary-vehicle simulation.
3. **VIF** exists specifically to **bridge** the primary-vehicle manufacturer and the body-builder/completing manufacturer(s) in staged bus manufacturing: it carries forward the subset of Annex III input data the next manufacturer needs (withholding the most sensitive component-level maps/correction factors, per Part III §1.1), the mission-profile-level simulation outputs needed to continue the simulation chain, and cryptographic hashes that let every downstream step (and ultimately the final CIF's §3.3–3.4) verify the chain back to the primary vehicle's original MRF and VIF.
4. The cryptographic-hash fields recur in all three files (MRF §3.3–3.7; CIF §3.3–3.7; VIF §1.4/§2.3) and are the explicit mechanism by which the Regulation makes the **entire staged-manufacturing simulation chain auditable** — i.e., this Annex is the technical backbone of the "trustworthy and auditable" requirement central to this Project's own goals: any completed heavy bus's final CO2/fuel-consumption figures can, in principle, be traced hash-by-hash back through every manufacturing stage to the primary vehicle's original simulation run.

This Annex does not itself restate the "method as described in point 2 of Annex I" for staged manufacturing — Part III explicitly references it rather than reproducing it. **Annex I point 2 is therefore the necessary companion reference** for understanding exactly how/when each stage's VIF is generated and consumed; it was out of scope for this assigned line range and has not been transcribed here.

---

## 5. Figures/diagrams

No figures, diagrams, charts or illustrations are referenced anywhere in the assigned line range (4316–4912). The entire range consists of defined-term text and enumerated field lists. No "[Figure referenced in source but not visually extracted…]" flag is needed for this range.

---

## 6. Summary of flagged ambiguities (for user attention)

- The "Amendment" column throughout is an **interpretive reconstruction** from unclosed `▼Mx` opening markers in the OCR text (see methodological note at top) — treat it as indicative, not a certified legal boundary.
- **1.1.9 and 1.1.18** (MRF) / **1.1.9 and 1.1.18** (CIF): shown in the source as `▼M4 __________` — items deleted by Regulation (EU) 2025/258, numbering gap preserved.
- **CIF §2.4**: numbering jumps from **2.4.3 straight to 2.4.5** with no 2.4.4 in the source text — transcribed faithfully; possible drafting/consolidation artifact in the Official Journal text itself, not an extraction error on this end (worth checking against the PDF directly if exact field count matters).
- **CIF §2.6.10** "Hydrogen range (km)" is tagged ▼M3 by the tracked marker state, which is suspect given hydrogen range is otherwise consistently a ►M4-era concept (Annex IV point 2(4); CIF §2.5.4) — flagged as an uncertain attribution.
- **1.9.x tyre "hash" sub-items**: axles 1–3 use lettered sub-items (1.9.3a/1.9.7a/1.9.11a) for the "hash of tyre input data" field, but axle 4's equivalent is plain-numbered 1.9.16 — an inconsistency in the source, transcribed as-is.
- **CIF 1.1.22** "Vehicle type approval number" appears to already be present under the M3 restructuring, while the equivalent MRF field (1.1.31) is only added under M4 — a discrepancy in field parity between the two files as drafted, not reconciled here.
- "ADC" (used in MRF §1.13.11–1.13.15) is not spelled out in this Annex's text; interpreted by context as an additional/auxiliary drive component, consistent with other VECTO driveline terminology, but this specific Annex does not define the acronym — flagged, not asserted as fact.
