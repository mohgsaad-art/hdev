# Annex IX — Verifying Lorry and Bus Auxiliary Data

**Source document:** Commission Regulation (EU) 2017/2400 of 12 December 2017 implementing Regulation (EC) No 595/2009 of the European Parliament and of the Council as regards the determination of the CO2 emissions and fuel consumption of heavy duty vehicles and amending Directive 2007/46/EC of the European Parliament and of the Council and Commission Regulation (EU) No 582/2011
**CELEX number:** 02017R2400 (consolidated text)
**Consolidation date:** 01.01.2026 — 007.001
**Range covered in this note:** lines 15980–16879 of the full consolidated-text OCR extraction (ANNEX IX in full)
**Amendment markers used in the source and reproduced below:** ►B = original 2017 baseline text; ►M1 = Reg. (EU) 2019/318; ►M2 = Reg. (EU) 2020/1181; ►M3 = Reg. (EU) 2022/1379; ►M4 = Reg. (EU) 2025/258. Where the source shows a page-footer stamp (e.g. "▼M3" followed by "02017R2400 — EN — 01.01.2026 — 007.001 — 388"), this marks the amendment version in force for the following block of text up to the next marker; these footer/page-break artifacts are omitted below except where needed to show where an amendment boundary falls, which is noted inline as "[amendment boundary: ▼M3]" etc.

---

## 1. Introduction

Annex IX describes the provisions regarding **declaration of technologies and other relevant input information on auxiliary systems** for heavy duty vehicles (HDVs), for the purpose of determining vehicle-specific CO2 emissions.

The power consumption of the following auxiliary types **shall be considered within the simulation tool (VECTO)** by using **technology-specific average generic models for power consumption**:

(a) Engine cooling fan
(b) Steering system
(c) Electric system
(d) Pneumatic system
(e) Heating, ventilation and air conditioning (HVAC) system
(f) Transmission Power Take-Off (PTO)

The generic values are **integrated in the simulation tool** and automatically used based on the relevant input information declared in accordance with this Annex. The related input data formats for the simulation tool are described in **Annex III**. For clear cross-reference, the three-digit parameter IDs used in Annex III are also listed throughout this Annex (e.g. "P181", "P294").

> **Modelling implication for this project:** VECTO does *not* simulate auxiliary power draw from first-principles component models (e.g. a detailed hydraulic-pump efficiency map); it uses a **declared-technology → generic average power-consumption lookup** approach. The manufacturer declares *which* technology variant is fitted (from a fixed enumerated list per auxiliary type), and the simulation tool applies a corresponding pre-calibrated generic power value/model. This is an important simplification to flag explicitly if replicating VECTO's auxiliary-power logic: the generic values themselves are **not disclosed in this Annex** — they are "integrated in the simulation tool" (i.e., embedded in VECTO's internal lookup tables/source code, not published as regulatory text here). Any "generic value" used in a sizing tool for these auxiliaries must therefore come from the actual VECTO source/config files, not be invented.

---

## 2. Definitions

For the purposes of this Annex, the following definitions apply. The related auxiliary type is stated in brackets after each definition. Numbering follows the source exactly, including gaps where a definition was deleted by a later amendment (shown as "–" in the source) and inserted sub-numbers (e.g. "14a", "26a").

### Engine cooling fan definitions

1. **"crankshaft mounted" fan** — a fan installation where the fan is driven in the prolongation of the crankshaft, often by a flange *(engine cooling fan)*.
2. **"belt or transmission driven" fan** — a fan that is installed in a position where an additional belt, tension system or transmission is needed *(engine cooling fan)*.
3. **"hydraulic driven" fan** — a fan propelled by hydraulic oil, often installed away from the engine. A hydraulic system with oil system, pump and valves influences losses and efficiencies in the system *(engine cooling fan)*.
4. **"electrically driven" fan** — a fan propelled by an electric motor. The efficiency for complete energy conversion, included in/out from battery, is considered *(engine cooling fan)*.
5. **"electronically controlled visco clutch"** — a clutch in which a number of sensor inputs together with SW logic are used to electronically actuate the fluid flow in the visco clutch *(engine cooling fan)*.

*[amendment boundary: ▼M3]*

6. **"bimetallic controlled visco clutch"** — a clutch in which a bimetallic connection is used to convert a temperature change into mechanical displacement. The mechanical displacement then works as an actuator for the visco clutch *(engine cooling fan)*.
7. **"discrete step clutch"** — a mechanical device where the grade of actuation can be made in distinct steps only (not continuously variable) *(engine cooling fan)*.
8. **"on/off clutch"** — a mechanical clutch which is either fully engaged or fully disengaged *(engine cooling fan)*.
9. **"variable displacement pump"** — a device that converts mechanical energy to hydraulic fluid energy. The amount of fluid pumped per revolution of the pump can be varied while the pump is running *(engine cooling fan)*.
10. **"constant displacement pump"** — a device that converts mechanical energy to hydraulic fluid energy. The amount of fluid pumped per revolution of the pump cannot be varied while the pump is running *(engine cooling fan)*.
11. **"electric motor control"** — the use of an electric motor to propel the fan. The electrical machine converts electrical energy into mechanical energy. Power and speed are controlled by conventional technology for electric motors *(engine cooling fan)*.

### Steering system definitions

12. **"fixed displacement pump (default technology)"** — a pump having an internal limitation of the flow rate *(steering system)*.
13. **"fixed displacement pump with electronic control"** — a pump using an electronic control of the flow rate *(steering system)*.
14. **"dual displacement pump"** — a pump with two chambers (with the same or different displacement), mechanical internal limitation of flow rate *(steering system)*.
14a. **"dual displacement pump with electronic control"** — a pump with two chambers (with the same or different displacement) which can be combined, or where under specific conditions only one of these is used. The flow rate is electronically controlled by a valve *(steering system)*.
15. **"variable displacement pump mech. controlled"** — a pump where the displacement is mechanically controlled internally (internal pressure scales) *(steering system)*.
16. **"variable displacement pump elec. controlled"** — a pump where the displacement is electronically controlled *(steering system)*.
17. **"electric driven pump"** — a steering system driven by an electric motor with continuously recirculating hydraulic fluid *(steering system)*.
17a. **"full electric steering gear"** — a steering system driven by an electric motor without continuously recirculating hydraulic fluid *(steering system)*.

