from pathlib import Path
import pytest
import os
import json
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import ENV_HOME, Project, ProjectException


def test_linking_file_source(tmp_path):
    home = Path(tmp_path, "home")
    dot_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(dot_file, "in vimrc")])
    project = Project.init(Path(projects, "vim"))
    project._home = home
    project.add_link(dot_file)

    # Check Dotfile
    assert dot_file.is_symlink()
    assert dot_file.readlink() == Path(project.path, "vimrc")
    assert dot_file.read_text() == "in vimrc"

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert "vimrc" in project_folder_content
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 2

    # Check Config
    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {"vimrc": {"source": Path("~", dot_file.relative_to(home)).as_posix()}}
    }


def test_linking_folder_source(tmp_path):
    home = Path(tmp_path, "home")
    dot_folder = Path(home, "config", "nvim")
    dot_file = Path(home, "config", "nvim", "init.lua")
    dotfile_content = "in dotfile"
    projects = Path(home, "projects")
    ensure_folder_tree(
        folders=[projects, dot_folder], files=[(dot_file, dotfile_content)]
    )
    project = Project.init(Path(projects, "nvim"))
    project._home = home
    project.add_link(dot_folder)

    # Check Dotfile
    assert dot_folder.is_symlink()
    assert dot_folder.readlink() == Path(project.path, dot_folder.name)
    assert dot_file.is_file()
    assert dot_file.read_text() == dotfile_content

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert dot_folder.name in project_folder_content
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 2
    project_dotfile_path = Path(project.path, dot_folder.name, dot_file.name)
    assert project_dotfile_path.is_file()
    assert project_dotfile_path.read_text() == dotfile_content

    # Check Config
    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {
            "nvim": {"source": Path("~", dot_folder.relative_to(home)).as_posix()}
        }
    }


def test_linking_symlink_source(tmp_path):
    home = Path(tmp_path, "home")
    documents = Path(home, "documents")
    dotfile = Path(documents, "dotfile")
    dotfile_link = Path(home, "config", "dotfile_link")
    dotfile_content = "in dotfile"
    projects = Path(home, "projects")
    ensure_folder_tree(
        folders=[projects, dotfile_link.parent], files=[(dotfile, dotfile_content)]
    )
    dotfile_link.symlink_to(dotfile)
    assert dotfile_link.is_symlink()
    assert dotfile.read_text() == dotfile_content

    project = Project.init(Path(projects, "nvim"))
    project._home = home
    project.add_link(dotfile_link)

    # Check Dotfile
    assert dotfile_link.is_symlink()

    print(dotfile_link.readlink())
    print(project.path)
    assert dotfile_link.readlink() == Path(project.path, dotfile_link.name)
    assert dotfile_link.is_file()
    assert dotfile_link.read_text() == dotfile_content

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert dotfile_link.name in project_folder_content
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 2
    assert Path(project.path, dotfile_link.name).is_symlink()

    # Check Config
    assert project.full_config_path.is_file()
    print(project.config)
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {
            "dotfile_link": {
                "source": Path("~", dotfile_link.relative_to(home)).as_posix()
            }
        }
    }


def test_linking_with_target(tmp_path):
    home = Path(tmp_path, "home")
    dot_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(dot_file, "in vimrc")])
    project = Project.init(Path(projects, "vim"))
    target_name = "vimrc2"
    project._home = home
    project.add_link(dot_file, target_name)

    # Check Dotfile
    assert dot_file.is_symlink()
    assert dot_file.readlink() == Path(project.path, target_name)
    assert dot_file.read_text() == "in vimrc"

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert target_name in project_folder_content
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 2

    # Check Config
    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {
            target_name: {"source": Path("~", dot_file.relative_to(home)).as_posix()}
        }
    }


