
# Annex Xb — Certification of Electric Powertrain Components
## Part 4: Testing of Capacitor Systems or Representative Capacitor Subsystems

**Source:** Commission Regulation (EU) 2017/2400 (consolidated), CELEX **02017R2400**, consolidation date **01.01.2026**.
**Range covered:** Annex Xb, point 6 (lines ≈21034–21203).
**Amendment provenance:** All of point 6 is **►M3** (Commission Regulation (EU) 2022/1379) — introduced alongside the battery/e-machine methodology in 2022.
**OCR caveat:** see file 12b header — equations reconstructed from corrupted OCR math symbols (×, −, Σ were garbled); verify against the original PDF for high-precision implementation.

---

## 6.0 Why capacitors get only one test run

> "The characteristics for a capacitor are hardly dependent on its state of charge or current, respectively. Therefore, **only a single test run is prescribed** for the calculation of the model input parameters." (point 6.1)

This is a deliberate simplification relative to the battery procedure (5 SOC levels × multiple pulse durations): a capacitor's R/C behaviour is treated as effectively SOC-independent, so one charge/discharge cycle suffices.

## 6.1 General provisions

- Capacitor system components may be **distributed in different devices** within the vehicle (same allowance as for batteries).

### 6.1.1 Sign convention for current
Positive = **discharging**; negative = **charging**. *(Same convention as the battery section, 5.1.2.1.)*

### 6.1.2 Reference location for ambient temperature
Measured within **1 m** of the capacitor UUT, at a manufacturer-indicated point.

### 6.1.3 Thermal conditions
- "Capacitor testing temperature" (target operating temperature) specified by the manufacturer; all capacitor-cell temperature measuring points within manufacturer limits throughout all test runs.
- **Liquid-conditioned**: conditioning-fluid temperature at capacitor UUT inlet maintained within **±2 K** of a manufacturer-specified value.
- **Air-cooled**: temperature at a manufacturer-indicated point kept within **+0 / −20 K** of the manufacturer-specified maximum.
- Available cooling/heating power on the testbench limited to a declared value, recorded with test data. Determination:
  1. Liquid conditioning: from conditioning-fluid mass flow and ΔT over the heat exchanger (capacitor UUT side).
  2. Electric conditioning: from voltage and current (manufacturer may re-wire the conditioning unit for certification to exclude conditioning power from the measured characteristics, but the externally-provided power must still be recorded).
  3. Other: good engineering judgement, agreed with the type-approval authority.

## 6.2 Test conditions

(a) Capacitor UUT placed in a temperature-controlled test cell, ambient conditioned at **25 ± 10 °C**.
(b) Voltage measured at the capacitor UUT terminals.
(c) The capacitor UUT's thermal conditioning system and the test-bench's corresponding loop fully operational per their respective controls.
(d) The control unit (CCU) enables the test bench to perform the requested procedure within the capacitor UUT's operational limits; its program may be adapted by the manufacturer for the test, if necessary.

## 6.3 Capacitor UUT characteristics test

