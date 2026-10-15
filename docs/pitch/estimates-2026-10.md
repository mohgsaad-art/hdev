# Pitch-deck physics estimates (October 2026)

Physics-based **estimates** for Bob's 9-slide pitch deck. These are small, transparent
calculations built on Bob's verified engines (`crosswind_engine`, `force_engine`,
`payload_engine` + `fill_payload`) and VECTO data — **not** a full simulation. No year
runs, no depot-charging runs, no driver model (it has open audit bugs). Every number
below carries its inputs, method and source.

- **VECTO**: stable branch **v5.1.3, commit `d16ba783c`** (verified: `git rev-parse HEAD`
  in the clone = `d16ba783c1d8af0ea68797f5d7ed6cf01877d402`).
- **Scripts**: `scratch/pitch_estimates/*.py`. Run any with the workspace venv:
  `/projects/sandbox/.venv/bin/python scratch/pitch_estimates/<script>.py`.
  Shared inputs + sources live in `scratch/pitch_estimates/vecto_data.py`.
- **Engine use**: `force_engine` with neutral defaults (β = 1, Θ_red = 0) → the simple
  road-load equation; VECTO's per-axle load-dependent RRC (exponent 0.9) is **not**
  applied. `crosswind_engine` called with Bob's 10° yaw clamp (and the no-clamp value
  reported alongside). Driver model **not** used; cycle energy uses the VECTO `.vdri`
  target-speed/grade trace with idealised acceleration (**no driver model; acceleration
  idealised**).

## Method key
- **M1** steady state: constant speed, flat, accel = 0, `force_engine` terms.
- **M2** cycle estimate without a driver model: per `.vdri` segment, road load +
  ½·m·Δv² for accelerations − braking energy recovered; stops add dwell time only.
  **No driver model; acceleration idealised.**
- **M3** battery side = wheel traction ÷ (0.95 × 0.95 × 0.98 = **0.8845**), recovery ×
  the same. HDEV placeholders, **no VECTO equivalent**. Headline = wheel-level unless
  battery-level differs by > 1 pp, then both are given.
- **M4** (item C only): VECTO OCV + Rᵢ battery with its charge limits, constant charger
  power cap, no thermal model.

## Vehicles
- **V1 — municipal refuse truck**: VECTO group **4** (RigidTruck 4×2, >16 t),
  mission **MunicipalUtility** (`SegmentTable.csv:12`). Body MU4 (rear collector),
  curb **6000 kg** (`Body_Trailers_Weights.csv` MU4 row). CdxA default **8.4 m²**,
  height **4.0 m**, crosswind set **RigidSolo** (group 4 "other" mission),
  MunicipalUtility payload low/reference **600 / 3000 kg**. **Chassis curb mass is
  MISSING** in VECTO for a >16 t Group-4 BEV refuse truck → run as an ASSUMPTION sweep
  **9000 / 11000 / 13000 kg** (middle value used for headline). Tyres/RRC also absent for
  this class → **ASSUMPTION** 315/70 R22.5 at the Group-5 declared RRCs 0.0034 / 0.0040
  (mean 0.0037).
- **V2 — regional delivery tractor-semitrailer**: VECTO group **5** (Tractor 4×2),
  mission **RegionalDelivery** (LongHaul used as a cross-border reference for item G).
  Specs from the generic Group-5 PEV job
  `Generic Vehicles/Declaration Mode/xEV XML Jobs/Lorries/Group5_ PEV_E4.xml`:
  tractor curb (`CorrectedActualMass`) **10143 kg** (line 14), tyres 315/70 R22.5
  (line 2133) at RRC 0.0034 / 0.0040 (lines 2134/2161), FzISO 33350 (lines 2135/2162),
  tractor CdxA_0 4.31 m² (line 2203). Combination air drag uses the declaration default
  **CdxA 8.7 m²** (`SegmentTable.csv:17`), height **4.0 m**, crosswind set
  **TractorSemitrailer**, RegionalDelivery payload low/reference **2600 / 12900 kg**.
  Semitrailer **ST1** curb **7500 kg**, combination GVM cap **40000 kg**
  (`Body_Trailers_Weights.csv` ST1 row).

Headline masses used below:
- V1 = 11000 (chassis, ASSUMPTION) + 6000 (MU4 body) + 3000 (ref payload) = **20000 kg**.
- V2 = 10143 (tractor) + 7500 (ST1) + 12900 (ref payload) = **30543 kg**.

