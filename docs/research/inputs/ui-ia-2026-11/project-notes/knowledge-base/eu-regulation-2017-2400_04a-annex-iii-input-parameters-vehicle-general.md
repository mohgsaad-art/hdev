# Annex III — Input Information Relating to the Characteristic of the Vehicle
## Part A: General Vehicle-Level Input Parameters

**Source document:** Commission Regulation (EU) 2017/2400 (implementing Regulation (EC) No 595/2009) — methodology for determining the CO2 emissions and fuel consumption of heavy-duty vehicles (VECTO)
**CELEX number:** 02017R2400
**Consolidated as of:** 01.01.2026 (consolidated text, version 007.001)
**Source lines covered in this file:** approx. 1993–2750, 3051–3231, 3525–3588 of the extracted text (Annex III, Introduction; Definitions §2; Table 1 "Vehicle/General"; Table 2 "Vehicle/AxleConfiguration"; Table 4 "VehicleTorqueLimits per gear"; Table 5 "Input parameters for vehicles exempted under Article 9"; §4 Vehicle mass; §5 Hydraulically/mechanically driven axles; §6 Gear dependent torque limits and gear disabling; §7 Vehicle specific engine idling speed)
**Amendment markers used throughout:** ►B = original 2017 baseline; ►M1 = Reg (EU) 2019/318; ►M2 = Reg (EU) 2020/1181; ►M3 = Reg (EU) 2022/1379; ►M4 = Reg (EU) 2025/258. Where a table or clause is reproduced below under a `▼M3` or `▼M4` banner in the source, that is the amendment that last substituted/introduced the whole block; inline `►M4 ... ◄` marks mark a phrase introduced/changed specifically by that amendment within an otherwise-older block.

---

## 1. Introduction & purpose (source §1)

Annex III lists the parameters the **vehicle manufacturer** must provide as input to the VECTO simulation tool. The applicable XML schema and example data are published separately on the "dedicated electronic distribution platform" (not part of this text).

---

## 2. Definitions (source §2) relevant to vehicle-level parameters

These are the regulation's own defined terms used throughout Annex III (only the subset relevant to general vehicle parameters is reproduced here in full; powertrain/electric-specific definitions are reproduced in file 04b).

1. **"parameter ID"**: unique identifier used in the simulation tool for a specific input parameter or set of input data.
2. **"type"**: data type of the parameter —
   - `string`: sequence of characters in ISO8859-1 encoding
   - `token`: sequence of characters in ISO8859-1 encoding, no leading/trailing whitespace
   - `date`: date and time in UTC, format `YYYY-MM-DDTHH:MM:SSZ` (e.g. `2002-05-30T09:30:10Z`)
   - `integer`: integral value, no leading zeros (e.g. `1 800`)
   - `double, X`: fractional number with exactly X digits after the decimal point and no leading zeros (e.g. `double,2` → `2345,67`; `double,4` → `45.6780`) — note the source text shows inconsistent decimal separators (comma vs. point) across examples; this is reproduced as printed and should be treated as a formatting artifact of the OCR/typesetting, not a substantive rule change.
3. **"unit"**: physical unit of the parameter.
4. **"corrected actual mass of the vehicle"**: the mass specified under "actual mass of the vehicle" per Commission Regulation (EU) No 1230/2012, **except**: tank(s) filled to at least 50% of capacity; liquid-containing systems filled to 100% of manufacturer-specified capacity, except waste-water systems which must remain empty.
   - For medium rigid lorries, heavy rigid lorries and tractors: mass determined **without superstructure**, corrected by the additional weight of non-installed standard equipment per point 4.3. The simulation tool automatically adds the mass of a standard body/semi-trailer/trailer. All parts mounted on/above the main frame are "superstructure" if installed only to facilitate a superstructure, independent of parts necessary for running-order condition.
   - For heavy buses that are **primary vehicles**: "corrected actual mass of the vehicle" is **not applicable** — the simulation tool allocates a generic mass value instead.
