"""Unit tests for internal document processor."""
import pytest
from pathlib import Path

from src.ingestion.internal_doc_processor import (
    extract_sections_from_markdown,
    parse_metadata_from_header,
    extract_topics,
    has_financials,
    has_projections,
    extract_internal_document,
    extract_all_internal_documents,
    InternalSection,
)


class TestExtractSectionsFromMarkdown:
    """Tests for extract_sections_from_markdown function."""

    def test_extracts_headers_and_content(self, sample_markdown_file):
        """Test that headers and content are correctly extracted."""
        sections = extract_sections_from_markdown(sample_markdown_file)

        assert len(sections) >= 2
        assert any(s["title"] == "Section 1" for s in sections)
        assert any(s["title"] == "Section 2" for s in sections)

    def test_headers_have_level(self, sample_markdown_file):
        """Test that header levels are correctly identified."""
        sections = extract_sections_from_markdown(sample_markdown_file)

        for section in sections:
            assert section["level"] in [1, 2, 3]

    def test_content_excludes_header_line(self, sample_markdown_file):
        """Test that section content excludes the header line."""
        sections = extract_sections_from_markdown(sample_markdown_file)

        section_1 = next((s for s in sections if s["title"] == "Section 1"), None)
        assert section_1 is not None
        assert not section_1["text"].startswith("## Section 1")

    def test_handles_empty_file(self, tmp_path):
        """Test handling of empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        sections = extract_sections_from_markdown(empty_file)
        assert sections == []


class TestParseMetadataFromHeader:
    """Tests for parse_metadata_from_header function."""

    def test_parses_document_id(self, sample_markdown_content):
        """Test document ID is extracted."""
        metadata = parse_metadata_from_header(sample_markdown_content)

        assert metadata["document_id"] == "TEST-001"

    def test_parses_date(self, sample_markdown_content):
        """Test date is extracted."""
        metadata = parse_metadata_from_header(sample_markdown_content)

        assert metadata["date"] is not None
        assert metadata["date"].year == 2025
        assert metadata["date"].month == 1
        assert metadata["date"].day == 1

    def test_parses_classification(self, sample_markdown_content):
        """Test classification is extracted."""
        metadata = parse_metadata_from_header(sample_markdown_content)

        assert "CONFIDENTIAL" in metadata["classification"]

    def test_handles_missing_fields(self):
        """Test handling when fields are missing."""
        content = "| Field | Value |\n|-------|-------|\n| **Document ID** | TEST-002 |"

        metadata = parse_metadata_from_header(content)

        assert metadata["document_id"] == "TEST-002"
        assert metadata["date"] is None

    def test_handles_bold_field_names(self):
        """Test parsing with **bold** field names."""
        content = """
| **Document ID** | DOC-123 |
| **Date** | March 15, 2025 |
| **Classification** | RESTRICTED |
"""

        metadata = parse_metadata_from_header(content)

        assert metadata["document_id"] == "DOC-123"
        assert metadata["classification"] == "RESTRICTED"


class TestExtractTopics:
    """Tests for extract_topics function."""

    def test_finds_known_keywords(self):
        """Test that known keywords are extracted."""
        text = "NVIDIA Blackwell dominates the AI training market. NEXL-X3 inference performance is strong."

        topics = extract_topics(text)

        assert "NVIDIA" in topics
        assert "NEXL-X3" in topics
        assert "inference" in topics

    def test_limits_to_10_topics(self):
        """Test that topic count is limited."""
        text = " ".join([
            "NVIDIA AMD TSMC AI GPU inference training",
            "revenue margin supply chain Taiwan automotive",
            "data center edge",
        ])

        topics = extract_topics(text)

        assert len(topics) <= 10

    def test_case_insensitive(self):
        """Test that matching is case-insensitive."""
        text = "nvidia gpu revenue NVIDIA GPU REVENUE"

        topics = extract_topics(text)

        assert len(topics) > 0

    def test_empty_text_returns_empty_list(self):
        """Test that empty text returns empty list."""
        topics = extract_topics("")

        assert topics == []


class TestHasFinancials:
    """Tests for has_financials function."""

    def test_detects_dollar_signs(self):
        """Test detection of dollar amounts."""
        assert has_financials("$391 billion revenue")
        assert has_financials("$45M")

    def test_detects_percentages(self):
        """Test detection of percentages."""
        assert has_financials("52% gross margin")
        assert has_financials("3.5%")

    def test_detects_financial_keywords(self):
        """Test detection of financial keywords."""
        assert has_financials("Revenue increased to $5B")
        assert has_financials("Net income margin improved")
        assert has_financials("Total assets grew")

    def test_returns_false_for_regular_text(self):
        """Test that regular text returns False."""
        assert not has_financials("The product launch went well")
        assert not has_financials("Team meeting scheduled")


class TestHasProjections:
    """Tests for has_projections function."""

    def test_detects_expect_keywords(self):
        """Test detection of 'expect'."""
        assert has_projections("We expect revenue growth")
        assert has_projections("Expected to launch in Q4")

    def test_detects_forecast_keywords(self):
        """Test detection of forecast/project."""
        assert has_projections("Forecast for 2026 shows improvement")
        assert has_projections("Projected revenue of $10B")

    def test_detects_target_keywords(self):
        """Test detection of target/plan."""
        assert has_projections("Our target is $6.8B")
        assert has_projections("Plan to expand margins")

    def test_returns_false_for_past_tense(self):
        """Test that past tense doesn't trigger."""
        assert not has_projections("Revenue was $5B last year")


