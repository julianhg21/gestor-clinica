from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.db import close_pool, open_pool


def create_app(title: str, version: str = "1.0.0") -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        open_pool()
        yield
        close_pool()

    app = FastAPI(title=title, version=version, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
