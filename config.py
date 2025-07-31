# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Эта строка теперь ГЛАВНАЯ. Pydantic-settings будет искать
    # переменную окружения с именем DATABASE_URL и читать ее значение.
    DATABASE_URL: str

    class Config:
        # Указываем, что нужно искать переменные в .env файле (для локальной разработки)
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()