# 13 — PR #3 follow-ups: verifications against VECTO v5.1.3

Resolves the five items raised after PR #3. VECTO clone verified at **stable, commit `d16ba783c`** (v5.1.3). Tags: **[VECTO]** = read from the clone; **[CORRECTION]** = fixes an earlier research-file statement.

---

## 1. Grade in the force balance — CORRECTION to `08-cycles-and-missions.md`  [VECTO][CORRECTION]

**Question:** which grade value is used in the force balance at each simulation step — left waypoint's `<grad>`, interpolated `<grad>`, or an altitude secant?

**Answer: an ALTITUDE SECANT over the step `ds`.** File `08` was **wrong** to conclude "declaration cycles use `<grad>` directly, no secant needed". The correct chain:

1. **At cycle load**, the per-point `<grad>` column builds an **altitude profile** by integration:
   `altitude += (entry.Distance − prevDistance) · RoadGradientPercent / 100.0`
   [VECTO] `DrivingCycleDataReader.cs:236` (`FilterDrivingCycleEntries`). So `<grad>` is consumed to make altitudes; it is **not** carried through to the force balance as-is.

2. **At each simulation step**, `DistanceBasedDrivingCycle.ComputeGradient(ds)` returns:
   ```csharp
   CurrentState.Altitude = VectoMath.Interpolate(leftSamplePoint.Distance, rightSamplePoint.Distance,
       leftSamplePoint.Altitude, rightSamplePoint.Altitude, PreviousState.Distance + ds);
   var gradient = VectoMath.InclinationToAngle(
       ((CurrentState.Altitude - PreviousState.Altitude) / ds).Value());
   return gradient;
   ```
   [VECTO] `DistanceBasedDrivingCycle.cs:412-433`. This is a **secant**: `grade = atan( (altitude(prev+ds) − altitude(prev)) / ds )` — altitude interpolated linearly between the bracketing sample points' altitudes, then differenced over the actual step length `ds`. **It is therefore step-size dependent.**

3. **Only two exceptions return the left sample's `RoadGradient` directly:** when `leftSample.Distance == rightSample.Distance` (zero-length interval) or `ds == 0` (initialization). [VECTO] `DistanceBasedDrivingCycle.cs:421-425`.

4. That `gradient` is passed as `CurrentState.Gradient` into `NextComponent.Request(absTime, ds, speed, CurrentState.Gradient)` (`DistanceBasedDrivingCycle.cs:341-344`) and reaches `Vehicle.SlopeResistance(gradient)` and `Vehicle.RollingResistance(gradient)` (`Vehicle.cs:238, 225`). So the **force balance uses the secant grade**, not the raw column value.

**Consequence for the spec:** the older HDEV note (requirements §1.1.12) was **right**; file 08's "no secant needed" was wrong. **M0.12 is NOT resolved** — HDEV's flat `grade_pct` does **not** match VECTO on a cycle where altitude is non-linear within a sample interval and the step `ds` differs from the sample spacing. The decision for Bob stands: match VECTO's altitude-secant grade (interpolate altitude between points, difference over `ds`) or record the difference as a flagged gap. `08-cycles-and-missions.md` §4 and the Top-10 item should be read with this correction.

> Note: on segments of **constant** `<grad>` the altitude is linear, so the secant over any `ds` equals that constant grade — i.e. for the simple reference cycles with piecewise-constant grade the numeric difference may be small, but the **mechanism** is the secant, and it diverges wherever grade changes within a step or `ds` straddles a sample point. Do not rely on "equal in practice" without a per-cycle check.

---

## 2. Payloads.csv — files are IDENTICAL  [VECTO][CORRECTION]

**Question:** `09` prose said `reference/vecto/resources/Payloads.csv` is "a small truncated version; the real one is different"; `12-cross-check.md` said identical and complete. Which is true?

**Answer: IDENTICAL and complete.** `12` is correct; the `09` prose was wrong.
```
md5  reference/vecto/resources/Payloads.csv                         = d5b9d22e490dbdfca3618ce2b7e86aaa
md5  VECTO/.../Resources/Declaration/Payloads.csv (clone, v5.1.3)   = d5b9d22e490dbdfca3618ce2b7e86aaa
```
[VECTO] both files are the same 5-line table (header + 4 GVW rows: 3500/7400/7500/16000). The two misleading lines in `09-vehicle-data-and-defaults.md` (the §5 header note and the parenthetical after the Payloads table) are **incorrect** and should be read as superseded by this item. The `defaults.py` work can cite either path — they are byte-equal.

