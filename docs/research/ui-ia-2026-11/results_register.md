# Master results register (14 Nov 2026)

One row per result. Full columns in `results_register.csv`. Documents: FR feasibility report, GC grid connection application, TA tender annex, FM financial model, GR grant application data, CP client presentation. Audiences: F fleet owners, M municipalities and public buyers, H housing associations, O truck makers and dealers, C charge point operators and grid companies.

**Rows: 114** (6 are candidates from other tools). Year-8 rows: 37.

## Count by page and level

| Page | headline figure | status line | section | table | chart | document only | Total |
|---|---|---|---|---|---|---|---|
| Overview | 4 | 2 | 0 | 9 | 1 | 0 | 16 |
| Energy | 3 | 0 | 0 | 3 | 6 | 0 | 12 |
| Audit | 0 | 2 | 3 | 2 | 0 | 0 | 7 |
| Battery | 5 | 2 | 3 | 2 | 3 | 0 | 15 |
| Charging | 4 | 0 | 2 | 2 | 2 | 0 | 10 |
| Grid and flexibility | 7 | 4 | 2 | 2 | 5 | 0 | 20 |
| Cost | 5 | 0 | 3 | 3 | 4 | 0 | 15 |
| CO₂ | 2 | 0 | 0 | 1 | 3 | 0 | 6 |
| Offers | 1 | 0 | 1 | 1 | 0 | 1 | 4 |
| Documents | 0 | 0 | 0 | 0 | 0 | 7 | 7 |
| Compare | 0 | 0 | 1 | 1 | 0 | 0 | 2 |

## Overview

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| ov.verdict | Verdict per vehicle and fleet (can switch / cannot) |  | Can my vehicles run electric? | status line | no chart: a sentence with a pass mark says it | yes | designed |
| ov.first_fail | First failing check |  | What stops this from working first? | status line | no chart | yes | designed |
| ov.chk_battery_new | Check: battery covers the hardest day when new | margin % | Is the battery big enough today? | table | no chart | no | planned |
| ov.chk_battery_y8 | Check: battery covers the hardest day at year 8 | margin % | Will the battery still do my hardest winter day in year 8? | table | no chart: pass or fail with margin | yes | planned |
| ov.chk_full | Check: every vehicle full before it leaves | h to spare | Will every truck be ready by departure? | table | no chart | no | planned |
| ov.chk_grid | Check: charging fits the grid connection | kW to spare | Does it fit my connection? | table | no chart | no | planned |
| ov.chk_route | Check: route fits the shift | h to spare | Does the round fit in the shift? | table | no chart | no | designed |
| ov.chk_weight | Check: load within the weight limit | t to spare | Can it carry the load? | table | no chart | no | designed |
| ov.fig_battery | Battery in each vehicle | kWh | How big a battery do I need? | headline figure | no chart: a number says it | yes | planned |
| ov.fig_chargers | Chargers (count, power) | -, kW | How many chargers, how big? | headline figure | no chart | no | planned |
| ov.fig_peak | Depot peak | kW, A | What is my depot peak? | headline figure | no chart | no | planned |
| ov.fig_saving | Saved against diesel over the period | DKK | What do I save? | headline figure | no chart | no | planned |
| ov.context | Input context as visuals (distance and payload across the day, shift window, depot, weather case) |  | What did I actually enter? | chart | small multiples: one tiny line per input (payload along route; shift bar; temperature), because Bob asked for input context as visuals | no | designed |
| ov.fleet_table | Results per fleet row (vehicles, route, load, hardest day, battery, charger, full again) |  | What does each row of my fleet need? | table | table, one row per fleet row | yes | designed |
| cand.suitability_list | Per-vehicle suitability list with first failing reason (range, charging viability, lifetime cost) |  | Which of my vehicles can switch and why not the others? | table | table with a reason column | yes | candidate |
| cand.column_choice | Choose which columns the results tables show, and export to CSV |  | Can I choose and export columns? | table | table control | no | candidate |

