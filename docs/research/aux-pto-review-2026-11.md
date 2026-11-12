# Auxiliaries and PTO deep dive: `P_aux`, `SP_power_helper`, `pto_engine`, aux/PTO part of `consumption_engine`

Date: 12 Nov 2026. Branch `aux-pto-review-2026-11`. For Bob. Nothing in the notebook or `src/` was changed.
Code of record: `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb` (sha256 `908c65c1…bd26`), loaded unchanged by
`docs/research/aux-pto-review-2026-11/_load_notebook.py`. VECTO source: `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`
(the `.vmod` files say VECTO 5.1.6-RC; I could not check a 5.1.6 tag, so `b8d6126` is the nearest source; the VAUX tables and the
`.vptoel`/`.vdri` copies in `reference/vecto/resources/` are byte-identical to the ones in `b8d6126` [TEST: `cmp`]).
Tags: `[VECTO]` `[REG]` `[SOURCE]` `[OEM]` `[CALC]` `[TEST]` `[ASSUMPTION]` `[SIMPLIFICATION]` `[OPEN]` as in the prompt. "Kiro's recommendation" marks the only places where I recommend.
All scripts are deterministic (checked: §12). Every CSV and graph is in `docs/research/aux-pto-review-2026-11/`.

---

## 0. Summary (one page)

**What is right.**
1. `P_aux` + `SP_power_helper` reproduce VECTO's electric W **exactly** for every combination a battery lorry can have: 3,454 table lookups and
   68,040 full combinations (group × mission × ES × HVAC × PS × 1–4 steered axles × SP technology), maximum difference 4.5e-13 W
   [TEST `test_every_valid_combination_matches_vecto_reimplementation`, `sweep_components.csv`]. Against the six E2 `.vmod` files all five aux match
   (SP: 23.009 W against 23.0 W is the 4-decimal-kW print of the `.vmod`) [TEST Gate 2, `gate2_e2_aux.csv`].
2. `pto_engine` + the old PTO loop give exactly VECTO's refuse energy: 96 PTO stops × 0.14993 kWh = **14.393 kWh**, standing time 2 s + 23 s = 25 s, PTO centred
   (1 s idle / 23 s PTO / 1 s idle) [TEST `partD1_municipal_summary.csv`; VECTO `DistanceBasedDrivingCycle.cs` 218-220, 264-304].
3. The aux timing rules are conservative: HDEV's aux total is 0.26–1.15 % **above** VECTO on the same VECTO rows; that is 0.012–0.090 % of the trip energy
   [TEST `partC2…csv`, `summary_effects.csv`]. All of it is Cond while **coasting** (VECTO off, HDEV on).

