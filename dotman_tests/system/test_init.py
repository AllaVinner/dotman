from pathlib import Path
import pytest
import json
import os
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project, Config, ProjectException


def test_non_existing_folder(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects])
    project_path = Path(projects, "vim")
    assert not project_path.exists()
    project = Project.init(project_path)
    assert project_path.is_dir()
    config_path = Path(project_path, project._config_file)
    assert config_path.is_file()
    with open(config_path, "r") as f:
        config_json = json.load(f)
    config = Config.model_validate(config_json)
    assert config == project.config
    assert os.listdir(project_path) == [config_path.name]


def test_existing_folder(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    project_path = Path(projects, "vim")
    ensure_folder_tree(folders=[project_path])
    assert project_path.exists()
    project = Project.init(project_path)
    assert project_path.is_dir()
    config_path = Path(project_path, project._config_file)
    assert config_path.is_file()
    with open(config_path, "r") as f:
        config_json = json.load(f)
    config = Config.model_validate(config_json)
    assert config == project.config
    assert os.listdir(project_path) == [config_path.name]


def test_err_existing_folder_as_file(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    project_path = Path(projects, "vim.txt")
    ensure_folder_tree(folders=[projects], files=[(project_path, "Some")])
    assert project_path.exists()
    assert project_path.is_file()
    with pytest.raises(ProjectException):
        _project = Project.init(project_path)


def test_err_existing_folder_as_symlink(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects])
    project_path = Path(projects, "vim.txt")
    project_path.symlink_to(home)
    assert project_path.exists()
    assert project_path.is_symlink()
    assert project_path.is_dir()
    with pytest.raises(ProjectException):
        _project = Project.init(project_path)


def test_err_existing_folder_with_config(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    project_path = Path(projects, "vim")
    config_path = Path(project_path, Project._config_file)
    config_content = "blabla"
    ensure_folder_tree(folders=[project_path], files=[(config_path, config_content)])
    with pytest.raises(ProjectException):
        _project = Project.init(project_path)
    with open(config_path, "r") as f:
        actual_config_content = f.read()
    assert actual_config_content == config_content
