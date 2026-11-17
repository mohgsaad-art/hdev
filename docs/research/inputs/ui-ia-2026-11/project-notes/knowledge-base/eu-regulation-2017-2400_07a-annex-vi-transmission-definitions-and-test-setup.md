# Annex VI — Verifying Transmission, Torque Converter, OTTC and ADC Data
## Part A: Introduction, Definitions, and General Test Setup

**Source:** Commission Regulation (EU) 2017/2400 (as implementing Regulation (EC) No 595/2009), consolidated text CELEX **02017R2400**, consolidation date **01.01.2026**, version 007.001.
**Range covered in this file:** Annex VI §1 (Introduction), §2 (Definitions), and the general/shared test-setup provisions of §3.1.2–3.1.5 (these apply across Options 1, 2 and 3 for transmission torque-loss testing).
**Companion files:**
- `07b-annex-vi-transmission-loss-measurement-and-maps.md` — Options 1/2/3 full procedures, formulas, uncertainty, input-file complement, standard/fallback values, simulation-tool input parameter tables, conformity-of-production testing.
- `07c-annex-vi-torque-converter-ottc-adc.md` — Torque converter (§4), OTTC/retarder (§5), ADC (§6, **including the EV-relevant Case C provision**), generic TC model, and component-specific information documents.

Amendment markers found in this range: **►B** (2017 baseline), **►M1** (Reg 2019/318), **►M3** (Reg 2022/1379). No ►M2 or ►M4 markers were visible in this specific sub-range (►M4 appears later, in the ADC section covered in file 07c).

---

## 1. Introduction

This annex describes the certification provisions regarding the torque losses of:
- **Transmissions**
- **Torque converter (TC)**
- **Other torque transferring components (OTTC)**
- **Additional driveline components (ADC)**

for heavy duty vehicles, and defines calculation procedures for standard (fallback) torque losses.

Key structural rule: TC, OTTC and ADC **can be tested either in combination with a transmission or as a separate unit**. If tested separately, the provisions of §4 (TC), §5 (OTTC) and §6 (ADC) apply. Torque losses from the drive mechanism connecting the transmission to these components **can be neglected**.

---

## 2. Definitions

All definitions below are "for the purposes of this Annex." Amendment markers are shown inline where the source text shows them.

1. **Transfer case** — a device that splits engine power and directs it to front and rear drive axles; mounted behind the transmission, both drive shafts connect to it; comprises a gearwheel set or chain drive system distributing power from transmission to axles. Typically can shift between standard drive mode (front or rear wheel drive), high-range traction mode (front and rear wheel drive), low-range traction mode, and neutral.

2. **Gear ratio** — forward gear ratio of input shaft speed (toward prime mover) to output shaft speed (toward driven wheels) without slip:
   `i = nin / nout`

3. **Ratio coverage** — ratio of largest to smallest forward gear ratios in a transmission:
   `φtot = imax / imin`

4. **Compound transmission** — a transmission with a large number of forward gears and/or large ratio coverage, composed of sub-transmissions combined to use most power-transferring parts in several forward gears.

5. **Main section** — the sub-transmission with the largest number of forward gears in a compound transmission.

6. **Range section** — a sub-transmission normally in series connection with the main section in a compound transmission; usually has two shiftable forward gears (low range gear → lower gears of the complete transmission; high range gear → higher gears).

7. **Splitter** — a design that splits the main section gears into two (usually) variants — low- and high-split gears — whose gear ratios are close compared to the ratio coverage of the transmission. Can be a separate sub-transmission, an add-on device, integrated with the main section, or a combination thereof.

8. **Tooth clutch** — a clutch where torque is transferred mainly by normal forces between mating teeth; can be engaged or disengaged only; operated in load-free conditions only (e.g., at gear shifts in a manual transmission).

9. **Angle drive** — a device transmitting rotational power between non-parallel shafts, often used with transversely oriented engine and longitudinal input to driven axle.

10. **Friction clutch** — a clutch for transfer of propulsive torque where torque is sustainably transferred by friction forces; can transmit torque while slipping; may (but need not) be operated at start-offs and at powershifts (retained power transfer during a gear shift).

11. **Synchroniser** — a type of tooth clutch where a friction device equalises the speeds of the rotating parts to be engaged.

