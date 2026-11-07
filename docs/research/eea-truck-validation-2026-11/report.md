# EEA truck validation v2 — report (7 Nov 2026)

> **The v1 Job 3 results merged in PR #27 are superseded by this v2 run and must not be used.**
> v1's "V-C best, median −14%" came largely from harness bugs (section 3), not from the
> drivetrain methods. This v2 run rebuilt the harness to the v1 rules, passed the gate, and
> gives a very different picture. Job 1 (v1) is kept with one fix; Job 2 is extended with
> sourced answers 2.1–2.7.

## GATE: PASSED

The rebuilt harness reproduces the 3 Nov "own maps + VECTO E2 drag" result on the VECTO
GenericVehicleE2 example to within **0.03%** on every cycle (threshold 1%). So the Job 3
numbers below are **validated**. Evidence: `gate_e2.csv`, section 4.

| cycle | load | v2 harness | 3 Nov Chain-E V1 | diff |
|---|---|---|---|---|
| RegionalDelivery | reference | 1.0471 | 1.0471 | −0.00% |
| RegionalDelivery | low | 0.9887 | 0.9887 | +0.00% |
| UrbanDelivery | reference | 0.8267 | 0.8268 | −0.01% |
| UrbanDelivery | low | 0.7376 | 0.7374 | +0.03% |

## Top answers (≤15 lines)

1. **How many real e-truck configs?** 4,603 in-scope trucks → **835 configs** (834 complete),
   unchanged from v1. Job 1 fix removed the `;Total` Mode artifact; counts identical.
2. **What do the certified numbers mean?** Certified kWh/km = SoC-corrected energy ÷ charging
   efficiency η ≈ 0.995 (**grid-side**); range uses the SoC-corrected (REESS-internal) energy;
   usable kWh is the OCV integral over the **0.855** SoC window (regulation default). All proven
   from VECTO source (2.1–2.3).
