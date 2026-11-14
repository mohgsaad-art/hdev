# Commission Regulation (EU) 2017/2400 — Annex I: Vehicle Classification & Heavy Bus CO2/Fuel Consumption Method

**CELEX number:** 02017R2400
**Consolidated text as of:** 01.01.2026 (consolidated version 007.001)
**Covers:** ANNEX I — "Classification of vehicles in vehicle groups and method to determine CO2 emissions and fuel consumption for heavy buses" (point 1 — classification tables for lorries/tractors/buses; point 2 — heavy-bus staged simulation method)

> Table reconstruction caveat (read before using the tables below): Tables 1, 2, 4, 5 and 6 in the source are two-dimensional matrices (vehicle configuration rows × mission-profile columns, with "x" marks and footnoted codes) that were flattened by OCR into linear text, with the multi-row column headers ("Long haul / Long haul EMS / Regional delivery / Regional delivery EMS / Urban delivery / Municipal utility / Construction" for lorries; "Heavy Urban / Urban / Suburban / Interurban / Coach" for buses) losing their exact per-cell alignment in several rows. I have reconstructed these as faithfully as the linear OCR text allows, but **the exact mapping of which "x" belongs to which specific mission-profile column in some rows could not be reconstructed with full certainty from text alone** — this is flagged per-table below. For anything load-bearing (e.g. programmatically assigning a vehicle group to a mission profile), cross-check the reconstructed table against the original PDF's actual grid/figure. Table 3 and Table 7 were reconstructed with higher confidence (simpler structure); Table 7 is a clean two-column mapping with no ambiguity.

---

## 1. Classification of the vehicles for the purpose of this Regulation

### 1.1 Classification of vehicles of category N

#### Table 1 — Vehicle groups for heavy lorries
*(replaced in its entirety by ►M4; rows for 4×4, 6×6, 8×2, 8×6, 8×8 and 5-axle configurations show vehicle-group numbers only, with mission-profile/body data not populated in the source text — these rows are genuinely sparse in the source, not an extraction gap)*

Columns, as given in the source header: **Axle configuration | Chassis configuration | Technically permissible maximum laden mass (tons) | Vehicle group | Long haul | Long haul EMS* | Regional delivery | Regional delivery EMS* | Urban delivery | Municipal utility | Construction**

| Axle config. | Chassis configuration | Max laden mass (t) | Vehicle group | Mission-profile marks as extracted (order: Long haul, Long haul EMS, Regional delivery, Regional delivery EMS, Urban delivery, Municipal utility, Construction) |
|---|---|---|---|---|
| 4×2 | Rigid lorry (or tractor)** | >7.4–7.5 | **1s** | "R R" (2 marks extracted — exact columns uncertain, see caveat) |
| 4×2 | Rigid lorry (or tractor)** | >7.5–10 | **1** | "R R" |
| 4×2 | Rigid lorry (or tractor)** | >10–12 | **2** | "R+T1 R R" |
| 4×2 | Rigid lorry (or tractor)** | >12–16 | **3** | "R R" |
| 4×2 | Rigid lorry | >16 | **4** | "R+T2 R R R R" |
| 4×2 | Tractor | >16 | **5** | "T+ST T+ST+T2 T+ST T+ST+T2 T+ST T+ST" |
| 4×4 | Rigid lorry | >7.5–16 | **(6)** | — (no mission-profile data shown in source; group number only) |
| 4×4 | Rigid lorry | >16 | **(7)** | — |
| 4×4 | Tractor | >16 | **(8)** | — |
| 6×2 | Rigid lorry, all weights | **9** | "R+T2 R+D+ST R R+D+ST R R" |
| 6×2 | Tractor, all weights | **10** | "T+ST T+ST+T2 T+ST T+ST+T2 T+ST" |
| 6×4 | Rigid lorry, all weights | **11** *(►M3)* | "R+T2 R+D+ST R R+D+ST R R" |
| 6×4 | Tractor, all weights | **12** *(►M3)* | "T+ST T+ST+T2 T+ST T+ST+T2 T+ST" |
| 6×6 | Rigid lorry, all weights | **(13)** | — |
| 6×6 | Tractor, all weights | **(14)** | — |
| 8×2 | Rigid lorry, all weights | **(15)** | — |
| 8×4 | Rigid lorry, all weights | **16** *(►M3)* | "R+T2 R+D+ST R R+D+ST R" |
| 8×6 / 8×8 | Rigid lorry, all weights | **(17)** | — |
| 8×2 / 8×4 / 8×6 / 8×8 | Tractor, all weights | **(18)** | — |
| 5 axles, all configs | Rigid lorry or tractor, all weights | **(19)** | — |

