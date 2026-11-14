# VECTO Technology Simulation Capabilities and Future Outlook (JRC, 2016)

## Document metadata
- **Title:** Report on VECTO Technology Simulation Capabilities and Future Outlook
- **Authors:** Nikiforos-Georgios Zacharof; Georgios Fontaras
- **Publisher:** Joint Research Centre (JRC), European Commission — Technical report ("evidence-based scientific support to the European policy-making process")
- **Year:** 2016
- **Report number:** EUR 28272 EN
- **ISBN (PDF):** 978-92-79-64158-9
- **ISSN:** 1831-9424
- **DOI:** 10.2790/10868
- **Publisher location:** Luxembourg: Publications Office of the European Union, 2016
- **Copyright:** © European Union, 2016 (reproduction authorised provided the source is acknowledged)
- **Contact:** Georgios Fontaras, Via E. Fermi 2749, TP 230, Ispra, 21027, Italy. georgios.fontaras@jrc.ec.europa.eu
- **Acknowledgements:** Biagio Ciuffo and Dimitrios Savvidis (JRC) for support/comments/revisions. Rachel Muncrief and Oscar Delgado (International Council on Clean Transportation, ICCT) for feedback on technologies investigated and questionnaire structure.
- **Page count (body, per source pagination):** Pages 1–46 (Acknowledgements p.1 through back-cover/imprint p.46), i.e. the full document as extracted by `project_read` (all pages, including Annex, References, abbreviations, figure/table lists).

> **Important scope note for this project (HDEV sizing & modelling tool):** This 2016 JRC report is **not** primarily about VECTO's capability to simulate pure battery-electric (BEV) or fuel-cell (FCEV) heavy-duty vehicles. It is a survey-based assessment of VECTO's ability to simulate ~40 **conventional and hybrid diesel powertrain fuel-efficiency technologies** for CO2 certification of diesel HDVs (rigid trucks, tractor-trailers, coaches, city buses), conducted in 2016 among OEMs, suppliers, research organizations and ACEA. The word "hybrid" here means diesel-electric (or diesel-hydraulic) hybrids, not full electrification. There is **no discussion in this document of full BEV/FCEV powertrain simulation methodology, battery sizing, charging, or depot modelling** — these topics are simply outside the report's scope. This is stated here explicitly per project instructions, rather than assumed.

---

## Abstract (verbatim summary)
The European Commission is developing VECTO (Vehicle Energy Consumption Calculation Tool) for Heavy Duty Vehicle CO2 certification. VECTO is described as "a vehicle simulation tool tailored to estimate CO2 emissions from heavy-duty vehicles of different categories, sizes and technologies." The report's purpose was to assess VECTO's capacity to properly simulate specific vehicle technologies and to gather feedback on capturing future technologies expected in HDVs. A dedicated questionnaire, based on a prior literature review of relevant technologies, was distributed to stakeholders. Findings: a large part of the surveyed technologies are already properly simulated by VECTO, indicating the tool and certification methodology "have reached a good level of maturity." The technologies not properly/fully captured were grouped into three categories based on the type of work needed (methodology-only vs. software+methodology vs. reassess later).

