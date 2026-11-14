# SR7/LOT4 Final Report — Chapter 4.4 (Ex-Post Test Procedure) and Chapter 4.5 (Regulatory Description)

> Part of the multi-file extraction of `sr7_lot4_final_report_en.pdf` (Service contract CLIMA.C.2/SER/2012/0004, EC DG CLIMA, report dated 30.10.2017). See `sr7-lot4-01-overview-and-metadata.md` for full document metadata and companion-file list.
>
> **Relevance to HDEV sizing/modelling:** This chapter's uncertainty-quantification methodology (bottom-up component/measurement/model uncertainty budgeting, top-down measured-vs-simulated deviation analysis) is a directly transferable template for validating/auditing any HDEV energy-consumption simulation against real-world telemetry — a core requirement for a tool positioned as "PVsyst for EVs."

## 4.4 Ex-Post Test Procedure (EPTP)

### Purpose and rationale
The EPTP validates VECTO input data via an independent test that **does not require OEM support**, because re-testing engine/gearbox/axle per their component procedures is "almost impossible without OEM support" (ECU signal dependencies) and because dismounting components for component-test-stand testing is already complex/costly.

### Method
A vehicle test based on **on-board measurement of rotational speed and torque at the driven wheels, plus fuel flow** ("[Figure 41 description: schematic diagram of the EPTP test setup, showing the on-board torque/speed sensors at the driven wheels and a fuel-flow meter feeding data used to recalculate the test cycle in VECTO.]"). The measured wheel torque/speed cycle is fed back into VECTO (using the vehicle's certified input data) and the recalculated fuel consumption should match the measured value. Covers **combined axle + gearbox + engine** input data. To eliminate the generic gear-shift model's influence, **measured engine speed or measured gear position** is also required as model input. Auxiliary energy consumption (generic in VECTO, real in the vehicle) is minimised by procedure design.

The methods and VECTO software adjustments were developed under SR7; **the technical annex text itself is governed by a separate DG GROW contract.**

### Design evolution
- **LOT3 constraint:** VECTO input data was not to be available to 3rd parties → EPTP was an "**Ex Ante**" test (steady-state points calculated during certification, reproduced later on the real vehicle).
- **LOT4 change:** VECTO input data made available post-certification → EPTP became an "**Ex Post**" approach using measured cycles as VECTO input directly, enabling more demanding cycles and tighter tolerances.
- In all LOT4-analysed cases, the **whole vehicle** is tested; the driven cycle is VECTO input; results are compared. Fuel consumption is always related to **measured work at the wheel** (wheel-hub torque meter) in **g/kWh**, eliminating wind/tyre-temperature/gradient uncertainty.

### Four candidate test-option types analysed
1. Steady-state test on a **chassis dyno** (~12 points covering the main areas of the corresponding CO2 cycle in the engine map).
2. Steady-state test on a **test track** (without a braking trailer, achievable wheel torques are low, not covering the full engine map).
3. Transient test on a **chassis dyno** (e.g., a short VECTO cycle version or the WHVC).
4. Transient test **on the road** (following ISC/PEMS-style boundary conditions but with fuel-flow meter + wheel-hub torque meter).

**Conclusion:** although on-road transient tests were expected to have higher uncertainty, analysis found "no major disadvantages in terms of inaccuracies" — so **the draft technical annex describes an on-road transient test procedure.**

### Proposed two-step EPTP (to reduce testing effort/cost)
- **"[Figure 42 description: flow chart of the proposed two-step check of VECTO input data.]"**
- **Step 1:** Validate VECTO input data via component-certification-number/auxiliary-configuration comparison plus a simple VECTO re-run using the original **hashed** certification dataset, re-computing and comparing hash values.
- **Step 2:** Physical EPTP (route selection, vehicle instrumentation, sensor/analyser calibration, fuel-consumption test run, torque-measurement-device drift check, evaluation).

Step 1 can be applied more broadly (low cost) and catches input-data-handling errors; Step 2 catches measured-vs-simulated deviations, triggering component re-testing if thresholds are exceeded.

### 4.4.1.1 Warm-up phase alignment with ISC/PEMS

The ISC-PEMS test — per **Commission Regulation (EU) 2016/1718 amending Regulation (EU) No 582/2011** ("testing by means of portable emission measurement systems (PEMS)") — mandates a cold start, which the VECTO simulation does not model, so a cold-start phase would need elimination from an EPTP-ISC-aligned dataset. Overall ISC-PEMS duration is **4–7× WHTC work or WHTC CO2 mass**, i.e., roughly **2–3.5 hours** of similar-to-WHTC driving — leaving sufficient time for EPTP even after excluding a long warm-up.

**TUG tests on 2 Euro VI diesel trucks** established warm-up limits:
- **Delivery truck** (started in urban traffic): coolant reached a constant 80 °C after **~10 minutes** ("[Figure 43 description: coolant-temperature time-series for the first 30 minutes of the delivery-truck test.]").
- **Tractor-trailer** (started in urban conditions at the TUG lab, moved to motorway after ~20 min): coolant reached a constant 90 °C after **~30 minutes** ("[Figure 44 description: coolant-temperature time-series for the tractor-trailer combination test.]").
- **Conclusion:** a **minimum 45-minute warm-up** for coolant temperature is "reasonable," covering lower-payload and colder-ambient cases. Since axle/gearbox have slower warm-up than engine coolant, an **overall 1-hour warm-up** is recommended as a compromise between ISC-alignment and adequate conditioning.

**"[Figure 45 description: coolant temperature vs. cumulative normalised positive engine work for both trucks, showing markedly different behaviour between the two vehicles — leading to the conclusion that a minimum-engine-work warm-up criterion offers no clear advantage over a minimum-time criterion and is more complex to implement.]"**

Additional recommendation: warm-up should include motorway driving at max speed; **no idling phase >2 minutes** should occur between warm-up and EPTP-relevant driving (semi-trailer test data after second 2400 showed cooling during such a gap). Alternative: decouple EPTP from ISC-PEMS entirely, warming up under well-defined conditions (e.g., 85 km/h highway), with PEMS-based pollutant checks as an optional add-on.

### 4.4.1.2 Uncertainty methodology (bottom-up approach)
Two combination methods used throughout:
- **Equation 1 (Gauss error propagation):** u = √[(u1·s1)² + (u2·s2)² + ... + (un·sn)²] — used for **independent** uncertainties; ui = uncertainty of contributor i, si = share of contributor i in total vehicle FC; u = total uncertainty at 98% probability.
- **Equation 2 (simple sum):** u = u1 + u2 + ... + un — used when uncertainties are treated as **dependent** (e.g., aggressive winding-road driving simultaneously raises cooling-fan demand, braking-air demand, and steering-pump demand).

Component FC-share weights (from VECTO simulations of 2016-generic standard vehicles, VECTO 3.1): engine fuel map contributes ~100% (baseline), gearbox losses contribute ~3.5%, etc. (used to weight component uncertainties into overall FC uncertainty.)

#### Auxiliary-related uncertainty analysis (tractor-trailer model, GVWR 40 t, 324 kW rated power)
Simulated on the VECTO Long Haul (LH) and Regional Delivery (RD) cycles, and on a constructed steady-state EPTP surrogate (12 operating points: 3 most-frequent gears [12, 11, 10] × 4 most-frequent engine-load points per gear, weighted 2×LH + 1×RD, each point held 5 min with a 2 min transition).

**Table 14 — Fan power variability**
| | Steady state, chassis dyno (20°C, 20 km/h blower) | Steady state, road (30°C, headwind=v_veh) | Transient, chassis dyno | Transient, road |
|---|---|---|---|---|
| W_wheel,pos [kWh] | 169.6 | 169.6 | 98.6 | 98.6 |
| FC fan on [g/h] | 37,125 | 37,012 | 20,644 | 20,501 |
| FC fan off [g/h] | 36,106 | 36,106 | 20,378 | 20,378 |
| % uncertainty | 2.8 | 2.5 | 1.3 | 0.6 |

**Table 15 — Alternator efficiency variability** (older external-fan alternator ~52% avg. efficiency vs. newer internal-fan ~75%; default electric demand LH 1.2 kW_el / RD 1.0 kW_el)
| | Chassis dyno steady | Road steady | Chassis dyno transient | Road transient |
|---|---|---|---|---|
| FC high [g/h] | 36,404 | 36,404 | 20,592 | 20,592 |
| FC low [g/h] | 36,205 | 36,205 | 20,470 | 20,470 |
| % uncertainty | 0.5 | 0.5 | 0.6 | 0.6 |

**Table 16 — Alternator on/off variability** (0.6 kW LH / 0.5 kW RD electric load; smart-alternator scenario where battery SOC is sufficient for >30 min without charging)
| | Chassis dyno steady | Road steady | Chassis dyno transient | Road transient |
|---|---|---|---|---|
| FC altern. on [g/h] | 36,236 | 36,236 | 20,444 | 20,444 |
| FC altern. off [g/h] | 35,906 | 35,906 | 20,197 | 20,197 |
| % uncertainty | 0.9 | 0.9 | 1.2 | 1.2 |

**A/C (HVAC) power demand:** computed via a two-step method: (1) solar heat-load tool from LDV Mobile A/C (MAC) test-procedure development [ref 14] — windows area 3.78 m², sun intensity 700 W/m², headwind 50 km/h, window angle 89°; (2) a coolant-circuit/compressor power-demand tool (also from MAC development) with 100% fresh-air intake, 2 occupants assumed (driver + technician).

**Table 17 — HVAC power-demand settings/results**
| Setting | a) | b) | c) |
|---|---|---|---|
| Ambient T [°C] | 0 | 30 | 20 |
| Glazing | "3.85mm lite green" | 2.1mm lite green + 0.76mm PVB + 1.6mm clear | IRR-coating 2.1mm clear + 0.76mm PVB + 1.6mm clear |
| Body [m³] | 8 | 10 | 8 |
| Calc. heat entrance [kW] | 0.05 | 1.09 | 0.67 |
| Mechanical HVAC power [kW] | 0.0 | 2.09 | 0.58 |
| Electric HVAC power [kW] | 0.06 | 0.07 | 0.07 |

