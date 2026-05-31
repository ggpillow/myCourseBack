"""
Схемы курсов: создание, обновление, краткое и детальное отображение.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryRead
from app.schemas.topic import TopicPreview, TopicRead


class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Название курса")
    description: str = Field(default="", max_length=5000)
    price: int = Field(default=0, ge=0, description="Цена в рублях, не может быть отрицательной")
    category_id: int = Field(..., gt=0)


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    price: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    price: int
    created_at: datetime
    category: CategoryRead
    likes_count: int = 0
    topics_count: int = 0


class CourseDetail(CourseRead):
    topics: list[TopicRead | TopicPreview] = []
    is_purchased: bool = False
    is_liked: bool = False