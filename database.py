# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings # Импортируем наши настройки

# 1. Создаем "движок" для подключения к базе данных.
#    Он использует URL, который мы сформировали в config.py.
engine = create_engine(settings.DATABASE_URL)

# 2. Создаем "фабрику сессий".
#    Каждый экземпляр SessionLocal будет отдельной сессией (разговором) с базой данных.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Создаем базовый класс для наших моделей.
#    Все наши будущие модели таблиц (User, Announcement и т.д.) будут наследоваться от него.
#    Это тот самый "Base", который не могли найти другие файлы.
Base = declarative_base()

# 4. Создаем зависимость (dependency) для FastAPI.
#    Эта функция будет вызываться для каждого API-запроса, который требует доступа к БД.
def get_db():
    """
    Зависимость (dependency) для получения сессии базы данных.
    Открывает сессию для каждого запроса и элегантно закрывает ее после.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()