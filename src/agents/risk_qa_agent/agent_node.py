"""Agent node — main LLM (Sonnet) as entry point with self-retrieval capability.

The agent has access to internal and public retriever tools. It can:
- Use tools to ground answers about NexlifyCorp, SEC filings, etc.
- Decide to delegate the full retrieval pipeline for complex multi-step queries
- Respond directly for conversational queries (no tool use)
"""
import logging

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from src.core.llm import get_llm
from src.agents.tools import create_public_retriever_tool, create_private_retriever_tool

logger = logging.getLogger(__name__)


AGENT_SYSTEM_PROMPT = """You are a Risk Intelligence QA Agent — a senior risk analyst.

You have access to two search tools:
- retrieve_public_documents: Search SEC EDGAR filings (10-K, 10-Q, 8-K) for public company info
- retrieve_private_documents: Search internal NexlifyCorp documents (risk registers, board memos, strategy docs)

You MUST use these tools when asked about:
- NexlifyCorp's own documents, strategy, risk landscape, board memos
- Specific SEC filings, company financials, competitor analysis
- Any question that requires factual evidence from documents

You CAN respond directly (from general knowledge) for:
- "Who are you", "what can you do", greetings, thanks
- General conversation unrelated to risk intelligence

## Decision Protocol

After using tools (or if no tools were needed), decide:

**"DIRECT:"** — Prefix your response with DIRECT: if you can answer from tool results or general knowledge without needing the full retrieval pipeline. Examples:
- Tool results fully answered the question
- Conversational query that needs no documents
- You found enough information to give a complete answer

**"DELEGATE:"** — Prefix your response with DELEGATE: if:
- The question requires a comprehensive multi-source analysis you can't fully answer with quick tool lookups
- The question is about detailed risk factor comparisons across many documents
- You need the full route→retrieve→reason→generate pipeline for a thorough evidence-backed answer

When in doubt, prefer DELEGATE — the full pipeline produces higher quality analysis."""


def _build_messages(messages: list) -> list:
    """Build the message list for the agent, converting state messages to LangChain format."""
    lc_messages = []
    for m in messages:
        if hasattr(m, "type"):
            if m.type == "human":
                lc_messages.append(HumanMessage(content=m.content))
            elif m.type == "ai":
                lc_messages.append(AIMessage(content=m.content))
            elif m.type == "tool":
                lc_messages.append(ToolMessage(content=m.content, tool_call_id=m.tool_call_id))
    return lc_messages


def _execute_tool_calls(tool_calls: list, public_tool, private_tool) -> list[ToolMessage]:
    """Execute a list of tool calls and return ToolMessage results."""
    results = []
    for tc in tool_calls:
        tool_name = tc.name
        tool_args = tc.args

        try:
            if tool_name == "retrieve_public_documents":
                result = public_tool.invoke(tool_args)
            elif tool_name == "retrieve_private_documents":
                result = private_tool.invoke(tool_args)
            else:
                result = f"Unknown tool: {tool_name}"

            results.append(ToolMessage(content=str(result), tool_call_id=tc.id))
            logger.info(f"  → Tool '{tool_name}' returned {len(str(result))} chars")
        except Exception as e:
            logger.error(f"  → Tool '{tool_name}' error: {e}")
            results.append(ToolMessage(content=f"Error: {e}", tool_call_id=tc.id))

    return results


def agent_node(state: dict) -> dict:
    """
    Entry point: main LLM with retriever tools decides conversational vs. retrieval path.

    Uses Sonnet with bound retriever tools. The LLM can use tools to ground answers
    about NexlifyCorp, SEC filings, etc., then decide to respond directly or delegate.

    conversational / tools answered question → responds directly, graph ENDs
    needs full multi-source analysis              → needs_retrieval=True, continue pipeline

    Args:
        state: AgentState with messages

    Returns:
        dict with needs_retrieval (bool) and messages (AIMessage)
    """
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No messages in state")

    # Build LangChain-formatted messages
    lc_messages = _build_messages(messages)

    # Create retriever tools
    public_tool = create_public_retriever_tool()
    private_tool = create_private_retriever_tool()

    # Bind tools to the main LLM
    main_llm = get_llm()
    llm_with_tools = main_llm.bind_tools([public_tool, private_tool])

    # Add system prompt as a HumanMessage first
    system_msg = HumanMessage(content=AGENT_SYSTEM_PROMPT)
    full_messages = [system_msg] + lc_messages

    # Invoke the LLM
    response = llm_with_tools.invoke(full_messages)
    logger.info(f"Agent node: initial response type={type(response).__name__}")

    # Tool execution loop — keep going until no more tool calls
    while hasattr(response, "tool_calls") and response.tool_calls:
        logger.info(f"  → Executing {len(response.tool_calls)} tool call(s)")

        # Add the AI response (with tool calls) to the message list
        full_messages.append(response)

        # Execute all tool calls
        tool_results = _execute_tool_calls(response.tool_calls, public_tool, private_tool)
        full_messages.extend(tool_results)

        # Re-invoke the LLM with tool results
        response = llm_with_tools.invoke(full_messages)

    # No more tool calls — get the final response text
    final_text = ""
    if hasattr(response, "content") and response.content:
        final_text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()

    logger.info(f"Agent node: final response starts with: {final_text[:80]}")

    # Check for DELEGATE vs DIRECT
    if final_text.upper().startswith("DELEGATE:"):
        logger.info("Agent node: DELEGATE — continuing to full retrieval pipeline")
        return {
            "needs_retrieval": True,
            "messages": [AIMessage(content=final_text)],
        }

    # DIRECT answer — use the text after "DIRECT:" if present
    if final_text.upper().startswith("DIRECT:"):
        answer = final_text[7:].strip()  # strip "DIRECT:" prefix
    else:
        answer = final_text  # fallback for responses without prefix

    logger.info("Agent node: DIRECT answer — graph will END")
    return {
        "needs_retrieval": False,
        "messages": [AIMessage(content=answer)],
    }