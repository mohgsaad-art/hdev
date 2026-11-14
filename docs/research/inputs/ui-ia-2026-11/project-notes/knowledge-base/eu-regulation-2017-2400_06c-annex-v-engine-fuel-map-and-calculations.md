# Commission Regulation (EU) 2017/2400 — Annex V: Verifying Engine Data
## Part C — Post-Processing of Measurement Data, Engine Pre-Processing Tool, Simulation-Tool Input Parameters & Pre-Processing Evaluation Steps

**CELEX number:** 02017R2400
**Consolidated text date:** 01.01.2026 (consolidation version 007.001)
**Covers:** Annex V, point 5 "Post-processing of measurement data", point 6 "Application of engine pre-processing tool", Appendix 7 "Input parameters for the simulation tool", and Appendix 8 "Important evaluation steps and equations of the engine pre-processing tool" (OCR source lines ~6179–8467, excluding Appendices 1–6, which are in Part D)
**Amendment markers:** ▼B = original 2017 baseline; ▼M1 = Reg (EU) 2019/318; ▼M3 = Reg (EU) 2022/1379; ▼M4 = Reg (EU) 2025/258

> This is the most directly relevant part of Annex V for anyone building VECTO-style simulation code: it defines exactly how raw dynamometer measurements become the engine input files (full-load curve, fuel map, correction factors) actually consumed by the VECTO simulation tool.

> **OCR fidelity warning:** The source PDF renders several formulas as inline mathematical objects (summation/fraction layouts, special minus/multiply glyphs). The OCR text extraction corrupted these into garbled Unicode fragments (e.g. "¼", "Ä", "Ü", "þ", "Ê", "Ì"). Below, each such formula has been **reconstructed** into standard mathematical notation using (a) the garbled layout as a structural guide and (b) the variable definitions given immediately beneath each formula in the source text — these definitions were extracted cleanly and are reliable. The reconstructed formulas all resolve to the standard **composite trapezoidal numerical integration rule**, which is the expected/conventional method for integrating a time-series of power or mass-flow values, consistent with VECTO methodology described elsewhere in this knowledge base. If exact symbolic fidelity to the official PDF typesetting is required, the original PDF page images should be checked directly.

---

## 5. Post-processing of measurement data ▼B

All calculations in this section are performed **specifically for each engine** within one engine CO2-family.

### 5.1 Calculation of engine work

**▼M1:** Total engine work over a cycle or defined period is determined from recorded engine-power values, per point 3.1.2 of this Annex and points 6.3.5/7.4.8 of Annex 4 to UN R49.

Engine work over a complete test cycle or each WHTC sub-cycle, by integrating recorded power values (**reconstructed trapezoidal-rule formula** — see OCR fidelity warning above):

> **Wact,i = h × [ ½P₀ + P₁ + P₂ + … + Pₙ₋₂ + Pₙ₋₁ + ½Pₙ ]**

where:
- `Wact,i` = total engine work over the time period from t0 to t1
- `t0` = time at start of period; `t1` = time at end of period
- `n` = number of recorded values over the period t0→t1
- `Pk [0…n]` = recorded engine-power values over the period, chronological order, k = 0 at t0 to n at t1
- `h` = interval width between adjacent recorded values = **(t1 − t0) / n**

### 5.2 Calculation of integrated fuel consumption

Any recorded **negative** fuel-consumption values are used directly (not set to zero) in the integration.

Total fuel mass consumed over a complete test cycle or each WHTC sub-cycle, by integrating recorded fuel mass-flow values (same trapezoidal structure as 5.1):

> **ΣFCmeas,i = h × [ ½ṃfuel,0 + ṃfuel,1 + ṃfuel,2 + … + ṃfuel,n₋2 + ṃfuel,n₋1 + ½ṃfuel,n ]**

where:
- `ΣFCmeas,i` = total fuel mass consumed over the period t0→t1
- `t0`, `t1`, `n` = as in 5.1
- `ṃfuel,k [0…n]` = recorded fuel mass-flow values over the period, chronological order
- `h` = (t1 − t0) / n

### 5.3 Calculation of specific fuel consumption figures

Correction and balancing factors (input to the simulation tool) are calculated by the **engine pre-processing tool**, based on measured specific fuel-consumption figures per 5.3.1/5.3.2.

