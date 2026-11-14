# Annex VI — Verifying Transmission, Torque Converter, OTTC and ADC Data
## Part B: Transmission Loss-Measurement Procedures, Loss-Map Generation, Calculation Methods, Standard Values & Conformity Testing

**Source:** Commission Regulation (EU) 2017/2400, consolidated text CELEX **02017R2400**, consolidation date **01.01.2026**, version 007.001.
**Range covered in this file:** Annex VI §3.1 (Option 1 formulas & calculation), §3.1.1 (torque-dependent loss calculation), §3.1.6–3.1.8 (Option 1 test procedure/validation/uncertainty), §3.2 (Option 2), §3.3 (Option 3), §3.4 (complement of input files), §7–§8 (conformity of certified properties & production conformity testing), Appendix 8 (standard/fallback transmission loss values), Appendix 11 (standard loss values — angle drive / single-speed component), Appendix 12 (simulation-tool input parameters).
**Companion files:** `07a` (definitions & general test setup), `07c` (torque converter, OTTC, ADC — including the EV-relevant Case C provision).

**IMPORTANT OCR NOTE ON FORMULAS:** The source PDF's mathematical notation did not extract cleanly as plain text. Equals signs appear as "¼", minus/subtraction as "Ä", multiplication as "Ü", and groupings as "Í...Î"; square-root radicals are broken across lines (e.g. "ffiffiffi…p"). For every formula below, this file first gives the **raw OCR-extracted text exactly as it appears in the source** (clearly marked "Raw OCR:"), followed immediately by **a reconstructed, human-readable version** (clearly marked "Reconstructed:") that substitutes the standard mathematical symbols. The reconstruction is my interpretation of the garbled OCR glyphs for readability only — it does not change, round, or add to the legal content; if the raw OCR and reconstruction ever appear to diverge, the raw OCR (and ultimately the original PDF) governs.

---

## 3.1. Option 1: Measurement of the torque independent losses, calculation of the torque dependent losses

### Main torque-loss equation

Raw OCR:
`Tl,in(nin,Tin,gear) = Tl,in,min_loss + fT × Tin + floss_corr × Tin + Tl,in,min_el + fel_corr × Tin + flosstcc × Tin` ▼M3
(this line extracted cleanly, unlike the correction-factor formulas below)

**Variables:**
- `Tl,in` = Torque loss related to input shaft [Nm]
- `Tl,in,min_loss` = Torque independent loss at minimum hydraulic loss level (minimum main pressure, cooling/lubrication flows, etc.), measured with free rotating output shaft from testing without load [Nm]
- `nin` = Speed at the transmission input shaft (downstream of torque converter, if applicable) [rpm]
- `fT` = Torque loss coefficient = 1 − ηT
- `Tin` = Torque at the input shaft [Nm]
- `floss_corr` = Loss correction for hydraulic loss level depending on input torque [-]
- `Tl,in,min_el` = Additional torque loss on input shaft by electric consumers corresponding to minimum electric power [Nm]
- `fel_corr` = Loss correction for electric power loss level depending on input torque [-]
- ▼M3 `floss_tcc` = Loss correction factor for slipping torque converter (or input side) clutch

### Correction factor — torque-dependent hydraulic losses

Raw OCR: `f loss_corr ¼ ðTl;in;max_loss Ä Tl;in;min_lossÞ / Tmax;in`

Reconstructed: **floss_corr = (Tl,in,max_loss − Tl,in,min_loss) / Tmax,in**

where `Tl,in,max_loss` = Torque independent loss at **maximum** hydraulic loss level (maximum main pressure, cooling/lubrication flows etc.), measured with free rotating output shaft from testing without load [Nm]; `Tmax,in` = Maximum allowed input torque for any forward gear in the transmission [Nm].

### Correction factor — torque-dependent electric losses

Raw OCR: `f el_corr ¼ ðTl;in;max_el Ä Tl;in;min_elÞ / Tmax;in`

Reconstructed: **fel_corr = (Tl,in,max_el − Tl,in,min_el) / Tmax,in**

where `Tl,in,max_el` = Additional torque loss on input shaft by electric consumers corresponding to **maximum** electric power [Nm].

### Electric-auxiliary torque loss

Raw OCR: `Tl;in;el ¼ Pel Í 0,7 Ü nin Ü 2π / 60 Î`

Reconstructed: **Tl,in,el = Pel / (0,7 × nin × 2π / 60)**

