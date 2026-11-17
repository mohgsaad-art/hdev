# Annex III — Input Information Relating to the Characteristic of the Vehicle
## Part B: Powertrain & Component Input Parameters (Auxiliaries, Electric Machines, REESS, Fuel Cell, Powertrain Architecture)

**Source document:** Commission Regulation (EU) 2017/2400 (implementing Regulation (EC) No 595/2009) — VECTO methodology
**CELEX number:** 02017R2400
**Consolidated as of:** 01.01.2026 (consolidated text, version 007.001)
**Source lines covered in this file:** approx. 2097–2234 (powertrain/electric definitions, §2 items 11–51), 2751–3051 (Tables 3/3a Auxiliaries), 3276–3524 (Tables 7–11a: HEV/PEV/FCHV general params, EM position, EM torque limits, REESS, boosting, fuel cell system), 3737–4025 (§10 HEV/FCHV/PEV powertrain architecture definitions, Tables 14/15/15a, §10.2–10.3)
**Amendment markers:** ►B = original 2017; ►M1 = Reg 2019/318; ►M2 = Reg 2020/1181; ►M3 = Reg 2022/1379; ►M4 = Reg 2025/258.

---

## Powertrain/electrification definitions (source §2, items 11–51)

These definitions (all under the ▼M3/▼M4 consolidated text banners as noted) underpin every table in this file and are directly relevant to a BEV/HEV/FCEV sizing tool's data model.

11. **"fuel cell"**: an energy converter transforming chemical energy (input) into electrical energy (output) or vice versa.
12. **"fuel cell vehicle" (FCV)**: a vehicle with a powertrain containing **exclusively** fuel cell(s) and electric machine(s) as propulsion energy converters.
13. **"fuel cell hybrid vehicle" (FCHV)**: an FCV equipped with a powertrain containing **at least one fuel storage system and at least one rechargeable electric energy storage system** as propulsion energy storage systems.
14. **"pure ICE vehicle"**: a vehicle where **all** propulsion energy converters are internal combustion engines.
15. **"electric machine" (EM)**: an energy converter transforming between electrical and mechanical energy.
16. **"energy storage system"**: a system that stores energy and releases it in the same form as input.
17. **"propulsion energy storage system"**: an energy storage system of the powertrain that is **not** a peripheral device, whose output energy is used directly/indirectly for vehicle propulsion.
18. **"category of propulsion energy storage system"**: a fuel storage system, a rechargeable electric energy storage system (**REESS**), or a rechargeable mechanical energy storage system.
19. **"downstream"**: a powertrain position closer to the wheels than the reference position.
20. **"drivetrain"**: the connected powertrain elements transmitting mechanical energy between the propulsion energy converter(s) and the wheels.
21. **"energy converter"**: a system where output energy form differs from input energy form.
22. **"propulsion energy converter"**: an energy converter of the powertrain that is not a peripheral device, whose output energy is used directly/indirectly for propulsion.
23. **"category of propulsion energy converter"**: an internal combustion engine, an electric machine, or a fuel cell.
24. **"form of energy"**: electrical, mechanical, or chemical (including fuels).
25. **"fuel storage system"**: a propulsion energy storage system storing chemical energy as liquid or gaseous fuel.
26. **"hybrid vehicle" (HV)**: a vehicle with a powertrain containing **at least two different categories** of propulsion energy converters **and at least two different categories** of propulsion energy storage systems.
27. **"hybrid electric vehicle" (HEV)**: an HV where one propulsion energy converter is an electric machine and the other is an ICE.
28. **"serial HEV"**: HEV architecture where the ICE powers one or more electrical energy conversion paths with **no mechanical connection** between ICE and wheels.
29. **"internal combustion engine" (ICE)**: energy converter with intermittent/continuous combustible-fuel oxidation, transforming between chemical and mechanical energy.
30. **"off-vehicle charging hybrid electric vehicle" (OVC-HEV)**: a HEV chargeable from an external source.
31. **"parallel HEV"**: HEV architecture where the ICE powers **only a single mechanically connected path** between engine and wheels.
32. **"peripheral devices"**: energy-consuming/converting/storing/supplying devices not directly/indirectly used for propulsion but essential to powertrain operation.
33. **"powertrain"**: the total combination of propulsion energy storage system(s), propulsion energy converter(s), drivetrain(s) providing mechanical energy at the wheels for propulsion, **plus peripheral devices**.
34. **"pure electric vehicle" (PEV)**: a motor vehicle per Reg (EU) 2018/858 Art. 3(16), with a powertrain containing **exclusively** electric machines as propulsion energy converters **and exclusively** rechargeable electric energy storage systems as propulsion energy storage systems, and/or alternatively any other means of direct conductive/inductive electric energy supply from the power network providing propulsion energy.
35. **"upstream"**: a powertrain position further from the wheels than the reference position.
36. **"IEPC"**: an integrated electric powertrain component per point 2(36) of Annex Xb.
37. **"IHPC Type 1"**: an integrated hybrid electric vehicle powertrain component Type 1 per point 2(38) of Annex Xb.

