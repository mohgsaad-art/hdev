# EEA HDV data: what it holds for electric trucks (6 Nov 2026)

Checked by Claude on files Bob produced in Colab. Facts from the data are marked [DATA]; inferences [INFERENCE].

## Files
1. **EEA 2019–2023 extract**: `HDV_CO2Emission_VehicleExtract_24042025.zip` from https://discomap.eea.europa.eu/App/CO2HDV/ (record 22fd286c-9737-4b38-b2bb-1f7a7d3e9916, CC-BY 4.0). Zip is 440 MB, Deflate64 (use `!unzip`, not Python zipfile). CSV 3.8 GB, 461 columns, 3,627,357 rows, one row per registered vehicle.
2. **Bob's file** (Google Drive, source not yet confirmed; licence unknown): 1.9 GB, 139 columns, manufacturer VECTO input records only, no mission results. Simulation dates 2021–2025, VECTO 3.3.9–4.3.3.

## EEA 2019–2023: electric trucks [DATA]
- Filter OEM_ZeroEmissionVehicle=Yes or MS_Electric=Yes gave 44,107 rows. 40,808 have no OEM record, and those include cars and vans (M1 14,538, N1 8,225; Audi, Tesla, BMW). Electric N2/N3 trucks with country data only: about 5,200.
- 3,221 OEM ZEV rows: every drivetrain field is a placeholder: gears 0, axle ratio 0, CdxA "A1", engine power 0. No aux, tyres or mission results. All were run with VECTO 3.3.x.
- [INFERENCE] The ZEVs were reported before VECTO could simulate them, so dummy values were used.
- The 70 rows that have mission results are diesel trucks wrongly flagged MS_Electric.
- **Use for HDEV:** counts of electric trucks by make, model, group and country only. No specs.

## Bob's file: electric vehicles [DATA]
- 18,731 ZEVs in 6,135 unique configs: 10,596 trucks (N2/N3) in 5,548 configs, plus 8,132 buses (M3).
- Trucks with PEVArchitecture filled: 46 % (E-IEPC 3,851; E2 553; E3 504). The other 5,688 have no architecture and axle ratio 0 (same placeholder pattern).
- Real axle ratio: all E2 and E3 trucks, and 2,431 of 3,851 IEPC trucks.
- Gear count: only the E2 trucks (2 gears, AMT): Renault LD 42RELAIR and Volvo FL 42 R E 16, axle 4.50 (some 3.90–5.14).
- Examples (configs × count):
  - Renault LD 42RELAIR, grp 4, E2, 4.50, A15 ×257
  - IVECO Daily NDE MY2021, grp 53, E3, 4.30 ×245
  - Renault ZM42T_MED, grp 5, IEPC, 2.64 ×170
  - Volvo FM/FH E, grp 4/5/9, IEPC, 2.64–3.08, A12–A23
  - MAN TGX 18.449 EB, grp 5, IEPC, 2.31–2.53
  - Scania R 400E, grp 9, IEPC, 4.25
- CdxA range codes (A1–A24) are real for about 46 % of trucks. [OPEN] Code→m² lookup not found yet.
- Aux_Pneumatic_Technology is filled (e.g. "Large Supply + AMS + elec. driven", "electrically").
- No cooling fan values (expected for BEV) and no steering pump column.
- OffVehicleChargingMaxPower is 0 % filled. SumNetPower is 3.7 % filled (360 / 350 / 0).
- **No battery capacity, no e-motor data, no loss maps, no kWh in either file.**

## Use for HDEV [INFERENCE]
- Sourced typical values per class:
  - BEV architecture share per group (IEPC dominant)
  - axle ratio per model
  - E2 2-speed + 4.50 for group 4
  - CdxA range per model (once the lookup is found)
  - pneumatic technology for electric trucks
- Repeat counts work as weights (how common each config is).
- Still needed elsewhere: battery, motor, efficiency, consumption.

## Open
- Confirm where Bob's file came from and its licence.
- CdxA range code → m² table.
- Newer EEA release (2023–2024, record c52f7b51-…) not yet checked.
