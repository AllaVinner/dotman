import pytest


from pathlib import Path
from dotman.examples import setup_folder_structure
from dotman.exceptions import DotmanException
from dotman.init import init
from dotman.config import CONFIG_FILE_NAME
import os


def test_init(tmp_path: Path):
    with setup_folder_structure(Path(tmp_path, "root"), stop_after="setup") as paths:
        init(paths.project)
        assert os.listdir(paths.project) == [CONFIG_FILE_NAME]
        assert paths.project_config.read_text() == "[dotfiles]\n"


def test_already_existing(tmp_path: Path):
    with setup_folder_structure(Path(tmp_path, "root"), stop_after="init") as paths:
        with pytest.raises(DotmanException) as ex_info:
            init(paths.project)
        assert ex_info.value.message == "Dotman project already initialized"
