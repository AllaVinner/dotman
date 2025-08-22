from pathlib import Path
import os
import sys
import logging

from dotman.context import Context, get_context
from dotman.exceptions import DotmanException


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


def format_dotfile_path(path: Path, context: Context | None = None) -> str:
    if context is None:
        context = get_context()
    path = resolve_path(path, context=context)
    if path.is_relative_to(context.home):
        return Path("~", path.relative_to(context.home)).as_posix()
    else:
        return path.as_posix()


def format_target_path(
    target: Path, project: Path, context: Context | None = None
) -> str:
    if context is None:
        context = get_context()
    full_target = resolve_path(Path(project, target), context=context)
    if not full_target.is_relative_to(project):
        raise DotmanException(
            f"Target {target.as_posix()} must be relative to project {project.as_posix()}."
        )
    formatted_target = full_target.relative_to(project)
    return formatted_target.as_posix()
