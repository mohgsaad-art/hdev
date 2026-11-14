# HDEV closeout: `force_engine`, `P_aux`, `SP_power_helper`, `pto_engine` finalised (12 Nov 2026, evening chat)

Read this first in the new chat (HVAC), then `claude/pto-knowledge-2026-11-12.md` for anything PTO. This chat continued from `claude/handover-function-finalization-2026-11-12.md`. Where this file and `claude/status-engine.md` disagree, **this file wins** (status-engine was last fully updated 9–12 Nov and is stale in the places listed in §7).

---

## 0. How to work with Bob (standing rules, incl. lessons from this chat)

- Bob builds and codes. Claude helps. Write code only when he asks. One step at a time. Lead with the direct answer. Short, simple English.
- Mention every assumption and simplification. No invented numbers; every value from an authentic source (VECTO, regulation, ISO, paper).
- Engine functions are pure maths, SI units inside, all parameters as arguments. All calculations in the engine. **The parser only looks up, converts units, checks inputs and fills gaps. All input checks live in the parser, for every function [DECIDED 12 Nov].**
- HDEV must not underestimate energy. Avoid features that need inputs users can't realistically give.
- **Lessons from this chat (Bob was rightly angry):**
  1. **Never say "I haven't checked VECTO" about something being finalised. Check the source first** (the VECTO fork and the hdev repo are public: clone them, `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b IEPC-experiments https://github.com/mohgsaad-art/vecto`).
  2. **Always say why a change is proposed:** what problem it fixes, whether it reduces assumptions, opens up more input types, or improves the estimate, with the size of the effect. Bob cannot decide from a bare list.
  3. **Always name the exact function and step** where something goes (e.g. "`consumption_engine` step 5", not "the drivetrain part").
  4. Only Kiro-reviewed functions get finalised. If Kiro has not dug into a function, it goes to Kiro first.
  5. Do not state a decision as Bob's unless he said it.

---

## 1. Function status (end of this chat)

| Function | Status | Note |
|---|---|---|
| `crosswind_engine` | Final | unchanged |
| `payload_engine` | Final | unchanged |
| `interp1`, `decel_distance`, `coast_distance` | Final | unchanged |
| `driver_model` | Final (12 Nov), **one gap found** | Rotor inertia missing from `coast_acc` (§3.2). SI-unit edits from the handover §6.2 still pending. Fix in a driver follow-up. |
| `force_engine` | **Final (12 Nov)** | Code of record §2.1. Kiro PR #30. |
| `P_aux` | **Final (12 Nov)** | Checks moved to parser. Code §2.2. Kiro PR #31. |
| `SP_power_helper` | **Final (12 Nov)** | Checks moved to parser. Code §2.3. Kiro PR #31. |
| `pto_engine` | **Final (12 Nov)** | Bob pasted it with the `too_short` raise removed (code in `pto-knowledge` §2.1). Kiro PR #31. Open library choice: `pto-knowledge` §4 item 1 (only option (b) would change it). |
| `HVAC_thermal`, `ssm_total_w`, `climate_lookup` | **Not final: sent to Kiro** | Never Kiro-reviewed. Prompt `claude/kiro-prompt-hvac-review-2026-11-12.md` (§5). status-engine.md's "Final" for these is wrong. |
| `consumption_engine` | Open (largest job) | Must take the new `force_engine` output, rotor term in step 5, drive-PTO routing, step-6 PTO rewrite (`pto-knowledge` §2.2–2.3), SI edit in step 3, payload wrap bug. |
| Parser (`defaults.py`) | Open | Jobs in §4 and `pto-knowledge` §2.4. |
| Battery, charging | Open | after consumption |

---

## 2. Code of record (Bob's pastes, 12 Nov)

