from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from contextvars import ContextVar
import sys
from typing import Iterator, Literal
from contextlib import contextmanager

from dotman.exceptions import DotmanException


class Platform(Enum):
    windows = "windows"
    mac = "mac"
    linux = "linux"

    @classmethod
    def from_system(cls) -> Platform:
        sys_platform = sys.platform
        platform_map = {
            "windows": Platform.windows,
            "linux": Platform.linux,
            "darwin": Platform.mac,
        }
        enum_platform = platform_map.get(sys_platform)
        if enum_platform is None:
            raise DotmanException(f"System platform {sys_platform} is not supported.")
        return enum_platform
        

PlatformLiteral = Literal["windows", "mac", "linux"]


@dataclass
class Context:
    cwd: Path = field(default_factory=Path.cwd)
    home: Path = field(default_factory=Path.home)
    platform: Platform = field(default_factory=Platform.from_system)


global_context: ContextVar[Context] = ContextVar("context")


def get_context() -> Context:
    try:
        return global_context.get()
    except LookupError:
        new_context = Context()
        global_context.set(new_context)
        return global_context.get()


@contextmanager
def managed_context(context: Context | None = None) -> Iterator[Context]:
    token = None
    try:
        if context is None:
            context = Context()
        token = global_context.set(context)
        yield get_context()
    finally:
        if token is not None:
            global_context.reset(token)