12. **Gear mesh efficiency** — ratio of output power to input power when transmitted in a forward gear mesh with relative motion.

13. **Crawler gear** — a low forward gear (speed reduction ratio larger than for non-crawler gears) designed for infrequent use, e.g., low-speed manoeuvres or occasional up-hill start-offs.

14. **Power take-off (PTO)** — a device on a transmission or engine to which an auxiliary driven device (e.g., a hydraulic pump) can be connected.

15. **Power take-off drive mechanism** — a device in a transmission that allows installation of a PTO.

16. **Lock-up clutch** — a friction clutch in a hydrodynamic torque converter; can connect input and output sides, eliminating slip. ►M3 In some cases permanent slip in fixed gears is intended, e.g. to prevent vibrations. ◄

17. ►M3 **Start-off clutch** — a clutch that adapts speed between engine and driving wheels when the vehicle starts off. ◄ Usually located between engine and transmission.

18. **Synchronised Manual Transmission (SMT)** — a manually operated transmission with two or more selectable speed ratios obtained using synchronisers. Ratio changing is normally achieved during a temporary disconnection of the transmission from the engine using a clutch (usually the vehicle start-off clutch).

19. **Automated Manual Transmission / Automatic Mechanically-engaged Transmission (AMT)** — an automatically shifting transmission with two or more selectable speed ratios obtained using tooth clutches (un-/synchronised). Ratio changing achieved during temporary disconnection from the engine. Shifts performed by an electronically controlled system managing shift timing, clutch operation, and engine speed/torque. System selects and engages the most suitable forward gear automatically but can be overridden by the driver in manual mode.

20. **Dual Clutch Transmission (DCT)** — an automatically shifting transmission with two friction clutches and several selectable speed ratios obtained by tooth clutches. Ratio shifts performed by an electronically controlled system. System selects the most suitable gear automatically, overridable in manual mode. ►M3 In some cases permanent slip in fixed gears is intended, e.g. to prevent vibrations. ◄

21. **Retarder** — an auxiliary braking device in a vehicle powertrain, aimed at permanent braking.

22. ▼M3 **Case S** — an Automatic Powershifting Transmission (APT) with **serial** arrangement of a torque converter and the connected mechanical parts of the transmission.

23. ▼M3 **Case P** — an APT with **parallel** arrangement of a torque converter and the connected mechanical parts of the transmission (e.g. power-split installations).

24. **Automatic Powershifting Transmission (APT)** — an automatically shifting transmission with more than two friction clutches and several selectable speed ratios obtained mainly by use of friction clutches. Ratio shifts performed by electronically controlled system; shifts normally performed without traction interruption (friction clutch to friction clutch).

25. **Oil conditioning system** — an external system that conditions the oil of a transmission at testing, circulating oil to and from the transmission, filtering and/or temperature conditioning it.

26. **Smart lubrication system** — a system affecting the load-independent losses (spin/drag losses) of the transmission depending on input torque and/or power flow. Examples: controlled hydraulic pressure pumps for brakes/clutches in an APT, controlled variable oil level, controlled variable oil flow/pressure for lubrication/cooling. May include oil-temperature control, but systems designed *only* for temperature control are **not** considered smart lubrication (since the transmission test procedure has fixed test temperatures).

27. **Transmission electric auxiliary** — an electric auxiliary used for the function of the transmission during steady-state operation (typical example: electric cooling/lubrication pump) — but **not** electric gear-shift actuators or electronic control systems/solenoid valves (low energy consumers, especially at steady-state operation).

28. **Oil type viscosity grade** — a viscosity grade as defined by SAE J306.

29. **Factory fill oil** — the oil type viscosity grade used for the factory oil fill, intended to remain in the transmission/TC/OTTC/ADC for the first service interval.

30. **Gearscheme** — the arrangement of shafts, gearwheels and clutches in a transmission.

31. **Powerflow** — the transfer path of power from input to output in a transmission via shafts, gearwheels and clutches.

32. ▼M3 **Differential** — a device that splits a torque into two branches (e.g. for left- and right-hand side wheels) while allowing these branches to rotate at unequal speeds. The torque-splitting function can be biased or deactivated by a differential brake- or differential-lock device (if applicable).

