# Annex III — Input Information Relating to the Characteristic of the Vehicle
## Part C: Advanced Driver Assistance Systems, Cargo Volume, Transfer of Results, Hydrogen Storage Capacity, Article 9 Exemptions

**Source document:** Commission Regulation (EU) 2017/2400 (implementing Regulation (EC) No 595/2009) — VECTO methodology
**CELEX number:** 02017R2400
**Consolidated as of:** 01.01.2026 (consolidated text, version 007.001)
**Source lines covered in this file:** approx. 3234–3272 (Table 6, ADAS input parameters), 3589–3689 (§8, ADAS definitions + Table 12 combinations), 3689–3736 (§9, Cargo volume, Table 13 + Figure 3), 4026–4095 (§11, Transfer of results between vehicles), 4096–4184 (§12, Usable capacity of hydrogen fuel storage system, Tables 16–17), 4185–4315 (Appendix 1, Vehicle technologies exempted under Article 9, Table 1 of Appendix 1)
**Amendment markers:** ►B = original 2017; ►M1 = Reg 2019/318; ►M2 = Reg 2020/1181; ►M3 = Reg 2022/1379; ►M4 = Reg 2025/258.

---

## Table 6 — Input parameters "Advanced driver assistance systems"

Column headers: Heavy lorries / Medium lorries / Heavy buses (primary vehicle) / Heavy buses (complete and completed vehicle) — all four marked X for every row in this table (i.e. these parameters apply uniformly across all vehicle classes and build stages).

| Parameter name | Parameter ID | Type | Unit | Description / Reference |
|---|---|---|---|---|
| EngineStopStart | P271 | boolean | [-] | Per point 8.1.1. Input only for **pure ICE vehicles and HEV**. ►M4 **For OVC-HEV the input shall be set to `true`.** ◄ |
| EcoRollWithoutEngineStop | P272 | boolean | [-] | Per point 8.1.2. Input only for **pure ICE vehicles**. |
| EcoRollWithEngineStop | P273 | boolean | [-] | Per point 8.1.3. Input only for **pure ICE vehicles**. |
| PredictiveCruiseControl | P274 | string | [-] | ►M4 Per point 8.1.4. Allowed values: `none`, `1,2`, `1,2,3` ◄ (i.e. which PCC functionality subset is implemented — see §8.1.4 below) |
| APTEcoRollReleaseLockupClutch | P333 | boolean | [-] | Only relevant for APT-S/APT-P transmissions combined with any Eco-roll function. Set `true` if "functionality (2)" per point 8.1.2 is the **predominant** Eco-roll mode. Input only for **pure ICE vehicles**. |

**HDEV-tool relevance:** every row in Table 6 is explicitly scoped to **pure ICE vehicles and HEV only** (with the single `OVC-HEV → EngineStopStart=true` exception under ▼M4) — i.e. the regulation treats fuel-saving ADAS (eco-roll, stop-start) as **not applicable/meaningless for PEV and FCHV**, since they have no ICE to stop/start or decouple. `PredictiveCruiseControl` (P274), however, is **not restricted to ICE** by its row text — PCC could in principle apply to any vehicle type optimizing energy use via gradient preview, though the regulation's examples (§8.1.4) are framed around engine/braking behaviour.

---

## §8 — Advanced driver assistance systems (full definitions)

**8.1** The following ADAS types, "primarily aiming for reduction of fuel consumption and CO2 emissions," shall be declared as input:

**8.1.1 Engine stop-start during vehicle stops**: a system that automatically shuts down and restarts the ICE during vehicle stops to reduce idling time. **Maximum time delay for automatic engine shutdown after vehicle stop: 3 seconds.**

**8.1.2 Eco-roll without engine stop-start**: automatically decouples the ICE from the drivetrain during specific downhill driving with low negative gradients. **Must be active at least at all cruise-control set speeds above 60 km/h.** Must cover one or both of:
- **Functionality (1):** ICE de-coupled from drivetrain, operates at idle speed; for APT-transmissions, the torque-converter lock-up clutch is **closed**.
- **Functionality (2) — "Torque converter lock-up clutch open"**: the lock-up clutch is **open** during Eco-roll, allowing the engine to coast at lower speeds, reducing/eliminating fuel injection. **Relevant only for APT-transmissions.**

