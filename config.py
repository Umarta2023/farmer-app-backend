# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки для подключения к базе данных
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"  # ИЗМЕНЕНИЕ: стандартный суперпользователь
    DB_PASS: str = "postgres" # ВАШ ПАРОЛЬ, который вы задали при установке
    DB_NAME: str = "farmer_db"

    @property
    def DATABASE_URL(self):
        # Формируем URL для подключения к SQLAlchemy
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()