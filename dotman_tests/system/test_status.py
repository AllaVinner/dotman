from pathlib import Path
from dotman_tests.test_utils import ensure_folder_tree

from dotman.main import Project, Config, ProjectException


def test_status(tmp_path):
    home = Path(tmp_path, "home")
    complete_dotfile = Path(home, "config", "complete")
    missing_dotfile = Path(home, "config", "missing")
    missing_dotfile_link = Path(home, "config", "missing_link")
    misdirected_dotfile_link = Path(home, "config", "miss_directed")
    projects = Path(home, "projects")
    ensure_folder_tree(
        folders=[projects],
        files=[
            (complete_dotfile, "in vimrc"),
            (missing_dotfile, "in vimrc"),
            (missing_dotfile_link, "in vimrc"),
            (misdirected_dotfile_link, "in vimrc"),
        ],
    )
    project_path = Path(projects, "vim")
    project = Project.init(project_path)
    project._home = home
    project.add_link(complete_dotfile)
    project.add_link(missing_dotfile)
    project.add_link(missing_dotfile_link)
    project.add_link(misdirected_dotfile_link)

    missing_dotfile.unlink()
    Path(project.path, missing_dotfile_link.name).unlink()
    misdirected_dotfile_link.unlink()
    misdirected_dotfile_link.symlink_to(complete_dotfile)

    project.refresh()
    status = project.status()
    assert "Complete" in status[complete_dotfile.name]
    assert "Dotfile not in project folder." in status[missing_dotfile_link.name]
    assert "Link does not exist." in status[missing_dotfile.name]
    assert (
        "Link does not point to project dotfile."
        in status[misdirected_dotfile_link.name]
    )