where `Pel` = Electric power consumption of electric consumers in transmission measured during transmission loss testing [W]. (Note: this expresses Tl,in,el as electrical power divided by an angular-speed-like term derived from nin and a 0,7 factor; the 0,7 factor's basis is not stated in the extracted text, and no further explanation appears in this annex — flagged as a figure/derivation not elaborated in the source text available.)

### ▼M3 Correction factor — slipping TC lock-up clutch / slipping input-side clutch

Raw OCR: `f losstcc ¼ Δntcc / nin`

Reconstructed: **floss_tcc = Δntcc / nin**

where `Δntcc` = Difference in speed between upstream and downstream side of slipping TC lock-up clutch (def. 2(16)) or slipping input side clutch (def. 2(20)) [rpm] (speed downstream of the slipping clutch is the speed `nin` at the transmission input shaft); `ηT` = Torque dependent efficiency (to be calculated); **for a direct gear, fT = 0,007 (ηT = 0,993)**.

---

## 3.1.1. Torque-dependent losses — calculation method

In cases of multiple parallel, nominally equal power flows (e.g. twin countershafts, several planet gearwheels in a planetary set), these can be treated as **one** power flow in this section.

### 3.1.1.1–3.1.1.6. Common (non-split, non-planetary) transmissions

For each indirect gear `g` of common transmissions with a non-split power flow and ordinary, non-planetary gear sets:

**3.1.1.2.** For each active gear mesh, torque-dependent efficiency `ηm` is set to fixed constants:
| Mesh type | ηm |
|---|---|
| External–external gear mesh | **0,986** |
| External–internal gear mesh | **0,993** |
| Angle drive gear mesh | **0,97** (may alternatively be determined by separate testing per §6 of this Annex) |

**3.1.1.3.** The product of these mesh efficiencies is multiplied by a torque-dependent bearing efficiency **ηb = 99,5 %**.

**3.1.1.4.** Total torque-dependent efficiency for gear g:
`ηTg = ηb × ηm,1 × ηm,2 × […] × ηm,n`

**3.1.1.5.** Torque-dependent loss coefficient for gear g:
`fTg = 1 − ηTg`

**3.1.1.6.** Torque-dependent loss on input shaft for gear g:
`Tl,inTg = fTg × Tin`

### 3.1.1.7. Special case — countershaft main section + planetary range section (non-rotating ring, planet carrier → output)

Raw OCR: `ηlowrange ¼ 1 þ ηm;ring Ü ηm;sun Ü zring / zsun / 1 þ zring / zsun`

Reconstructed (as a two-level fraction):

**ηlowrange = [1 + ηm,ring × ηm,sun × (zring/zsun)] / [1 + (zring/zsun)]**

where `ηm,ring` = torque-dependent efficiency of ring-to-planet gear mesh = **99,3 %**; `ηm,sun` = torque-dependent efficiency of planet-to-sun gear mesh = **98,6 %**; `zsun` = number of teeth of the sun gearwheel of the range section; `zring` = number of teeth of the ring gearwheel of the range section.

The planetary range section is treated as an additional gear mesh within the countershaft main section, and `ηlowrange` is included in the total `ηTg` (3.1.1.4.) for the low-range gears.

### 3.1.1.8–3.1.1.14. General method (complex split power flows / planetary gear sets)

For transmission types with more complex split power flows and/or planetary gear sets (e.g. conventional automatic planetary transmission), a simplified method applies — covering ordinary non-planetary gear sets and/or ring-planet-sun planetary gear sets. **Alternatively**, torque-dependent efficiency may be calculated per **VDI Regulation No. 2157** (both approaches must use the same constant gear-mesh-efficiency values from 3.1.1.2.).

Steps, per indirect gear g:

**3.1.1.9.** Assuming 1 rad/s input speed and 1 Nm input torque, build a table of speed (N) and torque (T) values for every gearwheel with a fixed rotational axis (sun, ring, ordinary gearwheels) and planet carriers. Speed/torque follow the right-hand rule, engine rotation = positive direction.

**3.1.1.10.** For each planetary gear set, relative speeds:
`Nsun–carrier = Nsun − Ncarrier`
`Nring–carrier = Nring − Ncarrier`
(Nsun, Nring, Ncarrier = rotational speeds [rad/s] of sun gearwheel, ring gearwheel, carrier respectively.)

**3.1.1.11.** Loss-producing powers in gear meshes:
- Ordinary non-planetary gear set: `P1 = N1 · T1`, `P2 = N2 · T2` (P = power [W], N = rotational speed [rad/s], T = torque [Nm])
- Planetary gear set — **virtual power** of sun/ring:
  `Pv,sun = Tsun · (Nsun − Ncarrier) = Tsun · Nsun/carrier`
  `Pv,ring = Tring · (Nring − Ncarrier) = Tring · Nring/carrier`
  Negative virtual power = power leaving the gear set; positive = power going into the gear set.

**Loss-adjusted powers Padj:**
- Ordinary non-planetary: `Pi > 0 ⇒ Pi,adj = Pi`; `Pi < 0 ⇒ Pi,adj = Pi · ηmi` (ηm = appropriate mesh efficiency from 3.1.1.2.)
- Planetary: `Pv,i ≥ 0 ⇒ Pi,adj = Pv,i`; `Pv,i < 0 ⇒ Pi,adj = Pi · ηmsun · ηmring`

**3.1.1.12.** Sum all loss-adjusted power values → torque-dependent gear-mesh power loss referring to input power:
`Pm,loss = Σ Pi,adj` (i = all gearwheels with a fixed rotational axis)

**3.1.1.13.** Torque-dependent bearing loss coefficient:
`fT,bear = 1 − ηbear = 1 − 0,995 = 0,005`

Torque-dependent gear-mesh loss coefficient (raw OCR: `f T;gearmesh ¼ Pm;loss / Pin ¼ Pm;loss Í 1 Nm Ü 1 rad / s Î`):

Reconstructed: **fT,gearmesh = Pm,loss / Pin**, where Pin (fixed input power) = 1 Nm × 1 rad/s [W].

Total torque-dependent loss coefficient: **fT = fT,gearmesh + fT,bear**

**3.1.1.14.** Torque-dependent loss on input shaft for the specific gear:
**Tl,inT = fT × Tin**

---

## 3.1.2. Torque independent losses — measured per §3.1.2.1–3.1.2.5 (procedure reproduced in full in file `07a`, since those provisions are shared across Options 1–3).

---

## 3.1.6. Test procedure (Option 1)

**3.1.6.1. Zero torque signal compensation**: sensor zero-signal measured with sensor installed in rig, drivetrain (input & output) free of load; measured deviation from zero is compensated.

**▼M3 3.1.6.2. Speed points**: torque loss measured at **600, 900, 1200, 1600, 2000, 2500, 3000, 4000 rpm** and multiples of 10 of these values up to the maximum speed per gear (per transmission spec) or the last speed point before the defined maximum speed. Additional intermediate points permitted. **Speed ramp ≤ 20 seconds.**

**▼B 3.1.6.3. Measurement sequence**
- 3.1.6.3.1. If equipped with smart lubrication systems and/or transmission electric auxiliaries: **two** measurement sequences — (a) lowest power consumption setting ("low loss level"), (b) highest possible power consumption setting ("high loss level").
- 3.1.6.3.2. Measurements performed lowest → highest speed.
- ►M3 3.1.6.3.3. Minimum **5-second** stabilisation time per speed point within the temperature limits of 3.1.2.5; extendable to max **60 seconds** by the manufacturer. Oil/ambient temps recorded during stabilisation. ◄
- ▼M3 3.1.6.3.4. After stabilisation, if torque loss is constant over time at the measured point: record signals (3.1.5.) for **min. 5 s, max. 15 s**. If not constant (e.g. intended periodic variation from active/passive control): manufacturer uses the testing time needed for a reproducible, representative result.
- ▼B 3.1.6.3.5. Each measurement performed **two times** per measurement setting.

## 3.1.7. Measurement validation (Option 1)

- ▼M3 3.1.7.1. Arithmetic mean values calculated for torque, speed, (if applicable) voltage and current for each measurement (min 5 s / max 15 s, or longer if needed per 3.1.6.3.4. logic).
- ▼B 3.1.7.2. Averaged speed deviation < **± 5 rpm** of the set point for each measured point across the complete series.
- 3.1.7.3. Mechanical torque loss / electrical power consumption calculated per measurement:
  ▼M3 **Tloss = Tl,in(nin, Tin, gear)** [i.e., the main equation above]
  ▼B **Pel = I × U**
  (Subtraction of test-rig-setup influences per 3.1.2.2. is allowed.)
- 3.1.7.4. Mechanical torque losses and electrical power consumption from the two measurement sets averaged (arithmetic mean).
- 3.1.7.5. Deviation between the two averaged torque-loss measurements < **± 5 % of average or ± 1 Nm**, whichever larger → arithmetic average of the two taken.
- 3.1.7.6. If deviation higher: take the **largest** averaged torque-loss value, or repeat the test for that gear.
- 3.1.7.7. Deviation between the two averaged electric power (V×I) measurements < **± 10 % of average or ± 5 W**, whichever larger → average taken.
- 3.1.7.8. If deviation higher: take the set of V/I values giving the **largest** averaged power, or repeat the test for that gear.

## 3.1.8. Measurement uncertainty (Option 1)

Reported torque loss:

Raw OCR: `Tloss,rep = Tloss + MAX (0, (UT,loss – 0,3 Nm))`

**Tloss,rep = Tloss + MAX(0, (UT,loss − 0,3 Nm))** — only the part of total uncertainty UT,loss exceeding 0,3 Nm is added. If UT,loss < 0,3 Nm, Tloss,rep = Tloss.

Total uncertainty based on: (1) Temperature effect; (2) Parasitic loads; (3) Calibration error (sensitivity tolerance, linearity, hysteresis, repeatability) — combined at **95 % confidence level** via "Gaussian law of error propagation" (root-sum-of-squares):

Raw OCR:
```
UT;loss ¼ UT;in ¼ 2 Ü ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi u2 TKC þ u2 TK0 þ u2 cal þ u2 para q
uTKC ¼ 1 ffiffiffi 3 p Ü wtkc / Kref Ü ΔK Ü Tc
uTK0 ¼ 1 ffiffiffi 3 p Ü wtk0 / Kref Ü ΔK Ü Tn
uCal ¼ 1 Ü Wcal / kcal Ü Tn
upara ¼ 1 ffiffiffi 3 p Ü wpara Ü Tn
wpara = senspara * ipara
```

Reconstructed:
- **UT,loss = UT,in = 2 × √(u²TKC + u²TK0 + u²cal + u²para)**
- **uTKC = (1/√3) × (wtkc / Kref) × ΔK × Tc**
- **uTK0 = (1/√3) × (wtk0 / Kref) × ΔK × Tn**
- **ucal = 1 × (Wcal / kcal) × Tn**  *(the leading "1 ×" in the raw OCR is ambiguous; shown as extracted)*
- **upara = (1/√3) × wpara × Tn**
- **wpara = senspara × ipara**

**Variables:**
- `Tloss` = Measured torque loss (uncorrected) [Nm]; `Tloss,rep` = Reported torque loss (after uncertainty correction) [Nm]
- `UT,loss` = Total expanded uncertainty of torque loss measurement at 95% confidence [Nm]; `UT,in` = Uncertainty of input torque loss measurement [Nm]
- `uTKC` = Uncertainty by temperature influence on current torque signal [Nm]; `wtkc` = Temperature influence on current torque signal per Kref, declared by sensor manufacturer [%]
- `uTK0` = Uncertainty by temperature influence on zero torque signal (related to nominal torque) [Nm]; `wtk0` = same, per Kref [%]
- `Kref` = Reference temperature span for uTKC/uTK0, wtk0/wtkc, declared by sensor manufacturer [K]
- `ΔK` = Difference in sensor temperature between calibration and measurement [K]. **If sensor temperature cannot be measured, default ΔK = 15 K.**
- `Tc` = Current/measured torque value at torque sensor [Nm]; `Tn` = Nominal torque value of torque sensor [Nm]
- `ucal` = Uncertainty by torque sensor calibration [Nm]; `Wcal` = Relative calibration uncertainty (related to nominal torque) [%]; `kcal` = Calibration advancement factor (declared by manufacturer, otherwise = 1)
- `upara` = Uncertainty by parasitic loads [Nm]; `wpara` = senspara × ipara = relative influence of forces/bending torques from misalignment
- `senspara` = Max influence of parasitic loads for the specific torque sensor, declared by manufacturer [%]; **if not declared, set to 1,0 %**
- `ipara` = Max influence of parasitic loads for the specific torque sensor, depending on test setup A/B/C:
  - **A) 10 %** — bearings isolate parasitic forces front/behind the sensor + flexible coupling (or cardan shaft) installed functionally next to the sensor (up/downstream); bearings may be integrated in the driving/braking machine and/or transmission as long as forces are isolated from the sensor. **[Figure 1 — "Example of test setup A for Option 1" — referenced in source but not visually extracted from this text-only OCR.]**
  - **B) 50 %** — bearings isolate parasitic forces front/behind the sensor but **no** flexible coupling installed next to the sensor (same bearing-integration allowance as A). **[Figure 2 — "Example of test setup B for Option 1" — referenced in source but not visually extracted from this text-only OCR.]**
  - **C) 100 %** — for other setups.

  ▼M3 For a transmission with integrated differential (front-wheel drive), the test setup needs a dynamometer on the input side and at least one on the output side(s), with torque measuring devices on input and output side(s). With only one output-side dynamometer, the free rotating end is rotatably locked to the other output end (e.g. activated differential lock or other mechanical lock implemented only for measurement). The A/B/C ipara graduation applies the same way. **[Figure 2A — "Example of test setup A for Option 1 for a transmission with integrated differential" — referenced but not visually extracted.] [Figure 2B — equivalent for setup B — referenced but not visually extracted.]**

  The manufacturer may adapt setups A/B per good engineering judgement with Approval Authority agreement (practical test-setup reasons); the reason and alternative setup must be documented in the test report.

  It is allowed to test **without** a separate bearing unit at the transmission input/output on the rig, if the transmission shaft being measured is supported by two bearings in the transmission housing able to absorb radial and axial gearset forces. **[Figure 2C — "Example where the forces in the transmission are isolated and not isolated from the input" — referenced but not visually extracted.]**

