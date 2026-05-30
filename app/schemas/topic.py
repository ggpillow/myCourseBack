from pydantic import BaseModel, ConfigDict


class TopicCreate(BaseModel):
    title: str
    content: str = ""
    order_index: int = 1
    is_free: bool = False


class TopicUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    order_index: int | None = None
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
