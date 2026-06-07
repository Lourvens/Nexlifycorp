"""Shared helpers for Risk QA Agent nodes.

Pure functions only — no state, no I/O, no graph wiring.
"""
from langchain_core.messages import BaseMessage


def message_text(message: BaseMessage) -> str:
    """Extract a plain string from a message.

    HumanMessage/AIMessage.content may be either a str or a list of
    content blocks (e.g., [{"type": "text", "text": "..."}]). Passing a
    list to downstream consumers like embedders raises
    AttributeError: 'list' object has no attribute 'replace'.
    The .text property handles both shapes.
    """
    return message.text


def last_user_query(state: dict) -> str:
    """Get the most recent human message text from state, or "" if none."""
    for m in reversed(state.get("messages") or []):
        if getattr(m, "type", None) == "human":
            return message_text(m)
    return ""


def require_human_query(state: dict) -> str:
    """Like last_user_query but raises if no human message is present.

    Use in entry-point nodes (e.g. route) where a query is mandatory.
    """
    query = last_user_query(state)
    if not query:
        raise ValueError("No HumanMessage found in state — cannot proceed")
    return query


def source_to_access_level(source_category: str) -> str:
    """Map a source_category value to its access_level label.

    SEC EDGAR filings are PUBLIC; Nexlify internal docs are INTERNAL.
    """
    return "PUBLIC" if source_category == "public_sec" else "INTERNAL"


def access_level_badge(access_level: str) -> str:
    """Render an access_level as a [PUBLIC]/[INTERNAL] badge for prompts."""
    return f"[{access_level}]"


def build_prompt(system: str, user_template: str, **kwargs) -> str:
    """Concatenate a system prompt with a .format()-rendered user prompt.

    The system prompt may contain literal JSON examples with curly braces,
    so it is not .format()-ed — only the user template is.
    """
    return system + "\n\n" + user_template.format(**kwargs)
