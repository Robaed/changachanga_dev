import re
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Any

import pydantic
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.ext.associationproxy import _AssociationList

from app.schemas.base_schemas import AuditColumnsCreate


class UserIdentityDocuments(Enum):
    NATIONAL_ID = "NATIONAL_ID"
    PASSPORT = "PASSPORT"


class AccountType(Enum):
    BUSINESS = 'BUSINESS'
    INDIVIDUAL = 'INDIVIDUAL'


class AccountInfo(BaseModel):
    account_type: AccountType


# address details
class UserAddressInDB(BaseModel):
    address_line: Optional[str]
    postal_code: Optional[str]
    city: Optional[str] = None
    country: str


class AddressCreate(UserAddressInDB):
    address_line: str
    postal_code: str
    city: Optional[str] = None


# KYC properties of a user
class UserKyc(BaseModel):
    full_name: Optional[str] = None
    id_number: Optional[str] = None
    gender: Optional[str] = None
    id_document_type: Optional[UserIdentityDocuments] = None
    id_date_of_issue: Optional[date] = None
    date_of_birth: Optional[date] = None
    address: UserAddressInDB


# Properties to receive via API for KYC verification
class UserAccountCreate(BaseModel):
    full_name: str
    id_number: str
    nationality: str
    gender: Optional[str] = None
    id_document_type: UserIdentityDocuments
    date_of_birth: date
    address: AddressCreate

    class Config:
        use_enum_values = True


# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    email_address: Optional[EmailStr] = None


# Properties to receive via API on creation
class UserCreate(BaseModel):
    email_address: Optional[EmailStr] = None
    phone_number: str
    password: str
    country_code: str = pydantic.Field(description="Country Phone Number code e.g. +254")

    @property
    def username(self):
        phone_number = self.phone_number.strip()
        country_code = self.country_code
        phone_number = phone_number.strip()
        phone_number = phone_number[(len(phone_number) - 9):]
        phone_number = "%s%s" % (country_code.strip(), phone_number)
        phone_number = phone_number.strip("+")
        return phone_number

    def get_username(self):
        return self.username

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, v: Optional[str], values) -> str:
        pattern = re.compile(r'^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$')
        pattern_match = pattern.match(v)
        if pattern_match is None:
            raise ValueError("Phone Number must start with country code e.g +25412345678")
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    user_no: int
    date_joined_utc: datetime
    account_no: str

    class Config:
        orm_mode = True


class ServiceAccountInDBBase(BaseModel):
    account_name: str
    account_no: str
    account_type: AccountType
    verification_status: int

    class Config:
        orm_mode = True


class Address(BaseModel):
    country: str
    account_id: str
    is_deleted: bool
    address_line: str
    city: str | None = None

    class Config:
        orm_mode = True


class VerificationStatus(BaseModel):
    verification_response: Optional[str]
    status: str
    account_id: str
    upload_data: Optional[str]
    state: str
    request_id: str
    status_reason: str
    id: str
    created_by: str
    last_edited_by: str


class KycProfile(BaseModel):
    full_name: str
    id_date_of_issue: Optional[datetime]
    id_number: str
    id_document_type: UserIdentityDocuments
    date_of_birth: date
    nationality: str
    gender: str | None = None

    class Config:
        orm_mode = True

    @validator("id_number")
    def marshall_id_number(cls, v):
        l_v = [i for i in v]
        n_v = len(v) // 2

        for i in range(n_v, len(v)):
            l_v[i] = "X"
        return "".join(l_v)


class Account(BaseModel):
    account_name: str
    account_type: str
    account_id: str
    account_no: str
    verification_status: int
    verification_status_id: str | None = None
    address: Address | None = None
    kyc_profile: KycProfile | None = None

    class Config:
        orm_mode = True


class AccountMembership(BaseModel):
    is_owner: bool
    account: Account

    class Config:
        orm_mode = True


class User(BaseModel):
    user_no: str
    username: str
    user_account_status: int
    user_id: str
    date_joined_utc: datetime

    class Config:
        orm_mode = True


class UserAccount(User):
    accounts: List[Optional[Account]] = None

    class Config:
        orm_mode = True

    @validator("accounts", pre=True)
    def evaluate_accounts_column(cls, v) -> List[Any]:
        if not isinstance(v, _AssociationList):
            if not isinstance(v, list):
                raise ValueError()
        res = []
        for i in v:
            res.append(i)
        v = res
        return v


# Additional properties stored in DB
class UserInDB(UserInDBBase, UserKyc):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str


class UserLoginInfoInDBBase(BaseModel):
    email_address: str | None = None
    phone_number: str | None
    hashed_password: str | None
    otp_hash: str | None
    is_verified: str | None
    user: str | None


class UserLoginInfoCreate(BaseModel, AuditColumnsCreate):
    email_address: str | None = None
    phone_number: str | None
    password: str
