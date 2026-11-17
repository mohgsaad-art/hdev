
# Annex Xb — Certification of Electric Powertrain Components
## Part 3: Testing of Battery Systems or Representative Battery Subsystems
### ⚠ CRITICAL FILE for battery-sizing work — every test condition, C-rate, SOC window, tolerance and formula below is transcribed exactly as given in the legal text.

**Source:** Commission Regulation (EU) 2017/2400 (consolidated), CELEX **02017R2400**, consolidation date **01.01.2026**.
**Range covered:** Annex Xb, point 5 (lines ≈20556–21033).
**Amendment provenance:** All of point 5 is **►M3** (Commission Regulation (EU) 2022/1379) — this is the **first EU-legislated battery-system test/certification methodology for VECTO**, introduced in 2022.
**OCR caveat:** see file 12b header — equations below are reconstructed from corrupted OCR math symbols; verify against the original PDF for sub-percent-level precision work.

---

## 5.0 Preliminary — HPBS vs HEBS, the battery-type fork

Every subsequent test parameter in this section forks on the battery type defined in file 12a §2.6:
- **HPBS** (high-power battery system): ratio of (max. discharge current at 50 % SOC) ÷ (nominal 1C-rate Ah capacity at RT) is **≥ 10**.
- **HEBS** (high-energy battery system): same ratio is **< 10**.

HPBS test current is generally expressed as **1C** (and preparation at 2C); HEBS test current is generally **1/3C**. Keep this fork in mind throughout — it changes virtually every number below.

The battery UUT's thermal conditioning device and corresponding test-bench thermal conditioning loop shall be **operational**, sized to satisfy the battery UUT's thermal conditioning performance per the vehicle application, and able to run the requested test procedure within the battery UUT's operational limits.

---

## 5.1 General provisions

- Battery UUT components may be **distributed in different devices** within the vehicle (i.e. a representative battery subsystem need not be a single physical enclosure).
- The battery UUT is **controlled by the BCU**; test-bench equipment follows the BCU's operational limits via bus communication. The BCU's thermal conditioning control and the test-bench's corresponding loop shall be operational per the BCU's commands, unless the specific test procedure states otherwise. **The BCU program may be adapted by the manufacturer** for the requested test procedure, but must stay within the battery UUT's operational and safety limits.

### 5.1.1 Conditions for thermal equilibration
Thermal equilibration is reached when, **over a period of 1 hour**, the deviation between the cell temperature specified by the manufacturer and the temperature at **all** cell-temperature measuring points is **< ±7 K**.

### 5.1.2 Sign conventions
**5.1.2.1 Current**: positive = **discharging**; negative = **charging**. *(Note: opposite convention compared to point 4.1.9.2's UUT-drawing-power-is-positive rule for electric machines — each section's local sign convention must be respected separately.)*

### 5.1.3 Reference location for ambient temperature
Measured within **1 m** of the battery UUT, at a point indicated by the manufacturer.

### 5.1.4 Thermal conditions
- "Battery testing temperature" (target operating temperature) is **specified by the manufacturer**.
- All cell-temperature measuring points must stay within manufacturer-specified limits during all test runs.
- **Liquid-conditioned battery UUT**: conditioning-fluid temperature recorded at the battery UUT inlet, maintained within **±2 K** of a manufacturer-specified value.
- **Air-cooled battery UUT**: temperature at a manufacturer-indicated point kept within **+0 / −20 K** of the manufacturer-specified maximum value.
- For all test runs, available cooling/heating power on the testbench is limited to a manufacturer-declared value, recorded with the test data. Determination methods:
  1. **Liquid conditioning**: from conditioning-fluid mass flow and ΔT over the heat exchanger on the battery UUT side.
  2. **Electric conditioning**: from voltage and current. The manufacturer may modify the conditioning unit's electrical connection for certification purposes to measure battery UUT characteristics **without** including conditioning electric power (e.g. if conditioning is implemented inside the battery UUT); the externally-provided electric cooling/heating power must nonetheless be recorded.
  3. **Other conditioning types**: based on good engineering judgement, agreed with the type-approval authority.