**Footnotes to Table 1:**
- (*) EMS = European Modular System.
- (**) "In these vehicle classes tractors are treated as rigid lorries but with specific curb weight of tractor."
- **T** = Tractor; **R** = Rigid lorry & standard body; **T1, T2** = standard trailers; **ST** = standard semitrailer; **D** = standard dolly.

**Legal consequence reminder (from Article 4, second paragraph):** vehicle groups **6, 7, 8, 13, 14, 15, 17, 18, 19** (the ones shown above with "( )" around the group number and no mission-profile data populated) are **excluded from Articles 5–23** of the Regulation — i.e. excluded from the licensing/certification/conformity machinery, even though they are formally classified here. Likewise, any vehicle with a **driven front axle** in groups **11, 12, 16** is excluded.

#### Table 2 — Vehicle groups for medium lorries
*(introduced/replaced by ►M4)*

| Drive config. | Chassis configuration | Vehicle group | Mission-profile marks as extracted |
|---|---|---|---|
| FWD / 4×2F | Rigid Lorry (or tractor) | **(51)** | — (no data populated in source) |
| FWD / 4×2F | Van | **(52)** | — |
| RWD / 4×2 | Rigid Lorry (or tractor) | **53** | "R R" |
| RWD / 4×2 | Van | **54** | "I I" |
| AWD / 4×4 | Rigid Lorry (or tractor) | **(55)** | — |
| AWD / 4×4 | Van | **(56)** | — |

**Footnotes to Table 2:**
- (*) EMS = European Modular System.
- **R** = Standard body; **I** = Van with its integrated body; **FWD** = Front wheel driven; **RWD** = Single driven axle which is not the front axle; **AWD** = More than a single driven axle.

**Legal consequence reminder (Article 4, second paragraph):** vehicle groups **51, 52, 55, 56** (medium lorries, all shown with no mission-profile data populated) are **excluded from Articles 5–23**.

### 1.2. Classification of vehicles of category M

#### 1.2.1. Heavy buses
(Heading only in source — introductory, no body text directly under it before 1.2.2 begins.)

#### 1.2.2. Classification of primary vehicles

**Table 3 — Vehicle groups for primary vehicles**
*(as amended by ►M3)*

Columns: Number of axles | Articulated (yes/no) | Low floor (LF) / High floor (HF) | Number of decks (SD/DD) | **Vehicle group** | Vehicle subgroup | Mission profile allocation (Heavy Urban / Urban / Suburban / Interurban / Coach)

| Axles | Articulated | Floor | Deck | Vehicle group (P-code) | Subgroup | Mission profiles marked "x" (as extracted, in order Heavy Urban–Urban–Suburban–Interurban–Coach) |
|---|---|---|---|---|---|---|
| 2 | no | LF | SD | **P31** | SD | x x x x *(4 of 5 — see caveat on exact column)* |
| 2 | no | LF | DD | **P31** | DD | x x x *(3 of 5)* |
| 2 | no | HF | SD | **P32** | SD | x x *(2 of 5)* |
| 2 | no | HF | DD | **P32** | DD | x x *(2 of 5)* |
| 3 | no | LF | SD | **P33** | SD | x x x x |
| 3 | no | LF | DD | **P33** | DD | x x x |
| 3 | no | HF | SD | **P34** | SD | x x |
| 3 | no | HF | DD | **P34** | DD | x x |
| 3 | yes | LF | SD | **P35** | SD | x x x x |
| 3 | yes | LF | DD | **P35** | DD | x x x |
| 3 | yes | HF | SD | **P36** | SD | x x |
| 3 | yes | HF | DD | **P36** | DD | x x |
| 4 | no | LF | SD | **P37** | SD | x x x x |
| 4 | no | LF | DD | **P37** | DD | x x x |
| 4 | no | HF | SD | **P38** | SD | x x |
| 4 | no | HF | DD | **P38** | DD | x x |
| 4 | yes | LF | SD | **P39** | SD | x x x x |
| 4 | yes | LF | DD | **P39** | DD | x x x |
| 4 | yes | HF | SD | **P40** | SD | x x |
| 4 | yes | HF | DD | **P40** | DD | x x |

