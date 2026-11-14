
# Annex Xb — Certification of Electric Powertrain Components
## Part 6: Conformity of Production, Family Concept, Markings, and Appendix Guide

**Source:** Commission Regulation (EU) 2017/2400 (consolidated), CELEX **02017R2400**, consolidation date **01.01.2026**.
**Range covered:** Annex Xb, Appendices 1–7, 12, 13, 14 (lines ≈21865–24320 approx., interleaved with Appendices 8–11 and 15 which are split out to file 12h for length/substantive reasons — see note below).
**Amendment provenance:** Appendices 1–6, 12 (points 1–4), 13 (point 1), 14 are **►M3** (Reg. (EU) 2022/1379). Appendix 7, Appendix 12 point 5 (FCS conformity of production), and Appendix 13 point 2 (FCS family concept) are **►M4** (Reg. (EU) 2025/258).

**Note on file organisation**: the source instructs appendices to be summarised in this file except where they contain substantive calculation methodology, tolerances or defaults, which must be preserved in full. Appendices 8 (EM standard values), 9 (IEPC standard values), 10 (REESS/battery/capacitor standard values), 11 (FCS standard values) and 15 (full simulation-tool input-parameter schema, all components) are **all substantive, default-value-generating methodology directly relevant to vehicle-level sizing when no component measurement is available** — given their length and importance, they are split into a dedicated file, **`12h-annex-xb-standard-values-and-simulation-input-parameters.md`**, rather than compressed here. This file (12f) covers the Appendix 12 (conformity of production) and Appendix 13 (family concept) methodology in full, plus a summarised guide to the purely-administrative/template appendices (1–7, 14).

---

## PART A — Appendix 12: Conformity of the Certified CO2 Emissions and Fuel Consumption Related Properties ("CoP")

This is the **production-conformity testing regime** — i.e. how regulators spot-check that series-production components still match their certified type, on an ongoing annual basis.

### A.1 Electric machine systems or IEPCs

- **1.1** Every EMS/IEPC must conform to the approved type per its certificate/annexes. CoP procedures comply with **Article 31 of Regulation (EU) 2018/858**.
- **1.2** Conformity checked against the certificate + Appendix 2/3 information packages.
- **1.4** Manufacturer tests **annually** at least the number of units in **Table 1**, based on total annual EMS/IEPC production (counting only units under this Regulation for which **no standard values** were used).
- **1.5** For annual volumes **≤4000**: family choice for testing agreed between manufacturer and approval authority.
- **1.6** For annual volumes **>4000**: the **highest-production-volume family is always tested**; manufacturer justifies the number of tests and family choice; remaining families agreed with the authority.

#### Table 1 — Sample size conformity testing (EMS / IEPC)

| Total annual production | Annual number of tests | Alternatively |
|---|---|---|
| 0 – 1 000 | n.a. | 1 test every 3 years (*) |
| 1 001 – 2 000 | n.a. | 1 test every 2 years (*) |
| 2 001 – 4 000 | 1 | n.a. |
| 4 001 – 10 000 | 2 | n.a. |
| 10 001 – 20 000 | 3 | n.a. |
| 20 001 – 30 000 | 4 | n.a. |
| 30 001 – 40 000 | 5 | n.a. |
| 40 001 – 50 000 | 6 | n.a. |
| > 50 000 | 7 | n.a. |

(*) The CoP test shall be performed in the first year.

- **1.7** Approval authority + manufacturer jointly identify the type(s) to test; authority ensures the tested type matches series-production standards.
- **1.8** If a test result (per 1.9) exceeds the 1.9.4 limit → **3 additional units** from the same family tested; if any fails → **Article 23 applies** (non-conformity consequences under the Regulation).