5. **"height of the integrated body"** (heavy buses only): difference in Z-direction between reference point 'A' (highest point) and reference point 'B' (lowest point) of an integrated body. [Figure 1 — "Height of the integrated body – standard case" — referenced in source but not visually extracted from this text-only OCR.] Special cases (deviations from standard case; see [Figure 2 — "Height of the integrated body – special cases" — referenced in source but not visually extracted from this text-only OCR]), introduced/maintained under ▼M3:
   - **Special case 1 (two levels):** height = average of h1 and h2, where h1 = difference between point A (determined in the cross-section at the rear end of the first passenger door) and point B; h2 = difference between point A and point B.
   - **Special case 2 (inclined):** same formula structure as case 1 (average of h1, h2 as defined above).
   - **Special case 3 (open top with roof section):** height determined in the remaining roof section.
   - **Special case 4 (open top without any roof section):** height = difference between the highest point of the vehicle within one metre (longitudinal direction) of the front screen/upper front screen (double-decker) and point B.
   - **All other cases** not covered by standard/special cases 1–4: height = difference between the highest point of the vehicle and point B.
6. **Reference point 'A'**: highest point on the bodywork (body/design panels, HVAC mounting brackets, hatches and similar excluded).
7. **Reference point 'B'**: lowest point on the lower outside edge of the bodywork (axle-mounting brackets etc. excluded).
8. **"vehicle length"** (heavy buses only): per Table I, Appendix 1, Annex I to Reg (EU) 1230/2012; additionally excludes removable load carrier devices, non-removable coupling devices, and other non-removable exterior parts not affecting usable passenger space.
9. **"vehicle width"**: per Table II, Appendix 1, Annex I to Reg (EU) 1230/2012, with the same exclusions as above.
10. **"entrance height in non-kneeled position"**: floor level within the first door aperture above ground, measured at the most forward door, vehicle in non-kneeled position.

*(Definitions 11–51, covering fuel cells, electric machines, energy storage/converter taxonomy, hybrid/PEV/FCHV definitions, dynamic charging, hydrogen storage, driver-selectable modes etc., are reproduced in full in file `04b-annex-iii-input-parameters-powertrain-components.md` since they underpin the powertrain/electric component parameter tables.)*

---

## 3. Set of input parameters — framework (source §3 intro)

> ►M4 In Tables 1 to 17 the sets of input parameters to be provided regarding the characteristics of the vehicle are specified. ◄

Different sets apply depending on application case: **medium lorries**, **heavy lorries**, **heavy buses**. For heavy buses, a further distinction is made between the **primary vehicle** stage and the **complete/completed vehicle** stage. Responsibilities by manufacturing stage (heavy buses, multi-stage build):

- **Primary vehicle manufacturers**: must provide all parameters in the "primary vehicle" column; may additionally provide complete/completed-vehicle parameters determinable at this stage. If so, Manufacturer (P235), Manufacturer Address (P252), VIN (P238) and Date (P239) must be provided for **both** parameter sets.
- **Interim manufacturers**: must provide complete/completed-vehicle parameters determinable at their stage and under their responsibility. If updating a parameter already provided by a previous stage, the **entire status** of that parameter must be re-specified (example given: if a second heat pump is added, the technology of **both** systems must be declared). Manufacturer, Manufacturer Address, VIN and Date must always be provided.
- **Manufacturers of the completed vehicle**: must provide parameters determinable at their stage and under their responsibility; same re-specification rule as interim manufacturers applies to updates. Manufacturer, Manufacturer Address, VIN, Date **and Corrected Actual Mass (P038)** must always be provided. The consolidated data set across all stages must contain the entire "complete vehicle or completed vehicle" column.
- **Manufacturers related to the "complete" stage** (single-stage build): must provide **all** input parameters (both primary and complete-vehicle columns), with Manufacturer/Address/VIN/Date provided for both sets.
- **`VehicleDeclarationType` (P293)** must be delivered by every manufacturing stage that provides any parameter listed in the complete/completed-vehicle column.

---

## Table 1 — Input parameters "Vehicle/General"

Columns "Heavy lorries / Medium lorries / Heavy buses (primary vehicle) / Heavy buses (complete or completed vehicle)" show an **X** where the parameter applies to that vehicle class/stage.

