"""Unit tests for vector store - simplified with proper mocking."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.core.config import (
    get_config,
    get_qdrant_url,
    get_collection_name,
)
from src.core.vector_store import (
    VectorStore,
    create_vector_store,
    get_vector_store,
    reset_vector_store,
    create_embeddings,
    convert_filter_dict_to_qdrant,
    parse_record_to_document,
    DEFAULT_COLLECTION,
    DEFAULT_EMBEDDING_DIM,
    QDRANT_URL,
    METADATA_FILTER_FIELDS,
)
from src.ingestion.types import (
    Chunk,
    ChunkMetadata,
    DataSourceCategory,
    AccessLevel,
    ContentType,
)

# Import mock data
from tests.mock import (
    create_sec_chunks_dataset,
    create_internal_chunks_dataset,
    create_mixed_chunks_dataset,
    chunk_to_document,
    chunks_to_documents,
    get_mock_chunks,
    get_mock_documents,
    MOCK_PUBLIC_METADATA,
    MOCK_CONFIDENTIAL_METADATA,
    FILTER_TEST_CASES,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_vectorstore():
    """Create a fully mocked VectorStore for unit tests.
    
    Patches at the module level where VectorStore uses the classes.
    """
    # Create mock embeddings that look like the real thing
    mock_emb = MagicMock()
    mock_emb.embed_query.return_value = [0.1] * 384
    mock_emb.embed_documents.return_value = [[0.1] * 384]
    
    # Create mock client
    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    
    # Create mock internal vectorstore
    mock_vs_internal = MagicMock()
    
    # Patch where VectorStore actually uses them in its own module
    with patch("src.core.vector_store.create_embeddings", return_value=mock_emb), \
         patch("src.core.vector_store.QdrantClient", return_value=mock_client), \
         patch("src.core.vector_store.QdrantVectorStore", return_value=mock_vs_internal):
        
        # Create VectorStore instance
        vs = VectorStore(collection_name="test_mock")
        
        # Replace internal vectorstore with our mock
        vs._vectorstore = mock_vs_internal
        vs._client = mock_client
        
        yield vs, mock_vs_internal, mock_client


# =============================================================================
# Test Constants
# =============================================================================

class TestConstants:
    """Tests for exported constants."""

    def test_default_collection(self):
        assert DEFAULT_COLLECTION == "nexlify_kb"

    def test_default_embedding_dim(self):
        assert DEFAULT_EMBEDDING_DIM == 384

    def test_qdrant_url_default(self):
        assert QDRANT_URL == "http://localhost:6333"

    def test_metadata_filter_fields_defined(self):
        assert "is_public" in METADATA_FILTER_FIELDS
        assert "content_type" in METADATA_FILTER_FIELDS
        assert "ticker" in METADATA_FILTER_FIELDS


# =============================================================================
# Test Config
# =============================================================================

class TestConfig:
    """Tests for configuration."""

    def test_get_config_returns_config(self):
        config = get_config()
        assert config is not None
        assert hasattr(config, "qdrant_url")

    def test_get_qdrant_url(self):
        url = get_qdrant_url()
        assert url.startswith("http://")

    def test_get_collection_name(self):
        name = get_collection_name()
        assert isinstance(name, str)
        assert len(name) > 0


# =============================================================================
# Test Embeddings
# =============================================================================

class TestCreateEmbeddings:
    """Tests for embeddings creation."""

    def test_create_embeddings_returns_embeddings(self):
        embeddings = create_embeddings()
        assert embeddings is not None

    @pytest.mark.skip(reason="Skipped to avoid model download time in CI")
    def test_create_embeddings_with_custom_model(self):
        embeddings = create_embeddings("sentence-transformers/all-mpnet-base-v2")
        assert embeddings is not None


# =============================================================================
# Test Filter Conversion
# =============================================================================

class TestConvertFilterDictToQdrant:
    """Tests for filter dict to Qdrant Filter conversion."""

    def test_none_filter_returns_none(self):
        result = convert_filter_dict_to_qdrant(None)
        assert result is None

    def test_empty_filter_returns_none(self):
        result = convert_filter_dict_to_qdrant({})
        assert result is None

    def test_single_field_filter(self):
        result = convert_filter_dict_to_qdrant({"is_public": True})
        
        assert result is not None
        assert hasattr(result, "must")
        assert len(result.must) == 1
        assert result.must[0].key == "metadata.is_public"

    def test_multiple_field_filter(self):
        result = convert_filter_dict_to_qdrant({
            "is_public": True,
            "content_type": "financial",
        })
        
        assert result is not None
        assert len(result.must) == 2
        keys = {c.key for c in result.must}
        assert "metadata.is_public" in keys
        assert "metadata.content_type" in keys

    def test_range_filter(self):
        result = convert_filter_dict_to_qdrant({
            "fiscal_year": {"gte": 2020}
        })
        
        assert result is not None
        assert result.must[0].key == "metadata.fiscal_year"
        assert result.must[0].range is not None

    def test_already_dotted_key_passthrough(self):
        result = convert_filter_dict_to_qdrant({
            "metadata.custom_field": "value"
        })
        
        assert result.must[0].key == "metadata.custom_field"

    def test_non_metadata_field_no_prefix(self):
        result = convert_filter_dict_to_qdrant({
            "custom_field": "value"
        })
        
        # custom_field is not in METADATA_FILTER_FIELDS
        assert result.must[0].key == "custom_field"

    def test_passes_through_qdrant_filter(self):
        """Test that direct Qdrant Filter objects pass through."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        direct_filter = Filter(must=[
            FieldCondition(key="metadata.is_public", match=MatchValue(value=True))
        ])
        
        result = convert_filter_dict_to_qdrant(direct_filter)
        
        assert result is direct_filter


