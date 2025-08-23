from dataclasses import dataclass
import os
from pathlib import Path

from dotman.config import Config, DotfileConfig
from dotman.context import get_context
from dotman.util import resolve_path


@dataclass
class DotfileLinkStatus:
    target: Path
    dotfile: Path
    status: str


@dataclass
class DotfileProjectStatus:
    project: Path
    links: list[DotfileLinkStatus]


def _status(project: Path) -> DotfileProjectStatus:
    context = get_context()
    config = Config.from_project(project)
    link_status: list[DotfileLinkStatus] = list()
    for target, formatted_dotfile in config.dotfiles.items():
        full_target = resolve_path(Path(project, target))
        if isinstance(formatted_dotfile, DotfileConfig):
            formatted_dotfile_link = formatted_dotfile.links[context.platform]
        else:
            formatted_dotfile_link = formatted_dotfile
        dotfile_path = resolve_path(formatted_dotfile_link)
        if not full_target.exists():
            stat = "Missing target"
        elif not dotfile_path.exists():
            stat = "Missing Dotfile"
        elif not dotfile_path.is_symlink():
            stat = "Dotfile is not a symlink"
        elif Path(os.readlink(dotfile_path)) != full_target:
            stat = "Dotfile link does not point to target"
        else:
            stat = "Complete"
        link_status.append(
            DotfileLinkStatus(target=Path(target), dotfile=dotfile_path, status=stat)
        )
    return DotfileProjectStatus(project=project, links=link_status)


def status(project: Path | str | None = None) -> DotfileProjectStatus:
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    return _status(project)
