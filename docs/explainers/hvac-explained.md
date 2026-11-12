# HVAC in HDEV, explained in plain English

*Written 12 Nov 2026 for Bob. Code of record: `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb`, cells 11 (`HVAC_thermal`), 12 (`ssm_total_w`), 13 (`climate_lookup`). Full review: `docs/research/hvac-review-2026-11.md`. All numbers in the worked example are `ILLUSTRATIVE` (made up to show the steps, not data).*

## What the three functions do

HVAC means heating, ventilation and air conditioning. HDEV needs to know how many watts the cab climate system takes from the battery in each hour of the weather year.

| Function | One-line job |
|---|---|
| `ssm_total_w` | Heat balance of the cab at one cab temperature. Positive W = the cab **gains** heat, negative W = it **loses** heat. |
| `climate_lookup` | For each hour, picks the heat-pump efficiency (COP) and who does the heating (heat pump, electric heater, fuel heater). |
| `HVAC_thermal` | Runs the balance at the two set-points, decides heating / cooling / ventilation, and turns the heat into battery watts. |

"SSM" = Steady State Model. It is VECTO's model for **buses** (VECTO = the EU certification simulator, Regulation (EU) 2017/2400). VECTO gives a **lorry** only one flat number (150–200 W mechanical, 187.5–250 W electric; `VAUX/HVAC-Table.csv`). HDEV applies the bus model to a truck cab, hour by hour. Every bus value used on a truck is a bus value (see the review).

## The heat balance (`ssm_total_w`)

At a chosen cab temperature `T_calc`:

```
heat gain =  walls     (T_out − T_calc) × A_surface × U
           + people    N × 50 W (if T_out < 17 °C) or 80 W
           + sun       solar × A_window × g × clouding × 0.25
           + fresh air ρ × cp × Q/3600 × (T_out − T_calc)      ← HDEV addition, 0 if Q = 0
```

* **U-value** [W/(m²·K)]: how many watts leak through one square metre of wall for each degree of difference. **UA** = U × A_surface [W/K]: the whole cab. A cab with UA = 60 W/K loses 60 W for each degree it is warmer than outside.
* **g-value**: the share of sun energy that gets through the window glass (0.95 in VECTO).
* **clouding** (0.65 or 0.8): VECTO's allowance for clouds. **0.25**: a constant written straight into VECTO's code (`SSMRun.cs:61`) and into the original 2015 Excel sheet (`SSHVAC_V07`, cell L89). Nobody wrote down why. We keep it and call it "unexplained".
* **Fresh air** `Q` [m³/h]: outside air pushed into the cab. It must be heated or cooled to cab temperature, which is the `ρ·cp·Q/3600·ΔT` term (ρ = air density, cp = heat capacity of air). VECTO has no such term.

## Heating, cooling or ventilation only? (`HVAC_thermal`, steps 1 and 4)

The balance is run twice: at the **heating set-point** (18 °C) → `run1`, and at the **cooling set-point** (23 °C) → `run2`. A **set-point** is the cab temperature the system tries to hold. Because 23 > 18, `run1 ≥ run2` always.

| `run1` | `run2` | Meaning | What happens |
|---|---|---|---|
| < 0 | < 0 | The cab loses heat even at 18 °C | **Heating** by the amount `|run1|` (the smaller loss), minus waste heat |
| > 0 | > 0 and outside ≥ 17 °C | The cab gains heat even at 23 °C | **Cooling** by `run2` (cool down to 23 °C) |
| > 0 | > 0 and outside < 17 °C | Gains heat, but it is cool outside | Nothing but the **fan** (VECTO switches the AC off below 17 °C) |
| > 0 | < 0 | Between the set-points | **Fan only** |

These four cases cover every hour (test `test_B2_three_modes_cover_every_hour_when_tcool_ge_theat`).

## From heat to battery watts

