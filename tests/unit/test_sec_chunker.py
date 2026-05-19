"""Unit tests for SEC chunker."""
import pytest
from datetime import datetime

from src.ingestion.chunk_strategies.sec_chunker import (
    SECChunker,
    chunk_sec_document,
    SEC_SECTION_MAPPING,
    TARGET_CHUNK_SIZE,
)
from src.ingestion.types import (
    SECSection,
    Chunk,
    DataSourceCategory,
    AccessLevel,
    ContentType,
    SECFormType,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_risk_section():
    """Sample risk section with multiple paragraphs."""
    content = """
NVIDIA Corporation faces various risks in its business operations.

Competition in the AI chip market is intense. We compete with AMD, Intel, and custom AI chips from cloud providers. Our Data Center segment faces significant competition from AMD's MI300 series and Intel's Gaudi accelerators.

Our dependence on TSMC for chip manufacturing poses operational risks. Any disruption in TSMC's production could materially impact our ability to meet customer demand. We have limited visibility into TSMC's production capacity allocation.

Regulatory challenges in international markets could affect our operations. Export controls on advanced AI chips to China have materially affected our revenue. Future regulatory changes could further impact our business.

We are subject to risks related to product transitions. Our ability to develop and manufacture next-generation products on schedule affects our competitive position.
"""
    return SECSection(
        name="Risk Factors",
        content=content,
        word_count=150,
    )


@pytest.fixture
def sample_business_section():
    """Sample business section."""
    content = """
Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories. The Company also sells a variety of related software, services, accessories, and third-party digital content.

The Company generates revenue from the sale of hardware products, software, and services. Services include the App Store, Apple Music, iCloud, and Apple TV+.
"""
    return SECSection(
        name="Business Description",
        content=content,
        word_count=80,
    )


@pytest.fixture
def large_paragraph_section():
    """Section with very large paragraph (>1200 chars)."""
    long_text = (
        "Our business depends on global economic conditions and market demand for our products. "
        "We operate in highly competitive markets with rapidly changing technology. "
        "Our results depend on our ability to innovate and compete effectively. "
        "We face significant competition and must manage our inventory and product transitions successfully. "
        "Our reliance on third-party manufacturers for components exposes us to supply chain risks. "
        "Currency fluctuations and geopolitical events can materially affect our financial results. "
        "Changes in consumer preferences and purchasing patterns could negatively impact our revenue. "
        "Our future success depends on our ability to develop new products and services on schedule. "
    ) * 5  # Repeat to make it very long
    return SECSection(name="Risk Factors", content=long_text, word_count=500)


# =============================================================================
# Test SECSectionMapping
# =============================================================================

class TestSectionMapping:
    """Tests for section name to Item mapping."""

    def test_risk_factors_maps_to_item_1a(self):
        """Test Risk Factors → Item 1A."""
        assert SEC_SECTION_MAPPING["Risk Factors"] == "Item 1A"

    def test_business_description_maps_to_item_1(self):
        """Test Business Description → Item 1."""
        assert SEC_SECTION_MAPPING["Business Description"] == "Item 1"

    def test_management_discussion_maps_to_item_7(self):
        """Test MD&A → Item 7."""
        assert SEC_SECTION_MAPPING["Management's Discussion and Analysis"] == "Item 7"

    def test_notes_maps_to_item_8(self):
        """Test Notes → Item 8."""
        assert SEC_SECTION_MAPPING["Notes to Financial Statements"] == "Item 8"


# =============================================================================
# Test SECChunker Initialization
# =============================================================================

class TestSECChunkerInit:
    """Tests for SECChunker initialization."""

    def test_creates_with_required_params(self):
        """Test basic initialization."""
        chunker = SECChunker(
            ticker="NVDA",
            form="10-K",
            fiscal_year=2024,
        )

        assert chunker.ticker == "NVDA"
        assert chunker.form == "10-K"
        assert chunker.fiscal_year == 2024

    def test_maps_10k_form_to_enum(self):
        """Test 10-K maps to FORM_10K."""
        chunker = SECChunker(ticker="AAPL", form="10-K", fiscal_year=2024)
        assert chunker.sec_form_type == SECFormType.FORM_10K

    def test_maps_10q_form_to_enum(self):
        """Test 10-Q maps to FORM_10Q."""
        chunker = SECChunker(ticker="AAPL", form="10-Q", fiscal_year=2024)
        assert chunker.sec_form_type == SECFormType.FORM_10Q

    def test_accepts_optional_cik(self):
        """Test CIK is stored."""
        chunker = SECChunker(
            ticker="NVDA",
            form="10-K",
            fiscal_year=2024,
            cik="1045810",
        )
        assert chunker.cik == "1045810"


# =============================================================================
# Test Paragraph Splitting
# =============================================================================

class TestParagraphSplitting:
    """Tests for _split_into_paragraphs method."""

    def test_splits_by_double_newline(self):
        """Test paragraph splitting by \n\n."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        
        paragraphs = chunker._split_into_paragraphs(text)
        
        assert len(paragraphs) == 3
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."

    def test_strips_empty_paragraphs(self):
        """Test empty paragraphs are filtered."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        text = "First.\n\n\n\nSecond."
        
        paragraphs = chunker._split_into_paragraphs(text)
        
        assert len(paragraphs) == 2
        assert "" not in paragraphs

    def test_strips_whitespace(self):
        """Test whitespace is stripped from paragraphs."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        text = "  First paragraph.  \n\n  Second paragraph.  "
        
        paragraphs = chunker._split_into_paragraphs(text)
        
        assert paragraphs[0] == "First paragraph."
        assert paragraphs[1] == "Second paragraph."


# =============================================================================
# Test Chunk Generation
# =============================================================================

class TestChunkGeneration:
    """Tests for full chunking workflow."""

    def test_chunks_risk_section(self, sample_risk_section):
        """Test chunking a risk section."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(sample_risk_section)

        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_all_chunks_have_correct_metadata(self, sample_risk_section):
        """Test all chunks have correct source metadata."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(sample_risk_section)

        for chunk in chunks:
            assert chunk.metadata.source_category == DataSourceCategory.PUBLIC_SEC
            assert chunk.metadata.ticker == "NVDA"
            assert chunk.metadata.fiscal_year == 2024
            assert chunk.metadata.sec_form == SECFormType.FORM_10K

    def test_chunks_have_prefix(self, sample_risk_section):
        """Test chunk content has section prefix."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(sample_risk_section)

        for chunk in chunks:
            assert chunk.content.startswith("[Item 1A]")

    def test_content_type_detected(self, sample_risk_section):
        """Test content type is detected as risk factors."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(sample_risk_section)

        for chunk in chunks:
            assert chunk.metadata.content_type == ContentType.RISK_FACTORS

    def test_chunk_ids_unique(self, sample_risk_section):
        """Test all chunk IDs are unique."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(sample_risk_section)

        chunk_ids = [c.metadata.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_chunk_ids_follow_format(self, sample_risk_section):
        """Test chunk IDs follow expected format."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(sample_risk_section)

        for chunk in chunks:
            # Format: nvda_10k_2024_risk_factors_XXXX
            assert chunk.metadata.chunk_id.startswith("nvda_10k_2024_risk_factors_")


# =============================================================================
# Test Large Paragraph Handling
# =============================================================================

class TestLargeParagraphHandling:
    """Tests for handling large paragraphs."""

    def test_very_large_paragraph_splits(self, large_paragraph_section):
        """Test that very large paragraphs are split."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(large_paragraph_section)

        # Should have multiple chunks
        assert len(chunks) > 1

    def test_split_chunks_within_size_limit(self, large_paragraph_section):
        """Test that split chunks are within size limits."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        chunks = chunker.chunk_section(large_paragraph_section)

        for chunk in chunks:
            # Prefixed content should be around TARGET_CHUNK_SIZE
            # (prefix adds ~15 chars)
            assert len(chunk.content) <= TARGET_CHUNK_SIZE + 50


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_section_returns_empty(self):
        """Test empty section returns no chunks."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        section = SECSection(name="Risk Factors", content="", word_count=0)
        
        chunks = chunker.chunk_section(section)
        
        assert len(chunks) == 0

    def test_single_short_paragraph(self):
        """Test single short paragraph."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        section = SECSection(name="Risk Factors", content="Short risk.", word_count=2)
        
        chunks = chunker.chunk_section(section)
        
        assert len(chunks) == 1
        assert chunks[0].content == "[Item 1A] Short risk."

    def test_unknown_section_name(self):
        """Test unknown section name is handled."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        section = SECSection(name="Unknown Section", content="Some content here.", word_count=5)
        
        chunks = chunker.chunk_section(section)
        
        # Should use original name as section identifier
        assert len(chunks) > 0
        assert chunks[0].content.startswith("[Unknown Section]")


# =============================================================================
# Test chunk_sec_document Helper
# =============================================================================

class TestChunkSecDocument:
    """Tests for chunk_sec_document function."""

    def test_chunks_multiple_sections(self, sample_risk_section, sample_business_section):
        """Test chunking multiple sections."""
        chunks = chunk_sec_document(
            ticker="NVDA",
            form="10-K",
            fiscal_year=2024,
            sections=[sample_risk_section, sample_business_section],
        )

        assert len(chunks) > 1

    def test_document_id_in_chunks(self, sample_risk_section):
        """Test document_id is set correctly."""
        chunks = chunk_sec_document(
            ticker="NVDA",
            form="10-K",
            fiscal_year=2024,
            sections=[sample_risk_section],
        )

        for chunk in chunks:
            assert chunk.metadata.document_id == "NVDA_10-K_2024"

    def test_cik_passed_to_chunks(self):
        """Test CIK is included in metadata."""
        section = SECSection(name="Risk Factors", content="Risk content.", word_count=3)
        
        chunks = chunk_sec_document(
            ticker="NVDA",
            form="10-K",
            fiscal_year=2024,
            sections=[section],
            cik="1045810",
        )

        for chunk in chunks:
            assert chunk.metadata.cik == "1045810"


# =============================================================================
# Test Content Type Detection
# =============================================================================

class TestContentTypeDetection:
    """Tests for automatic content type detection."""

    def test_risk_section_name_priority(self):
        """Test that section name takes priority over content patterns."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        content = "Revenue increased to $60B, representing 122% growth."
        
        content_type = chunker._detect_content_type(content, "Risk Factors")
        
        # Section name takes priority - still RISK_FACTORS even with financial content
        assert content_type == ContentType.RISK_FACTORS

    def test_business_section_stays_business(self):
        """Test business section stays business description."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        content = "We expect growth in revenue."
        
        content_type = chunker._detect_content_type(content, "Business Description")
        
        assert content_type == ContentType.BUSINESS_DESCRIPTION

    def test_financial_content_detected_for_unknown_section(self):
        """Test financial content is detected when section name is unknown."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        content = "Revenue increased to $60B, representing 122% growth. Net income was $30B."
        
        content_type = chunker._detect_content_type(content, "Other Section")
        
        # Financial keywords detected for unknown section
        assert content_type == ContentType.FINANCIAL_STATEMENTS

    def test_management_discussion_keywords_detected(self):
        """Test management discussion keywords are detected when no financial terms."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        content = "We expect strong growth in the market based on current forecasts for the upcoming quarter."
        
        content_type = chunker._detect_content_type(content, "Other Section")
        
        # "expect" and "forecast" keywords trigger MANAGEMENT_DISCUSSION
        assert content_type == ContentType.MANAGEMENT_DISCUSSION

    def test_default_is_general(self):
        """Test default content type is GENERAL."""
        chunker = SECChunker(ticker="NVDA", form="10-K", fiscal_year=2024)
        content = "General discussion about the business environment."
        
        content_type = chunker._detect_content_type(content, "Unknown Section")
        
        assert content_type == ContentType.GENERAL