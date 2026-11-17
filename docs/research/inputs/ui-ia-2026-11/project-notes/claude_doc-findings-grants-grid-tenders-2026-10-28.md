# Document findings: DK/DE grants, Radius grid guide, refuse-truck tenders (28 Oct 2026)

What each document requires, and what HDEV must output to serve it. **Verified** = read in the document. **Inference** = my reading, flagged.

## 1. Vejdirektoratet pool 2026 (DK) — ansøgningsvejledning, regnskabsinstruks, templates

Verified:
- Pool closed 30 Sep 2026, 15:00. Max DKK 4m per company/group. First come, first served. Private companies only; public companies and institutions cannot apply.
- Truck purchase grant = % × (ZE price − comparable diesel price). Lease grant = % × (NPV of ZE lease − NPV of diesel lease), excl. operating costs (energy, insurance, maintenance). Lease 12 months–8 years.
- Rates (18 Feb–30 Sep): trucks 50/40/20 % (small/medium/large); depot charging 30/20/5 %; periodically public depot 40/30/10 %.
- "Comparable diesel" must match: use type, legal GVW, motor kW, axle config/body, suspension, cab/options, fixed equipment; best available Euro class.
- NPV template (trucks): up to 8 ZE/diesel pairs, 10 year-rows each. Inputs per vehicle: name, discount rate (applicant's own), year, total cost that year (DKK). Down payment goes in year 1; residual value as an extra year after the lease, same for both. Formula `cost / (1+r)^(1 + year − first_year)` — the **first year is discounted one full period** (worked example: 500,000 / 1.035 = 483,092, r = 3.5 %). Checks: years must match between the pair; NPV() cross-check. Overview tab = NPV difference per pair.
- NPV template (chargers): up to 8 chargers, same inputs (name, rate, year, total cost that year).
- Budget template (depot/destination charging): columns = units, unit price (DKK), total (DKK), note. Rows = staff costs (salary, overhead), external deliveries (4 blank sub-rows), other costs, transport, total budget, grant. Text box: DKK excl. VAT; units and unit prices on every sub-item; must follow the regnskabsinstruks.
- Affiliated-companies template: name, CVR, employees, turnover, balance, partner or linked.
- Depot charging eligible costs: construction, installation, upgrade; internal salary (1,649 h/yr norm) + 18 % overhead; transport; equipment incl. **buffer batteries**; civil works; **grid connection**; **external services e.g. consultancy** (4.4.7); leasing/subscription of chargers up to 8 years as NPV. Not eligible: refundable VAT, interest, commissions; costs incurred before the application is received (4.1).
- Depot application form asks for: **how many trucks will charge daily, number of chargers and their power**, total budget excl. VAT, lease yes/no and term.
- Final report: location, number of chargers and power; management-approved accounts vs budget; auditor statement if depot grant ≥ DKK 500,000. Projects granted in 2026 must report by 31 Dec 2028.
- Pool status (VD page, 7 Sep 2026): DKK 197.3m to 165 projects; DKK 43.1m left.

Inference:
- The DK grant needs **price quotes, not physics**. HDEV's value here is sizing (chargers, kW, grid connection, buffer battery) that becomes the depot budget lines, and the buy/lease/diesel comparison.
- Consultancy is eligible in depot projects, but only if ordered after the application is received. A pre-application feasibility study is likely not fundable; post-application design work may be.
- HDEV's NPV must use VD's convention (discount year 1) or its numbers won't match the template.
- A 2027 round is not confirmed in these documents.

## 2. Radius / Cerius-Radius — "Sæt strøm til den tunge transport" (2025)

Verified:
- Radius lists the pre-work it wants, "possibly with a consultant": driving patterns and fleet; existing supply capacity; own installation ratings (service cable, main/sub boards); number and placement of chargers; charger types; optimal charging patterns; effect of connection fee and tariffs on the business case in different connection scenarios.
- Indicative screening needs: address, desired power (leveringsomfang), connection type (FNA/BNA), desired commissioning date, whether system services will be delivered (and which).
- Products: **FNA** (full access, one-off connection fee), **BNA** (limited access, 10/30/50 kV, pay actual cost only, curtailable, much cheaper), **TFL** (stepwise full access while grid is built). Can scale up, not down.
- Capacity cannot be reserved before a signed connection agreement; first come, first served.
- Tariff: customers at 10 kV and above (A-høj, A-lav, B-høj) pay a monthly **capacity charge based on the average of the 10 most loaded hours over the last 12 months**, plus a lower kWh tariff.
- Connection times: free capacity 12–18 months; no free capacity 2–4 years; Energinet must expand: ≥5 years not unusual. Process applies to installations > 125 kW.
- Worked examples (incl. VAT): 1×50 kW → 35 A ≈ DKK 62,000 (C-customer); 5×50 kW → 175 A ≈ DKK 300,000 (B-lav); 3×1 MW + 6×50 kW → 3 MW requested (below nameplate) ≈ DKK 4.8m FNA (A-lav).

Inference:
- Radius's pre-work list is HDEV's scope almost line by line.
- The top-10-hours capacity charge makes peak shaving directly priceable from a charging schedule.
- Example #3 (3 MW instead of nameplate) is a coincidence-factor decision HDEV should justify.

## 3. Germany — BMV Förderrichtlinie Ladeinfrastruktur für e-Lkw (BAnz 15.05.2026), Call A webinar, PtJ evaluation (5 Aug 2026)

Verified:
- Funds DC CCS/MCS charging for N2/N3, min. one charge point ≥ 50 kW; grid connection; load/energy management; **battery storage only if technically necessary**.
- **Planning and permitting costs are not eligible.** Leasing/rent and operating costs not eligible.
- Call A (SME, non-public): fixed **€500 per kW installed**; de minimis max €300,000, or AGVO max €1m per application. Before applying: confirm the existing grid connection is large enough, or file a connection request. Earmarking 24 months. Closed the same day (~430 applications, ~€150m).
- Call B (competitive): ranked on **€ requested per kW**; ~1,050 applications, ~€67m available; cut-off ≈ €230/kW. Ties: higher kW ranks better.
- Call C (public): 70 % €/kW (62 €/kW = 70 pts, 500 €/kW = 0) + 20 % AFIR site + 10 % Durchleitungsmodell; cut-off 58.145 pts.
- More calls announced; €1bn over 2026–2029.

Inference:
- kW sizing directly sets bid competitiveness. "Technically necessary" BESS needs a grid-limited simulation as evidence. "Is the existing connection big enough?" is a mandatory pre-check.

## 4. Ressourceindsamling A/S — Kontrakt, el-renovationsbiler

Verified:
- 10 electric 3-axle 2-chamber refuse trucks + options; 10-year service covering vehicle, chargers and batteries up to 30,000 km/year.
- Bidder states **usable battery capacity after 8 years** (Bilag 1, krav 11.8); battery replaced free if lower. Third-party ohm measurement.
- Delivery test must prove the spec. Downtime beyond 5 days/year/truck → loan vehicle or DKK 2,000/truck/day.
- Bilag 1 kravspecifikation not public in the contract file.

## 5. Rambøll for Forsyningstilsynet — Udbud i affaldssektoren (Feb 2025)

Verified:
- Six firms won 71 % of primary household contracts (Verdis 28 %, Meldgaard 21 %, Remondis 9 %, Marius Pedersen 6 %, City Container CPH 4 %, Lemvig Beton 4 %).
- Fuel requirement visible in notices: 3 % required, 13 % option, 84 % unknown. Trend: minimum share of collections electric + compete on higher share.
- Average contract length rising (6.7 years for 2024 starts).

Inference:
- The renovatør bidding is also a buyer: "what share of my collections can run electric" is bid-critical.

## 6. Tender requirements found (public notices / Klagenævnet)

Verified (full kravspecs sit behind tender portals; not downloaded):
- **ARC, 13 × 2-axle 1-chamber electric (Klagenævnet J.nr. 22/00081, 2 Feb 2022):** min. 150 kWh total battery; min. 105 kWh available; max. 25 % loss in first 8 years; charge monitoring with SMS alerts. Weights: price 60, quality 15, service 15, battery 10 (over-fulfilment scored 0–5, linear). No range, consumption or charging-power requirement in the quoted text.
- **ARC 2025, 14 × 3-axle electric:** price 40, quality 25, battery 10, service (not shown). Awarded Scania, DKK 122.6m. Docs: ethics.dk publicMaterial 07693cb8-e0d8-4e7d-ada0-a9a40ab546f2.
- **Ressourceindsamling 2025, 6 electric crane trucks (ref. 568354):** battery capacity 25, charging speed 15, load capacity 10, price 15. Awarded Scania DKK 66.5m. Comdia lists "Bilag 1 - kravspecifikation (01.10.2025).xlsx".
- **Thy Recycle 2026, 7 × 3-axle electric + chargers:** price 60, **range 20**, response time. Awarded Ejner Hessel DKK 31.5m (one bid). Docs: Mercell 277398419. Buyer advisor: COWI.
- **Frederiksberg 2026, 2 refuse + 2 × 10 t electric:** price 60, evaluation parameters 25, delivery 15. Docs offline from buyer.
- **Copenhagen green transport requirements:** e.g. "at least 40 % of trips with green vehicles", step model >30/50/60/70 %, fines per km/route of underperformance, route lists as documentation.

Inference:
- Buyers score battery capacity, charging speed and range as **declared spec numbers, not route-verified**. HDEV's gap: does the declared (and 8-year) capacity cover these routes in winter with compactor load.

## 7. EEA HDV dataset

Verified:
- Table definition (extract 2024-03-22): ZEV flags, axle config, curb mass, CdxA range, tyre RRC, per-mission CO2/fuel incl. MUL/MUR (municipal utility). **No** electric energy, battery or range fields.
- Latest release found: reporting period 1 Jul 2023–30 Jun 2024, published 18 Jul 2025. Schema not checkable from here (download blocked).

Inference:
- Use as diesel baseline. Whether the 2023–24 release adds ZEV energy fields is **unverified** — check its CSV header.

## Outputs HDEV must produce

| Output | Needed by | Status |
|---|---|---|
| Required grid power, FNA vs BNA | Radius screening, DE pre-check | Not built (needs charging schedule) |
| Top-10-hours average peak, with/without smart charging | Radius tariff | Not built |
| Chargers: count, kW; trucks charging per day | DK form, DE €/kW | Not built |
| Buffer battery "technically necessary" case | DE eligibility, DK budget | Not built |
| NPV per VD convention | DK templates | Not built (simple) |
| Share of routes/collections feasible on BEV | Waste tenders | Core consumption engine exists |
| Range check at 8-year usable capacity, winter | Refuse-truck tenders | Not built (degradation) |
| Diesel baseline CO2/fuel | Grants, CO2 | EEA MUL/MUR identified |
