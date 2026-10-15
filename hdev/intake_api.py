# STATUS: NEW (PR 3, Bob to review). builds the client-safe /api/intake payload for the DEMO intake flow.
#
# this is the ONE place that turns the sample-case fixture (demo/sample_case/extracted.json) PLUS the
# registry (src.registry, the single source of truth) into the JSON the browser sees during the §5.3
# filling animation. §0: all logic lives in Python; the UI is a dumb client that draws only what this
# payload contains - it does NO maths, hard-codes NO section names, NO counts, NO defaults and NO
# missing count. the meter widths, the header counter target, and the N/M/K in the assistant line are
# all SERVER numbers built here.
#
# §8 method-hiding, mirroring hdev/inputs_api.py and covered by tests/test_intake.py:
#   - NEVER emit `maps_to` for any field.
#   - `open` fields are the ONLY ones that may expose id + label + value + unit + source + class.
#   - `collapsed` fields are COUNTED only (into from_data/standard/missing section tallies); their
#     id/label/value/maps_to NEVER appear.
#   - `hidden` fields are neither counted nor shown.
#   - no coefficient / parameter / formula / data-source / technical-strategy name reaches the client.
#
# illustrative-values rule (§0 / §7): the sample case and every number in it is ILLUSTRATIVE. the
# payload carries `illustrative: true` so the UI can label it everywhere. fields with source
# "standard" are illustrative stand-in values sourced from the fixture itself, NOT the (not-yet-sourced,
# locked M1.1) defaults table - the mechanism (classify + tally) is real, the demo's standard values
# come from the fixture and are labelled illustrative.
#
# classification (per field, from the fixture slot's source):
#   from_data  : source startswith "file:" OR == "message"   (came from the dropped files/message)
#   standard   : source == "standard"                         (illustrative standard fill)
#   missing    : field absent from the fixture OR source == "missing"
# every registry open+collapsed field falls into exactly one class, so the three section tallies sum to
# the section total and the overall tallies sum to total_inputs (== /api/inputs total_inputs == open+collapsed).
#
# payload shape (stable contract):
#   {
#     "available": true,                 # false in real mode (demo-only endpoint)
#     "mode": "demo",
#     "illustrative": true,              # the whole sample case is illustrative; UI labels it
#     "note": str,                       # illustrative note from the fixture
#     "tool_name": "[TOOL NAME]",
#     "total_inputs": int,               # registry open+collapsed; equals /api/inputs total_inputs
#     "found": int,                      # from_data + standard, overall
#     "missing": int,                    # overall missing (registry+fixture derived, NEVER a literal)
#     "totals": {"from_data": int, "standard": int, "missing": int, "total": int},
#     "message_text": str,               # the dropped sample-case message (for the composer)
#     "sample_files": [str, ...],        # the two sample file names the UI attaches
#     "assistant": {                     # server-composed strings; the NUMBERS come from here, not JS
#         "opening": str,                # EXACT §4 opening line
#         "reading": "Reading…",
#         "found_line": "I found N of M inputs… K are missing"  # N/M/K are server numbers
#     },
#     "sections": [                      # registry order; drives the §5.3 fill animation
#       {
#         "id": str, "display_name": str,
#         "from_data": int, "standard": int, "missing": int, "total": int,
#         "found": int,                  # from_data + standard for THIS section (server-computed)
#         "cumulative_found": int,       # running overall found AFTER this section fills, in registry
#                                        #   order; the client sets the header counter to this at each
#                                        #   animation step so it never sums server numbers itself.
#                                        #   the last section's cumulative_found == payload.found.
#         "from_data_pct": int,          # meter blue-segment width % = round(from_data/total*100),
#         "standard_pct": int,           #   amber-segment width % = round(standard/total*100); both
#                                        #   are server-computed so the client only sets style.width.
#         "fields": [                    # OPEN fields only (id+label+value allowed); [] if none
#           {"id": str, "label": str, "type": str, "unit": str|None,
#            "value": any|None, "source": str|None, "class": "from_data"|"standard"|"missing",
#            "illustrative": true}
#         ]
#       }, ...
#     ],
#   }
#
# NOTE on §0 "the JS client does no maths": every number the UI renders is computed HERE. the per-
# section `found`, the `cumulative_found` running tally for the header counter, and the two meter
# segment widths (`from_data_pct` / `standard_pct`) are all server numbers; the client only assigns
# them to text / style.width and never computes a ratio or sums counts itself.
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.registry import (
    SECTIONS,
    fields_in_section,
    get_field,
    is_valid_source,
    visibility_counts,
)

