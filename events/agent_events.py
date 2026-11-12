from dataclasses import dataclass
from tools.base import Tool
from agent.modes import AgentMode

@dataclass
class Event:
    """Base class for all events."""
    ...

@dataclass
class ErrorEvent(Event):
    """Base class for error events."""
    ...
    error: str

@dataclass
class StreamingToken(Event):
    token: str

@dataclass
class UserMessageSubmitted(Event):
    message: str


class ThinkingStarted(Event):
    pass

@dataclass
class AssistantMessageFinished(Event):
    message: str

@dataclass
class ToolStarted(Event):
    tool_name: str

@dataclass
class ToolCallSucceeded(Event):
    tool_name: str


class AgentIdle(Event):
    pass


class AgentBusy(Event):
    pass

@dataclass
class ConversationLoaded(Event):
    messages: list

@dataclass
class ToolCallFailed(ErrorEvent):
    tool_name: str

@dataclass
class APICallFailed(ErrorEvent):
    pass

class ChangeMode(Event):
    new_mode: AgentMode