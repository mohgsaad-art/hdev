# Bob to fetch (pass 3)

Note on scope: the brief says list only links **not already** in
`manual-fetch-list-2026-11-06.md`. That file is **not in the repo** (nor are the
other named input files or the `inputs/`/`fetched/` folders), so I can't diff
against it. Everything below is what pass 3 found still missing; when you have
the manual-fetch-list, drop any row already there.

Columns match `catalogue.csv`:
`name | url | publisher | region | vehicle_classes | data_categories | why / what to get`

## Highest priority — unlocks the EEA battery data for the whole library

- **EEA HDV RP2024-25 relational dataset: `vehicle` + `memberstate_vehicle` header, READ_ME.txt, metadata XML** |
  https://www.eea.europa.eu/en/datahub (search "co2-emission-hdv reporting period 2024-2025") |
  EEA/DG-CLIMA | EU+UK+NO | N2/N3/M2/M3 | battery join |
  The `battery`, `electricmachine`, `iepc`, `voltagelevel_*` tables we have are
  **hashed** (Vehicle_id). The `vehicle` header holds both the hash and
  make/model/OEM/VehicleGroup. Fetch it so battery kWh / continuous kW can be
  attributed to a make/model. Also grab the READ_ME and metadata XML for the
  exact join keys and the per-table licence/confidentiality notes. (The EEA site
  returned 403 to the research sandbox; try from your network.)

## OEM technical data sheets (to replace cite-only secondary with [V])

- **ZF eWorX ePTO data sheet** | https://www.zf.com | ZF | EU | ePTO |
  Confirm whether 33/58 kW is electrical input or mechanical output (conflict 2).
- **MAN eTGX/eTGS/eTGL technical data sheet** | https://www.man.eu | MAN | EU/DE | N3 |
  Per-pack nominal voltage, Ah, mass, gears, MCS rating; confirm NMC in-document.
- **Mercedes eActros 600 technical data sheet** | https://eactros600.mercedes-benz-trucks.com |
  Daimler Truck | EU | N3 | battery/drivetrain | nominal voltage, usable kWh, pack mass.
- **Volvo 2026 Aero/FM/FH electric-range fact sheet** | https://stpi.it.volvo.com/STPIFiles/Volvo/FactSheet/ |
  Volvo | EU | N3 | battery | per-pack installed vs UBE for the 2026 generation
  (confirm the 460 kWh usable — conflict 12).
- **DAF XD/XF Electric torque line** | DAF BBI 202625 revision PDF | DAF | EU | N3 |
  OCR the motor-torque cell; check for 60/100 kW ePTO (conflict 3 & 4).
- **Scania BEV body-builder portal (EL PTO / EM PTO kW, 250 A supply)** |
  https://bodybuilder.scania.com | Scania | EU | N2/N3 | ePTO | the kW values.
- **Renault E-Tech D/T/C; IVECO S-eWay + eDaily; Fuso eCanter; Ford E-Transit** |
  OEM sites | EU | N1/N2/N3 | battery/drivetrain/masses.
- **Buses: Mercedes eCitaro; MAN Lion's City E; Volvo BZL/7900E; Yutong; BYD; Irizar; Heuliez; VDL; IVECO Bus** |
  OEM sites | EU/CN | M3 | battery/HVAC/range.
- **Vans: VW ID.Buzz Cargo; Merc eVito/eSprinter; Renault Kangoo/Master E-Tech; Stellantis e-vans; Toyota Proace Electric** |
  OEM sites | EU | N1 | usable kWh, Wh/km, range, payload.

## Body-equipment makers (ePTO / body energy — the biggest gap)

- **Refuse bodies: Geesinknorba, FAUN, Zoeller, Joab, Norba; Dennis Eagle eCollect** |
  OEM sites | EU | refuse body | compactor + lift electrical input kW, energy per cycle.
- **Cranes: HIAB eHiPro, Palfinger** | OEM | EU | crane | electrical input kW.
- **Reefers: Carrier Vector HE19 / 1550E City / R eCool; Thermo King Advancer; Schmitz S.KOe COOL** |
  OEM | EU | reefer | **cooling capacity (W) and COP** (we have the 19 kW electrical
  input; cooling capacity is a separate, missing figure).
- **Sweepers/road: Bucher, Aebi Schmidt, Boschung** | OEM | EU | body | electrical input.

## Measured consumption with conditions (region reports)

- **Sweden: RISE / Chalmers measured e-truck; klimatpremie dataset** | SE | N3 | measured kWh/km.
- **Germany: KBA per-type data; Fraunhofer ISI/IML; ADAC Ecotest e-vans; KsNI Table 2-5; Oeko ELV-Live 1&2; NOW bus heating; ZEHID 2026** | DE | N1/N3/M3 | measured + aux/HVAC.
- **UK: Cenex, VCA, Logistics UK, eFREIGHT 2030** | UK | N3 | measured.
- **US (physics only): Argonne Autonomie; OSTI 2311852 (get licence); CARB HVIP spec sheets** | US | N2/N3.
- **Norway: Enova e-truck; TOI; NAF/Motor El Prix (incl vans); Statens vegvesen schema** | NO | N1/N3 | measured + registry fields.
- **Denmark: DTU; Energistyrelsen; ARC/Aarhus/Frederiksberg e-refuse pilots; FDM e-van tests; Mobility Denmark / Dansk Elbil Alliance; DMR FTP extract fields** | DK | N3/N1 |
  measured e-refuse + vans; **and the 2.25 kWh/km Frederiksberg figure's origin (conflict 8)**.
- **ICCT ID-359 full report PDF** | https://theicct.org/wp-content/uploads/2025/08/ID-359-%E2%80%93-EU-goods-transport_report_final.pdf |
  ICCT | EU | N3 | read the correct-unit consumption tables (conflict 9).
- **TNO R10409; CEC-600-2024-010; Renodjurs Bilag 9** | mixed | N3.

## Registries, EU data, aggregators

- **RDW `Gekentekende_voertuigen_brandstof`** | https://opendata.rdw.nl | RDW | NL |
  N1/N2/N3/M3 | confirm dataset ID + columns (nominal continuous power, EV
  range/consumption kWh/km), CC0 licence, and counts of electric N2/N3/M3.
- **EAFO model lists** | https://alternative-fuels-observatory.ec.europa.eu | EU | all | model lists/export.
- **Battery Regulation 2023/1542 passport fields** | EUR-Lex | EU | all |
  which passport fields are public and from when (data carrier from 2027).
- **EPREL API for C3 tyres** | https://eprel.ec.europa.eu | EU | tyres |
  request API key; check whether the **rolling-resistance coefficient** (not just
  label class) is exposed, and C3 coverage.
- **EEA OBFCM 2024 real-world BEV dataset (record 13e6fad9-149c-4b86-9d83-cdf3569ccfee)** |
  https://www.eea.europa.eu/en/datahub | EEA | EU | M1/N1 | which BEV energy columns it holds.
- **ZETI; Chargepoly; EV Database API (price/terms — do NOT scrape); Open EV Data (licence file); Nature Sci Data 2025 EV dataset (licence)** |
  mixed | global | fields/licence only.