#### 5.3.1 Specific fuel consumption figures for WHTC correction factor

From actual measured values of the **hotstart WHTC** (4.3.3):

> **SFCmeas,Urban = ΣFCmeas,WHTC-Urban / Wact,WHTC-Urban**
> **SFCmeas,Rural = ΣFCmeas,WHTC-Rural / Wact,WHTC-Rural**
> **SFCmeas,MW = ΣFCmeas,WHTC-MW / Wact,WHTC-MW**

where `SFCmeas,i` = specific fuel consumption over WHTC sub-cycle i [g/kWh]; `ΣFCmeas,i` = total fuel mass consumed over sub-cycle i [g] (per 5.2); `Wact,i` = total engine work over sub-cycle i [kWh] (per 5.1).

**The 3 WHTC sub-cycles are defined as:**
1. **Urban:** cycle start → ≤ 900 s from cycle start
2. **Rural:** > 900 s → ≤ 1380 s from cycle start
3. **Motorway (MW):** > 1380 s from cycle start → cycle end

**5.3.1.1 Dual-fuel engines ▼M3:** these figures calculated for **each of the two fuels separately**.

#### 5.3.2 Specific fuel consumption figures for cold-hot emission balancing factor

From both the **hotstart and coldstart WHTC** (4.3.3), calculated separately:

> **SFCmeas,hot = ΣFCmeas,hot / Wact,hot**
> **SFCmeas,cold = ΣFCmeas,cold / Wact,cold**

where `SFCmeas,j` = specific fuel consumption [g/kWh]; `ΣFCmeas,j` = total fuel consumption over the WHTC [g] (5.2); `Wact,j` = total engine work over the WHTC [kWh] (5.1).

**5.3.2.1 Dual-fuel engines ▼M3:** calculated for each of the two fuels separately.

#### 5.3.3 Specific fuel consumption figures over WHSC

From actual measured WHSC values (4.3.4):

> **SFCWHSC = ΣFCWHSC / (WWHSC + ΣE_WHRWHSC)**

where `SFCWHSC` = specific fuel consumption over WHSC [g/kWh]; `ΣFCWHSC` = total fuel consumption over WHSC [g] (5.2); `WWHSC` = total engine work over WHSC [kWh] (5.1).

For engines with **more than one WHR system**, `E_WHRWHSC` is calculated **per WHR system separately**; for engines **without** a WHR system, `E_WHRWHSC` = **0**.
- `E_WHRWHSC` = total integrated E_WHR_net over the WHSC [kWh] (per 5.5)
- `ΣE_WHRWHSC` = sum of individual `E_WHRWHSC` of all installed WHR systems [kWh]

##### 5.3.3.1 Corrected specific fuel consumption figures over WHSC

`SFCWHSC` adjusted to `SFCWHSC,corr` to account for the difference between the test fuel's NCV and the standard NCV for that fuel technology:

> **SFCWHSC,corr = SFCWHSC × (NCVmeas / NCVstd)**

where `NCVmeas` = NCV of the test fuel (3.2) [MJ/kg]; `NCVstd` = standard NCV per **Table 4** [MJ/kg].

**Table 4 — Standard net calorific values of fuel types**

| Fuel type / engine type | Reference fuel type | Standard NCV [MJ/kg] |
|---|---|---|
| Diesel / CI | B7 | 42.7 |
| Ethanol / CI | ED95 | 25.7 |
| Petrol / PI | E10 | 41.5 |
| Ethanol / PI | E85 | 29.1 |
| LPG / PI | LPG Fuel B | 46.0 |
| Natural gas / PI or Natural Gas / CI ▼M3 | G25 or GR ▼M1 | 45.1 |
| Hydrogen / PI or Hydrogen / CI ▼M4 | Hydrogen | 120.0 |
| Diesel / CI ▼M4 | B100 | 37.2 |

##### 5.3.3.2 Special provisions for B7 reference fuel ▼B

If **B7 (Diesel/CI)** reference fuel was used, the standardisation correction (5.3.3.1) is **not** performed; `SFCWHSC,corr` is set equal to the uncorrected `SFCWHSC`.

##### 5.3.3.3 Special requirements for dual-fuel engines ▼M3