# =============================================================================
# Test Parse Record to Document
# =============================================================================

class TestParseRecordToDocument:
    """Tests for parsing Qdrant records to Documents."""

    def test_parses_standard_record(self):
        mock_record = Mock()
        mock_record.id = "test-uuid-123"
        mock_record.payload = {
            "page_content": "Test content",
            "metadata": {"is_public": True, "ticker": "NVDA"},
        }
        
        doc = parse_record_to_document(mock_record)
        
        assert doc.page_content == "Test content"
        assert doc.metadata["is_public"] is True
        assert doc.metadata["ticker"] == "NVDA"
        assert doc.metadata["qdrant_id"] == "test-uuid-123"

    def test_handles_extra_payload_fields(self):
        mock_record = Mock()
        mock_record.id = "test-uuid-456"
        mock_record.payload = {
            "page_content": "Content",
            "metadata": {"key": "value"},
            "extra_field": "extra_value",
        }
        
        doc = parse_record_to_document(mock_record)
        
        assert doc.metadata["extra_field"] == "extra_value"


# =============================================================================
# Test Mock Data
# =============================================================================

class TestMockData:
    """Tests for mock data generation."""

    def test_create_sec_chunks_dataset(self):
        chunks = create_sec_chunks_dataset()
        
        assert len(chunks) == 3
        assert all(c.metadata.is_public for c in chunks)
        assert all(c.metadata.ticker == "NVDA" for c in chunks)

    def test_create_internal_chunks_dataset(self):
        chunks = create_internal_chunks_dataset()
        
        assert len(chunks) == 3
        assert all(not c.metadata.is_public for c in chunks)

    def test_create_mixed_chunks_dataset(self):
        chunks = create_mixed_chunks_dataset()
        
        assert len(chunks) == 6
        public_count = sum(1 for c in chunks if c.metadata.is_public)
        private_count = sum(1 for c in chunks if not c.metadata.is_public)
        assert public_count == 3
        assert private_count == 3

    def test_chunks_to_documents_conversion(self):
        chunks = create_sec_chunks_dataset()
        docs = chunks_to_documents(chunks)
        
        assert len(docs) == len(chunks)
        assert all(hasattr(d, "page_content") for d in docs)
        assert all(hasattr(d, "metadata") for d in docs)

    def test_get_mock_chunks(self):
        chunks = get_mock_chunks()
        assert len(chunks) > 0

    def test_get_mock_documents(self):
        docs = get_mock_documents()
        assert len(docs) > 0


# =============================================================================
# Test VectorStore with Fixtures (Mocked)
# =============================================================================

class TestVectorStoreCRUD:
    """Tests for VectorStore CRUD operations."""

    def test_add_documents(self, mock_vectorstore):
        vs, mock_vs, _ = mock_vectorstore
        
        ids = vs.add_documents(
            texts=["doc1", "doc2"],
            metadatas=[{"key": "value1"}, {"key": "value2"}],
        )
        
        assert len(ids) == 2
        mock_vs.add_documents.assert_called_once()

    def test_add_documents_with_ids(self, mock_vectorstore):
        vs, mock_vs, _ = mock_vectorstore
        
        ids = vs.add_documents(
            texts=["doc1"],
            metadatas=[{"key": "value"}],
            ids=["custom-id-1"],
        )
        
        assert len(ids) == 1
        # Original ID should be added to metadata
        call_args = mock_vs.add_documents.call_args
        docs = call_args.kwargs["documents"]
        assert docs[0].metadata["original_id"] == "custom-id-1"

    def test_add_chunks(self, mock_vectorstore):
        vs, mock_vs, _ = mock_vectorstore
        
        chunks = get_mock_chunks()
        ids = vs.add_chunks(chunks)
        
        assert len(ids) == len(chunks)

    def test_delete(self, mock_vectorstore):
        vs, mock_vs, _ = mock_vectorstore
        
        vs.delete(["id1", "id2"])
        
        mock_vs.delete.assert_called_once()


