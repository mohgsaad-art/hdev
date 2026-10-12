# 09 — Vehicle data & defaults (SegmentTable, Payloads, weights, wheels, RRC, IMC, CdxA, weighting)

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**.

> The HDEV `reference/` bundle has small/old copies of some of these CSVs. The authoritative versions are the embedded resources under `VectoCore/VectoCore/Resources/Declaration/` in the clone — cite those.

---

## 1. SegmentTable.csv — vehicle group classification + defaults [VECTO]
`VectoCore/VectoCore/Resources/Declaration/SegmentTable.csv`, loaded by `TruckSegments.cs`.
- Column 1: `HDV group`. Columns 20–27: truck/trailer axle configs per mission (long-haul / other / EMS).
- **Column 40: `CdxA_Default` [m²]**, **Column 41: `CdxA_Construction` [m²]** — the air-drag standard values per group.
  - Group **5** (4×2 tractor, the main BEV lorry target): `CdxA_Default = 8.7`, `CdxA_Construction = 7.2` [m²]. [VECTO] `SegmentTable.csv` Group 5 rows.
- Read by `TruckSegments.ReadDefaultAirDragValue(row, missionType)`: uses `cdxa_construction` for Construction missions, else `cdxa_default`; empty cell → `null`. [VECTO] `TruckSegments.cs:ReadDefaultAirDragValue`.

**req §5.7 (CdxA defaults, Annex VIII extract missing):** The CdxA standard values **can be cited from VECTO code/resource** — `SegmentTable.csv` column `CdxA_Default` (e.g. Group 5 = 8.7 m²) — instead of the missing Annex VIII extract. The resource file is authoritative and in-repo. [VECTO] This resolves the §5.7 block *for the value*, though the regulation *text* is still absent (name it "Annex VIII air-drag standard values — regulation extract missing; value sourced from `SegmentTable.csv`").

---

## 2. Payloads.csv — reference payloads + interpolation [VECTO]
`.../Resources/Declaration/Payloads.csv`, class `Payloads.cs`.
Columns: `Gross Vehicle Weight, Payload 10%, Payload 50%, Payload 75%` (all kg).
```
Gross Vehicle Weight , Payload 10% , Payload 50% , Payload 75%
3500   , 80   , 420  , 630
7400   , 240  , 1210 , 1840
7500   , 250  , 1250 , 1900
16000  , 920  , 4600 , 6900
```
(This is the full embedded resource — note the HDEV `reference/vecto/resources/Payloads.csv` may differ; cite the clone resource.)

**Interpolation method [VECTO]** (`Payloads.cs:Lookup10/50/75Percent`): **linear interpolation in GVW** between the two bracketing table rows:
```csharp
section = Data.GetSection(d => d.Key < grossVehicleWeight);
return VectoMath.Interpolate(section.Item1.Key, section.Item2.Key,
    section.Item1.Value.PayloadXPercent, section.Item2.Value.PayloadXPercent, grossVehicleWeight);
```
Payload-string → column mapping (`DeclarationData.GetPayloadForGrossVehicleWeight`): `"pc10*"→10%`, `"pc75*"→75%`, else `50%`. [VECTO] `DeclarationData.cs:159-168`.

**Trailer payload [VECTO]**: `LookupTrailer = 0.75·(GVW − curb)`; for low loading divided by 7.5, rounded to nearest 100 kg, clamped to `[0, GVW−curb]`. [VECTO] `Payloads.cs:LookupTrailer`, `DeclarationData.cs:GetPayloadForTrailerWeight`.

---

## 3. Payload / GVW caps (task M0.20) [VECTO]
The payload is **clamped to the remaining mass budget**:
```csharp
var vehiclePayload = DeclarationData.GetPayloadForGrossVehicleWeight(grossVehicleWeight, payloadStr)
    .LimitTo(0.SI<Kilogram>(), grossVehicleWeight - vehicleWeight);   // vehicleWeight = curb + body (+trailer curb)
```
[VECTO] `TruckSegments.cs:GetLoading`. So the **cap = GVW − (vehicle curb + body curb + trailer curb)**. There is no separate hard-coded 40 t / 60 t literal in this path; the EMS 40 t/60 t limits come from the **trailer/combination GVW** rows in `Body_Trailers_Weights.csv` (e.g. ST1 remark: "fully loaded is GVM of tractor semitrailer combination = 40000 kg"). [VECTO] `Body_Trailers_Weights.csv`.

