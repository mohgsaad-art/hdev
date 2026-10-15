# STATUS: NEW (PR 1, Bob to review). Public API for the validate package.
#
# the validator checks every lever change and every patch against the registry and LEVERS. it enforces
# the slot lock flag (§9.4 / M6.14) and applies physical/logical sanity checks only (§9.6, no invented
# plausibility ranges). all error messages are plain words (§8 method-hiding). owner is "Bob".
from .validator import (
    ValidationResult,
    validate_lever,
    validate_patch,
    validate_range,
)

__all__ = [
    "ValidationResult",
    "validate_lever",
    "validate_patch",
    "validate_range",
]
