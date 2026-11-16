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
                            │        │        │       │        │
                            │        │        │       │        └ when it runs (Part B10)
                            │        │        │       └ body equipment power (B5)
                            │        │        └ load along the route (B4)
                            │        └ waypoints + stop table (B2, B3)
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
├─ Battery and motor cooling  Cond
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
| `aux.cond` | Battery and motor cooling (W) | (a) VECTO by mission [STD `Cond-Table.csv`]: 600 / 600 / 550 / 550 / 600 W for long haul / regional / urban / municipal / construction; (b) own W; (c) thermal model | (a) | DEF | `cond_power` | (c) is `PLANNED`. Timing rule today: on while moving or while PTO works. VECTO: on when a motor or the electric PTO is on, off when standing and when coasting. Kiro recommends keeping the HDEV rule (effect 0.012–0.090 % of trip energy). Under review in step 7. |
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
