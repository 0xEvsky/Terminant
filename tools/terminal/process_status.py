import csv
import os
import platform
import subprocess

from tools.base import Tool
from logger import log_info


class ProcessStatus(Tool):
    @property
    def name(self):
        return "terminal.process_status"

    @property
    def description(self):
        return "Check whether a process is running"

    @property
    def arguments(self):
        return {
            "pid": {
                "type": "integer",
                "description": "Process ID to inspect."
            }
        }

    def execute(self, **kwargs):
        pid = kwargs.get("pid")
        self.log_tool_call(self.name, kwargs)
        log_info(f"Executing {self.name}(pid={pid!r})")

        try:
            process_id = int(pid)

            if platform.system().lower().startswith("win"):
                completed = subprocess.run(
                    ["tasklist", "/FO", "CSV", "/NH", "/FI", f"PID eq {process_id}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                output = completed.stdout.strip()
                if not output or "No tasks are running" in output:
                    result = {"pid": process_id, "running": False, "status": "not_found"}
                    self.log_tool_result(self.name, result)
                    return result

                row = next(csv.reader([output]))
                result = {
                    "pid": process_id,
                    "running": True,
                    "status": "running",
                    "name": row[0] if len(row) > 0 else None,
                    "session_name": row[2] if len(row) > 2 else None,
                    "session_id": row[3] if len(row) > 3 else None,
                    "memory_usage": row[4] if len(row) > 4 else None,
                }
                self.log_tool_result(self.name, result)
                return result

            os.kill(process_id, 0)
            result = {"pid": process_id, "running": True, "status": "running"}
            self.log_tool_result(self.name, result)
            return result
        except ProcessLookupError:
            result = {"pid": pid, "running": False, "status": "not_found"}
            self.log_tool_result(self.name, result)
            return result
        except PermissionError:
            error = f"Error: Permission denied for process '{pid}'"
            self.log_tool_result(self.name, error)
            return error
        except FileNotFoundError:
            error = f"Error: Process '{pid}' not found"
            self.log_tool_result(self.name, error)
            return error
        except ValueError:
            error = f"Error: Invalid process id '{pid}'"
            self.log_tool_result(self.name, error)
            return error