# EEA certified e-trucks: test set, library draft, HDEV vs VECTO vs OEM

Bob, this is the write-up. Short version first, then detail. All work is in
`docs/research/eea-truck-validation-2026-11/`. Nothing in `src/` was changed.

## Top answers (15 lines)

1. **How many real e-truck configs can EV Scope use?** 4,603 in-scope e-trucks (ZEV N2/N3
   with a battery record). They collapse to **835 configs** (exact-duplicate, curb mass as a
   range); **834 are complete**. One Mercedes Actros row has an empty architecture field.
2. Complete configs by architecture: **751 E-IEPC** (of which 74 wheel-motor), 49 E2, 34 E3.
   9 makes, 126 make+model names. 737 of 834 complete configs use **standard-value**
   batteries; 97 measured.
3. **What do the certified numbers mean?** The certified kWh/km is **grid-side** energy =
   battery SoC energy ÷ charging efficiency (~0.995). The usable kWh is **VECTO-simulated**
   (installed × ~0.855, a regulation default SoC window), **not** an OEM figure. Both proven
   from VECTO source (see `certified_numbers_meaning.md`).
4. **How close is HDEV to certified?** Not close enough. Best variant (V-C, bus-generic maps)
   has **median error −14%** and only **27% of runs within ±10%**. V-B (EU standard maps) is
   similar. V-A (constant efficiency) is worst (−26%). V-D (fixed E2 maps) is unsuitable for
   trucks above ~250 kW.
5. HDEV is best on **measured-component E-IEPC/wheel-motor trucks** (V-C median ≈ 0-2%) and
   worst on **standard-value E2 trucks** (−30 to −39%) and the **Municipal Utility** cycle
   (−64 to −73%, where our flat aux/PTO assumption breaks).
6. **How do OEM figures compare?** Where conditions match (MAN eTGX), certified 1.27, HDEV
   1.27, OEM-derived 1.20 — all three agree. Mercedes/Volvo OEM measured figures (1.03/1.1)
   sit within ~15% of certified. OEM "up to X km" range figures overstate efficiency.
7. **What is still missing / `[BOB]` list** (section below): exact EEA CdxA bin edges;
   per-truck aux split by technology; motor full-load curves for V-B/V-C; some OEM kWh/km.

**Bottom line:** the EEA join gives EV Scope a clean, real, 835-config truck library with
certified kWh/km. But **no generic HDEV drivetrain fallback reproduces certified kWh/km
within ±10% across all architectures** — the same conclusion the 3 Nov VECTO-example matrix
reached, now confirmed on real certified trucks. To get within ±10% we need the measured
component maps, not fallbacks.

---

## Job 1 — test set and library draft

Built from the per-vehicle join files on `main` (`vehicles_xev.csv`, `missions_xev.csv`),
NOT the pre-grouped files. Rules 1–6 applied (`build_test_set.py`).

- **`truck_vehicles.csv`** — 4,603 rows, each with `complete` and `missing_fields`.
- **`truck_configs.csv`** — 835 configs (exact duplicates collapsed on the full config key;
  curb mass as min/max). Reconciles with Claude: 2,658 configs incl. curb mass, 835 excl.
- **`truck_missions.csv`** — per config × mission × payload: min/median/max certified kWh/km
  and range, vehicle count, Mode/ResultType.
- **`make_mapping.csv`** — every Make-string change (e.g. "Mercedes Benz" → "Mercedes-Benz",
  "MITSUBISHI FUSO or FUSO" → "Fuso", "DAF Trucks N.V." → "DAF"). No flagged makes
  (`##VEHICLE_MAKE##`/`added`/empty) were present in-scope.

**Settled the 355-row question.** The findings doc was unsure whether the 355 non-wheel-motor
IEPC trucks (Fuso Canter 303, IVECO S-eWay 52) needed a separate axle ratio. From
`hdv_2024_iepc.csv` (Bob added it): **all 355 have `DifferentialIncluded = true`**, so the
differential is inside the IEPC and no axle gear is needed. They are complete — no `[BOB]`.
1,420 E-IEPC "missing" axle ratios = 1,065 wheel-motor + 355 diff-included. Nothing is a gap.

**Library schema** (`library_schema_eea.md`): lists every column EEA can fill with unit,
provenance class and coverage %, and every column it cannot (charging power 0% filled for
ZEVs, chemistry, OEM usable kWh, peak power/torque, motor maps, ePTO kW, HVAC config 0%,
capacitor 0%, trailer tyres). Mode/ResultType explained: `ResultSuccessPEVType` and
`m:ResultSuccessPEVType` are the same PEV result type in CIF vs MRF; `Mode=Total` is the
whole-mission result.

## Job 2 — what the certified numbers mean

