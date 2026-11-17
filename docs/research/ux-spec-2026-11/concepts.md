# EV Scope UX concepts

> Scope: tool UX only. This file was written from `docs/design/hdev-input-map.md` before any rejected screen, PR #35 layout, or old-demo layout was inspected. [MAP §0–G] [JUDGEMENT]
>
> Status vocabulary in this file follows the map: `FINAL`, `WIP`, `DESIGNED`, `PLANNED`, `PROPOSED`, `OPEN`, and `PARKED`. [MAP §0.3]

## A0.1 The things people work with

| Object | Relationship | Life and reuse | Status | Evidence |
|---|---|---|---|---|
| Project | One project owns one base JSON, many fleet groups, shared project settings, scenarios, runs, results, and documents. | The base is durable and is never overwritten by a scenario. | DESIGNED | [MAP §0.4.1; §D13] |
| Fleet group | A project has many groups; one group represents a count of identical vehicles doing the same duty. | A group refers to reusable vehicle, route, load, body-equipment, and schedule objects. | DESIGNED | [MAP §1; §B10 `fleet.count`] |
| Vehicle | Many fleet groups may use one vehicle definition. | A library record is copied into a project and remains editable; VECTO standard values stay resettable. | FINAL / WIP / PLANNED by field | [MAP §A1; §B1; §E1 rules 1–7] |
| Route | Many fleet groups may use one route definition; one route has many waypoints and stops. | It may start from VECTO, typed data, a map, GPS, an AI-readable description, or a saved route. | FINAL / PLANNED by source | [MAP §A2; §B2] |
| Stop | A route has many ordered stops; the stop table is a filtered view of route waypoints, not another store. | Payload and PTO attach to stable stops; a stop may remain a driving stop when it stops changing payload. | FINAL / PROPOSED for bulk tools | [MAP §B3; §E2 rules 19 and 25] |
| Load pattern | A fleet group refers to one load pattern; one pattern can be reused on compatible routes. | It is constant, linear, or one value per payload-changing stop. | FINAL, with basis OPEN | [MAP §A3; §B4] |
| Body equipment / PTO | A fleet group refers to one equipment definition with stop, drive, and always-on parts. | A profile can be standard, saved, uploaded, or entered as a table. | FINAL / PLANNED / PARKED by part | [MAP §A4; §B5] |
| Schedule | A fleet group refers to one schedule; one schedule expands to many operating dates and later to sessions. | Week patterns, holidays, shutdowns, exceptions, shifts, and seasons change that expansion. | DESIGNED / PLANNED / OPEN by field | [MAP §A9; §B10; §D4] |
| Weather set | A project or depot uses one source with one or several real weather years. | Years stay paired to dates and create a spread; they are not averaged together. | FINAL / PLANNED / OPEN by branch | [MAP §A10; §B11] |
| Cab climate model | A project chooses one calculation mode; thermal mode depends on weather and cab data. | It changes energy for every affected vehicle and day. | FINAL, with PROPOSED cab templates | [MAP §A10; §B12] |
| Battery | A vehicle has battery data or asks the tool to size it. | Size, mass, usable capacity, charge limits, ageing, and the year-8 guarantee feed several later stages. | DESIGNED / PLANNED / OPEN | [MAP §A11 T13; §D1–D3] |
| Charging session | A schedule and energy result produce many sessions, or the user supplies a session list. | Sessions connect vehicles, batteries, chargers, and a shared site limit. | DESIGNED / PLANNED | [MAP §D0; §D4–D5] |
| Charger | A depot has many points or asks the tool to size them. | Charger capability controls strategies and whether flexibility is available. | DESIGNED / PLANNED / PROPOSED | [MAP §D5; §E5 rules 52–55] |
| Depot and grid connection | A project has a site and either an existing connection or a required future connection. | Building load, access terms, parking spaces, phases, and optional assets constrain charging. | DESIGNED / PLANNED / PROPOSED | [MAP §D6] |
| Price, tariff, cost and CO₂ set | One project has time series, price paths, paired electric/diesel costs, taxes, and emissions factors. | A cost-only start can supply the stage contract without routes. | PLANNED / PROPOSED / OPEN | [MAP §D0; §D8–D11] |
| Tender | A tender project has buyer requirements and one or more supplier bids. | The same routes and year-8 test apply to each bid. | PLANNED | [MAP §D12] |
| Scenario | A project has many scenarios; each stores changes to the base. | A scenario reruns from the first touched stage and never overwrites the base. | DESIGNED / PLANNED | [MAP §D13; §E5 rule 68] |
| Run | A project or scenario has many immutable runs with stage states and a fingerprint. | `check(project)` precedes a run and identifies missing, defaulted, and wrong values. | FINAL / WIP / PLANNED by stage | [MAP §0.4.2; §C0; §F2] |
| Result | One run produces many results, each with model status, source lineage, and start-point limits. | Results can be current, partial, user-supplied upstream, or out of date. | NOW / PLANNED | [MAP §F1–F2; §D0] |
| Document | A run can feed six named documents and data exports. | Documents select ordered inputs and results rather than becoming another model. | PLANNED | [MAP §F2] |
| Library entry | Libraries hold vehicles, drivetrain values, chargers, PTO profiles, routes, payload profiles, and schedules. | Standard entries are locked at the library level; a project receives an editable copy. | FINAL / DESIGNED / PLANNED | [MAP §D14; §E1 rule 1; §E2 rule 13] |

