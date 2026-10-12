# 11 — Validation data (generic BEV jobs, unit-test numeric anchors, headless run attempt)

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**. Serves **task M5.3**.

---

## 1. Generic / example BEV lorry jobs (full input sets)  [VECTO]

Complete, runnable BEV lorry declaration jobs shipped in the repo (`Generic Vehicles/`):

**Declaration mode:**
- `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/` — a complete Group-5 BEV lorry (E2 position). Variants: `BEV_E2.vecto`, `BEV_E2_Cont30kW.vecto`, `BEV_E2_PTO.vecto`. Components: 125 kW / 485 Nm EM (`GenericEMotor_125kW_485Nm.vem` + `.vemp` fld + `.vemo` map + `.vemd` drag), 243 kWh / 750 V battery (`GenericBattery_243kWh_750V.vbat` + `.vbatr` Ri + `.vbatv` OCV), AMT (`AMT.vgbx`), `Truck.vacc`, `xEV` aux.
- `Generic Vehicles/Declaration Mode/PEV/GenericIEPC/` — IEPC BEV variants (`IEPC__Gbx1Whl2`, `IEPC__Gbx3Axl`, `IEPC__Gbx3Whl2`, `IEPC__Gbx3_drag`).
- `Generic Vehicles/Declaration Mode/xEV XML Jobs/Lorries/` — XML-format BEV lorry jobs: `Group5_ PEV_E4.xml`, `Group5_ PEV_IEPC_E.xml`, `Group5_ PEV_IEPC_E_stdValues_v2.6.xml` (**standard-values** EM example), `Group5_ PEV_IEPC_E_multiCurve.xml`, `PEV_heavyLorry_AMT_E2.xml`.
- `Generic Vehicles/Declaration Mode/IMC_BEV_E2_Group5_2030/` — in-motion-charging BEV (`BEV_Group5_IMC.vecto`).
- `Generic Vehicles/Declaration Mode/MultiplePowertrains/Multiple_PEV_E3_E3_HeavyLorry.xml` etc.

**Engineering mode:**
- `Generic Vehicles/Engineering Mode/GenericVehicleE2/BEV_ENG.vecto` (+ `_Cont30kW`, `_PTO`, `_timeruns`), and `GenericVehicleE4/BEV_ENG.vecto`.

These are the **input anchors** for M5.3: once HDEV can run VECTO (on a machine with NuGet/network), these produce the reference per-mission kWh/km. **In this sandbox they cannot be executed** (see §3).

---

## 2. Unit / integration tests with concrete numeric expected results  [VECTO]

These are **directly usable as HDEV component-level validation** — exact inputs + exact expected outputs, no full VECTO run needed. HDEV can reproduce the component (OCV+Ri battery, EM map) and assert the same numbers.

### 2.1 Battery (`VectoCore/VectoCoreTest/Models/SimulationComponent/BatteryTest.cs`)
Component file: `TestData/Hybrids/Battery/GenericBattery.vbat` (initial SoC 0.8 in the DAO call).

**Usable energy** `BatteryUseableEnergyTest(minSoc, maxSoc, expected kWh)` — asserts `UseableStoredEnergy` to 1e-6 kWh:
| minSoC | maxSoC | expected kWh |
|---|---|---|
| 0.2 | 0.8 | 2.8725 |
| 0.25 | 0.75 | 2.395125 |
| 0.42 | 0.64 | 1.05564 |

**One-step SoC** `BatteryRequestTest(initialSoC, dt[s], powerDemand[W], expectedSoC)` — asserts resulting SoC to 1e-9 (sign: negative power = discharge lowers SoC, positive raises):
| initSoC | dt | P [W] | expected SoC |
|---|---|---|---|
| 0.5 | 0.5 | −500 | 0.499985523 |
| 0.5 | 1 | −14000 | 0.499175514 |
| 0.5 | 1 | 7000 | 0.5004016980 |
| 0.35 | 0.5 | −200 | 0.349994175 |
| 0.35 | 0.5 | −16000 | 0.3495245545 |
| 0.75 | 0.5 | −300 | 0.7499913702 |
| 0.75 | 0.5 | −14500 | 0.7495755113 |

**Overload / loss** `BatteryOverloadTestNoAux(initSoC, dt, P, maxDischarge[W], loss[W])` — asserts `MaxDischargePower` and `LossPower = I²·Ri` to 1e-2, returns `RESSUnderloadResponse`:
| initSoC | dt | P [W] | maxDischarge [W] | loss [W] |
|---|---|---|---|---|
| 0.5 | 0.5 | −500000 | −169875 | 70125 |
| 0.35 | 0.5 | −500000 | −168375 | 70125 |
| 0.75 | 0.5 | −500000 | −171375 | 70125 |
| 0.2001 | 3 | −500000 | −563.00328 | 0.40392 |
| 0.2001 | 1 | −500000 | −1686.58632 | 3.63528 |

