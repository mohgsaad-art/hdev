# Annex VI — Verifying Transmission, Torque Converter, OTTC and ADC Data
## Part C: Torque Converter (§4), Other Torque Transferring Components / Retarders (§5), and Additional Driveline Components (§6 — including the EV-relevant "Case C" provision)

**Source:** Commission Regulation (EU) 2017/2400, consolidated text CELEX **02017R2400**, consolidation date **01.01.2026**, version 007.001.
**Range covered in this file:** Annex VI §4 (Torque converter testing), §5 (OTTC/retarder testing), §6 (ADC testing, incl. §6.1.3 Case C), Appendix 9 (generic TC model), Appendix 10 (standard OTTC/retarder loss values), and Appendices 3–5 (TC/OTTC/ADC information documents).
**Companion files:** `07a` (definitions & general test setup), `07b` (transmission loss-measurement procedures, calculation methods, standard values, simulation-tool input parameters, conformity testing).

Amendment markers in this range: **►B**, **►M1**, **►M3**, and — critically — **►M4** (Regulation (EU) 2025/258), which introduces the explicit EV-relevant provision flagged below.

**OCR note:** As in file `07b`, mathematical formulas in this file are given both as "Raw OCR" (exact extracted text, with "¼"="=", "Ä"="−", "Ü"="×") and "Reconstructed" (readable form). See `07b`'s header for the full explanation of this convention.

---

## 4. Testing procedure for torque converter (TC)

▼M3 The TC characteristics needed for simulation-tool input are:
- **Tpum1000** — the reference (pump) torque at 1 000 rpm input speed
- **μ** — the torque ratio of the torque converter

Both depend on the **speed ratio v** (= output/turbine speed ÷ input/pump speed) of the TC.

The applicant applies the same method for TC characterisation **irrespective of which transmission-torque-loss option was chosen**.

### Case S vs. Case P (TC/mechanical-transmission arrangement)
- **Case S**: TC and mechanical transmission parts in **serial** arrangement.
- **Case P**: TC and mechanical transmission parts in **parallel** arrangement (power-split installation).

For **Case S**, TC characteristics may be evaluated either separately from the mechanical transmission, or in combination with it. For **Case P**, evaluation is possible **only** in combination with the mechanical transmission — and in that case, for hydromechanical gears under measurement, the **whole arrangement** (TC + mechanical transmission) is treated as a TC with characteristic curves similar to a standalone converter. When measured together with a mechanical transmission, the speed ratio v and all corresponding step widths/limits are adjusted for the mechanical transmission ratio.

### Two measurement options
(i) **Option A**: measurement at constant input speed.
(ii) **Option B**: measurement at constant input torque, per **SAE J643**.

The manufacturer may choose A or B for either Case S or Case P.

For simulation-tool input, torque ratio μ and reference torque Tpum are measured for **v ≤ 0,95** (vehicle propulsion mode). If standard values are used, TC-characteristic data provided to the tool covers only v ≤ 0,95 (or the adjusted speed ratio); **the simulation tool automatically adds generic values for overrun conditions.**

### Table 1 — Default values for v ≥ 1,00 (overrun conditions)
| v | μ | Tpum1000 |
|---|---|---|
| 1,000 | 1,0000 | 0,00 |
| 1,100 | 0,9999 | −40,34 |
| 1,222 | 0,9998 | −80,34 |
| 1,375 | 0,9997 | −136,11 |
| 1,571 | 0,9996 | −216,52 |
| 1,833 | 0,9995 | −335,19 |
| 2,200 | 0,9994 | −528,77 |
| 2,500 | 0,9993 | −721,00 |
| 3,000 | 0,9992 | −1 122,00 |
| 3,500 | 0,9991 | −1 648,00 |
| 4,000 | 0,9990 | −2 326,00 |
| 4,500 | 0,9989 | −3 182,00 |
| 5,000 | 0,9988 | −4 242,00 |

*(Reproduced exactly as in the source; the OCR rendered minus signs as "Ä" in the source table header context but the values themselves extracted with literal "–" minus signs, shown above as standard minus signs.)*

---

## 4.1. Option A: Measured TC characteristics at constant speed

