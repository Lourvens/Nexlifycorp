"""Mock data generators for testing."""
from dataclasses import dataclass
from typing import Generator
import uuid

from src.ingestion.types import (
    Chunk,
    ChunkMetadata,
    DataSourceCategory,
    AccessLevel,
    ContentType,
)
from langchain_core.documents import Document


# =============================================================================
# MOCK CHUNKS
# =============================================================================

@dataclass
class MockChunkFactory:
    """Factory for creating mock chunks with consistent IDs."""
    
    base_id: str = "mock_chunk"
    base_doc_id: str = "mock_doc"
    counter: int = 0
    
    def reset(self) -> None:
        """Reset counter for fresh sequences."""
        self.counter = 0
    
    def create(
        self,
        content: str | None = None,
        is_public: bool = True,
        content_type: ContentType = ContentType.RISK_FACTORS,
        ticker: str | None = None,
        fiscal_year: int = 2024,
        source_category: DataSourceCategory = DataSourceCategory.PUBLIC_SEC,
        access_level: AccessLevel | None = None,
        **metadata_overrides,
    ) -> Chunk:
        """Create a single mock chunk."""
        self.counter += 1
        chunk_id = f"{self.base_id}_{self.counter:03d}"
        
        # Determine access level from is_public unless explicitly provided
        if access_level is None:
            access_level = AccessLevel.PUBLIC if is_public else AccessLevel.CONFIDENTIAL
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            document_id=f"{self.base_doc_id}_001",
            source_category=source_category,
            source_detail="mock_test_data",
            access_level=access_level,
            is_public=is_public,
            content_type=content_type,
            ticker=ticker,
            fiscal_year=fiscal_year,
            **metadata_overrides,
        )
        
        return Chunk(
            content=content or f"Mock content {self.counter}: Sample text for testing.",
            metadata=metadata,
        )
    
    def create_batch(self, count: int, **kwargs) -> list[Chunk]:
        """Create multiple mock chunks."""
        return [self.create(**kwargs) for _ in range(count)]


# Default factory instance
chunk_factory = MockChunkFactory()


# =============================================================================
# SAMPLE DATASETS
# =============================================================================

def create_sec_chunks_dataset() -> list[Chunk]:
    """Create a dataset of SEC document chunks."""
    factory = MockChunkFactory(base_id="sec_chunk", base_doc_id="sec_doc")
    
    return [
        factory.create(
            content="[Item 1] Business Overview: NVIDIA is a technology company specializing in graphics processing units.",
            is_public=True,
            content_type=ContentType.BUSINESS_DESCRIPTION,
            ticker="NVDA",
            fiscal_year=2024,
            source_category=DataSourceCategory.PUBLIC_SEC,
        ),
        factory.create(
            content="[Item 1A] Risk Factors: We face intense competition in the AI chip market from AMD, Intel, and custom silicon providers.",
            is_public=True,
            content_type=ContentType.RISK_FACTORS,
            ticker="NVDA",
            fiscal_year=2024,
            source_category=DataSourceCategory.PUBLIC_SEC,
        ),
        factory.create(
            content="[Item 7] MD&A: Revenue increased 122% year-over-year driven by Data Center demand for AI training.",
            is_public=True,
            content_type=ContentType.MANAGEMENT_DISCUSSION,
            ticker="NVDA",
            fiscal_year=2024,
            source_category=DataSourceCategory.PUBLIC_SEC,
        ),
    ]


def create_internal_chunks_dataset() -> list[Chunk]:
    """Create a dataset of internal document chunks."""
    factory = MockChunkFactory(base_id="internal_chunk", base_doc_id="internal_doc")
    
    return [
        factory.create(
            content="CONFIDENTIAL: Strategic planning discussion for Q1 2025 expansion into new markets.",
            is_public=False,
            content_type=ContentType.STRATEGY,
            source_category=DataSourceCategory.INTERNAL_NEXLIFY,
            access_level=AccessLevel.CONFIDENTIAL,
        ),
        factory.create(
            content="CONFIDENTIAL: Board presentation on financial performance and budget allocation for FY2025.",
            is_public=False,
            content_type=ContentType.GOVERNANCE,
            source_category=DataSourceCategory.INTERNAL_NEXLIFY,
            access_level=AccessLevel.CONFIDENTIAL,
        ),
        factory.create(
            content="CONFIDENTIAL: Product roadmap discussion covering new features and market positioning.",
            is_public=False,
            content_type=ContentType.PRODUCT_ROADMAP,
            source_category=DataSourceCategory.INTERNAL_NEXLIFY,
            access_level=AccessLevel.STRICTLY_CONFIDENTIAL,
        ),
    ]


def create_mixed_chunks_dataset() -> list[Chunk]:
    """Create a mixed dataset with public and private chunks."""
    public = create_sec_chunks_dataset()
    private = create_internal_chunks_dataset()
    return public + private


# =============================================================================
# MOCK DOCUMENTS
# =============================================================================

def chunk_to_document(chunk: Chunk) -> Document:
    """Convert a Chunk to a LangChain Document."""
    return Document(
        page_content=chunk.content,
        metadata=chunk.metadata.model_dump(mode="json"),
    )


def chunks_to_documents(chunks: list[Chunk]) -> list[Document]:
    """Convert multiple Chunks to Documents."""
    return [chunk_to_document(c) for c in chunks]


def create_mock_documents(count: int = 5, **kwargs) -> list[Document]:
    """Create mock LangChain Documents."""
    chunks = chunk_factory.create_batch(count, **kwargs)
    return chunks_to_documents(chunks)


# =============================================================================
# MOCK METADATA
# =============================================================================

MOCK_PUBLIC_METADATA = {
    "is_public": True,
    "access_level": AccessLevel.PUBLIC.value,
    "source_category": DataSourceCategory.PUBLIC_SEC.value,
}

MOCK_CONFIDENTIAL_METADATA = {
    "is_public": False,
    "access_level": AccessLevel.CONFIDENTIAL.value,
    "source_category": DataSourceCategory.INTERNAL_NEXLIFY.value,
}

MOCK_NVDA_METADATA = {
    "is_public": True,
    "ticker": "NVDA",
    "source_category": DataSourceCategory.PUBLIC_SEC.value,
}


# =============================================================================
# FILTER TEST CASES
# =============================================================================

FILTER_TEST_CASES = [
    # (description, filter_dict, expected_matches)
    (
        "Public documents only",
        {"is_public": True},
        "public",
    ),
    (
        "Private documents only",
        {"is_public": False},
        "private",
    ),
    (
        "NVDA ticker",
        {"is_public": True, "ticker": "NVDA"},
        "ticker",
    ),
    (
        "Risk factors content type",
        {"is_public": True, "content_type": ContentType.RISK_FACTORS.value},
        "risk",
    ),
]


# =============================================================================
# PYTEST FIXTURES
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def get_mock_chunks(**kwargs) -> list[Chunk]:
    """Get mock chunks for testing."""
    return create_mixed_chunks_dataset()


def get_mock_documents(**kwargs) -> list[Document]:
    """Get mock documents for testing."""
    return chunks_to_documents(get_mock_chunks(**kwargs))