# crud/user.py
from sqlalchemy.orm import Session
from models import user as user_model
from schemas import user as user_schema

def get_user(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def create_user(db: Session, user: user_schema.UserCreate):
    # В Pydantic v2 .dict() считается устаревшим, используем .model_dump()
    db_user = user_model.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_or_create_user(db: Session, user: user_schema.UserCreate):
    db_user = get_user(db, user_id=user.id)
    if db_user:
        return db_user
    return create_user(db, user=user)

def update_user_region(db: Session, user_id: int, region: str):
    """Обновляет регион для указанного пользователя."""
    # Находим пользователя в базе
    db_user = get_user(db, user_id=user_id)
    
    if db_user:
        # Если нашли, обновляем поле region
        db_user.region = region
        db.commit() # Сохраняем изменения
        db.refresh(db_user) # Обновляем объект из БД
    
    return db_user