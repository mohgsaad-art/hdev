# EEA RP 2024–25 join: what is usable for trucks (7 Nov 2026)

From Bob's Colab join (`docs/research/eea-hdv-2024-peeks/join_xev_tables.py`), analysed by Claude on
`docs/research/eea-hdv-2024-join/vehicles_xev.csv` and `missions_xev.csv`. Hybrids ignored (Bob's decision).

## ZEV split
- 18,847 ZEV-flag vehicles: N3 9,720, M3 8,248, N2 876.
- Trucks (N2/N3) WITHOUT battery record: 5,993. 4,988 of them were simulated with VECTO 3.3.x (before ZEV certification under 2022/1379); they carry placeholders (gears 0, axle ratio 0.00) and only 306 have kWh/km. → Dropped. Values of 0 are placeholders, not data.
- Trucks WITH battery record: 4,603. All have curb mass, TPMLM, axle config, PEV architecture, CdxA bin, battery, motor/IEPC, pneumatic tech, and mission kWh/km.
- Axle ratio is "missing" for 1,420 of the 4,603, all E-IEPC:
  - 1,065 have IEPC `DesignTypeWheelMotor = true` (e.g. Mercedes "Actros"/"Econic") → no separate axle gear; total ratio sits in the IEPC (e.g. 407 kW, 2 gears, ratio 15.046; 601 kW, 4 gears, 10.572). Not a gap.
  - 355 (Fuso Canter 132 kW 1-gear ratio 19.528; IVECO S-eWay 851 kW 1-gear 25.101) are not wheel-motor designs. [INFERENCE] `DifferentialIncluded` may be true; not checked (flag not kept in the first join output; the script now keeps it as `diff=` in `iepc_desc`).
- Buses: primary records (no ClassBus) 2,270 have battery; completed buses (ClassBus set) 3,789 have no battery but 2,407 have kWh/km. Consistent with staged bus certification (components on the primary record). No link primary↔completed found in the joined columns. Buses parked for now.

## Certified kWh/km: battery side or grid side? (Claude check)
- For 44,360 truck mission rows: `ElectricEnergy_kwh_km × ActualChargeDepletingRange / bat_usable_sim_kwh` has median 1.005 (1st–99th percentile 0.992–1.017).
- So range = usable simulation kWh / reported kWh/km, consistently. [INFERENCE] This points to kWh/km being the energy drawn from the battery (no charging losses), but it does not prove it: VECTO could compute range from the same number whichever side it is on. Must be confirmed in VECTO code.

## Duplicates / gap filling (decided with Bob, 7 Nov)
- 4,603 truck vehicles = 2,658 distinct exact configs incl. curb mass = 835 excl. curb mass.
- One Make+Model name covers many variants, e.g. Mercedes "Actros": 6 battery setups, 5 motor setups, 8 CdxA bins, curb mass 7,882–13,802 kg; Volvo "FM 62R TE": 6 batteries, 6 axle ratios, 10 motor setups.
- Naming: eActros appears as Make "Mercedes Benz", Model "Actros".

Rules (Bob agreed):
1. Collapse only exact duplicates of the full config key. Library = one row per config with curb mass as a min/max range. Validation = per vehicle at its own mass. Mass is not collapsed.
2. Never fill a field from a row that differs in any other key field.
3. Completeness is architecture-aware: axle ratio required for E2/E3; for E-IEPC the IEPC ratio (+ axle ratio only if the IEPC excludes the axle/differential). Zeros count as missing.
4. Hybrids are ignored.
