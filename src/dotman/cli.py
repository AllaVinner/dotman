from pathlib import Path
import sys
from typing import get_args
import click
from dotman.status import status
from dotman.context import DotfileMode, Platform
from dotman.edit import edit
from dotman.exceptions import DotmanException
from dotman.setup import setup, setup_project
from dotman.add import add
from dotman.examples import Stage, setup_folder_structure
from dotman.init import init
from dotman.sync import sync, sync_project


def cli_error_handler(f):
    def inner(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except DotmanException as e:
            click.echo(e.message)
            sys.exit(1)

    return inner


@click.command("init")
@click.argument("project", type=click.Path(path_type=Path), required=False)
@cli_error_handler
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
@click.option(
    "--mode",
    "dotfile_mode",
    type=click.Choice(get_args(DotfileMode)),
    default="symlink",
)
@cli_error_handler
def add_dotfile(
    dotfile: Path, project: Path, target: Path | None, dotfile_mode: DotfileMode
) -> None:
    if target is None:
        target = Path(dotfile.name)
    add(project=project, dotfile=dotfile, target=target, dotfile_mode=dotfile_mode)


@click.command("setup")
@click.argument("target", type=click.Path(path_type=Path), required=False)
@click.option(
    "-p",
    "--project",
    "project",
    type=click.Path(path_type=Path),
    default=Path("."),
)
@click.option(
    "--mode",
    "dotfile_mode",
    type=click.Choice(get_args(DotfileMode)),
    default="symlink",
)
@cli_error_handler
def setup_target(project: Path, target: Path | None, dotfile_mode: DotfileMode) -> None:
    if target is None:
        setup_project(project=project, dotfile_mode=dotfile_mode)
    else:
        setup(project=project, target=target, dotfile_mode=dotfile_mode)


@click.command("edit")
@click.argument("target", type=click.Path(path_type=Path), required=True)
@click.argument("dotfile", type=click.Path(path_type=Path), required=True)
@click.option(
    "-p",
    "--project",
    "project",
    type=click.Path(path_type=Path),
    default=Path("."),
)
@click.option(
    "--platform",
    "platform",
    type=click.Choice(Platform),
    default=None,
)
@cli_error_handler
def edit_target(
    project: Path, target: Path, dotfile: Path, platform: Platform | None
) -> None:
    edit(project=project, target=target, dotfile=dotfile, platform=platform)


@click.command("example")
@click.argument("stage", type=click.Choice(get_args(Stage)), required=True)
@click.argument("folder", type=click.Path(path_type=Path), required=False)
@cli_error_handler
def example_setup(stage: Stage, folder: Path | None) -> None:
    if folder is None:
        folder = Path(".")
    setup_folder_structure(root_folder=folder, stage=stage)


@click.command("status")
@click.argument("project", type=click.Path(path_type=Path), required=False)
@cli_error_handler
def project_status(project: Path | None) -> None:
    if project is None:
        project = Path(".")
    stat = status(project=project)
    link_msgs = [f"{link.target.as_posix()}: {link.status}" for link in stat.links]
    link_msg = "\n  ".join(link_msgs)
    msg = f"""\
Project {stat.project.name}
  {link_msg}
"""
    click.echo(msg)


@click.command("sync")
@click.argument("target", type=click.Path(path_type=Path), required=False)
@click.option(
    "-p",
    "--project",
    "project",
    type=click.Path(path_type=Path),
    default=Path("."),
)
@cli_error_handler
def sync_target(project: Path, target: Path | None) -> None:
    if target is None:
        sync_project(project=project)
    else:
        sync(project=project, target=target)


@click.group()
def cli():
    pass


cli.add_command(init_project)
cli.add_command(add_dotfile)
cli.add_command(setup_target)
cli.add_command(edit_target)
cli.add_command(project_status)
cli.add_command(example_setup)


def main() -> None:
    cli()
