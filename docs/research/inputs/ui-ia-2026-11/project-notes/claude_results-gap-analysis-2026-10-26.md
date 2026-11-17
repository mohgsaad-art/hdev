# EV Scope results: gap analysis (26 Oct 2026)

Scope: what the results pages of the mock-up (`ev-scope-workbench-8.html`) are missing, judged against:
- VECTO's output files (Annex IV MRF/CIF, `.vsum`/`.vmod`),
- the COWI truck TCO sheet (`eltiltrucks-beregner-ark.xlsx`),
- the project knowledge base (4-leaf "Renovationskørsel på el 2023", Rambøll "Smartladning og V2X", Cerius/Radius notes),
- real Danish tenders found on 26 Oct 2026 (Ressourceindsamling, Frederiksberg, Gentofte, REFA, Dansk Retursystem, Aarhus, Herning, FynBus, Region Hovedstaden),
- Energinet's ancillary-service tender conditions.

Tags: **[SRC]** stated in a source (named), **[JUDGEMENT]** Claude's own reading, not from a source.

---

## 0. What the mock-up shows today

| Page | Panels |
|---|---|
| Overview | Verdict, 4 key figures, 6 feasibility checks, fleet day gantt, results by area |
| Energy | 4 KPIs, energy waterfall (driving / bin lifts / on-board), year heatmap, by month, on-board table |
| Charging | 4 KPIs, battery through hardest day, fleet schedule, strategies compared |
| Grid | 3 KPIs, depot power hardest day, load duration, flexibility bars |
| Cost | 4 KPIs, cumulative cost line, electric vs diesel bars, breakdown |
| CO₂ | 4 KPIs, per year, saved over time |
| Vehicles | 4 KPIs, each truck hardest day, range through year |

---

## 1. Biggest gaps (ranked by [JUDGEMENT])

1. **No energy balance.** VECTO splits every kWh: air, rolling, grade, inertia, mechanical brakes, gearbox, axle, motor, battery loss, each aux [SRC: `.vsum` columns used in harness v1.7]. The mock-up has 3 bars.
2. **Cost page is far thinner than COWI.** COWI has ~80 line items, financing, residual, break-even months, per-km / per-month / per-year / per-period TCO, lost production time, cost per loading metre [SRC: COWI '2025' sheet rows 20–109].
3. **Flexibility is one bar chart.** Nothing on which product, minimum bid, response time, hours available, revenue, or effect on readiness.
4. **No end-of-life view.** VECTO reports ranges at beginning and end of life [SRC: Annex IV CIF 2.5]. Ressourceindsamling's contract guarantees battery capacity after 8 years [SRC: contract §17.1]. The mock-up sizes for new batteries only.
5. **No audit block.** VECTO stamps tool version, run time and hashes of the inputs [SRC: Annex IV MRF §3]. It also prints a simulation quality check (average/min/max speed, max acceleration and deceleration, distance) [SRC: MRF 2.2]. The mock-up shows neither.
6. **No growth or phasing.** Tenders buy options for many more trucks (Ressourceindsamling: 10 + up to 70 within 48 months [SRC]). ARC needed 3,500–4,000 A per site and had to cut charger power [SRC: 4-leaf 2023]. The mock-up has one fleet size.
7. **No monthly balance table.** PVsyst's core report table has one row per month (see §2). The mock-up has a by-month bar only.

---

## 2. The PVsyst benchmark

**[JUDGEMENT]** This section is from general knowledge of the standard PVsyst simulation report. It was not re-checked against a report this session.

| PVsyst report section | HDEV equivalent | In mock-up? |
|---|---|---|
| Project summary: site, weather source, system type | Fleet, depot, DK1/DK2, weather station + year, engine version | Partly (header line only) |
| System parameters, every component listed | Vehicle, battery (nominal / usable), drivetrain, aux techs, chargers, connection | No (only on input pages) |
| Loss list with each assumption | Every standard value used, with its source | No |
| Main results: energy, specific yield, performance ratio | kWh/day, kWh/km, kWh/t-km, peak kW, readiness % | Partly |
| Normalised production chart | kWh/km by month, split by cause | No |
| **Balances and main results table** (monthly rows: irradiation, temperature, energy at array, energy to grid, PR) | Monthly rows: km, °C, kWh driving, kWh aux, kWh HVAC, kWh regen, kWh at battery, charger losses, kWh from grid, peak kW, cost | **No** |
| **Loss diagram** (sun → grid, each loss in %) | Grid → charger → battery → motor/inverter → gearbox/axle → wheel → air / roll / grade / brakes, plus aux branch | **No** |
| P50/P90 | Hardest-day energy and peak at P50/P90 across weather years | No |
| Financial analysis: investment, OPEX, LCOE, NPV, payback, cash flow | Year-by-year TCO, NPV, break-even, cost/km | Partly |
| CO₂ balance | LCA balance | Partly |

---

## 3. Gaps page by page

### 3.1 Energy and vehicle

