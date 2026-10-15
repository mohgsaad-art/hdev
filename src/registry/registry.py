# STATUS: NEW (PR 1, Bob to review). The input registry: every input the tool knows about.
# the UI draws sections and fields ONLY from this registry (user §3.1). counts and subgroup names match
# the §5.4 mock-up exactly (112 fields over 8 sections). if the registry ever differs from the mock-up,
# the registry wins and the UI follows (user §5.4).
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
# section metadata: display name, expandable flag, and subgroup names + counts (§5.4)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Section:
    id: str                               # one of SECTION_IDS
    display_name: str                     # client-facing section title
    expandable: bool                      # does the UI let the user expand it (§5.4)
    subgroups: Tuple[Tuple[str, int], ...]  # (subgroup name, expected field count) in order

    @property
    def total(self) -> int:
        return sum(count for _, count in self.subgroups)


# §5.4 table, verbatim. expandable: Operation yes, Energy prices yes, Weather no (field list not shown,
# but it is still drawn as a card); only Operation and Energy prices expose a field list in the UI.
SECTIONS: Tuple[Section, ...] = (
    Section("operation", "Operation", True, (("schedule", 5), ("routes", 5))),
    Section("vehicles", "Vehicles", False,
            (("body", 6), ("drivetrain", 5), ("battery", 4), ("wheels", 3), ("equipment", 6))),
    Section("depot_grid", "Depot & grid", False,
            (("site", 4), ("connection", 5), ("building_load", 4), ("chargers_on_site", 5))),
    Section("charging", "Charging", False,
            (("strategy", 3), ("charger_types", 4), ("time_windows", 4))),
    Section("energy_prices", "Energy prices", True,
            (("electricity", 5), ("grid_tariffs", 3), ("diesel", 2), ("trends", 2))),
    Section("weather", "Weather", False,
            (("location", 2), ("daily_records", 4), ("seasons", 3))),
    Section("costs_finance", "Costs & finance", False,
            (("purchase", 5), ("leasing", 4), ("maintenance", 5), ("finance", 6))),
    Section("policy_taxes", "Policy & taxes", False,
            (("taxes", 4), ("subsidies", 4))),
)


# small helper so the field tables below read cleanly: (local_id, label, type, unit, visibility, editable)
def _f(section: str, subgroup: str, local_id: str, label: str, ftype: str,
       unit: Optional[str], visibility: str, editable_in_demo: bool) -> Field:
    return Field(
        id=f"{section}.{subgroup}.{local_id}",
        section=section,
        subgroup=subgroup,
        label=label,
        type=ftype,
        unit=unit,
        visibility=visibility,
        editable_in_demo=editable_in_demo,
    )


# ---------------------------------------------------------------------------
# OPERATION (expandable, plain operational fields -> may be "open")
# ---------------------------------------------------------------------------
_OPERATION: List[Field] = [
    # schedule (5). "Shift end" is the §3.2 example lever extension: open + editable, dropdown (enum).
    _f("operation", "schedule", "shift_start", "Shift start", "time", None, "open", True),
    _f("operation", "schedule", "shift_end", "Shift end", "enum", None, "open", True),
    _f("operation", "schedule", "working_days_per_week", "Working days per week", "number", "days", "open", True),
    _f("operation", "schedule", "breaks_per_shift", "Breaks per shift", "number", None, "open", True),
    _f("operation", "schedule", "shifts_per_day", "Shifts per day", "number", None, "open", True),
    # routes (5)
    _f("operation", "routes", "daily_distance", "Daily distance", "number", "km", "open", True),
    _f("operation", "routes", "stops_per_day", "Stops per day", "number", None, "open", True),
    _f("operation", "routes", "longest_trip", "Longest trip of the day", "number", "km", "open", True),
    _f("operation", "routes", "return_to_depot", "Returns to depot each day", "bool", None, "open", True),
    _f("operation", "routes", "terrain", "Terrain", "enum", None, "open", True),
]

