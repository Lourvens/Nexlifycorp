# TODO: SLM Integration for Ontology Enrichment

## Context

Currently, the ontology enrichment step uses a frontier model for structured output. This provides high quality but a smaller or medium language model could achieve acceptable results for this bounded extraction task — identifying concepts, themes, and departments from financial text chunks.

Ontology enrichment is a **well-bounded, deterministic extraction task** — not open-ended generation. The model needs to:
1. Read a ~500-token chunk of SEC/financial text
2. Classify concepts, themes, and departments
3. Output a constrained JSON blob

This is exactly the kind of task where smaller models can excel.

## Implementation Plan

```
1. Add to src/core/config.py:
   - ontology_model: str = current frontier model default
   - ontology_provider: str = "anthropic"  # swappable provider
   - huggingface_model: str | None = None   # for HF-hosted models

2. Add to src/core/llm.py:
   - Support multiple providers (Anthropic, HuggingFace, etc.)
   - Factory function that returns the appropriate LLM adapter

3. Update _get_chain() in ontology_enricher.py:
   - Use the configured provider/model
   - Same ChatPromptTemplate | with_structured_output pattern
   - Tune temperature/prompts per model as needed

4. Evaluation:
   - Compare small/medium model output quality against frontier
   - Validate JSON adherence and domain accuracy
   - Ensure fail-open behavior is preserved
```

## Why Small/Medium Models Are Sufficient

| Aspect | Frontier | Small/Medium LM |
|--------|----------|-----------------|
| JSON adherence | High | Moderate-High (with tuning) |
| Domain accuracy | High | Acceptable for bounded task |
| Latency | Fast | Comparable or faster |
| Task complexity | Overkill | Well-matched |

The extraction task is constrained: fixed schema, specific domain vocabulary, short outputs. A frontier model's broad reasoning capabilities add less value here than they would in open-ended tasks.

## Status

**Not started** — awaiting evaluation and provider decision.