### 2.2 Electric-motor efficiency map (`.../SimulationComponentData/ElectricMotorEfficienyMapTest.cs`)
Component file: `TestData/Hybrids/ElectricMotor/GenericEMotor.vem`.

**Torque for a given electrical power** `(electricPower[W], speed[rpm]) → expectedTorque[Nm]`, asserts to 1e-3 Nm (negative torque = drive):
| P_el [W] | n [rpm] | expected T [Nm] |
|---|---|---|
| −10000 | 700 | −118.916545 |
| −20000 | 1200 | −141.451404 |
| 10000 | 700 | 155.046977 |
| 20000 | 1200 | 177.530544 |

**Efficiency bounds** on map files (`vem_P_inverter_DC_90_*.vemo` → η in [0.8999, 0.9001]; `_std.vemo` → [0,1]). [VECTO] lines 122-124.

**Overload buffer** (`ElectricMachineSystem_Std_Overload.xml` → `OverloadBuffer = 600063.423` J, 0.1 tol). [VECTO] lines 156-177.

### 2.3 Other BEV integration tests
`VectoCore/VectoCoreTest/Integration/BatteryElectric/BatteryElectricTest.cs`, `BEVTimeRunTest.cs`, `IEPCTest.cs` — mostly assert `FinishedWithoutErrors` + non-empty modal data (constant-speed, drive-off, halt, grade, aux-power cases over SoC 0.25/0.5/0.7, grades ±5%, P_aux 1–5 kW). They are **behavioural** (no shipped numeric kWh/km), useful as smoke tests but not numeric anchors. [VECTO]

---

## 3. Can VECTO run headless in this sandbox? — NO  [VECTO]/[INFERRED]

**Attempted** and **failed**. Findings:
- Runtime present: `dotnet 9.0.318` (can target net8.0). VECTO projects (`VectoCore.csproj`, `VectoConsole.csproj`) multi-target `net48;net6.0;net8.0`, so net8.0 is in principle runnable. No `mono`/`msbuild` present.
- **No prebuilt binaries** in the repo (`vectocmd.exe` / `VectoConsole.dll` absent).
- **NuGet restore fails**: sandbox network is **INTEGRATIONS_ONLY**; `dotnet build VectoConsole -f net8.0` returns `NU1301: Unable to load the service index for source https://api.nuget.org/v3/index.json … proxy tunnel request … failed with status code '403'` for every project. No local NuGet cache (`~/.nuget/packages` empty), no vendored packages.

**Conclusion:** VECTO cannot be built or run here. **The "run ONE generic BEV lorry declaration job and report per-mission kWh/km" step is skipped** per the task instruction (run only if it can). To produce the M5.3 reference, VECTO must be built on a machine with NuGet access; then run e.g. `Generic Vehicles/Declaration Mode/PEV/GenericVehicleE2/BEV_E2.vecto` or `xEV XML Jobs/Lorries/Group5_ PEV_E4.xml` via `vectocmd` and read the `.vsum`/`.vmod` (see 10-outputs-and-reporting.md for columns).

---

## 4. What HDEV needs (M5.3)
1. **Component-level validation first** (runnable now, no VECTO execution): reproduce `Battery` and `EfficiencyMap` with the shipped `GenericBattery.vbat` / `GenericEMotor.vem` and assert the §2.1/§2.2 numbers. This is the strongest available anchor and validates M3.3 (battery) and the EM map (01) directly.
2. **Full-run validation** (deferred): build VECTO off-sandbox, run a generic Group-5 BEV lorry job, capture per-mission kWh/km from the `.vsum`, compare M5.2 output within tolerance.

---

## 5. Open questions
- Does Bob have an off-sandbox VECTO build to produce the full-run reference number M5.3 needs? (Task M5.3 already notes "Bob supplies a VECTO reference number".)
- The §2.1 battery numbers use the **engineering** DAO + `GenericBattery.vbat` (not the 243 kWh declaration pack). HDEV should validate against whichever pack it ships; both files are available.
- Need to confirm the `.vem`/`.vbat` test files' internal values (OCV table, Ri) so the HDEV reproduction uses identical inputs — read `GenericBattery.vbat`'s referenced `.vbatv/.vbatr` before writing the HDEV test.

---

## 6. Unblocks spec task(s)
- **M5.3** — provides concrete, numeric, reproducible-now **component** validation cases (battery SoC-step, usable energy, overload loss; EM map torque lookups; overload buffer) with exact input files and tolerances. Lets M5.3 start with component tests even though the full VECTO run is blocked in-sandbox.
- **M3.3** — the battery test numbers (§2.1) are the acceptance criteria for the OCV+Ri model's "matches `Battery.cs` on a charge-curve test".
- **01 (EM map)** — the §2.2 numbers validate the HDEV EM map/interpolation if adopted.
- Documents the **headless-run blocker** (NuGet/network) so the full-run reference is correctly scheduled off-sandbox, not attempted again here.
