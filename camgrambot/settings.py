import os

import yaml
import pydantic


SETTINGS_FILE = os.getenv("SETTINGS_FILE", "settings.yaml")


class TelegramBotSettings(pydantic.BaseModel):
    token: pydantic.SecretStr


class Settings(pydantic.BaseModel):
    telegrambot: TelegramBotSettings

    @classmethod
    def get(cls) -> "Settings":
        try:
            return cls._singleton
        except AttributeError:
            cls._singleton = cls._load_settings_file()
            return cls._singleton

    @classmethod
    def _load_settings_file(cls) -> "Settings":
        with open(SETTINGS_FILE, "r") as f:
            read_dict = yaml.safe_load(f)
            return cls.model_validate(read_dict)
