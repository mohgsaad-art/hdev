# STATUS: NEW (PR 8, Bob to review). the pure chokepoint behind GET/POST /api/report (Step 8).
#
# this is the ONE place that gathers everything a report needs and calls report.build_pdf /
# report.build_xlsx. it mirrors the other hdev/*_api.py chokepoints: a pure function of the RESOLVED
# mode (demo|real) + the requested format + the request body, returning
# (status_code, data_bytes, media_type, filename) so the thin server route only has to wrap it in a
# Response. §0: all logic lives in Python; the browser only triggers the download.
#
# where the inputs come from:
#   results    : the request body "results" (the §3.3 payload the UI already holds) when present; else
#                a fresh DEFAULT demo scenario via hdev.run_api.build_run_payload('demo', ..., log_run
#                =False) so a quote-only report does NOT consume a run number or pollute the audit log.
#   audit      : audit.source_type_tallies() - the §8-safe SOURCE-TYPE counts table.
#   scenarios  : the saved-scenario list via hdev.scenarios_api.build_scenarios_payload('demo','list')
#                (accepted by the builder for forward-compat; the report body is driven by the run).
#   open_fields: the OPEN fields with values from hdev.intake_api.build_intake_payload('demo')
#                sections[].fields (open fields are the ONLY fields the report may name, §8).
#
# REAL-MODE DEGRADATION CHOICE (documented, per the briefing): in real mode the report is NOT 404'd.
# instead it is still produced with illustrative=False and NO watermark; every unavailable results
# field renders the literal "Not yet available" (report/builder.NOT_AVAILABLE). the audit source table
# and open fields are demo-only artefacts, so in real mode they come back empty/not-available and the
# section 9 counts/fields read "Not yet available" rather than leaking the demo fixture. this keeps the
# established "Not yet available" pattern visible in real mode instead of blanking the whole report.
from typing import Any, Dict, Mapping, Optional, Tuple

import report

# the demo default levers for a report built with no caller-supplied results (mirrors scenarios_api /
# chat_api: the 6-truck municipal refuse sample case).
_DEFAULT_LEVERS = {
    "fleet_size": 6,
    "charging_priority": "lowest_cost",
    "electricity_price": "expected",
    "weather_year": "normal",
    "ownership_years": 10,
}

# the two accepted formats and their HTTP content types + attachment filenames. "excel" is accepted as
# a friendly alias of "xlsx" (the UI's "Download data" button uses it).
PDF_MEDIA_TYPE = "application/pdf"
XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

_FORMATS = {
    "pdf": (PDF_MEDIA_TYPE, "hdev-report.pdf"),
    "xlsx": (XLSX_MEDIA_TYPE, "hdev-report.xlsx"),
    "excel": (XLSX_MEDIA_TYPE, "hdev-report.xlsx"),
}


def _resolve_format(fmt: Optional[str]) -> Optional[str]:
    # normalise the requested format to 'pdf' or 'xlsx' (mapping 'excel' -> 'xlsx'); None if invalid.
    if not isinstance(fmt, str):
        return None
    key = fmt.strip().lower()
    if key == "excel":
        return "xlsx"
    if key in ("pdf", "xlsx"):
        return key
    return None


def _demo_results(body: Mapping[str, Any]) -> Dict[str, Any]:
    # the §3.3 results to report: the caller's own 'results' if it looks like a results dict, else a
    # fresh default demo run (quote-only; log_run=False so no run number is consumed).
    supplied = body.get("results")
    if isinstance(supplied, Mapping) and supplied.get("kpis"):
        return dict(supplied)

    from hdev.run_api import build_run_payload

    levers = body.get("levers")
    if not isinstance(levers, Mapping):
        levers = dict(_DEFAULT_LEVERS)
    status, payload = build_run_payload("demo", {"levers": dict(levers)}, log_run=False)
    return payload if status == 200 else {}


def _demo_open_fields() -> list:
    # the OPEN fields with values (the only fields the report may name, §8). flattened across sections.
    from hdev.intake_api import build_intake_payload

    payload = build_intake_payload("demo")
    fields = []
    for section in payload.get("sections", []):
        for field in section.get("fields", []):
            fields.append(field)
    return fields


def _demo_scenarios() -> Dict[str, Any]:
    # the saved-scenario list (forward-compat input for the builder). never raises if empty.
    from hdev.scenarios_api import build_scenarios_payload

    status, payload = build_scenarios_payload("demo", "list")
    return payload if status == 200 else {}


def build_report_response(
    mode: str,
    fmt: Optional[str],
    body: Optional[Mapping[str, Any]] = None,
) -> Tuple[int, Optional[bytes], Optional[str], Optional[str]]:
    # pure chokepoint. `mode` is already resolved (demo|real); `fmt` is the requested ?format=; `body`
    # is the parsed JSON POST body (or None for a GET). returns (status, data_bytes, media_type,
    # filename). an invalid format -> 400 with no bytes.
    resolved = _resolve_format(fmt)
    if resolved is None:
        return 400, None, None, None

    body = body or {}
    media_type, filename = _FORMATS[resolved]

    if mode == "demo":
        # the full illustrative report from the demo data.
        results = _demo_results(body)
        audit = _demo_audit()
        scenarios = _demo_scenarios()
        open_fields = _demo_open_fields()
        illustrative = True
    else:
        # REAL MODE: produce the report anyway (do NOT 404). no demo fixture is read, so results/audit/
        # open fields are empty and every section renders "Not yet available"; no watermark.
        results = {}
        if isinstance(body.get("results"), Mapping):
            results = dict(body["results"])
        audit = {}
        scenarios = {}
        open_fields = []
        illustrative = False

    if resolved == "pdf":
        data = report.build_pdf(results, audit, scenarios, open_fields, illustrative=illustrative)
    else:
        data = report.build_xlsx(results, audit, scenarios, open_fields, illustrative=illustrative)

    return 200, data, media_type, filename


def _demo_audit() -> Dict[str, Any]:
    # the §8-safe SOURCE-TYPE counts table (counts only, never a field name).
    import audit as audit_pkg

    return audit_pkg.source_type_tallies()
