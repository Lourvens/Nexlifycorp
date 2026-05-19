"""Internal Document Chunker - H3 header extraction.

Extracts H3 sections from internal documents with H2 parent context.

Algorithm:
    1. Filter: H3 sections only (skip H2 containers, H1 title)
    2. Find parent H2 for section_path
    3. Build chunk content: "H2 / H3: content"
    4. Skip empty sections
"""
import re
from typing import Generator

from src.ingestion.types import (
    InternalSection,
    InternalDocument,
    Chunk,
    ChunkMetadata,
    DataSourceCategory,
    AccessLevel,
    ContentType,
    InternalDocType,
)


# Map folder name to InternalDocType
DOC_TYPE_MAPPING = {
    "annual_review": InternalDocType.ANNUAL_REVIEW,
    "board-memo": InternalDocType.BOARD_MEMO,
    "board_memo": InternalDocType.BOARD_MEMO,
    "product-roadmap": InternalDocType.PRODUCT_ROADMAP,
    "product_roadmap": InternalDocType.PRODUCT_ROADMAP,
    "risk-register": InternalDocType.RISK_REGISTER,
    "risk_register": InternalDocType.RISK_REGISTER,
    "risk": InternalDocType.RISK_REGISTER,
    "financial-review": InternalDocType.FINANCIAL_REVIEW,
    "financial_review": InternalDocType.FINANCIAL_REVIEW,
    "competitor-analysis": InternalDocType.COMPETITOR_ANALYSIS,
    "competitor_analysis": InternalDocType.COMPETITOR_ANALYSIS,
    "policy": InternalDocType.POLICY,
    "policies": InternalDocType.POLICY,
    "earnings-prep": InternalDocType.EARNINGS_PREP,
    "earnings_prep": InternalDocType.EARNINGS_PREP,
    "supply-chain": InternalDocType.SUPPLY_CHAIN,
    "supply_chain": InternalDocType.SUPPLY_CHAIN,
}


def _normalize_doc_type(doc_type: str) -> InternalDocType:
    """Normalize document type string to enum."""
    normalized = doc_type.lower().replace(" ", "-")
    return DOC_TYPE_MAPPING.get(normalized, InternalDocType.ANNUAL_REVIEW)


def _normalize_classification(classification: str) -> AccessLevel:
    """Map classification string to AccessLevel enum."""
    class_upper = classification.upper()
    
    if "STRICTLY CONFIDENTIAL" in class_upper or "RESTRICTED" in class_upper:
        return AccessLevel.STRICTLY_CONFIDENTIAL
    if "CONFIDENTIAL" in class_upper:
        return AccessLevel.CONFIDENTIAL
    if "INTERNAL" in class_upper or "NEXLIFY" in class_upper:
        return AccessLevel.INTERNAL
    
    return AccessLevel.INTERNAL  # Default


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    # First replace hyphens with underscores
    text = text.replace('-', '_')
    # Remove remaining special chars
    text = re.sub(r'[^\w\s]', '', text)
    # Replace spaces with underscores
    text = text.replace(' ', '_')
    # Collapse multiple underscores
    text = re.sub(r'_+', '_', text)
    # Remove trailing underscores
    text = text.strip('_')
    # Limit length
    return text[:50]


