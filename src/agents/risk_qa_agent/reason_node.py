"""Reason node — analyze retrieved chunks and produce reasoning_trace + citations."""
import logging

from src.agents.risk_qa_agent.prompts import REASON_SYSTEM_PROMPT, REASON_USER_PROMPT
from src.agents.risk_qa_agent.state import Citation
from src.agents.risk_qa_agent.utils import (
    access_level_badge,
    build_prompt,
    last_user_query,
    message_text,
    source_to_access_level,
)
from src.core.llm import get_llm

logger = logging.getLogger(__name__)


def _build_chunks_text(retrieved_chunks: list[dict]) -> str:
    """Render retrieved chunks as a readable string for the reason prompt."""
    blocks = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        badge = access_level_badge(source_to_access_level(chunk.get("source_category", "")))
        blocks.append(
            f"--- Chunk {i} {badge} ---\n"
            f"Document ID: {chunk.get('document_id', 'unknown')}\n"
            f"Title: {chunk.get('document_title', 'unknown')}\n"
            f"Date: {chunk.get('document_date', 'unknown')}\n"
            f"Content:\n{chunk.get('content', '')}"
        )
    return "\n\n".join(blocks)


def _build_citations(retrieved_chunks: list[dict]) -> list[Citation]:
    """Build one Citation per chunk, 1-indexed."""
    citations: list[Citation] = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        source_cat = chunk.get("source_category", "unknown")
        citations.append(
            Citation(
                index=i,
                document_id=chunk.get("document_id", f"doc-{i}"),
                document_title=chunk.get("document_title", "Unknown Document"),
                source_category=source_cat,
                access_level=source_to_access_level(source_cat),
                document_date=chunk.get("document_date"),
                excerpt=(chunk.get("content") or "")[:300],
                chunk_content=chunk.get("content", ""),
            )
        )
    return citations


def reason_node(state: dict) -> dict:
    """Analyze retrieved chunks → reasoning_trace + citations."""
    retrieved_chunks = state.get("retrieved_chunks") or []

    if not retrieved_chunks:
        logger.warning("Reason node: no chunks retrieved")
        return {
            "reasoning_trace": (
                "No documents were retrieved for this query. "
                "The answer cannot be grounded in evidence."
            ),
            "citations": [],
        }

    query = last_user_query(state)
    prompt = build_prompt(
        REASON_SYSTEM_PROMPT,
        REASON_USER_PROMPT,
        query=query,
        chunks_text=_build_chunks_text(retrieved_chunks),
    )
    logger.info("Reason node: analyzing %d chunks for query=%r", len(retrieved_chunks), query[:60])

    reasoning_trace = message_text(get_llm().invoke(prompt)).strip()
    citations = _build_citations(retrieved_chunks)

    logger.info("Reason node: trace produced %d citations", len(citations))
    return {"reasoning_trace": reasoning_trace, "citations": citations}
