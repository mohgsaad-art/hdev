
# Annex Xb — Certification of Electric Powertrain Components
## Part 5: Testing of Fuel Cell Systems (FCS)

**Source:** Commission Regulation (EU) 2017/2400 (consolidated), CELEX **02017R2400**, consolidation date **01.01.2026**.
**Range covered:** Annex Xb, point 7 (lines ≈21204–21864).
**Amendment provenance:** **All of point 7 is ►M4 — Commission Regulation (EU) 2025/258.** This is the **newest** addition to the Regulation and the **first EU-legislated hydrogen fuel-cell-system test/certification methodology for VECTO** (2025) — three years after the 2022 e-machine/battery/capacitor methodology (►M3). See file 12a §0.
**OCR caveat:** see file 12b header. The FCS section's equations are especially dense (nested summations, averaging-of-averaging steps); reconstructed carefully below but flagged wherever the OCR corruption made the operator ambiguous.

---

## 7.0 Why FCS testing looks different from battery/capacitor testing

FCS certification is a **steady-state power-sweep** methodology (≥12 discrete electrical-power operating points, ascending then descending, each held until stable) rather than a pulse-current/SOC-sweep methodology. The output is a **fuel-flow-vs-electric-power-output map** (analogous in spirit to an ICE's fuel map), explicitly designed to feed the VECTO simulation tool as an `OutputPower` → `FuelConsumption` lookup table (Appendix 15 Table 2, parameters P573/P574 — see file 12h).

## 7.1 Component test procedure for FCS

### 7.1.1 Fuel quality — Table 8: Definition of hydrogen reference fuel

| Characteristic | Unit | Min | Max | Test method |
|---|---|---|---|---|
| Hydrogen fuel index | % mole fraction | 99.97 (¹) | — | — |
| Total non-hydrogen gases | μmol/mol | — | 300 | List of non-H₂ gases + contaminant spec (⁶) |
| Water (H₂O) | μmol/mol | — | 5 | (⁵) |
| Total hydrocarbons except methane (C1 eq.) (²) | μmol/mol | — | 2 | (⁵) |
| Methane (CH₄) | μmol/mol | — | 100 | (⁵) |
| Oxygen (O₂) | μmol/mol | — | 5 | (⁵) |
| Helium (He) | μmol/mol | — | 300 | (⁵) |
| Total Nitrogen (N₂) and Argon (Ar) (²) | μmol/mol | — | 300 | (⁵) |
| Carbon dioxide (CO₂) | μmol/mol | — | 2 | (⁵) |
| Carbon monoxide (CO) (³) | μmol/mol | — | 0.2 | (⁵) |
| Total sulfur compounds (⁴) (H₂S basis) | μmol/mol | — | 0.004 | (⁵) |
| Formaldehyde (HCHO) | μmol/mol | — | 0.2 | (⁵) |
| Formic acid (HCOOH) | μmol/mol | — | 0.2 | (⁵) |
| Ammonia (NH₃) | μmol/mol | — | 0.1 | (⁵) |
| Total halogenated compounds (⁵) (halogenate-ion basis) | μmol/mol | — | 0.05 | (⁵) |

Footnotes: (1) hydrogen fuel index = 100 mol% minus "total non-hydrogen gases" (expressed in mol%). (2) Total hydrocarbons except methane includes oxygenated organic species. (3) Sum of measured CO + HCHO + HCOOH ≤ 0.2 μmol/mol. (4) Total sulfur compounds include at minimum H₂S, COS, CS₂ and mercaptans typically found in natural gas. (5) Test method shall be documented; ISO 21087 methods preferable. (6) Analysis of specific contaminants may be exempted depending on production process, with the vehicle manufacturer providing reasons to the responsible authority.

### 7.2 System boundary of the UUT and component descriptions

**7.2.1 System boundary**: FCS UUT may comprise different BoPCs; allowed configurations set out in **Table 9**. Terminology based on **SAE J2615**. All FCS configurations share two traits:
(a) tested/certified **without the outer cooling sub-system**, as a standalone power-supply unit with **no external vehicle electric components connected**;
(b) all comprise the **APS**.
Passive components affecting fuel consumption shall either be part of the FCS UUT or fitted in the test setup to ensure comparable vehicle-like operation.

The FCS UUT is set up per Table 9 and points 7.2.2–7.2.3; the configuration determines the FCS **type identifier**: **'A', 'B', 'C' or 'D'**.

### 7.2.2 FCS without Power Conditioning Sub-system (PCS)
If PCS not included → correction methods of point **7.5** applied to account for the power loss due to PCS efficiency.

### 7.2.3 FCS excluding power-consuming BoP components
Correction methods of point **7.5** applied to account for mandatory power-consuming components not in the UUT. All excluded components and their power uptake must be listed/documented in the Appendix 7 information document.

### Table 9 — Definition of FCS variants (Types A–D) for certification

Legend: "Part of FCS" = is the component considered inside the certified energy boundary; "Fitted for certification test" = is it physically present on the test bench (if not part of FCS, may be test-cell equipment per manufacturer spec).

| Sub-system | Component | Part of FCS? | Fitted for certification test |
|---|---|---|---|
| APS | Inlet particle filter | No | Yes, or test cell equipment (²) |
| APS | Inlet manifold | No | Yes, or test cell equipment (²) |
| APS | Intake air charging equipment (e.g. electric turbocharger/compressor) | Yes | Yes |
| APS | Air flow meter (³) | Yes | Yes |
| APS | Air inlet duct work | No | Yes, or test cell equipment (²) |
| APS | Inlet silencer (³) | No | Yes, or test cell equipment (²) |
| APS | Charge air cooler (³) | Yes | Yes |
| APS | Humidification (³) | Yes | Yes |
| TMS | All coolant pump(s) | Yes (Type A/C) / No or partly (Type B/D) | Yes; else test cell equipment (¹)(²)(⁵) |
| TMS | Radiator | No | Test cell equipment (²) |
| TMS | Ion-Exchanger (³)(⁶) | Yes | Yes, or test cell equipment (²)(³) |
| TMS | Fan | No | No |
| WTS | Water separator (³) | Yes | Yes |
| WTS | Drain Valve (³)(⁶) | Yes | Yes |
| WTS | Exhaust manifold | No | Yes, or test cell equipment (²) |
| WTS | Connecting pipes | No | Yes, or test cell equipment (²) |
| WTS | Silencer (³) | No | Yes, or test cell equipment (²) |
| WTS | Tail pipe | No | Yes, or test cell equipment (²) |
| WTS | Exhaust H₂-Sensor | No | Yes, or test cell equipment (²) |
| FPS | Fuel Supply System (FSS) | No | Yes, or test cell equipment (²) |
| FPS | Pressure regulator / Injector | Yes | Yes |
| FPS | Fuel heat exchanger (³) | Yes | Yes |
| FPS | Active Recirculation device (compressor/pump) (³) | Yes | Yes |
| FPS | Passive Recirculation device (injector/ejector) (³) | Yes | Yes |
| FPS | Filters (³) | Yes | Yes |
| FCSS | (no further breakdown) | Yes | Yes |
| PDS | Electrical components (cables, switches, relays) | Yes | Yes (⁴) |
| PCS | Voltage regulator (DC/DC) and/or converter (DC/AC) | Yes (Type A/C) / No (Type B/D) | Yes (Type A/C) / Test cell equipment (¹)(²) (Type B/D) |
| Fuel cell control sub-system | Processing/control unit | Yes | Yes |
| Fuel cell control sub-system | Software of specified version | Yes | Yes (⁴) |

Footnotes: (1) not part of the certified energy balance — missing BoPC accounted for via point 7.5. (2) per manufacturer spec, ensuring real-world-like operation. (3) if applicable/mounted on the FCS/vehicle. (4) only adaptations allowed to enable standalone operation. (5) integration of items optional. (6) may be part of either TMS or WTS.

### 7.2.4 Description of specific BoPCs
The TMS and cooling sub-system may have multiple coolant circuits, each divisible into inner/outer parts.
- **7.2.4.1 Inner part**: all cooling-circuit parts integrated into the FCS, part of the UUT's TMS.
- **7.2.4.2 Outer part**: all cooling-sub-system parts **not** part of the UUT — the "outer cooling sub-system" — including chassis-integrated heat exchangers that may vary by vehicle type.

---

## 7.3 Test procedure

### 7.3.1 Purpose
Validate manufacturer-declared performance/capability and measure fuel consumption/hydrogen mass flow under well-defined operating conditions, generating reproducible VECTO input data for fuel-consumption prediction of the certified FCS component.

### 7.3.2 Operation parameters and operating points — Table 10

| Name/Description | Mandatory | Unit |
|---|---|---|
| SCOP | Y | kW |
| Relative transition slope, ramp-up (RTS-UP) — manufacturer may specify; default per 7.3.4.6 if not | N | s⁻¹ |
| Relative transition slope, ramp-down (RTS-DOWN) — manufacturer may specify; default per 7.3.4.6 if not | N | s⁻¹ |
| Operating points #01..#nop (OP01 = lowest electrical power output; OPnop = highest; suffix 'a'=ascending, 'd'=descending per operating point) | Y | kW |
| FCS Type A/C: $U_{PCS,out,lower}$ — lower PCS output voltage at which FCS operates at OPnop without current limitation. FCS Type B/D: $U_{PCS,lower}$ is a manufacturer DC/DC requirement spec; test-cell DC/DC must meet it | Y | V |
| FCS Type A/C: $U_{PCS,out,upper}$ — upper PCS output voltage at OPnop. FCS Type B/D: $U_{PCS,upper}$ — manufacturer DC/DC requirement spec | Y | V |

### 7.3.3 Methodology
Records static data on a stabilised FCS at a set number of operating points, each specified by its electrical-power-output set-point. FCS operated in standard operating conditions documented per Appendix 7.
Voltage level at the PCS/external-electric-components interface:
$$U_{PCS,out} = 0.5 \times (U_{PCS,out,upper} + U_{PCS,out,lower})$$
If PCS is not part of the UUT, $U_{PCS,upper}$/$U_{PCS,lower}$ are derived from the manufacturer's DC/DC-converter requirement specs.
Manufacturer declares (per Appendix 7) **realistic boundary conditions** for normal in-vehicle FCS operation.

### 7.3.4 Test procedure description
Entire procedure performed **without interruption**, fully recorded.
Manufacturer specifies the lowest (OP01) and highest (OPnop) electrical-power-output operating points for the certification test range, covering the **whole real-world-operation span**.

**7.3.4.1 Definition of operating points**:
- Number of OPs, **nop ≥ 12**.
- OP01 and OPnop mandatory.
- Remaining OPs distributed within the range — **not necessarily equidistant**, but must enable good interpolation; smaller step size allowed in regions of elevated non-linearity.
- Naming: $P@OP01$, $P@OPxx$ (xx = 02…nop−1), $P@OPnop$.
- Maximum step size between adjacent OPs:
$$Step\text{-}size_{max} < 0.20 \times (P@OP_{nop} - P@OP_{01})$$

**7.3.4.2 Conditioning phase**: ≥**60 minutes** at an SCOP set-point between **40%–60%** of OPnop, defined by the manufacturer.

**7.3.4.3 Sequence of operating points**: starts at OP01, ascends to OPnop, then descends back to the lowest OP. Total duration depends on individual-OP stabilisation times. **[Figure 3 — "Sequence of OP" — referenced in source but not visually extracted from this text-only OCR.]**

**7.3.4.4 Steps at each operating point**:
- **Stabilisation time**: individually defined per OP, **between $t_{stab,min}=300{-}1\,s$ and $t_{stab,max}=1800{+}1\,s$**. Ascending/descending stabilisation times for the same OP must be within **2 s** of each other. Starts immediately after the ramp from the previous setpoint completes.
- **Analysis time**: $t_{anlys} = 180 \pm 1\,s$, starts after stabilisation; measured values in this window must meet the stability criteria (7.3.4.5) **unless** $t_{stab,max}=1800{+}1\,s$ was already used.
- **Standby time**: $t_{stb} = 10 \pm 1\,s$, follows the analysis time, separating from the next load point.
**[Figure 4 — "Steps to be performed at each OP" — referenced in source but not visually extracted from this text-only OCR.]**

**7.3.4.5 Stability criteria**:
Steadiness of fuel consumption (metered at the FCS fuel inlet, $\dot{m}_{F,FPS}$ per Figure 5) assessed by a **least-squares linear regression** (independent var. = time, dependent var. = fuel flow), per 7.3.6.1–7.3.6.2. Two stability indicators (7.3.6.3):
(a) **ARS** — absolute value of the relative slope of the estimate;
(b) **REE** — relative error of the estimate (degree of fluctuation).
An OP is **stable** if both indicators are below threshold within the analysis window. Normalised set power:
$$P@OPxx_{norm} = \frac{P@OPxx}{P@OP_{nop}}$$

### Table 11 — Threshold values

| Indicator | Threshold value |
|---|---|
| ARS | $7.0\times10^{-5}\ s^{-1}$ |
| REE | $\dfrac{1}{P@OPxx_{norm}+1}$ |

If stability fails at any OP, the test is **repeated** with an enlarged (up to the maximum) stabilisation time.

**7.3.4.6 Transition slope between OPs**: moderate slope, manufacturer-specified for up-/down-ramping; no restriction on slope value/shape. If none specified, default **RTS = +0.002 ± 0.0004 s⁻¹** (ramp-up) / **−0.002 ± 0.0004 s⁻¹** (ramp-down):
$$RTS = \frac{dP_{el}/dt}{P@OP_{nop}}$$
— $P_{el}$: electrical DC power output of the FCS; $dP_{el}/dt$: slope from $P_{el,1}$ at $t_1$ to $P_{el,2}$ at $t_2$ (transition time $dt=t_2-t_1$ small enough to neglect non-linearity).

**7.3.4.7 Calculation of measured fuel consumption and power output**:
Arithmetic mean over $t_{anlys}$ at each OP:
$$P_{FCS,avg,p} = \frac{1}{n}\sum_{i=1}^{n} P_{FCS,i,p} \qquad\qquad \dot{m}_{F,avg,p} = \frac{1}{n}\sum_{i=1}^{n} \dot{m}_{F,i,p}$$
— $p$ = ascending (a) or descending (d) path (omitted for OPnop); $n$ = number of recorded values in the averaging period. Power metered after the PDS ($P_{el,PDS}$) or PCS ($P_{el,PCS}$) per Figure 5/point 7.4, depending on UUT type.

Then, for each OP **below OPnop**, average the ascending and descending results:
$$P_{FCS,avg} = \frac{P_{FCS,avg,a} + P_{FCS,avg,d}}{2} \qquad\qquad \dot{m}_{F,avg} = \frac{\dot{m}_{F,avg,a} + \dot{m}_{F,avg,d}}{2}$$
(For OPnop this second averaging step does not apply — only one measurement exists.)

**7.3.4.8 Correction of FCS power output to reference conditions**:
$$P^*_{FCS} = P_{FCS,avg} + \Delta\eta \cdot \dot{m}_{F,avg} \cdot \frac{NCV_{std,H2}}{3600\ s/h}$$
with
$$\Delta\eta = k_{load} \times (p_{in} - p^*)$$
— $P^*_{FCS}$: electrical power output at reference conditions [kW]; $P_{FCS,avg}$: per 7.3.4.7 [kW]; $\dot{m}_{F,avg}$: fuel flow per 7.3.4.7 [g/h]; $NCV_{std,H2}$: standard net calorific value of hydrogen per point 5.3.3.1 [MJ/kg]; $p^*$: reference pressure = **0.975 bar**; $p_{in}$: intake-air pressure to the APS (labelled $p\_A,APS$ in Figure 5), averaged over $t_{anlys}$ then over ascending/descending (except OPnop) as for fuel consumption; $k_{load}$: gradient of efficiency per 7.3.4.8.1 [bar⁻¹].

**7.3.4.8.1 Gradient of efficiency $k_{load}$**:
Normalised power = $P_{FCS,avg}$(specific OP) ÷ $P_{FCS,avg}$(OPnop). $k_{load}$ determined from **Table 12** by **linear interpolation**; if normalised power < 0.1, use the $k_{load}$ value defined at 0.1.

### Table 12 — Parameter $k_{load}$ as function of normalized power

| Normalized power [-] | $k_{load}$ |
|---|---|
| 0.1 | 0.3730 |
| 0.2 | 0.1485 |
| 0.5 | 0.0745 |
| 0.8 | 0.0855 |
| 1.0 | 0.1115 |

### 7.3.5 Test conditions — Table 13: Ambient and media condition limits during certification test

| Parameter | Min | Max |
|---|---|---|
| Ambient pressure | 90.0 kPa | 102.0 kPa |
| Ambient temperature | 288.0 K | 298.0 K |
| Oxidant (air) inlet pressure | 90.0 kPa | 102.0 kPa |
| Oxidant (air) inlet temperature | 288.0 K | 303.0 K |
| Relative humidity, oxidant (air) supply | 45.0 % | 80.0 % |

### 7.3.6 Statistics

**7.3.6.1 Mean / standard deviation**:
$$\bar{x} = \frac{\sum_{i=1}^{n} x_i}{n} \qquad\qquad s = \sqrt{\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}}$$

