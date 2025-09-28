from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User


class Venue(SQLModel, table=True):
    __tablename__ = "venues"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str = Field(description="coffee or restaurant")
    price_range: str
    location: str
    description: str = Field(default="")
    created_by_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)

    created_by: Optional["User"] = Relationship(back_populates="created_venues")