**▼M4-introduced definitions (38–51) — i.e. new in Reg (EU) 2025/258, not present in M1–M3 text:**

38. **"dynamic charging technology"**: enables the vehicle to connect to an external electrical power supply **while in motion**, providing direct power to propulsion/auxiliary systems and/or charging the batteries.
39. **"overhead pantograph"**: dynamic charging technology using overhead contact-line infrastructure on roads.
40. **"overhead trolley"**: dynamic charging technology with current-collector poles for overhead contact-line connection.
41. **"ground rail"**: dynamic charging technology conductively transferring energy via rails embedded in/on the road surface.
42. **"wireless"**: dynamic charging technology inductively transferring energy via devices embedded in/on the road surface, providing magnetic fields.
43. **"compressed gaseous hydrogen"**: hydrogen storage technology storing hydrogen in gaseous form.
44. **"liquid hydrogen"**: hydrogen storage technology storing hydrogen in liquid form.
45. **"cryo-compressed hydrogen"** (▼M3 banner, but logically grouped with the M4 hydrogen set): stores hydrogen at temperatures from close to liquefaction up to ambient temperature, at **≥ 200 bar**; may operate at ambient temperature but nominal capacity may only be reached close to the liquefaction temperature.
46. **"empty hydrogen tank condition"**: the condition of a hydrogen tank from which a full tank can still be reached in a single refuelling event without venting, meeting either:
    (a) below which a driver indication "empty"/"almost empty" (or similar) appears; or
    (b) below which significantly limited performance is provided by the hydrogen energy conversion system.
47. **"off-vehicle charging hybrid vehicle" (OVC-HV)**: a hybrid vehicle (broader than HEV) chargeable from an external source.
48. **"off-vehicle charging fuel cell hybrid vehicle" (OVC-FCHV)**: an FCHV chargeable from an external source.
49. **"driver-selectable mode"**: a distinct driver-selectable condition that could affect emissions or fuel/energy consumption.
50. **"predominant mode"**: a single driver-selectable mode always selected at vehicle switch-on regardless of the mode active at previous shutdown, where: (a) it cannot be redefined to another mode; (b) it can only be switched to another mode by an intentional driver action after switch-on.
51. **"battery-only predominant mode"**: a predominant mode where an OVC-HV operates with propulsion energy provided **exclusively** by the REESS.

---

## Table 3 — Input parameters "Vehicle/Auxiliaries" for medium lorries and heavy lorries

Per source: "Tables 3 and 3a provide the lists for input parameters regarding auxiliary units. The technical definitions for determining these parameters are given in **Annex IX**. The parameter ID is used to provide a clear reference between the parameters of Annexes III and IX."

| Parameter name | Parameter ID | Type | Unit | Description / Reference |
|---|---|---|---|---|
| EngineCoolingFan/Technology | P181 | string | [-] | ►M4 Allowed values: `Crankshaft mounted - Electronically controlled visco clutch`, `Crankshaft mounted - Bimetallic controlled visco clutch`, `Crankshaft mounted - Discrete step clutch`, `Crankshaft mounted - On/off clutch`, `Belt driven or driven via transm. - Electronically controlled visco clutch`, `Belt driven or driven via transm. - Bimetallic controlled visco clutch`, `Belt driven or driven via transm. - Discrete step clutch`, `Belt driven or driven via transm. - On/off clutch`, `Hydraulic driven - Variable displacement pump`, `Hydraulic driven - Constant displacement pump`, `Electrically driven - Electronically controlled` ◄ |
| SteeringPump/Technology | P182 | string | [-] | ►M4 Allowed values: `Fixed displacement`, `Fixed displacement with elec. control`, `Dual displacement`, `Dual displacement with elec. control`, `Variable displacement mech. controlled`, `Variable displacement elec. controlled`, `Electric driven pump`, `Full electric steering gear`. **For PEV, FCHV or HEV with powertrain configuration `S`/`S-IEPC` (point 10.1.1), only `Electric driven pump` or `Full electric steering gear` are allowed.** Separate entry per active steered wheel axle, with axle position counted front→rear from 1. ◄ |
| ElectricSystem/Technology | P183 | string | [-] | Allowed values: `Standard technology`, `Standard technology - LED headlights, all` |
| PneumaticSystem/Technology | P184 | string | [-] | ►M4 Long allowed-value list covering supply size (`Small`/`Medium Supply 1-stage`/`Medium Supply 2-stage`/`Large Supply`) × clutch type (`ESS`, `visco clutch`, `mech. clutch`) × optional `AMS`, plus `Vacuum pump`, and electrically-driven variants (`... + elec. driven`). **For PEV or FCHV only "elec. driven" technologies are allowed values.** ◄ (full enumerated list, 30+ values, reproduced verbatim in source — see raw text for exact string list if needed for schema validation) |
| HVAC/Technology | P185 | string | [-] | Allowed values: `None`, `Default` |

