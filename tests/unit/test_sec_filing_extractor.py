"""Unit tests for SEC filing extractor."""
import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from src.ingestion.sec_filing_extractor import (
    extract_10k,
    extract_10q,
    _extract_metadata,
    _extract_sections,
    _extract_financials,
    _get_quarter,
    _save_to_disk,
)
from src.ingestion.types import (
    SEC10K,
    SECMetadata,
    SECSection,
    SECFinancials,
    DataSource,
)


# =============================================================================
# Test Helpers
# =============================================================================

def create_mock_filing(
    cik="320193",
    accession="0000320193-24-000123",
    date=None,
    company="Apple Inc.",
):
    """Create a mock filing object."""
    filing = Mock()
    filing.cik = cik
    filing.accession_number = accession
    filing.filing_date = date or datetime(2024, 11, 1)
    filing.company = company
    return filing


def create_mock_tenk_object():
    """Create a mock 10-K object with real string attributes."""
    tenk = Mock()
    # Note: content must be > 100 chars to pass the section extraction threshold
    tenk.company = "Apple Inc."
    tenk.business = (
        "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, "
        "and accessories globally. The Company also sells a variety of related software, services, accessories, "
        "and third-party digital content. Apple's products include the iPhone, Mac, iPad, Apple Watch, and AirPods."
    )
    tenk.risk_factors = (
        "Our business depends on global economic conditions and market demand for our products. "
        "We operate in highly competitive markets with rapidly changing technology. "
        "Our results depend on our ability to innovate and compete effectively. "
        "We face significant competition and must manage our inventory and product transitions successfully."
    )
    tenk.management_discussion = (
        "We expect continued growth in services revenue and market share. "
        "Our services business has become increasingly important to our overall revenue. "
        "We continue to invest heavily in research and development to bring new products to market. "
        "Our strong cash position allows us to return value to shareholders while investing in growth opportunities."
    )
    tenk.notes = (
        "See accompanying notes to consolidated financial statements. "
        "These financial statements have been prepared in accordance with U.S. GAAP. "
        "Significant accounting policies are described in Note 1 to the financial statements. "
        "The Company evaluates subsequent events through the date of filing this report."
    )
    
    auditor = Mock()
    auditor.name = "Ernst & Young LLP"
    tenk.auditor = auditor
    tenk.financials = None
    
    return tenk


def create_mock_financials_object():
    """Create mock financials with test data."""
    # Create income statement DataFrame
    income_data = [
        {"label": "Net sales", "FY2025-09-27": 391035000000.0},
        {"label": "Net income", "FY2025-09-27": 112010000000.0},
        {"label": "Diluted (in dollars per share)", "FY2025-09-27": 7.46},
    ]
    
    income_df = Mock()
    income_df.columns = ["concept", "label", "FY2025-09-27"]
    income_df.iterrows = Mock(return_value=iter(enumerate(income_data)))
    
    income_stmt = Mock()
    income_stmt.to_dataframe = Mock(return_value=income_df)
    
    # Create balance sheet DataFrame
    balance_data = [
        {"label": "Total assets", "2025-09-27": 364980000000.0},
    ]
    
    balance_df = Mock()
    balance_df.columns = ["concept", "label", "2025-09-27"]
    balance_df.iterrows = Mock(return_value=iter(enumerate(balance_data)))
    
    balance_sheet = Mock()
    balance_sheet.to_dataframe = Mock(return_value=balance_df)
    
    # Create financials container
    financials = Mock()
    financials.income_statement = Mock(return_value=income_stmt)
    financials.balance_sheet = Mock(return_value=balance_sheet)
    
    return financials


# =============================================================================
# Tests for _get_quarter
# =============================================================================

class TestGetQuarter:
    """Tests for the quarter extraction helper."""

    @pytest.mark.parametrize("month,expected", [
        (1, 1), (2, 1), (3, 1),
        (4, 2), (5, 2), (6, 2),
        (7, 3), (8, 3), (9, 3),
        (10, 4), (11, 4), (12, 4),
    ])
    def test_returns_correct_quarter(self, month, expected):
        """Test quarter calculation for all months."""
        date = datetime(2024, month, 15)
        assert _get_quarter(date) == expected


