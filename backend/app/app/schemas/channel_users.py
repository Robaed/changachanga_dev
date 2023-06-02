from typing import List

from pydantic import BaseModel

from .channel import Channel
from .user import User


class ChannelParticipant(BaseModel):
    user: User
    is_admin: bool

    class Config:
        orm_mode = True


class ChannelData(Channel):
    participants: List[ChannelParticipant]

    class Config:
        orm_mode = True
