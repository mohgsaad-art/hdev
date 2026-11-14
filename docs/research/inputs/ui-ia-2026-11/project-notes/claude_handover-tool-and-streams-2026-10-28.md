# EV Scope: tool description and revenue/value streams (handover, 28 Oct 2026)

Prepared for Bob, to give another AI enough context to generate new business-model ideas.

**How to read this file**
- **[VERIFIED]** = read in a named source document or web page during research (Oct 2026).
- **[JUDGEMENT]** = Claude's own assessment, not from a source.
- **[BUILT] / [IN PROGRESS] / [PLANNED]** = status of a tool feature.
- Numbers are only given where a source states them.

**Suggested prompt for the new AI:**
> Read this file. Using the tool description in Part 1, the market facts in Part 2 and the constraints in Part 4, propose new revenue and value streams that are not already listed in Part 3. For each: who pays, what they get in return, what the tool must be able to do, what outside condition it depends on, and a cheap way to test it. Flag every assumption. Prefer streams that do not depend on the same outside conditions as the top-ranked existing streams.

---

## Part 1. The tool (what it is, not the business)

### 1.1 Purpose
- A physics-based simulation tool that sizes and plans the electrification of **heavy-duty vehicle fleets and their depots** (refuse trucks, distribution trucks, crane trucks, and later vans, buses and cars).
- It answers, for a given fleet and its real routes:
  - can each route be driven electrically?
  - what battery size does each truck need?
  - what chargers are needed, and how many?
  - how much grid connection does the depot need?
  - what flexibility can the depot offer the grid?
  - what does it cost compared with diesel, and how much CO₂ does it save?
- Positioning goal: **"PVsyst for EVs"**. PVsyst is the solar simulation tool that lenders and independent engineers accept by name, because every loss is listed and auditable. EV Scope aims to be the auditable, brand-neutral standard report for vehicle electrification.
- Working name: **"EV Scope"** (used in a demo). An alternative name, "EVsyst", is undecided; don't use it yet.
- Planned brand mark: "EV" written like a parking sign, in parking-sign blue.