---

## 5.2 Preparation cycles

- Battery UUT conditioned by performing **up to 5 cycles** of full discharge → full charge, to stabilise system performance before actual testing.
- Consecutive full-discharge/full-charge cycles performed at the manufacturer-defined operational set temperature **until "preconditioned" status is reached**.
- **"Preconditioned" criterion**: discharged capacity between two consecutive discharges changes by **≤ 3 %** of rated capacity, **or** 5 repetitions have been performed.
- Battery UUT voltage must **not fall below the manufacturer-recommended minimum voltage** at end of discharge (lowest voltage under discharge without irreversible damage).
- Termination criteria for full discharge/full charge are **manufacturer-defined**.

### 5.2.1 Current levels in preparation cycles — HPBS
- **Discharging: 2C**
- **Charging**: per manufacturer's recommendations.

### 5.2.2 Current levels in preparation cycles — HEBS
- **Discharging: 1/3C**
- **Charging**: per manufacturer's recommendations.

---

## 5.3 Standard cycle (SC)

**Purpose**: ensures the same initial condition before each dedicated battery test, and establishes the charged energy for CoP purposes (Appendix 12). Performed at the manufacturer-defined operational set temperature.

### 5.3.1 Standard cycle for HPBS
Sequence: **standard discharge → rest period → standard charge → second rest period.**
- Standard discharge: constant current of **1C**, down to the minimum SOC per manufacturer specification.
- Rest period: starts immediately after discharge end, lasts **30 minutes**.
- Standard charge: per manufacturer's end-of-charge criteria and applicable charging time limits.
- Second rest period: starts immediately after charge end, lasts **30 minutes**.

### 5.3.2 Standard cycle for HEBS
Identical structure, but:
- Standard discharge: constant current of **1/3C**, down to the minimum SOC.
- Rest periods: **30 minutes** each (same as HPBS).
- Standard charge: per manufacturer specification.

---

## 5.4 Test runs to be performed

Before any test run in this point, the battery UUT must undergo the point 5.2 preparation-cycle procedure.

### 5.4.1 Test procedure for rated capacity
Measures rated capacity in Ah at constant-current discharge.

**5.4.1.1 Signals to be measured** (during preconditioning, standard cycles and the actual test run):
- Charge/discharge current at the battery UUT terminals;
- Voltage across the battery UUT terminals;
- Temperatures at all battery UUT measuring points;
- Ambient temperature in the testbench;
- Heating/cooling power for the battery UUT.

**5.4.1.2 Test run**:
- After full charge (per manufacturer spec) and thermal equilibration (5.1.1), perform a **standard cycle** (5.3).
- Actual test run must start **within 3 hours** after the standard cycle ends — otherwise, **repeat** the standard cycle.
- Performed at **RT**, constant-current discharge:
  - **HPBS**: to the manufacturer's rated **1C capacity** in Ah.
  - **HEBS**: to the manufacturer's rated **1/3C capacity** in Ah.
- All discharge tests terminated at manufacturer-specified minimum conditions.

**5.4.1.3 Interpretation of results**: **rated capacity** = the capacity in Ah obtained from integrating the battery current over time during the actual test run.

**5.4.1.4 Data to be reported**:
- Rated capacity (per 5.4.1.3);
- Average values over the actual test run of all 5.4.1.1 signals;
- **For CoP purposes, additionally calculate**:
  - Total charged energy, **$E_{cha}$**, from **20 % to 80 % SOC** during the standard cycle performed just before the actual test run;
  - Total discharged energy, **$E_{dis}$**, from **80 % to 20 % SOC** during the actual test run;
  - All SOC values based on the **actual measured** rated capacity (5.4.1.3).
  - **Round-trip efficiency**: $\eta_{BAT} = E_{dis} / E_{cha}$ — reported in the information document per Appendix 5.

