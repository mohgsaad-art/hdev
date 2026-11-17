# HDEV UI input inventory

2026-11-13 · Bob

## How to read this

This lists every input found in the project docs and the UI mock-up chats, grouped into 14 UI pages. It merges the 26 Oct input list with the 12–13 Nov engine decisions (rotor inertia, PTO routing, HVAC in kelvin, defaults only in `defaults.py`). Nothing here is a new decision: where a default or method is not settled it is tagged OPEN, and where no source exists it is tagged NO SOURCE.

**Source tags used in the Default column**

| Tag | Meaning |
|---|---|
| STD | Value from a named standard (VECTO / Reg. 2017/2400 annexes), looked up by the resolver |
| LIB | Filled from the data library (EEA RP 2024–25 tables) when a library vehicle is picked |
| EXT | Fetched from an external source (DMI, Energinet, Energistyrelsen, Eloverblik) |
| ASSUMP | An assumption or simplification; must be shown as such in the UI |
| NO SOURCE | A sample or placeholder value with no verified source; must not be shown as fact |
| OPEN | Decision not made yet |
| none | No default; user must enter (blocks Run if missing) |

**Input methods:** dropdown, number field, toggle (yes/no), table (editable rows), file upload (VDRI, GPS, CSV, spreadsheet), profile picker (saved profile or library), text/AI ("describe it", planned), and a connect action (Eloverblik/MitID).

**UI rules that apply everywhere (from the mock-up and registry chats)**

- Each page has a main part and a "More settings" fold-out for rarely changed fields.
- Every value carries a source tag; an edited value turns blue and shows a reset-to-default button.
- A missing required field is red and blocks Run.
- An engineering-view toggle shows physics names (Crr, CdxA, theta_red…); client view hides them.
- Each field is open, collapsed or hidden in the registry; hidden fields are never shown (page 14).
- Who supplies: Client, OEM, or Standard (the tool). OEM-only fields are greyed for clients.
- The UI shows tonnes, km, kWh, °C; the engine receives SI. Conversion happens in the parser only.
- Rules that change by source: Route page (section 2) and Vehicle page (section 4) lock or unlock fields depending on how the data was entered.

## 1. Project and Operation

One project JSON holds vehicles, routes, assignments and calendar; a scenario is the base plus changes. These fields set up the fleet and when it runs.

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Project name, scenario name | Text | none | Yes | Client | Project JSON |
| Fleet size (trucks) | Number | none | Yes; also a scenario lever | Client | Depot sizing, TCO |
| Shift start / end (hh:mm) | Time fields | none | Yes | Client | Calendar, charging window |
| Working days (Mon–Sun) | Day toggles | none | Yes | Client | Calendar |
| Holidays | Date list or country calendar | none (OPEN: which calendar source) | Yes | Client | Calendar |
| Calendar pattern: route, days, departure/return, exceptions | Table | none | Yes | Client | Runner, charging |
| Per-truck assignment: route, PTO profile, payload profile | Dropdowns per truck + "apply to all" | none | Yes | Client | Runner |
| Saved libraries: routes, PTO profiles, payload profiles | Profile picker + save | empty | Yes | Client | Assignment |
| Run mode: sizing (P = E/t) or simulation (per timestep) | Toggle | OPEN (no default decided) | Yes | Client | Charging stage |
| Brand-agnostic flag (tender comparison) | Toggle | none | Yes | Client / OEM | Offer sheet |

The run fingerprint (audit block with inputs, versions, sources) is produced by the tool, not entered.

## 2. Route and stops

A route is built from one of four sources, then turned into waypoints (distance, speed, grade, stop flag) for the driver model. A VDRI file is never altered: if the user edits it, it is saved as a "user route".

**Step 1: pick the source**

