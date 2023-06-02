from typing import Generic, TypeVar
from typing import Optional

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T", bound=BaseModel)


class Token(GenericModel, Generic[T]):
    access_token: str
    token_type: str
    data: T | None = None

    @classmethod
    def bearer_token(cls, token: str):
        return cls(token_type="bearer", access_token=token)


class TokenPayload(BaseModel):
    sub: Optional[str] = None
