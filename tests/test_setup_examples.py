from pathlib import Path
from dotman.examples import setup_folder_structure


def test_setup_setup(tmp_path: Path):
    paths = setup_folder_structure(tmp_path, "setup")
    assert paths.root.is_dir()
    assert paths.home.is_dir()
    assert paths.bashrc.is_file()
    assert paths.dot_config.is_dir()
    assert paths.tmux_dir.is_dir()
    assert paths.tmux_config.is_file()
    assert paths.project.is_dir()
    assert not paths.project_config.exists()
    assert not paths.project_bashrc.exists()
    assert not paths.project_tmux_dir.exists()
    assert not paths.project_tmux_config.exists()


def test_setup_init(tmp_path: Path):
    paths = setup_folder_structure(tmp_path, "init")
    assert paths.root.is_dir()
    assert paths.home.is_dir()
    assert paths.bashrc.is_file()
    assert paths.dot_config.is_dir()
    assert paths.tmux_dir.is_dir()
    assert paths.tmux_config.is_file()
    assert paths.project.is_dir()
    assert paths.project_config.is_file()
    assert not paths.project_bashrc.exists()
    assert not paths.project_tmux_dir.exists()
    assert not paths.project_tmux_config.exists()


def test_setup_add(tmp_path: Path):
    paths = setup_folder_structure(tmp_path, "add")
    assert paths.root.is_dir()
    assert paths.home.is_dir()
    assert paths.bashrc.is_symlink()
    assert paths.dot_config.is_dir()
    assert paths.tmux_dir.is_symlink()
    assert paths.tmux_config.is_file()
    assert paths.project.is_dir()
    assert paths.project_config.is_file()
    assert paths.project_bashrc.is_file()
    assert paths.project_tmux_dir.is_dir()
    assert paths.project_tmux_config.is_file()


def test_setup_new(tmp_path: Path):
    paths = setup_folder_structure(tmp_path, "new")
    assert paths.root.is_dir()
    assert paths.home.is_dir()
    assert not paths.bashrc.exists()
    assert paths.dot_config.is_dir()
    assert not paths.tmux_dir.exists()
    assert not paths.tmux_config.exists()
    assert paths.project.is_dir()
    assert paths.project_config.is_file()
    assert paths.project_bashrc.is_file()
    assert paths.project_tmux_dir.is_dir()
    assert paths.project_tmux_config.is_file()


def test_setup_resetup(tmp_path: Path):
    paths = setup_folder_structure(tmp_path, "resetup")
    assert paths.root.is_dir()
    assert paths.home.is_dir()
    assert paths.bashrc.is_symlink()
    assert paths.dot_config.is_dir()
    assert paths.tmux_dir.is_symlink()
    assert paths.tmux_config.is_file()
    assert paths.project.is_dir()
    assert paths.project_config.is_file()
    assert paths.project_bashrc.is_file()
    assert paths.project_tmux_dir.is_dir()
    assert paths.project_tmux_config.is_file()
