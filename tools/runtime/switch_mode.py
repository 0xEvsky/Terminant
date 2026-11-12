from tools.base import Tool
from agent.modes import AgentMode, ManualMode
from events.event_bus import EventBus
from events.events import ChangeAgentMode

class SwitchMode(Tool):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    @property
    def name(self):
        return 'Mode'

    @property
    def description(self):
        return 'Switches agent mode to <mode>'

    @property
    def arguments(self):
        return {
            "mode": {
                "type": "string"
            }
        }

    def execute(self, **kwargs):
        self.log_tool_call(self.name, kwargs)
        new_mode: AgentMode = kwargs.get('new_mode', ManualMode())