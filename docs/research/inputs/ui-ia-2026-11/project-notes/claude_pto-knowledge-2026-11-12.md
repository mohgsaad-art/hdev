# PTO: everything we know (for `consumption_engine`, the parser and the PTO profile library)

Written 12 Nov 2026 at the end of the force-engine / P_aux / PTO finalisation chat. This replaces §3b of `claude/status-engine.md` where they disagree. Tags: [VECTO] read in source (`mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126`), [SOURCE] external document (full text unless marked), [CALC] Claude's arithmetic from sourced inputs, [TEST] Kiro test (PR #31), [DECIDED] Bob agreed, [OPEN].

---

## 1. How VECTO handles PTO

### 1.1 Stop PTO (electric PTO cycle, `.vptoel`)
- The PTO cycle is attached **only to the MunicipalUtility mission** in declaration mode (`DeclarationModeHeavyLorryRunDataFactory.cs:251`). Other missions get only the PTO transmission loss (§1.3). [VECTO, PR #31]
- Standing time = stop time + PTO duration (`DistanceBasedDrivingCycle.cs` 218–220). [VECTO]
- PTO runs in the middle of the stop: idle S/2, PTO, idle S/2 (3-phase, `DistanceBasedDrivingCycle.cs` 264–279; 7-phase also S/2 each side). VECTO uses half seconds; HDEV floors to whole seconds (≤ 0.5 s shift, no energy effect). [VECTO]
- Profile is sampled by **left-hold** (each value held until the next time point; last row only marks the end) (`PTOCycleController.cs` 148, 153–168). Duration = last time − first time. [VECTO]
- The `.vptoel` W is already **electric**; `P_PTO_el` is in kW in the file (×1000 at `DrivingCycleDataReader.cs:841`). [VECTO]
- Generic refuse profile `MunicipalUtility_PTO_generic.vptoel`: 23 s, 8.42 / 33.69 / 25.92 kW, **0.14993 kWh per stop**. Municipal cycle: 96 PTO stops → 14.393 kWh; standing 2 s + 23 s = 25 s. HDEV `pto_engine` reproduces this exactly. [VECTO + TEST]
- Cond is on when an EM is on **or the E-PTO is on** (`Conditioning.cs` ~86). [VECTO]

### 1.2 Drive PTO and road sweeping (engineering mode only)
- Both exist **only in engineering mode** (`PowertrainBuilderBase.cs` 322–347). Declaration runs never have them. [VECTO]
- Powertrain order for E2: axle → (angle drive) → (output retarder) → gearbox → (input retarder) → **PTO** → E2 motor (`PowertrainBuilder.cs` 745–760). [VECTO]
- The drive-PTO power demand (W) is turned into a **torque on the motor shaft**: `PowerDemand / nEng` (`PowertrainBuilderBase.cs` 343–345), added to the traction torque request (`PEVPTO.cs` `Request`: `outTorque + torqueLoss`). The motor delivers both together; electric power comes from the **motor efficiency map** at that total torque and speed. **No fixed efficiency or factor.** [VECTO]
- Applied only while a gear is engaged and the shaft turns; otherwise 0 (`PEVPTO.cs` `Request`). [VECTO]
- Drive-PTO power per step is a **time-weighted average** over the step (`PTODriveAuxiliary.cs` `PowerDemand`: Σ P·overlap / dt). So for drive PTO VECTO averages; for the stop E-PTO it left-holds. [VECTO]
- A second drive-PTO activation while one still runs throws an error (`PTODriveAuxiliary.cs:26`); a profile still running at standstill logs a warning. A profile still running at the next stop keeps running. [VECTO]
- File: table with columns `t`, `PTO_Power` [kW]; JSON keys `PTOCycleDuringDrive` (job) and `PTO.CycleDriving` (vehicle) (`DrivingCycleDataReader.cs` 1034–1048). The string `.vptor` does not appear in the source. [VECTO, PR #31]
- Road sweeping needs a min. speed or gear (`PTODriveMinSpeed`), else VECTO throws. [VECTO]

### 1.3 PTO transmission loss (mechanical PTO hardware drag)
- If the vehicle declares a PTO type, VECTO adds a **constant torque** at the same motor-shaft PTO component on **every mission**, whenever a gear is engaged and the shaft turns, whether the PTO is used or not (`PowertrainBuilderBase.cs` 352–356, `PEVPTO.cs` `AddConstant`). [VECTO]
- Values from `Resources/Declaration/VAUX/PTO-tech.csv` (column `Torque Loss`): None 0; one gearwheel above oil 0; shift claw 0.4 Nm; multi-disc clutch 2.8; multi-disc clutch + oil pump 23.9; up to 2 gear wheels 1.2 / 3.2 / 24.3; more than 2 gear wheels 1.6 / 3.6 / 24.7; additional gearmesh without disconnect clutch 11.9 Nm. [VECTO]
- Power = torque × motor shaft speed, so it grows with motor speed.
- [CALC] The same table lists a `Power Loss` of 3000 W for the 23.9 Nm type: 3000 / 23.9 = 125.5 rad/s ≈ **1200 rpm**, a diesel engine speed. An E2 motor spins several times faster, so the same torque gives several times the power. This explains Kiro's 15.8 kWh/100 km (PR #31), which Kiro itself flagged as probably too high.
- Only trucks with a **mechanical** PTO gearbox are affected. Electric PTO bodies → type "None" → 0.
- [DECIDED 12 Nov] **Parked** until Bob's VECTO run 2 (`reference/vecto/jobs/aux-pto-2026-11/`) shows what VECTO really does for a BEV. If built: one more motor-side term = parser-looked-up torque × motor speed per row (`v / r_dyn × i_total`).

---

## 2. HDEV design (decided)

### 2.1 `pto_engine`: FINAL (12 Nov, Bob's paste, `too_short` raise removed)
```python
#PTO engine
def pto_engine(stop, is_on, stop_pto_t, stop_pto_w, drive_pto_t, drive_pto_w, stop_pto_eff, drive_pto_eff):

  stop = np.asarray(stop, dtype=float) # stop time of every waypoint/row in s, 0 means no stop; this is just the stop column from vecto or custom inputs this also includes PTO usage time
  is_on = np.array(is_on, dtype=float)       # 1 = PTO on at this waypoint, 0 = off
  stop_pto_t = np.asarray(stop_pto_t, dtype=float) #pto time profile
  stop_pto_w = np.asarray(stop_pto_w, dtype=float) #pto power profile
  drive_pto_w = np.asarray(drive_pto_w, dtype=float) #drive power profile
  drive_pto_t = np.asarray(drive_pto_t, dtype=float) #drive time profile


  is_on[0] = 0 # the first waypoint is the depot: never PTO there

  # turn each profile into one power value per second
  stop_steps = np.diff(stop_pto_t).astype(int) # how many seconds each value lasts
  stop_1s = np.repeat(stop_pto_w[:-1], stop_steps) # stop PTO, W per second

  drive_steps = np.diff(drive_pto_t).astype(int)
  drive_1s = np.repeat(drive_pto_w[:-1], drive_steps) # drive PTO, W per second

  pto_dur = len(stop_1s)   # stop profile length [s]

  #assigning stop pto profiles to waypoints
  is_stop = stop > 0 # true where the vehicle stops
  stop_on = is_stop & (is_on > 0) & (pto_dur > 0) # its a stop & stop pto is on & it has stop profile

  # putting the stop PTO in the center of stops same as VECTO
  pto_start = np.full (len(stop),np.nan) # NaN = no stop profile here
  pto_start[stop_on] = np.floor((stop[stop_on] - pto_dur) / 2) # floor for odd seconds = HDEV assumption

  #apply the effeciencies
  stop_1s = stop_1s / stop_pto_eff
  drive_1s = drive_1s / drive_pto_eff

  return is_on, pto_start, stop_1s, drive_1s
```
- The parser must guarantee every PTO stop is at least as long as the profile (otherwise `pto_start < 0` is returned without error and `consumption_engine` would place it wrongly).
- Profiles → 1 W value per second by left-hold (`np.diff(t).astype(int)` + `np.repeat(w[:-1], steps)`).
- Stop PTO centred: `pto_start = floor((stop − pto_dur)/2)` (floor = HDEV choice).
- `stop_1s / stop_pto_eff`, `drive_1s / drive_pto_eff`; both efficiencies default 1.0 (= VECTO electric PTO).
- Kiro PR #31: matches VECTO for whole-second profiles; refuse 14.393 kWh exact.

### 2.2 Where PTO lands in `consumption_engine` (to build when that function is finalised)
- **Stop profile:** from the first standing row of that stop + `pto_start`. Use `M == 0` for standing rows (not `V == 0`, which gives stop + 1 rows, +4 % on a 25 s stop constant) [TEST]. Use `searchsorted` instead of the per-stop `np.where` scan (O(rows × stops); ~120 s for a year in one array vs 0.6 s) [TEST].
- **Stop constant:** on all standing rows of that stop.
- **Drive profile:** from the first moving row after the stop; keeps running past the next stop (VECTO).
- **Drive constant (sweeper):** on all moving rows until the next stop. One sweeping power per route (flagged deviation from VECTO's distance-interpolated `PTO_Power`).
- **Mechanical vs electric drive PTO [agreed 12 Nov, to build in consumption]:** one yes/no input: "does the body have its own electric motor?"
  - **No (mechanical, on the traction motor shaft, VECTO's model):** add the drive-PTO W in **step 5** at the motor side, before dividing by motor × inverter efficiency (same place as `k_rot_rotor`), so traction-motor losses apply. Exact once motor maps replace the fixed efficiencies.
  - **Yes (own electric motor):** add it in **step 6** straight to battery power.
  - `drive_pto_eff` stays 1.0; the flag decides *where*, not a guessed number.
- **Always-on PTO** (chiller, mixer drum if modelled as constant): stays in `P_aux` (`PTO_always_on / PTO_eff`).
- **Cond rule:** on while moving or PTO-active (HDEV); VECTO: EM on or E-PTO on. Decide the drive-PTO case in the consumption review.
- **Overlap:** a new drive part while one still runs → raise (VECTO throws).
- Kiro PR #31 tested step-6 variant: `docs/research/aux-pto-review-2026-11/reference_copy.py: consumption_step6_v_pto1nov` (handles markers, drive part, constants; raises where VECTO raises).

### 2.3 Known bugs to fix in `consumption_engine` step 6 (Kiro PR #31)
- Cannot take the 1 Nov `pto_engine` outputs: a 0 s marker waypoint raises "no standing rows"; `is_on = 1` with only a drive profile gives `int(NaN)`; the drive profile is dropped silently; no slot for constants.
- `V == 0` standing rows off-by-one (use `M == 0`).
- `PTO_always_on` as a per-hour array is not hour-indexed (wrong length → broadcast error; length = rows → silently row-indexed).

### 2.4 Parser jobs (all checks live in the parser, decided 12 Nov)
- Profile times whole seconds, strictly increasing, finite; W ≥ 0; "no profile" = one point. (`astype(int)` truncates silently: `t = [0, 0.5, 1]` loses 100 % of the energy.) [TEST]
- `stop_pto_eff`, `drive_pto_eff`, `PTO_eff` in (0, 1]; no NaN.
- `is_on` 0/1, one value per waypoint; depot 0; `is_on = 1` at a 0 s marker only with a drive part.
- **Stop extension**: standing = stop + PTO duration (VECTO default); optional non-VECTO "use stop time as PTO time" → max(stop, PTO), flagged. The parser must make sure no stop is shorter than the PTO (the `too_short` raise moved here).
- Reject two stop waypoints at one distance; distances non-decreasing; driver `S` equals `wp_s` within 1e-3 m.
- Read `.vptoel` and the drive-PTO table; kW → W.
- VDRI `<PTO>` mapping: 1 → stop part; 2 → drive constant (sweeping); 3 → drive profile.
- Declared mechanical PTO type → warn "transmission drag not modelled" (until §1.3 is decided).
- Label every custom PTO value "non-VECTO" and every profile with its source and tag.

### 2.5 Deviation register (client report sentences; Kiro PR #31 §9)
- PTO start floored to whole seconds: "The PTO is centred in the stop, rounded down to a whole second."
- Profiles must be whole seconds.
- One sweeping power per route: "Sweeping power is a route average."
- Same PTO power at every stop.
- Drive-PTO efficiency default 1.0 (until the mechanical/electric flag is built): "Drive-PTO power is assumed to be electric."
- No PTO transmission torque loss: "No mechanical PTO drag is modelled."
- "Use stop time as PTO time" option is non-VECTO and non-conservative (about −2 s per Municipal stop).

---

## 3. Sources for the PTO profile library

Rule: every entry needs a source, a tag (measured / simulated / approximated / rating), a licence note, and the side it describes (pump/shaft mechanical vs electric).

### 3.1 Ready
| Body | Source | What | Tag |
|---|---|---|---|
| Refuse (VECTO generic) | `MunicipalUtility_PTO_generic.vptoel` (EUPL 1.2) | 23 s, 0.14993 kWh per stop, electric | [VECTO] official default |

### 3.2 Ban & Stipetić 2019 (full text read; details in `claude/findings-ban-stipetic-epto-2019.md`)
B. Ban, S. Stipetić, ACEMP-OPTIM 2019, https://ieeexplore.ieee.org/document/9007187. Table IV: time / torque / speed cycles for refuse, concrete mixer (8 m³), vacuum, hook-loader. **Approximated from OEM documents for motor sizing, not measured.** Shaft (pump) side.
[CALC] shaft energy per cycle (linear between points / left-hold): refuse illustrated subcycle 1.45 / 1.43 kWh over 5070 s; **mixer 42.6 / 45.0 kWh over 6060 s (mean 25 kW, peak 90.5 kW)**; vacuum 1.51 kWh over 5495 s; hook-loader 0.86 / 0.90 kWh over 4011 s.
Caveats: time points on half seconds (needs per-second averaging before it can enter HDEV, see §4 item 1); no ePTO motor efficiency given; the refuse cycle is only one subcycle (full cycle from their Fig. 5).

### 3.3 Bae et al. 2018, mixer gearbox (full text read)
M.H. Bae, T.Y. Bae, D.J. Kim, "The Strength Analysis of Differential Planetary Gears of Gearbox for Concrete Mixer Truck", IOP Conf. Ser. MSE 317 (2018) 012010, doi 10.1088/1757-899X/317/1/012010.
- 8 m³ mixer; gearbox ratio 132:1; max input 397 N·m / 1320 rpm; max output 52,400 N·m.
- Table 3: **design duty spectrum** (15 years, 70 % operation, 12 h/day, 28,400 h), torque and speed at the gearbox input (hydraulic motor output) per mode. **A design load spectrum for gear life, not a measurement.**
- [CALC] power per mode (T·n·2π/60) and time share: input concrete 26.3 kW (4 %); driving 5.25 kW (41 %); normal working 16.7 kW (12 %); max working 3.9 kW (1 %); driving 1.45 kW (38 %); washing 10.9 kW (4 %). **Time-weighted mean 6.2 kW** at the gearbox input. Implied drum speeds 1–15 rpm (input rpm ÷ 132).
- **Disagreement [OPEN]:** Bae's mean (6.2 kW at gearbox input) is about **4× lower** than Ban's mixer cycle mean (25 kW at pump shaft). Hydraulic pump + motor losses cannot explain 4×. Neither is measured.
- **Third source (Volvo guide, §3.6b):** 15–20 kW while the drum rotates on the move, 40–90 kW peak at the start of discharge. That sits close to Ban and far above Bae's driving modes (1.5–5.3 kW). So **Bae is the outlier**; Ban is supported by Volvo's guidance figures. Still no measurement. If a default is needed: Ban, flagged as approximated, cross-checked against Volvo.

### 3.4 Ferraris 2001, concrete mixers (full text read)
C.F. Ferraris, "Concrete mixing methods and concrete mixers: state of the art", J. Res. NIST 106(2) 391 (2001), doi 10.6028/jres.106.016. (Ban cites it as 2012.)
- Truck mixers are reversing drum mixers. Typical drum speed for mixing **1.57 rad/s (15 rpm)**; transport of pre-mixed concrete **0.2–0.6 rad/s (2–6 rpm)** (Ferraris citing her ref. [1]). No power or energy values.
- Use: a cross-check of drum speeds (consistent with Bae's implied 1–15 rpm).

### 3.5 HIAB Multilift (OEM technical data, read)
- **XP18T** (18 t hooklift, TD-XP18T-EN-AP_130812): max operating pressure 30 MPa, recommended max oil flow 80 l/min; cycle times at recommended flow: unloading 42–49 s, loading 33–38 s, tipping 37–44 s, lowering 27–32 s, **complete cycle 139–163 s**.
- **Multilift pump & hydraulic data** (HIAB Inc. USA): power needed at recommended flow per model: XR5S 10 kW (20 l/min), XR7S/XR8S 18 kW (35 l/min), XR10S 20 kW (40 l/min), OPT15S/ULT14S 30 kW (60 l/min), ULT16S 40 kW (80 l/min), ULT21S 50 kW (100 l/min), ULT26S/ULT30S 60 kW (120 l/min); all at 30 MPa relief pressure; fixed-displacement pumps; PTO ratio 75–120 %.
- [CALC] Upper bound for one XP18T complete cycle: 80 l/min × 300 bar / 600 = 40 kW hydraulic; ÷ 0.95 (Volvo ηt, §3.6) = 42.1 kW shaft; × 139–163 s = **1.6–1.9 kWh**. This is an **upper bound** (relief pressure all the time; real working pressure is lower). Ban's hook-loader cycle (0.86–0.90 kWh) sits below it, which is consistent.
- These are ratings and cycle times, not measured energy.

### 3.6 Volvo body builder instructions, "Hydraulic system and Power take-off", FM(4)/FH(4), ENG143321495, Release 33, 10.2018 (read)
- Pump power: **N = Q·p / (600·ηt)** [kW, l/min, bar], with **ηt ≈ 0.95** overall pump efficiency ("approximately").
- Worked examples: tipper 60–80 l/min at 230 bar → [CALC] 24–32 kW shaft; general crane 80 l/min at 250 bar → [CALC] 35 kW shaft.
- **Which bodies work while driving** (clutch-independent PTO): refrigerators, hook lifts, concrete mixers, snow ploughs / sand spreaders. Clutch-dependent (parked): tipping trucks, mobile cranes, tank trucks. Useful default for stop vs drive PTO per body type.
- PTO usage above 75 kW for 15 min or more needs a specific cooling/variant (rating limit, not energy).
- Note: this is **not** Ban's ref [2]; that is §3.6b (fetched by Bob 12 Nov).

### 3.6b Volvo, "Power take-offs and hydraulic pumps: Fields of application, Calculation guide", ENG version 08, 2007-06-15 (full text read; Ban's ref [2])
- Power demand per application, "for guidance only" (Volvo's words), diesel trucks with hydraulic PTO (pump-shaft side). [SOURCE]:
  milk tanker ~10 kW; car transporter 15–20; tipper 20–60 (most common, 60 % of EU PTO applications; used for short periods); skylift 18–30, ladder 65 for short intervals; refrigerated truck just over 20 (alternator or separate engine); chemical tanker 20–30; container lift 30–60; piece-goods crane 35–70; forest crane 40–65; **refuse 30–40**; liftdumper 45–55; skip 50–65; bulk compressor 40–60; sewage/slurry pump 30–80, jet-washing ~110; **cement mixer 40–90 peak (start of discharge, drum reversing), 15–20 kW while rotating on the move and for the rest of discharge**; concrete pump up to 160, extreme 220.
- Usage hours over five years (p. 7 chart; Claude read the values off the graphic, **approximate**): tipper ~600 h (text); bulk 1000–4000 h (text); refuse roughly 1000–2300 h; mixer roughly 800–1300 h; refrigerated roughly 900–1800 h; milk tanker roughly 1100–2100 h; cranes, skip, liftdumper, ladder under ~500 h (forest crane roughly 700–1450 h); sewage and concrete pump up to ~3700 h.
- Clutch-dependent PTO = stationary only; clutch-independent = while driving too. Refuse: "some markets allow" hydraulics while moving.
- Formulas: pump displacement `Dreq = Q·1000/(z·n_eng)`, torque `M = D·p/63`, power `P = M·z·n_eng·π/30000`; worked forest-crane example 95 l/min, 250 bar → 43 kW.
- Use: **default power ranges per body type** and a duty-time sanity check. Not profiles, not measured energy.

### 3.7 Parker Hannifin, Truck Hydraulics catalogue MSG30-8200/UK (read)
- Same pump formulas: torque M = D·Δp / (63·ηhm) [Nm], power P = q·Δp / (600·ηt) [kW]; ηt = ηv·ηhm.
- Typical applications per pump series (F1: cranes, hook loaders, skip loaders, forest cranes, concrete mixers; T1: tippers; twin-flow: cranes, hook loaders, refuse; VP1: cranes with load sensing, refuse, sewage).
- **No numeric overall efficiency values were found in the text.** Any efficiency curves are images that text extraction cannot read. [OPEN: Bob could check the F1/F2 pages for curves.]

### 3.8 Other leads (from earlier reviews)
- VTT/HSY winter e-refuse truck (web page, full): 2.3 kWh/km in collection, 1.4 kWh/km driving, > 500 containers and > 120 km per day → non-driving ≈ 0.9 kWh/km [CALC]; per stop ≤ 0.216 kWh all-in. HDEV/VECTO 0.1499 kWh per stop is 0.69× that bound (n = 1, plausibility only).
- Liebherr ETM mixer (OEM sheet in repo): drum drive 125 kW peak / 60 kW continuous, 32 kWh battery (rating).
- BTS/DOT report (abstract only, rosap.ntl.bts.gov/view/dot/78763): mixer up to 4 kWh/mile incl. aux.
- Mercedes eEconic ePTO: about 52 kW max / 30 kW continuous (rating).
- Carrier Vector eCool (fridge): 19.2 kWh pack, 19 kW max continuous discharge (rating).
- MDPI Appl. Sci. 11(7) 3033 (e-HPS waste compactor): abstract only.
- Fridge physics: ATP K = W/(S·ΔT), class limits IN 0.70, IR 0.40 W/m²K; COP vs temperature not published (parked).

### 3.9 Still to fetch
- Any **measured** ePTO energy per hour or per job for mixers, refuse, hook-loaders (none found so far).
- Fallmann 2023 (reefer, from the 9 Nov tools review).

---

## 4. Open decisions for Bob (PTO)

1. **Half-second profiles (Ban, and any measured data).** Either (a) the library stores whole-second, energy-preserving resamples made once when an entry is added (method documented per entry), and `pto_engine` stays as it is; or (b) `pto_engine` does per-second averaging itself (VECTO's drive-PTO code averages over each step, `PTODriveAuxiliary.cs`, so this is VECTO-backed for drive PTO). Only (b) changes `pto_engine`.
2. **Mixer default:** Ban (25 kW mean) vs Bae (6.2 kW mean) disagree 4×; Volvo's guidance (15–20 kW on the move, 40–90 kW discharge peak) supports Ban. No measured data. Leave without a default, or use Ban flagged.
3. **Ramps vs steps** for torque/speed tables like Ban's (6 % difference on the mixer). The paper does not say.
4. **ePTO motor + inverter efficiency** for shaft-side profiles: NO SOURCE yet.
5. **PTO transmission drag** (§1.3): parked until VECTO run 2.
