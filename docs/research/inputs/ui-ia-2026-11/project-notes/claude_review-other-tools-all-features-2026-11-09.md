# HDEV vs other tools and papers — every planned feature (9 Nov 2026)

Companion to `findings-other-tools-review-2026-11-09.md` (drivetrain, regen, rolling resistance, HVAC, battery sizing). This file covers everything else: payload, aux and reefer, GPS, battery electrical model and OCV, degradation, charging, flexibility, year structure, TCO and financing, CO₂, validation.

Tags: **[CODE]** I read the source code (file named). **[DOCS]** project README or docs page. **[PAPER]** paper text. **[JUDGEMENT]** my reading, not from a source. Nothing here is a recommendation that is decided; Bob decides.

---

## 0. What was read, and what could not be

| Tool | How | Licence | What it is |
|---|---|---|---|
| SimSES 2.1.1 (TUM EES) | PyPI source | BSD-3 | Battery system sim: OCV/Ri cell models, calendar + cycle ageing, thermal, converter losses |
| acnportal 0.3.3 (Caltech ACN-Sim) | PyPI source | BSD-3 | EV charging simulator + scheduling algorithms, real session data |
| EV2Gym 2.0.0 | PyPI source | MIT | V2G/charging gym environment, MPC and Gurobi baselines, degradation |
| eFLIPS-depot 4.20.4, eflips-model 11.4.1, eflips-opt 2.0.0 (TU Berlin) | PyPI source | **AGPL-3.0** | Bus depot discrete-event sim, smart charging, vehicle scheduling |
| FASTSim 3.1.0 (NREL) | PyPI source (Rust) | Apache-2.0 | Vehicle sim incl. transient cabin + battery thermal |
| T3CO 2.0.0 (NREL) | PyPI source | BSD-3 | TCO + opportunity costs on FASTSim |
| carculator_truck 0.5.0 (PSI) | PyPI source | BSD-3 | Truck LCA/TCO |
| BETOS / truck_fleet_electrification (TUM FTM) | Git clone (earlier today) | Apache-2.0 | N3 tractor energy, charging, ageing |
| PyBaMM 26.10 | PyPI source (parameter sets only) | BSD-3 | Battery physics; checked only its ECM example data |
| mappymatch 0.7.1 (NREL) | PyPI source | BSD-3 | GPS map matching |
| SpiceEV (RLI) | Docs first; **code read later via Bob's fork `mohgsaad-art/spice_ev`** (commit f0c7061, 2 Nov 2026), see §16.6 | MIT | Depot charging strategies |
| BLAST-Lite (NREL) | **README only** | BSD-3 | Cell degradation model library |
| dt-cargo (TUM) | **README only** | ODbL-1.0 | 10 Hz truck GPS dataset tools |

**Blocked:** after the first clone, GitHub refused all further clones from this session (proxy answered 403 to CONNECT). I did not try to route around it. SpiceEV and BLAST-Lite are not on PyPI, so only their docs/README were read.

Papers read today (in addition to the earlier file): KIT/Fraunhofer thesis ch. 4.1, 4.4 (TCO); Decher & Schäfers 2024 and Decher et al. 2026 (HAW Hamburg, truck depot flexibility); arXiv 2502.06435 (EV fleet flexibility polytope); Lösch et al. 2023 (reefer, Energies 16(18) 6459); Phumpho et al. 2026 (reefer CFD, Eng 7, 393). Energi Data Service API (CO2Emis) queried live.

---

## 1. One-page comparison (HDEV planned vs best practice found)

