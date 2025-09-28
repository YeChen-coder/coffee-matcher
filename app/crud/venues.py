from typing import List, Optional

from sqlmodel import Session, select

from app.models.venue import Venue
from app.schemas.venues import VenueCreate, VenueUpdate


def _model_dump(model) -> dict:
    return (
        model.model_dump(exclude_unset=True)
        if hasattr(model, "model_dump")
        else model.dict(exclude_unset=True)
    )


def get(session: Session, venue_id: int) -> Optional[Venue]:
    return session.get(Venue, venue_id)


def get_multi(session: Session, *, skip: int = 0, limit: int = 100, venue_type: Optional[str] = None) -> List[Venue]:
    statement = select(Venue)
    if venue_type:
        statement = statement.where(Venue.type == venue_type)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement))


def create(session: Session, venue_in: VenueCreate) -> Venue:
    venue = Venue(**_model_dump(venue_in))
    session.add(venue)
    session.commit()
    session.refresh(venue)
    return venue


def update(session: Session, db_venue: Venue, venue_in: VenueUpdate) -> Venue:
    update_data = _model_dump(venue_in)
    for field, value in update_data.items():
        setattr(db_venue, field, value)
    session.add(db_venue)
    session.commit()
    session.refresh(db_venue)
    return db_venue


def delete(session: Session, db_venue: Venue) -> None:
    session.delete(db_venue)
    session.commit()