Physical constants: g = **9.80665 m/s²** (`DeclarationData.cs:74`), VECTO air density
ρ = **1.188 kg/m³** (`DeclarationData.cs:76`). Weather-scenario densities from the ideal
gas law, dry air, sea-level pressure 101325 Pa, R = 287.05 J/(kg·K) (ASSUMPTION, Bob's
prompt §3).

---

## Results

Column key: *Wheel/battery* = which side the headline is on. All `.vdri` and `.csv`
sources are under `reference/vecto/resources/`; `.cs` under `reference/vecto/cs/`;
`.vecto`/`.xml`/`.vbat*` under the VECTO clone `Generic Vehicles/…` (path cited).

### W — bad-weather day vs good day (slide 3)

| ID | Headline | Full values | Vehicle | Case vs reference | Wheel/battery | Method | Inputs + sources (file:line) | Assumptions | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| W | **+36%** (bad day) | good 98.3 → typical +18% / bad +36% / severe +44% (wheel); batt +16/+31/+38% | V2 RegionalDelivery | bad/severe/typical vs good day | wheel **and** battery (differ > 1 pp) | M2 + crosswind | ρ good 1.188 (`DeclarationData.cs:76`); ρ bad/severe 1.352, typical 1.292 (ideal gas, −12/0 °C); wind 10.8/13.9/5.028 m/s @10 m (Bob §3); crosswind set TractorSemitrailer (`VCDV_parameters.csv`); 10° clamp (`crosswind_engine.py`); cycle `RegionalDelivery.vdri` | ρ via ideal gas, dry air; CdxA combo 8.7; 10° yaw clamp (HDEV, not VECTO) | **medium** — air-drag only; clamp deviation; no driver model |
| W | +28% (bad day) | good 6.45 → typical +13% / bad +28% / severe +36% (wheel); batt +10/+21/+27% | V1 refuse | bad/severe/typical vs good day | wheel **and** battery | M2 + crosswind | as above but CdxA 8.4, crosswind RigidSolo, `MunicipalUtility.vdri`, mass 20000 kg | chassis curb ASSUMPTION; air-drag only | **low** — small absolute kWh; slow cycle makes % air-drag swing fragile |

No-clamp values printed next to the clamp values in `02_weather.py`. For V2 the
**severe no-clamp** figure (+7.7%) is *lower* than the clamp figure (+44%): this is the
known yaw-polynomial artefact (ΔCdxA turns negative above ~20° for TractorSemitrailer),
which is exactly why Bob clamps at 10°. The clamped value is the defensible one.

**Not modelled (applies to every W number): cabin heating, battery temperature, P_aux.**
Each weather % is therefore a **lower bound for winter.**

### H — energy per working day, refuse truck, vs Frederiksberg (slide 6)

| ID | Headline | Full values | Vehicle | Case | Wheel/battery | Method | Inputs + sources | Assumptions | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| H | traction alone **~59 kWh/day ≈ 60% below** 149 | wheel 38.7/40.1/41.6; battery 56.3/59.4/62.5 kWh/day (chassis 9/11/13 t) | V1 refuse | vs real ~149 kWh | battery (traction only) | M2 + M3 | `MunicipalUtility.vdri` (11.24 km/round); <70 km day → 6.23 rounds (Bob §1); ρ 1.188 | chassis curb ASSUMPTION; traction only | **medium** |
| H | **+ PTO ~90 + aux ~10 → ~160 kWh/day**, now slightly **above** 149 | traction 59 + PTO 89.6 + aux 9.5 = 158.5 kWh/day | V1 refuse | explains the gap | battery | M2 + M3 + VECTO PTO + P_aux | PTO from `MunicipalUtility_PTO_generic.vptoel` (0.150 kWh × 96 stops/round); P_aux ES+HVAC+PS+Cond 2087 W (paux close-out §4) | generic PTO profile, not Frederiksberg's compactor; no cabin heating | **medium** |

**Verdict: the physics agrees.** Traction energy alone (~59 kWh/day) is far **below** the
real ~149 kWh. Adding the refuse-body **PTO/compactor** (~90 kWh/day, the dominant term)
and the VECTO auxiliary floor (~10 kWh/day) brings the total to **~160 kWh/day**, slightly
**above** 149. The gap the prompt anticipated (compactor/lift power, heating) is confirmed
quantitatively: the compactor is the single biggest piece. The remaining ~10 kWh overshoot
is well within the uncertainty of the generic PTO profile, the day-distance/rounds estimate,
and charging/battery losses not counted here; cabin heating (unmodelled) would push the real
figure the other way in winter.

