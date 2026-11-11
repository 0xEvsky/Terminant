import os

from tools.base import Tool, ToolResult
from logger import log_info


class Environment(Tool):
    @property
    def name(self):
        return "terminal_environment"

    @property
    def description(self):
        return "Get the current terminal environment"

    @property
    def arguments(self):
        return {}

    def execute(self, **kwargs):
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}()")

        try:
            environment = dict(os.environ)
            self.log_tool_result(self.name, f"{len(environment)} environment variables")
            return ToolResult(True, environment)
        except FileNotFoundError:
            error = "Error: Environment not available"
            self.log_tool_result(self.name, error)
            return ToolResult(False, error, error)
        except PermissionError:
            error = "Error: Permission denied reading environment"
            self.log_tool_result(self.name, error)
            return ToolResult(False, error, error)