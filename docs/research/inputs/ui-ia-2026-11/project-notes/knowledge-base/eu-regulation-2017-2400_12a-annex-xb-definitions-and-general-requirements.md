
# Annex Xb — Certification of Electric Powertrain Components
## Part 1: Definitions, Abbreviations and General Requirements

**Source:** Commission Regulation (EU) 2017/2400 (consolidated text), CELEX **02017R2400**, consolidation date **01.01.2026** (version 007.001).
**Range covered:** Annex Xb, point 1 (Introduction) and point 2 (Definitions and abbreviations) and point 3 (General requirements) — source lines ≈18785–19233.
**Companion files:** 12b (electric machine/IEPC/IHPC test procedure), 12c (battery), 12d (capacitor), 12e (FCS), 12f (conformity of production + appendix guide), 12g (Annex XI).

---

## 0. WHY THIS ANNEX MATTERS FOR THIS PROJECT (flag for the user)

The project's existing VECTO source material (LOT3 2014, SR7/LOT4 2017) explicitly stated that **battery, e-motor and fuel-cell component methodology was out of scope / future work**. **Annex Xb closes that gap.** It is the first legally-binding, Commission-adopted test and certification methodology for electric powertrain components under the EU HDV CO2/VECTO regulatory framework.

**Amendment provenance (read directly off the markers in the source text):**
- The whole of Annex Xb (electric machine systems, IEPC, IHPC Type 1, battery systems, capacitor systems — i.e. everything in point 2 definitions (1)–(53), and points 3–6) carries the **►M3** marker, i.e. it was inserted by **Commission Regulation (EU) 2022/1379** (amending Reg. 2017/2400). This is therefore the moment (2022) at which the EU first adopted an official methodology for certifying electric machine, IEPC, IHPC, battery and capacitor components for VECTO.
- The **Fuel Cell System (FCS)** provisions — definitions (54)–(72), the FCS abbreviations, Table 8 (hydrogen fuel quality), the whole of point 7 (FCS testing), Appendix 7 (FCS information document), Appendix 11 (FCS standard values), the FCS rows of Appendix 12 (conformity of production point 5), and the FCS rows of Appendix 13 (family concept point 2) — carry the **►M4** marker, i.e. they were inserted later by **Commission Regulation (EU) 2025/258**. FCS/hydrogen fuel-cell certification is therefore newer (2025) than battery/capacitor/e-machine certification (2022).
- Many individual sentences inside the M3-era electric-machine/IEPC/battery text also carry inline **►M4 ... ◄** markers, meaning Reg. 2025/258 also made smaller amendments/corrections to the 2022 e-machine, IEPC and battery provisions (not just adding FCS). These are flagged inline in files 12b/12c/12f where they occur.
- No **►M1** (2019/318) or **►M2** (2020/1181) markers appear anywhere in the assigned range — those two earlier amendments did not touch electric-powertrain component certification; electrification entered the Regulation only with M3/M4.

**Practical implication for the sizing tool:** any HDEV OEM/component-manufacturer VECTO certificate issued **before 2022** cannot contain battery/e-motor/capacitor data generated under this Annex (the methodology did not exist yet); any certificate **before 2025** cannot contain FCS data under this specific methodology.

---

## 1. Introduction (point 1 of Annex Xb)

> "The component test procedures described in this Annex shall produce input data relating to electric machine systems, IEPC, IHPC Type 1, battery systems and capacitor systems for the simulation tool."

(The Introduction text itself does not mention FCS explicitly even post-M4 insertion of point 7 — FCS input-data generation is described within point 7 and Appendix 11/15 directly.)

---

## 2. Definitions and abbreviations (point 2 of Annex Xb)

All items below are numbered exactly as in the source. Unless noted, all are **►M3** (2022/1379); items (54)–(72) are **►M4** (2025/258).

### 2.1 Battery / REESS terminology

