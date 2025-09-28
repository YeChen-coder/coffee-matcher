from typing import Optional

from sqlmodel import SQLModel


class VenueBase(SQLModel):
    name: str
    type: str
    price_range: str
    location: str
    description: Optional[str] = None
    created_by_id: Optional[int] = None


class VenueCreate(VenueBase):
    pass


class VenueUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[str] = None
    price_range: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    created_by_id: Optional[int] = None


class VenueRead(VenueBase):
    id: int