---

## 3. StationaryChargingPower.csv (500/250/100 kW, 0.5 h/event) — NOT a charger spec  [VECTO]

**Clarification:** these values are **VECTO's OVC-HEV / IMC energy-accounting table**, used to compute a plug-in-hybrid / in-motion-charging CO₂ credit — **not** a charger power specification and **not** a depot-charging physics input. [VECTO] `StationaryChargingLookup.cs`, `DeclarationData.cs:CalculateChargingEfficiencyOVCHEV/IMCOVCHEV` (see `04-charging.md` §2).

**Rule for the spec:** do **not** use 500/250/100 kW or 0.5 h/event as HDEV charger defaults. Wherever they are mentioned they must be labelled **"VECTO OVC-HEV accounting table, not a charger specification"**. HDEV charger ratings are OEM/CPO-supplied slots (see the new Requirement B slot registry) or real sourced defaults — never these accounting values. `04-charging.md` §4/§6/§8 wording that suggested them as "reference defaults for sizing/sweep" is superseded by this item.

---

## 4. M5.3 full reference run — task for Bob (off-sandbox)  [VECTO]

VECTO could not be built in the sandbox (NuGet restore blocked, `11-validation-data.md` §3). To get the end-to-end numeric reference M5.3 needs:

**Task for Bob (off-sandbox, official VECTO release):**
- Run `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BEV_E2.vecto` (or the equivalent current generic Group-5 BEV lorry job) with an official VECTO release on your own machine.
- Bring back, from the output files:
  - **per-mission `kWh/km`** (and `kWh/(t·km)`) — from the declaration report / `.vsum` electric-energy columns (see `10-outputs-and-reporting.md` §3).
  - **SoC start / end** per mission — `.vsum` `REESS_StartSoC`, `REESS_EndSoC`.
  - **`E_REESS_LOSS`** per mission — `.vsum` battery energy-balance column.
  - Keep the per-step `.vmod` for `SoC`, `P_REESS_T`, `U_0_REESS`, `I_REESS` if a row-level comparison is wanted (`10` §1).
- These become the M5.3 tolerance anchors. Until supplied, M5.3's full-run comparison stays **blocked** (component-level anchors in `11` §2 are usable now).

This is captured as a spec task (tasks.md, M5) marked 🔒 (needs Bob to run VECTO and supply the numbers).

---

## 5. 0.95/0.95/0.98 efficiencies — gap wording  [VECTO]

**Clarification (for the spec gap wording):** the 0.95 (motor) / 0.95 (inverter) / 0.98 (gearbox) efficiencies are an **HDEV placeholder with no VECTO equivalent**. VECTO uses a **speed × torque → electrical-power map** for the electric machine (inverter folded into the same map), not scalar efficiencies (`01-electric-machine.md` §2, §7). VECTO's only scalar EM-side constants are the **0.98 efficiency-clamp fallback** and the **0.98/0.96 ADC** mechanical factors — there is no 0.95 anywhere.

**Rule for the spec:** gap wording reads **"HDEV placeholder with no VECTO equivalent; VECTO uses a speed×torque electrical-power map (`01-electric-machine.md`)"**. It stays a **flagged gap**; adopting the map is a **decision for Bob**, not an automatic change. (requirements §1.5.4, §5 gap list updated accordingly.)

---

## Summary of corrections to earlier research files
| file | statement | correction |
|---|---|---|
| `08-cycles-and-missions.md` §4 + Top-10 | "declaration cycles use `<grad>` directly; no secant needed; M0.12 matches VECTO" | **Wrong.** Force balance uses an **altitude secant** per step (`DistanceBasedDrivingCycle.cs:412-433`); M0.12 **not** resolved. |
| `09-vehicle-data-and-defaults.md` §5 note + Payloads parenthetical | "reference `Payloads.csv` is small/old / may differ" | **Wrong.** Byte-identical to the clone (md5 match). |
| `04-charging.md` §4/§6/§8 | "500/250/100 kW, 0.5 h/event usable as reference charger defaults" | **Superseded.** OVC-HEV accounting table, **not** a charger spec; do not use as charger defaults. |

These research files are left as-is historically (PR #3 is merged); this follow-up file is the authoritative correction and is what the spec cites.