## Table 3a — Input parameters "Vehicle/Auxiliaries" for heavy buses

Column headers: Heavy buses (primary vehicle) / Heavy buses (complete or completed vehicle). This table is **substantially larger** than Table 3 because heavy-bus auxiliary systems (HVAC, electric system, pneumatic system) are far more parameterized due to passenger-comfort systems (heat pumps, heating).

| Parameter name | Parameter ID | Type | Unit | Description / Reference | Primary | Complete/completed |
|---|---|---|---|---|---|---|
| EngineCoolingFan/Technology | P181 | string | [-] | ►M4 similar enumerated list to Table 3, extended with 2-stage/3-stage discrete clutch variants ◄ | X | — |
| SteeringPump/Technology | P182 | string | [-] | ►M4 Same allowed values as Table 3, same PEV/FCHV/HEV `S`/`S-IEPC` restriction to electric options, same per-axle entry rule ◄ | X | — |
| ElectricSystem/AlternatorTechnology | P294 | string | [-] | Allowed values: `conventional`, `smart`, `no alternator`. Single entry per vehicle. **Pure ICE vehicles:** only `conventional`/`smart` allowed. **HEV with powertrain config `S`/`S-IEPC`:** only `no alternator`/`conventional` allowed. ►M4 **For PEV or FCHV no input is required.** ◄ | X | — |
| ElectricSystem/SmartAlternatorRatedCurrent | P295 | integer | [A] | Separate entry per smart alternator | X | — |
| ElectricSystem/SmartAlternatorRatedVoltage | P296 | Integer | [V] | Allowed values: `12`, `24`, `48`. Separate entry per smart alternator | X | — |
| ElectricSystem/SmartAlternatorBatteryTechnology | P297 | string | [-] | Allowed values: `lead-acid battery – conventional`, `lead-acid battery – AGM`, `lead-acid battery – gel`, `li-ion battery - high power`, `li-ion battery - high energy`. Separate entry per battery charged by smart alternator system | X | — |
| ElectricSystem/SmartAlternatorBatteryNominalVoltage | P298 | Integer | [V] | Allowed values: `12`, `24`, `48`. For series-configured batteries (e.g. two 12V units for a 24V system), declare the **single unit's** nominal voltage (12V in the example). Separate entry per battery | X | — |
| ElectricSystem/SmartAlternatorBatteryRatedCapacity | P299 | Integer | [Ah] | Separate entry per battery charged by smart alternator system | X | — |
| ElectricSystem/SmartAlternatorCapacitorTechnology | P300 | string | [-] | Allowed values: `with DCDC converter`. Separate entry per capacitor | X | — |
| ElectricSystem/SmartAlternatorCapacitorRatedCapacitance | P301 | integer | [F] | Separate entry per capacitor | X | — |
| ElectricSystem/SmartAlternatorCapacitorRatedVoltage | P302 | Integer | [V] | Separate entry per capacitor | X | — |
| ElectricSystem/SupplyFromHEVPossible | P303 | boolean | [-] | ►M4 Input only required for HEV combined with alternator technology `conventional` or `smart`. ◄ | X | — |
| ElectricSystem/InteriorlightsLED | P304 | boolean | [-] | — | X | — |
| ElectricSystem/DayrunninglightsLED | P305 | boolean | [-] | — | X | — |
| ElectricSystem/PositionlightsLED | P306 | boolean | [-] | — | X | — |
| ElectricSystem/BrakelightsLED | P307 | boolean | [-] | — | X | — |
| ElectricSystem/HeadlightsLED | P308 | boolean | [-] | — | X | — |
| PneumaticSystem/SizeOfAirSupply | P309 | string | [-] | ►M4 Allowed values: `Small`, `Medium Supply 1-stage`, `Medium Supply 2-stage`, `Large Supply 1-stage`, `Large Supply 2-stage`, `not applicable`. Electrically-driven compressor → `not applicable`. **For PEV or FCHV no input is required.** ◄ | X | — |
| PneumaticSystem/CompressorDrive | P310 | string | [-] | ►M4 Allowed values: `mechanically`, `electrically`. **For PEV or FCHV, only `electrically` is allowed.** ◄ | X | — |
| PneumaticSystem/Clutch | P311 | string | [-] | ►M4 Allowed values: `none`, `visco`, `mechanically`. **For PEV or FCHV no input is required.** ◄ | X | — |
| PneumaticSystem/SmartRegenerationSystem | P312 | boolean | [-] | — | X | — |
| PneumaticSystem/SmartCompressionSystem | P313 | boolean | [-] | ►M4 For PEV, FCHV, or HEV with powertrain config `S`/`S-IEPC`, **no input required**. ◄ | X | — |
| PneumaticSystem/RatioCompressorToEngine | P314 | double,3 | [-] | ►M4 Electrically driven compressor → `0.000`. **For PEV or FCHV no input is required.** ◄ | X | — |
| PneumaticSystem/Air suspension control | P315 | string | [-] | Allowed values: `mechanically`, `electronically` | X | — |
| PneumaticSystem/SCRReagentDosing | P316 | boolean | [-] | — | X | — |
| HVAC/SystemConfiguration | P317 | int | [-] | Allowed values: `0`–`10`. Incomplete HVAC system → `0`. `0` **not** applicable for complete/completed vehicles. | X | — |
| HVAC/HeatPumpTypeDriverCompartmentCooling | P318 | string | [-] | Allowed values: `none`, `not applicable`, `R-744`, `non R-744 2-stage`, `non R-744 3-stage`, `non R-744 4-stage`, `non R-744 continuous`. `not applicable` for HVAC configs 6 and 10 (supply from passenger heat pump). | X | — |
| HVAC/HeatPumpTypeDriverCompartmentHeating | P319 | string | [-] | Same allowed values/logic as P318, for heating | X | — |
| HVAC/HeatPumpTypePassengerCompartmentCooling | P320 | string | [-] | Allowed values: `none`, `R-744`, `non R-744 2-stage`, `non R-744 3-stage`, `non R-744 4-stage`, `non R-744 continuous`. Multiple heat pumps w/ different tech → declare dominant (e.g. by power or usage preference). | X | — |
| HVAC/HeatPumpTypePassengerCompartmentHeating | P321 | string | [-] | Same as P320, for heating | X | — |
| HVAC/AuxiliaryHeaterPower | P322 | integer | [W] | Enter `0` if no auxiliary heater installed | X | — |
| HVAC/Double glazing | P323 | boolean | [-] | — | X | — |
| HVAC/AdjustableCoolantThermostat | P324 | boolean | [-] | — | X | — |
| HVAC/AdjustableAuxiliaryHeater | P325 | boolean | [-] | — | X | — |
| HVAC/EngineWasteGasHeatExchanger | P326 | boolean | [-] | ►M4 For PEV or FCHV no input is required. ◄ | X | — |
| HVAC/SeparateAirDistributionDucts | P327 | boolean | [-] | — | X | — |
| HVAC/WaterElectricHeater | P328 | boolean | [-] | ►M4 Input to be provided only for HEV, FCHV and PEV. ◄ | X | — |
| HVAC/AirElectricHeater | P329 | boolean | [-] | ►M4 Input to be provided only for HEV, FCHV and PEV. ◄ | X | — |
| HVAC/OtherHeatingTechnology | P330 | boolean | [-] | ►M4 Input to be provided only for HEV, FCHV and PEV. ◄ | X | — |

