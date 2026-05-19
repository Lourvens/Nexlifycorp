"""SEC Filing Extraction Module."""
from src.ingestion.sec_filing_extractor import extract_10k, extract_10q
from src.ingestion.types import (
    SEC10K,
    SECMetadata,
    SECSection,
    SECFinancials,
    DataSource,
)
from src.ingestion.internal_doc_processor import (
    extract_internal_document,
    extract_all_internal_documents,
    InternalSection,
    InternalDocument,
)

__all__ = [
    # SEC Filing
    "extract_10k",
    "extract_10q",
    "SEC10K",
    "SECMetadata",
    "SECSection",
    "SECFinancials",
    "DataSource",
    # Internal Document
    "extract_internal_document",
    "extract_all_internal_documents",
    "InternalSection",
    "InternalDocument",
]