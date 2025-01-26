from pathlib import Path
import pytest
import os
import json
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project, ProjectException


def test_from_path(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects])
    project = Project.init(Path(projects, "vim"))
    project_2 = Project.from_path(project.path)

    assert project_2 == project


def test_from_non_project_path(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    project_path = Path(projects, "vim")
    ensure_folder_tree(folders=[project_path])
    with pytest.raises(ProjectException):
        _project = Project.from_path(project_path)


def test_from_faulty_project_path(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects])
    project = Project.init(Path(projects, "vim"))
    project.config
    with open(project.full_config_path, "r") as f:
        config_json = json.load(f)
    config_json["links"] = {"link_name": "some bad value"}
    with open(project.full_config_path, "w") as f:
        json.dump(config_json, f)
    with pytest.raises(ProjectException):
        _project = Project.from_path(project.path)


def test_from_missing_project_path(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects])
    project_path = Path(projects, "vim")
    with pytest.raises(ProjectException):
        _project = Project.from_path(project_path)


def test_from_file_project_path(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    project_path = Path(projects, "vim")
    ensure_folder_tree(folders=[projects], files=[(project_path, "aa")])
    with pytest.raises(ProjectException):
        _project = Project.from_path(project_path)


def test_from_symlink_project_path(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    dotfile = Path(home, "dotfile.txt")
    ensure_folder_tree(folders=[projects], files=[(dotfile, "aa")])
    project = Project.init(Path(projects, "vim"))
    project.add_link(dotfile)
    link_path = Path(home, "link_to_project")
    link_path.symlink_to(project.path)
    project_2 = Project.from_path(link_path)
    assert project_2.path != project.path
    assert project_2.path == link_path
    assert project_2.config == project.config