---

## 3.2. Option 2: Measured torque-independent losses + measured torque loss at maximum torque, linear interpolation for the rest

Main equation (▼M3):

**Tl,in(nin,Tin,gear) = Tl,in,min_loss + fTlimo × Tin + Tl,in,min_el + fel_corr × Tin + floss_tcc × Tin**

Torque loss coefficient based on the linear model:

Raw OCR: `f Tlimo ¼ Tl;maxT Ä Tl;in;min_loss / Tin;maxT`

Reconstructed: **fTlimo = (Tl,maxT − Tl,in,min_loss) / Tin,maxT**

**Variables (▼M3):**
- `Tl,in,min_loss` = Drag torque loss at transmission input, measured with free rotating output shaft, from testing without load [Nm]
- `nin` = Speed at the input shaft [rpm]
- `fTlimo` = Torque loss coefficient based on linear model [-]
- `Tin,maxT` = Maximum **tested** torque at the input shaft (normally 100% input torque; see 3.2.5.2. and 3.4.4.) [Nm]
- `Tl,maxT` = Torque loss related to input shaft with Tin = Tin,maxT
- `fel_corr`, `Tl,in,el`, `Tl,in,min_el`: as for Option 1
- `floss_tcc`: calculated as described in §3.1 (Option 1)

