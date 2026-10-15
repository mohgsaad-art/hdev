# STATUS: NEW (PR 10, Bob to review). the strict JSON tool-call REPLY SCHEMA + parser (Step 10).
#
# a backend may not have native tool calling (and even when it does, we normalise everything through
# one path). so the model is instructed to answer with ONE of exactly two JSON shapes:
#
#   a tool call:   {"tool": "<one allowed name>", "arguments": { ... }}
#   a plain reply: {"reply": "<text>"}
#
# parse_tool_reply() is the single "validate it in Python" chokepoint both backends run the raw model
# text through. it strips code fences, json.loads, checks the shape, and REJECTS an unknown tool name
# (so the model can never invoke a tool the server did not offer). returning a structured ProviderReply
# keeps the backends and the FEAT-003 conversation loop decoupled from the raw model text.
#
# this module invents no numbers and makes no network call; it is pure text/JSON validation.
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .errors import ToolReplyError

# the §4.2 tool names the assistant may call. this is the canonical allow-list; callers normally pass
# their own set to parse_tool_reply (so FEAT-003 owns the authoritative list), but keeping it here lets
# a backend validate with a sensible default and documents the surface in one place.
ALLOWED_TOOL_NAMES = (
    "run_scenario",
    "compare_runs",
    "save_scenario",
    "build_report",
    "set_inputs",
    "ask_missing",
    "apply_standard",
)

# a fenced code block the model sometimes wraps JSON in, e.g. ```json\n{...}\n``` or plain ```...```.
# we strip the fence (and an optional language tag) before json.loads so a well-behaved-but-chatty
# model still parses.
_FENCE_RE = re.compile(r"^\s*```(?:[a-zA-Z0-9_-]+)?\s*\n?(.*?)\n?\s*```\s*$", re.DOTALL)


@dataclass
class ProviderReply:
    # the normalised result of one provider turn. EXACTLY one of (tool_name set) or (text set) holds:
    #   - a tool call: tool_name + arguments (validated against the allow-list by the parser).
    #   - a plain reply: text (the user-facing candidate string).
    # a small dataclass so the FEAT-003 loop can branch on `is_tool_call` without touching raw JSON.
    tool_name: Optional[str] = None
    arguments: Dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None
    # the raw model text, kept for debugging/tests. never contains a key.
    raw: Optional[str] = None

    @property
    def is_tool_call(self) -> bool:
        return self.tool_name is not None

    @classmethod
    def tool(cls, name: str, arguments: Mapping[str, Any], raw: Optional[str] = None) -> "ProviderReply":
        return cls(tool_name=name, arguments=dict(arguments), text=None, raw=raw)

    @classmethod
    def message(cls, text: str, raw: Optional[str] = None) -> "ProviderReply":
        return cls(tool_name=None, arguments={}, text=text, raw=raw if raw is not None else text)


def strip_code_fences(raw_text: str) -> str:
    # remove a single surrounding ```...``` fence (with an optional language tag) if present. a model
    # that answers in a fenced block is common; stripping it lets the strict JSON parse succeed. text
    # without a fence is returned trimmed and unchanged otherwise.
    if raw_text is None:
        return ""
    match = _FENCE_RE.match(raw_text)
    if match:
        return match.group(1).strip()
    return raw_text.strip()


def parse_tool_reply(
    raw_text: str,
    allowed_tool_names: Optional[Iterable[str]] = None,
) -> ProviderReply:
    # the single validate-in-Python path. steps, in order:
    #   1. strip any code fence and surrounding whitespace.
    #   2. json.loads - a non-JSON reply is a shape error (we do NOT silently treat prose as a reply,
    #      because the system prompt requires the strict schema; FEAT-003 decides how to recover).
    #   3. require a JSON object with EXACTLY one of "tool" or "reply".
    #   4. for a tool call: the name must be a string on the allow-list, and arguments (if present)
    #      must be an object. an unknown tool name is REJECTED so the model cannot reach an un-offered
    #      tool.
    #   5. for a plain reply: "reply" must be a string.
    allowed = set(allowed_tool_names) if allowed_tool_names is not None else set(ALLOWED_TOOL_NAMES)

    cleaned = strip_code_fences(raw_text)
    if not cleaned:
        raise ToolReplyError("The model returned an empty reply.")

    try:
        data = json.loads(cleaned)
    except (ValueError, TypeError):
        # malformed JSON: a clear shape error, never echoing the (untrusted) model text as code.
        raise ToolReplyError("The model reply was not valid JSON for the tool-call schema.")

    if not isinstance(data, dict):
        raise ToolReplyError("The model reply must be a JSON object.")

    has_tool = "tool" in data
    has_reply = "reply" in data
    if has_tool and has_reply:
        raise ToolReplyError("The model reply must contain either a tool call or a reply, not both.")
    if not has_tool and not has_reply:
        raise ToolReplyError("The model reply must contain a 'tool' or a 'reply' field.")

    if has_tool:
        name = data.get("tool")
        if not isinstance(name, str) or not name:
            raise ToolReplyError("The tool name must be a non-empty string.")
        if name not in allowed:
            # the heart of the validation: reject anything not on the server's allow-list.
            raise ToolReplyError("The model requested an unknown tool.")
        arguments = data.get("arguments", {})
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            raise ToolReplyError("Tool arguments must be a JSON object.")
        return ProviderReply.tool(name, arguments, raw=raw_text)

    reply = data.get("reply")
    if not isinstance(reply, str):
        raise ToolReplyError("The 'reply' field must be a string.")
    return ProviderReply.message(reply, raw=raw_text)
