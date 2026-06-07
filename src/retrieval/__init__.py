"""
Retrieval layer for NexlifyCorp knowledge base.

Provides:
- FilterCriteria: Structured filter specification
- Retriever: Semantic search with metadata filtering

Usage:
    from src.retrieval import Retriever, FilterCriteria

    retriever = Retriever()
    results = retriever.retrieve(
        query="revenue growth",
        k=4,
        criteria=FilterCriteria(access_level=AccessLevel.PUBLIC)
    )
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.ingestion.types import AccessLevel, ContentType, DataSourceCategory


class FilterCriteria:
    """Structured filter specification for retrieval."""

    def __init__(
        self,
        access_level: Optional[AccessLevel] = None,
        content_types: Optional[list[ContentType]] = None,
        tickers: Optional[list[str]] = None,
        source_category: Optional[DataSourceCategory] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        is_public: Optional[bool] = None,
        sec_form: Optional[str] = None,
    ):
        self.access_level = access_level
        self.content_types = content_types
        self.tickers = tickers
        self.source_category = source_category
        self.date_from = date_from
        self.date_to = date_to
        self.is_public = is_public
        self.sec_form = sec_form

    def to_dict(self) -> dict:
        """Convert to dict for VectorStore.search()."""
        result = {}

        if self.access_level is not None:
            result["access_level"] = self.access_level.value
            result["is_public"] = self.access_level == AccessLevel.PUBLIC

        if self.content_types:
            result["content_type"] = [ct.value for ct in self.content_types]

        if self.tickers:
            result["ticker"] = self.tickers

        if self.source_category is not None:
            result["source_category"] = self.source_category.value

        if self.is_public is not None:
            result["is_public"] = self.is_public

        if self.date_from is not None:
            result["document_date_from"] = self.date_from.isoformat()

        if self.date_to is not None:
            result["document_date_to"] = self.date_to.isoformat()

        if self.sec_form is not None:
            result["sec_form"] = self.sec_form

        return result


__all__ = ["Retriever", "FilterCriteria", "AccessLevel", "ContentType", "DataSourceCategory"]


def __getattr__(name: str):
    if name == "Retriever":
        from src.retrieval.retriever import Retriever

        return Retriever
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")