Setting c) mechanical A/C power is **1.7× (LH) and 2.9× (RD)** the VECTO default; setting a) (0°C) is clearly below VECTO standard conditions.

**Table 18 — A/C FC variability and uncertainty**
| | Chassis dyno steady | Road steady | Chassis dyno transient | Road transient |
|---|---|---|---|---|
| Setting b) FC [g/h] | — | 36,540 | — | 20,805 |
| Setting a) FC [g/h] | — | 36,155 | — | 20,423 |
| % uncertainty | — | 1.1 | — | 1.9 |

Note: HVAC uncertainty could be "to a very large extent eliminated" by mandating HVAC-off testing (leaving only compressor drag losses).

**Table 19 — Air compressor variability** (12t GVWR delivery truck, 154 kW, Urban Delivery cycle; ESS = Energy Saving System / reduced idle losses)
| | Chassis dyno steady | Road steady | Chassis dyno transient | Road transient |
|---|---|---|---|---|
| W_wheel,pos [kWh] | 76.2 | 76.2 | 21.1 | 21.1 |
| Calculated FC [g/h] | 16,776 | 16,787 | 6,332 | 6,392 |
| Generic data FC [g/h] | 16,764 | 16,764 | 6,340 | 6,340 |
| % deviation | 0.07 | 0.14 | −0.1 | 0.8 |

