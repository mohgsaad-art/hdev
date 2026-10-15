# STATUS: NEW (PR 7, Bob to review). the §5.6 "Where every input came from" SOURCE-TYPE tallies (Step 7).
#
# this builds the audit source table: a list of {source_type, count, status} rows grouped by source
# TYPE, plus a total. §8 HARD RULE: SOURCE TYPES + COUNTS ONLY. a registry field id or label NEVER
# appears here. the UI draws only these rows, so a client sees "fuel_log_2025.xlsx: 7 inputs" and
# never which field came from the file.
#
# where the numbers come from: hdev.intake_api.build_intake_payload('demo') already classifies every
# open+collapsed registry field by the fixture's source into from_data/standard/missing and exposes the
# per-field source on OPEN fields. this module reads that payload and GROUPS the counts by source TYPE:
#   - each file source  (source == 'file:<name>')  -> one row per file name  (status 'From your files')
#   - the message source (source == 'message')      -> one row 'Your message' (status 'From your message')
#   - the standard source (source == 'standard')    -> one row 'Standard Danish values' (status 'Standard')
#   - missing/absent                                -> one row 'Missing' (status 'Not yet provided')
#
# collapsed fields: the intake payload exposes a per-field `source` only on OPEN fields, but it counts
# ALL open+collapsed fields into the section/overall from_data/standard/missing tallies. to keep the
# source table complete AND §8-safe (no collapsed field names), we:
#   - derive the per-FILE breakdown from the OPEN fields' `source` strings (file names only, never field
#     labels), and
#   - reconcile the message / standard / missing rows against the overall intake TOTALS so the counts
#     always sum to the registry open+collapsed total even though collapsed field sources are not
#     individually exposed. the collapsed from_data count that is not attributable to a named file is
#     folded into a generic 'Your files' row so no count is lost and no field is named.
#
# purity: pure function of the intake payload (which only reads the demo fixture + registry). no
# network, no AI provider.
from typing import Any, Dict, List

from hdev.intake_api import build_intake_payload

# the plain-word status labels per source type (the audit table's status column).
_STATUS_FROM_FILES = "From your files"
_STATUS_FROM_MESSAGE = "From your message"
_STATUS_STANDARD = "Standard"
_STATUS_MISSING = "Not yet provided"

# the client-facing row labels for the non-file source types.
_LABEL_MESSAGE = "Your message"
_LABEL_STANDARD = "Standard Danish values"
_LABEL_MISSING = "Missing"
# a generic bucket for from_data inputs that came from a file but whose file name is not exposed (i.e.
# collapsed fields counted into from_data). never names a field; names only "your files".
_LABEL_FILES_GENERIC = "Your files"


def _file_label(source: str) -> str:
    # turn a 'file:<name>' source into the bare file name used as the row label. never a field id.
    return source[len("file:"):] if source.startswith("file:") else source


def source_type_tallies() -> Dict[str, Any]:
    # build the §8-safe source table. returns {"rows": [{source_type, count, status}...], "total": int}.
    # rows are ordered: each file (alphabetical by name), then message, then standard, then missing, so
    # the UI order is stable.
    payload = build_intake_payload("demo")
    totals = payload.get("totals", {}) if isinstance(payload, dict) else {}
    overall_from_data = int(totals.get("from_data", 0))
    overall_standard = int(totals.get("standard", 0))
    overall_missing = int(totals.get("missing", 0))

    # per-file and message counts from the OPEN fields' source strings (file names only; §8-safe).
    file_counts: Dict[str, int] = {}
    message_count = 0
    for section in payload.get("sections", []):
        for field in section.get("fields", []):
            source = field.get("source")
            if not isinstance(source, str):
                continue
            if source.startswith("file:"):
                name = _file_label(source)
                file_counts[name] = file_counts.get(name, 0) + 1
            elif source == "message":
                message_count += 1

    # the from_data total covers both file and message sources. anything in from_data not attributed to
    # a named file or the message (i.e. collapsed from_data fields) is folded into a generic files row so
    # the counts reconcile with the overall total WITHOUT naming any field.
    named_file_total = sum(file_counts.values())
    attributed_from_data = named_file_total + message_count
    generic_files = max(0, overall_from_data - attributed_from_data)

    rows: List[Dict[str, Any]] = []

    # one row per named file, alphabetical for a stable UI order.
    for name in sorted(file_counts):
        rows.append({"source_type": name, "count": file_counts[name], "status": _STATUS_FROM_FILES})

    # a generic 'Your files' row only if some from_data count was not attributable to a named file.
    if generic_files:
        rows.append({"source_type": _LABEL_FILES_GENERIC, "count": generic_files, "status": _STATUS_FROM_FILES})

    # the message row (only if any input came from the message).
    if message_count:
        rows.append({"source_type": _LABEL_MESSAGE, "count": message_count, "status": _STATUS_FROM_MESSAGE})

    # standard + missing rows reconcile against the overall intake totals (collapsed fields of these
    # classes are not individually exposed, so the overall totals are authoritative here).
    if overall_standard:
        rows.append({"source_type": _LABEL_STANDARD, "count": overall_standard, "status": _STATUS_STANDARD})
    if overall_missing:
        rows.append({"source_type": _LABEL_MISSING, "count": overall_missing, "status": _STATUS_MISSING})

    total = sum(row["count"] for row in rows)
    return {"rows": rows, "total": total}


def rows_contain_no_field_names() -> bool:
    # TEST-FRIENDLY GUARD (§8). assert that NO source-table row label equals a registry field id or
    # label. returns True when the table is clean. used by the audit tests to prove the §8 rule.
    from src.registry import FIELDS

    forbidden = set()
    for field in FIELDS:
        forbidden.add(field.id)
        if getattr(field, "label", None):
            forbidden.add(field.label)

    table = source_type_tallies()
    for row in table["rows"]:
        if row["source_type"] in forbidden:
            return False
    return True
