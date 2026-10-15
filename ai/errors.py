# STATUS: NEW (PR 10, Bob to review). the AI provider ERROR types (Step 10).
#
# these are the clear, plain exceptions the backends raise. the hard rule: NO message here ever
# contains the API key (the key never reaches these classes - callers raise with fixed strings only).
# keeping them in their own module avoids an import cycle between the parser and the providers.


class ProviderError(Exception):
    # base class for every AI-backend failure, so a caller can catch all provider problems at once.
    pass


class MissingKeyError(ProviderError):
    # raised when a backend needs a key that is not set (gemini). the message tells Bob WHICH env var
    # to set and that ollama is the offline alternative - it never echoes the (absent) key.
    def __init__(self, message: str = "GEMINI_API_KEY is not set. Set it in your .env or switch AI_PROVIDER=ollama."):
        super().__init__(message)


class RateLimitError(ProviderError):
    # raised on an HTTP 429 from the backend. carries the plain fact that the rate limit was hit; no
    # key, no raw provider body (which could echo request detail).
    status_code = 429

    def __init__(self, message: str = "The AI provider rate limit was reached. Please try again shortly."):
        super().__init__(message)


class ToolReplyError(ProviderError):
    # raised when a model reply cannot be parsed into the strict tool-call/reply schema, or names a
    # tool that is not on the allow-list. the message describes the shape problem only; it never
    # includes a key and never trusts the model text as code.
    pass