def test_linking_multiple_source(tmp_path):
    home = Path(tmp_path, "home")
    os.environ[ENV_HOME] = home.as_posix()
    dotfile_1 = Path(home, "config", "dotfile1")
    dotfile_2 = Path(home, "config", "dotfile2")
    dotfile_1_content = "in dotfile 1"
    dotfile_2_content = "in dotfile 2"
    projects = Path(home, "projects")
    ensure_folder_tree(
        folders=[projects],
        files=[(dotfile_1, dotfile_1_content), (dotfile_2, dotfile_2_content)],
    )
    project = Project.init(Path(projects, "vim"))
    project.add_link(dotfile_1)
    project.add_link(dotfile_2)

    # Check Dotfile
    assert dotfile_1.is_symlink()
    assert dotfile_1.readlink() == Path(project.path, dotfile_1.name)
    assert dotfile_1.read_text() == dotfile_1_content
    assert dotfile_2.is_symlink()
    assert dotfile_2.readlink() == Path(project.path, dotfile_2.name)
    assert dotfile_2.read_text() == dotfile_2_content

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert dotfile_1.name in project_folder_content
    assert dotfile_2.name in project_folder_content
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 3

    # Check Config
    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {
            "dotfile1": {"source": Path("~", dotfile_1.relative_to(home)).as_posix()},
            "dotfile2": {"source": Path("~", dotfile_2.relative_to(home)).as_posix()},
        }
    }


def test_err_linking_with_existing_target(tmp_path):
    home = Path(tmp_path, "home")
    dotfile_1 = Path(home, "config", "dotfile1")
    dotfile_2 = Path(home, "config", "dotfile2")
    dotfile_1_content = "in dotfile 1"
    dotfile_2_content = "in dotfile 2"
    projects = Path(home, "projects")
    ensure_folder_tree(
        folders=[projects],
        files=[(dotfile_1, dotfile_1_content), (dotfile_2, dotfile_2_content)],
    )
    project = Project.init(Path(projects, "vim"))
    project._home = home
    project.add_link(dotfile_1)
    with pytest.raises(ProjectException):
        project.add_link(dotfile_2, target_name=dotfile_1.name)

    # Check Dotfile
    assert dotfile_1.is_symlink()
    assert dotfile_1.readlink() == Path(project.path, dotfile_1.name)
    assert dotfile_1.read_text() == dotfile_1_content
    assert not dotfile_2.is_symlink()
    assert dotfile_2.is_file()
    assert dotfile_2.read_text() == dotfile_2_content

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert dotfile_1.name in project_folder_content
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 2

    # Check Config
    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {
            "dotfile1": {"source": Path("~", dotfile_1.relative_to(home)).as_posix()},
        }
    }


def test_err_linking_with_missing_source(tmp_path):
    home = Path(tmp_path, "home")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects])
    dot_file = Path(home, "config", "vimrc")
    project = Project.init(Path(projects, "vim"))
    project._home = home
    with pytest.raises(ProjectException):
        project.add_link(dot_file)

    # Check Dotfile
    assert not dot_file.exists()

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 1

    # Check Config
    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {"links": {}}


def test_linking_with_tilde(tmp_path):
    home = Path(tmp_path, "home")
    os.environ[ENV_HOME] = home.as_posix()
    projects = Path(home, "projects")
    dotfile = Path(home, "config", "vimrc")
    ensure_folder_tree(folders=[projects], files=[(dotfile, "vimrc content")])
    project = Project.init(Path(projects, "vim"))
    dotfile_tilde = Path("~", Path(*dotfile.parts[-2:]))
    project.add_link(dotfile_tilde)

    # Check Dotfile
    assert dotfile.is_symlink()
    assert not dotfile_tilde.exists()

    # Check Project
    project_folder_content = os.listdir(project.path)
    assert dotfile_tilde.name in project_folder_content
    assert project._config_file in project_folder_content
    assert len(project_folder_content) == 2

    # Check Config
    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {"links": {"vimrc": {"source": "~/config/vimrc"}}}
    project_2 = Project.from_path(project.path)
    assert project_2 == project
