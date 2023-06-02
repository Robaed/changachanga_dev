import base64
import enum
from typing import Optional

import httpx
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

from app.schemas import payments


# region exception classes
class KcbPaymentGatewayClientException(Exception): pass


# endregion

# region models
class StkPushResultStatus(enum.Enum):
    success = "0"
    failed = "1"


class STKPushRequest(BaseModel):
    phoneNumber: str
    amount: str
    invoiceNumber: str
    sharedShortCode: bool
    orgShortCode: str
    orgPassKey: str
    callbackUrl: str
    transactionDescription: str


class StkPushResultResponse(BaseModel):
    MerchantRequestID: Optional[str]
    ResponseCode: Optional[str]
    CustomerMessage: Optional[str]
    CheckoutRequestID: Optional[bool]
    ResponseDescription: Optional[str]


class StkPushResultHeader(BaseModel):
    statusDescription: str
    statusCode: StkPushResultStatus


class StkPushResult(BaseModel):
    response: StkPushResultResponse
    header: StkPushResultHeader


class MakePaymentStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


class MakePaymentResult(BaseModel):
    provider_data: dict
    status: MakePaymentStatus


class CardPaymentRequest(BaseModel):
    card_number: str
    card_exp_month: str
    card_exp_year: str
    amount: float


class CardPaymentResponse(BaseModel):
    transaction_id: str
    status: str


# endregion


class KcbPaymentGatewayClient:
    _base_url = "https://wso2-api-gateway-direct-kcb-wso2-gateway.apps.test.aro.kcbgroup.com"
    _token_endpoint = '/token'

    def __init__(self, client_id: str, client_secret: str, server_host: AnyHttpUrl):
        self.client_id = client_id
        self.client_secret = client_secret
        self.server_host = server_host
        KcbPaymentGatewayClient._instance = self

    def _get_authorization_header(self) -> str:
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=1, max=10),
        reraise=True,
        retry=retry_if_exception_type(KcbPaymentGatewayClientException)
    )
    async def generate_access_token(self) -> str:
        auth_header = self._get_authorization_header()

        data = {
            'grant_type': 'client_credentials'
        }
        url = "%s%s" % (self._base_url, self._token_endpoint)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    params=data,
                    headers={'Authorization': auth_header}
                )

                response.raise_for_status()
                token_data = response.json()
                if response.status_code > 299:
                    raise KcbPaymentGatewayClientException("Could not obtain token %s" % response.text)
                return token_data['access_token']
        except httpx.TimeoutException as exc:
            raise KcbPaymentGatewayClientException('Timeout when calling KCB %s' % exc)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=1, max=10),
        reraise=True,
        retry=retry_if_exception_type(KcbPaymentGatewayClientException)
    )
    async def stk_push_request(self, stk_push_request: STKPushRequest):
        access_token = await self.generate_access_token()
        headers = {
            'accept': 'application/json',
            'routeCode': '207',
            'operation': 'STKPush',
            'messageId': '232323_KCBOrg_8875661561',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % access_token
        }
        payload = {
            "phoneNumber": stk_push_request.phoneNumber,
            "amount": stk_push_request.amount,
            "invoiceNumber": stk_push_request.invoiceNumber,
            "sharedShortCode": stk_push_request.sharedShortCode,
            "orgShortCode": stk_push_request.orgShortCode,
            "orgPassKey": stk_push_request.orgPassKey,
            "callbackUrl": stk_push_request.callbackUrl,
            "transactionDescription": stk_push_request.transactionDescription
        }

        # Make the API call to initiate the payment
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post('https://uat.buni.kcbgroup.com/mm/api/request/1.0.0/stkpush',
                                             headers=headers,
                                             json=payload)

                if response.status_code == 200:
                    return response.json()
                else:
                    raise KcbPaymentGatewayClientException('Payment failed.')
        except httpx.TimeoutException as exc:
            raise KcbPaymentGatewayClientException('Timeout when calling KCB %s' % exc)


class CyberSourceClientException(Exception):
    pass


