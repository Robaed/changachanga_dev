import json
from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, validator


class ServiceAccountsEnum(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"


class UserKycVerificationUpload(BaseModel):
    id_front: str
    id_back: Optional[str] = None


class KycVerificationState(Enum):
    queued = "queued"
    completed = "completed"


class KycVerificationStatus(Enum):
    PENDING = "PENDING"
    SUCEEDED = "SUCEEDED"
    FAILED = "FAILED"


class KycVerificationResponse(BaseModel):
    request_id: str
    status: KycVerificationStatus
    state: KycVerificationState
    status_reason: Optional[str] = None

    class Config:
        use_enum_values = True


class UserKycData(BaseModel):
    surname: str | None = None
    serial_no: str | None = None
    photo: str | None = None
    other_name: str | None = None
    id_number: str | None = None
    gender: str | None = None
    first_name: str | None = None
    family: str | None = None
    dob: str | None = None
    citizenship: str | None = None
    valid: bool


class UserKycVerificationProviderResult(BaseModel):
    success: bool
    payload: Optional[UserKycData] = None
    errors: Any | None


class AccountKycVerificationStatusModel(BaseModel):
    verification_response: Optional[dict | str]
    state: KycVerificationState
    request_status: KycVerificationStatus
    status_reason: Optional[Any]
    upload_data: Optional[Any]

    class Config:
        orm_mode = True
        use_enum_values = True

    @validator("verification_response", pre=True)
    def unpack_verification_response(cls, v):
        if v is None:
            return v
        try:
            v = json.loads(v)
        except Exception as exc:
            pass
        return v

    @validator("upload_data", pre=True)
    def unpack_upload_data(cls, v):
        if v is None:
            return v
        try:
            v = json.loads(v)
        except Exception as exc:
            pass
        return v

    @validator("status_reason", pre=True)
    def unpack_status_reason(cls, v):
        if v is None:
            return v
        try:
            v = json.loads(v)
        except Exception as exc:
            pass
        return v


