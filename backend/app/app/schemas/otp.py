from enum import Enum

from pydantic import BaseModel


class OtpVerificationStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class OtpVerificationResponse(BaseModel):
    status: int
    message: OtpVerificationStatus
    detail: str

    class Config:
        use_enum_values = True


class Otp(BaseModel):
    otp: str
    phone_number: str
