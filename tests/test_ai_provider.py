# STATUS: NEW (PR 10, Bob to review). fully-offline tests for the ai/ provider package (Step 10).
#
# these tests NEVER open a socket. the two httpx backends are driven with httpx.MockTransport, which
# answers from a Python handler instead of the network, so request-shaping and response-parsing are
# asserted without a real Gemini/Ollama endpoint. the FakeProvider makes no HTTP call at all. this is
# what CI runs, so no real API request ever executes.
#
# coverage mirrors the FEAT-002 acceptance criteria:
#   - config parse + key masking + defaults
#   - gemini request shaping (key in x-goog-api-key header, system instruction + tools present) and
#     tool-call AND plain-reply parsing
#   - ollama request shaping and both reply kinds
#   - parse_tool_reply: unknown tool / malformed JSON / code-fence stripping
#   - MissingKeyError, RateLimitError(429), retry on a transient 5xx
#   - the full data-guard truth table
#   - FakeProvider scripted replies + call recording, no network
import json

import httpx
import pytest

import ai
from ai import (
    AIConfig,
    FakeProvider,
    GeminiProvider,
    MissingKeyError,
    OllamaProvider,
    ProviderError,
    ProviderReply,
    RateLimitError,
    ToolReplyError,
    check_data_guard,
    load_config,
    parse_tool_reply,
    resolve_provider,
)


# ---------------------------------------------------------------------------
# small helpers for mocking httpx without a socket.
# ---------------------------------------------------------------------------
def _client_from_handler(handler) -> httpx.Client:
    # wrap a request->Response handler in a MockTransport so provider.post() answers locally.
    return httpx.Client(transport=httpx.MockTransport(handler))


def _gemini_json(text: str) -> dict:
    # a minimal valid Gemini generateContent response wrapping `text`.
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def _ollama_json(text: str) -> dict:
    # a minimal valid ollama /api/chat response wrapping `text`.
    return {"message": {"role": "assistant", "content": text}}


# ---------------------------------------------------------------------------
# (a) config loader: defaults, parsing, key masking.
# ---------------------------------------------------------------------------
def test_config_defaults_when_env_empty():
    cfg = load_config(environ={}, dotenv_path=_nonexistent_path())
    assert cfg.provider == "gemini"
    assert cfg.gemini_model == "gemini-2.0-flash"
    assert cfg.ollama_url == "http://127.0.0.1:11434"
    assert cfg.ollama_model == "llama3.1"
    assert cfg.gemini_api_key == ""
    assert cfg.allow_client_data_on_free_tier is False
    assert cfg.gemini_paid is False


def test_config_parses_env_overrides():
    cfg = load_config(
        environ={
            "AI_PROVIDER": "OLLAMA",
            "GEMINI_MODEL": "gemini-x-flash",
            "OLLAMA_URL": "http://localhost:9999",
            "OLLAMA_MODEL": "mistral",
            "ALLOW_CLIENT_DATA_ON_FREE_TIER": "YES",
            "GEMINI_PAID": "1",
        },
        dotenv_path=_nonexistent_path(),
    )
    # provider is lowercased so "OLLAMA" resolves cleanly.
    assert cfg.provider == "ollama"
    assert cfg.gemini_model == "gemini-x-flash"
    assert cfg.ollama_url == "http://localhost:9999"
    assert cfg.ollama_model == "mistral"
    # booleans parse case-insensitively from true/1/yes/on.
    assert cfg.allow_client_data_on_free_tier is True
    assert cfg.gemini_paid is True


def test_config_bool_false_tokens():
    cfg = load_config(
        environ={"ALLOW_CLIENT_DATA_ON_FREE_TIER": "false", "GEMINI_PAID": "no"},
        dotenv_path=_nonexistent_path(),
    )
    assert cfg.allow_client_data_on_free_tier is False
    assert cfg.gemini_paid is False


def test_config_repr_and_str_never_reveal_key():
    secret = "super-secret-key-value-12345"
    cfg = load_config(environ={"GEMINI_API_KEY": secret}, dotenv_path=_nonexistent_path())
    # the attribute still holds the real key for the provider to use...
    assert cfg.gemini_api_key == secret
    # ...but neither repr nor str nor an f-string may ever contain it.
    assert secret not in repr(cfg)
    assert secret not in str(cfg)
    assert secret not in f"{cfg}"
    assert "***set***" in repr(cfg)


