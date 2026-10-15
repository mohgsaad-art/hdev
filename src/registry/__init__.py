# STATUS: NEW (PR 1, Bob to review). Public API for the input registry package.
#
# this package is the single source of truth for every input the tool knows about (user §3.1/§3.2/§5.4).
# notable 🔒 open items touched here:
#   - M6.7: the Slot shape {value, unit, source, date, label, provided_by, locked, version} is LOCKED and
#     may change, so it is wrapped in one Slot class (slot.py). do not treat the shape as final.
# no physics default VALUES live in this package (defaults are the separate later task M1.1); every slot
# starts empty. client-facing labels obey §8 method-hiding. owner is referred to only as "Bob".
from .slot import (
    Slot,
    SOURCE_VALUES,
    SOURCE_FILE_PREFIX,
    PROVIDED_BY_VOCAB,
    is_valid_source,
)
from .fields import (
    Field,
    SECTION_IDS,
    FIELD_TYPES,
    VISIBILITY_VALUES,
)
from .registry import (
    Section,
    SECTIONS,
    FIELDS,
    SUBGROUPS,
    get_field,
    has_field,
    get_section,
    fields_in_section,
    fields_in_subgroup,
    section_counts,
    visibility_counts,
    listable_fields,
    counted_only_fields,
    editable_demo_fields,
)
from .levers import (
    LEVERS,
    FLEET_SIZE_MAX_FROM_PROJECT,
    allowed_lever_keys,
    is_lever_key,
)

__all__ = [
    "Slot",
    "SOURCE_VALUES",
    "SOURCE_FILE_PREFIX",
    "PROVIDED_BY_VOCAB",
    "is_valid_source",
    "Field",
    "SECTION_IDS",
    "FIELD_TYPES",
    "VISIBILITY_VALUES",
    "Section",
    "SECTIONS",
    "FIELDS",
    "SUBGROUPS",
    "get_field",
    "has_field",
    "get_section",
    "fields_in_section",
    "fields_in_subgroup",
    "section_counts",
    "visibility_counts",
    "listable_fields",
    "counted_only_fields",
    "editable_demo_fields",
    "LEVERS",
    "FLEET_SIZE_MAX_FROM_PROJECT",
    "allowed_lever_keys",
    "is_lever_key",
]
