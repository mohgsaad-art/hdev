# Kiro prompt: HVAC deep dive: `HVAC_thermal`, `ssm_total_w`, `climate_lookup` (12 Nov 2026)

Owner: Bob. Repo: `mohgsaad-art/hdev`. **Today's date is 12 November 2026.** When you research, look for documents up to this date (VECTO releases, regulation amendments, standards, papers and reports from 2023–2026), not only older ones.

**Run the whole job in one uninterrupted pass.** Do not stop to ask Bob anything. If something is unclear, choose the option that changes the least, write it under "Choices I made", and carry on. Open **one PR** at the end.

**Branch:** create `hvac-review-2026-11` from `main`. Copy this prompt to `docs/research/inputs/kiro-prompt-hvac-review-2026-11-12.md` as the first commit. Put everything new in `docs/research/hvac-review-2026-11/`, `tests/hvac/` and `docs/explainers/hvac-explained.md`. Open the PR from this branch to `main`.

---

## 0. Rules for this job (read first)

1. **Do not edit Bob's engine code.** Bob writes all engine code himself. Do not change the notebook or anything under `src/`. You may copy functions into `docs/research/hvac-review-2026-11/reference_copy.py` and make experimental variants there, clearly named (e.g. `HVAC_thermal_v_transient`, `ssm_total_w_v_speed_ua`). Every proposed change goes into the report as a **before / after snippet with its measured effect**.
2. **No invented numbers.** Every value you use or propose must come from a named source: VECTO source/resource file + line, Regulation (EU) 2017/2400 (incl. amendments up to 2025), an ISO/EN/SAE/UN/ASHRAE/NREL/JRC/EPA document, or a peer-reviewed paper or official report, with a link. If there is no source, write `NO SOURCE` and leave it as an open item. Illustrative test values are allowed only inside tests and must be labelled `ILLUSTRATIVE` in the test and the report.
3. **No silent fallbacks.** If an input is missing, do not fill it with a guess or a default. Mark the part `BLOCKED: <what is missing>` and keep going with the rest.
4. **Tag every statement in the report:**
   - `[VECTO]` read in VECTO source: give file, line numbers, branch and commit hash;
   - `[REG]` from Regulation (EU) 2017/2400 or its amendments: give annex/point;
   - `[STD]` from a standard (ISO, EN, SAE, UN, ASHRAE): give number, year, clause, and whether you read the text or only a summary;
   - `[SOURCE]` other external document: link, date, and whether you read the **full text** or only an **abstract/snippet**;
   - `[CALC]` your own arithmetic from sourced inputs (show the inputs);
   - `[TEST]` result of a test you ran (name the test file and function);
   - `[ASSUMPTION]` an HDEV choice with no source;
   - `[SIMPLIFICATION]` a deliberate simplification;
   - `[OPEN]` not resolved.
   Never pass an assumption or inference off as fact. If you are not sure you read something correctly, say so. A number seen only in a search snippet must be tagged `[SOURCE, snippet]` and must not be used as a model input.