**HDEV-tool relevance:** Table 3a is the richest source of **electrified-auxiliary-load parameters** in the whole Annex — every HVAC/pneumatic/steering/electric-system auxiliary has an explicit "electric-driven" variant and explicit PEV/FCHV carve-outs. This is a ready-made checklist for an HDEV depot/bus sizing tool's auxiliary power model (e.g. electric steering pump, electric compressor, water/air electric heaters — all flagged "only for HEV/FCHV/PEV").

---

## Table 7 — General input parameters for HEV, PEV and FCHV

| Parameter name | Parameter ID | Type | Unit | Description / Reference | Heavy lorries | Medium lorries | Heavy buses (primary) | Heavy buses (complete/completed) |
|---|---|---|---|---|---|---|---|---|
| ArchitectureID | P400 | string | [-] | Per point 10.1.3. Allowed values: `E2`,`E3`,`E4`,`E-IEPC`,`P1`,`P2`,`P2.5`,`P3`,`P4`,`S2`,`S3`,`S4`,`S-IEPC`,`F2`,`F3`,`F4`,`F-IEPC` | X | X | X | — |
| ArchitectureIDPwt2 | P552 | string | [-] | ▼M4. For multiple mechanically independent powertrains (point 10.1.4), the **second** powertrain's architecture ID. Allowed values restricted to: `E2`,`E3`,`E4`,`E-IEPC`,`S2`,`S3`,`S4`,`S-IEPC`,`F2`,`F3`,`F4`,`F-IEPC` (note: **no `P*` values allowed** for the second powertrain) | X | — | X | — |
| OVC | P553 | boolean | [-] | ▼M4. Vehicle where the REESS can be charged from an external source. Shall be `true` for: OVC-HEV; PEV; OVC-FCHV where the charging device is also designed for normal vehicle operation (not just service) | X | X | X | — |
| BatteryOnlyMode | P554 | boolean | [-] | ▼M4. Declared for HV per point 2(50). **For PEV this shall always be `true`.** | X | X | X | — |
| DynamicChargingTechnology | P555 | string | [-] | ▼M4. Allowed values: `None`, `Overhead pantograph`, `Overhead trolley`, `Ground rail`, `Wireless`. `Overhead pantograph` not applicable to medium lorries. `Overhead trolley` only applicable to heavy buses. | X | X | X | X |

