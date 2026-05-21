# Architecture

NexlifyCorp is a hybrid Knowledge Base + Agentic AI system.

## Tech Stack

- **LangChain + LangGraph** — orchestration and agentic workflows
- **Qdrant** — vector store for embeddings and similarity search
- **Claude** — LLM for extraction, summarization, and reasoning
- **SEC EDGAR** (via `edgartools`) — real public filings
- **Internal docs** — fictional enterprise documents

## Data Flow

```
SEC EDGAR / Internal Docs
       ↓
   [Extractors] → SEC10K, InternalDocument
       ↓
   [Chunkers] → unified Chunk objects
       ↓
   [VectorStore] → Qdrant (embedding + storage)
       ↓
   [Retrieval] → LangChain chains + LangGraph agents
```

## Extraction Layer

### SEC Extraction (`src/ingestion/sec_filing_extractor.py`)

- `edgartools` library with `set_identity(identity)` before SEC requests
- Extracts sections: `business`, `risk_factors`, `management_discussion`, `notes`
- XBRL financials pulled separately via `filing_obj.financials`
- Text cleaning via `src/utils/text_cleaner.py`

### Internal Documents (`src/ingestion/internal_doc_processor.py`)

- Processes fictional enterprise docs (risk registers, board memos, etc.)
- Each doc type has its own directory under `data/internal/`

## Chunking Layer

### SECChunker (`src/ingestion/chunk_strategies/`)

- Splits SEC sections into ~1000 char chunks with 200 char overlap
- Strategy: paragraph split → sentence split → fixed 500-char blocks
- Maps section names to SEC Item numbers: Item 1, Item 1A, Item 7, Item 8

### Unified Chunk Model

All document sources produce `Chunk` + `ChunkMetadata` objects (defined in `src/ingestion/types.py`).

## Vector Store (`src/retrieval/vector_store.py`)

- Qdrant with LangChain `QdrantVectorStore` wrapper
- Metadata nested under `metadata.` key (LangChain convention)
- Simple dict filters auto-converted: `{"is_public": True}` → `metadata.is_public=True`

Requires Qdrant Docker:
```bash
docker run -d --name nexlify-qdrant -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/data/qdrant:/qdrant/storage qdrant/qdrant
```

## Key Types (`src/ingestion/types.py`)

```python
Chunk           # atomic content unit
ChunkMetadata   # source, category, access level, etc.

DataSourceCategory:
  PUBLIC_SEC | INTERNAL_NEXLIFY

ContentType:
  RISK_FACTORS | FINANCIAL_STATEMENTS | MANAGEMENT_DISCUSSION |
  INTERNAL_POLICY | BOARD_MEMO | RISK_REGISTER | etc.

AccessLevel:
  PUBLIC | INTERNAL | CONFIDENTIAL | STRICTLY_CONFIDENTIAL
```

## Directory Structure

```
src/
  ingestion/      — extraction (SEC, internal) + chunking
  retrieval/     — Qdrant vector store + embeddings
  utils/         — logger (logger.info()), text cleaner

data/
  internal/      — organized by doc type (risk-registers/, board-memos/, etc.)
  qdrant/        — Qdrant storage files

docs/
  adr/           — Architecture Decision Records
  plans/         — feature plans and design docs
```