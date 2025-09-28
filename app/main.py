from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import init_db


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"


def create_application() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        yield

    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.include_router(api_router, prefix=settings.api_v1_str)

    if STATIC_DIR.exists():
        application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

        @application.get("/", include_in_schema=False)
        async def serve_index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html")
    else:

        @application.get("/", include_in_schema=False)
        async def healthcheck() -> dict[str, str]:
            return {"message": f"{settings.app_name} is running"}

    return application


app = create_application()
