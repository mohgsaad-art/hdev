# Standards and regulation (pass 1)

Written for Bob. Plain English. Short sentences. Every clause has a source and a
tag. Standards bodies (IEC/SAE/ISO) sell their text, so I quote only public
scope/summary pages and never reproduce paid normative text.

Keep this apart, always: **what a standard allows** (the envelope) vs **what a
product delivers** (the capability). They are different columns in the library.

---

## 1. MCS — Megawatt Charging System (section 3.2)

### Published vs draft as of Nov 2026

- **IEC 61851-23-3:2026 — PUBLISHED.** Edition 1.0, dated **2026-08**. This is
  the IEC standard for the **DC MCS supply equipment**. `[V]` (scope/preview
  pages only; full text is paid).
  - Scope (quoted from the public scope page): applies to EV supply equipment
    with "a rated maximum voltage at side A (supply network side) up to 1 000 V
    AC or up to 1 500 V DC and a rated maximum voltage at side B (EV side) up to
    1 250 V DC." Source: webstore.iec.ch publication 69016; ISBN
    978-2-8327-1438-6 on the ANSI preview. `[V]`
  - So the **standard envelope** on the vehicle side is **1250 V DC**.
- **SAE J3271 — MCS.** The SAE connector/system standard. Public Argonne FAQ
  (2023) describes the envelope: up to **3.75 MW = 3000 A at 1250 V DC**, with a
  440 kW uncooled entry point (350 A / 1250 V), and a >99.99% first-attempt
  startup success target. `[C]` (Argonne FAQ, public). Confirm the current
  J3271 publication status on the SAE catalogue — `[BOB]`.
- **CharIN MCS.** CharIN runs the MCS task force. Its 2025 "MCS 2.0 Standards
  Recommendations" whitepaper recommends **ISO 15118-20 as the sole comms
  protocol** for MCS. `[C]` (whitepaper referenced via search; fetch the
  official CharIN copy — `[BOB]`).

### Standard-allows vs product-delivers

- Standard ceiling: **3.75 MW, 3000 A, 1250 V DC** (`[C]` SAE/Argonne);
  IEC side-B voltage **1250 V DC** (`[V]`).
- Shipping products in the EU (2025-26): **~1.0-1.2 MW** per output.
  Kempower Mega Satellite Flex 1.2 MW MCS (`[C]`), ABB A200/HVC360 1.2 MW
  continuous (`[C]`), Heliox 1 MW shared (`[C]`), Tesla Semi charging ~1.2 MW
  (`[C]`, press). None reach the 3.75 MW ceiling yet.
- Trucks with MCS inlets on sale and public MCS sites in EU/DK: link to the
  **vehicle-side library** (do not duplicate battery data). Public DK MCS:
  Milence opened its first DK HGV hub in 2026 (`[C]`, electrive 2026-06-10);
  site kW/opening detail is `[BOB]`.

---

## 2. OCPP / ISO 15118 / timing (section 3.3)

### OCPP versions (source: Open Charge Alliance; secondary summaries `[C]`)

- **OCPP 1.6 (2015).** JSON over WebSocket; smart-charging profiles
  (`SetChargingProfile`). The de-facto installed base.
- **OCPP 2.0.1 (2020).** Published as **IEC 63584:2024**. Adds device model,
  three security profiles, and **ISO 15118-2 Plug & Charge** support.
- **OCPP 2.1 (2025-01-23).** Published as **IEC 63584-210:2025**. Adds
  **bidirectional charging (V2X)**, DER control, and **ISO 15118-20** support.
- Source: OCA protocols page (authoritative publisher) + codibly/episensor
  summaries. `[C]`. The spec text itself is downloadable from OCA but licensed —
  store the facts, not the PDF.
- **Certification:** which models are OCPP 2.0.1 certified is in the OCA
  Certified Products registry. Not opened — `[BOB]` (`oca_certified`).

### ISO 15118 / Plug & Charge / DIN 70121

- A key **modelling point** carried from the vehicle-side work: the charging
  **power curve is negotiated by the vehicle BMS over ISO 15118**, not fixed by
  the charger. Delivered power = min(charger, vehicle, grid connection).
  `[INFERENCE]`.
- Per-model support (ISO 15118-2 PnC, DIN 70121, ISO 15118-20 readiness) is on
  OEM datasheets — see `charger_specs_extracted.csv`. `[V]` where from a
  datasheet.

### Setpoint-response time and ramp rate — the real gap

- **No public, measured value** for DC-charger ramp rate (kW/s) or for
  backend-setpoint-to-delivered-power latency was found. `[BOB]` + see
  `conflicts.md` Q3.
- What exists are **requirements**, not measurements:
  - OCPP defines the `SetChargingProfile` mechanism (a limit the charger must
    honour); it does not publish a product's physical response time.
  - For grid flexibility, **Energinet** sets prequalification response-time
    requirements per product (FCR, aFRR, mFRR). Those are TSO requirements, not
    charger datasheet behaviour. Fetch the Energinet prequalification docs —
    `[BOB]` (`energinet_prequal`). `[INFERENCE]` FCR typically needs full
    activation within ~30 s; confirm from the primary document, do not treat as
    fact yet.

---

## 3. AFIR — Reg. (EU) 2023/1804 (section 3.7)

Primary: EUR-Lex consolidated text, **CELEX 02023R1804**, consolidation
**in force 2026-01-08** (ELI: data.europa.eu/eli/reg/2023/1804/2026-01-08).
EUR-Lex content is reusable commercially with attribution. `[V]` for substance;
the **exact article/paragraph numbers below are marked to re-confirm against the
consolidated text** — `[BOB-verify]` on the numbering, not the substance.

