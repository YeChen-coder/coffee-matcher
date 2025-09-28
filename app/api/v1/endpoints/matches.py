from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db
from app.crud import match_requests as matches_crud
from app.crud import timeslots as timeslots_crud
from app.crud import users as users_crud
from app.crud import venues as venues_crud
from app.schemas import match_requests as match_schemas

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post(
    "/",
    response_model=match_schemas.MatchRequestRead,
    status_code=status.HTTP_201_CREATED,
)
def create_match_request(
    *, session: Session = Depends(get_db), match_in: match_schemas.MatchRequestCreate
) -> match_schemas.MatchRequestRead:
    requester = users_crud.get(session, user_id=match_in.requester_id)
    target = users_crud.get(session, user_id=match_in.target_id)
    if not requester or not target:
        raise HTTPException(status_code=404, detail="Requester or target user not found")

    venue = venues_crud.get(session, venue_id=match_in.venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    if match_in.time_slot_id:
        slot = timeslots_crud.get(session, slot_id=match_in.time_slot_id)
        if not slot or slot.user_id != match_in.target_id:
            raise HTTPException(status_code=400, detail="Invalid time slot for target user")
        if match_in.proposed_time != slot.start_time:
            raise HTTPException(
                status_code=400,
                detail="Proposed time must match the selected time slot start",
            )

    return matches_crud.create(session, match_in=match_in)


@router.get(
    "/received/{user_id}", response_model=List[match_schemas.MatchRequestRead]
)
def read_received_matches(
    *, session: Session = Depends(get_db), user_id: int
) -> List[match_schemas.MatchRequestRead]:
    return matches_crud.get_received(session, user_id=user_id)


@router.get(
    "/sent/{user_id}", response_model=List[match_schemas.MatchRequestRead]
)
def read_sent_matches(
    *, session: Session = Depends(get_db), user_id: int
) -> List[match_schemas.MatchRequestRead]:
    return matches_crud.get_sent(session, user_id=user_id)


@router.put("/{match_id}", response_model=match_schemas.MatchRequestRead)
def update_match_request(
    *, session: Session = Depends(get_db), match_id: int, match_in: match_schemas.MatchRequestUpdate
) -> match_schemas.MatchRequestRead:
    match = matches_crud.get(session, match_id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match request not found")

    if match_in.venue_id:
        venue = venues_crud.get(session, venue_id=match_in.venue_id)
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")

    if match_in.time_slot_id:
        slot = timeslots_crud.get(session, slot_id=match_in.time_slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Time slot not found")
        if match_in.proposed_time and match_in.proposed_time != slot.start_time:
            raise HTTPException(
                status_code=400,
                detail="Proposed time must match the selected time slot start",
            )

    return matches_crud.update(session, db_match=match, match_in=match_in)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match_request(*, session: Session = Depends(get_db), match_id: int) -> None:
    match = matches_crud.get(session, match_id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match request not found")
    matches_crud.delete(session, db_match=match)
