# SR7/LOT4 Final Report — Chapter 4.2: Component Test Procedures

> Part of the multi-file extraction of `sr7_lot4_final_report_en.pdf` (Service contract CLIMA.C.2/SER/2012/0004, EC DG CLIMA, report dated 30.10.2017). See `sr7-lot4-01-overview-and-metadata.md` for full document metadata and the list of companion files.

## Context

Chapter 4.2 describes the four physical component test procedures underpinning VECTO input data: **Engine**, **Air drag**, **Transmission**, and **Axle**. These generate the certified physical parameters (fuel maps, CdxA, loss maps, ratios) that VECTO uses as simulation inputs. This chapter is highly relevant to any HDV/HDEV sizing tool insofar as it defines the rigor and structure of the input-data pipeline (test → pre-processing tool → simulation input) that a credible tool should mirror, even where the underlying physical component (e.g., an ICE) is replaced by an electric powertrain component.

## 4.2.1 Engine Test Procedure

**Purpose:** determine maximum engine power capability, motoring (drag) torque, and fuel consumption at defined steady-state operating points, plus correction factors for transient effects (since the fuel map itself is steady-state-derived).

### Table 1 — Test runs required for a complete engine test procedure
| Test run | Required for CO2-parent engine | Required for other engines within CO2-family |
|---|---|---|
| Engine full load curve | yes | yes |
| Engine motoring curve | yes | no |
| WHTC test | yes | yes |
| WHSC test | yes | yes |
| Fuel consumption mapping cycle (FCMC) | yes | no |

### Key improvements made during SR7 (relative to prior UN/ECE Regulation 49 baseline)
- Careful alignment with UN/ECE Regulation 49 procedures, because of the NOx/fuel-consumption trade-off — aligning pollutant and fuel-consumption test procedures is described as "of the utmost importance for getting realistic fuel consumption figures."
- A refined **engine CO2-family** concept (built on existing UN/ECE R49 family definitions): engines sharing design parameters and fuel-consumption characteristics can share the FCMC result (a single test run exceeding **3 hours**), reducing OEM test burden.
- Stricter laboratory test-condition (temperature, atmospheric pressure) definitions than UN/ECE R49.
- Clearer test-bed installation and auxiliary-configuration provisions (e.g., cooling fan, electric consumers) with correction methods for auxiliary power drawn during testing.
- Additional provisions for testbed engine-cooling conditioning to prevent gaming via optimized cooling.
- Extended measurement-equipment specifications (linearity, accuracy, dynamic behaviour) with stricter limits than UN/ECE R49.
- Standards for determining **Net Calorific Value (NCV)** of test fuels, with correction of results to standard reference-fuel NCV values (**except Diesel** — see below).
- Significant FCMC procedure improvements:
  - Provisions for handling test interruptions.
  - Preconditioning provisions.
  - A defined grid of target set-points ("[Figure 1 description: a plot of engine torque vs. engine speed defining a full-load-curve-bounded region divided into 4×4 equidistant torque/speed sections between characteristic speeds n_idle, n_A, n_B, n_95h, used to define the FCMC measurement grid.]").
  - A defined emission-monitoring procedure during FC recording, using specific mass emissions (g/kWh) evaluated within grid cells inside a "control area" based on UN/ECE R49 Not-To-Exceed provisions ("[Figure 2 description: engine-torque vs. engine-speed map showing an upper boundary (increased full-load curve) and lower boundary (lowest-rating full-load curve in the CO2-family), with 1/3-1/3-1/3 subdivisions marking the grid cells used for emissions monitoring, bounded by characteristic speeds n30 and nhi.]").
  - Exact calculation definitions for cycle-integrated fuel consumption and engine work (not present in UN/ECE R49) — needed for correction-factor and CoP limit-value calculation consistency.
  - **WHTC-correction-factor** and **Cold-Hot-Balancing-Factor**, derived per-engine from WHTC test runs, applied to base fuel-map consumption to represent dynamic-operation effects and to prevent gaming (optimizing hot-start fuel consumption at the cost of raised cold-start consumption to stay under emission limits). An additional correction factor accounts for extra fuel consumption from periodic DPF regeneration.
  - CoP (Conformity of Production) test-run count defined independent of an OEM's chosen CO2-family granularity size — "neutral approach" so neither small-family nor large-family strategies are penalized for equal annual production volume; connected to the same pass/fail emission-limit logic via a "refined statistic approach."

