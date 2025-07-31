# schemas/announcement.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import datetime

# Импортируем схему пользователя, чтобы показать ее в ответе
from .user import UserDisplay

# --- Схема для создания объявления ---
class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0, description="Цена должна быть больше нуля")
    
# --- Схема для отображения объявления ---
class AnnouncementDisplay(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    region: Optional[str] = None
    created_at: datetime.datetime
    
    # Здесь мы будем отображать полную информацию об авторе
    owner: UserDisplay 

    model_config = ConfigDict(from_attributes=True)