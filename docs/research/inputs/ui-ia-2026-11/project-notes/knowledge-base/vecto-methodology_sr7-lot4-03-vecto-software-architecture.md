# SR7/LOT4 Final Report — Chapter 4.3.1–4.3.4: VECTO Software Architecture, Simulation Approach, and Development Process

> Part of the multi-file extraction of `sr7_lot4_final_report_en.pdf` (Service contract CLIMA.C.2/SER/2012/0004, EC DG CLIMA, report dated 30.10.2017). See `sr7-lot4-01-overview-and-metadata.md` for full document metadata and companion-file list.

## 4.3.1 Overview

VECTO "models the main CO2 relevant components of heavy-duty vehicles and simulates a virtual drive on different routes." During SR7, VECTO was **significantly refactored from version 2.2 to version 3.2**: the simulation core was **rewritten from scratch in C#**, and the GUI was refactored to use the new core. Individual modules are separated via interfaces to allow different implementations/module swaps. The GUI is separated from the simulation core, enabling integration into OEM automated processes. The basic simulation approach was preserved.

## 4.3.2 Description

VECTO is a **vehicle longitudinal dynamics simulation tool** using a **backward simulation** approach: required engine speed/torque is computed from given wheel-side conditions (speed, acceleration), which are themselves set by the driving cycle (target speed, road gradient) and a driver model (e.g., max-acceleration limiting).

### 4.3.2.1 VECTO Software Modules and Architecture

"[Figure 5 description: block diagram of VECTO's software modules, showing separation of concerns between an Input module, a SimulationFactory module, individual Simulation Run components, and an Output module.]"

- **Input module:** reads all simulation-relevant parameters/model descriptions from multiple sources — multiple JSON/CSV files, single or multiple XML files, or a database backend. Interfaces defined in package `TUGraz.VectoCommon.InputData`.
- **SimulationFactory module:** different "factories" create required model parameters for a single simulation run from input + generic data, assemble the required powertrain, and prepare the run. For one vehicle, multiple runs are generated (different driving cycles, different payloads; vehicle configuration may also vary per cycle, e.g., an added generic trailer for some cycles). Runs are independent and can be executed sequentially or in parallel threads.
- **Simulation run:** contains all powertrain-component software modules + model parameters; simulates one combination of vehicle configuration × driving cycle × payload.
- **Output module:** collects all run results, generates reports (vehicle description, driving-performance parameters, fuel consumption/CO2). Two XML report formats currently generated: **Declaration Report** and **Customer Information**.

### 4.3.2.2 VECTO Vehicle Components and Model Parameters

Every energy-relevant powertrain component is a separate software component with defined mandatory interfaces, allowing modular assembly of different powertrain configurations as long as component input/output interfaces match.

**Minimal required components:** driving cycle, driver, vehicle, wheels, brakes, axle gear, transmission, clutch, combustion engine. Other components (retarder, torque converter, angle drive, auxiliaries) can be added where physically applicable.

"[Figure 6 description: overview diagram of the powertrain components' general structure as modelled in VECTO, showing the chain of components from driving cycle through to the internal combustion engine.]"

"[Figure 7 description: diagram illustrating the generic 'notation of a simulation component' — each component receives input parameters, holds internal model data, and produces output, per the convention described in Table 2.]"