**7.3.6.2 Regression analysis**:
$$a_1 = \frac{\sum_{i=1}^{n}(y_i-\bar{y})(x_i-\bar{x})}{\sum_{i=1}^{n}(x_i-\bar{x})^2} \qquad\qquad a_0 = \bar{y} - a_1\bar{x}$$
$$SEE = \sqrt{\frac{\sum_{i=1}^{n}\left[y_i-(x_i\cdot a_1 + a_0)\right]^2}{n}}$$

**7.3.6.3 Stability criteria**:
$$ARS = \left|\frac{a_1}{\bar{y}}\right| \qquad\qquad REE = \left|\frac{SEE}{\bar{y}}\right| \times 100\%$$

### 7.4 Certification test documentation
Reproducibility data documented in the Appendix 7 information document. Sensor positions defined per **Figure 5** ("Schematic sketch of a representative FCS including the position of relevant sensors"). **[Figure 5 — referenced in source but not visually extracted from this text-only OCR — this is an important schematic for implementers, showing sensor labels like $P\_el,PDS$, $P\_el,PCS$, $\dot m\_F,FPS$, $p\_A,APS$, $T\_C,in/out\_TMS$ etc. used throughout the equations above; consider requesting the original PDF page for this figure.]**

### 7.5 Calculation of effective electrical power output
$P^*_{FCS}$ (7.3.4.8) is corrected for:
(a) PCS not being part of the FCS installed for the test;
(b) power-consuming BoP components not installed at all, not installed within the UUT, or externally powered by test-bed infrastructure during the test.

