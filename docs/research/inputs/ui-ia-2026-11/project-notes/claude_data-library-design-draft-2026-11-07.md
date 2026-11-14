# Vehicle data library: what it is for, what EEA RP 2024–25 gives, provenance (draft, 7 Nov 2026)

Draft for discussion with Bob. Not decided. Based on peeks of 10 rows per table (`docs/research/eea-hdv-2024-peeks/`); no completeness numbers per make/model until the join is run.

## Why the library (Bob's reasons + Claude's additions)
- Bob: sizing works on generic/standard values; the library answers "which vehicle do I buy?" by simulating a specific model on the user's route; charger sizing must respect the vehicle's max charging power (CCS/MCS); exact axle/aux config for a specific-vehicle check; installed vs usable kWh for year-8 degradation and TCO.
- Claude [INFERENCE, ideas not decisions]: compare tender bids on the same route; payload and legal weight check per model (TPMLM, curb mass, Danish limits); validate HDEV against each model's certified VECTO kWh/km (missionprofile); market counts by country/model (memberstate_vehicle); toll/CO2-class inputs (vehicle group, ZEV flag).

## Provenance classes (every library field carries one)
1. **Certified component, measured** — EEA `CertificationMethod = Measured`: OEM tested the component, approval authority certified it, OEM reported it. [INFERENCE: strong; EEA READ_ME/metadata XML for RP 2024–25 not yet read.]
2. **Certified component, standard values** — `StandardValues`: OEM chose the generic Annex Xb values instead of testing. Real model name, but the component behaviour is generic. Which fields stay OEM-declared under standard values (e.g. rated power) must be checked in Annex Xb (project KB `12h-annex-xb-...`).
3. **VECTO simulation result** — e.g. `TotalUsableCapacityInSimulation`, missionprofile kWh/km and ranges: OEM ran VECTO on standard cycles/payloads. Certified simulation, not real-world.
4. **Registry** — `memberstate_vehicle`: what was registered where and when.
5. **OEM spec sheet / web page** — marketing claim; not certified; may mix gross/usable; generation-specific; copyrighted (store value + citation only).
6. **Trade press / aggregator** — lead only.
7. **Derived** — our arithmetic, shown.

## What EEA RP 2024–25 offers per table (from peeks)
| Table | Useful fields | Class | Notes |
|---|---|---|---|
| vehicle (2 GB, ~1.77 M rows) | make, model, category, group, axle config, curb mass, TPMLM, ZEV/HEV flags, PEVArchitecture, axle type/ratio, gears, CdxA bin, PTO flag, aux tech labels (pneumatic, HVAC config, fan), OffVehicleChargingMaxPower | 1/2 (cert. inputs) | Units/flags inconsistent; charging power empty in configs file |
| battery (35,021 pack rows, 8,020 vehicles) | installed kWh, VECTO usable kWh, nominal V, cert method | 1/2 + 3 (usable) | 846 vehicles 1 kWh/49 V, likely hybrids [INFERENCE] |
| electricmachine (4,157 rows) | type (PSM/ASM/ESM), position, count, rated kW, cert method | 1/2 | No peak, no torque |
| voltagelevel_electricmachine / _iepc | max continuous kW per voltage level | 1/2 | Voltage often blank; many duplicates |
| iepc (4,662 rows) | rated kW, gears, lowest total ratio, wheel-motor flag, differential flag, cert method | 1/2 | First rows share Vehicle_id with battery rows → join works for those |
| capacitor (489 rows) | capacitance F, min/max V (26–59 V) | 1/2 | Supercaps, likely hybrids [INFERENCE] |
| missionprofile (9.5 GB, ~15.9 M rows) | per mission+payload: kWh/km, kWh/t·km, actual charge-depleting range, equivalent all-electric range, zero-CO2 range, total mass, payload, avg speed | 3 | Sample rows are diesel; ZEV rows not yet checked |
| memberstate_vehicle (541 MB, ~2.6 M rows) | country, registration date, Electric/Hybrid, axles, TPMLM, WMI | 4 | Join on `vehicle_id` |
| steeringpumptechnology | tech label per steered axle | 1/2 | Map to VECTO SP table for W |
| enginetorquelimit | diesel torque limit % per gear | — | Not for BEV |
| transfer, derogation | OEM pooling/derogation | — | Not for library |

## Not in EEA (needs OEM sheets or nothing public)
Max DC/AC/MCS charging power and connector (EEA field empty in configs), charging curve, OEM usable kWh, chemistry, battery mass, warranty/SoH terms, peak power/torque, motor maps (not public), ePTO kW, tyre data (axle table not peeked).

## Next step
Colab join on Vehicle_id: vehicle (selected columns) ↔ battery ↔ electricmachine ↔ iepc ↔ voltagelevel ↔ missionprofile (ZEV rows only) → one small CSV per vehicle configuration; then completeness per field and per make/model.
