# crud/announcement.py
from sqlalchemy.orm import Session
from models import announcement as announcement_model
from schemas import announcement as announcement_schema
from typing import Optional
from models import user as user_model

def create_announcement(db: Session, announcement: announcement_schema.AnnouncementCreate, owner: user_model.User, image_url: Optional[str] = None):
    """Создает новое объявление, автоматически подставляя регион из профиля автора."""
    db_announcement = announcement_model.Announcement(
        title=announcement.title,
        description=announcement.description,
        price=announcement.price,
        owner_id=owner.id,
        region=owner.region,  
        image_url=image_url
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

def get_announcements(db: Session, skip: int = 0, limit: int = 100, region: Optional[str] = None):
    """Возвращает список объявлений с возможностью фильтрации по региону."""
    query = db.query(announcement_model.Announcement)
    
    # Если регион передан, добавляем фильтр
    if region:
        query = query.filter(announcement_model.Announcement.region == region)
        
    return query.offset(skip).limit(limit).all()

def get_announcement_by_id(db: Session, announcement_id: int):
    """Возвращает одно объявление по его ID."""
    return db.query(announcement_model.Announcement).filter(announcement_model.Announcement.id == announcement_id).first()

def get_announcements_by_owner_id(db: Session, owner_id: int):
    """Возвращает все объявления указанного пользователя."""
    return db.query(announcement_model.Announcement).filter(announcement_model.Announcement.owner_id == owner_id).all()