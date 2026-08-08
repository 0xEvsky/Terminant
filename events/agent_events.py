from dataclasses import dataclass
from tools.base import Tool

@dataclass
class AgentEvent:
    """Base class for all agent events."""
    ...

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
    tool: Tool

@dataclass
class ToolFinished(AgentEvent):
    tool: Tool


class AgentIdle(AgentEvent):
    pass


class AgentBusy(AgentEvent):
    pass

@dataclass
class AgentError(AgentEvent):
    error: str

@dataclass
class ConversationLoaded(AgentEvent):
    messages: list