### Relationship sketch

```text
PROJECT (one base JSON)
├── fleet groups 1..n
│   ├── count
│   ├── vehicle ref ──┐
│   ├── route ref ────┼── reusable project/library objects
│   │   └── stops 0..n│
│   ├── load ref ─────┤
│   ├── PTO ref ──────┤
│   └── schedule ref ─┘
├── weather + cab climate
├── battery → sessions → chargers ↔ depot/grid → flexibility
├── prices → costs/tax + CO₂
├── tender: buyer rules + bids 1..n
└── scenarios 0..n → runs 0..n → results → documents
```

The sketch treats fleet groups as assignments between reusable objects rather than as a spreadsheet row with five dropdowns. [MAP §1] [JUDGEMENT]

## A0.2 Tasks and cadence

The map gives object and engine cadence, not usage analytics, so every frequency below is a design assumption to test with users. [MAP §C0] [JUDGEMENT]

| User | Once per project or bid | Per reusable object or fleet change | Per check or run | Status and basis |
|---|---|---|---|---|
| Fleet owner or operator | Name the project, choose a start point, define the site, weather basis, and business purpose. | Describe operating groups, routes, loads, equipment, and calendars; add exceptions and growth. | Resolve missing items, run, inspect route fit, energy, readiness, and cost. | DESIGNED / PLANNED; [MAP §B1–B12; §D0; §F2] [JUDGEMENT] |
| Municipality or public buyer | Set tender purpose, common routes, project period, and buyer rules. | Define minimums, award curves, the year-8 guarantee, and bid columns. | Check each bid on the same duty, compare, and issue a tender annex. | PLANNED; [MAP §D2; §D12; §F2] [JUDGEMENT] |
| Truck maker or dealer | Open a buyer project in OEM view and identify the tested configuration. | Supply declared vehicle, battery, charging, and optional map data; save a configuration. | Run the buyer duty, inspect limits and audit flags, compare configurations. | FINAL / PLANNED; [MAP §B1; §B6–B8; §D1; §D12] [JUDGEMENT] |
| Charge-point operator, aggregator, or grid company | Define the depot, connection, access agreement, and market intent. | Maintain charger sets, capabilities, building profiles, price/tariff data, and phases. | Simulate schedules, inspect peaks, readiness and flexibility, compare strategies. | DESIGNED / PLANNED; [MAP §D5–D8] [JUDGEMENT] |
| Housing association | Choose a site-only or cost start and define the shared connection. | Import meter data, add resident charging demand and future phases. | Test what the supply can carry and compare managed cases. | PLANNED, not designed in map; [MAP §D6 `dep.housing`; §D15] [JUDGEMENT] |
| Consultant | Create or duplicate projects, import evidence, and choose the audience view. | Build and reuse client objects, maintain notes, assumptions, and scenarios. | Check, run, compare, export documents, and return to unfinished work. | DESIGNED / PLANNED; [MAP §0.4; §D13–D14; §F2] [JUDGEMENT] |
| Finance or sustainability specialist | Choose cost/CO₂ scope, period, method, and comparison fuels. | Enter prices, tariffs, paired costs, tax, subsidies, and emissions factors. | Inspect cash flow, break-even, sensitivity and CO₂, then export a model. | PLANNED / OPEN; [MAP §D8–D11; §F2] [JUDGEMENT] |
| Engineering analyst | Choose engineering view and a calibration/reference purpose. | Enter curves, factors, full loss maps, and source metadata. | Diagnose completeness, extrapolation, model status, and run fingerprint. | FINAL / WIP / OPEN; [MAP §B6–B9; §C10; §F2] [JUDGEMENT] |