**1.9 Production conformity testing procedure:**
- *1.9.1 Boundary conditions*: all Annex Xb certification-test boundary conditions apply, **except**: cooling power must stay within the certification limits; measurement is performed at **only one** of the two voltage levels (4.1.3), chosen by the manufacturer; the point 3.1 **measurement-equipment accuracy specs do NOT need to be met** for CoP testing (i.e. CoP testing may use less-precise instrumentation than type-approval testing — hence the uncertainty-correction equations below).
- *1.9.2 Test run*: **two setpoints** measured (optional cooldown between). **Setpoint 1**: overload-characteristics test (4.2.5). **Setpoint 2**: maximum-30-minute-continuous-torque test (4.2.4).
- *1.9.3 Post-processing — measurement-uncertainty correction*: because CoP testing may use lower-accuracy equipment than type approval, measured mechanical/electrical power values (4.2.5.3, 4.2.4.3) are corrected for the **difference** in equipment uncertainty between type-approval and CoP measurement systems (rotational speed, torque, current, voltage), separately for analyser-reading uncertainty and max-calibration-value uncertainty (both per point 3.1):

$$\Delta u_{P,el,CoP} = \sqrt{\Delta u_{U,maxcalib}^2 + \Delta u_{U,value}^2 + \Delta u_{I,maxcalib}^2 + \Delta u_{I,value}^2}$$
$$\Delta u_{P,mech,CoP} = \sqrt{\Delta u_{T,maxcalib}^2 + \Delta u_{T,value}^2 + \Delta u_{n,maxcalib}^2 + \Delta u_{n,value}^2}$$

Corrected values:
$$P^*_{mech} = P_{mech,meas}\,(1 - \Delta u_{P,mech,CoP}) \qquad\qquad P^*_{el} = P_{el,meas}\,(1 + \Delta u_{P,el,CoP})$$

- *1.9.4 Evaluation*: efficiency at each setpoint = $P^*_{mech}/P^*_{el}$. **$\eta_{A,CoP}$** = arithmetic mean of the two setpoints' efficiencies. **Pass condition**: $|\eta_{A,CoP} - \eta_{A,TA}| < 3\%$ of $\eta_{A,TA}$ — **raised to 4%** for an IEPC with a gearbox **or** a differential, and to **5%** for an IEPC with **both** a gearbox and a differential. $\eta_{A,TA}$ (type-approved efficiency) = arithmetic mean of the two 4.3.5/4.3.6 efficiency figures from the original type-approval information document.

### A.2 IHPCs Type 1

- **2.1–2.2** Same Article-31/Reg. 2018/858 basis; checked against Appendix 4 information package.
- **2.3–2.4** The point-1 (EMS/IEPC) provisions apply, **except**:
  (a) checked **per individual type**, not family (families not allowed for IHPC Type 1 — see 12b §4.4);
  (b) number-of-tests allocation agreed between manufacturer/authority;
  (c) all "family" references → "individual type" references;
  (d) $\eta_{A,TA}$ = arithmetic mean of the 4.3.5/4.3.6 figures **without** applying the 4.4.2.3 "virtual EMS" post-processing steps.

### A.3 Battery systems or representative battery subsystems

- **3.1–3.2** Same basis; checked against Appendix 5.
- **3.4** Annual test count — **Table 2**:

#### Table 2 — Sample size conformity testing (Battery)

| Total annual production | Annual tests | Alternatively |
|---|---|---|
| 0 – 3 000 | n.a. | 1 test every 3 years (*) |
| 3 001 – 6 000 | n.a. | 1 test every 2 years (*) |
| 6 001 – 12 000 | 1 | n.a. |
| 12 001 – 30 000 | 2 | n.a. |
| 30 001 – 60 000 | 3 | n.a. |
| 60 001 – 90 000 | 4 | n.a. |
| 90 001 – 120 000 | 5 | n.a. |
| 120 001 – 150 000 | 6 | n.a. |
| > 150 000 | 7 | n.a. |

(*) First-year CoP test required.

