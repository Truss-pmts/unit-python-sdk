from unittest.mock import Mock, patch

import pytest
import requests

from unit.api.payment_resource import PaymentResource
from unit.models.payment import BookPaymentDTO, ListPaymentParams


@pytest.fixture
def resource():
    return PaymentResource(api_url="https://unit.example", token="test-token")


@pytest.fixture
def native_payment():
    return {
        "type": "bookPayment",
        "id": "payment-1",
        "attributes": {
            "amount": 12500,
            "createdAt": "2026-10-26T12:00:00.000Z",
            "description": "Repayment",
            "direction": "Credit",
            "status": "Sent",
            "tags": {"attempt": "attempt-1"},
        },
        "relationships": {
            "account": {"data": {"type": "depositAccount", "id": "source-1"}},
            "counterpartyAccount": {
                "data": {"type": "depositAccount", "id": "destination-1"}
            },
        },
    }


@pytest.mark.parametrize("timeout", [None, 2.5])
def test_get_forwards_timeout_and_preserves_include(resource, native_payment, timeout):
    response = Mock(status_code=200)
    response.json.return_value = {"data": native_payment}
    kwargs = {} if timeout is None else {"timeout": timeout}

    with patch("unit.api.base_resource.requests.get", return_value=response) as transport:
        result = resource.get("payment-1", "account", **kwargs)

    assert transport.call_args.args == ("https://unit.example/payments/payment-1",)
    assert transport.call_args.kwargs["params"] == {"include": "account"}
    assert transport.call_args.kwargs["timeout"] == timeout
    assert isinstance(result.data, BookPaymentDTO)
    assert result.data.id == "payment-1"
    assert result.data.attributes["amount"] == 12500
    assert result.data.relationships["account"].id == "source-1"


@pytest.mark.parametrize("timeout", [None, 2.5])
def test_list_forwards_timeout_and_preserves_filters(resource, native_payment, timeout):
    response = Mock(status_code=200)
    response.json.return_value = {"data": [native_payment]}
    params = ListPaymentParams(limit=2, offset=4, tags='{"attempt":"attempt-1"}')
    kwargs = {} if timeout is None else {"timeout": timeout}

    with patch("unit.api.base_resource.requests.get", return_value=response) as transport:
        result = resource.list(params, **kwargs)

    assert transport.call_args.args == ("https://unit.example/payments",)
    assert transport.call_args.kwargs["params"] == {
        "page[limit]": 2,
        "page[offset]": 4,
        "filter[tags]": '{"attempt":"attempt-1"}',
    }
    assert transport.call_args.kwargs["timeout"] == timeout
    assert len(result.data) == 1
    assert isinstance(result.data[0], BookPaymentDTO)
    assert result.data[0].id == "payment-1"


def test_list_without_arguments_preserves_defaults(resource):
    response = Mock(status_code=200)
    response.json.return_value = {"data": []}

    with patch("unit.api.base_resource.requests.get", return_value=response) as transport:
        result = resource.list()

    assert transport.call_args.kwargs["params"] == {
        "page[limit]": 100,
        "page[offset]": 0,
    }
    assert transport.call_args.kwargs["timeout"] is None
    assert result.data == []


@pytest.mark.parametrize("method", ["get", "list"])
def test_read_timeout_propagates(resource, method):
    with patch("unit.api.base_resource.requests.get", side_effect=requests.Timeout):
        with pytest.raises(requests.Timeout):
            if method == "get":
                resource.get(payment_id="payment-1", timeout=2.5)
            else:
                resource.list(timeout=2.5)