### 3.2.1–3.2.4. Cross-references
General requirements / differential measurements / run-in: as Option 1 (3.1.2.1.–3.1.2.3.). Pre-conditioning: as Option 3 (3.3.2.1.). Test conditions (ambient/oil temp, oil quality/viscosity): as Option 1. Oil level/conditioning: as Option 3 (3.3.3.4.). Installation: torque-independent-loss part as Option 1 (3.1.3.); torque-dependent-loss part as Option 3 (3.3.4.). Measurement equipment: torque-independent as Option 1 (3.1.4.); torque-dependent as Option 3 (3.3.5.). Signals/recording: torque-independent as Option 1 (3.1.5.); torque-dependent as Option 3 (3.3.7.).

### 3.2.5. Test procedure
The torque loss map applied to the simulation tool contains torque-loss values vs. rotational input speed and input torque; the basic data is measured/calculated per this paragraph, then completed per §3.4 and formatted per Appendix 12.

- 3.2.5.1. Torque-independent losses determined per 3.1.1 (Option 1 procedure), but **only for the low loss level setting** of electric/hydraulic consumers.
- 3.2.5.2. Torque-dependent losses for each gear determined using the Option 3 procedure (3.3.6.), but over a different torque range: **measured at 100 % of the maximum transmission input torque per gear.** If output torque exceeds **10 kNm** (for a theoretical loss-free transmission) or input power exceeds the specified maximum input power, §3.4.4. applies.

### 3.2.6–3.2.7. Validation / uncertainty: per Option 3 (3.3.8.) for validation; torque-independent-loss uncertainty per Option 1 (3.1.8.), torque-dependent-loss uncertainty per Option 3 (3.3.9.).

---

## 3.3. Option 3: Measurement of the total torque loss

