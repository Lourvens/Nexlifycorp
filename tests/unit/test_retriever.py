"""Unit tests for the Retriever class."""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock

from langchain_core.documents import Document

from src.retrieval import Retriever, FilterCriteria
from src.ingestion.types import AccessLevel, ContentType, DataSourceCategory


class TestFilterCriteria:
    """Tests for FilterCriteria dataclass."""

    def test_empty_criteria(self):
        """FilterCriteria with no filters."""
        criteria = FilterCriteria()
        assert criteria.to_dict() == {}

    def test_access_level_filter(self):
        """Filter by access level."""
        criteria = FilterCriteria(access_level=AccessLevel.PUBLIC)
        result = criteria.to_dict()

        assert result["access_level"] == "public"
        assert result["is_public"] is True

    def test_content_types_filter(self):
        """Filter by content types."""
        criteria = FilterCriteria(
            content_types=[ContentType.RISK_FACTORS, ContentType.FINANCIAL_STATEMENTS]
        )
        result = criteria.to_dict()

        assert result["content_type"] == ["risk_factors", "financial_statements"]

    def test_tickers_filter(self):
        """Filter by tickers."""
        criteria = FilterCriteria(tickers=["NVDA", "AAPL"])
        result = criteria.to_dict()

        assert result["ticker"] == ["NVDA", "AAPL"]

    def test_source_category_filter(self):
        """Filter by source category."""
        criteria = FilterCriteria(source_category=DataSourceCategory.PUBLIC_SEC)
        result = criteria.to_dict()

        assert result["source_category"] == "public_sec"

    def test_date_range_filter(self):
        """Filter by date range."""
        date_from = datetime(2024, 1, 1)
        date_to = datetime(2024, 12, 31)
        criteria = FilterCriteria(date_from=date_from, date_to=date_to)
        result = criteria.to_dict()

        assert "document_date_from" in result
        assert "document_date_to" in result

    def test_is_public_filter(self):
        """Filter by is_public flag."""
        criteria = FilterCriteria(is_public=True)
        result = criteria.to_dict()

        assert result["is_public"] is True

    def test_combined_filters(self):
        """Multiple filters combined."""
        criteria = FilterCriteria(
            access_level=AccessLevel.INTERNAL,
            tickers=["NVDA"],
            content_types=[ContentType.RISK_FACTORS],
        )
        result = criteria.to_dict()

        assert result["access_level"] == "internal"
        assert result["ticker"] == ["NVDA"]
        assert result["content_type"] == ["risk_factors"]


class TestRetriever:
    """Tests for Retriever class."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock VectorStore."""
        store = Mock()
        store.search = Mock(return_value=[])
        store.search_with_scores = Mock(return_value=[])
        return store

    @pytest.fixture
    def retriever(self, mock_vector_store):
        """Create Retriever with mock VectorStore."""
        return Retriever(vector_store=mock_vector_store)

    def test_retrieve_with_no_results(self, retriever, mock_vector_store):
        """Retrieve with no matching documents."""
        mock_vector_store.search.return_value = []

        results = retriever.retrieve("test query")

        assert results == []
        mock_vector_store.search.assert_called_once_with(
            query="test query",
            k=4,
            filter={},
        )

    def test_retrieve_with_results(self, retriever, mock_vector_store):
        """Retrieve with matching documents."""
        docs = [
            Document(page_content="Test content", metadata={"source": "test"}),
            Document(page_content="More content", metadata={"source": "test2"}),
        ]
        mock_vector_store.search.return_value = docs

        results = retriever.retrieve("test query", k=5)

        assert len(results) == 2
        assert results[0].page_content == "Test content"
        mock_vector_store.search.assert_called_once_with(
            query="test query",
            k=5,
            filter={},
        )

    def test_retrieve_with_filter(self, retriever, mock_vector_store):
        """Retrieve with FilterCriteria."""
        criteria = FilterCriteria(access_level=AccessLevel.PUBLIC)
        mock_vector_store.search.return_value = []

        retriever.retrieve("revenue", criteria=criteria)

        mock_vector_store.search.assert_called_once()
        call_kwargs = mock_vector_store.search.call_args.kwargs
        assert call_kwargs["filter"] == {"access_level": "public", "is_public": True}

    def test_retrieve_with_scores(self, retriever, mock_vector_store):
        """Retrieve with relevance scores."""
        docs_with_scores = [
            (Document(page_content="Test", metadata={}), 0.95),
            (Document(page_content="Test2", metadata={}), 0.85),
        ]
        mock_vector_store.search_with_scores.return_value = docs_with_scores

        results = retriever.retrieve_with_scores("query", k=3)

        assert len(results) == 2
        assert results[0][1] == 0.95

    def test_format_results_empty(self, retriever):
        """Format empty results."""
        result = retriever.format_results([])
        assert result == "No relevant documents found."

    def test_format_results_with_docs(self, retriever):
        """Format results with documents."""
        docs = [
            Document(
                page_content="NVIDIA revenue grew 122% year over year",
                metadata={
                    "source_detail": "nvda_10k_2024",
                    "content_type": "financial_statements",
                    "ticker": "nvda",
                },
            )
        ]

        formatted = retriever.format_results(docs)

        assert "Document 1" in formatted
        assert "nvda_10k_2024" in formatted
        assert "NVIDIA revenue grew" in formatted
        assert "financial_statements" in formatted

    def test_format_results_truncates_long_content(self, retriever):
        """Long document content is truncated."""
        long_content = "A" * 1000
        docs = [
            Document(
                page_content=long_content,
                metadata={"source_detail": "test", "content_type": "general"},
            )
        ]

        formatted = retriever.format_results(docs)

        # Should be truncated to ~500 chars + "..."
        assert "..." in formatted
        assert len(formatted) < len(long_content) + 100

    def test_retrieve_caps_k_at_10(self, retriever, mock_vector_store):
        """k is capped at 10 to prevent excessive retrieval."""
        mock_vector_store.search.return_value = []

        retriever.retrieve("query", k=50)

        call_kwargs = mock_vector_store.search.call_args.kwargs
        assert call_kwargs["k"] == 10