**Footnote (fuel correction, Diesel exception):** "For Diesel fuel it was preliminarily concluded that the spread in NCV values is in the same magnitude than the analytics for the determination of NCV values. Hence this correction would not add any accuracy to the test results." Test fuel properties must still be reported in certification documents regardless.

**Stated overall goals of these improvements:** increase accuracy, repeatability, and reproducibility; improve testbed practicality; close potential certification "loopholes."

## 4.2.2 Engine Pre-processing Tool ("VECTO Engine")

Mandatory tool to compute VECTO engine input data from raw engine-test data. SR7 improvements:
- Ongoing compatibility updates with the evolving technical annex.
- More user-friendly interface; practical certification-process considerations.
- Automatic input-data compliance checks against the technical annex.
- Standardized fuel-map extrapolation to cover full-load-curve "knees" between target speed set-points.
- Standardized WHTC simulation for WHTC-correction-factor calculation.
- Standardized Cold-Hot-Balancing-Factor calculation.
- Standardized correction of fuel-map values to standard NCV (eliminating within-spec NCV variation effects).
- Conversion of full-load/motoring curves to VECTO's required (lower) logging frequency.
- "[Figure 3 description: screenshot of the VECTO Engine pre-processing tool's graphical user interface — not further described textually in the source beyond the caption.]"

## 4.2.3 Air Drag Test Procedure

**Purpose:** determine Cd×Afr (air drag coefficient × frontal area) at zero-yaw (β=0) conditions via a **constant speed test** on a straight test track.

**Method:** simultaneous measurement of driven-wheel torque, vehicle velocity, actual air-flow velocity (vehicle velocity + wind), and air-flow direction, at two constant speeds:
- **Low speed:** target range **10–15 km/h**
- **High speed:** target range **85–95 km/h** (or max achievable, with tolerance, if unattainable)

**Physical assumptions used to derive road load ("[Figure 4 description: schematic plot separating total road-load force into a constant rolling-resistance component and a velocity-squared-dependent air-drag component, illustrating how the two-speed test isolates each]"):**
- Rolling resistance force (Frol) is assumed **independent of vehicle speed**.
- Air-drag force increases **quadratically** with air velocity.

**Instrumentation:** high-precision positioning (opto-electronic barriers or DGPS), weather data, vehicle sensor data; detailed per-instrument/per-signal provisions specified.

### SR7-era improvements
- More detailed boundary conditions: payload, tyre conditions, preconditioning, test sequence.
- Comprehensive data-validity criteria for evaluation.
- Elaborated tolerances for all measurement systems.
- Extended evaluation algorithms (e.g., CdxA correction for reference-height deviation and anemometer influence).
- Revised norm-trailer specifications.

### Tyre rolling-resistance speed-dependency investigation (a key SR7 finding)
Based on tyre-industry test-drum data and IPW test-track tests for ACEA (ref [5]):
- In typical test conditions, tyre rolling resistance is **about 15% lower** in the low-speed test than the high-speed test (low-speed test driven right after high-speed test, so tyre temperature/pressure remain elevated but internal friction is lower at low speed).
- Assuming **speed-independent** rolling resistance yields CdxA values that are **conservatively 5–10% higher** than if the known speed-dependency were used.
- At **high tarmac temperatures (sunny, >40 °C surface)**, the speed-dependency **reverses** — low-speed rolling resistance becomes equal to or higher than high-speed — which harms repeatability/reproducibility.

### Resulting decisions (final procedure)
- Valid tests limited to **tarmac surface temperature ≤ 40 °C**.
- Evaluation uses the **simplified speed-independent rolling-resistance assumption** (mechanisms not fully understood; insufficient cross-tyre/cross-track data for a more detailed model) — acknowledged to yield CdxA values 5–10% higher than a speed-dependent model would.
- The VECTO Air Drag tool already implements the prerequisites (e.g., "altitude correction" option) for a future more accurate method, pending more speed-dependency data.

**Repeatability:** constant-speed tests on identical vehicles, repeated multiple times, show a **standard deviation of 2.5%** — consistent with (preliminary, end-of-LOT3) DG JRC analysis.

### Family concept and CoP for air drag
- Air drag is treated specially: "every single vehicle has its unique air drag characteristics" from a purely scientific standpoint, so the family concept focuses on identifying the **main CdxA-relevant vehicle characteristics** (cabin/roof geometry, aerodynamic add-ons like spoilers/side panels) as the primary target of future aerodynamic optimisation, while excluding less-relevant, usage-driven parameters (wheelbase, frame height, tyres) from family criteria to limit test burden.
- All certified CdxA values refer to **standard body and trailer designs** as defined in the HDV CO2 TA.
- **CoP tolerance for CdxA = 3 × assumed test repeatability = 3 × 2.5% = 7.5%.** CoP testing repeats the full constant-speed procedure under conditions close to certification testing (to reduce ambient-condition uncertainty contribution).