### 5.4.2 Test procedure for open circuit voltage, internal resistance and current limits
Determines the ohmic resistance (discharge/charge) and OCV vs. SOC; verifies declared max charge/discharge current.

**5.4.2.1 General provisions**:
- All SOC values based on the actual measured rated capacity (5.4.1.3).
- If the discharge-voltage limit is reached during discharge, current shall be reduced to **hold terminal voltage at the discharge voltage limit** for the rest of the pulse. Same logic for the charge-voltage limit during regenerative charge pulses.
- If test equipment cannot hit the requested current within **±1 %** of target within **100 ms** after a profile change, the affected data shall be **discarded** (no OCV/internal-resistance values derived from it).
- If BCU-declared operational limits (via bus) demand current reduction, the test bench **must comply**.

**5.4.2.2 Signals to be measured**: discharge current, terminal voltage, all measuring-point temperatures, ambient temperature, heating/cooling power.

**5.4.2.3 Test run**:
- *5.4.2.3.1 Preconditioning*: full charge + thermal equilibration (5.1.1), then a standard cycle (5.3); actual test must start **within 1–3 hours** after the standard cycle — otherwise repeat.
- *5.4.2.3.2 Test procedure*:
  - **HPBS SOC levels tested**: **80, 65, 50, 35, 20 %**.
  - **HEBS SOC levels tested**: **90, 70, 50, 35, 20 %**.
  - At the last step (20 % SOC), the manufacturer may **reduce max discharge current** to keep SOC above the minimum (avoiding deep discharge).
  - Before each SOC-level test, preconditioned per 5.4.2.3.1.
  - To reach the required SOC from the initial condition: discharge at constant **1C (HPBS)** / **1/3C (HEBS)**, then a **30-minute rest** before the next measurement.
  - Manufacturer declares, prior to test, the max charge/discharge current at each SOC level sustainable throughout the respective pulse time-increment (Table 3 for HPBS, Table 4 for HEBS).
  - Test performed at **RT**.

### Table 3 — Current profile for HPBS

| Time increment [s] | Time cumulative [s] | Target current |
|---|---|---|
| 0 | 0 | 0 |
| 20 | 20 | $I_{dischg\_max}/33$ |
| 40 | 60 | 0 |
| 20 | 80 | $I_{chg\_max}/33$ |
| 40 | 120 | 0 |
| 20 | 140 | $I_{dischg\_max}/32$ |
| 40 | 180 | 0 |
| 20 | 200 | $I_{chg\_max}/32$ |
| 40 | 240 | 0 |
| 20 | 260 | $I_{dischg\_max}/3$ |
| 40 | 300 | 0 |
| 20 | 320 | $I_{chg\_max}/3$ |
| 40 | 360 | 0 |
| 20 | 380 | $I_{dischg\_max}$ |
| 40 | 420 | 0 |
| 20 | 440 | $I_{chg\_max}$ |
| 40 | 480 | 0 |

*(Note: "/33" and "/32" in the source appear to be successive pulse-level dividers in a geometric/stepped progression toward full current — transcribed exactly as given in the consolidated text; verify against the original PDF table if these divisor values are load-bearing for an implementation, as "/33" then "/32" then "/3" then "×1" is an unusual non-monotonic-looking sequence that may reflect OCR of "1/33", "1/3²", etc. Flagging explicitly per project instructions rather than silently correcting.)*

### Table 4 — Current profile for HEBS

