from pathlib import Path
from typing import Literal, Self, Union
import json
from pydantic import BaseModel, Field, ValidationError


class Prefix(BaseModel):
    name: str
    prefix: Path
    description: str = Field(..., default="")


class PrivateConfig(BaseModel):
    prefixes: dict[str, Prefix]


class HomePrefixConfig(BaseModel):
    prefix_type: Literal["home"]


class RootPrefixConfig(BaseModel):
    prefix_type: Literal["root"]


class CustomPrefixConfig(BaseModel):
    prefix_type: Literal["custom"]
    name: str
    description: str


PrefixConfigTypes = Union[HomePrefixConfig, RootPrefixConfig, CustomPrefixConfig]


class Link(BaseModel):
    source_path: Path
    prefix_config: PrefixConfigTypes = Field(..., descriminator="prefix_type")


class PublicConfig(BaseModel):
    links: dict[str, Link]


class Project:
    path: Path
    public_config: PublicConfig
    private_config: PrivateConfig


class ProjectStructure:

    @classmethod
    def dotman(cls, project_path: Path | None = None) -> Path:
        suffix = Path(".dotman")
        if project_path is None:
            return suffix
        else:
            return Path(project_path, suffix)

    @classmethod
    def public_config(cls, project_path: Path | None = None) -> Path:
        return Path(cls.dotman(project_path), Path("public_config.json"))

    @classmethod
    def private_config(cls, project_path: Path | None = None) -> Path:
        return Path(cls.dotman(project_path), Path("private_config.json"))

    @classmethod
    def gitignore(cls, project_path: Path | None = None) -> Path:
        return Path(cls.dotman(project_path), Path(".gitignore"))