## A0.3 Shared criteria

Each concept is scored from 1, weak, to 5, strong. Scores are judgements, not test results. [JUDGEMENT]

1. Predictability before entry. [JUDGEMENT]
2. Calm handling of more than 300 inputs. [MAP Parts B and D] [JUDGEMENT]
3. Starting at any of the five stage contracts. [MAP §D0] [JUDGEMENT]
4. Working for one fleet group and two hundred groups. [MAP §1; §B10] [JUDGEMENT]
5. Supporting client, OEM, and engineering views without separate project models. [MAP §0.4.10] [JUDGEMENT]
6. Trust, provenance, and auditability. [MAP §0.4.2–3; §F2] [JUDGEMENT]
7. Room for planned stages while showing honest unavailable states now. [MAP §A11; Part D] [JUDGEMENT]
8. Build effort for Bob working by hand. [JUDGEMENT]

---

## Concept 1: Guided routebook

**Kind.** A branching sequence asks one bounded question at a time, with a permanent route map of completed, current, skipped, and later steps. [JUDGEMENT]

```text
┌ Project · Save state · Check · Run ─────────────────────────────┐
│ ROUTE  Start ✓  Duty ✓  Vehicle ●  Conditions ○  Site —  Cost ○│
├──────────────────────────────────────────────────────────────────┤
│  Vehicle for “Urban refuse group”                               │
│  Where will its data come from?                                 │
│  ( ) Exact library truck  ( ) Class only  ( ) Enter it myself  │
│                                                                  │
│  What this choice will ask next                                 │
│  Library: configuration → range decisions → review              │
│                                             Back   Save & next → │
└──────────────────────────────────────────────────────────────────┘
```

**One-task walk-through.** A fleet owner chooses “work it all out,” names one duty group, selects “class only,” sees the unresolved class-data gaps, describes a typed route, chooses load and PTO branches, assigns a calendar, chooses weather and cab mode, reviews `check()`, and runs to Route energy. [MAP §G1; §D0; §E1–E4] [JUDGEMENT]

**Why it could work.** One question and a clear next action contain local complexity and make conditional branches explicit. [JUDGEMENT]

**Where it fails.** Experts must traverse many steps, comparing two reusable objects is awkward, and two hundred groups turn a route into repetitive navigation. [MAP §1] [JUDGEMENT]

**Cost to Bob.** Branch routing, resumable position, and many step variants require more stateful shell work than the other concepts. [JUDGEMENT]

**Main compromise.** A left route map improves predictability but can become a second navigation system beside browser-like Back and application menus. [JUDGEMENT]

---

## Concept 2: Indexed workbench

**Kind.** A stable project index names every work area and states its promise before entry; the centre shows one object sheet or decision sheet; an optional right drawer shows checks, assumptions, or help. [JUDGEMENT]