def test_config_masked_key_when_unset():
    cfg = load_config(environ={}, dotenv_path=_nonexistent_path())
    assert cfg.masked_key() == "<unset>"
    assert cfg.has_gemini_key() is False


def test_config_reads_dotenv_but_env_wins(tmp_path):
    # a .env file is read when present; os.environ (the `environ` arg) overrides it.
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "AI_PROVIDER=ollama\n"
        "# a comment\n"
        'GEMINI_MODEL="from-file-flash"\n'
        "export OLLAMA_MODEL=file-llama\n",
        encoding="utf-8",
    )
    cfg = load_config(environ={"GEMINI_MODEL": "from-env-flash"}, dotenv_path=dotenv)
    assert cfg.provider == "ollama"            # from file
    assert cfg.gemini_model == "from-env-flash"  # env overrides file
    assert cfg.ollama_model == "file-llama"    # export + no env override


def _nonexistent_path():
    # a path that certainly does not exist, so the loader behaves as if there is no .env.
    from pathlib import Path

    return Path("/nonexistent/.env.does-not-exist")


# ---------------------------------------------------------------------------
# (b) GeminiProvider request shaping + parsing.
# ---------------------------------------------------------------------------
def test_gemini_request_shaping_and_tool_call_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["method"] = request.method
        captured["headers"] = request.headers
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json=_gemini_json('{"tool": "run_scenario", "arguments": {"fleet_size": 8}}'))

    cfg = AIConfig(provider="gemini", gemini_api_key="KEY-abc", gemini_model="gemini-2.0-flash")
    provider = GeminiProvider(cfg, client=_client_from_handler(handler))
    reply = provider.generate([{"role": "user", "content": "size my fleet"}], tools=["run_scenario", "set_inputs"])

    # URL + method shape.
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/v1beta/models/gemini-2.0-flash:generateContent")
    # the key goes in the x-goog-api-key HEADER, never in the URL or the body.
    assert captured["headers"]["x-goog-api-key"] == "KEY-abc"
    assert "KEY-abc" not in captured["url"]
    assert "KEY-abc" not in json.dumps(captured["body"])
    # the system instruction + the schema demand + the tool-name list are present in the body.
    sys_text = captured["body"]["systemInstruction"]["parts"][0]["text"]
    assert "RESULTS" in sys_text and "JSON" in sys_text
    assert "run_scenario" in sys_text and "set_inputs" in sys_text
    # the user turn is mapped to a "user" content.
    assert captured["body"]["contents"][0]["role"] == "user"
    # the scripted tool-call JSON parses into a tool-call ProviderReply.
    assert reply.is_tool_call
    assert reply.tool_name == "run_scenario"
    assert reply.arguments == {"fleet_size": 8}


def test_gemini_plain_reply_parse():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_gemini_json('{"reply": "Your fleet looks fine."}'))

    cfg = AIConfig(provider="gemini", gemini_api_key="KEY", gemini_model="gemini-2.0-flash")
    provider = GeminiProvider(cfg, client=_client_from_handler(handler))
    reply = provider.generate([{"role": "user", "content": "hi"}])
    assert not reply.is_tool_call
    assert reply.text == "Your fleet looks fine."


def test_gemini_missing_key_raises_before_request():
    called = {"hit": False}

    def handler(request: httpx.Request) -> httpx.Response:
        called["hit"] = True
        return httpx.Response(200, json=_gemini_json('{"reply": "x"}'))

    cfg = AIConfig(provider="gemini", gemini_api_key="", gemini_model="gemini-2.0-flash")
    provider = GeminiProvider(cfg, client=_client_from_handler(handler))
    with pytest.raises(MissingKeyError) as excinfo:
        provider.generate([{"role": "user", "content": "hi"}])
    # no request was attempted, and the message never contains a key value.
    assert called["hit"] is False
    assert "GEMINI_API_KEY" in str(excinfo.value)


