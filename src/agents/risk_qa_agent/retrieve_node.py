"""Retrieve node — fire Retriever per query, merge and dedupe by chunk id.

Reads:
- route_key (existing): which access levels to search
- rewrite_queries (new, from rewrite_node): one or more search queries
- rewrite_filters (new, from rewrite_node): optional narrow filters (content_types,
  tickers, date_from, date_to, sec_form — never access_level or source_category)

Writes:
- retrieved_chunks: current attempt's chunks with relevance scores
- previous_chunks: appends the previous attempt's chunks before overwriting
"""
import logging
from datetime import datetime, date

from langchain_core.documents import Document

from src.agents.risk_qa_agent.utils import last_user_query
from src.ingestion.types import AccessLevel, ContentType
from src.retrieval import FilterCriteria, Retriever

logger = logging.getLogger(__name__)


ROUTE_TO_ACCESS_LEVELS: dict[str, list[AccessLevel]] = {
    "public_only": [AccessLevel.PUBLIC],
    "internal_only": [AccessLevel.INTERNAL],
    "both": [AccessLevel.PUBLIC, AccessLevel.INTERNAL],
}

# Keys the rewrite is allowed to set in its filters. access_level and
# source_category are route_key's job and would conflate the layers.
REWRITE_FILTER_KEYS = ("content_types", "tickers", "date_from", "date_to", "sec_form")


def _coerce_content_types(values) -> list[ContentType] | None:
    """Coerce a list of strings to ContentType enums. Drops invalid values
    with a warning rather than crashing — a bad rewrite shouldn't kill the
    retrieval."""
    if not values:
        return None
    valid_values = [v.value if hasattr(v, "value") else str(v) for v in values]
    valid_enum_values = {ct.value for ct in ContentType}
    coerced: list[ContentType] = []
    for raw in valid_values:
        normalized = str(raw).strip().lower()
        if normalized in valid_enum_values:
            coerced.append(ContentType(normalized))
        else:
            logger.warning(
                "Dropping invalid content_types value %r — not a ContentType. "
                "Did the rewrite mean sec_form=%r?",
                raw, raw,
            )
    return coerced or None


def _coerce_sec_form(value) -> str | None:
    """Coerce a sec_form string. Accepts '10-K', '10-Q', '8-K' (case-insensitive)."""
    if value is None:
        return None
    raw = value.value if hasattr(value, "value") else str(value)
    normalized = raw.strip().upper()
    if normalized in {"10-K", "10-Q", "8-K"}:
        return normalized
    logger.warning("Dropping invalid sec_form value %r — must be 10-K, 10-Q, or 8-K", raw)
    return None


