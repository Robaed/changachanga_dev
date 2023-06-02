import unittest
from unittest.mock import AsyncMock

from app.providers.payment_lib import MpesaPaymentsGatewayClient, STKPushRequest, PaymentGatewayException


class MpesaPaymentGatewayClientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mpesa_client = MpesaPaymentsGatewayClient('org_short_code', 'org_pass_key')

    async def test_make_payment_success(self):
        mock_client = AsyncMock()
        mock_client.post.return_value.__aenter__.return_value.status_code = 200
        mock_client.post.return_value.__aenter__.return_value.json.return_value = {'status': 'success'}

        payload = STKPushRequest(
            phoneNumber='254712345678',
            amount='1000',
            invoiceNumber='INV001',
            sharedShortCode=True,
            orgShortCode='12345',
            orgPassKey='pass_key',
            callbackUrl='https://example.com/callback',
            transactionDescription='Payment for goods'
        )

        expected_payload = {
            'BusinessShortCode': 'org_short_code',
            'Password': 'encrypted_password',
            'Timestamp': '2023-05-26T12:34:56',
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': '1000',
            'PartyA': '254712345678',
            'PartyB': 'org_short_code',
            'PhoneNumber': '254712345678',
            'CallBackURL': 'https://example.com/callback',
            'AccountReference': 'INV001',
            'TransactionDesc': 'Payment for goods'
        }

        with unittest.mock.patch('httpx.AsyncClient', return_value=mock_client):
            response = await self.mpesa_client.make_payment(payload)

        mock_client.post.assert_called_once_with('https://payment-gateway-api.com/payments', json=expected_payload)
        self.assertEqual(response, {'status': 'success'})

    async def test_make_payment_failure(self):
        mock_client = AsyncMock()
        mock_client.post.return_value.__aenter__.return_value.status_code = 400

        payload = STKPushRequest(
            phoneNumber='254712345678',
            amount='1000',
            invoiceNumber='INV001',
            sharedShortCode=True,
            orgShortCode='12345',
            orgPassKey='pass_key',
            callbackUrl='https://example.com/callback',
            transactionDescription='Payment for goods'
        )

        with unittest.mock.patch('httpx.AsyncClient', return_value=mock_client):
            with self.assertRaises(PaymentGatewayException):
                await self.mpesa_client.make_payment(payload)

        mock_client.post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
