---
inclusion: always
---

# Product — what HDEV is, who it is for, what it must not block

Source: `KIRO_PROMPT_1_STEERING.md`, #[[file:docs/context/product-and-scope.md]], #[[file:docs/context/business-model-and-design-implications.md]]. No prices are included here (the business doc deliberately omits them). Anything not in those files or the prompt is labelled **Inferred**.

## Name
- Working name: **HDEV**. The final product name is undecided — never use any other name.

## What it is
- A physics-based, **VECTO-auditable** simulation engine for battery-electric vehicle fleet and depot electrification sizing, starting in Denmark. Positioning phrase used in the docs: "PVsyst for EVs".
- **Vehicle-agnostic by design**: trucks first; vans, buses, cars later. Because of this, engines are pure maths with every parameter passed in as an argument so the tool works for any country (see `engine-rules.md`).
- Academic base: Bob's MSc thesis on EV depot charging flexibility in DK2. The multi-agent RL (MADDPG/MARL) part is **not** part of HDEV.

## Target users
- Fleet operators, municipalities, housing associations, CPOs, OEMs.
- Vendor-neutral, independent analysis for parties who cannot use an OEM's own tool (public tenders, multi-brand fleets, CPOs serving several manufacturers, infrastructure investors).
- The incumbent being displaced in Denmark is Excel and OEM spreadsheets.

## Outputs (now → later)
1. Energy consumption per row/day/year (driver model → force → consumption).
2. Battery sizing (mode A real vehicle; mode B iterative sizing).
3. Charger sizing and depot charging simulation (ASAP, JIT; EDF / ES allocation; **cheapest-first planned**), site peak.
4. Flexibility (up/down headroom).
5. Later: TCO, CO₂, scenario comparison, sensitivity, Monte Carlo ranges, optimiser.

Phased roadmap (from memory, 26 Sep 2026): battery sizing → charger simulation/sizing (+ Eloverblik coincidence factor) → flexibility → TCO/LCA → MitID load import → CO₂ → electrification optimiser.

## Current scope (12 Oct 2026)
- Finish the engine and a **step-by-step UI**, running **locally**, with the project JSON handled locally.
- Transport now: a small local Python server (UI posts project JSON, gets results JSON back).

## Out of scope now — but the design must not block these
- FastAPI backend (planned replacement for the local server, same JSON).
- Self-serve website.
- An **AI chatbot that fills input sections from messy dumped data**.
- Eloverblik / MitID data import.
- Subscriptions.

## Design implications to respect now
From #[[file:docs/context/business-model-and-design-implications.md]] (these shape the current design even though the features are later):

1. **Scenario = base project + a small list of changes.** This is exactly what bid comparison needs (one fixed operational base, one change-set per bidder). Keep the mechanism clean.
2. **Separate operational data from equipment data** in the project JSON (routes/calendar vs vehicles/chargers), so a bidder can swap equipment without touching the buyer's operation.
3. **Every result must be traceable** — inputs, defaults used, sources, assumptions list. Neutrality and tender use depend on it.
4. **Results cannot depend on who pays.** No supplier-specific logic inside engines; supplier data enters only as input data, labelled with its source. Physics results are never for sale.
5. **Multiple parties, one project** and a live dashboard imply users/roles and persistent project storage later — out of scope now, but do not design the JSON in a way that blocks it.
6. **Outputs must be comparable side by side** — same metrics, same units, same assumptions list across scenarios.
7. Every input value carries **source + date** metadata, not just a value (needed for live inputs, traceability and change alerts).
8. **External data** (prices, tariffs, tax rates, projections) lives in versioned, dated data files fetched separately from engines, so a refresh = new data version and old reports stay reproducible.
9. A **standard spec template** for partner equipment (vehicle, battery, charger) = the same schema the user's vehicle/charger sections use.
10. Reports must be reproducible from (project JSON + data versions + code version).

## Regulatory hook (context only)
Energinet has paused new grid connection agreements and uses grid-friendliness as a prioritisation criterion; from 1 Jan 2026 residents in ejer-/andelsboligforeninger have a right to install charge points. So coincidence-factor and flexibility outputs matter commercially. Source documents are in the project knowledge base, not this bundle.
