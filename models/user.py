# models/user.py
from sqlalchemy import Column, BigInteger, String, DateTime, func
from database import Base # Импортируем нашу базовую модель

class User(Base):
    __tablename__ = 'users' # Название таблицы в базе данных

    # Описываем колонки таблицы
    id = Column(BigInteger, primary_key=True, index=True) # Уникальный ID пользователя из Telegram
    username = Column(String, nullable=True, unique=True) # Имя пользователя (@username)
    first_name = Column(String, nullable=False) # Имя
    last_name = Column(String, nullable=True) # Фамилия
    region = Column(String, nullable=True) # Регион, который укажет пользователь
    
    created_at = Column(DateTime, server_default=func.now()) # Дата создания записи
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # Дата обновления

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"