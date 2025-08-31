from pathlib import Path
import shutil
from typing import cast, get_args

from dotman.config import Config, DotfileConfig
from dotman.context import DotfileMode, get_context
from dotman.exceptions import DotmanException
from dotman.util import format_target_path, resolve_path


def _setup(target: Path, project: Path, dotfile_mode: DotfileMode):
    full_target = resolve_path(Path(project, target))
    formatted_target = format_target_path(target, project)
    config = Config.from_project(project)
    previous_dotconfig = config.dotfiles.get(formatted_target)
    if previous_dotconfig is None:
        raise DotmanException(
            f"Provided target {target.as_posix()} is not configured in project {project.as_posix()}."
        )
    elif isinstance(previous_dotconfig, DotfileConfig):
        context = get_context()
        formatted_dotfile = previous_dotconfig.links[context.platform]
    else:
        formatted_dotfile = previous_dotconfig
    if len(formatted_dotfile) == 0:
        raise DotmanException(
            f"Target {target.as_posix()} in project {project.as_posix()} is configured to empty."
        )
    dotfile_path = resolve_path(formatted_dotfile)
    if dotfile_path.exists():
        raise DotmanException(
            f"Cannot setup target {target.as_posix()}, in project {project.as_posix()}, as the dotfile path {dotfile_path.as_posix()} already is occupied."
        )
    if dotfile_mode == "symlink":
        dotfile_path.symlink_to(full_target)
    elif dotfile_mode == "copy":
        if full_target.is_dir():
            shutil.copytree(full_target, dotfile_path)
        else:
            shutil.copy2(full_target, dotfile_path)


def setup(
    target: Path | str,
    project: Path | str | None = None,
    *,
    dotfile_mode: DotfileMode | None = None,
):
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    if dotfile_mode is None:
        dotfile_mode = cast(DotfileMode, get_args(DotfileMode)[0])
    target = Path(target)
    _setup(target, project, dotfile_mode)


def _setup_project(project: Path, dotfile_mode: DotfileMode):
    context = get_context()
    config = Config.from_project(project)
    targets_and_dotfiles = []
    for formatted_target, formatted_dotconfig in config.dotfiles.items():
        full_target = resolve_path(Path(project, formatted_target))
        if isinstance(formatted_dotconfig, DotfileConfig):
            formatted_dotfile_link = formatted_dotconfig.links.get(context.platform)
            if formatted_dotfile_link is None:
                raise DotmanException(
                    f"Target {formatted_target}, in project {project.as_posix()} does not have a links configured for platform {context.platform}."
                )
        else:
            formatted_dotfile_link = formatted_dotconfig
        dotfile_path = resolve_path(formatted_dotfile_link)
        if dotfile_path.exists():
            raise DotmanException(
                f"Cannot setup target {formatted_target}, in project {project.as_posix()}, as the dotfile path {formatted_dotfile_link} already is occupied."
            )
        targets_and_dotfiles.append((full_target, dotfile_path))
    for full_target, dotfile in targets_and_dotfiles:
        if dotfile_mode == "symlink":
            dotfile.symlink_to(full_target)
        elif dotfile_mode == "copy":
            if full_target.is_dir():
                shutil.copytree(full_target, dotfile)
            else:
                shutil.copy2(full_target, dotfile)


def setup_project(
    project: Path | str | None = None, *, dotfile_mode: DotfileMode | None = None
):
    if dotfile_mode is None:
        dotfile_mode = cast(DotfileMode, get_args(DotfileMode)[0])
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    _setup_project(project, dotfile_mode=dotfile_mode)
