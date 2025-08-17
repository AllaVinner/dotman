from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
import toml

from dotman.exceptions import DotmanException


CONFIG_FILE_NAME = ".dotman.toml"

DotfilePath = Path


class Config(BaseModel):
    dotfiles: dict[DotfilePath, DotfilePath] = Field(default_factory=lambda: dict())

    @classmethod
    def from_project(cls, project: Path | str) -> Config:
        project = Path(project)
        config_path = Path(project, CONFIG_FILE_NAME)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = toml.load(f)
        except FileNotFoundError:
            raise DotmanException(
                f"Path {project.as_posix()} is not a dotman project. Please run `dotman init`."
            )
        try:
            config = Config.model_validate(config_dict)
        except ValidationError as e:
            raise DotmanException(str(e))
        return config

    def write(self, path: Path) -> None:
        config_dict = self.model_dump(mode="json", exclude_unset=True)
        if config_dict == dict():
            config_dict = self.__class__(dotfiles=dict()).model_dump(mode="json")
        with open(path, "w", encoding="utf-8") as f:
            toml.dump(config_dict, f)
