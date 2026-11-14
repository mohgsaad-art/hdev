# Charging Station Establishment and Operation — Operator's Service Level (Tender Evaluation Template)

**Source file:** `56b8be287f1e4500b2e23f3203039ab4.pdf` (opaque hash/ID filename — original document title recovered from content: "Etablering og drift af ladestandere - Operatørens serviceniveau")
**Category:** Tender/procurement template document (bid-evaluation appendix / paradigm)
**Original language:** Danish (translated to English below; proper nouns kept in Danish)
**One-line summary:** A companion Vejdirektoratet (Danish Road Directorate) tender template, published December 2022, structuring how bidders (charging-point operators) must describe their proposed service level — functionality, payment/data systems, and operational workflows — for qualitative award-criteria evaluation in Danish municipal EV charging tenders.

## Document Identification
This file's original filename was an opaque hash/ID string (`56b8be287f1e4500b2e23f3203039ab4.pdf`). Based on content — a header "Etablering og drift af ladestandere - Operatørens serviceniveau" (Establishment and operation of charging stations - Operator's service level), guidance text addressed to "operatøren" (the operator/bidder) explaining how to respond to award sub-criteria, references to "Underkriterium B" and "Underkriterium C" per "BUT 3.6.1" (Bedømmelse af Underkriteriernes Tilfredsstillelse — Assessment of Sub-Criteria Satisfaction, section 3.6.1), and the same Vejdirektoratet publication metadata as the companion Kravspecifikation document — this is determined with high confidence to be a **tender bid-response template/appendix** ("Bilag til tilbud") used alongside the Kravspecifikation (requirements specification) document, structuring how prospective charging-station operators must present their proposed service level for qualitative evaluation as part of a Danish municipal charging-infrastructure concession tender.

## Publication Details
- **Publisher:** **Vejdirektoratet** (Danish Road Directorate), responsible group "Udstyr for veje og bygværker."
- **Published:** 21 December 2022.
- **Status (as of extraction):** "Historiske" (Historical/archived); "Ophørsdato" (expiry date): 17 September 2024.
- **Document type:** A bid-response appendix template ("Bilag til tilbud") for prospective operators/bidders to complete as part of a tender submission, structured around two qualitative award sub-criteria: **Underkriterium B** ("Funktionalitet, system for betaling, og data" — Functionality, payment system, and data) and **Underkriterium C** ("Arbejdsgange og processer" — Workflows and processes).
- Companion document to `63b41becca03484da6136b2fab416294.pdf` ("Etablering og drift af ladestandere - Kravspecifikation," processed separately in this knowledge base), which sets the mandatory minimum technical requirements; this document instead structures the **discretionary/qualitative evaluation criteria** used to score competing bids above the mandatory minimums.

