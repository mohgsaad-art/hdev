# Current state of the EV Scope demo tool and landing page (14 Nov 2026)

Written by Claude. This describes what exists today in `website-wip/` on branch `claude/ev-scope-site-wip`, so Kiro can audit it. Bob has not accepted this version; section 4 lists the problems he raised.

## 1. Files

| Path | What it is |
|---|---|
| `website-wip/out/ev-scope-site.html` | The deliverable: landing page with the demo tool embedded (one self-contained file, ~3.1 MB, images and fonts as base64). Open it in a browser. |
| `website-wip/out/ev-scope-tool.html` | The demo tool alone (~240 KB). |
| `website-wip/src/model.js` | Field registry `DEFS` (every input: key, label, unit, type, source tag, reference, popup name `pop`, page `pg`, visibility rule `when`), sample project, and the stand-in demo model `compute()`. |
| `website-wip/src/ui.js` | Navigation, setup pages, field rendering, popups (`openDlg`, `openTpl`, `openPop`, `openStops`). |
| `website-wip/src/results.js` | Result pages, charts, compare page, the six document print layouts. |
| `website-wip/src/app.js` | Event handlers, fixed-question demo assistant, start-up. |
| `website-wip/src/tool.css`, `tool.html` | Tool styles and shell. |
| `website-wip/build_tool.py`, `build_site.py`, `site_parts.py`, `site_v2.py` | Build scripts. The site is built from `assets/site_stripped.html` (the original landing page with images replaced by placeholders) plus the edits in `build_site.py` and `site_v2.py`. |
| `website-wip/test_tool.py`, `test_site.py`, `peek.py` | Playwright tests and the capture script for the three preview screenshots. |
| `website-wip/assets/original-site.html` | The landing page as Bob uploaded it on 13 Nov, before this work. Compare against it. |

Run locally: `python3 build_tool.py && python3 peek.py && python3 build_site.py` (needs Chrome + Playwright for `peek.py`).

## 2. The demo tool today

**Important:** the tool runs a stand-in demo model in JavaScript, not the HDEV engine. Its constants are listed on the "Inputs and sources" page. It only exists to show the UI. The real engine is Python (see `project-notes/claude_status-engine.md`). The final product keeps all logic in Python and the UI as a dumb form.

**Top menu:** Setup · Results · Compare · Documents. A Run button and a run-state line in the header.

**Setup pages (left to right):**
1. Project: names, run mode (sizing; step-by-step simulation shown disabled), brand-neutral flag.
2. Fleet: the fleet table (row select, group name, count, a dropdown each for Vehicle, Route, Payload, PTO, Schedule with a one-line summary and "Edit"; "Stops" per row opens the stop table popup; Copy; Remove), bulk apply bar, "What will be driven" table (rows grouped into driver runs).
   - "Edit" opens the template in one popup. Detailed groups of a template open inside the same popup with a "Back" link. Vehicle groups: Trailer and wheels, Air drag and size, Tyres, Drivetrain, Braking energy, Battery details, Battery voltage and resistance, On-board systems.
3. Depot and grid: site, grid connection (existing/new, size, grid company, access), building load; popups Parking, Limited access what-if.
4. Charging: chargers (auto/choose), charging plan, ready-by; popups Charger load and losses, Flexibility.
5. Weather: depot location, weather station, year to size for, detail level, temperature shift, worst-day case; popup Wind; cab heating and cooling (fixed power or thermal model) with popups Set-points, Cab data, Climate constants; a month-by-month table.
6. Prices: price area, electricity price, level, tariff, own hourly prices; diesel; popup Other fuels and public charging.
7. Costs: per-vehicle electric/diesel price, service, insurance (two-column grid); financing; drivers; depot (popups Charger price list, Connection fees); depot write-off years.
8. Taxes and CO₂: road tax grid by period, CO₂ class, subsidy, grid CO₂ (projection or own), CO₂ at charging hours, diesel CO₂.
9. Check and run: missing values (each links to its page or popup), counts by source type, full list of every value and its source.

**Field marking:** sample or assumed value = small grey asterisk with a tooltip; edited = blue text with "Reset"; missing = red ring and Run blocked. A legend line at the bottom of each page.

**Results pages:** Overview, Energy, Battery, Charging, Grid, Cost, CO₂, Inputs and sources. Each starts with the page name, one status line with a pass/fail mark, then a band of four large figures, then sections.
- Overview: four figures, six checks (battery new, battery at year 8, full before leaving, grid connection, route fits shift, weight limit), fleet table of results.
- Energy: average/hardest day, per km, per year; where the energy goes; month chart; time on route.
- Battery: installed, usable new, usable at year 8, margin; hardest day against the battery bars; weight table.
- Charging: chargers, longest charge, time to spare; Gantt of the hardest day; per group; the three charging plans compared.
- Grid: depot peak and amperes, connection, room or overload, connection cost; load chart; behind the figures.
- Cost: totals, saving, break-even year; cumulative saving chart; by cost line; year by year.
- CO₂: per year, saved; year by year.
- Compare: two runs side by side (inputs that changed, results); quick what-if buttons.
- Documents: six document types, each opens a print layout (feasibility report, grid connection application, tender annex, financial model, grant application data, client presentation) plus a CSV export.

## 3. The landing page today (top to bottom)

1. Header: logo, nav (Who it's for, How it works, The tool, Documents, About, Contact), Ask, language (EN/DA/DE/NL), day/night switch, "Try the demo".
2. Hero: "Scope before you sign", one line ("Battery, charger and grid sizing for electric fleets, worked out from your own routes."), "Get early access" + "Try the demo", the depot image with day/night versions.
3. Who it is for: tabs for Fleet owners, Housing associations, Municipalities, Truck makers and charge operators. Each panel: audience title, one sentence on what it works out, three questions, an example box (fleet owner and municipality examples use demo sample figures, labelled), a vehicle image. Each tab has its own address (`#fleet-owners`, `#housing`, `#municipalities`, `#suppliers`).
4. How it works: the pinned scroll story with six chapters (On the road / Overnight with the day-night switch, Battery, Winter at year 8, Charging, Payload, Grid); images change as you scroll (payload fill, chargers changing).
5. See it on a sample depot: three demo screenshots (fleet, overview, cost) with a slow cursor.
6. Six documents from one run: the document fan; pick by tab, arrows or clicking a sheet.
7. Closing call to action, footer with business details (placeholders), Privacy and Terms pages.
- No Google Fonts or other third-party requests; IBM Plex Sans embedded (SIL OFL 1.1).

## 4. Problems Bob raised on this version (14 Nov), not yet solved

- Landing copy still reads as selling, not as plain help.
- Documents section "broken and not smooth".
- Hero paragraph, then audiences listed, then listed again (fixed in part: the hero audience buttons were removed after his message; Kiro should still judge the flow).
- "Documents you can take away" blocks (removed after his message).
- Tool: a separate Templates page was added and then removed after his message; cab heating moved from the vehicle to Weather after his message.
- Whether the current page split, popup split and results layout are right is exactly what Kiro is asked to research.
