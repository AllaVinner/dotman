from pathlib import Path

from dotman.add import _format_dotfile_path
from dotman.config import CONFIG_FILE_NAME, Config, DotfileConfig, DotfilePath
from dotman.context import Platform, PlatformLiteral, get_context
from dotman.exceptions import DotmanException
from dotman.util import resolve_path


def _edit(
    project: Path, dotfile: Path, target: Path, platform: Platform | None = None
) -> None:
    full_target = resolve_path(Path(project, target))
    formatted_target = full_target.relative_to(project)
    config = Config.from_project(project=project)
    formatted_dotfile = _format_dotfile_path(dotfile)
    previous_dotconfig = config.dotfiles.get(formatted_target)
    if previous_dotconfig is None:
        raise DotmanException(
            f"No target {formatted_target.as_posix()} configured in project {project.as_posix()}."
        )
    if platform is None:
        if isinstance(previous_dotconfig, DotfilePath):
            config.dotfiles[formatted_target] = formatted_dotfile
        else:
            context = get_context()
            previous_dotconfig.links[context.platform] = formatted_dotfile
    else:
        if isinstance(previous_dotconfig, DotfilePath):
            dotfile_config = DotfileConfig(
                links={
                    p: previous_dotconfig if p != platform else formatted_dotfile
                    for p in Platform
                }
            )
            config.dotfiles[formatted_target] = dotfile_config
        else:
            previous_dotconfig.links[platform] = formatted_dotfile
    dotman_config_path = Path(project, CONFIG_FILE_NAME)
    config.write(dotman_config_path)


def edit(
    target: Path | str,
    dotfile: Path | str,
    project: Path | str | None = None,
    platform: Platform | PlatformLiteral | None = None,
) -> None:
    if project is None:
        project = resolve_path(".")
    else:
        project = resolve_path(project)
    dotfile = resolve_path(dotfile)
    target = Path(target)
    if isinstance(platform, str):
        platform = Platform(platform)
    _edit(project, dotfile, target, platform=platform)
