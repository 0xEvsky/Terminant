from llm.client import LLMClient
from events.event_bus import EventBus
from agent.agent import Agent
from config.config import API_KEY
from logger import start_run_logging, stop_run_logging
from ui.app import TerminantApp

event_bus = EventBus()
client = LLMClient(api_key=API_KEY)
agent = Agent(client=client, event_bus=event_bus)
app = TerminantApp(event_bus=event_bus)

start_run_logging()
try:
	app.run()
finally:
	stop_run_logging()
