# STATUS: NEW (PR 10, Bob to review). the REAL-MODE /api/chat conversation loop (Step 10).
#
# this is the pure chokepoint behind the real-mode assistant turn. hdev/chat_api.build_chat_payload
# calls it (LAZILY, so the demo path never imports a provider) when mode == 'real'. it is the ONE place
# that: resolves the AI config + provider, runs the server-side DATA GUARD before any outbound call,
# drives the §4.2 tool loop, and runs the §4.3 number-check + §8 denylist on the model's final output.
#
# the hard ordering (data guard FIRST, then the loop, then the output guards):
#   1. resolve config (ai.load_config) + provider (ai.resolve_provider) - both dependency-injectable so
#      tests pass a FakeProvider and never touch the network.
#   2. read client_data from the project store (default true) and run ai.check_data_guard BEFORE any
#      provider call. if refused, return a structured {blocked:true, reason, suggest_provider:'ollama'}
#      payload and make NO provider call.
#   3. a METHOD / how / why question short-circuits to the EXACT deflection line (run through the
#      guards too) - a server-side safety net so even a non-cooperative model cannot leak methods.
#   4. otherwise run the loop: build a strict system prompt + §8-safe inputs (client-facing results
#      JSON + open fields; NEVER maps_to / collapsed / hidden names), call provider.generate(messages,
#      tools), execute any returned tool in Python (hdev.real_tools), append its result, loop (cap 5).
#      a text reply is the candidate.
#   5. build the SAFE template reply from the current results (explain/) and run ai.scrub_reply on the
#      model's candidate: any drifting number or any §8 term falls back to the template text.
#
# error surfacing: MissingKeyError -> a structured {error} payload telling Bob to set GEMINI_API_KEY or
# switch to ollama; RateLimitError -> a clear 'rate limit' payload. NEITHER ever contains the key.
#
# §0: all logic lives in Python; the browser is a dumb client that only renders the strings this
# returns. this module invents no numbers - every figure comes from the results JSON the chokepoints
# produce, and the model may only REPHRASE the template text.
from typing import Any, Dict, List, Mapping, Optional, Tuple

import explain

# the demo-equivalent default levers so a real-mode reply always has a results source to quote from
# even before Bob runs a scenario (the 6-truck municipal refuse sample case, matching chat_api).
_DEFAULT_LEVERS = {
    "fleet_size": 6,
    "charging_priority": "lowest_cost",
    "electricity_price": "expected",
    "weather_year": "normal",
    "ownership_years": 10,
}

# the loop cap: how many provider turns (tool call -> result -> next turn) we allow before we stop and
# use whatever text we have. small and bounded so a misbehaving model cannot loop forever.
_MAX_ITERATIONS = 5

# the method/how/why keywords that short-circuit to the deflection line, mirroring the demo keyword
# router precedence (checked FIRST so "why is it more expensive" deflects rather than being read as a
# price question). the deflection text itself comes from explain.method_deflection_line().
_METHOD_KEYWORDS = ("how ", "why", "which parameter", "parameter", "formula", "method", "calculat")

# the strict system prompt. it forbids every §8 never-shown category, says explain RESULTS not METHODS
# (a method question gets the EXACT deflection line), and constrains the model to the seven §4.2 tools
# and to rephrasing the provided template text only. it names NO forbidden term itself so the prompt
# cannot leak one. the provider adapter prepends its own schema instruction (ai.SYSTEM_INSTRUCTION);
# this adds the task framing on top.
_SYSTEM_PROMPT = (
    "You are the assistant inside a battery-electric fleet planning tool, talking to Bob. "
    "Explain RESULTS, never methods. Do not mention any formula, coefficient, parameter name, physics "
    "data source, or internal/technical charging-strategy name. The only charging-approach names you "
    "may use are the three plain labels: Lowest cost, Grid-friendly, Ready earliest. Never mention any "
    "input field that is not provided to you below, and never show an intermediate per-step value. "
    "If Bob asks how, why, or about a method or formula, reply with exactly: "
    "\"That's the engineering side. The results and every input source are in the report.\" "
    "You may ONLY call the provided tools to act, and you must choose their arguments carefully. "
    "For your final answer you may ONLY rephrase the suggested reply text you are given; never state a "
    "number that is not already in the results, and never introduce a new figure."
)


def _is_method_question(message: Optional[str]) -> bool:
    # a method/how/why/formula question. checked server-side so the deflection is enforced even if the
    # model ignores the system prompt.
    if not isinstance(message, str):
        return False
    text = message.lower()
    return any(kw in text for kw in _METHOD_KEYWORDS)


