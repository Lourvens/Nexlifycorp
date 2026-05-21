"""
Qdrant Vector Store - Proper LangChain wrapper with metadata handling.

Key Design Decisions:
1. LangChain Qdrant stores metadata under 'metadata' key (by design)
2. Filters use dot notation: 'metadata.is_public' for nested fields
3. We provide both simple dict filter API and Qdrant Filter API
4. Backward compatible with existing code

Requires Qdrant Docker running:
    docker run -d --name nexlify-qdrant -p 6333:6333 -p 6334:6334 \
      -v $(pwd)/data/qdrant:/qdrant/storage qdrant/qdrant

Usage:
    from src.core import VectorStore

    # Basic usage
    vs = VectorStore(collection_name="nexlify_kb")
    vs.add_documents(texts=[...], metadatas=[...])
    
    # Simple dict filter (we convert to Qdrant Filter)
    results = vs.search("revenue", filter={"is_public": True})
    
    # Direct Qdrant Filter (for complex queries)
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    filter = Filter(must=[FieldCondition(key="metadata.is_public", match=MatchValue(value=True))])
    results = vs.search("revenue", filter=filter)
"""
import uuid
from typing import Union
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, Filter, FieldCondition, 
    MatchValue, PayloadSchemaType
)
from langchain_qdrant import QdrantVectorStore
from src.utils.logger import logger


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_COLLECTION = "nexlify_kb"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_DIM = 384
QDRANT_URL = "http://localhost:6333"

# Metadata fields that are commonly used for filtering
# These will be prefixed with 'metadata.' in Qdrant filters
METADATA_FILTER_FIELDS = frozenset([
    "is_public", "content_type", "ticker", "source_category",
    "classification", "access_level", "sec_form", "sec_section",
    "internal_doc_type", "fiscal_year", "fiscal_quarter", "document_id"
])


# =============================================================================
# HELPERS
# =============================================================================

