from os.path import exists
from pprint import pprint
from pathlib import Path
import click
from typing import List, Dict, Literal, Self, Type, Self, get_args
import json
import os
from dataclasses import dataclass
from enum import Enum, auto
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

import shutil


class ProjectStructure:
    DOTMANAGER_ROOT = Path(".dotmanager")
    LINK_CONFIG = Path(DOTMANAGER_ROOT, "link_config.json")
    PREFIX_CONFIG = Path(DOTMANAGER_ROOT, "prefix_config.json")
    GITIGNORE = Path(DOTMANAGER_ROOT, ".gitignore")


PrefixTypeLiteral = Literal["ROOT", "HOME", "CUSTOM"]
PrefixTypeLiteral.__class__


class PrefixType(Enum):
    HOME = auto()
    ROOT = auto()
    CUSTOM = auto()

    @classmethod
    def names(cls) -> List[str]:
        return [e.name for e in cls]

    @classmethod
    def parse(cls, prefix_type: Self | PrefixTypeLiteral | str) -> Self:
        if isinstance(prefix_type, cls):
            return cls.__getitem__(prefix_type.name)
        elif isinstance(prefix_type, PrefixTypeLiteral):
            return cls.__getitem__(prefix_type)
        elif isinstance(prefix_type, str):
            matches = [name for name in cls.names() if name == prefix_type]
            if len(matches) == 0:
                s = '", "'
                raise ValueError(
                    f"Could not parse value '{prefix_type}' to a PrefixType. "
                    f'Allowed values are ["{s.join(cls.names())}"].'
                )
            elif len(matches) == 1:
                return cls.__getitem__(matches[0])
            else:
                raise ValueError(
                    "Unreachable code. Found more than one matched PrefixType."
                )
        else:
            raise ValueError(
                f"Could not parse value '{prefix_type}' to a PrefixType. "
                f"Is of type '{type(prefix_type)}'."
            )


class CustomPrefixConfig(BaseModel):
    name: str
    description: str = Field(default="")


class LinkConfig(BaseModel):
    link_path: Path
    target_name: str
    prefix_type: PrefixTypeLiteral
    prefix_config: None | CustomPrefixConfig = Field(default=None)


class LinkConfigFile(BaseModel):
    links: Dict[str, LinkConfig]

    @classmethod
    def from_file(cls, path: Path) -> Self:
        with open(path, "r") as f:
            file_obj = json.load(f)
        return cls.model_validate(file_obj)


class PrefixConfig(BaseModel):
    name: str
    path: Path
    description: str = Field(default="")


class PrefixConfigFile(BaseModel):
    prefixes: Dict[str, PrefixConfig]

    @classmethod
    def from_file(cls, path: Path) -> Self:
        with open(path, "r") as f:
            file_obj = json.load(f)
        return cls.model_validate(file_obj)


class ProjectConfig(BaseModel):
    links: Dict[str, LinkConfig] = Field(default_factory=lambda: {})
    prefixes: Dict[str, PrefixConfig] = Field(default_factory=lambda: {})

    def write_links(self, path: Path):
        links = dict(links={n: v.model_dump() for n, v in self.links.items()})
        with open(path, "w") as f:
            json.dump(links, f)

    def write_prefixes(self, path: Path):
        prefixes = dict(links={n: v.model_dump() for n, v in self.prefixes.items()})
        with open(path, "w") as f:
            json.dump(prefixes, f)


GITIGNORE_CONTENT = ProjectStructure.PREFIX_CONFIG.relative_to(
    ProjectStructure.DOTMANAGER_ROOT
).as_posix()


