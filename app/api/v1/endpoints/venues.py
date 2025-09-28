from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db
from app.crud import venues as venues_crud
from app.schemas import venues as venue_schemas

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("/", response_model=List[venue_schemas.VenueRead])
def read_venues(
    *, session: Session = Depends(get_db), venue_type: str | None = None
) -> List[venue_schemas.VenueRead]:
    return venues_crud.get_multi(session, venue_type=venue_type)


@router.post(
    "/", response_model=venue_schemas.VenueRead, status_code=status.HTTP_201_CREATED
)
def create_venue(
    *, session: Session = Depends(get_db), venue_in: venue_schemas.VenueCreate
) -> venue_schemas.VenueRead:
    return venues_crud.create(session, venue_in=venue_in)


@router.put("/{venue_id}", response_model=venue_schemas.VenueRead)
def update_venue(
    *, session: Session = Depends(get_db), venue_id: int, venue_in: venue_schemas.VenueUpdate
) -> venue_schemas.VenueRead:
    venue = venues_crud.get(session, venue_id=venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venues_crud.update(session, db_venue=venue, venue_in=venue_in)


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(*, session: Session = Depends(get_db), venue_id: int) -> None:
    venue = venues_crud.get(session, venue_id=venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    venues_crud.delete(session, db_venue=venue)
