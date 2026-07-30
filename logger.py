import sys
from datetime import datetime
from typing import TextIO


class AppLogger:
    def __init__(self, stream: TextIO | None = None):
        self.stream = stream or sys.stdout

    def info(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [INFO] {message}", file=self.stream)


logger = AppLogger()


def log_info(message: str) -> None:
    logger.info(message)


def set_stream(stream: TextIO | None) -> None:
    logger.stream = stream