**M0.20:** HDEV `mass.py` should assemble `m = vehicle + body + payload` and cap payload at `GVW − (vehicle+body+trailer curb)`, citing `SegmentTable.csv` (GVW), `Body_Trailers_Weights.csv` (curb/max-gross), and the `LimitTo` in `TruckSegments.cs:GetLoading`.

---

## 4. Body_Trailers_Weights.csv — body & trailer masses [VECTO]
`.../Resources/Declaration/Body_Trailers_Weights.csv`. Columns: `name, curb mass [kg], max gross mass [kg], delta CdxA for trailer operation in long haul [m²] (first/second trailer EMS), Axle count, Wheels, cargo volume [m³], remark`.
Examples: `B1` curb 1600 kg; `T1` trailer curb 3400, max gross 10500, ΔCdxA 1.3, 235/75 R17.5; `ST1` semitrailer curb 7500, max gross 24000, ΔCdxA 0/2.1, 385/65 R22.5 (combination 40 t); `MU4/MU9` municipal bodies 6000/6750 kg; `BT1–3` construction tipper bodies. [VECTO] file content.

The `delta CdxA for trailer operation` feeds the long-haul air-drag increment (first/second trailer for EMS). [VECTO]

---

## 5. Wheels.csv — dynamic radius, inertia, RRC factor [VECTO]
`.../Resources/Declaration/Wheels.csv`. Columns: `Wheel, cross-sectional width [mm], tire aspect ratio [%], rim diameter [inch], d [mm] (dynamic rolling diameter), Inertia, F [-], comment`.
Example: `315/70 R22.5`-class entries; `d [mm]` is the dynamic rolling **diameter** (dynamic radius = d/2); `Inertia` [kg·m²]; `F` factor = **3.05** for all heavy tyres. [VECTO] file head.
- Dynamic radius used by `Wheels`/`WheelEnd` to convert torque↔force; inertia adds to rotating mass. [INFERRED from column semantics; `Wheels.cs` consumes `WheelsData`.]

---

## 6. Rolling resistance — load dependence [VECTO]
Force (`Vehicle.cs:RollingResistance`):
```
F_roll = cos(gradient) · m · g · rrc_total
```
`rrc_total` is **load-dependent per axle** (`VehicleData.cs` ~lines 290–310):
```csharp
baseValue = AxleWeightShare · TotalVehicleMass · g / TyreTestLoad / nrWheels;
rrcShare  = AxleWeightShare · RollResistanceCoefficient · Math.Pow(baseValue, RollResistanceExponent − 1);
rrc_total = Σ rrcShare   (over axles)
```
with **`RollResistanceExponent = 0.9`** (`Utils/Physics.cs:51`). So RRC rises mildly as axle load drops below the tyre test load (standard tyre load-sensitivity exponent 0.9). `TyreTestLoad` per axle (trailer default `37500`, `DeclarationData.cs:Trailer.TyreTestLoad`; trailer RRC default `0.0055`). [VECTO] `VehicleData.cs`, `Physics.cs`, `DeclarationData.cs:Trailer`.

**req note (single-Crr gap):** HDEV's "single Crr, rotating mass off" is a simplification of this per-axle, load-dependent RRC. VECTO citation: `VehicleData.cs` RRC loop + `RollResistanceExponent=0.9`.

---

## 7. IMC-Tech.csv / DeltaAirDragAreaIMC (task M0.18) [VECTO]
`.../Resources/Declaration/IMC-Tech.csv`, class `IMCTechnologyLookup.cs`.
```
Technology         , heavy lorries , heavy buses , medium lorries , deltaCdxA
OverheadPantograph , 1 , 1 , 0 , 0.6
OverheadTrolley    , 0 , 1 , 0 , 0.0
GroundRail         , 1 , 1 , 1 , 0.0
Wireless           , 1 , 1 , 1 , 0.0
None               , 1 , 1 , 1 , 0.0
```
- Columns = allowed-flag per vehicle type + `deltaCdxA` [m²]. Only **OverheadPantograph** adds air drag (**0.6 m²**); all others 0. [VECTO] file content, `IMCTechnologyLookup.ParseData`.
- **How applied** (`AirdragDataAdapter.cs:DeltaCdxAIMC`): `deltaCdxAIMC = deltaCdxA · shareImcAvailable` where `shareImcAvailable = GetShareIMCInfrastructure(technology, vehicleOperation)` — a mission/operation-dependent fraction of the route with IMC infrastructure. Returns 0 for conventional (`ArchitectureID.UNKNOWN`) and for hybrids not in charge-depleting mode. [VECTO] `AirdragDataAdapter.cs:149-176`.
- The `DeltaAirDragAreaIMC` input field exists on the airdrag input (`JSONSubComponent.cs`) for engineering mode.

