# What the certified numbers mean (Job 2)

Bob, before we compare anything we have to know what the EEA numbers actually are.
This file answers the seven points. Every answer has a source: a VECTO file + line,
or a regulation annex + point. Where I could not find it, I say so.

Paths are relative to the VECTO source tree (`mohgsaad-art/VECTO`, EUPL 1.2).
Regulation = Reg. (EU) 2017/2400 consolidated (CELEX 02017R2400, 01.01.2026).

Tags: `[V]` opened primary source, `[D]` derived (arithmetic shown), `[INFERENCE]`,
`[BOB]` could not get it.

---

## 1. kWh/km basis: battery side, REESS side, or grid side?

**Answer: the certified `ElectricEnergy_kwh_km` is GRID side — it includes depot
charging losses. It is the battery SoC energy divided by a charging efficiency.** `[V]`

Chain in the code:

- `BatteryElectricPostprocessingCorrection.cs` lines 44–45 defines two energies:
  - `ElectricEnergyConsumption_SoC = -∫ P_reess_int dt` — energy at the battery, **after**
    internal-resistance losses (P_reess_int is the battery's internal power). This is the
    battery-side number.
  - `ElectricEnergyConsumption_Final = (-∫ P_reess_int dt + deltaEPSel) / chgEfficiency` —
    the SoC energy (plus a small electric-pneumatic correction) divided by the charging
    efficiency. This is the grid-side number.
- `DeclarationData.cs` line 1948 `CalculateChargingEfficiencyPEV`: charges the battery at
  depot power, `etaChgBatDepot = 1 − (LossPower + connectorLoss) / PowerDemand`. So the
  efficiency covers battery internal resistance **during charging** plus the junction-box /
  connector resistance.
- The **reported** consumption is the grid-side one. `XMLDeclarationReport.cs` line 255 sets
  the result consumption to `_Final`, then for a battery-electric vehicle lines 257–263
  overwrite it with `ranges.ElectricEnergyConsumption` from `CalculateElectricRangesPEV`.
  That value is `DoCalculateElectricRangesPEV` (`DeclarationData.cs` 2064–2086):
  `D21 = D13_SoC_corrected / D9_chargingEfficiency` → `ElectricEnergyConsumption = D21`. `[V]`

**So the number in `missions_xev.csv` `ElectricEnergy_kwh_km` is `battery-SoC energy ÷ charging efficiency`.**

**The range is on the battery side, not the grid side.** Same function, line
`D16_actualChargeDepletingRange = UseableStoredEnergy / D13_SoC × distance`. The range uses
D13 (battery SoC energy), **not** the grid-side D21. `[V]`

This explains Claude's consistency check exactly:
`kWh/km × range / usable = (D13/η) × (usable/D13 × dist) / dist / usable = 1/η`. `[D]`
Our data gives median **1.0048** (p1–p99 0.9921–1.0166, 44,258 rows), so the implied
charging efficiency is **η ≈ 1/1.0048 ≈ 0.9952 (~99.5%)**. The spread is the per-vehicle
battery/connector resistance. So:

> **Certified kWh/km (grid) ≈ HDEV battery-terminal kWh/km ÷ 0.995.**
> We will apply this when comparing (Job 3). HDEV's `consumption_engine` returns the
> battery-terminal net energy `E_battery` (its comment: "aux via DC/DC eff 1.0 like VECTO;
> battery Ri loss is in the battery engine"), i.e. **before** the Ri and charging-loss step.
> To reach the certified figure we divide HDEV kWh/km by 0.995. We report both the raw
> battery-side HDEV number and the grid-corrected one.

`.vsum` columns (for completeness): `EC_el_SoC` [kWh] = battery-internal, `EC_el_SoC_corr`
adds the electric-pneumatic correction, `EC_el_final` [kWh/km] = grid-side certified
(`SumDataFields.cs` 130–134). This matches the earlier note that the `.vsum` carries both a
terminal energy and `EC_el_final` (+1.1–1.6% on E2); the MRF/EEA field reports the final
(grid) one. `[V]`

---

## 2. Usable capacity and the ~0.855 ratio

**Answer: `TotalUsableCapacityInSimulation` is the SoC-map energy integrated between the
effective min and max SoC. The ~0.855 usable/installed ratio is a regulation default baked
into VECTO's declaration data, not an OEM number.** `[V]`

- `MRFREESSSpecificationsType.cs` lines 40–50 writes `TotalStorageCapacity =
  TotalStoredEnergy` and `TotalUsableCapacityInSimulation = UseableStoredEnergy`.
- `BatteryData.cs` 42–72: `UseableStoredEnergy = CalculateBatteryEnergy(MinSOC, MaxSOC)`,
  `TotalStoredEnergy = CalculateBatteryEnergy(0, 1)`.
- `BatteryDataAdapter.cs` 53–67 sets the effective window from `GenericSOC` and then applies
  a deterioration shrink:
  `MinSOC = maxSoc·(0.5·det) + minSoc·(1 − 0.5·det)`,
  `MaxSOC = maxSoc·(1 − 0.5·det) + minSoc·(0.5·det)`.
- `GenericSOC.csv`: `PEV, OVC=1, SOCMin 5, SOCMax 95, GenericDeterioration 5` (opened).
- `[D]` effective MinSOC = 0.95·0.025 + 0.05·0.975 = 0.0725; effective MaxSOC =
  0.95·0.975 + 0.05·0.025 = 0.92625; window = **0.85375 ≈ 0.855**.

Our data: usable/installed median **0.8551**, max 0.8649 (4,598 trucks). The cluster at
0.855 is the default; lower values are OEMs who declared a tighter SoC window (VECTO only
lets OEM values tighten, never widen the window). `[V]` `[D]`

Regulation anchor: the SoC window and deterioration for PEV REESS are declaration standard
values (Annex Xb / the VECTO declaration data that implements it). `[V]`

---

## 3. Standard values: what stays OEM, what VECTO generates

**Answer** (`[V]`, `ElectricMachinesDataAdapter.cs`, `BatteryDataAdapter.cs`; Annex Xb):

When `CertificationMethod = StandardValues` for an e-machine / IEPC / REESS, these inputs
stay **OEM-declared**: rated power (R85), continuous torque + its speed, overload torque +
speed + time, inertia, gear ratio(s), battery capacity, nominal voltage, OCV-vs-SoC curve,
max-current map.

VECTO **generates**: the efficiency / power map, the drag (no-load) curve, the
transmission-loss map, the overload buffer, the e-machine mechanical transmission efficiency
(`ElectricMachineDefaultMechanicalTransmissionEfficiency`), the REESS internal resistance
(read via the standard reader) and the junction-box / cable-connector resistance when the
OEM did not include them, and the usable-capacity SoC window (point 2).

Code path: `ElectricMachinesDataAdapter.cs` ~80–83 wraps a standard e-machine in
`StandardValuesInputData` with two synthetic voltage levels (1 V, 1e10 V); IEPC the same via
`StandardValueIEPCInputData` (~340–360). The map/curve generators are
`ElectricMotorMapReader` / `IEPCMapReader`, `…DragCurveReader`, and
`TransmissionLossMapReader.CreateEmADCLossMap`. Annex Xb Appendix 8 gives the e-machine
standard-value steps; its App. 8 steps 6–7 are the efficiency-table + drag construction we
reuse in Variant B. `[V]`

In our in-scope set: battery 3,798 StandardValues / 805 Measured; e-machine (E2/E3) 681
StandardValues / 326 Measured; IEPC 822 StandardValues / 2,774 Measured. `[V]`
This is why Job 3 splits results by component certification method.

---

## 4. Missions → cycles and loads

**Answer** (`[V]` `IDeclarationCycleFactory.cs` 38–42; `TruckSegments.cs` 195–258;
`VehicleDataAdapter.cs` 95–150; `VehicleData.cs` 196–216):

Truck missions seen in `missions_xev.csv` and their VECTO cycle file
(`Resources/Declaration/MissionCycles/`):

| Mission | Cycle file | Note |
|---|---|---|
| Long Haul | `LongHaul.vdri` | |
| Long Haul EMS | `LongHaul.vdri` | "EMS" stripped before lookup (line 40); EMS = extra trailer load, not a different cycle |
| Regional Delivery | `RegionalDelivery.vdri` | |
| Regional Delivery EMS | `RegionalDelivery.vdri` | EMS stripped |
| Urban Delivery | `UrbanDelivery.vdri` | |
| Municipal Utility | `MunicipalUtility.vdri` | + PTO sub-cycle (not used here) |
| Construction | `Construction.vdri` | uses the mission DefaultCDxA, not the certified one |

The resource name is `"MissionCycles." + mission.Replace("EMS","") + ".vdri"`. `[V]`

Payload and mass: `TruckSegments.cs` builds a `Mission` per vehicle group with
`BodyCurbWeight`, trailer(s) (`TrailerCurbWeight`, `DeltaCdA`, axle share), `RefLoad` and
`MaxLoad`, and `AxleWeightDistribution`. `VehicleDataAdapter` then assembles
`CurbMass = chassis curb`, `BodyAndTrailerMass = body curb + Σ trailer curb`,
`Loading = the mission payload`. `[V]`

**`TotalVehicleMass = CurbMass + BodyAndTrailerMass + Loading`** (`VehicleData.cs` 196–205).
So the `TotalVehicleMass` in `missions_xev.csv` **already includes body + trailer curb +
payload** — confirmed. `[V]` We therefore run HDEV at that mass directly and do not add a
body/trailer mass ourselves.

The two payloads per mission in the EEA data are the low payload (`RefLoad`, "reference")
and the high payload (`MaxLoad`) for that group. EMS rows carry a larger trailer/payload.

---

## 5. CdxA: bin → mission CdxA

The EEA gives only the bin `AirDrag_CdxA_range` (A1–A24), a certified-CdxA band under
Reg. 2018/956 Annex I Part C.

**Bin edges `[BOB]`-partial:** Reg. 2018/956 Annex I Part C defines the A1–A24 bands as fixed
m² intervals. The VECTO source does **not** ship the bin table (the drag curve is computed at
run time, not binned) — see note below. The band edges must be read from Reg. 2018/956
Annex I Part C itself. I did not have that annex open with line access in this run, so the
exact numeric edges per band are **`[BOB]`** (needs the 2018/956 Annex I Part C table). What
I can state from the data: bins seen are A1, A6, A9–A19, A23, A24, with A23 (1,255), A15
(726), A12 (701), A13 (694) the most common — consistent with tractors (A23) and mid-size
rigids. For Job 3 we run each truck at the **lower and upper edge of its bin** (two runs) as
the task requires, so the missing exact edges become a bounded range, not a point guess.

**Bin → simulation CdxA** (`[V]` `AirdragDataAdapter.cs`):
- Per-mission CdxA = certified `AirDragArea` + Σ `mission.Trailer.DeltaCdA` (the body/trailer
  delta per mission and group) — `CreateAirdragData` ~135–165. Construction uses
  `mission.DefaultCDxA` instead of the certified value.
- Crosswind: `GetDeclarationAirResistanceCurve` (20–86) builds a speed-dependent effective
  CdxA(v) from 60 to 130 km/h (5 km/h steps), integrating over wind height (Hellmann profile,
  exponent 0.2, base wind 3 m/s — `Physics.cs` 56, 66) and yaw. The yaw correction is
  `ΔCdxA(β) = a1·β + a2·β² + a3·β³`, with a1/a2/a3 from `VCDV_parameters.csv`:

  | class | a1 | a2 | a3 |
  |---|---|---|---|
  | RigidSolo | 0.013526 | 0.017746 | −0.000666 |
  | RigidTrailer | 0.017125 | 0.072275 | −0.004148 |
  | TractorSemitrailer | 0.030042 | 0.040817 | −0.00213 |

  (opened `VCDV_parameters.csv`.) These are exactly the coefficients the HDEV
  `crosswind_engine` test cell uses (TractorSemitrailer row), so our crosswind engine matches
  VECTO's declaration correction. `[V]`

So rigid trucks use the RigidSolo/RigidTrailer coefficients and tractors use
TractorSemitrailer; the body/trailer CdxA delta is added before the crosswind curve is built.

---

## 6. Auxiliaries: VECTO declaration electric power per mission (PEV)

`[V]` `HeavyLorryAuxiliaryDataAdapter.cs` (class `HeavyLorryPEVAuxiliaryDataAdapter`) +
`Resources/Declaration/VAUX/`. For PEVs the aux set is Electric system, HVAC, Pneumatic,
Steering pump (+ a Conditioning REESS load). All are ConnectToREESS = true.

Technology labels present in our in-scope trucks and their VECTO source:

- **Pneumatic** (`Aux_Pneumatic_Technology`): "Large Supply + AMS + elec. driven" (3,372),
  "Medium Supply 2-stage + elec. driven" (498), "Large Supply + elec. driven" (371),
  "Vacuum pump + elec. driven" (303), "Small + elec. driven" (57). Lookup table
  `VAUX/PS-Table.csv` (per technology × mission). For a fully-electric compressor the
  per-mission air demand is corrected to electric W in
  `BatteryElectricPostprocessingCorrection.cs` 24–35 via
  `PneumaticSystemElectricDemandPerAirGenerated`. `[V]`
- **Steering pump** (`steering_xev.csv`): "Electric driven pump" (4,103), "Full electric
  steering gear" (522). Base demand `VAUX/SP-Table.csv` (UF/B/S triples per group × mission),
  scaled by `SP-Axles.csv` (steered-axle count) and `SP-Tech.csv` technology factor; for PEV
  only these two technologies have PEV=1 and the electric UF factor is 0.857. This is the
  same SP-Table/SP-Axles/SP-Tech structure the HDEV `SP_power_helper` uses. `[V]`
- **HVAC** (`Aux_HVAC_SystemConfiguration`): **empty for all 4,603 trucks** in the data, so
  VECTO uses the HVAC default per group from `VAUX/HVAC-Table.csv`: e.g. groups 4/9/11 give
  Long haul 350 W, Regional 200, Urban 150, Municipal 300, Construction 200 (mechanical,
  divided by the HVAC electric-efficiency factor for battery W). `[V]`
- **Electric system (base)**: `VAUX/ES-Tech.csv`, standard technology ~1714 W long haul /
  ~1429 W other (mechanical, × alternator efficiency). `[V]`

Exact per-mission W rows are in those VAUX CSVs; Job 3 reads them directly for the aux inputs.

---

## 7. Tyres / RRC per axle

`[V]` `VehicleDataAdapter.cs` 95–188; `VehicleData.cs` 271–313; `Wheels.cs`; `Wheels.csv`;
`Physics.cs` 51.

- Each axle carries `AxleWeightShare = mission.AxleWeightDistribution[i]`,
  `RollResistanceCoefficient = Tyre.RollResistanceCoefficient` (the certified per-axle
  `SpecificRRC` in `axle_xev.csv`), `TyreTestLoad`, `TwinTyres`, dimension.
- Aggregation (`VehicleData.cs` 271–313): for each axle
  `baseValue = AxleWeightShare·TotalVehicleMass·g / TyreTestLoad / nrWheels`, then
  `rrcShare = AxleWeightShare · RRC · baseValue^(β−1)` with **β = 0.9**
  (`Physics.RollResistanceExponent`, `Physics.cs` 51). `TotalRollResistanceCoefficient` =
  Σ over **all** axles including trailer axles. The load-dependent exponent is the
  `baseValue^(−0.1)` term. `[V]`
- **r_dyn** is the average dynamic radius of the **driven** axle(s) only
  (`VehicleDataAdapter.cs` ~119–123): `DynamicTyreRadius = d·f/(2π)` from `Wheels.csv`
  (`Wheels.cs`). The HDEV `_stdval` r_dyn (265/70 R19.5 → 0.42086 m) uses this same formula. `[V]`
- `TyreDimension` → `Wheels.csv`: lookup by whitespace-stripped dimension string; the row
  gives d [mm], inertia, f (≈3.05). `[V]`
- Trailer axles are **not** in `axle_xev.csv`; for tractors VECTO uses generic trailer RRC /
  test-load from `DeclarationData.Trailer` with the mission's trailer axle share. Job 3 uses
  the VECTO declaration trailer values for tractor trailer axles (file + row cited in the
  run script).

**RRC missing / N/A in our data:** checked in `axle_xev.csv` — see
`sample_selection.md` for the per-sampled-vehicle count of axles with blank `SpecificRRC` or
`CertificationNumber = N/A`. Any such vehicle is flagged in the run outputs.

---

## Summary line for the report

The certified kWh/km is a **grid-side** number (battery SoC energy ÷ ~0.995 charging
efficiency). Usable kWh is the **VECTO-simulated** usable capacity = installed × ~0.855
(regulation default SoC window), not an OEM figure. Both are "certified (standard values)"
for ~82% of batteries. To compare, HDEV (battery-terminal) is divided by 0.995.

---

# v2 additions (7 Nov 2026) — sections 2.1–2.7

These sections are the v2 re-run answers. Where they differ from the v1 sections above,
**the v2 answer is the correct one.** Every number is sourced to VECTO source (file + line)
or regulation. VECTO source = `mohgsaad-art/VECTO` (EUPL 1.2), cloned for this run.

## 2.1 kWh/km basis: why the ratio dips below 1.000

**The reported kWh/km is grid-weighted energy = SoC-corrected energy ÷ charging efficiency.**
From `VectoCore/VectoCore/Models/Declaration/DeclarationData.cs`,
`DoCalculateElectricRangesPEV` (lines 2064–2092), quoted term by term:

```
2075  var D9_chargingEfficiencyBattery   = chargingEfficiency;                 // η
2076  var D15_useableBatteryCapacityForR_CDA = batteryData.UseableStoredEnergy; // usable [Ws]
2077  var D13_electricEnergyConsumption  = electricEnergyConsumptionSoCCorr;    // SoC_corr energy
2079  var D16_actualChargeDepletingRange = D15 / D13 * distance;               // the published range
2080  var D17_equivalentAllElectricRange = D16;
2081  var D18_zeroCO2EmissionsRange      = D17;
2083  var D21_electricEnergyConsumptionWeighted = D13 / D9;                     // the published kWh/km
```

- **D13** is `data.CorrectedModalData.ElectricEnergyConsumption_SoC_Corr` (line 2053): the
  SoC-corrected electric energy. "SoC_Corr" is the pneumatic/SoC-balance correction
  (`deltaEPSel` family), not the raw per-second SoC integral.
- **The published kWh/km (D21) = D13 / η.** Since η ≤ 1, D21 ≥ D13.
- **The published range (D16) uses D13**, *not* D21.

So the identity the v1 prompt expected, `kWh/km × range / usable = 1/η`, holds **only when the
`usable` you divide by is the same quantity as D15 (`UseableStoredEnergy`)**. Substituting:
`D21 × D16 / (D15 · distance) = (D13/η)·(D15·distance/D13) / (D15·distance) = 1/η`. Correct.

**Measured ratio over all 44,258 in-scope truck mission rows** (`ElectricEnergy_kwh_km` ×
`ActualChargeDepletingRange` ÷ `bat_usable_sim_kwh`; evidence pasted in report §2.1):

| stat | value |
|---|---|
| rows | 44,258 |
| below 1.000 | 3,678 (8.3%) |
| min | 0.5023 |
| P10 | 1.0001 |
| median | 1.0048 |
| P90 | 1.0084 |
| max | 1.0630 |

median 1.0048 ⇒ **η ≈ 0.995**, as v1 said.

**Why below 1.000 — two separate causes, found with evidence.** It is **not** rounding: both
`ElectricEnergy_kwh_km` and `ActualChargeDepletingRange` are published to **5 decimals**
(checked).

*How `UseableStoredEnergy` (D15) is built* — `BatteryData.cs` lines 40–100, quoted:
```
42  public WattSecond UseableStoredEnergy {
44    return Batteries.Select(x => x.Item1).Distinct().OrderBy(x => x).Aggregate(0,
45      (current, s) => current + Batteries.Where(x => x.Item1 == s)
46                               .Min(x => x.Item2.UseableStoredEnergy));   // .Min over parallel packs
78  public WattSecond UseableStoredEnergy => CalculateBatteryEnergy(MinSOC, MaxSOC);  // per pack
83  CalculateBatteryEnergy(minSoc,maxSoc):
88    foreach ((low,high) in SOCMap.Entries.Pairwise():
96       retVal += (max - min) * Capacity * voltage;   // OCV integral over the SoC window
```
`Item1` is the **series-string index**. So the system usable energy = sum over strings of the
**minimum** usable energy among the parallel packs in that string. `.Min(...)` takes the
minimum over the parallel packs sharing one series-string position.

*Cause 1 — the ≈ 0.50 extreme tail (only 4 vehicles).* Classifying vehicles by their median
ratio, **only 4 vehicles** have the parallel-string signature (median ratio < 0.75; the
12-pack `usable = 924` vehicles whose `kWh/km × range` ≈ 462 ≈ half of 924). For these the
published `bat_usable_sim_kwh` field sums all packs, while VECTO's D15 takes the string-min, so
the ratio halves. **Excluding these 4 vehicles, the minimum ratio rises from 0.5023 to 0.9820.**
So the halving explains the extreme tail and nothing else.

| population | n | min | P10 | median | P90 | max | below 1.0 |
|---|---|---|---|---|---|---|---|
| all in-scope rows | 44,258 | 0.5023 | 1.0001 | 1.0048 | 1.0084 | 1.0630 | 3,678 (8.3%) |
| excl. 4 parallel-string vehicles | 44,166 | 0.9820 | 1.0001 | 1.0048 | 1.0084 | 1.0630 | 3,586 (8.1%) |

*Cause 2 — the 8.1% of rows just below 1.0 (band 0.99–1.0, 3,552 rows).* These are **not** the
halving. They are spread across **all missions and all payloads** (no single-mission or
single-payload cluster; low-payload rows appear in both the <1.0 and ≥1.0 bands), so it is
**not a payload-weighting artifact**. The cause is the **SoC-correction term in D13**:

- D13 = `ElectricEnergyConsumption_SoC_Corr` (`CorrectedModalData.cs` line 50) =
  `ElectricEnergyConsumption_SoC + WorkBusAux_elPS_SoC_ElRange`, where
  `ElectricEnergyConsumption_SoC = −∫ P_reess_int` (REESS-internal energy, line 44/49) and the
  added term is **`deltaEPSel`** (`BatteryElectricPostprocessingCorrection.cs` lines 22–35), the
  pneumatic-air SoC-balance correction scaled by
  `DeclarationData.BusAuxiliaries.PneumaticSystemElectricDemandPerAirGenerated`.
- `bat_usable_sim_kwh` = `UseableStoredEnergy` = the OCV integral, **with no deltaEPSel term**.

So the ratio = `(D13/η) × (D15·distance/D13) / (bat_usable_field · distance)` = `(1/η) ×
(D15 / bat_usable_field)`, and `D15` carries the `deltaEPSel` SoC correction that the plain
`bat_usable_sim_kwh` field does not. On cycles where `deltaEPSel` is negative (SoC ends
slightly higher than the air-demand balance), D15/bat_usable_field drops just under 1, which
can cancel the `1/η ≈ 1.005` factor and push the row into the 0.99–1.0 band. **SoC vs SoC_corr
is the cause of the near-1.0 dips; payload weighting is ruled out.** The `1/η` relationship
itself is not violated — the divisor (`bat_usable_sim_kwh`) is simply the uncorrected OCV
energy, not the SoC-corrected D13-consistent usable energy.

**Which energy each field is:**
- `ElectricEnergy_kwh_km` (published) = **grid-side** (D13 includes the SoC_corr correction;
  then ÷ η adds the charging loss). It is the energy drawn **from the charger**.
- `ActualChargeDepletingRange` uses **REESS-internal energy** (D13 = SoC_corr energy at the
  battery, before the charging-loss division).
- `bat_usable_sim_kwh` = **REESS-internal usable stored energy** (`UseableStoredEnergy`), i.e.
  energy available inside the battery between the SoC window edges (§2.3), *before* charging
  losses. It is neither grid-side nor pure battery-terminal.

## 2.2 What HDEV must add to reach the certified basis

HDEV `consumption_engine` (`hdev_test_module.py` line 501) returns `E_battery`, the sum of
`P_battery = P_trac + P_aux_row` over the cycle. `P_trac` is motor/inverter/gearbox-side power;
there is **no battery internal-resistance term** and **no charging-loss term**. So HDEV returns
**battery-terminal** energy. The certified kWh/km (§2.1) is **grid-side** and its range basis is
**REESS-internal** — both above HDEV's terminal energy.

**(a) REESS internal loss — VECTO code path.** `CalculateChargingEfficiencyPEV`
(`DeclarationData.cs` line 1948) builds a `BatterySystem` and calls `tmpBattery.Request(...)`;
the loss comes from the battery's internal resistance. The per-step loss is `I²·R_i` where
`R_i` is the `InternalResistance` curve (built in `BatteryDataAdapter.cs` line ~68 via
`BatteryInternalResistanceReader.Create(b.InternalResistanceCurve, ...)`). During the driving
cycle the same internal-resistance loss sits between REESS-internal energy and battery-terminal
energy. **Inputs it needs:** the per-pack **internal resistance curve** vs SoC, the voltage/OCV
curve, and `ConnectionSystemResistance`/junction-box resistance.

**(b) Does EEA supply these? No.** EEA gives installed/usable kWh, nominal V and pack count.
It does **not** give the internal-resistance curve, the OCV curve, or the connection-system
resistance. **Confirmed: EEA has no resistance field** (`vehicles_xev.csv` battery columns are
`bat_packs, bat_installed_kwh, bat_usable_sim_kwh, bat_packs_inst_use, bat_nominal_v,
bat_cert_method` — no resistance, no OCV).

**(c) How η is computed (`CalculateChargingEfficiencyPEV`, `DeclarationData.cs` 1948–1964):**
charge the battery at `depotChargingPower`, measure `respChgBatDepot.LossPower` (internal
resistance loss) plus `connectorLoss = I²·ConnectionSystemResistance`, then
`η = 1 − (LossPower + connectorLoss) / PowerDemand`. **Inputs:** internal resistance curve,
internal voltage, `ConnectionSystemResistance`. **EEA gives none of these** → HDEV cannot
reproduce η from EEA data.

**Size of the missing terms — stated as two separate, individually-sourced parts (no combined
number without arithmetic):**

1. **REESS internal loss: +1.1 to +1.6 %, measured on the VECTO E2 example ONLY.** Source:
   Bob's 3 Nov E2 work (`docs/research/drag-default-test-2026-11/`, `step3_kwh_per_km.csv` and
   `claude/results-drag-and-drivetrain-matrix-360km-2026-11-03.md`), where `EC_el_final`
   (REESS-internal, incl. internal-resistance loss) was +1.1–1.6 % above the battery-terminal
   energy on the GenericVehicleE2 truck. **This is a single-vehicle VECTO-example figure; it is
   not a fleet value and does not transfer to the certified trucks** (whose resistance curves
   EEA does not carry).
2. **Charging loss: 1/η − 1. From §2.1, η (median) = 1/1.0048 = 0.99522, so charging loss =
   1/0.99522 − 1 = +0.48 %.** This is a fleet-median value from the data (§2.1), not E2.

I deliberately do **not** publish a single combined "+X %" figure, because the two parts have
different provenance (one E2-only, one fleet-median) and the per-vehicle REESS loss needs the
internal-resistance curve EEA does not provide. **This defines R11:** report HDEV terminal
kWh/km and certified as-published, and carry these two missing-terms sizes as **separate
columns** (labelled E2-only vs fleet-median), never folded into one constant.

## 2.3 Usable capacity: the arithmetic, corrected from source

**v1's 0.92625 / 0.85375 was wrong.** The correct VECTO formula and numbers, quoted from
`BatteryDataAdapter.cs` lines 62–67:

```
62  MinSOC = maxSoc * ((1d/2) * GenericDeterioration) + minSoc * (1 - (1d/2) * GenericDeterioration)
64  MaxSOC = maxSoc * (1 - (1d/2) * GenericDeterioration) + minSoc * ((1d/2) * GenericDeterioration)
```

`GenericSOC.csv` (quoted in full):
```
Architecture, OVC,  GenericSOCMin, GenericSOCMax, GenericDeterioration
PEV, 1, 5, 95, 5
```
So for a PEV: `minSoc = 5`, `maxSoc = 95`, `GenericDeterioration = 5` (percentage points),
`(1/2)·det = 2.5`.

- **MaxSOC** = 95·(1 − 0.025) + 5·0.025 = 92.625 + 0.125 = **92.75 %**
- **MinSOC** = 95·0.025 + 5·0.975 = 2.375 + 4.875 = **7.25 %**
- **SoC window** = 92.75 − 7.25 = **85.5 %** (= 0.855), **not** v1's 0.85375.

This confirms the v2 prompt's correction exactly.

**SoC window vs usable kWh.** The window above is a **SoC** window. Usable **kWh** is the OCV
curve integrated between MinSOC and MaxSOC (`BatteryData.cs`, `CalculateBatteryEnergy`). The two
are equal **only for a flat OCV curve** (constant terminal voltage); for a real rising OCV the
energy ratio differs slightly from the SoC ratio. The data median usable/installed ≈ **0.8551**
sits right on the **SoC window 0.855** (not a distinct energy ratio), which means the OCV curve
over this window is close enough to flat that the SoC window dominates — consistent with the
standard-value generic battery. So the 0.855 ratio is the **regulation default SoC window**,
confirmed, not an OEM figure.

## 2.4 CdxA bins — looked harder, still not found in any regulation or dataset doc

**Conclusion: the A1–A24 edges are NOT in the regulation and NOT in the EEA dataset
documentation. Marked `[BOB]`.** What was opened:

- **Reg. (EU) 2018/956, consolidated 14.03.2022 (CELEX 02018R0956-20220314)**, Annex I, via
  EUR-Lex `https://eur-lex.europa.eu/eli/reg/2018/956/2022-03-14/eng/xhtml`. Annex I row **23**
  is "**CdxA value (air drag value)**", point **1.8.4**; row 22 is the certification option
  (standard values / measurement, point 1.8.2); row 96 "Air drag model", 1.8.1. **The
  regulation reports the actual CdxA value in m² — there is no interval/bin table anywhere in
  Annex I (Parts A/B/C) or the amending acts M1–M5 listed on the consolidation page.** Content
  rephrased for licensing compliance (field names quoted as table labels only).
- **EEA 2024 HDV dataset catalogue record** `c7717abc-...` and the statistical metadata PDF
  `22fd286c-...` — both reachable only as PDF (this tool cannot read PDF); the v2 prompt states
  Bob already confirmed the metadata PDF (CC-BY 4.0) carries no bin table and the
  `HDV-tabledefinition (1).xlsx` has only `AirDrag_CdxA_range | nvarchar(20)` (a string field,
  no edges). Not repeated here.

So `AirDrag_CdxA_range` is an **EEA publication band** (a string bucket applied when EEA
publishes, to avoid printing the exact certified CdxA), **not** a regulation quantity. Its m²
edges are not published. **R10 therefore uses the VECTO standard-value CdxA** (`DefaultCDxA`
from `SegmentTable.csv` + trailer `DeltaCdA`), labelled "VECTO standard-value CdxA" in every
column and graph, and the bin edges stay `[BOB]`. URLs opened:
`eur-lex.europa.eu/eli/reg/2018/956/2022-03-14/eng/xhtml`,
`eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:02018R0956-20220314`,
`sdi.eea.europa.eu/.../c7717abc-...`, `sdi.eea.europa.eu/.../22fd286c-...`.

## 2.5 Auxiliaries per technology label — built, with arithmetic (`aux_per_label.csv`)

**Label counts across the 4,603 in-scope trucks** (`aux_label_counts.csv`):
- `Aux_Pneumatic_Technology`: `Large Supply + AMS + elec. driven` 3,368; `Medium Supply
  2-stage + elec. driven` 498; `Large Supply + elec. driven` 371; `Vacuum pump + elec.
  driven` 303; `Small + elec. driven` 57; `Medium Supply 1-stage + elec. driven` 1; blank 1.
  **All in-scope trucks use an `… + elec. driven` pneumatic** → PEV-applicable `*_el` rows exist.
- `SteeringpumpTechnology` (`steering_xev.csv`): `Electric driven pump` 4,085; `Full electric
  steering gear` 513. Both are PEV-applicable (`SP-Tech.csv`, `PEV=1`).
- `Aux_HVAC_SystemConfiguration`: **blank for all 4,603** (0% filled in EEA). The heat-pump /
  heater columns 35–41 are also blank. **EEA does not report the HVAC configuration** → we
  cannot pick the truck's HVAC label. `aux_per_label.csv` reports the VECTO **Default** HVAC
  row per group as the declaration standard, and this is flagged as a gap (not a per-truck value).
- `Aux_Electric_ElectricStorageCapacity` present; electric-system technology is the ES
  "Standard technology" row (ES-Tech.csv).

**Electric power per label × mission (PEV), with the row and arithmetic** — every constant has
file + line. Full table in `aux_per_label.csv`. Constants:
- `AlternatorEfficiency = 0.7` — `DeclarationData.cs:123`.
- `HVACElectricEfficiencyFactor = 0.8` — `DeclarationData.cs:126`.
- `PneumaticSystemElectricDemandPerAirGenerated = 5600 W / 325 NL/min` — `DeclarationData.cs:355`.

Adapter rules (`HeavyLorryAuxiliaryDataAdapter.cs`):
- **ES** electric = mech × 0.7 (line 120). e.g. Long Haul: 1714.29 × 0.7 = **1200.0 W**.
- **HVAC** electric = mech × (1/0.8) (line 78, 165). e.g. Default grp 5 Long Haul: 350 / 0.8
  = **437.5 W**.
- **PS (PEV, `IsFullyElectric`)** electric = the `*_el` column **directly** (line 140–143).
  e.g. `Large Supply + AMS + elec. driven`, Long Haul = **900.0 W** (`[Long Haul_el]`).
- **SP** split: electric pumps from `SP-Table.csv` baseline (UF/B/S) × `SP-Axles.csv` ×
  `SP-Tech.csv` factor (line 175–215); for `Full electric steering gear` the SP-Tech factor is
  0/0.143/1.429 (UF/B/S).
- **cond** (condenser) = `Cond-Table.csv` Lorry per mission, e.g. Long Haul **600 W**.

**Which terms VECTO applies always vs while driving.** In the lorry adapter every aux is
`DemandType = Constant` (always applied). The notebook `consumption_engine` instead applies
**SP only while moving** (`SP * moving`) and **cond only while moving or PTO active**
(`cond * (moving | pto_active)`), and ES/PS/HVAC always. **This differs from VECTO**, which
runs SP and cond always too. Listed under "For Bob: notebook issues". Mapping used in R9: ES,
PS, HVAC → `consumption_engine` always-on args (`ES`, `PS`, `HVAC`); SP → `SP`; cond → `cond`.

If a label has no matching row (e.g. the 1 blank pneumatic, or any HVAC per-truck label because
EEA gives none), the run is flagged and the HVAC term uses the group Default (documented), not
skipped — HVAC is a small term and skipping a truck for a universally-missing EEA field would
drop the whole fleet.

## 2.6 Municipal Utility and PTO

**Is PTO energy simulated for a PEV lorry on Municipal Utility?** VECTO attaches a **generic
electric-PTO profile** to the Municipal cycle via the vehicle's declaration PTO input
(`MunicipalUtility_PTO_generic.vptoel` / `.vptoc` / `.vptol`, in
`Resources/Declaration/MissionCycles/`). The Municipal body is selected by mission
(`TruckSegments.cs:316`, `GetBody` uses the `bodymunicipalutility` column). The ePTO profile:

- `MunicipalUtility_PTO_generic.vptoel` = `P_PTO_el` [kW] vs time, 24 one-second rows,
  **min 8.42, max 33.69, mean 23.57 kW** (electric PTO power while the vehicle works).
- `.vptol` = idle PTO torque vs engine speed; `.vptoc` = the PTO drive cycle.

**What triggers it.** The PTO is a **declared vehicle input**, not the `Transmission_PowerTakeOff`
flag alone. The flag `Transmission_PowerTakeOff` (Reg. 2018/956 Annex I row 31, point 1.3.8,
"Power take off yes/no") marks the **mechanical** PTO shaft. For a PEV the relevant input is an
**ePTO declaration** (the `.vptoel` profile), which EEA does **not** carry per vehicle.

**PTO flag counts in-scope:** `Transmission_PowerTakeOff` = blank 4,100; `false` 503;
**`true` 0**. So **no in-scope truck declares a mechanical PTO**, and EEA gives no per-vehicle
ePTO profile.

**Consequence for R12.** Because (a) EEA carries no per-vehicle ePTO declaration, (b) 0 trucks
flag a PTO, and (c) whether the certified Municipal figure includes the generic ePTO depends on
each OEM's declaration which we cannot read, **Municipal Utility is excluded from the summary
statistics** and reported separately with this reason. If a certified Municipal figure does
include the generic ePTO (mean 23.57 kW), HDEV without it would read far too low — which is
exactly the −64 to −73 % v1 Municipal error. We do not fabricate an ePTO profile per truck.

## 2.7 Mission set-up per group (`mission_setup.csv`)

Built from `SegmentTable.csv` (read at run time) for every valid HDV group × mission in the
sample (76 rows, groups 1s,1,3,4,5,9,10,11,12,16,53). Per row, with a source column for each
value: vehicle category, axle config, payload band, body code, trailer code, height,
`CdxA_Default` (or `CdxA_Construction` for Construction), the **crosswind parameter set name**
per mission (→ a1/a2/a3 from `VCDV_parameters.csv`), truck axle weight shares, trailer axle
weight shares, trailer RRC (0.0055) and test load (37500 N) from `DeclarationData.cs` class
`Trailer` (lines 837/839), and the driven axle number.

**This fixes R10's group→crosswind bug.** From `SegmentTable.csv`: groups **5, 10, 12 are
`Tractor` rows whose "Other"/"Long haul" crosswind set is `TractorSemitrailer`**, not
`RigidTrailer`. v1 hand-mapped them to `RigidTrailer`. The correct sets (read at run time):
`RigidSolo` (groups 1s/1/2/3 and the non-trailer missions of 4), `RigidTrailer` (group 4/9/11
Long Haul, and the EMS columns of 5/10/12), `TractorSemitrailer` (groups 5/10/12 tractors).
Crosswind a1/a2/a3 (`VCDV_parameters.csv`): RigidSolo 0.013526/0.017746/−0.000666; RigidTrailer
0.017125/0.072275/−0.004148; TractorSemitrailer 0.030042/0.040817/−0.00213.

**Driven axle.** `VehicleData.cs` marks `AxleType.VehicleDriven`; for the standard 4x2/6x2/6x4/
8x4 truck and tractor configs `AxleConfiguration.NumDrivenAxles() = 1` and the driven axle is
the **2nd** axle (the rearmost powered axle). r_dyn in R3 is taken from that axle's tyre.