**7.5.1 Recording of additional values**: for each coolant pump not installed (at all / within the UUT): $V̇_{C,TMS,in}$ (coolant volume flow upstream of TMS), $p_{C,TMS,in}$, $p_{C,TMS,out}$ (coolant pressures up-/downstream of TMS). For each externally-powered power-consuming BoP component: electrical power uptake $P_{el,AUX}$. Per 3.2.2, volume flow and electrical power uptake carry a **positive** sign. All recorded values averaged per OP using the same $t_{anlys}$ as 7.3.4.4.

**7.5.2 Equations for corrections**: evaluated per OP.

If PCS not part of the installed FCS, correct the PDS-location measured power for generic PCS losses:
$$P^*_{el,PCS} = P^*_{FCS,PDS} \times \eta_{DC/DC}$$
— $\eta_{DC/DC}$ (generic DC/DC converter efficiency) = **0.975**.

For each coolant pump not installed (at all/within UUT):
$$P_{el,Cool} = \frac{(p_{C,TMS,in} - p_{C,TMS,out}) \times \dot{V}_{C,TMS,in}}{\eta_{WP,hyd} \times \eta_{WP,EM}}$$
— $\eta_{WP,hyd}$ (generic pump hydraulic efficiency) = **0.8**; $\eta_{WP,EM}$ (generic electric pump-drive efficiency) = **0.8**.

