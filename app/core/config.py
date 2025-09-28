from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Coffee Matcher API"
    api_v1_str: str = "/api/v1"
    sqlite_file: str = "coffee_matcher.db"
    echo_sql: bool = False

    @property
    def database_url(self) -> str:
        db_path = Path(self.sqlite_file).absolute()
        return f"sqlite:///{db_path}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
