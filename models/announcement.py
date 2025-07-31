# models/announcement.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Announcement(Base):
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    region = Column(String, index=True, nullable=True)
    
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Эта строка создает связь с моделью User.
    # SQLAlchemy будет понимать, что owner_id - это ссылка на пользователя.
    owner = relationship("User") 

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Announcement(id={self.id}, title='{self.title}')>"