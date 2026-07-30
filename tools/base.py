from logger import log_info

class Tool:
    @property
    def name(self):
        ...
    @property
    def description(self):
        ...

    @property
    def arguments(self):
        ...

    def execute(self, **kwargs):
        ...

    def to_openai_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.arguments,
                    "required": list(self.arguments.keys()),
                },
            },
        }

    def log_tool_call(self, name: str, kwargs: dict):
        details = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        if details:
            log_info(f"Tool requested: {name}({details})")
        else:
            log_info(f"Tool requested: {name}")

    def log_tool_result(self, name: str, result):
        log_info(f"Tool returned {result}")
