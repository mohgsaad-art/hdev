
# Annex Xb — Certification of Electric Powertrain Components
## Part 7: Standard (Default) Values and the Full VECTO Input-Parameter Schema
### ⚠ HIGHEST-ACTIONABILITY FILE for this project — this is the EU's own default electric-powertrain component model (loss maps, battery OCV/DCIR/C-rate defaults, capacitor defaults, FCS efficiency defaults) usable when no physical component test exists, plus the exact XML parameter schema VECTO consumes.

**Source:** Commission Regulation (EU) 2017/2400 (consolidated), CELEX **02017R2400**, consolidation date **01.01.2026**.
**Range covered:** Annex Xb, Appendices 8, 9, 10, 11 and 15 (lines ≈22722–23421 and 24322–24695). Split out from file 12f for length and because this content is substantive calculation methodology/defaults (not blank templates) — see note in 12f.
**Amendment provenance:** Appendix 8 is **►M3** baseline with multiple **►M4** inline refinements (flagged below — mainly step 5 overload-characteristics wording and the step-6(e)(iii) efficiency formula). Appendix 9 is **►M3** with ►M4 inline refinements (equation wording in points (2) and (3)). Appendix 10 is **►M3** baseline with **extensive ►M4 rewriting** of point (1)(b)(d)(e) [battery defaults] and point (2)(d) [capacitor internal-resistance formula] — i.e. Reg. 2025/258 materially revised the 2022 battery/capacitor default-value method, not just added FCS. Appendix 11 (FCS standard values) is **entirely ►M4** (new in 2025, consistent with FCS being newly introduced). Appendix 15 input-parameter tables are **►M3** for EMS/IEPC/Battery/Capacitor (2022) with ►M4 amendments to specific rows (flagged inline); the Fuel cell system parameter tables are **entirely ►M4** (2025).
**OCR caveat:** as in other files — mathematical operators were corrupted by OCR; reconstructed with best engineering judgement, flagged where ambiguous.

---

# APPENDIX 8 — Standard values for electric machine system

Used to generate EMS input data **without physical component testing**, based on UN Regulation No. 85 (Rev. 1) data (the EU/UNECE electric-motor power-measurement regulation) via an 8-step procedure.

**Step 1**: UN Regulation No. 85 applied throughout this Appendix unless stated otherwise.

**Step 2 — Maximum torque vs. speed**: determined from UN R85 §5.3.1.4 data; extended per Annex Xb point 4.3.2 (linear extrapolation to 0 rpm / max operating speed).

**Step 3 — Minimum torque vs. speed**: Step-2 values × **(−1)**.

**Step 4 — Maximum 30-minute continuous torque + corresponding speed**: from UN R85 §5.3.2.3 data, as 30-minute average. If no value derivable (or it is 0 Nm) → set to **0 Nm**, with corresponding speed set to the **rated speed** from Step 2.

**Step 5 — Overload characteristics (►M4)**: from Step-2 data. Overload torque + corresponding speed = average values over the speed range where power ≥ **90%** of max power. If the resulting overload torque is **lower** than the Step-4 continuous torque → overload torque is **set equal to** the Step-4 continuous torque. Overload duration $t_{0\_maxP}$ = whole duration of the Step-2 test run **× 0.25**.

**Step 6 — Electric power consumption map**:
(a) Normalised power-loss map as a function of normalised torque/speed:
$$P_{loss,norm}(T_{norm,i}, \omega_{norm,j}) = \sum_{m,n=0}^{3} k_{mn}\,|T_{norm,i}|^m\,|\omega_{norm,j}|^n$$
— $k$: loss coefficient; $m$: torque-dependent-loss index (0–3); $n$: speed-dependent-loss index (0–3).

