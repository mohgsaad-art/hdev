# HDEV vs EEA-certified VECTO vs OEM — 2 real trucks (Claude, 7 Nov 2026)

Scripts: `run_compare.py`, `sens.py`, `plot.py`; notebook module `nbmod.py` (built from `HDEV_NEW_code_of_record_2026-11-07.ipynb`, fixes 1–2 only, g = 9.80665 passed). Data: `results.csv`. Graphs: `hdev_vs_eea_abs.png`, `hdev_vs_eea_pct.png`.

## Trucks
- **Fuso eCanter, EEA C0059** (group 1, 8.55 t). IEPC 1 gear, ratio 19.528, diff included, **standard-value IEPC**, **standard-value air drag** → CdxA = SegmentTable default 7.1 m² exactly. OEM (fuso-trucks.com): 430 Nm / 129 kW peak, PSM, max 15,000 rpm; L pack 123.9 kWh, 94 % usable, up to 200 km (50 % payload, box body, 20 °C).
- **IVECO S-eWay tractor, EEA C0091** (group 5). IEPC 1 gear, ratio 25.101, diff included, **measured IEPC**, **measured CdxA (bin A14, value unknown)** → standard 8.7 m² used. OEM (iveco.com, 15 Nov 2023): 9 × 82 = 738 kWh, 480 kW continuous, 1,800 Nm, "up to 500 km", no conditions.

## HDEV % vs certified (battery-terminal HDEV vs grid-side certified)
| | V-A constant | V-B EU std values | V-C bus-generic | V-D E2 as-is |
|---|---|---|---|---|
| Canter Regional | −33 / −34 | −2.2 / −2.5 | −5.6 / −5.9 | −3.2 / −3.6 |
| Canter Urban | −30 / −31 | +2.8 / +3.3 | −2.2 / −3.1 | +8.3 / +8.4 |
| S-eWay Long Haul | +15 / +16 | +86…+126 | +41…+92 | +32…+40 (out of map) |
| S-eWay Regional | +14 / +15 | +88…+120 | +43…+86 | +32…+38 (out of map) |
| S-eWay Urban | +3 / +4 | +67…+83 | +48…+61 | 0…+21 (out of map) |

