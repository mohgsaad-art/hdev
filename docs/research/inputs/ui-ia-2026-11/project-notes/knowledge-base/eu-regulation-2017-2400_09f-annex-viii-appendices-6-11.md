# Annex VIII — Verifying Air Drag Data: Appendices 6–11 (Conformity of Production, Standard Values, Markings, Simulation Tool Input Parameters, CFD Method Approval, CFD Licence Model)

**Source document:** Commission Regulation (EU) 2017/2400 (consolidated text, EUR-Lex)
**CELEX number:** 02017R2400
**Consolidation date:** 01.01.2026 (consolidated version 007.001)
**Range covered in this file:** Annex VIII, Appendices 6–11 (source lines 15345–15979; page markers 372–387)
**Amendment markers:** ►B = original 2017 baseline; ►M1 = Reg (EU) 2019/318; ►M3 = Reg (EU) 2022/1379; ►M4 = Reg (EU) 2025/258.

> **Same formula-reconstruction caveat as file `09c` applies to Appendix 10 below.** The OCR text garbled mathematical symbols (√, ≤, ≥, Σ, ×, parentheses, the decimal comma) into unrelated characters. I reconstructed them using the same character mapping documented in file `09c-annex-viii-input-data-and-validity-criteria.md` (ð→"(", Þ→")", Ä→"−", þ→"+", Ï→"≤", Ü→"×", ¼→"=", ";" between digits→",", "ffiffi...q" runs→√[...]). **This is my inferred reconstruction, not a verified transcription of the rendered PDF — verify against the original before encoding into simulation logic.**

---

## Appendix 6 — Conformity of the certified CO2 emissions and fuel consumption related properties (▼M3 title)

### 1. Verification method and additional provisions (▼B, with ▼M4 deletion)

Conformity shall be verified by **constant speed tests** as laid down in section 3 of the main part of this Annex. Additional provisions:

i. The ambient temperature of the constant speed test shall be within **± 5 °C** of the value from the certification measurement. Verified based on the average temperature from the first low speed tests as calculated by the pre-processing tool.

**▼M4** — (a sub-point here was deleted, shown as `__________` in the consolidated text; no replacement given.)

**▼B**
All conformity-of-production tests shall be **supervised by the approval authority**.

### 2. Failure criterion and retest allowance (▼B, with ▼M1 and ▼M4 amendments)

A vehicle **fails** the conformity test if the measured Cd·Acr(0) value is **higher than the Cd·Adeclared value declared for the parent vehicle plus a 7,5 % tolerance margin**.

If a first test fails, **up to two additional tests** on different days with the same vehicle may be performed. **►M1** Where the measured Cd·Acr(0) value of **all** performed tests exceeds Cd·Adeclared + 7,5 %, **Article 23 of this Regulation shall apply**. ◄

**▼M1**
For calculation of the Cd·Acr(0) value, the air drag pre-processing tool version of the **parent air drag** in accordance with Attachment 1 of Appendix 2 to this Annex shall be used.

**▼M4**
Notwithstanding the second paragraph, where the measured Cd·Acr(0) value of all tests performed in accordance with point 3.1 exceeds Cd·Adeclared + 7,5 %, the approval authority shall **investigate whether the approved CFD method has been applied correctly** for other air drag families with air drag characteristics determined per point 3.0.2. If it was not applied correctly, **Article 23 of this Regulation shall apply** to all air drag types set out on the basis of the approved CFD method, or to the air drag types concerned if the method was not applied correctly only for some of them.

### 3. Number of vehicles to be tested per year (▼M3)

The number of vehicles tested for conformity per year of production shall be determined based on **Table 17**, applied **separately** to medium lorries, heavy lorries and heavy buses.

### Table 17 — Number of vehicles to be tested for conformity per year of production

| Number of CoP tested vehicles | Schedule | Number of CoP-relevant vehicles produced the year before |
|---|---|---|
| 0 | — | ≤ 25 |
| 1 | every 3rd year (¹) | 25 < X ≤ 500 |
| 1 | every 2nd year | 500 < X ≤ 5 000 |
| 1 | every year | 5 000 < X ≤ 15 000 |
| 2 | every year | ≤ 25 000 |
| 3 | every year | ≤ 50 000 |
| 4 | every year | ≤ 75 000 |
| 5 | every year | ≤ 100 000 |
| 6 | every year | 100 001 and more |

