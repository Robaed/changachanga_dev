from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T", bound=BaseModel)


class ActivationStatuses(Enum):
    INITIATED = 'INITIATED'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    EXPIRED = 'EXPIRED'


class PhoneVerificationCode(BaseModel):
    phone_number: str
    verification_code: str


class PhoneVerificationRequest(BaseModel):
    phone_number: str


class UserActivationResult(GenericModel, Generic[T]):
    status: ActivationStatuses
    data: T | None = None
