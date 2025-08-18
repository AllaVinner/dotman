from pathlib import Path
import shutil
from dotman.config import CONFIG_FILE_NAME, Config
from dotman.context import Context, get_context
from dotman.exceptions import Unreachable
from dotman.util import resolve_path


def _format_dotfile_path(path: Path, context: Context | None = None) -> Path:
    if context is None:
        context = get_context()
    path = resolve_path(path, context=context)
    if path.is_relative_to(context.home):
        formatted_path = Path("~", path.relative_to(context.home))
    elif path.is_relative_to(context.root):
        formatted_path = Path("/", path.relative_to(context.root))
    else:
        raise Unreachable(
            f"Path {path.as_posix()} must be relative to root {context.root.as_posix()}."
        )
    return formatted_path


def _add(project: Path, dotfile: Path, target: Path) -> None:
    assert not target.is_absolute(), (
        f"Target path {target.as_posix()} cannot be absolute."
    )
    full_target = resolve_path(Path(project, target))
    formatted_target = full_target.relative_to(project)
    formatted_dotfile = _format_dotfile_path(dotfile)
    config = Config.from_project(project)
    config.dotfiles[formatted_target] = formatted_dotfile
    dotman_config_path = Path(project, CONFIG_FILE_NAME)

    shutil.move(dotfile, full_target)
    dotfile.symlink_to(full_target)
    config.write(dotman_config_path)


def add(
    dotfile: Path | str,
    target: Path | str | None = None,
    project: Path | str | None = None,
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
    _add(project, dotfile, target)
