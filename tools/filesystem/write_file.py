from pathlib import Path

from tools.base import Tool, ToolResult
from logger import log_info


class WriteFile(Tool):
    @property
    def name(self):
        return "filesystem_write_file"

    @property
    def description(self):
        return "Write text to a file"

    @property
    def arguments(self):
        return {
            "path": {
                "type": "string",
                "description": "File path to write."
            },
            "content": {
                "type": "string",
                "description": "Text content to write to the file."
            }
        }

    def execute(self, **kwargs):
        path = kwargs.get("path", "")
        content = kwargs.get("content", "")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(path={path!r})")

        try:
            Path(path).write_text(content, encoding="utf-8")
            result = f"File '{path}' written successfully"
            self.log_tool_result(self.name, result)
            return ToolResult(True, result)
        except FileNotFoundError:
            error = f"Error: Path '{path}' not found"
            self.log_tool_result(self.name, error)
            return ToolResult(False, error, error)
        except PermissionError:
            error = f"Error: Permission denied for '{path}'"
            self.log_tool_result(self.name, error)
            return ToolResult(False, error, error)