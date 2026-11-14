# Kiro prompt: where every input and result belongs in the EV Scope UI, plus a landing page review (14 Nov 2026)

Owner: Bob. Repo: `mohgsaad-art/hdev`. **Today's date is 14 November 2026.** When you research, look for material up to this date (VECTO releases and its user manual, current tool websites and manuals, design-system guidance from 2023–2026), not only older sources.

**Run the whole job in one uninterrupted pass.** Do not stop to ask Bob anything. If something is unclear, choose the option that changes the least, write it under "Choices I made", and carry on. Open **one PR** at the end.

**Branch:** create `ui-ia-research-2026-11` from **`claude/ev-scope-site-wip`** (not from `main`: the current tool and landing page live only on that branch, in `website-wip/`). Copy this prompt to `docs/research/inputs/ui-ia-2026-11/` as the first commit if it is not already there. Put everything new in `docs/research/ui-ia-2026-11/`. Open the PR from your branch to `claude/ev-scope-site-wip`.

---

## 0. Rules for this job (read first)

1. **This is research and design proposals, not a rebuild.** Do not edit anything in `website-wip/`, `src/`, the notebook or any engine code. You may build low-fidelity wireframes as new files under `docs/research/ui-ia-2026-11/wireframes/` (plain HTML, greyscale, no branding effort, clearly labelled "wireframe").
2. **Every input must have a home.** Bob's main complaint on 14 Nov was "Half the inputs are missing". Your input register (Part A) must cover **every** input in the inventory and in the appendices, **every** input of functions still to come, and anything you find in VECTO or other tools that HDEV would need. An input may be marked "hidden" (filled by `defaults.py`, never typed), but it must be listed and placed.
3. **The year-8 battery check is mandatory everywhere it applies.** Bob, 14 Nov: "including the 8 year thing which you have just forgotten". Danish tenders state usable battery capacity guaranteed at year 8 (Ressourceindsamling: ≥ 80 % after 8 years, bidder states it, free replacement if lower; ARC 2022: max 25 % loss in 8 years). The tool must take it as an input and report the hardest day (winter) at year-8 capacity. Treat it as a first-class topic in Parts A, B, D and E.
4. **No invented numbers.** Every value you quote comes from a named source with a link, or is labelled `ILLUSTRATIVE` (only in wireframes) or `NO SOURCE`. You are not asked to choose default values; where the register needs a default, copy it from the inventory with its tag, or write `OPEN`.
5. **Tag every statement in the report:** `[DOC]` (a project document in this repo, with path), `[TOOL]` (another tool's manual, website, help page or code, with link and date read), `[VECTO]` (VECTO source file and lines, or the VECTO user manual, version), `[GUIDE]` (design or usability guidance, e.g. NN/g, GOV.UK Design System, IBM Carbon, WCAG, with link), `[TEST]` (your own check on the current build, with screenshot path), `[JUDGEMENT]` (your own reasoning), `[OPEN]`. Never pass a judgement off as a finding. Say for each external source whether you read the full page or document, or only a summary or snippet.
6. **Never decide an open design choice for Bob.** Show the options with evidence. When you recommend, label it "Kiro's recommendation" and give the reason.
7. **Plain English** in everything. Short sentences. Define technical terms the first time. Refer to the owner only as "Bob". Bob reads on a phone often: tables and short lists beat paragraphs.
8. **Explain why.** Bob, 12 Nov: don't list changes "like I'm a machine". For each proposal, say what problem it solves, which of Bob's feedback lines it answers (quote the line from `bob-feedback-log-ui-and-landing.md`), and what it costs.
9. **Architecture rules that the UI must respect (decided by Bob, not up for review):**
   - The UI is a dumb form. All logic, defaults and calculations are in Python. The UI sends raw JSON (one project JSON with sections; reusable libraries are separate; a scenario is base + a list of changes; the original is never overwritten).
   - Defaults live only in `defaults.py`, each with value, unit, source and label. The parser cleans, converts units and checks inputs. The engine takes SI values only.
   - The UI shows tonnes, km, kWh, °C, km/h, kW; the parser converts.
   - Inputs that users can't realistically give are not asked; they get sourced defaults (shown as such in the report) or are derived from data already asked for.
10. **Licences and ethics.** Describe other tools' patterns in your own words. Don't copy their text, screenshots or code into the repo. No reverse engineering. If a manual is behind a login or paywall, add it to "Bob to fetch" with the link.

### 0.1 Pitfalls from earlier Kiro PRs (don't repeat them)
- Claiming "done" without evidence. Every claim in the summary points to a file, a CSV row, a screenshot or a source.
- Leaving documents unopened and writing `NOT FOUND`. Try every route to the full text (official site, PDF, archive.org, the vendor's help centre, YouTube walkthrough transcripts); otherwise put it on "Bob to fetch" with the link and exactly what to look for.
- Re-describing a tool from memory. Only describe what you read or saw, and say what and when.

---

## 1. Context

**EV Scope** (the engine is called HDEV) sizes the electrification of vehicle fleets and their depots: battery size per vehicle, charger size and count, the grid connection, flexibility, cost against diesel and CO₂. It is built to be auditable against VECTO, the EU's official heavy-duty simulation tool (Regulation (EU) 2017/2400). The goal is to be "PVsyst for EVs": a brand-neutral, auditable report that buyers, banks, grid companies and suppliers accept.

**Who uses it** (each needs to find their part fast):
- **Fleet owners and operators** (haulage, refuse collection, distribution): which vehicles can switch, battery, chargers, grid, cost.
- **Municipalities and public buyers** (refuse, utilities): tender requirements from their own routes, budget years, brand-neutral comparison.
- **Housing associations** (from 2026 residents in Denmark have a right to a charge point unless a real capacity limit prevents it): what the building's supply can carry.
- **Truck makers (OEMs) and dealers:** proving their spec on the buyer's routes, year-8 battery at winter, offer comparison.
- **Charge point operators and grid companies:** depot load hour by hour, connection size in amperes, full vs limited access (FNA/BNA), flexibility.
- **Two-sided inputs (planned):** the owner side enters operations; the supplier side enters spec-sheet values that override standard values on the same engine. OEM-only fields are greyed for clients. An engineering view shows physics names (Crr, CdxA); the client view hides them.

**What exists today:** read `docs/research/inputs/ui-ia-2026-11/current-build-map-2026-11-14.md` first. It maps the demo tool and landing page in `website-wip/`. The demo tool runs a stand-in JavaScript model only to show the UI. The real engine is Python and is mid-review (status in `project-notes/claude_status-engine.md`).

**What Bob thinks of it:** read `docs/research/inputs/ui-ia-2026-11/bob-feedback-log-ui-and-landing.md` in full. It holds Bob's own words. Your proposals are judged against it.

### 1.1 Inputs to read (all in the repo)

| What | Path |
|---|---|
| This prompt | `docs/research/inputs/ui-ia-2026-11/kiro-prompt-ui-ia-results-landing-research-2026-11-14.md` |
| Bob's feedback log (UI + landing), his words | `docs/research/inputs/ui-ia-2026-11/bob-feedback-log-ui-and-landing.md` |
| Map of the current build | `docs/research/inputs/ui-ia-2026-11/current-build-map-2026-11-14.md` |
| **Input inventory, 13 Nov (14 pages of inputs, with defaults and source tags)** | `docs/research/inputs/ui-ia-2026-11/hdev-ui-input-inventory-2026-11-13.md` |
| Older input list (26 Oct, includes engine argument names) | `project-notes/claude_ui-input-list-2026-10-26.md` |
| Engine status, every function's code of record and open items | `project-notes/claude_status-engine.md`, `claude_session-closeout-2026-11-12-force-paux-pto.md`, `claude_session-closeout-2026-11-13-hvac-final.md`, `claude_handover-function-finalization-2026-11-12.md`, `claude_pto-knowledge-2026-11-12.md`, `claude_kiro-prompt-consumption-engine-review-2026-11-13.md` |
| Results gap analysis (VECTO, PVsyst, COWI, tenders) | `project-notes/claude_results-gap-analysis-2026-10-26.md` |
| Outputs to add (FNA/BNA, year-8, tender help, battery passport) | `project-notes/claude_outputs-fna-bna-battery-passport-2026-10-28.md` |
| Tool description, market facts, tenders, grants, revenue streams | `project-notes/claude_handover-tool-and-streams-2026-10-28.md`, `claude_doc-findings-grants-grid-tenders-2026-10-28.md`, `claude_chat-summary-grants-tenders-streams-2026-10-28.md` |
| What other tools do (engine and features) | `project-notes/claude_review-other-tools-all-features-2026-11-09.md`, `claude_findings-other-tools-review-2026-11-09.md`, `claude_session-closeout-2026-11-09-tools-review.md`, `claude_hdev-landscape-analysis-2026-09-20.md`, `claude_chat-summary-hc-competitors-strategy-2026-10-28.md` |
| Data library design (vehicle and charger libraries) | `project-notes/claude_data-library-design-draft-2026-11-07.md`, `claude_status-data-library.md`, `docs/research/data-library-sources-2026-11/`, `docs/research/data-library-chargers-2026-11/` |
| VECTO defaults and payload design | `project-notes/claude_vecto-declaration-defaults-2026-10-07.md`, `claude_payload-resolver-design-2026-10-07.md` |
| Landing page history (likes, dislikes, brief, copy notes) | `project-notes/claude_landing-likes-dislikes-2026-10-29.md`, `claude_landing-page-brief-2026-10-28.md`, `claude_landing-copy-notes-2026-10-28.md` |
| Platform scope brainstorm | `project-notes/claude_brainstorm-2026-10-24-platform-scope.md` |
| Knowledge base (EU regulation extracts, Danish grid connection rules, charging guides, case studies, tenders) | `project-notes/knowledge-base/` |
| Kiro's earlier scaffolding (registry of fields, slots, levers) | `src/registry/`, `src/resolver/`, `.kiro/specs/` |
| Earlier landing mock-ups | `docs/design/ui-mockup/` |
| The current tool and site (open in a browser) | `website-wip/out/ev-scope-site.html`, `website-wip/out/ev-scope-tool.html`; sources in `website-wip/src/` (`model.js` holds the field registry `DEFS`) |
| The landing page as Bob uploaded it on 13 Nov | `website-wip/assets/original-site.html` |
| VECTO source | clone `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/VECTO` (top-level folders include `VECTO/` (classic GUI), `VECTO3GUI/`, `VECTO3GUI2020/`, `VECTOAux/`, `Documentation/` and `Generic Vehicles/`, checked by Claude on 14 Nov; read the job, vehicle, auxiliaries and output definitions and any user manual under `Documentation/`) |
| Open-source tools (Bob's forks) | `mohgsaad-art/fastsim`, `mohgsaad-art/blast-lite`, `mohgsaad-art/eflips-depot`, `mohgsaad-art/spice_ev`, `mohgsaad-art/dt-cargo`, `mohgsaad-art/acnportal` |

`project-notes/` means `docs/research/inputs/ui-ia-2026-11/project-notes/`.

---

## 2. The parts

### Part A: the master input register (the core of this job)

Build `inputs_register.csv` (and a readable `inputs_register.md` grouped by proposed page). **One row per input**, covering:
- every row of the 13 Nov inventory;
- every argument of every engine function in Appendix A (finalised and planned), mapped back to the user input or default that fills it;
- every input of the functions still to come (Appendix A.2), using what the project notes say they will need; where the notes don't say, research what comparable tools ask for (Part C) and mark the row `PROPOSED, needs Bob`;
- every field in the current demo (`website-wip/src/model.js`, `DEFS`) and say whether it matches an inventory row.

Columns:

| Column | Meaning |
|---|---|
| `id` | short stable key, e.g. `veh.curb_mass` |
| `label_ui` | plain-English label as a user would read it |
| `unit_ui` / `unit_engine` | e.g. t / kg |
| `feeds` | engine function(s) and argument(s), or report/document only |
| `status` | built / designed / planned / open (from the docs) |
| `who` | client / OEM / standard (tool) / external fetch |
| `fleet_user_can_give` | yes / usually / rarely / no, with one-line reason |
| `default_and_tag` | copied from the inventory (STD, LIB, EXT, ASSUMP, NO SOURCE, OPEN, none) |
| `depends_on` | the physical or business thing the value belongs to: the vehicle, the body, the battery, the route, a stop, the load, the shift/calendar, the depot site, the grid connection, the weather/location, the market (prices, taxes), the company (finance), the tender, the scenario |
| `changes_per` | how often it differs: per project / per vehicle type / per fleet row / per route / per stop / per hour / per year |
| `conditional_on` | which choice makes it appear (e.g. HVAC mode = thermal) |
| `required` | required to run / optional / hidden |
| `input_method` | number / dropdown / segmented choice / toggle / table / upload / profile picker / connect (e.g. Eloverblik) / derived (read-only) |
| `proposed_page`, `proposed_section` | from Part D |
| `tier` | main (on the page) / named popup / engineering view / hidden (defaults.py) |
| `popup_name` | if tier = named popup: the popup's title (what it holds, not "Advanced") |
| `reasoning` | one or two sentences: why this page, why this tier, citing the rule from Part D |
| `year8_related` | yes/no |
| `audiences` | which audiences care |
| `in_current_demo` | yes / no / partly, with the demo field key |
| `notes` | open questions, conflicts between documents |

At the end of the register: a count by page and tier, a list of **inventory rows you could not place** (should be zero), a list of **inputs found in other tools that HDEV has no row for** (candidates only, each with source), and a list of **conflicts between project documents** (e.g. a default stated differently in two notes).

### Part B: the master results register

Build `results_register.csv` (+ `.md` grouped by proposed result page). One row per result: everything in Appendix B, everything in the gap analysis and the outputs note, everything the current demo shows, and what other tools show (Part C) that HDEV lacks (marked as candidate).

Columns: `id`, `result` (plain label), `unit`, `question_it_answers` (in the reader's words, e.g. "Will the battery still do my hardest winter day in year 8?"), `audiences`, `produced_by` (function or stage; `planned` if not built), `status`, `proposed_page`, `level` (headline figure / status line / section / table / chart / report only / document only), `chart_type_and_why` (or "no chart: a number says it"), `documents` (which of the six documents include it), `year8_related`, `source_of_requirement` (tender, VECTO output, PVsyst convention, Bob, etc.), `in_current_demo`.

### Part C: research how other tools organise inputs and results

For each tool, read its official manual, help pages, documentation, website and, where available, its code or GUI source. Write one section per tool and one comparison table. For each tool record:
1. The top-level navigation: steps, tabs or pages, and their names and order.
2. How inputs are grouped (by physical object, by workflow step, by expertise level).
3. How detailed or expert inputs are hidden: popup/dialog, accordion, side panel, "expert mode" toggle, separate file editors. Note the **names** of such dialogs (e.g. PVsyst's "Detailed losses").
4. How defaults and their sources are shown (inline tags, colours, a separate report list).
5. How libraries/templates are handled (component databases, picking a vehicle or module, editing a copy, "save as").
6. How tables of many similar items are edited (fleet, routes, strings of modules, chargers) and bulk-edited.
7. How results are structured: overview, pages, figures, charts, the report and its section order.
8. How runs/scenarios are compared.

Tools, in order of priority:
- **VECTO** (the EU tool; job file editor, vehicle editor tabs, auxiliaries, driving cycles, engineering vs declaration mode, output files MRF/CIF/VIF, `.vsum`/`.vmod`, VECTO 3 GUI and the 2020 GUI). Use the user manual of the latest release you can find and the GUI source in the clone.
- **PVsyst** (the model EV Scope wants to be; project → system → detailed losses → simulation → report; its report layout and loss diagram).
- **NREL SAM (System Advisor Model)** (input pages by category in a left list, each page with sections; macros; parametrics).
- **HOMER Pro / HOMER Grid** (component library, schematic, sensitivity, optimisation results table).
- **PV*SOL** or **Sunny Design** (guided steps for less expert users).
- EV fleet and depot tools: **Dynamon**, **BetterFleet**, **Flowemo**, **Decade Energy**, **Chargepoly**, **ChargeSim** (if it exists under that name, check), **Geotab EVSA**, **Zeti**, **ElectricFleets/Sawatch** or similar you find; and NREL **EVI-Pro / EVI-X**, **T3CO**, **FASTSim** (inputs only), **eFLIPS**, **SpiceEV** (input file structure).
- The **COWI truck TCO sheet** (described in `project-notes/claude_handover-tool-and-streams-2026-10-28.md` and the gap analysis; the file itself is not in the repo: if you need it, put it on "Bob to fetch").
- Design guidance: **NN/g** (progressive disclosure, modal vs non-modal dialogs, accordions, form design, data tables, dashboards), **GOV.UK Design System** (question pages, "one thing per page", check answers page), **IBM Carbon** (EV Scope uses IBM Plex; Carbon's modal, data table, form, notification and empty-state guidance), **WCAG 2.2 AA**. Also **Stephen Few / NN/g** guidance on dashboard and KPI hierarchy.

For tools you can't access in full, say what you could see and add the rest to "Bob to fetch".

### Part D: the input information architecture (proposal)

Answer Bob's core request: what categories (pages) are needed, what goes on each, what goes in popups or dropdowns, and why. Bob's tests: "i should know what to expect from the pages before i go into them"; "20 pages is not right and 3 is not right"; "not ... everything in just one pop up"; things belong where they physically belong (cab heating with weather, not the vehicle).

1. **Write the placement rules first**, as numbered rules Bob can check, derived from Part C and the guidance. For example (your rules may differ; justify them): an input goes on the page of the thing it describes (`depends_on`); a value that most users leave at a sourced default goes in a named popup; a value only OEMs or engineers can give goes in the engineering view or the OEM side; a choice that changes which other inputs appear is shown on the page, not in a popup; a per-stop or per-hour value goes in a table, not in single fields; a popup holds one coherent topic and is named after it; nothing in a popup is required to run unless the popup shows a red count.
2. **Propose the page list** (names a user would predict), with one sentence each on what it holds and what it doesn't. Include where the fleet table, the five template types (vehicle, route, payload, PTO, schedule), the stop table, the libraries (vehicle library from EEA data, charger library), scenarios and the run check go. Bob has already rejected: a separate "Assumptions" page, a separate "Templates" page, cab heating under the vehicle.
3. **For each page:** sections in order, main fields, named popups with their contents, tables, conditional parts, and empty/first-run state. Show it as an outline and as a wireframe (`wireframes/inputs-<page>.html`).
4. **Templates and the fleet table:** how a user creates, picks, edits, copies and bulk-applies templates without a templates page; how "link or copy" on editing a shared template should work (show the options, Bob decides); how a new user gets started without building five templates first (e.g. a guided first row, "start from a sample", "describe your fleet"); how the table stays usable at 10+ columns and 50 rows and on a phone.
5. **The stop table:** what it shows per route source (VDRI, typed, GPS, AI), which columns are locked per source (inventory section 2), how payload and PTO per stop are edited, how 400 stops stay usable (filters, "apply to all", ranges).
6. **Client view, OEM view, engineering view:** what each shows and how a user switches; how library picks prefill fields and which become editable copies.
7. **Source marking:** Bob wants no source text beside fields; at most a subtle asterisk or colour, with sources in the report. Propose the marking scheme (sample, standard, assumption, your value, missing, NO SOURCE) and where the full source list lives.
8. **Tree test on paper:** write 40 tasks in a user's words and show where each lands under your proposal and under the current demo (e.g. "set the diesel price", "say the battery guarantee is 75 % at year 8", "enter cab heating set-points", "add 20 more refuse trucks on the same route", "make stop 12 longer", "mark the depot as limited access", "test a cold year", "upload my GPS log", "pick a Volvo FE Electric from the library", "set the tender's battery score curve", "add a second shift", "say a charger can be out of service", "enter the AdBlue price", "enter my own hourly prices", "say the body has its own electric motor"). Each task should be found on the first try from page names alone. Mark any task that needs two guesses.
9. **Two alternative structures** besides your recommendation (e.g. organised by workflow step vs by physical object vs by audience), with the trade-offs. Then "Kiro's recommendation" and why.

### Part E: the results information architecture (proposal)

Bob: "A lot of the outputs and results look merged because of poor visual hierarchy and bad alignment, it just looks like a sentence not results with million krona value." Earlier: some pages were empty and some redundant; the Overview should also show input context as visuals.

1. **Result page list** with one sentence each, mapped to the questions each audience asks (Part B). Where do these go: energy balance (VECTO-style split), monthly balance table (PVsyst-style), loss diagram, P50/P90 across weather years, **year-8 checks** (hardest day at year-8 capacity, winter at year 8, minimum usable kWh at year 8 for a tender, margin, predicted battery passport values after 8 years), charging sessions table, robustness cases (one charger down, late return, cold week), grid in amperes and kW with fee and lead-time band, FNA vs BNA, flexibility products, cost year by year, NPV, sensitivity, CO₂ incl. life cycle, offer sheet (several bids scored with the buyer's weights), audit block.
2. **Hierarchy per page:** page name, one status line, the headline figures (how many, which, units), then sections. Specify type scale and alignment rules (e.g. numbers right-aligned in tables, units smaller than values, labels above figures). Give an annotated wireframe for Overview, Battery (with year 8), Grid and Cost (`wireframes/results-<page>.html`).
3. **The Overview:** what it shows (input context as visuals, key figures, checks), and what it must not repeat.
4. **Charts:** for each chart, the question it answers and why that chart type. No chart where a number says it.
5. **The report and the six documents:** propose the full feasibility report outline (PVsyst-style: project summary, system parameters, assumptions and sources list, main results, monthly table, loss diagram, year-8 section, charging, grid, cost, CO₂, audit block) and, for the other five documents (grid connection application, tender annex, financial model, grant application data, client presentation), which results and inputs each contains and in what order. Use the real field lists from the knowledge base (Radius screening fields, Vejdirektoratet application fields, tender requirements and score curves).
6. **Compare runs / scenarios:** how two or more runs are compared (inputs changed, results changed), and where scenario levers live.

### Part F: audit of the current build

Open `website-wip/out/ev-scope-site.html` (and the tool through "Try the demo") in headless Chrome at 1440×900, 1280×800 and 390×844, day and night themes, English and Danish. Take screenshots into `docs/research/ui-ia-2026-11/audit/`.
1. **Against Bob's feedback log, line by line:** met / partly / not met, with the screenshot that shows it.
2. **Heuristic review** (Nielsen's 10 heuristics) of the tool's setup pages, popups, fleet table, stop table, results and documents. Each issue: where, what, severity (blocker/major/minor), screenshot, which rule from Part D it breaks.
3. **Accessibility** against WCAG 2.2 AA: keyboard path through the fleet table and popups, focus visibility, dialog focus trap, contrast, labels, target sizes, reduced motion. Use axe-core if you can run it; say which tool you used.
4. **Inputs coverage:** which inventory rows exist in the demo, which don't (from Part A).
5. **Performance:** the site is one ~3 MB file. Measure load and first paint; list the biggest assets.

### Part G: landing page research and proposals

The landing page is `website-wip/out/ev-scope-site.html` (built from `website-wip/assets/site_stripped.html` + `website-wip/build_site.py` + `website-wip/site_v2.py`). Bob's history of likes and dislikes is in the feedback log and `project-notes/claude_landing-likes-dislikes-2026-10-29.md`. **Keep what he likes:** day/night effect and images, the payload image that changes, the chargers that change, the report types, the logo, the parking-sign blue, subtle motion. **He dislikes:** selling copy and jargon, a paragraph in the hero, audiences listed twice, "documents you can take away" blocks, a documents section that is not smooth, cursor-following tiles, long text, SVG illustrations, cards everywhere, the generic AI/SaaS look, invented claims.

1. **Research** how comparable B2B engineering and energy software presents itself and routes different audiences: PVsyst, HOMER (UL Solutions), SAM, Dynamon, BetterFleet, Flowemo, Decade Energy, Chargepoly, Geotab EV, Elento (content only), Patensify (Bob's motion reference), plus 3–5 more you find that are known for clear technical B2B pages. For each: hero (what it says it sells, in how many words), how audiences find their part (menu by role, tabs, separate pages, a chooser), how the product is shown (screens, video, interactive), how documents/outputs are shown, tone (helpful vs selling), proof (sources, standards, validation). Screenshot references go in the report as links, not copies.
2. **Section-by-section review** of the current page: purpose, does it work (with screenshot), which feedback line it answers or breaks, and a proposal.
3. **Audience routing:** propose how each audience (fleet owners, municipalities, housing associations, OEMs/dealers, CPOs/grid companies) reaches its part in one step without the audiences being listed twice. Consider a role menu in the header, separate short pages per audience (`/for/municipalities`), or a single chooser. Bob: "i want to go to the part that concerns me and that's what sells".
4. **Copy:** write a proposed text for every block on the page, from the reader's point of view, plain and specific, no slogans, no claims without a source in the project notes. For each audience: the decision they face, one real example from the project notes (tenders, grid lead times, the year-8 guarantee, the 2026 right to charge, FNA/BNA), what the tool gives them. Include **year 8** where it matters (fleet owners, municipalities, OEMs). Mark every factual claim with its source path. Provide Danish only if you can cite a native-quality source for terms; otherwise English only and say so.
5. **Documents section:** propose an interaction that is smooth and lets visitors pick (Bob: "letting them pick"; "the document spread is great"; the fan must not cover its description; no "you get dumped with 6 documents"). Say what each document is for in one line and who reads it.
6. **Demo preview:** how much of the tool to show, which screens, and the cursor behaviour ("smooth ... not overwhelming ... enough with smooth cursor to guide the eye").
7. **Visual hierarchy:** a type scale and spacing system for the page, and where the current page breaks it.
8. **Mobile**, **accessibility** (WCAG 2.2 AA, reduced motion), **performance** (images as base64 in one file vs separate files), **legal** items already in place (Privacy, Terms, no cookies, no third-party requests) and anything missing for an EU B2B site.
9. Wireframes: `wireframes/landing-desktop.html` and `wireframes/landing-mobile.html` (greyscale, real proposed copy, image placeholders named after the existing images).

---

## 3. Deliverables

1. `docs/research/ui-ia-2026-11/report.md`, in this order:
   - **Summary first (one page, plain English):** the proposed input pages and popups in one table; the proposed result pages in one table; the top 10 problems in the current build with severity; the top landing-page changes; open choices for Bob.
   - Part A summary (counts, unplaced rows = 0, candidates, conflicts).
   - Part B summary.
   - Part C: one section per tool, then the comparison table.
   - Part D: placement rules, page list, page outlines, templates and fleet table, stop table, views, source marking, tree test, alternatives, recommendation.
   - Part E: result pages, hierarchy rules, overview, charts, report and document outlines, compare.
   - Part F: audit.
   - Part G: landing research, section review, routing, copy proposal, documents, demo, hierarchy, mobile/a11y/performance/legal.
   - **Questions for Bob** (each with options and evidence), "Choices I made", "Bob to fetch" (links + exactly what), "Seen in passing".
2. `inputs_register.csv` + `inputs_register.md`; `results_register.csv` + `results_register.md`; `tool_comparison.csv`; `tree_test.csv`.
3. `audit/` screenshots, `wireframes/` HTML files (each opens offline, no external requests).
4. One PR to `claude/ev-scope-site-wip`. The description lists what was done, how to open the wireframes, the top findings, the open questions, and the "Bob to fetch" list.

## 4. Stop conditions
- Never edit `website-wip/`, `src/` or engine code. Never decide an open design choice for Bob.
- If a tool's documentation can't be reached, record it and move on.

---

## Appendix A: functions and their inputs

### A.1 Engine functions (finalised or under review; full code in `project-notes/claude_status-engine.md` and the 12–13 Nov closeouts)

| Function | Status | Arguments (engine names) | Filled from |
|---|---|---|---|
| `crosswind_engine` | final | vehicle height, CdxA(0), yaw coefficients a1–a3 (VECTO `VCDV_parameters.csv` by vehicle type), `v_ref` 5.028 m/s at `h_ref` 10 m (DMI; HDEV decision), wind exponent, speed grid 60–130 km/h, yaw clamp 10° (HDEV decision, stated in every report) | vehicle page, defaults |
| `payload_engine` | final | `stop`, `shape` (constant / linear / custom), `payload_start`, `payload_end`, `payload_custom` | payload template, stop table |
| `pto_engine` | final | `stop`, `is_on` (per stop), `stop_pto_t`, `stop_pto_w`, `drive_pto_t`, `drive_pto_w`, `stop_pto_eff`, `drive_pto_eff` | PTO template, stop table |
| `driver_model` (+ `interp1`, `decel_distance`, `coast_distance`) | final | waypoints `wp_s, wp_v, wp_stop, wp_grade`; `.vacc` curves; `dt`; reference `coast_mass`; `m_red_wheels`; `cdxa_v`, `cdxa`; `Crr`, `beta`; `rho`, `g`; drag table `drag_v`, `drag_F`; `P_max`; driver constants (`lac_*`, `df_*`, `os_*`, `brake_margin`, `v_min_coast`) | route, vehicle, defaults |
| `force_engine` | final (12 Nov) | `g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red, J_rotor, i_total` | vehicle (tyres, drivetrain) |
| `P_aux` | final | ES, PS, HVAC, SP, Cond powers; always-on PTO; factors ES 0.7, PS 1.0, HVAC 1.25 (1.0 in thermal mode), SP 0.7, Cond 1.0, PTO eff | on-board systems, weather (HVAC) |
| `SP_power_helper` | final | steering baseline table, steered axles and technology per axle | vehicle |
| `ssm_total_w`, `climate_lookup`, `HVAC_thermal` | final (13 Nov) | ambient temperature and sun per hour; cab surface, U, people, window area, cab volume; heater type → COP and share tables; max heating/cooling power; ventilation rates; set-points 18/23/17 °C; constants (heater eff 0.93, ventilation power 0.56, heat per person, clouding, boundary 17 °C, g 0.95, solar factor 0.25, waste heat 0); fresh air Q (100 m³/h for 2 persons, Dvorak preprint); p, R, cp | weather page (cab heating), defaults |
| `consumption_engine` | under review | driver rows; force coefficients; vehicle mass + payload per waypoint; weather per hour (temperature, W1/W2 crosswind tables); aux per row; PTO outputs; drivetrain efficiencies or loss maps; regen rules (`v_no_regen`, `P_regen_max`, regen efficiency); mechanical vs electric drive PTO ("does the body have its own electric motor?") | vehicle, weather, PTO |
| Loss lookup (planned small function) | decided 13 Nov | loss maps (VECTO generic E2 / EU standard values: gearbox Annex VI App. 8, axle Annex VII App. 3, motor Annex Xb App. 8) **or** separate drive/regen efficiency numbers | vehicle (drivetrain) |
| Parser / `defaults.py` | open | every lookup: VECTO reference payload, body/trailer masses, CdxA, height, `.vacc`, aux tables, drag table, units, checks | (hidden) |

### A.2 Functions still to come (inputs to place; status from the project notes)

1. **Battery model** (OCV + Ri, SOC; Annex Xb App. 10 standard values as fallback): installed kWh, usable share (VECTO ≈ 0.855 × installed, to verify), OEM usable kWh, nominal voltage, OCV points, Ri table, max charge rate (C) by SOC, battery mass, chemistry, max DC charging power and connector, battery heating/conditioning (hook, planned), start SOC, target SOC, SOC window.
2. **Battery ageing and the year-8 check** (planned): guaranteed usable capacity at year 8 (%), warranty years and km, SoH curve or table (OEM), cell chemistry, cycle and calendar life, battery replacement (year, cost), link to residual value (KIT formula: residual = (scrap 15 % + 85 % × remaining SoH) × battery cost, see the tools review). Battery passport fields (DIN DKE SPEC 99100): rated capacity and fade, power and fade, internal resistance and its increase, round-trip efficiency, expected lifetime, state of certified energy.
3. **Battery sizing mode B** (size it, iterate mass): glider mass, pack energy density (kWh/kg), step size, sizing rule (hardest day at year 8 with margin), SOC buffer.
4. **Charging engine:** sizing mode (P = E/t) and simulation mode (time step: must come from Energinet product specs, OPEN); strategies shown to clients as Lowest cost / Grid-friendly / Ready earliest (internally ASAP, JIT, EDF, cost-based; no smart charging → ASAP only); charger power per point, number of points, charger type (AC on-board / DC), connector, charger efficiency/losses (4-leaf: 3–4 %), load factor 0.85; truck-to-point assignment and shared chargers; ready-by time; `charger_available` per stop (opportunity charging at the tip site or between shifts: no producer yet, OPEN); public charging share and price; charger outage (robustness case); late return; plug-in discipline.
5. **Calendar / year run:** operating weekdays with optional per-day reduction factor, Danish public holidays (computed; Store Bededag abolished from 2024), shutdown date ranges, exceptions, several shifts per day, a session list per vehicle and date carried across days and weekends.
6. **Weather fetch and use:** location → nearest DMI station with a full year per parameter, weather year(s), detail level (day / driving hours / hourly), temperature shift, worst day as its own case, P50/P90 across weather years, own weather file upload. Cold-tyre factor Kt (0.006 / 0.010 by load index; planned), wet/ice road factor (planned), door openings and cold-cab warm-up (parked).
7. **Depot and grid:** brownfield/greenfield, site address, grid company (Radius, Cerius, N1, TREFOR El-net, other), connection size (A or kW), customer category (C, B-lav, B-høj, A-lav, A-høj), building load (fixed / Eloverblik hourly via MitID / CT-logger upload), spare power, parking spaces and power per space, access type FNA / BNA / TFL (stepwise), BNA what-if cut (%, from–to time; a what-if, not a forecast), capacity charge (10 busiest hours), lead-time band, fleet growth phases (e.g. 10 trucks now, up to 70 within 48 months), buffer battery on site (planned).
8. **Flexibility:** offer to markets yes/no, products (FCR-D, FCR-N, mFRR, aFRR) with their minimum bids and response times (Energinet), aggregator yes/no, DSO flexibility pilot (Cerius/Radius terms), V2G readiness (ISO 15118-20 on truck and charger), hours per week available.
9. **Cost (TCO):** ownership period (8/10/12), financing (loan/lease/cash), interest, down payment, discount rate and NPV rule (Vejdirektoratet: year 1 discounted one period), residual value (table or SoH-linked), vehicle prices, service and insurance (EV vs diesel), tyres, driver wage, lost production time, downtime cost (e.g. tender fines DKK 2,000/truck/day), payload opportunity cost, charging dwell cost, chargers and trenching (COWI bands), connection fee (grid company formula), depot amortisation period (OPEN; ~30 years proposed), electricity cost split (spot by hour, grid tariff by time of day, electricity tax and refund), own hourly prices, price level, price paths (Energistyrelsen Klimastatus, planned), diesel, AdBlue, HVO100, biogas, public charging price, ETS2 on diesel from 2028, Danish km-toll by weight class and CO₂ class (extends to ≥ 3.5 t from 1 Jan 2027), subsidies (Vejdirektoratet pool, closed 30 Sep 2026; German BMV scheme; own amount), sensitivity ranges, Monte Carlo quartiles (planned).
10. **CO₂ and life cycle:** grid factor per year (Energistyrelsen series) or own value, CO₂ at actual charging hours (Energi Data Service CO2Emis, per price area), diesel CO₂ factor (NO SOURCE today), well-to-wheel, vehicle and battery production emissions, alternative fuels (HVO, biogas, B7).
11. **Tender and offer sheet:** buyer's award weights (price / technical / delivery / ESG), score curves (e.g. battery 250 → 450 kWh for 1 → 10 points; charging power 150 → 350 kW; load 5.8 → 9.5 t), minimum requirements (usable kWh at year 8, charging ≥ 150 kW between 10 % and 75 %, crane and compactor at the same time, ready at 80 % by 06:00), several OEM bids (spec values per bid), guarantee values (year-8 capacity, downtime ≤ 5 days/year, response within 2 h), brand-neutral flag.
12. **PTO extras:** fridge/TRU model (ATP K value or class, inner and outer box dimensions, set temperature, COP, heating mode), PTO shaft drag (`PTO-tech.csv`, parked), profile library with sources.
13. **Route sources:** VDRI (VECTO mission cycles), typed (distance, stops, dwell, road type, speeds 30/50/80 km/h, grade), GPS upload (only payload editable), AI "describe it" (planned; coordinates or text → waypoints via a map API), altitude, per-leg time windows (OPEN).
14. **Libraries:** vehicle library (EEA HDV CO₂ monitoring 2024–25, CC-BY 4.0, plus spec sheets; one row per exact configuration), charger and CPO library (`docs/research/data-library-chargers-2026-11/`), saved routes, payload profiles, PTO profiles, schedules.
15. **Scenarios and runs:** scenario levers (fleet size, charging strategy, price level, weather year, ownership years), base + changes, compare runs, run fingerprint (engine version, input hash, every default with its source).
16. **Two-sided inputs and views:** client / OEM / engineering view; slot metadata `{value, unit, source, date, label, provided_by, locked, version}` (OPEN, M6.7).
17. **AI assistant (planned):** fills inputs from messy data (spreadsheets, telematics dumps, descriptions). Where it sits in the input flow.

## Appendix B: results (now and planned; sources in the gap analysis and outputs note)

1. **Feasibility:** verdict per vehicle and fleet; checks (battery new, **battery at year 8**, full before leaving, grid connection, route fits shift, weight limit); first failing check.
2. **Energy:** kWh per day (average, hardest day, P50/P90 across weather years), kWh/km, kWh/t-km, per tonne collected; component energy balance (air, rolling, grade, inertia, mechanical brakes, gearbox, axle, motor, battery loss, each aux, HVAC, PTO, regen recovered); monthly balance table (km, °C, kWh driving, aux, HVAC, regen, at battery, charger losses, from grid, peak kW, cost); loss diagram (grid → charger → battery → motor → gearbox → wheel → air/roll/grade/brakes, plus aux branch); time stopped/accelerating/cruising/coasting/braking; speed and battery power over the day; sensitivity per extra tonne and per °C; winter vs summer; expected kWh/km by month and temperature in the shape fleets log it (FynBus); operating time (aktionstid), not only range; simulation quality check (average/min/max speed, max acceleration/deceleration, distance, share of time at full power).
3. **Battery:** installed vs usable (nominal vs usable), usable at year 8, **hardest day at year-8 capacity**, **winter at year 8**, margin left, SOC on return per vehicle across the year, minimum usable kWh at year 8 in winter for these routes (tender requirement), position on the tender's score curve, battery vs payload trade-off, payload left on each route, payload against diesel, predicted battery passport values after 8 years (energy throughput, equivalent full cycles, charging rates, time at hot/cold temperatures), when capacity would run out, ≥ 150 kW between 10 % and 75 % check.
4. **Charging:** chargers (size, count, ratio to trucks), per-session table (arrival SOC, kWh, start, end, power, finish, slack before departure), fleet schedule (Gantt), charger busy hours, strategies compared, robustness (one charger down, late return, cold week), spare trucks needed in a cold week, charging between shifts / at the tip site, charging losses.
5. **Grid:** depot peak (kW and A), load hour by hour, load duration curve, required connection (greenfield), customer category, connection fee from the price list, lead-time band, FNA vs BNA side by side, BNA what-if (does a 50 % cut 22:00–02:00 still leave every truck ready?), capacity charge with and without smart charging, peak growth with fleet phases, capacity-friendly vs system-friendly scores, amperes saved by load management.
6. **Flexibility:** up/down flexibility per hour within readiness, which products the fleet could qualify for (check against minimum bid and response time, not a revenue promise), aggregator needed, DSO pilot terms, hours per week available, V2G readiness, rebound after curtailment.
7. **Cost:** total and per km/month/year/period, electric vs diesel, break-even, year-by-year cash flow, cost by line, NPV (Vejdirektoratet rule), financing and residual, electricity split (spot/tariff/tax), sensitivity (electricity, diesel, km/year, residual, battery replacement, interest), service contract 8–10 years, downtime cost, depot cost split across trucks and its amortisation, alternatives (HVO, biogas), cost per t-km, grant-ready numbers.
8. **CO₂:** per year, saved over the period, grid factor path, CO₂ at charging hours, life cycle (production, well-to-wheel), comparison with HVO/biogas/B7.
9. **Tender / OEM view:** offer sheet (several bids on the same routes, scored with the buyer's weights), values each bidder would need to guarantee (year-8 capacity, downtime), crane and compactor energy and peak at the same time, kWh per lift or compaction cycle and per shift exported as a VECTO PTO profile.
10. **Audit and trust:** run fingerprint (engine version, date, input hash), every standard value and assumption with its source (PVsyst loss-list style), label on every number (measured / standard / assumption), model status per result (validated / in testing / not built), known decisions stated (10° yaw clamp, reference driver mass, fresh-air term, etc.), "hold back" rule (no firm winter verdict until cold-weather heating is validated: show winter as a labelled conservative case).
11. **Documents:** feasibility report, grid connection application (Radius screening fields: address, desired power, connection type, commissioning date, grid services yes/no), tender annex, financial model (spreadsheet), grant application data (Vejdirektoratet form: trucks charging daily, number and power of chargers, budget lines, lease NPV), client presentation (decision, cost, risks).
