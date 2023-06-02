from typing import List

from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.base_class import Base, AuditColumns, AutoIdColumns
from app.db.base_class import generate_random_sequence, generate_unique_str

__all__ = ['Channel', 'channel_before_insert', "channel_invite_before_insert", "ChannelParticipants",
           "ChannelInvite", "PaymentRequest", "payment_request_before_insert"

           ]


#
# 'WithdrawalApproval', 'Transaction', 'Withdrawal', 'Contribution', 'ChannelConfiguration',
#            'Participant']
#
#

class ChannelInvite(Base, AuditColumns, AutoIdColumns):
    """
    Tracks sent invites for a specific channel
    invite_status:
    - Pending New invite
    - 1 sent Invite sent to user
    - 3 accepted Invite accepted by user
    - 4 rejected User Rejected invite
    """
    channel_id: Mapped['str'] = mapped_column(ForeignKey('channels.id'))
    channel: Mapped['Channel'] = relationship(back_populates='channel_invites', lazy='joined')
    phone_number: Mapped['str'] = mapped_column(nullable=False)
    invite_code: Mapped['str'] = mapped_column(unique=True, index=True)
    invite_status: Mapped[str] = mapped_column(nullable=False)


class Channel(Base, AutoIdColumns, AuditColumns):
    channel_no: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    running_balance: Mapped[float] = mapped_column(nullable=False, default=0.0)
    link: Mapped[str | None] = mapped_column(nullable=True)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    video_url: Mapped[str | None] = mapped_column(nullable=True)
    image_url: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    account_no: Mapped[str] = mapped_column(ForeignKey("service_accounts.account_no"))
    account: Mapped["ServiceAccount"] = relationship(back_populates="channels", cascade='delete,all')
    participants: Mapped[List['ChannelParticipants']] = relationship(lazy='selectin')
    channel_invites: Mapped[List['ChannelInvite']] = relationship(lazy='selectin', back_populates='channel')

    # configuration: Mapped['ChannelConfiguration'] = relationship(back_populates="channel")

    # contributions: Mapped['Contribution'] = relationship()
    #
    # withdrawals: Mapped['Withdrawal'] = relationship()
    #
    # transactions: Mapped['Transaction'] = relationship(back_populates='channel')


class ChannelParticipants(Base, AuditColumns):
    __tablename__ = 'channel_participants'
    user_id: Mapped[str] = mapped_column(String(100), ForeignKey('users.user_id'), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(100), ForeignKey('channels.id'), primary_key=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    user: Mapped['User'] = relationship(lazy='selectin')
    # payment_requests: Mapped[List['PaymentRequest']] = relationship(lazy='joined')


class PaymentRequest(Base, AuditColumns, AutoIdColumns):
    request_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False, unique=True)
    payment_method: Mapped[str] = mapped_column(String(100))
    request_payload = mapped_column(JSONB, nullable=True)
    payment_request_result = mapped_column(JSONB, nullable=True)
    payment_callback_result = mapped_column(JSONB, nullable=True)
    request_status: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    channel_id: Mapped[String] = mapped_column(ForeignKey("channels.id"))
    user_id: Mapped['String'] = mapped_column(ForeignKey("users.user_id"))


# class ChannelConfiguration(Base, AutoIdColumns, AuditColumns):
#     target_amount: Mapped[float]
#     duration: Mapped[timedelta]
#
#     channel_id: Mapped[str] = mapped_column(ForeignKey(f"{Channel.__tablename__}.id"))
#     channel: Mapped['Channel'] = relationship(back_populates="configuration")
#
#
# class Contribution(Base, AutoIdColumns, AuditColumns):
#     amount: Mapped[float]
#     timestamp_utc: Mapped[float]
#     mpesa_receipt: Mapped[str] = mapped_column(nullable=True)
#     payment_channel: Mapped[int] = mapped_column(nullable=False)
#     card_number: Mapped[str] = mapped_column(nullable=True)
#     origination_channel_id: Mapped[str] = mapped_column(nullable=True)
#     transaction_id: Mapped[str] = mapped_column(nullable=True)
#     user_id: Mapped[str] = mapped_column(nullable=False)
#
#     channel_id: Mapped[str] = mapped_column(ForeignKey(f"{Channel.__tablename__}.id"))
#     channel: Mapped['Channel'] = relationship(back_populates="contributions")
#
#
# class Withdrawal(Base, AutoIdColumns, AuditColumns):
#     payment_account_id: Mapped[str]
#     transaction_id: Mapped[str] = mapped_column(nullable=True)
#     is_approved: Mapped[bool]
#     status: Mapped[str]
#     status_reason: Mapped[str]
#     date_initiated_utc: Mapped[str]
#     status_date_utc: Mapped[str]
#
#     channel_id: Mapped[str] = mapped_column(ForeignKey(f"{Channel.__tablename__}.id"))
#     channel: Mapped['Channel'] = relationship(back_populates="withdrawals")
#
#     approvals: Mapped['WithdrawalApproval'] = relationship(back_populates='withdrawal')
#
#
# class WithdrawalApproval(Base, AutoIdColumns, AuditColumns):
#     approver_id: Mapped[str]
#     is_approved: Mapped[bool] = mapped_column(default=False)
#     approved_at_utc: Mapped[datetime] = mapped_column(nullable=True)
#
#     withdrawal_id: Mapped[str] = mapped_column(ForeignKey(f"{Withdrawal.__tablename__}.id"))
#     withdrawal: Mapped['Withdrawal'] = relationship(back_populates="approvals")
#
#
# class Transaction(Base, AuditColumns, AutoIdColumns):
#     transaction_type: Mapped[str]
#     mpesa_receipt: Mapped[str]
#     mpesa_phone_number: Mapped[str]
#     bank_account_number: Mapped[str]
#     bank_account_name: Mapped[str]
#     bank_reference_number: Mapped[str]
#     destination_channel_id: Mapped[str]
#     originating_channel_id: Mapped[str]
#     card_number: Mapped[str]
#     amount: Mapped[float]
#     running_balance: Mapped[float]
#     timestamp_utc: Mapped[float]
#
#     channel_id: Mapped[str] = mapped_column(ForeignKey(f"{Channel.__tablename__}.id"))
#     channel: Mapped['Channel'] = relationship(back_populates="transactions")

########################################################################################################################
########################################################################################################################
########################################## Table Events ################################################################
########################################################################################################################
########################################################################################################################
@event.listens_for(Channel, 'before_insert')
def channel_before_insert(mapper, connection, target: Channel):
    channels_table = Channel.__table__
    channel_id = target.id
    if channel_id is None:
        target.id = generate_unique_str()
    target.channel_no = generate_random_sequence(connection=connection, table=channels_table,
                                                 column_id="channel_no", prefix="CH")
    target.code = generate_random_sequence(connection=connection, table=channels_table,
                                           column_id="code", generator_type='general', general_size=6)


@event.listens_for(ChannelInvite, 'before_insert')
def channel_invite_before_insert(mapper, connection, target: ChannelInvite):
    target.invite_code = generate_random_sequence(connection=connection, table=ChannelInvite.__table__,
                                                  column_id="invite_code",
                                                  generator_type='general', general_size=6)


@event.listens_for(PaymentRequest, 'before_insert')
def payment_request_before_insert(mapper, connection, target: PaymentRequest):
    target.request_id = generate_random_sequence(connection=connection, table=target.__table__,
                                                 column_id="request_id",
                                                 generator_type='general', general_size=10)