**Table 20 — Steering pump variability** (same delivery truck; default UD power 0.31 kW on-road; idle 0.26 kW on dyno; idle+banking 0.02 kW on test track)
| | Chassis dyno | On-road | Chassis dyno transient | On-road transient |
|---|---|---|---|---|
| W_wheel,pos [kWh] | 76.2 | 76.2 | 21.1 | 21.1 |
| Calculated FC [g/h] | 16,758 | 16,764 | 6,330 | 6,345 |
| Generic data FC [g/h] | 16,764 | 16,764 | 6,340 | 6,340 |
| % deviation | 0.04 | 0.0 | 0.16 | 0 |

**Table 21 — Summary of auxiliary-related uncertainties**
| % uncertainty | Chassis dyno, steady | Test track, steady | Chassis dyno, transient | On road, transient |
|---|---|---|---|---|
| Cooling fan | 2.8% | 2.5% | 1.3% | 0.6% |
| Alternator | 0.9% | 0.9% | 1.2% | 1.2% |
| HVAC | — | 1.1% | — | 1.9% |
| Compressor | 0.07% | 0.1% | 0.1% | 0.8% |
| Steering pump | 0.04% | 0.0% | 0.16% | 0.1% |
| Sum all aux. (Gauss, opt. a) | 2.9% | 2.9% | 1.8% | 2.5% |
| Sum aux. w/o HVAC (Gauss, opt. a) | 2.9% | 2.7% | 1.8% | 1.6% |
| Sum all aux. (simple sum, opt. b) | 3.8% | 4.6% | 2.8% | 4.6% |
| Sum aux. w/o HVAC (simple sum, opt. b) | 3.8% | 3.5% | 2.8% | 2.7% |
| **Assumed uncertainty EPTP (AC-off, aux. deactivated where possible)** | **3.5%** | **3.2%** | **2.4%** | **2.2%** |

