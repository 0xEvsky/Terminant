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
        self.agent_mode = False

    def step(self, messages=None):
        log_info(f"User: {messages}")
        if messages:
            self.memory.add_user_message(messages)

        while True:
            log_info("Sending messages to model")
            model_response = self.client.chat(messages=self.memory.get_messages())
            log_info("Model responded")

            if model_response.tool_calls:
                self.handle_tool_call(model_response)
                # log_info(f'Tool call.. Memory: {self.memory.messages[1:]}')
                continue
            
            response = model_response.content    
            self.memory.add_assistant_message(response)

            log_info("Final response generated")
            # log_info(f'Normal response.. Memory: {self.memory.messages[1:]}')

            return response


    def handle_tool_call(self, model_response):
        tool_call = model_response.tool_calls[0]
        tool_call_id = tool_call.id
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        self.memory.add_tool_call(id=tool_call_id, name=tool_name, arguments=tool_call.function.arguments)
        
        log_info(f'called tool: {tool_name}')
        log_info(f'arguments: {arguments}')

        result = 'NO RESULT'

        if tool_name == 'agent.check_mode':
            result = self.check_agent_mode()

        elif self.agent_mode:
            tool = get_tool(tool_name)
            
            result = tool.execute(**arguments)

        log_info(tool_call_id)
        self.memory.add_tool_result(tool_call_id=tool_call_id, content=json.dumps(result))


    def check_agent_mode(self) -> dict:
        return {"agent_mode": self.agent_mode}
        
        
