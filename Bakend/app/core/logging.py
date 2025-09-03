import logging
import sys
from typing import Any, Dict

from app.core.config import settings


class Logger:
    def __init__(self):
        self.logger = logging.getLogger(settings.PROJECT_NAME)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # Create console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def info(self, message: str, extra: Dict[str, Any] = None):
        self.logger.info(message, extra=extra)

    def error(self, message: str, extra: Dict[str, Any] = None):
        self.logger.error(message, extra=extra)

    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.logger.debug(message, extra=extra)


logger = Logger()
