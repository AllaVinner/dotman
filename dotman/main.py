from pprint import pprint
from pathlib import Path
import click
from typing import List, Dict, Literal, Self, Type, Self, get_args
import json
import os
from enum import Enum, auto, StrEnum
from pydantic import BaseModel, Field

import shutil


class ProjectStructure:
    DOTMANAGER_ROOT = Path(".dotman")
    PUBLIC_CONFIG = Path(DOTMANAGER_ROOT, "public_config.json")
    PRIVATE_CONFIG = Path(DOTMANAGER_ROOT, "private_config.json")
    GITIGNORE = Path(DOTMANAGER_ROOT, ".gitignore")


PrefixTypeLiteral = Literal["root", "home", "custom"]


class PrefixType(StrEnum):
    HOME = auto()
    ROOT = auto()
    CUSTOM = auto()

    @classmethod
    def names(cls) -> List[str]:
        return [e.name for e in cls]


class CustomPrefix(BaseModel):
    name: str
    path: Path
    description: str = Field(default="")


class PrivateConfigFile(BaseModel):
    prefixes: Dict[str, CustomPrefix]

    @classmethod
    def from_file(cls, path: Path) -> Self:
        with open(path, "r") as f:
            file_obj = json.load(f)
        return cls.model_validate(file_obj)

    def write(self, path: Path):
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))


class PublicCustomPrefix(BaseModel):
    name: str
    description: str = Field(default="")

    @classmethod
    def from_custom_prefix(cls, custom_prefix: CustomPrefix) -> Self:
        return cls(name=custom_prefix.name, description=custom_prefix.description)


class Link(BaseModel):
    link_path: Path
    target_name: str
    prefix_type: PrefixType
    prefix_config: None | CustomPrefix = Field(default=None)


class PublicLink(BaseModel):
    link_path: Path
    target_name: str
    prefix_type: PrefixType
    prefix_config: None | PublicCustomPrefix = Field(default=None)

    @classmethod
    def from_link(cls, link: Link) -> Self:
        public_prefix_config = (
            PublicCustomPrefix(
                name=link.prefix_config.name, description=link.prefix_config.description
            )
            if link.prefix_config
            else None
        )
        return cls(
            link_path=link.link_path,
            target_name=link.target_name,
            prefix_type=link.prefix_type,
            prefix_config=public_prefix_config,
        )

    def to_link(self, prefixes: dict[str, CustomPrefix]) -> Link:
        if self.prefix_config is None:
            prefix_config = None
        else:
            prefix_config = prefixes.get(self.prefix_config.name)
            if prefix_config is None:
                raise ValueError("Could not find prefix in available prefixes")
        return Link(
            link_path=self.link_path,
            target_name=self.target_name,
            prefix_type=self.prefix_type,
            prefix_config=prefix_config,
        )


class PublicConfigFile(BaseModel):
    links: Dict[str, PublicLink]

    @classmethod
    def from_file(cls, path: Path) -> Self:
        with open(path, "r") as f:
            file_obj = json.load(f)
        return cls.model_validate(file_obj)

    def write(self, path: Path):
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=4))


class ProjectConfig(BaseModel):
    links: Dict[str, Link] = Field(default_factory=lambda: {})
    prefixes: Dict[str, CustomPrefix] = Field(default_factory=lambda: {})

    def get_public_config(self) -> PublicConfigFile:
        links = {n: PublicLink.from_link(link) for n, link in self.links.items()}
        return PublicConfigFile(links=links)

    def get_private_config(self) -> PrivateConfigFile:
        return PrivateConfigFile(prefixes=self.prefixes)

    def write_public_config(self, path: Path):
        self.get_public_config().write(path)

    def write_private_config(self, path: Path):
        self.get_private_config().write(path)

    def write(self, project_path: Path) -> None:
        self.write_public_config(
            path=Path(project_path, ProjectStructure.PUBLIC_CONFIG)
        )
        self.write_private_config(
            path=Path(project_path, ProjectStructure.PRIVATE_CONFIG)
        )

    @classmethod
    def from_file_configs(
        cls, public_config: PublicConfigFile, private_config: PrivateConfigFile
    ) -> Self:
        links = {
            n: link.to_link(private_config.prefixes)
            for n, link in public_config.links.items()
        }
        return cls(links=links, prefixes=private_config.prefixes)

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        if not Path(project_path, ProjectStructure.DOTMANAGER_ROOT).exists():
            return cls()
        public_config = PublicConfigFile.from_file(
            Path(project_path, ProjectStructure.PUBLIC_CONFIG)
        )
        private_config = PrivateConfigFile.from_file(
            Path(project_path, ProjectStructure.PRIVATE_CONFIG)
        )
        return cls.from_file_configs(
            public_config=public_config, private_config=private_config
        )