### 3.3.1–3.3.3. Cross-references
General requirements, differential measurements, run-in: as Option 1.
**3.3.2.1. Pre-conditioning** (exception to Option 1's 3.1.2.4.): performed on the **direct drive gear** without applied torque to the output shaft, or with target output-shaft torque = 0; if no direct drive gear, use the gear with ratio closest to 1:1. *(Alternative, equally valid per the source text:* output-shaft torque within **±50 Nm**; or, if the rig has a master friction clutch at the input shaft, no applied torque to the **input** shaft, with the transmission then driven from the output side. These alternatives may be combined.)
**3.3.3.1–3.3.3.3.** Ambient temp / oil temp / oil quality-viscosity: as Option 1.
**3.3.3.4. Oil level/conditioning**: as Option 1 (3.1.2.5.5.) except the conditioning-system test point is specified as: (1) highest indirect gear; ▼M3 (2) input speed = min 60%, not higher than 80% of max input speed; ▼B (3) input torque = maximum input torque for the highest indirect gear.

### 3.3.4. Installation
Test rig driven by electric machines (input **and** output). ▼M3 Torque sensors installed at **both** input and output side(s) of the transmission. ▼B Other requirements as Option 1 (3.1.3.).

### 3.3.5. Measurement equipment
Torque-independent-loss measurement: per Option 1 (3.1.4.).
**Torque-dependent-loss measurement:** torque sensor uncertainty < **5 % of measured torque loss, or 1 Nm**, whichever is larger. Higher-uncertainty sensors allowed if the excess (over the smaller of the two bounds) is calculated and added per 3.3.9. All other equipment requirements as Option 1.

### 3.3.6. Test procedure
**3.3.6.1.** Zero torque signal compensation: as 3.1.6.1.
**▼M3 3.3.6.2. Speed range**: same speed points as Option 1 (600/900/1200/1600/2000/2500/3000/4000 rpm + multiples of 10 up to max speed per gear or last point below max). Speed ramp ≤ 20 s.
**3.3.6.3. Torque range**: for each speed point, torque loss measured at: **0 (free rotating output shaft), 200, 400, 600, 900, 1200, 1600, 2000, 2500, 3000, 3500, 4000, […] Nm**, up to the maximum input torque per gear (per transmission spec) or the last torque point below the defined max and/or before output torque reaches **10 kNm**. Additional intermediate points permitted; if the torque range is too small, additional points required so that **at least 5 equally spaced torque points** are measured (intermediate points may be rounded to the nearest multiple of 50 Nm). If output torque > 10 kNm or input power > specified max input power, §3.4.4. applies. **Torque ramp ≤ 15 seconds (180 seconds for Option 2).** Different torque sensors with limited ranges may be used on input/output to cover the full torque range, measured in sections using the same sensor set; the overall loss map is composed of these sections.
**3.3.6.4. Measurement sequence**: lowest → highest speed (3.3.6.4.1.); ▼M3 input torque varied low → high, within what the current torque sensors cover, for each speed point (3.3.6.4.2.); ►M3 min 5-second stabilisation per speed/torque point within 3.3.3 temperature limits, extendable to max 60 s (max 180 s for Option 2) ◄ (3.3.6.4.3.); ▼M3 after stabilisation, if torque loss constant, record signals (3.3.7.) for min 5 s / max 15 s, else use testing time needed for reproducible/representative result (3.3.6.4.3.1.); ▼B measurement set performed **two times total**, with sequenced repetition of sections using the same sensor set allowed (3.3.6.4.4.).

### 3.3.7. Measurement signals and data recording
At least: (1) Input **and output** torques [Nm]; (2) Input **and output** rotational speeds [rpm]; (3) Ambient temperature [°C]; (4) Oil temperature [°C]. ▼M3 Plus, where applicable: (5) Oil pressure [kPa] (hydraulic shift/clutch or mechanically-driven smart lubrication); (6)-(7) Voltage/current of transmission electric auxiliary [V]/[A]; (8) Test rig bearing temperature [°C] (differential measurements). Sampling ≥ 100 Hz; low-pass filter applied.

### 3.3.8. Measurement validation
- ▼M3 3.3.8.1. Arithmetic mean of torque, speed, (if applicable) voltage/current for min 5 s / max 15 s, per measurement; longer if torque loss not constant (as above).
- ▼B 3.3.8.2. Averaged input-shaft speed < ±5 rpm of set point. ►M1 Averaged input-shaft torque < ±5 Nm or ± ►M3 1,0 % ◄ of the torque set point, whichever is larger. ◄
- ▼M3 3.3.8.3. Mechanical torque loss / electric power consumption calculated per measurement:

  Raw OCR: `Tloss ¼ Tin Ü ð1 þ f losstcc Þ Ä Tout / igear þ I Ü U / ð0,7 Ü nin Ü 2π / 60Þ`

  Reconstructed: **Tloss = [Tin × (1 + floss_tcc) − Tout/igear] + [I×U / (0,7 × nin × 2π/60)]**

  For a transmission with **integrated differential** and a dynamometer on **each** output shaft:

  Raw OCR: `Tloss ¼ Tin Ü ð1 þ f losstcc Þ Ä Tout_1 / igear Ä Tout_2 / igear þ I Ü U / ð0,7 Ü nin Ü 2π / 60Þ`

  Reconstructed: **Tloss = [Tin × (1 + floss_tcc) − Tout_1/igear − Tout_2/igear] + [I×U / (0,7 × nin × 2π/60)]**

  (floss_tcc calculated per §3.1, as for Option 1. Subtraction of test-rig influences per 3.1.2.2. allowed.)
- ▼B 3.3.8.4. Mechanical torque losses / electrical power from the two sets averaged (arithmetic mean).
- 3.3.8.5. Deviation between the two averaged torque losses < **±5% of average or ±1 Nm**, whichever larger → average taken; if higher, take the largest value or repeat the test.
- 3.3.8.6–3.3.8.7. Deviation between the two averaged electric power values < **±10% of average or ±5 W**, whichever larger → average taken; if higher, take the set giving the largest power, or repeat.

### 3.3.9. Measurement uncertainty (Option 3)

Raw OCR: `Tloss,rep = Tloss + MAX (0, ΔUT,loss)` ; `ΔUT,loss = MIN ((UT,loss – 5 % * Tloss), (UT,loss – 1 Nm))`

**Tloss,rep = Tloss + MAX(0, ΔUT,loss)**, **ΔUT,loss = MIN((UT,loss − 5%×Tloss), (UT,loss − 1 Nm))** — i.e., only the part of UT,loss exceeding 5% of Tloss or 1 Nm (whichever of those two thresholds is **smaller**) is added.

Based on same 3 parameters (temperature effect, parasitic loads, calibration error) at 95% confidence:

Raw OCR:
```
UT;loss ¼ ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi UT;in2 þ Í UT;out / igear Î2 s
UT;in=out ¼ 2 Ü ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi u2 TKC þ u2 TK0 þ u2 cal þ u2 para q
```
(followed by the same uTKC/uTK0/ucal/upara/wpara formulas as Option 1, §3.1.8.)

Reconstructed:
- **UT,loss = √(UT,in² + (UT,out/igear)²)**
- **UT,in/out = 2 × √(u²TKC + u²TK0 + u²cal + u²para)** (computed separately for input and output torque sensor)
- uTKC, uTK0, ucal, upara, wpara: identical formulas to §3.1.8 above.

**Additional/changed variables vs. 3.1.8:** `uT,in/out` = uncertainty of input/output torque loss measurement, separately for input and output sensor [Nm]; `igear` = gear ratio [-].

**Test setup A/B/C for Option 3** (ipara graduation identical in meaning to Option 1's, but illustrated with different figures):
- A) 10% — **[Figure 3 — "Example of test setup A for Option 3" — referenced but not visually extracted.]**
- B) 50% — **[Figure 4 — "Example of test setup B for Option 3" — referenced but not visually extracted.]**
- C) 100% — other setups.
- ▼M3 Integrated-differential test setup (front-wheel drive): dynamometer on input side + at least one on output side(s), torque devices on input/output; single-output-dynamometer configs lock the free output end to the other (as in Option 1). **[Figure 5 — "Example of test setup A for a transmission with integrated differential" — referenced but not visually extracted.] [Figure 6 — equivalent for setup B — referenced but not visually extracted.]**

  ▼M3 For a dynamometer on **each** output shaft:

  Raw OCR: `UT;loss ¼ ffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffiffi UT;in2 þ Í UT;out1 / igear Î2 þ Í UT;out2 / igear Î2 s`

  Reconstructed: **UT,loss = √(UT,in² + (UT,out1/igear)² + (UT,out2/igear)²)**

  Manufacturer may adapt setups A/B per good engineering judgement with Approval Authority agreement (documented in test report). Testing without a separate bearing unit at transmission input/output is allowed under the same condition as Option 1 (shaft supported by two bearings in the transmission housing absorbing radial/axial gearset forces — see Figure 2C).

---

## 3.4. Complement of input files for the simulation tool

►M3 For each gear, a torque loss map covering the defined input speed/torque points shall be determined with one of the specified testing options or standard torque loss values. ◄ The basic loss map is then completed as follows:

- **3.4.1.** ►M3 Where the highest tested input speed is the last point below the defined max permissible transmission speed: extrapolate the torque loss up to max speed via **linear regression based on the two last measured speed points**. ◄
- **3.4.2.** ►M3 Same logic for input torque: extrapolate up to max torque via linear regression on the two last measured torque points for the corresponding speed point. ◄ To handle engine torque tolerances etc., the simulation tool will, if required, further extrapolate torque loss up to **10% above** the defined maximum permissible transmission torque.
- **3.4.3.** If both max-speed and max-torque extrapolation apply simultaneously, the combined point's torque loss is calculated via **two-dimensional linear extrapolation**.
- **3.4.4.** If max output torque exceeds **10 kNm** (theoretical loss-free transmission) and/or for speed/torque points with input power above the specified max input power, the manufacturer may take torque-loss values for all such points from one of: ▼M3 (1) Calculated fallback values (**Appendix 8**); (2) Option 1; (3) Option 2 or 3 combined with a torque sensor for higher output torques (if required). For cases (1)/(2), torque losses at load are measured at the input torque corresponding to output torque = 10 kNm and/or the specified max input power.
- **▼M3 3.4.5.** For speeds below the defined minimum speed, and the additional input speed step of **0 rpm**, copy the reported torque losses from the minimum speed point.
- **▼B 3.4.6.** To cover negative input torque during vehicle coasting, copy the positive-input-torque loss values to the corresponding negative input torques.
- **3.4.7.** With approval-authority agreement, torque losses for input speeds below **1000 rpm** may be replaced by the 1000 rpm losses when measurement is technically not possible.
- **▼M3 3.4.8.** If measuring certain speed points is technically impossible (e.g. due to natural frequency), the manufacturer may, with Approval Authority agreement, **calculate** torque losses by interpolation/extrapolation — limited to **max. 1 speed point per gear**.
- **▼B 3.4.9.** The torque loss map data shall be formatted/saved per **Appendix 12**.