1. **'battery control unit' or 'BCU'**: an electronic device that controls, manages, detects or calculates electric and thermal functions of the battery system and that provides communication between the battery system or battery pack or part of a battery pack and other vehicle controllers.
2. **'battery pack'**: a REESS (rechargeable electric energy storage system) that includes secondary cells or secondary cell assemblies, which are normally connected with cell electronics, power supply circuits and overcurrent shut-off device, including electrical interconnections and interfaces for external systems (examples of external systems: thermal conditioning, high voltage and low voltage auxiliary, and communication).
3. **'battery system'**: a REESS that consists of secondary cell assemblies or battery pack(s) as well as electrical circuits, electronics, interfaces for external systems (e.g. thermal conditioning system), BCUs and contactors.
4. **'representative battery subsystem'**: a subsystem of a battery system that consists of either secondary cell assemblies or battery pack(s) in serial and/or parallel configuration with electrical circuits, thermal conditioning system interfaces, control units and cell electronics. *(Allows certifying a scaled-down representative slice of a battery instead of the complete vehicle pack — important for test-bench feasibility.)*
5. **'cell'**: a basic functional unit of a battery, consisting of an assembly of electrodes, electrolyte, container, terminals and usually separators, that is a source of electric energy obtained by direct conversion of chemical energy.
6. **'cell electronics'**: an electronic device that collects and possibly monitors thermal or electric data of cells or cell assemblies or capacitors or capacitor assemblies and contains electronics for balancing between cells or capacitors, if necessary.
7. **'secondary cell'**: a cell designed to be electrically recharged by way of a reversible chemical reaction.

### 2.2 Capacitor terminology

8. **'capacitor'**: a device for storage of electrical energy achieved by the effects of electrostatic double-layer capacitance and electrochemical pseudo capacitance in an electrochemical cell.
9. **'capacitor cell'**: a basic functional unit of a capacitor, consisting of an assembly of electrodes, electrolyte, container, terminals and usually separators.
10. **'capacitor control unit' or 'CCU'**: analogous to BCU, for the capacitor system.
11. **'capacitor pack'**: a REESS including capacitor cells/assemblies normally connected with capacitor cell electronics, power supply circuits and overcurrent shut-off device, including electrical interconnections, interfaces for external systems and CCU.
12. **'capacitor system'**: a REESS that includes capacitor cells or capacitor assemblies or capacitor pack(s) plus electrical circuits, electronics, interfaces for external systems (e.g. thermal conditioning), CCU and contactors.
13. **'representative capacitor subsystem'**: analogous to representative battery subsystem — series/parallel subset of capacitor packs with associated electronics.
14. **'nC'**: the current rate equal to n times the one-hour discharge capacity expressed in ampere (i.e. the current that takes 1/n hours to fully charge or discharge the tested device based on the rated capacity). *(So "1C" = the current that fully discharges the rated Ah capacity in 1 hour; "2C" discharges it in 30 minutes; "1/3C" discharges it in 3 hours.)*

### 2.3 Drivetrain / mechanical terminology

15. **'continuously variable transmission' or 'CVT'**: an automatic transmission that can change seamlessly through a continuous range of gear ratios.
16. **'differential'**: a device that splits a torque into two branches (e.g. left-/right-hand wheels) while allowing unequal rotation speeds; the torque-splitting function can be biased or deactivated by a differential brake/lock device.
17. **'differential gear ratio'**: ratio of differential input speed (toward the primary propulsion energy converter) over differential output speed (toward driven wheels), both output shafts at equal speed.
18. **'drivetrain'**: connected elements of the powertrain for transmission of mechanical energy between propulsion energy converter(s) and the wheels.
35. **'gearbox'**: a device changing torque and speed with defined fixed ratios per gear; may include shiftable-gear functionality.
36. **'gear number'**: identifier for shiftable forward gears; gear with the highest gear ratio = number 1, increasing by 1 in descending order of gear ratios.
37. **'gear ratio'**: forward gear ratio of input-shaft speed (toward the primary propulsion energy converter) to output-shaft speed (toward driven wheels), without slip.

### 2.4 Electric machine terminology

