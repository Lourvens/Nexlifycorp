"""Route node — Haiku classifier for query routing."""
import logging

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from src.core.llm import get_fast_llm
from src.agents.risk_qa_agent.prompts import ROUTE_SYSTEM_PROMPT, ROUTE_USER_PROMPT

logger = logging.getLogger(__name__)


# Combined prompt: system message + user query template
ROUTE_PROMPT = PromptTemplate.from_template(
    ROUTE_SYSTEM_PROMPT + "\n\n" + ROUTE_USER_PROMPT
)


def build_route_chain():
    """Build the route chain: prompt template → Haiku → route_key string."""
    fast_llm = get_fast_llm()
    return ROUTE_PROMPT | fast_llm | StrOutputParser()


def route_node(state: dict) -> dict:
    """
    Classify the user's query and set route_key in state.

    Uses Haiku to analyze the query and determine which retrieval
    path(s) to activate: public_only, internal_only, or both.

    Args:
        state: AgentState with messages[-1] containing the user query

    Returns:
        dict with route_key set
    """
    # Get the latest user message
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No messages in state — cannot route empty query")

    # Find the last human message
    human_msgs = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    if not human_msgs:
        raise ValueError("No HumanMessage found in state")

    query = human_msgs[-1].content

    # Build and invoke the chain
    chain = build_route_chain()
    route_key_raw = chain.invoke({"query": query}).strip().lower()

    # Validate the route key
    valid_routes = {"public_only", "internal_only", "both"}
    if route_key_raw not in valid_routes:
        logger.warning(f"Invalid route_key '{route_key_raw}' — defaulting to 'both'")
        route_key = "both"
    else:
        route_key = route_key_raw

    logger.info(f"Route node: query='{query[:80]}...' → route_key='{route_key}'")

    return {"route_key": route_key}