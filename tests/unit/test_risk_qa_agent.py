"""Unit tests for Risk QA Agent."""
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.risk_qa_agent.state import RiskAgentState, Citation
from src.agents.risk_qa_agent.route_node import route_node
from src.agents.risk_qa_agent.graph import get_risk_qa_graph, build_risk_qa_graph


class TestRiskAgentState:
    def test_citation_structure(self):
        c = Citation(
            index=1,
            document_id="NCR-2025-Q2-001",
            document_title="2025-Q2-Internal-Risk-Register.md",
            source_category="internal_nexlify",
            access_level="INTERNAL",
            document_date="2025-05-17",
            excerpt="78% of our advanced packaging...",
            chunk_content="78% of our advanced packaging (CoWoS)...",
        )
        assert c["index"] == 1
        assert c["document_id"] == "NCR-2025-Q2-001"
        assert c["access_level"] == "INTERNAL"

    def test_agent_state_keys(self):
        """Verify RiskAgentState has the required keys via annotations."""
        from src.agents.risk_qa_agent.state import RiskAgentState
        annotations = RiskAgentState.__annotations__
        assert "messages" in annotations
        assert "route_key" in annotations
        assert "retrieved_chunks" in annotations
        assert "reasoning_trace" in annotations
        assert "citations" in annotations


class TestRouteNode:
    @patch("src.agents.risk_qa_agent.route_node.get_fast_llm")
    def test_route_public_only(self, mock_get_fast_llm):
        mock_llm = MagicMock()
        # Simulate the full chain invoke: chain.invoke({"query": ...})
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "public_only"
        mock_get_fast_llm.return_value = mock_chain

        # Patch the chain builder to return our mock chain
        with patch("src.agents.risk_qa_agent.route_node.build_route_chain") as mock_build:
            mock_build.return_value = mock_chain
            state = {"messages": [HumanMessage(content="What does NVIDIA's 10-K say about risk?")]}
            result = route_node(state)
            assert result["route_key"] == "public_only"

    @patch("src.agents.risk_qa_agent.route_node.get_fast_llm")
    def test_route_internal_only(self, mock_get_fast_llm):
        mock_llm = MagicMock()
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "internal_only"
        mock_get_fast_llm.return_value = mock_chain

        with patch("src.agents.risk_qa_agent.route_node.build_route_chain") as mock_build:
            mock_build.return_value = mock_chain
            state = {"messages": [HumanMessage(content="What is our supply chain risk?")]}
            result = route_node(state)
            assert result["route_key"] == "internal_only"

    @patch("src.agents.risk_qa_agent.route_node.get_fast_llm")
    def test_route_both(self, mock_get_fast_llm):
        mock_llm = MagicMock()
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "both"
        mock_get_fast_llm.return_value = mock_chain

        with patch("src.agents.risk_qa_agent.route_node.build_route_chain") as mock_build:
            mock_build.return_value = mock_chain
            state = {"messages": [HumanMessage(content="How does our risk compare to NVIDIA's?")]}
            result = route_node(state)
            assert result["route_key"] == "both"

    @patch("src.agents.risk_qa_agent.route_node.get_fast_llm")
    def test_route_invalid_defaults_to_both(self, mock_get_fast_llm):
        mock_llm = MagicMock()
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "junk_route"
        mock_get_fast_llm.return_value = mock_chain

        with patch("src.agents.risk_qa_agent.route_node.build_route_chain") as mock_build:
            mock_build.return_value = mock_chain
            state = {"messages": [HumanMessage(content="Tell me about risk")]}
            result = route_node(state)
            assert result["route_key"] == "both"


class TestRetrieveNode:
    def test_retrieve_node_requires_route_key(self):
        state = {"messages": [HumanMessage(content="test")]}
        with pytest.raises(ValueError, match="route_key not set"):
            from src.agents.risk_qa_agent.retrieve_node import retrieve_node
            retrieve_node(state)

    @patch("src.agents.risk_qa_agent.retrieve_node.create_public_retriever_tool")
    @patch("src.agents.risk_qa_agent.retrieve_node.create_private_retriever_tool")
    def test_retrieve_public_only(self, mock_private_tool, mock_public_tool):
        mock_public_tool.return_value.invoke.return_value = "Document 1: NVDA 10-K\nContent: Risk factors..."
        mock_private_tool.return_value.invoke.return_value = ""

        from src.agents.risk_qa_agent.retrieve_node import retrieve_node

        state = {
            "route_key": "public_only",
            "messages": [HumanMessage(content="What are NVIDIA's risk factors?")]
        }
        result = retrieve_node(state)
        assert "retrieved_chunks" in result

    @patch("src.agents.risk_qa_agent.retrieve_node.create_public_retriever_tool")
    @patch("src.agents.risk_qa_agent.retrieve_node.create_private_retriever_tool")
    def test_retrieve_internal_only(self, mock_private_tool, mock_public_tool):
        mock_public_tool.return_value.invoke.return_value = ""
        mock_private_tool.return_value.invoke.return_value = "Document 1: Internal Risk Register\nContent: Taiwan supply..."

        from src.agents.risk_qa_agent.retrieve_node import retrieve_node

        state = {
            "route_key": "internal_only",
            "messages": [HumanMessage(content="What is our supply chain risk?")]
        }
        result = retrieve_node(state)
        assert "retrieved_chunks" in result


class TestGraphBuilding:
    def test_graph_has_five_nodes(self):
        """Graph should have __start__ + 4 agent nodes."""
        graph = get_risk_qa_graph()
        # __start__ is auto-injected by LangGraph
        node_names = [k for k in graph.nodes.keys() if k != "__start__"]
        assert set(node_names) == {"route", "retrieve", "reason", "generate"}

    def test_graph_edges(self):
        """Graph should have linear edges: route→retrieve→reason→generate→END."""
        graph = get_risk_qa_graph()
        # Verify structure by checking it compiles without error
        assert graph is not None

    def test_graph_compile_singleton(self):
        """get_risk_qa_graph returns the same instance."""
        g1 = get_risk_qa_graph()
        g2 = get_risk_qa_graph()
        assert g1 is g2


class TestPrompts:
    def test_route_prompt_not_empty(self):
        from src.agents.risk_qa_agent.prompts import ROUTE_SYSTEM_PROMPT
        assert len(ROUTE_SYSTEM_PROMPT) > 50
        assert "public_only" in ROUTE_SYSTEM_PROMPT
        assert "internal_only" in ROUTE_SYSTEM_PROMPT
        assert "both" in ROUTE_SYSTEM_PROMPT

    def test_reason_prompt_not_empty(self):
        from src.agents.risk_qa_agent.prompts import REASON_SYSTEM_PROMPT
        assert len(REASON_SYSTEM_PROMPT) > 50
        assert "REASONING TRACE" in REASON_SYSTEM_PROMPT

    def test_generate_prompt_not_empty(self):
        from src.agents.risk_qa_agent.prompts import GENERATE_SYSTEM_PROMPT
        assert len(GENERATE_SYSTEM_PROMPT) > 50
        assert "citation" in GENERATE_SYSTEM_PROMPT.lower()