"""Structured JSON logging with correlation IDs and OpenTelemetry integration."""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from config.settings import settings


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = str(uuid.uuid4())
        return True


class StructuredFormatter(logging.Formatter):
    """Format logs as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]),
            }

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data

        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger with structured JSON output."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.log_level))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(StructuredFormatter())
        console_handler.addFilter(CorrelationIdFilter())
        logger.addHandler(console_handler)

        logger.propagate = False

    return logger


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    extra_data: dict[str, Any] | None = None,
) -> None:
    """Log a message with additional context data."""
    record = logger.makeRecord(
        logger.name,
        level,
        "",
        0,
        message,
        (),
        None,
    )
    if extra_data:
        record.extra_data = extra_data  # type: ignore[attr-defined]
    logger.handle(record)
