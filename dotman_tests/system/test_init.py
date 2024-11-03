from pathlib import Path
import json
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project


def test_init(tmp_path):
    home = Path(tmp_path, "home")
    config_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(config_file, "in vimrc")])
    project_path = Path(projects, "vim")

    project = Project.init(project_path)

    assert project_path.is_dir()
    assert project.full_dotman_path.is_dir()
    assert project.full_config_path.is_file()
    with open(project.full_config_path, "r") as f:
        config = json.load(f)
    assert config == {"links": {}}