class InternalChunker:
    """Chunks internal documents by H3 headers."""

    def __init__(
        self,
        doc_id: str,
        doc_type: str,
        classification: str = "CONFIDENTIAL",
    ):
        """
        Initialize Internal chunker.

        Args:
            doc_id: Document ID (e.g., "NBPQ4-2025-001")
            doc_type: Document type (e.g., "Board Memo", "Product Roadmap")
            classification: Document classification level
        """
        self.doc_id = doc_id
        self.doc_type = _normalize_doc_type(doc_type)
        self.classification = classification
        self.access_level = _normalize_classification(classification)

    def _find_parent_h2(
        self, 
        sections: list[InternalSection], 
        h3_index: int
    ) -> InternalSection | None:
        """Find the parent H2 for an H3 section."""
        h3_level = sections[h3_index].level
        
        # Look backwards for nearest H2
        for i in range(h3_index - 1, -1, -1):
            if sections[i].level == 2:  # H2
                return sections[i]
        
        return None

    def _build_section_path(self, h2: InternalSection, h3: InternalSection) -> str:
        """Build section path: 'H2 Title / H3 Title' (use original titles)."""
        # Use original titles without number prefixes (they already have numbers)
        return f"{h2.title} / {h3.title}"

    def _build_content(self, h2: InternalSection, h3: InternalSection) -> str:
        """Build chunk content with header context."""
        # Format: "Parent H2 / H3: content"
        h3_num_match = re.match(r'^(\d+(?:\.\d+)?)\.?\s*(.*)', h3.title)
        if h3_num_match:
            h3_num = h3_num_match.group(1)
            h3_rest = h3_num_match.group(2)
            header = f"{h2.title} / {h3_num} {h3_rest}"
        else:
            header = f"{h2.title} / {h3.title}"
        
        content = h3.content.strip()
        if content:
            return f"{header}: {content}"
        return header

    def _detect_content_type(self, content: str, doc_type: InternalDocType) -> ContentType:
        """Detect content type from text and document type."""
        content_lower = content.lower()
        
        # Check document type first
        if doc_type == InternalDocType.RISK_REGISTER:
            return ContentType.RISK_FACTORS
        if doc_type == InternalDocType.PRODUCT_ROADMAP:
            return ContentType.PRODUCT_ROADMAP
        if doc_type == InternalDocType.COMPETITOR_ANALYSIS:
            return ContentType.COMPETITIVE_ANALYSIS
        if doc_type == InternalDocType.FINANCIAL_REVIEW:
            return ContentType.FINANCIAL_STATEMENTS
        if doc_type == InternalDocType.POLICY:
            return ContentType.POLICY

        # Check content patterns
        if any(k in content_lower for k in ["$", "revenue", "income", "%", "margin", "assets", "billion", "million"]):
            return ContentType.FINANCIAL_STATEMENTS
        if any(k in content_lower for k in ["expect", "forecast", "target", "outlook", "plan", "roadmap"]):
            return ContentType.PROJECTION
        if any(k in content_lower for k in ["risk", "challenge", "threat", "concern"]):
            return ContentType.RISK_FACTORS
        if any(k in content_lower for k in ["competitor", "nvidia", "amd", "intel", "market share"]):
            return ContentType.COMPETITIVE_ANALYSIS
        if any(k in content_lower for k in ["strategy", "strategic", "vision", "goal"]):
            return ContentType.STRATEGY
        if any(k in content_lower for k in ["governance", "board", "director", "committee"]):
            return ContentType.GOVERNANCE

        return ContentType.GENERAL

    def _create_chunk(
        self,
        h2: InternalSection,
        h3: InternalSection,
        h2_index: int,
        h3_index: int,
    ) -> Chunk:
        """Create a Chunk from H2 + H3 sections."""
        content = self._build_content(h2, h3)
        section_path = self._build_section_path(h2, h3)
        content_type = self._detect_content_type(h3.content, self.doc_type)

        # Build chunk ID
        h2_slug = _slugify(h2.title)[:20]
        h3_slug = _slugify(h3.title)[:20]
        chunk_id = f"{self.doc_type.value}_{self.doc_id}_{h2_index:02d}_{h3_index:02d}"

        # Build metadata
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            document_id=self.doc_id,
            source_category=DataSourceCategory.INTERNAL_NEXLIFY,
            source_detail=f"nexlify_{self.doc_type.value}",
            access_level=self.access_level,
            is_public=False,
            content_type=content_type,
            internal_doc_type=self.doc_type,
            internal_section_path=section_path,
            document_date=h3.date or h2.date,
            # Indicators from H3 section
            contains_financials=h3.contains_financials,
            contains_projections=h3.contains_projections,
            topics=h3.topics,
        )

        return Chunk(content=content, metadata=metadata)

    def chunk_document(self, document: InternalDocument) -> list[Chunk]:
        """
        Chunk an internal document by H3 sections.

        Args:
            document: InternalDocument with sections

        Returns:
            List of Chunk objects (one per H3 with content)
        """
        chunks = []
        sections = document.sections

        # Track H2 indices for numbering
        h2_counter = 0
        h3_counter = 0
        current_h2_index = 0

        for i, section in enumerate(sections):
            # Skip H1 (document title)
            if section.level == 1:
                continue

            # Track H2
            if section.level == 2:
                h2_counter += 1
                current_h2_index = h2_counter
                h3_counter = 0

            # Process H3 sections
            if section.level == 3:
                # Skip empty sections
                if not section.content or len(section.content.strip()) < 10:
                    continue

                h3_counter += 1

                # Find parent H2
                parent_h2 = self._find_parent_h2(sections, i)

                if parent_h2:
                    chunk = self._create_chunk(
                        h2=parent_h2,
                        h3=section,
                        h2_index=current_h2_index,
                        h3_index=h3_counter,
                    )
                    chunks.append(chunk)
                else:
                    # H3 without parent H2 - use as own chunk
                    # This shouldn't happen normally but handle gracefully
                    chunk = self._create_chunk(
                        h2=section,  # Use self as parent
                        h3=section,
                        h2_index=current_h2_index,
                        h3_index=h3_counter,
                    )
                    chunks.append(chunk)

        return chunks


def chunk_internal_document(
    doc_id: str,
    doc_type: str,
    classification: str,
    sections: list[InternalSection],
) -> list[Chunk]:
    """
    Chunk an internal document.

    Args:
        doc_id: Document ID (fallback if sections don't have one)
        doc_type: Document type string
        classification: Classification level (fallback)
        sections: List of InternalSection objects

    Returns:
        List of Chunk objects
    """
    # Create document wrapper
    document = InternalDocument(sections=sections)
    
    # Find document_id and classification from sections (prefer non-H1 sections)
    effective_doc_id = doc_id
    effective_classification = classification
    
    for section in sections:
        if section.level != 1:  # Skip H1 title
            if section.document_id:
                effective_doc_id = section.document_id
            if section.classification:
                effective_classification = section.classification
            break  # Found our reference section

    chunker = InternalChunker(
        doc_id=effective_doc_id,
        doc_type=doc_type,
        classification=effective_classification,
    )

    return chunker.chunk_document(document)
