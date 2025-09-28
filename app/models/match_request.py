from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.timeslot import TimeSlot
    from app.models.user import User
    from app.models.venue import Venue


class MatchRequest(SQLModel, table=True):
    __tablename__ = "match_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="users.id", index=True)
    target_id: int = Field(foreign_key="users.id", index=True)
    time_slot_id: Optional[int] = Field(default=None, foreign_key="time_slots.id")
    proposed_time: datetime
    venue_id: int = Field(foreign_key="venues.id")
    status: str = Field(default="pending")
    message: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    requester: "User" = Relationship(
        back_populates="sent_requests",
        sa_relationship_kwargs={"foreign_keys": "MatchRequest.requester_id"},
    )
    target: "User" = Relationship(
        back_populates="received_requests",
        sa_relationship_kwargs={"foreign_keys": "MatchRequest.target_id"},
    )
    venue: "Venue" = Relationship()
    time_slot: Optional["TimeSlot"] = Relationship()
