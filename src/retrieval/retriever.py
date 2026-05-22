"""
Retriever - Semantic search against Qdrant vector store.

Provides structured filtering and result parsing for the agent system.

Usage:
    from src.retrieval import Retriever

    retriever = Retriever()
    docs = retriever.retrieve("risk factors", k=4)
    docs_with_scores = retriever.retrieve_with_scores("revenue", k=8)
"""
from typing import Optional
from langchain_core.documents import Document

from src.core import VectorStore, get_vector_store
from src.retrieval import FilterCriteria


class Retriever:
    """
    Semantic search retriever using the Qdrant vector store.

    Wraps VectorStore.search() with structured FilterCriteria
    for type-safe filtering in the agent layer.
    """

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize retriever.

        Args:
            vector_store: Optional VectorStore instance. If not provided,
                        uses the singleton from src.core.
        """
        self._vector_store = vector_store

    @property
    def vector_store(self) -> VectorStore:
        """Get VectorStore instance (lazy initialization)."""
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    def retrieve(
        self,
        query: str,
        k: int = 4,
        criteria: Optional[FilterCriteria] = None,
    ) -> list[Document]:
        """
        Retrieve relevant documents.

        Args:
            query: Search query text
            k: Number of results to return
            criteria: Optional filter criteria

        Returns:
            List of matching Documents (content + metadata)
        """
        k = min(k, 10)
        filter_dict = criteria.to_dict() if criteria else {}

        return self.vector_store.search(
            query=query,
            k=k,
            filter=filter_dict,
        )

    def retrieve_with_scores(
        self,
        query: str,
        k: int = 4,
        criteria: Optional[FilterCriteria] = None,
    ) -> list[tuple[Document, float]]:
        """
        Retrieve documents with relevance scores.

        Args:
            query: Search query text
            k: Number of results to return
            criteria: Optional filter criteria

        Returns:
            List of (Document, score) tuples
        """
        filter_dict = criteria.to_dict() if criteria else {}

        return self.vector_store.search_with_scores(
            query=query,
            k=k,
            filter=filter_dict,
        )

    def format_results(self, results: list[Document]) -> str:
        """
        Format retrieved documents for LLM consumption.

        Args:
            results: List of Documents from retrieve()

        Returns:
            Formatted string with source citations
        """
        if not results:
            return "No relevant documents found."

        formatted = []
        for i, doc in enumerate(results, 1):
            meta = doc.metadata
            source = meta.get("source_detail", "unknown")
            content_type = meta.get("content_type", "general")
            ticker = meta.get("ticker", "")

            header = f"[Document {i}] {source}"
            if ticker:
                header += f" ({ticker.upper()})"
            header += f" - {content_type}"

            formatted.append(f"{header}\n{doc.page_content[:500]}...")

        return "\n\n".join(formatted)
