from llm.client import LLMClient
from agent.agent import Agent
from agent.loop import runAgentLoop
import os

api_key = os.getenv("OPENROUTER_API_KEY")
client = LLMClient(api_key=api_key)
agent = Agent(client=client)

runAgentLoop(agent=agent)