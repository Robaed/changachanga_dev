import logging
from typing import List

import httpx
from pydantic import BaseModel

from app.core.config import settings


class SmsProvider(object):
    _logger: logging.Logger = None

    def __init__(self, logger: logging.Logger = None):
        if logger is None:
            logger = logging.getLogger(__name__)
        self._logger = logger

    def send_sms(self, msg: str, phone_number: str):
        raise NotImplementedError

    async def send_sms_async(self, msg: str, phone_number: str):
        raise NotImplementedError


class MockSmsProvider(SmsProvider):
    async def send_sms_async(self, msg: str, phone_number: str):
        self._logger.info(
            "SMS(%s:%s" % (phone_number, msg)
        )


class SendSmsException(Exception): pass


class AfrikasTalkingSms(SmsProvider):
    _api_key = None
    _shortcode = None
    _username = None
    INSTANCE = None

    def __init__(self, api_key: str, shortcode: str, username: str):
        if self.INSTANCE is not None:
            raise ValueError("Attempting to reinitialize a singleton")
        self._api_key = api_key
        self._shortcode = shortcode
        self._username = username

    @classmethod
    def GET_INSTANCE(cls):
        from app.core.config import settings
        if cls.INSTANCE is None:
            cls.INSTANCE = cls(api_key=
                               settings.AT_APIKEY,
                               shortcode=settings.AT_SHORTCODE,
                               username=settings.AT_USERNAME)
        return cls.INSTANCE

    class Recipient(BaseModel):
        statusCode: int
        number: str
        status: str
        cost: str
        messageId: str

    class SMSMessageData(BaseModel):
        Message: str
        Recipients: List['Recipient']

    class Payload(BaseModel):
        SMSMessageData: 'SMSMessageData'

    async def send_sms_async(self, msg: str, phone_number: str):
        url = "https://api.africastalking.com/version1/messaging"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "apiKey": self._api_key,
        }
        data = {
            "username": self._username,
            "to": "+%s" % phone_number,
            "message": msg,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)

            # Process the response
            if response.status_code == 200:
                resp = self.Payload.parse_obj(response.json())
            else:
                raise SendSmsException(response.text)


class WhatsAppProvider(SmsProvider):
    ENDPOINT = "https://api.maytapi.com/api"
    _product_id = None
    _phone_id = None
    token = None
    INSTANCE = None

    def __init__(self, *args, product_id: str, phone_id: str, token: str, **kwargs):
        super().__init__(*args, **kwargs)
        if self.INSTANCE is not None:
            raise ValueError("Attempting to reinitialize a singleton")
        self._phone_id = phone_id
        self._product_id = product_id
        self._token = token

    @classmethod
    def GET_INSTANCE(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls(token=settings.WA_TOKEN, product_id=settings.WA_PRODUCT_ID,
                               phone_id=settings.WA_PHONE_ID)
        return cls.INSTANCE

    async def send_sms_async(self, msg: str, phone_number: str):
        req_body = dict(
            type="text",
            message=msg,
            to_number=phone_number
        )

        req_headers = {
            "content-type": "application/json",
            "x-maytapi-key": self._token,
        }
        async with httpx.AsyncClient() as client:
            url = "%s/%s/%s/sendMessage" % (
                self.ENDPOINT,
                self._product_id,
                self._phone_id,
            )
            response = await client.post(url, json=req_body, headers=req_headers)
            if response.status_code > 299:
                raise SendSmsException(response.text)


class BongaSmsProvider(SmsProvider):
    INSTANCE = None
    _client_id = None
    _api_key = None
    _secret = None
    _url = "http://167.172.14.50:4002/v1/send-sms"

    def __init__(self, api_key: str, secret: str, client_id: str, service_id: str):
        if self.INSTANCE is not None: raise ValueError("Attempting to initialize singleton")
        self._client_id = client_id
        self._api_key = api_key
        self._service_id = service_id
        self._secret = secret

    @classmethod
    def GET_INSTANCE(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls(api_key=settings.BONGA_KEY, secret=settings.BONGA_SECRET,
                               client_id=settings.BONGA_CLIENT_ID,
                               service_id=settings.BONGA_SERVICE_ID)
        return cls.INSTANCE

    async def send_sms_async(self, msg: str, phone_number: str):

        payload = {
            'apiClientID': self._client_id,
            'key': self._api_key,
            'secret': self._secret,
            'txtMessage': msg,
            'MSISDN': phone_number,
            'serviceID': self._service_id
        }
        files = []
        headers = {}
        retry_count = 0
        max_retries = 12
        while True:
            async with httpx.AsyncClient() as client:
                response = await client.post(self._url, headers=headers, data=payload)
                response_text = response.text
                if response.status_code < 299:
                    break
                elif retry_count < max_retries:
                    retry_count += 1
                    continue
                else:
                    raise SendSmsException(response_text)
