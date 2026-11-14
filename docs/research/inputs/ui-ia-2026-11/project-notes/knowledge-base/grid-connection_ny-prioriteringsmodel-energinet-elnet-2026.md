\# Energinet's New Prioritization Model for Transmission Grid Connection (2026)

> **Source document:** "TILSLUTNING TIL ENERGINETS ELNET — 2026: Ny prioriteringsmodel for" (English: "Connection to Energinet's Grid — 2026: New Prioritization Model for [Connection]")
> **Publisher:** Energinet — the Danish transmission system operator (TSO), an independent public enterprise ("selvstændig offentlig virksomhed") owned by the Danish state. Address: Tonne Kjærsvej 65, 7000 Fredericia. Contact for prioritization-criteria questions: netkundecenter@energinet.dk
> **Document ID:** Dok. 25/06717-16, marked "Offentlig/Public" (Public)
> **Dating:** The project file name dates this to **1 February 2026**. The extracted body text does not itself contain an explicit publication-date field — the 1 Feb 2026 date should be treated as sourced from the filename, not confirmed inline in the document body. [flagging per instructions — not verified from an in-body date]
> **Document type:** A short public information brochure ("pjece") from Energinet aimed at existing and prospective grid customers ("netkunder"), not a formal executive order or law text.
> **Length:** ~9 pages (title page, intro, maturity requirements, prioritization criteria, old-vs-new process description, process illustration/diagram, customer cases, Q&A, contact/imprint page).

---

## 1. Relevance to the HDEV Sizing & Modelling Tool

