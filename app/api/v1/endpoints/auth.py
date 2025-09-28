from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session

from app.api.deps import get_db
from app.crud import users as users_crud
from app.schemas import users as user_schemas


class LoginRequest(BaseModel):
    email: EmailStr


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=user_schemas.UserRead)
def login(*, session: Session = Depends(get_db), payload: LoginRequest) -> user_schemas.UserRead:
    user = users_crud.get_by_email(session, payload.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
