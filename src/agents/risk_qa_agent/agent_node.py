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


def agent_node(state: dict) -> dict:
    """
    Entry point: Sonnet risk analyst with self-retrieval decides path.

    conversational / tool-answered question → DIRECT → graph ENDs
    needs full multi-source analysis         → DELEGATE → pipeline continues

    Args:
        state: AgentState with messages

    Returns:
        dict with needs_retrieval (bool) and messages (appended from create_agent result)
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

    # create_agent returns all messages in result["messages"] (human + tool calls + final AIMessage)
    agent_messages = result.get("messages", [])
    logger.info(f"Agent node: {len(agent_messages)} messages from create_agent")

    # Extract final text from the last message
    final_msg = agent_messages[-1] if agent_messages else None
    if final_msg and hasattr(final_msg, "content"):
        content = final_msg.content
        if isinstance(content, list):
            final_text = "".join(
                block.text for block in content if hasattr(block, "text")
            ).strip()
        else:
            final_text = str(content).strip()
    elif final_msg:
        final_text = str(final_msg).strip()
    else:
        final_text = ""

    logger.info(f"Agent node: final text starts with: {final_text[:80]}")

    # Check DELEGATE prefix — only special marker we need to detect
    if final_text.upper().startswith("DELEGATE:"):
        logger.info("Agent node: DELEGATE — continuing to retrieval pipeline")
        return {
            "needs_retrieval": True,
            "messages": agent_messages,  # pass through all messages from create_agent
        }

    # Direct response — no prefix stripping, just use the natural answer
    logger.info("Agent node: direct response — graph will END")
    return {
        "needs_retrieval": False,
        "messages": agent_messages,  # pass through all messages (add_messages will handle accumulation)
    }