- **3.6** Failing the 3.7.4 threshold → 3 additional units tested; any failure → Article 23.
- **3.7 Production conformity testing:**
  - *3.7.1*: all certification-test boundary conditions apply (unlike EMS, **no relaxation** of measurement-equipment accuracy is stated for battery CoP).
  - *3.7.2 Test run* — **two tests**:
    - **Test 1**: rated-capacity procedure (5.4.1).
    - **Test 2** (after Test 1): full-charge + thermal equilibration + standard cycle (5.3); actual test starts within 1–3 h of the standard cycle (else repeat); discharge at **3C (HPBS)** / **1C (HEBS)** to reach test SOC; then:
      - **HPBS**: 20-second discharge at **80% SOC** with declared $I_{dischg\_max}$, and 20-second charge at **20% SOC** with declared $I_{chg\_max}$ (both as documented at type approval).
      - **HEBS**: 120-second discharge at **90% SOC** with declared $I_{dischg\_max}$, and 120-second charge at **20% SOC** with declared $I_{chg\_max}$.
      - Currents recorded over the respective durations.
  - *3.7.3 Post-processing*: HPBS currents averaged over **20 s**; HEBS over **120 s**; absolute values used.
  - *3.7.4 Evaluation* — pass requires **all four**:
    (a) $C_{CoP} \ge 0.95\, C_{TA}$ (rated capacity ≥95% of type-approval value)
    (b) $(\eta_{BAT,CoP} - \eta_{BAT,TA}) \le 3\%$
    (c) $I_{dischg\_max,CoP} \ge I_{dischg\_max,TA}$ (at 80% SOC HPBS / 90% SOC HEBS)
    (d) $I_{chg\_max,CoP} \ge I_{chg\_max,TA}$ (at 20% SOC)

### A.4 Capacitor systems

- **4.1–4.2** Same basis; checked against Appendix 6.
- **4.4** Annual test count — **Table 3** (identical thresholds/values to battery Table 2: 0–3000→3yr, 3001–6000→2yr, 6001–12000→1, 12001–30000→2, 30001–60000→3, 60001–90000→4, 90001–120000→5, 120001–150000→6, >150000→7).
- **4.6** Failing 4.7.4 → 3 additional units; any failure → Article 23.
- **4.7 Production conformity testing**:
  - *4.7.1*: all certification boundary conditions apply.
  - *4.7.2 Test run*: per point 6.3 (the single charge/discharge-cycle test).
  - *4.7.3*: post-processed per point 6.4.
  - *4.7.4 Evaluation* — pass requires **both**:
    (a) $|(C_{CoP}/C_{TA}) - 1| < 3\%$
    (b) $|(R_{CoP}/R_{TA}) - 1| < 3\%$

### A.5 Fuel cell systems (►M4)

- **5.1–5.3** Same basis; checked against Appendix 7.
- **5.4** Annual test count — **Table 4**:

#### Table 4 — Sample size conformity testing (FCS)

| Number of relevant FCS produced the year before (**) | Annual number of tests |
|---|---|
| 0 – 3 000 | 1 test every 3 years (*) |
| 3 001 – 6 000 | 1 test every 2 years (*) |
| 6 001 – 12 000 | 1 |
| 12 001 – 30 000 | 2 |
| 30 001 – 60 000 | 3 |
| 60 001 – 90 000 | 4 |
| 90 001 – 120 000 | 5 |
| 120 001 – 150 000 | 6 |
| > 150 000 | 7 |

(*) First-year CoP test required. (**) Only FCS under this Regulation that did **not** receive standard values per Appendix 11 count.

