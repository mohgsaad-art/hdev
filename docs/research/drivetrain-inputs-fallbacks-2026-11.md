# Drivetrain inputs, safe fallbacks, and the coasting-drag table

**Owner:** Bob. **Repo:** `mohgsaad-art/hdev`. **Branch:** `drivetrain-inputs-fallbacks-2026-11`.
**Date:** 3 November 2026. **Author:** Kiro (AI).
**VECTO source read for this report:** `mohgsaad-art/VECTO`, default branch
`IEPC-experiments`, commit **`b8d6126`** (the commit named in the prompt). Where a value
was read in a different VECTO file it is tagged with the file and line.

**Tag key:** `[VECTO file:line]` read in VECTO source at `b8d6126`;
`[REG annex/point]` regulation text; `[OEM + link]` manufacturer doc;
`[STUDY + link]` external study; `[TEST script + result]` a test I ran in
`docs/research/drivetrain-inputs-fallbacks-2026-11/`; `[ASSUMPTION]` an HDEV choice with
no source. An untagged number is a defect — please flag it. **Facts** (read in a source)
and **inferences** (my reasoning) are separated in every section; inferences are
labelled **[INFERENCE]**.

---

## 0. Ten-line answer — "what must a user enter, what do we fill in, how wrong can it be?"

1. A fleet owner realistically has: **make/model, motor rated power & torque, number of
   motors, GVW, and tyre size** — all published on OEM spec sheets `[OEM]`.
2. They almost never have: **gearbox max input torque `Tmax_in`, gear ratios, axle ratio,
   motor-to-gearbox (ADC) ratio, and the motor full-load/drag curves** `[OEM][INFERENCE]`.
3. `r_dyn` is **solved**: a tyre-size string alone is enough — VECTO derives it as
   `d × f / (2π)` from a lookup table `[VECTO Wheels.cs:72]`, so this needs no user input.
4. `Tmax_in` is the dangerous one: halving it (user assumes 1 motor) **underestimates**
   energy by **5–6 %** `[TEST D4]`, and Bob's rule is HDEV must not underestimate.
5. The safe fallback for the unknown drivetrain inputs is **VECTO's own generic/example
   values** (its completed-bus generic method and its generic E2/IEPC example vehicles),
   labelled "VECTO example" in the report `[VECTO]`.
