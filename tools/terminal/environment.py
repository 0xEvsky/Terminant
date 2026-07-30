import os

from tools.base import Tool
from logger import log_info


class Environment(Tool):
    @property
    def name(self):
        return "terminal.environment"

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
            return environment
        except FileNotFoundError:
            error = "Error: Environment not available"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = "Error: Permission denied reading environment"
            self.log_tool_result(self.name, error)
            return error