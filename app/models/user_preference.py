from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    preference_type: str
    preference_value: str
    confidence: int = Field(default=1)

    user: "User" = Relationship(back_populates="preferences")