def _coerce_date(value) -> datetime | None:
    """Coerce a date-ish value to datetime. Accepts:
    - datetime: returned as-is
    - date: promoted to midnight datetime
    - ISO format string (YYYY-MM-DD or full ISO): parsed
    - None: returns None
    - Anything else: dropped with a warning.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            logger.warning("Dropping invalid date value %r — expected ISO format YYYY-MM-DD", value)
            return None
    logger.warning("Dropping invalid date value %r of type %s", value, type(value).__name__)
    return None


def _doc_to_chunk(doc: Document, index: int, score: float) -> dict:
    """Coerce a Document + its metadata + relevance score into a chunk dict.

    Metadata values may be lists (Qdrant returns multi-value fields like
    ticker/content_type as lists). We join them to strings so downstream
    .format() and template substitution don't break.
    """
    m = doc.metadata

    def as_str(key: str, default: str = "") -> str:
        v = m.get(key)
        if v is None:
            return default
        if isinstance(v, list):
            return ", ".join(str(x) for x in v) if v else default
        return str(v)

    return {
        "chunk_index": index,
        "content": doc.page_content or "",
        "document_id": as_str("document_id") or as_str("id") or f"doc-{index}",
        "document_title": as_str("source_detail", "Unknown Document"),
        "source_category": as_str("source_category", "unknown"),
        "access_level": as_str("access_level", "unknown"),
        "document_date": as_str("document_date") or None,
        "ticker": as_str("ticker") or None,
        "content_type": as_str("content_type") or None,
        "relevance_score": score,
    }


def _build_criteria(route_key: str, rewrite_filters: dict) -> FilterCriteria:
    """Build a FilterCriteria from route_key (access_level) and rewrite_filters
    (content_types, tickers, date_from, date_to, sec_form).

    Coerces string values to enums defensively — the rewrite is an LLM and
    can produce wrong-shaped values. Invalid values are dropped with a warning
    rather than crashing the graph.
    """
    access_levels = ROUTE_TO_ACCESS_LEVELS[route_key]
    if len(access_levels) == 1:
        criteria = FilterCriteria(access_level=access_levels[0])
    else:
        # "both" — leave access_level unset so we don't filter; the per-level
        # loop in retrieve_node handles it.
        criteria = FilterCriteria()

    if rewrite_filters:
        if "content_types" in rewrite_filters and rewrite_filters["content_types"] is not None:
            criteria.content_types = _coerce_content_types(rewrite_filters["content_types"])
        if "tickers" in rewrite_filters and rewrite_filters["tickers"] is not None:
            tickers = rewrite_filters["tickers"]
            if isinstance(tickers, str):
                tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
            criteria.tickers = [str(t).strip().upper() for t in tickers] or None
        for date_key in ("date_from", "date_to"):
            if date_key in rewrite_filters and rewrite_filters[date_key] is not None:
                coerced = _coerce_date(rewrite_filters[date_key])
                if coerced is not None:
                    setattr(criteria, date_key, coerced)
        if "sec_form" in rewrite_filters and rewrite_filters["sec_form"] is not None:
            criteria.sec_form = _coerce_sec_form(rewrite_filters["sec_form"])

    return criteria


def retrieve_node(state: dict) -> dict:
    """Dispatch retrieval per query × access level. Replace retrieved_chunks;
    append the previous chunks to previous_chunks."""
    route_key = state.get("route_key")
    if not route_key:
        raise ValueError("route_key not set in state — run route node first")
    if route_key not in ROUTE_TO_ACCESS_LEVELS:
        raise ValueError(
            f"Unknown route_key {route_key!r} — must be one of {list(ROUTE_TO_ACCESS_LEVELS)}"
        )

    queries = state.get("rewrite_queries") or [last_user_query(state)]
    rewrite_filters = state.get("rewrite_filters") or {}
    previous_attempt_chunks = state.get("retrieved_chunks") or []
    previous_chunks = list(state.get("previous_chunks") or [])

    # Stash the previous attempt's chunks before we overwrite retrieved_chunks.
    # At max attempts, generate_node merges previous_chunks + retrieved_chunks.
    if previous_attempt_chunks:
        previous_chunks.append(previous_attempt_chunks)

    query_label = queries[0][:50] if queries else "<empty>"
    logger.info(
        "Retrieve node: route_key=%r, queries=%d, rewrite_filters=%s, query=%r",
        route_key, len(queries), bool(rewrite_filters), query_label,
    )

    retriever = Retriever()
    criteria = _build_criteria(route_key, rewrite_filters)
    access_levels = ROUTE_TO_ACCESS_LEVELS[route_key]

    retrieved_chunks: list[dict] = []
    chunk_counter = 0

    for level in access_levels:
        # If criteria has its own access_level (single-level route), use as-is.
        # Otherwise inject this level.
        level_criteria = criteria
        if criteria.access_level is None:
            level_criteria = FilterCriteria(
                access_level=level,
                content_types=criteria.content_types,
                tickers=criteria.tickers,
                date_from=criteria.date_from,
                date_to=criteria.date_to,
                sec_form=criteria.sec_form,
            )
        for query in queries:
            results = retriever.retrieve_with_scores(query=query, k=10, criteria=level_criteria)
            for doc, score in results:
                retrieved_chunks.append(_doc_to_chunk(doc, chunk_counter, score))
                chunk_counter += 1
        logger.info("  → %s retrieval: %d chunks total", level.value, len(retrieved_chunks))

    logger.info("Retrieve node: %d chunks retrieved (attempt=%d)",
                len(retrieved_chunks), state.get("retrieval_attempts", 0))

    return {
        "retrieved_chunks": retrieved_chunks,
        "previous_chunks": previous_chunks,
    }
