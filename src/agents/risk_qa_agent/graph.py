"""LangGraph StateGraph for Risk QA Agent.

Graph structure (with corrective-RAG loop per ADR-006):

    START → route → rewrite → retrieve → reason → ┬─→ generate → END
                                                  └─→ rewrite (loop)
                                                       ↑
                                                       └── reason re-judges

The loop fires when reason_node returns evidence_sufficient=False AND
retrieval_attempts < MAX_ATTEMPTS. At max attempts, the agent proceeds to
generate which returns "I don't know" if evidence is still insufficient.
"""
import logging

from langgraph.graph import END, START, StateGraph

from src.agents.risk_qa_agent.generate_node import MAX_ATTEMPTS, generate_node
from src.agents.risk_qa_agent.reason_node import reason_node
from src.agents.risk_qa_agent.retrieve_node import retrieve_node
from src.agents.risk_qa_agent.rewrite_node import rewrite_node
from src.agents.risk_qa_agent.route_node import route_node
from src.agents.risk_qa_agent.state import RiskAgentState

logger = logging.getLogger(__name__)


def _after_reason(state: dict) -> str:
    """Decide whether to proceed to generate or loop back to rewrite."""
    sufficient = state.get("evidence_sufficient", False)
    attempts = state.get("retrieval_attempts", 0)
    if sufficient or attempts >= MAX_ATTEMPTS:
        return "generate"
    return "rewrite"


def build_risk_qa_graph():
    """Build and compile the Risk QA Agent StateGraph with the corrective-RAG loop."""
    builder = StateGraph(RiskAgentState)

    builder.add_node("route", route_node)
    builder.add_node("rewrite", rewrite_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("reason", reason_node)
    builder.add_node("generate", generate_node)

    builder.add_edge(START, "route")
    builder.add_edge("route", "rewrite")
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("retrieve", "reason")
    builder.add_conditional_edges(
        "reason",
        _after_reason,
        {"generate": "generate", "rewrite": "rewrite"},
    )
    builder.add_edge("generate", END)

    compiled = builder.compile()
    logger.info("Risk QA graph compiled (corrective-RAG loop enabled, max_attempts=%d)", MAX_ATTEMPTS)
    return compiled


_risk_qa_graph = None


def get_risk_qa_graph():
    """Get or create the compiled Risk QA graph singleton."""
    global _risk_qa_graph
    if _risk_qa_graph is None:
        _risk_qa_graph = build_risk_qa_graph()
    return _risk_qa_graph
