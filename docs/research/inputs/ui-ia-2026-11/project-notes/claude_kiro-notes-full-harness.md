# Notes for the Kiro full-harness run (all functions + defaults + parser + consumption_engine finished)

Living list. Add items as they come up; the full-harness Kiro prompt is written from this file. Refer to the owner only as "Bob".

## From the HVAC finalisation (13 Nov 2026, after Kiro PR #32)

1. **Fan linked to fresh air** (`HVAC_thermal` step 5): `fan_flow = where(fan_rate > 0, max(cab_volume*fan_rate, Q), 0)`, `fan_el = fan_flow * spec_vent_power`.
   - Why: HDEV's `q_freshair` heats Q = 100 m³/h of outside air, but the placeholder fan only moves 6.5 m³ × 7 /h = 45.5 m³/h. With Q = 0 the line equals VECTO exactly.
   - Measured (Claude, Kiro PR #32 set-up: placeholder cab, Q = 100 m³/h, DMI 06188 2025, ILLUSTRATIVE Mon–Fri 06–16): fan 66.5 → 146.2 kWh/yr, **+79.7 kWh (+11.7 % of HVAC energy)**. Fan runs in all 2610 operating hours.
   - [ASSUMPTION] all fresh air enters through the cab blower. Ram air while driving would make it an over-estimate.
   - [VECTO, bus] 0.56 Wh/m³ is a bus fan figure, here also applied to fresh air.
   - **Test in the harness:** sensitivity per mission (Regional / Urban / LongHaul) with HDEV driver rows; share of trip energy; search for any source on how truck cabs take in fresh air while driving (ram air vs blower) and fan specific power for truck cab blowers.

2. **Temperatures in kelvin across the engine.** `ssm_total_w` now uses `rho = p/(R*T_amb)` with T in K. `consumption_engine` step 3 `rho_row = p_air/(R_air*(T_amb_h[hour] + 273.15))` must drop `+ 273.15` at the same time. **Test:** the same weather array feeds both; check air density per row is ~1.2–1.3 kg/m³ (not ~0.6); check the parser converts every temperature (T_amb, set-points, T_boundary, T_cool_off, T_points) with the same +273.15.

3. **`climate_lookup` one temperature axis** (8 VECTO temperatures, K). VECTO reads the `heating/cooling` column of `DefaultClimatic.aenv` into a variable and never uses it (`EnvironmentalContidionsMapReader.cs`); all 11 conditions feed heating and cooling with the same COP column (`SSMCalculate.cs` 114–116, 184, 580–602). Effect +0.04 % (Q=100) / +0.15 % (Q=0). **Test:** at VECTO's points output = table; tie rule (colder point) at all 7 midpoints in K; parser drops duplicate temperatures (rows 4/5, 6/7, 8/9) only if their values are identical.

4. **Units moved to the parser:** Q m³/h → m³/s (÷3600); `vent_rate`, `vent_rate_heating` 1/h → 1/s (÷3600); `spec_vent_power` Wh/m³ → J/m³ (×3600 = 2016). **Test:** HVAC_el unchanged vs the 12 Nov code at identical physical inputs.

5. **Defaults moved out of signatures into the defaults function** (Bob's rule, 13 Nov: defaults function holds all default values; parser only cleans, formats, selects, converts and checks). **Test:** no engine function has a default argument; every default has a source tag. Open: `cp = 1005 J/kgK` has no source read yet.

6. **Fresh-air default Q = 100 m³/h for 2 persons** — Dvorak et al. preprint v1 (preprints.org 202412.0068, Section 2 Eq. 2: 102.4 m³/h at 1000 ppm CO₂, outdoor 550 ppm, 0.02304 m³/h CO₂ per person). Final WEVJ 16:129 version not opened (403). Validation point from the same paper: 3311 W total HVAC at −7 °C, set-point 23 °C, fresh air (Fig. 3) vs HDEV placeholder heat demand 2811 W (Q=100) / 1700 W (Q=0) — not like-for-like.
