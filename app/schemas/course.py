from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryRead
from app.schemas.topic import TopicPreview, TopicRead


class CourseCreate(BaseModel):
    title: str
    description: str = ""
    price: int = 0
    category_id: int


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    category_id: int | None = None


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
