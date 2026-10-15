# STATUS: NEW (PR 1, Bob to review). The validator: checks every lever change and every patch.
#
# scope rules it honours:
#   - user §3.2: the validator REJECTS any lever or value not in LEVERS. an open + editable_in_demo
#     registry field is ALSO an allowed lever target.
#   - requirements §9.4 / M6.14: a change-set write to a slot with locked=True is rejected. this is the
#     lock-flag check only; there is NO role system here (that is out of scope and partly 🔒).
#   - requirements §9.6: sanity checks are physical/logical ONLY - non-negative where physical, a
#     fraction/share within 0..1 where applicable, and min<=max. there are NO invented plausibility
#     ranges: an unusual-but-physical value must be ACCEPTED.
#   - §8 method-hiding: every error message below uses plain words only. no parameter/coefficient/
#     formula/data-source/technical-strategy names, and no collapsed/hidden field names.
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from ..registry import (
    LEVERS,
    FLEET_SIZE_MAX_FROM_PROJECT,
    get_field,
    editable_demo_fields,
)


@dataclass
class ValidationResult:
    ok: bool
    error: Optional[str] = None  # plain-language message when ok is False, §8 safe

    def __bool__(self) -> bool:
        return self.ok


def _ok() -> ValidationResult:
    return ValidationResult(True)


def _fail(message: str) -> ValidationResult:
    return ValidationResult(False, message)


# a value is treated as a share/fraction (must sit within 0..1, physical, §9.6) when the field id ends
# in one of these plain markers. no fraction fields exist in the PR 1 registry yet, but future fields
# (e.g. a charge level / state of charge) will match without needing a hand-maintained id list.
# none of these are exposed to the client by name; this is internal only.
_FRACTION_ID_SUFFIXES = ("state_of_charge", "fraction", "share", "ratio")


def _is_fraction_field(field) -> bool:
    local = field.id.rsplit(".", 1)[-1]
    return any(local == suffix or local.endswith("_" + suffix) for suffix in _FRACTION_ID_SUFFIXES)

# field types whose numeric value cannot be negative on physical/logical grounds (§9.6).
# a plain count, a duration, a distance, a capacity, a price and so on are all non-negative.
_NON_NEGATIVE_UNIT_HINTS = (
    "km", "kg", "kW", "kWh", "m", "m2", "m/s", "months", "years", "days",
    "litre", "litre/100km", "currency", "%",
)


# ---------------------------------------------------------------------------
# lever validation (user §3.2)
# ---------------------------------------------------------------------------
def validate_lever(key: str, value: Any, project: Optional[Mapping[str, Any]] = None) -> ValidationResult:
    # a lever target is EITHER one of the fixed LEVERS keys, OR an open + editable_in_demo registry field.
    if key in LEVERS:
        return _validate_fixed_lever(key, value, project)

    editable_ids = {f.id: f for f in editable_demo_fields()}
    if key in editable_ids:
        return _validate_field_value(editable_ids[key], value)

    return _fail(f"'{key}' is not something you can change here.")


def _validate_fixed_lever(key: str, value: Any, project: Optional[Mapping[str, Any]]) -> ValidationResult:
    spec = LEVERS[key]
    if spec["type"] == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            return _fail(f"'{key}' needs a whole number.")
        if value < spec["min"]:
            return _fail(f"'{key}' must be at least {spec['min']}.")
        # max may be "from project": resolve it from the project when one is given, else only enforce min.
        max_spec = spec["max"]
        if max_spec == FLEET_SIZE_MAX_FROM_PROJECT:
            if project is not None and "fleet_size" in project:
                project_max = project["fleet_size"]
                if isinstance(project_max, int) and value > project_max:
                    return _fail(f"'{key}' cannot be more than {project_max}.")
        elif isinstance(max_spec, int) and value > max_spec:
            return _fail(f"'{key}' cannot be more than {max_spec}.")
        return _ok()

    if spec["type"] == "enum":
        if value not in spec["options"]:
            return _fail(f"'{value}' is not one of the choices for '{key}'.")
        return _ok()

    return _fail(f"'{key}' cannot be validated.")


# ---------------------------------------------------------------------------
# patch validation (user §3.1 slot write path)
# ---------------------------------------------------------------------------
def validate_patch(patch: Mapping[str, Any]) -> ValidationResult:
    # a patch is {"field": <field id>, "value": <new value>, optional "locked": <current lock flag>}.
    field_id = patch.get("field")
    if not field_id:
        return _fail("This change does not say which input it applies to.")

    field = get_field(field_id)
    if field is None:
        return _fail("This input is not one the tool recognises.")

    # lock-flag enforcement (§9.4 / M6.14): a write to a locked slot is rejected.
    if patch.get("locked", False):
        return _fail("This value is locked and cannot be changed here.")

    return _validate_field_value(field, patch.get("value"))


# ---------------------------------------------------------------------------
# field-type + physical/logical sanity (requirements §9.6)
# ---------------------------------------------------------------------------
def _validate_field_value(field, value: Any) -> ValidationResult:
    # type check first
    if field.type == "bool":
        if not isinstance(value, bool):
            return _fail(f"'{field.label}' must be yes or no.")
        return _ok()

    if field.type == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return _fail(f"'{field.label}' must be a number.")
        return _sanity_number(field, float(value))

    if field.type == "enum":
        if not isinstance(value, (str, int)):
            return _fail(f"'{field.label}' must be a choice from the list.")
        return _ok()

    if field.type in ("text", "time"):
        if not isinstance(value, str):
            return _fail(f"'{field.label}' must be text.")
        return _ok()

    return _fail(f"'{field.label}' cannot be validated.")


def _sanity_number(field, value: float) -> ValidationResult:
    # §9.6: physical/logical checks ONLY. no invented plausibility ranges.
    # a share/fraction must sit within 0..1.
    if _is_fraction_field(field):
        if value < 0.0 or value > 1.0:
            return _fail(f"'{field.label}' must be between 0 and 1.")
        return _ok()

    # otherwise, reject negatives only where a negative makes no physical sense (count, distance,
    # capacity, price, duration ...). temperatures and trends CAN be negative, so they are not here.
    if field.unit in _NON_NEGATIVE_UNIT_HINTS and value < 0.0:
        return _fail(f"'{field.label}' cannot be negative.")

    # anything else, including an unusual-but-physical value, is accepted (§9.6).
    return _ok()


def validate_range(low: Any, high: Any, label: str = "range") -> ValidationResult:
    # generic min<=max check (§9.6), used where a field pairs a low and a high value.
    if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
        return _fail(f"'{label}' must use numbers.")
    if low > high:
        return _fail(f"'{label}' has its lowest value above its highest value.")
    return _ok()
