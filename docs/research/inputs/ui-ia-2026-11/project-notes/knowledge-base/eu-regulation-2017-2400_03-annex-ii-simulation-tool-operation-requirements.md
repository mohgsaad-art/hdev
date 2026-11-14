# Commission Regulation (EU) 2017/2400 — Annex II: Requirements and Procedures Related to the Operation of the Simulation Tool

**CELEX number:** 02017R2400
**Consolidated text as of:** 01.01.2026 (consolidated version 007.001)
**Covers:** ANNEX II — "Requirements and procedures related to the operation of the simulation tool" (point 1 — processes the vehicle manufacturer must set up; point 2 — approval-authority assessment; Appendix 1 — information-document model; Appendix 2 — licence model)

This Annex is the operational/organisational backbone referenced throughout Chapter 2 (Articles 6–8) of the Regulation: it defines **what a manufacturer's internal process and IT/data-management setup must look like** to be granted (and keep) a licence to operate the VECTO simulation tool, and **what the approval authority checks** before granting that licence and periodically thereafter.

---

## 1. The processes to be set up by the vehicle manufacturer with a view to the operation of the simulation tool

### 1.1 Minimum required processes
*(►B baseline, with 1.1.1(c) amended by ►M3)*

"The manufacturer shall set up **at least** the following processes:"

#### 1.1.1 — Data management system (input side): sourcing, storing, handling and retrieving input information/input data, and handling certificates

This system covers: sourcing, storing, handling and retrieving of the **input information and input data** for the simulation tool, as well as handling **certificates on the CO2 emissions and fuel consumption related properties** of component families, separate technical unit families and system families.

**The data management system shall at least:**

| Ref | Marker | Requirement (verbatim) |
|---|---|---|
| (a) | ►B | "ensure application of correct input information and input data to specific vehicle configurations" |
| (b) | ►B | "ensure correct calculation and application of standard values" |
| (c) | ►M3 | "verify by means of comparing cryptographic hashes that the input files of components, separate technical units, systems or if applicable their respective families, which are used for the simulation corresponds to the input data of the component, separate technical unit, system or if applicable their respective family for which the certification has been granted" |
| (d) | ►B | "include a protected database for storing the input data relating to the component families, separate technical unit families or system families and the corresponding certificates of the CO2 emissions and fuel consumption related properties" |
| (e) | ►B | "ensure correct management of the changes of specification and updates of components, separate technical units and systems" |
| (f) | ►B | "enable tracing of the components, separate technical units and systems after the vehicle is produced" |

