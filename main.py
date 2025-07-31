# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# Импортируем все наши модули
from database import get_db
from crud import user as user_crud
from crud import announcement as announcement_crud
from schemas import user as user_schema
from schemas import announcement as announcement_schema

# --- Создание экземпляра FastAPI и настройка CORS ---
app = FastAPI(
    title="Farmer's App API",
    description="API для приложения фермерского сообщества",
    version="0.3.0"  # Повысим версию, чтобы точно видеть изменения
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://farmer-app-frontend-ekracyjhz-rustams-projects-a2abc4d7.vercel.app/"
    "https://*.vercel.app" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    # Явно разрешаем все методы, включая OPTIONS
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
    # Явно разрешаем все стандартные и нестандартные заголовки
    allow_headers=["*"],
)


# --- Базовый эндпоинт ---
@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API для приложения фермеров!"}


# --- Эндпоинты для работы с пользователями ---
@app.post("/users/get_or_create", response_model=user_schema.UserDisplay, tags=["Users"])
def get_or_create_user_endpoint(
    user_data: user_schema.UserCreate,
    db: Session = Depends(get_db)
):
    return user_crud.get_or_create_user(db=db, user=user_data)


@app.get("/users/{user_id}", response_model=user_schema.UserDisplay, tags=["Users"])
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# --- Эндпоинт для виджета цен (ЗАГЛУШКА) ---
@app.get("/prices/{region}", tags=["Prices"])
def get_prices_for_region(region: str):
    """
    Возвращает цены на ключевые культуры для указанного региона.
    (Сейчас используются заглушки)
    """
    print(f"Запрошены фейковые цены для региона: {region}")
    
    # В будущем эти данные будут браться из базы данных
    mock_prices = [
        {"crop_name": "Пшеница 3 кл.", "price": 12500, "trend": "up"},
        {"crop_name": "Подсолнечник", "price": 28100, "trend": "down"},
        {"crop_name": "Ячмень", "price": 10200, "trend": "stable"}
    ]
    return mock_prices

@app.put("/users/{user_id}/region", response_model=user_schema.UserDisplay, tags=["Users"])
def update_user_region_endpoint(
    user_id: int,
    region_data: user_schema.UserUpdate, # Используем нашу схему для обновления
    db: Session = Depends(get_db)
):
    """
    Обновляет регион для пользователя с указанным user_id.
    """
    updated_user = user_crud.update_user_region(
        db=db, 
        user_id=user_id, 
        region=region_data.region
    )
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# --- Эндпоинты для работы с объявлениями ---
@app.post("/announcements/", response_model=announcement_schema.AnnouncementDisplay, tags=["Announcements"])
def create_new_announcement(
    announcement: announcement_schema.AnnouncementCreate, # <-- Схема теперь без региона
    current_user_id: int,
    db: Session = Depends(get_db)
):
    # 1. Находим пользователя-автора в базе данных
    db_user = user_crud.get_user(db, user_id=current_user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Author (user) not found")

    # 2. Передаем в CRUD-функцию сам ОБЪЕКТ пользователя
    return announcement_crud.create_announcement(
        db=db,
        announcement=announcement,
        owner=db_user # <-- Передаем весь объект
    )

@app.get("/announcements/", response_model=List[announcement_schema.AnnouncementDisplay], tags=["Announcements"])
def read_announcements(
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = None,
    db: Session = Depends(get_db)
):
    announcements = announcement_crud.get_announcements(
        db, skip=skip, limit=limit, region=region
    )
    return announcements

@app.get("/announcements/{announcement_id}", response_model=announcement_schema.AnnouncementDisplay, tags=["Announcements"])
def read_announcement_details(
    announcement_id: int,
    db: Session = Depends(get_db)
):
    """
    Получает детальную информацию об одном объявлении по его ID.
    """
    db_announcement = announcement_crud.get_announcement_by_id(db, announcement_id=announcement_id)
    if db_announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return db_announcement

# --- Блок для прямого запуска (для отладки) ---
if __name__ == "__main__":
    import uvicorn
    print("--- Запуск в режиме прямой отладки ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)