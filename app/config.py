from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    admin_ids: str = ""
    database_path: str = "./data/outfit_bg.sqlite3"
    background_path: str = "./data/background.jpg"
    placement_width_ratio: float = 0.72
    placement_height_ratio: float = 0.82
    placement_bottom_margin_ratio: float = 0.04
    max_photo_mb: int = 20
    output_quality: int = 95

    @property
    def admins(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_ids.split(",") if x.strip().isdigit()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
