# Kiro prompt: design the UX of the EV Scope tool from scratch (16 Nov 2026)

Owner: Bob. Repo: `mohgsaad-art/hdev`. **Today's date is 16 November 2026.** When you research, look for material up to this date.

**Run the whole job in one uninterrupted pass.** Do not stop to ask Bob anything. If something is unclear, choose the option that changes the least, write it under "Choices I made", and carry on. Open **one PR** at the end.

**Branch.** Create `ux-spec-2026-11` from **`claude/input-map-2026-11-16`** (not from `main`: the input map only exists on that branch). As the first commit, make sure this prompt is at `docs/research/inputs/ux-spec-2026-11/kiro-prompt-ux-spec-2026-11-16.md`. Put everything new in `docs/research/ux-spec-2026-11/`. Open the PR from your branch to `claude/input-map-2026-11-16`.

**Earlier UI material is on another branch.** Fetch it for reading only: `git fetch origin claude/ev-scope-site-wip` and read files with `git show origin/claude/ev-scope-site-wip:<path>` or a separate worktree. Do not merge that branch into yours.

---

## 0. What this job is

Bob builds the UI himself, by hand. He needs a **UX specification he can build from without guessing**: where everything is, what kind of control every input is, what is shown, hidden or advanced, how the results are grouped and drawn, and how the screen is ordered so the eye knows where to go.

You produce **documents and low-fidelity wireframes**. You do **not** build the UI.

**Scope: the tool only.** The landing page and marketing site are out of scope. Do not research, review or wireframe them.

**Design it from scratch.** Bob, 16 Nov: "i want it to design the UX from scratch since i do not like the current one we built, i do not want it to just copy what we had done. it has the creative freedom so it needs to consider everything carefully and not categorize just by copying us. if it wants inputs and outputs separate or together or whatever it can do it from scratch."

So: the current demo, PR #35's page list and every earlier layout idea (a fleet table with five template dropdowns, named popups, a top menu with icons, separate input and result pages, cab heating under Weather, a Check-and-run page, and so on) are **history, not requirements**. You may keep any of them only if your own research and reasoning lead there, and then you must say why it beats the alternatives you considered. You may equally merge inputs and results, use a canvas, a workspace with panels, a guided flow, a document-like model, or something else. Start from the users, their tasks and the structure of the data in the input map, not from the old screens.

The single most important quality target, in Bob's words from earlier feedback:

- "i should know what to expect from the pages before i go into them."
- "be careful of over correcting the problem and stuffing things into just one tab or everything in just one pop up, the goal is for it to be intuitive not go from overwhelming to empty overwhelming and confusing because everything is brushed under the rug."
- "A lot of the outputs and results look merged because of poor visual hierarchy and bad alignment, it just looks like a sentence not results with million krona value."
- From the 16 Nov brief for this job: maps, charts, texts, numbers and calendars "must not fight for attention to the point nothing feels important."

### 0.1 Rules (read first)

