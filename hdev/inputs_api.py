# STATUS: NEW (PR 2, Bob to review). builds the client-safe /api/inputs payload from the registry.
#
# this is the ONE place that turns the registry (src.registry, the single source of truth) into the
# JSON the browser sees. §0: all logic lives in Python; the UI is a dumb client that draws only what
# this payload contains. nothing about sections/counts is computed in JS.
#
# §8 method-hiding rules, enforced here and covered by tests/test_server.py:
#   - NEVER emit `maps_to` for any field (it names engine args / pipeline steps / source docs).
#   - `open` fields are the ONLY ones that may expose id + label.
#   - `collapsed` fields are COUNTED only: emit a count, never their id/label/maps_to.
#   - `hidden` fields are neither counted nor shown; they never appear at all.
#   - no coefficient / parameter / formula / data-source / technical-strategy names reach the client.
#
# counts are REGISTRY-DERIVED (section_counts(), visibility_counts()): never a hard-coded 112 or any
# §5.4 mock-up number. the UI header "N of <total> inputs" reads `total_inputs` from here.
#
# payload shape (stable contract; Steps 3-7 extend it without breaking these keys):
#   {
#     "mode": "demo" | "real",            # from HDEV_MODE; UI shows the demo pill when "demo"
#     "tool_name": "[TOOL NAME]",         # literal placeholder string shown in the UI (never a brand)
#     "filled_inputs": int,               # how many inputs are filled; 0 in the shell (nothing filled
#                                         # yet). server-driven so the UI never invents the count;
#                                         # later steps update it server-side.
#     "total_inputs": int,                # registry-derived open+collapsed total (hidden excluded)
#     "visibility_totals": {"open": int, "collapsed": int},   # overall, hidden deliberately omitted
#     "sections": [
#       {
#         "id": str, "display_name": str, "expandable": bool,
#         "count": int,                   # total fields in the section (open + collapsed)
#         "open_count": int, "collapsed_count": int,
#         "subgroups": [
#           {"name": str, "count": int,   # field count for the subgroup (open + collapsed)
#            # `fields` lists ONLY open fields (id + label). collapsed fields appear only in `count`.
#            "fields": [{"id": str, "label": str, "type": str, "unit": str|None,
#                        "editable_in_demo": bool}, ...]}
#         ],
#       }, ...
#     ],
#   }
# NOTE: Steps 3-7 may add per-field value/source slots to the open-field dicts and a top-level project
#       block; they must keep the §8 guarantees above (never add maps_to / collapsed names / hidden fields).
from typing import Any, Dict, List, Optional

from src.registry import (
    SECTIONS,
    fields_in_subgroup,
    listable_fields,
    section_counts,
    visibility_counts,
)

# literal tool-name placeholder shown in the UI (never a brand name). lives server-side so the client
# does not hard-code it.
TOOL_NAME = "[TOOL NAME]"

# valid HDEV_MODE values; demo is the default.
MODES = ("demo", "real")
DEFAULT_MODE = "demo"


def normalize_mode(raw: Optional[str]) -> str:
    # map the HDEV_MODE env var to a known mode, defaulting to demo for anything missing/unknown.
    if raw is None:
        return DEFAULT_MODE
    value = raw.strip().lower()
    return value if value in MODES else DEFAULT_MODE


def _open_field_dict(field) -> Dict[str, Any]:
    # client-safe view of a single OPEN field: id + label are allowed here, maps_to is NOT emitted.
    return {
        "id": field.id,
        "label": field.label,
        "type": field.type,
        "unit": field.unit,
        "editable_in_demo": field.editable_in_demo,
    }


def _subgroup_dict(section_id: str, subgroup: str, counts: Dict[str, Any]) -> Dict[str, Any]:
    # one subgroup: its registry-derived field count plus the list of its OPEN fields only.
    # collapsed fields in the subgroup are reflected in `count` but never named.
    open_fields = [
        _open_field_dict(f)
        for f in fields_in_subgroup(section_id, subgroup)
        if f.visibility == "open"
    ]
    return {
        "name": subgroup,
        "count": counts["subgroups"][subgroup],
        "fields": open_fields,
    }


def build_inputs_payload(mode: str = DEFAULT_MODE) -> Dict[str, Any]:
    # walk the registry and return the client-safe /api/inputs dict. pure function: no I/O, no env read
    # (the caller passes the already-resolved mode so this stays testable and side-effect free).
    counts = section_counts()
    totals = visibility_counts()  # whole-registry {open, collapsed, hidden}

    sections: List[Dict[str, Any]] = []
    for section in SECTIONS:
        section_vis = visibility_counts(section.id)
        sections.append(
            {
                "id": section.id,
                "display_name": section.display_name,
                "expandable": section.expandable,
                "count": counts[section.id]["n"],
                "open_count": section_vis["open"],
                "collapsed_count": section_vis["collapsed"],
                "subgroups": [
                    _subgroup_dict(section.id, name, counts[section.id])
                    for name in section.subgroups
                ],
            }
        )

    return {
        "mode": mode if mode in MODES else DEFAULT_MODE,
        "tool_name": TOOL_NAME,
        # nothing is filled in the shell yet, so this is a literal 0. it is emitted server-side so the
        # dumb client renders the "filled" counter from the payload instead of inventing it; later
        # steps update this count server-side without touching the client.
        "filled_inputs": 0,
        # registry-derived total: open + collapsed (hidden is never counted). NOT a literal.
        "total_inputs": totals["open"] + totals["collapsed"],
        "visibility_totals": {"open": totals["open"], "collapsed": totals["collapsed"]},
        "sections": sections,
    }