---

## 7. Conformity of the certified CO2 emissions and fuel consumption related properties

▼M3
- **7.1.** Every transmission/TC/OTTC/ADC must be manufactured to conform to the approved type per the certificate/annexes. ►M3 Conformity procedures comply with the conformity-of-production arrangements in **Article 31 of Regulation (EU) 2018/858**. ◄
- **7.2.** TC, OTTC and ADC are **excluded** from the production-conformity testing provisions of §8.
- **7.3.** Conformity is checked against the description in the Appendix 1 certificates.
- **7.4.** Conformity assessed per the specific conditions in this paragraph.
- **7.5.** The manufacturer shall test **annually at least the number of transmissions** in Table 3, based on total annual production (only transmissions falling under this Regulation count).
- **7.6.** Each tested transmission must be representative of a specific family. ►M4 Only **one** transmission per family shall be tested. ◄
- **7.7.** For annual production 1 001–10 000: family choice for testing agreed between manufacturer and approval authority.
- **7.8.** For annual production > 10 000: the family with the **highest production volume** is always tested; manufacturer justifies (e.g. via sales numbers) the number of tests and family choices to the approval authority; remaining families agreed with the approval authority.

**Table 3 — Sample size for conformity testing:**
| Total annual production of transmissions | Number of tests |
|---|---|
| 0 – 1 000 | 0 |
| > 1 000 – 10 000 | 1 |
| > 10 000 – 30 000 | 2 |
| > 30 000 | 3 |
| > 100 000 | 4 |

- **▼B 7.9.** Approval authority identifies, together with the manufacturer, the transmission type(s) to test, ensuring the selected type(s) is manufactured to the same standard as serial production.
- **7.10.** ►M4 Notwithstanding 7.6, if a test under §8 result is **higher** than specified in §8.1.3., **three additional transmissions** from the same family shall be tested. ◄ If at least one of those fails, Article 23 provisions apply.

## 8. Production conformity testing

Applied upon prior agreement between approval authority and applicant.

### 8.1. Conformity testing of transmissions
- **8.1.1.** Transmission efficiency determined via the **simplified procedure** in this paragraph.
- **8.1.2.1.** All boundary conditions from certification testing apply. If different oil type/temperature/inclination-angle conditions are used, the manufacturer must clearly show the influence of these vs. the certification conditions regarding efficiency.
- **8.1.2.2.** Same testing option as certification testing, limited to the operating points below.
  - ▼M3 8.1.2.2.1. If **Option 1** was used for certification: measure torque-independent losses at the two speeds (below) and use them to calculate torque losses at the three torque points (below). If **Option 2**: measure torque-independent losses at the two speeds; measure torque-dependent losses at max torque at those same two speeds; interpolate the three torque points as per the certification procedure. If **Option 3**: measure torque losses directly for all 18 operating points.
  - ▼B 8.1.2.2.2. 18 operating points defined by:
    1. **Gears**: the **3 highest gears** of the transmission.
    2. ▼M3 **Torque range**: if Option 1/2 was used for certification — three points: **0,6 × max(Tin,rep)**, **0,8 × max(Tin,rep)**, **max(Tin,rep)** (at the given input speed/gear, where max(Tin,rep(inputspeed,gear)) is the largest input torque value reported for certification for that combination). If Option 3 — the **3 highest torque points** actually measured at certification for that input-speed/gear combination.
    3. ▼B **Speed range**: **1200 rpm and 1600 rpm**.
- **▼M3 8.1.2.3.** Efficiency per operating point:

  Raw OCR: `ηi ¼ Tin;set Ä Tloss;rep / Tin;set`

  Reconstructed: **ηi = (Tin,set − Tloss,rep) / Tin,set**

  (`ηi` = efficiency of operating point 1–18; `Tin,set` = input torque set point [Nm]; `Tloss,rep` = reported torque loss after uncertainty correction [Nm].)
- **▼B 8.1.2.4.** Total conformity-test efficiency = arithmetic mean of all 18 operating-point efficiencies:

  Raw OCR: `ηA;CoP ¼ η1 þ η2 þ ½…â þ η18 / 18`

  Reconstructed: **ηA,CoP = (η1 + η2 + … + η18) / 18**

- **8.1.3.** Pass condition: conformity-test efficiency ηA,CoP shall not be lower than X% of the type-approved efficiency ηA,TA:

  **ηA,TA − ηA,CoP ≤ X**

  ▼M1 **X = 1,5 %** for SMT/AMT/DCT transmissions; **X = 3 %** for APT transmissions or transmissions with more than 2 friction shift clutches.

  ▼M3 ηA,TA calculated as the arithmetic mean of the 18 certification operating-point efficiencies, using the same 8.1.2.3./8.1.2.4. formulas and the 8.1.2.2.2. requirements.

---

## Appendix 8 — Standard (fallback) torque loss values: Transmission

Calculated fallback values, based on the transmission's maximum rated torque:

Raw OCR: `Tl;in ¼ ðTd0 þ Tadd0Þ þ ðTd1000 þ Tadd1000Þ Ü nin / 1 000 rpm þ ðf T þ f T_add Þ Ü Tin`

Reconstructed: **Tl,in = (Td0 + Tadd0) + (Td1000 + Tadd1000) × (nin / 1000 rpm) + (fT + fT_add) × Tin**

**Variables:**
- `Tl,in` = Torque loss related to the input shaft [Nm]
- `Tdx` = Drag torque at x rpm [Nm]
- `Taddx` = Additional angle-drive-gear drag torque at x rpm [Nm] (if applicable)
- `nin` = Speed at the input shaft [rpm]
- `fT` = 1 − η (η = efficiency); **fT = 0,01 for direct gear, 0,04 for indirect gears**
- `fT_add` = **0,04** for angle drive gear (if applicable)
- `Tin` = Torque at the input shaft [Nm]

**For transmissions with tooth shift clutches (SMT, AMT, DCT):**

Raw OCR: `Tdx ¼ Td0 ¼ Td1000 ¼ 10 Nm Ü Tmax in / 2 000 Nm ¼ 0,005 Ü Tmax in`

Reconstructed: **Tdx = Td0 = Td1000 = 10 Nm × (Tmax,in / 2000 Nm) = 0,005 × Tmax,in**

