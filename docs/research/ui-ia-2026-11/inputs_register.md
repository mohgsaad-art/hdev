# Master input register (14 Nov 2026)

One row per input. The full 23 columns are in `inputs_register.csv`. This page shows the short view, grouped by proposed page. Plain English. Tags: STD standard, LIB library, EXT external fetch, ASSUMP assumption, NO SOURCE, OPEN, none (copied from the inventory, not chosen by Kiro).

**Rows: 274.** Year-8 rows: 40. Demo fields (174 in `DEFS`) with a register row: 174 of 174 (checked by script). Inventory rows (178 table rows in sections 1-14) placed: 178 of 178 (`inventory_coverage_check.csv`, rule-based, first match wins).

## Count by page and tier

| Page | main | named popup | engineering view | hidden | Total |
|---|---|---|---|---|---|
| Project | 8 | 0 | 0 | 0 | 8 |
| Fleet | 54 | 62 | 7 | 5 | 128 |
| Depot and grid | 12 | 7 | 0 | 0 | 19 |
| Charging | 6 | 20 | 0 | 0 | 26 |
| Weather | 8 | 13 | 2 | 2 | 25 |
| Prices | 6 | 7 | 0 | 0 | 13 |
| Costs | 11 | 10 | 0 | 0 | 21 |
| Taxes, grants and CO₂ | 6 | 4 | 0 | 0 | 10 |
| Tender (shown only for tender projects) | 9 | 0 | 0 | 0 | 9 |
| Compare | 2 | 0 | 0 | 0 | 2 |
| Check and run | 0 | 0 | 0 | 13 | 13 |
| **Total** | 122 | 123 | 9 | 20 | 274 |

Status count: built 76, designed 99, planned 83, open 16.

Reading the tier column: **main** = on the page; **named popup** = in a popup named after what it holds; **engineering view** = only shown when the user switches to the engineering view; **hidden** = filled from `defaults.py`, never typed (still listed in the report).

## Project

### Project

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| proj.name | Project name |  | none | main | no | project |
| proj.scen | Scenario name |  | none | main | no | scenario |
| proj.purpose | What is this project for? |  | none | main | no | project |
| proj.mode | How should charging be worked out? (sizing or step by step) |  | OPEN (no default decided) | main | no | project |
| proj.brand | Brand-neutral comparison for tenders |  | none | main | no | project |
| proj.view | View: client / OEM / engineering |  | none | main | no | project |
| proj.lang | Language and units display |  | none | main | no | project |
| scn.assistant | Assistant fills inputs from messy data (spreadsheets, telematics dumps, descriptions) |  | none | main | no | scenario |

## Fleet

### Schedule template

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| cal.fleet_size | Number of vehicles in this row | trucks | none | main | no | fleet row |
| cal.group_name | Group name |  | none | main | no | fleet row |
| cal.shift_out | Leaves the depot (shift start) | hh:mm | none | main | no | shift/calendar |
| cal.shift_back | Back at the depot (shift end) | hh:mm | none | main | no | shift/calendar |
| cal.days | Working days (Mon to Sun) |  | none | main | no | shift/calendar |
| cal.day_factor | Reduction factor on selected days (e.g. Saturday runs half) | % | OPEN | named popup: Days and exceptions | no | shift/calendar |
| cal.holidays | Public holidays (country calendar or own dates) |  | none; OPEN which calendar source (inventory 1). Prompt: computed Danish holidays, Store Bededag abolished from 2024 | main | no | shift/calendar |
| cal.shutdown | Shutdown date ranges (e.g. summer closure) | date range | none | named popup: Days and exceptions | no | shift/calendar |
| cal.exceptions | Calendar exceptions (route, days, departure/return by date) |  | none | named popup: Days and exceptions | no | shift/calendar |
| cal.shifts | Several shifts per day (second shift on the same vehicle) |  | none | named popup: Days and exceptions | no | shift/calendar |
| cal.sessions | Session list per vehicle and date (carried across days and weekends) |  | n/a | hidden | no | shift/calendar |
| cal.opdays | Operating days a year | days | calculated | main | no | shift/calendar |
| asg.route | Route (per fleet row) |  | none | main | no | shift/calendar |
| asg.payload | Payload profile (per fleet row) |  | none | main | no | shift/calendar |
| asg.pto | PTO profile (per fleet row) |  | none | main | no | shift/calendar |
| asg.vehicle | Vehicle (per fleet row) |  | none | main | no | shift/calendar |
| asg.schedule | Schedule (per fleet row) |  | none | main | no | shift/calendar |
| asg.bulk | Apply to many rows at once |  | n/a | main | no | shift/calendar |
| lib.save_template | Save as template / save as my own |  | empty | main | no | shift/calendar |
| lib.vecto_templates | VECTO templates (pre-filled, locked) |  | STD | main | no | shift/calendar |

### Route template

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| rt.source | Where does the route come from? (VECTO cycle / typed / GPS log / describe it) |  | none | main | no | route |
| rt.vdri_mission | VECTO standard cycle (LongHaul, RegionalDelivery, UrbanDelivery, MunicipalUtility, Construction) |  | none | main | no | route |
| rt.gps_file | GPS log upload |  | none | main | no | route |
| rt.ai_text | Describe the route in words (assistant) |  | none | main | no | route |
| rt.leg_km | Distance (per day, or per leg in the stop table) | km | none | main | no | route |
| rt.road_type | Type of streets (deep urban / urban / non-urban) |  | none | main | no | route |
| rt.stops_n | Stops per day |  | none | main | no | route |
| rt.dwell | Time at each stop | s | 45 min per stop, ASSUMP (dt-cargo median is 22 min; needs a source) | main | no | route |
| rt.speed | Speed per road type | km/h | 30 / 50 / 80, ASSUMP | named popup: Speed and hills | no | route |
| rt.grade | Grade (slope) | % | 0 (flat), ASSUMP | named popup: Speed and hills | no | route |
| rt.depart | Departure time at depot (route start time) | hh:mm | none | main | no | route |
| rt.name | Route name (save to library) |  | none | main | no | route |
| rt.altitude | Altitude / pressure (per route or per row) | m | OPEN (per route or per row) | hidden | no | route |
| rt.window | Per-leg time windows |  | OPEN | named popup: Stops (stop table) | no | route |