**Footnotes to Table 3:**
1. "'P' indicates the primary stage of the classification; the two numbers separated by the slash indicate the numbers for vehicle groups the vehicle can be allocated in the complete or completed stage." (E.g. the header group "P31/32" in the raw source groups the P31 and P32 rows together under one classification cell before the LF/HF split.)
2. "'Low floor' means vehicle codes 'CE', 'CF', 'CG', 'CH', as set out in point 3 of part C of Annex I to Regulation (EU) 2018/858. 'High floor' means vehicle codes 'CA', 'CB', 'CC', 'CD', as set out in point 3 of part C of Annex I to Regulation (EU) 2018/858."
3. "'SD' means single deck vehicle, 'DD' means double deck."

**Important consequence (for sizing-tool logic):** a primary heavy bus is classified by only **3 criteria**: number of axles (2/3/4), articulated (yes/no), and ultimately simulated across **4 generic bodies** (HF/LF × SD/DD) and **11 mission profiles**, producing **22 results** (see point 2.3 below) — this is a materially simpler classification than the complete/completed-vehicle stage (6 criteria, see 1.2.3).

#### 1.2.3. Classification of complete vehicles or completed vehicles

The classification of complete or completed heavy buses is based on **six criteria**:
(a) Number of axles;
(b) Vehicle code (Annex I, Part C, point 3, Regulation (EU) 2018/858);
(c) Class of vehicle per paragraph 2 of **UN Regulation No. 107** of the UNECE ("Uniform provisions concerning the approval of category M2 or M3 vehicles with regard to their general construction", OJ L 52, 23.2.2018, p. 1);
(d) **Low entry vehicle** (yes/no, derived from vehicle code and type of axle) — determined per the decision flow in **Figure 1**;
(e) Number of passengers in the **lower deck**, from the Certificate of Conformity (per Annex VIII to Commission Implementing Regulation (EU) 2020/683 of 15 April 2020, OJ L 163, 26.5.2020, p. 1) or equivalent documents for individual vehicle approval;
(f) **Height of the integrated body**, determined per Annex VIII [to this Regulation — i.e. the Air Drag annex, outside this file's range].

> **[Figure referenced in source but not visually extracted from this text-only OCR — consult the original PDF if the diagram is needed.]** "Figure 1 — Decision flow to determine whether a vehicle is 'low entry' or not" is referenced immediately after criterion (d) above but the flowchart itself did not survive text extraction (the OCR text simply states "Figure 1" followed directly by "Decision flow to determine whether a vehicle is 'low entry' or not:" with no decision-tree content visible). This is a logic-critical diagram for anyone implementing the classification programmatically — it must be obtained from the source PDF.

The resulting classification tables are **Table 4** (2-axle buses), **Table 5** (3-axle buses) and **Table 6** (4-axle buses).

**Table 4 — Vehicle groups for complete vehicles and completed vehicles that are heavy buses with 2 axles**

Columns (per source header): Number of Axles | Chassis configuration (explanation only) | Vehicle Code* | Class of vehicle** (I / I+II or A / II / II+III / III or B) | Low Entry (CE/CG only) | Passenger seats in lower deck (CB/CD only) | Height of integrated body [mm] (Class II+III only) | **Vehicle group** | Mission profile (Heavy Urban / Urban / Suburban / Interurban / Coach)

| Axles | Chassis config | Vehicle Code | Class-of-vehicle marks | Low entry | Pax lower deck | Height [mm] | Vehicle group | Mission-profile marks (as extracted) |
|---|---|---|---|---|---|---|---|---|
| 2, rigid | LF, SD | CE | I, I+II/A, II marked ("x x x") | no | — | — | **31a** | x x x |
| 2, rigid | LF, SD | CE | I, I+II/A marked ("x x") | yes | — | — | **31b1** | x x x |
| 2, rigid | LF, SD | CE | I marked ("x") | yes | — | — | **31b2** | x x x x |
| 2, rigid | LF, DD | CF | I, I+II/A, II marked ("x x x") | — | — | — | **31c** | x x x |
| 2, rigid | LF open top, SD | CI | I, I+II/A, II, II+III, III/B marked ("x x x x x") | — | — | — | **31d** | x x x |
| 2, rigid | LF open top, DD | CJ | all classes marked ("x x x x x") | — | — | — | **31e** | x x x |
| 2, rigid | HF, SD | CA | I+II/A marked ("x") | — | — | — | **32a** | x x |
| 2, rigid | HF, SD | CA | II+III marked ("x") | — | — | ≤3 100 | **32b** | x x |
| 2, rigid | HF, SD | CA | II+III marked ("x") | — | — | >3 100 | **32c** | x x |
| 2, rigid | HF, SD | CA | III/B marked ("x") | — | — | — | **32d** | x x |
| 2, rigid | HF, DD | CB | I, I+II/A, II marked ("x x x") | — | ≤6 | — | **32e** | x x |
| 2, rigid | HF, DD | CB | I, I+II/A, II marked ("x x x") | — | >6 | — | **32f** | x x |

**Table 5 — Vehicle groups for complete vehicles and completed vehicles that are heavy buses with 3 axles**

| Axles | Chassis config | Vehicle Code | Class-of-vehicle marks | Low entry | Pax lower deck | Height [mm] | Vehicle group | Mission-profile marks |
|---|---|---|---|---|---|---|---|---|
| 3, rigid | LF, SD | CE | x x x | no | — | — | **33a** | x x x |
| 3, rigid | LF, SD | CE | x x | yes | — | — | **33b1** | x x x |
| 3, rigid | LF, SD | CE | x | yes | — | — | **33b2** | x x x x |
| 3, rigid | LF, DD | CF | x x x | — | — | — | **33c** | x x x |
| 3, rigid | LF open top, SD | CI | x x x x x | — | — | — | **33d** | x x x |
| 3, rigid | LF open top, DD | CJ | x x x x x | — | — | — | **33e** | x x x |
| 3, rigid | HF, SD | CA | x | — | — | — | **34a** | x x |
| 3, rigid | HF, SD | CA | x | — | — | ≤3 100 | **34b** | x x |
| 3, rigid | HF, SD | CA | x | — | — | >3 100 | **34c** | x x |
| 3, rigid | HF, SD | CA | x | — | — | — | **34d** | x x |
| 3, rigid | HF, DD | CB | x x x | — | ≤6 | — | **34e** | x x |
| 3, rigid | HF, DD | CB | x x x | — | >6 | — | **34f** | x x |
| 3, articulated | LF, SD | CG | x x x | no | — | — | **35a** | x x x |
| 3, articulated | LF, SD | CG | x x | yes | — | — | **35b1** | x x x |
| 3, articulated | LF, SD | CG | x | yes | — | — | **35b2** | x x x x |
| 3, articulated | LF, DD | CH | x x x | — | — | — | **35c** | x x x |
| 3, articulated | HF, SD | CC | x | — | — | — | **36a** | x x |
| 3, articulated | HF, SD | CC | x | — | — | ≤3 100 | **36b** | x x |
| 3, articulated | HF, SD | CC (2nd SD row) | x | — | — | >3 100 | **36c** | x x |
| 3, articulated | HF, SD | CC (2nd SD row) | x | — | — | — | **36d** | x x |
| 3, articulated | HF, DD | CD | x x x | — | ≤6 | — | **36e** | x x |
| 3, articulated | HF, DD | CD | x x x | — | >6 | — | **36f** | x x |

**Table 6 — Vehicle groups for complete vehicles and completed vehicles that are heavy buses with 4 axles**

| Axles | Chassis config | Vehicle Code | Class-of-vehicle marks | Low entry | Pax lower deck | Height [mm] | Vehicle group | Mission-profile marks |
|---|---|---|---|---|---|---|---|---|
| 4, rigid | LF, SD | CE | x x x | no | — | — | **37a** | x x x |
| 4, rigid | LF, SD | CE | x x | yes | — | — | **37b1** | x x x |
| 4, rigid | LF, SD | CE | x | yes | — | — | **37b2** | x x x x |
| 4, rigid | LF, DD | CF | x x x | — | — | — | **37c** | x x x |
| 4, rigid | LF open top, SD | CI | x x x x x | — | — | — | **37d** | x x x |
| 4, rigid | LF open top, DD | CJ | x x x x x | — | — | — | **37e** | x x x |
| 4, rigid | HF, SD | CA | x | — | — | — | **38a** | x x |
| 4, rigid | HF, SD | CA | x | — | — | ≤3 100 | **38b** | x x |
| 4, rigid | HF, SD | CA | x | — | — | >3 100 | **38c** | x x |
| 4, rigid | HF, SD | CA | x | — | — | — | **38d** | x x |
| 4, rigid | HF, DD | CB | x x x | — | ≤6 | — | **38e** | x x |
| 4, rigid | HF, DD | CB | x x x | — | >6 | — | **38f** | x x |
| 4, articulated | LF, SD | CG | x x x | no | — | — | **39a** | x x x |
| 4, articulated | LF, SD | CG | x x | yes | — | — | **39b1** | x x x |
| 4, articulated | LF, SD | CG | x | yes | — | — | **39b2** | x x x x |
| 4, articulated | LF, DD | CH | x x x | — | — | — | **39c** | x x x |
| 4, articulated | HF, SD | CC | x | — | — | — | **40a** | x x |
| 4, articulated | HF, SD | CC | x | — | — | ≤3 100 | **40b** | x x |
| 4, articulated | HF, SD | CC (2nd SD row) | x | — | — | >3 100 | **40c** | x x |
| 4, articulated | HF, SD | CC (2nd SD row) | x | — | — | — | **40d** | x x |
| 4, articulated | HF, DD | CD | x x x | — | ≤6 | — | **40e** | x x |
| 4, articulated | HF, DD | CD | x x x | — | >6 | — | **40f** | x x |

**Footnotes to Tables 4, 5, 6:**
- (*) Vehicle Code: in accordance with Regulation (EU) 2018/858.
- (**) Class of vehicle: in accordance with paragraph 2 of UN Regulation No. 107.

**On the ambiguity flag:** in Tables 4–6, the exact mapping of each "x" to a specific one of the five mission-profile columns (Heavy Urban / Urban / Suburban / Interurban / Coach) could not be recovered with certainty from the linearized OCR text — the count of "x" marks per row is reliable (extracted faithfully) but the specific column(s) they sit under is not. Given that mission-profile assignment materially affects which duty cycle is simulated for a given complete-bus vehicle-group code, **this should be verified against the original PDF table before being relied on for tool logic.**

---

## 2. Method to determine CO2 emissions and fuel consumption for heavy buses
*(as amended by ►M3 and ►M4 — the heavy-bus staged-simulation method)*

### 2.1 Overview
*(►B)* "For heavy buses the vehicle specifications of the complete vehicle or completed vehicle including properties of the final bodywork and auxiliary units shall be reflected in the results for CO2 emissions and fuel consumption. In the case of heavy buses built in steps, more than a single manufacturer may be involved in the process of generation of input data and input information and the operation of the simulation tool."

For heavy buses, CO2/fuel consumption is based on **two different simulations**:
(a) for the **primary vehicle**;
(b) for the **complete vehicle or completed vehicle**.

### 2.2 When both simulations are required
*(►B)* "If a heavy bus is approved by a manufacturer as a complete vehicle, the simulations shall be performed for both the primary vehicle and the complete vehicle."

### 2.3 The primary-vehicle simulation
*(►M3)*

- Input to the simulation tool for the **primary vehicle** covers input data on the **engine, transmission, tyres**, and input information for a **subset of auxiliary units** (footnote 3: "Input information and input data as defined in Annex III for primary vehicles").
- Classification into vehicle groups follows **Table 3**, based on number of axles and whether the vehicle is articulated.
- The simulation tool allocates a set of **4 different generic bodies** (high floor / low floor × single deck / double deck) and simulates **11 mission profiles** (as listed in Table 3 for each vehicle group) for **each** vehicle group, under **2 different loading conditions**.
- This produces a set of **22 results** for CO2 emissions and fuel consumption for a primary heavy bus. *(4 bodies is a simplification stated in the text — not literally 4 × 11 × 2 = 88; the regulation states the output set is "22 results," meaning the 11-mission-profile × 2-loading-condition combination (22) is computed per the single applicable vehicle-group/body allocation relevant to that primary vehicle, not across all 4 generic bodies simultaneously — this is exactly as the source states; I am not inferring beyond it.)*
- The simulation tool produces the **vehicle information file for the initial step (VIF1)**, containing all data needed by the next manufacturing step. VIF1 comprises: all **non-confidential** input data, the results for **energy consumption** in **[MJ/km]** (footnote 4: "The results for CO2 emissions and fuel consumption do not need to be submitted via the VIF, as this information can be calculated from results for energy consumption and the known fuel type"), information on the primary manufacturer, and the relevant **hashes** (footnote 5: "The content of the VIF is specified in detail in Annex IV, Part III").

*(►M4)* If a heavy bus is approved as a **complete vehicle**, only the mission profiles for the **primary vehicle group related to the group of the complete vehicle** (per **Table 7** below) **may be simulated** — i.e. the full 11-profile/22-result set need not be computed if the complete-vehicle group is already known; the simulation can be narrowed to the relevant primary group. If the complete-vehicle group **changes** in a subsequent manufacturing step, the primary vehicle manufacturer must make the **VIF1 with the full set of 22 results** available to the manufacturer responsible for that subsequent step (i.e. the full data set must still exist/be available even if a narrower simulation was initially run).

**Table 7 — Primary Vehicle Groups to be simulated in case of complete heavy buses**
*(introduced by ►M4; this table has a clean, unambiguous two-column structure)*

| Complete Vehicle Group | Primary Vehicle Group to be calculated |
|---|---|
| 31a, 31b1, 31b2, 31d | P31 SD |
| 31c, 31e | P31 DD |
| 32a, 32b, 32c, 32d | P32 SD |
| 32e, 32f | P32 DD |
| 33a, 33b1, 33b2, 33d | P33 SD |
| 33c, 33e | P33 DD |
| 34a, 34b, 34c, 34d | P34 SD |
| 34e, 34f | P34 DD |
| 35a, 35b1, 35b2 | P35 SD |
| 35c | P35 DD |
| 36a, 36b, 36c, 36d | P36 SD |
| 36e, 36f | P36 DD |
| 37a, 37b1, 37b2, 37d | P37 SD |
| 37c, 37e | P37 DD |
| 38a, 38b, 38c, 38d | P38 SD |
| 38e, 38f | P38 DD |
| 39a, 39b1, 39b2 | P39 SD |
| 39c | P39 DD |
| 40a, 40b, 40c, 40d | P40 SD |
| 40e, 40f | P40 DD |

Note: Table 7 only covers complete-vehicle groups 31–40 (2, 3 and 4-axle rigid/articulated buses from Tables 4–6). It does not list a mapping row for every one of 31a/31b1/31b2/31d individually split out beyond the groupings shown — the source groups several complete-vehicle-group suffixes (a, b1, b2, d, etc.) to the same primary vehicle group/subgroup in a single row, exactly as reproduced above.

### 2.4 Handing over the VIF1
*(►M3)*

- The primary vehicle manufacturer must make **VIF1 available** to the next manufacturer.
- If a primary-vehicle manufacturer provides data **beyond** the primary-vehicle requirements (Annex III), that extra data does **not** affect the primary-vehicle simulation results, but **is written into VIF1** for consideration at later steps.
- For a primary vehicle, the simulation tool also produces a **manufacturer's records file**.

### 2.5 Interim vehicles
*(►M3)*

- The **interim manufacturer** is responsible for a **sub-set** of relevant input data/input information for the final bodywork (footnote 6: "Subset for input information and input data as defined in Annex III for complete and completed vehicles").
- An interim manufacturer **does not apply for certification** of the completed vehicle.
- An interim manufacturer **adds or updates** information relevant to the completed vehicle and operates the simulation tool to produce an **updated and hashed VIFi** (footnote 7: "'i' represents the number of manufacturing steps involved in the process so far" — i.e. VIF1, VIF2, VIF3... as the bus passes through steps).
- The VIFi is made available to the next manufacturing step; it also serves the **documentation function toward approval authorities**.
- **No CO2/fuel-consumption simulations are performed on interim vehicles** — this is an explicit, important simplification: interim steps only update/carry data forward, they never trigger a new CO2 determination.

### 2.6 Modifications that trigger "primary manufacturer" responsibilities
*(►M3)*

> "If a manufacturer performs modifications to an interim, complete or completed vehicle, which would require updates to the input data or the input information allocated to the primary vehicle (e.g. a change of an axle or of tyres), the manufacturer performing the modification acts as a primary vehicle manufacturer with the corresponding responsibilities."

This is a key rule for sizing-tool logic: **any downstream modification that touches primary-vehicle-level input data** (e.g., axle or tyre change at the body-builder stage) **reclassifies that downstream party as a primary vehicle manufacturer** for that modification, with the full primary-vehicle-manufacturer obligations (simulation, VIF1 production, etc.) attaching to them.

### 2.7 The complete/completed-vehicle simulation
*(►M3/►M4)*

For a complete or completed vehicle, the manufacturer must complement and, if necessary, update the input data/input information for the final bodywork (as transmitted in VIFi from the previous step) and operate the simulation tool to calculate CO2 emissions and fuel consumption. Classification at this stage uses the **six criteria** of point 1.2.3 (Tables 4, 5, 6).

The simulation tool performs **four calculation steps**:

- **2.7.1 — Step 1:** Select the **primary vehicle sub-group** matching the bodywork of the complete/completed vehicle (e.g. "P34 DD" for complete-vehicle-group "34f") and retrieve the corresponding **energy consumption results from the primary vehicle simulation**.
- **2.7.2 — Step 2:** Perform simulations to quantify the **influence of the bodywork and auxiliaries** of the complete/completed vehicle **compared to the generic bodywork and auxiliaries** considered in the primary-vehicle simulation's energy-consumption results. These simulations use **generic data** for the parts of the primary-vehicle data set that are **not** part of the VIF information transfer between manufacturing steps (footnote 8: "See Annex IV, Part III, point 1.1").
- **2.7.3 — Step 3:** Combine the Step-1 primary-vehicle energy-consumption results with the Step-2 results to obtain the **energy consumption results of the complete or completed vehicle**. "The details of this calculation step are documented in the user manual of the simulation tool" — i.e. the Regulation explicitly defers the precise combination formula/algorithm to the VECTO user manual, not specified in the legal text itself.
- **2.7.4 — Step 4:** Calculate **CO2 emissions and fuel consumption** results from the Step-3 energy-consumption results and the **generic fuel specifications stored in the simulation tool**.

Steps 2, 3 and 4 are performed **separately for each combination** of mission profile (per Tables 4, 5, 6 for the relevant vehicle group) **in both low and representative loading conditions**.

For a complete/completed vehicle, the simulation tool produces: a **manufacturer's records file**, a **customer information file**, and a **VIFi** — the VIFi being made available to the next manufacturer if the vehicle undergoes a further completion step.

> **[Figure referenced in source but not visually extracted from this text-only OCR — consult the original PDF if the diagram is needed.]** "Figure 2 — Example of data flow in the case of a heavy bus manufactured in five steps" is referenced at the end of point 2.7.5 to illustrate the data flow (VIF1 → VIF2 → ... → final complete/completed-vehicle outputs) across a 5-step manufacturing chain. The diagram itself did not survive text extraction.

---

## Summary of the heavy-bus staged method (plain-language recap, for the sizing-tool's internal logic — not a substitute for the above verbatim transcription)

1. **Primary stage** (manufacturer of the rolling chassis/driveline): simulate using engine + transmission + tyres + partial auxiliaries input, classified by axle count + articulation only (Table 3) → produces energy-consumption results in MJ/km for up to 11 mission profiles × 2 loading conditions (22 results) and VIF1.
2. **Interim stage(s)** (0 to N body-builder steps before the final one): no simulation; just data carry-forward/update via VIFi, unless a change to primary-level inputs occurs (then that party becomes a primary manufacturer for that change).
3. **Complete/completed stage** (final body-builder or the manufacturer who completes the vehicle): classify by the 6 criteria (Tables 4/5/6) → look up matching primary sub-group (Table 7) → run Steps 1–4 to get final CO2/fuel-consumption results, customer information file, and certificate-of-conformity-ready outputs.

**Open items / things this file could not resolve from the text alone, flagged for the user:**
- The exact per-cell mission-profile alignment in Tables 1, 2, 4, 5, 6 (see caveats above).
- Figure 1 (low-entry decision flow) and Figure 2 (5-step data-flow example) — diagrams not present in this OCR text.
- The precise mathematical combination formula for Step 3 (point 2.7.3) is explicitly deferred by the Regulation itself to the VECTO **user manual** (a separate document from this Regulation) — not something this file can supply without that manual.
