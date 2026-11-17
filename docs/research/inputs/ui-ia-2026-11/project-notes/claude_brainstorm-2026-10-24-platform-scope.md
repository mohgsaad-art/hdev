# HDEV / EV Scope — brainstorm: platform scope and next steps
Date: 24 Oct 2026 (saved 30 Oct 2026)
Type: ideas and discussion only, not a technical spec.

Bob's working rules for this chat:
- Flag assumptions and simplifications explicitly.
- Ask for code, files or VECTO code when needed.
- No invented data, methods or numbers. Suggested values must be verifiable from authentic sources.
- One step at a time unless asked. Bob builds and codes; Claude helps.

Items marked **(to check)** are believed true but not yet verified. Confirm before using them in the tool.

---

## Bob's questions

1. The split between fleet owner and OEM, CPO, aggregator.
2. Handling all vehicle types: trucks, cars, vans, etc.
3. Can public OEM spec sheets let users pick an exact vehicle to simulate? Should that be an option?
4. Modularity: users can skip the consumption engine and run only the charging engine if they have consumption rates and operational data.
5. What's next? Consumption engine almost done. Thesis charger physics need rewriting on regulations, standards and robust physics; same for flexibility and full TCO/CO2. Where does MitID capacity data (load profile → peak coincidence → charger sizing within grid limit) fit?
6. Reporting (carbon, taxes, subsidy applications, grid applications, tenders): does it add value? Fintech analogy — automating finance and accounting saves time and effort.
7. Extending to other countries: language, prices, price structures, no MitID, different data sources, etc.
8. Anything else not being considered?

---

## 1. Fleet owner vs OEM, CPO, aggregator

One shared **project file** with slots. Each party fills the slots they actually know:

| Party | What they know | What they want from the tool |
|---|---|---|
| Fleet owner | Routes, stops, payload, depot hours, budget | "Will EVs work, what do I buy, what does it cost?" |
| OEM | Battery size, usable capacity, motor, mass, charging curve | "Does my truck fit this customer's operation?" |
| CPO | Charger power, ramp rates, OCPP, price | "Does my charger setup fit this depot and grid limit?" |
| Aggregator | Market products, prices, response times | "How much flexible load is here and when?" |

- Same engine for everyone; only the input screens differ (matches the 22 Oct note).
- Add a **source tag on every value**: standard value / user-entered / OEM-supplied. Extends the existing orange "assumed value" marking. Keeps the tool credible as neutral once suppliers put in numbers, and makes the tender bid comparison idea work almost for free.

## 2. All vehicle types

- The physics is the same for cars and trucks: rolling, air, slope, inertia, aux.
- What changes is **where the standard values come from**:
  - Trucks and buses: VECTO.
  - Cars and vans: WLTP (Regulation 2017/1151), with its own cycles.
  - VECTO was extended to medium lorries **(to check the exact weight range)**.
- So "all vehicles" is mostly a defaults library per vehicle category, not a new engine.
- The bigger difference is **charging behaviour**. Cars at a housing association plug in at random times; trucks follow schedules. That affects the charging and grid side more than consumption.

## 3. Picking an exact vehicle from OEM spec sheets

Offer it, but be honest about what it gives.
- **Spec sheets usually have:** battery size, sometimes usable size, max charging power, weights, claimed range.
- **They usually lack:** drag area, loss maps, aux loads, and often which cycle the range was measured on.
- **A public source for cars and vans:** the EEA CO2 monitoring dataset includes energy use per model **(to check BEV fields)**. Per-vehicle VECTO results for trucks go to the buyer and are likely not public **(to check)**.

Suggestion: a **vehicle library**. Picking a model fills in what's known; the rest comes from standard values, clearly tagged. Call it "based on published specs", not "exact simulation". It becomes exact only when the OEM supplies its own data, which is also a natural paid OEM feature.

Risk: scraping spec sheets can break the sites' terms of use. Manual entry or OEM-supplied data is safer.

## 4. Modular stages

