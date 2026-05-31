"""
Схемы лайков курсов.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LikeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    course_id: int
    created_at: datetime


class LikeToggleResponse(BaseModel):
    course_id: int
    is_liked: bool
    likes_count: int
