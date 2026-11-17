# SR7/LOT4 Final Report — Chapter 5: Application of VECTO to HDV Groups Not Covered by the Actual HDV CO2 Legislation

> Part of the multi-file extraction of `sr7_lot4_final_report_en.pdf` (Service contract CLIMA.C.2/SER/2012/0004, EC DG CLIMA, report dated 30.10.2017). See `sr7-lot4-01-overview-and-metadata.md` for full document metadata and companion-file list.
>
> **Relevance to HDEV sizing/modelling:** The M2/N2 (light/intermediate truck) cycle-representativeness analysis and the bus/coach AT-technology-ranking discussion are directly relevant if the HDEV tool needs to cover smaller electric trucks, electric buses, or if it needs a defensible method for choosing/validating representative duty cycles for a given vehicle segment.

At the end of SR7, VECTO does **not (fully) cover**:
i. Buses and coaches (M3 vehicles)
ii. Intermediate-size vehicles (3.51–7.49 t GVWR), both goods (N2) and persons (M2)
iii. All-wheel-drive trucks: groups 6,7,8 (4x4), 13,14 (6x6), 15,17 (8x2,8x6,8x8)
iv. Trucks with more than 4 axles
Additionally: **all VECTO-certified vehicles use standard bodies/(semi-)trailers**, leaving a "significant potential for CO2 reduction uncovered" (addressed in 5.3.2 below).

## 5.1 Buses and Coaches (M3 vehicles)

### 5.1.1 VECTO AT model development
**AT transmissions with torque converter dominate the city-bus market (>90% market share)** and are important for interurban buses too. Two AT design types:
- **AT-S ("serial")** — makes **ZF and Allison**
- **AT-P ("power-split")** — make **VOITH**

Most bus OEMs offer both designs; a major CO2-certification challenge is providing a **realistic ranking** between technologies across the bus fleet and VECTO CO2 cycles.

**SR7 work on the AT model:**
- Transferred the VECTO 2.2 AT approach into the refactored VECTO 3.
- Revised the torque-converter operating-point search algorithm from a "partly instable iterative method" (VECTO 2.2) to an **analytical algorithm** (VECTO 3).
- Extended the transmission-loss model to consider **clutch losses during AT power shifts** — identified as necessary for realistic AT-S vs. AT-P ranking; a simple algorithm was developed and agreed with industry in **spring 2017**.
- Extended AT gear-shift algorithms with additional parameters for closer real-world-shift fidelity.
- **Model validation (2016, ACEA data):** measurements on city buses with VOITH and ZF transmissions (mainly SORT-cycle-derived) simulated two ways:
  a. Providing measured gear information as VECTO input → **VECTO simulates FC for both transmission designs very well.**
  b. Only providing speed/gradient, letting VECTO's own AT gear-shift model decide → **a systematic bias favouring AT-S transmissions by a few percent in fuel consumption** appears, because the same generic gear-shift parameters were assumed for both AT concepts.
- **Conclusion:** the "physical" AT model itself is sufficiently capable; the **gear-shift model** is the source of bias. Further development is deferred to ACEA's 2017 pre-pilot-phase data collection and further OEM discussion (see 5.1.5).

### 5.1.2 Ricardo AAUX module implementation
The **Advanced Auxiliary sub-model (AAUX)** for buses/coaches, from the Ricardo SR3 project [ref 13], was transferred from VECTO 2 into **VECTO 3.1**, with bug fixes; guidelines for running/interpreting the AAUX model were elaborated and distributed for the **2017 pre-pilot phase**.

**Key caveat (hybrid relevance):** the approach for "smart auxiliaries" (brake-energy recuperation via alternators and/or pneumatic system) **may work for mild hybrids**, contingent on how future CO2 certification treats different hybrid architectures. **For full hybrids, the AAUX approach may not give reasonable results (risk of double-counting energy-saving potential)** if HEV simulation is also active in VECTO — detailed further in a parallel project [ref 12: Silberholz & Hausberger, "Feasibility assessment regarding the development of VECTO for hybrid heavy-duty vehicles," draft final report for service contract CLIMA.C.4/ETU/2016/0005LV, Graz, 6.7.2017].

