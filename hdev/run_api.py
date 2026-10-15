# STATUS: NEW (PR 4, Bob to review). the pure chokepoint behind POST /api/run (Step 4).
#
# this is the ONE place that turns a scenario request (mode + body of levers) into a results payload.
# it mirrors hdev/intake_api.py: a pure function of the RESOLVED mode (demo|real) so it is unit-testable
# without a socket. §0: all logic lives in Python; the browser is a dumb client that renders whatever
# JSON this returns and does no maths.
#
# behaviour by mode:
#   - real mode: return a not-yet-available payload {available: False, mode, reason} mirroring
#     intake_api's shape. the real runner is Step 9; demo.demo_engine is NEVER called in real mode.
#   - demo mode: validate every lever in the body via src.validate.validate_lever (which already rejects
#     any lever/value not in LEVERS, any out-of-range value, and accepts the open+editable_in_demo
#     field operation.schedule.shift_end). on the FIRST failure, return an error payload carrying the
#     validator's plain-language message (§8-safe). on success, call demo.demo_engine.run_scenario and
#     return the §3.3 results JSON (illustrative:true, mode:'demo').
#
# the handler returns (status_code, payload) so the thin server route in hdev/server.py only has to wrap
# it in a JSONResponse - keeping the HTTP mapping in one obvious place while the logic stays pure.
from typing import Any, Dict, Mapping, Optional, Tuple

from src.validate import validate_lever


def build_run_payload(
    mode: str,
    body: Optional[Mapping[str, Any]],
    log_run: bool = True,
) -> Tuple[int, Dict[str, Any]]:
    # pure chokepoint. `mode` is already resolved (demo|real). `body` is the parsed JSON request body;
    # its "levers" key (or the body itself) holds the lever map, and an optional "project" key gives
    # the current project context used for lever bounds (e.g. fleet_size max "from project").
    #
    # `log_run` controls the Step 7 run-counter side effect. a REAL run (the scenario-bar /api/run, an
    # assistant rerun button, a shift-end edit) allocates one run number and appends one §3.4 run-log
    # entry (log_run=True, the default). a QUOTE-ONLY rerun that only needs a results dict to read a
    # number from (chat_api._base_results for no-rerun replies) passes log_run=False so it does NOT
    # consume a run number or append to the audit trail - only genuine runs are counted and logged.
    body = body or {}

    if mode != "demo":
        # real mode: running is not available yet. mirror intake_api's not-available payload. the real
        # pipeline (runner.run) arrives in Step 9; demo_engine must NOT run here.
        return 404, {
            "available": False,
            "mode": mode,
            "reason": "Running is only available in demo mode in this build.",
        }

    project = body.get("project") if isinstance(body.get("project"), Mapping) else {}
    levers = body.get("levers")
    if not isinstance(levers, Mapping):
        # allow the levers to be passed at the top level too (demo convenience); drop reserved keys.
        levers = {k: v for k, v in body.items() if k not in ("levers", "project")}

    # validate every submitted lever. the validator rejects anything not in LEVERS or out of range and
    # accepts the open+editable field operation.schedule.shift_end. surface the FIRST plain-language
    # error with a 400 and NO results.
    for key, value in levers.items():
        result = validate_lever(key, value, project)
        if not result:
            return 400, {
                "mode": mode,
                "ok": False,
                "error": result.error,
            }

    # all levers valid -> run the illustrative demo engine. imported here (not at module load) so the
    # chokepoint has no import-time dependency on the demo package.
    from demo.demo_engine import run_scenario

    results = run_scenario(project, levers)

    if not log_run:
        # a quote-only rerun (e.g. to read a number for a no-rerun assistant reply). no run number is
        # allocated and nothing is appended to the audit trail.
        return 200, results

    # RUN-COUNTER OWNERSHIP (Step 7). build_run_payload is the SINGLE owner of run-number allocation
    # and run-log append for EVERY genuine demo run: the scenario-bar /api/run, the assistant rerun
    # buttons and the shift-end edit all route through here, so they share one monotonic N and one
    # append-only §3.4 run log. callers that need the number (e.g. chat_api's shift-edit reply) read
    # it back off the results as 'run_number'. this prevents double-counting - no other code path
    # allocates a run number or appends a run-log entry.
    from audit.run_log import build_run_entry, append_entry, latest_entry
    from hdev.project_store import get_store

    store = get_store()
    run_number = store.next_run_number()
    entry = build_run_entry(run_number, results, latest_entry())
    append_entry(entry)

    # expose the numeric run number alongside the existing deterministic string 'run_id' hash field
    # (which demo_engine owns and this must NOT overwrite). 'run_number' is the audit-trail N.
    results["run_number"] = run_number
    return 200, results
