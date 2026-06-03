"""Retrieve node — fires correct retriever(s) based on route_key."""
import logging
from typing import Literal

from langchain_core.messages import AIMessage

from src.agents.tools import create_public_retriever_tool, create_private_retriever_tool

logger = logging.getLogger(__name__)


def _format_chunk(doc: dict, chunk_idx: int) -> dict:
    """Normalize a retrieved document into a unified chunk dict."""
    return {
        "chunk_index": chunk_idx,
        "content": doc.get("content", ""),
        "document_id": doc.get("document_id", doc.get("id", "unknown")),
        "document_title": doc.get("document_title", doc.get("metadata", {}).get("source_detail", "Unknown")),
        "source_category": doc.get("source_category", doc.get("metadata", {}).get("source_category", "unknown")),
        "access_level": doc.get("access_level", doc.get("metadata", {}).get("access_level", "unknown")),
        "document_date": doc.get("document_date", doc.get("metadata", {}).get("document_date", None)),
    }


def _call_retriever_tool(tool, query: str, k: int = 10) -> list[dict]:
    """
    Call a retriever tool and parse the results.

    Returns a list of normalized chunk dicts.
    """
    public_tool = create_public_retriever_tool()
    private_tool = create_private_retriever_tool()

    try:
        raw_result = tool.invoke({
            "query": query,
            "k": k,
        })
        # Tool returns a formatted string — parse into chunks
        # The format_results returns a string; we need the raw docs
        # Re-retrieve using the retriever directly
        return _extract_chunks_from_result(raw_result)
    except Exception as e:
        logger.error(f"Retriever tool error: {e}")
        return []


def _extract_chunks_from_result(result_str: str) -> list[dict]:
    """
    Parse the string returned by a retriever tool into chunk dicts.

    The tool returns "No relevant documents found" or a formatted string
    with document content. We parse minimally to build the chunk structure.
    """
    if "No relevant documents found" in result_str:
        return []

    chunks = []
    # Simple parsing: the retriever formats results with document separators
    # We extract what we can from the formatted string
    lines = result_str.split("\n")
    current_doc = {}
    content_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("===") or line.startswith("Document"):
            # New document starting
            if current_doc and content_lines:
                current_doc["content"] = "\n".join(content_lines)
                chunks.append(current_doc)
                current_doc = {}
                content_lines = []
            # Parse header line
            if ":" in line:
                parts = line.split(":", 1)
                if "Document" in parts[0]:
                    current_doc["document_id"] = parts[1].strip()
        elif line.startswith("Content:"):
            content_lines.append(line[len("Content:"):].strip())
        elif line.startswith("Date:"):
            current_doc["document_date"] = line[len("Date:"):].strip()
        elif line.startswith("Source:"):
            current_doc["source_category"] = line[len("Source:"):].strip()

    if current_doc and content_lines:
        current_doc["content"] = "\n".join(content_lines)
        chunks.append(current_doc)

    return chunks


def retrieve_node(state: dict) -> dict:
    """
    Fire the appropriate retriever(s) based on route_key.

    Dispatches to:
    - public_only → retrieve_public_documents only
    - internal_only → retrieve_private_documents only
    - both → both in parallel (merged)

    Populates retrieved_chunks in state.

    Args:
        state: AgentState with route_key and messages

    Returns:
        dict with retrieved_chunks list
    """
    route_key = state.get("route_key")
    if not route_key:
        raise ValueError("route_key not set in state — run route node first")

    # Get the user query
    messages = state.get("messages", [])
    human_msgs = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    query = human_msgs[-1].content if human_msgs else ""

    logger.info(f"Retrieve node: route_key='{route_key}', query='{query[:60]}...'")

    retrieved_chunks = []
    chunk_counter = 0

    if route_key in ("public_only", "both"):
        public_tool = create_public_retriever_tool()
        public_chunks = _call_retriever_tool(public_tool, query)
        for c in public_chunks:
            c["chunk_index"] = chunk_counter
            retrieved_chunks.append(c)
            chunk_counter += 1
        logger.info(f"  → Public retrieval: {len(public_chunks)} chunks")

    if route_key in ("internal_only", "both"):
        private_tool = create_private_retriever_tool()
        private_chunks = _call_retriever_tool(private_tool, query)
        for c in private_chunks:
            c["chunk_index"] = chunk_counter
            retrieved_chunks.append(c)
            chunk_counter += 1
        logger.info(f"  → Private retrieval: {len(private_chunks)} chunks")

    logger.info(f"Retrieve node: total {len(retrieved_chunks)} chunks retrieved")

    return {"retrieved_chunks": retrieved_chunks}