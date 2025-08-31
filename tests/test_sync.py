from pathlib import Path
from dotman.sync import sync, sync_project
from dotman.context import Context, managed_context
from dotman.examples import setup_folder_structure


def test_full_project_with_copies(tmp_path: Path) -> None:
    paths = setup_folder_structure(Path(tmp_path, "root"), stage="complete-with-copy")
    with managed_context(Context(home=paths.home, cwd=paths.project)):
        paths.bashrc.write_text("This Is Updated")
        assert paths.bashrc.read_text() == "This Is Updated"
        assert paths.project_bashrc.read_text() != "This Is Updated"
        sync(paths.project_bashrc.name)
        assert paths.bashrc.read_text() == "This Is Updated"
        assert paths.project_bashrc.read_text() == "This Is Updated"

        assert paths.project_tmux_config.read_text() != "This Is Updated More"
        paths.tmux_config.write_text("This Is Updated More")
        sync_project()
        assert paths.project_tmux_config.read_text() == "This Is Updated More"