| Source | Input | What the user gives | Status |
|---|---|---|---|
| VDRI template | Dropdown of VECTO mission cycles (LongHaul, RegionalDelivery, UrbanDelivery, MunicipalUtility, Construction) | Mission only; cycle comes from VECTO | Input source |
| Typed | Table | Distance per leg, number of stops, dwell time | Input source |
| GPS upload | File upload | Track file | Input source |
| AI "describe it" | Text box | Free text turned into a typed route | Planned (adapter not built) |

**Step 2: what is editable in the stop table, by source**

| Source | Distances / road type | Stop time | Payload per stop | Everything else |
|---|---|---|---|---|
| VDRI | Locked | Editable | Editable | Locked |
| Typed | Editable | Editable | Editable | Editable |
| GPS | Locked | Locked | Editable | Locked |

**Typed-route fields and defaults**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Leg distance (km) | Number per leg | none | Yes | Client | Waypoints |
| Road type per leg: deep urban / urban / non-urban | Dropdown | none | Yes | Client | Waypoints |
| Speed per road type (km/h) | Number | 30 / 50 / 80 · ASSUMP | Yes (More settings) | Client | `driver_model` (`wp_v`) |
| Grade (%) | Number per leg | 0 (flat) · ASSUMP | Yes | Client | `driver_model` (`wp_grade`) |
| Number of stops | Number | none | Yes | Client | Waypoints, PTO |
| Dwell time per stop (min) | Number | 45 · ASSUMP (dt-cargo median stop is 22 min, so this needs a source) | Yes | Client | Waypoints, charging gaps |
| Departure time at depot | Time | none | Yes | Client | Weather start, charging |
| Route name, save to library | Text + button | none | Yes | Client | Library |

**GPS upload:** only payload is editable (table above). OPEN: whether the track's coordinates should also pick the weather station; today weather location is its own input (page 7).

Not user inputs: the VECTO acceleration curves (`vacc_*`) and design speed 85 km/h come from the VECTO table via the resolver (page 14).

## 3. Payload

Payload is shown in tonnes in the UI and passed as kg to the engine. The payload resolver turns the choices below into a payload per waypoint (`payload_wp`).

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Payload basis | Dropdown: VECTO reference payload / max payload / reference plus a max-payload run / custom | OPEN (not decided) | Yes | Client | Payload resolver |
| Payload shape | Dropdown: constant / linear (loaded to empty over the route) / custom | none | Yes | Client | Payload resolver |
| Payload value (t) | Number (constant, or start and end for linear) | VECTO reference payload by vehicle group and mission · STD (e.g. group 5 long haul: 19,300 kg reference, 2,600 kg low) | Yes | Client | `payload_wp` |
| Payload per stop (t) | Stop-table column (load / unload at each stop) | none | Yes, for all route sources | Client | `payload_wp` |
| Saved payload profile | Profile picker + save | empty | Yes | Client | Library |

The VECTO payload table is looked up by the resolver from the vehicle group and mission (page 14); the user only sees the resulting value and its STD tag. Whether the payload is limited by the vehicle's own max payload (from page 4) is part of the open basis decision.

## 4. Vehicle

Two ways in: pick a vehicle from the data library (EEA RP 2024–25 tables, one row per exact configuration) or enter it manually. A library pick fills the fields it knows; every other field is filled from VECTO standard values and tagged STD. OEM-only fields stay empty for clients.

**4a. Identity, body and mass**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Vehicle source | Toggle: library pick / manual | none | Yes | Client / OEM | Resolver |
| Library vehicle | Searchable dropdown | none | Yes (picked fields become editable copies) | Client | Resolver |
| VECTO vehicle group (1–16) | Dropdown | none | Yes | Client | Resolver lookups |
| Vehicle (curb) mass (kg or t) | Number | LIB if picked, else none | Yes | Client / OEM | `consumption_engine` (`m_vehicle`) |
| Body type | Dropdown (VECTO body list, e.g. B1) | none | Yes | Client | Body mass lookup |
| Body mass (kg) | Number | VECTO standard by body type · STD (e.g. B1 1,600 kg) | Yes | Client | `m_vehicle` |
| Trailer type / mass (kg) | Dropdown + number | VECTO standard by type · STD (e.g. ST1 7,500 kg) | Yes | Client | `m_vehicle` |
| Max payload / gross vehicle weight (t) | Number | LIB if picked, else none | Yes | Client / OEM | Payload page |
| Mass of rotating wheels, `m_red_wheels` (kg) | Number | none (OPEN: source) | Yes (engineering view) | Client | `driver_model`, `force_engine` |

