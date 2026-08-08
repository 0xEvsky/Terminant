from textual.widget import Widget
from events.event_bus import EventBus
from events.agent_events import AgentEvent

class AgentWidget(Widget):
    def __init__(self, event_bus: EventBus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus = event_bus
        self._subscriptions = []

    def subscribe(self, event_type: type[AgentEvent], handler: callable):
        """Subscribe to an event type.
        
        Args:
            event_type: The AgentEvent subclass to listen for
            handler: Callable that receives the event
        """
        self.event_bus.subscribe(event_type, handler)
        self._subscriptions.append((event_type, handler))

    def on_mount(self) -> None:
        """Called when widget is added to the widget tree."""
        pass

    def on_unmount(self) -> None:
        """Called when widget is removed from the widget tree."""
        # Unsubscribe from all events
        # (Optional: EventBus would need an unsubscribe method)
        pass
