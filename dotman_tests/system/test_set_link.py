from pathlib import Path
import os
import pytest
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project, ProjectException


def test_set_link(tmp_path):
    home = Path(tmp_path, "home")
    config_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(config_file, "in vimrc")])
    project_path = Path(projects, "vim")
    project = Project.init(project_path)
    project._home = home
    project.add_link(config_file)
    config_file.unlink()
    project.full_config_path.unlink()
    project = Project.init(project_path)
    project._home = home
    assert project.config.links == {}

    project.set_link(config_file)

    # Check Dotfiles
    assert config_file.is_file()
    assert config_file.is_symlink()

    # Check Project
    project_content = os.listdir(project.path)
    assert config_file.name in project_content
    assert project._config_file in project_content
    assert len(project_content) == 2

    # Check Config
    assert project.config.model_dump() == {
        "links": {
            config_file.name: {"source": Path("~", config_file.relative_to(home))}
        }
    }


def test_set_link_with_missing_target(tmp_path):
    home = Path(tmp_path, "home")
    config_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(config_file, "in vimrc")])
    project_path = Path(projects, "vim")
    project = Project.init(project_path)
    project._home = home
    project.add_link(config_file)
    config_file.unlink()
    project.full_config_path.unlink()
    project = Project.init(project_path)
    project._home = home
    assert project.config.links == {}

    with pytest.raises(ProjectException):
        project.set_link(config_file, "other")

    # Check Dotfiles
    assert not config_file.exists()

    # Check Project
    project_content = os.listdir(project.path)
    assert config_file.name in project_content
    assert project._config_file in project_content
    assert len(project_content) == 2

    # Check Config
    assert project.config.model_dump() == {"links": {}}


def test_set_link_with_exising_source(tmp_path):
    home = Path(tmp_path, "home")
    config_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(config_file, "in vimrc")])
    project_path = Path(projects, "vim")
    project = Project.init(project_path)
    project._home = home
    project.add_link(config_file)
    project.full_config_path.unlink()
    project = Project.init(project_path)
    project._home = home
    assert project.config.links == {}

    with pytest.raises(ProjectException):
        project.set_link(config_file)

    # Check Dotfiles
    assert config_file.exists()

    # Check Project
    project_content = os.listdir(project.path)
    assert config_file.name in project_content
    assert project._config_file in project_content
    assert len(project_content) == 2

    # Check Config
    assert project.config.model_dump() == {"links": {}}