Since the Ricardo input-data structure is "too complicated for a certification process," further simplification work is needed before bus CO2 certification can be introduced.

### 5.1.3 Bus and Coach workshop
A workshop was held **12 September 2016, Brussels**, primarily to inform non-ACEA bus OEMs (not previously engaged) about the B&C CO2 certification procedure; prepared/presented by TUG.

### 5.1.4 Baseline documents for the B&C Pre-Pilot Phase (PPP)
Because B&C methods were judged "not mature enough" for a full pilot phase (as run for trucks in 2015), a **"Pre-Pilot Phase" (PPP)** was organised (mainly via ACEA TF5 and DG JRC). PPP objectives:
1. Further validation of component-test-procedure descriptions (e.g., B&C air-drag testing may raise issues distinct from trucks).
2. Producing measurement data for VECTO development (esp. gear-shift-model parameterisation from real driving).
3. Proof-of-concept: VECTO simulation vs. measured fuel consumption.
4. Testing options for the B&C Ex-Post Validation test.

PPP planning documents (task descriptions, proposed test vehicles/measurements) and a detailed "how to use VECTO in the PPP" guide were produced (this guide is the basis for **Annex II** of this report, which is image-based/not text-extractable — see file 07). PPP measurements were performed by industry and DG JRC in **first half of 2017** and were under analysis at report time.

### 5.1.5 Open topics for B&C implementation into HDV CO2 legislation
i. **Generic data handling:** ACEA revising the B&C segmentation approach from a simple WB-2016 matrix to a "vehicle group" system aligned with the truck approach (cycle allocations, payloads, auxiliary data); draft table presented at the **2nd B&C meeting, June 2017**; finalisation targeted "until the end of this year" [2017]; to be reviewed by CLCCR; recommended for further Commission-consultant review before software/legislative implementation.
ii. **Finalisation of the AT gear-shift model:** two identified paths — (a) elaborate distinct shift-polygon/parameter settings for AT-S vs. AT-P; or (b) further extend the shared model with additional parameters for both types. Either path ideally needs a technical explanation of the inter-design difference, or at least industry agreement to use measurement-fitted settings.
iii. **AMT gear-shift model review for B&C** — activities launched by ACEA in **summer 2017**, covering trucks and B&C in parallel.
iv. **Minor Ricardo AAUX module issues** (raised in an "ACEA sideletter" plus ongoing B&C-segmentation-matrix-revision analysis) — notably, the Ricardo code requires certain data (e.g., vehicle length) to be entered multiple times; input-data handling recommended for "clean up."
v. **API link of VECTO B&C to OEM databases:** already established for trucks; B&C will need additional resources because (a) the large AAUX input-data set is not yet linked to the VECTO API, and (b) the bus-OEM landscape (far more companies, many smaller than truck OEMs) may need a different IT solution.
vi. **Legislative text elaboration** covering the bus segmentation table, an air-drag family concept (different from trucks), and AAUX parameterisation provisions (incl. an optional regenerative-electric-system test procedure as proposed by ACEA).
vii. **Organisation of a main Pilot Phase for B&C**, focused on "playing certification" (simulating certification per the draft legislative text, involving technical services/approval authorities) and on engaging additional bus manufacturers not yet actively participating.

## 5.2 Intermediate-Size Vehicles (M2 and N2, GVWR 3.5–7.49 t)

### Regulatory gap
- N2/M2 **above 7.5t GVWR**: VECTO groups defined, applicable in future.
- LCVs **below 3.5t GVWR**: WLTP light-duty test procedure applies (from September 2017).
- N2/M2 **between 3.51–7.49 t**: **not allocated to either procedure.**

An expert group (open to all interested parties; Commission, TUG, ACEA regularly participating) met: kick-off **29.10.2015, Brussels**; WebEx meetings **22.03.2016, 30.05.2016, 20.06.2016, 16.09.2016**.

