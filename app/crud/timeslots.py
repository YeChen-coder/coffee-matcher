from typing import List, Optional

from sqlmodel import Session, select

from app.models.timeslot import TimeSlot
from app.schemas.timeslots import TimeSlotCreate, TimeSlotUpdate


def _model_dump(model) -> dict:
    return (
        model.model_dump(exclude_unset=True)
        if hasattr(model, "model_dump")
        else model.dict(exclude_unset=True)
    )


def get(session: Session, slot_id: int) -> Optional[TimeSlot]:
    return session.get(TimeSlot, slot_id)


def get_by_user(session: Session, user_id: int) -> List[TimeSlot]:
    statement = select(TimeSlot).where(TimeSlot.user_id == user_id)
    return list(session.exec(statement))


def get_available(session: Session) -> List[TimeSlot]:
    statement = select(TimeSlot).where(TimeSlot.status == "available")
    return list(session.exec(statement))


def create(session: Session, slot_in: TimeSlotCreate) -> TimeSlot:
    slot = TimeSlot(**_model_dump(slot_in))
    session.add(slot)
    session.commit()
    session.refresh(slot)
    return slot


def update(session: Session, db_slot: TimeSlot, slot_in: TimeSlotUpdate) -> TimeSlot:
    update_data = _model_dump(slot_in)
    for field, value in update_data.items():
        setattr(db_slot, field, value)
    session.add(db_slot)
    session.commit()
    session.refresh(db_slot)
    return db_slot


def delete(session: Session, db_slot: TimeSlot) -> None:
    session.delete(db_slot)
    session.commit()
