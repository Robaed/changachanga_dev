
from sqlalchemy.orm import Session

from app import services, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    user_in = schemas.UserCreate(
        phone_number=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        country_code="254"
    )
    user = services.user.get_by_phonenumber(db, phone_number=user_in.phone_number)
    if not user:
        user_in = schemas.UserCreate(
            phone_number=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            country_code="254"
        )
        user = services.user.add_super_user(db, obj_in=user_in)  # noqa: F841