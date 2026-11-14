# HDEV handover: function finalization (closeout 2026-11-12)

Written for a new chat. Read this first, then continue from "Where we stopped" and "Next steps".

## 0. How to work with Bob (standing rules)

- Bob builds and codes. Claude helps. Write code only when he asks.
- One step at a time. Lead with the direct answer. Short, simple English.
- Mention every assumption and simplification explicitly. Never present them as fact.
- No invented numbers. Every value must be verifiable from an authentic source (VECTO, regulation, ISO, paper).
- Ask for code, files and VECTO code whenever needed.
- Engine functions are pure maths with all parameters as arguments. The engine does the calculations. The parser only does lookups, checks, defaults and gap-filling. (Bob rejected calculations in the parser: "crazy stupid".)
- Everything inside the engine is SI units (m/s, not km/h).
- HDEV must not underestimate energy. Avoid features that need hard-to-get user inputs.
- Kiro prompts: very detailed, one uninterrupted pass with gates, tags ([VECTO], [REG], [SOURCE], [CALC], [TEST], [ASSUMPTION]), "Bob to fetch" lists, NO SOURCE / BLOCKED lists. In files prepared for Kiro, refer to him only as "Bob".
- Do not claim Bob decided something unless he said it. (Past mistake: I said he decided on 10 Nov that `m_red_wheels` is computed in the parser. He had only said "lets proceed". I had proposed it.)

## 1. Context