### 4.1.1. General requirements
TC used for measurement must conform to drawing specifications for series production TCs. Modifications for testing (e.g. sensor inclusion) are permitted. Upon approval-authority request, the applicant must specify and prove conformity with Annex requirements.

### 4.1.2. Oil temperature
- TC measured **separately** from the transmission: input oil temperature = **90 °C +7/−3 K**.
- TC measured **together with** the transmission (Case S or P): **90 °C +20/−3 K**.
- Measured at drain plug or oil sump; if measured separately from the transmission, measured **prior to entering the converter test drum/bench**.

### 4.1.3. Oil flow rate and pressure
Input TC oil flow rate and output oil pressure kept within specified operational limits for the TC, depending on the related transmission type and the tested maximum input speed.

### 4.1.4. Oil quality/viscosity — as specified for transmission testing (3.1.2.5.3–3.1.2.5.4 in file `07a`).

### 4.1.5. Installation
TC installed on a testbed with torque sensor, speed sensor, and electric machine at **both** input and output shaft of the TC.

### 4.1.6. Measurement equipment
Calibration labs: ►M3 IATF ◄ 16949, ISO 9000 series, or ISO/IEC 17025; traceable to national/international standards.
- **4.1.6.1. Torque**: sensor uncertainty < **1 %** of measured torque; higher-uncertainty sensors allowed if the excess over 1% is calculated and added per 4.1.7.
- **4.1.6.2. Speed**: ≤ **± 1 rpm**
- **4.1.6.3. Temperature**: ambient and oil, both ≤ **± 1,5 K**

### 4.1.7. Test procedure
- **4.1.7.1.** Zero torque signal compensation — as 3.1.6.1.
- **4.1.7.2. Measurement sequence:**
  1. Input (pump) speed `npum` fixed constant within **1 000 rpm ≤ npum ≤ 2 000 rpm**.
  2. Speed ratio v adjusted by increasing output (turbine) speed `ntur` from 0 rpm up to the npum set value.
  3. Step width: **0,1** for v ∈ [0, 0,6]; **0,05** for v ∈ [0,6, 0,95].
  4. Upper v limit may be set below 0,95 by the manufacturer, provided **≥ 7 evenly distributed points** between v=0 and v<0,95 are covered.
  5. ►M3 Min. **3-second** stabilisation per point within the §4.1.2 temperature limits, extendable to max 60 s. Oil temperature recorded during stabilisation. ◄
  6. Per point, signals (§4.1.8) recorded for **min 3 s, max 15 s**.
  7. Full sequence (steps 1–6) performed **two times total**.

### 4.1.8. Measurement signals and data recording
At least: (1) Input (pump) torque Tc,pum [Nm]; (2) Output (turbine) torque Tc,tur [Nm]; (3) Input (pump) speed npum [rpm]; (4) Output (turbine) speed ntur [rpm]; (5) TC input oil temperature KTCin [°C]. Sampling ≥ 100 Hz; low-pass filter applied.

### 4.1.9. Measurement validation
- 4.1.9.1. Arithmetic mean of torque/speed for the 3–15 s window, per measurement.
- 4.1.9.2. Average the two measured torque/speed sets.
- 4.1.9.3. Deviation between the two averaged torques < **± 5 % of average or ± 1 Nm**, whichever larger → average taken. If higher, use for subsequent calculations (4.1.10./4.1.11.) or repeat the test:
  - For ΔUT,pum/tur calc: smallest averaged Tc,pum/tur value
  - For torque-ratio μ calc: largest averaged Tc,pum, smallest averaged Tc,tur
  - For reference-torque Tpum1000 calc: smallest averaged Tc,pum
- 4.1.9.4. Averaged input-shaft speed/torque < **± 5 rpm and ± 5 Nm** of set point for each operating point across the complete speed-ratio series.

### 4.1.10. Measurement uncertainty
Raw OCR: `ΔUT,pum/tur = MAX (0, (UT,pum/tur – 0,01 * Tc,pum/tur))`

**ΔUT,pum/tur = MAX(0, (UT,pum/tur − 0,01 × Tc,pum/tur))** — only the part of UT,pum/tur exceeding 1% of measured torque is used to correct the characteristic value.

Based on a single parameter: calibration error (sensitivity tolerance, linearity, hysteresis, repeatability), at 95% confidence:

