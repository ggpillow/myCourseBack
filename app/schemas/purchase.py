"""
Схемы покупок курсов.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.course import CourseRead


class PurchaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    created_at: datetime


class PurchaseWithCourse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    course: CourseRead
