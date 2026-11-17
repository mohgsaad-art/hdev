# SR7/LOT4 Final Report — Document Metadata, Overview & Task Summary

> **Source file:** `sr7_lot4_final_report_en.pdf` (project file)
> **Extraction date:** 2026-09-20
> **Coverage:** Full document, pages 1–156 (main body pages 1–128 fully text-extracted; Annex I pages 129–131 and Annex II pages 132–156 are image/scan-based in the source PDF and contain **no machine-extractable text** — flagged as "[unclear from source — Annex content not text-extractable]"). This is one of 7 knowledge-base files covering this report; see the companion files listed at the bottom for the rest of the coverage.

## 1. Document identification (from the document itself — not inferred from filename)

| Field | Value (verbatim from source) |
|---|---|
| Document type | "Draft final Report" |
| Full title | **"VECTO tool development: Completion of methodology to simulate Heavy Duty Vehicles' fuel consumption and CO2 emissions — Upgrades to the existing version of VECTO and completion of certification methodology to be incorporated into a Commission legislative proposal."** |
| Service contract | CLIMA.C.2/SER/2012/0004 |
| Specific Contract N° | 340201/2014/695203/SER/CLIMA.C.2 [exact digits partially ambiguous in OCR — rendered in source as "34020112014/695203/SERJCLIMA.C.2"; the contract number is otherwise consistently cited elsewhere as **CLIMA.C.2/SER/2012/0004**] |
| Framework contract | CLIMA.C.2/FRA/2013/0007 |
| Commissioning body | **European Commission, DG CLIMA** ("By order of EUROPEAN COMMISSION DG CLIMA") |
| Report number | I 15/17/Rex EM-I 2013/08 1670 |
| Report date | 30.10.2017 |
| Project nickname used throughout | **"SR7"** ("Service Request 7") — per the report's own abbreviations list: "SR7 'Service Request 7', naming of the project/contract described in this report." The filename element "LOT4" reflects that SR7 is the continuation/completion of the "LOT 4" consortium's work (LOT2 and LOT3 being the two prior projects under the same overall Commission programme). |
| Corresponding author listed on title page | Heinz Steven |

### Authors (as listed on page 2, with affiliations)
- Martin Rexeis — TUG (Technische Universität Graz)
- Markus Quaritsch — TUG
- Stefan Hausberger — TUG
- Gérard Silberholz — TUG
- Antonius Kies — TUG
- Heinz Steven — HS DAC
- Martin Goschütz — TNM
- Robin Vermeulen — TNO

### Subject matter (confirmed from content, not filename)
This is the **final technical report of the "SR7" service contract** under the European Commission's programme to develop **VECTO** (Vehicle Energy Consumption calculation Tool), the official EU simulation tool used to certify **CO2 emissions and fuel consumption of Heavy-Duty Vehicles (HDVs)** — trucks, and (partially) buses and coaches. It documents the finalisation of the VECTO-based HDV CO2 certification methodology that was subsequently adopted into EU legislation (the "HDV CO2 TA" — Technical Annex — adopted by the TCMV, Technical Committee on Motor Vehicles, on 11 May 2017). **This report predates and is entirely about conventional (internal-combustion-engine, ICE) heavy-duty vehicles.** Electrification (HEV/PHEV/EV) is referenced only as future/out-of-scope work items (see file 06 and 07 of this series). This is highly relevant background for an HDEV (Heavy-Duty Electric Vehicle) sizing tool because VECTO's simulation architecture, driving-cycle/mission-profile framework, generic vehicle/payload/auxiliary datasets, and validation methodology are the direct technical and regulatory ancestors of any future electric-HDV simulation/certification approach, and because a parallel/related project is explicitly cited as addressing hybrid/electric extensions (see Literature reference [12] in file 07).

## 2. Table of contents (as printed in the source, page 3–5)

1. Introduction (p.8)
2. Overview on the outcome of the project and the content of the report (p.9)
3. Work description per task (p.10) — Tasks A.1–A.4, B.1–B.6, C.1–C.7
4. Description of methodologies (p.24)
   - 4.1 Introduction
   - 4.2 Component test procedures (Engine, Air drag, Transmission, Axle)
   - 4.3 Software VECTO (overview, architecture, development methods, testability, generic data)
   - 4.4 Ex-Post test procedure (EPTP) (p.82)
   - 4.5 Regulatory description (p.100)
