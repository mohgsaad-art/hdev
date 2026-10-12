# 07 — PTO (all types, formats, idle losses, driving vs stops, BEV electric PTO)

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**.

---

## 1. PTO file formats  [VECTO]
Three PTO file types (default generic set in `Resources/Declaration/MissionCycles/MunicipalUtility_PTO_generic.*`):

| ext | meaning | columns | unit |
|---|---|---|---|
| **`.vptol`** | **PTO idle loss map** (mechanical) | `<Engine speed> [rpm]`, `<PTO Torque> [Nm]` | rpm, **Nm** |
| **`.vptoc`** | **PTO (activation) cycle** — mechanical PTO duty during the cycle | cycle rows | — |
| **`.vptoel`** | **electric PTO idle/activation cycle** (BEV) | `<t>`, `<P_PTO_el>` | s, **kW** |

Example `.vptol` (`MunicipalUtility_PTO_generic.vptol`): engine-speed → PTO drag torque (idle loss while PTO engaged but not doing work):
```
<Engine speed> [rpm], <PTO Torque> [Nm]
400,5.4
600,8.0
800,11.4
1000,15.5
```
[VECTO] Read by `PTOIdleLossMapReader.cs` (2 cols: Engine Speed, PTO Torque). [VECTO]

Example `.vptoel` (`EPTO-idle.vptoel`, generic BEV): time → electric PTO power:
```
<t> ,<P_PTO_el>
0 , 8.42
5 , 33.69
9 , 25.92
...
```
[VECTO] file content.

Declaration defaults (`DeclarationData.cs:1790-1795`): `DefaultPTOIdleLossMap = …MunicipalUtility_PTO_generic.vptol`, `DefaultPTOCycle = …vptoc`, `DefaultE_PTOActivationCycle = …vptoel`.

---

## 2. The `P_PTO_el` unit — docs say Nm, VECTO says **kW**  [VECTO]
The `.vptoel` column `<P_PTO_el>` is parsed as **kW → Watt**:
```csharp
PTOElectricalPowerDemand = (row.ParseDouble(Fields.PTOElectricalPowerDemand) * 1000).SI<Watt>(),   // ×1000 ⇒ input is kW
```
[VECTO] `DrivingCycleDataReader.cs:845` (`Fields.PTOElectricalPowerDemand = "P_PTO_el"`, line 343). So `8.42` means **8.42 kW = 8420 W** of electrical power — **not Nm**. **The HDEV docs' note that "docs say Nm, likely an error" is confirmed: it is electrical power in kW.** [VECTO]

---

## 3. PTO idle losses (PTO-tech.csv)  [VECTO]
`Resources/Declaration/VAUX/PTO-tech.csv` — mechanical PTO transmission losses by PTO technology (`Power Loss` [W], `Torque Loss` [Nm]):
```
Technology , Power Loss, Torque Loss
None                                                                 , 0    , 0
only one engaged gearwheel above oil level                           , 0    , 0
drive shaft of PTO - shift claw/synchronizer/sliding gearwheel       , 50   , 0.4
drive shaft of PTO - multi-disc clutch                               , 350  , 2.8
drive shaft of PTO - multi-disc clutch, oil pump                     , 3000 , 23.9
drive shaft and/or up to 2 gear wheels - ...                         , 150–3050 , 1.2–24.3
drive shaft and/or >2 gear wheels - ...                              , 200–3100 , 1.6–24.7
PTO with 1+ additional gearmesh(es), no disconnect clutch            , 1500 , 11.9
```
[VECTO] full file. These are the **constant idle losses** of the PTO drivetrain when engaged (the oil-pump variants are large: 3000 W). [VECTO]

---

