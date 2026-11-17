# HDEV — input list for UI design (26 Oct 2026)

Based on the engine functions in `HDEV_NEW.ipynb` plus the decisions in the close-outs and project notes.

## Key
- **Client** = fleet owner or operator enters it.
- **OEM** = manufacturer or spec sheet enters it. These override the client or standard value.
- **Std** = filled by `defaults.py` or the parser from VECTO or EU standard values. It is shown collapsed, and the user can override it.
- **Hidden** = constants or numerical settings. Not shown in the UI.

---

## Part 1 — What the user can enter (grouped for the UI)

### 1. Route (operation)
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| Route source: VDRI template / typed / GPS / AI | Client | – | parser |
| VDRI template pick (mission) | Client | – | `wp_s, wp_v, wp_stop, wp_grade` |
| Typed route: total distance, number of stops, average stop time | Client | dwell 45 min/stop, speeds 30/50/80 km/h, flat grade | resolver → waypoints |
| GPS file upload | Client | – | GPS adapter → waypoints |
| Stop table: stop time per stop | Client | from source | `wp_stop` |
| Shift start time | Client | – | `t_start` |
| Operating dates (year) | Client | – | year run |

Stop table editability: VDRI → stop time and payload editable, distances locked. Typed → everything editable. GPS → payload only.

### 2. Payload
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| Shape: constant / linear / custom | Client | constant | `shape` |
| Start payload [t] | Client | VECTO reference payload (Std) | `payload_start` |
| End payload [t] (linear only) | Client | – | `payload_end` |
| Payload per stop [t] (custom only, in stop table) | Client | – | `payload_custom` |
| **Open decision:** default = VECTO reference or max payload | Bob | – | defaults.py |

### 3. Vehicle body and mass
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| Vehicle type / group (rigid, tractor, van…) | Client | – | picks all Std lookups |
| Curb mass [kg] | Client (registration) / OEM | – | `m_vehicle` |
| Gross vehicle weight [kg] | Client (registration) | – | payload cap (planned parser check) |
| Vehicle height [m] | Client / OEM | VECTO generic by group (Std) | `vehicle_height` |
| CdxA(0) [m²] | OEM (certified, Annex VIII) | VECTO generic by group (Std) | `CdxA0` |
| Yaw coefficients a1, a2, a3 | OEM | VECTO by vehicle type, `VCDV_parameters.csv` (Std) | `crosswind_engine` |

### 4. Tyres and wheels
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| Rolling resistance Crr (EU tyre label) | Client / OEM | Std | `Crr` (driver model, force engine), `Crr_eff` (parser) |
| Tyre size → dynamic radius `r_dyn` | Client / OEM | Std | `force_engine` |
| Wheel inertia → `m_red_wheels` | OEM | Std (VECTO formula) | `driver_model` |

### 5. Drivetrain and motor
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| Motor rated power `P_max` | Client (spec sheet) / OEM | – | `driver_model` |
| Max regen power `P_regen_max` | OEM | none = no cap | `consumption_engine` |
| Motor / inverter / gearbox efficiency | OEM | 0.95 / 0.95 / 0.98 placeholders, to be replaced by Annex Xb standard maps | `consumption_engine` |
| Regen efficiency | OEM | placeholder | `consumption_engine` |
| Rotating inertia `theta_red` | OEM | 0 = off | `force_engine` |
| Drivetrain drag `P_drag_loss` | OEM | 0 now; from standard maps later | `driver_model` |

### 6. Auxiliaries
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| ES: technology dropdown or custom W | Client / OEM | VECTO table by mission (Std) | `ES_power` |
| ES efficiency | OEM | 0.7 (label: "0.7 = VECTO; set 1.0 if your value is already electric") | `ES_alteff` |
| PS: technology dropdown (elec. driven rows only) or custom W | Client / OEM | VECTO `PS-Table.csv` (Std) | `PS_power` |
| PS efficiency | OEM | 1.0 | `PS_alteff` |
| Steering: number of steered axles + technology per axle | Client / OEM | VECTO SP tables (Std) | `SP_power_helper` |
| SP efficiency | OEM | 0.7 (in code) | `SP_alteff` |
| HVAC mode: VECTO constant / thermal | Client | – | `HVAC_power` |
| HVAC VECTO: dropdown or custom W | Client / OEM | VECTO table (Std) | `HVAC_power` |
| Cond: dropdown (by mission) or custom W | Client / OEM | VECTO `Cond-Table.csv` (Std) | `cond_power` |
| Always-on PTO [W] (chiller, mixer) | Client | 0 | `PTO_always_on` |