**M0.18 decision support:**
- **Default 0** is correct for a BEV lorry that is **not** overhead-pantograph (all other technologies and `None` → 0 m²).
- If grounding from `IMC-Tech.csv`: only `OverheadPantograph` → **+0.6 m²**, further scaled by the infrastructure-availability share (mission-dependent). For a generic non-IMC BEV lorry, default **0** matches VECTO; expose the argument to ground 0.6 m² for pantograph vehicles. Cite `IMC-Tech.csv` + `AirdragDataAdapter.cs:DeltaCdxAIMC`.

---

## 8. Mission / payload weighting factors (combining Low/Reference) [VECTO]
`.../Resources/Declaration/CO2Standards/MissionProfileWeights.csv`, class `WeightingFactors.cs`.
- Keyed by **WeightingGroup** (e.g. `5-LH`, `5-RD`, `9-LH`, medium `51/52`…). Each mission column holds **`low/reference`** weights (the two loadings VECTO weights over: `LowLoading`, `ReferenceLoad`).
- Example Group **5-LH**: LongHaul `0.27/0.63`, RegionalDelivery `0.03/0.07`, Construction `0.5/0.5` → sum = 2.0 (vocational). Group 5-RD: LongHaul `0.03/0.07`, RegionalDelivery `0.27/0.63`, Construction `0.5/0.5`.
- Weights must sum to **1.0** (non-vocational) or **2.0** (vocational, incl. construction) or VECTO throws. [VECTO] `WeightingFactors.cs:ParseData` (`VocationalFactorsSum=2.0`, `NonVocationalFactorsSum=1.0`).
- Final declared result = Σ over (mission, loading) of weight · result(mission, loading). Only **two payload levels** (low, reference) per mission — not 10/50/75%. [VECTO]

**For HDEV:** the two-payload (low + reference) weighting with per-group factors is how VECTO produces a single CO₂/energy number. HDEV's single-reference-payload runs are a subset; adopting the weighting needs `MissionProfileWeights.csv` + the vehicle's weighting group.

---

## 9. What HDEV needs to replicate
1. GVW/axle config/CdxA default from `SegmentTable.csv` (Group 5 CdxA 8.7 m²).
2. Reference payload = linear-in-GVW interp of `Payloads.csv` (10/50/75%); trailer payload = 0.75·(GVW−curb).
3. Mass assembly + payload cap at `GVW − (curb+body+trailer curb)` (M0.20).
4. Body/trailer curb & ΔCdxA from `Body_Trailers_Weights.csv`.
5. Wheel dynamic radius + inertia from `Wheels.csv` (if modelling rotating mass; currently off → flag).
6. (If improving beyond single-Crr) per-axle load-dependent RRC with exponent 0.9.
7. IMC ΔCdxA: default 0; 0.6 m² only for OverheadPantograph × infrastructure share (M0.18).
8. (If adopting weighting) two-payload mission weighting from `MissionProfileWeights.csv`.

---

## 10. Open questions
- Which exact weighting group does the HDEV target BEV lorry fall in (5-LH vs 5-RD)? Depends on body/axle config.
- Does HDEV want the per-axle load-dependent RRC or keep single-Crr (currently flagged)? The exponent 0.9 and per-axle shares are available if wanted.
- `shareImcAvailable` values come from `GetShareIMCInfrastructure` + a VehicleOperation lookup — not fully traced here; only needed if modelling pantograph BEVs.

---

## 11. Unblocks spec task(s)
- **M0.20** — mass assembly + payload cap formula with exact VECTO citation (`TruckSegments.cs:GetLoading` LimitTo, `SegmentTable.csv`, `Body_Trailers_Weights.csv`).
- **M0.18** — `DeltaAirDragAreaIMC` default 0 is VECTO-correct for non-pantograph BEVs; 0.6 m² for pantograph × infra share (`IMC-Tech.csv`, `AirdragDataAdapter.cs`).
- **req §5.7 / M1.1** — CdxA default values can be cited from `SegmentTable.csv` (`CdxA_Default`, Group 5 = 8.7 m²) instead of the missing Annex VIII extract. Unblocks the 🔒 on `defaults.py` CdxA defaults (value available; regulation text still flagged missing).
- **M1.1 / M1.2** — Payloads interpolation, RRC (0.9 exponent, single-Crr neutral), body/trailer weights all transcribable with citations.
- **M2.8 (mission weighting)** — two-payload low/reference weighting source + sum rules.
