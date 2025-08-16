from dataclasses import dataclass, field
from pathlib import Path
from contextvars import ContextVar


@dataclass
class Context:
    cwd: Path = field(default_factory=lambda: Path.cwd())
    home: Path = field(default_factory=lambda: Path.home())
    root: Path = field(default_factory=lambda: Path("/"))


context = ContextVar("context")


def get_context():
    try:
        return context.get()
    except LookupError:
        new_context = Context()
        context.set(new_context)
        return new_context