(¹) The CoP test shall be performed within the first two years.

> Note: rows 2–6 of Table 17 are expressed as "≤ X" cumulative thresholds in the source (not "A < X ≤ B" ranges like the first three rows) — reproduced exactly as given; the apparent overlap/ambiguity between rows is in the source text itself.

For establishing production numbers, only air drag data falling under this Regulation's requirements, and **not** allocated standard air drag values under Appendix 7, shall be considered.

### 3.1 Additional CFD-method testing (▼M4)

Notwithstanding point 3, if the manufacturer has used an **approved CFD method** per point 3.0.2 to determine air drag characteristics, additional vehicles shall also be tested for conformity per **Table 17a**.

### Table 17a — Number of vehicles to be tested for conformity per year of production for the usage of the CFD method

| Number of CoP tested vehicles | Schedule | Number of vehicles produced with air drag certified using the approved CFD method |
|---|---|---|
| 1 | every 3rd year | ≤ 1 000 |
| 1 | every 2nd year | 1 000 < X ≤ 5 000 |
| 1 | every year | 5 000 < X ≤ 15 000 |
| 2 | every year | 15 000 < X ≤ 25 000 |
| 3 | every year | 25 000 < X ≤ 50 000 |
| 4 | every year | 50 001 and more |

### 4. Vehicle selection provisions (▼B, with ▼M3/▼M4 amendments)

**4.1.** Only vehicles from the production line shall be tested.
**4.2.** Only vehicles fulfilling the constant-speed-testing provisions of section 3.3 of the main part of this Annex shall be selected.
**▼M3**
**4.3.** Tyres are considered part of the measurement equipment and can be selected by the manufacturer.
**4.4.** Vehicles in families where the air drag value was determined via transfer from other vehicles per Appendix 5 point 5 are **not subject** to conformity testing.
**4.5.** Vehicles using standard values for air drag per **Appendix 8** [as written in the source — note: Appendix 7 is the "Standard values" appendix in this Annex; this appears to be another cross-reference inconsistency, since Appendix 8 in this Annex is actually "Markings." Flagging rather than silently correcting — likely intended as Appendix 7] are **not subject** to conformity testing.
**4.6.** **►M4** For the tests referred to in point 3, the first vehicle to be tested shall be selected from the air drag type or air drag family representing the **highest production numbers** in the corresponding year. ◄ Any additional vehicles shall be selected from all air drag families, agreed between manufacturer and approval authority based on families/groups already tested. If only one test per year or less is required, the vehicle shall always be selected from all air drag families, agreed between manufacturer and approval authority.
**▼M4**
**4.7.** For the tests referred to in point 3.1, only vehicles for which air drag characteristics were determined with an **approved CFD method** shall be selected.

### 5. Verification timing (▼B)

After a vehicle is selected for conformity testing, the manufacturer must verify conformity within **12 months**. The manufacturer may request a **6-month extension** if unable to verify within the required period due to weather conditions.

---

## Appendix 7 — Standard values (▼B)

Describes standard values for the declared air drag value **Cd·Adeclared**. Where standard values apply, **no air drag input data** shall be provided to the simulation tool — standard values are allocated automatically by the simulation tool.

### Table 18 — Standard values for Cd·Adeclared for heavy lorries

| Vehicle group | Standard value Cd·Adeclared [m²] |
|---|---|
| 1, 1s | 7,1 |
| 2 | 7,2 |
| 3 | 7,4 |
| 4 | 8,4 |
| 5 | 8,7 |
| 9 | 8,5 |
| 10 | 8,8 |
| 11 | 8,5 |
| 12 | 8,8 |
| 16 | 9,0 |

(Points 2 and 3 of this Appendix are empty "—" in the source — no content, reproduced as-is.)

### Table 21 — Standard values for Cd·Adeclared for heavy buses (point 4)

For vehicle sub-groups where aerodynamic drag measurement is not allowed (per point 7.3 of Appendix 5), standard values are **not relevant**.

