"""SEC Filing Extractor using edgartools."""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from edgar import Company, set_identity

from src.ingestion.types import (
    SEC10K,
    SECMetadata,
    SECSection,
    SECFinancials,
    DataSourceCategory,
    DataSource,
)
from src.utils.logger import logger
from src.utils.text_cleaner import clean_text


DEFAULT_OUTPUT_DIR = Path("data/extracted/public")


def extract_10k(
    ticker: str,
    year: int | None = None,
    identity: str = "NexlifyKB/research@nexlify.com",
    output_dir: Path | None = DEFAULT_OUTPUT_DIR,
) -> Optional[SEC10K]:
    """
    Extract a 10-K filing for a company.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "NVDA")
        year: Specific year to extract (None for latest)
        identity: User identity for SEC EDGAR (required by SEC)
        output_dir: Directory to save extracted JSON (None to skip saving)

    Returns:
        SEC10K object with extracted data, or None if failed
    """
    set_identity(identity)

    try:
        logger.info(f"[cyan]Extracting 10-K for {ticker}[cyan] ([yellow]year: {year or 'latest'}[yellow])")

        company = Company(ticker)
        filings = company.get_filings(form="10-K")

        if not filings:
            logger.warning(f"[yellow]No 10-K filings found for {ticker}[yellow]")
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
                logger.warning(f"[yellow]No 10-K found for {ticker} in {year}[yellow]")
                filing = filings.latest()
        else:
            filing = filings.latest()

        logger.info(f"[cyan]Found filing:[/cyan] [yellow]{filing.accession_number}[yellow] | date: [cyan]{filing.filing_date}[cyan]")

        # Get 10-K object with all parsed data
        tenk_obj = filing.obj()

        # Extract metadata
        metadata = _extract_metadata(ticker, tenk_obj, filing, DataSource.SEC_10K)

        # Extract all sections
        sections = _extract_sections(tenk_obj)

        # Extract financials from XBRL
        financials = _extract_financials(tenk_obj)

        # Get full text (disabled for now - only extract sections)
        full_text = ""  # Full text extraction disabled for pipeline efficiency

        # Build SEC10K object
        sec10k = SEC10K(
            metadata=metadata,
            full_text=full_text,
            sections=sections,
            financials=financials,
        )

        logger.info(
            f"[cyan]Extracted 10-K for {ticker}[cyan]: [bold]{len(sections)}[/bold] sections"
        )

        # Save to disk if output_dir provided
        if output_dir:
            _save_to_disk(sec10k, output_dir)

        return sec10k

    except Exception as e:
        logger.error(f"[red]✗[/red] Error extracting 10-K for {ticker}: {e}")
        return None


def extract_10q(
    ticker: str,
    year: int | None = None,
    quarter: int | None = None,
    identity: str = "NexlifyKB/research@nexlify.com",
    output_dir: Path | None = DEFAULT_OUTPUT_DIR,
) -> Optional[SEC10K]:
    """
    Extract a 10-Q filing for a company.

    Args:
        ticker: Stock ticker symbol
        year: Specific year (None for latest)
        quarter: Q1, Q2, Q3, or Q4 (None for latest)
        identity: User identity for SEC EDGAR
        output_dir: Directory to save extracted JSON (None to skip saving)

    Returns:
        SEC10K object with extracted data, or None if failed
    """
    set_identity(identity)

    try:
        logger.info(
            f"[cyan]Extracting 10-Q for {ticker}[cyan] "
            f"([yellow]year: {year or 'latest'}[yellow], [cyan]quarter: {quarter or 'latest'}[cyan])"
        )

        company = Company(ticker)
        filings = company.get_filings(form="10-Q")

        if not filings:
            logger.warning(f"[yellow]No 10-Q filings found for {ticker}[yellow]")
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

        # Full text (disabled for now)
        full_text = ""  # Full text extraction disabled for pipeline efficiency

        sec10k = SEC10K(
            metadata=metadata,
            full_text=full_text,
            sections=sections,
            financials=financials,
        )

        logger.info(f"[cyan]Extracted 10-Q for {ticker}[cyan]: [bold]{len(sections)}[/bold] sections")

        # Save to disk if output_dir provided
        if output_dir:
            _save_to_disk(sec10k, output_dir)

        return sec10k

    except Exception as e:
        logger.error(f"[red]✗[/red] Error extracting 10-Q for {ticker}: {e}")
        return None


