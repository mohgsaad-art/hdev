# Kiro research task: EV Scope charger, CPO and charging-cost data library, pass 1 (deep dive), 6 Nov 2026

Write for Bob in plain English, short sentences. Bob is the only person named.
Repo: `mohgsaad-art/hdev`. New branch: `data-library-chargers-2026-11`. **Do not change `src/`.** VECTO source (for reference only): `mohgsaad-art/VECTO`.

## 0. What this is

This is the charging-side twin of `kiro-prompt-data-library-sources-2026-11-06.md` (vehicle data library). Same rules, same tags, same deliverable style.

Goal: build a **sourced, licence-checked data library** of everything EV Scope needs to size, simulate and cost depot and public charging for heavy trucks (N2/N3), buses (M2/M3), vans (N1) and cars (M1), Denmark/EU focus:
1. Charger hardware: OEM technical data (AC, DC, MCS; power, voltage, current, cables, posts/dispensers, power cabinets, power sharing, efficiency, standby, ramp rates, response times, derating).
2. Communication and control: OCPP, ISO 15118, smart-charging profiles, response times to setpoints, Plug & Charge.
3. Costs: hardware, installation, grid connection, software/backend, maintenance/SLA, replacement cycles.
4. CPOs, eMSPs and charging contracts: who operates in Denmark/EU for heavy duty, public prices (kWh, minute, session, idle/blocking fees, subscriptions), depot/B2B contract structures (CPaaS, charging-as-a-service, revenue share, concession contracts).
5. Electricity price stack for charging in Denmark: spot, DSO tariffs, Energinet tariffs, elafgift, refund schemes, connection fees.
6. Regulation and standards that fix any of the above (AFIR, EPBD, Danish rules).

**Draft the structure, do not build the engine.** EV Scope is commercial: licence terms matter for every source.

**[INFERENCE] by Claude, labelled as such:** the topic list above is Bob's request translated into categories. It is not a claim that public data exists for each. Part of the job is to say plainly where no public source exists.

## 1. Read first

On the branch, in `docs/research/inputs/` (Bob adds these):
- `kiro-prompt-data-library-sources-2026-11-06.md` and `session-closeout-2026-11-06-data-library-research.md`: the vehicle-side pass, for rules and format.
- `manual-fetch-list-2026-11-06.md`: already-collected links. Don't duplicate.
- Project knowledge-base files on charging (Bob copies them in from the claude.ai project, folder `claude/knowledge-base/`):
  - `charging-infrastructure/`: `depot-charging-establishment-guide.md`, `region-hovedstaden-charging-tender-spec.md`, `roskilde-charging-contract.md`, `lyngby-taarbaek-charging-contract-draft.md`, `hilleroed-kommune-charger-tender-locations.md`, municipal charging strategies (Horsens, Esbjerg, Hillerød, Køge), `vejledning-til-kommuner-charging-guidance.md`, shared-parking guides.
  - `data-reports-misc/`: `ladestandere-kravspecifikation-paradigme.md`, `ladestandere-koncessionskontrakt-udkast.md`, `ladestandere-operatoerens-serviceniveau.md`, `ladestandere-but-paradigme.md`, `ladestandere-vejledning-udbudsforskrifter.md`, `planlaegning-etablering-ladeinfrastruktur-handbog.md`, `kbh-handlingsplan-ladeinfrastruktur-2021-2025.md`.
  - `fleet-electrification-guides/`: `smartladning-og-v2x-for-virksomheder.md`, `virksomhedsguide-2023-ladeinfrastruktur.md`, `guide-omstilling-ellastbiler.md`.
  - `grid-connection/`: Energinet/ENS/Cerius-Radius connection-priority documents.
- Three Excel files Bob holds: `eltiltrucks-beregner-ark.xlsx` (COWI e-truck calculator), `Elindsigt2.2.xlsx`, `ChargePointCalculator_v5.xlsx`.

**Use these first.** Tender specs and concession contracts often hold real SLA, uptime, response-time and price-structure clauses; extract them with section numbers.

