from pathlib import Path

from tools.base import Tool
from logger import log_info


class CreateDirectory(Tool):
    @property
    def name(self):
        return "filesystem.create_directory"

    @property
    def description(self):
        return "Create a directory recursively"

    @property
    def arguments(self):
        return {
            "path": {
                "type": "string",
                "description": "Directory path to create."
            }
        }

    def execute(self, **kwargs):
        path = kwargs.get("path", "")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(path={path!r})")

        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            result = f"Directory '{path}' created successfully"
            self.log_tool_result(self.name, result)
            return result
        except FileNotFoundError:
            error = f"Error: Path '{path}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{path}'"
            self.log_tool_result(self.name, error)
            return error