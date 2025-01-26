from pydantic import BaseModel, Field, config, ValidationError
import os
import json
from dataclasses import dataclass
from typing import Self

import shutil
from dataclasses import dataclass
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

ENV_HOME = "DOTMAN_HOME"


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

    def __post_init__(self):
        os_env_home = os.getenv(ENV_HOME)
        if os_env_home:
            self._home = Path(os_env_home)

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
        for link_name in config.links.keys():
            source = config.links[link_name].source
            if source.parts[0] == "~":
                source = Path(*source.parts[1:])
            config.links[link_name].source = source
        return cls(path=project_path, config=config)

    def write(self):
        config_path = Path(self.path, self._config_file)
        logger.info(f"Writing config file at: {config_path.as_posix()}")
        model_json = self.config.model_dump(mode="json")
        # TODO: Handle in an annotated serializing in a custom Path object instead
        for link_name in model_json["links"].keys():
            model_json["links"][link_name]["source"] = Path(
                "~", model_json["links"][link_name]["source"]
            ).as_posix()
        with open(config_path, "w") as f:
            json.dump(model_json, f)

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
            # TODO: Make this prettier
            # TODO: Make some tests to see how resolve
            # behave over .. and symlinks
            fake_source = Path(Path(*source.parts[:-1]), "xxx")
            fake_source = fake_source.resolve().relative_to(self._home)
            home_to_source_path = Path(Path(*fake_source.parts[:-1]), source.name)
        except ValueError:
            # TODO: Allow for root paths, maybe more?
            raise ProjectException("Source must be relative to home.")
        logger.info(f"Moving source {source.as_posix()} to {target_path.as_posix()}.")
        shutil.move(source, target_path)
        logger.info(
            f"Creating symlink from {source.as_posix()} to {target_path.as_posix()}."
        )
        source.symlink_to(target_path)
        self.config.links[target_name] = Link(source=home_to_source_path)
        self.write()

    def restore_link(self, link_name: str) -> None:
        link = self.config.links.get(link_name)
        if link is None:
            raise ProjectException(f"Could not find link '{link_name}' in project.")
        if link.source.parts[0] == "~":
            full_link_path = Path(self._home, Path(*link.source.parts[1:]))
        else:
            full_link_path = Path(self._home, link.source)
        if full_link_path.exists() or full_link_path.is_symlink():
            raise ProjectException(
                f"Cannot restore link. Already file at links source."
            )
        if not full_link_path.parent.exists():
            logger.info(f"Creating parent folders of link {link.source.as_posix()}")
            full_link_path.parent.mkdir(parents=True)

        logger.info(
            f"Creating symlink from {link.source.as_posix()} "
            f"to {Path(self.path, link_name).as_posix()}"
        )
        full_link_path.symlink_to(Path(self.path, link_name).resolve())

    def restore(self):
        for link_name in self.config.links:
            self.restore_link(link_name)

    def set_link(self, source_path: Path, target_name: str | None = None) -> None:
        if target_name is None:
            logger.debug(
                f"Setting target name to {source_path.name}, "
                f"inferred from source path {source_path.as_posix()}"
            )
            target_name = source_path.name
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
        self.config.links[target_name] = Link(source=Path("~", home_to_source_path))
        self.write()

    def status(self) -> dict[str, str]:
        link_status_dict: dict[str, str] = {}
        for target_name, link in self.config.links.items():
            if link.source.parts[0] == "~":
                full_path = Path(self._home, Path(*link.source.parts[1:]))
            else:
                full_path = Path(self._home, link.source)
            if not self.path.joinpath(target_name).exists():
                link_status = "Dotfile not in project folder."
            elif not full_path.is_symlink():
                print(full_path)
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

    def revert(self, link_name: str) -> None:
        """Move files to where the link is and revmove from config"""
        pass

    def refresh(self) -> None:
        self = self.__class__.from_path(self.path)