```text
┌ File Edit View Project Run Libraries Help · Project · Saved · RUN┐
├──────────────┬───────────────────────────────────────┬────────────┤
│ PROJECT INDEX│ Duty group: Urban refuse             │ CHECK (7)  │
│ Setup        │ What this sheet holds                 │ 2 missing  │
│ Duties (3)   │ ┌ Vehicle ─────────── Ready ┐         │ 4 defaults │
│  · Groups    │ │ Class-only · group 9      │         │ 1 wrong    │
│  · Routes    │ └───────────────────────────┘         │            │
│ Conditions   │ ┌ Route + stops ───── Ready ┐         │ Jump to →  │
│ Energy chain │ └───────────────────────────┘         │            │
│ Site         │ Load · equipment · schedule           │            │
│ Business case│ Latest route result: Not run          │            │
│ FINDINGS     │                            Review duty │            │
│  · Decisions │                                       │            │
│  · Route use │                                       │            │
└──────────────┴───────────────────────────────────────┴────────────┘
```

**One-task walk-through.** A consultant opens Duties, sees counts beside Groups, Vehicles and Routes, opens one duty group, replaces its vehicle reference, follows the persistent impact notice to Check, runs from Consumption, then opens Findings → Route energy without leaving the project frame. [MAP §1; §C0; §E5 rule 68; §F2] [JUDGEMENT]

**Why it could work.** The index exposes scope and status without displaying all fields; object sheets let shared things be edited once; decision sheets give results their own hierarchy. [MAP §D14; §F2] [JUDGEMENT]

**Where it fails.** The index can feel dense and object relationships need clear labels; novices may still want a suggested route through otherwise free navigation. [JUDGEMENT]

**Cost to Bob.** It needs a responsive three-region shell and a common sheet template, but most screens reuse those primitives. [JUDGEMENT]

**Main compromise.** Inputs and results are not forced into one timeline; a small “latest result” line can appear on an input sheet, but the authoritative result remains in Findings to prevent duplicate competing figures. [JUDGEMENT]

---

## Concept 3: Depot canvas

**Kind.** A spatial canvas shows a depot, routes, fleet groups, chargers, the connection, and stage outputs as linked nodes; selecting a node opens its inspector. [JUDGEMENT]

```text
┌ Project · Save · Check · Run ────────────────────────────────────┐
│ [Fleet 3]──uses──[Routes 5]──returns──┐                          │
│    │                                  ▼                          │
│ [Vehicles 4]                     [Depot]──[Grid]                  │
│    │                                  │                          │
│ [Energy]──[Battery]──[Sessions]──[Chargers]                      │
│                                        selected: Depot → panel   │
└──────────────────────────────────────────────────────────────────┘
```

**One-task walk-through.** A charge-point operator selects the Depot node, imports a load profile, links an existing Charger set, sees the Smart charging edge become unavailable, runs Charging, and follows the highlighted Grid result edge to peak and readiness findings. [MAP §D0; §D5–D7; §E5 rule 54] [JUDGEMENT]

**Why it could work.** Dependencies and stage skipping become visible, and the energy chain reads as a system rather than a form. [MAP §D0] [JUDGEMENT]

**Where it fails.** Maps, charts, graph nodes, tables, and controls would compete; phone use and keyboard navigation are hard; a canvas is poor for hundreds of stops or cost rows. [MAP §B3; §D9] [JUDGEMENT]

**Cost to Bob.** Pan, zoom, selection, linking, responsive fallback, and accessible alternatives create the highest build burden. [JUDGEMENT]

**Main compromise.** A canvas explains relationships but does not make exact data entry predictable enough to be the primary structure. [JUDGEMENT]

---

## Concept 4: Fleet ledger with drill-in

**Kind.** The fleet assignment ledger is the home of the model; columns show counts and reusable objects, while row detail opens in a lower pane and project-wide stages are separate ledgers. [JUDGEMENT]

```text
┌ Project · Save · Check · Run ────────────────────────────────────┐
│ FLEET LEDGER                              3 groups · 24 vehicles │
│ □ Group         Count  Vehicle    Route       State              │
│ □ Urban refuse     12  Class 9    Refuse A    2 missing          │
│ □ Winter refuse    12  Class 9    Winter A    Ready              │
│ □ Service van       2  Model X    Call-outs   1 wrong            │
├──────────────────────────────────────────────────────────────────┤
│ Selected rows (2): Apply vehicle · Apply schedule · Duplicate   │
│ Detail: Urban refuse → load | equipment | schedule | latest run │
└──────────────────────────────────────────────────────────────────┘
```

