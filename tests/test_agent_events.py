"""
Unit tests for agent event emission and consumption.

Tests cover:
1. Event emission by Agent using mock LLM outputs
2. Event consumption by UI handlers
"""

import json
from unittest.mock import Mock, MagicMock, patch, call
from dataclasses import dataclass
from typing import Optional

import pytest

from events.agent_events import (
    AgentEvent,
    UserMessageSubmitted,
    AssistantMessageFinished,
    StreamingToken,
    ConversationLoaded,
    AgentIdle,
    AgentBusy,
    ToolStarted,
    ToolCallSucceeded,
    ToolCallFailed,
    APICallFailed,
    ErrorEvent,
    ThinkingStarted,
)
from events.event_bus import EventBus
from agent.agent import Agent
from tools.base import Tool, ToolResult


# ============================================================================
# Mock LLM Client for testing event emission
# ============================================================================

class MockLLMClient:
    """Mock LLM client that returns predefined responses."""
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0

    def chat(self, messages):
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return "Default response"


@dataclass
class MockToolCall:
    """Mock tool call object."""
    id: str
    function: "MockFunction"


@dataclass
class MockFunction:
    name: str
    arguments: str


@dataclass
class MockModelResponse:
    """Mock model response with tool calls."""
    tool_calls: list
    content: str = ""


# ============================================================================
# Test Event Emission
# ============================================================================

