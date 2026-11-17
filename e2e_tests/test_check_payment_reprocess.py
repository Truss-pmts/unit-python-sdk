import unittest
from unittest.mock import MagicMock, patch

from unit.api.check_payment_resource import CheckPaymentResource
from unit.models import UnitError
from unit.models.check_payment import CheckPaymentDTO


def _check_payment_response(status: str) -> dict:
    return {
        "data": {
            "type": "checkPayment",
            "id": "1001",
            "attributes": {
                "createdAt": "2026-11-16T15:00:00.000Z",
                "updatedAt": "2026-11-16T15:05:00.000Z",
                "amount": 12500,
                "status": status,
                "description": "Check Payment | 0322",
                "checkNumber": "0322",
                "originated": False,
                "returnCutoffTime": "2026-11-17T16:50:00.000Z",
            },
            "relationships": {
                "account": {"data": {"type": "depositAccount", "id": "10001"}},
                "customer": {"data": {"type": "businessCustomer", "id": "100"}},
            },
        }
    }


class TestCheckPaymentReprocess(unittest.TestCase):
    @patch("unit.api.base_resource.requests.post")
    def test_reprocess_posts_without_body_and_decodes_check_payment(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _check_payment_response(status="Processed")
        mock_post.return_value = mock_response

        resource = CheckPaymentResource(api_url="https://api.s.unit.sh", token="token")
        response = resource.reprocess(check_payment_id="1001")

        self.assertEqual(
            mock_post.call_args.args,
            ("https://api.s.unit.sh/check-payments/1001/reprocess",),
        )
        self.assertIsNone(mock_post.call_args.kwargs["data"])
        self.assertIsInstance(response.data, CheckPaymentDTO)
        self.assertEqual(response.data.id, "1001")
        self.assertEqual(response.data.attributes["status"], "Processed")
        self.assertEqual(response.data.relationships["account"].id, "10001")

    @patch("unit.api.base_resource.requests.post")
    def test_reprocess_returns_unit_error(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "errors": [{"status": "400", "title": "Check payment is not in MarkedForReturn status"}]
        }

        resource = CheckPaymentResource(api_url="https://api.s.unit.sh", token="token")
        response = resource.reprocess(check_payment_id="1001")

        self.assertIsInstance(response, UnitError)
        self.assertEqual(
            response.errors[0].title, "Check payment is not in MarkedForReturn status"
        )


if __name__ == "__main__":
    unittest.main()
