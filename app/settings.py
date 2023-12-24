from pydantic_settings import BaseSettings, SettingsConfigDict
import os

env_file = os.path.dirname(__file__) + "\..\.env"


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=env_file, extra='ignore')


settings = Settings()
