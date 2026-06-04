"""LangGraph StateGraph for Risk QA Agent."""
import logging

from langgraph.graph import StateGraph, START, END

from src.agents.risk_qa_agent.state import RiskAgentState
from src.agents.risk_qa_agent.agent_node import agent_node
from src.agents.risk_qa_agent.route_node import route_node
from src.agents.risk_qa_agent.retrieve_node import retrieve_node
from src.agents.risk_qa_agent.reason_node import reason_node
from src.agents.risk_qa_agent.generate_node import generate_node

logger = logging.getLogger(__name__)


def _should_retrieve(state: dict) -> str:
    """Route from agent node: skip retrieval for direct_answer, otherwise proceed."""
    needs_retrieval = state.get("needs_retrieval", True)
    if not needs_retrieval:
        return "end"
    return "route"


def build_risk_qa_graph():
    """
    Build and compile the Risk QA Agent StateGraph.

    Graph structure:
        START → agent ──[needs_retrieval=False]──→ END  (direct answer)
                  └──[needs_retrieval=True]──→ route → retrieve → reason → generate → END

    Edges:
        START → agent (always)
        agent → END (when needs_retrieval=False, direct conversational answer)
        agent → route (when needs_retrieval=True, full retrieval pipeline)
        route → retrieve (always)
        retrieve → reason (always)
        reason → generate (always)
        generate → END (always)

    Args:
        None

    Returns:
        Compiled StateGraph ready for invocation
    """
    builder = StateGraph(RiskAgentState)

    # Add nodes
    builder.add_node("agent", agent_node)    # main LLM entry point
    builder.add_node("route", route_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("reason", reason_node)
    builder.add_node("generate", generate_node)

    # Define edges
    builder.add_edge(START, "agent")

    # Conditional: agent decides direct answer (END) or retrieval pipeline
    builder.add_conditional_edges(
        "agent",
        _should_retrieve,
        {
            "end": END,       # direct_answer path — agent responded, graph ends
            "route": "route", # needs_retrieval path — go through full chain
        }
    )

    # Full retrieval path edges
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