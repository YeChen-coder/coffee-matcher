from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Session, select

from app.models.user import User
from app.schemas.users import UserCreate, UserUpdate


def _model_dump(model) -> dict:
    return (
        model.model_dump(exclude_unset=True)
        if hasattr(model, "model_dump")
        else model.dict(exclude_unset=True)
    )


def get(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_by_email(session: Session, email: EmailStr) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_multi(session: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
    statement = select(User).offset(skip).limit(limit)
    return list(session.exec(statement))


def create(session: Session, user_in: UserCreate) -> User:
    user = User(**_model_dump(user_in))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update(session: Session, db_user: User, user_in: UserUpdate) -> User:
    update_data = _model_dump(user_in)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete(session: Session, db_user: User) -> None:
    session.delete(db_user)
    session.commit()
