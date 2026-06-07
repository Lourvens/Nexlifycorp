# ADR-006: Corrective-RAG Loop with Evidence Sufficiency Contract

**Status**: Accepted | Date: 2026-06-07

The Risk QA Agent now includes a self-correcting retrieval loop. When the reason
node judges the retrieved evidence insufficient, control flows back to the
rewrite node with the previous attempt's chunks and the reason's gap
description as feedback. The cycle is bounded by a 3-attempt budget; at
exhaustion, the agent returns "I don't know" rather than synthesizing an
ungrounded answer.

## Why this shape

The agent's whole pitch is evidence-backed answers with citations. A
single-shot retrieve-then-answer pipeline fails when the first retrieval
misses — either zero chunks, low-relevance chunks, or chunks that are
topically adjacent but don't actually answer the question. Letting the
LLM push back on its own evidence, and giving the retriever a second
chance to target the gap, is the simplest way to recover.

The system is intentionally *not* multi-hop (decompose the question
into sub-questions, answer each, then synthesize) and *not* iterative
refinement of the answer. The loop is purely on the *evidence
acquisition* step. The reasoning and generation steps run exactly once
on the final chunk set.

## Contract between reason and the retry rewrite

The reason node returns a structured judgment:

- `evidence_sufficient: bool` — `True` if the chunks answer the question
- `evidence_gap: str` — one-sentence description of what is missing
  (consumed by the retry rewrite as feedback; discarded if no retry)
- `evidence_confidence: float` — 0.0–1.0 self-rated confidence that the
  chunks fully answer the question

The retry rewrite receives the gap and the rejected chunks, and
produces new queries and (on retry) optional filters. We do not gate
retry on `confidence` < some threshold *in addition to* a non-empty
`gap` — we trust the score. A 0.9 confidence with a non-empty gap
means the LLM was being polite about an edge case; proceed to generate.

## Hard pre-LLM rules

Two cases force a retry before the LLM is even called:

1. `len(retrieved_chunks) == 0` — nothing retrieved, retry is mandatory
2. Best relevance score < 0.30 — chunks present but irrelevant, retry is mandatory

These are deterministic, free of LLM judgment, and cover the most
common failure modes without burning an LLM call.

## Considered alternatives

**Multi-hop decomposition in the rewrite.** Rejected: the comparison
intent already does per-entity decomposition. A full multi-hop
planner would handle "compare A and B against our internal assessment",
but that's better expressed as a `comparison` intent with two queries
than as a separate planning step.

**Confidence threshold < 0.7 = retry.** 0.7 was chosen empirically
because lower values (e.g., 0.5) caused the loop to over-fire on
genuinely-sufficient evidence, and higher values (e.g., 0.9) caused
the loop to under-fire on borderline evidence. 0.7 is a documented
constant in the reason prompt and can be tuned later based on eval data.

**"I don't know" at max retries vs. best-effort with caveat.** We
chose "I don't know". Adding a caveat preserves the user experience of
getting an answer, but if the LLM was honest about insufficiency three
times in a row, the answer *is* "I don't know" — caveat or not. A
silent best-effort answer in a system whose pitch is grounded answers
is the worst option: it erodes trust faster than a refusal does.

## Consequences

- **Cost**: up to 4× the reason-node LLM calls per question (3
  retries × 1 reason). Each reason call is Sonnet. Acceptable for a
  risk-intelligence tool used by analysts; not acceptable for a
  high-throughput consumer chatbot. The retry budget is a tuning knob.
- **Latency**: up to 4× the worst-case latency. The hard pre-LLM
  rules mitigate this for the most common failure mode (zero chunks).
- **State growth**: `previous_chunks` accumulates per attempt. Capped
  implicitly by the retry budget (max 3 lists of chunks, each ≤ k=10).
  The generate node merges and dedupes across all attempts at the end.
- **Test impact**: the graph is no longer a DAG. Existing tests that
  assume a linear flow need conditional-edge awareness. The graph
  builder exposes the same `get_risk_qa_graph()` singleton, so callers
  are unaffected.
