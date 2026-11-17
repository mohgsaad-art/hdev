# Drivetrain option x drag table: kWh/km and 360 km battery (3 Nov 2026)

Test run by Claude (script: scratchpad `matrix.py`, reuses Kiro's PR #23 modules `_chain.py`, `_driver_dragtable.py`, `std_table()` and the `18940ab` vehicle helpers). Nothing in `src/engine/` changed.

Setup: generic VECTO E2 (2 x 125 kW, 11.99 t GVW), reference load (Urban/Regional 9,590 kg; LongHaul = E2 + trailer, 19,811 kg), VECTO-equivalent weather (rho 1.188, declaration wind), aux = VECTO `.vmod` mean P_aux_el (1769 / 1983 / 2267 W), driver model with the agreed edits (g = 9.80665, drag table), gear 2 fixed. kWh/km at battery terminals, no battery losses.

Baseline checks: today's code 0.712 / 0.573 (22 Oct: 0.712 / 0.574); EU std maps 0.947 / 0.815 (exact); E2 maps 1.012 / 0.786 (22 Oct 1.012 / 0.787).

## kWh/km

| Case | Urban | Regional | LongHaul |
|---|---|---|---|
| Constant eff 0.95/0.95/0.98, no drag (today) | 0.573 | 0.712 | 1.158 |
| Constant eff + VECTO E2 drag | 0.601 | 0.723 | 1.175 |
| EU std maps (E2 inputs), no drag | 0.815 | 0.947 | 1.426 |
| EU std maps + EU std drag | 0.842 | 0.970 | 1.447 |
| EU std maps + VECTO E2 drag | 0.857 | 0.976 | 1.456 |
| E2 maps, no drag | 0.786 | 1.012 | 1.494 |
| E2 maps + VECTO E2 drag | 0.831 | 1.048 | 1.530 |
| VECTO (terminals) | 0.840 | 1.050 | 1.525 |
| VECTO incl. battery losses (`EC_el_final`) | 0.853 | 1.062 | 1.550 |

## Usable battery for 360 km (kWh/km x 360)

| Case | Urban | Regional | LongHaul |
|---|---|---|---|
| Constant eff, no drag (today) | 207 | 256 | 417 |
| Constant eff + VECTO E2 drag | 216 | 260 | 423 |
| EU std maps, no drag | 293 | 341 | 513 |
| EU std maps + EU std drag | 303 | 349 | 521 |
| EU std maps + VECTO E2 drag | 308 | 351 | 524 |
| E2 maps + VECTO E2 drag | 299 | 377 | 551 |
| VECTO incl. battery losses | 307 | 382 | 558 |

Installed = usable / 0.8 (Bob's own SoC-window assumption). Not included: winter, battery losses (VECTO adds 1.1-1.6 %), ageing.

## Findings
- Drag choice: +1.5 % (Regional, LongHaul) to +4.7 % (Urban) with constant efficiencies; +2-6 % with maps.
- Drivetrain loss model choice: constant 0.95/0.95/0.98 is 24-32 % below VECTO -> 80-130 kWh too small a battery at 360 km.
- E2 maps + VECTO E2 drag reproduce VECTO within 1 % on all three cycles.

## VECTO completed-bus generic method applied to the E2 truck (script `busgeneric.py`)

What the bus method makes generic [VECTO b8d6126]: motor efficiency map = normalized ASM/PSM map x rated point (`GenericBusElectricMotorData.cs` 171-192, 220-241; rated speed = end of constant-torque region, 20 % gradient rule, `ElectricMotorRatedSpeedHelper.cs` 20-53, `Constants.cs` 429 -> 2461.16 rpm / 485 Nm / 125 kW for E2); axle = 52.5 + 15*i, half fixed + half x n_out/150, + |T|/0.98 - |T| (`GenericTransmissionComponentData.cs` 66-165, `Constants.cs` 403-417).
What it still takes from the input: motor full-load curve, motor drag curve (line 54), motor type and count, ADC ratio (ADC loss 0.98 if ratio 1 else 0.96, line 43), gearbox data.
Drag table used: VECTO E2 table with the E2 axle part swapped for the bus axle [ASSUMPTION, Claude's method]: 1519 / 1650 / 1780 / 2108 / 2257 N at 45-85 km/h.

| Case | Urban | Regional | LongHaul |
|---|---|---|---|
| E2 maps + VECTO E2 drag | 0.831 (-1.0 %) | 1.048 (-0.2 %) | 1.530 (+0.3 %) |
| Bus method, E2 gearbox map (G1) | 0.917 (+9.2 %) | 1.080 (+2.8 %) | 1.577 (+3.4 %) |
| Bus method, EU std gearbox Tmax_in 1940 (G2) | 0.894 (+6.4 %) | 1.048 (-0.2 %) | 1.545 (+1.3 %) |
| EU std maps + VECTO E2 drag | 0.857 (+1.9 %) | 0.976 (-7.1 %) | 1.456 (-4.5 %) |

(% vs VECTO terminals.) The bus method lands at or above VECTO on every cycle; EU std maps fall 5-7 % below on Regional and LongHaul.

## Second example: VECTO test vehicle ADAS-PEV/Group5PCCEng (script `gp5.py`)

Source: `VectoCore/VectoCoreTest/TestData/Integration/ADAS-PEV/Group5PCCEng/` (commit b8d6126), engineering mode. Group-5 tractor + trailer: curb 8229 + trailer 7500 kg (`Class5_E2_NoADAS.vveh`), load 12,900 (Urban/Regional) / 19,300 kg (LongHaul) (`SegmentTable.csv` line 17), r_dyn 0.492 m, 5 axles. E2 version: 1 motor `Emo_325kW_2170Nm` (own map `generic_e_mot_325kW_2172Nm.vemo`, full load `generic_e_flc_325kW_2170Nm.vemp`, drag `GenericDrag.vemd`), ADC 2.0, 12-speed AMT with own loss maps, axle 2.64. E3 version: same motor on the axle, ADC 2.0. (The E4 version uses 2 x 125 kW wheel motors, so not comparable.)

Assumptions: CdxA 8.7 m2 flat (`SegmentTable.csv` CdxA_Default; the vveh has no CdA; no crosswind); aux 0 (same for all cases); gear = highest gear in which the motor can deliver the torque (22 Oct simple rule); driver power cap P_max = 311 kW at the wheels [CALC: 325 kW motor rated point x 0.957 through own gearbox 12 + axle maps]; ADC loss ignored; motor type of this example not stated (engineering file), so both generic ASM and PSM maps tested.
No VECTO result exists for this truck. Reference = its own component maps + own drag table (same method that matched VECTO within 1 % on E2; drag builder checked: reproduces E2 close-out 1.40/1.58/1.74/1.90/2.07 kN).
Limit: rows where the motor cannot deliver the torque at low speed (driver has only a power cap, no torque cap): E2 version 418/6059 (Urban), 130/3759 (Regional), 211/3609 (LongHaul); E3 version 2029/6080 on Urban -> E3 Urban not valid, others 225-266 rows. Read at the map edge; a few % uncertainty.

Drag tables [kN] at 0/20/45/55/65/75/85/100/130 km/h:
- G5 E2 own: 0.30 0.39 0.51 0.56 0.62 0.68 0.73 0.82 1.01 (about one third of the E2 group-2 truck's 1.4-2.1 kN)
- G5 E3 own: 0.18 0.26 0.37 0.42 0.46 0.51 0.56 0.63 0.78 (same motor, no gearbox: ~25 % below E2)
- EU std (E2 layout): 0.43 0.47 0.53 0.55 0.57 0.60 0.62 0.65 0.72
- bus method (E2 layout): 0.37 0.48 0.65 0.72 0.80 0.88 0.95 1.07 1.30

kWh/km (aux 0), % vs own maps + own drag:

| G5 E2 | Urban | Regional | LongHaul |
|---|---|---|---|
| own maps + own drag (reference) | 1.264 | 1.389 | 1.468 |
| constant 0.95/0.95/0.98, no drag | 1.165 (-7.8 %) | 1.344 (-3.3 %) | 1.527 (+4.0 %) |
| constant + own drag | 1.187 (-6.0 %) | 1.368 (-1.6 %) | 1.546 (+5.3 %) |
| constant + VECTO E2 drag table | 1.221 (-3.4 %) | 1.395 (+0.4 %) | 1.553 (+5.8 %) |
| own maps + VECTO E2 drag table | 1.391 (+10.1 %) | 1.447 (+4.2 %) | 1.563 (+6.5 %) |
| EU std maps + EU std drag | 1.556 (+23.2 %) | 1.477 (+6.3 %) | 1.550 (+5.6 %) |
| bus ASM + own gearbox | 1.577 (+24.8 %) | 1.485 (+6.9 %) | 1.529 (+4.2 %) |
| bus ASM + EU std gearbox | 1.804 (+42.8 %) | 1.550 (+11.5 %) | 1.573 (+7.2 %) |
| bus PSM + own gearbox | 1.274 (+0.8 %) | 1.462 (+5.2 %) | 1.557 (+6.1 %) |

| G5 E3 | Urban (not valid) | Regional | LongHaul |
|---|---|---|---|
| own maps + own drag (reference) | 1.211 | 1.404 | 1.584 |
| constant 0.95/0.95/0.98, no drag | 1.165 | 1.344 (-4.3 %) | 1.527 (-3.6 %) |
| constant + VECTO E2 drag table | 1.221 | 1.395 (-0.6 %) | 1.553 (-1.9 %) |
| own maps + VECTO E2 drag table | 1.256 | 1.441 (+2.7 %) | 1.603 (+1.2 %) |
| EU std maps + EU std drag | 1.436 | 1.457 (+3.8 %) | 1.625 (+2.6 %) |
| bus ASM + own gearbox | 1.718 | 1.548 (+10.3 %) | 1.703 (+7.5 %) |
| bus PSM + own gearbox | 1.250 | 1.489 (+6.1 %) | 1.685 (+6.4 %) |

Findings from the second example:
- Drag does not scale with truck size: this 35 t tractor (1 motor, direct top gear) drags ~1/3 of the 12 t E2 truck (2 motors, 2-speed). The VECTO E2 table overstates its drag (+2 to +10 % kWh/km).
- Same motor, E2 vs E3 layout: E3 drag ~25 % lower (one example; supports "more gear stages -> more drag").
- Constant 0.95/0.95/0.98: -8 to +5 % here vs -24 to -32 % on the group-2 E2 truck. Its error depends on the truck's own maps; not a fixed bias.
- EU std maps: +6 to +23 % here vs -7 % (Regional) on group-2 E2. Direction flips between trucks.
- Bus method: never below the reference on G5 E2; PSM map +1 to +6 %, ASM map up to +25 % (Urban). Motor type choice matters most.

## Third example: VECTO test vehicle 2nd_AmendmDeclMode/JSON/PEV/GenericVehicleB2_APTN (script `gp_b2.py`)

Source: `VectoCore/VectoCoreTest/TestData/Integration/DeclarationMode/2nd_AmendmDeclMode/JSON/PEV/GenericVehicleB2_APTN/` (commit b8d6126). Group-5 tractor: curb 10,143.4 + trailer 7,500 kg, CdA 4.31 m2, RRC 0.0034/0.004/0.0055, r_dyn 0.4922 m (`BEV_B2_Group5_LH_rl.vveh`); 2 motors `BEV_Group5_EM` 750 Nm each, rated 2069 rpm (VECTO rule), 325 kW total, own map `EM_Map.vemo`, drag `EM_drag.vemd`, motor-to-gearbox ratio 1.0; 3-speed APT-N 8.31 / 4.65 / 2.75 with `Gear_indirect.vtlm`; axle 2.64 `Axle_4x2_LH.vtlm`. Loads 12,900 / 19,300 kg (SegmentTable line 17).
Same assumptions as the second example (flat CdxA as in the file, aux 0, highest-feasible-gear rule, ADC loss ignored). Wheel cap P_max = 305.2 kW [CALC: 325 kW x 0.939 through own top gear + axle]. (A first run had a torque-direction error in this cap, giving 40 kW; discarded.)
Rows the motor cannot deliver (low-speed torque): 447/5748 Urban, 120/3392 Regional, 171/3109 LongHaul.

Drag tables [kN] at 0/20/45/55/65/75/85/100/130 km/h:
- own: 0.09 0.15 0.23 0.26 0.29 0.33 0.36 0.41 0.50
- EU std: 0.42 0.52 0.65 0.70 0.75 0.80 0.85 0.93 1.08
- bus (own gearbox): 0.19 0.28 0.43 0.49 0.55 0.61 0.67 0.77 0.95

| B2 APTN | Urban | Regional | LongHaul |
|---|---|---|---|
| own maps + own drag (reference) | 1.260 | 0.984 | 1.067 |
| constant 0.95/0.95/0.98, no drag | 0.987 (-21.7 %) | 0.927 (-5.8 %) | 1.026 (-3.9 %) |
| constant + own drag | 1.000 (-20.7 %) | 0.941 (-4.4 %) | 1.041 (-2.5 %) |
| constant + VECTO E2 drag table | 1.045 (-17.1 %) | 0.993 (+0.9 %) | 1.084 (+1.5 %) |
| own maps + VECTO E2 drag table | 1.295 (+2.8 %) | 1.034 (+5.1 %) | 1.116 (+4.5 %) |
| EU std maps + EU std drag | 1.868 (+48.2 %) | 1.282 (+30.2 %) | 1.334 (+25.0 %) |
| bus ASM + own gearbox | 1.792 (+42.2 %) | 1.172 (+19.1 %) | 1.204 (+12.8 %) |
| bus ASM + EU std gearbox | 1.944 (+54.3 %) | 1.334 (+35.5 %) | 1.372 (+28.5 %) |
| bus PSM + own gearbox | 1.450 (+15.0 %) | 1.145 (+16.3 %) | 1.228 (+15.1 %) |

## Across the three example trucks (Regional / LongHaul, % vs each truck's own data)

| Option | E2 group 2 (vs VECTO) | Group 5 PCC (E2 layout) | Group 5 B2 APTN |
|---|---|---|---|
| constant 0.95/0.95/0.98, no drag | -32 / -24 | -3 / +4 | -6 / -4 |
| constant + VECTO E2 drag table | -31 / -23 | 0 / +6 | +1 / +2 |
| own maps + VECTO E2 drag table | 0 / 0 | +4 / +7 | +5 / +5 |
| EU std maps + EU std drag | -8 / -5 | +6 / +6 | +30 / +25 |
| bus method, best motor type | +3 / +3 (ASM) | +5 / +6 (PSM) | +16 / +15 (PSM) |

Caveat: all three are VECTO example/test data sets, not certified or measured trucks. The comparison shows how much the fallbacks disagree with a truck's own component data, not with reality.
Key point: the drag table changes results by about +3 to +7 %; the choice of drivetrain loss model (constant, EU std, bus method, own maps) changes them by -32 to +48 %. No fallback stays within +/-10 % on all three trucks.

## Literature (hints only, none measures e-truck coasting drag directly)
- JRC, Bitsanis et al. 2023 (SAE 2023-01-0485): VECTO electric-mode energy within 2.5 % of measured (1.5 % with gear input).
- Yan et al. 2024, Lubricants 12(1):11: e-axle gearbox no-load losses > 80 % of total gearbox loss in their tests.
- Xu et al. 2024 (Chalmers, IEEE ESARS-ITEC): declutchable BEV powertrains to avoid electric-drive no-load losses while coasting (no numbers in abstract).
- Wolff et al. 2021 (TUM, Energies 14(2):328): powertrain topology changes BEV truck efficiency; single-machine beats multi-machine (no numbers in abstract).
