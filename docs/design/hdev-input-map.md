# HDEV input map: every function, every input, every path

Written 16 Nov 2026 for Bob, to build the UX from by hand.
Status of this file: **living document**. Update it when a function or a decision changes.

---

## 0. How to read this file

### 0.1 What this file is

For every function in the engine (written, in progress, and planned) this file lists:

1. every **argument** the function takes;
2. every **way that argument can be filled** (the branches: user types it, a library gives it, a standard value gives it, an external source gives it, or another function computes it);
3. which branches **close or open other inputs** (so the same thing is never entered twice);
4. what is **required**, what has a **default**, and what **blocks the run** when missing;
5. every **output**, and which outputs the user sees.

Part A is the tree (the picture). Part B is the same content from the user's side, input by input. Part C is the same content from the engine's side, function by function. Part D covers the stages that are not written yet. Part E is the list of lock/unlock rules. Part F is outputs. Part G is open decisions and conflicts between documents.

### 0.2 Sources this file was built from

| Source | What it gave |
|---|---|
| Bob's notebook `HDEV_NEW (7).ipynb` (attached 16 Nov) | The function signatures in Part C. This is the code of record. |
| Project closeouts 12, 13 and 16 Nov (`force-paux-pto`, `hvac-final`, `drivetrain-calibration`, `consumption-walkthrough`, `step6-drivetrain-inputs`), `pto-knowledge-2026-11-12`, `handover-function-finalization-2026-11-12`, `status-engine`, `status-data-library` | Decisions, defaults, parser jobs, open items. |
| `ui-input-list-2026-10-26`, `hdev-ui-input-inventory-2026-11-13` (repo branch `ui-ia-research-2026-11`), the 14 Nov Kiro UI prompt (Appendix A and B) | Earlier input lists and the list of planned functions. |
| Kiro's `inputs_register.csv` (PR #35, 274 rows) | Cross-check only, so nothing is missed. Kiro output can be wrong, so nothing is copied from it without a second source. |
| `results-gap-analysis-2026-10-26`, `outputs-fna-bna-battery-passport-2026-10-28`, `review-other-tools-all-features-2026-11-09` | Outputs, and inputs other tools ask for. |
| The three Excel files (`eltiltrucks-beregner-ark.xlsx` from COWI, `Elindsigt2.2.xlsx`, `ChargePointCalculator_v5.xlsx`), read cell by cell again on 16 Nov | The cost, tax, CO₂, electricity-bill and municipal-demand inputs in Part D. |
| VECTO resource files in the repo (`reference/vecto/resources/`) | The exact dropdown lists (aux technologies, bodies, trailers, crosswind sets, PTO types). |
| Repo `src/` (Kiro's draft charging, sizing, calendar, TCO and CO₂ modules, all marked "NEW, Bob to review") | Shapes of the planned functions. They are drafts, not decisions. |
| Past chats (2 Sep to 16 Nov) and project memory | Design decisions with dates. |

### 0.3 Tags used

**Status of a function or an input**

| Tag | Meaning |
|---|---|
| `FINAL` | Function is written and finalised by Bob. |
| `WIP` | Written, still being worked on (today: `consumption_engine`). |
| `DESIGNED` | Bob has decided how it works. Not coded yet. |
| `PLANNED` | Agreed that it will be built. The inputs are known from the project documents. |
| `PROPOSED` | Not decided by Bob. Either Claude's suggestion or something another tool asks for. Listed so it is not forgotten. **Bob decides.** |
| `OPEN` | A decision Bob has not made yet. |
| `PARKED` | Deliberately postponed by Bob. |

**Where a value comes from (the "ways we get it")**

| Tag | Meaning |
|---|---|
| `USER` | The user types, picks or uploads it. |
| `LIB` | Filled from a library when the user picks an entry: vehicle library (EEA certified data plus spec sheets), charger library, PTO profile library, saved routes, saved payload profiles, schedules. |
| `STD` | A standard value looked up by `defaults.py` (VECTO declaration tables, Regulation (EU) 2017/2400 annexes). |
| `EXT` | Fetched from outside: DMI (weather), Energinet Energi Data Service (prices, CO₂), Eloverblik (meter data), grid company price lists. |
| `CALC` | Computed by an engine function from other inputs. Never typed. |
| `CONST` | A physics or model constant kept in `defaults.py`. Not shown to clients. |

**How strongly the tool needs it**

| Tag | Meaning |
|---|---|
| `REQ` | Required. No default exists. A missing value blocks Run. |
| `DEF` | Has a default (`STD`, `LIB`, `EXT` or `CONST`). The user can overwrite it. |
| `OPT` | Optional feature. Off until the user turns it on. |
| `AUTO` | Never entered. Produced by the tool. |

### 0.4 Rules that apply to every input (decided earlier, repeated here because the UX depends on them)

1. **One project JSON.** The UI (or the AI assistant) only fills the JSON. All logic is in Python. [decided 27 Sep, 15 Nov]
2. **`fill()` marks every value** as *given*, *default* or *missing*, like PVsyst. `check(project)` runs the readers and the parser checks and stops before the engine. It returns the list of missing, defaulted and wrong values. The UI shows that list. [decided 14–15 Nov]
3. **Defaults live only in `defaults.py`**, each with value, unit, source and label. Not in function signatures, not in the parser, not in JavaScript. [decided 13 Nov]
4. **The parser** only cleans, converts units, selects and checks. **All calculations are in the engine.** [decided 12 Nov]
5. **SI inside the engine.** The UI shows t, km, km/h, °C, kW, kWh, min. The parser converts once. [decided 12 Nov]
6. **Any default can be overwritten.** An overwritten value is "your value" and can be reset. A custom value that replaces a VECTO value is labelled non-VECTO in the report. [decided 15 Oct]
7. **One branch per input.** When an input has several ways in, the user picks one way. The other ways close. Part E lists every such rule.
8. **Inputs the user cannot realistically give are not asked.** They come from standards or are derived. [decided 22 Oct]
9. **No source text next to fields.** At most a small mark. Sources go in the report and in the Check-and-run list. [decided 13–14 Nov]
10. **Three views on the same engine:** client view, OEM view, engineering view (physics names). OEM-only fields are greyed for clients. [designed; the slot shape `{value, unit, source, date, label, provided_by, locked, version}` is still `OPEN`]

### 0.5 What Claude assumed while writing this (not decisions)

- Where two project documents disagree, the **newer** one is used and the conflict is listed in Part G.
- Input IDs such as `veh.curb_mass` are **labels made up for this file** so the tree, the tables and the lock rules can point at each other. They are not code names. Rename them freely.
- The "map" route source (the user marks start, stops and return on a map) is taken from Bob's 16 Nov brief. In the older documents it only appears as the map API behind the planned AI adapter. It is listed as its own branch with status `PLANNED`.
- A "generic curb mass per vehicle class" is taken from Bob's 16 Nov brief. No document names its source yet, so the branch is listed and its source is marked `OPEN`.
- Nothing in Part D (planned stages) is a decision unless it carries a date.

---

## 1. The whole flow in one page

```
USER / AI ASSISTANT
   │  fills
   ▼
PROJECT JSON  (project, fleet rows, templates, depot, weather, prices, costs)
   │
   ▼
run(project)   or   check(project)  = same path, stops before the engine
   │
   ├─ READERS  one per input type, all give the same shapes
   │     read_vdri · read_typed · read_gps* · read_map* · read_callouts*
   │     read_weather (stored DMI files) · read_vptoel · vecto_loss_map
   │                                                     (* = planned)
   ├─ PARSER
   │     fill()       prefill from libraries + defaults.py, list the dates,
   │                  mark given / default / missing, run all checks
   │     to_engine()  convert to SI, build the argument set per function
   │
   ├─ ENGINE, once per (vehicle template × route × payload × PTO)
   │     E1 payload_engine      waypoints → payload on start + stop rows
   │     E2 pto_engine          waypoints → PTO flags and 1 s profiles
   │     E3 crosswind_engine    wind × speed → W1, W2 tables
   │     E4 driver_model        waypoints → 1 s rows (T, S, V, A, grade, M)
   │     E5 force_engine        rows → mass-free coefficients
   │     E6 SP_power_helper     steering tables → SP power
   │
   ├─ ENGINE, for every operating date
   │     E7 HVAC_thermal        hourly weather → cab HVAC power (thermal mode)
   │     E8 P_aux               aux powers × factors → electric W per aux
   │     E9 consumption_engine  rows + mass + weather + aux + PTO + drivetrain
   │                            → wheel, traction, aux and battery power
   │        (map path only: drivetrain() inside step 6)
   │
   ├─ PLANNED STAGES
   │     battery model (OCV + Ri) · battery ageing and the year-8 check
   │     battery sizing (mode A / mode B) · session hand-over
   │     charging (sizing mode / simulation mode) · depot and grid
   │     flexibility · cost (TCO) · taxes and subsidies · CO₂ · tender sheet
   │     sweeps, sensitivity, Monte Carlo
   ▼
RESULT  (numbers + the source of every value used)  →  result pages, documents
```

**Where a user's choice lives.** The fleet is one table. Each row is a group of identical vehicles with a count and five template picks. Everything about a truck's day hangs off these five templates. [decided 31 Oct to 13 Nov]

```
FLEET ROW  =  count  ×  [ Vehicle | Route | Payload | PTO | Schedule ]
                          │         │       │         │     │
                          │         │       │         │     └ when it runs (B10)
                          │         │       │         └ body equipment power (B5)
                          │         │       └ load along the route (B4)
                          │         └ waypoints + stop table (B2, B3)
                          └ everything physical about the truck (B1, B6–B9)

PROJECT-WIDE (one per project or per depot)
   Weather and cab climate (B11, B12) · Depot and grid · Charging · Prices ·
   Costs · Taxes, subsidies and CO₂ · Tender · Scenarios
```

**Run entry points.** A run does not have to start at consumption. Any stage can be run on its own from user data. [decided 12 Oct; `runner.run(base, changes)` refuses an incomplete entry contract]

```
START AT …            THE USER GIVES INSTEAD OF THE EARLIER STAGES
consumption           the full project (vehicle, route, payload, PTO, weather)
  └ skip consumption  own kWh/km per route (flagged override)
charging only         session list: arrival, departure, energy need (kWh),
                      arrival SOC  + battery + chargers + site limit
flexibility only      load profile (time, kW) + equipment capabilities
cost / CO₂ only       annual energy (kWh), peak (kW), equipment, prices
```

---

# PART A. The input tree

How to read the trees:

- `◉` = **pick exactly one** of the branches below it. Picking one closes the others.
- `☐` = optional, can be combined with its neighbours.
- `→` = what the choice opens. `✕` = what the choice closes.
- `[STD]`, `[LIB]`, `[EXT]`, `[USER]`, `[CALC]`, `[CONST]` = where the value comes from.
- `(REQ)` = no default, must be given. `(DEF)` = default exists, can be overwritten.
- `*PLANNED*`, `*PROPOSED*`, `*OPEN*`, `*PARKED*` = not built yet, see 0.3.

Every leaf is explained in Part B under the same number.

## A0. Top of the tree

```
PROJECT
├─ T1  Vehicle            (per vehicle template)
├─ T2  Route              (per route template)
├─ T3  Stop table         (belongs to the route, per fleet row when edited)
├─ T4  Payload            (per payload template)
├─ T5  PTO / body equipment (per PTO template)
├─ T6  Aerodynamics       (inside the vehicle template)
├─ T7  Tyres and wheels   (inside the vehicle template)
├─ T8  Drivetrain         (inside the vehicle template)
├─ T9  On-board systems   (inside the vehicle template)
├─ T10 Schedule and calendar (per schedule template)
├─ T11 Weather            (per project / depot)
├─ T12 Cab heating and cooling (with Weather)
├─ T13 Battery            *PLANNED*  (inside the vehicle template)
├─ T14 Charging           *PLANNED*
├─ T15 Depot and grid     *PLANNED*
├─ T16 Flexibility        *PLANNED*
├─ T17 Prices             *PLANNED*
├─ T18 Costs and finance  *PLANNED*
├─ T19 Taxes and subsidies *PLANNED*
├─ T20 CO₂ and life cycle *PLANNED*
├─ T21 Tender and offers  *PLANNED*
└─ T22 Scenarios, sweeps, uncertainty *PLANNED*
```

## A1. Vehicle (T1)

```
T1 VEHICLE
├─ ◉ Where does the vehicle come from?
│   ├─ A  Exact vehicle from the library            [LIB]
│   │      → fills: make, model, group, axle layout, curb mass
│   │        (CorrectedActualMass), TPMLM, architecture (E2 / E3 /
│   │        IEPC), motor rated kW, gears, axle ratio, tyre size and
│   │        certified RRC per axle, CdxA range (A1–A24), installed
│   │        and VECTO-usable kWh, steering technology per axle,
│   │        drivetrain numbers (method C) when fitted
│   │      → every filled field stays editable ("your value" + reset)
│   │      ✕ closes: vehicle class picker (group is known)
│   ├─ B  Vehicle class only (sizing, no truck chosen yet)   [STD]
│   │      → user picks: VECTO group (1–16, 51–56) or weight class
│   │        + axle layout + rigid/tractor
│   │      → fills: height, CdxA_Default, body/trailer by mission,
│   │        reference payload, crosswind set, axle load shares,
│   │        aux tables, class drivetrain numbers *OPEN*
│   │      → curb mass: generic for the class *OPEN source*
│   │        or battery sizing mode B computes it (T13)
│   └─ C  Manual entry                               [USER]
│          → user still picks the group (needed for every STD lookup)
│          → every field typed; blanks fall back to STD where one exists
│
├─ Mission  ◉ Long haul / Regional delivery / Urban delivery /
│             Municipal utility / Construction  (+ EMS variants)
│     follows the route when the route is a VECTO cycle;
│     picked by the user for typed, map and GPS routes
│     → selects: body or trailer, reference payload, crosswind set,
│       axle load shares, aux table column
│
├─ Curb mass  m_curb  (kg)                           (REQ in A and C)
│   ◉ library value / generic class value *OPEN* / typed (registration)
├─ Body or trailer mass  m_body_trailer  (kg)        (DEF)
│   ◉ VECTO standard for group + mission [STD] / typed [USER] / 0
│   ├─ body type  B-II, B1–B5 (box), BT1–BT3 (tipper), MU4/MU9/MU11 (refuse)
│   └─ trailer    none / T1 / T2 / ST1 / Dolly+ST1 (EMS) / STT1 / STT2
├─ Gross vehicle weight / TPMLM (kg)                 (REQ for the payload cap)
│   ◉ library / registration papers [USER]
└─ Vehicle height (m)                                (DEF)
    ◉ VECTO reference height for the group [STD] / typed [USER, OEM]
```

## A2. Route (T2) and stop table (T3)

```
T2 ROUTE
└─ ◉ Where does the route come from?
    ├─ A  VECTO cycle (VDRI template)                [STD]
    │      ◉ LongHaul / RegionalDelivery / UrbanDelivery /
    │        MunicipalUtility / Construction
    │      ✕ closes: distance, number of stops, speeds, grade, road type
    │      → stop table: stop time and payload editable, distances locked
    │      → once edited it becomes a "user route" (original untouched)
    ├─ B  Typed summary                               [USER]
    │      → total distance (REQ), number of stops (REQ)
    │      → time per stop (DEF 45 min *unsourced assumption*)
    │      → road type per leg ◉ deep urban / urban / non-urban
    │        → speed (DEF 30 / 50 / 80 km/h *unsourced assumption*)
    │      → grade (DEF flat)
    │      → the tool builds the stop table; everything is editable
    ├─ C  Map *PLANNED*                               [USER + EXT]
    │      → user marks depot, stops, return to depot
    │      → a routing provider gives road distance, speed, altitude
    │        *OPEN: provider not chosen*
    │      ✕ closes: distance, number of stops
    │      → stop time and payload editable; positions edited on the map
    ├─ D  GPS / telemetry upload *PLANNED*            [USER]
    │      ✕ closes: distance, number of stops, speeds, stop times
    │      → the adapter marks stops (zero-speed threshold *OPEN*)
    │      → only payload (and PTO on/off) editable in the stop table
    │      → grade from altitude must be smoothed (adapter job)
    │      → *OPEN*: can measured speed skip the driver model?
    ├─ E  Describe it / call-out logs (AI) *PLANNED*  [USER + EXT]
    │      → text, coordinates or an emergency call-out log
    │      → AI builds waypoints through the same map provider
    │      → user confirms before Run; guesses are flagged
    └─ F  Saved route from the library                [LIB]
           → any of A–E after "save as"; same editability as its source

   Common to every source
   ├─ Departure time from the depot (hh:mm)           (REQ)  → t_start
   ├─ Route name, "save as new template"
   └─ Altitude / air pressure  *OPEN: one value per route or per row*

T3 STOP TABLE   one row per stop (waypoints with stop > 0; depot start excluded)
├─ columns: distance from depot · stop time · payload after the stop ·
│           payload changes here (yes/no) · PTO on (yes/no)
├─ editable by source
│     VECTO cycle : stop time ✔  payload ✔  PTO ✔  distance ✕
│     typed       : everything ✔ (add / remove / move stops)
│     map         : stop time ✔  payload ✔  PTO ✔  position on the map
│     GPS         : payload ✔  PTO ✔   distance ✕  stop time ✕
├─ remove a stop from payload change → it stays a stop for driving
├─ 0-second marker row → can start a drive-PTO part where there is no stop
└─ bulk tools: apply to all, apply to a range  *PROPOSED*
```

## A3. Payload (T4)

```
T4 PAYLOAD
├─ ◉ How does the load change along the route?
│   ├─ constant        → one value (start payload)
│   │                    ✕ closes: end payload, per-stop payloads
│   ├─ linear          → start payload + end payload; equal step at each stop
│   │                    needs at least one stop
│   │                    ✕ closes: per-stop payloads
│   └─ per stop (custom) → one value after every stop, typed in the stop table
│                        ✕ closes: end payload
├─ ◉ Which value?  (the default basis is *OPEN*)
│   ├─ VECTO reference payload for group + mission     [STD]
│   ├─ VECTO low payload                               [STD]
│   ├─ maximum payload = GVW − curb − body/trailer     [CALC]
│   ├─ reference run plus a max-payload run beside it  *OPEN*
│   └─ own value (t)                                   [USER]
├─ Saved payload profile from the library              [LIB]
└─ Check (parser): 0 ≤ payload ≤ GVW − curb − body/trailer
      fail → error, with the hint "move up a vehicle class"
      legal weight limits → warning only *PLANNED*
```

## A4. PTO and body equipment (T5)

```
T5 PTO
├─ ◉ Does the body use power?
│   ├─ no                         ✕ closes everything below
│   └─ yes  → any mix of the three parts below
│
├─ ☐ STOP PART  (works while standing at stops flagged "PTO on")
│   ├─ ◉ power
│   │   ├─ one number (kW), fills the whole stop
│   │   └─ profile (time s, power W), played once per stop
│   │       ◉ VECTO refuse profile (23 s, 0.14993 kWh) [STD]
│   │         library profile [LIB] / own upload or table [USER]
│   ├─ efficiency  stop_pto_eff (DEF 1.0 = value is already electric)
│   └─ ◉ standing time rule
│       ├─ VECTO: standing = stop time + PTO time (DEF)
│       └─ "use stop time as PTO time": standing = max(stop, PTO)
│          (non-VECTO, flagged)
│
├─ ☐ DRIVE PART  (starts when the truck leaves a flagged stop)
│   ├─ ◉ power
│   │   ├─ one number (kW) until the next stop (sweeper)
│   │   └─ profile (time s, power W), played once; keeps running
│   │      through the next stop
│   ├─ efficiency  drive_pto_eff (DEF 1.0)
│   └─ ◉ Does the body have its own electric motor?
│       ├─ yes → power added at the battery (electric)
│       └─ no  → power added at the traction motor shaft (mechanical)
│                (not included in drivetrain method C for now)
│
├─ ☐ ALWAYS-ON PART  (chiller, mixer drum as a constant)
│   ├─ power (W) + efficiency PTO_eff (DEF 1.0)  → goes through P_aux
│   └─ fridge / TRU physics model *PARKED*
│        ATP K value or class · box size · set temperature · COP (REQ)
│
├─ Mechanical PTO type on the gearbox (PTO-tech.csv, 12 rows) *PARKED*
└─ Saved PTO profile from the library   [LIB]  ("save as" from any of the above)
```

## A5. Aerodynamics (T6)

```
T6 AERODYNAMICS
├─ CdxA at zero yaw, CdxA0 (m²)                               (DEF)
│   ◉ OEM declared value [USER, OEM]
│     library: EEA publishes only a range code A1–A24 [LIB]
│       *OPEN: bin edges are not in EEA or the regulation*
│     VECTO standard value for the group, CdxA_Default [STD]
│     Construction mission → CdxA_Construction (VECTO rule)
│   + trailer ΔCdxA added automatically for rigid + trailer (T1 1.3,
│     T2 1.5, EMS 2.1 m²) [STD]; tractors already include the semitrailer
├─ Yaw (crosswind) coefficients a1, a2, a3                     (DEF)
│   ◉ VECTO set by group + mission [STD]:
│       RigidSolo / RigidTrailer / TractorSemitrailer /
│       MediumLorriesRigid / MediumLorriesVan / CoachBus
│     own coefficients or own CdxA-vs-yaw table [USER, OEM]
│       *OPEN: upload format*
├─ Vehicle height (m)  → see T1
└─ Coast-down input  F = A + B·v + C·v²  *PARKED* (would replace Crr + CdxA)
```

## A6. Tyres and wheels (T7)

```
T7 TYRES AND WHEELS
├─ Rolling resistance  Crr  (N/kN in the UI)                   (DEF)
│   ◉ library: certified RRC per axle (EEA axle table) [LIB]
│     EU tyre label class per axle [USER]
│     one typed value [USER]
│     VECTO standard *OPEN: which standard value the parser uses*
│   → combined with axle load shares (by mission) and twin-tyre flags into
│     one Crr_eff; trailer axles added from VECTO mission data
├─ Rolling form exponent  beta   ◉ 0.9 VECTO (DEF) / 1.0 linear   [CONST]
├─ Tyre size → dynamic radius r_dyn (m)                        (REQ, no default)
│   ◉ library tyre size [LIB] / pick size from Wheels.csv (130 sizes) [STD]
│     / typed radius [USER]
├─ Wheel inertia  theta_red (kg·m²)                            (DEF 0 = off)
│   ◉ from tyre size (Wheels.csv inertia × number of wheels) [STD]
│     typed [USER, OEM] / 0
├─ Cold-tyre factor Kt *PLANNED*  ◉ off / from tyre load index (0.006 / 0.010)
└─ Wet, snow or ice road factor *PLANNED, OPEN*
```

## A7. Drivetrain (T8)

```
T8 DRIVETRAIN
├─ ◉ How are drivetrain losses given?          (pick one; no mixing)
│   ├─ A  Method C from the drivetrain library            [LIB]   ← DEFAULT
│   │      three numbers: drive_eff, regen_eff, drivetrain_drag_N
│   │      per truck (fitted on EEA certified results)
│   │      per weight class when no truck is chosen *OPEN: class numbers
│   │        show a wide spread (group 5: 15.8 points P10–P90)*
│   ├─ B  Method C typed by the user                      [USER]
│   │      the same three numbers
│   ├─ C  Three efficiencies (motor × inverter × gearbox) + regen efficiency
│   │      [USER]  → parser multiplies them into drive_eff; drag = 0
│   │      (this is method C with zero drag, not a third engine path)
│   └─ D  Full loss-map set (OEM)                         [USER, OEM]
│          axle map + one gearbox map per gear + motor map + motor limit
│          curves + ratios + ADC + gear per row
│          → runs drivetrain() instead of the three numbers
│          ✕ closes: A, B, C
│          partial set → error, no silent fallback
│          → also needs the gear rule *OPEN* and J_rotor
│
├─ Regen cap  P_regen_max (kW)                              (REQ for A–C)
│   ◉ rated motor power from the library (IEPC rated where IEPC) [LIB]
│     typed [USER, OEM]
│   map path: the motor's generation curve does this instead
├─ Drive-side limit  P_drive_max (kW)  *OPEN: rated or peak*
│   not a clip: rows above it are counted and reported
├─ No-regen speed  v_no_regen  (DEF 5 km/h, VECTO)          [CONST]
├─ Motor power for the driver model  P_max (kW)             (OPT)
│   ◉ rated power [LIB / USER] / none = no cap on acceleration
├─ Coasting drag table for the driver model  drag_v, drag_F
│   ◉ VECTO E2 drag table (DEF for all trucks, decided 3 Nov) [STD]
│     from the user's own drivetrain data [USER, OEM]
│     zero drag
├─ Rotor inertia  J_rotor (kg·m²)   ◉ 0 (DEF, neutral) / OEM value
├─ Total ratio  i_total             ◉ 1 (neutral) / one number / per row
│   gear rule when the gear is unknown *OPEN*
└─ Acceleration and braking limits (.vacc)
    ◉ VECTO Truck.vacc (DEF) [STD] / own curve [USER, engineering view]
```

## A8. On-board systems (T9)

```
T9 ON-BOARD SYSTEMS   (each one: ◉ VECTO table row / own value)
├─ Electric system  ES
│   ◉ VECTO technology [STD]: "Standard technology" /
│       "Standard technology - LED headlights, all"  (by mission)
│     own W [USER]
│   factor ES_alteff: 0.7 for a VECTO row; set 1.0 for an own electric W
├─ Air system  PS
│   ◉ VECTO technology, electric rows only [STD] (9 rows, by mission)
│     own W [USER]
│   factor PS_alteff: 1.0
├─ Steering  SP
│   ◉ VECTO method [STD]: group + mission baseline, number of steered
│       axles (1–4), one technology for all steered axles
│       ("Electric driven pump" / "Full electric steering gear")
│       → SP_power_helper
│     own W [USER]  ✕ closes: steered axles, technology
│   factor SP_alteff: 0.7 for VECTO; 1.0 for an own electric W
│   on only while the truck moves
├─ Motor and battery conditioning  Cond
│   ◉ VECTO value by mission [STD] (600 / 600 / 550 / 550 / 600 W)
│     own W [USER] / thermal model *PLANNED*
│   factor cond_eff: 1.0
│   on while moving or while PTO works *rule under review*
└─ Always-on equipment → see T5 (always-on part)
```

## A9. Schedule and calendar (T10)

```
T10 SCHEDULE  *DESIGNED; calendar builder is a Kiro draft*
├─ Leaves the depot / back at the depot (hh:mm)             (REQ)
├─ Working days  Mon … Sun                                   (REQ)
├─ Shifts per day  ◉ one / several (second shift on the same truck) *PLANNED*
├─ ◉ Public holidays
│   ├─ Danish calendar, computed (Store Bededag dropped from 2024)
│   │   ☐ count Grundlovsdag  ☐ count 24 Dec   (fleet-specific, flagged)
│   ├─ own list of dates
│   └─ none
├─ Shutdown periods (date ranges) *PLANNED*
├─ Exceptions by date (other route, other times) *DESIGNED*
├─ Seasonal route (e.g. winter route) = a second fleet row with its dates
├─ Reduced days (e.g. Saturday at half) *PLANNED*
└─ Emergency / on-call vehicles *OPEN: how they are entered*
```

## A10. Weather (T11) and cab climate (T12)

```
T11 WEATHER
├─ ◉ Where does the weather come from?
│   ├─ A  Stored DMI data (server side)                      [EXT]  ← DEFAULT
│   │      location → nearest station with a full year, per parameter
│   │      ◉ one weather year / several years (→ P50 / P90)
│   ├─ B  Own weather file                                   [USER] *PLANNED*
│   └─ C  VECTO declaration weather (comparison mode)        [STD]
│          wind 3 m/s at 4 m, air density 1.188 kg/m³, no hourly data
│          ✕ closes: location, year, shift, worst day
├─ Level of detail  ◉ hourly (what the engine uses) / drive-hours mean /
│                     daily mean   *OPEN whether the last two stay*
├─ Temperature shift (K)                                     (DEF 0)
├─ Worst day as its own case                                 (OPT)
├─ Air pressure  ◉ fixed 101,325 Pa (DEF) / from altitude *OPEN* /
│                  DMI hourly *OPEN*
├─ Air density  ◉ from temperature and pressure (DEF) /
│                 fixed 1.188 "VECTO mode" *PROPOSED (rho_fixed)*
├─ Wind  ◉ DMI hourly wind at 10 m (DEF) / one mean value (5.028 m/s at
│          10 m, older decision) / VECTO 3 m/s at 4 m
└─ Hidden: wind profile exponent 0.2 · yaw clamp 10° (HDEV decision, stated
           in every report) · height step · angle step · speed grid

T12 CAB HEATING AND COOLING
└─ ◉ How is cab climate power worked out?
    ├─ A  VECTO constant [STD]: "Default" or "None" for group + mission
    │      factor HVAC_eff = 1.25
    │      ✕ closes everything under C
    ├─ B  Own constant W [USER]
    │      factor 1.25, or 1.0 when the value is already electric
    │      ✕ closes everything under C
    └─ C  Thermal model, hour by hour  (factor forced to 1.0)
        ├─ people in the cab                                  (REQ)
        ├─ heater set-up  ◉ heat pump type / ☐ electric heater /
        │                   ☐ fuel heater  → COP and share tables [STD]
        │                   or own COP table [USER, OEM]
        ├─ set-points heat / cool / cooling-off  (DEF 18 / 23 / 17 °C, VECTO)
        ├─ cab data: wall area, U, window area, volume        (REQ, no
        │     sourced default) ◉ OEM values / cab-type template *PROPOSED*
        ├─ max heating and cooling power  (missing → no limit, flagged)
        ├─ ventilation rates (normal, while heating)          (REQ)
        ├─ fresh air  Q  (DEF 100 m³/h; 0 = exactly VECTO)
        └─ hidden constants (heater efficiency, fan power, heat per person,
           clouding, solar factor, waste heat, p, R, cp)
```

## A11. Planned stages (T13–T22), short tree

Full detail in Part D. Everything in this block is `PLANNED` unless marked otherwise.

```
T13 BATTERY
├─ ◉ Mode
│   ├─ A  I have a battery (datasheet or library)
│   │      → installed kWh (REQ) · usable kWh ◉ OEM value / VECTO share
│   │        (≈ 0.855 × installed) / own share
│   │      ✕ closes: sizing inputs
│   └─ B  Size it for me
│          → sizing rule: hardest day, at year-8 capacity, with a buffer
│          → glider mass + pack kWh/kg (REQ, no sourced default)
│          → battery mass feeds back into curb mass and max payload
│          ✕ closes: installed kWh
├─ Electrical model  ◉ EU standard values (Annex Xb App. 10) [STD] /
│                      OEM OCV + Ri tables / none (100 % efficient, today)
├─ Max charging power  ◉ OEM curve / C-rate table [STD: 0.9 C to 80 %] / kW
├─ SOC window (min, max), start SOC, target SOC  *OPEN*
└─ Year-8 check: guaranteed usable capacity at year 8 (%) (REQ for the check)
     ◉ tender or warranty value / OEM SoH curve / ageing model *PROPOSED*

T14 CHARGING
├─ ◉ Mode   sizing (P = E / t)  /  simulation (step by step, OCV + Ri)
├─ ◉ Chargers   size them for me  /  I choose (power, count, library pick)
├─ ◉ Strategy   Ready earliest (ASAP) / Grid-friendly (JIT) / Lowest cost
│     no smart charging on the charger → ASAP only (✕ the other two,
│     ✕ flexibility)
├─ Sharing rule between trucks  ◉ EDF / equal share (ES) / LLF *PROPOSED*
├─ Ready-by time · charger losses · time step *OPEN*
├─ ☐ Opportunity charging (between shifts, at the tip site) *OPEN*
├─ ☐ Public charging share and price
└─ ☐ Robustness cases: charger out, late return, cold week, plug-in discipline

T15 DEPOT AND GRID
├─ ◉ Site   brownfield (connection exists → size is an input)
│           greenfield (→ required connection is an output)
├─ ◉ Building load   one number / Eloverblik hourly (MitID) /
│                    CT-logger upload / none
├─ ◉ Access   full (FNA) / limited (BNA → what-if cut) / stepwise
├─ Grid company → customer category → connection fee formula
└─ ☐ fleet growth phases · ☐ buffer battery · ☐ on-site solar *PROPOSED*

T16 FLEXIBILITY   always calculated; inputs decide what is reported as an offer
├─ ☐ offer to markets → products FCR-D / FCR-N / mFRR / aFRR, aggregator
├─ ☐ DSO flexibility (pilot terms)
└─ ☐ V2G (needs ISO 15118-20 on truck and charger)

T17 PRICES
├─ ◉ Electricity   spot by hour, fetched [EXT] / own hourly file /
│                  day + night price / one flat price
├─ ◉ Grid tariff   grid company time-of-day table / own values
├─ ◉ Price path    flat / Energistyrelsen projection / own %/year
└─ Diesel, AdBlue, HVO100, biogas, public charging price

T18 COSTS AND FINANCE
├─ ◉ Financing   cash / loan (annuity + residual) / lease
├─ ◉ Residual value   % table by holding years / linked to battery SoH *OPEN*
├─ ◉ Charger cost     library band by kW / own quote
├─ ◉ Connection fee   grid company formula (amps) / own figure
└─ vehicle prices, service, insurance, tyres, wages, downtime, lost time

T19 TAXES AND SUBSIDIES
├─ Km-based road tax  ◉ auto from weight class + CO₂ class + zone / own rate
├─ ☐ ETS2 on diesel from 2028
└─ ◉ Subsidy   none / scheme / own amount

T20 CO₂
├─ ◉ Grid factor   Energistyrelsen yearly path / own value /
│                  actual charging hours (Energi Data Service)
└─ ☐ life cycle: vehicle + battery production, fuel well-to-tank

T21 TENDER AND OFFERS   (only when the project purpose is a tender)
├─ buyer side: award weights, score curves, minimum requirements
└─ supplier side: one column of spec values per bid, guarantees

T22 SCENARIOS
├─ base + list of changes (any field) · quick levers
├─ ☐ sweep (finite option lists) · ☐ sensitivity · ☐ Monte Carlo
└─ compare runs
```

---

# PART B. Every input, from the user's side (written functions)

Each table row is one input. Columns:

- **ID**: label used in this file only.
- **Input**: what the user sees, with the UI unit → the engine unit.
- **Ways to fill it**: the branches. Lettered branches are exclusive (pick one).
- **Default · source**: what `defaults.py` gives when the user gives nothing.
- **Need**: `REQ`, `DEF`, `OPT`, `AUTO` (see 0.3).
- **Feeds**: the engine argument(s) it ends up in.
- **Checks and notes**: parser checks, what it locks, flags for the report.

## B1. Vehicle: identity and mass (tree T1)

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `veh.source` | Where the vehicle comes from | (A) library pick, (B) vehicle class only, (C) manual | none | REQ | selects every lookup below | Choice shown on the page, not in a popup, because it changes which fields appear. |
| `veh.library_pick` | Library vehicle | Searchable list. One row per exact configuration (make, model, architecture, battery, motor, axle, CdxA range). [LIB: EEA HDV CO₂ data, reporting period 2024–25, plus spec sheets] | none | REQ in (A) | prefill of most `veh.*`, `tyre.*`, `drv.*`, `bat.*` fields | 4,603 trucks with a battery record are the usable set. Hybrids and buses are left out. A picked value becomes an editable copy. Every library value carries a provenance class (certified measured / certified standard values / VECTO simulated / registry / OEM claim / trade press / derived). |
| `veh.group` | VECTO vehicle group | (a) picked directly: 1, 1s, 2, 3, 4, 5, 9, 10, 11, 12, 16, and medium lorries 51–56; (b) looked up from vehicle category (rigid / tractor / van) + axle configuration + TPMLM band [STD `SegmentTable.csv`]; (c) from the library pick | none | REQ | key for height, CdxA_Default, body/trailer, reference payload, crosswind set, axle load shares, `SP-Table`, `HVAC-Table` | Groups 6, 7, 8 have empty steering baselines in VECTO. Groups 1s–3 have no Municipal or Construction steering baseline. The parser must give a clear error for an empty table cell. |
| `veh.mission` | Mission profile | (a) follows the VECTO cycle when the route is one; (b) picked by the user: Long haul, Regional delivery, Urban delivery, Municipal utility, Construction, plus EMS variants for long haul and regional | none | REQ | column key in every VECTO aux table; body/trailer; reference payload; crosswind set | For a typed, map or GPS route the user must still say which mission it resembles, because VECTO's standard values are stored per mission. This is an assumption the report must state. |
| `veh.curb_mass` | Empty weight of the chassis (t or kg → kg) | (a) library: EEA `CorrectedActualMass`; (b) generic value for the class; (c) typed from the registration papers; (d) computed in battery sizing mode B (glider + battery) | (b) has no named source yet: **OPEN** | REQ unless (d) | `m_curb` in `consumption_engine`; part of `coast_mass` | The library keeps curb mass as a min–max range per configuration (decided 7 Nov), so after a library pick the UI still needs one value. Which value is pre-filled (min, max, mid) is **OPEN**. |
| `veh.body_type` | Body | (a) VECTO standard body for group + mission [STD]: box `B-II`, `B1`–`B5`; tipper `BT1`–`BT3` (construction); refuse `MU4`, `MU9`, `MU11` (municipal); (b) none; (c) own | from `SegmentTable.csv` columns Body / Body Construction / Body MunicipalUtility | DEF | lookup for `veh.body_mass` | Body list and masses: `Body_Trailers_Weights.csv`. |
| `veh.body_mass` | Body weight (kg) | (a) VECTO mass for the body type: B-II 800, B1 1,600, B2 1,900, B3 2,000, B4 2,100, B5 2,200, BT1 2,000, BT2 3,230, BT3 4,355, MU4 6,000, MU9 6,750, MU11 6,750 kg [STD]; (b) typed | (a) | DEF | part of `m_body_trailer` | Kiro checked on the eCanter: EEA curb mass + standard body + payload = EEA test mass within 1 kg. |
| `veh.trailer_type` | Trailer | (a) VECTO standard for group + mission [STD]: none, `T1`, `T2`, `ST1`, `Dolly` (EMS only), `STT1`, `STT2`; (b) none; (c) own | from `SegmentTable.csv` columns Trailer / Trailer Construction / EMS | DEF | lookup for `veh.trailer_mass`, trailer ΔCdxA (`aero.cdxa0`), trailer axles (`tyre.crr`), wheel count (`tyre.theta_red`) | Picking a trailer changes four other inputs at once. All four follow automatically. |
| `veh.trailer_mass` | Trailer weight (kg) | (a) VECTO: T1 3,400, T2 5,400, ST1 7,500, Dolly 2,500, STT1 6,100, STT2 5,600 kg [STD]; (b) typed | (a) | DEF | part of `m_body_trailer` | The engine argument is one number: body + trailer. In the notebook it is still called `m_trailer`. |
| `veh.gvw` | Gross vehicle weight, TPMLM (t → kg) | (a) library; (b) typed from the registration papers | none | REQ for the payload cap | parser check on payload (B4); not an engine argument | VECTO also caps the combination at 40 t (tractor + semitrailer) and 60 t (EMS). Legal weight limits (Danish BEK 1447/2025, ZEV allowance) are planned as a **warning only**. |
| `veh.height` | Vehicle height (m) | (a) VECTO reference height for the group [STD]: groups 1, 1s 3.6; 2 3.75; 3 3.9; 4, 5, 7–12 4.0; 6 3.75; 13–16 3.6; medium rigid 3.5; van 2.9; (b) typed | (a) | DEF | `vehicle_height` in `crosswind_engine` | |
| `veh.ref_mass` | Reference mass for the driver | Computed: curb + body/trailer + VECTO reference payload for group and mission | n/a | AUTO | `coast_mass` in `driver_model` (screening run) | For the final pass on a chosen truck the driver is rerun at the exact mass. Which single mass to use when payload changes along the route (start, mean, other) is **OPEN**. |
| `veh.diesel_use` | Diesel the truck uses today (l/100 km) | typed | none | OPT now, REQ for cost | diesel comparison (Part D) | Listed here because users look for it on the vehicle. |

## B2. Route (tree T2)

All sources end in the same four arrays for the driver: `wp_s` (m), `wp_v` (m/s), `wp_stop` (s), `wp_grade` (%), plus one PTO flag and one payload value per waypoint. Every reader returns exactly this shape, so a new source is one new reader and nothing else changes.

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `rt.source` | Where the route comes from | (A) VECTO cycle, (B) typed, (C) map, (D) GPS upload, (E) describe it / call-out log, (F) saved route | none | REQ | picks the reader | The UI writes `"source"` into the route in the project JSON. `run()` picks the reader from it. |
| `rt.vdri` | VECTO cycle | LongHaul, RegionalDelivery, UrbanDelivery, MunicipalUtility, Construction [STD, files in `reference/vecto/resources/MissionCycles/`] | none | REQ in (A) | all four waypoint arrays; the `<PTO>` column of MunicipalUtility | Columns in the files: `<s>` distance m, `<v>` target speed km/h, `<grad>` %, `<stop>` s, optional `<PTO>` and `HW`. Every row is a waypoint. No resolver needed. The file is never changed. |
| `rt.distance` | Total distance per day (km → m) | typed | none | REQ in (B) | `wp_s` | Closed in A, C, D, E. |
| `rt.n_stops` | Number of stops | typed | none (0 allowed) | REQ in (B) | `wp_s`, `wp_stop` | Stops are spaced evenly until the user edits them. Even spacing is an assumption that must be flagged. Closed in A, C, D, E. |
| `rt.dwell` | Time at each stop (min → s) | typed; then per stop in the stop table | 45 min · Bob's judgement value, **unsourced** (the dt-cargo sample has a median of 22 min between trips) | DEF | `wp_stop` | Must be labelled an assumption. |
| `rt.road_type` | Road type per leg | deep urban / urban / non-urban | none | REQ in (B) | picks `rt.speed` | |
| `rt.speed` | Speed per road type (km/h → m/s) | (a) default per road type; (b) typed | 30 / 50 / 80 km/h · Bob's judgement values, **unsourced** | DEF | `wp_v` | "Speed wins over end time" when both are given (decided 2 Sep). |
| `rt.grade` | Grade (%) | (a) flat; (b) typed per leg; (c) from altitude along the route (map, GPS) | 0 · assumption | DEF | `wp_grade` | The driver turns grade into altitude and back into a per-row grade. GPS altitude must be smoothed first: raw 0.5 m noise adds +21 % to +41 % energy (Kiro PR #30). |
| `rt.map` | Map route | user marks depot, stops, return; a routing provider returns road distance, speed and altitude | none | REQ in (C) | all four arrays | `PLANNED`. Provider not chosen (cost, privacy). No reader designed. |
| `rt.gps_file` | GPS / telemetry file | upload | none | REQ in (D) | all four arrays | `PLANNED`. The adapter writes the stop duration on the first zero-speed row of each stop, so the single rule `stop > 0` works for every source. Zero-speed threshold **OPEN**. Whether a log with measured speed can skip the driver model **OPEN**. |
| `rt.describe` | Free text, coordinates, or an emergency call-out log | text or upload, read by the AI adapter | none | REQ in (E) | all four arrays | `PLANNED`. Uses the same map provider for road distance. The user confirms what the AI read before Run (Claude's suggestion). |
| `rt.saved` | Saved route | pick from the library | none | REQ in (F) | all four arrays | Keeps the editability of its original source. |
| `rt.depart` | Departure time from the depot (hh:mm) | (a) from the schedule template (`sch.out`); (b) typed on the route | none | REQ | `t_start` in `consumption_engine` (seconds from the start of the weather array) | Parser: `t_start ≥ 0`; weather must cover the whole trip; same time base (DMI is UTC, the user thinks in local time). Entered once: if the schedule has it, the route field is closed. |
| `rt.speed_cap` | Top speed | (a) VECTO design speed 85 km/h for all trucks [STD]; (b) typed | (a) | DEF | caps `wp_v` | How the cap is applied to typed routes is not written in the documents: check when the reader is written. |
| `rt.altitude` | Altitude of the route (m) | (a) none (sea level); (b) one value per route; (c) per row | none | OPT | air pressure `p_air` | `OPEN`: (b) or (c). Effect at 1,000 m: −6.1 % on Regional (Kiro PR #30). Not relevant for Denmark, relevant for EU expansion. |
| `rt.name` | Route name, "save as new template" | text + button | none | OPT | library | An edited VECTO cycle is saved as a user route. |

**Checks the parser must run on every route (all decided):** first waypoint distance = 0; distances never decrease; no two stops at the same distance; a waypoint with stop time > 0 must have target speed 0 (VECTO throws otherwise); a stop must not be followed only by 0 km/h waypoints (the truck would never move off); a cycle that starts at 0 km/h with no stop gets a 1 s stop (the engine does this, like VECTO).

## B3. Stop table (tree T3)

The stop table is a **view** of the waypoints with `stop > 0`, minus the depot start. The UI filters rows for display only. Edits go straight into the waypoint list. One JSON goes to Python on Run.

| ID | Column | Ways to fill it | Default | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `stop.distance` | Distance from the depot (km) | from the route source; editable only for typed (and on the map) | from source | AUTO / USER | `wp_s` | Locked for VECTO cycles and GPS. |
| `stop.time` | Stop time (min or s → s) | from the route source; editable for VECTO, typed, map | from source | DEF | `wp_stop`, `stop` in `payload_engine` and `pto_engine` | Locked for GPS. When stop PTO is on, the parser adds the PTO duration to the standing time (see `pto.standing_rule`). |
| `stop.payload` | Payload after this stop (t → kg) | only when payload shape = per stop | none | REQ in that shape | `payload_custom` | One value per stop plus the start value. |
| `stop.payload_changes` | Payload changes at this stop (yes/no) | tick box | yes | DEF | the parser passes a cleaned copy of `stop` to `payload_engine` | A stop switched off for payload stays a stop for driving. UrbanDelivery has 104 stops with a median of 15 s, so this is needed. |
| `stop.pto_on` | PTO works at this stop (yes/no) | tick box; pre-filled from the `<PTO>` column of a VECTO cycle | off | DEF | `is_on` in `pto_engine` | The depot (row 0) is always off. A 0-second marker row may be "on" only when there is a drive part. |
| `stop.charger` | A charger is available at this stop | tick box | off | OPT | opportunity charging | `OPEN`: `charger_available` has no producer yet. |

Editability by source is in tree A2. An edited VECTO cycle becomes a "user route". GPS allows payload and PTO edits only.

## B4. Payload (tree T4)

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `pl.shape` | How the load changes | (a) constant; (b) linear from start to end, equal change at every stop; (c) per stop | constant (the sensible default for VECTO cycles) | DEF | `shape` = `"constant"` / `"linear"` / `"custom"` | Any shape is allowed for any route source (decided 8 Oct). Linear needs at least one stop. The equal step in linear is an HDEV assumption with no source. |
| `pl.basis` | Which payload value | (a) VECTO reference payload for group + mission [STD]; (b) VECTO low payload [STD]; (c) maximum payload = GVW − curb − body/trailer; (d) reference run with a max-payload run beside it; (e) own value | **OPEN** (7 Oct said VECTO reference; reopened since) | DEF | `payload_start` | VECTO reference payloads, kg (low / reference): group 4 LH 1,900 / 14,000, RD and UD 900 / 4,400, MU 600 / 3,000; group 5 LH 2,600 / 19,300, RD and UD 2,600 / 12,900; group 9 LH 2,600 / 19,300, RD 1,400 / 7,100, MU 1,200 / 6,000; groups 1–3 and 51–56 come from GVW through `Payloads.csv`. |
| `pl.start` | Payload when leaving (t → kg) | from `pl.basis`, or typed | from `pl.basis` | DEF | `payload_start` | |
| `pl.end` | Payload at the end (t → kg) | typed | none | REQ when shape = linear | `payload_end` | Closed for constant and per stop. Parser: linear without an end value → clear error. |
| `pl.custom` | Payload after each stop (t → kg) | typed in the stop table, or pasted | none | REQ when shape = per stop | `payload_custom` (start value + one per stop) | Parser: length = number of payload stops + 1; no NaN. |
| `pl.profile` | Saved payload profile | pick from the library, "save as" | none | OPT | all of the above | Assigned per fleet row. |

**Checks (parser, decided):** 0 ≤ payload ≤ GVW − curb mass − body/trailer mass at every stop. On failure: an error that names the stop and suggests the next vehicle class up. Tonnes are converted to kg in the parser. Later, in the battery step, a bigger battery raises curb mass and lowers the maximum payload.

## B5. PTO and body equipment (tree T5)

One scheme covers every kind of body equipment. Everything hangs off the stop rows: a stop flagged "PTO on" can start a **stop part** (while standing) and a **drive part** (from leaving that stop until the next stop). Equipment that is always on is a third, separate part.

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `pto.use` | Does the body use power? | no / yes | no | DEF | opens the rest | |
| `pto.stop_kind` | Stop part: how the power is given | (a) none; (b) one number; (c) profile | none | OPT | | A number and a profile exclude each other. |
| `pto.stop_w` | Stop power (kW → W) | typed | none | REQ in (b) | placed by `consumption_engine` on all standing rows of each flagged stop | A constant skips `pto_engine`. `PLANNED`: the slot for constants in `consumption_engine` is not written yet. |
| `pto.stop_profile` | Stop profile (time s, power kW → W) | (a) VECTO refuse profile `MunicipalUtility_PTO_generic.vptoel`: 23 s, 8.42 / 33.69 / 25.92 kW, 0.14993 kWh per stop [STD]; (b) library profile [LIB]; (c) own table or upload [USER] | none; (a) is the only official default | REQ in (c) | `stop_pto_t`, `stop_pto_w` | Times: whole seconds, strictly increasing, finite. Power ≥ 0. Each value is held until the next time point; the last row only marks the end. "No profile" = one point. Half-second profiles (Ban & Stipetić) need resampling first: **OPEN** whether the library or `pto_engine` does it. The same profile plays at every flagged stop. |
| `pto.stop_eff` | Stop PTO efficiency | typed | 1.0 (= the value is already electric, as in VECTO) | DEF | `stop_pto_eff` | Must be in (0, 1]. Electric W = entered W ÷ efficiency. |
| `pto.standing_rule` | Standing time at a PTO stop | (a) VECTO: stop time + PTO duration; (b) "use stop time as PTO time": max(stop, PTO) | (a) | DEF | changes `wp_stop` before the driver runs | (b) is non-VECTO and non-conservative (about −2 s per Municipal stop) and must be flagged. The parser guarantees no stop is shorter than the profile. |
| `pto.drive_kind` | Drive part: how the power is given | (a) none; (b) one number until the next stop (sweeper); (c) profile played once | none | OPT | | |
| `pto.drive_w` | Drive power (kW → W) | typed | none; no sourced default exists | REQ in (b) | placed by `consumption_engine` on moving rows | One sweeping power for the whole route (a flagged deviation from VECTO). |
| `pto.drive_profile` | Drive profile (time s, power kW → W) | library / own | none | REQ in (c) | `drive_pto_t`, `drive_pto_w` | Starts on the first moving row after the stop. Keeps running through the next stop (VECTO behaviour). A new drive part while one still runs → error (VECTO throws). |
| `pto.drive_eff` | Drive PTO efficiency | typed | 1.0 | DEF | `drive_pto_eff` | Stays 1.0 by decision; the next input decides where the power is added. |
| `pto.own_motor` | Does the body have its own electric motor? | yes / no | none | REQ when a drive part exists | routing inside `consumption_engine` | Yes → added straight to battery power. No → added at the traction motor shaft, so motor losses apply. Decided 12 Nov, to build. Not included in method C for now (16 Nov). |
| `pto.always_w` | Equipment that is always on (W) | (a) one number; (b) a value per hour (needed later for the fridge model) | 0 | OPT | `PTO_always_on` in `P_aux` | |
| `pto.always_eff` | Its efficiency | typed | 1.0 | DEF | `PTO_eff` in `P_aux` | |
| `pto.fridge` | Fridge / TRU model | ATP K value from the certificate, or the class limit (IN 0.70, IR 0.40 W/m²K, flagged); inner and outer box size; set temperature; COP (no default); heating when outside is colder than the set temperature | none | OPT | would produce `PTO_always_on` per hour | `PARKED`. Results in urban use labelled a lower bound (no door openings). |
| `pto.mech_type` | Mechanical PTO type on the gearbox | 12 rows of VECTO `PTO-tech.csv` (None; one engaged gearwheel above oil level; shift claw / multi-disc clutch / multi-disc clutch + oil pump, for one shaft, up to 2 gear wheels, more than 2 gear wheels; additional gearmesh without disconnect clutch) | None | OPT | a constant drag torque at the motor shaft | `PARKED` until Bob's VECTO run 2. Until then, a declared mechanical PTO gives a warning "transmission drag not modelled". |
| `pto.profile_lib` | Saved PTO profile | pick, "save as" | none | OPT | all of the above | Simple option = one constant or the VECTO template. Advanced = create or upload a profile; it then appears in the same dropdown. Every library entry needs a source, a tag (measured / simulated / approximated / rating), a licence note, and the side it describes (shaft or electric). |

## B6. Aerodynamics (tree T6)

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `aero.cdxa0` | Air drag area at zero yaw, CdxA0 (m²) | (a) OEM declared value (constant-speed test, Reg. 2017/2400 Annex VIII); (b) library: only a range code A1–A24 is public, so a value inside the range; (c) VECTO standard value `CdxA_Default` for the group; (d) Construction mission: `CdxA_Construction` (VECTO replaces the declared value) | (c): group 1, 1s 7.1; 2 7.2; 3 7.4; 4 8.4; 5 8.7; 9 8.5; 10 8.8; 11 8.5; 12 8.8; 16 9.0; medium rigid 5.8; van 2.5 m² [STD `SegmentTable.csv`] | DEF | `CdxA0` in `consumption_engine`; reference `cdxa` table for `driver_model` | The parser adds the trailer ΔCdxA **before** the crosswind correction for a rigid truck pulling a trailer (T1 1.3, T2 1.5, EMS ST1 2.1 m²). Tractors: the declared value already includes the standard semitrailer. The A1–A24 bin edges are not in EEA or the regulation: **OPEN, Bob to fetch**. The `CdxA_Default` values should be verified against Annex VIII Appendix 7 before client use (noted 7 Oct). |
| `aero.yaw_set` | Crosswind coefficient set | (a) VECTO set for group + mission [STD `VCDV_parameters.csv`]: RigidSolo (0.013526, 0.017746, −0.000666), RigidTrailer (0.017125, 0.072275, −0.004148), TractorSemitrailer (0.030042, 0.040817, −0.00213), MediumLorriesRigid (−0.0015, 0.0086, −0.00029), MediumLorriesVan (0.0032, 0.00532, −0.00028), CoachBus (−0.000794, 0.02109, −0.00109); (b) own a1, a2, a3; (c) own CdxA-vs-yaw table | (a) | DEF | `a1`, `a2`, `a3` in `crosswind_engine` | Which set: e.g. group 5 long haul → TractorSemitrailer; group 4, 9, 11, 16 long haul → RigidTrailer, other missions → RigidSolo. (c) has no agreed upload format: **OPEN**. |
| `aero.coastdown` | Coast-down coefficients A, B, C | typed (OEM) | none | OPT | would replace Crr and CdxA | `PARKED` 12 Nov. Effect on the E2 was +0.12 % / +0.05 %. |

## B7. Tyres and wheels (tree T7)

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `tyre.crr` | Rolling resistance (N/kN in the UI → dimensionless) | (a) library: certified RRC per axle (EEA `axle` table, `SpecificRRC`, with `Twintyres`); (b) EU tyre label class per axle; (c) one typed value; (d) VECTO standard value | (d) is **OPEN**: no document says which standard value the parser uses | DEF | `Crr` in `driver_model`, `coast_distance`, `force_engine` (always the same number) | The number passed is `Crr_eff`: per-axle RRC combined with the axle load shares for the mission (`SegmentTable.csv`) and the trailer axles from VECTO mission data. It reproduces VECTO's per-axle rolling resistance. Where this combination is computed (the harness has `crr_eff()`) must follow the rule "calculations in the engine": **check when the parser is written**. |
| `tyre.beta` | Mass exponent in rolling resistance | 0.9 (VECTO) or 1.0 (linear) | 0.9 [STD VECTO `Physics.cs`] | CONST | `beta` in `driver_model`, `coast_distance`, `consumption_engine` | Same value everywhere (decided 10 Nov). 1.0 reduces to the simple equation. |
| `tyre.size` | Tyre size | (a) library (`TyreDimension` per axle); (b) pick from VECTO `Wheels.csv` (130 sizes); (c) typed radius | none | REQ | `r_dyn` (m) in `force_engine`; wheel inertia | `Wheels.csv` gives diameter and inertia per size. `r_dyn = 0` must be rejected. |
| `tyre.theta_red` | Inertia of the wheels (kg·m²) | (a) from tyre size and number of wheels incl. trailer [STD `Wheels.csv`]; (b) typed; (c) 0 | 0 = no rotating mass | DEF | `theta_red` in `force_engine`; `m_red_wheels` (kg) in `driver_model` | The two must describe the same wheels: `m_red_wheels = theta_red / r_dyn²`. Who computes it is **OPEN** (Bob corrected on 12 Nov that he never decided the parser does). Negative or NaN must be rejected. |
| `tyre.load_index` | Tyre load index | library / typed | none | OPT | picks the cold-tyre factor | `PLANNED`. |
| `tyre.cold` | Cold-tyre correction | off / on | off | OPT | rolling resistance × 1 / (1 + Kt·(T − 25)), Kt 0.006 if load index > 121, else 0.010 (ISO 28580, used outside its 20–30 °C range) | `PLANNED, OPEN`. Needs no new user input beyond the load index. Largest open item for "do not underestimate": +6 % to +19 % wheel energy at +10 to −10 °C in one model study. |
| `tyre.road` | Wet, snow or ice | off / from DMI precipitation | off | OPT | rolling resistance factor | `PLANNED, OPEN`. No agreed mapping from rain or snow to a factor. |

## B8. Drivetrain (tree T8)

The four ways in are exclusive. The engine has two paths only: **method C** (three numbers) and **maps** (`drivetrain()`).

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `drv.method` | How losses are given | (A) method C from the library; (B) method C typed; (C) three efficiencies + regen efficiency; (D) full loss-map set | (A) | DEF | picks the path in `consumption_engine` step 6 | Partial maps → error. No silent fallback. Decided 16 Nov. |
| `drv.drive_eff` | Drive efficiency | library (fitted on EEA certified results per truck); typed; or motor × inverter × gearbox multiplied by the parser | per truck from the library. For a class without a truck: **OPEN** | REQ in A–C | `drive_eff` | Electric power = mechanical power ÷ `drive_eff` while pushing. The old placeholders 0.95 / 0.95 / 0.98 have no source and gave about −32 % on Regional. The fitted numbers are "HDEV numbers": they must be refitted when the engine changes. |
| `drv.regen_eff` | Regeneration efficiency | library; typed | per truck from the library | REQ in A–C | `regen_eff` | Electric power recovered = mechanical × `regen_eff` while braking. |
| `drv.drag_n` | Constant drivetrain drag at the wheel (N) | library; typed; 0 in branch (C) | per truck from the library | REQ in A–B | `drivetrain_drag_N` | Added before the efficiencies: `Pw = P_wheel + drivetrain_drag_N · v_avg`. |
| `drv.regen_cap` | Largest regeneration power (kW → W) | (a) rated motor power from the library (`em_rated_kw_total`; IEPC rated power for IEPC trucks); (b) typed | (a). Assumption: one number stands in for VECTO's generation curve | REQ | `P_regen_max` | Applied on the mechanical side, before `regen_eff`. No longer optional (16 Nov). |
| `drv.drive_limit` | Largest drive power (kW → W) | rated or peak motor power | **OPEN: rated or peak** | REQ | `P_drive_max` | Not a clip. Rows above it are counted (rows, peak W, kWh above). Too many → rerun the driver at the exact mass. |
| `drv.v_no_regen` | No regeneration below (km/h → m/s) | constant | 5 km/h [STD VECTO `Constants.cs`] | CONST | `v_no_regen` | Tested on start-of-step speed with `<=`, only when power is negative. |
| `drv.p_max` | Motor power for the driver (kW → W) | rated power from library or spec sheet; none | none = no cap | OPT | `P_max` in `driver_model` | Flagged HDEV simplification: VECTO uses the full-load torque curve. Only acts when coasting is on. To revisit. |
| `drv.drag_table` | Coasting drag for the driver (speed m/s, force N) | (a) VECTO E2 drag table for every truck; (b) built from the user's own drivetrain data; (c) zero | (a), decided 3 Nov | DEF | `drag_v`, `drag_F` in `driver_model` and `coast_distance` | Must be passed as lists or tuples, never plain numbers. Whether the library's fitted `drv.drag_n` should also feed this table is not written anywhere: **OPEN**. |
| `drv.j_rotor` | Rotor inertia (kg·m²) | OEM value (certification `RotationalInertia`); 0 | 0 (neutral). No fleet default exists | DEF | `J_rotor` in `force_engine` | The parser must always pass it. For method C it is taken as 0 for EEA trucks (absorbed by the fit; an assumption not explicitly confirmed by Bob). |
| `drv.i_total` | Total ratio motor → wheel | one number; one value per row (from gears); 1 | 1 (neutral) | DEF | `i_total` in `force_engine` | Rule when the gear is unknown: 12 Nov said lowest gear; the 14–16 Nov closeout dropped it (+46 % to +71 % wrong). **OPEN** ("highest gear that can manage" was proposed). |
| `drv.vacc` | Acceleration and braking limits | (a) VECTO `Truck.vacc`: speed 0 / 25 / 50 / 60 / 120 km/h → acceleration 1 / 1 / 0.643 / 0.5 / 0.5 m/s², deceleration −1 / −1 / −1 / −0.5 / −0.5 m/s² [STD]; (b) own curve | (a) for all trucks | DEF | `vacc_v`, `vacc_acc`, `vacc_dec` in `driver_model` | Parser: speeds increasing, decelerations < 0, km/h → m/s. Engineering view only. |
| **Map set (branch D only)** | | | | | | |
| `drv.map_axle` | Axle ratio + axle loss map | OEM file | none | REQ in D | `i_axle`, `axle_map` in `drivetrain()` | VECTO `.vtlm` files go through the reader `vecto_loss_map()` first. |
| `drv.map_gear` | Gear ratios + one loss map per gear | OEM files | none | REQ in D | `i_gears`, `gear_maps` | |
| `drv.adc` | Motor's own gear (ADC): ratio, efficiency | OEM | efficiency 1.0 in VECTO declaration | REQ in D | `i_adc`, `eta_adc` | |
| `drv.map_motor` | Number of motors, motor map, drive and generation limit curves | OEM files | none | REQ in D | `n_em`, `em_map`, `em_T_drive`, `em_T_gen` | The generation curve is the regen cap in this path. Points outside a map use the nearest map point and are counted. |
| `drv.gear_row` | Gear per row | from a gear rule | **OPEN** | REQ in D | `gear` | Gear 0 = motor not connected. |
| `drv.pto_mech` | Mechanical drive PTO power per row | from `pto.*` when the body has no own motor | 0 | DEF | `P_pto_mech` | |

## B9. On-board systems (tree T9)

All of these end in `P_aux`. The rule for every one: **a VECTO table row, or an own value**. The factors are VECTO's and are kept as they are.

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `aux.es` | Electric system (W) | (a) VECTO technology, by mission [STD `ES-Tech.csv`]: "Standard technology" 1,714.29 W long haul, 1,428.57 W other missions; "Standard technology - LED headlights, all" 1,642.86 / 1,357.14 W; (b) own W | (a) Standard technology | DEF | `ES_power` | The table value × 0.7 = electric W (1,428.57 × 0.7 = 1,000 W matches VECTO). |
| `aux.es_eff` | ES factor | typed | 0.7 [STD VECTO alternator efficiency] | DEF | `ES_alteff` | **UI label needed:** "0.7 = VECTO; set 1.0 if your value is already electric". Otherwise an own electric value is cut by 30 % silently. |
| `aux.ps` | Air system (W) | (a) VECTO technology, electric rows only [STD `PS-Table.csv`]: Small, Medium Supply 1-stage, Medium Supply 2-stage, Large Supply (each with or without AMS) and Vacuum pump, all "+ elec. driven"; (b) own W | VECTO row for the mission | DEF | `PS_power` | Which column the parser reads for a BEV (mission column or the `_el` column) must be checked against VECTO when the parser is written. The E2 comparison used "Vacuum pump + elec. driven". |
| `aux.ps_eff` | PS factor | typed | 1.0 | DEF | `PS_alteff` | |
| `aux.sp_mode` | Steering power: how | (a) VECTO method; (b) own W | (a) | DEF | | (b) closes the two inputs below and skips `SP_power_helper`. |
| `aux.sp_axles` | Number of steered axles | 1 to 4; library | from the axle layout | DEF | rows of `SP_axle_shares` [STD `SP-Axles.csv`: 1 axle 100/100/100, 2 axles 100/70/70, 3 and 4 axles 100/50/50 %] | Baseline by group and mission from `SP-Table.csv`, e.g. group 5 regional 540 / 90 / 40 W (unloaded friction / banking / steering). |
| `aux.sp_tech` | Steering technology | one dropdown applied to all steered axles (decided 15 Oct). BEV rows: "Electric driven pump" (0.857, 0.857, 0.857), "Full electric steering gear" (0, 0.143, 1.429); or own factors | none stated | DEF | `SP_tech_factors` [STD `SP-Tech.csv`] | The library has the technology label per axle. The result of the helper is mechanical W. |
| `aux.sp_eff` | SP factor | typed | 0.7 | DEF | `SP_alteff` | Same label rule as ES. Steering is on only while the truck moves. |
| `aux.cond` | Motor and battery conditioning (W) | (a) VECTO by mission [STD `Cond-Table.csv`]: 600 / 600 / 550 / 550 / 600 W for long haul / regional / urban / municipal / construction; (b) own W; (c) thermal model | (a) | DEF | `cond_power` | (c) is `PLANNED`. Timing rule today: on while moving or while PTO works. VECTO: on when a motor or the electric PTO is on, off when standing and when coasting. Kiro recommends keeping the HDEV rule (effect 0.012–0.090 % of trip energy). Under review in step 7. |
| `aux.cond_eff` | Cond factor | typed | 1.0 | DEF | `cond_eff` | |
| `aux.depot_rule` | Aux power during depot charging | fixed rule | none drawn (decided 13 Oct) | CONST | charging stage | Battery conditioning during charging is a planned hook. |

## B10. Schedule and calendar (tree T10)

Status: `DESIGNED` (12 Oct, 14–15 Nov). `src/resolver/calendar.py` is a Kiro draft.

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `sch.out` / `sch.back` | Leaves the depot / back at the depot (hh:mm) | typed | none | REQ | `t_start`; charging session arrival and departure | The return time is also a result (the driver model gives the trip duration). If both are given, which wins is not written: **OPEN**. Earlier rule for typed routes: speed wins over end time. |
| `sch.days` | Working days Mon–Sun | toggles | none | REQ | list of operating dates | Every operating date is simulated directly (decided 12 Oct). |
| `sch.holidays` | Public holidays | (a) Danish holidays, computed from Easter; Store Bededag is not a holiday from 2024; Grundlovsdag and 24 Dec are optional switches because they are not statutory; (b) own dates; (c) none | caller decides; flagged as an assumption | DEF | operating dates | |
| `sch.shutdown` | Shutdown periods | date ranges | none | OPT | operating dates | `PLANNED`. |
| `sch.exceptions` | Exceptions by date | table: date, other route, other times | none | OPT | operating dates | |
| `sch.shifts` | Shifts per day | one / several | one | DEF | sessions between shifts | `PLANNED`. A second shift is a second trip on the same truck on the same date. |
| `sch.season` | Seasonal route | a second fleet row with its own date range | none | OPT | assignments | How calendar cases are entered (2 days a week, a winter route, two shifts, 20 identical trucks) is on Bob's data-flow page. |
| `sch.reduced` | Reduced days (e.g. Saturday at half) | % per weekday | none | OPT | | `PLANNED`. |
| `sch.oncall` | Emergency and on-call vehicles | call-out logs through the AI reader | none | OPT | | `OPEN`: how they are entered. |
| `fleet.count` | Number of identical vehicles in the row | typed | none | REQ | assignments (`count`); depot sizing; cost | Also a scenario lever. Identical rows reuse one driver run. |

## B11. Weather (tree T11)

Weather is stored server side and refreshed as needed. A project only picks from the stored data (decided 14 Nov).

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `wx.source` | Where weather comes from | (A) stored DMI data; (B) own weather file; (C) VECTO declaration weather | (A) | DEF | picks the reader | (C) is the "VECTO-equivalent case": one cycle, 3 m/s at 4 m, 1.188 kg/m³, constant reference payload. It must reproduce VECTO. |
| `wx.location` | Location | depot address, place, or map pick | the depot address | REQ in (A) | station lookup | Whether GPS coordinates of a route should pick the station is **OPEN**. |
| `wx.station` | Weather station | auto: nearest DMI station with a full year, chosen per parameter; changeable | auto [EXT] | AUTO | `T_amb_h`, solar, wind | |
| `wx.years` | Weather year(s) | one year / several years | none: default year **OPEN** | REQ in (A) | date-paired hourly series | Rules (decided 6 Oct): never average the same date across years; keep each real year paired by date; several years give the spread (P50 / P90). Also a scenario lever. |
| `wx.detail` | Level of detail | hourly / mean over drive hours / daily mean | hourly is what the code does | DEF | how `T_amb_h` is filled | Same function, different data. Whether the two coarser options stay is **OPEN**. |
| `wx.shift` | Shift every temperature by (K) | typed | 0 | DEF | `T_amb_h` | Sensitivity lever. |
| `wx.worst_day` | Run the worst day as its own case | toggle | off in the 13 Nov inventory | DEF | a separate sizing case | The 6 Oct rule says the worst day is always kept as its own sizing case. Whether that makes this toggle unnecessary for sizing runs is for Bob to say. |
| `wx.t_amb` | Outside temperature per hour (°C → K) | from the source | n/a | AUTO | `T_amb_h` in `consumption_engine`; `T_amb` in `HVAC_thermal` | Parser fills gaps (a NaN hour would silently give 0 W HVAC) and rejects values below about 150 K (°C passed by mistake). DMI stamps the end of the hour. |
| `wx.solar` | Sun per hour (W/m²) | from the source | n/a | AUTO | `solar` in `HVAC_thermal` | Whether VECTO's `solar` equals DMI global radiation is unverified (flag). |
| `wx.wind` | Wind speed (m/s) and its height | (a) DMI hourly wind at 10 m; (b) one mean value: 5.028 m/s at 10 m (DMI, earlier decision); (c) VECTO: 3 m/s at 4 m | (a) in the notebook; (b) in the 13 Nov inventory | DEF | `v_ref`, `h_ref` in `crosswind_engine` | The notebook indexes the crosswind table by weather hour, so (a) is what the code does. The two documents disagree: see Part G. |
| `wx.p_air` | Air pressure (Pa) | (a) fixed 101,325; (b) from route altitude (ISO 2533 formula); (c) DMI hourly | (a) | DEF | `p_air` in `consumption_engine` | (b) and (c) **OPEN**. |
| `wx.rho_mode` | Air density | (a) from temperature and pressure per row (HDEV); (b) fixed 1.188 kg/m³ (VECTO) | (a) | DEF | air density per row | (b) is a proposed `rho_fixed` argument for VECTO-mode fitting. The driver always uses 1.188 in the reference run. |
| `wx.const` | Crosswind constants | hidden | profile exponent 0.2; reference height 10 m (DMI) or 4 m (VECTO); yaw clamp 10° (HDEV decision, 6 Oct); speed grid 60–130 km/h, no 0 km/h; height step and angle step (the VECTO check used 0.4 m and 1°) | CONST | `wind_exp`, `h_ref`, `beta_limit_deg`, `v_veh_kmh`, `dh`, `dphi_deg` | The 10° clamp must be stated in every report. `beta_limit_deg = None` gives VECTO's behaviour. |

## B12. Cab heating and cooling (tree T12)

Placed with Weather because it is driven by temperature (decided 13–14 Nov).

| ID | Input | Ways to fill it | Default · source | Need | Feeds | Checks and notes |
|---|---|---|---|---|---|---|
| `hv.mode` | How cab climate power is worked out | (A) VECTO constant; (B) own constant W; (C) thermal model | none stated. Bob's stance (22 Oct): connect the thermal model and capture cold weather rather than rely on VECTO's constant | REQ | `HVAC_power` and `HVAC_eff` in `P_aux` | A and B close every thermal input. |
| `hv.const` | VECTO HVAC value | "Default" or "None" for group + mission [STD `HVAC-Table.csv`], e.g. Default: groups 4, 5, 9–12, 16 → 350 W long haul, 200 W regional, 150 W urban, 200 W construction; municipal 300 W (groups 4, 9, 11) | Default | DEF in (A) | `HVAC_power` | × 1.25 (= 1 / 0.8, VECTO `HVACElectricEfficiencyFactor`): 200 W → 250 W electric. Some cells are empty (e.g. municipal for group 12): clear error. |
| `hv.own_w` | Own HVAC power (W) | typed | none | REQ in (B) | `HVAC_power` | Factor 1.25 or 1.0 if already electric (same label rule as ES). |
| `hv.persons` | People in the cab | typed | none | REQ in (C) | `N_persons` | |
| `hv.heater` | Heater set-up | heat pump type (none, or a VECTO type; mechanical heat pumps are rejected for a BEV) + electric heater yes/no + fuel heater yes/no | none | REQ in (C) | picks the columns of the COP and share tables | [STD VECTO `DefaultClimatic.aenv`, `HeatingDistribution.csv`] |
| `hv.cop` | COP and heat-share tables | (a) VECTO tables at the 8 VECTO temperatures; (b) own table (OEM) | (a) | DEF in (C) | `T_points`, `cop_heat_points`, `cop_cool_points`, `hp_share_points`, `eh_share_points`, `fuel_share_points` | One temperature axis for all (decided 13 Nov). A missing heat-pump COP (below −5 °C for non-R-744) is filled by the parser with the nearest value and flagged as optimistic. Parser: COP > 0, shares in [0, 1] and sum ≤ 1, points unique and ascending. |
| `hv.setpoints` | Set-points: heat / cool / cooling off (°C → K) | typed | 18 / 23 / 17 °C [STD VECTO] | DEF in (C) | `T_heat`, `T_cool`, `T_cool_off` | 21–22 °C is what tests used (Mercedes, Chalmers); that raises annual HVAC energy by 26–38 %. Parser: `T_cool ≥ T_heat`. |
| `hv.cab` | Cab data: wall area (m²), U (W/m²K), window area (m²), volume (m³) | (a) OEM values; (b) cab-type template | **no sourced truck default exists**. Placeholder used in tests: 20 m² × 3.0 W/m²K = 60 W/K, inside the NREL measured range 51–65 W/K for a parked US sleeper cab | REQ in (C) | `A_surface`, `U`, `A_window`, `cab_volume` | Missing → red, Run blocked. (b) is `PROPOSED`: there are no sourced template values yet. |
| `hv.pmax` | Largest heating and cooling power (W) | OEM value | missing → no limit (`np.inf`), flagged | DEF in (C) | `max_heating_power`, `max_cooling_power` | |
| `hv.vent` | Ventilation rate, and while heating (per hour in the UI → 1/s) | OEM value | none | REQ in (C) | `vent_rate`, `vent_rate_heating` | |
| `hv.q` | Fresh air (m³/h → m³/s) | typed | 100 m³/h for 2 persons (Dvorak et al. preprint, Eq. 2: 102.4 m³/h at 1,000 ppm CO₂). 0 = exactly VECTO | DEF in (C) | `Q` | Non-VECTO, flagged: +55 % HVAC energy at 100 m³/h. |
| `hv.const_therm` | Thermal constants | hidden | heater efficiency 0.93; ventilation power 0.56 Wh/m³; heat per person (50, 80) W; clouding (0.65, 0.8); boundary 17 °C; window transmission 0.95; solar factor 0.25; waste heat 0 W (HDEV, conservative); pressure 101,325 Pa; gas constant 287.05 J/kgK; cp 1,005 J/kgK (**no source read yet**) | CONST | `eh_eff`, `spec_vent_power`, `heat_per_person`, `clouding`, `T_boundary`, `g`, `solar_factor`, `waste_heat`, `p`, `R`, `cp` | All temperatures are in kelvin inside the engine. The parser converts every one with the same +273.15. |
| `hv.eff` | HVAC factor into `P_aux` | automatic | 1.25 in A (and B unless electric); **1.0 in C** | AUTO | `HVAC_eff` | If C runs with 1.25 the result is 25 % too high. The parser sets it; it is not a user field in C. |

---

# PART C. Every function, from the engine's side (written functions)

Signatures are copied from Bob's notebook `HDEV_NEW (7).ipynb` (16 Nov). For each function: what it does, how often it runs, every argument with the input ID from Part B that fills it, and every output with where it goes and whether the user sees it.

"Default" in these tables means the value `defaults.py` should hold. Some defaults are still written in the function signature in the notebook; the 13 Nov rule is that they move to `defaults.py`.

## C0. Call order and how often each function runs

| # | Function | Status | Runs | Reruns when this changes |
|---|---|---|---|---|
| E1 | `payload_engine` | FINAL | once per fleet row (route × payload template) | stop table, payload shape or values |
| E2 | `pto_engine` | FINAL | once per fleet row (route × PTO template) | stop table, PTO flags, profiles, efficiencies |
| E3 | `crosswind_engine` | FINAL | once per vehicle and weather set, plus once at VECTO wind for the driver's reference table | vehicle height, yaw coefficients, wind data |
| E4 | `driver_model` (+ `interp1`, `decel_distance`, `coast_distance`) | FINAL | once per route × vehicle (reused for identical rows); a final pass at exact mass for a chosen truck | waypoints, stop times, reference vehicle, drag table |
| E5 | `force_engine` | FINAL | once per driver run | driver rows, Crr, wheel data, rotor data |
| E6 | `SP_power_helper` | FINAL | once per vehicle (VECTO steering mode only) | group, mission, steered axles, technology |
| E7 | `HVAC_thermal` (+ `ssm_total_w`, `climate_lookup`) | FINAL | once per weather year (hourly array), thermal mode only | weather, cab data, heater, set-points |
| E8 | `P_aux` | FINAL | once per vehicle (per hour for HVAC in thermal mode) | any aux value or factor |
| E9 | `consumption_engine` | WIP | once per vehicle × operating date | anything above, payload, weather of the date, drivetrain numbers |
| E9b | `drivetrain` (+ reader `vecto_loss_map`) | written, tested by Kiro (Gate 2); used only on the map path | inside E9 step 6 | maps, gear per row |

Row check between E6 and E7 (`check_rows`) and the result object are on Bob's data-flow page and are not repeated here.

---

## C1. `crosswind_engine` (FINAL)

**What it does.** Pure physics. For each wind speed and each vehicle speed it works out two numbers: `W1` (how much more air hits the truck than in still air) and `W2` (the extra drag area in m² from the air arriving at an angle). The effective drag area is then `CdxA_eff = CdxA0 · W1 + W2`. CdxA0 itself is not an input here.

```python
crosswind_engine(vehicle_height, v_ref, h_ref, a1, a2, a3, wind_exp, dh, dphi_deg, v_veh_kmh, beta_limit_deg)
```

| Argument | Unit | Filled from | Default | Notes |
|---|---|---|---|---|
| `vehicle_height` | m | `veh.height` | VECTO reference height by group | Sets how many height slices the wind profile is averaged over. |
| `v_ref` | m/s, one number or a list | `wx.wind` | DMI hourly wind (list, one per weather hour) for the consumption run; 3 m/s for the driver's reference table | A list gives one table row per wind value. |
| `h_ref` | m | `wx.const` | 10 m for DMI wind; 4 m for VECTO wind | Height at which `v_ref` was measured. |
| `a1`, `a2`, `a3` | m²/deg, m²/deg², m²/deg³ | `aero.yaw_set` | VECTO set by group + mission | Extra drag area as a cubic in yaw angle. |
| `wind_exp` | – | `wx.const` | 0.2 | How wind grows with height. |
| `dh` | m | `wx.const` | 0.4 m in the VECTO check | Height of one slice. |
| `dphi_deg` | degrees | `wx.const` | 1° in the VECTO check | Step in wind direction, 0–360°. |
| `v_veh_kmh` | km/h, list | `wx.const` | grid 60–130 km/h, never 0 | The only engine argument left in km/h (the function is final). Below 60 km/h the 60 value is held, like VECTO. |
| `beta_limit_deg` | degrees or `None` | `wx.const` | 10 | HDEV decision of 6 Oct: yaw is clamped at 10° and the extra drag held there, because VECTO's polynomial is only valid to that range. `None` = no clamp. |

| Output | Shape | Meaning | Goes to | User sees |
|---|---|---|---|---|
| `W1` | wind values × speed grid | air-speed ratio, dimensionless | `consumption_engine` (`W1`); parser builds the driver's reference `cdxa` table from the VECTO-wind run | no |
| `W2` | wind values × speed grid | extra drag area, m² | same | no |

**User-facing result built from it:** effective drag area by speed and wind, and the share of energy that goes to air drag (energy balance). **Report flags:** 10° yaw clamp (every report); wind taken at 10 m from DMI instead of VECTO's 3 m/s at 4 m; rectangle-rule averaging over height slices.

## C2. `payload_engine` (FINAL)

**What it does.** Pure logic on waypoints. It writes the payload on the start row and on each stop row, and leaves every other row blank (NaN). `consumption_engine` later carries each value forward by distance. It does not care where the waypoints came from.

```python
payload_engine(stop, shape, payload_start, payload_end=None, payload_custom=None)
```

| Argument | Unit | Filled from | Default | Notes |
|---|---|---|---|---|
| `stop` | s, one per waypoint | `stop.time`, cleaned by `stop.payload_changes` | from the route | Row 0 is the depot: its stop is never a payload change. A stop the user switched off for payload is passed as 0 in this copy only. |
| `shape` | text | `pl.shape` | `"constant"` | `"constant"`, `"linear"`, `"custom"`. Anything else raises. |
| `payload_start` | kg | `pl.start` (from `pl.basis`) | VECTO reference payload (default basis **OPEN**) | |
| `payload_end` | kg | `pl.end` | none | Used only by `"linear"`. |
| `payload_custom` | kg, list | `pl.custom` / `stop.payload` | none | Used only by `"custom"`. Length = number of stops + 1. |

| Output | Shape | Meaning | Goes to | User sees |
|---|---|---|---|---|
| `payload` (`payload_wp`) | one per waypoint, NaN except start and stops | payload after each stop, kg | `consumption_engine` (`payload_wp`) | yes, as the payload column of the stop table and as a payload-along-the-route picture on the Overview (Bob asked for this on 28 Oct) |

**Raises inside the engine (guards only):** linear with no stops; wrong custom length; unknown shape; negative payload. All friendly checks are in the parser (B4).
**Report flags:** equal payload step per stop in linear is an HDEV assumption; payload changes on arrival at the stop.

## C3. `pto_engine` (FINAL)

**What it does.** Turns the stop and drive profiles into one power value per second, and works out where inside each flagged stop the stop profile starts (centred, like VECTO).

```python
pto_engine(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff)
```

| Argument | Unit | Filled from | Default | Notes |
|---|---|---|---|---|
| `stop` | s per waypoint | `stop.time` after `pto.standing_rule` | from the route | Final standing time, PTO time already included by the parser. |
| `is_on` | 0 / 1 per waypoint | `stop.pto_on` | 0 | Row 0 is forced to 0. |
| `stop_pto_t`, `stop_pto_w` | s, W | `pto.stop_profile` | one point = no profile | Left-hold: each value lasts until the next time. |
| `drive_pto_t`, `drive_pto_w` | s, W | `pto.drive_profile` | one point = no profile | |
| `stop_pto_eff` | – | `pto.stop_eff` | 1.0 | Electric W = profile W ÷ efficiency. |
| `drive_pto_eff` | – | `pto.drive_eff` | 1.0 | |

| Output | Shape | Meaning | Goes to | User sees |
|---|---|---|---|---|
| `is_on` | per waypoint | cleaned flags | `consumption_engine` | no |
| `pto_start` | per waypoint, NaN where no stop profile | second inside the stop at which the profile starts = floor((stop − profile length) / 2) | `consumption_engine` | no |
| `stop_1s` | one per second of the stop profile | electric W | `consumption_engine` | as the profile preview in the PTO template *PROPOSED* |
| `drive_1s` | one per second of the drive profile | electric W | `consumption_engine` | same |

**User-facing results built from it:** kWh per stop and per shift for the body, peak kW, PTO share of the day's energy. Planned export: the profile in VECTO's PTO file format (crane/compactor energy sheet).
**Report flags:** PTO centred in the stop, rounded down to a whole second; profiles in whole seconds; same power at every stop; one sweeping power per route; no mechanical PTO drag modelled.

## C4. `driver_model` and its helpers (FINAL, 12 Nov)

**What it does.** VECTO's driver behaviour on fixed 1 s rows. It turns waypoints into a speed trace: accelerate, cruise, coast, brake, stand. With `coast_mass = None` it is pure kinematics. With a reference vehicle it adds look-ahead coasting and overspeed downhill. Driver behaviour is copied from VECTO on purpose, for auditability.

```python
driver_model(wp_s, wp_v, wp_stop, wp_grade,
             vacc_v, vacc_acc, vacc_dec, dt=1.0,
             coast_mass=None, m_red_wheels=0.0, cdxa_v=None, cdxa=None, Crr=None, beta=1.0, rho=1.188, g=9.80665,
             drag_v=(0.0,), drag_F=(0.0,), P_max=None,
             lac_min_v=50.0, lac_dist_factor=10.0, df_offset=2.5, df_scaling=1.5,
             df_vtarget=((0, 48, 52, 100), (0, 0, 1, 1)), df_vdrop=((-100, 9, 11, 100), (1, 1, 0, 0)),
             os_min_v=50.0, os_allowed=2.5, brake_margin=0.1, v_min_coast=5.0)
```

| Argument | Unit | Filled from | Default | Notes |
|---|---|---|---|---|
| `wp_s` | m | route reader (B2) | – | Waypoint distance. |
| `wp_v` | m/s | route reader | – | Target speed. km/h → m/s in the parser. |
| `wp_stop` | s | `stop.time` (+ PTO time) | – | Final standing time. |
| `wp_grade` | % | `rt.grade` | 0 | Turned into altitude inside; the row grade is a secant of altitude. |
| `vacc_v`, `vacc_acc`, `vacc_dec` | m/s, m/s², m/s² | `drv.vacc` | VECTO `Truck.vacc` | |
| `dt` | s | constant | 1.0 | HDEV deviation: VECTO uses variable steps of about 0.5 s. Costs about 1 % on Urban. |
| `coast_mass` | kg or `None` | `veh.ref_mass` (screening) or exact mass (final pass) | reference mass | `None` switches coasting and overspeed off. |
| `m_red_wheels` | kg | `tyre.theta_red` and `tyre.size` | 0 | Wheel inertia as an equivalent mass. |
| `cdxa_v`, `cdxa` | m/s, m² | reference table: `aero.cdxa0 · W1 + W2` at VECTO wind | – | Required when coasting is on. |
| `Crr` | – | `tyre.crr` | – | Required when coasting is on. Same value as in `force_engine`. |
| `beta` | – | `tyre.beta` | 0.9 (signature shows the neutral 1.0) | |
| `rho` | kg/m³ | constant | 1.188 (VECTO) | The driver always uses the reference air density in the screening run. |
| `g` | m/s² | constant | 9.80665 (VECTO) | |
| `drag_v`, `drag_F` | m/s, N | `drv.drag_table` | VECTO E2 table (signature shows zero drag) | Drivetrain drag while rolling with no motor torque. |
| `P_max` | W or `None` | `drv.p_max` | `None` | Caps acceleration by motor power. |
| `lac_min_v` | m/s | constant | 50 km/h | Look-ahead coasting only above this speed. |
| `lac_dist_factor` | m per km/h | constant | 10 | Look-ahead distance = speed in km/h × 10 m (VECTO's rule; the only `3.6` left inside). |
| `df_offset`, `df_scaling` | – | constant | 2.5, 1.5 | VECTO decision-factor constants. |
| `df_vtarget`, `df_vdrop` | km/h tables | constant | as in the signature | VECTO tables, km/h by definition. |
| `os_min_v`, `os_allowed` | m/s | constant | 50 km/h, 2.5 km/h | Overspeed downhill allowed above 50 km/h, by 2.5 km/h. |
| `brake_margin` | m | constant | 0.1 | |
| `v_min_coast` | m/s | constant | 5 km/h | No coasting below this. |

Caution kept from the 12 Nov closeout: the signature still shows the km/h numbers for the four thresholds. The parser must pass m/s, or the defaults change to `50/3.6` and so on (agreed SI edit, not yet pasted back).

| Output | Shape | Meaning | Goes to | User sees |
|---|---|---|---|---|
| `T` | per row | time since departure, s | `consumption_engine` | trip duration, return time |
| `S` | per row | distance, m | `consumption_engine` | distance check |
| `V` | per row | speed at the start of the step, m/s | `force_engine`, `consumption_engine` | speed-over-the-day chart; average, min and max speed (quality check) |
| `A` | per row | acceleration, m/s² | `force_engine` | max acceleration and deceleration (quality check) |
| `grade` | per row | road grade, % | `force_engine` | no |
| `M` | per row | driving mode: 0 standing, 1 accelerating, 2 cruising, 3 coasting, 4 braking | `consumption_engine` | time spent standing, accelerating, cruising, coasting, braking |

**Helpers (no user inputs of their own).**

| Helper | Arguments | Returns | Used by |
|---|---|---|---|
| `interp1(x, xs, ys)` | one number, table x, table y | linear interpolation, end values held | driver loop |
| `decel_distance(v_from, v_to, vacc_v, vacc_dec)` | two speeds, the `.vacc` table | braking distance, m (exact VECTO formula) | driver look-ahead |
| `coast_distance(v, v_target, h_now, h_target, s_now, s_target, coast_mass, m_red_wheels, cdxa_v, cdxa, Crr, beta, rho, g, drag_v, drag_F, df_offset, df_scaling, df_vtarget, df_vdrop)` | current and target speed and height, the reference vehicle, the drag table, VECTO decision factors | look-ahead coasting distance, m | driver look-ahead |

**Report flags (known deviations from VECTO):** fixed 1 s rows; back-to-back stops aim for the next positive target; air drag while coasting is instantaneous; braking that starts mid-step is scaled; `P_max` single power cap; fixed reference vehicle for coasting decisions in screening runs (measured error: Regional −0.39 % to 0.00 %, Urban −1.31 % to +0.68 %, Kiro PR #29). Known gap: rotor inertia is missing in the coasting rows (driver follow-up, not done).

## C5. `force_engine` (FINAL, 12 Nov)

**What it does.** Takes the driver's rows and returns coefficients that do not depend on mass, temperature or wind. Wheel power for any scenario is then one multiply-add per row: `P_wheel = m·k_lin + m^beta·k_roll + k_rot_wheel + rho·CdxA_eff·L`.

```python
force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red, J_rotor, i_total)
```

| Argument | Unit | Filled from | Default | Notes |
|---|---|---|---|---|
| `g` | m/s² | constant | 9.80665 | |
| `Crr` | – | `tyre.crr` | see B7 | |
| `speed`, `accel`, `grade` | m/s, m/s², % | `driver_model` outputs `V`, `A`, `grade` | – | CALC |
| `dt_s` | s | driver `dt` | 1.0 | |
| `r_dyn` | m | `tyre.size` | none | REQ. Must be > 0. |
| `theta_red` | kg·m² | `tyre.theta_red` | 0 | 0 switches wheel inertia off. |
| `J_rotor` | kg·m² | `drv.j_rotor` | 0 | No default in the signature: the parser always passes it. |
| `i_total` | – | `drv.i_total` | 1 | One number or one per row. |

| Output | Unit | Meaning | Goes to | User sees |
|---|---|---|---|---|
| `k_lin` | W/kg | slope + acceleration term per kg | `consumption_engine` | grade and inertia shares of the energy balance |
| `k_roll` | W/kg^beta | rolling term | `consumption_engine` | rolling share |
| `k_rot_wheel` | W | wheel inertia power | `consumption_engine` step 4 (wheel power) | inside inertia |
| `k_rot_rotor` | W | rotor inertia power | `consumption_engine` step 6, motor side. **Not** part of wheel power | inside drivetrain |
| `L` | m³/s³ | exact step average of ½·v³ | `consumption_engine` | air-drag share |
| `v_avg` | m/s | mean speed of the step | `consumption_engine` (CdxA lookup, drag power) | no |

## C6. `SP_power_helper` (FINAL)

**What it does.** VECTO's steering-pump rule. Only called when steering power is taken from the VECTO tables. An own W value skips it.

```python
SP_power_helper(SP_baseline, SP_axle_shares, SP_tech_factors)
```

| Argument | Unit | Filled from | Default | Notes |
|---|---|---|---|---|
| `SP_baseline` | W, three parts | `veh.group` × `veh.mission` → `SP-Table.csv` | by group and mission | Empty cell → parser error. |
| `SP_axle_shares` | %, one row of three per steered axle | `aux.sp_axles` → `SP-Axles.csv` | 1 steered axle | 1 to 4 rows. |
| `SP_tech_factors` | –, one row of three per steered axle | `aux.sp_tech` → `SP-Tech.csv`, or own | BEV rows only | Same number of rows as the shares. A wrong count still gives a number, so the parser must check it. |

| Output | Unit | Meaning | Goes to | User sees |
|---|---|---|---|---|
| return value | W, mechanical | steering power | `SP_power` in `P_aux` (× 0.7 → electric) | steering line in the on-board systems table |

Size on the E2: 3–32 W electric (0.02–0.07 % of trip energy).

## C7. `HVAC_thermal`, `ssm_total_w`, `climate_lookup` (FINAL, 13 Nov)

**What they do.** VECTO's cab heat balance (written for buses) applied hour by hour to a truck cab. `ssm_total_w` is the heat balance at one cab temperature. `climate_lookup` gives the COP and the split between heat pump, electric heater and fuel heater at each outside temperature. `HVAC_thermal` runs the balance at the heating and cooling set-points, decides heating, cooling or ventilation, and returns electric W per hour.

```python
HVAC_thermal(T_amb, solar, A_surface, U, N_persons, A_window, T_points, cop_heat_points, cop_cool_points,
             hp_share_points, eh_share_points, fuel_share_points, max_heating_power, max_cooling_power,
             cab_volume, vent_rate, vent_rate_heating,
             eh_eff, spec_vent_power, heat_per_person, clouding, T_boundary, g, solar_factor,
             waste_heat, T_heat, T_cool, T_cool_off, Q, p, R, cp)
ssm_total_w(T_amb, solar, T_calc, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)
climate_lookup(T_amb, T_points, cop_heat_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points)
```

| Argument | Unit (engine) | Filled from | Default | Notes |
|---|---|---|---|---|
| `T_amb` | K, per weather hour | `wx.t_amb` | – | |
| `solar` | W/m², per hour | `wx.solar` | – | |
| `A_surface`, `U` | m², W/m²K | `hv.cab` | none | REQ in thermal mode. |
| `A_window` | m² | `hv.cab` | none | REQ. |
| `cab_volume` | m³ | `hv.cab` | none | REQ. |
| `N_persons` | – | `hv.persons` | none | REQ. |
| `T_points` | K | `hv.cop` | 8 VECTO temperatures | One axis for COPs and shares. |
| `cop_heat_points`, `cop_cool_points` | – | `hv.cop` (by `hv.heater`) | VECTO | Gaps filled by the parser. |
| `hp_share_points`, `eh_share_points`, `fuel_share_points` | – | `hv.cop` (by `hv.heater`) | VECTO | Nearest temperature point; ties go to the colder one. |
| `max_heating_power`, `max_cooling_power` | W | `hv.pmax` | infinite, flagged | Cap on heat pump + electric heater; cap on cooling. |
| `vent_rate`, `vent_rate_heating` | 1/s | `hv.vent` | none | REQ. |
| `eh_eff` | – | `hv.const_therm` | 0.93 | |
| `spec_vent_power` | J/m³ | `hv.const_therm` | 0.56 Wh/m³ = 2,016 J/m³ | |
| `heat_per_person` | W, two values | `hv.const_therm` | (50, 80) | Below / above `T_boundary`. |
| `clouding` | –, two values | `hv.const_therm` | (0.65, 0.8) | |
| `T_boundary` | K | `hv.const_therm` | 17 °C | |
| `g` | – | `hv.const_therm` | 0.95 | Window transmission (not gravity). |
| `solar_factor` | – | `hv.const_therm` | 0.25 | Kept from VECTO; its meaning is undocumented. |
| `waste_heat` | W | `hv.const_therm` | 0 | HDEV choice, conservative. VECTO credits motor waste heat. |
| `T_heat`, `T_cool`, `T_cool_off` | K | `hv.setpoints` | 18, 23, 17 °C | |
| `Q` | m³/s | `hv.q` | 100 m³/h | 0 = VECTO. The fan moves at least this flow. |
| `p`, `R`, `cp` | Pa, J/kgK, J/kgK | `hv.const_therm` | 101,325; 287.05; 1,005 | cp: no source read yet. |

| Output | Shape | Meaning | Goes to | User sees |
|---|---|---|---|---|
| `HVAC_el` | W per weather hour | heat pump + electric heater + cooling + fan, electric | `HVAC_power` in `P_aux` with `HVAC_eff = 1.0`, then `HVAC` in `consumption_engine` | cab climate kWh per day, month and year; winter against summer; cab options compared (standard value / electric heater / heat pump) |
| `fuel_heat` | W heat per hour | heat delivered by a fuel heater | not used by the battery calculation | no. Flag: "diesel heater fuel not reported". |

**Report flags:** bus method used for a truck cab; hourly weather instead of VECTO's 11 conditions; COP interpolated, shares from the nearest point; COP held below −5 °C (optimistic); fresh air on; fan at least as large as fresh air; 18 °C set-point may understate winter energy; no door openings, no warm-up of a cold cab, no humidity.

## C8. `P_aux` (FINAL)

**What it does.** One line per auxiliary: electric W = entered W × its VECTO factor. Always-on PTO is divided by its efficiency. Works for one number or an array.

```python
P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on,
      ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0)
```

| Argument | Unit | Filled from | Default | Notes |
|---|---|---|---|---|
| `ES_power` | W | `aux.es` | VECTO row for the mission | |
| `PS_power` | W | `aux.ps` | VECTO row for the mission | |
| `HVAC_power` | W, number or per hour | `hv.const` / `hv.own_w` / `HVAC_el` | by `hv.mode` | |
| `SP_power` | W | `SP_power_helper` or own W | VECTO method | |
| `cond_power` | W | `aux.cond` | VECTO by mission | |
| `PTO_always_on` | W, number or per hour | `pto.always_w` | 0 | |
| `ES_alteff` | – | `aux.es_eff` | 0.7 | Multiplies. |
| `PS_alteff` | – | `aux.ps_eff` | 1.0 | Multiplies. |
| `HVAC_eff` | – | `hv.eff` | 1.25; 1.0 in thermal mode | Multiplies. |
| `SP_alteff` | – | `aux.sp_eff` | 0.7 | Multiplies. |
| `cond_eff` | – | `aux.cond_eff` | 1.0 | Multiplies. |
| `PTO_eff` | – | `pto.always_eff` | 1.0 | **Divides.** |

| Output | Unit | Goes to (`consumption_engine` argument) | When it is on | User sees |
|---|---|---|---|---|
| `ES_power` | W electric | `ES` | always | electrical system line |
| `PS_power` | W electric | `PS` | always | air system line |
| `HVAC_power` | W electric | `HVAC` | always (per hour in thermal mode) | cab climate line |
| `SP_power` | W electric | `SP` | only while moving | steering line |
| `cond_power` | W electric | `cond` | while moving or PTO active *(under review)* | conditioning line |
| `PTO_always_on` | W electric | `PTO_always_on` | always | equipment line |

Parser checks: every power ≥ 0, every factor > 0, no NaN or infinity. Verified by Kiro against VECTO for all 68,040 combinations.

## C9. `consumption_engine` (WIP)

**What it does.** Brings everything together per row: mass, weather hour, air density, effective drag area, wheel power, PTO placement, drivetrain and regeneration rules, auxiliaries, battery power, trip energy. Bob is rewriting steps 5–7 now. The input paths below do not depend on how those steps end up.

Signature in the notebook today:

```python
consumption_engine(T, S, V, M, dt,                                      # driver_model rows
                   k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg,   # force_engine
                   m_curb, m_trailer, wp_s, payload_wp, beta,           # masses, payload
                   t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,   # weather + crosswind
                   ES, PS, HVAC, SP, cond, PTO_always_on,               # P_aux outputs
                   is_on, pto_start, stop_1s, drive_1s,                 # pto_engine outputs
                   drive_eff, regen_eff, drivetrain_drag, P_regen_max=None)
```

Agreed changes not yet in the notebook (16 Nov closeouts): `drivetrain_drag` → `drivetrain_drag_N`; add `v_no_regen` and `P_drive_max`; `P_regen_max` becomes required; `m_trailer` holds body + trailer (`m_body_trailer`).

Step order agreed 16 Nov: 1 mass · 2 weather hour · 3 air density and CdxA · 4 wheel power · 5 place PTO · 6 drivetrain and regeneration rules · 7 auxiliaries and battery.

| Argument | Unit | Filled from | Default | Step | Notes |
|---|---|---|---|---|---|
| `T`, `S`, `V`, `M` | s, m, m/s, mode | `driver_model` | – | all | CALC |
| `dt` | s | driver `dt` | 1.0 | 7 | |
| `k_lin`, `k_roll`, `k_rot_wheel`, `L`, `v_avg` | see C5 | `force_engine` | – | 3, 4 | CALC |
| `k_rot_rotor` | W | `force_engine` | – | 6 | Motor side. |
| `m_curb` | kg | `veh.curb_mass` | – | 1 | |
| `m_trailer` (body + trailer) | kg | `veh.body_mass` + `veh.trailer_mass` | VECTO by group and mission | 1 | |
| `wp_s` | m | route reader | – | 1, 5 | Parser: first waypoint = first driver row = 0. |
| `payload_wp` | kg | `payload_engine` | – | 1 | Carried forward by distance. |
| `beta` | – | `tyre.beta` | 0.9 | 4 | |
| `t_start` | s | `rt.depart` / `sch.out` | – | 2 | Offset into the weather array. |
| `T_amb_h` | K per hour | `wx.t_amb` | – | 3 | The `+ 273.15` in the old code goes (temperatures arrive in K). |
| `W1`, `W2` | tables | `crosswind_engine` | – | 3 | One row per weather hour. |
| `cdxa_v` | speed grid | `wx.const` | 60–130 km/h | 3 | Proposed SI fix: grid converted to m/s once in the parser. |
| `CdxA0` | m² | `aero.cdxa0` (+ trailer ΔCdxA) | VECTO standard value | 3 | |
| `p_air`, `R_air` | Pa, J/kgK | `wx.p_air`, constant | 101,325; 287.05 | 3 | |
| `ES`, `PS`, `HVAC`, `SP`, `cond`, `PTO_always_on` | W | `P_aux` | – | 7 | `HVAC` and `PTO_always_on` may be per hour. |
| `is_on`, `pto_start`, `stop_1s`, `drive_1s` | see C3 | `pto_engine` | – | 5 | |
| `drive_eff`, `regen_eff`, `drivetrain_drag_N` | –, –, N | `drv.drive_eff`, `drv.regen_eff`, `drv.drag_n` | from the drivetrain library | 6 | Method C. |
| `P_regen_max` | W | `drv.regen_cap` | rated motor power | 6 | |
| `P_drive_max` *(to add)* | W | `drv.drive_limit` | **OPEN** rated or peak | 6 | Report only. |
| `v_no_regen` *(to add)* | m/s | `drv.v_no_regen` | 5 km/h | 6 | |
| stop / drive PTO constants *(to add)* | W | `pto.stop_w`, `pto.drive_w` | none | 5 | No slot yet. |
| body-has-own-motor flag *(to add)* | yes/no | `pto.own_motor` | none | 5–6 | Decides where the drive PTO is added. |
| `rho_fixed` *(proposed)* | kg/m³ | `wx.rho_mode` | none | 3 | For VECTO-mode fitting. |
| map set *(map path)* | – | `drv.map_*`, `drv.gear_row` | – | 6 | Passed on to `drivetrain()`. |

| Output | Unit | Meaning | Goes to | User sees |
|---|---|---|---|---|
| `P_wheel` | W per row | power at the wheels (+ driving, − braking) | energy balance | wheel energy; split into air, rolling, grade, inertia |
| `P_trac` | W per row | electric traction power (+ drawn, − recovered) | battery | driving energy; energy recovered by braking; drivetrain loss |
| `P_aux_row` | W per row | all auxiliaries and PTO | battery | on-board systems energy, per system |
| `P_battery` | W per row | power at the battery terminals | battery model, sizing, charging session | battery power over the day; peak power |
| `E_battery` | kWh | net trip energy | session hand-over, sizing | **kWh per day and kWh/km** (the headline numbers) |
| `drive_limit` *(to add)* | dict: rows, peak W, kWh above | rows above the motor's drive limit | report; trigger for the exact-mass rerun | warning line; "share of time at full power" |
| battery dict / per-part energies *(planned, step 7)* | kWh | split by part | results | the full energy balance and loss diagram |

**Report flags:** air density from temperature at fixed pressure (VECTO uses 1.188); hourly weather held for the whole hour; payload changes on arrival; battery treated as 100 % efficient until the battery model exists (certified figures include battery resistance loss); one number stands in for the motor's generation curve; `Cond` rule differs from VECTO.

## C10. `drivetrain` and `vecto_loss_map` (map path)

**What it does.** One chain, VECTO's loss rule at each part: wheel → axle → gearbox → mechanical PTO → motor's own gear (ADC) → rotor inertia → motor limits → motor map → electric power. Used only when the user gives a complete map set (`drv.method` = D). Kiro's Gate 2: −0.35 % / −0.56 % / −0.41 % against VECTO E2 electric energy.

```python
drivetrain(P_wheel, w_wheel, gear,
           i_axle, axle_map, i_gears, gear_maps, i_adc, eta_adc,
           n_em, em_map, em_T_drive, em_T_gen,
           P_rot_rotor, P_pto_mech)
vecto_loss_map(table)      # reader: VECTO .vtlm loss maps must go through this first
```

| Argument | Unit | Filled from | Notes |
|---|---|---|---|
| `P_wheel` | W per row | `consumption_engine` step 4 | |
| `w_wheel` | rad/s per row | `v_avg / r_dyn` | CALC |
| `gear` | integer per row, 0 = no gear | `drv.gear_row` | Gear rule **OPEN**. |
| `i_axle`, `axle_map` | –, rows of (input speed, input torque, torque loss) | `drv.map_axle` | |
| `i_gears`, `gear_maps` | one ratio and one map per gear | `drv.map_gear` | |
| `i_adc`, `eta_adc` | –, – | `drv.adc` | VECTO declaration uses efficiency 1.0. |
| `n_em`, `em_map`, `em_T_drive`, `em_T_gen` | count; rows of (speed, torque, electric power); limit curves | `drv.map_motor` | Recovering beyond the generation curve goes to the friction brakes. Driving beyond the drive curve is flagged, not clipped. |
| `P_rot_rotor` | W per row | `k_rot_rotor` from `force_engine` | |
| `P_pto_mech` | W per row | mechanical drive PTO from `pto.*` | 0 for now. |

| Output | Unit | Meaning | User sees |
|---|---|---|---|
| `P_el` | W per row | electric power of the motors | becomes `P_trac` |
| `P_axle_loss`, `P_gbx_loss`, `P_adc_loss`, `P_em_loss` | W per row | loss in each part | energy balance by part (the VECTO-style split) |
| `P_to_brakes` | W per row | recovered power the motors cannot take | braking loss |
| `extrapolated` | yes/no per row | row fell outside a map | count in the audit block |
| `over_limit` | yes/no per row | drive torque above the motor curve | warning line |

`vecto_loss_map(table)` takes a VECTO loss-map table and returns it with the torque column shifted by the loss (VECTO triangulates on input torque minus loss). Without it the gearbox loss is 2–3 % off.

An idea that is **not decided** (Bob: "skip for now"): hide the difference between method C and maps behind one loss table `P_loss(Pw, v)` built before the engine runs.

---

# PART D. Stages that are not written yet

**Read this first.** Nothing in Part D is code of record. Each row carries one of these:

- `PLANNED` = the project documents say this input will exist (a date is given where there is one).
- `DESIGNED` = Bob decided how it works.
- `PROPOSED` = not decided. Either another tool asks for it (the tool is named) or Claude suggests it. **Bob decides.**
- `OPEN` = a choice Bob has not made.
- `DRAFT CODE` = Kiro wrote a function in `src/` marked "NEW, Bob to review". The shape is shown because it is useful, not because it is agreed.

Numbers quoted from the COWI sheet are **samples from that file**. Most have no source in the file (audited 26 Sep). They are shown so the UX knows the field exists and what size of number goes in it. They must not ship as defaults without a source.

## D0. Stage order and entry contracts (DESIGNED 12 Oct)

```
consumption ─▶ battery ─▶ charging ─▶ flexibility ─▶ cost and CO₂
                 ▲           ▲
              sizing       sweeps        (operations wrapped around stages)
```

| Stage | What it needs at its door | Comes from the stage before as | Or the user gives |
|---|---|---|---|
| consumption | project JSON: vehicles, routes, calendar, weather | – | the full project, or own kWh/km per route (flagged override that skips E1–E9) |
| battery | battery power per row or energy per day; battery data | `P_battery`, `E_battery` | daily kWh |
| charging | session list `{arrival, departure, energy_need_kWh, arrival_SOC}` + battery + chargers + site limit | one session per vehicle per operating date | a pasted session list |
| flexibility | load profile `{time, kW}` or per-session power + equipment capabilities | charging power traces, site peak | a pasted load profile + capabilities |
| cost and CO₂ | annual energy, peak power, equipment list, prices, tariffs | charging and flexibility results | annual kWh + peak kW + prices |

`OPEN`: what happens when user-supplied data has a different time step from the stage (resample, reject, or run at the supplied step and flag it).

## D1. Battery electrical model (PLANNED; DRAFT CODE `src/charging/battery_ocv_ri.py`)

Decided in principle: VECTO's OCV + internal resistance model, with the EU standard values (Reg. 2017/2400 Annex Xb Appendix 10) when the user has no battery data. Today the battery is treated as 100 % efficient.

Draft shape: `battery_step(soc, power_w, dt_s, ocv_table, r_internal, capacity_as)` → new SOC, current, terminal voltage, loss.

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `bat.mode` | Battery mode | (A) I have a battery; (B) size it for me | none | DESIGNED 6 Oct | A closes the sizing inputs (D3). B closes installed kWh. |
| `bat.installed` | Installed energy (kWh) | library (EEA `battery` table, per pack); spec sheet; typed | none | PLANNED | REQ in mode A. |
| `bat.usable` | Usable energy (kWh) | (a) OEM usable value; (b) VECTO usable = SOC window 7.25 %–92.75 % ≈ 0.855 × installed [STD VECTO `BatteryDataAdapter.cs`]; (c) own share | (b) | PLANNED | Keep **installed, VECTO-usable and OEM-usable as three separate fields** (decided 7 Nov). Example of how far they differ: Volvo 540 kWh installed → 380 kWh usable. |
| `bat.v_nom` | Nominal voltage (V) | library; OEM | none | PLANNED | Needed to turn the standard OCV multipliers into volts. |
| `bat.ocv` | Open-circuit voltage by SOC | (a) EU standard: 0.88 / 0.94 / 1.00 / 1.06 / 1.12 × nominal at 0 / 10 / 50 / 90 / 100 % SOC [STD App. 10]; (b) OEM table | (a) | PLANNED | Parser: SOC strictly increasing. The lookup never extrapolates. |
| `bat.ri` | Internal resistance | (a) EU standard for high-energy batteries: 210 / 240 / 270 / 390 mΩ·Ah for 2 / 10 / 20 / 120 s pulses [STD App. 10]; (b) OEM table by SOC | (a) | PLANNED | Which pulse length to use for hours-long depot charging is a choice to flag (the 120 s value is the closest). |
| `bat.c_rate` | Largest charge rate by SOC | (a) EU standard: 0.9 C up to 80 % SOC, falling to 0 at 100 % [STD App. 10]; (b) OEM charging curve (kW by SOC); (c) one kW value | (a) | PLANNED | An OEM curve must override: real tapers are set by the battery management system. Also gives "no regeneration at a full battery" for free. |
| `bat.dc_max` | Fastest DC charging power (kW), connector | OEM spec sheet (CCS2 / MCS) | none | PLANNED | The EEA field for this is 0 % filled, so it must come from OEM sheets. Limits the charger power a truck can use. |
| `bat.mass`, `bat.chem` | Battery weight, chemistry | library / OEM | none | PLANNED | Chemistry is only needed for ageing. Neither is in EEA. |
| `bat.soc_window` | Lowest and highest SOC allowed (%) | typed; from `bat.usable` | **OPEN** | OPEN | Bob's own baseline uses a 20 % buffer (÷ 0.8). |
| `bat.soc_start`, `bat.soc_target` | SOC at the first departure; SOC to charge to | typed | **OPEN** (not in any document) | OPEN | After day one, arrival SOC is carried from the day before. |
| `bat.heating` | Battery heating and conditioning | OEM power or model | none | PLANNED hook (13 Oct) | "High-fidelity physics when data exists, simple model otherwise." Dollinger 2021 (model): about 4 % in winter. |
| `bat.charge_chain` | Charger + battery chain efficiency | from the charger (D5) and this model | measured range 82–91 % (CARB), 90 % (NREL) | PLANNED | Not in HDEV yet. Decides energy from the grid against energy into the battery. |

**Outputs (planned):** SOC over the day and the year, battery loss (kWh), energy at the terminals against energy inside the battery, lowest SOC of the hardest day, rows where regeneration was refused.

## D2. Battery ageing and the year-8 check (PLANNED, mandatory wherever it applies, Bob 14 Nov)

Danish tenders state a guaranteed usable capacity at year 8 (Ressourceindsamling: at least 80 % after 8 years; ARC 2022: at most 25 % loss in 8 years). The tool must take it as an input and report the hardest winter day at year-8 capacity.

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `age.guarantee` | Usable capacity guaranteed at the check year (%) | (a) the tender's or warranty's value; (b) OEM state-of-health curve or table; (c) an ageing model | none. No default exists | PLANNED | REQ for the year-8 check. Without it the check shows "not given", not a guess. |
| `age.check_year` | Year the check is made | typed | 8 | PLANNED | |
| `age.warranty` | Warranty years and km | typed / OEM | none | PLANNED | |
| `age.soh_curve` | State of health by year or by cycles | OEM table | none | PLANNED | |
| `age.model` | Ageing model | calendar + cycle model driven by HDEV's own SOC and temperature series | none | PROPOSED | From the 9 Nov tools review (SimSES, BLAST-Lite). Needs chemistry. Parameters only from the original papers: three open implementations of one paper give three different results. Results are qualitative and cannot show a late-life "knee". |
| `age.replace` | Battery replacement: year, cost | typed | none | PLANNED | Feeds cost. |
| `age.residual_link` | Link the residual value to remaining state of health | toggle | off | OPEN | KIT formula from the tools review: battery residual = (15 % scrap + 85 % × remaining state of health) × battery cost. |
| `age.passport` | Battery passport fields | OEM / passport file | none | PLANNED | Required for EV batteries placed on the market from 18 Feb 2027. Use the passport's field names in the battery data model: rated capacity and fade, power and fade, internal resistance and its increase, round-trip efficiency, expected lifetime, state of certified energy. |

**Outputs (planned):** usable kWh at year 8; hardest day at year-8 capacity (pass / fail and margin); winter at year 8; minimum usable kWh at year 8 for these routes (the tender figure); when capacity would run out; predicted passport values after 8 years (energy throughput, full equivalent cycles, charging rates, time at hot and cold temperatures).

## D3. Battery sizing (PLANNED; "not designed yet" on Bob's data-flow page; DRAFT CODE `src/charging/sizing.py`)

Draft shape of mode B: `size_battery_mode_b(glider_mass_kg, pack_kwh_per_kg, payload_kg, energy_per_km_per_kg, range_km, usable_fraction)`.

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `siz.rule` | What the battery must cover | hardest day of the year; at year-8 capacity; plus a buffer | none | DESIGNED in outline | The hardest day comes from the year run, not from a typed range. |
| `siz.buffer` | SOC buffer (%) | typed | **OPEN** | OPEN | Bob's baseline: × 1.1 for weather, ÷ 0.8 for a 20 % buffer. |
| `siz.glider_mass` | Truck weight without the battery (kg) | OEM; library (curb mass − battery mass, when both are known) | none. No source | PLANNED | REQ in mode B. |
| `siz.pack_density` | Pack energy density (kWh/kg) | OEM; literature | none. No source chosen | PLANNED | REQ in mode B. |
| `siz.step` | Battery size step (kWh) | (a) continuous; (b) real pack sizes from the library | none | PROPOSED | Real trucks come in pack steps (e.g. 4–6 packs). |
| `siz.payload_loop` | Feed battery mass back into curb mass and max payload | fixed rule | on | DESIGNED | A bigger battery lowers the payload left. An early note (9 Sep) solved this in closed form by treating energy as a straight line in mass. The 6 Oct finding is that a mass change can flip a row between driving and regeneration, so battery energy is not exactly a straight line in mass. Kiro's draft uses a loop. Which to use is **OPEN**. |

**Outputs (planned):** battery kWh (installed and usable), battery mass, new curb mass, payload left on each route, payload against diesel, the band from several weather years, position on a tender's score curve.

Bob's own baseline, kept as a comparison beside VECTO and HDEV: regression of kWh/km against weight for popular trucks in Denmark; battery = consumption × longest trip × 1.1 ÷ 0.8.

## D4. Calendar expansion and the session hand-over (DESIGNED 12 Oct; DRAFT CODE `src/resolver/calendar.py`, `session_handover.py`)

Inputs are the schedule inputs of B10. Nothing new for the user.

| Function (draft) | Takes | Gives |
|---|---|---|
| `build_calendar(start_date, end_date, operating_pattern, weather_by_date, danish_holidays, day_type)` | date range, weekday pattern, weather per date, holiday set | one row per date: operating yes/no, day type, weather |
| `build_sessions(day_energy_rows, start_soc, usable_pack_kwh)` | per operating day: arrival, departure, energy used | ordered sessions `{arrival, departure, energy_need_kWh, arrival_SOC}`; SOC carried from day to day and across weekends |

`OPEN` from the same notes: `charger_available` during the day has no producer; per-leg time windows.

## D5. Charging (PLANNED; DRAFT CODE `src/charging/charging_sim.py`, `year_depot_run.py`, Bob's thesis code `ev_charging_env.py`, `allocators_edf_es.py`, `flexibility_setpoints.py`)

Decided: two separate functions. **Sizing mode** is `P = E / t` per vehicle. **Simulation mode** is a per-time-step loop with the OCV + Ri battery, shared chargers and a site limit, run over the whole year with SOC carried over. Draft shapes: `sizing_power(energy_kwh, available_hours)`; `simulate_session(soc_start, power_request_w, duration_s, dt, ocv_table, r_internal, capacity_as, soc_max)`; `run_year_depot(sessions, chargers, site_limit_kw, dt, battery_params, soc_max)`.

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `chg.mode` | How charging is worked out | (a) sizing: smallest power that refills in the time parked; (b) simulation: step by step | **OPEN** | DESIGNED | (a) needs no chargers and no strategy: it closes `chg.strategy`, `chg.share_rule`, `chg.step`. |
| `chg.chargers` | Chargers | (a) size them for me; (b) I choose | none | DESIGNED | (a) makes power and count **outputs**. (b) opens the next three rows. |
| `chg.power` | Charger power per point (kW) | charger library pick; standard power steps; typed | none | PLANNED | COWI's steps: 22 (AC), 43.5, 50, 80, 150, 400 kW. Capped by `bat.dc_max`. |
| `chg.count` | Number of charge points | typed; or an output | none | PLANNED | Proposed way to get it (eFLIPS): simulate with plenty, then shrink to the peak number in use at once. |
| `chg.type` | Charger type, connector | AC (on-board charger) / DC; CCS2 / MCS | none | PLANNED | AC needs the truck's on-board charger power. |
| `chg.caps` | Charger capabilities | smart charging (yes/no); bidirectional (yes/no); lowest power; connectors per charger | none | DESIGNED (first), PROPOSED (rest) | **Decided rule:** no smart charging → ASAP only; the other strategies and flexibility are closed, and the report says why. |
| `chg.eff` | Charger losses | (a) one efficiency; (b) part-load curve from the datasheet | 3–4 % loss (4-leaf report 2023), an assumption | PLANNED | (b) is PROPOSED (matters for slow overnight charging). COWI uses a different idea: average session power = 0.85 × rated power ("load factor", no source in the file). |
| `chg.strategy` | Charging plan | Ready earliest (ASAP) / Grid-friendly (just in time) / Lowest cost (cheapest hours first) | **OPEN** | DESIGNED | Client names on the left, internal names stay hidden. Lowest cost needs hourly prices (D8). Other tools also offer: least-laxity-first, peak-minimising, a grid-company time window (PROPOSED). |
| `chg.share_rule` | How a limited site power is shared between trucks | earliest deadline first / equal share / least laxity first | none | thesis code has the first two; third PROPOSED | Engineering view. |
| `chg.ready_by` | Ready-by time | empty = when the truck leaves; or a clock time | departure time | PLANNED | Tender example: ready at 80 % by 06:00. |
| `chg.step` | Time step | typed | **OPEN**: must come from Energinet product specs. Bob wants finer than 5 min | OPEN | An argument, never hard-coded. |
| `chg.assign` | Which truck uses which point | auto / table; shared chargers | auto | PLANNED | |
| `chg.opportunity` | Charging during the day | none / between shifts at the depot / at a stop (tip site) | none | OPEN | Uses `stop.charger`. ARC added 100 kW chargers for this. |
| `chg.public` | Public charging | share of energy (%) or "only when the depot cannot cover it"; price (DKK/kWh) | COWI computes the share; price sample 3.25 DKK/kWh (FDM 2024) | PLANNED | COWI asks two yes/no questions here: "charge during driving and rest breaks?" and "can the truck charge at the depot during the day?". Both decide the lost-production cost (D9). |
| `chg.aux` | Aux power while charging | fixed rule: none | none (decided 13 Oct) | DESIGNED | |
| `chg.robust` | Robustness cases | one charger out of service; late return (min); cold week; plug-in discipline (% plugged in on return) | off | PLANNED | Each is a labelled what-if case. |
| `chg.min_conn` | Find the smallest connection that still works | toggle | off | PROPOSED | From eFLIPS (`lowest_power`, bisection). Gives the number a grid application needs. |

**Outputs (planned):** charger size and count, chargers per truck; per-session table (arrival SOC, kWh, start, end, power, finish time, slack before departure); fleet schedule; busy hours per charger; share of sessions met; strategies compared; depot load per time step; peak kW; energy from the grid including losses; unmet energy and which trucks; spare trucks needed in a cold week; the "at least 150 kW between 10 % and 75 %" check.

## D6. Depot and grid (PLANNED)

Site capacity is an **input** in one mode and an **output** in the other. Either way it reaches charging as power available over time.

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `dep.mode` | Is there a connection today? | (a) brownfield: yes; (b) greenfield: no | none | DESIGNED 22 Sep | (a) makes connection size an input and a constraint. (b) makes it an output and closes `dep.conn_size`, `dep.building`. |
| `dep.address` | Site address | text / map | none | PLANNED | Also gives price area and the default weather location. |
| `dep.dso` | Grid company | Radius, Cerius, N1, TREFOR El-net, other; or read from Eloverblik master data | from the address or Eloverblik | PLANNED | The Elindsigt file shows Eloverblik returns grid company, supplier and the power limit of the metering point. Using that to prefill is PROPOSED. |
| `dep.category` | Customer category | C, B-lav, B-høj, A-lav, A-høj | from connection size and voltage | PLANNED | Decides the fee formula and the tariff. |
| `dep.conn_size` | Connection size today | amperes or kW (unit switch); or Eloverblik power limit | none | PLANNED | REQ in brownfield. Danish connections are bought per ampere. |
| `dep.building` | Other load on the same connection | (a) none; (b) one number (kW); (c) Eloverblik hourly data through MitID; (d) CT-logger upload | none | PLANNED | (c) and (d) give an hourly profile and a coincidence factor. Shared buildings often have no meter on the main supply, so (d) needs an authorised installer for 4–8 weeks. |
| `dep.spare` | Spare power | computed: connection − building load, per hour | – | AUTO | This is what charging may use. |
| `dep.access` | Access to the grid | full (FNA) / limited (BNA) / stepwise | full | PLANNED | BNA only for 10 kV and above. |
| `dep.bna_cut` | Limited-access what-if | cut in %, from time, to time | none | PLANNED | A labelled what-if, never a forecast: nobody publishes how often cuts happen. Opens only when access = limited. |
| `dep.spaces` | Parking spaces that can have a charger; power per space | table | none | PLANNED | |
| `dep.growth` | Fleet growth phases | table: trucks, month | none | PLANNED | Tender example: 10 trucks now, up to 70 within 48 months. |
| `dep.lead_time` | Lead-time band; wanted commissioning date | typed / from the grid company | none | PLANNED | Reported range: 9 months to more than 6 years. |
| `dep.buffer` | Battery on site | kWh, kW | none | PLANNED | |
| `dep.solar` | Solar on site | kW | none | PROPOSED | In Kiro's registry and in SpiceEV. Not in Bob's notes. |
| `dep.distance` | Distance to the connection point (m) | typed | none | PROPOSED | For trenching cost. COWI uses a flat trenching amount per charger size instead. |
| `dep.housing` | Housing-association mode | residents, cars, share with a charge point by year | none | PLANNED, not designed | Coincidence factor from Eloverblik. The municipal calculator file gives a top-down demand curve (2022–2050, split home / housing association / workplace / public) as a reference only. |

**Outputs (planned):** depot peak in kW and amperes; load hour by hour; load-duration curve; required connection (greenfield); customer category; connection fee from the price list; lead-time band; full against limited access side by side; whether a given cut still leaves every truck ready; capacity charge with and without smart charging; peak by growth phase; capacity-friendly and system-friendly as two separate scores; amperes saved by load management.

## D7. Flexibility (thesis code exists; tool integration PLANNED; DRAFT CODE `src/charging/flexibility.py`)

Flexibility is **always calculated**. It is the gap between the earliest and the latest way of delivering the same energy, kept energy-neutral: anything shifted is recovered within the charging period. The inputs below only decide what is reported as an offer.

Engine-side quantities (all `CALC` from charging, nothing typed): which trucks are present, energy still needed, largest charging rate, site limit, time step, and for export: V2G-capable flag, current SOC, lowest SOC for V2G, battery capacity. Draft shapes: `feasible_heads(present, power_needed_kwh, max_charging_rate_kw, max_station_capacity_kw, dt_h, v2g_capable, soc_current, min_soc_v2g, battery_capacity_kwh)` and `flexibility_per_hour(load_profile_kw, feasible_import_kw, feasible_export_kw, dt_h)`.

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `flex.offer` | Offer flexibility to markets | yes / no | no | DESIGNED | Closed when the chargers have no smart charging. |
| `flex.products` | Products to check | FCR-D, FCR-N, mFRR, aFRR | none | PLANNED | A check against the rules, not a revenue promise. Rules noted on 26 Oct from Energinet's tender conditions: FCR-D minimum bid 0.1 MW, full response in 7.5 s; FCR-N 0.1 MW and at least 1 h of energy; mFRR 1 MW within 12.5 min; sub-second metering. Re-check before use. |
| `flex.aggregator` | Through an aggregator | yes / no | none | PLANNED | A small fleet is below the minimum bids on its own. |
| `flex.dso` | Grid-company flexibility | Cerius-Radius pilot terms | off | PLANNED | Pilot stage, 2 areas, limited-access customers excluded. |
| `flex.v2g` | Vehicle-to-grid | yes / no; lowest SOC for V2G | no | PLANNED | Needs ISO 15118-20 on both truck and charger. |
| `flex.core_window` | Hours the aggregator can rely on | from–to | none | PROPOSED | SpiceEV's "core standing time". |

**Outputs (planned):** up and down power per hour within readiness; the same as cumulative energy bounds (the standard shape every aggregator can read); which products the fleet could qualify for and why not; hours per week available; rebound after a curtailment; cost to readiness.

## D8. Prices (PLANNED)

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `pr.area` | Price area | DK1 / DK2 | from the site address | PLANNED | |
| `pr.el` | Electricity price | (a) hourly spot prices fetched from Energinet's Energi Data Service; (b) own hourly file; (c) day price + night price; (d) one flat price | (a) | PLANNED | (c) and (d) are the simple entries in Kiro's registry (PROPOSED). The plan for cost is the price **at the hours the simulation actually charges**. COWI's stand-in is the mean of the cheapest N hours of the day (N = daily depot charging hours, rounded up), on Jan–Jun 2024 prices × 1.92 for tariffs (the 1.92 has no stated basis). |
| `pr.level` | Price level | low / expected / high | expected; how the levels are defined is **OPEN** | OPEN | Scenario lever. KIT uses the 25 / 50 / 75 % quantiles of a Monte Carlo (PROPOSED). |
| `pr.tariff` | Grid tariff | (a) grid company's time-of-day table for the customer category; (b) own values | none; current price lists not yet in the repo | PLANNED | The Elindsigt file splits a bill into: spot price, supplier mark-up, supplier subscription, grid tariff (low 00–06 / high 06–17 and 21–24 / peak 17–21), grid subscription, Energinet system tariff, transmission tariff, system subscription, electricity tax. Those windows are household (C) tariffs, not depot (A / B) tariffs. |
| `pr.capacity` | Capacity charge | from the grid company | none | PLANNED | For 10 kV customers: based on the average of the 10 busiest hours. |
| `pr.tax` | Electricity tax and refund | typed / from the rate table | none. Kiro's tariff CSV contradicts itself; needs skat.dk | PLANNED | |
| `pr.vat` | Show prices with or without VAT | with / without | without (COWI is without) | PROPOSED | Elindsigt applies × 1.25. Businesses usually reclaim VAT. |
| `pr.path` | Price path over the years | (a) flat; (b) Energistyrelsen projection (Klimastatus og -fremskrivning, newest edition); (c) own % per year | none | PLANNED | COWI computes the projection but no cost formula uses it. |
| `pr.diesel` | Diesel (DKK/l) | typed | COWI sample 11.65 (ok.dk Jan–Jun 2024 + 0.50 duty) | PLANNED | |
| `pr.adblue` | AdBlue | DKK/l, or DKK/km | COWI sample 6.96 DKK/l; the cost sheet uses 0.11 DKK/km | PLANNED | |
| `pr.alt_fuel` | HVO100, biogas | DKK/l, DKK/kg | COWI sample HVO100 19.97 | PLANNED | |
| `pr.public` | Public fast charging (DKK/kWh) | typed | COWI sample 3.25 (FDM 2024) | PLANNED | |
| `pr.flex` | Payment for flexibility products | from Energinet / own | none | PROPOSED | Only if a revenue figure is ever shown. |

## D9. Costs and finance (PLANNED: "port the logic from the COWI sheet")

The first table is the COWI sheet row by row, so no cost input is missed. The second table is what the project notes and other tools add.

**D9a. Every input in the COWI truck cost sheet**

The `cost.*` labels in the third column are defined by this table.

| COWI input (sheet `2025` unless noted) | COWI sample | HDEV input | How HDEV would get it |
|---|---|---|---|
| Km per year (Dashboard) | 100,000 | `cost.km_year` | CALC from the year run; typed when running cost only |
| Years in the fleet (Dashboard) | 8 | `cost.years` | typed: 8 / 10 / 12 (scenario lever) |
| Operating days per year | 300 | – | CALC from the calendar (B10) |
| Km per day, kWh per day | computed | – | CALC |
| Battery capacity, max charging power, average session power | 600 kWh, 400 kW, 352 kW | `bat.*`, `chg.*` | from D1 and D5 |
| Consumption, summer and for the calculation | 1.07 and 1.19 kWh/km | – | CALC by the engine (this is HDEV's main difference) |
| Diesel consumption | 0.288 l/km | `veh.diesel_use` | typed; or from certified diesel data (PROPOSED) |
| Range | 504 km | – | CALC |
| Loading metres | 13.6 m | `cost.loading_m` | typed (PROPOSED: also cost per tonne-km) |
| Price new incl. equipment, electric and diesel | 2,050,000 / 1,150,000 DKK | `cost.price_ev`, `cost.price_diesel` | typed; library when a bid is entered |
| Subsidy (DKK) | 0 | `tax.subsidy` | D10 |
| Down payment | 0 | `cost.down` | typed |
| Residual value % by years held | 15 % (1–6 yrs), 12.5 (7), 10 (8), 7.5 (9), 5 (10), 0 (11–12), same for both | `cost.residual` | table; or linked to battery health (`age.residual_link`) |
| Interest | 3.45 % | `cost.interest` | typed |
| Financing rule | annuity, monthly, paid in advance, residual as balloon | `cost.financing` | cash / loan / lease |
| Depot charger power (Dashboard) | 50 kW | `chg.power` | from D5 |
| Charger and switchboard price | 12,500 to 700,000 DKK by size | `cost.charger` | library band by kW, or own quote |
| Connection amperes | 35 to 650 A by size | – | CALC from the depot peak |
| Price first 25 A, price per ampere | 17,950 and 1,280 DKK (Radius) | `cost.conn_fee` | grid company formula by category (Cerius 2026 incl. VAT: 23,500 for the first 25 A; then per ampere C 1,812.50, B-lav 1,737.50, B-høj 1,675; A-lav 1,637,500 and A-høj 900,000 per MVA), or own figure |
| Groundworks and trenching | 10,000 to 500,000 DKK by size | `cost.trench` | band by kW, or own quote, or from `dep.distance` |
| Driver wage per month (+ a hidden EV premium % that is empty) | 30,000 DKK | `cost.wage` | typed |
| Electricity price at the depot | from the price sheet | `pr.el` | D8, at the simulated charging hours |
| Diesel price, AdBlue per km | 11.65 DKK/l, 0.11 DKK/km | `pr.diesel`, `pr.adblue` | D8 |
| Share charged at the depot, public charging price | computed, 3.25 DKK/kWh | `chg.public`, `pr.public` | CALC from charging; price typed |
| Service per month | 7,685 / 5,000 DKK | `cost.service` | typed, electric and diesel |
| Tyre cost per tyre per km, number of tyres | 0.015 DKK, 8 | `cost.tyres` | typed; tyre count from the axle layout |
| Insurance per month | 1,476 / 768 DKK | `cost.insurance` | typed |
| Road tax per km by year (sheet `Afgifter`) | by weight class, CO₂ class, zone | `tax.km_*` | D10 |
| Hours in operation per day | 9.75 h | – | CALC from the schedule and the driver model |
| Charge during driving and rest breaks? (Dashboard) | No | `chg.public` | D5 |
| Can the truck charge at the depot during the day? | No | `chg.opportunity` | D5 |
| Lost production time | computed % × monthly fixed costs | `cost.lost_time` | CALC from charging (hours of public charging beyond breaks) |

**D9b. Added by the project notes and by other tools**

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `cost.discount` | Discount rate and present-value rule | typed | none | PLANNED | Vejdirektoratet's rule: year 1 is discounted one full period. |
| `cost.depot_years` | Years the depot is written off over | typed | **OPEN** (about 30 years suggested in the 4-leaf report against about 10 for vehicles) | OPEN | |
| `cost.downtime` | Cost of a day out of service | DKK/day | none (tender fine example: 2,000 DKK per truck per day) | PLANNED | T3CO: planned hours per year + unplanned hours per km × cost per hour (PROPOSED). |
| `cost.payload` | Cost of lost payload | DKK/t or extra trips | none | PLANNED | T3CO does this from a distribution of real loads (PROPOSED). |
| `cost.service_contract` | Service contract of 8–10 years | DKK/year | none | PLANNED | All the tenders read bundle one. |
| `cost.battery_price` | Battery price per kWh; replacement | DKK/kWh | none | PROPOSED | Needed to price sizing mode B and replacement. |
| `cost.sensitivity` | Sensitivity ranges | ± % on electricity, diesel, km/year, residual, battery replacement, interest | none | PLANNED | |
| `cost.alt` | Compare against HVO, biogas, B7 | toggles | off | PLANNED | |
| `cost.split` | Split the depot cost across trucks | rule | none | PLANNED | |

**Outputs (planned; COWI has the first two lines):** cost per km, month, year and period, electric against diesel; extra cost at the start, monthly operating saving, break-even in months and years; cost per loading metre per km. Added: year-by-year cash flow; present value; cost by line; electricity split into spot, tariff and tax; sensitivity chart; cost per tonne-km and per tonne collected; grant-ready numbers.

## D10. Taxes and subsidies (PLANNED)

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `tax.km_class` | Km-based road tax class | weight class (3.5–12 / 12–18 / 18–32 / over 32 t) from GVW; CO₂ emission class 1–5 (zero-emission = class 5); zone (environmental zone / other) | auto from the vehicle; zone share **OPEN** | PLANNED | COWI's sample pair: 0.1008 (electric) against 0.8525 DKK/km (diesel) for 2025–27, rising in 2028 and again in 2029. Take current rates from skm.dk. |
| `tax.km_zone_share` | Share of km inside environmental zones | typed; from the route when it has coordinates | none | PROPOSED | The rate differs by zone, so a share is needed. |
| `tax.km_rate` | Own rate table | DKK/km by year | none | PLANNED | Closes `tax.km_class`. |
| `tax.ets2` | Diesel under ETS2 from 2028 | toggle + price | off | PLANNED | |
| `tax.other` | Registration tax, yearly vehicle tax | typed | none | PROPOSED | In Kiro's registry. COWI only has the old yearly Eurovignette table as a comparison. |
| `tax.subsidy` | Subsidy | none / a scheme / own amount (DKK) | none | PLANNED | The Vejdirektoratet pool closed 30 Sep 2026. Separate fields for vehicle, charger and grid subsidy are PROPOSED (Kiro's registry). |

## D11. CO₂ and life cycle (PLANNED)

| ID | Input | Ways to fill it | Default · source | Status | Notes |
|---|---|---|---|---|---|
| `co2.grid` | CO₂ per kWh of grid electricity | (a) Energistyrelsen yearly series (COWI's copy: 41.5 g/kWh in 2024 falling to 7.0 in 2034; take the newest edition); (b) own value; (c) at the actual charging hours from Energi Data Service (5-minute values per price area) | (a) | PLANNED | (c): average or marginal factor is a method choice to state. |
| `co2.upstream` | Upstream factor on grid electricity | typed | COWI uses × 1.18 | PROPOSED | |
| `co2.diesel` | Diesel: tailpipe and fuel production (g CO₂e/l) | typed | COWI sample 2,420 + 900 for diesel with 7 % biodiesel; no source verified by us | PLANNED | |
| `co2.alt` | Biodiesel 1st and 2nd generation, HVO, biogas | typed | COWI sample fuel production 2,650 (1st gen. incl. land-use change) and 440 g/l (2nd gen.) | PLANNED | |
| `co2.vehicle` | Vehicle production (kg CO₂e per kg of vehicle), vehicle weight | typed | COWI sample 6.6 kg/kg (ICCT 2023) and 14,884 kg | PLANNED | |
| `co2.battery` | Battery production (kg CO₂e/kWh), battery size | typed | COWI sample 61 kg/kWh (IVL 2019) | PLANNED | |

**Outputs (planned):** tonnes per year, electric and diesel; saved over the period; grid factor path; CO₂ at the charging hours; life-cycle total and per km; km driven before the electric truck is ahead; comparison with HVO, biogas and B7.

## D12. Tender and offer sheet (PLANNED; shown only when the project is a tender)

| ID | Input | Side | Status | Notes |
|---|---|---|---|---|
| `ten.weights` | Award weights: price / technical / delivery / environment | buyer | PLANNED | Seen in Danish tenders: price 50–70 %, technical 25–35 %, delivery 15–25 %, environment 10 %. |
| `ten.curves` | Score curves, e.g. battery 250 → 450 kWh for 1 → 10 points | buyer | PLANNED | |
| `ten.minimums` | Minimum requirements: usable kWh at year 8; at least 150 kW between 10 % and 75 %; crane and compactor at the same time; ready at 80 % by 06:00 | buyer | PLANNED | |
| `ten.bids` | One column of spec values per bid (battery, usable, charging power, weight, price, service) | supplier | PLANNED | Bids override the generic values on the same routes. Idea being weighed: a link where bidders fill in their own column. |
| `ten.guarantees` | Guaranteed values: year-8 capacity, downtime ≤ 5 days per year, response within 2 h | supplier | PLANNED | |
| `ten.brand_neutral` | Brand-neutral report | buyer | PLANNED | |

## D13. Scenarios, sweeps, uncertainty (DESIGNED in outline)

| ID | Input | Ways to fill it | Status | Notes |
|---|---|---|---|---|
| `scn.changes` | A scenario = the base project + a list of changes | any field | DESIGNED | The base is never overwritten. The run restarts at the first stage a change touches. |
| `scn.levers` | Quick levers | fleet size, charging plan, price level, weather year, ownership years | DESIGNED | |
| `scn.sweep` | Option lists to try | battery sizes, charger power steps, charging plans, site limits | DESIGNED 22 Sep | The result is a menu of options, not one number. Include rows just under thresholds where the price jumps. Lists must come from real products and grid-company steps. |
| `scn.mc` | Uncertain inputs | distributions for payload, temperature, arrival time | PLANNED | Method: JCGM 101:2008. Gives ranges (P10 / P50 / P90). Weather spread across years is not Monte Carlo. |
| `scn.compare` | Compare runs | pick two or more | PLANNED | |

## D14. Libraries, assistant, views (PLANNED)

| Item | What it holds or does | Status |
|---|---|---|
| Vehicle library | one row per exact configuration, EEA certified data + spec sheets, provenance class on every field | data joined 7 Nov; schema is a draft |
| Drivetrain library | `drive_eff`, `regen_eff`, `drivetrain_drag_N` per truck, fitted on certified results | Kiro PRs #37–#40; decision on class numbers OPEN |
| Charger and tariff library | charger specs, grid-company price lists | Kiro PR #26, with known errors to fix |
| PTO profile library | sourced profiles per body type | only the VECTO refuse profile is an official default |
| Saved routes, payload profiles, schedules | the user's own templates | DESIGNED: reached from the fleet table, no separate templates page |
| AI assistant | fills the project JSON from dumped data, then asks for what `check()` lists as missing | PLANNED. It never picks defaults. |
| Client / OEM / engineering view | same engine, different fields shown | DESIGNED; slot shape OPEN |

## D15. Cross-check against the other two Excel files

| File | Inputs it asks for | Where they land in HDEV |
|---|---|---|
| `Elindsigt2.2.xlsx` | Eloverblik token (MitID); metering point or address when there are several; expected yearly kWh; electricity supplier and product, or manual subscription and mark-up; period; production address | `dep.building` branch (c): token, metering point, period. It also returns address, grid company, supplier and power limit → could prefill `dep.dso`, `dep.conn_size` (PROPOSED). Supplier product → `pr.el` mark-up and subscription. The file does **not** compute a coincidence factor. |
| `ChargePointCalculator_v5.xlsx` | municipality (98), year (2022–2050), EV uptake curve, split by place of charging (home / housing association / workplace / public), range-extension need | reference for `dep.housing` and for municipal clients only. Not part of depot sizing (decided 26 Sep). |

---

# PART E. Lock and unlock rules (what one choice does to other inputs)

This is the list to build the form logic from. "Closes" means the field is hidden or greyed and its value is not sent. "Fills" means the field gets a value the user can still overwrite. Rules marked *(Claude)* follow from the documents but were never stated as a rule: check them.

## E1. Vehicle

| # | When the user picks | It opens | It closes | It fills |
|---|---|---|---|---|
| 1 | `veh.source` = library pick | every vehicle field as an editable copy | the group and class pickers | group, axle layout, curb mass range, GVW, tyre size and RRC per axle, CdxA range, motor rated power, gears, installed and usable kWh, steering technology, drivetrain numbers (when fitted) |
| 2 | `veh.source` = class only | group or weight-class picker | library fields; OEM-only fields | every STD value for the group. Curb mass, tyre size, drivetrain numbers and the regen cap have no class value yet (see G1) |
| 3 | `veh.source` = manual | all fields | library fields | STD values where they exist |
| 4 | a mission | – | – | body or trailer, reference payload, crosswind set, axle load shares, the mission column of every aux table |
| 5 | mission = Construction | – | the declared CdxA | VECTO's `CdxA_Construction` |
| 6 | a trailer | – | – | trailer mass, trailer ΔCdxA (rigid + trailer), trailer axles in rolling resistance, trailer wheels in wheel inertia |
| 7 | any edit of a filled value | "reset" on that field | – | the value is marked "your value"; a replaced VECTO value is labelled non-VECTO in the report |

## E2. Route, stops, payload, PTO

| # | When the user picks | It opens | It closes | It fills |
|---|---|---|---|---|
| 8 | route = VECTO cycle | stop time, payload and PTO columns of the stop table | distance, number of stops, time per stop default, road type, speeds, grade | the mission (rule 4); for MunicipalUtility the PTO stops from the file |
| 9 | route = typed | distance, number of stops, time per stop, road type, speeds, grade; the full stop table | upload fields | 45 min, 30 / 50 / 80 km/h, flat (all flagged assumptions) |
| 10 | route = map | the map; stop time, payload, PTO | distance, number of stops | distance, speeds, altitude from the provider |
| 11 | route = GPS | payload and PTO columns only | distance, number of stops, speeds, stop times, grade | everything from the file |
| 12 | route = describe it / call-outs | a confirmation step before Run | manual route fields until confirmed | waypoints from the AI reader, guesses flagged |
| 13 | any edit of a VECTO cycle | "save as" | – | the route becomes a user route; the template stays untouched |
| 14 | the schedule gives a departure time | – | the departure field on the route | `t_start` |
| 15 | payload shape = constant | start payload | end payload, payload column of the stop table | – |
| 16 | payload shape = linear | start and end payload | payload column of the stop table | equal step at each payload stop |
| 17 | payload shape = per stop | payload column of the stop table | end payload | – |
| 18 | payload basis = a VECTO value or maximum | – | the typed value | start payload |
| 19 | "payload changes here" unticked on a stop | – | that stop's payload cell | the stop keeps its stop time for driving |
| 20 | PTO = no | – | every PTO field and the PTO column of the stop table | – |
| 21 | stop part = one number | stop power, efficiency | stop profile | – |
| 22 | stop part = profile | profile picker or table, efficiency, standing-time rule | stop power | standing time = stop time + profile length (VECTO rule) |
| 23 | drive part = one number or profile | "does the body have its own electric motor?" | the other drive option | – |
| 24 | PTO on, but no stop is ticked *(Claude)* | a warning | – | – |
| 25 | PTO ticked on a 0-second marker row | – | – | allowed only when a drive part exists |

## E3. Aerodynamics, tyres, drivetrain, on-board systems

| # | When the user picks | It opens | It closes | It fills |
|---|---|---|---|---|
| 26 | own a1, a2, a3 or own yaw table | – | the VECTO crosswind set | – |
| 27 | tyre size from the list | – | typed radius | radius and wheel inertia |
| 28 | cold-tyre correction on | tyre load index | – | Kt from the load index |
| 29 | `drv.method` = library (A) | – | typed numbers, three efficiencies, all map uploads | `drive_eff`, `regen_eff`, `drivetrain_drag_N`, regen cap |
| 30 | `drv.method` = typed (B) | the three numbers | library values, three efficiencies, maps | – |
| 31 | `drv.method` = three efficiencies (C) | motor, inverter, gearbox, regen efficiency | the drag number (set to 0), maps | `drive_eff` = product of the three |
| 32 | `drv.method` = maps (D) | every map upload, ratios, ADC, number of motors, limit curves, rotor inertia, gear rule | the three numbers and the typed regen cap (the generation curve replaces it) | – |
| 33 | maps incomplete | an error naming what is missing | Run | – |
| 34 | an aux = own W (ES, PS, SP, Cond) | the W field and its factor, with the "0.7 = VECTO; 1.0 if already electric" label | that aux's technology dropdown | – |
| 35 | steering = own W | W | steered axles, steering technology | – |
| 36 | no reference vehicle for the driver (`coast_mass` empty; engineering view) | – | coasting, overspeed, `P_max`, the driver's drag table | pure kinematic driver |

## E4. Weather and cab climate

| # | When the user picks | It opens | It closes | It fills |
|---|---|---|---|---|
| 37 | weather = stored DMI | location, year(s), shift, worst day | file upload | nearest station per parameter |
| 38 | several weather years | P50 / P90 results | – | – |
| 39 | weather = own file | upload | location, station, year | – |
| 40 | weather = VECTO declaration | – | location, year, shift, worst day, air-pressure options | wind 3 m/s at 4 m, air density 1.188 |
| 41 | weather = VECTO declaration *(Claude)* | – | cab climate mode C (it needs hourly temperature and sun) | – |
| 42 | cab climate = VECTO constant (A) | "Default / None" | own W, every thermal field | factor 1.25 |
| 43 | cab climate = own W (B) | W and the factor label | every thermal field | – |
| 44 | cab climate = thermal (C) | people, heater set-up, set-points, cab data, power limits, ventilation, fresh air | the constant fields | factor forced to 1.0; COP tables from the heater set-up |
| 45 | thermal, cab data missing | red fields | Run | – |

## E5. Planned stages

| # | When the user picks | It opens | It closes | It fills |
|---|---|---|---|---|
| 46 | run starts at charging / flexibility / cost | that stage's entry fields (D0) | all inputs of the earlier stages | – |
| 47 | own kWh/km per route | the kWh/km field | vehicle physics, PTO, on-board systems, weather for that route | flagged override |
| 48 | battery mode A | installed and usable kWh | sizing inputs | – |
| 49 | battery mode B | sizing rule, glider mass, pack density, buffer | installed kWh | battery kWh, mass, new curb mass |
| 50 | battery data = EU standard values | nominal voltage | OEM tables | OCV, resistance, charge-rate limit |
| 51 | year-8 guarantee given | year-8 results | – | – |
| 52 | charging mode = sizing | – | chargers, strategy, sharing rule, time step | smallest power per truck |
| 53 | chargers = size them for me | – | charger power and count | both become results |
| 54 | charger without smart charging | – | "Grid-friendly", "Lowest cost", flexibility offers | strategy = Ready earliest; the report says why |
| 55 | strategy = Lowest cost | – | – | needs hourly prices: closed when the electricity price is one flat number *(Claude)* |
| 56 | site = brownfield | connection size, building load, spare power | "required connection" as a result | – |
| 57 | site = greenfield | – | connection size, building load | required connection becomes a result |
| 58 | building load = Eloverblik | connect button, metering point, period | fixed kW, logger upload | hourly profile; could also fill grid company and connection size |
| 59 | access = limited | what-if cut (%, from, to) | – | allowed only for 10 kV and above |
| 60 | offer flexibility = yes | products, aggregator, V2G | – | – |
| 61 | electricity = own hourly file | upload | fetch, price level | – |
| 62 | financing = cash | – | interest, down payment, lease fields | – |
| 63 | financing = loan | interest, down payment, residual | lease fields | – |
| 64 | financing = lease | monthly lease, term | interest, residual *(Claude)* | – |
| 65 | own road-tax rate | rate table | weight class, CO₂ class, zone | – |
| 66 | grid CO₂ = own value | value | yearly path, hourly option | – |
| 67 | project purpose = tender | the tender page (buyer and supplier sides) | – | – |
| 68 | a scenario change | – | – | the run restarts at the first stage the change touches |

---

# PART F. Outputs

## F1. What each written function hands on (engine outputs)

Already listed per function in Part C. In one line each:

| Function | Outputs | Seen by the user directly? |
|---|---|---|
| `crosswind_engine` | `W1`, `W2` | no |
| `payload_engine` | payload per waypoint | yes: stop table, payload picture |
| `pto_engine` | `is_on`, `pto_start`, `stop_1s`, `drive_1s` | no (profile preview proposed) |
| `driver_model` | `T`, `S`, `V`, `A`, `grade`, `M` | yes: speed trace, time in each driving mode, trip duration |
| `force_engine` | `k_lin`, `k_roll`, `k_rot_wheel`, `k_rot_rotor`, `L`, `v_avg` | no |
| `SP_power_helper` | steering W | yes: one line in on-board systems |
| `HVAC_thermal` | `HVAC_el` per hour, `fuel_heat` | yes: cab climate energy |
| `P_aux` | six electric W values | yes: on-board systems table |
| `consumption_engine` | `P_wheel`, `P_trac`, `P_aux_row`, `P_battery`, `E_battery` (+ drive-limit count) | yes: every energy result |
| `drivetrain` | `P_el`, four loss arrays, `P_to_brakes`, two flag arrays | yes: loss per part |

## F2. What the user sees, by result page

Result pages as agreed on 13–14 Nov: Overview, Energy, Battery, Charging, Grid, Cost, CO₂, Compare, Documents, Inputs and sources. "Now" = can be produced when `consumption_engine` is finished. "Planned" = needs a stage from Part D.

**Overview**

| Result | Built from | When |
|---|---|---|
| Verdict per vehicle and for the fleet; first failing check | all stages | planned |
| Six checks: battery new, battery at year 8, full before leaving, grid connection, route fits the shift, weight limit | D1–D6, payload check | route-fits-shift and weight: now; rest planned |
| Input context as pictures: distance, stops, payload along the route, schedule | readers, `payload_engine` | now |
| Four headline figures | – | now / planned |

**Energy**

| Result | Built from | When |
|---|---|---|
| kWh per day (average, hardest day), kWh/km, kWh per tonne-km, per tonne collected | `E_battery`, distance, payload | now |
| P50 / P90 across weather years | several year runs | now |
| Energy balance: air, rolling, grade, inertia, brakes, drivetrain (per part on the map path), each auxiliary, cab climate, PTO, regeneration recovered | `force_engine` coefficients, `P_wheel`, `P_trac`, `P_aux_row`, `drivetrain` losses | now (battery loss planned) |
| Monthly table: km, °C, kWh driving, aux, cab climate, regeneration, at the battery, charger losses, from the grid, peak kW, cost | year run | first seven columns now |
| Loss diagram: grid → charger → battery → motor → gearbox → wheel → air / rolling / grade / brakes, with an aux branch | all stages | planned |
| Time standing, accelerating, cruising, coasting, braking | `M` | now |
| Speed and battery power over the day | `V`, `P_battery` | now |
| kWh/km per extra tonne and per °C; winter against summer | reruns of step 9 | now |
| Expected kWh/km by month and temperature, in the shape fleets log it | year run | now |
| Operating time (not only range) | `T` | now |
| Simulation quality check: average / min / max speed, max acceleration and deceleration, distance, share of time at full power | driver rows, drive-limit count | now |

**Battery**

| Result | When |
|---|---|
| Installed against usable; usable at year 8 | planned |
| Hardest day at year-8 capacity; winter at year 8; margin left | planned |
| SOC on return per truck across the year; lowest SOC | planned |
| Minimum usable kWh at year 8 for these routes; position on the tender's score curve | planned |
| Battery against payload; payload left; payload against diesel | planned |
| Predicted battery passport values after 8 years | planned |

**Charging**

| Result | When |
|---|---|
| Charger size and count; chargers per truck | planned |
| Session table: arrival SOC, kWh, start, end, power, finish, slack before departure | planned |
| Fleet schedule; busy hours per charger; share of sessions met | planned |
| Strategies compared | planned |
| Robustness: one charger out, late return, cold week; spare trucks | planned |
| Charging losses; energy from the grid | planned |

**Grid**

| Result | When |
|---|---|
| Depot peak in kW and amperes; load hour by hour; load-duration curve | planned |
| Required connection; customer category; connection fee; lead-time band | planned |
| Full against limited access; what-if cut | planned |
| Capacity charge with and without smart charging; peak by growth phase | planned |
| Flexibility up and down per hour; products the fleet could qualify for; hours per week | planned |

**Cost and CO₂**

| Result | When |
|---|---|
| Cost per km / month / year / period, electric against diesel; break-even | planned |
| Year-by-year cash flow; present value; cost by line; electricity split | planned |
| Sensitivity; alternatives (HVO, biogas) | planned |
| CO₂ per year and saved; grid factor path; at charging hours; life cycle | planned |

**Compare, Documents, Inputs and sources**

| Result | When |
|---|---|
| Two or more runs side by side: inputs that changed, results | planned |
| Six documents: feasibility report, grid connection application, tender annex, financial model, grant application data, client presentation; CSV export | planned |
| Crane / compactor energy sheet exported as a VECTO PTO profile | planned |
| Every value used, with its source and its mark (given / default / assumption / no source) | now (from `fill()`) |
| Run fingerprint: engine version, date, input hash | now |
| Model status per result (validated / in testing / not built) | now |
| Known decisions stated: 10° yaw clamp, reference driver mass, fresh-air term, PTO placement, drivetrain method | now |
| Rule: no firm winter verdict until cold-weather effects are validated; winter shown as a labelled conservative case | now |

---

# PART G. What blocks a run, what is open, and where documents disagree

## G1. The shortest path: what a user must give to run consumption

| Vehicle source | Must give | Gets for free | Gap today |
|---|---|---|---|
| Library truck | the truck; a route (one source); departure time and working days; depot location and weather year; cab climate mode | everything else | curb mass is a range in the library (which value?); CdxA is a range (which value?) |
| Class only | group or weight class; mission; route; schedule; location and weather year; cab climate mode | height, CdxA, body or trailer, payload, crosswind set, aux tables, `.vacc`, driver constants | **no class value yet for:** curb mass, tyre size (radius), drivetrain numbers, regen cap and drive limit (no rated power without a truck). These four decide whether a "weight class and routes only" user can run at all. |
| Manual | group; mission; curb mass; GVW; tyre size; drivetrain numbers and regen cap; route; schedule; weather; cab climate mode | every STD value | – |

Always required, whatever the path: a route source with its own required fields (B2), a departure time, working days, and in thermal cab mode the cab data, people, heater set-up and ventilation rates.

Never asked from a client: yaw coefficients, `.vacc`, driver constants, physics constants, the factors in `P_aux`, loss maps, rotor inertia.

## G2. Open decisions that change the UX

| # | Decision | Where it bites |
|---|---|---|
| 1 | Default payload basis: VECTO reference, maximum, or both | `pl.basis` |
| 2 | Generic curb mass per class: source | `veh.curb_mass`, class-only path |
| 3 | Class-level drivetrain numbers, or always per truck | `drv.method` for sizing users |
| 4 | `P_drive_max`: rated or peak power | `drv.drive_limit` |
| 5 | Gear rule when the gear is unknown; rotor term with a fixed or per-row ratio | `drv.i_total`, map path |
| 6 | Whether the fitted drivetrain drag also feeds the driver's coasting drag table | `drv.drag_table` |
| 7 | Map route provider | `rt.map`, AI reader |
| 8 | GPS: zero-speed threshold; can measured speed skip the driver model; do coordinates pick the weather station | `rt.gps_file` |
| 9 | Emergency and on-call vehicles: how they are entered | `sch.oncall` |
| 10 | Electric drive-PTO profile still running at the next stop: keep drawing while standing? Stop and sweeper constants now or later? | step 5 of `consumption_engine` |
| 11 | Half-second PTO profiles: resample in the library or average in `pto_engine` | `pto.stop_profile` |
| 12 | Mixer default profile (two sources 4× apart) | PTO library |
| 13 | Cond rule (keep HDEV's or follow VECTO); Cond with the drive-PTO part | `aux.cond` |
| 14 | Air pressure: fixed, per route from altitude, or per row; optional fixed air density | `wx.p_air`, `wx.rho_mode` |
| 15 | Cold-tyre and wet-road factors: build or not | `tyre.cold`, `tyre.road` |
| 16 | Weather default year; whether day-mean and drive-hours options stay | `wx.years`, `wx.detail` |
| 17 | Which value is pre-filled from a library range (curb mass, CdxA) | library pick |
| 18 | Who computes `m_red_wheels` and `Crr_eff` | parser / engine split |
| 19 | SOC window, start SOC, target SOC, sizing buffer | D1, D3 |
| 20 | Charging time step; default strategy; opportunity charging producer | D5 |
| 21 | Price-level definitions; depot write-off years; residual linked to battery health | D8, D9 |
| 22 | Slot shape for two-sided inputs; which fields are open, collapsed or hidden per view | all pages |
| 23 | What to do when supplied data has a different time step from the stage | D0 |
| 24 | If both departure and return times are given, which wins | `sch.out`, `sch.back` |

## G3. Where the documents disagree (newer one used in this file)

| # | Topic | Older statement | Newer statement used here |
|---|---|---|---|
| 1 | Wind into the crosswind engine | 13 Nov inventory: one reference wind, 5.028 m/s at 10 m | Notebook (16 Nov): the crosswind table is indexed by weather hour, so hourly wind. **Bob to confirm which is the default.** |
| 2 | Gear unknown | 12 Nov: use the lowest gear | 14–16 Nov closeout: dropped (+46 % to +71 % wrong); rule open |
| 3 | Regen cap | 26 Oct list and 13 Nov inventory: none = no cap | 16 Nov: required; default = rated motor power |
| 4 | Drivetrain default | 13 Nov inventory: 0.95 / 0.95 / 0.98, or a toggle maps vs efficiencies | 16 Nov: method C from the library is the default; the three efficiencies are method C with zero drag; maps only as a full set |
| 5 | `m_red_wheels` | `status-engine` (9–12 Nov): computed in the parser | 12 Nov correction: Bob never decided that; calculations stay in the engine |
| 6 | HVAC functions | `status-engine`: final on 9 Nov | 12 Nov: sent to Kiro first; 13 Nov: final |
| 7 | Gravity | 26 Oct list: 9.81 | 9.80665 (VECTO), decided |
| 8 | `theta_red` unit | 13 Nov inventory: dimensionless "inertia reduction" | By the formula in `force_engine` it is wheel inertia in kg·m² |
| 9 | Aux names | 13 Nov inventory: "Power steering PS", "Pneumatic system SP" | Code: PS = air (pneumatic) system, SP = steering pump. The inventory has them swapped. |
| 10 | Default payload | 7 Oct: VECTO reference | Listed as open since 2 Nov |
| 11 | Route sources | 8 Oct: four (VECTO cycle, typed, GPS, AI) | Bob's 16 Nov brief adds a map source and saved templates |
| 12 | Typed route | 13 Nov inventory: distance and road type per leg | Bob's 16 Nov brief and `resolve_typed`: total distance + number of stops, then edit |
| 13 | Time per stop default | 45 min (2 Sep, Bob's judgement) | The dt-cargo sample median is 22 min; the default has no source |
| 14 | Run mode (sizing / simulation) | 13 Nov inventory: on the Project page | Later page list: with Charging |
| 15 | PTO at a stop shorter than the profile | `pto_engine` raised an error (1 Nov) | 12 Nov: the check moved to the parser |

## G4. Things this file could not settle from the documents

- The crosswind speed-grid step, and the exact `dh` and `dphi_deg` the parser should pass (only the values of the VECTO check, 0.4 m and 1°, are written down).
- Which column of `PS-Table.csv` a battery-electric truck reads.
- Which VECTO standard value stands in for tyre rolling resistance when there is no certified or label value.
- How the top-speed cap (design speed 85 km/h) is applied to typed and map routes.
- Whether the EEA energy figure the drivetrain numbers were fitted on includes battery resistance loss (open since PR #40). It decides whether the battery model would count that loss twice.

---

*End of file. Sections A–C describe code that exists. Section D describes plans. Update the status tags as functions are finalised.*
