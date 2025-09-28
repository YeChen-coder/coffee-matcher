from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class MatchRequestBase(SQLModel):
    requester_id: int
    target_id: int
    time_slot_id: Optional[int] = None
    proposed_time: datetime
    venue_id: int
    message: Optional[str] = None


class MatchRequestCreate(MatchRequestBase):
    pass


class MatchRequestUpdate(SQLModel):
    time_slot_id: Optional[int] = None
    proposed_time: Optional[datetime] = None
    venue_id: Optional[int] = None
    status: Optional[str] = None
    message: Optional[str] = None


class MatchRequestRead(MatchRequestBase):
    id: int
    status: str
    created_at: datetime