### 2.1 `force_engine` (final)
```python
##4 FORCE ENGINE
## takes in rows from the driver model and calculates the force coeff per row independent of mass and temp and CdxA_eff
def force_engine(g, Crr, speed, accel, dt_s, grade, r_dyn, theta_red, J_rotor, i_total):

  speed = np.asarray(speed, dtype=float) # speed at start of the step
  accel = np.asarray(accel, dtype=float) # acceleration of the vehicle
  dt_s = np.asarray(dt_s, dtype=float)  # time step, s
  grade = np.asarray(grade, dtype=float) # gradient

  grade = np.arctan(grade / 100) # turns gradient in % into an angle in radians
  v1 = speed
  #v2 = speed + accel * dt_s
  v2 = np.maximum(speed + accel * dt_s, 0.0) # speed cannot go below 0, as in the driver model
  v_avg = (v1 + v2)/2  #speed in m/s

  #K = ((Crr * g * np.cos(grade)) + (g * np.sin(grade)) + accel) * v_avg
  # the K equation is the same with the added term of rotational force, if theta_red and J_rotor are 0 we get back the simple equation.
  k_lin = (g * np.sin(grade) + accel) * v_avg
  k_roll = Crr * g * np.cos(grade) * v_avg
  k_rot_wheel = (theta_red  / r_dyn**2) * accel * v_avg  # no rotating mass unless given
  k_rot_rotor = (J_rotor * i_total**2 / r_dyn**2) * accel * v_avg
  L = (v1 + v2) * (v1**2 + v2**2) / 8 # exact average of 0.5*v^3 over the step as VECTO CrosswindCorrectionCdxALookup

  return k_lin, k_roll, k_rot_wheel, k_rot_rotor, L, v_avg # we are taking out v_avg so we can use it to look up CdxA
```
- Only leftover: the comment `# no rotating mass unless given` is stale (no `if` any more). Cosmetic.
- Wheel power: `P_wheel = m·k_lin + m^β·k_roll + k_rot_wheel + ρ·CdxA_eff·L`. **`k_rot_rotor` is NOT part of wheel power**: it is added at the motor side in `consumption_engine` step 5, after the gearbox efficiency (VECTO applies rotor inertia at the motor shaft, `ElectricMotor.cs` 186–188, 297, 615).
- `i_total` can be a scalar or one value per row; `J_rotor = 0` gives the old result.
- No defaults on `J_rotor`, `i_total`: the parser must always pass them (neutral values `J_rotor = 0`, `i_total = 1`).

