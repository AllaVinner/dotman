from pathlib import Path
from dotman.context import Context, managed_context, resolve_path


def test_resolve_path() -> None:
    context = Context(cwd=Path("/a/home/c"), home=Path("/a/home"), root=Path("/"))
    with managed_context(context):
        assert resolve_path(Path("d/e")) == Path("/a/home/c/d/e")
        assert resolve_path(Path("/a/d")) == Path("/a/d")
        assert resolve_path(Path("~/c/dd")) == Path("/a/home/c/dd")
        assert resolve_path(Path("./../../e/f")) == Path("/a/e/f")

    context = Context(cwd=Path("/a/b"), home=Path("/a/home"), root=Path("/"))
    with managed_context(context):
        assert resolve_path(Path("c")) == Path("/a/b/c")
        assert resolve_path(Path("~/c/dd")) == Path("/a/home/c/dd")
        assert resolve_path(Path("./../../e/f")) == Path("/e/f")