19. **'electric machine' (EM)**: an energy converter transforming between electrical and mechanical energy.
20. **'electric machine system'**: a combination of electric powertrain components as installed in the vehicle comprising an electric machine, inverter and electronic control unit(s), including connections and interfaces for external systems.
21. **'electric machine type'**: one of (a) asynchronous machine (ASM), (b) excited synchronous machine (ESM), (c) permanent magnet synchronous machine (PSM), (d) reluctance machine (RM).
22. **'ASM'**: asynchronous machine — rotor current for torque is obtained by electromagnetic induction from the stator's rotating magnetic field.
23. **'ESM'**: excited synchronous machine — multiphase AC electromagnets on the stator create a field rotating with the line current; requires DC supplied to the rotor for excitation.
24. **'PSM'**: permanent-magnet synchronous machine — stator AC electromagnets create a rotating field; permanent magnets embedded in the steel rotor create a constant field.
25. **'RM'**: reluctance machine — stator AC electromagnets create a rotating field inducing non-permanent poles on an unwound ferromagnetic rotor; torque is generated via magnetic reluctance.
26. **'housing'**: an integrated/structural part of the component enclosing internal units, providing protection against direct contact.
27. **'energy converter'**: a system where output energy form differs from input energy form.
28. **'propulsion energy converter'**: a non-peripheral energy converter of the powertrain whose output energy is directly/indirectly used for vehicle propulsion.
29. **'category of propulsion energy converter'**: (i) internal combustion engine, (ii) electric machine, (iii) fuel cell.
30. **'energy storage system'**: stores energy and releases it in the same form as input.
31. **'propulsion energy storage system'**: a non-peripheral energy storage system of the powertrain whose output energy is used (directly/indirectly) for propulsion.
32. **'category of propulsion energy storage system'**: (i) fuel storage system, (ii) REESS, (iii) rechargeable mechanical energy storage system.
33. **'form of energy'**: (i) electrical, (ii) mechanical, (iii) chemical (incl. fuels).
34. **'fuel storage system'**: stores chemical energy as liquid or gaseous fuel.
43. **'internal combustion engine' or 'ICE'**: energy converter with intermittent/continuous oxidation of combustible fuel, transforming chemical ↔ mechanical energy.
44. **'inverter'**: an electric energy converter that changes DC to single-phase or polyphase AC.
45. **'peripheral device'**: any energy-consuming/converting/storing/supplying device not directly/indirectly used for propulsion but essential to powertrain operation (hence considered part of the powertrain).
46. **'powertrain'**: total combination in a vehicle of propulsion energy storage system(s), propulsion energy converter(s), the drivetrain(s) providing mechanical energy at the wheels for propulsion, plus peripheral devices.

### 2.5 IEPC / IHPC definitions — central to component-level HDEV modelling

40. **'integrated electric powertrain component' or 'IEPC'**: a combined system of an electric machine system together with the functionality of either a single- or multi-speed gearbox or a differential or both, characterised by **at least one** of:
   - shared housing of at least two components;
   - shared lubrication circuit of at least two components;
   - shared cooling circuit of at least two components;
   - shared electric connection of at least two components.
   Additionally, an IEPC must comply with **all** of:
   - only output shaft(s) toward driven wheels — **no input shaft(s)** for feeding propulsion torque in;
   - if more than one electric machine system is part of the IEPC, all electric machines must be connected to a **single DC power source** for all test runs under this Annex;
   - if a multi-speed-gearbox functionality is included, only **discrete** gear steps (no CVT).

41. **'IEPC design type wheel motor'**: an IEPC with either one or two output shafts connected directly to the wheel hub(s); two configurations:
   - **Configuration 'L'**: one output shaft — the same component is installed twice, symmetrically, left and right.
   - **Configuration 'T'**: two output shafts — a single component with one output shaft to the left and one to the right.

42. **'integrated hybrid electric vehicle powertrain component type 1' or 'IHPC Type 1'**: a combined system of **multiple** electric machine systems together with multi-speed-gearbox functionality, characterised by a **shared housing of all components** and **at least one** of:
   - shared lubrication circuit of at least two components;
   - shared cooling circuit of at least two components;
   - shared electric connection of at least two components.
   Additionally, an IHPC Type 1 must comply with **all** of:
   - only **one** input shaft (feeding propulsion torque in) and only **one** output shaft (toward driven wheels);
   - only discrete gear steps for all test runs (no CVT engagement during tests of the gearbox part);
   - must enable operation as a **parallel hybrid** (at least one specific mode used for all test runs);
   - must be testable in the transmission test under Annex VI with the electric power supply disconnected (point 4.4.1.2(b));
   - all electric machines connected to a **single DC power source** for all test runs;
   - the gearbox part shall **not** be operated as CVT for any test run under this Annex;
   - a **hydrodynamic torque converter shall not be part** of the IHPC Type 1.

   *(Methodological note, see file 12b §4.4: IHPC Type 1 is "virtually split" into two separate VECTO components for simulation — a virtual electric machine system and a virtual transmission — even though it is tested and certified as one physical unit. No family concept / standard values are allowed for IHPC Type 1; every individual type must be fully measured.)*

### 2.6 Other key terms

38. **'high-energy battery system' or 'HEBS'**: a battery system/representative subsystem for which the numerical ratio between (maximum discharge current in A, declared at 50% SOC per point 5.4.2.3.2) and (nominal electric charge output in Ah at 1C discharge rate at RT) is **< 10**.
39. **'high-power battery system' or 'HPBS'**: same ratio **≥ 10**.
   *(This HPBS/HEBS split drives nearly every subsequent battery test parameter — discharge C-rates, SOC test levels, pulse durations, standard-value defaults. See file 12c.)*
