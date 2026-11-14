# HDEV closeout: HVAC set finalised (`ssm_total_w`, `climate_lookup`, `HVAC_thermal`), 13 Nov 2026

Continues from `claude/session-closeout-2026-11-12-force-paux-pto.md`. Kiro HVAC review = **PR #32** (`hvac-review-2026-11`, report `docs/research/hvac-review-2026-11.md`). Claude re-checked Kiro's key VECTO claims in source (fork `IEPC-experiments`, `b8d6126`) and reran its 24 tests (pass). Items for the later full-harness Kiro run: `claude/kiro-notes-full-harness.md`.

## 1. Function status
| Function | Status |
|---|---|
| `ssm_total_w` | **Final (13 Nov)** |
| `climate_lookup` | **Final (13 Nov)** |
| `HVAC_thermal` | **Final (13 Nov)**; only cosmetic comment left (line 43 "air changes per hour" → per second) |
| `consumption_engine` | Open. **Knock-on:** step 3 `rho_row = p_air/(R_air*(T_amb_h[hour] + 273.15))` must drop `+ 273.15` (temperatures now in K) |

## 2. Decisions [all Bob, 13 Nov]
1. Keep VECTO's `0.25` solar factor (VECTO-auditable; meaning undocumented, `SSMRun.cs:61`; solar term ≈ −4 % of annual energy).
2. **All temperatures in kelvin** inside the engine (cleaner, matches VECTO internals). Parser converts every temperature with the same `+273.15` (T_amb, set-points, T_boundary, T_cool_off, T_points).
3. `Q` in m³/s; `vent_rate`, `vent_rate_heating` in 1/s; `spec_vent_power` in J/m³ (2016). Parser converts. No maths change.
4. **Defaults rule:** all default values live in a defaults function (`defaults.py`), not in function signatures and not in the parser. Parser only cleans, formats, selects inputs, converts units and does all checks so the engine doesn't break.
5. Q default = 100 m³/h for 2 persons (Dvorak et al. preprint v1, preprints.org 202412.0068, Section 2 Eq. 2 = 102.4 m³/h at 1000 ppm CO₂; full text read by Claude 13 Nov; final WEVJ 16:129 not opened).
6. `climate_lookup`: **one temperature axis** `T_points` (8 VECTO temperatures) for COPs and shares. Reason: VECTO reads the `heating/cooling` column of `DefaultClimatic.aenv` into a variable and never uses it (`EnvironmentalContidionsMapReader.cs`); all 11 conditions feed heating and cooling with the same COP column (`SSMCalculate.cs` 114–116, 184, 580–602). The 15 Oct split was Claude's suggestion, based on that column, and was wrong. Effect +0.04 % (Q=100) / +0.15 % (Q=0).
7. **Fan linked to fresh air:** `fan_flow = where(fan_rate > 0, max(cab_volume*fan_rate, Q), 0)`; Q = 0 = VECTO. +79.7 kWh/yr (+11.7 % of HVAC energy) on the PR #32 placeholder set-up. [ASSUMPTION] all fresh air through the blower (ram air not modelled). To test in the full harness.
8. **Heating set-point stays VECTO 18 °C** as default (user can override, e.g. 22 °C). Evidence for 21–22 °C (Daimler press 25 Feb 2025; Ramesh Babu 2025) → +26…38 % annual HVAC energy. Goes in the deviation register.
9. **`fuel_heat` unchanged** (returned, not used by `consumption_engine`; no effect on battery energy). **Note kept:** deviation-register flag "diesel heater fuel not reported"; build `min(heat, heater_kW)/0.80` (VECTO `SSMCalculate.cs` 208–210) only if a client needs diesel figures.

