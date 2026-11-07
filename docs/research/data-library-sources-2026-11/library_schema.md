# Data-library schema (proposal, section 6)

This is a proposal, not a build. Eight tables. Each row carries its own basis tag
and source, so a measured value and an OEM claim never sit in the same cell with
no way to tell them apart.

Column legend used below:
- `basis` — one controlled tag per value: `installed` | `usable` | `continuous`
  | `peak` | `measured` | `simulated` | `OEM claim` | `VECTO standard`.
- `source_id` — joins to the `sources` table.
- `page_or_table`, `quote` — provenance for every value.
- `licence_flag` — `open` (CC-BY / CC0 / public / EUPL) | `oem_cite` (OEM doc,
  cite only) | `restricted` (ISO, private, scraping-forbidden).

A design rule that falls straight out of pass 3: **store installed and usable as
two separate columns, and continuous and peak as two separate columns.** Never
derive one from the other by a fixed ratio — the Volvo PCE4 table alone runs
65%→70% usable across pack counts, and EEA real configs span 13%–86%.

---

## 1. vehicles
One row per make/model/variant/generation.

| column | unit | notes |
|---|---|---|
| vehicle_id (PK) | — | internal |
| make | — | e.g. Volvo |
| model | — | e.g. FM Electric |
| variant | — | e.g. ESS540K / 6x2 tractor |
| generation | — | e.g. PCE4, EX-D2, gen1/gen2 |
| vehicle_class | — | M1 / N1 / N2 / N3 / M2 / M3 |
| vecto_group | — | EEA VehicleGroup (e.g. 5, 9, P31/32) |
| axle_config | — | 4x2, 6x2… |
| pev_architecture | — | E2 / E3 / E4 / E-IEPC |
| body_type | — | tractor/rigid/refuse/mixer/reefer/bus |
| source_id, doc_date | — | provenance |
| licence_flag | — | |

Fillable from open sources: make/model/class/group/architecture/axle from EEA
`my_zev_configs` (CC-BY). Needs OEM doc: body_type detail, generation naming.

## 2. batteries
One row per battery option of a vehicle (or per EEA config).

| column | unit | basis | notes |
|---|---|---|---|
| battery_id (PK) | | | |
| vehicle_id (FK) | | | may be null when only the hashed EEA config is known |
| installed_kwh | kWh | installed | EEA TotalStorageCapacity / OEM |
| usable_kwh | kWh | usable | EEA TotalUsableCapacityInSimulation / OEM — separate column |
| pack_count | — | | |
| per_pack_installed_kwh | kWh | installed | |
| chemistry | — | OEM claim | LFP/NMC/NCA/Li-ion |
| nominal_voltage | V | | EEA NominalVoltage |
| capacity_ah | Ah | | |
| internal_resistance | Ω | simulated | VECTO generic only today |
| ocv_curve_ref | — | simulated | points SoC→V |
| soc_window | % | | e.g. 10–90 |
| ac_kw / dc_kw / mcs_kw | kW | | three columns |
| charge_20_80_min | min | | |
| charge_curve_ref | — | | kW vs SoC if available |
| thermal_heater_kw | kW | | rarely public |
| battery_mass_kg | kg | | per pack or total (state which) |
| warranty_terms | text | | |
| cert_method | — | measured/standard | EEA CertificationMethod |
| source_id, page_or_table, quote, doc_date, licence_flag | | | |

Fillable from open: installed, usable, nominal_voltage, cert_method (EEA CC-BY,
but hashed — no make/model until the `vehicle` header is fetched). Chemistry,
mass, per-pack, charging mostly OEM-cite. Ri/OCV: VECTO generic only.

## 3. motors_drivetrain
| column | unit | basis | notes |
|---|---|---|---|
| drivetrain_id (PK), vehicle_id (FK) | | | |
| architecture | — | | E2/E3/E4/IEPC |
| motor_count | — | OEM claim | |
| continuous_kw / peak_kw | kW | continuous / peak | two columns |
| continuous_nm / peak_nm | Nm | continuous / peak | two columns |
| peak_duration_s | s | | e.g. VECTO OverloadTime 120 |
| efficiency_map_ref / drag_curve_ref | — | simulated | VECTO generic |
| gearbox_type | — | | AMT/1-speed/… |
| gears_count | — | | EEA Transmission_NrOfGears |
| gear_ratios | list | | |
| axle_ratio | — | | EEA Axlegear_Ratio |
| max_input_torque | Nm | | rarely public |
| regen_limit | — | | VECTO only |
| source_id, page_or_table, quote, doc_date, licence_flag | | | |

Fillable from open: architecture, gears_count, axle_ratio, continuous_kw (EEA
MaxContinuousPower, hashed). Peak kW/Nm, maps: OEM-cite or VECTO generic.

## 4. aux_components
| column | unit | basis | notes |
|---|---|---|---|
| aux_id (PK), vehicle_id (FK) | | | |
| component | — | | cab_hvac / bus_hvac / steering_pump / air_compressor / dcdc_24v / battery_thermal |
| technology | — | | heat-pump vs PTC; electric-driven; etc. |
| power_w | W | VECTO standard / OEM claim | |
| mission | — | | long-haul/regional/urban/municipal/construction/coach |
| season | — | | summer/winter if available |
| heating_cooling | — | | heating vs cooling (HVAC) |
| source_id, page_or_table, quote, licence_flag | | | |