| Parameter name | Parameter ID | Type | Unit | Description / Reference | Heavy lorries | Medium lorries | Heavy buses (primary) | Heavy buses (complete/completed) |
|---|---|---|---|---|---|---|---|---|
| Manufacturer | P235 | Token | [-] | — | X | X | X | X |
| Manufacturer Address | P252 | Token | [-] | — | X | X | X | X |
| Model_CommercialName | P236 | Token | [-] | — | X | X | X | X |
| VIN | P238 | Token | [-] | — | X | X | X | X |
| Date | P239 | Date Time | [-] | Date and time when input information and input data is created | X | X | X | X |
| Legislative Category | P251 | String | [-] | Allowed values: `N2`, `N3`, `M3` | X | X | X | X |
| ChassisConfiguration | P036 | String | [-] | Allowed values: `Rigid Lorry`, `Tractor`, `Van`, `Bus` | X | X | X | — |
| AxleConfiguration | P037 | String | [-] | Allowed values: `4×2`, `4×2F`, `6×2`, `6×4`, `8×2`, `8×4` (`4×2F` = 4×2 with driven front axle) | X | X | X | — |
| Articulated | P281 | boolean | [-] | In accordance with Article 3, point (37) | — | — | X | — |
| CorrectedActualMass | P038 | Int | [kg] | Per "corrected actual mass of the vehicle" (point 2(4)) | X | X | X | — |
| TechnicalPermissibleMaximumLadenMass | P041 | int | [kg] | Per Article 2, point (7), Reg (EU) No 1230/2012 | X | X | X | X |
| IdlingSpeed | P198 | int | [1/min] | Per point 7.1. ►M4 For PEV and FCHV no input is required. ◄ | X | X | X | — |
| RetarderType | P052 | string | [-] | ►M4 Allowed values: `None`, `Losses included in Gearbox`, `Engine Retarder`, `Transmission Input Retarder`, `Transmission Output Retarder`, `Axlegear Input Retarder` (`Axlegear Input Retarder` applicable only for powertrain architectures `E3`, `S3`, `F3`, `S-IEPC`, `F-IEPC`, `E-IEPC`). Separate entry for each individual powertrain for multiple mechanically independent powertrains per point 10.1.4. ◄ | X | X | X | — |
| RetarderRatio | P053 | double,3 | [-] | Step-up ratio per Table 2 of Annex VI. ►M4 Separate entry per independent powertrain per 10.1.4. ◄ | X | X | X | — |
| AngledriveType | P180 | string | [-] | Allowed values: `None`, `Losses included in Gearbox`, `Separate Angledrive`. ►M4 Separate entry per independent powertrain per 10.1.4. ◄ | X | X | X | — |
| PTOShaftsGearWheels (¹) | P247 | string | [-] | Allowed values: `none`, `only the drive shaft of the PTO`, `drive shaft and/or up to 2 gear wheels`, `drive shaft and/or more than 2 gear wheels`, `only one engaged gearwheel above oil level`, `PTO which includes 1 or more additional gearmesh(es), without disconnect clutch`. ►M4 Separate entry per independent powertrain per 10.1.4. In case of IEPC and IHPC, no input shall be made. ◄ | X | — | — | — |
| PTOOtherElements (¹) | P248 | string | [-] | Allowed values: `none`, `shift claw, synchroniser, sliding gearwheel`, `multi-disc clutch`, `multi-disc clutch, oil pump`. ►M4 Separate entry per independent powertrain per 10.1.4. ◄ | X | — | — | — |
| *Engine input data* | — | — | — | ►M4 In accordance with Appendix 7 of Annex V ◄ — only applicable if the component is present in the vehicle | X | X | X | — |
| *Transmission input data* | — | — | — | ►M4 In accordance with Table 1–3, Appendix 12, Annex VI ◄ — only if present; separate entry per independent powertrain per 10.1.4 | X | X | X | — |
| *Torque converter input data* | — | — | — | ►M4 In accordance with Table 4–5, Appendix 12, Annex VI ◄ — only if present; separate entry per independent powertrain per 10.1.4 | X | X | X | — |
| *Axle input data* | — | — | — | ►M4 In accordance with Table 1–2, Appendix 6, Annex VII ◄ — only if present; separate entry per independent powertrain per 10.1.4 | X | X | X | — |
| *Angle drive input data* | — | — | — | ►M4 In accordance with Table 6–7, Appendix 12, Annex VI ◄ — refers to certified ADC component installed in angle-drive position; only if present; separate entry per independent powertrain per 10.1.4 | X | X | X | — |
| *Retarder input data* | — | — | — | ►M4 In accordance with Table 8–9, Appendix 12, Annex VI ◄ — only if present AND retarder losses not already provided with transmission input data; separate entry per independent powertrain per 10.1.4 | X | X | X | — |
| *Air drag input data* | P268 | token | [-] | ►M4 In accordance with Table 1, Appendix 9, Annex VIII ◄ — only applicable if certified input data provided | X | X | X | — |
| AirdragModifiedMultistage | P334 | boolean | [-] | Input required for all manufacturing stages subsequent to a first entry to the air drag component. If set to `true` without providing a certified air drag component, the simulation tool applies standard values per Annex VIII. | — | — | — | X |
| *IEPC input data* | — | — | — | ►M4 In accordance with Appendix 15, Annex Xb ◄ — only if present; separate entry per independent powertrain per 10.1.4 | X | X | X | — |
| ZeroEmissionVehicle | P269 | boolean | [-] | As defined in Article 3, point (15) | X | X | X | — |
| VocationalVehicle | P270 | boolean | [-] | Per Article 3, point (9), Reg (EU) 2019/1242 | X | — | — | — |
| NgTankSystem | P275 | string | [-] | Allowed values: `Compressed`, `Liquefied`. Only relevant for engines of fuel type `NG PI`/`NG CI` (P193). Where both tank systems present, declare the one with higher fuel-energy content. | X | X | X | — |
| Sleepercab | P276 | boolean | [-] | — | X | — | — | — |
| ClassBus | P282 | string | [-] | Allowed values: `I`, `I+II`, `A`, `II`, `II+III`, `III`, `B` per paragraph 2, UN Regulation No. 107 | — | — | X | — |
| NumberPassengersSeatsLowerDeck | P283 | int | [-] | Passenger seats excl. driver/crew; double-deck → lower deck only; single-deck → total seats | — | — | X | — |
| NumberPassengersStandingLowerDeck | P354 | int | [-] | Registered standing passengers; double-deck → lower deck only; single-deck → total | — | — | X | — |
| NumberPassengersSeatsUpperDeck | P284 | int | [-] | Upper-deck seats (double-deck); single-deck → `0` | — | — | X | — |
| NumberPassengersStandingUpperDeck | P355 | int | [-] | Upper-deck standing passengers (double-deck); single-deck → `0` | — | — | X | — |
| BodyworkCode | P285 | int | [-] | ►M4 Allowed values: `CA`,`CB`,`CC`,`CD`,`CE`,`CF`,`CG`,`CH`,`CI`,`CJ` per point 3, Part C, Annex I, Reg (EU) 2018/858. For bus chassis with vehicle code `CX`, no input delivered. ◄ | — | — | X | — |
| LowEntry | P286 | boolean | [-] | ►M4 "low entry" per point 1.2.3 of Annex I ◄ | — | — | X | — |
| HeightIntegratedBody | P287 | int | [mm] | Per point 2(5) | — | — | X | — |
| VehicleLength | P288 | int | [mm] | Per point 2(8) | — | — | X | — |
| VehicleWidth | P289 | int | [mm] | Per point 2(9) | — | — | X | — |
| EntranceHeight | P290 | int | [mm] | Per point 2(10) | — | — | X | — |
| DoorDriveTechnology | P291 | string | [-] | Allowed values: `pneumatic`, `electric`, `mixed` | — | — | X | — |
| Cargo volume | P292 | double,3 | [m³] | Only relevant for chassis configuration `van` | — | X | — | — |
| VehicleDeclarationType | P293 | string | [-] | Allowed values: `interim`, `final` | — | — | — | X |
| VehicleTypeApprovalNumber | P352 | token | [-] | Whole-vehicle type-approval number, or individual vehicle approval number for individual approvals | X | X | X | X |
| H2StorageUsableCapacity | P545 | double,1 | [kg] | ▼M4. Per point 12. Only relevant for vehicles with a hydrogen fuel storage system. For heavy buses, input only from the manufacturer responsible for the fuel storage system, or when changes made to an existing system. | X | X | X | X |
| HydrogenStorageTechnology | P546 | string | [-] | ▼M4. Allowed values: `Compressed`, `Liquid`, `Cryocompressed`. Same hydrogen-vehicle/heavy-bus provisions as P545. | X | X | X | X |
| SimulationToolLicenceNumber | P547 | token | [-] | ▼M4. Licence number for operation of the simulation tool per Article 7. | X | X | X | X |

