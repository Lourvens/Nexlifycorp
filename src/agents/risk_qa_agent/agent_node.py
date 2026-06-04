"""Agent node — main LLM (Sonnet) as entry point and risk analyst persona.

The agent uses full reasoning to decide:
- conversational / identity / meta questions → respond directly and END
- questions requiring document evidence → needs_retrieval=True, continue pipeline
"""
import logging

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from src.core.llm import get_llm
from src.agents.risk_qa_agent.prompts import GENERATE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


AGENT_DECISION_PROMPT = """You are a Risk Intelligence QA Agent — a senior risk analyst persona.

You have a full conversation history. Your job is to decide whether you can answer
the user's latest message directly, or whether you need to search documents first.

## Decision

**Respond directly and END** when the query is:
- Conversational: greetings, "thanks", "hello"
- Identity questions: "who are you", "what can you do", "tell me about yourself"
- Meta questions about how to use the system or the workflow
- Pure chat that doesn't require document evidence

**Delegate to the retrieval workflow** (set needs_retrieval=True) when the query asks:
- About SEC filings, risk factors, financial data, competitor analysis
- For specific facts, metrics, events, or analysis from documents
- Anything that mentions specific companies, time periods, or requires evidence
- Questions where document grounding would improve the answer

## Your Persona

You are a sharp, evidence-driven risk analyst. You cite your sources. You are concise.
You prefer precise, actionable insights over vague summaries. You work at NexlifyCorp,
focused on financial risk intelligence combining SEC EDGAR filings with internal docs.

## Important

If you respond directly (conversational path), your response IS the final answer —
the graph will END after your response. Do not mention the retrieval pipeline.
If you delegate, do not answer the question yourself — just set needs_retrieval=True
and the pipeline will produce the answer with evidence."""


def build_decision_prompt(query: str, conversation_history: str) -> str:
    return f"{AGENT_DECISION_PROMPT}\n\n## Conversation History\n{conversation_history}\n\n## Latest User Message\n{query}\n\n## Your Decision\nAnalyze the user's message. If you can answer directly, do so. If you must delegate to the retrieval workflow, say 'DELEGATE' on a single line."""


def agent_node(state: dict) -> dict:
    """
    Entry point: main LLM as risk analyst decides conversational vs. retrieval path.

    conversational → responds directly, graph ENDs
    needs docs      → needs_retrieval=True, graph continues route→retrieve→reason→generate

    Args:
        state: AgentState with messages

    Returns:
        dict with needs_retrieval (bool) and optionally messages (AIMessage for direct path)
    """
    messages = state.get("messages", [])
    if not messages:
        raise ValueError("No messages in state")

    human_msgs = [m for m in messages if hasattr(m, "type") and m.type == "human"]
    if not human_msgs:
        raise ValueError("No HumanMessage found")

    query = human_msgs[-1].content

    # Build conversation history (prior human messages as context)
    history_parts = []
    for m in messages[:-1]:
        role = "User" if hasattr(m, "type") and m.type == "human" else "Assistant"
        history_parts.append(f"{role}: {m.content}")
    conversation_history = "\n".join(history_parts) if history_parts else "(no prior history)"

    decision_prompt = build_decision_prompt(query, conversation_history)

    main_llm = get_llm()
    chain = RunnableLambda(lambda _: decision_prompt) | main_llm | StrOutputParser()

    response = chain.invoke({}).strip()

    logger.info(f"Agent node: query='{query[:60]}...' → response starts with: {response[:60]}")

    # Check if the LLM chose to delegate
    if response.upper().startswith("DELEGATE"):
        logger.info("Agent node: delegating to retrieval workflow")
        return {"needs_retrieval": True}

    # Direct answer path — response IS the final answer, graph ends
    logger.info("Agent node: direct answer, graph will END")
    return {
        "needs_retrieval": False,
        "messages": [AIMessage(content=response)],
    }