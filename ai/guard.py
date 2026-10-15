# STATUS: NEW (PR 10, Bob to review). the server-side DATA GUARD for the free-tier Gemini backend
# (Step 10).
#
# why this exists: the Gemini free tier may use the inputs it receives to improve Google's products.
# a project may hold a client's operational data, so every project carries a `client_data` flag
# (default true, owned by the project store in FEAT-003). this guard is the HARD, server-side gate the
# real chat path calls BEFORE any outbound provider call.
#
# the refuse condition is EXACTLY:
#     provider == 'gemini'  AND  client_data is True  AND  NOT GEMINI_PAID  AND  NOT ALLOW_CLIENT_DATA_ON_FREE_TIER
#
# everything else is allowed:
#   - ollama is ALWAYS allowed (it is local and offline, nothing leaves the machine).
#   - gemini with client_data false is allowed (no client data to protect).
#   - a paid key (GEMINI_PAID=true) lifts the guard (paid tier does not train on inputs).
#   - the explicit opt-in (ALLOW_CLIENT_DATA_ON_FREE_TIER=true) lifts the guard (Bob accepts the risk).
#
# when refused the result carries a plain reason and a suggestion to switch to ollama so the UI can
# render exactly why and what to do. this is a pure function; it makes no network call.
from dataclasses import dataclass
from typing import Optional

# the provider the guard suggests when it refuses: ollama keeps the project's data on the machine.
_SUGGEST_PROVIDER = "ollama"

# the plain-language reason shown when the guard refuses. no key, no internal names - just the risk and
# the fix. the UI renders this verbatim.
_REFUSE_REASON = (
    "This project is marked as holding client data, and the Gemini free tier may use what it receives "
    "to improve Google's products. To keep this project's data private, switch to the local Ollama "
    "backend, or (if you accept the free-tier terms) set ALLOW_CLIENT_DATA_ON_FREE_TIER=true. A paid "
    "Gemini key (GEMINI_PAID=true) also lifts this restriction."
)


@dataclass
class GuardResult:
    # the structured outcome of the guard. `allowed` is the gate the real path checks. when refused,
    # `reason` explains why and `suggest_provider` tells the UI what to recommend; both are None/empty
    # when allowed so a caller can forward the whole object to the client safely.
    allowed: bool
    reason: Optional[str] = None
    suggest_provider: Optional[str] = None


def check_data_guard(provider_name: str, client_data: bool, config) -> GuardResult:
    # the one gate. `config` is an AIConfig (we read only its two boolean lift-flags). the refuse
    # condition is spelled out exactly as the master prompt requires; any lift flag OR a non-gemini
    # provider OR client_data false => allowed.
    gemini_paid = bool(getattr(config, "gemini_paid", False))
    allow_free_tier = bool(getattr(config, "allow_client_data_on_free_tier", False))

    refuse = (
        provider_name == "gemini"
        and client_data is True
        and not gemini_paid
        and not allow_free_tier
    )

    if refuse:
        return GuardResult(allowed=False, reason=_REFUSE_REASON, suggest_provider=_SUGGEST_PROVIDER)
    return GuardResult(allowed=True)