(¹) **Footnote to Table 1:** if multiple PTOs are mounted to the transmission, only the component with the **highest losses** per point 3.6 of Annex IX, for its combination of `PTOShaftsGearWheels` and `PTOShaftsOtherElements` criteria, shall be declared.

**HDEV-tool relevance:** `ZeroEmissionVehicle` (P269), `H2StorageUsableCapacity` (P545) and `HydrogenStorageTechnology` (P546) are the three zero-emission-specific fields in this general table — all three were added by ▼M4 (Reg 2025/258), i.e. **not present in the original 2017 or M1–M3 text**. `IdlingSpeed` (P198) is explicitly waived for PEV and FCHV under ▼M4. This confirms the EU regulatory input schema itself treats BEV/FCHV idling and hydrogen tank sizing as first-class, separately-versioned fields — directly analogous to parameters your sizing tool will need (usable energy capacity, zero-emission flag).

---

## Table 2 — Input parameters "Vehicle/AxleConfiguration" (per wheel axle)

| Parameter name | Parameter ID | Type | Unit | Description / Reference | Heavy lorries | Medium lorries | Heavy buses (primary) | Heavy buses (complete/completed) |
|---|---|---|---|---|---|---|---|---|
| AxleNumber | P548 | integer | [-] | ▼M4. Position of the wheel axle, counting front→rear starting at 1 | X | X | X | — |
| Twin Tyres | P045 | boolean | [-] | — | X | X | X | — |
| Axle Type | P154 | String | [-] | Allowed values: `VehicleNonDriven`, `VehicleDriven` | X | X | X | — |
| Steered | P195 | boolean | [-] | Only **active** steered axles declared as "steered" | X | X | X | — |
| *Tyre input data* | — | — | — | ▼M4. In accordance with Appendix 3 of Annex X | X | X | X | X |
| Wheel End Friction | P549 | double,1 | [Nm] | ▼M4. Declared wheel-end friction value, determined per point 3.6, Annex VIIa. Installed wheel ends must have the same or lower friction. No input where standard values used. Relevant only for **non-driven** axles. | X | — | X | — |
| Certification number wheel end | P550 | token | [-] | ▼M4. Certificate number(s) for declared wheel-end friction (P549); relevant only where P549 is provided; multiple entries possible | X | — | X | — |

