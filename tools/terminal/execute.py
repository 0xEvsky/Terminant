import subprocess

from tools.base import Tool
from logger import log_info


class Execute(Tool):
    @property
    def name(self):
        return "terminal.execute"

    @property
    def description(self):
        return "Execute a terminal command"

    @property
    def arguments(self):
        return {
            "command": {
                "type": "string",
                "description": "Shell command to execute."
            }
        }

    def execute(self, **kwargs):
        command = kwargs.get("command", "")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(command={command!r})")

        try:
            completed = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = completed.stdout.strip()
            error_output = completed.stderr.strip()

            if completed.returncode != 0:
                error = error_output or output or f"Command failed with exit code {completed.returncode}"
                self.log_tool_result(self.name, error)
                return error

            result = output or "Command executed successfully"
            self.log_tool_result(self.name, result)
            return result
        except FileNotFoundError:
            error = f"Error: Command '{command}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{command}'"
            self.log_tool_result(self.name, error)
            return error