## 4.2.4 Air Drag Pre-processing Tool ("VECTO Air Drag")

SR7 improvements:
- Full compatibility with the latest constant-speed test technical annex.
- More user-friendly version incl. "direct start" option.
- Two modes, mirroring VECTO itself: **"Declaration Mode"** (fixed settings/validity criteria per the technical annex — the only mode in which certified CdxA values may be calculated) and **"Engineering Mode."**
- An accompanying MS Excel pre-processing tool distributed with the software for measurement visualisation and pre-checks.
- Fully documented in a dedicated user manual.
- Footnote: the (separate) **SR9 Bridge contract** plans to implement input-data **hashing** into VECTO Air Drag, available only in Declaration Mode following a valid CdxA calculation.

## 4.2.5 Transmission Test Procedure

**VECTO transmission inputs:** gear ratios, loss maps (torque loss as function of input speed and input torque), gear-dependent input torque/speed limits.

Three loss-assessment options (carried over from LOT3, refined during SR7); the standard torque-loss calculation procedure was separated out into its own technical-annex appendix:

- **Option 1** — Measurement of torque-independent losses + calculation of torque-dependent losses. SR7 added: detailed torque-dependent-loss calculation covering all transmission types; a measurement-uncertainty consideration concept; treatment of smart lubrication systems and transmission-specific electric auxiliaries.
- **Option 2** — Measurement of torque-independent losses + measurement of torque loss at maximum torque + **linear interpolation** of torque-dependent losses. Described as "a well-balanced compromise between measurement effort and accuracy."
- **Option 3** — Full measurement of total torque loss (most complex). SR7 added measurement-uncertainty treatment and new-technology (smart lubrication) consideration.

Also elaborated: separate methods for **torque converters**, other torque-transferring components (**retarders**), and additional driveline components (**angle drives**); calculated standard torque-loss values were extended to retarders, geared angle drives, and a **generic torque-converter model**.

**No standardised evaluation tool exists for transmissions** — OEMs must post-process test-stand data and generate standard loss maps using their own internal scripts.

## 4.2.6 Axle Test Procedure

Two options to determine driven-axle torque losses (for CO2 impact):

**Option 1 — Generic values (no physical test required):** load-dependent efficiency + basic drag torque at low load, refined during SR7 and allocated by specific axle category: **single reduction (SR), single reduction tandem (SRT), single portal (SP), hub reduction (HR), hub reduction tandem (HRT)**. Final category values verified by physical testing performed by expert-group members. Generic values are **intentionally set worse than measured values from low-efficiency components**, to incentivise actual component testing.

**Option 2 — Physical test:** measures output-torque vs. given input-torque difference on one representative "parent axle" of an "axle family" (family definition simplified from a formerly more complex sub-criteria structure). The parent axle is defined as the one with the **worst efficiency** among its performance-parameter group.

SR7 refinements to the physical-test procedure:
i. **Testing conditions:** oil/ambient-air temperature boundary conditions aligned to realistic real-life conditions with upper limits set to avoid overly optimistic results.
ii. **Testing environment/measurement accuracy:** installation and operating-characteristic descriptions for devices such as oil temperature conditioning systems, to ensure realistic results.
iii. **Test-bench setup:** detailed to minimize parasitic forces affecting torque measurement; an uncertainty-calculation method accounts for temperature, parasitic loads, and calibration errors, with different maximum-parasitic-load factors depending on bench setup/flexible-coupling installation.
iv. **Measurement data post-processing:** a defined conversion method turns the measured torque map into VECTO-compatible input data.

**No standardised component-test evaluation tool exists for axles either** (same situation as transmissions).

## Standards and organisations referenced in this chapter (exact names only)
- UN/ECE Regulation 49
- WHTC (World Harmonized Transient Cycle), WHSC (presumably World Harmonized Steady state Cycle — per abbreviations list, WHSC is used but full expansion not given verbatim in the abbreviations list excerpt seen; treat cautiously — [unclear from source: WHSC full name not explicitly spelled out in the extracted Abbreviations section, though WHTC is])
- ACEA (Reduced Rolling Resistance Study, ref. [5], performed by IPW at Klettwitz test track, report 429, 22 July 2015)
- HDV CO2 TA (Technical Annex)
- SR9 Bridge contract (a separate, later contract, referenced only in a footnote regarding hashing functionality)
