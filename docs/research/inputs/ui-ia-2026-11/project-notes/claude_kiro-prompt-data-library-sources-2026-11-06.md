# Kiro research task: EV Scope data library, pass 3 (deep dive), 6 Nov 2026

Write for Bob in plain English, short sentences. Bob is the only person named.
Repo: `mohgsaad-art/hdev`. New branch: `data-library-sources-2026-11`. **Do not change `src/`.** VECTO source: `mohgsaad-art/VECTO`.

## 0. What this is

Claude has done two research passes and Gemini one. Your job is pass 3:
1. **Dig deeper** into what passes 1 and 2 found: open the primary documents, get page numbers and exact quotes, and fill the missing fields.
2. **Cover the gaps** both passes left open (section 4).
3. **Settle the open conflicts** (section 5).
4. **Draft the data-library structure** (section 6), so we can decide what goes in.

Vehicle classes: heavy trucks N2/N3, buses M2/M3, vans N1, cars M1. Focus: Denmark/EU. EV Scope is a **commercial** tool, so licence terms matter for every source.

## 1. Read first

On the branch, in `docs/research/inputs/` (Bob adds these):
- `research-pass1-2026-11-06.md`: Claude pass 1 (catalogue, licences, CdxA table, CIF/MRF).
- `research-pass2-2026-11-06.md`: Claude pass 2 (Danish weights settled, OEM values, conflicts, extracted-value table).
- `gemini-research-2026-11-06.txt`: Gemini. **Leads only.** Several of its claims were false or unsourced; see section H of the fetch list.
- `manual-fetch-list-2026-11-06.md`: every link Bob is fetching (sections A–G), with status.
- `findings-eea-hdv-zev-data-2026-11-06.md`: what the EEA 2019–2023 file and Bob's 139-column file hold for ZEVs.
- Any files Bob has fetched, in `docs/research/inputs/fetched/`. **Use these first. Don't re-search what's already there.**