**UT,pum/tur = 2 × ucal**, where (Raw OCR: `ucal ¼ 1 Ü Wcal / kcal Ü Tn`) **ucal = 1 × (Wcal/kcal) × Tn**.

**Variables:** `Tc,pum/tur` = current/measured torque at input/output sensor (uncorrected) [Nm]; `Tpum` = input (pump) torque after uncertainty correction [Nm]; `UT,pum/tur` = uncertainty of input/output torque measurement at 95% confidence, separately for input/output sensor [Nm]; `Tn` = nominal torque value of sensor [Nm]; `ucal` = uncertainty by calibration [Nm]; `Wcal` = relative calibration uncertainty (% of nominal torque); `kcal` = calibration advancement factor (declared by manufacturer, else = 1).

### 4.1.11. Calculation of TC characteristics

Torque ratio:
Raw OCR: `μ ¼ Tc;tur Ä ΔUT;tur / Tc;pum þ ΔUT;pum`
Reconstructed: **μ = (Tc,tur − ΔUT,tur) / (Tc,pum + ΔUT,pum)**

Speed ratio:
Raw OCR: `v ¼ ntur / npum`
Reconstructed: **v = ntur / npum**

Reference torque at 1000 rpm:
Raw OCR: `Tpum1000 ¼ ðTc;pum Ä ΔUT;pumÞ Ü Í 1 000 rpm / npum Î2`
Reconstructed: **Tpum1000 = (Tc,pum − ΔUT,pum) × (1000 rpm / npum)²**

**Variables:** μ = torque ratio of the TC [-]; v = speed ratio of the TC [-]; Tc,pum = input (pump) torque, corrected [Nm]; npum = input (pump) speed [rpm]; ntur = output (turbine) speed [rpm]; Tpum1000 = reference torque at 1000 rpm [Nm].

---

## 4.2. Option B: Measurement at constant input torque (per SAE J643)

4.2.1–4.2.6. General requirements, oil temperature, oil flow/pressure, oil quality, installation, measurement equipment — all **as specified for Option A** (4.1.1.–4.1.6.).

