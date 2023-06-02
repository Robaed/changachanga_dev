import datetime
import uuid
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app import schemas
from app.core.security import get_password_hash_async, verify_password, create_random_code, get_password_hash
from app.models import User, UserActivationStatus, AccountKycVerificationStatus, ServiceAccount, UserLoginInfo, \
    AccountKycProfile, Address
from app.providers.kyc_providers import KycProviderBase
from app.providers.messaging_provider import SmsProvider
from app.schemas import ActivationStatuses
from app.schemas.user import UserCreate, UserUpdate, UserAccountCreate
from app.services.base import BaseService


class InvalidOtpError(Exception): pass


class UserManagementService(BaseService[User, UserCreate, UserUpdate]):
    def get_by_phonenumber(self, db: Session, *, phone_number: str) -> Optional[User]:
        user = db.query(User).filter_by(username=phone_number).first()
        return user

    async def get_by_phonenumber_async(self, db: AsyncSession, *, phone_number: str) -> Optional[User]:
        stmt = select(User).where(User.username == phone_number)
        res = await db.execute(stmt)
        user = res.scalars().first()
        return user

    async def get_by_user_no(self, db: AsyncSession, *, user_no: str) -> Optional[User]:
        stmt = select(User).where(User.user_no == user_no)
        res = await db.execute(stmt)
        user = res.scalar()
        return user

    async def create_async(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            created_by="SYS_ADMIN",
            last_edited_by="SYS_ADMIN",
            user_role=1,
            username=obj_in.get_username()
        )
        hashed_password = await get_password_hash_async(obj_in.password)
        login_info = UserLoginInfo(
            hashed_password=hashed_password,
            phone_number=obj_in.get_username(),
            email_address=obj_in.email_address,
            verification_status=1,
            created_by="SYS_ADMIN",
            last_edited_by="SYS_ADMIN",
        )
        db_obj.login_info = login_info
        db.add(db_obj)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise
        finally:
            await db.flush()
        await db.refresh(db_obj)
        return db_obj

    def add_super_user(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            created_by="SYS_ADMIN",
            last_edited_by="SYS_ADMIN",
            user_role=10,
            user_account_status=2,
            username=obj_in.get_username(),
        )
        hashed_password = get_password_hash(obj_in.password)
        login_info = UserLoginInfo(
            hashed_password=hashed_password,
            phone_number=obj_in.get_username(),
            email_address=obj_in.email_address,
            verification_status=2,
            created_by="SYS_ADMIN",
            last_edited_by="SYS_ADMIN",
        )
        db_obj.login_info = login_info
        db.add(db_obj)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise
        finally:
            db.flush()
        db.refresh(db_obj)
        return db_obj

    async def is_verified(self, db: AsyncSession, user: User) -> bool:
        service_account = await self.get_service_account_by_account_no(db=db, user=user)
        return service_account.verification_status == 2

    async def get(self, db: AsyncSession, id: Any) -> Optional[User]:
        query = select(User).filter_by(user_id=id).options(
            selectinload(User.account_membership)
        )
        res = await db.execute(query)
        return res.scalar()

    async def verify_user_kyc(self, db: AsyncSession, user: User, obj_in: UserAccountCreate,
                              kyc_app: KycProviderBase) -> AccountKycVerificationStatus:
        service_account: ServiceAccount = await self.get_service_account_by_account_no(
            db=db,
            user=user
        )
        if service_account is None:
            raise Exception("Complete registration process to validate your KYC documents")
        if service_account.verification_status == 2:
            raise Exception("Account Already Verified")

        address: Address = service_account.address or Address()
        kyc_profile: AccountKycProfile = service_account.kyc_profile or AccountKycProfile()
        address.country = obj_in.address.country
        address.address_line = obj_in.address.address_line
        address.city = obj_in.address.city
        address.created_by = user.user_id
        address.last_edited_by = user.user_id
        service_account.address = address
        kyc_profile.full_name = obj_in.full_name
        kyc_profile.date_of_birth = obj_in.date_of_birth
        kyc_profile.id_document_type = obj_in.id_document_type
        kyc_profile.nationality = obj_in.nationality
        kyc_profile.gender = obj_in.gender
        kyc_profile.id_number = obj_in.id_number
        kyc_profile.created_by = user.user_id
        kyc_profile.last_edited_by = user.user_id
        try:
            kyc_verification_result = await kyc_app.verify_user_kyc(
                first_name=obj_in.full_name.split()[0],
                last_name=obj_in.full_name.split()[-1],
                id_number=obj_in.id_number
            )
            kyc_verification_status = AccountKycVerificationStatus(
                id=str(uuid.uuid4()),
                state=schemas.KycVerificationState.queued.value,
                request_status=schemas.KycVerificationStatus.PENDING.value,
                status_reason="Queued for processing",
                last_edited_by=user.user_id,
                created_by=user.user_id,
                upload_data=obj_in.json()
            )
            kyc_verification_status.verification_response = kyc_verification_result.json()
            service_account.verification_status_id = kyc_verification_status.id
            service_account.verified_date_utc = datetime.datetime.utcnow()
            service_account.address = address
            if kyc_verification_result.success:
                kyc_verification_status.request_status = schemas.KycVerificationStatus.SUCEEDED.value
                kyc_verification_status.status_reason = "Verified"
                service_account.kyc_profile = kyc_profile
                service_account.verification_status = 2
            else:
                service_account.verification_status = 3
                kyc_verification_status.request_status = schemas.KycVerificationStatus.FAILED.value
                kyc_verification_status.status_reason = kyc_verification_result.errors
            kyc_verification_status.state = schemas.KycVerificationState.completed.value
            service_account.verification_statuses.append(kyc_verification_status)
            db.add(service_account)
            db.add(user)
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise
        finally:
            await db.flush()
        await db.refresh(kyc_verification_status)
        return kyc_verification_status

    async def update(
            self, session: AsyncSession, *, db_obj: User,
            obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash_async(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(session, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, phone_number: str, password: str) -> \
            Optional[User]:
        user = await self.get_by_phonenumber_async(db, phone_number=phone_number)
        if not user:
            return None
        password_verified = await verify_password(password, user.login_info.hashed_password)
        if not password_verified:
            return None
        return user

    async def get_service_account_by_account_no(self, db: AsyncSession, user: User) -> ServiceAccount:
        account_query = await db.execute(
            select(ServiceAccount).where(ServiceAccount.account_no == user.account_no)
        )
        service_account = account_query.scalars().first()
        return service_account

    async def is_active(self, user: User) -> bool:
        return user.user_account_status > 1

    async def is_superuser(self, user: User) -> bool:
        return user.user_role == 10

    async def send_activation_code(self, db: AsyncSession, user: User, sms_app: SmsProvider,
                                   expiry_in_seconds: int = 10):
        activation_status = UserActivationStatus(
            user_id=user.user_id,
            expiry_time=datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry_in_seconds),
            created_by=user.user_id,
            last_edited_by=user.user_id
        )
        db.add(activation_status)
        await db.commit()
        await db.refresh(activation_status)
        await sms_app.send_sms_async(
            "%s is your verification code for Changachanga" % activation_status.activation_code,
            phone_number=user.username)
        return user

    async def activate_user(self, db: AsyncSession, activation_code: int, user: User) -> Optional[UserActivationStatus]:
        if user.user_account_status > 1:
            raise HTTPException("User account is active")
        stmt = select(UserActivationStatus).where(UserActivationStatus.activation_code == activation_code)
        result = await db.execute(stmt)
        activation_status: UserActivationStatus = result.scalars().first()
        sa_query = await db.execute(select(ServiceAccount).where(ServiceAccount.account_no == user.account_no))
        service_account: ServiceAccount = sa_query.scalars().first()
        if service_account is None:
            service_account = ServiceAccount(account_name=user.username,
                                             account_no=user.account_no,
                                             account_type='INDIVIDUAL',
                                             created_by=user.user_id,
                                             last_edited_by=user.user_id)
            user.accounts.append(service_account)

        if activation_status is None:
            return None
        if ActivationStatuses(activation_status.status) != ActivationStatuses.INITIATED:
            return None
        elif activation_status.expiry_time < datetime.datetime.utcnow():
            status_result = ActivationStatuses.EXPIRED
        elif ActivationStatuses(activation_status.status) != ActivationStatuses.INITIATED:
            status_result = ActivationStatuses(activation_status.status)
        else:
            user.user_account_status = 2
            user.login_info.verification_status = 2
            status_result = ActivationStatuses.SUCCEEDED
        activation_status.status = status_result.value
        activation_status.last_edited_date_utc = datetime.datetime.utcnow()
        activation_status.last_edited_by = user.user_id
        activation_status.last_edited_date_utc = datetime.datetime.utcnow()
        db.add(user)
        db.add(activation_status)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise
        finally:
            await db.flush()
        await db.refresh(activation_status)
        return activation_status

    async def send_otp(self, db: AsyncSession, user: User, sms_app: SmsProvider):
        otp = await create_random_code(6)
        login_info = user.login_info
        hashed_phone_verification = await get_password_hash_async(otp)
        login_info.otp_hash = hashed_phone_verification
        db.add(login_info)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc
        finally:
            await db.flush()
        await sms_app.send_sms_async("%s is your verification code for Changachanga" % otp,
                                     phone_number=login_info.phone_number)
        return user

    async def verify_otp(self, db: AsyncSession, user: User, otp: str):
        login_info = user.login_info
        if login_info.verify_otp(otp):
            login_info.otp_hash = None
            db.add(login_info)
            try:
                await db.commit()
            except Exception as exc:
                await db.rollback()
                raise exc
            finally:
                await db.flush()
            return True
        return False



user = UserManagementService(User)