## 4. PTO during driving vs during stops  [VECTO]
- **Electric PTO (BEV)**: `EPTO.cs` — `PowerDemand = ptoCycleController.CycleData.LeftSample.PTOElectricalPowerDemand`. It is an **IAuxDemand** consumer (`AuxID = PTOConsumer`), i.e. the PTO power is added to the aux draw from the battery, driven by the `.vptoel` time profile. `EPTOOn = PowerDemand != 0`. [VECTO] `EPTO.cs`.
- **Mechanical PTO**: `PTOCycleController.cs` + `PTODriveAuxiliary.cs` + `PEVPTO.cs` — the PTO activation cycle (`.vptoc`) runs during the stop/activation phase; idle losses (`.vptol`) apply when engaged. [VECTO]
- The MunicipalUtility mission interleaves driving with PTO-active **stops** (refuse collection). The electric PTO activation cycle (`.vptoel`) plays out in time at each stop. [INFERRED from the generic file being named `MunicipalUtility_PTO_generic`.]

**The deferred HDEV gap (M0.10, +~23 s/stop PTO stop-time):** the PTO activation cycle adds time at each stop that HDEV currently does not model. The `.vptoel`/`.vptoc` cycles are the VECTO source for that stop-time. [VECTO] ties to M0.10.

---

## 5. Which missions / vehicle types use PTO  [VECTO]
- **MunicipalUtility** (refuse) is the PTO mission (default PTO files are `MunicipalUtility_PTO_generic.*`). Construction tipper bodies may also use PTO. [VECTO] `DeclarationData.cs`, `Body_Trailers_Weights.csv` (MU/BT bodies).
- Vehicle types: lorries with refuse/tipper bodies. The generic BEV job `PEV/GenericVehicleE2/BEV_E2_PTO.vecto` + `EPTO-idle.vptoel` is the BEV PTO example. [VECTO]

---

## 6. How VECTO computes PTO energy for a BEV  [VECTO]
Electric PTO power (kW from `.vptoel`) is drawn **directly from the battery** as an aux consumer (`EPTO : IAuxDemand`, `AuxID = PTOConsumer`), summed into `P_aux_el` alongside the five standard aux (06 §1). The energy is `∫ P_PTO_el dt` over the activation cycle. No efficiency chain is applied beyond the battery (DC/DC = 1.0). [VECTO] `EPTO.cs`, `ElectricAuxiliaries.cs`.

For the **Conditioning** term (06 §1), an active electric PTO (`EPTOOn`) also keeps `Cond` on even if the EM is off. [VECTO] `Conditioning.cs:GetPEV_SHEV_PowerDemand`.

---

## 7. What HDEV needs
1. Parse `.vptoel` as **time [s] → P_PTO_el [kW→W]**; add to the battery aux draw during PTO-active stops.
2. (If modelling mechanical PTO) `.vptol` idle loss (rpm→Nm) and `.vptoc` activation cycle.
3. PTO-tech idle losses from `PTO-tech.csv` (0–3100 W) if a specific PTO technology is modelled.
4. Model (or explicitly defer + flag) the PTO stop-time added per stop (M0.10, +~23 s/stop).
5. Keep electric PTO energy = ∫P_PTO_el dt from the battery (DC/DC=1.0).

---

## 8. Open questions
- Exact stop-time the `.vptoel`/`.vptoc` cycles add per MunicipalUtility stop (needs reading the full `.vptoc` / mission cycle). The ~23 s/stop figure is from the HDEV docs; confirm against the generic PTO cycle length.
- Does the HDEV target include refuse (MU) BEVs at all, or is PTO out of initial scope? (M0.10 defers it.)

---

## 9. Unblocks spec task(s)
- **M0.10 (PTO stop-time gap, deferred)** — the `.vptoel`/`.vptoc` activation cycles are the VECTO source for the +~23 s/stop stop-time; gives the gap wording a citation.
- **M0.15 (p_aux)** — electric PTO is an aux consumer (`PTOConsumer`) drawn from the battery; `P_PTO_el` unit confirmed **kW** (not Nm).
- **M0.16 (Cond toggle)** — `EPTOOn` keeps Conditioning on even with EM off.
- Corrects the docs' `P_PTO_el` unit ambiguity → it is kW electrical power (`DrivingCycleDataReader.cs:845`).