| Area | Best practice found (who) | HDEV today / planned | [JUDGEMENT] |
|---|---|---|---|
| Battery electrical model | OCV(SOC,T) + hysteresis + R(SOC,T,SOH)·I, current from quadratic, current limits from voltage limits (SimSES). Regulatory: OCV(SOC), Ri(SOC, pulse 2/10/20/120 s), C-rate limits vs SOC (VECTO / Annex Xb App. 10) | VECTO OCV + Ri planned, not coded; battery = 100 % efficient today | VECTO base is right. SimSES shows the two things VECTO lacks: temperature and ageing feeding back into Ri and capacity |
| Charging taper | Usually **none**: constant power (eFLIPS depot sim, eflips-opt "we do not support charging curves", T3CO, KIT). Analytic 2-stage taper (acnportal, EV2Gym). Taper emerging from max-voltage limit (SimSES) | Exponential taper deprecated; OCV+Ri sim planned | HDEV's plan is ahead of most. A sourced fallback taper exists: App. 10 HEBS max charge 0.9 C to 80 % SOC → 0 at 100 % |
| Charger losses | Constant (eFLIPS 0.95 default, BETOS 0.9). Part-load curve P_loss = P0 + K·P² (SimSES Notton model) | Not built | Part-load form matters for low-power overnight charging; needs a sourced P0/K or charger datasheet |
| Strategies | ASAP, balanced/ALAP, cheapest-first, peak windows, flex windows, DSO schedule, EDF, LLF, round robin, LRPT, MPC, LP peak minimisation | JIT/ASAP + EDF/ES; cheapest-first planned | Coverage comparable. Missing: **least-laxity-first**, **peak-minimising LP**, **DSO window/schedule** |
| Minimum grid connection | Bisection on the grid limit until smart charging still finishes (eFLIPS `lowest_power`); exact LP min-peak (eflips-opt) | Sizing mode = P = E/t per vehicle; simulation mode planned | Add a site-level "minimum connection" search on top of the simulation mode |
| Flexibility | Laxity-based flexibility matrix (Decher); power/energy polytope per EV, summed for fleet (arXiv 2502.06435) | Thesis: energy-neutral up/down flexibility within the session | HDEV's energy-neutral rule is stricter than both. The polytope (power and energy bounds per time step) is the standard output shape; HDEV should report it |
| Battery ageing | Calendar √t + cycle √FEC with virtual-time continuation and half-cycle detection, also resistance growth (SimSES, BETOS, Naumann LFP; Schmalstieg NMC); 14 cell models (BLAST-Lite) | Not built | Copy the *structure* (stateless, virtual time). Parameters must come from the original papers, not from re-implementations (they disagree, §6) |
| Cabin HVAC | Transient lumped cabin + PID + COP as fraction of Carnot, speed-dependent heat loss (FASTSim). Steady α_cab·ΔT/COP (KIT) | VECTO SSM steady-state per hour + fresh-air term | HDEV is more sourced (VECTO SSM). Transient warm-up is the one thing missing |
| Battery thermal / BTMS | Combined cabin + battery thermal with separate heat/cool sources (FASTSim); BTMS power vs T (KIT) | Not built | Fits the "ready for battery thermal" note; needs sourced pack parameters |
| Reefer | No open, validated lumped model found | Planned (ATP K) | HDEV's ATP-K plan is not behind anyone open; primary source to fetch (Fallmann 2023) |
| Payload | Lost-payload cost from a real truck-weight distribution (T3CO); curb mass ↔ battery ↔ payload loop (carculator); payload per trip from EU road-freight survey (KIT) | Payload shapes per stop; no payload-capacity check vs diesel | Biggest missing *commercial* output: payload penalty |
| GPS | Map matching (mappymatch LCSS); 10 Hz truck dataset with tracks/tours/signal-loss fields (dt-cargo) | GPS adapter planned, stop rule open | Use map matching only if road grade/limits are needed; dt-cargo fields are a good template |
| TCO | Annuity TCO, resale regression on age + mileage, battery residual ∝ SOH, tolls, price bands, Monte Carlo scenarios (KIT); component-based price, depreciation, insurance %, financing, downtime and payload opportunity costs (T3CO) | Port COWI later | Add residual value tied to ageing, downtime cost, payload cost |
| CO₂ | Annual factors (COWI); full LCA (carculator) | Planned | Danish 5-min CO₂ intensity per price area is live (Energi Data Service `CO2Emis`) → charging-hour emissions |
| Year structure | Continuous fixed-step run over whole scenario (SpiceEV); discrete-event over schedule + consumption lookup table (eFLIPS); probabilistic weekly/daily profiles (KIT) | Per-date direct computation decided; binning fallback | Continuous year-long charging run is standard practice |
| Validation | Charging energy vs real depot (Decher: 3,280 vs 3,278 kWh); diesel vs EEA (KIT) | Consumption vs EEA (10 trucks) | HDEV leads on consumption validation; nothing yet on charging |

---

## 2. Payload

**T3CO payload opportunity cost** [CODE `cost_models/opportunity_costs.py` `set_payload_cap_cost_multiplier`]:
1. Builds a probability density of real truck operating weights with a Gaussian KDE (bandwidth 0.15), weighted by miles travelled, from a US weight survey file.
2. New cargo ceiling = GVWR − (BEV empty mass − reference empty mass) + a ZEV weight credit.
3. Expected lost payload = ∫ p(w)·(w − ceiling) for weights between the new ceiling and GVWR.
4. Cost multiplier = 1 + lost payload / BEV payload capacity → more trucks/trips needed.

**carculator_truck** [CODE `model.py` l.48–115]: loops curb mass → battery mass (from target range) → power → available payload until payload change converges; cargo mass clipped to available payload. Default payloads per size class from ACEA and the SR7 report, with the file's own comment that "we have to do some guessing" [CODE `data/payloads.yaml`].

**KIT** [PAPER §3.1, §4.1]: payload per trip from Eurostat road-freight microdata (Reg. (EU) 70/2012 survey: truck, journey and goods records incl. payload). Reports most trucks run at 60–90 % of max payload on at least one trip; 10–20 % do at least one overloaded trip. Microdata are anonymised and provided for scientific use.

**For HDEV:**
- Missing output: **payload capacity loss vs diesel** and its cost (also flagged in the 26 Oct gap analysis). Needs: BEV curb mass, GVW limit, legal ZEV weight allowance, and a payload distribution.
- [JUDGEMENT] A real payload *distribution* (not one value) is what makes the penalty meaningful; for Danish fleets the national road-freight survey is the natural source. **Licence check needed** before using survey microdata in a commercial tool.
- The ZEV weight allowance in EU law (Directive 96/53/EC as amended) and the Danish BEK 1447/2025 limits should be cited from the text; not re-fetched today.

## 3. Auxiliaries, cab, battery thermal, reefer

**FASTSim 3 cabin** [CODE `vehicle/cabin.rs`, `hvac/hvac_sys_for_lumped_cabin.rs`]:
- Lumped cabin with heat capacitance, shell heat-transfer coefficient to ambient (separate value when stopped), and a Reynolds number over a flat plate, so heat loss depends on speed.
- HVAC is a PID controller with deadband; COP = Carnot COP × `frac_of_ideal_cop` (default 0.15); heater cap `pwr_aux_for_hvac_max` default 5 kW. Defaults carry no citation in the code.
- A second variant couples cabin **and battery** temperature, with separate battery heating/cooling sources.

**FASTSim battery efficiency** [CODE `reversible_energy_storage.rs` l.1307]: constant, f(C-rate), or f(C-rate, SOC, T) — no OCV+Ri. It does **taper regen near full SOC** (a "regen buffer" below max SOC, l.400–425).

**Reefer:** no open, validated lumped model found. Lösch et al. 2023 [PAPER] uses a switched state-space model with door openings but gives no transmission K, no COP data and no error metric; the model is in Fallmann et al. 2023 (Appl. Therm. Eng. 220, 119719). Phumpho et al. 2026 [PAPER] is CFD; only eTRU energy 0.117 kWh/km on one 555 km, 8 h route.

