from pathlib import Path
import click
from dotman.init import init


@click.command("init")
@click.argument("project_path", type=click.Path(path_type=Path), required=False)
def init_project(project_path: Path | None) -> None:
    if project_path is None:
        project_path = Path(".")
    init(project_path=project_path)


@click.group()
def cli():
    pass


cli.add_command(init_project)


def main() -> None:
    cli()