where `Tmax,in` = Maximum allowed input torque in any forward gear of the transmission [Nm] = max(Tmax,in,gear); `Tmax,in,gear` = Maximum allowed input torque in a given gear (gear = 1, 2, 3, … top gear). **For transmissions with a hydrodynamic torque converter, this input torque is the torque at transmission input before the torque converter.**

**For transmissions with friction shift clutches (> 2 friction clutches):**

Raw OCR: `Tdx ¼ Td0 ¼ Td1000 ¼ 30 Nm Ü Tmax in / 2 000 Nm ¼ 0,015 Ü Tmax in`

Reconstructed: **Tdx = Td0 = Td1000 = 30 Nm × (Tmax,in / 2000 Nm) = 0,015 × Tmax,in**

(Here "friction clutch" means a clutch/brake operating with friction, required for sustained torque transfer in at least one gear.)

**For transmissions including an angle drive (e.g. bevel gear)** — add the angle-drive drag torque to Tdx's calculation:

Raw OCR: `Taddx ¼ Tadd0 ¼ Tadd1000 ¼ 10 Nm Ü Tmax in / 2 000 Nm ¼ 0,005 Ü Tmax in` (only if applicable)

Reconstructed: **Taddx = Tadd0 = Tadd1000 = 10 Nm × (Tmax,in / 2000 Nm) = 0,005 × Tmax,in**

▼M3 **For transmissions with an integrated differential**, the integrated differential is treated **as an angle drive** — the Tadd0, Tadd1000, fT_add expressions above are used in calculating Tl,in.

---

## Appendix 11 — Standard (fallback) torque loss values: Geared angle drive or drivetrain component with a single speed ratio

> **EV/Hybrid relevance flag:** This appendix's subject — a "geared angle drive or drivetrain component with a single speed ratio" — is the regulatory category that **covers single-speed reduction gears** of the type typically used in battery-electric and fuel-cell HDV drivelines (i.e., a fixed-ratio gear stage with no shifting elements, as opposed to a multi-speed SMT/AMT/DCT/APT). The formula and default coefficients below are directly relevant for sizing/estimating the mechanical loss of an EV's single-speed drive unit when test data isn't available. Note, however, that the Annex does **not** label this appendix as EV-specific — it is written generically for any single-ratio component (e.g., a bevel-gear angle drive) and the manufacturer determines applicability; treat the "EV relevance" framing here as this knowledge base's own analytical inference, not a statement in the Regulation itself.

►M3 Consistent with the standard loss values for a transmission+geared-angle-drive combination in Appendix 8, the standard losses of a geared angle drive or single-speed-ratio drivetrain component **without a transmission** are calculated from:

Raw OCR: `Tl;ad;in ¼ Tadd0 þ Tadd1000 Ü nin / 1 000 rpm þ f T_add Ü Tin`

Reconstructed: **Tl,ad,in = Tadd0 + Tadd1000 × (nin / 1000 rpm) + fT_add × Tin**

**Variables:**
- `Tl,in` = Torque loss related to the input shaft of transmission [Nm] *(note: the source variable list uses "Tl,in" in its definitions even though the formula itself uses "Tl,ad,in" — reproduced exactly as in the source; this inconsistency appears to be an artifact of the regulation text itself, not an OCR error, since both instances are legible)*
- `Taddx` = Additional angle drive gear drag torque at x rpm [Nm] (if applicable)
- `nin` = Speed at the input shaft of transmission [rpm]
- `fT` = 1 − η (η = efficiency)
- `fT_add` = **0,04** for angle drive gear
- `Tin` = Torque at the input shaft of transmission [Nm]
- `Tmax,in` = Maximum allowed input torque in any forward gear of transmission [Nm] = max(Tmax,in,gear); `Tmax,in,gear` = max allowed input torque in gear (gear = 1, 2, 3, … top gear)

Raw OCR: `Taddx ¼ Tadd0 ¼ Tadd1000 ¼ 10 Nm Ü Tmax in / 2 000 Nm ¼ 0,005 Ü Tmax in`

Reconstructed: **Taddx = Tadd0 = Tadd1000 = 10 Nm × (Tmax,in / 2000 Nm) = 0,005 × Tmax,in**

The standard losses from these calculations may be **added** to a transmission's Options-1–3 torque losses to get the combined transmission+angle-drive torque losses.

---

## Appendix 12 — Input parameters for the simulation tool (Transmission / TC / ADC / Retarder data schema)

This Appendix lists the parameters the transmission/TC/OTTC/ADC manufacturer must supply as simulation-tool input. The applicable XML schema and example data are available on the "dedicated electronic distribution platform" (not reproduced in this text extraction).

**Definitions:**
- **Parameter ID** — unique identifier used in the simulation tool for a specific input parameter or data set.
- **Type** — data type:
  | Type | Definition |
  |---|---|
  | string | sequence of characters, ISO8859-1 encoding |
  | token | sequence of characters, ISO8859-1 encoding, no leading/trailing whitespace |
  | date | date & time in UTC, format `YYYY-MM-DDTHH:MM:SSZ` (e.g. `2002-05-30T09:30:10Z`) |
  | integer | integral data type, no leading zeros (e.g. `1800`) |
  | double, X | fractional number with exactly X digits after the decimal point, no leading zeros (e.g. `double,2` → `2345.67`; `double,4` → `45.6780`) |
- **Unit** — physical unit of the parameter.

### ▼M1 Table 1 — Input parameters "Transmission/General"
| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| Manufacturer | P205 | token | [-] | |
| Model | P206 | token | [-] | |
| CertificationNumber | P207 | token | [-] | |
| Date | P208 | dateTime | [-] | Date/time the component hash is created |
| AppVersion | P209 | token | [-] | |
| TransmissionType | P076 | string | [-] | ►M3 Allowed values(¹): 'SMT', 'AMT', 'APT-S', 'APT-P', 'APT-N', **'IHPC Type 1'** ◄ |
| MainCertificationMethod | P254 | string | [-] | Allowed values: 'Option 1', 'Option 2', 'Option 3', 'Standard values' |
| ▼M3 DifferentialIncluded | P353 | boolean | [-] | ►M4 Only required for front-wheel-driven vehicles ◄ |
| AxlegearRatio | P150 | double,3 | [-] | Optional; only required if 'DifferentialIncluded' is true |

▼M1 footnote (¹): "DCT shall be declared as transmission type AMT."

