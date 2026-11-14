# VECTO / HDV CO2 Certification Methodology — Part 4: VECTO Software Architecture, Simulation Equations, and VECTO-CSE

*(Source: same LOT 3 report, Report No. I 07/14/Rex EM, 25.06.2014, Section 6 "Software description", pages 99–136 of 170. This is the single most methodologically important part of the document for a simulation-tool rebuild: it contains VECTO's core calculation architecture and all its governing equations, verbatim.)*

> **Scope reminder:** This VECTO version (as of June 2014) is a **backwards-calculating, quasi-stationary longitudinal-dynamics model for conventional (ICE) HDVs**. All equations below describe an internal-combustion-engine powertrain (engine fuel map, gearbox, axle, mechanical auxiliaries). No electric-motor, battery, or fuel-cell energy-flow equations appear anywhere in this chapter. If your project intends to mirror VECTO's *architecture* (backward quasi-static simulation, 1Hz resolution, driver model, resistance equations, map interpolation) for an electric powertrain, the resistance/kinematics equations (rolling, air, slope, acceleration resistance — Equations 2–14) are directly reusable since they are powertrain-agnostic; the engine-map interpolation and WHTC-correction logic (Equations 15–19) are ICE-specific and would need to be replaced by a motor/battery efficiency-map and energy-balance model, which is **not documented in this source**.

## 6.1. VECTO — General Characteristics

VECTO = "**Vehicle Energy consumption Calculation Tool**." **[Figure 60 description]:** the VECTO application logo.

**Main characteristics (verbatim):**
- Backwards-calculating, quasi-stationary longitudinal dynamics model
- Driving model to consider real-life driving behaviour (gear shifting, coasting, braking)
- Constant time steps of 1 second (1 Hz)
- Compatible with distance-based and time-based driving cycles
- Input/output via text files (**CSV and JSON**)
- Implemented as a **Visual Basic .NET** application
- Graphical user interface (GUI) for calculation control and editing of main input files

**[Figure 61 description]:** example screenshot of the VECTO GUI.

## 6.1.1. Model Structure — Four Main Modules

**[Figure 62 description]:** block diagram of VECTO's four main calculation modules in sequence, M1 → M2 → M3 → M4.

| Module | Name | Function |
|---|---|---|
| M1 | Driving Cycle Pre-processing | Converts distance-based mission profile to 1Hz time-based format; converts time-based cycles to 1Hz if needed |
| M2 | Driver Pre-processing | Applies driver functions not tractable in the backward loop (Overspeed, Look-Ahead Coasting) |
| M3 | Power Calculation | Core module: computes engine torque/speed at each time step from driving resistances, powertrain losses, auxiliary demand |
| M4 | FC Calculation | Interpolates fuel consumption from the stationary FC map and applies the WHTC correction |

### 6.1.1.1. Driving Cycle Pre-processing (M1)

Mission profiles (as defined in regulation) specify only target speed levels; VECTO adds driving-behaviour elements (acceleration/deceleration).

- **Target deceleration** is defined as a function of speed, limiting deceleration during braking to represent average real-life behaviour; the same functional approach is used for target acceleration. **[Figure 63 description]:** example curves of speed-dependent target acceleration (red) and deceleration (blue) — both predefined per vehicle category for declaration mode. **Table 56 (Acceleration and deceleration limit over vehicle speed, from the Annex, applies here)** — reproduced:

| v [km/h] | acc [m/s²] | dec [m/s²] |
|---|---|---|
| 0 | 1 | −1 |
| 25 | 1 | −1 |
| 50 | 0.642857143 | −1 |
| 60 | 0.5 | −0.5 |
| 120 | 0.5 | −0.5 |

- **[Figure 64 description]:** cycle before (blue) and after (per above) pre-processing in M1 — shows target-speed profile augmented with realistic accel/decel ramps.
- Two supported cycle input types, **[Figure 65 description]** (sub-module split M1.1/M1.2):
  - **Time-based cycles:** speed defined over time, any/variable frequency (e.g. CAN data) → sub-module M1.2 converts to 1Hz.
  - **Distance-based cycles** (default for declaration mission profiles): speed defined over distance → sub-module M1.1 converts to 1Hz time-based.
- Declaration mission-profile cycle parameters: **Target speed [km/h], Slope [%], Stop time [s]** (stop time only relevant for distance-based cycles).
- **New time-step creation (M1.3):** needed to compute vehicle acceleration from speed; acceleration = difference between two original-time-step speed values, allocated to a **new time step inserted between** the old ones. **[Figure 66 description]:** diagram of new (red/green) time steps inserted relative to original (blue) speed samples to compute acceleration. All cycle input parameters (speed, slope, etc.) are interpolated onto these new time steps.

### 6.1.1.2. Driver Pre-processing (M2)

Applies, in a pre-processing step (rather than inside the main backward loop, because they require nested forward/backward sub-loops):
- **Overspeed**
- **Eco-Roll**
- **Look-Ahead Coasting**

**[Figure 67 description]:** block diagram of M2 split into two sub-modules (M2.1 for Overspeed/Eco-Roll, and the Look-Ahead Coasting sub-module).

### 6.1.1.3–6.1.1.5. Overspeed and Eco-Roll

Both address vehicle behaviour on non-zero slope, exploiting negative slopes + inertia for lower FC; both are mutually exclusive per vehicle configuration (vehicles without Eco-Roll always use Overspeed in declaration mode).

- **Overspeed:** activates when total wheel power demand (Pwheel) < 0 (i.e., accelerating on negative slope). Clutch stays closed, engine in motoring, vehicle accelerates beyond target speed until a defined relative speed-limit threshold, then mechanical brakes engage. **[Figure 68 description]:** example trace — target speed (purple) & actual speed (orange) on top-left axis, slope (brown) top-right axis; engine power (blue), motoring curve (orange), mechanical brake power (green) below; example allows overspeed up to target+5 km/h.
- **Eco-Roll:** instead of engine-drag braking, shifts to Neutral with engine idling to maximize free-roll distance using kinetic energy; engine only overcomes idle losses + auxiliary demand during the roll; re-engages above/below a speed threshold around target. **[Figure 69 description]:** analogous trace to Figure 68, showing idling engine during free-roll and braking at the upper threshold.

### 6.1.1.6. Look-Ahead Coasting

Forward-looking function: detects upcoming target-speed reductions and induces early, fuel-efficient deceleration (engine braking before mechanical braking), using a predefined target deceleration (a_lookahead) to compute deceleration timing. **[Figure 70 description]:** geometric construction for calculating deceleration start-time T [s] before a target-speed reduction point. The coasting trajectory is calculated forward from that start point until it meets the M1-defined braking-deceleration trajectory; resulting deceleration = coasting phase + combined mechanical braking/engine drag.

### 6.1.1.7–6.1.1.9. Power Calculation (M3) — Core Loop

**[Figure 71 description]:** block diagram of the M3 per-time-step loop: M3.1 (limit acceleration) → M3.2 (power at wheels) → M3.3 (gear shift model) → M3.4 (engine power calculation), running sequentially from first to last time step.

- **M3.1 Limit acceleration:** clamps acceleration to the speed-dependent target curve (Figure 63) — ensures realistic acceleration even for high-power/low-load vehicles or downhill roads.
- **M3.2 Power at wheels:** sums rolling, air, slope, and acceleration resistance (detailed equations below).

### 6.1.1.10. Rolling Resistance

**Equation 2:**
```
F_roll = RRC × m × g × cos(αS)     [N]
```
where RRC = weighted mean rolling resistance coefficient [-]; m = total vehicle mass [kg]; g = gravitational acceleration [m/s²]; αS = slope [rad].

**Equation 3** (RRC as a function of total vehicle mass and per-axle tyre load, accounting for different tyres per axle type — steering/powered/trailer):
```
RRC = Σᵢ [ s(i) × RRC_ISO(i) × ( s(i)·m·g / (w(i)·Fz_ISO(i)) )^(β−1) ]     for i = 1..n axles
```
where: s(i) = relative axle load [-]; RRC_ISO(i) = tyre RRC per **ISO 28580** [-]; m = vehicle mass + loading [kg]; g = 9.81 m/s²; w(i) = number of tyres on axle i (4 if twin tyres, else 2); Fz_ISO(i) = tyre test load per ISO 28580 (85% of max load) [N]; **β = constant parameter = 0.9** [-]. The load-dependency function is cited from Michelin literature and validated against ETRTO tire-drum data with varied test load.

### 6.1.1.11. Air Resistance

**Equation 4:**
```
F_air = cd × A × ρ × v_veh² / 2     [N]
```
cd = drag coefficient [-]; A = frontal area [m²]; ρ = air density [kg/m³]; v_veh = vehicle speed [m/s].

Since Equation 4 is valid only for windless conditions, a correction factor accounts for average wind:

**Equation 5:**
```
cd = cd(0) × f_cd(v_veh)
```
cd(0) = drag coefficient at yaw angle β=0; f_cd = speed-dependent correction factor. **[Figure 72 description]:** the drag-coefficient scaling factor f_cd vs. vehicle speed — factor is held constant below 60 km/h (uncertain yaw-angle dependency + minor aero contribution at low speed anyway), then declines toward 1 as speed increases (see Table 55 values below). **[Figure 73 description]:** geometric diagram of wind components/angles — yaw angle β between driving direction and relative air-flow direction.

**Equation 6** (total air resistance integrated over yaw angle using a generic yaw-angle-dependent Cd(β)):
```
F_air = (1/2) × A × ρ × (1/2π) × ∫₀^(2π) cd(β) × v_air(v_veh, φ)² dφ     [N]
```
**Equation 7** (air inflow speed as function of vehicle speed and wind direction φ):
```
v_air(v_veh, φ) = √[ (v_wind·cosφ + v_veh)² + (v_wind·sinφ)² ]
```
**Equation 8** (deriving the cross-wind correction factor f_cd by merging Eq. 4–6):
```
f_cd(v_veh) = (1 / (2π × v_veh²)) × ∫₀^(2π) Δcd(β) × v_air(v_veh, φ)² dφ     [-]
```
Δcd(β) = generic function for relative change of cd with yaw angle [-].

**Table 55 (Drag coefficient scaling factor, from Annex)** — reproduced (values are noted in the source as provisional, to be updated per the ACEA Whitebook April version and eventually made vehicle-class- and trailer-configuration-dependent):

| v_veh [km/h] | cdx_rel [-] |
|---|---|
| 0–60 | 1.098791052 (constant) |
| 65 | 1.088803287 |
| 70 | 1.080533793 |
| 75 | 1.073611979 |
| 80 | 1.067741189 |
| 85 | 1.062704492 |
| 90 | 1.058339882 |
| 95 | 1.054524125 |
| 100 | 1.051161940 |

### 6.1.1.12. Slope Resistance

**Equation 9:**
```
Fs = m × g × sin(αS)     [N]
```

### 6.1.1.13. Acceleration Resistance

**Equation 10:**
```
F_acc = (m + Θ_red / r_dyn²) × a     [N]
```
m = vehicle mass + loading [kg]; Θ_red = reduced rotational inertia [kg·m²]; r_dyn = effective (dynamic) wheel radius [m]; a = vehicle acceleration [m/s²].

**Equation 11** (reduced rotational inertia, merging all powertrain rotational inertias to the drive axle):
```
Θ_red = Σⱼ Θⱼ × ijⱼ²     [kg·m²]     for j = 1..n components
```
Θⱼ = inertia of a single component [kg·m²]; ijⱼ = total transmission ratio from component j to the drive axle [-]. Note: **engine inertia is excluded here** — added separately when engine power is computed.

### 6.1.1.14. Total Power at Wheels

**Equation 12:**
```
P_wheel = v × (F_roll + F_air + Fs + F_acc)     [W]
```
v = vehicle speed [m/s].

### 6.1.1.15. Gear Shift Model

Represents average manual/AMT shifting behaviour via **shift curves** (engine speed for up-/down-shift as function of engine torque). **[Figure 74 description]:** example up-shift and down-shift curves plotted over the engine speed–torque map. Gear change triggers when the engine operating point crosses a shift curve; gears may be skipped if the resulting speed stays within the shift curves and torque is below full load. In AMT mode, up-shifts can be initiated even below the up-shift curve under the same boundary conditions.

*(Footnote: a beta Automatic Transmission (AT) model existed and was tested by ZF, VOITH, Allison, and EvoBus; a generic AT model was planned for finalization by June 2014, as extra LOT3 work.)*

### 6.1.1.16. Start Gear Calculation

Trucks typically skip low gears when starting on flat roads/low load. Since target-speed cycles have abrupt initial speed changes (which would force first-gear selection if shift curves were used directly), VECTO instead defines a **fictional load case**: actual loading/auxiliary demand/slope combined with a predefined representative speed and acceleration (average real-life "just after start" conditions). The highest gear satisfying shift-curve constraints (with adequate torque reserve) is selected. **[Figure 75 description]:** example showing different start gears chosen for the same target-speed cycle at different road slopes.

### 6.1.1.17. Engine Speed Calculation

**Equation 13** (valid when clutch fully closed):
```
n = (60 / 2π) × (v / r_dyn) × i_axle × i_gear     [min⁻¹]
```
n = engine speed [min⁻¹]; v = vehicle speed [m/s]; r_dyn = effective wheel radius [m]; i_axle = final drive ratio [-]; i_gear = current gear ratio [-].

Not valid during clutch slip at low speed — VECTO uses a **clutch model** for engine speed at low vehicle speed until the clutch fully closes. **[Figure 76 description]:** engine speed during acceleration from standstill — n_clutch (red, clutch model active) vs. n per Equation 13 (orange) vs. resulting blue trace. The clutch model accounts for the engine's full speed range (idle to rated), making it valid across engine/vehicle sizes.

### 6.1.1.18. Engine Power Calculation

**Equation 14** (all additional losses between wheels and engine):
```
Pe = P_wheel + Ploss_Axle + Ploss_Ret + Ploss_GB + Paux_Sum + Pa_Eng     [kW]
```
- P_wheel = power at wheels [kW] (Equation 12)
- Ploss_Axle = differential (axle) losses [kW]
- Ploss_GB = gearbox losses [kW]
- Ploss_Ret = hydraulic-retarder idling losses [kW]
- Paux_Sum = total auxiliary power demand [kW]
- Pa_Eng = inertia losses of engine and flywheel [kW]

Gearbox and differential losses: torque/speed-map based (measurements). Retarder idle losses: speed-dependent (engine or drive-axle speed, depending on retarder type) torque loss. Component sequence is respected (e.g., axle losses are embedded in the torque flowing through the gearbox).

### 6.1.1.19. Auxiliaries (Generic Map-Based Model)

**[Figure 77 description]:** block diagram of the generic auxiliary model: supply power → efficiency → auxiliary input power → mechanical drive efficiency → mechanical power at crankshaft.

Three-step method:
1. Supply power demand per auxiliary defined in the driving cycle (time/distance dependent).
2. Auxiliary input power computed from supply power and a predefined efficiency map.
3. A constant efficiency covers losses between auxiliary and engine.

**Equation 15:**
```
PauxOut = Psupply / η_eff     [kW]
```
**Equation 16:**
```
PauxIn = AuxMap(n_aux, PauxOut)     [kW]
```
**Equation 17:**
```
Paux = PauxIn / η_mech     [kW]
```
where: Psupply = effective supply power demand [kW]; η_eff = consumer efficiency [-]; n_aux = auxiliary speed (constant ratio to engine speed) [min⁻¹]; AuxMap(n,P) = interpolation from the auxiliary efficiency map [kW]; η_mech = mechanical (belt/gear) drive efficiency [-]; Paux = mechanical auxiliary power demand at the crankshaft [kW]. All individual Paux values sum into Paux_Sum in Equation 14.

**Important limitation (verbatim):** this generic map-based approach was, as of the end of LOT3, only available in **"engineering mode."** For **declaration mode**, pre-defined generic Paux constant values are used per HDV class/mission profile/technology (see Part 2, section 4.2.6, and Part 5's Annex tables).

### 6.1.1.20. Transient Engine Full Load (PT1 Model)

To represent the transient (non-instantaneous) torque build-up of a real engine, a first-order (PT1) lag is applied to lower the stationary full-load curve under transient conditions.

**Equation 18:**
```
P_fld = P_fld_stat + t_PT1 × Pe(t−1) / (t_PT1 + 1)     [kW]
```
P_fld_stat = stationary full load at the given engine speed [kW]; t_PT1 = PT1 time constant at that engine speed [s]; Pe(t−1) = engine power at the preceding time step [kW]. The time constant varies with engine speed (**[Figure 78 description]:** exemplary stationary full-load/motoring curve with a PT1 time-constant curve over engine speed) — lower time constant (faster response) at higher engine speeds.

**Table 54 (PT1 time constant, from Annex)** — reproduced:

| Engine speed [1/min] | PT1 [s] |
|---|---|
| 400 | 0 |
| 800 | 0.47 |
| 1000 | 0.58 |
| 1200 | 0.53 |
| 1400 | 0.46 |
| 1500 | 0.43 |
| 1750 | 0.22 |
| 1800 | 0.2 |
| 2000 | 0.11 |
| 2500 | 0.11 |

**[Figure 79 description]:** comparison of a measured vs. PT1-calculated full-load torque step, at two different engine speeds — used to validate the transient model.

### 6.1.1.21. Start/Stop

Shuts down the engine at standstill to save fuel. Since VECTO uses constant auxiliary power demand (no battery/charge-control modeling), engine-off periods would otherwise create an invalid energy balance. VECTO instead **corrects overall fuel consumption post-hoc** using a linear regression between engine power and FC (see section 6.1.1.27). Engine-stop conditions (all three must hold, after a predefined activation delay): (1) Pwheel ≤ 0; (2) vehicle speed below a threshold; (3) engine has run for a minimum time.

### 6.1.1.22. Speed Reduction

If required power exceeds the transient full-load curve (common at rectangular target-speed steps), vehicle speed is reduced and the time step is **repeated from M3.2** until power demand is satisfiable. **[Figure 80 description]:** example 0→45 km/h acceleration trace showing engine power (blue) constrained by transient full load (brown).

### 6.1.1.23. Distance Correction

Because Overspeed/Speed-Reduction can make actual distance diverge from the target-speed-implied distance, a correction compares actual vs. theoretical distance and — if the error is reduced by doing so — duplicates the current time step (if under-distance) or skips the next one (if over-distance). Independent of Speed Reduction, so acceleration phases are unaffected; can occasionally disturb coasting phases (introducing short traction intervals), judged an insignificant effect on comparability between vehicles. **[Figure 81 description]:** mission-profile trace with (bottom) vs. without (top) Distance Correction — blue = target speed, red = simulated speed.

### 6.1.1.24. Traction Interruption (TI)

Gear changes in non-powershift transmissions open the driveline briefly (vehicle rolls freely). Since VECTO runs at 1Hz, sub-second TI durations are approximated: the exact roll-out for the true TI duration is computed, and the resulting end-speed is passed to the **nearest rounded 1Hz time step** (e.g., a 2.3s TI computes the exact 2.3s roll-out but applies the result at the 2s mark). Documented limitation: while producing realistic acceleration-time orders of magnitude, the approach is **not accurate enough for reliable ranking** of fuel efficiency between transmissions with/without TI — flagged for further work post-LOT3.

**Suggested default TI values for declaration** (verbatim; bracketed ACEA-suggested values flagged as "should not be used until accuracy can be ensured"):
- MT: 2 seconds (ACEA suggested: 2.2)
- AMT: 1 second (ACEA suggested: 1.5)
- DCT: 0 seconds (ACEA suggested: 0.8)

## 6.1.1.25–6.1.1.28. Fuel Consumption Calculation (M4)

**[Figure 82 description]:** M4 block diagram — three-step chain: map interpolation → Start/Stop correction → WHTC correction.

### 6.1.1.26. Map Interpolation

Base FC value taken from the stationary FC map [g/h] over engine speed [1/min] and torque [Nm] (**[Figure 83 description]:** example 3D/contour fuel-consumption map). For interpolation, the map is **triangulated via the Delaunay method** (Delaunay, 1934) — **[Figure 84 description]:** the resulting triangulated surface covering the whole FC map. The interpolation returns the z-coordinate (fuel consumption) for a given (speed, torque) load point on this triangulated surface, applied at every time step of the mission profile.

### 6.1.1.27. Start/Stop Correction

Three-step correction (for vehicles with the Start/Stop function):
1. From all 1Hz simulation data points, compute a **linear regression** FC[g/h] = k·Pe[kW] + d (**[Figure 85 description]:** example scatter + regression line of engine power vs. fuel consumption).
2. From the difference between simulated (with Start/Stop) and target auxiliary energy consumption [kWh], compute a cycle-average mechanical power change ΔPe [kW] of the ICE (using average alternator efficiency and engine-running time).
3. Apply correction at every 1Hz time step:
```
ΔFC [g/h] = ΔPe × k
```
(If the engine is in motoring conditions, ΔFC is set to zero.)

### 6.1.1.28. WHTC Correction (Final Calculation Step)

Recall from Part 2 (section 4.2.1.2) the background. In VECTO's runtime:
1. Interpolate FC for the WHTC load cycle from the engine fuel map, based on **target engine speed/torque** derived from the full-load curve — yielding Urban/Rural/Motorway part FC values.
2. Compute the mission-profile-specific correction factor:

**Equation 19:**
```
CF_WHTC = Σᵢ₌₁³ [ fᵢ × (FC_meas_i / FC_calc_i) ]     [-]
```
i = index for {Urban, Rural, Motorway}; fᵢ = weighting factor per part (Table 4 / Table 45, mission-profile specific); FC_meas_i = WHTC measurement result per part [g/kWh] (input parameter); FC_calc_i = calculated FC per part [g/kWh].
3. Multiply CF_WHTC into each time step's FC value.

The WHTC correction is the **final step** of the VECTO calculation chain. **CO2 result = fuel consumption × a gravimetric CO2/FC factor** (per the Carbon-balance formula in Part 2, section 4.2.1.1).

## 6.1.2–6.1.3. Documentation

- **User Manual:** provided in HTML format, accessible from the VECTO GUI.
- **Developer Guide:** obtained together with the VECTO software from the **CITnet server** (European Commission's internal collaboration platform) — i.e., not publicly distributed at this stage; access implies restricted/internal availability.

---

## 6.2. VECTO-CSE (Constant Speed Evaluator) — Aerodynamic Test Evaluation Tool

**History:** a first version ("CSE 1.0") was developed in 2012 by TUG under a DG JRC-sponsored project, distributed to HDV CO2 advisory group members, and applied during LOT3's 2012–2013 Proof-of-Concept phase. A major update, **VECTO-CSE V2.01**, was released to match the revised aero test procedure.

**Key improvements in V2.01 vs V1.0 (verbatim list):**
- Supports any test-track layout / measurement-section configuration / driving directions.
- Two supported methods for identifying whether the vehicle is inside a measurement section: (a) opto-electronic barriers + GPS, or (b) high-precision DGPS.
- Automatic calibration of mobile-anemometer and vehicle-speed signals.
- Automatically evaluates the "high speed + two low speed" test sequence per measurement-section/direction combination.
- All validity checks from the Technical Annex (ambient conditions, torque/speed stability during constant-speed phases) are built in.

Status: released June 2014 as an **"engineering version"** allowing user-adjustable evaluation parameters, intended for use while the aero test procedure's final details were still being settled during 2014; a fixed-parameter **"declaration version"** was planned once the official procedure was finalized.

### 6.2.1. VECTO-CSE Input Files

**Table 36 (Overview input files)** — reproduced:

| File type | Extension | Purpose |
|---|---|---|
| Vehicle | `*.csveh` | Tested vehicle configuration (test mass, anemometer height, etc.) |
| Ambient conditions | `*.csamb` | Stationary weather-station data |
| Measurement-section config ("ms config") | `*.csms` | Coordinates, driving directions of measurement sections (separately configurable for calibration run vs. measurement runs) |
| Measurement data | `*.csdat` | Vehicle-recorded data at 100Hz; separate files required for: (i) calibration run, (ii) first low-speed run, (iii) high-speed run, (iv) second low-speed run |
| Altitude profile (optional) | `*.csalt` | Measurement-section altitude profile, used for gradient-force correction if enabled |
| Job | `*.csjob` | All evaluation settings + paths to input data; auto-created via GUI, editable via text editor; also stores main results after a successful run |
| Criteria (optional) | — | Saved/imported evaluation parameters (validity criteria, correction settings); parameters used are always also stored in the Jobfile for traceability |

### 6.2.2. Evaluation Algorithms

**Position processing:** (D)GPS coordinates converted to UTM coordinates ("Lat (UTM)"/"Long (UTM)"); inside measurement sections, the vehicle's position is also projected onto the line between the section's start/end coordinates ("Lat (root)"/"Long (root)") — this projected point is the reference for section-entry/exit detection and altitude allocation.

**Assignment of data to measurement sections — two options:**
- **Option 1 (Trigger signal):** entry/exit identified when (1) trigger signal changes integer value, (2) vehicle position is within a configurable ± square (`delta_x_max`, `delta_y_max`) of the section start/end point, and (3) heading is within ± `delta_head_max` degrees.
- **Option 2 (DGPS signal):** entry/exit identified when (1) an imaginary line perpendicular to the section through the start/end point is crossed within ± `delta_y_max` of that point, and (2) heading is within ± `delta_head_max` degrees. (Per the Technical Annex, Option 2 is valid **only** with high-accuracy DGPS — a constraint VECTO-CSE cannot itself verify.)

Additional validity check: driven distance inside the section (from calibrated speed) vs. the section's specified distance; if the absolute difference exceeds `leng_crit` (pre-set 3m, "final value to be decided"), the data is invalid. All these threshold parameters have pre-set defaults in V2.01 based on available test-data experience, adjustable per case.

**Calibration-test evaluation (vehicle speed, air speed, yaw angle):**
- **Vehicle speed:** `v_veh = v_veh_can × fv_veh`, where the calibration factor fv_veh is the average ratio of a reference speed (from track-length/time under Option 1, or DGPS speed / DGPS-derived speed under Option 2) to the CAN front-axle speed signal, across all calibration-run datasets. In V2.01, method (a) — direct DGPS speed — is used by default; both methods' results are shown in the output file for comparison.
- **Air speed & yaw angle:** correction factors `fvpe` (air-speed position error) and `βame` (yaw-angle misalignment) are computed per an iterative procedure: (1) apply the anemometer's own instrument-calibration correction (y = fx+d); (2) initially assume all datasets valid; (3) require ≥5 valid datasets per section/direction (adjustable), discarding the extra dataset from the direction with more data if directions are unbalanced; (4) compute fvpe/βame from all "used=1" datasets per the Technical Annex formulas (with fape, the yaw position-error correction, from generic data); (5) recompute undisturbed air-speed/yaw/wind values with boundary-layer correction; (6) re-check wind-criteria validity and iterate from (3) if any dataset's validity changed.

**Constant-speed-test evaluation:**

**Total traction force:**
```
F_trac = (T_L + T_R) × n_eng × π / (30 × i_gear × i_axle × v_veh)     [N]
```
TL, TR = corrected left/right wheel torque [Nm]; n_eng = engine speed [rpm]; i_gear, i_axle = gear/axle ratios; v_veh = vehicle speed [m/s].

**Correction for gradient and acceleration forces (optional, disabled by default in V2.01):**
```
F_res = F_trac − F_grd × s_grd − F_acc × s_acc
```
```
F_grd = m_veh × g × sin(Δalt / Δdist)
```
```
F_acc = m_veh × a_avg + (I_wh × ω̇ × ω) / v_veh
```
- Gradient correction disabled by default because it doesn't affect baseline Cd×A results (only single-section RRC estimates) under VECTO-CSE's general evaluation principle.
- Acceleration correction disabled by default: within the tight speed-stability tolerances mandated for the constant-speed phases (**±0.15 km/h low speed, ±0.3 km/h high speed**), even small oscillations can meaningfully bias traction-force readings for heavy vehicles (a footnote gives a worked example: a fully-loaded class 5 tractor-semitrailer's worst-case allowed speed drop yields ~550N of acceleration force — about 25% of the air-drag force at that speed — reduced to ~250N when empty). No robust averaging-window setting for the correction had been identified from the limited LOT3 data (no CAN speed signal in the available dataset); flagged for further 2014 investigation.

**Normalization to reference air density:**
```
F_res,ref = F_res × (ρ_air,ref / ρ_air)
```
ρ_air,ref = **1.188 kg/m³** (reference condition). ρ_air computed from vehicle-measured air temperature and stationary-station pressure/humidity:
```
p_v,H2O = 611 × (RH_stat/100) × 10^[7.5·t_amb,stat / (237+t_amb,stat)]
ρ_air = (p_amb,stat − p_v,H2O) / (287.1 × (t_amb,veh + 273.15)) + p_v,H2O / (461.9 × (t_amb,veh + 273.15))
```

**Low-speed rolling-resistance correction (optional):**
```
F_res,ref = F_res,ref × f_roll,corr
```
Default `f_roll,corr = 1` (no correction). Example given: if low-speed RRC is known to be 85% of high-speed RRC, set correction factor = 1/0.85 = 1.176.

**Validity/exclusion criteria (verbatim categories):**
- Auto-excluded: invalid wind speed (all test types); invalid yaw angle (calibration, high-speed); speed/torque stability criteria not met (low/high speed); unequal dataset counts per heading direction (high speed) or per section/direction across the two low-speed tests.
- Warnings only (pilot phase): ambient-condition range exceeded; tire-pressure deviation between low/high speed exceeded; RRC deviation between first/second low-speed test exceeded.
- Aborts evaluation: test-track direction deviation >20° from ±180° between sections; insufficient valid datasets in any test type.

**Cd×A and RRC calculation, per measurement-section/direction combination:**
- Linear regression: `F_res,ref` vs. squared air speed (v_air²) across all "used=1" high-speed and both low-speed datasets, weighted so cumulative high-speed weighting = 50%. Regression yields slope F2 [Ns²/m²] and intercept F0 [N].
- Average absolute yaw angle β_avrg computed from high-speed datasets only.
```
Cd(β_avrg) × Afr = 2 × F2 / ρ_air,ref     [m²]
```
```
RRC = 1000 × F0 / (m_veh × g)     [kg/t]
```

**Overall result and yaw-angle correction:**
- Overall Cd(β_avrg)×Afr and β_avrg = arithmetic average across all applicable section/direction combinations.
```
Cd × Afr = Cd(β_avrg) × Afr − ΔCd·Afr(β_avrg)
```
ΔCd·Afr(β_avrg) = the generic yaw-angle correction curve (vehicle-class- and configuration-specific — rigid vs. trailer) evaluated at β_avrg. An alternative method (yaw correction applied per section/direction *before* averaging) was also computed during the pilot phase and reported as "Option 2" for comparison.

### 6.2.3. Documentation

User Manual (input/output file formats, GUI operation, plus a developer-oriented source-code chapter) distributed with the software via CITnet.

---

*(Continued in Part 5: Work-Program Overview, Open Issues incl. Hybrid/Advanced-Technology Roadmap, Summary, Literature, Glossary of Key Terms, and full Annex Declaration-Mode Data Tables)*
