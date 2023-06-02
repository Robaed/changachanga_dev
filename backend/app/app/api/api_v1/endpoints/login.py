from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.accounts
from app import services, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash_async
from app.providers.messaging_provider import SmsProvider

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token[schemas.User])
async def login_access_token(
        db: AsyncSession = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await services.user.authenticate(
        db, phone_number=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    elif not await services.user.is_active(user):
        raise HTTPException(status_code=401, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await security.create_access_token(
        user.user_id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "data": schemas.User.from_orm(user)
    }


@router.post("/login/test-token", response_model=schemas.User)
async def test_token(current_user: app.models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/reset-password", response_model=schemas.Msg)
async def reset_password(phone_number: str = Body(...),
                         otp: str = Body(...),
                         new_password: str = Body(...),
                         db: AsyncSession = Depends(deps.get_db),
                         apiKey: str = Depends(deps.get_api_key),
                         ) -> Any:
    """
    Reset password for a user
    """
    user = await services.user.get_by_phonenumber_async(db=db, phone_number=phone_number)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not await services.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    if not services.user.verify_otp(db=db, user=user, otp=otp):
        raise HTTPException(status_code=400, detail="Invalid token")
    hashed_password = await get_password_hash_async(new_password)
    user.login_info.hashed_password = hashed_password
    db.add(user)
    await db.commit()
    return {"msg": "Password updated successfully"}


@router.post("/send-verification-code", response_model=schemas.OtpVerificationResponse)
async def send_phone_verification_code(data_in: schemas.PhoneVerificationRequest,
                                       db: AsyncSession = Depends(deps.get_db),
                                       apiKey: str = Depends(deps.get_api_key),
                                       sms_app: SmsProvider = Depends(deps.get_sms_app)) -> Any:
    """
    Sends the user phone verification code.
    """

    user = await services.user.get_by_phonenumber_async(db=db, phone_number=data_in.phone_number)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    await services.user.send_activation_code(db=db, user=user, sms_app=sms_app,
                                             expiry_in_seconds=settings.VERICATION_CODE_EXPIRE_SECONDS)
    return schemas.OtpVerificationResponse(
        status=201,
        message=schemas.OtpVerificationStatus.SUCCESS,
        detail="OTP sent to users phone number"
    )


@router.post("/verify-phonenumber", response_model=schemas.UserActivationResult[schemas.Token[schemas.User]])
async def verify_user_phone(data_in: schemas.PhoneVerificationCode,
                            apiKey: str = Depends(deps.get_api_key),
                            db: AsyncSession = Depends(deps.get_db)) -> Any:
    """
    Verify users phone number to mark the user as active
    :param data_in:
    :param db:
    :return:
    """
    user = await services.user.get_by_phonenumber_async(db=db, phone_number=data_in.phone_number)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    try:
        db_obj = await services.user.activate_user(db=db, user=user, activation_code=data_in.verification_code)
        if db_obj is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid Activation Code"
            )
        response = schemas.UserActivationResult(status=db_obj.status)
        if schemas.ActivationStatuses(db_obj.status) == schemas.ActivationStatuses.SUCCEEDED:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = await security.create_access_token(
                user.user_id, expires_delta=access_token_expires
            )
            token = schemas.Token.bearer_token(token=access_token)
            token.data = schemas.User.from_orm(user)
            response.data = token
        else:
            response.status = db_obj.status
            raise HTTPException(
                status_code=400,
                detail=response.dict()
            )
        return response
    except Exception as exc:
        await db.rollback()
        raise
    finally:
        await db.flush()


@router.post("/forget-password", response_model=schemas.OtpVerificationResponse)
async def forget_password(req: schemas.ResetPasswordRequest,
                          db: AsyncSession = Depends(deps.get_db),
                          apiKey: str = Depends(deps.get_api_key),
                          sms_app: SmsProvider = Depends(deps.get_sms_app)) -> Any:
    """
    Sends otp to user via SMS or Email for password reset
    """

    user = await services.user.get_by_phonenumber_async(db=db, phone_number=req.phone_number)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    await services.user.send_otp(db=db, user=user, sms_app=sms_app)
    return schemas.OtpVerificationResponse(
        status=201,
        message=schemas.OtpVerificationStatus.SUCCESS,
        detail="OTP sent to users phone number"
    )
