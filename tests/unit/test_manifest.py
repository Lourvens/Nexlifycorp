"""Unit tests for ingestion manifest and auto-ingest functionality."""
import json
import tempfile
from pathlib import Path
import pytest

from src.ingestion.manifest import IngestionManifest


class TestIngestionManifest:
    """Test IngestionManifest class."""

    @pytest.fixture
    def temp_manifest(self):
        """Create temporary manifest file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"documents": {}}')
            return Path(f.name)

    @pytest.fixture
    def manifest_with_data(self, temp_manifest):
        """Create manifest with sample data."""
        data = {
            "documents": {
                "NVDA_10K_2024": {
                    "type": "sec",
                    "ticker": "NVDA",
                    "form": "10-K",
                    "year": 2024,
                    "ingested_at": "2026-05-22T10:00:00",
                    "chunks": 228
                },
                "TEST-001": {
                    "type": "internal",
                    "doc_type": "board_memo",
                    "ingested_at": "2026-05-22T11:00:00",
                    "chunks": 15
                }
            }
        }
        with open(temp_manifest, 'w') as f:
            json.dump(data, f)
        return temp_manifest

    def test_load_empty_manifest(self, temp_manifest):
        """Loading empty manifest creates empty documents dict."""
        manifest = IngestionManifest(temp_manifest)
        assert manifest.count == 0

    def test_load_manifest_with_data(self, manifest_with_data):
        """Loading manifest with data populates documents."""
        manifest = IngestionManifest(manifest_with_data)
        assert manifest.count == 2
        assert manifest.is_ingested("NVDA_10K_2024")
        assert manifest.is_ingested("TEST-001")
        assert not manifest.is_ingested("UNKNOWN")

    def test_is_ingested_returns_true_for_known_doc(self, manifest_with_data):
        """is_ingested returns True for existing document."""
        manifest = IngestionManifest(manifest_with_data)
        assert manifest.is_ingested("NVDA_10K_2024") is True

    def test_is_ingested_returns_false_for_unknown_doc(self, manifest_with_data):
        """is_ingested returns False for unknown document."""
        manifest = IngestionManifest(manifest_with_data)
        assert manifest.is_ingested("UNKNOWN_DOC") is False

    def test_get_returns_document_metadata(self, manifest_with_data):
        """get returns document metadata dict."""
        manifest = IngestionManifest(manifest_with_data)
        doc = manifest.get("NVDA_10K_2024")
        assert doc is not None
        assert doc["ticker"] == "NVDA"
        assert doc["chunks"] == 228

    def test_get_returns_none_for_unknown(self, manifest_with_data):
        """get returns None for unknown document."""
        manifest = IngestionManifest(manifest_with_data)
        assert manifest.get("UNKNOWN") is None

    def test_mark_ingested_adds_document(self, temp_manifest):
        """mark_ingested adds new document to manifest."""
        manifest = IngestionManifest(temp_manifest)
        manifest.mark_ingested(
            doc_id="AAPL_10K_2024",
            doc_type="sec",
            chunks=200,
            ticker="AAPL",
            form="10-K",
            year=2024
        )
        assert manifest.is_ingested("AAPL_10K_2024")
        doc = manifest.get("AAPL_10K_2024")
        assert doc["type"] == "sec"
        assert doc["chunks"] == 200
        assert "ingested_at" in doc

    def test_remove_deletes_document(self, manifest_with_data):
        """remove deletes document from manifest."""
        manifest = IngestionManifest(manifest_with_data)
        assert manifest.is_ingested("NVDA_10K_2024")
        result = manifest.remove("NVDA_10K_2024")
        assert result is True
        assert not manifest.is_ingested("NVDA_10K_2024")
        assert manifest.count == 1

    def test_remove_returns_false_for_unknown(self, manifest_with_data):
        """remove returns False for unknown document."""
        manifest = IngestionManifest(manifest_with_data)
        result = manifest.remove("UNKNOWN")
        assert result is False

    def test_list_by_type_filters_correctly(self, manifest_with_data):
        """list_by_type returns only documents of specified type."""
        manifest = IngestionManifest(manifest_with_data)
        sec_docs = manifest.list_by_type("sec")
        internal_docs = manifest.list_by_type("internal")
        assert "NVDA_10K_2024" in sec_docs
        assert "TEST-001" in internal_docs
        assert len(sec_docs) == 1
        assert len(internal_docs) == 1

    def test_list_all_returns_all_documents(self, manifest_with_data):
        """list_all returns all documents with metadata."""
        manifest = IngestionManifest(manifest_with_data)
        all_docs = manifest.list_all()
        assert len(all_docs) == 2
        doc_ids = [d[0] for d in all_docs]
        assert "NVDA_10K_2024" in doc_ids
        assert "TEST-001" in doc_ids

    def test_count_returns_total_documents(self, manifest_with_data):
        """count returns total number of documents."""
        manifest = IngestionManifest(manifest_with_data)
        assert manifest.count == 2


class TestManifestPersistence:
    """Test manifest file persistence."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    def test_manifest_saves_to_file(self, temp_dir):
        """mark_ingested persists to file."""
        manifest_path = temp_dir / ".ingestion_manifest.json"
        manifest = IngestionManifest(manifest_path)
        manifest.mark_ingested("DOC1", "sec", 100)
        manifest.save()

        # Load new instance to verify persistence
        manifest2 = IngestionManifest(manifest_path)
        assert manifest2.is_ingested("DOC1")
        assert manifest2.get("DOC1")["chunks"] == 100

    def test_manifest_loads_nonexistent_file(self, temp_dir):
        """Loading nonexistent manifest creates empty manifest."""
        manifest_path = temp_dir / ".ingestion_manifest.json"
        manifest = IngestionManifest(manifest_path)
        assert manifest.count == 0