**What is wrong or missing (ranked by what can hurt).**
| # | Finding | Size | Source tag | Engine / parser |
|---|---|---|---|---|
| 1 | **BUG** Fractional profile times are truncated silently: `t=[0,1.5,3]` gives −33 % PTO energy; `t=[0,0.5,1]` gives **−100 %** and no PTO start | up to −100 % of that PTO | [TEST] `test_pto_engine.py` | parser (reject non-whole seconds) |
| 2 | **BUG** `consumption_engine` cannot take the 1 Nov `pto_engine` outputs: a 0 s marker waypoint raises "no standing rows", `is_on=1` with only a drive profile raises `int(NaN)`, the drive profile is dropped silently, no slot for constants | whole drive PTO missing | [TEST] `test_old_new_interface.py` | engine (step 6 rewrite, variant given) |
| 3 | **BUG** `P_aux` misses the checks on `PTO_always_on < 0` and `PTO_eff <= 0`: −100 W passes, `PTO_eff=0` gives `inf` with a warning only; NaN/inf pass, array shapes unchecked | −100 W…inf | [TEST] `test_p_aux.py` | engine (Bob's intended version fixes the first two) |
| 4 | Standing rows found with `V == 0` give **stop + 1 rows** (the first accelerating second also has speed 0): stop constants would run 1 s too long (+4 % for a 25 s stop) | +1 s on a 25 s stop constant (+4 %) | [TEST] `partD2_scenarios.csv` | engine (add `M == 0`) |
| 5 | The per-stop `np.where` scan is O(rows × stops): fine for one route (2 ms) and for 365 separate days (0.84 s), but **~120 s** if a year ever sits in one array (extrapolated); `searchsorted` makes it 0.6 s | speed only | [TEST] `partD_runtime_machine_dependent.csv` | engine |
| 6 | **New finding, not in 06/07/14:** a BEV that declares a *mechanical* PTO type gets a constant torque loss in front of the motor on **every mission**, not only while the PTO works. Calculated 15.8 kWh per 100 km for the 23.9 Nm "oil pump" type (15 % of the Regional, 19 % of the Urban, 10 % of the LongHaul battery energy), 1.85 kWh for the 2.8 Nm type. **Not yet seen in a VECTO run** | 0.26–15.8 kWh/100 km | [VECTO] `PowertrainBuilderBase.cs` 352-356 + [CALC] | needs Bob's VECTO run 2; HDEV has no term |
| 7 | VECTO's drive PTO (sweeper) is a **mechanical** load on the motor shaft, so motor losses apply; HDEV's `drive_pto_eff` default 1.0 treats it as electric | motor loss, 5–15 % of the PTO energy [OPEN: no motor-map number computed] | [VECTO] `PowertrainBuilderBase.cs` 332-347, `PEVPTO.cs` | parser (set `drive_pto_eff`) |

**Aux-timing changes (all tiny).** Cond off while coasting: −0.017 kWh Regional, −0.075 kWh Urban, −0.019 kWh LongHaul (ref. load); that is −0.016 %, −0.089 %, −0.013 % of the trip energy.
SP at `V > 0.01 m/s`: < 0.001 kWh. Because the current rules are the conservative side and the change only moves HDEV from "slightly above VECTO" to "equal to VECTO"
(LongHaul would go 0.05 % **below**), this is **a swap of one assumption for VECTO's, with no independent validation behind it**. Kiro's recommendation: keep the current rule and use the
deviation sentence in §9; change only if Bob wants line-by-line VECTO fidelity.

**Validation (Part F).** Only one comparable measured set was readable: the HSY/VTT winter e-refuse truck, 2.3 kWh/km total, 1.4 kWh/km driving (n = 1, winter, includes cab heating).
HDEV with the VECTO refuse profile gives 0.1499 kWh per stop (1.28 kWh/km on the Municipal cycle), which is **0.69 ×** the upper bound of VTT's non-driving energy per container. This is a plausibility check, not validation.
Everything else is `NOT FOUND` or `BLOCKED` (§8).

**Open items:** [OPEN] VECTO runs 1 and 2 (`reference/vecto/jobs/aux-pto-2026-11/`); [OPEN] why 0.8 for HVAC; [OPEN] measured standing-aux and Cond data; [OPEN] drive-PTO motor efficiency number.

---

## 1. Re-verification of `06`, `07`, `14` at `b8d6126` (CONFIRMED / CORRECTED / NOT FOUND)

Full list with the exact code line: `partA_reverification_06_07_14.csv` (27 claims, produced by grepping the source).

- **CONFIRMED (values):** `AlternatorEfficiency` 0.7, `DCDCEfficiency` 1.0, `HVACElectricEfficiencyFactor` 0.8; HVAC factor is 1/0.8; Cond on when an EM is on or the EPTO is on; SP (ID `STP`) removed when stopped;
  `P_PTO_el` is kW; default E-PTO cycle is `MunicipalUtility_PTO_generic.vptoel`; stop time = `StoppingTime` + PTO duration; 3-phase/7-phase stop; `PTOActivity` 0–3; road-sweeping and while-drive PTO only in engineering mode; the ES/PS/HVAC/SP/Cond tables quoted in `06`.
- **CORRECTED (lines moved, v5.1.3 `d16ba783c` → `b8d6126`):** DeclarationData 123/124/126 (was 128/129/131); Conditioning `oneEmOn || EPTOOn` is :86 (was :85-91); `DrivingCycleDataReader` ×1000 at :841 (was :845);
  `DefaultE_PTOActivationCycle` :1676 (was :1795); stop time :218-220 (was :226-227); phases :242-304 (was :248-310); `PTOActivity` :306-312; SP ×0.7 :220 (was :239); axle count check :188-190 (was :212); `EmOff` is :32 and is called `EmOff`, not `EmOffPrev`.
- **CORRECTED (content):**
  - `14` A2.6 says an electric PTO has no idle/transmission loss. True for the E-PTO consumer itself (`EPTO.cs` returns only the cycle value), **wrong for the vehicle**: if the vehicle declares a PTO type, `GetPEVPTO` adds `PTO_TRANSM` as a constant torque on the motor side (lines 352-356).
  - `14` B4 says `ElectricAuxDemand` is forced to 0 at `PowertrainBuilder.cs` 642 and 778. I find **one** such line (599, serial-hybrid builder). For the BEV declaration run it is 0 anyway: column `P_aux_P_aux_el_el` = 0 in all six `.vmod` [TEST].
  - `06` §5 open question "why group 5/10 Municipal HVAC = 0" is **answered**: groups 5 and 10 (tractors) have no Municipal-utility mission in `SegmentTable.csv`, so that cell is never looked up [TEST `test_hvac_default_group_5_and_10_municipal_zero_is_never_looked_up`]. Municipal exists only for groups 4, 9, 11.
  - `06` says SP-Table has Municipal values for groups 5/10 — true, but unused for the same reason.
- **NEW (not in the old notes):** the PTO cycle is attached **only** on MunicipalUtility (`DeclarationModeHeavyLorryRunDataFactory.cs:251`, other missions get only the transmission loss); drive-PTO overlap throws an error (`PTODriveAuxiliary.cs:26`); the `.vptoel` is sampled by left-hold, the last row only marks the end (`PTOCycleController.cs:148`);
  `VehicleStopped` uses the **previous** step's speed (`Vehicle.cs:262`).
- **NOT FOUND:** the string `.vptor` (the drive-PTO profile file extension) does not appear in the source; the JSON keys are `PTOCycleDuringDrive` (job) and `PTO.CycleDriving` (vehicle) and the file is read as a table with columns `t`, `PTO_Power` [kW] (`DrivingCycleDataReader.cs` 1034-1048).

## 2. Gates

- **Gate 1 PASS** [TEST]: `run_steps.py` unchanged, `VECTO_SRC=/projects/sandbox/vecto-src`: Chain S, V1, reference load: RegionalDelivery **0.9749**, UrbanDelivery **0.8502** kWh/km. The rewritten CSVs were byte-identical to the committed ones (`git status` clean).
  Environment: Python 3.11, numpy 2.4.6, scipy; venv in `/projects/sandbox/.venv-aux` (the system site-packages is read-only).
- **Gate 2 PASS** [TEST] (`gate2_e2_aux.csv`, produced by `run_part_b_sweep.py` which parses the VAUX csv itself):

| Mission | Aux | Table value | HDEV electric W | `.vmod` W | Diff |
|---|---|---|---|---|---|
| Regional | ES | 1428.5714 (mech) | 1000.000 | 1000.0 | 0 |
| Regional | HVAC | 200 | 250.000 | 250.0 | 0 |
| Regional | PS | 200 (`_el`) | 200.000 | 200.0 | 0 |
| Regional | SP | 32.87 (mech) | 23.009 | 23.0 | 0.009 (print precision) |
| Regional | Cond | 600 | 600 | 600 | 0 |
| Urban | ES / HVAC / PS / SP / Cond | 1428.57 / 150 / 162 / 45.73 / 550 | 1000 / 187.5 / 162 / 32.011 / 550 | 1000 / 187.5 / 162 / 32.0 / 550 | ≤ 0.011 (SP print) |
| LongHaul | ES / HVAC / PS / SP / Cond | 1714.29 / 200 / 237 / 4.29 / 600 | 1200 / 250 / 237 / 3.003 / 600 | 1200 / 250 / 237 / 3.0 / 600 | ≤ 0.003 (SP print) |

- **Gate 3** [TEST] (`gate3_differences.csv`): the Appendix 1.1–1.4 code in the prompt is **identical** (whitespace-normalised) to notebook cells 9, 10, 14 and steps 6–7 of cell 16. `src/engine/` has **no** `pto_engine` and **no** `SP_power_helper`; its `p_aux.py` is an older, different function
  (`p_aux(P_ES, P_HVAC, P_PS, P_SP, P_Cond, moving, motor_on)`, no factors, no PTO) and `consumption.py` is older too (default DC/DC 0.98, see §13). The notebook is the code of record.

## 3. Part A: line-by-line audit

### 3.1 Appendix 1.1 `P_aux`
| Lines | What it does | VECTO stand-in | Verdict |
|---|---|---|---|
| `powers = [np.asarray(...)]` | turns numbers/lists into float arrays | – | OK |
| `effs = (…)` | five factors, defaults 0.7 / 1.0 / 1.25 / 0.7 / 1.0 | `HeavyLorryAuxiliaryDataAdapter.cs` 118-120 (ES ×0.7), 140-143 (PS `_el` as is), 78 + 165 (HVAC ×1/0.8), 220 (SP ×0.7), 106 (Cond, no factor) | **MATCH** |
| `np.any(p < 0)` | no negative aux | – | OK, but **NaN/inf pass** (BUG, test) and `PTO_always_on` is not in the loop (BUG) |
| `e <= 0` | efficiency > 0 | – | OK for the five; `PTO_eff` is not checked (BUG); `nan <= 0` is False, so NaN passes |
| `p * e` | electric W | see above | **MATCH** (sweep) |
| `PTO_always_on / PTO_eff` | shaft W ÷ efficiency | none (HDEV rule) | OK; comment "undo the multiply above" is stale [TEST] |
| return | six values | – | arrays or scalars; mismatched array lengths are returned as they are |

### 3.2 Appendix 1.2 `SP_power_helper`
| Lines | What it does | VECTO | Verdict |
|---|---|---|---|
| shape checks | one (UF,B,S) row per steered axle, tech rows = axle rows | `HeavyLorryAuxiliaryDataAdapter.cs` 188-190 (count must match) | MATCH. Not checked: baseline shape (scalar is broadcast ×3), NaN, negative, shares > 100, > 4 axles (VECTO has rows 1–4 only) [TEST] |
| `baseline * shares.sum(0) / 100` | each part × summed axle shares | `SteeringPump.cs` 89-91 (baseline/100 × raw share) | MATCH (the /100 sits on the other factor, equivalent) |
| `* tech_factors.mean(0)` | averaged technology factor | `SteeringPump.cs` 107-111 (`factors / axleCount`) | MATCH. Release notes: "all CFs are averaged over all steered axles with electric technology" |
| `parts.sum()` | UF + B + S | `SteeringPump.cs` 113-114 | MATCH |

Subtle point [VECTO]: the *n-th* row of `SP-Axles.csv` is the share of the *n-th* steered axle (`SteeringPump.cs` 77-80: `axleCount++` then `Lookup(mission, axleCount)`), so the parser must pass rows 1…n, not "the row for n axles".

### 3.3 Appendix 1.3 `pto_engine`
| Line | What it does | VECTO | Verdict |
|---|---|---|---|
| `is_on[0] = 0` | no PTO at the depot | none | HDEV decision |
| `np.diff(t).astype(int)` + `np.repeat(w[:-1], steps)` | 1 s profile, left-hold | `EPTOCycleController` holds the left sample, last row = end (`PTOCycleController.cs` 148, 153-168) | MATCH for whole seconds; **BUG for fractions** |
| `pto_dur = len(stop_1s)` | profile length | `Duration = last.Time − first.Time` (`PTOCycleController.cs` 69/137) | MATCH (23 s) |
| `stop_on = is_stop & (is_on>0) & (pto_dur>0)` | where a stop profile applies | `Left.PTOActive == DuringStop` | OK; `> 0` here vs `== 1` in step 6 |
| `floor((stop − pto_dur)/2)` | PTO in the middle | 3-phase: idle `StoppingTime/2`, PTO, idle `StoppingTime/2` (`DistanceBasedDrivingCycle.cs` 264-279; 7-phase also `S/2` each side: 0.5 + (S/2−1) + 0.5) | **MATCH**, floor for odd seconds = HDEV choice (VECTO uses half seconds, ≤ 0.5 s shift, no energy effect) |
| `too_short` raise | PTO longer than stop | VECTO adds the PTO time to the stop (`:218-220`) | OK, parser must extend (rule decided) |
| `/ stop_pto_eff`, `/ drive_pto_eff` | shaft → electric | E-PTO W is already electric in VECTO | HDEV choice; no checks (0 → inf, −1 → negative, 2 → half) [TEST] |

### 3.4 Appendix 1.4 steps 6–7
| Line | What it does | VECTO | Verdict |
|---|---|---|---|
| loop over `pto_on_col == 1` | stop PTO per waypoint | – | works only for old outputs [TEST] |
| `np.where((V==0) & isclose(S, wp_s[i], atol=1e-3))` | standing rows | `stopTime` phases | gives stop + 1 rows on the notebook driver [TEST]; O(rows×stops) |
| `k0 = at_stop[0] + pto_start`, guard `k1 > at_stop[-1]+1` | centred placement | 3-phase | MATCH (1 s / 23 s / 1 s) |
| `moving = V > 0` → `SP * moving` | SP off when standing | `ElectricAuxiliaries.cs` 114-116 (|v| ≤ 0.01 m/s, previous step) | **DEVIATION (already flagged)**, < 0.001 kWh |
| `cond * (moving | pto_active)` | Cond rule | `Conditioning.cs` 85-91 (EM not off, or EPTO on) | **DEVIATION (already flagged)**: HDEV is on while coasting and braking slowly |
| `ES + PS + HVAC_row` | always on | `DemandType.Constant` (`HeavyLorryAuxiliaryDataAdapter.cs` 61-64) | MATCH |
| `+ PTO_always_on` | not hour-indexed | – | **BUG** for a per-hour array: wrong length → numpy broadcast error; length equal to the number of rows → silently row-indexed [TEST] |
| `P_battery = P_trac + P_aux_row` | aux added 1:1 | `DCDCConverter.cs` 45 with eff 1.0 (`DeclarationData.cs:124`) | **MATCH**; VECTO also zeroes aux if the battery cannot deliver (`P_DC/DC_missing`, `DCDCConverter.cs` 59-68): HDEV has no limit [OPEN, not a bug] |

### 3.5 Hard-coded numbers
`partA_hardcoded_numbers.csv` (19 lines). In short: the five factors are VECTO constants passed as default arguments (parser should pass them); `/100`, `/3.6e6` are unit definitions;
`V == 0`, `atol=1e-3` are numerical tolerances; `is_on[0]=0`, `floor`, `PTO_eff=1.0` are HDEV choices; `astype(int)` is a numerical hazard.

## 4. Questions Q1–Q10 (answers from the VECTO source at `b8d6126`)

**Q1 – meaning of table values and factors (PEV).** Verdict **MATCH**.
- ES: `ES-Tech.csv` = mechanical W at an alternator; electric = × 0.7 (`HeavyLorryAuxiliaryDataAdapter.cs:118-120`). Why 0.7 for a vehicle without an alternator: the tables were built as engine-shaft equivalents; VECTO's release notes (`ReleaseNotesVecto3x.md` ~367) state the same 0.7 principle applies to PEVs. The electric load is therefore the 24 V load of a conventional truck (1000 W Regional), not the larger table number. [VECTO]
- PS: for a PEV only techs with `PEV = 1` (the "elec. driven" ones) are allowed; the electric W is the `*_el` column **as is** (`:139-143`). The `_el` values of the AMS rows are not 0.7 × mech (e.g. "Small + AMS + elec. driven" 675 W against 0.7 × 357 = 250 W) [TEST `test_ps_el_column_is_not_always_0_7_times_mech_column`], so the parser must read the `_el` column, never derive it.
- HVAC: `HVAC-Table.csv` "Default" = mechanical compressor W; electric = × 1/0.8 = 1.25 (`:78, 165`). The release notes say HVAC for lorries is only yes/no (`None`/`Default`). Why 0.8: [OPEN] no rationale found in code or release notes.
- SP: table = mechanical W (`SteeringPump.cs` doc line 56: "power demand is mechanical also for the electric pumps"), electric = × 0.7 (`:220`).
- Cond: table = electric W, no factor (`:106`); keyed by mission only (`Conditioning.cs:37`).
- HDEV's `P_aux` reproduces VECTO for every valid combination (§0, `sweep_components.csv`). The tables are empty/invalid for: SP Municipal/Construction for groups 1s,1,2,3 and Municipal for 12, 16; ES Municipal/Construction for medium groups 51–56; every table for groups 6–8, 13–15, 17 (not valid groups); HVAC Municipal for 12/16. HDEV and the VECTO re-implementation agree on all 1,826 failing lookups (`sweep_empty_or_invalid.csv`); the parser must give a clear error for them.
  Municipal utility exists only for groups 4, 9, 11 (`SegmentTable.csv`); Urban delivery is missing for groups 9, 10, 11, 12 and 16.

**Q2 – when each aux is on (PEV).** From the six `.vmod` (`partC1_vmod_aux_by_state.csv`, ReferenceLoad):
| State (DriverAction) | SP on-fraction (Regional / Urban / LongHaul) | Cond on-fraction | EM off fraction |
|---|---|---|---|
| standing (Halt 0) | 0.000 / 0.001 / 0.002 | 0.005 / 0.008 / 0.037 | 0.996 / 0.986 / 0.967 |
| accelerating (Accelerate 6, a>0.1) | 0.983 / 0.989 / 0.997 | 0.981 / 0.989 / 0.994 | ≈ 0 |
| cruising (6, |a|≤0.1) | 1.000 | 1.000 | 0 |
| coasting (Coast 4) | 1.000 | **0.049 / 0.070 / 0.031** | 0.888 / 0.865 / 0.952 |
| braking (Brake −5) | 0.990 / 0.980 / 0.986 | 0.947 / 0.931 / 0.965 | 0.069 / 0.092 / 0.047 |
`DriverAction` enum (Driver.cs 51-58): Halt 0, Roll 2, Coast 4, Accelerate 6, Brake −5. [VECTO + TEST] SP and Cond are **not** at full level in the first second of a start (VECTO switches on at the next sub-step; on-fraction 0.29 in the first accelerating second): both use the previous step's state (`Vehicle.cs:262`, `ElectricMotor.cs:32`).
Leads in §1.2 item 2: **confirmed** ("DemandType.Constant", Cond on iff an EM is not off, |v| ≤ 0.01 m/s). **STP-off-when-stopped**: deliberate in VECTO: commit `be6ce764` (29 Sep 2022) changed the stop-list of `ElectricAuxiliaries` from Fan to SteeringPump with the message "ignore fan when ice is off, ignore steering pump when vehicle is stopped" [VECTO git history via the GitHub API]. That the electric pump shares the ID "STP" (`Constants.cs:59-60`) is how the rule reaches it; whether the authors thought of the electric pump specifically is not documented [OPEN]. HDEV's sentence "follows VECTO's current behaviour" is correct.

**Q3 – Cond.** "Conditioning power for electric propulsion components" [VECTO release notes]: cooling/heating of motor, inverter and battery are not itemised anywhere I could read ([OPEN] finer split). `Cond-Table.csv`: one row "Lorry", 600/600/550/550/600 W for Long haul/Regional/Urban/Municipal/Construction; key = mission only. Applied fully when at least one EM is not off **or** the E-PTO is on (`Conditioning.cs:83-91`); the release notes say "propelling/braking, or E_PTO = on". During a stop PTO, VECTO therefore runs Cond at 550 W (0.337 kWh over the 96 stops on Municipal) — and HDEV's rule `moving | pto_active` does the same [TEST]. Verdict: Cond-during-PTO **MATCH**; Cond-while-coasting **DEVIATION (already flagged)**.

**Q4 – SP.** Full logic in §3.2. Baseline per (mission, group) in U+F/B/S; blank cells → lookup error; groups 6–8 empty. Allowed PEV technologies: only "Electric driven pump" (factors 0.857/0.857/0.857) and "Full electric steering gear" (0/0.143/1.429) — the `PEV` column of `SP-Tech.csv`, `fully electric` column is not used for the applicability test. At most 4 steered axles (`SP-Axles.csv` rows 1–4; the 5th gives "No value found for SteeringPump Axle"). No speed or steering-angle dependence; only the stop switch. **MATCH**.

**Q5 – PS.** `PEV = 1` rows only; electric W = `<mission>_el` column; mission dependence only (no group). 9 allowed technologies. **MATCH**.

**Q6 – HVAC.** "Default" = mechanical A/C compressor W per (group, mission); "None" = 0. Group 4/9/11 Municipal 300 W; 5/10 Municipal 0 (never looked up). × 1.25. **MATCH**. [OPEN] rationale of 0.8.

**Q7 – path to the battery.** All aux (ES, HVAC, PS, SP, Cond, EPTO, Padd_hv, `ElectricAuxDemand`) sit in `ElectricAuxiliaries` → `DCDCConverter` (eff 1.0) → `ElectricSystem` → REESS (`PowertrainBuilderBase.cs` 233-268). `P_aux_el_HV` = `P_aux_el` in all six `.vmod`. Nothing is supplied by regen first; the sum goes to the battery as a demand like any other. The DC/DC converter limits: if the battery cannot give the power, VECTO sets the aux to 0 and logs `P_DC/DC_missing` (`DCDCConverter.cs` 59-68) — HDEV has no such limit [OPEN]. HDEV's "sum of aux W added to traction W at the battery terminals" **MATCHES**.

**Q8 – stop PTO timing.** Standing time = `StoppingTime` + PTO duration (`DistanceBasedDrivingCycle.cs:218-220`). Phases (`:264-304`): `StoppingTime ≤ 3 s` → 3 phases (idle `S/2`, PTO, idle `S/2`); `> 3 s` → 7 phases with the same total idle on each side. So the PTO sits exactly in the middle (half seconds allowed). Sampling: the `.vptoel` row is held until the next row (left-hold); the step length is the row spacing (`GetNextCycleTime`), so HDEV's `np.repeat` is the same for whole seconds. A stop with PTO but `StoppingTime = 0` starts the PTO at once (`:259-261`). Two back-to-back PTO stops: each stop resets the cycle (`ActivateIdle` → `Reset`, `PTOCycleController.cs` 172-176, 185-189). A stop shorter than the profile cannot occur in VECTO (the PTO time is added). The PTO cycle is attached **only on MunicipalUtility** (`:251`). **MATCH** (rounding = HDEV choice).

**Q9 – drive PTO.** Two engineering-mode paths (`PowertrainBuilderBase.cs` 325-350): road sweeping (`PTO` = 2, power from the cycle column `PTO_Power` [kW], interpolated over distance, `RoadSweeperAuxiliary.cs`) and while-drive (`PTO` = 3, a time profile started at the cycle row's distance, `PTODriveAuxiliary.cs`). The while-drive profile **keeps running through a stop** (a warning only); a second start while it runs **throws** "Additional PTO activation during drive requested while PTO still active!" (`:26`). Both are **mechanical** torques on the shaft in front of the motor (`PEVPtoTransm`: torque = P / ω), so the motor's own losses and inertia apply. Engineering mode only: confirmed. Verdicts: keeps running **MATCH**; overlap error **MATCH** in the variant; one sweeping power per route **DEVIATION (already flagged)**; `drive_pto_eff = 1.0` default **DEVIATION (new, flag it)** if the drive PTO is mechanical.

**Q10 – VECTO terms HDEV has no term for** (`partA_q10_unmodelled_terms.csv`):
- PTO transmission torque loss `PTO_TRANSM` on the motor side when a PTO type is declared: [CALC] 0.26 / 1.85 / 15.8 kWh per 100 km for the 0.4 / 2.8 / 23.9 Nm types (Regional ReferenceLoad; Urban and LongHaul within 0.06 kWh of these because the motor revolutions per km are the same). Assumes the torque acts at motor speed (`PTO` is between gearbox input and motor, `PowertrainBuilder.cs` 971-980). **Needs VECTO run 2.** The conventional `Power Loss` column (3000 W for the oil-pump type) would give ~3 kW at ~1200 rpm; the torque form gives 9.6 kW mean at motor speed, so the calculation may be an over-estimate of what VECTO does [OPEN].
- `Padd_hv`, `ElectricAuxDemand`: 0 in the E2 runs [TEST]. DC/DC loss: 0. `P_DC/DC_missing`: no HDEV term. Fan/engine-off: n/a for a BEV.

## 5. Part B: unit tests (`tests/aux_pto/`, `pytest tests/aux_pto`: 113 passed, ~7 s)
| File | Covers | Findings (BUG = Bob's code gives a wrong or silent result on a realistic input) |
|---|---|---|
| `test_p_aux.py` | scalars, lists, hourly arrays incl. `PTO_always_on`, zeros, negatives, efficiencies, NaN, shapes, stale comment | BUG `PTO_always_on = −100` passes; BUG `PTO_eff = 0` → `inf` (warning only), 0/0 → NaN; BUG NaN/inf pass; BUG mismatched array lengths pass; `PTO_eff = 1.5` accepted; array-valued efficiency gives an unclear numpy error; stale comment confirmed |
| `test_sp_power_helper.py` | 1–4 axles vs hand calc, 5 axles, shape errors, empty, NaN | scalar baseline broadcast to 870 W; 2-D baseline accepted; NaN/negative/share 300 % accepted; 5 axles accepted (VECTO has none) |
| `test_pto_engine.py` | VECTO refuse file, centring, `is_on` rules, fractional times, profile errors, efficiencies, NaN | BUG fractional time; BUG sub-second profile vanishes; `is_on` = 2/0.5 accepted; plateau time dropped silently; 2-point zero profile is **not** "no profile" |
| `test_vecto_sweep.py` | Gate 2, 68,040 combinations vs the independent C# re-implementation `vecto_aux_reimpl.py`, empty cells | no mismatch |
| `test_old_new_interface.py` | 1 Nov outputs in the old slots | BREAKS marker waypoint, BREAKS `int(NaN)`, BREAKS drive profile dropped, BREAKS no slot for constants; two stops at one distance are matched to the same rows without error |
| `test_step6_variant.py`, `test_step6_copy_matches_notebook.py` | Part D; copies checked against the real `consumption_engine` | – |

`vecto_aux_reimpl.py` was written from the C# lines only (header lists them), without looking at Bob's code.

## 6. Part C: aux timing vs VECTO, row by row (`run_part_c.py`)

**C1** Table in Q2. LongHaul uses the VECTO files (truck + trailer); no HDEV driver is needed for C1–C3.
**C2** HDEV's current rules on the same VECTO rows (V = speed at the start of the row, rebuilt as `v_avg − a·dt/2`), ReferenceLoad / LowLoading:
| Mission | SP kWh VECTO → HDEV | Cond kWh VECTO → HDEV | Total aux VECTO → HDEV | Difference |
|---|---|---|---|---|
| Regional ref | 0.0328 → 0.0329 | 0.8384 → 0.8570 | 3.2415 → 3.2602 | +0.0187 kWh (+0.58 %) |
| Regional low | 0.0328 → 0.0328 | 0.8414 → 0.8568 | 3.2445 → 3.2600 | +0.0155 (+0.48 %) |
| Urban ref | 0.0895 → 0.0905 | 1.4814 → 1.5562 | 6.6273 → 6.7032 | +0.0759 (+1.15 %) |
| Urban low | 0.0894 → 0.0904 | 1.4973 → 1.5536 | 6.6406 → 6.6979 | +0.0573 (+0.86 %) |
| LongHaul ref | 0.0037 → 0.0037 | 0.7245 → 0.7425 | 2.8468 → 2.8648 | +0.0180 (+0.63 %) |
| LongHaul low | 0.0037 → 0.0037 | 0.7322 → 0.7395 | 2.8461 → 2.8534 | +0.0073 (+0.26 %) |
Where the Cond difference sits (`partC2_diff_by_state.csv`, Regional ref, kWh): coasting 0.0136, braking 0.0033, accelerating 0.0012, others < 0.001. The earlier note (+0.7 % / +1.9 %) is of the same order; the exact numbers differ because of the row-start speed used here.
**C3** Rule variants, one at a time, total aux difference to VECTO [kWh | % of VECTO trip energy], ReferenceLoad (`summary_effects.csv`, graph `graph_partC_rule_variants.png`):
| Variant | Regional | Urban | LongHaul |
|---|---|---|---|
| current | +0.0187 \| +0.018 % | +0.0759 \| +0.090 % | +0.0180 \| +0.012 % |
| (a) SP on at V > 0.01 m/s | +0.0187 \| +0.018 % | +0.0755 \| +0.090 % | +0.0180 \| +0.012 % |
| (b) Cond only if motor not off (proxy P2) | +0.0017 \| +0.002 % | +0.0012 \| +0.001 % | **−0.0014 \| −0.001 %** (under VECTO) |
| (c) Cond also during stop PTO | same as (b): no PTO in E2 runs; tested in Part D | – | – |
| (a)+(b)+(c) | +0.0017 | +0.0007 | −0.0014 |
| (d) SP and Cond always on | +0.1473 \| +0.140 % | +0.6099 \| +0.726 % | +0.0290 \| +0.019 % |
Motor-off proxy (`partC3_motor_off_proxies.csv`): P2 = `M ∈ {0,3}` or (`M == 4` and `V ≤ v_no_regen`) is best (845 s against VECTO's 852.7 s Regional; 3792 against 3796.8 Urban). It is also the set of rows where the notebook itself sets `P_trac = 0`. P1 (standing + coasting only) misses 6–14 s of low-speed braking, standing only (P3) is far off. All variants except (d) are within 0.1 % of the aux total of VECTO's own Cond. **Conservative choice: current rule (or (d))**; rule (b) is the only one that can end below VECTO.
**C4** HDEV's own driver rows (notebook `driver_model`, E2 reference set-up, thresholds in m/s, coasting on, E2 drag table): Regional ref total aux +0.50 % (rules a+b+c: +0.07 %), Regional low +0.45 % (+0.10 %), Urban ref +1.48 % (+0.74 %), Urban low +1.21 % (+0.75 %) (`partC4_hdev_driver_rows.csv`). The Urban remainder is the driver: HDEV needs 13,576 s against VECTO's 13,489 s (+0.64 %), and all time-proportional aux scale with it. LongHaul: **BLOCKED** (truck + trailer: trailer axle data, mass and CdxA not set up; a truck-only run is a named pitfall).

## 7. Part D: PTO on rows (`reference_copy.py: consumption_step6_v_pto1nov`, `run_part_d.py`)

Built exactly to §1.1 of the prompt; ENGINE (pure arrays and numbers). Rules and where they come from:
| Rule | VECTO | HDEV decision | New proposal |
|---|---|---|---|
| Stop profile starts at first standing row + `pto_start`, must fit | 3-phase stop | decided | – |
| Stop constant on all standing rows, ÷ efficiency | n/a (VECTO has profiles only) | decided | find standing rows with `V == 0 and M == 0` (see below) |
| Drive profile from the first moving row after the stop, keeps running through the next stop | `PTODriveAuxiliary` keeps running (warning) | decided | – |
| Overlap of two drive profiles → error | throws (`:26`) | – | `ValueError`, same message idea |
| Drive constant until first standing row of next stop | road sweeping runs while `PTO = 2` rows | decided | – |
| 0 s marker waypoint can start a drive part | `PTO = 3` row at a distance | decided | window starts at first row at/after the marker |
| Cond during PTO | on (`Conditioning.cs:86`) | on (`moving | pto_active`) | for drive PTO the vehicle moves so Cond is on anyway |
| Row matching `V == 0` and distance ±1e-3 m | – | current code | `searchsorted` on `S` (non-decreasing), reject two stops at one distance |
**D3 – MunicipalUtility** (`partD1_municipal_summary.csv`, `partD1_municipal_per_stop.csv`): the VDRI flags **96** PTO stops (rows 2607–5467 m, 2 s stop each); standing = 25 s; PTO energy on rows **14.39307 kWh = 96 × 0.149928** (difference 0); every stop 1 s idle / 23 s PTO / 1 s idle; Cond during the PTO 0.337 kWh; route time 4389 s with the extension against 2181 s without (forgetting the 23 s loses 2,208 s of standing time). **Any refuse/Municipal energy number must include this PTO (14.39 kWh = 1.28 kWh/km on this cycle) and the 23 s per stop.** The E2 vehicle is only a stand-in for the driver rows (`[ASSUMPTION]`, group 2 has no Municipal mission, see Part I).
**Off-by-one found:** with the notebook driver the first accelerating row of every stop also has `V == 0` (rows with `V==0` minus rows with `M==0` = 1 for all 96 stops). A stop constant found with `V == 0` runs 26 rows instead of 25 (`stop constant 3000 W: 0.021667 vs 0.020833 kWh`, +4 %). The profile case is unaffected (centred from `at_stop[0]`).
Scenarios (all ILLUSTRATIVE W; `partD2_scenarios.csv`): sweeper constant 6000 W/0.9 for 100 rows = 0.1852 kWh ✓; mixed refuse 2 stops + 60 s × 4 kW drive = 0.3665 kWh ✓; PTO on the last waypoint: stop profile placed, drive part has no rows ✓; drive profile longer than the route is truncated and flagged ✓; drive profile running through the next stop ✓; overlap → error ✓; marker with a stop profile configured → only the drive part ✓; two stops at one distance → error ✓; float drift 5e-4 m ok, 2e-3 m → "no standing rows found" ✓; stop shorter than the profile → `pto_engine` error ✓; odd standing time floor ✓.
**D4 runtime** (`partD_runtime_machine_dependent.csv`, machine-dependent): one Municipal route 2.2 ms (current loop) against 1.6 ms (variant); 365 sequential days 0.84 s against 0.62 s; 365 days in one 1.6 M-row array: variant 0.6 s, current loop ≈ 120 s (measured on 5 days, extrapolated by (365/5)²). If a year ever sits in one array with `S` restarting each day, the match `V == 0 & S == wp_s` would hit every day [OPEN design hazard]; Option A (one day per call) avoids it.

## 8. Parts E, F, G

### 8.1 Part E: what is known beyond VECTO (I read only what is listed; everything else is `Bob to fetch`)
| Item | Source (what I read) | Value / finding | Tag | For HDEV | VECTO low or high? |
|---|---|---|---|---|---|
| Refuse PTO + cab, winter e-truck | VTT/HSY project news 24 May 2023, `vttresearch.com/en/project_news/refuse-truck-future-hums-along-quietly-without-emissions`, **full page** | 2.3 kWh/km in collection, 1.4 kWh/km driving, > 500 containers, > 120 km/day; cab heating/demisting "a fairly large proportion"; body hydraulics (hydraulic cylinders and pump; drive of the pump not stated) | [SOURCE] | non-driving ≈ 0.9 kWh/km [CALC]; HDEV Municipal PTO+aux 1.48 kWh/km | VECTO per-stop PTO 0.1499 kWh vs ≤ 0.216 kWh/container all-in: VECTO profile is plausibly low-ish [OPEN, n = 1] |
| Waste-collection vehicles, simulation from real operational data | TRID 1852414 abstract only | eWCV 1.85 kWh/km, diesel 5.43 kWh/km | [SOURCE abstract] | context | – |
| ePTO load cycles | Ban & Stipetić, IEEE VPPC 2019 (abstract on scispace; ICEM 2020 PDF returned 403) | load-cycle approximations for refuse, concrete mixer, hook-loader, vacuum trucks | [SOURCE abstract] | **candidate profile library**: needs the full text | – |
| e-HPS waste compactor | MDPI Appl. Sci. 11(7) 3033 (abstract; page 403) | electric hydraulic pump, 65,000 € life-time saving, CO₂ −80 % | [SOURCE abstract] | no kWh/stop read | – |
| Concrete mixer drum | Liebherr ETM sheet in repo `docs/research/electric-truck-mixer-etm.pdf`; BTS/DOT report abstract | drum drive 125 kW peak / 60 kW continuous, 32 kWh battery [OEM]; mixer up to 4 kWh/mile incl. aux, ~2× a class 8 e-truck [SOURCE abstract, `rosap.ntl.bts.gov/view/dot/78763`] | [OEM] [SOURCE abstract] | rating, not consumption; a drum kWh/h figure was **not found** | – |
| ePTO rating | Mercedes eEconic sheet in repo | ePTO high power ~52 kW max / ~30 kW continuous at 50 % SOC | [OEM] | rating only | – |
| Fridge unit | Carrier Vector eCool sheet in repo | battery pack 19.2 kWh, max continuous discharge 19 kW | [OEM] | rating only | – |
| Fridge physics | ATP: K = W/(S·ΔT); IN K ≤ 0.70, IR K ≤ 0.40 W/m²K (`wetten.overheid.nl` ATP text, search snippet); the fork's own earlier report `claude/REPORT_tru_power_model.md` @ `b8d6126` (secondary: its primary sources were **not** re-read): COP 1.1–1.4 (SEMI-THERM 2016) / ~1.7 (MDPI 11, 5614), capacity factor 1.75 is a sizing margin, not a running multiplier, EPRI TRU 15,000 kWh/yr ≈ 41 kWh/day | [SOURCE] + secondary | minimal model = `K·S·(T_out − T_set)/COP` per hour into `PTO_always_on`; inputs K, S from the ATP certificate (easy), COP vs T **not published** (hard-to-get, rule 10) → keep a documented default band, flagged | – |
| Cold-climate aux | Chalmers/Volvo "Heating load reduction strategies for cabin and battery climatization in electric trucks" (abstract); SAE 2022-01-0199 (abstract: aux power estimates within 6 % MAPE); e-bus heating factor 1.9 (MDPI WEVJ 12(1) 7 abstract) | qualitative: higher aux demand for cabin and battery climatization in the cold | [SOURCE abstract] | Cond and HVAC are the weather-sensitive aux; VECTO's Cond is flat 550–600 W | VECTO Cond likely **low** in cold and **high** in mild weather [OPEN, no number read] |
| Fleet data | Öko-Institut "Real-world data analysis of battery electric trucks" (`oeko.de/fileadmin/oekodoc/Real-world-data-analysis-of-battery-electric-trucks.pdf`); NREL Fleet DNA; Dollinger 2021 | **not read** (PDF; web fetch cannot open PDFs) | NOT FOUND | – | – |

Standing aux (Part E.2): `NOT FOUND` in full text. What the physics says [CALC/ASSUMPTION]: ES, PS, HVAC keep running at stops in VECTO already; only SP (23–32 W) and Cond (550–600 W) are off. VECTO's rule makes sense for SP (no steering) and for Cond when the motor is idle; if the battery conditioning runs while the truck stands (hot or cold soak) VECTO would **under**-estimate by up to 0.55–0.6 kW × standing hours. Standing is 746 s (Regional) to 3349 s (Urban) per cycle, i.e. at most 0.11–0.51 kWh of Cond per cycle, 0.1–0.6 % of trip energy; and on Municipal the 96 × 23 s PTO window is already counted.

**PTO profile library candidates** (every entry must be cited and tagged before it enters the library; nothing below is a value to use yet):
| Body | Candidate source | What exists | Values | Licence | Status |
|---|---|---|---|---|---|
| Refuse (VECTO generic) | `MunicipalUtility_PTO_generic.vptoel` | 23 s, 8.42 / 33.69 / 25.92 kW, 0.14993 kWh per stop | in the file | EUPL 1.2 (repo licence) | **ready** [VECTO] |
| Refuse (measured) | VTT/HSY page | ≈ 0.9 kWh/km non-driving, ≤ 0.216 kWh/container all-in | upper bound only | VTT web text (cite) | boundary unclear |
| Refuse / mixer / hook-loader / vacuum | Ban & Stipetić 2019 | load cycles | not read | paper (cite) | **Bob to fetch** |
| Mixer | Liebherr ETM | 60 kW continuous drum drive rating | rating | OEM | not a consumption |
| Sweeper | VECTO engineering example `Class9_RigidTruck_6x2_Roadsweeper` (PTO-cycle.vptoc, diesel) | mechanical, not electric | not read in this job | EUPL | optional |
| Fridge, crane, tipper, tail lift | none found | – | `NOT FOUND` | – | open |

### 8.2 Part F: independent validation (`partF_validation.csv`, `run_part_f.py`)
| Quantity | HDEV / VECTO | Other source | Spread |
|---|---|---|---|
| Aux share of battery-terminal energy, E2 (VECTO runs) | Regional 3.09 %, Urban 7.89 %, LongHaul 1.86 % | NOT FOUND (no measured share read) | – |
| Refuse non-driving energy per km | HDEV (VECTO profile + Urban aux) 1.28 + 0.20 = **1.48 kWh/km** | VTT 0.9 kWh/km (winter, n = 1, includes cab heating; HDEV cycle has 8.5 stops/km) | HDEV 1.65 × VTT per km; per stop 0.69 × VTT's all-in bound |
| Mixer kWh/hour, fridge kWh/hour | `BLOCKED` (no sourced mixer vehicle or ATP data in the repo) | – | – |
Verdict: HDEV with VECTO's refuse profile is neither clearly above nor below the one measured case; the spread depends on stops per km and on what the 0.9 kWh/km contains. This is **not** validation. Spread for the PTO per stop could be 0.7 × to 1 ×, per km 1.65 ×.

### 8.3 Part G: how other tools model aux/PTO (code read in Bob's forks, shallow clones)
| Tool | What I read | Aux model | PTO / body | Lesson for HDEV |
|---|---|---|---|---|
| FASTSim `mohgsaad-art/fastsim` @ `6a07d4d` (Rust) | `drive_cycle.rs`, `simdrive/mod.rs`, `vehicle/bev.rs`, `conv.rs`, `compat/fastsim_2/mod.rs` (grep + partial reading) | one constant base aux power (`aux_kw` / `pwr_aux_base`) added to the battery request (`bev.rs` 199-213); `solve_thermal(T_amb)` adds HVAC/battery thermal aux (`simdrive/mod.rs` ~427); source comment: "TODO: add provision for optional time-varying aux load" (`drive_cycle.rs:49`) | none found | same split HDEV has (constant base + weather-dependent thermal); FASTSim also has no body model |
| eflips-depot @ `87f95ee` | `api/private/consumption.py` | no aux term: consumption comes from a lookup table over incline, ambient temperature, level of loading and speed (`t_amb`, `level_of_loading`); temperature is the only aux proxy | none | a table by ambient T absorbs HVAC and thermal aux; PTO would need an extra axis |
| spice_ev @ `f0c7061` | grep only | consumption per trip read from input (SimBEV `energy_consumption`), no aux model found | none | – |
| dt-cargo @ `805c534` | `main.ipynb` headings | data set (anonymised recorded truck operation), no energy model | none | possible source for body-use patterns, not read |
| Autonomie, TU Graz PHEM, US EPA GEM | **only titles/links found** (GEM v3.5.1/v4.0 user guides at `nepis.epa.gov`, Autonomie NHTSA validation slides) | content **not read** | not read | Bob to fetch |

## 9. Proposed changes (before / after) and deviation register

**Rule 8 check on each change: does it have a standard or validation behind it, or does it only swap one assumption for another?**

**P1 (BUG fix, ENGINE) – checks in `P_aux`.** Before: `for p in powers:` / `for e in effs:`. After (Bob's intended version, tested as `P_aux_v_bob_intended`): `for p in powers + [PTO_always_on]:` and `for e in effs + (PTO_eff,):`. Extra proposal (`P_aux_v_checks`): reject NaN/inf, mismatched array shapes, `PTO_eff > 1`. Effect: no change on valid input; stops −100 W and `inf`. Not an assumption swap.
**P2 (BUG fix, PARSER) – whole-second profile times, strictly increasing, W ≥ 0, finite, efficiency in (0,1], `is_on` ∈ {0,1} and right length, "no profile" = one point.** Function `parser_check_pto` in `reference_copy.py` (tested). Effect: removes a −33 % … −100 % error on fractional profiles. Per-second averaging of fractional profiles stays parked.
**P3 (ENGINE) – step 6 for the 1 Nov outputs.**
```python
# before (notebook)                                          # after (variant, tested)
for i in np.where(pto_on_col == 1)[0]:                        pto_row, stop_active, drive_active, events = consumption_step6_v_pto1nov(
    at_stop = np.where((V == 0) & np.isclose(S, wp_s[i],          S, V, wp_s, stop_wp, is_on, pto_start, stop_1s, drive_1s,
                       rtol=0, atol=1e-3))[0]                      stop_const_W, drive_const_W, stop_eff, drive_eff, M=M)
    ... raises if no standing rows (also for a marker)         # then: P_aux_row = ES + PS + HVAC_row + SP*moving + cond*(moving|stop_active)
    pto_row[k0:k1] = pto_1s                                    #            + PTO_always_on + pto_row
```
Effect: Municipal stop PTO unchanged (14.393 kWh); drive and constant parts now possible; 365-day runtime 0.84 s → 0.62 s (single array: ~120 s → 0.6 s). Matches VECTO's rules (overlap error, run-through). Not an assumption swap.
**P4 (ENGINE) – standing rows with `M == 0`.** +4 % on a 25 s stop constant when `V == 0` is used alone. Needs `M` in the call (it is already an argument of `consumption_engine`).
**P5 (ENGINE, optional) – SP on at `V > 0.01 m/s`.** Effect < 0.001 kWh per cycle. Swap of one threshold for VECTO's; **not worth making**.
**P6 (ENGINE, optional) – Cond off while the motor is off (coasting, standing, braking below `v_no_regen`).** Effect −0.017 / −0.075 / −0.019 kWh (Regional / Urban / LongHaul ref) = −0.016 % / −0.089 % / −0.013 % of trip energy. Moves HDEV towards VECTO and, for LongHaul, below it (−0.05 % of aux). Only a swap to VECTO's assumption, and it lowers energy (Bob's stance 9). **Kiro's recommendation: do not change; use the sentence below.**
**P7 (PARSER) – drive-PTO efficiency.** If the drive PTO is a mechanical load on the traction motor (VECTO's model), set `drive_pto_eff` to the motor+inverter efficiency, not 1.0; if the body has its own electric motor, 1.0. Needs a yes/no from the user (not hard to get). [OPEN] number.
**P8 (OPEN, needs VECTO run 2) – PTO transmission drag** for a declared mechanical PTO type. Do nothing until Bob's run confirms the size (calculated up to 0.158 kWh/km).

**Deviation register** (HDEV against VECTO, aux and PTO; sentence for a client report):
| # | Deviation | Size | Sentence |
|---|---|---|---|
| D1 | Cond is on while coasting and braking slowly (VECTO: off when the motor is off) | +0.26…1.15 % of aux, +0.012…0.090 % of trip energy | "HDEV keeps the conditioning load on whenever the truck is moving; VECTO switches it off while coasting. This adds up to 0.09 % to the trip energy." |
| D2 | SP on for any speed > 0 (VECTO: > 0.01 m/s, previous step) | < 0.001 kWh | "Steering-pump power is applied whenever the truck moves." |
| D3 | 1 s rows against VECTO's sub-second steps (first second of a start counts fully) | inside D1/D2 | – |
| D4 | PTO start: floor for odd seconds (VECTO half seconds) | ≤ 0.5 s shift, no energy effect | "The PTO is centred in the stop, rounded down to a whole second." |
| D5 | Profiles must be whole seconds | parser rejects | – |
| D6 | One sweeping power per route (VECTO: distance-interpolated `PTO_Power`) | depends on the cycle | "Sweeping power is a route average." |
| D7 | Same PTO power at every stop | – | – |
| D8 | `drive_pto_eff` default 1.0 | motor loss missing if mechanical | "Drive-PTO power is assumed to be electric." |
| D9 | No PTO transmission torque loss | 0.26…15.8 kWh/100 km if a mechanical PTO type is declared (calculated, unconfirmed) | "No mechanical PTO drag is modelled." |
| D10 | No `P_DC/DC_missing` limit | none unless the battery is empty | – |
| D11 | Optional "use stop time as PTO time" (standing = max(stop, PTO)) is **non-VECTO** and non-conservative (shorter standing, e.g. −2 s per Municipal stop ≈ −0.07 kWh/route aux) | small | "Stop time includes the PTO time (non-VECTO option)." |
| D12 | HVAC from the thermal model replaces the table (other job); no aux while charging (VECTO has no charging) | – | – |

## 10. Part H: parser jobs
| Job | Why | Source |
|---|---|---|
| Look up ES, PS (`_el`), HVAC, SP (baseline × axle rows 1…n × tech), Cond by group, mission (non-EMS), technology | engines take W only | [VECTO] tables, `vecto_aux_reimpl.py` |
| Allow only PEV technologies (`PEV = 1`) for PS and SP; ES 2 techs; HVAC None/Default; blank/`---` cell → clear error listing group/mission | VECTO throws | [VECTO] `sweep_empty_or_invalid.csv` |
| Reject > 4 steered axles; pass SP-Axles rows 1…n (n-th axle) | `SP-Axles.csv` has rows 1–4 | [VECTO] `SteeringPump.cs:77-80` |
| Mission must exist for the group (`SegmentTable.csv`): Municipal only groups 4, 9, 11 | else the lookup is meaningless | [VECTO] |
| Pass the five factors (0.7 / 1.0 / 1.25 / 0.7 / 1.0); `HVAC_eff = 1.0` for thermal-model HVAC | engine purity | [VECTO] `DeclarationData.cs` |
| kW → W for `.vptoel` and `PTO_Power`; entered ÷ efficiency; efficiency in (0, 1] | engine takes W | [VECTO] `DrivingCycleDataReader.cs:841` |
| Profile times whole seconds, strictly increasing, finite, W ≥ 0; "no profile" = one point | `pto_engine` truncates | [TEST] |
| `is_on` 0/1, length = waypoints; depot 0; `is_on = 1` at a 0 s marker only with a drive part | old/new interface | [TEST] |
| Stop extension: standing = stop + PTO duration; optional non-VECTO max() flagged | VECTO rule | [VECTO] `:218-220` |
| Reject two stop waypoints at one distance; distances non-decreasing; check driver `S` equals `wp_s` (tolerance 1e-3 m) | row matching | [TEST] |
| Drive-profile overlap check (or leave to the engine) and warn if a drive profile runs past the end of the route | VECTO error | [VECTO] `PTODriveAuxiliary.cs:26` |
| Label every custom aux value "non-VECTO" and every PTO profile with source and tag | rule 2 | – |
| Declared mechanical PTO type → warn: transmission drag not modelled | Q10 | [VECTO] |

## 11. Part I and J
Part I: `reference/vecto/jobs/aux-pto-2026-11/` (README + 2 vehicles + 2 jobs). Group-2 E2 never runs Municipal; the files raise `MassMax` to 18 t (group 4). **Untested in VECTO** [OPEN].
Part J: `docs/explainers/aux-and-pto-explained.md`.

## 12. How to run, determinism, files
```
python3.11 -m venv .venv-aux && .venv-aux/bin/pip install numpy pandas matplotlib pytest scipy pypdf cryptography
git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/VECTO.git vecto-src   # .git suffix needed in this sandbox; sparse checkout is fine
cd docs/research/aux-pto-review-2026-11
VECTO_SRC=/projects/sandbox/vecto-src python _load_notebook.py   # prints the 14 functions loaded
python run_gate3.py; python run_part_a_tables.py; python run_part_b_sweep.py; python run_part_c.py; python run_part_d.py
python run_part_d_timing.py   # machine-dependent
python run_part_f.py; python make_summary.py
cd ../../.. && pytest tests/aux_pto
```
Determinism [TEST]: every script except `run_part_d_timing.py` was run twice; the 18 CSVs and the PNG (19 files) were byte-identical (md5sum). Timing differs by nature.

## 13. Seen in passing (out of scope; file and line only)
- `src/engine/consumption.py:26` default `eta_dcdc=0.98` (VECTO: 1.0, `DeclarationData.cs:124`); the file is not the notebook version.
- Notebook `driver_model` defaults `lac_min_v=50.0`, `os_min_v=50.0`, `os_allowed=2.5`, `v_min_coast=5.0` are km/h-sized while speeds are m/s (cell 4 signature): coasting never switches on with defaults (PR #30 finding; I used the m/s values).
- `P_aux` cannot take an array-valued efficiency (e.g. an hourly COP), `if e <= 0` (cell 9).
- `consumption_engine` parameter name `regen_effeiciency` (typo, cell 16).

## 14. Choices I made
1. Used `b8d6126` as the VECTO source although the `.vmod` header says 5.1.6-RC (no 5.1.6 tag was available to me).
2. Reconstructed "speed at the start of a row" from the 1 Hz averages as `v_avg − a·dt/2` (the 1 Hz `.vmod` rows are averages, `ds/v = 1.000`).
3. Motor-off proxy: P2 (best match with the `EM_E2_off` column); also the set where the notebook sets `P_trac = 0`.
4. Municipal stand-in vehicle: E2 reference vehicle with Urban aux values (group 2 has no Municipal mission) – only for the driver rows and the PTO placement, no traction energy was computed or compared.
5. Variant step 6 raises where VECTO raises (overlap) and where the data are inconsistent (no standing rows), never fills.
6. "No profile" is encoded as a one-point profile in tests (a 2-point `[0,1]/[0,0]` is a 1 s profile).
7. Sweep: HVAC "Default" for a cell that is blank is a failed lookup, as in VECTO.
8. The venv `/projects/sandbox/.venv-aux` and the clones in `/projects/sandbox/vecto-src` and `/projects/sandbox/oss-src` are outside the repo; nothing from them is committed.

## 15. Bob to fetch (could not open)
- Ban & Stipetić, "Electric Multipurpose Vehicle Power Take-Off: Overview, Load Cycles and Actuation via Synchronous Reluctance Machine", IEEE 2019, DOI 10.1109/…9007187 (scispace page `scispace.com/papers/electric-multipurpose-vehicle-power-take-off-overview-load-22neu66ch7`); ICEM 2020 PDF `bib.irb.hr:8443/1196387/download/1196387.2020_ICEM_1.pdf` (HTTP 403).
- MDPI Appl. Sci. 11(7) 3033 `mdpi.com/2076-3417/11/7/3033` (403); MDPI Smart Cities 3(3) 54 / White Rose `eprints.whiterose.ac.uk/id/eprint/165905/1/smartcities-03-00054-v2.pdf` (PDF).
- Öko-Institut `oeko.de/fileadmin/oekodoc/Real-world-data-analysis-of-battery-electric-trucks.pdf`; NREL Fleet DNA; Dollinger 2021 (battery heating ≈ 4 %).
- Chalmers `research.chalmers.se/publication/545506/file/545506_Fulltext.pdf`; SAE 2022-01-0199; MDPI WEVJ 12(1) 7, 14(5) 126.
- DOT/BTS mixer report `rosap.ntl.bts.gov/view/dot/78763/dot_78763_DS1.pdf`; TRID 1852414 (eWCV 1.85 kWh/km).
- ATP consolidated text and UNECE ECE/TRANS/WP.11/2021/21 (K, S definitions, factor 1.75); the primary sources of `claude/REPORT_tru_power_model.md`.
- GEM v4.0 user guide `nepis.epa.gov/Exe/ZyPDF.cgi?Dockey=P1015AND.pdf`; Autonomie validation `nhtsa.gov/sites/nhtsa.gov/files/anl-autonomie-vehicle-model-validation-1509.pdf`; PHEM documentation (not located).
- Regulation (EU) 2017/2400 Annex IX auxiliary tables: **no `[REG]` statement is made in this report**; the table values are cited as `[VECTO]` only. `NO SOURCE` for the physical meaning of 0.8 (HVAC), of the Cond split and of the numeric SP/Cond table values (the release notes give the method, not a measurement).

## 16. BLOCKED list
- LongHaul with HDEV driver rows (trailer) – Part C4.
- Concrete mixer and refrigerated body validation (Part F) – no sourced vehicle / ATP data.
- VECTO runs 1–3 (Part I) – Bob.
- Measured standing-aux, Cond and fleet aux share – papers not readable.
- Numbers of the drive-PTO motor efficiency – no motor map used in this job.