**4b. Aerodynamics**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| CdxA (m²) | Number | VECTO CdxA_Default by group · STD (e.g. group 4: 8.4, group 5: 8.7, group 9: 8.5, group 16: 9.0) | Yes | Client / OEM | `driver_model`, `consumption_engine` |
| CdxA vs yaw or speed table | Table / file upload (OEM air-drag data) | none; OPEN: exact upload format | Yes | OEM | `crosswind_engine` |
| Vehicle height (m) | Number | VECTO reference height by group · STD (groups 1/1s 3.6, group 2 3.75, group 3 3.9, groups 4/5/7–12 4.0, group 6 3.75, groups 13–16 3.6) | Yes | Client | `crosswind_engine` |

**4c. Tyres and wheels**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Rolling resistance coefficient, Crr (–) | Number | none (OPEN: whether the resolver supplies a VECTO standard value) | Yes | Client / OEM | `force_engine` |
| Dynamic tyre radius r_dyn (m) | Number | none | Yes | Client / OEM | `force_engine` |
| Tyre load index | Dropdown / number | none | Yes | Client | Cold-tyre factor (not built) |
| Cold-tyre factor Kt | Number | 0.006 if load index > 121, else 0.010 · planned item, OPEN | Yes (More settings) | Standard | Crr correction (not built) |
| Wet / ice road factor | Dropdown | OPEN (not built) | Yes | Client | Crr correction (not built) |
| Inertia reduction `theta_red` (–) | Number | none (OPEN: source) | Yes (engineering view) | Client / OEM | `force_engine` |

**4d. Drivetrain and motor**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Motor / e-axle / iePC | Library dropdown or manual | LIB if picked | Yes | Client / OEM | Efficiency lookup, `P_max` |
| Max motor power `P_max` (kW) | Number | LIB if picked, else none | Yes | Client / OEM | `driver_model` |
| Gearbox: single speed or gear table with ratios | Dropdown + table | none | Yes | OEM | `i_total` per row |
| Total ratio `i_total` per row (–) | Computed from gear and final drive | none | Via the gear table | OEM | `force_engine` |
| Rotor inertia `J_rotor` (kg·m²) | Number | NO SOURCE (no fleet default) | Yes | OEM | `force_engine` |
| Efficiency method | Toggle: loss maps / separate drive and regen efficiencies | OPEN (calibrate to EEA vs V-C bus method) | Yes | Client | `consumption_engine` |
| Loss maps (motor, inverter, gearbox) | Table / file upload | VECTO generic E2 standard values · STD | Yes | OEM | Loss lookup function (planned) |
| Drive / regen efficiency numbers | Numbers (motor, inverter, gearbox) | 0.95 / 0.95 / 0.98 · NO SOURCE (placeholders in code) | Yes | Client / OEM | `consumption_engine` |
| Regeneration: no-regen speed (km/h), max regen power (kW), regen efficiency (–) | Numbers | none | Yes | OEM | `consumption_engine` (`v_no_regen`, `P_regen_max`, `regen_effeiciency`) |

If the gear is unknown in a row, the engine uses the lowest gear (highest ratio).