**For HDEV:**
- Cab: HDEV's VECTO SSM base is better sourced than FASTSim's defaults. What FASTSim adds is **transient warm-up** (cold cab at departure) and **speed-dependent heat loss**. [JUDGEMENT] Warm-up matters for short urban trips in winter; it needs a sourced cab heat capacity.
- **Regen at full battery:** a truck leaving the depot at 100 % SOC cannot regenerate. HDEV currently has no battery state in the consumption step, so this is missed. It will fall out of the OCV+Ri battery model if current limits are applied (App. 10: max charge current 0 at 100 % SOC).
- Reefer: HDEV's planned ATP-K model is not behind any open tool.

## 4. GPS and routes

- **dt-cargo** [DOCS README]: output tables `fleet.csv` (GVW, mass with trailer, axle class), `tracks.csv` (start/stop time, distance, gap to next track, avg/max speed, signal-loss count/distance/ratio, HDOP, flags home_base / long_haul / rest_area / fuel / industrial area), and 10 Hz `speed` per track. Long-haul flag: end of recording > 150 km from home bases. Processing rules are in the Data in Brief paper (not fetched; captcha).
- **mappymatch** [CODE]: LCSS map matcher (defaults: distance epsilon 50 m, cutting threshold 10 m), plus OSRM/Valhalla wrappers.
- **Route_Dynamics** (earlier file): LiDAR surface model needs smoothing to remove bridges and vehicles.
- **For HDEV:** [JUDGEMENT] dt-cargo's track fields (signal loss, gap, HDOP, location flags) are a ready-made template for the GPS adapter's quality checks and for flagging depot vs rest stops. Its 10 Hz speed data could test the driver model's speed traces (ODbL licence: share-alike for derived databases).

## 5. Battery electrical model and OCV curves

| Source | OCV | Resistance | Current limits | Temperature | Heat |
|---|---|---|---|---|---|
| VECTO / Annex Xb [CODE `Battery.cs`; knowledge-base 12c, 12h] | Table vs SOC; standard: 0.88/0.94/1.00/1.06/1.12 × V_nom at 0/10/50/90/100 % | Ri(SOC, pulse duration); standard specific resistance HEBS 210/240/270/390 mΩ·Ah for 2/10/20/120 s | C-rate vs SOC; standard HEBS charge 0.9 C (0–80 %) → 0 at 100 % | none | losses only |
| SimSES [CODE `battery/battery.py`, `model/cell/*`] | Per cell: LFP table (Sony), NMC sigmoid fit (Samsung 94 Ah, Collath et al. 2024) | Rint(SOC,T) table (LFP) or constant (NMC 0.819 mΩ); scaled by SOH_R | From V_max/V_min with Rint, plus C-rate limits; optional linear voltage derating | yes | irreversible + entropic |
| KIT [PAPER Eq. 4.25] | – | Rint, R(T, SOC) factor, reference at 20 °C/50 %/1 s | – | yes | – |
| BETOS [CODE] | Cell tables (Schmalstieg NMC) | R(T, SOC) | SOC-dependent C-rate curve (Wassiliadis ID.3) | yes | – |
| PyBaMM ECM example [CODE] | – | – | – | – | Its docstring says it "does not reflect the properties of any particular cell" and the source is not disclosed → **do not use** |

**For HDEV:**
- Keep VECTO OCV+Ri as the auditable base; use App. 10 values when no battery data.
- [JUDGEMENT] SimSES shows the step after VECTO: the **charging taper comes out of the model** once V_max and Ri are known, instead of being a separate input curve. Real truck tapers are BMS-set (thermal and lifetime limits), so an OEM curve must still override it.
- VECTO's Ri depends on pulse duration (2/10/20/120 s). For depot charging lasting hours, the 120 s value (HEBS) is the closest; this is a choice to flag.

## 6. Battery ageing (cycling and calendar/shelf)

**SimSES** [CODE `model/degradation/sony_lfp_*.py`, `degradation/*`]:
- Calendar (Naumann et al. 2018): capacity loss ∝ √t, stress = Arrhenius(T) × SOC polynomial; resistance increase linear in t.
- Cycle (Naumann et al. 2020): capacity loss ∝ √FEC, stress = C-rate term × DoD polynomial; resistance increase linear in FEC.
- **Virtual-time continuation:** each step converts accumulated loss back to an equivalent time/FEC under the current stress, then adds the new step. This makes √-law ageing path-dependent and correct when stress changes.
- **Half-cycle detection** on SOC direction reversals gives DoD, mean SOC and C-rate per half-cycle.
- Models are stateless; the accumulated state is passed in. Capacity loss reduces SOH_Q; resistance growth raises SOH_R, which scales Ri.

**BETOS** [CODE `M10_Evaluation/M10_0_Aging_Model/Aging_Model.py`]:
- Implements the same Naumann LFP model plus Schmalstieg NMC.
- Schmalstieg calendar: cell temperatures below 25 °C are clamped to 25 °C ("aging model is not valid" below). In Denmark this *overestimates* calendar ageing (conservative).
- Rainflow counting is commented out; it uses one cycle = max(SOC) − min(SOC) of the window.
- **Coefficients disagree with SimSES** for the same Naumann papers: calendar resistance SOC term +3.3903 (BETOS) vs −3.3903 (SimSES); cycle resistance C-rate term 0.0023 − 0.0018·C (BETOS) vs 0.0021 − 0.0020·C (SimSES). **Resolved from the originals in §16.1.**

**EV2Gym** [CODE `models/ev.py` l.442–]: Schmalstieg-type model with hard-coded car values (78 kWh pack, 2.05 Ah cell, 15,000 km/yr, 2-year-old battery, 25 °C) and a linear OCV (3.3324 + 0.8263·SOC V). Not reusable for trucks.