Corrected SFC over WHSC calculated **for each of the two fuels separately** from their respective SFCWHSC values. Point 5.3.3.2 applies for the Diesel B7 fuel.

### 5.4 Correction factor for engines with periodically-regenerated exhaust after-treatment ▼B

For engines with after-treatment systems regenerated on a **periodic basis** (point 6.6.1 of Annex 4 to UN R49 ▼M3): fuel consumption adjusted by a correction factor **CFRegPer**, determined per point 6.6.2 of Annex 4 to UN R49.

For **continuous**-regeneration systems (point 6.6 of Annex 4 to UN R49): **no** correction factor determined — **CFRegPer = 1**.

Full-load curve (4.3.1) used to denormalise the WHTC reference cycle and compute reference values per points 7.4.6/7.4.7/7.4.8 of Annex 4 to UN R49. In addition to Annex-4 provisions, actual fuel mass flow (3.4) is recorded for **each WHTC hot-start test** per point 6.6.2 of Annex 4 to UN R49.

Specific fuel consumption for each WHTC hot-start test performed:

> **SFCmeas,m = ΣFCmeas,m / Wact,m**

where `SFCmeas,m` = specific fuel consumption [g/kWh]; `ΣFCmeas,m` = total fuel consumption over the WHTC [g] (5.2); `Wact,m` = total engine work over the WHTC [kWh] (5.1); `m` = index for each individual WHTC hot-start test.

Weighted specific fuel consumption across individual WHTC tests:

> **SFCw = (n × SFCavg + nr × SFCavg,r) / (n + nr)**

where `n` = number of WHTC hot-start tests **without** regeneration; `nr` = number of WHTC hot-start tests **with** regeneration (minimum 1); `SFCavg` = average SFC from all non-regeneration tests [g/kWh]; `SFCavg,r` = average SFC from all regeneration tests [g/kWh].

Correction factor:

> **CFRegPer = SFCw / SFCavg**

**5.4.1 Dual-fuel engines ▼M3:** CFRegPer calculated **for each of the two fuels separately**.

### 5.5 Special provisions for WHR systems ▼M3

Points 5.5.1–5.5.3 apply **only** where a WHR_mech or WHR_elec system is in the test setup; calculated separately for mechanical and electrical net power.

#### 5.5.1 Calculation of integrated E_WHR_net

Applies only to WHR-equipped engines. Negative P_WHR_net values are used directly (not zeroed). Same trapezoidal-integration structure as 5.1/5.2:

> **E_WHRmeas,i = h × [ ½P_WHRmeas,0 + P_WHRmeas,1 + P_WHRmeas,2 + … + P_WHRmeas,n₋2 + P_WHRmeas,n₋1 + ½P_WHRmeas,n ]**

where `E_WHRmeas,i` = total integrated E_WHR_net over the period t0→t1; `P_WHRmeas,k [0…n]` = recorded mechanical/electrical P_WHR_net at `t0 + k×h`, chronological order; `h` = (t1 − t0) / n.

#### 5.5.2 Calculation of specific E_WHR_net figures

Correction/balancing factors (input to the simulation tool) calculated by the engine pre-processing tool from measured specific E_WHR_net per 5.5.2.1/5.5.2.2.

##### 5.5.2.1 Specific E_WHR_net figures for WHTC correction factor

From the hotstart WHTC (4.3.3):

> **S_E_WHRmeas,Urban = E_WHRmeas,WHTC-Urban / Wact,WHTC-Urban**
> **S_E_WHRmeas,Rural = E_WHRmeas,WHTC-Rural / Wact,WHTC-Rural**
> **S_E_WHRmeas,MW = E_WHRmeas,WHTC-MW / Wact,WHTC-MW**

where `S_E_WHRmeas,i` = specific E_WHR_net over WHTC sub-cycle i **[kJ/kWh]**; `E_WHRmeas,i` = total integrated E_WHR_net over sub-cycle i [kJ] (5.5.1); `Wact,i` = total engine work over sub-cycle i [kWh] (5.1). The 3 WHTC sub-cycles as defined in 5.3.1.

##### 5.5.2.2 Specific E_WHR_net figures for cold-hot emission balancing factor

From both hotstart and coldstart WHTC (4.3.3), separately:

> **S_E_WHRmeas,hot = E_WHRmeas,hot / Wact,hot**
> **S_E_WHRmeas,cold = E_WHRmeas,cold / Wact,cold**

