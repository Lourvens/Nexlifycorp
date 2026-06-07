"""Route node — classify user query into public/internal/both retrieval paths."""
import logging
from functools import lru_cache
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.agents.risk_qa_agent.prompts import ROUTE_SYSTEM_PROMPT, ROUTE_USER_PROMPT
from src.agents.risk_qa_agent.utils import require_human_query
from src.core.llm import get_fast_llm

logger = logging.getLogger(__name__)

RouteKey = Literal["public_only", "internal_only", "both"]


class RouteDecision(BaseModel):
    """Structured routing decision returned by the LLM."""

    route_key: RouteKey = Field(
        description=(
            "Which retrieval path(s) to activate: "
            "'public_only' for SEC filings, 'internal_only' for NexlifyCorp internal "
            "documents, 'both' when the query needs cross-referencing."
        )
    )


@lru_cache(maxsize=1)
def _router():
    """Build a structured-output router. Cached so it's built once per process."""
    return get_fast_llm().with_structured_output(RouteDecision)


def route_node(state: dict) -> dict:
    """Classify the latest user message and set route_key.

    Uses structured output so the LLM is constrained to one of the three
    valid route keys — no string parsing, no fallback needed.
    """
    query = require_human_query(state)

    decision = _router().invoke(
        [
            SystemMessage(content=ROUTE_SYSTEM_PROMPT),
            HumanMessage(content=ROUTE_USER_PROMPT.format(query=query)),
        ]
    )

    route_key: RouteKey = "both"
    if decision is not None and getattr(decision, "route_key", None):
        route_key = decision.route_key
    else:
        logger.warning(
            "Route node: structured output returned no route_key for query=%r — defaulting to both",
            query[:80],
        )

    logger.info("Route node: query=%r → route_key=%r", query[:80], route_key)
    return {"route_key": route_key}