### Classification issue
- WLTP applies up to **2.84 tonnes** vehicle empty (reference) mass.
- HD engine test procedure (WHTC, WHSC, PEMS) applies from **2.61 tonnes** empty mass upward.
- **A large share of N2 falls into an overlap zone** where the OEM can choose the applicable regulation (influenced by customer specification, e.g., multistage-vehicle final body weight).
- **Rough shares (from expert-group discussion):** Daimler and IVECO — roughly half of N2/M2 vehicles are below 7 tons (e.g., Daily [lower-weight N2] and Eurocargo [higher-weight N2]); ~50% of these vehicles are registered under LDV emission regulation. **VW:** almost all N2/M2 tested under LDV regulation. **MAN:** all trucks tested under HDE regulation (MAN's N2 typically has 7.49 t GVW).
- "[Figure 46 description: photograph of an example light truck with 5.50 t GVWR, illustrating the typical vehicle segment under discussion.]"

### Technical applicability
- **No technical restriction identified** against using VECTO for N2/M2 above 3.5 t.
- WLTP chassis-dyno test beds are **limited in vehicle weight**, clearly below 7.5 tonnes for typical bed designs.
- **Simplest proposed split:** use WLTP for vehicles type-approved under WLTP; use VECTO for N2/M2 already engine-type-approved under WHTC/WHSC (since that's already a core VECTO engine-data-certification element).

### Test-cycle representativeness — two proposed options
a) Certify VECTO-route N2/M2 using the **WLTC** as the VECTO test cycle (for compatibility with WLTP-certified peers) — but this requires aligning VECTO-WLTC results with actual WLTP chassis-dyno results (road-load determination differences, mimicking chassis-dyno conditions in VECTO, auxiliary power alignment) — assessed as "quite challenging," with risk that mis-alignment creates a competitive disadvantage for one certification path.
b) Give VECTO-route N2/M2 a **separate, representativeness-oriented cycle** — saves development effort but produces **non-comparable results** between WLTP g/km and VECTO g/t-km reporting, again with possible competitive-disadvantage risk.

**Finding: WLTC is not representative for LCVs in the N2 range** (see 5.2.2 below). Options floated:
- Use VECTO for all N2/M2 **above ~5.5t GVWR** (no WLTP overlap there).
- For smaller N2/M2, discuss and choose among: exclude sub-5.5t from CO2 certification; allow both WLTP and VECTO with clear customer-facing labelling; or require VECTO for all N2/M2 regardless of WLTP pollutant certification (adds cost).

### 5.2.1 Vehicle models / current certification options overview

### Table 27 — Typical N2 truck GVWR ranges by make/model (min–max, t), by body type
| Make | Model | Van (min–max) | Flatbed/Tipper (min–max) | Chassis (min–max) |
|---|---|---|---|---|
| DAF | LF | — | — | 7.49 |
| Iveco | Fiat Ducato | 2.60–4.00 | 3.00–4.00 | 3.00–4.30 |
| Ford | Transit | 2.90–4.70 | 3.10–4.70 | — |
| Fuso | Canter | — | — | 3.50–7.49 |
| Isuzu | N55 | — | — | 5.50 (max GVWR >5.50t noted) |
| Iveco | Daily | 3.30–7.00 | 3.30–7.20 | — |
| Iveco | Eurocargo | — | — | 7.49 |
| MAN | TGL | — | — | — |
| M B | Atego | — | 6.50–7.49 | — |
| M B | Sprinter | 3.00–5.50 | 3.19–5.50 | 3.19–5.50 |
| Renault | Opel Movano | 2.80–4.50 | 3.50–4.50 | 3.50–4.50 |
| Renault | D6.5 | — | — | 7.00 |
| Renault | Master | 2.80–4.50 | 3.50–4.50 | — |
| Renault | Maxity | — | 3.50–4.50 | — |
| VW (MAN) | Crafter (TGE) | 3.00–5.50 | 3.00–5.50 | 3.00–5.50 |

*(Source table layout was dense/column-ambiguous in places after extraction; reproduced with best-effort make/model/body-type mapping — "[unclear from source: some minor cell-to-model alignments in the original Table 27 could not be perfectly reconstructed from the text extraction, though all cited GVWR ranges and the overall conclusion below are verbatim]".)*