def create_embeddings(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> HuggingFaceEmbeddings:
    """Create embeddings function with CPU."""
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def convert_filter_dict_to_qdrant(
    filter_dict: dict | None,
    metadata_prefix: str = "metadata"
) -> Filter | None:
    """
    Convert a simple dict filter to Qdrant Filter format.
    
    Handles nested metadata fields properly:
        {'is_public': True} -> metadata.is_public=True
    
    Args:
        filter_dict: Simple dict like {'is_public': True}
        metadata_prefix: Prefix for metadata fields (default: 'metadata')
        
    Returns:
        Qdrant Filter object ready for queries
        
    Examples:
        >>> convert_filter_dict_to_qdrant({'is_public': True})
        Filter(must=[FieldCondition(key='metadata.is_public', match=MatchValue(value=True))])
        
        >>> convert_filter_dict_to_qdrant({'is_public': True, 'content_type': 'financial'})
        Filter(must=[FieldCondition(key='metadata.is_public', ...), FieldCondition(key='metadata.content_type', ...)])
    """
    if not filter_dict:
        return None
    
    # If already a Filter, return as-is
    if isinstance(filter_dict, Filter):
        return filter_dict
    
    conditions = []
    
    for key, value in filter_dict.items():
        # Determine the full key path
        if key in METADATA_FILTER_FIELDS:
            # These known metadata fields -> use dot notation
            full_key = f"{metadata_prefix}.{key}"
        elif "." in key:
            # Already has dot notation -> use as-is
            full_key = key
        else:
            # Other fields -> use as-is (might be top-level)
            full_key = key
        
        if isinstance(value, dict):
            # Range filter: {'fiscal_year': {'gte': 2020}}
            conditions.append(FieldCondition(key=full_key, range=value))
        else:
            # Exact match
            conditions.append(FieldCondition(
                key=full_key,
                match=MatchValue(value=value)
            ))
    
    return Filter(must=conditions) if conditions else None


def parse_record_to_document(record) -> Document:
    """Convert Qdrant Record to LangChain Document."""
    payload = record.payload
    
    # Get content from 'page_content'
    content = payload.pop("page_content", "")
    
    # Get metadata (LangChain stores under 'metadata' key)
    metadata = payload.pop("metadata", {})
    
    # Add qdrant_id for reference
    metadata["qdrant_id"] = str(record.id)
    
    # Add any remaining payload fields
    for key, value in payload.items():
        if key not in metadata:
            metadata[key] = value
    
    return Document(page_content=content, metadata=metadata)


# =============================================================================
# VECTOR STORE
# =============================================================================

class VectorStore:
    """
    Simple Qdrant vector store wrapper with proper LangChain integration.
    
    Key design:
    - Uses LangChain QdrantVectorStore (standard LangChain interface)
    - Metadata is stored nested under 'metadata' key (LangChain convention)
    - Filters can be simple dicts (we convert) or Qdrant Filter objects
    
    Why nested metadata?
    - LangChain convention for all vector stores
    - Clean separation of content vs metadata
    - Consistent with Chroma, Pinecone, etc.
    """
    
    def __init__(
        self,
        collection_name: str = DEFAULT_COLLECTION,
        url: str = QDRANT_URL,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        force_recreate: bool = False,
        create_indexes: bool = False,
    ):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the collection to use
            url: Qdrant server URL
            embedding_model: HuggingFace model name for embeddings
            force_recreate: Delete and recreate collection if exists
            create_indexes: Create payload indexes for filter fields (faster reads)
        """
        self.collection_name = collection_name
        self.url = url
        self._create_indexes = create_indexes
        
        logger.info(f"Connecting to Qdrant: {url}")
        
        # Create Qdrant client
        self._client = QdrantClient(url=url)
        
        # Create embeddings
        self._embeddings = create_embeddings(embedding_model)
        
        # Ensure collection exists
        self._setup_collection(force_recreate=force_recreate)
        
        # Create LangChain vector store
        self._vectorstore = self._create_vectorstore()
        
        logger.info(f"VectorStore ready: {collection_name} ({self.count} points)")
    
    def _create_vectorstore(self) -> QdrantVectorStore:
        """Create LangChain QdrantVectorStore."""
        return QdrantVectorStore(
            client=self._client,
            collection_name=self.collection_name,
            embedding=self._embeddings,
            # Default LangChain settings:
            # content_payload_key="page_content"
            # metadata_payload_key="metadata"
        )
    
    def _setup_collection(self, force_recreate: bool = False) -> None:
        """Create collection if it doesn't exist."""
        if self._client.collection_exists(self.collection_name):
            if force_recreate:
                logger.info(f"Deleting collection: {self.collection_name}")
                self._client.delete_collection(self.collection_name)
            else:
                logger.info(f"Collection exists: {self.collection_name}")
                return
        
        logger.info(f"Creating collection: {self.collection_name} (dim={DEFAULT_EMBEDDING_DIM})")
        self._client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=DEFAULT_EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        
        # Optionally create payload indexes
        if self._create_indexes:
            self._create_payload_indexes()
        
        logger.info(f"Collection created: {self.collection_name}")
    
    def _create_payload_indexes(self) -> None:
        """Create payload indexes for commonly filtered fields."""
        # Map field name -> schema type
        field_schemas = {
            "is_public": PayloadSchemaType.BOOL,
            "content_type": PayloadSchemaType.KEYWORD,
            "ticker": PayloadSchemaType.KEYWORD,
            "source_category": PayloadSchemaType.KEYWORD,
            "classification": PayloadSchemaType.KEYWORD,
            "sec_form": PayloadSchemaType.KEYWORD,
            "internal_doc_type": PayloadSchemaType.KEYWORD,
            "fiscal_year": PayloadSchemaType.INTEGER,
            "fiscal_quarter": PayloadSchemaType.INTEGER,
            "document_id": PayloadSchemaType.KEYWORD,
        }
        
        for field, schema in field_schemas.items():
            try:
                # Index the nested field path
                full_path = f"metadata.{field}"
                self._client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=full_path,
                    field_schema=schema,
                )
                logger.info(f"Created index: {full_path}")
            except Exception as e:
                logger.debug(f"Index skipped for {field}: {e}")
    
    def _string_to_uuid(self, id_str: str) -> str:
        """Convert string ID to deterministic UUID."""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, id_str))
    
    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    
    def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document ID strings
            
        Returns:
            List of UUIDs for the added documents
        """
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        if ids is None:
            uuids = [str(uuid.uuid4()) for _ in texts]
        else:
            uuids = [self._string_to_uuid(id_str) for id_str in ids]
            # Add original_id for reference
            for meta, orig_id in zip(metadatas, ids):
                if "original_id" not in meta:
                    meta["original_id"] = orig_id
        
        # Create LangChain Documents
        docs = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadatas)
        ]
        
        self._vectorstore.add_documents(documents=docs, ids=uuids)
        logger.info(f"Added {len(texts)} documents")
        
        return uuids
    
    def add_chunks(self, chunks: list) -> list[str]:
        """Add Chunk objects (from src/ingestion/types.py)."""
        texts = [c.content for c in chunks]
        metadatas = [c.metadata.model_dump(mode="json") for c in chunks]
        ids = [c.metadata.chunk_id for c in chunks]
        
        return self.add_documents(texts, metadatas, ids)
    
    def add_documents_from_chunks(self, chunks: list) -> list[str]:
        """Alias for add_chunks (more descriptive name)."""
        return self.add_chunks(chunks)
    
    def delete(self, ids: list[str]) -> None:
        """Delete documents by original string IDs."""
        uuids = [self._string_to_uuid(id_str) for id_str in ids]
        self._vectorstore.delete(ids=uuids)
        logger.info(f"Deleted {len(ids)} documents")
    
    def clear(self) -> None:
        """Delete the entire collection."""
        self._client.delete_collection(self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")
        self._setup_collection()
    
    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter: Union[dict, Filter, None] = None,
    ) -> list[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter: Optional filter
                - dict: Simple filter like {'is_public': True}
                  (will be converted to Qdrant Filter with metadata. prefix)
                - Filter: Direct Qdrant Filter object
                - None: No filtering
                
        Returns:
            List of matching documents
        """
        # Convert dict filter to Qdrant Filter if needed
        qdrant_filter = convert_filter_dict_to_qdrant(filter)
        
        return self._vectorstore.similarity_search(
            query=query,
            k=k,
            filter=qdrant_filter,
        )
    
    def search_with_scores(
        self,
        query: str,
        k: int = 4,
        filter: Union[dict, Filter, None] = None,
    ) -> list[tuple[Document, float]]:
        """
        Search with relevance scores.
        
        Args:
            query: Search query text
            k: Number of results
            filter: Optional filter (dict or Filter)
            
        Returns:
            List of (document, score) tuples
        """
        qdrant_filter = convert_filter_dict_to_qdrant(filter)
        
        return self._vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=qdrant_filter,
        )
    
    def as_retriever(self, **kwargs):
        """Get as LangChain retriever for use in chains."""
        return self._vectorstore.as_retriever(**kwargs)
    
    # -------------------------------------------------------------------------
    # Info
    # -------------------------------------------------------------------------
    
    @property
    def count(self) -> int:
        """Get number of documents in collection."""
        try:
            info = self._client.get_collection(self.collection_name)
            return info.points_count
        except Exception:
            return 0
    
    def exists(self) -> bool:
        """Check if collection exists."""
        return self._client.collection_exists(self.collection_name)
    
    def get_all(self, limit: int = 1000) -> list[Document]:
        """Get all documents from collection using scroll."""
        records, _ = self._client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        
        return [parse_record_to_document(r) for r in records]
    
    def get_by_ids(self, uuids: list[str]) -> list[Document]:
        """Get documents by their UUIDs."""
        records = self._client.retrieve(
            collection_name=self.collection_name,
            ids=uuids,
            with_payload=True,
        )
        
        return [parse_record_to_document(r) for r in records]
    
    def get_by_original_id(self, original_id: str) -> list[Document]:
        """Get document by its original string ID."""
        records, _ = self._client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(
                    key="metadata.original_id",
                    match=MatchValue(value=original_id)
                )]
            ),
            limit=10,
            with_payload=True,
            with_vectors=False,
        )
        
        return [parse_record_to_document(r) for r in records]


# =============================================================================
# FACTORY
# =============================================================================

def create_vector_store(
    collection_name: str = DEFAULT_COLLECTION,
    url: str = QDRANT_URL,
    **kwargs,
) -> VectorStore:
    """Factory function to create VectorStore instances."""
    return VectorStore(
        collection_name=collection_name,
        url=url,
        **kwargs,
    )


# Backward compatibility singleton
_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Get singleton instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def reset_vector_store() -> None:
    """Reset singleton."""
    global _vector_store
    _vector_store = None