# ---------------------------------------------------------------------------
# VEHICLES (no expand; all fields collapsed per §3.1)
# ---------------------------------------------------------------------------
_VEHICLES: List[Field] = [
    # body (6)
    _f("vehicles", "body", "vehicle_type", "Vehicle type", "enum", None, "collapsed", False),
    _f("vehicles", "body", "body_type", "Body type", "enum", None, "collapsed", False),
    _f("vehicles", "body", "empty_weight", "Empty weight", "number", "kg", "collapsed", False),
    _f("vehicles", "body", "max_weight", "Maximum weight", "number", "kg", "collapsed", False),
    _f("vehicles", "body", "length", "Length", "number", "m", "collapsed", False),
    _f("vehicles", "body", "height", "Height", "number", "m", "collapsed", False),
    # drivetrain (5)
    _f("vehicles", "drivetrain", "axle_layout", "Axle layout", "enum", None, "collapsed", False),
    _f("vehicles", "drivetrain", "rated_power", "Rated power", "number", "kW", "collapsed", False),
    _f("vehicles", "drivetrain", "top_speed", "Top speed", "number", "km/h", "collapsed", False),
    _f("vehicles", "drivetrain", "gear_count", "Number of gears", "number", None, "collapsed", False),
    _f("vehicles", "drivetrain", "driven_axles", "Driven axles", "number", None, "collapsed", False),
    # battery (4)
    _f("vehicles", "battery", "usable_capacity", "Usable battery capacity", "number", "kWh", "collapsed", False),
    _f("vehicles", "battery", "total_capacity", "Total battery capacity", "number", "kWh", "collapsed", False),
    _f("vehicles", "battery", "max_charge_power", "Maximum charging power", "number", "kW", "collapsed", False),
    _f("vehicles", "battery", "warranty_years", "Battery warranty", "number", "years", "collapsed", False),
    # wheels (3)
    _f("vehicles", "wheels", "tyre_size", "Tyre size", "text", None, "collapsed", False),
    _f("vehicles", "wheels", "axle_count", "Number of axles", "number", None, "collapsed", False),
    _f("vehicles", "wheels", "wheel_count", "Number of wheels", "number", None, "collapsed", False),
    # equipment (6)
    _f("vehicles", "equipment", "cooling_unit", "Cooling unit fitted", "bool", None, "collapsed", False),
    _f("vehicles", "equipment", "tail_lift", "Tail lift fitted", "bool", None, "collapsed", False),
    _f("vehicles", "equipment", "heating", "Cabin heating", "enum", None, "collapsed", False),
    _f("vehicles", "equipment", "air_conditioning", "Air conditioning", "bool", None, "collapsed", False),
    _f("vehicles", "equipment", "onboard_charger", "Onboard charger fitted", "bool", None, "collapsed", False),
    _f("vehicles", "equipment", "extra_equipment_load", "Extra equipment load", "number", "kg", "collapsed", False),
]

# ---------------------------------------------------------------------------
# DEPOT & GRID (no expand; all collapsed)
# ---------------------------------------------------------------------------
_DEPOT_GRID: List[Field] = [
    # site (4)
    _f("depot_grid", "site", "parking_spaces", "Parking spaces at depot", "number", None, "collapsed", False),
    _f("depot_grid", "site", "site_area", "Site area", "number", "m2", "collapsed", False),
    _f("depot_grid", "site", "overnight_parking", "Overnight parking at depot", "bool", None, "collapsed", False),
    _f("depot_grid", "site", "distance_to_grid", "Distance to grid connection point", "number", "m", "collapsed", False),
    # connection (5)
    _f("depot_grid", "connection", "connection_capacity", "Grid connection capacity", "number", "kW", "collapsed", False),
    _f("depot_grid", "connection", "voltage_level", "Connection voltage level", "enum", None, "collapsed", False),
    _f("depot_grid", "connection", "spare_capacity", "Spare connection capacity", "number", "kW", "collapsed", False),
    _f("depot_grid", "connection", "upgrade_available", "Connection upgrade available", "bool", None, "collapsed", False),
    _f("depot_grid", "connection", "upgrade_lead_time", "Connection upgrade lead time", "number", "months", "collapsed", False),
    # building_load (4)
    _f("depot_grid", "building_load", "base_load", "Site base load", "number", "kW", "collapsed", False),
    _f("depot_grid", "building_load", "peak_load", "Site peak load", "number", "kW", "collapsed", False),
    _f("depot_grid", "building_load", "has_solar", "On-site solar fitted", "bool", None, "collapsed", False),
    _f("depot_grid", "building_load", "solar_capacity", "On-site solar capacity", "number", "kW", "collapsed", False),
    # chargers_on_site (5)
    _f("depot_grid", "chargers_on_site", "existing_chargers", "Chargers already on site", "number", None, "collapsed", False),
    _f("depot_grid", "chargers_on_site", "existing_charger_power", "Existing charger power", "number", "kW", "collapsed", False),
    _f("depot_grid", "chargers_on_site", "charger_spaces", "Spaces reserved for chargers", "number", None, "collapsed", False),
    _f("depot_grid", "chargers_on_site", "shared_chargers", "Chargers shared with others", "bool", None, "collapsed", False),
    _f("depot_grid", "chargers_on_site", "charger_access", "Charger access", "enum", None, "collapsed", False),
]

