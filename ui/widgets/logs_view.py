from textual.widgets import RichLog

from events.event_bus import EventBus
from logger import LogRecord, get_history, subscribe, unsubscribe
from ui.widgets.base import AgentWidget


class LogsView(AgentWidget):
    """Shows every log_info call in a side panel."""

    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(event_bus, **kwargs)
        self.log_display = None
        self.max_lines = 200
        self._log_listener = None
        self._initialized = False
        self._mounted = False
        self._lines: list[LogRecord | str] = []

    def compose(self):
        self.log_display = RichLog(
            id="log-display",
            markup=True,
            highlight=False,
            wrap=True,
            auto_scroll=True,
        )
        yield self.log_display

    def on_mount(self) -> None:
        # Guard against double mount
        if self._mounted:
            return
        self._mounted = True

        self._log_listener = self._on_log_record
        subscribe(self._log_listener)

        if self.log_display:
            self.log_display.write("Logs")
            self.log_display.write("----")
            self._lines = ["Logs", "----"]
            self._initialized = True

        for record in get_history():
            self._append_record(record)

    def on_unmount(self) -> None:
        if self._log_listener is not None:
            unsubscribe(self._log_listener)
            self._log_listener = None
        self._mounted = False
        self._initialized = False

    def _on_log_record(self, record: LogRecord) -> None:
        self._append_record(record)

    def _append_record(self, record: LogRecord) -> None:
        if not self.log_display or not self._initialized:
            return

        # Use RichLog's native append capability for normal operation
        self.log_display.write(record.to_rich_text())
        self._lines.append(record)

        # Trim infrequently to avoid flickering - only when significantly over limit
        if len(self._lines) > self.max_lines + 50:
            self._trim_log()

    def _trim_log(self) -> None:
        """Trim the log by keeping only the most recent max_lines entries."""
        if not self.log_display:
            return

        # Keep only the most recent max_lines entries
        self._lines = self._lines[-self.max_lines:]

        # Clear and rewrite - this happens infrequently (every 50 lines over limit)
        self.log_display.clear()
        for line in self._lines:
            if isinstance(line, LogRecord):
                self.log_display.write(line.to_rich_text())
            else:
                self.log_display.write(line)