## Energy

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| en.kwh_day | Energy per day (average, hardest day, P50 / P90 across weather years) | kWh | How much energy per day, and on my worst day? | headline figure | no chart | yes | designed |
| en.kwh_km | Energy per km, per t-km, per tonne collected | kWh/km, kWh/t-km | How efficient is it? | headline figure | no chart | no | designed |
| en.balance | Component energy balance (air, rolling, grade, inertia, brakes, gearbox, axle, motor, battery loss, each aux, HVAC, PTO, regen) | kWh | Where does the energy go? | chart | horizontal waterfall: shows how parts add up to a total (VECTO .vsum split) | no | designed |
| en.monthly | Monthly balance table (km, °C, driving, aux, HVAC, regen, at battery, charger losses, from grid, peak kW, cost) | kWh | What does each month look like? | table | table: PVsyst report convention, numbers right-aligned | yes | planned |
| en.loss | Loss diagram (grid to charger to battery to motor to gearbox to wheel to air, roll, grade, brakes; aux branch) | % of previous | Where are the losses? | chart | flow (Sankey-style) loss diagram: PVsyst convention; each loss is a % of the previous quantity, not additive | no | planned |
| en.p50p90 | P50 / P90 across weather years | kWh | How bad is a bad year? | chart | range band on the monthly line: shows spread without Monte Carlo | yes | planned |
| en.time_split | Time stopped / accelerating / cruising / coasting / braking | h, % | How is the day made up? | chart | single stacked bar: parts of one whole | no | designed |
| en.profile | Speed and battery power over the day | km/h, kW | What does one day look like? | chart | two aligned lines on a shared time axis | no | designed |
| en.sens_t | Sensitivity per extra tonne and per °C | kWh/t, kWh/K | What does a tonne or a cold day cost? | table | two-row table, a number says it | yes | planned |
| en.season | Winter against summer | kWh | How different is winter? | chart | two bars side by side | yes | planned |
| en.kwhkm_temp | Expected kWh/km by month and temperature (FynBus shape) | kWh/km | Can I compare prediction with what my trucks log? | table | table in FynBus Bilag 1 §2.21 shape | yes | planned |
| en.optime | Operating time (aktionstid), not only range | h | How many hours can it work? | headline figure | no chart | yes | planned |

## Audit

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| en.simqa | Simulation quality check (avg/min/max speed, max acceleration and deceleration, distance, share of time at full power) |  | Is the simulation sane? | table | table | no | designed |
| au.fingerprint | Run fingerprint (engine version, date, input hash) |  | Can I trust and repeat this run? | section | no chart | no | designed |
| au.sources | Every standard value and assumption with its source (PVsyst loss-list style) |  | Where does each number come from? | table | table grouped by page, filter by tag | no | designed |
| au.labels | Label on every number (measured / standard / assumption) |  | Is this a fact or an assumption? | status line | inline mark | no | designed |
| au.status | Model status per result (validated / in testing / not built) |  | Is this result tested? | status line | inline mark | no | planned |
| au.decisions | Known decisions stated (10° yaw clamp, reference driver mass, fresh-air term) |  | What was decided for me? | section | list | no | designed |
| cand.calc_report | Calculation report: number of runs, feasible and infeasible cases, suggestions for missing items |  | Why did my run fail or warn? | section | list | no | candidate |

## Battery

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| bat.installed_usable | Installed against usable (nominal vs usable) | kWh | What is nominal and what is usable? | headline figure | paired figures | yes | planned |
| bat.usable_y8 | Usable capacity at year 8 | kWh | What is left at year 8? | headline figure | no chart | yes | planned |
| bat.hardest_y8 | Hardest day at year-8 capacity | kWh, margin % | Will the battery still do my hardest winter day in year 8? | section | bar of day need against capacity new and at year 8: one comparison, same axis | yes | planned |
| bat.winter_y8 | Winter at year 8 (labelled conservative case until cold-weather heating is validated) | kWh | What if it is cold and the battery is old? | section | same bars with a winter case marked | yes | planned |
| bat.min_kwh_y8 | Minimum usable kWh at year 8 in winter for these routes | kWh | What must I write in the tender? | headline figure | no chart: a number | yes | planned |
| bat.score_pos | Position on the tender score curve (e.g. 250 to 450 kWh gives 1 to 10 points) | points | How many points is my battery worth? | chart | a line with a marker: the curve is the buyer's, the marker is the bid | yes | planned |
| bat.margin | Margin left on the hardest day | % | How close am I? | headline figure | no chart | yes | planned |
| bat.soc_return | State of charge on return per vehicle across the year | % | How empty do trucks come home? | chart | distribution (strip per month) because many days | yes | planned |
| bat.trade | Battery against payload trade-off | kWh, t | What do I give up in load? | chart | scatter of options: two quantities against each other | no | planned |
| bat.payload_left | Payload left on each route | t | How much can I carry? | table | table | no | designed |
| bat.vs_diesel | Payload against diesel | t | Do I carry less than diesel? | table | table | no | planned |
| bat.passport | Predicted battery passport values after 8 years (energy throughput, equivalent full cycles, charge rates, time at hot and cold) |  | What will my battery data look like in year 8? | section | table of passport fields | yes | planned |
| bat.run_out | When capacity would run out | year | When does the battery fail my route? | headline figure | no chart | yes | planned |
| bat.fast_charge | Check: at least 150 kW between 10 % and 75 % | yes / no | Does it meet the tender's charging window? | status line | no chart | no | planned |
| au.holdback | Hold-back rule: winter shown as labelled conservative case until cold-weather heating is validated |  | Can I rely on winter? | status line | inline notice | yes | designed |

