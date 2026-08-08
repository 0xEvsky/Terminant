# ui/widgets/input_bar.py
from textual.widgets import Input
from events.event_bus import EventBus
from events.agent_events import UserMessageSubmitted, AgentBusy, AgentIdle
from ui.widgets.base import AgentWidget

class InputBar(AgentWidget):
    """Captures user input and emits events."""
    
    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(event_bus, **kwargs)
        self.input_widget = Input(id="user-input", placeholder="Type your message...")
    
    def compose(self):
        yield self.input_widget
    
    def on_mount(self) -> None:
        self.subscribe(AgentBusy, self._on_agent_busy)
        self.subscribe(AgentIdle, self._on_agent_idle)

    def _on_agent_busy(self, event: AgentBusy) -> None:
        """Agent is thinking—disable input."""
        self.input_widget.disabled = True
    
    def _on_agent_idle(self, event: AgentIdle) -> None:
        """Agent done—enable input."""
        self.input_widget.disabled = False
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        
        if message:
            self.event_bus.emit(UserMessageSubmitted(message=message))
            self.input_widget.value = ""