3. **How close is HDEV to certified, per variant?** **V-A (today's notebook `consumption_engine`)
   median −0.5%, 44% within ±10%.** **V-B and V-C cannot run from EEA data** (no motor full-load
   curve, R7). **V-D (fixed E2 maps) +29%**, unsuitable on 760/1274 runs. Best on E-IEPC
   (−2.5%), biased high on E-IEPC-wheel (+17%).
4. **Which v1 conclusions changed?** v1's headline "no fallback within ±10%, V-C −14% best" is
   **superseded**: the −14%/−26% were harness artifacts. With the bugs fixed, V-A is near-zero
   median bias; the real finding is that **V-B/V-C cannot even run from EEA data**, and V-A's
   spread (not its centre) is what exceeds ±10%.
5. **Did the gate pass?** **Yes** (0.03%).
6. **How do OEM figures compare?** Where an OEM page gives usable kWh + range (MAN, Iveco
   S-eWay, Fuso, Scania) the derived kWh/km is within ~15% of certified; most OEM pages give no
   range+kWh pair → `[BOB]`. No matched OEM headline cites VECTO (independent). `three_way.csv`.
7. **What is missing / `[BOB]`?** CdxA bin edges; per-tyre FzISO; motor full-load curves;
   per-truck HVAC label; multi-speed gear ratios; per-vehicle ePTO. See `[BOB]` list below.

**Bottom line.** Fixing the harness moved the central error from −14/−26% to ≈0% for the one
variant EEA data can actually drive (V-A). The honest limits are now explicit: the standard/
generic motor variants (V-B/V-C) **cannot be run** without a declared full-load curve, and V-A
still has a wide per-truck spread (±20–27% at P10/P90) and a systematic high bias on wheel-motor
IEPCs. No generic option is within ±10% on every truck.

---

## Decisions Kiro made (per your instruction)

1. **Branch/PR.** PR #27 is already merged; GitHub cannot reattach commits to a merged PR. I
   kept working on `eea-truck-validation-2026-11`, rebased onto current `main`, and open a new
   PR titled "EEA truck validation v2 (supersedes #27 Job 3)". The supersede notice is at the
   top of this report and the PR.
2. **V-B/V-C = "cannot run from EEA data".** R7 says the rated point needs a full-load curve EEA
   lacks. Rather than invent `n_rated`, I return a skip with that reason for every V-B/V-C run.
   A `SENS_N_RATED` env var enables the optional sensitivity path (R7), left off by default.
3. **Tyre test load (FzISO).** Not in EEA and no truck standard exists (only the trailer 37500 N
   default). I used one sourced stand-in (ETRTO 315/70 R22.5 single load, 31300 N) for all truck
   axles and flagged it `[BOB]`; every `crr_eff` depends on it. Listed in `[BOB]`.
4. **HVAC label.** `Aux_HVAC_SystemConfiguration` is blank for all 4,603 trucks, so I used the
   VECTO **Default** HVAC row per group (not skipping the whole fleet for a universally-missing
   EEA field). Flagged.
5. **Steering-pump electric (SP arg).** Folded to 0 extra W (dominated by ES/PS); the SP-Table×
   SP-Tech split needs a per-axle electric/mech breakdown the EEA steering field doesn't fully
   pin down. Documented, small term.
6. **Municipal excluded from summary** (R12): EEA has no per-vehicle ePTO, so Municipal is
   reported separately (V-A −61.6%), not in the headline.
7. **Out-of-map threshold = 2%** marked `[proposal, Bob to decide]` in `run_hdev.py`.
8. **Air density.** VECTO uses a fixed ρ=1.188; I chose R_air=287.058, T_amb=20°C →
   p_air=99962.8 Pa so `consumption_engine`'s ρ=p/(R·T) returns 1.188 (arithmetic in R1).
9. **Gate cycle.** The 3 Nov matrix and the repo reference use the same 100 km declaration
   cycles; the gate drives those with the crosswind-corrected CdxA table the 3 Nov used.

---

## Job 1 — one fix (done)

`truck_missions.csv` collapsed `Mode`/`ResultType` with `";".join(sorted(set(...)))`. When a
value was an empty string, `sorted({"", "Total"})` joined to `";Total"`. **Fix:** drop empty
strings before the sorted-unique join (`build_test_set.py`, the two `modes`/`rts` lines).

Evidence (counts unchanged):
```
before: in-scope 4603 | configs 835 | missions 8759 | mode values ['', ';Total', 'Total']
after : in-scope 4603 | configs 835 | missions 8759 | mode values ['', 'Total']
```
**Empty Mode rows:** 3,373 of 8,759 `truck_missions.csv` rows still have an empty `mode`. This
is **not** an artifact — in the raw `missions_xev.csv`, 30,466 of 44,258 in-scope truck rows
have a genuinely blank `Mode` (only 13,792 carry `Total`). `Mode` is blank whenever the EEA
export did not stamp a mode tag; both `ResultSuccessPEVType` (CIF) and `m:ResultSuccessPEVType`
(MRF) appear with and without `Total`. We keep the blank rather than fabricate a value.

## Job 2 — sourced answers 2.1–2.7

Full detail in `certified_numbers_meaning.md` (v2 additions section). Headlines:
- **2.1** kWh/km = D13/η (`DeclarationData.cs:2064–2092`), proven. Ratio over 44,258 rows:
  8.3% below 1.0. **Two causes, separated:** the ≈0.50 extreme tail is only **4** parallel-
  string vehicles (`.Min` over strings, `BatteryData.cs:40–100`); excluding them, min rises
  0.5023→0.9820. The remaining 8.1% just-below-1.0 band is the **deltaEPSel SoC correction**
  (`CorrectedModalData.cs:50`, `BatteryElectricPostprocessingCorrection.cs:22–35`) — not
  rounding (fields are 5-decimal) and not payload weighting (spread across all payloads).
- **2.2** REESS internal loss needs the internal-resistance curve (EEA lacks it); η needs the
  same + connection resistance (EEA lacks it). Missing terms stated as **two separate** sourced
  parts: REESS +1.1–1.6% (**E2 example only**, 3 Nov) and charging +0.48% (fleet median, 1/η−1).
- **2.3** corrected window = **0.855** (`BatteryDataAdapter.cs:62–67` + `GenericSOC.csv`); v1's
  0.85375 was wrong.
- **2.4** CdxA bin edges **not found** (reg field 23 is the actual CdxA value; EEA docs have no
  table) → `[BOB]`; R10 uses VECTO standard-value CdxA.
- **2.5** `aux_per_label.csv` with sourced arithmetic (AlternatorEfficiency 0.7, HVAC 1/0.8,
  pneumatic electric from `_el` columns). HVAC config 0% filled in EEA.
- **2.6** Municipal generic ePTO mean 23.57 kW; 0 trucks flag PTO; excluded from summary.
- **2.7** `mission_setup.csv` from `SegmentTable.csv`; groups 5/10/12 are **TractorSemitrailer**
  (v1 hand-mapped them to RigidTrailer — a bug R10 fixes).

## Job 3 — harness changes (R1–R13), with evidence

**R1 — V-A calls the notebook `consumption_engine`.** `run_hdev.run_one` calls
`H.consumption_engine(...)` for V-A (returns `E_battery` at the terminals). V-B/C/D reuse the
returned `P_wheel` + `P_aux_row`. Arguments and their sources are listed at the top of
`run_hdev.py`: `m_vehicle=TotalVehicleMass`, `payload_wp=0`, `beta=0.9` (Physics.cs:51),
air density p_air/R_air/T_amb chosen so ρ=1.188 (decision 8), crosswind W1/W2 from the mission's
VECTO set (2.7), per-truck aux (2.5), efficiencies 0.95/0.95/0.98/0.95 from the 3 Nov matrix.
*Evidence:* V-A median error moved from v1 −26% to **−0.5%** (`summary_stats.md`).

**R2 — rotating inertia.** `vehicle_rrc_inertia` sums `nrWheels × axle.Inertia` from
`Wheels.csv` (twin from `axle_xev.csv`) over truck + trailer axles, exactly as
`VehicleData.cs:273–315`. `theta_red` (kg·m²) → `force_engine`; `m_red = WheelsInertia/r_dyn²`
(kg) → `driver_model`. Trailer wheel inertia uses the real trailer tyre dim from
`Body_Trailers_Weights.csv`. Motor/gearbox inertia: EEA has none → left out, listed as a gap.
*Evidence:* `m_red` column in `hdev_vs_certified.csv` (non-zero per run).

**R3 — tyres/RRC the VECTO way.** `TotalRollResistanceCoefficient = Σ share·RRC·(share·m·g/
FzISO/nrWheels)^(β−1)` over truck+trailer axles (`VehicleData.cs:297`), then
`Crr_eff = rrc_total·m^(1−β)` so the notebook's `m^β·k_roll` equals VECTO's `rrc_total·m·g`.
r_dyn from the **driven** axle (2nd axle, `VehicleData.cs` VehicleDriven). FzISO is `[BOB]`
(decision 3). Missing RRC / N-A cert / unknown tyre → **skip and list** (no default).
*Arithmetic for one run (E2 gate, mass 9589.6 kg):* rrc_total = 0.00738, Crr_eff = 0.00738×
9589.6^0.1 = 0.01788; VECTO F_roll = 0.00738×9589.6×9.80665 = 694 N; notebook
m^0.9×Crr_eff×g = 9589.6^0.9×0.01788×9.80665 = 694 N. Match. *Evidence:* `crr_eff` column.

**R4 — driver: drag table, cache key, power limit.** The invented `build_drag` is gone.
Per-variant drag: V-A zero (3 Nov matrix), V-B/V-C the 3 Nov `_stdval.Drivetrain.drag_force_old`
parameterised with the truck's ratio/r_dyn, V-D the 3 Nov `_e2_drag.build_drag_table`. **Each
variant gets its own driver run.** The driver cache key (`run_driver`) includes mission, exact
mass, crr_eff, r_dyn, m_red, a drag-table hash and a CdxA-table hash — no mass rounding, no
dropped drag/CdxA. `P_max` = EEA rated power is passed to the driver; a second max-continuous
figure is available in the vehicle data. **For Bob:** in the notebook `driver_model`, `P_max`
is applied only when `coast_on` is true (`hdev_test_module.py` ~line 309:
`if P_max is not None and coast_on`). Coasting is on in these runs (drag table passed), so the
cap is active; listed under "For Bob". *Evidence:* `run_hdev.py` `run_driver` key.

**R5 — drivetrain chains use the real loss models.** V-D uses the 3 Nov `_chain.make_chain("E")`
(E2 axle + gearbox `.vtlm` loss maps + de-normalised motor map + regen cap from the field
curve) — the exact chain that passed the gate. V-B/V-C would use the standard/bus-generic
components, but R7 blocks them on EEA data. No "motor map + constant 0.96" shortcut remains.

**R6 — gear ratios EEA doesn't have.** Multi-speed E2/E3 with no per-gear ratios → **skip V-B/
V-C and list** ("multispeed_no_gear_ratios(R6)", 344 runs). Single-speed and IEPC use the EEA
total ratio. No made-up ratios. *Evidence:* flags in `hdev_vs_certified.csv`.

**R7 — no 3000 rpm.** The rated point needs a declared full-load curve
(`GenericRatedPointHelper`); EEA has none. So **V-B/V-C's main result is "cannot run from EEA
data"** (930 runs, "no_fullload_curve(R7)"). Stated plainly. An optional, clearly-labelled
sensitivity path exists behind `SENS_N_RATED` (off by default).

**R8 — no silent clamping.** The nearest-neighbour fill is removed: maps/loss use
`LinearNDInterpolator` only; out-of-domain returns NaN. `out_of_map_share` is counted per run
(share of positive wheel energy outside the map) and written to
`hdev_vs_certified.csv`. Threshold **2% [proposal, Bob to decide]**: above it, the run's kWh/km
is withheld and flagged. *Evidence:* `*_out_of_map_share` columns.

**R9 — aux per truck.** The flat `AUX_W` is gone; per-truck ES/PS/HVAC/cond from
`aux_per_label.csv` (2.5) are passed to `consumption_engine`. EMS missions map to the base
cycle's aux. *Evidence:* `aux_ES/PS/HVAC/SP/cond` columns.

**R10 — CdxA and crosswind.** Crosswind set + CdxA + height read from `mission_setup.csv`
(`SegmentTable.csv`) at run time — groups 5/10/12 now correctly `TractorSemitrailer`. Trailer
`DeltaCdA` (`Body_Trailers_Weights.csv`, e.g. T2=1.5, ST1=0/2.1) is **added** to the vehicle
CdxA (`AirdragDataAdapter.cs:117`). No bin edges (2.4) → one run at **VECTO standard-value
CdxA**, labelled so in every column/graph; bin edges `[BOB]`.

**R11 — same basis.** No constant 0.995 divisor. `hdev_vs_certified.csv` reports
`V-*_batt_kwh_km` (terminal), `certified_kwh_km` (as published), and **two separate** missing-
term columns: `missing_charging_loss_pct` (0.48, fleet) and `missing_reess_loss_pct_e2only`
(1.1–1.6, E2 only). Not folded into a constant.

**R12 — Municipal and PTO.** Per 2.6: EEA has no per-vehicle ePTO; `consumption_engine`'s PTO
needs standstill rows we cannot place → Municipal is **excluded from the summary** and reported
separately (V-A −61.6%). `pto_W_avg=0` with the reason documented.

**R13 — follow-limit replaced.** The v1 `follow_limit_flag` is gone. Instead `cycle_dev_s`
(driver reaches cycle end kinematically; power-cap effects via `P_max`) and the R8
`out_of_map_share` are the "cannot follow" signals.

## Section 4 — gate (passed)

`gate_e2.py` drives the v2 chain (notebook `driver_model` + `force_engine` + 3 Nov Chain-E +
E2 drag) on the E2 example, Regional/Urban, reference/low, and compares to the 3 Nov Chain-E V1
numbers. **Worst |diff| 0.03%** (table above). The first gate attempt failed at ~6.5% low; the
cause was a gate-script setup error (flat CdA 4.83 instead of the velocity-dependent crosswind-
corrected CdxA table the 3 Nov used) — fixed in the gate script. The production `run_hdev.py`
already uses the crosswind engine, so it was never affected.

## Section 5 — error attribution

`error_attribution.csv` + `error_attribution_charts.png`: 6 runs (one per architecture on
Regional Delivery + the two worst-error runs), flipping one input at a time v1→v2. For V-A the
drivetrain is constant-efficiency in both v1 and v2, so the input changes (aux, inertia, RRC,
crosswind set, DeltaCdA, power cap) move the error only a few points each; the large v1→v2 swing
came from **calling `consumption_engine` correctly and honest aux/RRC**, not from any single
input. The table shows which fix moved each run and by how much.

## For Bob: notebook issues

1. **`driver_model` P_max only applies when coasting** (`hdev_test_module.py` ~line 309:
   `if P_max is not None and coast_on:`). If a run has coasting off, the power cap silently does
   nothing. Not fixed (we don't edit the notebook); flagged. In our runs coasting is on.
2. **`consumption_engine` applies SP only while moving and cond only while moving/PTO**, but
   VECTO's lorry adapter applies ES/PS/HVAC/SP/cond as `DemandType=Constant` (always). So the
   notebook under-counts SP and cond during stops vs VECTO. Not fixed; flagged.
3. **`consumption_engine` indexes W1/W2/T_amb/HVAC by cycle hour** — callers must pass 2-D
   `[hour, speed]` W1/W2 and per-hour T_amb/HVAC or it raises `IndexError` on cycles over 1 h.
   Worked around in the harness (tiling per hour); noted so Bob knows the calling contract.

## [BOB] list

1. **CdxA A1–A24 bin edges (m²)** — not in Reg. 2018/956 (field 23 is the actual value) or EEA
   docs. Used VECTO standard-value CdxA. (2.4)
2. **Per-tyre FzISO (tyre test load)** — not in `axle_xev.csv`; no truck standard exists. Used
   one ETRTO stand-in (31300 N); every `crr_eff` depends on it. (R3, decision 3)
3. **Motor full-load curves** — EEA has none → V-B/V-C cannot run. (R7)
4. **Per-gear ratios for multi-speed E2/E3** — EEA gives only the count → those runs skipped. (R6)
5. **Per-truck HVAC configuration** — `Aux_HVAC_SystemConfiguration` 0% filled → group Default
   used. (2.5)
6. **Per-vehicle ePTO profile** — EEA has none → Municipal excluded. (2.6, R12)
7. **Motor/gearbox rotating inertia** — EEA has none → left out of `theta_red`. (R2)

## How to reproduce

```
cd docs/research/eea-truck-validation-2026-11
uv venv .venv --python 3.11 && source .venv/bin/activate
uv pip install numpy scipy pandas matplotlib
export VECTO_SRC=/path/to/VECTO MPLCONFIGDIR=/tmp/mpl
python build_test_set.py            # Job 1
python build_aux.py                 # aux_per_label.csv (2.5)
python build_mission_setup.py       # mission_setup.csv (2.7)
python select_sample.py             # sample
timeout 1500 python -u gate_e2.py | tee gate_run.log   # section 4 gate
timeout 1500 python -u run_hdev.py | tee run.log        # Job 3 -> hdev_vs_certified.csv
python error_attribution.py && CHARTS=1 python -c "import error_attribution as E; E.make_charts()"
python build_three_way.py           # Job 4
python make_graphs.py               # graphs 1-5
```

VECTO source `mohgsaad-art/VECTO` (EUPL 1.2).

## Section 8 — "Done when" (evidence)

**Gate passed** — see the GATE table at the top (`gate_e2.csv`), worst 0.03%.

**Every number in `run_hdev.py` / `_drivetrains.py` is read from a file or has a source comment.**
`grep -nE "[0-9]+\.[0-9]+" run_hdev.py _drivetrains.py` — the physics literals are:
```
G = 9.80665            # DeclarationData.cs:72 GravityAccelleration
RHO_VECTO = 1.188      # DeclarationData.cs:74 AirDensity
BETA = 0.9             # Physics.cs:51 RollResistanceExponent
R_AIR = 287.058        # std dry air; T_AMB = 20 -> P_AIR = 1.188*287.058*293.15 = 99962.8 Pa
ADC_EFF_RATIO1 = 0.98 / ADC_EFF_OTHER = 0.96   # GenericBusElectricMotorData.cs 42-49
OUT_OF_MAP_THRESHOLD = 0.02   # [proposal, Bob to decide]
TR_RRC, TR_TL = 0.0055, 37500.0  # DeclarationData.cs:837/839 (trailer)
FZISO_STANDIN = 31300.0          # [BOB] ETRTO 315/70R22.5 single load
VA_* = 0.95/0.95/0.98/0.95       # 3 Nov drivetrain matrix
missing_charging_loss_pct = 0.48 # 1/eta-1, eta=0.99522 (2.1 fleet median)
```
Every other decimal is a column index, an array bound, or read from a VECTO/EEA file at run time.

**No nearest-neighbour fills, no silent defaults.**
`grep -nE "NearestND|except:|0.0055|0.489|3000|0.995|AUX_W|build_drag" run_hdev.py _drivetrains.py`:
- `NearestND`, `n_rated=3000` → **comment-only** (documenting their removal).
- `0.0055`/`37500` → **sourced** trailer constants (DeclarationData.cs:837/839), comment on prev line.
- `build_drag_table` → the **3 Nov `_e2_drag` import** (the reused sourced builder), not the
  invented v1 `build_drag` (which is deleted).
- `0.489`, `0.995`, `AUX_W`, bare `except:` → **not present**.

**Two full runs byte-identical.** `diff runA.csv runB.csv` → empty (RESULT: byte-identical).
Command and output pasted in section 3 R-work; re-verified after the r_dyn fix.

**Every skipped run is in `skipped_runs.csv`** (0 rows this run: no config was fully skipped;
V-B/V-C skips are per-variant and recorded as flags in `hdev_vs_certified.csv`, e.g.
`no_fullload_curve(R7)`, `multispeed_no_gear_ratios(R6)`).

**2.1–2.7 each have a sourced answer or "not found"** — `certified_numbers_meaning.md` v2
section (2.4 is "not found" with every URL listed).

**Every OEM value has OEM URL, date, quote and tag** — `three_way.csv` (15 configs; trade-press
figures retagged `[C]` and excluded from the derived kWh/km; `[BOB]` where no range+kWh pair).