**One-task walk-through.** An operator pastes fifty groups, selects twelve rows, applies one schedule, opens the two exceptions, resolves missing references, and runs the fleet. [MAP §1; §B10 `fleet.count`; §D14] [JUDGEMENT]

**Why it could work.** Bulk fleet work, comparison, spreadsheet paste, and frozen identifiers are direct. [MAP §B3; §D6] [JUDGEMENT]

**Where it fails.** The ledger makes the fleet look like the whole project even for a cost-only or housing-association start, and dense columns recreate the risk of five opaque dropdowns per row. [MAP §D0; §D6 `dep.housing`] [JUDGEMENT]

**Cost to Bob.** The editable grid, selection model, paste validation, and narrow-screen alternative are substantial but bounded. [JUDGEMENT]

**Main compromise.** It is an excellent component inside another concept, but a weak application-wide information architecture. [JUDGEMENT]

---

## A0.4 Scorecard

| Criterion | Guided routebook | Indexed workbench | Depot canvas | Fleet ledger | Reason |
|---|---:|---:|---:|---:|---|
| Predictability | 5 | 5 | 2 | 3 | A route map or promise-bearing index says what comes next; canvas nodes and ledger columns need interpretation. [JUDGEMENT] |
| Calm with 300+ inputs | 5 | 4 | 3 | 2 | One-question steps are calm; sheets disclose by tier; an inspector or wide grid accumulates controls. [MAP Parts B and D] [JUDGEMENT] |
| Start at any stage | 4 | 5 | 5 | 2 | A free index and dependency canvas accept alternate contracts directly; a fleet-first ledger does not. [MAP §D0] [JUDGEMENT] |
| Fleet size 1–200 | 2 | 5 | 2 | 5 | The workbench can host a dedicated ledger; the routebook and canvas repeat or crowd. [MAP §1] [JUDGEMENT] |
| Three views | 4 | 5 | 3 | 3 | Sheet tiers can reveal fields in place while preserving object context. [MAP §0.4.10] [JUDGEMENT] |
| Trust and audit | 4 | 5 | 3 | 4 | The workbench can keep checks and provenance beside the active sheet without putting source prose beside every field. [MAP §0.4.2–3, 9] [JUDGEMENT] |
| Planned stages | 4 | 5 | 5 | 3 | The index can reserve stable homes with explicit availability states; graph nodes also extend well. [MAP Part D] [JUDGEMENT] |
| Bob build effort | 2 | 4 | 1 | 3 | Shared sheet templates are simpler than route orchestration, a graph editor, or making every task grid-native. [JUDGEMENT] |
| **Total / 40** | **30** | **38** | **24** | **25** | The total is a comparison aid, not user evidence. [JUDGEMENT] |

## A0.5 Kiro's recommendation: Indexed workbench

**Recommendation.** Use the Indexed workbench as the whole-tool structure. [JUDGEMENT]

**Problem it solves.** The permanent index gives every destination a one-line promise, status, and count before entry, while each sheet keeps one object or one decision question in focus. [JUDGEMENT]

**Feedback it answers.** It directly addresses Bob's requirement that “i should know what to expect from the pages before i go into them,” without hiding the model in one giant panel. [DOC `bob-feedback-log-ui-and-landing.md`, quote supplied in the 16 Nov brief; full log not yet read at this point] [JUDGEMENT]

**What it costs.** The left index consumes width and needs a list-first phone layout; shared objects also require explicit “used by” and copy-versus-update behaviour. [JUDGEMENT]

**Alternative considered.** The Guided routebook is calmer for a first-time single-fleet user, but it taxes repeat editing and bulk work. [JUDGEMENT]

### What the recommendation borrows