## Executive Summary (key points)
- Questionnaire covered: whether VECTO sufficiently captures a technology's CO2 effect; current/future market penetration; free-text comments.
- **Response rate:** 10 respondents completed the full survey; 8 more partially completed it (quit before finishing their selected categories).
- **Respondent affiliations:** research organizations, OEMs, and OEM associations. Vehicle manufacturers responded **collectively via ACEA** (European Automobile Manufacturers' Association), whose response is presented separately; some individual OEM-affiliated experts also responded individually.
- Feedback was **mostly qualitative**; quantitative data (numeric CO2/FC effect estimates) was limited.
- **Three action-priority groups** were defined for technologies not (fully) captured by VECTO:
  1. **Short-term interventions** — technology can already be covered; work needed mostly on the *certification methodology*, minimal/limited VECTO software changes: Improved alternator, Wide-base single tires, Tire pressure monitoring/automatic inflation systems, Improved oil pumps, Vehicle speed limiter.
  2. **Mid-term interventions** — require additional work at *both* methodological and software level (sometimes substantial): Predictive Cruise Control (PCC)/Advanced Driver Assist Systems (ADAS), Waste heat recovery, Electric hybrids, Electric turbocharger, A/C efficiency and refrigerant, Active flow systems, Trailer aerodynamic improvements, Dual Clutch Transmission, Neutral idle.
  3. **No action for now, reassess mid-term if more data available** — Improved cooling fan, Improved air compressor, Vehicle body redesign, Adjustable fifth wheel, Continuously Variable Transmission (CVT), Hydraulic hybrids, ECU/Engine software optimization.
- Full technology-by-technology detail is in **Table 3** (Annex, reproduced below).

---

## 1. Introduction
VECTO is described as being developed by the European Commission "in order to calculate CO2 emissions from heavy-duty vehicles (HDV)" and is "expected to be the backbone of the future European fuel consumption and CO2 emissions certification procedure for HDVs in Europe." As of 2016, VECTO and the accompanying certification methodology had "reach[ed] an established level of maturity with test results demonstrating their capacity to realistically capture the CO2 emissions and fuel consumption of HDVs."

The report's stated purpose: assess (a) whether established, fuel-consumption-relevant technologies are insufficiently simulated, and (b) whether new/emerging technologies expected in coming years should be implemented in VECTO.

Methodology: a literature review identified candidate technologies → a questionnaire was circulated to OEMs, suppliers, research organizations, and ACEA, asking about:
- Effect of each technology on CO2 emissions across HDV types and operating conditions
- Level of market penetration now and in a 5–10 year horizon
- Additional comments/feedback on VECTO's performance regarding the technology

ACEA responded officially and collectively (separate section); some individual OEM-affiliated experts also responded individually.

## 2. Identification of relevant technologies
A literature review identified technologies likely to enter the HDV market to improve fuel efficiency, organized by category (engine, aerodynamics, tires, axles/transmission, hybrids, mass, idling, components/auxiliaries, controls/energy management) — see **Table 1** below and the fuller **Table 2** in a companion file.

Note on data provenance: "The number of sources found regarding the European market and the European HDV fleet was relatively limited. Many estimates were based on studies made for US vehicles and fleets and on information provided by the US Environmental Protection Agency (EPA)." Because the US and European markets/fleets differ, results were **presented separately by region of origin (US vs. Europe)** in Table 2. The questionnaire feedback on technology CO2 impact "confirmed, in most cases, the estimates which were found in the literature, particularly the ones focusing on European vehicles."

## 3. Questionnaire structure
- Built on an online platform; respondents self-selected technology categories matching their expertise; only questions in selected categories were shown.
- For each technology, first question: is its CO2 effect "sufficiently captured by VECTO"?
  - If **yes** → skip to next technology.
  - If **no** or **"I don't know / not sure"** → asked to estimate: fuel consumption reduction, and current/future market penetration, for four HDV classes:
    - Rigid trucks
    - Tractor–trailers
    - Coaches
    - City buses
- Free-text comments allowed per question, plus general comments at survey end.
- Disclaimer: responses reflect **individual expert opinions**, not official positions of their affiliations.

## 4. Responses overview
- Collection period: **23 March 2016 – 10 June 2016**.
- 10 respondents completed the survey; 8 more gave partial feedback but quit before finishing.
- **ACEA replied separately** with a comprehensive overview, examined/presented apart from other respondents due to its significance.
- Data obtained was mostly qualitative; little usable quantitative data for statistical analysis.

**[Figure 1 description — "Number of respondents by technology category and breakdown by respondent affiliation"]:** A bar chart (page 7) with y-axis "Number of respondents" (scale 0–14) and x-axis = technology category (Engine, Aerodynamics, Tyres, Mass decrease, Transmission and differentials, Hybrids, Idling, Components and auxiliaries - Controls/Energy management). [Exact per-category respondent counts and the affiliation breakdown (colors/series) are not resolvable from the extracted text — the chart's data values themselves were not present as text in the source extraction; noting as [unclear from source] rather than guessing.]

## 5. Results and Discussion

### 5.1 Simulated technologies overview
Each technology was classified into one of three categories based on the pattern of survey answers:
- **Simulated:** all respondents said the technology's effect is sufficiently captured.
- **Not simulated:** all respondents said it is not sufficiently captured.
- **Contradicted:** some respondents said yes, others said no.
("I don't know/not sure" answers were excluded from this classification.)

**[Figure 2 description — "Individual technologies were separated into three categories depending on the simulation capabilities of VECTO"]:** Bar chart (page 8), y-axis "Number of technologies" (scale 0–14), x-axis = same technology categories as Figure 1 (Engine, Aerodynamics, Tyres, Mass decrease, Transmission and differentials, Hybrids, Idling, Components and auxiliaries - Controls/Energy management), with three series: Simulated / Not simulated / Contradicted. [Exact bar heights per category/series were not resolvable as text from the extraction; noted as [unclear from source].]

ACEA additionally used its own 4-level classification (used throughout Table 3):
- **Captured:** effect fully captured, available in VECTO.
- **Partially captured:** effect partially captured, or models are "readily available for implementation in VECTO."
- **Not captured:** effect not yet captured but model development/implementation work is "in process."
- **Not covered/possible:** not possible to implement, or no model development in process.

### 5.2 Technology quantitative effect
Few respondents gave quantitative fuel-consumption effect data; sample sizes were 1–3 estimates per technology — too small for statistical analysis, but "as the replies reflect experts' opinion they can be considered to be highly significant." These are compiled in **Table 4** below, alongside literature-review values (Table 2), separated into EU and USA because of regional diversity.

### 5.3 Market penetration
Data was scarce (1–2 replies for many technologies) — presented in **Table 5** as "a starting reference point for future investigation," not a robust market study.

Technologies estimated to reach **>10% market penetration in Europe within 5–10 years** (i.e., "important" penetration) per respondents: improved cooling fan, improved water pump, roof fairings, trailer mounted extensions, boat tails, mild electric hybrids, LED lighting, improvements in air compressor, and predictive cruise control / other advanced driver aid systems. Report notes most of these "can be captured by VECTO provided that the certification methodology is adequate." Report recommends further feedback specifically on penetration rates of waste heat recovery, electric turbocharging, and full hybridization (buses), since these "appear to offer important benefits."

## 6. Conclusions
- Some technologies had highly divergent respondent opinions on VECTO coverage; ACEA's contribution added clarity in these cases by identifying specific uncaptured features and suggesting implementation methods.
- Quantitative data insufficient for statistics but usable as a general estimate for some technologies.
- A large share of surveyed technologies were already sufficiently captured, or could be captured with limited additional simulation effort (e.g., adding a generic factor) or through certification-methodology extension.

### Full list of proposed actions by technology (Conclusions section, verbatim structure)

**A. Short-term interventions (certification-methodology work, minimal/limited VECTO software change):**
- **Improved alternator** — needs a certification procedure, to be discussed with CLEPA (European Association of Automotive Suppliers), ACEA, and other stakeholders; generic technology list can be expanded if proven necessary.
- **Wide base single tires** — consider a generic aerodynamic-improvement factor for these tires, to be quantified via dedicated drag-determination tests; no info found on actual market share; additional feedback could be sought from ETRMA (European Tyre & Rubber Manufacturers' Association).
- **Tire pressure monitoring and automatic inflation systems (TPMS/ATIS)** — noted as potentially contradictory: HDVs are type-approved on the tire's official rolling-resistance coefficient, but operating under-inflated increases real-world rolling resistance/consumption. Two proposed promotion options: (a) mandate these systems (real-world savings + possible safety benefit), or (b) increase the rolling-resistance value used in VECTO by x% vs. nominal to reflect real-world deterioration, accepting the nominal value only if the vehicle has TPMS.
- **Improved oil pumps** — investigate need to add to generic technology list; further feedback requested from engine OEMs.
- **Vehicle speed limiter** — further feedback requested from ACEA on need/implementation; ACEA said a simple implementation is possible; no market-penetration data available.

**B. Mid-term interventions (work needed at both methodology and software level, sometimes substantial):**
- **Predictive Cruise Control (PCC) / Advanced Driver Assist Systems (ADAS)** — request additional feedback from stakeholders/ACEA; a clear definition is needed (PCC/ADAS terms are "too general" and cover non-comparable systems); validation methodology needed to confirm real-world CO2 benefit delivery; implement only once OEM/supplier consensus reached on definition, characteristics, simulation approach, validation; a fixed CO2 discount per technology (to be quantified) suggested as a possible short-term interim solution, contingent on proving realism.
- **Waste heat recovery (WHR)** — extent of current coverage via VECTO's engine-map-based methodology should be investigated further; certification/engine-map-measurement issues need resolving before further model development; a fixed CO2 discount of **2–3.5%** could be a short-term solution but needs supporting data across operating conditions/vehicle categories. Notes a steady-state fuel-map approach may overestimate savings due to WHR systems' high thermal inertia.
- **Electric hybrids** — addressing fully hybrid vehicles needs substantial VECTO tool AND certification-methodology development (incl. certification of hybrid components). A first solution "along the lines proposed in the ACEA White Book" can be investigated. **A contract on the topic had already been launched by DG Clima** (as of report writing). Fully capturing electric hybrids "might require in the future transition to a forward-looking model which would require a complete redesign of VECTO software" — to be assessed separately. [Note: "forward-looking model" vs. VECTO's current backward-looking/map-based simulation approach is an important architectural distinction for this project.]
- **Electric turbocharger** — should be considered in future VECTO updates, especially alongside electric hybrid systems; feedback requested from OEMs; ACEA stated simulation models for this technology are available.
- **A/C efficiency and refrigerant** — discuss defining a certification procedure for system efficiency, starting with buses/coaches, later extending the bus-auxiliaries model to trucks if relevant.
- **Active flow systems** — discuss inclusion in drag-determination tests, or a generic-technology-list approach if significance is proven.
- **Trailer aerodynamic improvements** — discuss including non-standard trailer bodies in drag-determination tests; extend methodology if necessary.
- **Dual Clutch Transmission (DCT)** — efficiency is captured, but unclear why shifting strategy should differ from existing; feedback requested from suppliers/OEMs (incl. market-penetration predictions); discuss developing a shifting logic if needed — noted that reaching consensus on a common shifting logic "can be very time consuming."
- **Neutral idle** — reassess after automatic-transmission modelling is implemented (a prerequisite).

**C. No action advised now; revisit mid-term if more data available:**
- **Cooling fan** — possibly adopt a bus-auxiliaries-like operating approach in future if needed; generic cooling-fan energy-consumption values could be revised with new data.
- **Air compressor** — consider extending coverage of specific technologies if verifiable; discuss extending part/all of the bus-auxiliaries module to trucks if needed.
- **Vehicle body redesign** — consider revising standard bodies used in the drag-determination procedure in future.
- **Adjustable fifth wheel** — possible need to revisit the constant-speed drag test once the technology becomes widely available in Europe.
- **Continuously Variable Transmission (CVT)** — discuss adding in future if it becomes relevant for the European market; note possible relevance for non-European markets; could investigate a global-level solution if needed.
- **Hydraulic hybrids** — little information collected; request additional feedback within the DG Clima Hybrids contract framework; any VECTO-implementation need must be clearly demonstrated.
- **ECU/Engine software optimization** — very difficult to describe/validate; possibly consider in future as part of a "VECTO-SILs" (Software-In-the-Loop) upgrade if deemed necessary for certification; would require accompanying validation methodology.

### Additional qualitative findings from respondent comments (Section 6, closing remarks)
- Most feedback focused on **trucks (rigid and tractor-trailer)**; little info was received on **city buses and coaches**.
- The **engine-map approach is considered sufficient** for many engine/axle/transmission technologies under **steady driving conditions**, but its sufficiency for **transient driving** is disputed in some cases; more sophisticated technologies (e.g., WHR) should account for transient conditions.
- **Many emerging technologies relating to energy recuperation and storage are not captured** by the (2016) VECTO version; respondents flagged the need to implement these as the tool develops toward hybrid powertrains, covering hydraulic, electric-hybrid, and flywheel energy storage applications.
- A key highlighted issue: **design of electrical paths**, especially for handling recuperated/restored energy — better design/implementation of electrical paths is needed to simulate hybrids and to properly simulate electrically-controlled components (electric turbochargers, air compressors, fans).
- **Electrically powered/controlled component options are not adequately simulated compared to their mechanical counterparts** (as of 2016).

---

## Annex — Table 1: List of technologies by category
*(Source Table 1, p.5 — technology taxonomy used to structure the whole study)*

| Engine | Aerodynamics | Tires | Axles and transmission |
|---|---|---|---|
| Turbochargers | External grilles | Wide base single tires | Automated Manual Transmission (AMT) |
| Intake/exhaust | Active flow systems | Low rolling resistance tires | Continuously Variable Transmission (CVT) |
| Waste heat recovery | Mirror replacement | Tire pressure monitor systems | Dual Clutch Transmission (DCT) |
| Internal friction reduction | Tractor cabin and trailer fairings | Automatic tire inflation systems | Additional gear ratios |
| Engine efficiency | Boat tails | | Axle efficiency |
| Engine downspeeding | Vortex generators | | Lubricants |
| Lubricant | Adjustable fifth wheel | | |
| Engine Control Unit (ECU) optimization | Vehicle redesign | | |
| Cooling fan | | | |
| Alternator | | | |
| Water pumps | | | |
| Oil pumps | | | |

| Hybrids | Mass | Idling | Components and auxiliaries |
|---|---|---|---|
| Hydraulic hybrids | Mass reduction | Stop-start systems | Electric hydraulic power steering |
| Full/mild electric hybrids | | Auxiliary power units | LED lighting |
| Flywheel | | Neutral idle | Air compressor |
| | | | A/C efficiency and refrigerant |
| | | | Reflective paint and glazing |
| | | | Predictive cruise control |
| | | | Advanced Driver Assistance Systems |

> Full literature-review detail per technology (effect size, source, region, description) is reproduced verbatim in the companion file **Table 2 — Literature review of technologies reducing fuel consumption in heavy-duty vehicles** (`vecto-technology-literature-review-table2.md`), covering: Turbochargers, Intake/exhaust, Internal friction reduction, Increase in engine efficiency, Aftertreatment system optimization, Waste heat recovery, Engine downspeeding, ECU/Engine software optimization, Cooling fan, Water pumps, Low-viscosity lubricant, External grille shutter, Active flow control, Mirror replacement, Tractor cabin mounted extensions, Trailer-mounted extensions, Boat tails/extension panels, Vortex generators, Adjustable fifth wheel, Complete vehicle redesign, Full airflow package, Wide base singles, LRR tires, Tire pressure systems, Automatic inflation system, AMT, DCT, CVT, Axle efficiency, Additional gear ratios, 6x2 / Enhanced 6x2 / Disconnect 6x4 axle, Low-viscosity lubricants (axle/transmission), Hydraulic hybrid, Electric hybrids, Flywheel, Mass reduction, Auxiliary power units (APU), Stop-start, Neutral idle, A/C system efficiency, Solar reflective paint/glazing, Electro-hydraulic power steering, LED lighting, Predictive cruise control, Advanced Driver Assistance Systems (ADAS), Vehicle speed limiter.

---

## Annex — Table 3: Summary of VECTO capabilities based on respondent feedback and proposed action
*(Source Table 3, pp.27–32. Note: the source PDF text extraction for the rightmost "Respondent feedback/Suggestions" column was visibly truncated/fragmented for many rows — likely a layout/column-wrap artifact in the original PDF table. Where a cell's text is incomplete or garbled in the source, it is marked "[fragment in source — incomplete]" rather than filled in.)*

| Category | Technology | Online-survey classification | ACEA classification | Overall / respondent feedback summary |
|---|---|---|---|---|
| Engine | Turbochargers | Contradicting views | Partially captured / Models available | Mechanical turbochargers captured sufficiently. Further work needed on electric-path design for electric turbocompounds. ACEA: electrical path could be captured by a recuperation model (adaptation of a future hybrid model). [fragment in source — incomplete] |
| Engine | Intake/Exhaust | Contradicting views | Simulating | ACEA: considered in fuel map. No action. |
| Engine | Waste heat recovery | Contradicting views | Model work necessary prior to implementation in VECTO | Energy-recovery model required; could use fuel-map approach, though steady fuel-map approach could overestimate savings (high thermal inertia of WHR systems). Mechanical WHR covered by fuel map. One respondent: backward simulation not adequate for capturing this technology's effect. Inadequacies also noted in engine certification procedure. ACEA: fuel-map approach generally suitable; NOx/PM certification definition necessary; estimated fuel savings 2–3% depending on cycle. [fragment in source — incomplete] |
| Engine | After-treatment system optimization | Simulating | Simulating | All but one respondent consider it captured. Dissenting respondent: NOx and CO2 measured separately, no link between CO2 calculation and actual NOx test. One respondent: dependency on aftertreatment thermal conditions not fully covered. No action. |
| Engine | Internal friction reduction | Simulating | Simulating | No action. |
| Engine | Increase in engine efficiency | Simulating | Simulating | No action. |
| Engine | Engine downspeeding | Simulating | Simulating | ACEA: fully captured but additional verification of shifting strategy may be required. No action. |
| Engine | Low Viscosity Lubricant | Simulating | Simulating | Captured in the steady-state engine map; only the lubricant used in engine testing is considered — no way to assess different lubricants without a test. No action. |
| Engine | ECU/Engine software optimization | Contradicting views | Not possible / not reasonable | Cannot be captured by a generic driver/gearshifting model; ECU optimization and intelligent controllers difficult to implement in current VECTO; possibility of Software-In-the-Loop mentioned. ACEA: not covered; estimated FC benefit ~1%. No action [fragment — mentions "validate" / "part of a..." incomplete]. |
| Engine | Cooling fan | Contradicting views | Simulating | Covered via technology list with generic values. One respondent: in current VECTO cycles the fan is off most of the time, hard to demonstrate savings; current approach (adding fan-loss as a constant value per technology) sufficient for now, but future accuracy may need fan-control-strategy and engine cooling-circuit modelling. Another respondent: VECTO should allow on-demand activation and different power levels depending on other vehicle systems' status; need for a forward-looking model mentioned. No action [fragment incomplete]. |
| Engine | Alternator | Contradicting views | Model work necessary prior to implementation in VECTO | Some respondents say covered; others ask for extension of the electric-auxiliary technology list plus a certification procedure. ACEA: not fully captured yet; technology list extendable only after an alternator-efficiency certification test procedure is defined; estimated benefit ~0.5%. No action [fragment — mentions "certificat..." "members" incomplete]. |
| Engine | Water pumps | Contradicting views | Simulating | Most respondents consider effect captured in engine map; some note lack of transient-operation modelling (currently a steady-state map). No action [fragment — "transient" incomplete]. |
| Engine | Oil pumps | Simulating | Partially captured / Models available | ACEA: can be captured either via fuel-map approach or a technology-list approach with generic power demands. No action [fragment — "an actuator" / "technolog[y]" incomplete]. |
| Aerodynamics | External grille shutters | Contradicting views | Partially captured / Models available | Contradicting views on actual benefit; effect can be quantified during the air-drag test. ACEA: effect captured either via 0° yaw-angle air-drag tests (if mounted on tractor during test) or via generic values in a technology list with an average generic improvement. No action [fragment — "air drag" incomplete]. |
| Aerodynamics | Active flow systems | Not simulating | Partially captured / Models available | Not captured by methodology, particularly trailer-mounted systems, though testing possibilities exist. One respondent: trailer aerodynamic drag is a large fraction of total vehicle drag — "low hanging fruit" is at the trailer side; active flow control needs energy (a cost vs. passive devices), so 5–10 year penetration will be low. ACEA: same 0° yaw-angle test / generic-value approach as external grille shutters. No action [fragment — "non-standard," "quantify" incomplete]. |
| Aerodynamics | Mirror retraction/replacement, component replacement | Contradicting views | Simulating | Effect can be captured during the constant-speed air-drag test. No action. |
| Aerodynamics | Tractor cabin mounted extensions | Contradicting views | Simulating | Captured; one respondent: constant-speed test doesn't capture sidewinds, so the technology's full potential isn't captured. No action. |
| Aerodynamics | Trailer mounted extensions | Contradicting views | Not possible / not reasonable | Not captured — only standard body types considered in air-drag determination. Respondents note high potential savings if applied at trailer level. ACEA suggests a 3% CO2 benefit from this technology. No action [fragment — "non-standard," "how to a[ddress]" incomplete]. |
| Aerodynamics | Boat tails/extension panels | Contradicting views | Not possible / not reasonable | Not captured — only standard body types considered. Expected to increase after a change in weights-and-dimensions legislation. ACEA suggests a 3% CO2 benefit. |
| Aerodynamics | Vortex generators | Contradicting views | Not possible / not reasonable | Not captured — only standard body types considered. ACEA suggests ~0.5% CO2 benefit. |
| Aerodynamics | Adjustable fifth wheel | Contradicting views | Partially captured / Models available | Can be captured by constant-speed test; one respondent disagrees (test doesn't capture this technology). ACEA: can be captured by constant-speed test; alternatively proposes a list of generic air-drag reduction values. No action [fragment — "speed te[st]," "Europe" incomplete]. |
| Aerodynamics | Vehicle redesign | Contradicting views | Simulating | Can be captured by constant-speed test; two respondents disagree, saying the test doesn't capture side-wind effect and thus underestimates potential. ACEA: can be captured. No action [fragment — "speed te[st]" incomplete]. |
| Tires | Wide base single tires | Contradicting views | Partially captured / Models available | Rolling-resistance effect captured; aerodynamic effect not captured since drag determination uses standard tires. No action [fragment — "improvement," "tests" incomplete]. |
| Tires | Low rolling resistance tires | Contradicting views | Simulating | Rolling-resistance effect considered captured, though questions raised on the fraction of LRR tires sold in Europe. No action. |
| Tires | Tire pressure monitor systems | Contradicting views | Partially captured / Models available | Can be captured via a technology-list approach as a generic rolling-resistance impact. ETRMA suggested mandatory TPMS for HDVs at a later stage to help uptake. No action [fragment — "improvement," "approved the tire," "increases" incomplete]. |
| Tires | Automatic tire inflation systems | Contradicting views | Partially captured / Models available | Can be captured via a technology-list approach as a generic rolling-resistance impact. [fragment in source heavily truncated — mentions real-world vs. nominal rolling resistance and "the latter quantified" but exact meaning is incomplete/unclear from source.] |
| Axles and transmission | Automated Manual Transmission (AMT) | Contradicting views | Simulating | All but one respondent consider it captured. No action. |
| Axles and transmission | Continuously Variable Transmission (CVT) | Not simulating | Model work necessary prior to implementation in VECTO | Not captured; appears not relevant for the near future. One gearbox OEM: will not offer CVTs for HDVs in the near future. One respondent: CVT definition should comprehend all CVT and IVT (Infinite Variable Transmission) architectures. No action [fragment — "the future," "possibilit[y]" incomplete]. |
| Axles and transmission | Dual Clutch Transmission (DCT) | Contradicting views | Partially captured / Models available | Efficiency considered captured, but differences in shifting logic/duration not covered. A gearbox OEM: these can be simulated as AT (Automatic Transmission) powershifts. [fragment — mentions differing feedback, prediction, developing a general shifting logic being "very time consuming" — matches Conclusions section text.] |
| Axles and transmission | Additional gear ratios | Simulating | Simulating | Consensus that it's covered. One manufacturer: disengageable axle drive not offered. No action [fragment — mentions "clutches" incomplete]. |
| Axles and transmission | Axle efficiency | Simulating | Simulating | Effect captured in efficiency map (if measured). No action. |
| Axles and transmission | Lubricants | Simulating | Simulating | Effect of transmission lubricant included in the transmission efficiency map test method (options 2–3). No action. |
| Hybrids | Hydraulic hybrids | Contradicting views | Model work necessary prior to implementation in VECTO | ACEA: hydraulic hybrid solutions not (yet) available in the ACEA White Book. No action [fragment — "from ACEA," "by DG Clima" incomplete, consistent with Conclusions section]. |
| Hybrids | Full/mild electric hybrids | Not simulating | Partially captured / Models available | Energy-recuperation and storage system should be developed. Mild hybrids should be captured — expected to gain significance in urban applications. Should investigate electrification of auxiliaries in addition to powertrains. ACEA: not yet covered in VECTO, but ACEA recommends an implementation approach in their **2016 White Book**. [fragment — mentions "addressing," "development," "certification," "a first solution [along the lines of ACEA White] Book," "[contract has] been launched [by DG Clima]," "it [is] difficult" — consistent with Conclusions section text on Electric hybrids.] |
| Hybrids | Flywheel | Not simulating | Partially captured / Models available | [Row cut off in source extraction — no further detail captured before Table 3 continues to next category on the following page.] |
| Mass | Mass reduction | Simulating | Simulating | No action. |
| Idling | Stop-start systems | Contradicting views | Simulating | Consensus it's covered; one respondent expressed the opposite view. No action. |
| Idling | Auxiliary power units | Not simulating | Model work necessary prior to implementation in VECTO | Not captured. ACEA: overnight engine idling in Europe is "very exceptional"; estimated effect 0.1%. No action [fragment — "insignificant" incomplete]. |
| Idling | Neutral idle | Not simulating | Model work necessary prior to implementation in VECTO | Currently not captured. ACEA: not captured, as automatic-transmission modelling is still under development; estimated effect 0.4%. "Re-assess" [fragment — matches Conclusions section: reassess after AT modelling implemented]. |
| Components and auxiliaries | Electric hydraulic power steering | Simulating | Simulating | No action. |
| Components and auxiliaries | LED headlights | Contradicting views | Simulating | Most participants say covered; dissenters gave no justification. No action. |
| Components and auxiliaries | Air compressor | Contradicting views | Simulating | Sufficiently captured, though not all technologies covered. VECTO sufficiently covers mechanically-driven compressors and related tech. VECTO should also consider electrically-driven compressors. One respondent: VECTO should in future also consider pneumatic consumers (brake, gearshift, air suspension) for truck and trailer, to cover these systems' efficiency. ACEA: several technologies captured (the ones easily verified at truck level). No action [fragment — "coverage," "can discuss bus auxiliaries [extension]" incomplete]. |
| Components and auxiliaries | A/C efficiency and refrigerant | Not simulating | Model work necessary prior to implementation in VECTO | Mostly covered for buses/coaches but not trucks. ACEA: A/C efficiency can be captured by extending the auxiliary list if a certification test procedure for system efficiency is determined. No action [fragment — "certificat[ion]," "buses and [coaches, extend]... to trucks" incomplete]. |
| Components and auxiliaries | Reflective paint and glazing | Not simulating | Partially captured / Models available | ACEA: effect not captured for trucks, but could be captured within the HVAC auxiliary model for buses and coaches. No action [fragment — "and coaches" incomplete]. |
| Controls/Energy management | Predictive cruise control | Not simulating | Partially captured / Models available | Not fully captured in VECTO; one vehicle OEM considers these systems covered. ACEA recommends an implementation approach in their **2016 White Book**. [fragment — mentions "request," "implementation," "what exactly [these systems are, as PCC/ADAS terms] are too general," "stakeholders," "CO2 benefit," "implementation has been [proposed as a] long process," "quantified" — consistent with Conclusions section text.] |
| Controls/Energy management | Advanced Driver Assistance Systems | Contradicting views | Partially captured / Models available | Some active control functions not requiring driver interaction are included (e.g. Eco-Roll), but available technologies should be extended. ACEA: effect not captured in VECTO, but recommends an implementation approach in their 2016 White Book. |
| Controls/Energy management | Vehicle Speed limiter | [not specified in survey classification column for this row] | Partially captured / Models available | ACEA: not captured in present VECTO; simple implementation is possible. "Request implementation" [fragment, consistent with Conclusions section]. |

---

## Annex — Table 4: Effect on fuel consumption by technology type, based on respondents' replies
*(Source Table 4, pp.33–35. "Median / Highest / Lowest" are as labelled in the source table header; note the values appear in the source as Median, then two more numeric columns which by position/sign convention read as the higher-magnitude and lower-magnitude reduction estimates. Values are percentages; a negative sign denotes a fuel-consumption **reduction**. "Number of estimates" = how many respondents provided a numeric value for that row.)*

| Category | Technology | Vehicle type | Median | Highest | Lowest | Number of estimates |
|---|---|---|---|---|---|---|
| Engine | Waste heat recovery | Rigid trucks | -3.5% | -5.0% | -2.0% | 1 |
| Engine | Waste heat recovery | Tractor-trailers | -3.5% | -5.0% | -2.0% | 1 |
| Engine | Waste heat recovery | Coaches | -3.0% | -4.0% | -2.0% | 1 |
| Engine | Engine software management optimization | Rigid trucks | -3.5% | -5.0% | -2.0% | 1 |
| Engine | Improved cooling fan | Rigid trucks | -0.5% | -1.0% | 0.0% | 2 |
| Engine | Improved cooling fan | Tractor-trailers | -0.5% | -1.0% | 0.0% | 1 |
| Engine | Improved alternator | Rigid trucks | -0.4% | -0.5% | -0.3% | 1 |
| Engine | Improved alternator | Rigid or Tractor-trailer | — | — | — | [unclear from source] |
| Engine | Improved water pumps | Rigid trucks | -0.8% | -1.0% | -0.5% | 2 |
| Engine | Improved water pumps | Tractor-trailers | -0.8% | -1.0% | -0.5% | 1 |
| Aerodynamics | Active flow control | Rigid trucks | -2.0% | -15.0% | -1.0% | 3 |
| Aerodynamics | Active flow control | Tractor-trailers | -2.5% | -20.0% | -1.0% | 3 |
| Aerodynamics | Active flow control | Coaches | -2.5% | -12.0% | -1.0% | 3 |
| Aerodynamics | External grille shutter | Rigid trucks | -0.5% | -1.0% | 0.0% | 1 |
| Aerodynamics | External grille shutter | Tractor-trailers | -1.0% | -1.5% | -0.5% | 1 |
| Aerodynamics | Roof fairing design | Rigid trucks | -13.0% | -16.0% | -10.0% | 1 |
| Aerodynamics | Roof fairing design | Tractor-trailers | -16.0% | -22.0% | -10.0% | 1 |
| Aerodynamics | Wheel/bogie fairings and side skirts | Rigid trucks | -3.5% | -5.0% | -2.0% | 1 |
| Aerodynamics | Wheel/bogie fairings and side skirts | Tractor-trailers | -4.5% | -5.0% | -4.0% | 1 |
| Aerodynamics | Wheel/bogie fairings and side skirts | Coaches | -1.5% | -2.0% | -1.0% | 1 |
| Aerodynamics | Trailer-mounted extensions | Rigid trucks | [no value given in source] | | | |
| Aerodynamics | Trailer-mounted extensions | Tractor-trailers | [no value given in source] | | | |
| Aerodynamics | Boat tails/extension panels | Rigid trucks | -3.5% | -4.0% | -3.0% | 1 |
| Aerodynamics | Boat tails/extension panels | Tractor-trailers | -3.5% | -4.0% | -3.0% | 1 |
| Aerodynamics | Boat tails/extension panels | Coaches | -4.5% | -5.0% | -4.0% | 1 |
| Aerodynamics | Vortex generators | Rigid trucks | -0.5% | -1.0% | 0.0% | 2 |
| Aerodynamics | Vortex generators | Tractor-trailers | -0.5% | -1.0% | 0.0% | 2 |
| Aerodynamics | Complete vehicle redesign | Rigid trucks | -2.5% | -3.0% | -2.0% | 1 |
| Aerodynamics | Complete vehicle redesign | Tractor-trailers | -5.0% | -7.0% | -3.0% | 1 |
| Aerodynamics | Complete vehicle redesign | Coaches | -5.5% | -8.0% | -3.0% | 1 |
| Axles and Transmission | AMT | Rigid trucks | -0.5% | -1.0% | 0.0% | 1 |
| Axles and Transmission | AMT | Tractor-trailers | -0.5% | -1.0% | 0.0% | 1 |
| Axles and Transmission | AMT | Coaches | -0.5% | -1.0% | 0.0% | 1 |
| Hybrids | Hydraulic hybrid | Rigid trucks | -3.5% | -5.0% | -2.0% | 1 |
| Hybrids | Full electric hybrids | Rigid trucks | -6.0% | -8.0% | -4.0% | 1 |
| Hybrids | Mild electric hybrids | Rigid trucks | -2.0% | -3.0% | -1.0% | 1 |
| Idling | Idle control technologies | Rigid or Tractor-trailer | [no value given in source] | | | |
| Idling | Neutral idle | Rigid or Tractor-trailer | [no value given in source] | | | |
| Components and auxiliaries | A/C system efficiency | Rigid or Tractor-trailer | [no value given in source] | | | |
| Components and auxiliaries | High efficiency exterior lighting | Rigid trucks | -0.4% | -0.5% | -0.3% | 1 |
| Components and auxiliaries | Air compressor | Rigid trucks | -0.4% | -0.5% | -0.3% | 1 |

> Rows marked "[no value given in source]" correspond to technology/vehicle-type combinations listed in Table 4's row structure but for which the extracted text contained no numeric percentage (i.e., the source table itself left these cells blank — likely because no respondent provided a quantitative estimate for that combination).

---

## Annex — Table 5: Technology market penetration
*(Source Table 5, pp.36–37. "Current market penetration" and "Expected market penetration in 5–10 years" use ACEA/respondent-defined bands: Innovation <3%, Low 3–10%, Developing 11–30%, Established 31–60%, Standard ≥61%. "Responses" = number of respondents providing an estimate for that row.)*

| Category | Technology | Current market penetration | Expected market penetration (5–10 yrs) | Responses |
|---|---|---|---|---|
| Engine | Electrical turbocompound | Innovation <3% | Low 3–10% | 1 |
| Engine | Improvements in intake/outtake system | Innovation <3% | Low 3–10% | 1 |
| Engine | Waste heat recovery | Innovation <3% | Low 3–10% | 2 |
| Engine | ECU optimization | Low 3–10% | Low 3–10% | 1 |
| Engine | Cooling fan | Developing 11–30% | Standard ≥61% | 1 |
| Engine | Improved alternator | Developing 11–30% | Established 31–60% | 1 |
| Engine | Improved water pump | Low 3–10% | Developing 11–30% / Established 31–60% / Standard ≥61% [range as given in source] | 2 |
| Aerodynamics | Active flow control systems | Innovation <3% | Innovation <3% | 1 |
| Aerodynamics | External grille shutters | Innovation <3% | Low 3–10% | 1 |
| Aerodynamics | Roof fairings | Established 31–60% | Standard ≥61% | 1 |
| Aerodynamics | Trailer mounted extensions | Low 3–10% | Developing 11–30% | 1 |
| Aerodynamics | Boat tails | Innovation <3% | Developing 11–30% | 1 |
| Aerodynamics | Vortex generators | Innovation <3% | Innovation <3% | 1 |
| Aerodynamics | Complete vehicle redesign | Innovation <3% | Low 3–10% | 1 |
| Axles and transmission | AMT | Established 31–60% | Established 31–60% | 1 |
| Axles and transmission | CVT | Innovation <3% | Innovation <3% | 1 |
| Hybrids | Hydraulic hybrid | Innovation <3% | Innovation <3% | [unclear from source — no count given] |
| Hybrids | Full electric hybrid | Innovation <3% | Low 3–10% | 2 |
| Hybrids | Full electric hybrid (**Buses**, separate sub-row) | Buses: Low 3–10% | Buses: Developing 11–30% | 2 |
| Hybrids | Mild electric hybrid | Low 3–10% | Developing 11–30% | 1 |
| Components and auxiliaries | LED lighting | Developing 11–30% | Established 31–60% | 1 |
| Components and auxiliaries | Improvements in air compressor | Developing 11–30% | Established 31–60% | 1 |
| Components and auxiliaries | Predictive cruise control | Developing 11–30% | Established 31–60% | 1 |

> Table caption in source: "Technology market penetration. Expected market share change is highlighted" — the source PDF used cell highlighting/shading to flag rows with an expected step-change in market band; this formatting was not recoverable in text extraction, so no shading distinction is reproduced here.

---

## Standards, regulations, and organizations referenced
- **VECTO** — Vehicle Energy Consumption Calculation Tool, developed by the European Commission for HDV CO2 certification (described as the intended "backbone of the future European fuel consumption and CO2 emissions certification procedure for HDVs in Europe").
- **ACEA** — European Automobile Manufacturers' Association (responded collectively for vehicle manufacturers; issued a "2016 White Book" referenced multiple times regarding proposed hybrid/PCC/ADAS implementation approaches).
- **CLEPA** — European Association of Automotive Suppliers (proposed consultee for alternator certification procedure).
- **ETRMA** — European Tyre & Rubber Manufacturers' Association (proposed consultee for wide-base tire feedback; also suggested mandatory TPMS at a later stage).
- **DG Clima** — European Commission Directorate-General for Climate Action (had already launched a contract on Electric hybrids / referenced also for Hydraulic hybrids feedback framework).
- **US EPA (Environmental Protection Agency)** and **US Department of Transportation** — cited extensively as source of literature-review technology effect estimates ("Proposed Rulemaking for Greenhouse Gas Emissions and Fuel Efficiency Standards for Medium- and Heavy-Duty Engines and Vehicles – Phase 2," EPA-420-D-15-900, 2015).
- **NHTSA** — National Highway Traffic Safety Administration (cited via Reinhart 2015 "Commercial Medium- and Heavy-Duty Truck Fuel Efficiency Technology Study," DOT HS 812 146).
- **ICCT** — International Council on Clean Transportation (Rachel Muncrief, Oscar Delgado credited in Acknowledgements for feedback on technology list/questionnaire structure).
- **NACFE** — North American Council for Freight Efficiency ("Trucking Efficiency" reports cited repeatedly in Table 2/references, e.g., on wide-base tires, TPMS, 6x2 axles, lightweighting, downspeeding, electronic engine parameters).
- **JRC** — Joint Research Centre, European Commission (publisher).
- **TUG** — Technical University of Graz (cited: Hausberger et al. 2011 trailer/tire test-procedure evaluation).
- **Umweltbundesamt (German Federal Environment Agency)** — Dünnebeil et al. 2015 "Future Measures for Fuel Savings and GHG Reduction of Heavy-Duty Vehicles" (UBA-FB 002058), a frequently-cited EU data source in Table 2.

## Abbreviations (from source "List of abbreviations and definitions," p.43)
| Abbreviation | Definition |
|---|---|
| A/C | Air conditioning |
| ACEA | European Automobile Manufacturers' Association |
| ADAS | Advanced Driving Assistance Systems |
| AMT | Automated Manual Transmission |
| AT | Automatic Transmission |
| BSFC | Brake Specific Fuel Consumption |
| CLEPA | European Association of Automotive Suppliers |
| CVT | Continuously Variable Transmission |
| DCT | Dual Clutch Transmission |
| ECU | Engine Control Unit |
| ETRMA | European Tyre & Rubber Manufacturers' Association |
| FC | Fuel Consumption |
| FE | Fuel Economy |
| HDV | Heavy-Duty Vehicle |
| HVAC | Heating Ventilation Air Conditioning |
| IVT | Infinite Variable Transmission |
| JRC | Joint Research Centre |
| LED | Light-Emitting Diode |
| OEM | Original Equipment Manufacturer |
| PCC | Predictive Cruise Control |
| PEM | Portable Emissions Measurement |
| PM | Particulate Matter |
| RRC | Rolling Resistance Coefficient |
| TPMS | Tire Pressure Monitoring System |
| TUG | Technical University of Graz |
| VECTO | Vehicle Energy Consumption Calculation TOol |
| WHR | Waste Heat Recovery |
| WHTC | World Harmonized Test Cycle |

## List of figures (source, p.44)
- Figure 1: Number of respondents by technology category and breakdown by respondent affiliation (p.7)
- Figure 2: Individual technologies were separated into three categories depending on the simulation capabilities of VECTO (p.8)

## List of tables (source, p.45)
- Table 1: List of technologies by category (p.5)
- Table 2: Literature review of technologies reducing fuel consumption in heavy-duty vehicles (p.14)
- Table 3: Summary of the VECTO capabilities based on respondent feedback and proposed action (p.27)
- Table 4: Effect on fuel consumption by technology type based on respondents' replies (p.33)
- Table 5: Technology market penetration. Expected market share change is highlighted (p.36)

## Full reference list (source, pp.38–42)
1. Agnolucci, Paolo. 2007. "Prospects of Fuel Cell Auxiliary Power Units in the Civil Markets." *International Journal of Hydrogen Energy*, Fuel Cells, 32(17): 4306–18. doi:10.1016/j.ijhydene.2007.05.017.
2. ATDynamics. 2011. "Fuel-Efficient Active Flow Control for Tractor Trailers." ICAT Grant No. 08-1.
3. Baker, Rick, Richard Billings, Birgit Caliandro, Mike Sabisch, Alan Stanard, and Jim Lindner. 2015. "Global Green Freight Action Plan - Technical Background Report." ERG Project No.: 0303.02.012.002. Eastern Research Group.
4. Bender, Frank A., Thomas Bosse, and Oliver Sawodny. 2014. "An Investigation on the Fuel Savings Potential of Hybrid Hydraulic Refuse Collection Vehicles." *Waste Management* 34(9): 1577–83. doi:10.1016/j.wasman.2014.05.022.
5. Boretti, Alberto. 2010. "Improvements of Truck Fuel Economy Using Mechanical Regenerative Braking." doi:10.4271/2010-01-1980.
6. Bridgestone Tires. 2014. "Ecopia - Our New Generation of Fuel Efficient Tyres."
7. Brockbank, Chris, and Chris Greenwood. 2009. "Fuel Economy Benefits of a Flywheel CVT Based Mechanical Hybrid for City Bus and Commercial Vehicle Applications." *SAE International Journal of Commercial Vehicles* 2(2): 115–22. doi:10.4271/2009-01-2868.
8. Brodrick, Christie-Joy, Timothy E. Lipman, Mohammad Farshchi, Nicholas P. Lutsey, Harry A. Dwyer, Daniel Sperling, III Gouse S. William, D. Bruce Harris, and Foy G. King Jr. 2002. "Evaluation of Fuel Cell Auxiliary Power Units for Heavy-Duty Diesel Trucks." *Transportation Research Part D: Transport and Environment* 7(4): 303–15. doi:10.1016/S1361-9209(01)00026-8.
9. Buresti, G., G.V. Iungo, and G. Lombardi. 2007. "Methods for the Drag Reduction of Bluff Bodies and Their Application to Heavy Road-Vehicles." DDIA 2007-6. 1st Interim Report.
10. Burtt, David J. 2007. "Fuel Economy Benefits of a High Torque Infinitely Variable Transmission for Commercial Vehicles." doi:10.4271/2007-01-4206.
11. Continental. 2015. "ContiPressureCheck - The Tyre Pressure Monitoring System."
12. Cummins. n.d. "Cummins MPG Guide. Secrets of Better Fuel Economy - The Physics of MPG."
13. Daccord, Rémi, Antoine Darmedru, and Julien Melis. 2014. "Oil-Free Axial Piston Expander for Waste Heat Recovery." doi:10.4271/2014-01-0675.
14. de Oliveira, Leonardo Alencar, Marcio de Almeida D'Agosto, Vicente Aprigliano Fernandes, and Cíntia Machado de Oliveira. 2014. "A Financial and Environmental Evaluation for the Introduction of Diesel-Hydraulic Hybrid-Drive System in Urban Waste Collection." *Transportation Research Part D: Transport and Environment* 31(August): 100–109. doi:10.1016/j.trd.2014.05.021.
15. Duleep, K.G. 2011. "Heavy Duty Truck Fuel Economy: Technology and Testing." Presented at Michelin Bibendum, Berlin, May.
16. Dünnebeil, Frank, Carsten Reinhard, Udo Lambrecht, Antonius Kies, Stefan Hausberger, and Martin Rexeis. 2015. "Future Measures for Fuel Savings and GHG Reduction of Heavy-Duty Vehicles." (UBA-FB) 002058. Dessau-Roßlau: Umweltbundesamt.
17. EPA. 2015. "Low-Viscosity Lubricants - A Glance at Clean Freight Strategies." www.epa.gov/smartway.
18. EPA. "Weight Reduction: A Glance at Clean Freight Strategies."
19. EPA, and Department of Transport. 2015. "Proposed Rulemaking for Greenhouse Gas Emissions and Fuel Efficiency Standards for Medium- and Heavy-Duty Engines and Vehicles–Phase 2." EPA-420-D-15-900.
20. Gao, Zhiming, Charles Finney, Charles Daw, Tim J. LaClair, and David Smith. 2014. "Comparative Study of Hybrid Powertrains on Fuel Saving, Emissions, and Component Energy Loss in HD Trucks." *SAE International Journal of Commercial Vehicles* 7(2): 414–31. doi:10.4271/2014-01-2326.
21. Gao, Zhiming, David E. Smith, C. Stuart Daw, K. Dean Edwards, Brian C. Kaul, Norberto Domingo, James E. Parks II, and Perry T. Jones. 2015. "The Evaluation of Developing Vehicle Technologies on the Fuel Economy of Long-Haul Trucks." *Energy Conversion and Management* 106(December): 766–81. doi:10.1016/j.enconman.2015.10.006.
22. Goodyear. 2012. "Factors Affecting Truck Fuel Economy." Brochure, April 20.
23. Hausberger, Stefan, Martin Rexeis, Jürgen Blassnegger, and Silberholz Gerard. 2011. "Evaluation of Fuel Efficiency Improvements in the Heavy-Duty Vehicle (HDV) Sector from Improved Trailer and Tire Designs by Application of a New Test Procedure." I-24/2011 Hb-Em 18/11/679. TUG.
24. Hill, Nikolas, John Norris, Felix Kirsch, Craig Dun, Neil McGregor, Enrico Pastori, and Ian Skinner. 2015. "Light Weighting as a Means of Improving Heavy Duty Vehicles' Energy Efficiency and Overall CO2 Emissions." ED59243. Heavy Duty Vehicles Framework Contract – Service Request 2. Didcot, UK: Ricardo-AEA.
25. Holmberg, Kenneth, Peter Andersson, Nils-Olof Nylund, Kari Mäkelä, and Ali Erdemir. 2014. "Global Energy Consumption due to Friction in Trucks and Buses." *Tribology International* 78(October): 94–114. doi:10.1016/j.triboint.2014.05.004.
26. LaClair, Tim J., and Russell Truemner. 2005. "Modelling of Fuel Consumption for Heavy-Duty Trucks and the Impact of Tire Rolling Resistance." SAE International.
27. Lajunen, Antti. 2014. "Fuel Economy Analysis of Conventional and Hybrid Heavy Vehicle Combinations over Real-World Operating Routes." *Transportation Research Part D: Transport and Environment* 31(August): 70–84. doi:10.1016/j.trd.2014.05.023.
28. Lammert, Michael P., Jonathan Burton, Petr Sindler, and Adam Duran. 2014. "Hydraulic Hybrid and Conventional Parcel Delivery Vehicles' Measured Laboratory Fuel Economy on Targeted Drive Cycles." *SAE International Journal of Alternative Powertrains* 4(1). doi:10.4271/2014-01-2375.
29. Landman, Drew, Matthew Cragun, Mike McCormick, and Richard Wood. 2011. "Drag Reduction of a Modern Straight Truck." *SAE International Journal of Commercial Vehicles* 4(1): 256–62. doi:10.4271/2011-01-2283.
30. Lustbader, Jason Aaron, Cory Kreutzer, Matthew A. Jeffers, Steven Adelman, Skip Yeakel, Philip Brontz, Kurt Olson, and James Ohlinger. 2014. "Impact of Paint Color on Rest Period Climate Control Loads in Long-Haul Trucks." doi:10.4271/2014-01-0680.
31. Macián, V., J. R. Serrano, V. Dolz, and J. Sánchez. 2013. "Methodology to Design a Bottoming Rankine Cycle, as a Waste Energy Recovering System in Vehicles. Study in a HDD Engine." *Applied Energy* 104(April): 758–71. doi:10.1016/j.apenergy.2012.11.075.
32. McCarthy, James, Timothy Korhumel, and Andrew Marougy. 2009. "Performance of a Fuel Reformer, LNT and SCR Aftertreatment System Following 500 LNT Desulfation Events." *SAE International Journal of Commercial Vehicles* 2(2): 34–44. doi:10.4271/2009-01-2835.
33. Michelin Trucks. 2012. "Michelin White Book."
34. Midgley, W., H. Cathcart, and D. Cebon. 2013. "Modelling of Hydraulic Regenerative Braking Systems for Heavy Vehicles." *Proceedings of the Institution of Mechanical Engineers, Part D: Journal of Automobile Engineering* 227(7): 1072–84. doi:10.1177/0954407012469168.
35. Mohamed-Kassim, Zulfaa, and Antonio Filippone. 2010. "Fuel Savings on a Heavy Vehicle via Aerodynamic Drag Reduction." *Transportation Research Part D: Transport and Environment* 15(5): 275–84. doi:10.1016/j.trd.2010.02.010.
36. NACFE. 2010. "Executive Report - Wide Base Tires." ER1002.
37. NACFE. 2013. "Tire Pressure Systems."
38. Nieman, Andy. 2014. "The Right Solution for Downsped Engines." Dana Limited.
39. Park, Jim. 2014. "Making the Case for Low-Rolling-Resistance Tires." February.
40. Patidar, Ashok, Umashanker Gupta, and Ankur Bansal. 2015. "Fuel Efficiency Improvement of Commercial Vehicle by Investigating Drag Resistance." doi:10.4271/2015-01-2893.
41. Patten, Jeff, Brian McAuliffe, William Mayda, and Bernard Tanguay. 2012. "Review of Aerodynamic Drag Reduction Devices for Heavy Trucks and Buses." CSTT-HVC-TR-205. Ottawa: National Research Council Canada.
42. Rahman, S. M. Ashrafur, H. H. Masjuki, M. A. Kalam, M. J. Abedin, A. Sanjid, and H. Sajjad. 2013. "Impact of Idling on Fuel Consumption and Exhaust Emissions and Available Idle-Reduction Technologies for Diesel Vehicles – A Review." *Energy Conversion and Management* 74(October): 171–82. doi:10.1016/j.enconman.2013.05.019.
43. Reinhart, Thomas. 2015. "Commercial Medium- and Heavy-Duty Truck Fuel Efficiency Technology Study - Report #1." DOT HS 812 146. National Highway Traffic Safety Administration.
44. Ricardo. 2009. "The Science of Spin."
45. Schoettle, Brandon, Michael Sivak, and Yoshihiro Fujiyama. 2008. *LEDs and Power Consumption of Exterior Automotive Lighting: Implications for Gasoline and Electric Vehicles*. University of Michigan, Transportation Research Institute.
46. Schubert, Raymond, and Matt Kromer. 2008. "Heavy-Duty Truck Retrofit Technology: Assessment and Regulatory Approach." Cupertino, CA: TIAX LLC.
47. Seifert, A., O. Stalnov, D. Sperber, G. Arwatz, V. Palei, S. David, I. Dayan, and I. Fono. 2016. "Large Trucks Drag Reduction Using Active Flow Control."
48. Storey, John M. E., John F. Thomas, Samuel A. Lewis, Thang Q. Dam, K. Dean Edwards, Gerald L. Devault, and Dominic J. Retrossa. 2003. "Particulate Matter and Aldehyde Emissions from Idling Heavy-Duty Diesel Trucks." doi:10.4271/2003-01-0289.
49. Surcel, Marius-Dorin, Yves Provencher, and Jan Michaelsen. 2009. "Fuel Consumption Track Tests for Tractor-Trailer Fuel Saving Technologies." *SAE International Journal of Commercial Vehicles* 2(2): 191–202. doi:10.4271/2009-01-2891.
50. Taylor, Robert, K. Selby, R. Herrera, and D. A. Green. 2011. "The Effect of Engine, Axle and Transmission Lubricant, and Operating Conditions on Heavy Duty Diesel Fuel Economy: Part 2: Predictions." *SAE International Journal of Fuels and Lubricants* 5(1): 488–95. doi:10.4271/2011-01-2130.
51. T&E (Transport & Environment). 2010. "The Case for the Exemption of Aerodynamic Devices in Future Type-Approval Legislation for Heavy Goods Vehicles." Brussels.
52. T&E. 2012. "Smart, Safer, Cleaner: How Small Changes to Lorry Design Can Make a Big Difference."
53. Total Lubricants. 2015. "Reduce Truck's Fuel Consumption."
54. Total Lubricants. 2016. "Total Fuel Economy Lubricants."
55. Trucking Efficiency. 2013. "Confidence Findings on the Potential of 6x2 Axles." NACFE.
56. Trucking Efficiency. 2015a. "Trucking Efficiency Confidence Report: Lightweighting Executive Summary."
57. Trucking Efficiency. 2015b. "Confidence Report: Electronic Engine Parameters - Executive Summary."
58. Trucking Efficiency. 2015c. "Trucking Efficiency Confidence Report: Downspeeding."
59. Vaja, Iacopo, and Agostino Gambarotta. 2010. "Internal Combustion Engine (ICE) Bottoming with Organic Rankine Cycles (ORCs)." *Energy*, ECOS 2008 21st International Conference, 35(2): 1084–93. doi:10.1016/j.energy.2009.06.001.
60. Van Batavia, Brian L. 2009. "Hydraulic Hybrid Vehicle Energy Management System." doi:10.4271/2009-01-2834.
61. Volvo. 2016. "Volvo Trucks XE Packages."
62. Volvo Trucks. 2016. "Every Drop Counts - Air Flow Package."
63. WABCO. 2016. "Advanced Driver Assistance Systems."
64. Zhao, Hengbing, Andrew Burke, and Marshall Miller. 2013. "Analysis of Class 8 Truck Technologies for Their Fuel Savings and Economics." *Transportation Research Part D: Transport and Environment* 23(August): 55–63. doi:10.1016/j.trd.2013.04.004.

---

## Relevance to the HDEV sizing & modelling tool project

These are observations drawn directly from the source document's stated content — flagged as interpretive where they extend beyond a literal restatement:

1. **VECTO's core simulation architecture (as implied, not fully detailed, in this report) is a backward-looking, engine-map-based simulator.** Respondents explicitly noted that "backward simulation is not adequate for capturing the effect of" waste heat recovery, and the report states that fully capturing electric hybrids "might require in the future transition to a forward-looking model which would require a complete redesign of VECTO software." **[This is the report's own statement, not this assistant's inference]** — it is directly relevant to design choices for a new HDEV tool, since forward-looking (causal, driver-model-in-the-loop) simulation is generally needed to properly represent battery/energy-storage dynamics, which map-based backward simulation struggles with.
2. **Electrical path / energy storage modelling was identified in 2016 as VECTO's key gap**, specifically: "design of the electrical paths especially in the case of handling restored energy" and "electrically powered/controlled component options are not adequately simulated compared to the mechanical counterparts." This is a direct, source-stated pointer to what a next-generation (fully electric) sizing tool needs to do differently/better: model electrical energy paths, recuperation, and storage explicitly rather than as a generic map/discount factor.
3. **VECTO's technology-representation methods, as characterized by respondents/ACEA, fall into a few patterns worth reusing conceptually for an HDEV tool:** (a) steady-state component efficiency/loss **maps** (engine, axle, transmission) — sufficient for steady conditions, contested for transient; (b) **generic technology-list discount factors** (fixed % CO2/FC benefit applied when a technology is present) — used for things like alternators, fans, mirrors; (c) **modified physical test procedures** (e.g., constant-speed air-drag test, engine-map test) to capture a technology's physical effect directly.
4. **This document is silent on BEV/FCEV powertrain simulation, charging behavior, depot/fleet-level modelling, or battery sizing** — these are not addressed at all in this 2016 report and nothing here should be used as a source for those topics. If those topics are needed, VECTO's later versions (post-2019, which added electric/hybrid powertrain modules) or other JRC/VECTO documentation would need to be separately sourced and reviewed — this has not been done here.
5. **ACEA's "2016 White Book"** is referenced multiple times as containing ACEA's proposed implementation approach for electric hybrids, PCC, and ADAS in VECTO — this could be a valuable primary source to locate if deeper detail on early industry-proposed hybrid/electric simulation methodology is wanted; it is not itself in this project's knowledge base and was not reviewed here.
