from llm.client import LLMClient
from agent.memory import Memory

class Agent:
    def __init__(self, client: LLMClient):
        self.client: LLMClient = client
        self.memory = Memory()

    def step(self, messages):
        self.memory.add_user_message(messages)
        messages = self.memory.get_messages()
        model_response = self.client.chat(messages=messages)
        self.memory.add_assistant_message(model_response)
        return model_response
        
