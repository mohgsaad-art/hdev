# Kiro task: EEA certified e-trucks — test set, library draft, HDEV vs VECTO vs OEM (7 Nov 2026)

Write for Bob in plain English, short sentences. Bob is the only person named.
Repo: `mohgsaad-art/hdev`. New branch: `eea-truck-validation-2026-11`. **Do not change `src/`.** Test code goes in `docs/research/eea-truck-validation-2026-11/`.
VECTO source: `mohgsaad-art/VECTO` (EUPL 1.2).

## 0. What this is

The EU's EEA dataset (Reg. 2018/956, reporting period 2024–25, CC-BY 4.0) holds, per registered heavy truck:
- its certified VECTO inputs (masses, axle, CdxA bin, battery, e-motor/IEPC, aux technologies), and
- its certified VECTO results per mission and payload (kWh/km, range).

Bob joined the tables. For 4,603 electric trucks with full component records, we now have real model names next to certified inputs and certified kWh/km.

This task has four jobs:
1. Build the clean truck test set and a draft library table from the join (rules are fixed, section 2).
2. Settle what the certified numbers mean (section 4), before any comparison.
3. Run HDEV on a sample of real certified trucks and compare with their certified kWh/km (section 5).
4. Add the OEM website figure for the same trucks as a third column (section 6).

## 1. Read first

All on `main`:
- `docs/research/inputs/findings-eea-2024-join-trucks-2026-11-07.md` — **read this first**. Claude's analysis of the join and the rules Bob agreed.
- `docs/research/eea-hdv-2024-join/`:
  - `vehicles_xev.csv` — one row per vehicle (22,445 rows: ZEV, HEV and "other"; use ZEV trucks only).
  - `missions_xev.csv` — certified mission results for those vehicles (one row per vehicle × mission × payload).
  - `configs_xev.csv`, `missions_by_config_xev.csv`, `join_report.txt` — grouped views from the join script. **Do not use them as the test set**: they were built before the rules in section 2 (they group by Make/Model strings and include placeholders). Rebuild from the per-vehicle files.
- `docs/research/eea-hdv-2024-peeks/` — header + sample rows of every EEA table, the peek script and the join script (`join_xev_tables.py`).
- Earlier drivetrain work you must reuse, not rebuild:
  - `docs/research/drivetrain-inputs-fallbacks-2026-11/` (`_stdval.py`, `_harness.py`, `run_tests.py`): EU standard-value drivetrain, VECTO generic axle, coasting drag, harness around the code-of-record `driver_model`.
  - `docs/research/drag-default-test-2026-11/` (`_chain.py`, `_driver_dragtable.py`, `run_steps.py`).
  - Results so far (from the 3 Nov matrix, Claude): on the VECTO E2 example, constant 0.95/0.95/0.98 efficiencies are 24–32 % below VECTO; EU standard maps −8 to +6 %; own maps + VECTO E2 drag within 1 %. On two VECTO test tractors the fallbacks spread −22 % to +54 %. **No fallback stayed within ±10 % on all three.** These were VECTO example vehicles, not certified trucks. This task is the first test on certified trucks.
- Reg. 2017/2400 consolidated (EUR-Lex, CELEX 02017R2400, 01.01.2026 consolidation): Annex IV (output fields), Annex Xb (standard values for e-machines, IEPC, REESS).

Files that may or may not be on `main` when you start (Bob is adding them; check `docs/research/` and `docs/research/eea-hdv-2024-join/`):
- `hdv_2024_iepc.csv`, `hdv_2024_electricmachine.csv`, `hdv_2024_capacitor.csv` (small).
- `axle_xev.csv` and `steering_xev.csv`: the EEA axle and steering-pump rows for our vehicles, made with `docs/research/eea-hdv-2024-peeks/extract_axle_steering_xev.py`. The axle table (peek: `peek_hdv_2024_axle.txt`) has, per vehicle and axle: `AxleNumber`, `TyreDimension`, certified `SpecificRRC`, tyre `CertificationNumber`, `Twintyres`.
If missing, mark the dependent items `[BOB]` and continue.

## 2. Rules (strict, already decided by Bob)

1. **Scope:** ZEV-flag trucks (VehicleCategory N2/N3) **with a battery record**. Ignore hybrids and the 5,993 ZEV trucks without battery records (VECTO 3.3.x placeholders). Buses are out of scope for this task.
2. **Zeros are missing** (e.g. `Axlegear_Ratio = 0.00`, gears `0`).
3. **Completeness is architecture-aware:**
   - E2 / E3: axle ratio > 0 required.
   - E-IEPC: IEPC ratio required; axle ratio required only if the IEPC does not include the axle/differential. `DesignTypeWheelMotor = true` → no separate axle gear. For the 355 Fuso Canter / IVECO S-eWay rows (not wheel motor, no axle ratio) check `DifferentialIncluded` in `hdv_2024_iepc.csv`; if the file is missing, keep them out and mark `[BOB]`.
