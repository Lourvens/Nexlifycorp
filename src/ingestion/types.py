"""SEC Filing Extraction Types."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DataSource(str, Enum):
    """Source of the document data."""
    SEC_10K = "sec_10k"
    SEC_10Q = "sec_10q"


class SECMetadata(BaseModel):
    """Metadata extracted from SEC filing."""
    ticker: str
    company_name: str
    cik: str | None = None
    accession_number: str | None = None
    form: str
    filing_date: datetime | None = None
    document_date: datetime | None = None
    fiscal_year: int | None = None
    fiscal_quarter: int | None = None
    auditor: str | None = None
    source: DataSource = DataSource.SEC_10K


class SECSection(BaseModel):
    """A section extracted from a SEC filing."""
    name: str
    content: str = ""
    word_count: int = 0


class SECFinancials(BaseModel):
    """Financial data extracted from XBRL."""
    revenue: float | None = None
    net_income: float | None = None
    total_assets: float | None = None
    total_equity: float | None = None
    operating_income: float | None = None
    eps: float | None = None


class SEC10K(BaseModel):
    """Complete 10-K/10-Q filing data."""
    metadata: SECMetadata
    full_text: str = ""
    sections: list[SECSection] = Field(default_factory=list)
    financials: SECFinancials | None = None

    def model_dump(self, **kwargs):
        """Convert to dict for JSON serialization."""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to strings
        if data["metadata"]["filing_date"]:
            data["metadata"]["filing_date"] = data["metadata"]["filing_date"].isoformat()
        if data["metadata"]["document_date"]:
            data["metadata"]["document_date"] = data["metadata"]["document_date"].isoformat()
        return data