### Pneumatic system definitions

18. *— [deleted; no text in consolidated version]*
19. **"air compressor with energy saving system" or "ESS"** — a compressor reducing the power consumption during blow-off, e.g. by closing the intake side; ESS is controlled by system air pressure *(pneumatic system)*.

*[amendment boundary: ▼M3]*

20. **"compressor clutch (visco)"** — a disengageable compressor where the clutch is controlled by the system air pressure (no smart strategy); minor losses during disengaged state caused by visco clutch *(pneumatic system)*.
21. **"compressor clutch (mechanically)"** — a disengageable compressor where the clutch is controlled by the system air pressure (no smart strategy) *(pneumatic system)*.
22. **"air management system with optimal regeneration" or "AMS"** — an electronic air processing unit that combines an electronically controlled air dryer for optimised air regeneration and an air delivery preferred during overrun conditions (requires a clutch or ESS) *(pneumatic system)*.

### Electric system definitions

23. **"light emitting diode" or "LED"** — semiconductor devices that emit visible light when an electrical current passes through them *(electric system)*.
24. *— [deleted; no text in consolidated version]*

### PTO definitions

25. **"power take-off" or "PTO"** — a device on a transmission or an engine to which an optional power-consuming device ("consumer"), e.g. a hydraulic pump, can be connected; a power take-off is usually optional *(PTO)*.
26. **"power take-off drive mechanism"** — a device in a transmission that allows the installation of a power take-off *(PTO)*.
26a. **"engaged gearwheel"** — a gearwheel which is engaged with running shafts of either the engine or transmission while the PTO clutch (if applicable) is open *(PTO)*.
27. **"tooth clutch"** — a (manoeuvrable) clutch where torque is transferred mainly by normal forces between mating teeth. A tooth clutch can either be engaged or disengaged. It is operated in load-free conditions only (e.g. at gear shifts in a manual transmission) *(PTO)*.
28. **"synchroniser"** — a type of tooth clutch where a friction device is used to equalise the speeds of the rotating parts to be engaged *(PTO)*.
29. **"multi-disc clutch"** — a clutch where several friction linings are arranged in parallel whereby all friction pairs get the same pressing force. Multi-disc clutches are compact and can be engaged and disengaged under load. They may be designed as dry or wet clutches *(PTO)*.
30. **"sliding wheel"** — a gearwheel used as a shift element where the shifting is realised by moving the gearwheel on its shaft into or out of the gear mesh of the mating gear *(PTO)*.

### Additional engine cooling fan definitions

31. **"discrete step clutch (off + 2 stages)"** — a mechanical device where the grade of actuation can be made in two distinct steps plus off only (not continuously variable) *(engine cooling fan)*.
32. **"discrete step clutch (off + 3 stages)"** — a mechanical device where the grade of actuation can be made in three distinct steps plus off only (not continuously variable) *(engine cooling fan)*.

*[amendment boundary: ▼M3]*

### Additional pneumatic system definitions

33. **"ratio compressor to engine"** — the forward gear ratio of the air compressor to the speed of the engine without slip *(pneumatic system)*.

*[amendment boundary: ▼M3]*

34. **"air suspension control mechanically"** — an air suspension system in which the air suspension control valves are operated mechanically without electronics and software *(pneumatic system)*.
35. **"air suspension control electronically"** — an air suspension system in which a number of sensor inputs together with software logic are used to electronically actuate the air suspension control valves *(pneumatic system)*.
36. **"pneumatic SCR reagent dosing"** — compressed air is used for dosing reagent into the exhaust system *(pneumatic system)*.
37. **"door drive technology pneumatic"** — the passenger doors of the vehicle are operated with compressed air *(pneumatic system)*.
38. **"door drive technology electric"** — the passenger doors of the vehicle are operated with an electric motor or with an electro-hydraulic system *(pneumatic system)*.
39. **"door drive technology mixed"** — both "door drive technology pneumatic" and "door drive technology electric" are installed in the vehicle *(pneumatic system)*.
40. **"smart regeneration system"** — a pneumatic system in which the regeneration air demand is optimised with respect to the quantity of dried air that is produced *(pneumatic system)*.
41. **"smart compression system"** — a pneumatic system in which the air delivery is electronically controlled with preferred air delivery during overrun conditions *(pneumatic system)*.

### Additional electric system definitions — lighting

42. **"interior lights"** — the lights within the passenger compartment installed to fulfil the requirements of paragraph 7.8 (artificial interior lighting) in Annex 3 to UN Regulation No. 107 *(electric system)*.
43. **"day running lights"** — the "daytime running lamp" in accordance with paragraph 2.7.25 of UN Regulation No. 48 *(electric system)*.
44. **"position lights"** — the "side marker lamp" in accordance with paragraph 2.7.24 of UN Regulation No. 48 *(electric system)*.
45. **"brake lights"** — the "stop lamp" in accordance with paragraph 2.7.12 of UN Regulation No. 48 *(electric system)*.
46. **"headlights"** — the "passing-beam (dipped-beam) headlamp" in accordance with paragraph 2.7.10 of UN Regulation No. 48, and the "driving-beam (main-beam) headlamp" in accordance with paragraph 2.7.9 of UN Regulation No. 48 *(electric system)*.

Footnote references for (42)–(46):
- UN Regulation No. 107 — Uniform provisions concerning the approval of category M2 or M3 vehicles with regard to their general construction (OJ L 52, 23.2.2018, p. 1).
- UN Regulation No. 48 — Uniform provisions concerning the approval of vehicles with regard to the installation of lighting and light-signalling devices (OJ L 14, 16.1.2019, p. 42).

*[amendment boundary: ▼M4]* (these two footnotes were updated in M4)

### Additional electric system definitions — alternator/battery

47. **"alternator"** — an electric machine to charge the battery and to supply electric power to the electrical auxiliary system when the vehicle's internal combustion engine is running. An alternator cannot contribute to propulsion of the vehicle *(electric system)*.
48. **"smart alternator system"** — a system of one or more alternators in combination with one or more dedicated REESS (Rechargeable Energy Storage System) which is electronically controlled with preferred generation of electric energy during overrun conditions *(electric system)*.

