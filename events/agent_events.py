from dataclasses import dataclass
from tools.base import Tool

@dataclass
class AgentEvent:
    """Base class for all agent events."""
    ...

@dataclass
class ErrorEvent(AgentEvent):
    """Base class for error events."""
    ...
    error: str

@dataclass
class StreamingToken(AgentEvent):
    token: str

@dataclass
class UserMessageSubmitted(AgentEvent):
    message: str


class ThinkingStarted(AgentEvent):
    pass

@dataclass
class AssistantMessageFinished(AgentEvent):
    message: str

@dataclass
class ToolStarted(AgentEvent):
    tool_name: str

@dataclass
class ToolCallSucceeded(AgentEvent):
    tool_name: str


class AgentIdle(AgentEvent):
    pass


class AgentBusy(AgentEvent):
    pass

@dataclass
class ConversationLoaded(AgentEvent):
    messages: list

@dataclass
class ToolCallFailed(ErrorEvent):
    tool_name: str

@dataclass
class APICallFailed(ErrorEvent):
    pass