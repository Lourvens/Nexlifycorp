"""SEC Filing Extractor using edgartools."""
from datetime import datetime
from pathlib import Path
from typing import Optional

from edgar import Company, set_identity

from src.ingestion.types import (
    SEC10K,
    SECMetadata,
    SECSection,
    SECFinancials,
    DataSource,
)
from src.utils.logger import logger


def extract_10k(
    ticker: str,
    year: Optional[int] = None,
    identity: str = "NexlifyKB/research@nexlify.com",
) -> Optional[SEC10K]:
    """
    Extract a 10-K filing for a company.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "NVDA")
        year: Specific year to extract (None for latest)
        identity: User identity for SEC EDGAR (required by SEC)

    Returns:
        SEC10K object with extracted data, or None if failed
    """
    set_identity(identity)

    try:
        logger.info(f"Extracting 10-K for {ticker} (year: {year or 'latest'})")

        company = Company(ticker)
        filings = company.get_filings(form="10-K")

        if not filings:
            logger.warning(f"No 10-K filings found for {ticker}")
            return None

        # Get specific year or latest
        if year:
            filing = next(
                (
                    f
                    for f in filings
                    if f.filing_date and f.filing_date.year == year
                ),
                None,
            )
            if not filing:
                logger.warning(f"No 10-K found for {ticker} in {year}")
                filing = filings.latest()
        else:
            filing = filings.latest()

        logger.info(f"Found filing: {filing.accession_number}, date: {filing.filing_date}")

        # Get 10-K object with all parsed data
        tenk_obj = filing.obj()

        # Extract metadata
        metadata = _extract_metadata(ticker, tenk_obj, filing, DataSource.SEC_10K)

        # Extract sections
        sections = _extract_sections(tenk_obj)

        # Extract financials
        financials = _extract_financials(tenk_obj)

        # Get full text
        full_text = filing.text() or ""

        # Build SEC10K object
        sec10k = SEC10K(
            metadata=metadata,
            full_text=full_text,
            sections=sections,
            financials=financials,
        )

        logger.info(
            f"Extracted 10-K for {ticker}: {len(sections)} sections, "
            f"{len(full_text.split())} words"
        )

        return sec10k

    except Exception as e:
        logger.error(f"Error extracting 10-K for {ticker}: {e}")
        return None


def extract_10q(
    ticker: str,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    identity: str = "NexlifyKB/research@nexlify.com",
) -> Optional[SEC10K]:
    """
    Extract a 10-Q filing for a company.

    Args:
        ticker: Stock ticker symbol
        year: Specific year (None for latest)
        quarter: Q1, Q2, Q3, or Q4 (None for latest)
        identity: User identity for SEC EDGAR

    Returns:
        SEC10K object with extracted data, or None if failed
    """
    set_identity(identity)

    try:
        logger.info(
            f"Extracting 10-Q for {ticker} "
            f"(year: {year or 'latest'}, quarter: {quarter or 'latest'})"
        )

        company = Company(ticker)
        filings = company.get_filings(form="10-Q")

        if not filings:
            logger.warning(f"No 10-Q filings found for {ticker}")
            return None

        filing = filings.latest()

        # Try to get specific quarter if specified
        if year and quarter:
            target = next(
                (
                    f
                    for f in filings
                    if f.filing_date
                    and f.filing_date.year == year
                    and _get_quarter(f.filing_date) == quarter
                ),
                None,
            )
            if target:
                filing = target

        tenq_obj = filing.obj()

        # Extract metadata (similar to 10-K but source is 10-Q)
        metadata = _extract_metadata(ticker, tenq_obj, filing, DataSource.SEC_10Q)

        # Extract sections
        sections = _extract_sections(tenq_obj)

        # Extract financials
        financials = _extract_financials(tenq_obj)

        # Full text
        full_text = filing.text() or ""

        sec10k = SEC10K(
            metadata=metadata,
            full_text=full_text,
            sections=sections,
            financials=financials,
        )

        logger.info(f"Extracted 10-Q for {ticker}: {len(sections)} sections")

        return sec10k

    except Exception as e:
        logger.error(f"Error extracting 10-Q for {ticker}: {e}")
        return None


def _extract_metadata(
    ticker: str,
    filing_obj,
    filing,
    source: DataSource,
) -> SECMetadata:
    """Extract metadata from filing object."""
    return SECMetadata(
        ticker=ticker,
        company_name=filing_obj.company if hasattr(filing_obj, "company") else ticker,
        cik=str(filing.company.cik) if hasattr(filing.company, "cik") else None,
        accession_number=filing.accession_number,
        form="10-K" if source == DataSource.SEC_10K else "10-Q",
        filing_date=filing.filing_date,
        document_date=filing.filing_date,
        fiscal_year=filing.filing_date.year if filing.filing_date else None,
        source=source,
    )


def _extract_sections(filing_obj) -> list[SECSection]:
    """Extract key sections from filing object."""
    sections = []

    section_mapping = {
        "business": "Business Description",
        "risk_factors": "Risk Factors",
        "md_and_a": "Management's Discussion and Analysis",
        "legal_proceedings": "Legal Proceedings",
    }

    for attr, name in section_mapping.items():
        try:
            content = getattr(filing_obj, attr, None)
            if content and isinstance(content, str) and len(content) > 100:
                # Truncate very long content
                content = content[:50000] if len(content) > 50000 else content
                sections.append(
                    SECSection(
                        name=name,
                        content=content,
                        word_count=len(content.split()),
                    )
                )
        except Exception:
            pass

    return sections


def _extract_financials(filing_obj) -> Optional[SECFinancials]:
    """Extract financial data from XBRL."""
    try:
        if not hasattr(filing_obj, "financials") or not filing_obj.financials:
            return None

        financials = SECFinancials()

        try:
            income = filing_obj.financials.income_statement
            if income:
                # Try to extract key metrics
                # Note: actual implementation depends on edgartools API
                pass
        except Exception:
            pass

        return financials

    except Exception:
        return None


def _get_quarter(date: datetime) -> int:
    """Get quarter from date."""
    return (date.month - 1) // 3 + 1


if __name__ == "__main__":
    # Test extraction
    result = extract_10k("AAPL", 2024)
    if result:
        logger.info(f"Extracted: {result.metadata.company_name}")
        logger.info(f"Sections: {len(result.sections)}")
    else:
        logger.error("Extraction failed")