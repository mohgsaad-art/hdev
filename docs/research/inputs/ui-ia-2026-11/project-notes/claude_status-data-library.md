# HDEV data library: living status and decisions

Read this first for anything about the OEM/official data library, the EEA HDV data or the charger/tariff library. Update this file each session; don't write new closeouts.

Started 9 Nov 2026. It merges and replaces:
- `status-data-library-combined-2026-11-07.md`;
- the 6 Nov data-library closeout;
- the 7 Nov EEA-library closeout.

Originals are in the GitHub archive (batch 2). The validation results that came out of the library (HDEV vs EEA certified, calibration) are in `session-closeout-2026-11-07-validation-fallbacks-calibration.md` and in `status-engine.md` §4.

Kept as separate reference docs:
- `data-library-design-draft-2026-11-07.md` (schema draft);
- `findings-eea-2024-join-trucks-2026-11-07.md`;
- `findings-eea-hdv-zev-data-2026-11-06.md`;
- `manual-fetch-list-2026-11-06.md` (~90 links);
- `files-to-fetch-2026-11-02.md`.

Rules: Kiro output can be wrong, so spot-check it. **CHECKED** means Claude re-checked it from the files. **[INFERENCE]** means not verified.

---

## 1. Goal and decisions

**Goal:** a library of OEM and official technical data for BEV trucks (later buses, vans, cars), with Denmark/EU focus. EV Scope is commercial, so every source's licence matters.

**Why (Bob):**
- Pick a specific vehicle for a route.
- Check the vehicle's charging power against the charger (MCS etc.).
- Use the exact axle/aux config for a specific-vehicle check.
- Know installed vs usable capacity, for year-8 degradation and TCO.

**Claude's extra ideas (not decided):** tender bid comparison, payload/legal weight check, per-model validation, market counts, toll/CO₂ class.

**Decisions (Bob, 7 Nov):**
- One row per exact config. Curb mass is kept as a min/max range. Validation runs per vehicle at its own mass.
- Collapse only exact duplicates. Never fill a field from a row that differs in any other key field.
- Zeros = missing.
- Completeness is architecture-aware: axle ratio for E2/E3, IEPC ratio for E-IEPC.
- Ignore hybrids. Buses are out of scope for now.
- Every value carries a provenance class: certified measured / certified standard values / VECTO simulated / registry / OEM claim / trade press / derived.
- Keep **installed vs VECTO-usable vs OEM-usable kWh** as three separate fields.

---

## 2. EEA HDV CO₂ data

### 2019–2023 release (flat CSV, CC-BY 4.0)
- 3.8 GB, 461 columns, 3,627,357 rows.
- The ZEV rows are placeholders: no kWh, battery, e-motor or HVAC kW.
- 44,107 rows are electric-flagged; only 3,221 have OEM ZEV records.
- 82 rows are OEM "Diesel CI" but MS_Electric = Yes.
- Download: `https://discomap.eea.europa.eu/App/CO2HDV/HDV_CO2Emission_VehicleExtract_24042025.zip`. It is Deflate64, so use `!unzip`.

### RP 2024–25 relational tables (record `1e44df1d-6a56-41e4-9d67-aeae0ab909c9`, CC-BY 4.0 per EEA catalogue)

All tables are keyed by `Vehicle_id` (a 0x… hash). Don't join on `Pk_Vehicle`.

- **`vehicle`** (2 GB, ~1.77 M rows, 139 cols): this is Bob's 139-column Drive file.
  - Columns: make, model, category, group, curb mass, TPMLM, ZEV/HEV flags, PEVArchitecture, axle type/ratio, gears, CdxA bin (A1–A24), PTO flag, aux technology labels, OffVehicleChargingMaxPower.
  - Quirks: TPMLM mixes kg and t; flags mix true/false and 1/0; "NULL" text.
- **`battery`**: one row per pack. Installed kWh, `TotalUsableCapacityInSimulation`, nominal V, cert method. Min/max V and capacitance are empty.
- **`electricmachine`**: type, position, count, rated kW, cert method.
- **`iepc`**: rated kW, gears, lowest total ratio, `DifferentialIncluded`, `DesignTypeWheelMotor`.
- **`voltagelevel_*`**: max continuous kW only. **No peak power, torque or maps anywhere.**
- **`axle`**: per axle `TyreDimension`, certified `SpecificRRC`, `Twintyres`.
- **`missionprofile`** (9.5 GB): per vehicle × mission × payload. `ElectricEnergy_kwh_km`, ranges, `TotalVehicleMass`, payload, average speed.
- **`memberstate_vehicle`**: registrations per country and date.
- **Not for the library:**
  - `enginetorquelimit` (diesel torque limit %);
  - `steeringpumptechnology` (label only);
  - `capacitor` (likely hybrids);
  - `transfer`;
  - `derogation`.