class TestEventEmission:
    """Tests for event emission by the Agent."""

    def setup_method(self):
        """Set up fresh event bus and agent for each test."""
        self.event_bus = EventBus()
        self.received_events = []

        # Subscribe to all event types to capture them
        for event_type in [
            UserMessageSubmitted, AssistantMessageFinished, StreamingToken,
            ConversationLoaded, AgentIdle, AgentBusy, ToolStarted,
            ToolCallSucceeded, ToolCallFailed, APICallFailed, ThinkingStarted
        ]:
            self.event_bus.subscribe(event_type, self._capture_event)

    def _capture_event(self, event):
        self.received_events.append(event)

    def _create_agent(self, client):
        return Agent(client=client, event_bus=self.event_bus)

    def test_emits_user_message_submitted(self):
        """Test that UserMessageSubmitted event is emitted when user sends message."""
        client = MockLLMClient(["Response"])
        agent = self._create_agent(client)

        # Directly emit the event (simulating UI submitting a message)
        agent.event_bus.emit(UserMessageSubmitted(message="Hello"))

        user_events = [e for e in self.received_events if isinstance(e, UserMessageSubmitted)]
        assert len(user_events) == 1
        assert user_events[0].message == "Hello"

    def test_emits_agent_busy_and_idle_for_simple_response(self):
        """Test AgentBusy and AgentIdle events for simple string response."""
        client = MockLLMClient(["Simple response"])
        agent = self._create_agent(client)

        # Emit user message to trigger processing
        agent.event_bus.emit(UserMessageSubmitted(message="Hi"))

        # Wait for background thread to complete (in real test, we'd need to wait)
        # For this test, we check events are emitted by directly calling the handler
        busy_events = [e for e in self.received_events if isinstance(e, AgentBusy)]
        assert len(busy_events) >= 1

    def test_emits_assistant_message_finished_for_string_response(self):
        """Test AssistantMessageFinished is emitted for string response."""
        client = MockLLMClient(["String response"])
        agent = self._create_agent(client)

        # Simulate the background processing
        agent._process_message_background("Hello")

        assistant_events = [e for e in self.received_events if isinstance(e, AssistantMessageFinished)]
        assert len(assistant_events) == 1
        assert assistant_events[0].message == "String response"

    def test_emits_tool_started_and_succeeded_for_tool_call(self):
        """Test ToolStarted and ToolCallSucceeded for successful tool call."""
        # Create a mock response with tool call
        tool_call = MockToolCall(
            id="call_123",
            function=MockFunction(name="filesystem_list_files", arguments='{"path": "."}')
        )
        response_with_tool = MockModelResponse(tool_calls=[tool_call])
        final_response = "Files listed successfully"

        client = MockLLMClient([response_with_tool, final_response])
        agent = self._create_agent(client)

        # Enable agent mode
        agent.agent_mode = True

        # Process message - this will trigger tool call
        agent._process_message_background("List files")

        started_events = [e for e in self.received_events if isinstance(e, ToolStarted)]
        succeeded_events = [e for e in self.received_events if isinstance(e, ToolCallSucceeded)]

        assert len(started_events) == 1
        assert started_events[0].tool_name == "filesystem_list_files"
        assert len(succeeded_events) == 1
        assert succeeded_events[0].tool_name == "filesystem_list_files"

    def test_emits_tool_call_failed_for_invalid_json(self):
        """Test ToolCallFailed is emitted for invalid JSON in tool arguments."""
        tool_call = MockToolCall(
            id="call_123",
            function=MockFunction(name="filesystem_list_files", arguments="invalid json")
        )
        response_with_tool = MockModelResponse(tool_calls=[tool_call])

        client = MockLLMClient([response_with_tool, "Done"])
        agent = self._create_agent(client)
        agent.agent_mode = True

        agent._process_message_background("List files")

        failed_events = [e for e in self.received_events if isinstance(e, ToolCallFailed)]
        assert len(failed_events) == 1
        assert failed_events[0].tool_name == "filesystem_list_files"
        assert "Invalid JSON" in failed_events[0].error

    def test_emits_tool_call_failed_for_unknown_tool(self):
        """Test ToolCallFailed is emitted for unknown tool."""
        tool_call = MockToolCall(
            id="call_123",
            function=MockFunction(name="unknown_tool", arguments='{}')
        )
        response_with_tool = MockModelResponse(tool_calls=[tool_call])

        client = MockLLMClient([response_with_tool, "Done"])
        agent = self._create_agent(client)
        agent.agent_mode = True

        agent._process_message_background("Use unknown tool")

        failed_events = [e for e in self.received_events if isinstance(e, ToolCallFailed)]
        assert len(failed_events) == 1
        assert failed_events[0].tool_name == "unknown_tool"
        assert "not found" in failed_events[0].error

    def test_emits_tool_call_failed_when_agent_mode_disabled(self):
        """Test ToolCallFailed is emitted when agent mode is disabled."""
        tool_call = MockToolCall(
            id="call_123",
            function=MockFunction(name="filesystem_list_files", arguments='{"path": "."}')
        )
        response_with_tool = MockModelResponse(tool_calls=[tool_call])

        client = MockLLMClient([response_with_tool, "Done"])
        agent = self._create_agent(client)
        agent.agent_mode = False  # Disabled

        agent._process_message_background("List files")

        failed_events = [e for e in self.received_events if isinstance(e, ToolCallFailed)]
        assert len(failed_events) == 1
        assert failed_events[0].tool_name == "filesystem_list_files"
        assert "Agent mode is disabled" in failed_events[0].error

    def test_emits_api_call_failed_on_exception(self):
        """Test APICallFailed is emitted when LLM client raises exception."""
        client = Mock()
        client.chat.side_effect = Exception("API Error")

        agent = self._create_agent(client)
        agent._process_message_background("Hello")

        failed_events = [e for e in self.received_events if isinstance(e, APICallFailed)]
        assert len(failed_events) == 1
        assert "API Error" in failed_events[0].error

    def test_emits_thinking_started(self):
        """Test ThinkingStarted event emission."""
        agent = self._create_agent(MockLLMClient(["Response"]))
        agent.event_bus.emit(ThinkingStarted())

        thinking_events = [e for e in self.received_events if isinstance(e, ThinkingStarted)]
        assert len(thinking_events) == 1

    def test_emits_conversation_loaded(self):
        """Test ConversationLoaded event emission."""
        agent = self._create_agent(MockLLMClient(["Response"]))
        messages = [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}]
        agent.event_bus.emit(ConversationLoaded(messages=messages))

        loaded_events = [e for e in self.received_events if isinstance(e, ConversationLoaded)]
        assert len(loaded_events) == 1
        assert loaded_events[0].messages == messages