# =============================================================================
# Test VectorStore Search (Mocked)
# =============================================================================

class TestVectorStoreSearch:
    """Tests for VectorStore search operations."""

    def test_search_basic(self, mock_vectorstore):
        vs, mock_vs, _ = mock_vectorstore
        
        mock_doc = Mock()
        mock_vs.similarity_search.return_value = [mock_doc]
        
        results = vs.search("test query", k=5)
        
        assert len(results) == 1
        mock_vs.similarity_search.assert_called_once()

    def test_search_with_dict_filter(self, mock_vectorstore):
        vs, mock_vs, _ = mock_vectorstore
        
        mock_vs.similarity_search.return_value = []
        
        vs.search("test", filter={"is_public": True})
        
        # Verify filter was converted to Qdrant Filter
        call_args = mock_vs.similarity_search.call_args
        qdrant_filter = call_args.kwargs["filter"]
        assert qdrant_filter is not None
        assert qdrant_filter.must[0].key == "metadata.is_public"

    def test_search_with_qdrant_filter(self, mock_vectorstore):
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        vs, mock_vs, _ = mock_vectorstore
        
        direct_filter = Filter(must=[
            FieldCondition(key="metadata.is_public", match=MatchValue(value=True))
        ])
        
        vs.search("test", filter=direct_filter)
        
        # Direct filter should pass through unchanged
        call_args = mock_vs.similarity_search.call_args
        passed_filter = call_args.kwargs["filter"]
        assert passed_filter is direct_filter

    def test_search_with_scores(self, mock_vectorstore):
        vs, mock_vs, _ = mock_vectorstore
        
        mock_doc = Mock()
        mock_vs.similarity_search_with_score.return_value = [(mock_doc, 0.95)]
        
        results = vs.search_with_scores("test", k=5)
        
        assert len(results) == 1
        assert results[0][1] == 0.95


# =============================================================================
# Test VectorStore Info (Mocked)
# =============================================================================

class TestVectorStoreInfo:
    """Tests for VectorStore info methods."""

    def test_count(self, mock_vectorstore):
        vs, _, mock_client = mock_vectorstore
        
        mock_info = Mock()
        mock_info.points_count = 42
        mock_client.get_collection.return_value = mock_info
        
        assert vs.count == 42

    def test_exists(self, mock_vectorstore):
        vs, _, mock_client = mock_vectorstore
        
        result = vs.exists()
        
        assert result is True
        mock_client.collection_exists.assert_called_with("test_mock")

    def test_get_all(self, mock_vectorstore):
        vs, _, mock_client = mock_vectorstore
        
        mock_record = Mock()
        mock_record.id = "uuid-123"
        mock_record.payload = {
            "page_content": "Test",
            "metadata": {"key": "value"},
        }
        mock_client.scroll.return_value = ([mock_record], None)
        
        docs = vs.get_all()
        
        assert len(docs) == 1
        assert docs[0].page_content == "Test"


# =============================================================================
# Test Factory and Singleton
# =============================================================================

class TestFactoryAndSingleton:
    """Tests for factory and singleton patterns."""

    def test_reset_clears_singleton(self):
        import src.core.vector_store as vs_module
        
        vs_module._vector_store = Mock()
        
        reset_vector_store()
        
        assert vs_module._vector_store is None


# =============================================================================
# Integration Tests (require Qdrant running)
# =============================================================================

@pytest.mark.slow
class TestVectorStoreIntegration:
    """Integration tests that require Qdrant running."""

    def test_full_workflow_with_mock_data(self):
        """Test full workflow with mock data."""
        vs = VectorStore(collection_name="test_integration", force_recreate=True)
        
        # Add chunks
        chunks = get_mock_chunks()
        ids = vs.add_chunks(chunks)
        assert len(ids) == len(chunks)
        
        # Search with filter
        results = vs.search("revenue", k=10, filter={"is_public": True})
        assert isinstance(results, list)
        
        # Get all
        all_docs = vs.get_all()
        assert len(all_docs) == len(chunks)
        
        # Cleanup
        vs.clear()

    def test_filter_equivalence(self):
        """Test that dict and Qdrant Filter give same results."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        vs = VectorStore(collection_name="test_filter", force_recreate=True)
        
        # Add test data
        vs.add_documents(
            texts=["Public doc", "Private doc"],
            metadatas=[
                {"is_public": True, "content_type": "public"},
                {"is_public": False, "content_type": "private"},
            ],
        )
        
        # Dict filter
        results_dict = vs.search("doc", filter={"is_public": True})
        
        # Qdrant Filter
        qdrant_filter = Filter(must=[
            FieldCondition(key="metadata.is_public", match=MatchValue(value=True))
        ])
        results_qdrant = vs.search("doc", filter=qdrant_filter)
        
        # Should return same documents
        assert len(results_dict) == len(results_qdrant)
        
        # Cleanup
        vs.clear()