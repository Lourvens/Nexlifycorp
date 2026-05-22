"""
Agent tools - Retriever as LangChain tool.

Uses LangChain's standard create_retriever_tool for integration.
"""
from typing import Callable

from langchain_core.tools import tool

from src.retrieval import Retriever


def create_retriever_tool(
    retriever_getter: Callable[[], Retriever] | None = None,
    name: str = "retrieve_documents",
    description: str | None = None,
) -> tool:
    """
    Create a LangChain tool from the Retriever using standard @tool decorator.

    This follows LangChain's best practices for retriever tools.

    Args:
        retriever_getter: Optional callable that returns a Retriever instance.
                          If not provided, Retriever is created directly.
        name: Tool name (default: "retrieve_documents")
        description: Tool description (auto-generated if None)

    Returns:
        LangChain Tool for document retrieval
    """
    _retriever_getter = retriever_getter or (lambda: Retriever())

    if description is None:
        description = """Search for relevant documents from SEC filings and internal Nexlify Corp documents.

Use this tool when the user asks about financial information, company performance,
risk factors, competitive analysis, or any topic requiring factual grounding.

The tool returns formatted document excerpts with source citations."""

    @tool
    def retrieve_documents(query: str, k: int = 4) -> str:
        """
        Search for relevant documents from SEC filings and internal docs.

        Use this when user asks about:
        - Financial performance, revenue, earnings
        - Risk factors and market concerns
        - Competitive analysis and market positioning
        - Strategy and projections
        - Any topic requiring factual grounding from documents

        Args:
            query: The search query (e.g., "NVDA revenue growth 2024")
            k: Number of documents to retrieve (default: 4, max: 10)

        Returns:
            Formatted string containing relevant document excerpts
        """
        retriever = _retriever_getter()

        # Cap k to prevent excessive retrieval
        k = min(k, 10)

        docs = retriever.retrieve(query=query, k=k)

        if not docs:
            return "No relevant documents found for your query."

        # Format for LLM consumption
        return retriever.format_results(docs)

    # Set name and description explicitly
    retrieve_documents.name = name
    retrieve_documents.description = description

    return retrieve_documents


def get_retriever_tool() -> tool:
    """Get the default retriever tool (singleton pattern)."""
    return create_retriever_tool()