**Reading note:** point (c) is a direct, mandatory **hash-verification control** — the manufacturer's data-management system must itself verify (not merely store) that the input files actually used in a given simulation run cryptographically match the certified input data for that component/family. This is a non-negotiable IT-integrity control the regulation imposes on the manufacturer's own systems (distinct from the approval authority's separate hash-based checks elsewhere in the Regulation, e.g. Article 9(3)-(5), Article 17(4)).

#### 1.1.2 — Data management system (output side): retrieving inputs, running calculations, storing outputs

A second, distinct data management system covering: **retrieving** the input information and input data, running the **calculations by means of the simulation tool**, and **storing the output data**.

**This data management system shall at least:**

| Ref | Marker | Requirement (verbatim) |
|---|---|---|
| (a) | ►B | "ensure a correct application of cryptographic hashes" |
| (b) | ►B | "include a protected database for storing the output data" |

**Reading note:** the Regulation deliberately requires **two separate data-management systems** — one for the certified-input side (1.1.1) and one for the calculation/output side (1.1.2) — each with its own protected database and its own hash-integrity control. For a sizing/modelling tool positioning itself as "PVsyst for EVs," this two-system separation (input provenance/integrity vs. output storage/integrity) is a useful architectural pattern to mirror if the tool aims to be "auditable" in a VECTO-equivalent sense.

#### 1.1.3 — Process for consulting the distribution platform and keeping the tool up to date
*(►B)*

"Process for consulting the dedicated electronic distribution platform referred to in Article 5(2) and Article 10(1) and (2), as well as downloading and installing the latest versions of the simulation tool."

#### 1.1.4 — Staff training
*(►B)*

"Appropriate training of staff working with the simulation tool."

---

## 2. Assessment by the approval authority

### 2.1 Verification scope
*(►B, with sub-points amended by ►M3)*

"The approval authority shall verify whether the processes set out in point 1 related to the operation of the simulation tool have been set up."

**The approval authority shall also verify the following:**

| Ref | Marker | Requirement (verbatim) |
|---|---|---|
| (a) | ►B | "the functioning of the processes set out in points 1.1.1, 1.1.2 and 1.1.3 and the application of the requirement set out in point 1.1.4" |
| (b) | ►M3 | "that the processes used during the demonstration are applied in the same manner in all the production facilities manufacturing vehicles belonging to the application case concerned" |
| (c) | ►B | "the completeness of the description of the data and process flows of operations related to the determination of the CO2 emissions and fuel consumption of the vehicles" |

**Minimum verification depth, for point (a):**
*(►M3)* "For the purpose of the second paragraph, point (a), the verification shall include determination of the CO2 emissions and fuel consumption of **at least one vehicle from each production facility** for which the licence has been applied for."

**Cross-reference (outside this file's range, but material):** this point-2 assessment is the same assessment referenced in Article 6(3) (accompanying the licence application) and in Article 20(2) (performed **four times per year** by the approval authority to verify ongoing adequacy of the licensed processes, see Chapter 5 of the general-provisions file).

---

## Appendix 1 — Model of an information document for the purposes of operating the simulation tool with a view to determining the CO2 emissions and fuel consumption of new vehicles

*(mixed ►B / ►M3 — this is the template referenced by Article 6(2) as the required form for the **licence application**)*

**SECTION I**

1. *(►M3)* Name and address of vehicle manufacturer:
2. *(►B)* Assembly plants for which the processes referred to in point 1 of Annex II of Regulation (EU) 2017/2400 have been set up with a view to the operation of the simulation tool:
3. *(►M3)* Application case covered:
4. *(►B)* Name and address of the manufacturer's representative (if any)

**SECTION II**

1. Additional information
   1.1 Data and process flow handling description (e.g. flow chart)
   1.2 Description of quality management process
   1.3 Additional quality management certificates (if any)
   1.4 Description of simulation tool data sourcing, handling and storage
   1.5 Additional documents (if any)
2. Date:
3. Signature:

---

## Appendix 2 — Model of a licence to operate the simulation tool with a view to determining CO2 emissions and fuel consumption of new vehicles

*(►B baseline — this is the template referenced by Article 7(2) as the required form for the **granted licence** itself)*

**Maximum format: A4 (210 × 297 mm)**

**Header fields on the licence form:**
- "LICENCE TO OPERATE THE SIMULATION TOOL WITH A VIEW TO DETERMINING CO2 EMISSIONS AND FUEL CONSUMPTION OF NEW VEHICLES"
- Communication concerning (tick/select one, footnote (1) "Delete where not applicable"):
  - granting
  - extension
  - refusal
  - withdrawal
- Administration stamp — "of the licence to operate simulation tool with regard to Regulation (EC) No 595/2009 as implemented by Regulation (EU) 2017/2400."
- Licence number:
- Reason for extension:

**SECTION I**
*(►M3)*
0.1 Name and address of vehicle manufacturer:
0.2 Production facilities and/or assembly plants for which the processes referred to in point 1 of Annex II to Commission Regulation (EU) 2017/2400 (footnote (2): OJ L 349, 29.12.2017, p. 1) have been set up with a view to the operation of the simulation tool
0.3 Application case covered:

**SECTION II**
*(►B)*
1. Additional information
   1.1 Assessment report performed by an approval authority
   1.2 Data and process flow handling description (e.g. flow chart)
   1.3 Description of quality management process
   1.4 Additional quality management certificates (if any)
   1.5 Description of simulation tool data sourcing, handling and storage
   1.6 Additional documents (if any)
2. Approval authority responsible for carrying out the assessment
3. Date of the assessment report
4. Number of assessment report
5. Remarks (if any): see Addendum
6. Place
7. Date
8. Signature

**Footnotes to Appendix 2:**
1. "Delete where not applicable (there are cases where nothing needs to be deleted when more than one entry is applicable)"
2. OJ L 349, 29.12.2017, p. 1. [i.e. the original publication reference of this Regulation itself]

---

## Practical synthesis — IT-security / data-integrity requirements implied by Annex II

For the "HDEV sizing & Modelling Tool" project, the following are the **explicit, verifiable** IT/process requirements this Annex places on a VECTO-licensed manufacturer (useful as a checklist if the project wants to describe how an OEM's VECTO compliance process works, or to design an analogous audit trail in the sizing tool):

1. **Two logically separated data-management systems**: (i) input/certificate management (sourcing, storage, correct application of standard values, hash-verification against certification, protected database, change management, post-production traceability); (ii) calculation/output management (hash application, protected output database).
2. **Mandatory cryptographic-hash verification** at the point input files are used in a simulation run, matching them against the certified input data (Annex II, point 1.1.1(c), added by ►M3) — not just storage of hashes, but active verification.
3. **A defined process for keeping current** with the Commission's distribution platform and tool updates (Article 5(2)/10(1)-(2) cross-reference).
4. **Documented staff training** on the simulation tool.
5. **Uniform process application across all production facilities** within an application case (►M3 addition) — the approval authority must check this at **every facility**, with a minimum of **one full CO2/fuel-consumption determination per facility** as part of the licensing assessment.
6. **Full process documentation** (flow charts, QM descriptions, data sourcing/handling/storage description) as a mandatory attachment to both the licence application (Appendix 1) and the granted licence record (Appendix 2) — i.e. the regulator keeps the manufacturer's own process documentation on file as part of the licence itself, not just the licence number.

**Nothing in this Annex specifies**: particular IT security standards (e.g. ISO 27001), specific hashing algorithms, specific database technologies, or retention formats — the Regulation is deliberately **technology-neutral** on *how* these controls are implemented, only *that* they exist and are verified. This is worth flagging explicitly: do not assume a specific technical standard is mandated unless it is found in the simulation tool's own user manual or in another Annex not covered by this file.

**Cross-references outside this file's assigned range:**
- Article 5(2): the dedicated electronic distribution platform.
- Article 6: licence application procedure (uses Appendix 1 of this Annex).
- Article 7: licence granting (uses Appendix 2 of this Annex).
- Article 8: subsequent changes to licensed processes.
- Article 9(3)-(5): cryptographic hash obligations on manufacturer's records file / vehicle information file / customer information file (a related but distinct hash regime from the Annex II, 1.1.1(c) internal verification control).
- Article 20(2): the four-times-per-year approval-authority assessment (same "point 2 of Annex II" assessment referenced here).
