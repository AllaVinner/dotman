from pathlib import Path
from dotman.config import Config, DotfileConfig
from dotman.context import Context, Platform, managed_context
from dotman.edit import edit
from dotman.examples import managed_setup, setup_folder_structure
from dotman.setup import setup_project


def test_basic(tmp_path: Path) -> None:
    paths = setup_folder_structure(Path(tmp_path, "root"), stop_after="new")
    with managed_context(Context(home=paths.home, cwd=paths.project)):
        edit(project=paths.project, target="tmux", dotfile="~/tmux")
        setup_project(project=paths.project)
        assert Path(paths.home, "tmux").is_symlink()


def test_platform_specific(tmp_path: Path) -> None:
    with managed_setup(Path(tmp_path, "root"), stage="new") as paths:
        edit(
            project=paths.project,
            target="tmux",
            dotfile="~/tmux",
            platform=Platform.windows,
        )
        config = Config.from_project(paths.project)
        tmux_dotconfig = config.dotfiles[Path("tmux")]
        assert isinstance(tmux_dotconfig, DotfileConfig)
        assert tmux_dotconfig.links[Platform.windows] == Path("~/tmux")
        assert tmux_dotconfig.links[Platform.linux] == Path("~/dot_config/tmux")
        assert tmux_dotconfig.links[Platform.mac] == Path("~/dot_config/tmux")
        setup_project(project=paths.project)
        assert Path(paths.home, "tmux").is_symlink()
