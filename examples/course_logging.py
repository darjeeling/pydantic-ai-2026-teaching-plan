from __future__ import annotations

import logging
import os
from pathlib import Path

DEFAULT_API_LOG_FILE = Path("logs/api-calls.log")
FILE_HANDLER_NAME = "course-api-file"


def configure_api_call_logging(log_file: str | Path | None = None) -> Path | None:
    """Write provider/API call breadcrumbs to a local file.

    The default level intentionally avoids request/response payloads. Set
    COURSE_API_LOG_LEVEL=DEBUG only for throwaway prompts with no secrets.
    """
    if os.getenv("COURSE_API_LOG_DISABLED") == "1":
        return None

    log_path = Path(log_file or os.getenv("COURSE_API_LOG_FILE", DEFAULT_API_LOG_FILE))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    level_name = os.getenv("COURSE_API_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    course_logger = logging.getLogger("course.api")
    handler = next(
        (existing for existing in course_logger.handlers if existing.name == FILE_HANDLER_NAME),
        None,
    )
    if handler is None:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.name = FILE_HANDLER_NAME
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
    handler.setLevel(level)

    for logger_name in ("course.api", "httpx", "openai", "pydantic_ai"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        if not any(existing.name == FILE_HANDLER_NAME for existing in logger.handlers):
            logger.addHandler(handler)

    httpcore_level = logging.DEBUG if level <= logging.DEBUG else logging.WARNING
    httpcore_logger = logging.getLogger("httpcore")
    httpcore_logger.setLevel(httpcore_level)
    if not any(existing.name == FILE_HANDLER_NAME for existing in httpcore_logger.handlers):
        httpcore_logger.addHandler(handler)

    course_logger.info(
        "api log configured file=%s level=%s",
        log_path,
        level_name,
    )
    return log_path


def api_logger() -> logging.Logger:
    return logging.getLogger("course.api")