### HVAC system definitions

49. **"heating, ventilation and air conditioning system" or HVAC system** — a system that can actively heat and/or actively cool down and exchange or replace air to provide improved air quality for the passenger and/or the driver compartment *(HVAC system)*.
50. **"HVAC system configuration"** — a combination of HVAC system components in accordance with **Table 13** of this Annex *(HVAC system)*.
51. **"thermal comfort system for passenger compartment"** — a system that uses fans to circulate air within the vehicle or blows fresh air into the vehicle, where the air volume flow can at least be actively cooled or heated. The air is distributed from the roof of the vehicle and, in the case of double deckers, in both floors. In the case of open-top double deckers, in the lower deck *(HVAC system)*.
52. **"number of heat pumps for passenger compartment"** — the number of heat pumps installed in the vehicle to heat up and/or cool down cabin air or fresh air supplied to the passenger compartment. If a heat pump is used for both the passenger and the driver compartment, it is counted for the passenger compartment only. **If different heat pumps for heating and cooling are installed, the number of heat pumps shall be defined by the lower number of both separate cases** — i.e. the number of heat pumps for cooling and the number of heat pumps for heating shall be considered separately (e.g. in the case of 2 heat pumps for cooling and 1 heat pump for heating: only 1 heat pump shall be considered) *(HVAC system)*.
53. **"air conditioning system for driver compartment"** — a system is installed in the vehicle that can cool down the cabin air or fresh air supplied to the driver or driver compartment *(HVAC system)*.
54. **"air conditioning system for passenger compartment"** — a system is installed in the vehicle that can cool down the cabin air or fresh air supplied to the passenger compartment *(HVAC system)*.
55. **"independent heat pump for driver compartment"** — a heat pump is installed in the vehicle that is only used for the driver compartment *(HVAC system)*.
56. **"heat pump 2-stage"** — a heat pump where the grade of actuation can be made in two steps only but not continuously variable *(HVAC system)*.
57. **"heat pump 3-stage"** — a heat pump where the grade of actuation can be made in three steps only but not continuously variable *(HVAC system)*.
58. **"heat pump 4-stage"** — a heat pump where the grade of actuation can be made in four steps only but not continuously variable *(HVAC system)*.

*[amendment boundary: ▼M3]*

59. **"heat pump continuous"** — a heat pump where the grade of actuation is continuously variable, or where the air-conditioning compressor is driven by an electric motor with continuously variable speed *(HVAC system)*.
60. **"auxiliary heater power"** — as stated on the label defined in paragraph 4 of Annex 7 to UN Regulation No. 122 *(HVAC system)*.
61. **"double glazing"** — windows of the passenger compartment consisting of two glass window panes separated by a gas-filled space or by vacuum. In the case of several types of windows within the passenger compartment, the predominant window type by surface area shall be selected. For the assessment of the predominant window type, the windscreen, the rear window, the driver side-window(s), windows within doors, windows above and in front of the front axle (see Figure 1 for examples), as well as tiltable windows, **shall not be considered** *(HVAC system)*.

> **Figure 1 — "Windows not to be considered for predominant window type"**: [Figure referenced in source but not visually extracted from this text-only OCR.]

62. **"heat pump"** — a system that uses a refrigerant in a circular process to transfer thermal energy from the environment to the passenger compartment and/or the driver compartment and/or transfers thermal energy in the opposite direction (cooling and/or heating functionality) with a **coefficient of performance (COP) larger than 1** *(HVAC system)*.

*[amendment boundary: ▼M4]*

63. **"R-744 heat pump"** — a continuous (i.e. electrically driven) heat pump which uses R-744 refrigerant (CO2) as working medium *(HVAC system)*.

*[amendment boundary: ▼M3]*

64. **"non R-744 heat pump"** — a heat pump which uses a working medium other than R-744 refrigerant. For the possible grade of actuation (2-stage, 3-stage, 4-stage, continuous), definitions (56) to (59) apply *(HVAC system)*.

Footnote: UN Regulation No. 122 — Uniform technical prescriptions concerning the approval of vehicles of categories M, N and O with regard to their heating systems (OJ L 19, 24.1.2020, p. 42).

*[amendment boundary: ▼M3]*

65. **"adjustable coolant thermostat"** — a coolant thermostat whose characteristics are influenced by at least one additional input besides the coolant temperature, e.g. active electric heating of the thermostat *(HVAC system)*.
66. **"adjustable auxiliary heater"** — a fuel-operated heater with at least 2 levels of heating capacity besides "off" that can be controlled depending on the required heating system capacity in the bus *(HVAC system)*.
67. **"engine waste gas heat exchanger"** — a heat exchanger that uses the thermal energy of engine waste gas to heat the cooling circuit *(HVAC system)*.
68. **"separate air distribution ducts"** — one or multiple air channels connected to a thermal comfort system to distribute conditioned air evenly to the passenger compartment. Air channels may include loud speakers or HVAC water supply and electric harness. Reservoirs for compressed air shall not be installed within this/these channel(s). By this model parameter, the simulation tool considers reduced heat transfer losses to the ambient or components within the channel.
    - For **HVAC configurations 8, 9 and 10** in vehicle groups **31, 33, 35, 37 and 39**, this input **shall be set to "true"** — those configurations benefit from reduced losses as cooled air is directly blown into the vehicle interior even without any air channel.
    - For **all HVAC configurations** in vehicle groups **32, 34, 36, 38 and 40**, this parameter **shall be set to "true"** as this is state-of-the-art.
    *(HVAC system)*
69. **"electrically driven compressor"** — a compressor driven by an electric motor *(pneumatic system)*.
70. **"water electric heater"** — a device using electric energy to heat up the coolant of the vehicle with a **coefficient of performance lower than 1** and that is actively used for the heating functionality during vehicle operation on road *(HVAC system)*.
71. **"air electric heater"** — a device using electric energy to heat up the air of the passenger and/or driver compartment with a **coefficient of performance lower than 1** *(HVAC system)*.
72. **"other heating technology"** — any fully electric technology used for heating up the passenger and/or driver compartment not covered by the technologies in definitions (62), (70) or (71) *(HVAC system)*.