**Already known from the COWI file (Claude's earlier audit, do not re-derive, but do re-check):**
- Charger + cabinet cost bands by kW (22, 43.5, 50, 80, 150, 400 kW) in DKK with trenching cost. COWI's only attribution: prices "hentet hos en ladestanderoperatør i 2024", operator not named. **Tag `[C]`, unverifiable source.** Find independent price points to compare.
- Radius connection fee formula used by COWI (fixed base 0–25 A + DKK per extra A), sourced to radiuselnet.dk. The rate may have changed: re-fetch the current figure.
- Public fast-charging average 3.25 DKK/kWh, FDM, 1 Jan–15 Aug 2024 (Uno-X, E.ON, Allego, OK). Dated: find a newer FDM figure or equivalent.
- Load factor 0.85 in COWI: unsourced. Do not reuse without a source.

## 2. Rules (strict)

1. **No invented numbers.** Every value needs a link, page/table/section number for PDFs, the exact quote, and the document date.
2. Tag every item:
   - `[V]` you opened the primary source
   - `[C]` secondary source or snippet only
   - `[D]` you derived it (show the arithmetic)
   - `[INFERENCE]` your reasoning
   - `[BOB]` you could not open it; give the exact URL and what to get
3. Facts and inferences on separate lines.
4. Keep these apart, always:
   - rated vs continuous vs peak power (and peak duration)
   - per-cabinet vs per-dispenser vs per-connector power
   - grid-side (AC input) vs vehicle-side (DC output) power and efficiency
   - max current vs current at a given voltage (power vs voltage curve)
   - list price vs quoted/tender price vs subsidised price; excl./incl. VAT; currency and year
   - hardware vs installation vs grid connection vs software vs service
   - public ad-hoc price vs subscription price vs B2B contract price
   - datasheet claim vs certified/tested vs field-measured
   - standard requirement (what the standard allows) vs product capability (what the product does)
5. OEM figures = `OEM claim`, with datasheet date/revision and product generation.
6. Prices: always currency, year, VAT status, what is included, and region. Convert only if asked, and show the exchange rate source and date.
7. Don't scrape sites whose terms forbid it (price apps, roaming platforms, CPO apps). Record the terms.
8. Aggregators and trade press (electrive, ChargeUp Europe, Zap-Map, PlugShare, TÜV-style blogs, consultancy blogs) are **leads only**; confirm with the primary source or mark `[C]`.
9. When sources disagree, list both. Never pick one silently.
10. No efficiency, ramp rate, response time, coincidence factor, uptime or cost value without a source. If a standard sets a requirement (e.g. a response time for setpoint changes), quote the clause; do not present it as measured product behaviour.
11. Standards documents (IEC, ISO, SAE, EN) are usually paid. Use public summaries, scope pages and freely published drafts; record what you could and could not read. Never reproduce paid text beyond a short quote.

## 3. The fields EV Scope needs

### 3.1 Charger hardware (per product / variant)
- Make, model, variant, generation, datasheet date/revision, market availability (EU/DK)
- Type: AC / DC / MCS / pantograph (top-down, bottom-up) / wireless (note only)
- Architecture: all-in-one vs split (power cabinet + dispensers/posts); max dispensers per cabinet; dynamic power sharing granularity (module size kW)
- Output power: rated, continuous, peak (+ duration); per connector; simultaneous charging split
- Output voltage range (V DC min–max) and **power vs voltage curve** (constant-power range; e.g. full power only above X V)
- Output current: max A DC per connector; cable-cooled vs uncooled limit
- AC input: voltage, phases, frequency, max input current, input kVA, power factor, THD
- Efficiency: peak and at partial load (with the load points given); standby/no-load consumption (W)
- **Ramp rate** (kW/s or time to full power after session start)
- **Response time** to a power setpoint change (local and via OCPP/backend), if published
- Derating: temperature range, altitude, derating curve
- Connectors: CCS2 (IEC 62196-3), MCS, CHAdeMO, Type 2 AC; number per unit
- Cables: length, cooled/uncooled, cable management, max current per cable
- Posts/dispensers: footprint, IP/IK rating, cable reach
- Bidirectional capability (V2G/V2X), and to which standard
- Communication: OCPP version(s) and certification (OCA), ISO 15118-2 / -20, Plug & Charge, DIN 70121, local load management, Modbus/API
- Metering: MID / Eichrecht, display, payment terminal (AFIR ad-hoc requirement)
- Mass, dimensions, noise dB(A), cooling (air/liquid)
- Warranty, design life, MTBF if published
- List price (if public), price year

### 3.2 MCS specifically
- Status of the MCS standard(s): IEC (e.g. IEC 61851-23-3, IEC 63379 — verify numbers), SAE J3271, CharIN MCS specification version and date. Which are published vs draft as of Nov 2026.
- Max current and voltage defined by the standard vs what shipping products deliver.
- Shipping MCS products in EU (OEM, model, kW, A, V, first delivery date).
- Trucks with MCS inlets on sale in EU (OEM, model, MCS kW claimed). Link to the vehicle-library prompt; do not duplicate battery data.
- Public MCS sites in EU/DK (operator, location, kW, opening date). Pilot vs commercial.

### 3.3 Communication, control and timing
- OCPP 1.6J, 2.0.1, 2.1: what each adds for smart charging (SetChargingProfile, composite schedules, ISO 15118 support, V2X in 2.1). Source: Open Charge Alliance documents (check licence; spec text may be free to download but not free to reproduce).
- OCA certification lists: which products are OCPP 2.0.1 certified.
- Published or measured **latency** from backend setpoint to delivered power change; any DSO/TSO requirement for flexibility response time (Energinet ancillary services: FCR, aFRR, mFRR prequalification timing for EV aggregations).
- Danish flexibility/aggregator products that EV depots can enter, and the technical prerequisites.

### 3.4 Costs (each with currency, year, VAT, scope, region, source)
- Hardware price per kW class (AC 11/22 kW; DC 50, 150, 300–400 kW; MCS 750 kW–1 MW+)
- Installation (civil works, trenching per metre, foundations, cabling)
- Transformer / substation / switchgear (if customer-owned)
- Grid connection fees per DSO in Denmark (Radius, Cerius, N1, TREFOR El-net, Konstant, others): formula, DKK/A or DKK/kW, fixed parts, current tariff document and date
- Backend/software fees (per connector per month), SIM/data
- Maintenance/service contracts and SLA levels (uptime %, response time, fix time) with prices
- Spare parts / replacement cycle (cables, modules)
- Public cost studies: e.g. ICCT, T&E, ACEA, Fraunhofer, NOW GmbH, DTU, Energistyrelsen, Danish municipal tenders. Extract tables with page numbers.
- Subsidy and grant schemes that change capex (Danish ladepuljer for trucks, EU CEF AFIF): amounts, rules, award lists with real project costs (award lists often publish budget per site; these are real price points).

### 3.5 CPOs, eMSPs, charging contracts
- CPOs and HD-charging operators active in Denmark and nearby EU corridors. For each: sites, HD-capable sites, max kW, MCS yes/no, truck-accessible bays, booking, opening date. **Leads to check (from Claude's general knowledge, not verified, may be outdated):** Milence, Clever, E.ON Drive, Circle K, Ionity, Spirii, Monta, Allego, OK, Uno-X/other fuel-station brands, Aral pulse, Shell Recharge, EnBW, Tesla (trucks? check). Confirm each from primary sources; drop any that are wrong.
- Public price lists: per kWh, per minute, session fee, idle/blocking fee, subscription tiers, truck-specific tariffs, roaming mark-ups. Date-stamp every price; note whether prices are dynamic (time-of-day).
- eMSP / fuel-card providers for trucks (e.g. DKV, UTA, Shell Card, Circle K, Travis Road Services, check each): fees on top of CPO price.
- Depot and B2B contract models: charging-as-a-service, CPaaS, leasing, concession (from the Danish municipal concession drafts in section 1), revenue-share, fixed DKK/kWh offtake, energy-as-a-service. Extract clause structure: term, who owns hardware, who pays grid connection, price indexation, uptime penalties.
- Roaming platforms (Hubject, Gireve, e-clearing.net): fee structures if public.

### 3.6 Electricity cost stack for charging in Denmark
- Spot price: Energi Data Service (Energinet) datasets, DK1/DK2, hourly/15-min; licence.
- DSO tariffs (time-of-use, per customer category: A-high, A-low, B-high, B-low, C), per DSO, current tariff tables and dates. Check the current Danish tariff model and any 2025–2027 changes.
- Energinet system and network tariffs.
- Elafgift and any reduced rate or refund relevant to EV charging (the Danish "ladestander-refusion"/reduced elafgift for charging: confirm current status, rate, who can claim, end date).
- Effektbetaling / capacity charges if any DSO has them.
- Connection fee rules (tilslutningsbidrag) and grid-connection queue rules (link to project `grid-connection/` docs).
- Public price indices for charging: FDM, Energistyrelsen, Danmarks Statistik, ChargeUp Europe.

### 3.7 Regulation and standards that set numbers
- AFIR (Reg. (EU) 2023/1804): HDV charging pool targets (power per pool, spacing, dates), ad-hoc payment, price transparency, data (static/dynamic data, National Access Point), OCPP/ISO 15118 obligations and dates. Extract article + paragraph.
- Danish National Access Point for AFIR data: does it exist, URL, licence, what fields (location, power, connector, price, availability)? **High priority: it may be the open dataset of all DK public chargers with prices.**
- EPBD recast pre-cabling/charger requirements (relevance to depots: low, note only).
- Danish rules: Ladestanderloven / BEK on charging points, elafgift law, any requirement for smart charging, ISO 15118, meters.
- EU delegated acts on charging standards (Reg. 2023/1804 Annex II and later amendments adding MCS?): verify.
- Measuring instrument rules (MID; Germany Eichrecht as a market constraint).

## 4. Work list

### 4.1 Mine the project documents first
Extract from the Danish tender, concession and service-level documents listed in section 1: required kW, connector types, OCPP version, uptime %, response/fix times, penalties, price structure, contract term. Section/page for every item. These are real Danish procurement requirements: high value.

### 4.2 Charger OEM datasheets
For each OEM below, find the current EU datasheet(s) for its AC, DC, MCS (if any) and HD depot products. Fill section 3.1 fields with page numbers.
**Lead list (Claude's general knowledge, not verified; drop or add as found):** ABB E-mobility, Kempower, Alpitronic, Siemens (SICHARGE / Heliox), Heliox, Ekoenergetyka, Delta, Tritium/Exicom, Autel, Circontrol, Wallbox, Zaptec, Easee, Enercon? (check), Efacec, SBRS, Ads-tec, Nidec?, Hitachi Energy (bus/pantograph), Schunk (pantograph), Staubli (MCS connectors), Phoenix Contact, Huber+Suhner, ITT (MCS cables/connectors), Kostad, Enovates, Elinta, Teltonika.
- Mark which OEMs publish list prices (most do not).
- Record each datasheet's licence/terms (OEM docs are copyrighted: we store values with citation, not the PDFs).

### 4.3 MCS deep dive
Section 3.2. Primary sources: CharIN, IEC/SAE catalogue pages, OEM press releases, Milence and other HD CPO announcements, EU-funded MCS pilot reports (e.g. HoLa project in Germany: check name, report licence). Record dates carefully; MCS status changes fast.

### 4.4 OCPP / ISO 15118 / timing
Section 3.3. Open Charge Alliance pages and certification list; Energinet prequalification documents for flexibility services and any EV-specific rules; published papers or test reports with **measured** setpoint latency or ramp rate (academic, DTU, JRC, TNO, Fraunhofer). If none exist, say so.

### 4.5 Costs
Section 3.4. Prioritise: Danish municipal tender award values; Danish/EU grant award lists with per-project budgets; ICCT/T&E/NOW/Fraunhofer/JRC cost studies with tables; DSO tariff documents. Each price needs year and scope. Compare with the COWI bands (section 1) and list the differences; do not judge which is right without evidence.

### 4.6 CPOs and prices
Section 3.5. Use CPO websites and published price pages (not apps if terms forbid). For Denmark, also check the AFIR National Access Point (3.7) and any Energistyrelsen/Vejdirektoratet charger register. Record date of each price capture.

### 4.7 Electricity cost stack
Section 3.6. Energinet, each DSO's tariff page and PDF, Skatteministeriet satser for elafgift, Energistyrelsen. Current values with effective dates. Note planned changes with dates.

### 4.8 Regulation
Section 3.7. EUR-Lex consolidated text of AFIR (latest consolidation date); Danish retsinformation.dk texts.

### 4.9 Open datasets on chargers and charging sessions
Find and catalogue (fields, size, licence, commercial use):
- AFIR NAP Denmark (and Germany, Netherlands, Sweden for comparison)
- EAFO (European Alternative Fuels Observatory) charger statistics
- Open Charge Map (licence: check, CC BY-SA?), OpenStreetMap charging tags (ODbL: copyleft implications for a commercial tool)
- Bundesnetzagentur Ladesäulenregister (Germany)
- NOBIL (Norway)
- Real charging-session datasets (e.g. Dundee, Boulder, ElaadNL, ACN-Data/Caltech, Danish datasets): licence and whether HD trucks/buses are included
- NREL Fleet DNA / any bus-depot charging load datasets (CC BY 4.0 for Fleet DNA per earlier pass; confirm charging data coverage)

## 5. Questions to settle (mark verdict or `[BOB]`)
1. Does a Danish AFIR National Access Point exist, and does it publish prices openly with a licence that allows commercial reuse?
2. Which MCS standard documents are published (not draft) as of Nov 2026, and what max current/power do they define?
3. Are there any public, **measured** values for charger ramp rate and setpoint response time (OCPP) for DC chargers? If not, which standard clauses set requirements?
4. Is there a source for charger efficiency at partial load beyond OEM datasheets?
5. What is the current Danish elafgift treatment for EV charging (reduced rate/refund), and until when?
6. Are COWI's charger cost bands consistent with independent, dated sources? Where not, list both.
7. Current Radius connection fee per A vs COWI's figure; and equivalents for Cerius, N1, TREFOR El-net, Konstant.
8. Public truck charging price in Denmark (Milence and others) per kWh, date-stamped.
9. Which Danish public tenders/concessions publish uptime % and fix-time SLAs, and what values?
10. Licence of Open Charge Map and OSM charging data: usable in a commercial tool, and under what conditions?

## 6. Draft the data-library structure

Propose (don't build) tables, each with columns, units, a "basis" tag (rated/continuous/peak; per-cabinet/per-connector; claim/tested/measured; list/tender/quoted price), source id, page, quote, date, licence flag. Minimum tables:
- `charger_products` (make, model, variant, generation, type, architecture)
- `charger_power_specs` (power vs voltage, current, efficiency, standby, derating, ramp, response)
- `charger_connectors_cables`
- `charger_comms` (OCPP, ISO 15118, certification)
- `charger_costs` (hardware, install, connection, software, service; currency, year, VAT, scope)
- `grid_connection_tariffs` (DSO, formula, effective date)
- `electricity_tariffs` (spot source, DSO ToU, Energinet, elafgift; effective dates)
- `cpo_sites` (operator, location, kW, MCS, truck access)
- `cpo_prices` (operator, product, price components, capture date)
- `contracts` (model, term, ownership, SLA, penalties; from tenders)
- `standards_regulation` (document, clause, requirement, in-force date)
- `sources_licences`

Say which columns can be filled from open, commercially usable sources, which need OEM documents or quotes, and which have no public source.

## 7. Deliverables

Put everything in `docs/research/data-library-chargers-2026-11/`.

1. `catalogue.csv`: `id, name, url, publisher, region, data_categories, fields_verified, fields_claimed, format_access, size, licence, commercial_use (yes/no/unclear), update_frequency, doc_date, status (V/C/BOB), notes`
2. `field_coverage.csv`: `field, charger_class (AC/DC/MCS/pantograph), best_source_id, other_source_ids, coverage (full/partial/none), notes`
3. `charger_specs_extracted.csv`: `make, model, variant, generation, type, field, value, unit, basis, condition (e.g. at V, at temp), source_id, page_or_table, quote, doc_date, tag`
4. `costs_extracted.csv`: `item, kW_class, value, currency, year, vat (excl/incl), scope_included, region, basis (list/tender/quote/study), source_id, page_or_table, quote, tag`
5. `cpo_prices.csv`: `operator, country, site_or_network, connector, max_kW, price_component, value, unit, currency, vat, capture_date, source_url, tag`
6. `tariffs_dk.csv`: `component (spot/DSO/Energinet/elafgift/connection), dso, customer_category, time_band, value, unit, effective_from, effective_to, source_url, page, tag`
7. `contracts_and_sla.md`: extracted clauses from tenders/concessions, with document and section.
8. `standards_regulation.md`: section 3.7 and MCS/OCPP status, clause references.
9. `conflicts.md`: section 5 items plus new ones, both links, verdict or `[BOB]`.
10. `library_schema.md`: section 6.
11. `bob_to_fetch.md`: links not already in `manual-fetch-list-2026-11-06.md`; columns: what, link, how, why.
12. `report.md`. Top: max 15 lines answering:
    - What can we fill from open, commercially usable sources?
    - What needs OEM documents or supplier quotes?
    - What has no public source?
    - Top 10 sources to start the charger library with.
    Then detail by category (hardware, MCS, comms/timing, costs, CPOs/prices, tariffs, regulation).
13. A PR against `main`. No changes to `src/`.

## 8. Done when
- Every OEM in 4.2 and every CPO lead in 3.5 has a catalogue row, even if "not found / not relevant", with the search used.
- Every value in the extracted CSVs has a link, page/section and quote, date, and tag.
- Every price has currency, year, VAT status and scope.
- All 10 questions in section 5 have a verdict or a `[BOB]` item.
- Nothing from Claude's lead lists is carried forward as fact without a `[V]` or `[C]` source.
