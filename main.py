# main.py
from fastapi import FastAPI, Depends, HTTPException, APIRouter # <-- Добавляем APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# Импортируем все наши модули
from database import get_db
from crud import user as user_crud
from crud import announcement as announcement_crud
from schemas import user as user_schema
from schemas import announcement as announcement_schema

# --- Создание экземпляра FastAPI ---
app = FastAPI(
    title="Farmer's App API",
    description="API для приложения фермерского сообщества",
    version="1.0.0-STABLE" # Финальная стабильная версия
)

# --- Настройка CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- СОЗДАЕМ РОУТЕР С ПРЕФИКСОМ /api ---
api_router = APIRouter(prefix="/api")


# --- Базовый эндпоинт ---
@app.get("/")
def read_root():
    return {"message": "API для фермеров, версия 1.0.0"}


# --- Эндпоинты, которые будут входить в /api ---

# Заменяем @app.post на @api_router.post и убираем /api из пути
@api_router.post("/users/get_or_create", response_model=user_schema.UserDisplay, tags=["Users"])
def get_or_create_user_endpoint(user_data: user_schema.UserCreate, db: Session = Depends(get_db)):
    return user_crud.get_or_create_user(db=db, user=user_data)

@api_router.get("/users/{user_id}", response_model=user_schema.UserDisplay, tags=["Users"])
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    # ... (код функции без изменений)
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@api_router.get("/users/{user_id}/announcements", response_model=List[announcement_schema.AnnouncementDisplay], tags=["Users"])
def read_user_announcements(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает список объявлений, созданных пользователем.
    """
    # В реальном приложении можно было бы добавить проверку,
    # что пользователь с user_id вообще существует.
    announcements = announcement_crud.get_announcements_by_owner_id(db=db, owner_id=user_id)
    return announcements

@api_router.get("/prices/{region}", tags=["Prices"])
def get_prices_for_region(region: str):
    # ... (код функции без изменений)
    print(f"Запрошены фейковые цены для региона: {region}")
    mock_prices = [
        {"crop_name": "Пшеница 3 кл.", "price": 12500, "trend": "up"},
        {"crop_name": "Подсолнечник", "price": 28100, "trend": "down"},
        {"crop_name": "Ячмень", "price": 10200, "trend": "stable"}
    ]
    return mock_prices

@api_router.put("/users/{user_id}/region", response_model=user_schema.UserDisplay, tags=["Users"])
def update_user_region_endpoint(user_id: int, region_data: user_schema.UserUpdate, db: Session = Depends(get_db)):
    # ... (код функции без изменений)
    updated_user = user_crud.update_user_region(
        db=db, user_id=user_id, region=region_data.region
    )
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@api_router.post("/announcements/", response_model=announcement_schema.AnnouncementDisplay, tags=["Announcements"])
def create_new_announcement(announcement: announcement_schema.AnnouncementCreate, current_user_id: int, db: Session = Depends(get_db)):
    # ... (код функции без изменений)
    db_user = user_crud.get_user(db, user_id=current_user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Author (user) not found")
    return announcement_crud.create_announcement(db=db, announcement=announcement, owner=db_user)

@api_router.get("/announcements/", response_model=List[announcement_schema.AnnouncementDisplay], tags=["Announcements"])
def read_announcements(skip: int = 0, limit: int = 100, region: Optional[str] = None, db: Session = Depends(get_db)):
    # ... (код функции без изменений)
    announcements = announcement_crud.get_announcements(db, skip=skip, limit=limit, region=region)
    return announcements

@api_router.get("/announcements/{announcement_id}", response_model=announcement_schema.AnnouncementDisplay, tags=["Announcements"])
def read_announcement_details(announcement_id: int, db: Session = Depends(get_db)):
    # ... (код функции без изменений)
    db_announcement = announcement_crud.get_announcement_by_id(db, announcement_id=announcement_id)
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return db_announcement

# --- ПОДКЛЮЧАЕМ РОУТЕР К ОСНОВНОМУ ПРИЛОЖЕНИЮ ---
app.include_router(api_router)


# --- Блок для прямого запуска (для отладки) ---
if __name__ == "__main__":
    import uvicorn
    print("--- Запуск в режиме прямой отладки ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)