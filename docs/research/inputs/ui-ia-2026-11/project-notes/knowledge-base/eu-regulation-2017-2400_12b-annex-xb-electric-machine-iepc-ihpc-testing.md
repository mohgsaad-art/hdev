
# Annex Xb — Certification of Electric Powertrain Components
## Part 2: Testing of Electric Machine Systems, IEPCs and IHPCs Type 1

**Source:** Commission Regulation (EU) 2017/2400 (consolidated), CELEX **02017R2400**, consolidation date **01.01.2026**.
**Range covered:** Annex Xb, point 4 (lines ≈19234–20555).
**Amendment provenance:** This entire point 4 is **►M3** (Reg. (EU) 2022/1379) baseline text, with numerous individual **►M4** (Reg. (EU) 2025/258) refinements embedded inline (flagged below where they occur — mostly clarifications around multispeed-gearbox gear-dependent torque testing, voltage-range wording, and interruption-handling of the EPMC test sequence). See file 12a §0 for full provenance discussion.
**OCR caveat:** The source PDF's mathematical operators (×, −, √, Σ, sub/superscripts) were corrupted by text extraction (rendered as characters such as "Ü", "Ä", "ä", "ð", "Þ", "¼", "þ"). Equations below are reconstructed using standard engineering notation based on context and dimensional consistency. Where any doubt exists it is flagged. For sub-millimeter/sub-percent-tolerance work, verify against the original PDF rendering.

---

## 4.1 Test conditions

The UUT shall be installed; measurands current, voltage, electric inverter power, rotational speed and torque shall be defined per **Figure 1** and point 4.1.1.
**[Figure 1 — "Provisions for measurement of electric machine system or IEPC" — referenced in source but not visually extracted from this text-only OCR.]**

### 4.1.1 Equations for power figures

**4.1.1.1 Inverter power**
$$P_{INV\_in} = V_{INV\_in} \times I_{INV\_in}$$
- $P_{INV\_in}$ = electric inverter power to/from the inverter (or DC/DC converter) on the DC side of the inverter (or on the DC-power-source side of the DC/DC converter) **[W]**
- $V_{INV\_in}$ = voltage at that input **[V]**
- $I_{INV\_in}$ = current at that input **[A]**

Where there are multiple inverter (or DC/DC converter) connections to the electric DC power source (per 4.1.3), the **total sum** of all different electric inverter powers shall be measured.

**4.1.1.2 Mechanical output power**
$$P_{UUT\_out} = \frac{2\pi}{60} \times T_{UUT} \times n$$
- $P_{UUT\_out}$ = mechanical output power of the UUT **[W]**
- $T_{UUT}$ = torque of the UUT **[Nm]**
- $n$ = rotational speed of the UUT **[min⁻¹]**

For an **electric machine system**, torque/speed are measured at the rotational shaft. For an **IEPC**, torque/speed are measured at the gearbox output side, or (if a differential is included) at the differential output side(s).

For an IEPC with integrated differential: the output torque measuring device(s) may be installed on both output sides or only one. If only one dynamometer is used on the output side, the free-rotating end shall be rotatably locked to the other end (e.g. via activated differential lock or another mechanical lock implemented only for measurement).

**IEPC design type wheel motor — measurement provisions:**
- **Configuration 'L'**: torque/speed measured at the gearbox output side; input parameter `NrOfDesignTypeWheelMotorMeasured` = **1**.
- **Configuration 'T'**: torque device(s) on both or only one output shaft.
  - **Both** measured: torque values of both shafts are **summed virtually**; speed values of both shafts are **averaged virtually** (in test-bench data processing or post-processing). `NrOfDesignTypeWheelMotorMeasured` = **2**.
  - **Only one** measured: torque/speed taken at the gearbox output side. `NrOfDesignTypeWheelMotorMeasured` = **1**.