| Vehicle parameter sub-group | Standard value Cd·Adeclared [m²] |
|---|---|
| 31a | not relevant |
| 31b1 | not relevant |
| 31b2 | 4,9 |
| 31c | not relevant |
| 31d | not relevant |
| 31e | not relevant |
| 32a | 4,6 |
| 32b | 4,6 |
| 32c | 4,6 |
| 32d | 4,6 |
| 32e | 5,2 |
| 32f | 5,2 |
| 33a | not relevant |
| 33b1 | not relevant |
| 33b2 | 5,0 |
| 33c | not relevant |
| 33d | not relevant |
| 33e | not relevant |
| 34a | 4,7 |
| 34b | 4,7 |
| 34c | 4,7 |
| 34d | 4,7 |
| 34e | 5,3 |
| 34f | 5,3 |
| 35a | not relevant |
| 35b1 | not relevant |
| 35b2 | 5,1 |
| 35c | not relevant |
| 36a | 4,8 |
| 36b | 4,8 |
| 36c | 4,8 |
| 36d | 4,8 |
| 36e | 5,4 |
| 36f | 5,4 |
| 37a | not relevant |
| 37b1 | not relevant |
| 37b2 | 5,1 |
| 37c | not relevant |
| 37d | not relevant |
| 37e | not relevant |
| 38a | 4,8 |
| 38b | 4,8 |
| 38c | 4,8 |
| 38d | 4,8 |
| 38e | 5,4 |
| 38f | 5,4 |
| 39a | not relevant |
| 39b1 | not relevant |
| 39b2 | 5,2 |
| 39c | not relevant |
| 40a | 4,9 |
| 40b | 4,9 |
| 40c | 4,9 |
| 40d | 4,9 |
| 40e | 5,5 |
| 40f | 5,5 |

### Table 22 — Standard values for Cd·Adeclared for medium lorries (point 5)

| Vehicle group | Standard value Cd·Adeclared [m²] |
|---|---|
| 53 | 5,8 |
| 54 | 2,5 |

> Note: Table 22 lists only groups 53 and 54, even though Table 16a (Appendix 5, file `09e`) references transfer relationships involving groups 51 and 52 as well (51↔53, 52↔54). This may mean groups 51/52 always receive standard values via the Table 16a transfer-from-53/54 path, or it may be an incomplete table in the source — reproduced exactly as extracted, flagged for the user's awareness rather than inferring missing rows.

---

## Appendix 8 — Markings (▼M3 title)

A certified vehicle's cabin or bodywork shall bear:

**▼M1**
1.1. The manufacturer's name or trade mark

**▼B**
1.2. The make and identifying type indication as recorded in paragraphs 0.2 and 0.3 of Appendix 2 to this Annex

1.3. The certification mark: a rectangle surrounding the lower-case letter **'e'** followed by the distinguishing number of the Member State that granted the certificate:

| Number | Member State |
|---|---|
| 1 | Germany |
| 2 | France |
| 3 | Italy |
| 4 | Netherlands |
| 5 | Sweden |
| 6 | Belgium |
| 7 | Hungary |
| 8 | Czech Republic |
| 9 | Spain |
| 11 | United Kingdom |
| 12 | Austria |
| 13 | Luxembourg |
| 17 | Finland |
| 18 | Denmark |
| 19 | Romania |
| 20 | Poland |
| 21 | Portugal |
| 23 | Greece |
| 24 | Ireland |
| 25 | Croatia |
| 26 | Slovenia |
| 27 | Slovakia |
| 29 | Estonia |
| 32 | Latvia |
| 34 | Bulgaria |
| 36 | Lithuania |
| 49 | Cyprus |
| 50 | Malta |

> Note: numbers 10, 14, 15, 16, 22, 28, 30, 31, 33, 35, 37–48 are absent from this list, exactly as given in the source (these correspond to other UNECE distinguishing numbers not assigned to, or not listed for, this certification scheme).