| Time increment [s] | Time cumulative [s] | Target current |
|---|---|---|
| 0 | 0 | 0 |
| 120 | 120 | $I_{dischg\_max}/33$ |
| 40 | 160 | 0 |
| 120 | 280 | $I_{chg\_max}/33$ |
| 40 | 320 | 0 |
| 120 | 440 | $I_{dischg\_max}/32$ |
| 40 | 480 | 0 |
| 120 | 600 | $I_{chg\_max}/32$ |
| 40 | 640 | 0 |
| 120 | 760 | $I_{dischg\_max}/3$ |
| 40 | 800 | 0 |
| 120 | 920 | $I_{chg\_max}/3$ |
| 40 | 960 | 0 |
| 120 | 1080 | $I_{dischg\_max}$ |
| 40 | 1120 | 0 |
| 120 | 1240 | $I_{chg\_max}$ |
| 40 | 1280 | 0 |

(Same divisor caveat as Table 3 applies.)

Where:
- $I_{dischg\_max}$ = absolute value of the manufacturer-specified max discharge current at that SOC level, sustainable through the pulse time increment.
- $I_{chg\_max}$ = absolute value of the manufacturer-specified max charge current at that SOC level, sustainable through the pulse time increment.

**Voltage measurement**: $V_0$ (voltage at time zero, before the first target-current change) = average over **100 ms**.

**For HPBS, measured**:
1. For each discharge/charge pulse level (Table 3): voltage under zero current, averaged over the **last second before** the current change — $V_{dstart}$ (discharge) / $V_{cstart}$ (charge).
2. For each discharge pulse level: voltage at **2, 10, 20 s** after the current change ($V_{d2}, V_{d10}, V_{d20}$) and corresponding current ($I_{d2}, I_{d10}, I_{d20}$), each averaged over **100 ms**.
3. For each charge pulse level: voltage at **2, 10, 20 s** ($V_{c2}, V_{c10}, V_{c20}$) and current ($I_{c2}, I_{c10}, I_{c20}$), averaged over 100 ms.

### Table 5 — Voltage measurement points per current-pulse level, HPBS

| Time after current change [s] | D/C | Voltage | Current |
|---|---|---|---|
| 2 | D | $V_{d2}$ | $I_{d2}$ |
| 10 | D | $V_{d10}$ | $I_{d10}$ |
| 20 | D | $V_{d20}$ | $I_{d20}$ |
| 2 | C | $V_{c2}$ | $I_{c2}$ |
| 10 | C | $V_{c10}$ | $I_{c10}$ |
| 20 | C | $V_{c20}$ | $I_{c20}$ |

