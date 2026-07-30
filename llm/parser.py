import json
from logger import log_info

class ToolCallParser:
    @staticmethod
    def parse(response: str) -> dict:
        try:
            data = json.loads(response)
            if data.get("type") == "tool_call":
                log_info('Parsed agent response as tool_call')
                return {
                    "is_tool_call": True,
                    "tool": data["tool"],
                    "arguments": data["arguments"]
                }
            else:
                log_info('Parsed agent response as message')
                return {"is_tool_call": False, "message": data["content"]}
        except json.JSONDecodeError:
            log_info('Response parsing failed')
            return {"is_tool_call": False, "message": response}