## Charging

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| ch.chargers | Chargers: size, count, ratio to trucks | kW, - | How many chargers? | headline figure | no chart | no | planned |
| ch.sessions | Per-session table (arrival SOC, kWh, start, end, power, finish, slack before departure) |  | What happens at each charge? | table | table with right-aligned numbers | no | planned |
| ch.gantt | Fleet schedule (Gantt) |  | Who charges when? | chart | Gantt: shows time overlap of sessions per charger | no | designed |
| ch.busy | Charger busy hours | h | Are chargers used enough? | headline figure | no chart | no | planned |
| ch.strategies | Strategies compared (Lowest cost / Grid-friendly / Ready earliest) |  | Which plan is best for me? | table | small comparison table: 3 columns, same rows | no | designed |
| ch.robust | Robustness: one charger down, late return, cold week |  | What if something goes wrong? | section | table of cases with pass/fail | yes | planned |
| ch.spare | Spare trucks needed in a cold week | trucks | How many spare trucks? | headline figure | no chart | yes | planned |
| ch.between | Charging between shifts and at the tip site |  | Can I top up between shifts? | section | table | no | planned |
| ch.losses | Charging losses | kWh | How much is lost in charging? | headline figure | no chart | no | planned |
| cand.hourly_depot_soc | State of charge of the whole fleet over the day | % | How full is my fleet at each hour? | chart | line: one quantity over time | no | candidate |

## Grid and flexibility

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| gr.peak | Depot peak (kW and A) | kW, A | What is my peak in amperes? | headline figure | no chart | no | planned |
| gr.load_hour | Load hour by hour | kW | When is the load high? | chart | step line for the hardest day with the connection as a limit line: shows room and overload | no | designed |
| gr.ldc | Load duration curve | kW | How often is the load high? | chart | sorted line: only way to show frequency | no | planned |
| gr.required | Required connection (greenfield) | A, kW | How big a connection must I order? | headline figure | no chart | no | planned |
| gr.category | Customer category | - | Which category am I? | status line | no chart | no | planned |
| gr.fee | Connection fee from the price list | DKK | What does the connection cost? | headline figure | no chart | no | designed |
| gr.lead | Lead-time band | months | How long will I wait? | headline figure | no chart: a band in words | no | planned |
| gr.fna_bna | FNA against BNA side by side |  | Full or limited access? | section | two-column table | no | planned |
| gr.bna_whatif | BNA what-if: does a cut (e.g. 50 % from 22:00 to 02:00) still leave every truck ready? |  | Can I survive a cut? | section | result line plus the load chart with the cut shaded | no | planned |
| gr.cap_charge | Capacity charge (average of the 10 busiest hours) with and without smart charging | DKK/month | What does the peak cost? | headline figure | no chart | no | planned |
| gr.growth | Peak growth with fleet phases | kW | When does the connection run out? | chart | step line by phase | no | planned |
| gr.scores | Capacity-friendly and system-friendly scores |  | Is it good for the local grid? | table | two numbers | no | planned |
| gr.amps_saved | Amperes saved by load management | A | What does load management save? | headline figure | no chart | no | planned |
| fx.updown | Up and down flexibility per hour within readiness | kW | How much can I offer? | chart | two bands above and below zero | no | planned |
| fx.products | Which products the fleet could qualify for (check against minimum bid and response time, not a revenue promise) |  | Could I sell flexibility? | table | table: product, minimum bid, response, qualifies yes / no | no | planned |
| fx.aggr | Aggregator needed |  | Do I need an aggregator? | status line | no chart | no | planned |
| fx.dso | DSO pilot terms |  | What do the DSO terms say? | status line | no chart | no | planned |
| fx.hours | Hours per week available | h | How long am I available? | headline figure | no chart | no | planned |
| fx.v2g | V2G readiness |  | Is my kit V2G ready? | status line | no chart | no | planned |
| fx.rebound | Rebound after curtailment | kW | What happens after a cut? | chart | line | no | planned |

