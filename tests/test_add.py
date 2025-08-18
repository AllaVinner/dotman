from pathlib import Path

from dotman.add import add
from dotman.config import Config
from dotman.examples import setup_folder_structure


def test_basic(tmp_path: Path) -> None:
    with setup_folder_structure(Path(tmp_path, "root"), stop_after="init") as paths:
        add(dotfile="~/bashrc")
        assert paths.bashrc.exists()
        assert paths.bashrc.is_symlink()
        assert Path(paths.project, paths.bashrc.name).exists()
        assert (
            Path(paths.project, paths.bashrc.name).read_text()
            == f"ORIGIN: {paths.bashrc.name}"
        )
        config = Config.from_project(paths.project)
        assert Path(paths.bashrc.name) in config.dotfiles
        assert config.dotfiles[Path(paths.bashrc.name)] == Path("~/bashrc")

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
        assert Path(paths.tmux_dir.name) in config.dotfiles
        assert config.dotfiles[Path(paths.tmux_dir.name)] == Path("~/dot_config/tmux")
