# STATUS: NEW (PR 10, Bob to review). the FINAL-REPLY safety net for the real-mode assistant (Step 10).
#
# the LLM output is UNTRUSTED. even with a strict system prompt a model can drift: invent a number or
# leak a §8 method/physics/internal-strategy term or a collapsed/hidden field name. this module is the
# hard, server-side guard that runs on the model's final user-facing reply BEFORE it reaches the
# client. it applies BOTH checks and, on ANY violation, returns the safe template text instead - so a
# non-cooperative model can never leak a method or a drifting figure.
#
# the two checks (both reused/mirrored from the demo path, so demo and real share one definition of
# "safe"):
#   1. explain.number_check(reply, results, registry_values, safe_reply): any number not in the
#      current results JSON (or the registry/LEVERS numbers) blocks the reply (§4.3 number check).
#   2. a §8 TERM DENYLIST: every collapsed/hidden registry field id + label (mirroring
#      report.builder.hidden_field_names()) PLUS a fixed list of forbidden method / physics /
#      internal-strategy terms (VECTO, DMI, CdxA, k_lin, k_roll, P_wheel, P_aux, rho, rolling
#      resistance, air drag, state of charge, ASAP, JIT, EDF, ES, cost-based, setpoint, OCV, ...).
#      a case-insensitive, word-boundary match on any of these blocks the reply.
#
# scrub_reply() is the one entry point the conversation loop calls. it is pure (no network, no AI) and
# invents no numbers - it only ever returns either the model's reply (clean) or the safe template.
import re
from typing import Any, Iterable, List, Mapping, Optional

import explain

# the fixed §8 forbidden terms: method names, physics data sources, coefficient/parameter symbols, and
# the INTERNAL/technical charging-strategy names. the ONLY charging-approach names allowed in a reply
# are the three client-facing labels (Lowest cost / Grid-friendly / Ready earliest), so the internal
# keys and setpoint words below are all denied. kept lowercase; matched case-insensitively.
#
# note: these are the terms themselves, never shown to a client. this list is the denylist, not output.
_FORBIDDEN_TERMS = (
    # physics data sources / method names
    "vecto",
    "dmi",
    # coefficient / parameter symbols and physics quantities
    "cdxa",
    "k_lin",
    "k_roll",
    "p_wheel",
    "p_aux",
    "rho",
    "rolling resistance",
    "air drag",
    "state of charge",
    "soc",
    "ocv",
    "open circuit voltage",
    "internal resistance",
    "setpoint",
    # internal / technical charging-strategy names (the client only ever sees the three plain labels)
    "asap",
    "jit",
    "edf",
    "cost-based",
    "cost based",
    "grid-based",
    "earliest-deadline",
)

# a term that contains only word characters (letters/digits/underscore) is matched with \b word
# boundaries so "soc" does not fire inside "society". a term with a space or a hyphen is matched as a
# plain case-insensitive substring (word boundaries do not behave intuitively around those).
def _compile_term(term: str) -> re.Pattern:
    if re.fullmatch(r"[\w]+", term):
        return re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
    return re.compile(re.escape(term), re.IGNORECASE)


_FORBIDDEN_PATTERNS = [_compile_term(t) for t in _FORBIDDEN_TERMS]


def _hidden_name_patterns() -> List[re.Pattern]:
    # every collapsed/hidden registry field id + label becomes a denylist pattern, mirroring
    # report.builder.hidden_field_names() so the report guard and the chat guard agree on exactly which
    # names are off-limits. imported lazily so this module has no import-time dependency on report/.
    try:
        from report.builder import hidden_field_names
    except Exception:
        return []
    patterns: List[re.Pattern] = []
    for name in hidden_field_names():
        if not name:
            continue
        # field ids/labels are matched as plain case-insensitive substrings: an id like
        # "vehicle.aero.cdxa" or a label with spaces should block wherever it appears.
        patterns.append(re.compile(re.escape(name), re.IGNORECASE))
    return patterns


def denylisted_term(reply: str) -> Optional[str]:
    # return the FIRST matched forbidden term/field name in `reply`, or None when the reply is clean.
    # returning the match lets a test assert which term tripped the guard; the caller only needs the
    # boolean (match is not None).
    if not reply:
        return None
    for pattern in _FORBIDDEN_PATTERNS:
        m = pattern.search(reply)
        if m:
            return m.group(0)
    for pattern in _hidden_name_patterns():
        m = pattern.search(reply)
        if m:
            return m.group(0)
    return None


def scrub_reply(
    reply: str,
    results: Mapping[str, Any],
    safe_reply: str,
    registry_values: Optional[Iterable[Any]] = None,
) -> str:
    # the one entry point. apply BOTH guards to the model's final reply and return the SAFE template
    # text on any violation; otherwise return the reply unchanged. order:
    #   1. the §8 term denylist (a leaked method/physics/strategy/hidden-field name) -> replace.
    #   2. the §4.3 number check (a number not sourced from results/registry) -> replace.
    # both fall back to the SAME safe_reply (the template string the loop already built from results),
    # so a blocked reply is replaced by a true, client-safe sentence rather than being dropped.
    if reply is None:
        return safe_reply
    if denylisted_term(reply) is not None:
        return safe_reply
    ok, safe = explain.number_check(reply, results, registry_values=registry_values, safe_reply=safe_reply)
    if not ok:
        return safe
    return reply
