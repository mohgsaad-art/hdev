# 10 — Outputs & reporting (.vmod, .vsum, MRF/CIF/VIF for BEVs, graphs)

VECTO source: `mohgsaad-art/VECTO` @ `stable` / `d16ba783c` (v5.1.3). Tags: **[VECTO]** / **[INFERRED]**.

---

## 1. Modal results `.vmod` — per-step columns  [VECTO]
`Models/Simulation/Data/ModalResultField.cs` (caption + output factor). BEV-relevant columns:

**Driving-resistance power** (all [kW], factor 1e-3):
- `P_roll`, `P_air`, `P_slope`, `P_wheel_in`, `P_wheel_inertia`, `P_wheelEnd_in`, `P_wheelEnd_saving`.

**Auxiliary power**:
- `P_aux_el [kW]`, `P_aux_el_HV [kW]` (high-voltage aux), `P_aux_{id}_el [kW]` (per-aux).

**Electric machine** (per axle, [kW]):
- `P_{pos}-em_drive_max`, `P_{pos}-em_gen_max` (torque limits × speed), `P_{pos}-em_mech`, `P_{pos}-em_mech_map`, `P_{pos}-em_el` (electrical), `P_{pos}-em_loss`, `P_{pos}-em_inertia_loss`, `P_{pos}_in/out/mech/loss`, `P_{pos}_transm_loss`.
- `EM_OVL-{pos}-em [%]` (thermal buffer used), `EM_{pos}_off` (motor-off flag). Also `n_EM`, `T_EM`.

**REESS / battery** (`ModalResultField.cs:465-477`):
| caption | field | unit |
|---|---|---|
| `P_REESS_T` | `P_reess_terminal` | kW (terminal power) |
| `P_REESS_int` | `P_reess_int` | kW (U0·I) |
| `P_REESS_loss` | `P_reess_loss` | kW (I²·Ri) |
| `REESS SOC` | `REESSStateOfCharge` | % |
| `P_REESS_charge_max` / `discharge_max` | | kW |
| `U_REESS_terminal` | `U_reess_terminal` | V |
| `U_0_REESS` | `U0_reess` | V (OCV) |
| `I_REESS` | `I_reess` | A |
| `P_REESS_ES_T` | `P_terminal_ES` | kW |
| `P_REESS_JB_Cables_loss` | `P_ES_Conn_loss` | kW (connector loss) |

These map 1:1 to the HDEV battery model (03) and EM model (01) — exactly the per-step quantities HDEV should emit for comparison. [VECTO]

---

## 2. Summary `.vsum` — per-run columns  [VECTO]
`OutputData/SummaryDataContainer.cs`. BEV-relevant (`BatteryColumns`, lines ~372-383):
- `REESS_CAPACITY`, `REESS_StartSoC`, `REESS_EndSoC`, `REESS_MinSoC`, `REESS_MaxSoC`, `REESS_DeltaEnergy`.
- Energy balance: `E_REESS_LOSS`, `E_REESS_T_chg` / `E_REESS_T_dischg` (terminal charge/discharge energy), `E_REESS_int_chg` / `E_REESS_int_dischg` (internal).
- (FCHV adds `FC_HEV_SOC_*` SoC-correction columns — not pure BEV.)
One summary row **per mission × payload**. [VECTO]

---

## 3. BEV declaration XML reports (MRF / CIF / VIF)  [VECTO]
`OutputData/XML/DeclarationReports/`:
- **MRF** (Manufacturer Report File) — full detail incl. component specs (`MRFElectricMachineType`, `MRFREESSSpecificationsType`, `MRFIEPCType`).
- **CIF** (Customer Information File) — customer-facing summary.
- **VIF** (Vehicle Information File) — primary-vehicle components for multi-stage (`VIFElectricMachineType`, `VIFIepcType`, `VIFElectricMotorTorqueLimitsType`).

**Electric energy consumption output** (`Common/ElectricEnergyWriter.cs`, `LorryElectricEnergyConsumptionWriter.GetEnergyConsumption`): for each result the BEV reports electrical energy consumption as a **list of units** [VECTO] lines 70-90:
```
elEnergy / distance                 → kWh/km
elEnergy / distance / payload       → kWh/(t·km)
elEnergy / distance / cargoVolume   → kWh/(m³·km)   (if volume > 0)
+ MJ/km, MJ/(t·km), MJ/(m³·km) equivalents
```
Produced **per mission × payload** and as a **weighted result** (`GetElement(IWeightedResult weighted)`), using the mission/payload weighting factors (09 §8). [VECTO]

**Range**: VECTO declaration does **not** report a driving range as a primary BEV output in the energy writer read here — it reports **energy consumption** (kWh/km) and SoC/energy balance; range is derivable (useable energy ÷ kWh/km) but not a direct field in `ElectricEnergyWriter`. [INFERRED — exhaustive read of the energy writer; a range field may exist elsewhere in the schema but was not found in the result writers.]

---

## 4. Results per mission / payload  [VECTO]
Each declaration run produces results for each **mission** at each **loading** (low + reference, 09 §8), then a **weighted** total. The `.vsum` has a row per (mission, payload); the XML reports group by mission with per-payload entries and the weighted CO₂/energy. [VECTO] `ResultGroupWriter.cs`, `ResultTotalWriter.cs`.

---

## 5. Graphs / plots  [VECTO]
`Tools/GraphDrawer/` (`Program.cs`) — a standalone tool that plots VECTO modal (`.vmod`) data (e.g. speed, power, SoC vs distance/time). The main GUI (`VECTO3GUI2020`) has result visualisation. No declaration *report* ships plots; plotting is a tool/GUI feature over the `.vmod`. [VECTO] (GUI not inspected in depth — out of headless scope.)

---

## 6. What HDEV needs
1. Emit per-step results matching the `.vmod` BEV columns (SoC, U0, U_terminal, I, P_reess_terminal/int/loss, P_em_el/loss, P_aux_el, P_roll/air/slope) for direct comparison with a VECTO `.vmod`.
2. Summary per run: start/end/min/max SoC, ΔEnergy, E_loss, charge/discharge energy.
3. BEV consumption in **kWh/km**, kWh/(t·km), kWh/(m³·km), per mission × payload + weighted.
4. Range = useable energy ÷ kWh/km (HDEV-computed; VECTO reports consumption, not range directly).

---

## 7. Open questions
- Is there a dedicated BEV "range"/"actual charge-depleting range" field in the VIF/CIF XML schema (vs HEV)? The energy writer only emits consumption; the schema (`XMLNames`) may define a range element elsewhere. Needs the schema XSD (not read here).
- Which exact `.vmod` columns HDEV must match for M5.3 (likely SoC + P_reess_terminal + kWh/km).

---

## 8. Unblocks spec task(s)
- **M5.3 (validation)** — the `.vmod` BEV column list is the comparison target; `.vsum` SoC/energy columns are the per-run anchor; kWh/km is the headline metric.
- **M2.8 / M4.1 (results, runner)** — HDEV results JSON should mirror these fields (per-mission kWh/km + SoC balance + weighted).
- **M1.7 (assumptions report)** — reporting structure (per mission/payload + weighted) informs the HDEV report layout.