Each component has: internal model data (e.g., measured loss-maps, fuel-consumption maps, or generic values), input parameters (e.g., power demand from the previous component, represented as a tuple such as force+velocity or torque+angular speed), and output. Because of backward simulation, **"model input" flows toward the wheel side** while **"model output" flows toward the engine side** — but parameter *naming* follows the normal (forward) power-flow direction (e.g., the gearbox's model *input* is named "gearbox torque out"/"gearbox angular speed out", while its *output* parameters are named "gearbox torque in"/"gearbox angular speed in"). Simulation time and interval are provided to every component in addition to component-specific inputs. Exceptions: "Driving Cycle" has no input (first component); "Engine" has no output listed as feeding a further component (last component).

### Table 2 — Model parameters and model input/output for all powertrain components

| Component | Model Input | Model Parameters | Model Output |
|---|---|---|---|
| Driving Cycle | None | Target speed, stop times, road gradient over distance | Current simulation distance; current target speed; current road gradient |
| Driver | Simulation distance; target speed; road gradient (loop through) | Generic acceleration and deceleration curve | Acceleration; road gradient |
| Vehicle | Acceleration; road gradient | Vehicle's mass; air drag coefficient Cd*A | Vehicle speed; force |
| Wheels | Vehicle speed; force | Dynamic tyre radius; rolling resistance (all wheels, incl. generic trailer) | Angular speed; torque |
| Brakes | Angular speed; torque | None | Angular speed; torque |
| Axle gear | Angular speed; torque | Gear ratio; loss-map | Angular speed; torque |
| Angle drive | Angular speed; torque | Gear ratio; loss-map | Angular speed; torque |
| Retarder | Angular speed; torque | Type of retarder; idle loss-map | Angular speed; torque |
| Transmission | Angular speed; torque | Type of transmission; per-gear gear ratio and loss-map | Angular speed; torque |
| Torque converter | Angular speed; torque | Characteristic curves for input torque and torque ratio | Angular speed; torque |
| Start-up Clutch | Angular speed; torque | None (generic model) | Angular speed; torque |
| Auxiliaries | Angular speed; torque | Technology for cooling fan, pneumatic system, steering pump, HVAC, electric system (from generic list) | Torque demand |
| Internal combustion engine | Angular speed; torque; torque demand of auxiliaries | Full-load curve; drag curve; fuel-consumption map; fuel type | Fuel consumption and CO2 emissions |

"[Figure 8 description: example diagram showing a virtual assembly of vehicle components for an MT/AMT vehicle with a transmission-output retarder, and the associated power flows, excerpted from the VECTO User Manual.]"

**Simulation Container:** holds all powertrain components and mediates data exchange during simulation; each component implements an information interface (e.g., `IGearboxInfo`, `IEngineInfo`) and the container forwards requests accordingly.

### 4.3.2.3 VECTO Basic Simulation Approach

The driving cycle is target speed over distance; every vehicle must be simulated over exactly the same distance, so the cycle is split into simulation steps whose distance adapts to current vehicle speed so each step covers **approximately 0.5 seconds**. The **Driver component performs the space-domain → time-domain transition**: given current velocity and the interval's acceleration, the time for the simulation distance is computed.

"[Figure 9 description: a UML-style sequence diagram illustrating the two-phase simulation-step process described below.]"

Each simulation step has two phases:
1. **Search phase:** find a valid operating point for all powertrain components (adjust vehicle acceleration until engine speed/torque land on a valid operating point).
2. **Commit phase:** finalize the step — write to the simulation trace (modal results), update internal component state, advance to the next step.

The search is done via requests propagated from the driving cycle through all components (each may transform the physical representation, e.g., Wheels converts velocity+force into angular velocity+torque for the next component); each component typically adds losses and forwards the request. If the request results in a valid operating point everywhere, the engine returns success; otherwise the relevant component signals failure and the driving strategy adjusts (see 4.3.2.4). "Dry-run" requests are used during search, with responses indicating how far a request exceeds validity; a successful search is confirmed with a repeat, real request.

For an interval [ti, ti+1], the general assumption is **constant acceleration** — so speed and angular velocity are linear functions and torque is constant *for most components*. This assumption fails for components with non-linear speed dependency (e.g., **air resistance force**, proportional to velocity squared). VECTO handles these via the **"energy-equivalent average force"**: it integrates the power loss (e.g., v_veh × F_airdrag) analytically over the interval and computes the equivalent average force from the vehicle's average speed in that interval. Similar treatment applies to other non-linear components (e.g., torque converter); where an analytic relation is unavailable, a **linear approximation** is used. Losses are computed/looked up in loss-maps using the interval's average power demand. Step output is the **average value** of each quantity (torque, speed, force, angular speed) across the interval.

"[Figure 10 description: 'Simulation Approach' diagram plotting acceleration (a), velocity (v), force (F), speed (N), and torque (T) over a simulation interval, with orange dots marking the output (average) values per step.]"

### 4.3.2.4 VECTO Driver Strategy

The driver component splits into: (1) the **driver** (basic driving actions) and (2) the **driver strategy** (decision logic for which action to take). Basic driving actions:
- **Accelerate:** powertrain closed (gear engaged, clutch closed); accelerate toward target speed within the driver model's acceleration limit; engine not overloaded; brakes inactive.
- **Coasting:** powertrain closed; engine operating at full drag load; acceleration adjusted to reach this operating point.
- **Roll:** powertrain open (no gear engaged); vehicle rolls unmotored; acceleration adjusted so gearbox input torque (engine side) is zero.
- **Brake:** powertrain open or closed; decelerate via mechanical brakes to the next target speed per the driver's deceleration curve; gearbox-input-torque condition depends on whether a gear is engaged.

The driving strategy must react to powertrain-component responses (e.g., a gearbox-shift response forces a switch to the Roll action, since no gear is engaged during traction interruption), making the strategy logic "rather complex."

**Handling target-speed changes (look-ahead):**
- **Speed increase:** simplest — acceleration starts exactly when the new higher target speed becomes effective; the driver only ensures the next simulation interval starts precisely at the speed-change point.
- **Speed decrease:** more complex — the vehicle must not exceed the new lower target speed once it takes effect, so deceleration (respecting the driver's max deceleration curve) must begin early enough. This is done in **two phases**: first **coasting** (using engine drag, i.e., releasing the accelerator), then **braking** (mechanical brakes at max deceleration). The coasting phase is omitted if vehicle velocity is below a threshold, or if coasting acceleration would be >0, or would exceed the driver's max deceleration. The decision of how far ahead of a speed decrease to start coasting follows a proposal from the **ACEA Whitebook 2016** [ref 7]: compare the vehicle's total energy (potential + kinetic) at the speed-change point vs. the current state; if the difference exceeds a threshold, coasting begins. During coasting, at every interval the driver also computes the distance required to reach the next target speed under max deceleration, and switches from coasting to braking once that distance is reached.

### 4.3.2.5 MT/AMT Transmission

MT/AMT gearboxes require **traction interruption** for shifts (engine disconnected from the powertrain during shifting → valid operating point during interruption means zero torque at gearbox input, handled in the search-operating-point logic). During interruption, engine speed is decoupled from vehicle velocity and controlled by a dedicated controller that targets the estimated engine speed for engaging the next gear (mimicking realistic driver behaviour); if the gearbox disengages because the vehicle stops, engine speed decreases to idle, governed by the engine's drag torque.

**Traction interruption time is a generic parameter:** **1 second for AMTs, 2 seconds for MTs.** VECTO simulates this interval exactly — if the current simulation interval would exceed it, the gearbox forces the interval to be adjusted to match exactly.

### 4.3.2.6 AT Transmission

AT transmissions require **no traction interruption** — engine can always transmit torque. Gear shifts cause additional losses from opening/closing internal clutches ("power-shift"). Power-shift losses are determined by current torque, angular-speed difference, and shift time (**0.8 seconds**).

### 4.3.2.7 VECTO Gearshift Strategy

Gearshift decision logic is separated from the transmission model. General rule: a shift can only be initiated **after** a valid operating point is found (engine returns success). Different strategies exist for MT/AMT vs. AT:
- **MT/AMT shifting rules:** implemented per the **ACEA WhiteBook 2016** [ref 7].
- **AT shifting rules:** elaborated jointly with industry (gearbox OEMs and ACEA) over SR7.
Both are fully documented in the VECTO User Manual (not reproduced in this report).

## 4.3.3 Development Methods

A "lean" software process roughly followed the **SPICE quality framework (ISO 15504, software lifecycle processes: ISO 12207)** — specifically the ENG.4–ENG.8 (V-model) processes and key supporting processes (not all Base Practices implemented). Main goal: maintainable, extensible code with reliable results — modular architecture and defined change-management processes.

### 4.3.3.1 Software Design
Modular, extensible architecture for: easy simulation-model reconfiguration; easy integration of independently-developed components (e.g., by an aggregate supplier); a common API for parameterization/output handling; a common simulation framework (esp. time control); architectural decoupling of simulation engine and GUI.

VECTO 2.2 (from LOT3) was a proof-of-concept requiring significant refactoring for legislative use. **Refactoring goals:**
- Separate GUI and simulation.
- Allow integration of the simulation kernel into OEM-specific software.
- Introduce a component model.
- Time- and distance-accurate simulation.
- Exact modelling of physical/mechanical equations.
- **All computations in SI units.**
- Introduce software unit testing.
- Introduce sanity checks for model parameters.
- Introduce exceptions for error handling.
- Embed all generic data in the executable.

### 4.3.3.2 Software Development Process
Test-driven development; all features/changes tracked in **CITnet/Jira**. Some issues coarse-grained (major refactors, e.g. gearbox model or driver strategy); many others fine-grained (bug fixes). Uniform coding style enforced via project-wide **ReSharper** settings. Source control: **GIT**, following the **GitFlow** process — each developer works in a personal fork, auto-synced from master; features/fixes go in dedicated branches; completed branches merge into the main repository's development branch; releases merge development → master (allowing continued development while urgent bugs can still be patched in the released version).

**Merge requirements for an issue to enter the development tree:**
- Meets coding standard/style.
- Builds without warnings (strict mode).
- Unit tests written, test data provided.
- All unit tests green.
- Source-code documentation where necessary.
- Documentation (user manual) updated.

### 4.3.3.3 Software Release Process
Extensive checklists cover unit tests, simulation time, and fuel-consumption checks for reference vehicles (Tables 3 and 4 reproduce two actual checklist templates used).

**Table 3 (Checklist for preparation of release) — key checklist items (verbatim categories):** Update version number (Version.cs for VectoCore/VectoConsole); documentation updates (version number, changelog date, new/changed features via tickets/commits, new/removed input fields, sample input files); changelog updates (PDF + User Manual); unit test suites (VECTO Core Tests, VECTO UserBugs Tests, VECTO Auxiliaries Tests, ModelBased Tests — all must pass, non-passing test names logged); generic-vehicle simulation smoke tests across Declaration Mode (Class 2, Class 5) and Engineering Mode (Class 2, Class 5, Class 9+PTO, CityBus AT-S, CityBus AT-P, InterurbanBus AAUX, Engine Only) with recorded execution time and final fuel-consumption figures (l/100km or g/h); VECTO API GUI button checks; VectoCMD (command-line) Declaration Class 2 check; release creation (license header update, RELEASE-mode compile, user-manual compile, ZIP creation and extraction smoke test, development→master branch merge, version tagging).

**Table 4 (Checklist for publish of release):** Upload ZIP to SVN; update Confluence wiki full changelog; update Confluence short-changelog table + download link; notify customers via a Jira ticket (example: "VECTO-58") including download link and Confluence link; copy archive to project release folder; record release date and releasing person.

## 4.3.4 VECTO Testability and Code Quality

### 4.3.4.1 Unit Tests, Integration Tests, and Test Coverage
**~1,440 unit/integration tests** implemented for VECTO 3. Code coverage (measured with ReSharper): **87% for VectoCore, 85% for VectoCommon**, combined **86.7%** total ("[Figure 11 description: bar/column chart of test coverage percentages broken down presumably by module, per the caption 'Test coverage measured with ReSharper' — underlying per-module values beyond the two cited percentages are not given in extracted text]"). Container/helper classes (e.g., parsing, enum-to-GUI conversion) show lower coverage; excluding them, coverage is **~90%**.

**Physical-soundness tests:** dedicated tests verify power/loss balance for every simulation step (modal data) and for overall (summary) data. The following energy-balance equations must hold for every simulation interval (variable names per VECTO's modal `.vmod` result-file abbreviations):

```
P_eng_FCmap = T_eng_fcmap * n_eng_avg
P_eng_fcmap = P_eng_out + P_AUX + P_eng_inertia (+ P_PTO_Transm + P_PTO_Consumer) 
            = P_loss_total + P_AUX + P_eng_inertia
P_loss_total = P_clutch_loss + P_gbx_loss + P_ret_loss + P_gbx_inertia + P_angle_loss 
             + P_axle_loss + P_brake_loss + P_wheel_inertia + P_air + P_roll + P_grad 
             + P_veh_inertia (+ P_PTOconsumer + P_PTO_transm)
```

And for summary (`.vsum`) data:
```
E_fcmap_pos = E_fcmap_neg + E_powertrain_inertia + E_aux_sum + E_clutch_loss + E_tc_loss 
            + E_gbx_loss + E_ret_loss + E_angle_loss + E_axl_loss + E_brake 
            + E_vehicle_inertia + E_air + E_roll + E_grad + E_PTO_consum + E_PTO_transm
E_fcmap_pos = P_fcmap_pos * time
```

### 4.3.4.2 Model-based integration tests
Extensive robustness testing: input parameters (corrected actual curb mass, CdxA, RRC [rolling resistance coefficient], transmission loss maps, axle ratio) varied in small steps across a technically-reasonable range, for typical vehicles of **groups 2, 5, and 9**. Trend of fuel consumption plus stability indicators (number of gearshifts, % of driving time at engine full load) were analysed.

- "[Figure 12 description: example plot of fuel consumption (l/100km) vs. CdxA variation for a group-2 vehicle, showing a monotonic trend used to check model stability.]"
- "[Figure 13 description: example plot of number of gear shifts vs. CdxA variation for a group-2 vehicle.]"
- "[Figure 14 description: example plot of percentage of engine full-load operating time vs. CdxA variation for a group-2 vehicle.]"

**In total, ~5,000 simulation runs were performed**, "all... executed by VECTO successfully" with "no unsteady or unreasonable phenomena... identified."

### 4.3.4.3 Code Complexity
Goal: reduce cyclomatic complexity vs. VECTO 2.2, targeting **max cyclomatic complexity of 10 per method** (not always achieved — exceptions mainly in Engineering-Mode-only methods, e.g., measured-speed mode, modal-data output filters, CSV handling, and inherently-complex strategy classes like driver/shift strategies).

"[Figures 15–20 description: a series of six charts tracking code-quality metrics across all VECTO releases (from v2.2 baseline through v3.2.0), namely: Fig.15 Maximum code complexity over releases (y-axis 0–300); Fig.16 Maximum complexity per line over releases (y-axis ~0 to 9.00E-04); Fig.17 Average methods per class over releases (y-axis 0–14); Fig.18 Average statements per method over releases (y-axis 0–18); Fig.19 Number of classes/interfaces over releases (y-axis 0–450); Fig.20 Percentage of files with max complexity >11 over releases (y-axis 0–50%). All show a clear improvement (reduction in complexity metrics, increase in modularity/class count) from v2.2 to later 3.x releases.]"

### Table 5 — Code quality metrics over all VECTO releases (reproduced in full)
| VECTO Version | Number of Files | Line Count | Number of Methods | Number of Statements | Number of Classes/Interfaces | Avg. Methods per Class | Avg. Statements per Method | Max. Complexity | Methods with Max. Complexity >11 | % Files with Max. Complexity >11 | Max. Complexity per Line |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.2 | 49 | 25,383 | 863 | 13,503 | 76 | 12.70 | 17.19 | 243 | 24 | 49.0% | 8.74E-04 |
| 3.0.1.315 | 212 | 28,055 | 1,670 | 13,387 | 369 | 5.25 | 4.54 | 20 | 9 | 4.2% | 9.90E-05 |
| 3.0.2.434 | 236 | 41,812 | 2,038 | 16,356 | 416 | 5.64 | 5.01 | 25 | 13 | 5.5% | 7.34E-05 |
| 3.0.2.466 | 237 | 42,002 | 2,059 | 16,507 | 418 | 5.69 | 5.01 | 25 | 13 | 5.5% | 7.29E-05 |
| 3.0.3.495 | 172 | 26,632 | 1,488 | 9,766 | 350 | 4.56 | 2.51 | 23 | 12 | 7.0% | 1.32E-04 |
| 3.0.3.536 | 172 | 26,676 | 1,486 | 9,770 | 350 | 4.54 | 2.52 | 23 | 12 | 7.0% | 1.31E-04 |
| 3.0.4.544 | 180 | 28,995 | 1,617 | 10,674 | 372 | 4.60 | 2.62 | 26 | 13 | 7.2% | 1.23E-04 |
| 3.0.4.565 | 180 | 28,993 | 1,617 | 10,678 | 372 | 4.60 | 2.62 | 26 | 12 | 6.7% | 1.22E-04 |
| 3.1.0.652 | 215 | 32,452 | 1,791 | 12,489 | 430 | 4.43 | 2.93 | 27 | 24 | 11.2% | 1.26E-04 |
| 3.1.0.662 | 215 | 33,515 | 1,791 | 12,517 | 430 | 4.43 | 2.93 | 27 | 24 | 11.2% | 1.23E-04 |
| 3.1.0.683 | 215 | 33,696 | 1,800 | 12,617 | 432 | 4.44 | 2.94 | 27 | 23 | 10.7% | 1.23E-04 |
| 3.1.1.742 | 219 | 34,678 | 1,852 | 12,987 | 438 | 4.62 | 3.09 | 28 | 25 | 11.4% | 1.22E-04 |
| 3.1.1.748 | 219 | 34,717 | 1,855 | 13,017 | 438 | 4.62 | 3.10 | 28 | 25 | 11.4% | 1.23E-04 |
| 3.1.2.796 | 219 | 35,193 | 1,867 | 13,280 | 440 | 4.63 | 3.15 | 30 | 27 | 12.3% | 1.24E-04 |
| 3.1.2.810 | 219 | 35,410 | 1,874 | 13,401 | 440 | 4.65 | 3.19 | 39 | 27 | 12.3% | 1.25E-04 |
| **3.2.0** | **220** | **37,165** | **2,010** | **14,248** | **447** | **5.00** | **3.21** | **15** | **12** | **5.5%** | **1.04E-04** |

*(3.2.0 is the final SR7 release baseline; note complexity dropped sharply from 3.1.2.810's max of 39 back down to 15, and % of high-complexity files dropped from 12.3% to 5.5%, indicating a deliberate clean-up pass before final release.)*

### 4.3.4.4 Traceability of VECTO Development
GitFlow approach retained; every new feature requires a **CITnet/Jira** issue, implemented in a dedicated feature branch, then merged upon acceptance — providing full traceability.

**Aggregate development statistics (SR7 period):**
- **~400 issues** for new features/bugs created (all but 2 processed — those 2 awaiting ACEA input).
- **~100 issues** for end-user support requests.
- **>3,200 GIT commits** submitted.
- **>400 merge requests** merged.

## Standards and organisations referenced in this section (exact names only)
- ISO/IEC 15504 (SPICE quality framework)
- ISO/IEC 12207 (software lifecycle processes)
- ACEA WhiteBook / White Book 2016 (CO2 declaration procedure for HDV, ACEA Workgroup CO2HDV) — ref [7]
- GIT, GitFlow, ReSharper, CITnet/Jira, Confluence, SVN (development/release tooling named explicitly)