def _safe_results_for_model(results: Mapping[str, Any]) -> Dict[str, Any]:
    # the §8-safe view of the results fed to the model: the client-facing blocks only. the §3.3 results
    # dict is ALREADY client-safe (the chokepoints never put maps_to / collapsed / hidden names in it),
    # so we forward the known client-facing keys and drop anything unexpected defensively.
    allowed_keys = (
        "settings",
        "kpis",
        "verdict",
        "energy",
        "charging",
        "costs",
        "co2",
        "grid",
        "mode",
        "illustrative",
    )
    out: Dict[str, Any] = {}
    for key in allowed_keys:
        if key in results:
            out[key] = results[key]
    return out


def _open_fields_for_model(mode: str) -> List[Dict[str, Any]]:
    # the OPEN fields with values, the ONLY fields the assistant may name (§8). demo reads them from the
    # intake payload; real mode has no fixture yet so this is empty. never names a collapsed/hidden field.
    if mode != "demo":
        return []
    try:
        from hdev.intake_api import build_intake_payload

        payload = build_intake_payload("demo")
        fields: List[Dict[str, Any]] = []
        for section in payload.get("sections", []):
            for field in section.get("fields", []):
                fields.append(
                    {
                        "id": field.get("id"),
                        "label": field.get("label"),
                        "value": field.get("value"),
                        "unit": field.get("unit"),
                    }
                )
        return fields
    except Exception:
        return []


def _base_results(mode: str, body: Mapping[str, Any]) -> Dict[str, Any]:
    # the results dict to quote from: the caller's current_results if present, else a fresh default
    # scenario. in real mode build_run_payload uses the real runner (null fields for stubs); in demo it
    # uses the demo engine. a quote-only run (log_run=False) so no run number is consumed just to read.
    current = body.get("current_results")
    if isinstance(current, Mapping) and current.get("kpis"):
        return dict(current)
    from hdev.run_api import build_run_payload

    levers = body.get("levers")
    if not isinstance(levers, Mapping) or not levers:
        levers = dict(_DEFAULT_LEVERS)
    project = body.get("project") if isinstance(body.get("project"), Mapping) else {}
    try:
        status, payload = build_run_payload(mode, {"levers": dict(levers), "project": dict(project)}, log_run=False)
    except TypeError:
        # the real-mode build_run_payload may not accept log_run on every path; fall back without it.
        status, payload = build_run_payload(mode, {"levers": dict(levers), "project": dict(project)})
    return payload if status == 200 and isinstance(payload, Mapping) else {}


def _template_reply(results: Mapping[str, Any]) -> str:
    # the SAFE, client-safe candidate the model may only rephrase, and the fallback the guards return on
    # any violation. built in Python from the results via explain.summary_text so it always holds true,
    # §8-safe numbers drawn straight from the results JSON.
    try:
        text = explain.summary_text(results)
        if text:
            return text
    except Exception:
        pass
    # if a summary cannot be built (e.g. empty real-mode results), fall back to the plain not-available
    # assistant line rather than inventing anything.
    return explain.unmatched_fallback_line()


def _blocked_payload(mode: str, guard) -> Tuple[int, Dict[str, Any]]:
    # the structured data-guard refusal the UI renders. a 200 (chosen for consistency - it is a normal,
    # expected outcome the client should display, not an HTTP error) carrying blocked:true + the reason
    # + the ollama suggestion. NO provider call was made.
    return 200, {
        "available": True,
        "mode": mode,
        "blocked": True,
        "reason": guard.reason,
        "suggest_provider": guard.suggest_provider or "ollama",
    }


def _error_payload(mode: str, message: str) -> Tuple[int, Dict[str, Any]]:
    # the structured provider-error payload the UI renders (missing key / rate limit). the message is a
    # fixed plain string from the error type; it NEVER contains the API key.
    return 200, {
        "available": True,
        "mode": mode,
        "error": message,
    }