### 4.2.7. Test procedure
- 4.2.7.1. Zero torque signal compensation — as 3.1.6.1.
- ▼M4 **4.2.7.2. Measurement sequence:**
  1. Input torque Tpum set to a positive level at npum = **1000 rpm**, with the TC output shaft held non-rotating (ntur = 0 rpm). *(Note: this step is marked ▼B in the source immediately following the ▼M4 heading for 4.2.7.2 — i.e., the sub-step text itself is the original 2017 baseline language, while the M4 amendment evidently affected the heading/structure of 4.2.7.2 without visibly changed wording extracted in this OCR. Flagged as ambiguous — it's unclear from the text-only extraction exactly what M4 changed in this clause; verify against the official amending Regulation 2025/258 if the precise change matters.)*
  2. Speed ratio v adjusted by increasing ntur from 0 rpm up to a value covering the usable v range with **≥ 7 evenly distributed speed points**.
  3. Step width: **0,1** for v ∈ [0, 0,6]; **0,05** for v ∈ [0,6, 0,95].
  4. Upper v limit may be set below 0,95 by the manufacturer.
  5. ►M3 Min. **5-second** stabilisation per point within §4.2.2 temperature limits, extendable to max 60 s. Oil temperature recorded during stabilisation. ◄
  6. ▼M3 Per point, values (§4.2.8) recorded for **min 5 s, max 15 s**.
  7. ▼B Full sequence performed **two times total**.

### 4.2.8–4.2.11. Measurement signals/validation/uncertainty/TC-characteristic calculation — all **as specified for Option A** (4.1.8.–4.1.11.).

---

## 5. ►M3 Testing procedure for other torque transferring components (OTTC) ◄

**Scope**: engine retarders, transmission retarders, driveline retarders, and components treated in the simulation tool as a retarder. Includes vehicle-starting devices like a single wet transmission input clutch or hydro-dynamic clutch.

## 5.1. Methods for establishing retarder drag losses

Retarder drag torque loss is a function of **retarder rotor speed**. Since a retarder can be integrated at different points in the driveline, rotor speed depends on the drive part (speed reference) and the step-up ratio between drive part and retarder rotor:

### Table 2 — Retarder rotor speeds
| Configuration | Speed reference | Retarder rotor speed calculation |
|---|---|---|
| A. Engine Retarder | Engine Speed | `nretarder = nengine × istep-up` |
| B. Transmission Input Retarder | Transmission Input Shaft Speed | `nretarder = ntransm.input × istep-up = ntransm.output × itransm × istep-up` |
| ▼M3 C. Transmission Output Retarder or Axlegear Input Retarder | Transmission Output Shaft Speed or Axlegear Input Shaft Speed | `nretarder = ntransm.output × istep-up` |

where: `istep-up` = step-up ratio = retarder rotor speed/drive part speed; `itransm` = transmission ratio = transmission input speed/transmission output speed.

Retarders **integrated in the engine and non-separable** are tested together with the engine (not covered by this section). Retarders **disconnectable** from the driveline/engine via any clutch are treated as having **zero rotor speed** (hence zero power losses) when disconnected.

Retarder drag losses are measured by one of:
1. Measurement on the retarder as a stand-alone unit
2. Measurement in combination with the transmission

### 5.1.1. General requirements
If measured stand-alone, results are affected by test-rig bearing torque losses — permitted to measure and subtract these. Retarder used must conform to series-production drawing specifications; test modifications (sensors, external oil conditioning) permitted. Per the **family concept** (Appendix 6), measured drag losses for transmissions-with-retarder can be used for the equivalent transmission-without-retarder. Same transmission unit may be used for measuring both with/without-retarder variants. Applicant must prove conformity on approval-authority request.

### 5.1.2. Run-in
Optional, on applicant request:
- 5.1.2.1. Run-in time ≤ **100 hours** at zero retarder apply torque; optionally up to **6 hours** with retarder apply torque.

### 5.1.3. Test conditions
- **5.1.3.1. Ambient temperature**: 25 °C ± 10 K, measured 1 m laterally from the retarder.
- **5.1.3.2. Ambient pressure**: for magnetic retarders, min. **899 hPa** per International Standard Atmosphere (ISA), ISO 2533.
- **5.1.3.3. Oil/water temperature** (hydrodynamic retarders): except for the fluid, no external heating allowed. Stand-alone testing: fluid temp ≤ **87 °C**. Combined-with-transmission testing: transmission testing oil-temp limits apply (see file `07a`, §3.1.2.5.2.).
- **5.1.3.4. Oil/water quality**: new recommended first-fill oil for the European market. For water retarders: water quality per manufacturer spec; water pressure fixed near vehicle condition (**1 ± 0,2 bar** relative pressure at retarder input hose).
- **5.1.3.5. Oil viscosity**: multiple recommended first-fill oils considered equal if kinematic viscosity within **50 %** of each other at the same temperature (within the KV100 tolerance band) — note this is a **wider** tolerance than the 10% used for transmission oils.
- **5.1.3.6. Oil/water level**: per nominal retarder specification.

### 5.1.4. Installation
Electric machine, torque sensor, speed sensor mounted at the input side of the retarder or transmission. Installation inclination angle as for vehicle installation per homologation drawing **± 1°**, or at **0° ± 1°**.

### 5.1.5. Measurement equipment — as specified for transmission testing (3.1.4., file `07a`).

### 5.1.6. Test procedure
- 5.1.6.1. Zero torque signal compensation — as 3.1.6.1.
- 5.1.6.2. Measurement sequence follows the transmission-testing provisions of 3.1.6.3.2.–3.1.6.3.5.
  - **5.1.6.2.1. Stand-alone unit**: speed points **200, 400, 600, 900, 1200, 1600, 2000, 2500, 3000, 3500, 4000, 4500, 5000 rpm**, continuing up to the maximum retarder rotor speed.
  - **5.1.6.2.2. In combination with transmission**:
    1. Selected transmission gear must allow the retarder to reach its maximum rotor speed.
    2. Torque loss measured at the operating speeds per the related transmission testing.
    3. Measurement points may be added below 600 rpm (transmission input speed) if requested by the manufacturer.
    4. **Separation method** (manufacturer option) — test in order:
       1. Load-independent torque loss for the complete transmission **including** retarder, measured per §3.1 (transmission testing), in one of the higher gears → `Tl,in,withret`
       2. Replace retarder/related parts with the equivalent no-retarder variant parts; repeat the measurement → `Tl,in,withoutret`
       3. Load-independent retarder-system torque loss = difference: `Tl,in,retsys = Tl,in,withret − Tl,in,withoutret`

### 5.1.7. Measurement signals and data recording — as transmission testing (3.1.5., file `07a`).
### 5.1.8. Measurement validation — all recorded data checked/processed per transmission testing (3.1.7., file `07b`).

## 5.2. Complement of input files for the simulation tool (retarder)
- 5.2.1. Retarder torque losses for speeds below the lowest measurement speed = the measured loss **at** that lowest speed (held constant, not extrapolated).
- 5.2.2. If retarder losses were separated via the with/without-retarder difference method (5.1.6.2.2.4.), the actual retarder rotor speed depends on retarder location and/or selected gear ratio and retarder step-up ratio, and may differ from the measured transmission input shaft speed — actual rotor speeds relative to the measured drag-loss data are calculated per Table 2 (§5.1 above).
- 5.2.3. Torque loss map data formatted/saved per Appendix 12 (file `07b`).

---

## ▼M3 6. Testing procedure for additional drivetrain components (ADC) / drivetrain component with a single speed ratio (e.g. angle drive)

## 6.1. Methods for establishing losses of a drivetrain component with a single speed ratio

▼M1 The losses of a single-speed-ratio drivetrain component are determined using one of the following cases:

### 6.1.1. Case A: Measurement on a separate drivetrain component with a single speed ratio
The same **three options** defined for transmission-loss determination apply:
- **Option 1**: Measured torque-independent losses, calculated torque-dependent losses (= Transmission test Option 1)
- **Option 2**: Measured torque-independent losses, measured torque-dependent losses at full load (= Transmission test Option 2)
- **Option 3**: Measurement under full-load points (= Transmission test Option 3)

Measurement/validation/uncertainty follow the corresponding transmission-test-option procedure in §3, **diverging in the following**:

Measurements performed at **200 rpm and 400 rpm** (at the component's input shaft), and at **600, 900, 1200, 1600, 2000, 2500, 3000, 4000 rpm** and multiples of 10 of these up to the maximum speed per the component's specification, or the last speed point before the defined maximum. Additional intermediate points permitted.

**6.1.1.1. Applicable speed range**: *(heading present in source; no further text follows it in the extracted range before §6.1.2 — flagged as possibly truncated or as a heading with content that did not extract separately from the paragraph above it.)*

### 6.1.2. Case B: Individual measurement of a single-speed-ratio drivetrain component connected to a transmission
Testing follows one of the defined transmission-testing options (Option 1/2/3, same definitions as 6.1.1.).

**6.1.2.1. Separation method** (manufacturer option) — test in order:
1. Torque loss for the complete transmission **including** the single-speed-ratio drivetrain component, measured per the applicable transmission-testing option → `Tl,in,withad`
2. Replace the component/related parts with the equivalent variant without it; repeat the measurement → `Tl,in,withoutad`
3. Torque loss for the component system = `Tl,in,adsys = max(0, Tl,in,withad − Tl,in,withoutad)` *(note the `max(0, …)` floor — unlike the retarder-separation formula in §5.1.6.2.2.4, which has no floor — i.e., ADC separation losses cannot be reported as negative, reproduced exactly as in the source.)*

### ▼M4 6.1.3. Case C: Belt (or similar technology) connecting an electric machine system to the main powertrain of the vehicle

> **★ EV-RELEVANCE — PRIMARY FINDING OF THIS ANNEX ★**
> This is the single most directly EV-relevant provision found anywhere in the assigned Annex VI range. It was introduced by **►M4 (Regulation (EU) 2025/258)** — the newest amendment visible in this extraction.

Full text (as extracted):

> "Case C: Belt (or similar technology) that is used for connection of an electric machine system to the main powertrain of the vehicle (as defined in the description of the optional ADC input data in Table 8 of Annex III of this Regulation). In this case the input data required in accordance with **Table 7 of Appendix 12** shall be determined in accordance with the provisions defined in **Appendix 11**, whereby the value of **fT shall be 0,08** and the **maximum available torque of the electric machine system shall be used for Tmax,in**."

**What this means in plain terms:**
- Where a vehicle's electric machine system is mechanically coupled to the main powertrain via a **belt (or similar technology)** — rather than being in-line/coaxial — that belt connection is classified as an **ADC (Additional Driveline Component) of type "single speed ratio,"** and its losses are calculated using the **Appendix 11** fallback formula (see file `07b` for the full formula):
  `Tl,ad,in = Tadd0 + Tadd1000 × (nin/1000 rpm) + fT_add × Tin`
  — but with **two EV-specific substitutions**:
  1. **fT = 0,08** (double the generic angle-drive default of 0,04 used elsewhere in Appendix 8/11 for a conventional bevel-gear angle drive).
  2. **Tmax,in = the maximum available torque of the electric machine system** (not a transmission/gearbox max input torque).
- The resulting loss-map data is reported using the **ADC/LossMap schema (Table 7 of Appendix 12)** — i.e., it is injected into the simulation tool through the same data channel as any other ADC, just with EV-specific input values.
- This confirms that **Annex III, Table 8** ("optional ADC input data") separately defines/describes this electric-machine-belt-connection scenario — that table was **not** part of this assigned Annex VI range, so its exact wording is **not reproduced here**; it should be read directly if the project needs the full definition of this ADC input-data category.

**Implication for the HDEV sizing tool**: if modelling a battery-electric or hybrid HDV where the e-motor drives the wheels (or a gearbox/axle) through a belt rather than a direct/coaxial shaft coupling, this is the regulatory mechanism VECTO uses to account for that belt's mechanical loss — a fixed-form loss equation parameterized by the motor's max torque, not a measured loss map (unless the manufacturer chooses to measure it under Case A/B instead, which Case C does not preclude — Case C is simply the *standard-values* fallback path specific to this belt-to-e-machine configuration).

## 6.2. Complement of input files for the simulation tool (ADC)
▼M3
- 6.2.1. Torque losses for speeds below the defined minimum speed, and additionally at input speed = **0 rpm**, set equal to the loss at the minimum speed.
- 6.2.2. Where the highest tested input speed was the last point below the component's defined max permissible speed: extrapolate up to max speed via **linear regression on the two last measured speed points**.
- 6.2.3. To calculate torque loss data for the transmission input shaft that the single-speed component is combined with: use **linear interpolation and extrapolation**.

---

## Appendix 9 — Generic model: torque converter

For TC characteristics determination, a **generic TC model** depending on specific engine characteristics may be applied. Valid **only** for a TC combined with an engine sharing the same characteristic engine data:
- `nrated` = Maximum engine speed at maximum power (from the engine full-load curve, as calculated by the engine pre-processing tool) [rpm]
- `Tmax` = Maximum engine torque (same source) [Nm]

### Four-point model for TC torque capacity
**[Figure 1 — "Generic torque capacity" — referenced in source but not visually extracted from this text-only OCR.]**
**[Figure 2 — "Generic torque ratio" — referenced in source but not visually extracted from this text-only OCR.]**

**Definitions:**
- `TP1000` = Pump reference torque: Raw OCR `TP1000 ¼ TP Ü Í 1 000 rpm / np Î 2` → Reconstructed: **TP1000 = TP × (1000 rpm / np)²** [Nm]
- `v` = Speed ratio: **v = n2/n1** [-]
- `μ` = Torque ratio: **μ = T2/T1** [-]
- `vs` = Speed ratio at overrun point: **vs = n2/n1** [-]. For TC with rotating housing (Trilock-type), vs is typically **1**. For other TC concepts (especially power-split), vs may differ from 1.
- `vc` = Speed ratio at coupling point: **vc = n2/n1** [-]
- `v0` = Stall point: **v0 = 0** [rpm]
- `vm` = Intermediate speed ratio: **vm = n2/n1** [-]

### Generic torque capacity — model definitions
**Stall point:**
- At **70 %** of nominal engine speed.
- Engine torque at stall point = **80 %** of maximum engine torque.
- Engine/pump reference torque at stall point:
  Raw OCR: `TP1000ðv0Þ ¼ Tmax Ü 0,80 Ü Í 1 000 rpm / 0,70 Ü nn Î2`
  Reconstructed: **TP1000(v0) = Tmax × 0,80 × (1000 rpm / (0,70 × nn))²**

**Intermediate point:**
- `vm = 0,6 × vs`
- Reference torque = **80 %** of stall-point reference torque: **TP1000(vm) = 0,8 × TP1000(v0)**

**Coupling point:**
- `vc = 0,90 × vs` (90% of overrun conditions)
- Reference torque = **50 %** of stall-point reference torque: **TP1000(vc) = 0,5 × TP1000(v0)**

**Overrun point:**
- At v = vs: **TP1000(vs) = 0**

### Generic torque ratio — model definitions
▼M4
**Stall point** (v0 = 0):
**μ(v0) = 1,8 / vs**

▼B
**Intermediate point**: linear interpolation between stall point and coupling point.

**Coupling point** (vc = 0,9 × vs):
**μ(vc) = 0,95 / vs**

**Overrun point** (v = vs):
**μ(vs) = 0,95 / vs**

**Efficiency**: **η = μ × v**

Linear interpolation between the calculated specific points is used throughout.

> Note the ▼M4 marker on the stall-point torque-ratio formula `μ(v0) = 1,8/vs` — this is one of the few numeric-value changes attributable to the 2025/258 amendment visible in this extraction (alongside the Case C ADC provision above). It is **not** itself EV-specific (it governs the generic conventional-TC model), but is flagged since it is part of the same amending Regulation that introduced the EV-relevant Case C.

---

## Appendix 10 — Standard (fallback) torque loss values: Other torque transferring components (retarders)

**For primary hydrodynamic retarders (oil or water) with included vehicle-launch functionality:**

Raw OCR: `Tretarder ¼ 20 / istepÄup þ Í 4 / ðistepÄupÞ 3 Î Ü Í nretarder / 1000 Î2`

Reconstructed: **Tretarder = (20/istep-up) + (4/(istep-up)³) × (nretarder/1000)²**

**For other hydrodynamic retarders (oil or water):**

Raw OCR: `Tretarder ¼ 10 / istepÄup þ Í 2 / ðistepÄupÞ 3 Î Ü Í nretarder / 1000 Î2`

Reconstructed: **Tretarder = (10/istep-up) + (2/(istep-up)³) × (nretarder/1000)²**

**For magnetic retarders (permanent or electro-magnetic):**

Raw OCR: `Tretarder ¼ 12 / istepÄup þ Í 5 / ðistepÄupÞ 4 Î Ü Ínretarder / 1000 Î2`

Reconstructed: **Tretarder = (12/istep-up) + (5/(istep-up)⁴) × (nretarder/1000)²**

**Variables:** `Tretarder` = Retarder drag loss [Nm]; `nretarder` = Retarder rotor speed [rpm] (per Table 2, §5.1 above); `istep-up` = Step-up ratio = retarder rotor speed / drive component speed (per §5.1 above).

*(Note the exponent on the step-up-ratio term differs by retarder type: cubed for the two hydrodynamic formulas, fourth-power for the magnetic-retarder formula — reproduced exactly as extracted; this is a substantive difference in the regulation, not an OCR artifact, since the exponents "3" and "4" are both clearly legible in the source.)*

---

## Appendices 3, 4, 5 — Component-specific information documents (brief summary)

**Appendix 3 — Hydrodynamic torque converter (TC) information document.** General identification fields (0.1–0.10, same structure as the transmission document in Appendix 2 — see file `07a`). Part 1 "Essential characteristics of the (parent) TC and TC types within a family":
- **1.1** For TC **without** mechanical transmission (serial arrangement): outer/inner torus diameter, P/T/S arrangement in flow direction, torus width, oil type per test spec, blade design.
- **1.2** For TC **with** mechanical transmission (parallel arrangement): same items as 1.1, plus gear scheme/power flow in TC mode, bearing types, cooling/lubrication pump type, shift-element types, and oil level per drawing (central-axis reference).
- Attachment 1: method of measurement — TC with mechanical transmission (yes/no); TC as separate unit (yes/no).

**Appendix 4 — Other torque transferring components (OTTC) information document.** Same general-field structure. Part 1 "Specific OTTC information":
- **1.1** Hydrodynamic OTTC/retarder: outer torus diameter, torus width, blade design, operating fluid, OD−ID, blade count, fluid viscosity.
- **1.2** Magnetic OTTC/retarder: drum design (electro-magnetic or permanent-magnetic), outer rotor diameter, cooling-blade design, blade design, operating fluid, OD−ID, rotor count, cooling-blade/blade count, fluid viscosity, arm count.
- **1.3** Hydrodynamic-clutch OTTC: outer torus diameter, torus width, blade design, fluid viscosity, OD−ID, blade count.
- Attachment 1: method of measurement (with transmission / with engine / drive mechanism / direct — each yes/no); max test speed of OTTC main torque absorber (e.g. retarder rotor) [rpm].

**Appendix 5 — Additional driveline components (ADC) information document.** Same general-field structure. Part 1 "Specific ADC/angle drive information" (1.1–1.10): gear ratio & gearscheme; angle between input/output shaft; bearing types; number of teeth per gearwheel; single gear width; number of dynamic shaft seals; oil viscosity (±10%); tooth surface roughness; specified oil level (central-axis ref., per drawing spec); oil level tolerance (±1 mm).
- Attachment 1: method of measurement (with transmission / drive mechanism / direct — each yes/no); max test speed at ADC input [rpm].

> Note: these three appendices, as extracted, describe only the **conventional** hydrodynamic/magnetic/mechanical ADC categories (angle drives, retarders, torque converters) — none of Appendices 3–5's information-document fields explicitly reference the electric-machine belt connection (Case C) added by M4 in §6.1.3. This suggests either (a) Appendix 5's generic "ADC/angle drive information" fields are intended to be reused as-is for a Case C belt component (with the electric-machine-specific parameters — fT=0,08, max e-machine torque — captured via the Appendix 12 Table 6/Table 7 data schema rather than a new information-document field), or (b) Annex III Table 8 (not in this extraction range) introduces additional information-document content for Case C that sits outside Annex VI. This is a gap/ambiguity worth checking against Annex III directly if the project needs the complete Case C declaration/certification paperwork.

---

## Summary: EV/Hybrid-relevant content found in this Annex VI range

1. **§6.1.3, Case C (►M4, Reg 2025/258)** — the clearest, explicit EV provision: belt-connected electric machine system treated as a single-speed-ratio ADC, with `fT = 0,08` and `Tmax,in` = max available torque of the electric machine system, reported via Appendix 12 Table 7 (ADC/LossMap) using the Appendix 11 fallback formula. **This directly supports modelling the mechanical coupling loss of a belt-driven e-axle/e-motor auxiliary drive in a VECTO-aligned sizing tool.**
2. **Appendix 12, Table 1 — "IHPC Type 1"** transmission-type value (flagged in file `07b`) — plausibly hybrid/electric-powertrain-related, but **not defined within Annex VI**; needs verification elsewhere (Annex III or VECTO documentation) before being relied upon.
3. **Appendix 11** (single-speed-ratio component fallback formula) — generically applicable to any fixed-ratio gear stage, including (by this knowledge base's own inference, not stated in the Regulation) a single-speed EV reduction gear — distinct from Case C, which is specifically the *belt* connection case.
4. No other explicit references to batteries, electric machines, inverters, or EV-specific driveline topologies were found elsewhere in definitions (§2), the transmission-type definitions (SMT/AMT/DCT/APT/Case S/P/N), or the TC/OTTC sections — those remain written entirely in terms of conventional ICE-driveline hardware (friction clutches, torque converters, hydrodynamic/magnetic retarders).

## Ambiguities / OCR flags summary for this file
1. Formula-glyph substitutions (¼/Ä/Ü/Í…Î/ffiffiffi) — see `07b` header for the general convention; raw OCR and reconstruction given side-by-side above for every formula.
2. Figures 1 and 2 of Appendix 9 ("Generic torque capacity" / "Generic torque ratio") — referenced but not visually extracted.
3. §6.1.1.1 "Applicable speed range" — a heading with no distinct body text visible in the extraction before §6.1.2 begins; possibly truncated or merged into the preceding paragraph.
4. §4.2.7.2's ►M4 heading marker vs. the unmarked (▼B-consistent) body text beneath it — unclear exactly what the 2025/258 amendment changed in this specific clause from this text-only extraction; flagged for verification against the amending Regulation if precision is needed.
5. Appendices 3–5 do not visibly reference the Case C electric-machine belt scenario — flagged as a possible cross-reference gap to Annex III, Table 8 (outside this assigned range).
