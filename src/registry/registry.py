# STATUS: NEW (PR 1, Bob to review). The input registry: every input the tool knows about.
# the UI draws sections, fields AND counts ONLY from this registry (user §3.1 / §5.4): the registry is
# the single source of truth. the §5.4 mock-up numbers (a 112 total and the per-subgroup counts) were
# PLACEHOLDERS, not requirements - the real total is whatever the engine/source mapping yields, and the
# UI follows the registry. section/subgroup counts here are COMPUTED from FIELDS, never hard-coded.
# every field carries an internal `maps_to` naming the engine input / pipeline step / source document it
# feeds (see fields.py); a field with no legitimate mapping was removed rather than kept as padding.
#
# visibility rule (§3.1): every vehicle-physics, weather-physics, charging-physics and drivetrain field
# is "collapsed". only Operation and Energy prices fields may be "open". Costs & finance and Policy & taxes
# default to "collapsed" (Bob to review in the PR). "collapsed" fields are counted in totals but never
# listed by name in the UI; "hidden" fields are never counted or shown.
#
# §8 method-hiding: labels below are plain client-facing words only. no parameter/coefficient/formula/
# data-source/technical-strategy names. collapsed fields are counted but their names never reach the client.
#
# no physics default VALUES live here (that is the later M1.1 defaults.py). this file is pure structure.
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .fields import Field, SECTION_IDS


# ---------------------------------------------------------------------------
# section metadata: display name, expandable flag, and the ORDERED subgroup names.
# subgroup membership and all counts are DERIVED from FIELDS (see section_counts / total) - no hard-coded
# numbers live here. the §5.4 mock-up counts were placeholders, not requirements.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Section:
    id: str                      # one of SECTION_IDS
    display_name: str            # client-facing section title
    expandable: bool             # does the UI let the user expand it (§5.4)
    subgroups: Tuple[str, ...]   # ordered subgroup names in the section (counts derived from FIELDS)

    @property
    def total(self) -> int:
        # registry-derived: how many fields this section actually holds.
        return len(fields_in_section(self.id))


# section order + subgroup NAMES (§5.4 structure). expandable: Operation yes, Energy prices yes;
# every other section is drawn as a card but does not expose a field list. counts come from the registry.
SECTIONS: Tuple[Section, ...] = (
    Section("operation", "Operation", True, ("schedule", "routes")),
    Section("vehicles", "Vehicles", False,
            ("body", "drivetrain", "battery", "wheels", "equipment")),
    Section("depot_grid", "Depot & grid", False,
            ("site", "connection", "building_load", "chargers_on_site")),
    Section("charging", "Charging", False,
            ("strategy", "charger_types", "time_windows")),
    Section("energy_prices", "Energy prices", True,
            ("electricity", "grid_tariffs", "diesel", "trends")),
    Section("weather", "Weather", False,
            ("location", "daily_records", "seasons")),
    Section("costs_finance", "Costs & finance", False,
            ("purchase", "leasing", "maintenance", "finance")),
    Section("policy_taxes", "Policy & taxes", False,
            ("taxes", "subsidies")),
)


# small helper so the field tables below read cleanly. `maps_to` is required: it names the engine input
# / pipeline step / source doc this field feeds (internal metadata, not shown to the client).
def _f(section: str, subgroup: str, local_id: str, label: str, ftype: str,
       unit: Optional[str], visibility: str, editable_in_demo: bool, maps_to: str) -> Field:
    return Field(
        id=f"{section}.{subgroup}.{local_id}",
        section=section,
        subgroup=subgroup,
        label=label,
        type=ftype,
        unit=unit,
        visibility=visibility,
        editable_in_demo=editable_in_demo,
        maps_to=maps_to,
    )


