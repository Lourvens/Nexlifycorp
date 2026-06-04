"""Agent state definitions for the Risk QA Agent."""
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class Citation(TypedDict):
    """Structured citation for a retrieved chunk."""
    index: int  # footnote number [1], [2], etc.
    document_id: str
    document_title: str
    source_category: str  # "public_sec" or "internal_nexlify"
    access_level: str  # "PUBLIC" or "INTERNAL"
    document_date: str | None
    excerpt: str  # relevant excerpt from the chunk
    chunk_content: str  # full chunk content


class RiskAgentState(TypedDict):
    """State for the Risk QA Agent graph."""

    messages: Annotated[list[AnyMessage], add_messages]
    """Conversation messages. HumanMessage at input, AIMessage at output.

    Typed as list[AnyMessage] so LangGraph Studio detects langgraph_type=messages
    and enables the Chat tab.
    """

    route_key: Annotated[str, None]
    """
    Routing decision from the route node.
    Values: "public_only" | "internal_only" | "both"
    """

    needs_retrieval: Annotated[bool, None]
    """
    Gatekeeper decision: whether the query requires document retrieval.
    True  → go through route → retrieve → reason → generate
    False → skip retrieval, go directly to generate (for general/conversational queries)
    """

    retrieved_chunks: Annotated[list[dict], None]
    """
    Unified list of retrieved chunks from both paths.
    Each dict has keys: content, document_id, document_title,
    source_category, access_level, document_date, chunk_index
    """

    reasoning_trace: Annotated[str, None]
    """
    Output of the reason node.
    Structured per-source narrative + conflict detection.
    """

    citations: Annotated[list[Citation], None]
    """
    Structured citation metadata for the generate node.
    Built by reason node, used by generate node to format footnotes.
    """