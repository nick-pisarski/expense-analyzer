"""Logging configuration for the expense analyzer"""

import os
import logging
from logging.config import dictConfig


def configure_logging():
    """Configure logging based on environment variables"""
    # Get log level from environment variable, default to INFO
    log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Validate log level
    valid_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = valid_levels.get(log_level_name, logging.INFO)

    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": log_level,
                "formatter": "standard",
                "filename": os.environ.get("LOG_FILE", "expense_analyzer.log"),
                "mode": "a",
            },
        },
        "loggers": {
            "expense_analyzer": {"handlers": ["console", "file"], "level": log_level, "propagate": False},
        },
    }

    # Apply configuration
    dictConfig(logging_config)

    # Log the configuration
    logger = logging.getLogger("expense_analyzer")
    logger.info(f"Expense Analyzer logging configured with level: {log_level_name}")
