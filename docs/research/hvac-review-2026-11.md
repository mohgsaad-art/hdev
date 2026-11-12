# HVAC deep dive: `HVAC_thermal`, `ssm_total_w`, `climate_lookup` (12 Nov 2026)

For Bob. Branch `hvac-review-2026-11`. Code of record: `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb`, cells 11–13.
Nothing in the notebook or `src/` was edited. All scripts and CSVs are in `docs/research/hvac-review-2026-11/`; tests in `tests/hvac/` (24 pass); explainer in `docs/explainers/hvac-explained.md`.

**Tags:** `[VECTO]` read in VECTO source (repo `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126ab0bc2ab8beb3eaee878f7198126b600a`; paths below are relative to `VectoCore/VectoCore/` unless stated) · `[REG]` · `[STD]` · `[SOURCE]` · `[CALC]` · `[TEST]` · `[ASSUMPTION]` · `[SIMPLIFICATION]` · `[OPEN]`. Abbreviations for VECTO files: SR = `Models/BusAuxiliaries/DownstreamModules/Impl/HVAC/SSMRun.cs`, SC = `…/HVAC/SSMCalculate.cs`, SI = `…/HVAC/SSMInputs.cs`, CO = `Configuration/Constants.cs`, DD = `Models/Declaration/DeclarationData.cs`.

---

## 0. Summary (one page)

**What is right.** `[TEST]` Bob's three functions reproduce VECTO's bus SSM maths. A line-by-line Python port (`vecto_ssm_port.py`) matches **152 of 152** expected values asserted in VECTO's own unit test file `SSMTestHeatingCooling.cs` (`gate3_vecto_unit_tests.csv`). Bob's code and the port agree to **< 2·10⁻¹² W** on a 781-point grid (T −30…40 °C × solar 0…1000 W/m²) for five heating-distribution set-ups, in the total and in each part (heat pump, electric heater, AC, fan) (`gate3_grid_summary.csv`). At VECTO's own 11 conditions the weighted result is identical (193.39 W for Bob's placeholder cab; `part_c_points.csv`). The claim "run1 ≥ run2 always, so the three modes cover every hour" is **confirmed** when T_cool ≥ T_heat (`test_B2_*`; it fails if a user sets T_cool < T_heat, a parser check). The three ventilation switches are hard-wired `true` for every VECTO declaration bus `[VECTO]` `InputData/Reader/DataObjectAdapter/SimulationComponents/AuxiliaryDataAdapter/PrimaryBusAuxiliaryDataAdapter.cs:536–538`, so Bob's code (which has no switches) is right to assume them on.