where `S_E_WHRmeas,j` = specific E_WHR_net over the WHTC [kJ/kWh]; `E_WHRmeas,j` = total integrated E_WHR_net over the WHTC [kJ] (5.5.1); `Wact,j` = total engine work over the WHTC [kWh] (5.1).

#### 5.5.3 WHR correction factor for periodically-regenerated after-treatment

This correction factor is **set to 1**.

---

## 6. Application of engine pre-processing tool ▼B

Executed for **each engine** within one engine CO2-family, using the input defined in 6.1. The output data of the engine pre-processing tool is the **final result** of the engine test procedure and must be documented.

### 6.1 Input data for the engine pre-processing tool

#### 6.1.1 Full load curve of the CO2-parent engine

Input = the CO2-parent engine's full-load curve (Appendix 3; 4.3.1). If Article 15(5) applied: that specific engine's own full-load curve is used instead.

**▼M3 file format:** CSV, separator = Unicode COMMA (U+002C) `,`. First line = header (no data); data from line 2. Column 1 = engine speed [min⁻¹], rounded to 2 decimal places (ASTM E 29-06). Column 2 = torque [Nm], rounded to 2 decimal places (ASTM E 29-06).

#### 6.1.2 Full load curve

Input = the engine's own full-load curve (4.3.1). Same CSV format/rounding as 6.1.1.

#### 6.1.3 Motoring curve of the CO2-parent engine

Input = CO2-parent engine's motoring curve (Appendix 3; 4.3.2). Article 15(5) exception as in 6.1.1. Same CSV format/rounding.

#### 6.1.4 Fuel consumption map of the CO2-parent engine ▼M3

Input = values determined for the CO2-parent engine (Appendix 3; point 4.3.5). Article 15(5) exception applies. Input data = **only** the average measurement values over the 30 ± 1 s period (4.3.5.5(1)).

**File format:** CSV, separator = Unicode COMMA (U+002C). Header row defines each column's content:
- **"engine speed"** → data from row 2, min⁻¹, rounded to 2 decimal places (ASTM E 29-06)
- **"torque"** → Nm, rounded to 2 decimal places (ASTM E 29-06)
- **"massflow fuel 1"** → g/h, rounded to 2 decimal places (ASTM E 29-06)

**6.1.4.1 Dual-fuel engines:** add column **"massflow fuel 2"** → g/h, rounded to 2 decimal places (ASTM E 29-06).

**6.1.4.2 WHR-equipped engines:** for **WHR_mech**: add column **"WHR mechanical power"**; for **WHR_elec**: add column **"WHR electrical power"** — values per point 4.3.5.3.1, in **W**, rounded to the nearest whole number (ASTM E 29-06).

#### 6.1.5 Specific fuel consumption figures for WHTC correction factor

Input = the three SFC values over WHTC sub-cycles (urban/rural/motorway), g/kWh, per 5.3.1. Rounded to 2 decimal places (ASTM E 29-06).

**6.1.5.1 Dual-fuel engines ▼M3:** values for "massflow fuel 1" fuel type → GUI tab **"Fuel 1"**; values for "massflow fuel 2" fuel type → GUI tab **"Fuel 2"**.

#### 6.1.6 Specific fuel consumption figures for cold-hot emission balancing factor

Input = the two SFC values (hotstart/coldstart WHTC), g/kWh, per 5.3.2. Rounded to 2 decimal places.

**6.1.6.1 Dual-fuel engines ▼M3:** same Fuel-1/Fuel-2 tab split as 6.1.5.1.

#### 6.1.7 Correction factor for periodically-regenerated after-treatment

Input = `CFRegPer` per 5.4. For continuous-regeneration systems: **1** (per 5.4). Rounded to 2 decimal places.

**6.1.7.1 Dual-fuel engines ▼M3:** Fuel-1/Fuel-2 tab split as above.

#### 6.1.8 NCV of test fuel

Input = test-fuel NCV [MJ/kg] (3.2). **▼M1:** rounded to 2 decimal places.

**6.1.8.1 Dual-fuel engines ▼M3:** Fuel-1/Fuel-2 tab split.

#### 6.1.9 Type of test fuel

