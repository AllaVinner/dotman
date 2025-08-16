import pytest


from pathlib import Path
from dotman.exceptions import DotmanException
from dotman.init import init
from dotman.config import CONFIG_FILE_NAME
import os


def test_init(tmp_path: Path):
    project_path = Path(tmp_path, "project")
    project_path.mkdir()
    assert os.listdir(project_path) == []
    init(project_path)
    assert os.listdir(project_path) == [CONFIG_FILE_NAME]
    assert Path(project_path, CONFIG_FILE_NAME).read_text() == "[dotfiles]\n"


def test_already_existing(tmp_path: Path):
    project_path = Path(tmp_path, "project")
    project_path.mkdir()
    init(project_path)
    with pytest.raises(DotmanException) as ex_info:
        init(project_path)
    assert ex_info.value.message == "Dotman project already initialized"