4. **Deduplicate only exact duplicates** of the full config key. Never fill a field from another row that differs in any key field, even with the same Make/Model name.
5. **Do not collapse mass.** Library rows carry curb mass as min/max. Validation runs use each vehicle's own `TotalVehicleMass` from `missions_xev.csv`.
6. Clean Make strings without changing meaning ("Mercedes Benz" = "Mercedes-Benz", "KING LONG" = "King Long"). List every mapping you apply. Rows with Make "##VEHICLE_MAKE##", "added" or empty stay in the counts but are flagged and left out of the OEM comparison.
7. No invented numbers. Every value needs a source (file + column, VECTO file + line, regulation article/annex/point, or URL + quote). Tags: `[V]` opened primary, `[C]` secondary, `[D]` derived (show arithmetic), `[INFERENCE]`, `[BOB]` could not get it.
8. Keep apart: installed vs VECTO-simulated usable vs OEM-declared usable kWh; rated vs continuous vs peak power; battery-side vs grid-side kWh/km; certified (measured component) vs certified (standard values) vs VECTO simulated vs OEM claim.

## 3. Job 1: test set and library draft

1. Build `truck_vehicles.csv`: one row per in-scope vehicle, cleaned (rules 1–6), with a `complete` flag and a `missing_fields` text column.
2. Build `truck_configs.csv`: exact duplicates collapsed. Key = all component/config fields (make, model, group, axle config, architecture, axle ratio, gears, CdxA bin, battery packs installed/usable, nominal V, e-machine description, IEPC description incl. wheel/diff flags, pneumatic tech, HVAC config fields, PTO flag, TPMLM). Add: vehicle count, registrations, DK registrations, curb mass min/max, certification method per component, VECTO version range, simulation date range.
3. Build `truck_missions.csv`: per config × mission × payload, min/median/max certified kWh/km and range, plus the vehicle count. Keep `Mode`/`ResultType` (seen values: `Total`, `ResultSuccessPEVType`, `m:ResultSuccessPEVType`) and explain what they mean from VECTO code or Annex IV.
4. Report counts in plain terms: vehicles, configs, makes, models; complete vs incomplete; per make; per architecture; measured vs standard-value components.
5. Draft `library_schema_eea.md`: the vehicle-library columns that EEA can fill, each with unit, provenance class (certified measured / certified standard values / VECTO simulated / registry / derived), coverage % in this test set, and the EEA column it comes from. List what EEA cannot fill (charging power: `OffVehicleChargingMaxPower` is 0 % filled for ZEVs; chemistry; OEM usable kWh; peak power/torque; motor maps; ePTO kW; tyres unless the axle table has them).

## 4. Job 2: what the certified numbers mean (settle before comparing)

Answer each from VECTO source (file + line) or Reg. 2017/2400 (annex + point). If you can't, say so.
1. **kWh/km basis.** Is `ElectricEnergy_kwh_km` (missionprofile / MRF "Energy consumption kWh/km") energy at the battery terminals, at the REESS incl. internal losses, or from the grid incl. charging losses?
   - Claude's check: `kWh/km × ActualChargeDepletingRange / bat_usable_sim_kwh` = 1.005 median (0.992–1.017, 44,360 rows). [INFERENCE] points to battery side but proves only consistency. Confirm in code.
   - Earlier work: VECTO `.vsum` has both terminal energy and `EC_el_final` (incl. battery losses, +1.1–1.6 % on E2). State which one the MRF reports.
2. **Usable capacity.** How VECTO computes `TotalUsableCapacityInSimulation` (SoC window? standard values?). Is the ~0.855 usable/installed ratio seen in the data a regulation default? Give the clause.
3. **Standard values.** When `CertificationMethod = StandardValues` for an e-machine, IEPC or battery: which inputs are still OEM-declared (e.g. rated power, ratio) and which are generated by VECTO (maps, drag, losses)? Point to Annex Xb and the VECTO classes that generate them.
4. **Missions → cycles and loads.** For each mission name in `missions_xev.csv` (Long Haul, Long Haul EMS, Regional Delivery, Regional Delivery EMS, Urban Delivery, Municipal Utility, Construction, and any others): the VECTO cycle file, how payload and `TotalVehicleMass` are set, and what body/trailer is assumed (mass and CdxA addition). Confirm `TotalVehicleMass` already includes body/trailer + payload.
5. **CdxA.** EEA gives only the bin (A1–A24, Reg. 2018/956 Annex I Part C). Give the bin edges from the regulation. Explain how VECTO turns the vehicle's certified CdxA into the mission CdxA (body/trailer delta, crosswind correction) for rigid trucks and tractors.
6. **Auxiliaries.** For each aux technology label found in the in-scope trucks (pneumatic, steering pump from `steering_xev.csv`, HVAC config, electric system), give the VECTO declaration electric power per mission for PEVs (file + row).
7. **Tyres / RRC.** The axle table gives certified `SpecificRRC` and `TyreDimension` per axle. Explain how VECTO uses them in declaration mode: how per-axle RRC is combined with the mission's axle load shares (incl. trailer axles, which are not in this table) and the load-dependent exponent; which axle sets r_dyn; how `TyreDimension` maps to `Wheels.csv`. Give file + line. Note any vehicles with RRC missing or with `CertificationNumber` = N/A.

