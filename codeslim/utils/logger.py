"""
Structured Logging Module for CodeSlim.

Provides centralized structlog configuration with dual rendering modes:
- Developer Mode: Colorized console output for interactive debugging.
- CI/CD Mode: JSON line formatting for automated log processors.
"""

import logging
import sys
from typing import Any, cast

import structlog


def setup_logging(*, log_level: str = "INFO", json_output: bool = False) -> None:
    """
    Configure application-wide structured logging.

    Args:
        log_level: Severity threshold (DEBUG, INFO, WARNING, ERROR).
        json_output: If True, outputs JSON lines; otherwise outputs console logs.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    renderer: structlog.types.Processor
    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            pad_event=35,
        )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=numeric_level,
    )


def get_logger(name: str, **initial_context: Any) -> structlog.stdlib.BoundLogger:
    """
    Return a named structlog logger with optional bound context.

    Args:
        name: Module identifier (e.g., 'codeslim.analyzers.complexity').
        **initial_context: Key-value context bound to all log events.
    """
    logger = structlog.get_logger(name)

    if initial_context:
        logger = logger.bind(**initial_context)

    return cast(structlog.stdlib.BoundLogger, logger)
