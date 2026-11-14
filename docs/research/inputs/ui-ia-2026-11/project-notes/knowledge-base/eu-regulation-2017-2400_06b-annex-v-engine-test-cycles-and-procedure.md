# Commission Regulation (EU) 2017/2400 — Annex V: Verifying Engine Data
## Part B — Testing Procedure: Test Runs, Cycles (WHTC/WHSC/FCMC), Setpoint Grid, Test Sequence & Validity of Data

**CELEX number:** 02017R2400
**Consolidated text date:** 01.01.2026 (consolidation version 007.001)
**Covers:** Annex V, point 4 "Testing procedure" in full (points 4.1 to 4.3.5.7.2) (OCR source lines ~5587–6178)
**Amendment markers:** ▼B = original 2017 baseline; ▼M1 = Reg (EU) 2019/318; ▼M3 = Reg (EU) 2022/1379; ▼M4 = Reg (EU) 2025/258

> See Part A (`06a-...md`) for the status note on this Annex being the current legally-binding engine test procedure (superseding the 2014/2017 draft VECTO technical reports), and the HDEV-relevance flag (ICE/dual-fuel/H2-ICE only, not applicable to BEV powertrains directly).

---

## 4. Testing procedure ▼B

All measurement data determined per **Annex 4 to UN Regulation No. 49**, unless this Annex states otherwise. ▼M3

### 4.1 Overview of test runs to be performed

**Table 3** gives the overview of all test runs required for certifying one engine CO2-family (Appendix 3).

The **fuel consumption mapping cycle (FCMC)** (point 4.3.5) and the **engine motoring curve** (point 4.3.2) are **omitted** for all engines in the family **except the CO2-parent engine**.

If, at the manufacturer's request, Article 15(5) provisions are applied, the FCMC and motoring-curve recording must be performed **additionally** for that specific engine.

**Table 3 — Overview of test runs to be performed**

| Test run | Reference to paragraph | Required for CO2-parent engine | Required for other engines within CO2-family |
|---|---|---|---|
| Engine full load curve | 4.3.1 | yes | yes |
| Engine motoring curve | 4.3.2 | yes | no |
| WHTC test | 4.3.3 | yes | yes |
| WHSC test | 4.3.4 | yes | yes |
| Fuel consumption mapping cycle | 4.3.5 | yes | no |

### 4.2 Allowed changes to the engine system ▼B

Changing the **target value of the engine idle-speed controller** to a lower value in the ECU is allowed for all test runs involving idle operation, to prevent interference between the engine idle-speed controller and the test-bed speed controller.

**4.2.1 Dual-fuel engines ▼M3:** must operate in **dual-fuel mode** during all test runs in point 4.3. If a switch to service mode occurs during a test run, all recorded data for that run is **void**.

### 4.3 Test runs ▼B

#### 4.3.1 Engine full load curve

Recorded per points 7.4.1–7.4.5 of Annex 4 to UN R49. ▼M3

#### 4.3.2 Engine motoring curve

Omitted for all engines except the CO2-parent engine (Appendix 3). Per point 6.1.3 (Part C), the CO2-parent engine's motoring curve applies to **all** engines in the same CO2-family. If Article 15(5) is invoked, the motoring curve must additionally be recorded for that specific engine.

Recorded per **option (b)** in point 7.4.7 of Annex 4 to UN R49 ▼M3 — determines the **negative torque** required to motor the engine between maximum and minimum mapping speed with minimum operator demand.

The test continues directly after the full-load-curve mapping (4.3.1). At the manufacturer's request it may be recorded separately; in that case the engine-oil temperature at the end of the full-load-curve run must be recorded, and the manufacturer must demonstrate to the approval authority that the oil temperature at the start of the motoring-curve run is within **± 2 K** of that value.

**Procedure:** at the start, engine operated at minimum operator demand at **maximum mapping speed** (point 7.4.3 of Annex 4 to UN R49). Once the motoring-torque value has stabilised within **± 5%** of its mean for ≥10 s, data recording starts; engine speed is then decreased at an average rate of **8 ± 1 min⁻¹/s** from maximum to minimum mapping speed (point 7.4.3 of Annex 4 to UN R49). ▼M3

