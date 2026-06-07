"""Rewrite node — fused intent classification + query reformulation.

On attempt 1: classify intent, produce optimized search queries.
On retry (attempt > 1): reuse locked intent, produce new queries + optional
filters, informed by the previous attempt's chunks and the reason node's gap.
"""
import logging
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field

from src.agents.risk_qa_agent.prompts import REWRITE_SYSTEM_PROMPT, REWRITE_USER_PROMPT
from src.agents.risk_qa_agent.utils import build_prompt, last_user_query
from src.core.llm import get_fast_llm

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3

Intent = Literal["factual_lookup", "comparison", "risk_assessment", "summary", "explanation"]


class RewriteResult(BaseModel):
    """Structured rewrite output: intent + queries + optional filters + rationale."""

    intent: Intent = Field(
        description=(
            "User's query intent. One of: factual_lookup, comparison, risk_assessment, "
            "summary, explanation. On retry, confirm the locked intent from attempt 1."
        )
    )
    queries: list[str] = Field(
        description=(
            "Reformulated search queries. Count per intent: "
            "factual_lookup=1, comparison=N per entity, risk_assessment=1-3, "
            "summary=1, explanation=1-2."
        )
    )
    filters: dict | None = Field(
        default=None,
        description=(
            "Optional metadata filters. ONLY populate on retry. "
            "Allowed keys: content_types, tickers, date_from, date_to. "
            "Do NOT include access_level or source_category."
        ),
    )
    rationale: str = Field(
        description="One sentence explaining the rewrite strategy."
    )


@lru_cache(maxsize=1)
def _rewriter():
    """Build a structured-output rewriter. Cached so it's built once per process."""
    return get_fast_llm().with_structured_output(RewriteResult)


def _format_previous_chunks(chunks: list[dict]) -> str:
    """Render previous attempt's chunks for the rewrite prompt."""
    if not chunks:
        return "(no previous chunks — this is the first attempt)"
    lines = []
    for i, c in enumerate(chunks, 1):
        title = c.get("document_title", "unknown")
        excerpt = (c.get("content") or "")[:150]
        score = c.get("relevance_score", "?")
        lines.append(f"  [{i}] {title} (score={score:.3f}): {excerpt}...")
    return "\n".join(lines)


def rewrite_node(state: dict) -> dict:
    """Classify intent, rewrite the query, return {intent, queries, filters, rationale}.

    On attempt 1: produces queries only (no filters).
    On retry: reuses the locked intent, produces new queries + optional filters
    informed by the previous attempt's chunks and the reason's gap.
    """
    query = last_user_query(state)
    attempt = state.get("retrieval_attempts") or 0
    is_retry = attempt > 0

    # On retry, lock the intent from attempt 1 (stored in state after first rewrite)
    locked_intent = state.get("intent") or "<not yet classified — you are attempt 1>"

    previous_chunks_text = _format_previous_chunks(state.get("retrieved_chunks") or [])
    previous_gap = state.get("evidence_gap") or "(no gap — this is the first attempt)"

    user_prompt = REWRITE_USER_PROMPT.format(
        query=query,
        attempt=attempt + 1,
        intent=locked_intent,
        previous_chunks_text=previous_chunks_text,
        previous_gap=previous_gap,
    )
    prompt = build_prompt(REWRITE_SYSTEM_PROMPT, user_prompt)

    result = _rewriter().invoke(prompt)

    if result is None:
        logger.warning("Rewrite node: structured output returned None — using raw query")
        return {
            "intent": "factual_lookup",
            "rewrite_queries": [query],
            "rewrite_filters": {},
            "retrieval_attempts": attempt + 1,
        }

    logger.info(
        "Rewrite node: attempt=%d, intent=%s, queries=%d, filters=%s",
        attempt + 1,
        result.intent,
        len(result.queries),
        "yes" if result.filters else "no",
    )
    logger.debug("Rewrite queries: %s", result.queries)

    return {
        "intent": result.intent,
        "rewrite_queries": result.queries,
        "rewrite_filters": result.filters or {},
        "retrieval_attempts": attempt + 1,
    }