### Additional electric system definitions — battery/capacitor (relevant to 12V/24V/48V electrical loads)

73. **"lead-acid battery – conventional"** — a lead-acid battery where none of definitions (74) or (75) applies *(electric system)*.
74. **"lead-acid battery – AGM"** (Absorbed Glass Mat) — lead-acid batteries where glass fibre mats soaked in electrolyte are used as separators between the negative and positive plates *(electric system)*.
75. **"lead-acid battery – gel"** — lead-acid batteries where a silica gelling agent is mixed into the electrolyte *(electric system)*.
76. **"Li-ion battery - high power"** — a Li-ion battery where the numerical ratio between rated maximum current in [A] and the rated capacity in [Ah] is **equal to or larger than 10** *(electric system)*.

*[amendment boundary: ▼M3]*

77. **"Li-ion battery - high energy"** — a Li-ion battery where the numerical ratio between rated maximum current in [A] and the rated capacity in [Ah] is **less than 10** *(electric system)*.
78. **"capacitor with DC/DC converter"** — an (ultra) capacitor electrical energy storage unit combined with a DC/DC unit that adapts the voltage level and controls the current to and from the electric consumer board net *(electric system)*.
79. **"articulated bus"** — a heavy bus that is an incomplete vehicle, complete vehicle or completed vehicle consisting of at least two rigid sections connected to each other by an articulated section. Connection and disconnection of the sections are to be possible only in a workshop. For complete or completed heavy buses of this type, the articulated section shall permit the free movement of travellers between the rigid sections.

---

## 3. Description of auxiliary-relevant input information into the simulation tool

### 3.1. Engine cooling fan

The information on engine cooling fan technology shall be provided based on the applicable combinations of **fan drive** and **fan control** technology as described in Table 4.

- If a new technology within a fan drive cluster (e.g. crankshaft mounted) cannot be found in the list, the technology allocated to **"default for fan drive cluster" (DC)** shall be provided.
- If a new technology cannot be found in any fan drive cluster, the technology allocated to **"default overall" (DO)** shall be provided.

**Table 4 — Engine cooling fan technologies (Parameter ID P181)**

| Fan drive cluster | Fan control | Medium and heavy lorries | Heavy buses |
|---|---|---|---|
| Crankshaft mounted | Electronically controlled visco clutch | X | X |
| Crankshaft mounted | Bimetallic controlled visco clutch | X (DC) | X |
| Crankshaft mounted | Discrete step clutch | X | |
| Crankshaft mounted | Discrete step clutch (off + 2 stages) | X | |
| Crankshaft mounted | Discrete step clutch (off + 3 stages) | X | |
| Crankshaft mounted | On/off clutch | X | X (DC, DO) |
| Belt driven or driven via transmission | Electronic controlled visco clutch | X | X |
| Belt driven or driven via transmission | Bimetallic controlled visco clutch | X (DC) | X |
| Belt driven or driven via transmission | Discrete step clutch | X | |
| Belt driven or driven via transmission | Discrete step clutch (off + 2 stages) | X | |
| Belt driven or driven via transmission | Discrete step clutch (off + 3 stages) | X | |
| Belt driven or driven via transmission | On/off clutch | X | X (DC) |
| Hydraulically driven | Variable displacement pump | X | X |
| Hydraulically driven | Constant displacement pump | X (DC, DO) | X (DC) |
| Electrically driven | Electric motor control | X (DC) | X (DC) |

Legend: **X** = applicable; **DC** = default for fan drive cluster; **DO** = default overall.

> Note: for medium and heavy lorries, the overall default (DO) is "Hydraulically driven / Constant displacement pump". For heavy buses, the overall default (DO) is "Crankshaft mounted / On/off clutch".

### 3.2. Steering system

The technology of the steering system shall be provided in accordance with Table 5, **per each active steered axle on the vehicle**.

- If a new technology within a steering technology cluster (e.g. mechanically driven) cannot be found in the list, the technology allocated to **"default for steering technology cluster"** shall be provided.
- If a new technology cannot be found in any steering technology cluster, the technology allocated to **"default overall"** shall be provided.

**Table 5 — Steering system technologies (Parameter ID P182)**

| Steering technology cluster | Technology | Medium and heavy lorries | Heavy buses |
|---|---|---|---|
| Mechanically driven | Fixed displacement | X (DC, DO) | X (DC, DO) |
| Mechanically driven | Fixed displacement, electronical control | X | X |
| Mechanically driven | Dual displacement pump | X | X |
| Mechanically driven | Dual displacement pump with electronic control | X | X |
| Mechanically driven | Variable displacement, mechanical control | X | X |
| Mechanically driven | Variable displacement, electronical control | X | X |
| Electric | Electric driven pump | X (DC) | X (DC) |
| Electric | Full electric steering gear | X | X |

Legend: **X** = applicable; **DC** = default for steering technology cluster; **DO** = default overall.

> Both lorries and buses share the same overall default: "Mechanically driven / Fixed displacement".

### 3.3. Electric System

#### 3.3.1. Medium lorries and heavy lorries

The technology of the electric system shall be provided in accordance with Table 6. **If the technology used in the vehicle is not listed, "standard technology" shall be provided to the simulation tool.**

**Table 6 — Electric system technologies for medium lorries and heavy lorries (Parameter ID P183)**

| Technology |
|---|
| Standard technology |
| Standard technology - LED headlights |

#### 3.3.2. Heavy buses

The technology of the electric system shall be provided in accordance with Table 7 — a much more granular, multi-parameter declaration than for lorries.

**Table 7 — Electric system technologies for heavy buses**