**Note:** Tables 3 and 3a (auxiliary units) use the same parameter-ID numbering scheme cross-referenced to Annex IX, but are reproduced in file `04b` since they are powertrain/component-category tables.

---

## Table 4 — Input parameters "VehicleTorqueLimits" per gear (optional)

Renamed/retitled under ▼M4 (title itself marked ►M4◄); rows below carry ▼M3 provenance for the underlying parameters with ►M4 wording refinements.

| Parameter name | Parameter ID | Type | Unit | Description / Reference | Heavy lorries | Medium lorries | Heavy buses (primary) |
|---|---|---|---|---|---|---|---|
| Gear | P196 | integer | [-] | ►M4 Only gear numbers need be specified where vehicle-related torque limits per point 6 apply. ◄ | X | X | X |
| MaxTorque | P197 | integer | [Nm] | ►M4 Maximum engine or transmission input torque for the specific gear defined per point 6. ◄ | X | X | X |

Cross-reference: see §6 "Gear dependent torque limits and gear disabling" below for the substantive rule (which gears, what limit, verification).

---

## Table 5 — Input parameters for vehicles exempted according to Article 9

This is the **reduced parameter set** for vehicles exempted from full VECTO simulation under Article 9(1) (see Appendix 1 of Annex III, reproduced in file `04c`, for the exemption criteria and the controlled vocabulary of `Technology` values). Column header in source reads "Heavy buses (complete **and** completed vehicle)" (note "and" vs. "or" used in Table 1 — reproduced exactly as printed; likely a drafting inconsistency, not a substantive distinction).

