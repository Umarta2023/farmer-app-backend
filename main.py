# main.py

import uuid
from fastapi import FastAPI, Depends, HTTPException, APIRouter, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from pyuploadcare import Uploadcare
from config import settings

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
    version="1.2.0" # Повышаем версию с Uploadcare
)

# --- Конфигурация Uploadcare ---
uploadcare = Uploadcare(
    public_key=settings.UPLOADCARE_PUBLIC_KEY,
    secret_key=settings.UPLOADCARE_SECRET_KEY,
)

# --- Настройка CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Создаем роутер с префиксом /api ---
api_router = APIRouter(prefix="/api")

# --- Базовый эндпоинт (вне /api) ---
@app.get("/")
def read_root():
    return {"message": "API для фермеров, версия 1.2.0"}

# --- Эндпоинты, которые будут входить в /api ---

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

@api_router.get("/prices/{region}", tags=["Prices"])
def get_prices_for_region(region: str):
    mock_prices = [
        {"crop_name": "Пшеница 3 кл.", "price": 12500, "trend": "up"},
        {"crop_name": "Подсолнечник", "price": 28100, "trend": "down"},
    ]
    return mock_prices

@api_router.post("/announcements/", response_model=announcement_schema.AnnouncementDisplay, tags=["Announcements"])
def create_new_announcement(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    current_user_id: int = Form(...),
    db: Session = Depends(get_db),
    image: UploadFile = File(None) 
):
    db_user = user_crud.get_user(db, user_id=current_user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Author (user) not found")

    image_url_to_save = None
    if image:
        # Читаем файл в байты
        file_bytes = image.file.read()
        # Загружаем файл в Uploadcare
        ucare_file = uploadcare.upload(file_bytes)
        # Получаем готовый CDN URL
        image_url_to_save = ucare_file.cdn_url
        print(f"Файл загружен в Uploadcare, URL: {image_url_to_save}")
        
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


# --- Подключаем роутер к основному приложению ---
app.include_router(api_router)


# --- Блок для прямого запуска (для отладки) ---
if __name__ == "__main__":
    import uvicorn
    print("--- Запуск в режиме прямой отладки ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)