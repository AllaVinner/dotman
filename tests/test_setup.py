from pathlib import Path

from dotman.setup import setup, setup_project
from dotman.context import Context, managed_context
from dotman.examples import setup_folder_structure


def test_basic(tmp_path: Path) -> None:
    paths = setup_folder_structure(Path(tmp_path, "root"), stop_after="new")
    with managed_context(Context(home=paths.home, cwd=paths.project)):
        setup(project=paths.project, target="bashrc")
        assert paths.bashrc.is_file()
        assert paths.bashrc.is_symlink()
        setup(project=paths.project, target="tmux")
        assert paths.tmux_dir.is_dir()
        assert paths.tmux_dir.is_symlink()
        assert paths.tmux_config.is_file()


def test_full_project(tmp_path: Path) -> None:
    paths = setup_folder_structure(Path(tmp_path, "root"), stop_after="new")
    with managed_context(Context(home=paths.home, cwd=paths.project)):
        setup_project(project=paths.project)
        assert paths.bashrc.is_file()
        assert paths.bashrc.is_symlink()
        assert paths.tmux_dir.is_dir()
        assert paths.tmux_dir.is_symlink()
        assert paths.tmux_config.is_file()