(a) After fully charging then fully discharging the capacitor UUT to its lowest operating voltage (per the manufacturer's specified charging method), **soak for ≥ 2 hours but ≤ 6 hours**.
(b) Capacitor UUT temperature at test start: **25 ± 2 °C**. Alternatively, **45 ± 2 °C** may be selected if reported to the approval/certification authority as more representative of the typical application's conditions.
(c) After the soak, perform a complete charge/discharge cycle per **Figure 2** with constant current **$I_{test}$** = the maximum allowed continuous current for the capacitor UUT, as specified by the manufacturer.
   **[Figure 2 — "Example of voltage curve for the capacitor UUT measurement" — referenced in source but not visually extracted from this text-only OCR.]**
(d) Procedure detail:
   - After a **≥30-second waiting period ($t_0$ to $t_1$)**, charge at constant $I_{test}$ until **$V_{max}$** (maximum operating voltage) is reached.
   - Stop charging; **soak 30 seconds ($t_2$ to $t_3$)** for voltage to settle to its final value **$V_b$**.
   - Discharge at constant $I_{test}$ until **$V_{min}$** (lowest operating voltage) is reached.
   - From **$t_4$ onward**, another **≥30-second** waiting period for voltage to settle to its final value **$V_c$**.
(e) Current and voltage over time ($I_{meas}$, $V_{meas}$) recorded at **≥10 Hz**.
(f) Characteristic values determined (illustrated in Figure 2):
   - **$V_a$**: no-load voltage right before the charge pulse starts.
   - **$V_b$**: no-load voltage right before the discharge pulse starts.
   - **$V_c$**: no-load voltage after the discharge pulse ends.
   - **$\Delta V(t_1)$, $\Delta V(t_3)$**: voltage changes directly after applying constant current $I_{test}$ at $t_1$ and $t_3$ respectively — determined via a **linear approximation** to the voltage characteristic (per "detail A" of Figure 2) using the **least-squares method**. Data sampling for the straight-line approximation starts once the gradient change between two adjacent data points is **< 0.5 %**, moving in the direction of increasing time.
   - **$\Delta V(t_1)$** = absolute difference between $V_a$ and the intercept value of the straight-line approximation at $t_1$.
   - **$\Delta V(t_3)$** = absolute difference between $V_b$ and the intercept value of the straight-line approximation at $t_3$.
   - **$\Delta V(t_2)$** = absolute difference between $V_{max}$ and $V_b$.
   - **$\Delta V(t_4)$** = absolute difference between $V_{min}$ and $V_c$.

## 6.4 Post-processing of measurement data of the capacitor UUT

### 6.4.1 Calculation of internal resistance and capacitance

(a) **Capacitance** for charging and discharging:
$$C_{charge} = \frac{\int_{t_1}^{t_2} I_{meas}\, dt}{V_b - V_a} \qquad\qquad C_{discharge} = \frac{\int_{t_3}^{t_4} I_{meas}\, dt}{V_c - V_b}$$

(b) **Maximum current** for charging and discharging:
$$I_{max,charging} = \frac{\int_{t_1}^{t_2} I_{meas}\, dt}{t_2 - t_1} \qquad\qquad I_{max,discharging} = \frac{\int_{t_3}^{t_4} I_{meas}\, dt}{t_4 - t_3}$$

(c) **Internal resistance** for charging and discharging:
$$R_{charge} = \frac{\Delta V(t_1) - \Delta V(t_2)}{2\, I_{max,charging}} \qquad\qquad R_{discharge} = \frac{\Delta V(t_3) - \Delta V(t_4)}{2\, I_{max,discharging}}$$

(d) For the model, **only a single capacitance and resistance** are needed:
$$C = \frac{C_{charge} + C_{discharge}}{2} \qquad\qquad R = \frac{R_{charge} + R_{discharge}}{2}$$
*(OCR note: source renders the connecting operator between the two terms as what looks like a subtraction glyph, but physically and dimensionally an average of a charge-phase and discharge-phase estimate of the same property is the only sensible construction — reconstructed as an arithmetic mean. If a literal difference were intended, C and R would not be well-defined single model parameters; flagging for verification against the original PDF.)*

(e) **Maximum voltage** = the recorded value of $V_b$; **minimum voltage** = the recorded value of $V_c$ (both from point 6.3(f)).

---

## Cross-reference to standard (default) capacitor values

Where certification uses **standard values** instead of measurement, Appendix 10 point (2) gives the full default-generation method: rated capacitance and voltage scaled from cell datasheet values; $V_{min,Cap} = 0.45 \times V_{max,Cap}$; a reference-based internal-resistance formula using $R_{I,ref}=0.00375\,\Omega$, $V_{ref}=2.7\,V$, $C_{ref}=3000\,F$; and max charge/discharge current = capacitance [F] × **5.0 A/F**. Fully reproduced in file **12h-annex-xb-standard-values-and-simulation-input-parameters.md**. The XML input-parameter schema (`Capacitance`, `InternalResistance`, `MinVoltage`, `MaxVoltage`, `MaxChargingCurrent`, `MaxDischargingCurrent`, `TestingTemperature`, parameter IDs P532–P544) is in Appendix 15, also in file 12h.
