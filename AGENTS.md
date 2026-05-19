# NexlifyCorp Agent

> Agent guidance for NexlifyCorp — AI Financial Analyst Assistant

---

## Project Definition

NexlifyCorp is a hybrid Knowledge Base + Agentic AI system for financial intelligence workflows. It combines real public SEC EDGAR filings with fictional internal documents, progressing through a structured learning path toward production-grade enterprise architecture.

**Tech Stack**: LangChain + LangGraph, Chroma, LangChain-Anthropic (Claude), Neo4j (planned), Streamlit
**Package Manager**: `uv` — run all Python commands via `uv run python`

---

## Directory Structure

```
src/
├── ingestion/          # SEC filing loading & processing
├── retrieval/          # RAG, Hybrid, GraphRAG retrievers
├── agents/             # LangGraph agents & workflows
├── evaluation/         # Ragas, metrics, testing
└── utils/              # Helpers, text cleaning, logging

data/
├── public/             # Real SEC 10-K, 10-Q filings
└── internal/           # Fictional Nexlify Corp documents

docs/                   # Architecture Decision Records
streamlit_app/          # Web UI
notebooks/              # Experiments & daily notes
```

---

## Feature Tracking System

### Files

- **`feature-list.json`** — Canonical feature registry
- **`docs/feature-rules.md`** — Feature tracking rules, schema, and status lifecycle

### Adding a Feature

Before implementing any new functionality, add it to `feature-list.json`:

```json
{
  "id": "feature-name",
  "name": "Feature Name",
  "description": "Brief description of what it does",
  "status": "planned",
  "phase": "1",
  "location": "src/path/",
  "dependencies": ["package"]
}
```

### Marking a Feature as Done

Change `status` to `"implemented"` only when ALL are true:

- Code exists at the specified `location`
- All listed `dependencies` are installed and working
- Feature passes basic validation
- `phase` reflects the actual phase completed

### Status Lifecycle

```
planned → in_progress → implemented
                         └──→ deprecated (if superseded)
```

---

## Tech Stack Rules

| Component        | Technology                              |
|------------------|----------------------------------------|
| Framework        | LangChain + LangGraph                   |
| LLM              | LangChain-Anthropic (Claude via `anthropic` package) |
| Vector Store     | Chroma → Weaviate / Pinecone (planned)  |
| Graph DB         | Neo4j (planned, Day 8+)                 |
| Document Process | Unstructured, pypdf, edgartools         |
| UI              | Streamlit                               |
| Evaluation      | Ragas / LangSmith                        |
| Package Manager  | `uv` (use for ALL Python commands)      |

**Always use `uv run python`** — never plain `python`
**Always use `uv run streamlit`** — never plain `streamlit`

---

## SEC Filing Extraction

### Extractor Flow (`src/ingestion/sec_filing_extractor.py`)

1. Call `set_identity(identity)` before any SEC EDGAR request
2. Use `Company(ticker).get_filings(form="10-K")` to fetch filings
3. Extract via `filing.obj()` to get parsed 10-K object
4. Pull metadata, sections, and XBRL financials separately
5. Clean text with `src/utils/text_cleaner.py` before storage

### Data Types (`src/ingestion/types.py`)

| Model           | Purpose                                    |
|-----------------|--------------------------------------------|
| `SEC10K`        | Complete 10-K/10-Q filing container        |
| `SECMetadata`   | CIK, accession number, auditor, fiscal year |
| `SECSection`    | Named section content + word count         |
| `SECFinancials` | XBRL metrics (revenue, net income, etc.)  |
| `DataSource`    | Enum: `SEC_10K`, `SEC_10Q`                |

### Text Cleaning (`src/utils/text_cleaner.py`)

- Remove box-drawing characters (U+2500-U+257F)
- Strip recurring page footers (e.g., `"Apple Inc. | 2024 Form 10-K | 5"`)
- Normalize non-breaking spaces and tabs
- Remove lines that are only numbers or box-drawing chars

---

## Code Standards

### Python Conventions

- Follow **PEP 8** — formatting via `uv run black`
- Use **type annotations** on all function signatures
- Use **Pydantic** for all data models
- Prefer **immutable patterns** (frozen dataclasses, NamedTuple)
- Use `logging` module — never `print()`

### File Organization

- Small files (< 400 lines, 800 max)
- Organize by feature/domain, not by type
- Extract utilities from large modules
- One class or functional group per file

### Error Handling

- Handle errors explicitly at every level
- Provide user-friendly error messages in UI code
- Log detailed error context in backend code
- Never silently swallow errors

---

## Security Rules

- **Never hardcode secrets** — use environment variables via `.env`
- Validate all user input before processing
- Use parameterized queries for any database operations
- SEC identity string (`set_identity`) must be configurable, not hardcoded
- Error messages must not leak sensitive internal data

---

## Development Workflow

1. **Research first** — check if existing code or library solves 80%+ of the problem before writing new
2. **Add feature to `feature-list.json`** before starting implementation
3. **Write tests first** (pytest, `uv run pytest`)
4. **Keep features small and focused** — one feature per PR
5. **Update `feature-list.json`** status when feature is complete

---

## Evaluation

- Run `uv run pytest` to validate changes
- Use `uv run pytest --cov=src --cov-report=term-missing` for coverage
- Minimum test coverage: 80%

---

## Logging

Use `src/utils/logger.py` for structured logging:

```python
from src.utils.logger import logger

logger.info("Processing started")
logger.error(f"Failed: {e}")
logger.debug(f"Extracted {count} items")
```

---

## Commands

```bash
# Run SEC extractor
uv run python src/ingestion/sec_filing_extractor.py

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Launch Streamlit UI
uv run streamlit run streamlit_app/app.py
```