from pathlib import Path
import json
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project


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

    assert gitignore_path.is_symlink()
    assert gitignore_path.readlink() == Path(project.path, "global.ignore")
    assert gitignore_path.read_text() == ".venv/"

    assert gitconfig_path.is_symlink()
    assert gitconfig_path.readlink() == Path(project.path, ".gitconfig")
    assert gitconfig_path.read_text() == "username: Me"

    gitignore_path.unlink()
    gitconfig_path.unlink()

    project.restore()

    assert gitignore_path.is_symlink()
    assert gitignore_path.readlink() == Path(project.path, "global.ignore")
    assert gitignore_path.read_text() == ".venv/"

    assert gitconfig_path.is_symlink()
    assert gitconfig_path.readlink() == Path(project.path, ".gitconfig")
    assert gitconfig_path.read_text() == "username: Me"
