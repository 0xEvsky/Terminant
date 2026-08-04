from llm.client import LLMClient
from events.event_bus import EventBus
from agent.agent import Agent
from agent.loop import runAgentLoop
from config.config import API_KEY

client = LLMClient(api_key=API_KEY)
agent = Agent(client=client, event_bus=EventBus())

runAgentLoop(agent=agent)
