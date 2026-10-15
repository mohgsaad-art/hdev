# STATUS: NEW (PR 10, Bob to review). the AI provider CONFIG loader (Step 10).
#
# this reads the handful of env vars that pick and set up an AI backend. it is a pure, offline helper:
# it reads os.environ and, only if present, a plain .env file at the repo root (a tiny KEY=VALUE
# parser - we do NOT add python-dotenv as a dependency for this). os.environ ALWAYS wins over the
# .env file so a shell export can override the file.
#
# the one hard rule here (§0 + the Step 10 data-guard section): the GEMINI_API_KEY is a secret. it is
# NEVER logged, NEVER put in __repr__/__str__, and NEVER placed in an exception message. AIConfig masks
# it so an accidental print(config) or a log line can never leak Bob's key. the real key only ever
# leaves this object through the explicit .gemini_api_key attribute, which only the provider reads to
# build the request header.
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

# the repo root is two levels up from this file (ai/config.py -> ai/ -> repo root). the optional .env
# lives there (see .env.example in FEAT-003).
_REPO_ROOT = Path(__file__).resolve().parent.parent

# defaults chosen in FEAT-002: gemini is the default backend; the model is a free-tier Flash model that
# was on the free tier at build time (documented in the README). ollama points at the usual local port.
DEFAULT_PROVIDER = "gemini"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llama3.1"

# the masked stand-ins shown instead of the real key.
_KEY_SET = "***set***"
_KEY_UNSET = "<unset>"

# the tokens that read as boolean-true (case-insensitive). anything else is false, so an unset or
# garbage value is safely treated as "off" - important because the data-guard flags DEFAULT to off.
_TRUE_TOKENS = {"true", "1", "yes", "on"}


def _parse_bool(raw: Optional[str]) -> bool:
    # a value counts as true only when it is one of the explicit true tokens; everything else (None,
    # "", "false", "no", "0") is false. this keeps GEMINI_PAID / ALLOW_CLIENT_DATA_ON_FREE_TIER off by
    # default so the data guard stays strict unless Bob opts in on purpose.
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_TOKENS


def _read_dotenv(path: Path) -> Dict[str, str]:
    # a minimal KEY=VALUE parser so we do not add a dependency. it reads a .env file if it exists,
    # ignores blank lines and '#' comments, strips an optional surrounding quote pair, and never
    # raises on a malformed line (a bad line is just skipped) so a stray line can never crash startup.
    values: Dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        # no file (or unreadable): behave as if there is no .env at all.
        return values
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # allow an optional leading "export " so a shell-style .env still parses.
        if stripped.startswith("export "):
            stripped = stripped[len("export "):].strip()
        key, sep, value = stripped.partition("=")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        # strip one matching pair of surrounding quotes if present.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            values[key] = value
    return values


@dataclass
class AIConfig:
    # the resolved AI configuration. the API key field is private-by-convention: it is read directly
    # only by GeminiProvider when it builds the request header. the dataclass repr is OVERRIDDEN below
    # so the key never appears in a repr/str/log line.
    provider: str = DEFAULT_PROVIDER
    gemini_api_key: str = ""
    gemini_model: str = DEFAULT_GEMINI_MODEL
    ollama_url: str = DEFAULT_OLLAMA_URL
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    allow_client_data_on_free_tier: bool = False
    gemini_paid: bool = False

    def has_gemini_key(self) -> bool:
        # true when a non-empty key is set. used by the provider to raise a clear MissingKeyError
        # BEFORE building a request, and never exposes the key itself.
        return bool(self.gemini_api_key)

    def masked_key(self) -> str:
        # the only safe thing to print about the key: whether it is set, never its value.
        return _KEY_SET if self.has_gemini_key() else _KEY_UNSET

    def __repr__(self) -> str:
        # custom repr so logging/printing a config can NEVER leak the key. the key is reduced to a
        # masked marker; every other field is safe to show.
        return (
            "AIConfig("
            f"provider={self.provider!r}, "
            f"gemini_api_key={self.masked_key()}, "
            f"gemini_model={self.gemini_model!r}, "
            f"ollama_url={self.ollama_url!r}, "
            f"ollama_model={self.ollama_model!r}, "
            f"allow_client_data_on_free_tier={self.allow_client_data_on_free_tier!r}, "
            f"gemini_paid={self.gemini_paid!r})"
        )

    # str falls back to repr, so masking covers both str(config) and f"{config}".
    __str__ = __repr__


def load_config(
    environ: Optional[Dict[str, str]] = None,
    dotenv_path: Optional[Path] = None,
) -> AIConfig:
    # build an AIConfig from the environment, layered over an optional .env file. os.environ wins over
    # the .env file (a shell export overrides the file). both arguments are injectable so tests can
    # drive the loader without touching the real process environment or a real file.
    env = dict(os.environ if environ is None else environ)

    # layer: start from the .env file (if any), then overlay the process/explicit env so env wins.
    path = _REPO_ROOT / ".env" if dotenv_path is None else dotenv_path
    file_values = _read_dotenv(path)
    merged: Dict[str, str] = {}
    merged.update(file_values)
    merged.update(env)

    def _get(name: str, default: str) -> str:
        value = merged.get(name)
        if value is None or value == "":
            return default
        return value

    return AIConfig(
        provider=_get("AI_PROVIDER", DEFAULT_PROVIDER).strip().lower(),
        gemini_api_key=merged.get("GEMINI_API_KEY", "") or "",
        gemini_model=_get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
        ollama_url=_get("OLLAMA_URL", DEFAULT_OLLAMA_URL),
        ollama_model=_get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
        allow_client_data_on_free_tier=_parse_bool(merged.get("ALLOW_CLIENT_DATA_ON_FREE_TIER")),
        gemini_paid=_parse_bool(merged.get("GEMINI_PAID")),
    )
