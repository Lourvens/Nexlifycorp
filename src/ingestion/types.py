"""Unified types for hybrid Knowledge Base (SEC + Internal Docs)."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# =============================================================================
# DATA SOURCE ENUMS (with backward compatibility)
# =============================================================================

# New unified naming
class DataSourceCategory(str, Enum):
    """Category of data source."""
    PUBLIC_SEC = "public_sec"              # SEC EDGAR filings
    INTERNAL_NEXLIFY = "internal_nexlify"  # Nexlify Corp internal docs
    EXTERNAL_PARTNER = "external_partner"  # Future: partner data
    USER_UPLOADED = "user_uploaded"        # Future: user documents


# Backward compatibility alias (old SEC-only naming)
class DataSource(str, Enum):
    """Backward compatibility alias - prefer DataSourceCategory."""
    SEC_10K = "sec_10k"
    SEC_10Q = "sec_10q"


class SECFormType(str, Enum):
    """SEC form types."""
    FORM_10K = "10-K"
    FORM_10Q = "10-Q"
    FORM_8K = "8-K"


class InternalDocType(str, Enum):
    """Internal document types from Nexlify Corp."""
    ANNUAL_REVIEW = "annual_review"
    BOARD_MEMO = "board_memo"
    PRODUCT_ROADMAP = "product_roadmap"
    RISK_REGISTER = "risk_register"
    FINANCIAL_REVIEW = "financial_review"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    POLICY = "policy"
    EARNINGS_PREP = "earnings_prep"
    SUPPLY_CHAIN = "supply_chain"


# =============================================================================
# CONTENT CLASSIFICATION
# =============================================================================

class ContentType(str, Enum):
    """What kind of content is in the chunk."""
    RISK_FACTORS = "risk_factors"
    FINANCIAL_STATEMENTS = "financial_statements"
    MANAGEMENT_DISCUSSION = "management_discussion"
    BUSINESS_DESCRIPTION = "business_description"
    PRODUCT_ROADMAP = "product_roadmap"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    STRATEGY = "strategy"
    GOVERNANCE = "governance"
    TECHNICAL_SPEC = "technical_spec"
    PROJECTION = "projection"
    POLICY = "policy"
    GENERAL = "general"


class AccessLevel(str, Enum):
    """Access control levels."""
    PUBLIC = "public"                         # Anyone
    INTERNAL = "internal"                    # Nexlify employees
    CONFIDENTIAL = "confidential"            # Executive only
    STRICTLY_CONFIDENTIAL = "strictly_confidential"  # Board/ExComm only


# =============================================================================
# UNIFIED CHUNK TYPE
# =============================================================================

class ChunkMetadata(BaseModel):
    """
    Unified metadata for ALL document chunks (public + internal).
    
    This is the single source of truth for:
    - Source identification
    - Content classification
    - Access control
    - Temporal data
    - Domain filtering
    """
    
    # ─────────────────────────────────────────────────────────────────────
    # SOURCE IDENTIFICATION (REQUIRED)
    # ─────────────────────────────────────────────────────────────────────
    
    chunk_id: str = Field(description="Unique ID for this chunk")
    document_id: str = Field(description="Parent document ID")
    
    source_category: DataSourceCategory = Field(
        description="High-level category: public vs internal"
    )
    source_detail: str = Field(
        description="Specific source: 'nvda_10k_2025', 'nexlify_annual_review', etc."
    )
    
    # ─────────────────────────────────────────────────────────────────────
    # ACCESS CONTROL
    # ─────────────────────────────────────────────────────────────────────
    
    access_level: AccessLevel = Field(
        default=AccessLevel.INTERNAL,
        description="Who can see this chunk"
    )
    is_public: bool = Field(
        default=False,
        description="True = SEC/public filing, False = internal doc"
    )
    
    # ─────────────────────────────────────────────────────────────────────
    # CONTENT CLASSIFICATION
    # ─────────────────────────────────────────────────────────────────────
    
    content_type: ContentType = Field(
        default=ContentType.GENERAL,
        description="What kind of content"
    )
    
    # ─────────────────────────────────────────────────────────────────────
    # SOURCE-SPECIFIC FIELDS (nullable, only set for relevant sources)
    # ─────────────────────────────────────────────────────────────────────
    
    # SEC-specific fields
    ticker: str | None = Field(default=None, description="Stock ticker (SEC docs)")
    sec_form: SECFormType | None = Field(default=None, description="10-K, 10-Q")
    sec_section: str | None = Field(default=None, description="Item 1A, 7, etc.")
    fiscal_year: int | None = Field(default=None, description="Fiscal year")
    fiscal_quarter: int | None = Field(default=None, description="Fiscal quarter")
    cik: str | None = Field(default=None, description="SEC CIK number")
    
    # Internal doc fields
    internal_doc_type: InternalDocType | None = Field(
        default=None, 
        description="Type of internal document"
    )
    internal_section_path: str | None = Field(
        default=None,
        description="Section path like '3. Product / 3.1 NEXL-X3'"
    )
    
    # ─────────────────────────────────────────────────────────────────────
    # TEMPORAL & OTHER
    # ─────────────────────────────────────────────────────────────────────
    
    document_date: datetime | None = Field(
        default=None,
        description="Date of the original document"
    )
    ingestion_date: datetime = Field(
        default_factory=datetime.now,
        description="When chunk was created"
    )
    
    # Content indicators
    contains_financials: bool = False
    contains_projections: bool = False
    contains_confidential_info: bool = False
    
    # Topics extracted from content
    topics: list[str] = Field(default_factory=list)


class Chunk(BaseModel):
    """
    Unified chunk representing a unit of content from any source.
    
    This is the atomic unit stored in the vector database.
    """
    
    content: str = Field(
        description="The actual text content to embed and retrieve"
    )
    
    metadata: ChunkMetadata = Field(
        description="All metadata for filtering and access control"
    )
    
    # For debugging/traceability
    source_filename: str | None = None
    
    def to_chroma_metadata(self) -> dict:
        """Convert to Chroma-compatible metadata dict."""
        m = self.metadata
        
        return {
            # Required for Chroma
            "chunk_id": m.chunk_id,
            "document_id": m.document_id,
            
            # Source
            "source_category": m.source_category.value,
            "source_detail": m.source_detail,
            
            # Access control
            "access_level": m.access_level.value,
            "is_public": m.is_public,
            
            # Content classification
            "content_type": m.content_type.value,
            
            # SEC fields (nullable)
            "ticker": m.ticker or "",
            "sec_form": m.sec_form.value if m.sec_form else "",
            "sec_section": m.sec_section or "",
            "fiscal_year": m.fiscal_year or 0,
            "fiscal_quarter": m.fiscal_quarter or 0,
            
            # Internal doc fields (nullable)
            "internal_doc_type": m.internal_doc_type.value if m.internal_doc_type else "",
            "internal_section_path": m.internal_section_path or "",
            
            # Indicators
            "contains_financials": m.contains_financials,
            "contains_projections": m.contains_projections,
            "contains_confidential_info": m.contains_confidential_info,
            
            # Dates
            "document_date": m.document_date.isoformat() if m.document_date else "",
            "ingestion_date": m.ingestion_date.isoformat(),
            
            # Topics (join to string for Chroma)
            "topics": ",".join(m.topics) if m.topics else "",
        }
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "content": self.content,
            "metadata": {
                "chunk_id": self.metadata.chunk_id,
                "document_id": self.metadata.document_id,
                "source_category": self.metadata.source_category.value,
                "source_detail": self.metadata.source_detail,
                "access_level": self.metadata.access_level.value,
                "is_public": self.metadata.is_public,
                "content_type": self.metadata.content_type.value,
                "ticker": self.metadata.ticker,
                "sec_form": self.metadata.sec_form.value if self.metadata.sec_form else None,
                "sec_section": self.metadata.sec_section,
                "fiscal_year": self.metadata.fiscal_year,
                "fiscal_quarter": self.metadata.fiscal_quarter,
                "cik": self.metadata.cik,
                "internal_doc_type": self.metadata.internal_doc_type.value if self.metadata.internal_doc_type else None,
                "internal_section_path": self.metadata.internal_section_path,
                "document_date": self.metadata.document_date.isoformat() if self.metadata.document_date else None,
                "ingestion_date": self.metadata.ingestion_date.isoformat(),
                "contains_financials": self.metadata.contains_financials,
                "contains_projections": self.metadata.contains_projections,
                "contains_confidential_info": self.metadata.contains_confidential_info,
                "topics": self.metadata.topics,
            },
            "source_filename": self.source_filename,
        }


# =============================================================================
# SEC FILING TYPES (Original - kept for extraction layer)
# =============================================================================

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
    source: DataSource = DataSource.SEC_10K  # Backward compatibility


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
        if data["metadata"]["filing_date"]:
            data["metadata"]["filing_date"] = data["metadata"]["filing_date"].isoformat()
        if data["metadata"]["document_date"]:
            data["metadata"]["document_date"] = data["metadata"]["document_date"].isoformat()
        return data


# =============================================================================
# INTERNAL DOCUMENT TYPES (Original - kept for extraction layer)
# =============================================================================

class InternalSection(BaseModel):
    """A section extracted from an internal document."""
    # Content
    title: str
    content: str = ""
    level: int = 2  # H2 or H3

    # Document metadata (inherited)
    company: str = "Nexlify Corp"
    document_type: str
    document_id: str | None = None
    classification: str
    date: datetime | None = None

    # Section-specific metadata
    section_path: str = ""
    topics: list[str] = Field(default_factory=list)
    contains_financials: bool = False
    contains_projections: bool = False


class InternalDocument(BaseModel):
    """Complete internal document data."""
    sections: list[InternalSection] = Field(default_factory=list)

    @property
    def metadata(self) -> dict:
        """Get document-level metadata from first section."""
        if self.sections:
            s = self.sections[0]
            return {
                "company": s.company,
                "document_type": s.document_type,
                "document_id": s.document_id,
                "classification": s.classification,
                "date": s.date,
            }
        return {}
