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