# ---------------------------------------------------------------------------
# OPERATION (expandable, plain operational fields -> may be "open")
# ---------------------------------------------------------------------------
_OPERATION: List[Field] = [
    # schedule (5). "Shift end" is the §3.2 example lever extension: open + editable, dropdown (enum).
    _f("operation", "schedule", "shift_start", "Shift start", "time", None, "open", True,
       "resolver calendar/charging timing (design.md pipeline step D/E + M); charging session arrival/departure windows; resolver written last"),
    _f("operation", "schedule", "shift_end", "Shift end", "enum", None, "open", True,
       "resolver calendar/charging timing (step D/E + M); also an open+editable lever target (§3.2); resolver written last"),
    _f("operation", "schedule", "working_days_per_week", "Working days per week", "number", "days", "open", True,
       "calendar build (design.md step D/E build_calendar: operating-day count); resolver written last"),
    _f("operation", "schedule", "breaks_per_shift", "Breaks per shift", "number", None, "open", True,
       "driver_model stop rows + charging opportunity windows (design.md steps G/M); resolver written last"),
    _f("operation", "schedule", "shifts_per_day", "Shifts per day", "number", None, "open", True,
       "calendar/charging sequence (design.md step D/E + M); resolver written last"),
    # routes (5)
    _f("operation", "routes", "daily_distance", "Daily distance", "number", "km", "open", True,
       "resolve_typed -> waypoints distance_m (design.md step C->G; docs/context/input-layer-and-json.md typed input)"),
    _f("operation", "routes", "stops_per_day", "Stops per day", "number", None, "open", True,
       "resolve_typed -> payload_engine stop column / waypoint stop_s (design.md step C->H; payload_engine arg stop)"),
    _f("operation", "routes", "longest_trip", "Longest trip of the day", "number", "km", "open", True,
       "resolve_typed -> waypoints / battery sizing worst-day (design.md step C->G, L sizing)"),
    _f("operation", "routes", "return_to_depot", "Returns to depot each day", "bool", None, "open", True,
       "charging session construction - depot plug-in each day (design.md step M)"),
    _f("operation", "routes", "terrain", "Terrain", "enum", None, "open", True,
       "resolve_typed -> waypoint grade/altitude (design.md step C->G driver_model grade); resolver written last"),
]

