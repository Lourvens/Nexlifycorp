"""
Agent tools - Retriever as LangChain tool.

Uses LangChain's standard create_retriever_tool for integration.
"""
import logging
from datetime import datetime
from typing import Callable, Optional

from langchain_core.tools import tool

from src.ingestion.types import AccessLevel, ContentType, DataSourceCategory
from src.retrieval import Retriever, FilterCriteria

logger = logging.getLogger(__name__)


def _parse_filter_criteria(
    access_level: Optional[str] = None,
    content_type: Optional[str | list[str]] = None,
    tickers: Optional[str | list[str]] = None,
    source_category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Optional[FilterCriteria]:
    """Parse string or list filter args into FilterCriteria."""
    criteria = FilterCriteria()

    if access_level:
        try:
            criteria.access_level = AccessLevel(access_level.lower())
        except ValueError:
            logger.warning(f"Ignoring invalid access_level: {access_level}")

    if content_type:
        types = [content_type] if isinstance(content_type, str) else content_type
        valid_types = []
        for t in types:
            try:
                valid_types.append(ContentType(t.lower()))
            except ValueError:
                logger.warning(f"Ignoring invalid content_type: {t}")
        if valid_types:
            criteria.content_types = valid_types

    if tickers:
        if isinstance(tickers, str):
            tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
        else:
            tickers = [t.strip().upper() for t in tickers]
        criteria.tickers = tickers

    if source_category:
        try:
            criteria.source_category = DataSourceCategory(source_category.lower())
        except ValueError:
            logger.warning(f"Ignoring invalid source_category: {source_category}")

    if date_from:
        try:
            criteria.date_from = datetime.fromisoformat(date_from)
        except ValueError:
            logger.warning(f"Ignoring invalid date_from: {date_from}")

    if date_to:
        try:
            criteria.date_to = datetime.fromisoformat(date_to)
        except ValueError:
            logger.warning(f"Ignoring invalid date_to: {date_to}")
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


def _build_retriever_tool(
    retriever_getter: Callable[[], Retriever] | None = None,
    name: str = "retrieve_documents",
    description: str | None = None,
    forced_access_level: AccessLevel | None = None,
) -> tool:
    """
    Build a retriever tool with optional forced access level constraint.

    Args:
        retriever_getter: Optional callable that returns a Retriever instance.
        name: Tool name
        description: Tool description
        forced_access_level: If set, this access level is always applied (for public/private split)

    Returns:
        LangChain Tool for document retrieval
    """
    _retriever_getter = retriever_getter or (lambda: Retriever())

    @tool
    def retrieve_documents(
        query: str,
        k: int = 4,
        content_type: Optional[str | list[str]] = None,
        tickers: Optional[str | list[str]] = None,
        source_category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> str:
        """
        Search for relevant documents.

        Args:
            query: The search query (e.g., "NVDA revenue growth 2024")
            k: Number of documents to retrieve (default: 4, max: 10)
            content_type: Filter by content type(s) - "risk_factors",
                "financial_statements", "management_discussion",
                "business_description", "strategy", "competitive_analysis", etc.
                Can be a single string or a list of strings.
            tickers: Filter by stock ticker(s) - single ticker (e.g., "NVDA")
                or list (e.g., ["NVDA", "AAPL"]) to search specific companies
            source_category: Filter by source - "public_sec" for SEC filings,
                "internal_nexlify" for internal Nexlify docs
            date_from: Filter documents from this date (ISO format: YYYY-MM-DD)
            date_to: Filter documents up to this date (ISO format: YYYY-MM-DD)

        Returns:
            Formatted string containing relevant document excerpts
        """
        retriever = _retriever_getter()
        k = min(k, 10)

        criteria = _parse_filter_criteria(
            access_level=forced_access_level.value if forced_access_level else None,
            content_type=content_type,
            tickers=tickers,
            source_category=source_category,
            date_from=date_from,
            date_to=date_to,
        )

        docs = retriever.retrieve(query=query, k=k, criteria=criteria)

        if not docs:
            return "No relevant documents found for your query."

        return retriever.format_results(docs)

    retrieve_documents.name = name
    retrieve_documents.description = description or ""
    return retrieve_documents


def create_public_retriever_tool(
    retriever_getter: Callable[[], Retriever] | None = None,
) -> tool:
    """Search for relevant PUBLIC documents from SEC filings."""
    description = """Search public SEC filings (10-K, 10-Q) and public documents.

Use for: company financials, risk factors, market data, competitive analysis.
This tool ONLY searches public SEC filings - it cannot access internal docs."""
    return _build_retriever_tool(
        retriever_getter=retriever_getter,
        name="retrieve_public_documents",
        description=description,
        forced_access_level=AccessLevel.PUBLIC,
    )


def create_private_retriever_tool(
    retriever_getter: Callable[[], Retriever] | None = None,
) -> tool:
    """Search for relevant INTERNAL documents from Nexlify Corp."""
    description = """Search internal Nexlify Corp documents (board memos, strategy, confidential info).

Use for: internal strategy, confidential risk assessments, earnings prep, policy docs.
This tool ONLY searches internal Nexlify documents - it cannot access public SEC filings."""
    return _build_retriever_tool(
        retriever_getter=retriever_getter,
        name="retrieve_private_documents",
        description=description,
        forced_access_level=AccessLevel.INTERNAL,
    )


def get_retriever_tool() -> tool:
    """Get the default retriever tool (singleton pattern)."""
    return _build_retriever_tool(name="retrieve_documents")