**4e. Battery** (the battery model with OCV + Ri is not built yet)

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Battery mode | Toggle: A real vehicle (datasheet) / B size it | none | Yes | Client | Battery stage |
| Installed energy (kWh) | Number | LIB if picked | Yes | Client / OEM | Battery stage |
| Battery mass (kg) | Number | LIB if picked (mode A); computed in mode B | Yes | OEM | `m_vehicle` |
| VECTO-usable energy (kWh) | Number | about 0.855 × installed · approximate, verify the factor | Yes | Standard | Battery stage |
| OEM-usable energy (kWh) | Number | none | Yes | OEM only | Battery stage |
| Cell chemistry | Dropdown | none | Yes | OEM only | Ageing (planned) |
| Warranty / SoH curve | Table | none | Yes | OEM only | Ageing (planned) |
| OCV points (× V_nom at 0/10/50/90/100 % SOC) | Table | 0.88 / 0.94 / 1.00 / 1.06 / 1.12 · STD (Annex Xb App. 10) | Yes | OEM | Battery stage |
| Internal resistance Ri (mΩ·Ah at 2/10/20/120 s) | Table | 210 / 240 / 270 / 390 · STD (Annex Xb App. 10, HEBS) | Yes | OEM | Battery stage |
| Max charge rate (C) | Table | 0.9 C up to 80 % SOC, 0 at 100 % · STD (Annex Xb App. 10) | Yes | OEM | Battery stage, charging |
| Max DC charging power (kW), connector | Number + dropdown | none | Yes | OEM only | Charging (page 8) |

## 5. On-board systems

All feed `P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on, … efficiencies)`, then `consumption_engine`. The ES and SP factor of 0.7 must be labelled in the UI.

**5a. Auxiliary loads**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Electric system ES (W) | Number | VECTO standard by group · STD (value not listed in this inventory) | Yes | Client / OEM | `P_aux` |
| Power steering PS (W) | Number | VECTO standard · STD | Yes | Client / OEM | `P_aux` |
| Pneumatic system SP (W) | Number | VECTO standard · STD | Yes | Client / OEM | `P_aux` |
| Condensing / other cond (W) | Number | VECTO standard · STD; open question whether it runs while coasting | Yes | Client / OEM | `P_aux` |
| Factors per load (ES, PS, HVAC, SP, cond) | Numbers (More settings) | ES 0.7, PS 1.0, HVAC 1.25 (1.0 in thermal mode), SP 0.7, cond 1.0 · STD | Yes (engineering view) | Standard | `P_aux` |
| Always-on PTO power (W) | Number | none; divided by PTO efficiency | Yes | Client | `P_aux` |
| No auxiliary power during depot charging | Fixed rule | On · design decision | No | Standard | Charging |

**5b. HVAC: choose one mode**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| HVAC mode | Toggle: constant / thermal | none | Yes | Client | `consumption_engine` |
| Constant: VECTO HVAC table (dropdown) or custom power (W) | Dropdown / number | VECTO table value · STD | Yes | Client | `P_aux` (`HVAC_power`) |
| Thermal: number of persons | Number | none | Yes | Client | `HVAC_thermal` (`N_persons`) |
| Thermal: heater type (heat-pump type for the HD case; electric heater yes/no; fuel heater yes/no) | Dropdown + toggles | none | Yes | OEM | `climate_lookup` |
| Thermal: COP and share tables by ambient temperature | Table | VECTO tables · STD | Yes | OEM | `climate_lookup` |
| Set-points: heat / cool / cool-off (°C) | Numbers | 18 / 23 / 17 · STD | Yes (e.g. 22 °C heating) | Client | `HVAC_thermal` (`T_heat`, `T_cool`, `T_cool_off`) |

**5c. Thermal HVAC cab data** (required in thermal mode; no sourced truck default exists for any of them)

| Field (unit) | Input | Default |
|---|---|---|
| Cab surface area `A_surface` (m²) | Number | none |
| Heat transfer coefficient `U` (W/m²K) | Number | none |
| Window area `A_window` (m²) | Number | none |
| Cab volume (m³) | Number | none |
| Max heating power / max cooling power (W) | Numbers | none |
| Ventilation rate and heating ventilation rate (m³/h in UI) | Numbers | none |

Required and missing in thermal mode: red field, Run blocked.

**5d. Thermal HVAC constants** (defaults live in `defaults.py`; shown under More settings, overwritable in engineering view)