* **Heat pump:** moves heat instead of making it. **COP** (coefficient of performance) = heat delivered ÷ electricity used. COP 2.5 means 1 kW of electricity gives 2.5 kW of heat. It gets worse when it is colder. `HP_el = heat ÷ COP`.
* **Electric heater:** a resistor. Efficiency 0.93 (VECTO), so `EH_el = heat ÷ 0.93`.
* **Share table** (`climate_lookup`): at −20 °C a heat pump may do only 40 % and the electric heater 20 % (the rest a fuel heater); at 8 °C and above the heat pump does 100 %. HDEV takes the shares of the **nearest** temperature point. Exact ties go to the colder point.
* **Cap:** the heat pump + electric heater cannot give more than `max_heating_power`. If the demand is higher, both are scaled down by the same factor. The fuel heater is not capped in HDEV.
* **Air conditioning:** `AC_el = cooling ÷ cooling COP`, capped at `max_cooling_power`.
* **Fan:** `fan = cab_volume × air_changes_per_hour × 0.56 Wh/m³`. **Air change rate** = how many times per hour the cab air volume is moved (7 per hour in the small-bus VECTO configurations, 10 or 20 in the others).
* **Total** `HVAC_el = HP_el + EH_el + AC_el + fan`. It goes into `P_aux` with `HVAC_eff = 1.0` (the default 1.25 would add 25 % on top).

## Small worked example (ILLUSTRATIVE)

Cab: A = 20 m², U = 3.0 → UA = 60 W/K; 2 people; windows 4 m²; volume 6.5 m³; fan 7 per hour; outside **−5 °C**, dark, `Q = 0`. Heat pump with COP 2.04, share 100 %.

1. `run1` (cab at 18 °C): walls = (−5 − 18) × 60 = −1380 W; people = 2 × 50 = +100 W → **−1280 W**.
2. `run2` (cab at 23 °C): walls = (−5 − 23) × 60 = −1680 W; people +100 W → −1580 W.
3. Both negative → heating. Demand = |max(−1280, −1580)| = **1280 W** of heat.
4. Heat pump: 1280 ÷ 2.04 = **627 W** electric.
5. Fan: 6.5 × 7 × 0.56 = **25.5 W**.
6. `HVAC_el` = 627 + 25.5 ≈ **653 W** from the battery.

(With `Q = 100 m³/h` the air term adds ρ·cp·100/3600·(−23) ≈ −0.85 kW of heat loss: about +415 W electric at COP 2.04.)

## Which VECTO lines each piece stands in for (commit `b8d6126`, branch `IEPC-experiments`)

| HDEV piece | VECTO |
|---|---|
| `ssm_total_w` walls, people, sun | `SSMRun.cs:48–64` (constants: `Constants.cs:93–97, 114`; `SSMInputs.cs:49–64`) |
| two set-points 18 / 23 | `SSMRun.cs:26–45`, `Constants.cs:102–103` (low-floor buses use a different upper value, HDEV does not) |
| heating demand | `SSMCalculate.cs:744–773` |
| share split and cap | `SSMCalculate.cs:215–242` (shares: `HeatingDistribution.csv`) |
| COP division, electric heater | `SSMCalculate.cs:172–213`, COPs `DefaultClimatic.aenv` |
| cooling | `SSMCalculate.cs:337–374, 553–578` |
| fan and ventilation modes | `SSMInputs.cs:85–89`, `SSMCalculate.cs:272–296, 376–427` |
| 1/0.8 factor for lorries (not used in thermal mode) | `DeclarationData.cs:126`, `HeavyLorryAuxiliaryDataAdapter.cs:78` |

What HDEV does **differently** from VECTO: real hourly weather instead of 11 fixed conditions; COP interpolated in temperature instead of one COP per condition; shares by nearest temperature instead of per condition; the fresh-air term; no technology benefits; no low-floor upper set-point; fuel heater not capped or divided by its efficiency.