## 3. Code of record (Bob's pastes, 13 Nov)
```python
def ssm_total_w(T_amb, solar, T_calc, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q):
  T_amb = np.asarray(T_amb, dtype=float) # K
  solar = np.asarray(solar, dtype=float) # W/m²
  rho = p / (R * T_amb )
  q_wall = (T_amb - T_calc) * A_surface * U
  q_people = N_persons * np.where(T_amb < T_boundary, heat_per_person[0], heat_per_person[1])
  q_solar = solar * A_window * g * np.where(T_amb < T_boundary, clouding[0], clouding[1]) * solar_factor
  q_freshair = rho * cp * Q * (T_amb - T_calc)   # Q in m³/s
  return q_wall + q_people + q_solar + q_freshair

def climate_lookup(T_amb, T_points, cop_heat_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points):
  T_amb = np.asarray(T_amb, dtype=float)
  cop_heat = np.interp(T_amb, T_points, cop_heat_points)
  cop_cool = np.interp(T_amb, T_points, cop_cool_points)
  dist = np.abs(T_amb[..., None] - np.asarray(T_points, dtype=float))
  idx = np.argmin(dist, axis=-1)                 # tie -> first = colder
  hp_share = np.asarray(hp_share_points, dtype=float)[idx]
  eh_share = np.asarray(eh_share_points, dtype=float)[idx]
  fuel_share = np.asarray(fuel_share_points, dtype=float)[idx]
  return cop_heat, cop_cool, hp_share, eh_share, fuel_share
```
`HVAC_thermal`: Bob's 13 Nov paste — signature without defaults, `T_points` instead of the two grids, step 5:
```python
  fan_flow = np.where(fan_rate > 0, np.maximum(cab_volume * fan_rate, Q), 0.0)
  fan_el = fan_flow * spec_vent_power
```
Rest unchanged from the 12 Nov code of record.

**Check (Claude, 13 Nov):** new set vs old notebook on DMI 06188 2025, placeholder cab: Q=0 438.2 → 438.9 kWh/yr (+0.15 %, one axis only; K and SI changes exact); Q=100 678.0 → 758.0 (+11.8 % = fan link + one axis). `climate_lookup` returns VECTO table values at all 8 points; colder-point tie holds at all 7 midpoints in K.

## 4. defaults.py entries (HVAC)
| Arg | Default | Source |
|---|---|---|
| eh_eff | 0.93 | VECTO DefaultClimatic.aenv |
| spec_vent_power | 0.56 Wh/m³ | VECTO Constants.cs 111–112 |
| heat_per_person, clouding, T_boundary, g, solar_factor | (50, 80) W; (0.65, 0.8); 17 °C; 0.95; 0.25 | VECTO Constants.cs 93–97, 114; SSMRun.cs:61 |
| waste_heat | 0 W | HDEV, conservative (VECTO credits EM waste heat M14Impl.cs 78) |
| T_heat, T_cool, T_cool_off | 18, 23, 17 °C | VECTO Constants.cs 102–103; SSMInputs.cs:77 |
| Q | 100 m³/h | Dvorak preprint |
| p, R, cp | 101325 Pa, 287.05, 1005 J/kgK | ISO 2533 (summary only); **cp NO SOURCE read yet** |
| T_points, COP columns, shares | DefaultClimatic.aenv, HeatingDistribution.csv (duplicate temps 4/5, 6/7, 8/9 dropped) | VECTO |
Required in thermal mode, no sourced truck default: A_surface, U, A_window, cab_volume, max_heating_power, max_cooling_power, vent_rate, vent_rate_heating (BLOCKED in PR #32 Part G).

## 5. Parser jobs (HVAC)
Fill weather NaN (else silent 0 W); fill COP grid NaN before the call (nearest value, 2 Nov decision); cop > 0, eh_eff > 0, shares in [0,1] sum ≤ 1, caps finite, T_cool ≥ T_heat, points unique ascending, duplicate temps identical, Q ≥ 0; temps < ~150 K → raise (°C passed by mistake); all unit conversions above; `HVAC_eff = 1.0` into `P_aux` in thermal mode (else +25 %); DMI end-of-hour stamp; build HD case from (heat pump type, electric heater y/n, fuel heater y/n); reject mechanical heat pumps for BEV.

## 6. Deviation register additions
Bus SSM on truck cab; hourly weather vs 11 conditions (−13 %); COP interpolation / nearest shares (±0.1 %); COP held below −20 °C and below −5 °C fill (optimistic); fresh air on (+55 % at Q=100); fan ≥ fresh air (+11.7 %); 18 °C set-point may understate winter energy (21–22 °C observed); 0.25 solar factor undocumented; waste heat 0 (conservative); diesel heater fuel not reported; no door openings / warm-up / humidity (humidity: non-conservative).

## 7. Next (Bob's questions 13 Nov: parser vs consumption engine, defaults.py, JSON, main.py)
See chat answer; open.
