# VECTO → HDEV research index

Research mapping everything in **VECTO (stable, commit `d16ba783c`, v5.1.3)** that HDEV can use or must replicate for **battery-electric lorries**. Clone: `mohgsaad-art/VECTO`. Read-only research — no `src/`, spec, steering, or `docs/decisions` were changed. Every finding cites a file path (+ line numbers where useful) and is tagged **[VECTO]** (read from source) or **[INFERRED]** (interpretation). No values were invented; missing items are named and marked missing.

> **Headless-run status:** VECTO **cannot** be built/run in this sandbox — network is INTEGRATIONS_ONLY and NuGet restore fails (403). The "run one BEV job" step was skipped by design; see `11-validation-data.md` §3.

## Files (one line each)
| file | topic |
|---|---|
| `01-electric-machine.md` | EM efficiency/loss map (format, interpolation, power→loss), full-load & drag torque, overload/thermal buffer, inverter/ADC, regen/accel limits, generic/standard (Annex Xb) maps, the 0.95/0.95/0.98 placeholder vs VECTO's 0.98. |
| `02-transmission-axle.md` | Gearbox/axle loss maps for BEV (single-speed, APT-N, IEPC, BEVCycleGearbox); constant-efficiency fallback `(1−η)·|T|`; generic values (ADC 0.98/0.96, IEPC axle 0.96). |
| `03-battery.md` | REESS model: OCV(SoC), Ri(SoC,t_pulse), quadratic current solve, limits, SoC window, connection resistance, `I²·Ri` loss always, no temperature. **M3.3** + "no battery loss while driving" gap. |
| `04-charging.md` | VECTO does NOT simulate charging; only OVC-HEV/IMC energy-accounting lookups (power 500/250/100 kW, 0.5 h/event). Battery primitives for the HDEV charging stepper. |
| `05-braking-regen-driver.md` | Regen-first then mechanical-brake split, regen limits, coast/roll, LAC/EcoRoll/PCC defaults, EmOffPrev (**M0.16**), high-mass power limit (**M0.11**), BEV uses common `Truck.vacc` (**M0.13**). |
| `06-auxiliaries-all.md` | Lorry BEV 5-term P_aux (verified vs v5.1.3) + bus SSM HVAC heat-balance (climate points, heat-pump COP incl. −20 °C) for Danish-winter cabin heating. **M0.15/M0.16**. |
| `07-pto-all.md` | PTO formats (.vptol/.vptoc/.vptoel), PTO-tech idle losses, driving vs stops, BEV electric PTO; `P_PTO_el` unit confirmed **kW** (docs' "Nm" is an error). **M0.10/M0.15**. |
| `08-cycles-and-missions.md` | Mission cycles, columns (hw/pto/AUX_), distance/time/measured-speed types, grade read directly vs altitude derived (**M0.12**), stop handling, cycles end with v=0 (MU stop=3). |
| `09-vehicle-data-and-defaults.md` | SegmentTable (CdxA 8.7 Group 5), Payloads (+linear interp), body/trailer weights, mass/payload cap (**M0.20**), Wheels, load-dependent RRC (0.9), IMC ΔCdxA (**M0.18**), CdxA defaults for **§5.7**, mission weighting. |
| `10-outputs-and-reporting.md` | `.vmod` BEV columns (SoC, U0, I, P_reess_*, P_em_*), `.vsum` battery columns, MRF/CIF/VIF kWh/km·(t·km)·(m³·km) per mission/payload + weighted, GraphDrawer. |
| `11-validation-data.md` | Generic BEV lorry jobs + unit-test numeric anchors (battery SoC-step, usable energy, overload loss; EM map torque; overload buffer); headless-run blocked. **M5.3**. |
| `12-cross-check.md` | Every number in the paux + defaults decision docs vs v5.1.3: **all match, no differences**; two open items resolved. **M1.1**. |
| `14-pto-aux-followups.md` | PTO & aux follow-ups: 4 PTOActivity states incl. PTO-while-driving; stop = StoppingTime + PTO Duration; electric PTO energy ∫P_PTO_el·dt (0.14993 kWh/activation); SP ×0.7 = alternator efficiency, UF/B/S = unloaded&friction/banking/steering; Conditioning = electric-propulsion-component thermal mgmt; no lorry aux temperature dependence; BEV aux tech lists; Wheels r_dyn=d·F/(2π). Confirms/corrects 07. |

## Spec task → finding → file
| spec task / req | finding | file |
|---|---|---|
| **M0.8** | Cycles end with v=0; first v=0/stop=0 forced to 1 s; stop points duplicated | 08 |
| **M0.10** | PTO stop-time source = `.vptoel`/`.vptoc` activation cycles (deferred gap) | 07 |
| **M0.11** | High-mass power limit is emergent (overload → reduce accel via `GetMaxDriveTorque` + `MaxDischargePower`); HDEV defers it | 05, 01 |
| **M0.12** | Declaration `.vdri` carry grade `<grad>` directly; altitude derived; flat `grade_pct` matches VECTO (secant only for altitude input) | 08 |
| **M0.13** | BEV lorries use the common `Truck.vacc` (reference bundle byte-identical to generic BEV job) | 05 |
| **M0.15** | 5-term P_aux + constants/tables re-verified; blank/`---` → raise; 2938.9/2537/1937 W | 06, 12 |
| **M0.16** | EM off ⇔ `EMTorque == null` (`ElectricMotor.cs:EmOffPrev`); `Cond` toggles on motor-on / EPTO-on | 01, 05, 06 |
| **M0.18** | `DeltaAirDragAreaIMC` default 0 is VECTO-correct for non-pantograph; 0.6 m² only OverheadPantograph × infra share | 09 |
| **M0.20** | Mass = vehicle+body+payload; payload cap = `GVW − (curb+body+trailer curb)` | 09, 12 |
| **M0.21** | Sign-dependent η lives in the EM map (drive vs gen); battery `I²·Ri` loss belongs in consumption; driveline loss torque-based | 01, 02, 03 |
| **M1.1 / §5.7** | Defaults (CdxA 8.7, payloads, body masses, aux) all verified vs v5.1.3; CdxA citeable from `SegmentTable.csv` instead of missing Annex VIII | 09, 12 |
| **M3.0/M3.4/M3.7** | No VECTO charging sim; stepper reuses `Battery.Request(+power)` + `MaxChargePower` + SoC cap + `I²·Ri` | 04, 03 |
| **M3.1/M3.2** | Capacity [Ah], UseableStoredEnergy, SoC window | 03 |
| **M3.3** | OCV+Ri quadratic battery model, exact formats/units, generic 243 kWh pack | 03 |
| **M5.3** | Component-level numeric anchors (battery, EM map) runnable now; full-run reference blocked in-sandbox | 11 |
| **req §1.5.4 / §5 gaps** | 0.95/0.95 are HDEV placeholders (no VECTO equivalent); 0.98 is VECTO's clamp fallback; real path is the normalized PSM/ASM map | 01 |
| **Cabin heating gap** | Truck declaration has none; bus SSM (`SSMCalculate.cs` + `DefaultClimatic.aenv`, COP to −20 °C) is the only authentic VECTO temperature-dependent HVAC | 06 |
| **M2.8 (weighting)** | Two-payload (low/reference) mission weighting from `MissionProfileWeights.csv`; sum 1.0 (or 2.0 vocational) | 09 |

## Top 10 things HDEV should adopt next (ranked)
1. **OCV + Ri quadratic battery model** replacing the exponential taper — the single biggest fidelity gain; fully specified with exact formats. **[VECTO]** `03-battery.md`.
2. **Battery `I²·Ri` loss every step (drive + regen)** — closes the "no battery loss while driving" gap; VECTO always computes it. **[VECTO]** `03-battery.md`.
3. **Switch to the common `Truck.vacc`** (M0.13) — zero-risk, the reference bundle file is byte-identical to the generic BEV job. **[VECTO]** `05-braking-regen-driver.md`.
4. **`motor_on = not EmOffPrev` (EM off ⇔ torque==null)** for the P_aux `Cond` toggle (M0.16) — exact VECTO rule. **[VECTO]** `01`, `05`.
5. **Payload cap = GVW − (curb+body+trailer curb)** and mass assembly (M0.20) — correct, with citations. **[VECTO]** `09-vehicle-data-and-defaults.md`.
6. **Grade read directly from `<grad>`** (M0.12) — confirms HDEV flat `grade_pct` already matches VECTO on declaration cycles; no secant needed. **[VECTO]** `08-cycles-and-missions.md`.
7. **CdxA defaults from `SegmentTable.csv`** (Group 5 = 8.7 m²) to unblock §5.7 without the missing Annex VIII extract. **[VECTO]** `09`, `12`.
8. **Component-level validation now** (battery SoC-step, usable energy, overload loss; EM map torque) using shipped `GenericBattery.vbat` / `GenericEMotor.vem` — the runnable part of M5.3. **[VECTO]** `11-validation-data.md`.
9. **Regen-first-then-mechanical-brake split** with regen vanishing at high SoC — the correct energy accounting for braking. **[VECTO]** `05-braking-regen-driver.md`.
10. **Bus SSM heat-balance for a flagged Danish-winter cabin-heating layer** (COP to −20 °C, electric/fuel heater η) — the only authentic VECTO temperature-dependent HVAC; **[INFERRED]** that it is reusable for a lorry (it is a bus model → must be flagged non-VECTO). `06-auxiliaries-all.md`.

## Notes / still-missing
- **Regulation extracts remain missing** from `reference/regulation/`: Annex Xb (electric-machine map) and Annex VIII (air-drag standard values). This research cites **VECTO code/resources** for those values (normalized PSM/ASM `.vmap`; `SegmentTable.csv CdxA_Default`), per `vecto-grounding.md`. The regulation *text* is still flagged missing.
- Full-run VECTO reference (per-mission kWh/km) must be produced **off-sandbox** (NuGet blocked here).
