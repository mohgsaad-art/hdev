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


def build_run_payload(mode: str, body: Optional[Mapping[str, Any]]) -> Tuple[int, Dict[str, Any]]:
    # pure chokepoint. `mode` is already resolved (demo|real). `body` is the parsed JSON request body;
    # its "levers" key (or the body itself) holds the lever map, and an optional "project" key gives
    # the current project context used for lever bounds (e.g. fleet_size max "from project").
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
    return 200, results
