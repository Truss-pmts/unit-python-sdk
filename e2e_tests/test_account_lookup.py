import unittest
from unittest.mock import MagicMock, patch

from unit.api.account_resource import AccountResource
from unit.models import UnitError
from unit.models.account import ListAccountParams


class TestAccountLookup(unittest.TestCase):
    def test_account_lookup_params(self):
        params = ListAccountParams(
            limit=1, routing_number="051000017", account_number="10000123"
        )
        self.assertEqual(
            params.to_dict(),
            {
                "page[limit]": 1,
                "page[offset]": 0,
                "filter[routingNumber]": "051000017",
                "filter[accountNumber]": "10000123",
            },
        )

    @patch("unit.api.base_resource.requests.get")
    def test_account_lookup_match(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
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
            ]
        }
        mock_get.return_value = mock_response

        resource = AccountResource(api_url="https://api.s.unit.sh", token="token")
        params = ListAccountParams(
            limit=1, routing_number="051000017", account_number="10000123"
        )
        response = resource.list(params=params, timeout=5)

        self.assertEqual(response.data[0].id, "1000000")
        self.assertEqual(response.data[0].relationships["customer"].id, "100")
        self.assertEqual(mock_get.call_args.args, ("https://api.s.unit.sh/accounts",))
        self.assertEqual(mock_get.call_args.kwargs["params"], params.to_dict())
        self.assertEqual(mock_get.call_args.kwargs["timeout"], 5)

    @patch("unit.api.base_resource.requests.get")
    def test_account_lookup_no_match(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        resource = AccountResource(api_url="https://api.s.unit.sh", token="token")
        params = ListAccountParams(
            routing_number="051000017", account_number="10000123"
        )
        response = resource.list(params=params)

        self.assertEqual(response.data, [])
        self.assertIsNone(mock_get.call_args.kwargs["timeout"])

    @patch("unit.api.base_resource.requests.get")
    def test_account_lookup_error(self, mock_get):
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = {
            "errors": [{"status": "400", "title": "Invalid value"}]
        }
        resource = AccountResource(api_url="https://api.s.unit.sh", token="token")
        params = ListAccountParams(
            routing_number="051000017", account_number="invalid"
        )

        response = resource.list(params=params, timeout=5)

        self.assertIsInstance(response, UnitError)
        self.assertEqual(response.errors[0].title, "Invalid value")


if __name__ == "__main__":
    unittest.main()