> **EV/Hybrid relevance flag — important finding:** The `TransmissionType` allowed-value list includes **"IHPC Type 1"** alongside the conventional SMT/AMT/APT-S/APT-P/APT-N categories. "IHPC" is not spelled out anywhere in this Annex VI extraction — its expansion (plausibly something like "Integrated Hybrid/electric Powertrain Component," but this is **not confirmed by the source text in this extraction range**) and its technical definition are **not given in Annex VI**. Given the project's focus on HDEV sizing, this value almost certainly denotes a transmission-type category covering integrated electric or hybrid drive units (e.g., single-speed e-axles or integrated e-motor+gearbox units) within the VECTO type-approval framework, but **this is an inference, not something stated in the text read so far** — it should be verified against Annex III (vehicle input data, Table 8 referenced in §6.1.3 of this Annex — see file `07c`) or the main Regulation body/other annexes, which likely define "IHPC" explicitly. Flagging per project instructions: do not treat "IHPC = hybrid/electric powertrain component" as confirmed; verify against the full regulation text or VECTO documentation before relying on it.
> Also note the OCR rendered "Allowed values (42)" — this is almost certainly a mis-OCR'd footnote marker (likely "(1)", matching the single footnote that follows, or possibly two adjacent footnote references "(4)(2)" to other provisions) rather than a literal count of 42 values, since only 6 values are listed. Reproduced as extracted; flagged as ambiguous. Likewise "APTN" in the raw list most likely corresponds to "APT-N" (hyphen dropped by OCR), consistent with the "Case N" / "Case S" / "Case P" definitions in §2(22)-(23)/(33) of this Annex.

### Table 2 — Input parameters "Transmission/Gears" (per gear)
| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| GearNumber | P199 | integer | [-] | |
| Ratio | P078 | double,3 | [-] | ►M3 For a transmission with included differential, the transmission gear ratio is indicated **without** the axle gear ratio ◄ |
| MaxTorque | P157 | integer | [Nm] | optional |
| MaxSpeed | P194 | integer | [1/min] | optional |

### Table 3 — Input parameters "Transmission/LossMap" (per gear, per grid point)
| Parameter name | Parameter ID | Type | Unit |
|---|---|---|---|
| InputSpeed | P096 | double,2 | [1/min] |
| InputTorque | P097 | double,2 | [Nm] |
| TorqueLoss | P098 | double,2 | [Nm] |

### Table 4 — Input parameters "TorqueConverter/General"
| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| Manufacturer | P210 | token | [-] | |
| Model | P211 | token | [-] | |
| ▼M1 CertificationNumber | P212 | token | [-] | |
| Date | P213 | dateTime | [-] | Date/time the component hash is created |
| AppVersion | P214 | string | [-] | |
| CertificationMethod | P257 | string | [-] | Allowed values: 'Measured', 'Standard values' |

### Table 5 — Input parameters "TorqueConverter/Characteristics" (per grid point in the characteristic curve)
| Parameter name | Parameter ID | Type | Unit |
|---|---|---|---|
| SpeedRatio | P099 | double,4 | [-] |
| TorqueRatio | P100 | double,4 | [-] |
| InputTorqueRef | P101 | double,2 | [Nm] |

### ▼M3 Table 6 — Input parameters "ADC/General" (only required if component applicable)
| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| Manufacturer | P220 | token | [-] | |
| Model | P221 | token | [-] | |
| ▼M1 CertificationNumber | P222 | token | [-] | |
| Date | P223 | dateTime | [-] | Date/time the component hash is created |
| AppVersion | P224 | string | [-] | |
| Ratio | P176 | double,3 | [-] | |
| CertificationMethod | P258 | string | [-] | Allowed values: 'Option 1', 'Option 2', 'Option 3', 'Standard values' |

### ▼M3 Table 7 — Input parameters "ADC/LossMap" (per grid point; only required if component applicable)
| Parameter name | Parameter ID | Type | Unit |
|---|---|---|---|
| InputSpeed | P173 | double,2 | [1/min] |
| InputTorque | P174 | double,2 | [Nm] |
| TorqueLoss | P175 | double,2 | [Nm] |

> **EV/Hybrid relevance flag:** Table 7 ("ADC/LossMap") is the schema referenced by §6.1.3 "Case C" in Annex VI (the belt connecting an electric machine system to the main powertrain — see file `07c`), which explicitly states that "the input data required in accordance with **Table 7 of Appendix 12**" must be determined per Appendix 11, with `fT = 0,08` and `Tmax,in` = the max available torque of the electric machine system. This is the clearest, explicit EV-linkage in this Annex's input-parameter schema.

### Table 8 — Input parameters "Retarder/General" (only required if component applicable)
| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| Manufacturer | P225 | token | [-] | |
| Model | P226 | token | [-] | |
| ▼M1 CertificationNumber | P227 | token | [-] | |
| Date | P228 | dateTime | [-] | Date/time the component hash is created |
| AppVersion | P229 | string | [-] | |
| CertificationMethod | P255 | string | [-] | Allowed values: 'Measured', 'Standard values' |

### Table 9 — Input parameters "Retarder/LossMap" (per grid point; only required if component applicable)
| Parameter name | Parameter ID | Type | Unit |
|---|---|---|---|
| RetarderSpeed | P057 | double,2 | [1/min] |
| TorqueLoss | P058 | double,2 | [Nm] |

---

## Ambiguities / OCR flags summary for this file
1. **Pervasive OCR glyph substitution** in nearly every formula (¼→"=", Ä→"−", Ü→"×", Í...Î→parenthetical grouping, "ffiffiffi...p"/"ffiffiffiffiffiffi...q" → square-root radicals). Raw text is preserved verbatim above; reconstructions are my interpretation, clearly labelled, for engineering usability — always defer to the original PDF/EUR-Lex text for legal precision.
2. **Figures 1–6 and 2A/2B/2C** (test-rig setup diagrams for Options 1 and 3, including integrated-differential variants) are referenced throughout §3.1.8 and §3.3.9 but **not visually extracted** — flagged individually at each occurrence above.
3. **"IHPC Type 1"** transmission type (Appendix 12, Table 1) — flagged above as the strongest candidate EV/hybrid-relevant data point in the Annex VI parameter schema, but its full definition was not found within this annex's extracted range; needs verification against Annex III or VECTO documentation.
4. **"Allowed values (42)"** footnote-marker anomaly and **"APTN"** (likely "APT-N") — both flagged above as probable OCR artifacts, reproduced as-extracted.
5. Appendix 11's variable list mixes `Tl,in` (in prose) with `Tl,ad,in` (in the formula) — reproduced exactly as in the source; flagged as a possible drafting inconsistency in the regulation itself, not corrected here.
