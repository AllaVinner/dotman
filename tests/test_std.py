# Ensure common functions works as expexted
from pathlib import Path
import shutil


def test_copytree_folder(tmp_path: Path) -> None:
    folder = Path(tmp_path, "folder")
    folder.mkdir()
    file_a = Path(folder, "a")
    file_a.write_text("File A")

    shutil.move(folder, Path(tmp_path, "b"))
    assert Path(tmp_path, "b/a").exists()
    assert Path(tmp_path, "b/a").read_text() == "File A"


def test_copytree_file(tmp_path: Path) -> None:
    file_a = Path(tmp_path, "a")
    file_a.write_text("File A")

    shutil.move(file_a, Path(tmp_path, "b"))
    assert Path(tmp_path, "b").exists()
    assert Path(tmp_path, "b").read_text() == "File A"