| Constant | Default · source |
|---|---|
| Electric heater efficiency | 0.93 · STD (VECTO) |
| Specific ventilation power | 0.56 Wh/m³ · STD (VECTO) |
| Heat per person (W): (50, 80) · STD (VECTO) |  |
| Clouding factors | (0.65, 0.8) · STD (VECTO) |
| Boundary temperature | 17 °C · STD (VECTO) |
| Solar transmission g / solar factor | 0.95 / 0.25 · STD (VECTO) |
| Waste heat | 0 · STD (VECTO) |
| Fresh-air flow Q | 100 m³/h for 2 persons · Dvorak preprint |
| Pressure 101,325 Pa; gas constant 287.05 | Physical constants |
| Specific heat of air cp 1,005 | NO SOURCE read yet |

The parser converts °C to K, Q to m³/s, ventilation rates to 1/s and specific ventilation power to J/m³.

## 6. PTO (power take-off for bodies: refuse, mixer, crane, tipper…)

A PTO has a stop part, a drive part, or both. Each part is a constant power or a (time, power) profile with its own efficiency. One sweeping power per route. Feeds `pto_engine(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff)`.

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| PTO on this route | Toggle, and per stop in the stop table (`is_on`) | Off | Yes | Client | `pto_engine` |
| Stop PTO: constant power (kW) or profile (t in s, W) | Number or table / upload | VECTO refuse profile (23 s, 0.14993 kWh per stop) is the only official default · STD; mixer default OPEN (Ban vs Bae) | Yes | Client | `stop_pto_t`, `stop_pto_w` |
| Drive PTO: constant power (kW) or profile | Number or table / upload | none | Yes | Client | `drive_pto_t`, `drive_pto_w` |
| Stop PTO efficiency / drive PTO efficiency (–) | Numbers | 1.0 · ASSUMP | Yes | Client / OEM | `stop_pto_eff`, `drive_pto_eff` |
| Does the body have its own electric motor? | Yes / no toggle | none | Yes | Client / OEM | Routing of drive PTO: no = mechanical (step 5 in `consumption_engine`), yes = electric (step 6) |
| Electric PTO motor efficiency | Number | NO SOURCE | Yes | OEM | Step 6 |
| Use stop time as PTO time | Toggle | Off · non-VECTO option, must be labelled | Yes | Client | `pto_engine` |
| Saved PTO profile | Profile picker + save | empty | Yes | Client | Library |
| Always-on PTO (W) | On page 5 | none | Yes | Client | `P_aux` |

Open items for this page: profile resolution (half-second profiles), PTO transmission drag (parked), the mechanical-PTO question, and a planned refrigeration unit input.

## 7. Weather

Weather feeds the ambient temperature and wind per row (`T_amb_h`, `W1`, `W2`) and the crosswind engine, which runs once per vehicle. Years are never averaged; the worst day is kept as its own case.

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Location (address, place or depot) | Text / map pick | none | Yes | Client | Station lookup |
| Weather station | Auto: nearest DMI station with a full year of data; dropdown to change | Nearest with full year · EXT (DMI) | Yes | Client | Weather fetch |
| Weather year | Dropdown | none (OPEN: default year) | Yes; also a scenario lever | Client | Weather fetch |
| Detail level | Dropdown: day / driving hours / hourly | none (OPEN) | Yes | Client | Weather fetch |
| Temperature shift (K) | Number | 0 | Yes | Client | `T_amb_h` |
| Reference wind (m/s at 10 m) | Number (More settings) | 5.028 m/s at 10 m · HDEV decision, replaces VECTO's 3 m/s at 4 m | Yes (engineering view) | Standard | `crosswind_engine` |
| Worst-day case | Toggle | Off | Yes | Client | Separate scenario |

Not user inputs: yaw angle clamp of 10 degrees (page 14). Temperatures are converted to kelvin by the parser.

## 8. Charging

