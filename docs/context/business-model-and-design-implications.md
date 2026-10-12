# Business model — only the parts that shape the software design

Sources: past chats "Wind modelling engine code optimization" (Aug 2026), "Opus 5.5 capabilities" and "Tool and consultancy pricing strategy" (27 Sep 2026), "Completing the tool…" (May 2026), project memory. Prices, partners and negotiations are deliberately left out. Tags: **Stated** (Bob's position), **Idea** (discussed, not decided).

## Positioning (Stated)
- Vendor-neutral, VECTO-auditable, independent analysis for parties who cannot use an OEM's own tool: public tenders, multi-brand fleets, CPOs serving several manufacturers, infrastructure investors.
- The real incumbent in Denmark is Excel and OEM spreadsheets.
- Two separate things: (1) an impartial consultancy, paid only by the buyer; (2) the platform/tool, which may also earn supplier-side money (listings, leads). **Physics results are never for sale** — suppliers cannot pay to change or rank results.

## Who uses it, and for what
| User | Use | Status |
|---|---|---|
| Fleet operators, municipalities, housing associations | Size vehicles, batteries, chargers, grid connection; check flexibility and cost before buying | core |
| Buyers writing a tender | Turn their real operation into the technical requirements of the tender | Idea |
| OEMs, CPOs, charger makers, aggregators bidding in a tender | Show their product's technical fit on the buyer's own operational data | Idea ("tender technical-fit check") |
| Buyers evaluating bids | **Bid comparison room**: buyer's operational data stays fixed; each bidder's specs (price, battery, charger, costs) are run on the same data; paid per tender by the buyer, bidders join free to protect neutrality; possibly bidders fill in their own data via a link | Idea |
| Clients after a project | Live dashboard that keeps operational data current for the next tender instead of a new analysis | Idea |
| OEMs / CPOs / aggregators | Flat, labelled listing (no pay-to-rank); leads; aggregators: flexibility potential | Idea |
| Individuals (personal vehicles) | Free tier | Idea |

Other revenue ideas discussed (not decided): paid depot studies, advisor/installer annual licences (PVsyst-style), re-tender update fee, anonymised aggregate data for DSOs/aggregators (requires a data clause in every contract).

## Why this matters for the code (implications to respect now)
1. **Scenario = base project + small list of changes** (already decided) is exactly what bid comparison needs: one fixed operational base, one change-set per bidder. Keep this mechanism clean.
2. **Separate operational data from equipment data** in the project JSON (routes/calendar vs vehicles/chargers), so a bidder can swap equipment without touching the buyer's operation.
3. **Every result must be traceable** (inputs, defaults used, sources, assumptions list) — neutrality and tender use depend on it.
4. **Results cannot depend on who pays**: no supplier-specific logic inside engines; supplier data enters only as input data, labelled with its source.
5. **Multiple parties, one project** (buyer + bidders) and a live dashboard imply users/roles and persistent project storage later — out of scope now, but don't design the JSON in a way that blocks it.
6. **Outputs must be comparable side by side** (same metrics, same units, same assumptions list) across scenarios.

## From Bob's Business Model Canvas v2 (Sep 2026) — product-relevant items only
Two tracks: an impartial (brand-agnostic) consultancy, and the HDEV web tool owned by Bob (not brand-agnostic; may carry paid OEM placements, always labelled). Beachhead segment: municipalities and housing associations. Web-tool segments: CPOs, OEMs, aggregators, electrical installers and consultants (power users), individuals (free tier — parked, outside heavy-duty scope).

Features named on the canvas ("Idea" = Claude's suggestion on canvas page 2, not decided):
- Instant reports; self-service with AI support, with referral to the consultancy when a user needs help.
- **Live inputs**: prices, tariffs, taxes and rules update automatically (load is modelled; prices are live). Idea: a data refresh calendar (spot prices, DSO tariffs, SKM road-tax rates, each new Energistyrelsen edition).
- **Every number traceable**: each input shows its source and date (VECTO, Energi Data Service, SKM, Energistyrelsen). (Idea)
- **Grid-friendliness dossier**: coincidence factor and flexibility documented for a DSO / Energinet connection application. (Idea)
- **Capacity from DataHub data**, no logger where the site has its own metering point; "connect once" via Eloverblik/MitID so data stays live. (Idea for connect-once)
- **Tender technical-fit check**; **bid comparison room** (buyer's operation fixed, bidders enter specs through a link, compared like for like — suggested as flagship).
- **Re-tender ready / live dashboard**: data provided once; the next analysis is an update, not a restart. Change alerts when tariffs, taxes or prices shift. (Idea for alerts)
- Partners (OEMs, CPOs, aggregators) supply spec and price data through **one standard template**. (Idea: partner onboarding kit)
- **Neutrality firewall**: paid placements visibly labelled, never change a result or ranking. (Idea)
- Benchmark library of anonymised depot load profiles, with client consent, to fill data gaps. (Idea)
- Co-branded reports keep HDEV attribution ("Analysed with HDEV"), never white-label. (Idea)
- Tool tiers: Viewer (lite dashboard) · Pro (full tool) · Team (seats); pay-per-report credits. (Idea)
- Free depot check (quick grid-headroom estimate) as lead magnet. (Idea)
- Published methodology and validation cases against VECTO. (Idea)

Extra design implications from the canvas:
7. Every input value carries **source + date** metadata, not just a value — needed for live inputs, traceability and change alerts.
8. External data (prices, tariffs, tax rates, projections) lives in versioned, dated data files fetched separately from engines, so a refresh = new data version, and old reports stay reproducible.
9. A **standard spec template** for partner equipment (vehicle, battery, charger) = the same schema the user's vehicle/charger sections use.
10. Reports must be reproducible from (project JSON + data versions + code version).

Nothing here should be built now. It is context so the current design does not paint itself into a corner.
