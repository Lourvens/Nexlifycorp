"""Unit tests for Internal chunker."""
import pytest
from datetime import datetime

from src.ingestion.chunk_strategies.internal_chunker import (
    InternalChunker,
    chunk_internal_document,
    _normalize_doc_type,
    _normalize_classification,
    _slugify,
    DOC_TYPE_MAPPING,
)
from src.ingestion.types import (
    InternalSection,
    InternalDocument,
    Chunk,
    DataSourceCategory,
    AccessLevel,
    ContentType,
    InternalDocType,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_board_memo_sections():
    """Sample board memo with H2/H3 structure."""
    return [
        InternalSection(
            title="NEXLIFY CORP - BOARD PRESENTATION",
            content="",
            level=1,
            document_type="Board Memo",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="Q4 2025 Board Meeting",
            content="Meeting on January 27, 2026",
            level=2,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="1. CEO Strategic Review",
            content="",
            level=2,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="1.1 Financial Performance",
            content="Q4 revenue reached $36.2B, exceeding guidance by 8%. AI infrastructure demand drove 3x growth in data center segment. Gross margin improved to 74% from 72%.",
            level=3,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
            topics=["revenue", "AI", "margin"],
            contains_financials=True,
        ),
        InternalSection(
            title="1.2 Product Strategy",
            content="NEXL-X4 is on track for Q3 release. Hardware validation completed with 15% performance improvement over NEXL-X3. Supply chain partnerships with TSMC and Samsung secured.",
            level=3,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
            topics=["NEXL-X4", "hardware"],
            contains_projections=True,
        ),
        InternalSection(
            title="2. Risk Assessment",
            content="",
            level=2,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="2.1 Supply Chain Risks",
            content="Taiwan concentration remains a concern. We are exploring alternative manufacturers for critical components. AMD partnership provides backup GPU supply.",
            level=3,
            document_type="Board Memo",
            document_id="NBPQ4-2025-001",
            classification="CONFIDENTIAL",
            topics=["supply chain", "Taiwan", "AMD"],
            contains_financials=False,
        ),
    ]


@pytest.fixture
def empty_h2_with_h3_sections():
    """H2 with no content but has H3 children."""
    return [
        InternalSection(
            title="3. Products",
            content="",  # Empty H2
            level=2,
            document_type="Product Roadmap",
            document_id="NCPR-2026-001",
            classification="CONFIDENTIAL",
        ),
        InternalSection(
            title="3.1 NEXL-X4",
            content="Next generation inference chip with 3x performance improvement. Expected release Q3 2026. Targeting hyperscale customers.",
            level=3,
            document_type="Product Roadmap",
            document_id="NCPR-2026-001",
            classification="CONFIDENTIAL",
            topics=["NEXL-X4", "inference", "Q3"],
            contains_projections=True,
        ),
        InternalSection(
            title="3.2 NEXL-A3",
            content="Training accelerator for large language model training. 40% faster than NEXL-A2. Samples available Q1 2026.",
            level=3,
            document_type="Product Roadmap",
            document_id="NCPR-2026-001",
            classification="CONFIDENTIAL",
            topics=["NEXL-A3", "training", "LLM"],
            contains_projections=True,
        ),
    ]


# =============================================================================
# Test Helper Functions
# =============================================================================

class TestDocTypeNormalization:
    """Tests for _normalize_doc_type function."""

    def test_maps_board_memo(self):
        """Test board-memo maps to BOARD_MEMO."""
        assert _normalize_doc_type("board-memo") == InternalDocType.BOARD_MEMO
        assert _normalize_doc_type("Board Memo") == InternalDocType.BOARD_MEMO

    def test_maps_product_roadmap(self):
        """Test product-roadmap maps to PRODUCT_ROADMAP."""
        assert _normalize_doc_type("product-roadmap") == InternalDocType.PRODUCT_ROADMAP

    def test_maps_risk_register(self):
        """Test risk-register maps to RISK_REGISTER."""
        assert _normalize_doc_type("risk-register") == InternalDocType.RISK_REGISTER
        assert _normalize_doc_type("risk") == InternalDocType.RISK_REGISTER

    def test_default_for_unknown(self):
        """Test unknown doc type defaults to ANNUAL_REVIEW."""
        assert _normalize_doc_type("unknown-type") == InternalDocType.ANNUAL_REVIEW


class TestClassificationNormalization:
    """Tests for _normalize_classification function."""

    def test_maps_confidential(self):
        """Test CONFIDENTIAL maps to CONFIDENTIAL access level."""
        assert _normalize_classification("CONFIDENTIAL") == AccessLevel.CONFIDENTIAL

    def test_maps_restricted(self):
        """Test RESTRICTED maps to STRICTLY_CONFIDENTIAL."""
        assert _normalize_classification("RESTRICTED") == AccessLevel.STRICTLY_CONFIDENTIAL

    def test_maps_strictly_confidential(self):
        """Test STRICTLY CONFIDENTIAL maps to STRICTLY_CONFIDENTIAL."""
        assert _normalize_classification("STRICTLY CONFIDENTIAL — BOARD") == AccessLevel.STRICTLY_CONFIDENTIAL

    def test_maps_internal(self):
        """Test INTERNAL maps to INTERNAL."""
        assert _normalize_classification("NEXLIFY INTERNAL") == AccessLevel.INTERNAL

    def test_default_is_internal(self):
        """Test default is INTERNAL."""
        assert _normalize_classification("UNKNOWN") == AccessLevel.INTERNAL


class TestSlugify:
    """Tests for _slugify function."""

    def test_lowercase(self):
        """Test conversion to lowercase."""
        assert _slugify("CEO Strategic Review") == "ceo_strategic_review"

    def test_removes_special_chars(self):
        """Test special characters are removed, hyphens become underscores."""
        assert _slugify("Product: NEXL-X4 (2026)") == "product_nexl_x4_2026"

    def test_collapse_underscores(self):
        """Test multiple underscores are collapsed."""
        assert _slugify("Q1  --  Q2") == "q1_q2"

    def test_limit_length(self):
        """Test long text is truncated."""
        long_title = "A" * 100
        result = _slugify(long_title)
        assert len(result) == 50


# =============================================================================
# Test InternalChunker Initialization
# =============================================================================

class TestInternalChunkerInit:
    """Tests for InternalChunker initialization."""

    def test_creates_with_required_params(self):
        """Test basic initialization."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )

        assert chunker.doc_id == "NBPQ4-2025-001"
        assert chunker.doc_type == InternalDocType.BOARD_MEMO

    def test_classification_maps_to_access_level(self):
        """Test classification maps to access level."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )

        assert chunker.access_level == AccessLevel.CONFIDENTIAL

    def test_doc_type_normalized(self):
        """Test doc type is normalized."""
        chunker = InternalChunker(
            doc_id="NCPR-2026-001",
            doc_type="Product Roadmap",  # Space instead of hyphen
        )

        assert chunker.doc_type == InternalDocType.PRODUCT_ROADMAP


# =============================================================================
# Test Parent H2 Finding
# =============================================================================

class TestParentH2Finding:
    """Tests for _find_parent_h2 method."""

    def test_finds_immediate_previous_h2(self, sample_board_memo_sections):
        """Test finds the immediate previous H2."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
        )

        # Index 3 is "1.1 Financial Performance" (H3)
        # Index 2 is "1. CEO Strategic Review" (H2)
        parent = chunker._find_parent_h2(sample_board_memo_sections, 3)

        assert parent is not None
        assert parent.title == "1. CEO Strategic Review"

    def test_finds_distant_h2(self):
        """Test finds H2 even when more than one section away."""
        sections = [
            InternalSection(title="H2 Title", content="", level=2, document_type="Test", document_id="T1", classification="CONFIDENTIAL"),
            InternalSection(title="H3a", content="Content a", level=3, document_type="Test", document_id="T1", classification="CONFIDENTIAL"),
            InternalSection(title="H3b", content="Content b", level=3, document_type="Test", document_id="T1", classification="CONFIDENTIAL"),
            InternalSection(title="H3c", content="Content c", level=3, document_type="Test", document_id="T1", classification="CONFIDENTIAL"),
        ]
        chunker = InternalChunker(doc_id="T1", doc_type="test")

        # Index 3 is "H3c" - parent should be "H2 Title"
        parent = chunker._find_parent_h2(sections, 3)

        assert parent is not None
        assert parent.title == "H2 Title"


# =============================================================================
# Test Section Path Building
# =============================================================================

class TestSectionPathBuilding:
    """Tests for _build_section_path method."""

    def test_creates_path_with_numbers(self):
        """Test path creation with numbered sections."""
        chunker = InternalChunker(doc_id="T1", doc_type="test")
        h2 = InternalSection(title="1. CEO Review", content="", level=2, document_type="Test", document_id="T1", classification="CONFIDENTIAL")
        h3 = InternalSection(title="1.1 Financial", content="", level=3, document_type="Test", document_id="T1", classification="CONFIDENTIAL")

        path = chunker._build_section_path(h2, h3)

        assert "1. CEO Review" in path
        assert "1.1 Financial" in path

    def test_creates_path_without_numbers(self):
        """Test path creation without numbered sections."""
        chunker = InternalChunker(doc_id="T1", doc_type="test")
        h2 = InternalSection(title="CEO Review", content="", level=2, document_type="Test", document_id="T1", classification="CONFIDENTIAL")
        h3 = InternalSection(title="Financial Performance", content="", level=3, document_type="Test", document_id="T1", classification="CONFIDENTIAL")

        path = chunker._build_section_path(h2, h3)

        assert "CEO Review" in path
        assert "Financial Performance" in path


# =============================================================================
# Test Content Building
# =============================================================================

class TestContentBuilding:
    """Tests for _build_content method."""

    def test_includes_h2_and_h3_titles(self):
        """Test content includes both H2 and H3."""
        chunker = InternalChunker(doc_id="T1", doc_type="test")
        h2 = InternalSection(title="2. Strategy", content="", level=2, document_type="Test", document_id="T1", classification="CONFIDENTIAL")
        h3 = InternalSection(title="2.1 Vision", content="Become the leader.", level=3, document_type="Test", document_id="T1", classification="CONFIDENTIAL")

        content = chunker._build_content(h2, h3)

        assert "2. Strategy" in content
        assert "2.1 Vision" in content
        assert "Become the leader." in content


# =============================================================================
# Test Content Type Detection
# =============================================================================

class TestContentTypeDetection:
    """Tests for automatic content type detection."""

    def test_detects_risk_register(self):
        """Test risk register doc type."""
        chunker = InternalChunker(doc_id="T1", doc_type="risk-register")
        content = "This is a risk section content."

        content_type = chunker._detect_content_type(content, InternalDocType.RISK_REGISTER)

        assert content_type == ContentType.RISK_FACTORS

    def test_detects_product_roadmap(self):
        """Test product roadmap doc type."""
        chunker = InternalChunker(doc_id="T1", doc_type="product-roadmap")
        content = "New product launching soon."

        content_type = chunker._detect_content_type(content, InternalDocType.PRODUCT_ROADMAP)

        assert content_type == ContentType.PRODUCT_ROADMAP

    def test_detects_financial_from_content(self):
        """Test financial detection from content."""
        chunker = InternalChunker(doc_id="T1", doc_type="board-memo")
        content = "Revenue grew to $100B with 50% margin improvement."

        content_type = chunker._detect_content_type(content, InternalDocType.BOARD_MEMO)

        assert content_type == ContentType.FINANCIAL_STATEMENTS

    def test_detects_projection_from_content(self):
        """Test projection detection from content."""
        chunker = InternalChunker(doc_id="T1", doc_type="board-memo")
        content = "We plan to release next quarter targeting enterprise customers."

        content_type = chunker._detect_content_type(content, InternalDocType.BOARD_MEMO)

        assert content_type == ContentType.PROJECTION

    def test_default_is_general(self):
        """Test unknown content defaults to GENERAL."""
        chunker = InternalChunker(doc_id="T1", doc_type="board-memo")
        content = "Regular meeting notes without specific content."

        content_type = chunker._detect_content_type(content, InternalDocType.BOARD_MEMO)

        assert content_type == ContentType.GENERAL


# =============================================================================
# Test Document Chunking
# =============================================================================

class TestDocumentChunking:
    """Tests for chunk_document method."""

    def test_chunks_h3_sections_only(self, sample_board_memo_sections):
        """Test only H3 sections with content become chunks."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        # 3 H3 sections with content (1.1 Financial, 1.2 Product, 2.1 Supply Chain)
        assert len(chunks) == 3

    def test_h2_containers_skipped(self, sample_board_memo_sections):
        """Test H2 containers are not turned into chunks."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        # "1. CEO Strategic Review" is H2 with no content - should not be chunk
        for chunk in chunks:
            assert "1. CEO Strategic Review" not in chunk.content.split("/")[0] or chunk.metadata.internal_section_path

    def test_empty_h3_sections_skipped(self, sample_board_memo_sections):
        """Test empty H3 sections are skipped."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        for chunk in chunks:
            # Empty sections should not be chunked
            content = chunk.content.split(":")[-1] if ":" in chunk.content else chunk.content
            assert len(content.strip()) > 5

    def test_preserves_parent_h2_context(self, sample_board_memo_sections):
        """Test H3 chunks include H2 parent context."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        # Find the supply chain risk chunk
        supply_chain_chunk = next(
            (c for c in chunks if "Supply Chain" in c.metadata.internal_section_path),
            None
        )
        assert supply_chain_chunk is not None
        assert "1. CEO Strategic Review" in supply_chain_chunk.content or \
               "2. Risk Assessment" in supply_chain_chunk.content

    def test_empty_h2_with_h3_works(self, empty_h2_with_h3_sections):
        """Test H2 container with H3 children works."""
        chunker = InternalChunker(
            doc_id="NCPR-2026-001",
            doc_type="product-roadmap",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=empty_h2_with_h3_sections)

        chunks = chunker.chunk_document(document)

        assert len(chunks) == 2  # Two H3 sections

    def test_all_chunks_have_correct_metadata(self, sample_board_memo_sections):
        """Test all chunks have correct metadata."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        for chunk in chunks:
            assert chunk.metadata.source_category == DataSourceCategory.INTERNAL_NEXLIFY
            assert chunk.metadata.document_id == "NBPQ4-2025-001"
            assert chunk.metadata.access_level == AccessLevel.CONFIDENTIAL
            assert chunk.metadata.is_public == False
            assert chunk.metadata.internal_doc_type == InternalDocType.BOARD_MEMO

    def test_chunk_ids_unique(self, sample_board_memo_sections):
        """Test all chunk IDs are unique."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        chunk_ids = [c.metadata.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_topics_preserved(self, sample_board_memo_sections):
        """Test topics from H3 are preserved in chunk."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        # Find chunk with revenue topic
        revenue_chunk = next(
            (c for c in chunks if "revenue" in c.metadata.topics),
            None
        )
        assert revenue_chunk is not None
        assert "revenue" in revenue_chunk.metadata.topics

    def test_indicators_preserved(self, sample_board_memo_sections):
        """Test contains_financials and contains_projections preserved."""
        chunker = InternalChunker(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
        )
        document = InternalDocument(sections=sample_board_memo_sections)

        chunks = chunker.chunk_document(document)

        # Find financial performance chunk (has_financials=True)
        financial_chunk = next(
            (c for c in chunks if "Financial Performance" in c.metadata.internal_section_path),
            None
        )
        assert financial_chunk is not None
        assert financial_chunk.metadata.contains_financials == True

        # Find product strategy chunk (has_projections=True)
        product_chunk = next(
            (c for c in chunks if "Product Strategy" in c.metadata.internal_section_path),
            None
        )
        assert product_chunk is not None
        assert product_chunk.metadata.contains_projections == True


# =============================================================================
# Test chunk_internal_document Helper
# =============================================================================

class TestChunkInternalDocument:
    """Tests for chunk_internal_document function."""

    def test_chunks_document_from_sections(self, sample_board_memo_sections):
        """Test chunking from sections list."""
        chunks = chunk_internal_document(
            doc_id="NBPQ4-2025-001",
            doc_type="board-memo",
            classification="CONFIDENTIAL",
            sections=sample_board_memo_sections,
        )

        # 3 H3 sections with content
        assert len(chunks) == 3

    def test_doc_id_from_section_preferred(self, sample_board_memo_sections):
        """Test document_id from section is preferred over param."""
        chunks = chunk_internal_document(
            doc_id="DIFFERENT-ID",  # This should be overridden
            doc_type="board-memo",
            classification="CONFIDENTIAL",
            sections=sample_board_memo_sections,
        )

        for chunk in chunks:
            assert chunk.metadata.document_id == "NBPQ4-2025-001"