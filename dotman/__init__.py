version = "0.0.1"
__version__ = "0.0.2"

import logging

logging.basicConfig(
    encoding="utf-8",
    format="%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.WARN,
)

logger = logging.getLogger(__name__)