**1.4. ►M3** The certification mark shall also include, near the rectangle, the **'base certification number'** as specified for Section 4 of the type-approval number set out in Annex I to **Regulation (EU) 2020/683**, preceded by the two figures indicating the sequence number assigned to the latest technical amendment to this Regulation, and by a character **'P'** indicating the approval was granted for air drag. For this Regulation, **the sequence number shall be 02**. ◄

**1.4.1. Example and dimensions of the certification mark (▼M3)**
**[Figure referenced in source but not visually extracted from this text-only OCR — an example certification mark graphic, described in text as follows:]**

> The certification mark affixed to a cabin shows that the type concerned has been certified in **Poland (e20)**, pursuant to this Regulation. The first two digits (**02**) indicate the sequence number assigned to the latest technical amendment to this Regulation. The following letter indicates the certificate was granted for air drag (**P**). The last five digits (**00005**) are those allocated by the approval authority for the air drag, as the base certification number.

**1.5.** The certification mark shall be affixed to the cabin **indelibly and clearly legibly**, visible when the cabin is installed on the vehicle, and affixed to a part necessary for normal cabin operation not normally requiring replacement during cabin life. **►M1** Markings/labels/plates/stickers must be durable for the useful life of the cabin, clearly legible and indelible. ◄ The manufacturer shall ensure markings cannot be removed without destroying or defacing them.

### 2. Numbering (▼M3)

**2.1.** Certification number for air drag shall comprise:

> `eX*YYYY/YYYY*ZZZZ/ZZZZ*P*00000*00`

| Section 1 | Section 2 | Section 3 | Additional letter to Section 3 | Section 4 | Section 5 |
|---|---|---|---|---|---|
| Indication of country issuing the certificate | HDV CO2 determination Regulation '2017/2400' | Latest amending Regulation (ZZZZ/ZZZZ) | P = Air drag | Base certification number 00000 | Extension 00 |

---

## Appendix 9 — Input parameters for the simulation tool (▼B)

### Introduction

Describes the list of parameters to be provided by the vehicle manufacturer as input to the simulation tool. The applicable **XML schema** and example data are available at the dedicated electronic distribution platform. The XML is **automatically generated by the air drag pre-processing tool**.

### Definitions

1. **'Parameter ID'**: unique identifier used in the simulation tool for a specific input parameter or set of input data.
2. **'Type'**: data type of the parameter:

| Type | Description |
|---|---|
| string | sequence of characters in ISO8859-1 encoding |
| token | sequence of characters in ISO8859-1 encoding, no leading/trailing whitespace |
| date | date and time in UTC, format `YYYY-MM-DDTHH:MM:SSZ` (italic letters = fixed characters), e.g. '2002-05-30T09:30:10Z' |
| integer | value with integral data type, no leading zeros, e.g. '1800' |
| double, X | fractional number with exactly X digits after the decimal point ('.'), no leading zeros; e.g. for 'double, 2': '2345.67'; for 'double, 4': '45.6780' |

3. **'Unit'**: physical unit of the parameter.

### Table 1 — Input parameters 'AirDrag'

| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| Manufacturer | P240 | token | | |
| Model | P241 | token | | |
| CertificationNumber | P242 | token | | Identifier of the component as used in the certification process |
| Date | P243 | date | | Date and time when the component hash is created |
| AppVersion | P244 | token | | Number identifying the version of the air drag pre-processing tool |
| CdxA_0 | P245 | double, 2 | [m²] | Final result of the air drag pre-processing tool |
| DeltaCdxA_CFD (▼M4) | P561 | double, 2 | [m²] | Incremental difference ΔCd·Acr(0)_CFD obtained by means of CFD per point 3.0.2. Only relevant if the CFD option is applied |
| Licence number CFD method (▼M4) | P562 | token | [-] | Only relevant if the CFD option is applied |
| DeltaCdxA_declared (▼M4) | P563 | double, 2 | [m²] | Difference between Cd·Adeclared (per point 3.0.3) and ΔCd·Acr(0) (per point 3.0.1 or 3.0.2, as applicable) |
| DeltaTransferredCdxA (▼M4) | P564 | double, 2 | [m²] | Delta Cd·A from transfer to related families in other vehicle groups, per Table 16 (Appendix 5, heavy lorries), Table 16a (Appendix 5, medium lorries), or Table 16b (Appendix 5, heavy buses). If no transfer rule applied, CdxA_0 shall be provided. If transferred by copying CdxA from another vehicle group, '0' shall be provided. If no transfer rule has been applied, leave empty |

