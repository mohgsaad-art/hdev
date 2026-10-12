# 06 — Auxiliaries (all): lorry BEV P_aux + bus SSM HVAC heat balance

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**.

> The lorry-BEV auxiliary values were traced in detail in `docs/decisions/2026-10-08_session-closeout-paux.md`. **I re-verified the key CSVs/constants against the v5.1.3 clone and they MATCH** (see 12-cross-check.md). This file (a) confirms that trace against stable, and (b) adds the **bus SSM HVAC** model (temperature/solar/heat-pump) which the paux doc only touched — the most relevant piece for Danish-winter cabin heating.

---

## 1. Lorry BEV P_aux (verified against v5.1.3)  [VECTO]

Per-step aux power (from `ElectricSystem.cs`, `ElectricAuxiliaries.cs`, `Conditioning.cs`):
```
P_aux(t) = P_ES + P_HVAC + P_PS + P_SP·[moving] + P_cond·[motor on]
```
All five are **electric**, drawn from the REESS, DC/DC efficiency = 1.0. BEV declares **exactly 4** aux (ES, HVAC, PS, SP) + Conditioning = 5 terms. No cooling fan. [VECTO]

**Constants re-verified** (`DeclarationData.cs`): `AlternatorEfficiency = 0.7` (:128), `DCDCEfficiency = 1.0` (:129), `HVACElectricEfficiencyFactor = 0.8` (:131). ✅ match paux doc §3.3.

**Tables re-verified against clone CSVs** (`Resources/Declaration/VAUX/`):
- `ES-Tech.csv`: Standard tech LH `1714.2857`, RD/UD/MU/Constr `1428.5714`; LED variant `1642.8571`/`1357.1429`. ✅ match paux §4.1. (×0.7 → 1200/1000 W etc.)
- `Cond-Table.csv`: Lorry LH 600, RD 600, UD 550, MU 550, Constr 600. ✅ match paux §4.5.
- `HVAC-Table.csv` Default: Group 5 = 350/200/150/**0**/200 (LH/RD/UD/MU/Constr); `None` = 0 everywhere. ✅ match paux §4.2 (incl. Group 5/10 MU = 0). (×1.25 → electric.)
- `PS-Table.csv` `_el` columns: `Small + elec. driven` 750/750/813/813/750; `Small + AMS + elec. driven` 675/675/732/732/675; `Medium Supply 1-stage + elec. driven` 750/687/687/687/750. ✅ match paux §4.3. (Read `_el` directly; AMS rows are NOT mech×0.7.)
- `SP-Table.csv`, `SP-Axles.csv`, `SP-Tech.csv`, `ES-Tech_Medium.csv` present and consistent. (SP = 0 while stopped.)

**State switching** [VECTO]:
- `SteeringPump` (ID `STP`) excluded when `VehicleStopped` (`ElectricAuxiliaries.cs`). Electric SP shares the `STP` ID so it is also zeroed at standstill.
- `Conditioning` (ID `COND`) on only when an EM is on (`!EmOffPrev`) or an electric PTO is on (`Conditioning.cs:GetPEV_SHEV_PowerDemand`). Ties to M0.16 / 05 §3.
- Fan excluded when engine off — irrelevant (BEV has no fan).

**Cycle-carried aux** [VECTO]: cycle files may have `AUX_<id>` columns (kW→W) read by `AuxSupplyPowerReader.cs` — a per-row aux override, separate from the declaration tables. (See 08-cycles-and-missions.md.)

**Illustrative totals** (paux §5, technologies chosen for arithmetic): Group 5 RD BEV ≈ 2938.9 W (moving, motor on) / 2537 W (stopped, motor on) / 1937 W (stopped, motor off). These are the M0.15 acceptance numbers.

---

## 2. Bus SSM HVAC — the temperature-dependent heat-balance model  [VECTO]

Buses use a **Steady-State Model (SSM)** for HVAC that trucks do **not**: `Models/BusAuxiliaries/DownstreamModules/Impl/HVAC/SSMCalculate.cs` + `SSMInputs.cs` + `SSMTOOL.cs`. It computes HVAC **electrical** and **mechanical** base/adjusted power and **heating demand** as a **weighted average over environmental conditions** (temperature × solar), with explicit **heat pumps** and **electric/fuel heaters**.

