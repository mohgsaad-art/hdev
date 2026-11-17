# SR7/LOT4 Final Report — Chapter 4.3.5: Generic Data in VECTO for Official CO2 Simulation

> Part of the multi-file extraction of `sr7_lot4_final_report_en.pdf` (Service contract CLIMA.C.2/SER/2012/0004, EC DG CLIMA, report dated 30.10.2017). See `sr7-lot4-01-overview-and-metadata.md` for full document metadata and companion-file list.
>
> **★ HIGH RELEVANCE TO HDEV SIZING/MODELLING:** This chapter is the single most directly reusable section of the report for an HDEV/depot sizing tool. It defines the entire generic-data scaffolding (mission profiles/driving cycles, vehicle segmentation, standard bodies/trailers, representative payloads, auxiliary power demand, wheel/tyre data, fuel/energy properties, ambient conditions) that any physically-grounded HDV simulation — electric or otherwise — needs to define equivalently. Note throughout: **all data in this chapter is for conventional (ICE) diesel/CNG/LPG/ethanol-fuelled trucks only** — no electric-specific generic data exists in this report.

## Table 6 — Segmentation matrix (vehicle group definitions)

The "segmentation matrix" defines, per **vehicle group**, the applicable mission profile(s), vehicle configuration, and allocated standard body, as a function of axle/chassis configuration and technically permissible maximum laden mass.

| Axle config. | Chassis config. | Max laden mass (t) | Group | Long haul | Long haul (EMS) | Regional delivery | Regional delivery (EMS) | Urban delivery | Municipal utility | Construction |
|---|---|---|---|---|---|---|---|---|---|---|
| 4x2 | Rigid (or tractor)* | 7.5–10 | 1 | — | — | R | — | R | — | B1 |
| 4x2 | Rigid (or tractor)* | >10–12 | 2 | R+T1 | — | R | — | R | — | B2 |
| 4x2 | Rigid (or tractor)* | >12–16 | 3 | — | — | R | — | R | — | B3 |
| 4x2 | Rigid | >16 | 4 | R+T2 | — | R | — | — | — | B4 |
| 4x2 | Tractor | 7.5–16 | 5 | T+ST1 | T+ST1+T2 | T+ST1 | — | — | — | — |
| 4x4 | Rigid | >16 | (6) excluded | | | | | | | |
| 4x4 | Rigid | >16 | (7) excluded | | | | | | | |
| 4x4 | Tractor | all weights | (8) excluded | | | | | | | |
| 6x2 | Rigid | all weights | 9 | R+T2 | — | R+D+ST1 | — | R | R+D+ST1 | R... B5 |
| 6x2 | Tractor | all weights | 10 | T+ST1 | T+ST1+T2 | T+ST1 | — | — | T+ST1+T2 | |
| 6x4 | Rigid | all weights | 11 | R+T2 | — | R+D+ST | — | R | R+D+ST | R B5 |
| 6x4 | Tractor | all weights | 12 | T+ST1 | T+ST1+T2 | T+ST1 | — | — | T+ST1+T2 | T+ST1 |
| 6x6 | Rigid | all weights | (13) excluded | | | | | | | |
| 6x6 | Tractor | all weights | (14) excluded | | | | | | | |
| 8x2 | Rigid | all weights | (15) excluded | | | | | | | |
| 8x4 | Rigid | all weights | 16 | — | — | — | — | — | — | R |
| 8x6/8x8 | Rigid | all weights | (17) excluded | | | | | | | |

