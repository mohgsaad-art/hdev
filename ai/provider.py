# STATUS: NEW (PR 10, Bob to review). the AI PROVIDER adapter: one interface, two httpx backends, and
# a test double (Step 10).
#
# the shape FEAT-003 depends on: one Provider interface with a single method
#     generate(messages, tools) -> ProviderReply
# and two interchangeable backends chosen by AI_PROVIDER with NO other code change:
#   - GeminiProvider (default): Google Gemini Developer API over httpx. the key goes in the
#     x-goog-api-key HEADER (never the URL or body) so it cannot leak into a log line or a stored URL.
#   - OllamaProvider: a local, offline model over httpx at OLLAMA_URL.
#
# both backends inject the SAME system instruction (forbids §8 content, demands the strict JSON
# tool-call/reply schema) and run the model's raw text through parse_tool_reply - the single
# validate-in-Python path. both retry a transient 5xx a few times with a short backoff, map a 429 to
# RateLimitError, and never put the key in any message. a missing gemini key raises MissingKeyError
# BEFORE any request is built.
#
# FakeProvider is the CI/test double: constructed with a scripted list of ProviderReply objects, it
# pops the next one on each generate() call and records what it was called with. it makes NO network
# call, so no real API request ever runs in CI.
#
# the httpx client/transport is injectable on both real backends so tests drive them with
# httpx.MockTransport and never open a socket.
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional, Sequence

import httpx

from .config import AIConfig
from .errors import MissingKeyError, ProviderError, RateLimitError, ToolReplyError
from .tool_schema import ALLOWED_TOOL_NAMES, ProviderReply, parse_tool_reply

# the §8-forbidding, schema-demanding system instruction injected into every backend. it names NO
# forbidden term itself (so this string cannot leak one); it tells the model to answer RESULTS not
# METHODS, to never emit a number not in the provided results, and to reply ONLY with the strict JSON
# schema. FEAT-003 extends the conversation around this; FEAT-002 just needs the instruction present
# and asserted by the request-shaping tests.
SYSTEM_INSTRUCTION = (
    "You are a careful assistant for a battery-electric fleet planning tool. "
    "Answer about RESULTS, never about methods, formulas, coefficients, physics data sources, "
    "internal strategy names, or any hidden input field. "
    "A method or how/why question gets exactly: "
    "\"That's the engineering side. The results and every input source are in the report.\" "
    "Never state a number that is not already present in the results you are given. "
    "Reply with ONE JSON object and nothing else: either "
    '{"tool": "<one of the allowed tools>", "arguments": {...}} to call a tool, '
    'or {"reply": "<your text>"} to answer. Do not wrap it in code fences.'
)

# retry policy for a transient server-side failure (5xx) or a connection blip. small and bounded so a
# real outage fails fast with a clear error rather than hanging. the sleep is tiny and monkeypatchable
# in tests (we patch time.sleep so the retry test runs instantly).
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 0.2
_TIMEOUT_SECONDS = 30.0

# the status codes we treat as transient and retry. 429 is handled separately (RateLimitError) and is
# NOT retried here - the caller surfaces the rate-limit message to Bob.
_RETRYABLE_STATUS = {500, 502, 503, 504}


class Provider(ABC):
    # the one interface. a backend takes the message list (role/content turns) and an optional tool
    # list and returns a normalised ProviderReply (a tool call or a text reply). nothing else.
    @abstractmethod
    def generate(self, messages: Sequence[Mapping[str, Any]], tools: Optional[Sequence[Any]] = None) -> ProviderReply:
        raise NotImplementedError


def _allowed_names(tools: Optional[Sequence[Any]]) -> List[str]:
    # derive the allow-list parse_tool_reply validates against. a tool entry may be a plain name string
    # or a dict with a "name" key (so FEAT-003 can pass richer tool specs later). when no tools are
    # given we fall back to the canonical §4.2 list so a stray tool name is still rejected.
    if not tools:
        return list(ALLOWED_TOOL_NAMES)
    names: List[str] = []
    for tool in tools:
        if isinstance(tool, str):
            names.append(tool)
        elif isinstance(tool, Mapping) and isinstance(tool.get("name"), str):
            names.append(tool["name"])
    return names or list(ALLOWED_TOOL_NAMES)


def _tools_block(tools: Optional[Sequence[Any]]) -> str:
    # a short, human-readable list of the allowed tool names appended to the system instruction so the
    # model knows which tools exist. names only - no argument schemas leak any internal detail here.
    names = _allowed_names(tools)
    return "Allowed tools: " + ", ".join(names) + "."