## 5. Job 3: HDEV vs certified kWh/km

**Sample.** Pick 40–60 complete configs, spread across: make (all makes with complete configs), architecture (E2, E3, E-IEPC incl. wheel-motor), vehicle group, component certification method (measured vs standard values), and battery size. List why each was picked. Run each on all its certified missions and both payloads, at each vehicle's own `TotalVehicleMass` (if one config has many vehicles, run the vehicle with median mass and the min and max; say which).

**HDEV runs.** Use the existing test harness (section 1). No engine edits. For every run:
- cycle = the VECTO declaration cycle for that mission;
- mass = `TotalVehicleMass`;
- axle/IEPC ratio, gears, motor type/count/rated kW from the join;
- aux = VECTO declaration values for that truck's technology labels (section 4.6);
- weather = VECTO declaration (as in the 3 Nov matrix);
- kWh/km on the same basis as the certified figure (section 4.1). If HDEV and EEA bases differ, convert with a stated, sourced factor or report both.

Variants (each a separate column):
- V-A: today's constant 0.95/0.95/0.98, no drag.
- V-B: EU standard-value drivetrain maps + EU standard drag (`_stdval.py`).
- V-C: VECTO bus-generic motor method (PSM or ASM as the EEA `ElectricMachineType` says; for IEPC say what you used).
- Tyres: use the vehicle's own certified per-axle `SpecificRRC` and `TyreDimension` from `axle_xev.csv`, combined as VECTO does (section 4.7). Trailer/semi-trailer tyres for tractors: use the VECTO declaration trailer values (file + row). If `axle_xev.csv` is missing, use two RRC bounds you justify from a source and mark `[BOB]`.
- For each variant: CdxA at the bin's lower and upper edge (two runs). Report both. Do not pick a single "best" CdxA.

**Outputs.**
- `hdev_vs_certified.csv`: config, vehicle, mission, payload, mass, certified kWh/km, each HDEV variant × corner, % difference.
- Summary in plain terms: error distribution (median, 10th/90th percentile) per variant, per architecture, per mission, measured vs standard-value components. Say whether the certified value falls inside HDEV's CdxA range.
- Flag runs where the driver/motor cannot follow the cycle (power or torque limit), as in the 3 Nov matrix; report their share.
- If any input needed for a run is missing, skip the run and list it. No guessed fill-ins.

## 6. Job 4: OEM website as third column

For 15–25 of the sampled configs (cover each make):
1. Find the OEM's own page or spec sheet for the same model generation. Record URL, date, model generation, and the exact quote.
2. Extract what it states: range (km) and its conditions (payload, cycle, temperature, "up to"), kWh/km if given, installed and usable kWh, charging power.
3. Derive kWh/km only when the same page gives usable kWh and range under stated conditions. Tag `[D]`, show arithmetic, and say whether the page's kWh is installed or usable. If the page says "VECTO" or cites certification, say so (then it is not independent).
4. Matching rule: only match an OEM page to an EEA config when battery size and motor/architecture agree. If they don't agree, record "no match" with the reason. Model name alone is not a match (e.g. EEA "Actros" covers several eActros variants).
5. Output `three_way.csv`: config, mission (if the OEM states one), certified kWh/km, HDEV kWh/km (each variant, CdxA range), OEM-stated or derived kWh/km, OEM conditions, tags.
6. Interpretation rules for the report:
   - HDEV vs certified = model accuracy (same cycle, mass, inputs).
   - OEM vs certified = how the OEM's conditions differ from certification.
   - HDEV vs OEM = only meaningful where conditions match; say when they don't.
   Don't call any column "the truth".

OEM documents are copyrighted: store values with citation, not the PDFs. Trade press is a lead only.

## 7. Deliverables

In `docs/research/eea-truck-validation-2026-11/`:
1. `truck_vehicles.csv`, `truck_configs.csv`, `truck_missions.csv`
2. `make_mapping.csv` (every Make string change)
3. `library_schema_eea.md`
4. `certified_numbers_meaning.md` (section 4, with file/line and annex/point references)
5. `sample_selection.md`
6. `hdev_vs_certified.csv` + the scripts that produced it
7. `three_way.csv`
8. `report.md`. Top: max 15 lines answering:
   - How many real e-truck configs can EV Scope use, and how complete are they?
   - What do the certified kWh/km and usable kWh mean exactly?
   - How close is HDEV to certified kWh/km, per drivetrain variant?
   - How do OEM website figures compare?
   - What is still missing, and who has to get it (`[BOB]` list)?
   Then detail.
9. A PR against `main`. No changes to `src/`.

## 8. Done when
- Every in-scope vehicle is in `truck_vehicles.csv` with a complete flag and its missing fields.
- Section 4 has an answer with a source, or a clear "not found" for each of the 7 points.
- Every HDEV run uses only sourced inputs; skipped runs are listed with the reason.
- Every OEM value has URL, date, quote and tag.