**8.1.3 Eco-roll with engine stop-start**: automatically decouples the ICE during specific downhill driving with low negative slopes; after decoupling the ICE is shut down after a short time delay and stays shut down during the **main share** of the eco-roll phase. **Must be active at least at cruise-control set speeds above 60 km/h.**

**8.1.4 Predictive Cruise Control (PCC)**: optimises use of potential energy during a driving cycle based on an available **preview of road gradient data** (via GPS). A declared PCC system must have a **gradient preview distance longer than 1 000 metres** and cover **all** of:
1. **Crest coasting** — approaching a crest, vehicle velocity is reduced *before* the point where gravity alone would accelerate it beyond the cruise-control set speed, so following downhill braking is reduced.
2. **Acceleration without engine power** — during downhill driving at low velocity + high negative slope, acceleration happens with **no engine power usage**, so downhill braking is reduced.
3. **Dip coasting** — during downhill braking at "overspeed" (a speed above the cruise-control set speed), PCC **increases the overspeed** for a short period to end the downhill event at a higher vehicle velocity.

A PCC system may be declared if it covers **either** functionalities (1)+(2), **or** (1)+(2)+(3) — i.e. (3) alone or (2)+(3) without (1) are not valid combinations; (1) is mandatory whenever PCC is declared.

**8.2** The **eleven** valid combinations of ADAS systems as simulation-tool inputs are given in **Table 12**. Combinations 2–11 **shall not** be declared for SMT transmissions. Combinations 3, 6, 9, 11 **shall not** be declared for APT transmissions.

### Table 12 — Combinations of advanced driver assistance systems as input parameters

| Combination no. | Engine stop-start during vehicle stops | Eco-roll without engine stop-start | Eco-roll with engine stop-start | Predictive cruise control |
|---|---|---|---|---|
| 1 | yes | no | no | no |
| 2 | no | yes | no | no |
| 3 | no | no | yes | no |
| 4 | no | no | no | yes |
| 5 | yes | yes | no | no |
| 6 | yes | no | yes | no |
| 7 | yes | no | no | yes |
| 8 | no | yes | no | yes |
| 9 | no | no | yes | yes |
| 10 | yes | yes | no | yes |
| 11 | yes | no | yes | yes |

**8.3** Any declared ADAS system shall **by default** be set to fuel-economy mode after **each key-off/key-on cycle**.

**8.4** If an ADAS system is declared, it must be possible to **verify its presence** via real-world driving against the §8.1 definitions. For declared **combinations**, the **interaction** of functionalities (e.g. PCC + eco-roll with engine stop-start) must also be demonstrated. The verification procedure must account for the fact that systems need certain boundary conditions to be "active" (e.g. engine at operating temperature for stop-start; certain vehicle-speed ranges for PCC; certain road-gradient/vehicle-mass ratios for eco-roll). The manufacturer must submit a **functional description of boundary conditions** under which systems are "inactive" or reduced-efficiency. The approval authority may request technical justification of these boundary conditions and assess compliance.

