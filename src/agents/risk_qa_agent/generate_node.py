"""Generate node — produce final cited answer, or "I don't know" at max retries.

Two terminal paths:
1. evidence_sufficient=True (or attempts < 3 but reason said go): merge
   retrieved_chunks + previous_chunks, dedupe by (document_id, chunk_index),
   take top-k by relevance_score, then generate with citations.
2. evidence_sufficient=False AND retrieval_attempts >= 3: return
   "I don't know" — the agent tried 3 times and reason said the evidence
   still doesn't support a grounded answer. See ADR-006.
"""
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

MAX_ATTEMPTS = 3
TOP_K_FOR_GENERATE = 10

NO_EVIDENCE_MESSAGE = (
    "I don't have enough evidence to answer this question confidently. "
    "I attempted to retrieve relevant information multiple times, "
    "but the available documents don't directly address your query. "
    "Please rephrase the question or provide more context."
)


def _chunk_key(chunk: dict) -> tuple:
    """Identity for dedupe: same doc, same chunk position."""
    return (chunk.get("document_id"), chunk.get("chunk_index"))


def _merge_top_k(retrieved: list[dict], previous: list[list[dict]], k: int) -> list[dict]:
    """Flatten previous attempts + current, dedupe by (doc, chunk_index),
    keep highest relevance_score per identity, take top-k by score."""
    pool = list(retrieved)
    for attempt in previous:
        pool.extend(attempt)

    best: dict[tuple, dict] = {}
    for chunk in pool:
        key = _chunk_key(chunk)
        if key not in best or chunk.get("relevance_score", 0) > best[key].get("relevance_score", 0):
            best[key] = chunk

    ranked = sorted(best.values(), key=lambda c: c.get("relevance_score", 0), reverse=True)
    return ranked[:k]


def _build_citations_text(chunks: list[dict]) -> str:
    """Render top-k chunks as a readable string for the generate prompt."""
    if not chunks:
        return "No citations available."

    lines = []
    for i, c in enumerate(chunks, 1):
        badge = access_level_badge(c.get("access_level", ""))
        excerpt = (c.get("excerpt") or c.get("content") or "")[:200]
        lines.append(
            f"[{i}] {c.get('document_id', 'unknown')} — "
            f"{c.get('document_title', 'Unknown')} "
            f"({c.get('document_date', 'unknown date')}) {badge}\n"
            f"    Excerpt: \"{excerpt}\""
        )
    return "\n".join(lines)


def generate_node(state: dict) -> dict:
    """Generate the final answer, or return 'I don't know' at max retries."""
    evidence_sufficient = state.get("evidence_sufficient", False)
    retrieval_attempts = state.get("retrieval_attempts", 0)
    reasoning_trace = state.get("reasoning_trace", "") or ""
    query = last_user_query(state)

    # Terminal failure: at max retries, evidence still insufficient.
    if not evidence_sufficient and retrieval_attempts >= MAX_ATTEMPTS:
        logger.warning(
            "Generate node: 'I don't know' — exhausted %d attempts, evidence still insufficient",
            retrieval_attempts,
        )
        return {"messages": [AIMessage(content=NO_EVIDENCE_MESSAGE)]}

    # Normal path: merge chunks across attempts, top-k by score.
    retrieved = state.get("retrieved_chunks") or []
    previous = state.get("previous_chunks") or []
    top_chunks = _merge_top_k(retrieved, previous, TOP_K_FOR_GENERATE)
    citations_text = _build_citations_text(top_chunks)

    prompt = build_prompt(
        GENERATE_SYSTEM_PROMPT,
        GENERATE_USER_PROMPT,
        query=query,
        reasoning_trace=reasoning_trace,
        citations_text=citations_text,
    )

    logger.info(
        "Generate node: query=%r, %d top chunks (from %d current + %d past attempts), trace %d chars",
        query[:60], len(top_chunks), len(retrieved), len(previous), len(reasoning_trace),
    )

    answer = message_text(get_llm().invoke(prompt)).strip()
    logger.info("Generate node: answer %d chars", len(answer))
    return {"messages": [AIMessage(content=answer)]}