**For HEBS, measured** (adds a **120 s** point vs. HPBS's set of 2/10/20 s):
1. Zero-current voltage before change: $V_{dstart}$/$V_{cstart}$ (last-second average).
2. Discharge pulse: voltage/current at **2, 10, 20, 120 s** ($V_{d2..d120}$, $I_{d2..d120}$).
3. Charge pulse: voltage/current at **2, 10, 20, 120 s** ($V_{c2..c120}$, $I_{c2..c120}$).

### Table 6 — Voltage measurement points per current-pulse level, HEBS

| Time after current change [s] | D/C | Voltage | Current |
|---|---|---|---|
| 2 | D | $V_{d2}$ | $I_{d2}$ |
| 10 | D | $V_{d10}$ | $I_{d10}$ |
| 20 | D | $V_{d20}$ | $I_{d20}$ |
| 120 | D | $V_{d120}$ | $I_{d120}$ |
| 2 | C | $V_{c2}$ | $I_{c2}$ |
| 10 | C | $V_{c10}$ | $I_{c10}$ |
| 20 | C | $V_{c20}$ | $I_{c20}$ |
| 120 | C | $V_{c120}$ | $I_{c120}$ |

**5.4.2.4 Interpretation of results** — calculated separately per SOC level.

**5.4.2.4.1 Calculations for HPBS:**
1. Internal resistance per discharge pulse level:
$$R_{Id2} = \frac{V_{dstart} - V_{d2}}{I_{d2}} \qquad R_{Id10} = \frac{V_{dstart} - V_{d10}}{I_{d10}} \qquad R_{Id20} = \frac{V_{dstart} - V_{d20}}{I_{d20}}$$
2. Discharging internal resistances $R_{Id2\_avg}$, $R_{Id10\_avg}$, $R_{Id20\_avg}$ = average over all current pulse levels (Table 3) of the step-1 values.
3. Internal resistance per charge pulse level:
$$R_{Ic2} = \frac{V_{cstart} - V_{c2}}{I_{c2}} \qquad R_{Ic10} = \frac{V_{cstart} - V_{c10}}{I_{c10}} \qquad R_{Ic20} = \frac{V_{cstart} - V_{c20}}{I_{c20}}$$
4. Charging internal resistances $R_{Ic2\_avg}$, $R_{Ic10\_avg}$, $R_{Ic20\_avg}$ = average over all levels of step-3 values.
5. **Overall internal resistances** $R_{I2}$, $R_{I10}$, $R_{I20}$ = average of the respective discharging (step 2) and charging (step 4) values. **→ These are the DCIR values reported as input data (see Appendix 15, Table 3, file 12h).**
6. **Open circuit voltage (OCV)** = the value of $V_0$ measured for that SOC level.
7. Max **discharging** current limit = average over **20 s** at the target current $I_{dischg\_max}$ for that SOC level.
8. Max **charging** current limit = average over **20 s** at the target current $I_{chg\_max}$. **Absolute values** reported as final.

**5.4.2.4.2 Calculations for HEBS:** identical structure but adds the **120 s** pulse point throughout:
1. $R_{Id2}, R_{Id10}, R_{Id20}, R_{Id120}$ (discharge) via the same $(V_{dstart}-V_{dX})/I_{dX}$ formula.
2. Averaged over all levels → $R_{Id2\_avg}, R_{Id10\_avg}, R_{Id20\_avg}, R_{Id120\_avg}$.
3. $R_{Ic2}, R_{Ic10}, R_{Ic20}, R_{Ic120}$ (charge), same formula.
4. Averaged → $R_{Ic2\_avg}, R_{Ic10\_avg}, R_{Ic20\_avg}, R_{Ic120\_avg}$.
5. **Overall**: $R_{I2}, R_{I10}, R_{I20}, R_{I120}$ = average of discharging/charging.
6. OCV = $V_0$ for that SOC level.
7. Max discharging current limit = average over **120 s** at $I_{dischg\_max}$.
8. Max charging current limit = average over **120 s** at $I_{chg\_max}$. Absolute values reported.

---

## 5.5 Post-processing of measurement data of the battery UUT

- **OCV vs. SOC**: built from the values determined per SOC level (5.4.2.4.1 point 6 for HPBS / 5.4.2.4.2 for HEBS).
- **Internal resistance vs. SOC**: built from the values per SOC level (5.4.2.4.1 point 5 for HPBS / 5.4.2.4.2 for HEBS).
- **Max discharging/charging current limits**: based on manufacturer-declared values (pre-test). **If** a specific measured value (5.4.2.4.1(7)/(8) for HPBS, 5.4.2.4.2 for HEBS) **deviates by more than ±2 %** from the declared value → the **measured** value is reported instead.

---

## Cross-reference to standard (default) battery values

Where a battery is certified using **standard values** instead of full measurement, the defaults (OCV-vs-SOC curve formula from nominal voltage, DCIR specific-resistance tables for HPBS/HEBS, and max charge/discharge C-rate-vs-SOC tables) are given in **Appendix 10** of this Annex — fully reproduced in file **12h-annex-xb-standard-values-and-simulation-input-parameters.md**. The full XML input-parameter schema for battery systems (`RatedCapacity`, `OCV`, `DCIR RI2/RI10/RI20/RI120`, `MaxChargingCurrent`, `MaxDischargingCurrent`, parameter IDs P511–P531) is in Appendix 15, also reproduced in file 12h.
