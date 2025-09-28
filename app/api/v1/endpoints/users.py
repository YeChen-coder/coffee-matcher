from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db
from app.crud import users as users_crud
from app.schemas import users as user_schemas

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[user_schemas.UserRead])
def read_users(
    *,
    session: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[user_schemas.UserRead]:
    return users_crud.get_multi(session, skip=skip, limit=limit)


@router.post(
    "/", response_model=user_schemas.UserRead, status_code=status.HTTP_201_CREATED
)
def create_user(
    *, session: Session = Depends(get_db), user_in: user_schemas.UserCreate
) -> user_schemas.UserRead:
    existing = users_crud.get_by_email(session, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return users_crud.create(session, user_in=user_in)


@router.get("/{user_id}", response_model=user_schemas.UserRead)
def read_user(
    *, session: Session = Depends(get_db), user_id: int
) -> user_schemas.UserRead:
    user = users_crud.get(session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=user_schemas.UserRead)
def update_user(
    *, session: Session = Depends(get_db), user_id: int, user_in: user_schemas.UserUpdate
) -> user_schemas.UserRead:
    user = users_crud.get(session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return users_crud.update(session, db_user=user, user_in=user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(*, session: Session = Depends(get_db), user_id: int) -> None:
    user = users_crud.get(session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    users_crud.delete(session, db_user=user)
