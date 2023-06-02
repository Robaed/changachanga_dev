import re
from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import validator


class InviteStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ChannelInviteCreate(BaseModel):
    phone_numbers: List[str] | None

    @validator("phone_numbers", pre=True)
    def validate_phone_numbers(cls, v: List[str] | None = None):
        if v is None: return v
        pattern = re.compile(r'^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$')
        res = []
        while True:
            try:
                i = v.pop()
            except IndexError:
                break
            i = i.strip()
            pattern_match = pattern.match(i)
            if pattern_match is None:
                raise ValueError("Value must be a valid phone number")
            res.append(i)
        return res


class ChannelInviteIn(BaseModel):
    channel_id: str
    phone_number: str
    invite_status: InviteStatus
    created_by: str
    last_edited_by: str

    class Config:
        orm_mode = True
        use_enum_values = True


class ChannelInviteOut(BaseModel):
    id: str
    channel_id: str
    phone_number: str
    invite_code: str
    invite_status: InviteStatus

    class Config:
        orm_mode = True
        use_enum_values = True


# Shared properties
class ChannelBase(BaseModel):
    description: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None


# Properties to receive on item creation
class UserChannelCreate(BaseModel):
    name: str
    description: str


class ChannelCreate(ChannelBase):
    description: str
    name: str


# Properties to receive on item update
class ChannelUpdate(ChannelBase):
    pass


# Properties to return to client


class Channel(BaseModel):
    channel_no: str
    running_balance: float
    link: str = None
    code: str
    video_url: str = None
    image_url: str = None
    description: str
    title: str
    account_no: str

    class Config:
        orm_mode = True


class InviteCode(BaseModel):
    invite_code: str
