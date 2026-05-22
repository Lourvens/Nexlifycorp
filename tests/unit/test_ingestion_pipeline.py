"""Unit tests for IngestionPipeline."""
import pytest
from unittest.mock import Mock, MagicMock, patch

from src.ingestion.ingestion_pipeline import (
    IngestionPipeline,
    create_ingestion_pipeline,
    get_ingestion_pipeline,
    reset_ingestion_pipeline,
)
from src.ingestion.types import (
    Chunk,
    ChunkMetadata,
    SEC10K,
    SECMetadata,
    SECSection,
    InternalDocument,
    InternalSection,
    DataSourceCategory,
    AccessLevel,
    ContentType,
    InternalDocType,
)
from datetime import datetime


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_vector_store():
    """Create a mock VectorStore."""
    mock_vs = MagicMock()
    mock_vs.add_chunks.return_value = ["chunk-1", "chunk-2", "chunk-3"]
    return mock_vs


@pytest.fixture
def pipeline(mock_vector_store):
    """Create pipeline with mock VectorStore."""
    return IngestionPipeline(mock_vector_store)


@pytest.fixture
def sample_sec_doc():
    """Create a sample SEC10K document."""
    metadata = SECMetadata(
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        cik="1045810",
        form="10-K",
        fiscal_year=2024,
        fiscal_quarter=4,
        filing_date=datetime(2024, 2, 21),
        document_date=datetime(2024, 1, 31),
    )

    sections = [
        SECSection(
            name="Risk Factors",
            content="NVIDIA faces competition in the AI chip market. Our Data Center segment faces significant competition from AMD's MI300 series.",
            word_count=150,
        ),
        SECSection(
            name="Business Description",
            content="NVIDIA Corporation designs, manufactures, and markets computer graphics processors and related software.",
            word_count=100,
        ),
    ]

    return SEC10K(metadata=metadata, sections=sections)


@pytest.fixture
def sample_internal_doc():
    """Create a sample InternalDocument."""
    sections = [
        InternalSection(
            title="NEXLIFY CORP - BOARD PRESENTATION",
            content="",
            level=1,
            document_type="Board Memo",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="Q4 2025 Board Meeting",
            content="Meeting on January 27, 2026",
            level=2,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="1. CEO Strategic Review",
            content="",
            level=2,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="1.1 Financial Performance",
            content="Q4 revenue reached $36.2B, exceeding guidance by 8%. AI infrastructure demand drove 3x growth in data center segment.",
            level=3,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
            contains_financials=True,
        ),
    ]

    return InternalDocument(sections=sections)


# =============================================================================
# Tests: IngestionPipeline Init
# =============================================================================

class TestPipelineInit:
    """Tests for pipeline initialization."""

    def test_creates_with_vector_store(self, mock_vector_store):
        """Pipeline stores the vector store reference."""
        pipeline = IngestionPipeline(mock_vector_store)
        assert pipeline.vector_store is mock_vector_store

    def test_process_methods_exist(self, pipeline):
        """Pipeline has all process methods."""
        assert hasattr(pipeline, 'process_sec_filing')
        assert hasattr(pipeline, 'process_internal_doc')
        assert hasattr(pipeline, 'ingest_sec_filing')
        assert hasattr(pipeline, 'ingest_internal_doc')


# =============================================================================
# Tests: SEC Processing
# =============================================================================

class TestSecProcessing:
    """Tests for SEC filing processing."""

    def test_process_sec_filing_returns_chunks(self, pipeline, sample_sec_doc, mock_vector_store):
        """process_sec_filing returns list of Chunks."""
        with patch('src.ingestion.ingestion_pipeline.extract_10k') as mock_extract:
            mock_extract.return_value = sample_sec_doc

            chunks = pipeline.process_sec_filing("NVDA", 2024, "10-K")

            assert isinstance(chunks, list)
            assert len(chunks) > 0
            assert all(isinstance(c, Chunk) for c in chunks)

    def test_process_sec_filing_no_filing(self, pipeline, mock_vector_store):
        """process_sec_filing returns empty list when no filing found."""
        with patch('src.ingestion.ingestion_pipeline.extract_10k') as mock_extract:
            mock_extract.return_value = None

            chunks = pipeline.process_sec_filing("INVALID", 2024, "10-K")

            assert chunks == []

    def test_process_sec_filing_chunks_have_correct_metadata(self, pipeline, sample_sec_doc):
        """Chunks have correct SEC metadata."""
        with patch('src.ingestion.ingestion_pipeline.extract_10k') as mock_extract:
            mock_extract.return_value = sample_sec_doc

            chunks = pipeline.process_sec_filing("NVDA", 2024, "10-K")

            for chunk in chunks:
                assert chunk.metadata.source_category == DataSourceCategory.PUBLIC_SEC
                assert chunk.metadata.ticker == "NVDA"
                assert chunk.metadata.is_public is True
                assert chunk.metadata.access_level == AccessLevel.PUBLIC

    def test_ingest_sec_filing_calls_add_chunks(self, pipeline, sample_sec_doc, mock_vector_store):
        """ingest_sec_filing calls vector_store.add_chunks."""
        with patch('src.ingestion.ingestion_pipeline.extract_10k') as mock_extract:
            mock_extract.return_value = sample_sec_doc

            count = pipeline.ingest_sec_filing("NVDA", 2024, "10-K")

            mock_vector_store.add_chunks.assert_called_once()
            # sample_sec_doc has 2 sections, so we get 2 chunks
            assert count == 2