5. Application of the VECTO method for HDV groups not covered by the actual HDV CO2 legislation (p.101) — Buses & coaches, intermediate-size vehicles (M2/N2), other HDV groups
6. Main open work for follow up activities after SR7 (p.120)
7. Summary and outlook (p.124)
8. Literature (p.127)
- Annex I: Documents for Planning of the Bus and Coach Pre-Pilot Phase (PPP) (p.129) — **image-based, not text-extractable**
- Annex II: Guidelines how to use VECTO in the Bus and Coach Pre-Pilot Phase (PPP) (p.132) — **image-based, not text-extractable**

## 3. Executive summary / objectives (Chapter 1 "Introduction" and Chapter 2, verbatim substance)

The European Commission (EC) prepared a certification methodology for HDV CO2 emissions based on **testing individual vehicle components** (engine, transmission/axle, air drag, tyres) and **subsequently simulating** the fuel consumption/CO2 emissions of the whole vehicle — rather than testing the complete vehicle directly. This is explicitly stated as a means to capture the diversity of HDV configurations "without heavily increasing the complexity and costs for vehicle certification."

**VECTO** ("Vehicle Energy Consumption calculation Tool") is the central software product of this approach: it "simulates CO2 emissions and fuel consumption based on vehicle longitudinal dynamics using a driver model for backward simulation of target speed cycles." Required engine load is derived from driving resistances, drivetrain losses, and auxiliary power draw; engine speed comes from a gear-shift model, gear ratios, and wheel diameter; fuel consumption is interpolated from an engine fuel map; CO2 is calculated from fuel consumption and reference fuel specifications.

Prior projects **LOT2** [ref 3] and **LOT3** [ref 4] had already brought the method and software to "a high level." **SR7's objectives** were to:
a) Finalise the entire CO2 certification method for trucks as the basis for a legislative procedure.
b) Advance additional open tasks: inclusion of additional HDV categories/technologies and improvement of software quality.

Tasks covered by the consortium:
a) Development of proper methodologies for component tests, validation tests, and simulation.
b) Development of the necessary software.
c) Elaboration of default input data / generic values.
d) User assistance.
e) Stakeholder consultation.

Work was performed "in close cooperation with industry and with JRC" (Joint Research Centre).

### SR7 project deliverables (as explicitly listed in Chapter 2)
1. The VECTO software itself (final version **VECTO 3.2**), "suitable to be used as the backbone of the future European HDV CO2 certification."
2. A complete set of **generic data** for CO2 certification of trucks for **vehicle groups 1, 2, 3, 4, 5, 9, 10, 11, 12 and 16** — comprising driving cycles, driver-model settings, generic gear-shift strategies (MT, AMT, AT), vehicle payloads, standard body/trailer definitions, wheel specifications for all common HDV tyre dimensions, auxiliary power-demand data, refuse-truck ("municipal cycle") usage data, fuel properties for the six ECE R49 reference fuel types, and average European ambient-condition data.
3. A VECTO user manual (HTML, embedded in the GUI).
4. A VECTO software development guidelines document (Annex II of the final report).
5. The **"VECTO Engine"** pre-processing tool + user manual (PDF).
6. The **"VECTO Air Drag"** pre-processing tool + user manual (PDF).
7. This final report.

## 4. Methodology (high-level, per Chapter 4.1)

The overall "VECTO approach" consists of four main elements (detailed fully in companion files 02–05):
1. **Component test procedures** for the main fuel-efficiency-relevant components: engine, transmission and other torque-transmitting components, axle, air drag, and tyres.
2. **Standardised pre-processing tools**: "VECTO Engine" (evaluates the engine component test) and "VECTO Air Drag" (evaluates the constant-speed air-drag test).
3. The **VECTO simulation tool** itself, with embedded "generic" data on mission profiles, payloads, driver behaviour, etc.
4. **Regulatory/legislative implementation** of 1–3.

## 5. Work description per SR7 task (Chapter 3) — condensed status table

SR7's proposal structured work into Tasks A (methodology/coordination), B (2015 VECTO upgrade / core finalisation), and C (extensions to other vehicle groups and software quality).