# =============================================================================
# Tests for _extract_metadata
# =============================================================================

class TestExtractMetadata:
    """Tests for metadata extraction."""

    def test_extracts_ticker(self):
        """Test that ticker is correctly extracted."""
        filing = create_mock_filing()
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("AAPL", tenk, filing, DataSource.SEC_10K)

        assert metadata.ticker == "AAPL"

    def test_extracts_company_name(self):
        """Test that company name is correctly extracted."""
        filing = create_mock_filing()
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("AAPL", tenk, filing, DataSource.SEC_10K)

        assert metadata.company_name == "Apple Inc."

    def test_extracts_cik(self):
        """Test that CIK is correctly extracted."""
        filing = create_mock_filing(cik="789019")
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("MSFT", tenk, filing, DataSource.SEC_10K)

        assert metadata.cik == "789019"

    def test_extracts_accession_number(self):
        """Test that accession number is correctly extracted."""
        filing = create_mock_filing(accession="0000102909-24-000001")
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("AAPL", tenk, filing, DataSource.SEC_10K)

        assert metadata.accession_number == "0000102909-24-000001"

    def test_extracts_filing_date(self):
        """Test that filing date and fiscal year are correctly extracted."""
        filing = create_mock_filing(date=datetime(2024, 11, 1))
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("AAPL", tenk, filing, DataSource.SEC_10K)

        assert metadata.filing_date == datetime(2024, 11, 1)
        assert metadata.fiscal_year == 2024

    def test_extracts_auditor(self):
        """Test that auditor is correctly extracted."""
        filing = create_mock_filing()
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("AAPL", tenk, filing, DataSource.SEC_10K)

        assert metadata.auditor == "Ernst & Young LLP"

    def test_sets_source_for_10k(self):
        """Test that source is set to SEC_10K."""
        filing = create_mock_filing()
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("AAPL", tenk, filing, DataSource.SEC_10K)

        assert metadata.source == DataSource.SEC_10K
        assert metadata.form == "10-K"

    def test_sets_source_for_10q(self):
        """Test that source is set to SEC_10Q."""
        filing = create_mock_filing()
        tenk = create_mock_tenk_object()

        metadata = _extract_metadata("AAPL", tenk, filing, DataSource.SEC_10Q)

        assert metadata.source == DataSource.SEC_10Q
        assert metadata.form == "10-Q"


# =============================================================================
# Tests for _extract_sections
# =============================================================================

class TestExtractSections:
    """Tests for section extraction."""

    def test_extracts_business_section(self):
        """Test that business section is extracted."""
        tenk = create_mock_tenk_object()

        sections = _extract_sections(tenk)

        business = next((s for s in sections if s.name == "Business Description"), None)
        assert business is not None
        assert "Apple Inc." in business.content

    def test_extracts_risk_factors_section(self):
        """Test that risk factors section is extracted."""
        tenk = create_mock_tenk_object()

        sections = _extract_sections(tenk)

        risk = next((s for s in sections if s.name == "Risk Factors"), None)
        assert risk is not None

    def test_extracts_management_discussion_section(self):
        """Test that MD&A section is extracted."""
        tenk = create_mock_tenk_object()

        sections = _extract_sections(tenk)

        md = next((s for s in sections if s.name == "Management's Discussion and Analysis"), None)
        assert md is not None

    def test_sections_have_word_count(self):
        """Test that sections have word count calculated."""
        tenk = create_mock_tenk_object()

        sections = _extract_sections(tenk)

        for section in sections:
            assert section.word_count > 0
            assert isinstance(section.word_count, int)

    def test_section_content_is_string(self):
        """Test that section content is a string."""
        tenk = create_mock_tenk_object()

        sections = _extract_sections(tenk)

        for section in sections:
            assert isinstance(section.content, str)

    def test_skips_missing_sections(self):
        """Test that missing sections are skipped gracefully."""
        tenk = Mock(spec=["company", "auditor"])
        tenk.company = "Test"
        tenk.business = None
        tenk.risk_factors = None
        tenk.management_discussion = None
        tenk.notes = None
        tenk.auditor = Mock()
        tenk.auditor.name = "Test"
        tenk.financials = None

        sections = _extract_sections(tenk)

        assert isinstance(sections, list)


