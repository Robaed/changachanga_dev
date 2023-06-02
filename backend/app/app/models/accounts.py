from datetime import datetime
from typing import List
from typing import Optional

from sqlalchemy import ForeignKey, event
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.base import Connection
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship, mapped_column

from app.db.base_class import Base, AuditColumns, generate_unique_str, AutoIdColumns, generate_random_sequence, \
    number_id_generator

__all__ = ['ServiceAccount', "AccountKycVerificationStatus", "PaymentAccount", "User",
           "kyc_verification_status_before_insert", "user_before_insert", "service_account_before_insert",
           "UserActivationStatus", "user_activation_status_before_insert", 'UserAccountMembership', 'Address',
           "Country", "AccountKycProfile", "UserLoginInfo"]


class Country(Base, AutoIdColumns, AuditColumns):
    __tablename__ = "countries"
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    nationality: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class UserLoginInfo(Base, AutoIdColumns, AuditColumns):
    """
    Verification status
    - 1 Not verified
    - 2 verified
    """
    email_address: Mapped[str] = mapped_column(String(255), index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(100), index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    otp_hash: Mapped[str] = mapped_column(nullable=True)
    verification_status: Mapped[int] = mapped_column(default=1)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.user_id'))
    user: Mapped['User'] = relationship(back_populates='login_info', lazy='joined')

    async def verify_otp(self, code) -> bool:
        from app.core.security import verify_password
        if self.otp_hash is None:
            return False
        return await verify_password(code, self.otp_hash)


class User(Base, AuditColumns):
    """
    Main user information model
    id_document_type:
        - NATIONAL_ID: national id
        - PASSPORT: passport
    user_role:
        - 1 Normal user
        - 10 SuperUser
    account_status:
        - 1 Not Active
        - 2 Active
        - -1 Blocked
    """
    user_id: Mapped[str] = mapped_column(default=generate_unique_str, index=True, nullable=False, primary_key=True)
    user_no: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    date_joined_utc: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    user_account_status: Mapped[int] = mapped_column(default=1, nullable=False)
    user_role: Mapped[int] = mapped_column(default=1, nullable=False)
    login_info: Mapped[Optional['UserLoginInfo']] = relationship('UserLoginInfo', back_populates='user', lazy='joined',
                                                                 cascade='all,delete')
    account_membership: Mapped[List['UserAccountMembership']] = relationship(back_populates='user', lazy='joined')
    accounts: AssociationProxy[List['ServiceAccount']] = association_proxy(
        "account_membership",
        "account",
        creator=lambda account_obj: UserAccountMembership(account=account_obj)
    )

    activations: Mapped['UserActivationStatus'] = relationship(back_populates="user", lazy='joined',
                                                               cascade='delete,all')


    @hybrid_property
    def account_no(self):
        return 'IND%s' % self.user_no


class UserAccountMembership(Base, AutoIdColumns):
    __table_name__ = "user_account_memberships"
    account_id: Mapped[str] = mapped_column(ForeignKey("service_accounts.account_id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    user: Mapped['User'] = relationship(back_populates='account_membership', lazy='joined')
    account: Mapped['ServiceAccount'] = relationship(lazy="joined")
    is_owner: Mapped[bool] = mapped_column(default=True)


class ServiceAccount(Base, AuditColumns):
    '''
    Store Account Data for a user or a business
    - verification status
        - 1 unverified
        - 2 verified
        - 3 failed verification
    - account_type:
        - INDIVIDUAL: Service account for an individual specified by the user_id
        - BUSINESS: Service account for a business specified bt the business_id
    '''
    account_name: Mapped[str]
    account_id: Mapped[str] = mapped_column(default=generate_unique_str, index=True, primary_key=True)
    account_no: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    account_type: Mapped[str]
    verification_status: Mapped[int] = mapped_column(default=1, nullable=True)
    verified_date_utc: Mapped[Optional[datetime]]
    verification_status_id: Mapped[str | None] = mapped_column(nullable=True)
    verification_statuses: Mapped[List['AccountKycVerificationStatus']] = relationship(lazy='joined',
                                                                                       cascade='all,delete')
    channels: Mapped[List['Channel']] = relationship(back_populates="account", cascade='all,delete')
    payment_account: Mapped[List['PaymentAccount']] = relationship(back_populates="account")
    address: Mapped['Address'] = relationship(lazy='joined', cascade='all,delete')
    kyc_profile: Mapped['AccountKycProfile'] = relationship('AccountKycProfile', back_populates='account',
                                                            lazy='joined', cascade='all,delete')


class AccountKycProfile(Base, AutoIdColumns, AuditColumns):
    full_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(nullable=False)
    id_document_type: Mapped[str | None] = mapped_column(String(100))
    id_date_of_issue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100))
    id_number: Mapped[str | None] = mapped_column(String(100), nullable=False, unique=True)
    gender: Mapped[str | None] = mapped_column(String(100), nullable=True)
    account_id: Mapped[str] = mapped_column(ForeignKey('service_accounts.account_id'))
    account: Mapped['ServiceAccount'] = relationship(back_populates='kyc_profile')


class AccountKycVerificationStatus(Base, AutoIdColumns, AuditColumns):
    __tablename__ = "kyc_verification_status"
    request_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    account_id: Mapped[str] = mapped_column(ForeignKey(f"{ServiceAccount.__tablename__}.account_id"))
    verification_response: Mapped[JSONB | None] = mapped_column(JSONB, nullable=True)
    state: Mapped[str] = mapped_column(String(200))
    request_status: Mapped[str] = mapped_column(String(200), nullable=True)
    status_reason= mapped_column(JSONB, nullable=True)
    upload_data = mapped_column(JSONB, nullable=True)


class Address(Base, AutoIdColumns, AuditColumns):
    __tablename__ = 'addresses'
    country: Mapped[str]
    address_line: Mapped[str | None]
    city: Mapped[str | None]
    account_id: Mapped[str] = mapped_column(ForeignKey('service_accounts.account_id'))
    account: Mapped['ServiceAccount'] = relationship(back_populates='address')


class UserActivationStatus(Base, AutoIdColumns, AuditColumns):
    """
    Store information regarding activation status of a user account
    Attributes:
        activation_reason(string): Either USER_REGISTRATION or PHONENUMBER_CHANGE
        status(string):
        ActivationStatus.INITIATED: Verification request initiated
        ActivationStatus.SUCCEEDED: User verified successfully
        ActivationStatus.FAILED: Could not verify user
        ActivationStatus.EXPIRED: Activation Expired
    """
    __tablename__ = "user_activation_status"
    user_activation_status_id: Mapped[str] = mapped_column(default=generate_unique_str, index=True, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(f'{User.__tablename__}.user_id'), nullable=False)
    user: Mapped['User'] = relationship(back_populates="activations", lazy='joined')
    activation_code: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    status: Mapped[str] = mapped_column(default="INITIATED")
    activation_reason: Mapped[str] = mapped_column(default="USER_REGISTRATION")
    expiry_time: Mapped[datetime]


# class ManagerPermission:
#     CREATE_CHANNEL = 0x19
#     MANAGE_FUNDS = 0x20
#     ADMINISTER = 0X80


# class ManagerRole(Base, AuditColumns):
#     """
#     Roles to control access to business resources
#     """
#     id: Mapped[int] = mapped_column(primary_key=True, index=True)
#     name: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
#     default: Mapped[bool] = mapped_column(nullable=False, index=True)
#     permissions: Mapped[int]
#     managers: Mapped[List['Management']] = relationship(back_populates='role')
#
#
# class Management(Base, AutoIdColumns, AuditColumns):
#     """
#     THese are owners of a particular business
#     """
#     business_id: Mapped[str] = mapped_column(ForeignKey(f"{Business.__tablename__}.id"))
#     user_id: Mapped[str] = mapped_column(nullable=False, index=True)
#     role: Mapped['ManagerRole'] = relationship(back_populates="managers")
#     role_id: Mapped['str'] = mapped_column(ForeignKey(f'{ManagerRole.__tablename__}.id'))
#
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return 'business_managers'
#
#     @staticmethod
#     def insert_roles(db: Session):
#         roles = {
#             'Administrator': (0xff, False)
#         }
#
#         for r in roles:
#             role = db.query(ManagerRole).filter_by(name=r).first()
#             if role is None:
#                 role = ManagerRole(name=r)
#             role.permissions = roles[r][0]
#             role.default = roles[r][1]
#             db.add(role)
#         db.commit()


class PaymentAccount(Base, AutoIdColumns, AuditColumns):
    bank_account_number: Mapped[str] = mapped_column(nullable=True)
    bank_code: Mapped[str] = mapped_column(nullable=True)
    bank_branch: Mapped[str] = mapped_column(nullable=True)
    bank_swift_code: Mapped[str] = mapped_column(nullable=True)
    currency: Mapped[str]
    mpesa_account_number: Mapped[str]
    is_approved: Mapped[bool] = mapped_column(default=False)
    account_id: Mapped[str]

    account_id: Mapped[str] = mapped_column(ForeignKey("service_accounts.account_id"))
    account: Mapped["ServiceAccount"] = relationship(back_populates="payment_account")


#####################################################################################
############################### MAPPER EVENTS #######################################
#####################################################################################
@event.listens_for(User, "before_insert")
def user_before_insert(mapper, connection: Connection, target: User):
    user_no = generate_random_sequence(connection=connection, table=User.__table__, column_id="user_no")
    target.user_no = user_no


@event.listens_for(ServiceAccount, "before_insert")
def service_account_before_insert(mapper, connection: Connection, target: ServiceAccount):
    if target.account_no is not None:
        return
    account_no = generate_random_sequence(connection=connection, table=ServiceAccount.__table__, column_id="account_no",
                                          prefix=target.account_type[:3])
    target.account_no = account_no


@event.listens_for(AccountKycVerificationStatus, "before_insert")
def kyc_verification_status_before_insert(mapper, connection, target: AccountKycVerificationStatus):
    table = ServiceAccount.__table__
    request_id = generate_random_sequence(connection=connection, table=AccountKycVerificationStatus.__table__,
                                          column_id="request_id")
    target.request_id = request_id


@event.listens_for(UserActivationStatus, 'before_insert')
def user_activation_status_before_insert(mapper, connection, target: UserActivationStatus):
    user_info_table = User.__table__
    user_activation_status_table = UserActivationStatus.__table__
    connection.execute(
        user_info_table.update().
        where(user_info_table.c.user_id == target.user_id).
        values(last_edited_date_utc=datetime.utcnow(), user_account_status=1, last_edited_by=target.created_by)
    )
    connection.execute(
        UserActivationStatus.__table__.delete()
        .where(user_activation_status_table.c.user_id == target.user_id)
    )
    target.activation_code = number_id_generator(6)
