"""Agent node — Sonnet risk analyst entry point using langchain.agents.create_agent.

Uses create_agent with bound retriever tools for self-grounded answers.
Decision protocol:
- DIRECT: answer from tool results or general knowledge, graph ENDs
- DELEGATE: continue through route→retrieve→reason→generate pipeline
"""
import logging

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage

from src.core.llm import get_llm
from src.agents.tools import create_public_retriever_tool, create_private_retriever_tool
from src.agents.risk_qa_agent.prompts import AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Tools for create_agent
AGENT_TOOLS = [
    create_public_retriever_tool(),
    create_private_retriever_tool(),
]


def _extract_final_text(result: dict) -> str:
    """Extract text from the last message in agent result."""
    messages = result.get("messages", [])
    if not messages:
        return ""

    last = messages[-1]
    if hasattr(last, "content"):
        if isinstance(last.content, list):
            return "".join(
                block.text for block in last.content
                if hasattr(block, "text")
            ).strip()
        return str(last.content).strip()
    return str(last).strip()


def agent_node(state: dict) -> dict:
    """
    Entry point: Sonnet risk analyst with self-retrieval decides path.

    conversational / tool-answered question → DIRECT → graph ENDs
    needs full multi-source analysis         → DELEGATE → pipeline continues

    Args:
        state: AgentState with messages

    Returns:
        dict with needs_retrieval (bool) and messages (AIMessage list)
    """
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No messages in state")

    # Build LangChain message list from state
    lc_messages = []
    for m in messages:
        if not hasattr(m, "type"):
            continue
        if m.type == "human":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.type == "ai":
            lc_messages.append(AIMessage(content=m.content))

    # Create and invoke the agent
    main_llm = get_llm()
    agent = create_agent(
        model=main_llm,
        tools=AGENT_TOOLS,
        system_prompt=AGENT_SYSTEM_PROMPT,
    )

    result = agent.invoke({"messages": lc_messages})

    final_text = _extract_final_text(result)
    logger.info(f"Agent node: final text starts with: {final_text[:80]}")

    # Check DELEGATE vs DIRECT
    if final_text.upper().startswith("DELEGATE:"):
        logger.info("Agent node: DELEGATE — continuing to retrieval pipeline")
        return {
            "needs_retrieval": True,
            "messages": [AIMessage(content=final_text)],
        }

    # DIRECT answer — strip prefix if present
    if final_text.upper().startswith("DIRECT:"):
        answer = final_text[7:].strip()
    else:
        answer = final_text

    logger.info("Agent node: DIRECT answer — graph will END")
    return {
        "needs_retrieval": False,
        "messages": [AIMessage(content=answer)],
    }