# =============================================================================
# Tests for _extract_financials
# =============================================================================

class TestExtractFinancials:
    """Tests for financial data extraction."""

    def test_returns_none_when_no_financials(self):
        """Test that None is returned when no financials available."""
        tenk = Mock(spec=["financials"])
        tenk.financials = None

        result = _extract_financials(tenk)

        assert result is None

    def test_returns_object_when_financials_exist(self):
        """Test that SECFinancials object is returned when data exists."""
        tenk = create_mock_tenk_object()
        tenk.financials = create_mock_financials_object()

        result = _extract_financials(tenk)

        assert result is not None
        assert isinstance(result, SECFinancials)


# =============================================================================
# Tests for _save_to_disk
# =============================================================================

class TestSaveToDisk:
    """Tests for save to disk functionality."""

    def test_creates_directory(self, tmp_path):
        """Test that output directory is created."""
        output_dir = tmp_path / "sec_output"
        metadata = SECMetadata(
            ticker="AAPL",
            company_name="Apple Inc.",
            form="10-K",
            source=DataSource.SEC_10K,
        )
        sec10k = SEC10K(metadata=metadata, full_text="", sections=[], financials=None)

        filepath = _save_to_disk(sec10k, output_dir)

        assert output_dir.exists()
        assert filepath.exists()

    def test_creates_correct_filename(self, tmp_path):
        """Test that filename is correct."""
        output_dir = tmp_path / "sec_output"
        metadata = SECMetadata(
            ticker="NVDA",
            company_name="NVIDIA Corp",
            form="10-K",
            fiscal_year=2024,
            source=DataSource.SEC_10K,
        )
        sec10k = SEC10K(metadata=metadata, full_text="", sections=[], financials=None)

        filepath = _save_to_disk(sec10k, output_dir)

        assert filepath.name == "NVDA_10-K_2024.json"

    def test_saves_json_content(self, tmp_path):
        """Test that JSON content is correct."""
        output_dir = tmp_path / "sec_output"
        metadata = SECMetadata(
            ticker="AAPL",
            company_name="Apple Inc.",
            form="10-K",
            source=DataSource.SEC_10K,
        )
        section = SECSection(name="Test Section", content="Test content", word_count=2)
        sec10k = SEC10K(metadata=metadata, full_text="", sections=[section], financials=None)

        filepath = _save_to_disk(sec10k, output_dir)

        with open(filepath) as f:
            data = json.load(f)

        assert data["metadata"]["ticker"] == "AAPL"
        assert data["metadata"]["form"] == "10-K"
        assert len(data["sections"]) == 1
        assert data["sections"][0]["name"] == "Test Section"


# =============================================================================
# Tests for extract_10k (mocked)
# =============================================================================

class TestExtract10k:
    """Tests for the main extract_10k function."""

    @patch("src.ingestion.sec_filing_extractor.Company")
    def test_extracts_10k_successfully(self, mock_company_class):
        """Test successful 10-K extraction with mocked edgartools."""
        filing = create_mock_filing()
        tenk = create_mock_tenk_object()

        mock_filings = Mock()
        mock_filings.latest.return_value = filing
        mock_filings.__iter__ = Mock(return_value=iter([filing]))

        mock_company = Mock()
        mock_company.get_filings.return_value = mock_filings
        mock_company_class.return_value = mock_company

        with patch.object(filing, "obj", return_value=tenk):
            result = extract_10k("AAPL", output_dir=None)

        assert result is not None
        assert result.metadata.ticker == "AAPL"
        assert result.metadata.form == "10-K"

    @patch("src.ingestion.sec_filing_extractor.Company")
    def test_returns_none_for_empty_filings(self, mock_company_class):
        """Test that None is returned when no filings found."""
        mock_company = Mock()
        mock_company.get_filings.return_value = []
        mock_company_class.return_value = mock_company

        result = extract_10k("INVALID", output_dir=None)

        assert result is None


# =============================================================================
# Tests for extract_10q (mocked)
# =============================================================================