**▼M1**
In case standard values per **Appendix 7** are used in the simulation tool, **no input data for the air drag component** shall be provided — standard values are allocated automatically per the vehicle group scheme.

---

## Appendix 10 — Approval of the CFD method (▼M1 title; body largely ▼M4)

### 1. Validation procedure overview

For determining air drag characteristics using a CFD method as described in point 3.0.2, the validity of the CFD method shall be approved as follows:

(a) Application of the CFD method shall be in accordance with **Appendix 1 of Annex VIII to Regulation (EU) 2018/858**.

(b) Specific validation using physical tests shall be based on **two different vehicles 'A' and 'B'**, with B being the configuration with lower air drag. A and B shall fulfil:

(i) For medium and heavy lorries: meet the criteria of point 4.1 of Appendix 5 (special cases per point 2 of Appendix 5 also considered).

(ii) The air drag difference between the two vehicles shall meet:

> ΔCd·Acr(0)_CST > 3,5 % × [ (Cd·Acr(0)_CST,avg,A + Cd·Acr(0)_CST,avg,B) / 2 ]

where:

> ΔCd·Acr(0)_CST = Cd·Acr(0)_CST,avg,A − Cd·Acr(0)_CST,avg,B

- `Cd·Acr(0)_CST,avg,A` = average air drag value of vehicle A, measured in a series of constant speed tests per point 1(d).
- `Cd·Acr(0)_CST,avg,B` = average air drag value of vehicle B, measured analogously.

(c) The manufacturer shall perform the following steps to determine the air drag difference between A and B using CFD:

**(i) Conditions to be met in CFD simulations:**
1. Vehicle geometries used in CFD simulations shall correspond to the vehicle setup prescribed in point 3.3 for the constant speed test.
2. Air speed in the simulation: **90 km/h** for lorries, **100 km/h** for buses.
3. Only **0° yaw angle** shall be considered.
4. All wheels (tyres and rims) shall be modelled as **rotating elements** (rotating boundary conditions or real rotating components) with the corresponding rotational speed.
5. The ground of the simulation domain shall be modelled with a **tangential velocity opposite to the vehicle's advancing direction**.
6. The simulation domain shall be discretised with a **minimum of 60 million volume elements**, including mesh refinements at wake regions and other key aerodynamic areas.
7. Steady-state CFD methods: run for a **minimum of 2 000 iterations**.
8. Transient CFD methods: run for a **minimum of 10 seconds** of simulation time.

**(ii)** The incremental difference ΔCd·Acr(0)_CFD between vehicles A and B using the CFD method shall be calculated as:

> ΔCd·Acr(0)_CFD = Cd·Acr(0)_CFD,A − Cd·Acr(0)_CFD,B

where Cd·Acr(0)_CFD corresponds to the average of:
- the last, at least, **400 iterations** for steady-state methods;
- the last, at least, **5 seconds** of simulation time for transient methods.

**(iii)** The ΔCd·Acr(0)_CFD value shall be submitted to the approval authority **before starting the constant speed tests** described in point (d).

(d) For both vehicles A and B, a reference value for air drag characteristics — Cd·Acr(0)_CST,avg,A and Cd·Acr(0)_CST,avg,B respectively — shall be determined from a series of constant speed tests:

**(i)** The reference value Cd·Acr(0)_CST,avg shall be the **arithmetic mean** of the Cd·Acr(0)_CST values from all available constant speed tests performed with a given vehicle. Only valid results per point 3.10 shall be considered. It is **not permitted** to exclude available and valid constant speed test results for the vehicle configuration under consideration, unless justified to the approval authority.

**(ii)** The **95 % confidence interval (CI95)** of the mean of test data, Cd·Acr(0)_CST,avg, shall fall within the range **Cd·Acr(0)_CST,avg ± 2,5 %**, determined by:

> (s / √n) × t ≤ 0,025 × x̄