**BLAST-Lite** [DOCS]: 14 cell models (LFP, NMC111/622/811, NCA, LMO, NMC-LTO) with source DOIs. The authors state the models are trained on 1–3 years and extrapolated to 10+, so "treat all models as qualitative", and give a rule of thumb that pack life is 20–30 % less than cell life. Uncertainty via a `degradation_scalar`.

**Sizing/TCO use:** KIT (SoC-window power law, certified calendar age 13 y Ni-rich / 15 y Fe/Mn from Hesse et al. 2017); carculator (cycle life NMC 3,000 citing Preger et al. 2020, battery replacements; as written in the code the replacement count is clipped to between 1 and 3, so I read it as never below 1 — to check with the authors' intent).

**For HDEV:**
- [JUDGEMENT] Copy the SimSES *structure* (stateless, virtual time, half-cycles, Q and R both degrade), which matches HDEV's pure-function rule.
- Ageing should feed three places: capacity at end of life for sizing (tender §17.1 style guarantee), Ri growth for losses, and battery residual value in TCO.
- Cell parameters: only from original papers, chemistry-matched, with BLAST-Lite's "qualitative" warning carried into reports.

## 7. Charging simulation

**Strategies found:**
- SpiceEV [DOCS]: greedy; balanced (lowest feasible power across standing time; needs departure estimate); balanced market (cheapest price periods); schedule (DSO-provided, collective or individual); peak load window (greedy/needy/balanced sub-strategies); flex window; distributed (opportunity vs depot). Stationary batteries, V2G and local generation supported. Incentive models: capacity charge with a 2,500 h utilisation threshold, time-variable grid fees, flexible windows, schedule-deviation charges (German tariff context).
- acnportal [CODE `algorithms/sorted_algorithms.py`]: FCFS, LCFS, EDF, LLF (least laxity first), LRPT, round robin; max feasible rate per EV by bisection under network constraints; three-phase current constraints [CODE `network/charging_network.py`]; discrete pilot levels per EVSE; `SimpleRampdown` learns each EV's real max rate from what it actually draws.
- eFLIPS [CODE `smart_charging.py`]: vehicles sorted by flexibility (least flexible first), each fills the cheapest price intervals under the grid limit; precondition loads added as fixed load; `lowest_power` bisects the grid limit to the lowest value at which the schedule still completes.
- eflips-opt [CODE `smart_charging.py`]: Pyomo LP minimising peak site power at 5 min steps with 10 kW quantisation, then a second pass smoothing each vehicle's power; the code states charging curves are not supported (constant power only).
- EV2Gym [CODE]: ASAP/ALAP/round robin heuristics, MPC and Gurobi baselines incl. V2G profit.

**Charging physics found:**
- Constant power and constant efficiency are the norm (eFLIPS VehicleType `charging_efficiency` default 0.95; BETOS 0.9).
- acnportal/EV2Gym 2-stage model: constant up to a transition SOC (default 0.8), then max rate falls linearly to 0 at 100 %; the "continuous" method integrates this **analytically within the time step**, so results do not depend on step length [CODE `models/battery.py` l.207–280].
- SimSES converter loss: Notton form, no-load loss + quadratic loss [CODE `model/converter/notton.py`].

**Validation:** Decher & Schäfers 2024 [PAPER]: one depot (waste collection, sweepers), 47 charging events in March 2023, 2-min infrastructure-side power data: 3,280 kWh measured vs 3,278 kWh simulated; max deviation per 15-min step 120 kWh.

**For HDEV:**
- [JUDGEMENT] Add **LLF** (least laxity first). It is the natural fleet rule when dwell windows differ, and it maps directly onto Decher's flexibility categories.
- Add a **site minimum-connection search** (bisection like eFLIPS, or LP like eflips-opt) on top of the per-timestep simulation. That is the number grid applications need.
- Integrate taper analytically within each step (acnportal method) so the 5-min vs 1-min choice does not change energy delivered.
- Charger part-load efficiency: Notton form with sourced coefficients or charger datasheet points.
- Charging validation is a gap: no measured depot data yet.

## 8. Flexibility quantification

- **Decher & Schäfers 2024** [PAPER]: flexibility = possibility to shift load while plugged in. Category per vehicle and step: cat = t_departure − Δt_c,min − t, with Δt_c,min = ΔSOC energy / mean max charging power; priority ψ = Δt_c,min / (t_d − t). Load is shifted unchanged (no power modulation); no V2G; non-truck depot loads not yet included.
- **Decher et al. 2026** [PAPER]: grid impact of a 30-truck refuse depot (50 kW each, 300 kWh/day, 15:00–07:00) on SimBench MV grids; flexibility utilisation left for future work.
- **arXiv 2502.06435** [PAPER]: each EV = polytope of power bounds (0 when not plugged in) and energy bounds C_min ≤ C ≤ C_max with charge/discharge efficiencies and self-discharge, plus a minimum energy at departure. Fleet = sum of the b-vectors (assumes identical efficiencies). Not stated as energy-neutral.
  - [JUDGEMENT] Summing b-vectors gives a set that contains the true fleet set (Minkowski sum), so it can **overstate** fleet flexibility; the paper does not test this.
- **HDEV thesis:** energy-neutral up/down flexibility recovered within the charging period.

**For HDEV:**
- [JUDGEMENT] HDEV's energy-neutral rule is stricter and closer to how balancing products are settled. Keep it, but **report flexibility in the standard shape**: per time step, upper and lower power bound and cumulative energy bounds (the polytope), per vehicle and for the fleet. Every aggregator and DSO can read that shape.
- Compute the fleet envelope from vehicle simulations, not by summing bounds, or state that summing is an upper bound.
- Product check (FCR-D, FCR-N, mFRR minimum bids and response times, DSO pilot terms) stays as in the 26 Oct gap analysis; none of the tools above does that check.

## 9. Year / day structure (the 12 Oct open question)

- SpiceEV [DOCS]: one continuous scenario at a fixed step (example 15 min) over the whole period, with price, fixed load and generation time series.
- eFLIPS [CODE]: discrete-event simulation over the whole schedule; consumption per trip segment from a 4-D lookup table (grade, ambient T, load level, mean speed) with nearest-neighbour fallback outside the table.
- KIT [PAPER §4.1]: probabilistic weekly mileage, then daily trips, then payload allocation per trip, all drawn from survey data; Monte Carlo on top.
- **For HDEV:** [JUDGEMENT] a continuous year-long charging run carrying SOC across days and weekends is the common pattern. It removes the representative-week stitching problem in the 12 Oct note; the per-date consumption results feed it as energy per session.

## 10. TCO and financial modelling

**KIT** [PAPER §4.4]:
- TCO per km = (CAPEX × capital recovery factor + Σ discounted OPEX) / total km; CRF = r(1+r)^t / ((1+r)^t − 1); CAPEX net of discounted resale value.
- Truck price = retail-price-equivalent factor × (chassis + motor €/kW + HV €/kW + battery €/kWh); RPE 1.27 mature, 1.42 emerging (Link et al. 2024c).
- Resale: regression on age, mileage, power, axle configuration, body type, from used-truck listings (R² ≈ 0.75); battery residual = (scrap value 15 % + 85 % × remaining SOH) × battery cost; remaining life = min(cycle-life fraction, calendar-life fraction).
- Maintenance: BET 60–85 % of diesel per km; insurance 3 % of retail price per year; tolls by country with BET reductions (Eurovignette); driver wages omitted (one-for-one replacement assumed).
- Energy prices: Eurostat non-household bands (`nrg_pc_205_c`), trend indices, Monte Carlo (N = 500); LOW/MEDIUM/HIGH = 25/50/75 % quantiles.

**T3CO** [CODE]:
- Vehicle price from components plus markup; per-year depreciation rates → residual; insurance as % of price per year; financing with down payment and interest; discounting.
- Opportunity costs: payload (§2); **charging dwell time** beyond free time × cost per hour; **maintenance downtime** (planned h/yr + unplanned h/mile + tyre changes) × cost per hour.
- No battery replacement found in its cost models (searched).

**For HDEV:**
- COWI already covers wages, lost production time, financing and tax; what KIT and T3CO add is a **residual value model tied to age, mileage and battery SOH**, and **downtime and payload opportunity costs**.
- [JUDGEMENT] KIT's battery residual-value formula links ageing (§6) to TCO in one line; it is a good bridge.
- Quartile-based scenarios from a Monte Carlo are a clean way to present LOW/MED/HIGH without inventing scenario values.

## 11. CO₂

- Energi Data Service `CO2Emis` (queried live today): 5-minute CO₂ emission intensity per price area (DK1, DK2), e.g. 89 (DK1) and 117 (DK2) at 2026-11-09 19:00 DK time. Unit to confirm in the dataset description (presumably g/kWh).
- COWI uses annual Energistyrelsen factors; carculator does full life-cycle inventories.
- **For HDEV:** [JUDGEMENT] emissions at the actual charging times is a feature none of the tools read here has, and smart charging can be shown to cut CO₂, not only cost. Whether to use average intensity (CO2Emis) or a marginal factor is a method choice to state.

## 12. Validation and uncertainty practice

- Consumption: HDEV's leave-one-out vs 10 EEA-certified BETs is more than any tool read here did for BETs.
- Charging: Decher's depot comparison (energy and per-step deviation) is the template.
- Ageing: BLAST-Lite's "qualitative" warning and pack-vs-cell rule of thumb.
- Uncertainty: KIT Monte Carlo (N = 500, PERT on EEA parameters; quantile scenarios); BLAST-Lite scalar; HDEV has JCGM 101 planned.

## 13. Do not copy (bugs or weak spots found, as read in code)

1. BETOS grade force `sin(arctan(slope)/100)` (earlier file).
2. BETOS kWh model has no aux term and no regen cap; sensitivity scales energy ∝ payload.
3. BETOS Naumann coefficients differ in sign/value from SimSES (§6).
4. BETOS rainflow disabled (one cycle per window).
5. T3CO battery mass `ess_kg_per_kwh / ess_max_kwh` (divides).
6. EV2Gym degradation with hard-coded passenger-car constants and linear OCV.
7. PyBaMM ECM example data: undisclosed, not a real cell.
8. eFLIPS `ControlSmartCharging` passes 5 arguments to `SmartCharging(...)`, which takes 4, and checks `power_limit_grid` while storing `power_limit_gird` → would fail if called.
9. eFLIPS consumption lookup silently uses nearest neighbour outside the table.
10. KIT rolling-resistance temperature term (earlier file).

## 14. Where HDEV is already ahead (judgement, for positioning)

- VECTO-traceable vehicle physics with crosswind, VECTO driver model and per-component aux — none of the open tools combine these for trucks.
- Validation against certified BET results.
- Energy-neutral flexibility definition.
- PTO and stop-level payload modelling: none of the tools read here has PTO profiles.
- Danish regulatory layer (grid connection, Energinet, DataHub/Eloverblik).

## 15. Links / DOIs for Bob to fetch

Priority 1 (needed to implement correctly):
- Naumann et al. 2018, LFP calendar ageing, J. Energy Storage — doi 10.1016/j.est.2018.01.019
- Naumann et al. 2020, LFP cycle ageing, J. Power Sources — doi 10.1016/j.jpowsour.2019.227666
- Schmalstieg et al. 2014, NMC ageing model, J. Power Sources — doi 10.1016/j.jpowsour.2014.02.012
- Collath et al. 2024 (NMC 94 Ah OCV fit), J. Energy Storage 87, 111508 — doi 10.1016/j.est.2024.111508
- Karlsson et al. 2023a (SOC window vs FEC) — cited in KIT thesis bibliography
- DT-CARGO paper, Data in Brief 2023 — doi 10.1016/j.dib.2023.109246

Priority 2:
- Lauth, Mundt, Göhlich (eFLIPS smart charging algorithm) — cited in `smart_charging.py`; title not in code
- Lee, Li, Low et al., acnportal / ACN-Sim and ACN-Data papers (Caltech) — via acnportal docs
- Fallmann et al. 2023, refrigerated vehicle model, Appl. Therm. Eng. 220, 119719
- NREL CoolCab report — https://www.nrel.gov/docs/fy10osti/47415.pdf
- Hesse et al. 2017 (certified calendar life) and Link et al. 2024c (component costs) — in KIT bibliography
- 2023 J. Energy Storage multi-cell ageing study used by BLAST-Lite — doi 10.1016/j.est.2023.109042
- BLAST-Lite and SpiceEV source code: https://gh.ali360.cloudns.ch/NREL/BLAST-Lite and https://gh.ali360.cloudns.ch/rl-institut/spice_ev (blocked from here; a zip download would let me read them)
- Eurostat road freight microdata access terms (Reg. (EU) 70/2012) — for commercial-use check
- Directive 96/53/EC consolidated text (ZEV weight allowance) and BEK 1447/2025

---

## 16. Update, 9 Nov evening: papers Bob fetched + SpiceEV code

Read: Naumann et al. 2018 (J. Energy Storage 17, 153–169), Naumann et al. 2020 (J. Power Sources 451, 227666), Schmalstieg et al. 2014 (J. Power Sources 257, 325–334), Collath et al. 2024 (J. Energy Storage 87, 111508), Wikner et al. 2021 (J. Power Sources Advances 8, 100054), Fallmann et al. 2023 (Appl. Therm. Eng. 220, 119719), SpiceEV source code. Equation signs were checked on the page images, because text extraction drops minus signs.

### 16.1 Naumann LFP model: which re-implementation is right

**Calendar (Naumann 2018, Table 7 p. 163, Eq. 14 p. 165):** k_SOC,Rinc(SOC) = c·(SOC − 0.5)² + d with **c = −3.3903**, d = 1.5604.
- SimSES (−3.3903) matches the paper. **BETOS (+3.3903) is wrong**: it turns the paper's hump-shaped curve (most resistance growth at mid SOC, Fig. 7c) into a U shape (least growth at mid SOC).
- Other calendar values (paper, %-based): k_ref,Qloss 0.0012571 %·s^-0.5, Ea 17.126 kJ/mol, c 2.8575, d 0.60225 (cubic in SOC − 0.5); k_ref,Rinc 3.4194·10⁻⁸ %/s, Ea 71.827 kJ/mol. T_ref 25 °C, SOC_ref 100 %. SimSES stores them ÷100 (fraction, not %); consistent.

**Cycle (Naumann 2020, Table 6 p. 8, Eq. 8):** k_C-rate = a·C-rate + b.
- Table 6 as printed: a_Rinc = **0.0020**, b_Rinc = **−0.0021**. That gives a negative factor for every C-rate below 1.05, which is not physical.
- Fig. 6c on the same page shows the fitted line falling from about 0.0023 at 0 C to about 0.0005 at 1 C (read from the graph, approximate).
- So **the printed table appears to have a sign error.** BETOS (0.0023 − 0.0018·C) matches the figure; SimSES (0.0021 − 0.0020·C) swaps the table's signs and gives about 0.0001 at 1 C, which is below the figure.
- [JUDGEMENT] Neither implementation is a safe copy. Check for an erratum or ask the authors before using the Rinc cycle term. The Qloss cycle values (a 0.0630, b 0.0971, c 4.0253, d 1.0923, z = 0.5) have no such conflict.

**Validity limits stated by the papers:**
- Cell: Sony US26650FTC1 LFP/graphite, 3.0 Ah basis (Naumann 2020 §2.1).
- Cycle model has **no temperature term**; temperature effect between 25 °C and 40 °C was negligible. The paper says additional ageing (lithium plating) is expected below 25 °C or above 40 °C, which is not modelled.
- Cycle tests only up to 1 C. DOC < 80 % showed unsteady trends with capacity recovery; the model is fitted on 80 % and 100 % DOC.
- [JUDGEMENT] For trucks charged at high power in a Danish winter, both limits are exceeded. Results would be extrapolations and must be labelled so.

### 16.2 Schmalstieg 2014 (NMC)
- Cell: Sanyo UR18650E, 2.05 Ah min. All cycle tests at 1 C and 35 °C.
- Calendar: α_cap = (7.543·V − 23.75)·10⁶·exp(−6976/T); α_res = (5.270·V − 16.32)·10⁵·exp(−5986/T) (Eq. 14–15, p. 329, checked on the page image), with V the cell voltage in volts, T in kelvin and t in **days**; C = 1 − α_cap·t^0.75.
- Cycle: β_cap = 7.348·10⁻³·(V̄ − 3.667)² + 7.600·10⁻⁴ + 4.081·10⁻³·ΔDOD; β_res = 2.153·10⁻⁴·(V̄ − 3.725)² − 1.521·10⁻⁵ + 2.798·10⁻⁴·ΔDOD (values below 1.5·10⁻⁵ set to 1.5·10⁻⁵); Q in **Ah per cell**.
- Total: C = 1 − α_cap·t^0.75 − β_cap·√Q; R = 1 + α_res·t^0.75 + β_res·Q (Eq. 22–23, p. 330).
- The paper states the Arrhenius extrapolation "seems to be valid down to temperatures at 0 °C" in its verification. **Correction to §6:** BETOS clamping cell temperature to ≥ 25 °C is not required by the paper; it overestimates calendar ageing in cold weather (conservative, but not the source's method).
- [JUDGEMENT] The model needs cell voltage, so it needs an OCV curve for the same cell; Q must be per cell, not per pack.

### 16.3 Ageing "knee" (Collath et al. 2024)
- Late-life cells can show a steep rise in degradation (nonlinear ageing / knee), attributed mainly to lithium plating. Their aging study shows cells can return to a lower degradation rate with a reduced charging rate and voltage window. Physicochemical model built with SimSES + PyBaMM.
- [JUDGEMENT] √t / √FEC empirical models (Naumann, Schmalstieg) cannot produce a knee. For HDEV's end-of-life capacity check this matters: a model that never shows a knee can overstate remaining life near 80 % SOH. Report it as a stated limit.

### 16.4 SOC window (Wikner et al. 2021, Chalmers/Volvo Cars)
- Commercial 26 Ah pouch cell (LMO/NMC blend), 10 % SOC intervals plus wide windows, ±1/2/4 C, 25/35/45 °C, up to 28 months.
- Lower SOC windows significantly improved ageing; high SOC with high C-rate increased it (mainly loss of lithium inventory).
- [JUDGEMENT] Supports a charging-strategy output HDEV could show: "charge just in time to the needed SOC" vs "charge to 100 % on arrival", with an ageing difference. Calendar ageing at high SOC is the mechanism in Naumann too (k_SOC,Qloss rises steeply above ~75 % SOC, Fig. 7a).

### 16.5 Reefer (Fallmann et al. 2023)
- Control-oriented hybrid model of a **small** refrigerated chamber: lumped thermal capacities incl. insulation walls and secondary storage loop, explicit door openings, switching modes. Parameters fitted to 18.4 h of measurements of one vehicle; fit to validation data 86.2 % (temperature) and 88.7 % (total power).
- [JUDGEMENT] Good structure reference (door-opening term, wall heat capacity) but parameters are vehicle-specific fits, not a generic default. HDEV's ATP-K approach stays the default; the door-opening heat-transfer formula it cites ([37] in the paper) is worth fetching.

### 16.6 SpiceEV: what the code shows
- **Battery** [`battery.py`]: constant efficiency (default 0.95) applied by scaling the charging curve; self-discharge `loss_rate`; piecewise-linear charging curve (power vs SOC). Within each linear section the SOC is solved **analytically** (exponential solution, `t = ln((x2 + n/m)/(soc + n/m))·c/m`), so energy per step does not depend on step length. Same idea as acnportal.
- **Consumption input** [`generate_from_statistics.py`, `generate_from_csv.py`]: constant `mileage` kWh/100 km × distance → ΔSOC, or ΔSOC / arrival SOC given per trip; desired SOC = trip need × (1 + buffer, default 10 %). No physics. [JUDGEMENT] HDEV's per-trip energy can feed exactly this interface.
- **Flex band** [`generate/generate_schedule.py` `generate_flex_band`]: per time step `min` (no charging, plus battery/V2G discharge), `base` (fixed load minus generation), `max` (all present vehicles at max power), all clamped to the grid connector; energy needed tracked per standing interval; optional "core standing time" during which flexibility is guaranteed (warnings if a vehicle arrives or leaves inside it). Report gives average flexible power per 6 h window.
  - [JUDGEMENT] This is a power band plus interval energy, not a coupled power–energy envelope: `max` assumes every plugged-in vehicle can draw full power even when its energy need is already met. HDEV's energy-neutral approach is tighter. "Core standing time" is a useful product idea: the window an aggregator can rely on.
- **Costs** [`costs.py`]: German grid-fee structure: SLP vs RLM metering, capacity charge €/kW·a by voltage level with two price sets around a **2,500 h/a utilisation time**, commodity price per step, feed-in remuneration, taxes and levies. [JUDGEMENT] The structure transfers; the numbers do not. Danish tariffs (Radius/Cerius time-of-use, Energinet tariffs, elafgift) must be built from Danish sources.

### 16.7 Still to fetch
- Naumann 2020 erratum (if any) or author confirmation for the Rinc C-rate signs.
- The door-opening heat-transfer reference [37] in Fallmann 2023.
- Sony US26650FTC1 OCV data (needed to use Naumann with an OCV+Ri model) — SimSES ships an LFP OCV table for this cell; source to confirm in SimSES docs.

---

## 17. Update, 9 Nov late evening: Bob's forks (full repos)

Read from `mohgsaad-art/`: blast-lite, fastsim (commit of 28 Sep 2026), dt-cargo, acnportal, eflips-depot (5 Nov 2026).

### 17.1 BLAST-Lite (NREL) — battery ageing
- **Input is exactly what HDEV will produce:** a time series of time, SOC and temperature [CODE `degradation_model.py` `simulate_battery_life`]. The series is split into cycles with rainflow; degradation is updated at breakpoints (at most every day or every 1 equivalent full cycle).
- **Life to a threshold:** the input (e.g. one year) is repeated until a time, capacity or EFC threshold is reached → "years until 80 % capacity".
- **Ageing feedback (`is_conserve_energy_throughput`, default on):** as capacity falls, the same energy use becomes a deeper SOC swing, so ageing speeds up. [JUDGEMENT] This is the right default for trucks, which need the same kWh every day whatever the battery's health.
- **State update without "virtual time":** power-law states are advanced with their state equation (dy = k·p·(y/k)^((p−1)/p)·dx), which gives the same path-dependence as SimSES's virtual-time trick.
- **Every model carries its tested range** (`experimental_range`): cycling temperature, DoD, max charge and discharge C-rate. Examples:

| Model | Cycling T [°C] | Max charge C | Note in code |
|---|---|---|---|
| LFP-Gr 250 Ah prismatic (large-format, closest to truck cells) | 10–45 | 0.65 | "very poor extrapolations outside" tested T for cycling; only low-rate charge data |
| NMC-Gr 50/75 Ah (same 2023 study) | 10–45 | 1.75–2 | – |
| NMC622 DENSO 50 Ah | 10–60 | 1 | no knee seen |
| NMC811 LG M50 | 0–25 | 0.3 | – |
| NCA Panasonic / NMC811 LG MJ1 | 15–35 / 0–50 | 0.5 / 1 | "WILL NOT PREDICT KNEE-POINT" |
| LFP Sony-Murata (Naumann data) | 20–40 | 1 | capacity model re-fitted at NREL (doi 10.1149/1945-7111/ac86a8) |

- **Naumann resistance — a third version:** BLAST uses k_SOC,Rinc = −3.3903·(SOC − 0.5)**³** + 1.5604 [CODE `lfp_gr_SonyMurata3Ah_2018.py` l.214]; the paper's Eq. 14 is **squared**. Cycle C-rate term −0.002·C + 0.0021 (same as SimSES). So three open implementations of one paper give three different results (BETOS, SimSES, BLAST).
- **Uncertainty:** `degradation_scalar` multiplies all rates; the helper runs ±1/2/3σ with default σ = 0.15 (no source given in the code).
- **Stated caveats (README):** expected life only; no abuse, vibration or cell imbalance; models trained on 1–3 years and extrapolated to 10+ ("treat as qualitative"); pack life "20–30 % less than cell life" rule of thumb (no citation).
- **Do not copy:** `scale_vehicle_profile_to_annual_efcs` pads a profile with made-up high-DoD events to hit an EFC target; temperature input is taken as cell temperature (examples feed ambient climate data).

### 17.2 FASTSim full repo
- **No electric heavy truck is calibrated or validated.** The two trucks in `cal_and_val/` (Class 8 regional delivery, Class 4 Isuzu NPR) are conventional diesel (`pt_type: Conv`). BEV and thermal calibration is on cars only (2020 Chevrolet Bolt, 2021 Hyundai Sonata hybrid).
- **How NREL calibrates** [CODE `cal_and_val/thermal/cal_bev.py`, `python/fastsim/pymoo_api.py`]:
  - Data: Argonne dynamometer tests (ANL "D3" database) with SOC, cabin temperature and battery temperature, at −6.7 °C, 22 °C and 35–38 °C with HVAC set points and solar load noted.
  - About 70 % of test cycles for calibration, the rest held out for validation.
  - Fitted parameters include motor peak efficiency and efficiency range, cabin heat-transfer coefficients and heat capacity, battery thermal conductances and heat capacity, HVAC controller gains and COP fraction.
  - Error = time-averaged absolute difference between model and measured traces; multi-objective optimisation (pymoo).
- [JUDGEMENT] Two lessons: (1) NREL itself calibrates motor efficiency to measured energy, so HDEV's "calibrate to certified results" (Method C) is mainstream practice; (2) fitted thermal values are effective, not physical (Bolt: cabin heat-transfer 15.0 W/m²K driving vs 234.8 W/m²K stopped) and are car-specific, so they cannot be reused for trucks.

### 17.3 dt-cargo (TUM) — real truck operations
- The repo has **only plotting code**; the GPS cleaning pipeline is not in it (described in the Data in Brief paper).
- It ships a **public sample**: 53 trucks (GVW 18–32 t, 26–40 t with trailer), 101,826 trips ("tracks") from Aug 2021 to Apr 2022, with flags (home base, long haul, rest area, fuel station, industrial area). Licence ODbL.
- Quick statistics I computed from the public files (splitting days at midnight; flag definitions not checked against the paper, so indicative only):
  - Stop between two trips: median 22 min (10–90 %: 5–165 min). 11 % of stops ≤ 5 min, 66 % 5–60 min, 17 % 1–6 h, 5 % > 6 h. Long stops (> 6 h): median 10.6 h.
  - Many trucks start in the night: first departure per vehicle-day median about 03:00. The charging window is not always "overnight".
  - Distance per vehicle-day: median 95 km, 75 % 353 km, 90 % 517 km (many near-zero days from yard moves).
  - The `track_gap` column is not the time gap between trips (37.5 vs 50.0 min for the same pair); its unit needs the paper.
- [JUDGEMENT] A real source for default stop lengths and depot windows. HDEV's typed-route default of 45 min per stop is longer than this median; the default's own source should be checked.

### 17.4 acnportal repo
- Same code as the PyPI package. Adds ready KPIs [CODE `acnsim/analysis`]: share of requested energy delivered, share of sessions met (within 10 %), three-phase current unbalance (NEMA definition), energy cost and demand charge from time-of-use tariffs.
- [JUDGEMENT] "Share of sessions met" is a simple, client-friendly reliability number for the charging page.

### 17.5 eFLIPS-depot repo
- **Steady state:** schedules are repeated (daily or weekly, detected automatically) before and after the analysis period and only the middle is kept [CODE `api/__init__.py` l.709–713, 898–907]. Same idea as the 12 Oct note ("run two weeks, keep the second").
- **Charger count:** simulate an over-provisioned depot, then shrink each area to the peak number of vehicles there at the same time (`shrink_to_peak_usage`, 1-min resolution). Together with `lowest_power` (grid limit) this gives both number of chargers and connection size.
- Also: a diesel-fleet run for comparison, and depot parking layout generation (outside HDEV's scope).
