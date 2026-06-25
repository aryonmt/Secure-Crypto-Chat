"""
Custom Logging Module for Professional Output Formatting.

Provides a centralized logging configuration to ensure consistent,
readable, and timestamped output formats across all application components.
"""

import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Initialize and configure a logger instance with standard formatting.

    This function safely configures a stream handler for console output.
    It checks for existing handlers to prevent duplicate log entries when
    called multiple times.

    Args:
        name (str): The identifier name for the logger (e.g., 'SERVER' or 'CLIENT').

    Returns:
        logging.Logger: The fully configured logger instance ready for use.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent attaching multiple handlers to the same logger
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Standard format: [YYYY-MM-DD HH:MM:SS] [LEVEL] - Message
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
