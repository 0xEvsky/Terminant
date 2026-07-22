from llm.client import LLMClient

class Agent:
    def __init__(self, client: LLMClient):
        self.client: LLMClient = client

    def step(self, prompt):
        return self.client.chat(prompt)