Sizing mode computes P = E / t; simulation mode steps through time. Clients see three strategy names; the internal names (ASAP, JIT, EDF, cost-based) stay hidden.

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Charging strategy | Dropdown: Lowest cost / Grid-friendly / Ready earliest | none (OPEN) | Yes; also a scenario lever | Client | Charging stage |
| Charger power per point (kW) | Number or pick from charger list (page 11) | none | Yes | Client | Charging stage |
| Number of charge points | Number | none; an output in greenfield sizing | Yes | Client | Charging stage |
| Load factor (–) | Number (More settings) | 0.85 | Yes | Client | Charging stage |
| Ready-by time (hh:mm) | Time | none | Yes | Client | Charging stage |
| Time step (min) | Number (More settings) | OPEN: must come from Energinet specs; the mock-up shows 5 min as an ASSUMP | Yes | Standard | Simulation mode |
| Truck-to-point assignment | Table or auto | none | Yes | Client | Charging stage |
| Available power over time `available_power(t)` | Derived from page 9 (fixed value, metered profile or logger) | none | Via page 9 | Client | Charging stage |
| Offer flexibility to markets | Toggle | Off | Yes | Client | Flexibility output |
| Markets | Multi-select: FCR-D, FCR-N, mFRR, aFRR | none | Yes | Client | Flexibility output |

Flexibility is always calculated as an output; the toggle and market choice only decide what is reported as an offer. Battery limits (max charge rate, connector) come from page 4e. Start and target state of charge are not specified in the sources read for this inventory: OPEN.

## 9. Depot and grid

Capacity is an input in brownfield mode (an existing connection) and an output in greenfield mode (the tool sizes it). Either way it reaches charging as a time-varying `available_power(t)`.

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Site mode | Toggle: brownfield / greenfield | none | Yes | Client | Capacity logic |
| Site address | Text / map pick | none | Yes | Client | Grid company, weather |
| Grid company | Dropdown: Radius, Cerius, N1, TREFOR El-net, Other | none | Yes | Client | Connection fee (page 11) |
| Connection size | Number with unit switch (A or kW) | none (brownfield) | Yes | Client | `available_power(t)` |
| Building load | Choice: fixed value (kW) / metered hourly profile (Eloverblik, via MitID connect) / CT-logger upload | none | Yes | Client | `available_power(t)` |
| Spare power (kW) | Number | Computed from connection minus building load | Yes | Client | `available_power(t)` |
| Parking spaces and power per space | Table | none | Yes | Client | Charge-point count |
| Access: full or limited (FNA / BNA) | Dropdown | none | Yes | Client | Flexibility, `available_power(t)` |
| Connect to Eloverblik | Connect button | Off | Yes | Client | Building load |

Outputs shown on this page in greenfield mode (not inputs): required connection size and number of charge points.

## 10. Prices

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Price area | Dropdown: DK1 / DK2 | Auto from site address | Yes | Client | Spot price fetch |
| Electricity spot price (DKK/kWh, hourly) | Auto fetch; or upload own hourly series | Energinet energidataservice · EXT | Yes | Client | Charging cost |
| Price level | Dropdown: low / expected / high | Expected (OPEN: how the levels are defined) | Yes; also a scenario lever | Client | Cost |
| Grid tariff and taxes (DKK/kWh) | Number or table | none (OPEN: source per grid company) | Yes | Client | Cost |
| Diesel (DKK/l) | Number | 11.65 · OK.dk Jan–Jun 2024 plus 0.50 for the duty rise (COWI base case uses 11.15) | Yes | Client | Diesel comparison |
| AdBlue (DKK/l) | Number | 6.96 · source to confirm | Yes | Client | Diesel comparison |
| HVO100 (DKK/l) | Number | 19.97 · source to confirm | Yes | Client | Diesel comparison |
| Public fast-charging price (DKK/kWh) | Number | 3.25 · FDM 2024 | Yes | Client | Cost of public charging |
| Current diesel use (l/100 km) | Number | none | Yes | Client | Diesel comparison |

