"""Logging utility for Nexlify KB."""
import logging
import sys
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

console = Console(
    theme=Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
    })
)

def get_logger(name: str = "nexlify_kb") -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
        )
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(message)s",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger


logger = get_logger()