class TestExtract10q:
    """Tests for the main extract_10q function."""

    @patch("src.ingestion.sec_filing_extractor.Company")
    def test_extracts_10q_successfully(self, mock_company_class):
        """Test successful 10-Q extraction with mocked edgartools."""
        filing = create_mock_filing()
        tenk = create_mock_tenk_object()

        mock_filings = Mock()
        mock_filings.latest.return_value = filing
        mock_filings.__iter__ = Mock(return_value=iter([filing]))

        mock_company = Mock()
        mock_company.get_filings.return_value = mock_filings
        mock_company_class.return_value = mock_company

        with patch.object(filing, "obj", return_value=tenk):
            result = extract_10q("AAPL", output_dir=None)

        assert result is not None
        assert result.metadata.form == "10-Q"

    @patch("src.ingestion.sec_filing_extractor.Company")
    def test_filters_by_quarter(self, mock_company_class):
        """Test that quarter filtering works."""
        q1_filing = create_mock_filing(date=datetime(2024, 2, 15))
        q1_filing.accession_number = "0000320193-24-000001"

        q2_filing = create_mock_filing(date=datetime(2024, 5, 10))
        q2_filing.accession_number = "0000320193-24-000002"

        mock_filings = Mock()
        mock_filings.__iter__ = Mock(return_value=iter([q1_filing, q2_filing]))
        mock_filings.latest.return_value = q2_filing

        mock_company = Mock()
        mock_company.get_filings.return_value = mock_filings
        mock_company_class.return_value = mock_company

        tenk = create_mock_tenk_object()

        with patch.object(q2_filing, "obj", return_value=tenk):
            result = extract_10q("AAPL", year=2024, quarter=2, output_dir=None)

        assert result is not None


# =============================================================================
# Tests for model serialization
# =============================================================================

class TestSEC10KModel:
    """Tests for SEC10K model serialization."""

    def test_model_dump_serializes_datetime(self):
        """Test that datetime is serialized to string."""
        metadata = SECMetadata(
            ticker="AAPL",
            company_name="Apple Inc.",
            form="10-K",
            filing_date=datetime(2024, 11, 1),
            source=DataSource.SEC_10K,
        )
        sec10k = SEC10K(metadata=metadata, full_text="", sections=[], financials=None)

        data = sec10k.model_dump()

        assert isinstance(data["metadata"]["filing_date"], str)
        assert "2024-11-01" in data["metadata"]["filing_date"]


class TestSECFinancialsModel:
    """Tests for SECFinancials model."""

    def test_can_hold_financial_data(self):
        """Test that financials model can hold all financial data."""
        financials = SECFinancials(
            revenue=391035000000.0,
            net_income=112010000000.0,
            total_assets=364980000000.0,
            operating_income=133050000000.0,
            eps=7.46,
        )

        assert financials.revenue == 391035000000.0
        assert financials.eps == 7.46

    def test_can_have_none_values(self):
        """Test that financial fields can be None."""
        financials = SECFinancials()

        assert financials.revenue is None
        assert financials.eps is None


class TestDataSourceEnum:
    """Tests for DataSource enum."""

    def test_sec_10k_value(self):
        """Test SEC_10K enum value."""
        assert DataSource.SEC_10K.value == "sec_10k"

    def test_sec_10q_value(self):
        """Test SEC_10Q enum value."""
        assert DataSource.SEC_10Q.value == "sec_10q"


class TestSECSectionModel:
    """Tests for SECSection model."""

    def test_can_create_section(self):
        """Test that section can be created."""
        section = SECSection(
            name="Business Description",
            content="Company business content...",
            word_count=5,
        )

        assert section.name == "Business Description"
        assert section.word_count == 5


class TestSECMetadataModel:
    """Tests for SECMetadata model."""

    def test_can_create_metadata(self):
        """Test that metadata can be created."""
        metadata = SECMetadata(
            ticker="AAPL",
            company_name="Apple Inc.",
            cik="320193",
            form="10-K",
            fiscal_year=2024,
            source=DataSource.SEC_10K,
        )

        assert metadata.ticker == "AAPL"
        assert metadata.fiscal_year == 2024
        assert metadata.source == DataSource.SEC_10K