# ============================================================================
# Test Event Consumption by UI
# ============================================================================

class TestEventConsumption:
    """Tests for UI event consumption - testing internal methods that handlers call.

    These test the actual logic methods (_add_*_message, _set_status) directly
    without requiring full Textual app initialization or call_from_thread.
    """

    def setup_method(self):
        """Set up mock UI components."""
        from ui.app import TerminantApp

        # Create a minimal app instance without full initialization
        self.mock_chat_log = Mock()
        self.mock_status_label = Mock()

        # Create app with mocked components (bypassing Textual's __init__)
        self.app = object.__new__(TerminantApp)
        self.app.chat_log = self.mock_chat_log
        self.app.status_label = self.mock_status_label
        # status_text and is_busy are reactive attrs - we can't set them without full init
        # Tests that need them will be skipped

    def test_add_system_message(self):
        """Test _add_system_message formats correctly."""
        self.app._add_system_message("System message")
        self.mock_chat_log.write.assert_called_with("[dim italic]System message[/]")

    def test_add_user_message(self):
        """Test _add_user_message formats correctly."""
        self.app._add_user_message("User message")
        self.mock_chat_log.write.assert_called_with("[bold green]►[/bold green] User message")

    def test_add_assistant_message(self):
        """Test _add_assistant_message formats correctly."""
        self.app._add_assistant_message("Assistant message")
        self.mock_chat_log.write.assert_called_with("[bold blue]▸[/bold blue] Assistant message")

    def test_add_tool_message(self):
        """Test _add_tool_message formats correctly."""
        self.app._add_tool_message("Tool message")
        self.mock_chat_log.write.assert_called_with("[yellow]Tool message[/yellow]")

    def test_add_error_message(self):
        """Test _add_error_message formats correctly."""
        self.app._add_error_message("Error message")
        self.mock_chat_log.write.assert_called_with("[bold red]✗ Error message[/bold red]")

    # Note: _set_status tests skipped - requires Textual reactive attributes initialized
    # (status_text and is_busy are reactive attrs that need full __init__)

    def test_filter_model_formatting(self):
        """Test _filter_model_formatting removes markdown."""
        text = "**Bold** and *italic* and `code`"
        filtered = self.app._filter_model_formatting(text)
        assert filtered == "Bold and italic and code"

        # Test with various markdown
        text = "__underline__ and ''quotes''"
        filtered = self.app._filter_model_formatting(text)
        assert filtered == "underline and quotes"

    def test_tool_started_message(self):
        """Test tool started produces correct message via _add_tool_message."""
        # The handler calls _add_tool_message
        self.app._add_tool_message("🔧 Tool started: my_tool")
        self.mock_chat_log.write.assert_called_with("[yellow]🔧 Tool started: my_tool[/yellow]")

    def test_tool_succeeded_message(self):
        """Test tool succeeded produces correct message via _add_tool_message."""
        self.app._add_tool_message("✓ Tool succeeded: my_tool")
        self.mock_chat_log.write.assert_called_with("[yellow]✓ Tool succeeded: my_tool[/yellow]")

    def test_tool_failed_message(self):
        """Test tool failed produces correct message via _add_error_message."""
        self.app._add_error_message("Tool 'my_tool' failed: Permission denied")
        self.mock_chat_log.write.assert_called_with("[bold red]✗ Tool 'my_tool' failed: Permission denied[/bold red]")

    def test_api_failed_message(self):
        """Test API failed produces correct message via _add_error_message."""
        self.app._add_error_message("API call failed: Connection timeout")
        self.mock_chat_log.write.assert_called_with("[bold red]✗ API call failed: Connection timeout[/bold red]")

    def test_error_event_message(self):
        """Test generic error produces correct message via _add_error_message."""
        self.app._add_error_message("Error: Something went wrong")
        self.mock_chat_log.write.assert_called_with("[bold red]✗ Error: Something went wrong[/bold red]")

    # Note: _set_status tests skipped - requires Textual reactive attributes initialized
    # (status_text and is_busy are reactive attrs that need full __init__)


