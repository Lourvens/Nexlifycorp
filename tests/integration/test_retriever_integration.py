"""Integration tests for the Retriever against Qdrant.

These tests require a running Qdrant instance.
Skip with: pytest tests/integration/test_retriever_integration.py -m integration
"""
import pytest

from src.retrieval import Retriever, FilterCriteria
from src.ingestion.types import AccessLevel, ContentType, DataSourceCategory


def qdrant_available() -> bool:
    """Check if Qdrant is running and accessible."""
    try:
        from src.core import get_vector_store
        vs = get_vector_store()
        return vs.count >= 0  # If we can connect, it's available
    except Exception:
        return False


@pytest.mark.skipif(not qdrant_available(), reason="Qdrant not running")
class TestRetrieverIntegration:
    """Integration tests against real Qdrant."""

    def test_retrieve_empty_collection(self):
        """Retrieve from empty collection returns empty."""
        retriever = Retriever()
        results = retriever.retrieve("test query")
        assert results == []

    def test_retrieve_with_access_filter(self):
        """Filter by access level."""
        retriever = Retriever()
        criteria = FilterCriteria(access_level=AccessLevel.PUBLIC)

        results = retriever.retrieve("revenue", criteria=criteria)
        # May be empty if no public data indexed
        assert isinstance(results, list)

    def test_retrieve_with_ticker_filter(self):
        """Filter by ticker."""
        retriever = Retriever()
        criteria = FilterCriteria(tickers=["NVDA"])

        results = retriever.retrieve("financial", criteria=criteria)
        assert isinstance(results, list)

    def test_retrieve_with_scores(self):
        """Retrieve with relevance scores."""
        retriever = Retriever()

        results = retriever.retrieve_with_scores("risk factors", k=5)
        assert isinstance(results, list)
        for doc, score in results:
            assert score >= 0.0
            assert score <= 1.0

    def test_format_results_with_data(self):
        """Format results with actual data."""
        retriever = Retriever()
        docs = retriever.retrieve("NVIDIA", k=3)

        formatted = retriever.format_results(docs)
        assert isinstance(formatted, str)
        if docs:
            assert "Document 1" in formatted


@pytest.mark.integration
class TestRetrieverWithData:
    """Tests that require indexed data."""

    @pytest.fixture(autouse=True)
    def check_qdrant(self):
        """Skip if Qdrant unavailable or empty."""
        if not qdrant_available():
            pytest.skip("Qdrant not available")

        retriever = Retriever()
        if retriever.vector_store.count == 0:
            pytest.skip("No data in vector store - run ingestion first")

    def test_retrieve_public_sec_data(self):
        """Retrieve SEC public filings."""
        retriever = Retriever()
        criteria = FilterCriteria(
            is_public=True,
            source_category=DataSourceCategory.PUBLIC_SEC,
        )

        results = retriever.retrieve("revenue", criteria=criteria, k=5)
        assert isinstance(results, list)

    def test_retrieve_risk_factors(self):
        """Retrieve risk factor content."""
        retriever = Retriever()
        criteria = FilterCriteria(
            content_types=[ContentType.RISK_FACTORS],
        )

        results = retriever.retrieve("market risk", criteria=criteria, k=3)
        assert isinstance(results, list)

    def test_retrieve_with_date_filter(self):
        """Filter by date range."""
        from datetime import datetime

        retriever = Retriever()
        criteria = FilterCriteria(
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 12, 31),
        )

        results = retriever.retrieve("quarterly", criteria=criteria, k=3)
        assert isinstance(results, list)