"""Retrieve node — dispatches Retriever directly based on route_key.

Calls Retriever().retrieve() for each access level implied by the route,
merges results into a unified chunk list. No string parsing — chunks
are built directly from Document.metadata.
"""
import logging

from langchain_core.documents import Document

from src.ingestion.types import AccessLevel
from src.retrieval import Retriever, FilterCriteria

logger = logging.getLogger(__name__)


ROUTE_TO_ACCESS_LEVELS: dict[str, list[AccessLevel]] = {
    "public_only": [AccessLevel.PUBLIC],
    "internal_only": [AccessLevel.INTERNAL],
    "both": [AccessLevel.PUBLIC, AccessLevel.INTERNAL],
}


def _doc_to_chunk(doc: Document, chunk_index: int) -> dict:
    """Build a unified chunk dict from a Document's metadata."""
    m = doc.metadata
    source_category = m.get("source_category", "unknown")
    access_level = m.get("access_level", "unknown")

    return {
        "chunk_index": chunk_index,
        "content": doc.page_content,
        "document_id": m.get("document_id", m.get("id", "unknown")),
        "document_title": m.get("source_detail", "Unknown"),
        "source_category": source_category,
        "access_level": access_level,
        "document_date": m.get("document_date"),
        "ticker": m.get("ticker"),
        "content_type": m.get("content_type"),
    }


def retrieve_node(state: dict) -> dict:
    """
    Fire the appropriate retriever(s) based on route_key.

    Dispatches to:
    - public_only   → AccessLevel.PUBLIC only
    - internal_only → AccessLevel.INTERNAL only
    - both          → both, results merged

    Args:
        state: AgentState with route_key and messages

    Returns:
        dict with retrieved_chunks list
    """
    route_key = state.get("route_key")
    if not route_key:
        raise ValueError("route_key not set in state — run route node first")

    if route_key not in ROUTE_TO_ACCESS_LEVELS:
        raise ValueError(
            f"Unknown route_key '{route_key}' — must be one of {list(ROUTE_TO_ACCESS_LEVELS)}"
        )

    # Get the user query
    messages = state.get("messages", [])
    human_msgs = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    query = human_msgs[-1].content if human_msgs else ""

    logger.info(f"Retrieve node: route_key='{route_key}', query='{query[:60]}...'")

    retriever = Retriever()
    access_levels = ROUTE_TO_ACCESS_LEVELS[route_key]
    retrieved_chunks: list[dict] = []
    chunk_index = 0

    for level in access_levels:
        criteria = FilterCriteria(access_level=level)
        docs = retriever.retrieve(query=query, k=10, criteria=criteria)
        for doc in docs:
            retrieved_chunks.append(_doc_to_chunk(doc, chunk_index))
            chunk_index += 1
        logger.info(f"  → {level.value} retrieval: {len(docs)} chunks")

    logger.info(f"Retrieve node: total {len(retrieved_chunks)} chunks retrieved")

    return {"retrieved_chunks": retrieved_chunks}