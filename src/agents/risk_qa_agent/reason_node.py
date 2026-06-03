"""Reason node — two-pass synthesis: analyze chunks + detect conflicts."""
import logging

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

from src.core.llm import get_llm
from src.agents.risk_qa_agent.prompts import REASON_SYSTEM_PROMPT, REASON_USER_PROMPT
from src.agents.risk_qa_agent.state import Citation

logger = logging.getLogger(__name__)


def _build_chunks_text(retrieved_chunks: list[dict]) -> str:
    """Render retrieved chunks into a readable string for the reason prompt."""
    lines = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        source_type = "PUBLIC" if chunk.get("source_category") == "public_sec" else "INTERNAL"
        lines.append(f"--- Chunk {i} [{source_type}] ---")
        lines.append(f"Document ID: {chunk.get('document_id', 'unknown')}")
        lines.append(f"Title: {chunk.get('document_title', 'unknown')}")
        lines.append(f"Date: {chunk.get('document_date', 'unknown')}")
        lines.append(f"Content:\n{chunk.get('content', '')}")
        lines.append("")
    return "\n".join(lines)


def _parse_citations(retrieved_chunks: list[dict], reasoning_output: str) -> list[Citation]:
    """
    Build Citation list from retrieved chunks.

    The reasoning trace already contains the analysis. Here we just build
    structured Citation records for the generate node.
    """
    citations = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        source_cat = chunk.get("source_category", "unknown")
        access = "PUBLIC" if source_cat == "public_sec" else "INTERNAL"

        citation = Citation(
            index=i,
            document_id=chunk.get("document_id", f"doc-{i}"),
            document_title=chunk.get("document_title", "Unknown Document"),
            source_category=source_cat,
            access_level=access,
            document_date=chunk.get("document_date"),
            excerpt=chunk.get("content", "")[:300],  # first 300 chars as excerpt
            chunk_content=chunk.get("content", ""),
        )
        citations.append(citation)

    return citations


def reason_node(state: dict) -> dict:
    """
    Analyze retrieved chunks and produce reasoning_trace + citations.

    Two-pass synthesis:
    1. Read all chunks, identify key facts per source
    2. Detect conflicts between internal and public sources
    3. Build structured reasoning trace and citations

    Args:
        state: AgentState with retrieved_chunks and messages

    Returns:
        dict with reasoning_trace and citations
    """
    retrieved_chunks = state.get("retrieved_chunks", [])
    messages = state.get("messages", [])

    if not retrieved_chunks:
        logger.warning("Reason node: no chunks retrieved")
        return {
            "reasoning_trace": "No documents were retrieved for this query. The answer cannot be grounded in evidence.",
            "citations": []
        }

    # Get user query
    human_msgs = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    query = human_msgs[-1].content if human_msgs else ""

    chunks_text = _build_chunks_text(retrieved_chunks)

    logger.info(f"Reason node: analyzing {len(retrieved_chunks)} chunks for query: '{query[:60]}...'")

    # Build the reason chain
    reason_prompt = REASON_SYSTEM_PROMPT + "\n\n" + REASON_USER_PROMPT.format(
        query=query,
        chunks_text=chunks_text
    )

    fast_llm = get_llm()  # reason uses main LLM (Sonnet) for quality
    chain = reason_prompt | fast_llm | StrOutputParser()

    reasoning_trace = chain.invoke({}).strip()

    # Build citations from chunks
    citations = _parse_citations(retrieved_chunks, reasoning_trace)

    logger.info(f"Reason node: reasoning trace produced {len(citations)} citations")

    return {
        "reasoning_trace": reasoning_trace,
        "citations": citations
    }