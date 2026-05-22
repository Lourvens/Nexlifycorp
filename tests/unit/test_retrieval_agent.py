"""Unit tests for the retrieval agent."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agents.retrieval_agent import (
    create_retrieval_agent,
    create_llm_node,
    create_tool_node,
    should_continue,
    MessagesState,
)


class TestShouldContinue:
    """Tests for conditional edge logic."""

    def test_end_when_no_tool_calls(self):
        """Route to END when LLM doesn't call tools."""
        state = MessagesState(messages=[
            AIMessage(content="Here's the answer directly.")
        ])

        result = should_continue(state)
        assert result == "__end__"

    def test_continue_when_tool_calls(self):
        """Route to tool_node when LLM calls tools."""
        ai_message = AIMessage(
            content="",
            tool_calls=[
                {"name": "retrieve_documents", "args": {"query": "test"}, "id": "call_123"}
            ]
        )
        state = MessagesState(messages=[ai_message])

        result = should_continue(state)
        assert result == "tool_node"

    def test_end_on_empty_messages(self):
        """Route to END when messages list is empty."""
        state = MessagesState(messages=[])
        result = should_continue(state)
        assert result == "__end__"


class TestLLMNode:
    """Tests for the LLM node."""

    @pytest.fixture
    def mock_model(self):
        """Create a mock model."""
        model = Mock(spec=ChatAnthropic)
        model.bind_tools = Mock(return_value=model)
        model.invoke = Mock(return_value=AIMessage(content="Test response"))
        return model

    @pytest.fixture
    def mock_tool(self):
        """Create a mock tool."""
        tool = Mock()
        tool.name = "retrieve_documents"
        return tool

    def test_llm_node_calls_model_with_messages(self, mock_model, mock_tool):
        """LLM node invokes model with system prompt + messages."""
        node = create_llm_node(mock_model, [mock_tool])

        state = MessagesState(messages=[HumanMessage(content="What is AI?")])
        result = node(state)

        mock_model.invoke.assert_called_once()
        call_args = mock_model.invoke.call_args[0][0]
        assert len(call_args) == 2  # SystemMessage + HumanMessage

    def test_llm_node_returns_messages(self, mock_model, mock_tool):
        """LLM node returns updated messages."""
        node = create_llm_node(mock_model, [mock_tool])

        state = MessagesState(messages=[HumanMessage(content="Hi")])
        result = node(state)

        assert "messages" in result
        assert len(result["messages"]) == 1


class TestToolNode:
    """Tests for the tool execution node."""

    @pytest.fixture
    def mock_tool(self):
        """Create a mock tool."""
        tool = Mock()
        tool.name = "retrieve_documents"
        tool.invoke = Mock(return_value="Retrieved: NVIDIA revenue was $60B")
        return tool

    def test_tool_node_executes_tool_calls(self, mock_tool):
        """Tool node calls tools and returns results."""
        node = create_tool_node({"retrieve_documents": mock_tool})

        ai_message = AIMessage(
            content="",
            tool_calls=[
                {"name": "retrieve_documents", "args": {"query": "NVDA"}, "id": "call_1"}
            ]
        )
        state = MessagesState(messages=[ai_message])

        result = node(state)

        mock_tool.invoke.assert_called_once_with({"query": "NVDA"})
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], ToolMessage)

    def test_tool_node_handles_unknown_tool(self, mock_tool):
        """Tool node handles unknown tool gracefully."""
        node = create_tool_node({"retrieve_documents": mock_tool})

        ai_message = AIMessage(
            content="",
            tool_calls=[
                {"name": "unknown_tool", "args": {}, "id": "call_1"}
            ]
        )
        state = MessagesState(messages=[ai_message])

        result = node(state)

        assert len(result["messages"]) == 1
        assert "Unknown tool" in result["messages"][0].content

    def test_tool_node_no_tool_calls(self, mock_tool):
        """Tool node returns empty on no tool calls."""
        node = create_tool_node({"retrieve_documents": mock_tool})

        ai_message = AIMessage(content="Just a regular response")
        state = MessagesState(messages=[ai_message])

        result = node(state)

        assert result["messages"] == []


class TestCreateRetrievalAgent:
    """Tests for agent factory function."""

    def test_create_agent_with_defaults(self):
        """Create agent with default parameters."""
        with patch("src.agents.retrieval_agent.ChatAnthropic") as mock_chat:
            mock_chat.return_value = Mock()
            agent = create_retrieval_agent()

            assert agent is not None
            mock_chat.assert_called_once()

    def test_create_agent_with_custom_model(self):
        """Create agent with custom model."""
        custom_model = Mock(spec=ChatAnthropic)
        custom_model.bind_tools = Mock(return_value=custom_model)

        agent = create_retrieval_agent(model=custom_model)

        assert agent is not None

    def test_agent_has_checkpointer(self):
        """Agent is compiled with checkpoint saver."""
        from langgraph.checkpoint.memory import InMemorySaver

        with patch("src.agents.retrieval_agent.ChatAnthropic") as mock_chat:
            mock_chat.return_value = Mock()
            mock_chat.return_value.bind_tools = Mock(return_value=mock_chat.return_value)

            agent = create_retrieval_agent()

            # Agent should have a checkpointer attribute
            # (langgraph compiles with checkpointer if provided)
            assert hasattr(agent, "checkpointer")

    def test_agent_has_graph(self):
        """Agent has compiled graph structure."""
        with patch("src.agents.retrieval_agent.ChatAnthropic") as mock_chat:
            mock_chat.return_value = Mock()
            mock_chat.return_value.bind_tools = Mock(return_value=mock_chat.return_value)

            agent = create_retrieval_agent()

            # Agent should have invoke method
            assert callable(agent.invoke)


class TestAgentInvocation:
    """Integration-style tests for agent invocation (mocked)."""

    def test_agent_invoke_simple_question(self):
        """Agent can answer simple questions without tools."""
        from src.agents.retrieval_agent import create_retrieval_agent

        # Create a mock model that responds without tools
        mock_model = Mock()
        mock_response = AIMessage(content="2 + 2 = 4")
        mock_model.bind_tools = Mock(return_value=mock_model)
        mock_model.invoke = Mock(return_value=mock_response)

        agent = create_retrieval_agent(model=mock_model)

        result = agent.invoke(
            {"messages": [HumanMessage(content="What is 2 + 2?")]},
            {"configurable": {"thread_id": "test-1"}}
        )

        assert len(result["messages"]) == 2  # HumanMessage + AIMessage

    def test_agent_invoke_with_tool_call(self):
        """Agent invokes tools when needed."""
        from src.agents.retrieval_agent import create_retrieval_agent

        mock_model = Mock()
        mock_response = AIMessage(
            content="Let me search for that.",
            tool_calls=[
                {"name": "retrieve_documents", "args": {"query": "revenue"}, "id": "call_1"}
            ]
        )
        mock_model.bind_tools = Mock(return_value=mock_model)
        mock_model.invoke = Mock(return_value=mock_response)

        # Create mock retriever tool
        mock_tool = Mock()
        mock_tool.name = "retrieve_documents"
        mock_tool.invoke = Mock(return_value="Found 3 documents about revenue")

        agent = create_retrieval_agent(model=mock_model, retriever_tool=mock_tool)

        result = agent.invoke(
            {"messages": [HumanMessage(content="What was the revenue?")]},
            {"configurable": {"thread_id": "test-2"}}
        )

        # Should have: HumanMessage, AIMessage (with tool call), ToolMessage, AIMessage (final)
        assert len(result["messages"]) >= 3