**Already settled (don't redo):**
- CdxA bins A1–A24 (Reg. 2018/956 Annex I Part C).
- VECTO CIF is per vehicle and private; MRF is confidential.
- Danish BEK 1447/2025: 20 t two-axle from 1 Jan 2026; 58 t (7+ axles) and 4.20 m from 1 Jan 2027.
- EEA data is CC-BY 4.0; RDW is CC-0; Traficom open data is CC BY 4.0; NREL Fleet DNA is CC BY 4.0.
- VECTO code is EUPL 1.2.
- ISO 24162 covers refuse trucks only.
- Volvo FH/FM ePTO is 30/60/90 kW.

### 1b. New since the first draft: what Bob has already fetched (6 Nov, evening)

Bob has placed these in `docs/research/inputs/fetched/`. **Open and extract from each; tag `[V]` with page/table.** Files marked (not yet read) were attached but nobody has extracted values yet.

| File | What it is | Status |
|---|---|---|
| Volvo FM Electric global page (txt) | Volvo spec table | Read. Battery 360–540 kWh (4–6 packs), **usable up to 460 kWh**, CCS 350 kW (<750 V), 20→80 % in 65 min, power levels 300/350/400/470/540 kW, 2 EM + 8-speed, range up to 470 km, ePTO 3 levels 30/60/90 kW + clutch-independent transmission PTO. `[V]` OEM claim, page text dated 2026 (no model-year stated). Resolves installed vs usable for FM only. |
| Frederiksberg PVI e-RCV article (txt) | Varebilogtransport.dk, 28 Jun 2013 | Read. 255 kWh / 600 V; 26 t GVW / 9 t payload (vs 12 t diesel); 80 % usable = 204 kWh; 0.9 kWh/km road (204/225) and **1.7 kWh/km collection (204/120)**; charge 20–100 % 6 h, 0–full 9 h. `[C]` trade press, 2013, one pilot truck. Conflict 8: the 1.7 figure is reproduced by 204/120; the 2.25 figure is not in this article, find its source. |
| Scania/Unicon/Liebherr article (txt) | The Driven, 11 May 2026 | Read. 400 kWh battery, ePTO drives the mixer drum, ~200 km. `[C]` trade press. Find the Scania/Unicon primary release. |
| RDW `m9d7-ebf2` metadata (txt) | Dutch registry column list | Read. Licence "Public Domain / CC0". Useful columns: `massa_alt_aandr` (additional mass for alternative drive), `technische_max_massa_voertuig`, `laadvermogen`, `aerodyn_voorz`, `massa_rijklaar`, `wielbasis`. Next: RDW's electric sub-datasets (battery kWh, power, consumption), see 4.5. |
| EPREL tyres page (txt) | EU tyre label registry | Read. 311,463 models, classes C1/C2/C3, labels = fuel efficiency class, wet grip, noise dB. Public API needs a key request. Check whether **rolling resistance coefficient** is exposed (the label gives a class only) and the C3 coverage. |
| EP Legislative Train, W&D directive (txt, 25 Oct 2026) | Status of 2023/0265(COD) | Read. Status "Tabled". EP: +4 t ZEV. Council general approach 4 Dec 2025: ZEV bonus differs for 5- and 6-axle, up to +0.9 m length. Trilogues started 9 Dec 2025. Nothing says adopted. Confirm there is no later outcome. |
| EEA cars page (txt) | Cars CO2 explorer, 10,833,597 rows | Read. Has electric energy consumption, electric range, mass, WLTP fields. |
| Table definitions: vans 2025 provisional, cars 2025 provisional (xlsx) | EEA column definitions | (not yet read) List fields and units; say which are usable for M1/N1 library rows. |
| EEA HDV RP 2023 subset page, EEA real-world cars & vans page (txt) | Page text | Read. Real-world (OBFCM) 2024 dataset published 3 Sep 2026, record `13e6fad9-149c-4b86-9d83-cdf3569ccfee`. |
| `129da213-ISO-FDIS-24162.pdf` (11 pp) | Refuse-body standard draft | (not yet read) Extract duty cycles, energy/lift definitions, anything on electric bodies. |
| `f9e6fc4d-COM_2025_589.pdf` (33 pp) | Commission proposal | (not yet read) Extract what changes for ZEV weights/dimensions and the date. |
| `c54ce48d-B20230141505.pdf` (14 pp) | Danish legal text | (not yet read) Identify it (BEK 1415/2023?) and extract the ZEV +2 t wording; settle conflict 8b below. |
| `376db476-DG1229.pdf`, `36c0ab69-E_Produktblatt_eEconic_ENG_screen.pdf`, `3225049d-BEV_BATTERY_ELECTRIC_VEHICLE.pdf`, `c7d4f9bb-2BATT170_Eng_05_331735919.pdf`, `b4ebb9b8-Carrier_Transicold_Vector_eCool_ENG.pdf`, `a31c6f0d-electric-truck-mixer-etm.pdf` | OEM / body documents | (not yet read) Identify each from its first page, then extract every aux/PTO/battery/charging value with page numbers. eEconic sheet settles conflicts 1–2; Liebherr ETM settles conflict 7; Carrier settles reefer electrical input vs cooling capacity. |

**EEA RP 2024–25 and RP 2023–24 are relational, not one flat file.** Bob listed the files (record `1e44df1d-…` and `450fe389-…`). Tables: `vehicle` (392 MB), `memberstate_vehicle` (177 MB), `missionprofile` (1.5 GB), `axle` (214 MB), `steeringpumptechnology` (84 MB), `enginetorquelimit`, `enginefueltype`, `advancedreducingtechnology`, and the **electric ones: `battery` (824 KB), `electricmachine` (362 KB), `iepc` (311 KB), `voltagelevel_electricmachine` (371 KB), `voltagelevel_iepc` (434 KB), `capacitor` (32 KB), `derogation`, `transfer`**. RP 2023–24 has `battery` (128 KB), `electricmachine` (4 KB), `iepc` (47 KB). Plus a READ_ME.txt and a 43 KB metadata XML. **Hypothesis `[INFERENCE]`: these hold the VECTO component inputs for ZEVs (battery, e-machine, IEPC, voltage level), which the 2019–2023 flat file lacked.** Nobody has opened them yet. Bob will upload the small ones; see 4.4.

## 2. Rules (strict)

1. **No invented numbers.** Every value needs a link, a page/table number for PDFs, and the exact quote.
2. Tag every item:
   - `[V]` you opened the primary source
   - `[C]` secondary source or snippet only
   - `[D]` you derived it (show the arithmetic)
   - `[INFERENCE]` your reasoning
   - `[BOB]` you could not open it; give the exact URL and what to get
3. Facts and inferences on separate lines.
4. Keep these apart, always:
   - installed vs usable kWh
   - continuous vs peak power (and peak duration)
   - electrical input vs mechanical output (ePTO)
   - cooling capacity vs electrical input (reefers)
   - measured vs simulated vs reported vs OEM claim
5. OEM figures = `OEM claim`, with the document date and model generation.
6. Don't scrape sites whose terms forbid it (EV Database, OEM portals). Record the terms.
7. Aggregators (motorwatt, truckbusworld, evcompass, electrive, trade press) are **leads only**; confirm with the OEM or mark `[C]`.
8. When sources disagree, list both. Never pick one silently.
9. No efficiency, drag or loss value without a source. In particular, do not use Gemini's "ePTO 0.82–0.88" or "1.5–2.5 % transmission drag".

## 3. The fields EV Scope needs

**Battery**
- installed/usable kWh
- chemistry
- nominal voltage, Ah, pack/cell count
- internal resistance, OCV curve
- SoC window
- AC/DC/MCS kW
- charging curve (kW vs SoC, or 20–80 % times)
- thermal management / battery heater kW
- battery mass
- warranty/SoH terms

**Drivetrain**
- architecture (E2/E3/E4/IEPC)
- motor count
- continuous/peak kW and Nm
- torque/speed curve, efficiency map, drag torque
- gearbox type, gears and ratios
- axle ratio
- max input torque
- regen limits

**Auxiliaries (kW, per component)**
- cab and bus HVAC (heat pump vs PTC; heating and cooling)
- e-steering pump
- e-air compressor
- DC/DC 24 V load
- battery thermal management
- summer/winter values

**PTO / body**
- ePTO electrical and mechanical kW (continuous/peak/duration), voltage, SoC condition
- body equipment electrical input and energy per cycle, per hour or per tonne: refuse (compactor, lift), crane, reefer (input kW, COP), mixer drum, tipper, sweeper, hook lift

**Masses and limits**
- curb mass, GVW/GCW, axle loads, payload
- battery mass
- EU and Danish ZEV allowances (in force vs proposed, with dates)

**Aero and tyres**
- CdxA/CdA, frontal area
- tyre RRC/label class, size

**Consumption**
- CIF kWh/km
- WLTP Wh/km and range
- measured kWh/km with mass, temperature, cycle and sample size

## 4. Work list

### 4.1 Dig deeper on pass 1 + 2 findings
For each source below, open the primary document. Record every field from section 3 that it contains, with page and quote.
- Mercedes eActros 600 product sheet, eEconic product sheet and pages, ZF eWorX.
- DAF XD and XF Electric infosheets: ePTO 25/90 kW, and whether 60/100 kW were added (electrive Jan 2026).
- MAN eTGX/eTGS/eTGL gen 1 and gen 2 (2026): battery gross/net per pack, chemistry, gears, MCS.
- Volvo FH/FM/FH Aero/FL/FE Electric pages, the electromobility product guide, the FL battery fact sheet, the VNR BBI.
- Scania BEV pages and the BEV body-builder booklet: PTO EL / PTO EM kW, voltage, 250 A supply.
- Solaris Urbino 12 electric sheets and STOAG fleet data: bus HVAC kW.
- Liebherr ETM; Dennis Eagle eCollect; Carrier Vector eCool / 1550 E City / [R]eCool.
- KsNI evaluation (Table 2-5), Öko-Institut ELV-Live reports 1 and 2, NOW bus report (heating chapter), ZEHID annual report 2026 (pp. 21–36) and decks, ICCT Aug 2025 (check the kWh/km unit typo), TNO R10409, CEC-600-2024-010, Renodjurs Bilag 9, Frederiksberg PVI articles.

### 4.2 VECTO itself (you have the repo)
- `Generic Vehicles/` (Declaration and Engineering mode): list every BEV/PEV generic vehicle (E2, E3, E4, IEPC, buses). For each:
  - motor rated/peak power and torque
  - the drag curve file
  - gear and axle ratios
  - battery (REESS) capacity, voltage, Ri, SoC limits
  - aux values

  Give file paths and line numbers.
- Reg. 2017/2400 Annex Xb standard values as implemented in VECTO code: e-machine standard values, IEPC, REESS (Appendix 10). Give file and line.
- `Resources/Declaration/` aux tables for BEV: ES, SP, PS, HVAC, Cond. Which values apply to PEVs? Which electric technologies exist (e.g. "electrically driven" steering pump, electric compressor)?
- Check the licence file (EUPL 1.2).

### 4.3 Gaps neither pass covered (pass 3 queue)
- **Sweden:** RISE / Chalmers measured e-truck data; klimatpremie data.
- **Germany:** KBA (per-type technical data or statistics only), Fraunhofer ISI / IML, ADAC Ecotest e-vans.
- **UK:** Cenex reports, VCA, Logistics UK, eFREIGHT 2030 outputs.
- **US (physics only):** Argonne Autonomie, OSTI 2311852 contents and licence, CARB HVIP spec sheets.
- **Norway:** Enova e-truck reports, TØI, NAF/Motor El Prix (incl. vans), Statens vegvesen schema (battery/range fields?).
- **Denmark:** DTU studies, Energistyrelsen, ARC / Aarhus / Frederiksberg / other municipal e-refuse pilots, FDM e-van tests, Mobility Denmark / Dansk Elbil Alliance, DMR FTP extract fields.
- **OEMs not yet covered:**
  - Trucks: Renault E-Tech D/T/C, IVECO S-eWay and eDaily, Fuso eCanter, Ford E-Transit
  - Buses: Mercedes eCitaro, MAN Lion's City E, Volvo BZL/7900E, Yutong, BYD, Irizar, Heuliez, VDL, IVECO
  - Vans: VW ID.Buzz Cargo, Mercedes eVito/eSprinter, Renault Kangoo/Master E-Tech, Stellantis e-vans, Toyota Proace Electric
  - Body-builder guides: MAN (MANTED), Volvo EU, DAF BBI, Renault
- **Body makers:** Geesinknorba, FAUN, Zoeller, Joab, Norba, HIAB eHiPro, Palfinger, Thermo King Advancer, Schmitz Cargobull S.KOe COOL, Bucher, Aebi Schmidt, Boschung.
- **EU:** EAFO model lists; Battery Regulation 2023/1542 passport fields (which will be public, from when); EPREL API for C3 tyres; EEA OBFCM BEV columns.
- **Aggregators:** ZETI (fields, export, licence), Chargepoly, EV Database (API price/terms), Open EV Data (actual licence file), Nature Sci Data 2025 EV dataset (licence).

### 4.4 EEA files (highest priority; if you can download)
The EEA site returned 403 to Claude's sandbox, so try it, and if blocked mark `[BOB]`.
1. Read the READ_ME.txt and the metadata XML of record 1e44df1d (and 450fe389). Extract the table list, column definitions, units, keys that join the electric tables to `vehicle`, and the licence.
2. For `battery`, `electricmachine`, `iepc`, `voltagelevel_electricmachine`, `voltagelevel_iepc`, `capacitor`: list every column with dtype, null rate, 5 sample rows, row count. State plainly whether they hold **installed kWh, usable kWh, nominal voltage, peak/continuous kW, torque, maps, gear ratio, loss data**, or only technology codes / IDs / certification numbers. Do not guess from column names; show the values.
3. Join `battery` and the e-machine tables to `vehicle` (and `memberstate_vehicle`) and count ZEV vehicles with a battery record, by OEM, make, model, vehicle group. This is the "how many real BEV truck configurations have battery data" number.
4. Compare the `vehicle` header with Bob's 139-column file (columns in `findings-eea-hdv-zev-data-2026-11-06.md`); say whether Bob's file is this release or an earlier one.
5. `steeringpumptechnology`, `axle`: only the header and 5 rows; note what auxiliary data exists.
6. Skip `missionprofile` (1.5 GB) unless the other tables prove the joins need it; if you do open it, stream the first 100,000 rows only.
7. Licence: CC-BY 4.0 per catalogue; confirm from the metadata XML and note any personal-data or confidentiality notes (vehicle IDs are hashed).

### 4.5 RDW electric datasets
RDW dataset `m9d7-ebf2` is CC0. Find the sibling RDW datasets for fuel/energy (e.g. `Gekentekende_voertuigen_brandstof`, which in the Dutch API holds nominal continuous power and, for EVs, range/consumption fields): confirm their IDs, columns, licence, and whether N2/N3/M2/M3 BEVs have kWh or kWh/km. Report counts of electric N2/N3/M3 vehicles. If the API is blocked, mark `[BOB]` with the exact URL.

## 5. Open conflicts to settle

1. eEconic battery: 336 kWh installed (Mercedes) vs 3 × ~105 kWh = 315 kWh (Mercedes text, Electrek). Usable kWh?
2. eEconic ePTO: ~30/~52 kW electrical at 50 % SoC vs 31/55 kW mechanical vs eWorX 33/58 kW. Which is which?
3. DAF XD torque: 930/1,370 Nm (daf.global) vs 1,500/2,400 Nm (electrive).
4. DAF ePTO options: 25/90 kW vs 60/100 kW added.
5. MAN chemistry NMC (MAN) vs LFP (madeingermany.de); usable 480 of 534 kWh vs "534 usable" (electrive).
6. Volvo FL battery: 175–565 kWh / 3–8 packs (global) vs 280–565 kWh / 3–6 packs (UK).
7. Liebherr ETM peak: 120 kW (p.5) vs 125 kW (p.7).
8. Frederiksberg PVI e-RCV: 1.7 vs 2.25 kWh/km in collection.
9. ICCT Aug 2025: "92 to 150 kWh/km" (typo for kWh/100 km?).
10. Danish ZEV +2 t (BEK 1415/2023) vs the new 20 t two-axle limit "uanset drivmiddel" (BEK 1447/2025): do they stack or does the 20 t replace the bonus? Settle from the legal text (see `c54ce48d-B20230141505.pdf`).
11. EEA PEVArchitecture field: where it comes from (VECTO input vs EEA-added), and which release has it.
12. Volvo FM: installed 360–540 kWh vs usable "up to 460 kWh" (Volvo page). Is 460 the usable of the 540 kWh pack? Find the Volvo document that states usable per pack count. Do not assume a ratio.
10. Danish ZEV +2 t (BEK 1415/2023): does it still apply on top of the new 20 t two-axle limit (BEK 1447/2025, "uanset drivmiddel")?
11. EEA: does the RP 2024–25 CSV contain PEVArchitecture or energy fields (record 13f5615a / 1e44df1d)?

## 6. Draft the data-library structure

Propose (don't build) the tables a data library would need. For each table:
- the columns
- units
- the "basis" tag (installed/usable, continuous/peak, measured/simulated/claim)
- source id, page, quote
- a licence flag

Minimum tables:
- vehicles (make, model, variant, generation, class, VECTO group)
- batteries
- motors/drivetrain
- aux components
- ePTO/body equipment
- masses/limits (date-effective)
- measured consumption (with conditions)
- sources/licences

Say which columns can be filled from open, commercially usable sources, which need OEM documents, and which have no public source.

## 7. Deliverables

Put everything in `docs/research/data-library-sources-2026-11/`.

1. `catalogue.csv`. Columns: `id, name, url, publisher, region, vehicle_classes, data_categories, fields_verified, fields_claimed, format_access, size, licence, commercial_use (yes/no/unclear), update_frequency, doc_date, status (V/C/BOB), found_in (P1/P2/G/K), notes`
2. `field_coverage.csv`. Columns: `field, class, best_source_id, other_source_ids, coverage (full/partial/none), notes`
3. `extracted_values.csv`. Columns: `make, model, variant, generation, class, field, value, unit, basis, source_id, page_or_table, quote, doc_date, tag`
4. `vecto_generic_bev.md`: section 4.2 results with file and line references.
5. `conflicts.md`: all section 5 items plus any new ones, with both links and a verdict.
6. `library_schema.md`: section 6.
7. `bob_to_fetch.md`: only links **not already** in `manual-fetch-list-2026-11-06.md`, same columns.
8. `report.md`. Top: max 15 lines answering:
   - What can we fill from open, commercially usable sources?
   - What needs OEM documents?
   - What has no public source?
   - Top 10 sources to start the library with.

   Then detail by data category.
9. A PR against `main`. No changes to `src/`.

## 8. Done when
- Every source and OEM in sections 4.1–4.3 has a catalogue row, even if it's "not found", with the search you used.
- Every value in `extracted_values.csv` has a link, page and quote.
- All 11 conflicts have a verdict or a `[BOB]` item.