# ---------------------------------------------------------------------------
# VEHICLES (no expand; all fields collapsed per §3.1)
# ---------------------------------------------------------------------------
_VEHICLES: List[Field] = [
    # body (6)
    _f("vehicles", "body", "vehicle_type", "Vehicle type", "enum", None, "collapsed", False,
       "defaults selection key: VECTO vehicle group / mission (2026-10-07 VECTO defaults note - SegmentTable.csv); pending defaults.py / M1.1"),
    _f("vehicles", "body", "body_type", "Body type", "enum", None, "collapsed", False,
       "body/trailer curb mass selection (2026-10-07 VECTO defaults note - Body_Trailers_Weights.csv); feeds mass m at power_step J; pending defaults.py / M1.1"),
    _f("vehicles", "body", "empty_weight", "Empty weight", "number", "kg", "collapsed", False,
       "power_step J mass term m = vehicle+body+payload (design.md step J); force/power pipeline"),
    _f("vehicles", "body", "max_weight", "Maximum weight", "number", "kg", "collapsed", False,
       "payload cap (GVWR) at mass assembly (design.md step J; 2026-10-07 VECTO defaults note payload capped by GVWR/40t/60t)"),
    _f("vehicles", "body", "length", "Length", "number", "m", "collapsed", False,
       "battery sizing mode B glider geometry / mass assembly (design.md step L); pending sizing.py"),
    _f("vehicles", "body", "height", "Height", "number", "m", "collapsed", False,
       "crosswind_engine arg vehicle_height (src/engine/crosswind_engine.py); reference height default in 2026-10-07 VECTO defaults note"),
    # drivetrain (5)
    _f("vehicles", "drivetrain", "axle_layout", "Axle layout", "enum", None, "collapsed", False,
       "VECTO vehicle group / crosswind coefficient set selection (2026-10-07 VECTO defaults note); pending defaults.py / M1.1"),
    _f("vehicles", "drivetrain", "rated_power", "Rated power", "number", "kW", "collapsed", False,
       "power/consumption cap and battery sizing (design.md steps J/L)"),
    _f("vehicles", "drivetrain", "top_speed", "Top speed", "number", "km/h", "collapsed", False,
       "driver_model target speed cap (design.md step G driver_model)"),
    _f("vehicles", "drivetrain", "gear_count", "Number of gears", "number", None, "collapsed", False,
       "pending defaults.py / M1.1 (BEV drivetrain)"),
    _f("vehicles", "drivetrain", "driven_axles", "Driven axles", "number", None, "collapsed", False,
       "rolling-resistance / axle-share selection (2026-10-07 VECTO defaults note axle load shares; force_engine Crr); pending defaults.py / M1.1"),
    # battery (4)
    _f("vehicles", "battery", "usable_capacity", "Usable battery capacity", "number", "kWh", "collapsed", False,
       "battery sizing + charging (design.md steps L sizing, M charging battery kWh)"),
    _f("vehicles", "battery", "total_capacity", "Total battery capacity", "number", "kWh", "collapsed", False,
       "battery sizing mode A datasheet kWh (design.md step L)"),
    _f("vehicles", "battery", "max_charge_power", "Maximum charging power", "number", "kW", "collapsed", False,
       "charging session charger/vehicle power limit (design.md step M charger kW)"),
    _f("vehicles", "battery", "warranty_years", "Battery warranty", "number", "years", "collapsed", False,
       "pending TCO (§4I, built later)"),
    # wheels (2)
    _f("vehicles", "wheels", "tyre_size", "Tyre size", "text", None, "collapsed", False,
       "dynamic rolling radius r_dyn for force_engine (src/engine/force_engine.py arg r_dyn); pending defaults.py / M1.1"),
    _f("vehicles", "wheels", "axle_count", "Number of axles", "number", None, "collapsed", False,
       "axle count for per-axle rolling resistance (2026-10-07 VECTO defaults note axle load shares); pending defaults.py / M1.1"),
    # equipment (6)
    _f("vehicles", "equipment", "cooling_unit", "Cooling unit fitted", "bool", None, "collapsed", False,
       "p_aux auxiliary load (src/engine/p_aux.py - STUB, pending p_aux)"),
    _f("vehicles", "equipment", "tail_lift", "Tail lift fitted", "bool", None, "collapsed", False,
       "p_aux / extra equipment load at mass assembly (p_aux STUB + design.md step J); pending p_aux"),
    _f("vehicles", "equipment", "heating", "Cabin heating", "enum", None, "collapsed", False,
       "p_aux HVAC/cond cabin heating (src/engine/p_aux.py HVAC/Cond - STUB, non-VECTO cabin heating extra; pending p_aux)"),
    _f("vehicles", "equipment", "air_conditioning", "Air conditioning", "bool", None, "collapsed", False,
       "p_aux HVAC load (src/engine/p_aux.py HVAC - STUB, pending p_aux)"),
    _f("vehicles", "equipment", "onboard_charger", "Onboard charger fitted", "bool", None, "collapsed", False,
       "charging path - onboard AC charger capability (design.md step M); pending"),
    _f("vehicles", "equipment", "extra_equipment_load", "Extra equipment load", "number", "kg", "collapsed", False,
       "mass assembly m at power_step J (design.md step J added equipment mass)"),
]

