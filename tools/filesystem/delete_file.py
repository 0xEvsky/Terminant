from pathlib import Path

from tools.base import Tool
from logger import log_info


class DeleteFile(Tool):
    @property
    def name(self):
        return "filesystem.delete_file"

    @property
    def description(self):
        return "Delete a file"

    @property
    def arguments(self):
        return {
            "path": {
                "type": "string",
                "description": "File path to delete."
            }
        }

    def execute(self, **kwargs):
        path = kwargs.get("path", "")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(path={path!r})")

        try:
            Path(path).unlink()
            result = f"File '{path}' deleted successfully"
            self.log_tool_result(self.name, result)
            return result
        except FileNotFoundError:
            error = f"Error: File '{path}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{path}'"
            self.log_tool_result(self.name, error)
            return error