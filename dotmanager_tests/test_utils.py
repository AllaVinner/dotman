from typing import List, Tuple
from pathlib import Path


def ensure_folder_tree(
    folders: List[Path] | None = None, files: List[Tuple[Path, str]] | None = None
) -> None:
    """Assumes paths with suffixes are files."""
    if folders is None:
        folders = []
    if files is None:
        files = []
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
    for path, content in files:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
    for folder in folders:
        assert folder.exists, f"Path '{path.as_posix()}' should exists by now"
    for path, content in files:
        assert path.exists, f"Path '{path.as_posix()}' should exists by now"