### 7. HVAC thermal (only when HVAC mode = thermal)
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| Cab dimensions → wall area, window area, volume | OEM (or class template) | placeholders today; must be replaced | `A_surface, A_window, cab_volume` |
| Insulation U | OEM | Std | `U` |
| Number of people in cab | Client | – | `N_persons` |
| Heater type → COP points and shares (HP / electric / fuel) | Client / OEM | VECTO tables (Std) | `T_heat_points … fuel_share_points` |
| Max heating / cooling power [W] | OEM | – | `max_heating_power, max_cooling_power` |
| Electric heater efficiency | OEM | 0.93 | `eh_eff` |

### 8. PTO
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| PTO at stops on/off per stop (stop table column) | Client | – | `is_on` |
| Stop PTO profile (`t`, `W`), or one constant value | Client / OEM | VECTO `.vptoel` (Std) | `pto_t, pto_w` |
| Option: "use stop time as PTO time" | Client | off (VECTO: stop + PTO time) | parser |
| **Planned:** driving PTO start / end per waypoint + driving profile | Client / OEM | off | consumption engine |
| **Planned:** fridge unit: ATP K (or class IN/IR), inner + outer box dimensions, set temp, cooling COP points, heating efficiency | Client / OEM | off; constant W stays the default | new helper |
| **Planned (after drivetrain):** PTO shaft type (`PTO-tech.csv` dropdown) | OEM | none | consumption engine |

### 9. Weather
| Input | Who | Default / note | Feeds |
|---|---|---|---|
| Location → DMI station | Client | – | `T_amb_h`, `v_ref`, solar |
| Weather year | Client | – | same |

---

## Part 2 — Filled automatically (no user field)
- **From the route and driver model:** `T, S, V, A, grade, M`, `k_lin, k_roll, k_rot, L, v_avg`, `payload_wp`, `pto_1s`, `pto_on_col`, `pto_start_col`, and `W1`/`W2` tables.
- **From weather:** hourly `T_amb_h`, solar and `v_ref`.
- **Derived:** `coast_mass` (fixed reference mass), `cdxa_v` / `cdxa` reference table, `beta` = 0.9 with `Crr_eff` (parser).

## Part 3 — Hidden constants and settings (VECTO / physics)
- **Crosswind:** `h_ref` 10 m (DMI), `wind_exp` 0.2, `dh`, `dphi_deg`, speed grid 60–130 km/h, `beta_limit_deg` 10° (HDEV decision).
- **Driver model:** `.vacc` curves by vehicle, `dt` 1 s, `rho` 1.188, `g` 9.81, `lac_min_v` 50, `lac_dist_factor` 10, `df_offset` 2.5, `df_scaling` 1.5, `df_vtarget`, `df_vdrop`, `os_min_v` 50, `os_allowed` 2.5, `brake_margin` 0.1, `v_min_coast` 5.
- **Consumption:** `p_air` 101,325 Pa, `R_air` 287.05, `v_no_regen` 5 km/h.
- **HVAC thermal:** `spec_vent_power` 0.56, `vent_rate`, `vent_rate_heating`, `heat_per_person` (50, 80), `clouding` (0.65, 0.8), `T_boundary` 17, `g` 0.95, `solar_factor` 0.25, `waste_heat` 0, `T_heat` 18, `T_cool` 23, `T_cool_off` 17.

## Planned inputs from other agreed work (not in the code yet)
- Drivetrain standard values (Annex Xb): gear and axle data → the parser derives loss maps, regen limit and coasting drag.
- Cold-tyre factor Kt: 0.006 (load index > 121) or 0.010, picked from the tyre load index.
- Battery: capacity; OCV + Ri or EU standard values (Annex Xb App. 10).

## Things to check in the code
- `P_aux` default `HVAC_eff = 1.25`. For the HVAC thermal path it must be 1.0, because `HVAC_thermal` already returns electric W.
- `consumption_engine` takes `PTO_always_on` as one number. The fridge model needs per hour, the same treatment `HVAC` has.
- Payload is entered in tonnes in the UI but used in kg in the engine. Convert in the parser.