**Final effective electrical power output** (VECTO input):
$$P^*_{el,FCS,net} = P^*_{el,PCS} + \sum_{i=1}^{n}\frac{P_{el,AUX,i}}{\eta_{DC/DC}} + \sum_{j=1}^{o} P_{el,AUX,j} + \sum_{k=1}^{p}\frac{P_{el,Cool,k}}{\eta_{DC/DC}} + \sum_{l=1}^{q} P_{el,Cool,l}$$
where $\eta_{DC/DC}=0.975$ throughout, and the four summations distinguish components by their electrical connection point:
- $P_{el,AUX,i}$: auxiliaries connected at PDS, or via a **separate** DC/DC converter (loss-corrected, $i=1..n$).
- $P_{el,AUX,j}$: auxiliaries connected at PCS, or **without** a separate DC/DC converter (not loss-corrected, $j=1..o$).
- $P_{el,Cool,k}$: coolant pumps connected at PDS / via separate DC/DC (loss-corrected, $k=1..p$).
- $P_{el,Cool,l}$: coolant pumps connected at PCS / without separate DC/DC (not loss-corrected, $l=1..q$).

**7.5.3 Input to the simulation tool**: $P^*_{el,FCS,net}$ **× (−1)**, and absolute values of fuel flow ($\dot m_{F,avg}$, 7.3.4.7), are used as VECTO input. *(The ×(−1) sign flip aligns with the point 3.2.2 convention that energy/media leaving the UUT boundary is negative — the net electrical output, which leaves the FCS, is recorded as a negative quantity consistent with that sign convention, then used as the magnitude.)*

---

## Cross-reference to standard (default) FCS values and the input parameter schema

Where certification uses **standard values** instead of measurement, **Appendix 11** gives: the FCS input data based on max. electrical power output (per UN Regulation No 100, Annex 6, Appendix 1, point 4.6), a generic **normalized-power-vs-efficiency table** (0.01→3.67%; 1.0→40.0%), and the fuel-mass-flow equation using the standard net calorific value of hydrogen $NCV_{std,H2}$ (point 5.3.3.1). Fully reproduced in file **12h-annex-xb-standard-values-and-simulation-input-parameters.md**. The FCS XML input schema (`FCSRatedPower`, `FuelMap` with `OutputPower`/`FuelConsumption`, parameter IDs P566–P574) is in Appendix 15, also in file 12h.