**HDEV-tool relevance:** `DynamicChargingTechnology` (P555, ▼M4/new) is the regulation's formal input for **catenary/pantograph/in-motion-charging buses and trucks** — directly relevant if your tool covers e-highway or opportunity-charging depot scenarios. `OVC` (P553) and `BatteryOnlyMode` (P554) are the formal flags distinguishing plug-in hybrids from pure battery-electric operation.

---

## Table 8 — Input parameters per electric machine position

Header note: "Separate entry for each individual powertrain in the case of multiple mechanically independent powertrains in accordance with point 10.1.4. (Only applicable if the component is present in the vehicle or in the specific powertrain)"

| Parameter name | Parameter ID | Type | Unit | Description / Reference |
|---|---|---|---|---|
| PowertrainPosition | P403 | string | [-] | Position of the EM per points 10.1.2/10.1.3. Allowed values: `1`,`2`,`2.5`,`3`,`4`,`GEN`. Only **one** EM position per powertrain allowed, except architecture `S` (requires EM position `GEN` **plus** one other of `2`/`3`/`4`). Position `1` **not allowed** for architectures `S` and `E`. Position `GEN` **only** allowed for architecture `S`. |
| Count | P404 | integer | [-] | Number of identical electric machines at the specified position. Where `PowertrainPosition`=`4`, Count must be a **multiple of 2** (e.g. 2, 4, 6) |
| *Electric machine system input data* | — | — | — | ▼M4. In accordance with Appendix 15 of Annex Xb |
| *ADC input data* | — | — | — | In accordance with Appendix 12 of Annex VI. Optional, for an additional single-step gear ratio (ADC) between EM shaft and the connection point to the vehicle's powertrain per point 10.1.2. Where EM is belt-connected, provisions of point 6.1.3 Annex VI apply. **Not allowed where `IHPCType` = `IHPC Type 1`.** |
| P2.5GearRatios | P407 | double,3 | [-] | Only applicable where `PowertrainPosition`=`P2.5`. Declared for **each forward gear**. Value = `nGBX_in / nEM` (EM without ADC) or `nGBX_in / nADC` (EM with ADC), where nGBX_in = transmission input shaft speed, nEM = EM output shaft speed, nADC = ADC output shaft speed |

## Table 9 — Torque limitations per electric machine position (optional)

Header note: "Declaration of separate dataset for each voltage level measured under `CertificationNumberEM`. Declaration not allowed where parameter `IHPCType` is set to `IHPC Type 1`." ▼M4 adds: "Separate entry for each individual powertrain in the case of multiple mechanically independent powertrains in accordance with point 10.1.4."

| Parameter name | Parameter ID | Type | Unit | Description / Reference |
|---|---|---|---|---|
| OutputShaftSpeed | P408 | double,2 | [1/min] | Exact same rotational-speed entries as declared under `CertificationNumberEM` for parameter `P468` of Appendix 15, Annex Xb |
| MaxTorque | P409 | double,2 | [Nm] | Maximum EM torque (referring to output shaft) as function of rotational-speed points declared under `P469`, Appendix 15, Annex Xb. Each declared max-torque value must either be **< 0.9 × original value** at that speed, or **match exactly** the original value. Declared values must **not be < 0**. Where `Count` (P404) > 1, declare torque for a **single** EM (as tested under `CertificationNumberEM`) |
| MinTorque | P410 | double,2 | [Nm] | Minimum EM torque (output shaft) vs. speed points under `P470`, Appendix 15, Annex Xb. Each declared value must either be **> 0.9 × original value**, or match exactly. Declared values must **not be > 0**. Same single-EM rule as MaxTorque when Count > 1 |

**Numeric tolerance note:** the "0.9×" derating rule in Table 9 (both directions) is an explicit, auditable tolerance band the simulation tool enforces between a certified EM's raw torque curve and the vehicle-declared (possibly software-limited) torque curve — useful if your sizing tool wants to model OEM-applied torque de-rating for durability/NVH/driveline-protection reasons without re-certifying the EM.

## Table 10 — Input parameters per REESS

"(Only applicable if the component is present in the vehicle)"

