from pydantic import BaseModel, Field, config, ValidationError
from dataclasses import dataclass
from typing import Self

import shutil
from dataclasses import dataclass
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


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
            raise ProjectException(
                f"Given project path already exists as a file. "
                f"Project path: {project_path.as_posix}"
            )
        if not project_path.exists():
            logger.info(f"Creating project folder at: {project_path.as_posix()}")
            project_path.mkdir(parents=True)
        config = Config(links={})
        self = cls(path=project_path, config=config)
        if Path(project_path, cls._config_file).exists():
            raise ProjectException(
                f"Given project path is already a dotman project. "
                f"Project path: {project_path.as_posix()}"
            )
        self.write()
        return self

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        if not project_path.is_dir():
            raise ProjectException(
                f"Given project path is not a directory. "
                f"Project Path: {project_path.as_posix()}"
            )
        config_file = Path(project_path, cls._config_file)
        if not config_file.is_file():
            raise ProjectException(
                f"Cannot find config in project. "
                f"Project Path: {project_path.as_posix()}"
            )
        with open(config_file, "r") as f:
            config_content = f.read()
        try:
            config = Config.model_validate_json(config_content)
        except ValidationError as e:
            raise ProjectException(
                f"{e}"
                f"Config file at {config_file.as_posix()} is corrupted. "
                f"Parsing failed with the above validation error."
            )
        return cls(path=project_path, config=config)

    def write(self):
        config_path = Path(self.path, self._config_file)
        logger.info(f"Writing config file at: {config_path.as_posix()}")
        with open(config_path, "w") as f:
            f.write(self.config.model_dump_json())

    def add_link(self, source: Path, target_name: str | None = None) -> None:
        # TODO: Fix issue where you try to add the same source twice,
        # but with different target names.
        if target_name is None:
            logger.debug(
                f"Setting target name to {source.name}, "
                f"inferred from source path {source.as_posix()}"
            )
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
            # TODO: Make some tests to see how resolve
            # behave over .. and symlinks
            home_to_source_path = source.resolve().relative_to(self._home)
        except ValueError:
            # TODO: Allow for root paths, maybe more?
            raise ProjectException("Source must be relative to home.")
        logger.info(f"Moving source {source.as_posix()} to {target_path.as_posix()}.")
        shutil.move(source, target_path)
        logger.info(
            f"Creating symlink from {source.as_posix()} to {target_path.as_posix()}."
        )
        source.symlink_to(target_path.absolute())

        self.config.links[target_name] = Link(source=Path("~", home_to_source_path))
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

    def status(self):
        link_status_dict = {}
        for target_name, link in self.config.links.items():
            full_path = Path(self._home, link.source)
            if not self.path.joinpath(target_name).exists():
                link_status = "Dotfile not in project folder."
            elif not full_path.is_symlink():
                link_status = "Link does not exist."
            elif (
                not full_path.resolve().relative_to(self.path.resolve()).as_posix()
                == target_name
            ):
                link_status = "Link does not point to project dotfile."
            else:
                link_status = "Complete"
            link_status_dict[target_name] = link_status
        return link_status_dict