### 4.1.2 Run-in (optional, on request of the applicant)
- Total run-time for optional run-in **plus** measurement of a UUT (except wheel-ends): **≤ 120 hours**.
- Only **factory-fill oil** used for run-in (may also be used for testing per 4.2).
- Speed/torque profile for run-in specified by the component manufacturer.
- Run-in must be documented (run-time, speed, torque, oil temperature) and reported to the approval authority.
- Requirements for oil temperature (4.1.8.1), measurement accuracy (3.1) and test setup (4.1.3–4.1.7) **do not apply** during run-in.

### 4.1.3 Power supply to inverter
- DC, constant-voltage, capable of supplying/absorbing adequate power at the UUT's max (mechanical/electrical) power for the duration of all test runs.
- DC input voltage to the inverter shall be within **±2 %** of the requested target value during all periods where recorded data is used as a basis for simulation-tool input data.
- **Two voltage levels are defined** (Table 2 in 4.2 specifies which test run uses which level(s)):
  - **$V_{min,Test}$**: target DC input voltage corresponding to the **minimum** voltage for unlimited operating capability.
  - **$V_{max,Test}$**: target DC input voltage corresponding to the **maximum** voltage for unlimited operating capability.
  - ►M4 clarification: "unlimited operating capability" means a **representative voltage range typically applied in real vehicles** — not necessarily the technical min/max input voltage, and not reflecting extreme boundary conditions where high-level vehicle control (outside the actual UUT control logic) limits capability (e.g. reduced propulsion torque due to REESS limitations).

### 4.1.4 Setup and wiring
All wiring, shielding, brackets etc. per the component manufacturer(s)' specified conditions.

### 4.1.5 Cooling system
Temperature of all EMS parts must stay within component-manufacturer limits throughout all test runs. For IEPC/IHPC Type 1, this also covers gearboxes and axles that are part of the unit.

**4.1.5.1.1 Cooling power for torque-limitation measurement** (applies to all test runs of 4.2 **except** EPMC/4.2.6):
Manufacturer declares, for each cooling circuit with external heat-exchanger connection:
- max. coolant mass flow or max. inlet pressure;
- admitted max. coolant temperature;
- max. available cooling power on the testbench.
These are documented in the component's information document.

Actual values recorded with test data (must stay below declared maxima), per cooling circuit:
- coolant volume/mass flow;
- coolant temperature at UUT cooling-circuit inlet;
- coolant temperature at test-bed heat exchanger inlet/outlet (UUT side).

- For **all** test runs of 4.2: minimum coolant temperature at the UUT cooling circuit inlet, for liquid cooling = **25 °C**.
- Non-regular test fluids must not exceed manufacturer temperature limits.
- Max. available cooling power (liquid cooling) = f(coolant mass flow, ΔT over test-bed heat exchanger, specific heat capacity of coolant).
- **No additional fan** for actively cooling UUT components is allowed in the test setup.

### 4.1.6 Inverter
Operated in the same mode/settings as specified by the component manufacturer for actual in-vehicle use.

### 4.1.7 Ambient conditions in test cell
**25 ± 10 °C**, measured within 1 m of the UUT.

### 4.1.8 Lubricating oil for IEPCs or IHPC Type 1 (not applicable to standalone EM systems)
- **4.1.8.1 Oil temperatures**: measured at oil-sump centre or another suitable point (good engineering practice); auxiliary regulating system allowed per 4.1.8.4. For external oil conditioning (test purposes only), may measure within 5 cm downstream of the housing outlet. Must not exceed the manufacturer's temperature limit in either case; engineering rationale required to show the external conditioning isn't improving efficiency. For oil circuits **not** part of/connected to any EMS cooling circuit, temperature shall **not exceed 70 °C**.
- **4.1.8.2 Oil quality**: only recommended factory-fill oils.
- **4.1.8.3 Oil viscosity**: if multiple factory-fill oils specified, manufacturer chooses one whose kinematic viscosity (KV) at the same temperature is within **±10 %** of the KV of the highest-viscosity oil (within the specified KV100 tolerance band).
- **4.1.8.4 Oil level/conditioning**: within manufacturer's maintenance-spec min/max levels. External conditioning/filtering permitted (UUT housing may be modified to include it), but must not be used to raise efficiency or generate propulsion torque improperly.
- **4.1.8.5 Installation requirements (►M4)**: UUT installed at the vehicle homologation-drawing inclination angle **±1°**; alternatively at **0° ± 1°** to cover all in-vehicle installation variants.

