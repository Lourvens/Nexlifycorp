# TODO: SLM Integration for Cost-Efficient Ontology Enrichment

## Context

Currently, the ontology enrichment step uses `claude-sonnet-4.6` via `ChatAnthropic` for structured output. This provides high quality but at significant cost — each chunk (~500 tokens) costs API credits per call.

With ~1500+ chunks in the vector store and new filings being ingested regularly, the cumulative cost of ontology enrichment using a frontier model is non-trivial.

## Proposal: Switch to Small Language Models (SLMs)

### Why SLMs Work for This Task

Ontology enrichment is a **well-bounded, deterministic extraction task** — not open-ended generation. The LLM is not required to reason deeply or produce creative output. It needs to:

1. Read a ~500-token chunk of SEC/financial text
2. Classify concepts, themes, and departments
3. Output a short, constrained JSON blob

This is exactly the kind of task where smaller models excel:
- The schema is fixed (3 fields, short lists)
- The domain vocabulary is specific but bounded (financial/business terms)
- The output format is strict JSON with no creative freedom needed

### Candidate Models

**HuggingFace-hosted (local, no API cost):**
- `Qwen/Qwen2.5-7B-Instruct` — strong multilingual, good structured output
- `microsoft/Phi-3-mini-4k-instruct` — excellent reasoning-to-size ratio
- `mistralai/Mistral-7B-Instruct-v0.3` — well-tested, good JSON adherence
- `google/gemma-2-9b-it` — efficient, strong on classification tasks

**API-backed (still cheap vs frontier):**
- `anthropic/claude-haiku-4-7` (if available)
- `openai/gpt-4o-mini`
- `google/gemini-1.5-flash`

### Implementation Plan

```
1. Add to src/core/config.py:
   - ontology_model: str = "claude-sonnet-4.6"  # current default
   - ontology_provider: Literal["anthropic", "huggingface", "openai"] = "anthropic"
   - huggingface_endpoint: str | None = None   # for local GGUF serving

2. Add to src/core/llm.py:
   - create_ontology_llm(provider, model, endpoint) factory
   - Support for ChatHuggingFace wrapper from langchain_huggingface
   - Fallback: if huggingface_endpoint set, use local model via API

3. Swap in _get_chain():
   - Use the appropriate LLM based on config
   - Same ChatPromptTemplate | with_structured_output pattern
   - SLMs may need temperature=0.3 for better JSON adherence

4. Cost monitoring:
   - Log token usage per batch (estimate from chunk count)
   - Track enrichment failures vs cost
```

### Tradeoffs to Document

| Aspect | Frontier (Claude Sonnet) | SLM (Qwen 7B) |
|--------|-------------------------|---------------|
| Quality | ★★★★★ | ★★★☆☆ |
| Cost/chunk | ~$0.01-0.02 | ~$0.001 (local) |
| Latency | ~1-2s | ~0.5-1s (GPU) / ~3-5s (CPU) |
| JSON adherence | ★★★★★ | ★★★☆☆ (need prompt tuning) |
| Domain accuracy | ★★★★★ | ★★★☆☆ (may miss nuances) |
| Infrastructure | API only | GPU or local serving |

### Recommendation

Start with `Qwen/Qwen2.5-7B-Instruct` via HuggingFace Inference API (or local GGUF with `llama.cpp`). It's:
- Cheap (~$0.001/chunk at API rates vs $0.01-0.02 for Claude)
- Fast enough for batch enrichment
- Strong enough for the structured extraction task
- Well-supported in langchain_huggingface

Evaluate quality by running enrichment on 50 chunks and comparing concept/theme overlap with Claude-enriched chunks from the same doc.

## Status

**Not started** — awaiting cost profiling and infrastructure decision (local GPU vs API).