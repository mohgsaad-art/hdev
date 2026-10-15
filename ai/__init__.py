# STATUS: NEW (PR 10, Bob to review). public surface of the ai/ provider package (Step 10).
#
# this package is the real-mode AI adapter: one Provider interface, two httpx backends (gemini default
# + ollama), a FakeProvider for offline tests, a .env config loader that never leaks the key, the
# strict JSON tool-call schema + parser, the clear error types, and the server-side data guard.
# FEAT-002 delivers all of the above as pure, offline-testable Python; FEAT-003 wires it into the real
# /api/chat loop. DEMO mode never imports or calls anything here.
from .config import (
    AIConfig,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
    DEFAULT_PROVIDER,
    load_config,
)
from .errors import MissingKeyError, ProviderError, RateLimitError, ToolReplyError
from .guard import GuardResult, check_data_guard
from .safety import denylisted_term, scrub_reply
from .provider import (
    FakeProvider,
    GeminiProvider,
    OllamaProvider,
    Provider,
    SYSTEM_INSTRUCTION,
    resolve_provider,
)
from .tool_schema import (
    ALLOWED_TOOL_NAMES,
    ProviderReply,
    parse_tool_reply,
    strip_code_fences,
)

__all__ = [
    # config
    "AIConfig",
    "load_config",
    "DEFAULT_PROVIDER",
    "DEFAULT_GEMINI_MODEL",
    "DEFAULT_OLLAMA_URL",
    "DEFAULT_OLLAMA_MODEL",
    # provider interface + backends
    "Provider",
    "GeminiProvider",
    "OllamaProvider",
    "FakeProvider",
    "resolve_provider",
    "SYSTEM_INSTRUCTION",
    # tool-call schema + parser
    "ProviderReply",
    "parse_tool_reply",
    "strip_code_fences",
    "ALLOWED_TOOL_NAMES",
    # errors
    "ProviderError",
    "MissingKeyError",
    "RateLimitError",
    "ToolReplyError",
    # data guard
    "check_data_guard",
    "GuardResult",
    # final-reply safety net
    "scrub_reply",
    "denylisted_term",
]