### 4.1.9 Sign conventions
- **4.1.9.1 Torque/power**: positive = UUT driving the dyno; negative = UUT braking the dyno (dyno driving UUT).
- **4.1.9.2 Current**: positive = UUT drawing power from the supply; negative = UUT delivering power to the supply/inverter.

---

## 4.2 Test runs to be performed

Table 2 defines all required test runs for certifying one specific electric machine system family or IEPC family (families defined per Appendix 13, see file 12f). The EPMC (4.2.6) and the drag curve (4.2.3) are **omitted for all family members except the parent**. Where the manufacturer invokes Article 15(5) of the Regulation, EPMC and drag curve shall be performed **additionally** for that specific EM/IEPC.

### Table 2 — Overview of test runs (Electric machine systems / IEPCs)

| Test run | Ref. point | Required voltage level(s) | Required for parent | Required for other family members |
|---|---|---|---|---|
| Maximum and minimum torque limits | 4.2.2 | $V_{min,Test}$ and $V_{max,Test}$ | yes | yes |
| Drag curve | 4.2.3 | Either $V_{min,Test}$ or $V_{max,Test}$ | yes | no |
| Maximum 30-minute continuous torque | 4.2.4 | $V_{min,Test}$ and $V_{max,Test}$ | yes | yes |
| Overload characteristics | 4.2.5 | $V_{min,Test}$ and $V_{max,Test}$ | yes | yes |
| EPMC (electric power mapping cycle) | 4.2.6 | $V_{min,Test}$ and $V_{max,Test}$ | yes | no |

### 4.2.1 General provisions
- All measurements with all UUT temperatures kept within manufacturer-defined limits.
- All tests performed with temperature-dependent de-rating functionality **fully active**. External parameters (outside the EMS boundary) that influence de-rating in-vehicle shall **not** be considered in any test run under this Annex.
- EMS: torque/speed refer to the EM rotational shaft (unless stated otherwise).
- IEPC: torque/speed refer to the gearbox output side, or differential output side if included.

### 4.2.2 Test of maximum and minimum torque limits
Measures max/min torque characteristics to verify declared system limitations.

**For IEPC with multispeed gearbox (►M4):**
(a) test performed for the gear with ratio **closest to 1**;
(b) if two gears are equidistant from ratio 1, use the gear with the **higher** ratio;
(c) **additionally**, the test **may** be performed for all other forward gears, producing a dedicated dataset per forward gear.

The test shall be performed for each applicable voltage/gear combination declared per 4.2.2.1, applying 4.2.2.2–4.2.2.4 separately to each.

**4.2.2.1 Declaration of values**: manufacturer declares max/min torque vs. rotational speed (0 rpm to max operating speed) prior to test — separately per forward gear (►M4) and separately for $V_{min,Test}$ and $V_{max,Test}$.

**4.2.2.2 Verification of maximum torque limits:**
- Conditioning (unpowered) at 25 ± 10 °C for **≥ 2 hours** (may be shortened/omitted if run directly after another test, provided the UUT stays in the testcell at 25 ± 10 °C).
- Just before the test: run for **3 minutes** at 80 % of max power at the manufacturer-recommended speed.
- Measure output torque/speed at **≥ 10 different rotational speeds**.
  - Lowest speed setpoint ≤ **2 %** of declared max operating speed (or the lowest realisable by the test setup).
  - Highest speed setpoint = declared max operating speed.
  - Remaining ≥8 setpoints between them, manufacturer-specified, with interval between adjacent setpoints ≤ **15 %** of max operating speed.