| Electric system cluster | Parameter | Parameter ID | Input to the simulation tool | Explanations |
|---|---|---|---|---|
| Alternator | Alternator technology | **P294** | conventional / smart / no alternator | "smart" shall be declared for systems fulfilling definition (48). "no alternator" is applicable for HEVs which do not have an alternator in the electric auxiliary system. ►M4: For PEV or FCHV no input is required. ◄ |
| Alternator | Smart alternator – maximum rated current | **P295** | value in [A] | Maximum rated current at nominal speed in accordance with manufacturer's labelling or data sheet, or measured in accordance with standard **ISO 8854:2012**. Input per smart alternator. |
| Alternator | Smart alternator – rated voltage | **P296** | value in [V] | Allowed values: '12', '24', '48'. Input per smart alternator. |
| Batteries for smart alternator systems | Technology | **P297** | lead-acid battery – conventional / lead-acid battery – AGM / lead-acid battery – gel / li-ion battery - high power / li-ion battery - high energy | Input per battery charged by smart alternator system. If a battery technology cannot be found in the list, "Lead-acid battery – Conventional" shall be provided as input. |
| Batteries for smart alternator systems | Nominal voltage | **P298** | value in [V] | Allowed values: '12', '24', '48'. Input per battery charged by smart alternator system. **Where batteries are configured in series (e.g. two 12V units for a 24V system), the actual nominal voltage of the single battery units (12V in this example) shall be provided.** |
| Batteries for smart alternator systems | Rated capacity | **P299** | value in [Ah] | Capacity in Ah in accordance with manufacturer's labelling or data sheet. Input per battery charged by smart alternator system. |
| Capacitors for smart alternator systems | Technology | **P300** | with DC/DC converter | Input per battery charged by smart alternator system. |
| Capacitors for smart alternator systems | Rated capacitance | **P301** | value in [F] | Capacitance in Farad (F) in accordance with manufacturer's labelling or data sheet. Input per capacitor charged by smart alternator system. |
| Capacitors for smart alternator systems | Rated voltage | **P302** | value in [V] | Rated operating voltage in accordance with manufacturer's labelling or data sheet. Input per capacitor charged by smart alternator system. |
| Auxiliary electric energy supply | Supply of electric auxiliaries from HEV REESS possible | **P303** | true / false | To be set to 'true' if the vehicle is equipped with a controlled power link that enables transfer of electric energy from a HEV propulsion energy storage system to the electric consumer board net. **Input only required for HEV.** |
| Interior lights | Interior lights LED | **P304** | true / false | Parameters shall only be set to true if all lights of the category are in line with the definitions in points 2(42) to 2(46). |
| Exterior lights | Day running lights LED | **P305** | true / false | (see above note on definitions) |
| Exterior lights | Position lights LED | **P306** | true / false | |
| Exterior lights | Brake lights LED | **P307** | true / false | |
| Exterior lights | Headlights LED | **P308** | true / false | |

> **Flag — relevance to electrified HDVs (12V/24V/48V auxiliary loads):** This is the single most directly relevant block in Annex IX to understanding how VECTO treats low-voltage electrical loads on electrified heavy-duty vehicles.
> - P303 ("Supply of electric auxiliaries from HEV REESS possible") is explicitly a **HEV-only** input per the text, and ►M4 explicitly states that for Alternator technology (P294), **"For PEV or FCHV no input is required."** This implies that for **pure battery-electric (PEV/BEV) and fuel-cell (FCHV) heavy vehicles, the entire "Alternator" cluster of Table 7 (P294–P296) is not applicable/not required** — consistent with such vehicles having no belt/engine-driven alternator at all; their 12V/24V/48V board net is instead supplied via a DC/DC converter from the main traction battery (this DC/DC-converter supply path is not itself parametrised as a discrete "technology" in this Annex's Table 7 — it is implicit in the absence of an alternator input, and VECTO's generic treatment of this consumption path is not disclosed in the regulatory text).
> - The **"batteries for smart alternator systems"** and **"capacitors for smart alternator systems"** clusters (P297–P302) are tied specifically to the alternator cluster and therefore read as **conventional/ICE/HEV-architecture-specific** declarations (describing the low-voltage buffer battery/capacitor charged by a smart alternator), not a generic battery model applicable to all propulsion types.
> - The **lighting technology flags (P304–P308, LED true/false)** and the **LED declarations in Table 6 (P183, lorries)** appear to be **propulsion-architecture-agnostic** — i.e., still relevant and declarable regardless of whether the vehicle is diesel, HEV, PEV or FCHV, since lighting loads exist on any vehicle type.
> - **This means VECTO's Annex IX framework does not appear to give a detailed, technology-differentiated generic auxiliary power model for the 12V/24V/48V board-net load path on PEVs/FCHVs** (beyond lighting LED flags) — the Alternator/Battery/Capacitor clusters that would otherwise capture this are explicitly skipped for these propulsion types. If your tool needs a defensible number for "low-voltage auxiliary power draw on a BEV," this Annex does not supply one directly; it would need to come from elsewhere in the Regulation (e.g. Annex III's general auxiliary input definitions, or the VECTO Engineering/calculation tool's internal generic auxiliary power tables, which are not part of this legal text) or from OEM-specific measured data. **This is a gap to flag explicitly, not to fill with an invented number.**

### 3.4. Pneumatic system

#### 3.4.1. Pneumatic systems working with over pressure

##### 3.4.1.1. Size of air supply

For pneumatic systems working with over pressure, the size of air supply shall be provided in accordance with Table 8.

**Table 8 — Pneumatic systems with over pressure – size of air supply**

| Size of air supply | Medium and heavy lorries (part of P184) | Heavy buses (P309) |
|---|---|---|
| Small — displacement ≤ 250 cm³; 1 cylinder / 2 cylinder | X | X |
| Medium — 250 cm³ < displacement ≤ 500 cm³; 1 cylinder / 2 cylinder 1-stage | X | X |
| Medium — 250 cm³ < displacement ≤ 500 cm³; 1 cylinder / 2 cylinder 2-stage | X | X |
| Large — displacement > 500 cm³; 1 cylinder / 2 cylinder 1-stage / 2-stage | X, DO | |
| Large — displacement > 500 cm³; 1-stage | | X, DO |
| Large — displacement > 500 cm³; 2-stage | | X |

Legend: **X** = applicable; **DO** = default overall.

