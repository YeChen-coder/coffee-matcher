from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db
from app.crud import preferences as preferences_crud
from app.crud import users as users_crud
from app.schemas import preferences as preference_schemas

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/{user_id}", response_model=List[preference_schemas.PreferenceRead])
def read_preferences(
    *, session: Session = Depends(get_db), user_id: int
) -> List[preference_schemas.PreferenceRead]:
    return preferences_crud.get_by_user(session, user_id=user_id)


@router.post(
    "/",
    response_model=preference_schemas.PreferenceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_preference(
    *, session: Session = Depends(get_db), preference_in: preference_schemas.PreferenceCreate
) -> preference_schemas.PreferenceRead:
    user = users_crud.get(session, user_id=preference_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return preferences_crud.create(session, preference_in=preference_in)


@router.put("/{preference_id}", response_model=preference_schemas.PreferenceRead)
def update_preference(
    *,
    session: Session = Depends(get_db),
    preference_id: int,
    preference_in: preference_schemas.PreferenceUpdate,
) -> preference_schemas.PreferenceRead:
    preference = preferences_crud.get(session, preference_id=preference_id)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    return preferences_crud.update(
        session, db_preference=preference, preference_in=preference_in
    )


@router.delete("/{preference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(*, session: Session = Depends(get_db), preference_id: int) -> None:
    preference = preferences_crud.get(session, preference_id=preference_id)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    preferences_crud.delete(session, db_preference=preference)