# ---------------------------------------------------------------------------
# CHARGING (no expand; all collapsed). strategy uses only client-facing names, never technical ones (§8).
# ---------------------------------------------------------------------------
_CHARGING: List[Field] = [
    # strategy (3)
    _f("charging", "strategy", "charging_priority", "Charging priority", "enum", None, "collapsed", False),
    _f("charging", "strategy", "smart_charging", "Smart charging allowed", "bool", None, "collapsed", False),
    _f("charging", "strategy", "ready_time", "Ready time each morning", "time", None, "collapsed", False),
    # charger_types (4)
    _f("charging", "charger_types", "charger_power", "Charger power", "number", "kW", "collapsed", False),
    _f("charging", "charger_types", "connector_type", "Connector type", "enum", None, "collapsed", False),
    _f("charging", "charger_types", "chargers_count", "Number of chargers", "number", None, "collapsed", False),
    _f("charging", "charger_types", "plugs_per_charger", "Plugs per charger", "number", None, "collapsed", False),
    # time_windows (4)
    _f("charging", "time_windows", "window_start", "Charging window start", "time", None, "collapsed", False),
    _f("charging", "time_windows", "window_end", "Charging window end", "time", None, "collapsed", False),
    _f("charging", "time_windows", "daytime_charging", "Daytime charging allowed", "bool", None, "collapsed", False),
    _f("charging", "time_windows", "opportunity_charging", "Top-up charging during the day", "bool", None, "collapsed", False),
]

# ---------------------------------------------------------------------------
# ENERGY PRICES (expandable, price-facing -> plain fields may be "open")
# ---------------------------------------------------------------------------
_ENERGY_PRICES: List[Field] = [
    # electricity (5)
    _f("energy_prices", "electricity", "price_level", "Electricity price level", "enum", None, "open", True),
    _f("energy_prices", "electricity", "day_price", "Daytime electricity price", "number", "currency/kWh", "open", True),
    _f("energy_prices", "electricity", "night_price", "Night-time electricity price", "number", "currency/kWh", "open", True),
    _f("energy_prices", "electricity", "fixed_fee", "Fixed electricity fee", "number", "currency/month", "open", True),
    _f("energy_prices", "electricity", "contract_type", "Electricity contract type", "enum", None, "open", True),
    # grid_tariffs (3)
    _f("energy_prices", "grid_tariffs", "capacity_charge", "Grid capacity charge", "number", "currency/kW", "open", True),
    _f("energy_prices", "grid_tariffs", "energy_charge", "Grid energy charge", "number", "currency/kWh", "open", True),
    _f("energy_prices", "grid_tariffs", "peak_charge", "Grid peak charge", "number", "currency/kW", "open", True),
    # diesel (2)
    _f("energy_prices", "diesel", "diesel_price", "Diesel price", "number", "currency/litre", "open", True),
    _f("energy_prices", "diesel", "diesel_consumption", "Diesel use per 100 km", "number", "litre/100km", "open", True),
    # trends (2)
    _f("energy_prices", "trends", "electricity_trend", "Expected electricity price trend", "number", "%/year", "open", True),
    _f("energy_prices", "trends", "diesel_trend", "Expected diesel price trend", "number", "%/year", "open", True),
]

# ---------------------------------------------------------------------------
# WEATHER (no expand; all collapsed per §3.1 weather-physics rule)
# ---------------------------------------------------------------------------
_WEATHER: List[Field] = [
    # location (2)
    _f("weather", "location", "region", "Region", "enum", None, "collapsed", False),
    _f("weather", "location", "climate_zone", "Climate zone", "enum", None, "collapsed", False),
    # daily_records (4)
    _f("weather", "daily_records", "avg_temperature", "Average temperature", "number", "degC", "collapsed", False),
    _f("weather", "daily_records", "min_temperature", "Lowest temperature", "number", "degC", "collapsed", False),
    _f("weather", "daily_records", "max_temperature", "Highest temperature", "number", "degC", "collapsed", False),
    _f("weather", "daily_records", "wind_speed", "Average wind speed", "number", "m/s", "collapsed", False),
    # seasons (3)
    _f("weather", "seasons", "winter_length", "Winter length", "number", "months", "collapsed", False),
    _f("weather", "seasons", "cold_days", "Cold days per year", "number", "days", "collapsed", False),
    _f("weather", "seasons", "weather_year", "Weather year", "enum", None, "collapsed", False),
]

