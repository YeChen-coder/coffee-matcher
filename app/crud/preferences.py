from typing import List, Optional

from sqlmodel import Session, select

from app.models.user_preference import UserPreference
from app.schemas.preferences import PreferenceCreate, PreferenceUpdate


def _model_dump(model) -> dict:
    return (
        model.model_dump(exclude_unset=True)
        if hasattr(model, "model_dump")
        else model.dict(exclude_unset=True)
    )


def get(session: Session, preference_id: int) -> Optional[UserPreference]:
    return session.get(UserPreference, preference_id)


def get_by_user(session: Session, user_id: int) -> List[UserPreference]:
    statement = select(UserPreference).where(UserPreference.user_id == user_id)
    return list(session.exec(statement))


def create(session: Session, preference_in: PreferenceCreate) -> UserPreference:
    preference = UserPreference(**_model_dump(preference_in))
    session.add(preference)
    session.commit()
    session.refresh(preference)
    return preference


def update(session: Session, db_preference: UserPreference, preference_in: PreferenceUpdate) -> UserPreference:
    update_data = _model_dump(preference_in)
    for field, value in update_data.items():
        setattr(db_preference, field, value)
    session.add(db_preference)
    session.commit()
    session.refresh(db_preference)
    return db_preference


def delete(session: Session, db_preference: UserPreference) -> None:
    session.delete(db_preference)
    session.commit()
