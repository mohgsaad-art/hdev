# Method C run inside VECTO's own engine: 2 single-gear trucks

16 Nov 2026. Owner: Bob. Branch `vecto-engine-method-c-2026-11`, from `group5-class-numbers-2026-11` (PR #38, head c80200b). Folder `docs/research/vecto-engine-method-c-2026-11/`.
Analysis only: no notebook, `src/` or harness edit. VECTO fork `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126` (VectoCore 4.3.4-DEV).
Trucks: C0091 IVECO S-eWay (group 5, 1-gear IEPC, 12 results) and C0059 Fuso eCanter (group 1, 1-gear IEPC, 4 results). Every certified mission except Municipal, as PR #37 Part 3.

Contains data from the European Environment Agency (EEA) HDV CO2 monitoring 2024-25, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Derived values, not endorsed by the EEA. [DATA]

**Scope of this version.** The refit with F0 placed inside the IEPC map (planned as a robustness check) was **not run**; Bob stopped new runs. Its consequence is stated in "Two caveats".

## What this test can and cannot show

- Can: split the hide-one error into "HDEV engine" (driver, braking, motor-off rows, step size) and "C form plus unknown inputs", by fitting and testing the same method C on the same certified results with both engines. [TEST]
- Cannot: reveal an effect that is the same on every mission (a constant extra per km). C absorbs it with either engine. It also cannot separate an effect that both engines share: both engines get the same inputs, so a wrong input (tyre test load, battery, IEPC losses) sits in both. [ASSUMPTION / interpretation]
- "Certified" here means the PR #37 target: EEA `ElectricEnergy_kwh_km`. Both engines are compared with it as terminal energy / 0.995. This is calibration on certified VECTO results, not validation.

## Answers

**1. How much of the hide-one error disappears with VECTO's engine?** (Table 6, 7)

| 16 results, both trucks | HDEV engine (PR #37) | VECTO engine | disappears |
|---|---:|---:|---:|
| mean absolute error | 3.98 % | 2.88 % | 28 % |
| worst error | 12.70 % | 11.21 % | 12 % |
| Urban mean absolute error (6 results) | 6.88 % | 5.65 % | 18 % |

- S-eWay (12 results): mean absolute 1.55 % to 0.74 % (52 % disappears), worst 3.71 % to 2.75 % (26 %), Urban mean absolute 2.53 % to 2.31 % (9 %).
- eCanter (4 results): mean absolute 11.25 % to 9.29 % (17 %), worst 12.70 % to 11.21 % (12 %), Urban mean absolute 11.24 % to 8.99 % (20 %).
- By the definition of the test, the part that disappears is HDEV's engine and the remainder is C's form plus unknown inputs. For the S-eWay the HDEV share is not shown to be robust (caveat 2). For the eCanter it is a small share: 80 % or more of its hide-one error is not HDEV's engine.
- The size of the engine effect at fixed method C values: VECTO predicts 1.4 to 1.6 % lower energy on average, 2.2 to 2.9 % lower on Urban, about equal on Long Haul (Table 8). At the wheel, VECTO asks 0.2 % (eCanter Regional) to 6.0 % (S-eWay Urban) less net energy from the powertrain than HDEV, most in stop-and-go cycles (Table 4). [TEST]

**2. Do the fitted values change between engines, and by how much?** (Table 5)
- S-eWay: eta_d 0.966 to 0.930, eta_r 0.913 to 0.922, F0 603 to 461 N, CdxA 5.650 (upper edge of range A14, at the bound) to 5.643 (inside). rms error on all results 1.17 % to 0.53 %. The CdxA edge hit seen in PR #37/#38 does not appear with VECTO's engine.
- eCanter: eta_d 0.689 to 0.653, eta_r 1.0 (at its upper bound) in both, F0 106 N to 0.5 N (at its lower bound). rms 8.06 % to 7.00 %.

**3. eCanter: does the 8-12 % miss remain with VECTO's engine?** Yes: hide-one errors -10.4, -8.8, +6.8, +11.2 % with VECTO against -12.0, -10.6, +9.8, +12.7 % with HDEV. Even fitted on all four results the VECTO-engine rms is 7.0 %, with eta_r and F0 both at their bounds. Evidence on the cause is in Part 3. The cause itself is [OPEN]; the strongest lead is a loss that grows faster than linearly with speed in a standard-values IEPC.

## Two caveats that change how the numbers above must be read

### Caveat 1. What the EEA number is: battery loss and certified-definition

- The harness (PR #37) and this study compare with terminal energy / 0.995, where terminal energy = `E_REESS_T_dischg - E_REESS_T_chg`. This follows the earlier definition; it is not what VECTO reports as the declaration result.
- VECTO's declaration result is `EC_el_final = (-integral of P_reess_int) / charging efficiency`: `BatteryElectricPostprocessingCorrection.cs` line 45, written to the report at `XMLDeclarationReport.cs` line 255. `P_reess_int` is the **internal** battery power, so it contains the battery internal-resistance loss (and the junction-box and cable loss is in the terminal figure already). The charging efficiency is computed from the battery for a depot charge (`DeclarationData.cs` line 1948), not fixed at 0.995. [VECTO]
- That the EEA field is this quantity is likely but **not verified** in the EEA data. [OPEN]
- Size, from this study's own runs with a **generic battery** (Ri not scaled to the real pack, capacity and voltage from EEA): EC_el_final is higher than terminal energy by 2.1 to 7.5 % on the S-eWay (mean 3.7 %, Urban 6.2 %), and by 1.0 to 1.3 % on the eCanter (Table 12). The battery loss depends on current squared, so it is larger on Urban and on heavy loads. C cannot absorb a mission- and load-dependent term.
- The real battery data (internal resistance curve, open-circuit voltage curve, SoC window, per-pack capacity) are in the vehicle XML and not in EEA: `NO SOURCE`. The generic battery is therefore an assumption, and the 2 to 7.5 % is an illustration of size, not a result for these trucks.
- Consequence: **no fit in this study tests battery loss as an HDEV-engine difference.** All fits use the terminal definition for both engines. If the EEA value is EC_el_final, part of every error reported here, in both engines, is this definition mismatch. It would push the S-eWay Urban and heavy-load results up relative to Regional and Long Haul. It is too small (1.0 to 1.3 %) to explain the eCanter's 7 to 11 %.

### Caveat 2. Where F0 is placed in VECTO changes the prediction

- Prompt construction used here: F0 as a constant loss torque F0 x r_dyn in a separate axle gear (ratio 1.0, loss map with a constant "Torque Loss" column), placed after the IEPC. Both EEA IEPCs include the differential, so this axle gear exists only as our construction. The IEPC is then declared with `DifferentialIncluded = false`. [ASSUMPTION]
- That loss acts on the vehicle in every phase, including coasting and braking, so it also changes the speed trace. The harness applies F0 only to rows where the powertrain is engaged. These are two different meanings of "F0".
- Measured at the same method C values (Table 11): putting the same loss torque **inside the IEPC map** instead lowers the S-eWay prediction by 0.9 to 1.7 % (mean -1.35 %). On the eCanter the effect is nil (F0 is about 0 there).
- This 1.35 % is the same size as the engine effect at fixed values (1.4 to 1.6 %) and as the hide-one gap for the S-eWay (0.8 pp). **The refit with F0 inside the IEPC map was not run**, so it is not shown that the S-eWay result "52 % of the mean error is HDEV's engine" survives a change of F0 placement. Treat that figure as conditional on the axle-loss construction. The eCanter result does not depend on it (F0 about 0 in both engines). [OPEN]

# Part 0: can VECTO run here?

Yes. [TEST]
- Build: `VectoConsole` (`vectocmd.dll`, target net6.0) built with the .NET 9.0.319 SDK; no .NET 6 runtime is installed, so it runs on the 9.0 runtime with `DOTNET_ROLL_FORWARD=Major` and `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1`. Script `build_vecto.sh`. Build time 24 s.
- Run: `dotnet vectocmd.dll [-mod] [-t] BEV_E2.vecto` on `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BEV_E2.vecto`. The job runs 6 results (3 cycles x 2 loadings).
- Version: the fork is 4.3.4-DEV, Bob's 22 Oct numbers are from 5.1.6-RC (not available here). The reference-load numbers agree to 0.05 %.

**Table 1. E2 reference.**

| cycle | loading | terminal kWh/km (VECTO fork 4.3.4-DEV) | EC_el_final kWh/km | Bob 22 Oct (5.1.6-RC) | difference |
|---|---:|---:|---:|---:|---:|
| LongHaul | LowLoading | 1.3505 | 1.3676 |  |  |
| LongHaul | ReferenceLoad | 1.5255 | 1.5499 |  |  |
| RegionalDelivery | LowLoading | 0.9923 | 1.0021 |  |  |
| RegionalDelivery | ReferenceLoad | 1.0504 | 1.0621 | 1.05 | +0.04 % |
| UrbanDelivery | LowLoading | 0.7482 | 0.7566 |  |  |
| UrbanDelivery | ReferenceLoad | 0.8404 | 0.8528 | 0.84 | +0.05 % |

Time per run:

**Table 2. Timing.**

| mode | command | runs | wall s | CPU s |
|---|---:|---:|---:|---:|
| sequential with mod data | vectocmd -mod -t BEV_E2.vecto | 6 | 75.2 | 75.4 |
| parallel no mod data | vectocmd -t BEV_E2.vecto | 6 | 28.8 | 110.0 |

Without `-v` and `-mod` the runs go in parallel. Later jobs (4 to 12 results) took 21 to 23 s (eCanter) and 53 s (S-eWay) alone; four S-eWay jobs together took 85 s.

# Part 1: job files

## 1.1 Every input, value and source (`p1_inputs_table.csv`) [DATA] [VECTO] [ASSUMPTION]

| truck | input | value | source | tag |
|---|---:|---:|---:|---:|
| C0091 | vehicle | Iveco S-eWay, group 5, N3 4x2 | EEA vehicles_xev.csv Make, Model, VehicleGroup, VehicleCategory, AxleConfiguration | [DATA] |
| C0091 | median-mass vehicle id | 0xB15F0952A80BC0AD... | harness.config_runs (PR #37 rule: one vehicle per exact config) | [ASSUMPTION] |
| C0091 | CurbWeight [kg] | 11782.0 | EEA vehicles_xev.csv CorrectedActualMass of that vehicle | [DATA] |
| C0091 | MassMax / TPMLM [t] | 20.0 | EEA vehicles_xev.csv TechnicalPermissibleMaximumLadenMass | [DATA] |
| C0091 | IEPC rated power [kW] | 851.0 | EEA vehicles_xev.csv iepc_desc (RatedPower) | [DATA] |
| C0091 | IEPC gears / lowest total ratio | 1 / 25.101 | EEA iepc_desc; differential included (hdv_2024_iepc.csv DifferentialIncluded = true) | [DATA] |
| C0091 | IEPC certification method (EEA) | Measured | EEA configs: iepc_cert_method | [DATA] |
| C0091 | axle 1 tyre / RRC / twin | 385/55 R22.5 / 0.0045 / False | EEA axle_xev.csv TyreDimension, SpecificRRC, Twintyres | [DATA] |
| C0091 | axle 1 wheel inertia per tyre [kgm2] / r_dyn [m] | 15.9 / 0.4803 | VECTO Resources/Declaration/Wheels.csv (same file the harness reads) | [VECTO] |
| C0091 | axle 2 tyre / RRC / twin | 315/70 R22.5 / 0.0068 / True | EEA axle_xev.csv TyreDimension, SpecificRRC, Twintyres | [DATA] |
| C0091 | axle 2 wheel inertia per tyre [kgm2] / r_dyn [m] | 14.9 / 0.4922 | VECTO Resources/Declaration/Wheels.csv (same file the harness reads) | [VECTO] |
| C0091 | FzISO [N] | 31300.0 | NO SOURCE (EEA has no FzISO); harness stand-in | [ASSUMPTION] |
| C0091 | air drag | Measured, range A14 | EEA AirDrag_CertificationMethod, AirDrag_CdxA_range; Reg. 2018/956 Annex I Part C via cdxa_ranges.py | [DATA]/[REG] |
| C0091 | auxiliaries | ES Standard technology; PS 'Small + elec. driven'; HVAC Default; steering: Electric driven pump | EEA Aux_Pneumatic_Technology; VECTO VAUX tables (same as harness aux_per_label.csv) | [DATA]/[VECTO] |
| C0091 | battery | installed 729 kWh, nominal 660 V | EEA bat_installed_kwh, bat_nominal_v; the terminal energy does not depend on it | [DATA]/[ASSUMPTION] |
| C0059 | vehicle | Fuso Canter, group 1, N2 4x2 | EEA vehicles_xev.csv Make, Model, VehicleGroup, VehicleCategory, AxleConfiguration | [DATA] |
| C0059 | median-mass vehicle id | 0x7047015223518ACA... | harness.config_runs (PR #37 rule: one vehicle per exact config) | [ASSUMPTION] |
| C0059 | CurbWeight [kg] | 4204.0 | EEA vehicles_xev.csv CorrectedActualMass of that vehicle | [DATA] |
| C0059 | MassMax / TPMLM [t] | 8.55 | EEA vehicles_xev.csv TechnicalPermissibleMaximumLadenMass | [DATA] |
| C0059 | IEPC rated power [kW] | 132.0 | EEA vehicles_xev.csv iepc_desc (RatedPower) | [DATA] |
| C0059 | IEPC gears / lowest total ratio | 1 / 19.528 | EEA iepc_desc; differential included (hdv_2024_iepc.csv DifferentialIncluded = true) | [DATA] |
| C0059 | IEPC certification method (EEA) | StandardValues | EEA configs: iepc_cert_method | [DATA] |
| C0059 | axle 1 tyre / RRC / twin | 225/70 R19.5 / 0.0067 / False | EEA axle_xev.csv TyreDimension, SpecificRRC, Twintyres | [DATA] |
| C0059 | axle 1 wheel inertia per tyre [kgm2] / r_dyn [m] | 6.4 / 0.3937 | VECTO Resources/Declaration/Wheels.csv (same file the harness reads) | [VECTO] |
| C0059 | axle 2 tyre / RRC / twin | 225/70 R19.5 / 0.0072 / True | EEA axle_xev.csv TyreDimension, SpecificRRC, Twintyres | [DATA] |
| C0059 | axle 2 wheel inertia per tyre [kgm2] / r_dyn [m] | 6.4 / 0.3937 | VECTO Resources/Declaration/Wheels.csv (same file the harness reads) | [VECTO] |
| C0059 | FzISO [N] | 31300.0 | NO SOURCE (EEA has no FzISO); harness stand-in | [ASSUMPTION] |
| C0059 | air drag | Standard values, range A19 | EEA AirDrag_CertificationMethod, AirDrag_CdxA_range; Reg. 2018/956 Annex I Part C via cdxa_ranges.py | [DATA]/[REG] |
| C0059 | auxiliaries | ES Standard technology; PS 'Vacuum pump + elec. driven'; HVAC Default; steering: Electric driven pump | EEA Aux_Pneumatic_Technology; VECTO VAUX tables (same as harness aux_per_label.csv) | [DATA]/[VECTO] |
| C0059 | battery | installed 123 kWh, nominal 348 V | EEA bat_installed_kwh, bat_nominal_v; the terminal energy does not depend on it | [DATA]/[ASSUMPTION] |

Unknown or not published, same choices as the PR #37 harness so both engines get the same inputs:
- exact CdxA inside its range: range middle as start, then fitted inside the range for the S-eWay (measured air drag); the eCanter has standard-value air drag, so CdA = the VECTO default 7.1 m2, not fitted. [ASSUMPTION]
- tyre test load FzISO 31,300 N on all axles: `NO SOURCE`, the harness stand-in. [ASSUMPTION]
- curb mass: not unknown. EEA `CorrectedActualMass` of the median-mass vehicle (11,782 kg; 4,204 kg). VECTO's total masses equal EEA's to 1 kg on all 16 results; the program stops if not.
- payloads: VECTO computes them (group 5 from the segment table, group 1 from `Payloads.csv` by interpolation to 8,550 kg: 332.76 and 1,663.82 kg, EEA 333 and 1,664). [VECTO]
- aux labels: ES Standard technology; PS from EEA; HVAC Default; steering "Full electric steering gear" because the harness sets the steering pump to 0 W (EEA says "Electric driven pump"). VECTO still adds 32 W for it (vmod column `P_aux_STP_el`). Total aux agrees with the harness within 0.001 kWh/km on all 16 results (Table 3).

VECTO rules used (every line read in the fork):

| rule | VECTO file (fork b8d6126) | line | use here |
|---|---:|---:|---:|
| loss map: points are stored at (input speed, input torque - torque loss) -> constant loss torque is a constant column | VectoCore/VectoCore/Models/SimulationComponent/Data/Gearbox/TransmissionLossMap.cs | 77 | F0 as axle loss: constant Torque Loss column |
| loss map: loss is read at (out speed x ratio, out torque / ratio) and is a torque at the input side | VectoCore/VectoCore/Models/SimulationComponent/Data/Gearbox/TransmissionLossMap.cs | 94 | axle ratio 1.0, so input side = wheel side: T0 = F0 x r_dyn |
| loss map: Torque Loss must be between 0 and 1,000,000 Nm | VectoCore/VectoCore/Models/SimulationComponent/Data/Gearbox/TransmissionLossMap.cs | 153 | F0 = 0 gives loss 0, allowed |
| IEPC power map reader: lowest speed entries are copied to 0 rpm by clustering the lowest two speeds | VectoCore/VectoCore/InputData/Reader/ComponentData/IEPCMapReader.cs | 85 | map speed grid starts 0, 3.37, 33.7 rpm like the VECTO generic IEPC |
| IEPC power map reader: map is triangulated on (-torque, speed) with the electric power as value | VectoCore/VectoCore/InputData/Reader/ComponentData/IEPCMapReader.cs | 55 | interpolation is linear between grid points |
| IEPC power map reader: map is extended to 1.2 x the full-load torque by scaling | VectoCore/VectoCore/InputData/Reader/ComponentData/IEPCMapReader.cs | 144 | map covers +-T_cap |
| standard-values IEPC gets two fake voltage levels (1 V, 10e9 V) | VectoCore/VectoCore/InputData/Reader/DataObjectAdapter/SimulationComponents/ElectricMachinesDataAdapter.cs | 82 | our IEPC uses 100 V and 2000 V levels with the same map |
| electric energy of the declaration result = (-integral P_reess_int) / charging efficiency | VectoCore/VectoCore/OutputData/ModDataPostprocessing/Impl/BatteryElectricPostprocessingCorrection.cs | 45 | EC_el_final includes the battery internal loss |
| result written to the declaration report = ElectricEnergyConsumption_Final | VectoCore/VectoCore/OutputData/XML/XMLDeclarationReport.cs | 255 | EEA field is most likely this one; not verified in the EEA file |
| charging efficiency of the battery (depot charging) | VectoCore/VectoCore/Models/Declaration/DeclarationData.cs | 1948 | depends on the real battery |
| segment group 5 tractor 4x2, vocational 0 | VectoCore/VectoCore/Resources/Declaration/SegmentTable.csv | 17 | payloads, trailers, axle shares, CdxA default |
| segment group 1 rigid 4x2 (7.5-10 t) | VectoCore/VectoCore/Resources/Declaration/SegmentTable.csv | 6 | body B1, payload pc10/pc50 |
| payload of group 1: 10 % and 50 % payload by gross vehicle weight (7,500 t row) | VectoCore/VectoCore/Resources/Declaration/Payloads.csv | 4 | 333 kg and 1,664 kg for 8,550 kg by linear interpolation to the 16,000 row |
| payload of group 1 (16,000 row) | VectoCore/VectoCore/Resources/Declaration/Payloads.csv | 5 | interpolation partner |
| body B1 curb mass 1,600 kg | VectoCore/VectoCore/Resources/Declaration/Body_Trailers_Weights.csv | 4 | total mass of the eCanter = CurbWeight + 1,600 + payload |
| semitrailer ST1 7,500 kg, delta CdxA 0 / 2.1 | VectoCore/VectoCore/Resources/Declaration/Body_Trailers_Weights.csv | 17 | total mass of the S-eWay |
| wheel data 315/70 R22.5 (r_dyn, inertia) | VectoCore/VectoCore/Resources/Declaration/Wheels.csv | 41 | inertia 14.9 kgm2 |
| wheel data 385/55 R22.5 | VectoCore/VectoCore/Resources/Declaration/Wheels.csv | 50 | inertia 15.9 kgm2 |
| wheel data 225/70 R19.5 | VectoCore/VectoCore/Resources/Declaration/Wheels.csv | 113 | inertia 6.4 kgm2 |
| declared CdxA replaced by the default on the construction mission | VectoCore/VectoCore/InputData/Reader/DataObjectAdapter/SimulationComponents/AirdragDataAdapter.cs | 147 | same rule in the harness |
| PEV auxiliaries: ES standard technology | VectoCore/VectoCore/Resources/Declaration/VAUX/ES-Tech.csv | 2 | same as harness aux_per_label.csv |
| steering pump technology 'Full electric steering gear' factor | VectoCore/VectoCore/Resources/Declaration/VAUX/SP-Tech.csv | 9 | gives 32 W in the vmod (UF 0 but base share), the harness uses 0 W |
| alternator efficiency 0.7 | VectoCore/VectoCore/Models/Declaration/DeclarationData.cs | 123 | aux conversion |
| distance-based runs use a target time interval of 0.5 s (vmod column dt) | VectoCore/VectoCore/Configuration/Constants.cs | 277 | step size is a VECTO engine feature (HDEV uses 1 s) |

## 1.2 Method C as VECTO inputs (all constructions by us) [ASSUMPTION]

| C term | VECTO construction | why |
|---|---|---|
| eta_d, eta_r | IEPC power map (`.viepco`: n_out [rpm], T_out [Nm], P_el [kW]) with P_el = T x omega / eta_d for T > 0 and T x omega x eta_r for T < 0, on the wheel side (the differential is inside the IEPC, so n_out and T_out are wheel shaft values) | constant efficiency |
| torque limits | full-load curve T = min(T_cap, P_rated / omega), same for recuperation. P_rated = EEA IEPC rated power (851 kW, 132 kW). T_cap = 60,000 Nm (S-eWay), 12,000 Nm (eCanter) at the wheel, chosen above the largest torque the driver's acceleration limit asks, so the limit is power, as in the harness (`p_max = rated kW`). | EEA gives no torque limit: `NO SOURCE` |
| continuous / overload rating | set equal to the full-load curve, overload time 300 s | no derating, as the harness |
| drag curve | 0 Nm | harness variant V-A has zero coasting drag |
| IEPC inertia | 0 | the harness has none; EEA has none |
| F0 | constant torque loss F0 x r_dyn in a ratio-1.0 axle gear (`TransmissionLossMap.cs` lines 77, 94, 153); see caveat 2 | prompt |
| CdxA | `CdA` in the vehicle file; VECTO replaces it by the default on Construction (`AirdragDataAdapter.cs` line 147) and adds the trailer delta, like the harness | same rules |
| battery | generic battery file scaled in capacity to the EEA installed kWh; terminal energy does not depend on it, EC_el_final does (caveat 1) | NO SOURCE for the real battery |

The map grid has 24 speeds (first speeds 0, 3.37, 33.7 rpm because the reader finds the zero-rpm entries from the two lowest speeds, `IEPCMapReader.cs` line 85) and 91 torques (geometric). VECTO linearly interpolates the product T x omega between grid points. Offline on the harness wheel-power rows of both trucks the energy error of the interpolation is at most 0.14 %. A denser grid (14,000 points) made reading the files take 201 s, so it was not used. [TEST]

## 1.3 Check of the construction: eta_d = eta_r = 1, F0 = 0 (`p1_balance.csv`) [TEST]

Balance: `E_terminal = E_IEPC_el + E_aux + E_cables` closes to 0.00001 kWh/km or better on all 16 results. With a lossless map the IEPC electric energy equals the wheel energy to 0.0004 kWh/km (0.05 %; the interpolation error). Mechanical brake loss at most 0.0003 kWh/km. Aux: VECTO against harness within 0.001 kWh/km.

**Table 3. Balance check.**

| truck | mission | payload kg | terminal kWh/km (vsum) | terminal - (IEPC el + aux + cables) | IEPC electric | wheel in | IEPC el - wheel in | mechanical brake loss | aux VECTO | aux harness |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0059 | Regional Delivery | 333 | 0.73011 | -0.0 | 0.69864 | 0.6986 | 5e-05 | 0.0 | 0.03133 | 0.03124 |
| C0059 | Regional Delivery | 1664 | 0.7548 | -0.0 | 0.72349 | 0.72347 | 2e-05 | 0.0 | 0.03116 | 0.03127 |
| C0059 | Urban Delivery | 333 | 0.43259 | 0.0 | 0.36606 | 0.36595 | 0.00011 | 0.0 | 0.0664 | 0.06635 |
| C0059 | Urban Delivery | 1664 | 0.45761 | 0.0 | 0.39107 | 0.39068 | 0.0004 | 0.00029 | 0.06637 | 0.06639 |
| C0091 | Construction | 2600 | 0.87015 | 1e-05 | 0.81394 | 0.81388 | 6e-05 | 0.0 | 0.05556 | 0.05545 |
| C0091 | Construction | 12900 | 1.02211 | 1e-05 | 0.96537 | 0.96534 | 3e-05 | 1e-05 | 0.05542 | 0.05514 |
| C0091 | Long Haul | 2600 | 0.9447 | -0.0 | 0.90781 | 0.90778 | 3e-05 | 0.0 | 0.03651 | 0.03712 |
| C0091 | Long Haul | 19300 | 1.18435 | 0.0 | 1.14725 | 1.14723 | 2e-05 | 0.0 | 0.03619 | 0.03711 |
| C0091 | Long Haul EMS | 3500 | 1.21297 | 0.0 | 1.17583 | 1.17581 | 2e-05 | 0.0 | 0.03651 | 0.03712 |
| C0091 | Long Haul EMS | 26500 | 1.54349 | -0.0 | 1.50573 | 1.50572 | 1e-05 | 0.0 | 0.03618 | 0.03712 |
| C0091 | Regional Delivery | 2600 | 0.87794 | -0.0 | 0.83655 | 0.83652 | 3e-05 | 0.0 | 0.0409 | 0.04126 |
| C0091 | Regional Delivery | 12900 | 1.02811 | -0.0 | 0.98636 | 0.98634 | 2e-05 | 0.0 | 0.04082 | 0.04123 |
| C0091 | Regional Delivery EMS | 3500 | 1.13246 | 0.0 | 1.09074 | 1.09072 | 2e-05 | 0.0 | 0.04091 | 0.04126 |
| C0091 | Regional Delivery EMS | 17500 | 1.34008 | -0.0 | 1.29766 | 1.29766 | 1e-05 | 0.0 | 0.04082 | 0.04123 |
| C0091 | Urban Delivery | 2600 | 0.65227 | -0.0 | 0.55962 | 0.55953 | 9e-05 | 0.0 | 0.09144 | 0.09109 |
| C0091 | Urban Delivery | 12900 | 0.80279 | -0.0 | 0.70889 | 0.70876 | 0.00013 | 8e-05 | 0.09139 | 0.09116 |

What each engine asks of the powertrain at the wheel (eta = 1, F0 = 0), net energy per km, VECTO against HDEV:

**Table 4. Wheel energy, two engines.**

| truck | mission | results | net wheel energy VECTO vs HDEV, mean % | min % | max % | drive side % | regen side (magnitude) % |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0059 | Regional | 2 | -0.2 | -0.2 | -0.2 | -0.5 | -6.2 |
| C0059 | Urban | 2 | -3.5 | -3.7 | -3.3 | -2.9 | -2.0 |
| C0091 | Construction | 2 | -4.1 | -5.3 | -2.8 | -2.7 | -0.6 |
| C0091 | Long | 4 | -0.7 | -1.3 | -0.3 | -0.9 | -2.6 |
| C0091 | Regional | 4 | -3.8 | -4.9 | -2.9 | -2.7 | +1.1 |
| C0091 | Urban | 2 | -6.0 | -6.6 | -5.3 | -2.4 | -0.5 |

The harness has a one-second row of -4.1 MW wheel power in the S-eWay Construction 2,600 kg result (VECTO's largest wheel power for the same result is -476 kW; rated power 851 kW). Elsewhere the largest regeneration rows are similar in both engines (S-eWay Urban 12,900 kg: -707 kW HDEV, -739 kW VECTO). VECTO writes 0.5 s steps; HDEV uses 1 s. Which of driver, braking limit, motor-off rows and step size causes the 0.2 to 6 % was **not separated**. [OPEN]

# Part 2: method C fitted in VECTO

## 2.1 Method [TEST]

Same objective as PR #37 (`methods_lib.fit_v2`): relative residuals pred/cert - 1, bounds eta_d 0.5-1, eta_r 0.3-1, F0 0-3000 N, declared CdxA inside its Reg. 2018/956 Annex I Part C range for measured air drag; variables scaled by their upper bound; method `trf`. The PR #37 starts were used: the HDEV optimum and the third PR #37 start (0.95, 0.95, 0 N). Every function value is one VECTO job. The Jacobian comes from finite differences at the start (one job per parameter) and Broyden updates from the exact VECTO residuals afterwards. Both starts reached the same valley (S-eWay costs 1.654e-4 and 1.669e-4; eCanter 0.00981 both); the lower cost is kept. A fresh finite-difference gradient at the S-eWay solution is 0.0015 (scaled units).
Hide-one: each fold starts at the full-data solution with the Jacobian from there held fixed; the residuals are exact VECTO values. A fresh finite-difference gradient at the fold solution is 5e-5 (fold 11, the largest error) and 2e-4 (fold 10, which has CdxA at its bound), checked on these two folds only. All 212 VECTO jobs (100 S-eWay, 112 eCanter, 4 of them the F0-in-IEPC evaluations) are listed in `p2_vecto_runs.csv`; each command stayed under 10 minutes and resumed from the cache.

## 2.2 Fitted values, both engines (Table 5, `p2_fitted_values.csv`)

**Table 5. Fitted values.**

| truck | engine | values fitted | eta_d | eta_r | F0 N | CdxA m2 | rms error on all results % | at a bound |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0091 IVECO S-eWay | HDEV engine (PR #37) | 4 | 0.96641 | 0.91328 | 602.8034 | 5.65 | 1.168 | cdxa_declared |
| C0091 IVECO S-eWay | VECTO engine | 4 | 0.93048 | 0.92237 | 461.47771 | 5.64332 | 0.525 | none |
| C0059 Fuso eCanter | HDEV engine (PR #37) | 3 | 0.68868 | 1.0 | 105.91395 | - | 8.06 | regen |
| C0059 Fuso eCanter | VECTO engine | 3 | 0.65261 | 1.0 | 0.46346 | - | 7.003 | regen;F0 |

## 2.3 Per truck and mission (`p2_per_result.csv`, figure `p3_hide_one.png`)

Hide-one prediction and error for each result; the last two columns are the error when fitted on all results.

| truck | mission | payload kg | certified kWh/km | HDEV hide-one pred | HDEV err % | VECTO hide-one pred | VECTO err % | HDEV err % (fit on all) | VECTO err % (fit on all) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0091 | Construction | 2600 | 1.139 | 1.1363 | -0.24 | 1.1346 | -0.39 | -0.20 | -0.27 |
| C0091 | Construction | 12900 | 1.337 | 1.352 | +1.12 | 1.3353 | -0.13 | +0.99 | -0.11 |
| C0091 | Long Haul | 2600 | 1.189 | 1.1631 | -2.18 | 1.1723 | -1.40 | -1.49 | -0.90 |
| C0091 | Long Haul | 19300 | 1.457 | 1.4424 | -1.00 | 1.4545 | -0.17 | -0.88 | -0.16 |
| C0091 | Long Haul EMS | 3500 | 1.473 | 1.4504 | -1.53 | 1.4714 | -0.11 | -1.32 | -0.11 |
| C0091 | Long Haul EMS | 26500 | 1.854 | 1.821 | -1.78 | 1.8529 | -0.06 | -1.23 | -0.06 |
| C0091 | Regional Delivery | 2600 | 1.125 | 1.1364 | +1.01 | 1.1231 | -0.17 | +0.77 | -0.05 |
| C0091 | Regional Delivery | 12900 | 1.302 | 1.3306 | +2.20 | 1.3079 | +0.46 | +1.98 | +0.42 |
| C0091 | Regional Delivery EMS | 3500 | 1.4 | 1.4116 | +0.83 | 1.4102 | +0.73 | +0.74 | +0.62 |
| C0091 | Regional Delivery EMS | 17500 | 1.654 | 1.682 | +1.69 | 1.6654 | +0.69 | +1.23 | +0.44 |
| C0091 | Urban Delivery | 2600 | 0.9854 | 0.9987 | +1.35 | 1.0039 | +1.87 | +0.68 | +0.97 |
| C0091 | Urban Delivery | 12900 | 1.247 | 1.2008 | -3.71 | 1.2127 | -2.75 | -1.42 | -0.83 |
| C0059 | Regional Delivery | 333 | 1.235 | 1.0871 | -11.97 | 1.1064 | -10.42 | -10.07 | -8.82 |
| C0059 | Regional Delivery | 1664 | 1.262 | 1.1286 | -10.57 | 1.1515 | -8.75 | -8.68 | -7.35 |
| C0059 | Urban Delivery | 333 | 0.738 | 0.8101 | +9.78 | 0.7881 | +6.78 | +4.89 | +3.79 |
| C0059 | Urban Delivery | 1664 | 0.7822 | 0.8815 | +12.70 | 0.8698 | +11.21 | +7.70 | +7.07 |

![hide-one errors](p3_hide_one.png)

Method C values at fixed values, VECTO engine against HDEV engine (`p2_engine_at_fixed_theta.csv`), Table 8:

**Table 8. Engine effect at fixed values.**

| method C values | truck | missions | results | VECTO minus HDEV, mean % | min % | max % |
|---|---:|---:|---:|---:|---:|---:|
| HDEV fit values | C0091 | Urban | 2 | -2.23 | -2.84 | -1.61 |
| HDEV fit values | C0091 | Regional | 4 | -1.94 | -2.66 | -1.20 |
| HDEV fit values | C0091 | Long | 4 | -0.12 | -0.62 | +0.34 |
| HDEV fit values | C0091 | Constr | 2 | -1.90 | -2.85 | -0.94 |
| HDEV fit values | C0091 | all results | 12 | -1.37 | -2.85 | +0.34 |
| HDEV fit values | C0059 | Urban | 2 | -2.54 | -2.64 | -2.43 |
| HDEV fit values | C0059 | Regional | 2 | -0.18 | -0.24 | -0.12 |
| HDEV fit values | C0059 | all results | 4 | -1.36 | -2.64 | -0.12 |
| VECTO fit values | C0091 | Urban | 2 | -2.57 | -3.08 | -2.06 |
| VECTO fit values | C0091 | Regional | 4 | -2.24 | -2.99 | -1.55 |
| VECTO fit values | C0091 | Long | 4 | -0.25 | -0.74 | +0.20 |
| VECTO fit values | C0091 | Constr | 2 | -2.24 | -3.18 | -1.30 |
| VECTO fit values | C0091 | all results | 12 | -1.63 | -3.18 | +0.20 |
| VECTO fit values | C0059 | Urban | 2 | -2.87 | -3.00 | -2.73 |
| VECTO fit values | C0059 | Regional | 2 | -0.28 | -0.36 | -0.21 |
| VECTO fit values | C0059 | all results | 4 | -1.57 | -3.00 | -0.21 |

# Part 3: the answer in numbers

## 3.1 Summary (Table 6, `p3_summary.csv`)

**Table 6. Summary.**

| truck | test | engine | mean error % | mean abs % | worst abs % | Urban mean abs % | Urban worst abs % | within 5 % (share %) | too low (share %) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0091 | fit on all results | HDEV engine (PR #37) | -0.01 | 1.08 | 1.98 | 1.05 | 1.42 | 100 | 50 |
| C0091 | fit on all results | VECTO engine | -0.00 | 0.41 | 0.97 | 0.9 | 0.97 | 100 | 67 |
| C0091 | hide one result | HDEV engine (PR #37) | -0.19 | 1.55 | 3.71 | 2.53 | 3.71 | 100 | 50 |
| C0091 | hide one result | VECTO engine | -0.12 | 0.74 | 2.75 | 2.31 | 2.75 | 100 | 67 |
| C0059 | fit on all results | HDEV engine (PR #37) | -1.54 | 7.83 | 10.07 | 6.3 | 7.7 | 25 | 50 |
| C0059 | fit on all results | VECTO engine | -1.33 | 6.76 | 8.82 | 5.43 | 7.07 | 25 | 50 |
| C0059 | hide one result | HDEV engine (PR #37) | -0.02 | 11.25 | 12.7 | 11.24 | 12.7 | 0 | 50 |
| C0059 | hide one result | VECTO engine | -0.30 | 9.29 | 11.21 | 8.99 | 11.21 | 0 | 50 |

## 3.2 Share of the error that disappears with VECTO's engine (Table 7, `p3_share_removed_by_vecto_engine.csv`)

**Table 7. Share removed.**

| truck | test | metric | HDEV engine % | VECTO engine % | share that disappears % |
|---|---:|---:|---:|---:|---:|
| C0091 | fit on all results | mean absolute error | 1.08 | 0.41 | 61.9 |
| C0091 | fit on all results | worst absolute error | 1.98 | 0.97 | 51.2 |
| C0091 | fit on all results | Urban mean absolute error | 1.05 | 0.9 | 14.5 |
| C0091 | fit on all results | Urban worst absolute error | 1.42 | 0.97 | 31.7 |
| C0091 | hide one result | mean absolute error | 1.55 | 0.74 | 52.1 |
| C0091 | hide one result | worst absolute error | 3.71 | 2.75 | 25.7 |
| C0091 | hide one result | Urban mean absolute error | 2.53 | 2.31 | 8.6 |
| C0091 | hide one result | Urban worst absolute error | 3.71 | 2.75 | 25.7 |
| C0059 | fit on all results | mean absolute error | 7.83 | 6.76 | 13.7 |
| C0059 | fit on all results | worst absolute error | 10.07 | 8.82 | 12.4 |
| C0059 | fit on all results | Urban mean absolute error | 6.3 | 5.43 | 13.8 |
| C0059 | fit on all results | Urban worst absolute error | 7.7 | 7.07 | 8.2 |
| C0059 | hide one result | mean absolute error | 11.25 | 9.29 | 17.4 |
| C0059 | hide one result | worst absolute error | 12.7 | 11.21 | 11.8 |
| C0059 | hide one result | Urban mean absolute error | 11.24 | 8.99 | 20.0 |
| C0059 | hide one result | Urban worst absolute error | 12.7 | 11.21 | 11.8 |
| both trucks (16 results) | fit on all results | mean absolute error | 2.77 | 2.0 | 27.8 |
| both trucks (16 results) | fit on all results | worst absolute error | 10.07 | 8.82 | 12.4 |
| both trucks (16 results) | fit on all results | Urban mean absolute error | 3.67 | 3.16 | 13.9 |
| both trucks (16 results) | fit on all results | Urban worst absolute error | 7.7 | 7.07 | 8.2 |
| both trucks (16 results) | hide one result | mean absolute error | 3.98 | 2.88 | 27.6 |
| both trucks (16 results) | hide one result | worst absolute error | 12.7 | 11.21 | 11.8 |
| both trucks (16 results) | hide one result | Urban mean absolute error | 6.88 | 5.65 | 17.9 |
| both trucks (16 results) | hide one result | Urban worst absolute error | 12.7 | 11.21 | 11.8 |

## 3.3 eCanter: what is left, and what could cause it

Facts (VECTO engine unless noted):
1. The miss remains: hide-one -10.4, -8.8, +6.8, +11.2 %; in-sample rms 7.0 %; eta_r = 1.0 and F0 = 0.5 N are both at their bounds (Table 5). Training on 3 results with 3 values still leaves 5.9 to 7.6 % rms, so the form cannot fit even those. [TEST]
2. The certified energy is 1.66 to 1.70 times the lossless wheel-plus-aux energy of VECTO on all four results (Table 9), almost the same factor for Regional and Urban although Urban recovers about 9 times more regeneration per unit of drive energy. A constant efficiency with free regeneration cannot do that: the Urban results come out too high or Regional too low. [CALC]
3. The extra energy (certified minus lossless) is 0.50 kWh/km in Regional and 0.30 to 0.32 in Urban, almost independent of payload (Table 9). Multiplied by the average speed that is 30.6 to 30.8 kW at 61.1 km/h and 8.1 to 8.6 kW at 26.7 km/h. The ratio 3.7 for a speed ratio 2.29 is a power law with exponent 1.6 on two missions. F0 gives a loss power proportional to speed (exponent 1), so it cannot follow. The S-eWay with a measured IEPC has 15 to 19 kW and 9 to 12 kW at the same speeds (exponent about 0.6). [CALC]
4. If eta_r is allowed up to 3, the HDEV engine fits all four results to 0.38 % rms with eta_r = 1.63, which is not physical. VECTO's map reader does not represent that: at eta_r 1.029 instead of 0.999 the energy goes up by 0.6 to 0.8 pp (Table 10), so the VECTO side of this test cannot be run. [TEST]
5. The EEA IEPC certification method is `StandardValues` with no certificate number. In PR #39 the DAF configs with a standard-values IEPC needed 1.3 to 1.6 times the harness physics; the eCanter needs 1.34 to 1.49 times (`p1_ecanter_ratio.csv` of that PR). [DATA]
6. Battery loss and the EC_el_final definition add 1.0 to 1.3 % on this truck with a generic battery (Table 12), far too small. F0 placement: no effect (F0 about 0).

Possible causes, none confirmed:
- A speed-dependent loss in the standard-values IEPC that grows faster than linear, for example iron and windage loss at the high internal speed (the vmod shows 11,000 rpm at 85 km/h). Support: fact 3. Not supported or refuted: the standard-values IEPC data are not available (`NO SOURCE`). [OPEN]
- A regeneration credit smaller than the model gives, with a drive loss that is not proportional to energy. Support: fact 2 and 4. [OPEN]
- Unknown inputs shared by both engines (tyre test load, the EEA vehicle's real battery and its internal resistance). Too small to explain 7 to 11 % by the sizes seen here. [OPEN]

What would decide it (Bob to fetch): the eCanter standard-values IEPC loss map as VECTO builds it (vehicle XML or an XML-based VECTO run), and the real battery data.

**Table 9. Certified against lossless VECTO energy (eta 1, F0 0), `p3_certified_vs_lossless.csv`.**

| truck | mission | payload kg | certified kWh/km | VECTO lossless (eta 1, F0 0) kWh/km | certified / lossless | extra kWh/km | average speed km/h | extra x speed kW | VECTO C fit error % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0091 | Construction | 2600 | 1.139 | 0.8745 | 1.302 | 0.2645 | 45.71 | 12.09 | -0.27 |
| C0091 | Construction | 12900 | 1.337 | 1.0272 | 1.302 | 0.3098 | 45.74 | 14.17 | -0.11 |
| C0091 | Long Haul | 2600 | 1.189 | 0.9494 | 1.252 | 0.2396 | 80.21 | 19.21 | -0.90 |
| C0091 | Long Haul | 19300 | 1.457 | 1.1903 | 1.224 | 0.2667 | 80.33 | 21.42 | -0.16 |
| C0091 | Long Haul EMS | 3500 | 1.473 | 1.2191 | 1.208 | 0.2539 | 80.21 | 20.37 | -0.11 |
| C0091 | Long Haul EMS | 26500 | 1.854 | 1.5512 | 1.195 | 0.3028 | 80.33 | 24.32 | -0.06 |
| C0091 | Regional Delivery | 2600 | 1.125 | 0.8824 | 1.275 | 0.2426 | 61.05 | 14.81 | -0.05 |
| C0091 | Regional Delivery | 12900 | 1.302 | 1.0333 | 1.26 | 0.2687 | 61.06 | 16.41 | +0.42 |
| C0091 | Regional Delivery EMS | 3500 | 1.4 | 1.1382 | 1.23 | 0.2618 | 61.04 | 15.98 | +0.62 |
| C0091 | Regional Delivery EMS | 17500 | 1.654 | 1.3468 | 1.228 | 0.3072 | 61.06 | 18.76 | +0.44 |
| C0091 | Urban Delivery | 2600 | 0.9854 | 0.6555 | 1.503 | 0.3299 | 26.65 | 8.79 | +0.97 |
| C0091 | Urban Delivery | 12900 | 1.247 | 0.8068 | 1.546 | 0.4402 | 26.63 | 11.72 | -0.83 |
| C0059 | Regional Delivery | 333 | 1.235 | 0.7338 | 1.683 | 0.5012 | 61.14 | 30.64 | -8.82 |
| C0059 | Regional Delivery | 1664 | 1.262 | 0.7586 | 1.664 | 0.5034 | 61.11 | 30.76 | -7.35 |
| C0059 | Urban Delivery | 333 | 0.738 | 0.4348 | 1.697 | 0.3032 | 26.67 | 8.09 | +3.79 |
| C0059 | Urban Delivery | 1664 | 0.7822 | 0.4599 | 1.701 | 0.3223 | 26.65 | 8.59 | +7.07 |

Relaxed eta_r (Table 10, `p3_relaxed_etar.csv`):

| engine / run | eta_d | eta_r | F0 N | rms % | errors on the 4 results % (Reg 333, Reg 1664, Urb 333, Urb 1664) |
|---|---:|---:|---:|---:|---:|
| HDEV | 0.6235 | 1.6262 | 157.3 | 0.381 | -0.53;+0.52;+0.12;-0.11 |
| VECTO at fixed eta_d 0.652, F0 0.5 N | 0.652 | 0.999 | 0.5 |  | -8.73;-7.26;+3.94;+7.23 |
| VECTO at fixed eta_d 0.652, F0 0.5 N | 0.652 | 1.029 | 0.5 |  | -8.68;-7.20;+4.59;+8.00 |

F0 inside the IEPC map instead of the axle loss map (Table 11, `p2_f0_construction.csv`):

| truck | method C values | F0 inside the IEPC map vs F0 in the axle loss map, mean % | min % | max % |
|---|---:|---:|---:|---:|
| C0091 | HDEV fit values | -1.74 | -2.17 | -1.19 |
| C0091 | VECTO fit values | -1.35 | -1.71 | -0.92 |
| C0059 | HDEV fit values | -0.27 | -0.40 | -0.13 |
| C0059 | VECTO fit values | -0.01 | -0.01 | -0.00 |

EC_el_final against terminal energy, generic battery (Table 12, `p2_final_vs_terminal.csv`):

| truck | mission | payload kg | certified kWh/km | terminal / 0.995 | EC_el_final / 0.995 (generic battery) | final vs terminal % | error terminal basis % | error final basis % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0091 | Construction | 2600 | 1.139 | 1.1359 | 1.1679 | +2.8 | -0.27 | +2.54 |
| C0091 | Construction | 12900 | 1.337 | 1.3355 | 1.3918 | +4.2 | -0.11 | +4.10 |
| C0091 | Long Haul | 2600 | 1.189 | 1.1783 | 1.2028 | +2.1 | -0.90 | +1.16 |
| C0091 | Long Haul | 19300 | 1.457 | 1.4547 | 1.5014 | +3.2 | -0.16 | +3.05 |
| C0091 | Long Haul EMS | 3500 | 1.473 | 1.4714 | 1.508 | +2.5 | -0.11 | +2.38 |
| C0091 | Long Haul EMS | 26500 | 1.854 | 1.8529 | 1.929 | +4.1 | -0.06 | +4.05 |
| C0091 | Regional Delivery | 2600 | 1.125 | 1.1245 | 1.1518 | +2.4 | -0.05 | +2.38 |
| C0091 | Regional Delivery | 12900 | 1.302 | 1.3075 | 1.3524 | +3.4 | +0.42 | +3.87 |
| C0091 | Regional Delivery EMS | 3500 | 1.4 | 1.4087 | 1.4506 | +3.0 | +0.62 | +3.61 |
| C0091 | Regional Delivery EMS | 17500 | 1.654 | 1.6613 | 1.7342 | +4.4 | +0.44 | +4.85 |
| C0091 | Urban Delivery | 2600 | 0.9854 | 0.9949 | 1.0426 | +4.8 | +0.97 | +5.81 |
| C0091 | Urban Delivery | 12900 | 1.247 | 1.2367 | 1.3299 | +7.5 | -0.83 | +6.65 |
| C0059 | Regional Delivery | 333 | 1.235 | 1.1261 | 1.1371 | +1.0 | -8.82 | -7.93 |
| C0059 | Regional Delivery | 1664 | 1.262 | 1.1692 | 1.1816 | +1.1 | -7.35 | -6.37 |
| C0059 | Urban Delivery | 333 | 0.738 | 0.7659 | 0.7744 | +1.1 | +3.79 | +4.93 |
| C0059 | Urban Delivery | 1664 | 0.7822 | 0.8375 | 0.8485 | +1.3 | +7.07 | +8.48 |

# Lists

**NO SOURCE**
- Real battery data of both trucks (internal resistance, open-circuit voltage curve, SoC window, per-pack capacity); the generic battery is an assumption.
- The standard-values IEPC data of the eCanter (loss map); IEPC torque limits, continuous rating, inertia, gear and axle ratio split (EEA gives total ratio only).
- Tyre test load FzISO.
- The EEA definition of `ElectricEnergy_kwh_km` (terminal energy against EC_el_final), not verified in the EEA files.

**BLOCKED**
- VECTO 5.1.6-RC (Bob's 22 Oct version) is not available here; the 4.3.4-DEV fork was used. The two agree on the E2 reference to 0.05 %.
- VECTO cannot represent eta_r > 1, so the relaxed-eta_r test exists for the HDEV engine only.
- The F0-in-IEPC-map refit and hide-one test were not run (stopped by Bob).

**Bob to fetch**
1. The eCanter and S-eWay vehicle XML (battery, IEPC) or a VECTO run of them, to settle caveat 1 and fact 5 of Part 3.3.
2. Which VECTO field the EEA `ElectricEnergy_kwh_km` is (EC_el_final or terminal energy), for example from one EEA vehicle with a known VECTO run.

**Choices I made**
1. VECTO fork 4.3.4-DEV, built from the `IEPC-experiments` commit b8d6126, not 5.1.6-RC.
2. Terminal energy / 0.995 as the target for both engines (the PR #37 definition); EC_el_final reported beside it but not fitted.
3. F0 as an axle-gear loss map (the prompt's construction) as the only fitted construction; F0 inside the IEPC map only evaluated at fixed values.
4. Torque cap 60,000 Nm and 12,000 Nm at the wheel; continuous = overload rating; IEPC inertia 0; drag 0. All unsourced.
5. Starts: the HDEV optimum and the third PR #37 start; the second start of the S-eWay reached the same valley.
6. Hide-one with a fixed Jacobian and an exact finite-difference gradient check on 2 of the 12 S-eWay folds; the eCanter folds were not gradient checked (training rms is 5.9 to 7.6 %, bounds active).
7. The HDEV engine side is PR #37's own code, recomputed (`hdev_reference.py`); the hide-one predictions match `part3_predictions.csv` to 0.00005 kWh/km.
8. Python packages in a virtual environment outside the repo (`/projects/sandbox/.venv`), because system site-packages are read-only.

**Kiro's recommendation (Bob decides).** Before using the engine split for the S-eWay, run the F0-in-IEPC-map refit (about 40 minutes). Before comparing with EEA numbers at the 1 to 7 % level, settle which VECTO field the EEA value is.

# How to run

```bash
bash build_vecto.sh                                   # builds vectocmd from the fork
cd docs/research/vecto-engine-method-c-2026-11
python hdev_reference.py                              # HDEV engine fits (PR #37 code)
python p1_balance.py                                  # Part 1.3
python part2_fit.py C0059 full axle; python part2_fit.py C0059 loro axle      # repeat the same command until it prints DONE (10-minute budget)
python part2_fit.py C0091 full axle; python part2_fit.py C0091 loro axle
python part2_extra.py all; python part3_relaxed.py; python part3_answer.py; python p3_plot.py
python p1_vecto_refs.py; python build_report.py
```