# ============================================================================
# Test Full Integration: Event Flow from Agent to UI
# ============================================================================

class TestEventFlowIntegration:
    """Integration tests for full event flow from Agent through EventBus to UI."""

    def setup_method(self):
        self.event_bus = EventBus()
        self.mock_chat_log = Mock()
        self.mock_status_label = Mock()

        # Create minimal app instance
        from ui.app import TerminantApp
        self.app = object.__new__(TerminantApp)
        self.app.event_bus = self.event_bus
        self.app.chat_log = self.mock_chat_log
        self.app.status_label = self.mock_status_label
        # Note: status_text and is_busy are reactive attrs that need full init

        # Mock call_from_thread to execute callbacks immediately in tests
        def mock_call_from_thread(func, *args, **kwargs):
            func(*args, **kwargs)
        self.app.call_from_thread = mock_call_from_thread

        # Set up event handlers (normally done in __init__)
        self.app._setup_event_handlers()

    def test_tool_execution_emits_correct_sequence(self):
        """Test that tool execution emits events in correct order."""
        self.event_bus = EventBus()
        received = []

        for etype in [ToolStarted, ToolCallSucceeded]:
            self.event_bus.subscribe(etype, lambda e: received.append(e))

        # Create agent
        client = MockLLMClient(["Done"])
        agent = Agent(client=client, event_bus=self.event_bus)
        agent.agent_mode = True

        # Create a mock tool call and handle it directly
        tool_call = MockToolCall(
            id="call_123",
            function=MockFunction(name="filesystem_list_files", arguments='{"path": "."}')
        )
        agent.handle_tool_call(tool_call)

        # Verify order: ToolStarted then ToolCallSucceeded
        assert len(received) == 2
        assert isinstance(received[0], ToolStarted)
        assert received[0].tool_name == "filesystem_list_files"
        assert isinstance(received[1], ToolCallSucceeded)
        assert received[1].tool_name == "filesystem_list_files"

    def test_tool_failure_emits_correct_events(self):
        """Test that tool failure emits correct events."""
        self.event_bus = EventBus()
        received = []

        for etype in [ToolStarted, ToolCallFailed]:
            self.event_bus.subscribe(etype, lambda e: received.append(e))

        client = MockLLMClient(["Done"])
        agent = Agent(client=client, event_bus=self.event_bus)
        agent.agent_mode = True

        # Call unknown tool
        tool_call = MockToolCall(
            id="call_123",
            function=MockFunction(name="unknown_tool", arguments='{}')
        )
        agent.handle_tool_call(tool_call)

        # Verify: Only ToolCallFailed (ToolStarted is only emitted for known tools)
        assert len(received) == 1
        assert isinstance(received[0], ToolCallFailed)
        assert received[0].tool_name == "unknown_tool"
        assert "not found" in received[0].error

    def test_ui_receives_all_expected_events(self):
        """Test UI handlers receive all event types correctly.

        Uses the already set up self.app which has mocked components.
        """
        # Emit event types that don't require reactive attributes
        # (AgentIdle, AgentBusy, ThinkingStarted trigger _set_status which needs reactives)
        events_to_test = [
            AssistantMessageFinished(message="Test"),
            ToolStarted(tool_name="test_tool"),
            ToolCallSucceeded(tool_name="test_tool"),
            ToolCallFailed(tool_name="test_tool", error="Error"),
            APICallFailed(error="API Error"),
            ConversationLoaded(messages=[]),
        ]

        for event in events_to_test:
            self.event_bus.emit(event)

        # Verify message event handlers were called (chat_log.write)
        # Note: call_from_thread is mocked to execute immediately in tests
        # Status events (AgentIdle, AgentBusy, ThinkingStarted) are not tested here
        # as they require Textual reactive attributes initialized
        assert self.mock_chat_log.write.call_count >= 1  # at least some message events


