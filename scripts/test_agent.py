#!/usr/bin/env python3
"""
Test script for the retrieval agent.

Usage:
    python scripts/test_agent.py

Requirements:
    - Qdrant running at localhost:6333
    - ANTHROPIC_API_KEY set in .env
    - Vector store has some data (run ingestion first)
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage

from src.agents import create_retrieval_agent


def test_agent_basic():
    """Test basic agent invocation."""
    print("Creating agent...")
    agent = create_retrieval_agent()

    print("\n--- Test 1: Direct question (no retrieval needed) ---")
    result = agent.invoke(
        {"messages": [HumanMessage(content="What is 2 + 2?")]},
        {"configurable": {"thread_id": "test-1"}}
    )
    print(result["messages"][-1].content[:500])

    print("\n--- Test 2: Financial question (should trigger retrieval) ---")
    result = agent.invoke(
        {"messages": [HumanMessage(content="What was NVIDIA's revenue in their latest 10-K?")]},
        {"configurable": {"thread_id": "test-2"}}
    )
    print(result["messages"][-1].content[:1000])

    print("\n--- Test 3: Follow-up (uses checkpoint memory) ---")
    result = agent.invoke(
        {"messages": [HumanMessage(content="Tell me more about their risk factors")]},
        {"configurable": {"thread_id": "test-2"}}
    )
    print(result["messages"][-1].content[:500])


def test_retriever_only():
    """Test retriever directly."""
    from src.retrieval import Retriever

    print("\n--- Test Retriever ---")
    retriever = Retriever()

    docs = retriever.retrieve("revenue", k=3)
    print(f"Retrieved {len(docs)} documents")

    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        print(f"\n[{i}] {meta.get('source_detail', 'unknown')}")
        print(f"    Content type: {meta.get('content_type', 'unknown')}")
        print(f"    Preview: {doc.page_content[:150]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("NexlifyCorp Retrieval Agent Test")
    print("=" * 60)

    try:
        test_retriever_only()
    except Exception as e:
        print(f"Retriever test failed (may need Qdrant): {e}")

    try:
        test_agent_basic()
    except Exception as e:
        print(f"\nAgent test failed: {e}")
        print("Check ANTHROPIC_API_KEY and Qdrant connection")