*(This table is reproduced as faithfully as possible from the source's dense layout; some cell/column alignments in the original PDF table were ambiguous after text extraction — flagged as "[unclear from source: exact cell alignment of Table 6 for a few group/mission combinations may not be pixel-perfect versus the original PDF table, though all group definitions and legend values are verbatim]".)*

**Legend:** EMS = European Modular System (permits longer/heavier combinations on parts of the road network); EMS results computed by VECTO **only for vehicles with rated power ≥300 kW**. R = Rigid & standard body; T1, T2 = standard trailers; ST1 = standard semitrailer; D = standard dolly. (** in these vehicle classes tractors are treated as rigids but with specific tractor curb weight.)

## 4.3.5.1 Mission Profiles and CO2 Cycles

VECTO uses **target speed cycles ("CO2 test cycles")** — defining desired/traffic-limited velocity over trip distance. **5 cycles for HGVs and 5 for buses/coaches** were developed, coordinated by ACEA with consortium support; cycles were validated against the WHDC database during LOT3.

**Implemented mission profiles:** Long haul; Regional delivery; Urban delivery; Construction; Municipal utility; Citybus heavy urban; Citybus urban; Citybus suburban; Interurban bus; Coach.

**Cycles reviewed/amended during SR7:** Long haul; Regional delivery; Municipal utility; Citybus suburban. ("Urban delivery" and "Construction" cycle updates were still under ACEA review at project end and not assessable within SR7.)

### Long Haul cycle (amended, 2015 update)
Based on an ACEA-commissioned SIOUX LIME assessment (ref [8]). LIME's finding on the pre-update cycle: "the average speed is low compared to the measurements. Approximately 10% of the distance is travelled at a speed of 60 km/h or less... the CO2-cycle contains a relatively high number of large speed fluctuations. On the contrary, at 80 km/h, the CO2-cycle does not induce any minor speed fluctuations due to traffic behaviour."
- **"[Figure 21 description: target speed and gradient profile with stop-time markers for the updated (2015) Long Haul cycle — 100 km distance, ~80 km/h average speed, 67 seconds total stop time.]"**
- Updated cycle: **100 km distance, ~80 km/h average speed, 67 s total stop time.**
- **"[Figure 22 description: cumulative time-weighted vehicle-speed frequency distribution curves comparing 7 real-world WHDC-database long-haul vehicles (veh 17,18,31–35) against the old and amended VECTO Long Haul cycles — the amended cycle shifts the distribution but the report notes the amendment "cannot be justified" by the (18–20-year-old) WHDC data alone, while acknowledging LIME's newer 18-trip European dataset (300–1500 km trips) is more current and methodologically sound; the amended cycle also lacks traffic-jam sections seen in real agglomeration driving.]**

### Regional Delivery cycle (2016 update)
LIME finding on pre-update cycle: too much distance at ≤50 km/h legal-speed roads; too little on >50 km/h non-highway roads; sufficient highway share already present.
- **"[Figure 23 description: target speed/gradient profile with stop times for the updated (2016) Regional Delivery cycle — 100 km distance, ~60 km/h average speed, 746 s total stop time.]"**
- **"[Figure 24 description: cumulative time-weighted speed-frequency distribution comparing old vs. amended Regional Delivery cycle against WHDC trips of 50–150 km distance; the amended curve tracks the WHDC average better except stop-phase frequency is significantly higher (12% vs. 7%), outside the WHDC data range.]"**

### Municipal Utility cycle (refuse truck, rear-loader type)
Three parts: (1) approach to collection area, (2) collection, (3) drive to waste processing site. Parts 1&3 plus a draft collection part were from LOT3; **the collection part was updated in SR7 to align with DIN SPEC 30752-1** [ref 6]. Collection part: 20 m and 40 m distance segments with 25-second stops including garbage-collection PTO power draw (elaborated jointly with **DIN NA 051 "Normenausschuss Kommunale Technik" (NKT), Germany**).
- **"[Figure 25 description: speed/distance profile of the Municipal cycle (2017 update) — total 11.2 km distance, ~9 km/h average speed; the collection-part sub-segment covers 2.9 km at ~3 km/h average speed.]"**

### Suburban public transport bus cycle (2016 update)
- **"[Figure 26 description: speed/gradient/stop-time profile of the updated (2016) Suburban bus cycle.]"**
- **"[Figure 27 description: cumulative time-weighted speed-frequency distributions comparing old vs. amended Suburban cycle against WHDC bus data (Switzerland inter-city veh 29; Germany suburban/inter-city veh 22, 24) and 2010 Ruhrgebiet measurements (Düsseldorf, Essen, Hagen); the amended cycle is shifted ~3 km/h higher between 15–55 km/h, and low speeds (already underrepresented in the old cycle) remain underrepresented.]"**

### N2 vehicle cycle-representativeness comparison (relevant to sizing smaller HDEVs — see file 06 for full N2/M2 discussion)
A speed-capped WLTC (cap 88 km/h, same total distance as uncapped) was compared against WHDC real-world N2 driving data and VECTO Urban/Regional Delivery cycles.
- **"[Figure 28 description: speed-time trace comparing the original WLTC 3b and a speed-capped WLTC 3a (cap 88 km/h) over ~1900 seconds.]"**
- **"[Figures 29–33 description: five cumulative speed-frequency-distribution plots (one per N2 vehicle, WHDC database vehicles 1–4 and 11, GVM 5,600–12,000 kg) each comparing multiple real-world journeys against the capped WLTC, VECTO Urban Delivery, and amended Regional Delivery cycles — used to assess representativeness for the N2/M2 segment.]"**

## 4.3.5.2 Standard Bodies and Standard Trailers

### Table 7 — VECTO parameters for standard bodies and standard trailers
| Name | Curb mass [kg] | Max gross mass [kg] | Delta CdxA for trailer operation in long haul [m²] (as 1st trailer) | Delta CdxA (as 2nd trailer, EMS) | Axle count | Wheels dimension | Tyre RRC [N/kN] | Cargo volume [m³] |
|---|---|---|---|---|---|---|---|---|
| B1 | 1,600 | — | — | — | — | — | — | 36.5 |
| B2 | 1,900 | — | — | — | — | — | — | 45.2 |
| B3 | 2,000 | — | — | — | — | — | — | 47.7 |
| B4 | 2,100 | — | — | — | — | — | — | 49.4 |
| B5 | 2,200 | — | — | — | — | — | — | 51.9 |
| T1 | 3,400 | 10,500 | 1.3 | — | 2 | 235/75 R17.5 | 5.5 (mid of energy class "C") | 39.8 |
| T2 | 5,400 | 18,000 | 1.5 | 1.5 | 2 | 385/65 R22.5 | — | 49.5 |
| ST1 | 7,500 | 24,000 | 0 | 2.1 | 3 | 385/65 R22.5 | — | 91 |
| Dolly | 2,500 | 12,000 | — | — | 2 | 315/70 R22.5 | — | 0 |

*(Note: table column alignment for T1/T2/ST1's tyre-RRC and CdxA-delta values reproduced as best-effort from a dense source table; "[unclear from source: a few cell values in the original Table 7 layout were ambiguous after OCR/text-extraction and are reproduced with best-effort alignment]".)*

Elaborated in cooperation with **CLCCR and ACEA**.

### Standard body/trailer usable cargo volume methodology
Motivation: HDV CO2 is usually related to distance (gCO2/km) or mass-distance (gCO2/t-km); stakeholders also requested **volume** be considered (utility metric), enabling **gCO2/m³-km** reporting.

**Definition:** Usable Cargo Volume = L_INT × W_INT × H_INT (largest cubic volume that fits), based on outer dimensions of standard bodies/trailers per the HDV CO2 TA. Internal length/width fitted to discrete numbers of Euro pallets with a small margin. Real volume may differ depending on actual internal construction (footnote: a customer knowing their specific body/trailer volume can compute actual gCO2/m³-km by dividing VECTO's distance-based g/km result by the known volume).
- **"[Figure 34 description: diagram giving dimensions, cargo volume, and Euro-pallet count for each reference body (B1–B5).]"**
- **"[Figure 35 description: diagram giving dimensions, cargo volumes, and pallet counts for each reference (semi-)trailer (T1, T2, ST1).]"**

Dimensions reviewed by **Prof. Pflug representing CLCCR/VDA**.

**Alternative for vehicles with different chassis/bodywork length:** L_INT = L_EXT − front − rear (front/rear thickness from reference-body specs); L_EXT = (free chassis length) − (cabin-to-body distance) + (overhang). Cabin-to-body distance typically 50–80 mm (avoids cabin/bodywork chassis-flex collision); default rear overhang "probably... about 0m" for many vehicles. Real cargo-volume measurement is suggested as a future option, especially for multistage vehicles.

## 4.3.5.3 EMS Vehicle Configurations

Segmentation matrix includes gross combination mass **>40,000 kg** per the **European Modular System (EMS)** concept, permitted under **Directive 96/53/EC, Article 4 §4(b)**. Proposed EMS configurations: **gross combination mass 60,000 kg, max length 25.25 m**, configurable from groups 5, 9, 10, 11, 12. Actually permitted in **Sweden, Finland, Denmark, The Netherlands, Spain, and parts of Germany**.
- **"[Figure 36 description: diagram of EMS vehicle configurations as simulated in VECTO, using additional/different trailers including a 'dolly' for coupling a standard semitrailer to a group 9/11 rigid.]"**

EMS results computed only for **rated power ≥300 kW** (referring to specific motorisation ≥5 kW per tonne gross combination mass).

## 4.3.5.4 Vehicle Payloads

Source: ACEA White Book (representative payloads per vehicle group × mission profile) plus ref [6] data for refuse-vehicle typical payloads.

**Payload logic implemented in VECTO:**
- Typical loading factor for **long haul: 75%**.
- Typical loading factor for **other cycles (except municipal): 50%**.
- For **groups 1–3** (wide spread of max GVW within group): payload computed via **functions of max gross vehicle weight**.
- For **groups 4 and higher**: **fixed absolute payloads** per group and mission profile.
- For the **municipal cycle**: representative payloads per axle configuration as described in ref [6].

VECTO versions until early 2017 also simulated empty and fully-loaded vehicles; final decision: for **official CO2 declaration, VECTO simulates representative payload plus 10% payload**, allowing customers to interpolate/extrapolate for their use case (mass-dependency is "quite linear"). Reasons against simulating fully-loaded vehicles: extra input data burden (registered-vehicle specs, country-specific limit handling) and significantly increased per-vehicle computation time.

### Table 8 — VECTO payloads in tons (representative load / 10% load), by vehicle group and mission profile
| Group | Long haul (repr./10%) | Long haul EMS (repr./10%) | Regional delivery (repr./10%) | Regional delivery EMS (repr./10%) | Urban delivery (repr./10%) | Municipal utility (repr./10%) | Construction (repr./10%) |
|---|---|---|---|---|---|---|---|
| 1 | — | — | — | — | f50%/f10% | — | — |
| 2 | f10%+5.3 / f75%+0.7 | — | — | — | f50%/f10% | — | — |
| 3 | — | — | — | — | f50%/f10% | — | — |
| 4 | 14.0/1.9 | — | 4.4/0.9 | — | — | 3.0/0.6 | — |
| 5 | 19.3/2.6 | 26.5/3.5 | 12.9/2.6 | 17.5/3.5 | — | — | — |
| 9 | 19.3/2.6 | 26.5/3.5 | 7.1/1.4 | 17.5/3.5 | — | 6.0/1.2 | — |
| 10 | 19.3/2.6 | 26.5/3.5 | 12.9/2.6 | 17.5/3.5 | — | — | — |
| 11 | 19.3/2.6 | 26.5/3.5 | 7.1/1.4 | 17.5/3.5 | — | 6.0/1.2 | 7.1/1.4 |
| 12 | 19.3/2.6 | 26.5/3.5 | 12.9/2.6 | 17.5/3.5 | — | — | 12.9/2.6 |
| 16 | — | — | — | — | — | — | 12.9/2.6 |

*(Groups 1–3's "urban delivery" column values are functions f50%/f10% per Figure 37, not fixed numbers — reproduced as stated in the source.)*

**"[Figure 37 description: plot of the linear payload functions (for 10%, 50%, and 75% typical payload) vs. max gross vehicle weight, applicable to vehicle groups 1, 2, and 3.]"**

**VECTO payload reduction rules (caps):**
- If total rigid mass (corrected actual curb mass + standard body mass + payload, groups 1–3) exceeds GVWR → payload reduced to match GVWR.
- If total combination mass (rigid+trailer or tractor+semitrailer) exceeds **40 t (non-EMS)** or **60 t (EMS)** → payload reduced to match that cap.

## 4.3.5.5 Generic Data for the "Municipal Cycle" (Refuse Trucks)

Applies to vehicle groups **4, 9, 11**. Elaborated with **DIN-Normenausschuss Kommunale Technik (NKT)**. Components:
1. Driving cycle (section 4.3.5.1 above).
2. **Refuse body mass:**

| Vehicle group | Refuse body mass [kg] |
|---|---|
| 4 | 6,000 |
| 9 | 6,750 |
| 11 | 6,750 |

3. **PTO losses** considered from the technology "only the drive shaft of the PTO – shift claw, synchroniser, sliding gearwheel" (per Table 10 in Annex IX of the HDV CO2 TA), applied in the Municipal cycle **regardless of the vehicle's actual mounted PTO technology**.
4. Power-consumption data for the refuse body:
   a. **"[Figure 38 description: generic engine-speed and load pattern during PTO activation, at vehicle standstill during the garbage-collection phase.]"**
   b. **"[Figure 39 description: idling power-consumption curve of the hydraulic pump vs. engine speed during normal vehicle operation — relevant because the generic refuse truck is defined with no PTO declutch capability, so hydraulics losses persist even when inactive.]"**

**Rule of thumb (explicitly stated):** the refuse body's power consumption contributes **~45% of total fuel consumption in the collection part** and **~30% of total fuel consumption over the whole Municipal cycle.**

All other vehicle parameters (CdxA, rolling resistance) use the vehicle's own declared values for Municipal-cycle simulation.

## 4.3.5.6 Generic Data for the "Construction Cycle"

Construction trucks differ significantly from standard-box-body trucks in aerodynamics and superstructure/trailer mass. Since body/trailer-specific characteristics are not yet part of CO2 certification (see file 06, section 5.3.2), **generic body-mass and CdxA values for typical construction vehicles are used**; ACEA was elaborating typical values at project end. **Interim solution (final SR7 VECTO release 3.2.0.925):** uses the standard-body masses and fall-back CdxA values as interim generic construction-vehicle data, pending industry input. Relevant to **vehicle groups 11, 12, 16**, CO2-certified from **1 July 2020**.

## 4.3.5.7 Auxiliaries (Generic Auxiliary Power Data)

Auxiliary systems consume energy for non-propulsion functions. Two categories:
- **Implicitly covered by the engine fuel map** (not modelled separately): engine oil pump, coolant pump, fuel delivery pump, fuel high-pressure pump.
- **Modelled individually in VECTO:** engine cooling fan, alternator, air compressor, steering pump, A/C compressor. **PTO system losses are also treated like an auxiliary.**

For trucks, auxiliary influence on overall FC is "of secondary importance" — hence VECTO uses **simple methods**: constant power added to the ICE, from tables (by auxiliary technology × mission profile) or formulas (from specific vehicle specs). The complete set of tables/formulas is in **HDV CO2 TA Annex IX**.

## 4.3.5.8 VECTO Driver Strategy and Gear-Shift Strategy (Generic Parameterisation)

Elaborated from industry proposals (ACEA Whitebook, transmission-supplier proposals), adapted to VECTO's structure; fully documented in the VECTO User Manual.

**Known issues at end of SR7:**
- AMT shift strategy validated for long-haul and partly regional-delivery driving, but criticised for "poor fuel efficient shifting in low speed cycles (especially urban delivery and municipal cycle)"; ACEA investigating updates for autumn-2017 testing.
- AT truck model fine-tuned using Daimler data (two identical trucks, one AMT one AT, run simultaneously on a Municipal utility route and a regional route). Result: **VECTO 3.2 slightly favours AT over AMT in fuel-consumption ranking vs. measurement**, attributed mainly to inefficient AMT gear-shift strategy — recommendation: **re-validate AT gear-shift strategy once AMT strategy is updated**, to preserve correct AT-vs-AMT ranking.
- Bus AT gear-shift models still under development; a systematic bias exists between the two main bus-AT market competitors (see file 06, section 5.1.1).

## 4.3.5.9 Generic Data for Air Resistance Calculation

1. **Air density: 1.188 kg/m³** — corresponds to 12 °C ambient temperature, 1013 mbar sea-level pressure, converted to an average altitude of 200 m.
2. **Average wind conditions:** **3 m/s at 4 m height**, uniformly distributed from all directions [ref 9].
3. **Yaw-angle dependency of CdxA:** third-order polynomial CdxA(β) − CdxA(0) = a1·β + a2·β² + a3·β³ [note: source text shows "a3 β²" but this is presumably a typographical duplication in the OCR'd source — the polynomial is stated as "3rd order"], valid for 0–10° yaw, symmetric around 0°; coefficients from **ACEA White Book 2016**.

### Table 10 — Coefficients for yaw-angle dependency of air drag
| Vehicle type | a1 | a2 | a3 |
|---|---|---|---|
| Rigid solo | 0.013526 | 0.017746 | −0.000666 |
| Rigid trailer, EMS | 0.017125 | 0.072275 | −0.004148 |
| Tractor semitrailer | 0.030042 | 0.040817 | −0.002130 |
| Bus, coach | −0.000794 | 0.021090 | −0.001090 |

**"[Figure 40 description: plot of the resulting CdxA correction as a function of yaw/inflow angle, for each of the four vehicle-type curves in Table 10.]"**

Footnote: the CdxA value measured by VECTO Air Drag from the constant-speed test is itself corrected for cross-wind influence during testing (refers to zero yaw angle), via a method similar to the "average cross wind" method used inside VECTO's simulation. An accompanying MS Excel tool (distributed with VECTO) reproduces the cross-wind calculation algorithms.

## 4.3.5.10 Wheels (Generic Tyre/Wheel Data)

VECTO requires, per wheel/tyre size: rotational inertia data and data to calculate dynamic tyre radius. Because tyre-dimension codes are not all "self-explaining" (e.g., missing aspect ratio), VECTO's tyre-dimension input list is **limited to a fixed table** elaborated with ACEA from the Whitebook 2016 dimension list.

### Table 11 — Generic wheel data in VECTO (reproduced in full)
| Wheel dimension code | Cross-sectional width [mm] | Tyre aspect ratio [%] | Rim diameter [in] | Design overall diameter d [mm] | Inertia | F [-] |
|---|---|---|---|---|---|---|
| 9.00 R20 | 258 | 0.95 | 20 | 1018 | 10.5 | 3.05 |
| 9 R22.5 | 230 | 0.95 | 22.5 | 970 | 8.9 | 3.05 |
| 9.5 R17.5 | 240 | 0.95 | 17.5 | 842 | 4.9 | 3.05 |
| 10 R17.5 | 254 | 0.95 | 17.5 | 858 | 5 | 3.05 |
| 10 R22.5 | 254 | 0.95 | 22.5 | 1020 | 11 | 3.05 |
| 10.00 R20 | 275 | 0.95 | 20 | 1052 | 13.1 | 3.05 |
| 11 R22.5 | 279 | 0.95 | 22.5 | 1050 | 14.4 | 3.05 |
| 11.00 R20 | 286 | 0.95 | 20 | 1082 | 14.6 | 3.05 |
| 11.00 R22.5 | 279 | 0.95 | 22.5 | 1050 | 16 | 3.05 |
| 12 R22.5 | 300 | 0.95 | 22.5 | 1084 | 16.85 | 3.05 |
| 12.00 R20 | 313 | 0.95 | 20 | 1122 | 19.5 | 3.05 |
| 12.00 R24 | 313 | 0.95 | 24 | 1226 | 27.7 | 3.05 |
| 12.5 R20 | 317.5 | 0.95 | 20 | 1120 | 12.7 | 3.05 |
| 13 R22.5 | 320 | 0.95 | 22.5 | 1124 | 20 | 3.05 |
| 14.00 R20 | 370 | 0.95 | 20 | 1238 | 30.8 | 3.05 |
| 14.5 R20 | 368.3 | 0.95 | 20 | 1092 | 14.8 | 3.05 |
| 16.00 R20 | 406.4 | 0.95 | 20 | 1343 | 47.5 | 3.05 |
| 205/75 R17.5 | 205 | 0.75 | 17.5 | 753 | 3.5 | 3.05 |
| 215/75 R17.5 | 212 | 0.75 | 17.5 | 767 | 3.9 | 3.05 |
| 225/70 R17.5 | 226 | 0.70 | 17.5 | 761 | 4 | 3.05 |
| 225/75 R17.5 | 226 | 0.75 | 17.5 | 783 | 4 | 3.05 |
| 235/75 R17.5 | 233 | 0.75 | 17.5 | 797 | 4.5 | 3.05 |
| 245/70 R17.5 | 248 | 0.70 | 17.5 | 789 | 5.2 | 3.05 |
| 245/70 R19.5 | 248 | 0.70 | 19.5 | 839 | 6 | 3.05 |
| 255/70 R22.5 | 255 | 0.70 | 22.5 | 930 | 9.5 | 3.05 |
| 265/70 R17.5 | 262 | 0.70 | 17.5 | 817 | 5.6 | 3.05 |
| 265/70 R19.5 | 262 | 0.70 | 19.5 | 867 | 6.5 | 3.05 |
| 275/70 R22.5 | 276 | 0.70 | 22.5 | 958 | 11.9 | 3.05 |
| 275/80 R22.5 | 276 | 0.80 | 22.5 | 1012 | 12.8 | 3.05 |
| 285/60 R22.5 | 285 | 0.60 | 22.5 | 914 | 10.6 | 3.03 |
| 285/70 R19.5 | 283 | 0.70 | 19.5 | 895 | 7.9 | 3.05 |
| 295/55 R22.5 | 292 | 0.55 | 22.5 | 896 | 10.2 | 3.03 |
| 295/60 R22.5 | 292 | 0.60 | 22.5 | 926 | 10.8 | 3.03 |
| 295/80 R22.5 | 298 | 0.80 | 22.5 | 1044 | 15.5 | 3.05 |
| 305/60 R22.5 | 306 | 0.60 | 22.5 | 938 | 11.4 | 3.03 |
| 305/70 R19.5 | 305 | 0.70 | 19.5 | 923 | 9.2 | 3.05 |
| 305/70 R22.5 | 305 | 0.70 | 22.5 | 1000 | 13.9 | 3.05 |
| 305/75 R24.5 | 305 | 0.75 | 24.5 | 1080 | 21.2 | 3.05 |
| 315/45 R22.5 | 307 | 0.45 | 22.5 | 856 | 9.9 | 3.03 |
| 315/60 R22.5 | 313 | 0.60 | 22.5 | 950 | 12.8 | 3.03 |
| 315/70 R22.5 | 312 | 0.70 | 22.5 | 1014 | 14.9 | 3.05 |
| 315/80 R22.5 | 312 | 0.80 | 22.5 | 1076 | 17.6 | 3.05 |
| 325/95 R24 | 325 | 0.95 | 24 | 1228 | 27.6 | 3.05 |
| 335/80 R20 | 340 | 0.80 | 20 | 1044 | 13.5 | 3.05 |
| 355/50 R22.5 | 361 | 0.50 | 22.5 | 928 | 12.2 | 3.03 |
| 365/70 R22.5 | 375 | 0.70 | 22.5 | 1084 | 18.6 | 3.05 |
| 365/80 R20 | 360 | 0.80 | 20 | 1092 | 17.2 | 3.05 |
| 365/85 R20 | 364 | 0.85 | 20 | 1128 | 22.5 | 3.05 |
| 375/45 R22.5 | 372 | 0.45 | 22.5 | 910 | 11.2 | 3.03 |
| 375/50 R22.5 | 374 | 0.50 | 22.5 | 948 | 13 | 3.03 |
| 375/90 R22.5 | 369 | 0.90 | 22.5 | 1248 | 33.8 | 3.05 |
| 385/55 R22.5 | 386 | 0.55 | 22.5 | 996 | 15.9 | 3.03 |
| 385/65 R22.5 | 389 | 0.65 | 22.5 | 1072 | 19.2 | 3.03 |
| 395/85 R20 | 386 | 0.85 | 20 | 1180 | 27.9 | 3.05 |
| 425/65 R22.5 | 430 | 0.65 | 22.5 | 1124 | 22.5 | 3.03 |
| 495/45 R22.5 | 500 | 0.45 | 22.5 | 1018 | 20.7 | 3.03 |
| 525/65 R20.5 | 530 | 0.65 | 20.5 | 1203 | 35 | 3.03 |

**Dynamic tyre radius formula:** r_dyn = (1 / (2·π)) · F · d, where F = the "Inertia F" factor from Table 11 and d = design overall diameter from Table 11. *(Note: the source labels this column "Inertia F [-]" and reuses it directly in the radius formula — reproduced verbatim; this dual use of "F" for both an inertia-related factor and the radius-formula factor is exactly as it appears in the source text.)*

Tyre industry noted some future dimensions are not yet covered — **recommendation to update the table regularly**; since valid VECTO wheel-dimension-code entries are also listed in the HDV CO2 TA, updates require a **legislative text update** too.

## 4.3.5.11 Fuel Properties

VECTO engine input is on a **mass-flow basis (g/h)**; converting to volumetric (l/h), energy (MJ/h), and CO2 (g/h) requires fuel **density, CO2 content (g CO2 per g fuel), and LHV (Lower Heating Value)** for each of the **six "Engine Fuel Types"** defined in the HDV CO2 technical annex. Main source: **JEC (JRC, EUCAR, CONCAWE) Tank-to-Wheels report v4.0** [ref 10]. ED95 CO2 factor calculated by TUG from Scania-provided fuel composition.

### Table 12 — VECTO fuel properties (reproduced in full)
| Engine Fuel Type | Reference Fuel | Density [kg/m³] | CO2 content [g_CO2/g_Fuel] | LHV [MJ/kg] | Data Source |
|---|---|---|---|---|---|
| Diesel / CI | B7 | 836 | 3.13 | 42.7 | [10] |
| Ethanol / CI | ED95 | 820 | 1.83 | 25.7 | Scania (composition, density, LHV); IVT calculations for CO2 content |
| Petrol / PI | E10 | 750 | 3.04 | 41.5 | [10] |
| Ethanol / PI | E85 | 786 | 2.09 | 29.1 | [10], corrected for LHV as specified in the HDV CO2 TA |
| LPG / PI | LPG Fuel B | not required | 3.02 | 46.0 | [10] |
| NG / PI | G25 (test fuel, representing typical CNG real-world fuel) | not required | 2.54 | 45.1 | [10] |

*(Type definitions per HDV CO2 TA Annex V. "Not required" reflects the footnote that LPG/NG results are mass-flow based, not volumetric, in VECTO output.)*

**Important open issue flagged at end of SR7:** industry claimed VECTO's LNG results show **unrealistically high mass-based fuel consumption and CO2**, because market LNG fuel composition differs significantly from the CNG specification VECTO applies to all NG-fuelled vehicles. **Recommendation: investigate further; consider separate CNG vs. LNG engine fuel types.**

**★ Directly relevant caveat for electrification work:** "Currently VECTO considers only Tank to Wheel emissions (TTW). Neglecting the Well to Tank (WTT) chain does not correctly rank the real GHG impact of different propulsion technologies (**different fuels or electricity from the grid if PHEVs and EVs might be covered by VECTO in future**)." This is the report's only direct textual acknowledgement that VECTO's TTW-only scope would misrank EVs/PHEVs against ICE vehicles without a WTT (grid-electricity-generation) accounting layer — a first-order consideration for any HDEV energy/CO2 sizing tool aiming for "PVsyst for EVs"-level credibility.

## 4.3.5.12 Weighting of WHTC Correction Factors

WHTC correction factors (WCF_urban, WCF_road, WCF_motorway) are computed by VECTO Engine as: measured hot-WHTC fuel consumption (per sub-phase) ÷ steady-state-fuel-map-interpolated value at the corresponding engine speed/torque points. When VECTO simulates a full mission-profile cycle, the three factors are combined via:

```
WCF_Tot-i = WCF_Urb × WF_Urb-i + WCF_Rur × WF_Rur-i + WCF_MW × WF_MW-i
```

### Table 13 — Weighting factors for WHTC category correction factors (final values from HDH GTR work)
| Index | Mission profile | WF Motorway | WF Road | WF Urban |
|---|---|---|---|---|
| 1 | Long haul | 89% | 0% | 11% |
| 2 | Regional delivery | 53% | 30% | 17% |
| 3 | Urban delivery | 4% | 27% | 69% |
| 4 | Municipal utility | 2% | 0% | 98% |
| 5 | Construction | 6% | 32% | 62% |
| 6 | Citybus | 0% | 0% | 100% |
| 7 | Interurban bus | 19% | 36% | 45% |
| 8 | Coach | 78% | 22% | 0% |

This weighting approach and its derivation is documented in a separate reference on the **Heavy Duty Hybrid (HDH) HILS test procedure** [ref 11].

## Standards, organisations, and legal references in this chapter (exact names only)
- HDV CO2 TA (Annexes III, V, IX referenced specifically)
- DIN SPEC 30752-1
- DIN-Normenausschuss Kommunale Technik (NKT), Germany
- Directive 96/53/EC, Article 4 §4(b) (EMS vehicle combinations)
- ACEA White Book / Whitebook 2016
- JEC (JRC, EUCAR, CONCAWE) Tank-to-Wheels Report v4.0
- ECE R49 (six reference engine fuel types)
- CLCCR, VDA (Prof. Pflug)
- HDH (Heavy Duty Hybrid) GTR / UNECE-GRPE HDH Working Group HILS test-procedure report