**Key conclusion:** only the **Fuso Canter** and **Iveco Daily** are available both below and above 5.50 t GVWR — suggesting **~5.5t as a natural subdivision threshold** if the 3.5–7.5t segment needs splitting. N2/M2 up to 5.50t are usually derived from the N1/M1 (light-duty) platform; N2/M2 from 5.50t up are usually derived down from the N3/M3 (heavy-duty) platform.

### 5.2.2 Cycle-representativeness analysis

A VECTO model of a **typical light truck** (based on an MB Sprinter) was built (Table 28, Figure 47 — model parameters and a full-load/drag/fuel-map chart; full numeric column headers in the source table were partly ambiguous after extraction, but key modelled values include: GVWR ~5,000 kg [C1-tyre RRC bin], vehicle width/height and CdxA per NEDC/WLTC test configurations, final-drive ratio 4.727, 6-speed manual transmission, mechanical efficiency ~0.96 [final drive & indirect gears] / 0.98 [direct gears], dynamic tyre radius 0.339 m for 195/75R16 driven wheels, wheel-set inertia 1.5 kg·m² [x6 wheels], equivalent wheel mass 131 kg, engine+clutch inertia 1.5 kg·m², average auxiliary mechanical power (chassis-dyno conditions) 1.75 kW).

**Cycles analysed:**
a) Real-world in-use N2 cycles (only 4 found in the entire WLTP database).
b) "LDV-dyno": NEDC, WLTC (for N1).
c) "HDV-dyno": JE05, NERV, WHVC (for N3).
d) VECTO CO2 cycles for N3.

### Table 29 — Driving dynamics of analysed cycles (selected columns)
| Cycle | Payload (%/t) | Duration [s] | Distance [km] | v_avg [km/h] | v_roll,avg [km/h] | Stops/km | Stand [% time] | RPA [m/s²] | ã [m/s²] |
|---|---|---|---|---|---|---|---|---|---|
| Real World 1 | variable | 28,908 | 330.7 | 41.2 | 46.5 | 0.57 | 11.4 | 0.098 | 0.102 |
| Real World 2 | variable | 28,572 | 235.8 | 29.7 | 40.5 | 0.91 | 26.7 | 0.109 | 0.114 |
| Real World 3 | variable | 299,913 | 3,759.8 | 45.1 | 49.7 | 0.39 | 9.2 | 0.120 | 0.124 |
| Real World 4 | variable | 1,484,645 | 29,623.9 | 71.8 | 77.6 | 0.14 | 7.4 | — | — |
| NEDC, 88 km/h | 0 | 1,180 | 10.5 | 31.9 | 42.5 | 1.24 | 24.8 | 0.089 | 0.093 |
| WLTC 3b, 88 km/h | 28% | 1,801 | 21.6 | 43.1 | 49.6 | 0.37 | 13.0 | 0.127 | 0.132 |
| JE05 | n.def. | 1,830 | 13.9 | 27.3 | 36.5 | 1.01 | 25.2 | 0.116 | 0.121 |
| NERV 20+60 | n.def. | 1,809 | 20.1 | 40.0 | 45.6 | 0.70 | 12.3 | 0.121 | 0.125 |
| WHVC | n.def. | 1,800 | 20.1 | 40.1 | 46.5 | 0.60 | 13.6 | 0.101 | 0.104 |
| Long Haul '15 (VECTO) | 28% | 4,546 | 100.2 | 79.3 | 80.5 | 0.03 | 1.4 | 0.012 | 0.053 |
| Reg. Delivery '12 (VECTO) | 28% | 1,581 | 25.8 | 58.8 | 63.3 | 0.19 | 7.0 | 0.045 | 0.111 |
| Reg. Delivery '16 (VECTO) | 28% | 5,934 | 100.0 | 60.7 | 69.0 | 0.10 | 12.1 | 0.035 | 0.084 |
| Urb. Delivery '12 (VECTO) | 28% | 3,267 | 27.8 | 30.6 | 37.9 | 0.94 | 19.3 | 0.095 | 0.148 |

