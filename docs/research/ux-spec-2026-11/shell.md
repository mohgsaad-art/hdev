# EV Scope tool: the application shell (Parts B and C of the UX brief)

Written by Claude on 17 Nov 2026, after Kiro's run stopped at its usage limit. Scope: the tool only.

**What this file is.** The frame every screen sits in: the regions of the screen, the project index, the menus, the projects home, saving, import and export, running, the three views, the conventions shared by every screen, and the five start points.

**What it is built from.** Kiro's surviving files in this folder (`concepts.md`, `research.md`, `menu_map.csv`, `inputs_ux.csv`, `lock_rules_ux.csv`, `results_ux.csv`, `tree_test.csv`), the input map (`docs/design/hdev-input-map.md`) and Bob's feedback log. I did no new research into other tools. Where I rely on Kiro's research I cite its principle number (`DP-01` to `DP-25`, defined in `research.md` section 15).

**How to read the tags.** `[MAP]` = the input map. `[KIRO]` = one of Kiro's files in this folder. `[BOB]` = Bob's feedback log, quoted. `[JUDGEMENT]` = my own reasoning, not evidence. `[OPEN]` = not decided; listed again in section 13. To keep the file readable I tag each table row or paragraph once, not each sentence.

**What is not evidence.** Nothing here has been tested with users. Every size in pixels is a proposal for the wireframe, to be changed when Bob sees it. `[JUDGEMENT]`

---

## 1. The concept in one paragraph

Kiro recommended the **Indexed workbench** (`concepts.md` A0.5). A permanent **project index** on the left names every place in the project and says what it holds. The **sheet** in the centre shows one thing at a time: one object (a vehicle, a route) or one question (does the battery last?). An optional **side panel** on the right holds checks, sources, help and the assistant. Commands (save, run, export) live in a **menu row** at the top, separate from places. `[KIRO concepts.md A0.5; DP-01, DP-02]`

This file specifies that concept. Section 13 lists what Bob must confirm, and the first question there is whether he accepts the concept at all. The runner-up is a guided step-by-step flow (`concepts.md` Concept 1).

---