Fillable from open: VECTO declaration tables (EUPL) give W by mission/group and
flag which apply to PEV. EEA gives the technology CODE only. Real OEM aux kW and
seasonal values: BOB.

## 5. epto_body_equipment
| column | unit | basis | notes |
|---|---|---|---|
| equip_id (PK), vehicle_id (FK) | | | |
| equipment | — | | ePTO / refuse_compactor / lift / crane / reefer / mixer / tipper / sweeper / hook_lift |
| electrical_input_kw | kW | continuous or peak (state) | keep separate from mech output |
| mechanical_output_kw | kW | continuous or peak | keep separate from elec input |
| peak_duration_s | s | | |
| voltage | V | | e.g. 650 V DC |
| soc_condition | % | | e.g. "@50% SoC" |
| energy_per_cycle | kWh/cycle | measured | refuse/compaction |
| energy_per_hour | kWh/h | | reefer |
| energy_per_tonne | kWh/t | | |
| cooling_capacity_w | W | | reefers — separate from input kW |
| cop | — | | reefers |
| source_id, page_or_table, quote, licence_flag | | | |

Fillable from open: almost nothing. ePTO elec (DAF 25/90; eEconic 52/30) and mech
(Liebherr 125/60; Carrier reefer 19 kW input) are OEM-cite. Refuse/crane/tipper
energy: BOB. ISO 24162 gives the measurement method only (restricted).

## 6. masses_limits (date-effective)
| column | unit | notes |
|---|---|---|
| limit_id (PK) | | |
| vehicle_id (FK) or jurisdiction | — | per-vehicle masses OR legal limit |
| curb_mass_kg / gvw_kg / gcw_kg / payload_kg | kg | |
| axle_loads_kg | list | |
| battery_mass_kg | kg | |
| jurisdiction | — | e.g. DK, EU |
| rule_axles | — | 2-axle lorry, 7+ axle combo… |
| limit_kg / length_m / height_m | | the legal value |
| drivetrain_scope | — | all / ZEV / alt-fuel |
| effective_from / effective_to | date | **date-effective** |
| legal_ref | — | BEK 1447/2025 §21… |
| source_id, quote, licence_flag | | open (law) |

Fillable from open: EEA masses (CorrectedActualMass, TPMLM) and the Danish BEKs
(public law). This is one of the best-covered tables.

## 7. measured_consumption (with conditions)
| column | unit | basis | notes |
|---|---|---|---|
| meas_id (PK), vehicle_id (FK) | | | |
| value | kWh/km or Wh/km | measured / WLTP / simulated | state which |
| mass_kg | kg | | test mass |
| temperature_c | °C | | |
| cycle | — | | WLTP / VECTO mission / real route |
| sample_size | n | | |
| region | — | | |
| source_id, page_or_table, quote, doc_date, licence_flag | | | |

Fillable from open: EEA cars/vans WLTP Wh/km + range (CC-BY). Real measured
truck kWh/km with full conditions: mostly BOB (ICCT, RISE, Oeko, TNO, NAF).

## 8. sources_licences
| column | notes |
|---|---|
| source_id (PK) | matches catalogue.csv `id` |
| name, url, publisher, region | |
| licence | CC-BY 4.0 / CC0 / EUPL-1.2 / public law / OEM / ISO |
| commercial_use | yes / no / unclear |
| status | V / C / BOB |
| doc_date | |
| notes | |

This table is `catalogue.csv`.

---

## Column fill summary

**Fillable now from open, commercially usable sources**
(EEA CC-BY, RDW CC0, VECTO EUPL, public law):
- vehicles: make, model, class, vecto_group, axle_config, pev_architecture
- batteries: installed_kwh, usable_kwh, nominal_voltage, cert_method (EEA — but
  hashed, no make/model yet)
- motors: architecture, gears_count, axle_ratio, continuous_kw (EEA — hashed)
- aux: VECTO standard demands by mission (W) + which apply to PEV
- masses_limits: TPMLM, CorrectedActualMass; all Danish/EU legal limits
- measured_consumption: WLTP Wh/km + range for M1/N1 (cars/vans)
- CdxA bin (A1–A24) from EEA

**Needs OEM documents (cite-only):**
- chemistry, per-pack kWh, battery mass, charging kW/curve, warranty
- motor peak kW/Nm, motor count, gear ratios, max input torque
- ePTO electrical and mechanical kW, voltage, SoC condition
- reefer cooling capacity + COP, mixer/crane/body kW

**No public source today (any basis):**
- battery internal resistance, OCV curve (only VECTO generic exists)
- battery thermal/heater kW
- CIF kWh/km (per-vehicle, private)
- efficiency/torque maps per model (only VECTO generic)
- refuse compactor/lift, tipper, sweeper, hook-lift energy per cycle/tonne
- tyre RRC coefficient (EPREL gives label class only — pending API check)