### Task A — ongoing/cross-cutting tasks
| Task | Content | Status |
|---|---|---|
| A.1 | General rules/methods valid across all tasks; test plans for pilot phase (trucks) and pre-pilot phase (buses); user support; targeted validation activities (TUG chassis-dyno tests, support to JRC/ACEA validation); comparison of real-world "proof of concept" FC/CO2 vs. simulated results (see PhD thesis, ref [2]) — "All comparisons indicate that realistic fuel consumption values are provided by VECTO." | Completed |
| A.2 | Software development guidelines (delivered as Annex II) | Completed |
| A.3 | User assistance (phone/email/audioweb); evaluation of test results; training workshops: VECTO Air Drag (23.04.2015), VECTO general (29–30.06.2015), VECTO Buses and Coaches (12.09.2016), Ex-Post Validation (14.12.2015), VECTO PTO (18.01.2017); help desk via CITnet Jira (set up by JRC) | Completed |
| A.4 | Stakeholder consultation: 3 advisory board meetings; 8 editing board meetings; 10 bus-related meetings; 5 N2/M2 meetings (4 via audioweb); 41 meetings on other topics (transmission, IT, etc.); 3 Ex-Post Validation meetings; 31 expert-group meetings (engine, air drag, auxiliaries) | Completed |

### Task B — 2015 VECTO upgrades and finalisation
| Task | Content | Status |
|---|---|---|
| B.1 (8 sub-items) | Complete transmission sub-model (MT/AMT adjustments; AT model calibrated by TUG, released July 2017 — note: "a few percent inaccuracy can already change the ranking between gear box models"); finalise air-drag test definition; finalise VECTO-CSE tool, renamed **"VECTO Air Drag"**; review/validate HDV mission cycles (Municipal cycle updated per DIN SPEC 30752-1); relevant tests with OEMs/JRC (Daimler, Scania chassis-dyno tests at TUG); tool development ("VECTO Engine", "VECTO Air Drag", EPTP "Pwheel mode"); bus-auxiliary sub-model issues addressed; finalise VECTO version as pilot-phase-1 backbone | Completed (gear-shift logic amendments still under industry discussion) |
| B.1 deliverables | Final LOT4 releases: **VECTO 3.2** (incl. VECTO Air Drag, VECTO Engine); HTML user manual; CO2 test cycles + generic input data set; generic HDV input-data set; VECTO Air Drag/Engine user manuals (PDF) | — |
| B.2 | Review/amend engine map calculation approach: measurement-equipment accuracy requirements (improved vs. Euro VI); corrections for variable fuel carbon content (applicable to all test fuels except Diesel — for Diesel, "fuel analysis shows the same range of uncertainty compared to the spread in fuel specifications," so no correction applied, but test fuel properties must still be reported); legislative implementation of engine test technical annex | Completed |
| B.3 | Verification/Validation (EPTP) finalisation: reviewed LOT3 "SiCo" (simple constant-speed) VV method → concluded VECTO input data should be released for ex-post recalculation rather than ex-ante calculation; 2 trucks tested at TUG chassis dynos with wheel-rim torque measurement; further tests at OEMs/JRC; draft technical annex released January 2017; one industry comment round; OEM feedback expected autumn 2017 | Completed by TUG; ACEA pilot-phase testing not yet done by Sept. 2017 |
| B.4 | Finalise technical annex: updates from LOT3 open issues adopted by TCMV 11 May 2017; V&V technical annex delivered as basis for test phase; CoP (Conformity of Production) methods/tolerances elaborated via technical/statistical analyses | Completed |
| B.5 | Multistage-vehicle second-stage certification: example standard look-up tables for 2 vehicle categories forwarded to CLCCR; CLCCR developing a CFD tool to simulate air-drag changes from alternative bodies vs. standard bodies (assumed more cost-efficient than physical testing if standardised); further activities postponed pending CFD feasibility; representative cargo volume elaborated alongside representative payload, enabling gCO2/m³-km reporting | Look-up tables completed; further work deferred, "unclear if needed" |
| B.6 | Demonstration test campaign organised with main OEMs + Type-Approval Authorities/Technical Services; feedback collected and used to amend technical annexes and VECTO source code | Completed |

