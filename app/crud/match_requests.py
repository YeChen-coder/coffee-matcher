from typing import List, Optional

from sqlmodel import Session, select

from app.models.match_request import MatchRequest
from app.schemas.match_requests import MatchRequestCreate, MatchRequestUpdate


def _model_dump(model) -> dict:
    return (
        model.model_dump(exclude_unset=True)
        if hasattr(model, "model_dump")
        else model.dict(exclude_unset=True)
    )


def get(session: Session, match_id: int) -> Optional[MatchRequest]:
    return session.get(MatchRequest, match_id)


def get_received(session: Session, user_id: int) -> List[MatchRequest]:
    statement = select(MatchRequest).where(MatchRequest.target_id == user_id)
    return list(session.exec(statement))


def get_sent(session: Session, user_id: int) -> List[MatchRequest]:
    statement = select(MatchRequest).where(MatchRequest.requester_id == user_id)
    return list(session.exec(statement))


def create(session: Session, match_in: MatchRequestCreate) -> MatchRequest:
    match = MatchRequest(**_model_dump(match_in))
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def update(session: Session, db_match: MatchRequest, match_in: MatchRequestUpdate) -> MatchRequest:
    update_data = _model_dump(match_in)
    for field, value in update_data.items():
        setattr(db_match, field, value)
    session.add(db_match)
    session.commit()
    session.refresh(db_match)
    return db_match


def delete(session: Session, db_match: MatchRequest) -> None:
    session.delete(db_match)
    session.commit()
