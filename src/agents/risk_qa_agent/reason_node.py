"""Reason node — analyze chunks, produce reasoning_trace + citations, judge sufficiency.

Two-step:
1. (Existing) Free-form reasoning trace via Sonnet
2. (New) Structured sufficiency judgment via Haiku, consuming the trace and chunks

Hard pre-LLM rules force a retry without burning the judgment call:
- 0 chunks → must retry (unless budget exhausted → "I don't know")
- Best relevance score < 0.30 → must retry
"""
import logging
from functools import lru_cache

from pydantic import BaseModel, Field

from src.agents.risk_qa_agent.prompts import REASON_SYSTEM_PROMPT, REASON_USER_PROMPT
from src.agents.risk_qa_agent.state import Citation
from src.agents.risk_qa_agent.utils import (
    access_level_badge,
    build_prompt,
    last_user_query,
    message_text,
    source_to_access_level,
)
from src.core.llm import get_fast_llm, get_llm

logger = logging.getLogger(__name__)

RELEVANCE_FLOOR = 0.30


class SufficiencyJudgment(BaseModel):
    """Structured output for the reason node's sufficiency judgment."""

    sufficient: bool = Field(
        description=(
            "True if the retrieved chunks fully support a grounded answer to the "
            "user's question. False if chunks are missing, off-topic, or insufficient."
        )
    )
    gap: str = Field(
        default="",
        description=(
            "One-sentence description of what is missing. Empty if sufficient. "
            "Be specific: not 'more info needed' but 'no chunk addresses X'."
        ),
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Self-rated confidence in the sufficiency judgment (0.0-1.0).",
    )


@lru_cache(maxsize=1)
def _judge():
    return get_fast_llm().with_structured_output(SufficiencyJudgment)


def _build_chunks_text(retrieved_chunks: list[dict]) -> str:
    """Render retrieved chunks as a readable string for the reason prompt."""
    blocks = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        badge = access_level_badge(source_to_access_level(chunk.get("source_category", "")))
        score = chunk.get("relevance_score")
        score_str = f" [score={score:.3f}]" if isinstance(score, (int, float)) else ""
        blocks.append(
            f"--- Chunk {i} {badge}{score_str} ---\n"
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


def _hard_rule_sufficiency(retrieved_chunks: list[dict]) -> tuple[bool, str, float] | None:
    """Return (sufficient, gap, confidence) if a hard rule fires, else None.

    Hard rules are deterministic and bypass the LLM:
    - 0 chunks → insufficient
    - best relevance score < RELEVANCE_FLOOR → insufficient
    """
    if not retrieved_chunks:
        return (False, "no chunks were retrieved", 1.0)

    scores = [c.get("relevance_score") for c in retrieved_chunks if isinstance(c.get("relevance_score"), (int, float))]
    if scores and max(scores) < RELEVANCE_FLOOR:
        return (False, f"retrieved chunks have low relevance (best score {max(scores):.2f} < {RELEVANCE_FLOOR})", 1.0)

    return None


def reason_node(state: dict) -> dict:
    """Analyze retrieved chunks → reasoning_trace + citations + sufficiency judgment."""
    retrieved_chunks = state.get("retrieved_chunks") or []

    if not retrieved_chunks:
        logger.warning("Reason node: no chunks retrieved")
        return {
            "reasoning_trace": (
                "No documents were retrieved for this query. "
                "The answer cannot be grounded in evidence."
            ),
            "citations": [],
            "evidence_sufficient": False,
            "evidence_gap": "no chunks were retrieved",
            "evidence_confidence": 1.0,
        }

    # Hard pre-LLM rules: if they fire, skip the judgment LLM call.
    hard = _hard_rule_sufficiency(retrieved_chunks)
    if hard is not None:
        sufficient, gap, confidence = hard
        logger.info("Reason node: hard rule fired — sufficient=%s, gap=%r", sufficient, gap)
        # Still produce a trace so the generate node has something to cite from,
        # but skip the LLM trace call if the evidence is obviously insufficient.
        query = last_user_query(state)
        prompt = build_prompt(
            REASON_SYSTEM_PROMPT, REASON_USER_PROMPT,
            query=query, chunks_text=_build_chunks_text(retrieved_chunks),
        )
        reasoning_trace = message_text(get_llm().invoke(prompt)).strip()
        citations = _build_citations(retrieved_chunks)
        return {
            "reasoning_trace": reasoning_trace,
            "citations": citations,
            "evidence_sufficient": sufficient,
            "evidence_gap": gap,
            "evidence_confidence": confidence,
        }

    query = last_user_query(state)
    chunks_text = _build_chunks_text(retrieved_chunks)

    prompt = build_prompt(
        REASON_SYSTEM_PROMPT, REASON_USER_PROMPT,
        query=query, chunks_text=chunks_text,
    )
    logger.info("Reason node: analyzing %d chunks for query=%r", len(retrieved_chunks), query[:60])

    reasoning_trace = message_text(get_llm().invoke(prompt)).strip()
    citations = _build_citations(retrieved_chunks)

    # Structured sufficiency judgment — small, fast Haiku call
    judgment_prompt = (
        "You are a strict evidence-sufficiency judge.\n\n"
        f"## User Question\n{query}\n\n"
        f"## Reasoning Trace\n{reasoning_trace[:2000]}\n\n"
        "## Your Judgment\n"
        "Decide if the chunks fully answer the question. Be honest — if the trace "
        "hedges or says chunks are off-topic, mark insufficient. "
        "If insufficient, write a one-sentence gap describing what's missing."
    )
    judgment = _judge().invoke(judgment_prompt)

    if judgment is None:
        logger.warning("Reason node: sufficiency judgment returned None — defaulting to insufficient")
        return {
            "reasoning_trace": reasoning_trace,
            "citations": citations,
            "evidence_sufficient": False,
            "evidence_gap": "sufficiency judgment unavailable",
            "evidence_confidence": 0.0,
        }

    logger.info(
        "Reason node: sufficient=%s, confidence=%.2f, gap=%r",
        judgment.sufficient, judgment.confidence, judgment.gap[:80],
    )

    return {
        "reasoning_trace": reasoning_trace,
        "citations": citations,
        "evidence_sufficient": judgment.sufficient,
        "evidence_gap": judgment.gap,
        "evidence_confidence": judgment.confidence,
    }
