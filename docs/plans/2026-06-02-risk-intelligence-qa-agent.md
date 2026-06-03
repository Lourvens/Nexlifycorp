# Risk Intelligence QA Agent — Implementation Plan

**Date:** 2026-06-02
**Status:** Draft
**Phase:** 1 (foundational)

---

## Overview

Build a LangGraph-powered QA agent that answers natural language questions about NexlifyCorp's risk landscape, grounded in the knowledge base with explicit source citations. The agent routes queries to the correct retrieval path(s) (public SEC filings vs. internal NexlifyCorp documents), retrieves evidence, reasons over the evidence, and generates cited answers.

**Key principle:** Public and internal documents are **never mixed** at retrieval. The agent maintains strict separation via `source_category` (`PUBLIC_SEC` vs `INTERNAL_NEXLIFY`) and access-level enforcement via `forced_access_level`.

---

## Data Scope — Phase 1

### Internal KB (INTERNAL_NEXLIFY)
| Category | Documents |
|----------|-----------|
| `risk-registers/` | Q2 2025 Internal Risk Register, Cybersecurity Incident Report |
| `supply-chain/` | Supply Chain Risk Assessment (geopolitical + capacity) |
| `competitor-analyses/` | NVIDIA & AMD Competitive Analysis |

### Public KB (PUBLIC_SEC)
| Category | Documents |
|----------|-----------|
| SEC 10-K / 10-Q | Risk factors, MD&A, financial statements from NexlifyCorp and key competitors (NVDA, AMD) |

### Deferred to Phase 2
- `board-memos/`, `financial-reviews/` — CONFIDENTIAL tier (role-based access)
- `hr-policies/`, `product-specs/`, `policies/` — out of scope for risk intelligence

---

## Architecture

### Agent Graph (LangGraph StateGraph)

```
                        ┌─────────────┐
                        │    start    │
                        └──────┬──────┘
                               ▼
                        ┌─────────────┐
                        │    route    │  Haiku classifier
                        │  (fast_llm) │  Sets route_key in state
                        └──────┬──────┘
                               ▼
                    ┌──────────┴──────────┐
                    │                     │
           route_key =               route_key =
           "internal_only"        "public_only"
                    │                     │
                    ▼                     ▼
           ┌───────────────┐     ┌───────────────┐
           │   retrieve    │     │   retrieve    │
           │ (private tool)│     │ (public tool) │
           └───────┬───────┘     └───────┬───────┘
                   │                     │
                   │      route_key = "both"
                   │           │
                   │    ┌─────┴─────┐
                   │    ▼           ▼
                   │  ┌─────────┐ ┌─────────┐
                   │  │priv_tool│ │pub_tool │
                   │  └────┬────┘ └────┬────┘
                   │       │           │
                   └───────┼───────────┘
                           ▼
                   ┌───────────────┐
                   │    reason    │  Analyzes chunks
                   │ (main_llm)    │  Detects conflicts
                   └───────┬───────┘
                           ▼
                   ┌───────────────┐
                   │   generate    │  Produces final
                   │  (main_llm)   │  cited answer
                   └───────┬───────┘
                           ▼
                        ┌─────────────┐
                        │     end     │
                        └─────────────┘
```

### Agent State (`AgentState`)

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]  # conversation history
    route_key: str                                        # "public_only" | "internal_only" | "both"
    retrieved_chunks: list[dict]                          # unified chunk records from both paths
    reasoning_trace: str                                  # output of the reason node
    citations: list[Citation]                             # structured citation metadata
```

### Node Responsibilities

| Node | Input | Output | LLM Used |
|------|-------|--------|----------|
| `route` | `state.messages[-1].content` (user query) | Sets `state.route_key` | `fast_llm` (Haiku) |
| `retrieve` | `state.route_key` | Populates `state.retrieved_chunks` | Tool calls (no LLM) |
| `reason` | `state.retrieved_chunks` + query | `state.reasoning_trace` + `state.citations` | `main_llm` (Sonnet) |
| `generate` | `state.reasoning_trace` + `state.citations` + query | Final answer (appended to `state.messages`) | `main_llm` (Sonnet) |

### Dual-Path Retrieval

The `retrieve` node uses the existing `create_public_retriever_tool` and `create_private_retriever_tool` factories from `src/agents/tools.py`:

```
query → route (Haiku) → route_key
                          ├── "public_only"  → retrieve_public_documents
                          ├── "internal_only" → retrieve_private_documents
                          └── "both"          → both in parallel
