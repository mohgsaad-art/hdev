# STATUS: NEW (PR 10, Bob to review). fully-offline tests for the REAL-MODE /api/chat loop (Step 10).
#
# every test here drives the whole flow with a FakeProvider (or no provider at all, for the data-guard
# refusals), so NO socket is ever opened and NO real Gemini/Ollama call runs - this is what CI runs.
# the FakeProvider is scripted with ProviderReply objects (tool calls then a final text reply) and
# records every call so a test can assert the loop fed tool results back.
#
# coverage mirrors the FEAT-003 acceptance criteria:
#   - client_data defaults to true; get/set + reset keep the default.
#   - the data guard end to end: gemini + client_data (default) BLOCKS with a reason + ollama
#     suggestion and makes NO provider call; GEMINI_PAID or ALLOW_CLIENT_DATA_ON_FREE_TIER allows;
#     ollama always allowed.
#   - the seven §4.2 tools dispatch to their chokepoints with server-validated args; an unknown tool
#     and a bad lever/patch are rejected.
#   - the §4.3 number-check + §8 denylist block a drifting/forbidden reply and fall back to the
#     template text; a clean rephrase passes.
#   - the missing-key and 429 paths surface clear structured errors that never leak the key.
#   - a method/how/why question returns the EXACT deflection line.
#   - demo mode never constructs/calls a provider (a raising FakeProvider is injected and a demo
#     request still succeeds).
import json

import pytest
from fastapi.testclient import TestClient

import ai
from ai import AIConfig, FakeProvider, MissingKeyError, ProviderReply, RateLimitError
from hdev import project_store, real_tools
from hdev.real_chat import build_real_chat_payload
from hdev.server import create_app

BASE_LEVERS = {
    "fleet_size": 6,
    "charging_priority": "lowest_cost",
    "electricity_price": "expected",
    "weather_year": "normal",
    "ownership_years": 10,
}

# the exact §4.3 method-deflection line (plain apostrophe) the real path must return verbatim.
DEFLECTION = "That's the engineering side. The results and every input source are in the report."


@pytest.fixture()
def store():
    # a fresh, isolated project store per test (clears the in-memory singleton + the runtime file).
    project_store.reset_for_tests()
    return project_store.get_store()


def _run_results(store):
    # a §3.3 demo results dict to quote from, produced through the real run_scenario tool chokepoint.
    r = real_tools.dispatch_tool("run_scenario", {"levers": dict(BASE_LEVERS)}, "demo", store)
    assert r["ok"] is True
    return r["results"]


# ---------------------------------------------------------------------------
# (a) client_data flag defaults + get/set + reset
# ---------------------------------------------------------------------------
def test_client_data_defaults_true(store):
    # a fresh store assumes the project holds client data.
    assert store.get_client_data() is True


def test_client_data_set_and_get(store):
    store.set_client_data(False)
    assert store.get_client_data() is False
    store.set_client_data(True)
    assert store.get_client_data() is True


def test_client_data_reset_restores_default(store):
    store.set_client_data(False)
    assert store.get_client_data() is False
    project_store.reset_for_tests()
    assert project_store.get_store().get_client_data() is True


# ---------------------------------------------------------------------------
# (b) the data guard end to end (via the real chokepoint, FakeProvider never called when blocked)
# ---------------------------------------------------------------------------
def test_guard_blocks_gemini_client_data_default_no_provider_call(store):
    # gemini + client_data true (default) + no lift flags -> blocked, and the provider is NEVER called
    # (a FakeProvider that raises on any call proves it).
    cfg = AIConfig(provider="gemini", gemini_api_key="irrelevant")
    raising = FakeProvider(raise_on_call=AssertionError("provider must not be called when blocked"))
    status, payload = build_real_chat_payload({"message": "hi"}, config=cfg, provider=raising, store=store)
    assert status == 200
    assert payload["blocked"] is True
    assert payload["suggest_provider"] == "ollama"
    assert isinstance(payload["reason"], str) and payload["reason"]
    assert raising.calls == []  # no outbound call was made
    assert "reply" not in payload


def test_guard_allows_gemini_when_paid(store):
    cfg = AIConfig(provider="gemini", gemini_api_key="k", gemini_paid=True)
    fp = FakeProvider(replies=[ProviderReply.message("Here is the plan summary.")])
    status, payload = build_real_chat_payload({"message": "summary"}, config=cfg, provider=fp, store=store)
    assert status == 200
    assert payload.get("blocked") is not True
    assert fp.calls  # the provider WAS called
    assert "reply" in payload


def test_guard_allows_gemini_when_free_tier_opt_in(store):
    cfg = AIConfig(provider="gemini", gemini_api_key="k", allow_client_data_on_free_tier=True)
    fp = FakeProvider(replies=[ProviderReply.message("Here is the plan summary.")])
    status, payload = build_real_chat_payload({"message": "summary"}, config=cfg, provider=fp, store=store)
    assert status == 200
    assert payload.get("blocked") is not True
    assert fp.calls


