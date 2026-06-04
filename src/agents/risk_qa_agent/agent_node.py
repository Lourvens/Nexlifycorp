"""Agent node — Sonnet risk analyst with manual tool loop.

Simple approach: bind tools to model, manually handle tool calls in a loop,
return a single AIMessage. No create_agent magic.
"""
import logging

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from src.core.llm import get_llm
from src.agents.tools import create_public_retriever_tool, create_private_retriever_tool
from src.agents.risk_qa_agent.prompts import AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Tools bound to this node
AGENT_TOOLS = [
    create_public_retriever_tool(),
    create_private_retriever_tool(),
]


def _extract_text(response) -> str:
    """Extract text from an AIMessage response."""
    if hasattr(response, "content") and response.content:
        if isinstance(response.content, list):
            return "".join(
                block.text for block in response.content
                if hasattr(block, "text")
            ).strip()
        return str(response.content).strip()
    if hasattr(response, "text"):
        return str(response.text).strip()
    return str(response).strip()


def agent_node(state: dict) -> dict:
    """
    Entry point: Sonnet with retriever tools decides path.

    conversational / tool-answered  → needs_retrieval=False, returns final AIMessage
    complex multi-source analysis   → needs_retrieval=True, pipeline continues

    Pattern: manual tool loop — bind_tools → invoke → while tool_calls: execute + reinvoke
    """
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No messages in state")

    # Build message list: SystemMessage + all state messages
    lc_messages: list = [SystemMessage(content=AGENT_SYSTEM_PROMPT)]
    for m in messages:
        if not hasattr(m, "type"):
            continue
        if m.type == "human":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.type == "ai":
            lc_messages.append(AIMessage(content=m.content if hasattr(m, "content") else str(m)))

    # Bind tools to main LLM
    main_llm = get_llm()
    model = main_llm.bind_tools(AGENT_TOOLS)

    # First invocation
    response = model.invoke(lc_messages)
    lc_messages.append(response)

    # Manual tool loop
    while hasattr(response, "tool_calls") and response.tool_calls:
        logger.info(f"  → Executing {len(response.tool_calls)} tool call(s)")

        for tc in response.tool_calls:
            tool_name = tc.name
            tool_args = tc.args
            tool_id = tc.id

            try:
                # Find the matching tool
                matched = next((t for t in AGENT_TOOLS if t.name == tool_name), None)
                if matched:
                    result = matched.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"

                logger.info(f"  → Tool '{tool_name}' returned {len(str(result))} chars")
                lc_messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_id)
                )
            except Exception as e:
                logger.error(f"  → Tool '{tool_name}' error: {e}")
                lc_messages.append(
                    ToolMessage(content=f"Error: {e}", tool_call_id=tool_id)
                )

        # Re-invoke with tool results
        response = model.invoke(lc_messages)
        lc_messages.append(response)

    # No more tool calls — extract final text
    final_text = _extract_text(response)
    logger.info(f"Agent node: final text = {final_text[:80]}")

    # Check DELEGATE vs DIRECT
    if final_text.upper().startswith("DELEGATE:"):
        delegate_note = final_text[9:].strip()
        logger.info("Agent node: DELEGATE")
        return {
            "needs_retrieval": True,
            "messages": [AIMessage(content=delegate_note)],
        }

    # DIRECT answer — strip prefix
    if final_text.upper().startswith("DIRECT:"):
        answer = final_text[7:].strip()
    else:
        answer = final_text

    logger.info("Agent node: DIRECT — graph ENDs")
    return {
        "needs_retrieval": False,
        "messages": [AIMessage(content=answer)],
    }