1. **UX only.** Do not edit `src/`, `hdev/`, `website-wip/`, the notebook or any engine code. Wireframes are new files under `docs/research/ux-spec-2026-11/wireframes/`: plain HTML and CSS, greyscale plus one accent, no brand polish, no JavaScript logic beyond showing and hiding panels, every file labelled "wireframe" and opening offline with no external requests.
2. **The input map is the source of truth for inputs.** `docs/design/hdev-input-map.md` lists every input, every way to fill it, every lock rule and every output. **Every input ID in Parts B and D of the map and every lock rule in Part E must appear in your specification.** Where the map and an older document disagree, the map wins. Where the map says `OPEN`, `PROPOSED` or `PARKED`, do not decide it: design the screen so either answer fits, and list it under "Questions for Bob". **The map also repeats some old layout ideas** (section 0.4 items 9 and 10, the "fleet row" picture in section 1, the page names in Part F2, and notes such as "shown on the page, not in a popup"). Those layout statements are history like the rest of the old UI. What binds you in the map is the content: the inputs, the ways to fill them, what is required, the lock rules and the outputs.
3. **Status must stay visible in your documents.** Carry the map's status tag (`FINAL`, `WIP`, `DESIGNED`, `PLANNED`, `PROPOSED`, `OPEN`, `PARKED`) into every row you write. Planned stages get a designed home now, and a designed "not available yet" state.
4. **No invented numbers.** Wireframes may show sample values only when labelled `ILLUSTRATIVE`. Never choose a default value. Copy defaults and their source tags from the map, or write `OPEN`.
5. **Tag every statement** in the research and the specification: `[MAP]` (the input map, with section), `[DOC]` (another project document, with path), `[TOOL]` (another tool's manual, help page, site or code, with link and date read), `[GUIDE]` (design or usability guidance, with link), `[STD]` (a standard, e.g. WCAG 2.2, ISO 9241, with clause), `[TEST]` (your own check, with screenshot path), `[JUDGEMENT]` (your reasoning), `[OPEN]`. Say for each external source whether you read the whole page or document, part of it, or only a snippet.
6. **Take inspiration, do not copy.** Describe other tools' patterns in your own words. No copied text, screenshots, icons or code in the repo. No reverse engineering. Anything behind a login or paywall goes on "Bob to fetch" with the link and exactly what to look for.
7. **Explain why.** For every structural choice say what problem it solves, which line of Bob's feedback it answers (quote it from `bob-feedback-log-ui-and-landing.md`), what it costs, and what the alternative was. Bob, 12 Nov: do not list changes "like I'm a machine".
8. **Never decide an open design choice for Bob.** Show the options with evidence. Label your pick "Kiro's recommendation" with the reason.
9. **Plain English.** Short sentences. Define a technical term the first time. Refer to the owner only as "Bob". Bob often reads on a phone: tables and short lists beat paragraphs.
10. **Architecture rules the UX must respect (decided, not up for review):**
    - The UI is a dumb form. All logic, defaults and calculations are in Python. The UI reads and writes **one project JSON**. A scenario is the base project plus a list of changes. The base is never overwritten.
    - `check(project)` returns the list of missing, defaulted and wrong values without running the engine. `run(project)` does the same and then runs. The UI only displays what they return.
    - Defaults live in `defaults.py`. Every value is marked *given*, *default* or *missing*.
    - The UI shows t, km, km/h, °C, kW, kWh, min, DKK. Python converts.
    - Client view, OEM view and engineering view are three views of the same data.
11. **What is fixed and what is free.**
    - **Fixed (content and behaviour):** every input, branch, lock rule and output in the input map; rule 10 above; the year-8 battery check is never dropped; the user can start at any stage (Part C); projects can be saved, reopened, listed, imported and exported (Part B); nothing a user typed is silently lost.
    - **Fixed (taste, in Bob's words):** it should read as a serious, trusted industry tool, "professional, modern, simple yet technical", not "websitey", not a gimmick, not dated, not "AI-website" looking. Charts only where they help: "not everything a graph, not all bar charts".
    - **Free (yours to design):** everything else. Navigation model, number and names of screens, whether inputs and results live apart or together, what is a page, a panel, a dialog, a table or a canvas, how the fleet is entered, where libraries and templates live, how defaults and sources are shown, where Run lives.
    - **Use Bob's feedback log as evidence of problems, not as a list of solutions.** It records what annoyed him in the old build (too many fields at once, unpredictable pages, things hidden under the rug, half the inputs missing, results that read like a sentence, sources cluttering every field). Your design must not recreate those problems. It does not have to adopt the fixes that were tried.

### 0.2 Pitfalls from earlier Kiro PRs (do not repeat)

- Claiming "done" without evidence. Every claim in the summary points to a file, a CSV row or a screenshot.
- Dropping inputs. PR #35 was started because "Half the inputs are missing". Gate 1 below exists for this.
- Describing a tool from memory. Only describe what you read or saw, and say when.
- Writing `NOT FOUND` after one attempt. Try the official site, the PDF manual, the help centre, archive.org and video walkthrough transcripts, then put it on "Bob to fetch".
- Deciding things. PR #35 placed the year-8 guarantee and several OPEN items as if settled. Offer options.
- Inheriting the old structure. Do not open the old demo or PR #35's wireframes until you have written your own first concept (Part A0). Read them afterwards, only to check what failed.

### 0.3 Gates (stop and fix before going on)

- **Gate 0, concepts.** `concepts.md` exists with at least three concepts that differ in kind, scored on the same criteria, before any detailed specification is written.
- **Gate 1, coverage.** A script (`coverage_check.py`, committed) reads every input ID from `docs/design/hdev-input-map.md` (the backticked IDs in the first column of the Part B and Part D tables, and the `cost.*` labels in table D9a) and checks that each has exactly one row in `inputs_ux.csv`. Zero missing, zero duplicated. Paste the script output into the report.
- **Gate 2, lock rules.** Every rule 1–68 in Part E of the map has a row in `lock_rules_ux.csv` naming the screen, the trigger control, what appears, what disappears, and what happens to a value already typed in a field that closes. Zero missing.
- **Gate 3, entry points.** Each of the five start points in Part C below has a complete walk-through in `journeys.md` from "New project" to a result page, naming every screen in order.
- **Gate 4, wireframes open.** Every wireframe is opened in headless Chrome at 1440×900, 1280×800 and 390×844 with no console errors and no external requests. Screenshots are committed under `screens/`.
- **Gate 5, attention.** Every wireframe has its attention order written on it (see Part F, item 6) and passes your own greyscale squint check.

---

## 1. Context

**EV Scope** (the engine is called HDEV) sizes the electrification of vehicle fleets and their depots: energy use per route, battery size, charger size and count, grid connection, flexibility, cost against diesel, and CO₂. It is built to be auditable against VECTO, the EU's official heavy-duty vehicle simulation tool. The aim is to be "PVsyst for EVs": a brand-neutral, auditable result that buyers, banks, grid companies and suppliers accept.

**Users.** Fleet owners and operators; municipalities and public buyers; housing associations; truck makers and dealers; charge point operators, aggregators and grid companies; consultants who run it for a client. One product, used self-serve or run by a consultant.

**Engine status today.** Consumption (route → energy at the battery) is written and being finalised. Battery, charging, grid, flexibility, cost and CO₂ are planned. The UX must cover all of it, and must look right when only the first stage exists.

### 1.1 Read these first (in this order)

| What | Where |
|---|---|
| **The input map** (tree, every input and its branches, every function, planned stages, lock rules, outputs, open decisions) | `docs/design/hdev-input-map.md` (your branch) |
| Bob's feedback log (use only section A to C and F on the tool; ignore the landing page section), in his words | `docs/research/inputs/ui-ia-2026-11/bob-feedback-log-ui-and-landing.md` on `claude/ev-scope-site-wip` |
| **After your first concept only:** your earlier research (PR #35): tool comparison and result register are useful raw material; its page list and wireframes are not a starting point | `docs/research/ui-ia-2026-11/` on `claude/ev-scope-site-wip` |
| **After your first concept only:** map of the old demo build (what Bob rejected) | `docs/research/inputs/ui-ia-2026-11/current-build-map-2026-11-14.md` on `claude/ev-scope-site-wip` |
| **After your first concept only:** the old demo tool | `website-wip/out/ev-scope-tool.html` on `claude/ev-scope-site-wip` |
| Results gap analysis; outputs to add; what other tools do | under `docs/research/inputs/ui-ia-2026-11/project-notes/` on `claude/ev-scope-site-wip`: `claude_results-gap-analysis-2026-10-26.md`, `claude_outputs-fna-bna-battery-passport-2026-10-28.md`, `claude_review-other-tools-all-features-2026-11-09.md` |
| Master spec: stage entry contracts, slots, capability gating | `.kiro/specs/hdev-master-plan/design.md` Part 4 |
| VECTO source and GUI (for how the official tool lays out its editors) | `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/VECTO` |

**How PR #35 and the old demo relate to this job.** Bob does not like the UX that was built. PR #35 organised inputs by adjusting that build. This job starts again. Use PR #35 only as (a) research notes on other tools, to extend rather than repeat, and (b) a list of results. Where PR #35's register and the input map disagree, the map wins.

---

## 2. The parts

### Part A0. Concepts before structure (write `concepts.md`)

Before you look at any old screen:

1. From the input map alone, write down the **objects** the user works with (project, vehicle, route, stop, load, body equipment, schedule, depot, grid connection, charger, weather, prices, costs, scenario, run, result, document, library entry) and how they relate (one-to-many, shared, reused).
2. Write the **tasks** per user type and how often each is done (once per project, per vehicle, per run).
3. Sketch **at least three really different UX concepts** for the whole tool, each on one page with a rough wireframe of its main screen and a walk through one task. They must differ in kind, not in page names. Examples of different kinds, to show the range and not to choose from: a guided step flow; a hub with objects you open; a single workspace with a model tree on one side and a context panel; a spreadsheet-like fleet sheet with drill-in; a canvas of the depot and routes; a document that fills in as you answer; inputs and results on the same screen with live "what is still missing".
4. Score the concepts against the same criteria: predictability ("i should know what to expect ... before i go into them"), calm with 300+ inputs, starting at any stage, work for a fleet of 1 and of 200, the three views (client, OEM, engineering), trust and auditability, room for the planned stages, effort for Bob to build by hand.
5. Pick one as "Kiro's recommendation", say what you took from the others, and what you gave up. Everything after this part is specified for the recommended concept. Keep the runner-up documented well enough that Bob could choose it instead.

### Part A. Research (do this before and alongside Part A0; write it up in `research.md`)

For each topic: what you read, what the pattern is, when it works, when it fails, and what it means for EV Scope. One comparison table per topic. Then a short list of **numbered design principles** that the rest of the specification cites by number.

**A1. Application shells and menu bars in professional tools.** How desktop-class tools in a browser arrange a menu bar (File, Edit, View, …) together with page navigation, a toolbar, a status area and side panels, without two navigation systems fighting each other. Where Save, Run, Undo, Help and the project name live. Look at engineering and simulation tools first, then document-style SaaS.

**A2. Project management.** Project list or home screen; create, open, open recent, duplicate, rename, archive, delete; autosave against explicit save; "unsaved changes"; version history and restore; import and export of a project file; what happens when an imported file is from an older version or has errors; templates and sample projects; search and sort; what metadata a project card shows.

**A3. Starting in the middle.** How tools let a user skip earlier steps when they already have the intermediate result (for example entering a measured load profile instead of modelling it). How they show which stages are modelled, which are user-supplied and which are not run.

**A4. Organising many inputs.** Progressive disclosure; wizard against hub-and-spoke against free navigation; modal dialog against side panel against accordion against separate page; grouping by physical object against grouping by workflow step; how expert fields are separated from everyday fields; how a choice that changes which fields appear is presented.

**A5. Choosing the control.** Evidence-based rules for: text field, number field, number with stepper, slider, dropdown, radio or segmented choice, checkbox, toggle, date and time pickers, table entry, file upload, map pick, profile or curve editor, "connect an account". Include the known cases where a control is the wrong choice (for example a slider for a precise value, a dropdown for two options, a toggle where the two states are not opposites). Units inside fields, unit switching, thousands separators, decimal comma against decimal point for Danish users.

**A6. Editable tables and bulk work.** Fleet-style tables with a dropdown per cell; bulk apply; copy and paste from a spreadsheet; long tables (a route can have hundreds of stops); frozen columns; row grouping; how such tables behave on a narrow screen.

**A7. Special views.** Maps for marking a depot, stops and a return; calendars for operating days, holidays, shutdowns and exceptions; curve and profile editors (a power-against-time profile, a price series, a loss map upload); previews of uploaded files with column mapping.

**A8. Defaults, sources and trust.** How serious tools show that a value is a default, a library value, a user value or missing, without clutter. How they present an assumptions list and an audit trail. What makes an engineering tool feel trustworthy rather than like a marketing page.

**A9. Results and dashboards.** Page-level hierarchy of key figures, status, charts and tables. How many headline figures. Where detail lives. How a "not calculated yet" result is shown. How partial runs are shown.

**A10. Choosing the chart.** For each kind of question (how much, compared with what, share of a whole, change over time, distribution, range and uncertainty, flow and losses, schedule, where on a map, pass or fail against a limit) which form is best supported by evidence and which forms are known to mislead. Evaluate at least: single number, number with a reference, table, bar, stacked bar, waterfall, line, overlaid lines, area, band (P10–P90), heat map (hour × day), box plot, load-duration curve, Gantt, Sankey or loss diagram, scatter, radar ("spider") chart, bullet graph, small multiples, map. For the radar chart give a clear verdict with evidence on when, if ever, it should be used here. Colour: a palette that works for colour-blind readers and in greyscale print.

**A11. Visual hierarchy.** Type scale, spacing scale, grid, alignment, grouping (proximity, common region), emphasis levels, number formatting, density. How to check a screen for competing emphasis.

**A12. Help and onboarding.** Menu help, inline help, glossary, first-run guidance, empty states, sample projects, error messages that say what to do.

**A13. Accessibility.** WCAG 2.2 AA for forms, dialogs, tables, charts (text alternatives, data tables behind charts), keyboard paths, focus, target sizes, reduced motion.

**Tools to study** (read manuals, help pages and, where open, the GUI source; say what you could and could not see):

- Simulation and engineering: **VECTO** (job editor, vehicle editor, auxiliaries, cycles, results), **PVsyst**, **NREL SAM**, **HOMER Pro / HOMER Grid**, **PV\*SOL** or **Sunny Design**, **OpenStudio / EnergyPlus front ends**, **QGIS** (menu bar plus panels plus map).
- EV fleet and depot: **Dynamon**, **BetterFleet**, **Flowemo**, **Decade Energy**, **Chargepoly**, **Geotab EVSA**, NREL **EVI-Pro / EVI-X** and **T3CO**, **eFLIPS**, **SpiceEV**, and others you find.
- Project and document handling in the browser: **Figma**, **Google Docs / Sheets**, **Notion**, **Linear**, **Airtable**, **Grafana**, **Tableau / Power BI** (for dashboards and for save, export and version patterns).
- The **COWI truck cost sheet** and the two other Excel files in `reference/excel/` (what a spreadsheet user is used to seeing).

**Guidance to start from.** These are leads from Claude's general knowledge. Claude did **not** re-read them for this prompt, so open each one yourself and cite what you actually read; drop any that do not say what is implied here.

- Nielsen Norman Group articles on progressive disclosure, modal and non-modal dialogs, accordions, wizards, form design, sliders, dropdowns against radio buttons, toggles against checkboxes, data tables, dashboards, empty states, error messages and the ten usability heuristics.
- GOV.UK Design System and service manual (question pages, "check your answers", error summary, date input).
- IBM Carbon Design System (the brand uses IBM Plex): data table, modal, form, number input, notification, empty state, UI shell.
- Material Design 3 and Apple Human Interface Guidelines (menus, sliders, pickers).
- Baymard Institute research on form fields.
- Luke Wroblewski, *Web Form Design*.
- Stephen Few, *Show Me the Numbers* and *Information Dashboard Design*, including the bullet graph specification and his critiques of radar charts and gauges.
- Cleveland and McGill (1984) on graphical perception; Edward Tufte, *The Visual Display of Quantitative Information*; Tamara Munzner, *Visualization Analysis and Design*.
- The Financial Times "Visual Vocabulary" and the Data Viz Project (chart choosers by question type).
- Okabe and Ito colour-blind-safe palette; ColorBrewer.
- ISO 9241-110 (dialogue principles) and ISO 9241-125 (visual presentation of information); WCAG 2.2.
- Shneiderman's eight golden rules; Jakob's law; Hick's law; Fitts's law (use them only where you can show they apply).

### Part B. The application shell

Specify the frame that every screen sits in. Deliver `shell.md` plus wireframes.

1. **Screen regions.** Name each region of your recommended concept with its job, its size, what it must never hold, and how it behaves at 1440, 1280 and 390 px. The tool needs the "typical things" a desktop-class application has (file handling, edit, view, help) in a form that suits your concept: a classic menu bar, a command menu, a toolbar, or a mix. Show how that layer and the main navigation coexist without becoming two competing navigations. Give at least two arrangements with trade-offs, then "Kiro's recommendation".
2. **The menu (or its equivalent), item by item.** For every menu and item: label, what it does, shortcut, when it is disabled, and which Python call or JSON change it corresponds to. Cover at least the list below, adapted to EV Scope. Add or remove items with a reason.
   - **File:** New project (opens the start chooser, Part C); Open; Open recent; Save; Save as; Duplicate; Rename; Import project (file); Export project (file); Export results (CSV, spreadsheet); Export documents (the six documents); Project settings; Close project.
   - **Edit:** Undo; Redo; Reset field to default; Reset page to defaults; Find an input (search across all pages and popups, jumps to the field).
   - **View:** Client view / OEM view / Engineering view; Show or hide the assistant; Show default and assumption marks; Units and number format; Language; Theme; Density; Zoom.
   - **Project:** Start point (which stage the project starts at); Scenarios (new scenario, manage, compare); Fleet growth phases; Notes.
   - **Run:** Check (runs `check(project)`); Run; Run from a stage; Stop; Run history; Compare runs.
   - **Libraries:** Vehicles; Drivetrain numbers; Chargers; PTO profiles; Routes; Payload profiles; Schedules; Import into a library. (Where libraries and reusable templates live is yours to design.)
   - **Help:** Getting started; Guide to this page; Glossary; Method and sources; Model status (what is validated, in testing, not built); Keyboard shortcuts; What is new; Report a problem; About (engine version, run fingerprint).
3. **Projects home.** The screen that lists all saved projects so the user picks which to work on. Specify: list against cards (with a recommendation); what each entry shows (name, client or site, start point, fleet size, last edited, last run and its status, which stages have results, number of scenarios, a "needs attention" count from `check()`); sort, filter, search; actions (open, duplicate, rename, export, archive, delete with confirmation); the empty state for a first-time user; sample projects; import from here.
4. **Saving.** Recommend autosave, explicit save, or both, with evidence, and specify the visible save state ("Saved", "Saving…", "Unsaved changes", "Could not save"), leaving with unsaved changes, and two tabs open on one project. The project JSON is saved server side (decided 12 Oct). Specify version history and restore as an option for Bob, not a decision.
5. **Import and export.** File type and naming; what is inside an export (project, scenarios, libraries used, results or not); the import flow: choose file → validation by Python → a result screen listing what was read, what was defaulted and what is wrong → open. Importing a file from an older version. Importing data files into inputs (GPS log, weather file, price series, PTO profile, loss maps, session list, load profile, meter data) is a separate pattern: preview, column mapping, units, row count, problems found.
6. **Run and status.** Where the Run button lives; what "Check" shows; the run-progress display by stage; the stale-results rule (an input changed after the last run: which results are marked out of date, using the rerun logic in the input map Part C0 and rule 68); cancel; errors that point to the field.
7. **The assistant.** It fills inputs from dumped data and asks for what `check()` lists as missing. Specify how its suggestions are shown, confirmed and marked, and that the user confirms what it read before Run. It never picks defaults.
8. **Views.** How the client, OEM and engineering views change what is shown, where the switch is, and how a field that is hidden in the current view but holds a non-default value is signalled.
9. **Global conventions.** Field marks (given, default, library, assumption, no source, missing, edited), units, number formats, dates and times, error wording, confirmation dialogs, keyboard shortcuts, loading and empty states.

### Part C. Start points: entering the tool at any stage

A user does not have to start at consumption. Specify each start point as a complete path. Deliver in `shell.md` (the chooser) and `journeys.md` (the walk-throughs).

| # | The user says | Starts at | They give instead of the earlier stages | Input map |
|---|---|---|---|---|
| 1 | "Work it all out from my routes" | consumption | the full project | Parts B, C |
| 2 | "I know my consumption" | battery / charging | kWh/km per route (and km per day), or kWh per day | D0, rule 47 |
| 3 | "I know what each truck needs to charge" | charging | a session list: arrival, departure, energy needed, arrival state of charge; battery; chargers or "size them"; site limit | D0, D5 |
| 4 | "I already have chargers" (exact count and power) and want flexibility | flexibility | the chargers and their capabilities, plus either the sessions or a load profile | D0, D7 |
| 5 | "I only want the cost and CO₂" | cost | yearly energy, peak power, equipment list, prices | D0, D9–D11 |

For each: the question that routes the user there (wording options); which pages appear, which are hidden and which are optional; the entry form itself (controls, upload with preview, validation); how the stage strip or progress display shows "modelled", "you supplied this" and "not run"; how results downstream are labelled as resting on a user-supplied value; how the user later **adds** an earlier stage (for example starts with kWh/km, later lets the tool model consumption) or **switches** start point without losing what they typed; what happens to values in pages that close. Cover combinations too: start point 2 with existing chargers; start point 3 leading into cost; a housing association with residents' chargers and no routes at all.

`OPEN` in the map: what happens when supplied data has a different time step from the stage. Design the import screen so resample, reject and "run at the supplied step" are all possible, and list it as a question.

### Part D. Inputs

Deliver `inputs_ux.csv` (one row per input ID in the map), `inputs.md` (screen by screen), `components.md` (the special components) and wireframes. "Page", "section" and "popup" below mean whatever containers your concept uses: name them in your own terms.

**D1. Placement rules.** Write numbered rules first, derived from Part A, that decide for any input: where it lives, and whether it is always visible, one step away, expert-only or never shown. Then apply them. Derive the grouping from the data and the tasks. Do not start from the old page names or from the section order of the input map (the map is ordered by engine function, which is not necessarily how a user thinks).

**D2. Control rules.** Write numbered rules that decide the control from the nature of the input: how many options, whether the options are exclusive, whether the value is precise or approximate, whether it is one value or a series, whether it has a unit, whether it comes from a library. Starting hypotheses from Claude, to **test against your research, not to adopt** (each is `[JUDGEMENT]`):

- An exclusive choice that changes which fields appear (the `◉` nodes in Part A of the map) is a visible radio group or segmented control on the page, never hidden in a dropdown or a popup.
- An exclusive choice among many named items (a VECTO technology row, a tyre size, a library vehicle) is a dropdown; with more than about fifteen items or with attributes to compare, a searchable picker.
- A precise engineering quantity is a number field with its unit, never a slider.
- A slider is only for what-if exploration where the feel of the range matters more than the exact value (a scenario lever), and always paired with a number field.
- Yes-or-no with immediate effect is a toggle; yes-or-no as one of several independent options is a checkbox.
- A series (per stop, per hour, per year) is a table, with paste from a spreadsheet and file upload.
- A value that is normally a default is one step away from the main view, pre-filled, and distinguishable from a value the user gave.

**D3. One row per input in `inputs_ux.csv`.** Columns:

| Column | Meaning |
|---|---|
| `id` | the ID from the input map |
| `map_status` | FINAL / WIP / DESIGNED / PLANNED / PROPOSED / OPEN / PARKED |
| `label` | plain-English label; a second label for the engineering view where the map gives a physics name |
| `help_text` | one line a user sees on demand; no formulas in the client view |
| `page`, `section` | where it lives |
| `tier` | always visible / one step away / expert view / never shown |
| `container` | the name of the dialog, panel or sub-screen it lives in, if any |
| `control` | exact control (see D2), with the rule number that chose it |
| `options` | the option list, copied from the map (for example the VECTO rows) |
| `unit_ui`, `unit_switch` | unit shown; alternative units if switchable (for example A or kW) |
| `default_behaviour` | empty / pre-filled default with mark / pre-filled from library / computed read-only, with the map's source tag |
| `required` | required / default / optional / automatic, per the map |
| `validation` | the parser checks from the map, written as the message the user would see |
| `appears_when`, `closes_when` | from the lock rules, with rule numbers |
| `fills` | what this input fills elsewhere |
| `views` | client / OEM / engineering |
| `start_points` | which of the five start points show it |
| `scenario_lever` | yes / no |
| `year8_related` | yes / no |
| `reason` | one or two sentences: why this page, tier and control |

**D4. Screen-by-screen specification (`inputs.md`).** For each screen or container: its one-sentence promise ("what you will find here"), what it does not hold, its parts in order, the main fields, what is one step away, tables, conditional parts, the first-run and empty state, and the layout grid. Test the structure against Bob's "20 is wrong, 3 is wrong" and "not ... everything in just one pop up".

**D5. Things the UX must make possible (`components.md`).** The list below names **capabilities**, taken from the input map. How each is done is yours to design: several may merge into one component, and none has to look like the old build. For each, give states, behaviour, keyboard path and a wireframe.

1. **Entering a fleet**: groups of identical vehicles with a count; each group combines a vehicle, a route, a load pattern, body equipment and a schedule; the same route or vehicle is reused across groups; changing many groups at once; 1 group and 50 groups; a new user's first group without preparing anything beforehand. (The old build used one table with five dropdowns per row. Bob does not want that copied by default. Consider it as one candidate among others.)
2. **Reusing things** (vehicles, routes, load patterns, equipment profiles, schedules): pick, edit, "save as", what happens to other groups when a shared item is edited (options for Bob), VECTO's standard items shown as locked.
3. **Vehicle source chooser**: library truck, class only, manual (map tree A1), including what the form looks like after a library pick fills it, and how library ranges (curb mass, CdxA) are handled (`OPEN` in the map).
4. **Route source chooser**: VECTO cycle, typed, map, GPS upload, describe it or call-out log, saved route (map tree A2), with each source's own form.
5. **The map view**: marking the depot, stops and return; editing; what the map shows after a GPS upload; what it shows for a VECTO cycle (which has no geography).
6. **The stop table**: columns and what is locked per source (map A2 and B3); payload and PTO per stop; hundreds of stops; apply to all, apply to a range; the 0-second marker row.
7. **Payload**: the three shapes and the basis choice, with a picture of payload along the route.
8. **PTO editor**: the three parts (stop, drive, always-on), number or profile, the profile editor (time and power table with a preview curve), the "body has its own electric motor" question, the standing-time rule.
9. **Drivetrain chooser**: the four exclusive ways in (map tree A7), the map-set upload with its completeness check, and what a sizing user with no truck sees.
10. **On-board systems**: for each system, "VECTO row or own value", with the factor label "0.7 = VECTO; set 1.0 if your value is already electric" where the map requires it.
11. **Schedule and calendar**: working days, holidays, shutdowns, exceptions, shifts, a year calendar view.
12. **Weather picker**: source, location, station, year or years, shift, worst day.
13. **Cab climate**: the three modes and the required cab data in thermal mode. Decide where it belongs by asking what the value depends on and where a user would look for it (Bob objected strongly to finding it under the vehicle when it is driven by temperature).
14. **Depot and grid**: brownfield against greenfield, amperes or kW, building load sources including the Eloverblik connect flow, full against limited access with the what-if cut.
15. **Charging**: sizing against simulation, "size them for me" against "I choose", the charger library pick, strategy, capabilities and what they close.
16. **Price inputs**: fetched hourly prices, own file, simple prices; tariffs; price paths.
17. **Cost inputs**: a two-column electric-against-diesel layout where both exist; financing choices and what each closes.
18. **Tender**: buyer side and supplier side, several bids side by side.
19. **Knowing what is missing before Run**: the missing, defaulted and wrong list from `check()`, each item leading to its field; and the full value-and-source list. Whether this is a screen, a panel or always-present feedback is yours to design.
20. **Upload with preview and column mapping** (shared pattern).
21. **"Not available yet"** for planned inputs: how a planned page or field looks today so the structure is stable when the stage is built.

**D6. Lock rules (`lock_rules_ux.csv`).** One row per rule 1–68 of the map: screen, trigger, what appears, what disappears, animation or none, and what happens to a typed value in a field that closes (kept and restored if the user switches back, or cleared: recommend one rule for the whole tool with evidence).

### Part E. Results

Deliver `results_ux.csv` (one row per result), `results.md` (screen by screen) and wireframes.

**E1. Result list.** Start from Part F of the input map, PR #35's `results_register.csv`, the gap analysis and the outputs note. One row per result. Columns: `id`, `result`, `unit`, `question_it_answers` (in the reader's words), `audiences`, `built_from` (function output or planned stage), `available` (now / planned), `page`, `level` (headline figure / status line / section figure / chart / table / report only / document only), `form` (see E3), `form_reason` (with the Part A principle number), `compare_with` (limit, diesel, another scenario, another year, none), `uncertainty` (none / P50–P90 / range), `drill_down_to`, `documents`, `year8_related`, `start_points` (which start points produce it).

**E2. Where results live.** Decide from scratch how results are grouped and where they appear in your concept (their own screens, beside the inputs that drive them, a report-like document, or a mix), mapped to the questions each audience asks. If there is a summary view, say what it holds and what it must not repeat. Known problems to avoid from the old build: empty pages, redundant pages, checks eating the summary, and no view that pulls the fragmented inputs together (distance, stops, payload along the route, schedule).

**E3. The form of every result.** For each result choose among: a number; a number against a limit; a short sentence; a table; and the chart forms in A10. Write the choice and the reason. Bob's taste: "charts only where they help"; "not everything a graph, not all bar charts"; a bar that only repeats the number beside it adds nothing. Give special attention to these, with two or three candidate forms each and a recommendation:

- the energy balance (air, rolling, grade, inertia, brakes, drivetrain, each auxiliary, cab climate, PTO, regeneration recovered);
- the loss diagram from grid to wheel;
- the monthly table;
- energy across the year (per day, by temperature);
- hardest day against battery capacity, new and at year 8, with margin;
- P50 and P90 across weather years;
- speed, power and state of charge over a day;
- time in each driving mode;
- the fleet charging schedule;
- depot load against the connection limit; load-duration curve;
- flexibility up and down per hour;
- strategies compared; scenarios compared; several bids compared on several criteria (this is where a radar chart is usually proposed: give your verdict);
- cost over the years, break-even, cost by line, sensitivity;
- CO₂ per year and saved;
- pass-or-fail checks;
- anything on a map; anything on a calendar.

**E4. Results when only part of the tool has run.** The page and the figure when a stage is planned but not built, when a stage was skipped because the user started later, and when a result rests on a user-supplied value or on an assumption with no source. Bob's rule: no firm winter verdict until cold-weather effects are validated; winter is shown as a labelled conservative case.

**E5. Compare and scenarios.** How two or more runs are compared: which inputs changed, which results changed, and where the quick levers live.

**E6. Trust.** The run fingerprint, the list of every value with its source and mark, the model status per result, and the standing statements (for example the 10° yaw clamp). Where each appears on screen and in documents, without cluttering the result pages.

**E7. Documents.** The six documents (feasibility report, grid connection application, tender annex, financial model, grant application data, client presentation): the picker, and which results and inputs each contains, in order.

### Part F. Visual hierarchy system

Deliver `hierarchy.md`. This is the part that prevents "nothing feels important".

1. **Emphasis levels.** Define a small fixed number of levels (for example four) and what may sit at each. State the budget per screen: how many level-1 items a screen may have, and so on. Give the rule for what wins when a map, a chart, a table and a set of key figures are on one screen.
2. **Type scale and number style.** Sizes and weights for page title, section title, label, value, unit, help text, table text, chart text. Values larger than labels; units smaller than values; tabular numerals; right-aligned numbers in tables; decimal and thousands rules; how a million-krone figure is written.
3. **Spacing and grid.** One spacing scale; a column grid for 1440 and 1280 px; how groups are separated, and how any one container style is kept from being used for everything.
4. **Colour roles.** Greyscale first. One accent. Red and green only for pass and fail. A chart palette that survives greyscale printing and colour blindness. Never colour as the only signal.
5. **Screen templates.** A small set of templates that every screen of your concept uses, with fixed positions for the title, status, headline figures, primary visual, secondary visuals, tables and actions.
6. **Attention order on every wireframe.** On each wireframe mark the intended reading order 1, 2, 3, … and state what the eye should land on first and why. Then check it: view the screenshot blurred and in greyscale and say what stands out. If it is not item 1, fix the wireframe.
7. **Density.** How a screen with many fields stays calm: grouping, alignment, label position, field width matched to expected content.
8. **Motion.** Where something may animate and where it must not.

### Part G. Journeys, states and edge cases

Deliver `journeys.md`.

1. **Journeys.** At least these, each as numbered steps naming the screen, the action and what the user sees: (a) a fleet owner with route summaries and no chosen truck sizes a battery; (b) a municipality prepares a refuse-truck tender with a year-8 requirement; (c) a truck maker tests its truck on a buyer's saved project; (d) a consultant opens last month's project, duplicates it, changes the weather year and compares; (e) a charge point operator with existing chargers and a session list quantifies flexibility; (f) a finance user enters yearly energy and prices and gets cost only; (g) a housing association checks what its supply can carry; (h) a user imports a project file made by a colleague; (i) a user uploads a GPS log; (j) a user returns to a half-finished project.
2. **State diagrams** for: project (new, draft, checked, running, results current, results out of date); a field (empty, default, library, user, edited, invalid, closed by a rule); a stage (not started, user-supplied, ready, running, done, failed, not available yet).
3. **Edge cases**: a required value with no default; a library pick that leaves gaps; a partial loss-map set; a payload above the limit ("move up a vehicle class"); a PTO longer than its stop; a run that fails at one truck of fifty; an import with unknown fields; a very large fleet; a route with 400 stops; no internet for a fetch.

### Part H. Wireframes

Low fidelity, greyscale plus one accent, real labels from `inputs_ux.csv`, sample values labelled `ILLUSTRATIVE`. Each wireframe carries its attention order (Part F item 6) and margin notes citing rule numbers. Required, at 1440 px, with 1280 and 390 px variants where the layout changes:

- The three (or more) concept sketches from Part A0.
- Projects home (with projects; empty first-run state).
- New project: the start chooser (five start points).
- The shell, with the file / edit / view / help layer open.
- Import project: validation result screen.
- Every screen of your recommended concept that holds inputs.
- Entering a fleet: empty, three groups, fifty groups, changing many at once, phone width.
- A vehicle in each of its three source states (library truck, class only, manual), with its expert-level detail reachable.
- A route in each source state, including the map view and the GPS upload preview.
- Stops for a VECTO cycle, a typed route and a GPS route.
- Body equipment (PTO) with a profile.
- Schedule with a year calendar.
- Weather, and cab climate in thermal mode.
- Depot and grid in brownfield and greenfield; the Eloverblik connect flow.
- Charging in sizing mode and in simulation mode; chargers without smart charging (what closes).
- Start-point entry forms: kWh/km; session list upload; load profile upload; cost only.
- What is missing before Run (missing, defaulted and wrong items).
- Run in progress; results out of date.
- Every screen that shows results, with one variant showing a planned stage as "not available yet" and one showing a run that started at charging.
- Comparing runs.
- Choosing documents.
- The engineering view of one screen beside its client view.
- One clickable prototype (`wireframes/prototype.html`) that links the shell, projects home, the start chooser, two input screens and two result screens, so Bob can click through the frame.

### Part I. Checks on paper

1. **Tree test** (`tree_test.csv`): at least 60 tasks in a user's words, covering every screen, the menu layer, projects, import and export, each start point, and at least ten inputs that are one step away or expert-only. For each: where a user would look first under your structure, and whether it is found on the first try. Include these: "open the project I worked on last week"; "save a copy before I change the battery"; "send the project file to a colleague"; "I already know my trucks use 1.1 kWh/km"; "I have 12 chargers of 150 kW already"; "I only want to see the cost"; "say the battery must keep 80 % after 8 years"; "use my own hourly prices"; "the body has its own motor"; "add a winter route"; "switch to amperes"; "see where a default came from"; "what does CdxA mean"; "which results are not validated yet"; "undo that"; "find the tyre size field".
2. **Heuristic walk-through** of your own wireframes against Nielsen's ten heuristics and your Part A principles. List what still fails.
3. **Coverage** (Gates 1 and 2), pasted into the report.
4. **Old-problem check**: go through sections A to C of Bob's feedback log line by line and show, with a wireframe reference, that your design does not recreate each problem. Separately list anything you kept from the old build and why it earned its place.

---

## 3. Deliverables

All under `docs/research/ux-spec-2026-11/`:

1. `report.md`: a one-page summary first (the chosen concept and the runner-up; the shell in one diagram; where inputs and results live; the five start points; the ten most important design principles; the open questions), then a short section per part pointing to the detailed files.
2. `concepts.md` (Part A0), `research.md` (Part A) and `tool_comparison.csv`.
3. `shell.md` (Parts B and C) and `menu_map.csv` (every menu item: menu, item, action, shortcut, enabled when, Python call or JSON change).
4. `inputs.md`, `components.md`, `inputs_ux.csv`, `lock_rules_ux.csv` (Part D).
5. `results.md`, `results_ux.csv` (Part E).
6. `hierarchy.md` (Part F).
7. `journeys.md` (Part G).
8. `wireframes/` (Part H) and `screens/` (Gate 4 screenshots).
9. `tree_test.csv`, `coverage_check.py` and its output (Part I).
10. In `report.md`: **Questions for Bob** (each with options and evidence), **Choices I made**, **Bob to fetch** (link plus exactly what to look for), **What I kept from the old build and why**, **Seen in passing**.
11. One PR to `claude/input-map-2026-11-16`. The description lists what was done, how to open the prototype, the gate results, the top findings and the open questions.

## 4. Stop conditions

- Never edit `src/`, `hdev/`, `website-wip/`, the notebook, `docs/design/hdev-input-map.md` or any engine code. If you find an error in the input map, list it; do not fix it.
- Never build production UI. Wireframes only.
- Nothing on the landing page or marketing site.
- Never decide an item the map marks `OPEN`, `PROPOSED` or `PARKED`.
- If a tool's documentation cannot be reached, record it and move on.
