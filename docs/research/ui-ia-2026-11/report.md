# Where every input and result belongs in EV Scope, plus a landing page review

Research and design proposals for Bob. 14 Nov 2026. Branch `ui-ia-research-2026-11`, from `claude/ev-scope-site-wip`.

**How to read this.** Short sentences. Tables first. Every statement carries a tag: `[DOC]` project document, `[TOOL]` other tool's manual or site, `[VECTO]` VECTO manual or source, `[GUIDE]` design guidance, `[TEST]` my own check on the current build (screenshots in `audit/`), `[JUDGEMENT]` my own reasoning, `[OPEN]` not decided. Where I only saw a snippet or the first part of a page, I say so. Nothing here edits `website-wip/`, `src/` or engine code.

---

# Summary (one page)

## 1. Proposed input pages and popups

| Page | What it holds | Rows (main / popup / eng. / hidden) | Named popups |
|---|---|---|---|
| Project | Name, purpose of the project, run mode, brand-neutral flag. | 8 (8 / 0 / 0 / 0) | 0 |
| Fleet | The fleet table and, behind its cells, the five templates (vehicle, route, payload, equipment, schedule), stops, library picks. | 128 (54 / 62 / 7 / 5) | 15 |
| Depot and grid | Site, grid connection, access type, building load, growth, parking. | 19 (12 / 7 / 0 / 0) | 6 |
| Charging | Chargers, charging plan, ready-by, flexibility, what-if cases about failures. | 26 (6 / 20 / 0 / 0) | 8 |
| Weather | Location, weather year, wind, cab heating and cooling. | 25 (8 / 13 / 2 / 2) | 5 |
| Prices | Electricity, tariffs, diesel and other fuels, public charging. | 13 (6 / 7 / 0 / 0) | 4 |
| Costs | Ownership, finance, vehicle prices, service, wages, depot costs, sensitivity. | 21 (11 / 10 / 0 / 0) | 7 |
| Taxes, grants and CO₂ | Km-toll, diesel tax changes, subsidies, CO₂ factors. | 10 (6 / 4 / 0 / 0) | 3 |
| Tender (shown only for tender projects) | Buyer weights, score curves, minimums, the bids. | 9 (9 / 0 / 0 / 0) | 0 |
| Compare | Scenario levers (the same fields as on their home pages). | 2 (2 / 0 / 0 / 0) | 0 |
| Check and run | Missing values, sample and assumed values, the source list, Run. | 13 (0 / 0 / 0 / 13) | 0 |

Total: **274 inputs** in `inputs_register.csv`. 83 of the 254 inputs that a user would see have no field in today's demo (mostly planned functions). The Fleet page holds nearly half of all rows because the five templates live behind its cells (Question 1). Hidden rows are never typed; they are listed on Check and run and in the report.

Pages are the same names as in the demo, plus a **Tender** page that appears only for tender projects. Cab heating stays under **Weather**, as Bob decided. The year-8 guarantee is a **main field of the vehicle template** (not in a popup) and is repeated as a required value on Check and run.

## 2. Proposed result pages

| Result page | What it answers | Register rows |
|---|---|---|
| Overview | Verdict, four figures, six checks (year 8 is its own line), input context as small visuals, results per fleet row. | 16 |
| Energy | Energy per day and per km, component balance, monthly table, loss diagram, P50 / P90. | 12 |
| Battery | Installed against usable, usable at year 8, hardest day at year-8 capacity, winter at year 8, tender minimum, score curve position, passport values. | 15 |
| Charging | Chargers, sessions, schedule, strategies compared, robustness cases. | 10 |
| Grid and flexibility | Peak in A and kW, required connection, fee, lead time, FNA against BNA, capacity charge, flexibility. | 20 |
| Cost | Total, break-even, year by year, NPV, financing, sensitivity. | 15 |
| CO₂ | Per year, saved, grid path, life cycle. | 6 |
| Offers | Several bids scored with the buyer's weights (tender projects only). | 4 |
| Audit | Fingerprint, every standard value and assumption with source, model status. | 7 |
| Documents | The six documents. | 7 |
| Compare | Two runs side by side. | 2 |

Register: **114 results** in `results_register.csv`. The Overview carries input context as small visuals and does not repeat other pages.

## 3. Top 10 problems in the current build

| # | Severity | Problem | Evidence |
|---|---|---|---|
| 1 | major | 83 of 254 visible inputs in the register have no field in the demo (warranty years, battery replacement, tender page, Eloverblik, charger outage, fleet growth, ampere unit, weather location, library pick). | `inputs_register.csv` column `in_current_demo` `[TEST]` |
| 2 | major | The Fleet page shows a "What will be driven" table (driver runs). It is run planning, not an input. Bob: inputs must not show outputs. Borderline, because it is derived from inputs. | `audit/tool_1440x900_setup-fleet.png` `[TEST]` |
| 3 | major | Fleet table cells are cramped at 1440 px: dropdown text is cut ("City collection", "Fills up along t") and each cell has a separate "Edit" link under it. 8 actions per row (5 Edit, Stops, Copy, Remove). | same screenshot; row buttons listed in `audit/tool_audit_raw.json` `[TEST]` |
| 4 | major | On a phone the fleet table becomes a long list of label and value lines with no row grouping. A lone checkbox sits above the first row. | `audit/tool_390x844_setup-fleet.png` `[TEST]` |
| 5 | major | Danish header at 1440 px breaks: "EV Scope", "Hvem er det for", "Prøv demoen" wrap onto two lines. | `audit/site_1440x900_day_da_hero.png` `[TEST]` |
| 6 | major | Landing type has no scale: 17 different font sizes in the main sections, H2 headings at 38, 44, 40 and 44 px, 42 text elements at 10 px or smaller (30 at 10 px, 6 at 9 px, 6 at 7 px). | computed styles on `#top, #for, #depot, #demo, #documents` `[TEST]` |
| 7 | major | Legal pages still hold placeholders: [COMPANY LEGAL NAME], [CVR NUMBER], [STREET, POSTCODE AND CITY], [YOUR EMAIL]. Not publishable. | Privacy view text `[TEST]` |
| 8 | minor | Year 8 is on the Overview and Battery pages but not visible on the fleet row (the vehicle cell says "Group 4, battery sized by the tool"). | `audit/tool_1440x900_setup-fleet.png` `[TEST]` |
| 9 | minor | Weather has no location field; the station is a fixed text "Nearest to the depot". Inventory asks for a location. | `website-wip/src/model.js` `DEFS.wx` `[DOC]` |
| 10 | minor | Accessibility: axe 4.14.0 finds 1 serious `scrollable-region-focusable` on the Battery and Grid result pages, 1 serious `color-contrast` in the document fan, and 2 moderate landmark issues while the vehicle dialog is open. 19 controls on the Fleet page at 390 px are under 24 px (WCAG 2.5.8). | `audit/tool_audit_raw.json`, `audit/site_audit_raw.json` `[TEST]` |

More in Part F (the "Inputs and sources" page is 7,379 px long; the embedded tool does not follow the night theme; two near-duplicate site files in `out/`).

## 4. Top landing page changes

1. Show the five audiences **once**: a role chooser under the hero. Remove the second list in the header. Picking a role swaps the section below (title and image change with it).
2. One type scale and one spacing scale for the whole page (G7).
3. Pre-select the matching document in the document picker. The description stays under the fan.
4. Fix the Danish header wrap. Fill the legal placeholders.
5. Rewrite each block from the reader's side, with one sourced example per role. Copy in G4.
6. Demo preview: three screens, one slow cursor, one stop per screen, still frames for reduced motion.

## 5. Open choices for Bob

Twelve questions, each with options, are at the end of the report. The big ones: **Q1** Fleet page weight, **Q2** popup or side panel, **Q3** link or copy, **Q4** first-run start, **Q5** where the roles are listed on the landing page, **Q7** what to show as the year-8 default.

---

# Part A: master input register

Files: `inputs_register.csv` (23 columns, one row per input), `inputs_register.md` (grouped by page), `engine_args_map.csv` (every engine argument from Appendix A mapped to register ids), `inventory_coverage_check.csv` (every inventory row mapped to register ids).

**What went in** `[TEST]`:
- all 178 table rows of inventory sections 1 to 14 (placed: **178 of 178, unplaced: 0**; rule-based matching written by me, first match wins, so it proves a home exists, not that it is the best one `[JUDGEMENT]`);
- all 174 fields of the demo's `DEFS` (**174 of 174** have a register row, checked by script; `in_current_demo` holds the demo key);
- every engine function in Appendix A.1 and every planned function in A.2 (`engine_args_map.csv`);
- inputs seen in other tools that HDEV has no row for: 24 candidates in `inputs_register.md`, each with source;
- 16 conflicts between documents (also in `inputs_register.md`).