## Document Structure
1. Bilag til tilbud: Operatørens serviceniveau (Appendix to bid: Operator's service level)
2. Section B: Funktionalitet, system for betaling, og data (Functionality, payment system, and data)
3. Section C: Arbejdsgange og processer (Workflows and processes)

Template instructs the drafting municipality to insert the names of the specific "delkontrakter" (sub-contracts) and "optioner" (options) covered, with a checkbox-style list for each, and cautions to keep sub-contract/option naming consistent across all tender documents (or, alternatively, to tender locations individually and cross-reference a separate locations annex).

## Section B: Functionality, Payment System, and Data

Each numbered point below follows the same three-part template structure: (1) the qualitative criterion/what is assessed positively, (2) elaboration of how the weighting/scoring works, (3) guidance to the contracting authority (ordregiver) on the rationale, followed by a blank "Tilbudsgivers besvarelse" (Bidder's response) field for the operator to complete.

### B.1 — User Interface / Functionality
- Assessed positively if the operator provides a user interface that does not itself increase the risk of misuse/faulty operation — e.g., an app or QR code linking to a website — with clear, easy-to-understand, intuitive charging and payment procedures.
- Positive weight given for: clarity/simplicity of use; guidance on operation and payment provided in multiple languages, accessible via app, website, or other media; ability for the end user to see charging power and State of Charge (SoC) during charging via app/website/other media; and the operator demonstrating (via description, examples, visualizations, or a live demo) that support for payment questions/issues is fast and effective.
- Rationale (guidance to contracting authority): this criterion rewards a good customer experience across charging-point operation, payment, and operator support/contact.

### B.2 — Charging Power Above Contractual Minimum
- Assessed positively if the operator's charging stations can charge at higher power than the Contract requires, weighted positively in proportion to how much the offered solution exceeds the charging-power requirement in Kravspecifikation section 3.2.
- Guidance: the contracting authority should consider whether it values locations where the operator proposes a higher-power charger than the stated minimum — e.g., if a 22 kW charger is required but the operator judges the location has a business case for a fast charger instead, this could be weighted positively.

### B.3 — Payment and Payment Systems
- Assessed positively if, beyond debit/credit cards, charging points also support **RFID, apps, or other payment methods** — the more payment methods supported, the more positive weight given.
- Guidance: relates to the desirability of offering end users multiple payment options as good customer service; this criterion rewards operators offering a broader range of payment methods.

### B.4 — Price Uniformity Across Customer Types
- Assessed positively if end-user prices are uniform regardless of customer affiliation/relationship type; assessed as best if all end users pay the same price for charging.
- If the operator uses a business model where not all end users pay the same, positive weight is given in proportion to how small the price differences are between different end-user groups (e.g., the operator's subscription customers/customer club members vs. other ad-hoc customers).
- Legal basis cited: **AFI-lovens § 3, stk. 3** requires that prices charged by the operator to end users be **reasonable and non-discriminatory**. The contracting authority is obliged to ensure agreements with operators contain contract terms on reasonable, non-discriminatory prices, per **§3 of BEK nr. 1073 af 28/06/2022** — "Bekendtgørelse om ordregiveres indgåelse af aftaler om retten til at virke som operatør af offentligt tilgængelige ladepunkter" (Executive Order on contracting authorities' conclusion of agreements on the right to act as operator of publicly accessible charging points).

### B.5 — Data Accessibility
- Assessed positively if the operator's per-charging-point statistics are delivered to the contracting authority in an easily accessible way — e.g., via an online dashboard, Power BI, or similar — rather than as raw data (e.g., an Excel sheet).
- Operators are asked to attach visualizations, screenshots, demo access, or similar to illustrate their proposed solution.
- More positive weight given the more data the contracting authority can access on charging-point usage, in an easily accessible and clear manner.
- Guidance: useful for the contracting authority when assessing infrastructure value ahead of re-tendering.

### B.6 — Incident Logging System
- Assessed positively if the operator offers an incident-logging system that can effectively and precisely register events (errors, customer inquiries, etc.) and their handling/resolution.
- Positive weight given if data registration happens automatically as much as possible rather than manually, with manually-entered incidents (for cases that can't be auto-logged) still carrying automatic timestamping.
- Positive weight if the contracting authority can get access to the incident system, even if only read access, a special interface, and/or extractable statistics (e.g., on handling/resolution times).
- Guidance note: **not all operators can currently offer an incident-logging system**, which is why this is included as a qualitative (scored) criterion rather than a mandatory requirement in the Kravspecifikation. Beneficial for the contracting authority to be able to follow incidents and their resolution, and to use statistics to assess whether the operator is meeting maintenance/operations expectations.

## Section C: Workflows and Processes

### C.1 — Establishment Process
- Assessed positively if the operator's description of the establishment process appears well-developed and makes it credible that all charging stations will be established within the deadline.
- Positive weighting criteria include evidence the operator: has full overview of the entire establishment process; has workflows that appear well-tested/proven; has command of necessary authority approvals, including excavation permits, LER (underground utility registry) information retrieval, and the signage plan; and presents a robust-seeming timeline.
- Guidance: the contracting authority has an interest in the operator having firm control of the establishment process, and can reward a strong solution description here.

### C.2 — Cleaning and Maintenance Plan
- Assessed positively if the cleaning and maintenance plan appears sensible and sufficient.
- Positive weight given if the operator's description makes a sufficiently high level of cleaning/maintenance credible; operators asked to state response times and frequency of inspection and cleaning.
- Guidance: contracting authority has an interest in charging stations on public land remaining functional and appearing clean/well-kept; the operator should be able to inspect the area and clean within a reasonable response time in response to reports (e.g., graffiti) that aren't automatically logged in an incident system.

### C.3 — Fault, Deficiency, and Emergency Handling
- Assessed positively if the operator makes credible that its proposed solution can ensure stable operation, including in cases of faults, deficiencies, and emergencies.
- Operators must describe how different fault-report types are handled, differentiated by severity:
  - Less serious incidents (e.g., graffiti)
  - More serious incidents (e.g., non-functional charging stations)
  - Emergencies involving personal danger/risk to people
- Reports may also arrive via different channels requiring different handling: automatically reported; reported by end users (phone, email, or app); reported by the contracting authority.
- Operators must describe how such reports are handled, including whether the reporter receives feedback/status updates.
- Positive weight given if faults/deficiencies/emergencies are demonstrably handled quickly and within stated deadlines, and if feedback/status is given back to the original reporter.
- Guidance: contracting authority has an interest in fast, effective fault handling; giving reporters status feedback also reduces the volume of follow-up inquiries directed at the contracting authority during the operational phase.

### C.4 — Communication and Collaboration with the Contracting Authority
- Assessed positively if the contracting authority can easily and without obstacles reach the operator and quickly receive adequate assistance.
- A demonstrated focus on a good, stable collaboration with the contracting authority throughout the entire contract period is desired.
- Positive weight if it is easy for the contracting authority to know whom in the operator's organization to contact for different situations.
- Positive weight if the operator describes how it will contribute to a good, stable collaboration with the contracting authority, and if the operator can make credible a smooth handover between the different phases: bid phase, construction phase, and operational phase.
- Guidance: beneficial for the contracting authority to have, e.g., a single point of contact throughout the agreement period, and a good handover in the event of staff changes; operators might offer regular status meetings as an example mechanism.

### C.5 — Organizational Robustness
- Assessed positively if the operator can make credible that it offers a robust, professional organization with processes and workflows suited to ensuring the concession contract's requirements will be met at a high level.
- Operators asked to attach an organizational chart or similar showing how the operator is organized internally and in relation to any subcontractors, to demonstrate capability to deliver the task.
- Positive weight if the operator's processes/workflows appear well-tested and integrated into the operator's organization.
- Operators asked to describe:
  1. How the organization works with any subcontractors to ensure an efficient establishment process, a stable operational process, and a good service experience for both the contracting authority and end users
  2. How the operator analyzes logged incidents for evaluation purposes
  3. What response times are offered, and how short response times for fault resolution are ensured
  4. The policy for stocking components with long delivery/lead times
- Guidance: the operator's organization may consist of several subcontractors handling different tasks across the establishment and operation phases; the operator should describe how cross-party collaboration happens smoothly and without complication. It is advantageous if the operator's organization continuously improves its practices and services offered — ongoing self-evaluation is viewed positively.

## Named Legislation Referenced
- **AFI-loven § 3, stk. 3** — Danish law implementing the EU Alternative Fuels Infrastructure framework, requiring reasonable, non-discriminatory end-user pricing
- **BEK nr. 1073 af 28/06/2022** — "Bekendtgørelse om ordregiveres indgåelse af aftaler om retten til at virke som operatør af offentligt tilgængelige ladepunkter" (Executive Order on contracting authorities' conclusion of agreements on the right to operate publicly accessible charging points) — §3 requires non-discriminatory pricing terms in operator agreements
- **BUT 3.6.1** — referenced as the underlying tender-evaluation methodology section number ("Bedømmelse af Underkriteriernes Tilfredsstillelse" — sub-criteria satisfaction assessment) governing how Underkriterium B and C are scored; the full BUT document itself is not part of this file.

## Relationship to Companion Document
This document should be read alongside `63b41becca03484da6136b2fab416294.pdf` (processed separately as "Charging Station Establishment and Operation — Requirements Specification," knowledge base path: `claude/knowledge-base/data-reports-misc/ladestandere-kravspecifikation-paradigme.md`), which sets the mandatory minimum technical requirements (Kravspecifikation) that this document's qualitative criteria build on top of — e.g., criterion B.2 explicitly scores bids on how far they exceed the charging-power minimums set in "Kravspecifikation, pkt. 3.2."

## Notes on Extraction Limitations
- This is a legal/procurement template document; content extracted cleanly as structured prose and tables with minimal loss. No charts, graphs, or non-text visual content were identified in the extraction.
- The template's blank "Tilbudsgivers besvarelse" (Bidder's response) fields are intentionally empty in this generic paradigm version, to be completed by an actual bidding operator in a live tender process — they are not omissions from extraction.
