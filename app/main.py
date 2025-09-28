from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import init_db


def create_application() -> FastAPI:
    settings = get_settings()
    
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        yield

    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.include_router(api_router, prefix=settings.api_v1_str)
    return application


app = create_application()
