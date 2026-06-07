# Risk QA Agent

The retrieval-augmented reasoning layer of the NexlifyCorp Knowledge Base.
Decides where to look, how to phrase the search, whether the evidence is
enough, and how to write a grounded answer.

## Language

**Intent**:
The purpose of the user's query, classified by the rewrite node and used
to drive how the query is reformulated for retrieval.
_Avoid_: Query type, query class, classification

**Intent taxonomy** (five values): `factual_lookup`, `comparison`,
`risk_assessment`, `summary`, `explanation`. Each maps to a different
rewrite strategy and retrieval behavior.

**Rewrite**:
The act of reformulating the user's query into one or more optimized
search queries before retrieval. Output is a `RewriteResult` containing
`queries` (always) and `filters` (on retry). The rewrite is intent-aware
and may be feedback-aware on retry.
_Avoid_: Query expansion, query reformulation (too generic)

**Retrieval retry**:
A second (or third) retrieval attempt triggered when the reason node
judges the evidence insufficient. Capped at a retry budget of 3. At
budget exhaustion, the agent returns "I don't know" rather than
synthesizing an ungrounded answer.

**Evidence sufficiency**:
A binary judgment by the reason node: do the retrieved chunks support
a grounded answer to the query? Determined by hard pre-LLM rules
(zero chunks, low relevance) plus a CoT-prompted confidence score
(threshold ≥ 0.7).

**Gap**:
The reason node's free-text explanation of what is missing when it
judges evidence insufficient. Consumed by the retry rewrite as
feedback so the next attempt targets the missing piece.

**Retrieval retry budget**:
The maximum number of corrective retrieval attempts. Currently 3. When
exceeded, the system returns "I don't know" without generating.