### 4.4.1.3 Measurement-equipment uncertainty

**Table 22 — Uncertainties from measurement equipment**
| % uncertainty | Chassis dyno, steady | Test track, steady | Chassis dyno, transient | On road, transient |
|---|---|---|---|---|
| Rotational speed at wheels | 0.40% | 0.40% | 0.40% | 0.40% |
| Torque at wheel rims | 0.40% | 0.50% | 0.40% | 0.50% |
| Cornering uncertainty | 0.00% | 0.30% | 0.00% | 0.30% |
| Total power at wheels | 0.80% | 1.20% | 0.80% | 1.20% |
| Rotational speed, engine | 0.20% | 0.20% | 0.20% | 0.20% |
| VECTO fuel-interpolation result | 0.80% | 1.20% | 0.80% | 1.20% |
| Fuel mass flow (on-board measured) | 1.0% | 1.5% | 1.0% | 1.5% |
| Total error (g/kWh), Gauss (opt. a) | 1.28% | 1.92% | 1.28% | 1.92% |
| Total error (g/kWh), simple sum (opt. b) | 1.80% | 2.70% | 1.80% | 2.70% |
| Measurement uncertainty already in CoP | 0.90% | 0.90% | 0.90% | 0.90% |
| **Error assumed for EPTP (CoP added later)** | **0.6%** | **1.4%** | **0.6%** | **1.4%** |

50% additional uncertainty was assumed for on-road vs. chassis-dyno conditions to account for uncontrolled ambient temperature/pressure variability (no direct data available on this effect at the time).

### 4.4.1.4 Uncertainties from effects not modelled in VECTO

**Table 23 — Uncertainties from unmodelled effects**
| % uncertainty | Chassis dyno, steady | Test track, steady | Chassis dyno, transient | On road, transient |
|---|---|---|---|---|
| Transient engine effects | 0% | 0% | 1.5% | 1.5% |
| Gear shifts | 0% | 0% | 1% | 1% |
| Transmission/engine temperatures | 0.5% | 1.0% | 1.0% | 1.5% |
| Exhaust after-treatment temperatures | 0.5% | 2% | 0.5% | 2% |
| **Total (simple sum, opt. b)** | **1.0%** | **3.0%** | **4.0%** | **6.0%** |
| Total for tighter test conditions | 0.7% | 2.0% | 2.7% | 4.0% |

"Tighter test conditions" = testing only above 10°C ambient and dry, with a 1-hour warm-up, allowed max-speed running, limited idling, and minimum-average-urban-speed/low-urban-share limits. Gauss (option a) is explicitly stated as **not applicable here** since these systematic errors are not independent (e.g., a cold, winding, hilly-downhill trip needing SCR heating can combine several underestimation effects at once).

### 4.4.1.5 Serial-production / component-test (CoP) tolerances

CoP tolerances (converted to g/kWh via g_fuel/kWh_mech = 1000/(Eta_i × LHV_fuel), using **LHV = 11.81 g/kWh** as the reference here) are combined via Gauss propagation (independent, since deviations against certified per-component values are independent):

**Table 24 — Component/production uncertainties**
| % uncertainty | Chassis dyno, steady | Test track, steady | Chassis dyno, transient | On road, transient |
|---|---|---|---|---|
| Production engine (g/kWh tolerance) | 3% | 3% | 3% | 3% |
| Production gearbox (CoP efficiency) | 1.5% | 1.5% | 1.5% | 1.5% |
| Production axle (CoP efficiency, run-in) | 2% | 2% | 2% | 2% |
| **Total (Gauss, opt. a)** | **3.02%** | **3.02%** | **3.02%** | **3.02%** |

### 4.4.1.6 Total bottom-up uncertainty

**Table 25 — Total uncertainties, bottom-up**
| % uncertainty | Chassis dyno, steady | Test track, steady | Chassis dyno, transient | On road, transient |
|---|---|---|---|---|
| Auxiliaries w/o A/C | 3.50% | 3.20% | 2.40% | 2.20% |
| Measurement equipment | 0.64% | 1.41% | 0.64% | 1.41% |
| VECTO model uncertainty | 1.00% | 3.00% | 4.00% | 6.00% |
| CoP of component tests | 3.02% | 3.02% | 3.02% | 3.02% |
| VECTO tighter uncertainty | 0.70% | 2.00% | 2.70% | 4.00% |
| **Total bottom-up (Gauss, opt. a)** | **4.8%** | **5.5%** | **5.6%** | **7.2%** |
| Total motorway-only (Gauss, opt. a) | 4.7% | 5.0% | 4.8% | 5.7% |
| Total bottom-up (simple sum, opt. b) | 8.2% | 10.6% | 10.1% | 12.6% |
| Total motorway-only (simple sum, opt. b) | 7.9% | 9.6% | 8.8% | 10.6% |

