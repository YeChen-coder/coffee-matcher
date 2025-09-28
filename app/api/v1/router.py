from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    matches,
    preferences,
    timeslots,
    users,
    venues,
)

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(timeslots.router)
api_router.include_router(venues.router)
api_router.include_router(matches.router)
api_router.include_router(preferences.router)
api_router.include_router(auth.router)
