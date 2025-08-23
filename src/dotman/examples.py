from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal

from dotman.add import add
from dotman.config import CONFIG_FILE_NAME
from dotman.context import Context, Platform, managed_context
from dotman.init import init
from dotman.util import resolve_path


Stage = Literal["first-time", "add", "complete", "new-machine"]


@dataclass
class BasicPaths:
    root: Path
    home: Path
    bashrc: Path
    dot_config: Path
    tmux_dir: Path
    tmux_config: Path
    project: Path
    project_config: Path
    project_bashrc: Path
    project_tmux_dir: Path
    project_tmux_config: Path

    @classmethod
    def from_root(cls, root_path: Path | str) -> BasicPaths:
        root_path = Path(root_path)
        return cls(
            root=Path(root_path),
            home=Path(root_path, "home"),
            bashrc=Path(root_path, "home/bashrc"),
            dot_config=Path(root_path, "home/dot_config"),
            tmux_dir=Path(root_path, "home/dot_config/tmux"),
            tmux_config=Path(root_path, "home/dot_config/tmux/tmux.conf"),
            project=Path(root_path, "home/project"),
            project_bashrc=Path(root_path, "home/project/bashrc"),
            project_tmux_dir=Path(root_path, "home/project/tmux"),
            project_tmux_config=Path(root_path, "home/project/tmux/tmux.conf"),
            project_config=Path(root_path, "home/project", CONFIG_FILE_NAME),
        )


def setup_folder_structure(
    root_folder: Path | str,
    stage: Stage,
) -> BasicPaths:
    paths = BasicPaths.from_root(resolve_path(root_folder))
    for path in [
        paths.root,
        paths.home,
        paths.project,
        paths.dot_config,
        paths.tmux_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)
    for path in [paths.bashrc, paths.tmux_config]:
        path.write_text("ORIGIN: " + path.name)
    if stage == "first-time":
        return paths
    init(project=paths.project)
    if stage == "add":
        return paths
    add(project=paths.project, dotfile=paths.bashrc)
    add(project=paths.project, dotfile=paths.tmux_dir)
    if stage == "complete":
        return paths
    paths.bashrc.unlink()
    paths.tmux_dir.unlink()
    if stage == "new-machine":
        return paths


@contextmanager
def managed_setup(base_dir: Path | str, stage: Stage) -> Iterator[BasicPaths]:
    with managed_context(
        context=Context(
            cwd=Path(base_dir, "home/project"),
            home=Path(base_dir, "home"),
            platform=Platform.windows,
        )
    ):
        yield setup_folder_structure(base_dir, stage=stage)
