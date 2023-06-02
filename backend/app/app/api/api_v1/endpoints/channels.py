import logging
import os
import tempfile
import uuid
from typing import Any
from typing import List

from fastapi import APIRouter, Depends
from fastapi import HTTPException, UploadFile, Form
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.accounts
import app.schemas.channel
from app import models, schemas
from app import services
from app.api import deps
from app.providers import payment_lib
from app.schemas import channel_users
from app.schemas.payments import PaymentMethods, ContributionRequest

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("", response_model=schemas.Channel)
async def create_channel(
        *,
        db: AsyncSession = Depends(deps.get_db),
        channel_name: str = Form(),
        channel_description: str = Form(),
        current_user: app.models.User = Depends(deps.get_verified_user),
        video: UploadFile | None = None,
        image: UploadFile,
        s3_uploader=Depends(deps.get_s3_uploader)
) -> Any:
    try:
        service_account = await services.user.get_service_account_by_account_no(
            user=current_user,
            db=db
        )
        if service_account is None:
            raise HTTPException(status_code=404, detail="Service Account Not found")

        user_is_owner = await db.execute(
            select(app.models.UserAccountMembership).where(
                app.models.UserAccountMembership.user_id == current_user.user_id
            ).where(app.models.UserAccountMembership.account_id == service_account.account_id)
            .where(app.models.UserAccountMembership.is_owner == True)
        )
        if user_is_owner.scalars().first() is None:
            raise HTTPException(status_code=401, detail="Cannot Create Channels on this account")
        video_url = None
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = tempfile.mktemp(dir=temp_dir)
            with open(file_path, "wb") as f:
                f.write(image.file.read())
            with open(file_path, 'rb') as f:
                file_ext = os.path.splitext(image.filename)[1]
                image_fname = f"assets/images/{uuid.uuid4()}{file_ext}"
                image_s3_url = await s3_uploader.save_file_async(f, image_fname)
                image_s3_url = image_s3_url
                if not image_s3_url:
                    raise HTTPException(status_code=500, detail="Failed to upload files to S3")
            if video is not None:
                video_path = tempfile.mktemp(dir=temp_dir)
                with open(video_path, "wb") as f:
                    f.write(video.file.read())
                with open(video_path, 'rb') as f:
                    # Upload the video to S3 bucket
                    video_ext = os.path.splitext(video.filename)[1]
                    video_filename = f"assets/videos/{uuid.uuid4()}{video_ext}"
                    video_s3_url = await s3_uploader.save_file_async(f, video_filename)
                    if not video_s3_url:
                        raise HTTPException(status_code=500, detail="Failed to upload video to S3")
            else:
                video_s3_url = None

        channel = app.models.Channel(
            video_url=video_s3_url,
            image_url=image_s3_url,
            description=channel_description,
            title=service_account.kyc_profile.full_name,
            account_no=current_user.account_no,
            account=service_account,
            created_by=current_user.user_id,
            name=channel_name
        )
        db.add(channel)
        await db.commit()
        await db.refresh(channel)  # Add current user as a participant and owner
        participant = models.ChannelParticipants(
            user_id=current_user.user_id,
            channel_id=channel.id,
            is_admin=True
        )
        db.add(participant)
        await db.commit()
        return channel
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error("Encountered exception %s when trying to create channel for user %s" % (exc, current_user.user_id))
        raise HTTPException(status_code=500, detail="Failed to create channel")
    finally:
        await db.flush()


@router.get("", response_model=List[schemas.Channel])
async def list_channels(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: app.models.User = Depends(deps.get_verified_user),
) -> Any:
    """
    Retrieve items.
    """
    if services.user.is_superuser(current_user):
        items = await services.channel.get_multi(db, skip=skip, limit=limit)
    else:
        items = await services.channel.get_my_channels(
            db=db, owner_account_no=current_user.user_id, skip=skip, limit=limit
        )
    return items


