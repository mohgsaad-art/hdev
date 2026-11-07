# Conflicts and open questions (pass 1)

Written for Bob. Plain English. Each of the 10 section-5 questions gets a
verdict or a `[BOB]`. When sources disagree, both are listed; I never pick one
silently.

---

## Q1. Does a Danish AFIR National Access Point exist, with open prices and a commercial-reuse licence?

**Verdict: partly answered. Existence yes (required); open price dataset + licence = `[BOB]`.**

- AFIR **requires** every member state to run a National Access Point and
  requires CPOs to report static (location, power, connector, price) and dynamic
  (availability, status) charge-point data to it. `[V]` (AFIR) + `[C]` (Monta
  confirms it submits this data to NAPs on operators' behalf).
- Whether the **Danish NAP publishes the full charge-point dataset *including
  price* openly, and under a licence that allows commercial reuse**, is
  **unconfirmed**. I could not identify the DK NAP host or its licence this pass.
- `[BOB]` highest priority: confirm the DK NAP URL (candidates: Danish ITS NAP,
  Vejdirektoratet, Energistyrelsen, energidataservice.dk), its fields (does it
  carry price?), and its licence. If it carries prices openly, it is the single
  best source for `cpo_sites` + `cpo_prices` for all of Denmark.

---

## Q2. Which MCS standard documents are published (not draft) as of Nov 2026, and what max current/power?

**Verdict: answered.**

- **IEC 61851-23-3:2026 is PUBLISHED** (Edition 1.0, 2026-08). `[V]` (scope
  page). Envelope: EV-side (side B) **up to 1250 V DC**; supply side up to
  1000 V AC / 1500 V DC.
- **SAE J3271 / CharIN MCS** envelope (public FAQ): **3.75 MW = 3000 A at
  1250 V DC**; 440 kW uncooled entry. `[C]`. Confirm J3271 formal publication
  status on SAE catalogue — `[BOB]`.
- Standard-allows (3.75 MW) vs product-delivers (~1-1.2 MW today) kept apart in
  `charger_specs_extracted.csv`. `[V]`/`[C]`.

---

## Q3. Any public, measured values for charger ramp rate and OCPP setpoint-response time? If not, which standard clauses set requirements?

**Verdict: no measured public values found. Requirements only.**

- Searched OEM datasheets, OCA, and research (JRC/TNO/Fraunhofer/DTU). **No
  public measured DC ramp rate (kW/s) or backend-setpoint-to-power latency**
  surfaced. `[BOB]`.
- Requirements, not measurements, do exist:
  - OCPP `SetChargingProfile` (a limit the charger must honour) — OCA. `[C]`.
  - Energinet ancillary-service prequalification sets response-time
    requirements per product (FCR/aFRR/mFRR). Fetch for exact figures — `[BOB]`.
- Do **not** present any standard/TSO requirement as measured product behaviour.

---

## Q4. A source for charger efficiency at partial load beyond OEM datasheets?

**Verdict: none found this pass.**

- OEM datasheets quote **peak** efficiency only (e.g. >95%, up to 98.2%
  Alpitronic S2). `[V]`/`[C]`. No public **partial-load efficiency curve with
  load points** was found. `[BOB]`: look for JRC/Fraunhofer test reports or
  independent lab measurements.

---

## Q5. Current Danish elafgift treatment for EV charging (reduced rate/refund), and until when?

**Verdict: answered (primary, skat.dk).**

- **General elafgift** base rate was "nedsat til 0,8 øre/kWh fra den 1. januar
  2021" and the government has cut it to the **EU minimum (~0.8 øre/kWh) for
  2026-2027** (down from ~72.7 øre/kWh). `[V]` skat.dk E.A.4.3.6.1 for the 0.8
  øre figure; `[C]` ground.news for the 2026-27 cut (confirm exact scope in the
  finance act). **Important nuance:** with the general rate already near zero in
  2026-27, the special EV refund matters far less in those two years.
- **Special EV-charging refund scheme:** electricity used to **charge registered
  EVs' batteries** gets an elafgift refund; the scheme (sec. 21 of lov nr.
  1353/2012) is temporary and was **extended to 31 December 2030** by lov nr.
  203 of 2021-02-13. `[V]` skat.dk E.A.4.6.1.2. The residual non-refundable
  component is **0.4 øre/kWh**. `[V]` skat.dk.
- Who can claim: liable operators of the charging (business-rules apply);
  confirm exact eligibility and the interaction with the 2026-27 general cut —
  partial `[BOB]`.

---

## Q6. Are COWI's charger cost bands consistent with independent, dated sources?

**Verdict: partly; mostly not independently confirmable yet. Both listed.**