33. ▼M3 **Case N** — an APT **without** a torque converter.

> **EV/Hybrid relevance note:** None of these 33 definitions explicitly names an electric machine, battery, or single-speed EV reduction gear. The definitions are built around conventional friction/tooth clutches, torque converters, and planetary gearsets. The explicit EV-specific provision in this Annex appears later, in §6.1.3 "Case C" (an M4 amendment) covering a belt connecting an electric machine system to the main powertrain — see file `07c`. The "IHPC Type 1" transmission-type value found in Appendix 12 (file `07b`) is also flagged there as likely EV/hybrid-relevant.

---

## 3. Testing procedure for transmissions — structural overview

For testing the losses of a transmission, **the torque loss map for each individual transmission type shall be measured**. Transmissions may be grouped into families with similar/equal CO2-relevant data per Appendix 6 (family concept — summarised later in this file).

For determining transmission torque losses, the applicant for a certificate shall apply **one of the following methods for each single forward gear** (crawler gears excluded):

1. **Option 1**: Measurement of the torque independent losses, calculation of the torque dependent losses.
2. **Option 2**: Measurement of the torque independent losses, measurement of the torque loss at maximum torque, and interpolation of the torque dependent losses based on a linear model.
3. **Option 3**: Measurement of the total torque loss.

> The full formulas, calculation steps, measurement sequences, validation criteria and uncertainty budgets for each option are reproduced in file `07b` of this knowledge base — they are long and option-specific, so they are kept together there. This file (07a) covers only the setup/administrative provisions that are **common to all three options** (3.1.2 General requirements through 3.1.5 Measurement signals), reproduced in full below.

---

## 3.1.2. General requirements for transmission testing (applies to all options)

### 3.1.2.1. General requirements
The transmission used for measurements shall be in accordance with the drawing specifications for series production transmissions and **shall be new**.

Modifications to meet testing requirements of this Annex (e.g. inclusion of measurement sensors, adaptation of an external oil conditioning system) are permitted.

The tolerance limits in this paragraph refer to measurement values **without sensor uncertainty**.

▼M1 Total tested time per transmission individual and gear **shall not exceed 5 times the actual testing time per gear** (allowing retesting of transmission if needed due to measuring or rig error). ◄

▼B The same transmission individual may be used for a **maximum of 10 different tests** (e.g. tests of torque losses for variants with/without retarder, with different temperature requirements, or with different oils). If the same transmission individual is used for tests of different oils, the **recommended factory fill oil shall be tested first**.

It is **not permitted** to run a certain test multiple times to choose a test series with the lowest results.

Upon request of the approval authority, the applicant for a certificate shall specify and prove conformity with the requirements defined in this Annex.

### 3.1.2.2. Differential measurements
To subtract influences caused by the test rig setup (e.g. bearings, clutches) from the measured torque losses, differential measurements are permitted to determine these **parasitic torques**.

►M3 The measurements shall be performed at the same speed points and same test rig bearing temperature(s) **± 3 K** used for the testing. ◄ The torque sensor measurement uncertainty shall be below **0,3 Nm**.

### 3.1.2.3. Run-in
On request of the applicant, a run-in procedure may be applied, subject to:
- 3.1.2.3.1. Not exceeding **30 hours per gear** and **100 hours in total**.
- 3.1.2.3.2. Applied input torque limited to **100 %** of maximum input torque.
- 3.1.2.3.3. Maximum input speed limited by the specified maximum speed for the transmission.
- 3.1.2.3.4. Speed/torque profile for the run-in procedure specified by the manufacturer.
- 3.1.2.3.5. Run-in procedure documented by the manufacturer re: run-time, speed, torque, oil temperature, and reported to the Approval authority.
- 3.1.2.3.6. The requirements for ambient temperature (3.1.2.5.1.), measurement accuracy (3.1.4.), test set-up (3.1.8.) and installation angle (3.1.3.2.) **do not apply** to the run-in procedure.