Additional rules:
- In the case of a two-stage compressor, **the displacement of the first stage** shall be used to describe the size of the air compressor system.
- In the case of non-piston compressors, the **"default overall" (DO)** technology shall be declared.
- In the case of heavy buses with electrically driven compressors, **"not applicable"** shall be provided as input for size of air supply, as this parameter is not considered by the simulation tool for that configuration.

##### 3.4.1.2. Fuel saving technologies

Fuel saving technologies shall be provided in accordance with the combinations listed in **Table 9** for medium and heavy lorries, and **Table 10** for heavy buses.

**Table 9 — Pneumatic systems with over pressure – fuel saving technologies for heavy lorries, medium lorries (part of Parameter P184)**

| Combination No. | Compressor drive | Compressor clutch | Air compressor with Energy Saving System (ESS) | Air Management System with optimal regeneration (AMS) |
|---|---|---|---|---|
| 1 | mechanically | no | no | no |
| 2 | mechanically | no | yes | no |
| 3 | mechanically | visco | no | no |
| 4 | mechanically | mechanically | no | no |
| 5 | mechanically | no | yes | yes |
| 6 | mechanically | visco | no | yes |
| 7 | mechanically | mechanically | no | yes |
| 8 | electrically | no | no | no |
| 9 | electrically | no | no | yes |

**Table 10 — Pneumatic systems with over pressure – fuel saving technologies for heavy buses**

| Combination No. | Compressor drive (P310) | Compressor clutch (P311) | Smart regeneration system (P312) | Smart compression system (P313) |
|---|---|---|---|---|
| 1 | mechanically | ►M4 none ◄ | no | no |
| 2 | mechanically | ►M4 none ◄ | yes | no |
| 3 | mechanically | ►M4 none ◄ | no | yes |
| 4 | mechanically | ►M4 none ◄ | yes | yes |
| 5 | mechanically | ►M4 visco ◄ | no | no |
| 6 | mechanically | ►M4 visco ◄ | yes | no |
| 7 | mechanically | ►M4 visco ◄ | no | yes |
| 8 | mechanically | ►M4 visco ◄ | yes | yes |
| 9 | mechanically | ►M4 mechanically ◄ | no | no |
| 10 | mechanically | ►M4 mechanically ◄ | yes | no |
| 11 | mechanically | ►M4 mechanically ◄ | no | yes |
| 12 | mechanically | ►M4 mechanically ◄ | yes | yes |
| 13 | electrically | ►M4 None ◄ | no | no |
| 14 | electrically | ►M4 none ◄ | yes | no |

> Note: Table 10 in the source text is truncated at combination 14 within the extracted line range (the table may continue beyond the OCR block boundary at the page break to "02017R2400 — EN — 01.01.2026 — 007.001 — 400"; combinations 15/16, if they exist for the electrically-driven branch with smart compression system = yes, are **not visible in this extraction** and should be verified against the source PDF directly if a complete enumeration is required). The ►M4 brackets around "none"/"visico"/"mechanically" in the Compressor clutch column indicate this column's values were amended by Regulation (EU) 2025/258.

##### 3.4.1.3. Further characteristics of the pneumatic system for heavy buses

For heavy buses, further characteristics of the pneumatic system shall be declared per **Table 11**.

**Table 11 — Further characteristics of the pneumatic system for heavy buses**

| Parameter | Parameter ID | Input to the simulation tool | Explanations |
|---|---|---|---|
| Ratio compressor to engine | **P314** | value in [-] | Ratio = compressor speed / engine speed. Only applicable in the case of mechanically driven compressor. |
| Entrance height in non-kneeled position | **P290** | value in [mm] | In accordance with the definitions set out in point 2(10) of Annex III. Documentation of this value shall be given by vehicle setup drawings used during parametrisation of the air suspension control of the vehicle. Value shall represent the state as delivered to the customer as normal ride height. This parameter is only relevant for heavy buses. |
| Air suspension control | **P315** | mechanically / electronically | |
| Pneumatic SCR reagent dosing | **P316** | true / false | See point 2(36). |
| Door drive technology | **P291** | pneumatic / mixed / electric | |

#### 3.4.2. Pneumatic systems working with vacuum

For vehicles with pneumatic systems working with **vacuum (relative negative pressure)**, either **"Vacuum pump"** or **"Vacuum pump + elec. driven"** shall be provided as input to the simulation tool (**Parameter P184**). **This technology is not applicable for heavy buses.**

### 3.5. HVAC system

#### 3.5.1. HVAC system for medium lorries and heavy lorries

The technology of the HVAC system shall be provided in accordance with Table 12.

**Table 12 — HVAC system technologies for medium lorries and heavy lorries (Parameter ID P185)**

| Technology |
|---|
| None (no air conditioning system for driver compartment) |
| Default |

#### 3.5.2. HVAC system for heavy buses

The HVAC system configuration shall be provided in accordance with the definitions set out in **Table 13**. A graphical representation of the different configurations is given in **Figure 2**.

> **Figure 2 — "HVAC system configuration for heavy buses (Rigid and Articulated)"**: [Figure referenced in source but not visually extracted from this text-only OCR.]

**Table 13 — HVAC system configuration for heavy buses (Parameter ID P317)**

| HVAC system configuration | Thermal comfort system for passenger compartment | Number of heat pumps for passenger compartment (per def. (52)) — Rigid | Number of heat pumps for passenger compartment (per def. (52)) — Articulated | Driver compartment supplied by heat pump(s) for passenger compartment | Independent heat pump(s) for driver compartment |
|---|---|---|---|---|---|
| 1 | No | 0 | 0 | No | No |
| 2 | No | 0 | 0 | No | Yes |
| 3 | Yes | 0 | 0 | No | No |
| 4 | Yes | 0 | 0 | No | Yes |
| 5 | Yes | 1 | 1 or 2 | No | No |
| 6 | Yes | 1 | 1 or 2 | Yes | No |
| 7 | Yes | 1 | 1 or 2 | No | Yes |
| 8 | Yes | > 1 | > 2 | No | No |
| 9 | Yes | > 1 | > 2 | No | Yes |
| 10 | Yes | > 1 | > 2 | Yes | No |

