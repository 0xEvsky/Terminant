import os
from pathlib import Path

from tools.base import Tool
from logger import log_info


class ListFiles(Tool):
    @property
    def name(self):
        return "filesystem.list_files"

    @property
    def description(self):
        return "List files in a specific path"

    @property
    def arguments(self):
        return {
            "path": {
                "type": "string",
                "description": "Directory path to list files from."
            }
        }

    def execute(self, **kwargs):
        path = kwargs.get("path", ".")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(path={path!r})")

        try:
            files = os.listdir(path)
            self.log_tool_result(self.name, f"{len(files)} files")
            return files
        except FileNotFoundError:
            error = f"Error: Path '{path}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{path}'"
            self.log_tool_result(self.name, error)
            return error