### Stops (stop table)

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| stop.table | Stop table (stop, distance from depot, time at stop, payload after, PTO on) |  | from route source | main | no | route |
| stop.time | Stop time (per stop) | s | from source | main | no | stop |
| stop.payload | Payload after this stop (per stop) | t | none | main | no | stop |
| stop.pto_on | PTO works at this stop (per stop) |  | Off | main | no | stop |

### Payload template

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| pl.basis | Which payload? (VECTO reference / max payload / reference plus max run / my own) |  | OPEN (not decided) | main | no | load |
| pl.shape | How does payload change during the day? (constant / linear / per stop) |  | none | main | no | load |
| pl.start | Payload (constant, or when leaving) | t | VECTO reference payload by group and mission, STD (group 5 long haul 19,300 kg reference, 2,600 kg low) | main | no | load |
| pl.end | Payload at the end of the route | t | none (linear only) | main | no | load |
| pl.custom | Payload per stop | t | none | main | no | stop |
| pl.save | Saved payload profile |  | empty | main | no | load |

### PTO template

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| pto.type | When does the powered equipment work? (none / at stops / all the time) |  | Off | main | no | body |
| pto.stop_kwh | Energy per stop (or constant stop power) | kWh | VECTO refuse profile (23 s, 0.14993 kWh per stop), STD; mixer default OPEN | main | no | load |
| pto.stop_s | Working time per stop | s | 23 s, STD (refuse) | main | no | load |
| pto.profile | Power profile over time (instead of one figure) | s, W | none | main | no | load |
| pto.always_w | Power while on shift (equipment that is always on) | W | none | main | no | load |
| pto.drive_w | Power while driving (drive PTO) | W | none | main | no | load |
| pto.eff_stop | Efficiency at stops |  | 1.0, ASSUMP | named popup: Efficiency and drive | no | load |
| pto.eff_drive | Efficiency while driving |  | 1.0, ASSUMP | named popup: Efficiency and drive | no | load |
| pto.own_motor | Does the body have its own electric motor? |  | none | named popup: Efficiency and drive | no | load |
| pto.eff_motor | Efficiency of the electric PTO motor |  | NO SOURCE | named popup: Efficiency and drive | no | load |
| pto.stop_as_pto | Count the whole stop as working time (non-VECTO option) |  | Off, ASSUMP (non-VECTO option, must be labelled) | named popup: Efficiency and drive | no | load |
| pto.fridge | Fridge or TRU unit (ATP K value or class, box dimensions, set temperature, COP, heating mode) |  | none | named popup: Fridge unit | no | load |
| pto.drag | PTO shaft drag (PTO-tech.csv) |  | none | engineering view | no | load |
| pto.save | Saved PTO profile |  | empty | main | no | load |

### Vehicle template: Vehicle and body

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| veh.source | Where does the vehicle data come from? (library pick / I enter it) |  | none | main | no | vehicle |
| veh.library | Library vehicle (EEA 2024-25, one row per exact configuration) |  | none | main | no | vehicle |
| veh.group | VECTO vehicle group (1-16) |  | none | main | no | vehicle |
| veh.curb_mass | Chassis weight, empty (curb mass) | kg | LIB if picked, else none | main | no | vehicle |
| veh.body_type | Body type (VECTO body list, e.g. B1) |  | none | main | no | vehicle |
| veh.body_mass | Body weight | kg | VECTO standard by body type, STD (e.g. B1 1,600 kg) | main | no | vehicle |
| veh.trailer | Trailer type and weight | kg | VECTO standard by type, STD (e.g. ST1 7,500 kg) | named popup: Trailer and wheels | no | vehicle |
| veh.gvw | Gross vehicle weight / max payload | t | LIB if picked, else none | main | no | vehicle |
| veh.m_red_wheels | Weight of the rotating wheels (m_red_wheels) | kg | none (OPEN source) | named popup: Trailer and wheels | no | vehicle |
| veh.diesel_use | Diesel the truck uses today | l/100 km | none | main | no | vehicle |
| veh.cdxa | Air drag area (CdxA) | m2 | VECTO CdxA_Default by group, STD (group 4: 8.4, 5: 8.7, 9: 8.5, 16: 9.0) | named popup: Air drag and size | no | vehicle |
| veh.cdxa_file | Air drag by wind angle, from the maker (CdxA vs yaw or speed) |  | none; OPEN upload format | named popup: Air drag and size | no | vehicle |
| veh.height | Vehicle height | m | VECTO reference height by group, STD (groups 1/1s 3.6; 2 3.75; 3 3.9; 4/5/7-12 4.0; 6 3.75; 13-16 3.6) | named popup: Air drag and size | no | vehicle |
| veh.yaw_coef | Yaw coefficients a1-a3 |  | VECTO VCDV_parameters.csv by vehicle type, STD | hidden | no | vehicle |
| veh.p_max | Largest motor power (P_max) | kW | LIB if picked, else none | main | no | vehicle |

### Vehicle template: Tyres

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| veh.crr | Tyre rolling resistance (Crr) | N/kN | none (OPEN: standard value from resolver?) | named popup: Tyres | no | vehicle |
| veh.r_dyn | Tyre radius when rolling (r_dyn) | m | none | named popup: Tyres | no | vehicle |
| veh.load_idx | Tyre load index |  | none | named popup: Tyres | no | vehicle |
| veh.kt | Cold-tyre factor Kt |  | 0.006 if load index > 121, else 0.010; planned, OPEN | engineering view | no | vehicle |
| veh.wet | Road surface (dry / wet / icy) |  | OPEN (not built) | named popup: Tyres | no | vehicle |
| veh.theta_red | Inertia reduction factor (theta_red) |  | none (OPEN source) | engineering view | no | vehicle |