# =============================================================================
# Tests: Internal Doc Processing
# =============================================================================

class TestInternalProcessing:
    """Tests for internal document processing."""

    def test_process_internal_doc_returns_chunks(self, pipeline, sample_internal_doc, mock_vector_store):
        """process_internal_doc returns list of Chunks."""
        with patch('src.ingestion.internal_doc_processor.extract_internal_document_from_content') as mock_extract:
            mock_extract.return_value = sample_internal_doc

            content = "# Test\n## CONFIDENTIAL\n### Content"
            chunks = pipeline.process_internal_doc("TEST-001", "board_memo", content)

            assert isinstance(chunks, list)

    def test_process_internal_doc_with_no_doc(self, pipeline, mock_vector_store):
        """process_internal_doc returns empty list when parse fails."""
        with patch('src.ingestion.internal_doc_processor.extract_internal_document_from_content') as mock_extract:
            mock_extract.return_value = None

            chunks = pipeline.process_internal_doc("TEST-001", "board_memo", "invalid")

            assert chunks == []

    def test_ingest_internal_doc_calls_add_chunks(self, pipeline, sample_internal_doc, mock_vector_store):
        """ingest_internal_doc calls vector_store.add_chunks."""
        with patch('src.ingestion.internal_doc_processor.extract_internal_document_from_content') as mock_extract:
            mock_extract.return_value = sample_internal_doc

            count = pipeline.ingest_internal_doc("TEST-001", "board_memo", "# Test")

            mock_vector_store.add_chunks.assert_called_once()


# =============================================================================
# Tests: Factory Functions
# =============================================================================

class TestFactory:
    """Tests for factory functions."""

    def test_create_ingestion_pipeline_with_mock_vs(self, mock_vector_store):
        """Factory creates pipeline with provided VectorStore."""
        pipeline = create_ingestion_pipeline(vector_store=mock_vector_store)
        assert pipeline.vector_store is mock_vector_store

    def test_get_ingestion_pipeline_singleton(self, mock_vector_store):
        """get_ingestion_pipeline returns singleton."""
        reset_ingestion_pipeline()

        with patch('src.core.VectorStore') as mock_vs_class:
            mock_vs_class.return_value = mock_vector_store

            p1 = get_ingestion_pipeline()
            p2 = get_ingestion_pipeline()

            assert p1 is p2

    def test_reset_ingestion_pipeline(self, mock_vector_store):
        """reset_ingestion_pipeline clears singleton."""
        reset_ingestion_pipeline()

        with patch('src.core.VectorStore') as mock_vs_class:
            mock_vs_class.return_value = mock_vector_store

            p1 = get_ingestion_pipeline()
            reset_ingestion_pipeline()

            with patch('src.core.VectorStore') as mock_vs_class2:
                mock_vs_class2.return_value = mock_vector_store
                p2 = get_ingestion_pipeline()

                assert p1 is not p2


# =============================================================================
# Tests: Chunk Metadata Verification
# =============================================================================

class TestChunkMetadata:
    """Tests verifying chunks have correct metadata structure."""

    def test_sec_chunk_has_public_source_category(self, pipeline, sample_sec_doc):
        """SEC chunks have PUBLIC_SEC source category."""
        with patch('src.ingestion.ingestion_pipeline.extract_10k') as mock_extract:
            mock_extract.return_value = sample_sec_doc

            chunks = pipeline.process_sec_filing("NVDA", 2024, "10-K")

            for chunk in chunks:
                assert chunk.metadata.source_category == DataSourceCategory.PUBLIC_SEC
                assert chunk.metadata.is_public is True

    def test_sec_chunk_has_ticker_and_form(self, pipeline, sample_sec_doc):
        """SEC chunks have ticker and form information."""
        with patch('src.ingestion.ingestion_pipeline.extract_10k') as mock_extract:
            mock_extract.return_value = sample_sec_doc

            chunks = pipeline.process_sec_filing("NVDA", 2024, "10-K")

            for chunk in chunks:
                assert chunk.metadata.ticker == "NVDA"
                assert chunk.metadata.sec_form is not None

    def test_chunk_ids_are_unique(self, pipeline, sample_sec_doc):
        """All chunk IDs are unique."""
        with patch('src.ingestion.ingestion_pipeline.extract_10k') as mock_extract:
            mock_extract.return_value = sample_sec_doc

            chunks = pipeline.process_sec_filing("NVDA", 2024, "10-K")

            chunk_ids = [c.metadata.chunk_id for c in chunks]
            assert len(chunk_ids) == len(set(chunk_ids))