```

Filters used in Phase 1:
- `content_type` — risk_factors, financial_statements, management_discussion
- `tickers` — NVDA, AMD (for public SEC filings)
- `date_from` / `date_to` — recency filtering
- `k` — default 10, adjustable

### Haiku Fast Classifier

Create `src/core/llm.py` additions:
```python
def create_fast_llm(...) -> ChatAnthropic
def get_fast_llm(...) -> ChatAnthropic  # singleton
```

Config: `Settings.anthropic_fast_model = "claude-haiku-4.5"` (default). Model name inherits from same config factory as the main LLM — same `create_llm` / `get_llm` pattern but with a dedicated fast model.

### Two-Pass Synthesis

**Pass 1 (reason):** Reads all retrieved chunks, produces:
- Per-source narrative (what each chunk contributed)
- Conflict detection (internal vs public contradictions explicitly flagged)
- Confidence level per finding

**Pass 2 (generate):** Takes reasoning trace + citations → produces final answer with:
- Inline numbered footnote citations (e.g., `¹`)
- Footnotes: document title, date, classification badge (`[PUBLIC]` / `[INTERNAL]`)
- Visible "Reasoning Trace" expandable section below the answer

---

## Citation Format

### Inline (in answer text)
```
The Taiwan CoWoS dependency is the highest-probability, highest-impact risk (CRITICAL, score 9.0/10)¹
```

### Footnote
```
[1] NCR-2025-Q2-001 — 2025-Q2-Internal-Risk-Register.md (May 17, 2025) [INTERNAL]
    Excerpt: "78% of our advanced packaging (CoWoS) supply flows through TSMC facilities in Taiwan"
```

### Reasoning Trace (expandable)
```
REASONING TRACE
━━━━━━━━━━━━━━
Source 1 [INTERNAL]: NCR-2025-Q2-001 — Internal Risk Register
  → Nexlify's Taiwan CoWoS dependency: 78%
  → Risk score: 9.0/10 (CRITICAL)

Source 2 [PUBLIC]: NVDA 10-K 2024 — SEC EDGAR
  → NVIDIA discloses Taiwan as primary manufacturing location
  → NVIDIA does NOT quantify customer-specific supply chain exposure

CONFLICT DETECTED: Internal assessment (78% CoWoS dependency) vs public
disclosure (no customer-specific quantification). NVIDIA's public risk
factors are aggregated at product line level.

Final Answer: [generated answer with inline citations]
```

---

## Implementation Phases

### Phase 1 — Core Infrastructure
1. Add `anthropic_fast_model` config field to `src/core/config.py`
2. Add `create_fast_llm` / `get_fast_llm` factory to `src/core/llm.py` (inherits same pattern as `create_llm`)
3. Define `AgentState` in `src/agents/risk_agent/state.py`
4. Build `route` node — Haiku classifier that sets `route_key` from query text
5. Build `retrieve` node — dispatches to correct retriever(s) based on `route_key`
6. Build `reason` node — two-pass synthesis (analyze chunks → structured reasoning)
7. Build `generate` node — citation-aware answer generation
8. Build LangGraph `StateGraph` in `src/agents/risk_agent/graph.py`
9. Write unit tests for each node (route, retrieve, reason, generate)

### Phase 2 — Enhancements
- Role-based access filtering (INTERNAL vs CONFIDENTIAL vs STRICTLY_CONFIDENTIAL)
- Add `board-memos/` and `financial-reviews/` internal categories
- Reranking / quality scoring of retrieved chunks
- Streaming UX (via LangGraph server)

### Phase 3 — Scale
- Iterative retrieval (agent can refine query and call retriever again)
- Cross-competitor comparison reports (auto-generated from both paths)
- Evaluation harness (RAGAs metrics)

---

## File Structure

```
src/agents/risk_agent/
├── __init__.py
├── state.py          # AgentState definition
├── graph.py          # StateGraph construction + nodes
├── route_node.py     # Haiku classifier node
├── retrieve_node.py  # Dual-path retrieval node
├── reason_node.py    # Two-pass synthesis node
├── generate_node.py  # Citation-aware generation node
└── prompts.py         # System prompts for route/reason/generate

src/core/
├── llm.py            # Add create_fast_llm / get_fast_llm
├── config.py         # Add anthropic_fast_model field
```

---

## Configuration

```python
# src/core/config.py
anthropic_model: str = "claude-sonnet-4.6"       # main LLM for generate/reason
anthropic_fast_model: str = "claude-haiku-4.5"  # fast classifier for route
```

---

## Dependencies

- `src/agents/tools.py` — existing `create_public_retriever_tool` / `create_private_retriever_tool`
- `src/ingestion/types.py` — `DataSourceCategory`, `AccessLevel`, `ChunkMetadata`
- `src/retrieval/` — existing `FilterCriteria`, vector store retrieval
- `src/core/llm.py` — extend with fast LLM factory
- `src/core/config.py` — extend with fast model config

---

## Test Scenarios

| Query | Expected route_key | Expected sources |
|-------|-------------------|-----------------|
| "What is our supply concentration risk?" | `internal_only` | risk-register, supply-chain |
| "How are NVIDIA and AMD disclosing geopolitical risk?" | `public_only` | NVDA + AMD 10-Ks |
| "How does our risk compare to industry peers?" | `both` | internal risk register + public SEC filings |
| "What are the key risk factors in our latest 10-K?" | `public_only` | NexlifyCorp 10-K |
| "Any new supply chain risks in the last 6 months?" | `internal_only` | recent supply-chain docs |

---

## Out of Scope (Phase 1)

- User authentication / session management (handled by LangGraph server)
- Role-based access filtering (Phase 2)
- Streaming output (LangGraph server handles UX)
- Iterative retrieval refinement
- RAG evaluation (Phase 3)
- Multi-turn conversation memory (future: chat history in state)