### Vehicle template: Drivetrain

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| veh.motor | Motor / e-axle / iePC (library or manual) |  | LIB if picked | named popup: Drivetrain | no | vehicle |
| veh.gear_type | Gearbox: single speed or several gears |  | none | named popup: Drivetrain | no | vehicle |
| veh.i_total | Total gear ratio (i_total), per gear row |  | none (lowest gear if unknown) | named popup: Drivetrain | no | vehicle |
| veh.j_rotor | Rotor inertia (J_rotor) | kg m2 | NO SOURCE (no fleet default) | engineering view | no | vehicle |
| veh.eff_method | Efficiency method (loss maps / separate efficiencies) |  | OPEN (calibrate to EEA vs V-C bus method) | named popup: Drivetrain | no | vehicle |
| veh.loss_maps | Loss maps for motor, inverter and gearbox |  | VECTO generic E2 standard values, STD | named popup: Drivetrain | no | vehicle |
| veh.eff_motor | Motor efficiency |  | 0.95, NO SOURCE (placeholder in code) | named popup: Drivetrain | no | vehicle |
| veh.eff_inv | Inverter efficiency |  | 0.95, NO SOURCE (placeholder in code) | named popup: Drivetrain | no | vehicle |
| veh.eff_gb | Gearbox efficiency |  | 0.98, NO SOURCE (placeholder in code) | named popup: Drivetrain | no | vehicle |
| veh.v_no_regen | No braking energy back below | km/h | 5 km/h in code (list: 5 km/h hidden constant per 26 Oct list) | named popup: Braking energy | no | vehicle |
| veh.p_regen | Largest braking power back | kW | none = no cap | named popup: Braking energy | no | vehicle |
| veh.eff_regen | Efficiency when braking |  | none | named popup: Braking energy | no | vehicle |

### Vehicle template: Battery

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| bat.mode | Battery: let the tool size it / I have a battery size |  | none | main | no | battery |
| bat.installed | Installed battery (kWh) | kWh | LIB if picked | main | no | battery |
| bat.usable_oem | OEM-usable energy (kWh) | kWh | none | named popup: Battery details | no | battery |
| bat.usable_share | Usable share of the battery (VECTO about 0.855 x installed) | % | about 0.855 x installed, STD approximate, verify | named popup: Battery details | no | battery |
| bat.mass | Battery weight | kg | LIB if picked (mode A); computed in mode B | named popup: Battery details | no | battery |
| bat.chem | Cell chemistry |  | none | named popup: Battery ageing | yes | battery |
| bat.dc_max | Fastest DC charging power | kW | none | named popup: Battery details | no | battery |
| bat.connector | Charging connector (CCS2 / MCS) |  | none | named popup: Battery details | no | battery |
| bat.c_rate | Largest charging rate (C) by state of charge | C | 0.9 C up to 80 % SOC, 0 at 100 %, STD (Annex Xb App. 10) | named popup: Battery details | no | battery |
| bat.ocv | Cell voltage curve (OCV at 0/10/50/90/100 % SOC) | - | 0.88 / 0.94 / 1.00 / 1.06 / 1.12 x V_nom, STD (Annex Xb App. 10) | named popup: Battery voltage and resistance | no | battery |
| bat.ri | Internal resistance Ri (2/10/20/120 s) | mOhm Ah | 210 / 240 / 270 / 390, STD (Annex Xb App. 10, HEBS) | named popup: Battery voltage and resistance | no | battery |
| bat.v_nom | Nominal voltage | V | none | named popup: Battery voltage and resistance | no | battery |
| bat.soc_window | SOC window (lowest and highest allowed) | % | none; OPEN | named popup: Battery details | no | battery |
| bat.heating | Battery heating and conditioning | W | none | engineering view | no | battery |
| age.guarantee | Battery capacity guaranteed at year 8 (usable, %) | % | none; demo sample 70 % ASSUMP (Rambøll 2023: warranties often go down to 70 %) | main | yes | battery |
| age.warranty_years | Warranty years | years | none | named popup: Battery ageing | yes | battery |
| age.warranty_km | Warranty km | km | none | named popup: Battery ageing | yes | battery |
| age.check_year | Year the guarantee is checked at | years | 8 | named popup: Battery ageing | yes | battery |
| age.soh_curve | State-of-health curve or table (OEM) | % | none | named popup: Battery ageing | yes | battery |
| age.cycle_life | Cycle and calendar life | cycles / years | none | named popup: Battery ageing | yes | battery |
| age.replace_year | Battery replacement (year, cost) | year, DKK | none | named popup: Battery ageing | yes | company (finance) |
| age.residual_link | Residual value linked to remaining state of health (KIT formula: scrap 15 % + 85 % x SoH, x battery cost) | % | OPEN (formula from tools review) | named popup: Battery ageing | yes | company (finance) |
| age.passport | Battery passport fields (rated capacity and fade, power and fade, Ri increase, round-trip efficiency, expected lifetime, state of certified energy) |  | none | engineering view | yes | battery |
| siz.glider_mass | Glider mass (truck without battery) | kg | none (source needed) | named popup: Size the battery | yes | battery |
| siz.pack_density | Pack energy density | kWh/kg | none (source needed, KIT table exists) | named popup: Size the battery | yes | battery |
| siz.step | Battery size step | kWh | none | named popup: Size the battery | yes | battery |
| siz.rule | Sizing rule (hardest day at year 8, with margin) | % | none | named popup: Size the battery | yes | battery |
| siz.soc_buffer | State-of-charge buffer | % | none | named popup: Size the battery | yes | battery |

### Vehicle template: On-board systems

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| aux.es | Electrical system power (ES) | W | VECTO standard by group, STD (value not listed in inventory) | named popup: On-board systems | no | vehicle |
| aux.ps | Air system power for brakes and suspension (PS) | W | VECTO standard, STD | named popup: On-board systems | no | vehicle |
| aux.sp | Power steering (SP) | W | VECTO standard method, STD | named popup: On-board systems | no | vehicle |
| aux.sp_axles | Steered axles and steering technology per axle |  | VECTO SP tables, STD | named popup: On-board systems | no | vehicle |
| aux.cond | Battery and motor cooling (Cond) | W | VECTO standard, STD (open question: does it run while coasting) | named popup: On-board systems | no | vehicle |
| aux.always_pto | Equipment that is always on (W) | W | none | named popup: On-board systems | no | vehicle |
| aux.factors | Factors per load (ES 0.7, PS 1.0, HVAC 1.25 (1.0 in thermal mode), SP 0.7, Cond 1.0) |  | STD | engineering view | no | vehicle |
| aux.pto_eff | PTO efficiency used in P_aux |  | 1.0 ASSUMP | hidden | no | vehicle |
| aux.depot_rule | No auxiliary power during depot charging |  | On, design decision | hidden | no | vehicle |