### 2.2 `P_aux` (final)
```python
##5.1 Electrical system - finalized
def P_aux(ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on, ES_alteff=0.7, PS_alteff=1.0, HVAC_eff=1.25, SP_alteff=0.7, cond_eff=1.0, PTO_eff=1.0): #get rid of hardcoding later
  # pure: electric W per aux = input W * efficiency factor
  # works for one number or an array using numpy
  # PTO_always_on = always-on PTO only (chiller, mixer); stop PTO comes from pto_engine and is laid on rows in the consumption engine

  powers = [np.asarray(p, dtype=float) for p in (ES_power, PS_power, HVAC_power, SP_power, cond_power)] # convert first so lists work
  effs = (ES_alteff, PS_alteff, HVAC_eff, SP_alteff, cond_eff)
  PTO_always_on = np.asarray(PTO_always_on, dtype=float)

  ES_power, PS_power, HVAC_power, SP_power, cond_power = (p * e for p, e in zip(powers, effs))
  PTO_always_on = PTO_always_on / PTO_eff  

  return ES_power, PS_power, HVAC_power, SP_power, cond_power, PTO_always_on
```
- Exact VECTO: all 68,040 aux combinations, max difference 4.5e-13 W (PR #31).
- [DECIDED] Keep the "efficiency" multipliers as they are; **UI note** (saved to memory): ES/SP 0.7 is a back-conversion that applies only to VECTO table values (mechanical W); a custom electric value needs 1.0, otherwise it is silently cut by 30 %. HVAC 1.25 = 1/0.8 (`HVACElectricEfficiencyFactor`). Thermal-mode HVAC → `HVAC_eff = 1.0`.

### 2.3 `SP_power_helper` (final)
```python
# returns mechanical W, goes into P_aux as SP_power gets multiplied by 0.7 for electrical W

def SP_power_helper(SP_baseline, SP_axle_shares, SP_tech_factors):

  SP_baseline = np.asarray(SP_baseline, dtype=float)         # (UF, B, S) in W, from SP-Table.csv
  SP_axle_shares = np.asarray(SP_axle_shares, dtype=float)   # one (UF, B, S) row in % per steered axle, from SP-Axles.csv
  SP_tech_factors = np.asarray(SP_tech_factors, dtype=float) # one (UF, B, S) row per steered axle, from SP-Tech.csv or custom

  parts = SP_baseline * SP_axle_shares.sum(axis=0) / 100 # each part summed over the steered axles
  parts = parts * SP_tech_factors.mean(axis=0)           # VECTO: average technology factor over all steered axles
  return float(parts.sum())                  # add the 3 parts,
```
- Exact VECTO (`SteeringPump.cs`). 3–32 W electric on the E2 (~0.02–0.07 % of trip energy): not worth research beyond VECTO.
- Parser must keep both shape checks (the tech-factor row count one matters: a wrong count still gives a number, silently wrong).

### 2.4 `pto_engine` (final)
Bob's final paste (raise removed) is in `claude/pto-knowledge-2026-11-12.md` §2.1. The `too_short` check moved to the parser (stop extension). Everything about PTO: `claude/pto-knowledge-2026-11-12.md`.

---

## 3. Findings this chat

### 3.1 `force_engine` (Kiro PR #30, rechecked by Claude)
- Matches VECTO to within 0.012 % of positive wheel energy on VECTO's own speed trace. The remaining HDEV-vs-VECTO error is the driver: +0.27 % Regional, +2.55 % Urban, +0.43 % LongHaul.
- **Kiro's Q10:** nothing else in VECTO's wheel power besides what HDEV has. `P_wheelEnd_saving` is 0 on all six runs; brake loss is a use of wheel energy, not an extra term. Only missing term was motor rotor inertia, which VECTO applies at the motor shaft (0.228 / 1.22 kWh Regional / Urban; +0.30 % / +1.49 % if reflected to the wheel).
- `atan` vs `asin`, CdxA look-up speed, slope mass, the `v2` clamp and `L`: current code as good or better on every one.
- The E2 **shifts gears**: Kiro used `J_rotor = 0.45 kg·m²` (2 × 0.225) and `i = 2.0 × 2.59 × gear ratio` per row from the `.vmod` `Gear` column. (Claude's earlier "one-gear E2" was wrong.)
- `J_rotor` source for a user truck: certification XML `RotationalInertia`; EEA public table has no inertia column → NO SOURCE for a fleet default.

### 3.2 Rotor inertia in the driver (Claude read VECTO source this chat)
| Where | VECTO | HDEV | Match |
|---|---|---|---|
| Look-ahead coasting decision `ComputeCoastingDistance` (`DefaultDriverStrategy.cs` 721–756) | mass = `TotalMass + ReducedMassWheels`, **no rotor** | `coast_distance`: `coast_mass + m_red_wheels` | **Yes** |
| Coasting rows themselves (`ElectricMotor.cs` 186–188, 285–289): motor off → `DragCurveLookup + inertiaTorqueEm` | **rotor inertia included** | `coast_acc`: `m_eff = coast_mass + m_red_wheels`, no rotor | **No (gap)** |
- Effect: HDEV's truck slows down too fast while coasting (rotor energy missing). Size not measured; rotor and wheel inertia are similar size on the E2 (Urban 1.22 vs 1.04 kWh).
- Fix (driver follow-up, not done): `m_eff = coast_mass + m_red_wheels + J_rotor·i_total²/r_dyn²` in `coast_acc` only (not in `coast_distance`, which matches VECTO without it).
- Bob was rightly angry that this was not checked before. **Offered, not yet answered:** a short Kiro driver job that lists every force, inertia and loss term VECTO uses while driving, coasting and braking (file + line) next to HDEV's, and measures any gap. The `consumption_engine` steps 5–7 Kiro prompt must do the same column-by-column check from the start.

### 3.3 Rotor inertia vs drag table (explained to Bob)
- Drag table (`drag_v`, `drag_F`): friction and magnetic losses, depends on speed, acts at constant speed too, energy lost as heat.
- Rotor inertia: energy stored in the spinning rotor, depends on acceleration, zero at constant speed, given back when slowing (net cost only through regen/brake losses).
- No double counting.

### 3.4 Coast-down input (A + B·v + C·v²) [DECIDED: parked]
- Effect on E2 +0.12 % / +0.05 % (PR #30). Helps only users with real coast-down data (OEM UI). Problems: one test mass (breaks β scaling), test-day wind clashes with the crosswind model, B can double-count drivetrain drag.
- If ever added: the B-term coefficient must be the exact step average `(v1² + v1·v2 + v2²)/3`, not `v_avg²` (Kiro's +0.12 % used `v_avg²`).
- [DECIDED] Current Crr and CdxA inputs are fine.

### 3.5 PTO (Claude read VECTO source this chat): see `pto-knowledge` §1. Key points:
- Drive PTO: torque at the motor shaft, motor map gives the loss, no fixed efficiency, engineering mode only.
- PTO transmission loss: constant torque from `PTO-tech.csv` at the motor shaft, every mission, if a mechanical PTO type is declared; the table was made at ~1200 rpm diesel speed [CALC] → parked until VECTO run 2.

### 3.6 PTO library sources read this chat (details in `pto-knowledge` §3)
Ban & Stipetić 2019 (cycles, approximated); Bae 2018 (mixer design duty spectrum, mean 6.2 kW, 4× below Ban's mixer); Ferraris 2001 (drum speeds 15 rpm mixing, 2–6 rpm transport); HIAB XP18T (cycle 139–163 s, 80 l/min, 30 MPa) and HIAB pump table (10–60 kW by model); Volvo body builder PTO instructions (N = Q·p/(600·ηt), ηt ≈ 0.95; which bodies work while driving); Parker MSG30-8200 (formulas, no numeric efficiencies in text); **Volvo "Fields of application, Calculation guide" (2007, Ban's ref [2])**: power demand per body type (refuse 30–40 kW; mixer 15–20 kW on the move, 40–90 kW discharge peak; etc.) and usage hours over 5 years. It supports Ban's mixer figures, so Bae is the outlier. Saved: `claude/findings-ban-stipetic-epto-2019.md`.

---

## 4. Decisions this chat [all DECIDED by Bob, 12 Nov]
1. `force_engine`: rotor inertia as its own coefficient `k_rot_rotor`, added at the motor side in consumption step 5 (option b), not in wheel power.
2. Unknown gear: use the **lowest gear (highest ratio)** as the safe default for `i_total`.
3. Coast-down input: parked. Current Crr and CdxA stay.
4. **All input checks in the parser** for every function. Removed from `P_aux` and `SP_power_helper`; `force_engine` never had them; `pto_engine` `too_short` raise to be removed.
5. `P_aux` "efficiency" naming kept; UI note instead.
6. `pto_engine` points 1–3 (fractional times, `too_short`, efficiency ≤ 0) → parser. Done: Bob removed the raise; `pto_engine` final.
7. Drive PTO: the yes/no "body has its own electric motor" decides where it is added in `consumption_engine` (step 5 at the motor shaft if mechanical, step 6 at the battery if electric); `drive_pto_eff` stays 1.0. Built when `consumption_engine` is finalised. **Not parked.**
8. PTO transmission drag: **parked** until VECTO run 2.
9. HVAC set goes to Kiro first (Bob: only finalise what Kiro has dug into).

## 5. Kiro prompt written this chat
- `claude/kiro-prompt-hvac-review-2026-11-12.md` (also sent to Bob as a file). Scope: `HVAC_thermal`, `ssm_total_w`, `climate_lookup`, plus a read-only check of how `HVAC_el` enters `P_aux` and `consumption_engine`. Kiro creates branch `hvac-review-2026-11` from `main` and copies the prompt to `docs/research/inputs/`.
- Structure: rules (incl. checks in parser, hourly structure must stay, inputs users can give), 3 gates (Gate 3 = line-by-line Python port of VECTO's SSM vs Bob's code), Q1–Q13 on VECTO SSM (0.25 solar factor, solar quantity vs DMI, `DefaultClimatic.aenv` points, heating split, COP, waste heat, fresh air vs ventilation, driver vs passenger compartment, technology benefits, lorry HVAC table), Parts A–L (audit, tests, VECTO reproduction + deviation register, sensitivity/tornado, Danish year vs VECTO table, physics beyond VECTO incl. speed-dependent UA, warm-up, preconditioning, door openings, humidity, fresh-air standards, solar, measured heat-pump COP, battery conditioning note; data sources for easy inputs (cab geometry by cab type, UA, OEM heat-pump yes/no, DMI, measured BEV energy vs temperature); other tools' code; validation; VECTO runs; performance; explainer). Appendix has the three functions verbatim.
- Status: **not yet run.** Bob gives it to Kiro.

## 6. Parser jobs added this chat
- `force_engine`: `r_dyn > 0`, `theta_red ≥ 0`, `J_rotor ≥ 0`, `i_total > 0`, no NaN; always pass `J_rotor`, `i_total`; unknown gear → lowest gear ratio.
- `P_aux`: all powers ≥ 0 incl. `PTO_always_on`; all efficiencies > 0 incl. `PTO_eff`; no NaN/inf; `HVAC_eff = 1.0` in thermal mode.
- `SP_power_helper`: axle-share shape (n × 3, n ≥ 1, ≤ 4 steered axles); tech-factor shape = axle-share shape.
- `pto_engine`: see `pto-knowledge` §2.4 (whole seconds, efficiencies in (0, 1], stop extension incl. the moved `too_short` check, `is_on` shape, etc.).

## 7. `claude/status-engine.md` is stale here (update it in the next chat)
- §1 table: `force_engine`, `P_aux`, `SP_power_helper`, `pto_engine` → final (this file §1); HVAC set → "sent to Kiro", not "Final".
- §2.1 / §2.3: code shown still has the checks; replace with §2.2 / §2.3 here.
- §2.4 HVAC: keep, but mark "pending Kiro HVAC review".
- §3b PTO: replace by a pointer to `claude/pto-knowledge-2026-11-12.md`; the "drive PTO efficiency 1.0 skips motor losses" flag is superseded by decision 7.
- §5 item 1 and §6 "parser computes `m_red_wheels = theta_red / r_dyn²`": **wrong**; Bob never decided that (correction from the handover). The engine computes it.
- §5 "Agreed review order": now HVAC (Kiro) → `consumption_engine` (Kiro first, steps 5–7) → driver follow-up.
- Add PR #30 / #31 findings (handover §3) and the SI-unit edits (handover §6.2).

## 8. Open decisions for Bob
1. Send the HVAC prompt to Kiro (done by Bob outside the chat).
2. Driver follow-up Kiro job (full VECTO force/inertia/loss term inventory): yes/no.
3. PTO library: half-second profiles (resample in library vs averaging in `pto_engine`); mixer default (Ban vs Bae, 4× apart); ramps vs steps; ePTO motor efficiency source (`pto-knowledge` §4).
4. Still open from the handover: altitude/pressure (a) one pressure per route or (b) per row; cold-tyre and wet-road factors (needs reading Hyttinen 2023 and VTI 971A, not done yet); Cond-while-coasting rule (Kiro: keep); VECTO runs 2 (mechanical PTO drag) and A (raw output).

## 9. Next steps (in order)
1. New chat: HVAC. Wait for Kiro's HVAC PR, then review it function by function the same way (what's right, what's wrong, why each change, effect size, engine or parser).
2. While waiting: update `claude/status-engine.md` (§7 list), and read Hyttinen 2023 + VTI 971A for the cold-tyre / wet-road decision (handover §7 step 1, still not done).
3. Then the `consumption_engine` Kiro prompt (steps 5–7: drivetrain, rotor term, drive-PTO routing, step-6 PTO rewrite, regen, battery hook), with a full VECTO column-by-column check.
4. Driver follow-up: rotor term in `coast_acc`, SI edits, comment fixes (if Bob says yes, via Kiro first).

## 10. Working-environment notes
- VECTO source cloned read-only this chat at `/home/claude/mohgsaad-art/vecto` (branch `IEPC-experiments`, `b8d6126`); hdev branches `force-engine-review-2026-11` and `aux-pto-review-2026-11` cloned read-only. This session could **not push** to the repo (read-only); the HVAC prompt must be put in the repo by Kiro or Bob.
- Kiro outputs: PR #30 `docs/research/force-engine-review-2026-11.md`; PR #31 `docs/research/aux-pto-review-2026-11.md` (+ folders, tests, explainers).