def test_guard_allows_gemini_when_client_data_false(store):
    store.set_client_data(False)
    cfg = AIConfig(provider="gemini", gemini_api_key="k")
    fp = FakeProvider(replies=[ProviderReply.message("Here is the plan summary.")])
    status, payload = build_real_chat_payload({"message": "summary"}, config=cfg, provider=fp, store=store)
    assert status == 200
    assert payload.get("blocked") is not True
    assert fp.calls


def test_guard_allows_ollama_regardless_of_client_data(store):
    # ollama is local/offline, so it is always allowed even for a client-data project.
    assert store.get_client_data() is True
    cfg = AIConfig(provider="ollama")
    fp = FakeProvider(replies=[ProviderReply.message("Here is the plan summary.")])
    status, payload = build_real_chat_payload({"message": "summary"}, config=cfg, provider=fp, store=store)
    assert status == 200
    assert payload.get("blocked") is not True
    assert fp.calls


# ---------------------------------------------------------------------------
# (c) the seven §4.2 tools dispatch to their chokepoints with server-validated args
# ---------------------------------------------------------------------------
def test_tool_run_scenario_dispatches(store):
    r = real_tools.dispatch_tool("run_scenario", {"levers": dict(BASE_LEVERS)}, "demo", store)
    assert r["ok"] is True
    assert r["results"]["settings"]["fleet_size"] == 6


def test_tool_run_scenario_bad_lever_rejected(store):
    r = real_tools.dispatch_tool("run_scenario", {"levers": {"fleet_size": "many"}}, "demo", store)
    assert r["ok"] is False
    assert "whole number" in r["error"]


def test_tool_save_and_compare(store):
    results = _run_results(store)
    saved = real_tools.dispatch_tool("save_scenario", {"name": "Base", "results": results}, "demo", store)
    assert saved["ok"] is True
    assert saved["saved"]["scenario"]["name"] == "Base"
    cmp_ = real_tools.dispatch_tool("compare_runs", {}, "demo", store)
    assert cmp_["ok"] is True
    assert cmp_["comparison"]["count"] >= 1


def test_tool_save_scenario_needs_name(store):
    r = real_tools.dispatch_tool("save_scenario", {}, "demo", store)
    assert r["ok"] is False


def test_tool_build_report(store):
    results = _run_results(store)
    r = real_tools.dispatch_tool("build_report", {"format": "pdf", "results": results}, "demo", store)
    assert r["ok"] is True
    assert r["report"]["bytes"] > 0
    assert r["report"]["filename"].endswith(".pdf")


def test_tool_build_report_bad_format(store):
    r = real_tools.dispatch_tool("build_report", {"format": "docx"}, "demo", store)
    assert r["ok"] is False


def test_tool_set_inputs_validates_patch(store):
    # a bad patch (unknown field) is rejected via validate_patch; nothing is persisted.
    bad = real_tools.dispatch_tool("set_inputs", {"patch": {"field": "no.such.field", "value": 5}}, "demo", store)
    assert bad["ok"] is False
    # an unknown field name is rejected server-side.
    assert "recognise" in bad["error"] or "recognize" in bad["error"]


def test_tool_ask_missing_lists_open_missing_fields(store):
    r = real_tools.dispatch_tool("ask_missing", {}, "demo", store)
    assert r["ok"] is True
    # every listed field carries an id + label only (§8: no maps_to, no collapsed/hidden names).
    for field in r["missing_fields"]:
        assert set(field.keys()) == {"id", "label"}


def test_tool_apply_standard_rejects_unknown_field(store):
    r = real_tools.dispatch_tool("apply_standard", {"fields": ["definitely.not.a.field"]}, "demo", store)
    assert r["ok"] is False


def test_tool_unknown_name_rejected(store):
    r = real_tools.dispatch_tool("not_a_tool", {}, "demo", store)
    assert r["ok"] is False


def test_unknown_tool_rejected_by_parser():
    # the parser is the first gate: a tool name not on the allow-list is rejected before the loop.
    from ai import parse_tool_reply, ToolReplyError

    with pytest.raises(ToolReplyError):
        parse_tool_reply(json.dumps({"tool": "rm_rf", "arguments": {}}), real_tools.tool_names())


def test_loop_executes_tool_then_returns_text_feeding_result_back(store):
    # a scripted tool call followed by a text reply: the loop must execute the tool, append its result,
    # and call the provider again with the tool result in the message list.
    cfg = AIConfig(provider="ollama")
    fp = FakeProvider(
        replies=[
            ProviderReply.tool("run_scenario", {"levers": dict(BASE_LEVERS)}),
            ProviderReply.message("Here is the plan summary for your fleet."),
        ]
    )
    status, payload = build_real_chat_payload({"message": "run and summarise"}, config=cfg, provider=fp, store=store)
    assert status == 200
    assert "reply" in payload
    # two provider turns: the tool call, then the final text.
    assert len(fp.calls) == 2
    # the second call carries a tool-result turn fed back in.
    roles = [m["role"] for m in fp.calls[1]["messages"]]
    assert "tool" in roles


