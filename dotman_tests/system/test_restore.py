from pathlib import Path
import pytest
import os
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project, ProjectException


def test_restore(tmp_path):
    home = Path(tmp_path, "home")
    config_path = Path(home, "git-config")
    gitignore_path = Path(config_path, ".gitignore")
    gitconfig_path = Path(config_path, ".gitconfig")
    project_path = Path(home, "projects", "git")
    ensure_folder_tree(
        folders=[project_path],
        files=[(gitignore_path, ".venv/"), (gitconfig_path, "username: Me")],
    )

    project = Project.init(project_path)
    project._home = home
    project.add_link(source=gitignore_path, target_name="global.ignore")
    project.add_link(source=gitconfig_path)

    gitignore_path.unlink()
    gitconfig_path.unlink()

    project.restore()

    # Check dotfiles
    assert gitignore_path.is_symlink()
    assert gitignore_path.readlink() == Path(project.path, "global.ignore")
    assert gitignore_path.read_text() == ".venv/"

    assert gitconfig_path.is_symlink()
    assert gitconfig_path.readlink() == Path(project.path, ".gitconfig")
    assert gitconfig_path.read_text() == "username: Me"

    # Check Project
    project_content = os.listdir(project.path)
    assert "global.ignore" in project_content
    assert ".gitconfig" in project_content
    assert len(project_content) == 3

    # Check Config
    project_2 = Project.from_path(project.path)
    assert project_2 == project


def test_restore_with_empty_config(tmp_path):
    home = Path(tmp_path, "home")
    project_path = Path(home, "projects", "git")
    ensure_folder_tree(
        folders=[project_path],
    )
    project = Project.init(project_path)
    project._home = home
    project.restore()

    # Check Project
    project_content = os.listdir(project.path)
    assert project_content == [project._config_file]

    # Config
    project_2 = Project.from_path(project.path)
    assert project_2 == project
    assert project.config.links == {}


def test_restore_with_existing_file(tmp_path):
    home = Path(tmp_path, "home")
    config_path = Path(home, "git-config")
    gitconfig_path = Path(config_path, ".gitconfig")
    project_path = Path(home, "projects", "git")
    ensure_folder_tree(
        folders=[project_path],
        files=[(gitconfig_path, "username: Me")],
    )
    project = Project.init(project_path)
    project._home = home
    project.add_link(source=gitconfig_path)
    gitconfig_path.unlink()
    ensure_folder_tree(
        files=[(gitconfig_path, "username: Me")],
    )
    with pytest.raises(ProjectException):
        project.restore()

    # Check Dotfiels
    assert gitconfig_path.is_file()
    assert not gitconfig_path.is_symlink()

    # Check Project
    project_content = os.listdir(project.path)
    assert project._config_file in project_content
    assert gitconfig_path.name in project_content
    assert len(project_content) == 2

    # Config
    project_2 = Project.from_path(project.path)
    assert project_2 == project


def test_restore_with_missing_target(tmp_path):
    home = Path(tmp_path, "home")
    config_path = Path(home, "git-config")
    gitconfig_path = Path(config_path, ".gitconfig")
    project_path = Path(home, "projects", "git")
    ensure_folder_tree(
        folders=[project_path],
        files=[(gitconfig_path, "username: Me")],
    )
    project = Project.init(project_path)
    project._home = home
    project.add_link(source=gitconfig_path)
    with pytest.raises(ProjectException):
        project.restore_link("other")