> Cross-reference: Definition (68) ("separate air distribution ducts") specifically calls out **HVAC configurations 8, 9 and 10** in vehicle groups 31/33/35/37/39 as mandatorily "true" for that parameter, and **all configurations** in vehicle groups 32/34/36/38/40 as mandatorily "true" as well — tying this configuration table directly into the broader vehicle-group classification system used elsewhere in the Regulation (vehicle groups defined in Annex I).

The HVAC system parameters shall be declared in accordance with **Table 14**.

**Table 14 — HVAC system parameters (heavy buses)**

| Parameter | Parameter ID | Input to the simulation tool | Explanations |
|---|---|---|---|
| Heat pump type for cooling driver compartment | **P318** | none / not applicable / R-744 / non R-744 2-stage / non R-744 3-stage / non R-744 4-stage / non R-744 continuous | 'not applicable' shall be declared for HVAC system configurations 6 and 10 due to supply from passenger heat pump. ►M4: For PEV and FCHV only continuous (i.e. electrically driven) heat pump types are allowed inputs (i.e. 'R-744' or 'non R-744 continuous'). ◄ |
| Heat pump type for heating driver compartment | **P319** | none / not applicable / R-744 / non R-744 2-stage / non R-744 3-stage / non R-744 4-stage / non R-744 continuous | 'not applicable' shall be declared for HVAC system configurations 6 and 10 due to supply from passenger heat pump. ►M4: For PEV and FCHV only continuous (i.e. electrically driven) heat pump types are allowed inputs (i.e. 'R-744' or 'non R-744 continuous'). ◄ |
| Heat pump type for cooling passenger compartment | **P320** | none / R-744 / non R-744 2-stage / non R-744 3-stage / non R-744 4-stage / non R-744 continuous | In the case of multiple heat pumps with different technologies for cooling the passenger compartment, the dominant technology shall be declared (e.g. in accordance with available power or preferred usage in operation). ►M4: For PEV and FCHV only continuous (i.e. electrically driven) heat pump types are allowed inputs (i.e. 'R-744' or 'non R-744 continuous'). ◄ |
| Heat pump type for heating passenger compartment | **P321** | none / R-744 / non R-744 2-stage / non R-744 3-stage / non R-744 4-stage / non R-744 continuous | In the case of multiple heat pumps with different technologies for heating the passenger compartment, the dominant technology shall be declared (e.g. in accordance with available power or preferred usage in operation). ►M4: For PEV and FCHV only continuous (i.e. electrically driven) heat pump types are allowed inputs (i.e. 'R-744' or 'non R-744 continuous'). ◄ |
| Auxiliary heater power | **P322** | value in [W] | Rated output as specified for the device. Enter '0' if no auxiliary heater is installed. |
| Double glazing | **P323** | true / false | |
| Adjustable coolant thermostat | **P324** | true / false | |
| Adjustable auxiliary heater | **P325** | true / false | |
| Engine waste gas heat exchanger | **P326** | true / false | |
| Separate air distribution ducts | **P327** | true / false | |
| Water electric heater | **P328** | true / false | ►M4: Input to be provided only for HEV, FCHV and PEV. ◄ |
| Air electric heater | **P329** | true / false | ►M4: Input to be provided only for HEV, FCHV and PEV. ◄ |
| Other heating technology | **P330** | true / false | ►M4: Input to be provided only for HEV, FCHV and PEV. ◄ |

> **Flag — electrified-vehicle relevance:** Parameters P318–P321 (heat pump type for driver/passenger cooling and heating) are **restricted for PEV and FCHV** to only the continuous (electrically driven) heat pump types — "R-744" or "non R-744 continuous" — per ►M4. This is a direct, explicit regulatory constraint on HVAC architecture for battery-electric and fuel-cell buses (no 2/3/4-stage non-continuous heat pumps allowed as declared input for those propulsion types), reflecting that non-continuous (clutch/stage-based, typically engine-belt or compressor-driven) heat pump technologies are tied to having an ICE present. Similarly, P328 "Water electric heater", P329 "Air electric heater" and P330 "Other heating technology" are **only required as inputs for HEV, FCHV and PEV** — i.e., these are the electric supplemental-heating declarations relevant specifically to electrified architectures (since electrified vehicles typically lack waste engine heat for cabin heating and need electric resistive/other heating as backup/supplement to the heat pump). This is the clearest regulatory linkage in Annex IX between the HVAC input schema and propulsion electrification.

### 3.6. Transmission Power Take-Off (PTO)

For heavy lorries with a PTO and/or PTO drive mechanism installed on the transmission, the power consumption shall be considered by **determined generic values**. These represent power losses in usual drive mode **when the consumer connected to a PTO (e.g. a hydraulic pump) is switched off/disengaged**. Application-related power consumption when the consumer is engaged is added by the simulation tool separately and **is not described in this table**.

*[amendment boundary: ▼M4 for the table header / ▼M3 for table content]*

**Table 15 — Mechanical power demand of PTOs with switched-off consumers for heavy lorries**

| Design variant (power losses vs. a transmission without PTO / PTO drive mechanism) — Additional drag loss relevant parts: Shafts/gear wheels (Parameter P247) | Additional drag loss relevant parts: Other elements (Parameter P248) | Power loss [W] |
|---|---|---|
| only one engaged gearwheel positioned above the specified oil level (no additional gearmesh) | — | 0 |
| only the drive shaft of the PTO | tooth clutch (incl. synchroniser) or sliding gearwheel | 50 |
| only the drive shaft of the PTO | multi-disc clutch | 350 |
| only the drive shaft of the PTO | multi-disc clutch with dedicated pump for PTO clutch | 3 000 |
| drive shaft and/or up to 2 engaged gearwheels | tooth clutch (incl. synchroniser) or sliding gearwheel | 150 |
| drive shaft and/or up to 2 engaged gearwheels | multi-disc clutch | 400 |
| drive shaft and/or up to 2 engaged gearwheels | multi-disc clutch with dedicated pump for PTO clutch | 3 050 |
| drive shaft and/or more than 2 engaged gearwheels | tooth clutch (incl. synchroniser) or sliding gearwheel | 200 |
| drive shaft and/or more than 2 engaged gearwheels | multi-disc clutch | 450 |
| drive shaft and/or more than 2 engaged gearwheels | multi-disc clutch with dedicated pump for PTO clutch | 3 100 |
| PTO which includes 1 or more additional gearmesh(es), without disconnect clutch | — | 1 500 |

