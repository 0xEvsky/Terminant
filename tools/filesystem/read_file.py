from pathlib import Path

from tools.base import Tool
from logger import log_info


class ReadFile(Tool):
    @property
    def name(self):
        return "filesystem.read_file"

    @property
    def description(self):
        return "Read a file as text"

    @property
    def arguments(self):
        return {
            "path": {
                "type": "string",
                "description": "File path to read."
            }
        }

    def execute(self, **kwargs):
        path = kwargs.get("path", "")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(path={path!r})")

        try:
            content = Path(path).read_text(encoding="utf-8")
            self.log_tool_result(self.name, f"{len(content)} characters")
            return content
        except FileNotFoundError:
            error = f"Error: File '{path}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{path}'"
            self.log_tool_result(self.name, error)
            return error