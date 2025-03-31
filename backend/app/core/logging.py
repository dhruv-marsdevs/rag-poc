import logging
import sys
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel

from app.core.config import get_settings


class LoggingSettings(BaseModel):
    """Logging settings."""

    LOG_LEVEL: str = get_settings().LOG_LEVEL
    LOGGERS: List[str] = ["app"]


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configure logging based on logging settings.
    Intercepting all standard logging and routing it through loguru.
    """
    logging_settings = LoggingSettings()

    # Remove all existing handlers
    logging.root.handlers = []
    logging.root.setLevel(logging_settings.LOG_LEVEL)

    # Intercept standard logging
    for name in logging.root.manager.loggerDict.keys():
        if name in logging_settings.LOGGERS or name.startswith("app"):
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True

    # Initialize loguru
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": (
                    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                    "<level>{message}</level>"
                ),
                "level": logging_settings.LOG_LEVEL,
                "diagnose": True,
            }
        ]
    )

    # Intercept standard logging and route through loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Add custom logger
    logger.info("Logging is configured.")
    return logger