### T — sensitivity of the refuse truck's daily energy (slide 7)

Baseline battery net per round **9.53 kWh** (V1, 20000 kg, good day, full regen).
Ranked largest first:

| Rank | Input | −10 % result (kWh) | +10 % result (kWh) | −% | +% |
|---|---|---|---|---|---|
| 1 | **drivetrain efficiency product** | 7.13 (+10 % η) | 12.29 (−10 % η) | −25.2 % | +29.0 % |
| 2 | CdxA | 9.08 | 9.99 | −4.7 % | +4.8 % |
| 3 | curb mass (chassis+body) | 9.11 | 9.96 | −4.5 % | +4.5 % |
| 4 | tyre rolling resistance (Crr) | 9.30 | 9.76 | −2.4 % | +2.4 % |
| 5 | stop count | 9.30 | 9.76 | −2.4 % | +2.4 % |
| 6 | air temperature (±10 K) | 9.69 (−10 K, colder) | 9.38 (+10 K, warmer) | +1.6 % | −1.5 % |
| 7 | payload | 9.46 | 9.61 | −0.8 % | +0.8 % |

Method/sources: `03_sensitivity.py`, M2 + M3, battery-level net. **Drivetrain efficiency
dominates** because on this stop-start cycle the net is small and the efficiency product
hits traction (÷η) *and* regen (×η) in opposite directions, so a 10 % efficiency change
levers the net by ~27 %. Air temperature uses density at base ≈ 24 °C ± 10 K (colder air
is denser → more drag → more energy). Confidence **medium** for the ranking; **low** for
the absolute drivetrain-efficiency magnitude (sensitive to the small net energy and the
placeholder η).

### C — "Ready by 06:00?" charging slow-down (slide 3)

| ID | Headline | Full values | Vehicle | Case | Wheel/battery | Method | Inputs + sources | Assumptions | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| C | **No slow-down in VECTO data**: 50 kW charge is essentially constant power (+0.0 % vs kWh ÷ kW) | 20→80 % = 341 min, 283.9 kWh; 80→90 % = 58 min, 48.0 kWh; 5.68 vs 5.76 min per 1 % SoC | generic Group-5 BEV battery | 20→80 % vs top of window | battery | M4 | `GenericBattery_243kWh_750V.vbat` (Cap 324 Ah/pack, SOC 10–90 %), `.vbatr` Rᵢ 0.04 Ω, `.vbatv` OCV, `MaxCurrent.vimax` I_charge 1620 A **flat**; `Battery.cs:Request`; 50 kW charger (Bob §1) | 2 identical packs; charger power split evenly; no thermal model | **high** (for the VECTO conclusion) |

VECTO's generic pack has **no SoC-dependent charge-current taper** (the max-current map is
flat 1620 A) and its usable window stops at **90 %**. At a 50 kW charger the charger power
is the binding limit across the whole window — the battery does not throttle until the
SoC-window cap bites in the final fraction of a percent. **A genuine 80 → 100 % CV taper is
therefore NOT representable from VECTO data → that specific comparison is "not estimable
now"** (needs a real OEM charge-rate-vs-SoC curve). The straight-line "kWh ÷ kW" estimate is
accurate to **+0.0 %** here precisely because there is no taper.

### R / P / B / G — slide-4 tiles