- Each operating point held ≥ **3 seconds**; torque/speed recorded as average of the **last second**.
- Whole test completed within **5 minutes**.

**4.2.2.3 Verification of minimum torque limits:** identical procedure/timing to 4.2.2.2, at the **same rotational speeds**.

**4.2.2.4 Interpretation of results:**
- Declared **maximum** torque accepted as final if ≤ **+2 %** (overall max) / **+4 %** (other points) above measured values, with a tolerance of **±2 %** for rotational speed.
- If declared values exceed these limits → **measured values used as final.**
- If declared values are **lower** than measured → **declared values used as final.**
- Declared **minimum** torque accepted as final if ≥ **−2 %** (overall min) / **−4 %** (other points), tolerance ±2 % speed.
- If declared values exceed these limits (more negative) → measured values used as final.
- If declared values are **higher** (less negative) than measured → declared values used as final.

### 4.2.3 Test of drag curve
Measures mechanical/electrical power needed to spin the UUT at a given speed via external power.
- Conditioning: unpowered, 25 ± 10 °C, ≥ 2 hours (shortenable as above).
- Optional 3-minute 80 %-power warm-up run before the test.
- **Three test options:**
  - **Option A**: output shaft connected to load machine, which drives the UUT; inverter supply or AC phase cables may be inactive/disconnected.
  - **Option B**: output shaft **not** connected to a load machine; UUT operated at target speed via inverter power supply.
  - **Option C**: output shaft connected to load machine; UUT operated by load machine, inverter power, or a combination.
- Tested at ≥ the same speeds as 4.2.2.2 (more allowed). Each point held ≥ **10 s**, actual speed within **±2 %** of setpoint.
- Recorded as average over last **5 seconds**:
  - Option B/C: electric power to the inverter.
  - Option A/C: load-machine torque applied to the UUT output shaft(s).
  - All options: UUT rotational speed.
- For IEPC with multispeed gearbox: test only for the gear closest to ratio 1 (tie → higher ratio); additional gears optional.

### 4.2.4 Test of maximum 30-minute continuous torque
Measures the max continuous torque achievable on average over **1 800 seconds**. For multispeed-gearbox IEPC: only the gear closest to ratio 1 (tie → higher ratio).

**4.2.4.1 Declaration**: manufacturer declares max 30-min continuous torque + corresponding speed (speed range where mechanical power > **90 %** of the overall max power from 4.2.2 data), separately per voltage level.

**4.2.4.2 Verification**:
- Conditioning: unpowered, 25 ± 10 °C, ≥ **4 hours** (shortenable if directly consecutive).
- Run at declared torque/speed setpoint for **1 800 s total**.
- Measured mechanical power must stay within **±5 %** of the declared value; speed within **±2 %**.
- Final "maximum 30-min continuous torque" = average output torque over the 1800 s window; corresponding speed = average speed over the window.

**4.2.4.3 Interpretation**:
- Declared values accepted as final if they do not differ by more than **+4 %** (torque, tolerance ±2 % speed) from measured averages.
- If exceeded → repeat 4.2.4.1–4.2.4.3 with different declared values.
- If declared torque is **lower** than measured → declared values used as final.
- Additionally calculate: average actual measured electric inverter power over the 1800 s; and the "average 30-minute continuous power" from final torque × final speed.

### 4.2.5 Test of overload characteristics
Measures the duration the UUT can sustain max output torque. Multispeed-gearbox IEPC: gear closest to ratio 1 only.

**4.2.5.1 Declaration**: manufacturer declares max output torque at the same speed setpoint used in 4.2.4.2, **≥** the max 30-min continuous torque (4.2.4.3). Also declares duration **$t_{0\_maxP}$** for which this torque can be constantly achieved. Declared separately per voltage level.

