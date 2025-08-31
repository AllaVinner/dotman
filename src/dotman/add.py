from pathlib import Path
import shutil
from dotman.config import CONFIG_FILE_NAME, Config
from dotman.context import DotfileMode
from dotman.util import format_dotfile_path, format_target_path, resolve_path


def _add(
    project: Path, dotfile: Path, target: Path, *, dotfile_mode: DotfileMode = "symlink"
) -> None:
    full_target = resolve_path(Path(project, target))
    formatted_target = format_target_path(target, project)
    formatted_dotfile = format_dotfile_path(dotfile)
    config = Config.from_project(project)
    config.dotfiles[formatted_target] = formatted_dotfile
    dotman_config_path = Path(project, CONFIG_FILE_NAME)

    if dotfile_mode == "symlink":
        shutil.move(dotfile, full_target)
        dotfile.symlink_to(full_target)
    elif dotfile_mode == "copy":
        if dotfile.is_file():
            shutil.copy2(dotfile, full_target)
        else:
            shutil.copytree(dotfile, full_target)
    config.write(dotman_config_path)


def add(
    dotfile: Path | str,
    target: Path | str | None = None,
    project: Path | str | None = None,
    *,
    dotfile_mode: DotfileMode = "symlink",
) -> None:
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    dotfile = resolve_path(dotfile)
    if target is None:
        target = Path(dotfile.name)
    else:
        target = Path(target)
    _add(project, dotfile, target, dotfile_mode=dotfile_mode)
