from os import link
import shutil
import click
from pathlib import Path
from dotman.main import Project


@click.group()
def cli():
    pass


@click.command("hello")
def hello():
    print("hello")


@click.command("init")
@click.argument("path", type=click.Path(path_type=Path), default=Path("."))
def init_project(path):
    Project.init(project_path=path)


@click.command("add")
@click.argument("link-source", type=click.Path(path_type=Path))
@click.option("-f", "--force-overwrite", type=bool, is_flag=True, default=False)
@click.option(
    "-p",
    "--project",
    "project_path",
    type=click.Path(path_type=Path),
    default=Path("."),
)
@click.option("-n", "--targe-name", type=str, default=None)
def add_link(
    link_source: Path, project_path: Path, target_name: str, force_overwrite: bool
):
    project = Project.from_path(project_path=project_path)
    if force_overwrite:
        if link_source.is_symlink():
            link_source.unlink()
        else:
            if link_source.exists():
                shutil.rmtree(link_source)

    project.add_link(source=link_source, target_name=target_name)


@click.command("restore")
@click.argument("project-path", type=click.Path(path_type=Path), default=Path("."))
@click.option("-n", "--target-name", multiple=True)
def restore(project_path, target_name):
    project = Project.from_path(project_path=project_path)
    if len(target_name) == 0:
        target_name = list(project.config.links)
    for link_name in target_name:
        project.restore_link(link_name)


cli.add_command(init_project)
cli.add_command(add_link)
cli.add_command(restore)