**4.2.5.2 Verification**:
- Conditioning: unpowered, 25 ± 10 °C, ≥ 2 hours (shortenable if consecutive).
- Pre-test: run **30 minutes** at **50 %** of the max 30-min continuous torque (4.2.4.3) at that speed.
- Then run at the declared max-output-torque/speed setpoint.
- Measure torque, speed, DC input voltage, and inverter power over the declared **$t_{0\_maxP}$**.

**4.2.5.3 Interpretation**:
- Recorded torque/speed accepted if within **±2 %** (torque) and **±2 %** (speed) of declared values over the whole $t_{0\_maxP}$.
- Otherwise repeat 4.2.5.1–4.2.5.3 with revised declared torque and/or $t_{0\_maxP}$.
- Final values = averages of rotational speed, torque, DC input voltage over $t_{0\_maxP}$; also average inverter power over the same period.

### 4.2.6 EPMC test (Electric Power Mapping Cycle)
Measures inverter power to/from the UUT across operating points.

**4.2.6.1 Preconditioning**: unpowered, 25 ± 10 °C, ≥ 2 hours (shortenable if consecutive).

**4.2.6.2 Operating points to be measured (►M4):**

*4.2.6.2.1 Speed setpoints* — standalone EMS or IEPC with no shiftable gears:
(a) same setpoints as 4.2.2.2 for the respective voltage level;
(b) + the speed setpoint for the max-30-min-continuous-torque verification (4.2.4.2) for that voltage level;
(c) further setpoints may be added.

For a multispeed-gearbox IEPC where torque limits were determined for a **single gear only** (4.2.2(a)/(b)):
(d) setpoints for the gear closest to ratio 1, $n_{k,gear\_iCT1}$, used as the basis;
(e) converted to other gears by:
$$n_{k,gear} = n_{k,gear\_iCT1} \times \frac{i_{gear\_iCT1}}{i_{gear}}$$
— $n_{k,gear}$: speed setpoint k for a specific gear; $i_{gear}$: gear ratio of that gear; $i_{gear\_iCT1}$: gear ratio of the gear closest to 1.

For a multispeed-gearbox IEPC where torque limits were determined **for each forward gear** (4.2.2(c)) (►M4):
(f) same setpoints as 4.2.2.2, per voltage level and per forward gear;
(g) + the max-30-min speed setpoint (4.2.4.2), converted per the equation in (e);
(h) further setpoints optional.

*4.2.6.2.2 Torque setpoints* — standalone EMS or IEPC with no shiftable gears:
(a) ≥10 torque setpoints, both positive (driving) and negative (braking) side; lowest = overall minimum torque ($T_{min\_overall}$), highest = overall maximum torque ($T_{max\_overall}$) from 4.2.2.4;
(b) remaining ≥8 setpoints between them; max interval between adjacent setpoints = **22.5 %** of $T_{max\_overall}$;
(c) positive-torque limit at a given speed = max-torque limit at that speed (4.2.2.4) minus **5 %** of $T_{max\_overall}$; setpoints above this limit collapse to one setpoint at the max-torque-limit value;
(d) negative-torque limit analogous with $T_{min\_overall}$;
(e) min/max torque limitation at a specific speed determined by linear interpolation of 4.2.2.4 data.

For multispeed-gearbox IEPC, single-gear torque limits (4.2.2(a)) (►M4):
(f) torque setpoints for the gear closest to ratio 1, $T_{j,gear\_iCT1}$, used as basis;
(g) converted to other gears:
$$T_{j,gear} = T_{j,gear\_iCT1} / i_{gear\_iCT1} \times i_{gear}$$
(h) setpoints $T_{j,gear}$ with absolute value **> 10 kNm** are **not required** to be measured in the actual test (4.2.6.4).

