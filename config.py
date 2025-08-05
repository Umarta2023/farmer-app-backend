# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки для подключения к базе данных
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # Ключей Uploadcare здесь больше нет

    @property
    def DATABASE_URL(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()