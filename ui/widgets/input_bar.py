# ui/widgets/input_bar.py
from collections.abc import Callable

from textual import events
from textual.containers import Horizontal
from textual.widgets import Static
from textual.widgets import TextArea
from events.event_bus import EventBus
from events.agent_events import UserMessageSubmitted, AgentBusy, AgentIdle
from ui.widgets.base import AgentWidget


class PromptTextArea(TextArea):
    """Text area that submits on Enter while retaining Shift+Enter for newlines."""

    def __init__(self, on_submit: Callable[[], None], **kwargs):
        super().__init__(**kwargs)
        self._on_submit = on_submit

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            event.stop()
            event.prevent_default()
            self._on_submit()
            return

        await super()._on_key(event)


class InputBar(AgentWidget):
    """Captures user input and emits events."""
    
    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(event_bus, **kwargs)
        self.input_widget = PromptTextArea(
            on_submit=self._submit_message,
            id="user-input",
            soft_wrap=True,
            compact=True,
        )
        self.prompt_symbol = Static(">", id="prompt-symbol")

    def compose(self):
        with Horizontal(id="input-row"):
            yield self.prompt_symbol
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
        self.input_widget.focus()
    
    def _submit_message(self) -> None:
        message = self.input_widget.text.strip()

        if message:
            self.event_bus.emit(UserMessageSubmitted(message=message))
            self.input_widget.text = ""
            self.input_widget.focus()