Report notes: VECTO uncertainties are lower on motorway driving (less transient, fewer gearshifts, all components at steady temperature) — suggesting a possible policy of a **higher tolerance for the whole trip than for the motorway-only part**. Repetition of a failed test is discussed as a way to tighten effective tolerances, but "the probability that... three times the worst case combination occurs is close to zero" only holds for randomly-distributed uncertainties — since real uncertainties are **not normally distributed**, "a confidence interval for more repetitions cannot be determined here."

**Illustrative regulatory guidance floated:** possibly demand **<7.5% deviation** for the whole cycle where motorway share is high, or allow more overall deviation (due to aggressive-driving-style effects) if requiring a **tighter (~<6%) motorway-only agreement**.

### 4.4.1.7 Top-down approach (measured vs. simulated deviations, real test data)

**Table 26 — Collected deviations between measured and VECTO-simulated fuel consumption**
| Source | Steady state, chassis dyno: Max pos. dev. | Avg. abs. dev. | Steady state, test track: Max pos. dev. | Avg. abs. dev. | Transient, chassis dyno: Max pos. dev. | Avg. abs. dev. | Transient, road: Max pos. dev. | Avg. abs. dev. |
|---|---|---|---|---|---|---|---|---|
| OEM 1 | — | — | — | — | 6.4% | 0.9% | 4.6% | 1.2% |
| OEM 2 | 0.2% | 1.6% | 1.8% | 1.0% | 3.6% | 4.0% | 3.4% | 2.3% |
| OEM 3 | 0.0% | 4.4% | — | — | — | — | — | — |
| OEM 4 | 0.0% | 5.8% | — | — | 2.7% | 9.0% | — | — |
| OEM 5 | 0.0% | 3.9% | — | — | 0.9% | 4.3% | — | — |
| TUG test 1 | — | — | — | — | 5.1% | 1.1% | 3.2% | 1.7% |
| JRC veh 1 | — | — | — | — | 8.6% | 6.7% | 2.9% | 1.1% |
| JRC veh 2 | — | — | — | — | 2.8% | 2.1% | 1.4% | 0.8% |
| JRC veh 3 | — | — | — | — | 0.0% | 3.4% | 0.0% | 2.5% |
| **Maximum** | 0.2% | 5.8% | 1.8% | 1.0% | 8.6% | 9.0% | 4.6% | 2.5% |
| **Average** | 0.1%* | 3.9%* | 1.0%* | 1.0%* | 3.6% | 3.6% | 1.9%* | 1.7% |