47. **'rated capacity'**: total number of ampere-hours withdrawable from a fully charged battery, determined per point 5.4.1.3.
48. **'rated speed'**: highest rotational speed of the electric machine system at which the overall maximum torque occurs.
49. **'room temperature' or 'RT'**: ambient air inside the test cell at **(25 ± 10) °C**.
50. **'state of charge' or 'SOC'**: available electrical charge stored in a battery system, expressed as % of rated capacity per 5.4.1.3 (0% = empty, 100% = full).
51. **'unit under test' or 'UUT'**: the electric machine system, IEPC or IHPC Type 1 actually tested.
52. **'battery UUT'**: the battery system or representative battery subsystem actually tested.
53. **'capacitor UUT'**: the capacitor system or representative capacitor subsystem actually tested.

### 2.7 Fuel Cell System (FCS) definitions — ►M4 (Reg. 2025/258)

54. **'FCS UUT'**: the fuel cell system ('FCS') or representative fuel cell ('FC') subsystem actually tested.
55. **'balance of plant' or 'BoP'**: the assembly of all supporting components and auxiliary systems of an FCS needed to deliver the energy, other than the generating unit itself (e.g. transformers, inverters, supporting structures).
56. **'BoP-component' or 'BoPC'**: a component belonging to a BoP.
57. **'air processing sub-system' or 'APS'**: assembly delivering air (oxygen-containing media) for reaction in the FCS; may provide air to the fuel processing sub-system, thermal management sub-system (TMS) and fuel cell stack sub-system (FCSS); may include filtration, purification, compression, humidification, flow control.
58. **'fuel processing sub-system' or 'FPS'**: converts supplied fuel (chemically/physically) to a form usable in the FCSS; may include pressure regulation, humidification, mixing. Also called "fuel processor subsystem" / "fuel processor."
59. **'thermal management sub-system' or 'TMS'**: provides thermal and water management for the FCS; may include accumulator, pump, radiator, condenser; may provide water recovery/humidification.
60. **'fuel cell stack sub-system' or 'FCSS'**: assembly containing one or more fuel-cell stacks where an electrochemical reaction (fuel + oxidant) converts chemical energy to electric energy. Includes connections for fuel/oxidant/exhaust, electrical connections for stack power, load-monitoring means. May include additional-fluid conduits, fault detection, enclosures/pressure vessels, ventilation. Also called "fuel cell module," "fuel cell power module," "fuel cell stack assembly."
61. **'fuel cell control sub-system'**: controls/monitors FCS conditions, automatically responds to vehicle power demand while preventing hazardous conditions/damage; generally a microprocessor-based device, may include diagnostics.
62. **'power distribution sub-system' or 'PDS'**: components connecting the FCSS to the power conditioning system, converting power for FCS use; may include cables, switches/contactors/relays, buses, connectors, instrumentation. **Has only DC power as input.**
63. **'fuel cell system' or 'FCS'**: energy converter transforming chemical energy into electric energy via series-connected electrochemical cells (the "fuel cell stack"). Includes all necessary BoP components to supply fuel, oxygen (e.g. as air), cooling and media conditioning for sound FC-stack operation. Different configurations ("Types," see Table 9 in file 12e) exist.
64. **'power conditioning system' or 'PCS'**: components converting the fuel cell stack's electric energy into vehicle-usable electricity. Includes **at least** a voltage regulator (DC/DC) and/or voltage converter (DC/AC); may connect to the cooling-media loop; interfaces between FCS and the battery/other electrical vehicle loads.
65. **'water treatment sub-system' or 'WTS'**: provides treatment of process water used in the FCS; may include a demineralizing/deionizing resin bed and instrumentation; may provide water recovery/humidification.
66. **'inner cooling loop' or 'ICL'**: in FCS designs with split inner (primary)/outer (secondary) cooling loops, a closed coolant loop connected to the different BoPCs' cooling media, integrated into the FCS as part of the TMS. Multiple ICLs may exist (e.g. one for power electronics PDS/PCS, one for FCSS).
67. **'outer cooling sub-system'**: components exchanging the FCS's waste heat (stored in the coolant fluid) with the environment; may include radiators, pumps, fans, other actuators.
68. **'external electric components'**: all electric components not part of the FCS and/or not electrically connected to the DC power between FCSS and PCS — includes the vehicle's electric machines and the REESS.
69. **'relative transition slope' or 'RTS'**: a coefficient expressing the change rate of the FCS electric-power-output set-point, relating the time-rate of change to the upper electric power output of the FCS.
70. **'system conditioning operating point' or 'SCOP'**: a set-point for electrical power output suited to condition the FCS during the specified conditioning-phase duration.
71. **'setpoint' or 'SP'**: the desired/target value for an essential variable or process value of a system.
72. **'process value' / 'process variable' or 'PV'**: the current measured value for an essential variable/process value.

