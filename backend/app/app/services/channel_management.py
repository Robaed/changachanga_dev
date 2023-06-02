from typing import List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import User
from app.models.channels import Channel, ChannelInvite, ChannelParticipants
from app.providers.messaging_provider import SmsProvider
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelInviteCreate, ChannelInviteIn, InviteStatus
from app.services.base import BaseService


class ChannelService(BaseService[Channel, ChannelCreate, ChannelUpdate]):
    async def create_with_owner(
            self, db: AsyncSession, *, obj_in: ChannelCreate, owner_id: int
    ) -> Channel:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_owner(
            self, db: AsyncSession, *, owner_account_no: int, skip: int = 0, limit: int = 100
    ) -> List[Channel]:
        stmt = select(self.model).where(self.model.account_no == owner_account_no).offset(skip).limit(limit)
        results = await db.execute(stmt)
        return results.scalars().unique().all()

    async def get_my_channels(
            self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Channel]:
        stmt = select(self.model).join(ChannelParticipants).where(ChannelParticipants.user_id == user_id)
        results = await db.execute(stmt)
        return results.scalars().unique().all()

    async def user_is_channel_admin(self, db: AsyncSession, channel_obj: Channel, user: User):
        query = select(Channel).join(ChannelParticipants).where(
            Channel.channel_no == channel_obj.channel_no,
            ChannelParticipants.is_admin == True,
            ChannelParticipants.user_id == user.user_id
        )
        result = await db.execute(query)
        return result.scalar() is not None

    async def get_channel_by_no(self, db: AsyncSession, channel_no: str) -> Channel:
        channel_query = await db.execute(
            select(self.model).where(
                self.model.channel_no == channel_no
            )
        )
        return channel_query.scalar()

    async def create_channel_invites(self, db: AsyncSession, db_obj: Channel, data_in: ChannelInviteCreate, user: User):
        invites = [
            ChannelInvite(
                **ChannelInviteIn(channel_id=db_obj.id,
                                  phone_number=phone_number,
                                  invite_status=InviteStatus.PENDING,
                                  created_by=user.user_id,
                                  last_edited_by=user.user_id).dict()
            ) for phone_number in data_in.phone_numbers
        ]
        res = []
        try:
            while True:
                try:
                    invite = invites.pop()
                except IndexError as exc:
                    break
                invite.channel = db_obj
                db.add(invite)
                # await db.refresh(invite)
                res.append(invite)
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Duplicate invite code detected.")
        finally:
            await db.flush()
        return res

    async def send_invites_to_users(self, db: AsyncSession, sms_app: SmsProvider, channel_obj: Channel,
                                    invites: List[ChannelInvite]):
        for invite in invites:
            try:
                sms_message = f"You are invited to join the {channel_obj.name}." \
                              f" On ChangaChanga. Invitation code: {invite.invite_code}"
                await sms_app.send_sms_async(sms_message, invite.phone_number)

                invite.invite_status = InviteStatus.SENT.value  # Set invite_status to "sent"
                db.add(invite)
                await db.commit()
            except Exception as e:
                await db.rollback()
                self._logger.error(f"Failed to send invite to {invite.phone_number}: {str(e)}")
            finally:
                await db.flush()

        return

    async def has_participant(self, db: AsyncSession, user: User, channel: Channel) -> bool:
        res = user in [p.user for p in channel.participants]
        return res


channel = ChannelService(Channel)