def _extract_metadata(
    ticker: str,
    filing_obj,
    filing,
    source: DataSource,
) -> SECMetadata:
    """Extract metadata from filing object."""
    # Get CIK from filing.cik attribute
    cik = None
    try:
        cik = str(filing.cik) if hasattr(filing, "cik") else None
    except Exception:
        pass

    # Get auditor info
    auditor = None
    try:
        if hasattr(filing_obj, "auditor") and filing_obj.auditor:
            auditor = filing_obj.auditor.name if hasattr(filing_obj.auditor, "name") else str(filing_obj.auditor)
    except Exception:
        pass

    return SECMetadata(
        ticker=ticker,
        company_name=filing_obj.company if hasattr(filing_obj, "company") else ticker,
        cik=cik,
        accession_number=filing.accession_number,
        form="10-K" if source == DataSource.SEC_10K else "10-Q",
        filing_date=filing.filing_date,
        document_date=filing.filing_date,
        fiscal_year=filing.filing_date.year if filing.filing_date else None,
        auditor=auditor,
        source=source,
    )


def _extract_sections(filing_obj) -> list[SECSection]:
    """Extract all key sections from filing object."""
    sections = []

    # Section attribute mapping for 10-K
    section_mapping = {
        "business": "Business Description",
        "risk_factors": "Risk Factors",
        "management_discussion": "Management's Discussion and Analysis",
        "notes": "Notes to Financial Statements",
    }

    for attr, name in section_mapping.items():
        try:
            content = getattr(filing_obj, attr, None)
            if content and isinstance(content, str) and len(content) > 100:
                # Clean the content
                content = clean_text(content)
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
    if not hasattr(filing_obj, "financials") or not filing_obj.financials:
        return None

    try:
        financials = SECFinancials()
        fin = filing_obj.financials

        # Get the FY column (first data column)
        def get_fy_col(df):
            # For income statement: look for FY in column name
            fy_cols = [c for c in df.columns if "FY" in str(c)]
            if fy_cols:
                return fy_cols[0]
            # For balance sheet: use first date column
            date_cols = [c for c in df.columns if c not in ['concept', 'label', 'standard_concept', 'level', 'abstract', 'dimension', 'is_breakdown', 'dimension_axis', 'dimension_member', 'dimension_member_label', 'dimension_label', 'balance', 'weight', 'preferred_sign', 'parent_concept', 'parent_abstract_concept']]
            return date_cols[0] if date_cols else df.columns[-1]

        # Extract from income statement
        try:
            income = fin.income_statement()
            income_df = income.to_dataframe()
            fy_col = get_fy_col(income_df)

            # Map label to financial field
            label_to_field = {
                "net sales": "revenue",
                "revenue": "revenue",
                "total revenue": "revenue",
                "net income": "net_income",
                "operating income": "operating_income",
                "basic (in dollars per share)": "eps",
                "diluted (in dollars per share)": "eps",
            }

            for idx, row in income_df.iterrows():
                label = str(row.get("label", "")).lower().strip()
                
                # Check for match
                if label in label_to_field:
                    field = label_to_field[label]
                    val = row[fy_col]
                    if val and isinstance(val, (int, float)) and not str(val) == "nan":
                        try:
                            setattr(financials, field, float(val))
                        except (ValueError, TypeError):
                            pass
        except Exception as e:
            logger.debug(f"Income statement extraction error: {e}")

        # Extract from balance sheet
        try:
            balance = fin.balance_sheet()
            balance_df = balance.to_dataframe()
            fy_col = get_fy_col(balance_df)

            label_to_field = {
                "total assets": "total_assets",
                "total stockholders' equity": "total_equity",
                "total equity": "total_equity",
            }

            for idx, row in balance_df.iterrows():
                label = str(row.get("label", "")).lower().strip()
                
                if label in label_to_field:
                    field = label_to_field[label]
                    val = row[fy_col]
                    if val and isinstance(val, (int, float)) and not str(val) == "nan":
                        try:
                            setattr(financials, field, float(val))
                        except (ValueError, TypeError):
                            pass
        except Exception as e:
            logger.debug(f"Balance sheet extraction error: {e}")

        return financials

    except Exception as e:
        logger.warning(f"Financials extraction error: {e}")
        return None


def _get_quarter(date: datetime) -> int:
    """Get quarter from date."""
    return (date.month - 1) // 3 + 1


def _save_to_disk(sec10k: SEC10K, output_dir: Path) -> Path:
    """Save SEC10K to JSON file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Filename: {ticker}_{form}_{year}.json
    fiscal_year = sec10k.metadata.fiscal_year or "unknown"
    filename = f"{sec10k.metadata.ticker}_{sec10k.metadata.form}_{fiscal_year}.json"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sec10k.model_dump(), f, indent=2, default=str)

    logger.info(f"[green]✓[/green] Saved: [dim]{filepath}[dim]")
    return filepath


if __name__ == "__main__":
    # Test extraction
    result = extract_10k("AAPL", 2024)
    if result:
        logger.info(f"Extracted: {result.metadata.company_name}")
        logger.info(f"Sections: {len(result.sections)}")
        logger.info(f"CIK: {result.metadata.cik}")
        logger.info(f"Auditor: {result.metadata.auditor}")
        if result.financials:
            logger.info(f"Revenue: {result.financials.revenue}")
    else:
        logger.error("Extraction failed")