| Parameter name | Parameter ID | Type | Unit | Description / Reference |
|---|---|---|---|---|
| StringID | P411 | integer | [-] | Arrangement of representative battery sub-systems per Annex Xb at vehicle level: each battery sub-system allocated to a specific string via this parameter. All specific strings connected in **parallel**; sub-systems within one string connected in **series**. Allowed values: `1`, `2`, `3`, … |
| *REESS input data* | — | — | — | In accordance with Appendix 15 of Annex Xb |
| DeteriorationPerformanceRatio | P557 | double,2 | [%] | ▼M4. **For PEV and OVC-HV**: either the Minimum Performance Requirement (MPR) applicable to the vehicle in main lifetime per Table 3, Annex II, Reg (EU) 2024/1257 (Euro 7), **or** a Declared Performance Requirement (DPR) higher than the MPR, if declared by the manufacturer and assessed per Reg 2024/1257 and its implementing legislation. **For HV which are not OVC-HV: no input shall be provided.** |
| SOCmin | P413 | double,1 | [%] | Only relevant for REESS type `battery`. **For PEV, and for OVC-HV with battery-only predominant mode** (point 2(50)): declare as % of rated capacity at the point where zero (or OEM-defined low limit) remaining charge is indicated to driver, or where normal vehicle operation in battery-only mode becomes impossible due to low charge. **For HV that are not OVC-HV, and OVC-HV without battery-only predominant mode:** optional; only effective in the tool where the input is **higher** than the generic value documented in the user manual |
| SOCmax | P414 | double,1 | [%] | Mirror of SOCmin at the high end: for PEV/battery-only-mode OVC-HV, declare as % of rated capacity when vehicle shown as "fully charged" to driver. For other HV: optional; only effective where input is **lower** than the generic value in the user manual |

Table 10 footnotes:
(1) Cites Regulation (EU) 2024/1257 of the European Parliament and Council (24 April 2024) — "Euro 7" — on type-approval of motor vehicles/engines re: emissions **and battery durability**, amending Reg 2018/858, repealing Regs 715/2007, 595/2009, Reg 582/2011, Reg 2017/1151, **Reg 2017/2400 itself** (i.e. this very VECTO Regulation gets partially repealed/absorbed by Euro 7 in respects not detailed here) and Implementing Reg 2022/1362.
(2) **"normal vehicle operation"** excludes any significant operational limitation (example given: "limp home operation" is **not** considered normal operation) — relevant to how SOCmin is defined (the threshold is where normal, non-limp-mode operation becomes impossible).

**HDEV-tool relevance — high priority:** Table 10 is the authoritative source for **usable battery capacity / SOC-window definitions** tied directly to EU Battery-Durability (Euro 7, Reg 2024/1257) minimum performance requirements. `DeteriorationPerformanceRatio` (P557), `SOCmin` (P413) and `SOCmax` (P414) collectively define the "usable energy window" concept your sizing tool should mirror — and they are explicitly **tool-default-overridable only in the direction that narrows the usable window**, never widens it (SOCmin input only effective if *higher* than generic; SOCmax only effective if *lower*).

## Table 11 — Boosting limitations for parallel HEV (optional)

"Only allowed where powertrain configuration in accordance with point 10.1.1 is `P` or `IHPC Type 1`."

| Parameter name | Parameter ID | Type | Unit | Description / Reference |
|---|---|---|---|---|
| RotationalSpeed | P415 | double,2 | [1/min] | Referring to transmission input shaft speed |
| BoostingTorque | P416 | double,2 | [Nm] | In accordance with point 10.2 |

## Table 11a — Input parameters per fuel cell system (▼M4, new)

"(Only applicable if the component is present in the vehicle) One or two different fuel cell systems, each may have up to 3 identical units installed."

| Parameter name | Parameter ID | Type | Unit | Description / Reference |
|---|---|---|---|---|
| Count | P558 | integer | [-] | Number of identical units. Allowed values: `1`, `2`, `3` |
| MinPower | P559 | integer | [W] | Optional. Declared lower power limit of the fuel cell system at vehicle integration level |
| MaxPower | P560 | integer | [W] | Optional. Declared upper power limit of the fuel cell system at vehicle integration level |
| *fuel cell system input data* | — | — | — | In accordance with Appendix 15 of Annex Xb |

**HDEV-tool relevance:** Table 11a (entirely new under ▼M4 / Reg 2025/258) confirms the regulation now supports **up to two distinct fuel cell system types, each with up to 3 identical units** — i.e. a max of 6 physical fuel cell stacks per vehicle in the formal input schema, each optionally power-limited independently of its certified rating.

---

## §10 — HEV, FCHV and PEV: powertrain architecture (▼M4 heading; applies "only in the case of HEV, FCHV and PEV")

### 10.1 Definition of vehicle's powertrain architecture

**10.1.1 Powertrain configuration** — determined as:
- HEV: `P` (parallel HEV) / `S` (serial HEV) / `S-IEPC` (IEPC component present) / `IHPC Type 1` (where the EM component parameter `IHPCType` = `IHPC Type 1`)
- PEV: `E` (EM component present) / `E-IEPC` (IEPC component present)
- FCHV (▼M4): `F` (EM component present) / `F-IEPC` (IEPC component present)

**10.1.2 Positions of EMs in the vehicle's powertrain** — where powertrain configuration (10.1.1) is `P`, `S`, `F` or `E`, EM position is per **Table 14**:

### Table 14 — Possible positions of EMs in the vehicle's powertrain

