import math
import random
from datetime import datetime, timedelta
from typing import Any, Union

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


async def create_random_code(length=4):
    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    OTP = ""

    # length of password can be changed
    # by changing value in range
    for i in range(length):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


async def create_access_token(
        subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash_async(password: str) -> str:
    return pwd_context.hash(password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
