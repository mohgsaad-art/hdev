# STATUS: NEW (PR 7, Bob to review). the pure chokepoint behind GET /api/audit (Step 7).
#
# this is the ONE place that builds the §5.6 Audit-trail payload: the "Where every input came from"
# source-type table (SOURCE TYPES + COUNTS ONLY, §8) plus the §3.4 run log newest-first. it mirrors
# hdev/intake_api.py and hdev/run_api.py: a pure function of the RESOLVED mode (demo|real) returning
# (status_code, payload) so the thin server route only wraps it in a JSONResponse.
#
# payload shape:
#   {
#     "available": true,
#     "mode": "demo",
#     "source_table": {"rows": [{source_type, count, status}, ...], "total": int},
#     "note": "Every value can be changed. Changes are logged with who and when.",
#     "run_log": [ §3.4 entries, newest-first ]
#   }
#
# REAL-MODE DEGRADATION CHOICE (documented): the audit source table is derived from the DEMO intake
# tallies (demo/sample_case) and the run log is a demo-only artefact, so in real mode there is nothing
# §8-safe to show yet. this endpoint therefore follows the SAME not-yet-available pattern as
# run_api/intake_api: {available:false, mode, reason} with 404. (the real engine + real intake are
# Steps 9/10; the audit trail becomes real alongside them.)
from typing import Any, Dict, Tuple

import audit

# the EXACT §5.6 audit note (plain words; names no field).
AUDIT_NOTE = "Every value can be changed. Changes are logged with who and when."


def build_audit_payload(mode: str) -> Tuple[int, Dict[str, Any]]:
    # pure chokepoint. `mode` is already resolved (demo|real).
    if mode != "demo":
        return 404, {
            "available": False,
            "mode": mode,
            "reason": "The audit trail is only available in demo mode in this build.",
        }

    source_table = audit.source_type_tallies()      # SOURCE TYPES + COUNTS ONLY (§8)
    run_log = audit.list_entries()                   # §3.4 entries, newest-first

    return 200, {
        "available": True,
        "mode": mode,
        "source_table": source_table,
        "note": AUDIT_NOTE,
        "run_log": run_log,
    }
