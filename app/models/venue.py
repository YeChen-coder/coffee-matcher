from typing import Optional

from sqlmodel import Field, SQLModel


class Venue(SQLModel, table=True):
    __tablename__ = "venues"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str = Field(description="coffee or restaurant")
    price_range: str
    location: str
    description: str = Field(default="")