Input = test-fuel type selected per 3.2. **▼M4:** diesel engine tested with **B100** reference fuel → input is **"Diesel B100 CI"**.

**6.1.9.1 Dual-fuel engines ▼M3:** Fuel-1/Fuel-2 tab split.

#### 6.1.10 Engine idle speed of the CO2-parent engine

Input = `nidle` [min⁻¹] of the CO2-parent engine, as declared by the manufacturer in the Appendix-2 information document. Article 15(5) exception applies. Rounded to nearest whole number.

#### 6.1.11 Engine idle speed

Input = `nidle` [min⁻¹] of the engine, as declared in the Appendix-2 information document. Rounded to nearest whole number.

#### 6.1.12 Engine displacement

Input = displacement [ccm], as declared. Rounded to nearest whole number.

#### 6.1.13 Engine rated speed

Input = rated speed [min⁻¹], declared at point 3.2.1.8 of the Appendix-2 information document. Rounded to nearest whole number.

#### 6.1.14 Engine rated power ▼M3

Input = rated power [kW], declared at point 3.2.1.8 of the Appendix-2 information document. Rounded to nearest whole number.

#### 6.1.15 Manufacturer

Name, ISO8859-1 character sequence.

#### 6.1.16 Model

Name, ISO8859-1 character sequence.

#### 6.1.17 Certification Number ▼M3

ISO8859-1 character sequence.

#### 6.1.18 Dual-fuel ▼M3

GUI checkbox "Dual-fuel" set active for dual-fuel engines.

#### 6.1.19 WHR_no_ext ▼M3

GUI checkbox "MechanicalOutputICE" set active.

#### 6.1.20 WHR_mech ▼M3

GUI checkbox "MechanicalOutputDrivetrain" set active.

#### 6.1.21 WHR_elec ▼M3

GUI checkbox "ElectricalOutput" set active.

#### 6.1.22 Specific E_WHR_net figures for WHTC correction factor — WHR_mech ▼M3

3 values (urban/rural/motorway), kJ/kWh, per 5.5.2.1. Rounded to 2 decimal places; GUI tab **"WHR Mechanical"**.

#### 6.1.23 Specific E_WHR_net figures for cold-hot balancing factor — WHR_mech ▼M3

2 values (hotstart/coldstart), kJ/kWh, per 5.5.2.2. Rounded to 2 decimal places; GUI tab **"WHR Mechanical"**.

#### 6.1.24 Specific E_WHR_net figures for WHTC correction factor — WHR_elec ▼M3

3 values, kJ/kWh, per 5.5.2.1. Rounded to 2 decimal places; GUI tab **"WHR Electrical"**.

#### 6.1.25 Specific E_WHR_net figures for cold-hot balancing factor — WHR_elec ▼M3

2 values, kJ/kWh, per 5.5.2.2. Rounded to 2 decimal places; GUI tab **"WHR Electrical"**.

#### 6.1.26 WHR correction factor for periodically-regenerated after-treatment ▼M3

Factor per 5.5.3. Rounded to 2 decimal places; GUI field in tab **"WHR Electrical"** (WHR_elec engines) or **"WHR Mechanical"** (WHR_mech engines).

---

## Appendix 7 — Input parameters for the simulation tool ▼M3

**Introduction:** lists parameters the component manufacturer must provide as input to the simulation tool (VECTO). The applicable XML schema and example data are available on the "dedicated electronic distribution platform" (not specified further in this Annex). The XML is **automatically generated by the engine pre-processing tool**.

**Definitions:**
1. **"Parameter ID"** — unique identifier used in the simulation tool for a specific input parameter/data set. ▼M1
2. **"Type"** — data type:
   - `string` — ISO8859-1 character sequence
   - `token` — ISO8859-1 character sequence, no leading/trailing whitespace
   - `date` — UTC date-time, format `YYYY-MM-DDTHH:MM:SSZ` (e.g. `2002-05-30T09:30:10Z`)
   - `integer` — integral type, no leading zeros (e.g. `1800`)
   - `double, X` — fractional number with exactly X digits after the decimal point, no leading zeros (e.g. `double,2` → `2345.67`; `double,4` → `45.6780`)
3. **"Unit"** — physical unit.

### Table 1 — Input parameters "Engine/General" ▼M3

| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| Manufacturer | P200 | token | [-] | |
| Model | P201 | token | [-] | |
| CertificationNumber | P202 | token | [-] | |
| Date | P203 | dateTime | [-] | Date/time the component-hash is created |
| AppVersion | P204 | token | [-] | Version number of engine pre-processing tool |
| Displacement | P061 | int | [cm³] | |
| IdlingSpeed | P063 | int | [1/min] | |
| RatedSpeed | P249 | int | [1/min] | |
| RatedPower | P250 | int | [W] | |
| MaxEngineTorque | P259 | int | [Nm] | |
| WHRTypeMechanicalOutputICE | P335 | boolean | [-] | |
| WHRTypeMechanicalOutputDrivetrain | P336 | boolean | [-] | |
| WHRTypeElectricalOutput | P337 | boolean | [-] | |
| WHRElectricalCFUrban | P338 | double,4 | [-] | Required if WHRTypeElectricalOutput = true |
| WHRElectricalCFRural | P339 | double,4 | [-] | Required if WHRTypeElectricalOutput = true |
| WHRElectricalCFMotorway | P340 | double,4 | [-] | Required if WHRTypeElectricalOutput = true |
| WHRElectricalBFColdHot | P341 | double,4 | [-] | Required if WHRTypeElectricalOutput = true |
| WHRElectricalCFRegPer | P342 | double,4 | [-] | Required if WHRTypeElectricalOutput = true |
| WHRMechanicalCFUrban | P343 | double,4 | [-] | Required if WHRTypeMechanicalOutputDrivetrain = true |
| WHRMechanicalCFRural | P344 | double,4 | [-] | Required if WHRTypeMechanicalOutputDrivetrain = true |
| WHRMechanicalCFMotorway | P345 | double,4 | [-] | Required if WHRTypeMechanicalOutputDrivetrain = true |
| WHRMechanicalBFColdHot | P346 | double,4 | [-] | Required if WHRTypeMechanicalOutputDrivetrain = true |
| WHRMechanicalCFRegPer | P347 | double,4 | [-] | Required if WHRTypeMechanicalOutputDrivetrain = true |

### Table 1a — Input parameters "Engine" per fuel type ▼M3

| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| WHTCUrban | P109 | double,4 | [-] | |
| WHTCRural | P110 | double,4 | [-] | |
| WHTCMotorway | P111 | double,4 | [-] | |
| BFColdHot | P159 | double,4 | [-] | |
| CFRegPer | P192 | double,4 | [-] | |
| CFNCV | P260 | double,4 | [-] | |
| FuelType | P193 | string | [-] | **▼M4** Allowed values: `Diesel CI`, `Ethanol CI`, `Petrol PI`, `Ethanol PI`, `LPG PI`, `NG PI`, `NG CI`, `H2 CI`, `H2 PI`, `Diesel B100 CI` |

### Table 2 — Input parameters "Engine/FullloadCurve" (per grid point in the full-load curve)

| Parameter name | Parameter ID | Type | Unit |
|---|---|---|---|
| EngineSpeed | P068 | double,2 | [1/min] |
| MaxTorque | P069 | double,2 | [Nm] |
| DragTorque | P070 | double,2 | [Nm] |

### Table 3 — Input parameters "Engine/FuelMap" (per grid point in the fuel map; one map required per fuel type) ▼M3

| Parameter name | Parameter ID | Type | Unit | Description/Reference |
|---|---|---|---|---|
| EngineSpeed | P072 | double,2 | [1/min] | |
| Torque | P073 | double,2 | [Nm] | |
| FuelConsumption | P074 | double,2 | [g/h] | |
| WHRElectricPower | P348 | int | [W] | Required if WHRTypeElectricalOutput = true |
| WHRMechanicalPower | P349 | int | [W] | Required if WHRTypeMechanicalOutputDrivetrain = true |

---

## Appendix 8 — Important evaluation steps and equations of the engine pre-processing tool ▼B

Describes the key evaluation steps performed by the engine pre-processing tool, **in the order listed**:

**1. Reading of input files and automatic check of input data**
1.1 Check requirements for input data per point 6.1 of this Annex.
1.2 Check requirements for recorded FCMC data per points 4.3.5.2 and 4.3.5.5(1) of this Annex.

**2. Calculation of characteristic engine speeds** from full-load curves of the parent engine and the actual certification engine, per point 4.3.5.2.1.

