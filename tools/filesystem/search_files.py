import glob
import os

from tools.base import Tool
from logger import log_info


class SearchFiles(Tool):
    @property
    def name(self):
        return "filesystem.search_files"

    @property
    def description(self):
        return "Search for files recursively using a glob pattern"

    @property
    def arguments(self):
        return {
            "path": {
                "type": "string",
                "description": "Directory path to search under."
            },
            "pattern": {
                "type": "string",
                "description": "Glob pattern to match filenames."
            }
        }

    def execute(self, **kwargs):
        path = kwargs.get("path", ".")
        pattern = kwargs.get("pattern", "*")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(path={path!r}, pattern={pattern!r})")

        try:
            matches = glob.glob(os.path.join(path, "**", pattern), recursive=True)
            self.log_tool_result(self.name, f"{len(matches)} matches")
            return matches
        except FileNotFoundError:
            error = f"Error: Path '{path}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{path}'"
            self.log_tool_result(self.name, error)
            return error