For multispeed-gearbox IEPC, per-forward-gear torque limits (4.2.2(c)) (►M4):
(i) ≥10 setpoints per gear, via (a)–(e) applied per gear;
(j) resulting setpoints with absolute value **> 10 kNm** not required to be measured.

*4.2.6.2.3 Minimum amount of torque setpoints* — detailed rules (►M4) for adding setpoints at **9.8 kNm / −9.8 kNm**, **6.66 kNm / −6.66 kNm**, and **3.33 kNm / −3.33 kNm** thresholds when the number of original setpoints ≤10 kNm on the positive or negative side is 1 or 2, to ensure adequate map density near the 10 kNm cutoff. (Full branching logic — see source point (a)–(d), 8 sub-cases; this ensures at least 2 extra interpolation points exist near the high-torque cutoff region for each speed setpoint.)

**4.2.6.3 Signals to be measured**: at each operating point — electric power to/from the inverter, and output torque and speed of the UUT.

**4.2.6.4 Test sequence**:
- Steady-state setpoints at defined speed/torque per 4.2.6.2.
- **(►M4) Unforeseen-interruption handling**: UUT stays in testcell at 25 ± 10 °C; warm-up per manufacturer recommendation before continuing; test sequence continues at the next **lower** speed setpoint (preconditioning only, no data recorded) before resuming actual recording from the speed setpoint where interruption occurred.
- For IEPC: test sequence performed **per gear sequentially**, starting from the highest gear ratio, descending; all setpoints of a gear's dataset completed before switching gear; test may be interrupted after completing each gear; different torque meters allowed.
- Warm-up before first setpoint per manufacturer recommendation. First speed setpoint = lowest.
- **Ordering within a speed setpoint** (a)–(m):
  (a) highest positive torque first; (b) lowest positive torque; (c) second-highest positive; (d) second-lowest positive; (e) continue alternating highest→lowest remaining until all positive setpoints done; (f) optional cool-down; (g) lowest negative torque; (h) highest negative torque; (i) second-lowest negative; (j) second-highest negative; (k) continue alternating until all negative setpoints done; (l) optional cool-down; (m) move to next-higher speed setpoint, repeat (a)-(m).
- **(►M4) Hold time/tolerance**: each point held ≥ **5 seconds**; speed held within **±1 % or 20 rpm** (whichever larger); torque (except at the highest/lowest setpoint per speed) held within **±1 % of setpoint or ±5 Nm** (standalone EMS) / **±2 % or ±20 Nm** (IEPC with gearbox and/or differential), whichever larger.
- Recorded values = average over the **last 2 seconds** of the hold time.

---

## 4.3 Post-processing of measurement data of the UUT

**4.3.1 General**: all steps 4.3.2–4.3.6 performed separately per voltage level ($V_{min,Test}$ / $V_{max,Test}$).

**4.3.2 Maximum/minimum torque limits**: extend via **linear extrapolation** (2 closest points) to 0 rpm and to the declared max operating speed where measured data doesn't cover these ranges. (►M4: for multispeed-gearbox IEPC with per-gear torque limits, this is done **separately per forward gear**.)

**4.3.3 Drag curve (►M4)**: drag torque carries a **negative** sign (per 4.1.9 convention). Modification steps:
1. Where inverter supply was inactive/disconnected → set electric power values to 0.
2. Where output shaft was not connected to the load machine → set torque values to 0.
3. Extend (1)+(2)-modified data via linear extrapolation to the max operating speed where data doesn't cover it.
4. Modified electric-power values (from steps 1–3) = **virtual mechanical loss power**, converted to **virtual drag torque** at the corresponding output-shaft speed; this virtual drag torque has a **negative** sign.
5. At each speed setpoint, add the virtual drag torque (step 4) to the actual load-machine torque → **total drag torque** of the UUT as f(speed).
6. The total drag torque at the **lowest** speed setpoint (from step 5) is **copied to a new entry at 0 rpm**.

