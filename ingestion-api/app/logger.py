"""
logger.py – Structured JSON logging for the ingestion API.

Every log record is emitted as a single JSON line so that log aggregators
(CloudWatch Logs Insights, Datadog, Loki …) can parse and query fields
without regex.

Usage:
    from app.logger import get_logger
    log = get_logger(__name__)
    log.info("execution_recorded", job_name="etl_job", run_id="abc123", duration_ms=42)
"""

import logging
import json
import os
import sys
import time
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Formats a LogRecord as a single-line JSON object."""

    RESERVED = {"message", "asctime", "levelname", "name", "exc_info", "exc_text", "stack_info"}

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
            "env":       os.getenv("APP_ENV", "unknown"),
            "version":   os.getenv("APP_VERSION", "unknown"),
        }

        # Merge any extra keyword args passed via log.info("msg", extra={...})
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and key not in self.RESERVED and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger


# ── Request timing context manager ────────────────────────────────────────────

class Timer:
    """Simple wall-clock timer for measuring request durations."""

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.elapsed_ms = round((time.perf_counter() - self._start) * 1000, 2)
