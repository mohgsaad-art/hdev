# HDEV session record: validation against VECTO, OEMs and studies; drivetrain maps; winter physics; battery sizing (22 Oct 2026, evening)

Follows `claude/session-closeout-2026-10-22-vecto-bev-comparison.md` (same day, afternoon).

Tags used below:
- **[VECTO]**: read from the repo `mohgsaad-art/VECTO` (branch `IEPC-experiments`), file and line given, or from Bob's VECTO 5.1.6 run.
- **[SOURCE]**: external source, linked.
- **[REG]**: Regulation (EU) 2017/2400, from the project knowledge base.
- **[CALC]**: Claude's own arithmetic from sourced inputs.
- **[ASSUMP]**: an HDEV or test choice. Must be flagged in reports.
- **[DECIDED]**: Bob agreed.
- **[OPEN]**: not resolved.

**Bob's code is unchanged.** Everything here was a test, outside his engine. Section 9 lists the changes he agreed to make.

---

## 0. How Bob wants answers (said again this session)

- Plain English and short sentences. No "machine language".
- Answer **every** part of a question.
- Don't validate against one source (Öko, or VECTO alone). Use several independent sources for **every** part of the model, not only HVAC, and show how much the sources disagree among themselves.
- Getting VECTO's exact number is not validation. Agreement with independent tests, studies and OEM figures is.
- HVAC questions mean HVAC only. Battery heating is a separate topic; Cond stays a VECTO constant for now.

---

## 1. Plain answers to the core questions

**Why does a BEV need gearbox and axle losses?**
- The motor spins about 10× faster than the wheels, so there are always gears.
- VECTO's BEV layouts [VECTO, `PowertrainPosition.cs` 18–21]:
  - E2: motor + separate gearbox (our test truck);
  - E3: motor on the axle;
  - E4: motor in the wheel;
  - IEPC: motor and gears in one unit.

**Does VECTO use generic values?**
- For a certified truck, VECTO uses the maker's measured component maps. For any part the maker didn't test, it uses the EU standard-value formulas, which are built to be pessimistic [SOURCE: SR7 Lot 4 report §4.2.6].
- Mission data is the same for every truck in a vehicle group: cycles, payload, aux, HVAC.
- `GenericVehicleE2` is an example truck. Its maps are examples, not a real truck.