## Depot and grid

### Site

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| dep.name | Depot name |  | none | main | no | depot site |
| dep.mode | Is there a grid connection today? (brownfield / greenfield) |  | none | main | no | depot site |
| dep.address | Site address |  | none | main | no | depot site |
| dep.spaces | Parking spaces with room for a charger, and power per space | -, kW | none | named popup: Parking | no | depot site |
| dep.growth | Fleet growth phases (e.g. 10 trucks now, up to 70 within 48 months) | trucks, months | none | named popup: Growth phases | no | depot site |
| dep.buffer | Buffer battery on site (planned) | kWh, kW | none | named popup: Buffer battery | no | depot site |
| dep.housing | Housing site mode: residents with a right to a charge point (building supply, number of dwellings, spaces) |  | none | named popup: Residents and spaces | no | depot site |

### Grid connection

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| dep.dso | Grid company (Radius, Cerius, N1, TREFOR El-net, other) |  | none | main | no | depot site |
| dep.category | Customer category (C, B-lav, B-høj, A-lav, A-høj) |  | none | main | no | depot site |
| dep.conn_size | Connection size today (A or kW, with unit switch) | A / kW | none (brownfield) | main | no | depot site |
| dep.access | Access to the grid: full (FNA) / limited (BNA) / stepwise (TFL) |  | none | main | no | depot site |
| dep.bna_cut | Limited-access what-if: cut in power, from, to | % / hh:mm | none | named popup: Limited access what-if | no | depot site |
| dep.lead_time | Lead-time band (existing application / free capacity?) |  | none | named popup: Connection process | no | depot site |
| dep.commission | Desired commissioning date | date | none | named popup: Connection process | no | depot site |

### Building load

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| dep.base_mode | Building load: one figure / hourly meter data (Eloverblik via MitID) / CT-logger upload |  | none | main | no | depot site |
| dep.base_kw | Building load (fixed) | kW | none | main | no | depot site |
| dep.eloverblik | Connect to Eloverblik |  | Off | main | no | depot site |
| dep.logger | CT-logger upload |  | none | main | no | depot site |
| dep.spare | Spare power (connection minus building load) | kW | computed | main | no | depot site |

## Charging

### Chargers and plan

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| chg.mode | Chargers: size them for me / I choose the size |  | none | main | no | depot site |
| chg.power | Charger power per point | kW | none | main | no | depot site |
| chg.points | Number of charge points |  | none; an output in greenfield sizing | main | no | depot site |
| chg.type | Charger type (AC on-board / DC) |  | none | named popup: Charger type and connector | no | depot site |
| chg.connector | Connector |  | none | named popup: Charger type and connector | no | depot site |
| chg.library | Charger from the charger library |  | none | main | no | depot site |
| chg.strategy | Charging plan: Lowest cost / Grid-friendly / Ready earliest |  | none (OPEN) | main | no | depot site |
| chg.ready_by | Ready-by time | hh:mm | none (empty = when the vehicle leaves) | main | no | depot site |
| chg.load_factor | Average charger load while charging (load factor) | % | 0.85, STD (COWI truck cost sheet) | named popup: Charger load and losses | no | depot site |
| chg.losses | Charger losses (efficiency) | % | 3 to 4 %, ASSUMP (4-leaf 2023) | named popup: Charger load and losses | no | depot site |
| chg.soc_start | Start state of charge at arrival (if not taken from the route run) | % | none; OPEN (not specified in sources) | named popup: Charging limits | no | depot site |
| chg.soc_target | Target state of charge (charge to) | % | none; OPEN | named popup: Charging limits | no | depot site |
| chg.step | Time step | min | OPEN: must come from Energinet specs; mock-up shows 5 min ASSUMP | named popup: Charger load and losses | no | depot site |
| chg.assign | Truck-to-point assignment and shared chargers |  | none | named popup: Which truck uses which charger | no | depot site |
| chg.opportunity | Charging between shifts or at the tip site (charger_available per stop) |  | none; OPEN | named popup: Charging away from the depot | no | depot site |
| chg.public_share | Public charging share (and price) | % | none | named popup: Public charging | no | depot site |
| chg.outage | Charger can be out of service (robustness case) |  | none | named popup: What if something fails | no | depot site |
| chg.late | Late return (robustness case) | min | none | named popup: What if something fails | no | depot site |
| chg.discipline | Plug-in discipline (share of vehicles plugged in on return) | % | none | named popup: What if something fails | no | depot site |
| chg.cold_week | Cold week case |  | none | named popup: What if something fails | no | depot site |
| flex.offer | Offer flexibility to the power markets |  | Off | named popup: Flexibility | no | depot site |
| flex.markets | Markets (FCR-D, FCR-N, mFRR, aFRR) |  | none | named popup: Flexibility | no | depot site |
| flex.aggregator | Aggregator yes / no |  | none | named popup: Flexibility | no | depot site |
| flex.dso_pilot | DSO flexibility pilot (Cerius/Radius terms) |  | none | named popup: Flexibility | no | depot site |
| flex.v2g | V2G readiness (ISO 15118-20 on truck and charger) |  | none | named popup: Flexibility | no | depot site |
| flex.hours | Hours per week available for flexibility | h | none | named popup: Flexibility | no | depot site |

## Weather