**4.3.4 EPMC**: extended per forward gear and per voltage level separately:
1. Lowest-speed-setpoint torque/power data pairs copied to a new entry at **0 rpm**.
2. Highest-speed-setpoint data pairs copied to a new entry at **highest speed × 1.05**.
3. **(►M4)** For an omitted torque setpoint (per 4.2.6.2.2(h)/(j)), a new data point is calculated: speed = omitted setpoint speed; torque = omitted setpoint torque; inverter power = **linear extrapolation** using the least-squares regression line (slope, y-intercept) of the **3 actually-measured points** closest to that torque value at the same speed; starting point = inverter power of the closest actually-measured point, applying only the regression slope.
   - (d) For **positive** torque: extrapolated power lower than the closest measured point's power → **clamped to that measured power**.
   - (e) For **negative** torque: extrapolated power higher than the closest measured point's power → **clamped to that measured power**.
   - (f) Notwithstanding (d)/(e): if the extrapolated efficiency (electrical inverter power vs. mechanical power) exceeds either (i) the efficiency from the Appendix 9 standard-values procedure for this operating point, or (ii) the closest-measured-point's efficiency **minus 2 percentage points** (e.g. 90.5 % − 2 % = 88.5 %) — the extrapolated power is **replaced** to reflect exactly that bounding efficiency.
4. At each speed setpoint, a new point from the **highest torque setpoint × 1.05** is added, with inverter power calculated to **hold mechanical/inverter-power efficiency constant**.
5. Similarly, a new point from the **lowest torque setpoint × 1.05** is added, holding inverter/mechanical-power efficiency constant.

**4.3.5 Overload characteristics**: efficiency = average mechanical output power over $t_{0\_maxP}$ ÷ average inverter power over $t_{0\_maxP}$.

**4.3.6 Maximum 30-minute continuous torque**: efficiency = average 30-min continuous power ÷ average inverter power.
**(►M4)** Additionally, from the 4.2.4.2 time-resolved data, compute (per cooling circuit with external heat exchanger) the **average cooling power** and **average coolant temperature at the UUT cooling-circuit inlet** over the 1800 s period. Cooling power = f(coolant specific heat capacity, coolant mass flow, ΔT over the test-bed heat exchanger on the UUT side).

---

## 4.4 Special provisions for testing of IHPCs Type 1

IHPCs Type 1 are **virtually split into two separate VECTO components**: an electric machine system and a transmission. Two separate component datasets are generated.

- Points 4.1–4.2 apply as for IEPC.
- Torque/speed measured at the **output shaft of the system** (toward wheels).
- **Family concept (Appendix 13) is NOT allowed** for IHPC Type 1 → no test-run omission; **all** test runs of 4.2 must be performed for each individual IHPC Type 1 — **except** the drag-curve test (4.2.3), which is **omitted**.
- **Standard values are not allowed** for IHPC Type 1 (every unit must be fully measured).

### 4.4.1 Test runs

**4.4.1.1 Total system characteristics** (losses of the complete IHPC incl. gearbox):
Performed per the IEPC-with-multispeed-gearbox provisions. Input shaft (feeding propulsion torque) either disconnected/freely rotating, or fixed/non-rotating.

**Table 2a — Overview of test runs for IHPC Type 1:**

| Test run | Reference |
|---|---|
| Maximum and minimum torque limits | 4.2.2 |
| Maximum 30-minute continuous torque | 4.2.4 |
| Overload characteristics | 4.2.5 |
| EPMC | 4.2.6 |

EPMC measured **per forward gear** (per 4.2.6.2), since multispeed-gearbox-IEPC provisions apply.