| Position index of EM | Powertrain configuration | Transmission type (Table 1, App.12, Annex VI) | Definition / Requirements | Further explanations |
|---|---|---|---|---|
| **1** | P | AMT, APT-S, APT-P | Connected upstream of the clutch (AMT) or upstream of the torque-converter input shaft (APT-S/APT-P). EM connected to ICE crankshaft directly or via mechanical connection (e.g. belt). | Distinction of "P0": EMs that in principle **cannot** contribute to propulsion (i.e. alternators) are handled as auxiliary-system input (Table 3/3a + Annex IX), not here. However, EMs at this position that **can** in principle propel but whose declared max torque (Table 9) is set to **zero** shall be declared as `P1`. |
| **2** | ►M4 E, S, F ◄ | AMT | EM connected downstream of the clutch and upstream of the transmission input shaft. | — |
| **2** | E, S | AMT, APT-N, APT-S, APT-P | EM connected upstream of the transmission input shaft (AMT/APT-N) or upstream of the torque converter input shaft (APT-S/APT-P). | — |
| **2,5** | P | AMT, APT-S, APT-P | EM connected downstream of the clutch (AMT) or downstream of torque-converter input shaft (APT-S/APT-P), and upstream of the transmission output shaft. | EM connected to a specific shaft inside the transmission (e.g. layshaft). A specific transmission ratio for **each mechanical gear** must be provided (per Table 8 / `P2.5GearRatios`). |
| **3** | P | AMT, APT-S, APT-P | EM connected downstream of transmission output shaft, upstream of the axle. | — |
| **3** | ►M4 E, S, F ◄ | n.a. | EM connected upstream of the axle. | — |
| **4** | P | AMT, APT-S, APT-P | EM connected downstream of the axle. | — |
| **4** | ►M4 E, S, F ◄ | n.a. | EM connected to the wheel hub; same arrangement installed **twice** in symmetric application (one left, one right, at the same longitudinal wheel position). | — |
| **GEN** | S | n.a. | EM mechanically connected to an ICE but **under no operational circumstances** mechanically connected to the vehicle's wheels. | — |

Footnote: "The term EM as used here includes an additional ADC component, if present."

**10.1.3 Powertrain architecture ID** — determined from powertrain configuration (10.1.1) + EM position (10.1.2) via **Table 15**'s valid combinations.

**Special rule for `IHPC Type 1`:**
(a) Architecture ID `P2` is declared (Table 7), and the powertrain component data per Table 15's `P2` row is the simulation-tool input, with **separate** component data for EM and transmission per point 4.4.3 of Annex Xb.
(b) EM component data under (a) is provided with `PowertrainPosition` (Table 8) set to `2`.

### Table 15 — Valid inputs of powertrain architecture into the simulation tool

| Powertrain type | Config | Architecture ID | ICE present | EM pos. GEN | EM pos. 1 | EM pos. 2 | Transmission present | EM pos. 3 | Axle present | EM pos. 4 | Comments |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PEV | E | **E2** | no | no | no | yes | yes | no | yes | no | — |
| PEV | E | **E3** | no | no | no | no | no | yes | yes | no | — |
| PEV | E | **E4** | no | no | no | no | no | no | no | yes | — |
| PEV | IEPC | **E-IEPC** | no | no | no | no | no | no | (1) | no | — |
| HEV | P | **P1** | yes | no | yes | no | yes | no | yes | no | — |
| HEV | P | **P2** | yes | no | no | yes | yes | no | yes | no | (2) |
| HEV | P | **P2.5** | yes | no | no | yes | yes | no | yes | no | (3) |
| HEV | P | **P3** | yes | no | no | no | yes | yes | yes | no | (4) |
| HEV | P | **P4** | yes | no | no | no | yes | no | yes | yes | — |
| HEV | S | **S2** | yes | yes | no | yes | yes | no | yes | no | — |
| HEV | S | **S3** | yes | yes | no | no | no | yes | yes | no | — |
| HEV | S | **S4** | yes | yes | no | no | no | no | no | yes | — |
| HEV | S-IEPC | **S-IEPC** | yes | yes | no | no | no | no | (1) | no | — |
| FCHV (▼M4) | F | **F2** | no | no | no | yes | yes | no | yes | no | — |
| FCHV | F | **F3** | no | no | no | no | no | yes | yes | no | — |
| FCHV | F | **F4** | no | no | no | no | no | no | no | yes | — |
| FCHV | F-IEPC | **F-IEPC** | no | no | no | no | no | no | (1) | no | — |

Table 15 footnotes:
(1) "Yes" (axle component present) **only** where both `DifferentialIncluded` and `DesignTypeWheelMotor` are set to `false`.
(2) Not applicable for transmission types APT-S and APT-P.
(3) Where the EM is connected to a specific shaft inside the transmission (e.g. layshaft) per the Table 8/14 definition.
(4) Not applicable for front-wheel-driven vehicles.

**10.1.4 Second mechanically independent powertrain (▼M4, new provision)**

Where the vehicle has **two powertrains**, each propelling **different wheel axles**, that **can under no circumstances be mechanically connected**, the manufacturer declares a **second powertrain ID** per 10.1.3. The two powertrains must **share the same REESS** and have **separate electrical-to-mechanical energy converters**.