# ---------------------------------------------------------------------------
# DEPOT & GRID (no expand; all collapsed)
# ---------------------------------------------------------------------------
_DEPOT_GRID: List[Field] = [
    # site (4)
    _f("depot_grid", "site", "parking_spaces", "Parking spaces at depot", "number", None, "collapsed", False,
       "charging site layout - simultaneous sessions (design.md step M site model); pending"),
    _f("depot_grid", "site", "site_area", "Site area", "number", "m2", "collapsed", False,
       "charging site layout - space available for chargers/parking (design.md step M site model); pending"),
    _f("depot_grid", "site", "overnight_parking", "Overnight parking at depot", "bool", None, "collapsed", False,
       "charging session window - overnight dwell (design.md step M); pending"),
    _f("depot_grid", "site", "distance_to_grid", "Distance to grid connection point", "number", "m", "collapsed", False,
       "TCO grid upgrade cost input (design.md §4I TCO; req §11); built LATER - \"pending TCO (§4I, built later)\""),
    # connection (5)
    _f("depot_grid", "connection", "connection_capacity", "Grid connection capacity", "number", "kW", "collapsed", False,
       "charging site cap kW couples vehicles (design.md step M site cap)"),
    _f("depot_grid", "connection", "voltage_level", "Connection voltage level", "enum", None, "collapsed", False,
       "grid connection model for charging site cap (design.md step M); pending"),
    _f("depot_grid", "connection", "spare_capacity", "Spare connection capacity", "number", "kW", "collapsed", False,
       "charging site available cap for EVs (design.md step M site cap)"),
    _f("depot_grid", "connection", "upgrade_available", "Connection upgrade available", "bool", None, "collapsed", False,
       "TCO/sweep grid upgrade option (design.md step N sweep site limit, §4I TCO); built LATER - \"pending sweep.py / TCO (§4I)\""),
    _f("depot_grid", "connection", "upgrade_lead_time", "Connection upgrade lead time", "number", "months", "collapsed", False,
       "TCO project timeline (design.md §4I TCO; req §11); built LATER - \"pending TCO (§4I, built later)\""),
    # building_load (4)
    _f("depot_grid", "building_load", "base_load", "Site base load", "number", "kW", "collapsed", False,
       "charging site cap net of building load (design.md step M site cap)"),
    _f("depot_grid", "building_load", "peak_load", "Site peak load", "number", "kW", "collapsed", False,
       "charging site cap peak coupling (design.md step M site cap)"),
    _f("depot_grid", "building_load", "has_solar", "On-site solar fitted", "bool", None, "collapsed", False,
       "site generation offsetting charging load (design.md step M); pending"),
    _f("depot_grid", "building_load", "solar_capacity", "On-site solar capacity", "number", "kW", "collapsed", False,
       "site generation kW offsetting charging load (design.md step M); pending"),
    # chargers_on_site (5)
    _f("depot_grid", "chargers_on_site", "existing_chargers", "Chargers already on site", "number", None, "collapsed", False,
       "charging site existing charger inventory (design.md step M); pending"),
    _f("depot_grid", "chargers_on_site", "existing_charger_power", "Existing charger power", "number", "kW", "collapsed", False,
       "charging charger kW (design.md step M charger kW)"),
    _f("depot_grid", "chargers_on_site", "charger_spaces", "Spaces reserved for chargers", "number", None, "collapsed", False,
       "charging site layout / sweep charger count (design.md steps M, N sweep); pending"),
    _f("depot_grid", "chargers_on_site", "shared_chargers", "Chargers shared with others", "bool", None, "collapsed", False,
       "charging session availability (design.md step M); pending"),
    _f("depot_grid", "chargers_on_site", "charger_access", "Charger access", "enum", None, "collapsed", False,
       "charging session availability / policy gating (design.md step M + §4F capability gating); pending"),
]

# ---------------------------------------------------------------------------
# CHARGING (no expand; all collapsed). strategy uses only client-facing names, never technical ones (§8).
# ---------------------------------------------------------------------------
_CHARGING: List[Field] = [
    # strategy (3)
    _f("charging", "strategy", "charging_priority", "Charging priority", "enum", None, "collapsed", False,
       "charging policy lever (§3.2 lever charging_priority; design.md step M policy + §4F capability gating). client-facing names only (§8)"),
    _f("charging", "strategy", "smart_charging", "Smart charging allowed", "bool", None, "collapsed", False,
       "capability gate charger.smart_charging (design.md §4F: false -> ASAP only; step M policy)"),
    _f("charging", "strategy", "ready_time", "Ready time each morning", "time", None, "collapsed", False,
       "charging JIT/ASAP target - ready by departure (design.md step M flexibility_setpoints)"),
    # charger_types (3)
    _f("charging", "charger_types", "charger_power", "Charger power", "number", "kW", "collapsed", False,
       "charging charger kW (design.md step M charger kW; sweep N)"),
    _f("charging", "charger_types", "connector_type", "Connector type", "enum", None, "collapsed", False,
       "charging connector/power compatibility (design.md step M); pending"),
    _f("charging", "charger_types", "chargers_count", "Number of chargers", "number", None, "collapsed", False,
       "charging site charger count / sweep (design.md steps M, N sweep)"),
    # time_windows (4)
    _f("charging", "time_windows", "window_start", "Charging window start", "time", None, "collapsed", False,
       "charging allowed window start (design.md step M session windows)"),
    _f("charging", "time_windows", "window_end", "Charging window end", "time", None, "collapsed", False,
       "charging allowed window end (design.md step M session windows)"),
    _f("charging", "time_windows", "daytime_charging", "Daytime charging allowed", "bool", None, "collapsed", False,
       "charging opportunity window flag (design.md step M)"),
    _f("charging", "time_windows", "opportunity_charging", "Top-up charging during the day", "bool", None, "collapsed", False,
       "charging opportunity (top-up) sessions during day (design.md step M)"),
]