# ---------------------------------------------------------------------------
# (d) final-reply guards on the MODEL OUTPUT: number-check + §8 denylist
# ---------------------------------------------------------------------------
def test_clean_rephrase_passes(store):
    # a clean reply that quotes only numbers present in the results passes through unchanged.
    results = _run_results(store)
    battery = results["kpis"]["battery_kwh"]
    clean = f"Each truck is sized for about a {battery} kWh battery."
    cfg = AIConfig(provider="ollama")
    fp = FakeProvider(replies=[ProviderReply.message(clean)])
    status, payload = build_real_chat_payload(
        {"message": "summary", "current_results": results}, config=cfg, provider=fp, store=store
    )
    assert status == 200
    assert payload["reply"] == clean


def test_drifting_number_blocked_falls_back_to_template(store):
    # a reply with a number not in the results is blocked and replaced by the safe template text.
    results = _run_results(store)
    cfg = AIConfig(provider="ollama")
    drift = "The battery is 424242 kWh."
    fp = FakeProvider(replies=[ProviderReply.message(drift)])
    status, payload = build_real_chat_payload(
        {"message": "summary", "current_results": results}, config=cfg, provider=fp, store=store
    )
    assert status == 200
    assert "424242" not in payload["reply"]
    assert payload["reply"] != drift


def test_forbidden_term_blocked_falls_back_to_template(store):
    # a reply leaking a §8 method/physics term is blocked and replaced by the safe template text.
    results = _run_results(store)
    cfg = AIConfig(provider="ollama")
    leak = "We computed this from the VECTO air drag coefficients."
    fp = FakeProvider(replies=[ProviderReply.message(leak)])
    status, payload = build_real_chat_payload(
        {"message": "summary", "current_results": results}, config=cfg, provider=fp, store=store
    )
    assert status == 200
    assert "VECTO" not in payload["reply"]
    assert "air drag" not in payload["reply"].lower()
    assert payload["reply"] != leak


# ---------------------------------------------------------------------------
# (e) clear error surfacing: missing key + 429, never leaking the key
# ---------------------------------------------------------------------------
def test_missing_key_surfaces_structured_error_without_key(store):
    # gemini with the guard lifted (paid) but the provider raises MissingKeyError on call: the payload
    # tells Bob which env var to set / to switch to ollama, and never contains a key value.
    cfg = AIConfig(provider="gemini", gemini_api_key="", gemini_paid=True)
    fp = FakeProvider(raise_on_call=MissingKeyError())
    status, payload = build_real_chat_payload({"message": "summary"}, config=cfg, provider=fp, store=store)
    assert status == 200
    assert "error" in payload
    assert "GEMINI_API_KEY" in payload["error"]  # names the var, not the value
    assert "ollama" in payload["error"].lower()


def test_rate_limit_surfaces_structured_error(store):
    cfg = AIConfig(provider="ollama")
    fp = FakeProvider(raise_on_call=RateLimitError())
    status, payload = build_real_chat_payload({"message": "summary"}, config=cfg, provider=fp, store=store)
    assert status == 200
    assert "error" in payload
    assert "rate limit" in payload["error"].lower()


# ---------------------------------------------------------------------------
# (f) a method/how/why question returns the EXACT deflection line (through the guards)
# ---------------------------------------------------------------------------
def test_method_question_returns_exact_deflection(store):
    cfg = AIConfig(provider="ollama")
    # the provider should not even be needed for a method question; give it a raising fake to prove it.
    fp = FakeProvider(raise_on_call=AssertionError("method question must not call the provider"))
    for msg in ("how is the battery sized?", "why that number?", "which parameter drives this?"):
        status, payload = build_real_chat_payload({"message": msg}, config=cfg, provider=fp, store=store)
        assert status == 200
        assert payload["reply"] == DEFLECTION
    assert fp.calls == []


# ---------------------------------------------------------------------------
# (g) demo mode never constructs/calls a provider (end to end via the server)
# ---------------------------------------------------------------------------
def test_demo_request_never_calls_provider(monkeypatch):
    # inject a FakeProvider that raises if called into resolve_provider, then drive a DEMO request. the
    # demo chokepoint must answer from explain/ templates WITHOUT ever touching the provider.
    def _boom(*a, **k):
        raise AssertionError("demo mode must never construct/call a provider")

    monkeypatch.setattr(ai, "resolve_provider", _boom)
    # also fail hard if the real path were entered at all.
    import hdev.real_chat as real_chat

    monkeypatch.setattr(real_chat, "build_real_chat_payload", lambda *a, **k: (_ for _ in ()).throw(AssertionError("real path must not run in demo mode")))

    c = TestClient(create_app())  # default env -> demo mode
    resp = c.post("/api/chat", json={"action": "compare_strategies", "levers": BASE_LEVERS})
    assert resp.status_code == 200
    assert "Lowest cost" in resp.json()["reply"]
