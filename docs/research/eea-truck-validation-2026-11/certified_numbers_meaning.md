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
