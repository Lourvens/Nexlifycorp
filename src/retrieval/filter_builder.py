"""
Filter builder utilities for retrieval.

Provides helper functions to construct filter dicts for VectorStore.search().

Usage:
    from src.retrieval.filter_builder import build_access_filter, build_date_filter

    filters = {
        **build_access_filter(AccessLevel.PUBLIC),
        **build_date_filter(date_from=datetime(2024, 1, 1)),
    }
"""
from datetime import datetime
from typing import Any

from src.ingestion.types import AccessLevel, ContentType, DataSourceCategory


def build_access_filter(access_level: AccessLevel) -> dict[str, Any]:
    """Build filter dict for access level."""
    return {
        "access_level": access_level.value,
        "is_public": access_level == AccessLevel.PUBLIC,
    }


def build_content_type_filter(content_types: list[ContentType]) -> dict[str, Any]:
    """Build filter dict for content types (OR logic)."""
    return {"content_type": [ct.value for ct in content_types]}


def build_ticker_filter(tickers: list[str]) -> dict[str, Any]:
    """Build filter dict for tickers (OR logic)."""
    return {"ticker": tickers}


def build_source_category_filter(category: DataSourceCategory) -> dict[str, Any]:
    """Build filter dict for source category."""
    return {"source_category": category.value}


def build_date_filter(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict[str, str]:
    """Build filter dict for date range."""
    result = {}
    if date_from:
        result["document_date_from"] = date_from.isoformat()
    if date_to:
        result["document_date_to"] = date_to.isoformat()
    return result


def merge_filters(*filters: dict[str, Any]) -> dict[str, Any]:
    """
    Merge multiple filter dicts (AND logic).

    Note: Qdrant handles array values as OR within the same field.
    For AND across different fields, use must conditions.
    """
    result = {}
    for f in filters:
        result.update(f)
    return result
