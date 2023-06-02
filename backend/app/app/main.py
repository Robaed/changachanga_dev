import logging
import os
import sys
from functools import lru_cache
from logging import config as logging_config
from pathlib import Path

import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.session import engine_aio


@lru_cache()
def get_logger() -> logging.Logger:
    logging_file_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), "logging.conf"
    )
    logging_config.fileConfig(logging_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    azure_logger = logging.getLogger("azure")
    azure_logger.setLevel(logging.ERROR)

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    azure_logger.addHandler(handler)
    logger.addHandler(handler)

    return logger


# Setup logging
logger = get_logger()

BASE_DIR = Path(__file__).resolve().parent

if settings.SENTRY_DSN is not None:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=settings.environment
    )

app = FastAPI(**settings.fastapi_kwargs)

app.include_router(api_router, prefix=settings.API_V1_STR)

if settings.BACKEND_CORS_ORIGIN:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health", tags=["health"])
async def health():
    return "OK"


@app.on_event("shutdown")
async def shutdown():
    await engine_aio.dispose()