**Flagging explicit relevance:** This document describes how Energinet (the Danish TSO) now queues and screens applications to connect to the **transmission grid** ("transmissionsnettet"). This directly affects how quickly a project — including a very large depot, charging hub, or industrial consumption load applying at transmission voltage — moves through Energinet's connection process, and in what order Energinet allocates its own case-processing resources. For the HDEV tool this matters for:
- Modelling realistic **grid-connection lead times** for large depots/hubs, especially any that would need to interconnect directly to the transmission grid (as opposed to a DSO distribution grid).
- Understanding that a depot project's queue position for **case processing** (sagsbehandling) is no longer purely date-of-application ("først-til-mølle" / first-come-first-served), but depends on documented project maturity and how well the project fits existing grid capacity.
- Understanding that the **underlying capacity allocation right** itself remains first-come-first-served once maturity is met (per Energinet's own Q&A) — only the *processing queue*, not the capacity right, is reprioritized.
- The new capacity map ("kapacitetskort," see §5) as a planning input: it will show which stations have free/available bays and whether a station's local area is consumption- or production-dominated — both facts materially affect where a large flexible consumption load (e.g., an EV depot) would be classified and how fast it could be connected.

**Important scope caveat:** This document explicitly concerns connection to Energinet's **transmission grid**. Most HDEV depots will connect at the distribution level via a DSO (Danish: DSO/net-selskab), not directly to Energinet. The document does not state whether or how DSOs apply an equivalent model; it does not mention DSO-level prioritization at all. [unclear from source — no DSO-level prioritization is described; only the DSO's initial referral role into Energinet's process is mentioned, see §4]. This model would only apply directly to a depot/consumption project large enough to connect at transmission voltage, or indirectly as a policy signal for how DSOs might eventually be expected to manage similar queues.

---

## 2. Background and Rationale (Why the Model Changed)

- Denmark's green transition ("den grønne omstilling") is accelerating electrification, increasing the need for **flexibility and speed** in Energinet's handling of new project connections.
- Historically, Energinet had few requirements for a project to be registered for case processing ("sagsbehandling") regarding transmission grid connection, and processing all projects regardless of maturity was not a major challenge because project volume was limited.
- The pace of the green transition has caused a **sharply rising demand** for transmission grid connections. Projects are also increasingly complex, with a **growing share being consumption and hybrid projects** (as opposed to pure production/generation projects).
- This has produced a marked **queue ("kø")** for Energinet's case processing of grid-connection projects, leading to **longer processing times** for new grid customers.
- The prior model was a pure **"first-come, first-served" principle** ("først-til-mølle-princippet"): projects registered earliest are placed first in the queue and reach case processing soonest.
- Problem with first-come-first-served: **less-mature projects can block far more mature projects** from moving forward, since queue position was based only on submission date, not readiness.
- Following a recommendation from the **"NEKST" working group** ("NEKST-arbejdsgruppens anbefaling"), Energinet decided to introduce a new prioritization model for connecting consumption and production installations ("forbrugs- og produktionsanlæg") to the transmission grid. [The NEKST working group is referenced but not further defined/described in this document — unclear from source what NEKST stands for or who comprises it.]
- Energinet states prioritization follows **objective and transparent criteria** that comply with the **non-discrimination principle** ("ikke-diskriminationsprincippet"). No specific statute, executive order, or EU regulation number is cited in this brochure for that principle — [unclear from source; the non-discrimination principle is asserted but not linked to a specific legal citation in the extracted text].
- Energinet explicitly states these changes **do not affect its work on larger grid-expansion projects** ("større netudbygningsprojekter") — Energinet still assesses overall need and makes a holistic assessment for those separately.

### Three headline changes introduced

1. **New maturity requirements** ("modenhedskrav") for grid-customer projects wanting to be screened for transmission connection — so resources are more targeted at sufficiently mature projects, without discouraging market interest in green investment.
2. **New prioritization criteria** ("prioriteringskriterier") intended to better utilize the existing grid, strengthening Energinet's long-term planning and giving better conditions to optimize the future energy system.
3. **An addition to the capacity map** ("kapacitetskort"), going live in early 2026 ("primo 2026"), letting grid customers see which stations have free bays/room for new bays, and whether a station is consumption- or production-dominated — giving customers an overview of where fastest connection is possible.

---

## 3. New Maturity Requirements ("Modenhedskrav")

Energinet introduces **two minimum maturity requirements** that a project must meet **before the screening process begins**. Purpose: more effective use of Energinet's overall resource pool and faster processing of more-mature projects. Energinet explicitly states these requirements **must not become a barrier** to the growing interest in green investment, and is exploring whether **further** maturity requirements may be needed later, depending on the observed effect of the current ones.

| # | Requirement | Detail |
|---|---|---|
| 1 | **Documentation of area/land rights** ("Dokumentation for rettigheder til arealet") | The grid customer must show documentation of the possibility to acquire rights to the project area, or conditional agreements to acquire such rights. Examples: purchase agreements, option agreements, or similar. Assessed by how far along the customer is in dialogue with the landowner. |
| 2 | **Project timeline** ("Tidsplan for projektet") | The customer must submit a timeline following an Energinet template, documenting expected time needed to obtain necessary permits, showing the project's expected main milestones — from initial planning and authority/regulatory processes through execution, testing, and desired commissioning ("idriftsættelse"). |

**Land-rights documentation — accepted evidence tiers** (all three are accepted as meeting the requirement, at different strength levels):
- A **written declaration of willingness** to reach an agreement → indicates the process has begun.
- A **signed option agreement** → strengthens the right of disposal ("råderet").
- A **final purchase agreement** → considered completed rights acquisition.

**Timeline documentation — example milestone content:** local plan and environmental permit, investment decisions, grid compliance studies, design, procurement and construction, and expected commissioning date.

**Effect of meeting maturity requirements:** Once a project's maturity requirements are fulfilled, **capacity in the grid is allocated ("henføres") to the project** — i.e., meeting maturity requirements is the trigger for capacity reservation (see §6 on how this interacts with first-come-first-served).

**Stated purpose of the maturity requirements:**
- Ensure projects with high maturity that apply for connection can be connected as fast as possible.
- Support the desire for faster renewable energy build-out during a period of resource pressure.
- The land-rights requirement is meant to minimize the risk of **project changes during the connection process**.
- The timeline requirement is meant to give Energinet greater insight into the customer's project and thus a better basis to assess the project's overall maturity.

**Potential future maturity requirements:** Energinet is exploring whether further maturity requirements should be implemented over time. [unclear from source — no specifics given on what these might be.]

---

## 4. New Prioritization Criteria ("Prioriteringskriterier")

In addition to the maturity requirements, Energinet introduces a set of prioritization criteria. **Stated purpose:** ensure overall resources are used where they create the greatest value — e.g., by optimizing utilization of the existing grid, thereby freeing up resources — so Energinet can work more efficiently across projects. The criteria are divided into **four groups**, described below (the fourth being an implicit catch-all/"other" category plus a note on possible future criteria).

| Criterion | What it means / how it's determined |
|---|---|
| **1. Projects that do not require new bays** ("Kræver ikke nye felter") | E.g., adding batteries to an existing production facility. Means the customer's project can be included in an already-established or already-planned grid connection, making it simpler and faster to process. |
| **2. Projects connectable within the station area** ("Kan tilsluttes inden for stationsarealet") | Determined by whether there is a free bay at the nearest station, or room to establish one — meaning no station expansion or new station is needed. This can also include stations that are decided-but-not-yet-established. |
| **3. Consumption plants in production-dominated areas, and vice versa** ("Forbrugsanlæg i produktionsdominerede områder og omvendt") | Area type follows the map underlying Energinet's **producer payment scheme** ("producentbetaling"). Plant type (consumption vs. production) is determined by the direction with the **largest registered exchange capacity**. If a project requests equal capacity in both directions, it is categorized as the **opposite** of the area type it is located in — which benefits the project owner for final prioritization purposes. |
| **4. Projects where local-plan drafting has been initiated** ("Udarbejdelse af forslag til lokalplan er igangsat") | It must have been decided to initiate drafting of a local plan proposal for the grid-customer project, if the project requires one. If the installation does not require a new local plan, the criterion is automatically considered met. This functions as a **minimum requirement for up-prioritization**. Typically follows a project having been through a public pre-consultation ("fordebat"). |
| **Possible future prioritization criteria** | Energinet is exploring whether to adapt or implement additional future prioritization criteria. [unclear from source — no specifics given.] |

Energinet explicitly frames this as its **"first attempt"** at prioritization criteria; experience with these will determine whether criteria are later added or adjusted.

---

## 5. The Capacity Map Addition ("Kapacitetskort")

- Going live **primo (early) 2026**.
- Will let grid customers see, per station: (a) whether there are **free bays** or room to establish new bays, and (b) whether the station is **consumption-dominated or production-dominated**.
- Purpose: give customers an overview of which stations offer the fastest possible connection.
- [unclear from source — no URL, access method, or further technical detail on the capacity map tool is given in this brochure beyond the above description.]

---

## 6. Old Process vs. New Process

### 6.1 Previous process (first-come-first-served)

- Energinet received a project after a **referral from the DSO**.
- The project then got a place in the queue for grid-connection projects, **based purely on submission order**, until the project was started.
- No longer considered appropriate given the sharply rising demand for transmission connections and resulting longer processing times.

### 6.2 New process

Energinet's stated recommendation is to introduce more and better prioritization criteria supporting more efficient, optimized case processing. Stated aim: a **transparent and objective** prioritization of projects that better utilizes both Energinet's limited processing resources and the existing grid capacity. Energinet again notes this is its **first proposal** for prioritization criteria; future experience will inform whether criteria are added or adjusted.

**Process steps** (a project passes through these before being assigned a queue place):

1. **Maturity check:** Energinet assesses whether the project meets the maturity requirements (§3). If not met, Energinet opens a dialogue with the customer on how to bring the project into compliance.
2. **Network-utilization grouping:** Once maturity requirements are met, the project is placed in a group based on the **three network-utilization prioritization criteria** (criteria 1–3 in §4: no new bays / within station area / counter-type area) — or "Others" ("Øvrige") if none apply.
3. **Local-plan categorization:** The project is further categorized by whether local-plan drafting has been initiated (criterion 4 in §4) — meant to let Energinet confirm dialogue with the municipality has begun, demonstrating a degree of maturity.
4. **Priority-group assignment:** Based on the combined assessment, the project is assigned to a **priority group**, which determines the **order in which it reaches case processing** at Energinet.

**Ability to move within the queue:** A project can move up or down in priority groups if there are improvements relevant to the criteria (e.g., a bay becomes free). It is the **grid customer's own responsibility** to notify Energinet of project-specific improvements. If bays become available, Energinet proactively contacts the customer about the possibility.

### 6.3 Two distinct queues — an important nuance (from the Q&A, §8)

The document distinguishes between:
- **Queue for grid capacity allocation** ("kø til kapacitet i nettet") — triggered once maturity requirements are met; per Energinet's own Q&A, **capacity is still allocated to a project on a first-come-first-served basis** ("kapaciteten henføres stadig til projektet efter først-til-mølle-princippet"). This is Energinet's explicit answer to why the new model is not considered discriminatory: **basic grid-customer rights to capacity are unchanged.**
- **Queue for case processing** ("kø til sagsbehandling") — this is the queue actually reordered by the new prioritization criteria (network utilization + local-plan maturity), determining how fast Energinet's own staff/resources get to screening a given project.

---

## 7. Priority Groups (1–8) — Illustration of the New Process

The process diagram (page 6 of the source) shows the following flow and produces **eight numbered priority groups**, reconstructed here as a table. [Note: this table is my structural interpretation of the flow diagram as extracted from the source text — the source presents this as a branching diagram, not a literal table, so the exact rendering below reflects that reconstruction, not a table appearing verbatim in the original.]

**Flow:** Referral from DSO → Application to Energinet → **Maturity check** (dialogue if unmet) → capacity queue placement → **Network-utilization criterion** (one of: no new bays / within station area / counter-type-area consumption-production / others) → **Local-plan status** (drafting initiated, or others) → **Priority group (1–8)**.

| Priority Group | Network-Utilization Criterion Met | Local-Plan Status |
|---|---|---|
| 1 | No new bays required | Local-plan drafting initiated (or not required) |
| 2 | No new bays required | Others (local-plan drafting not initiated) |
| 3 | Connectable within station area | Local-plan drafting initiated (or not required) |
| 4 | Connectable within station area | Others (local-plan drafting not initiated) |
| 5 | Consumption plant in production-dominated area, or vice versa | Local-plan drafting initiated (or not required) |
| 6 | Consumption plant in production-dominated area, or vice versa | Others (local-plan drafting not initiated) |
| 7 | Others (none of criteria 1–3 met) | Local-plan drafting initiated (or not required) |
| 8 | Others (none of criteria 1–3 met) | Others (local-plan drafting not initiated) |

Lower group numbers = processed sooner; group 8 is the slowest tier (worst combination: needs new grid infrastructure/station work, is not counter-type to its area, and has not started local-plan work).

---

## 8. Worked Customer Cases (from the source, page 7)

Energinet stresses these are **hypothetical** examples; actual placement always depends on the specifics of the real project.

1. **Battery addition to an existing solar project that already has a connection agreement.** Since this is a modification to an existing project not requiring new bays, it would now be placed in **priority group 1 or 2** (depending on local-plan status). Under the new criteria, this type of project gets faster processing than before.
2. **A project that does not meet Energinet's maturity requirements** (e.g., missing project area or a concrete timeline). Energinet enters into dialogue with the developer on what's needed to proceed to case processing. Under the old approach, Energinet would have started case processing even though the project was not mature.
3. **A large solar plant to be built in a production-dominated area**, requiring both a new station and a new local plan. This would be placed in **priority group 8**. Under the old approach, this project would have been processed under pure first-come-first-served — even though the actual grid connection would in practice face a long wait if, for example, a new station had to be built.

---

## 9. Questions & Answers (Energinet's own FAQ, page 8)

| Question | Energinet's Answer |
|---|---|
| What happens if my project doesn't meet the maturity requirements? | Energinet enters dialogue on how to bring the project into compliance, and guides the customer on what's missing and how to fix it. |
| Can my project be deprioritized even though I already registered it? | Depends on process stage. If the project has already reached the **maturation phase** ("modningsfasen"), it is **not affected** by the changes. If it is still in the queue awaiting screening or maturation, prioritization can change depending on which criteria it meets. |
| Isn't the maturity/prioritization requirement discriminatory? | No — basic grid-customer rights are unchanged; **capacity is still allocated on a first-come-first-served basis**. This measure makes Energinet's overall grid-connection work more efficient. |
| Can I be reprioritized if I make improvements (e.g., a local plan gets adopted)? | Yes — up to screening, projects can be **up- or down-prioritized** depending on which criteria are met (e.g., starting local-plan drafting triggers reprioritization). **Once a project reaches the maturation phase, it can no longer be up- or down-prioritized**, unless significant changes are made (e.g., to location or power capacity), in which case the project may be **closed and the process restarted**. |
| How long can I keep being pushed down the queue — can I get stuck? | Energinet continues to aim for project developers to have clarity on their screening project **within 24 months** — so a customer cannot get permanently stuck; case processing continues as before. Energinet is working toward **standardized cases being screenable within 12 months**. |
| Will Energinet make further changes in the future? | Energinet continuously develops and improves its workflows and expects **more prioritization criteria** in the future. The current maturity/prioritization criteria are described as a "first attempt" at ensuring resources are used more effectively and targeted at projects most likely to be realized first. |
| How is a project classified as consumption vs. production for the relevant criterion? | Based on the direction with the **largest requested exchange (development) capacity**. If a project requests equal capacity in both directions, it is categorized as the **opposite** of the area type it's located in — which benefits the project owner in final prioritization. |

---

## 10. Key Verifiable Figures / Facts Extracted (no invented values)

- **24 months** — Energinet's target for a project developer to have clarity/resolution on their screening project (stated goal, not a legal deadline per the extracted text).
- **12 months** — Energinet's target for screening standardized cases.
- **8** — number of priority groups in the new model.
- **2** — number of new maturity requirements (land rights; project timeline).
- **4** — number of prioritization-criteria "groups" as presented (3 concrete network-utilization criteria + local-plan status), plus an explicit note of possible future criteria.
- **Primo 2026** — target go-live for the capacity map addition. [Not a specific calendar date — "primo" means "early" in Danish; exact date unclear from source.]
- Document ID: **Dok. 25/06717-16**.

---

## 11. Explicit Gaps / Items Marked Unclear from Source

- No specific law, executive order (bekendtgørelse), or EU regulation is cited by name/number for the "non-discrimination principle" referenced.
- "NEKST-arbejdsgruppen" (NEKST working group) is named as the source of the recommendation but is not defined, described, or dated anywhere in this document.
- No explicit in-body publication date; "1 February 2026" is taken from the project file name only.
- No description of how (or whether) DSOs apply an equivalent prioritization model at the distribution level — the document only covers Energinet's transmission-grid process.
- No numeric detail on current queue length, number of projects, or MW volumes affected.
- No detail on the capacity map's exact launch date, URL, or technical access method beyond "primo 2026."
- No description of appeal/complaint mechanisms if a customer disputes their priority-group placement.
- No specific voltage-level thresholds stated for what counts as "transmission grid" connection in this document (Denmark's transmission grid is typically 132/150 kV and 400 kV, but this figure is general market knowledge, not stated in this brochure — [unclear from source]).

---

*Extraction and English translation prepared by Claude from Energinet's Danish-language source brochure (project file: `ny-prioriteringsmodel-for-tilslutning-til-energinets-elnet-1-februar-2026.pdf`). All Danish legal/technical terms are preserved in parentheses on first use. No values, assumptions, or interpretations beyond the source text have been added except where explicitly marked as a reconstruction (§7 table) or flagged as unclear (§11).*