5. **VECTO version.** Bob's `.vmod` files were written by **VECTO 5.1.6-RC**. Read VECTO source in `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`. Clone with `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/VECTO`. Re-check every VECTO line number in this prompt; they are leads, not facts.
6. **VECTO cannot run in your sandbox.** Anything needing a new VECTO run is Bob's job. Write the exact job/GUI steps for him instead (Part J).
7. **Engine purity rule (Bob's architecture).** Engine functions are pure maths: every parameter is an argument, nothing hard-coded, no I/O, **no unit conversion inside, everything in SI units**. All calculations belong in the engine. The parser (`defaults.py`, not written yet) only looks up, converts units, checks inputs and fills gaps. **All input checks live in the parser** (decided 12 Nov), not in engine functions. Judge every proposed change against this rule and say for each one: **engine** or **parser**.
8. **Hourly structure stays.** `HVAC_thermal` is evaluated per **weather hour** (array over hours), and the consumption engine maps the hourly HVAC W onto the 1 s driver rows. It must stay mass-free and row-free so that a year of weather × many trucks stays cheap. Any proposal that needs per-row or per-second evaluation (e.g. a transient cabin model) must say so loudly, show the runtime cost (Part K), and offer a version that keeps the hourly structure if one exists.
9. **Bob's validation rule.** Matching VECTO exactly is **not** validation. VECTO is the audit reference. Validation means comparison with several independent sources (other models, standards, measured data), showing how far HDEV and each source differ. A change that only swaps one assumption for another, with no standard or validation behind it, is not worth making. Say so when that is the case.
10. **Bob's modelling stance.** HDEV must not underestimate energy. Where the physics is uncertain, show which choice is the conservative one.
11. **Inputs users can actually give.** Bob does not want features that need inputs fleet users can't realistically provide (e.g. cab U-value, window g-value, heat-pump COP curve). For every input, say: can a fleet user give it? If not, what is the best **sourced** default, and can it be derived from data already asked for (cab type, vehicle class, weather, OEM spec sheet)?
12. Plain English in the report. Short sentences. Define every technical term the first time you use it. Refer to the owner only as "Bob".
13. **Never decide an open design choice for Bob.** Show evidence; if you recommend, label it "Kiro's recommendation".

### 0.1 Pitfalls from earlier Kiro PRs (do not repeat them)

- **PR #20 (HVAC parameters, 1 Nov):** most PDFs could not be opened, and many values were left as `NOT FOUND (behind PDF)`. This time: try every route to the **full text** (publisher HTML, DOE OSTI, `docs.nrel.gov` / `docs.nlr.gov`, institutional repositories such as `research.chalmers.se`, `publications.jrc.ec.europa.eu`, ResearchGate pages, author pages, arXiv/preprints). If you still cannot open it, put it in the **"Bob to fetch"** table with link/DOI and **exactly which table/figure/value** Bob should extract.
- Using snippet numbers as model inputs. Do not.
- Filling missing values silently (e.g. `max_heating_power` missing → 0 instead of flagged).
- A "gate" test that compares hard-coded numbers instead of running the actual code.
- Results that change between runs. Every script must be deterministic; run each main script twice and confirm identical CSVs.
- Claiming "done" without evidence. Every claim in the summary points to a CSV, test or file line.
- Mixing bus and lorry data without saying so. VECTO's SSM is a **bus** model; VECTO lorries use a constant HVAC table (`VAUX/HVAC-Table.csv`). Every bus value applied to a truck cab must be flagged as such.

### 0.2 Scope

**In scope:**
- `HVAC_thermal` (notebook cell 11), `ssm_total_w` (cell 12), `climate_lookup` (cell 13). See Appendix 1.
- How the output enters the rest of the engine: `HVAC_el` → `P_aux(HVAC_power=..., HVAC_eff=1.0)` (cell 9) → hourly HVAC laid onto rows in `consumption_engine` (cell 16). **Read-only consistency check**: shape contract (scalar vs per-hour array), hour indexing, units. Report bugs; do not review the rest of `consumption_engine`.

**Out of scope (later jobs):** battery and motor conditioning (`cond_power`, Cond), battery thermal model, fridge/TRU, `consumption_engine` steps 5–7, the driver model. If you notice something there in passing, list it under "Seen in passing (out of scope)" with file and line only. **Exception:** Part F item 9 asks for a short research note on battery conditioning, because it shares weather inputs with HVAC. Report only; no variants.

### 0.3 Decisions already made by Bob (do not reopen; you may report evidence against them)

From the 2 Nov review (`claude/status-engine.md` in Bob's project; context only):
1. **Fresh-air term** `q_freshair = rho·cp·Q/3600·(T_amb − T_calc)` added in `ssm_total_w`. `Q = 0` gives exactly VECTO. Parser default proposed 100 m³/h for 2 occupants (pending a check of Dvorak 2025, WEVJ 16:129). Humidity ignored.
2. **Cab area and U unchanged** (`A_surface`, `U` are arguments). Current placeholders 20 m² × 3.0 W/m²K = 60 W/K; NREL CoolCab measured parked UA of a US sleeper cab 51 and 65 W/K (re-check this).
3. **Missing heat-pump COP** (non-R-744 at −20 °C): the parser fills it with the nearest value (−5 °C), a flat clip. Flagged as optimistic below −5 °C. The engine raises if a COP is still NaN.
4. **Setpoints** stay as arguments with VECTO defaults 18 / 23 / 17 °C.
5. **Weather gaps** are filled in the parser (a NaN hour would silently give 0 W).
6. **Optional checks go to the parser**: unmet heat/cooling outputs, `eh_eff > 0`, ascending points.
7. **Hourly evaluation** with real weather (DMI) instead of VECTO's fixed environmental-condition points.
8. **No aux power while depot charging** (decided 13 Oct).

Report flags already noted (re-check each, do not just repeat): bus SSM used for a truck cab; hourly instead of VECTO's condition points; COP interpolation, nearest-point heating split, COP clip; fresh air on (non-VECTO); the 0.25 solar factor unexplained; whether VECTO `solar` equals DMI global radiation unverified; measured UA is parked (lower bound while driving); door openings and cold-cab warm-up not modelled.

### 0.4 Inputs (in the repo or the VECTO fork)

| What | Path | Used in |
|---|---|---|
| Bob's notebook = **code of record** (12 Nov) | `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb` | everything |
| Earlier HVAC research (PR #20) | `docs/research/hvac-thermal-parameters-2026-11.md` | context; re-check every number |
| VECTO aux notes | `docs/research/vecto/06-auxiliaries-all.md`, `14-pto-aux-followups.md`, `12-cross-check.md` | context |
| Aux/PTO review (PR #31) | `docs/research/aux-pto-review-2026-11.md` | context (P_aux, HVAC factor 1/0.8) |
| E2 `.vmod` runs + `.vsum` | `docs/research/vecto/` | Part E (VECTO lorry HVAC value per mission) |
| Test harness v1.7 | `docs/research/vecto/hdev_test_harness_v1.7.py` | E2 set-up |
| VECTO SSM source | `VectoCore/VectoCore/Models/BusAuxiliaries/DownstreamModules/Impl/HVAC/`: `SSMRun.cs`, `SSMCalculate.cs`, `SSMInputs.cs`, `SSMTOOL.cs`, `TechnologyBenefits.cs`, `EnvironmentalConditionsMap.cs`, `HeatingDistributionMap.cs`, `HeatingDistributionCasesMap.cs`, `M01Impl.cs` | A, C |
| VECTO bus declaration data | `VectoCore/VectoCore/Models/Declaration/DeclarationData.cs` (bus section, ~lines 340–600: `DefaultEnvironmentalConditions`, `HeatingDistribution*`, `VentilationRate` ~451, `CalculateCOP` ~566) | A, C |
| VECTO bus resources | `VectoCore/VectoCore/Resources/Declaration/Buses/`: `DefaultClimatic.aenv`, `SSMDefaults.AHSM`, `SSMTechList.csv`, `HeatingDistribution.csv`, `HeatingDistributionCases.csv`, `HVACHeatingPower*.csv`, `HVACCoolingPower*.csv` | A, C |
| VECTO lorry HVAC table | `VectoCore/VectoCore/Resources/Declaration/VAUX/HVAC-Table.csv` | E |
| VECTO unit tests for SSM / bus aux (look for expected values) | search `VectoCore/VectoCoreTest/` for `SSM`, `BusAux`, `HVAC` | Gate 3, C |
| Open-source tools (Bob's forks) | `mohgsaad-art/fastsim`, `mohgsaad-art/eflips-depot`, `mohgsaad-art/spice_ev`, `mohgsaad-art/dt-cargo`, `mohgsaad-art/blast-lite`, `mohgsaad-art/acnportal` | H |

**How to load the notebook functions (do this exactly):** write `docs/research/hvac-review-2026-11/_load_notebook.py`. It reads the `.ipynb` JSON, takes the **code cells only**, skips cell 0 (it imports `torch`, `gymnasium`, `requests` etc., which must NOT be installed), and `exec`s the rest in one namespace that starts with `import math, bisect; import numpy as np`. Do not change any cell text. Print the list of function names loaded. All tests and scripts import from this loader, so they always test Bob's exact code.

**Weather data.** Danish hourly weather: try the DMI Open Data API (`opendataapi.dmi.dk`, `metObs` collection: hourly mean temperature `temp_mean_past1h` and global radiation `radia_glob_past1h`) for Copenhagen (Landbohøjskolen 06186 or Kastrup 06180) for one full recent year (2024 or 2025). Save the CSV in the repo with the exact query URL and download date. If you cannot reach it: `BLOCKED: DMI data`, write the exact query for Bob, and use a clearly labelled `ILLUSTRATIVE` synthetic year only for runtime tests (never for energy results).

---

## 1. What these functions do

HDEV is a Python engine that sizes battery-electric trucks and depots, built to be auditable against VECTO (the EU certification simulator, Regulation (EU) 2017/2400).

VECTO gives a **lorry** one constant HVAC power per mission (150–250 W electric after the 1/0.8 factor). For **buses** VECTO has a physics model, the Steady State Model (SSM): a heat balance of the passenger/driver compartment at fixed environmental conditions, which gives a heating or cooling demand, splits heating between heat pump, electric heater and fuel heater, converts it to electric power with COPs and efficiencies, and adds ventilation fan power.

HDEV applies that bus SSM to a truck cab, per weather hour:
- `ssm_total_w`: heat balance of the cab (W, positive = cab gains heat) at a cabin temperature `T_calc`: walls `(T_amb − T_calc)·A_surface·U`, people, sun through windows, plus HDEV's fresh-air term.
- `HVAC_thermal`: runs the balance at the heating setpoint (18 °C) and the cooling setpoint (23 °C); decides heating / cooling / ventilation; subtracts waste heat; splits the heat (`climate_lookup`); caps it at max heating/cooling power; turns heat into battery W (heat pump ÷ COP, electric heater ÷ efficiency, AC ÷ cooling COP); adds fan power `cab_volume·fan_rate·spec_vent_power`; returns `HVAC_el` (W electric) and `fuel_heat` (W heat from a diesel heater, not from the battery).
- `climate_lookup`: COPs by linear interpolation over temperature; heating split shares by the nearest temperature point (tie → colder point).

---

## 2. Gates (must pass before anything else)

**Gate 1, environment:** run `docs/research/drag-default-test-2026-11/run_steps.py` unchanged. Confirm Chain S, variant V1, reference load: RegionalDelivery **0.9749** and UrbanDelivery **0.8502** kWh/km (±0.0005, from its regenerated `step3_kwh_per_km.csv`). If it fails, stop everything except Part A and report what differs.

**Gate 2, code of record:** load the notebook with `_load_notebook.py`. Confirm the three functions in Appendix 1 are byte-identical to the notebook cells. Diff them against any older copy in `src/` and report differences. The notebook is the code of record.

**Gate 3, VECTO reproduction:** write a line-by-line Python port of VECTO's SSM path (`SSMRun.TotalW`, the heating/cooling/ventilation decision in `SSMCalculate.cs`, the heating split and caps, COP and fan power) in `docs/research/hvac-review-2026-11/vecto_ssm_port.py`, with every line citing the C# line it ports. If VECTO's test project has SSM test cases with expected values, run the port against them first and report the match. Then run Bob's functions and the port on the same inputs: a grid of `T_amb` −30…+40 °C (1 °C), solar 0…1000 W/m² (100 W/m²), `Q = 0`, VECTO default parameters from `SSMDefaults.AHSM` / `DeclarationData.cs` (cite each). Report the max absolute difference in `HVAC_el` and in each part (heat pump, electric heater, AC, fan). Earlier claim to confirm or reject: "Bob's code matches VECTO with all three ventilation switches on; run1 ≥ run2 always, so the three modes cover every hour."

---

(The full prompt continues with sections 3 "Questions to answer from the VECTO source (Part A)" Q1–Q13, 4 "The parts" A–L, 5 "Deliverables", 6 "Stop conditions" and Appendix 1 (code of record). It was delivered to Kiro in the session message of 12 Nov 2026; the Appendix 1 code is in the notebook `HDEV_NEW_code_of_record_2026-11-12.ipynb` cells 11–13, and is not retyped here (the prompt itself says to load it from the notebook). A short summary of the later sections is in `docs/research/hvac-review-2026-11.md`, section "Task scope".)
