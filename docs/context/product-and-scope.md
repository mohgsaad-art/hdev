# HDEV — product context and scope (for steering)

Source: Bob's project memory (overview, ways-of-working, engine notes), summarised by Claude 12 Oct 2026. Commercial/partner details deliberately excluded.

## What HDEV is
- Working name: **HDEV**. Final product name undecided — do not use any other name.
- A physics-based, **VECTO-auditable** simulation engine for battery-electric vehicle fleet and depot electrification sizing, starting in Denmark. Positioning: "PVsyst for EVs".
- **Vehicle-agnostic by design** (trucks first; vans, buses, cars later). Engines are pure maths: every parameter is an argument so the tool works for any country.
- Target users: fleet operators, municipalities, housing associations, CPOs, OEMs. Vendor-neutral, independent analysis.
- Academic base: Bob's MSc thesis on EV depot charging flexibility in DK2 (energy-neutral up/down flexibility for JIT and ASAP charging). The multi-agent RL (MADDPG) part is NOT part of HDEV.

## Outputs (now → later)
1. Energy consumption per row/day/year (driver model → force → consumption).
2. Battery sizing (mode A real vehicle; mode B iterative sizing).
3. Charger sizing and depot charging simulation (ASAP, JIT; EDF / ES allocation; cheapest-first planned), site peak.
4. Flexibility (up/down headroom).
5. Later: TCO, CO₂, scenario comparison, sensitivity, Monte Carlo ranges, optimiser.

## Phased roadmap (from memory, 26 Sep 2026)
battery sizing → charger simulation/sizing (+ Eloverblik coincidence factor) → flexibility → TCO/LCA → MitID load import → CO₂ → electrification optimiser.

## Current scope (12 Oct 2026)
- Finish the engine and a **step-by-step UI**, running **locally**, with the project JSON handled locally.
- Transport now: a small local Python server (UI posts project JSON, gets results JSON). **Planned: FastAPI** replaces that layer later with the same JSON.
- Out of scope now, but the design must not block them: FastAPI backend, self-serve website, an **AI chatbot that fills input sections from messy dumped data**, Eloverblik/MitID import, subscriptions.

## Regulatory hook (why grid-friendliness matters) — context only
Energinet has paused new grid connection agreements and uses grid-friendliness as a prioritisation criterion; from 1 Jan 2026 residents in ejer-/andelsboligforeninger have a right to install charge points. So coincidence-factor and flexibility outputs matter commercially. (Source documents are in the project knowledge base, not this bundle.)

## Client-facing dashboard (prototype)
Static page, hand-drawn SVG/canvas, no external dependencies, Bob's own design system (paper/ink restraint, hairline rules, tabular numerals, terracotta for assumed values). All figures currently illustrative placeholders. Open: how this relates to the step-by-step input UI once a local server exists.