### Weather and location

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| wx.location | Location (address, place or depot) |  | none | main | no | weather/location |
| wx.station | Weather station |  | Nearest DMI station with a full year, EXT (DMI) | main | no | weather/location |
| wx.year | Weather year (one or several) |  | none (OPEN default year) | main | no | weather/location |
| wx.detail | Level of detail (day / driving hours / hourly) |  | none (OPEN) | named popup: Weather detail | no | weather/location |
| wx.shift | Shift every temperature by | K | 0 | named popup: Weather detail | no | weather/location |
| wx.worst | Run the worst day as its own case |  | Off | main | no | weather/location |
| wx.own_file | Own weather file upload |  | none | named popup: Weather detail | no | weather/location |
| wx.pxx | P50 / P90 across weather years (on / off) |  | On when several years | named popup: Weather detail | yes | weather/location |
| wx.wind | Reference wind (m/s at 10 m) | m/s | 5.028 m/s at 10 m, HDEV decision (replaces VECTO 3 m/s at 4 m) | named popup: Wind | no | weather/location |
| wx.wind_exp | Wind exponent |  | 0.2 (26 Oct list), hidden constant | hidden | no | weather/location |
| wx.yaw | Yaw clamp 10 degrees | degrees | 10, HDEV decision, stated in every report | hidden | no | weather/location |

### Cab heating and cooling

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| hv.mode | Cab heating and cooling: one fixed power / worked out from the weather |  | none | main | yes | weather/location |
| hv.const_w | Heating and cooling power (VECTO table or own) | W | VECTO table value, STD | main | yes | weather/location |
| hv.persons | People in the cab |  | none | main | yes | weather/location |
| hv.heater | Heater (heat pump, electric heater, fuel heater) |  | none | main | yes | weather/location |
| hv.cop | COP and share tables by ambient temperature |  | VECTO tables, STD | named popup: Heater tables | yes | weather/location |
| hv.setpoints | Set-points: heat / cool / cool-off | °C | 18 / 23 / 17, STD | named popup: Set-points | yes | weather/location |
| hv.a_surface | Cab surface area | m2 | none (no sourced default) | named popup: Cab data | yes | weather/location |
| hv.u | Heat loss through the cab (U) | W/m2K | none (no sourced default) | named popup: Cab data | yes | weather/location |
| hv.a_window | Window area | m2 | none (no sourced default) | named popup: Cab data | yes | weather/location |
| hv.volume | Cab volume | m3 | none (no sourced default) | named popup: Cab data | yes | weather/location |
| hv.p_max | Largest heating and cooling power | W | none | named popup: Cab data | yes | weather/location |
| hv.vent | Ventilation and ventilation while heating | m3/h | none | named popup: Cab data | yes | weather/location |
| hv.constants | Climate constants (heater efficiency 0.93, ventilation power 0.56 Wh/m3, heat per person 50/80 W, clouding 0.65/0.8, boundary 17 °C, g 0.95, solar factor 0.25, waste heat 0, fresh air 100 m3/h for 2 persons, cp 1005) |  | STD (VECTO); fresh air Dvorak preprint; cp NO SOURCE read yet | engineering view | yes | weather/location |
| hv.door | Door openings and cold-cab warm-up |  | none | engineering view | yes | weather/location |

## Prices

### Electricity

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| pr.area | Price area (DK1 / DK2) |  | Auto from site address | main | no | market (prices, taxes) |
| pr.spot | Electricity spot price (hourly) | DKK/kWh | Energinet energidataservice, EXT | main | no | market (prices, taxes) |
| pr.own_hourly | Your own hourly prices | DKK/kWh | none | main | no | market (prices, taxes) |
| pr.level | Price level (low / expected / high) |  | Expected (OPEN: how levels are defined) | main | no | market (prices, taxes) |
| pr.tariff | Grid tariff and taxes (time of day) | DKK/kWh | none (OPEN: source per grid company) | main | no | market (prices, taxes) |
| pr.tax_refund | Electricity tax and refund | DKK/kWh | none | named popup: Electricity tax and refund | no | market (prices, taxes) |
| pr.capacity_charge | Capacity charge (average of the 10 busiest hours, A-høj, A-lav, B-høj) | DKK/kW month | none | named popup: Capacity charge | no | market (prices, taxes) |
| pr.paths | Price paths over the ownership period (Energistyrelsen Klimastatus) |  | none | named popup: Price paths | no | market (prices, taxes) |
| pr.diesel | Diesel price | DKK/l | 11.65, OK.dk Jan-Jun 2024 plus 0.50 for the duty rise (COWI base case uses 11.15) | main | no | market (prices, taxes) |
| pr.adblue | AdBlue price | DKK/l | 6.96, source to confirm | named popup: Other fuels and public charging | no | market (prices, taxes) |
| pr.hvo | HVO100 price | DKK/l | 19.97, source to confirm | named popup: Other fuels and public charging | no | market (prices, taxes) |
| pr.biogas | Biogas price |  | none | named popup: Other fuels and public charging | no | market (prices, taxes) |
| pr.public | Public fast-charging price | DKK/kWh | 3.25, FDM 2024 | named popup: Other fuels and public charging | no | market (prices, taxes) |

## Costs

### Ownership and finance

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| fin.years | Ownership period (8 / 10 / 12 years) | years | none (OPEN) | main | no | company (finance) |
| fin.financing | Financing (loan / lease / cash) |  | none | main | no | company (finance) |
| fin.interest | Interest rate | % | 3.45, NO SOURCE (COWI sample) | main | no | company (finance) |
| fin.down | Down payment | DKK | none | main | no | company (finance) |
| fin.discount | Discount rate and NPV rule (Vejdirektoratet: year 1 discounted one period) | % | none | main | no | company (finance) |

### Vehicle costs

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| fin.residual | Residual value (% of price per year, table or SoH-linked) | % | 15 % for years 1-6, NO SOURCE (COWI sample) | named popup: Residual value | no | company (finance) |
| fin.price_ev | Electric truck price | DKK | 2,050,000, NO SOURCE (COWI sample) | main | no | company (finance) |
| fin.price_d | Diesel truck price | DKK | 1,150,000, NO SOURCE (COWI sample) | main | no | company (finance) |
| fin.service | Service, electric vs diesel | DKK/month | 7,685 vs 5,000, NO SOURCE (COWI sample) | main | no | company (finance) |
| fin.insurance | Insurance, electric vs diesel | DKK/month | 1,476 vs 768, NO SOURCE (COWI sample) | main | no | company (finance) |
| fin.tyres | Tyres, electric vs diesel | DKK/km | none | named popup: Running costs | no | company (finance) |

