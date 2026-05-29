from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    access_token_expire_minutes: int = 30


config = Config()