@router.get("/{channel_no}", response_model=channel_users.ChannelData)
async def read_channel(
        *,
        db: AsyncSession = Depends(deps.get_db),
        channel: app.models.Channel = Depends(deps.participant_get_channel),
        current_user: app.models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    return channel


@router.get("/{channel_no}/participants", response_model=List[channel_users.ChannelParticipant])
async def list_channels_participants(
        channel: app.models.Channel = Depends(deps.participant_get_channel),
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    participants = channel.participants
    return participants


@router.post("/{channel_no}/invite-participant", response_model=List[schemas.ChannelInviteOut])
async def invite_channel_participant(
        data: schemas.ChannelInviteCreate,
        db: AsyncSession = Depends(deps.get_db),
        current_user: app.models.User = Depends(deps.get_current_active_user),
        channel: app.models.Channel = Depends(deps.admin_get_channel),
        sms_app=Depends(deps.get_sms_app)
) -> Any:
    """
    Retrieve items.
    """
    res = await services.channel.create_channel_invites(db=db, user=current_user, data_in=data, db_obj=channel)
    await services.channel.send_invites_to_users(db=db, invites=res, sms_app=sms_app, channel_obj=channel)
    for r in res:
        await db.refresh(r)
    return res


@router.get("/{channel_no}/invites", response_model=List[schemas.ChannelInviteOut])
async def get_channel_invites(
        channel: app.models.Channel = Depends(deps.admin_get_channel),
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    # Extract the invites from the channel object
    invites = channel.channel_invites
    return invites


@router.post("/join-channel", response_model=List[schemas.Channel])
async def join_channel(
        invite_data: app.schemas.channel.InviteCode,
        db: AsyncSession = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    try:
        # Get the channel invite by the invite code
        invite_query = await db.execute(
            select(models.ChannelInvite).where(models.ChannelInvite.invite_code == invite_data.invite_code)
        )
        invite: models.ChannelInvite = invite_query.scalar()

        if invite is None:
            raise HTTPException(status_code=404, detail="Invite not found")

        # Check if the user is already a participant of the channel
        existing_participant_query = await db.execute(
            select(models.ChannelParticipants).where(
                models.ChannelParticipants.user_id == current_user.user_id,
                models.ChannelParticipants.channel_id == invite.channel_id
            )
        )
        existing_participant = existing_participant_query.scalar()

        if existing_participant is not None:
            raise HTTPException(status_code=400, detail="User is already a participant of the channel")

        # Create a new channel participant entry for the user
        invite.invite_status = schemas.InviteStatus.ACCEPTED.value
        new_participant = models.ChannelParticipants(
            user_id=current_user.user_id,
            channel_id=invite.channel_id,
            is_admin=False
        )
        db.add(invite)

        db.add(new_participant)
        await db.commit()

        # Retrieve the updated list of channels for the user
        user_channels = await services.channel.get_my_channels(db=db, user_id=current_user.user_id)

        return user_channels
    except Exception as exc:
        logger.error("Encountered exceptions %s while accepting user invite" % exc)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Unable to send user invite")
    finally:
        await db.flush()


@router.post("/{channel_no}/contribute")
async def contribute_to_channel(
        data_in: ContributionRequest,
        current_user: models.User = Depends(deps.get_current_active_user),
        channel: models.Channel = Depends(deps.participant_get_channel),
        payment_gateway: payment_lib.PaymentGatewayClient = Depends(deps.get_payment_gateway),
        db: AsyncSession = Depends(deps.get_db)
):
    try:
        payment_requests = app.models.PaymentRequest(
            request_status=schemas.PaymentRequestStatuses.INITIATED.value,
            payment_method=data_in.payment_method.value,
            request_payload=data_in.json(),
            channel_id=channel.id,
            user_id=current_user.user_id
        )
        db.add(payment_requests)
        await db.commit()
        await db.refresh(payment_requests)
        result = await payment_gateway.make_payment(request_id=payment_requests.request_id, req=data_in)
        payment_requests.payment_request_result = result.json()
        db.add(payment_requests)
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Could not complete payment %s" % exc)
    finally:
        await db.flush()

    return payment_requests


# @router.put("/{id}", response_model=schemas.Item)
# def update_channel(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     item_in: schemas.ChannelUpdate,
#     current_user: app.models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Update an item.
#     """
#     item = services.channel.get(db=db, id=id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not services.user.is_superuser(current_user) and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     item = services.channel.update(db=db, db_obj=item, obj_in=item_in)
#     return item


# @router.delete("/{id}", response_model=schemas.Item)
# def delete_channel(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     current_user: app.models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Delete an item.
#     """
#     item = services.channel.get(db=db, id=id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if not services.user.is_superuser(current_user) and (item.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     item = services.channel.remove(db=db, id=id)
#     return item