### Operations costs

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| fin.wage | Driver wage | DKK/month | 30,000, NO SOURCE (COWI sample) | main | no | company (finance) |
| fin.lost_time | Lost production time (charging dwell, downtime) | h, DKK/h | none | named popup: Downtime and lost time | no | company (finance) |
| fin.downtime | Downtime cost (e.g. tender fines DKK 2,000 per truck per day) | DKK/day | none | named popup: Downtime and lost time | yes | company (finance) |
| fin.payload_cost | Payload opportunity cost | DKK/t | none | named popup: Downtime and lost time | no | company (finance) |

### Depot costs

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| fin.charger_price | Charger hardware and trenching (charger class or own) | DKK | COWI bands 22 kW 12,500 + 10,000 ... 400 kW 700,000 + 500,000 (2024 operator prices, operator not named; verify) | named popup: Charger price list | no | company (finance) |
| fin.conn_fee | Grid connection fee (computed from grid company and amps, or entered) | DKK | Radius 17,950 + 1,280 per extra A (may be stale); Cerius 2026 23,500 first 25 A then per A by category | named popup: Connection fees | no | company (finance) |
| fin.depot_years | Depot amortisation period | years | OPEN (about 30 years proposed vs 10 for vehicles) | main | no | company (finance) |

### Sensitivity

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| fin.sensitivity | Sensitivity ranges | % | none | named popup: Sensitivity ranges | no | company (finance) |
| fin.monte | Monte Carlo quartiles |  | none | named popup: Sensitivity ranges | no | company (finance) |

### Alternatives

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| fin.diesel_alt | Compare against HVO100 / biogas / B7 |  | none | named popup: Compare with other fuels | no | company (finance) |

## Taxes, grants and CO₂

### Taxes and subsidies

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| tax.km_class | Km-tax inputs: weight class, CO2 class, zone |  | Auto from vehicle group and route | main | no | market (prices, taxes) |
| tax.km_rate | Road tax rate (km-toll) by year | DKK/km | EV 0.1008 vs diesel 0.8525 for 2025-27; steps up in 2028 and 2029 (weight class to confirm) | main | no | market (prices, taxes) |
| tax.ets2 | Diesel under ETS2 from 2028 |  | none | named popup: Taxes on diesel | no | market (prices, taxes) |
| tax.subsidy | Subsidy scheme (none / Vejdirektoratet / German BMV / own amount) |  | none; VD pool closed 30 Sep 2026 | main | no | market (prices, taxes) |
| tax.grant | Grant or subsidy, paid once | DKK | none (demo 0) | main | no | market (prices, taxes) |

### CO2

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| co2.grid | CO2 from grid electricity (Energistyrelsen path / own value) | g/kWh | Energistyrelsen series 41.5 falling to 7.0 over 2024-2034, EXT (demo used 19.35) | main | no | market (prices, taxes) |
| co2.hours | CO2 at actual charging hours (Energi Data Service CO2Emis) |  | Off, planned | main | no | market (prices, taxes) |
| co2.diesel | Diesel CO2 factor | kg/l | 2.65, NO SOURCE (sample) | named popup: Fuel CO2 factors | no | market (prices, taxes) |
| co2.wtw | Well-to-wheel and life cycle (vehicle and battery production) |  | none | named popup: Life-cycle CO2 | no | market (prices, taxes) |
| co2.alt | Alternative fuels (HVO, biogas, B7) |  | none | named popup: Fuel CO2 factors | no | market (prices, taxes) |

## Tender (shown only for tender projects)

### Tender

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| ten.weights | Award weights (price / technical / delivery / ESG) | % | none (tenders found: price 40-70 %, technical 25-35 %, delivery 15-25 %, ESG 10 %, project note 26 Oct) | main | yes | tender |
| ten.curves | Score curves (battery 250 to 450 kWh gives 1 to 10 points; charging power 150 to 350 kW; load 5.8 to 9.5 t) |  | none | main | yes | tender |
| ten.min_usable_y8 | Minimum usable kWh at year 8 (buyer requirement) | kWh | none | main | yes | tender |
| ten.min_charge | Minimum charging power window (e.g. at least 150 kW between 10 % and 75 %) | kW | none | main | yes | tender |
| ten.min_ready | Ready at 80 % by 06:00 (buyer requirement) | hh:mm, % | none | main | yes | tender |
| ten.min_pto | Crane and compactor at the same time (requirement) |  | none | main | yes | tender |
| ten.bids | Several OEM bids (spec values per bid: battery kWh, usable at year 8, charging kW, load t, price) |  | none | main | yes | tender |
| ten.guarantees | Guarantee values (year-8 capacity, downtime up to 5 days per year, response within 2 h) |  | none | main | yes | tender |
| ten.brand_flag | Brand-neutral flag |  | none | main | yes | tender |

## Compare

### Scenarios

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| scn.levers | Scenario levers (fleet size, charging strategy, price level, weather year, ownership years) |  | none | main | no | scenario |
| scn.changes | List of changes (any field) |  | none | main | no | scenario |

## Check and run

### Run check