def test_gemini_429_maps_to_rate_limit_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limited"})

    cfg = AIConfig(provider="gemini", gemini_api_key="KEY", gemini_model="gemini-2.0-flash")
    provider = GeminiProvider(cfg, client=_client_from_handler(handler))
    with pytest.raises(RateLimitError) as excinfo:
        provider.generate([{"role": "user", "content": "hi"}])
    # the message never leaks the key and mentions the rate limit plainly.
    assert "KEY" not in str(excinfo.value)
    assert "rate limit" in str(excinfo.value).lower()


def test_gemini_retries_transient_5xx_then_succeeds():
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] < 2:
            return httpx.Response(503, json={"error": "temporary"})
        return httpx.Response(200, json=_gemini_json('{"reply": "ok now"}'))

    cfg = AIConfig(provider="gemini", gemini_api_key="KEY", gemini_model="gemini-2.0-flash")
    # inject a no-op sleep so the backoff does not slow the test.
    provider = GeminiProvider(cfg, client=_client_from_handler(handler), sleep=lambda *_: None)
    reply = provider.generate([{"role": "user", "content": "hi"}])
    assert attempts["n"] == 2  # one retry happened
    assert reply.text == "ok now"


# ---------------------------------------------------------------------------
# (c) OllamaProvider request shaping + parsing.
# ---------------------------------------------------------------------------
def test_ollama_request_shaping_and_tool_call_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["method"] = request.method
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json=_ollama_json('{"tool": "build_report", "arguments": {"format": "pdf"}}'))

    cfg = AIConfig(provider="ollama", ollama_url="http://127.0.0.1:11434", ollama_model="llama3.1")
    provider = OllamaProvider(cfg, client=_client_from_handler(handler))
    reply = provider.generate([{"role": "user", "content": "make a report"}], tools=["build_report"])

    assert captured["method"] == "POST"
    assert captured["url"] == "http://127.0.0.1:11434/api/chat"
    assert captured["body"]["model"] == "llama3.1"
    assert captured["body"]["stream"] is False
    # a leading system turn carries the schema demand + the tool-name list.
    first = captured["body"]["messages"][0]
    assert first["role"] == "system"
    assert "JSON" in first["content"] and "build_report" in first["content"]
    # the user turn follows.
    assert captured["body"]["messages"][-1] == {"role": "user", "content": "make a report"}
    assert reply.is_tool_call and reply.tool_name == "build_report"
    assert reply.arguments == {"format": "pdf"}


def test_ollama_plain_reply_parse():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ollama_json('{"reply": "All local and private."}'))

    cfg = AIConfig(provider="ollama", ollama_model="llama3.1")
    provider = OllamaProvider(cfg, client=_client_from_handler(handler))
    reply = provider.generate([{"role": "user", "content": "hi"}])
    assert not reply.is_tool_call
    assert reply.text == "All local and private."


def test_ollama_connect_error_gives_clear_message():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    cfg = AIConfig(provider="ollama", ollama_url="http://127.0.0.1:11434", ollama_model="llama3.1")
    provider = OllamaProvider(cfg, client=_client_from_handler(handler))
    with pytest.raises(ProviderError) as excinfo:
        provider.generate([{"role": "user", "content": "hi"}])
    assert "not reachable" in str(excinfo.value)
    assert "127.0.0.1:11434" in str(excinfo.value)


# ---------------------------------------------------------------------------
# (d) parse_tool_reply: unknown tool, malformed JSON, code fences.
# ---------------------------------------------------------------------------
def test_parse_tool_reply_strips_code_fences():
    raw = '```json\n{"reply": "fenced hello"}\n```'
    reply = parse_tool_reply(raw, ["run_scenario"])
    assert not reply.is_tool_call
    assert reply.text == "fenced hello"


def test_parse_tool_reply_rejects_unknown_tool():
    raw = '{"tool": "delete_everything", "arguments": {}}'
    with pytest.raises(ToolReplyError) as excinfo:
        parse_tool_reply(raw, ["run_scenario", "build_report"])
    assert "unknown tool" in str(excinfo.value).lower()


def test_parse_tool_reply_rejects_malformed_json():
    with pytest.raises(ToolReplyError):
        parse_tool_reply("this is not json at all", ["run_scenario"])