6. The **coasting-drag table** (the review's #1 fix) is now built correctly: the 22 Oct
   table dropped two loss terms and gave 0.56–0.78 kN; the corrected table gives
   **1.9–3.6 kN**, landing in VECTO's measured 2.0–3.4 kN band `[TEST D2]`.
7. Fed into the driver model, the corrected drag table pulls HDEV's Regional coast share
   from **7.8 % → 1.27 %** (VECTO 1.46 %) and overspeed seconds from **180 → 0** (VECTO 0),
   and cuts the speed RMS vs VECTO from 1.28 to **0.37 km/h** `[TEST D7]`.
8. A naive "fleet owner knows only motor torque + tyre" guess (no count, no ADC, no
   gears) **underestimates energy by 8–14 %** `[TEST D5]` — not acceptable as-is.
9. Recommendation: require the 5 easy inputs; fill the rest from VECTO generic values;
   for `Tmax_in` use `motor torque × motor count × ADC` **only when count and ADC are
   known**, otherwise a conservative (over-stated) value so energy is never under-read.
10. All of this is **parser / `defaults.py`** work. The engine only ever receives finished
    tables (`drag_v`, `drag_F`, loss maps). The only engine-side change is the already-agreed
    driver-model edit (drag table + `g = 9.80665`).

---

## Part A — Inventory: what the standard-value formulas need

### A.0 How VECTO actually applies "standard values" (important architecture fact)

**Fact.** VECTO does **not** compute the gearbox/axle/motor standard-value torque-loss
formulas inside its simulation core. For a **certified** component it reads a pre-built
loss map (`.vtlm`), efficiency map (`.vmap`) and drag curve; the standard-value formulas
(Annex VI App. 8 gearbox, Annex VII App. 3 axle, Annex Xb App. 8 motor) are applied
**upstream**, in the component certification tool, and the result is handed to VECTO as a
map `[VECTO TransmissionLossMapReader.cs:45-98]` (loss maps are read, not generated).
The electric-motor "standard values" path confirms this: `StandardValuesEmInputData`
**passes the drag curve and full-load curve through unchanged** and only synthesises
voltage levels `[VECTO ElectricMachinesDataAdapter.cs:816-884]`.

**The one exception is the completed-bus generic method** (Part C.1), where VECTO *does*
build axle/gearbox/motor data from a few inputs inside the code
(`GenericTransmissionComponentData.cs`, `GenericBusElectricMotorData.cs`).

**[INFERENCE]** So for HDEV the realistic choice is **not** "re-implement VECTO's loss
model" (there is nothing to re-implement — VECTO reads maps). It is: **build the loss
maps / drag table in the parser** from the regulation formulas or from VECTO's generic
method, hand finished tables to the engine. This is exactly the agreed P3 split.

### A.1 Inputs the standard-value formulas need, per layout

VECTO's BEV layouts `[VECTO 02-transmission-axle.md + PowertrainPosition]`:
**E2** motor + separate gearbox + axle; **E3** motor on the axle; **E4** motor in the
wheel; **IEPC** motor + gears in one unit (with or without a separate axle).

| Component | Formula / data VECTO uses when not measured | Exact source | Inputs it needs | Units |
|---|---|---|---|---|
| Gearbox (per gear) | `T_loss,in = Td0 + Td1000·n/1000 + fT·|T_in|`; `Td0 = Td1000 = 0.005·Tmax_in`; `fT` 0.04 indirect / 0.01 direct | `[REG Annex VI App. 8]`; applied upstream, VECTO reads the map `[VECTO TransmissionLossMapReader.cs]` | gear ratios, `Tmax_in`, which gear is direct (1:1) | Nm, rpm |
| Axle (generic/bus) | `Td0 = 52.5 + 15·i`; **half fixed + half·(n_out/150)** + `|T|/0.98 − |T|` | `[VECTO GenericTransmissionComponentData.cs:71-124]` + `[VECTO Constants.cs:403-417]` | axle ratio `i` | Nm, rpm |
| Angle drive (if any) | same axle output-loss map × **0.75** correction factor | `[VECTO Constants.cs:417 FactorAngleDrive]` + `GenericTransmissionComponentData.cs:46-66` | angle-drive ratio | Nm |
| Motor loss map | normalized ASM/PSM map **scaled by the rated point** of the full-load curve; k_mn table × 0.96 is the standard-value map build | `[VECTO GenericBusElectricMotorData.cs:202-215]` (de-normalize); `[REG Annex Xb App. 8 step 6]` (k_mn, ×0.96) | motor type (ASM/PSM/…), full-load curve → rated point (N, T, P), motor count | rpm, Nm, W |
| Motor drag curve | drag torque at `Tn=0.01`, `wn=1` and `wn=4`, linear in/out | `[REG Annex Xb App. 8 step 7]`; VECTO reads it `[VECTO ElectricMachinesDataAdapter.cs:882]` | rated speed, motor type/efficiency coeffs | Nm, rpm |
| IEPC | gear efficiency **0.96**, axle-gear efficiency **0.96** (if differential included), normalized IEPC map scaled by rated point | `[VECTO GenericBusIEPCData.cs:23-24, 108-131, 166-187]` | gear ratios, differential-included flag, FLD rated point | — |
| ADC (motor→gearbox) loss | **0.98** if ratio = 1, else **0.96** | `[VECTO GenericBusElectricMotorData.cs:43]` | ADC ratio | — |
| `r_dyn` from tyre | `DynamicTyreRadius = d · f / (2π)`; `d`,`f` from a tyre table | `[VECTO Wheels.cs:72]` + `[VECTO Wheels.csv]` | tyre size string | m |

Battery is out of scope (prompt §2).

### A.1 — Axle formula conflict (MUST-RESOLVE)

**Resolved from VECTO source.** The 22 Oct test used `Td0 = 70 + 20·i` (a constant, η 0.98),
and labelled it `[ASSUMP]` because the regulation text it was transcribing was
OCR-garbled `[TEST hdev_addon_std_drag_v1.py line 25]`. VECTO's **actual generic axle**,
read at `b8d6126`, is different:

```
[VECTO GenericTransmissionComponentData.cs:83-124]
  td0        = T0 + i·T1
  td0_       = td0 · 0.5          # fixed half
  td150_     = td0 · 0.5          # speed-dependent half
  lossOut(n,T) = td0_ + td150_ · n_out / td_n + |T|/η − |T|
[VECTO Constants.cs:405-415]
  T0 = 52.5 ; T1 = 15 ; td_n = 150 ; η (Efficiency) = 0.98 ; OutputSpeedStart = 50
```

So VECTO uses **`Td0 = 52.5 + 15·i`**, split half constant and half proportional to
`n_out/150 rpm`, **plus** the efficiency term `|T|/0.98 − |T|`. At `n_out = 0` VECTO uses
`OutputSpeedStart = 50 rpm` for the speed term `[VECTO …:98-100]`.

- **Which axle type?** This is VECTO's **one generic axle** used for completed-bus generic
  data and the angle-drive (× 0.75). The regulation defines per-type standard values
  (single reduction, hub reduction, single portal, etc.) in **Annex VII Appendix 3** — the
  clean EUR-Lex / circabc text for those per-type constants is **on the "Bob to fetch"
  list** (the PDF could not be fetched here; content-type blocked). What VECTO's *code*
  gives is the generic-bus axle above; it is the defensible fallback. `[REG Annex VII App. 3]` `[OPEN — exact per-type table]`
- **Effect:** replacing `70 + 20·i` with the VECTO `52.5 + 15·i` split moves the Regional
  baseline from **0.913 → 0.960 kWh/km (+5 %)** `[TEST D3]`. So the axle formula is **not**
  a detail; the VECTO form is the one to use.

### A.2 — Gearbox standard value (MUST-RESOLVE)

**Confirmed, with a caveat.** `Td0 = Td1000 = 0.005·Tmax_in`, `fT = 0.04` indirect /
`0.01` direct, is the Annex VI App. 8 AMT formula the 22 Oct test used
`[REG Annex VI App. 8]` `[TEST hdev_addon_std_drag_v1.py:std_gearbox]`. **VECTO's code does
not apply this formula** — it reads the finished gearbox loss map
`[VECTO TransmissionLossMapReader.cs:45-98]`; the formula lives in the component
certification tool (A.0). I could not read the regulation *text* for the exact `fT`
split (PDF content-type blocked) — it is on the "Bob to fetch" list. The E2 is a
2-speed **reduction** gearbox (3.86 / 1.93), so **neither gear is 1:1 direct**; both use
`fT = 0.04` `[VECTO AMT.vgbx]` `[INFERENCE]`.

### A.3 — Motor standard value (MUST-RESOLVE)

**Confirmed.** Annex Xb App. 8 **step 6** (k_mn efficiency table, × 0.96) and **step 7**
(drag curve from `Tn=0.01` at `wn=1,4`, linear) match what the 22 Oct test built
`[REG Annex Xb App. 8]` `[TEST std_motor / std_motor_drag]`. VECTO's own generic-bus motor
path takes a **normalized** ASM/PSM efficiency map and **scales it by the rated point of
the full-load curve** `[VECTO GenericBusElectricMotorData.cs:202-215, GenericBusEMBase.cs:22-35]`,
with ADC loss fixed 0.98/0.96 `[VECTO …:43]`. **Strictly required inputs** for the motor:
- the **full-load torque/speed curve** (to get the rated point N_rated, T_rated, P_rated —
  everything is scaled by it) — **required**;
- the **machine type** (ASM/ESM/RM share one normalized map; PSM has its own)
  `[VECTO GenericBusEMBase.cs:24-33]` — **required** (picks the map);
- **motor count** — **required** (scales torque/power);
- a rated *point* alone is not enough for the generic-bus method — it needs the curve
  shape, but the rated point is what scales the map `[VECTO GenericRatedPointHelper]`.

---

## Part B — Where can each input come from?

| Input | Who realistically has it | Public source? | Example values (links) | Hard for a fleet owner? |
|---|---|---|---|---|
| Motor rated power / torque | OEM spec sheet | **Yes** | see B1 | **No** |
| Number of motors | OEM spec sheet (sometimes) | Partly | eActros "two motors" `[OEM]` | Mostly no |
| GVW / vehicle class | OEM spec sheet, registration | **Yes** | 12/16/19 t (DAF XB) `[OEM]` | No |
| Tyre size | OEM spec sheet, the tyre sidewall | **Yes** | 265/70 R19.5 (E2) `[VECTO]` | **No** |
| Gearbox type / #gears | OEM spec sheet (sometimes) | Partly | Renault E-Tech "2-speed" `[OEM]` | Often |
| Gear ratios | component datasheet / MRF | **Rarely public** | VECTO E2 3.86/1.93 `[VECTO]` | **Yes** |
| Axle ratio | component datasheet / MRF | **Rarely public** | VECTO E2 2.59 `[VECTO]` | **Yes** |
| `Tmax_in` (gearbox max input torque) | gearbox certification | **No public source** | — | **Yes (hardest)** |
| ADC (motor→gearbox) ratio | component datasheet / MRF | **Rarely public** | VECTO E2 2.0 `[VECTO]` | **Yes** |
| Motor full-load / drag curve | motor certification / MRF | **No** | VECTO E2 `.vemp`/`.vemd` `[VECTO]` | **Yes** |

### B1 — OEM spec sheets for the validation-set trucks

One row per truck. All are published motor/vehicle data; **none** publishes `Tmax_in`,
gear ratios, axle ratio or ADC ratio.

| Truck | Motor power | Motor torque | # motors | Gearbox | Axle ratio | Tyre | Source |
|---|---|---|---|---|---|---|---|
| MAN eTGL (12 t) | 210 kW | 800 Nm continuous | n/s | n/s | n/s | n/s | [sustainabletruckvan](https://www.sustainabletruckvan.com/iaa-2024-man-etgl-electric-distribution-truck/) `[OEM]` |
| Renault E-Tech D | n/s | 425 Nm (per spec) | n/s | **2-speed** | n/s | n/s | [renault-trucks.pt](https://www.renault-trucks.pt/product/renault-trucks-e-tech-d-electric) `[OEM]` |
| Renault E-Tech D Wide | 370 kW peak / 260 kW cont. | n/s | n/s | n/s | n/s | n/s | [renault-trucks.de](https://www.renault-trucks.de/product/e-tech-d-wide) `[OEM]` |
| DAF XB Electric | 120 or 190 kW nominal | 950 / 1850 Nm nominal (2600 / 3500 Nm peak) | n/s | n/s | n/s | n/s | [daf.global](https://www.daf.global/en-us/trucks/new-generation-daf-xb-electric) `[OEM]` |
| Fuso eCanter | 110 kW (4.25 t) up to 185 kW (PSM) | 380 Nm (PSM variant) | n/s | n/s | n/s | n/s | [fuso-trucks.com](https://www.fuso-trucks.com/product/ecanter/6-0-tonnes-e/) `[OEM]` |
| Mercedes eActros (orig.) | 2 × 125 kW | 2 × 485 Nm | **2** | — | n/s | n/s | [autoevolution](https://www.autoevolution.com/news/mercedes-benz-introduces-the-eactros-a-200-km-heavy-duty-electric-truck-123745.html) `[OEM]` |
| Mercedes eEconic | (as eActros family) | — | — | — | — | — | [mercedes-benz-trucks.com](https://www.mercedes-benz-trucks.com/int/en/trucks/eeconic.html) `[OEM]` |

Note: the Mercedes eActros original (2 × 125 kW / 2 × 485 Nm) **is** VECTO's generic E2
reference motor `[VECTO GenericEMotor_125kW_485Nm.vemp]` — so the E2 "truth" values this
report tests against correspond to a real published truck. _Content on these pages was
rephrased for compliance with source licensing; "n/s" = not stated on the public page._

### B2 — Customer Information File (CIF) under 2017/2400

**Fact.** VECTO produces three declaration XML reports `[VECTO 10-outputs-and-reporting.md]`:
**MRF** (Manufacturer Report File — *full* component specs, incl. `MRFElectricMachineType`,
`MRFIEPCType`), **CIF** (Customer Information File — customer-facing *summary*), and **VIF**
(Vehicle Information File — primary-vehicle components for multi-stage build). The CIF a
fleet owner receives with a certified truck is a **summary**: it carries the tyre
dimension and headline energy/CO₂ numbers (the TU Graz CIF2PDF example files show e.g.
`315/70 R22.5`) `[STUDY itna.tugraz.at CIF2PDF]`, but it does **not** expose gear ratios,
`Tmax_in` or the ADC ratio — those are MRF/manufacturer detail. The exact CIF field list
(Annex IV / the ZEV amendment that added BEV fields) is on the "Bob to fetch" list (the
regulation Annex PDF could not be fetched here). `[REG Annex IV]` `[OPEN — exact CIF field list]`

**[INFERENCE]** For a **certified** truck the realistic drivetrain source is: motor
power/torque + tyre from the CIF/spec sheet, everything else from VECTO generic values.
The MRF would have it all but a fleet owner will not have the MRF.

### B3 — Tyre size → `r_dyn` (SOLVED)

**Fact.** `[VECTO Wheels.cs:72]`:
```
DynamicTyreRadius = WheelsDiameter(d) × CircumferenceFactor(f) / (2π)
```
`d` and `f` come from the tyre table `[VECTO Wheels.csv]` keyed by the tyre-size string.
For the E2 tyre **265/70 R19.5**: `d = 867 mm`, `f = 3.05` → `r_dyn = 867 × 3.05 / (2π) =
0.42086 m` `[TEST — matches harness v1.7's 0.4209]`. `f` is **3.05 for all heavy tyres**
`[VECTO Wheels.csv]`. So **a tyre-size string alone is enough** — no `r_dyn` input needed.
(The prompt's "0.867 factor" is actually `d = 867 mm` for this tyre; the real factor is
`f = 3.05`.)

### B4 — `Tmax_in` (the hard one)

**Fact.** Neither VECTO's code nor the OEM spec sheets state the gearbox max input torque
when only motor data is known. VECTO reads `Tmax_in` from the gearbox input data; there is
no formula in VECTO that derives it from motor data `[VECTO — grep: no derivation]`. The
22 Oct test assumed `Tmax_in = motors × motor max torque × ADC = 2 × 485 × 2.0 = 1940 Nm`
`[ASSUMPTION][TEST]`. I found **no** regulation point or VECTO rule that defines this.
**[INFERENCE]** The `motor torque × count × ADC` derivation is physically reasonable (the
gearbox must take at least what the motors can deliver), but it depends on **two** other
unknowns (count and ADC); when those are themselves guessed, `Tmax_in` can come out far too
low — and because `Td0 = 0.005·Tmax_in`, a low `Tmax_in` **under**-reads the gearbox drag
and therefore energy (B4 is why D4/D5 underestimate). The safe fallback is to **over-state**
`Tmax_in` when count/ADC are unknown (see Part E).

---

## Part C — Does VECTO / the regulation already have a "generic vehicle" mechanism?

### C1 — Completed-bus generic data (YES — this is the key mechanism)

**Fact.** For **completed buses**, VECTO builds full drivetrain data from a few inputs,
inside the code:
- **Motor** (`GenericBusElectricMotorData.CreateGenericElectricMotorData`): takes the
  motor **full-load curve**, **machine type** and **count**; reads a **normalized** ASM or
  PSM efficiency map (`Resources/Declaration/GenericBusData/EfficiencyMap_{ASM,PSM}_normalized.vmap`)
  and **de-normalizes it by the rated point** of the full-load curve
  `[VECTO GenericBusElectricMotorData.cs:191-215]`; ADC loss fixed **0.98** (ratio = 1) else
  **0.96** `[VECTO …:43]`; drag curve from the input `[VECTO …:50]`.
- **Axle / angle drive** (`GenericTransmissionComponentData`): builds the loss map from the
  **ratio** alone via `Td0 = 52.5 + 15·i` (A.1) `[VECTO GenericTransmissionComponentData.cs:71-124]`.
- **IEPC** (`GenericBusIEPCData`): gear efficiency 0.96, axle-gear 0.96, normalized IEPC map
  scaled by the rated point `[VECTO GenericBusIEPCData.cs]`.

**What it takes:** motor FLD + type + count, gear/axle **ratios**, ADC ratio, differential
flag. **What it fills in:** the full efficiency/loss maps and drag curves.
**Regulation point it implements:** the completed-bus generic-component method of
**Annex Xb** (standard values / simulation input parameters) `[REG Annex Xb]`.

**Can it be used for trucks?** **Legally it is a bus method** (declared for completed
buses) — say so. **Technically**, the formulas are drivetrain-agnostic (a ratio and a
rated point are all they consume), so they would run for a truck drivetrain and produce
plausible maps. **[INFERENCE]** This is the most defensible fallback source for HDEV's
truck drivetrain loss maps — it is *VECTO's own code*, not an invented model — provided it
is labelled "VECTO generic (bus method, applied to a truck)".

### C2 — Generic example vehicles

**Fact.** `Generic Vehicles/Declaration Mode/PEV/` contains only **`GenericVehicleE2`** and
**`GenericIEPC`** (the IEPC in 1-speed, 1-speed+axle, and wheel-motor variants)
`[VECTO Generic Vehicles/Declaration Mode/PEV/]`. These are **examples, not certified
vehicle data** (they ship with the tool as worked examples). **E3/E4 examples do exist,
but elsewhere:** `GenericVehicleE4` is under **Engineering Mode**
`[VECTO Generic Vehicles/Engineering Mode/GenericVehicleE4]`, and `GenericVehicleE3` /
`GenericVehicleE4` appear in **test data** (`VectoCoreTest/TestData/Integration/TimeRun/
MeasuredSpeed/` and `…/DeclarationMode/2nd_AmendmDeclMode/JSON/PEV/GenericVehicleE4`)
`[VECTO]`. So there is **no Declaration-mode E3/E4 PEV example**, but there are
Engineering-mode and test-data E3/E4 examples to read component values from.

### C3 — Segment / class tables

**Fact.** `Resources/Declaration/SegmentTable.csv` holds per-group **air-drag** defaults
(`CdxA_Default`, e.g. Group 5 = 8.7 m²) and axle **configuration** per mission, and
`Payloads.csv` holds reference payloads `[VECTO 09-vehicle-data-and-defaults.md]`. **There
is no per-vehicle-class default for drivetrain specs** — no table of default gear ratios,
axle ratios, or motor sizes by class. `Wheels.csv` gives `r_dyn` from tyre size (B3).
So: **drivetrain geometry has no class-level default in VECTO**; only air-drag, payload,
mass, and tyre data do. `[VECTO]`

### C4 — Other standards with generic e-truck drivetrain data

I could not link and quote a ready-to-use numeric generic e-truck drivetrain dataset from
NREL FASTSim / Autonomie / JRC in the search snippets (the DOE/NREL/Argonne component-sizing
papers describe *method*, not a downloadable default gear/axle/motor-loss set)
`[STUDY DOE/NREL/Argonne component sizing](https://www.mdpi.com/2032-6653/8/1/78/pdf?version=1526033110)`.
**[INFERENCE]** VECTO's own generic method (C1) is the only source I can both link and
quote with specific numbers, so it is the fallback I recommend; the others are on the
"Bob to fetch" list if an independent cross-check is wanted. _Rephrased for compliance._

---

## Part D — Fallback options and their effect (tests)

All tests: code-of-record driver model + standard-value drivetrain (`_stdval.py`) +
repo `force_engine`. E2 reference vehicle (harness v1.7 values), reference load.
**`P_aux = 0`** on purpose — this study isolates the **drivetrain**, so the kWh/km figures
are drivetrain-only and run a little below the 22 Oct full-chain numbers (which included
auxiliaries). What matters is the **direction** and the **relative** effect.
Scripts + CSVs in `docs/research/drivetrain-inputs-fallbacks-2026-11/`.
Reproduce: `VECTO_SRC=/path/to/VECTO python run_tests.py` and `… python run_d7.py`.

### D1 — Baselines reproduce the 22 Oct setup

With the **reg70** axle (what 22 Oct used) and the old drag table `[TEST D1, D1_D2_D3_*.csv]`:

| Cycle | no-drag | old-drag | 22 Oct (incl. aux) |
|---|---|---|---|
| Regional | 0.913 | 0.937 | 0.947 / 0.971 |
| Urban | 0.742 | 0.770 | 0.815 / 0.844 |

The ~1–3 % gap is explained: `P_aux = 0` here, and this uses the **real VECTO reference
CdxA table** (crosswind) rather than the 22 Oct flat handling. The **setup is the same**;
the small offset is accounted for. VECTO `.vsum`: 1.050 / 0.840 `[TEST / review]`.

### D2 — Fixing the drag table (the key correction)

**Fact.** The 22 Oct `drag_force` used only the fixed loss parts (gearbox `Td0`, `Td1000`;
axle `Td0`) **plus** the motor drag, and **dropped** (a) the gearbox `fT·|T_in|` term and
(b) the axle `(1/η − 1)·|T|` term (and, for the VECTO axle, the speed-dependent half)
`[TEST hdev_addon_std_drag_v1.py:drag_force]`. VECTO's coasting resistance reads the
component losses **at the operating point the drag itself produces**, i.e.
`(gearboxLoss + axleLoss + emDrag − iceDrag)/v` `[VECTO DefaultDriverStrategy.cs:764-769]`.
The corrected table sums the loss **powers** at that operating point and divides by speed,
exactly as VECTO does.

Drag force at the wheel, VECTO axle `[TEST D2, D2_drag_tables.csv]`:

| speed | 22 Oct (old) | corrected (D2) | VECTO measured `.vmod` (review) |
|---|---|---|---|
| 40 km/h | 0.56 kN | **1.86 kN** | ~2.0 kN |
| 50 km/h | 0.60 kN | **2.21 kN** | ~2.0 kN |
| 60 km/h | 0.65 kN | **2.56 kN** | ~2.5 kN |
| 70 km/h | 0.69 kN | **2.91 kN** | — |
| 80 km/h | 0.73 kN | **3.26 kN** | ~3.4 kN |
| 90 km/h | 0.78 kN | **3.61 kN** | ~3.4 kN |

The corrected table lands squarely in VECTO's measured **2.0–3.4 kN** band; the old table
was **3–4× too low**. kWh/km effect (VECTO axle) `[TEST D1_D2_D3_*.csv]`:

| Cycle | no-drag | +old drag | +corrected drag |
|---|---|---|---|
| Regional | 0.960 | 0.985 (+2.6 %) | **0.996 (+3.7 %)** |
| Urban | 0.747 | 0.775 (+3.7 %) | **0.793 (+6.2 %)** |
| Municipal (PTO) | 0.779 | 0.820 (+5.3 %) | **0.840 (+7.9 %)** |

### D3 — Applying the A.1 axle result

Swapping the 22 Oct `70 + 20·i` constant axle for the VECTO `52.5 + 15·i` split
`[TEST D1_D2_D3_*.csv]`:

| Cycle | reg70 (no-drag) | VECTO axle (no-drag) | Δ |
|---|---|---|---|
| Regional | 0.913 | 0.960 | **+5.1 %** |
| Urban | 0.742 | 0.747 | +0.7 % |
| Municipal | 0.773 | 0.779 | +0.8 % |

The axle formula matters most on Regional (more axle-torque-weighted driving). The VECTO
form is the sourced one and raises energy (safe direction).

### D4 / D6 — One-at-a-time sensitivity + direction check

Each input swapped for a fallback rung; corrected drag on; vs the E2 truth
`[TEST D4_D6_sensitivity.csv]`. **Flagged `UNDER` = underestimates energy (violates Bob's
rule).**

| Input | Fallback rung | Regional | Urban | Municipal | Direction |
|---|---|---|---|---|---|
| `Tmax_in` | 1 motor assumed (970) | −6.1 % | −5.1 % | −5.2 % | **UNDER** |
| `Tmax_in` | low guess (1000) | −5.9 % | −5.0 % | −5.0 % | **UNDER** |
| `Tmax_in` | conservative ×2 (3880) | +12.1 % | +10.4 % | +10.0 % | over (safe) |
| gear ratios | single-speed = top (1.93) | 0.0 % | 0.0 % | 0.0 % | ~equal |
| gear ratios | wrong single-speed (10.0) | −2.7 % | +84.6 % | +34.8 % | mixed (unstable) |
| axle ratio | example 3.08 | +6.6 % | +3.0 % | +2.7 % | over (safe) |
| axle ratio | high 4.0 | +22.3 % | +12.5 % | +12.4 % | over |
| motor count | 1 (vs 2) | +1.3 % | +6.4 % | +6.6 % | over |
| ADC ratio | none 1.0 (vs 2.0) | +1.6 % | +14.4 % | +13.0 % | over |
| ADC ratio | 3.0 | +4.7 % | −1.1 % | −1.2 % | mixed (**UNDER** urban/muni) |
| `r_dyn` | bigger tyre 315/70 R22.5 | −5.7 % | −2.3 % | −2.1 % | **UNDER** |
| `r_dyn` | smaller tyre ~0.39 | +4.3 % | +2.3 % | +2.1 % | over |

**Readings:**
- **`Tmax_in` is the single most dangerous input** — too-low values underestimate by
  5–6 %. This confirms the 22 Oct concern (1940 vs 5500 Nm moved Regional 0.947→1.150).
- **Gear ratios barely matter** *if* the gear actually used is right (single-speed = top
  gear 1.93 ≈ 0 % because the E2 drives in gear 2 for >99 % of the cycle `[TEST / review]`).
  A *wrong* ratio (10.0) is wildly off — so a plausible ratio is needed, not the exact one.
- **`r_dyn` from the wrong tyre underestimates** (a bigger tyre lowers motor speed and the
  modelled losses). Because tyre size is easy to get (B3), this should never be a fallback.
- **axle ratio, motor count, ADC** mostly over-estimate when guessed conservatively — safe.

### D5 — All fallbacks together (fleet owner minimal knowledge)

"Knows only make/model, motor power+torque, tyre size": so **count, ADC, gears, axle ratio,
`Tmax_in` are all fallbacks**. Naive rungs (count=1, ADC=1.0, `Tmax_in = torque only`,
single-speed, example axle) `[TEST D5_all_fallbacks.csv]`:

| Cycle | fallback kWh/km | truth kWh/km | error |
|---|---|---|---|
| Regional | 0.917 | 0.996 | **−7.9 %** |
| Urban | 0.683 | 0.793 | **−13.9 %** |
| Municipal | 0.751 | 0.840 | **−10.6 %** |

**This naive combination underestimates by 8–14 % — it violates Bob's rule.** The dominant
cause is `Tmax_in` set from torque alone (485 Nm vs 1940 Nm). The fix (Part E): when count
and ADC are unknown, set `Tmax_in` **conservatively high**, not from the single-motor torque.

### D7 — Drag table in the driver model vs VECTO

Rerun of the PR-#21 Part-D comparison with the corrected drag table fed into a **test-only
copy** of the driver model with the agreed edits (`drag_v=(0.0,)`, `drag_F=(0.0,)` defaults;
`coast_acc`/`coast_distance` read `interp1(v, drag_v, drag_F)`; `g = 9.80665`; inputs in
m/s). `[TEST D7, D7_driver_drag_vs_vecto.csv]`:

| Cycle | metric | no drag | old drag | **corrected drag** | VECTO |
|---|---|---|---|---|---|
| Regional | coast % | 7.80 | 4.75 | **1.27** | 1.46 |
| Regional | secs > 85 km/h | 180 | 57 | **0** | 0 |
| Regional | speed RMS vs VECTO | 1.28 | — | **0.37** | — |
| Urban | coast % | 5.17 | 3.81 | **1.52** | 2.16 |
| Urban | secs > 85 km/h | 4 | 13 | **0** | 11 |
| Urban | speed RMS vs VECTO | 2.00 | — | **0.78** | — |
| LongHaul | coast % | 4.58 | 1.07 | **0.73** | 2.39 |
| LongHaul | speed RMS vs VECTO | 1.68 | — | **1.59** | — |

**Reading:** the corrected drag table **closes the review's #1 gap**. Regional coast share
goes from 2–4× VECTO to **spot-on** (1.27 vs 1.46 %), overspeed seconds from **180 → 0**,
and speed RMS from 1.28 to **0.37 km/h**. Urban improves similarly. **LongHaul slightly
over-corrects** (HDEV now coasts a touch less than VECTO, 0.73 vs 2.39 %) — LongHaul is
dominated by steady cruise where drag matters least, and its coast share is small either
way; flagged as a minor residual, not a regression. `[TEST D7]`

---

## Part E — Recommendation

### E1 — Minimal user input set (realistic for a fleet owner)

| User enters | Why it's realistic | Everything else → |
|---|---|---|
| make / model | they know it | — |
| **motor rated power & torque** | on every spec sheet `[OEM]` | scales the motor map (VECTO generic method C1) |
| **number of motors** | usually on the spec sheet `[OEM]` | needed for `Tmax_in` and motor scaling |
| **motor type** (ASM/PSM) if known, else default PSM | sometimes stated | picks the normalized map `[VECTO]` |
| **GVW / vehicle group** | registration / spec sheet | mass, payload, CdxA default `[VECTO]` |
| **tyre size** | sidewall / spec sheet | `r_dyn` derived exactly (B3) — **no `r_dyn` input** |

**Filled in by the parser (fallback rung in brackets):**
- gear ratios → **VECTO generic / example** (E2 3.86/1.93, or a single-speed if the OEM
  says 1-speed) `[VECTO example]`; effect ≈ 0 if the operating gear is right (D4).
- axle ratio → **VECTO example 2.59** (or the completed-bus generic) `[VECTO example]`.
- ADC ratio → **VECTO example 2.0** (or 1.0 if "motor on gearbox input") `[VECTO example]`.
- `Tmax_in` → **`motor torque × count × ADC`** *when count and ADC are set*; otherwise a
  **conservative over-estimate** (do not derive from torque alone) `[derived / conservative]`.
- motor full-load/drag curve → **VECTO generic method** scaled by the rated point from the
  entered power/torque `[VECTO generic]`.

### E2 — Error band that set produces, and its direction

- With the **recommended** set (motor power/torque + count + type + GVW + tyre, everything
  else VECTO-generic), the remaining unknowns are gear/axle/ADC/`Tmax_in`. Using VECTO
  example values for those and the corrected drag table, the E2 reproduces the truth to
  within the D4 single-input bands (axle example +3 to +7 %, ADC +1 to +14 %) — i.e. the
  recommended set tends to **over-estimate** (safe) unless `Tmax_in` is derived too low.
- The **naive** set (torque only, no count/ADC) **underestimates by 8–14 %** `[TEST D5]` —
  **do not ship this**.
- Per cycle, the corrected drag table itself adds +3.7 % (Regional) / +6.2 % (Urban) /
  +7.9 % (Municipal) vs no drag `[TEST D2]`, all in the **safe (higher)** direction.

### E3 — Labelling (what the report must show the user)

| Value | Label in the report |
|---|---|
| gear ratios, axle ratio, ADC ratio (when not user-supplied) | **"VECTO example"** |
| motor efficiency/loss maps, drag curve | **"VECTO generic (bus method, applied to a truck)"** |
| `r_dyn` | **"derived from tyre size"** |
| `Tmax_in` (from torque×count×ADC) | **"derived"**; (conservative) → **"assumption (conservative)"** |
| coasting-drag table | **"from standard values"** (and note it reproduces VECTO 2.0–3.4 kN) |

### E4 — Open questions for Bob (each with options + trade-off)

1. **`Tmax_in` when count/ADC unknown.**
   (a) derive `torque × 1 × 1` → *underestimates 5–6 %, breaks the no-under rule*;
   (b) derive `torque × count × ADC` with VECTO-example count/ADC → *best estimate, small
   bias either way*; (c) conservative fixed over-estimate → *never under-reads, but inflates
   energy a few %*. **Trade-off:** accuracy vs guaranteeing no underestimate. *Recommend (b),
   fall back to (c).*
2. **Axle formula source.** (a) VECTO generic `52.5 + 15·i` (sourced in code, used here);
   (b) the per-type Annex VII App. 3 table (needs the clean regulation text). **Trade-off:**
   ship now with (a) vs wait for the exact per-type constants. *Recommend (a) now, confirm
   with (b).*
3. **Bus generic method for trucks.** (a) use it (it's VECTO's own code, drivetrain-agnostic,
   but declared for buses); (b) wait for a truck-specific generic source. **Trade-off:** a
   defensible, linkable fallback today vs legal tidiness. *Recommend (a), labelled clearly.*
4. **LongHaul slight over-correction** of the drag (D7: 0.73 vs VECTO 2.39 % coast). (a)
   accept (tiny absolute effect on a cruise-dominated cycle); (b) tune the drag at high
   speed. **Trade-off:** simplicity vs chasing < 2 % of coast share. *Recommend (a).*

### E5 — Where it lives

**Fact / confirmed.** Everything above is **parser / `defaults.py`** work:
- the parser builds the **loss maps** and the **drag table** (`drag_v`, `drag_F`) from the
  standard-value formulas / VECTO generic method / uploaded component files;
- the engine only **interpolates** finished tables.
The only engine-side change is the **already-agreed** driver-model edit (drag table +
`g = 9.80665`), prototyped here in the test-only `_driver_dragtable.py`. **No new engine
change is proposed**, and `src/engine/` is untouched in this PR. `[VECTO P3 split / review]`

---

## Bob to fetch

| Document | Why it is needed | Link |
|---|---|---|
| Reg. (EU) 2017/2400 **Annex VII Appendix 3** (axle standard torque loss, per type) | the exact per-type axle constants (single reduction / hub / portal) to confirm A.1 beyond VECTO's one generic axle | https://circabc.europa.eu/sd/a/2d14d59c-7180-4026-98d0-db0f2a61f8d6/HDV%20CO2%20certification%20ISC%20Annexes%207-11%20FINAL.pdf |
| Reg. (EU) 2017/2400 **Annex VI Appendix 8** (gearbox standard torque loss) | the exact `fT` direct/indirect split and `Tmax_in` definition (A.2) | https://circabc.europa.eu/sd/a/7e669890-a263-4908-8605-f83e32a893fb/HDV%20CO2%20certification%20Annex%206%20post%20BRP.pdf |
| Reg. (EU) 2017/2400 **Annex IV** (CIF / MRF / VIF field lists), inc. the ZEV amendment | exactly which drivetrain fields a fleet owner's CIF carries (B2) | http://data.europa.eu/eli/reg/2017/2400/2026-01-01/eng/xhtml |
| OEM **MRF / detailed datasheets** for the validation trucks | the gear/axle/ADC ratios and `Tmax_in` the public spec sheets omit (B1) | per-OEM dealer portal (e.g. dafbbi.com spec sheets) |
| NREL FASTSim / Autonomie **default HD-electric component set** | an independent generic drivetrain cross-check for C4 (snippets only here) | https://www.nrel.gov/transportation/fastsim |

## How to run everything

```bash
# from the repo root, in a venv with numpy, scipy
python -m venv .venv && . .venv/bin/activate && pip install numpy scipy
cd docs/research/drivetrain-inputs-fallbacks-2026-11
VECTO_SRC=/path/to/VECTO python run_tests.py   # D1-D6 -> D1_D2_D3_*.csv, D2_drag_tables.csv, D4_D6_sensitivity.csv, D5_all_fallbacks.csv
VECTO_SRC=/path/to/VECTO python run_d7.py       # D7 driver-model drag vs VECTO -> D7_driver_drag_vs_vecto.csv
```
`VECTO_SRC` must point at a VECTO checkout at commit `b8d6126` (only
`GenericEMotor_125kW_485Nm.vemp` is read from it, for the E2 full-load curve). The VECTO
`.vmod` files for D7 are already in `docs/research/vecto/`. Nothing imports or edits any
`src/engine/` file; the driver model is the code-of-record copy in
`tests/driver_model/reference_copy.py`, and the D7 edits live in the test-only
`_driver_dragtable.py`.
