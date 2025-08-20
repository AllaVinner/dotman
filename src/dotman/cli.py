from pathlib import Path
from typing import get_args
import click
from dotman.add import add
from dotman.examples import Stage, setup_folder_structure
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
    default=None,
)
def add_dotfile(dotfile: Path, project: Path, target: Path | None) -> None:
    if target is None:
        target = Path(dotfile.name)
    add(project=project, dotfile=dotfile, target=target)


@click.command("example")
@click.argument("stage", type=click.Choice(get_args(Stage)), required=True)
@click.argument("folder", type=click.Path(path_type=Path), required=False)
def example_setup(stage: Stage, folder: Path | None) -> None:
    if folder is None:
        folder = Path(".")
    setup_folder_structure(root_folder=folder, stop_after=stage)


@click.group()
def cli():
    pass


cli.add_command(init_project)
cli.add_command(add_dotfile)
cli.add_command(example_setup)


def main() -> None:
    cli()
