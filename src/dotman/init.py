import logging
from pathlib import Path
from dotman.exceptions import DotmanException
from dotman.util import format_path
from dotman.config import CONFIG_FILE_NAME, Config

logger = logging.getLogger("__name__")


def _init(project_path: Path) -> None:
    logger.info(f"Initialize project at {format_path(project_path)}")
    logger.debug(f"Ensure project folder {format_path(project_path)}")
    project_path.mkdir(parents=True, exist_ok=True)
    dotman_config_path = Path(project_path, CONFIG_FILE_NAME)
    if dotman_config_path.exists():
        logger.info("Dotman project already initialized")
        raise DotmanException("Dotman project already initialized")
    config = Config()
    logger.debug(f"Write configuration to {format_path(dotman_config_path)}")
    config.write(dotman_config_path)
    logger.info(f"Complete initialization of project at {format_path(project_path)}")


def init(project_path: Path | str | None):
    if project_path is None:
        project_path = Path(".")
    project_path = Path(project_path)
    _init(project_path)
