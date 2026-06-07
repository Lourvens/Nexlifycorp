"""Generate node — produce final cited answer from reasoning_trace + citations."""
import logging

from langchain_core.messages import AIMessage

from src.agents.risk_qa_agent.prompts import GENERATE_SYSTEM_PROMPT, GENERATE_USER_PROMPT
from src.agents.risk_qa_agent.utils import (
    access_level_badge,
    build_prompt,
    last_user_query,
    message_text,
)
from src.core.llm import get_llm

logger = logging.getLogger(__name__)


def _build_citations_text(citations: list[dict]) -> str:
    """Render citations as a readable string for the generate prompt."""
    if not citations:
        return "No citations available."

    lines = []
    for c in citations:
        badge = access_level_badge(c.get("access_level", ""))
        excerpt = (c.get("excerpt") or "")[:200]
        lines.append(
            f"[{c.get('index')}] {c.get('document_id', 'unknown')} — "
            f"{c.get('document_title', 'Unknown')} "
            f"({c.get('document_date', 'unknown date')}) {badge}\n"
            f"    Excerpt: \"{excerpt}\""
        )
    return "\n".join(lines)


def generate_node(state: dict) -> dict:
    """Generate the final answer and append an AIMessage to messages."""
    reasoning_trace = state.get("reasoning_trace", "") or ""
    citations = state.get("citations") or []
    query = last_user_query(state)

    prompt = build_prompt(
        GENERATE_SYSTEM_PROMPT,
        GENERATE_USER_PROMPT,
        query=query,
        reasoning_trace=reasoning_trace,
        citations_text=_build_citations_text(citations),
    )

    logger.info(
        "Generate node: query=%r, %d citations, trace %d chars",
        query[:60],
        len(citations),
        len(reasoning_trace),
    )

    answer = message_text(get_llm().invoke(prompt)).strip()
    logger.info("Generate node: answer %d chars", len(answer))
    return {"messages": [AIMessage(content=answer)]}
