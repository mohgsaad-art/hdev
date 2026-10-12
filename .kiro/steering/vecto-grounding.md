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

## VECTO reference files — now present
The VECTO C# source and resource files listed in #[[file:reference/vecto/ADD_THESE_FILES.md]] have been copied in from the VECTO repo (branch `stable`, commit `d16ba783c`, v5.1.3):
- `reference/vecto/cs/` — C# source (e.g. `AirDrag.cs`, `Vehicle.cs`, `Wheels.cs`, `Battery.cs`, `Driver.cs`, `DistanceBasedDrivingCycle.cs`, `MeasuredSpeedDrivingCycle.cs`, `CrosswindCorrectionCdxALookup.cs`, `VectoRunData.cs`, `DeclarationData.cs`, `Constants.cs`, `DrivingCycleData.cs`, the aux adapters, …).
- `reference/vecto/cs/declaration/` — declaration lookups (`HVAC.cs`, `PneumaticSystem.cs`, `SteeringPump.cs`, `ElectricSystem.cs`, `Conditioning.cs`, `AbstractAuxiliaryVehicleArchitectureLookup.cs`). The two names shared with `cs/` (`ElectricSystem.cs`, `Conditioning.cs`) are the **declaration-lookup** versions and live only here.
- `reference/vecto/resources/` — `SegmentTable.csv`, `Payloads.csv`, `Body_Trailers_Weights.csv`, `Wheels.csv`, `VCDV_parameters.csv`, `IMC-Tech.csv`, `Cdv_Generator_VECTO3.2.xlsx`, plus `MissionCycles/` (the five truck `.vdri` + the three `MunicipalUtility_PTO_generic` PTO files), `VACC/Truck.vacc`, and `VAUX/` (`HVAC-Table.csv`, `ES-Tech.csv`, `ES-Tech_Medium.csv`, `PS-Table.csv`, `SP-Table.csv`, `SP-Tech.csv`, `SP-Axles.csv`, `Cond-Table.csv`, `PTO-tech.csv`).

Every file on the list was found; **none is missing**. These are READ-ONLY — never edit anything under `reference/`. Still cite the file name for any value taken from them.

**Regulation extracts still MISSING.** `reference/regulation/` still contains only `ADD_THESE_FILES.md`; the Regulation (EU) 2017/2400 markdown extracts are **not present**. Any step needing one (e.g. `12b-annex-xb-electric-machine-iepc-ihpc-testing.md` for the electric-machine efficiency map, or the Annex VIII air-drag standard-value appendices) must **name the specific file and mark it "missing"**, not guess. [REG] values already quoted in `docs/` may be used with their doc citation, but the underlying regulation file is still marked missing.

## Deviations from VECTO — rules
- Allowed **only** as **optional arguments**, **clearly labelled non-VECTO**, and **listed in the assumptions report**.
- **Do not add any deviation that is not already in `docs/`.**

## Already-decided deviations (collected from docs — do not add to this table)
Each is stated as a decision in `docs/`. Add nothing here that the docs do not state as a deviation.

| Deviation | What it does | Why | Source file |
|---|---|---|---|
| **Yaw clamp at 10°** (`beta_limit_deg`) | Holds ΔCdxA at its 10° value above 10° yaw; `None` = VECTO behaviour (no clamp) | VECTO's a1–a3 yaw polynomial is only valid 0–10° (SR7); for tractor-semitrailer it peaks ~13° and goes negative >19.9° (fit artefact). Danish wind pushes yaw past 10° at low speed. Must appear in every client report. | #[[file:docs/decisions/2026-10-06_crosswind-verification.md]], #[[file:docs/decisions/2026-10-07_session-closeout-crosswind-payload.md]] §2; code #[[file:src/engine/crosswind_engine.py]] |
| **In-cycle payload variation** | Lets payload change at stops within one cycle (shapes constant/linear/custom) instead of one constant payload per cycle | Real deliveries change load during the day. VECTO declaration uses a single constant reference payload per cycle. Reports must state this is an HDEV addition beyond VECTO. | #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §2, #[[file:docs/design/payload-stop-rows-then-fill.md]]; code #[[file:src/engine/payload_engine.py]] |
| **Real DMI wind instead of VECTO declaration wind** (`v_ref`, `h_ref` as arguments) | Uses measured Danish wind (DMI, e.g. 5.028 m/s at 10 m) in the crosswind step instead of VECTO's declaration wind (3 m/s at 4 m). Passing the VECTO values reproduces the auditable case exactly. | Real local wind is the point of HDEV; VECTO's single declaration wind is only for type-approval. The VECTO-equivalent case (3 m/s at 4 m, constant reference payload) must stay exactly reproducible. | #[[file:docs/decisions/2026-10-07_session-closeout-crosswind-payload.md]] §2, #[[file:docs/design/year-and-day-simulation-problem.md]] §6 |
| **Editing a VDRI → relabelled "user route"** | Allows editing stop durations and payload on a VDRI cycle; the edited cycle is labelled a user route and the original VECTO file is never changed | Relaxes the earlier "VDRI never altered, constant payload only" rule (7 Oct) so real operations can be represented, while keeping the VECTO template file untouched and the result clearly non-standard. | #[[file:docs/decisions/2026-10-08_session-closeout-payload-force.md]] §2, #[[file:docs/context/input-layer-and-json.md]] |

### Candidates deliberately NOT added (and why)
To keep this table to true, decided VECTO deviations:
- **Placeholder motor/inverter/gearbox efficiencies (0.95 / 0.95 / 0.98)** — the docs label these a *model gap / placeholder*, not a decided deviation. Listed under "Known VECTO gaps" below. Source: #[[file:docs/design/status-and-known-contradictions.md]] §5.
- **Typed-input resolver assumptions — even stop spacing, 45 min dwell, default speeds 30/50/80 km/h** — the docs label these **Assumptions** (Bob's judgement, unsourced), to live in `defaults.py` with an HDEV ASSUMPTION label, not VECTO deviations. Source: #[[file:docs/context/input-layer-and-json.md]], #[[file:docs/decisions/2026-10-07_session-closeout-crosswind-payload.md]] §4.

## Known VECTO gaps to flag in reports (not deviations — missing from VECTO itself)
From #[[file:docs/decisions/2026-10-08_session-closeout-paux.md]] §7 and #[[file:docs/design/status-and-known-contradictions.md]] §5. Flag these; do not invent values to fill them:
- **No cabin heating** in the VECTO truck path; HVAC is one constant per group × mission with no ambient-temperature input. Danish winter is not represented by VECTO declaration values.
- **No temperature or solar dependence** for trucks (exists only in the bus SSM model).
- **No DC/DC loss** (efficiency fixed at 1.0 in Declaration Mode).
- **No aux during depot charging** (open for the charging engine).
- Motor/inverter/gearbox efficiencies are **placeholders** (0.95 / 0.95 / 0.98); VECTO has a map-based electric-machine path (Annex Xb) not yet grounded.
- Any non-VECTO extra Bob later adds (DC/DC loss, cabin heating, charging-time aux) must be an optional, flagged layer with a neutral default — and must cite an authentic non-VECTO source for its numbers.