# ---------------------------------------------------------------------------
# ENERGY PRICES (expandable, price-facing -> plain fields may be "open")
# ---------------------------------------------------------------------------
_ENERGY_PRICES: List[Field] = [
    # electricity (4)
    _f("energy_prices", "electricity", "price_level", "Electricity price level", "enum", None, "open", True,
       "electricity price lever (§3.2 lever electricity_price low/expected/high; design.md step O costs)"),
    _f("energy_prices", "electricity", "day_price", "Daytime electricity price", "number", "currency/kWh", "open", True,
       "charging/TCO electricity price series (design.md steps M, O; req §11 price slot)"),
    _f("energy_prices", "electricity", "night_price", "Night-time electricity price", "number", "currency/kWh", "open", True,
       "charging/TCO electricity price series night (design.md steps M, O)"),
    _f("energy_prices", "electricity", "contract_type", "Electricity contract type", "enum", None, "open", True,
       "TCO tariff model selection (design.md step O; req §11); pending TCO (§4I)"),
    # grid_tariffs (3)
    _f("energy_prices", "grid_tariffs", "capacity_charge", "Grid capacity charge", "number", "currency/kW", "open", True,
       "TCO grid capacity charge (design.md step O; req §11 tariff slot); built LATER - \"pending TCO (§4I)\""),
    _f("energy_prices", "grid_tariffs", "energy_charge", "Grid energy charge", "number", "currency/kWh", "open", True,
       "TCO grid energy charge (design.md step O; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("energy_prices", "grid_tariffs", "peak_charge", "Grid peak charge", "number", "currency/kW", "open", True,
       "TCO grid peak/demand charge coupled to site peak (design.md steps N, O; req §11); built LATER - \"pending TCO (§4I)\""),
    # diesel (2)
    _f("energy_prices", "diesel", "diesel_price", "Diesel price", "number", "currency/litre", "open", True,
       "TCO diesel baseline comparison (design.md step O; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("energy_prices", "diesel", "diesel_consumption", "Diesel use per 100 km", "number", "litre/100km", "open", True,
       "TCO diesel baseline energy use (design.md step O); built LATER - \"pending TCO (§4I)\""),
    # trends (2)
    _f("energy_prices", "trends", "electricity_trend", "Expected electricity price trend", "number", "%/year", "open", True,
       "TCO price escalation over ownership years (design.md step O; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("energy_prices", "trends", "diesel_trend", "Expected diesel price trend", "number", "%/year", "open", True,
       "TCO diesel price escalation (design.md step O); built LATER - \"pending TCO (§4I)\""),
]

# ---------------------------------------------------------------------------
# WEATHER (no expand; all collapsed per §3.1 weather-physics rule)
# ---------------------------------------------------------------------------
_WEATHER: List[Field] = [
    # location (2)
    _f("weather", "location", "region", "Region", "enum", None, "collapsed", False,
       "weather climatology fetch key - DMI region (design.md step W weather_for_rows; src/data_fetch build_weather); pending build_weather"),
    _f("weather", "location", "climate_zone", "Climate zone", "enum", None, "collapsed", False,
       "weather temperature/wind series selection (design.md step W); pending build_weather"),
    # daily_records (4)
    _f("weather", "daily_records", "avg_temperature", "Average temperature", "number", "degC", "collapsed", False,
       "weather_for_rows temps_by_hour -> rho + aux (design.md step W; air density rho = P/(R T))"),
    _f("weather", "daily_records", "min_temperature", "Lowest temperature", "number", "degC", "collapsed", False,
       "weather extreme day-type (design.md step W + D/E calendar cold-day bin)"),
    _f("weather", "daily_records", "max_temperature", "Highest temperature", "number", "degC", "collapsed", False,
       "weather extreme day-type (design.md step W + D/E calendar)"),
    _f("weather", "daily_records", "wind_speed", "Average wind speed", "number", "m/s", "collapsed", False,
       "crosswind_engine v_ref wind speed + weather_for_rows winds_by_hour (src/engine/crosswind_engine.py arg v_ref; design.md step W)"),
    # seasons (2)
    _f("weather", "seasons", "winter_length", "Winter length", "number", "months", "collapsed", False,
       "calendar day-type binning season length (design.md step D/E group_runs); pending calendar.py"),
    _f("weather", "seasons", "weather_year", "Weather year", "enum", None, "collapsed", False,
       "weather year lever (§3.2 lever weather_year normal/cold_winter; design.md step W/D-E)"),
]