class CyberSourceClient:
    def __init__(self, api_key: str, merchant_id: str):
        self.api_key = api_key
        self.merchant_id = merchant_id

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=1, max=10),
        reraise=True,
        retry=retry_if_exception_type(CyberSourceClientException)
    )
    async def process_card_payment(self, payment_request: CardPaymentRequest) -> CardPaymentResponse:
        url = "https://api.cybersource.com/v2/payments"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "card_number": payment_request.card_number,
            "card_exp_month": payment_request.card_exp_month,
            "card_exp_year": payment_request.card_exp_year,
            "amount": payment_request.amount,
            "merchant_id": self.merchant_id,
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response_data = response.json()

                transaction_id = response_data.get("transaction_id")
                status = response_data.get("status")
                if response.status_code > 499:  # retry 5XX errors
                    raise CyberSourceClientException(
                        "Could not complete card payment. Encountered Exception %s" % response.text)
                if response.status_code > 399:  # permanently fail for 4XX errors
                    raise Exception("Unable to complete card payment request %s " % response.text)
                payment_response = CardPaymentResponse(transaction_id=transaction_id, status=status)
                return payment_response
        except httpx.TimeoutException as exc:  # retry timeout exceptions
            raise CyberSourceClientException("Timeout error while processing card payment")


class PaymentGatewayClient:
    _instance = None

    def __init__(self,
                 kcb_client_id: str,
                 kcb_client_secret: str,
                 cybersource_api_key: str,
                 cybersource_merchant_id: str,
                 server_host: AnyHttpUrl):
        """
        Initializes an instance of the PaymentGatewayClient.

        Args:
            kcb_client_id (str): The KCB client ID.
            kcb_client_secret (str): The KCB client secret.
            cybersource_api_key (str): The CyberSource API key.
            cybersource_merchant_id (str): The CyberSource merchant ID.
            server_host (AnyHttpUrl): The server host URL.

        Raises:
            RuntimeError: If an instance of the PaymentGatewayClient is already created.

        """

        if PaymentGatewayClient._instance is not None:
            raise RuntimeError("Cannot create multiple instances of Singleton class")
        self._kcb_client = KcbPaymentGatewayClient(client_id=kcb_client_id, client_secret=kcb_client_secret,
                                                   server_host=server_host)

        self._cybersource_client = CyberSourceClient(cybersource_api_key, cybersource_merchant_id)

    @classmethod
    def get_instance(cls, kcb_client_id: str,
                     kcb_client_secret: str,
                     cybersource_api_key: str,
                     cybersource_merchant_id: str, server_host: AnyHttpUrl):

        if not cls._instance:
            cls._instance = PaymentGatewayClient(
                kcb_client_id, kcb_client_secret, cybersource_api_key, cybersource_merchant_id, server_host=server_host
            )
        return cls._instance

    async def make_payment(self, request_id: str, req: payments.ContributionRequest) -> MakePaymentResult:
        if req.payment_method == "CARD":
            # Make a card payment using CyberSource client
            card_payment_request = CardPaymentRequest(
                card_number=req.card_details.card_number,
                card_exp_month=req.card_details.card_exp_month,
                card_exp_year=req.card_details.card_exp_year,
                amount=req.amount
            )
            card_payment_response = await self._cybersource_client.process_card_payment(card_payment_request)

            # Create and return the MakePaymentResult
            result = MakePaymentResult(
                provider_data=card_payment_response.dict(),
                status=MakePaymentStatus.SUCCESS
            )
            return result
        elif req.payment_method == "MPESA":
            # Make an stkpush request using KCB client
            stk_push_request = STKPushRequest(
                phoneNumber=req.mpesa_details.account_number,
                amount=str(req.amount),
                invoiceNumber=request_id,
                sharedShortCode=True,
                orgShortCode="",
                orgPassKey="",
                callbackUrl="",
                transactionDescription="ChangaChanga Contribution"
            )
            stk_push_response = await self._kcb_client.stk_push_request(stk_push_request)

            # Create and return the MakePaymentResult

            result = MakePaymentResult(
                provider_data=stk_push_response.dict(),
                status=MakePaymentStatus.SUCCESS
            )
            return result
        else:
            raise ValueError("Invalid payment method")
