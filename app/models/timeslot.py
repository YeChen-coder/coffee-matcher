from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User


class TimeSlot(SQLModel, table=True):
    __tablename__ = "time_slots"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    start_time: datetime
    end_time: datetime
    status: str = Field(default="available")

    user: "User" = Relationship(back_populates="time_slots")
