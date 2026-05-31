"""
Agent tools - Retriever as LangChain tool.

Uses LangChain's standard create_retriever_tool for integration.
"""
from datetime import datetime
from typing import Callable, Optional

from langchain_core.tools import tool

from src.ingestion.types import AccessLevel, ContentType, DataSourceCategory
from src.retrieval import Retriever, FilterCriteria


def _parse_filter_criteria(
    access_level: Optional[str] = None,
    content_type: Optional[str] = None,
    tickers: Optional[str] = None,
    source_category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Optional[FilterCriteria]:
    """Parse string filter args into FilterCriteria."""
    criteria = FilterCriteria()

    if access_level:
        try:
            criteria.access_level = AccessLevel(access_level.lower())
        except ValueError:
            pass  # Ignore invalid values

    if content_type:
        try:
            criteria.content_types = [ContentType(content_type.lower())]
        except ValueError:
            pass

    if tickers:
        criteria.tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    if source_category:
        try:
            criteria.source_category = DataSourceCategory(source_category.lower())
        except ValueError:
            pass

    if date_from:
        try:
            criteria.date_from = datetime.fromisoformat(date_from)
        except ValueError:
            pass

    if date_to:
        try:
            criteria.date_to = datetime.fromisoformat(date_to)
        except ValueError:
            pass

    # Return None if no filters were set
    if all(
        v is None
        for v in [
            criteria.access_level,
            criteria.content_types,
            criteria.tickers,
            criteria.source_category,
            criteria.date_from,
            criteria.date_to,
        ]
    ):
        return None

    return criteria


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
    def retrieve_documents(
        query: str,
        k: int = 4,
        access_level: Optional[str] = None,
        content_type: Optional[str] = None,
        tickers: Optional[str] = None,
        source_category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> str:
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
            access_level: Filter by access level - "public", "internal"
            content_type: Filter by content type - "risk_factors",
                "financial_statements", "management_discussion",
                "business_description", "strategy", "competitive_analysis", etc.
            tickers: Filter by stock ticker(s), comma-separated
                (e.g., "NVDA,AAPL" to search only NVIDIA and Apple docs)
            source_category: Filter by source - "public_sec" for SEC filings,
                "internal_nexlify" for internal Nexlify docs
            date_from: Filter documents from this date (ISO format: YYYY-MM-DD)
            date_to: Filter documents up to this date (ISO format: YYYY-MM-DD)

        Returns:
            Formatted string containing relevant document excerpts
        """
        retriever = _retriever_getter()

        # Cap k to prevent excessive retrieval
        k = min(k, 10)

        # Build filter criteria from parameters
        criteria = _parse_filter_criteria(
            access_level=access_level,
            content_type=content_type,
            tickers=tickers,
            source_category=source_category,
            date_from=date_from,
            date_to=date_to,
        )

        docs = retriever.retrieve(query=query, k=k, criteria=criteria)

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