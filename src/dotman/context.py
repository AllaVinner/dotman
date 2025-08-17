import os
from dataclasses import dataclass, field
from pathlib import Path
from contextvars import ContextVar
from typing import Iterator


@dataclass
class Context:
    cwd: Path = field(default_factory=lambda: Path.cwd())
    home: Path = field(default_factory=lambda: Path.home())
    root: Path = field(default_factory=lambda: Path("/"))


global_context: ContextVar[Context] = ContextVar("context")


def get_context() -> Context:
    try:
        return global_context.get()
    except LookupError:
        new_context = Context()
        global_context.set(new_context)
        return global_context.get()


def managed_context(context: Context | None) -> Iterator[Context]:
    token = None
    try:
        if context is None:
            context = Context()
        token = global_context.set(context)
        yield get_context()
    finally:
        if token is not None:
            global_context.reset(token)


def resolve_path(path: Path, context: Context) -> Path:
    norm_path = Path(os.path.normpath(path))
    if path.is_absolute():
        return norm_path
    parts = path.parts
    if len(parts) == 0:
        return context.cwd
    if parts[0] == "~":
        return Path(context.home, *parts[1:])
    return Path(context.cwd, path) 
    