import random
import re
import time
from datetime import datetime, timedelta
from typing import Optional

import jwt

from app.core.config import settings


def snake2camel(snake: str, start_lower: bool = False) -> str:
    """
    Converts a snake_case string to camelCase.

    The `start_lower` argument determines whether the first letter in the generated camelcase should
    be lowercase (if `start_lower` is True), or capitalized (if `start_lower` is False).
    """
    camel = snake.title()
    camel = re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), camel)
    if start_lower:
        camel = re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), camel)
    return camel


def camel2snake(camel: str) -> str:
    """
    Converts a camelCase string to snake_case.
    """
    snake = re.sub(r"([a-zA-Z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", camel)
    snake = re.sub(r"([a-z0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    return snake.lower()


async def retry_with_backoff(fn, retries=5, backoff_in_seconds=1):
    x = 0
    while True:
        try:
            return await fn()
        except:
            if x == retries:
                raise
            sleep = (backoff_in_seconds * 2 ** x +
                     random.uniform(0, 1))
            time.sleep(sleep)
            x += 1


def generate_password_reset_token(phone_number: str) -> str:
    delta = timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": phone_number}, settings.SECRET_KEY, algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["phone_number"]
    except jwt.JWTError:
        return None
