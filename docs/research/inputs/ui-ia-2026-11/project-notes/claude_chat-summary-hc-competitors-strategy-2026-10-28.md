# HDEV / EV Scope: chat summary (26–28 Oct 2026)

Handover for a new chat. Facts marked *(sourced)* were checked against a source in the chat. Everything else is Bob's decision, a plan, or an assumption, and is labelled as such.

---

## 1. City Tekniq / Hans Chr. Jensen (HC): partnership ended

**Background**
- **15 Oct:** Bob presented to HC. HC said he does roughly the same thing his own way, and asked to see the actual tool workflow.
- **20 Oct:** Bob showed the EV Scope mockup demo. HC wanted an illustrative, high-level report and talked about marketing and municipal politics. He floated a split: Bob takes truck companies, HC takes municipal work.

**Bob's email (26 Oct)** offered two options:
1. A one-project contract with a client HC brings. HC gets 10% in total for bringing the client, and the remaining 90% is split. No exclusivity, no NDA, ends on delivery.
2. If HC wants Bob to do sales, marketing or content work, HC pays Bob as a freelancer.

The email also said further meetings, demos or material must fall under one of these, and stayed open to other ideas.

**HC's reply (26 Oct)**
- His mother had died that Saturday.
- He rejected both options. In his view there is nothing in it for him, sales and marketing are the scarce part, and "the analytic work can be done with your tools and mine".
- He reversed the proposal: Bob brings the client and takes 10%, and HC gets paid an hourly rate for sales.
- His conclusion: they are too far apart for a shared-risk model. "Write again if you see the light."

**Decided next step**
- Send a short, warm reply within a day or two. Lead with condolences, then one neutral line closing the business topic.
- Leave the door open for HC to refer clients (e.g. transport companies).
- Don't mention that Bob will sell to installers or competitors.
- Draft already agreed in the chat. Status: **not yet confirmed as sent.**

**Bob's direction going forward**
- Go independent: finish the platform and sell it, including to electrical installers and HC's competitors (e.g. Elento).
- Use nothing that came from HC: no clients, templates, pricing or workflow.
- No NDA was ever signed. Bob should check that no other agreement restricts him.

---

## 2. Platform positioning (Bob's decisions)

- **A facilitator / marketplace, not a competitor.** The fleet owner's operational data stays fixed. OEMs, CPOs and installers enter their own specs and prices, and these are tested on the same simulation.
- **Built on EU regulations and standards** (VECTO, Reg. 2017/2400).
- **Not forced to be brand-agnostic.** Users can size from scratch, pick from a vehicle/charger library, or size first and then find matching models. When a report is brand-agnostic (e.g. for municipalities), the report says so.
- **A spec database is a core USP and revenue stream.** Bob's analogy is MyFitnessPal. Revenue options: OEMs/CPOs pay for listings, and API licensing.
- **Route ZERO:** Bob will use it for inspiration and gap-finding. It's his decision and liability. Note: its ToS Section 4 bars "attempt to derive … methodology", and Section 7.2 limits outputs to internal use.
- **Expansion:** Denmark is too small and slow. The plan is EU + UK.

---

## 3. Competitor research

### Dynamon (UK, *sourced*)

**Company**
- University of Southampton spinout (2015). Started as fuel/tyre/aero analytics for hauliers, before EVs.
- bp ventures invested £4m (Series A, Aug 2023), with a commercial agreement to offer the tools to bp pulse customers.
- 11–50 staff. Shareholders' funds £4.7m (30 Jun 2025).

**ZERO (report service, consultancy-delivered)**
- Price by fleet size:
  - up to 50 vehicles: £4,990
  - 51–100: £6,990
  - 101–200: £8,990
  - 201–300: £10,990
  - over 300: bespoke programme
- Delivered in ~6 weeks from receiving data. In 2025 the CEO said "within a few days".
- Inputs: telematics, fleet list, depot list. Synthetic routes when telematics are missing.
- They describe it as physics/vehicle-dynamics based, every route modelled, worst-case duty cycles included.
- Outputs: feasibility and battery sizing, rollout plan, charger count/power, grid (where known), BESS, TCO, CO₂.

**Route ZERO (self-serve app)**
- Pricing: free for 100 sims in the first month, then 10 a month; £100 per user per month for unlimited.
- Paid plans need a UK business identifier.
- Flow: vehicle → route → inputs → pass/fail with charge stops.
- Multi-OEM truck library plus custom vehicles.
- Covers all of Europe, with 400+ truck charging sites.

**Data**
- Proprietary EV performance database, built with on-road testing and validated by re-running real routes virtually.

