# STATUS: NEW (PR 6, Bob to review). public API of the explain/ package (Step 6).
#
# explain/ turns the §3.3 results JSON (and the registry only where a field LABEL is needed) into the
# plain-language assistant text the DEMO assistant says back. in demo there is NO LLM, so the TEMPLATES
# in templates.py ARE the reply; in real mode (Step 10) an LLM may only REPHRASE these, never add a
# number or a method/physics detail. §8 method-hiding and the §4.3 number-check are enforced in this
# package (templates.py + number_check). everything here is pure/offline: no network, no AI provider,
# no clock dependence.
from .templates import (
    summary_text,
    compare_strategies_reply,
    price_up_reply,
    more_trucks_reply,
    cold_winter_reply,
    shift_edit_reply,
    method_deflection_line,
    unmatched_fallback_line,
    number_check,
    allowed_number_tokens,
)

__all__ = [
    "summary_text",
    "compare_strategies_reply",
    "price_up_reply",
    "more_trucks_reply",
    "cold_winter_reply",
    "shift_edit_reply",
    "method_deflection_line",
    "unmatched_fallback_line",
    "number_check",
    "allowed_number_tokens",
]