**What is wrong or risky (numbers on Bob's placeholder cab, Copenhagen 2025, ILLUSTRATIVE Mon–Fri 06–16 schedule; `Q = 100 m³/h` unless stated).**

| # | Finding | Size | Tag | Where |
|---|---|---|---|---|
| 1 | **BUG (silent)**: one NaN in `T_amb` **or `solar`** gives **0 W** for that hour, even a −10 °C night where solar is irrelevant. The DMI year has 58 temperature and 32 radiation gap hours. | up to 90 h at 0 W | `[TEST]` | `test_BUG_nan_solar_or_temperature_gives_silent_zero_watt` |
| 2 | **BUG-class contract**: a NaN in the COP grid (VECTO's `-` cell: non-R-744 at −20 °C) makes `np.interp` return NaN for **every** T between −20 and −5 °C → `ValueError` at −12 °C. The parser fill must happen before the call. | hours −11…−5 °C: 61 h in 2025 | `[TEST]` | `test_BUG_nan_in_cop_grid_…` |
| 3 | The **18 °C heating set-point** is a VECTO bus boundary, not a measured cab temperature. Both independent sources read use **21–22 °C**. Raising it adds **+112 / +152 kWh/yr (Q=0)** and **+192 / +261 kWh/yr (Q=100)** for 21 / 22 °C (+26 % … +38 %). The conservative direction is the higher set-point. | +25…+38 % | `[CALC]` | `part_f_effects.csv` |
| 4 | Placeholder cab (UA = 60 W/K) gives a heating demand at −10 °C of **1.8–3.0 kW** (set-point 22 °C, Q=0/100) against **4.07–4.45 kW** simulated for a real electric truck cab (Ramesh Babu 2025, Table 4). HDEV is 26–59 % lower. | −26…−59 % | `[CALC]` vs `[SOURCE, full text, simulated]` | `part_i_comparison.csv` |
| 5 | The **fresh-air term is the biggest single lever**: Q=100 m³/h adds **+240 kWh/yr (+55 %)**; Q=0 gives HDEV 168 W mean, below VECTO's lorry table (250 W / 187.5 W). And Q = 100 m³/h exceeds the placeholder fan flow (6.5 m³ × 7 /h = 45.5 m³/h): fan power and Q are not linked. | +55 % | `[CALC]` | `part_c_deviations.csv`, `part_f_effects.csv` |
| 6 | With `HVAC_eff` left at `P_aux`'s default 1.25, thermal-mode watts are inflated by 25 %. | +25 % (678 → 847 kWh/yr) | `[TEST]` | `test_B7_thermal_output_can_feed_P_aux_with_eff_1` |

**Ranked list of proposed changes** (full before/after in section 9; none applied to the notebook):

| Rank | Change | Effect | Engine / parser | Basis | New user input? |
|---|---|---|---|---|---|
| 1 | Fill/validate NaN in `T_amb`, `solar`, COP grids, shares; check `cop>0`, `T_cool ≥ T_heat`, shares sum ≤ 1 | prevents 0 W / `inf` / 200 % heat | **parser** | `[TEST]` | no |
| 2 | Pass `HVAC_eff=1.0` to `P_aux` in thermal mode | −20 % vs the 1.25 default (−169 kWh/yr) | **parser** | `[TEST]` | no |
| 3 | Make the heating set-point an explicit, disclosed input; report 21 °C as a sensitivity | +112…+192 kWh/yr | **parser** (argument already exists) | Daimler press + Ramesh Babu `[SOURCE]` vs VECTO `[VECTO]` | optional |
| 4 | Replace the placeholder cab by sourced values (cab type → geometry/UA) | unknown; −26…−59 % at −10 °C today | **parser** (lookup) | `BLOCKED: no sourced cab geometry/UA found` | cab type only |
| 5 | Link Q to the fan: fan flow = max(Q, V·rate) | fan only, small (< 30 W) | engine (1 line) or parser | `[CALC]` | no |
| 6 | (optional) return fuel **power** = min(heat, heater kW)/0.80 like VECTO SC 208–210 | none on electricity; fuel kWh/yr 138 vs 111 heat | engine | `[VECTO]` | heater kW |
| – | Per-hour parked/driving UA | **no code change needed**: `U`/`A_surface` already accept per-hour arrays (`test_A_per_hour_array_inputs_work_without_code_change`) | parser | Chalmers: +9–10 % heating load 0→90 km/h `[SOURCE, simulated]` | no |

**Rule 9 check.** None of the changes above is "swap one assumption for another": #1–2 fix errors, #3 and #4 are backed by independent sources, #5 is internal consistency. Changing the 0.25 solar factor, the 7 /h vent rate or COPs without a source would be a swap, and was not proposed.

**Open items / NO SOURCE:** explanation of the 0.25 factor; cab geometry, UA, glazing for EU truck cabs; heat-pump COP below −5 °C (measured); door-opening air exchange; cab thermal mass; OEM heater/heat-pump data; see section 14 ("Bob to fetch") and the BLOCKED list.

---

## 1. Gates

**Gate 1 (environment) PASS.** `[TEST]` `VECTO_SRC=/projects/sandbox/_work/vecto-src python run_steps.py` (unchanged) in `docs/research/drag-default-test-2026-11/`. Result in regenerated `step3_kwh_per_km.csv`: RegionalDelivery reference Chain S V1 **0.9749**, UrbanDelivery **0.8502** kWh/km. `git status` shows the regenerated CSVs identical to the committed ones. (The E2 vehicle files came from the same VECTO commit, fetched as git blobs; see section 13.)

**Gate 2 (code of record) PASS.** `[TEST]` `gate2_code_of_record.py`: cells 11, 12, 13 equal Appendix 1 of the prompt. Cells 12 and 13 are byte-identical; cell 11 differs only in trailing white space. No copy of the three functions exists in `src/` (grep: none); the older notebook `HDEV_NEW_code_of_record_2026-11-07.ipynb` has cells 14–16 (same functions at different cell numbers; not diffed line by line). The loader prints: `HVAC_thermal, P_aux, SP_power_helper, climate_lookup, coast_distance, consumption_engine, crosswind_engine, decel_distance, driver_model, force_engine, interp1, payload_engine, pto_engine, ssm_total_w`.

**Gate 3 (VECTO reproduction) PASS.**
(a) `[TEST]` `gate3_vecto_unit_tests.py`: port vs expected values copied from `VectoCore/VectoCoreTest/Models/Declaration/BusAux/SSMTestHeatingCooling.cs` (test bus: code CA, 12 × 2.55 × 3 m, 40 seats, lines 1579–1617). Covered: heating demand CFG1 and CFG3 × 11 conditions; heating distribution CFG1 (16 cases, lines 426–445) and CFG2 (17 cases, lines 480–514: mechanical and electrical heat pumps, electric heater, 30 kW fuel heater); cooling/ventilation single-condition CFG1/CFG3 (8) and the weighted cooling average for CFG1–4 (6). **152/152 within the test's own 1e-3 W.** Two inputs had to be inferred and are confirmed by the match: passenger count `min((L_int−1.2)·W·2.2, 40)+1` (group 32a, Interurban density 2.2 pass/m², `Resources/Declaration/CompletedBusSegmentationTable.csv` line 9; `[ASSUMPTION]` that the test uses the first mission = Interurban) and the "separate air distribution ducts" benefit (0.04 on cooling power and cooling ventilation, `SSMTechList.csv`).
Not covered: mechanical-compressor power chain after the SSM, CFG5–10 (two-compartment AC), low-floor buses.
(b) `[TEST]` `gate3_grid.py`: Bob's `HVAC_thermal` vs the port on the same inputs (COP/share lookups given to both, so only the maths is compared). Max |difference|: total, heat pump, electric heater, AC, fan, fuel heat all **≤ 2·10⁻¹² W** (floating-point noise) in all five cases (HD1, HD2, HD3 with 5 kW caps, HD9, HD11). Bob's parts were separated without changing his code (switching one part off through its own arguments; method in the script header).

---

## 2. Part A: line-by-line audit of Appendix 1

### 2.1 `HVAC_thermal` (cell 11)

| Line (what it does) | VECTO stand-in | Verdict |
|---|---|---|
| `T_amb = np.asarray(...)` converts to array | – | OK. Lists, scalars, 2-D work (`test_A_*`). |
| `run1 = ssm_total_w(.., T_heat, ..)`, `run2 = (.., T_cool, ..)` | `TCalc` SR:26–45 | **DEVIATION (new)**: VECTO's upper set-point is `max(23, T_env − 3 K)` for **low-floor buses** (SR:40–44; `Constants.cs:99`). For high/semi-low floor it is 23 °C = Bob. Irrelevant for a truck cab; note only. |
| `losing_heat = (run1<0)&(run2<0)` | SC:763 | MATCH |
| `heating_demand = abs(max(run1,run2)) − waste_heat`, floored at 0 | SC:764–771 | MATCH. `waste_heat` comes from simulation in VECTO (Q5). |
| `climate_lookup(...)` | env-table by ID, SC:218, 184–189 | **DEVIATION (already flagged)**: by temperature, not by condition ID. Effect 0.1 % (section 6). |
| `fuel_heat = heating_demand * fuel_share` (not capped) | SC:220, 208–210: `min(FuelFiredHeaterPower, …)/fuel_eff` | **DEVIATION (new)**: VECTO caps at the heater kW and divides by efficiency 0.80 (the `fuel heater` column of `DefaultClimatic.aenv`). Bob's output is heat. No effect on electricity (`[TEST]` `part_f_effects.csv`). |
| `sum_heat = min(max_heating_power, demand·(hp+eh))` | SC:224 | MATCH |
| `rest = where(isclose(fuel,1),1,1−fuel)`, `scale = sum_heat/rest` | SC:225–231 | MATCH incl. `fuel_share = 1` (`IsEqual(0)`); shares not summing to 1 are **not checked** in either VECTO or Bob (`test_A_shares_not_summing_to_one_not_checked`: 200 % heat delivered). |
| `HP_el = where(hp_heat>0, hp_heat/cop_heat, 0)`; raises on NaN COP | SC:194–202 give **0 W silently** | **DEVIATION (already flagged, better than VECTO)**. |
| `EH_el = eh_heat/eh_eff` | SC:203–207 | MATCH. `eh_eff=0` → `inf` (no check; parser). |
| `gaining_heat = (run1>0)&(run2>0)&(T_amb ≥ T_cool_off)` | SC:343, 356 (`IsSmallerOrEqual(0)` has a tolerance; Bob uses exact `>0`) | MATCH (differs only within ~1 mW of zero). |
| `cooling_demand = min(run1,run2)`, capped | SC:360; 566–570 | MATCH |
| `AC_el = cooling/cop_cool` | SC:570 | MATCH. VECTO: COP NaN → 0 W (SC:567); Bob raises. `cop_cool=0` → `inf`. |
| `ventillation_status = ((T<T_off)&(run1>0)&(run2>0)) | ((run1>0)&(run2<0))` | SC:419–421 | MATCH |
| `fan_rate = where(losing_heat, vent_rate_heating, where(gaining_heat|vent_status, vent_rate, 0))`; `fan_el = V·rate·0.56` | SC:290–292, 394–397, 422–425; SI:85–89 | MATCH. Case `run1>0>run2` → idle ventilation at `vent_rate`. VECTO multiplies each fan term by `(1 − tech benefit)`; Bob has none. |
| `HVAC_el = HP+EH+AC+fan` | SC:553–578, 703–706 | MATCH (VECTO also sums over conditions with weights). |
| returns `(HVAC_el, fuel_heat)` | – | `fuel_heat` is dropped by `consumption_engine` (cell 16 does not take it): diesel use is not counted anywhere `[OPEN]`. |

### 2.2 `ssm_total_w` (cell 12)

| Line | VECTO | Verdict |
|---|---|---|
| `rho = p/(R·(T+273.15))` | – | Fresh-air only. Ideal gas; `p=101325`, `R=287.05` (ISO 2533:1975 gives 287.05287, `[STD, summary only]`). |
| `q_wall = (T_amb−T_calc)·A·U` | SR:56–57 | MATCH |
| `q_people = N·where(T<T_boundary, 50, 80)` | SR:58–59, SI:58–64, CO:96–97 | MATCH |
| `q_solar = solar·A_window·g·clouding·solar_factor` | SR:60–61, CO:94–95, 114 | MATCH; `solar_factor=0.25` equals the **literal `0.25` in SR:61** (see Q1). |
| `q_freshair = rho·cp·Q/3600·(T_amb−T_calc)` | none | **DEVIATION (already flagged)**. `Q/3600` is a hidden unit conversion (m³/h → m³/s) and violates rule 7: the parser should pass `Q` in m³/s (engine would then drop `/3600`). `[SIMPLIFICATION]` humidity ignored. |

### 2.3 `climate_lookup` (cell 13)

`np.interp` for COPs: MATCH at VECTO's points, interpolation elsewhere is HDEV's own `[SIMPLIFICATION]` (VECTO has no value between conditions). Holds end values outside the grid, so below −20 °C and above 33 °C the end COP is used (VECTO never evaluates outside its 11 points). Nearest-point shares: ties go to the colder point `[TEST]` `test_B4_*`. 2-D input works. **Contract problem:** NaN anywhere in a COP array spreads over the whole neighbouring segment (finding 2).

### 2.4 Every hard-coded number and default argument

| Value | Where | Class | Source |
|---|---|---|---|
| `273.15` | cell 12 | unit definition (°C→K) | – (rule 7: should be in parser or a named constant) |
| `3600` | cell 12 | unit conversion | – (rule 7 issue, above) |
| `eh_eff=0.93` | cell 11 | VECTO constant | `DefaultClimatic.aenv` columns "…electric heater" (0.93) `[VECTO]` |
| `spec_vent_power=0.56` Wh/m³ | cell 11 | VECTO constant | CO:111–112; `SSMDefaults.AHSM` `[VECTO]` |
| `heat_per_person=(50,80)` W | cell 11 | VECTO constant | CO:96–97 |
| `clouding=(0.65,0.8)` | cell 11 | VECTO constant | CO:94–95 |
| `T_boundary=17` | cell 11 | VECTO constant | CO:93 (the old HTML help says 12 °C; the code and manual formula say 17) |
| `g=0.95` | cell 11 | VECTO constant | CO:114; `SSMDefaults.AHSM` `BC_GFactor` |
| `solar_factor=0.25` | cell 11 | VECTO literal | SR:61; original Excel SSHVAC_V07 `INPUT & RESULTS SHEET!L89` |
| `T_heat=18, T_cool=23` | cell 11 | VECTO constant (bus boundary temperatures) | CO:102–103 |
| `T_cool_off=17` | cell 11 | VECTO constant | SI:77 |
| `p=101325, R=287.05, cp=1005` | cell 11 | standard-atmosphere values (HDEV choice for cp) | ISO 2533 `[STD, summary only]`; cp 1005 `[ASSUMPTION]` (no source read; textbook value for dry air) |
| `waste_heat=0` | cell 11 | HDEV choice | conservative (Q5) |
| `Q=0` | cell 11 | HDEV choice | `Q=0` = VECTO |
| `isclose(fuel_share,1.0)` | cell 11 | tolerance | VECTO `IsEqual(0)` (SC:225) |

**Units** (all SI except where noted): `T_amb` °C; `solar` W/m²; `A_surface`, `A_window` m²; `U` W/(m²K); `cab_volume` m³; `vent_rate` 1/h (**not SI**: rule 7 says 1/s; VECTO stores 1/s internally via `20.SI(Unit.SI.Per.Hour)`, CO:105–107); `spec_vent_power` Wh/m³ (**not SI**, J/m³ = ×3600); `Q` m³/h (**not SI**); powers W. The comment `m³ × 1/h × Wh/m³ = W` shows the three non-SI units cancel by luck of arithmetic; the parser should convert all three to SI and the engine drop the implicit factors.

Robustness results are in section 3 (tests).

---

## 3. Part B: tests (`tests/hvac/test_hvac_B.py`, `pytest tests/hvac -q` → 24 passed)

| Test | Result |
|---|---|
| B1 `Q=0` equals port (781 pts × 5 cases) and VECTO unit tests | pass |
| B2 cold/dark = heating only; hot/sunny = cooling only; between = fan only; `run1≥run2`; modes cover every hour | pass |
| B3 `HVAC_el` non-decreasing as T falls below 17 °C (4 combinations) | pass |
| B3 documented jumps | see table below |
| B4 `climate_lookup` = `np.interp`; ties → colder; 1-D and 2-D | pass |
| B5 caps keep heat-pump : electric-heater ratio; fuel heat not capped; cooling cap | pass |
| B6 fresh air = ρ·cp·Q/3600·ΔT by hand (−10 °C, Q=100: −1048.5 W) | pass |
| B7 hourly array indexed like `T_amb_h` (`hour=(t_start+T)//3600`); scalar works; array too short → `IndexError` (loud); `P_aux` default 1.25 inflates | pass |
| A robustness: scalar solar + array T; 2-D; per-hour `U`; `U=0`; `A_window=0`; `max_heating=inf`; waste heat ≫ demand → fan only; `cop=0` → `inf`; NaN cap → NaN | characterised |

**Jumps** (`part_b_jumps.csv`, placeholder cab, R-744 + electric heater, 0.01 K grid, as T falls):

| At | Size | Cause |
|---|---|---|
| −12.5 °C | **+429 W (Q=0, 300 W/m²)**, +800 W (Q=100, dark) | nearest-point share switch from the −5 °C row (heat pump 100 %) to the −20 °C row (50 % electric heater) |
| 17.0 °C (with sun) | **−107 W (Q=0, 800 W/m²)**, −54 W (Q=100) | AC switches off below 17 °C (and persons 80 → 50 W, clouding 0.8 → 0.65) |
| ~13 °C and ~8 °C (800 W/m²) | ±25.5 W | cab flips between fan-only and nothing as `run2` changes sign |

All three are VECTO's own switches (`[VECTO]` SC:343, 419–421; CO:93) except the first, which is HDEV's nearest-point rule (VECTO has a share per *condition*, not per temperature). A linear interpolation of the shares would remove the 429 W step; effect on annual energy +0.13 % (section 6).

---

## 4. Part A answers Q1–Q13

**Q1 Heat balance.** `[VECTO]` SR:48–64: `Q_wall + persons + solar`, formulas in section 2. Constants: CO:93–97, 114 (50/80 W, 0.65/0.8, 17 °C, 0.95). **0.25**: literal in SR:61, also literal in the original Excel (`SSHVAC_V07_final.xlsm`, `INPUT & RESULTS SHEET!L89: =C47*D9*C17*C18*0.25`, same in L90), no cell comment, not in the Version Log (read all 8 version entries), not in the VECTO manual page (`Documentation/User Manual/3-simulation-models/BusAuxiliaries.md`, formula only), not in `AA_HVAC.html`. **`NO SOURCE`** for its meaning. `[ASSUMPTION]` (my reading, not a fact): a geometric factor from window area to sun-lit projected area; nothing in the repo supports it. Not read: TU Graz bus aux reports and the Commission bus study (`Bob to fetch`).
Verdict: MATCH; the factor is `DEVIATION-free but unexplained`.

**Q2 Solar input.** `[VECTO]` the SSM takes `Solar` in W/m² (`WattPerSquareMeter`, `EnvironmentalConditionMapEntry.cs:63`) from `DefaultClimatic.aenv` column `Solar` (10–200 W/m², mean weighted ≈ 90 W/m² `[CALC]`) and a default 400 W/m² (CO:117). Whether it is horizontal, window-plane or direct is **not stated anywhere I could read** `[OPEN]`. The values (max 200) are far below clear-sky global radiation, so they look like a **time-and-orientation average on the window**, not an hourly global-horizontal reading. DMI `radia_glob_past1h` is mean global horizontal radiation over the past hour in W/m² `[SOURCE, DMI parameter name + API values read; definition page not opened]`; 2025 maximum 909 W/m², mean 123 W/m² `[CALC]`. So they are **not the same quantity**: feeding DMI global radiation straight into `solar·A_window·g·clouding·0.25` probably over-states window gain on vertical glass in winter (low sun) and is the reason the solar term matters little (section 5: −4 % of annual energy; ignoring it is conservative). Conversion to a window-plane value needs sun position and orientation (not worth it; at most 4 % of energy).

**Q3 Environmental conditions.** `[VECTO]` `Resources/Declaration/Buses/DefaultClimatic.aenv` (copy in `vecto_data/`): 11 rows (ID, T, solar, weight): (−20, 10, 0.0053) (−5, 30, 0.0826) (2, 30, 0.0826) (8, 20, 0.1661) (8, 155, 0.0826) (14, 30, 0.0826) (14, 175, 0.1243) (20.5, 30, 0.1243) (20.5, 200, 0.1243) (26, 150, 0.0826) (33, 150, 0.0427); weights are normalised by their sum (`EnvironmentalContidionsMapReader.cs:88–91`; raw sum 1.0). Rows 1–7 are `h`eating, 8–11 `c`ooling; all rows are used for both. VECTO sums per-condition electric W × weight (SC:101–123, 553–578). Per-point maths is identical to Bob's `[TEST]`: `part_c_points.csv` shows diff 0 W at every point and 5.7·10⁻¹⁴ W weighted. Weighted result: **193.39 W** (placeholder cab, R-744 + heater, caps 5 kW, vent 7/h, Q=0), **267.16 W** (VECTO driver-compartment analogue, bus values). Against the VECTO bus result: VECTO's published bus numbers are for whole buses (e.g. 295.39 W ventilation-only for the test bus, CFG1, `SSMTestHeatingCooling.cs:238`), not for a cab; there is no VECTO number for the same inputs except via the port, which equals Bob. `[OPEN]` a real VECTO run on a cab-sized bus would close it (section 12).

**Q4 Decision logic.** `[VECTO]` SC:272–296 (heating ventilation if `run1<0 && run2<0`), SC:337–374 (cooling if `T ≥ 17` and both `>0`), SC:376–398 (ventilation during AC), SC:400–427 (`T<17 && both>0` or `run1>0 && run2<0` → idle ventilation). Confirmed identical to Bob's `losing_heat`, `gaining_heat`, `ventillation_status`, `fan_rate`. Case `run1>0>run2` (between set-points) → idle ventilation at `vent_rate`, no heating or cooling: MATCH. `T_cool_off` = SI:77 constant 17 °C. The three switches are `true` (above).

**Q5 Waste heat.** `[VECTO]` `Models/BusAuxiliaries/DownstreamModules/Impl/M14Impl.cs:51–63`: usable waste heat = ICE heat × 0.2 × 0.75 + **electric-motor waste heat × 0.9 × 0.75** (CO:196–200); average over the cycle from simulation, subtracted from heating demand (SC:769). So for a BEV VECTO **does credit motor losses**. Bob's `waste_heat=0` is conservative. With the E2 `.vmod` mean `P_E2-em_loss` (12.0 kW, Regional) the formula gives **8.1 kW** usable `[CALC]` (`part_e_waste_heat.csv`), which would remove nearly all cab heating while driving (annual kWh 678 → 107, `part_d_sensitivity.csv`). Not a recommendation: that credit is large, depends on a coolant path to the cab heater that the user may not have, and needs the battery/motor model (out of scope). Showing it is the point: **0 is the conservative end.**

**Q6 Heating split and caps.** `[VECTO]` the case is chosen from (heat-pump type, any electric heater, fuel heater > 0 kW) by `HeatingDistributionCasesMap.GetHeatingDistributionCase` (`…HVAC/HeatingDistributionCasesMap.cs:77–86`) → HD1…HD12 (`HeatingDistributionCases.csv`); the share is looked up by **(case, condition ID)** (`HeatingDistributionMap.cs:17–24`), no interpolation, no nearest-point: each of the 11 conditions has its own row. Example HD3 (R-744 + electric heater + fuel heater): ID1 40/20/40 %, ID2 70/0/30, ID3 80/0/20, IDs 4–11 100/0/0 (heat pump/electric/fuel). Cap: SC:224 `min(maxHeatingPower, hp+eh)` with `maxHeatingPower = MaxHeatingPower × compartment fraction` (SC:179, 181); fuel heater: `min(FuelFiredHeaterPower, heat)/eff` (SC:208–210). Bob's `rest`/`scale` = SC:225–232 **MATCH**, including `fuel_share = 1`. Shares not summing to 1: not checked in either.

**Q7 COP.** `[VECTO]` COP = table value per condition per technology in `DefaultClimatic.aenv` (R-744, non-R-744 2-/3-/4-stage, continuous), same table for heating and cooling rows, **no interpolation**. Missing cell `-` → key absent (`EnvironmentalContidionsMapReader.cs:66–70`) → `double.NaN` (SC:184–185) → heat pump contributes **0 W silently** (SC:194–197); cooling the same (SC:567–568). **Confirmed.** Only the −20 °C row has missing cells (all non-R-744 columns). For **BEV**: VECTO accepts only R-744 and non-R-744 *continuous* heat pumps (mechanical 2/3/4-stage are rejected, `SpecificCompletedBusAuxiliaryDataAdapter.cs`, `DoHVACInputSanityChecks`; `IsElectrical` = R-744 or continuous, `VectoCommon/…/ISSMDeclarationInputs.cs:323–326`). The parser's flat clip at −5 °C (COP 1.78 for continuous): where VECTO says 0 W, the clip gives heat; against physical reality (COP falls towards 1 as it gets colder) it is **optimistic**. Size in Copenhagen 2025 (min −11.4 °C, 61 h below −5 °C): clip vs COP floor 1.0 differ by **0.2 W mean (0.1 %)** (`part_c_deviations.csv` step (e)). Larger in a Nordic year; the COP below −5 °C needs measured data (`NOT FOUND`, section 7). The conservative choice is the lower COP.

**Q8 Electric heater and fan constants.** `eh_eff=0.93`: aenv columns water/air/other electric heater `[VECTO]`; underlying physical basis `NO SOURCE`. `0.56 Wh/m³`: CO:111–112; basis `NO SOURCE`. Ventilation rates `[VECTO]` DD:451–474: configurations 1–2: 7 /h; configurations 3–10: 20 /h (10 /h while heating). `.AHSM` engineering defaults: 20 / 7. For a truck cab the VECTO analogue is the **driver compartment**; its configuration is 2 (driver AC only) → **7 /h** for both. That is what I used for the placeholder runs (a `Choice`).

**Q9 Fresh air vs ventilation.** `[VECTO]` the ventilation rate only sets **fan power** (SI:85–89). It never enters the heat balance: VECTO has no outside-air heating or cooling load. So HDEV's `q_freshair` double-counts **nothing in VECTO**; it adds a physical load VECTO omits. `Q` (outside air) and `V·rate` (air moved by the fan, possibly recirculated) are different quantities; if the fan moves the fresh air then `V·rate ≥ Q`. With the placeholders `V·rate = 45.5 m³/h < Q = 100 m³/h` `[CALC]`: inconsistent. Link proposed in section 9 (change 5).

**Q10 Driver vs passenger compartment.** `[VECTO]` the SSM splits the bus into a driver compartment (length 1.2 m, `Constants.cs:207`) and a passenger compartment; each has its own heat pump type, maximum heating/cooling power (`HVACHeatingPowerDriver.csv`, `HVACCoolingPowerDriver.csv`: **0–5 kW heating (5 kW in most configurations, 3.5 kW in configuration 6) and 0–5 kW cooling (4 kW for coaches)** per configuration) and share of the load by length (SI:217–223). The right analogue for a truck cab is the **driver compartment**. HDEV mixes: the placeholder `A_surface`, window and U are cab-like, but VECTO's U (3.0/3.5/4.0 W/m²K by floor type, DD:553–564) and constants are **bus** values; VECTO's bus counts the driver as +1 person.

**Q11 Technology benefits.** `[VECTO]` `TechnologyBenefits.cs`, `SSMTechList.csv`: double glazing (4 % on heating, cooling and ventilation, all floor types), separate air distribution ducts (4 % cooling power and cooling ventilation), adjustable auxiliary heater (2 % heating, ventilation), adjustable coolant thermostat (2 %), engine waste gas heat exchanger (4 % low floor only), heat pump system line is commented out. Maximum total benefit 0.5 (CO:100; the `.AHSM` file says 0.03). For a cab only **double glazing** is plausible as a yes/no. Effect would be ≤ 4 % of the load; no truck-cab source for this value `NO SOURCE`.

**Q12 Lorry table.** `[VECTO]` `Resources/Declaration/VAUX/HVAC-Table.csv` (copy `vecto_data/VAUX_HVAC-Table.csv`): column "HDV Group", rows 1s…16, 51…56; values W **mechanical** (e.g. group 2: Long haul 200, Regional 200, Urban 150), `HeavyLorryAuxiliaryDataAdapter.cs:157–174`: `PowerDemandElectric = mech × 1/0.8` (`DD:126`). E2 `.vmod` `P_aux_AC_el`: Regional 250 W, LongHaul 250 W, Urban 187.5 W `[TEST]` (read from the files). Source of the table values not stated in the repo `NO SOURCE`. HDEV thermal gives the same watts as the table at (placeholder cab, R-744 + heater, night): Q=0: **5.8 °C or 29.6 °C** for 250 W and **8.2 °C or 27.5 °C** for 187.5 W; Q=100: 9.6 / 27.7 °C and 11.4 / 26.2 °C; with 500 W/m² sun the cold crossing moves 4 K colder (`[CALC]`, scan in the session; the equivalent solves are `part_f_effects.csv`: Q=0 needs UA = 92 W/K for 250 W and 68 W/K for 187.5 W, or Q = 90 / 22 m³/h at UA = 60 W/K).

**Q13 Not in HDEV.** (list, size where known): low-floor upper set-point (irrelevant); technology benefits (≤ 4 %); mechanical heat pump/compressor path (not a BEV); fuel heater cap and efficiency 0.80 (fuel only); waste-heat credit (large, Q5); humidity and defogging (VECTO has none either; Ramesh Babu show fresh air for fogging rises the load, section 7); door openings, preconditioning, heater run-on, minimum compressor power: **none in VECTO** either; cold-start warm-up (VECTO is steady state).

---

## 5. Part C: reproduction and deviation register (`part_c_points.csv`, `part_c_deviations.csv`)

Placeholder cab = A 20 m², U 3.0, window 4 m², V 6.5 m³, N 2, R-744 + electric heater (HD2), caps 5 kW / 5 kW (VECTO driver-compartment values), vent 7 /h, Q as stated. "VECTO driver analogue" = BUS values: A 24.9 m², window 6.8 m², V 7.65 m³, U 3.0, N 1 (formulas in `hvac_common.py`, lines cited there: Constants.cs:207, DD:481–487, adapter 356–360). Annual figures: Copenhagen (DMI 06188) 2025, 2610 operating hours (ILLUSTRATIVE Mon–Fri 06–16 local).

| Step (vs "Bob hourly, Q=0") | Placeholder mean W / kWh·yr⁻¹ | Δ | Driver analogue W | Δ |
|---|---|---|---|---|
| Bob hourly, Q=0 | 167.9 / 438 | – | 239.9 | – |
| (a) + fresh air Q=100 | 259.8 / 678 | **+54.7 %** | 331.8 | +38.3 % |
| (b) VECTO 11-point weighted mean (not hourly) | 193.4 | +15.2 % | 267.2 | +11.3 % |
| (c) COP as step, not interp | 167.8 | −0.08 % | 239.8 | −0.07 % |
| (d) shares interpolated, not nearest | 168.1 | +0.13 % | 240.3 | +0.13 % |
| (e) non-R-744 HP only, clip 1.78 vs floor 1.0 at −20 °C | 176.9 vs 177.1 | +0.1 % | 253.1 vs 253.4 | +0.1 % |

**Deviation register** (E2 Regional/Urban use the same cab and weather; they differ only in the VECTO lorry value and the km):

| Deviation | Size on 2025 Danish year | Sentence for a client report |
|---|---|---|
| Bus SSM applied to a truck cab | cab values are placeholders; analogue +43 % vs placeholder at Q=0 | "Cab climate energy is estimated with the EU certification tool's bus heat-balance model applied to a truck cab; cab size and insulation are assumptions." |
| Hourly real weather instead of 11 conditions | −13 % (placeholders) / −10 % (analogue) vs VECTO weights | "Climate energy uses hourly measured temperature and sun for the chosen location instead of the certification tool's 11 fixed conditions." |
| COP interpolated, shares by nearest temperature | ±0.1 % | "Heat-pump efficiency is interpolated between the certification tool's tabulated temperatures." |
| COP clip below −5 °C | ≤ 0.1 % in 2025; larger in colder climates `[OPEN]` | "Below −5 °C the heat-pump efficiency is held at its −5 °C value, which may be optimistic." |
| Fresh air on (`Q`) | +55 % (Q=100) | "A fresh-air load (not in the certification tool) is added; this raises the estimate by roughly half." |
| Heating set-point 18 °C | 21 °C: +26 % (Q=0) / +28 % (Q=100); 22 °C: +35 % / +38 % | "The cab heating set-point is the certification tool's 18 °C; measured trucks are run at 21–22 °C, so winter energy may be understated." |
| 0.25 solar factor | solar term is −4 % of annual energy (reduces heating), 0.02 % per ±10 % | "A fixed factor from the certification tool reduces the effect of sunshine; its origin is undocumented." |
| Waste heat 0 | VECTO credits motor losses; Bob 0 is the conservative end | "No heat from motor/inverter losses is credited." |
| No technology benefits, no door openings/warm-up | ≤ 4 %; unknown | "Insulation options, door openings and cold starts are not modelled." |
| Fuel heater not capped / not /0.80 | no electric effect | – |

---

## 6. Part D: sensitivity (`part_d_sensitivity.csv`, `part_d_tornado.png`)

Base: placeholder cab, Q=100, 678 kWh/yr in operating hours. No sourced ranges exist for most inputs (`NO SOURCE`, bars skipped), so the continuous inputs are shown as **±10 % elasticities** (not ranges), and the discrete options have sources.

| Input | ±10 % → swing kWh/yr (% of base) |
|---|---|
| `cop_heat` | 115 (17.0 %) |
| `A_surface` = `U` (UA) | 83 (12.2 %) |
| `Q` | 49 (7.2 %) |
| `cab_volume` (fan) | 13 (2.0 %) |
| `cop_cool` | 8 (1.2 %) |
| `vent_rate` | 4 (0.6 %) |
| `A_window`, `g`, `solar_factor` | 0.1 (0.02 %) |
| `eh_eff`, `max_heating_power`, `max_cooling_power` | 0: not reached in 2025 (the electric heater only works at the −20 °C row; 5 kW caps never bind) |

| Option (source) | kWh/yr | Δ |
|---|---|---|
| U = 4.0 (VECTO low-floor bus, DD:557) | 817 | +20.5 % |
| U = 3.5 (VECTO semi-low, DD:559) | 747 | +10.2 % |
| no heat pump, electric heater only (VECTO HD9) | 1743 | **+157 %** |
| continuous heat pump, clip at −20 °C | 720 | +6.1 % |
| 1 person instead of 2 | 702 | +3.5 % |
| Q = 0 | 438 | −35 % |
| fan rates 20/10 /h (VECTO config 3–10) | 736 | +8.5 % |
| set-point 20/23 (ILLUSTRATIVE) | 803 | +18.5 % |
| waste heat 8.1 kW while driving (VECTO M14 formula) | 107 | −84 % |

**Top five and whether a fleet user can give them** (rule 11): (1) *heat pump yes/no* (+157 % without): **yes**, one tick; sourced default = VECTO share tables HD1/HD2/HD9. (2) *heat-pump COP curve* (±17 %): **no**; default = VECTO R-744 / continuous columns by temperature (`DefaultClimatic.aenv`); conservative end = lower COP; note R-744 vs continuous differ by ≈ 6 %. (3) *UA* (±12 %; U=3.5/4 → +10/+20 %): **no**; default: not found for EU truck cabs (`BLOCKED`); derive from cab type once geometry is sourced; conservative end = higher UA. (4) *Q* (±7 %; 0 → −35 %): **no**; default: Bob's 100 m³/h (the number is from Dvorak 2025, seen only as a search snippet, `[SOURCE, snippet]`, so **not usable as a model input until the full text is read**). (5) *set-point* (+26…38 %): **yes** but users will not know; defaults 21–22 °C from the two sources vs VECTO 18 °C; conservative end = higher.

---

## 7. Part E: HDEV thermal vs VECTO's constant table (`part_e_annual.csv`, `part_e_monthly.csv`, `part_e_weeks.csv`, `part_e_monthly.png`)

Same cab and weather for all missions; the VECTO lorry value depends on the mission (E2 `.vmod` `P_aux_AC_el`). Drive assumed the whole 10-h shift at the mission's average speed (ILLUSTRATIVE). Share of trip energy uses Chain S V1 from Gate 1 (LongHaul has none). Cab values "(iii) best sourced" are **BLOCKED** (no sourced truck-cab geometry/UA found); the bus driver-compartment analogue is shown instead and labelled BUS.

| Mission | Source | kWh/yr (op. h) | mean W | kWh/100 km | % of trip energy |
|---|---|---|---|---|---|
| Regional | (i) VECTO table | 652.5 | 250 | 0.41 | 0.42 |
| Regional | (ii) HDEV placeholders Q=0 | 438.2 | 167.9 | 0.27 | 0.28 |
| Regional | (ii) HDEV placeholders Q=100 | 678.0 | 259.8 | 0.42 | 0.44 |
| Regional | (iii-bus) driver analogue Q=0 / Q=100 | 626.2 / 866.1 | 239.9 / 331.8 | 0.39 / 0.54 | 0.40 / 0.56 |
| Urban | (i) VECTO table | 489.4 | 187.5 | 0.70 | 0.83 |
| Urban | (ii) placeholders Q=0 / Q=100 | 438.2 / 678.0 | 167.9 / 259.8 | 0.63 / 0.97 | 0.74 / 1.14 |
| Urban | (iii-bus) Q=0 / Q=100 | 626.2 / 866.1 | 239.9 / 331.8 | 0.90 / 1.24 | 1.06 / 1.46 |
| LongHaul | (i) VECTO table | 652.5 | 250 | 0.31 | n/a |
| LongHaul | (ii) placeholders Q=100 | 678.0 | 259.8 | 0.33 | n/a |

The E2 cab is the same truck in all three missions (same `.vsum` configuration), so no separate LongHaul cab is needed. Annual HVAC is **0.3–1.5 % of trip energy** in every variant `[CALC]`, so on kWh/km the cab climate is small compared with traction; it is large in cold weather in absolute terms. **Coldest week (ISO 7, mean 0.1 °C):** VECTO 250 W flat = 12.5 kWh/week; HDEV 415 W (Q=0) / 689 W (Q=100) = 20.8 / 34.5 kWh; analogue 593 / 867 W. **Hottest week (ISO 33, 20.4 °C):** HDEV 138 / 140 W = 6.9 / 7.0 kWh, i.e. **below** VECTO's constant. So HDEV thermal is lower than the flat table in summer and higher in winter; the **conservative result** for a winter-heavy fleet is the one with Q=100 (and a set-point of 21–22 °C). Monthly values in `part_e_monthly.csv`.

---

## 8. Part F: physics beyond VECTO (research + measured effect)

Effects use no invented numbers: they are equivalence solves, per-unit factors, or counts from VECTO files (`part_f_effects.csv`). Source depth is limited: only the documents named below were opened in full; everything else is in section 14.

| # | Topic | What I found | Size / effect | Hourly-structure compatible? | Conservative? |
|---|---|---|---|---|---|
| 1 | Driving vs parked UA | `[SOURCE, full text, simulated]` Ramesh Babu 2025 Table 4 (−10 °C): heater rate 3.87 → 4.25 kW CFD (+9.8 %), 4.07 → 4.45 kW 0D (+9.3 %) from 0 to 90 km/h. FASTSim uses a flat-plate Nusselt correlation for moving vehicles and a fixed stop value (`fastsim-core/src/vehicle/cabin.rs:225–300`, threshold 2 mph). NREL's measured UA (51/65 W/K) **not re-verified**: the absolute baseline UA is in a figure, tables 1–3 of NREL/SAE 2016 give only % reductions (read p.457). | per +10 % UA: +15 W (+9 %) | yes: `U` already accepts a per-hour array; parser passes parked/driving by hour. Needs mean speed per hour. | higher UA = conservative |
| 2 | Cold-start warm-up | formula only: per start `C_cab · ΔT`; mean ΔT over cold operating hours 9.1 K → **0.0025 kWh per start per kJ/K**. C_cab: `NO SOURCE`. Stops: Regional 11 / 1.63 h, Urban 104 / 3.75 h, LongHaul 4 (VECTO `.vmod`). | unknown until C_cab sourced | yes: energy per start at departure rows | – |
| 3 | Preconditioning on charger | not researched (no source opened). | – | – | – |
| 4 | Door openings | no measured truck-cab value found (PR #20 also `NOT FOUND`). Formula: 0.0027 kWh per m³ exchanged at 9 K; Urban cycle has 104 stops. | per-m³ unit only | yes | – |
| 5 | Humidity / demisting | `[SOURCE, full text]` Ramesh Babu 2025: at −10 and −20 °C the heating load rises with two occupants and 90 % RH because more fresh air is needed against fogging and 1000 ppm CO₂ (Sec. 5.3, Fig. 23). Ignoring humidity is therefore **non-conservative**. | not quantified in text read | yes (factor on Q) | no |
| 6 | Fresh air per person | `[SOURCE, snippet only]` Dvorak 2025: ~100 m³/h for two persons at 1000 ppm (MDPI page returned 403; full text not opened). EN 16798-1 / ASHRAE 62.1 not opened. | Q=100 → +240 kWh/yr | yes | higher Q conservative |
| 7 | Solar | solar term is a **4 % reduction** of annual energy (S=0 gives +4 %); ignoring sun is conservative. Sol-air method (ASHRAE Fundamentals) not opened. | ≤ 4 % | yes | ignoring sun = conservative |
| 8 | COP vs ambient, measured | not found in text read. Ramesh Babu 2025 gives auxiliary power rising 1.8 kW → 9 kW from 10 °C to −20 °C (sim., whole truck). SAE J2765, EN 14511 not opened. | – | – | – |
| 9 | Battery/motor conditioning (report only) | Ramesh Babu 2025 (sim.): "battery heating below 0 °C is the second largest auxiliary load" (Sec 5.1); Daimler press 25 Feb 2025 (read in full): at −2 °C average, +25 % consumption vs class-A-tyre run, of which **5 points** cab climate at 21 °C, **< 1 point** battery heating; VECTO `Cond` flat 550–600 W (`.vmod` `P_aux_COND_el`). Same hourly `T_amb` can drive it. Dollinger & Fischerauer 2021, Stanford drayage, Öko-Institut ELV-LIVE: not opened. | – | yes (same weather array) | – |

---

## 9. Proposed changes: before / after, effect, engine or parser

None is applied to the notebook. Variants live in `reference_copy.py`; patches printed by `python reference_copy.py`.

**1. Parser: validate and fill (engine unchanged)** — before: `T_amb`, `solar` NaN → 0 W; COP grid NaN → ValueError over a whole segment. After: parser fills weather gaps (DMI example: linear in time, 58 T-hours, 32 S-hours of 8760 filled, `hvac_common.load_weather`), fills the COP grid before the call (flat clip, or lower value), checks `cop>0`, `eh_eff>0`, `T_cool ≥ T_heat`, shares in [0,1] with sum ≤ 1, `max_*_power` finite, ascending points. Tag `[TEST]`. Not an assumption swap.

**2. Parser: `HVAC_eff=1.0`** in `P_aux(...)` for thermal mode (VECTO's 1/0.8 factor, `DD:126`, applies to the lorry table, not to a thermal model). Effect: omitting it adds 25 % (678 → 847 kWh/yr).

**3. Heating set-point (Kiro's recommendation)**: keep VECTO's 18 °C as the audited reference value but add 21 °C as a standard sensitivity in client reports. Evidence: Daimler press (21 °C day, 19 °C night, `[SOURCE, full page read]`), Ramesh Babu (22 °C target, `[SOURCE, full text]`). Effect: +112 kWh/yr (Q=0), +192 kWh/yr (Q=100). Bob decided to keep 18 °C (decision 4); this is evidence, not a reopening.

**4. Cab geometry/UA by cab type**: before: placeholders; after: lookup. **BLOCKED** until a sourced table exists. Method with a source: box surface `2(L·W + L·H + W·H)`, `V = L·W·H` (VECTO manual `BusAuxiliaries.md` and Excel cell `C8`), window = window height × length + front/rear area (adapter lines 356–360); inputs L, W, H per cab type: `NO SOURCE`.

**5. Fan–Q link (engine, one line, optional)**
```python
# before (cell 11, step 5)
fan_el = cab_volume * fan_rate * spec_vent_power
# after (Kiro's suggestion; units must be SI after the parser change)
fan_flow = np.maximum(cab_volume * fan_rate, Q)        # m³/h here, 1/s·m³ in SI
fan_el   = fan_flow * spec_vent_power
```
Effect with Q=100 and V=6.5 m³, 7 /h: fan 25.5 W → 56 W in every hour where the fan runs (+30 W, `[CALC]`; small against 260 W mean). Swaps nothing: removes an inconsistency; but the 0.56 Wh/m³ is a bus figure `[VECTO]`.

**6. Fuel power (engine, optional)** `v_fuel_eff`:
```python
# before
return HVAC_el, fuel_heat
# after
return HVAC_el, np.minimum(fuel_heat, fuel_heater_power) / fuel_eff
```
Electricity unchanged (`[TEST]` max change 0 W). Fuel 138 kWh/yr vs 111 kWh heat for HD3 shares. Needs `fuel_heater_power` (kW from OEM sheet) and `fuel_eff` 0.80 `[VECTO]`.

**Not proposed (would swap one assumption for another):** changing 0.25, 7 /h, 0.56, g, clouding or the people loads without a source.

---

## 10. Input table for the UI

| Input | Unit | Fleet user can give? | Sourced default | Conservative end | Derived from |
|---|---|---|---|---|---|
| `T_amb`, `solar` hourly | °C, W/m² | place, not the series | DMI 06188 (DK); ERA5/national met services elsewhere (not checked) | – | location |
| `A_surface`, `cab_volume`, `A_window` | m², m³, m² | no | **BLOCKED**; method in change 4 | larger | cab type (needs table) |
| `U` / UA | W/m²K | no | VECTO bus 3.0/3.5/4.0 (**bus**); NREL UA `not verified` | higher | cab type |
| `N_persons` | – | yes | 1 or 2 | more persons lowers heating, raises cooling | user |
| `T_heat`, `T_cool`, `T_cool_off` | °C | no | 18 / 23 / 17 `[VECTO]`; 21–22 observed | higher heating set-point | – |
| heat-pump present, type | – | **yes (tick)** | HD1/HD2/HD9 `[VECTO]` | no heat pump | OEM sheet |
| COP curves | – | no | `DefaultClimatic.aenv` (R-744, continuous) | lower COP | HP type |
| `max_heating_power`, `max_cooling_power` | W | partly | 5 kW / 5 kW (VECTO driver compartment, **bus**) | lower cap | OEM sheet |
| `eh_eff` | – | no | 0.93 `[VECTO]` | – | – |
| `vent_rate`, `vent_rate_heating` | 1/h (SI: 1/s) | no | 7 / 7 (VECTO config 2, bus) | higher | – |
| `spec_vent_power` | Wh/m³ (SI: J/m³) | no | 0.56 `[VECTO]` | – | – |
| `Q` | m³/h (SI: m³/s) | no | Bob's 100; **source not usable yet** | higher | N_persons |
| `heat_per_person`, `clouding`, `T_boundary`, `g`, `solar_factor` | W, –, °C, –, – | no | VECTO constants | – | – |
| `waste_heat` | W | no | 0 | 0 | – |
| `p`, `R`, `cp` | Pa, J/kgK, J/kgK | no | 101325 / 287.05 / 1005 | – | – |

---

## 11. Parser jobs found

Fill gaps in `T_amb`, `solar` (finding 1) and COP grids (finding 2); check `cop>0`, `eh_eff>0`, shares, caps finite, `T_cool ≥ T_heat`, ascending points, `Q ≥ 0`; convert `vent_rate` (1/h→1/s), `spec_vent_power` (Wh/m³→J/m³), `Q` (m³/h→m³/s); pass `HVAC_eff=1.0`; DMI convention (stamp = end of hour; `hour_start = stamp − 1 h`, UTC → local for schedules); build the heating-distribution case (HD1…HD12) from (heat pump type, electric heater y/n, fuel heater y/n) and take per-row shares; reject mechanical heat pumps for a BEV (VECTO does); decide hour-0 alignment of `HVAC` and `T_amb_h` (`hour=(t_start+T)//3600`); a cache key for the hourly result (below).

**Performance (Part K, `part_k_timing.csv`)**: Intel Xeon Platinum 8488C, Python 3.11.15, numpy 2.4.6, mean of 5: 24 h **0.115 ms**; 8760 h **0.76 ms**; 365 × 24 2-D **0.69 ms**. 1000 different cabs × a year ≈ 0.8 s uncached. No transient variant was built, so no cost to report. Cache the hourly vector by key (weather series id/hash, all cab and system inputs, set-points, `Q`); trivially cheap, so caching is optional.

---

## 12. Part J: VECTO runs for Bob

No run is **needed** to close any question here (the port equals VECTO's own test results). Optional: a completed-bus declaration run with a 1.2 m driver-only bus would give VECTO's own per-condition SSM output to compare with the analogue (`Q3`); I did not write job files because the declaration output does not list per-condition values `[OPEN, not checked]`.

---

## 13. Part H: other tools

| Tool | Read | Heat balance / cabin | COP | Solar | Difference from HDEV |
|---|---|---|---|---|---|
| VECTO SSM | code + manual + original Excel | steady, fixed conditions, formulas above | table per condition | window term with 0.25 | HDEV = same maths hourly |
| FASTSim 3 (`mohgsaad-art/fastsim`, branch `fastsim-3`, commit `6a07d4d`) | code read: `cabin.rs` 160–300, `hvac_sys_for_lumped_cabin.rs` 10–62, 103–270 | **transient lumped cabin** with a controller around `te_set`, dead-band; moving: flat-plate forced convection (Incropera 7.30/7.38) in series with a shell coefficient; stopped: separate coefficient; threshold 2 mph | **fraction of Carnot**, default `frac_of_ideal_cop = 0.15`, ideal-COP floor when ΔT < 5 K | **none** (`cabin.rs:2` "TODO: add … solar heat load") | per-row/second model, car-specific fitted values; speed-dependent heat loss (which HDEV lacks); no fresh-air term seen |
| eflips-depot, spice_ev, dt-cargo, acnportal, blast-lite | file-name search only (no HVAC/cabin/climate file names found; blast-lite has only a climate data `.mat`) | not read | – | – | no HVAC model found; **not code-read** `[OPEN]` |
| TU Graz PHEM, Autonomie, EPA GEM, SUMO, TUM/KIT/Chalmers tools | **not opened** | – | – | – | `Bob to fetch` |

Effect on HDEV numbers: a Carnot-fraction COP of 0.15 would give COP ≈ 0.15 × 268/28 = 1.4 at −5 °C vs VECTO's 2.04: **not applied** (car-specific fit, not a standard).

---

## 14. Parts G and I: data sources and independent validation

### 14.1 What was read in full

| Source | Type | Read | Facts |
|---|---|---|---|
| Ramesh Babu, Sebben, Chroneer et al. 2025, *Thermal Sci. Eng. Progress* 60, 103417, `research.chalmers.se/publication/545506` | simulated CFD + 0D, electric truck (Volvo), 17 pages | **full text** | Table 4 (p.9) heater rate −10 °C: CFD 3.87/4.15/4.21/4.25 kW, 0D 4.07/4.32/4.39/4.45 kW at 0/30/60/90 km/h; auxiliary mean 1.8 kW (10 °C) → 9 kW (−20 °C); cabin heating largest aux load; target 22 °C; 10 kW battery heater; fresh air against fogging and CO₂ ≤ 1000 ppm |
| Daimler Truck press release, eActros 600 winter tour, 25 Feb 2025 | OEM press text | full page | at −2 °C average: +25 % consumption vs class-A-tyre run; 5 points cab climate at 21 °C; < 1 point battery heating; day 21 °C / night 19 °C; hoteling reduces range by 2–5 % |
| Lustbader et al. 2016, SAE Int. J. Passeng. Cars Mech. Syst. 9(2), NREL `docs.nlr.gov/docs/fy16osti/66860.pdf` | measured, Volvo cab bucks | full text (6 p.) | UA method (Eq.1); only **% reductions** in Tables 1–3 (20.6 %, 43 %, 53.3 %); baseline absolute UA only in Fig.5 |
| NREL CoolCalc, `docs.nlr.gov/docs/fy14osti/52452.pdf` | tool paper | text extracted; no W/K values | – |

### 14.2 `HDEV vs the two datasets` (`part_i_comparison.csv`, **not like-for-like**: the vehicles' own cab data are missing → placeholders `BLOCKED`)

| Item | Value |
|---|---|
| Ramesh Babu 0D heater rate, −10 °C, 22 °C target | 4.07 (standstill) – 4.45 kW (90 km/h) |
| `[CALC]` implied total conductance = rate / 32 K | 127 – 139 W/K (placeholder: UA 60 W/K + 37 W/K at Q=100) |
| HDEV heat demand −10 °C, set-point 22 °C, placeholders Q=0 / 100 | 1.82 / 3.02 kW (−55 % / −26 % vs 4.07 kW) |
| same, VECTO driver analogue (bus) Q=0 / 100 | 2.58 / 3.78 kW (−37 % / −7 %) |
| HDEV electric at −2 °C, night, placeholders Q=0 / 100 | 0.52 / 0.84 kW |
| Daimler: 5 points × E2 0.9749 kWh/km × 61.2 km/h | ≈ 3.0 kW (order of magnitude; other truck) |

The earlier lead "HDEV ≈ 3.1 kW vs Chalmers 4.15–4.45 kW at −10 °C" is **reproduced in magnitude**: HDEV heat demand with Q=100 and a 22 °C set-point is 3.0 kW (placeholder), 3.8 kW (bus analogue). With the 18 °C set-point: 2.6 / 3.3 kW. HDEV is **low while driving**, and the speed effect (+9–10 %) is not in HDEV. The Chalmers table counts *heater rate* (thermal) and does not state occupants or fresh-air rate in the text I extracted for Table 4 (they are given in Sec. 5.3 for the later scenarios `[OPEN]`).

### 14.3 BLOCKED (no guessing) and Part G items

* G1 cab geometry by cab type (Mercedes, Volvo, Scania, DAF, MAN, Renault dimension sheets): **not searched**; BLOCKED.
* G2 UA/U: NREL 51/65 W/K **not re-verified** (figure 5 of 66860 / earlier NREL reports); Dvorak 2025, Lustbader 2012 (`NREL/TP-5400-52452` is the CoolCalc paper above), OSTI 973699: not opened.
* G3 OEM spec sheets: **not searched**; BLOCKED.
* G4 weather: DMI works **without a key** (checked 12 Nov 2026); stations 06186 (Landbohøjskolen) and 06180 (Kastrup) have **no** `radia_glob_past1h`; the only active Copenhagen-area station with both parameters is **06188 Sjælsmark** (55.876 N, 12.412 E); 2025: 8730 of 8760 hourly rows, 28 temperature and 2 radiation values blank, 30 rows missing; hour stamps are end-of-hour (`past1h`); solar peak at hour-start 11 UTC in June, one hour later than the 10 UTC expected, so the end-of-hour convention is `[ASSUMPTION]`. Licence of DMI open data: not checked here `[OPEN]` (Bob to confirm CC BY 4.0). Other countries (ERA5, national services): not checked.
* G5 measured energy vs temperature (Öko-Institut ELV-LIVE, ICCT 2023, NREL Fleet DNA, Volvo/Scania, VTT): not opened.
* Part I other items (Dvorak rig, JRC133756, e-bus HVAC): not opened.

### 14.4 Bob to fetch

| Document | Link / DOI | Exactly what to extract |
|---|---|---|
| Dvorak et al. 2025, WEVJ 16:129 | https://www.mdpi.com/2032-6653/16/3/129 (403 from sandbox); preprint https://www.preprints.org/manuscript/202412.0068 | cab volume, heater/AC kW, UA or insulation values, fresh-air flow vs persons, measured heating power vs ambient temperature (table/figure) |
| Lustbader et al. 2016, SAE 2016-… (NREL 66860) | https://www.nlr.gov/docs/fy16osti/66860.pdf | **Figure 5** (page 4): baseline UA slope in W/K for the standard-curtain case; confirm or reject 51/65 W/K |
| Lustbader 2012 / NREL TP-5400-52452, OSTI 973699 | https://docs.nlr.gov/docs/fy14osti/52452.pdf, OSTI 973699 | cab surface area, volume, glazing area, UA in W/K |
| Ramesh Babu 2025 Sec. 5.3 / Fig. 23 | https://research.chalmers.se/publication/545506/file/545506_Fulltext.pdf | occupants, fresh-air flow and RH used for Table 4; heating load vs ambient (Fig. 21) |
| JRC133756 | JRC publications | heating at −7 °C vs cooling at 35 °C power |
| ISO 2533:1975, EN 16798-1, ASHRAE 62.1, ISO 7730, ISO 9050 | standards bodies | clause numbers for fresh-air per person, g-value definition |
| SAE J2765, EN 14511 | – | COP test conditions |
| Heat-pump COP below −5 °C | R-744 / R-1234yf / R-290 papers | measured COP vs ambient at −20…−5 °C |
| VECTO bus/SSM background reports | TU Graz, Commission bus study | meaning of the 0.25 factor; basis of 0.56 Wh/m³ and 0.93 |
| OEM sheets eActros 300/400/600, eEconic, Volvo FH/FM/FL Electric, Scania, DAF, MAN eTG, Renault E-Tech | OEM sites | heater kW, AC kW, heat pump yes/no, cab dimensions |
| Öko-Institut ELV-LIVE, ICCT 2023, Dollinger & Fischerauer 2021 Energies 14(18) 5804 | – | temperature-binned kWh/km, battery conditioning power |

---

## 15. Seen in passing (out of scope)

* Cell 9 (`P_aux`): default `HVAC_eff=1.25`, a magic default when thermal mode needs 1.0.
* Cell 16 (`consumption_engine`) line "HVAC_row": applies HVAC to every row including standing rows; `fuel_heat` is never consumed. Hour index `(t_start+T)//3600` assumes hour 0 of the array is the reference.
* VECTO `.AHSM` engineering file (`BC_MaxTemperatureDeltaForLowFloorBusses 4.0`, `MaxPossibleBenefit 0.03`) differs from the declaration constants in `Constants.cs` (3.0, 0.5).

## 16. Choices I made

1. The 12 Nov notebook was **not on `main`**. I copied it from `origin/aux-pto-review-2026-11` (identical md5 `8e6c580a…` on `force-engine-review-2026-11`) into `docs/research/inputs/` in the first commit.
2. The prompt copy in `docs/research/inputs/kiro-prompt-hvac-review-2026-11-12.md` holds sections 0–2 verbatim and a **summary pointer** for sections 3–6 and Appendix 1 (the Appendix is in the notebook and in `appendix1_prompt_text.py`). Not a full verbatim copy.
3. `git clone` of the VECTO fork failed through the sandbox gateway; files were fetched as git blobs by GitHub API at commit `b8d6126` (byte-identical). The branch tip was verified as `b8d6126ab0…`.
4. Weather: DMI station **06188**, year **2025**, `Europe/Copenhagen` local time for the schedule; gaps filled linearly in time inside the test tooling (the parser's job).
5. ILLUSTRATIVE operating schedule Mon–Fri 06:00–16:00 local; whole shift driving.
6. Placeholder arguments Bob did not give: N = 2, vent 7/7 /h (VECTO config 2), caps 5 kW / 5 kW (VECTO driver compartment, Interurban column), R-744 + electric heater (HD2), COPs from `DefaultClimatic.aenv`. Passenger count `+1 driver` as VECTO.
7. Part D uses ±10 % elasticities because sourced ranges exist for few inputs.
8. Gate 3 grid supplies identical COP/share lookups to Bob and the port (the lookup *method* is compared in Part C).
9. Part J: no job files written (not needed).
10. I did not fetch or read most of Part G/H/I sources: time/tool limits (PDF and MDPI access). They are in the fetch table instead of guessed.

## 17. Reproduce

```
python -m venv v && v/bin/pip install numpy pandas matplotlib scipy pytest
cd docs/research/hvac-review-2026-11 && PYTHON=../../../v/bin/python bash run_all.sh
pytest tests/hvac -q
```
`determinism_sha256.txt` holds the SHA-256 of every output CSV; two full runs gave identical hashes (timing CSV excluded: it measures speed).
Gate 1 needs `VECTO_SRC` pointing to a checkout containing `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2` of commit `b8d6126`.