def build_real_chat_payload(
    body: Optional[Mapping[str, Any]],
    config=None,
    provider=None,
    store=None,
) -> Tuple[int, Dict[str, Any]]:
    # the real-mode chat chokepoint. `body` is the parsed request body. config/provider/store are all
    # dependency-injectable so tests drive the whole flow with a FakeProvider and a test store and NEVER
    # open a socket. mode is 'real' here by construction (chat_api only calls this in real mode).
    import ai

    body = body or {}
    mode = "real"

    # (1) resolve config + provider. injected objects win so tests never hit load_config/the network.
    if config is None:
        config = ai.load_config()
    if store is None:
        from hdev.project_store import get_store

        store = get_store()

    provider_name = (getattr(config, "provider", "") or "").strip().lower()

    # (2) DATA GUARD - BEFORE any provider construction or outbound call. read client_data (default
    # true) from the store and gate the free-tier gemini backend.
    client_data = True
    try:
        client_data = bool(store.get_client_data())
    except Exception:
        client_data = True

    guard = ai.check_data_guard(provider_name, client_data, config)
    if not guard.allowed:
        # refused: return the structured blocked payload and make NO provider call.
        return _blocked_payload(mode, guard)

    # resolve the provider only AFTER the guard allows it, so a refused request never even constructs a
    # network-capable backend. tests inject `provider` directly to assert the loop without a socket.
    if provider is None:
        provider = ai.resolve_provider(config)

    message = body.get("message") if isinstance(body.get("message"), str) else None

    # the results we quote from + the safe template reply the model may only rephrase.
    results = _base_results(mode, body)
    safe_reply = _template_reply(results)

    # (3) method/how/why short-circuit: the EXACT deflection line, run through the guards too so even
    # this fixed string is checked. no provider call is needed for a method question.
    if _is_method_question(message):
        deflection = explain.method_deflection_line()
        final = ai.scrub_reply(deflection, results, safe_reply=deflection)
        return 200, {"available": True, "mode": mode, "reply": final}

    # (4) the conversation loop. build the message list + the §8-safe inputs, then drive the model.
    try:
        reply_text = _run_loop(provider, message, results, mode, store)
    except ai.MissingKeyError as exc:
        # a missing gemini key: tell Bob which env var to set / to switch to ollama. no key echoed.
        return _error_payload(mode, str(exc))
    except ai.RateLimitError as exc:
        # a 429: a clear 'rate limit reached' message. no key, no raw provider body.
        return _error_payload(mode, str(exc))
    except ai.ProviderError:
        # any other provider failure (unreachable backend, bad response shape): a plain generic message
        # so the UI shows something, never a stack trace and never a key.
        return _error_payload(mode, "The assistant could not be reached. Please try again shortly.")

    # (5) final-reply guards on the MODEL OUTPUT: §8 denylist + §4.3 number-check, falling back to the
    # safe template text on any violation.
    final = ai.scrub_reply(reply_text, results, safe_reply=safe_reply)
    return 200, {"available": True, "mode": mode, "reply": final}


def _run_loop(provider, message: Optional[str], results: Mapping[str, Any], mode: str, store) -> str:
    # drive provider.generate up to _MAX_ITERATIONS times, executing any tool call in Python and
    # feeding its result back, until the model returns a text reply (the candidate). the model is given
    # ONLY §8-safe inputs: the client-facing results JSON + the open fields. it is NOT given maps_to,
    # collapsed/hidden names, or any intermediate value.
    import json

    from hdev import real_tools

    safe_results = _safe_results_for_model(results)
    open_fields = _open_fields_for_model(mode)

    # the context turn the model sees: the task framing + the §8-safe data + the user's message. the
    # template reply is included as the text the model may rephrase for its final answer.
    context = {
        "instruction": _SYSTEM_PROMPT,
        "results": safe_results,
        "open_fields": open_fields,
        "suggested_reply": _template_reply(results),
        "user_message": message or "",
    }
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
    ]

    tools = list(real_tools.tool_names())

    last_text = ""
    for _ in range(_MAX_ITERATIONS):
        reply = provider.generate(messages, tools)
        if reply.is_tool_call:
            # execute the tool in Python (validated server-side), append its result, and loop so the
            # model can use it. the model NEVER executes anything itself.
            result = real_tools.dispatch_tool(reply.tool_name, reply.arguments, mode, store=store)
            messages.append({"role": "assistant", "content": json.dumps({"tool": reply.tool_name, "arguments": reply.arguments}, ensure_ascii=False)})
            messages.append({"role": "tool", "content": json.dumps(result, ensure_ascii=False)})
            continue
        # a text reply: this is the candidate final reply (to be rephrased from the template + guarded).
        last_text = reply.text or ""
        break

    # if the loop exhausted its iterations on tool calls, fall back to the safe template text.
    if not last_text:
        return _template_reply(results)
    return last_text
