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

    retrieved_chunks: list[dict]
    """Unified list of retrieved chunks from both paths.
    Each dict: content, document_id, document_title, source_category,
    access_level, document_date, chunk_index."""

    reasoning_trace: str
    """Output of the reason node: structured per-source narrative + conflict detection."""

    citations: list[Citation]
    """Structured citation metadata for the generate node."""
