"""
Схемы тем курса: создание, обновление, полное и preview-отображение.
"""

from pydantic import BaseModel, ConfigDict, Field


class TopicCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="", max_length=50000)
    order_index: int = Field(default=1, ge=1, description="Порядок отображения, начиная с 1")
    is_free: bool = False


class TopicUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=50000)
    order_index: int | None = Field(default=None, ge=1)
    is_free: bool | None = None


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    order_index: int
    is_free: bool
    course_id: int


class TopicPreview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    order_index: int
    is_free: bool