GITIGNORE_CONTENT = ProjectStructure.PRIVATE_CONFIG.relative_to(
    ProjectStructure.DOTMANAGER_ROOT
).as_posix()


class DotProject(BaseModel):
    project_path: Path
    config: ProjectConfig = Field(default_factory=lambda: ProjectConfig())
    # TODO: Make home and root paths into true non-validate fields. Remove the type hinting
    home_path: Path = Field(default_factory=lambda: Path.home(), exclude=True)
    root_path: Path = Field(default_factory=lambda: Path("/"), exclude=True)

    def set_home_path(self, home_path: Path) -> None:
        if not home_path.is_relative_to(self.root_path):
            raise ValueError(
                "When setting home path, the home path must be relative to current root"
            )
        self.home_path = home_path

    def set_root_path(self, root_path: Path) -> None:
        if not self.home_path.is_relative_to(root_path):
            raise ValueError("When setting root path, the home path must be relative")
        self.root_path = root_path

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        project_config = ProjectConfig.from_path(project_path=project_path)
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
        project_path.mkdir(exist_ok=True, parents=True)
        Path(project_path, ProjectStructure.DOTMANAGER_ROOT).mkdir()
        project = cls(project_path=project_path)
        project._write_gitignore()
        project.config.write_public_config(
            Path(project.project_path, ProjectStructure.PUBLIC_CONFIG)
        )
        project.config.write_private_config(
            Path(project.project_path, ProjectStructure.PRIVATE_CONFIG)
        )
        return project

    @classmethod
    def ensure(cls, project_path: Path) -> Self:
        if Path(project_path, ProjectStructure.DOTMANAGER_ROOT).exists():
            return cls.from_path(project_path)
        else:
            return cls.init(project_path)

    def write(self):
        self.config.write_public_config(
            Path(self.project_path, ProjectStructure.PUBLIC_CONFIG)
        )
        self.config.write_private_config(
            Path(self.project_path, ProjectStructure.PRIVATE_CONFIG)
        )

    def add_link(
        self,
        source_path: Path,
        target_name: str | None = None,
        prefix_type: PrefixType | PrefixTypeLiteral | None = None,
        prefix_config: CustomPrefix | None = None,
    ):
        # Harmonize and Validate Input
        link_name = self._create_link_setup(
            source_path=source_path,
            target_name=target_name,
            prefix_type=prefix_type,
            prefix_config=prefix_config,
        )
        self._create_link_system_call(link_name)
        self.write()

    def _create_link_setup(
        self,
        source_path: Path,
        target_name: str | None = None,
        prefix_type: PrefixType | PrefixTypeLiteral | None = None,
        prefix_config: CustomPrefix | None = None,
    ):
        # Harmonize and Validate Input
        full_source_path = source_path.expanduser().resolve()
        prefix_type = PrefixType(prefix_type or PrefixType.HOME)
        if prefix_type != PrefixType.CUSTOM and prefix_config is not None:
            raise ValueError(
                "Only prefix type 'CUSTOM' may have a custom prefix config"
            )
        if target_name is None:
            target_name = source_path.name
        full_target_path = Path(self.project_path, target_name).resolve()
        if prefix_type == PrefixType.HOME:
            prefix = self.home_path
        elif prefix_type == PrefixType.ROOT:
            prefix = self.root_path
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
            raise ValueError(
                f"Source Path does not exist exists. Soure Path: {full_source_path}"
            )
        if not full_source_path.is_relative_to(prefix):
            raise ValueError(
                "Link prefix, if specified must be relative to source path."
            )

        # Create Config
        self.config.links[target_name] = Link(
            link_path=full_source_path.relative_to(prefix),
            target_name=target_name,
            prefix_type=prefix_type,
            prefix_config=prefix_config,
        )
        if prefix_config:
            self.config.prefixes[prefix_config.name] = prefix_config
        return target_name

    def _create_link_system_call(self, link_name: str):
        link = self.config.links[link_name]
        if link.prefix_type == PrefixType.HOME:
            prefix = self.home_path
        elif link.prefix_type == PrefixType.ROOT:
            prefix = self.root_path
        elif link.prefix_type == PrefixType.CUSTOM:
            if link.prefix_config is None:
                raise ValueError("Link has prefix type CUSTOM, but no prefix config")
            if prefix_config := self.config.prefixes.get(link.prefix_config.name):
                prefix = prefix_config.path
            else:
                print(link)
                print(link.prefix_config.name)
                print(list(self.config.prefixes.keys()))
                raise ValueError(
                    f"Could not find the prefix in link inside the given prefixes."
                )
        else:
            raise ValueError(
                f"Unreachable. Prefix type '{link.prefix_type}', did not match any conditions"
            )
        full_source_path = Path(prefix, link.link_path)
        full_target_path = Path(self.project_path, link.target_name)
        shutil.move(full_source_path, full_target_path)
        full_source_path.symlink_to(full_target_path)

    def status(self):
        for link_name, link_config in self.config.links.items():
            if link_config.prefix_type == "home":
                full_link_path = Path(Path.home(), link_config.link_path)
            else:
                raise ValueError("Not implemented")

            print("Link Name: ", link_name)
            print("    Link Path: ", link_config.link_path)
            print("    Prefix Type: ", link_config.prefix_type)
            print("    Link exists: ", Path(full_link_path).exists())
            print("    Link Target: ", Path(link_config.link_path).resolve().as_posix())
            print("    Target Name: ", link_config.target_name)


def clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir()


@click.group()
def dm():
    pass


@click.command("add")
@click.argument("source_path")
@click.argument("project_path", default=".")
@click.option("-n", "--name", "target_name", type=str, default=None)
@click.option("--prefix-type", type=str, default=None)
@click.option("--prefix", type=str, default=None)
@click.option("--prefix-name", type=str, default=None)
@click.option("--prefix-description", type=str, default=None)
def add_link(
    source_path: Path,
    project_path: Path,
    target_name: str | None,
    prefix_type: str | None,
    prefix: str | None,
    prefix_name: str | None,
    prefix_description: str | None,
):
    if prefix and prefix_description and prefix_name:
        prefix_config = CustomPrefix(
            name=prefix_name, path=Path(prefix), description=prefix_description
        )
    else:
        prefix_config = None
    if prefix_type is None:
        prefix_type_ = PrefixType.HOME
    else:
        prefix_type_ = PrefixType(prefix_type)

    dot_project = DotProject.ensure(Path(project_path))
    dot_project.add_link(
        source_path=Path(source_path),
        target_name=target_name,
        prefix_type=prefix_type_,
        prefix_config=prefix_config,
    )


@click.command("setup1")
@click.argument("path", default=".")
def setup1(path):
    root_path = Path(path)
    clean_dir(root_path)
    files_path = Path(root_path, "files")
    projects_path = Path(root_path, "projects")
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
    dm.add_link(source_path=file_a)
    dm.add_link(source_path=file_b)


@click.command("setup3")
@click.argument("path", default=".")
def setup3(path):
    root_path = Path(path)
    clean_dir(root_path)
    home_path = Path(root_path, "home")
    home_path.mkdir()
    projects_path = Path(home_path, "mydotfiles")
    projects_path.mkdir()
    Path(home_path, "a.config").touch()
    Path(home_path, "b.config").touch()


@click.command("status")
@click.option("-s", "--source", type=str, default=".")
def status(source):
    source_path = Path(source)
    dot_project = DotProject.ensure(Path(source_path))
    dot_project.status()


# @click.command("config")
# @click.option("-s", "--source", type=str, default=".")
# def config(source):
#     source_path = Path(source)
#     dot_project = DotProject.from_path(Path(source_path))
#     pprint(dot_project.config.to_dict())
#     pprint(dot_project.private_config.to_dict())


@click.command("hello")
def hello():
    print("hello")


dm.add_command(hello)
dm.add_command(add_link)
dm.add_command(status)
dm.add_command(setup1)
dm.add_command(setup2)
dm.add_command(setup3)
# dm.add_command(config)


def cli():
    dm()