### Task C — extension to additional vehicle groups and software quality
| Task | Content | Status |
|---|---|---|
| C.1 | Validate SR3 "auxiliaries" project outcome: Ricardo bus auxiliary tool implemented into VECTO (from v3.1); test cases added; bugs fixed (with JRC/Ricardo); analysis of applicability to mild hybrids (brake-energy recuperation via alternators — may work) and full hybrids (auxiliary tool "may not work properly" if HEV simulation included — detailed in a **parallel project**: CLIMA.C.4/ETU/2016/0005LV, "Feasibility assessment regarding the development of VECTO for hybrid heavy-duty vehicles") | Completed |
| C.2 | Buses and coaches: pre-pilot phase (PPP) designed/coordinated — covers component testing + VECTO simulation but **not** type-approval authorities/technical services; final "pilot phase" postponed (insufficient time for industry testing); baseline generic-parameter documents for PPP elaborated | ~50% complete |
| C.3 | VECTO for intermediate-size vehicles (M2/N2, 3.5–7.49 t): 5 stakeholder meetings; several N2/M2 vehicles simulated; comparison of VECTO cycles vs. real-world N2 data vs. WLTC → **WLTC not representative of N2/M2 mission profiles**; heavier N2/M2 fit VECTO cycles reasonably; open political-decision issue on how sub-5.5t N2 vehicles should be handled (dual pollutant-certification eligibility: WLTP vs HDV engine procedure); no complete validation dataset available for N2/M2 accuracy assessment (expert judgement suggests similar accuracy to N3/M3) | ~70% complete |
| C.4 | Vehicles not covered in LOT3/LOT4 — analysis of relevance: refuse trucks (small overall CO2 contribution but relevant for public tenders) — VECTO simulation option added for refuse trucks and PTO bodies; recommendation on classes not to include in first-step legislation (see file 06) | Completed |
| C.5 | Make VECTO code testable / add test cases — VECTO 3.2 fulfils C.5 requirements | Completed |
| C.6 | Truck pilot-phase organisation (continuation of B.6) + first bus/coach "Pre-Pilot Phase"; component test data / VECTO input data from truck & bus tests held only by OEMs/partly TUG under bilateral NDAs — **not shared** for confidentiality reasons | Completed |
| C.7 | Guidelines for overhauling VECTO as a forward-looking, vector-capable-language tool: review led to a 2014–2015 re-programming of VECTO; structure kept as "mainly backward simulation" with forward-simulation switches where necessary (e.g., coasting) — "demands for robustness and computation time seemed not to be possible with a forward looking model at current state of art"; feature assessment: API for data-exchange automation implemented; GUI/batch (command-line) functionality implemented; **web-server functionality not implemented** (data-security concerns, high cost); improved error handling; simulation-tool version management defined; standard data formats used | Completed |

## 6. Companion knowledge-base files (full document coverage)
- `sr7-lot4-01-overview-and-metadata.md` (this file) — metadata, objectives, Chapters 1–3
- `sr7-lot4-02-component-test-procedures.md` — Chapter 4.2 (Engine, Air Drag, Transmission, Axle test procedures)
- `sr7-lot4-03-vecto-software-architecture.md` — Chapter 4.3.1–4.3.4 (VECTO software architecture, simulation approach, driver/gearshift strategy, development process, code-quality metrics)
- `sr7-lot4-04-generic-data-and-certification-inputs.md` — Chapter 4.3.5 (segmentation matrix, driving cycles, standard bodies/trailers, payloads, wheels, fuel properties, auxiliaries)
- `sr7-lot4-05-ex-post-test-procedure-and-regulatory.md` — Chapter 4.4 (EPTP) and Chapter 4.5 (regulatory description)
- `sr7-lot4-06-extended-vehicle-groups.md` — Chapter 5 (buses/coaches, M2/N2 intermediate vehicles, all-wheel-drive trucks, bodies/trailers)
- `sr7-lot4-07-open-topics-summary-and-references.md` — Chapters 6–8 (follow-up topics, summary/outlook, full literature list) + note on non-extractable Annexes

## 7. Standards, regulations, and organisations referenced in this section of the report (exact names only)
- UN/ECE Regulation 49 (heavy-duty engine emissions test regulation referenced throughout for alignment)
- HDV CO2 legislation adopted by TCMV (Technical Committee on Motor Vehicles) on 11 May 2017, and its technical annexes ("HDV CO2 TA")
- DIN SPEC 30752-1 (Refuse collection vehicles — environmental efficiency test procedure)
- European Commission, DG CLIMA (contracting authority); DG GROW (referenced re: EPTP technical annex, separate contract)
- Joint Research Centre (JRC)
- ACEA (European Automobile Manufacturers' Association)
- CLCCR (referenced re: standard body/trailer and CFD air-drag work)
- CITnet/Jira (EC IT ticketing system used for VECTO support/bug tracking)