from .inputs_api import TOOL_NAME

# the fixture lives at repo-root/demo/sample_case/extracted.json. this module is hdev/intake_api.py,
# so repo root is two parents up.
_FIXTURE_PATH = Path(__file__).resolve().parent.parent / "demo" / "sample_case" / "extracted.json"
_MESSAGE_PATH = _FIXTURE_PATH.parent / "message.txt"

# the two sample files the intake flow attaches, by name (Step 3 does not parse them).
SAMPLE_FILES = ("fuel_log_2025.xlsx", "collection_routes.pdf")

# EXACT §4 opening assistant line (must match character-for-character, including the en dashes).
OPENING_LINE = (
    "Hi. Drop in whatever you have – fuel logs, route lists, spreadsheets – "
    "and tell me what you want to find out. No GPS needed."
)
READING_LINE = "Reading…"

# the three classes a field can fall into.
CLASS_FROM_DATA = "from_data"
CLASS_STANDARD = "standard"
CLASS_MISSING = "missing"


def _load_fixture() -> Dict[str, Any]:
    # read the illustrative sample-case fixture. pure data file, no network, no AI.
    with _FIXTURE_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_message() -> str:
    # the dropped sample-case message the composer uses. fall back to empty if absent.
    try:
        return _MESSAGE_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _classify(source: Optional[str]) -> str:
    # map a fixture slot source to one of the three classes. anything missing/unknown -> missing.
    if source is None:
        return CLASS_MISSING
    if source == "missing":
        return CLASS_MISSING
    if source == "standard":
        return CLASS_STANDARD
    if source == "message" or source.startswith("file:"):
        return CLASS_FROM_DATA
    # any other valid source (user_edit, standard_approved) is not expected in the Step 3 fixture;
    # treat it conservatively as missing so it is never counted as found without an explicit class.
    return CLASS_MISSING