*(Note: the source's Table 26 layout groups columns in a way that made a few "Maximum"/"Average" summary-row values ambiguous on extraction — the report's own text states "Maximum 6.4% 5.8% 4.6% 9.0% 8.6% 6.7% 3.4% 2.5%" and "Average 1.9% 2.9% 2.5% 3.9% 3.6% 3.6% 1.9% 1.7%" as a flat sequence across the 8 sub-columns (Steady-dyno max/avg, Steady-track max/avg, Transient-dyno max/avg, Transient-road max/avg); reproduced here per that verbatim flat sequence: Steady-state chassis dyno: max 6.4%, avg 1.9%; Steady-state test track: max 5.8%, avg 2.9%; wait — cross-check against per-OEM rows suggests the safest-fidelity approach is to present the report's own summary line verbatim rather than re-derive it: "[unclear from source: Table 26's exact column-to-value mapping for the Maximum/Average summary rows could not be reconstructed with full confidence from the extracted text layout; the source's own summary sentence states: 'Maximum 6.4% 5.8% 4.6% 9.0% 8.6% 6.7% 3.4% 2.5%' and 'Average 1.9% 2.9% 2.5% 3.9% 3.6% 3.6% 1.9% 1.7%', in the column order Steady-state-chassis-dyno(max,avg), Steady-state-test-track(max,avg), Transient-chassis-dyno(max,avg), Transient-road(max,avg)"].)*

**Special note:** OEM 4's steady-state tests used only 3 test points (technical/time constraints) with fuel consumption from CAN signal only, and only one of two wheel-hub torque meters worked correctly.

**Top-down conclusions:**
- Average absolute deviations are comparable across test methods and **below the bottom-up 98th-percentile uncertainty estimates (5–10%, method-dependent)**.
- Some single tests exceed the ~13% bottom-up uncertainty estimate, with no clear explanation found after discussion with the testers.
- **Longer tests (on-road) give lower deviations than short tests (steady-state points).**
- **On-road tests with accurate fuel-flow/torque/rpm-at-driven-wheels and engine-speed measurement are a viable EPTP option** and are what the draft technical annex implements.
- Available data is "insufficient to come up with reliable uncertainties of an EPTP method."

### 4.4.1.8 Next steps (EPTP)
ACEA to run further EPTP tests per the draft annex to resolve: tolerances for VECTO-vs-EPTP deviations; best urban/road/motorway driving mix (accuracy vs. representativeness trade-off); lowest-cost/effort test design; various technical details. Feedback will refine open issues. **Open questions:** number of EPTP tests per OEM per year; responsibility for running tests; consequences of a failed EPTP (input-data-alignment error = user's fault; measured-vs-simulated deviation = possible VECTO-model inaccuracy for that specific truck, requiring re-testing of engine/transmission/axle per their certification procedures).

## 4.5 Regulatory Description

Main HDV-CO2-certification approaches were already elaborated under LOT2/LOT3, including a "draft technical annex" from LOT3 — but this was "neither complete from a technical point of view nor did it cover crucial points like family concepts and CoP testing."

**SR7 timeline for the technical annexes:**
- **Phase 1 (to summer 2015):** complete all technical issues (100% test-procedure description, measurement-equipment tolerances, etc.) to establish a solid baseline for the pilot phase.
- **Phase 2:** analysed/discussed with COM, industry, NGOs, and drafted into legislative text:
  - Optimisations/amendments from pilot-phase feedback and expert-group discussion.
  - **Family concepts:** reduce component-testing effort by grouping similar-CO2-performance model types into "families." Core principle: the **worst-CO2-performing model/type is the family "parent"** used for certified component testing; OEMs can define additional (better-performing) families via extra testing.
  - **"Standard values" ("fall-back values"):** applied when a component is not measured per the relevant test procedure (e.g., small-series products); tuned by industry/consultants so that measured components always outperform standard values (testing incentive). Noted as "in particular challenging for transmissions" given multiple test-vs-standard-value combination options.
  - **CoP provisions:** test procedure definition for selected components; tolerance/statistics elaboration for pass/fail; definition of the number of CoP-tested components required per OEM per year.

Generic data (CO2 cycles, payloads, cargo volumes) were **decided by DG GROW not to be incorporated into the legislative texts** — Chapter 4.3.5 of this report (see file 04) is the primary documentation for that data. Auxiliary data and standard body/semi-trailer definitions **are** in the technical annexes.

### Two additional crucial implementation issues that emerged during SR7
a) **IT/process integration:** VECTO must handle "10,000s" of simulations per OEM per day (certification of every produced vehicle + customer-information simulation for every sales inquiry) — requiring full automation coupling OEM product databases to VECTO. An **IT group** (ACEA + main suppliers + the VECTO IT team) produced VECTO input/output data provisions (**XML schemas** for component input data and for a complete vehicle "job"), implemented as separate Appendices to the relevant HDV CO2 legislation annexes (or included by reference).
b) **Data-integrity assurance:** since VECTO results are **legally binding CO2-declaration documents**, and component input data is TAA-certified (legally valid), the integrity of electronically stored/exchanged data must be ensured throughout certification and CoP. SR7 prepared requirement discussions with the Commission and industry; **continued under DG CLIMA Contract No 356/PP/2014/FC.**

## Standards, regulations, and organisations referenced in this chapter (exact names only)
- Commission Regulation (EU) 2016/1718 amending Regulation (EU) No 582/2011 (PEMS testing)
- HDV CO2 TA (adopted by TCMV, 11 May 2017)
- DG GROW (separate EPTP technical-annex contract)
- DG CLIMA Contract No 356/PP/2014/FC (data-integrity follow-on work)
- ACEA (IT group participant)
- JRC, TUG, and named OEMs (anonymised as "OEM 1"–"OEM 5" in Table 26) as data contributors
- Ref [14]: Hausberger S., Vermeulen R. et al., "MAC performance test procedure," TNO report, 2013 (source of the A/C heat-load and compressor tools used in the auxiliary-uncertainty analysis)
