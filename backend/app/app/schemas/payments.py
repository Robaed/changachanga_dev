import enum
from typing import Union

import pydantic
from pydantic import BaseModel, validator


class PaymentMethods(enum.Enum):
    MPESA = "MPESA"
    CARD = "CARD"


class Currencies(enum.Enum):
    KES = "KES"


class CardPaymentDetails(BaseModel):
    card_number: str
    card_exp_month: str
    card_exp_year: str
    card_cvv: str


class MpesaPaymentDetails(BaseModel):
    account_number: str


class ContributionRequest(pydantic.BaseModel):
    amount: float
    currency: Currencies
    mpesa_details: Union[MpesaPaymentDetails, None] = None
    card_details: Union[CardPaymentDetails, None] = None
    payment_method: PaymentMethods

    @validator("payment_method")
    def validate_payment_method(cls, v: PaymentMethods, values: dict):
        if v == PaymentMethods.MPESA:
            assert values.get('mpesa_details') is not None
            assert values.get('card_details') is None
        if v == PaymentMethods.CARD:
            assert values.get('mpesa_details') is None
            assert values.get('card_details') is not None
        return v


class PaymentRequestStatuses(enum.Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
