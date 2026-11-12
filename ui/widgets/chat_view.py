# ui/widgets/chat_view.py
from textual.widgets import Static
from rich.markup import escape
from events.event_bus import EventBus
from events.events import (
    UserMessageSubmitted,
    AssistantMessageFinished,
    StreamingToken,
    ConversationLoaded,
)
from ui.widgets.base import AgentWidget

class ChatView(AgentWidget):
    """Displays the conversation. Reactive only—listens to events."""
    
    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(event_bus, **kwargs)
        self.messages = []
        self.message_display = None

    def compose(self):
        """Yield child widgets."""
        self.message_display = Static(id="message-display", markup=True)
        yield self.message_display
    
    def on_mount(self) -> None:
        """Set up event subscriptions."""
        self.subscribe(UserMessageSubmitted, self._on_user_message)
        self.subscribe(AssistantMessageFinished, self._on_assistant_message)
        self.subscribe(StreamingToken, self._on_streaming_token)
        self.subscribe(ConversationLoaded, self._on_conversation_loaded)

        if self.message_display:
            self.message_display.update(
                "[b]Terminant[/b]\nType a message below to start the conversation."
            )

    #handlers
    def _on_user_message(self, event: UserMessageSubmitted) -> None:
        self.messages.append(("user", event.message))
        self._render_messages()
    
    def _on_assistant_message(self, event: AssistantMessageFinished) -> None:
        self.messages.append(("assistant", event.message))
        self._render_messages()
    
    def _on_streaming_token(self, event: StreamingToken) -> None:
        if self.messages and self.messages[-1][0] == "assistant":
            role, text = self.messages[-1]
            self.messages[-1] = (role, text + event.token)
            self._render_messages()
    
    def _on_conversation_loaded(self, event: ConversationLoaded) -> None:
        self.messages = event.messages
        self._render_messages()
    
    def _render_messages(self) -> None:
        content = ""
        for role, text in self.messages:
            if role == "user":
                content += f"[on #3a3a3a]> {escape(text)}[/]\n\n"
            else:
                content += f"[b]• {text}[/b]\n\n"

        if not content:
            content = "Terminant\n\nType a message below to start the conversation."
        
        if self.message_display:
            self.message_display.update(content)