Full answers with VECTO file+line and regulation annex in `certified_numbers_meaning.md`.
Headlines:

- **kWh/km is grid-side.** Reported value = `D13 battery-SoC energy / D9 charging efficiency`
  (`DeclarationData.cs` 2064–2086; `XMLDeclarationReport.cs` 255–263). The range uses the
  battery-SoC energy, not the grid value — which is exactly why Claude's
  `kWh/km × range / usable` check gives `1/η` (median 1.0048 ⇒ η ≈ 0.995). We confirmed this
  on the data. **HDEV (battery-terminal) ÷ 0.995 = certified basis**, applied in Job 3.
- **Usable = installed × ~0.855.** GenericSOC.csv PEV window 5–95% with 5% deterioration
  gives an effective 0.0725–0.92625 window = 0.85375 (`BatteryDataAdapter.cs` 53–67). Data
  median 0.8551 — the regulation default, not an OEM number.
- **Standard values:** rated power/torque/ratio/capacity stay OEM-declared; VECTO generates
  the maps, drag curves, loss maps and SoC window (`ElectricMachinesDataAdapter.cs`,
  `BatteryDataAdapter.cs`; Annex Xb).
- **Missions → cycles, mass, CdxA, aux, tyres:** all cited (points 4–7). `TotalVehicleMass`
  already includes body + trailer + payload (`VehicleData.cs` 196–205) — so we run HDEV at
  that mass directly. Crosswind coefficients a1/a2/a3 in HDEV's `crosswind_engine` match
  VECTO's `VCDV_parameters.csv` exactly.

## Job 3 — HDEV vs certified kWh/km

- **Sample** (`sample_selection.md`, `sample_configs.csv`): 52 complete configs spread across
  all 9 makes, all 4 architectures (E2 12, E3 13, E-IEPC 17, E-IEPC-wheel 10), 11 vehicle
  groups, measured (19) vs standard (33) components, and 4 battery buckets. Each run uses the
  vehicle's own `TotalVehicleMass`; where a config has many vehicles we ran the median/min/max
  mass. 1,274 (config × vehicle × mission × payload) runs.
- **HDEV module** (`hdev_test_module.py`): a TEST-ONLY copy of the 7-Nov notebook functions
  with ONLY the four agreed fixes applied (split `v_cap` line; `drag_v`/`drag_F` replacing
  `P_drag_loss`; `g=9.80665` passed explicitly; PTO test cell ignored). Every other line is
  the notebook's.
- **Variants** (`_drivetrains.py`, `run_hdev.py`): V-A notebook constant efficiencies
  (0.95·0.95·0.98, regen 0.95); V-B EU standard-value maps (Annex VI App.8 gearbox + VECTO
  generic axle + Annex Xb motor); V-C VECTO completed-bus normalised ASM/PSM map +
  generic axle; V-D fixed E2 example maps (125 kW × 2, unscaled). For V-B/C/D traction power
  is computed from `P_wheel` with the variant drivetrain, then `+ P_aux` exactly as
  `consumption_engine` does — `consumption_engine` itself is not edited (its constant
  efficiencies are only used by V-A).
- **CdxA:** two corners per run at the VECTO group `CdxA_Default` ±10% (SegmentTable.csv;
  Construction uses `CdxA_Construction`). The exact EEA A1–A24 bin edges are a publication
  convention we could not source authoritatively (`[BOB]`); the ±10% band stands in and both
  corners are reported — we never pick one "best" CdxA.

**Results** (`hdev_vs_certified.csv`, `summary_stats.md`, graphs 1–3, 5):

| variant | median % err | 10th/90th % | within ±5% | within ±10% | cert in CdxA range |
|---|---|---|---|---|---|
| V-A | −26.0 | −68.5 / +0.4 | 6% | 13% | 7% |
| V-B | −14.9 | −52.4 / +18.5 | 15% | 25% | 13% |
| V-C | **−14.3** | −45.0 / +22.4 | **16%** | **27%** | 16% |
| V-D | −18.5 | −61.3 / +25.3 | 12% | 27% | 13% |

- **Closest variant:** V-C (bus-generic maps), narrowly over V-B. On **measured-component
  trucks** V-C median error is ≈ 0%, V-B −2.3%. On **E-IEPC wheel-motor** trucks V-B/V-C are
  within ±2% median — the best case.
- **Where it fails:** standard-value E2 trucks (−30 to −39%), the Municipal Utility cycle
  (−64 to −73%; flat aux/PTO assumption), and the heavy high-payload tractors (~2.5-3.2
  certified kWh/km, HDEV ~0.8-1.0 — the big underestimate cluster in graph 1).
