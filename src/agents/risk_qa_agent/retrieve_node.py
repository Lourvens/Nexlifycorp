"""Retrieve node — fire Retriever per access level implied by route_key."""
import logging

from langchain_core.documents import Document

from src.agents.risk_qa_agent.utils import last_user_query
from src.ingestion.types import AccessLevel
from src.retrieval import FilterCriteria, Retriever

logger = logging.getLogger(__name__)


ROUTE_TO_ACCESS_LEVELS: dict[str, list[AccessLevel]] = {
    "public_only": [AccessLevel.PUBLIC],
    "internal_only": [AccessLevel.INTERNAL],
    "both": [AccessLevel.PUBLIC, AccessLevel.INTERNAL],
}


def _doc_to_chunk(doc: Document, index: int) -> dict:
    """Coerce a Document + its metadata into a unified chunk dict.

    Metadata values may be lists (Qdrant returns multi-value fields like
    ticker/content_type as lists). We join them to strings so downstream
    .format() and template substitution don't break.
    """
    m = doc.metadata

    def as_str(key: str, default: str = "") -> str:
        v = m.get(key)
        if v is None:
            return default
        if isinstance(v, list):
            return ", ".join(str(x) for x in v) if v else default
        return str(v)

    return {
        "chunk_index": index,
        "content": doc.page_content or "",
        "document_id": as_str("document_id") or as_str("id") or f"doc-{index}",
        "document_title": as_str("source_detail", "Unknown Document"),
        "source_category": as_str("source_category", "unknown"),
        "access_level": as_str("access_level", "unknown"),
        "document_date": as_str("document_date") or None,
        "ticker": as_str("ticker") or None,
        "content_type": as_str("content_type") or None,
    }


def retrieve_node(state: dict) -> dict:
    """Dispatch retrieval per route_key, return merged chunk list."""
    route_key = state.get("route_key")
    if not route_key:
        raise ValueError("route_key not set in state — run route node first")
    if route_key not in ROUTE_TO_ACCESS_LEVELS:
        raise ValueError(
            f"Unknown route_key {route_key!r} — must be one of {list(ROUTE_TO_ACCESS_LEVELS)}"
        )

    query = last_user_query(state)
    logger.info("Retrieve node: route_key=%r, query=%r", route_key, query[:60])

    retriever = Retriever()
    retrieved_chunks: list[dict] = []

    for level in ROUTE_TO_ACCESS_LEVELS[route_key]:
        docs = retriever.retrieve(query=query, k=10, criteria=FilterCriteria(access_level=level))
        base = len(retrieved_chunks)
        retrieved_chunks.extend(_doc_to_chunk(doc, base + i) for i, doc in enumerate(docs))
        logger.info("  → %s retrieval: %d chunks", level.value, len(docs))

    logger.info("Retrieve node: total %d chunks retrieved", len(retrieved_chunks))
    return {"retrieved_chunks": retrieved_chunks}