What the engine already produces but the pages don't show [SRC: Kiro prompt §B, engine outputs]:
- time spent stopped, accelerating, cruising, coasting and braking;
- energy recovered by braking;
- a day profile of speed and battery power;
- kWh/km per extra tonne of load, and per °C;
- what drives the result: wind against temperature;
- cab climate options compared (standard value / electric heater / heat pump).

Missing, by source:
- **Component energy balance** (see §1.1) [SRC: VECTO].
- **kWh per tonne-km and per tonne collected.** VECTO reports per km, per t-km and per m³-km [SRC: Annex IV 2.3].
- **Nominal against usable battery.** The 4-leaf report warns these "can differ substantially"; Scania gives usable as 73 % of nominal [SRC: 4-leaf 2023].
- **Operating time (aktionstid), not just range.** The 4-leaf report says operating time matters as much as range. At Frederiksberg, 70 km a day still left a 175 kWh battery at 15 %, so they moved to 255 kWh [SRC].
- **State of charge on return, per truck, across the year.** Operators quote it this way: Vejle returns at 28–43 %, Rødovre above 50 %, Nottingham at 40 % [SRC: 4-leaf].
- **End-of-life check.** The hardest day must still fit with the battery at its guaranteed capacity in year 8 [SRC: Ressourceindsamling §17.1; VECTO begin/end of life].
- **Payload against diesel.** The electric truck can carry less: Frederiksberg's PVI carried 2 t less, Herning's conversions lost 1 t of total weight [SRC: 4-leaf]. COWI uses the same vehicle weight for both [SRC: COWI audit].
- **Hills when fully loaded.** Rødovre's trucks reach only about 35 km/h on a slight incline when full [SRC: 4-leaf]. [JUDGEMENT] The force engine could report speed on a given grade at full load. This is not built.
- **Expected kWh/km by month and by temperature**, written so it can be checked later. FynBus makes the operator log kWh/km every second and plans to analyse it by month, temperature and driver, split between driving and heating [SRC: FynBus Bilag 1 §2.21]. [JUDGEMENT] HDEV's prediction should be in the same shape, so predicted can be compared with actual.

### 3.2 Charging

Missing:
- **A table of every charging session, per truck:** arrival SoC, kWh, start, end, power, finish time, slack before 06:00.
- **Charger use:** hours busy, and the ratio of chargers to trucks.
- **Charging between shifts and at the tip site.** ARC added 100 kW chargers to top up between first and second shift. The 4-leaf report recommends DC chargers at the disposal site so trucks can carry smaller batteries [SRC].
- **Losses and charger type.** AC on-board versus DC off-board, the connector, and the 3–4 % charging loss the 4-leaf report cites [SRC].
- **Robustness:**
  - one charger out of service;
  - a late return;
  - a cold week.
  Region H requires 99 % uptime and repair within 24 h [SRC]. Ressourceindsamling allows at most 5 downtime days per truck per year [SRC].

### 3.3 Grid

Missing:
- **Connection in amperes and its cost.** Danish connections are bought per ampere [SRC: COWI/Radius]. Above 750 A and 4,500 A the customer takes over parts of the grid [SRC: Radius via 4-leaf]. The mock-up gives kW only.
- **Lead time.** Getting a connection can take from 9 months to more than 6 years [SRC: 4-leaf table].
- **The building's own load as a real hourly profile.** Today it is a 30 kW constant. The Eloverblik data idea is in the project memory.
- **Peak growth with fleet phases.** At what fleet size does the connection run out? See §1.6.
- **Capacity-friendly and system-friendly as two separate scores.** Cerius/Radius say these are different things: selling system services can make local congestion worse [SRC: netvenlighed note].

### 3.4 Flexibility (today one bar chart)

Missing:
- **Up and down flexibility per hour,** limited by battery energy and the 06:00 readiness, with the cost to readiness.
- **Which products the fleet could sell.** This is a check against the product rules, not a revenue promise [SRC: Energinet tender conditions]:
  - FCR-D: minimum bid 0.1 MW, full response within 7.5 s;
  - FCR-N: minimum 0.1 MW, needs at least 1 h of energy;
  - mFRR: minimum 1 MW, fully delivered within 12.5 min;
  - all products need measurements at under 1 s.

  [JUDGEMENT] 6 trucks × 40 kW = 240 kW, which is below the 1 MW mFRR minimum. That means an aggregator or a larger fleet. The page should say so.
- **DSO flexibility.** Cerius/Radius pilot terms [SRC]:
  - response within 15 min;
  - available 24/7;
  - paid 1:1 at 80 % delivery or more, nothing below 30 %;
  - value capped at the avoided reinforcement cost (annuity, 40 years, 5 %);
  - BNA customers excluded.

  It is a pilot in 2 areas only, so it must be shown as pilot-stage.
