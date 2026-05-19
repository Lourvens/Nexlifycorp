"""Chunk Builder - Converts extracted sections to unified Chunks.

NOTE: This module is NOT fully implemented yet. 
We're building towards unified Chunk storage in Chroma.

Architecture:
    Extractor Output          Chunk Builder           Chroma Storage
    ┌─────────────────┐       ┌─────────────────┐     ┌─────────────────┐
    │ SECSection      │──────►│                  │     │                 │
    │ InternalSection │       │  Chunk Builder  │────►│  Chroma DB      │
    └─────────────────┘       │  (TODO)         │     │                 │
                             │                  │     └─────────────────┘
                             └─────────────────┘

Current Status:
- types.py: ✅ Unified Chunk type defined
- Chunk Builder: 🔄 STUB - not implemented yet
- Next: Implement conversion logic
"""

from typing import Optional

from src.ingestion.types import (
    Chunk,
    ChunkMetadata,
    SECSection,
    InternalSection,
    DataSourceCategory,
    AccessLevel,
    ContentType,
)


def section_to_chunk(
    section: SECSection | InternalSection,
    **kwargs,
) -> Optional[Chunk]:
    """
    Convert an extracted section to a unified Chunk.
    
    Args:
        section: Either SECSection or InternalSection
        **kwargs: Additional metadata fields
        
    Returns:
        Chunk object ready for embedding and storage
        
    TODO: Implement this
    
    Example usage (when implemented):
    
        # From SEC filing
        sec_section = SECSection(name="Risk Factors", content="...")
        chunk = section_to_chunk(
            sec_section,
            ticker="NVDA",
            source_category=DataSourceCategory.PUBLIC_SEC,
        )
        
        # From internal doc
        internal_section = InternalSection(title="NEXL-X4 Roadmap", ...)
        chunk = section_to_chunk(
            internal_section,
            internal_doc_type=InternalDocType.PRODUCT_ROADMAP,
            source_category=DataSourceCategory.INTERNAL_NEXLIFY,
        )
    """
    raise NotImplementedError(
        "Chunk builder not yet implemented. "
        "See src/ingestion/types.py for the unified Chunk type definition."
    )


# =============================================================================
# PLANNED IMPLEMENTATION
# =============================================================================

"""
Implementation will follow this pattern:

1. Source Detection:
   - Check if section has 'ticker' attr → SEC filing
   - Check if section has 'document_type' attr → Internal doc

2. Metadata Mapping:
   SEC Section → ChunkMetadata:
   - ticker = section.ticker (from metadata)
   - sec_section = section.name
   - source_category = PUBLIC_SEC
   - is_public = True
   - access_level = PUBLIC
   
   Internal Section → ChunkMetadata:
   - internal_doc_type = section.document_type
   - internal_section_path = section.section_path
   - source_category = INTERNAL_NEXLIFY
   - is_public = False
   - access_level = map_classification(section.classification)

3. Content Indicators:
   - contains_financials = detect_financials(content)
   - contains_projections = detect_projections(content)
   - topics = extract_keywords(content)

4. Chunk ID Generation:
   - Format: {source}_{doc_id}_{section_index}
   - Example: "nvda_10k_2025_risk_001"
"""