Hydraulically driven axles are treated as **non-driven** per point 5(a) and therefore **do not count** as a mechanically independent powertrain.

**Only** configurations `S`, `S-IEPC`, `F`, `F-IEPC` and `E` may be declared for a second independent powertrain (i.e. **no parallel-HEV `P*` second powertrain** is allowed). Only the architecture-ID combinations marked "yes" in **Table 15a** are valid.

### Table 15a — Valid inputs of powertrain architecture for first + second powertrain (architecture ID × ArchitectureIDPwt2)

| 1st \ 2nd → | E2 | E3 | E4 | E-IEPC | S2 | S3 | S4 | S-IEPC | F2 | F3 | F4 | F-IEPC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **E2** | yes | yes | yes | yes | no | no | no | no | no | no | no | no |
| **E3** | yes | yes | yes | yes | no | no | no | no | no | no | no | no |
| **E4** | yes | yes | yes | yes | no | no | no | no | no | no | no | no |
| **E-IEPC** | yes | yes | yes | yes | no | no | no | no | no | no | no | no |
| **S2** | no | no | no | no | yes | yes | yes | yes | no | no | no | no |
| **S3** | no | no | no | no | yes | yes | yes | yes | no | no | no | no |
| **S4** | no | no | no | no | yes | yes | yes | yes | no | no | no | no |
| **S-IEPC** | no | no | no | no | yes | yes | yes | yes | no | no | no | no |
| **F2** | no | no | no | no | no | no | no | no | yes | yes | yes | yes |
| **F3** | no | no | no | no | no | no | no | no | yes | yes | yes | yes |
| **F4** | no | no | no | no | no | no | no | no | yes | yes | yes | yes |
| **F-IEPC** | no | no | no | no | no | no | no | no | yes | yes | yes | yes |

**Reading:** an `E*` powertrain can only pair with another `E*` powertrain; `S*` only with `S*`; `F*` only with `F*`. Cross-category dual powertrains (e.g. one electric + one fuel-cell axle) are **not** valid inputs. **Flag for HDEV tool:** this directly constrains any "dual independent axle powertrain" (e.g. e-axle front + e-axle rear with separate inverters but shared battery) design you might model — mixed-technology dual powertrains are excluded by the regulation's input schema.

### 10.2 Boosting limitation for parallel HEV

The manufacturer **may** declare limits on total propulsion torque (referring to transmission input shaft) for a parallel HEV, to restrict boosting capability. Only allowed where powertrain configuration (10.1.1) is `P` or `IHPC Type 1`.

Limitations are declared as **additional torque allowed on top of the ICE full-load curve**, as a function of transmission input shaft rotational speed; the simulation tool **linearly interpolates** between declared points. **In the rotational speed range 0 → engine idling speed** (point 7.1), the full-load torque available from the ICE equals **only the ICE full-load torque at idling speed**, due to clutch-behaviour modelling during vehicle starts.

Where declared: values for additional torque must be given **at least** at rotational speed `0` and at the **maximum rotational speed of the ICE full-load curve**; any number of intermediate values may be declared. Declared additional-torque values **below zero are not allowed**. A manufacturer may declare a limitation that exactly matches the ICE full-load curve by declaring `0 Nm` additional torque throughout.

### 10.3 Engine stop-start functionality for HEVs

Where the vehicle has engine stop-start per point 8.1.1 (considering the boundary conditions of point 8.4, reproduced in file `04c`), input parameter `P271` (Table 6, file 04c) **shall be set to `true`**.

---

## Cross-references to other Annexes resolved/unresolved in this range

- Engine input data → **Appendix 7 of Annex V** (not in this extraction range — flagged as external cross-reference).
- Transmission/torque-converter/angle-drive/retarder input data → **Appendix 12 of Annex VI**, Tables 1–9 (external cross-reference, not extracted here).
- Axle input data → **Appendix 6 of Annex VII**, Tables 1–2 (external, not extracted here).
- Tyre input data → **Appendix 3 of Annex X** (external, not extracted here; see file 04a Table 2).
- Wheel-end friction → **Annex VIIa, point 3.6** (external).
- Air drag input data → **Appendix 9 of Annex VIII**, Table 1 (external).
- IEPC / EM / REESS / fuel cell system component input data → **Appendix 15 of Annex Xb** (external, referenced repeatedly — this appears to be the single most important cross-referenced appendix for electric-powertrain component certification data and would be very high-value to extract next if available in the source PDF).
- `IHPCType` parameter and "IHPC Type 1" architecture detail → **Annex Xb, point 2(38) and point 4.4.3** (external).
- Representative battery sub-system arrangement on vehicle level → **Annex Xb** generally (external).

None of these component-level Annexes (V, VI, VII, VIIa, VIII, IX [partially — auxiliary definitions], X, Xa, Xb) were part of the assigned line range (1993–4315) and are **not** reproduced here; they would need separate extraction if required for the tool's component-level data model.