- Project: HDEV, a VECTO-auditable EV truck and depot sizing engine ("PVsyst for EVs"). Repo `mohgsaad-art/hdev`. VECTO fork `mohgsaad-art/VECTO` (branch `IEPC-experiments`, commit `b8d6126`). VECTO 5.1.6-RC `.vmod` files (E2 BEV; Regional / Urban / LongHaul; ReferenceLoad / LowLoading).
- Pipeline: payload/PTO on waypoints -> crosswind_engine -> driver_model (1 s rows) -> force_engine -> consumption_engine -> battery/charging -> sizing.
- `force_engine` returns mass-free coefficients `k_lin, k_roll, k_rot, L, v_avg`. Wheel power is `P_wheel = m*k_lin + m^beta*k_roll + k_rot + rho*CdxA_eff*L` (beta = 0.9; `Crr_eff` reproduces VECTO's per-axle rolling resistance).
- Process: for each function, Kiro (AWS agent, works on branches and opens PRs) digs deep and tests beyond VECTO (standards, ISO, papers, other tools). Small functions are grouped.
- Code of record: `docs/research/inputs/HDEV_NEW_code_of_record_2026-11-12.ipynb` (17 cells), on both Kiro branches.

## 2. What was done this session

1. Wrote two Kiro prompts and saved them in the repo and in the project:
   - `docs/research/inputs/kiro-prompt-force-engine-review-2026-11-12.md` (branch `force-engine-review-2026-11`, commit 65f091a). Covers `force_engine` and steps 1-4 of `consumption_engine`. Parts A-K, three gates, Q1-Q10 on VECTO. Executed as **Kiro PR #30**.
   - `docs/research/inputs/kiro-prompt-aux-pto-review-2026-11-12.md` (branch `aux-pto-review-2026-11`, commits 7ba2ad7 and 6fa495e). Covers `P_aux`, `SP_power_helper`, `pto_engine`, and steps 6-7 of `consumption_engine`. HVAC is out of scope. Executed as **Kiro PR #31**. Commit 6fa495e added the rule to pass the driver thresholds in m/s.
2. Pushed Bob's latest notebook to both branches (identical bytes).
3. Reviewed PR #30 and PR #31 and spot-checked key numbers.
4. Agreed edits with Bob (see section 6).
5. Answered Bob's question "are all functions final?" (verdict in section 4).

## 3. Kiro results

### PR #30 (force engine)

Outputs: `docs/research/force-engine-review-2026-11.md`, folder `docs/research/force-engine-review-2026-11/`, `tests/force_engine/` (37 tests), `docs/explainers/force-engine-explained.md`, `reference/vecto/jobs/force-engine-2026-11/`.

- `force_engine` matches VECTO to within 0.012 % of positive wheel energy when fed VECTO's own trace.
- The remaining error is the driver: +0.27 % Regional, +2.55 % Urban, +0.43 % LongHaul.
- `v_act` in the `.vmod` is the interval mean. Reading it as the start speed adds +0.57 % / +3.8 %.
- Bugs found:
  - Negative or NaN `theta_red` is silently dropped.
  - An array `theta_red` crashes.
  - `r_dyn = 0` divides by zero.
  - Latent: a row just before `wp_s[0]` wraps to the last payload.
  - VECTO errors above 130 km/h while HDEV holds the value.
- Rotor inertia: VECTO applies it at the motor shaft (0.228 / 1.22 kWh; +0.30 % / +1.49 % if reflected to the wheel).
- Part F candidates (none built):
  - Cold-tyre factor: model end points only, Crr 0.007 -> 0.014 from 20 to -20 degC (Ramesh Babu 2025). +6.2 % to +18.7 % on Regional.
  - Wet/ice roads: VTI 971 numbers were unread by Kiro. Askerdal 2025 ice Crr 0.0093-0.0158.
  - Humidity: negligible.
  - Altitude: -6.1 % Regional at 1000 m, -11.6 % at 2000 m (needs a parser-supplied `p_air`).
  - Curve resistance: no sourced data.
  - GPS grade noise: raw 0.5 m noise adds +21 % / +41 %; smoothing needed.
  - Coast-down A,B,C mapping: +0.12 % / +0.05 %.
- Part G, tool comparison: FASTSim takes air density from temperature and elevation per step. SUMO has a rotating-mass term and a curve term. eflips-depot uses a consumption look-up table.
- Part H: no measured wheel-power split exists, so the road-load model is not independently validated.
- "Bob to fetch" list (Kiro could not open): Hyttinen 2023 (doi 10.1016/j.polymertesting.2023.108004), VTI 971, UN R117, ISO 28580, etc.

### PR #31 (aux and PTO)

Outputs: `docs/research/aux-pto-review-2026-11.md`, `docs/explainers/aux-and-pto-explained.md`, `tests/aux_pto/` (113 tests), `reference/vecto/jobs/aux-pto-2026-11/`, a tested step-6 variant in `reference_copy.py`.

- `P_aux` and `SP_power_helper` match VECTO for all 68,040 combinations (max diff 4.5e-13 W).
- MunicipalUtility refuse case: 96 stops x 0.14993 kWh = 14.393 kWh (I confirmed: 96 stops, stop time 2 s, 25 s standing with 23 s PTO centred).
- Aux timing: HDEV aux is 0.26-1.15 % above VECTO, i.e. 0.012-0.090 % of trip energy, all from Cond running while coasting. Kiro recommends keeping the rule.
- Bugs:
  - Fractional profile times are truncated silently (`astype(int)`).
  - `consumption_engine` cannot take the 1 Nov `pto_engine` outputs (marker waypoint, dropped drive profile, `int(NaN)`).
  - `P_aux` lacks `PTO_always_on < 0` and `PTO_eff <= 0` checks (`PTO_eff = 0` gives inf, NaN passes).
  - Standing-row off-by-one: `V == 0` finds stop + 1 rows, +4 % on a 25 s stop constant. Use `M == 0`.
  - Per-stop `np.where` is O(rows x stops). Use `searchsorted`.
- New, unconfirmed: a BEV that declares a mechanical PTO type gets constant torque loss on every mission, calculated up to 15.8 kWh/100 km for the oil-pump type. Kiro itself flags this as a likely over-estimate (VECTO table lists 3 kW). Needs VECTO run 2.
- Drive-PTO efficiency default 1.0 treats a sweeper PTO as electric, whereas VECTO's is mechanical on the motor shaft.
- No [REG] statements (Annex IX is not in the repo). No source for the HVAC 0.8 factor or the Cond split. Validation is only a plausibility check against one VTT winter refuse truck. LongHaul with HDEV driver rows, and mixer/fridge validation, are blocked.

Aux logic reminder: `P_aux` multiplies ES 0.7, PS 1.0, HVAC 1.25, SP 0.7, Cond 1.0. Always-on PTO is divided by `PTO_eff`. `SP_power_helper` matches VECTO `SteeringPump.cs`. `pto_engine` returns `is_on, pto_start, stop_1s, drive_1s`.

## 4. Verdict given to Bob: which functions are final

"No, not everything is final." Code matches VECTO, but some improvements beyond VECTO still need a decision.

**`force_engine`**
1. Rotor inertia in `m_red`: agreed, Bob is doing the edit.
2. Optional coast-down input `F = A + B*v + C*v^2`: needs one new mass-free coefficient `k_B = v_avg^2`. Effect on the E2 is small (+0.12 % / +0.05 %) but lets users with real test data skip the Crr/CdxA assumptions. **Bob must say yes or no.**
3. Nothing else. Kiro checked `asin` vs `atan`, CdxA at start or end speed, slope mass, and none is better than the current code.

**Wheel power (`consumption_engine` steps 1-4)**, where temperature- and weather-dependent items belong (`force_engine` stays temperature-free)
3. Cold tyres: +6 % to +19 % of wheel energy at +10 to -10 degC (model, Chalmers). Not built because Kiro had one simulation source and no measured curve. Bob uploaded the measured paper (Hyttinen 2023, Scania/KTH). Largest open item, and it fits the "do not underestimate" rule.
4. Wet or snowy roads: on ice, one measured truck showed rolling resistance about double (Askerdal 2025). Not built because Kiro could not map rain/snow to a factor. Bob uploaded VTI 971A. DMI hourly precipitation is already available, so this needs no new user input.
5. Air pressure from altitude: open choice between (a) one pressure per route from altitude, or (b) per row. I suggested (a). The engine computes density; the parser supplies the pressure input.
6. Humidity: not worth it (<= 0.25 %, ignoring it is the safe side).
7. Curve resistance: no measured source. Skip.

**Not engine work, noted**
- GPS grade must be smoothed (raw noisy altitude inflates energy by +20 % to +190 %). Job for the GPS adapter, later.
- The driver's 1 s step costs about 1 % on Urban. `dt` is already an argument, nothing to change.

**`P_aux`, `SP_power_helper`, `pto_engine`**
- `P_aux`: add the missing checks, plus NaN/inf. Otherwise final.
- `SP_power_helper`, `pto_engine`: final.
- Drive PTO: one yes/no input ("does the body have its own motor?") to set the efficiency.
- Still open: mechanical-PTO drag (waits for VECTO run 2); fridge model (parked, needs ATP data); measured standing aux and Cond data (Kiro found none).

**Not reviewed yet:** HVAC functions (`HVAC_thermal`, `ssm_total_w`, `climate_lookup`), consumption steps 5-7 (drivetrain, regen, battery hook), the driver defaults, the battery, the parser.

Bottom line: `force_engine` is final after Bob's edit plus a yes or no on the coast-down input. The wheel-power part is not final until items 3 and 4 are decided.

## 5. Where we stopped

I had offered: read the two PDFs Bob attached and come back with the measured numbers for cold tyres and wet roads, and whether they are solid enough to build. Bob's reply was to save this handover and continue in a new chat. The PDFs have not been read by me yet.

Attachments from this session (re-attach in the new chat if needed):
- `VTIrapport971A.pdf` (VTI report 971A, water/snow on roads and rolling resistance)
- `S0142941823000843-main.pdf` (Hyttinen et al. 2023, truck tyre rolling resistance vs temperature and speed, Polymer Testing)
- `HDEV_NEW__4_.ipynb` (older notebook; the code of record is the 2026-11-12 one in the repo)
- `d4c97793-attachment.txt` (Kiro's PR #31 response)

## 6. Edits Bob has agreed to (not yet all pasted back)

### 6.1 `force_engine`: rotor inertia and `theta_red` fix (Bob has not yet pasted the edited function)

```python
def force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red, J_rotor=0.0, i_total=1.0):
  ...
  m_red = (theta_red + J_rotor * i_total**2) / r_dyn**2  # reduced mass of spinning parts: wheels + motor rotor seen at the wheel [kg]
  k_rot = m_red * accel * v_avg
```

- `J_rotor = 0` gives today's result. `i_total` may be a single number now and per-row later.
- The driver later needs the same two arguments and the same `m_red` line.
- No drivetrain function exists yet. The planned drivetrain function will replace the fixed efficiencies in consumption step 5. Rotor inertia fits the pre-analysis in `force_engine` with a fixed gear ratio as default, and a flag for multi-gear trucks.
- Also fix: negative/NaN `theta_red` must not be dropped silently (raise), array `theta_red` must work, `r_dyn = 0` must raise, and the row-before-`wp_s[0]` wrap.

### 6.2 SI-unit edits (Bob agreed; he said to focus on `force_engine` only for now)

- Driver defaults become `lac_min_v = 50/3.6`, `os_min_v = 50/3.6`, `os_allowed = 2.5/3.6`, `v_min_coast = 5/3.6`.
- Look-ahead line `v * 3.6 * lac_dist_factor` becomes `v * lac_dist_factor`, with the default 10 -> 36.
- `coast_distance`: drop the two `* 3.6` in `f_vt` / `f_vd` (tables come in m/s).
- `consumption_engine` step 3: `v_kmh = np.clip(v_avg * 3.6, ...)` becomes `np.clip(v_avg, ...)` with `cdxa_v` in m/s.

### 6.3 Other pending code fixes

- `P_aux`: add the missing checks (`PTO_always_on < 0`, `PTO_eff <= 0`, NaN) and fix the stale comment.
- pto_engine test cell: 8 arguments, 4 outputs.
- Three driver comment fixes: line 24 (VECTO file name), line 27, and line 190 (comment is the wrong way round).
- Step 6 rewire in `consumption_engine`: `M == 0` for standing rows, `searchsorted`, the drive part, marker waypoints, constants, overlap. Parser must reject fractional times.

## 7. Next steps (in this order, one at a time)

1. Read the two PDFs (VTI 971A and Hyttinen 2023). Report the measured numbers for cold-tyre Crr vs temperature (and speed) and wet/snow factors. Say whether they are solid enough to build, and what assumptions remain (tyre type, truck vs car tyres, test conditions, mapping to DMI data). Quote no more than short phrases.
2. Bob pastes the edited `force_engine`. Check it against section 6.1.
3. Bob answers: coast-down input yes or no; altitude option (a) or (b).
4. Decide cold-tyre and wet-road factors, then where they live (consumption step 3/4, with temperature and precipitation as arguments, not in `force_engine`).
5. Update `claude/status-engine.md` in the project:
   - remove the claim that `m_red_wheels = theta_red / r_dyn^2` is a parser calculation (the engine computes it);
   - add PR #30 / #31 findings and decisions, the SI-units edits, the rotor-inertia design and the review order.
   - Also update memory (engine design rule: engine computes, parser only looks up and checks) only if Bob asks.
6. Write next Kiro prompts: HVAC functions (`HVAC_thermal`, `ssm_total_w`, `climate_lookup`), then consumption steps 5-7 (drivetrain, regen, battery hook); possibly a driver follow-up (SI edits, rotor inertia argument).

## 8. Open decisions for Bob

- Coast-down A,B,C input: add or never.
- Altitude/pressure: (a) one pressure per route computed from altitude (recommended) or (b) per row.
- Cond-while-coasting rule: Kiro recommends keeping it.
- Drive-PTO efficiency default: add yes/no input for an electric body motor.
- Rotor inertia `J_rotor` / gear-ratio handling for multi-gear trucks.
- Whether to run VECTO run 2 (mechanical PTO drag) and run A (raw output) to close the open items.

## 9. Things not to repeat

- Do not say something "belongs to the drivetrain job" as if that function exists. It does not exist yet.
- Do not put calculations in the parser.
- Do not state a decision as Bob's unless he said it.
- Keep answers short and in simple English. Explain formulas in plain words (e.g. the ISO 2533 barometric formula `p = 101325 x (1 - 0.0065*h/288.15)^5.2559`; constants as commonly quoted, Kiro did not re-read them from the ISO text).
- "All functions final" is true only for the functions Kiro has reviewed. State what has not been reviewed.
