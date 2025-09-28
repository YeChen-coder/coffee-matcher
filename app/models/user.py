from typing import List, Optional, TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.match_request import MatchRequest
    from app.models.timeslot import TimeSlot
    from app.models.user_preference import UserPreference
    from app.models.venue import Venue


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: EmailStr = Field(index=True, sa_column_kwargs={"unique": True})
    bio: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    ai_analysis_json: Optional[str] = None

    time_slots: List["TimeSlot"] = Relationship(back_populates="user")
    sent_requests: List["MatchRequest"] = Relationship(
        back_populates="requester",
        sa_relationship_kwargs={"foreign_keys": "MatchRequest.requester_id"},
    )
    received_requests: List["MatchRequest"] = Relationship(
        back_populates="target",
        sa_relationship_kwargs={"foreign_keys": "MatchRequest.target_id"},
    )
    preferences: List["UserPreference"] = Relationship(back_populates="user")
    created_venues: List["Venue"] = Relationship(back_populates="created_by")
