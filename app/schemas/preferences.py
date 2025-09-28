from typing import Optional

from sqlmodel import SQLModel


class PreferenceBase(SQLModel):
    user_id: int
    preference_type: str
    preference_value: str
    confidence: int = 1


class PreferenceCreate(PreferenceBase):
    pass


class PreferenceUpdate(SQLModel):
    preference_type: Optional[str] = None
    preference_value: Optional[str] = None
    confidence: Optional[int] = None


class PreferenceRead(PreferenceBase):
    id: int