*(Cross-reference: §10.3 in file 04b states that where HEV engine stop-start per 8.1.1 is present, considering 8.4's boundary conditions, `P271` must be `true`.)*

---

## §9 — Cargo volume (vans)

**9.1.** For vehicles of chassis configuration **`van`**, cargo volume is calculated as:

```
Cargo volume = [(L_C,floor + L_C)/2] × [(W_C,max + W_C,wheelhouse)/2] × [(H_C,max + H_C,rearwheel)/2]   [m³]
```

*(Reproduced from source OCR, which renders this with garbled formatting — "ðLC;floor þ LCÞ / 2 · ðWC;max þ WC;wheelhouse Þ2 · ðHC;max þ HC;rearwheelÞ2" — the equation above is the editor's best-faith reconstruction of the clearly-intended "average of two length measures × average of two width measures × average of two height measures" structure, consistent with the dimension definitions in Table 13. **This reconstruction should be verified against the original PDF's typeset equation (not just the OCR text layer) before being relied upon as authoritative** — flagged explicitly per project instructions not to pass off any inferred formula as verified fact.)*

Dimensions are determined per **Table 13** and **[Figure 3 — "Definition of cargo volume for medium lorries" — referenced in source but not visually extracted from this text-only OCR]**.

### Table 13 — Definitions related to cargo volume for medium lorries of type van

| Formula symbol | Dimension | Definition |
|---|---|---|
| L_C,floor | Cargo length at floor | Longitudinal distance from the most rearward point of the last seating row (or partition wall) to the foremost point of the closed rear compartment, projected to the zero Y-plane; measured at the height of the cargo floor surface |
| L_C | Cargo length | Longitudinal distance from the X-plane tangent to the most rearward point on the seatback (incl. head restraints) of the last seating row (or partition wall) to the foremost X-plane tangent to the closed rear compartment (tailgate, rear doors, or other limiting surface); measured at the height of the most rearward point of the last seating row or partition wall |
| W_C,max | Maximum cargo width | Maximum lateral distance of the cargo compartment, measured between the cargo floor and 70 mm above the floor; excludes transitional arc, local protrusions, depressions, pockets |
| W_C,wheelhouse | Cargo width at wheelhouse | Minimum lateral distance between the limiting interferences (pass-through) of the wheelhouses, measured between the cargo floor and 70 mm above the floor; same exclusions as above |
| H_C,max | Maximum cargo height | Maximum vertical distance from the cargo floor to the headlining or other limiting surface, measured behind the last seating row/partition wall at the vehicle centreline |
| H_C,rearwheel | Cargo height at rear wheel | Vertical distance from the top of the cargo floor to the headlining/limiting surface, measured at the rear wheel X-coordinate at the vehicle centreline |

*(Cross-reference: `Cargo volume` parameter P292 in Table 1, file 04a, double/3 type, [m³] unit, "only relevant to vehicles of chassis configuration 'van'".)*

---

## §11 — Transfer of results of the simulation tool to other vehicles

**11.1.** Simulation results may be transferred to other vehicles (per Article 9(6)) if **all** of:
(a) input data/information is **completely identical** except VIN (P238) and Date (P239). For primary heavy buses, additional input relevant to the interim vehicle and already available at the initial stage **may differ**, but special measures must be taken.
(b) the **version of the simulation tool** is identical.

**11.2.** Result files to be considered for transfer:
(a) medium/heavy lorries: manufacturer's records file + customer information file
(b) primary heavy buses: manufacturer's records file + vehicle information file
(c) complete/completed heavy buses: manufacturer's records file + customer information file + vehicle information file

**11.3.** To transfer results, modify the files above by replacing data elements per the subpoints below with updated information. **Modifications allowed only for data elements related to the current stage of completion.**

**11.3.1 Manufacturer's records file:** (a) VIN (Annex IV, Part I, 1.1.3); (b) Date output file created (Annex IV, Part I, 3.2)

**11.3.2 Customer information file:** (a) VIN (Annex IV, Part II, 1.1.1); (b) Date output file created (Annex IV, Part II, 3.2)

**11.3.3 Vehicle information file:**
- 11.3.3.1 Primary heavy bus: (a) VIN (Annex IV, Part III, 1.1); (b) Date output file created (Annex IV, Part III, 1.3.2)
- 11.3.3.2 Where a primary heavy bus manufacturer provides data beyond primary-vehicle requirements that differs between original and transferred vehicle, the related vehicle information file elements must be updated accordingly.
- 11.3.3.3 Complete/completed heavy bus: (a) VIN (Annex IV, Part III, 2.1); (b) Date output file created (Annex IV, Part III, 2.2.2)

**11.3.4 Signature elements to update after modification:**
- 11.3.4.1 Lorries: manufacturer's records file (Annex IV, Part I, 3.6 & 3.7); customer information file (Annex IV, Part II, 3.3 & 3.4)
- 11.3.4.2 Primary heavy buses: manufacturer's records file (Annex IV, Part I, 3.3 & 3.4); vehicle information file (Annex IV, Part III, 1.4.1 & 1.4.2)
- 11.3.4.3 Primary heavy buses with additional interim-vehicle input also provided: manufacturer's records file (3.3 & 3.4); vehicle information file (1.4.1, 1.4.2 **and** 2.3.1)
- 11.3.4.4 Complete/completed heavy buses: manufacturer's records file (3.6 & 3.7); vehicle information file (2.3.1)

**11.4.** Where CO2/fuel consumption cannot be determined for the original vehicle due to a simulation-tool malfunction, the **same measures** apply to vehicles with transferred results.

**11.5.** If result-transfer is used by a manufacturer, the related process must be **demonstrated to the approval authority** as part of granting the process licence.

*(This section is administrative/certification-process-focused rather than a technical input parameter — included for completeness since it is part of the assigned Annex III range; of lower direct relevance to a sizing/simulation tool, but relevant if your tool also needs to model the **certification record-keeping** workflow, e.g. for an OEM-facing feature.)*

---

## §12 — Usable capacity of the hydrogen fuel storage system

"For fuel storage systems containing hydrogen the usable capacity shall be determined." Three methods depending on storage technology (cross-reference: `HydrogenStorageTechnology` P546, file 04a Table 1, allowed values `Compressed`/`Liquid`/`Cryocompressed`).

### 12.1 Compressed gaseous hydrogen

```
m_usable = V_CHSS × (ρ_15°C,NWP − ρ_15°C,pmin,rel) × 0.001
```

where:
- `m_usable` = usable capacity **[kg]**
- `V_CHSS` = volume of the compressed hydrogen storage technology **[l]**
- `p_min,rel` = relative pressure corresponding to empty hydrogen tank condition **[MPa]**
- `ρ_15°C,NWP` = density of compressed gaseous hydrogen at 15°C and at **Nominal Working Pressure (NWP)** as defined in point 2.17 of UN Regulation No 134 **[g/l]** — determined from **Table 16** by linear interpolation
- `ρ_15°C,pmin,rel` = density of compressed gaseous hydrogen at 15°C and at `p_min,rel` **[g/l]** — determined from **Table 16** by linear interpolation

### Table 16 — Density of compressed hydrogen at 15°C [g/l]

Temperature fixed at 15°C; density tabulated by pressure (MPa):

| Pressure (MPa) | 0,5 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 35 | 70 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Density (g/l) at 15°C | 0,9 | 1,7 | 2,6 | 3,4 | 4,2 | 4,9 | 5,7 | 6,5 | 7,3 | 8,0 | 24,0 | 40,2 | — |

**⚠ Table alignment flag:** the source OCR row reads "**15 | 0,5 0,9 1,7 2,6 3,4 4,2 4,9 5,7 6,5 7,3 8,0 24,0 40,2**" as a single run-on line under the header "Temperature (°C) / Pressure (MPa) / 0,5 1 2 3 4 5 6 7 8 9 10 35 70". This means there are **13 pressure column headers** (0,5/1/2/3/4/5/6/7/8/9/10/35/70 MPa) but only **12 density values** listed after the leading "15" (which is itself the temperature value, not a 14th data point). **I could not unambiguously re-align all 13 pressure values to 12 density values from the OCR text alone** — one value is either missing or the "15" being read as temperature actually consumes the first data slot. The values as printed, left-to-right after "15": 0,5 → 0.5; then 0,9; 1,7; 2,6; 3,4; 4,2; 4,9; 5,7; 6,5; 7,3; 8,0; 24,0; 40,2 (12 values for 13 headers, with "0,5" ambiguous as either the 0.5 MPa column header repeated or its own density value of 0.5 g/l). **Recommend verifying this table directly against the original PDF's typeset table (not the OCR text layer) before using these density values for any calculation** — this is exactly the kind of transcription risk the project's "do not pass off assumptions as factual" instruction is meant to catch, so it is flagged rather than silently resolved.

### 12.2 Liquid hydrogen

```
m_usable = V_LHSS × (ρ_full,ref − ρ_empty) × 0.001
```

where:
- `m_usable` = usable capacity **[kg]**
- `V_LHSS` = volume of the liquid hydrogen storage technology **[l]**
- `ρ_full,ref` = density of liquid hydrogen at **full hydrogen tank condition** **[g/l]**, defined by the operational conditions: (a) vehicle operated until empty hydrogen tank condition reached; (b) refilling starts immediately afterward; (c) regarding the state of hydrogen provided by the refuelling infrastructure, reference is made to international standards where available
- `ρ_empty` = density of liquid hydrogen at **empty hydrogen tank condition** **[g/l]**

"The calculation model of the densities shall be disclosed to the approval authority on request."

### 12.3 Cryo-compressed hydrogen (▼M4, new)

```
m_usable = V_CCHSS × ρ_filling × f_usable × 0.001
ρ_filling = 0.0589 × p_filling + 52.395
```

where:
- `m_usable` = usable capacity **[kg]**
- `V_CCHSS` = volume of the cryo-compressed hydrogen storage technology **[l]**
- `ρ_filling` = density of hydrogen at the end of the refuelling process **[g/l]**
- `f_usable` = usable share, determined from **Table 17** by linear interpolation **[-]**
- `p_filling` = absolute hydrogen pressure in the tank at the end of the refuelling process **[bar]**

The value for `p_filling` used in calculations must be documented in the information document for the cryo-compressed hydrogen tank system; existing international standards on cryo-compressed refuelling infrastructure must be taken into account where available.

### Table 17 — Usable share of hydrogen mass in a cryo-compressed hydrogen storage technology [-]

| Absolute pressure corresponding to empty hydrogen tank condition [bar] | f_usable (*) [-] |
|---|---|
| 5 | 0,97 |
| 8 | 0,95 |
| 10 | 0,93 |
| 15 | 0,88 |
| 20 | 0,85 |
| 30 | 0,75 |

(*) The specified `f_usable` values **assume the tank has an internal heating system activated when minimum pressure is reached**. Where there is no such in-tank heating system, the manufacturer shall apply, **upon approval from the approval authority**, a **lower** value for `f_usable`.

**HDEV-tool relevance — high priority for FCEV/H2 sizing:** §12 gives you three complete, formally-defined, auditable methods to convert **physical tank volume** into **usable kg of H2** depending on storage technology — exactly the kind of primary-source numeric method the project instructions require (verifiable from an authentic source, not an estimate). Table 17's `f_usable` values (0.75–0.97 depending on minimum tank pressure, 5–30 bar) are a genuine regulatory numeric input directly usable in a hydrogen HDEV range/capacity model, **conditional on the in-tank heating system assumption** stated in footnote (*).

---

## Appendix 1 — Vehicle technologies exempted from Article 9(1) obligations

Table title: "Vehicle technologies for which the obligations laid down in Article 9(1), first subparagraph, do not apply, as provided in that subparagraph." This table defines the **criteria** that map to the `Technology` parameter (P332, file 04a Table 5) controlled-vocabulary values.

### Table 1 of Appendix 1

| Vehicle technology category | Criteria for exemption | Input parameter value (Table 5, Annex III) |
|---|---|---|
| **Fuel cell vehicle** | ►M4 Exempted where **at least one** applies: — an FCV that is **not** an FCHV per point 2(13); — vehicle has multiple EMs within a single powertrain **not** at the same drivetrain connection point (point 10.1.2); — vehicle has multiple EMs at the **same** connection point but **without identical specifications** (same component certificate); — vehicle has a powertrain architecture **other than** F2–F4 or F-IEPC (point 10.1.3). ◄ | `'FCV Article 9 exempted'` |
| **Dual-fuel** | ►M4 Dual-fuel vehicles with a natural-gas- or LPG-operated engine of types **1B, 2B, 3B** per Article 2(53), 2(55), 2(56) of Reg (EU) No 582/2011; **or** dual-fuel vehicles with a hydrogen-operated engine of a type **other than 1A** per Article 2(52) of Reg (EU) No 582/2011. ◄ | `'Dual-fuel vehicle Article 9 exempted'` |
| **HEV** | ►M4 Exempted where **at least one** applies: — multiple EMs within a single powertrain **not** at the same connection point (10.1.2); — multiple EMs at the same connection point **without identical specifications**; — powertrain architecture **other than** P1–P4, S2–S4, S-IEPC (10.1.3), **or other than IHPC Type 1**. ◄ | `'HEV Article 9 exempted'` |
| **PEV** | ►M4 Exempted where **at least one** applies: — multiple EMs within a single powertrain **not** at the same connection point; — multiple EMs at the same connection point **without identical specifications**; — powertrain architecture **other than** E2–E4 or E-IEPC (10.1.3). ◄ | `'PEV Article 9 exempted'` |
| **Multiple permanently mechanically independent powertrains** | ►M4 The vehicle has **more than one** powertrain, each propelling different wheel axle(s), which can under no circumstances be mechanically connected, **and** the specific system is **not covered** by the allowed combinations defined in point 10.1.4. ◄ Hydraulically driven axles are treated as non-driven per point 5(a) and thus not counted as an independent powertrain. | `'Multiple powertrains Article 9 exempted'` |
| **Non-electric hybrid vehicles** | The vehicle is a HV but **not** a HEV per point 2(26) and (27). | `'HV Article 9 exempted'` |
| **Other** (▼M4) | Any other propulsion technology not listed in this table, for which simulation per Article 9 is **not possible** due to limitations of the simulation tool regarding that specific propulsion technology. | `'Other technology Article 9 exempted'` |

**Unresolved cross-reference flag:** the `Technology` parameter P332 (Table 5, file 04a) allows two additional values — `'In-motion charging Article 9 exempted'` and `'H2 ICE Article 9 exempted'` — that **do not appear as rows** in this Appendix 1 table within the assigned extraction range (lines 1993–4315). Either (a) these two categories' exemption criteria are defined in a part of Appendix 1 that falls just outside this range (the extraction ends at line 4315, Appendix 1 / Table 1 footnotes), or (b) they are defined elsewhere in Article 9 of the Regulation's main body (not Annex III). **Recommend checking the lines immediately following 4315, and/or Article 9 itself, to resolve this.**

### Footnotes to Appendix 1 Table 1

(*) Commission Regulation (EU) No 1230/2012 of 12 December 2012, implementing Reg (EC) No 661/2009, on type-approval requirements for masses and dimensions of motor vehicles and trailers, amending Directive 2007/46/EC (OJ L 353, 21.12.2012, p. 31).

(**) Regulation (EU) 2019/2144 of the European Parliament and of the Council of 27 November 2019, on type-approval requirements for motor vehicles/trailers and systems/components/STUs regarding general safety and occupant/vulnerable-road-user protection, amending Reg 2018/858, repealing Regs (EC) 78/2009, 79/2009, 661/2009, and multiple Commission Regulations (OJ L 325, 16.12.2019, p. 1).

---

## Summary of zero-emission/HDEV-specific flags across this file

1. ADAS (Table 6, §8) is fuel-saving-ICE-centric; only `OVC-HEV` gets a forced `EngineStopStart=true`; PEV/FCHV are implicitly outside the stop-start/eco-roll framework.
2. §12's three hydrogen usable-capacity formulas (compressed/liquid/cryo-compressed) are a ready-made, source-verifiable physics model for H2 tank sizing — but the Table 16 compressed-hydrogen density table has an OCR alignment ambiguity that needs verification against the source PDF directly.
3. Appendix 1's exemption table is the authoritative decoder for the `Technology` (P332) field, but two of its allowed values (in-motion charging, H2 ICE) have no visible criteria row in this extracted range.