**4.3.2.1 Special requirements for WHR systems:** for **WHR_mech**/**WHR_elec** systems, data recording for the motoring curve must not start before the mechanical/electrical power reading has stabilised within **± 10%** of its mean for ≥10 s.

#### 4.3.3 WHTC test

Performed per Annex 4 to UN R49. Weighted emission results must meet the limits in **Regulation (EC) No 595/2009**. Dual-fuel engines must meet the limits in point 5 of Annex XVIII to Regulation (EU) No 582/2011. The full-load curve (4.3.1) is used to **denormalise** the reference cycle and compute reference values per points 7.4.6/7.4.7/7.4.8 of Annex 4 to UN R49.

**4.3.3.1 Measurement signals and data recording:** in addition to Annex 4 to UN R49 requirements, record the actual fuel mass flow (point 3.4) and the data referred to in point 4.3.5.3(5)(a) (below) applied to the WHTC test. ▼M4

**4.3.3.2 Special requirements for WHR systems ▼M3:** record mechanical P_WHR_net (WHR_mech) or electrical P_WHR_net (WHR_elec) per point 3.1.6.

#### 4.3.4 WHSC test

Performed per Annex 4 to UN R49; emission results must meet limits in Regulation (EC) No 595/2009. Dual-fuel engines: limits per point 5 of Annex XVIII to Regulation (EU) No 582/2011. Full-load curve (4.3.1) used for denormalisation / reference-value calculation per points 7.4.6/7.4.7/7.4.8 of Annex 4 to UN R49.

**4.3.4.1 Measurement signals and data recording:** as 4.3.3.1, applied to the WHSC test. ▼M4

**4.3.4.2 Special requirements for WHR systems ▼M3:** as 4.3.3.2, applied to the WHSC test.

#### 4.3.5 Fuel consumption mapping cycle (FCMC) ▼M3

Omitted for all engines except the CO2-parent engine. The fuel-map data recorded for the CO2-parent engine applies to **all** engines in the family. If Article 15(5) is invoked, FCMC is performed additionally for that specific engine.

The engine fuel map is measured over a series of **steady-state engine operation points** (grid defined in 4.3.5.2). Metrics: **fuel consumption [g/h]** as a function of **engine speed [min⁻¹]** and **engine torque [Nm]**.

##### 4.3.5.1 Handling of interruptions during the FCMC

- If an **after-treatment regeneration event** occurs during the FCMC (for engines with periodically-regenerated systems per point 6.6 of Annex 4 to UN R49 ▼M3): all measurements at that engine-speed mode are void; the regeneration event is completed, then the procedure continues per **4.3.5.1.1**.
- If an **unexpected interruption/malfunction/error** occurs: all measurements at that speed mode are void, and the manufacturer chooses either:
  1. continue per **4.3.5.1.1**, or
  2. repeat the **whole** FCMC per points 4.3.5.4 and 4.3.5.5.

##### 4.3.5.1.1 Provisions for continuing the FCMC

Engine started and warmed up per point 7.4.1 of Annex 4 to UN R49 ▼M3. After warm-up, engine preconditioned for **20 minutes at mode 9** (Table 1 of point 7.2.2 of Annex 4 to UN R49). The full-load curve (4.3.1) is used to denormalise mode-9 reference values per points 7.4.6/7.4.7/7.4.8 of Annex 4 to UN R49.

Directly after preconditioning, target engine-speed and torque change **linearly within 20–46 s** to the **highest target torque setpoint** at the next **higher** target engine-speed setpoint than the one where the interruption occurred (remaining time up to 46 s used for stabilisation if reached sooner). Engine operation continues from that point per the 4.3.5.5 test sequence, **without recording**. When the highest target torque setpoint at the particular target speed where the interruption occurred is reached, recording **resumes** per the 4.3.5.5 sequence.

##### 4.3.5.2 Grid of target setpoints

Fixed normalised grid: **10 target engine-speed setpoints × 11 target torque setpoints**. Conversion from normalised to actual values is based on the **CO2-parent engine's full-load curve** (Appendix 3; recorded per 4.3.1).

###### 4.3.5.2.1 Definition of target engine speed setpoints

10 target speed setpoints = **4 base** + **6 additional**.

Characteristic engine speeds `nidle`, `nlo`, `npref`, `n95h`, `nhi` determined from the CO2-parent engine's full-load curve, applying the definitions in point 7.4.6 of Annex 4 to UN R49.

**n57** determined by:
> **n57 = 0.565 × (0.45 × nlo + 0.45 × npref + 0.1 × nhi − nidle) × 2.0327 + nidle**
>
> *(Transcribed exactly as extracted from the source text. The combination of coefficients 0.565 and 2.0327 is unusual and could not be cross-checked against the original PDF's rendered equation — OCR of mathematical notation elsewhere in this Annex is known to be unreliable (see Part C, point 5.1, for a clearer example of OCR corruption). Verify this exact formula against the official PDF or a verified secondary source before relying on it in code.)*

**4 base target engine speed setpoints:**
1. Base engine speed 1: **nidle**
2. Base engine speed 2: **nA = n57 − 0.05 × (n95h − nidle)**
3. Base engine speed 3: **nB = n57 + 0.08 × (n95h − nidle)**
4. Base engine speed 4: **n95h**

**Potential distances between speed setpoints:**
1. dnidleA_44 = (nA − nidle) / 4
2. dnB95h_44 = (n95h − nB) / 4
3. dnidleA_35 = (nA − nidle) / 3
4. dnB95h_35 = (n95h − nB) / 5
5. dnidleA_53 = (nA − nidle) / 5
6. dnB95h_53 = (n95h − nB) / 3

**Absolute deviations between the two sections:**
1. dn44 = ABS(dnidleA_44 − dnB95h_44)
2. dn35 = ABS(dnidleA_35 − dnB95h_35)
3. dn53 = ABS(dnidleA_53 − dnB95h_53)

**6 additional target engine speed setpoints** (▼M1), determined by:
1. If **dn44 ≤ (dn35 + 5)** AND **dn44 ≤ (dn53 + 5)**: divide range `nidle→nA` into **4** equidistant sections and range `nB→n95h` into **4** equidistant sections.
2. If **(dn35 + 5) < dn44** AND **dn35 < dn53**: divide `nidle→nA` into **3** sections and `nB→n95h` into **5** sections.
3. If **(dn53 + 5) < dn44** AND **dn53 < dn35**: divide `nidle→nA` into **5** sections and `nB→n95h` into **3** sections.

*Figure 1 — "Definition of speed setpoints" [Figure referenced in source but not visually extracted from this text-only OCR] — exemplarily illustrates case (1) above.*

###### 4.3.5.2.2 Definition of target torque setpoints

11 target torque setpoints = **2 base** + **9 additional**.

- **2 base torque setpoints:** zero engine torque and the CO2-parent engine's **maximum full-load torque (Tmax_overall)** (4.3.1).
- **9 additional torque setpoints:** dividing the range zero → `Tmax_overall` into **10 equidistant sections**.

**▼M1/▼M3:** At a particular target engine-speed setpoint, any target torque setpoint that **exceeds** the full-load torque value (from the full-load curve, 4.3.1) at that speed **minus 5% of Tmax_overall** is **replaced** by a single target torque setpoint at the full-load torque for that speed. Each such replacement setpoint is measured **only once** during the FCMC sequence (4.3.5.5).

*Figure 2 — "Definition of torque setpoints" [Figure referenced in source but not visually extracted from this text-only OCR].*

##### 4.3.5.3 Measurement signals and data recording

Recorded data:
1. Engine speed
2. Engine torque, corrected per point 3.1.2
3. Fuel mass flow consumed by the whole engine system per point 3.4
4. Gaseous pollutants per UN Regulation No. 49 definitions ▼M3 (particulate pollutants, methane and ammonia emissions **not required** to be monitored during the FCMC run)
5. **▼M4 — if the test engine has an OBFCM device (point 3.1.2):**
   - (a) the information in points 8.13.15.3–8.13.15.8 of Annex Xa;
   - (b) for each fuel-mass-flow data point (item 3), the OBFCM instantaneous engine fuel-rate value per point 5.13 of Annex Xa;
   - (c) the time intervals between the fuel-mass-flow data points (item 3).

Gaseous-pollutant measurement per points 7.5.1, 7.5.2, 7.5.3, 7.5.5, 7.7.4, 7.8.1, 7.8.2, 7.8.4 and 7.8.5 of Annex 4 to UN R49. For point 7.8.4 of Annex 4 to UN R49, "test cycle" in that paragraph means the **complete sequence** from preconditioning (4.3.5.4) to the end of the test sequence (4.3.5.5).

**4.3.5.3.1 Special requirements for WHR systems:** record mechanical P_WHR_net (WHR_mech) or electrical P_WHR_net (WHR_elec) per point 3.1.6.

##### 4.3.5.4 Preconditioning of the engine system

Dilution system (if applicable) and engine started/warmed up per point 7.4.1 of Annex 4 to UN R49 ▼M3. After warm-up, engine + sampling system preconditioned for **20 minutes at mode 9** (Table 1 of point 7.2.2 of Annex 4 to UN R49) while the dilution system runs simultaneously. The CO2-parent engine's full-load curve (4.3.1) denormalises mode-9 reference values per points 7.4.6/7.4.7/7.4.8 of Annex 4 to UN R49. ▼M3

Directly after preconditioning, target speed/torque change **linearly within 20–46 s** to match the first target setpoint of the test sequence (4.3.5.5); remaining time up to 46 s used for stabilisation if reached sooner.

##### 4.3.5.5 Test sequence

Steady-state target setpoints (defined speed/torque per 4.3.5.2) with defined ramps between them. The **highest target torque setpoint at each target engine speed** is operated at **maximum operator demand**. The **first** target setpoint is the **highest target speed** and **highest target torque**.

**Steps to cover all target setpoints:**

1. Engine operated **95 ± 3 s** at each target setpoint:
   - First **55 ± 1 s** = stabilisation period.
   - **▼M3:** following **30 ± 1 s**, engine controlled as:
     - (a) Engine-speed mean value held at the target speed within **± 1%** of the highest target engine speed.
     - (b) Except full-load points: engine-torque mean value held at the target torque within **± 20 Nm or ± 2% of Tmax_overall**, whichever is **greater**.
   - **▼M3:** recorded values (4.3.5.3) stored as the **averaged value over the 30 ± 1 s** period. Remaining **10 ± 1 s** may be used for data post-processing/storage; target setpoint held throughout.
2. After one setpoint's measurement is complete: target speed held constant within **± 20 min⁻¹**; target torque decreased **linearly within 20 ± 1 s** to the next lower target torque setpoint. Measurement then per subpoint (1).
3. **▼M3:** After the **zero-torque** setpoint is measured (subpoint 1): target speed decreased linearly to the next lower target speed setpoint while operator demand simultaneously increases linearly to maximum, **within 20–46 s** (remaining time to 46 s for stabilisation if reached sooner). Measurement then follows the subpoint-(1) stabilisation procedure, then torque setpoints at the new constant target speed are adjusted per subpoint (2).

*Figure 3 — "Steps to be performed at each measurement setpoint" and Figure 4 — "Sequence of steady state measurement setpoints" [Figures referenced in source but not visually extracted from this text-only OCR].*

##### 4.3.5.6 Data evaluation for emission monitoring

Gaseous pollutants (4.3.5.3) monitored during the FCMC; characteristic-speed definitions per point 7.4.6 of Annex 4 to UN R49 apply. ▼M3

###### 4.3.5.6.1 Definition of control area

**4.3.5.6.1.1 Engine speed range for the control area:**
1. Based on the **CO2-parent engine's** full-load curve (Appendix 3; 4.3.1).
2. Includes all engine speeds **≥ n30**, the 30th-percentile cumulative speed distribution (all engine speeds incl. idle, ascending order) over the **hotstart WHTC** test cycle (4.3.3), for the full-load curve in subpoint (1).
3. Includes all engine speeds **≤ nhi** (same full-load curve).

**4.3.5.6.1.2 Engine torque and power range for the control area:**
1. Lower torque boundary based on the full-load curve of the **lowest-rated engine** in the CO2-family (4.3.1).
2. Includes all load points with torque **≥ 30%** of the maximum torque from subpoint (1)'s full-load curve.
3. Notwithstanding (2): points below **30% of the maximum power value** (subpoint-1 curve) are **excluded**.
4. Notwithstanding (2)/(3): the **upper boundary** is based on the **CO2-parent engine's** full-load curve (4.3.1), with the torque at each speed **increased by 5% of Tmax_overall** (4.3.5.2.2). This modified/increased curve = upper boundary of the control area.

*Figure 5 — "Definition of the engine speed, torque and power range for the control area" [Figure referenced in source but not visually extracted from this text-only OCR].*

###### 4.3.5.6.2 Definition of the grid cells

Control area divided into grid cells for emission monitoring:
- **9 cells** for engines with rated speed **< 3000 min⁻¹**; **12 cells** for rated speed **≥ 3000 min⁻¹**.
- (1) Outer boundaries aligned to the control area (4.3.5.6.1).
- (2) ▼M3: **2 vertical lines** equally spaced between n30 and nhi for 9-cell grids, or **3 vertical lines** for 12-cell grids.
- (3) **2 lines** equally spaced in torque (i.e. thirds) at each vertical line within the control area.

All engine-speed (min⁻¹) and torque (Nm) boundary values rounded to **2 decimal places** per **ASTM E 29-06**.

*Figure 6 — "Definition of the grid cells for the control area exemplarily for 9 cell grid" [Figure referenced in source but not visually extracted from this text-only OCR].*

###### 4.3.5.6.3 Calculation of specific mass emissions

Specific mass emissions of gaseous pollutants = **average value per grid cell** = arithmetic mean of specific mass emissions over all engine speed/torque points measured during the FCMC that fall in that cell. ▼M3: specific mass emission of each single engine speed/torque point = **averaged value over the 30 ± 1 s** measurement period (4.3.5.5(1)).

A point located directly on a line separating cells counts toward the average of **all adjacent** cells.

Total mass emission of each gaseous pollutant for each FCMC point, **m_FCMC,i [g]**, over the 30 ± 1 s period, calculated per point 8 of Annex 4 to UN R49. ▼M3

Actual engine work for each FCMC point, **W_FCMC,i [kWh]**, over the 30 ± 1 s period, determined from recorded speed/torque values (4.3.5.3).

**Specific mass emissions e_FCMC,i [g/kWh]** for each point:
> **eFCMC,i = mFCMC,i / WFCMC,i**

##### 4.3.5.7 Validity of data

###### 4.3.5.7.1 Requirements for validation statistics of the FCMC

Linear regression of actual values (`nact`, `Mact`, `Pact`) on reference values (`nref`, `Mref`, `Pref`) for the FCMC. Actual values determined from recorded data (4.3.5.3). Ramps between setpoints are **excluded** from the regression.

To minimise time-lag bias, the entire actual speed/torque signal sequence may be advanced or delayed relative to the reference sequence — **if shifted, both speed and torque must be shifted by the same amount in the same direction**.

Method: **least squares**, per points A.3.1/A.3.2 of Appendix 3 to Annex 4 to UN R49; best-fit equation form per point 7.4.6 of Annex 4 to UN R49; **recommended at 1 Hz**. ▼M3

Point omissions permitted per **Table 4 (Permitted point omissions from regression analysis)** of Annex 4 to UN R49, before the regression; additionally, **all** torque/power values at **maximum operator demand** points are omitted for regression purposes only. Points omitted for regression are **not** omitted from other calculations. Omission may apply to the whole cycle or any part.

Data valid if criteria of **Table 3 (Regression line tolerances for the WHSC)** of Annex 4 to UN R49 are met.

###### 4.3.5.7.2 Requirements for emission monitoring ▼M3

FCMC data valid if specific mass emissions of regulated gaseous pollutants per grid cell (4.3.5.6.3) meet:

(a) Non-dual-fuel engines: applicable limits per point 5.2.2 of Annex 10 to UN Regulation 49.
(b) Dual-fuel engines: limits per Annex XVIII to Regulation (EU) No 582/2011 (reference to a pollutant limit in Annex I to Regulation (EU) 595/2009 replaced by the same pollutant's limit per point 5.2.2 of Annex 10 to UN/ECE Regulation 49).

If a grid cell has **fewer than 3** engine speed/torque points, this validity check **does not apply** to that cell.
