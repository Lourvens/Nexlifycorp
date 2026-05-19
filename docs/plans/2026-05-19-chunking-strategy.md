# Chunking Strategy Design

**Date**: 2026-05-19
**Status**: Approved
**Related**: ADR-001 (Unified Chunk Type)

---

## Overview

Two distinct chunking strategies based on document source:

| Source | Strategy | Chunk Size | Overlap |
|--------|----------|------------|---------|
| **SEC Filings** | Paragraph + Sentence splitting | 1000 chars | 200 chars |
| **Internal Docs** | Header-based (H3 granularity) | Variable | None |

---

## SEC Filing Chunking

### Why Paragraph Splitting?

SEC sections are massive (Risk Factors: 106K chars). Naive chunking loses context.

### Algorithm

```
1. Receive: SECSection(content, name, metadata)
2. Split by \n\n (natural paragraphs)
3. For each paragraph:
   - If > 1200 chars, split by sentence (~150 chars)
   - If still > 1200 chars, split by 500 char blocks
4. Create Chunk with:
   - content = "[Section Name] paragraph text..."
   - metadata.sec_section = "Item 1A" (mapped from section name)
5. Return list of Chunks
```

### Chunk ID Format
```
{sec_ticker}_{sec_form}_{fiscal_year}_{section_slug}_{index:04d}
Example: nvda_10k_2024_risk_factors_0001
```

### Section Name Mapping

| SECSection.name | sec_section |
|-----------------|-------------|
| Business Description | Item 1 |
| Risk Factors | Item 1A |
| Management's Discussion and Analysis | Item 7 |
| Notes to Financial Statements | Item 8 |

---

## Internal Document Chunking

### Why H3 Granularity?

Internal docs have variable header depths. H3 provides:
- Self-contained content (usually 300-2000 chars)
- Meaningful context when combined with parent H2 path
- Granularity for precise retrieval

### Algorithm

```
1. Receive: InternalDocument(sections[])
2. Filter: H3 sections only (skip H2 containers, H1 title)
3. For each H3 with content > 0 chars:
   - Find parent H2 for section_path
   - Build chunk_id from doc_id + H2/H3 slugs
   - Create Chunk with:
     - content = "parent_h2_title / h3_title: h3_content..."
     - metadata.section_path = "X. Parent / X.Y Child"
4. Skip: H2 with no H3 children, empty H3 sections
```

### Chunk ID Format
```
{internal_doc_type}_{doc_id}_{h2_index}_{h3_index:02d}
Example: board-memo_NBPQ4-2025-001_02_01
```

---

## Metadata Population

### Required Fields (All Chunks)

```python
ChunkMetadata(
    chunk_id="...",           # Generated as above
    document_id="...",        # Ticker+form+year or internal doc_id
    source_category=...,      # PUBLIC_SEC or INTERNAL_NEXLIFY
    source_detail="...",      # "nvda_10k_2024" or "nexlify_board_memo"
    access_level=...,         # PUBLIC or from classification
    is_public=...,            # True for SEC, False for internal
    content_type=...,         # From section/document analysis
    content="...",            # Chunk text with context prefix
    topics=[],                # Extracted keywords
    contains_financials=...,  # Pattern matching
    contains_projections=..., # Pattern matching
)
```

### Source-Specific Fields

| Field | SEC | Internal |
|-------|-----|----------|
| ticker | ✅ NVDA | ❌ |
| sec_form | ✅ 10-K | ❌ |
| sec_section | ✅ Item 1A | ❌ |
| fiscal_year | ✅ 2024 | ❌ |
| internal_doc_type | ❌ | ✅ Board Memo |
| internal_section_path | ❌ | ✅ "2. CEO Review / 2.1 Financial" |

---

## Content Type Classification

### Automatic Detection

| Pattern | ContentType |
|---------|-------------|
| "risk", "Risk Factor" | RISK_FACTORS |
| "$", "revenue", "income", "%" | FINANCIAL_STATEMENTS |
| "We expect", "forecast", "target" | MANAGEMENT_DISCUSSION |
| "product", "roadmap", "NEXL-X" | PRODUCT_ROADMAP |
| "competitor", "NVIDIA", "AMD" | COMPETITIVE_ANALYSIS |
| Default | GENERAL |

---

## Implementation Plan

### Phase 1: Core Chunk Builder
- [ ] `src/ingestion/chunk_builder.py` - Base class
- [ ] `SECChunker` - Paragraph/sentence splitting
- [ ] `InternalChunker` - H3 extraction with hierarchy

### Phase 2: Chunk Processing
- [ ] Content type detection
- [ ] Topic extraction (reuse from extractor)
- [ ] Financial/projection flagging

### Phase 3: Integration
- [ ] Connect to existing extractors
- [ ] Save chunks to JSON for inspection
- [ ] Unit tests for both chunkers

---

## File Structure

```
src/ingestion/
├── chunk_builder.py      # Base classes + factory
├── chunk_strategies/
│   ├── __init__.py
│   ├── sec_chunker.py    # SEC paragraph splitting
│   └── internal_chunker.py # Internal H3 extraction
└── types.py              # Already defined: Chunk, ChunkMetadata

tests/unit/
├── test_sec_chunker.py
└── test_internal_chunker.py
```

---

## Example Outputs

### SEC Chunk
```json
{
  "content": "[Risk Factors] NVIDIA Corporation faces various risks including: competition in the AI chip market, supply chain disruptions, and regulatory challenges in international markets. Our dependence on TSMC for chip manufacturing poses operational risks...",
  "metadata": {
    "chunk_id": "nvda_10k_2024_risk_factors_0001",
    "document_id": "nvda_10k_2024",
    "source_category": "public_sec",
    "source_detail": "nvda_10k_2024",
    "ticker": "NVDA",
    "sec_form": "10-K",
    "sec_section": "Item 1A",
    "fiscal_year": 2024,
    "content_type": "risk_factors",
    "contains_financials": false,
    "topics": ["NVIDIA", "AI", "GPU"]
  }
}
```

### Internal Chunk
```json
{
  "content": "2. CEO Strategic Review / 2.1 Financial Performance: Q4 revenue reached $36.2B, exceeding guidance by 8%. AI infrastructure demand drove 3x growth in data center segment...",
  "metadata": {
    "chunk_id": "board-memo_NBPQ4-2025-001_02_01",
    "document_id": "NBPQ4-2025-001",
    "source_category": "internal_nexlify",
    "source_detail": "nexlify_board_memo",
    "internal_doc_type": "board_memo",
    "internal_section_path": "2. CEO Strategic Review / 2.1 Financial Performance",
    "classification": "CONFIDENTIAL",
    "content_type": "financial_statements",
    "contains_financials": true,
    "contains_projections": false,
    "topics": ["revenue", "AI", "data center"]
  }
}
```

---

## Next Steps

1. Implement `SECChunker.paragraph_split()`
2. Implement `InternalChunker.h3_extract()`
3. Add content type detection
4. Write unit tests
5. Integrate with extraction pipeline