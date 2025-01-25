import os
import sys
import shutil
import click
from pathlib import Path
from dotman.main import Project, ProjectException
import functools


def dotman_cli_cmd(func):
    """Wrapps function in try/except to display errors nicely to users."""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ProjectException as e:
            click.echo(e)
            sys.exit(1)

    return wrapper_timer


@click.command("init", short_help="Init a dotman project")
@click.argument("project-path", type=click.Path(path_type=Path), default=Path("."))
@dotman_cli_cmd
def init_project(project_path: Path):
    """Init a dotman project in PROJECT_PATH

    Either in an empty directory. Then add links using `add`.
    Or initiate in an existing dotfile folder.
    Then define the exising dotfile links using `set`.

    The init command simply creates a config file in the project path.
    """
    Project.init(project_path=project_path)


@click.command("add", short_help="Add a dotfile to a dotman project")
@click.argument("link-source", type=click.Path(path_type=Path))
@click.argument("project-path", type=click.Path(path_type=Path), default=Path("."))
@click.option(
    "-n",
    "--target-name",
    type=str,
    default=None,
    help="Name of link and the dotfile after moving. Defaults to the name of the link source file.",
)
@dotman_cli_cmd
def add_link(
    link_source: Path,
    project_path: Path,
    target_name: str | None,
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
    try:
        project = Project.from_path(project_path=project_path)
    except ProjectException as e:
        click.echo(e)
        sys.exit(1)
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
    try:
        project = Project.from_path(project_path=target_path.parent)
    except ProjectException as e:
        click.echo(e)
        sys.exit(1)
    project.set_link(source_path, target_path.name)


@click.command("status", short_help="Updates dotman project with exising dotfiles.")
@click.argument("source-path", type=click.Path(path_type=Path), default=Path("."))
def status(source_path: Path):
    """Updates dotman project with link from SOURCE_PATH to existing dotfile in TARGET_PATH"""
    try:
        project = Project.from_path(project_path=source_path)
    except ProjectException as e:
        click.echo(e)
        sys.exit(1)
    status = project.status()
    for p, s in status.items():
        click.echo(f"{p}: {s}")


@click.group()
def setup():
    """Playground tests"""
    pass


@click.command("new-config", short_help="You have a new config you want to track.")
@click.argument("home-folder", type=click.Path(path_type=Path))
def setup_new_config(home_folder: Path):
    if home_folder.exists() and len(os.listdir(home_folder)) > 0:
        raise FileExistsError("Home folder exist and is not empty")
    home_folder.mkdir(parents=True, exist_ok=True)
    projects_folder = Path(home_folder, "projects")
    new_config_folder = Path(home_folder, "configs")
    new_config_file = Path(new_config_folder, "config.toml")
    projects_folder.mkdir()
    new_config_folder.mkdir()
    new_config_file.touch()


@click.command(
    "new-machine", short_help="You have a new machine, and newly dowloaded dot files."
)
@click.argument("home-folder", type=click.Path(path_type=Path))
def setup_new_machine(home_folder: Path):
    if home_folder.exists() and len(os.listdir(home_folder)) > 0:
        raise FileExistsError("Home folder exist and is not empty")
    home_folder.mkdir(parents=True, exist_ok=True)
    docs_folder = Path(home_folder, "docs")
    config_folder = Path(home_folder, "configs")
    git_file = Path(config_folder, "gitconfig.toml")
    bash_file = Path(config_folder, "bashrc")
    nvim_folder = Path(config_folder, "nvim")
    nvim_file = Path(nvim_folder, "init.nvim")
    docs_folder.mkdir()
    config_folder.mkdir()
    git_file.touch()
    bash_file.touch()
    nvim_folder.mkdir()
    nvim_file.touch()

    project = Project.init(Path(docs_folder, "my-dotfiles"))
    project.add_link(git_file)
    project.add_link(bash_file)
    project.add_link(nvim_folder)
    shutil.rmtree(config_folder)


setup.add_command(setup_new_config)
setup.add_command(setup_new_machine)


@click.group()
def cli():
    """Dotman: a very simple dotfile manager

    Add an exising dotfile to a repo - see `add`

    Restore the neccesary links on a new machine - see `restore`
    """
    pass


cli.add_command(init_project)
cli.add_command(add_link)
cli.add_command(restore)
cli.add_command(status)
cli.add_command(set_link)
cli.add_command(setup)