where:

> s = √[ (1/(n−1)) × Σ (i=1 to n) (xᵢ − x̄)² ]
>
> x̄ = (1/n) × Σ (i=1 to n) xᵢ

- `s` = standard deviation of the sample for Cd·Acr(0)_CST.
- `x̄` = mean average value of the sample for Cd·Acr(0)_CST.
- `n` = number of constant speed tests for the considered vehicle configuration.
- `xᵢ` = air drag value Cd·Acr(0)_CST obtained from a single constant speed test.
- `t` = score for the 95 % confidence interval of the double-sided t-distribution, per **Table 1** below.

**Table 1 — t-distribution scores by number of tests**

| # tests (n) | t |
|---|---|
| 3 | 4,303 |
| 4 | 3,182 |
| 5 | 2,776 |
| 6 | 2,571 |
| 7 | 2,447 |
| 8 | 2,365 |
| 9 | 2,306 |
| 10 | 2,262 |
| 11 | 2,228 |

> Note: these are the standard two-sided 95 %-confidence t-distribution critical values for degrees of freedom = n−1 (i.e. df = 2 through 10), consistent with published Student's t-tables. This cross-check supports (but does not replace) verifying the exact transcription against the source PDF.

**(iii)** A **minimum of three** valid constant speed tests shall be performed per vehicle configuration and included in the calculation.

**(iv)** If the criterion in (ii) is not met, **additional constant speed tests** shall be performed.

**(v)** If the criterion in (ii) is still not met after **eleven** valid constant speed tests, all tests for this vehicle configuration shall be considered **void** and may not be used for this Appendix's purposes.

**(vi)** The reference value for the air drag difference between the two vehicles, ΔCd·Acr(0)_CST, shall be calculated as:

> ΔCd·Acr(0)_CST = Cd·Acr(0)_CST,avg,A − Cd·Acr(0)_CST,avg,B

(e) Compliance of the CFD method shall be demonstrated by fulfilling:

> ΔCd·Acr(0)_CST − TOL < ΔCd·Acr(0)_CFD < ΔCd·Acr(0)_CST + TOL

where:

> TOL = 0,035 × [ (Cd·Acr(0)_CST,avg,A + Cd·Acr(0)_CST,avg,B) / 2 ]

> **Note on operator reconstruction:** unlike most inequalities in this Annex (which I reconstructed as "≤"), the OCR glyphs for this specific pair of comparisons rendered differently and are reproduced here as **strict inequality "<"** based on the distinct glyph pattern in the source for this formula (different from the "Ï" glyph used elsewhere for ≤). This distinction (strict `<` vs `≤`) could matter for edge-case compliance determination — **verify against the original PDF before relying on it.**

### 2. Information to accompany the CFD-method approval application

For each vehicle A and B:
(a) CFD software used, including version number information.
(b) Values for Cd·Acr(0)_CFD in m².
(c) The **SHA256 hash** of the CFD simulation file (geometry data, mesh and physics settings, domain discretisation, boundary conditions, flow field results). If split into several files, they shall be stored under a single compressed file (e.g. `*.zip`), and the SHA256 hash corresponds to that single compressed file. All simulation setup parameters (mesh, technical parameters necessary to reproduce the simulation) and the associated CFD tool version shall be **kept by the manufacturer for 10 years**, and reproduced at the approval authority's request.
(d) Raw data of the evolution curve of Cd·Acr(0)_CFD versus iteration (steady-state) or versus time (transient), in `*.csv` format.
(e) Post-processing images of the CFD simulations per the principles illustrated by **Figures 3 to 6 in Annex V of Implementing Regulation (EU) 2022/1362**. **[Figures referenced in an external regulation, not visually extracted here.]**
(f) Values for Cd·Acr(0)_CST and Cd·Acr(0)_CST,avg.
(g) Air drag information document per **Appendix 2** to this Annex, accompanied by test reports for each valid constant speed test.

### 3–5. Scope, issuance, and renewal of CFD method approval

**3.** Approval of the CFD method shall be carried out **separately** for application on lorries and on buses.

**4.** If compliance is demonstrated per points 1 and 2, the approval authority shall issue a licence per the model in **Appendix 11**.