**How they sell**
- Case studies with big names and numbers: Asda, Royal Mail, TfL, DFDS (Danish), Wincanton/IKEA, NHS, Maritime. Cress Company cut peak demand from 3,300 to 900 kW.
- Government-funded programmes: Transport Scotland pays up to £15k of free analysis per SME fleet; ZENFreight lead partner; DESNZ police-fleet study.
- Consultancy partners: PA Consulting (Islington, which fed a £25m renewal programme), AllChiefs (NL), eMotion Fleet (Japan).
- Telematics marketplaces: Geotab, Samsara, Verizon Connect; ~100 telematics API connections.
- Toyota sales-tool build; free TCO calculator; depot game "Charge Control".

**Gaps in their public material** (absence on their site, not proof they lack it)
- No PTO / refuse-body modelling.
- No tender or bid verification.
- Nothing Danish.
- No flexibility markets.
- No AI assistant.
- Independence claim vs bp investment.
- Sample report still "coming soon".

**Not UK-only.** They're already in Europe, including DFDS's rollout into mainland Europe.

### Other players

- **Plexar Energy** (Nordhavn, CIP affiliate, 2024): financed renewable microgrids, logistics depots included. Claims a microgrid "can supply over 60% of daily charging needs". A potential bidder and customer.
- **FLEXECHARGE** (CPH): HARMON-E load management for CPOs and depots; raised €5m in 2025. Downstream of HDEV, so a partner.
- **Decade Energy** (FR): builds, finances and operates depot power. 1,500+ feasibility studies; raised €22m in 2026; expanding to the Nordics.
- **ChargeSim (NL):** depot simulation, bus-first; eYardPlanner for trucks.
- **BetterFleet:** planning plus charge management.
- **Flowemo (DK):** charger layout, electrical calculations and documentation. Starts from a *given* charger set, so HDEV is upstream of it. Its partners (ABB, Monta, Hessel Power, Eltel…) are a channel.
- **DORA TMS (DK):** haulier transport management system with CO₂ reporting. An integration partner.
- **OEM tools (free, single brand):** Daimler eTruck Ready, DAF Route Simulator, Volvo Range & Route.
- **Open source:** eFLIPS (TU Berlin), SimBA/WeBus (RLI, free bus web tool), REVOL-E-TION and LIFT (TUM).
- **Not yet assessed:** Elento, Siemens, The Mobility House, Ampcontrol, Milence/Depotcharge, COWI/Ramboll/Sweco.

### Market evidence (*sourced*)

- ICCT/Fraunhofer: EU e-truck charging demand ~100 TWh by 2035, ~200 TWh by 2045; depot charging is 70–80%+ in most countries.
- DTU (Menchaca Santos et al.): up to 70% less grid capacity with coordinated charging; Danish grocery fleet of 33 trucks. The LinkedIn post said 75%.
- T&E/Fraunhofer: 40 trucks need ~2 MW at 50 kW chargers vs ~6 MW at 150 kW.
- ICCT: batteries sized for the worst day are under-used, which hurts TCO.

---

## 4. Denmark-specific facts (*sourced*)

**Refuse tenders**
- Vejen: ≥75% zero-emission collections. Randers: 80%.
- Holbæk/FORS replanned routes around electric range; residents lose the same pickup weekday for every waste type.
- Cirkulær: almost all household-waste tenders now demand electric or alternative-fuel trucks.

**Ressourceindsamling A/S (Glostrup) contract**
- 10 three-axle, two-compartment electric refuse trucks, plus options for 70 more.
- 10-year service contracts, up to 30,000 km per year.
- **The bidder must state usable battery capacity after 8 years.** If it's lower, the battery is replaced free, checked by a third-party Ohm measurement.
- The requirement spec (Bilag 1) is not yet obtained.

**Other**
- Scania vs I/S REFA appeals ruling: bids lose on spec details.
- Reno Djurs (2021): ~120 km range in mixed collection, 220 km pure driving.
- **Road toll** (from 1 Jan 2025, ≥12 t, CO₂-class based, per Dansk Erhverv citing the bill): over 32 t outside environmental zones, electric 0.20 vs diesel 1.35 DKK/km in 2025–27, rising to 0.25 vs 1.67 from 2028. Other cited rates differ, so verify with Skattestyrelsen. Expected extension to ≥3.5 t from Jan 2027.
- **Grant pool 2026** (Vejdirektoratet): DKK 159.9m per the executive order. Open 4 Feb–30 Sep 2026, first come first served, max DKK 4m per applicant. Requires the budget template, plus quotes for the electric truck *and* a comparable diesel truck. DI called it the "last time" the pool opens.
- **Grid**
  - Radius Q2 2026: 24.6% of medium connections took >12 months in the construction phase.
  - Limited (non-firm) grid access is much cheaper but can be curtailed.
  - Energinet paused new connection agreements on 2 Mar 2026 and lifted the pause on 3 Jun 2026 (per Plesner).
  - Radius asks for driving patterns, charger count/type and an **optimised charging profile** in connection requests.
- **DataHub 3.0:** live since 18 Sep 2026. 15-minute metering, independent aggregators (exact start date unconfirmed), virtual meters (a flexible asset behind the same connection metered separately). Eloverblik third-party data sharing with customer consent.