**Why is VECTO's HVAC "low", and ours with it?**
- VECTO is a certification tool for one standard day, so truck HVAC is a fixed table value.
- The bus SSM heat balance we borrowed counts only wall loss, body heat and sun [VECTO, `SSMRun.cs` 48–63].
- It leaves out:
  - heating the incoming fresh air (VECTO only counts the fan's electricity);
  - door openings;
  - warm-up from a cold cab.
- Our cab inputs are placeholders.
- No measured HVAC-only number for a truck cab was found. NREL's CoolCab work reports only percentage UA reductions.

**Why were OEM figures lower than HDEV?**
- Spec-sheet ranges are "up to" best cases.
- Real e-drives are more efficient than the deliberately pessimistic standard values. For example, the eActros/eEconic e-axle has no separate gearbox [SOURCE: *Renovationskørsel på el 2023*, project knowledge base].
- The route behind the claim is unknown.
- Correction I made in the chat: I had claimed spec sheets divide by the *installed* battery. There was no source for that, so I retracted it.

---

## 2. Validation sources collected (kWh/km)

| Source | Truck | Figure | Basis |
|---|---|---|---|
| [MAN eTGL](https://man.eu/uk/en/trucks/all-models/the-man-etgl/etgl.html) | **11.99 t** (same GVW as E2) | **0.69** | OEM. 160 kWh usable, up to 235 km |
| [Renault E-Tech D12](https://www.renault-trucks.com/en/newsroom/press-releases/e-tech-d12-and-d14) | 12 t | 0.80 | [CALC] 176 kWh ÷ 220 km |
| [Renault E-Tech D16](https://www.renault-trucks.de/sites/default/files/2024-09/Renault%20Trucks%20E-TECH%20D16%20MED%20P4x2_0.pdf) | 16.7 t | 1.14 | [CALC] 375 kWh gross ÷ 330 km |
| [Renault D16 test drive (Moottori)](https://moottori.fi/koeajo/maistiainen-renault-trucks-d-16-4x2-e-tech-sahkoa-jakeluliikenteeseen/) | empty | 0.80 | Trip computer |
| [DAF XB Electric](https://www.electrive.com/2023/08/24/daf-trucks-presents-the-daf-xb-electric-truck/) | 12–19 t | 0.81 | [CALC] 282 kWh ÷ 350 km |
| [Fuso eCanter](https://www.fleetnews.co.uk/truck/reviews/fuso-ecanter) | 7.49 t | 0.66 | [CALC] 66 kWh usable ÷ ~100 km |
| [Volvo FL heat test](https://www.volvotrucks.com/en-en/news-stories/stories/2022/march/volvo-electric-fl-truck-heat-test-in-australia.html) | 15 t | 0.73 | Measured, above 35 °C (Volvo press) |
| Volvo FL Electric, *Guide til Flådeejere* | – | 1.00 | 200 kWh ÷ 200 km |
| [NREL Smith Newton](https://www.energy.gov/sites/default/files/2015/10/f27/64238.pdf) | ≈10 t (older technology) | 0.79–0.87 | Measured fleet (DC) |
| [Öko-Institut eActros](https://www.oeko.de/fileadmin/oekodoc/Real-world-data-analysis-of-battery-electric-trucks-operating-in-Germany.pdf) | 19 t | 0.67 (> 60 km/h), 0.72 (20–60 km/h) | Measured medians |
| [MAN fleet average](https://www.sustainabletruckvan.com/man-electric-trucks-on-road-consumption/) | mixed | 0.90 | Measured |
| Bob's Danish regression | 18.6–64 t data | C = 0.626 + 0.0142·W, R² 0.87 | → **0.796 at 11.99 t** (extrapolated) |
| Liimatainen et al. regression | 7.5–40 t data | C = 0.592 + 0.0220·W, R² 0.74 | → **0.855 at 11.99 t** |

Notes:
- Bob's Danish data has repeated rows (4 × 44 t and 3 × 27 t), which inflates R².
- Regression slopes compare across different trucks. They are not "extra load on one truck".

**Other parts of the model:**
- **Charger + battery chain efficiency:** 82–91 %, median 85.5 % [SOURCE: [CARB Appendix G](https://ww2.arb.ca.gov/sites/default/files/barcu/regact/2019/act2019/appg.pdf)]; NREL 90 %. Depot energy is therefore 10–15 % above battery energy. [OPEN: not in HDEV]
- **Cold tyres:**
  - [Smithers](https://www.smithers.com/en-gb/resources/2026/march/taking-the-study-of-tire-rolling-resistance-to-new): rolling resistance +30–45 % at −10 °C, +60–75 % at −20 °C, vs 25 °C;
  - [ISO 28580](https://law.resource.org/pub/us/cfr/ibr/inc/iso/iso.28580.2009.pdf): Kt 0.006 for truck tyres with load index > 121, 0.010 at or below 121, valid 20–30 °C only;
  - KTH car-tyre thesis: about 1.7 %/°C of tyre temperature.
- **Battery heater:** 60–80 % of aux power on the coldest days [SOURCE: [Stanford drayage study](https://pangea.stanford.edu/ERE/pdf/OnoriPDF/Journals/128.pdf), a simulation].
- **E-bus door openings:** about 28 % of heat loss at −10 °C [SOURCE: [MDPI 2021, simulated](https://www.mdpi.com/2076-3417/11/24/11761)].
- **Cooling unit:** +0.092 kWh/km for trucks with a temperature-control unit [SOURCE: Öko].
- **Regen share, coasting drag, battery-to-wheel efficiency:** no independent measured value found anywhere. ORNL gives only a simulated "≈75 % battery-to-wheel".

---

## 3. Loss-map tests (`claude/hdev_maps_test_v1.py`, `claude/hdev_maps_test_v2.py`)

Run in Claude's workspace using Bob's v1.7 export, his `.vmod` files and the E2 component files.

**Method check:** the maps applied to VECTO's own rows reproduce VECTO's loss columns:
- axle −0.7 / −1.0 %;
- gearbox −0.1 / −0.9 %;
- motor +0.3 / −1.3 %.

Lookup as in VECTO [VECTO, `TransmissionLossMap.cs` 77, 94; `EfficiencyMap.cs` 23].

**HDEV rows with each drivetrain** (gear from VECTO by distance; kWh/km at battery terminals):

| Drivetrain | Regional | Urban |
|---|---|---|
| Fixed 0.95/0.95/0.98 (before) | 0.712 | 0.574 |
| VECTO example maps | 1.012 | 0.787 |
| **All EU standard values** (Tmax_in 1940 Nm) | **0.947** | **0.815** |
| All standard, Tmax_in 5500 Nm (sensitivity) | 1.150 | 0.950 |
| VECTO | 1.050 | 0.840 |

Findings:
- The 32 % gap to VECTO was almost all fixed drivetrain efficiency.
- The regen torque cap was never reached.
- With the maps, regen recovers 64 % / 75 % of braking energy (VECTO: 57 % / 73 %).
- VECTO used gear 2 for more than 99 % of driving (gear 1 for 45 s on Urban), so a full shift strategy is not needed.
- Standard-value losses on Regional (axle / gearbox / motor): 8.8 / 13.5 / 10.6 kWh per trip. VECTO example: 5.0 / 16.0 / 18.3.
- **The gearbox max input torque is the single most sensitive input (about ±20 %).** Spec sheets don't give it. [ASSUMP: 1940 Nm = 2 × 485 Nm × 2.0]

**Standard-value formulas used** [REG]:
- **Gearbox:** Annex VI App. 8, AMT: Td0 = Td1000 = 0.005 × Tmax_in; fT 0.04 (indirect gear), 0.01 (direct).
- **Axle:** Annex VII App. 3, single reduction: η 0.98, Td0 = 70 + 20·i. [ASSUMP: the regulation text is OCR-garbled, so the axle was built the way VECTO builds its generic axle, `GenericTransmissionComponentData.cs` 101–152, constants `Constants.cs` 403–420]
- **Motor:** Annex Xb App. 8 step 6 (ASM k_mn table, × 0.96) and step 7 (drag curve).
- **IEPC:** Annex Xb App. 9: gear drag 0.0025 × Tmax_in; fT from Annex VI 3.1.1 (η_b 0.995 × η_m 0.986 per mesh) [ASSUMP: 2 meshes]; differential Td0 = 25 + 15·i, η 0.98 for a bevel mesh.

---

## 4. Colab add-on with coasting drag (`claude/hdev_addon_std_drag_v1.py`)

- Runs after harness v1.7 in the same Colab session. Bob ran it.
- The drag goes into his `driver_model` through `P_drag_loss` as a number whose `/v` returns the drag force (a test trick only).
- The D0 "FAIL" was a false alarm: the check flagged the line where the argument is passed. The real use is `F_loss = P_drag_loss / v`.
- Standard-value coast drag: 0.63–0.85 kN at 40–90 km/h. VECTO's example drag measured from the `.vmod`: 1.43–2.05 kN.

| kWh/km | Regional | Urban | Municipal (PTO) |
|---|---|---|---|
| A: before | 0.712 | 0.574 | 2.007 |
| B: standard drivetrain | 0.947 | 0.815 | 2.262 |
| **C: B + coasting drag** | **0.971** | **0.844** | **2.305** |
| VECTO | 1.050 | 0.840 | – |

Speed trace vs VECTO (RMS difference, sampled every 10 m):
- Regional: 1.28 → 0.63 km/h;
- Urban: 2.00 → 1.27 km/h.

Coasting share: 7.8 → 4.5 % on Regional (VECTO 1.3 %). Seconds above 85 km/h on Regional: 177 → 53 (VECTO 0).

---

## 5. PTO / refuse cycle

| Source | Total kWh/km | Driving share |
|---|---|---|
| HDEV (all fixes), VECTO Municipal cycle, 12 t | 2.31 | 0.82 (PTO + other 65 %) |
| [VTT Finland](https://www.vttresearch.com/en/project_news/refuse-truck-future-hums-along-quietly-without-emissions), measured (weight not stated) | 2.3 | 1.4 (other 39 %) |
| Frederiksberg PVI 26 t [CALC] | ≥ 2.1 | – |

- The totals agree, but the splits differ. A proper normalisation isn't possible: no weight or lifts per km are given.
- VECTO has no Municipal mission for group 2. It would need an engineering-mode run. [OPEN]
- Proper refuse-truck test standard: [ISO 24162:2022](https://www.iso.org/standard/77958.html).

---

## 6. Slopes (standard drivetrain)

| | HDEV Regional | HDEV Urban | VECTO | Öko measured |
|---|---|---|---|---|
| Payload, kWh/km per t | 0.029 | 0.048 | 0.025 / 0.040 | 0.018 |
| Payload, % per t | 3.1 | 5.9 | 2.4 / 4.8 | 1.9 |
| Temperature, % per °C (before the winter pieces) | −0.25 | −0.29 | 0 | −1.35 |

- **Payload:** HDEV ≈ VECTO. VECTO is the regulatory method, so we follow it.
- The 10–15 % payload difference vs VECTO is my explanation, not checked with numbers: constant efficiency, the driver model run at one fixed mass, and different test points. [OPEN: needs the LowLoading `.vmod`]

---

## 7. Winter + battery test (`claude/hdev_winter_test_v1.py`, `claude/hdev_winter_test_v2.py`)

Uses DMI 2025 trip temperatures (Regional, 07:00 departure): mean 9.3 °C, January 2.5 °C, July 17.9 °C, minimum −6.3 °C.

**Pieces added:**
1. air density from temperature;
2. cold tyres via ISO 28580, Kt 0.006 [ASSUMP: used outside 20–30 °C; tyre warm-up ignored; load index > 121];
3. HVAC thermal using the harness T14 band means, placeholder cab, electric heater (heat pump as an alternative);
4. fresh-air heating: V × n × ρ × cp × (18 − T) / 0.93 [ASSUMP: V 6.5 m³, n 7/h, cp 1005];
5. battery losses: VECTO OCV + Ri, Ri 0.04 Ω, 648 Ah, start at 50 % SoC. It matches VECTO's own battery losses: 0.922 vs 0.920 kWh (Regional), 0.996 vs 1.025 kWh (Urban).

**Effect of each piece at −5 °C** (kWh/km, Regional / Urban):

| Step | Regional | Urban |
|---|---|---|
| Base | 1.016 | 0.861 |
| + battery losses | 1.026 | 0.872 |
| + HVAC | 1.044 | 0.916 |
| + fresh air | 1.051 | 0.932 |
| + cold tyres | **1.096** | **0.974** |

**Final values (all pieces on):**

| | EU std E2, Regional | Modern e-axle (IEPC std), Regional | EU std E2, Urban | Modern e-axle (IEPC std), Urban |
|---|---|---|---|---|
| 24 °C reference | 0.979 | 0.919 | 0.854 | 0.796 |
| Year mean | 1.030 | 0.970 | 0.901 | 0.842 |
| January | 1.060 | 0.999 | 0.935 | 0.876 |
| Design day (coldest 5 % of days) | 1.074 | 1.013 | 0.950 | 0.891 |

- HDEV vs VECTO at reference, with battery losses on both sides: Regional −7.8 %, Urban +0.2 %.
- Winter swing (January vs July): +6.5 % / +8.3 %. At −5 vs 24 °C: +12 % / +14 %. Measured data says more (Öko ≈ +21 % for the same January–July gap; e-buses +14 to +45 %). **Winter is still short.**
- Still missing:
  - battery heating (≈ 4 % of winter consumption, [Dollinger & Fischerauer 2021](https://www.mdpi.com/1996-1073/14/18/5804), a model study);
  - the battery's Ri rising in the cold (no source yet);
  - door openings;
  - snow and slush;
  - Cond thermal.

---

## 8. Battery sizing for one day (~100 km)

Rule: kWh/km × 100 km × 1.1 (weather) ÷ 0.8 (SoC window). HDEV uses its design day and skips the 1.1, because weather is already modelled.

| System | Regional battery | Urban battery |
|---|---|---|
| VECTO (example truck) | 146 kWh | 117 kWh |
| HDEV, EU standard drivetrain + winter | 134 kWh | 119 kWh |
| HDEV, modern e-axle (IEPC std) + winter | 127 kWh | 111 kWh |
| Bob's Danish fit | 110 kWh | 110 kWh |
| Liimatainen fit | 118 kWh | 118 kWh |
| MAN eTGL claim (0.69) | 95 kWh | 95 kWh |
| Renault D12 (0.80) | 110 kWh | 110 kWh |
| Volvo FL measured (0.73) | 100 kWh | 100 kWh |
| Volvo FL, fleet guide (1.00) | 138 kWh | 138 kWh |
| NREL Smith Newton (0.79–0.87) | 109–120 kWh | 109–120 kWh |

- MAN sells the eTGL with 160 kWh usable.
- **What to tell a client:**
  - Urban: about 110–120 kWh. All methods agree within about 10 %.
  - Regional: about 110–135 kWh. The deciding factor is the real drivetrain efficiency, so ask the OEM for its VECTO file or component data.
- The OEM, guide and fleet rows are consumption figures put through the formula, not real sizing decisions for this route.
- Not included: battery ageing, battery heating, cold Ri.

**[DECIDED, Bob]:** "Our ranges were actually good." Once Monte Carlo runs are added, these ranges become a confidence band.

---

## 9. Agreed changes for Bob's code (Bob builds them, one step at a time)

**Parser (`defaults.py`)**
- Standard-value gearbox map (Annex VI App. 8). Needs ratios and Tmax_in. Tmax_in must be shown to the user and labelled.
- Standard-value axle map (Annex VII App. 3). Needs axle type and ratio.
- Option for an integrated e-axle (Annex Xb App. 9).
- Standard-value motor map and drag curve (Annex Xb App. 8). Needs max torque curve, rated speed, motor type and motor count.
- Optional upload of real VECTO files (`.vemo`, `.vemp`, `.vemd`, `.vtlm`), labelled "measured".
- Store maps the VECTO way: points of (n_in, T_in − loss) → loss.
- Build a coasting-drag table (drag force at the wheels vs speed) from the same maps.

**Driver model**
- Replace the scalar `P_drag_loss` with the drag-vs-speed table, in `coast_acc` and `coast_distance`.
- Small fix: in `coast_distance`, apply `math.atan` to `grad` before `math.cos`.

**Consumption engine, step 5**
- Replace the fixed efficiencies and `regen_effeiciency` with a per-row chain: wheel → axle/differential → gearbox → motor map → electric power, for both driving and braking.
- Simple gear rule: highest gear unless the motors can't deliver the torque.
- Regen cap from the motor's generating-torque curve, instead of the fixed `P_regen_max`.
- Keep: no motor power when coasting; no regen below 5 km/h.

**Consumption engine: cold tyres** (non-VECTO, switchable, labelled)
- Rolling term × 1 / (1 + Kt × (T − 25)), with Kt as an input.

**HVAC**
- Connect `HVAC_thermal` per weather hour, with `HVAC_eff = 1.0`.
- Add the fresh-air heating term (non-VECTO, labelled).
- Replace the placeholder cab values.

**Battery engine**
- VECTO OCV + Ri with SoC tracking; loss = I²R.
- Fallback when there's no data: Annex Xb App. 10 standard values.

**Not needed:** the VECTO PEV AMT shift strategy port (956 lines); changes to `force_engine`, `payload_engine`, `pto_engine`, `P_aux` or `crosswind_engine`.

**Monte Carlo inputs later:** weather day, payload, drivetrain choice, Tmax_in, Kt, cab inputs, heater type.

**First step proposed:** the parser's standard-value drivetrain maps.

---

## 10. Open items

1. Battery heating, cold Ri, door openings, snow/slush and Cond thermal: find sources first.
2. Charger + battery chain losses (10–15 %) for depot energy.
3. Class templates with sourced standard-value inputs (Tmax_in especially).
4. VECTO engineering-mode run for Municipal + PTO, and a like-for-like OEM refuse truck figure.
5. Payload-slope split vs VECTO (needs the LowLoading `.vmod`).
6. Validation band document per truck class.
7. Calibrate on one pilot fleet's telematics data.
8. Earlier open items still stand, e.g. explaining `interp1` / `decel_distance` / `coast_distance` / `driver_model` to Bob, and "EM total rated power 500 kW" in the `.vsum`.

---

## 11. Files

**In the project:**
- `claude/hdev_maps_test_v1.py`
- `claude/hdev_maps_test_v2.py`
- `claude/hdev_addon_std_drag_v1.py`
- `claude/hdev_winter_test_v1.py`
- `claude/hdev_winter_test_v2.py`
- this file

**Bob uploaded this session** (re-upload in a new chat if needed):
- `BEV_E2_RegionalDelivery_ReferenceLoad_1Hz.vmod`
- `BEV_E2_UrbanDelivery_ReferenceLoad_1Hz.vmod`
- `hdev_outputs.zip` (v1.7)
- `hdev_addon_outputs.zip`
- `HDEV_NEW.ipynb` (current engine code, unchanged)
