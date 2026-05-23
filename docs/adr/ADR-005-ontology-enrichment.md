# ADR-005: Ontology Enrichment Layer

**Date**: 2026-05-22
**Status**: accepted
**Context**: The ingestion pipeline produces `ChunkMetadata` with content_type, access_level, and topics, but retrieval relies purely on vector similarity. Two problems: **synonymy** (semantically similar terms have distant vectors) and **strategic context** (a query about "Q3 performance" should boost financial docs, but vector search has no concept of this).

## Decision

Add a pluggable **ontology enrichment step** to the ingestion pipeline that uses Claude structured output to analyze each chunk's content and inject semantic metadata:

- `concepts: list[str]` — key business/financial concepts (e.g., "revenue", "margin expansion", "AI investment")
- `strategic_themes: list[str]` — strategic themes (e.g., "growth", "cost efficiency", "regulatory compliance")
- `departments: list[str]` — relevant departments (e.g., "finance", "engineering", "legal")

### Architecture

```
Pipeline Flow (per document):
Extract → Chunk → Embed → Store → [Ontology Enrichment]
                              ↑                    ↑
                         vector stored      retry only metadata
                         (no re-embed)       via Qdrant set_payload
```

**Key design decisions:**

1. **Per-chunk analysis** — Each ~512-token chunk is analyzed individually by the LLM for maximum granularity
2. **Plug/unplug via flag** — `enable_ontology=True` in `create_ingestion_pipeline()`; no code changes needed to disable
3. **Fail-open** — If LLM call fails, the chunk continues through the pipeline with empty ontology fields and `ontology_enrichment_failed=True`
4. **No re-embed on retry** — Qdrant `set_payload` updates only metadata, not the vector
5. **Idempotent** — Re-running produces the same result, safe for retries

### Structured Output

Using `langchain_anthropic.ChatAnthropic.with_structured_output(OntologySchema)` with `temperature=0`:

```python
class OntologySchema(BaseModel):
    concepts: list[str]
    strategic_themes: list[str]
    departments: list[str]
```

### New Fields in ChunkMetadata

```python
class ChunkMetadata(BaseModel):
    # ... existing fields ...
    concepts: list[str] = []
    strategic_themes: list[str] = []
    departments: list[str] = []
    ontology_enrichment_failed: bool = False
```

## Consequences

- **Positive**: Rich semantic metadata for retrieval boosting; fail-open design; LLM-only retry costs
- **Negative**: Additional LLM latency during ingestion; added cost per chunk; increases Qdrant payload size
- **Neutral**: Metadata is advisory — retrieval logic must be updated separately to actually use the ontology fields for boosting

## Alternatives Considered

1. **Query-time analysis only** — Rejected: Would require LLM call on every search, higher latency at retrieval
2. **Document-level analysis** — Rejected: Less granular; a 50-page 10-K would lose per-section nuance
3. **Fixed taxonomy** — Rejected: Limiting; emergent concepts in filings (e.g., new AI risks) can't be captured
4. **Required enrichment** — Rejected: Would make the pipeline brittle; fail-open ensures core ingestion always works

## Pre-Implementation Steps

1. Add `ontology-enrichment` feature to `feature-list.json`
2. Create `src/ingestion/ontology_enricher.py` with `OntologySchema` and `OntologyEnrichmentStep`
3. Update `src/ingestion/ingestion_pipeline.py` factory with `enable_ontology` flag
4. Update `src/ingestion/types.py` to add ontology fields to `ChunkMetadata`
5. Create `scripts/test_ontology.py` for testing

## Implementation Notes

- Reuse `get_llm()` from `src.core.llm` (singleton ChatAnthropic)
- Content capped at 4000 tokens per LLM call (chunk.content[:4000])
- Retry: 2x with exponential backoff, then skip and set `ontology_enrichment_failed=True`
- Qdrant payload update via `set_payload` on retry (no re-embed)