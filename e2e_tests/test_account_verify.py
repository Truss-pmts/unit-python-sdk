import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from unit.api.account_resource import AccountResource
from unit.models.account import AccountVerifyRequest


class TestAccountVerify(unittest.TestCase):
    def test_account_verify_request_to_json_api(self):
        request = AccountVerifyRequest(
            routing_number="051000017", account_number="10000123"
        )
        self.assertEqual(
            request.to_json_api(),
            {
                "data": {
                    "type": "accountVerify",
                    "attributes": {
                        "routingNumber": "051000017",
                        "accountNumber": "10000123",
                    },
                }
            },
        )

    @patch("unit.api.base_resource.requests.post")
    def test_account_verify_match(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "exists": True,
                "account": {
                    "type": "depositAccount",
                    "id": "1000000",
                    "attributes": {
                        "createdAt": "2023-01-01T00:00:00.000Z",
                        "name": "Peter Parker",
                        "status": "Open",
                        "depositProduct": "checking",
                        "routingNumber": "051000017",
                        "accountNumber": "10000123",
                        "currency": "USD",
                        "balance": 10000,
                        "hold": 0,
                        "available": 10000,
                        "tags": {},
                    },
                    "relationships": {
                        "customer": {
                            "data": {"type": "individualCustomer", "id": "100"}
                        }
                    },
                },
            }
        }
        mock_post.return_value = mock_response

        resource = AccountResource("https://api.s.unit.sh", "token")
        request = AccountVerifyRequest(
            routing_number="051000017", account_number="10000123"
        )
        response = resource.verify(request=request)

        self.assertTrue(response.data.exists)
        self.assertEqual(response.data.account.id, "1000000")
        self.assertEqual(response.data.account.relationships["customer"].id, "100")

    @patch("unit.api.base_resource.requests.post")
    def test_account_verify_no_match(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"exists": False}}
        mock_post.return_value = mock_response

        resource = AccountResource("https://api.s.unit.sh", "token")
        request = AccountVerifyRequest(
            routing_number="051000017", account_number="10000123"
        )
        response = resource.verify(request=request)

        self.assertFalse(response.data.exists)
        self.assertIsNone(response.data.account)


if __name__ == "__main__":
    unittest.main()