Price paths over the ownership period (Energistyrelsen Klimastatus) are a planned input and not built.

## 11. Costs and finance

**11a. Ownership and vehicle costs**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Ownership period (years) | Dropdown: 8 / 10 / 12 | none (OPEN); also a scenario lever | Yes | Client | TCO |
| Financing | Dropdown: loan / lease / cash | none | Yes | Client | TCO |
| Interest rate (%) | Number | 3.45 · NO SOURCE (COWI sample) | Yes | Client | TCO |
| EV truck price (DKK) | Number or LIB | 2,050,000 · NO SOURCE (COWI sample) | Yes | Client / OEM | TCO |
| Diesel truck price (DKK) | Number | 1,150,000 · NO SOURCE (COWI sample) | Yes | Client | TCO |
| Service, EV vs diesel (DKK/month) | Numbers | 7,685 vs 5,000 · NO SOURCE (COWI sample) | Yes | Client | TCO |
| Insurance, EV vs diesel (DKK/month) | Numbers | 1,476 vs 768 · NO SOURCE (COWI sample) | Yes | Client | TCO |
| Driver wage (DKK/month) | Number | 30,000 · NO SOURCE (COWI sample) | Yes | Client | TCO |
| Residual value (% of price, per year) | Number or table | 15 % for years 1–6 · NO SOURCE (COWI sample) | Yes | Client | TCO |

**11b. Depot costs**

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Charger hardware and trenching (DKK) | Pick a charger class or enter own | COWI bands below (2024 operator prices, operator not named; verify) | Yes | Client | TCO |
| Grid connection fee (DKK) | Computed from grid company and amps, or entered | Formulas below | Yes | Client | TCO |
| Depot amortisation period (years) | Number | OPEN (about 30 years proposed vs 10 for vehicles; not decided) | Yes | Client | TCO |

Charger bands (DKK):

| kW | Amps | Hardware | Trenching |
|---|---|---|---|
| 22 | 35 | 12,500 | 10,000 |
| 43.5 | 80 | 120,000 | 16,000 |
| 50 | 80 | 150,000 | 50,000 |
| 80 | 125 | 200,000 | 150,000 |
| 150 | 250 | 400,000 | 250,000 |
| 400 | 650 | 700,000 | 500,000 |

Connection fee formulas:

- Radius (COWI sheet, may be stale): 17,950 DKK base for the first 25 A plus 1,280 DKK per extra A.
- Cerius 2026, incl. VAT: 23,500 DKK for the first 25 A; then per extra A: C 1,812.50, B-lav 1,737.50, B-høj 1,675; A-lav 1,637,500 per MVA, A-høj 900,000 per MVA.
- N1, TREFOR El-net: no formula in the sources read (enter manually).

**11c. Not built yet:** NPV with a discount rate (Vejdirektoratet rule: year 1 discounted one period), sensitivity ranges on prices, and price paths.

## 12. Taxes, subsidies and CO₂

| Field (unit) | Input | Default · source | Overwrite | Who | Feeds |
|---|---|---|---|---|---|
| Km-based road tax inputs: weight class, CO₂ class, zone | Dropdowns | Auto from vehicle group and route | Yes | Client | TCO |
| Road tax rate (DKK/km) | Number / table by year | EV 0.1008 vs diesel 0.8525 for 2025–27; steps up in 2028 and 2029 · source in project data; weight class to confirm | Yes | Client | TCO |
| Subsidy | Dropdown: none / Vejdirektoratet pool / German BMV scheme / custom amount (DKK) | none; the Vejdirektoratet pool closed 30 Sep 2026 | Yes | Client | TCO |
| Grid CO₂ intensity (g/kWh) | Number or yearly table | Energistyrelsen series, 41.5 falling to 7.0 over 2024–2034 · EXT (the mock-up used 19.35) | Yes | Client | CO₂ result |
| Diesel CO₂ factor (kg/l) | Number | 2.65 · NO SOURCE (sample) | Yes | Client | CO₂ result |
| CO₂ at actual charging hours | Toggle | Off · planned (Energi Data Service CO2Emis) | Yes | Client | CO₂ result |