- **No driver/motor follow failures** were flagged on this sample (the driver reached the end
  of every cycle; no torque/power cap stopped a run). **No runs were skipped** for missing
  inputs — every sampled config had a ratio, rated power and per-axle RRC. 0 sampled vehicles
  had a missing/N-A axle RRC.
- **Does any variant stay within ±10% on all architectures?** **No.** Even V-C is within ±10%
  median only on E-IEPC-wheel; it is −39% on E2. This matches the 3-Nov finding on VECTO
  example trucks: no fallback held ±10% everywhere.

**Why HDEV reads low.** Three stated causes: (a) a single flat per-mission aux value (we did
not split aux by each truck's pneumatic/steering/HVAC technology — a documented limitation);
(b) standard/generic motor maps scaled from rated power with an assumed `n_rated = 3000 rpm`
(flagged `[ASSUMP]` on every V-B/V-C run) rather than the real full-load curve, which EEA
does not carry; (c) the generic maps are smoother/more efficient than the real certified
components. The underestimate is systematic, not random.

## Job 4 — OEM website as third column

`three_way.csv` + graph 4. 10 OEM entries covering all makes, each with URL, date, exact
quote, and a battery+motor match check. Highlights:

| make | certified | HDEV V-C (lo..hi) | OEM kWh/km | OEM basis |
|---|---|---|---|---|
| MAN eTGX | 1.27 | 1.27 | 1.20 | `[D]` 480 kWh net / 400 km |
| Mercedes eActros 600 | 1.20 | 1.28 | 1.03 | `[V]` measured testing-tour 103 kWh/100km |
| Volvo FH Electric | 1.35 | 1.31 | 1.10 | `[V]` measured road test |
| Scania 624 kWh | 1.89 | 1.31 | 1.56 | `[D]` 624 kWh / 400 km (installed, overstates) |
| Iveco S-eWay tractor | 1.31 | 1.83 | 1.06 | `[D]` 635 kWh / 600 km |
| Fuso eCanter (L / M) | 1.00 | 0.68 | 0.62 / 0.60 | `[D]` nominal / range |

Interpretation (kept apart, as required): HDEV-vs-certified is model accuracy (same cycle,
mass, inputs); OEM-vs-certified shows how OEM conditions differ from certification (their
"up to X km" ranges overstate efficiency vs the certified mix of missions); HDEV-vs-OEM is
only meaningful where conditions match (MAN is the clean case). No column is "the truth".
No OEM page we matched cites VECTO for its headline number, so the OEM figures are
independent of certification. DAF, Renault and the Iveco eDaily pages gave no usable
kWh + range pair, so their OEM kWh/km is `[BOB]`.

## Still missing — `[BOB]` list

1. **Exact EEA CdxA A1–A24 bin edges (m²).** The regulation reports the actual CdxA value;
   the A-bins are an EEA publication band whose edges I could not source. Used VECTO group
   DefaultCdxA ±10% instead. Bob: get the EEA bin→m² table to tighten the CdxA corners.
2. **Per-truck aux split by technology.** We used one flat electric-aux total per mission.
   The VECTO VAUX tables (PS-Table/SP-Table/HVAC-Table/ES-Tech, all located) can give a
   per-truck split; wiring each truck's pneumatic/steering/HVAC label through is the next
   step and would lift the low-speed cycles (Municipal Utility, Urban).
3. **Motor full-load curves for V-B/V-C.** We assumed `n_rated = 3000 rpm` to scale the
   standard/generic maps from rated power. EEA has no full-load curve. Measured `.vemp`-style
   curves (or Annex Xb rated-speed rules per machine class) would remove this assumption.
4. **Gearbox ratios for multi-speed E2/E3 and IEPC internal gear split.** EEA gives the total
   ratio and gear count but not each gear ratio; we used a single effective ratio.
5. **OEM kWh/km for DAF XB, Renault E-Tech D, Iveco eDaily** — their pages give battery and
   power but not a usable-kWh + range pair to derive kWh/km.

## How to reproduce

```
uv venv .venv --python 3.11 && uv pip install numpy scipy pandas matplotlib
export VECTO_SRC=/path/to/VECTO MPLCONFIGDIR=/tmp/mpl
python build_test_set.py        # Job 1
python select_sample.py         # Job 3 sample
python run_hdev.py              # Job 3 runs -> hdev_vs_certified.csv
python analyze_results.py       # summary_stats.md
python build_three_way.py       # Job 4 -> three_way.csv
python make_graphs.py           # graphs 1-5
```

Scripts: `build_test_set.py`, `select_sample.py`, `_drivetrains.py`, `run_hdev.py`,
`analyze_results.py`, `build_three_way.py`, `make_graphs.py`, and the TEST-ONLY engine copy
`hdev_test_module.py`. VECTO source `mohgsaad-art/VECTO` (EUPL 1.2).