### 1.2 Core design principles
- **Traceable to EU VECTO.** VECTO is the EU's official simulation tool for certifying heavy-duty vehicle CO₂ and energy use (Regulation (EU) 2017/2400). The engine follows VECTO's physics and parameters. Where data is missing, defaults reduce back to VECTO standard values.
- **Validated against more than VECTO.** Results are checked against independent tests, studies and OEM spec-sheet figures, showing how far HDEV and each source differ. Matching VECTO alone is not counted as validation.
- **Conservative.** The tool must not underestimate energy use. Where uncertain, it picks the conservative option (e.g. models cold-weather cabin heating instead of VECTO's constant value).
- **Pure, parameterised physics.** Every engine function takes all coefficients as arguments, with nothing hard-coded, so it works for any country and every value is editable. Standard values live in a separate defaults layer.
- **Brand-agnostic.** The analysis is vendor-neutral. Reports can be flagged brand-agnostic (e.g. for municipalities and public tenders).
- **Modular.** Any stage can run on its own: only charging, only flexibility, only TCO, or TCO plus flexibility, without starting from consumption.
- **No hard-to-get inputs.** The tool avoids features that need inputs users can't realistically supply, and derives them from data already asked for.
- **Logic in Python.** All physics and resolver logic is in Python. The UI is a form that sends raw JSON.

### 1.3 Simulation pipeline (in order)
1. **Input layer.** Four input paths emit the same internal route format:
   - typed entry (distance, stops, dwell time);
   - VECTO standard driving cycles (VDRI files, e.g. urban delivery, regional delivery, municipal utility/refuse);
   - telemetry/GPS upload;
   - an AI adapter that turns messy data (coordinates, descriptions, dumps) into routes. [PLANNED]

   Defaults: dwell 45 min per stop; speeds 30/50/80 km/h for deep urban / urban / non-urban; gradient flat; payload = VECTO reference payload. [BUILT, design locked]
2. **Payload engine.** Payload changes at stops (constant, linear or custom). It is editable per stop. [BUILT]
3. **Crosswind engine.** Effective air-drag area by speed, using VECTO's crosswind method. Uses Danish wind data from DMI (v_ref 5.028 m/s at 10 m) instead of VECTO's default. [BUILT, matches VECTO's Excel]
4. **Driver model.** Second-by-second speed profile from VECTO's kinematic driver: acceleration, deceleration, look-ahead coasting, overspeed. [IN PROGRESS, full rewrite]
5. **Force engine.** Wheel power from mass, rolling resistance, grade, rotating inertia and air drag. It is split so any weather or payload scenario is a cheap multiply-add per row. [BUILT]
6. **Consumption engine.** Wheel power → battery power, through drivetrain losses and regen limits. Adds auxiliaries:
   - electric system, pneumatics, steering pump (VECTO models);
   - HVAC and battery conditioning (VECTO lookup, or a thermal model from weather) [thermal model IN PROGRESS];
   - PTO (power take-off: compactor or crane hydraulics), either at stops using VECTO's power profile or always on.

   Drivetrain is moving from fixed efficiencies to EU standard-value loss formulas (gearbox, axle, motor). [IN PROGRESS] Battery losses (VECTO OCV + Ri model) are [PLANNED]; today the battery is treated as 100% efficient.
7. **Charging engine.**
   - Sizing mode: minimum power = energy / available time.
   - Simulation mode: per-timestep battery model (VECTO OCV + Ri), with time step as an argument (finer than 5 min, because some grid-service products need it).
   - Strategies: just-in-time (JIT), as-soon-as-possible (ASAP), earliest-deadline-first (EDF) / ES allocation, and cheapest-first planned.

   [PLANNED; the old model is deprecated]
8. **Grid / depot layer.** Depot peak, coincidence factor, connection size. Building base load from Eloverblik (the Danish metering-data portal) via the customer's login (MitID). [PLANNED]
9. **Flexibility.** Up/down flexibility per hour, limited by battery energy and the next morning's readiness. Energy-neutral (any shifted energy is recovered within the charging window). From Bob's DTU MSc thesis on EV depot charging flexibility in Denmark's DK2 price zone. [Thesis work exists; tool integration PLANNED]
10. **Cost and CO₂.** TCO versus diesel, NPV, financing, residual value, electricity price split (spot, grid tariff, tax), sensitivity, and CO₂ (including a falling grid emission factor). It will port logic from a COWI truck TCO spreadsheet. [PLANNED]
11. **Optimiser.** An electrification planning optimiser. [PLANNED, last]

### 1.4 Year simulation
Every operating day of the year is simulated directly, with weather per day. The driver model runs once per vehicle and route, and weather and payload scenarios reuse it cheaply. [DESIGNED]

### 1.5 Outputs (current UI mock-up, mostly placeholder numbers)
- **Overview:** verdict, key figures, feasibility checks, fleet day Gantt chart.
- **Energy:** energy split (driving / bin lifts / on-board systems), year heatmap, by month.
- **Charging:** battery state through the hardest day, fleet charging schedule, strategies compared.
- **Grid:** depot power on the hardest day, load-duration curve, flexibility.
- **Cost:** cumulative cost, electric vs diesel, breakdown.
- **CO₂:** per year, saved over time.
- **Vehicles:** each truck's hardest day, range through the year.

**Known output gaps** (from a gap analysis against VECTO outputs, PVsyst reports and Danish tenders):
- a full component energy balance (air, rolling, grade, inertia, brakes, gearbox, axle, motor, battery, each auxiliary);
- a monthly balance table;
- a loss diagram;
- P50/P90 for the hardest day;
- end-of-life check (does the hardest day still fit at the guaranteed battery capacity in year 8?);
- connection size in amperes and its cost, plus lead time;
- fleet growth phases;
- a per-session charging table;
- robustness cases (one charger down, late return, cold week);
- which grid-service products the fleet qualifies for;
- a year-by-year cash flow;
- an audit block (engine version, input hash, every standard value used with its source);
- an "offer sheet" that compares several OEM bids on the same routes using the buyer's own scoring weights.

### 1.6 Planned two-sided input split
- **Owner side** (fleet operator or public buyer): operations, routes, depot, grid limits. These are fixed.
- **Supplier side** (OEM, dealer, charger maker, CPO): exact spec-sheet values plugged into the same simulation. Examples: battery usable capacity, charging power and ramp, motor, OCPP, prices.
- The purpose: bidders prove their product fits the buyer's real operation, on the same engine.

### 1.7 Vehicle / charger spec library [PLANNED]
- A database of vehicle and charger specs, built from spec sheets and open databases. Standard values fill gaps.
- Users can size from scratch, pick a model from the library, or size first and then find matching models.
- Seen as a major unique selling point (a "MyFitnessPal" analogy: the value is in the database).
- **Open data source:** the EEA heavy-duty vehicle CO₂ monitoring dataset, reporting period 2024–2025.
  - [VERIFIED] Licence: CC-BY 4.0. It includes a battery table with, per vehicle, total kWh, usable kWh in simulation, nominal voltage and certification method (8,020 vehicles, 35,021 pack rows).
  - 3,410 pack rows are "Measured" and 31,611 are VECTO "Standard values".
  - Vehicle IDs are hashed VINs. Make and model sit in a separate vehicle table that has not been processed yet.
- **Not used:** Chargepoly's data hub. It is free to view, but no reuse licence was found, so it isn't copied.

### 1.8 Tech stack
- Python engine with dataclasses and NumPy. FastAPI backend planned. Runs locally with a project JSON for now.
- Step-by-step web UI with collapsible inputs, separate output pages and a Run button. The look should be a serious industry tool, not a gimmick.
- AI assistant planned to fill inputs from messy data.
- VECTO C# source is used as the audit reference.

### 1.9 Current status
- The engine is mid-rebuild (correctness first), and consumption is being validated against VECTO results and OEM figures.
- Charging, grid, flexibility, cost and CO₂ engines are designed but not yet coded.
- Solo founder (Bob, DTU MSc Sustainable Energy / Electric Energy Systems, Copenhagen). He builds the code himself.
- No paying customers yet. The tool is kept private until hosting is funded.

---

## Part 2. Market facts gathered (Denmark first, then EU)

### 2.1 Grid connection (Radius / Cerius, DSO for most of Zealand) [VERIFIED: "Sæt strøm til den tunge transport", 2025]
- **Radius's pre-work list.** Radius asks fleets to do this "possibly together with a consultant":
  - driving patterns and fleet;
  - existing supply capacity;
  - ratings of the site's own installation;
  - number and placement of chargers;
  - charger types;
  - optimal charging patterns;
  - effect of connection fees and tariffs on the business case.
- **Screening fields:** address, desired power, connection type, commissioning date, and whether grid services will be sold.
- **Connection products:**
  - Full access (FNA): one-off connection fee.
  - Limited access (BNA): pay actual cost only; cheaper, but can be curtailed.
  - Stepwise (TFL): full access delivered in steps while the grid is built.
- You can scale up, not down. Capacity can't be reserved before a signed agreement.
- **Capacity charge:** customers at 10 kV and above pay a monthly charge based on the average of their 10 most loaded hours in the last 12 months.
- **Timelines:** 12–18 months with free capacity; 2–4 years without; 5+ years if Energinet (the Danish TSO) must expand.
- **Worked examples (incl. VAT):**
  - 35 A ≈ DKK 62k;
  - 175 A ≈ DKK 300k;
  - 3 MW full access ≈ DKK 4.8m. In this example the customer requested 3 MW, below the chargers' nameplate rating.

### 2.2 Danish grant pool for heavy transport (Vejdirektoratet 2026) [VERIFIED]
- Covers ZE truck purchase or lease (the extra cost versus a comparable diesel) and depot charging. Max DKK 4m per company. First come, first served. Private companies only.
- **Rates:**
  - trucks 50/40/20% (small/medium/large companies);
  - depot charging 30/20/5%;
  - publicly accessible part-time depot charging 40/30/10%.
- **Templates:**
  - Budget template: units, unit price, total. Lines: staff, overhead, external deliveries, other, transport.
  - Lease NPV template: ZE vs diesel pairs; the first year is discounted one period.
  - Charger NPV template.
- Eligible depot costs include buffer batteries, grid connection and consultancy. Costs incurred before the application is received are not eligible. Commissions are not eligible.
- **Application form** asks: how many trucks charge daily, and the number and power of chargers.
- **Status:** the pool closed 30 Sep 2026. By 7 Sep 2026, DKK 197.3m had gone to 165 projects. In the 7 Sep round, 38 of the 59 trucks were leased. A 2027 round is not confirmed.

### 2.3 German BMV e-truck charging programme (2026–2029, €1bn) [VERIFIED]
- **Call A (SMEs):** €500 per kW installed. Before applying, the applicant must confirm the grid connection is sufficient. Used up the same day.
- **Call B (all companies):** ranked by € requested per kW; cut-off about €230/kW. Oversubscribed about 6×.
- **Call C (public charging):** scored on €/kW plus AFIR site plus Durchleitungsmodell.
- Battery storage is funded only if technically necessary. Planning costs are not eligible.

### 2.4 Refuse-truck tenders (Danish public buyers) [VERIFIED]
- **Ressourceindsamling, 6 electric crane trucks (2025):**
  - minimum 250 kWh usable, ≥80% left after 8 years;
  - ≥150 kW charging between 10% and 75% charge, CCS2;
  - crane and compactor must run at the same time at full speed;
  - minimum 5.8 t load;
  - after servicing, the truck must be at 80% by 06:00;
  - workshop within 15 km "because of limited range";
  - **no range or consumption requirement.**
- **Scoring (linear):**

  | Criterion | 1 point at | 10 points at | Weight |
  |---|---|---|---|
  | Battery | 250 kWh | ≥450 kWh | 25% |
  | Charging power | 150 kW | ≥350 kW | 15% |
  | Load | 5.8 t | ≥9.5 t | 15% / 10% (document inconsistent) |
  | Price | +50% vs cheapest | cheapest | 15% |
  | Length, axle function, cab entry height | | | 10% each |

  Awarded to Scania, DKK 66.5m.
- **Ressourceindsamling, 10 refuse trucks (contract):** 10-year service up to 30,000 km/year. The bidder states usable battery capacity after 8 years, and the battery is replaced free if lower. Downtime beyond 5 days/year means a loan truck or a DKK 2,000/truck/day fine.
- **Other tenders:**
  - ARC (Amager Ressourcecenter) 2025: 14 electric trucks, battery weighted 10%, DKK 122.6m.
  - Thy Recycle 2026: range weighted 20%; COWI advised; one bid.
  - Frederiksberg 2026: price 60 / technical 25 / delivery 15.
  - ARC 2022 required SMS alerts if a truck isn't charging at a set time.
- **Who wins household collection contracts** (Rambøll for Forsyningstilsynet, Feb 2025): six firms win 71% (Verdis 28%, Meldgaard 21%, Remondis 9%, Marius Pedersen 6%, City Container CPH 4%, Lemvig Beton 4%).
- 87% of contracts with private collection firms have penalty systems.
- Tenders increasingly require a minimum share of collections done electrically, and bidders compete on a higher share. Contract lengths are rising (6.7 years average for 2024 starts).

### 2.5 Finance and insurance [VERIFIED unless marked]
- Residual value, not range, is now named the main financing risk for e-trucks (Vertelo CEO, ICCT panel, Sep 2026).
- **Candidate Danish lessors** [JUDGEMENT: not confirmed as e-truck lenders]: Nordania (Danske Bank), Jyske Finans, Volvo Financial Services (VFS Denmark), Scania and Daimler Truck finance arms.
- **Insurers:**
  - Munich Re sells an "E-Mobility Warranty Cover", aimed at manufacturers and suppliers.
  - TWAICE (battery analytics) has its accuracy guarantee underwritten by a Munich Re subsidiary.
  - Aviloo sells battery tests plus insurance-backed warranties for used EVs.

### 2.6 Analogues (other companies' models) [VERIFIED]
- **PVsyst:** sold as per-seat licences; lenders and independent engineers ask for its report by name.
- **EnergySage:** marketplace, free for shoppers; vetted providers pay; built with US DOE funding.
- **Geotab EVSA:** EV suitability sold as a telematics marketplace add-in.
- **Pearl Street:** grid study software for utilities and developers, acquired by Enverus in 2025.
- **Zeem:** EV fleet-as-a-service, backed by infrastructure capital.

### 2.7 Other context
- **Energinet:** paused new connection agreements (2 Mar 2026), then lifted the pause (3 Jun 2026). Grid-friendliness is stated as a queue prioritisation criterion.
- **DataHub 3.0** (live 18 Sep 2026): 15-minute metering, independent aggregators, third-party data access with customer consent.
- **Energinet grid-service minimum bids:** FCR-D 0.1 MW, FCR-N 0.1 MW, mFRR 1 MW. [JUDGEMENT] A small depot (e.g. 6 trucks × 40 kW = 240 kW) needs an aggregator.

---

## Part 3. Revenue and value streams, ranked best to worst

**Ranking criteria [JUDGEMENT]:**
- time to first money;
- size of the payer pool;
- dependency on outside conditions;
- how much of it the tool can already do;
- defensibility.

Stream types: **Revenue**, **Value** (credibility, distribution or data, not direct cash), **Moat** (compounds over time), **Funding**.

### Tier A: strongest

1. **Route-verified requirement specs for public buyers** (Revenue)
   - What: waste companies and municipalities get tender requirements checked against their real routes, winter and year-8 battery, instead of "min. 250 kWh".
   - Who pays: ARC, Ressourceindsamling, Renovest, Nordværk and similar, or their technical advisors.
   - Why top: real tender documents show the gap (no range or route check). It uses the consumption engine, which is the most advanced part, and tenders recur.
   - Depends on: electric tenders continuing.
2. **Bid support for collection firms** (Revenue)
   - What: "what share of my collections can run electric, with this depot" for each municipal bid.
   - Who pays: the six firms that win 71% of contracts, plus smaller ones.
   - Depends on: tenders.
3. **Fixed-price analysis packs for fleets** (Revenue)
   - What: a grid pack (Radius screening fields, connection size, full vs limited access), a grant pack, and a TCO / buy-vs-lease pack.
   - Needs: the charging and grid engines.
   - Depends on: grid queue pain; grants for the grant pack.
4. **DSO dialogue pack via Radius and Green Power Denmark** (Value)
   - What: a standard intake format DSOs would welcome. Radius's own guide invites consultant pre-work, and its contact is markedsdialog@cerius-radius.dk.
   - Value: format lock-in and credibility. It's free and fast.
5. **Engineering consultancy licences** (Revenue)
   - What: COWI- or Rambøll-type advisors who run tenders use the tool instead of competing with it.
6. **"Morning readiness" service** (Revenue, recurring)
   - What:
     - plan each night's charging so every truck reaches the charge its first route needs;
     - alert early overnight if a truck isn't charging;
     - keep an independent evidence log of why a truck wasn't ready (grid curtailment, charger fault, truck fault, late plug-in, workshop).
   - Who pays: everyone who can be liable.
     - Collection firms pay municipal fines (penalties are in 87% of private contracts).
     - Truck suppliers pay DKK 2,000/day downtime fines.
     - Workshops must return trucks at 80% by 06:00.
     - Charger suppliers carry uptime.
     - Depot owners on limited access carry curtailment.
   - Needs: the charging engine plus live charger/telematics data. Paid monthly per truck.

### Tier B: good, but needs more built or has a narrower market

7. **Success fee for limited-access (BNA) readiness** (Revenue)
   - What: prove a depot can live with curtailable access, and take a share of the full-access fee it avoids (Radius example: 3 MW full access ≈ DKK 4.8m).
   - Not grant-eligible, because commissions aren't. [JUDGEMENT] Whether clients accept success fees is unverified.
8. **Bid score optimiser for OEMs and dealers** (Revenue)
   - What: choose the battery size that maximises total tender score (battery vs load vs price) and still covers the routes.
   - Who pays: Scania, Volvo, Hessel, Phoenix and similar.
9. **Tool licences for electrical installers** (Revenue)
   - Who: Elento and similar installers.
10. **Calibrated consumption data** (Moat)
    - What: real kWh/km per model, duty cycle, temperature and payload, from every project.
11. **Tender requirements library** (Moat)
    - What: structured public tender specs and scoring rules. Feeds streams 1, 2 and 8.
12. **Public vehicle catalogue from EEA CC-BY data** (Value)
    - What: SEO, trust and top of the funnel.
13. **Grant pack / Vejdirektoratet format** (Value + Revenue)
    - What: pre-fill VD's templates and ask VD to accept the format (not to endorse).
    - Depends on: the pool being renewed.
14. **German €/kW grant check** (Value + Revenue)
    - What: kW sizing plus the mandatory "is my connection enough?" check.
15. **Delivery test and 8-year battery verification** (Revenue)
    - What: independent checks over the 8–10 year service period.
16. **Bankable feasibility report (the PVsyst model)** (Revenue)
    - What: a report lenders' technical advisors accept. Needs the audit block and validation evidence first.
17. **Lite dashboard subscription** (Revenue)
    - What: a view-only dashboard that keeps fleet data current for the next tender. Draft price in Bob's canvas: ~DKK 399/month.
18. **Innovation grants** (Funding)
    - What: EUDP, Innobooster, Horizon Europe, DTU Skylab. Deadlines and eligibility not checked.

### Tier C: later, speculative, or small

19. **E-truck residual value and battery-health index** (Revenue)
    - Who pays: lessors and banks.
    - Needs: a degradation model (not built). The Danish market alone is probably small; EU-wide is better.
20. **Telematics / TMS marketplace add-in** (Value + Revenue)
    - What: distribution where the route data lives (Geotab-style marketplace, DORA TMS).
    - Risk: Geotab already has its own EV tool for lighter vehicles.
21. **Depot load forecasts for DSOs and Energinet** (Revenue)
    - Needs: many projects and client consent.
22. **Aggregator referral / flexibility revenue share** (Revenue)
    - Limit: small depots sit below grid-service minimum bids.
23. **Municipal fleet transition plans** (Revenue)
24. **Dealer pre-sales fit check** and **white-label sizing widget for charger makers** (Revenue)
25. **Verified / sponsored listings in the catalogue** (Revenue)
    - Must be labelled and never affect brand-agnostic reports. Possible credibility tension.
26. **Training and certification** for analysts (Revenue)
27. **Quarterly Danish heavy-EV charging index** (Value)
    - What: press, DSO and investor attention.
28. **Insurance-backed prediction guarantee** (Value)
    - What: an insurer stands behind "this fleet covers these routes".
    - Needs: validation evidence. The partner would be a specialist like Munich Re, not a Danish retail insurer.
29. **Underwriting engine for per-km / as-a-service providers** (Revenue)
    - No Danish provider has been found yet.
30. **Referral to impartial consultancy** and a **DTU validation partnership** (Value)

### Dependency spread [JUDGEMENT]
- Streams leaning on **electric tenders**: 1, 2, 8, 11, 15.
- On **grid queue pain**: 3, 4, 7, 21.
- On **grant schemes**: 3 (part), 13, 14, 18.
- On **data access / partners**: 10, 20, 21, 22.
- On **finance / insurance markets**: 16, 19, 28, 29.
- With **no outside dependency**: 6 (partly), 30.
- The tenders-plus-grid base is the strongest, because the two don't depend on each other.

---

## Part 4. Constraints and preferences for any new idea

- **Brand-neutral analysis is the core promise.** Paid supplier placement must never influence brand-agnostic reports.
- **The platform is a facilitator, not a competitor.** It should be a marketplace on EU rules and standards that fleet owners, OEMs/bidders, installers and buyers all use.
- **Protect the method.** Show outputs, not how the engine works, to partners. Code and IP stay in Bob's own entity. No employment by a partner (Danish IP rules, and DTU Skylab grant eligibility).
- **Ethics and data:** no reverse-engineering competitor tools, and no copying databases without a reuse licence.
- **Market order:** Denmark first, as the reference market. Then Germany (biggest pain plus money), then the Netherlands (grid congestion), with the UK last (Dynamon is the incumbent there). Denmark alone is seen as too small.
- **Competitors:**
  - The real incumbent in Denmark is Excel and OEM spreadsheets.
  - Foreign tools: Dynamon (UK) is treated as the blueprint to beat on tech and ease of use, not on price. Others: ChargeSim, BetterFleet, Flowemo, Decade Energy, Chargepoly.
  - OEMs (Volvo, Scania) run their own route simulations when quoting.
- **Partnership history:** a consulting partnership with a Danish electrical installer did not work out (Oct 2026). Relationships are kept neutral, and referrals are still welcome.
- **Capacity:** Bob is a solo founder with no outside funding. He prefers ideas that reuse one engine and one project file across many payers.

---

## Part 5. Open questions worth exploring

1. Who in Denmark carries e-truck residual value risk today, and how do they set it?
2. Would a DSO formally accept or recommend a standard intake format?
3. Will Vejdirektoratet run a 2027 pool, and in what form?
4. What do Danish collection contracts fine per missed route?
5. Which Danish or Nordic per-km or as-a-service e-truck providers exist?
6. Which telematics systems do Danish hauliers and collection firms actually use?
7. Can the same engine serve vans, buses and cars to widen the market, and who pays there?

**Sources** (all accessed Oct 2026):
- [Radius: "Sæt strøm til den tunge transport" (2025)](https://radiuselnet.dk/wp-content/uploads/Saet-stroem-til-den-tunge-transport_2025-1.pdf)
- Vejdirektoratet pool 2026 documents: ansøgningsvejledning, regnskabsinstruks, budget and NPV templates, pool page
- [BMV Förderrichtlinie (BAnz 15.05.2026) and PtJ evaluation of applications (5 Aug 2026)](https://www.ptj.de/foerdermoeglichkeiten/ladeinfrastruktur-fuer-schwere-nutzfahrzeuge)
- Ressourceindsamling: Bilag 1 kravspecifikation, udbudsbetingelser and tilbudsliste (Oct 2025); Kontrakt el-renovationsbiler
- [Rambøll for Forsyningstilsynet: "Udbud i affaldssektoren" (Feb 2025)](https://forsyningstilsynet.dk/Media/638840266189276238/Udbud%20i%20affaldssektoren_Analyserapport_inkl%20h%C3%B8ringsnotat.pdf)
- [Klagenævnet for Udbud, J.nr. 22/00081 (ARC)](https://klfu.naevneneshus.dk/media/documents/Volvo_Danmark_AS_mod_IS_Amager_Ressourcecenter.pdf)
- [openprocurements.com: Danish refuse-truck tender listings](https://dk.openprocurements.com/cpv/34144512/)
- [EEA HDV CO₂ monitoring 2024–2025 (CC-BY 4.0)](https://doi.org/10.2909/1e44df1d-6a56-41e4-9d67-aeae0ab909c9)
- [Vertelo / ICCT panel on residual value (Autocar Professional, Sep 2026)](https://www.autocarpro.in/news/residual-value-not-range-emerging-as-key-risk-for-electric-trucks-vertelo-134419)
- [Munich Re: enabling the e-mobility transition](https://munichre.com/en/solutions/for-industry-clients/enabling-the-e-mobility-transition.html)
- [TWAICE accuracy guarantee (electrive.net)](https://www.electrive.net/2022/12/12/twaice-garantiert-ab-sofort-genauigkeit-der-batterieanalyse/)
- [Aviloo battery warranty (Bestmag)](https://www.bestmag.co.uk/aviloo-battery-warranty-used-evs/)
- [PVsyst review](https://www.heavengreenenergy.com/blog/pvsyst-review)
- [EnergySage company page](https://energysage.com/about-us/company)
- [Geotab EVSA launch in Europe](https://www.geotab.com/uk/press-release/evsa-launches-in-europe)
- [Enverus acquires Pearl Street (Mar 2025)](https://enverus.com/newsroom/undo-the-queue-enverus-acquires-pearl-street-technologies-to-solve-for-a-more-reliable-resilient-grid)
- [Zeem funding (AJOT)](https://www.ajot.com/news/zeem-solutions-ev-fleet-as-a-service-provider-secures-50-million-capital-investment-from-affiliates-of-arclight-capital-partners-announces-strategic-partnership-with-laz-parking-realty-investors)