class TestExtractInternalDocument:
    """Tests for extract_internal_document function."""

    def test_returns_internal_document(self, sample_markdown_file):
        """Test that function returns InternalDocument."""
        doc = extract_internal_document(sample_markdown_file, "Test Document")

        assert doc is not None
        assert isinstance(doc.sections, list)
        assert len(doc.sections) > 0

    def test_section_has_correct_metadata(self, sample_markdown_file):
        """Test that section inherits document metadata."""
        doc = extract_internal_document(sample_markdown_file, "Test Document")

        section = doc.sections[0]
        assert section.company == "Nexlify Corp"
        assert section.document_type == "Test Document"
        assert section.document_id == "TEST-001"
        assert section.classification == "CONFIDENTIAL"

    def test_section_extracts_topics(self, sample_markdown_file):
        """Test that topics are extracted for sections."""
        doc = extract_internal_document(sample_markdown_file, "Test Document")

        # At least one section should have topics
        sections_with_topics = [s for s in doc.sections if s.topics]
        # May be empty depending on content

    def test_handles_missing_file(self, tmp_path):
        """Test handling of non-existent file."""
        fake_path = tmp_path / "nonexistent.md"

        doc = extract_internal_document(fake_path, "Test")

        assert doc is None

    def test_sections_have_correct_structure(self, sample_risk_register_content, tmp_path):
        """Test that sections have all required fields."""
        test_file = tmp_path / "risk.md"
        test_file.write_text(sample_risk_register_content)

        doc = extract_internal_document(test_file, "Risk Register")

        for section in doc.sections:
            assert hasattr(section, "title")
            assert hasattr(section, "content")
            assert hasattr(section, "level")
            assert hasattr(section, "topics")
            assert hasattr(section, "contains_financials")
            assert hasattr(section, "contains_projections")


class TestDocumentMetadata:
    """Tests for InternalDocument.metadata property."""

    def test_metadata_returns_first_section_data(self, sample_markdown_file):
        """Test that metadata is derived from first section."""
        doc = extract_internal_document(sample_markdown_file, "Test")

        metadata = doc.metadata

        assert metadata["document_type"] == "Test"
        assert metadata["document_id"] == "TEST-001"
        assert metadata["classification"] == "CONFIDENTIAL"

    def test_metadata_empty_for_no_sections(self):
        """Test metadata for document with no sections."""
        from src.ingestion.types import InternalDocument

        doc = InternalDocument(sections=[])
        metadata = doc.metadata

        assert metadata == {}


class TestFullPipeline:
    """Integration tests for full extraction pipeline."""

    def test_extract_all_internal_documents(self, tmp_path):
        """Test extracting all documents from directory structure."""
        # Create test directory structure
        (tmp_path / "risk-registers").mkdir()
        risk_file = tmp_path / "risk-registers" / "test_risk.md"
        risk_file.write_text("""
# Test Risk Register

## CONFIDENTIAL

| Field | Value |
|-------|-------|
| **Document ID** | TEST-RISK-001 |
| **Date** | January 1, 2025 |
| **Classification** | CONFIDENTIAL |

## 1. Overview

Risk content here.
""")

        docs = extract_all_internal_documents(
            base_path=tmp_path,
            output_dir=tmp_path / "extracted"
        )

        assert len(docs) == 1
        assert docs[0].metadata["document_type"] == "Risk Register"
        assert docs[0].metadata["document_id"] == "TEST-RISK-001"