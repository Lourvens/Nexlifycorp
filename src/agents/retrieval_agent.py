"""
Minimal LangGraph retrieval agent for NexlifyCorp.

Provides a tool-calling agent that:
1. Decides whether to retrieve documents or respond directly
2. Retrieves documents when needed for grounding
3. Generates coherent financial answers

Usage:
    from src.agents import create_retrieval_agent

    agent = create_retrieval_agent()
    result = agent.invoke(
        {"messages": [HumanMessage(content="What was NVDA's revenue in 2024?")]},
        {"configurable": {"thread_id": "user-123"}}
    )
"""
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph, START, END

from src.agents.prompts import TOOL_SYSTEM_PROMPT
from src.agents.tools import get_retriever_tool
from src.core.llm import get_llm


# =============================================================================
# Graph Nodes
# =============================================================================

def create_llm_node(model: ChatAnthropic, tools: list[tool]):
    """Create the LLM node function."""
    model_with_tools = model.bind_tools(tools)

    def llm_node(state: MessagesState) -> MessagesState:
        """Call the LLM with tools bound."""
        response = model_with_tools.invoke(
            [SystemMessage(content=TOOL_SYSTEM_PROMPT)] + state["messages"]
        )
        return {"messages": [response]}

    return llm_node


def create_tool_node(tools_by_name: dict[str, tool]):
    """Create the tool execution node."""

    def tool_node(state: MessagesState) -> MessagesState:
        """Execute tool calls from the last message."""
        last_message = state["messages"][-1]

        if not last_message.tool_calls:
            return {"messages": []}

        results = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name in tools_by_name:
                result = tools_by_name[tool_name].invoke(tool_args)
                results.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )
            else:
                results.append(
                    ToolMessage(
                        content=f"Unknown tool: {tool_name}",
                        tool_call_id=tool_call["id"],
                    )
                )

        return {"messages": results}

    return tool_node


# =============================================================================
# Conditional Edge
# =============================================================================

def should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
    """Route to tool_node if LLM made tool calls, otherwise end."""
    messages = state["messages"]
    if not messages:
        return "__end__"

    last_message = messages[-1]

    # If the LLM made tool calls, route to tool execution
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"

    # Otherwise, respond directly to user
    return "__end__"


# =============================================================================
# Agent Factory
# =============================================================================

def create_retrieval_agent(
    model: ChatAnthropic | None = None,
    retriever_tool: tool | None = None,
    checkpoint_saver=None,  # Optional - langgraph dev provides its own
):
    """
    Create the minimal LangGraph retrieval agent.

    Args:
        model: ChatAnthropic instance. If None, creates default Sonnet.
        retriever_tool: LangChain tool for retrieval. If None, creates default.
        checkpoint_saver: Checkpointer for conversation memory.
                         langgraph dev provides its own; pass None in that context.

    Returns:
        Compiled LangGraph agent
    """
    # Setup
    model = model or get_llm()
    retriever_tool = retriever_tool or get_retriever_tool()

    tools = [retriever_tool]
    tools_by_name = {t.name: t for t in tools}

    # Create nodes
    llm_node_fn = create_llm_node(model, tools)
    tool_node_fn = create_tool_node(tools_by_name)

    # Build graph
    builder = StateGraph(MessagesState)

    builder.add_node("llm_node", llm_node_fn)
    builder.add_node("tool_node", tool_node_fn)

    builder.add_edge(START, "llm_node")

    builder.add_conditional_edges(
        "llm_node",
        should_continue,
        {
            "tool_node": "tool_node",
            "__end__": END,
        },
    )

    builder.add_edge("tool_node", "llm_node")

    # Compile - only add checkpointer if explicitly provided
    # langgraph dev provides its own persistence
    if checkpoint_saver is not None:
        return builder.compile(checkpointer=checkpoint_saver)
    return builder.compile()


# =============================================================================
# Singleton (for langgraph.json)
# =============================================================================

_agent = None


def get_agent():
    """Get singleton agent instance for LangGraph CLI."""
    global _agent
    if _agent is None:
        _agent = create_retrieval_agent()
    return _agent


# Export as `agent` for langgraph.json convention
# langgraph CLI expects a callable that returns the graph when invoked with config
agent = get_agent