| id | Label | Unit | Default and tag | Tier / popup | Year 8 | Depends on |
|---|---|---|---|---|---|---|
| proj.fingerprint | Run fingerprint (engine version, input hash, every default with source) |  | n/a | hidden | no | project |
| hid.vecto_payload | VECTO reference payload table by group and mission |  | STD | hidden | no | load |
| hid.vecto_body | Body and trailer masses, reference height, CdxA_Default |  | STD | hidden | no | vehicle |
| hid.vacc | Acceleration curves vacc_v, vacc_acc, vacc_dec; design speed 85 km/h |  | STD (VECTO table) | hidden | no | route |
| hid.driver_consts | Driver-model parameters lac_*, df_*, os_*, brake_margin 0.1, v_min_coast 5 m/s |  | defaults.py | hidden | no | route |
| hid.ref_mass | Reference mass for first driver pass, then exact final pass |  | Pipeline rule | hidden | no | route |
| hid.dt | Driver time step 1 s | s | defaults.py (HDEV deviation: VECTO uses about 0.5 s) | hidden | no | route |
| hid.physics | g 9.81, rho 1.188 (older list) or computed from p_air 101,325 Pa and R_air 287.05, beta 0.9 |  | Constants / computed | hidden | no | weather/location |
| hid.crosswind_grid | Crosswind speed grid 60-130 km/h, h_ref 10 m, dh, dphi_deg |  | defaults.py | hidden | no | vehicle |
| hid.yaw_never_avg | Never average across weather years; worst day kept as own case |  | HDEV decision | hidden | no | weather/location |
| hid.units | Unit conversion (t to kg, km/h to m/s, °C to K, m3/h to m3/s) |  | n/a | hidden | no | vehicle |
| hid.slot_meta | Slot metadata {value, unit, source, date, label, provided_by, locked, version} |  | OPEN | hidden | no | vehicle |
| hid.audit | Model status per result (validated / in testing / not built), decisions stated |  | n/a | hidden | no | scenario |

## Inventory rows that could not be placed

None: 0 of 178. See `inventory_coverage_check.csv` for the row-by-row mapping. The matching is by name pattern written by Kiro ([JUDGEMENT]); it proves every row has a home, not that the home is the best one.

Inventory sections 15 and the "Open decisions" list are not table rows. Each open decision is a register row with status `open`: payload basis (`pl.basis`), mixer PTO default (`pto.stop_kwh` note), half-second PTO profile (`pto.profile`), PTO drag (`pto.drag`), mechanical PTO (`pto.own_motor`), drivetrain rule (`veh.eff_method`), altitude pressure (`rt.altitude`), Kt and wet road factor (`veh.kt`, `veh.wet`), charging time step (`chg.step`), Cond while coasting (`aux.cond`), slot shape (`hid.slot_meta`), weather defaults (`wx.year`, `wx.detail`), price levels (`pr.level`), depot amortisation (`fin.depot_years`), GPS picks weather station (`rt.gps_file` note).

## Inputs found in other tools that HDEV has no row for (candidates only)

| Candidate | Where seen | Source and date read | Why it might matter |
|---|---|---|---|
| Local generation (PV) time series and fixed load time series | SpiceEV `generate.cfg` options include_local_generation_csv, include_fixed_load_csv | https://github.com/mohgsaad-art/spice_ev (examples/configs/generate.cfg, read 14 Nov 2026) | Depot with rooftop PV; HDEV has building load but no on-site generation row |
| Minimum state of charge when leaving (default 0.8) | SpiceEV `min_soc` | same file | HDEV has ready-by and target SOC (bat.soc_target) but no "minimum at departure" distinct from target |
| Minimum power at a charge point (share of installed power) | SpiceEV `cs_power_min` | same file | Planned charging engine may need it |
| Voltage level of the grid connection (HV, HV/MV, MV, MV/LV, LV) for price sheets | SpiceEV `voltage_level`; eFLIPS-depot `cost_params.json` gc LV / MV with default distance | https://github.com/mohgsaad-art/eflips-depot (tests/ebustoolbox/static/ebustoolbox/examples/cost_params.json, read 14 Nov 2026) | HDEV has customer category (C, B-lav ...) which is the Danish equivalent; distance to the grid point is not asked |
| Distance to the grid connection point (cable length) | eFLIPS-depot cost params `default_distance` | same file | Connection cost in Denmark may depend on it; sources not checked |
| Stationary (buffer) battery: capacity and C-rate | SpiceEV `battery = [[capacity, C-rate]]` | generate.cfg | Covered by dep.buffer (planned) |
| Vehicle lifetime and maintenance cost per km | eFLIPS-depot cost params `lifetime`, `c_maint_per_km` | cost_params.json | HDEV has service per month; per-km variant not in register |
| Battery lifetime in years and battery cost per kWh | eFLIPS-depot `lifetime_battery`, `cost_per_kWh` | cost_params.json | Needed for battery replacement cost; HDEV has age.replace_year with cost, but no cost per kWh row |
| V2G discharge limit and V2G power factor | SpiceEV vehicle_types `discharge_limit`, `v2g_power_factor` | https://github.com/mohgsaad-art/spice_ev examples/data/vehicle_types.json | Only needed if V2G is modelled; flex.v2g is a yes/no today |
| Charging curve per vehicle (power against SOC) | SpiceEV / eFLIPS vehicle_types `charging_curve` | same files | HDEV has max C-rate by SOC (bat.c_rate) which is the same idea in a different shape |
| Glider mass, drive-axle weight share, wheel base, centre of gravity height, component mass multiplier | FASTSim vehicle yaml (e.g. 2016 CHEVROLET Spark EV): glider_kg, drive_axle_weight_frac, wheel_base_m, veh_cg_m, comp_mass_multiplier | https://github.com/mohgsaad-art/fastsim (cal_and_val/f2-vehicles, read 14 Nov 2026) | Glider mass is siz.glider_mass; axle load share is not in HDEV (VECTO has relative axle load per axle) |
| Battery mass per kWh, motor mass per kW, battery maximum power | FASTSim `ess_kg_per_kwh`, `mc_pe_kg_per_kw`, `ess_max_kw` | same yaml | siz.pack_density covers the first; motor mass and battery max power are not in the register |
| Technically permissible maximum laden mass (TPMLM), axle configuration and vehicle category (these decide the HDV group) | VECTO vehicle editor, General tab | VECTO user manual F_VEH-Editor.md, branch IEPC-experiments (read first ~7.5k characters, 14 Nov 2026) | HDEV asks the group directly (veh.group). A user who does not know the group needs these three to find it |
| Axle table: relative axle load, RRC per axle, FzISO, wheel inertia per axle | VECTO vehicle editor, Axles/Wheels | same manual | HDEV uses one Crr and m_red_wheels; a VECTO audit would need the axle table. Engineering view candidate |
| Retarder losses, angledrive, axle gear ratio and losses | VECTO vehicle editor, Powertrain tab | same manual | Drivetrain popup candidates; relevant when loss maps are used |
| Battery testing temperature, SoC min / SoC max, max current map | VECTO REESS editor (M_BatteryPackEditor.md) | VECTO user manual, read in full | bat.soc_window and bat.c_rate cover most; testing temperature is OEM-only |
| Air density (global setting) | VECTO Settings (manual F_VEH-Editor mentions Air Density under Settings) | same manual | HDEV computes it from p_air and R_air; no user input |
| Auxiliary demand varying along the route (Padd column in the cycle) | VECTO job editor, Engineering mode auxiliaries | VECTO manual D1_VECTO-Job-Editor.md (read first ~5k characters) | HDEV has aux per row from P_aux; time-varying user aux not in register |
| Inflation rate, tax rate, insurance rate, property rate, salvage value | SAM Financial Parameters (Loan Type, Analysis Parameters, Tax and Insurance Rates, Property Rates, Salvage Value) | https://courses.ems.psu.edu/eme810/node/594 (search snippet only; page not opened) | Candidates for the cost page: inflation and salvage value are not in the register (residual value covers salvage) |
| Project lifetime and sensitivity variables with several values per input | HOMER Pro sensitivity variable; Project tab | https://homerenergy.com/products/pro/docs/latest/navigating_homer.html (read in full); sensitivity variable page snippet only | Equivalent of scenario levers; HDEV has the five levers only |
| AC mains: voltage, number of phases, phase displacement, feed-in control | PV*SOL System type, climate and grid page | https://help.valentin-software.com/pvsol/en/pages/system-type-climate-and-grid/ (read in full 14 Nov 2026) | HDEV works in amperes at 400 V in the demo (`amps = kW x 1000 / (sqrt3 x 400)`); voltage and phases are not inputs |
| Simulation time step (1 hour or 1 minute) | PV*SOL, same page | same page | chg.step (OPEN) |
| Charging locations (zones where the vehicle dwells) and preferences | Geotab EVSA four sections: Vehicles to Assess, EV Models, Charging Locations, Preferences | https://support.geotab.com/en-GB/mygeotab/mygeotab-add-ins/doc/evsa-add-in (first ~4k characters read) | HDEV has one depot; multiple charging locations for opportunity charging are open (chg.opportunity) |
| Consumption profile of building (load profile library) | PV*SOL navigation page Consumption | https://help.valentin-software.com/pvsol/en/pages/ (read in full) | dep.base_mode covers fixed, Eloverblik, logger; a profile library (office, warehouse) is not in the register |

