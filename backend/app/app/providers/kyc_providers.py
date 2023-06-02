import random

import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

from app.core.config import settings
from app.schemas.kyc_verification import UserKycData, UserKycVerificationProviderResult


class KycProviderBase(object):
    async def verify_user_kyc(self, id_number: str, first_name: str,
                              last_name: str) -> UserKycVerificationProviderResult: raise NotImplementedError


class MockKycProvider(KycProviderBase):
    async def verify_user_kyc(self, *args, **kwargs) -> UserKycVerificationProviderResult:
        result = random.choice([True, False])
        return UserKycVerificationProviderResult(
            success=result
        )


class IprsKycProvider(KycProviderBase):
    _username = None
    _password = None
    ENDPOINT = "http://197.248.4.134/iprs/databyid"

    INSTANCE = None

    @classmethod
    def GET_INSTANCE(cls):
        if cls.INSTANCE is None:
            return cls(
                username=settings.IPRS_USERNAME,
                password=settings.IPRS_PASSWORD
            )

    def __init__(self, username: str, password: str):
        if self.INSTANCE is not None: raise ValueError
        self._password = password
        self._username = username

    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, min=3, max=10), reraise=True,
           retry=retry_if_exception_type(httpx.TimeoutException))
    async def verify_user_kyc(self, id_number: str, first_name: str,
                              last_name: str) -> UserKycVerificationProviderResult:
        username = self._username
        password = self._password
        url = "%s?number=%s" % (self.ENDPOINT, id_number)
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, auth=(username, password))
            if response.status_code == 200:
                data = response.json()
                res: UserKycData = UserKycData.parse_obj(data)
                try:
                    assert res.valid is True
                    assert res.first_name.strip().lower() == first_name.strip().lower()
                    assert res.surname.strip().lower() == last_name.strip().lower()
                except AssertionError as exc:
                    return UserKycVerificationProviderResult(success=False, payload=res,
                                                             errors="Failed Verification ID and password mismatch")
                return UserKycVerificationProviderResult(success=True, payload=res)
            else:
                return UserKycVerificationProviderResult(success=False, errors=response.text)
