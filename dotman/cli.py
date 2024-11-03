from os import link
import shutil
import click
from pathlib import Path
from dotman.main import Project


@click.group()
def cli():
    """Dotman: a very simple dotfile manager

    Add an exising dotfile to a repo - see `add`

    Restore the neccesary links on a new machine - see `restore`
    """
    pass


@click.command("hello")
def hello():
    print("hello")


@click.command("init", short_help="Init a dotman project")
@click.argument("project-path", type=click.Path(path_type=Path), default=Path("."))
def init_project(project_path: Path):
    """Init a dotman project in PROJECT_PATH

    Either in an  empty directory. Then add links using `add`.

    Or initiate in an existing dotfile folder.
    Then define the exising dotfile links using `set`.
    """
    Project.init(project_path=project_path)


@click.command("add", short_help="Add a dotfile to a dotman project")
@click.argument("link-source", type=click.Path(path_type=Path))
@click.argument("project-path", type=click.Path(path_type=Path), default=Path("."))
@click.option(
    "-n",
    "--targe-name",
    type=str,
    default=None,
    help="Name of link and the dotfile after moving. Defaults to the source name.",
)
def add_link(
    link_source: Path, project_path: Path, target_name: str, force_overwrite: bool
):
    """Add a dotfile in LINK_SOURCE to project in PROJECT_PATH"""
    project = Project.from_path(project_path=project_path)
    project.add_link(source=link_source, target_name=target_name)


@click.command("restore", short_help="Restore links from a dotman project")
@click.argument("project-path", type=click.Path(path_type=Path), default=Path("."))
@click.option(
    "-n",
    "--target-name",
    multiple=True,
    help="Name of link and the dotfile. If left out, all links will be restored.",
)
def restore(project_path, target_name):
    """Restore links in PROJECT_PATH"""
    project = Project.from_path(project_path=project_path)
    if len(target_name) == 0:
        target_name = list(project.config.links)
    for link_name in target_name:
        project.restore_link(link_name)


@click.command("set", short_help="Updates dotman project with exising dotfiles.")
@click.argument("source-path", type=click.Path(path_type=Path))
@click.argument("target-path", type=click.Path(path_type=Path))
@click.option("-f", "--force-overwrite", type=bool, is_flag=True, default=False)
def set_link(source_path: Path, target_path: Path, force_overwrite):
    """Updates dotman project with link from SOURCE_PATH to existing dotfile in TARGET_PATH"""
    if force_overwrite:
        if source_path.is_symlink():
            source_path.unlink()
        elif source_path.exists():
            shutil.rmtree(source_path)
    project = Project.from_path(project_path=target_path.parent)
    project.set_link(source_path, target_path.name)


cli.add_command(init_project)
cli.add_command(add_link)
cli.add_command(restore)
cli.add_command(set_link)