| Parameter name | Parameter ID | Type | Unit | Description / Reference | Heavy lorries | Medium lorries | Heavy buses (primary) | Heavy buses (complete/completed) |
|---|---|---|---|---|---|---|---|---|
| Manufacturer | P235 | token | [-] | — | X | X | X | X |
| ManufacturerAddress | P252 | token | [-] | — | X | X | X | X |
| Model_CommercialName | P236 | token | [-] | — | X | X | X | X |
| VIN | P238 | token | [-] | — | X | X | X | X |
| Date | P239 | date Time | [-] | Date/time input created | X | X | X | X |
| LegislativeCategory | P251 | string | [-] | Allowed values: `N2`, `N3`, `M3` | X | X | X | X |
| ChassisConfiguration | P036 | string | [-] | Allowed values: `Rigid Lorry`, `Tractor`, `Van`, `Bus` | X | X | X | — |
| AxleConfiguration | P037 | string | [-] | Allowed values: `4×2`, `4×2F`, `6×2`, `6×4`, `8×2`, `8×4` | X | X | X | — |
| Articulated | P281 | boolean | [-] | Per Annex I definition (this Regulation) | — | — | X | — |
| CorrectedActualMass | P038 | int | [kg] | Per §2 point (4) | X | X | X | — |
| TechnicalPermissibleMaximumLadenMass | P041 | int | [kg] | Per Article 2(7), Reg (EU) No 1230/2012 | X | X | X | X |
| ZeroEmissionVehicle | P269 | boolean | [-] | Per Article 3(15) | X | X | X | — |
| Sleepercab | P276 | boolean | [-] | — | X | — | — | — |
| ClassBus | P282 | string | [-] | Allowed values: `I`,`I+II`,`A`,`II`,`II+III`,`III`,`B` per UN Reg 107 §2 | — | — | X | — |
| NumberPassengersSeatsLowerDeck | P283 | int | [-] | (same definition as Table 1) | — | — | X | — |
| NumberPassengersStandingLowerDeck | P354 | int | [-] | (same definition as Table 1) | — | — | X | — |
| NumberPassengersSeatsUpperDeck | P284 | int | [-] | (same definition as Table 1) | — | — | X | — |
| NumberPassengersStandingUpperDeck | P355 | int | [-] | (same definition as Table 1) | — | — | X | — |
| BodyworkCode | P285 | int | [-] | ►M4 Allowed values `CA`–`CJ` per Annex I Part C point 3, Reg 2018/858 ◄ (no `CX` exclusion clause repeated here, unlike Table 1) | — | — | X | — |
| LowEntry | P286 | boolean | [-] | "low entry" per point 1.2.2.3 of Annex I — **note:** cites point **1.2.2.3**, whereas Table 1's LowEntry cites point **1.2.3** — reproduced exactly as printed; appears to be a cross-reference inconsistency between the two tables in the source, worth checking against Annex I directly if load-bearing for your tool. | — | — | X | — |
| HeightIntegratedBody | P287 | int | [mm] | Per point 2(5) | — | — | X | — |
| SumNetPower | P331 | int | [W] | Maximum possible sum of positive propulsion power of all energy converters linked to the vehicle drivetrain or wheels | X | X | X | — |
| Technology | P332 | string | [-] | ►M4 Per Table 1 of Appendix 1. Allowed values: `FCV Article 9 exempted`, `Dual-fuel vehicle Article 9 exempted`, `HEV Article 9 exempted`, `PEV Article 9 exempted`, `In-motion charging Article 9 exempted`, `Multiple powertrains Article 9 exempted`, `H2 ICE Article 9 exempted`, `HV Article 9 exempted`, `Other technology Article 9 exempted` ◄ | X | X | X | — |
| SimulationToolLicenceNumber | P551 | token | [-] | ▼M4. Licence number per Article 7 | X | X | X | X |

