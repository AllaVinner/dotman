from pathlib import Path
import pytest
import os
import json
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project, ProjectException, ENV_HOME


def test_migrating_config(tmp_path):
    home = Path(tmp_path, "home")
    os.environ[ENV_HOME] = home.as_posix()
    config = Path(home, "config")
    nvim = Path(config, "nvim")
    init_lua = Path(nvim, "init.lua")
    tmux = Path(config, "tmux.conf")
    projects = Path(home, "projects")
    ensure_folder_tree(
        folders=[projects],
        files=[
            (init_lua, "init.lua file"),
            (tmux, "tmux config"),
        ],
    )
    project_path = Path(projects, "config")
    project = Project.init(Path(projects, "vim"))

    project.add_link(nvim)
    project.add_link(tmux)

    # Check Dotfiles
    assert nvim.is_symlink()
    assert nvim.is_dir()
    assert init_lua.is_file()
    assert nvim.readlink() == Path(project.path, nvim.name)
    assert tmux.is_symlink()
    assert tmux.is_file()
    assert tmux.readlink() == Path(project.path, tmux.name)

    # Check Project
    project_content = os.listdir(project.path)
    assert nvim.name in project_content
    assert tmux.name in project_content
    assert project._config_file in project_content

    # Check Config
    with open(project.full_config_path, "r") as f:
        config_json = json.load(f)
    assert config_json == {
        "links": {
            "nvim": {"source": "~/config/nvim"},
            "tmux.conf": {"source": "~/config/tmux.conf"},
        }
    }

    status = project.status()
    assert status == {
        "nvim": "Complete",
        "tmux.conf": "Complete",
    }