### 3.1.2.4. Pre-conditioning
- 3.1.2.4.1. Pre-conditioning of transmission and test rig equipment (to achieve correct/stable temperatures before run-in/testing) is allowed.
- ▼M3 3.1.2.4.2. Pre-conditioning shall be performed **without applied torque to the non-driven shaft**.
- ▼B 3.1.2.4.3. Maximum input speed limited by the specified maximum speed for the transmission.
- 3.1.2.4.4. Maximum combined pre-conditioning time: **50 hours total** per transmission. May be split into sequences; each single pre-conditioning sequence shall not exceed ►M3 **100** ◄ minutes.
- 3.1.2.4.5. Pre-conditioning time is **not** counted against the run-in/test time budgets.

### 3.1.2.5. Test conditions

**3.1.2.5.1. Ambient temperature**
Range: **25 °C ± 10 K**, measured **1 m laterally** from the transmission. Does not apply during run-in.

**3.1.2.5.2. Oil temperature**
Except for the oil, **no external heating is allowed**. During measurement (except stabilisation):

| Transmission type | Without retarder | With retarder |
|---|---|---|
| SMT / AMT / DCT | ≤ 83 °C (drain plug) | ≤ 87 °C |
| TC planetary transmissions, or transmissions with > 2 friction clutches | ≤ 93 °C | ≤ 97 °C |

If measurements of a transmission without retarder are combined with separate retarder measurements, the **lower** temperature limit applies (to compensate for retarder drive mechanism/step-up gear and the clutch of a disengageable retarder).

To apply the increased "with retarder" limits, the retarder must be integrated in the transmission or have an integrated cooling/oil system with the transmission.

During run-in, the same oil-temperature specs as regular testing apply. **Exceptional peaks up to 110 °C** are allowed:
1. During run-in, up to max. **10 %** of the applied run-in time.
2. During stabilisation time.

Oil temperature measured at the drain plug or in the oil sump.

**3.1.2.5.3. Oil quality**
New, recommended first-fill oil for the European market shall be used. Same oil fill may be used for run-in and torque measurement.

**3.1.2.5.4. Oil viscosity**
If multiple oils are recommended for first fill, they are considered **equal** if kinematic viscosity is within **10 %** of each other at the same temperature (within the specified KV100 tolerance band). Any oil with lower viscosity than the test oil is assumed to produce lower losses. Additional first-fill oils must fall either within the 10 % band or have lower viscosity to be covered by the same certificate.

**3.1.2.5.5. Oil level and conditioning**
Oil level must meet nominal transmission specifications. If an external oil conditioning system is used, the oil inside the transmission shall be kept at the specified volume corresponding to the specified oil level.

**Conditioning-system validation check**: one test point measured with conditioning system **on and off**; deviation between the two torque-loss (= input torque) measurements shall be **< 5 %**. Test point specification:
1. Gear = highest indirect gear.
2. ▼M3 Input speed = minimum of **60 %**, not higher than **80 %** of max input speed.
3. Temperatures per 3.1.2.5.

For transmissions with hydraulic pressure control or a smart lubrication system, torque-independent-loss measurement shall be performed with **two settings**: (a) transmission system pressure at least the minimum value for conditions with engaged gear; (b) maximum possible hydraulic pressure (see 3.1.6.3.1., reproduced in file 07b).

---

## 3.1.3. Installation (applies to torque-independent-loss testing under all options)

▼M3 3.1.3.1. The electric machine and torque sensor shall be mounted to the **input side** of the transmission. The output shaft(s) shall rotate freely. For a transmission with an **integrated differential** (e.g. front-wheel drive), the output ends shall be allowed to be rotatably locked into each other (e.g. activated differential lock, or any other mechanical differential lock implemented only for the measurement).

▼B 3.1.3.2. Installation shall be at the angle of inclination as for vehicle installation per the homologation drawing **± 1°**, or at **0° ± 1°**.

3.1.3.3. The internal oil pump shall be included in the transmission.

3.1.3.4. If an oil cooler is optional or required, it may be excluded from the test, or any oil cooler may be used.

3.1.3.5. Testing can be done with or without power take-off drive mechanism and/or PTO. For PTO/PTO-drive-mechanism power losses, values in ►M3 Annex IX ◄ apply, assuming the transmission is tested *without* PTO drive mechanism/PTO.

3.1.3.6. Measurement may be performed with or without single dry clutch (1 or 2 plates) installed. Clutches of any other type **shall** be installed during the test.

