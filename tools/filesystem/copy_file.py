from pathlib import Path
import shutil

from tools.base import Tool
from logger import log_info


class CopyFile(Tool):
    @property
    def name(self):
        return "filesystem.copy_file"

    @property
    def description(self):
        return "Copy a file"

    @property
    def arguments(self):
        return {
            "source": {
                "type": "string",
                "description": "Source file path."
            },
            "destination": {
                "type": "string",
                "description": "Destination file path."
            }
        }

    def execute(self, **kwargs):
        source = kwargs.get("source", "")
        destination = kwargs.get("destination", "")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(source={source!r}, destination={destination!r})")

        try:
            shutil.copy2(str(Path(source)), str(Path(destination)))
            result = f"File copied from '{source}' to '{destination}' successfully"
            self.log_tool_result(self.name, result)
            return result
        except FileNotFoundError:
            error = f"Error: File '{source}' not found"
            self.log_tool_result(self.name, error)
            return error
        except PermissionError:
            error = f"Error: Permission denied for '{source}'"
            self.log_tool_result(self.name, error)
            return error