**Note:** the allowed-value list for `Technology` (P332) includes `'In-motion charging Article 9 exempted'` and `'H2 ICE Article 9 exempted'`, but **neither of these two categories appears as a row** in Appendix 1's exemption-criteria table (reproduced in file 04c) within this extracted range — only `FCV`, `Dual-fuel`, `HEV`, `PEV`, `Multiple powertrains`, `HV` (non-electric hybrid) and `Other` have corresponding criteria rows in Appendix 1 Table 1. This may mean the criteria for "In-motion charging" and "H2 ICE" exemptions are defined elsewhere (e.g. a different point of Article 9 itself, not in Annex III) — **flagged as an unresolved cross-reference**; recommend checking Article 9 of the main Regulation body directly.

---

## 4. Vehicle mass for medium rigid lorries and tractors, heavy rigid lorries and tractors

**4.1.** The vehicle mass used as input for the simulation tool shall be the **corrected actual mass of the vehicle** (see definition, point 2(4) above).

**4.2.** If not all standard equipment is installed, the manufacturer shall **add** the mass of the following construction elements to the corrected actual mass:
(a) Front underrun protection (per Reg (EU) 2019/2144)
(b) Rear underrun protection (per Reg (EU) 2019/2144)
(c) Lateral protection (per Reg (EU) 2019/2144)
(d) Fifth wheel (per Reg (EU) 2019/2144)

**4.3.** Mass of these construction elements (exact figures, reproduced faithfully from source):

*For vehicle groups 1s, 1, 2 and 3 (Annex I, Table 1) and groups 51 and 53 (Annex I, Table 2):*
| Element | Mass |
|---|---|
| (a) Front underride protection | **45 kg** |
| (b) Rear underride protection | **40 kg** |
| (c) Lateral protection | **8,5 kg/m × wheel base [m] − 2,5 kg** |

*For vehicle groups 4, 5, 9 to 12 and 16 (Annex I, Table 1):*
| Element | Mass |
|---|---|
| (a) Front under-ride protection | **50 kg** |
| (b) Rear under-ride protection | **45 kg** |
| (c) Lateral protection | **14 kg/m × wheel base [m] − 17 kg** |
| (d) Fifth wheel | **210 kg** |

*(Decimal commas in the source — "8,5 kg/m", "2,5 kg" — are EU-style decimal separators = 8.5 kg/m and 2.5 kg in US/UK notation; reproduced exactly as printed.)*

---

## 5. Hydraulically and mechanically driven axles

(a) A **hydraulically driven axle** shall be treated as **non-drivable**; the manufacturer shall **not** count it when establishing the vehicle's axle configuration.
(b) A **mechanically driven axle** shall be treated as **drivable**; the manufacturer **shall** count it when establishing the axle configuration.

*(This provision is cross-referenced repeatedly elsewhere in Annex III — e.g. in the definition of "mechanically independent powertrain" at point 10.1.4 and in the Appendix 1 "Multiple permanently mechanically independent powertrains" exemption criterion — both reproduced in file 04b/04c.)*

---

## 6. Gear dependent torque limits and gear disabling (▼M4 heading)

**6.1 Gear dependent engine torque limits** (▼M3 text): for the **highest 50% of gears** (example given: gears 7–12 of a 12-gear transmission), the manufacturer **may** declare a gear-dependent maximum engine torque limit **not higher than 95% of the maximum engine torque**.

**6.2 Gear disabling** (▼M4): for **the highest gear only**, OR **both of the highest two gears** (example: gears 5 and 6 of a 6-gear transmission), the manufacturer may declare complete gear disabling by providing **0 Nm** as the gear-specific torque limit. Disabling **only the second-highest gear** (without also disabling the highest) is **not allowed**.

**6.3 Verification requirements** (▼M3): gear-dependent torque limits (6.1) and gear disabling (6.2) are subject to verification in the Verification Testing Procedure (VTP) per Annex Xa, point 6.1.1.1(c).

---

## 7. Vehicle specific engine idling speed

**7.1.** Engine idling speed must be declared for each individual vehicle equipped with an ICE. The declared vehicle engine idling speed shall be **equal to or higher than** the value specified in the engine input data approval (i.e. vehicle-level idling speed ≥ engine-certification idling speed).

*(Cross-reference: `IdlingSpeed` P198 in Table 1 above; explicitly not required for PEV/FCHV under ▼M4 since they have no ICE.)*
