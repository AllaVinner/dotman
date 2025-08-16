from pathlib import Path
from pydantic import BaseModel, Field
import toml


CONFIG_FILE_NAME = ".dotman.toml"

DotfilePath = Path


class Config(BaseModel):
    dotfiles: dict[DotfilePath, DotfilePath] = Field(default_factory=lambda: dict())

    def write(self, path: Path) -> None:
        config_dict = self.model_dump(mode="json", exclude_unset=True)
        if config_dict == dict():
            config_dict = self.__class__(dotfiles=dict()).model_dump(mode="json")
        with open(path, "w", encoding="utf-8") as f:
            toml.dump(config_dict, f)
