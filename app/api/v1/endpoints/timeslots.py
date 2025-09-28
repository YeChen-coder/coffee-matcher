from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db
from app.crud import timeslots as timeslots_crud
from app.schemas import timeslots as timeslot_schemas

router = APIRouter(prefix="/timeslots", tags=["timeslots"])


@router.get("/", response_model=List[timeslot_schemas.TimeSlotRead])
def read_timeslots(
    *, session: Session = Depends(get_db), user_id: int | None = None
) -> List[timeslot_schemas.TimeSlotRead]:
    if user_id is not None:
        return timeslots_crud.get_by_user(session, user_id=user_id)
    return timeslots_crud.get_available(session)


@router.post(
    "/", response_model=timeslot_schemas.TimeSlotRead, status_code=status.HTTP_201_CREATED
)
def create_timeslot(
    *, session: Session = Depends(get_db), slot_in: timeslot_schemas.TimeSlotCreate
) -> timeslot_schemas.TimeSlotRead:
    return timeslots_crud.create(session, slot_in=slot_in)


@router.put("/{slot_id}", response_model=timeslot_schemas.TimeSlotRead)
def update_timeslot(
    *, session: Session = Depends(get_db), slot_id: int, slot_in: timeslot_schemas.TimeSlotUpdate
) -> timeslot_schemas.TimeSlotRead:
    slot = timeslots_crud.get(session, slot_id=slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    return timeslots_crud.update(session, db_slot=slot, slot_in=slot_in)


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeslot(*, session: Session = Depends(get_db), slot_id: int) -> None:
    slot = timeslots_crud.get(session, slot_id=slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    timeslots_crud.delete(session, db_slot=slot)