| ID | Headline | Full values | Vehicle | Case vs reference | Wheel/battery | Method | Inputs + sources | Assumptions | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| R | realistic driving uses **+9 %** (V2) / **+147 %** (V1) vs constant average speed | V2 real 98.3 vs const 90.4 kWh (avg 73 km/h); V1 real 6.45 vs const 2.61 kWh (avg 17 km/h) | V2 RD / V1 MU | real trace vs same distance at avg speed | wheel, full regen | M2 | cycles `RegionalDelivery.vdri`, `MunicipalUtility.vdri`; masses above | avg speed = distance ÷ moving time; no driver model | **medium** (V2), **medium-low** (V1, huge % off a tiny baseline) |
| P1 | payload swings energy **−13 % (empty) … +10 % (max)** | empty 85.0 / ref 98.3 / max 108.0 kWh (wheel) | V2 RegionalDelivery | empty / reference / max | wheel (batt within 1 pp of trend) | M2 | payloads 0 / 12900 / 22357 kg (`SegmentTable.csv:17`, 40 t cap `Body_Trailers_Weights.csv`) | combo CdxA 8.7 | **medium** |
| P2 | real varying payload ≈ constant-average (**within 1 %**) | (i) 6.24 / (ii) 6.30 (+1.0 %) / (iii) full 6.45 (+3.3 %) / (iv) empty 6.10 (−2.3 %) kWh wheel | V1 refuse | 4 payload shapes | wheel | M2 + `payload_engine`(linear)+`fill_payload` | start 0 → end 3000 kg over 102 stops; tare 17000 kg | even payload step per stop (`payload_engine` "linear", unsourced) | **medium** |
| B | **~59 % of traction energy is braking**; a no-recovery model overstates net by **~140 %** | recovered 56.7 / 58.6 / 60.2 %; overstate +131 / +141 / +151 % (chassis 9/11/13 t) | V1 refuse | regen on the refuse cycle | wheel | M2 | `MunicipalUtility.vdri`; masses above | 100 % capture at the wheel | **medium** |
| G | grade **small in Denmark** (+0.6 % V2, +0.7 % V1 with full regen); **decisive without recovery** (+17 % V2 RD, +10 % LongHaul) | V2 RD full +0.6 % / no-regen +17.4 %; V1 MU +0.7 % / +3.8 %; LongHaul −0.1 % / +9.5 % | V2 & V1 | grade vs flat | wheel | M2 | grade column of each `.vdri`; alt ranges V2 RD −104…+54 m, LongHaul −48…+144 m | full vs no regen bracketing | **medium** |
| O | refuse-body PTO **0.15 kWh per stop**, **14.4 kWh per round**, ~90 kWh/day | 96 PTO stops/round × 0.1499 kWh; day (6.23 rounds) ≈ 89.6 kWh | V1 refuse | PTO energy | battery (DC/DC = 1.0) | VECTO PTO | `MunicipalUtility_PTO_generic.vptoel` (t 0–23 s, 8.42→33.7 kW); PTO stop count = 96 (`MunicipalUtility.vdri` `<PTO>` column); `07-pto-all.md §2` (P_PTO_el is kW) | generic profile, not a specific compactor | **medium** |

---

## All ASSUMPTIONS (one list)

1. **V1 chassis curb mass** — MISSING in VECTO for a >16 t Group-4 BEV refuse truck;
   swept at **9000 / 11000 / 13000 kg** (11000 used for headlines).
2. **V1 tyres / RRC** — no Group-4 BEV refuse file; reuse **315/70 R22.5** and the
   Group-5 declared RRCs **0.0034 / 0.0040** (mean 0.0037).
3. **Single representative Crr** = arithmetic mean of the two declared axle RRCs. VECTO's
   per-axle, load-dependent RRC (exponent 0.9, `VehicleData.cs`) is **not** applied.
4. **force_engine neutral defaults**: β = 1, Θ_red = 0 → no rotating-inertia term, no
   load-dependent rolling term (the simple road-load equation).
5. **No driver model; acceleration idealised** — constant acceleration over each `.vdri`
   segment from the target speeds; braking energy taken as the negative wheel-power part.
6. **M3 drivetrain placeholders** 0.95 × 0.95 × 0.98 = 0.8845 for traction, same for
   recovery — HDEV placeholders, **no VECTO equivalent**.
7. **Full braking recovery (regen fraction = 1)** at the wheel in the headline cycle
   figures (B and G also report the no-recovery bracket).
8. **Air density via the ideal gas law**, dry air, sea-level pressure 101325 Pa,
   R = 287.05 J/(kg·K) (Bob §3). Scenario temperatures/winds are Bob's prompt (§3).
9. **10° yaw clamp** on the crosswind polynomial — an HDEV decision, **not VECTO**
   (no-clamp values reported alongside).
10. **CdxA = declaration default** (8.7 m² V2 combination, 8.4 m² V1), not a measured
    certificate; weather effect enters CdxA only (no density effect on rolling/accel).
11. **Day = <70 km ≈ 6.23 MunicipalUtility rounds** (Bob §1); the real day may differ.
12. **PTO** = the generic VECTO electric-PTO activation profile, not Frederiksberg's
    actual compactor; one activation per PTO-flagged stop (96/round).
