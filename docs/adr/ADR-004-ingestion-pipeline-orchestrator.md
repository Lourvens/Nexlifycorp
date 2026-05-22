# ADR-004: Ingestion Pipeline Orchestrator

**Date**: 2026-05-21
**Status**: proposed
**Context**: The ingestion pipeline components (extractors, chunkers, vector store) exist independently but lack orchestration. Currently, ingesting a document requires manually chaining: extract → chunk → store. We need a unified pipeline that automates this flow.

## Decision

Implement `ingestion_pipeline.py` as the orchestration layer in `src/ingestion/`, replacing the current `chunk_builder.py` stub.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 IngestionPipeline                           │
├─────────────────────────────────────────────────────────────┤
│  process_sec_filing(ticker, year?) → list[Chunk]           │
│  process_internal_doc(doc_id, doc_type, content) → Chunks │
│  ingest_to_vector_store(chunks) → count                     │
│  ingest_sec_filing(ticker, year?) → count  (full pipeline)│
│  ingest_internal_doc(...) → count      (full pipeline)    │
└─────────────────────────────────────────────────────────────┘
```

### Naming Change

- `src/ingestion/chunk_builder.py` → `src/ingestion/ingestion_pipeline.py`
- Module docstring updated to reflect orchestrator role

### Pipeline Methods

| Method | Purpose |
|--------|---------|
| `process_sec_filing()` | Extract 10-K → chunk → return Chunks (no store) |
| `process_internal_doc()` | Parse markdown → chunk → return Chunks |
| `ingest_sec_filing()` | Full pipeline: Extract → Chunk → Store → return count |
| `ingest_internal_doc()` | Full pipeline: Parse → Chunk → Store → return count |

### Embedding Integration

Embeddings occur **inside VectorStore.add_chunks()** — no separate embedding step:
- `Chunk.content` is embedded via `LocalEmbeddingFunction`
- Metadata stored in Qdrant payload
- No embedding code needed in pipeline

## Consequences

- **Positive**: Single entry point for ingestion; testable in isolation; clean separation of "process" (no side effects) vs "ingest" (stores)
- **Negative**: Adds another layer; potential over-abstraction if only one caller
- **Neutral**: Does not affect existing chunker/extractor interfaces (they remain unchanged)

## Alternatives Considered

1. **Extend VectorStore with ingest methods** — Rejected: VectorStore should only handle storage, not extraction logic
2. **Keep manual chaining** — Rejected: Error-prone, forces callers to know the full pipeline steps
3. **Separate pipeline package** — Rejected: Over-engineering; a single module is sufficient for now

## Implementation Notes

- Reuse existing `SECChunker` and `InternalChunker` directly
- `VectorStore` injected as dependency (enables mocking)
- Factory function `create_ingestion_pipeline()` for consistency with VectorStore pattern
- Tests: unit tests with mocked VectorStore, integration tests with real Qdrant