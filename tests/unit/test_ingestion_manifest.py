"""Tests for manifest integration in ingestion pipeline."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ingestion.ingestion_pipeline import IngestionPipeline, _get_doc_id


class TestGetDocId:
    """Test _get_doc_id helper function."""

    def test_generates_correct_doc_id_with_year(self):
        """_get_doc_id generates correct ID with year."""
        doc_id = _get_doc_id("NVDA", "10-K", 2024)
        assert doc_id == "NVDA_10K_2024"

    def test_generates_correct_doc_id_without_year(self):
        """_get_doc_id generates correct ID with 'latest' when year is None."""
        doc_id = _get_doc_id("NVDA", "10-K", None)
        assert doc_id == "NVDA_10K_latest"

    def test_removes_hyphen_from_form(self):
        """_get_doc_id removes hyphen from form."""
        doc_id = _get_doc_id("AAPL", "10-Q", 2024)
        assert doc_id == "AAPL_10Q_2024"


class TestManifestIntegration:
    """Test manifest integration in IngestionPipeline."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        vs = Mock()
        vs.add_chunks = Mock()
        return vs

    @pytest.fixture
    def mock_manifest(self):
        """Create mock manifest."""
        with patch('src.ingestion.ingestion_pipeline.get_manifest') as mock:
            manifest = Mock()
            manifest.is_ingested = Mock(return_value=False)
            manifest.mark_ingested = Mock()
            mock.return_value = manifest
            yield manifest

    @pytest.fixture
    def pipeline(self, mock_vector_store):
        """Create pipeline with mock vector store."""
        return IngestionPipeline(mock_vector_store)

    def test_sec_ingestion_checks_manifest(self, pipeline, mock_manifest):
        """ingest_sec_filing checks manifest before ingesting."""
        with patch.object(pipeline, 'process_sec_filing', return_value=[]) as mock_process:
            mock_manifest.is_ingested.return_value = True

            result = pipeline.ingest_sec_filing("NVDA", 2024)

            mock_manifest.is_ingested.assert_called_once_with("NVDA_10K_2024")
            mock_process.assert_not_called()

    def test_sec_ingestion_skips_when_already_ingested(self, pipeline, mock_manifest):
        """ingest_sec_filing skips if already in manifest."""
        mock_manifest.is_ingested.return_value = True

        result = pipeline.ingest_sec_filing("NVDA", 2024)

        assert result == 0
        pipeline.vector_store.add_chunks.assert_not_called()

    def test_sec_ingestion_ingests_when_not_in_manifest(self, pipeline, mock_manifest, mock_vector_store):
        """ingest_sec_filing ingests when not in manifest."""
        mock_manifest.is_ingested.return_value = False
        mock_chunks = [Mock(), Mock()]
        with patch.object(pipeline, 'process_sec_filing', return_value=mock_chunks):
            result = pipeline.ingest_sec_filing("NVDA", 2024)

            mock_vector_store.add_chunks.assert_called_once_with(mock_chunks)
            mock_manifest.mark_ingested.assert_called_once()

    def test_sec_ingestion_marks_manifest_on_success(self, pipeline, mock_manifest, mock_vector_store):
        """ingest_sec_filing marks manifest after successful ingest."""
        mock_manifest.is_ingested.return_value = False
        mock_chunks = [Mock(), Mock(), Mock()]
        with patch.object(pipeline, 'process_sec_filing', return_value=mock_chunks):
            result = pipeline.ingest_sec_filing("NVDA", 2024)

            call_args = mock_manifest.mark_ingested.call_args
            assert call_args[1]['doc_id'] == "NVDA_10K_2024"
            assert call_args[1]['doc_type'] == "sec"
            assert call_args[1]['chunks'] == 3

    def test_internal_ingestion_checks_manifest(self, pipeline, mock_manifest):
        """ingest_internal_doc checks manifest before ingesting."""
        mock_manifest.is_ingested.return_value = True

        result = pipeline.ingest_internal_doc("TEST-001", "board_memo", "# Title\nContent")

        mock_manifest.is_ingested.assert_called_once_with("TEST-001")
        pipeline.vector_store.add_chunks.assert_not_called()

    def test_internal_ingestion_skips_when_already_ingested(self, pipeline, mock_manifest):
        """ingest_internal_doc skips if already in manifest."""
        mock_manifest.is_ingested.return_value = True

        result = pipeline.ingest_internal_doc("TEST-001", "board_memo", "# Title\nContent")

        assert result == 0

    def test_internal_ingestion_ingests_when_not_in_manifest(self, pipeline, mock_manifest, mock_vector_store):
        """ingest_internal_doc ingests when not in manifest."""
        mock_manifest.is_ingested.return_value = False
        mock_chunks = [Mock(), Mock()]
        with patch.object(pipeline, 'process_internal_doc', return_value=mock_chunks):
            result = pipeline.ingest_internal_doc("TEST-001", "board_memo", "# Title\nContent")

            mock_vector_store.add_chunks.assert_called_once_with(mock_chunks)
            mock_manifest.mark_ingested.assert_called_once()

    def test_internal_ingestion_marks_manifest_on_success(self, pipeline, mock_manifest, mock_vector_store):
        """ingest_internal_doc marks manifest after successful ingest."""
        mock_manifest.is_ingested.return_value = False
        mock_chunks = [Mock()]
        with patch.object(pipeline, 'process_internal_doc', return_value=mock_chunks):
            result = pipeline.ingest_internal_doc("TEST-001", "board_memo", "# Title\nContent")

            call_args = mock_manifest.mark_ingested.call_args
            assert call_args[1]['doc_id'] == "TEST-001"
            assert call_args[1]['doc_type'] == "internal"
            assert call_args[1]['chunks'] == 1