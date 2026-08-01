from openai import OpenAI
from config.config import DEFAULT_MODEL, COMMON_FREE_MODELS
from logger import log_info
from tools.registry import tool_registry

class LLMClient:
    def __init__(self, api_key=None, model=COMMON_FREE_MODELS[1]):
        self.api_key = api_key
        self.model = model

    def chat(self, messages):
        if not messages:
            raise ValueError("no messages has been provided")

        if not self.api_key:
            return "Model client not configured: set OPENROUTER_API_KEY to enable API calls."

        response = self._call_api(messages)
        return response

    def _call_api(self, messages):
        while True:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )

            check_mode_tool = {
                "type": "function",
                "function": {
                    "name": "agent.check_mode",
                    "description": "Checks if agent mode is enabled or not",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
            }

            tools=[tool.to_openai_schema() for tool in tool_registry.values()]
            tools.append(check_mode_tool)

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools
            )

            if response.choices != None:
                return response.choices[0].message

