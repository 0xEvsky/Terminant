from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from events.event_bus import EventBus
from events.agent_events import ConversationLoaded
from ui.widgets.chat_view import ChatView
from ui.widgets.input_bar import InputBar

class TerminantApp(App):
    """The root UI application. Owns the event loop and widget tree."""
    
    def __init__(self, event_bus: EventBus, memory_store=None, **kwargs):
        super().__init__(**kwargs)
        self.event_bus = event_bus
        self.memory_store = memory_store
    
    def on_mount(self) -> None:
        """Called when the app starts. Load conversation history."""
        #TODO: past_messages = self.memory_store.load_conversation()
        
        self.event_bus.emit(ConversationLoaded(messages=['']))
    
    def compose(self) -> ComposeResult:
        """Yield the widget tree."""
        # Main container
        with Vertical(id="app-container"):
            # Chat display area
            yield ChatView(event_bus=self.event_bus, id="chat-view")
            
            # Input bar at bottom
            yield InputBar(event_bus=self.event_bus, id="input-bar")
    
    def on_unmount(self) -> None:
        """Called when app closes. Save conversation history."""
        # We'll implement this after we see how ChatView stores messages
        pass