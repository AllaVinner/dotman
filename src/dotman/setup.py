from pathlib import Path

from dotman.config import Config
from dotman.context import get_context
from dotman.exceptions import DotmanException
from dotman.util import resolve_path


def _setup(target: Path, project: Path):
    full_target = resolve_path(Path(project, target))
    formatted_target = full_target.relative_to(project)
    config = Config.from_project(project)
    formatted_dotfile = config.dotfiles.get(formatted_target)
    if formatted_dotfile is None:
        raise DotmanException(
            f"Provided target {target.as_posix()} is not configured in project {project.as_posix()}."
        )
    context = get_context()
    if formatted_dotfile.parts[0] == "~":
        formatted_dotfile = Path(context.home, *formatted_dotfile.parts[1:])
    if formatted_dotfile.exists():
        raise DotmanException(
            f"Cannot setup target {target.as_posix()}, in project {project.as_posix()}, as the dotfile path {formatted_dotfile.as_posix()} already is occupied."
        )
    formatted_dotfile.symlink_to(full_target)


def setup(
    target: Path | str,
    project: Path | str | None = None,
):
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    target = Path(target)
    _setup(target, project)


def _setup_project(project: Path):
    context = get_context()
    config = Config.from_project(project)
    targets_and_dotfiles = []
    for formatted_target, formatted_dotfile in config.dotfiles.items():
        full_target = resolve_path(Path(project, formatted_target))
        if formatted_dotfile.parts[0] == "~":
            formatted_dotfile = Path(context.home, *formatted_dotfile.parts[1:])
        if formatted_dotfile.exists():
            raise DotmanException(
                f"Cannot setup target {formatted_target.as_posix()}, in project {project.as_posix()}, as the dotfile path {formatted_dotfile.as_posix()} already is occupied."
            )
        targets_and_dotfiles.append((full_target, formatted_dotfile))
    for full_target, dotfile in targets_and_dotfiles:
        dotfile.symlink_to(full_target)


def setup_project(
    project: Path | str | None = None,
):
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    _setup_project(project)
