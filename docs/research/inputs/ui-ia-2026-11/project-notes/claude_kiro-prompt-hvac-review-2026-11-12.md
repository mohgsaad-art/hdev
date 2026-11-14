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

## 3. Questions to answer from the VECTO source (Part A)

Answer each with `[VECTO]` file + lines + commit, and a verdict: **MATCH**, **DEVIATION (already flagged)**, **DEVIATION (new, flag it)** or **BUG**. Quote the exact C# lines.

- **Q1 Heat balance.** Exact formula of `SSMRun.TotalW` and every constant it uses: heat per person (50 / 80 W), clouding factors (0.65 / 0.8), boundary temperature (17 °C), window g-value (0.95), the **0.25 solar factor**. Where does each come from (`SSMDefaults.AHSM`, `SSMInputs.cs`, code)? What do they physically mean? Is there any documentation (VECTO user manual, TU Graz bus aux reports, the SSM tool's original Excel/VBA, bus HVAC study for the Commission) that explains 0.25? If none: `NO SOURCE`.
- **Q2 Solar input.** What irradiance does VECTO's SSM expect: global horizontal, on the window plane, direct only? What units? Is it the same quantity as DMI `radia_glob_past1h`? If not, what conversion would be needed (and is it worth it)?
- **Q3 Environmental conditions.** What is in `DefaultClimatic.aenv` (temperatures, solar values, weights) and how VECTO combines the SSM results over these points into one value per mission. HDEV evaluates every hour of real weather instead. Is the per-point maths identical, so that HDEV's hourly result at VECTO's points reproduces VECTO's per-point values? Then compute HDEV's weighted value at VECTO's points and compare with VECTO's bus result.
- **Q4 Heating / cooling / ventilation decision.** VECTO's logic with the two setpoints, `T_cool_off`, and the three ventilation switches (`VentilationOnDuringHeating`, `VentilationWhenBothHeatingAndACInactive`, `VentilationDuringAC`). Confirm HDEV's `losing_heat`, `gaining_heat`, `ventillation_status` and `fan_rate` lines, including what happens when `run1 > 0 > run2` (cab between setpoints).
- **Q5 Waste heat.** What VECTO subtracts as waste heat for buses (engine coolant heat for ICE? anything for BEV: motor, inverter, battery?). HDEV's default `waste_heat = 0`. Is 0 the conservative choice for a BEV truck?
- **Q6 Heating split and caps.** `HeatingDistribution.csv` / `HeatingDistributionCases.csv`: how the case is chosen (HDEV leaves "HD-case column picking" to the parser), how VECTO picks the share at a temperature (nearest point? step? interpolation?) and tie handling. How VECTO caps heat pump + electric heater at max heating power, and how the fuel heater is treated (`FuelFiredHeaterPower`, efficiency 0.80). Confirm HDEV's `rest` / `scale` logic, including `fuel_share = 1.0` and shares that do not sum to 1.
- **Q7 COP.** Where VECTO gets heating and cooling COP vs temperature (per refrigerant: R-744, R-134a, R-1234yf …; `CalculateCOP` ~566; `SSMTechList.csv`). Interpolation or steps? What VECTO does at temperatures with no COP (earlier finding: silently 0 W; confirm). Is the parser's flat clip below −5 °C optimistic or conservative, and by how much?
- **Q8 Electric heater and fan constants.** Sources of `eh_eff = 0.93` and `spec_vent_power = 0.56` Wh/m³; ventilation rates (air changes per hour) for heating and non-heating (`VentilationRate` ~451) and what HDEV should pass for a truck cab.
- **Q9 Fresh air vs ventilation.** Does VECTO's ventilation rate bring outside air into the heat balance anywhere, or is it only fan power? Is HDEV's `q_freshair` double-counting anything in VECTO's model? Is `Q` (m³/h of fresh air) the same air as `cab_volume·vent_rate`? If they should be linked, say how.
- **Q10 Driver vs passenger compartment.** The bus SSM treats driver and passenger compartments separately (`HVACHeatingPowerDriver.csv` etc.). Which one is the right analogue for a truck cab, and does HDEV mix them?
- **Q11 Technology benefits.** What `TechnologyBenefits.cs` / `SSMTechList.csv` contain (double glazing, insulation, heat recovery, adjustable heaters …). Which would matter for a truck cab and could be an easy user choice (yes/no) instead of a hard number?
- **Q12 Lorry table.** What VECTO's lorry `HVAC-Table.csv` values represent (which conditions, which source, mechanical or electric). At which ambient conditions does HDEV's thermal model give the same W as the table for the E2 missions?
- **Q13 Anything else** VECTO's SSM includes that HDEV has no term for (e.g. humidity, door openings for buses, preconditioning, auxiliary heater run-on, minimum compressor power). List each, with size if possible.

---

## 4. The parts

### Part A: line-by-line audit
Go through Appendix 1 line by line. For each line: what it does in plain words; the VECTO lines it stands in for; verdict. Answer Q1–Q13. List every hard-coded number and every default argument (`273.15`, `3600`, `0.93`, `0.56`, `(50, 80)`, `(0.65, 0.8)`, `17`, `0.95`, `0.25`, `18`, `23`, `101325`, `287.05`, `1005` …) and say whether each is a unit definition, a VECTO constant (source), a standard value (source), or an HDEV choice. Check the units of every argument (W, W/m², m², W/m²K, m³, 1/h, Wh/m³, m³/h, °C) and flag any hidden unit conversion against rule 7 (e.g. `Q/3600`: m³/h → m³/s; should the parser pass `Q` in m³/s?).

Also check robustness, each as a short test (Part B): scalar vs array inputs for every argument (e.g. `solar` scalar with `T_amb` array; `max_heating_power` array); `T_amb` exactly at a heating point (tie in `climate_lookup`); `T_amb` outside the COP grid (`np.interp` holds end values: is that what VECTO does?); NaN in `T_amb` or `solar`; shares with NaN; `cop = 0`; `U = 0`; `A_window = 0`; `max_heating_power = inf`; `waste_heat` larger than demand; 2-D `T_amb` (days × hours).

### Part B: unit and analytic tests (`tests/hvac/`, runnable with `pytest`)
1. `Q = 0` reproduces the VECTO port (Gate 3) exactly.
2. Energy balance signs: very cold and dark → heating only; very hot and sunny → cooling only; in between → ventilation only; check the boundaries.
3. Monotonicity: `HVAC_el` never decreases as `T_amb` falls below the heating setpoint (with fixed solar); report any jump and its cause (e.g. the people/clouding switch at `T_boundary = 17 °C`, the nearest-point share switch). Show each jump in W.
4. `climate_lookup`: equals `np.interp` for COPs; nearest-point shares with ties going to the colder point; works for 1-D and 2-D `T_amb`.
5. Caps: heating demand above `max_heating_power` keeps the heat pump / electric heater ratio; `fuel_heat` is not capped (confirm against VECTO, Q6); cooling cap.
6. Fresh-air term: equals `rho·cp·Q/3600·ΔT` against a hand calculation with ISO 2533 / ideal-gas density (cite the constants).
7. Shape contract with the consumption engine: per-hour array of length = number of weather hours, indexed the same way as `T_amb_h` in `consumption_engine` (cell 16); scalar HVAC also works. Report any mismatch.

### Part C: VECTO reproduction and the deviation register
Using `vecto_ssm_port.py` and Bob's functions:
1. At VECTO's environmental-condition points (Q3), with VECTO's bus parameters: per-point and weighted results, Bob vs port.
2. With Bob's truck-cab placeholders (A_surface 20 m², U 3.0 W/m²K, A_window 4 m², cab_volume 6.5 m³; all `[ASSUMPTION]` until sourced, Part G): same comparison, so the effect of each HDEV deviation is shown separately: (a) fresh air on, (b) hourly real weather vs condition points, (c) COP interpolation vs VECTO's method, (d) nearest-point split, (e) COP clip below −5 °C.
3. Deviation register: every HDEV-vs-VECTO difference, its size, and the exact sentence to use in a client report.

### Part D: sensitivity (which inputs matter, which users can give)
Over one Danish hourly year (DMI, Part 0.4) and the E2 missions' operating hours (assume a stated `ILLUSTRATIVE` daily schedule, e.g. 06:00–16:00 weekdays, and say so): one-at-a-time and a tornado chart of annual HVAC kWh for each input over its **sourced** range (if no sourced range: `NO SOURCE`, skip the bar): `A_surface`, `U`, `A_window`, `g`, `solar_factor`, `Q`, `N_persons`, setpoints, `cop_heat_points`, `cop_cool_points`, heating shares (heat pump present or not), `eh_eff`, `max_heating_power`, `waste_heat`, `cab_volume`, `vent_rate`. Rank the inputs. For the top five, say whether a fleet user can give it (rule 11), the best sourced default, and the conservative end.

### Part E: HDEV thermal vs VECTO's constant table on real Danish weather
For the E2 Regional and Urban missions (and LongHaul if the cab differs; if so, say how): annual and monthly HVAC energy (kWh) and kWh/100 km from (i) VECTO's lorry table value (from the `.vmod`/`.vsum`, cite), (ii) HDEV thermal with the current placeholders, (iii) HDEV thermal with the best sourced cab values from Part G. Also share of trip energy, using the E2 Chain S kWh/km from Gate 1. Show the coldest week and hottest week separately. Mark which result is conservative.

### Part F: physics beyond VECTO (research + measured effect; candidates, not changes)
For each item: what the physics is; the best sources (standards first, then measured studies, then models); typical size for a 12–40 t electric truck cab in Danish and Nordic conditions; how HDEV could include it **without breaking rule 8** (prefer a per-hour term or factor); what extra user input it needs (prefer none); and the measured effect on E2 Regional and Urban using `reference_copy.py` variants. Mark which are conservative.

1. **Driving vs parked heat transfer.** Outside heat-transfer coefficient rises with vehicle speed; NREL's measured UA (51/65 W/K) is parked. Is there a sourced speed-dependent UA for truck cabs (or a standard correlation, e.g. flat-plate forced convection)? Could the parser pass two UA values (parked / driving) or a per-hour mean speed?
2. **Cold-cab warm-up (transient).** The first minutes after a cold start need extra heat to warm the cab's thermal mass. Sources for truck cab thermal mass (J/K) and warm-up energy per start; how often starts happen (stops per day from the route). Can it be an energy per start, added at departure rows, keeping the hourly structure?
3. **Preconditioning on the charger.** Many BEV trucks warm the cab (and battery) from the grid before departure. Size the effect on battery energy. Bob decided no aux while charging (13 Oct); report only what preconditioning would change and what input it needs.
4. **Door openings** on urban delivery (cab door open at each stop): any measured air exchange or heat loss per opening for truck cabs (or vans/buses, flagged)? Size it with the stop count of the Urban cycle.
5. **Humidity and demisting.** Winter demisting needs fresh air or AC with reheat. Sources and size. Is ignoring humidity conservative or not?
6. **Fresh air per person.** Standards for fresh-air rate per occupant (e.g. EN 16798-1, ISO 7730/ASHRAE 62.1 for buildings; any vehicle standard or OEM practice; Dvorak 2025: 100 m³/h for 2 occupants at 1000 ppm CO₂). Check the current proposed default (100 m³/h) against them; give the sourced range.
7. **Solar.** Whether window-only solar gain with a 0.25 factor is reasonable, vs solar on the opaque cab surfaces (sol-air temperature, ASHRAE Fundamentals) and window orientation. Size the difference on a Danish summer day.
8. **Heat-pump COP vs ambient, measured.** Measured heating COP curves for bus/truck/van heat pumps (R-744 vs R-1234yf vs R-290), especially below −5 °C, to replace the parser's flat clip. Standards for COP testing (SAE J2765 for MAC; EN 14511 for heat pumps; any vehicle HP standard). Give values only from full text.
9. **(Report only) Battery and motor conditioning in cold/heat.** VECTO's Cond is a flat 550–600 W. List the best sources on BEV truck battery heating/cooling power vs ambient (e.g. Dollinger & Fischerauer 2021, Energies 14(18) 5804; Stanford drayage study; Mercedes eActros 600 winter tour 2025: battery heating < 1 point of +25 %; Öko-Institut ELV-LIVE). Say whether it could share the hourly weather input with `HVAC_thermal`. No variants, no code.

### Part G: data sources that make the inputs easier (the most useful part for Bob)
Goal: replace HDEV's unsourced placeholders with sourced defaults, ideally derived from things a fleet user knows (cab type, truck model, vehicle class).
1. **Cab geometry by cab type**: outer surface area, interior volume, glazing area for common EU cab types (day cab / sleeper cab; low / normal / high roof; e.g. from OEM dimension sheets (Mercedes, Volvo, Scania, DAF, MAN, Renault), VECTO cab-type definitions if any, ISO/SAE vehicle dimension standards). Show how `A_surface`, `cab_volume`, `A_window` could be derived from cab width × height × length with a sourced method, or say `NO SOURCE`.
2. **UA / U-value of truck cabs**: NREL CoolCab and CoolCalc (`NREL/TP-5400-52452`, `NREL/TP-5400-66860`, OSTI 973699), Lustbader 2012, Dvorak 2025, Ramesh Babu 2025 (DOI 10.1016/j.tsep.2025.103417), any EU measurement. Extract the exact numbers with table/figure references.
3. **Heat pump / heater / AC data from OEM spec sheets**: does the truck have a heat pump (yes/no)? Heater kW, AC kW. Collect for the main EU BEV trucks (eActros 300/400/600, eEconic, Volvo FH/FM/FL Electric, Scania BEV, DAF XF/XD/XB Electric, MAN eTGM/eTGX, Renault E-Tech). This lets the UI ask one yes/no instead of a COP curve.
4. **Weather**: confirm which DMI parameters and stations to use (temperature, global radiation), units, gaps, and licence; confirm the DMI global radiation matches what the SSM expects (Q2). Also name the equivalent free sources for other EU countries (e.g. ERA5/Copernicus, national met services) since the tool is meant for any country.
5. **Measured BEV truck energy vs temperature** for validation (Part I): Öko-Institut ELV-LIVE temperature-binned kWh/km, ICCT 2023 real-world HDV BEV report, NREL Fleet DNA, Mercedes eActros 600 winter tests, Volvo or Scania winter data, Nordic fleet trials (e.g. Swedish/Norwegian/Finnish e-truck reports, VTT).
For every source: what it gives, licence, whether you read the full text, and the exact values with page/table.

### Part H: how other tools do it (read the code where it is open)
Compare term by term with HDEV: heat balance terms, cabin temperature control (steady vs transient, setpoints), fresh air, solar, COP model (fixed, curve, fraction of Carnot), heater types, fan power, waste heat, battery thermal coupling, time step.
- Read the code: NREL FASTSim (`mohgsaad-art/fastsim`, cabin/HVAC thermal model; Rust files and Python; earlier note: transient lumped cabin + PID + COP as fraction of Carnot, speed-dependent heat loss; fitted values are car-specific), `eflips-depot` (consumption look-up with ambient temperature axis), `spice_ev`, `blast-lite` (battery thermal), `dt-cargo`, `acnportal` (say if a tool has no HVAC model).
- Read the documentation (or code if public): TU Graz PHEM, Argonne Autonomie, US EPA GEM, SUMO electric vehicle model, any TUM / KIT / Chalmers truck-energy tool with HVAC, and the original VECTO bus auxiliaries / SSM documentation (TU Graz, Ricardo, or the Commission's bus study).
One table: tool | each term's formula | source file/line or doc page | difference from HDEV | does it change HDEV's numbers (estimate only if sourced). Say for each tool whether you read code, full documentation, or only a summary.

### Part I: independent validation
Search for measured HVAC electric power (or energy) of electric truck cabs, and failing that electric bus driver compartments or vans (flagged), against ambient temperature: Dvorak 2025 (WEVJ 16:129, AIT truck cab rig), JRC133756 (heating at −7 °C vs cooling at 35 °C), Ramesh Babu 2025 (simulated, flag), Mercedes eActros 600 winter (cab climate about 5 points of +25 % at −2 °C, OEM press text), Öko-Institut, any e-bus HVAC measurements. For each: what was measured, conditions, and how HDEV compares when set up with **that** vehicle's sourced values only (anything missing → `BLOCKED`, no guessing). Earlier [CALC] lead to re-check: at −10 °C HDEV gives about 3.1 kW vs Chalmers 4.15–4.45 kW heater power, so HDEV may be low while driving. If nothing measured exists for a quantity, write `NOT FOUND`. Every document you could not open goes in the **"Bob to fetch"** table.

### Part J: VECTO runs Bob should do (write them, don't run them)
Only if they answer a question this job could not close. Example: a VECTO completed-bus declaration run whose SSM output (per environmental condition, if VECTO writes it) lets Gate 3 be checked against VECTO's own numbers. Exact GUI steps or job files for VECTO 5.1.6, which output columns or files to look at. Put them in `reference/vecto/jobs/hvac-2026-11/` with a README. If no run is needed, say so.

### Part K: performance
Time `HVAC_thermal` on one day (24 h) and on 365 days × 24 h, and on a 2-D array (days × hours); mean of 5 runs; say the CPU. Time any transient variant from Part F the same way. Say whether the hourly HVAC result should be cached per (weather year × cab inputs) and what the cache key would be.

### Part L: plain-English explainer
Write `docs/explainers/hvac-explained.md`: what the three functions do, the heat balance in plain words with a small worked example (ILLUSTRATIVE numbers, labelled), how heating/cooling/ventilation is decided, how heat becomes battery power (COP, efficiency), the fan, and which VECTO lines each piece stands in for. Define every term (U-value, UA, COP, g-value, setpoint, air change rate).

---

## 5. Deliverables

1. `docs/research/hvac-review-2026-11.md`, in this order:
   - **Summary first (one page):** what is right, what is wrong, a ranked list of proposed changes (each with measured effect in kWh and %, source tag, engine or parser, VECTO / standard / HDEV assumption, and whether it needs a new user input), and open items.
   - Gates 1–3.
   - Part A audit table + Q1–Q13 answers.
   - Parts B–E results (tables first; graphs under `docs/research/hvac-review-2026-11/`).
   - Parts F, G, H, I tables.
   - **Proposed changes:** before/after snippet against Appendix 1, why (source tag), measured effect, engine or parser, and whether it only swaps one assumption for another.
   - **Input table for the UI**: every input of the three functions | unit | can a fleet user give it? | sourced default (with source) | conservative end | derived from (cab type / OEM sheet / weather / none).
   - **Deviation register:** every HDEV-vs-VECTO difference, its size on E2 Regional/Urban on the Danish year, and the exact sentence to use in a client report.
   - **Parser jobs found** (new checks, lookups, unit conversions and inputs the parser must provide).
   - "Seen in passing (out of scope)", "Choices I made", "Bob to fetch" (link/DOI + exactly which table/figure/value), and the `BLOCKED` list.
2. `docs/research/hvac-review-2026-11/`: `_load_notebook.py`, `vecto_ssm_port.py`, `reference_copy.py` with variants, one runnable script per part (`python run_part_c.py` etc.), the weather CSV with its query, all CSVs and graphs. Each script prints the files it wrote.
3. `tests/hvac/`: Part B tests, runnable with `pytest`.
4. `reference/vecto/jobs/hvac-2026-11/` (Part J, only if needed).
5. `docs/explainers/hvac-explained.md` (Part L).
6. One PR to `main`. The description lists: what was done, how to run every script and the tests, the top 5 findings with numbers, every value with `NO SOURCE`, every `BLOCKED` item, and the "Bob to fetch" list.

## 6. Stop conditions
- If a test shows Bob's code crashes or gives a wrong number on a realistic input, report it as **BUG** with a minimal reproducing input, and keep going.
- Never edit the notebook or `src/`. Never decide an open design choice for Bob.

---

## Appendix 1: code of record (Bob's notebook, 12 Nov 2026; verbatim; load it from the notebook, do not retype it)

### 1.1 `HVAC_thermal` (cell 11)
```python
def HVAC_thermal(T_amb, solar, A_surface, U, N_persons, A_window, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points,
                 hp_share_points, eh_share_points, fuel_share_points, max_heating_power, max_cooling_power, cab_volume, vent_rate, vent_rate_heating,
                 eh_eff=0.93, spec_vent_power=0.56, heat_per_person=(50.0, 80.0), clouding=(0.65, 0.8), T_boundary=17.0, g=0.95, solar_factor=0.25,
                 waste_heat=0.0, T_heat=18.0, T_cool=23.0, T_cool_off=17.0, Q=0.0, p=101325.0, R=287.05, cp=1005.0):
  # Tcalc just becomes the two setpoints for heating and cooling
  T_amb = np.asarray(T_amb, dtype=float)

  # step 1: run ssm total i.e. total heat balance at 18 and 23 C, and get the heating or cooling demand
  run1 = ssm_total_w(T_amb, solar, T_heat, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)
  run2 = ssm_total_w(T_amb, solar, T_cool, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)

  losing_heat = (run1 < 0) & (run2 < 0)
  heating_demand = np.where(losing_heat, np.abs(np.maximum(run1, run2))-waste_heat,0.0)
  heating_demand = np.maximum(heating_demand, 0.0)

  #step 2: how this heat is split between heat pump, electrical heater, and fuel heater and their caps at diff temps SSMCalculate.cs lines 215-245
  cop_heat, cop_cool, hp_share, eh_share, fuel_share = climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points)

  fuel_heat = heating_demand * fuel_share                                            # fuel heater part, not capped here
  sum_heat = np.minimum(max_heating_power, heating_demand * (hp_share + eh_share))   # cap on heat pump + electric heater only

  rest = np.where(np.isclose(fuel_share, 1.0), 1.0, 1 - fuel_share)  # heat pump + el. heater's part; 1.0 if fuel does everything
  scale = sum_heat / rest                                                    # getting a scaling factor to downside but keep ratio
  hp_heat = scale * hp_share                                                 # heat delivered by heat pump [W]
  eh_heat = scale * eh_share                                                 # heat delivered by electric heater [W]

  #step 3: heating W to what it costs the batery W
  if np.any((hp_heat > 0) & np.isnan(cop_heat)):
    raise ValueError("heat pump COP missing for this temperature")  # HDEV: VECTO silently gives 0 W here
  HP_el = np.where(hp_heat > 0, hp_heat / cop_heat, 0.0)             # heat pump: heat ÷ COP
  EH_el = eh_heat / eh_eff                                           # battery W for el heating

  #step 4: cooling
  gaining_heat = (run1 > 0) & (run2 > 0) & (T_amb >= T_cool_off)            # gaining heat at both 18 and 23 setpoint, and Tamb greater than 17
  cooling_demand = np.where(gaining_heat, np.minimum(run1, run2), 0.0)      # cooling demand / heat to remove W, smaller of the two = cool to 23C
  cooling_demand = np.minimum(cooling_demand, max_cooling_power)            # cap at AC max cooling power
  if np.any((cooling_demand > 0) & np.isnan(cop_cool)):
      raise ValueError("cooling COP missing for this temperature")
  AC_el = np.where(cooling_demand > 0, cooling_demand / cop_cool, 0.0)                # battery W for cooling

  #step 5; ventilation fan, VECTO SSMCalculate.cs lines 270-295, 376-397, 399-428; VentPower (SSMInputs.cs:88)
  ventillation_status = ((T_amb < T_cool_off) & (run1 > 0) & (run2 > 0)) | ((run1 > 0) & (run2 < 0))
  fan_rate = np.where(losing_heat, vent_rate_heating, np.where(gaining_heat | ventillation_status, vent_rate, 0.0)) # air changes per hour
  fan_el = cab_volume * fan_rate * spec_vent_power  #m³ × 1/h × Wh/m³ = W

  #step 6: total battery W for HVAC (goes into P_aux as HVAC_power with HVAC_eff = 1.0)
  HVAC_el = HP_el + EH_el + AC_el + fan_el    # heat pump + electric heater + AC + fan [W electric]
  return HVAC_el, fuel_heat                   # fuel_heat = heat from the diesel heater [W heat], not battery
```

### 1.2 `ssm_total_w` (cell 12)
```python
# this is a helper for HVAC thermal
# step 1: cabin heat balance, VECTO SSMRun.TotalW (SSMRun.cs lines 48-64)
def ssm_total_w(T_amb, solar, T_calc, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q):
#ambient Temp, Cabin temp target, surface area cabin, heat dissapation , num of people, surface area of windows, heat per person, clouding low or high, Temp switch for body heat and clouding, solar allowance of windows, soalr factor is unknown?
  T_amb = np.asarray(T_amb, dtype=float) # outside temp per weather hour [°C]
  solar = np.asarray(solar, dtype=float) # sunlight per weather hour [W/m²]
  rho = p / (R * (T_amb + 273.15)) # density of outside air

  q_wall = (T_amb - T_calc) * A_surface * U    #heat thru walls, diff in amb temp and cabin temp * surface area of cabin and heat permissivity
  q_people = N_persons * np.where(T_amb < T_boundary, heat_per_person[0], heat_per_person[1]) # heat thru people, no of people * their body heat based on amb Temp
  q_solar = solar * A_window * g * np.where(T_amb < T_boundary, clouding[0], clouding[1]) * solar_factor # heat from the sun passing thru windows based on clouding
  q_freshair = rho * cp * Q / 3600 * (T_amb - T_calc)
  return q_wall + q_people + q_solar + q_freshair
```

### 1.3 `climate_lookup` (cell 13)
```python
#This is a helper for HVAC thermal
def climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points):
  # abm temp,5 VECTO heat points
  T_amb = np.asarray(T_amb, dtype=float)

  cop_heat = np.interp(T_amb, T_heat_points, cop_heat_points)  # heat pump heating COP per hour
  cop_cool = np.interp(T_amb, T_cool_points, cop_cool_points)  # cooling COP per hour

  dist = np.abs(T_amb[..., None] - np.asarray(T_heat_points, dtype=float))  # distance from each hour to each heating point
  idx = np.argmin(dist, axis=-1)                          # nearest point; on a tie argmin takes the first = colder

  hp_share = np.asarray(hp_share_points, dtype=float)[idx]     # heat pump part of the heat
  eh_share = np.asarray(eh_share_points, dtype=float)[idx]     # electric heater part
  fuel_share = np.asarray(fuel_share_points, dtype=float)[idx] # fuel heater part

  return cop_heat, cop_cool, hp_share, eh_share, fuel_share
```

### 1.4 Where the output goes (read from the notebook; consistency check only)
- `P_aux(..., HVAC_power=HVAC_el, ..., HVAC_eff=1.0)` (cell 9): thermal-mode HVAC is already electric W, so the VECTO 1.25 factor must be 1.0 here (parser job).
- `consumption_engine` (cell 16): HVAC scalar or per weather hour, indexed by `hour = ((t_start + T) // 3600)` like `T_amb_h`. Check this contract in Part B7.
