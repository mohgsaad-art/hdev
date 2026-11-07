# Charger data-library schema (proposed, not built) — pass 1

Written for Bob. Plain English. This proposes the tables; it does not build the
engine. Every table carries a `basis` tag so the rated/continuous/peak,
per-cabinet/per-connector, claim/tested/measured, and list/tender/quoted
distinctions never collapse. Every value row carries `source_id`, `page`,
`quote`, `date`, and a `licence_flag`.

Column legend used throughout:
- `basis` — one of: rated / continuous / peak(+duration); per-cabinet /
  per-dispenser / per-connector; grid-side / vehicle-side; claim / tested /
  measured; list / tender / quoted / subsidised; standard-allows /
  product-delivers.
- `tag` — V / C / D / INFERENCE / BOB (as in the CSVs).
- `licence_flag` — open-commercial / cite-only / share-alike / paid / unclear.

---

## 1. `charger_products`
make, model, variant, generation, datasheet_date, type (AC/DC/MCS/pantograph/
wireless), architecture (all-in-one / split), max_dispensers_per_cabinet,
sharing_module_kW, market_availability (EU/DK), source_id, page, quote,
licence_flag, tag.
- Fillable now from OEM datasheets (**cite-only**). Not open-commercial.

## 2. `charger_power_specs`
product_id, power_rated_kW, power_continuous_kW, power_peak_kW, peak_duration_s,
power_basis (per-connector/per-cabinet), voltage_min_V, voltage_max_V,
constant_power_above_V, current_max_A, current_cooled_flag, ac_input_V,
ac_input_phases, ac_input_max_A, power_factor, thd_pct, efficiency_peak_pct,
efficiency_partial (list of load-point:pct), standby_W, ramp_rate_kW_per_s,
setpoint_response_ms, derating_temp_range_C, derating_altitude, source_id, page,
quote, date, basis, tag.
- Power/voltage/current/peak-efficiency fillable from datasheets (cite-only).
- **efficiency_partial, standby_W, ramp_rate, setpoint_response: NO PUBLIC
  SOURCE** — mostly empty / BOB.

## 3. `charger_connectors_cables`
product_id, connector_type (CCS2/MCS/CHAdeMO/Type2/NACS), connector_standard
(IEC 62196-3 / IEC 61851-23-3 / ...), connectors_per_unit, cable_length_m,
cable_cooled_flag, cable_max_A, cable_mgmt, post_footprint, ip_rating, ik_rating,
cable_reach_m, source_id, page, quote, licence_flag, tag.
- Partly fillable from datasheets; MCS connector ratings need connector-maker
  sheets (Staubli/H+S/Phoenix Contact) — BOB.

## 4. `charger_comms`
product_id, ocpp_versions, ocpp_certified_flag (OCA registry), iso_15118_2_pnc,
iso_15118_20, din_70121, local_load_mgmt, modbus_api, v2g_v2x_flag,
v2x_standard, metering_mid_eichrecht, payment_terminal_flag, source_id, page,
quote, licence_flag, tag.
- OCPP/ISO 15118 fillable from datasheets (cite-only). `ocpp_certified_flag`
  needs the OCA registry — BOB. MID/Eichrecht + payment terminal partly from
  datasheet + AFIR requirement.

## 5. `charger_costs`
item, kW_class, value, currency, year, vat (excl/incl), scope_included
(hardware / install / connection / software / service), region, basis (list /
tender / quoted / study / subsidised), source_id, page, quote, licence_flag, tag.
- Fillable from COWI (DK 2024, cite-only) + study/installer bands (secondary).
  **No OEM list prices.** Tender/award values are the best real points — need
  the Danish tender documents + AFIF award lists (BOB).

## 6. `grid_connection_tariffs`
dso, customer_category, fee_type (tilslutningsbidrag base / per-A / per-kW /
stikledning), value, unit, effective_from, effective_to, source_url, page,
quote, licence_flag, tag.
- COWI has Radius 2024 (cite-only). Current per-DSO takstblade = BOB
  (Radius/Cerius/N1/TREFOR/Konstant).

## 7. `electricity_tariffs`
component (spot / dso_net_tou / energinet_system / energinet_transmission /
elafgift / supplier_markup), dso_or_body, customer_category, time_band
(Lav/Høj/Spids), value, unit, effective_from, effective_to, source_url, page,
quote, licence_flag, tag.
- Spot = Energi Data Service (open, confirm licence). elafgift = skat.dk
  (open). DSO TOU + Energinet tariffs = current takstblade (BOB; Elindsigt gives
  modelled examples only).

## 8. `cpo_sites`
operator, country, site_name, lat, lon, max_kW, connectors, mcs_flag,
truck_access_flag, booking_flag, opening_date, pilot_or_commercial, source_id,
capture_date, licence_flag, tag.
- EAFO counts (CC BY, open). Site-level: OSM (ODbL/share-alike), DK NAP (if
  open — BOB), operator sites (cite-only). HD-capable list = thin, BOB.

## 9. `cpo_prices`
operator, country, site_or_network, connector, max_kW, price_component (ad-hoc
kWh / per-minute / session / idle-blocking / subscription / roaming-markup /
B2B), value, unit, currency, vat, dynamic_flag, capture_date, source_url,
licence_flag, tag.
- Milence DK/EU = open-to-cite (primary). Car-CPO prices app/terms-restricted
  (cite published pages; many BOB).

## 10. `contracts`
model (CaaS / CPaaS / lease / concession / revenue-share / fixed-offtake /
EaaS), term, hardware_owner, grid_connection_payer, price_basis, indexation,
uptime_sla_pct, response_time, fix_time, penalty, source_doc, section, tag.
- **Mostly BOB** — needs the Danish tender/concession/service-level documents
  (not in repo). AFIR fixes ad-hoc payment + data obligations (open).

## 11. `standards_regulation`
document, clause_or_article, requirement, standard_allows_vs_product,
in_force_date, status (published/draft), source_url, page, quote, licence_flag,
tag.
- Fillable now: AFIR (EUR-Lex, open), OCPP/IEC mapping (cite), MCS IEC/SAE
  scope (paid text — scope only), elafgift law (open).

## 12. `sources_licences`
source_id, publisher, url, licence, commercial_use (yes/no/unclear),
share_alike_flag, attribution_required, doc_date, notes.
- Cross-cuts everything; mirrors `catalogue.csv`.

---

## Which columns can be filled from open, commercially usable sources?

- **Open-commercial (CC BY / EU reuse / gov open):** AFIR articles (EUR-Lex);
  elafgift law + rate (skat.dk); spot price (Energi Data Service — confirm);
  EAFO charger counts (CC BY 4.0); Bundesnetzagentur DE register; MDPI DK price
  study (CC BY). These can live directly in the product.
- **Open but share-alike (copyleft — keep in a separate layer):** OSM (ODbL),
  Open Charge Map (CC BY-SA if confirmed). Usable commercially but a derived DB
  must stay under the same licence.
- **Cite-only (store the value, not the document):** all OEM datasheets (power,
  voltage, current, efficiency, OCPP, ISO 15118, connectors); COWI cost bands;
  Milence prices; CPO published price pages.
- **Paid (scope/preview only):** IEC/SAE/ISO standard text (IEC 61851-23-3, SAE
  J3271, ISO 15118). Store the envelope, never the normative text.
- **No public source (leave empty / BOB):** partial-load efficiency curve,
  standby W, ramp rate, setpoint-response latency, charger MTBF, uptime/fix-time
  SLA values (until Danish tenders are added), eMSP card mark-ups, backend SaaS
  fees, DK NAP price fields (until the NAP is confirmed).
