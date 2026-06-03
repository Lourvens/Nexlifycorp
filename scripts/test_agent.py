#!/usr/bin/env python3
"""
Test script for the retriever.

Usage:
    python scripts/test_agent.py

Requirements:
    - Qdrant running at localhost:6333
    - Vector store has some data (run ingestion first)
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


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
    print("NexlifyCorp Retriever Test")
    print("=" * 60)

    try:
        test_retriever_only()
    except Exception as e:
        print(f"Retriever test failed (may need Qdrant): {e}")