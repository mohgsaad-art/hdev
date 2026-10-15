# STATUS: NEW (PR 1, Bob to review). LEVERS: the only things the assistant and the scenario bar may change.
# shape and values are verbatim from user §3.2. the validator rejects any lever or value not in this list.
#
# §8 method-hiding note: charging_priority exposes only the three CLIENT-FACING names
# (lowest_cost / grid_friendly / ready_earliest). the internal mapping of those three to the technical
# charging setpoints lives in a later runner/levers task and NEVER leaves the server. do not add the
# technical names here.
from typing import Any

# "from project" means the max is resolved at validation time from the project, not a fixed number.
FLEET_SIZE_MAX_FROM_PROJECT = "from project"

LEVERS = {
    "fleet_size":        {"type": "int",  "min": 1, "max": FLEET_SIZE_MAX_FROM_PROJECT},
    "charging_priority": {"type": "enum", "options": ["lowest_cost", "grid_friendly", "ready_earliest"]},
    "electricity_price": {"type": "enum", "options": ["low", "expected", "high"]},
    "weather_year":      {"type": "enum", "options": ["normal", "cold_winter"]},
    "ownership_years":   {"type": "enum", "options": [8, 10, 12]},
}


def allowed_lever_keys() -> tuple:
    # the fixed lever keys from §3.2
    return tuple(LEVERS.keys())


def is_lever_key(key: str) -> bool:
    return key in LEVERS