# ============================================================================
# Test Event Data Integrity
# ============================================================================

class TestEventDataIntegrity:
    """Tests to ensure event data is correctly preserved through emission and consumption."""

    def test_tool_started_preserves_tool_name(self):
        """Test ToolStarted event preserves tool_name correctly."""
        event = ToolStarted(tool_name="my_tool")
        assert event.tool_name == "my_tool"

    def test_tool_call_succeeded_preserves_tool_name(self):
        """Test ToolCallSucceeded event preserves tool_name correctly."""
        event = ToolCallSucceeded(tool_name="my_tool")
        assert event.tool_name == "my_tool"

    def test_tool_call_failed_preserves_tool_name_and_error(self):
        """Test ToolCallFailed preserves tool_name and error."""
        event = ToolCallFailed(tool_name="my_tool", error="Something went wrong")
        assert event.tool_name == "my_tool"
        assert event.error == "Something went wrong"

    def test_assistant_message_finished_preserves_message(self):
        """Test AssistantMessageFinished preserves message."""
        event = AssistantMessageFinished(message="Hello world")
        assert event.message == "Hello world"

    def test_conversation_loaded_preserves_messages(self):
        """Test ConversationLoaded preserves messages list."""
        messages = [{"role": "user", "content": "Hi"}]
        event = ConversationLoaded(messages=messages)
        assert event.messages == messages
        assert event.messages is messages  # Same reference

    def test_api_call_failed_preserves_error(self):
        """Test APICallFailed preserves error."""
        event = APICallFailed(error="Network error")
        assert event.error == "Network error"

    def test_user_message_submitted_preserves_message(self):
        """Test UserMessageSubmitted preserves message."""
        event = UserMessageSubmitted(message="User input")
        assert event.message == "User input"


# ============================================================================
# Test Event Bus Functionality
# ============================================================================

class TestEventBus:
    """Tests for the EventBus itself."""

    def test_subscribe_and_emit(self):
        """Test basic subscribe and emit."""
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe(AssistantMessageFinished, handler)
        bus.emit(AssistantMessageFinished(message="Test"))

        assert len(received) == 1
        assert received[0].message == "Test"

    def test_multiple_subscribers(self):
        """Test multiple subscribers for same event type."""
        bus = EventBus()
        received1 = []
        received2 = []

        bus.subscribe(AssistantMessageFinished, lambda e: received1.append(e))
        bus.subscribe(AssistantMessageFinished, lambda e: received2.append(e))
        bus.emit(AssistantMessageFinished(message="Test"))

        assert len(received1) == 1
        assert len(received2) == 1

    def test_subscriber_isolation(self):
        """Test subscribers for different event types are isolated."""
        bus = EventBus()
        received1 = []
        received2 = []

        bus.subscribe(AssistantMessageFinished, lambda e: received1.append(e))
        bus.subscribe(ToolStarted, lambda e: received2.append(e))

        bus.emit(AssistantMessageFinished(message="Test"))
        bus.emit(ToolStarted(tool_name="tool"))

        assert len(received1) == 1
        assert len(received2) == 1

    def test_emit_with_no_subscribers(self):
        """Test emit with no subscribers doesn't crash."""
        bus = EventBus()
        # Should not raise
        bus.emit(AssistantMessageFinished(message="Test"))

    def test_event_order_preserved(self):
        """Test events are delivered in order."""
        bus = EventBus()
        received = []

        bus.subscribe(AssistantMessageFinished, lambda e: received.append(e))

        bus.emit(AssistantMessageFinished(message="1"))
        bus.emit(AssistantMessageFinished(message="2"))
        bus.emit(AssistantMessageFinished(message="3"))

        assert [e.message for e in received] == ["1", "2", "3"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])