from datetime import datetime
from pathlib import Path

from tools.base import Tool
from logger import log_info


class FileInfo(Tool):
    @property
    def name(self):
        return "filesystem.file_info"

    @property
    def description(self):
        return "Get information about a file or directory"

    @property
    def arguments(self):
        return {
            "path": {
                "type": "string",
                "description": "File or directory path to inspect."
            }
        }

    def execute(self, **kwargs):
        path = kwargs.get("path", ".")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(path={path!r})")

        try:
            target = Path(path)
            stats = target.stat()
            result = {
                "name": target.name,
                "path": str(target),
                "is_file": target.is_file(),
                "is_directory": target.is_dir(),
                "size": stats.st_size,
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            }
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