*(RPA = Relative Positive Acceleration [Weijer 1997]; ã = characteristic acceleration incl. altitude change [O'Keefe 2007, doi 10.4271/2007-01-0302]; real-world cycles simulated without road gradient, so ã there reflects velocity-course dynamics only; acceleration values between −0.05 and +0.05 m/s² excluded from RPA/ã for real-world cycles to remove measurement-noise artefacts.)*

**Real World cycles 1–3 characteristic ranges:** average velocity 30–45 km/h; average rolling velocity 40–50 km/h; 0.4–0.9 stops/km; 9–27% time standing; RPA ~0.1–0.12; ã ~0.10–0.12 m/s². Real World 4 is closer to long-haul than delivery traffic.

**Key findings:**
- **NEDC:** lowest velocity range, very low dynamics (RPA, ã) even for vans.
- **WLTC:** better velocity match, but "rather too transient" — increases high-load engine-operation share (see below).
- **HDV chassis-dyno cycles fit real-world dynamics better**, though JE05 is "too slow"; NERV 20+60 is at the upper end of dynamics; WHVC "matches quite well, but lacks a bit of dynamics."
- **VECTO Long Haul** unsuited to most light trucks (real-world N2 data shows delivery-traffic-dominated usage).
- A **combination of VECTO Regional Delivery ('16) + Urban Delivery ('12)** would better match real-world N2 dynamics.
- Target-acceleration curve used in these simulations: HDV curve for GVWR ≥7.50t (desired accel. +1.0 m/s² from 0–25 km/h, decreasing to +0.5 m/s² at ≥60 km/h) — noted as adjustable if a dedicated N2 mission profile is developed later. No real-world M2 (bus-type light) driving data was found.

**"[Figure 48 description: eight small multiples plotting simulated fuel consumption (L/100km) vs. payload (0–2.5 t) for the N2 VECTO vehicle model across Real World cycles 1–4, VECTO Long Haul 2015, Regional Delivery 2016/2012, and Urban Delivery 2012, plus a table-style inset giving single-payload-point results for NEDC/WLTC/JE05/NERV/WHVC. Key values shown at default WLTC 28% payload: Real World 1 = 8.9, Real World 2 = 9.5, Real World 3 = 9.2, Real World 4 = 8.8, Long Haul 2015 = 7.2, Reg. Delivery 2016 = 7.6, Reg. Delivery 2012 = 7.5, Urb. Delivery 2012 = 9.9 L/100km; NEDC (0% payload) = 8.3, WLTC 3b (28%) = 8.8, JE05 = 9.6, NERV 20+60 = 8.5, WHVC = 8.5 L/100km. The steeper FC-vs-payload slope for more transient cycles reflects that more brake energy is dissipated at higher mass, while air-drag/auxiliary energy is mass-independent.]"**

**Summary of FC results at 28% payload (default WLTC payload basis; NEDC uses its own 100 kg reference-mass payload):**
- Real World cycles: **8.8–9.5 L/100km** (lowest on the motorway-like Real World 4).
- LDV cycles (both capped at 88 km/h): NEDC (no payload) 8.3, WLTC 3b (28% payload) 8.8 L/100km — similar.
- HDV cycles: **8.5–9.6 L/100km** spread, highest on the slow JE05 (most engine idling at stop).
- VECTO cycles: **7.2–9.9 L/100km**, highest on Urban Delivery.

**"[Figure 49 description: engine-map bubble charts (power vs. engine speed) showing share of overall fuel consumption per operating-point cluster, for Real World cycles 1–4 and the LDV dyno cycles (NEDC, WLTC), payload 0% for NEDC / 28% for others — bubble area proportional to FC share.]"**

Findings: Real World 1–3 concentrate FC in the **lower halves** of the power/speed ranges, with low full-load share and fairly even distribution; Real World 4 (motorway-like) shifts to higher power/speed. **NEDC** matches only the lower-power-range level but at slightly too-high engine speed, and — due to the artificial constant-acceleration profile — its FC clusters onto discrete map nodes rather than being distributed. **WLTC** better matches the real-world speed range but shows a **much higher full-load share** than real-world data — attributed to the WLTC's underlying database being mainly N1 (car-derived-van) real-world cycles, where higher power-to-mass ratios drive higher accelerations than typical N2 vehicles exhibit; the WLTC's sustained 88 km/h motorway segment also over-weights that single high-load operating point.

**"[Figure 50 description: analogous engine-map bubble charts for the HDV dyno cycles (JE05, NERV, WHVC) and the VECTO cycles (Long Haul, Regional Delivery, Urban Delivery), all at 28% payload.]"**

Findings: JE05/NERV/WHVC **match the real-world load distribution well** (main operating area and FC distribution), except WHVC shows an FC accumulation on its motorway part not seen in real-world data. **VECTO Long Haul is unsuited to light trucks** (FC concentrated at the few 85 km/h motorway operating points). **VECTO Regional Delivery (2016)** is also limited — its motorway share accounts for **63% of total cycle fuel consumption** (footnote: the 2012 version's motorway share is also high, 57%, but its FC is more evenly distributed across the map than the 2016 version's).

**Overall conclusion:** WLTC is not representative of N2 real-world load distributions; HDV test cycles fit much better; VECTO Long Haul and Regional Delivery are not representative of smaller N2/M2 (too much motorway-driving weight); a **weighted result from VECTO Regional Delivery + Urban Delivery** fits the available real-world N2 data well.

### 5.2.3 Outlook / prerequisites for future N2/M2 CO2 certification
- Decide whether one procedure covers the full 3.51–7.49t GVWR range, or whether a further split is needed (e.g., N2a/M2a 3.51–5.50t vs. N2b/M2b 5.51–7.49t).
- Decide chassis-dyno-based vs. VECTO-simulation-based certification.
- **A possible solution:** VECTO-based CO2 certification for all N2 above ~5.50t GVWR.
- For smaller N2 currently type-approved on chassis dyno, adding VECTO would be extra burden; for those on the engine test bed, adding chassis-dyno testing would add cost — **"no preference seems to exist"**; a political decision is needed.
- Appropriate driving cycles: a mix of existing VECTO urban + regional delivery cycles already matches real-world N2 well; for chassis-dyno testing, WLTP is fixed for chassis-dyno-approved N2, but **WLTC is not very representative** — whether to introduce an additional chassis-dyno CO2 cycle needs discussion.
- All VECTO generic datasets may need N2/M2-specific adjustment (acceleration curve and payloads already tested in this work; standard bodies and auxiliary power demand values still need definition).
- The **number of OEMs in the N2/M2 market is much higher than in N3** — after data adjustments, manufacturer iteration loops would be needed, potentially leading to a coordinated pilot phase as done for N3/M3 — "expected to be the most time consuming" step, but "necessary to reach general understanding and acceptance of the new method."

## 5.3 Further HDV Groups Not Considered Yet

Planned CO2-certified vehicle groups cover **~98% of European HDV CO2 emissions** (per LOT1/LOT2 report data, assumed still broadly representative — explicit assumption stated: "We do not assume that the truck market has changed a lot in the last years").

**"[Figure 51 description: bar or pie chart showing the share of each VECTO truck group in total EU HDV CO2 emissions, compiled from LOT1/LOT2 data; groups shown in brackets are those not (yet) foreseen for CO2 certification.]"**

**Legislative roll-out steps and cumulative CO2 coverage:**
- **Step 1 (1 Jan 2019),** groups 4, 5, 9, 10: **~71%**
- **Step 2 (1 Jan 2020),** groups 1, 2, 3: **~8%**
- **Step 3 (1 Jul 2020),** groups 11, 12, 16: **~9%**
- **Step 4 (open, undated at report time),** buses and coaches: **~10%**

### Table 30 — Share of VECTO truck groups and mission profiles in EU HDV CO2 emissions (compiled from ref [4]; bracketed groups not yet CO2-certified)
| Category | Group | Urban Delivery | Municipal | Regional Delivery | Long Haul | Construction | City Class I | Interurb. Class II | Coach Class III | Sum |
|---|---|---|---|---|---|---|---|---|---|---|
| Truck 4x2, 2 axles: Rigid+(Tractor) 7.5–10t | 1 | 0.5% | — | 0.2% | 0.7% | 1.1% | — | — | — | 2.6% |
| Rigid+(Tractor) >10–12t | 2 | 0.5% | — | 0.2% | 0.7% | 1.1% | — | — | — | 2.6% |
| Rigid+(Tractor) >12–16t | 3 | 0.5% | — | 0.2% | 0.7% | 1.1% | — | — | — | 2.6% |
| Rigid >16t | 4 | 0.8% | — | 0.5% | 1.2% | 5.3% | — | — | — | 7.7% |
| Tractor >16t | 5 | — | — | 10.5% | 33.8% | 4.5% | — | — | — | 48.8% |
| Rigid 7.5–16t (4x4) | (6) | — | — | — | — | 0.0% | — | — | — | 0.2%/0.3%* |
| Rigid >16t (4x4) | (7) | — | — | — | — | 0.0% | — | — | — | 0.4% |
| Tractor >16t (4x4) | (8) | — | — | — | — | 0.3% | — | — | — | 0.3% |
| Truck 6x2/2-4, 3 axles: Rigid all weights | 9 | 1.2% | 1.0% | — | 4.2% | — | — | — | — | 6.4% |
| Tractor all weights | 10 | — | — | 8.2% | — | — | — | — | — | 8.2% |
| 6x4 Rigid all weights | 11 | 1.4% | — | — | 2.5% | — | — | — | — | 3.9% |
| 6x4 Tractor all weights | 12 | — | — | 1.0% | — | 0.3% | — | — | — | 1.3% |
| 6x6 Rigid all weights | (13) | — | — | — | — | 0.6% | — | — | — | 0.6% |
| 6x6 Tractor all weights | (14) | — | — | — | — | 0.1% | — | — | — | 0.1% |
| Truck 8x2, 4 axles: Rigid all weights | (15) | 0.0% | — | — | — | 0.2% | — | — | — | 0.2% |
| 8x4 Rigid all weights | 16 | — | — | — | — | 4.1% | — | — | — | 4.1% |
| 8x6/8x8 Rigid all weights | (17) | — | — | — | — | 0.3% | — | — | — | 0.3% |
| Bus City Class I | b&c | — | — | — | — | — | 4.4% | — | — | 4.4% |
| Coach Interurban Class II | b&c | — | — | — | — | — | — | 2.7% | — | 2.7% |
| Coach Class III | b&c | — | — | — | — | — | — | — | 2.5% | 2.5% |
| **Total** | | **2.3%** | **2.4%** | **15.0%** | **57.3%** | **13.4%** | **4.4%** | **2.7%** | **2.5%** | **100.0%** |

*(Some individual group-level cell mappings in the dense source table are reproduced with best-effort fidelity — "[unclear from source: a few individual cell-to-mission-profile mappings in the original Table 30, particularly for the small bracketed/excluded groups, could not be perfectly disambiguated from the text extraction, though the group definitions, the per-category totals, and the grand total row (2.3%/2.4%/15.0%/57.3%/13.4%/4.4%/2.7%/2.5% = 100.0%) are verbatim from the source]".) **Key takeaway (unambiguous): Long haul (57.3%) dominates total HDV CO2 emissions by a wide margin, followed by Regional delivery (15.0%) and Construction (13.4%).***

### 5.3.1 All-wheel-drive trucks
Not covered due to low overall CO2 contribution and specialised/inhomogeneous mission profiles (fuel-saving technologies like low-RR tyres and low-drag bodies often conflict with off-road-vehicle customer needs) — "[Figure 52 description: photograph of a 6x6 rigid truck example (MAN TGS 6x6, Kessler and Hemro-Tech GmbH, sourced from www.Ditzj.de).]" No urgent inclusion need identified, but **recommendation to monitor market development** (comparing total vehicle-registration numbers against CO2-reporting-covered vehicle numbers as an indicator) in case non-regulated-truck share grows.

### 5.3.2 Specific bodies, trailers, and semi-trailers
Considered **more important than AWD trucks** for further CO2 coverage. No statistics exist on yearly mileage by body/trailer type, so CO2-emission share by body type cannot be assessed directly — but since tractor groups 5 and 10 (long-haul-dominant) have the highest truck CO2 share, their associated semi-trailers likely have correspondingly high CO2 share, and aerodynamic improvements there have high leverage.

### Table 31 — Market share of body/trailer types (compiled from ref [4])
| | Box/Curtain | Tank/Bulk | Container/Swap | Tipper | Others | Total |
|---|---|---|---|---|---|---|
| Truck bodies | 39% | 2% | 8% | 18% | 34% | 100% |
| Semi trailers | 60% | 7% | 8% | 12% | 13% | 100% |
| Trailers | 31% | 4% | 16% | 18% | 31% | 100% |

Currently **all trucks are certified using "standard bodies"/"standard-trailers"** in box-body design, so real body/trailer improvements are not reflected in CO2 certification unless the standards themselves are updated. Footnote: air-drag differences by body type were investigated in ref [15] — **tank/bulk bodies found ~7% lower CdxA, tippers ~15% lower CdxA** than box bodies (at zero-crosswind conditions); cross-wind sensitivity also differs significantly by body type.

**Proposed path forward:** a **generic tractor model per tractor group** (e.g., based on average CO2-monitoring efficiencies) would let VECTO compute full tractor+trailer CO2 values even though the actual trailer pairing is unknown at tractor certification. Trailer/semitrailer "fuel efficiency" could then be expressed as **% CO2 reduction vs. the standard trailer**; truck bodies could use either a multistage g/t-km approach or a similar % reduction vs. standard body.

**Proposed steps for body builders:**
1. Identify body/trailer weight.
2. Select tyres, obtain the tyre-manufacturer's VECTO input (RRC etc.).
3. Simulate or measure CdxA (or the delta against the standard body/trailer); default to unchanged CdxA if no measured value exists.
4. Run VECTO with adjusted mass/tyre/air-drag data, using either the real chassis's VECTO data or generic chassis/tractor data.

A well-defined **CFD-simulation-based certification approach** is floated as a cost-efficient path (referencing the **US EPA Phase 2 regulations**, which permit CFD under defined parameter/settings provisions); **CLCCR and VDA were working on this** at report time with no results yet available. A cheaper first step (semi-trailers only): use weight + tyre selection for VECTO calculation, with **credits for well-defined aero-devices** (side skirts, boat tails) — providing incentives for low-RR tyres and standard aero devices on semi-trailers at low certification cost.

## Standards, organisations, and references cited in this chapter (exact names only)
- SORT cycles (Standardised OnRoad Test 1/2/3, bus cycle — per abbreviations list)
- ACEA (TF5 working group; White Book 2016; segmentation-matrix revision work)
- DG JRC
- CLCCR, VDA
- Ricardo (SR3 project — ref [13]: Norris, Hill, Kirsch, Nurse, Revereault, Preston — "Quantifying energy consumption of HDV auxiliary components and their contribution to CO2 emissions of buses and coaches," Heavy Duty Vehicles Framework Contract Service Request 3 Final Report for DG Climate Action, Ref CLIMA.C.2/FRA/2013/0007)
- Ref [12]: Silberholz G., Hausberger S. — "Feasibility assessment regarding the development of VECTO for hybrid heavy-duty vehicles," draft final report, service contract CLIMA.C.4/ETU/2016/0005LV, Graz, 6.7.2017
- Ref [15]: Frasquet C., Indinger T. — "Schwere Nutzfahrzeugkonfigurationen unter Einfluss realitätsnaher Anströmbedingungen," FAT Schriftenreihe 281, 2014
- US EPA Phase 2 (Heavy-Duty vehicle GHG) regulations (referenced re: CFD-based certification precedent)
- WLTP / WLTC (Worldwide Harmonized Light Vehicles Test Procedure/Cycle)
- JE05, NERV, WHVC (named HDV chassis-dyno test cycles)
