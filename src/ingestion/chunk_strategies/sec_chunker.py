"""SEC Filing Chunker - Paragraph + Sentence splitting.

Splits SEC sections into ~1000 char chunks with 200 char overlap.

Algorithm:
    1. Split by \n\n (natural paragraphs)
    2. For each paragraph > 1200 chars, split by sentence (~150 chars)
    3. If still > 1200 chars, split by 500 char blocks
"""
import re
from typing import Generator

from src.ingestion.types import (
    SECSection,
    Chunk,
    ChunkMetadata,
    DataSourceCategory,
    AccessLevel,
    ContentType,
    SECFormType,
)


# SEC section name to Item number mapping
SEC_SECTION_MAPPING = {
    "Business Description": "Item 1",
    "Risk Factors": "Item 1A",
    "Management's Discussion and Analysis": "Item 7",
    "Notes to Financial Statements": "Item 8",
}

# Target chunk size and overlap
TARGET_CHUNK_SIZE = 1000
OVERLAP_SIZE = 200
MAX_PARAGRAPH_SIZE = 1200
SENTENCE_SIZE = 150
MAX_DEPTH = 5


class SECChunker:
    """Chunks SEC filings into semantic units."""

    def __init__(
        self,
        ticker: str,
        form: str,
        fiscal_year: int,
        cik: str | None = None,
        content_type: ContentType | None = None,
    ):
        """
        Initialize SEC chunker.

        Args:
            ticker: Stock ticker (e.g., "NVDA")
            form: Form type (e.g., "10-K", "10-Q")
            fiscal_year: Fiscal year (e.g., 2024)
            cik: SEC CIK number
            content_type: Override content type detection
        """
        self.ticker = ticker
        self.form = form
        self.fiscal_year = fiscal_year
        self.cik = cik
        self.content_type = content_type

        # Map form to SECFormType enum
        self.sec_form_type = SECFormType.FORM_10K if "10-K" in form else SECFormType.FORM_10Q

    def _split_into_paragraphs(self, text: str) -> list[str]:
        """Split text by double newlines (natural paragraphs)."""
        paragraphs = text.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_by_sentence(self, text: str) -> list[str]:
        """
        Split text by sentence boundaries and group into ~150 char chunks.
        
        Looks for sentence-ending punctuation followed by space and capital letter.
        Long sentences are split into fixed-size blocks.
        """
        # Pattern: period/exclamation/question + space + capital letter
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Combine sentences into ~150 char chunks
        result = []
        current = ""
        for sentence in sentences:
            # Handle very long sentences by splitting them
            if len(sentence) > MAX_PARAGRAPH_SIZE:
                # First yield current chunk if not empty
                if current:
                    result.append(current)
                    current = ""
                # Split long sentence into fixed-size blocks
                for i in range(0, len(sentence), MAX_PARAGRAPH_SIZE):
                    block = sentence[i:i + MAX_PARAGRAPH_SIZE]
                    if block:
                        result.append(block)
                continue
            
            if len(current) + len(sentence) <= SENTENCE_SIZE:
                current = (current + " " + sentence).strip() if current else sentence
            else:
                if current:
                    result.append(current)
                current = sentence
        
        if current:
            result.append(current)
        
        return result

    def _split_into_chunks(self, text: str, depth: int = 0) -> Generator[str, None, None]:
        """
        Iteratively split text into chunks of target size.
        
        Strategy:
        1. Try paragraph splitting (\n\n)
        2. Try sentence splitting (~150 chars)
        3. Fall back to fixed-size blocks (500 chars)
        
        Args:
            text: Text to split
            depth: Current recursion depth (prevents infinite loops)
        """
        text = text.strip()
        if not text or depth > MAX_DEPTH:
            return

        # If text is small enough, yield as single chunk
        if len(text) <= TARGET_CHUNK_SIZE:
            yield text
            return

        # Try paragraph splitting first
        paragraphs = self._split_into_paragraphs(text)
        
        # If no meaningful paragraph splits, try sentence splitting
        if len(paragraphs) <= 1 or (len(paragraphs) == 1 and len(paragraphs[0]) > MAX_PARAGRAPH_SIZE):
            sentences = self._split_by_sentence(text)
            if len(sentences) > 1:
                # Combine sentences into chunks
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 2 <= TARGET_CHUNK_SIZE:
                        current_chunk = (current_chunk + "\n\n" + sentence).strip() if current_chunk else sentence
                    else:
                        if current_chunk:
                            yield current_chunk
                        current_chunk = sentence
                if current_chunk:
                    yield current_chunk
                return
            else:
                # Final fallback: fixed-size character chunks
                for i in range(0, len(text), 500):
                    chunk = text[i:i + 500].strip()
                    if chunk:
                        yield chunk
                return
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If single paragraph is too big, recurse with depth limit
            if len(para) > MAX_PARAGRAPH_SIZE:
                if current_chunk:
                    yield current_chunk
                    current_chunk = ""
                # Use iterative approach for large paragraphs
                yield from self._split_large_text(para, depth)
            else:
                # Check if adding this paragraph exceeds target
                if len(current_chunk) + len(para) + 2 <= TARGET_CHUNK_SIZE:
                    if current_chunk:
                        current_chunk += "\n\n"
                    current_chunk += para
                else:
                    if current_chunk:
                        yield current_chunk
                    current_chunk = para

        if current_chunk:
            yield current_chunk

    def _split_large_text(self, text: str, depth: int = 0) -> Generator[str, None, None]:
        """
        Split large text using iterative approach (no recursion).
        
        Tries: sentence splitting -> fixed-size blocks
        """
        text = text.strip()
        if not text:
            return
        
        # Try sentence splitting first
        sentences = self._split_by_sentence(text)
        if len(sentences) > 1:
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 2 <= TARGET_CHUNK_SIZE:
                    current_chunk = (current_chunk + "\n\n" + sentence).strip() if current_chunk else sentence
                else:
                    if current_chunk:
                        yield current_chunk
                    current_chunk = sentence
            if current_chunk:
                yield current_chunk
            return
        
        # Fallback: fixed-size blocks of 500 chars
        for i in range(0, len(text), 500):
            chunk = text[i:i + 500].strip()
            if chunk:
                yield chunk

    def _get_section_item(self, section_name: str) -> str:
        """Map section name to SEC Item number."""
        return SEC_SECTION_MAPPING.get(section_name, section_name)

    def _detect_content_type(self, content: str, section_name: str) -> ContentType:
        """Detect content type from text and section name."""
        # Check section name first
        section_lower = section_name.lower()
        
        if "risk" in section_lower:
            return ContentType.RISK_FACTORS
        if "management" in section_lower or "discussion" in section_lower:
            return ContentType.MANAGEMENT_DISCUSSION
        if "financial" in section_lower:
            return ContentType.FINANCIAL_STATEMENTS
        if "business" in section_lower:
            return ContentType.BUSINESS_DESCRIPTION

        # Check content patterns (only if section name doesn't match)
        content_lower = content.lower()
        
        if any(k in content_lower for k in ["$", "revenue", "income", "%", "margin", "assets"]):
            return ContentType.FINANCIAL_STATEMENTS
        if any(k in content_lower for k in ["expect", "forecast", "target", "outlook", "project"]):
            return ContentType.MANAGEMENT_DISCUSSION
        if any(k in content_lower for k in ["risk", "challenge", "uncertainty"]):
            return ContentType.RISK_FACTORS

        return ContentType.GENERAL

    def _create_chunk(
        self,
        content: str,
        section_name: str,
        index: int,
        document_id: str,
    ) -> Chunk:
        """Create a Chunk from content."""
        # Detect or use provided content type
        if self.content_type:
            content_type = self.content_type
        else:
            content_type = self._detect_content_type(content, section_name)

        # Add section prefix for context
        section_item = self._get_section_item(section_name)
        prefixed_content = f"[{section_item}] {content}"

        # Generate chunk ID
        section_slug = section_name.lower().replace(" ", "_").replace("'", "")
        chunk_id = f"{self.ticker.lower()}_{self.form.lower().replace('-', '')}_{self.fiscal_year}_{section_slug}_{index:04d}"

        # Build metadata
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            document_id=document_id,
            source_category=DataSourceCategory.PUBLIC_SEC,
            source_detail=f"{self.ticker.lower()}_{self.form.lower().replace('-', '')}_{self.fiscal_year}",
            access_level=AccessLevel.PUBLIC,
            is_public=True,
            content_type=content_type,
            ticker=self.ticker,
            sec_form=self.sec_form_type,
            sec_section=section_item,
            fiscal_year=self.fiscal_year,
            cik=self.cik,
        )

        return Chunk(content=prefixed_content, metadata=metadata)

    def chunk_section(self, section: SECSection) -> list[Chunk]:
        """
        Chunk a single SEC section into multiple Chunks.

        Args:
            section: SECSection with name, content, word_count

        Returns:
            List of Chunk objects
        """
        chunks = []
        document_id = f"{self.ticker}_{self.form}_{self.fiscal_year}"

        # Split content into chunks
        text_chunks = list(self._split_into_chunks(section.content))

        for i, text in enumerate(text_chunks):
            chunk = self._create_chunk(
                content=text,
                section_name=section.name,
                index=i + 1,
                document_id=document_id,
            )
            chunks.append(chunk)

        return chunks


def chunk_sec_document(
    ticker: str,
    form: str,
    fiscal_year: int,
    sections: list[SECSection],
    cik: str | None = None,
) -> list[Chunk]:
    """
    Chunk an entire SEC document (all sections).

    Args:
        ticker: Stock ticker
        form: Form type (10-K, 10-Q)
        fiscal_year: Fiscal year
        sections: List of SECSection objects
        cik: SEC CIK number

    Returns:
        List of all Chunks from all sections
    """
    chunker = SECChunker(
        ticker=ticker,
        form=form,
        fiscal_year=fiscal_year,
        cik=cik,
    )

    all_chunks = []
    for section in sections:
        section_chunks = chunker.chunk_section(section)
        all_chunks.extend(section_chunks)

    return all_chunks