---

## 5. Data and database findings

| Source | Reuse | What it gives |
|---|---|---|
| VECTO tool + EU standard values | Yes (free Commission tool, EU law) | Defaults per vehicle group |
| EEA HDV monitoring dataset (2019–2023 CSV) | Yes, with attribution ("unless otherwise indicated") | Certified data. Electric-truck fields **unconfirmed**; ICCT found ZEVs largely absent early on. Bob to check the table definition |
| VECTO Customer Information File | Bidder supplies it | kWh/km and range per mission profile, at beginning and end of life (Annex IV Part II) |
| OEM spec sheets | Collect facts yourself with a source link | Battery, mass, power, charging |
| Chargepoly Data Hub, ZETI | Don't copy (EU database right) | Use to discover models only |
| carculator_truck | No licence stated; 20 old/US rows | Skip |

- **VECTO certification gaps:** groups 6–8, 13–15 and 17–19 are excluded (4x4, 6x6, 8x2, 5-axle). 6x2 refuse trucks are group 9, which has the municipal-utility mission profile. 8x2 refuse trucks are excluded.
- **Rarely published:** CdA, rolling resistance, loss maps, usable vs gross battery, aux/PTO. Fill from standard values; calibrate with telematics.
- **Key analysis:** specs alone are not a moat, since Chargepoly gives them away free. The moat is **calibrated real-world consumption** (model × duty cycle × temperature × payload), fed back from every project.

---

## 6. Strategy analysis (Claude's analysis, 27 Oct)

**Core insight**
- Five parties (fleet, DSO, municipality, OEM/CPO/installer, bank) re-create the same numbers in different documents.
- Aim to be **"PVsyst for EVs"**: one auditable project file exported as a DSO request, grant budget, tender answer and bankable feasibility report.
- PVsyst became standard because banks accept its reports (transparent losses, P50/P90).

**Needed USPs, ranked**
1. Firm vs non-firm vs BESS grid comparison (turns Bob's flexibility thesis into cash).
2. DSO-ready export. Get one DSO (Radius/Cerius) to accept or recommend the format.
3. Grant pack generation (DK budget template, DE €/kW, UK DCS grid evidence).
4. Right-sizing from a full-year simulation, giving a P50/P90 day.
5. Tender module (bid verification, end-of-life range vs the 8-year battery guarantee).
6. ESG export later. After the 2026 Omnibus, CSRD is mandatory only above 1,000 staff and €450m turnover. Use metered data, not simulation.

**Honest gaps**
- Engine at Block 0; driver model being rewritten; no drivetrain maps yet.
- **Battery modelled as 100% efficient.** OCV + Ri charging model not coded.
- **No depot simulation:** charger assignment, taper, sharing, shifts, BESS dispatch, tariffs.
- No telematics/GPS import. No references or case studies.
- "VECTO-traceable" is unvalidated until compared with a VECTO electric-truck run, OEM figures and real truck data.
- **Tension:** a black-box tool vs becoming a standard. Suggestion: publish the method document, keep code and data closed.

**Partners:** Flowemo (upstream integration), Decade/Plexar-type developers, DORA TMS, installers (licence).

**Market order:** DK as reference → Germany (€1bn depot-charging programme 2026–29, up to €500/kW per one summary, truck toll exemption to 30 Jun 2031, no public grid map) → NL (15,498 grid requests queued, non-firm contracts) → UK (truck grant up to £81k, Depot Charging Scheme up to 70%/£1m, but Dynamon is the incumbent).

**Business-model blueprint (from Dynamon):** fixed-price reports by fleet size, a freemium self-serve tool, free calculators as lead magnets, case studies with numbers, consultancy partners, telematics marketplaces. Beat them on speed (~1 min engine), traceability, refuse/PTO, Danish/EU rules, the tender module and AI intake.

---

## 7. Open actions

- [ ] Send condolence reply to HC.
- [ ] Get and paste:
  - Radius "Sæt strøm til den tunge transport 2025" PDF
  - Vejdirektoratet budget template
  - Ressourceindsamling Bilag 1 (requirement spec)
  - EEA HDV table definition
  - Forsyningstilsynet waste tender report PDF
  - German BMV Call A documents
- [ ] Collect 10–20 real Danish refuse-truck tender packages.
- [ ] Validate the engine against VECTO BEV, OEM data and real truck data.
- [ ] Spec a depot simulation (charger allocation, taper, BESS, tariffs).
- [ ] Define the vehicle library field structure (spec sheet / standard value / OEM-verified / calibrated tags).
- [ ] Research still missing: Elento; NL/SE/NO/FR grants; charger, civil works and transformer costs; e-truck prices and lead times; bank/lessor requirements; ISO 14083 details.
- [ ] Possible next research: Danish funding for fleet analyses (Transport Scotland equivalent).
