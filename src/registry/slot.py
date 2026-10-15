# STATUS: NEW (PR 1, Bob to review). Slot class for the input registry.
# The slot shape {value, unit, source, date, label, provided_by, locked, version} is LOCKED as 🔒 M6.7
# (requirements §9.1 + user §3.1): it is still undecided and MAY CHANGE. that is exactly WHY the whole
# shape is wrapped in this one class, so a future change happens in one place only.
# no physics default VALUES live here (defaults are a separate later task M1.1); a fresh slot is empty.
from dataclasses import dataclass, field, asdict
from datetime import date as _date
from typing import Any, Optional

# source is one of these, verbatim from user §3.1.
# "file:<filename>" is a prefix family, every other member is a fixed string.
SOURCE_FILE_PREFIX = "file:"
SOURCE_VALUES = (
    "message",         # value came from the client's free-text message
    "user_edit",       # value typed/edited by the user in the UI
    "standard",        # value filled from a standard source (not yet client-approved)
    "standard_approved",  # standard value the client has approved
    "missing",         # no value yet
)

# provided_by vocabulary from requirements §9.1. this is OPEN-ENDED: new providers may appear,
# so the validator treats it as a hint set, not a closed enum.
PROVIDED_BY_VOCAB = ("client", "OEM", "CPO", "aggregator", "consultant", "Bob")


def is_valid_source(source: Optional[str]) -> bool:
    # accepts the fixed set and any "file:<filename>" string
    if not isinstance(source, str):
        return False
    if source.startswith(SOURCE_FILE_PREFIX) and len(source) > len(SOURCE_FILE_PREFIX):
        return True
    return source in SOURCE_VALUES


@dataclass
class Slot:
    # one stored value for one registry field. shape is 🔒 M6.7, see header.
    value: Any = None               # the stored value, None until something fills it
    unit: Optional[str] = None      # unit string or None (unitless / enum / text)
    source: str = "missing"         # where the value came from, see SOURCE_VALUES
    date: Optional[_date] = None    # when the value was set
    label: Optional[str] = None     # plain client-facing label for this value, §8 safe
    provided_by: Optional[str] = None  # who provided it, open vocab, see PROVIDED_BY_VOCAB
    locked: bool = False            # if True, a change-set write is rejected (§9.4 / M6.14)
    version: int = 1                # bumped on each accepted write

    def to_dict(self) -> dict:
        # plain dict view of the 8 fields, handy for the api layer later
        return asdict(self)

    @classmethod
    def empty(cls) -> "Slot":
        # a fresh, unfilled slot: no value, source "missing", unlocked, version 1
        return cls()
