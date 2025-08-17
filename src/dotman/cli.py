from pathlib import Path
import click
from dotman.add import add
from dotman.init import init


@click.command("init")
@click.argument("project", type=click.Path(path_type=Path), required=False)
def init_project(project: Path | None) -> None:
    if project is None:
        project = Path(".")
    init(project=project)


@click.command("add")
@click.argument("dotfile", type=click.Path(path_type=Path), required=True)
@click.option(
    "-p",
    "--project",
    "project",
    type=click.Path(path_type=Path),
    default=Path("."),
)
@click.option(
    "-t",
    "--target",
    "target",
    type=click.Path(path_type=Path),
    default=Path("."),
)
def add_dotfile(dotfile: Path, project: Path, target: Path | None) -> None:
    if target is None:
        target = Path(dotfile.name)
    add(project=project, dotfile=dotfile, target=target)


@click.group()
def cli():
    pass


cli.add_command(init_project)
cli.add_command(add_dotfile)


def main() -> None:
    cli()
