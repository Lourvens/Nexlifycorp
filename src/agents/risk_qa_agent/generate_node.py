"""Generate node — citation-aware answer generation."""
import logging

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from src.core.llm import get_llm
from src.agents.risk_qa_agent.prompts import GENERATE_SYSTEM_PROMPT, GENERATE_USER_PROMPT

logger = logging.getLogger(__name__)


def _build_citations_text(citations: list[dict]) -> str:
    """Render citations into a readable string for the generate prompt."""
    if not citations:
        return "No citations available."

    lines = []
    for c in citations:
        badge = "[INTERNAL]" if c.get("access_level") == "INTERNAL" else "[PUBLIC]"
        date = c.get("document_date", "unknown date")
        excerpt = c.get("excerpt", "")[:200]
        lines.append(
            f"[{c.get('index')}] {c.get('document_id', 'unknown')} — "
            f"{c.get('document_title', 'Unknown')} ({date}) {badge}\n"
            f"    Excerpt: \"{excerpt}\""
        )
    return "\n".join(lines)


def generate_node(state: dict) -> dict:
    """
    Generate the final cited answer using reasoning_trace + citations.

    Takes:
    - reasoning_trace: the structured analysis from the reason node
    - citations: structured citation metadata
    - query: the original user question

    Produces:
    - AIMessage appended to messages with the final answer

    Args:
        state: AgentState with reasoning_trace, citations, messages

    Returns:
        dict with updated messages (AIMessage added)
    """
    reasoning_trace = state.get("reasoning_trace", "")
    citations = state.get("citations", [])
    messages = state.get("messages", [])

    # Get user query
    human_msgs = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    query = human_msgs[-1].content if human_msgs else ""

    citations_text = _build_citations_text(citations)

    logger.info(f"Generate node: generating answer for query: '{query[:60]}...'")
    logger.info(f"  → {len(citations)} citations, reasoning trace length: {len(reasoning_trace)}")

    # Build the generate chain
    generate_prompt = GENERATE_SYSTEM_PROMPT + "\n\n" + GENERATE_USER_PROMPT.format(
        query=query,
        reasoning_trace=reasoning_trace,
        citations_text=citations_text
    )

    main_llm = get_llm()
    chain = generate_prompt | main_llm | StrOutputParser()

    answer = chain.invoke({}).strip()

    logger.info(f"Generate node: answer produced ({len(answer)} chars)")

    # Return updated messages with the AIMessage
    return {"messages": [AIMessage(content=answer)]}