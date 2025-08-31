from dataclasses import dataclass
import os
from pathlib import Path

from dotman.config import Config, DotfileConfig
from dotman.context import get_context
from dotman.util import folder_md5, md5_of_file, resolve_path


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
            if full_target.is_file():
                if not dotfile_path.is_file():
                    stat = "Dotfile is not a symlink, nor a file which the target is"
                else:
                    dotfile_md5 = md5_of_file(dotfile_path)
                    target_md5 = md5_of_file(full_target)
                    if dotfile_md5 == target_md5:
                        stat = "Complete - Copy"
                    else:
                        stat = "Dotfile is not a symlink nor eqaul in content"
            else:
                if not dotfile_path.is_dir():
                    stat = (
                        "Dotfile is not a symlink, nor a directory which the target is"
                    )
                else:
                    dotfile_md5s = folder_md5(dotfile_path)
                    target_md5s = folder_md5(full_target)
                    extra_in_dotfile = set(dotfile_md5s.keys()) - set(
                        target_md5s.keys()
                    )
                    extra_in_target = set(target_md5s.keys()) - set(dotfile_md5s.keys())
                    if len(extra_in_dotfile) > 0:
                        extra_path_str = ", ".join(
                            [p.as_posix() for p in extra_in_dotfile]
                        )
                        stat = f"Dotfile is not a symlink, and contains extra files compared to target: {extra_path_str}"
                    elif len(extra_in_target) > 0:
                        extra_path_str = ", ".join(
                            [p.as_posix() for p in extra_in_target]
                        )
                        stat = f"Dotfile is not a symlink, and is missing files compared to target: {extra_path_str}"
                    else:
                        stat = "Complete - Copy"
                        for path in dotfile_md5s.keys():
                            if dotfile_md5s[path] != target_md5s[path]:
                                stat = f"Dotfile is not a symlink, and file {path.as_posix()} is not identical to target."
                                break
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