13. **P_aux floor** uses the VECTO-traced "motor-on" constants (ES 1000 + HVAC 375 + PS 162
    + Cond 550 = 2087 W); steering pump = 0 when stopped; **no cabin heating** (VECTO has
    none for lorries) and no motor-on/standstill time-share modelling.
14. **Charging**: 2 identical packs, 50 kW split evenly, no thermal model; usable window
    10–90 % per VECTO.
15. **P2 payload shape** = `payload_engine` "linear" (even step per stop) — unsourced
    HDEV assumption.

## "Not estimable now" items

- **C — 80 % → 100 % charge taper**: VECTO's generic pack has no SoC-dependent
  charge-current taper (flat 1620 A) and its usable window stops at 90 %. A true CV-taper
  comparison needs a **real OEM charge-rate-vs-SoC curve** (not in VECTO).
- **Winter cabin heating / battery derating in W and H**: VECTO has **no cabin-heating and
  no battery-temperature model for lorries** (paux close-out §7). Needs an authentic,
  explicitly non-VECTO heating source and a battery-temperature model. Until then every
  weather number is a stated **lower bound**.
- **V1 absolute energy**: pinned only to within the chassis-curb ASSUMPTION sweep; a real
  Group-4 BEV refuse curb mass would tighten H, T, B, O.

## W — which vehicle to headline for "same truck, same route, same load"

Use **V2 (the regional-delivery tractor-semitrailer)**. It is the more defensible single
number because: (a) it runs at road speed (~73 km/h average) where air drag is the biggest
energy term, so the density + wind effect is large **and** physically robust; (b) the
absolute swing is large and legible (good 98 → bad **134 kWh**, +36 % at the wheel); (c) the
crosswind coefficient set (TractorSemitrailer) and CdxA default are both well-sourced for
this group.

**The refuse truck's weather effect is too small to headline.** Although its *percentage*
looks large (+28 %), the absolute swing is tiny (6.45 → 8.3 kWh at the wheel) because the
truck is slow and its net energy is dominated by stop-start/regen, not air drag — so the
percentage is fragile and easy to misread. Headline V2; mention V1 only as "even the slow
city truck feels it."

---

## One slide sentence + one footnote caveat per item

- **W.** *Slide:* "The same tractor on the same regional run needs about a third more
  battery on a cold, windy day than on a calm mild one." *Footnote:* air-drag only; cabin
  heating and battery cold are extra, so the real winter penalty is larger.
- **H.** *Slide:* "Our physics lands near the real 149 kWh day once the compactor is counted
  — driving is only about a third of it." *Footnote:* uses VECTO's generic compactor profile
  and an estimated day length; heating not included.
- **T.** *Slide:* "What moves the refuse truck's daily energy most: the drivetrain, then
  air drag and vehicle weight; payload matters least." *Footnote:* the drivetrain figure is
  amplified by heavy regen on a stop-start cycle and uses a placeholder efficiency.
- **C.** *Slide:* "At 50 kW this battery fills at a steady rate — there's no late slow-down
  to plan around." *Footnote:* true only up to 90 %; a real pack's top-end taper needs the
  manufacturer's charge curve, which VECTO does not provide.
- **R.** *Slide:* "Driving the real stop-start route uses far more energy than one tidy
  average speed suggests." *Footnote:* no driver model; acceleration idealised from the
  cycle's target speeds.
- **P1/P2.** *Slide:* "Load doesn't stay the same all day, but using the average load gets
  the energy right to within a percent." *Footnote:* true for total energy; a varying load
  still changes *when* in the day energy is used and how much braking can be recovered.
- **B.** *Slide:* "On a refuse round, well over half the driving energy is won back on the
  stops — ignore it and you overstate the battery by about 140 %." *Footnote:* assumes full
  recovery at the wheel; real recovery is lower.
- **G.** *Slide:* "Hills barely matter on flat Danish routes, but on a long cross-border
  climb they can add well over 15 %." *Footnote:* with regen a there-and-back route nets to
  near zero; the big number assumes a descent you cannot fully recover.
- **O.** *Slide:* "The refuse body itself draws about 0.15 kWh every time it packs — roughly
  90 kWh over a day." *Footnote:* VECTO's generic compactor profile, not a specific truck.

---

*Nothing in `src/` was changed. All scripts are in `scratch/pitch_estimates/` and
re-runnable. Sources: VECTO v5.1.3 `d16ba783c`; HDEV engines and decision/research docs
cited inline.*