- **Amperes saved by load management.** At PostNord, phase rotation saved 33 % and queuing a further 50 %, about 800,000 DKK in total [SRC: Rambøll].
- **Hours per week available.** As a benchmark: Frederiksberg Forsyning's V2G cars offered 118 h/week for about 12,000 DKK per car per year. Those were passenger cars on CHAdeMO [SRC: Rambøll], so not directly transferable.
- **V2G readiness.** It needs ISO 15118-20 on both the truck and the charger [SRC: 4-leaf / Rambøll].
- **Rebound effect** after a curtailment [SRC: Cerius/Radius pilot question 2e].

### 3.5 Cost

COWI has all of these [SRC: '2025' sheet]:
- price, subsidy, down payment;
- residual value % and interest, with annuity financing;
- charger, connection by amps, trenching;
- driver wages;
- fuel per km incl. AdBlue;
- public-charging share and price;
- service, tyres, insurance;
- km-based road tax by year;
- lost production time;
- TCO per km / month / year / period;
- break-even in months;
- cost per loading metre.

Missing in the mock-up:
- **A year-by-year cash-flow table,** not one cumulative line.
- **Financing and residual value,** and NPV with a discount rate.
- **Electricity cost split:** spot price, grid tariff by time of day, electricity tax and refund. Region H's spec shows the tax-refund flow [SRC].
- **Price paths.** COWI computes the Klimastatus projection but does not feed it into TCO [SRC: COWI audit].
- **Sensitivity:** electricity price, diesel price, km/year, residual value, battery replacement, interest rate.
- **Service contract over 8–10 years,** the lever for battery guarantee terms, and downtime cost. All the tenders bundle 8–10 years of service [SRC: Frederiksberg, Ressourceindsamling, Gentofte].
- **The depot cost split across trucks,** and a separate depot amortisation. The 4-leaf report suggests about 30 years for electrical infrastructure against about 10 for vehicles. Esbjerg amortises its bus depot over 24 years [SRC].
- **Alternatives beyond diesel:** HVO, biogas. Vejle and Sønderborg chose gas for part of their fleets [SRC: 4-leaf]. COWI compares CO₂ against biodiesel [SRC].
- **Cost per tonne-km and per tonne collected** [JUDGEMENT].

### 3.6 CO₂

Missing:
- **Life-cycle numbers:** vehicle and battery production, and well-to-wheel fuel. COWI's LCA sheet has the sources [SRC].
- **A grid emission factor that falls each year.** Energistyrelsen's series goes from 41.5 to 7.0 g/kWh between 2024 and 2034 [SRC: COWI Dataark LCA].
- **The emission factor at the actual charging hours** [JUDGEMENT].
- **Comparison with HVO, biogas and B7 diesel** [SRC: COWI dashboard].

### 3.7 OEM / tender view (not in the mock-up at all)

What the tenders actually score and require:
- **Award weights:**
  - price 50–70 %;
  - technical evaluation 25–35 %;
  - delivery time 15–25 %;
  - ESG/environment 10 %.

  [SRC: Frederiksberg, REFA, Dansk Retursystem, Aarhus, Herning]
- **The evaluated price formula.** Frederiksberg adds vehicles + service + hourly rate + call-out fee [SRC].
- **Values an OEM must guarantee:**
  - battery capacity at 8 years;
  - downtime ≤ 5 days/year;
  - response within 2 h;
  - fines of 2,000 DKK/day.

  [SRC: Ressourceindsamling]
- **The route simulation the OEMs already do.** Volvo and Scania run a route simulation in the offer phase, and Scania asks buyers to contact them before fixing battery size [SRC: 4-leaf].

[JUDGEMENT] The missing result is an "offer sheet": several OEM offers on the same routes, side by side, scored with the buyer's own weights, plus the values each OEM would need to guarantee.

---

## 4. Trust and audit gaps

- **Run fingerprint:** engine version, date and time, a hash of the inputs [SRC: VECTO MRF §3].
- **Simulation quality check:**
  - average, minimum and maximum speed;
  - maximum acceleration and deceleration;
  - total distance;
  - share of time at full power.

  [SRC: VECTO MRF 2.2]
- **A list of every standard value and assumption used, with its source,** like PVsyst's loss list.
- **Model status per result:** tested against VECTO, in testing, or not built yet. Battery losses, cold tyres and drivetrain maps are "in testing" [SRC: Kiro prompt §B].
- **Known decisions stated in every report.** Example: the crosswind yaw angle is capped at 10° [SRC: engine memory, 6 Oct].

---

## 5. Presentation problems Bob raised (26 Oct)

- **Labels too far from values.** Field titles are small and grey, with a one-line description underneath, and sit far from the value or input field. [JUDGEMENT] The label, value and unit should sit on one line.
- **Bars with no information.** Example: the "use of limit" meters in the feasibility checks repeat the number next to them.
- **Long tables with no hierarchy.**
- **Charts too high-level.** No component split, no monthly balance, no confidence band.
- **Cost page:** one simple chart.

---

## 6. Not decided here

This is an inventory only. Bob decides what to build and in what order.
