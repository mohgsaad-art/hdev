# 04 — Does VECTO model charging?

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**.

---

## 1. Short answer
**VECTO does NOT simulate charging as a physical, time-domain process** (no SoC-vs-time charging stepper, no charger curve integration during a plugged-in session). For **pure BEV declaration**, SoC only *decreases* over the driving cycle; the battery is not recharged in the simulation. [INFERRED from `Battery.cs` only being driven by the EM power request during the cycle; no charging component in the BEV powertrain build.]

What VECTO **does** have is **charging-energy ACCOUNTING via lookup tables**, used only for **OVC-HEV** (plug-in hybrids) and **IMC** (in-motion charging) to compute an energy/CO₂ credit — not a charging simulation. [VECTO] `StationaryChargingLookup.cs`, `DeclarationData.cs` `CalculateChargingEfficiencyOVCHEV` / `CalculateChargingEfficiencyIMCOVCHEV`.

---

## 2. The charging-accounting lookups  [VECTO]
`StationaryChargingLookup.cs` loads three declaration tables keyed by (vehicle group × mission):

### 2.1 Stationary charging **power from infrastructure** [kW]
`Resources/Declaration/VehicleOperation/StationaryChargingPower.csv` (`StationaryChargingPowerFromInfrastructureLookup`, value in **kW**):
```
Vehicle Group , Long haul , Regional delivery , Urban delivery , Municipal utility , Construction , ...
2  , 500 , 250 , 250 , --- , ---
4  , 500 , 250 , 250 , 150 , 100
5  , 500 , 250 , 250 , --- , 100
9  , 500 , 250 , --- , 150 , 100
...
31 / P31SD / P31DD , --- , --- , --- , --- , --- , 450 , 450 , 450 , 300  (buses)
```
`---` = not applicable. Group 5 long-haul = **500 kW**, regional/urban delivery **250 kW**, construction **100 kW**. [VECTO] file content.

### 2.2 Stationary charging **duration per event** [h]
`.../StationaryChargingDuration.csv` (`StationaryChargingDurationPerEventLookup`, value in **hours** → seconds): mostly **0.50 h** per event across lorry missions. [VECTO] file content.

### 2.3 Charging **events per day/mission**
`.../ChargingEventDuringMission.csv` (`StationaryChargingEventsPerDayLookup`, dimensionless count). [VECTO]

### 2.4 In-motion-charging infrastructure share
`ShareInMotionChargingInfrastructureLookupBase.cs` + `GetShareIMCInfrastructure` — fraction of a mission with IMC (overhead/rail) available; feeds the ΔCdxA (09 §7) and the IMC charge credit. [VECTO]

### 2.5 How they're used
`DeclarationData.cs` (~lines 1940-2042) computes a weighted **charging efficiency** (`EtaChargingWeighted`) and energy-from-grid shares for OVC-HEV/IMC CO₂ accounting — a post-processing credit, not an in-loop charge. There is **no** per-step battery charge integration against a charger. [VECTO] `CalculateChargingEfficiencyOVCHEV`, `CalculateChargingEfficiencyIMCOVCHEV`.

---

## 3. Closest physics pieces VECTO does have  [VECTO]
Even without a charging simulation, these primitives exist (and are what a charging stepper would reuse):
- **Battery charge limits**: `Battery.MaxChargePower(dt)`, `MaxChargeCurrent(dt)`, SoC-dependent `MaxCurrentMap.LookupMaxChargeCurrent`, and the `(MaxSOC−SoC)·Cap/dt` per-step cap (03 §4). A charge request is just `Request(absTime, dt, +power)`.
- **Charge loss** `I²·Ri` applies identically to charging (positive current). (03 §1.)
- **Connection resistance** loss in the electric system (03 §6).
- **WHRCharger** (`WHRCharger.cs`) and **GensetChargerAdapter** (`GensetChargerAdapter.cs`) — on-board chargers for *waste-heat recovery* and *genset* (range-extender) configs, not depot charging. `GensetChargerAdapter` sets `ConnectionSystemResistance = 0`. [VECTO]

---

## 4. Implication for HDEV
- HDEV's charging engine (M3.x) is **beyond VECTO** — there is no VECTO depot/opportunity charging simulation to match. HDEV must build it from the battery primitives (03) + its own charger model; this must be flagged as an **HDEV addition**, not a VECTO reproduction. (Matches the grounding note "No aux during depot charging — open for the charging engine".)
- The VECTO **charging-power table** (Group 5 LH 500 kW / RD 250 kW / Construction 100 kW) and **0.5 h/event duration** are the only VECTO-sourced charging numbers; usable as *reference defaults* for the sizing/sweep, cited as declaration accounting values (not physics).
- The battery stepper (`Request(dt, +power)`, `MaxChargePower`, SoC cap, `I²·Ri`) is exactly what the HDEV charging stepper (M3.0/M3.4) should emulate for the charge direction.

---

## 5. Open questions
- Does HDEV want to anchor charger kW defaults to VECTO's `StationaryChargingPower.csv` (500/250/100 kW) or to Danish real-world/Energinet specs? (The grounding doc marks charging-window specs "from Energinet, to be sourced".)
- IMC (overhead pantograph) in-motion charging: if HDEV ever models it, `ShareInMotionChargingInfrastructureLookupBase` + the IMC ΔCdxA (09 §7) are the VECTO pieces. Out of current scope.

---

## 6. Unblocks spec task(s)
- **M3.0 / M3.4 / M3.7 (charging stepper)** — confirms there is **no** VECTO charging simulation to match; the stepper reuses `Battery.Request(+power)` + `MaxChargePower` + SoC cap + `I²·Ri`. Charging engine is a flagged HDEV addition.
- **M3.1 / M3.2 / M3.10 (sizing, sweep)** — VECTO charging-power table (Group 5: 500/250/100 kW) and 0.5 h/event as reference defaults.
- **M3.8 (cheapest-first)** — unaffected by VECTO (pure HDEV).
- Clarifies the grounding gap "No aux during depot charging" — VECTO never models the charging phase at all, so any charging-time aux is 100% an HDEV addition.
