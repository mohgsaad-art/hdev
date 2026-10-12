# Reference Excel files — what they are and why they are here

**Intent:** these three Excel files are NOT HDEV code and NOT needed for the current phase (engine + UI). They are reference material for LATER phases (TCO, CO₂, coincidence factor, municipal demand). Do not plan work on them now; just know they exist and what they contain. Source of this summary: Claude's cell-by-cell audit on 26 Sep 2026 (project memory `cowi-data-sources.md`, `competitive-features.md`). The files themselves are in `reference/excel/`.

---

## 1. `eltiltrucks-beregner-ark.xlsx` — COWI electric-truck TCO/LCA calculator (free public version)

**Intent in HDEV:** template for the future TCO / CO₂ phase (roadmap step "TCO/LCA overlay — port logic from eltiltrucks-beregner-ark"). Copy the *structure and sourced formulas*, never the dated numbers.

**Sheets:** Dashboard (summary), Ladeinfrastruktur (charger costs), 2025–2030 year sheets, Elpriser (electricity prices), Afgifter (road tax), LCA, Dataark TCO & LCA (lookup tables).

**Sourced elements (reusable as METHOD, refresh the numbers):**
- Grid connection fee (Radius DSO): 17,950 DKK base for first 25 A + 1,280 DKK per extra A (radiuselnet.dk "Tilslutningsbidrag"). Only Radius; other Danish DSOs differ.
- Charger hardware + trenching cost bands 22–400 kW ("hentet hos en ladestanderoperatør i 2024", operator not named).
- Load factor 0.85 for chargers (load time = battery kWh ÷ (charger kW × 0.85)).
- Fuel prices Jan–Jun 2024 (ok.dk): diesel 11.15 DKK/l (TCO uses 11.65 = +0.50 duty per "Aftale om deludmøntning af Grøn Fond"), AdBlue 6.96, HVO100 19.97.
- Electricity: Elpriser!J23 = average of the cheapest N hours per day (N = ROUNDUP of daily depot charging hours) of Jan–Jun 2024 DK1/DK2 spot × 48/25 (×1.92 multiplier standing in for tariffs; basis not stated). Sources: radiuselnet.dk, energidataservice.dk Elspotprices.
- A Klimastatus og -fremskrivning 2024 price projection (2023–2035) is computed in Elpriser but NOT referenced by any TCO formula.
- Km-based road tax (vejafgift) by weight class / CO₂ class / zone, el vs diesel (skm.dk rate tables). E.g. 2025–27: 0.1008 DKK/km el vs 0.8525 diesel; rising in 2028 and 2029+.
- LCA factors: ICCT 2023, T&E 2020, IVL 2019 battery production, Energistyrelsen 2023 grid emission factors (declining curve 2024–2034).

**UNSOURCED in the file (do not reuse as facts):** truck prices (EV 2,050,000 / diesel 1,150,000 DKK), service, insurance, interest 3.45%, driver wage, residual-value %, 300 operating days, 9.75 h/day, 1.19 kWh/km, 0.288 l/km, 504 km range.

**Method facts:** year sheets 2026–2030 are NOT different vintages (all link back to 2025; only road tax changes). Financing = Excel PMT annuity with residual as balloon. Lost-production cost (EV only) = monthly fixed costs × (public-charging hours ÷ daily operating hours). Breakeven = capex difference ÷ average monthly operating saving. "Lademeter" metric = TCO per km ÷ 13.6 m.

**Not in this free file (despite COWI marketing):** lower payload for EVs, cost optimisation, sensitivity analysis, price projections feeding TCO.

---

## 2. `Elindsigt2.2.xlsx` — household/meter electricity insight tool (Eloverblik)

**Intent in HDEV:** reference for the planned Eloverblik integration (MitID token → hourly consumption per metering point → coincidence factor → charger sizing). Out of scope now.

**Contents:** token input (Kontrolpanel), bill breakdown by component (spot, distribution, system tariff, transmission, duty), surplus production, hidden-fee detection, and Timespecifikation = full-year hourly rows (consumption, spot, tariffs, cost per hour). Data source: Eloverblik / DataHub API. It does NOT compute a coincidence factor, load diversity or flexibility.

---

## 3. `ChargePointCalculator_v5.xlsx` — municipal charge-point demand calculator

**Intent in HDEV:** validation/reference only (top-down municipal charger demand). Not core to depot sizing.

**Contents:** all 98 Danish municipalities; EV uptake S-curve 2022–2050; charging split by location type (A home, B housing association, C workplace, D public/fast); fast-charger need from range extension. Source of the underlying population/vehicle data not found in the extracted cells. No grid constraints, no coincidence factor, no cost.
