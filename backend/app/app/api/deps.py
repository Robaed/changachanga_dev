from typing import Generator

import jwt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as http_status

import app.models.accounts
from app import services
from app.core import security
from app.core.config import settings, SmsProviders, KycProviders
from app.db.session import async_session
from app.providers.file_uploders import S3FileUploader
from app.providers.kyc_providers import KycProviderBase, IprsKycProvider, MockKycProvider
from app.providers.messaging_provider import MockSmsProvider, SmsProvider, AfrikasTalkingSms, WhatsAppProvider, \
    BongaSmsProvider
from app.providers.payment_lib import KcbPaymentGatewayClient, PaymentGatewayClient
from app.schemas import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_sms_app() -> SmsProvider:
    if settings.SMS_PROVIDER == SmsProviders.AT:
        provider = AfrikasTalkingSms.GET_INSTANCE()
    elif settings.SMS_PROVIDER == SmsProviders.WA:
        provider = WhatsAppProvider.GET_INSTANCE()
    elif settings.SMS_PROVIDER == SmsProviders.BONGA:
        provider = BongaSmsProvider.GET_INSTANCE()
    else:
        provider = MockSmsProvider()
    return provider


async def get_kyc_app() -> KycProviderBase:
    if settings.KYC_PROVIDER == KycProviders.IPRS:
        return IprsKycProvider.GET_INSTANCE()
    return MockKycProvider()


async def get_db() -> Generator:
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


async def get_current_user(
        db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> app.models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        # The token has expired
        raise jwt.InvalidTokenError('Token has expired')
    except (jwt.DecodeError, jwt.InvalidTokenError, ValidationError):
        # The token is invalid
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await services.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
        current_user: app.models.User = Depends(get_current_user),
) -> app.models.User:
    if not await services.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_verified_user(
        current_user: app.models.User = Depends(get_current_user),
        db=Depends(get_db)
) -> app.models.User:
    if not await services.user.is_verified(user=current_user, db=db):
        raise HTTPException(status_code=400, detail="User is not verified")
    return current_user


async def get_current_active_superuser(
        current_user: app.models.User = Depends(get_current_user),
) -> app.models.User:
    if not await services.user.is_superuser(user=current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_channel(channel_no: str, db: AsyncSession = Depends(get_db)) -> app.models.Channel:
    channel = await services.channel.get_channel_by_no(db=db, channel_no=channel_no)
    if not channel:
        # Handle the case when the channel is not found
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


async def participant_get_channel(channel: app.models.Channel = Depends(get_channel),
                                  db: AsyncSession = Depends(get_db),
                                  current_user=Depends(get_current_active_user)) -> app.models.Channel:
    is_admin = await services.user.is_superuser(current_user)
    is_participant = await services.channel.has_participant(db=db, user=current_user, channel=channel)
    if not (is_admin or is_participant):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return channel


async def admin_get_channel(channel: app.models.Channel = Depends(participant_get_channel),
                            db: AsyncSession = Depends(get_db),
                            current_user=Depends(get_current_active_user)) -> app.models.Channel:
    is_admin = await services.user.is_superuser(current_user)
    is_channel_admin = await services.channel.user_is_channel_admin(db=db, channel_obj=channel, user=current_user)
    if not (is_admin or is_channel_admin):
        raise HTTPException(403, detail="User us not authorised to perform this function")
    return channel


async def get_s3_uploader() -> S3FileUploader:
    bucket_name: str = settings.S3_BUCKET_NAME
    access_key_id: str = settings.S3_ACCESS_KEY_ID
    secret_access_key: str = settings.S3_SECRET_ACCESS_KEY
    region_name: str = settings.S3_REGION_NAME
    if any(param is None for param in [bucket_name, access_key_id, secret_access_key, region_name]):
        raise HTTPException(status_code=500, detail="Invalid S3 uploader parameters")
    return S3FileUploader(bucket_name, access_key_id, secret_access_key, region_name)


API_KEY_NAME = settings.API_KEY_NAME

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


def validate_api_key(api_key: str):
    return api_key in settings.API_KEY.split(",")


async def get_api_key(
        api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie),
):
    if validate_api_key(api_key_query):
        return api_key_query
    elif validate_api_key(api_key_header):
        return api_key_header
    elif validate_api_key(api_key_cookie):
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


async def get_payment_gateway() -> KcbPaymentGatewayClient:
    client = KcbPaymentGatewayClient.get_instance(client_id=settings.KCB_CLIENT_ID,
                                                  client_secret=settings.KCB_CLIENT_SECRET,
                                                  server_host=settings.SERVER_HOST)
    return client
