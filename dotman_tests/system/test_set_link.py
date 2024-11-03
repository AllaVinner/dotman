from pathlib import Path
import json
import shutil
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project


def test_set_link(tmp_path):
    home = Path(tmp_path, "home")
    config_file = Path(home, "config", "vimrc")
    projects = Path(home, "projects")
    ensure_folder_tree(folders=[projects], files=[(config_file, "in vimrc")])

    project_path = Path(projects, "vim")
    project = Project.init(Path(projects, "vim"))
    project._home = home
    project.add_link(config_file)
    config_file.unlink()

    new_project_path = Path(projects, "vim2")
    shutil.move(project_path, new_project_path)
    shutil.rmtree(Path(new_project_path, project._dotman_dir))

    new_project = Project.init(new_project_path)
    new_project._home = home

    assert not project_path.exists()
    assert new_project_path.exists()
    assert len(new_project.config.links.keys()) == 0

    new_project.set_link(config_file, config_file.name)

    assert config_file.is_symlink()
    assert config_file.readlink() == Path(new_project.path, "vimrc")
    assert config_file.read_text() == "in vimrc"

    assert new_project.full_config_path.is_file()
    with open(Path(new_project.full_config_path), "r") as f:
        config = json.load(f)
    assert config == {
        "links": {"vimrc": {"source": config_file.relative_to(home).as_posix()}}
    }
