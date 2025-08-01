# crud/user.py
from sqlalchemy.orm import Session
from models import user as user_model
from schemas import user as user_schema

def get_user(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def create_user(db: Session, user: user_schema.UserCreate):
    # Создаем объект, явно передавая поля, которые есть в схеме
    db_user = user_model.User(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
        # region по умолчанию будет NULL
    )
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
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db_user.region = region
        db.commit()
        db.refresh(db_user)
    return db_user