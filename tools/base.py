from dataclasses import asdict, dataclass
from typing import Any

from logger import log_info


@dataclass
class ToolResult:
    success: bool
    output: Any = None
    error: str | None = None

    def to_dict(self):
        return asdict(self)

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

    def execute(self, **kwargs) -> ToolResult:
        ...

    def validate_arguments(self, arguments: dict) -> bool:
        required_args = set(self.arguments.keys())
        provided_args = set(arguments.keys())
        missing_args = required_args - provided_args
        if missing_args:
            raise ValueError(f"Missing required arguments: {', '.join(missing_args)}")

        unexpected_args = provided_args - required_args
        if unexpected_args:
            raise ValueError(f"Unexpected arguments: {', '.join(unexpected_args)}") 

        return True

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
