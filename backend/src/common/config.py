from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    access_token_expire_minutes: int = 30

    tmdb_api_key: str
    tmdb_base_url: str = "https://api.themoviedb.org/3"

    resend_api_key: str
    email_from: str = "noreply@cinema-booking.ru"


config = Config()  # type: ignore[call-arg]
