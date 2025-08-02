# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Эта строка теперь ГЛАВНАЯ. Pydantic-settings будет искать
    # переменную окружения с именем DATABASE_URL и читать ее значение.
    UPLOADCARE_PUBLIC_KEY: str = "60c2ed7ac31f52bfb943"
    UPLOADCARE_SECRET_KEY: str = "ba986a9d0e3ebf98bb06"
    DATABASE_URL: str

    class Config:
        # Указываем, что нужно искать переменные в .env файле (для локальной разработки)
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()