class DotProject(BaseModel):
    project_path: Path
    config: ProjectConfig = Field(default_factory=lambda: ProjectConfig())
    _home_path: Path = Field(default_factory=lambda: Path.home(), exclude=True)
    _root_path: Path = Field(default_factory=lambda: Path("/"), exclude=True)

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
            return cls(project_path=project_path)
        link_config = LinkConfigFile.from_file(
            Path(project_path, ProjectStructure.LINK_CONFIG)
        )
        prefix_config = PrefixConfigFile.from_file(
            Path(project_path, ProjectStructure.PREFIX_CONFIG)
        )
        project_config = ProjectConfig(
            links=link_config.links, prefixes=prefix_config.prefixes
        )
        return cls(project_path=project_path, config=project_config)

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
        dot_manager = cls(project_path=project_path)
        dot_manager._write_gitignore()
        dot_manager.config.write_links(
            Path(dot_manager.project_path, ProjectStructure.LINK_CONFIG)
        )
        dot_manager.config.write_prefixes(
            Path(dot_manager.project_path, ProjectStructure.PREFIX_CONFIG)
        )
        return dot_manager

    @classmethod
    def ensure(cls, project_path: Path) -> Self:
        if Path(project_path, ProjectStructure.DOTMANAGER_ROOT).exists():
            return cls.from_path(project_path)
        else:
            return cls.init(project_path)

    def update(self):
        self.config.write_links(Path(self.project_path, ProjectStructure.LINK_CONFIG))
        self.config.write_prefixes(
            Path(self.project_path, ProjectStructure.PREFIX_CONFIG)
        )

    def create_link(
        self,
        source_path: Path,
        target_name: str | None = None,
        prefix_type: PrefixType | PrefixTypeLiteral | None = None,
        prefix_config: PrefixConfig | None = None,
    ):
        # Harmonize and Validate Input
        full_source_path = source_path.expanduser().resolve()
        prefix_type = PrefixType.parse(prefix_type or PrefixType.HOME)
        if prefix_type != PrefixType.CUSTOM and prefix_config is not None:
            raise ValueError("Only prefix type 'CUSTOM' has a custom prefix config")
        if target_name is None:
            target_name = source_path.name
        full_target_path = Path(self.project_path, target_name).resolve()
        if prefix_type == PrefixType.HOME:
            prefix = self._home_path
        elif prefix_type == PrefixType.ROOT:
            prefix = self._root_path
        elif prefix_type == PrefixType.CUSTOM:
            if prefix_config is None:
                raise ValueError(
                    "if prefix type custom was used, then a prefix config must be given"
                )
            prefix = prefix_config.path
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
            prefix_config=prefix_config,
        )
        self.config.links[target_name] = LinkConfig.model_validate(link_config)

        # Execute Actions
        shutil.move(full_source_path, full_target_path)
        full_source_path.symlink_to(full_target_path)
        self.config.write_links(Path(self.project_path, ProjectStructure.LINK_CONFIG))
        self.config.write_prefixes(
            Path(self.project_path, ProjectStructure.PREFIX_CONFIG)
        )

    def status(self):
        for link_name, link_config in self.config.links.items():
            if link_config.prefix_type == "HOME":
                full_link_path = Path(Path.home(), link_config.link_path)
            else:
                raise ValueError("Not implemented")

            print("Link Name: ", link_name)
            print("    Link Path: ", link_config.link_path)
            print("    Prefix Type: ", link_config.prefix_type)
            print("    Link exists: ", Path(full_link_path).exists())
            print("    Link Target: ", Path(link_config.link_path).resolve().as_posix())
            print("    Target Name: ", link_config.target_name)


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
    prefix_description: str | None,
):
    if prefix and prefix_description and prefix_name:
        prefix_config = PrefixConfig(
            name=prefix_name, path=Path(prefix), description=prefix_description
        )
    else:
        prefix_config = None

    dot_project = DotProject.ensure(Path(target))
    dot_project.create_link(
        source_path=Path(source),
        target_name=target_name,
        prefix_type=PrefixType.parse(prefix_type),
        prefix_config=prefix_config,
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


@click.command("setup2")
@click.option("-r", "--root", type=str, default=".")
def setup2(root: str):
    root_path = Path(root)
    root_path.mkdir(exist_ok=True)
    files_path = Path(root_path, "files")
    projects_path = Path(root_path, "projects")
    if files_path.exists():
        shutil.rmtree(files_path)
    if projects_path.exists():
        shutil.rmtree(Path("./projects"))
    files_path.mkdir()
    projects_path.mkdir()
    file_a = Path(files_path, "a")
    file_a.touch()
    file_b = Path(files_path, "b")
    file_b.touch()
    dm = DotProject.ensure(Path(projects_path, "pm1"))
    dm.create_link(source_path=file_a)
    dm.create_link(source_path=file_b)


@click.command("status")
@click.option("-s", "--source", type=str, default=".")
def status(source):
    source_path = Path(source)
    dot_project = DotProject.ensure(Path(source_path))
    dot_project.status()


@click.command("config")
@click.option("-s", "--source", type=str, default=".")
def config(source):
    source_path = Path(source)
    dot_project = DotProject.from_path(Path(source_path))
    pprint(dot_project.config.to_dict())
    pprint(dot_project.private_config.to_dict())


@click.command("hello")
def hello():
    print("hello")


dm.add_command(hello)
dm.add_command(create_link)
dm.add_command(status)
dm.add_command(setup1)
dm.add_command(setup2)
dm.add_command(config)


def cli():
    dm()