def _fixture_slots(fixture: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    # the id -> slot mapping from the fixture, validated against the registry and the source vocab so a
    # bad fixture fails loudly here rather than leaking a bad value to the client.
    slots = fixture.get("fields", {})
    for fid, slot in slots.items():
        if get_field(fid) is None:
            raise ValueError(f"fixture references unknown registry field id: {fid}")
        src = slot.get("source")
        if not is_valid_source(src):
            raise ValueError(f"fixture field {fid} has invalid source: {src!r}")
    return slots


def _empty_tally() -> Dict[str, int]:
    return {CLASS_FROM_DATA: 0, CLASS_STANDARD: 0, CLASS_MISSING: 0, "total": 0}


def _pct(part: int, whole: int) -> int:
    # meter segment width as a whole-number percent of the section total. computed server-side so the
    # client only assigns the result to style.width (§0: the JS does no maths). zero total -> 0%.
    if not whole:
        return 0
    return round((part / whole) * 100)


def build_intake_payload(mode: str) -> Dict[str, Any]:
    # the single chokepoint for /api/intake. the caller passes the resolved mode (demo|real). in real
    # mode the demo fixture is NOT exposed - real intake is a later step. pure function otherwise:
    # reads the fixture file only, no network, no AI provider.
    if mode != "demo":
        # real mode: the demo sample case must not leak. a clear not-available payload.
        return {
            "available": False,
            "mode": mode,
            "reason": "Intake is only available in demo mode in this build.",
        }

    fixture = _load_fixture()
    slots = _fixture_slots(fixture)

    # per-section tallies and open-field views, in registry order. collapsed fields are COUNTED only.
    sections: List[Dict[str, Any]] = []
    overall = _empty_tally()

    for section in SECTIONS:
        tally = _empty_tally()
        open_fields: List[Dict[str, Any]] = []

        for field in fields_in_section(section.id):
            if field.visibility == "hidden":
                # §8: hidden fields are neither counted nor shown. skip entirely.
                continue

            slot = slots.get(field.id)
            source = slot.get("source") if slot else None
            cls = _classify(source)

            # count every open+collapsed field into exactly one class.
            tally[cls] += 1
            tally["total"] += 1

            if field.visibility == "open":
                # open fields may expose id + label + value + unit + source + class. value/source are
                # None when the field is missing from the fixture.
                open_fields.append(
                    {
                        "id": field.id,
                        "label": field.label,
                        "type": field.type,
                        "unit": field.unit,
                        "value": slot.get("value") if slot else None,
                        "source": source,
                        "class": cls,
                        # every demo value is illustrative; flagged per-field so the UI can label it.
                        "illustrative": True,
                    }
                )
            # collapsed fields: counted in `tally` above, never named/valued here.

        # roll the section tally into the overall totals.
        for key in (CLASS_FROM_DATA, CLASS_STANDARD, CLASS_MISSING, "total"):
            overall[key] += tally[key]

        # per-section and running numbers, all computed here so the client never does maths. the
        # section `found` is from_data+standard; `cumulative_found` is the overall found AFTER this
        # section fills (registry order), so the UI can set the header counter to a server number at
        # each animation step without summing. the two meter widths are percentages of the section
        # total.
        section_found = tally[CLASS_FROM_DATA] + tally[CLASS_STANDARD]
        cumulative_found = overall[CLASS_FROM_DATA] + overall[CLASS_STANDARD]

        sections.append(
            {
                "id": section.id,
                "display_name": section.display_name,
                "from_data": tally[CLASS_FROM_DATA],
                "standard": tally[CLASS_STANDARD],
                "missing": tally[CLASS_MISSING],
                "total": tally["total"],
                "found": section_found,
                "cumulative_found": cumulative_found,
                "from_data_pct": _pct(tally[CLASS_FROM_DATA], tally["total"]),
                "standard_pct": _pct(tally[CLASS_STANDARD], tally["total"]),
                "fields": open_fields,
            }
        )

    # overall numbers. found = from_data + standard; missing is registry+fixture derived (NEVER literal).
    found = overall[CLASS_FROM_DATA] + overall[CLASS_STANDARD]
    missing = overall[CLASS_MISSING]
    total_inputs = overall["total"]

    # sanity: total_inputs must equal the registry open+collapsed total so /api/intake agrees with
    # /api/inputs. this is a construction-time guard, not a client-visible value.
    reg = visibility_counts()
    assert total_inputs == reg["open"] + reg["collapsed"], "intake total disagrees with registry"

    # server-composed assistant strings. the NUMBERS come from here; the UI only renders them.
    found_line = f"I found {found} of {total_inputs} inputs… {missing} are missing"

    return {
        "available": True,
        "mode": mode,
        # the whole sample case is illustrative; the UI labels it everywhere these appear.
        "illustrative": bool(fixture.get("illustrative", True)),
        "note": fixture.get("note", ""),
        "tool_name": TOOL_NAME,
        "total_inputs": total_inputs,
        "found": found,
        "missing": missing,
        "totals": {
            CLASS_FROM_DATA: overall[CLASS_FROM_DATA],
            CLASS_STANDARD: overall[CLASS_STANDARD],
            CLASS_MISSING: overall[CLASS_MISSING],
            "total": total_inputs,
        },
        "message_text": _load_message(),
        "sample_files": list(SAMPLE_FILES),
        "assistant": {
            "opening": OPENING_LINE,
            "reading": READING_LINE,
            "found_line": found_line,
        },
        "sections": sections,
    }