### 2.8 Abbreviations (point 2, closing list)

| Abbreviation | Meaning |
|---|---|
| AC | alternating current |
| DC | direct current |
| DCIR | direct current internal resistance |
| EMS | electric machine system |
| OCV | open circuit voltage |
| SC | standard cycle |

---

## 3. General requirements (point 3 of Annex Xb)

> "The calibration laboratory facilities shall comply with the requirements of either IATF 16949, ISO 9000 series or ISO/IEC 17025. All laboratory reference measurement equipment, used for calibration and/or verification, shall be traceable to national or international standards."

### 3.1 Measurement equipment specifications — Table 1 (verbatim, with ►M3/►M4 markers as they appear in source)

| Measurement system | Accuracy (¹) | Amendment |
|---|---|---|
| Rotational speed | 0.5 % of the analyser reading **or** 0.1 % of max. calibration (²) of rotational speed, **whichever is larger** | ►M3 |
| Torque | 0.6 % of the analyser reading **or** 0.3 % of max. calibration (²) **or** 0.5 Nm of torque, **whichever is larger** | ►M3 |
| Fuel mass flow (³) | 1.0 % of the analyzer reading **or** 0.5 % of max. calibration (²), **whichever is larger** | ►M4 |
| Air/oxidant mass flow (¹) | 1.0 % of the analyzer reading **or** 0.5 % of max. calibration (²), **whichever is larger** | ►M4 |
| Cooling liquid mass flow | 2.5 % of the analyzer reading **or** 0.1 % of max. calibration (²), **whichever is larger** | ►M4 |
| Cooling liquid volume flow | 2.5 % of the analyzer reading **or** 0.1 % of max. calibration (²), **whichever is larger** | ►M4 |
| Cooling liquid pressure | 0.5 % of the analyzer reading **or** 0.1 % of max. calibration (²), **whichever is larger** | ►M4 |
| Fuel, ambient, air pressure | **1 kPa** | ►M4 |
| Current | 0.5 % of the analyser reading **or** 0.25 % of max. calibration (²) **or** 0.5 A of current, **whichever is larger** | ►M3 |
| Voltage | 0.5 % of the analyser reading **or** 0.25 % of max. calibration (²) of voltage, **whichever is larger** | ►M3 |
| Temperature | **1.5 K** | ►M3 |
| Dew point temperature | ±2.5 K of the analyzer reading **or** 1.0 % of max. calibration (²), **whichever is larger** | ►M4 |

Footnotes to Table 1:
1. **'Accuracy'** = the absolute value of deviation of the analyser reading from a reference value traceable to a national or international standard.
2. The **'maximum calibration'** value = the maximum predicted value for the respective measurement system expected during a specific test run under this Annex, multiplied by a factor of **1.1**.
3. If volume flow is metered, the accuracy shall be transferred as accuracy of mass-flow measurement.

**Multi-point calibration is allowed**: a measurement system may be calibrated up to a nominal value less than the capacity of the measurement system.

### 3.2 Data recording

- All measurement data, **except temperature**, shall be measured and recorded at a frequency of **not less than 100 Hz**.
- For **temperature**, a measurement frequency of **not less than 10 Hz** is sufficient.
- Signal filtering may be applied in agreement with the approval authority; any **aliasing effect shall be avoided**.

#### 3.2.1 Data recording for FCS-certification purposes (►M4)
For FCS certification, the sampling frequency shall be **constant**, with a sample frequency of **at least 10 Hz for all values** (this supersedes the general 100 Hz rule for the FCS-specific procedure of point 7).

#### 3.2.2 Sign convention of energy and media exchange over the UUT boundary for FCS certification (►M4)
Flow of media or energy **leaving** the UUT = **negative** sign; and vice-versa (entering = positive).
*(Note: this is the opposite sign convention used for current elsewhere in the Annex — see §4.1.9.2 in file 12b, where current drawn by the UUT from the supply is positive. Each sub-system's sign convention is local to its own section; always check which point number governs a given signal before combining datasets.)*