- **5.6** Failing 5.7.4 → 3 additional units; any failure → Article 23.
- **5.7 Production conformity testing**:
  - *5.7.1 Boundary conditions*: certification boundary conditions apply, **except** the point 3.1 measurement-equipment accuracy specs **do not need to be met**; CoP testing **may use regular market fuel** (reference fuel of 7.1.1 only used at manufacturer's request).
  - *5.7.2 Test run*: per point 7.3.4, but with a **reduced OP count**, or the manufacturer may opt to re-measure the full original OP set. Reduced-OP target points selected by normalized set power $P@OPxx_{norm} = P@OPxx / P@OP_{nop}$, chosen from the original certification's OPs by these rules:
    (a) OP next ≤0.15 (or lowest OP if none exists);
    (b) OP next >0.15 (or next-highest if (a) duplicates);
    (c) OP closest to 0.4 (tie → lower OP; or next-highest if duplicate);
    (d) OP next <0.7 (or next-highest if duplicate);
    (e) OP = 1.0 (measured once if duplicate).
    OPs with normalized power 1.0 are treated as OPnop (measured once); all others measured twice (ascending+descending).
  - *5.7.3 Post-processing*: $P_{FCS,avg}$ processed per point 7.5 → $P^*_{el,FCS,net}$; then corrected for CoP-equipment uncertainty (current, voltage, fuel mass flow) analogously to the EMS procedure:
    $$\Delta u_{P,el,CoP} = \sqrt{\Delta u_{U,maxcalib}^2 + \Delta u_{U,value}^2 + \Delta u_{I,maxcalib}^2 + \Delta u_{I,value}^2}$$
    $$\Delta u_{\dot m fuel,CoP} = \sqrt{\Delta u_{\dot m fuel,maxcalib}^2 + \Delta u_{\dot m fuel,value}^2}$$
    $$P^*_{el,CoP} = P^*_{el,FCS,net}\,(1-\Delta u_{P,el,CoP}) \qquad\qquad m_{F,CoP} = \dot m_{F,avg}\,(1+\Delta u_{\dot m fuel,CoP})$$
  - *5.7.4 Evaluation*: specific fuel consumption $SFC_{CoP} = m_{F,CoP}/P^*_{el,CoP}$ per target OP; type-approved $SFC_{TA} = \dot m_{F,avg}/P^*_{el,FCS,net}$ from the original certification's matching OPs. Absolute relative deviation per OP:
    $$ARD = \frac{|SFC_{CoP}-SFC_{TA}|}{SFC_{TA}}$$
    **Pass**: average ARD across all tested OPs **< 0.08** (8%).

---

## PART B — Appendix 13: Family Concept (full detail)

### B.1 Electric machine systems and IEPCs (►M3)

A **family** groups EMS/IEPCs sharing common design/performance parameters, letting the manufacturer test only a representative **parent** and extend results to other members (see file 12b Table 2: drag curve and EPMC are skipped for non-parent members).

- **1.1 General**: manufacturer decides family membership subject to the listed criteria; the Approval Authority approves the family; manufacturer provides supporting information.
- **1.2 Special cases**: parameter interactions not listed in 1.4, with strong influence on performance/power consumption, must be identified by the manufacturer and notified — becomes a new-family criterion.
- **1.4 Representativeness**: the Authority may require additional testing/evidence to pick the best-representative parent, or require the manufacturer to split into smaller, more representative families.
- **1.5 Parameters defining a family**:
  - **1.5.1 — must be essentially the same** across all members: (a) electric machine (rotor/stator/windings — dimensions, design, material); (b) inverter (power modules, conductive bars); (c) internal cooling system layout/dimensions/material; (d) internal fans layout/dimension; (e) inverter software basic calibration (temperature models, derating limits, torque path, flux calibration, current control, voltage modulation, sensor-specific calibration only if sensor changed); (f) gear-related parameters (IEPC only, per Annex VI definitions). Changes to (a)–(f) acceptable only with sound engineering rationale that performance/power-consumption is unaffected.
  - **1.5.2 — must be common, with Authority-approved ranges permitted**:
    (a) output shaft interface: any changes allowed;
    (b) end shields: internal design checked for cooling-element/airflow effects; external design (screws, suspension, flange) has no influence if no passive cooling elements removed/changed;
    (c) bearings: changes allowed if number/type unchanged;
    (d) shaft: changes allowed if active/passive cooling unaffected;
    (e) HV connection: position/type changes allowed;
    (f) housing: changes allowed if no passive cooling elements removed/changed;
    (g) sensor: changes allowed if certified performance unchanged;
    (h) inverter housing: changes allowed if no passive cooling or active-parts layout changed;
    (i) inverter HV connection: changes allowed if active-parts/cooling layout unchanged;
    (j) inverter software: all changes not altering the basic EM calibration allowed; **output-power limitation between family members is explicitly allowed**;
    (k) inverter sensor: changes allowed if certified performance unchanged;
    (l) **oil viscosity**: all factory-fill oils' KV at the same temperature ≤ **110%** of the KV used for certification (within the KV100 tolerance band);
    (m) **maximum torque curve**: parent's max-torque curve (4.2.2.4) must be ≥ all other members' at every speed; members within **+40 Nm or +4%** (whichever larger) above the parent are "considered equal";
    (n) **minimum torque curve**: parent's min-torque curve must be ≤ all other members'; within **−40 Nm or −4%** (whichever larger) below the parent are "considered equal";
    (o) **EPMC map coverage**: all members must have ≥**60%** (rounded up) of the parent's EPMC-map points located within their own max/min torque-curve boundaries.
- **1.6 Choice of the parent**: the member with the **highest overall maximum torque** (per 4.2.2).

### B.2 Fuel Cell Systems (►M4)

- **2.1–2.4**: same family-concept structure as EMS/IEPC (manufacturer proposes, Authority approves; representativeness may require extra testing or a smaller family).
- **2.5 Parameters defining an FCS family**:
  - **2.5.1 — must apply to all members**:
    (a) same FCS Type (per Table 9, file 12e);
    (b) fuel cell stack: ±**5%** tolerance for weight & size, ±**2%** for number of cells and cell surface area;
    (c) PCS (if applicable): ±**5%** efficiency;
    (d) air compressor: ±**5%** efficiency;
    (e) humidifier (if applicable): similar layout/dimension;
    (f) pumps (if applicable): similar layout/dimension;
    (g) heat exchangers: similar layout/dimension;
    (h) electrical plugs: any changes allowed;
    (i) piping: any changes allowed;
    (j) media actuators: any changes allowed;
    (k) housing: any changes allowed;
    (l) sensors: changes allowed if the "parent" sensor's precision is still met;
    (m) **minimum OP coverage**: all family members need ≥**8** operating points (per 7.3.4.1) within their individually-declared operating range.
  - Changes to (a)–(l) beyond the above require Authority approval + sound engineering rationale.
- **2.6 Choice of the parent**: the member with the **highest overall effective electric power output**.

---

## PART C — Appendix guide: templates and administrative appendices (summarised)

**Why summarised here**: Appendices 1–7 and 14 are certificate/information-document **blank-form templates** (field lists for manufacturers/authorities to fill in) and a markings/numbering scheme — they contain essentially no calculation methodology of their own (they *reference* the calculation points elsewhere in the Annex). Per the task brief, these are compressed into a purpose-and-key-fields table rather than reproduced field-by-field. Appendices 8–11 and 15 (which **do** contain substantive methodology/defaults/parameter schemas) are instead fully reproduced in file **12h**.

| Appendix | Title | Amendment | Purpose | Key fields / structure |
|---|---|---|---|---|
| **1** | Model of a certificate of a component, separate technical unit or system | ►M3 | The actual **certificate template** issued by a type-approval authority for an EMS/IEPC/IHPC Type 1/battery/capacitor system. Max A4. | Admin stamp; granting/extension/refusal/withdrawal checkbox; certification number; hash; Section I (manufacturer, type, means of ID, marking location/method, addresses); Section II (approval authority, test-report date/number, remarks, signature); attachments = information package + test report. |
| **2** | Information document — electric machine system | ►M3 | The manufacturer's **technical dossier** backing an EMS certificate; defines the data fields that must exist for every parent + family member. | General ID fields (0.1–0.10); **Part 1** essential characteristics table (test voltages, basic/max motor speed, max power/speed, max torque/speed, max 30-min power) **repeated as columns per parent + family member #1/#2/#3…**; electric-machine working-principle fields (DC/AC, phases, excitation, sync/async, rotor type, pole count, rotational inertia); power-controller fields (make, type, control principle, max current/duration, DC voltage range, DC/DC-converter-included flag); cooling-system fields; **"documented values from component testing"**: efficiency figures for CoP (ref. 4.3.5/4.3.6), per-cooling-circuit declared/recorded flow, temperature and power values. Attachment 1 = test-condition info. |
| **3** | Information document — IEPC | ►M3 | Same structure as Appendix 2, **plus** gearbox fields (gear ratios/scheme/powerflow, bearing/shift-element types, gear counts, oil specs/levels/viscosity, per-forward-gear max input torque/power/speed) and differential fields (gear ratio, oil volume/level/spec, bearing/seal types, wheel-end details, planetary/spur gear counts). | As above + §5 Gearbox + §6 Differential + §7 documented test values. Attachment 1 = max tested input speed/torque. |
| **4** | Information document — IHPC Type 1 | ►M3 | Not a standalone template — **explicitly composed of the applicable parts of Appendix 2 (EMS) + Appendix 2 of Annex VI (transmission)**, reflecting the "virtual split" of IHPC Type 1 into two VECTO components (see file 12b §4.4). | Cross-reference only; no new fields defined. |
| **5** | Information document — battery system or representative battery subsystem | ►M3 | Technical dossier for a battery certificate. | General ID; **Part 1**: complete-system-or-subsystem flag; HPBS/HEBS type; cell chemistry; series/parallel cell counts; junction-box/serial-connector-representativeness flags; conditioning-system fields (liquid/air, temp limits, flow rates); **documented test values**: round-trip efficiency for CoP, max charge/discharge current for CoP, testing temperature, per-test-run conditioning power declarations. |
| **6** | Information document — capacitor system or representative capacitor subsystem | ►M3 | Technical dossier for a capacitor certificate. | Mirrors Appendix 5 structure: cell technology/spec, series/parallel counts, conditioning system, testing temperature, conditioning power per test run. |
| **7** | Information document — FCS | ►M4 | Technical dossier for an FCS certificate; **most complex of the templates** — mirrors the BoPC breakdown of Table 9. | General ID + **Part 1** essential characteristics per parent/family member (upper power, weight, dimensions, $U_{out}$/$I_{out}$ ranges, PCS output voltage range, FCS Type A–D); APS fields (compressor make/type/power-uptake range, humidification device); TMS fields (coolant specific heat/density @345K); WTS fields (deionization unit, ion-conductivity); FPS fields (injector/ejector, recirculation blower); FCSS fields (stack make/type, cell count/surface area, reference current/temperature/pressure/stoichiometry/voltage, MEA make/type); PDS/PCS/control-subsystem fields (plug type, DC/DC make/voltage ranges, firmware version). **3 attachments**: (1) FCS test conditions (ambient/oxidant/coolant values, SCOP, all OP targets, PCS voltage levels, optional RTS values); (2) declared in-vehicle operating-boundary-condition table (ambient temp/pressure/humidity, coolant inlet/outlet temp — each with lower/upper bound per OP); (3) **certification test results table** — 25 numbered rows of arithmetic-mean measured values per OP (duration, ARS, REE, setpoint/process-value power & current, fuel mass/volume flow & pressure/temp, air mass/volume flow & pressure/temp/humidity, coolant mass/volume flow & temp in/out, electric power supplied at PDS/PCS) — **with an accompanying sensor-accuracy-type classification table (Type I/II/III, Table 2 of Attachment 3)** defining minimum precision per signal (Type I = Table 1 §3.1 lab-grade accuracy; Type II = integrated/accessible automotive sensors; Type III = best-practice/unspecified). |
| **14** | Markings and numbering | ►M3 (certification-mark letters), with the FCS letter added under ►M4 | Defines the **physical certification mark and certification-number format** that must be affixed to every certified electric powertrain component. | Mark = rectangle around lower-case 'e' + Member-State distinguishing number (full 27-country table reproduced below) + base certification number preceded by the Regulation's sequence number (currently **'02'**) and a **component-type letter**: **M**=electric machine system, **I**=IEPC, **H**=IHPC Type 1, **B**=battery system, **F**=fuel cell system (►M4), **A**=capacitor system. Full certification-number format: `eX*YYYY/YYYY*ZZZZ/ZZZZ*X*00000*00` (country / base Regulation / latest amending Regulation / component-type letter / base certification number / extension number). Marking durability/legibility/visibility requirements also specified (must survive component life, be legible on the installed vehicle, and be on a part not normally replaced). |

**Table 1 of Appendix 14 — Member-State distinguishing numbers** (for the certification mark, full list as given): 1 Germany, 2 France, 3 Italy, 4 Netherlands, 5 Sweden, 6 Belgium, 7 Hungary, 8 Czechia, 9 Spain, 12 Austria, 13 Luxembourg, 17 Finland, 18 Denmark, 19 Romania, 20 Poland, 21 Portugal, 23 Greece, 24 Ireland, 25 Croatia, 26 Slovenia, 27 Slovakia, 29 Estonia, 32 Latvia, 34 Bulgaria, 36 Lithuania, 49 Cyprus, 50 Malta.

**Worked example given in the source (point 1.4.1)**: a mark reading "e12" + "02M00005" = approved in **Austria**, under the Regulation's latest-amendment sequence **02**, for an **electric machine system** (M), with base certification number **00005**.
