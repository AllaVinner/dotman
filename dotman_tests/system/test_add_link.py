from pathlib import Path
import json
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project


def test_linking(tmp_path):
    home = Path(tmp_path, "home")
    config_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(config_file, "in vimrc")])

    project = Project.init(Path(projects, "vim"))
    project._home = home
    project.add_link(config_file)

    assert config_file.is_symlink()
    assert config_file.readlink() == Path(project.path, "vimrc")
    assert config_file.read_text() == "in vimrc"

    assert project.full_config_path.is_file()
    with open(Path(project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {"vimrc": {"source": config_file.relative_to(home).as_posix()}}
    }