- Borrow the Guided routebook's optional **suggested next task**, but never block free navigation. [JUDGEMENT]
- Borrow the Fleet ledger as a dedicated **bulk mode** inside Duties, not as the whole application. [JUDGEMENT]
- Borrow the canvas's simple **stage dependency strip**, but render it as a non-interactive status explanation rather than a second navigation system. [JUDGEMENT]
- Keep a **route/depot map only where geography answers the active question**, not as the shell. [MAP §B2 `rt.map`; §D6 `dep.address`] [JUDGEMENT]

### What the recommendation gives up

- It gives up the routebook's guarantee that everyone sees every question in one prescribed order. [JUDGEMENT]
- It gives up the canvas's immediate picture of the whole energy chain. [JUDGEMENT]
- It gives up making spreadsheet users feel that every object is directly editable in one grid. [JUDGEMENT]

### Runner-up Bob could choose instead

The Guided routebook is the runner-up if initial self-service completion is more important than frequent expert editing and fleets above roughly a few groups. That fleet-size threshold is not evidence and must be tested rather than shipped as a rule. [JUDGEMENT]

A routebook implementation should still include an object library and a bulk fleet ledger; otherwise reuse and two-hundred-group work remain weak. [MAP §1; §D14] [JUDGEMENT]

## A0.6 First structural commitments for later specification

These commitments concern layout, not map items marked `OPEN`, `PROPOSED`, or `PARKED`. [JUDGEMENT]

| Commitment | Problem solved | Bob feedback answered | Cost | Rejected alternative | Basis |
|---|---|---|---|---|---|
| One permanent Project index, with one-line promises and status counts. | Users can predict a destination before opening it. | “i should know what to expect from the pages before i go into them.” | Less width for the sheet. | Unlabelled icon rail or top-level tabs. | [JUDGEMENT] |
| One sheet in the centre; core inputs never live only in the right drawer. | Details remain discoverable and do not become a pile of popups. | “not ... everything in just one pop up.” | More explicit sheets. | Modal-first editing. | [JUDGEMENT] |
| Checks, assumptions, and help share one optional context drawer. | Feedback stays near the work without becoming a second page tree. | “things hidden under the rug” and source clutter concerns in the brief. | The drawer cannot show all three contexts at once. | Permanent three-column dashboards. | [MAP §0.4.2, 9] [JUDGEMENT] |
| Duties are assignment cards by default and a ledger in bulk mode. | One group reads plainly; fifty groups remain workable. | “20 is wrong, 3 is wrong,” quoted in the brief. | Two presentations of one data model. | Five dropdowns in every default row. | [MAP §1] [JUDGEMENT] |
| Authoritative results live in a Findings book grouped by user question; input sheets show only a small latest-run reference. | Large figures, charts, and status no longer read as one sentence or compete with forms. | “results look merged because of poor visual hierarchy and bad alignment.” | One click between editing and deep result detail. | Duplicate full results beside every input. | [MAP §F2] [JUDGEMENT] |
| Stage status is explanatory, not navigation. | Modelled, user-supplied, skipped, planned, stale, and failed states remain legible without a second menu. | “maps, charts, texts, numbers and calendars must not fight.” | Stage changes need a dedicated Start-point command. | Clickable pipeline plus page navigation. | [MAP §D0] [JUDGEMENT] |
| Every planned stage has a stable index home and an explicit “Not available yet” sheet. | The structure does not jump when code arrives, and empty pages do not masquerade as results. | Empty and unpredictable pages described in the brief. | More visible future scope. | Hide all planned stages until release. | [MAP Part D] [JUDGEMENT] |
| Closed branch values are retained in a reversible dormant store and omitted from the run payload. | A branch switch never silently destroys typed work while Python receives only the active branch. | “nothing a user typed is silently lost.” | JSON/UI state needs dormant-value handling. | Clear on close or submit hidden values. | [MAP §0.4.7; Part E definition of closes] [JUDGEMENT] |

## A0.7 Gate 0 result

`concepts.md` contains four concepts that differ in interaction kind, one shared eight-criterion scorecard, a recommendation, a buildable runner-up, and explicit trade-offs. No old screen or PR #35 layout was read before this gate. [TEST manual document check, 2026-11-16] [JUDGEMENT]
