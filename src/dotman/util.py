from pathlib import Path
import sys
import logging


def format_path(path: Path) -> str:
    return path.resolve().as_posix()


def logger_setup(logger: logging.Logger) -> None:
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
