from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.models
import app.models.accounts
from app import services, schemas
from app.api import deps

router = APIRouter()


@router.get("", response_model=List[schemas.User])
async def read_users(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: app.models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await services.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("", response_model=schemas.User)
async def create_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        api_key: app.models.User = Depends(deps.get_api_key),
        sms_app=Depends(deps.get_sms_app)
) -> Any:
    """
    Create new user.
    """
    user = await services.user.get_by_phonenumber_async(db=db, phone_number=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    try:
        user = await services.user.create_async(db, obj_in=user_in)
        await services.user.send_activation_code(db, user=user, sms_app=sms_app, expiry_in_seconds=60*5)
    except Exception as exc:
        await db.rollback()
        raise
    finally:
        await db.flush()

    return user


@router.put("/me", response_model=schemas.User)
async def update_user_primary_info(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_in: schemas.UserUpdate,
        current_user: app.models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    user = await services.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.UserAccount)
async def read_user(
        db: AsyncSession = Depends(deps.get_db),
        current_user: app.models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/me/kyc", response_model=schemas.KycProfile)
async def get_kyc_details(db: AsyncSession = Depends(deps.get_db),
                          current_user: app.models.User = Depends(deps.get_current_active_user)):
    stmt = select(app.models.AccountKycProfile).join(app.models.ServiceAccount).where(
        app.models.ServiceAccount.account_no == current_user.account_no
    )
    res = await db.execute(stmt)
    kyc_profile = res.scalars().first()
    return kyc_profile


@router.post("/me/upload-kyc", response_model=schemas.AccountKycVerificationStatusModel)
async def upload_users_kyc(
        verification_data: schemas.UserAccountCreate,
        db: AsyncSession = Depends(deps.get_db),
        current_user: app.models.User = Depends(deps.get_current_active_user),
        kyc_app=Depends(deps.get_kyc_app)
) -> Any:
    """
    Upload KYC data
    """
    user = current_user
    try:
        verification_status = await services.user.verify_user_kyc(
            db=db,
            user=current_user,
            obj_in=verification_data,
            kyc_app=kyc_app
        )
    except Exception as exc:
        raise HTTPException(400, detail="Could not validate KYC details %s" % exc)

    return verification_status


@router.get("/{user_id}", response_model=schemas.UserAccount)
async def read_user_by_id(
        user_id: int,
        current_user: app.models.User = Depends(deps.get_current_active_user),
        db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await services.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not await services.user.user_role(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user