## Findings
1. **Canter V-B within ±3.3 %** on all 4 runs. The Canter was certified with the same standard-value IEPC method, so this is an end-to-end check of HDEV's driver, forces, tyres, aux and crosswind against VECTO on a real certified truck.
2. **V-A (today's constant efficiency) is −30 to −34 % on the Canter.** That matches the 3 Nov E2 finding (−24 to −32 %).
3. **S-eWay: V-B and V-C overshoot by +38 to +126 %**, whatever rated speed is used (3,000–10,000 rpm swept). The standard maps are built to be conservative; this truck was certified with a measured map.
4. **S-eWay V-A moves about 6–7 % per 1 m² of CdxA.** It would match the certified figure at CdxA ≈ 6.7–6.9 m², but the measured value isn't published. Not a result.
5. V-D is out of map on the S-eWay (E2 motors 2 × 125 kW against an 851 kW truck), so it's unusable there.
6. **OEM figures:** Canter 0.58 kWh/km (derived, battery side) is 20–24 % below certified Urban and 52–53 % below Regional. S-eWay 1.48 kWh/km is on an installed-kWh basis, so it's only an upper bound.
7. No method stays within ±10 % on both trucks.

## Assumptions (all flagged in code)
- Truck tyre test load FzISO is not in EEA → wheel load assumed equal to test load (base^(β−1) = 1). The trailer uses VECTO's 37,500 N.
- Rated speed = R85 rated power / OEM max torque (VECTO's corner-point rule for a constant-torque / constant-power curve).
- V-B: ratio split between gearbox and differential is unknown → √i each. Sensitivity ±1 %.
- V-C IEPC: declared output full-load torque assumed = motor T_max × ratio (no loss). V-C drag uses the V-B drag table, since VECTO uses the declared drag curve, which EEA doesn't have.
- HVAC config is blank in EEA → HVAC "Default" row. ES = "Standard technology".
- S-eWay motor type is not published → PSM and ASM both run (range shown).
- S-eWay "1,800 Nm" read as motor-side total ([INF]: × 25.1 ≈ 45,000 Nm wheel torque on the newer brochure).
- HDEV has no battery-loss model. The certified figure includes REESS internal losses and charging losses (EEA ratio 1.016 Canter, 1.000 S-eWay).

## Notebook issues found (for Bob)
- `driver_model` / `coast_distance` use rolling force = Crr·m·g (linear), but `consumption_engine` uses Crr·g·m^β. One Crr can't satisfy both. Here: driver got VECTO's total RRC, consumption got RRC·m^(1−β).
- `P_max` is applied only when coasting is on (`if P_max is not None and coast_on`).
- `consumption_engine` applies SP only while moving, and cond only while moving or with PTO active. VECTO treats SP as constant and cond as dynamic.

## Fallback scorecard (added same day; `ext.py`, `results_ext.csv`)
Added the S-eWay EMS missions (28–51 t, ST1 + T2, RigidTrailer crosswind, dCdA +1.5) and V-E = VECTO GenericIEPC `IEPC_Gbx1Speed+Axle` example map as-is (250 kW PSM, 12.276).
Error vs reference, min..max. Certified trucks are compared with the EEA figure; 3 Nov example trucks with their own maps (E2 with VECTO), Regional/LongHaul unless noted.

| Fallback | Canter (cert., std IEPC) | S-eWay (cert., measured, 22–51 t) | E2 12 t (3 Nov) | G5 PCC tractor (3 Nov) | G5 B2 APTN tractor (3 Nov) |
|---|---|---|---|---|---|
| V-A constant 0.95/0.95/0.98 | −34..−30 | +3..+16 (CdxA std 8.7) | −32..−24 | −8..+4 | −22..−4 |
| V-B EU std values | −3..+3 | +67..+126 | −8..0 | +6..+23 | +25..+48 |
| V-C bus-generic, best type | −6..−2 | +36..+44 (ASM; PSM +60..+92) | +3..+9 | +1..+6 | +15..+16 |
| V-D E2 example as-is | −4..+8 | out of map (unusable) | own | — | — |
| V-E generic IEPC example as-is | −12..−9 | +17..+32, out of map | — | — | — |

No fallback is within ±10 % on all trucks. V-C is the only one never more than 6 % below the reference (conservative), at up to +44 % (+92 % with the wrong motor type) on an efficient measured heavy truck. V-B is best when EEA says the component was certified with standard values.

## Calibration to EEA certified values (calib.py, calib2.py, calib3.py)
- One constant efficiency fitted on one mission: Canter Urban +27..+34 %, S-eWay Urban −19..−22 % → fails.
- Efficiency + fixed loss: unphysical fit (negative fixed loss / eta = 1.0), errors up to 13 % → fails.
- **Bus-method map shape + 2 fitted parameters (loss scale on the map, CdxA), fitted on Regional + Urban at one payload:**
  Canter worst 0.4 % on the other runs; S-eWay ASM map worst 6.1 % (Long Haul low payload), PSM map ~5 % (CdxA hit 5.0 m² bound).
  Fitted CdxA is an effective value, not the real one (Canter fit 8.25 m² vs known 7.1 m²).
- Only 2 trucks, VECTO cycles only. Proposal (Bob to decide): library trucks → fit these 2 parameters to their EEA certified missions; non-library trucks → uncalibrated bus method with a stated error band.

## Leave-one-out calibration on 10 EEA-certified trucks (robust.py, final.py, calibration_kwh_km.csv)
Fit on all other certified runs of the same vehicle, predict the one left out. Worst error per truck:
| Truck | A today | B 1 eff + drag | C drive/regen eff + drag | D bus map (1-gear) |
|---|---|---|---|---|
| Fuso eCanter 7 t | 34.3 | 13.3 | 11.6 | 1.5 |
| IVECO S-eWay tractor | 16.4 | 3.5 | 2.3 | 2.1 |
| Scania R 400E tractor 6-gear | 25.9 | 5.6 | 5.5 | – |
| MAN eTGX tractor 4-gear | 29.1 | 8.9 | 7.9 | – |
| Mercedes eActros 600 4-gear | 37.8 | 11.1 | 8.3 | – |
| Renault D rigid 2-speed | 24.9 | 6.9 | 4.6 | – |
| Volvo FM 6x2 12-gear | 3.1 | 1.5 | 1.9 | – |
| Mercedes Econic 6x2 refuse | 6.0 | 1.2 | 0.9 | – |
| IVECO eDaily van E3 | 14.5 | 2.0 | 0.7 | – |
| DAF XB 6x2 3-gear | 4.4 | 3.3 | 2.6 | – |
Misses above 5 % for C are Urban at low payload (and Canter). DAF has only 4 runs for 4 parameters (weak test).