# ---------------------------------------------------------------------------
# COSTS & FINANCE (no expand; default collapsed, Bob to review)
# ---------------------------------------------------------------------------
_COSTS_FINANCE: List[Field] = [
    # purchase (5)
    _f("costs_finance", "purchase", "vehicle_price", "Vehicle purchase price", "number", "currency", "collapsed", False,
       "TCO capex vehicle price (design.md §4I TCO; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "purchase", "charger_price", "Charger purchase price", "number", "currency", "collapsed", False,
       "TCO capex charger price (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "purchase", "installation_cost", "Installation cost", "number", "currency", "collapsed", False,
       "TCO capex install (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "purchase", "grid_upgrade_cost", "Grid upgrade cost", "number", "currency", "collapsed", False,
       "TCO capex grid upgrade (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "purchase", "resale_value", "Resale value", "number", "currency", "collapsed", False,
       "TCO residual value (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    # leasing (3)
    _f("costs_finance", "leasing", "monthly_lease", "Monthly lease cost", "number", "currency/month", "collapsed", False,
       "TCO opex lease (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "leasing", "lease_term", "Lease term", "number", "months", "collapsed", False,
       "TCO lease horizon (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "leasing", "down_payment", "Down payment", "number", "currency", "collapsed", False,
       "TCO lease upfront (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    # maintenance (5)
    _f("costs_finance", "maintenance", "service_cost", "Service cost per year", "number", "currency/year", "collapsed", False,
       "TCO opex maintenance (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "maintenance", "tyre_cost", "Tyre cost per year", "number", "currency/year", "collapsed", False,
       "TCO opex tyres (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "maintenance", "insurance_cost", "Insurance cost per year", "number", "currency/year", "collapsed", False,
       "TCO opex insurance (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "maintenance", "repair_budget", "Repair budget per year", "number", "currency/year", "collapsed", False,
       "TCO opex repairs (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "maintenance", "downtime_cost", "Downtime cost per day", "number", "currency/day", "collapsed", False,
       "TCO opex downtime (§4I); built LATER - \"pending TCO (§4I)\""),
    # finance (6)
    _f("costs_finance", "finance", "ownership_years", "Ownership period", "enum", "years", "collapsed", False,
       "ownership-years lever (§3.2 lever ownership_years 8/10/12; TCO horizon §4I)"),
    _f("costs_finance", "finance", "interest_rate", "Interest rate", "number", "%/year", "collapsed", False,
       "TCO discounting (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "finance", "loan_amount", "Loan amount", "number", "currency", "collapsed", False,
       "TCO financing (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "finance", "loan_term", "Loan term", "number", "years", "collapsed", False,
       "TCO financing horizon (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("costs_finance", "finance", "annual_mileage", "Annual mileage", "number", "km/year", "collapsed", False,
       "TCO per-km normalisation + annual energy totals (design.md steps D/E totals, §4I TCO)"),
    _f("costs_finance", "finance", "discount_rate", "Discount rate", "number", "%/year", "collapsed", False,
       "TCO NPV discount rate (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
]

# ---------------------------------------------------------------------------
# POLICY & TAXES (no expand; default collapsed, Bob to review)
# ---------------------------------------------------------------------------
_POLICY_TAXES: List[Field] = [
    # taxes (4)
    _f("policy_taxes", "taxes", "registration_tax", "Registration tax", "number", "currency", "collapsed", False,
       "TCO capex tax (§4I; req §11); built LATER - \"pending TCO (§4I)\""),
    _f("policy_taxes", "taxes", "annual_road_tax", "Annual road tax", "number", "currency/year", "collapsed", False,
       "TCO opex tax (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("policy_taxes", "taxes", "energy_tax", "Energy tax", "number", "currency/kWh", "collapsed", False,
       "TCO electricity tax on energy price (design.md step O; §4I); built LATER - \"pending TCO (§4I)\""),
    _f("policy_taxes", "taxes", "vat_rate", "VAT rate", "number", "%", "collapsed", False,
       "TCO VAT (§4I); built LATER - \"pending TCO (§4I)\""),
    # subsidies (3)
    _f("policy_taxes", "subsidies", "vehicle_subsidy", "Vehicle purchase subsidy", "number", "currency", "collapsed", False,
       "TCO capex subsidy (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("policy_taxes", "subsidies", "charger_subsidy", "Charger purchase subsidy", "number", "currency", "collapsed", False,
       "TCO capex charger subsidy (§4I); built LATER - \"pending TCO (§4I)\""),
    _f("policy_taxes", "subsidies", "grid_subsidy", "Grid upgrade subsidy", "number", "currency", "collapsed", False,
       "TCO capex grid subsidy (§4I); built LATER - \"pending TCO (§4I)\""),
]


# the full field list, in section order
FIELDS: Tuple[Field, ...] = tuple(
    _OPERATION + _VEHICLES + _DEPOT_GRID + _CHARGING
    + _ENERGY_PRICES + _WEATHER + _COSTS_FINANCE + _POLICY_TAXES
)

# index by id for fast lookup
_FIELDS_BY_ID: Dict[str, Field] = {f.id: f for f in FIELDS}
_SECTIONS_BY_ID: Dict[str, Section] = {s.id: s for s in SECTIONS}

# subgroup view: {section_id: {subgroup: [Field, ...]}}
SUBGROUPS: Dict[str, Dict[str, List[Field]]] = {}
for _field in FIELDS:
    SUBGROUPS.setdefault(_field.section, {}).setdefault(_field.subgroup, []).append(_field)


# ---------------------------------------------------------------------------
# lookups / helpers
# ---------------------------------------------------------------------------
def get_field(field_id: str) -> Optional[Field]:
    # return the Field for an id, or None if it is not in the registry
    return _FIELDS_BY_ID.get(field_id)


def has_field(field_id: str) -> bool:
    return field_id in _FIELDS_BY_ID


def get_section(section_id: str) -> Optional[Section]:
    return _SECTIONS_BY_ID.get(section_id)


def fields_in_section(section_id: str) -> List[Field]:
    return [f for f in FIELDS if f.section == section_id]


def fields_in_subgroup(section_id: str, subgroup: str) -> List[Field]:
    return [f for f in FIELDS if f.section == section_id and f.subgroup == subgroup]


def section_counts() -> Dict[str, Dict[str, object]]:
    # registry-derived counts per section: n (fields in the section) plus a per-subgroup breakdown.
    # there is NO comparison to a hard-coded §5.4 "expected" total - the registry is the source of truth.
    out: Dict[str, Dict[str, int]] = {}
    for section in SECTIONS:
        subgroup_counts = {
            name: len(fields_in_subgroup(section.id, name)) for name in section.subgroups
        }
        out[section.id] = {
            "n": len(fields_in_section(section.id)),
            "subgroups": subgroup_counts,
        }
    return out


def visibility_counts(section_id: Optional[str] = None) -> Dict[str, int]:
    # count fields by visibility, optionally within one section
    pool = FIELDS if section_id is None else fields_in_section(section_id)
    counts = {"open": 0, "collapsed": 0, "hidden": 0}
    for f in pool:
        counts[f.visibility] += 1
    return counts


def listable_fields(section_id: Optional[str] = None) -> List[Field]:
    # "open" fields: the only ones the UI may list by name (§3.1)
    pool = FIELDS if section_id is None else fields_in_section(section_id)
    return [f for f in pool if f.visibility == "open"]


def counted_only_fields(section_id: Optional[str] = None) -> List[Field]:
    # "collapsed" fields: counted in totals but never named in the UI (§3.1)
    pool = FIELDS if section_id is None else fields_in_section(section_id)
    return [f for f in pool if f.visibility == "collapsed"]


def editable_demo_fields() -> List[Field]:
    # open + editable_in_demo fields are ALSO allowed levers (user §3.2 bullet)
    return [f for f in FIELDS if f.visibility == "open" and f.editable_in_demo]