## Cost

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| co.total | Total cost and per km, month, year, period (electric against diesel) | DKK | What does it cost in total? | headline figure | no chart | no | designed |
| co.breakeven | Break-even (months or year) | months | When does it pay back? | headline figure | no chart | no | designed |
| co.cashflow | Year-by-year cash flow | DKK | What happens each year? | table | table: years as columns, lines as rows, plus a cumulative line chart | no | designed |
| co.cumulative | Cumulative saving against diesel | DKK | When do I come out ahead? | chart | one line with zero line: crossing point is the answer | no | designed |
| co.lines | Cost by line | DKK | Where does the money go? | chart | horizontal bars sorted by size: parts, not time | no | designed |
| co.npv | NPV (Vejdirektoratet rule: year 1 discounted one period) | DKK | What is it worth in today's money? | headline figure | no chart | no | planned |
| co.fin | Financing and residual | DKK | What do loan, lease and cash cost? | section | table | yes | planned |
| co.elsplit | Electricity cost split (spot / tariff / tax) | DKK | What am I paying for in a kWh? | chart | stacked bar: parts of one whole | no | planned |
| co.sens | Sensitivity (electricity, diesel, km/year, residual, battery replacement, interest) | DKK | What if prices differ? | chart | tornado: ranks the inputs by effect | yes | planned |
| co.service | Service contract 8-10 years | DKK | What does 8 to 10 years of service cost? | section | table | yes | planned |
| co.downtime | Downtime cost | DKK | What do breakdowns cost? | headline figure | no chart | yes | planned |
| co.depot | Depot cost split across trucks and its amortisation | DKK | What does the depot cost per truck? | table | table | no | planned |
| co.alt | Alternatives (HVO, biogas) | DKK | Is HVO or biogas cheaper? | table | table | no | planned |
| co.perton | Cost per t-km and per tonne collected | DKK | What does a tonne cost? | headline figure | no chart | no | planned |
| co.grant | Grant-ready numbers (budget lines, trucks charging daily, number and power of chargers, lease NPV) |  | What goes in the grant form? | section | table matching the VD form | no | planned |

## CO₂

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| c2.year | CO2 per year | t | How much CO2 per year? | headline figure | no chart | no | designed |
| c2.saved | CO2 saved over the period | t | How much do I save? | headline figure | no chart | no | designed |
| c2.path | Grid factor path by year | g/kWh | How does the grid get cleaner? | chart | line over years | no | designed |
| c2.hours | CO2 at charging hours | g/kWh | Is night charging cleaner? | chart | line by hour | no | planned |
| c2.lca | Life cycle (production and well-to-wheel) | t | What is the full life-cycle footprint? | chart | stacked bar: parts of one whole | no | planned |
| c2.alt | Comparison with HVO, biogas and B7 | t | How does it compare with other fuels? | table | table | no | planned |

## Offers

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| of.sheet | Offer sheet: several bids run on the same routes and scored with the buyer's weights |  | Which bid is best for my routes? | section | table of bids with scores, plus score bars per criterion | yes | planned |
| of.guarantee | Values each bidder would need to guarantee (year-8 capacity, downtime) |  | What must each bidder promise? | table | table | yes | planned |
| of.pto | Crane and compactor energy and peak at the same time | kWh, kW | Can both run at once? | headline figure | no chart | no | planned |
| of.vpto | kWh per lift or compaction cycle and per shift, exported as a VECTO PTO profile | kWh | What is the cycle energy? | document only | no chart (file export) | no | planned |

## Documents

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| dc.report | Feasibility report |  | The full study | document only | no chart | yes | designed |
| dc.grid | Grid connection application (Radius screening fields: address, desired power, connection type, commissioning date, grid services yes/no) |  | The application for the grid company | document only | no chart | no | designed |
| dc.tender | Tender annex |  | The annex for a tender | document only | no chart | yes | designed |
| dc.fin | Financial model (spreadsheet) |  | The numbers in a sheet | document only | no chart | no | designed |
| dc.grant | Grant application data (VD form) |  | The data for a grant form | document only | no chart | no | designed |
| dc.pres | Client presentation (decision, cost, risks) |  | The decision pack | document only | no chart | yes | designed |
| cand.presentation | Customer presentation export of all results prepared as pages |  | Can I show this to the board? | document only | no chart | no | candidate |

## Compare

| id | Result | Unit | Question it answers | Level | Chart and why | Year 8 | Status |
|---|---|---|---|---|---|---|---|
| cm.diff | Compare runs: inputs changed and results changed |  | What changed between two runs? | section | two-column table with changed inputs on top, results deltas below | yes | designed |
| cand.sensitivity_grid | Results table over several values of one input (sensitivity cases) |  | What happens across a range of prices or sizes? | table | table, one row per case, ranked by a chosen column | yes | candidate |