## 2. The regions of the screen

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ A  MENU ROW      EV Scope │ File Edit View Project Run Libraries Help │ Find │
├──────────────────────────────────────────────────────────────────────────────┤
│ B  PROJECT ROW   Project name ▾ · Scenario ▾ · Saved │ stage strip │ View ▾ │
│                                                        Check (n) │ Run       │
├────────────────┬──────────────────────────────────────────┬──────────────────┤
│ C PROJECT      │ D  SHEET                                 │ E  SIDE PANEL    │
│   INDEX        │    Title                                 │    (optional)    │
│                │    One line: what you will find here     │    Check         │
│   Setup        │                                          │    Sources       │
│   Duties       │    … one object or one question …        │    Help          │
│   Conditions   │                                          │    Assistant     │
│   Energy chain │                                          │                  │
│   Site         │                                          │                  │
│   Business case│                                          │                  │
│   ───────────  │                                          │                  │
│   Findings     │                                          │                  │
└────────────────┴──────────────────────────────────────────┴──────────────────┘
```

| Region | Its one job | Proposed size | It must never hold | Why |
|---|---|---|---|---|
| **A. Menu row** | Commands: things you *do* to the project (save, export, undo, run, open a library, get help). | Full width, one thin row. | Places. No link to a sheet lives here. | Two lists of places is what makes two navigations fight. Commands are verbs, the index is nouns. `[DP-01]` |
| **B. Project row** | Says where you are and what state the project is in: project name, scenario, save state, the stage strip (section 8), the view switch, Check and Run. | Full width, one row, taller than A. | Inputs. Results. | Bob must always see which project and scenario he is editing, whether it is saved, and whether the results are current. `[DP-03]` |
| **C. Project index** | The only list of places. Groups of sheets, each with a status. | Left, about 260 px wide, scrolls on its own. | Commands. Fields. Result numbers. | "i should know what to expect from the pages before i go into them." `[BOB B5]` `[DP-02]` |
| **D. Sheet** | The work: one object or one question at a time. Every input and every result lives in a sheet. | Centre, takes the remaining width; content column capped (about 960 px) so lines of fields do not stretch on wide screens. | Navigation to other sheets, except plain links in text. | Core work never lives only in a side panel or a dialog. `[DP-11]` |
| **E. Side panel** | Things *about* the work: the list from `check()`, the source of the field in focus, help for this sheet, the assistant. One at a time. | Right, about 340 px, closed by default. | Any input that exists nowhere else. | "the goal is for it to be intuitive not go from overwhelming to empty overwhelming and confusing because everything is brushed under the rug." `[BOB B2]` |

There is **no bottom status bar**. Run progress and results freshness sit in the project row; short messages ("Saved", "Weather fetched") appear as a brief notice near the project row; anything the user must act on goes into the Check list. One region fewer is one thing fewer competing for the eye. `[JUDGEMENT]` (VECTO and QGIS both use a bottom status bar; this is a deliberate difference. `[KIRO research.md §2]`)

### 2.1 How the frame behaves at three widths

| Width | Menu row A | Project row B | Index C | Sheet D | Side panel E |
|---|---|---|---|---|---|
| **1440** | All seven menus by name. | Everything on one row. | Open, about 260 px. | About 840 px with the panel open, wider when it is closed. | Opens beside the sheet. |
| **1280** | All seven menus by name. | Stage strip shortens to five small state marks with the full words on hover and focus. | Open, about 240 px. | Never narrower than about 640 px. | Opens *over* the right edge of the sheet instead of squeezing it. |
| **390** (phone) | One "Menu" button that opens the same seven menus as a list. | Project name, save state and Run only. Check, view and stage strip move into the Menu list. | Becomes the project's first full screen: a plain list of the same groups and sheets. | Full screen, with a back link to the index. | Full screen, opened from a button on the sheet. |

On a phone the index is not squeezed into a strip of icons. It becomes its own screen, because a list of named places with a status each is exactly what a narrow screen shows well. `[DP-24]` `[JUDGEMENT]`

### 2.2 Two arrangements considered

| | Arrangement 1 (recommended) | Arrangement 2 |
|---|---|---|
| What | Two rows: a menu row with the seven menus by name, then the project row. | One row: a single "Menu" button plus a command search, with the project identity, Check and Run on the same row. |
| For | The "typical things" (File, Edit, View, Help) are visible by name, as Bob asked. A new user can read what the tool can do. | One row less of chrome. Closer to current web tools. |
| Against | About one extra row of height. | Commands are hidden behind one button; a user must open it to learn what exists. Feels less like a desktop-class engineering tool. |
| Phone | Collapses to Arrangement 2. | Same. |

**Claude's recommendation:** Arrangement 1 from 1280 px up, Arrangement 2 on a phone. The reason: Bob asked for the menu bar by name and wants the tool to read as "a serious, trusted industry tool" `[BOB A1]`; the engineering tools in Kiro's research (VECTO, QGIS, SAM, OpenStudio) all show their menus by name. `[KIRO research.md §2]` The cost is one thin row.

Bob's earlier standing rule said "Horizontal top menu with icons" `[BOB A2]`. That rule described the old build, where the top menu was the list of pages. Here the top row holds commands and the pages are in the index, so the two do not conflict; whether the menus carry icons is a visual choice for the UI stage.

---

## 3. The project index

The index is the single list of places. It has two parts, divided by a line: **the model** (what you enter) and **Findings** (what the tool worked out). Bob's rule "Inputs must not show outputs" `[BOB B11]` is kept by this division.

### 3.1 The places and what each promises

Sheet names come from Kiro's registers so that every input and result already has a home (`inputs_ux.csv` column `page`, `results_ux.csv` column `page`). The promises are mine, written from the inputs each sheet holds. `[KIRO]` `[JUDGEMENT]`

| Group | Sheet | "What you will find here" | Inputs in `inputs_ux.csv` |
|---|---|---|---|
| **Setup** | Start and purpose | What this project is for, where the modelling starts, the site and the project period. | none in the map yet (see section 13, Q7) |
| | Scenarios | The what-if versions of this project and what each one changes. | 5 |
| **Duties** | Fleet groups | Which vehicles do which work: how many, on which route, with which load, equipment and schedule. | 1 |
| | Vehicle | One vehicle type: where its data comes from, its mass, aerodynamics, tyres, drivetrain and on-board systems. | 52 |
| | Route and stops | One route: where it comes from, its distance and speeds, and every stop. | 22 |
| | Load and body equipment | What the vehicle carries along the route, and any body equipment that draws power. | 22 |
| | Schedule and calendar | When the vehicles work: days, shifts, holidays, shutdowns and exceptions. | 10 |
| **Conditions** | Weather and cab climate | The weather the fleet drives in, and the heating and cooling of the cab that follows from it. | 26 |
| **Energy chain** | Battery and ageing | The battery you have or want sized, how it ages, and the year-8 guarantee. | 29 |
| | Charging | The chargers you have or want sized, and how charging is managed. | 17 |
| **Site** | Depot and grid | The depot, its grid connection and what else the building uses. | 16 |
| | Flexibility | Whether and how the depot offers flexibility to the grid. | 6 |
| **Business case** | Prices and tariffs | Electricity and fuel prices, tariffs and how they change over the years. | 13 |
| | Costs and finance | What the electric and the diesel option cost, and how they are paid for. | 26 |
| | Taxes and CO₂ | Road tax, subsidies and the emission factors. | 12 |
| | Tender and bids | The buyer's requirements and each supplier's bid. Shown only when the project purpose is a tender. `[MAP rule 67]` | 6 |
| **Findings** | Decision | The answer in one place: does it work, what is needed, and what limits it. | (results) |
| | Energy and duty | How much energy each route uses and where it goes. | |
| | Battery and payload | Whether the battery covers the hardest day, new and at year 8. | |
| | Charging and resilience | When each vehicle charges and whether it leaves on time. | |
| | Site and flexibility | The depot's load against its connection, and the flexibility it can offer. | |
| | Cost and CO₂ | Cost against diesel over the years, and emissions saved. | |
| | Compare | Two or more runs or scenarios side by side. | |
| | Inputs and sources | Every value used in this run, with its source. | |
| | Documents | The six documents you can produce. | |

That is 16 model sheets in 6 groups and 9 Findings sheets: 25 places. Bob: "having 20 pages is also not right and have 3 is also not right, the balance is what makes it intuitive" `[BOB B5]`. The grouping is the answer to that: the eye meets 7 group names first, and at most 5 sheets inside any group. Whether 25 is too many is a question the wireframe should settle (section 13, Q2). `[JUDGEMENT]`

### 3.2 What an index row shows

| Element | Rule |
|---|---|
| Group name | Always visible. Under it, one grey line with the group's promise (for example "Duties: what the vehicles do"). |
| Sheet name | One line. The sheet's own promise appears when the pointer or keyboard focus is on the row, and again as the first line of the sheet itself. |
| Status | One short word or count at the right edge, from the list in 3.3. Text, never colour alone. `[DP-21]` |
| Object count | Where a sheet holds several objects (vehicles, routes, schedules), the number, for example "Vehicle 3". |
| Current place | The row for the open sheet is marked with the accent colour and a bar at its left edge. |

On a phone there is room for both lines, so every row shows its promise. `[JUDGEMENT]`

### 3.3 Status words in the index

| On a model sheet | Meaning | Comes from |
|---|---|---|
| (nothing) | Complete, nothing to do. | `check(project)` |
| `2 missing` | Required values with no default are missing. Blocks Run. | `check(project)` |
| `1 wrong` | A value fails a parser check. Blocks Run. | `check(project)` |
| `Not used` | Closed by the start point (section 12). Its values are kept. | project JSON |
| `Planned` | The stage is planned and not built. The sheet still opens, says "Not available yet" and what it will hold. `[DP-25]` The short word is used in the index because the long one, repeated on nine rows, drowned the rest in the wireframe. | model status |

| On a Findings sheet | Meaning |
|---|---|
| (nothing) | Results are current. |
| `Not run` | No run yet. |
| `Out of date` | An input changed after the last run (section 8.3). |
| `Partly` | Some of this sheet's results exist, others wait for a planned stage. |
| `Planned` | Every result on this sheet belongs to a planned stage. |

Defaulted values do **not** show in the index. They are normal, they do not block Run, and a count of them beside every sheet would make every sheet look unfinished. They are counted once, in the Check panel. `[BOB B3: "i dont like showing the sources or assumptions next to each field"]` `[JUDGEMENT]`

### 3.4 Reusable things are objects, opened from the index

Vehicle, Route and stops, Load and body equipment, and Schedule and calendar each hold **several named objects** (three vehicle types, five routes). Opening such a sheet shows the list of its objects first; picking one opens it. Fleet groups then refer to those objects by name. `[DP-09]` `[MAP §1]`

This replaces both the old "fleet table with five dropdowns" as the only way in, and the separate Templates page Bob rejected ("So now you a whole page for fucking templates?????" `[BOB B9]`). How a group picks its objects, and what a first-time user sees before any object exists, belongs in `components.md` (capability 1 and 2 of the brief) and is not decided here. `[OPEN]`

---

## 4. The menus

Every item, its action, shortcut, when it is enabled and the Python call behind it is in `menu_map.csv` (72 rows, Kiro). This section is the summary and my corrections.

| Menu | Items |
|---|---|
| **File** | New project · Open · Open recent · Save · Save as · Duplicate · Rename · Import project · Export project · Export results (CSV, spreadsheet) · Export documents (six) · Project settings · Close project · Archive project · Delete project |
| **Edit** | Undo · Redo · Reset field to default · Reset page to defaults · Find an input |
| **View** | Client view / OEM view / Engineering view · Show or hide the assistant · Show default and assumption marks · Units and number format · Language · Theme · Density · Zoom |
| **Project** | Start point · Scenarios (new, manage, compare) · Fleet growth phases · Notes |
| **Run** | Check · Run · Run from a stage · Stop · Run history · Compare runs |
| **Libraries** | Vehicles · Drivetrain numbers · Chargers · PTO profiles · Routes · Payload profiles · Schedules · Import into a library |
| **Help** | Getting started · Guide to this page · Glossary · Method and sources · Model status · Keyboard shortcuts · What is new · Report a problem · About |

### 4.1 Corrections to `menu_map.csv`

| # | Issue | What I recommend | Why |
|---|---|---|---|
| 1 | Kiro added **Cut, Copy, Paste, Select all** to Edit. | Leave them out of the menu. They still work everywhere through the browser's own shortcuts. | They are not EV Scope commands; four extra items push the two that matter (Reset, Find) down. `[JUDGEMENT]` |
| 2 | Kiro gave **New project** the shortcut Ctrl/Cmd+N, and **Open** Ctrl/Cmd+O. | No shortcut for New project. Keep the others only if the prototype shows the browser lets the page take them. | A web page generally cannot take Ctrl/Cmd+N (new window), +T or +W from the browser. This is from my general knowledge of browsers and I did not test it; check in the prototype. `[JUDGEMENT]` |
| 3 | **Archive** and **Delete** are in the File menu. | Keep them on the projects home only (section 5), not in the menu of an open project. | Deleting the project you are inside is rare and dangerous; the list is where you tidy projects. `[JUDGEMENT]` |
| 4 | The `map_status` column mixes the map's seven tags with new ones ("DOC-required; API OPEN"). | Split into two columns: `map_status` (one of the seven tags) and `build_status` (what exists in code today). | The brief's rule 3 asks for the map's tag. What is built today is useful, but it is a different fact. Not changed yet; see section 13, Q9. |
| 5 | **Scenarios** appears in the Project menu and as a sheet in the index. | Keep both, with different jobs: the menu holds the *commands* (New scenario, Compare), the sheet is the *place* that lists scenarios. | Follows `DP-01`. The scenario you are *in* is always shown in the project row. |
| 6 | **Libraries** menu and the object lists in Duties. | The Duties sheets hold this project's objects. The Libraries menu opens the shared libraries (EEA trucks, VECTO cycles, chargers) that objects are copied *from*. | A library value becomes an editable copy in the project. `[MAP rule 1, rule 13]` |

### 4.2 "Find an input"

One box, at the right of the menu row, also opened with a shortcut. It searches labels, engineering names (CdxA, Crr), glossary terms and input IDs across every sheet, and jumps to the field, opening the sheet and any closed section on the way. If the field is closed by a lock rule, the result says so and says which choice closed it. `[DP-22]` `[JUDGEMENT]`

This is the safety net for the nine tasks in Kiro's `tree_test.csv` that it predicts a user will look for in the wrong place first (for example the maximum regeneration power, which a user may look for under Battery but which lives under Vehicle).

---

## 5. Projects home

The screen a user sees after signing in, and after File → Close project. It lists every saved project so the user picks which to work on.

**List, not cards.** Each project has about ten facts worth comparing down a column (below). A table lets the eye run down "last edited" or "needs attention"; cards scatter them. `[KIRO research.md §3]` `[JUDGEMENT]`

| Column | Shows | Source |
|---|---|---|
| Name | Project name; under it, client or site in grey. | project JSON |
| Starts at | The start point in words: "Routes", "Known consumption", "Charging sessions", "Existing chargers", "Cost only". | project JSON `[MAP §D0]` |
| Fleet | Number of vehicles and groups, or "–" when the project has no fleet. | project JSON |
| Results | Which of the five stages have results: five small marks, with words on hover and focus. | last run |
| Last run | Date, and "Out of date" if inputs changed since. | last run |
| Needs attention | Count of missing and wrong values from `check(project)`. Empty when zero. | `check(project)` |
| Scenarios | Count. | project JSON |
| Last edited | Date and time. Default sort, newest first. | server |

| Feature | Specification |
|---|---|
| Opening | Click or Enter on a row opens the project where the user left it. |
| Row actions | Open · Duplicate · Rename · Export · Archive · Delete. Behind one "more" button per row, and on right-click. |
| Delete | A confirmation that names the project and says what is lost (the project, its scenarios and its runs). Archive is offered in the same dialog as the safer choice. |
| Search and sort | One search box (name, client, site). Click a column heading to sort. A filter for start point and for "Archived". |
| New and import | Two buttons above the list: **New project** (opens the start chooser, section 12) and **Import project**. |
| Sample projects | A short separate list under the user's own, labelled "Samples". Opening one creates a copy; the sample itself cannot be changed. Which samples exist is `[OPEN]`. |
| Empty state (first visit) | No table. Three choices in a row with one line each: start a new project, open a sample, import a file. Under them, one sentence on what a project is. |
| Phone | Each project becomes two lines: name and client; then start point, last edited and "needs attention". |

---

## 6. Saving

| Topic | Specification | Status |
|---|---|---|
| Model | **Autosave plus an explicit Save.** Every committed edit is saved to the server shortly after it is made. File → Save forces it now. | Recommendation `[KIRO research.md §3]`; Bob to confirm (Q4) |
| Why both | Autosave means a closed laptop loses nothing. An explicit Save is what users of engineering tools expect to find, and gives a way to retry after a failure. | `[JUDGEMENT]` |
| Save state | Always visible in the project row, as words: `Saved` · `Saving…` · `Unsaved changes` · `Could not save` · `Changed elsewhere`. | `[DP-03]` |
| `Could not save` | Stays until fixed. Offers "Try again" and "Export a copy" so work can be rescued. Nothing typed is thrown away. | `[DP-05]` |
| Leaving with unsaved changes | Only possible when a save failed. The browser's own "leave this page?" prompt is shown. | `[JUDGEMENT]` |
| Two tabs on one project | The second tab to save is told "Changed elsewhere" and offered: reload the newer version, or save mine as a copy. Never a silent overwrite. | Options for Bob (Q4) |
| Saving is not running | A save never creates results. A run records exactly which saved state it used. | `[DP-04]` |
| Scenario | Edits made inside a scenario are saved as changes on top of the base. The base is never overwritten. | Decided `[MAP §D13]` |
| Version history | **Not decided.** Option A: none; Duplicate is the way to keep an old state. Option B: named versions the user creates ("Before battery change"), with restore that makes a new version instead of deleting the newer one. | `[OPEN]` (Q5) |

---

## 7. Import and export

### 7.1 Project file

| Topic | Specification | Status |
|---|---|---|
| Export project | One file that can be imported again. Holds the base project, its scenarios, and a copy of every library record the project uses, so it opens on a colleague's account. | `[KIRO research.md §3]` |
| Results in the file | A choice at export: "Include results of the last run". Off by default. | `[OPEN]` |
| File type and name | Not decided. The name should carry the project name and the date. | `[OPEN]` (Q6) |
| Export results | CSV or spreadsheet of result tables. Cannot be imported as a project, and the dialog says so. | `[DP-17]` |
| Export documents | Opens Findings → Documents. | `[BOB C4]` |

### 7.2 Importing a project: four steps

1. **Choose** the file.
2. **Python validates it.** The UI shows "Checking…" and does nothing else.
3. **Result screen**, a full sheet with four short lists: *Read* (what was found: counts of vehicles, routes, scenarios); *Changed* (values converted because the file is from an older version); *Defaulted* (values the file did not hold); *Wrong or unknown* (values Python rejected or did not recognise, each with the reason).
4. **Open as a new project.** An import never replaces an existing project. `[DP-05, DP-06]`

If the *Wrong* list holds anything that blocks, the button reads "Open anyway and fix" and the items appear in the Check panel after opening.

### 7.3 Importing data into an input

GPS log, weather file, price series, PTO profile, loss maps, session list, load profile, meter data: all use **one shared pattern** (capability 20 in the brief, to be detailed in `components.md`): choose → preview of the first rows → say which column is what and in which unit → Python checks every row → a summary (row count, time span, time step, gaps, duplicates) → confirm. Nothing enters the project until the user confirms. `[DP-06]`

What happens when the file's time step differs from the stage's is `[OPEN]` in the map (§G2.23). The summary step therefore has room for three choices (resample, reject, run at the file's step) and none is preselected.

---

## 8. Check, Run and status

### 8.1 Check

| Topic | Specification |
|---|---|
| Where | A **Check** button in the project row, with the count of missing and wrong values on it. Always visible. |
| What it does | Calls `check(project)`. The UI only shows what comes back. `[MAP §0.4.2]` |
| What it shows | Opens the side panel with three lists: **Missing** (required, no default), **Wrong** (failed a parser check, with the parser's message), **Defaulted** (filled from `defaults.py`; a count with the list folded shut). |
| Each item | Says the sheet and the field in words, and jumps to the field when clicked. |
| When it runs | On opening a project, after each saved edit, and on demand. Whether checking after every edit is fast enough is for the build to show. `[OPEN]` |
| The full list | Every value with its source and mark is a table on Findings → Inputs and sources. The panel is the short "what must I fix" list; the sheet is the complete record. |

This answers capability 19 of the brief (knowing what is missing before Run) with always-present feedback plus a panel, not a separate "Check and run" page. `[JUDGEMENT]`

### 8.2 Run

| Topic | Specification |
|---|---|
| Where | A **Run** button at the right end of the project row. The one button on the screen that uses the filled accent colour. |
| Enabled | When nothing is missing or wrong for the stages that will run. Otherwise it stays clickable and opens the Check panel, so the user learns why. `[JUDGEMENT]` |
| What it runs | From the first stage whose inputs changed, to the last stage that is built. Run → "Run from a stage" lets the user choose. `[MAP §C0, §D0]` |
| Progress | The stage strip (8.4) shows each stage turning from "Running" to done. Run becomes **Stop** while running. `[KIRO research.md §2, VECTO]` |
| The user while it runs | Can keep reading any sheet. Editing an input during a run is allowed and marks the coming results out of date. `[OPEN]` |
| When it ends | The index marks under Findings update. The user is not moved to another sheet; a notice offers "Open Decision". |
| Failure | The stage strip shows "Failed" on the stage. The notice names the vehicle group and the cause and links to the field if there is one. Results of stages that finished stay. A run that fails for one group of fifty keeps the other forty-nine. `[OPEN: whether the engine can do this]` |
| Stop | What is kept after Stop is `[OPEN]` (`menu_map.csv` row Run/Stop). |

### 8.3 Results out of date

When an input changes after a run, the results that depend on it are marked **Out of date**: in the index, in the project row ("Results out of date since 14:02"), and at the top of each affected Findings sheet. The old numbers stay readable, clearly marked, until the next run. `[DP-21]`

Which results an input affects comes from the rerun table in the map (§C0: a route or class change reruns driver and force; payload, weather or date reruns consumption only; times rerun charging only) and from lock rule 68. Until Python can report this per field, **every** Findings sheet is marked out of date after any input change. That is honest and simple; it is refined later without changing the screen. `[MAP §C0, rule 68]` `[KIRO lock_rules_ux.csv row 68]`

### 8.4 The stage strip

A row of the five stages in the project row. It **explains**; it is not a way to move around. Clicking a stage opens a small note saying what the state means and what to do next. `[DP-02, DP-07]`

```text
Consumption        Battery           Charging          Flexibility       Cost and CO₂
Modelled           Not available yet You supplied this Not run           Not available yet
```

| State | Meaning |
|---|---|
| Modelled | EV Scope worked this out in the last run. |
| You supplied this | The user gave this stage's result directly (section 12). |
| Ready | Inputs complete, not run yet. |
| Not run | Not run, and something is missing. |
| Running | In progress. |
| Failed | The run stopped here. |
| Out of date | An input changed since the run. |
| Not available yet | Planned, not built. |

Today the strip reads: Consumption in work, the other four "Not available yet". `[MAP §C0, Part D]`

---

## 9. The assistant

| Topic | Specification | Status |
|---|---|---|
| Where | One of the four modes of the side panel. Closed by default. | `[JUDGEMENT]` |
| What it does | Reads data the user drops in (a route description, a spec sheet, a spreadsheet) and proposes values for inputs. Asks for what `check()` lists as missing. | Planned `[MAP §D14]` |
| What it never does | Choose a default. Change a value without the user confirming. | Decided `[BOB A4]` |
| Suggestions | Listed in the panel as "field → proposed value → where I read it". The user accepts each, or all. Nothing enters the project before that. | `[DP-06]` |
| Marking | An accepted value carries the mark "read by assistant" until the user edits or confirms it on the sheet. | `[JUDGEMENT]` |
| Before Run | If any accepted value is still unconfirmed, Check lists it. Whether that blocks Run is for Bob. | `[OPEN]` (Q8) |

---

## 10. The three views

Client, OEM and engineering are three views of the same project, not three projects. `[MAP §0.4.10]`

| Topic | Specification |
|---|---|
| The switch | In the project row, always visible, showing the current view by name. Also in the View menu. |
| What changes | Which fields a sheet shows (column `views` in `inputs_ux.csv`), and whether a field shows its plain label or also its engineering name (CdxA, Crr). `[BOB B13]` |
| What never changes | The index. The same sheets exist in all three views, so nothing moves when the view changes. The values. The results. `[JUDGEMENT]` |
| Counts today | Of 263 inputs: 212 appear in all three views; 34 are OEM and engineering only, shown to a client as a read-only summary; 17 are never shown as fields and appear only in Inputs and sources. `[KIRO inputs_ux.csv]` |
| A hidden field with a non-default value | The section it belongs to shows one line: "2 values set in the engineering view". Clicking it offers to switch view. A client must never run a project shaped by values he cannot see without being told. `[JUDGEMENT]` |
| OEM-only fields for a client | Shown greyed with their value, not removed. `[BOB B13]` |
| Remembered | Per user, per project. `[OPEN]` |

---

## 11. Conventions shared by every screen

### 11.1 Field marks

Bob: "i dont like showing the sources or assumptions next to each field the user dsnt care much about it ... its things that go in the report, putting it on every field looks crowded and ugly." At most "a subtle asterisk or a colour". `[BOB B3]`

So a field carries **at most one small mark**, and the source itself is one step away, in the side panel.

| State of the value | What the field looks like | What the side panel (Sources) says |
|---|---|---|
| Given by the user | No mark. Plain. | "You entered this." |
| Default from `defaults.py` | Value in grey, small mark `D` after the unit. | The default and its source tag from the map. |
| From a library or a standard table | Small mark `L`. | Which library record or VECTO table. |
| Assumption with no source | Small mark `A`. | "No source. This is an assumption." in plain words. |
| Edited (the user changed a default or library value) | Value in the accent blue, with a small "reset" control. `[BOB B13]` | The original value and where it came from. |
| Missing and required | Empty, red outline, the words "Required" under it. `[BOB B13]` | Why it is needed. |
| Wrong | Red outline, the parser's message under it. The rejected entry stays in the field. | The same message. |
| Read by the assistant, unconfirmed | Small mark `?`. | What it read it from. |
| Closed by a lock rule | Not shown. The choice that closed it says in one line what it replaced. | – |

The letters are placeholders for the UI stage; the rule is "one mark, with a text meaning, never colour alone". View → "Show default and assumption marks" turns the `D`, `L` and `A` marks off for a clean screen; missing, wrong and edited always show. `[DP-16]` `[JUDGEMENT]`

### 11.2 A value in a field that closes

One rule for the whole tool, from Kiro's `lock_rules_ux.csv` (all 68 rows): **the value is kept, hidden, and comes back if the user switches back.** It is not sent to Python while closed. `[DP-08]` `[MAP §0.4.7]`

### 11.3 Units, numbers, dates

| Topic | Rule | Status |
|---|---|---|
| Units shown | t, km, km/h, °C, kW, kWh, min, DKK. Python converts. | Decided `[MAP §0.4.4]` |
| Unit position | After the value, inside the field, in grey. Label, value and unit on one line. `[BOB B13]` | |
| Unit switch | Only where the map allows it (for example amperes or kW for a connection). The switch sits on the field. | `[MAP §D6]` |
| Decimal and thousands marks | Danish style (1.234,5) or international (1,234.5) is a setting in View → Units and number format. What Python accepts when a user types the other style is not defined. | `[OPEN]` `[KIRO research.md §6.1]` |
| Large money | Whole kroner with thousands separators and "DKK" after; millions as "2,4 mio. DKK" only in headline figures. | `[JUDGEMENT]`, for `hierarchy.md` |
| Dates and times | 24-hour clock. Dates typed, with a calendar as a help, never a calendar alone. | `[KIRO research.md §6]` |

### 11.4 Dialogs, errors, empty states

| Topic | Rule |
|---|---|
| Dialogs that block | Only for a short decision that must be made now: delete, leave with a failed save, replace a file. Never for entering data. `[DP-11]` |
| Detail inside a sheet | Bob asked for named popups for detailed inputs, titled by content ("Tyres", not "Advanced settings"). `[BOB B7]` Kiro's research prefers one named level of detail inside the sheet over dialogs. Which of the two (a named panel that opens over the sheet, or a named section that unfolds in place) is decided per screen in `inputs.md`, with a wireframe of both for one screen. `[OPEN]` (Q3) |
| Error wording | What is wrong, in which field, and what to do. No codes. The text comes from Python. |
| Empty sheet | Says what the sheet is for and offers the one first action ("Add a route"). |
| Not available yet | The sheet opens, says what it will hold when the stage is built, and shows its inputs greyed if they are already designed. No sample numbers. `[DP-25]` |
| Loading | A fetch (weather, prices, map route) shows "Fetching…" on the field it fills, and failure as a message there with "Try again". |

---

## 12. Start points: entering at any stage

A user does not have to start at consumption. `[MAP §D0]`

### 12.1 The start chooser

Shown by New project. One question, five answers, each with one line saying what the user will be asked for. No other fields on this screen except the project name.

**"What do you already know?"**

| # | Answer (wording to test) | Under it | Starts at |
|---|---|---|---|
| 1 | Work it all out from my routes | You describe vehicles, routes and schedules. EV Scope works out the rest. | Consumption |
| 2 | I know my consumption | You give kWh per km for each route, or kWh per day. | Battery |
| 3 | I know what each vehicle needs to charge | You give a list of charging sessions: arrival, departure, energy needed. | Charging |
| 4 | I already have chargers | You give the chargers and either the sessions or a load profile. | Flexibility |
| 5 | I only want the cost and CO₂ | You give yearly energy, peak power, the equipment and prices. | Cost and CO₂ |

The start point is stored in the project and can be changed at any time with Project → Start point, which shows this same screen.

### 12.2 What the index shows for each start

Derived from column `start_points` of `inputs_ux.csv` and lock rules 46 and 47. `[KIRO]` `[MAP]`

| Sheet | 1 Routes | 2 Consumption | 3 Sessions | 4 Chargers | 5 Cost only |
|---|---|---|---|---|---|
| Start and purpose, Scenarios | ● | ● | ● | ● | ● |
| Fleet groups, Schedule and calendar | ● | ◐ only if km per day is taken from the schedule | – | – | – |
| Vehicle | ● | – | – | – | ◐ one field |
| Route and stops, Load and body equipment | ● | – | – | – | – |
| Weather and cab climate | ● | – | – | – | – |
| Battery and ageing | ● | ● | ● | ◐ if the sessions need battery data | – |
| Charging | ● | ● | ● | ● | – |
| Depot and grid | ● | ● | ● | ● | ◐ if peak or tariff is needed |
| Flexibility | ● | ● | ● | ● | – |
| Prices and tariffs, Costs and finance, Taxes and CO₂ | ● | ● | ● | ● | ● |

● shown · ◐ shown in part · – marked "Not used"

**A sheet that is not used stays in the index, greyed, with the words "Not used".** It is not removed. Two reasons: the index looks the same in every project, so a user always knows where things are; and it shows at a glance what this project is *not* modelling. Opening such a sheet says why it is not used and offers "Model this stage too". `[JUDGEMENT]` (Alternative: hide unused sheets. Shorter index, but the structure changes between projects. Q2.)

### 12.3 The entry form for the supplied stage

Each start from 2 to 5 adds **one entry form** at the top of the first sheet that is used: the place where the user gives what the earlier stages would have produced.

| Start | The form | Lives on |
|---|---|---|
| 2 | A small table: route or vehicle group, kWh per km, km per day. Or one number: kWh per day. Typed or pasted. | Battery and ageing |
| 3 | The session list: upload or paste, using the shared import pattern (7.3). Columns: arrival, departure, energy needed, state of charge on arrival. | Charging |
| 4 | Chargers (count, power, capabilities), plus sessions or a load profile through the shared import pattern. | Charging, Flexibility |
| 5 | Yearly energy, peak power, equipment list. | Costs and finance |

The exact fields are in the map (§D0) and get their controls in `inputs.md`. `[MAP §D0]`

### 12.4 How results say what they rest on

Every result that depends on a supplied stage carries one line under its title: "Based on consumption you supplied" (or sessions, or a load profile). The stage strip says "You supplied this" on that stage. Findings sheets for stages that were skipped say "Not modelled in this project" and offer "Model this stage too". They never show an empty chart. `[DP-07, DP-21]`

### 12.5 Adding an earlier stage, or switching

| Case | What happens |
|---|---|
| Started with kWh/km, now wants consumption modelled | Project → Start point → "Work it all out from my routes". The Duties and Conditions sheets become active. The kWh/km the user typed is **kept** and shown on the Battery sheet as "Your earlier value, not used now", with a way to switch back. Results stay as they were until the new stage has run successfully. `[DP-08]` `[KIRO research.md §4]` |
| Started with routes, now has measured consumption | Per route: "Use my own kWh/km for this route". Closes vehicle physics, body equipment, on-board systems and weather for that route only. All typed values are kept. `[MAP rule 47]` |
| Switches to a later start | The earlier sheets turn "Not used". Nothing is deleted. `[MAP rule 46]` |

### 12.6 Combinations

| Combination | How the shell handles it |
|---|---|
| Known consumption **and** existing chargers | Start 2. On the Charging sheet the user picks "I choose the chargers" instead of "size them for me". No special start is needed. `[MAP §D5]` |
| Sessions leading into cost | Start 3. The Business case sheets are already active. |
| A housing association with residents' chargers and no routes | **No start fits cleanly.** Kiro's tree test predicts a miss here (TT-070). The nearest is start 4 or 5. The map marks housing as planned and not designed (`dep.housing`, §D15). See Q1b. `[OPEN]` |

---

## 13. Questions for Bob

| # | Question | Options | Claude's recommendation |
|---|---|---|---|
| **Q1** | Do you accept the **Indexed workbench** as the concept? | (a) Yes. (b) The guided step flow instead (`concepts.md` Concept 1). (c) Neither; say what is wrong. | (a), but decide after looking at the wireframe `wireframes/shell-main.html`. |
| Q1b | Should there be a **sixth start**: "I only want to check what my site's supply can carry"? | (a) Add it now as a planned start. (b) Leave housing associations to starts 4 and 5 until that stage is designed. | (b) for now; it is planned and not designed in the map. |
| **Q2** | The index has 25 places in 7 groups, and unused sheets stay visible as "Not used". Too many? | (a) As specified. (b) Hide unused sheets. (c) Merge some sheets (say which feel like one place). | (a). |
| Q3 | Detailed inputs: **named popups** (your 14 Nov request) or **named sections that unfold inside the sheet**? | (a) Popups. (b) Unfolding sections. (c) Decide per screen. | See both drawn for one screen in the next step, then choose. |
| Q4 | Saving: autosave plus a Save command? And two tabs on one project: warn and offer a copy? | Yes / no for each. | Yes to both. |
| Q5 | Version history? | (A) None; use Duplicate. (B) Named versions with restore. | (A) first; (B) is more server work. |
| Q6 | Project file: type and what it holds. | A single `.json`; or a zipped package with attachments (GPS logs, weather files). | Needs your view on how large attachments get. |
| Q7 | "Setup → Start and purpose" needs inputs the map does not list as IDs: project name, client, site, project purpose, period. Shall I add them to the input map as a short new section? | Yes / no. | Yes; they exist in the designs but have no IDs. |
| Q8 | Must values read by the assistant be confirmed before Run is allowed? | Block / warn only. | Block. |
| Q9 | Kiro's files use compound statuses ("FINAL / OPEN") that its own checker rejects, and the checker crashes. Fix the files, or relax the checker? | (a) Allow compound statuses in the checker. (b) Force one tag per row. | (a). A lock rule can touch fields of different status; one tag would hide that. |

## 14. Choices I made

| Choice | Why | Easy to reverse? |
|---|---|---|
| No bottom status bar. | One region fewer. Status lives in the project row. | Yes. |
| Defaulted values are not counted in the index. | They are normal; counting them makes every sheet look unfinished. | Yes. |
| Run stays clickable when something is missing and opens the Check panel. | A greyed-out button does not say why. | Yes. |
| After a run the user is not moved to Findings. | Moving the user without asking is disorienting; a notice offers it. | Yes. |
| Until Python reports dependencies per field, any input change marks all Findings out of date. | Honest and simple; no guessing in the UI. | Yes, by design. |
| Cut, Copy, Paste, Select all removed from the Edit menu; Archive and Delete removed from File. | Section 4.1. | Yes. |
| Kiro's sheet names kept unchanged. | All 263 inputs and 162 results already point at them; renaming is cheap later and should follow Bob's reaction to the wireframe. | Yes. |
| I did not use Kiro's idea of a "small latest result line" on input sheets. | "Inputs must not show outputs." `[BOB B11]` | Yes. |

## 15. What comes next

1. Bob looks at `wireframes/shell-main.html` and answers Q1 and Q2.
2. `journeys.md`: the ten journeys and the five start points walked through screen by screen.
3. `inputs.md` and `components.md`: every sheet, starting with Fleet groups and one Duties sheet drawn both ways for Q3.
4. `results.md` and `hierarchy.md`.
5. The remaining wireframes and the clickable prototype.