**Join results (Bob's Colab, 7 Nov):**
- 22,445 vehicles kept; 0 component records failed to join.
- Flags: ZEV 18,847, HEV 1,727, "other" 1,871.
- **Trucks with a battery record: 4,603. This is the usable set.**
  - 2,658 exact configs incl. curb mass; 835 excl. curb mass.
  - One model name covers many variants (e.g. Actros: 6 batteries, 5 motor setups, 8 CdxA bins, 7.9–13.8 t).
- Trucks without a battery record (5,993) are VECTO 3.3.x placeholders. Dropped.
- Axle ratio is "missing" on 1,420 E-IEPC trucks:
  - 1,065 are wheel-motor IEPC (ratio inside the IEPC);
  - 355 are Fuso Canter / IVECO S-eWay with `DifferentialIncluded = true`.
- `OffVehicleChargingMaxPower` is 0 % filled, so charging power must come from OEM sheets.
- Make strings need cleaning ("Mercedes Benz"/"Mercedes-Benz", "##VEHICLE_MAKE##", 4.1 % empty).
- 846 vehicles have a single 1 kWh / 49 V battery [INFERENCE: hybrids]. Exclude them.
- Usable/installed per pack ≈ 0.855.
  - **CHECKED** by Kiro v2: VECTO MaxSOC 92.75 % − MinSOC 7.25 % (`BatteryDataAdapter.cs` 62–67).
  - This is VECTO's simulation value, not OEM usable. Volvo ESS sheet: 6 × 90 = 540 installed → 380 usable.
- kWh/km × range / usable_sim = 1.005 median. [INFERENCE] the certified kWh/km is battery-side.
- Buses:
  - primary records have a battery;
  - completed buses have kWh/km but no battery.
  - The link between them was not found. Parked.

**Repo files** (`mohgsaad-art/hdev`, `main`):
- `docs/research/eea-hdv-2024-peeks/` (headers and samples, `peek_drive_csv.py`);
- `docs/research/eea-hdv-2024-join/` (`vehicles_xev.csv`, `missions_xev.csv`, `join_report.txt`; the configs files predate the 7 Nov rules, so don't use them as the test set);
- `join_xev_tables.py`, `extract_axle_steering_xev.py`.

**Bob's older CSV checks (CHECKED):**
- `hdv_2024_battery`: 35,021 pack rows, all kWh, 31,611 standard / 3,410 measured.
- `voltagelevel_electricmachine`: 2,538 exact duplicate rows.
- `voltagelevel_iepc`: 7,090 duplicates; most common 440 kW.
- `my_zev_configs`: 18,731 registrations / 6,135 configs, derived from the 139-column file.

---

## 3. Weights and legal (Denmark/EU)

- **BEK 1447/2025** (in force 1 Jan 2026): two-axle lorry 20,000 kg; three-axle twin-tyre 28,000 kg; no ZEV line.
- **Previous BEK 1415/2023:** 18 t / 26 t, each + up to 2 t ZEV.
- 58 t (7+ axles) and 4.20 m from 1 Jan 2027.
- Read from PDF text; **verify on retsinformation.dk.** Whether the old ZEV +2 t still stacks is **unresolved**.
- **EU W&D revision 2023/0265(COD):** not adopted (trilogues since Dec 2025). EP wants +4 t ZEV; **not law.**
- Directive 96/53/EC applies. ZEV allowance (Reg. 2019/1242 Art. 20) is the actual extra ZEV-tech weight, up to 2 t. EUR-Lex Art. 10b not yet read.
- COM(2025)589 is a tolling amendment, not weights & dimensions.
- Modulvogntog (60 t) order not found.
- Engine decision: the payload cap uses the registered GVW. Legal limits are only a later warning (`status-engine.md` §2.2).

---

## 4. OEM / press values collected (tag before use; none are certified)

- **Volvo FM Electric** (global page, 2026, OEM): 360–540 kWh (4–6 packs), usable up to 460; CCS 350 kW; 300–540 kW; 2 EM + 8-speed; ePTO 30/60/90 kW; up to 470 km.
- **Volvo PCE4:** 540 installed → 380 usable (Volvo sheet, in repo).
- **Frederiksberg PVI e-refuse** (trade press 2013, one pilot): 255 kWh, 26 t, 0.9 kWh/km road, 1.7 kWh/km collection.
- **Scania/Unicon/Liebherr mixer** (trade press 2026): 400 kWh, ePTO drum, ~200 km.
- **Fuso eCanter, IVECO S-eWay:** see the 11-07 calibration closeout §4.
- **Web/press only [C]:** DAF torque 1,500/2,400 Nm; MAN NMC 534/480 kWh; eActros 600 data; Volvo "460 = 2026 Aero".
- **Gemini claims judged false or unsourced (do not use):**
  - Volvo ePTO 100/150 kW;
  - ePTO efficiency 0.82–0.88;
  - fixed transmission drag 1.5–2.5 %;
  - ISO 24162 covering cranes (it covers refuse bodies only);
  - a free DMR REST API;
  - TNO CC-BY CSVs;
  - "58 t from 2026".

**No public source yet for:** motor loss maps, charging curves, per-component aux kW, ePTO efficiency, energy per refuse lift.

---

## 5. Other datasets and licences

| Source | Licence | Notes |
|---|---|---|
| EEA HDV | CC-BY 4.0 | |
| RDW (`m9d7-ebf2`) | CC0 | masses, payload, aero devices |
| Traficom | CC BY 4.0 | |
| NREL Fleet DNA | CC BY 4.0 | |
| dt-cargo | ODbL | 53 trucks; see the tools review |
| VECTO code | EUPL 1.2 (copyleft) | |
| Transportstyrelsen | paid | |
| Statens vegvesen | API key + eID | |
| DMR bulk | weekly XML, no licence found | |
| OEM documents | copyrighted | |
| EV Database | commercial | |
| ISO 24162 | paid | |
| EPREL tyres | API key needed | label classes only, no RRC value on the page |
| EEA cars/vans | | 2025 tables not yet read; OBFCM 2024 real-world (record `13e6fad9-…`) |

---

## 6. Charger / CPO / tariff library (Kiro PR #26, plus earlier passes)

- Kiro outputs: `docs/research/data-library-chargers-2026-11/` and `charger-hardware-sources-2026-11/`.
- **Errors found:**
  - `tariffs_dk.csv` contradicts itself on elafgift (0.8 øre "since 2021" vs "cut to 0.8 øre for 2026–27"). Needs the skat.dk satser.
  - `costs_extracted.csv` labels USD installer estimates as COWI.
  - Elindsigt tariffs are household (C) tariffs, not depot (A/B).
  - IEC 61851-23-3:2026, Milence prices and AFIR article numbers are unverified.
  - `catalogue.csv` was re-typed; spot-check it.
- **Still missing:**
  - Danish tender/concession/SLA documents in the repo;
  - current DSO takstblade (Radius, Cerius, N1, TREFOR, Konstant);
  - skat.dk elafgift.
- Unrun Kiro prompts kept in the project: `kiro-prompt-charger-cpo-data-library-2026-11-06.md` and `kiro-prompt-data-library-sources-2026-11-06.md`.

---

## 7. Open items / next steps (in order)

1. Review Kiro's EEA truck validation v2 PR when it arrives (checks are listed in the 11-07 calibration closeout §3).
2. Read the EEA RP 2024–25 READ_ME and metadata XML (licence, column definitions).
3. Fields EEA can't fill come from OEM sheets: charging power, connector/MCS, OEM usable kWh, chemistry, warranty.
4. Truck FzISO and the CdxA bin edges (A1–A24) are not in EEA or the regulation. `[BOB]`
5. Motor type for IEPC trucks is not in EEA.
6. Charger library: fetch the DSO takstblade, skat.dk elafgift and the Danish tender/SLA docs; fix Kiro's CSV errors.
7. Buses: find the primary ↔ completed link (parked).
8. Not yet researched: Sweden, Germany KBA, UK, US, Norway, body makers.
9. Verify BEK 1447/2025 on retsinformation.dk; resolve ZEV +2 t stacking.

---

## 8. Archive

Batch 2 (9 Nov 2026) holds the originals: the 6 Nov and 7 Nov closeouts and the 7 Nov combined status. The 7 Nov EEA closeout is also on `main` at `docs/research/inputs/`.
