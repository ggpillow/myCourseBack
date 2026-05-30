from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.like import Like
    from app.models.purchase import Purchase
    from app.models.topic import Topic


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    price: Mapped[int] = mapped_column(nullable=False, default=0)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    category: Mapped["Category"] = relationship(back_populates="courses")
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Topic.order_index",
    )
    purchases: Mapped[list["Purchase"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