# ---------------------------------------------------------------------------
# COSTS & FINANCE (no expand; default collapsed, Bob to review)
# ---------------------------------------------------------------------------
_COSTS_FINANCE: List[Field] = [
    # purchase (5)
    _f("costs_finance", "purchase", "vehicle_price", "Vehicle purchase price", "number", "currency", "collapsed", False),
    _f("costs_finance", "purchase", "charger_price", "Charger purchase price", "number", "currency", "collapsed", False),
    _f("costs_finance", "purchase", "installation_cost", "Installation cost", "number", "currency", "collapsed", False),
    _f("costs_finance", "purchase", "grid_upgrade_cost", "Grid upgrade cost", "number", "currency", "collapsed", False),
    _f("costs_finance", "purchase", "resale_value", "Resale value", "number", "currency", "collapsed", False),
    # leasing (4)
    _f("costs_finance", "leasing", "monthly_lease", "Monthly lease cost", "number", "currency/month", "collapsed", False),
    _f("costs_finance", "leasing", "lease_term", "Lease term", "number", "months", "collapsed", False),
    _f("costs_finance", "leasing", "down_payment", "Down payment", "number", "currency", "collapsed", False),
    _f("costs_finance", "leasing", "lease_mileage_limit", "Lease mileage limit", "number", "km/year", "collapsed", False),
    # maintenance (5)
    _f("costs_finance", "maintenance", "service_cost", "Service cost per year", "number", "currency/year", "collapsed", False),
    _f("costs_finance", "maintenance", "tyre_cost", "Tyre cost per year", "number", "currency/year", "collapsed", False),
    _f("costs_finance", "maintenance", "insurance_cost", "Insurance cost per year", "number", "currency/year", "collapsed", False),
    _f("costs_finance", "maintenance", "repair_budget", "Repair budget per year", "number", "currency/year", "collapsed", False),
    _f("costs_finance", "maintenance", "downtime_cost", "Downtime cost per day", "number", "currency/day", "collapsed", False),
    # finance (6)
    _f("costs_finance", "finance", "ownership_years", "Ownership period", "enum", "years", "collapsed", False),
    _f("costs_finance", "finance", "interest_rate", "Interest rate", "number", "%/year", "collapsed", False),
    _f("costs_finance", "finance", "loan_amount", "Loan amount", "number", "currency", "collapsed", False),
    _f("costs_finance", "finance", "loan_term", "Loan term", "number", "years", "collapsed", False),
    _f("costs_finance", "finance", "annual_mileage", "Annual mileage", "number", "km/year", "collapsed", False),
    _f("costs_finance", "finance", "discount_rate", "Discount rate", "number", "%/year", "collapsed", False),
]

# ---------------------------------------------------------------------------
# POLICY & TAXES (no expand; default collapsed, Bob to review)
# ---------------------------------------------------------------------------
_POLICY_TAXES: List[Field] = [
    # taxes (4)
    _f("policy_taxes", "taxes", "registration_tax", "Registration tax", "number", "currency", "collapsed", False),
    _f("policy_taxes", "taxes", "annual_road_tax", "Annual road tax", "number", "currency/year", "collapsed", False),
    _f("policy_taxes", "taxes", "energy_tax", "Energy tax", "number", "currency/kWh", "collapsed", False),
    _f("policy_taxes", "taxes", "vat_rate", "VAT rate", "number", "%", "collapsed", False),
    # subsidies (4)
    _f("policy_taxes", "subsidies", "vehicle_subsidy", "Vehicle purchase subsidy", "number", "currency", "collapsed", False),
    _f("policy_taxes", "subsidies", "charger_subsidy", "Charger purchase subsidy", "number", "currency", "collapsed", False),
    _f("policy_taxes", "subsidies", "grid_subsidy", "Grid upgrade subsidy", "number", "currency", "collapsed", False),
    _f("policy_taxes", "subsidies", "subsidy_cap", "Subsidy cap", "number", "currency", "collapsed", False),
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


def section_counts() -> Dict[str, Dict[str, int]]:
    # per section: how many fields the registry actually holds (n) and the §5.4 expected total.
    out: Dict[str, Dict[str, int]] = {}
    for section in SECTIONS:
        n = len(fields_in_section(section.id))
        out[section.id] = {"n": n, "total": section.total}
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