def test_parse_tool_reply_rejects_both_tool_and_reply():
    raw = '{"tool": "run_scenario", "reply": "x"}'
    with pytest.raises(ToolReplyError):
        parse_tool_reply(raw, ["run_scenario"])


def test_parse_tool_reply_accepts_known_tool_default_allowlist():
    # with no explicit allow-list, the canonical §4.2 names are used.
    raw = '{"tool": "ask_missing", "arguments": {"fields": ["a"]}}'
    reply = parse_tool_reply(raw)
    assert reply.is_tool_call and reply.tool_name == "ask_missing"
    assert reply.arguments == {"fields": ["a"]}


def test_parse_tool_reply_bad_arguments_type():
    raw = '{"tool": "run_scenario", "arguments": "oops"}'
    with pytest.raises(ToolReplyError):
        parse_tool_reply(raw, ["run_scenario"])


# ---------------------------------------------------------------------------
# (e) resolve_provider.
# ---------------------------------------------------------------------------
def test_resolve_provider_picks_backend():
    assert isinstance(resolve_provider(AIConfig(provider="gemini")), GeminiProvider)
    assert isinstance(resolve_provider(AIConfig(provider="ollama")), OllamaProvider)


def test_resolve_provider_unknown_raises():
    with pytest.raises(ProviderError):
        resolve_provider(AIConfig(provider="azure"))


# ---------------------------------------------------------------------------
# (f) data-guard truth table.
# ---------------------------------------------------------------------------
def test_guard_refuses_gemini_client_data_no_flags():
    cfg = AIConfig(provider="gemini", gemini_paid=False, allow_client_data_on_free_tier=False)
    result = check_data_guard("gemini", True, cfg)
    assert result.allowed is False
    assert result.suggest_provider == "ollama"
    assert result.reason and "Google" in result.reason


def test_guard_allows_when_gemini_paid():
    cfg = AIConfig(provider="gemini", gemini_paid=True)
    assert check_data_guard("gemini", True, cfg).allowed is True


def test_guard_allows_when_allow_flag_set():
    cfg = AIConfig(provider="gemini", allow_client_data_on_free_tier=True)
    assert check_data_guard("gemini", True, cfg).allowed is True


def test_guard_allows_gemini_when_client_data_false():
    cfg = AIConfig(provider="gemini")
    assert check_data_guard("gemini", False, cfg).allowed is True


def test_guard_allows_ollama_regardless_of_client_data():
    cfg = AIConfig(provider="ollama")
    assert check_data_guard("ollama", True, cfg).allowed is True
    assert check_data_guard("ollama", False, cfg).allowed is True


def test_guard_ollama_allowed_even_with_free_tier_flags_off():
    # ollama is local; the free-tier flags are irrelevant to it.
    cfg = AIConfig(provider="ollama", gemini_paid=False, allow_client_data_on_free_tier=False)
    assert check_data_guard("ollama", True, cfg).allowed is True


# ---------------------------------------------------------------------------
# (g) FakeProvider: scripted replies, call recording, no network.
# ---------------------------------------------------------------------------
def test_fake_provider_returns_scripted_replies_in_order():
    scripted = [
        ProviderReply.tool("run_scenario", {"fleet_size": 6}),
        ProviderReply.message("Here is the summary."),
    ]
    fake = FakeProvider(scripted)
    first = fake.generate([{"role": "user", "content": "run it"}], tools=["run_scenario"])
    second = fake.generate([{"role": "user", "content": "tool result here"}])
    assert first.is_tool_call and first.tool_name == "run_scenario"
    assert second.text == "Here is the summary."
    # it recorded both calls with the messages/tools it saw (so the loop can be asserted).
    assert len(fake.calls) == 2
    assert fake.calls[0]["tools"] == ["run_scenario"]
    assert fake.calls[1]["messages"][0]["content"] == "tool result here"


def test_fake_provider_raise_on_call():
    # the double a demo-path test uses to prove no provider is ever invoked.
    fake = FakeProvider(raise_on_call=ProviderError("must not be called"))
    with pytest.raises(ProviderError):
        fake.generate([{"role": "user", "content": "x"}])


def test_fake_provider_exhausted_raises():
    fake = FakeProvider([ProviderReply.message("only one")])
    fake.generate([])
    with pytest.raises(ProviderError):
        fake.generate([])
