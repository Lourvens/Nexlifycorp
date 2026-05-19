# ADR-001: Unified Chunk Type for Hybrid Knowledge Base

## Status
**Accepted** | Date: 2025-05-18

## Context
We are building a hybrid Knowledge Base system that combines:
1. **Public SEC filings** (10-K, 10-Q from EDGAR)
2. **Internal Nexlify Corp documents** (Confidential board memos, product roadmaps, etc.)

The system needs to:
- Search across both sources when appropriate
- Filter by source type (public vs internal)
- Support access control (different users see different content)
- Classify content by type (risk factors, financials, strategy, etc.)

## Decision Drivers
1. Consistent querying across both public and internal sources
2. Metadata filtering for RBAC (Role-Based Access Control)
3. Content routing (send "risk" questions to risk factor sections)
4. Future extensibility (partner docs, user uploads)

## Decision
We will use a **unified `Chunk` type** that represents atomic content from any source.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        UNIFIED CHUNK                            │
├─────────────────────────────────────────────────────────────────┤
│  content: str              # The actual text to embed           │
│  metadata: ChunkMetadata  # All filtering/classification data   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     CHUNK METADATA                              │
├─────────────────────────────────────────────────────────────────┤
│  SOURCE IDENTIFICATION                                          │
│  ├── chunk_id: str           # Unique ID "nvda_10k_2025_risk_001"│
│  ├── document_id: str       # Parent document ID                │
│  ├── source_category: Enum  # PUBLIC_SEC | INTERNAL_NEXLIFY     │
│  └── source_detail: str     # Specific source identifier        │
│                                                                 │
│  ACCESS CONTROL                                                 │
│  ├── access_level: Enum    # PUBLIC | INTERNAL | CONFIDENTIAL  │
│  └── is_public: bool        # Quick filter for public docs       │
│                                                                 │
│  CONTENT CLASSIFICATION                                         │
│  └── content_type: Enum     # RISK_FACTORS | FINANCIALS | etc   │
│                                                                 │
│  SOURCE-SPECIFIC (nullable)                                     │
│  ├── SEC: ticker, form, section, fiscal_year, cik              │
│  └── Internal: doc_type, section_path                          │
│                                                                 │
│  TEMPORAL                                                       │
│  ├── document_date: datetime                                   │
│  └── ingestion_date: datetime                                   │
│                                                                 │
│  INDICATORS                                                     │
│  ├── contains_financials: bool                                 │
│  ├── contains_projections: bool                                │
│  └── topics: list[str]                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Key Enums

```python
class DataSourceCategory(str, Enum):
    PUBLIC_SEC = "public_sec"
    INTERNAL_NEXLIFY = "internal_nexlify"
    EXTERNAL_PARTNER = "external_partner"
    USER_UPLOADED = "user_uploaded"

class ContentType(str, Enum):
    RISK_FACTORS = "risk_factors"
    FINANCIAL_STATEMENTS = "financial_statements"
    MANAGEMENT_DISCUSSION = "management_discussion"
    PRODUCT_ROADMAP = "product_roadmap"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    STRATEGY = "strategy"
    # ... etc

class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    STRICTLY_CONFIDENTIAL = "strictly_confidential"
```

## Consequences

### Positive
1. **Consistent storage**: All chunks in one Chroma collection with uniform metadata
2. **Flexible querying**: Filter by source, content type, or access level
3. **RBAC-ready**: Access level field enables role-based filtering
4. **Content routing**: content_type enables intelligent routing to relevant sections
5. **Future-proof**: New source types can use the same structure

### Negative
1. **Metadata overhead**: Every chunk has ~20 metadata fields (some nullable)
2. **Schema migration**: Existing systems need migration path
3. **Complexity**: More fields to manage than simple source/dest approach

### Neutral
1. Extractor layer (SECSection, InternalSection) remains unchanged
2. ChunkBuilder will convert extractors → Chunks (not yet implemented)

## Alternatives Considered

### Option A: Separate Collections
Store SEC filings and internal docs in separate Chroma collections.

**Rejected because:**
- Harder to query across both sources
- Duplicated metadata schemas
- No unified access control

### Option B: Source Field Only
Single `source` field with values like "nvda_10k", "nexlify_roadmap".

**Rejected because:**
- No structured filtering (access level, content type)
- Harder to implement RBAC
- Less explicit about what the metadata means

## Implementation Notes

1. **ChunkBuilder** (TODO): Will convert `SECSection` → `Chunk` and `InternalSection` → `Chunk`
2. **Chroma Storage**: Store all chunks in single collection with metadata filters
3. **Query Pattern**: 
   ```python
   results = collection.query(
       query_texts=["What are NVIDIA's competitive risks?"],
       where={
           "source_category": "public_sec",
           "content_type": "risk_factors",
       }
   )
   ```

## Related ADRs
- ADR-002: Chunking Strategy (planned)
- ADR-003: Embedding Model Selection (planned)

## Review
Review after Day 5 when ChunkBuilder is implemented.