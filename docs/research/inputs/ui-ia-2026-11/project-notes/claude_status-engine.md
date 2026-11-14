# HDEV engine: living status and decisions

Read this first in a new chat. Update this file each session instead of writing a new closeout.

Started 9 Nov 2026. Last updated **12 Nov 2026** (session 10–12 Nov: `driver_model` finalised section by section, Kiro PR #29 reference-driver sensitivity; see §6).

It merges and replaces every engine closeout from 6 Oct to 3 Nov:
- 10-06 precompute;
- 10-08 crosswind/payload, P_aux, payload/force;
- 10-12 status and contradictions, Kiro planning, year/day problem;
- 10-19 P_aux/HVAC;
- 10-21 PTO/driver;
- 10-22 consumption harness, VECTO BEV comparison, function review, validation/drivetrain/winter;
- 10-31 PTO;
- 11-01, 11-02, 11-03.

The originals are in the GitHub archive (§7).

Still kept as separate project docs:
- `session-closeout-2026-11-07-validation-fallbacks-calibration.md`: EEA validation, fallbacks, calibration methods A–D.
- `session-closeout-2026-11-09-tools-review.md`, `findings-other-tools-review-2026-11-09.md` and `review-other-tools-all-features-2026-11-09.md`: what other tools do.
- `kiro-prompt-driver-reference-sensitivity-2026-11-10.md`: the prompt behind PR #29 (§6).
- `ui-input-list-2026-10-26.md`: every user input.
- `vecto-declaration-defaults-2026-10-07.md`, `payload-resolver-design-2026-10-07.md` and `crosswind-verification-2026-10-06.md`: reference notes.
- `status-data-library-combined-2026-11-07.md`: data library.

Full VECTO tables live in the archived closeouts and in the repo. Look there for:
- the BEV aux trace (10-08 P_aux, in the repo at `docs/decisions/`);
- the climate/COP and HD-case tables (10-19).

---

## 0. System design (decided; details in the archive)

**Pipeline** (each step at the frequency it actually changes):
1. Inputs (project JSON).
2. Parser/resolver (`defaults.py`, written last).
3. Waypoints (VDRI / typed / GPS).
4. `payload_engine` and `pto_engine` on waypoints.
5. `crosswind_engine` once per vehicle.
6. `driver_model`: 1 s rows, once per route at the reference vehicle (screening); a final pass at exact values for the chosen truck [DECIDED 10 Nov, §6].
7. `force_engine`.
8. `consumption_engine`: maps payload, PTO, hourly weather and aux onto rows; wheel → battery power.
9. Battery and charging (to rebuild).
10. Sizing sweeps.
11. TCO / CO₂ / report.

**Where things are mapped onto rows [DECIDED 19 Oct]:**
- All of it happens inside `consumption_engine`. Payload is matched by distance with `searchsorted`; stop PTO by `V == 0` and stop distance, with a 1e-3 m tolerance.
- Nothing aux-related goes into the driver model.

**Why kWh can't be scaled:** a change in mass or ρ can flip a row between traction and regen. So every (day × weather × mass) combination needs its own row-wise multiply-add. It is cheap with numpy. [DECIDED 6 Oct]

**Year structure [DECIDED 12 Oct]:**
- Pattern input (route, days, departure/return, exceptions) → calendar expand → consumption per vehicle per date, with that date's weather.
- Each vehicle-date produces one session object `{arrival, departure, energy_need_kWh, arrival_SOC}`.
- One year-long depot charging run with shared chargers and grid limit; an SOC shortfall carries over.
- Monte Carlo is an optional layer on top.
- Weather spread = percentiles across the weather year; it is not Monte Carlo.
- A timing gate comes first. The harness T12 ran a full year at a few ms per day for consumption. PR #29 timed the driver: 0.06 s (Regional) / 0.13 s (Urban) per run [TEST]. The year-long charging run is not yet timed. [OPEN]
- Hourly weather per row (option C) is what the harness and the engine already use. The older "daily weather first" note is superseded.
- Charging time step is an argument; the actual resolutions must come from Energinet product specs. [OPEN, unsourced]

**Weather rules [DECIDED 6 Oct]:**
- Never average the same calendar date across years. Keep each real year paired by date.
- Keep the worst day as its own sizing case.
- DMI: each parameter comes from the nearest station with a full year (harness method).
- The old `dmi_weather_climatology.py` in the repo breaks the no-cross-year-averaging rule. [OPEN]

**Other system decisions:**
- One project JSON with sections (vehicles, routes, assignments, calendar), each with its own Pydantic schema. Reusable libraries are separate files.
- "Skip a step" (e.g. user kWh/km) is a flagged resolver override.
- Any stage can run on its own from user data: `runner.run(base, changes)` refuses an incomplete entry contract.
- Slots for OEM/CPO/aggregator data: proposed shape `{value, unit, source, date, label, provided_by, locked, version}`. [OPEN: Bob to confirm, M6.7]
- No smart charging → ASAP only [DECIDED]. Other capability gates are suggestions only. [OPEN, M6.16]
- Battery sizing modes:
  - A: real vehicle (datasheet mass and kWh);
  - B: size it (iterate mass). Glider-mass and pack-density sources are still needed.
- Caching by input keys comes later. The engines are already written cache-ready (pure functions, no globals).
- The Kiro master spec (`.kiro/specs/hdev-master-plan/`) is in the repo. Its open items are M6.6, 6.7, 6.16, 6.20, 6.21, 6.24 and 6.25.
- **No unit conversion inside engine functions [DECIDED 3 Nov, applied to `driver_model` 10 Nov]:** all km/h → m/s is done in the parser. The only `3.6` left in `driver_model` is VECTO's own look-ahead rule (km/h × 10 m) and the decision-factor tables in `coast_distance` (km/h by VECTO definition).

**Resolved from the 12 Oct contradiction list:**
- Payload runs on waypoints before the driver; mapping onto rows happens in the consumption engine.
- Rows are numpy arrays.
- CdxA grid is 60–130 km/h.
- The stale class `DriverModel` is replaced by the function `driver_model`. Housekeeping still to do in the repo.
- Grade is an altitude secant per row (M0.12 resolved by the rewrite).
- Backend: FastAPI later.

Tags used below:
- **[VECTO]**: read in `mohgsaad-art/VECTO`.
- **[VMOD]/[VSUM]**: read from Bob's VECTO 5.1.6-RC run (22 Oct).
- **[SOURCE]**: external source read by Claude.
- **[CALC]**: Claude's arithmetic from sourced inputs.
- **[TEST]**: Kiro's or Claude's test.
- **[ASSUMPTION]**, **[DECIDED]** (Bob agreed), **[SUGGESTED]** (not yet decided), **[OPEN]**.

VECTO line numbers in this file: unless stated otherwise they are from `mohgsaad-art/VECTO`, branch `IEPC-experiments`, commit `b8d6126` (checked 10 Nov). Older references from Kiro PR #21 used v5.1.3 `d16ba783c`; re-check before client citations.

Working rules:
- The engine stays dumb and pure. Checks, lookups, defaults and gap-filling go in the parser.
- Code of record lives in Bob's notebook (`HDEV_NEW` notebook, latest uploaded 9 Nov as `HDEV_NEW (3).ipynb`; repo copy `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-07.ipynb` is older) and in the repo `mohgsaad-art/hdev`. This file holds the code of record for functions whose closeouts are archived, and for `driver_model` (§3.0).
- Review method (since 9 Nov): Bob goes through each function section by section; Claude explains the current code, the logic and any change in plain English; Bob adds his own comments and finalises.

---

## 1. Function status (as of 12 Nov 2026)

| Function | Status | Note |
|---|---|---|
| `crosswind_engine` | **Final** | 10° yaw clamp stated in every report. Parser: speed grid 60–130 km/h, no 0 km/h. Test cell only prints a heading (no VECTO Excel comparison). |
| `payload_engine` | **Final, unchanged** | All guards go to the parser (§2.2). |
| `interp1`, `decel_distance` | **Final** | |
| `coast_distance` | **Final (12 Nov)** | Drag table `drag_v`/`drag_F` read at `v`; **β rolling form added** (`beta` argument after `Crr`). Code in §3.0. |
| `driver_model` | **Final (12 Nov)** | Reviewed section by section. Code of record in §3.0. Smoke-tested by Claude on a made-up route (runs; not a validation). Three comment fixes pending (§3.0). |
| `force_engine` | **Open: next to review** | Never reviewed section by section. Check consistency with the driver (β form, grade angle, wheel inertia `theta_red / r_dyn²` ↔ `m_red_wheels`). Test cell uses `g = 9.81`. |
| `P_aux` | **Final logic; small fix** | Bob's notebook checks skip `PTO_always_on < 0` and `PTO_eff <= 0`; stale comment "undo the multiply above". Code of record in §2.1 has the checks. |
| `pto_engine` | **Final (engine side)** | In the notebook with the `is_on` return. **Test cell broken:** uses the old 4-argument call and unpacks 3 outputs. |
| `SP_power_helper` | **Final** | Matches VECTO `SteeringPump.cs` exactly (§2.3). Read-through only. |
| `ssm_total_w`, `climate_lookup`, `HVAC_thermal` | **Final** | Q/p/R/cp edit confirmed in the notebook (9 Nov). Read-through only; open items are parser jobs (§2.4). |
| `consumption_engine` | **Open (largest job)** | Old `pto_engine` outputs; drive PTO; fixed efficiencies (about −32 % Regional); regen cap; SP/Cond timing; battery-loss hook (§3c). |
| Parser (`defaults.py`) | **Open** | Jobs in §2, §3.0, §3b and §6. |
| Battery model (OCV + Ri), charging engine | **Open** | After the consumption engine. |

**Agreed review order (12 Nov):** `force_engine` → `P_aux` fix → `pto_engine` test cell → `SP_power_helper` read-through → HVAC read-through → `consumption_engine`.

---

## 2. Code of record for the finalised functions

### 2.1 `P_aux`
```python
##5.1 Electrical system
def P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on, ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0):
  powers = [np.asarray(p, dtype=float) for p in (ES_power, PS_power, HVAC_power, SP_power, cond_power)]
  effs = (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff)
  PTO_always_on = np.asarray(PTO_always_on, dtype=float)

  for p in powers + [PTO_always_on]:
      if np.any(p < 0):
          raise ValueError("aux power cannot be negative")
  for e in effs + (PTO_eff,):
      if e <= 0:
          raise ValueError("efficiency must be > 0")

  ES_power, PS_power, HVAC_power, SP_power, cond_power = (p * e for p, e in zip(powers, effs)) # VECTO factors: multiply
  PTO_always_on = PTO_always_on / PTO_eff # shaft W / efficiency = electric W (1.0 = already electric)

  return ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on
```

Why it multiplies: VECTO does. These all match the VECTO .vmod:
- ES 1428.57 W × 0.7 = 1000 W;
- HVAC 200 W × 1.25 = 250 W;
- SP 32.87 W × 0.7 = 23.0 W.

Open around `P_aux`:
- `HVAC_eff` must be passed as 1.0 when HVAC comes from the thermal model (parser job).
- `PTO_always_on` must accept a per-hour array for the later fridge model. `P_aux` already works with arrays.
- Bob's notebook version (9 Nov) is missing the `PTO_always_on` and `PTO_eff` checks shown above.

### 2.2 `payload_engine` (Bob's, unchanged)
```python
def payload_engine(stop, shape, payload_start, payload_end=None, payload_custom=None):
  stop = np.asarray(stop, dtype=float)
  is_stop = stop > 0
  is_stop[0] = False
  n_stops = int(is_stop.sum())
  if shape == "constant":
      values = np.full(n_stops + 1, float(payload_start))
  elif shape == "linear":
      if n_stops == 0:
          raise ValueError("linear needs at least one stop")
      values = np.linspace(payload_start, payload_end, n_stops + 1) # hdev assumption (unsourced)
  elif shape == "custom":
      values = np.asarray(payload_custom, dtype=float)
      if len(values) != n_stops + 1:
          raise ValueError(f"custom needs {n_stops + 1} values, got {len(values)}")
  else:
      raise ValueError(f"unknown shape: {shape}")
  if np.any(values < 0):
      raise ValueError("payload cannot be negative")
  payload = np.full(len(stop), np.nan)
  payload[0] = values[0]
  payload[is_stop] = values[1:]
  return payload
```

Parser jobs [DECIDED]:
- `linear` without `payload_end` → clear error. NaN check on custom values.
- Stops switched off for payload change → the parser passes a cleaned `stop` copy. UrbanDelivery has 104 stops, median 15 s.
- Cap: 0 ≤ payload ≤ registered GVW − curb − body/trailer (VECTO TPMLM, `TruckSegments.cs` 233–234, 276–277). Convert tonnes to kg.
- Legal weight limits only as a later **warning**.
- Later, in the battery step: a bigger battery means higher curb mass and lower max payload.

Sources:
- **VECTO reference payloads:** ACEA White Book, about 75 % long haul and 50 % others; fixed per group ≥ 4, GVW functions for groups 1–3 (SR7 Lot 4 §4.3.5.4).
- **Weights law:** revision 2023/0265(COD) is not adopted, so Directive 96/53/EC applies.
- **ZEV allowance:** likely max 2 t = the actual extra ZEV-tech weight (Reg. 2019/1242 Art. 20; Irish SI 47/2025; DK BEK 1663/2023 §22). Kiro read 1 t (alt-fuel only). EUR-Lex Art. 10b not yet read.
- **Danish order:** DK BEK 1663/2023 is Historic. Its successor and the 60 t modulvogntog order were not found.

[OPEN] Default payload for sizing:
- VECTO reference (7 Oct decision); or
- max payload; or
- reference plus a max-payload run beside it.

### 2.3 `SP_power_helper` (Bob's)
```python
# returns mechanical W, goes into P_aux as SP_power gets multiplied by 0.7 for electrical W
def SP_power_helper(SP_baseline, SP_axle_shares, SP_tech_factors):
  SP_baseline = np.asarray(SP_baseline, dtype=float)         # (UF, B, S) in W, SP-Table.csv
  SP_axle_shares = np.asarray(SP_axle_shares, dtype=float)   # one (UF, B, S) row in % per steered axle, SP-Axles.csv
  SP_tech_factors = np.asarray(SP_tech_factors, dtype=float) # one (UF, B, S) row per steered axle, SP-Tech.csv or custom
  if SP_axle_shares.ndim != 2 or SP_axle_shares.shape[1] != 3 or len(SP_axle_shares) == 0:
      raise ValueError("SP_axle_shares needs one (UF, B, S) row per steered axle")
  if SP_tech_factors.shape != SP_axle_shares.shape:
      raise ValueError("need one technology (UF, B, S) per steered axle")
  parts = SP_baseline * SP_axle_shares.sum(axis=0) / 100
  parts = parts * SP_tech_factors.mean(axis=0)
  return float(parts.sum())
```

[VECTO] sources:
- `SteeringPump.cs` 58–114 (result is mechanical W, line 56; /100 at line 142).
- `HeavyLorryAuxiliaryDataAdapter.cs` 188–190 (tech count = steered axles) and 220 (electric = mech × 0.7).

**Standstill:** the BEV electric steering pump is off when stopped.
- `ElectricAuxiliaries.PowerDemand` drops "STP" when the vehicle is stopped.
- `Constants.cs` 59–60: `SteeringPump` and `SteeringPump_el` share the ID "STP", so this looks incidental.
- Report it as "follows VECTO's current behaviour".
- Stopped means |v| ≤ 0.01 m/s (`Vehicle.cs` 262, per Kiro).

Parser jobs:
- PEV-applicable technologies only.
- Max 4 steered axles.
- Clear error for empty SP-Table cells (groups 1s–3 have no Municipal/Construction; groups 6–8 are empty).
- A custom W value bypasses the helper.

### 2.4 HVAC thermal (with the 11-02 §4.4 edit applied; confirmed in Bob's notebook 9 Nov)

**The edit:**
- `HVAC_thermal` takes `Q=0.0, p=101325.0, R=287.05, cp=1005.0` as its last arguments.
- It passes them to **both** `ssm_total_w` calls. Without this, `ssm_total_w` raises a TypeError.

```python
def ssm_total_w(T_amb, solar, T_calc, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q):
  T_amb = np.asarray(T_amb, dtype=float) # outside temp per weather hour [°C]
  solar = np.asarray(solar, dtype=float) # sunlight per weather hour [W/m²]
  rho = p / (R * (T_amb + 273.15)) # density of outside air
  q_wall = (T_amb - T_calc) * A_surface * U
  q_people = N_persons * np.where(T_amb < T_boundary, heat_per_person[0], heat_per_person[1])
  q_solar = solar * A_window * g * np.where(T_amb < T_boundary, clouding[0], clouding[1]) * solar_factor
  q_freshair = rho * cp * Q / 3600 * (T_amb - T_calc)
  return q_wall + q_people + q_solar + q_freshair

def climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points):
  T_amb = np.asarray(T_amb, dtype=float)
  cop_heat = np.interp(T_amb, T_heat_points, cop_heat_points)
  cop_cool = np.interp(T_amb, T_cool_points, cop_cool_points)
  dist = np.abs(T_amb[..., None] - np.asarray(T_heat_points, dtype=float))
  idx = np.argmin(dist, axis=-1)                          # tie -> first = colder
  hp_share = np.asarray(hp_share_points, dtype=float)[idx]
  eh_share = np.asarray(eh_share_points, dtype=float)[idx]
  fuel_share = np.asarray(fuel_share_points, dtype=float)[idx]
  return cop_heat, cop_cool, hp_share, eh_share, fuel_share

def HVAC_thermal(T_amb, solar, A_surface, U, N_persons, A_window, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points,
                 hp_share_points, eh_share_points, fuel_share_points, max_heating_power, max_cooling_power, cab_volume, vent_rate, vent_rate_heating,
                 eh_eff=0.93, spec_vent_power=0.56, heat_per_person=(50.0, 80.0), clouding=(0.65, 0.8), T_boundary=17.0, g=0.95, solar_factor=0.25,
                 waste_heat=0.0, T_heat=18.0, T_cool=23.0, T_cool_off=17.0, Q=0.0, p=101325.0, R=287.05, cp=1005.0):
  T_amb = np.asarray(T_amb, dtype=float)
  # step 1: heat balance at 18 and 23 C
  run1 = ssm_total_w(T_amb, solar, T_heat, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)
  run2 = ssm_total_w(T_amb, solar, T_cool, A_surface, U, N_persons, A_window, heat_per_person, clouding, T_boundary, g, solar_factor, p, R, cp, Q)
  losing_heat = (run1 < 0) & (run2 < 0)
  heating_demand = np.where(losing_heat, np.abs(np.maximum(run1, run2)) - waste_heat, 0.0)
  heating_demand = np.maximum(heating_demand, 0.0)
  # step 2: split + cap (SSMCalculate.cs 215-245)
  cop_heat, cop_cool, hp_share, eh_share, fuel_share = climate_lookup(T_amb, T_heat_points, cop_heat_points, T_cool_points, cop_cool_points, hp_share_points, eh_share_points, fuel_share_points)
  fuel_heat = heating_demand * fuel_share
  sum_heat = np.minimum(max_heating_power, heating_demand * (hp_share + eh_share))
  rest = np.where(np.isclose(fuel_share, 1.0), 1.0, 1 - fuel_share)
  scale = sum_heat / rest
  hp_heat = scale * hp_share
  eh_heat = scale * eh_share
  # step 3: heating electric W
  if np.any((hp_heat > 0) & np.isnan(cop_heat)):
    raise ValueError("heat pump COP missing for this temperature")  # HDEV: VECTO silently gives 0 W here
  HP_el = np.where(hp_heat > 0, hp_heat / cop_heat, 0.0)
  EH_el = eh_heat / eh_eff
  # step 4: cooling
  gaining_heat = (run1 > 0) & (run2 > 0) & (T_amb >= T_cool_off)
  cooling_demand = np.where(gaining_heat, np.minimum(run1, run2), 0.0)
  cooling_demand = np.minimum(cooling_demand, max_cooling_power)
  if np.any((cooling_demand > 0) & np.isnan(cop_cool)):
      raise ValueError("cooling COP missing for this temperature")
  AC_el = np.where(cooling_demand > 0, cooling_demand / cop_cool, 0.0)
  # step 5: ventilation fan (SSMCalculate.cs 270-295, 376-397, 399-428; SSMInputs.cs 88)
  ventillation_status = ((T_amb < T_cool_off) & (run1 > 0) & (run2 > 0)) | ((run1 > 0) & (run2 < 0))
  fan_rate = np.where(losing_heat, vent_rate_heating, np.where(gaining_heat | ventillation_status, vent_rate, 0.0))
  fan_el = cab_volume * fan_rate * spec_vent_power
  # step 6: total (into P_aux as HVAC_power with HVAC_eff = 1.0)
  HVAC_el = HP_el + EH_el + AC_el + fan_el
  return HVAC_el, fuel_heat
```

**[VECTO] check:**
- `SSMRun.cs` 25–64;
- `SSMCalculate.cs` 744–773, 215–245, 172–212, 337–374, 553–570, 272–296 and 376–428;
- `SSMInputs.cs` 85–88.

Bob's code matches VECTO with all three ventilation switches on. run1 ≥ run2 always, so the three modes cover every hour.

**HVAC decisions [DECIDED, 2 Nov]:**
1. **Fresh-air term.** `Q = 0` gives exactly VECTO. The parser default is 100 m³/h, pending the Dvorak 2025 check (https://www.mdpi.com/2032-6653/16/3/129). Humidity is ignored.
2. **No change to area or U.** Keep `A_surface` and `U`.
3. **Missing heat-pump COP** (non-R-744 at −20 °C). The parser fills it with the nearest value (−5 °C), which makes a flat clip. Flagged as optimistic below −5 °C.
4. **Setpoints** stay as arguments with VECTO defaults 18 / 23 / 17 °C. Mercedes tested at 21 °C, Chalmers at 22 °C.
5. **Weather gaps** are filled in the parser, because a NaN hour would silently give 0 W.
6. **Optional checks go to the parser:** unmet heat/cooling outputs, `eh_eff > 0`, ascending points.

**HVAC parser jobs:**
- `HVAC_eff = 1.0` in thermal mode.
- Missing max heating/cooling power → `np.inf`, flagged.
- Cab inputs get no silent defaults.
- HD-case column picking (see the 10-19 closeout).
- Fuel heater: VECTO caps at `FuelFiredHeaterPower` and divides by 0.80. Needed only if diesel use is reported.

**HVAC report flags:**
- Bus SSM is used for a truck cab (no lorry method in 2017/2400 incl. 2025/258).
- Hourly instead of VECTO's 11 points.
- COP interpolation, nearest-point split, COP clip.
- Fresh air is on (non-VECTO).
- The 0.25 solar factor is unexplained in VECTO; whether VECTO `solar` = DMI global radiation is unverified.
- Measured UA is parked, so it is a lower bound while driving.
- Door openings and cold-cab warm-up are not modelled.

**Cab and winter sources [SOURCE]:**
- **NREL CoolCab (973699):** measured UA of a US sleeper cab, parked, **51 and 65 W/K**. The placeholder 20 m² × 3.0 = 60 W/K sits inside this range.
- **Lustbader 2012:** a measured UA includes natural leaks, but not forced fresh air. So the fresh-air term is not double counted.
- **Ramesh Babu 2025 (Chalmers/Volvo, simulated):**
  - heater 4.15–4.45 kW at −10 °C;
  - Crr 0.007 at 20 °C rising to 0.014 at −20 °C;
  - consumption +58 % at −20 °C vs 20 °C.
- **Mercedes eActros 600 winter tour 2025 (OEM press text):** about +25 % at −2 °C.
  - Rolling + air resistance about 15 points; less recuperation about 4; cab climate about 5; battery heating < 1.
  - Snow/ice on class D tyres: almost +50 %.
- **Öko-Institut ELV-LIVE (measured):** −0.13 kWh/km per +10 °C at a mean of 0.96 kWh/km.
- [CALC] At −10 °C, HDEV gives 3.1 kW vs Chalmers 4.2–4.45 kW, so HDEV is low while driving.
- **Conclusion:** the winter penalty is mainly rolling resistance and air density, not HVAC.

Parked: door openings (no cab data), cold-cab warm-up (needs thermal mass), CO₂-controlled recirculation, per-person Q.

---

## 3. Driver model

### 3.0 Final `driver_model` and `coast_distance` (12 Nov 2026) [DECIDED]

**Changes made this session (10–12 Nov), all agreed by Bob:**
1. SyntaxError fixed: `v_cap = …` and `a = max(min(...))` split onto two lines.
2. `P_drag_loss` removed. Drag table `drag_v=(0.0,), drag_F=(0.0,)` (one-item tuples; a plain `0.0` breaks `interp1`). Default = zero drag. Used in `coast_acc` and passed to `coast_distance`, both read at the current speed `v` (matches VECTO).
3. `g = 9.80665` (VECTO `DeclarationData.cs` **line 72**; line 74 is `AirDensity = 1.188`. Earlier notes citing 74 for g were wrong).
4. **No unit conversion inside:** `wp_v`, `vacc_v`, `cdxa_v`, `lac_min_v`, `os_min_v`, `os_allowed`, `v_min_coast` all come in as m/s from the parser. The `3.6` in the look-ahead line stays: it is VECTO's rule (km/h × `lac_dist_factor` m). **Caution:** the signature defaults for the four thresholds still show the km/h numbers (50, 50, 2.5, 5). The parser must always pass m/s values; or change the defaults to `50/3.6`, `2.5/3.6`, `5/3.6` (Claude's suggestion, Bob to decide).
5. **β rolling form everywhere** [DECIDED 10 Nov]: `F_roll = Crr · g · m^β · cos θ`, β = 0.9 (`Physics.cs` line 51). New `beta` argument (default 1.0 = linear). Same form now in `coast_acc`, `coast_distance` and `consumption_engine`. Parser passes the same `Crr` (= `Crr_eff`, harness `crr_eff()`, which reproduces VECTO's per-axle mass-dependent Crr exactly) and `beta` to all of them. Backed by KIT thesis Eq. A.11 (one m^β formula everywhere); BETOS uses linear everywhere; only HDEV mixed the two.
6. **`P_max` kept, flagged** [DECIDED 12 Nov]: optional single motor-power cap on acceleration; only acts when coasting is on (it needs `coast_acc` for the resistance); `F_res` now includes the coasting drag table, which is only a rough stand-in for drivetrain losses while driving; 1 m/s floor (HDEV choice) avoids dividing by zero. VECTO uses the motor full-load torque curve instead. **Revisit later:** keep the power cap or switch to VECTO's torque-curve method.
7. Fixed reference vehicle kept for screening; final exact pass for the chosen truck (§6, PR #29).

**Pending comment fixes (Bob):**
- Line 24: `# VECTO DrivingCycleDataReader.cs 221-223: cycle starting at 0 km/h without stop gets a 1 s stop`.
- Line 27: "VECTO line 246-253" names no file (Claude can look it up).
- Line 190 (`elif v + ca * dt > target:`): comment is the wrong way round. Should read "rolling one more step still stays above target → keep rolling down towards it".
- Optional: rolling comment in `coast_acc` mention "VECTO β form, same as consumption".

**Code of record (Bob's 12 Nov paste, with comments):**
```python
##3 Driver model
# driver model: VECTO DefaultDriverStrategy on fixed 1 s rows (HDEV deviation: VECTO uses ~0.5 s variable steps)
# pure kinematics when coast_mass is None; with coast_mass: look-ahead coasting + overspeed at a FIXED reference vehicle (HDEV assumption)
def driver_model(wp_s, wp_v, wp_stop, wp_grade,
                 vacc_v, vacc_acc, vacc_dec, dt=1.0,
                 coast_mass=None, m_red_wheels=0.0, cdxa_v=None, cdxa=None, Crr=None, beta=1.0, rho=1.188, g=9.80665,
                 drag_v=(0.0,), drag_F=(0.0,), P_max=None,
                 lac_min_v=50.0, lac_dist_factor=10.0, df_offset=2.5, df_scaling=1.5,
                 df_vtarget=((0, 48, 52, 100), (0, 0, 1, 1)), df_vdrop=((-100, 9, 11, 100), (1, 1, 0, 0)),
                 os_min_v=50.0, os_allowed=2.5, brake_margin=0.1, v_min_coast=5.0):

  # converting waypoints into lists
  s_wp = [float(x) for x in wp_s]                      # waypoint distance [m]
  v_wp = [float(x)  for x in wp_v]                # waypoint target speed [m/s] --> / 3.6 must be in parser
  stop_wp = [float(x) for x in wp_stop]                # FINAL standing time [s] (PTO already added by the parser)
  gr_wp = np.asarray(wp_grade, dtype=float)            # waypoint grade [%]
  n = len(s_wp)

  rise = np.diff(np.asarray(s_wp)) * gr_wp[:-1] / 100  # height gained between two consecutive waypoints
  alt_wp = np.concatenate(([0.0], np.cumsum(rise))) # altitude at each way point
  alt_l = alt_wp.tolist() # convert altitude into list
  gr_l = gr_wp.tolist() # convert gradient into list

  if v_wp[0] == 0 and stop_wp[0] == 0:                 # VECTO line 221: cycle starting at 0 km/h without stop gets a 1 s stop
      stop_wp[0] = 1.0

  # speed the driver aims for after passing waypoint i; after a stop it is the next waypoint's target (VECTO line 246-253)
  # (HDEV: if several stops follow each other, take the next POSITIVE target, so the truck never gets stuck at 0 km/h)
  seg_v = [0.0] * n # target speed after each waypoint
  nxt = 0.0 # next positive target speed moving back from waypoint
  for i in range(n - 1, -1, -1): #moving backwards
      seg_v[i] = v_wp[i] if v_wp[i] > 0 else nxt
      if v_wp[i] > 0:
          nxt = v_wp[i]
  # change points: only waypoints whose target differs from the segment before can trigger braking/coasting
  chg = [i for i in range(1, n) if v_wp[i] != seg_v[i-1]] # index where the current way point speed is diff from previous segment target speed
  chg_s = [s_wp[i] for i in chg] #get the distance of the waypoints at those index

  vv = [float(x) for x in vacc_v]                       # .vacc speeds in m/s --> / 3.6  goes in parser
  va = [float(x) for x in vacc_acc]              # max acceleration at each speed
  vd = [float(x) for x in vacc_dec]              # max decceleration at each speed

  coast_on = coast_mass is not None # coasting condition check if coasting mass is present
  if coast_on:
      if cdxa_v is None or cdxa is None or Crr is None: # checking if all parameters exist to calculate coasting
          raise ValueError("coasting needs cdxa_v, cdxa and Crr")  # guard only; parser gives friendly message
      m_eff = coast_mass + m_red_wheels                # effective mass incl. rotating wheels
      cv = [float(x) for x in cdxa_v]                   # reference CdxA table speeds in m/s -->reference speed into m/s / 3.6  in parser
      cc = [float(x) for x in cdxa]

  # /3.6 in parser
  lac_min = lac_min_v        # look ahead coasting only above this speed
  os_min = os_min_v          # overspeed allowed only when target is above this
  os_add = os_allowed        # how above target speed can it exceed downhill
  v_min_c = v_min_coast      # dont coast below this

  # acceleration with no motor torque at speed v on segment k [m/s²]
  def coast_acc(v, k):

      th = math.atan(gr_l[k] / 100)

      F = (rho / 2 * interp1(v, cv, cc) * v * v        # air drag, instantaneous (HDEV: VECTO uses the step average)
           + coast_mass**beta * g * Crr * math.cos(th)       # rolling resistance, mass without wheel inertia like VECTO
           + coast_mass * g * math.sin(th)             # slope force
           + interp1(v, drag_v, drag_F) )      # motor/gearbox drag while rolling

      return -F / m_eff         # divide by m_eff altho we use coast_mass because wheels add inertia not weight

  T, S, V, A, M = [], [], [], [], []    # rows: time, distance, speed, acceleration, driving mode
  t = 0.0                               #initialize start time
  s = s_wp[0]                           #initialize start position
  v = v_wp[0]                           # VECTO starts at the first waypoint's target speed (DistanceBasedDrivingCycle.cs line 107)
  s_end = s_wp[-1]                      # end position

  # standing rows at waypoint i
  def add_stop(i, t):

      for _ in range(int(round(stop_wp[i] / dt))): # for the number of dt time steps the stop happens
          T.append(t); S.append(s_wp[i]); V.append(0.0); A.append(0.0); M.append(0) #append stationary state to rows
          t += dt # increment time by the time step
      return t

  if v_wp[0] == 0:       # check if route starts at a stop
      t = add_stop(0, t)  # initial stop
      v = 0.0             # explicitly set the speed to 0

  trig = None   # active slowdown: [index, trigger distance, target speed, coasting allowed, braking started]
  max_steps = int(sum(stop_wp) / dt + (s_end - s_wp[0]) / 0.5 + 10000)  # guard against endless loops (truck must average > 0.5 m/s)

  #-----For each step
  for _ in range(max_steps):    # for all steps
      if s >= s_end - 1e-6:    # if travelled distance greater or equal to final distance break
          break
      k = bisect.bisect_right(s_wp, s) - 1             # waypoint segment we are in
      target = seg_v[k]                                # target speed for that segment
      v_os = target + os_add if target > os_min else target  # overspeed limit (VECTO IsOverspeedAllowed: > 50 km/h, +2.5 km/h)

      if trig is not None and s >= trig[1] - 1e-6:     # Check whether a previous slowdown trigger has been passed
          trig = None

      # look ahead (VECTO GetNextDrivingAction, lines 647-683)
      look = max(2 * v * dt, v * 3.6 * lac_dist_factor, 1.2 * decel_distance(v, 0.0, vv, vd) + v * dt) # max of:twice the vehicle travels in one step, distance based on speed,  the distance required to decelerate from the current speed to zero with safety factor
      j0 = bisect.bisect_right(chg_s, s)              # findin upcoming speed changes
      j1 = bisect.bisect_right(chg_s, s + look)
      best_b = None                                    # candidate with the earliest braking start
      best_c = None                                    # candidate with the earliest coasting start

      for j in range(j0, j1):     #loop thru every speed change way point in the look ahead range
          i = chg[j]
          vt = v_wp[i] + os_add if v_wp[i] > os_min else v_wp[i]  # target incl. overspeed (VECTO line 662)

          if vt >= v:           # Ignore speed changes that don't require slowing down
              continue
          b_start = s_wp[i] - (decel_distance(v, vt, vv, vd) + brake_margin) # Calculate the braking start position

          c_start = b_start   # initially coasting start is set equal to breaking start position
          if coast_on and v > lac_min:        # if coasting is on and if speed is above look ahead speed
              cd = coast_distance(v, vt, interp1(s, s_wp, alt_l), alt_l[i], s, s_wp[i],   # Calculate the coasting distance
                                  coast_mass, m_red_wheels, cv, cc, Crr, beta, rho, g, drag_v, drag_F,
                                  df_offset, df_scaling, df_vtarget, df_vdrop)

              if cd > 0:                                # if coasting distance is positive
                  c_start = s_wp[i] - cd                # calculate the coasting start position

          if best_b is None or b_start < best_b[1]:  #finds the upcoming speed change with the earliest braking start position
              best_b = (i, b_start, c_start, vt)
          if best_c is None or c_start < best_c[2]:   #finds the upcoming speed change with the earliest coasting start position
              best_c = (i, b_start, c_start, vt)

      action = None                                   # initially no driving action
      if best_b is not None:                           # VECTO: braking action, unless the earliest coasting one is the same point
          i, b_start, c_start, vt = best_b              # select earliest breaking candidate if there is at least one speed reduction coming up
          coast_ok = best_c[0] == i and c_start < b_start     # is coasting allowed for the same waypoint with breaking; must belong to same waypoint, coasting must start before breaking
          action = (i, s_wp[i], vt, coast_ok, min(b_start, c_start))    # creates a tupple; Waypoint index, Waypoint position, Target speed, Whether coasting is allowed, Earliest action start position

      if trig is None and action is not None and s + v * dt >= action[4]:  # start slowing down if the next step would pass the start point
          trig = [action[0], action[1], action[2], action[3], False]
      elif trig is not None and action is not None and action[1] != trig[1]:    #checks whether a new driving action has appeared while another slowdown is already active
          b_new = action[1] - (decel_distance(v, action[2], vv, vd) + brake_margin)     #Calculates the braking start position for the new target
          b_cur = trig[1] - (decel_distance(v, trig[2], vv, vd) + brake_margin)       #Calculates the braking start position for the existing target
          if b_new < b_cur:                            # a nearer slowdown needs earlier braking (VECTO CheckSwitchingToBraking)
              trig = [action[0], action[1], action[2], False, True]   # switch to new breaking action if new breaking is earlier

      # -- choose acceleration
      acc_max = interp1(v, vv, va)        #max acc allowed at current speed
      dec_max = interp1(v, vv, vd)        #max dec allowed at current speed

      if trig is not None:                #is there an active slowdown trigger
          i_t, s_t, v_t, coast_ok, braking = trig
          b_start = s_t - (decel_distance(v, v_t, vv, vd) + brake_margin)   # recalculate breaking start at current speed

          if 0 < v <= v_t:                             #situation 1; next target already reached; current speed > 0 and <= target speed
              a = max(dec_max, min(acc_max, (v_t - v) / dt)); mode = 2        #acceleration needed to reach target speed in 1 step limited by acc/dec limits
          elif coast_on and coast_ok and not braking and s + v * dt < b_start and v >= v_min_c:  #situation 2; coasting before braking start
              ca = coast_acc(v, k)                     # calculates the acceleration resulting from coasting
              a = min(ca, (max(target, v) - v) / dt)   # never faster than max(target, current speed)
              a = max(a, dec_max)                      # limits
              mode = 3 if a >= ca - 1e-9 else 4        # speed cap active -> braking, not coasting
          elif not braking and s < b_start:            # Situation 3: Braking starts during the current time step
              frac = (s + v * dt - b_start) / (v * dt) if v > 0 else 1.0      # fraction of the time step occurs after reaching the braking start position
              a = dec_max * min(max(frac, 0.0), 1.0); mode = 4  # factor is limited between 0 and 1
              trig[4] = True                           # breaking flag set to true, once braking, stay braking until the point
          else:                                        # Situation 4: Active braking
              rem = s_t - s                            # remaining distance to the target waypoint
              if rem < 2 * v * dt and v > v_t:         # checks whether the vehicle is very close to the target waypoint
                  a = (v_t**2 - v**2) / (2 * rem) if rem > 1e-6 else dec_max        # Adapt deceleration to the remaining distance
              else:                                    # If the vehicle is not yet within the final one or two time steps
                  a = max(dec_max, (v_t - v) / dt)     # calculates the acceleration needed to reach the target speed in one time step within limits
              mode = 4                                 # breaking
              trig[4] = True                           # set breaking flag

      else:                                            # when there is no active trigger
          if v < target - 1e-9:                        # does it need to accelerate
              a = min(acc_max, (target - v) / dt)      # calculates the acceleration needed to reach the target speed within one time step

              if P_max is not None and coast_on:       # optional motor power cap (HDEV simplification, not VECTO's motor search)
                  F_res = -coast_acc(v, k) * m_eff     # equivalent resistance force; F=ma
                  a = min(a, (P_max / max(v, 1.0) - F_res) / m_eff)   #estimates the maximum available acceleration after accounting for resistance forces
              if action is not None:                   # don't speed up so much that the next slowdown can't be braked for in time
                  room = action[1] - s - v * dt - brake_margin   # This calculates the remaining distance available after the current time step
                  v_cap = math.sqrt(max(action[2]**2 + 2 * -dec_max * max(room, 0.0), 0.0))   # maximum speed that would still allow the vehicle to reach target speed over reamining distance
                  a = max(min(a, (v_cap - v) / dt), 0.0)    # limits acceleration so that the vehicle does not exceed the calculated speed cap
              mode = 1                                # acceleration mode

          elif coast_on and target > os_min:           # at/above target with overspeed allowed: coast
              ca = coast_acc(v, k)                     # acc during coasting
              if ca >= 0:                              # coasting acc is > 0 (could be downhill)
                  a = max(dec_max, min(ca, (v_os - v) / dt))   # downhill: let it run up to target + 2.5 km/h, then hold
                  mode = 3 if a >= ca - 1e-9 else 4            # holding the speed needs brakes then switch to mode 4
              elif v + ca * dt > target:          # coasting would bring down speed below target speed   <-- COMMENT WRONG, see pending fixes
                  a = ca
                  mode = 3                     # roll back down towards target
              else:
                  a = (target - v) / dt; mode = 2      # would drop below target -> hold target
          elif v > target + 1e-9:                      # current speed greater than target
              a = max(dec_max, (target - v) / dt)      # calculates the acceleration needed to return to the target speed
              mode = 4                                 # above target without overspeed ; brake to target
          else:                                        # current speed equal to target
              a = 0.0
              mode = 2                        # cruise

      # ---------- move one step
      v_new = v + a * dt                               # update new speed
      if v_new < 0:                                    # does vehicle stop inside the step
          ds = v * v / (2 * -a) if a < 0 else 0.0      # calculate actual stopping distance
          v_new = 0.0                                  # set speed to 0 ; stopped
      else:
          ds = (v + v_new) / 2 * dt                    # distance travelled in one step

      if trig is not None and trig[2] == 0 and (v_new <= 0 or s + ds >= trig[1]): #Does the vehicle need to stop, and has it reached the point where it must stop
          ds = max(trig[1] - s, 0.0)                   # arrive exactly at the stop (HDEV: VECTO shortens the step instead)
          v_new = 0.0

      T.append(t); S.append(s); V.append(v); A.append((v_new - v) / dt); M.append(mode)
      t += dt
      s += ds
      v = v_new

      if trig is not None and trig[2] == 0 and v == 0:  # arrived at a stop
          s = trig[1]                                   # set stop position as exact stop postiion target
          t = add_stop(trig[0], t)                      #adds the required stationary time at the stop waypoint
          trig = None
  else:
      raise RuntimeError("driver_model did not reach the end of the route")  # guard only

  # ---after the loop: arrays + grade from altitude
  T = np.asarray(T); S = np.asarray(S); V = np.asarray(V); A = np.asarray(A); M = np.asarray(M, dtype=int)
  s_next = np.append(S[1:], s)                         # distance at the end of each row
  ds_row = s_next - S
  h1 = np.interp(S, s_wp, alt_wp)
  h2 = np.interp(s_next, s_wp, alt_wp)
  k_row = np.searchsorted(s_wp, S, side="right") - 1
  grade = np.where(ds_row > 1e-9, (h2 - h1) / np.where(ds_row > 1e-9, ds_row, 1.0) * 100, gr_wp[k_row])  # [%]; standing rows use the waypoint grade
  return T, S, V, A, grade, M
```

```python
# helper: look-ahead coasting distance, VECTO DefaultDriverStrategy.ComputeCoastingDistance (lines 721-756) - finalized
def coast_distance(v, v_target, h_now, h_target, s_now, s_target,
                   coast_mass, m_red_wheels, cdxa_v, cdxa, Crr, beta, rho, g, drag_v, drag_F,
                   df_offset, df_scaling, df_vtarget, df_vdrop):
  m_eff = coast_mass + m_red_wheels
  dE = m_eff * g * (h_now - h_target) + m_eff * (v**2 - v_target**2) / 2
  v_avg = (v + v_target) / 2
  cda = interp1(v_avg, cdxa_v, cdxa)
  F_air = rho / 8 * cda * (v + v_target) * (v**2 + v_target**2) / v_avg
  grad = (h_target - h_now) / (s_target - s_now)       # no atan: VECTO uses cos(rise/run) [DECIDED 3 Nov]
  F_roll = math.cos(grad) * coast_mass**beta * g * Crr  # β form [DECIDED 10 Nov]
  F_loss = interp1(v, drag_v, drag_F)                   # drag table at current speed v
  f_vt = interp1(v_target * 3.6, df_vtarget[0], df_vtarget[1])
  f_vd = interp1((v - v_target) * 3.6, df_vdrop[0], df_vdrop[1])
  DF = df_offset - df_scaling * f_vt * f_vd
  return dE / (DF * (F_air + F_roll + F_loss))
```

**Known HDEV deviations from VECTO in the driver (state in reports):**
- Fixed 1 s rows (VECTO ~0.5 s variable steps); step not shortened to land on braking start or stop point.
- Back-to-back stops: HDEV aims for the next positive target.
- Air drag in `coast_acc` is instantaneous (VECTO step average).
- Braking that starts mid-step is scaled by the fraction of the step after `b_start`.
- `P_max` single power cap (VECTO: motor torque curve).
- Fixed reference vehicle for coasting decisions (screening).

**VECTO line references checked 10 Nov (`IEPC-experiments`, `b8d6126`):**
- 1 s start stop: `DrivingCycleDataReader.cs` 221–223. Lines 224–226 throw if a waypoint has stop time > 0 and target speed > 0 (→ parser check).
- `MinVelocityForCoast = 5 km/h`: `Constants.cs` **301** on this branch (PR #21's "305" was another version).
- `g = 9.80665`: `DeclarationData.cs` 72; `AirDensity = 1.188`: 74; β = 0.9: `Physics.cs` 51.

**Smoke test (Claude, 12 Nov) [TEST]:** Bob's exact pasted code, made-up 10 km route (start stop, 80 → 50 → 80 km/h, 30 s stop, ±1–2 % grades, made-up `.vacc`, 10 t, made-up drag table): runs to the end with and without coasting and with `P_max` = 150 kW (made-up). Coasting replaced some braking (mode 3: 8 rows, mode 4: 36 → 33). Code check only, not validation. Found: a route where a stop is followed only by 0 km/h waypoints never moves off; the RuntimeError guard catches it (→ parser check).

### 3.1 What was checked earlier (Kiro PR #21, 2–3 Nov, verified by Claude)

**Kiro's work:**
- Repo `mohgsaad-art/hdev`, branch `driver-model-review-2026-11`, commit `18940ab`.
- Review doc: `docs/research/driver-model-review-2026-11.md`.
- Tests: `tests/driver_model/` (129 pass); `reference_copy.py` is the old code of record.
- VECTO runs: `docs/research/vecto/`.

**Housekeeping:** `src/engine/driver_model.py` in the repo is the stale April class version. Replace it with §3.0.

**Holds vs VECTO** (VECTO v5.1.3 commit `d16ba783c`; re-check line numbers before client citations):
- `interp1` = `np.interp`.
- `decel_distance` is exact (`AccelerationCurve.cs` 119–181).
- `coast_distance` matches term by term, apart from the drivetrain-loss term (`DefaultDriverStrategy.cs` 741–779). Now uses the drag table.
- **No atan** in `coast_distance` [DECIDED]: VECTO uses `cos(rise/run)`.
- Decision-factor tables and driver constants are exact.
- Standing time equals VECTO exactly: 746 / 3349 / 67 s [VMOD].
- Known deviation: back-to-back stops (above).

**Drivetrain coasting drag:**
- Missing drag was why HDEV coasted and overspeeded too much.
- VECTO drag at the wheels [VMOD]: 1.43 kN at about 45 km/h, rising to 2.05 kN at about 85 km/h.
- The E2 component files reproduce it [CALC]: 1.42 / 1.58 / 1.75 / 1.91 / 2.07 kN at 45 / 55 / 65 / 75 / 85 km/h. So **the parser can build the drag table from drivetrain maps; no .vmod is needed.**
- Kiro's "2× too low" note is wrong. [OPEN] Tell Kiro.
- With VECTO's drag table [TEST, D2]: coast share, overspeed and speed RMS match VECTO; Regional wheel traction is 67.2 / 67.2 kWh.
- A small leftover overspeed (~0.9 % vs ~0.1 %) is **accepted** [DECIDED].
- **Drag default [DECIDED 3 Nov]:** VECTO E2 drag table for all trucks; users with their own drivetrain data can supply it; constant-efficiency option also offered.

**Withdrawn Kiro claims:**
- LongHaul run with the wrong vehicle. Group-2 LongHaul is truck + trailer, CdxA 6.13 m², 19,811 kg ref.
- Low-load runs at reference mass.
- "2.0–3.4 kN drag" (it included air + rolling).
- The ".vsum shares are false alarm" claim is half right: the .vsum shares use acceleration thresholds of ±0.125 m/s².
- "Gap is classification".

**kWh/km targets** (generic E2, VECTO-equivalent weather, battery terminals):

| Version | Regional | Urban |
|---|---|---|
| Code today (0.95/0.95/0.98, no drag) | 0.712 | 0.574 |
| EU std maps | 0.947 | 0.815 |
| **EU std maps + std drag (target)** | **0.971** | **0.844** |
| + battery losses (OCV + Ri) | 0.979 | 0.854 |
| VECTO `.vsum` | 1.050 | 0.840 |

[DECIDED, 3 Nov] Target is row 3, then row 4 once battery losses are built. Regional stays about 8 % under VECTO because the EU standard motor map is more efficient than VECTO's example motor.

Open items:
- Optional VECTO run R5 (look-ahead off, engineering mode).
- LongHaul trailer payload rule (only if HDEV must compute it).
- No independent coasting validation found yet. Possible check: TUM 10 Hz truck GPS (Zenodo 16411298, ODbL) for speed profiles.

---

## 3b. PTO (design final 31 Oct; consumption side still open)

**VECTO [VECTO]:**
- Stop PTO (label 1) is the only kind used in declaration (Municipal).
- Sweeping (2) and drive PTO (3) exist in engineering mode only (`PowertrainBuilderBase.cs` 325, 339).
- For a BEV, drive PTO goes on the motor shaft (321–349).
- Standing time = stop + PTO duration (`DistanceBasedDrivingCycle.cs` 218–220).
- The PTO runs in the middle of the stop.
- Refuse profile: 23 s, **0.14993 kWh per stop**.

**Design [DECIDED]:**
- No 0/1/2/3 labels. Each waypoint has one on/off flag. If on, there can be a **stop part** and/or a **drive part** (from leaving that stop until the next stop).
- Each part is one number (fills its window) or a profile (plays its own seconds once).
- A drive part still running at the next stop keeps running (VECTO).
- A 0 s marker row can start a drive part.
- One sweeping power per route (a deviation from VECTO, flagged).
- Always-on PTO stays in `P_aux`.
- Constants skip `pto_engine`.
- **Efficiency fields** per kind (stop / drive / always-on), default 1.0. The engine divides by them (electric = entered ÷ eff).
- Readable code: one step per line.

**`pto_engine` code of record (1 Nov):**
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

  too_short = np.where(pto_start < 0)[0]
  if len(too_short) > 0:
      raise ValueError(f"PTO ({pto_dur} s) is longer than the stop at waypoint(s) {too_short.tolist()}; the parser must extend these stops")

  #apply the effeciencies
  stop_1s = stop_1s / stop_pto_eff
  drive_1s = drive_1s / drive_pto_eff

  return is_on, pto_start, stop_1s, drive_1s
```

**Consumption side [OPEN]:**
- Stop profile: from the first standing row of that stop + `pto_start`.
- Stop constant: on all standing rows of the stop.
- Drive profile: from the first moving row after the stop, running past the next stop.
- Drive constant: on all moving rows until the next stop.
- Constants are divided by their efficiency when placed.
- Overlap check for drive jobs (VECTO raises an error).
- Cond rule for the drive part.

**Parser jobs:**
- Read `.vptoel` / `.vptor`; convert kW to W.
- Times must be whole seconds and increasing; no negative W.
- `is_on` must have one value per waypoint.
- VDRI `<PTO>` mapping: 1 → stop part; 2 → drive constant; 3 → `.vptor` profile.
- Stop extension (VECTO default; "use stop time as PTO time" option flagged).
- Reject two stops at the same distance.

**Report flags:**
- PTO is placed in the middle of the stop, using floor for odd seconds.
- Sweep power is constant.
- Drive PTO efficiency 1.0 skips motor losses.
- Per-second holding (VECTO averages).
- Drive PTO is an engineering-mode feature.

**Profile library:**
- Only the VECTO refuse profile is an official default.
- Driving PTO has no sourced default; the user must enter it.
- Every entry needs a source, a tag (measured / simulated / rating) and a licence check.
- Leads: Ban & Stipetić 2019; MDPI Appl. Sci. 11(7) 3033; VTT refuse ~2.3 kWh/km.

**Parked:**
- **Fridge (TRU) model:** K = W/(S·ΔT) (ATP); K from the ATP certificate, or the class limit (0.40 / 0.70) flagged. COP is required (no default). Heating mode when outside is colder than set temperature. No door uplift; urban results labelled a lower bound. Needs `PTO_always_on` per hour.
- **PTO shaft drag:** VECTO `PTO-tech.csv` torque loss, only with a gearbox. Waits for the drivetrain maps.
- **Per-truck assignment** of routes / PTO / payload: a saved library with "apply to all".

---

## 3c. `consumption_engine`: current form (21–22 Oct; Bob's notebook is authoritative)

```python
def consumption_engine(T, S, V, M, dt,                                   # driver_model rows
                       k_lin, k_roll, k_rot, L, v_avg,                   # force_engine
                       m_vehicle, wp_s, payload_wp, beta,                # mass; payload_wp from payload_engine
                       t_start, T_amb_h, W1, W2, cdxa_v, CdxA0, p_air, R_air,  # weather per hour + crosswind tables + air constants
                       ES, PS, HVAC, SP, cond, PTO_always_on,            # P_aux outputs (HVAC scalar or per hour)
                       pto_1s, pto_on_col, pto_start_col,                # pto_engine outputs
                       motor_eff, inverter_eff, gearbox_eff, regen_effeiciency, v_no_regen, P_regen_max=None):

  T, S, V, M = (np.asarray(x) for x in (T, S, V, M))                              # driver rows
  wp_s, payload_wp = np.asarray(wp_s, dtype=float), np.asarray(payload_wp, dtype=float)
  T_amb_h, cdxa_v = np.asarray(T_amb_h, dtype=float), np.asarray(cdxa_v, dtype=float)
  pto_1s, pto_on_col, pto_start_col = (np.asarray(x, dtype=float) for x in (pto_1s, pto_on_col, pto_start_col))

  # --- 1. mass per row: payload forward-filled by distance (payload_engine writes it on start + stop waypoints only)
  has_pl = ~np.isnan(payload_wp)
  k_pl = np.searchsorted(wp_s[has_pl], S, side="right") - 1
  m_row = m_vehicle + payload_wp[has_pl][k_pl]                     # [kg]

  # --- 2. weather hour of each row
  hour = ((t_start + T) // 3600).astype(int)

  # --- 3. air density and CdxA_eff per row
  rho_row = p_air / (R_air * (T_amb_h[hour] + 273.15))             # ideal gas, fixed pressure (HDEV; VECTO fixed 1.188)
  cdxa_tab = CdxA0 * np.asarray(W1) + np.asarray(W2)               # VECTO AirdragDataAdapter.cs 59-87
  v_kmh = np.clip(v_avg * 3.6, cdxa_v[0], cdxa_v[-1])              # below 60 km/h uses the 60 value like VECTO
  j = np.clip(np.searchsorted(cdxa_v, v_kmh, side="right") - 1, 0, len(cdxa_v) - 2)
  w = (v_kmh - cdxa_v[j]) / (cdxa_v[j+1] - cdxa_v[j])
  cdxa_row = cdxa_tab[hour, j] * (1 - w) + cdxa_tab[hour, j+1] * w

  # --- 4. wheel power per row [W]
  P_wheel = m_row * k_lin + m_row**beta * k_roll + k_rot + rho_row * cdxa_row * L

  # --- 5. wheel power -> electric traction power [W]
  drivetrain_effeiciency = motor_eff * inverter_eff * gearbox_eff
  P_trac = np.where(P_wheel > 0, P_wheel / drivetrain_effeiciency, P_wheel * regen_effeiciency)
  P_trac = np.where(M == 3, 0.0, P_trac)                           # coasting: no motor torque (BatteryElectricMotorController.cs 44-46)
  P_trac = np.where((M == 4) & (V <= v_no_regen), 0.0, P_trac)     # braking <= 5 km/h: brakes only (same file 62-69; Constants.cs 323)
  if P_regen_max is not None:
      P_trac = np.maximum(P_trac, -P_regen_max)

  # --- 6. aux power per row [W]
  n = len(T)
  pto_row = np.zeros(n); pto_active = np.zeros(n, dtype=bool)
  for i in np.where(pto_on_col == 1)[0]:
      at_stop = np.where((V == 0) & np.isclose(S, wp_s[i], rtol=0, atol=1e-3))[0]
      if len(at_stop) == 0:
          raise ValueError(f"no standing rows found for stop at {wp_s[i]} m")
      k0 = at_stop[0] + int(pto_start_col[i]); k1 = k0 + len(pto_1s)
      if k1 > at_stop[-1] + 1:
          raise ValueError(f"PTO does not fit in stop at {wp_s[i]} m")
      pto_row[k0:k1] = pto_1s; pto_active[k0:k1] = True
  moving = V > 0
  HVAC_row = np.asarray(HVAC, dtype=float)[hour] if np.ndim(HVAC) else float(HVAC)
  P_aux_row = ES + PS + HVAC_row + SP * moving + cond * (moving | pto_active) + PTO_always_on + pto_row

  # --- 7. battery terminals
  P_battery = P_trac + P_aux_row                                   # DC/DC eff 1.0 (DeclarationData.cs 124); battery Ri loss -> battery engine
  E_battery = np.sum(P_battery * dt) / 3.6e6
  return P_wheel, P_trac, P_aux_row, P_battery, E_battery
```

**Known gaps in this form:**
- It still uses the **old `pto_engine` outputs** (`pto_1s`, `pto_on_col`, `pto_start_col`). It must be updated to the 1 Nov outputs (`is_on`, `pto_start`, `stop_1s`, `drive_1s`) and the drive part added (§3b).
- Fixed efficiencies: the main error.
- Regen cap.
- Coast rows: motor gives 0 torque, so `P_trac = 0` is right; drivetrain drag acts only through the driver's speed (it slows the truck faster). Nothing more needed here (clarified 10 Nov).
- Cond and SP rules differ from VECTO (§5 item 4).
- No battery loss.
- Rolling: consumption already uses the β form, now the same as the driver (§3.0).

Flags:
- ρ from ISO 2533 p and R (VECTO uses a fixed 1.188).
- Hourly weather is held for the whole hour.
- Payload changes on arrival.

---

## 4. Validation and fallback summary (details in the 11-07 closeout)

- On the Fuso eCanter (standard-value IEPC, certified), HDEV with EU standard values is within ±3.3 % of EEA. So driver, forces, tyres, aux and crosswind are about ±3 % when drivetrain data is right.
- Today's constant efficiencies are 3–38 % off on 10 EEA trucks.
- No uncalibrated fallback stays within ±10 % on all trucks. The bus method (V-C) is the most even.
- Calibration to EEA certified results, leave-one-out:
  - Method C (drive eff + regen eff + F0, + CdxA if measured) works on every truck; 7 of 10 are within 5 %.
  - Method D (bus IEPC map + loss scale) is ≤ 2 %, but single-gear trucks only.
- [OPEN, Bob] Default drivetrain rule:
  - truck in EEA → calibrate (C, or D for single-gear IEPC);
  - otherwise → V-C with a stated error band.
- 9 Nov tools review: nobody does drivetrain better without data. Load-dependent efficiency (FASTSim, KIT) is the best-practice fallback. NREL also calibrates. Drivetrain maps are treated as an **input/parser question**, not a blocker [DECIDED, 9 Nov].
- Accuracy target [DECIDED 7 Nov]: HDEV kWh/km error ≤ 5 %. The reference-driver error (§6: ≤ 0.4 % Regional, ≤ 1.3 % Urban) uses part of that budget in screening runs.

### 4b. VECTO BEV_E2 run and part-by-part comparison (22 Oct) [VSUM/VMOD]

**The run:**
- VECTO 5.1.6-RC, declaration mode, `BEV_E2.vecto`.
- Outputs are on Bob's PC and in the repo at `docs/research/vecto/`.
- Declaration starts and ends at 50 % SoC.

**VECTO results (reference load):**
- Regional 1.050 and Urban 0.840 kWh/km at the battery terminals.
- LongHaul 1.550 (truck + trailer).
- Low load: Regional 1.0022, Urban 0.7566.

**Wheel physics matches VECTO:**
- rolling is exact;
- air −0.1 % / −2.2 %;
- positive wheel energy −2.3 % / −1.3 %.

The 32 % gap was the fixed drivetrain efficiencies:
- VECTO gearbox + axle losses 23.0 / 22.4 kWh, motor 20.0 / 18.4 kWh;
- VECTO battery loss ≈ 0.92 / 1.03 kWh.
- With VECTO's trip-average efficiencies, HDEV is −2.4 % / −4.1 %.

Aux matches after the harness fix:
- PS "Vacuum pump + elec. driven";
- SP "Full electric steering gear" (23.0 / 32.0 W);
- totals +0.7 % / +1.9 %.

VECTO Cond rule: on whenever any motor is not EmOff (`Conditioning.cs` 83–91). It is 0 when standing and when coasting. [OPEN, §5 item 4]

Regen with fixed efficiency: 88 % of wheel braking, vs VECTO 57 % / 73 %.

### 4c. Independent validation, drivetrain maps, winter, battery sizing (22 Oct)

**kWh/km sources (12 t class)** (full links are in the archived 10-22 closeout):
- MAN eTGL 0.69 (OEM);
- Renault D12 0.80 [CALC];
- DAF XB 0.81 [CALC];
- Volvo FL 0.73 (measured, hot) and 1.00 (fleet guide);
- NREL Smith Newton 0.79–0.87 (measured);
- Öko eActros 0.67–0.72 (measured medians);
- MAN fleet 0.90;
- Bob's Danish regression 0.796 @ 11.99 t; Liimatainen 0.855.

**Charger + battery chain:** 82–91 %, median 85.5 % (CARB App. G); NREL 90 %. Not in HDEV yet. [OPEN]

**Standard-value drivetrain maps** [REG]:
- Gearbox: Annex VI App. 8 (Td0 = Td1000 = 0.005·Tmax_in; fT 0.04 indirect / 0.01 direct).
- Axle: Annex VII App. 3 (η 0.98, Td0 = 70 + 20·i), built like VECTO's generic axle.
- Motor: Annex Xb App. 8 (ASM k_mn × 0.96; drag curve).
- IEPC: App. 9.

Results:
- **Gearbox Tmax_in is the most sensitive input (about ±20 %)** and is not on spec sheets.
- With the maps, regen recovers 64 % / 75 % (VECTO 57 % / 73 %).
- Gear 2 is used > 99 % of the time, so no shift strategy port is needed.

**Winter pieces** (harness add-on, DMI 2025):
- At −5 °C, Regional goes 1.016 → 1.096 kWh/km. Contributions: battery losses, HVAC, fresh air, and cold tyres (ISO 28580 Kt 0.006, used outside its 20–30 °C range).
- January vs July: +6.5 % / +8.3 %.
- Measured data show more: Öko ≈ +21 %; e-buses +14 to +45 %. **Winter is still short.**
- Missing:
  - battery heating (≈ 4 %, Dollinger 2021, model);
  - cold Ri;
  - door openings;
  - snow/slush;
  - Cond thermal.

**Battery sizing for a ~100 km day** (kWh/km × 100 ÷ 0.8 SoC window, design day):
- HDEV Regional 127–134 kWh, Urban 111–119 kWh.
- VECTO 146 / 117 kWh.
- Independent figures 95–138 kWh.
- Bob [DECIDED]: "our ranges were actually good". Once Monte Carlo is added, they become a confidence band.

**Agreed code changes (22 Oct; most are in §5):**
- Parser builds the standard maps and the coast-drag table.
- Optional upload of real VECTO component files.
- Consumption step 5 becomes a per-row chain (wheel → axle → gearbox → motor map → electric): highest gear unless torque-limited; regen cap from the generating-torque curve.
- Cold-tyre term, switchable: rolling × 1 / (1 + Kt·(T − 25)).
- HVAC thermal per hour with `HVAC_eff = 1.0`.
- Battery: OCV + Ri with SoC, using App. 10 standard values as the fallback.
- The "atan in `coast_distance`" item from this list was **cancelled** on 3 Nov.

**Earlier validation:**
- T13 vs VECTO 2.2 12 t truck: rolling +0.02 %, air +1.1 %, positive wheel energy −2.0 %.
- eActros-like vs Öko regression: mild weather at or above measured; winter clearly under.
- Temperature slope is only 7–28 % of the measured −0.013 kWh/km/°C.

---

## 5. Next steps: finalise functions, one at a time (Bob decides the order)

Done since 9 Nov: old items 1 (driver part A bugs), 2 (rolling form → β everywhere), 3 (`P_max` → kept, flagged).

1. **`force_engine`** section-by-section review (next). Check against the driver:
   - β form: `k_roll = Crr·g·cos θ·v_avg`, mass applied as `m^β` in consumption: consistent.
   - Grade angle: both use `atan(grade/100)`.
   - Wheel inertia: `theta_red / r_dyn²` must equal the driver's `m_red_wheels` (parser computes it once).
   - Test cell `g = 9.81` → 9.80665.
2. **`P_aux` fix:** add the `PTO_always_on < 0` and `PTO_eff <= 0` checks; remove the stale comment.
3. **`pto_engine` test cell:** 8-argument call, 4 outputs.
4. **`SP_power_helper`, HVAC functions:** read-through only.
5. **Aux timing vs VECTO:** HDEV runs SP only while moving and cond only while moving or PTO-active. VECTO aux are `DemandType.Constant` and cond is Dynamic (`HeavyLorryAuxiliaryDataAdapter.cs` 61–110). Decide in the consumption review.
6. **`consumption_engine` review:**
   - switch to the 1 Nov `pto_engine` outputs and add the drive-PTO part (§3b, §3c);
   - replace fixed efficiencies with maps (the biggest fix);
   - regen cap rule (KIT: rated motor power);
   - no regen at full battery;
   - battery-loss hook;
   - SP on when v > 0.01 m/s.
7. **Battery model (OCV + Ri) and charging engine rebuild.**
   - App. 10 standard values: OCV, HEBS DCIR, HEBS max charge 0.9 C to 80 % then 0 at 100 %.
8. **Parser (`defaults.py`):** all jobs in §2, §3.0, §3b and §6.

Other open items:
- Read Dvorak 2025 to confirm 100 m³/h.
- NREL TP-5400-66860 for cab data.
- Danish weights order and modulvogntog (retsinformation.dk).
- EUR-Lex Art. 10b (1 t vs 2 t).
- Cold tyres: Chalmers Crr range and the Mercedes tyre-class effect.
- Cond rule with always-on PTO and the drive-PTO part; BEV "motor off" = `EmOffPrev` (EM torque null).
- Driver: up to 1 km/h over target on a few rows where a 1 s row crosses close waypoints.
- Payload-slope split vs VECTO (needs the LowLoading `.vmod`).
- VECTO engineering-mode run for Municipal + PTO.
- ".vsum EM total rated power 500 kW" vs 2 × 125 kW: not explained.
- Charger + battery chain losses for depot energy.
- Fix or replace `dmi_weather_climatology.py` in the repo (it averages across years).
- Replace the stale `src/engine/driver_model.py` in the repo with §3.0.
- Later: `P_max` power cap vs VECTO motor torque curve (§3.0 item 6).
- Final exact pass: which single `coast_mass` to use when payload changes along a route (start, mean or other) [OPEN, untested].

---

## 6. Session 10–12 Nov 2026: decisions and findings

**Reference driver vs exact driver (Kiro PR #29, branch `driver-reference-sensitivity-2026-11`, folder `docs/research/driver-reference-sensitivity-2026-11/`) [TEST, checked by Claude against the CSVs]:**
- Question: how much kWh/km changes because the driver's coasting uses the reference mass, ρ = 1.188 and CdxA at VECTO declaration wind (3 m/s at 4 m), instead of the true values. Energy step identical in both (Chain S, E2 drag table, constant aux).
- Gate passed: `run_steps.py` reproduces Regional 0.9749 / Urban 0.8502. With drag read at `v` (Bob's code): 0.9746 / 0.8498.
- Realistic corners (empty to TPMLM × −10/+30 °C × 0/8 m/s): Regional −0.39 % to 0.00 %; **Urban −1.31 % to +0.68 %**. Including the impossible 0.5× / 1.5× masses: −0.40 % / −1.89 %.
- **Mass is the cause** (largest input in 31 of 32 corners). Temperature alone < 0.19 %, wind alone < 0.43 %.
- Direction: light loads → reference driver **underestimates** (up to −1.3 % Urban empty); full load → overestimates (+0.2 to +0.7 %).
- No-coasting driver within 0.8 % of the matched driver (coasting only 2–4 % of moving time on these cycles).
- Timing (Intel Xeon 8488C): driver 0.056 s Regional / 0.132 s Urban per run; energy step 0.0015 / 0.0042 s.
- Caveats: no 10° yaw clamp; `theta_red = 0` in the energy step; ~0.1 % differences are noise; only Chain S + E2 drag; no VECTO comparison, no real weather or HVAC.

**Decision [DECIDED 10 Nov]:** screening and sizing sweeps use the single reference driver run (VECTO-traceable: VECTO's own driver uses the same reference mass, ρ and declaration crosswind; error measured small). For the chosen truck, a **final pass** reruns the driver at exact mass (and weather if wanted). `force_engine` stays mass-free; the energy step reuses the driver rows.

**Why mass sits in both the driver and the energy step (explained 10 Nov):** energy depends strongly on mass, driving decisions only weakly (when coasting starts). The slow driver loop runs once at the reference; the fast energy step runs with true mass for every case. `coast_acc` and `force_engine` are kept as two functions (opposite questions: acceleration from forces vs power from acceleration; scalar `math` in the loop vs numpy arrays), but must use the same formulas: β rolling form, same `g`, same wheel inertia.

**Reference mass:** not fixed. Parser sets it per vehicle and mission = empty mass (curb + body/trailer) + VECTO reference payload (`Payloads.csv`; groups 1–3 by GVW, 50 % column interpolated at TPMLM, `Payloads.cs` 54–57; fixed per group ≥ 4; differs by mission). E2 test: 6,570 + 3,019.59 kg.

**New parser jobs (10–12 Nov):**
- Pass all driver speeds in m/s (`wp_v`, `vacc_v`, `cdxa_v`, `lac_min_v`, `os_min_v`, `os_allowed`, `v_min_coast`).
- Pass `drag_v` (m/s) / `drag_F` (N) as lists or tuples, never plain numbers.
- Pass the same `Crr` (= `Crr_eff`) and `beta` to the driver, `coast_distance` and consumption.
- Compute `m_red_wheels = theta_red / r_dyn²` from the same inputs as `force_engine` (harness assumption: motor rotor inertia ignored).
- `coast_mass` = reference mass per vehicle and mission (screening) or exact mass (final pass).
- Reject a waypoint with stop time > 0 and target speed > 0 (VECTO `DrivingCycleDataReader.cs` 224–226 throws).
- Reject a route where a stop is followed only by 0 km/h waypoints (the truck never moves off).

**Kiro prompt saved:** `claude/kiro-prompt-driver-reference-sensitivity-2026-11-10.md` (ran as PR #29).

---

## 7. Archive (GitHub)

Batch 2 (9 Nov 2026) is `hdev-archive-batch2-2026-11-09.zip` in `mohgsaad-art/hdev`, `main`, commit `f7d2da4`, checksum verified. Its `ARCHIVE_INDEX.md` lists each file. It holds:
- all engine closeouts from 6 Oct to 31 Oct;
- the 10-12 status, year/day and code-snapshot docs;
- the executed Kiro prompts;
- harness v1.5 and v1.6, the winter tests, the maps tests and the drag add-on;
- the 6 and 7 Nov data-library closeouts.

Where the full detail lives:
- full VECTO tables: 10-08 P_aux and 10-19 closeouts;
- 21 Oct driver research: 10-21 closeout;
- validation links: 10-22 validation closeout.

Batch 1 (9 Nov 2026) is at `mohgsaad-art/hdev`, `main`, file `hdev-archive-batch1-2026-11-09.zip`.
- Commit `cbe39e1`.
- SHA-256 67e07d51e6cdccd5e0fe9ec2e5e2e2a3a02e19902ef67ad7645c8be156f00111, verified against the copy sent.
- `ARCHIVE_INDEX.md` inside lists each file.

Removed from the project on 9 Nov:
- the 11-01, 11-02 and 11-03 closeouts;
- "Current code - 14th April 2026" and "Summary";
- all 29 VECTO .cs copies. 26 are on `mohgsaad-art/VECTO` branch `IEPC-experiments`; WheelEnd, ShiftStrategyFactory and FuelCellSystem are in the zip.