**4.4.1.2 Losses of the gearbox part within the system:**
- Tested per Annex VI, point 3.3 (transmission test), **except**:
  - input shaft connected to and driven by a dynamometer (per Annex VI 3.3);
  - power supply from the DC source to the inverter(s)/DC-DC converter(s) **disconnected** (dummy magnets/rotors may be used in the electric machine(s) to allow this without damage);
  - torque range of Annex VI 3.3.6.3 **extended to negative torque values**, mirroring the positive-side setpoints with a negative sign.

### 4.4.2 Post-processing of IHPC Type 1 data

**4.4.2.1 Total system characteristics**: per 4.3.1–4.3.6, **except** 4.3.3 (drag curve) is omitted (not measured). Multispeed-gearbox-specific provisions applied where relevant.

**4.4.2.2 Gearbox-part losses**: per Annex VI point 3.4, **except**:
- Annex VI 3.4.2–3.4.5 provisions applied **analogously to negative torque values** too;
- Annex VI 3.4.6 **not applied**.

**4.4.2.3 Deriving the virtual electric machine system's specific data**: *(the two efficiency figures from 4.3.5/4.3.6 are **not** carried through these conversion steps — they serve only CoP assessment, not component-data derivation)*

(a) Convert speed/torque from the output shaft to the **input shaft** of the IHPC Type 1 (per gear, if multiple gears tested):
$$n_{EM,virt} = n_{output} \times i_{gbx}$$
$$T_{EM,virt} = T_{output} \times \frac{1}{i_{gbx}} + T_{loss,gbx}\left(n_{EM,virt},\ T_{output} \times \frac{1}{i_{gbx}},\ gear\right)$$
- $n_{EM,virt}$: virtual EMS speed referred to IHPC input shaft [1/min]
- $n_{output}$: measured IHPC output-shaft speed [1/min]
- $i_{gbx}$: ratio of input-shaft speed over output-shaft speed for the engaged gear [–]
- $T_{EM,virt}$: virtual EMS torque referred to IHPC input shaft [Nm]
- $T_{output}$: measured IHPC output-shaft torque [Nm]
- $T_{loss,gbx}$: gearbox torque loss at the input shaft, by **2-D linear interpolation** from the gearbox loss maps (4.4.2.2), for the respective gear [Nm]

(b) Convert electric power maps (per forward gear, converted to input shaft per (a)) to the virtual EMS by removing gearbox losses:
$$P_{el,virt}(n_{EM,virt}, T_{EM,virt}) = P_{el,meas}(n_{EM,virt}, T_{EM,virt}) - T_{loss,gbx}(n_{EM,virt}, T_{EM,virt}, gear) \times n_{EM,virt}$$
(dimensionally this term requires the appropriate $2\pi/60$ torque→power conversion factor, consistent with 4.1.1.2)

(c) Virtual EMS **drag torque** at the same $n_{EM,virt}$ setpoints used for the max/min torque curve: **each value is set to zero.**

(d) Virtual EMS **rotational inertia**: convert the actual electric machine(s)' inertia (determined per Appendix 8, point 8) to the value referred to the IHPC Type 1 input shaft.

### 4.4.3 Generating input data for the simulation tool
Two separate component datasets generated — EMS and transmission — **sharing the same certification number**.

- **4.4.3.1** Virtual EMS input data: per Appendix 15 EMS definitions, from the final 4.4.2.3 data.
- **4.4.3.2** Virtual transmission input data: per Appendix 12 (of **Annex VI**) Tables 1–3, from the final 4.4.2.2 data; the `TransmissionType` parameter (Table 1) is set to **'IHPC Type 1'**.

---

## Key cross-references for the sizing tool

- Appendix 8 (standard default e-motor loss-map generation from UN R85 data) — see file 12h.
- Appendix 9 (standard values for IEPC incl. gearbox/differential loss formulas) — see file 12h.
- Appendix 13 (family concept — which EM/IEPC units can share a single certificate) — see file 12f.
- Appendix 15 Tables 1–6 (exact XML parameter IDs P450–P510 for EMS/IEPC input) — see file 12h.
