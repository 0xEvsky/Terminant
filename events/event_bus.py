from collections import defaultdict
from events.agent_events import AgentEvent
from logger import log_info

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: type[AgentEvent], callback: callable):
        self.subscribers[event_type].append(callback)
    
    def emit(self, event: AgentEvent):
        log_info(f'Event emit: {event}')
        event_subscribers = self.subscribers[type(event)]
        for callback in event_subscribers:
            callback(event)