- COWI "Ladestander og eltavle" (DKK, 2024, operator un-named): 22 kW 12,500;
  43.5 kW 120,000; 50 kW 150,000; 80 kW 200,000; 150 kW 400,000; 400 kW 700,000.
  `[C]` (re-read from the file; attribution = "hentet hos en
  ladestanderoperatør i 2024", not named — unverifiable).
- Independent points are **different in scope**, so not a clean comparison:
  - Pass-4 installer bands: DC 150 kW **hardware** $45k-100k; 350 kW **hardware**
    $120k-200k; 300-350 kW **installed** $180k-300k+. `[C]`, US-centric.
  - MDPI DK study: energy prices (0.75 / 3.00 DKK/kWh), not hardware capex. `[C]`.
- They are not directly comparable (DKK hardware-only 2024 vs USD hardware-or-
  installed; different years, VAT status unclear). **Listed both; no judgement
  without a like-for-like independent DK 2024-26 hardware quote** — `[BOB]`.

---

## Q7. Current Radius connection fee per A vs COWI's figure; and Cerius, N1, TREFOR El-net, Konstant?

**Verdict: COWI figure captured; current figures = `[BOB]`.**

- COWI used Radius **first 25 A = 17,950 DKK** and **1,280 DKK per extra A**
  (2024, cited to radiuselnet.dk). `[C]` (re-read from file). Example: 80 A =
  17,950 + 55*1,280 = 88,350 DKK; 650 A = 817,950 DKK. `[D]` (arithmetic
  confirmed against the sheet).
- The rate may have changed since 2024. Re-fetch the **current Radius takstblad**
  and the equivalents for **Cerius, N1, TREFOR El-net, Konstant** — none fetched
  this pass. `[BOB]` (catalogue rows `radius_elnet`, `cerius_tariff`,
  `n1_tariff`, `trefor_tariff`, `konstant_tariff`).

---

## Q8. Public truck charging price in Denmark (Milence and others) per kWh, date-stamped?

**Verdict: answered for Milence (primary).**

- **Milence DK ad-hoc = DKK 2.799/kWh ex VAT**, from 2026-01-01. `[V]`
  (milence.com tariff table, captured 2026-11-06; confirmed by electrive
  2026-06-10). Milence **Charge Card direct = EUR 0.399/kWh ex VAT** (Eurozone).
  `[V]`.
- Other HD-truck public prices in DK: no second confirmed HD operator price this
  pass. Car-CPO prices (edri DC 3.45 / AC 2.65 DKK/kWh; Clever) are app/
  terms-restricted — capture published pages only, `[BOB]`.

---

## Q9. Which Danish public tenders/concessions publish uptime % and fix-time SLAs, and what values?

**Verdict: blocked — documents not in repo.**

- The Danish tender/concession/service-level documents named in the brief
  (`ladestandere-operatoerens-serviceniveau.md`, the Region Hovedstaden tender
  spec, the koncessionskontrakt-udkast, the municipal contracts) are **not in
  the repo**. So no uptime %, response/fix-time or penalty values could be
  extracted this pass. `[BOB]` — add the files; see `contracts_and_sla.md`.

---

## Q10. Licence of Open Charge Map and OSM charging data: usable in a commercial tool, and under what conditions?

**Verdict: OSM answered; OCM to confirm.**

- **OpenStreetMap = ODbL 1.0.** `[V]` (openstreetmap.org/copyright). Commercial
  use **is allowed**, but with two conditions that matter for a commercial
  product: **attribution** to OSM and contributors, and **share-alike** — a
  database you derive from OSM must itself be offered under ODbL. That copyleft
  is the catch for a proprietary dataset.
- **Open Charge Map:** OCM's site states a Creative Commons (CC BY-SA) licence,
  which would carry the **same share-alike** constraint. I could not open the
  OCM licence/API page this pass to confirm the exact version and API terms.
  `[BOB]`.
- `[INFERENCE]` For a commercial EV Scope dataset, prefer sources whose licence
  is permissive without copyleft: **EAFO (CC BY 4.0)**, **EUR-Lex/EC (EU
  reuse)**, **Bundesnetzagentur register (DE public)**, and the **DK NAP** (if it
  turns out open). Use OSM/OCM for discovery/validation, but keep their data in a
  separate, ODbL-compliant layer so the share-alike does not infect the whole
  product.

---

## New conflicts / cautions found this pass

- **Elindsigt tariff numbers are a modelled example, not official rates.** The
  "Din Regning" sheet is a worked Jan-2026 example (net tariff Lav 0.1164 / Høj
  0.3492 / Spids 1.0476 DKK/kWh; systemtarif 0.072; transmission 0.043; elafgift
  0.008). Treat as illustrative `[C]`; verify every value against the current
  DSO takstblad and Energinet/skat.dk before use. Listed with a loud caveat in
  `tariffs_dk.csv`.
- **COWI load factor 0.85 is unsourced.** It appears as the ratio of
  "gennemsnitlig ladeeffekt pr ladesession" to rated power (e.g. 42.5/50,
  340/400 = 0.85 across all kW classes). `[D]` the ratio is 0.85; `[C]` the
  value itself has no source in the file. Do not reuse without a source.
- **Milence site/location/kW for the DK hub** is not captured (price is). `[BOB]`.
