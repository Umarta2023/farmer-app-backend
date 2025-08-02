# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки для подключения к базе данных (будут браться из окружения)
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # --- КЛЮЧИ UPLOADCARE (будут браться из окружения) ---
    UPLOADCARE_PUBLIC_KEY: str
    UPLOADCARE_SECRET_KEY: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # Указываем, что нужно читать переменные из .env файла (для локальной разработки)
        env_file = ".env"

settings = Settings()