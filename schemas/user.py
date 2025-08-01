# schemas/user.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import datetime

# --- Схемы для получения данных от пользователя ---

class UserBase(BaseModel):
    id: int = Field(..., description="Уникальный ID пользователя из Telegram")
    username: Optional[str] = Field(None, description="Имя пользователя (@username)")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    region: Optional[str] = Field(None, description="Регион, указанный пользователем")

# schemas/user.py
class UserCreate(BaseModel):
    id: int = Field(...)
    username: Optional[str] = Field(None)
    first_name: str = Field(...)
    last_name: Optional[str] = Field(None)
    # Здесь НЕ должно быть region

class UserUpdate(BaseModel):
    region: Optional[str] = Field(None, description="Регион, указанный пользователем")


# --- Схемы для возврата данных пользователю ---

class UserDisplay(UserBase):
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    # Эта конфигурация позволяет Pydantic читать данные из объектов SQLAlchemy
    # В Pydantic v2 `orm_mode` заменен на `from_attributes`
    model_config = ConfigDict(from_attributes=True)