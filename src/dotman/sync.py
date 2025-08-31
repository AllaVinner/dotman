from pathlib import Path
import shutil

from dotman.config import Config, DotfileConfig
from dotman.context import get_context
from dotman.exceptions import DotmanException
from dotman.util import format_target_path, resolve_path


def _check_target_dotfile_sync_compatibility(
    dotfile: Path, target: Path, project: Path
):
    if not dotfile.exists():
        raise DotmanException(
            f"Cannot refresh target {target.as_posix()}, in project {project.as_posix()}, as the dotfile path {dotfile.as_posix()} doesn't exist."
        )
    if dotfile.is_symlink():
        raise DotmanException(
            f"Cannot refresh target {target.as_posix()}, in project {project.as_posix()}, as the dotfile path {dotfile.as_posix()} is a symlink."
        )
    if target.is_dir():
        if not dotfile.is_dir():
            raise DotmanException(
                f"Cannot refresh target {target.as_posix()}, in project {project.as_posix()}, as the dotfile path {dotfile.as_posix()} is not a directory."
            )
    else:
        if not dotfile.is_file():
            raise DotmanException(
                f"Cannot refresh target {target.as_posix()}, in project {project.as_posix()}, as the dotfile path {dotfile.as_posix()} is not a file."
            )


def _sync_target_to_dotfile(target: Path, dotfile: Path):
    if target.is_dir():
        shutil.rmtree(target)
        shutil.copytree(dotfile, target)
    else:
        target.unlink()
        shutil.copy2(dotfile, target)


def _sync(target: Path, project: Path):
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
    _check_target_dotfile_sync_compatibility(
        dotfile=dotfile_path, target=full_target, project=project
    )
    _sync_target_to_dotfile(target=full_target, dotfile=dotfile_path)


def sync(
    target: Path | str,
    project: Path | str | None = None,
):
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    target = Path(target)
    _sync(target, project)


def _sync_project(project: Path) -> None:
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
        _check_target_dotfile_sync_compatibility(dotfile_path, full_target, project)
        targets_and_dotfiles.append((full_target, dotfile_path))
    for full_target, dotfile in targets_and_dotfiles:
        _sync_target_to_dotfile(full_target, dotfile)


def sync_project(
    project: Path | str | None = None,
):
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    _sync_project(project)
