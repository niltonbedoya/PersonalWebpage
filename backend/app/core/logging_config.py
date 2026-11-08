"""Rotating File Logging Configuration.

Configures a structured, bounded rotating file logger (max 10 MB, 5 backups)
at logs/app.log to debug the application, RAG queries, and security guardrails.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOG_DIR = REPO_ROOT / "logs"
LOG_FILE = LOG_DIR / "app.log"


def setup_logging() -> None:
    """Initialize rotating file logger."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    # Check if a RotatingFileHandler is already installed
    has_file_handler = any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers)

    if not has_file_handler:
        file_handler = RotatingFileHandler(
            filename=str(LOG_FILE),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.INFO)


def get_recent_logs(lines: int = 100) -> List[str]:
    """Retrieve the last N lines from the app.log file."""
    if not LOG_FILE.exists():
        return ["No log entries recorded yet."]
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            return [line.rstrip() for line in all_lines[-lines:]]
    except Exception as e:
        return [f"Error reading logs: {e}"]
