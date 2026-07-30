import json
from llm.client import LLMClient
from agent.memory import Memory
from llm.prompts import SYSTEM_PROMPT
from logger import log_info
from tools.registry import get_tool
from tools.base import Tool


class Agent:
    def __init__(self, client: LLMClient):
        self.client: LLMClient = client
        self.memory = Memory()
        self.memory.add_system_message(SYSTEM_PROMPT)

    def step(self, messages):
        log_info(f"User: {messages}")
        self.memory.add_user_message(messages)
        messages = self.memory.get_messages()

        log_info("Sending messages to model")
        model_response = self.client.chat(messages=messages)
        log_info("Model responded")

        response_content = ''


        if model_response["is_tool_call"]:
            tool: Tool = get_tool(model_response['tool'])
            arguments = model_response['arguments']

            log_info(f'parsed tool: {tool.name}')
            log_info(f'parsed arguments: {arguments}')

            result = tool.execute(**arguments)
            return result
        else:
            response_content = model_response["message"]
            self.memory.add_assistant_message(response_content)
            log_info("Final response generated")
            log_info(self.memory.messages[1:])
            return response_content

        
        
