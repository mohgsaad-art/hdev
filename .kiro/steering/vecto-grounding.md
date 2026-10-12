---
inclusion: always
---

# VECTO grounding — scope, source order, and allowed deviations

Source: `KIRO_PROMPT_1_STEERING.md`, the dated close-outs, #[[file:reference/vecto/ADD_THESE_FILES.md]], #[[file:reference/regulation/ADD_THESE_FILES.md]]. This file governs any physics value or formula.

## Scope
- **VECTO Declaration Mode**, **heavy and medium lorries**, **battery-electric (BEV/PEV)**.
- Buses, conventional/diesel, hybrid and FCHV paths are reference only, used to explain the BEV path (as in #[[file:docs/decisions/2026-10-08_session-closeout-paux.md]]).

## Source order (highest wins)
1. **VECTO C# source and resource files** (code.europa.eu/vecto/vecto, stable branch).
2. **Regulation (EU) 2017/2400** (consolidated 01.01.2026).
3. **VECTO documentation.** The 2014 LOT3 report is diesel-era; **where it differs from the repo files, the repo wins** (e.g. the P_aux close-out found the repo CSVs supersede the 2014 doc tables).
4. **Peer-reviewed literature.**
5. **HDEV assumption** (lowest; always labelled).

## Hard rules
- **Always cite the file name** for any value or formula.
- **Never invent a physics value or formula.** No made-up numbers anywhere.
- **If a needed VECTO file is not in `reference/`, say which file is needed and stop — do not guess.**

## Reference files are currently MISSING
`reference/vecto/` and `reference/regulation/` contain only `ADD_THESE_FILES.md`. The actual VECTO C# source, VECTO resource CSVs/VDRIs and the Regulation 2017/2400 extracts are **not present in this bundle**. Until they are added, any step that needs one of them must **name the specific file and mark it "missing"**, not proceed on a guess. The lists of required files are in #[[file:reference/vecto/ADD_THESE_FILES.md]] and #[[file:reference/regulation/ADD_THESE_FILES.md]]. Values already extracted and quoted in `docs/` may be used **with their doc citation**, but the underlying source file is still marked missing.

Named files repeatedly needed but not yet present (examples): `AirDrag.cs`, `VCDV_parameters.csv`, `CrosswindCorrectionCdxALookup.cs`, `Vehicle.cs`, `Wheels.cs`, `SegmentTable.csv`, `Payloads.csv`, `Body_Trailers_Weights.csv`, `Truck.vacc`, the `VAUX/` CSVs, `DrivingCycleData.cs` (grade vs altitude), `IMC-Tech.csv` (`DeltaAirDragAreaIMC`), `12b-annex-xb-electric-machine-iepc-ihpc-testing.md` (electric-machine efficiency map).

## Deviations from VECTO — rules
- Allowed **only** as **optional arguments**, **clearly labelled non-VECTO**, and **listed in the assumptions report**.
- **Do not add any deviation that is not already in `docs/`.**

## Already-decided deviations (collected from docs — do not add to this table)
| Deviation | What it does | Why | Source file |
|---|---|---|---|
| **Yaw clamp at 10°** (`beta_limit_deg`) | Holds ΔCdxA at its 10° value above 10° yaw; `None` = VECTO behaviour (no clamp) | VECTO's a1–a3 yaw polynomial is only valid 0–10° (SR7); for tractor-semitrailer it peaks ~13° and goes negative >19.9° (fit artefact). Danish wind pushes yaw past 10° at low speed. Must appear in every client report. | #[[file:docs/decisions/2026-10-06_crosswind-verification.md]], #[[file:docs/decisions/2026-10-07_session-closeout-crosswind-payload.md]] §2; code #[[file:src/engine/crosswind_engine.py]] |
| **In-cycle payload variation** | Lets payload change at stops within one cycle (shapes constant/linear/custom) instead of one constant payload per cycle | Real deliveries change load during the day. VECTO declaration uses a single constant reference payload per cycle. Reports must state this is an HDEV addition beyond VECTO. | #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §2, #[[file:docs/design/payload-stop-rows-then-fill.md]]; code #[[file:src/engine/payload_engine.py]] |

## Known VECTO gaps to flag in reports (not deviations — missing from VECTO itself)
From #[[file:docs/decisions/2026-10-08_session-closeout-paux.md]] §7 and #[[file:docs/design/status-and-known-contradictions.md]] §5. Flag these; do not invent values to fill them:
- **No cabin heating** in the VECTO truck path; HVAC is one constant per group × mission with no ambient-temperature input. Danish winter is not represented by VECTO declaration values.
- **No temperature or solar dependence** for trucks (exists only in the bus SSM model).
- **No DC/DC loss** (efficiency fixed at 1.0 in Declaration Mode).
- **No aux during depot charging** (open for the charging engine).
- Motor/inverter/gearbox efficiencies are **placeholders** (0.95 / 0.95 / 0.98); VECTO has a map-based electric-machine path (Annex Xb) not yet grounded.
- Any non-VECTO extra Bob later adds (DC/DC loss, cabin heating, charging-time aux) must be an optional, flagged layer with a neutral default — and must cite an authentic non-VECTO source for its numbers.
