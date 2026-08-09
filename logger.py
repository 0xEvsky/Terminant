import inspect
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, TextIO


@dataclass(frozen=True)
class LogRecord:
    timestamp: str
    level: str
    message: str
    caller: str

    def format(self) -> str:
        return f"[{self.timestamp}] [{self.level}] [{self.caller}] {self.message}"


LogListener = Callable[[LogRecord], None]


class AppLogger:
    def __init__(self, stream: TextIO | None = None):
        self.stream = stream
        self._history: list[LogRecord] = []
        self._listeners: list[LogListener] = []

    def info(self, message: str, caller: str | None = None) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caller_text = caller or self._resolve_caller()
        record = LogRecord(
            timestamp=timestamp,
            level="INFO",
            message=message,
            caller=caller_text,
        )
        self._history.append(record)
        if self.stream is not None:
            print(record.format(), file=self.stream)

        for listener in list(self._listeners):
            listener(record)

    def subscribe(self, listener: LogListener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: LogListener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def history(self) -> list[LogRecord]:
        return list(self._history)

    def _resolve_caller(self) -> str:
        frame = inspect.currentframe()
        if frame is None or frame.f_back is None:
            return "unknown"

        caller_frame = frame.f_back.f_back
        if caller_frame is None:
            return "unknown"

        filename = Path(caller_frame.f_code.co_filename).name
        return f"{filename}:{caller_frame.f_lineno} {caller_frame.f_code.co_name}"


logger = AppLogger()


def log_info(message: str) -> None:
    frame = inspect.currentframe()
    caller = None
    if frame is not None and frame.f_back is not None:
        caller_frame = frame.f_back
        filename = Path(caller_frame.f_code.co_filename).name
        caller = f"{filename}:{caller_frame.f_lineno} {caller_frame.f_code.co_name}"

    logger.info(message, caller=caller)


def set_stream(stream: TextIO | None) -> None:
    logger.stream = stream


def subscribe(listener: LogListener) -> None:
    logger.subscribe(listener)


def unsubscribe(listener: LogListener) -> None:
    logger.unsubscribe(listener)


def get_history() -> list[LogRecord]:
    return logger.history()
