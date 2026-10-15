# STATUS: NEW (PR 1, Bob to review). Field structure for the input registry.
# a Field is pure metadata that tells the UI how to draw one input. shape is from user §3.1.
# client-facing labels obey §8 method-hiding: plain words only, never a parameter/coefficient/formula/
# data-source/technical-strategy name.
#
# `maps_to` is INTERNAL metadata: it names the engine input / pipeline step / function argument / source
# document a field feeds. it is NEVER shown to the client, so it is NOT subject to the §8 plain-words
# rule that governs `label`; it MAY name engine args, pipeline steps (design.md A->O), or source docs.
# where the real target is a 🔒 locked / not-yet-decided item, maps_to SAYS SO ("pending ...") rather
# than inventing a target. every field MUST carry a non-empty maps_to or construction fails loudly.
from dataclasses import dataclass
from typing import Optional

# the 8 sections from §5.4, in order
SECTION_IDS = (
    "operation",
    "vehicles",
    "depot_grid",
    "charging",
    "energy_prices",
    "weather",
    "costs_finance",
    "policy_taxes",
)

# allowed field types from user §3.1
FIELD_TYPES = ("time", "number", "enum", "text", "bool")

# allowed visibility from user §3.1
# open:      label and value shown when the section is expanded
# collapsed: counted in section/subgroup totals, never listed by name in the UI
# hidden:    internal, never counted or shown
VISIBILITY_VALUES = ("open", "collapsed", "hidden")


@dataclass(frozen=True)
class Field:
    id: str                     # dotted id, e.g. "operation.schedule.shift_end"
    section: str                # one of SECTION_IDS
    subgroup: str               # subgroup name within the section (§5.4)
    label: str                  # plain client-facing label, §8 safe
    type: str                   # one of FIELD_TYPES
    unit: Optional[str]         # unit string or None
    visibility: str             # one of VISIBILITY_VALUES
    editable_in_demo: bool      # may the demo user edit this field
    maps_to: str                # INTERNAL: engine input / pipeline step / source doc this field feeds

    def __post_init__(self):
        # constrain the enum-like fields so a typo in the registry fails loudly
        if self.section not in SECTION_IDS:
            raise ValueError(f"unknown section: {self.section}")
        if self.type not in FIELD_TYPES:
            raise ValueError(f"unknown field type: {self.type}")
        if self.visibility not in VISIBILITY_VALUES:
            raise ValueError(f"unknown visibility: {self.visibility}")
        # a field with no mapping is a bug (or mock-up padding): fail loudly so it cannot slip in.
        if not self.maps_to or not self.maps_to.strip():
            raise ValueError(f"field {self.id} is missing maps_to")