## 13. Scenario levers

A scenario is the base project plus a list of changes; `runner.run(base, changes)` restarts the pipeline at the earliest stage the change touches. The assistant-UI spec lists five levers:

| Lever | Page | Stage restarted |
|---|---|---|
| Fleet size | 1 | Charging / depot |
| Charging priority (strategy) | 8 | Charging |
| Electricity price (level) | 10 | Costs |
| Weather year | 7 | Crosswind / driver model onwards |
| Ownership years | 11 | TCO |

Input: dropdown or slider per lever, a "new scenario" button (a compare view is not specified in the sources read). Any other field can also be changed in a scenario; these five are the ones promoted to a quick control. The stage column is my reading of the pipeline order, not a stated rule.

## 14. Hidden and auto-filled values (not in the UI)

These are filled by the resolver / `defaults.py` and are never typed by a client. Each still carries a source tag in the audit block; whether any are exposed in engineering view is a registry choice.

| Value | Where it comes from |
|---|---|
| VECTO reference payload table, body and trailer masses, reference height, CdxA_Default | Resolver lookup by vehicle group and mission (STD) |
| Truck acceleration curves (`vacc_v`, `vacc_acc`, `vacc_dec`), design speed 85 km/h | VECTO table (STD) |
| Driver-model parameters (`lac_*`, `df_*`, `os_*`), `brake_margin`, `v_min_coast` | `defaults.py` |
| Reference mass for the first driver-model pass, then the exact final pass | Pipeline rule |
| Yaw clamp 10 degrees, never average across years | HDEV decisions |
| Gravity g, air density inputs (`p_air`, `R_air`), `beta` | Constants / computed |
| Run fingerprint (inputs, versions, sources, dates) | Tool output |
| Slot metadata `{value, unit, source, date, label, provided_by, locked, version}` | M6.7, still open |
| Units conversion, kelvin, SI | Parser |

The parser only cleans, formats, selects, converts units and checks inputs. It holds no defaults and does no calculation.

## 15. Open decisions and defaults with no source

The UI needs these settled, or needs the field to show the OPEN / NO SOURCE tag, before it is built.

**Open decisions**

- Default payload basis: VECTO reference payload, max payload, or reference plus a max-payload run.
- Mixer PTO default (Ban vs Bae); half-second PTO profile handling; PTO transmission drag (parked); the mechanical-PTO question.
- Drivetrain default rule: calibrate to EEA data vs the V-C bus method; loss maps vs separate efficiencies.
- Altitude pressure: per route or per row.
- Cold-tyre factor Kt and wet/ice road factor (planned, not built).
- Charging time step (must come from Energinet specs); whether Cond runs while coasting.
- Slot shape (M6.7) and which fields are open, collapsed or hidden in the registry.
- Weather year and detail defaults; price-level definitions; depot amortisation period.
- Whether GPS coordinates should pick the weather station.

**Defaults with no verified source (must not be shown as fact)**

- COWI sample values: EV and diesel truck price, service, insurance, interest 3.45 %, driver wage, residual value 15 %.
- Diesel CO₂ factor 2.65 kg/l; specific heat of air cp 1,005.
- Dwell time 45 min per stop (dt-cargo median is 22 min); speeds 30 / 50 / 80 km/h and flat grade for typed routes.
- Placeholder drivetrain efficiencies 0.95 / 0.95 / 0.98; PTO efficiency 1.0; electric PTO motor efficiency.
- Cab geometry and U values for thermal HVAC; rotor inertia `J_rotor` (no fleet default).
- AdBlue 6.96 and HVO100 19.97 DKK/l (confirm source); VECTO-usable battery factor 0.855 (confirm).
- Charger hardware prices (2024, operator unnamed) and the Radius fee formula (may be stale).
