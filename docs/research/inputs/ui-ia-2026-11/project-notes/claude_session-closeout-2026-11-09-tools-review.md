# Session closeout, 9 Nov 2026: review of other tools and papers (research only, nothing built)

Paste at the start of the next chat. Project rules as always: Bob builds and codes; Claude helps; no invented numbers; sources for every value; one step at a time.

## What was done
Read the code of 15 open tools and about 15 papers to learn how others handle drivetrain losses, aux, battery, ageing, charging, flexibility, TCO, CO₂ and GPS. Full findings:
- `claude/findings-other-tools-review-2026-11-09.md` — drivetrain, regen, rolling resistance, HVAC, battery sizing (+ KIT thesis details).
- `claude/review-other-tools-all-features-2026-11-09.md` — every other feature, HDEV vs others, do-not-copy list, links (§16 papers Bob fetched, §17 Bob's forks).

Forks in Bob's GitHub (`mohgsaad-art/`): spice_ev, blast-lite, fastsim, dt-cargo, acnportal, eflips-depot. Clones from the original owners' GitHub were blocked by this environment; forks work.

## Main takeaways (plain English)
- **Drivetrain without data:** nobody solves it better. Best-practice fallback = efficiency that depends on load (FASTSim, KIT). Treated as an **input/parser question**, not a blocker for finalising engine functions (Bob, 9 Nov).
- **NREL also calibrates motor efficiency to measured energy** → our EEA calibration (Method C) is mainstream.
- **Physics gaps:** battery losses (OCV+Ri planned), battery temperature and heating, no regen at full battery, regen cap rule (KIT: rated motor power), cab warm-up, one rolling-resistance form everywhere, charger part-load losses, charging taper (App. 10 HEBS: 0.9 C to 80 % → 0 at 100 %), ageing.
- **Feature gaps:** payload penalty vs diesel, minimum grid connection + charger count (eFLIPS: peak simultaneous charging), least-laxity-first and peak-minimising charging, flexibility reported as power/energy bounds per step, CO₂ at charging hour (Energinet `CO2Emis`, 5 min, DK1/DK2), residual value tied to battery health, downtime cost, "share of sessions met", continuous year run with steady-state warm-up.
- **Ageing models:** take structure from SimSES/BLAST-Lite; take numbers only from original papers. Naumann resistance terms differ in BETOS, SimSES and BLAST; Naumann 2020 Table 6 Rinc C-rate signs look misprinted. All models have tested ranges (often ≤ 1 C charge, ≥ 10–25 °C); flag extrapolation; no knee.
- **Where HDEV is ahead:** certified-result validation, VECTO-traceable physics, PTO, energy-neutral flexibility, OCV+Ri charging plan, ISO cold-tyre form, Danish layer.
- **Real truck ops data (dt-cargo, 53 trucks, ODbL):** median stop 22 min (HDEV typed default 45 min — check its source); many trucks start ~03:00. Indicative only until the DT-CARGO paper (doi 10.1016/j.dib.2023.109246) confirms definitions.

## Next chat: finalise engine functions (from 7 Nov closeout §7 and engine status)
Final already: crosswind_engine, payload_engine, pto_engine, P_aux, SP_power_helper, decel_distance, coast_distance (drag table); HVAC_thermal final once Q/p/R/cp are passed to both `ssm_total_w` calls.
Open, in suggested order (Bob decides):
1. `driver_model` part A: SyntaxError (v_cap line), remove `P_drag_loss` remnants, `g` = 9.80665, `pto_engine` test-cell signature.
2. Rolling resistance: driver model linear Crr·m·g vs consumption Crr·g·m^β → one form.
3. `P_max` only active when `coast_on` → decide.
4. Aux timing vs VECTO (SP and cond only while moving in HDEV; VECTO constant/dynamic).
5. `force_engine` one-by-one review.
6. `consumption_engine` review (regen cap, battery-loss hook).
7. Then battery model (OCV+Ri) and charging engine rebuild.