### Heavy-duty vehicle recharging targets

- HDV recharging **pools** with power output **>= 350 kW** must be deployed
  **every 60 km along the TEN-T core network** and **every 100 km on the TEN-T
  comprehensive network, from 2025**, with full coverage by **2030**. `[V]`
  substance (consilium 2023-07-25; EC IP/23/1867; EUR-Lex summary).
- By **31 Dec 2027**, on **at least half** of the TEN-T comprehensive network,
  each recharging pool must provide **>= 300 kW** and include **at least one
  150 kW** point; over the **entire** comprehensive network by **31 Dec 2030**.
  `[V]` (EUR-Lex summary page).
- (These HDV obligations sit in **Article 4** of AFIR; confirm the exact
  paragraph and any 4a split in the consolidated text — `[BOB-verify]`.)

### Light-duty / general

- For LDV, a power-per-registered-EV target applies: **>= 1.3 kW per registered
  BEV and 0.8 kW per PHEV** (fleet-based), plus **150 kW fast pools every 60 km**
  on TEN-T from 2025. `[V]` (EUR-Lex/UNECE summary). Relevant to M1/N1 sizing.

### Payment, transparency, data

- **Ad-hoc charging without a subscription** and **transparent ad-hoc pricing**
  are required. `[V]` substance.
- **Static and dynamic data** (location, power, connector, availability, price)
  must be made available via the **National Access Point**. `[V]` substance;
  CPO reporting confirmed by Monta `[C]`.
- Per-unit **card/contactless payment** requirements apply above power
  thresholds (AFIR ad-hoc payment rules) — relates to the MID/payment-terminal
  field in `charger_specs_extracted.csv`. `[BOB-verify]` exact article.

### HDV MCS pools (via CEF AFIF funding topic)

- A publicly accessible HDV recharging pool under the CEF AFIF 2026 topic is
  defined as **>= 4 MCS points, each >= 1 MW** (not necessarily simultaneous at
  max). `[V]` (EU Funding & Tenders portal, CEF-T-2026-AFIFGEN-COSTS). AFIF
  **award lists publish per-site budgets** = real cost points — fetch them
  (`[BOB]`, `cef_afif_mcs`).

### Delegated acts / MCS in AFIR Annex II

- Whether a delegated act has added MCS to AFIR's technical-spec annex by Nov
  2026 is **not confirmed**. `[BOB-verify]` against the consolidated Annex II.

---

## 4. The Danish National Access Point for AFIR data (section 3.7, HIGH PRIORITY)

- AFIR **requires** every member state to have a National Access Point and
  requires CPOs to report static + dynamic charge-point data to it. `[V]`
  (AFIR) + `[C]` (Monta confirms it reports on CPOs' behalf).
- **Does a Danish NAP exist, with open prices and a commercial-reuse licence?**
  **Not confirmed in this pass.** DK runs an ITS NAP; whether it publishes the
  full AFIR charge-point dataset (incl. price) openly, under what licence, is
  unverified. This is the single highest-value open-data question. `[BOB]` — see
  `conflicts.md` Q1. Candidate hosts to check: the Danish ITS NAP, Vejdirektoratet,
  Energistyrelsen, and `energidataservice.dk`.

---

## 5. Danish rules (section 3.7)

- **Elafgiftsloven** (electricity-duty law): LBK nr. 1284 of 2023-11-03 with
  later amendments. `[V]` (skat.dk E.A.4.6.1.2). See `tariffs_dk.csv` and
  `conflicts.md` Q5 for the EV-charging refund scheme (extended to 2030).
- **Ladestanderbekendtgoerelse / Ladestanderloven** (EPBD-derived charger
  requirements for buildings): not fetched this pass — `[BOB]` on
  retsinformation.dk.
- **EPBD recast** pre-cabling/charger requirements: relevance to depots is low
  (building-focused) — note only, per brief. `[BOB]` if needed.
- **MID / Germany Eichrecht:** a market constraint for metering/billing hardware
  sold across the EU. Note as a constraint; no DK-specific Eichrecht equivalent.
  `[INFERENCE]`.

---

## Summary table of standards/regulation status

| Document | Clause / envelope | In force / status | Tag |
|---|---|---|---|
| IEC 61851-23-3:2026 | MCS DC EVSE; EV-side <=1250 V DC | Published 2026-08 | V (scope only) |
| SAE J3271 | MCS up to 3.75 MW / 3000 A / 1250 V | Public FAQ 2023; confirm pub status | C / BOB |
| CharIN MCS 2.0 | ISO 15118-20 as sole comms | Whitepaper 2025 | C / BOB |
| OCPP 1.6 | SetChargingProfile smart charging | 2015, installed base | C |
| OCPP 2.0.1 = IEC 63584:2024 | device model, ISO 15118-2 PnC | 2020 / IEC 2024 | C |
| OCPP 2.1 = IEC 63584-210:2025 | V2X, ISO 15118-20 | 2025-01-23 | C |
| AFIR Art. 4 (HDV) | >=350 kW pools 60/100 km from 2025 | In force; consol. 2026-01-08 | V (substance) |
| AFIR comprehensive | >=300 kW/pool + 150 kW pt by 2027/2030 | In force | V |
| CEF AFIF HDV MCS pool | >=4 MCS pts each >=1 MW | 2026 funding topic | V |
| DK NAP (AFIR data) | existence/licence/price fields | UNCONFIRMED | BOB |
| Elafgiftsloven LBK 1284/2023 | EV charging refund to 2030 | In force | V |