3.1.3.7. The individual influence of parasitic loads shall be calculated for each specific test rig setup and torque sensor as described in 3.1.8 (see file 07b).

---

## 3.1.4. Measurement equipment (applies across all options; Options 2/3 add their own stricter torque-sensor tolerance for the torque-dependent part — see file 07b)

Calibration laboratory facilities shall comply with either ►M3 **IATF** ◄ 16949, ISO 9000 series, or ISO/IEC 17025. All laboratory reference measurement equipment used for calibration/verification shall be traceable to national (international) standards.

| Signal | Uncertainty requirement |
|---|---|
| **3.1.4.1. Torque** | Sensor uncertainty < **0,3 Nm** (higher-uncertainty sensors allowed if the excess over 0,3 Nm is calculated and added to the measured torque loss per 3.1.8.) |
| **3.1.4.2. Speed** | ≤ **± 1 rpm** |
| **3.1.4.3. Temperature** | Ambient: ≤ **± 1,5 K**; Oil: ≤ **± 1,5 K** |
| **3.1.4.4. Pressure** | ≤ **1 %** of max measured pressure |
| ▼M3 **3.1.4.5. Voltage** | ≤ **1 %** of max measured voltage |
| **3.1.4.6. Electric current** | ≤ **1 %** of max measured current |

---

## 3.1.5. Measurement signals and data recording

At least the following signals shall be recorded during measurement:
1. Input torques [Nm]
2. Input rotational speeds [rpm]
3. Ambient temperature [°C]
4. Oil temperature [°C]

If equipped with a hydraulically-controlled shift/clutch system or a mechanically driven smart lubrication system, additionally:
5. Oil pressure [kPa]

If equipped with transmission electric auxiliary, additionally:
6. Voltage of transmission electric auxiliary [V]
7. Current of transmission electric auxiliary [A]

For differential measurements (compensating test-rig-setup influences), additionally:
8. Test rig bearing temperature [°C]

**Sampling/recording rate: ≥ 100 Hz.** A low-pass filter shall be applied to reduce measurement errors.

> Note: Option 3's version of this clause (3.3.7, covered in file 07b) additionally requires recording **output** torque and speed, since Option 3 measures total (input-to-output) torque loss directly.

---

## Appendix 6 — Family Concept (summary; general/administrative — applies across transmission, TC, OTTC and ADC)

*(Full appendix text reproduced in detail; this appendix governs how manufacturers group components for certification and is cross-referenced from §3, §4, §5 and §6.)*

**1. General**: A transmission/TC/OTTC/ADC family is characterised by common design and performance parameters among all family members. The manufacturer decides family membership subject to the criteria below; the Approval Authority must approve the family, and the manufacturer must supply appropriate member information.

**1.1 Special cases**: Where parameter interactions exist, or where devices/features not listed in §9 of this appendix strongly influence performance level, the manufacturer must identify these (on the basis of good engineering practice) and notify the Approval Authority — such features become a criterion for a new family.

**1.2**: The family concept exists to let manufacturers group components with similar/equal CO2-relevant data.

**2.** The Approval Authority may require additional testing to characterise the highest torque loss within a family; if family members incorporate other loss-relevant features, these must be identified and factored into parent selection.

**3. Transmission family — parameters that must be identical across all members (3.1):**
(a) Gear ratio, gearscheme and powerflow (forward gears only, crawler gears excluded)
(b) Center distance for countershaft transmissions
(c) Type of bearings at corresponding positions (if fitted)
(d) Type of shift elements (tooth clutches incl. synchronisers, or friction clutches) at corresponding positions

**Transmission family — parameters that must be common, with an Approval-Authority-approved range permitted (3.2):**
(a) Single gear width ± 1 mm
(b) Total number of forward gears
(c) Number of tooth shift clutches
(d) Number of synchronisers
(e) Number of friction clutch plates (except single dry clutch, 1–2 plates)
(f) Outer diameter of friction clutch plates (same exception)
(g) Surface roughness of the teeth
(h) Number of dynamic shaft seals
(i) Oil flow for lubrication/cooling per input shaft revolution
(j) Oil viscosity (± 10 %)
(k) System pressure for hydraulically controlled gearboxes
(l) Specified oil level (reference to central axis, per drawing spec, average of tolerance band; oil level considered equal if all rotating parts except the oil pump/drive are above it)
(m) Specified oil level (± 1 mm)

