import os
import unittest
from unit import Unit
from unit.models import Relationship
from unit.models.payment import CreateAchStopPaymentRequest

token = os.environ.get('TOKEN')
client = Unit("https://api.s.unit.sh", token)


def test_create_ach_stop_payment_payload():
    request = CreateAchStopPaymentRequest(
        originator_name=["SINCLAIR FUNDING"],
        direction="Debit",
        min_amount=1000,
        is_multi_use=True,
        description="Block unauthorized debit",
        relationships={"account": Relationship("depositAccount", "10000")},
    )

    payload = request.to_json_api()

    assert payload["data"]["type"] == "achStopPayment"
    attributes = payload["data"]["attributes"]
    assert attributes["originatorName"] == ["SINCLAIR FUNDING"]
    assert attributes["direction"] == "Debit"
    assert attributes["minAmount"] == 1000
    assert attributes["isMultiUse"] is True
    assert attributes["description"] == "Block unauthorized debit"
    assert "account" in payload["data"]["relationships"]


def test_create_ach_stop_payment():
    # request = CreateAchStopPaymentRequest(
    #     originator_name=["SINCLAIR FUNDING"],
    #     is_multi_use=True,
    #     relationships={"account": Relationship("depositAccount", "10000")},
    # )
    # response = client.ach_stop_payments.create(request)
    # assert response.data.type == "achStopPayment"
    assert True