(b) Grid points:
- (i) **Normalised speed**: 0.02, 0.20, 0.40, 0.60, 0.80, 1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.20, 2.40, 2.60, 2.80, 3.00, 3.20, 3.40, 3.60, 3.80, 4.00 (extended in 0.2 increments above 4.00 if the EMS's max speed exceeds this normalised range).
- (ii) **Normalised torque**: −1.00, −0.95, −0.90, −0.85, −0.80, −0.75, −0.70, −0.65, −0.60, −0.55, −0.50, −0.45, −0.40, −0.35, −0.30, −0.25, −0.20, −0.15, −0.10, −0.05, −0.01, 0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00.

(c) Loss coefficient $k_{mn}$ tables (two sets — **PSM gets its own table, all other machine types share a second table**):

**(i) PSM**:
| m\n | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 3 | 0 | 0 | 0 | 0 |
| 2 | 0.018 | 0.001 | 0.03 | 0 |
| 1 | 0.0067 | 0 | 0 | 0 |
| 0 | 0 | 0.005 | 0.0025 | 0.003 |

**(ii) All other electric-machine types (ASM, ESM, RM)**:
| m\n | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 3 | 0 | 0 | 0 | 0 |
| 2 | 0.1 | 0.03 | 0.03 | 0 |
| 1 | 0.01 | 0 | 0.001 | 0 |
| 0 | 0.003 | 0 | 0.001 | 0.001 |

(d) Efficiency map from the loss map, at each grid point (same grid as (b)):
- Normalised torque **< 0**:
$$\eta(T_{norm,i},\omega_{norm,j}) = \frac{T_{norm,i}\,\omega_{norm,j} + P_{loss,norm}(T_{norm,i},\omega_{norm,j})}{T_{norm,i}\,\omega_{norm,j}} \times 0.96$$
(if the result is < 0, set η = 0)
- Normalised torque **> 0**:
$$\eta(T_{norm,i},\omega_{norm,j}) = \frac{T_{norm,i}\,\omega_{norm,j}}{T_{norm,i}\,\omega_{norm,j} + P_{loss,norm}(T_{norm,i},\omega_{norm,j})} \times 0.96$$
*(Note the constant 0.96 factor appears in both branches — an explicit flat 4% derating applied to the theoretical loss-based efficiency, likely representing additional losses not captured by the $k_{mn}$ polynomial model, e.g. parasitic/auxiliary losses. Treat 0.96 as a fixed regulatory constant, not an estimate.)*

(e) Actual power-loss map from the efficiency map:
(i) Actual speed: $n_j = \omega_{norm,j} \times n_{rated}$ [1/min] ($n_{rated}$ = rated speed from Step 2).
(ii) Actual torque: $T_i = T_{norm,i} \times T_{max}$ [Nm] ($T_{max}$ = overall max torque from Step 2).
(iii) Actual power loss **(►M4)**:
$$P_{loss}(T_i,n_j) = \left(1-\eta\!\left(\frac{T_i}{T_{max}},\frac{n_j}{n_{rated}}\right)\right)\times |T_i| \times n_j \times \frac{2\pi}{60}$$
(iv) Actual electric inverter power: $P_{el}(T_i,n_j) = P_{loss}(T_i,n_j) + T_i \times n_j \times \dfrac{2\pi}{60}$.

(f) The actual electric power map (e) is extended per Annex Xb point 4.3.4 subpoints (1),(2),(4),(5) (the 0-rpm copy, the ×1.05-speed copy, and the ×1.05-torque-at-constant-efficiency copies — see file 12b §4.3.4).

**Step 7 — Drag curve** from the Step-6(e) power-loss map:
(a) Drag torque at the two grid points defined by normalised torque = **0.01** and normalised speed = **{1.00, 4.00}**:
$$T_{drag} = \frac{-P_{loss}\left(T_i\Big|\tfrac{T_i}{T_{max}}=0.01,\ n_j\Big|\tfrac{n_j}{n_{rated}}=\{1.00,4.00\}\right)}{\frac{2\pi}{60}\times n_j}$$
(b) A third drag-torque value at **0 rpm**, by linear extrapolation from the two Step-7(a) values.
(c) A fourth drag-torque value at the **maximum normalised speed grid point** (per Step 6(b)(i)), by linear extrapolation.

**Step 8 — Rotational inertia** — two allowed options:
(a) **Option 1**: actual rotational inertia from the rotor's geometric form and material densities (CAD-tool methods permitted); detailed method agreed with the type-approval authority.
(b) **Option 2**: from the rotor's outer dimensions — fit a **hollow cylinder** where: (i) outer diameter = the rotor point with the largest radial distance from the rotation axis; (ii) inner diameter = the rotor point with the smallest radial distance; (iii) length = the distance between the two furthest-apart points measured parallel to the rotation axis. Inertia of this hollow cylinder calculated using a **material density of 7 850 kg/m³** (standard steel density).

---

# APPENDIX 9 — Standard values for IEPC

Extends Appendix 8 to a full IEPC (EM + optional gearbox + optional differential). Condition: where >1 electric machine is part of the IEPC, **all must have identical specs**, connected at the same reference position (upstream or downstream of gearbox), running at the same speed at that position with torque/power **summed via a summation gearbox**.

### Two options for generating IEPC input data:

**Option 1 — standard values for ALL components**:
(a) EMS standard values per Appendix 8 for a **single** machine; if multiple identical machines, **multiply all torque/power figures (mechanical + electrical) and the rotational inertia by the number of machines**. Use these multiplied values for all further steps.
(b) **Gearbox** (if included): standard values determined **per forward gear** for the electric power consumption map, but **only for the gear closest to ratio 1** for all other input data:
  (i) gearbox losses per Appendix 9 point (2) below;
  (ii) EM output shaft speed/torque treated as gearbox input shaft speed/torque;
  (iii) convert torque to gearbox output shaft **(►M4)**:
  $$T_{i,GBX} = \left(T_{i,EM} - T_{i,l,in}(n_{j,EM}, T_{i,EM}, gear)\right) \times i_{gear}$$
  (iv) convert speed to gearbox output shaft: $n_{j,GBX} = n_{j,EM} / i_{gear}$.
(c) **Differential** (if included): standard values per forward gear for the electric power map, only the ratio-closest-to-1 gear for other data:
  (i) differential losses per Appendix 9 point (3) below;
  (ii) gearbox-output (or EM-output if no gearbox) torque points used as differential-input torque;
  (iii) convert torque to differential output:
  $$T_{i,diff,out} = \left(T_{i,diff,in} - T_{i,diff,l,in}(T_{i,diff,in})\right) \times i_{diff}$$
  (iv) convert speed to differential output: $n_{j,diff,out} = n_{j,diff,in} / i_{diff}$.

**Option 2 — measure the EM, standard values for the rest**:
(a) EMS component data **measured** per Annex Xb point 4 (file 12b); if multiple identical machines, multiply torque/power/inertia figures by the machine count, as in Option 1(a).
(b)/(c) Gearbox/differential standard values exactly as Option 1(b)/(c), substituting the measured EM data as the basis.

### (2) IEPC internal component: gearbox losses (►M4)
$$T_{gbx,l,in}(n_{in}, T_{in}, gear) = T_{d0} + T_{d1000}\times\frac{n_{in}}{1000\,\text{rpm}} + f_{T,gear}\times|T_{in}|$$
— $T_{gbx,l,in}$: torque loss at input shaft [Nm]; $T_{dx}$: drag torque at x rpm [Nm]; $n_{in}$: input-shaft speed [rpm]; $f_{T,gear}$: gear-dependent torque-loss coefficient [–]; $T_{in}$: input-shaft torque [Nm]; $gear$ = 1…highest gear number.

- (b) Applied to all transmission gears downstream of the EM output shaft.
- (c) If a differential is included: applied to all gears downstream of the EM output shaft and upstream of (excluding) the gear mesh with the differential input gear (external-external spur/bevel mesh, or a single planetary gearset).
- (d) Wheel-hub motors: applied to all gears downstream of the EM output shaft and upstream of the wheel hub.
- (e) $f_T$ determined per **Annex VI paragraph 3.1.1**.
- (f) $f_T = \mathbf{0.007}$ for a **direct gear**.
- (g) $T_{d0}$ and $T_{d1000}$ = **0.0075 × $T_{max,in}$** for gearboxes with **more than 2 friction shift clutches**.
- (h) $T_{d0}$ and $T_{d1000}$ = **0.0025 × $T_{max,in}$** for all other gearboxes.
- (i) $T_{max,in}$ = overall max value of all individual max-allowed input torques across the gearbox's forward gears [Nm].

### (3) IEPC internal component: differential losses (►M4)
$$T_{diff,l,in}(T_{in}) = \eta_{diff}\times\frac{T_{diff,d0}}{i_{diff}} + (1-\eta_{diff})\times|T_{in}|$$
— $T_{diff,l,in}$: torque loss at differential input [Nm]; $T_{diff,d0}$: drag torque [Nm]; $\eta_{diff}$: torque-dependent efficiency [–]; $T_{in}$: input torque [Nm]; $i_{diff}$: differential gear ratio [–].

- (b) Applied to all differential gear meshes, including the input-gear mesh.
- (c) $\eta_{diff}$ determined per **Annex VI paragraph 3.1.1**, where $\eta_m$ = **0.98** for a **bevel gear mesh**.
- (d) Differential-internal-gear losses are **ignored** for (b)–(c).
- (e) **Bevel gear mesh at the differential crown gear**: $T_{diff,d0} = 25\ \text{Nm} + 15\ \text{Nm} \times i_{diff}$.
- (f) **Spur gear mesh or single planetary gearset at the differential input gear**: $T_{diff,d0} = 25\ \text{Nm} + 5\ \text{Nm} \times i_{diff}$.

---

# APPENDIX 10 — Standard values for REESS (Battery and Capacitor)

### (1) Battery system or representative battery subsystem

(a) **Battery-type determination**: HEBS/HPBS classification from the ratio of (max. current in A, per UN Reg. No. 100 Annex 6 Appendix 2 point 1.4.4) to (capacity in Ah, per point 1.4.3): **HEBS if ratio < 10; HPBS if ratio ≥ 10.**

(b) **(►M4) Rated capacity**: Ah value from the **cell manufacturer's datasheet** single-cell capacity, scaled by the parallel/series arrangement, **then multiplied by a factor of 0.9** (a 10% derating of nameplate cell capacity to arrive at the usable system-level rated capacity default).

(c) **OCV vs. SOC**, from nominal voltage $V_{nom}$ (UN Reg. No. 100 Annex 6 Appendix 2 point 1.4.1):

| SOC [%] | OCV [V] |
|---|---|
| 0 | 0.88 × $V_{nom}$ |
| 10 | 0.94 × $V_{nom}$ |
| 50 | 1.00 × $V_{nom}$ |
| 90 | 1.06 × $V_{nom}$ |
| 100 | 1.12 × $V_{nom}$ |

(d) **(►M4) DCIR defaults** — calculated by dividing a fixed specific resistance [mOhm×Ah] by the rated capacity [Ah] (per (b)), then multiplying by the number of series-connected cells (per UN Reg. No. 100 Annex 6 Appendix 2 point 1.3.2):

**(i) HPBS**:
| DCIR | Specific resistance [mOhm × Ah] |
|---|---|
| RI2 | 40 |
| RI10 | 45 |
| RI20 | 50 |

**(ii) HEBS**:
| DCIR | Specific resistance [mOhm × Ah] |
|---|---|
| RI2 | 210 |
| RI10 | 240 |
| RI20 | 270 |
| RI120 | 390 |

(e) **(►M4) Max charge/discharge current defaults**, as C-rates (nC) vs. SOC:

**HPBS**:
| SOC [%] | C-rate — max charging | C-rate — max discharging |
|---|---|---|
| 0 | 9.0 | 0.0 |
| 30 | 9.0 | 50.0 |
| 80 | 9.0 | 50.0 |
| 100 | 0.0 | 50.0 |

**HEBS**:
| SOC [%] | C-rate — max charging | C-rate — max discharging |
|---|---|---|
| 0 | 0.9 | 0.0 |
| 30 | 0.9 | 5.0 |
| 80 | 0.9 | 5.0 |
| 100 | 0.0 | 5.0 |

Absolute values used as final for both charge and discharge current.

### (2) Capacitor system or representative capacitor subsystem (►M4)

(a) **Capacitance**: rated capacitance from the capacitor-system/subsystem datasheet (may be scaled up from a single cell's rated capacitance per the series/parallel arrangement).

(b) **Maximum voltage ($V_{max,Cap}$)**: rated voltage from the datasheet (may be scaled up from a single cell per the series/parallel arrangement).

(c) **Minimum voltage ($V_{min,Cap}$)**: $V_{max,Cap} \times \mathbf{0.45}$.

(d) **Internal resistance**:
$$R_{I,Cap} = R_{I,ref} \times \frac{V_{max,Cap} - V_{min,Cap}}{0.55 \times V_{ref}} \times \frac{C_{ref}}{C_{Cap}} \times \frac{1}{n_{ser}}$$
— $R_{I,ref} = \mathbf{0.00375\ \Omega}$ (reference internal resistance); $V_{ref} = \mathbf{2.7\ V}$ (reference max voltage); $C_{ref} = \mathbf{3000\ F}$ (reference capacitance); $C_{Cap}$: capacitance per (a) [F]; $n_{ser}$: number of series-connected cells per (a) [–].

(e) **Max charge/discharge current**: $C_{Cap}$ [F] × **5.0 A/F**; absolute value used for both.

---

# APPENDIX 11 — Standard values for FCS (►M4, entirely new 2025 methodology)

(a) FCS input data (per Appendix 15) based on the **maximum electrical power output** of the FCS, per **UN Regulation No. 100, Annex 6, Appendix 1, point 4.6**.

(b) If more than one FCS is installed in the vehicle, (a) is declared **and defaulted separately per individual FCS**, per the corresponding required input in Table 11a of Annex III to this Regulation (outside the assigned extraction range).

(c) Fuel-mass-flow vs. electrical-power-output defaults, via a **generic efficiency table**:

| Normalized power [-] | Efficiency [%] |
|---|---|
| 0.01 | 3.67 |
| 0.05 | 18.33 |
| 0.10 | 36.67 |
| 0.125 | 45.83 |
| 0.15 | 55.00 |
| 0.20 | 54.12 |
| 0.25 | 53.24 |
| 0.30 | 52.35 |
| 0.35 | 51.47 |
| 0.40 | 50.59 |
| 0.45 | 49.71 |
| 0.50 | 48.82 |
| 0.55 | 47.94 |
| 0.60 | 47.06 |
| 0.65 | 46.18 |
| 0.70 | 45.29 |
| 0.75 | 44.41 |
| 0.80 | 43.53 |
| 0.85 | 42.65 |
| 0.90 | 41.76 |
| 0.95 | 40.88 |
| 1.00 | 40.00 |

*(Note the striking non-monotonic shape: efficiency **peaks sharply around 15% normalized power (55.00%)**, then **drops and declines steadily** from 20% to 100% power (54.12% → 40.00%). This matches well-known hydrogen PEM fuel-cell behaviour — efficiency peaks at low partial load and falls off toward rated power — and is transcribed exactly as given; it is a genuine regulatory default curve shape, not a transcription artefact, though the very sharp jump between 0.125→0.55% and 0.15→0.20 (55.00%→54.12%) exactly at the boundary is worth independently cross-checking against the original PDF if this default table is implemented.)*

(d) Fuel mass flow and corresponding electrical power output:
$$\dot m_{fuel} = \frac{P_{rated,el} \times P_{norm,i}}{eta_i \times 100} \times 3600\,\text{s/h} \Big/ NCV_{std,H2}\,\text{[kJ/g]}$$
$$P_{FCS,el,i} = P_{rated,el} \times P_{norm,i}$$
— $\dot m_{fuel}$: fuel mass flow [g/h]; $P_{rated,el}$: max. electrical power output per (a) [kW]; $P_{norm,i}$: normalized electrical power output per (c) [-]; $eta_i$: efficiency per (c) corresponding to $P_{norm,i}$ [%]; $NCV_{std,H2}$: standard net calorific value of hydrogen per point 5.3.3.1 [MJ/kg]; $P_{FCS,el,i}$: electrical power output [kW].

---

# APPENDIX 15 — Input parameters for the simulation tool (the full VECTO XML schema for electric powertrain components)

Describes every parameter a component manufacturer must supply as VECTO input. The actual XML schema + example data live on a "dedicated electronic distribution platform" (not part of the Regulation text itself).

**Data types used**: `string`/`token` (ISO8859-1 character sequences; token = no leading/trailing whitespace), `date` (`YYYY-MM-DDTHH:MM:SSZ` UTC), `integer` (no leading zeros), `double, X` (exactly X digits after the decimal comma, no leading zeros — e.g. `double,2` → "2345,67"; `double,4` → "45,6780"; **note: decimal comma, not point, per EU convention**), `unit` = physical unit.

## Electric machine system — Tables 1–6

**Table 1 — General** (parameter IDs P450–P466):

| Parameter | ID | Type | Unit | Notes |
|---|---|---|---|---|
| Manufacturer | P450 | token | - | |
| Model | P451 | token | - | |
| CertificationNumber | P452 | token | - | |
| Date | P453 | dateTime | - | date/time the component-hash is created |
| AppVersion | P454 | token | - | tool/version used for evaluating measured data |
| ElectricMachineType | P455 | string | - | 'ASM', 'ESM', 'PSM', 'RM' |
| CertificationMethod | P456 | string | - | ►M4: 'Measured', 'Standard values' |
| R85RatedPower | P457 | integer | W | per UN Reg. No 85 Annex 2 §1.9 |
| RotationalInertia | P458 | double,2 | kgm² | per Appendix 8 point 8 |
| DcDcConverterIncluded | P465 | boolean | - | ►M4: true if a DC/DC converter is part of the EMS (point 4.1); **always true** if CertificationMethod='Standard values' |
| IHPCType | P466 | string | - | 'None', 'IHPC Type 1' |

**Table 2 — VoltageLevels** (per voltage level measured; P459–P463, P467):

| Parameter | ID | Type | Unit |
|---|---|---|---|
| VoltageLevel | P467 | integer | V (no input if 'Standard values') |
| ContinuousTorque | P459 | double,2 | Nm |
| TestSpeedContinuousTorque | P460 | double,2 | 1/min |
| OverloadTorque | P461 | double,2 | Nm |
| TestSpeedOverloadTorque | P462 | double,2 | 1/min |
| OverloadDuration | P463 | double,2 | s |

**Table 3 — MaxMinTorque** (per operating point, per voltage level; P468–P470): `OutputShaftSpeed` [1/min], `MaxTorque` [Nm], `MinTorque` [Nm].

**Table 4 — DragTorque** (per operating point; P471–P472): `OutputShaftSpeed` [1/min], `DragTorque` [Nm].

**Table 5 — ElectricPowerMap** (per operating point, per voltage level; **+ per forward gear if IHPC Type 1**; P473–P475): `OutputShaftSpeed` [1/min], `Torque` [Nm], `ElectricPower` [W].

**Table 6 — Conditioning** (per cooling circuit with external heat exchanger; no input if 'Standard values'; P476–P477): `CoolantTempInlet` [°C] and `CoolingPower` [W] (►M4: both specified as the average over both voltage levels, per points 4.1.5.1/4.3.6).

## IEPC — Tables 1–7 (P478–P510, P565)

**Table 1 — General**: same P478–P486 pattern as EMS (Manufacturer/Model/CertificationNumber/Date/AppVersion/ElectricMachineType/R85RatedPower/RotationalInertia), plus `CertificationMethod` (P484: 'Measured for complete component' / 'Measured for EM and standard values for other components' / 'Standard values for all components'), `DifferentialIncluded` (P493, boolean), `DesignTypeWheelMotor` (P494, boolean), `NrOfDesignTypeWheelMotorMeasured` (P495, integer, allowed '1'/'2'), and **(►M4) `DisengagementClutch`** (P565, boolean — true if the IEPC has a functionality that actively/mechanically disconnects all EMs from the rest of the powertrain under certain conditions, possibly further downstream including some gearing).

**Table 2 — Gears** (per forward gear; P496–P499): `GearNumber`, `Ratio` [double,3, EM rotor speed / IEPC output shaft speed], `MaxOutputShaftTorque` (optional; ►M4: for wheel-motor type, must correspond to the measured configuration — double if two components were measured vs. one), `MaxOutputShaftSpeed` (optional).

**Table 3 — VoltageLevels**: same structure as EMS Table 2 (P487–P491, P500).

**Table 4 — MaxMinTorque** (per OP, per voltage level, **per forward gear measured** — optional gear-dependent per 4.2.2(c)): P501–P503.

**Table 5 — DragTorque** (per OP, per forward gear measured — optional per 4.2.3): P504–P505.

**Table 6 — ElectricPowerMap** (per OP, per voltage level, per forward gear): P506–P508.

**Table 7 — Conditioning**: same structure as EMS Table 6: P509–P510.

## Battery system — Tables 1–4 (P511–P531, P516/P517/P521)

**Table 1 — General**:

| Parameter | ID | Type | Unit | Notes |
|---|---|---|---|---|
| Manufacturer | P511 | token | - | |
| Model | P512 | token | - | |
| CertificationNumber | P513 | token | - | |
| Date | P514 | dateTime | - | |
| AppVersion | P515 | token | - | |
| CertificationMethod | P517 | string | - | 'Measured', 'Standard values' |
| BatteryType | P518 | string | - | 'HPBS', 'HEBS' |
| RatedCapacity | P519 | double,2 | Ah | ►M4: if 'Standard values', per Appendix 10(1)(b) |
| ConnectorsSubsystemsIncluded | P520 | boolean | - | representative cable harness included (always true if full system tested) |
| JunctionboxIncluded | P516 | boolean | - | (►M4 renumbered) representative junction box w/ shut-off + fuses included (always true if full system tested) |
| TestingTemperature | P521 | integer | °C | per 5.1.4; no input if 'Standard values' |

**Table 2 — OCV** (per SOC level measured; P522–P523): `SOC` [%], `OCV` [V].

**Table 3 — DCIR** (per SOC level measured; P524–P528): `SOC` [%] (for 'Standard values', same DCIR provided at SOC=0% and SOC=100%), `DCIR RI2` (P525), `DCIR RI10` (P526), `DCIR RI20` (P527) — all [mOhm], per Appendix 10(1)(d) if standard values; `DCIR RI120` (P528) — optional, **HEBS only**.

**Table 4 — Current limits** (per SOC level measured; P529–P531): `SOC` [%], `MaxChargingCurrent` [A] (►M4: per Appendix 10(1)(e) if standard, positive sign), `MaxDischargingCurrent` [A] (same).

## Capacitor system — Table 1 (P532–P544, P537)

| Parameter | ID | Type | Unit | Notes |
|---|---|---|---|---|
| Manufacturer | P532 | token | - | |
| Model | P533 | token | - | |
| CertificationNumber | P534 | token | - | |
| Date | P535 | dateTime | - | |
| AppVersion | P536 | token | - | |
| CertificationMethod | P538 | string | - | ►M4: 'Measured', 'Standard values' |
| Capacitance | P539 | double,2 | F | |
| InternalResistance | P540 | double,2 | Ohm (►M4: unit changed to **mOhm**) | |
| MinVoltage | P541 | double,2 | V | |
| MaxVoltage | P542 | double,2 | V | |
| MaxChargingCurrent | P543 | double,2 | A | |
| MaxDischargingCurrent | P544 | double,2 | A | |
| TestingTemperature | P537 | integer | °C | per 6.1.3; no input if 'Standard values' |

## Fuel cell system — Tables 1–2 (P566–P574) (►M4, entirely new)

**Table 1 — General**:

| Parameter | ID | Type | Unit | Notes |
|---|---|---|---|---|
| Manufacturer | P566 | token | - | |
| Model | P567 | token | - | |
| CertificationNumber | P568 | token | - | |
| Date | P569 | dateTime | - | |
| AppVersion | P570 | token | - | |
| CertificationMethod | P571 | string | - | 'Measured', 'Standard values' |
| FCSRatedPower | P572 | integer | kW | per UN Reg. No 100 Annex 6 Appendix 1 §4.6 |

**Table 2 — FuelMap** (per operating point measured; P573–P574): `OutputPower` [kW, double,2 — electric power from the FCS, per 7.5.3], `FuelConsumption` [g/h, double,2 — fuel mass flow, per 7.5.3].

---

## Reference footnotes carried from the source (apply across Appendices 8–15)
- (*) "determined in accordance with points 4.3.5 and 4.3.6 of this Annex"
- (**) "determined in accordance with points 5.4.1.4 of this Annex"
- (***) **UN Regulation No. 100** of the UNECE — *"Uniform provisions concerning the approval of vehicles with regard to specific requirements for the electric powertrain"* (OJ L449, 15.12.2021, p.1). This is the cross-referenced external regulation that supplies the nameplate cell/pack data (voltage, capacity, current, cell counts) used throughout Appendix 10's battery/capacitor default-value method.

---

## Direct implications for the HDEV sizing/modelling tool

1. **This is the EU's own reference default component model.** Any time the project needs a physically-plausible, legally-sourced (not "made up") default for an e-motor loss map, battery internal resistance/OCV curve, capacitor R/C, or FCS efficiency curve — in the absence of an actual manufacturer datasheet/certificate — these Appendix 8–11 formulas are the authoritative, citable source, not a rough estimate.
2. **Parameter IDs (P450–P574)** give the project a ready-made, legally-defined schema to mirror or import against if the tool ever needs to read/write actual VECTO component XML files (e.g. for round-tripping manufacturer-supplied certified component data).
3. **The HPBS/HEBS split (file 12a §2.6) is the single most important branch point** for any battery model in this tool — C-rate defaults differ by roughly an order of magnitude between the two types (e.g. max discharge C-rate default: 50C for HPBS vs. 5C for HEBS at 80%/30% SOC).
4. **The FCS efficiency-vs-power default curve (Appendix 11(c))** — peaking near 15% load and declining toward rated power — is a legally-sourced, citable starting point for any hydrogen fuel-cell efficiency assumption in the tool, rather than an invented curve shape.