**4. Parent transmission selection** — the parent is chosen by, in order: highest single gear width → highest total gear count → highest tooth shift clutch count → highest synchroniser count → highest friction clutch plate count → highest friction plate OD → highest tooth surface roughness → highest dynamic shaft seal count → highest lubrication/cooling oil flow → highest oil viscosity → highest hydraulic system pressure → highest specified oil level (central-axis ref.) → highest specified oil level (±1 mm).

**5–6. TC family parameters & parent selection** — for serial (no mechanical transmission) TCs: outer/inner torus diameter, P/T/S flow-direction arrangement, torus width, oil type, blade design must be identical; any member can be parent if these match. For parallel (with mechanical transmission) TCs, the same list applies plus gear scheme/power flow in TC mode, bearing types, cooling/lubrication pump type, shift element types; oil level (per drawing, central-axis ref.) may vary within an approved range, and parent = highest such oil level.

**7–8. OTTC family parameters & parent selection** — separate criteria sets for (i) hydrodynamic retarder/OTTC (outer torus diameter, torus width, blade design, operating fluid — identical; OD-ID, blade count, fluid viscosity ±50% — rangeable; parent = highest OD-ID, highest blade count, highest viscosity), (ii) magnetic retarder/OTTC (drum design, outer rotor diameter, cooling blade design, blade design — identical; OD-ID, rotor count, cooling-blade count, arm count — rangeable; parent = highest of each), and (iii) hydrodynamic-clutch OTTC (outer torus diameter, torus width, blade design — identical; fluid viscosity ±10%, OD-ID, blade count — rangeable; parent = highest of each).

**9–10. ADC/angle-drive family parameters & parent selection** — identical: gear ratio & gearscheme, shaft angle, bearing type. Rangeable: single gear width, dynamic shaft seal count, oil viscosity ±10%, tooth surface roughness, specified oil level (central-axis ref.). Parent = highest of each rangeable parameter.

---

## Appendix 7 — Markings and Numbering (administrative; applies to all certified components)

**1. Markings** — a certified component shall bear:
1.1. ▼M1 Manufacturer's name/trade mark.
1.2. ▼M1 Make and type indication per information document points 0.2/0.3.
1.3. Certification mark: a rectangle around lower-case "**e**" followed by the Member-State distinguishing number (full 29-state list reproduced in source, e.g. 1=Germany, 2=France, 3=Italy, 4=Netherlands, 5=Sweden, 6=Belgium, 7=Hungary, 8=Czech Republic, 9=Spain, 11=UK, 12=Austria, 13=Luxembourg, 17=Finland, 18=Denmark, 19=Romania, 20=Poland, 21=Portugal, 23=Greece, 24=Ireland, 25=Croatia, 26=Slovenia, 27=Slovakia, 29=Estonia, 32=Latvia, 34=Bulgaria, 36=Lithuania, 49=Cyprus, 50=Malta).
1.4. ►M3 The mark also includes, near the rectangle, the "base approval number" (per Section 4 of the type-approval number format in Annex IV to Reg (EU) 2020/683), preceded by **two digits** for the sequence number of the latest technical amendment to this Regulation and an **alphabetical character** for the certified part (Table 1 below). ◄ Sequence number for this Regulation = ►M3 **02**◄.

**Table 1 — component letter code:**
| Letter | Component |
|---|---|
| G ▼M1 | Transmission |
| C | Torque Converter (TC) |
| O | Other torque transferring component (OTTC) |
| D | Additional driveline component (ADC) |

▼M3 1.5. Worked example: mark on a component certified in Poland (e20) under this Regulation; "02" = sequence number of latest amendment; next digit = component letter (e.g. "G" = transmission); last five digits (e.g. 00005) = base approval number assigned by the approval authority.

1.6. Other type sizes than in 1.5 permitted on request, with prior approval-authority agreement, provided clearly legible.

1.7. Markings/labels/plates/stickers must be durable for the component's useful life, clearly legible, indelible, and not removable without destruction/defacement.