## Conflicts between project documents (and the demo)

| Topic | What the documents say | Problem |
|---|---|---|
| Dwell time per stop | Inventory §2: default 45 min per stop (ASSUMP). Demo sample: 20 s per stop for refuse. Inventory also says dt-cargo median stop is 22 min. | Unit and meaning differ (minutes between stops vs seconds of work at a stop). Needs a decision: separate "time at stop (work)" from "dwell (parked)". |
| Usable share of battery | Inventory §4e: about 0.855 x installed (verify). Demo: 90 % sample value. | Different numbers; neither verified. |
| Year-8 guarantee value | Demo sample: 70 % (Rambøll 2023 "warranties often down to 70 %"). Prompt: Ressourceindsamling at least 80 % at 8 years. Doc findings §6: ARC 2022 max 25 % loss in 8 years (= 75 %). | Three values in use. No default should be shown as fact; the field must be required. |
| Grid CO₂ path | Inventory §12: 41.5 falling to 7.0 g/kWh over 2024-2034. Demo: 19.35 g/kWh in 2026 falling to 8.26 in 2034 (includes upstream). | Different series or different scope; Energistyrelsen series itself not opened. |
| Air density | Demo engine: 1.2. 26 Oct list: 1.188. Engine: computed from p_air 101,325 and R_air 287.05. | Hidden value, but the report must state one. |
| Diesel price tag | Inventory: 11.65 = OK.dk Jan-Jun 2024 plus 0.50 for the duty rise (COWI uses 11.15). Demo tags it "Standard". | An estimate shown as a standard; should be ASSUMP. |
| Always-on PTO asked twice | Inventory §5a (page 5, on-board systems) and §6 (page 6, PTO). | One input must live in one place: proposal puts it on the PTO template and fills P_aux from it. |
| Departure time asked twice | Inventory §1 shift start and §2 "Departure time at depot". | Same value; proposal asks once on the schedule. |
| Diesel use and vehicle prices | Inventory pages 10 and 11 (Prices, Costs). Demo: diesel use is in the vehicle template; vehicle prices, service and insurance are stored in the vehicle template but shown on the Costs page. | Proposal: diesel use stays with the vehicle (it describes the old truck); prices stay on Costs. Only diesel use differs from the inventory. |
| Weather location | Inventory §7: its own input. Demo: weather page has no location field; says "Nearest to the depot". | Proposal: one site address, reused, with a visible override. |
| v_no_regen | Inventory §4d: none (user field). 26 Oct list: hidden constant 5 km/h. | Hidden or OEM-only? |
| Road tax years | Inventory §12: EV 0.1008 vs diesel 0.8525 for 2025-27. Demo labels "2026 to 2027". | Year range differs. |
| Km-toll weight class | Inventory §12 "weight class to confirm"; outputs note: extends to trucks of 3.5 t and above from 1 Jan 2027. | Weight class scope to confirm. |
| Heater type supplied by | Inventory §5b: OEM. 26 Oct list: client or OEM. | Who |
| HVAC factor | P_aux default 1.25; must be 1.0 in thermal mode (26 Oct list "things to check"; inventory §5a). | Documented; parser job. |
| Charging step size | Inventory §8: OPEN, mock-up shows 5 min as ASSUMP. Demo tags it Assumption. | Consistent; still unsourced. |

## Engine arguments mapped to inputs

See `engine_args_map.csv` (every function in Appendix A.1 and A.2 of the prompt, with the register ids that fill it).
