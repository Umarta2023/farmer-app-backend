# main.py

import shutil
import uuid
import os
from fastapi import FastAPI, Depends, HTTPException, APIRouter, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Импортируем наши модули
from database import get_db
from crud import user as user_crud
from crud import announcement as announcement_crud
from schemas import user as user_schema
from schemas import announcement as announcement_schema

# --- Константы и начальная настройка ---
UPLOADS_DIR = "uploads"

# --- Создание экземпляра FastAPI и роутера ---
app = FastAPI(
    title="Farmer's App API",
    description="API для приложения фермерского сообщества",
    version="2.1.0-prefixed-storage"
)

api_router = APIRouter(prefix="/api")

# --- Настройка CORS ---
# Для продакшена лучше указать конкретные домены фронтенда
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Создаем папку для загрузок при старте приложения ---
os.makedirs(UPLOADS_DIR, exist_ok=True)

# --- "Примонтируем" папку uploads для раздачи картинок ---
# Любой запрос на /uploads/some_file.jpg будет искать файл в папке uploads на сервере
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


# =================================================================
# ===                  ОПРЕДЕЛЕНИЕ API-ЭНДПОИНТОВ               ===
# =================================================================

# --- Системные эндпоинты ---
@api_router.get("/health", status_code=200, tags=["System"])
def health_check():
    """Проверка работоспособности сервера."""
    return {"status": "ok"}

# --- Эндпоинты для работы с пользователями ---
@api_router.post("/users/get_or_create", response_model=user_schema.UserDisplay, tags=["Users"])
def get_or_create_user_endpoint(user_data: user_schema.UserCreate, db: Session = Depends(get_db)):
    return user_crud.get_or_create_user(db=db, user=user_data)

@api_router.get("/users/{user_id}", response_model=user_schema.UserDisplay, tags=["Users"])
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None: raise HTTPException(status_code=404, detail="User not found")
    return db_user

@api_router.put("/users/{user_id}/region", response_model=user_schema.UserDisplay, tags=["Users"])
def update_user_region_endpoint(user_id: int, region_data: user_schema.UserUpdate, db: Session = Depends(get_db)):
    updated_user = user_crud.update_user_region(db=db, user_id=user_id, region=region_data.region)
    if updated_user is None: raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@api_router.get("/users/{user_id}/announcements", response_model=List[announcement_schema.AnnouncementDisplay], tags=["Users"])
def read_user_announcements(user_id: int, db: Session = Depends(get_db)):
    announcements = announcement_crud.get_announcements_by_owner_id(db=db, owner_id=user_id)
    return announcements


# --- Эндпоинты для цен ---
@api_router.get("/prices/{region}", tags=["Prices"])
def get_prices_for_region(region: str):
    # В будущем эти данные будут браться из базы данных или парсера
    mock_prices = [
        {"crop_name": "Пшеница 3 кл.", "price": 12500, "trend": "up"},
        {"crop_name": "Подсолнечник", "price": 28100, "trend": "down"},
    ]
    return mock_prices


# --- Эндпоинты для работы с объявлениями ---
@api_router.post("/announcements/", response_model=announcement_schema.AnnouncementDisplay, tags=["Announcements"])
def create_new_announcement(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    current_user_id: int = Form(...),
    db: Session = Depends(get_db),
    image: Optional[UploadFile] = File(None) 
):
    db_user = user_crud.get_user(db, user_id=current_user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Author (user) not found")

    image_url_to_save = None
    if image:
        # Генерируем уникальное имя файла и путь один раз
        unique_filename = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join(UPLOADS_DIR, unique_filename)
        
        # Сохраняем файл на диск
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        # Формируем URL для записи в базу данных
        image_url_to_save = f"/uploads/{unique_filename}"
        
    announcement_data = announcement_schema.AnnouncementCreate(
        title=title, description=description, price=price
    )
    
    return announcement_crud.create_announcement(
        db=db,
        announcement=announcement_data,
        owner=db_user,
        image_url=image_url_to_save
    )

@api_router.get("/announcements/", response_model=List[announcement_schema.AnnouncementDisplay], tags=["Announcements"])
def read_announcements(skip: int = 0, limit: int = 100, region: Optional[str] = None, db: Session = Depends(get_db)):
    announcements = announcement_crud.get_announcements(db, skip=skip, limit=limit, region=region)
    return announcements

@api_router.get("/announcements/{announcement_id}", response_model=announcement_schema.AnnouncementDisplay, tags=["Announcements"])
def read_announcement_details(announcement_id: int, db: Session = Depends(get_db)):
    db_announcement = announcement_crud.get_announcement_by_id(db, announcement_id=announcement_id)
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return db_announcement


# =================================================================
# ===          ПОДКЛЮЧЕНИЕ РОУТЕРОВ И ЗАПУСК ПРИЛОЖЕНИЯ         ===
# =================================================================

# Подключаем роутер с префиксом /api
app.include_router(api_router)

# Корневой эндпоинт для проверки, что сам сайт работает
@app.get("/")
def read_root():
    return {"message": f"API для фермеров, версия {app.version}"}

# Блок для прямого запуска (удобно для локальной отладки)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)