1.8. If separate certificates for transmission/TC/OTTC/ADC are granted by the same approval authority and the parts are installed in combination, **one** certification mark (per 1.3) suffices, followed by the applicable 1.4 markings for each component, separated by "/".

1.9. The certification mark must be visible when installed on the vehicle, affixed to a part necessary for normal operation that does not normally require replacement during component life.

1.10. If TC or OTTC is not accessible/visible once assembled with a transmission, its certification mark goes on the transmission instead. If the TC/OTTC is **uncertified**, a "–" is shown instead of the certification number next to the relevant Table-1 letter.

**2. Numbering**
▼M3 2.1. Certification number format:
```
eX*YYYY/YYYY*ZZZZ/ZZZZ*X*00000*00
 section1  section2  section3  +letter   section4  section5
```
- Section 1: country issuing the certificate
- Section 2: HDV CO2 determination Regulation "2017/2400"
- Section 3 + letter: latest amending Regulation (ZZZZ/ZZZZ) + Table-1 component letter
- Section 4: base certification number (00000)
- Section 5: extension (00)

---

## Appendices 1 & 2 (brief pointer — full templates not reproduced here)

**Appendix 1** sets out the **model certificate** for a transmission/TC/OTTC/ADC family (max format A4), including Section I (manufacturer identification fields 0.1–0.7) and Section II (test-option declaration field 1.1, specifying — for transmissions — the option used for **each output-torque range** 0–10 kNm and >10 kNm, separately per gear; approval authority; test-report date/number; remarks; signature block).

**Appendix 2** sets out the **transmission information document** template: general identification fields (0.1–0.10), Part 1 "Essential characteristics of the (parent) transmission and transmission types within a family" covering items 1.1–1.19 (gear ratio/gearscheme/powerflow; center distance; bearing/shift-element types; gear width; forward gear count; shift clutch/synchroniser counts; friction clutch plate count/diameter; tooth surface roughness; dynamic shaft seal count; oil flow/viscosity/system pressure/level; and, per 1.18 ►M3◄, **gear ratio, max input torque, max input power and max input speed per gear, for the highest-rated version per family member**). ▼M3 Item 1.19 requires declaring whether the **TC lock-up clutch (or input-side clutch) has permanent slip in fixed gears**, and if so, a full slip map `TC-slip [rpm]` vs. input torque/speed per gear is required (the source gives gear-1 worked example data, reproduced verbatim below).

**Worked example — Appendix 2, item 1.19, "TC-slip [rpm] Gear 1" (input torque reference, Nm, rows; input speed reference, rpm, columns 600/900/1200/1600/2000/2500):**

| Input Torque Ref. (Nm) | 600 rpm | 900 rpm | 1200 rpm | 1600 rpm | 2000 rpm | 2500 rpm |
|---|---|---|---|---|---|---|
| 0 | 20 | 50 | 60 | 60 | 60 | 60 |
| 200 | 30 | 40 | 10 | 10 | 10 | 10 |
| 400 | 30 | 40 | 20 | 20 | 20 | 20 |
| 600 | 30 | 40 | 20 | 20 | 20 | 20 |
| 900 | 30 | 40 | 20 | 20 | 20 | 20 |
| 1200 | 30 | 40 | 20 | 20 | 20 | 20 |

Attachment 1 to the transmission information document requires: measurement with retarder (yes/no); measurement with angle drive (yes/no); maximum tested input speed [rpm]; maximum tested input torque [Nm].

> Appendices 3, 4 and 5 (TC / OTTC / ADC information documents) are component-specific and are reproduced in full in file `07c-annex-vi-torque-converter-ottc-adc.md`, alongside the relevant test procedures.

---

## Ambiguities / OCR flags in this file's range
- The document is a consolidated EUR-Lex text; mathematical symbols were frequently mis-OCR'd in the source extraction (e.g. "=" rendered as "¼", "−" as "Ä", "×" as "Ü", square-root glyphs broken across lines). This file's range (§1–§2, §3.1.2–§3.1.5) is **prose-only** and was not affected by this issue — no formulas appear here. The formula-heavy sections (§3.1.1, §3.1.6–3.1.8, §3.2–3.4) are handled in file `07b`, which flags the OCR garbling explicitly and gives reconstructed readable forms alongside the raw extracted text.
- No figures/diagrams appear in this file's range.
