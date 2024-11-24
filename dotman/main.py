from pydantic import BaseModel, Field, config
import click
from dataclasses import dataclass
import os
from typing import Self

import shutil
from dataclasses import dataclass
import json
from pathlib import Path


class ProjectException(Exception):
    pass


class Link(BaseModel):
    source: Path


class Config(BaseModel):
    links: dict[str, Link]


@dataclass
class Project:
    path: Path
    config: Config
    _home = Path.home()
    _config_file = ".dotman.json"

    @property
    def config_path(self) -> Path:
        return Path(self._config_file)

    @property
    def full_config_path(self) -> Path:
        return Path(self.path, self.config_path)

    @classmethod
    def init(cls, project_path: Path) -> Self:
        if project_path.is_file():
            raise ProjectException("Given project path already exists as a file.")
        elif not project_path.is_dir():
            project_path.mkdir(parents=True)
        config = Config(links={})
        self = cls(path=project_path, config=config)
        if Path(project_path, cls._config_file).exists():
            raise ProjectException("Given path is already a dotman project.")
        self.write()
        return self

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        if not project_path.is_dir():
            raise ProjectException("Given project path is not a directory")
        config_file = Path(project_path, cls._config_file)
        if not config_file.is_file():
            raise ProjectException("Cannot find config in project")
        with open(config_file, "r") as f:
            config_content = f.read()
        config = Config.model_validate_json(config_content)
        return cls(path=project_path, config=config)

    def write(self):
        with open(Path(self.path, self._config_file), "w") as f:
            f.write(self.config.model_dump_json())

    def add_link(self, source: Path, target_name: str | None = None) -> None:
        if target_name is None:
            target_name = source.name
        if target_name in self.config.links:
            raise ProjectException(
                f"Target {target_name} already exists in project config."
            )
        target_path = Path(self.path, target_name)
        if target_path.exists():
            raise ProjectException(f"Target {target_name} already exists in project.")
        if not source.exists():
            raise ProjectException(f"Source {source} does not exists.")
        try:
            home_to_source_path = source.absolute().relative_to(self._home)
        except ValueError:
            raise ProjectException("Source must be relative to home.")

        shutil.move(source, target_path)
        source.symlink_to(target_path.absolute())

        self.config.links[target_name] = Link(source=home_to_source_path)
        self.write()

    def restore_link(self, link_name: str) -> None:
        if link_name not in self.config.links:
            raise ProjectException(f"Could not find link 'link_name' in project.")
        link = self.config.links[link_name]
        full_link_path = Path(self._home, link.source)
        if full_link_path.exists() or full_link_path.is_symlink():
            raise ProjectException(
                f"Cannot restore link. Already file at links source."
            )
        if not full_link_path.parent.exists():
            full_link_path.parent.mkdir(parents=True)
        full_link_path.symlink_to(Path(self.path, link_name).absolute())

    def restore(self):
        for link_name in self.config.links:
            self.restore_link(link_name)

    def set_link(self, source_path: Path, target_name: str) -> None:
        target_path = Path(self.path, target_name)
        if not target_path.exists():
            raise ProjectException(f"Link target {target_name} does not exist.")
        if source_path.exists():
            raise ProjectException(f"Source exists. {source_path}")
        try:
            home_to_source_path = source_path.relative_to(self._home)
        except ValueError:
            raise ProjectException("Source must be relative to home.")

        source_path.symlink_to(target_path.absolute())
        self.config.links[target_name] = Link(source=home_to_source_path)
        self.write()
