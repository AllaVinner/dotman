from os.path import exists
from pathlib import Path
import click
from typing import List, Dict, Literal, Self, Type, Self
import json
import os
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
import shutil


class ProjectStructure:
    DOTMANAGER_ROOT = Path(".dotmanager")
    CONFIG = Path(DOTMANAGER_ROOT, "config.json")
    PRIVATE_CONFIG = Path(DOTMANAGER_ROOT, "config.private.json")
    GITIGNORE = Path(DOTMANAGER_ROOT, ".gitignore")


PrefixTypeLiteral = Literal["ROOT", "HOME", "CUSTOM"]


class PrefixType(Enum):
    HOME = auto()
    ROOT = auto()
    CUSTOM = auto()

    @classmethod
    def parse(cls, prefix_type: PrefixTypeLiteral | Self) -> Self:
        if isinstance(prefix_type, PrefixType):
            prefix_type = prefix_type.name
        return cls.__getitem__(prefix_type)


class ProjectConfig:
    def __init__(self, config=None):
        self.links = config.get("links", {}) if config else {}
        self.prefixes = config.get("prefixes", {}) if config else {}

    def to_dict(self) -> Dict:
        # TODO: Remove None values from writing
        return dict(links=self.links, prefixes=self.prefixes)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def write(self, path: Path):
        with open(path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        return cls(json_str)

    @classmethod
    def from_path(cls, file_path: Path) -> Self:
        with open(file_path, "r") as f:
            return cls.from_json(json.load(f))


GITIGNORE_CONTENT = ProjectStructure.PRIVATE_CONFIG.relative_to(
    ProjectStructure.DOTMANAGER_ROOT
).as_posix()


class DotProject:

    def __init__(
        self,
        project_path: Path,
        config: ProjectConfig | None = None,
        private_config: ProjectConfig | None = None,
    ):
        self.project_path = project_path
        self.config = config if config else ProjectConfig({})
        self.private_config = private_config if private_config else ProjectConfig({})
        self._home_path = Path.home()
        self._root_path = Path("/")

    def _set_home_path(self, home_path: Path) -> None:
        if not home_path.is_relative_to(self._root_path):
            raise ValueError(
                "When setting home path, the home path must be relative to current root"
            )
        self._home_path = home_path

    def _set_root_path(self, root_path: Path) -> None:
        if not self._home_path.is_relative_to(root_path):
            raise ValueError("When setting root path, the home path must be relative")
        self._root_path = root_path

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        if not Path(project_path, ProjectStructure.DOTMANAGER_ROOT).exists():
            return cls(project_path)
        config_path = Path(project_path, ProjectStructure.CONFIG)
        if config_path.exists():
            config = ProjectConfig.from_path(config_path)
        else:
            config = ProjectConfig()
        private_config_path = Path(project_path, ProjectStructure.CONFIG)
        if private_config_path.exists():
            private_config = ProjectConfig.from_path(private_config_path)
        else:
            private_config = ProjectConfig()
        return cls(project_path, config, private_config)

    def _write_gitignore(self):
        gitignore_path = Path(self.project_path, ProjectStructure.GITIGNORE)
        mode = "w"
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()
            if not GITIGNORE_CONTENT in gitignore_content:
                mode = "a"
        with open(gitignore_path, mode) as f:
            f.write("\n" + GITIGNORE_CONTENT)

    @classmethod
    def init(cls, project_path: Path) -> Self:
        project_path.mkdir(exist_ok=True)
        Path(project_path, ProjectStructure.DOTMANAGER_ROOT).mkdir()
        dot_manager = cls(project_path)
        dot_manager._write_gitignore()
        dot_manager.config.write(
            Path(dot_manager.project_path, ProjectStructure.CONFIG)
        )
        dot_manager.private_config.write(
            Path(dot_manager.project_path, ProjectStructure.PRIVATE_CONFIG)
        )
        return dot_manager

    @classmethod
    def ensure(cls, project_path: Path) -> Self:
        if Path(project_path, ProjectStructure.DOTMANAGER_ROOT).exists():
            return cls.from_path(project_path)
        else:
            return cls.init(project_path)

    def update(self):
        self.config.write(Path(self.project_path, ProjectStructure.CONFIG))
        self.private_config.write(
            Path(self.project_path, ProjectStructure.PRIVATE_CONFIG)
        )

    def create_link(
        self,
        source_path: Path,
        target_name: str | None = None,
        prefix_type: PrefixType | PrefixTypeLiteral | None = None,
        prefix: Path | None = None,
        prefix_name: str | None = None,
        prefix_config_type: str | None = None,
        prefix_description: str | None = None,
    ):
        # Harmonize and Validate Input
        full_source_path = source_path.expanduser().resolve()
        prefix_type = PrefixType.parse(prefix_type or PrefixType.HOME)
        prefix_config_type = prefix_config_type or "PRIVATE"
        if target_name is None:
            target_name = source_path.name
        full_target_path = Path(self.project_path, target_name).resolve()
        if prefix is None:
            if prefix_type == PrefixType.HOME:
                prefix = self._home_path
            elif prefix_type == PrefixType.ROOT:
                prefix = self._root_path
            elif prefix_type == PrefixType.CUSTOM:
                if prefix_name is None:
                    raise ValueError(
                        "Prefix name must be given for prefix type CUSTOM."
                    )
                elif prefix_name in self.config.prefixes:
                    prefix = Path(self.config.prefixes[prefix_name])
                elif prefix_name in self.private_config.prefixes:
                    prefix = Path(self.private_config.prefixes[prefix_name])
                else:
                    raise ValueError(
                        "If a prefix name is given but no prefix, then the prefix must exist in config or config.private."
                    )
            else:
                raise ValueError("Unreachable")
        else:
            if prefix_name is None:
                raise ValueError("If prefix is given, you must also set a prefix name")
            else:
                if prefix_name in self.config.prefixes:
                    if prefix_name != self.config.prefixes[prefix_name]:
                        raise ValueError(
                            "If prefix and prefix_name is exist in config prefix, then they have to be equal."
                        )
                if prefix_name in self.private_config.prefixes:
                    if prefix_name != self.private_config.prefixes[prefix_name]:
                        raise ValueError(
                            "If prefix and prefix_name is exist in private config prefix, then they have to be equal."
                        )
            prefix = prefix.resolve()
        prefix_config_type = prefix_config_type or "PRIVATE"
        if target_name in self.config.links:
            raise ValueError(
                "Target already exists in project_config, but not in sources..."
            )

        # Validate Paths
        if full_target_path.exists():
            raise ValueError("Target already exists")
        if not full_source_path.exists():
            raise ValueError("Source Path does not exist exists")
        if not full_source_path.is_relative_to(prefix):
            raise ValueError(
                "Link prefix, if specified must be relative to source path."
            )

        # Create Config
        link_config = dict(
            link_path=full_source_path.relative_to(prefix).as_posix(),
            target_name=target_name,
            prefix_type=prefix_type.name,
            prefix_name=prefix_name,
            prefix_description=prefix_description,
        )
        self.config.links[target_name] = link_config

        if prefix_name:
            prefix_config = dict(
                prefix_name=prefix_name,
                prefix=prefix.as_posix(),
            )
            if prefix_config_type == "PRIVATE":
                self.private_config.prefixes[prefix_name] = prefix_config
            else:
                self.config.prefixes[prefix_name] = prefix_config

        # Execute Actions
        shutil.move(full_source_path, full_target_path)
        full_source_path.symlink_to(full_target_path)
        self.config.write(Path(self.project_path, ProjectStructure.CONFIG))
        self.private_config.write(
            Path(self.project_path, ProjectStructure.PRIVATE_CONFIG)
        )

    def get_full_config(self) -> ProjectConfig:
        return ProjectConfig(self.config.to_dict() | self.private_config.to_dict())

    def status(self):
        config = self.get_full_config()
        for link_name, link_config in config.links.items():
            if link_config["prefix_type"] == "HOME":
                full_link_path = Path(Path.home(), link_config["link_path"])
            else:
                raise ValueError("Not implemented")
            print("Link Name: ", link_name)
            print("    Link Path: ", link_config["link_path"])
            print("    Prefix Type: ", link_config["prefix_type"])
            print("    Link exists: ", Path(full_link_path).exists())
            print(
                "    Link Target: ", Path(link_config["link_path"]).resolve().as_posix()
            )
            print("    Target Name: ", link_config["target_name"])


@click.group()
def dm():
    pass


@click.command("create-link")
@click.option("-s", "--source", type=str, required=True)
@click.option("-t", "--target", type=str, required=True)
@click.option("-n", "--name", "target_name", type=str, default=None)
@click.option("--prefix-type", type=str, default=None)
@click.option("--prefix", type=str, default=None)
@click.option("--prefix-name", type=str, default=None)
@click.option("--prefix-config-type", type=str, default=None)
@click.option("--prefix-description", type=str, default=None)
def create_link(
    source: Path,
    target: Path,
    target_name: str | None,
    prefix_type: str | None,
    prefix: str | None,
    prefix_name: str | None,
    prefix_config_type: str | None,
    prefix_description: str | None,
):
    dot_project = DotProject.ensure(Path(target))
    dot_project.create_link(
        Path(source),
        target_name=target_name,
        prefix_type=prefix_type,
        prefix=Path(prefix) if prefix else None,
        prefix_name=prefix_name,
        prefix_config_type=prefix_config_type,
        prefix_description=prefix_description,
    )


@click.command("setup1")
def setup1():
    files_path = Path("./files")
    projects_path = Path("./projects")
    if files_path.exists():
        shutil.rmtree(files_path)
    if projects_path.exists():
        shutil.rmtree(Path("./projects"))
    files_path.mkdir()
    projects_path.mkdir()
    Path(files_path, "a").touch()
    Path(files_path, "b").touch()


@click.command("status")
@click.option("-s", "--source", type=str, default=".")
def status(source):
    source_path = Path(source)
    dot_project = DotProject.ensure(Path(source_path))
    dot_project.status()


@click.command("hello")
def hello():
    print("hello")


dm.add_command(hello)
dm.add_command(create_link)
dm.add_command(setup1)
dm.add_command(status)


def cli():
    dm()