Yes. Define a clear handover between stages, like a plug and socket. Consumption → charging hands over roughly:
- energy needed per vehicle per day (or per trip)
- when each vehicle is at the depot (arrival and departure time)
- the battery state it must leave with

If the user already has kWh/km and a schedule, they fill that handover directly and skip consumption. The same pattern applies further down: charging → load profile → grid → headroom → flexibility, and so on.

## 5. What's next, and where MitID fits

1. **Consumption.** Almost done.
2. **Charging.** Rewrite the thesis model on the already chosen battery model (OCV + Ri), with charger limits from the charging standards (IEC 61851, ISO 15118). Output: load profile per vehicle.
3. **Site and grid check.** MitID/Eloverblik fits here. Existing site load + simulated charging load → compare the peak with the connection limit.
4. **Flexibility.** How much charging can move while still meeting departure needs.
5. **TCO and CO2** on top.

Two insights for step 3:
- **Depots may not need a coincidence factor.** A coincidence factor is a shortcut for when you don't know when everyone charges. HDEV simulates charging, so it gets the real combined peak. Housing associations with random car charging would need a standard coincidence factor; which Danish/EN standard gives one is **(to find)**.
- **Hourly meter data hides short peaks.** An hour that averages 80 kW can contain a much higher spike. This is why the CT logger note exists. DataHub has been moving to 15-minute data **(to check how far)**.

## 6. Reporting

Likely the biggest value multiplier. The fintech analogy holds: **enter data once, get many documents.** Most numbers already come from the engine. Candidates:
- **Transport CO2 reports to ISO 14083.** Hauliers are increasingly asked for these by customers.
- **Clean Vehicles Directive (2019/1161) reporting** for municipalities and public buyers (minimum clean-vehicle shares in procurement).
- **Grid connection applications** to the DSO (power, load profile, connection size).
- **Subsidy applications** under Danish truck electrification pools **(to check what is open now)**.
- **Tender specifications and bid comparison.**
- **A finance case** for a bank or leasing company, built from the TCO.

Cautions:
- Some documents carry legal responsibility. The tool produces a draft the user checks and signs, not a final legal document.
- CSRD scope was cut back recently **(to check current scope)**. Don't build for it first.

## 7. Other countries

Mostly a **country pack**: a folder of settings and data connectors. The engine doesn't change (engine functions already take every value as an argument).

| Stays the same | Changes per country |
|---|---|
| Physics, driver model, charging physics | Meter data access (Eloverblik is Danish; others have their own data hubs or none) |
| EU rules: VECTO, WLTP, charging standards, Clean Vehicles Directive | Tariff structure (energy-based, peak-power-based, time of day) |
| Report layouts | Taxes, road tolls, subsidies |
| | Grid connection rules and DSO thresholds |
| | Weather source (DMI here; ERA5 from Copernicus covers Europe as a fallback) |
| | Grid CO2 intensity, currency, language |

- No meter data API → fallback to uploading a meter export or CT logger file.
- The Nordics are the natural next step (similar markets).

## 8. Things not yet considered

- **GDPR.** MitID meter data and driver GPS traces are personal data. Needs consent handling, storage rules and a data processing agreement with customers.
- **Liability.** If a sizing leads to a grid trip, who is responsible? Clear terms and "advisory only" framing.
- **Battery ageing.** Capacity fades; sizing for day one may fail in year six. Matters for sizing and TCO. A recognised standard/method is **(to find)**.
- **Phased rollout.** "Five trucks now, ten in 2028" changes grid and charger decisions.
- **Recording standard versions.** Every report should record regulation versions and data dates used, for later audits.
- **Payload rules.** EU weights rules give zero-emission trucks extra allowed weight **(to check current amount)**. Ties into the payload-loss item from the COWI list.
- **Validation library as marketing.** Cross-checks against VECTO, studies and spec sheets can become a public "how we validate" page — earns trust without revealing the method.

---

## Suggested next discussion

Start with #5: fixing the consumption → charging handover makes #4 (modular stages) and #1 (who fills which slot) fall into place.
