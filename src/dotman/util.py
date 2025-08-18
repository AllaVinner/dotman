from pathlib import Path
import os
import sys
import logging

from dotman.context import Context, get_context


def format_path(path: Path) -> str:
    return path.resolve().as_posix()


def logger_setup(logger: logging.Logger) -> None:
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)


def resolve_path(path: Path | str, context: Context | None = None) -> Path:
    if context is None:
        context = get_context()
    norm_path = Path(os.path.normpath(path))
    if norm_path.is_absolute():
        return norm_path
    parts = norm_path.parts
    if len(parts) == 0:
        return context.cwd
    if parts[0] == "~":
        return Path(os.path.normpath(Path(context.home, *parts[1:])))
    return Path(os.path.normpath(Path(context.cwd, norm_path)))
