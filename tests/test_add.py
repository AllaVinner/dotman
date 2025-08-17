from pathlib import Path

from dotman.add import add
from dotman.config import Config
from dotman.context import Context, managed_context
from dotman.init import init


def test_basic(tmp_path: Path) -> None:
    root = Path(tmp_path, "root")
    home = Path(root, "home")
    project = Path(home, "project")
    dot_config = Path(home, "dot_config")
    tmux_dir = Path(dot_config, "tmux")
    bashrc = Path(home, "bashrc")
    tmux_config = Path(tmux_dir, "tmux.conf")

    for path in [root, home, project, dot_config, tmux_dir]:
        path.mkdir(parents=True, exist_ok=True)
    for path in [bashrc, tmux_config]:
        path.write_text("ORIGIN: " + path.name)
    with managed_context(Context(cwd=project, home=home, root=root)):
        init(project=project)
        add(project=project, dotfile=bashrc)
        assert bashrc.exists()
        assert bashrc.is_symlink()
        assert Path(project, bashrc.name).exists()
        assert Path(project, bashrc.name).read_text() == f"ORIGIN: {bashrc.name}"
        config = Config.from_project(project)
        assert Path(bashrc.name) in config.dotfiles
        assert config.dotfiles[Path(bashrc.name)] == Path("~/bashrc")

        add(project=project, dotfile=tmux_dir)
        assert tmux_dir.exists()
        assert tmux_dir.is_symlink()
        assert Path(project, tmux_dir.name).exists()
        assert Path(project, tmux_dir.name).is_dir()
        assert Path(project, tmux_dir.name, tmux_config.name).exists()
        assert (
            Path(project, tmux_dir.name, tmux_config.name).read_text()
            == f"ORIGIN: {tmux_config.name}"
        )
        config = Config.from_project(project)
        assert Path(tmux_dir.name) in config.dotfiles
        assert config.dotfiles[Path(tmux_dir.name)] == Path("~/dot_config/tmux")