### 2.1 Climate points  [VECTO] `Resources/Declaration/Buses/DefaultClimatic.aenv`
The "11 climate points" (ID, EnvTemp °C, Solar W/m², WeightingFactor, heating/cooling flag, then **heat-pump COP per technology** and **heater efficiency**):
```
ID, EnvTemp, Solar, Weight, h/c, R-744, non R-744 2-stage, 3-stage, 4-stage, continuous, water el. heater, air el. heater, other el. heating, fuel heater
1 , -20 , 10 , 0.0053 , h , 1.80 , -    , -    , -    , -    , 0.93 , 0.93 , 0.93 , 0.80
2 , -5  , 30 , 0.0826 , h , 2.04 , 1.54 , 1.64 , 1.68 , 1.78 , 0.93 , 0.93 , 0.93 , 0.80
3 ,  2  , 30 , 0.0826 , h , 2.50 , 2.00 , 2.10 , 2.10 , 2.22 , 0.93 , 0.93 , 0.93 , 0.80
4 ,  8  , 20 , 0.1661 , h , 2.98 , 2.70 , 2.80 , 2.82 , 2.94 , 0.93 , 0.93 , 0.93 , 0.80
...
8 , 20.5, 30 , 0.1243 , c , 3.80 , 3.62 , 3.74 , 3.74 , 3.88 , - , - , , -
11, 33  ,150 , 0.0427 , c , 2.14 , 2.50 , 2.60 , 2.62 , 2.74 , - , - , , -
```
[VECTO] file content (first/last rows quoted). The weighting factors sum to ≈1.0 across the 11 points — this is the EU "average European climate" weighting.

### 2.2 Heat-pump / heater physics  [VECTO] `SSMCalculate.cs`
- Heating power per compartment (driver / passenger) split by `MaxHeatingPower · HVACContribution`.
- **Heat pump mechanical power = heating demand / COP** for the selected heat-pump type at that environmental condition: `HeatPumpPowerMech = heatingDemand / cop` (COP from `env.HeatPumpCoP[type]`; `NaN` COP → 0 → falls back to electric/fuel heater). [VECTO] `SSMCalculate.cs:182-196`.
- Electric heater uses the heater efficiency (0.93) and fuel heater 0.80. [VECTO] `.aenv` columns + `SSMCalculate`.
- Final HVAC power = weighted sum over the 11 points (`ElectricalWBase/Adjusted`, `CalculateAverageHeatingDemand`). [VECTO] `SSMCalculate.cs`.

### 2.3 Smart electrics, pneumatics, other bus aux
The bus auxiliary stack (`Models/BusAuxiliaries/`) also has smart-electrics (alternator/battery management, `SimpleBattery.cs`, `BatteryLimits.cs`), pneumatics, and the SSM. These are bus-only; trucks use the flat declaration tables (§1). [VECTO]

---

## 3. Danish-winter cabin heating — what's usable  [INFERRED]
- **Truck declaration HVAC has no heating and no temperature input** (§1; HVAC is one constant per group×mission, A/C-compressor only). This is the confirmed gap: VECTO declaration does **not** represent Danish winter cabin heating for a lorry.
- **The bus SSM model IS a real, temperature-dependent heat-balance** with heat-pump COP down to −20 °C (R-744 COP 1.80) and electric/fuel heater efficiencies. If HDEV wants a physically grounded cabin-heating term for Danish winter, the SSM climate map (`DefaultClimatic.aenv`) + the `heatingDemand/COP` physics (`SSMCalculate.cs`) are the **authentic VECTO source** to reuse — but it is a **bus** model, so applying it to a lorry is an **HDEV extension beyond VECTO declaration** and must be flagged as such (matches paux §10 "reuse VECTO's bus SSM heat-balance physics per row with DMI temperature/solar").
- Two gaps the paux doc already flagged remain: (a) mapping VECTO's 11 discrete climate points to continuous DMI temperature; (b) a heat-pump COP value at exactly −20 °C exists (1.80 for R-744) but no sub-−20 °C extrapolation. [VECTO] COP table stops at −20 °C.

---

## 4. What HDEV needs
1. Lorry P_aux: the 5-term function (M0.15) with the verified tables/constants and the `moving`/`motor_on` toggles.
2. Blank/`---` cells → raise (mirror VECTO).
3. (Optional, flagged non-VECTO) cabin heating via the bus SSM: `P_heat_el = heatingDemand(T) / COP(type, T)` using `DefaultClimatic.aenv` + DMI temperature, clearly labelled an HDEV extension.

---

## 5. Open questions (from paux doc, still open)
- `EmOffPrev` for BEV (resolved in 05 §3: EM off ⇔ EMTorque==null).
- Why Group 5/10 MU HVAC = 0 (explicit 0, not blank).
- AMS `_el` values (read directly, not derived).
- Heat-pump COP below −20 °C (not in VECTO table).
- Continuous-temperature mapping of the 11 climate points.

---

## 6. Unblocks spec task(s)
- **M0.15 (p_aux)** — all tables/constants re-verified against v5.1.3; the 5-term function + state toggles + blank-raise behaviour are confirmed. Acceptance numbers 2938.9/2537/1937 W stand.
- **M0.16** — `Cond` toggles on `!EmOffPrev` (motor on), confirmed.
- **Cabin-heating gap / Danish winter** — the bus SSM (`SSMCalculate.cs`, `DefaultClimatic.aenv`, COP table incl. −20 °C) is the only authentic VECTO temperature-dependent HVAC physics; usable as a flagged HDEV extension. Feeds the assumptions-report gap wording (M1.7) and any future heating layer.
- **12-cross-check.md** — this file's verification feeds the cross-check (all paux numbers match v5.1.3).