**3. Processing of fuel consumption (FC) map**
3.1 FC values at `nidle` are **copied** to engine speed (`nidle − 100 min⁻¹`) in the map.
3.2 FC values at `n95h` are **copied** to engine speed (`n95h + 500 min⁻¹`) in the map.
3.3 **Extrapolation** of FC values at all engine-speed setpoints to a torque value of **1.1 × Tmax_overall**, using **least-squares linear regression** based on the **3 measured FC points with the highest torque values** at each engine-speed setpoint. **▼M3:** extrapolated FC values lower than the measured full-load value at that speed are **set to the measured full-load value**.
3.4 **FC = 0** added for interpolated motoring-torque values at all engine-speed setpoints in the map.
3.5 **FC = 0** added for (minimum of interpolated motoring-torque values from 3.4) **minus 100 Nm**, at all engine-speed setpoints.
3.6 **▼M3:** **WHR power = 0** added at all points referred to in 3.4 and 3.5.

**4. Simulation of FC and cycle work over WHTC and sub-parts, for the actual certification engine**
4.1 WHTC reference points denormalised using the full-load-curve input, at its originally-recorded resolution.
4.2 FC calculated for the denormalised WHTC reference speed/torque values (4.1).
4.3 FC calculated with **engine inertia set to 0**.
4.4 FC calculated with standard **PT1-function** (as in the main vehicle simulation) for engine-torque response, **active**.
4.5 FC for **all motoring points** set to **0**.
4.6 FC for all non-motoring engine operation points calculated from the FC map by **Delaunay interpolation** (as in the main vehicle simulation).
4.7 Cycle work and FC calculated per the equations in points 5.1/5.2 of this Annex.
4.8 Simulated specific FC values calculated analogous to points 5.3.1/5.3.2 of this Annex (for measured values).

**5. Calculation of WHTC correction factors**
5.1 Measured values (from pre-processing-tool input) and simulated values (from step 4) used per 5.2–5.4.
5.2 **CFUrban = SFCmeas,Urban / SFCsimu,Urban**
5.3 **CFRural = SFCmeas,Rural / SFCsimu,Rural**
5.4 **CFMW = SFCmeas,MW / SFCsimu,MW**
5.5 If a calculated correction factor is **< 1**, it is **set to 1**.
5.6 **▼M3:** for **dual-fuel engines**, the calculated correction factor for a specific fuel type **may** be < 1.
5.7 **▼M3:** notwithstanding 5.6 — if, for dual-fuel engines, the ratio of (measured total specific fuel energy of both fuels) / (simulated total specific fuel energy of both fuels) is **< 1**, the specific fuel consumption values are adapted by the pre-processing tool so that ratio equals **1**.

**6. Calculation of cold-hot emission balancing factor**
6.1 Calculated per the equation in 6.2.
6.2 **BFcold-hot = 1 + 0.1 × (SFCmeas,cold − SFCmeas,hot) / SFCmeas,hot**
6.3 If the calculated factor is **< 1**, it is **set to 1**.

**7. Correction of FC values in the FC map to standard NCV**
7.1 Performed per the equation in 7.2.
7.2 **FCcorrected = FCmeasured,map × (NCVmeas / NCVstd)**
7.3 `FCmeasured,map` = the FC-map input value **after processing per step 3**.
7.4 `NCVmeas`, `NCVstd` defined per point 5.3.3.1 of this Annex.
7.5 If **B7 (Diesel/CI)** reference fuel (3.2) was used during testing, the correction in 7.1–7.4 is **not performed**.

**8. Converting engine full-load and motoring torque values (actual certification engine) to a logging frequency of 8 min⁻¹ in engine speed**
**▼M1:**
8.1 If the **average logging frequency** of the originally-recorded full-load curve is **< 6**: conversion by **arithmetical averaging** over intervals of **± 4 min⁻¹** of the given setpoint, based on the full-load-curve input at its originally-recorded resolution. If the average logging frequency is **≥ 6**: conversion by **linear interpolation**, based on the full-load-curve input at its originally-recorded resolution.

*(This is the final point of the OCR text within the assigned extraction range; point 8 of Appendix 8 is the last item transcribed — the Appendix may continue beyond the assigned line range.)*
