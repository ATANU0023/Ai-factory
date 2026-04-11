import os
import sys
import uuid
import logging
import json
from datetime import datetime, timezone
from typing import Any

from ai_software_factory.config.settings import settings

# Global flag for interactive mode (CLI usage)
IS_INTERACTIVE_MODE = (
    os.environ.get("AI_FACTORY_INTERACTIVE") == "true" 
    or sys.stdin.isatty() # If running in a real terminal, it's interactive!
)

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = str(uuid.uuid4())
        return True


class HumanReadableFormatter(logging.Formatter):
    """Format logs in human-readable format for interactive mode."""

    def format(self, record: logging.LogRecord) -> str:
        # In interactive mode, only show actual ERRORS to keep it clean
        if record.levelno >= logging.ERROR:
            timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
            level = record.levelname
            message = record.getMessage()
            return f"[{timestamp}] {level}: {message}"
        return ""  # Suppress INFO and WARNING in interactive mode

class StructuredFormatter(logging.Formatter):
    """Format logs as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        # Return empty if we are in interactive mode but somehow this formatter is called
        if IS_INTERACTIVE_MODE:
            return ""
            
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


def get_logger(name: str, interactive: bool | None = None) -> logging.Logger:
    """Get a configured logger with structured JSON output.
    
    Args:
        name: Logger name
        interactive: If True, use human-readable format. If None, auto-detect (defaults to True for CLI).
    """
    logger = logging.getLogger(name)

    # Force interactive mode if running in terminal
    is_interactive = True if IS_INTERACTIVE_MODE else (interactive if interactive is not None else False)

    if not logger.handlers:
        # Use WARNING as base level, but HumanReadableFormatter will filter even more
        logger.setLevel(logging.WARNING)

        # Console handler
        console_handler = logging.StreamHandler()
        
        # Use human-readable format for interactive mode
        if is_interactive:
            console_handler.setFormatter(HumanReadableFormatter())
            # In interactive mode, only show ERROR and above by default on the handler
            console_handler.setLevel(logging.ERROR)
        else:
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
