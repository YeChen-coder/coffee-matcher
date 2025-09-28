from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class TimeSlotBase(SQLModel):
    start_time: datetime
    end_time: datetime
    status: str = "available"


class TimeSlotCreate(TimeSlotBase):
    user_id: int


class TimeSlotUpdate(SQLModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class TimeSlotRead(TimeSlotBase):
    id: int
    user_id: int