**5.** The approval shall be **renewed** in any of the following cases:
(a) A change is made to the CFD method that could potentially affect the validity of results.
(b) After **5 years** of approval.
(c) At the request of the approval authority.

If not renewed, the approval shall be considered **withdrawn**, and the CFD method shall no longer be used for this Annex's purposes.

Within the first 5 years of initial approval, any renewal may use the **original dataset** from constant speed testing. After that, a **new set of test data** performed on different vehicles (if such vehicles exist) shall be provided for the renewal.

---

## Appendix 11 — Model of a licence to apply a CFD method for air drag determination (▼M4)

**[Figure/form layout referenced in source but not visually extracted from this text-only OCR — structured licence form, reproduced below in field order.]**

Maximum format: **A4 (210 × 297 mm)**

> LICENCE TO APPLY A CFD METHOD FOR AIR DRAG DETERMINATION

Communication concerning:
— granting (¹)
— refusal (¹)
— withdrawal (¹)

(¹) delete if not applicable

**Administration stamp** [Figure referenced in source but not visually extracted from this text-only OCR]

> of the licence to apply a CFD method with regard to air drag determination in accordance with Annex VIII to Regulation (EU) 2017/2400.

CFD method licence number (numbering system per point 2 of **Appendix 8**, with the additional letter to Section 3 'P' replaced by **'CFD'**): ___
Reason for refusal / withdrawal: ___

### SECTION I

0.1. Name and address of the manufacturer:
0.2. Vehicles covered by licence (lorries, buses):
0.3. CFD software used including version number information
0.4. SHA256 hashes in accordance with point 2, item (c) of this Appendix

### SECTION II

1. Approval authority responsible for the assessment
2. Date of the assessment report
3. Number of the assessment report
4. Remarks (if any)
5. Place
6. Date
7. Signature

Attachments (for each vehicle configuration A and B):
1. Raw data of the evolution curve of Cd·Acr(0)_CFD
2. Post-processing images of the CFD simulations
3. Air drag information document
4. Test reports for each valid constant speed test

*(The source list is unnumbered for the last item "Test reports for each valid constant speed test" — reproduced as a 4th attachment item for clarity, though the source text itself does not prefix it with "4.")*

---

## Cross-references used in this section

- Regulation (EU) 2020/683, Annex I — type-approval numbering, Section 4 "base certification number" (external)
- Regulation (EU) 2018/858, Annex VIII, Appendix 1 — CFD method application requirements (external)
- Implementing Regulation (EU) 2022/1362, Annex V, Figures 3–6 — CFD post-processing image conventions (external)
- Article 23 of Regulation (EU) 2017/2400 — consequences of conformity-of-production failure (external to this Annex; not reproduced)
- Appendix 2 — Air drag information document (see file `09d`)
- Appendix 5 — air drag family and transfer tables (see file `09e`)
- Appendix 7 — standard values (this file, above)
- Appendix 8 — markings/certification numbering (this file, above)

## Figures referenced but not visually extracted

- Appendix 8, point 1.4.1 — example certification mark graphic (described in text, see above).
- Appendix 1 and Appendix 11 — certificate/licence form layout and "Administration stamp" graphics.
- Appendix 10, point 2(e) — reference to Figures 3–6 of Annex V of Implementing Regulation (EU) 2022/1362 (external document, not part of this Annex's own figures).

## Open items flagged for the user in this file

1. **Appendix 6, point 4.5** cross-references "Appendix 8" for standard air drag values — but Appendix 8 in this Annex is "Markings," not standard values (that is Appendix 7). Likely a drafting/consolidation cross-reference error; verify against the original PDF.
2. **Table 22 (Appendix 7)** lists standard values only for medium-lorry groups 53 and 54, not 51/52, despite Table 16a (Appendix 5) defining a transfer relationship for all four groups. Possibly intentional (51/52 always use the Table 16a transfer path) — flagged, not resolved.
3. **Appendix 10, section 1(e), TOL formula** — the comparison operator was reconstructed as strict "<" based on a different OCR glyph than the "≤" used elsewhere; double-check against the source.