**Counts.** 274 rows. Status: built 76, designed 99, planned 83, open 16 `[DOC]`. Year-8 rows: 40 (guarantee, warranty, state-of-health curve, replacement, sizing rule, cab heating that drives winter, downtime cost, all tender minimums). `required` means "no default exists, so Run is blocked": 68 required, 22 optional with a default, 161 optional, 23 hidden.

**Defaults are copied, not chosen.** Where the register has a default it is the inventory's value with its tag. Where the inventory is silent it says `none` or `OPEN`. I did not invent any default.

**Three findings from building the register** `[JUDGEMENT]`:
1. Always-on PTO and departure time are asked twice in the inventory (pages 5 and 6; pages 1 and 2). The register asks once.
2. The year-8 value has three different numbers in project material: 70 % (demo sample, Rambøll 2023), at least 80 % (tender, as stated in Bob's brief), max 25 % loss (ARC 2022, so 75 %). The field must be required, with no default shown as fact.
3. VECTO derives the vehicle group from vehicle category, axle configuration and technically permissible maximum laden mass `[VECTO]` (manual, vehicle editor, General tab, first 7.5k characters read). HDEV asks the group directly. A user who does not know the group needs those three.

---

# Part B: master results register

Files: `results_register.csv`, `results_register.md`. **114 rows** (6 are candidates from other tools: marked `candidate`). Columns as in the brief. Sources for each row are in `source_of_requirement`: mostly `project-notes/claude_results-gap-analysis-2026-10-26.md` (gap analysis) and `claude_outputs-fna-bna-battery-passport-2026-10-28.md` (outputs note).

Year-8 results: usable at year 8, hardest day at year-8 capacity, winter at year 8, minimum usable kWh at year 8 for a tender, tender score position, predicted battery passport values, battery run-out year, the Overview check, downtime cost, and the offer-sheet guarantees. Each is on the Battery page, the Overview checks or the Offers page.

---

# Part C: how other tools organise inputs and results

Full table in `tool_comparison.csv` (18 rows, 12 columns, with links and what I read). Short version:

## What I read, and what I did not

| Source | What I read |
|---|---|
| VECTO manual (markdown in Bob's fork, 4.3.4-DEV of 10 Mar 2025) | First 5k to 7.5k characters of: main form, job editor, vehicle editor, auxiliary dialog, battery editor, calculation modes. Battery editor read in full. GUI form file names listed, **forms not opened** |
| VECTO releases page | Read. Official latest: **5.1.7, 27 Oct 2026** (5.1.6-RC 8 Oct, 5.1.4-RC 3 Sep). The fork is behind. The 5.1.x manual was **not opened** |
| PVsyst help | Project design index, array and system losses index, loss diagram: full. Product site not extractable. **Report layout not read** |
| SAM | Home page full. A 2020 SAM demo transcript (partial). Macros and parametrics: search snippets only |
| HOMER Pro | Navigating, Results, Library: full. Sensitivity pages: snippets only |
| PV*SOL | Navigation page overview and "System type, climate and grid": full. Homepage full |
| Dynamon, BetterFleet, Decade, Flowemo, Elento | Homepage text. Product UIs **not seen** |
| Geotab EVSA | User guide, first ~4k characters |
| EVI-Pro Lite, Chargepoly | Search snippets only |
| FASTSim, eFLIPS-depot, SpiceEV (Bob's forks) | One vehicle yaml; `cost_params.json`, `vehicle_types.json`, `default_settings.json`; `generate.cfg`, `vehicle_types.json`, `price_sheet.json` |
| NN/g (progressive disclosure, modal and nonmodal, dashboards), GOV.UK (check answers, question pages), IBM Carbon (modal), WCAG 2.5.8 | First ~4k characters of each |
| **Not reached** | Zeti, ElectricFleets/Sawatch, T3CO, Sunny Design. A tool named "ChargeSim" did not turn up in the first search. NN/g accordions, forms and data tables; Stephen Few; Carbon data table, form, notification and empty state. Listed under "Bob to fetch" |

## Per tool (one short section each)

**VECTO** `[VECTO]`. A main form with a job list and an options tab. Each physical component has its own editor and its own file: vehicle, engine, gearbox, battery. The job file points to them. In Declaration mode many parameters are set by the tool and locked. In Engineering mode they open. Auxiliary technologies sit in their own dialog. Results are files: summary (.vsum), modal (.vmod), XML report.
*Lesson:* "locked in declaration" is the clean way to show standard values. One editor per component matches "one named popup per topic".

**PVsyst** `[TOOL]`. Project (site and weather) holds variants. Each variant gets a system definition. A first run uses reasonable defaults. Refinement comes second, in a panel named "Detailed losses". Warnings are orange (can run) or red (cannot). The loss diagram is in every report. Each loss is a percentage of the previous quantity, so losses do not add up.
*Lesson:* defaults first, refine later; orange and red status; a popup named after its content; variants as scenarios. This is the closest model.

**SAM** `[TOOL]`. A page list on the left per technology (Location and Resource, System Design, Financial Parameters and others). Shading is a month-by-hour table.
*Lesson:* a visible page list is the Setup sub-menu. A month-by-hour table is a good shape for own prices or a grid cut window.

**HOMER Pro** `[TOOL]`. Toolbar: Design, Results, Library. Welcome page offers a Setup Assistant. Library entries that ship with the tool are read-only; you copy one into your own library, then edit. Results are two tables (sensitivity cases, optimisation results) with a "Calculation Report" that lists why a run failed.
*Lesson:* copy-then-edit answers "link or copy". Setup Assistant is the guided first row.

**PV*SOL** `[TOOL]`. A fixed list of navigation pages in workflow order. The system type you pick switches pages on or off. Four message levels at the bottom (information, warning, no simulation, error). A Presentation page prints a customer presentation.
*Lesson:* a project purpose choice that switches the Tender page on. Message levels map to missing, assumed, ok.

**Dynamon, BetterFleet, Decade, Flowemo** `[TOOL]`. I saw home pages only. Dynamon shows a starting price and names customers. Decade is a provider (it sells grid power and charging), so it is not neutral. Flowemo shows calculations updating as you edit a map layout and shares a project with or without prices.
*Lesson:* "share with or without prices" is the client view hiding OEM fields.

**Geotab EVSA** `[TOOL]`. Four sections: Vehicles to Assess, EV Models, Charging Locations, Preferences. A vehicle passes if range, charging viability and lifetime cost all pass.
*Lesson:* three plain conditions per vehicle make a clean verdict. Row filters suit a 50-row fleet table.

**EVI-Pro Lite, FASTSim, eFLIPS-depot, SpiceEV** `[TOOL]`. EVI-Pro Lite is one short form (location, number of vehicles, daily distance, temperature, vehicle type, charging shares, charging level, time of day) from a DOE news item. The others are libraries with JSON or YAML inputs. SpiceEV puts option comments in its config file. eFLIPS has grid-connection cost by voltage level and battery lifetime and cost per kWh.
*Lesson:* the project JSON can follow SpiceEV: plain keys with a comment per key.

**COWI sheet** `[DOC]`. Not in the repo. About 80 line items on one sheet (gap analysis section 3.5). Bob to fetch.

**Design guidance** `[GUIDE]`. NN/g: show a few important options first and put advanced ones on request (progressive disclosure); modal dialogs interrupt and block. Carbon: modals only for short, non-frequent tasks; if a user repeats a task, make it completable on the page. GOV.UK: a check-your-answers page before submitting. WCAG 2.5.8: targets at least 24 by 24 CSS px unless spaced. NN/g dashboards: length and position carry numbers.

## Comparison (how each tool answers the eight questions)

| | Navigation | Grouping | Hides detail | Defaults | Library | Many items | Results | Compare |
|---|---|---|---|---|---|---|---|---|
| VECTO | main form plus editors | by component | editors, aux dialog, locked in declaration | predefined and locked | component files | axle table | files .vsum .vmod XML | job list |
| PVsyst | project, variant, system, simulate | by thing | "Detailed losses" | defaults first, orange / red | component DBs | module layout | report with loss diagram | variants |
| SAM | left page list | by category | option dialogs | not seen | weather library | month-by-hour table | graphs, data tables | cases |
| HOMER | Design / Results / Library | by role | Library, Setup Assistant | library defaults | copy then edit | search space | two tables, calc report | sensitivity |
| PV*SOL | workflow pages | by step | options dialogs | project status panel | product DB | n/a | results then presentation | n/a |
| Geotab EVSA | four sections | by step | filters | country defaults | EV models | filtered list | verdict per vehicle | new assessment |


---

# Part D: the input information architecture (proposal)

Bob's tests: "i should know what to expect from the pages before i go into them"; "20 pages is not right and 3 is not right"; not "everything in just one pop up"; things belong where they physically belong `[DOC]` `bob-feedback-log-ui-and-landing.md` B2, B5, B10.

## D1. Placement rules (numbered, so Bob can check any field against them)

| Rule | Text | Why (evidence) |
|---|---|---|
| R1 | An input goes on the page of the **thing it describes** (`depends_on` in the register: vehicle, body, battery, route, stop, load, shift, depot site, grid connection, weather, market, company, tender, scenario). | Bob: cab heating and the weather `[DOC]` B10; VECTO groups by component `[VECTO]`; PV*SOL by step `[TOOL]` |
| R2 | A value most users leave at a **sourced default** goes in a **named popup** on that page. | PVsyst "Detailed losses" `[TOOL]`; NN/g progressive disclosure `[GUIDE]` |
| R3 | A value only an OEM or engineer can give goes in the **OEM side** (greyed for clients) or the **engineering view**. Physics names (Crr, CdxA, theta_red) appear only in the engineering view. | Bob's Oct rule `[DOC]` B13; VECTO locked declaration fields `[VECTO]` |
| R4 | A **choice that changes which other inputs appear** stays on the page, never in a popup. The dependent fields show directly under it. | Bob: not everything under the rug `[DOC]` B2; PV*SOL system type switches pages `[TOOL]` |
| R5 | A **per-stop, per-hour, per-year or per-bid** value goes in a table, not in single fields. | SAM month-by-hour table `[TOOL]`; inventory section 2 `[DOC]` |
| R6 | A popup holds **one topic**, is **named after what it holds**, has about 8 fields or fewer, and is **one level deep**. | Bob: "Tyres", not "Advanced" `[DOC]` B7; Carbon: modals sparingly `[GUIDE]` |
| R7 | **Nothing required to run hides in a popup** unless its button shows a red "N needed". | Bob: missing required field is red and blocks Run `[DOC]` B13 |
| R8 | Constants and lookups are **hidden** (`defaults.py`), never typed, and listed in the report. | Architecture rule 9 `[DOC]` |
| R9 | Anything repeated per vehicle type, route, payload, equipment or shift is a **template** reached from the fleet table. No Templates page. | Bob 13 Nov `[DOC]` B9 |
| R10 | Input pages never show results. | Bob `[DOC]` B11 |
| R11 | Values from outside (market, regulation) live on market pages (Prices, Taxes). Values the company owns live on Costs. | `[JUDGEMENT]` |
| R12 | The year-8 guarantee is a **main field**, required, repeated on Check and run and on the Battery result page. | Bob 14 Nov `[DOC]` B12 |
| R13 | No source text beside fields. A mark only (D7). Sources live in the report and on Check and run. | Bob `[DOC]` B3 |

Every register row cites the rule in its `reasoning` column.

## D2. The page list

| Page | What it holds | Rows (main / popup / eng. / hidden) | Named popups |
|---|---|---|---|
| Project | Name, purpose of the project, run mode, brand-neutral flag. | 8 (8 / 0 / 0 / 0) | 0 |
| Fleet | The fleet table and, behind its cells, the five templates (vehicle, route, payload, equipment, schedule), stops, library picks. | 128 (54 / 62 / 7 / 5) | 15 |
| Depot and grid | Site, grid connection, access type, building load, growth, parking. | 19 (12 / 7 / 0 / 0) | 6 |
| Charging | Chargers, charging plan, ready-by, flexibility, what-if cases about failures. | 26 (6 / 20 / 0 / 0) | 8 |
| Weather | Location, weather year, wind, cab heating and cooling. | 25 (8 / 13 / 2 / 2) | 5 |
| Prices | Electricity, tariffs, diesel and other fuels, public charging. | 13 (6 / 7 / 0 / 0) | 4 |
| Costs | Ownership, finance, vehicle prices, service, wages, depot costs, sensitivity. | 21 (11 / 10 / 0 / 0) | 7 |
| Taxes, grants and CO₂ | Km-toll, diesel tax changes, subsidies, CO₂ factors. | 10 (6 / 4 / 0 / 0) | 3 |
| Tender (shown only for tender projects) | Buyer weights, score curves, minimums, the bids. | 9 (9 / 0 / 0 / 0) | 0 |
| Compare | Scenario levers (the same fields as on their home pages). | 2 (2 / 0 / 0 / 0) | 0 |
| Check and run | Missing values, sample and assumed values, the source list, Run. | 13 (0 / 0 / 0 / 13) | 0 |

What each page does **not** hold is stated at the top of its wireframe. Bob already rejected a separate Assumptions page, a separate Templates page and cab heating under the vehicle: none of them appear. `[DOC]` B4, B9, B10.

Where the things Bob named go:
- **Fleet table:** Fleet page.
- **Five template types:** Fleet page, behind the cells.
- **Stop table:** Fleet page, "Stops" on a row (D5).
- **Vehicle library (EEA data) and charger library:** vehicle library pick is in the Vehicle template (source = library); charger library pick is in Charging (`chg.library`).
- **Scenarios:** Compare (the levers are the same fields as on their home pages).
- **Run check:** Check and run.

## D3. Outlines and wireframes

One wireframe per page in `wireframes/`, built from the register. Open them in any browser; no external requests (checked: 0 requests).

| Page | File |
|---|---|
| Project | `inputs-project.html` |
| Fleet (table, first-run state, what opens behind each cell) | `inputs-fleet.html` |
| Fleet, vehicle template panel (year-8 field shown) | `inputs-fleet-vehicle-panel.html` |
| Depot and grid | `inputs-depot.html` |
| Charging | `inputs-charging.html` |
| Weather (with cab heating) | `inputs-weather.html` |
| Prices | `inputs-prices.html` |
| Costs | `inputs-costs.html` |
| Taxes, grants and CO₂ | `inputs-tax.html` |
| Tender | `inputs-tender.html` |
| Check and run | `inputs-check.html` |

Each wireframe lists sections in order, main fields, conditional fields (dotted bar and "shows when"), named popups with field counts (a heavier border when a popup holds a required value), tables, and an "empty / first-run" note. Page leads and popup names are in the register (`popup_name`). Engineering and hidden counts are shown as one grey line per section.

**Vehicle template.** It has 10 named popups, grouped under four small headings so it does not read as a wall of buttons: *Chassis* (Trailer and wheels, Air drag and size, Tyres), *Powertrain* (Drivetrain, Braking energy), *Battery* (Battery details, Battery voltage and resistance, Battery ageing, Size the battery), *On-board systems* (On-board systems). Main part of the panel: vehicle and body fields, battery mode, installed battery, **guaranteed usable capacity at year 8**.

## D4. Templates and the fleet table

**How a user works without a Templates page.** Each fleet row has five cells. Each cell is a dropdown plus a one-line summary. "Edit" opens the template panel. "Save as my own" copies what was just typed into the library under a name. VECTO templates are pre-filled and locked until copied `[DOC]` E.

**Link or copy** (Bob decides; Question 3).

| Option | What happens on editing a template used by several rows | Evidence |
|---|---|---|
| A. Always linked | All rows change. A "Make a copy" button exists (today's demo). | VECTO: shared files edited in place `[VECTO]` |
| B. Ask once | Header says "Used by N rows". Save asks: "Change for all N rows" (default) or "Only this row" (makes a copy). | HOMER copies before editing `[TOOL]`; `[JUDGEMENT]` |
| C. Always copy on edit | The edited row gets its own copy. Nothing else changes. | PVsyst "Save as" for variants `[TOOL]` |

**Kiro's recommendation: B.** It avoids the silent surprise of A and the silent drift of C. It costs one question per edit of a shared template.

**Getting started without building five templates** (Question 4).

| Option | What the user does | Cost |
|---|---|---|
| A. Start from a sample | Loads the sample project (today). | Easy, but the user still has to replace everything. |
| B. Guided first row | One row with six questions: vehicle group, distance per day, stops, return time, count, payload. The five templates are created and named silently, with sourced standard values. | Needs the parser to build five templates from six values. |
| C. Describe your fleet | The assistant fills the first row from words or a spreadsheet. | Assistant is planned, not built. |

**Kiro's recommendation: B, with A and C offered next to it.** PVsyst starts with a minimal set and defaults and refines later `[TOOL]`; HOMER offers a Setup Assistant `[TOOL]`.

**Table at 10+ columns and 50 rows.** On desktop: sticky header and first two columns, filter by group name, select all matching, bulk apply (route, payload, schedule, vehicle, equipment) once. Cells show a short summary and keep "Edit" next to the dropdown (today it is under it and far from it). On a phone: each row becomes a card with count, group, five summary lines and an "Edit" under each. `[JUDGEMENT]`, from `audit/tool_390x844_setup-fleet.png` where the list has no card boundary.

**Move "What will be driven" to Check and run.** It is run planning, not an input (rule R10).

## D5. The stop table

Today the demo already has it: a popup with 400 rows and the columns Stop, From the depot (km), Time at the stop (s), Payload after (t), PTO works. `[TEST]` (`audit/tool_1440x900_stops-popup.png`).

| Source | Distance and road type | Stop time | Payload per stop | PTO per stop |
|---|---|---|---|---|
| VECTO cycle | locked | editable | editable | editable |
| Typed | editable | editable | editable | editable |
| GPS log | locked | locked | editable | editable |
| Describe it (planned) | like typed | like typed | editable | editable |

`[DOC]` inventory section 2 (locks). The inventory's PTO-per-stop is stated for all sources in section 6.

Proposal: open it as a **full-height panel**, not a small popup (400 rows). Show a locked cell with a small lock mark and a tooltip "From the VECTO cycle. Copy the route to edit." Tools for 400 stops: filter (for example only stops with PTO), select a range by typing "12 to 40", "apply to all" and "apply to range" for stop time, payload and PTO, paste from a spreadsheet, and a one-line summary strip above (stops, total stop time, payload at start and end). On a phone: a list, one stop per line, range selection by two number fields. Decisions for the panel type are in Question 2.

## D6. Client view, OEM view, engineering view

| View | Shows | How to switch |
|---|---|---|
| Client | All main fields. OEM-only fields greyed with a lock. | Segmented control "View" in the header |
| OEM | Same pages. OEM-only fields editable (chemistry, state-of-health curve, OCV and resistance tables, loss maps, air-drag file, regeneration limits, bids on the Tender page). | same |
| Engineering | Adds physics names (Crr, CdxA, theta_red, J_rotor) as second labels and the engineering-only rows (factors, constants, Kt). | same |

Library picks prefill the fields the library knows (tag LIB). Each prefilled field becomes an **editable copy**; an edited field turns blue with a reset (existing rule `[DOC]` B13). The register's `who` column says who supplies each value.

## D7. Source marking (Bob wants no source text beside fields)

| What it is | Mark on the field | In the report |
|---|---|---|
| Standard value (EU rule, VECTO, library) | none (the quiet state) | Source list: value, unit, source, date |
| Sample value | grey asterisk | listed as sample |
| Assumption | grey asterisk | listed as assumption with reason |
| NO SOURCE (placeholder) | grey asterisk, and the result is labelled "placeholder" in the report | listed in a separate "No source" block |
| Your value | blue text and a Reset link | listed as "your value" |
| Missing and required | red ring, Run blocked, popup button shows "N needed" | not applicable |
| OPEN (decision not made) | grey asterisk | listed as open |

The full source list lives in three places: Check and run (count by mark, full list), the Audit result page, and the report section "Assumptions and sources". The demo already uses most of this `[TEST]`. What I add: NO SOURCE is separated from assumption in the report, because the inventory insists NO SOURCE values "must not be shown as fact" `[DOC]`. Question 10.

## D8. Tree test on paper

40 tasks in `tree_test.csv`. This is **my own paper test** `[JUDGEMENT]`, not a test with users. For each task: where it lands under the proposal and in the current demo, and whether it is found on the first try from page names alone.

| | Proposal | Current demo |
|---|---|---|
| Found first try ("yes") | 28 of 40 | 21 of 40 |
| Might need two guesses ("maybe") | 12 | 10 |
| Partly in the demo | n/a | 2 |
| Not in the demo (not built) | n/a | 7 |

Tasks that probably need two guesses under the proposal: "say the battery guarantee is 75 % at year 8" (nobody expects battery under Fleet), "upload my GPS log", "say the body has its own electric motor" ("PTO" is jargon), tyres, vehicle height, air-drag file, battery offered, "Saturdays at half", "shift start 05:00" (Project or Fleet?), "km-toll" (Prices or Taxes?). The pattern: **anything inside a vehicle, route or equipment template needs the user to know that those live under Fleet**. Mitigation (a search box in the header, summary lines on the fleet row that show the year-8 value, and the links from Check and run). This is a real weakness of "no Templates page" and is why Question 1 exists.

## D9. Two alternative structures, and the recommendation

| | Structure | Good | Bad |
|---|---|---|---|
| **A (recommended)** | By thing: Project, Fleet, Depot and grid, Charging, Weather, Prices, Costs, Taxes, Tender, Check | Same names as today; predictable for market and site values; matches how tools like VECTO and PV*SOL group | Fleet is heavy (128 rows behind it) |
| B | By workflow step (GOV.UK style): Who you are, Your vehicles, Your routes, Your depot, Your prices, Check | Easy for first-timers; one thing per page | Many small pages; re-entry means walking steps; vehicle and route templates still need a table |
| C | By audience: separate input sets for fleet owner, municipality, housing, OEM, CPO | Each user sees only what they need | Duplicates fields; harder to keep one engine; "who am I" decided before they can start; the OEM and client views already cover most of the difference |

**Kiro's recommendation: A, plus the guided first row and a header search.** Reason: Bob asked for pages he can predict by name; A keeps today's names; B and C trade that away. `[JUDGEMENT]`

---

# Part E: the results information architecture (proposal)

## E1. Result pages

| Result page | What it answers | Register rows |
|---|---|---|
| Overview | Verdict, four figures, six checks (year 8 is its own line), input context as small visuals, results per fleet row. | 16 |
| Energy | Energy per day and per km, component balance, monthly table, loss diagram, P50 / P90. | 12 |
| Battery | Installed against usable, usable at year 8, hardest day at year-8 capacity, winter at year 8, tender minimum, score curve position, passport values. | 15 |
| Charging | Chargers, sessions, schedule, strategies compared, robustness cases. | 10 |
| Grid and flexibility | Peak in A and kW, required connection, fee, lead time, FNA against BNA, capacity charge, flexibility. | 20 |
| Cost | Total, break-even, year by year, NPV, financing, sensitivity. | 15 |
| CO₂ | Per year, saved, grid path, life cycle. | 6 |
| Offers | Several bids scored with the buyer's weights (tender projects only). | 4 |
| Audit | Fingerprint, every standard value and assumption with source, model status. | 7 |
| Documents | The six documents. | 7 |
| Compare | Two runs side by side. | 2 |

Mapped to the questions each reader asks: fleet owners and OEMs go Overview, Battery, Cost; municipalities go Battery, Offers, Cost; housing associations go Grid; CPOs and grid companies go Grid and Charging. The Flexibility rows (up and down per hour, products, aggregator, pilot terms, V2G, hours) are a **section on Grid**, not a page of their own, so no page is thin `[DOC]` C1 (Bob: some pages were empty).

Where the named results go:

| Result | Page and level |
|---|---|
| Energy balance (VECTO split) | Energy, chart: horizontal waterfall |
| Monthly balance table (PVsyst style) | Energy, table |
| Loss diagram | Energy, chart: flow diagram (PVsyst convention: each loss is a percentage of the previous quantity) |
| P50 / P90 across weather years | Energy, range band on the monthly line |
| **Year-8 checks** (hardest day at year-8 capacity, winter at year 8, minimum usable kWh at year 8, margin, passport values) | **Battery**, with one check line on the Overview |
| Charging sessions table, robustness cases | Charging |
| Grid in A and kW with fee and lead-time band, FNA against BNA | Grid and flexibility |
| Flexibility products | Grid and flexibility, section |
| Cost year by year, NPV, sensitivity | Cost |
| CO₂ including life cycle | CO₂ |
| Offer sheet (bids scored with the buyer's weights) | Offers (tender projects only) |
| Audit block | Audit (today called "Inputs and sources") |

## E2. Hierarchy per page

Every results page follows the same four steps, drawn in `wireframes/results-overview.html`, `results-battery.html`, `results-grid.html`, `results-cost.html`:

1. **Page name** (26 px, semibold).
2. **One status line** with a mark and a sentence (17 px). The sentence says the answer, not the topic.
3. **Headline figures**: 3 or 4, in a row. Label above (12 px, grey), value (30 px), unit beside it (14 px, grey), one note line below (12 px). Figures answer a question; they are not decoration.
4. **Sections** (17 px) with a one-line subtitle, then a table or a chart.

Alignment: text left, numbers right, units in the column header not in the cells, one decimal rule per column, thousands separated, labels never far from their value (Bob 26 Oct: label, value and unit on one line `[DOC]`). Pass and fail as a mark plus a word, never colour alone (WCAG 1.4.1 `[GUIDE]`, not re-read here). Bars that only repeat the number beside them are removed `[DOC]` C3.

**Why this answers Bob's "looks like a sentence, not results with million krona value".** Today's Overview already has the four-figure band `[TEST]` (`audit/tool_1440x900_result-ov.png`). What it lacks is a scale that makes a million-krona value look different from a label: the proposal fixes sizes, right alignment and a single status line. Cost: one consistent scale to maintain.

## E3. The Overview

Shows: the status line, four headline figures (battery, chargers, depot peak, saving), six checks (year 8 its own line), **input context as small visuals** (payload along the route, shift and charging window on a 24-hour bar, temperature range of the weather case, connection against building load), and the fleet table. It must not repeat: chart series that live on other pages, per-check bars, long tables.

## E4. Charts: question and why

| Chart | Question | Type and why |
|---|---|---|
| Hardest day against battery (new and year 8) | Does the need stay under the limit? | bars against two limit lines: one comparison, same axis |
| Component energy balance | Where does the energy go? | horizontal waterfall: parts add to a total |
| Loss diagram | Where are the losses? | flow diagram: PVsyst convention |
| Load across the hardest day | Is there room on the connection? | step line with the connection as a limit line |
| State of charge on return | How empty do trucks come home? | strip per month: a distribution, many days |
| Battery against payload | What do I give up in load? | scatter: two quantities |
| Cumulative saving | When do I come out ahead? | one line with a zero line |
| Cost by line | Where does the money go? | sorted horizontal bars: parts of a whole |
| Sensitivity | What matters most? | tornado: ranks inputs by effect |
| Grid factor path | How does the grid get cleaner? | line over years |
| **No chart** | usable kWh at year 8, minimum for a tender, break-even, NPV, fee, lead time, connection size | a number says it |

## E5. The report and the six documents

Order for the **feasibility report** (PVsyst-style; PVsyst's own report order was not read, so this follows the table in the gap analysis `[DOC]` section 2 and my reading `[JUDGEMENT]`):
1. Project summary (fleet, depot, weather source and year, engine version).
2. System parameters (vehicle, battery nominal and usable, drivetrain, chargers, connection).
3. Assumptions and sources (every standard value and assumption, with its mark).
4. Main results (the four figures, six checks).
5. Monthly balance table.
6. Loss diagram.
7. **Year-8 section** (usable at year 8, hardest day, winter at year 8, margin, tender minimum).
8. Charging (sessions, strategies, robustness).
9. Grid (A and kW, fee, lead time, FNA against BNA).
10. Cost (year by year, NPV, sensitivity).
11. CO₂ (including life cycle).
12. Audit block (fingerprint, model status, decisions stated, hold-back notice).

The other five documents:

| Document | Fields, in order | Source of the field list |
|---|---|---|
| Grid connection application | Address; desired power; connection type (FNA, BNA, TFL); desired commissioning date; grid services yes or no and which; supporting load curve; ampere figures | Radius screening needs `[DOC]` doc-findings §2 |
| Tender annex | Usable battery at year 8 in winter; route energy in winter; charging power window (for example at least 150 kW between 10 and 75 %); ready-by; crane and compactor together; guarantee values; the buyer's score curve position | Outputs note; tenders `[DOC]` doc-findings §4, §6 |
| Financial model | Year-by-year cash flow; financing; residual; NPV with year 1 discounted one period; sensitivity | Vejdirektoratet NPV template `[DOC]` §1 |
| Grant application data | Trucks charging daily; number and power of chargers; budget lines (units, unit price, total, note) excl. VAT; lease yes or no and term; NPV of lease against diesel | Vejdirektoratet form `[DOC]` §1 |
| Client presentation | The decision; cost and saving; risks (year 8, winter, grid lead time); next step | Bob `[DOC]` C4 |

Pool closed 30 Sep 2026 for Vejdirektoratet `[DOC]`; the German scheme is the live alternative named in the register.

## E6. Compare runs and scenarios

Compare shows two runs side by side. **Top:** the inputs that changed (name, old, new), only those. **Below:** results with the difference, for the headline figures and the six checks. A third run adds a column. Scenario levers are the same fields as on their home pages; on Compare you only pick which to vary (fleet size, charging plan, price level, weather year, ownership years `[DOC]` inventory 13). A scenario is base plus a list of changes; the base is never overwritten. HOMER's Sensitivity Cases table (one row per case) is a model for several-value levers `[TOOL]`. PVsyst "Save as" with descriptive names is the model for naming runs `[TOOL]`.

---

# Part F: audit of the current build

**How it was run** `[TEST]`. Headless Chromium (Playwright's headless shell, Chromium 1232 build) driven by `playwright-core`. Viewports 1440×900, 1280×800, 390×844. The landing page was run in day and night themes and in English and Danish (12 combinations). The tool (`out/ev-scope-tool.html`) was audited standalone at the 3 viewports; it has no night theme of its own, so day only. Keyboard test, focus-trap test and reduced-motion test were run on the tool at 1440 px and on the site. Accessibility: **axe-core 4.14.0**, rule sets WCAG 2 A and AA, 2.1 AA, 2.2 AA and best practice. Not done: screen reader test, zoom to 400 %, axe in night theme, Danish tool UI (the tool is English only in the build; the site translates to DA, DE, NL). 124 screenshots in `audit/`. Raw numbers in `audit/tool_audit_raw.json` and `audit/site_audit_raw.json`. Scripts are not committed (kept out of the repo on purpose; listed under "Choices I made").

Bob's pitfall list: no claim below is without a file.

## F1. Against Bob's feedback log, line by line

Reference numbers are those of `bob-feedback-log-ui-and-landing.md`.

| Line | Bob's point | Verdict | Evidence |
|---|---|---|---|
| A1 | Serious industry tool, not websitey | partly met `[JUDGEMENT]` | Clean, light, IBM Plex; `tool_1440x900_result-bat.png` |
| A2 | Classic SaaS layout, top menu with icons, Run button, collapsible assistant | met | `tool_1440x900_setup-fleet.png`: Setup, Results, Compare, Documents, Run, Assistant |
| A3 | Parking-sign blue, light surfaces, subtle neumorphism, no yellow, logo not redrawn | met for colour, no yellow seen; **logo not compared with the original asset** | same screenshots |
| A4 | UI is a dumb form | cannot be tested from the UI: the demo runs a JavaScript stand-in model (build map) `[DOC]` | `current-build-map-2026-11-14.md` |
| B1 | Too many fields at once, operations and route separate and confusing | partly met | Fleet has route and operations in one table; the vehicle dialog still has 12 fields on its main part (`audit/tool_audit_raw.json` `dialog1`) |
| B2 | Do not over-correct into one tab or one popup | partly met | Popups are per topic (8 in the vehicle template) but the whole fleet logic sits on one page |
| B3 | No source or assumption text beside fields | met | small asterisk, legend at the bottom of the dialog (`tool_1440x900_fleet-template-popup.png`) |
| B4 | No separate Assumptions page | met | Sub-menu has none |
| B5 | Predictable pages | partly met | paper test: 21 of 40 tasks found first try; 10 may need two guesses (`tree_test.csv`) |
| B6 | All inputs must exist | **not met** | 83 of 254 register inputs have no field |
| B7 | Named popups, not "Advanced" | met | Trailer and wheels, Air drag and size, Tyres, Drivetrain, Braking energy, Battery details, Battery voltage and resistance, On-board systems |
| B8 | The fleet table | met | `tool_1440x900_setup-fleet.png` |
| B9 | No Templates page | met | Sub-menu has none |
| B10 | Things belong where they physically belong | partly met | Cab heating is under Weather (met). Weather has no location field |
| B11 | Inputs must not show outputs | partly met | "What will be driven" on the Fleet page |
| B12 | Year-8 check never dropped | met in the demo, weak as an input | Main field in the vehicle dialog; Overview check; Battery page. Sample value 70 % marked with an asterisk. No warranty years, no replacement, no tender minimum |
| B13 | Label, value, unit on one line; edited value blue with reset; missing red and blocks Run; engineering view; OEM-only greyed | partly met | First three seen (`...fleet-template-popup.png` shows Reset links and the run line "N values needed"). **Engineering view toggle and OEM greying not found in the header**; `ui.js` has an `enG` state but I did not find a control `[TEST]` |
| C1 | Some pages empty, some redundant | partly met | Result pages are 895 to 1,710 px tall, none empty; "Inputs and sources" is 7,379 px |
| C2 | Poor hierarchy, results look merged | partly met | Four-figure band and status line exist (`tool_1440x900_result-ov.png`, `result-bat.png`); figures and tables mostly aligned |
| C3 | Overview carries input context as visuals; charts too high level (no component split, no monthly balance, no confidence band) | **not met** | Overview has figures, checks and a table, no input visuals. Energy has a 3-part split (driving 82, on-board 25, body equipment 60 kWh in the sample) and a monthly bar chart, no VECTO-style component balance, no monthly table, no P50 / P90 (`tool_1440x900_result-en.png`) |
| C4 | Six documents are core | met | Documents page (`tool_1440x900_documents.png`) |
| D1 | Keep day/night, payload image, chargers that change, report types | met in build map; images seen in `site_1440x900_day_en_hero.png`; pinned story captured in `site_1440x900_day_en_story-*.png` | |
| D2 | No cursor-following tiles | met (not seen) | no tile hover effect seen |
| D3 | Clear what it sells | partly met | One line under the headline says "Battery, charger and grid sizing for electric fleets, worked out from your own routes." Plain, but "Scope before you sign" does not say it |
| D4 | Demo preview: smooth, every tab but not overwhelming | partly met | Three screens (fleet, overview, cost); cursor behaviour not recorded here |
| D5 | Personalisation: one step to my part | partly met | "Who it is for" is the second section (top at about 970 px, one screen below the hero); four tabs, one of which is "Truck makers and charge operators" (two audiences in one tab) |
| D6 | Framing from their point of view | partly met | Role tabs ask three questions each; the sample example is the same style |
| D7 | Hierarchy: the title stays while cycling through roles | partly met | H2 "Who it is for" stays; the H3 "For fleet owners" and image change (`site_1440x900_day_en_for-tab*.png`) |
| D8 | Not "you get this document" | partly met | Picker with tabs and arrows; no role preselect |
| D9 | Customer-facing, not jingle | partly met | Page is short (676 words) and plain `[TEST]` |
| D10 | Jargon, hero paragraph, audiences listed twice, "documents you can take away" | partly met | Hero is 26 words including buttons; audiences appear in the header ("Who it's for") and as tabs; no "take away" block found |
| D11 | Planning tool, not an operator | met | No wording about operating charging seen in the sections read |
| D12 | No invented numbers; samples labelled | met | "Sample case with illustrative figures" under each example |

## F2. Heuristic review (Nielsen's ten)

| # | Where | What | Severity | Rule broken | Evidence |
|---|---|---|---|---|---|
| 1 | Setup > Fleet | 8 actions per row (5 × Edit, Stops, Copy, Remove) in a 1440 px row; Edit sits under the dropdown, not beside it. Heuristic 8, minimalist design | minor | R9 (templates reached from cells) | `tool_1440x900_setup-fleet.png` |
| 2 | Setup > Fleet | Dropdown text is cut ("City collection", "Fills up along t"). Heuristic 6, recognition | major | n/a | same |
| 3 | Setup > Fleet at 390 px | No row boundary; checkbox alone above the row. Heuristic 4, consistency | major | n/a | `tool_390x844_setup-fleet.png` |
| 4 | Setup > Fleet | "What will be driven" and "Driver run" are run planning, in engineer words. Heuristics 2 and 8 | major | R10 | same |
| 5 | Column and page names | "PTO" as a column name (jargon); "Charging", "Cost" and "Costs", "CO₂" and "Taxes and CO₂" mean two different pages in Setup and Results. Heuristics 2 and 4 | minor | `[JUDGEMENT]` | sub-menus in the screenshots |
| 6 | Results disabled before run | Results, Compare, Documents are disabled with a tooltip only; no on-screen reason | minor | Heuristic 1 | `tool_audit_raw.json`; the run state line says "Not run yet" |
| 7 | Vehicle dialog | Dialog heading takes focus with a visible box but the dialog title is a heading, not a banner; moderate duplicate banner and unique landmark issues | minor | WCAG best practice | axe `dialog:template` |
| 8 | Results > Battery and Grid | Wide tables sit in a scrollable region that keyboard users cannot reach. axe serious `scrollable-region-focusable` | major (a11y) | WCAG 2.1.1 | `tool_audit_raw.json` |
| 9 | Results > Inputs and sources | 7,379 px, 4 to 8 times longer than other results pages | minor | Heuristic 8 | `tool_audit_raw.json` pages |
| 10 | Embedded tool in the site at night | The tool stays in day colours when the site is in night theme | minor | Heuristic 4 | `site_1440x900_night_en_demo-in-site.png` |
| 11 | Weather | No location field; the station is a fixed text | minor | B10 | `model.js` |
| 12 | Landing, Danish | Header wraps at 1440 px | major | Heuristic 4 | `site_1440x900_day_da_hero.png` |

Positives worth keeping `[TEST]`: Escape closes the dialog; focus stays inside the dialog (0 escapes in 45 Tab presses); the run line says what is wrong ("N values needed before you can run"); a missing required field blocks Run.

## F3. Accessibility (WCAG 2.2 AA), tool used: axe-core 4.14.0 plus scripted checks

| Check | Result | Evidence |
|---|---|---|
| Keyboard path through the fleet table | 69 tab stops in the first 70 presses, 49 inside the fleet table, first stops: select all, row checkbox, group name, count, vehicle dropdown, Edit. Reachable. | `tool_audit_raw.json` `keyboard` |
| Focus visibility | 0 of 69 stops without a visible outline or shadow | same |
| Dialog focus trap | focus starts inside; 0 escapes in 45 Tab presses; Escape closes | `focusTrap`, `escCloses` |
| axe on tool pages (Fleet, Weather, Check, Overview, Documents) | no violations | `axe` |
| axe on Battery and Grid | 1 serious each: `scrollable-region-focusable` | `axe` |
| axe on the open dialog | 2 moderate: `landmark-no-duplicate-banner`, `landmark-unique` | `axe` |
| axe on the landing page (day, English, top state) | 1 serious: `color-contrast` on `.dim.sheet:nth-child(2) > .foot` (the document fan) | `site_audit_raw.json` |
| Target size (2.5.8, 24 × 24 px) | Under 24 px at 390 px: 3 on Project, 19 on Fleet, 5 on Depot, 5 on Charging, 6 on Weather, 3 on Tax, 6 on Overview (checkboxes 15 to 16 px, row links 24 × 17 px). The criterion allows small targets with enough spacing; I did not check spacing | `small` in the raw file |
| Reduced motion | tool: 0 animated or transitioning elements and a `prefers-reduced-motion` rule; site: 0 and 0 | `reducedMotion` |
| Labels | no label issues reported by axe on the pages tested | |
| Landing images | 60 images, none without an `alt` attribute, 55 with empty `alt` (treated as decorative). Whether the product images are really decorative needs a decision | `imgs` |
| **Not tested** | night theme contrast, other states of the pinned story, the Danish and other languages with axe, screen reader, 200 to 400 % zoom | |

## F4. Inputs coverage

178 inventory rows, all with a register row. Demo: 169 of 274 register rows have a field (`in_current_demo` = yes), 2 partly, 103 no (83 of the 103 are not hidden). The missing ones fall in four groups: (1) planned functions (ageing detail, sizing mode B, calendar exceptions, tender, flexibility detail, growth); (2) inventory items missing in the demo (ampere unit, Eloverblik, weather location, library pick, TFL access, wet road); (3) year-8 detail (warranty years, replacement, residual link); (4) all hidden defaults, which are right to be absent. File: `inputs_register.csv`.

## F5. Performance (landing page)

Measured from local disk, so not a network measure `[TEST]`: `DOMContentLoaded` 186 ms, first paint 164 ms. Page file **3,032 KB**. Of this: 49 inline WebP images, **1,938 KB decoded** (base64 adds about a third on top); fonts 71 KB; everything else (HTML, CSS, JS, text) 448 KB. The largest images are 95, 75, 74, 72, 71 and 66 KB. On a 10 Mbit/s link a 3.0 MB file needs about 2.4 s to transfer `[JUDGEMENT]`, arithmetic only. Everything sits in one file, so no image can be cached separately and the whole page must load before the first image shows. The folder `website-wip/out/` holds two near-identical files whose names differ only in case (`ev-scope-site.html` and `EV-Scope-site.html`, about 3.1 MB each); on Windows or macOS that is a collision `[TEST]`.

---

# Part G: landing page research and proposals

## G1. Research (what I could read, what I could not)

I read the home page text of HOMER, SAM, PV*SOL, Dynamon, BetterFleet, Decade Energy, Flowemo and Elento. **PVsyst's home page could not be extracted** (empty). **Patensify and the "3 to 5 clear technical B2B pages" were not reviewed** in this pass. Screenshot references are not captured as links. Word counts are my counts of the visible text.

| Site | What the hero sells | How roles find their part | How the product is shown | Tone and proof |
|---|---|---|---|---|
| HOMER (UL Solutions) | "Optimize the value of your hybrid power system" | Three products by **situation** (Self-sufficiency and resilience, Electric Bill Optimization, Utility-scale investment), not by job title | Not seen in text | Selling plus proof: "more than 250,000 energy professionals in over 190 countries" `[TOOL]` |
| SAM | A free desktop application for techno-economic analysis | A plain list of what it models; no roles | An intro video | Plain, helpful; no selling; names NREL and the 2017 General Description paper as the deeper reference |
| PV*SOL | "The trusted software for solar design" | One product | Feature list with numbers (module and inverter counts) | Selling; claims "industry standard" |
| Dynamon | "De-risk your fleet decarbonisation" | One line naming fleet operators, OEMs, charge providers, consultants, leasing, telematics | Case studies with named customers; a starting price on the page | Helpful plus proof by named customers |
| BetterFleet | A long mission sentence | Fleet planning, operations, charge management as products | Not seen | Proof by certifications (Cyber Essentials Plus, SOC 2) |
| Decade Energy | Provider of grid power and charging | Not by role | Not seen | A provider, not neutral; proof by counts of studies |
| Flowemo (Danish) | "Planlæg ladeinfrastruktur på minutter" | One audience | Videos per feature; map and 3D | Helpful; "book a demo" |
| Elento (Danish) | "Ladestandere til erhverv, ejendomme og boligforeninger" | **Menu by audience** (Erhverv, Boligforeninger, Projektudvikling), plus a three-type "who we help" block | Not a tool | Questions framed from the customer's side; a free first assessment; legal footer with CVR `[TOOL]` |

`[JUDGEMENT]` The two patterns most relevant to Bob's "i want to go to the part that concerns me": **Elento** (a menu by audience with one page each) and **HOMER** (routing by situation). Neither lists audiences twice.

## G2. Section by section review of the current page

| Section | Purpose | Does it work (`[TEST]`) | Feedback line | Proposal |
|---|---|---|---|---|
| Header | Navigate, language, theme, demo | English fine; Danish wraps (`site_1440x900_day_da_hero.png`) | D5 | Fix wrap; remove "Who it's for" if roles move to the hero chooser |
| Hero | Say what it is | 26 words incl. buttons; one line; image day and night (`site_1440x900_day_en_hero.png`); headline "Scope before you sign" is a slogan | D3, D10 | Plainer headline, one line, roles under it (G3) |
| Who it is for | Role routing | Four tabs, three questions, one example, image (`..._for.png`); big empty area under the questions; a tab combines two audiences | D5, D7 | One role per tab; title and breadcrumb change with the role (G3) |
| How it works | Pinned story, seven chapters in 6,480 px | Long; contains the liked elements; captured at 4 scroll points | D1 | Keep, shorten hook sentences to the effect on the reader |
| See it on a sample depot | Demo preview | three screens | D4 | G6 |
| Six documents | Picker with a fan | Works; sheets in the fan are cut at the right edge; one contrast issue (`..._documents.png`) | D8 | G5 |
| Closing, footer | Call to action, legal | Placeholders in legal pages | n/a | Fill them |

## G3. Audience routing

Options (Bob decides; Question 5):

| Option | How it works | Good | Bad |
|---|---|---|---|
| A. Role menu in the header | Five role links; each opens a short page `/for/<role>` | One step from anywhere; Elento does this | Header gets long; the Danish header already wraps |
| B. **Role chooser under the hero** | "I am a …" with five buttons; choosing swaps the section below the hero (same page, `#fleet-owners` and so on) | Visible on first load; the audiences are listed once; matches "go to the part that concerns me" | The home page without a role chosen shows no role content, so a default is needed |
| C. Separate pages per role | Each its own short page | Best for search and sharing links | Seven pages to build and keep |

**Kiro's recommendation: B, with every role keeping its own address (`#municipalities` already exists), and "Who it's for" removed from the header.** The title row shows "For municipalities and public buyers" with the role in a breadcrumb line, so Bob's complaint "nothing besides the button tells me" is answered. Cost: one more state to build and test.

## G4. Copy proposal (reader's point of view; every fact has a source path)

Rules used: plain words, no slogans, no figure without a source, sample figures marked as sample. **English only.** I cite no native-quality Danish source for terms, so no Danish proposal.

**Hero.** Headline: *Check an electric fleet before you sign*. One line: *Battery, chargers and grid connection, worked out from your own routes and your hardest winter day at year 8.* (No source needed: it describes the tool.) Under it: the five role buttons.

**Roles** (decision they face, three questions, one example with its source, what they get). Also in `wireframes/landing-desktop.html`.

**Fleet owners.** Decision: *Which of our vehicles can switch, and what does the depot need?* You can answer: How much battery does each vehicle need?; Will it still finish the hardest winter day at year 8?; Do we have to upgrade the grid connection?. Example: Grid companies quote 12 to 18 months to connect when capacity is free, and 2 to 4 years when it is not. Find out which case you are in before you order vehicles. Source: `project-notes/claude_doc-findings-grants-grid-tenders-2026-10-28.md §2`. You get: Feasibility report; Grid connection application.

**Municipalities and public buyers.** Decision: *What do we write in the tender, and which bid fits our own routes?* You can answer: What usable battery must a bid state at year 8?; Does a bid still cover our hardest winter route?; How do the bids score with our weights?. Example: Danish tenders already ask bidders to state the usable battery capacity guaranteed at year 8. One refuse-truck contract asks for at least 80 % and a free replacement if it is lower (80 % as stated in Bob's brief; contract text not re-read for this proposal). Source: `project-notes/claude_doc-findings-grants-grid-tenders-2026-10-28.md §4 and §6; Bob's prompt of 14 Nov, section 0.3 and 1`. You get: Tender annex; Client presentation.

**Housing associations.** Decision: *How many residents can charge before the building's supply is full?* You can answer: How many charge points fit the supply we have?; What does the evening peak look like when everyone is home?; What connection would the rest need?. Example: From 2026 residents in Denmark have a right to a charge point unless a real capacity limit prevents it (stated in Bob's brief; the law text is not in the project notes, so check before publishing). Planned: this view is not built yet, so label it "coming". Source: `Bob's prompt of 14 Nov, section 0.3 and 1`. You get: Feasibility report; Grid connection application.

**Truck makers and dealers.** Decision: *Does our spec work on the buyer's routes, in winter, at year 8?* You can answer: Does the spec cover the buyer's hardest winter day at year 8?; What battery and charging power does the tender score reward?; How does our bid compare with the others?. Example: Scania asks buyers to contact them before the battery size is fixed, and runs a route simulation in the offer phase. Source: `project-notes/claude_results-gap-analysis-2026-10-26.md §3.7 (via 4-leaf 2023)`. You get: Tender annex; Offer sheet.

**Charge operators and grid companies.** Decision: *What will this depot put on the grid, hour by hour and in amperes?* You can answer: What is the depot peak in kW and in A?; Is full or limited access the better fit?; How much flexibility could the fleet offer?. Example: ARC needed 3,500 to 4,000 A per site and had to cut charger power to fit. Source: `project-notes/claude_results-gap-analysis-2026-10-26.md §1.6 (via 4-leaf 2023)`. You get: Grid connection application; Load profile.


**Positioning line** (in the footer area and the About page): *EV Scope plans and sizes. It does not operate charging.* `[DOC]` feedback log D11.

**How it works, one hook sentence each** (the effect on the reader, then one line on what the tool does):

| Chapter | Hook (effect) | What the tool does |
|---|---|---|
| Your routes go in | The same truck uses different energy on different routes. | You give routes, stops, loads; the tool works out the energy. |
| Overnight | Charging time decides how big the connection must be. | The tool schedules charging in the hours the vehicles are parked. |
| Battery size | A battery that is big enough today may not be at year 8. | The tool sizes against the capacity guaranteed at year 8. |
| Winter at year 8 | The hardest day is a cold day, with an older battery. | The tool runs the cold day at year-8 capacity and says if it passes. |
| Charger size | Too small and trucks are not ready; too big and you pay for power you do not use. | The tool sizes chargers from time parked and energy needed. |
| Payload | A full truck and an empty truck use different energy. | The tool changes the load along the route. |
| Grid connection | The grid company decides how long you wait. | The tool gives amperes, kW and the fee from the price list. |

`[JUDGEMENT]` These hooks are qualitative statements about physics and the tool, not claims about the product's results.

## G5. Documents section

Proposed interaction (answers Bob: "letting them pick", "the fan must not cover its description", "no dumped with six documents"):
- Title: **Which document do you need?** One line: *Pick one to see what is in it.*
- The role chosen above **preselects** one document (municipality: Tender annex). The user can pick another.
- Tabs, arrows and clicking a sheet do the same thing (Bob: one navigation pattern, 29 Oct).
- Fan of five or six sheets; the selected sheet is on top; **the description sits below the fan**, never under a sheet.
- No "you get all six".

| Document | One line | Who reads it |
|---|---|---|
| Feasibility report | The full study with every input and source. | Owner, bank, board |
| Grid connection application | The fields the grid company asks for: address, desired power, full or limited access, commissioning date, grid services. | Grid company |
| Tender annex | Usable battery at year 8, route energy in winter, charging window. | Buyer and bidders |
| Financial model | Year-by-year spreadsheet with the NPV rule used in the Vejdirektoratet form. | Finance |
| Grant application data | Trucks charging daily, chargers and their power, budget lines, lease. | Grant body |
| Client presentation | The decision, the cost and the risks on a few pages. | Board, customers |

## G6. Demo preview

Three screens, in this order: **Fleet** (what you enter), **Overview** with the year-8 line (what you learn), **Battery** (the winter day at year 8). Today it is fleet, overview, cost. Cursor: rests on the one figure that matters, moves once with an ease of about a second, clicks, then stops; no loop; the cursor never leads into a different screen. Reduced motion: still frames with a ring around the figure. `[JUDGEMENT]`, from Bob: "smooth ... not overwhelming ... enough with smooth cursor to guide the eye" `[DOC]` D4.

## G7. Visual hierarchy: type scale and spacing

Measured today `[TEST]`: 17 font sizes (7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 20, 21, 28, 38, 40, 44, 80 px), the hero H1 is 80 px, H2s are 38, 44, 40, 44 px, 42 text elements are at 10 px or smaller.

Proposed scale (px; base 16): **12** label, **14** note, **16** body, **18** lead, **24** subheading, **32** section title, **48** hero headline (fluid down to 32 on phones). Spacing steps of 8: 8, 16, 24, 48, 96. One heading size per level. No text under 12 px. Cost: re-setting about 40 elements; benefit: the page reads in one rhythm (Bob: "now its all to the point i dont even know how to read" `[DOC]` D6).

## G8. Mobile, accessibility, performance, legal

- **Mobile** (390 px): no horizontal overflow in any of the 12 runs; hero fits (`site_390x844_night_en_hero.png`). The role tabs scroll sideways and show two tabs at a time (hidden ones are not obvious). The role chooser should wrap to a column of five buttons.
- **Accessibility:** one serious contrast issue in the fan; text under 12 px; 55 images with empty alt to review; reduced motion already respected.
- **Performance:** split images out of the single file, serve them with caching, load the pinned-story images on approach, keep fonts embedded. The single-file build is useful as an offline deliverable but not as the live page. Cost: a build step and hosting for assets.
- **Legal** `[TEST]` `[JUDGEMENT]`, not legal advice. In place: Privacy (says no cookies, no analytics, nothing loaded from other companies), Terms, contact view. Missing before launch: the company name, CVR, address and email (placeholders), a named person responsible for the privacy text. Not found: an accessibility statement. Whether an EU B2B site needs one depends on the company and the services sold; ask a lawyer.

---

# Questions for Bob

Each has options and evidence. I recommend where I can, and say why.

**Q1. The Fleet page holds 128 of 274 inputs.** Options: (A) keep it; the cells open the templates; (B) add a "Vehicle" page that lists vehicle templates. Evidence: paper test says anything inside a template needs two guesses (tree_test). You rejected a Templates page, and B recreates it for vehicles. *Kiro's recommendation: A, with row summaries that show the year-8 value, a header search, and Check and run links.* Cost: the weakness stays.

**Q2. Template editing: popup, side panel or inline?** Carbon says modals interrupt and should be used sparingly for short, non-frequent tasks, and that repeated tasks should be on the page. NN/g says modals block. But you asked for named popups. Options: (A) modal as today; (B) side panel on desktop, full-screen sheet on phones, with named popups one level deeper; (C) inline expand under the row. *Recommendation: B.* The fleet table stays visible while you edit. Cost: a new component.

**Q3. Link or copy** when a shared template is edited. See D4. *Recommendation: B, ask once.*

**Q4. First run.** See D4. *Recommendation: guided first row, with sample and assistant next to it.*

**Q5. Where the five audiences are listed on the landing page.** See G3. *Recommendation: chooser under the hero, remove from header.*

**Q6. Name and content of the Taxes page.** Options: keep "Taxes, grants and CO₂"; merge taxes into Prices ("Prices and taxes") and keep Grants and CO₂ on their own page; split into Taxes and Grants and CO₂. The paper test shows "km-toll" may need two guesses. *No recommendation: it needs a test with users.*

**Q7. What to show as the year-8 default.** Three values exist: 70 % (demo, Rambøll 2023), at least 80 % (tender, as stated in your brief), 75 % (ARC 2022: max 25 % loss). Options: (A) required, no default; (B) default 70 % with an asterisk (today); (C) default from the tender page when the project is a tender. *Recommendation: A for tender projects, B with a visible asterisk otherwise.* Reason: a default shown as fact could pass a check the buyer would fail.

**Q8. Project purpose choice** ("size my fleet / compare offers for a tender / check a housing site"). It switches the Tender page on. Not in the inventory. Options: add it; or show the Tender page always. *Recommendation: add it (PV*SOL's system type does the same).*

**Q9. Housing association view.** The right to a charge point from 2026 is in your brief, not in the project notes I could check. Options: build a housing view (`dep.housing`, planned) or put "coming" on the landing page. *Recommendation: "coming"; do not claim it on the page until it exists.*

**Q10. Mark for NO SOURCE.** Same asterisk as assumptions, with a separate block in the report (proposed), or a different mark. Evidence: inventory section 15 says NO SOURCE "must not be shown as fact".

**Q11. Dwell time.** Inventory says 45 minutes per stop (ASSUMP); the demo sample uses 20 seconds of work per stop. Two different things share one name. Options: split into "time at the stop (work)" and "time parked between stops".

**Q12. Overview input visuals.** Add four small visuals (payload, shift window, temperature, connection against building load)? *Recommendation: yes, but only those four.* They answer your C3 request.

---

# Choices I made

1. Branched from `claude/ev-scope-site-wip` as asked. The prompt file was already in the branch, so I did not copy it again.
2. The VECTO fork could not be cloned (the sandbox's git gateway refused the repository). I read the user manual and the file list through the GitHub API instead. VECTO GUI source forms were **not** read, only listed.
3. The tool was audited standalone at all three viewports in day theme only (it has no night theme). The site was audited in day and night, English and Danish.
4. Browser: the headless Chromium already on the machine, driven by `playwright-core`. axe-core 4.14.0 installed locally. The scripts are outside the repo (kept small and not part of the deliverable).
5. `required` in the register means "no default exists, so Run is blocked". If a default exists the row is "optional (has default)".
6. I did not choose any default value. Where the inventory had one it is copied with its tag.
7. I built the wireframes from the register by script, so every page's fields match the register; hand-drawn pages are the results and landing wireframes.
8. I marked candidates from other tools as `candidate`, not as inputs.
9. A page "Tender" and a project purpose choice are **proposals** `PROPOSED, needs Bob`.
10. I rated "What will be driven" as a major issue because Bob's rule is explicit, even though it is derived from inputs and not a result.
11. The tree test is a paper test by me, not a user test.

# Bob to fetch

| What | Link | Look for |
|---|---|---|
| PVsyst sample report PDF and the product site | https://www.pvsyst.com | Report section order and page; the site returned no text |
| COWI truck TCO sheet | not in repo | tab names, input section order |
| VECTO 5.1.7 user manual and GUI source | https://code.europa.eu/vecto/vecto/-/releases | Whether the vehicle editor changed since 4.3.4-DEV; form layouts |
| Zeti, ElectricFleets/Sawatch, T3CO, Sunny Design, Chargepoly, Dynamon ZERO demo, BetterFleet demo | their sites | Input navigation, how detail is hidden, results order |
| HOMER sensitivity and economics pages | https://homerenergy.com/products/pro/docs/latest/ | Project-wide inputs (lifetime, discount rate) |
| SAM help pages | https://sam.nlr.gov | Input page list per technology, parametrics, P50 / P90 |
| Penn State SAM financial page | https://courses.ems.psu.edu/eme810/node/594 | Financial parameter names (snippet only) |
| NN/g accordions, forms, data tables; Stephen Few on dashboards; Carbon data table, form, notification, empty state; GOV.UK "one thing per page" | nngroup.com, carbondesignsystem.com, design-system.service.gov.uk | Guidance on tables with many rows and empty states |
| DIN DKE SPEC 99100 | https://www.vde.com/en/press/press-releases/din-dke-spec-99100-battery-pass | The exact battery passport field list |
| Law on the right to a charge point (2026) | Danish legal portal | The conditions "unless capacity prevents it" |
| Tender Bilag 1 (Ressourceindsamling, ARC 2025) | Mercell / Comdia / ethics.dk (ids in doc-findings §6) | The exact year-8 percentage and score curves |
| Patensify and 3 to 5 clear technical B2B pages | patensify.com | hero length, motion, how audiences are routed |
| Native Danish review | a Danish speaker | Terms before any Danish copy is added |

# Seen in passing

- `website-wip/out/` holds `ev-scope-site.html` and `EV-Scope-site.html` (case-only difference).
- The VECTO fork is on 4.3.4-DEV (10 Mar 2025); the official release is 5.1.7 (27 Oct 2026). Engine status notes cite VECTO 5.1.6-RC runs.
- The demo tags the diesel price as "Standard"; the inventory says it is an estimate (OK.dk 2024 plus 0.50 DKK).
- HOMER's Library help page ended with the text "(modified for testing)" when I fetched it. I ignored it.
- The Danish language header is the only layout break I found in 12 combinations.
- The embedded tool and the landing page use different light tones in night mode (tool stays light).