class GeminiProvider(Provider):
    # Google Gemini Developer API backend (the default). the request is a POST to
    #   {base}/v1beta/models/{model}:generateContent
    # with the key in the x-goog-api-key HEADER (not the URL, not the body). the body carries a
    # systemInstruction + the conversation turns mapped to Gemini's contents[] shape.
    _BASE_URL = "https://generativelanguage.googleapis.com"

    def __init__(self, config: AIConfig, client: Optional[httpx.Client] = None, sleep=time.sleep):
        self._config = config
        # the client is injectable so tests pass an httpx.Client wired to a MockTransport. when none is
        # given we build a default client lazily (so constructing a provider never opens a socket).
        self._client = client
        # sleep is injectable so the retry test does not actually wait.
        self._sleep = sleep

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=_TIMEOUT_SECONDS)
        return self._client

    def _url(self) -> str:
        model = self._config.gemini_model
        return f"{self._BASE_URL}/v1beta/models/{model}:generateContent"

    def _build_body(self, messages: Sequence[Mapping[str, Any]], tools: Optional[Sequence[Any]]) -> Dict[str, Any]:
        # map our neutral role/content turns to Gemini's contents[] (role "user"/"model", parts[].text)
        # and attach the system instruction (which includes the schema demand + the tool-name list).
        contents: List[Dict[str, Any]] = []
        for msg in messages:
            role = msg.get("role", "user")
            # Gemini uses "model" for the assistant role; map "assistant" accordingly, "system" turns
            # are folded into systemInstruction below so skip them here.
            if role == "system":
                continue
            gemini_role = "model" if role in ("assistant", "model") else "user"
            contents.append({"role": gemini_role, "parts": [{"text": str(msg.get("content", ""))}]})

        system_text = SYSTEM_INSTRUCTION + " " + _tools_block(tools)
        return {
            "systemInstruction": {"parts": [{"text": system_text}]},
            "contents": contents,
        }

    def generate(self, messages: Sequence[Mapping[str, Any]], tools: Optional[Sequence[Any]] = None) -> ProviderReply:
        if not self._config.has_gemini_key():
            # fail BEFORE building a request so no outbound call is attempted with an empty key. the
            # message names the env var, never the (absent) key value.
            raise MissingKeyError()

        url = self._url()
        body = self._build_body(messages, tools)
        # the key rides in the header, never the URL/body. a test asserts exactly this.
        headers = {"x-goog-api-key": self._config.gemini_api_key, "content-type": "application/json"}

        data = _post_with_retries(self._get_client(), url, body, headers, self._sleep)
        text = _extract_gemini_text(data)
        return parse_tool_reply(text, _allowed_names(tools))


class OllamaProvider(Provider):
    # local, offline backend. POST {OLLAMA_URL}/api/chat with model + messages + stream:false. the
    # same system instruction + schema demand is injected as a leading system turn. no key is involved
    # (ollama is local), so a connection failure gives a clear "not reachable" message, not a key error.
    def __init__(self, config: AIConfig, client: Optional[httpx.Client] = None, sleep=time.sleep):
        self._config = config
        self._client = client
        self._sleep = sleep

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=_TIMEOUT_SECONDS)
        return self._client

    def _url(self) -> str:
        base = self._config.ollama_url.rstrip("/")
        return f"{base}/api/chat"

    def _build_body(self, messages: Sequence[Mapping[str, Any]], tools: Optional[Sequence[Any]]) -> Dict[str, Any]:
        # prepend the system instruction as a system turn, then pass the conversation through. ollama's
        # /api/chat takes a flat messages[] of {role, content}.
        system_text = SYSTEM_INSTRUCTION + " " + _tools_block(tools)
        out: List[Dict[str, Any]] = [{"role": "system", "content": system_text}]
        for msg in messages:
            if msg.get("role") == "system":
                # fold any extra system turn into content so we keep a single leading system message.
                out.append({"role": "system", "content": str(msg.get("content", ""))})
                continue
            out.append({"role": msg.get("role", "user"), "content": str(msg.get("content", ""))})
        return {"model": self._config.ollama_model, "messages": out, "stream": False}

    def generate(self, messages: Sequence[Mapping[str, Any]], tools: Optional[Sequence[Any]] = None) -> ProviderReply:
        url = self._url()
        body = self._build_body(messages, tools)
        headers = {"content-type": "application/json"}
        try:
            data = _post_with_retries(self._get_client(), url, body, headers, self._sleep)
        except httpx.ConnectError:
            # ollama is local and may simply not be running; say so plainly (no key involved).
            raise ProviderError(f"Ollama is not reachable at {self._config.ollama_url}.")
        text = _extract_ollama_text(data)
        return parse_tool_reply(text, _allowed_names(tools))


