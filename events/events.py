"""Event definitions for the Terminant application.

This module contains all event classes used for communication between
the Agent, UI, and other components via the EventBus.

Events are organized into categories:
- Base Events: Core event hierarchy
- Message Events: User/assistant message lifecycle
- Tool Events: Tool execution lifecycle
- State Events: Agent state changes (busy/idle)
- Error Events: Error reporting
- Control Events: Mode changes and conversation management
"""

from dataclasses import dataclass
from tools.base import Tool
from agent.modes import AgentMode


@dataclass
class Event:
    """Base class for all events in the system.

    All event types should inherit from this class to ensure
    consistent handling by the EventBus.
    """
    ...


@dataclass
class ErrorEvent(Event):
    """Base class for all error events.

    Attributes:
        error: Human-readable error message describing what went wrong.
    """
    error: str


@dataclass
class StreamingToken(Event):
    """Emitted for each token received during streaming response from the LLM.

    Used to display incremental assistant output in real-time.

    Attributes:
        token: A single token/character from the streaming response.
    """
    token: str


@dataclass
class UserMessageSubmitted(Event):
    """Emitted when the user submits a message in the chat input.

    This event triggers the agent to process the user's message
    and generate a response.

    Attributes:
        message: The raw text content of the user's message.
    """
    message: str


class ThinkingStarted(Event):
    """Emitted when the agent begins processing/thinking.

    This event signals the start of agent processing, typically used
    to show a "thinking" indicator in the UI.
    """
    pass


@dataclass
class AssistantMessageFinished(Event):
    """Emitted when the assistant completes generating a response.

    This event contains the full completed message and is used
    to add the final assistant message to the chat history.

    Attributes:
        message: The complete assistant response message.
    """
    message: str


@dataclass
class ToolStarted(Event):
    """Emitted when a tool execution begins.

    Used to notify the UI that a tool is starting, allowing
    display of a "tool running" indicator.

    Attributes:
        tool_name: The name of the tool being executed.
    """
    tool_name: str


@dataclass
class ToolCallSucceeded(Event):
    """Emitted when a tool execution completes successfully.

    Used to notify the UI that a tool finished without errors.

    Attributes:
        tool_name: The name of the tool that succeeded.
    """
    tool_name: str


class AgentIdle(Event):
    """Emitted when the agent becomes idle (finished processing).

    Signals that the agent is ready to accept new user input.
    Used to update UI status indicators.
    """
    pass


class AgentBusy(Event):
    """Emitted when the agent starts processing (becomes busy).

    Signals that the agent is currently working and not ready
    for new input. Used to update UI status indicators.
    """
    pass


@dataclass
class ConversationLoaded(Event):
    """Emitted when conversation history is loaded from storage.

    Contains the full message history to be displayed in the chat.

    Attributes:
        messages: List of message dictionaries with 'role' and 'content' keys.
                  Typically loaded from a JSON file or database.
    """
    messages: list


@dataclass
class ToolCallFailed(ErrorEvent):
    """Emitted when a tool execution fails.

    Provides details about which tool failed and why.

    Attributes:
        tool_name: The name of the tool that failed.
        error: Description of the failure reason (inherited from ErrorEvent).
    """
    tool_name: str


@dataclass
class APICallFailed(ErrorEvent):
    """Emitted when an API call to the LLM provider fails.

    Used for network errors, rate limits, authentication failures,
    or other API-level issues.

    Attributes:
        error: Description of the API failure (inherited from ErrorEvent).
    """
    pass


@dataclass
class AgentModeChangeRequested(Event):
    """Emitted when a request is made to change the agent's operating mode.

    This event is typically emitted by the UI when the user selects
    a different mode (e.g., switching between chat and agent mode).

    Attributes:
        new_mode: The AgentMode enum value representing the requested mode.
    """
    new_mode: AgentMode


@dataclass
class ChangeAgentMode(Event):
    """Emitted when the agent's operating mode has actually changed.

    This event confirms the mode change has been applied and
    is typically emitted by the agent after processing the request.

    Attributes:
        new_mode: The AgentMode enum value of the newly active mode.
    """
    new_mode: AgentMode