"""Mock data module for testing."""
from tests.mock.data import (
    # Factories
    MockChunkFactory,
    chunk_factory,
    # Datasets
    create_sec_chunks_dataset,
    create_internal_chunks_dataset,
    create_mixed_chunks_dataset,
    # Helpers
    chunk_to_document,
    chunks_to_documents,
    create_mock_documents,
    get_mock_chunks,
    get_mock_documents,
    # Constants
    MOCK_PUBLIC_METADATA,
    MOCK_CONFIDENTIAL_METADATA,
    MOCK_NVDA_METADATA,
    FILTER_TEST_CASES,
)

__all__ = [
    # Factories
    "MockChunkFactory",
    "chunk_factory",
    # Datasets
    "create_sec_chunks_dataset",
    "create_internal_chunks_dataset",
    "create_mixed_chunks_dataset",
    # Helpers
    "chunk_to_document",
    "chunks_to_documents",
    "create_mock_documents",
    "get_mock_chunks",
    "get_mock_documents",
    # Constants
    "MOCK_PUBLIC_METADATA",
    "MOCK_CONFIDENTIAL_METADATA",
    "MOCK_NVDA_METADATA",
    "FILTER_TEST_CASES",
]