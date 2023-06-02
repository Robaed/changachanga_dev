import os
import typing
from enum import Enum
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import List
import secrets

from pydantic import AnyHttpUrl, validator, PostgresDsn, AnyUrl
from pydantic import BaseSettings, BaseModel


class SmsProviders(Enum):
    AT = "AT"
    MOCK = "MOCK"
    WA = "WA"
    BONGA = "BONGA"


class KycProviders(Enum):
    IPRS = "IPRS"
    MOCK = "MOCK"


class CeleryBeatConfig:
    name: str
    task: str
    schedule: float
    args: tuple

    def to_config(self):
        return {
            'task': self.task,
            'schedule': self.schedule,
            'args': self.args
        }


beats: List[CeleryBeatConfig] = []


class CeleryConfig(BaseModel):
    broker_url: AnyUrl = "redis://localhost:6379"
    result_backend: AnyUrl | None = "redis://localhost:6379"
    timezone: str = 'UTC'
    beat_schedule: dict = {
        beat.name: beat.to_config() for beat in beats
    }
    task_routes: dict = {
        "app.tasks.*": "main-queue"
    }


class AppSettings(BaseSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "ChangaChanga Platform Api"
    version: str = "0.1.0"
    logging_enabled: bool = True
    disable_docs: bool = True

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    VERICATION_CODE_EXPIRE_SECONDS: int = (60 * 10)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = (60 * 24 * 7)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = (60 * 24 * 7 * 2)
    RESET_TOKEN_EXPIRE_HOURS: int = 3
    SERVER_NAME: str

    SENTRY_DSN: typing.Optional[str] = None
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str = ""
    environment: str = "production"
    SERVER_HOST: AnyHttpUrl

    BACKEND_CORS_ORIGIN: typing.List[typing.Union[AnyHttpUrl, str]] = []
    POSTGRES_USER: typing.Optional[str] = None
    POSTGRES_PASSWORD: typing.Optional[str] = None
    POSTGRES_SERVER: typing.Optional[str] = None
    POSTGRES_PORT: typing.Optional[str] = None
    POSTGRES_DB: typing.Optional[str] = None
    SQLALCHEMY_DATABASE_URI: typing.Optional[PostgresDsn] = None
    ASYNC_SQLALCHEMY_DATABASE_URI: typing.Optional[PostgresDsn] = None
    celery: CeleryConfig = CeleryConfig()
    # sms config
    AT_APIKEY: str | None = None
    AT_SHORTCODE: str | None = None
    AT_USERNAME: str | None = None
    SMS_PROVIDER: SmsProviders = SmsProviders.MOCK
    WA_TOKEN: str | None = None
    WA_PRODUCT_ID: str | None = None
    WA_PHONE_ID: str | None = None
    BONGA_SERVICE_ID: str | None = None
    BONGA_CLIENT_ID: str | None = None
    BONGA_KEY: str | None = None
    BONGA_SECRET: str | None = None
    # IPRS config
    IPRS_PASSWORD: str | None
    IPRS_USERNAME: str | None
    KYC_PROVIDER: KycProviders = KycProviders.MOCK
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    S3_BUCKET_NAME: str | None = None
    S3_ACCESS_KEY_ID: str | None
    S3_SECRET_ACCESS_KEY: str | None
    S3_REGION_NAME: str | None
    API_KEY_NAME: str = "apiKey"
    API_KEY: str = secrets.token_urlsafe(32)
    KCB_CLIENT_ID: str
    KCB_CLIENT_SECRET: str


    class Config:
        env_nested_delimiter = "__"
        env_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../../.env"
        )
        case_sensitive = False
        env_file_encoding = "utf-8"

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        """
        This returns a dictionary of the most commonly used keyword arguments when initializing a FastAPI instance
        If `self.disable_docs` is True, the various docs-related arguments are disabled, preventing your spec from being
        published.
        """
        fastapi_kwargs: Dict[str, Any] = {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

        if self.disable_docs:
            fastapi_kwargs.update(
                {"docs_url": None, "openapi_url": None, "redoc_url": None}
            )
        return fastapi_kwargs

    @validator("BACKEND_CORS_ORIGIN", pre=True)
    def assemble_cors_origins(
            cls, v: typing.Union[str, typing.List[str]]
    ) -> typing.Union[typing.List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
            cls, v: typing.Optional[str], values: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB')}",
        )

    @validator("ASYNC_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_sync_db_connection(
            cls, v: typing.Optional[str], values: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB')}",
        )


@lru_cache()
def get_settings() -> AppSettings:
    return AppSettings()


settings = get_settings()
