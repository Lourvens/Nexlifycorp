# CLAUDE.md

Project guidance for Claude Code. See `docs/[topic].md` for detailed references.

---

## TASK PROGRESSION

Track long-running multi-agent tasks in `PROGRESSION.md`.
See `docs/progression-rules.md` for format and status definitions.
Status: `pending` → `in_progress` → `blocked`/`completed`/`stuck`

---

## FEATURE TRACKING

Add new features to `feature-list.json` before implementing.
Status lifecycle: `planned` → `in_progress` → `implemented` → `deprecated`
See `docs/feature-rules.md` for details.

---

## PROJECT OVERVIEW

NexlifyCorp — hybrid KB + Agentic AI combining SEC EDGAR filings with internal enterprise docs for financial intelligence. LangChain + LangGraph, Qdrant vector store, Claude.

---

## PACKAGE MANAGER

Always use `uv`: `uv run python`, `uv run pytest`.

---

## COMMANDS

```bash
uv run pytest                    # all tests
uv run pytest tests/unit/...     # single file
uv run pytest --cov=src          # with coverage
```

---

## ARCHITECTURE

Data flow: SEC/Internal → Extractors → Chunkers → VectorStore → Retrieval
See `docs/architecture.md` for full details.

### Key Types (`src/ingestion/types.py`)
`Chunk` + `ChunkMetadata` — unified document unit
`DataSourceCategory`: `PUBLIC_SEC` | `INTERNAL_NEXLIFY`
`ContentType`: `RISK_FACTORS`, `FINANCIAL_STATEMENTS`, `MANAGEMENT_DISCUSSION`, etc.
`AccessLevel`: `PUBLIC` | `INTERNAL` | `CONFIDENTIAL` | `STRICTLY_CONFIDENTIAL`

### Directory Structure
- `src/ingestion/` — extraction + chunking
- `src/retrieval/` — Qdrant vector store
- `src/utils/` — logger, text cleaner
- `data/internal/` — by doc type
- `docs/adr/` — Architecture Decision Records

## ARCHITECTURE

Data flow: SEC/Internal → Extractors → Chunkers → VectorStore → Retrieval
See `docs/architecture.md` for full details.

### Key Types (`src/ingestion/types.py`)
`Chunk` + `ChunkMetadata` — unified document unit
`DataSourceCategory`: `PUBLIC_SEC` | `INTERNAL_NEXLIFY`
`ContentType`: `RISK_FACTORS`, `FINANCIAL_STATEMENTS`, `MANAGEMENT_DISCUSSION`, etc.
`AccessLevel`: `PUBLIC` | `INTERNAL` | `CONFIDENTIAL` | `STRICTLY_CONFIDENTIAL`

### Directory Structure
- `src/ingestion/` — extraction + chunking
- `src/retrieval/` — Qdrant vector store
- `src/utils/` — logger, text cleaner
- `data/internal/` — by doc type
- `docs/adr/` — Architecture Decision Records

### Vector Store
Requires Qdrant Docker: `docker run -d --name nexlify-qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/data/qdrant:/qdrant/storage qdrant/qdrant`

### ADR

When a feature needs its own architecture, create an ADR first.
See `docs/adr-rules.md` for format and when to write an ADR.
Save to `docs/adr/ADR-XXX-short-title.md`.

---

## TESTING

pytest config in `pytest.ini`: markers (`unit`, `integration`, `slow`), min version 7.0, `pythonpath = .`
Fixtures in `tests/conftest.py`: `test_data_dir`, `sample_markdown_content`, `sample_risk_register_content`, etc.

---