from dataclasses import dataclass, field
from pathlib import Path
from contextvars import ContextVar
from typing import Iterator
from contextlib import contextmanager


@dataclass
class Context:
    cwd: Path = field(default_factory=lambda: Path.cwd())
    home: Path = field(default_factory=lambda: Path.home())


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
