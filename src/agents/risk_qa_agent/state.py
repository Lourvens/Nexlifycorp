"""Agent state definitions for the Risk QA Agent."""
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class Citation(TypedDict):
    """Structured citation for a retrieved chunk."""
    index: int
    document_id: str
    document_title: str
    source_category: str
    access_level: str
    document_date: str | None
    excerpt: str
    chunk_content: str


class RiskAgentState(TypedDict):
    """State for the Risk QA Agent graph."""

    messages: Annotated[list[AnyMessage], add_messages]
    """Conversation messages. add_messages reducer appends, so HumanMessage at input,
    AIMessage at output. Typed as list[AnyMessage] so LangGraph Studio detects
    langgraph_type=messages and enables the Chat tab."""

    route_key: str
    """Routing decision from the route node: 'public_only' | 'internal_only' | 'both'."""

    intent: str
    """Classified intent of the user query. Locked across retries so the rewrite
    strategy is stable: 'factual_lookup' | 'comparison' | 'risk_assessment' |
    'summary' | 'explanation'."""

    rewrite_queries: list[str]
    """The actual search queries produced by the rewrite. Read by retrieve_node.
    Length varies by intent: 1 for factual_lookup/summary, N for comparison,
    1-3 for risk_assessment, 1-2 for explanation."""

    rewrite_filters: dict
    """Optional metadata filters from the rewrite (set on retry only).
    Shape matches FilterCriteria.to_dict(): access_level, content_types, tickers,
    date_from, date_to. access_level/source_category are NOT in scope here —
    those are route_key's job."""

    retrieved_chunks: list[dict]
    """Chunks from the current retrieval attempt. Each dict has content, document_id,
    document_title, source_category, access_level, document_date, chunk_index,
    relevance_score. Replaced on each retry."""

    previous_chunks: list[list[dict]]
    """Chunks from past attempts, in order. Outer index = attempt number. At
    generate time, merged with retrieved_chunks and deduped by document_id+chunk_index,
    keeping the highest relevance_score. See ADR-006."""

    retrieval_attempts: int
    """0-indexed counter of how many retrieval attempts have been made. Capped at 3."""

    evidence_sufficient: bool
    """Set by reason_node. True if retrieved_chunks support a grounded answer."""

    evidence_gap: str
    """Set by reason_node when evidence_sufficient is False. One-sentence description
    of what is missing. Consumed by the retry rewrite as feedback."""

    evidence_confidence: float
    """Set by reason_node. 0.0-1.0 self-rated confidence that the chunks fully
    answer the question. < 0.7 triggers a retry (subject to hard pre-LLM rules)."""

    reasoning_trace: str
    """Output of the reason node: structured per-source narrative + conflict detection."""

    citations: list[Citation]
    """Structured citation metadata for the generate node."""