class FakeProvider(Provider):
    # the CI/test double. constructed with a scripted sequence of ProviderReply objects; each
    # generate() pops the next one and records the (messages, tools) it was called with so a test can
    # assert the loop fed tool results back. makes NO network call. a `raise_on_call` option lets a
    # test prove the demo path never calls a provider (FEAT-003).
    def __init__(self, replies: Optional[Sequence[ProviderReply]] = None, raise_on_call: Optional[Exception] = None):
        self._replies: List[ProviderReply] = list(replies or [])
        self._raise_on_call = raise_on_call
        # a log of every call, for assertions. each entry is {"messages": [...], "tools": [...]}.
        self.calls: List[Dict[str, Any]] = []

    def generate(self, messages: Sequence[Mapping[str, Any]], tools: Optional[Sequence[Any]] = None) -> ProviderReply:
        self.calls.append({"messages": list(messages), "tools": list(tools) if tools else None})
        if self._raise_on_call is not None:
            raise self._raise_on_call
        if not self._replies:
            raise ProviderError("FakeProvider has no more scripted replies.")
        return self._replies.pop(0)


# ---------------------------------------------------------------------------
# shared HTTP helpers (used by both real backends).
# ---------------------------------------------------------------------------
def _post_with_retries(
    client: httpx.Client,
    url: str,
    json_body: Mapping[str, Any],
    headers: Mapping[str, str],
    sleep,
) -> Dict[str, Any]:
    # POST with a small retry loop. a 429 maps to RateLimitError immediately (not retried - the caller
    # tells Bob to wait). a 5xx or a transient transport error is retried up to _MAX_ATTEMPTS with a
    # short backoff; the final failure raises a plain ProviderError. no message ever includes the key.
    last_error: Optional[Exception] = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = client.post(url, json=json_body, headers=dict(headers))
        except httpx.ConnectError:
            # let a connection error bubble so OllamaProvider can give its local-reachability message.
            raise
        except httpx.HTTPError as exc:
            # a transient transport error (timeout, read error): retry, then give up with a clear msg.
            last_error = exc
            if attempt < _MAX_ATTEMPTS:
                sleep(_BACKOFF_SECONDS * attempt)
                continue
            raise ProviderError("The AI provider could not be reached. Please try again shortly.")

        status = response.status_code
        if status == 429:
            raise RateLimitError()
        if status in _RETRYABLE_STATUS:
            # a transient server error: retry a couple of times before giving up.
            last_error = ProviderError(f"The AI provider returned a temporary error ({status}).")
            if attempt < _MAX_ATTEMPTS:
                sleep(_BACKOFF_SECONDS * attempt)
                continue
            raise last_error
        if status >= 400:
            # a non-retryable client/server error. a plain message with the status only (no body, which
            # could echo request detail; no key).
            raise ProviderError(f"The AI provider returned an error ({status}).")

        try:
            return response.json()
        except ValueError:
            raise ProviderError("The AI provider returned a response that could not be read.")

    # unreachable in practice (the loop always returns or raises), but keep a clear fallback.
    raise ProviderError("The AI provider could not be reached. Please try again shortly.")


def _extract_gemini_text(data: Mapping[str, Any]) -> str:
    # pull candidates[0].content.parts[0].text out of a Gemini generateContent response. a shape we do
    # not recognise is a clear error rather than a silent empty reply.
    try:
        candidates = data["candidates"]
        parts = candidates[0]["content"]["parts"]
        texts = [p.get("text", "") for p in parts if isinstance(p, Mapping)]
        text = "".join(texts)
    except (KeyError, IndexError, TypeError):
        raise ProviderError("The AI provider returned an unexpected response shape.")
    if not text:
        raise ProviderError("The AI provider returned an empty response.")
    return text


def _extract_ollama_text(data: Mapping[str, Any]) -> str:
    # ollama /api/chat returns {"message": {"content": "..."}}; /api/generate returns {"response": ...}.
    # accept either so the backend is robust to the endpoint choice.
    message = data.get("message")
    if isinstance(message, Mapping) and isinstance(message.get("content"), str):
        text = message["content"]
    elif isinstance(data.get("response"), str):
        text = data["response"]
    else:
        raise ProviderError("The AI provider returned an unexpected response shape.")
    if not text:
        raise ProviderError("The AI provider returned an empty response.")
    return text


# ---------------------------------------------------------------------------
# provider selection.
# ---------------------------------------------------------------------------
def resolve_provider(config: AIConfig, http_client: Optional[httpx.Client] = None) -> Provider:
    # pick a backend by config.provider with NO other code change for the caller. an unknown value is a
    # clear error (not a silent default) so a typo in AI_PROVIDER is caught at startup. the http client
    # is injectable so tests wire a MockTransport.
    name = (config.provider or "").strip().lower()
    if name == "gemini":
        return GeminiProvider(config, client=http_client)
    if name == "ollama":
        return OllamaProvider(config, client=http_client)
    raise ProviderError(f"Unknown AI_PROVIDER '{config.provider}'. Use 'gemini' or 'ollama'.")
