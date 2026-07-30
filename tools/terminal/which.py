import shutil

from tools.base import Tool
from logger import log_info


class Which(Tool):
    @property
    def name(self):
        return "terminal.which"

    @property
    def description(self):
        return "Find the path to an executable"

    @property
    def arguments(self):
        return {
            "command": {
                "type": "string",
                "description": "Command or executable name to locate."
            }
        }

    def execute(self, **kwargs):
        command = kwargs.get("command", "")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(command={command!r})")

        try:
            path = shutil.which(command)
            if path is None:
                error = f"Error: Command '{command}' not found"
                self.log_tool_result(self.name, error)
                return error

            self.log_tool_result(self.name, path)
            return path
        except FileNotFoundError:
            error = f"Error: Command '{command}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{command}'"
            self.log_tool_result(self.name, error)
            return error