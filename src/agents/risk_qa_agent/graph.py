"""LangGraph StateGraph for Risk QA Agent."""
import logging

from langgraph.graph import StateGraph, START, END

from src.agents.risk_qa_agent.state import RiskAgentState
from src.agents.risk_qa_agent.route_node import route_node
from src.agents.risk_qa_agent.retrieve_node import retrieve_node
from src.agents.risk_qa_agent.reason_node import reason_node
from src.agents.risk_qa_agent.generate_node import generate_node

logger = logging.getLogger(__name__)


def build_risk_qa_graph():
    """
    Build and compile the Risk QA Agent StateGraph.

    Graph structure:
        START → route → retrieve → reason → generate → END

    Edges:
        START → route (always)
        route → retrieve (conditional on route_key)
        retrieve → reason (always, after retrieval completes)
        reason → generate (always)
        generate → END (always)

    Args:
        None

    Returns:
        Compiled StateGraph ready for invocation
    """
    builder = StateGraph(RiskAgentState)

    # Add nodes
    builder.add_node("route", route_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("reason", reason_node)
    builder.add_node("generate", generate_node)

    # Define edges
    builder.add_edge(START, "route")
    builder.add_edge("route", "retrieve")
    builder.add_edge("retrieve", "reason")
    builder.add_edge("reason", "generate")
    builder.add_edge("generate", END)

    # Compile
    compiled = builder.compile()

    logger.info("Risk QA graph compiled successfully")
    return compiled


# Singleton graph instance
_risk_qa_graph = None


def get_risk_qa_graph():
    """Get or create the compiled Risk QA graph singleton."""
    global _risk_qa_graph
    if _risk_qa_graph is None:
        _risk_qa_graph = build_risk_qa_graph()
    return _risk_qa_graph