from textual.widgets import RichLog

from events.event_bus import EventBus
from logger import LogRecord, get_history, subscribe, unsubscribe
from ui.widgets.base import AgentWidget


class LogsView(AgentWidget):
    """Shows every log_info call in a side panel."""

    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(event_bus, **kwargs)
        self.log_display = None
        self.lines = ["Logs", "----"]
        self.max_lines = 200
        self._log_listener = None

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
        self._log_listener = self._on_log_record
        subscribe(self._log_listener)

        if self.log_display:
            self.log_display.write("Logs")
            self.log_display.write("----")

        for record in get_history():
            self._append_record(record)

    def on_unmount(self) -> None:
        if self._log_listener is not None:
            unsubscribe(self._log_listener)

    def _on_log_record(self, record: LogRecord) -> None:
        self._append_record(record)

    def _append_record(self, record: LogRecord) -> None:
        self.lines.append(record.format())
        self.lines = self.lines[-self.max_lines :]

        if self.log_display:
            self.log_display.clear()
            for line in self.lines:
                self.log_display.write(line)
