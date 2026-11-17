# Annex VIII — Verifying Air Drag Data: Input Data Tables (Pre-Processing Tool) and Validity Criteria

**Source document:** Commission Regulation (EU) 2017/2400 (consolidated text, EUR-Lex)
**CELEX number:** 02017R2400
**Consolidation date:** 01.01.2026 (consolidated version 007.001)
**Range covered in this file:** Annex VIII, Sections 3.9–3.10 (source lines 14198–14609; page markers 344–352)
**Amendment markers:** ►B = original 2017 baseline; ►M1 = Reg (EU) 2019/318; ►M2 = Reg (EU) 2020/1181; ►M3 = Reg (EU) 2022/1379; ►M4 = Reg (EU) 2025/258.

> ## ⚠️ CRITICAL TRANSCRIPTION NOTE — formula symbol reconstruction
>
> This section of the regulation contains mathematical inequalities and formulas (point 3.10). The underlying OCR text extraction **corrupted the mathematical symbols** into unrelated characters (an artefact of how the PDF's embedded math/symbol font was decoded). I have reconstructed the intended meaning by pattern-matching the garbled characters against the surrounding numeric structure (e.g. a value, a tolerance, a comparison), **not** by consulting the original PDF's rendered page. The mapping I inferred is:
>
> | Garbled OCR character(s) | Reconstructed as | Basis |
> |---|---|---|
> | `ð` | `(` | consistently opens bracketed expressions |
> | `Þ` | `)` | consistently closes bracketed expressions |
> | `Ä` | `−` (minus) | appears between a variable and a tolerance value inside brackets, e.g. "vlms,avrg Ä 0,5" |
> | `þ` | `+` (plus) | mirrors `Ä` on the upper-bound side of the same inequality |
> | `Ï` | `≤` (less-than-or-equal) | used as the comparison operator in two-sided inequalities |
> | `Ü` | `×` (multiplication) | appears before a numeric tolerance factor, e.g. "× 0,8" / "× 1,2" |
> | `¼` | `=` (equals) | appears in definition formulas, e.g. "rdyn,avrg ¼ 30 · igear..." |
> | `;` between two digits | `,` (decimal comma, EU convention) | e.g. "0;5" reconstructed as "0,5" |
> | `Pn  i¼1` / `Xn  j¼1` | `Σ (i=1 to n)` / `Σ (j=1 to n)` | summation sigma rendered as stray "P"/"X" plus "i¼1"/"j¼1" |
> | long "ffiffi...q" runs | square-root radical `√[ ... ]` | radical sign glyph decomposed by OCR into repeated "ffi" strokes with a trailing "q" |
> | `Ê ... Ì` | `(` ... `)` around a fraction | alternate bracket glyph pair, same role as ð/Þ |
>
> **I am flagging this explicitly per your standing instruction not to pass off reconstructions as verified fact.** The *values* (tolerances, thresholds, Hz rates, percentages) are transcribed with high confidence because they appear as plain digits, not symbols. The *operators* (≤ vs <, the exact bracket nesting) are my best-effort reconstruction of intent and **should be verified against the actual PDF page images** (pages 347–352 of the consolidated PDF, "02017R2400 — EN — 01.01.2026 — 007.001 — 347" through "— 352") before being encoded into any simulation logic. I did not have access to the rendered PDF page, only the OCR text layer, in this task.

---

## 3.9 Input data for air drag pre-processing tool (►M1 heading amendment)

The following tables show the requirements for measurement data recording and preparatory data processing for input into the air drag pre-processing tool:
- Table 2 (numbered "Table 1" in some print runs — see note below) — vehicle data file
- Table 3 — ambient conditions file
- Table 4 — measurement section configuration file
- Table 5 — measurement data file
- Table 6 — altitude profile files (optional input data)

**►M1** A detailed description of the requested data formats, input files and evaluation principles can be found in the **technical documentation of the air drag pre-processing tool** (external document, not part of the Regulation text itself — flagged as a gap: the actual calculation algorithm is not in this Annex). ◄ Data processing shall be applied as specified in section 3.8.

> **Table-numbering discrepancy in the source text:** the prose at the start of 3.9 says "Table 2 for the vehicle data file," but the table that immediately follows is explicitly headed "**Table 1** — Input data for the air drag pre-processing tool – vehicle data file." This is reproduced exactly as it appears in the consolidated text; it looks like a numbering inconsistency in the official consolidated document itself (possibly a leftover from an earlier amendment renumbering), not an OCR error, since both the "Table 2" reference and the "Table 1" heading render as plain digits. Flagging this for the user rather than silently "fixing" it.

### Table 1 (referenced in prose as "Table 2") — vehicle data file (▼M3 / ▼B)

| Input data | Unit | Remarks |
|---|---|---|
| Vehicle group code | [-] | 1–19 for heavy lorries (Table 1 of Annex I); 31a–40f for heavy buses (Tables 4–6 of Annex I); 51–56 for medium lorries (Table 2 of Annex I) |
| Vehicle configuration with trailer | [-] | 'No' if measured without trailer; 'Yes' if measured with trailer (tractor–semitrailer combination) |
| Vehicle test mass | [kg] | actual mass during measurements |
| Technically permissible maximum laden mass | [kg] | heavy lorries: of the rigid lorry or tractor (w/o trailer or semitrailer); all other vehicle classes: no entry |
| Axle ratio | [-] | axle transmission ratio (footnotes 1, 2 — see below) |
| Gear ratio high speed | [-] | transmission ratio of gear engaged during high speed test (footnotes 1, 4) |
| Gear ratio low speed | [-] | transmission ratio of gear engaged during low speed test (footnotes 1, 4) |
| Anemometer height | [m] | height above ground of the installed anemometer's measurement point |
| Vehicle height | [m] | medium/heavy rigid lorries & tractors: max vehicle height per 3.5.3.1 item vii; all other vehicle classes: no entry |
| Fixed transmission ratio in low speed test | [-] | 'yes'/'no' (for vehicles that cannot drive with locked torque converter in the low speed test) |
| Vehicle maximum speed | [km/h] | maximum speed the vehicle can be practically operated at on the test track (footnote 3) |
| Torque meter drift left wheel | [Nm] | average torque meter readings per 3.5.3.9 |
| Torque meter drift right wheel | [Nm] | — |
| Time stamp zeroing of torque meters | [s] since day start (of first day) | — |
| Time stamp drift check torque meters | [s] since day start (of first day) | — |

Footnotes:
1. Transmission ratios specified with at least 3 digits after the decimal separator.
2. If either the cardan speed signal or the average wheel speed signal is provided (see 3.4.3, Option 1 for vehicles with torque converters, or Option 2), the axle ratio input parameter shall be set to **'1 000'**.
3. Input only required if the value is lower than **88 km/h**.
4. If average wheel speed is provided (3.4.3 Option 2), the gear ratio input parameters shall be set to **'1 000'**.

### Table 3 — ambient conditions file (▼M3)

| Signal | Column identifier | Unit | Measurement rate | Remarks |
|---|---|---|---|---|
| Time | `<t>` | [s] since day start (first day) | — | — |
| Ambient temperature | `<t_amb_stat>` | [°C] | at least 1 averaged value per 6 minutes | stationary weather station |
| Ambient pressure | `<p_amb_stat>` | [mbar] | " | stationary weather station |
| Relative air humidity | `<rh_stat>` | [%] | " | stationary weather station |

### Table 4 — measurement section configuration file (▼B)

| Input data | Unit | Remarks |
|---|---|---|
| Trigger signal used | [-] | 1 = trigger signal used; 0 = no trigger signal used |
| Measurement section ID | [-] | user-defined ID number |
| Driving direction ID | [-] | user-defined ID number |
| Heading | [°] | heading of the measurement section |
| Length of the measurement section | [m] | — |
| Latitude start point of section | decimal degrees or decimal minutes | standard GPS, decimal degrees: min. 5 digits after decimal separator |
| Longitude start point of section | " | standard GPS, decimal minutes: min. 3 digits after decimal separator |
| Latitude end point of section | " | DGPS, decimal degrees: min. 7 digits after decimal separator |
| Longitude end point of section | " | DGPS, decimal minutes: min. 5 digits after decimal separator |
| Path and/or filename of altitude file | [-] | only required for constant speed tests (not the misalignment test) and if altitude correction is enabled |

### Table 5 — measurement data file (▼B / ▼M1 / ▼M3 / ▼M4)

| Signal | Column identifier | Unit | Measurement rate | Remarks |
|---|---|---|---|---|
| Time | `<t>` | [s] since day start (first day) | 100 Hz | rate fixed to 100 Hz; used for correlation with weather data and frequency checks |
| (D)GPS latitude | `<lat>` | decimal degrees or decimal minutes | GPS ≥ 4 Hz; DGPS ≥ 100 Hz | standard GPS decimal degrees: min. 5 digits after decimal separator |
| (D)GPS longitude | `<long>` | — | — | standard GPS decimal minutes: min. 3 digits; DGPS decimal degrees: min. 7 digits; DGPS decimal minutes: min. 5 digits after decimal separator |
| (D)GPS heading | `<hdg>` | [°] | ≥ 4 Hz | — |
| DGPS velocity | `<v_veh_GPS>` | [km/h] | ≥ 20 Hz | — |
| Vehicle velocity | `<v_veh_CAN>` | [km/h] | ≥ 20 Hz | raw CAN bus front axle signal |
| Air speed | `<v_air>` | [m/s] | ≥ 4 Hz | raw data (instrument reading) |
| Inflow angle (beta) | `<beta>` | [°] | ≥ 4 Hz | raw data (instrument reading); '180°' = air flow from front |
| Engine speed, cardan speed, average wheel speed, or electric motor speed | `<n_eng>`, `<n_card>`, `<n_wheel_ave>` or `<n_EM>` | [rpm] | ≥ 20 Hz | see provisions in 3.4.3 (▼M3) |
| Torque meter (left wheel) | `<tq_l>` | [Nm] | ≥ 20 Hz | — |
| Torque meter (right wheel) | `<tq_r>` | [Nm] | ≥ 20 Hz | — |
| Ambient temperature on vehicle | `<t_amb_veh>` | [°C] | ≥ 1 Hz | — |
| Trigger signal | `<trigger>` | [-] | 100 Hz | optional; required if measurement sections identified by opto-electronic barriers (option 'trigger_used=1') |
| Proving ground temperature | `<t_ground>` | [°C] | ≥ 1 Hz | — |
| Validity | `<valid>` | [-] | — | optional signal (1 = valid; 0 = invalid) |
| Service brake (▼M4) | `<s_brake>` | [-] | ≥ 4 Hz | 'Service brake demand pressure' per **ISO 11992-2:2014** (0 = passive, 1 = active) |

### Table 6 — altitude profile file (▼B)

| Input data | Unit | Remarks |
|---|---|---|
| Latitude | decimal degrees or decimal minutes | decimal degrees: min. 7 digits after decimal separator |
| Longitude | " | decimal minutes: min. 5 digits after decimal separator |
| Altitude | [m] | min. 2 digits after decimal separator |

---

## 3.10 Validity criteria (▼B)

This section sets out the criteria to obtain valid results in the air drag pre-processing tool.

### 3.10.1 Validity criteria for the constant speed test

#### 3.10.1.1 — Dataset acceptance criteria

The air drag pre-processing tool accepts datasets recorded during the constant speed test if **all** of the following are met:

i. Average vehicle speed is within the criteria of 3.5.2 (high speed test range, also used by reference for stability checks).
ii. Ambient temperature is within the range of 3.2.2, checked from the vehicle-measured ambient temperature signal.
iii. Proving ground temperature is within the range of 3.2.3.
iv. Valid average wind speed conditions per 3.2.5 item i.
v. Valid gust wind speed conditions per 3.2.5 item ii.
vi. Valid average yaw angle conditions per 3.2.5 item iii.

vii. **Stability criteria for vehicle speed:**

**Low speed test:**

> (vlms,avrg − 0,5 km/h) ≤ vlm,avrg ≤ (vlms,avrg + 0,5 km/h)

where:
- `vlms,avrg` = average of vehicle speed per measurement section [km/h]
- `vlm,avrg` = central moving average of vehicle speed with `Xms` seconds time base [km/h]
- `Xms` = time needed to drive 25 m distance at actual vehicle speed [s]

**High speed test:**

> (vhms,avrg − 0,3 km/h) ≤ vhm,avrg ≤ (vhms,avrg + 0,3 km/h)

where:
- `vhms,avrg` = average of vehicle speed per measurement section [km/h]
- `vhm,avrg` = 1 s central moving average of vehicle speed [km/h]

viii. **Stability criteria for vehicle torque (▼M3 for low speed; ▼B for high speed):**

**Low speed test:**

> (Tlms,avrg − Tgrd) × (1 − tol) ≤ (Tlm,avrg − Tgrd) ≤ (Tlms,avrg − Tgrd) × (1 + tol)
>
> Tgrd = Fgrd,avrg × rdyn,avrg

where:
- `Tlms,avrg` = average of Tsum per measurement section
- `Tgrd` = average torque from gradient force
- `Fgrd,avrg` = average gradient force over the measurement section
- `rdyn,avrg` = average effective rolling radius over the measurement section (formula under item xi below) [m]
- `Tsum` = TL + TR; sum of corrected torque values, left and right wheel [Nm]
- `Tlm,avrg` = central moving average of Tsum with `Xms` seconds time base
- `Xms` = time needed to drive 25 m distance at actual vehicle speed [s]
- `tol` = relative torque tolerance: **0,5** for medium lorries and heavy lorries in groups 1s, 1 and 2; **0,3** for heavy lorries in other groups and heavy buses

> **Note:** the reconstructed text above shows the *same* bracket expression `(Tlms,avrg – Tgrd)` on both the left side (inside the parenthetical minus Tgrd) and seemingly re-used as the upper-bound multiplier base in the OCR source; the raw OCR literally repeats `(Tlms,avrg – Tgrd)` three times rather than switching the middle term to `Tlm,avrg`. I have corrected the middle term to `Tlm,avrg` by analogy with the high-speed-test formula immediately below it (which uses `Thm,avrg` in the middle, `Thms,avrg` on the outer bounds) and with the vehicle-speed stability criteria pattern (moving average bounded between two static-average ± tolerance bounds). **This is an inferred correction, not a verified transcription — check against the original PDF.**

**High speed test:**

> (Thms,avrg − Tgrd) × 0,8 ≤ (Thm,avrg − Tgrd) ≤ (Thms,avrg − Tgrd) × 1,2

where:
- `Thms,avrg` = average of Tsum per measurement section [Nm]
- `Tgrd` = average torque from gradient force (see low speed test definition) [Nm]
- `Tsum` = TL + TR; sum of corrected torque values, left and right wheel [Nm]
- `Thm,avrg` = 1 s central moving average of Tsum [Nm]

(i.e. a **± 20 %** band around the gradient-corrected average torque for the high speed test.)

ix. Valid heading of the vehicle passing a measurement section: **< 10° deviation** from target heading (applicable to low speed test, high speed test, and misalignment test).

x. Driven distance inside the measurement section, calculated from calibrated vehicle speed, shall not differ from the target distance by more than **3 metres** (applicable to low speed test and high speed test).

xi. **►M3** Plausibility check for engine speed, cardan speed, or average wheel speed (whichever applicable):

**Engine speed or average wheel speed check — high speed test:**

> [ 30 · igear · iaxle · (vhms,avrg − 0,3) / 3,6 ] / [ rdyn,ref,HS · π · (1 − 0,02) ] ≤ neng,1s ≤ [ 30 · igear · iaxle · (vhms,avrg + 0,3) / 3,6 ] / [ rdyn,ref,HS · π · (1 + 0,02) ]
>
> rdyn,avrg = 30 · igear · iaxle · vhms,avrg / (3,6 · neng,avrg · π)
>
> rdyn,ref,HS = (1/n) · Σ (j=1 to n) rdyn,avrg,j

where:
- `igear` = transmission ratio of the gear selected in the high speed test [-]
- `iaxle` = axle transmission ratio [-]
- `vhms,avrg` = average vehicle speed (high speed measurement section) [km/h]
- `neng,1s` = 1 s central moving average of engine speed or average wheel speed (high speed measurement section) [rpm]
- `neng,avrg` = average engine speed or average wheel speed (high speed measurement section) [rpm]
- `rdyn,avrg` = average effective rolling radius for a single high speed measurement section [m]
- `rdyn,ref,HS` = reference effective rolling radius calculated from all valid high speed measurement sections (number = n) [m]

**Engine speed or average wheel speed check — low speed test:**

> [ 30 · igear · iaxle · (vlms,avrg − 0,5) / 3,6 ] / [ rdyn,ref,LS1/LS2 · π · (1 − 0,02) ] ≤ neng,float ≤ [ 30 · igear · iaxle · (vlms,avrg + 0,5) / 3,6 ] / [ rdyn,ref,LS1/LS2 · π · (1 + 0,02) ]
>
> rdyn,avrg = 30 · igear · iaxle · vlms,avrg / (3,6 · neng,avrg · π)
>
> rdyn,ref,LS1/LS2 = (1/n) · Σ (j=1 to n) rdyn,avrg,j

where (▼M1):
- `igear` = transmission ratio of the gear selected in the low speed test [-]
- `iaxle` = axle transmission ratio [-]
- `vlms,avrg` = average vehicle speed (low speed measurement section) [km/h]
- `neng,float` = central moving average of engine speed or average wheel speed with `Xms` seconds time base (low speed measurement section) [rpm]
- `neng,avrg` = average engine speed or average wheel speed (low speed measurement section) [rpm]
- `Xms` = time needed to drive 25 metre distance at low speed [s]
- `rdyn,avrg` = average effective rolling radius for a single low speed measurement section [m]
- `rdyn,ref,LS1/LS2` = reference effective rolling radius calculated from all valid measurement sections for low speed test 1 or low speed test 2 (number = n) [m]

The plausibility check for **cardan speed** is performed analogously, with `neng,1s` replaced by `ncard,1s` (1 s central moving average of cardan speed in the high speed measurement section), `neng,float` replaced by `ncard,float` (moving average of cardan speed with `Xms` seconds time base in the low speed measurement section), and `igear` set to a value of **1**.

xii. The particular part of the measurement data was not marked as **'invalid'** in the air drag pre-processing tool input file.

#### 3.10.1.2 — Unequal dataset counts between the two low speed runs

The pre-processing tool excludes single datasets from evaluation if the number of datasets for a particular combination of measurement section and driving direction differs between the first and second low speed tests. In this case, the **first datasets from the low speed run with the higher number of datasets are excluded** (i.e. datasets are trimmed from the start of the run with more datasets until counts match).

#### 3.10.1.3 — Exclusion of section/direction combinations

The tool excludes a single combination of measurement section and driving direction from the evaluation if:
i. No valid dataset is available from low speed test 1 and/or low speed test 2.
ii. Fewer than **two** valid datasets from the high speed test are available.

#### 3.10.1.4 — Conditions invalidating the complete constant speed test

The tool considers the complete constant speed test invalid if:
i. Test track requirements per 3.1.1 are not met.
ii. Fewer than **10 datasets per heading** available (high speed test).
iii. Fewer than **5 valid datasets per heading** available (misalignment calibration test).

**▼M1**
iv. The rolling resistance coefficients (RRC) for the first and second low speed test differ by more than **0,40 kg/t**. Checked separately for each measurement-section/driving-direction combination.

### 3.10.2 Validity criteria for the misalignment test

#### 3.10.2.1 — Dataset acceptance criteria

The tool accepts datasets recorded during the misalignment test if:
i. Average vehicle speed is within the criteria of 3.5.2 for the high speed test.
ii. Valid average wind speed conditions per 3.2.5 item i.
iii. Valid gust wind speed conditions per 3.2.5 item ii.
iv. Valid average yaw angle conditions per 3.2.5 item iii.

v. **Stability criteria for vehicle speed:**

> (vhms,avrg − 1 km/h) ≤ vhm,avrg ≤ (vhms,avrg + 1 km/h)

where:
- `vhms,avrg` = average of vehicle speed per measurement section [km/h]
- `vhm,avrg` = 1 s central moving average of vehicle speed [km/h]

#### 3.10.2.2 — Single measurement section invalidity

The tool considers data from a single measurement section invalid if:
i. The average vehicle speeds from all valid datasets from each driving direction differ by more than **2 km/h**.
ii. Fewer than **5 datasets per heading** are available.

#### 3.10.2.3 — Complete misalignment test invalidity

The tool considers the complete misalignment test invalid if no valid result is available for a single measurement section.

**▼M4** — (an em-dash / deletion marker appears alone at this point in the consolidated text, indicating a previously-amended sub-point was deleted by M4 and left blank; no replacement text follows in the source.)

---

## Cross-references used in this section

- Annex I, Tables 1, 2, 4–6 — vehicle group code definitions (external to this extraction range)
- Annex Xa, Table 2 — wheel-speed measurement method requirements (external)
- ISO 11992-2:2014 — service brake demand pressure signal definition (external)
- Technical documentation of the air drag pre-processing tool — referenced but not part of the Regulation text (external software documentation; genuine gap in the legal text for a from-scratch re-implementation of Cd·Acr(0))

## Figures referenced but not visually extracted

None identified in sections 3.9–3.10.