*[amendment boundary: ▼M4]*

In the case of **multiple PTOs mounted to the transmission**, only the component with the **highest losses** in accordance with Table 15, for its combination of criteria **"PTOShaftsGearWheels"** and **"PTOShaftsOtherElements"**, shall be declared.

**For medium lorries and heavy buses, no declaration of transmission PTOs is foreseen** (i.e., Annex IX's PTO provisions apply only to heavy lorries).

> **Modelling note:** these PTO power-loss values (0 W to 3,100 W) are **fixed, published numeric generic values** directly in the regulatory text — unlike the fan/steering/electric/HVAC auxiliaries, where the generic power-consumption values are not disclosed and are only referenced as "integrated in the simulation tool." These PTO figures ARE directly usable/citable (CELEX 02017R2400, Annex IX, Table 15) as authoritative drag-loss figures for a heavy lorry PTO declared off/disengaged.

---

## Summary of all Parameter IDs referenced in Annex IX

| Parameter ID | Description | Table/Section |
|---|---|---|
| P181 | Engine cooling fan technology | Table 4, §3.1 |
| P182 | Steering system technology (per active steered axle) | Table 5, §3.2 |
| P183 | Electric system technology (medium/heavy lorries) | Table 6, §3.3.1 |
| P184 | Pneumatic system — size of air supply (lorries, part) / fuel saving technology (lorries, part) / vacuum system technology | Tables 8, 9, §3.4.2 |
| P185 | HVAC system technology (medium/heavy lorries) | Table 12, §3.5.1 |
| P247 | PTO — additional drag loss relevant parts: shafts/gear wheels | Table 15, §3.6 |
| P248 | PTO — additional drag loss relevant parts: other elements | Table 15, §3.6 |
| P290 | Entrance height in non-kneeled position (heavy buses) | Table 11, §3.4.1.3 |
| P291 | Door drive technology (heavy buses) | Table 11, §3.4.1.3 |
| P294 | Alternator technology (heavy buses) | Table 7, §3.3.2 |
| P295 | Smart alternator – maximum rated current | Table 7, §3.3.2 |
| P296 | Smart alternator – rated voltage | Table 7, §3.3.2 |
| P297 | Batteries for smart alternator systems — technology | Table 7, §3.3.2 |
| P298 | Batteries for smart alternator systems — nominal voltage | Table 7, §3.3.2 |
| P299 | Batteries for smart alternator systems — rated capacity | Table 7, §3.3.2 |
| P300 | Capacitors for smart alternator systems — technology | Table 7, §3.3.2 |
| P301 | Capacitors for smart alternator systems — rated capacitance | Table 7, §3.3.2 |
| P302 | Capacitors for smart alternator systems — rated voltage | Table 7, §3.3.2 |
| P303 | Supply of electric auxiliaries from HEV REESS possible | Table 7, §3.3.2 |
| P304 | Interior lights LED | Table 7, §3.3.2 |
| P305 | Day running lights LED | Table 7, §3.3.2 |
| P306 | Position lights LED | Table 7, §3.3.2 |
| P307 | Brake lights LED | Table 7, §3.3.2 |
| P308 | Headlights LED | Table 7, §3.3.2 |
| P309 | Pneumatic system — size of air supply (heavy buses) | Table 8, §3.4.1.1 |
| P310 | Compressor drive (heavy buses) | Table 10, §3.4.1.2 |
| P311 | Compressor clutch (heavy buses) | Table 10, §3.4.1.2 |
| P312 | Smart regeneration system (heavy buses) | Table 10, §3.4.1.2 |
| P313 | Smart compression system (heavy buses) | Table 10, §3.4.1.2 |
| P314 | Ratio compressor to engine (heavy buses) | Table 11, §3.4.1.3 |
| P315 | Air suspension control (heavy buses) | Table 11, §3.4.1.3 |
| P316 | Pneumatic SCR reagent dosing (heavy buses) | Table 11, §3.4.1.3 |
| P317 | HVAC system configuration (heavy buses) | Table 13, §3.5.2 |
| P318 | Heat pump type for cooling driver compartment | Table 14, §3.5.2 |
| P319 | Heat pump type for heating driver compartment | Table 14, §3.5.2 |
| P320 | Heat pump type for cooling passenger compartment | Table 14, §3.5.2 |
| P321 | Heat pump type for heating passenger compartment | Table 14, §3.5.2 |
| P322 | Auxiliary heater power | Table 14, §3.5.2 |
| P323 | Double glazing | Table 14, §3.5.2 |
| P324 | Adjustable coolant thermostat | Table 14, §3.5.2 |
| P325 | Adjustable auxiliary heater | Table 14, §3.5.2 |
| P326 | Engine waste gas heat exchanger | Table 14, §3.5.2 |
| P327 | Separate air distribution ducts | Table 14, §3.5.2 |
| P328 | Water electric heater | Table 14, §3.5.2 |
| P329 | Air electric heater | Table 14, §3.5.2 |
| P330 | Other heating technology | Table 14, §3.5.2 |

---

## Open items / things not visible in this OCR extraction

1. **Figure 1** ("Windows not to be considered for predominant window type") and **Figure 2** ("HVAC system configuration for heavy buses (Rigid and Articulated)") are both referenced but not visually present in this text-only extraction.
2. **Table 10** (heavy bus pneumatic fuel-saving combinations) is only visible up to combination 14 (electrically driven, clutch "none", smart regeneration "yes", smart compression "no") within this line range; whether further rows exist should be verified directly against the source PDF if a full enumeration (e.g. combination with smart compression system = yes on the electric-drive branch) is needed.
3. The **actual numeric generic power-consumption values** used internally by VECTO for fan, steering, electric-system and HVAC auxiliary technologies are **not disclosed in this Annex** (only the PTO table, Table 15, gives explicit watt figures). Any such values needed for a sizing tool must be sourced from VECTO's own technical/engineering documentation or source code, not inferred or invented from this legal text.
