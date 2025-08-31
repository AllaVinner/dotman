from pathlib import Path

from dotman.add import add
from dotman.config import Config
from dotman.context import Context, managed_context
from dotman.examples import setup_folder_structure


def test_basic(tmp_path: Path) -> None:
    paths = setup_folder_structure(Path(tmp_path, "root"), stage="add")
    with managed_context(Context(home=paths.home, cwd=paths.project)):
        add(dotfile="~/bashrc")
        assert paths.bashrc.exists()
        assert paths.bashrc.is_symlink()
        assert Path(paths.project, paths.bashrc.name).exists()
        assert (
            Path(paths.project, paths.bashrc.name).read_text()
            == f"ORIGIN: {paths.bashrc.name}"
        )
        config = Config.from_project(paths.project)
        assert paths.bashrc.name in config.dotfiles
        assert config.dotfiles[paths.bashrc.name] == "~/bashrc"

        add(project=paths.project, dotfile="~/dot_config/tmux")
        assert paths.tmux_dir.exists()
        assert paths.tmux_dir.is_symlink()
        assert paths.project_tmux_dir.exists()
        assert paths.project_tmux_dir.is_dir()
        assert paths.project_tmux_config.exists()
        assert (
            paths.project_tmux_config.read_text() == f"ORIGIN: {paths.tmux_config.name}"
        )
        config = Config.from_project(paths.project)
        assert paths.tmux_dir.name in config.dotfiles
        assert config.dotfiles[paths.tmux_dir.name] == "~/dot_config/tmux"


def test_as_copy(tmp_path: Path) -> None:
    paths = setup_folder_structure(Path(tmp_path, "root"), stage="add")
    with managed_context(Context(home=paths.home, cwd=paths.project)):
        add(dotfile="~/bashrc", dotfile_mode="copy")
        assert paths.bashrc.exists()
        assert not paths.bashrc.is_symlink()
        assert Path(paths.project, paths.bashrc.name).exists()
        assert (
            Path(paths.project, paths.bashrc.name).read_text()
            == f"ORIGIN: {paths.bashrc.name}"
        )
        config = Config.from_project(paths.project)
        assert paths.bashrc.name in config.dotfiles
        assert config.dotfiles[paths.bashrc.name] == "~/bashrc"

        add(project=paths.project, dotfile="~/dot_config/tmux", dotfile_mode="copy")
        assert paths.tmux_dir.exists()
        assert not paths.tmux_dir.is_symlink()
        assert paths.project_tmux_dir.exists()
        assert paths.project_tmux_dir.is_dir()
        assert paths.project_tmux_config.exists()
        assert (
            paths.project_tmux_config.read_text() == f"ORIGIN: {paths.tmux_config.name}"
        )
        config = Config.from_project(paths.project)
        assert paths.tmux_dir.name in config.dotfiles
        assert config.dotfiles[paths.tmux_dir.name] == "~/dot_config/tmux"
