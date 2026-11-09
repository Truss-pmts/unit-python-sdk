import copy
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from unit.api.payment_resource import PaymentResource
from unit.api.wire_resource import WireResource
from unit.models import Address, Relationship, UnitError, UnitResponse, WireCounterparty
from unit.models.codecs import DtoDecoder, UnitEncoder
from unit.models.event import (
    AssignmentCreatedEvent,
    AssignmentEscalatedEvent,
    PaymentCreatedEvent,
    PaymentPendingReviewEvent,
    PaymentRejectedEvent,
    PaymentReturnedEvent,
    PaymentSentEvent,
)
from unit.models.payment import (
    AchPaymentDTO,
    CreateWirePaymentRequest,
    ListPaymentParams,
    SimulateIncomingWireRequest,
    SimulateTransmitWireRequest,
    WirePaymentDTO,
)
from unit.models.transaction import ReturnedWireTransactionDTO, WireTransactionDTO

API_URL = "https://api.s.unit.sh"

# Fixtures are copied from Unit's documentation:
#   https://unit.co/docs/api/payments/wires/api/
#   https://unit.co/docs/api/payments/wires/resources/
#   https://unit.co/docs/api/payments/wires/simulations/
#   https://unit.co/docs/api/payments/wires/rejections-and-returns/
#   https://unit.co/docs/api/events/
#   https://unit.co/docs/api/resources/ (Returned Wire Transaction)
# A fixture that is not a verbatim copy says how it differs. None of them has been checked against a live Unit
# response, so these tests prove the SDK matches the documentation and nothing more.

COUNTERPARTY = {
    "name": "April Oniel",
    "routingNumber": "812345678",
    "accountNumber": "1000000001",
    "address": {
        "street": "20 Ingram St",
        "city": "Forest Hills",
        "state": "CA",
        "postalCode": "11375",
        "country": "US",
    },
}

CREATE_REQUEST = {
    "data": {
        "type": "wirePayment",
        "attributes": {
            "amount": 200,
            "direction": "Credit",
            "description": "Wire payment",
            "counterparty": COUNTERPARTY,
        },
        "relationships": {"account": {"data": {"type": "depositAccount", "id": "10000"}}},
    }
}

CREATE_RESPONSE = {
    "data": {
        "type": "wirePayment",
        "id": "1135",
        "attributes": {
            "createdAt": "2021-08-30T12:19:18.639Z",
            "amount": 200,
            "direction": "Credit",
            "description": "Wire payment",
            "counterparty": COUNTERPARTY,
            "status": "Pending",
        },
        "relationships": {
            "account": {"data": {"type": "account", "id": "10000"}},
            "customer": {"data": {"type": "customer", "id": "10000"}},
            "customers": {"data": [{"type": "customer", "id": "10000"}]},
            "transaction": {"data": {"type": "transaction", "id": "4"}},
        },
    }
}

SENT_RESOURCE = {
    "data": {
        "type": "wirePayment",
        "id": "3",
        "attributes": {
            "createdAt": "2021-10-05T06:33:45.035Z",
            "amount": 200,
            "direction": "Credit",
            "description": "Wire payment",
            "counterparty": COUNTERPARTY,
            "status": "Sent",
            "imadOmad": {"imad": "123456", "omad": "654321"},
        },
        "relationships": {
            "account": {"data": {"type": "account", "id": "10000"}},
            "customer": {"data": {"type": "customer", "id": "10000"}},
            "customers": {"data": [{"type": "customer", "id": "10000"}]},
            "transaction": {"data": {"type": "transaction", "id": "1"}},
        },
    }
}

CANCEL_RESPONSE = {
    "data": {
        "type": "wirePayment",
        "id": "1483",
        "attributes": {
            "createdAt": "2024-12-13T16:18:07.654Z",
            "amount": 100,
            "direction": "Credit",
            "description": "Wire",
            "counterparty": COUNTERPARTY,
            "status": "Canceled",
        },
        "relationships": {
            "account": {"data": {"type": "account", "id": "10000"}},
            "customer": {"data": {"type": "customer", "id": "10000"}},
            "customers": {"data": [{"type": "customer", "id": "10000"}]},
            "transaction": {"data": {"type": "transaction", "id": "260"}},
            "org": {"data": {"type": "org", "id": "1"}},
            "bank": {"data": {"type": "bank", "id": "1"}},
        },
    }
}

# The ACH item is the documented List response example. The wire item is the create response with a rejection
# reason added: the docs say reason is optional on a wirePayment and list the wire rejection reasons.
REJECTED_WIRE = copy.deepcopy(CREATE_RESPONSE["data"])
REJECTED_WIRE["id"] = "1136"
REJECTED_WIRE["attributes"]["status"] = "Rejected"
REJECTED_WIRE["attributes"]["reason"] = "Invalid Routing Number"

LIST_RESPONSE = {
    "data": [
        {
            "type": "achPayment",
            "id": "50",
            "attributes": {
                "createdAt": "2020-01-13T16:01:19.346Z",
                "status": "Pending",
                "counterparty": {
                    "routingNumber": "812345678",
                    "accountNumber": "12345569",
                    "accountType": "Checking",
                    "name": "Jane Doe",
                },
                "description": "Funding",
                "direction": "Credit",
                "amount": 10000,
            },
            "relationships": {
                "account": {"data": {"type": "depositAccount", "id": "555"}},
                "customer": {"data": {"type": "individualCustomer", "id": "99823"}},
                "counterparty": {"data": {"type": "counterparty", "id": "4567"}},
                "transaction": {"data": {"type": "transaction", "id": "4003"}},
            },
        },
        CREATE_RESPONSE["data"],
        REJECTED_WIRE,
    ],
    "meta": {"pagination": {"total": 3, "limit": 100, "offset": 0}},
}

SANDBOX_INCOMING_REQUEST = {
    "data": {
        "type": "wirePayment",
        "attributes": {"amount": 10000, "description": "Wire Payment from Sandbox"},
        "relationships": {"account": {"data": {"type": "depositAccount", "id": "10001"}}},
    }
}

SANDBOX_INCOMING_RESPONSE = {
    "data": {
        "type": "wirePayment",
        "id": "108",
        "attributes": {
            "createdAt": "2021-02-24T11:31:10.009Z",
            "amount": 10000,
            "description": "Wire Payment from Sandbox",
        },
        "relationships": {
            "account": {"data": {"type": "depositAccount", "id": "10001"}},
            "customer": {"data": {"type": "customer", "id": "10000"}},
        },
    }
}

SANDBOX_TRANSMIT_REQUEST = {
    "data": {
        "type": "transmitWirePayment",
        "relationships": {"payment": {"data": {"type": "FedWirePayment", "id": "2"}}},
    }
}

SANDBOX_TRANSMIT_RESPONSE = {
    "data": {
        "type": "wirePayment",
        "id": "2",
        "attributes": {
            "createdAt": "2021-09-15T10:23:56.716Z",
            "amount": 200,
            "description": "Wire payment",
        },
        "relationships": {
            "account": {"data": {"type": "depositAccount", "id": "10000"}},
            "customer": {"data": {"type": "customer", "id": "10000"}},
        },
    }
}

# The docs example has no description, which the docs mark as optional.
WIRE_TRANSACTION = {
    "type": "wireTransaction",
    "id": "9547",
    "attributes": {
        "createdAt": "2020-07-05T15:49:36.864Z",
        "direction": "Credit",
        "amount": 1000,
        "balance": 12000,
        "summary": "Wire to Jane Smith",
        "imadOmad": {"imad": "123456", "omad": "654321"},
        "counterparty": {
            "name": "Jane Smith",
            "routingNumber": "812345678",
            "accountNumber": "10039",
            "accountType": "Checking",
        },
    },
    "relationships": {
        "account": {"data": {"type": "depositAccount", "id": "10035"}},
        "customer": {"data": {"type": "customer", "id": "5"}},
    },
}

RETURNED_WIRE_TRANSACTION = {
    "data": {
        "type": "returnedWireTransaction",
        "id": "265",
        "attributes": {
            "createdAt": "2021-06-06T07:23:30.101Z",
            "amount": 200,
            "direction": "Debit",
            "balance": 3716500,
            "summary": "Returned due to: NAMEMISSMATCH |  420 E Polk St., Phoenix, AZ -Part Commission",
            "reason": "Insufficient Funds",
            "imad": "123456",
            "omad": "654321",
        },
        "relationships": {
            "account": {"data": {"type": "account", "id": "10001"}},
            "customer": {"data": {"type": "customer", "id": "10000"}},
            "payment": {"data": {"type": "payment", "id": "122"}},
        },
    }
}


def event_relationships(payment_id, account_id, customer_id):
    return {
        "payment": {"data": {"id": payment_id, "type": "payment"}},
        "account": {"data": {"id": account_id, "type": "account"}},
        "customer": {"data": {"id": customer_id, "type": "customer"}},
    }


PAYMENT_CREATED_EVENT = {
    "id": "4132",
    "type": "payment.created",
    "attributes": {
        "createdAt": "2021-12-27T12:12:39.133Z",
        "status": "Pending",
        "direction": "Credit",
        "amount": 2500,
        "tags": {"tag": "value"},
    },
    "relationships": event_relationships("6", "10009", "10002"),
}

PAYMENT_SENT_EVENT = {
    "id": "291",
    "type": "payment.sent",
    "attributes": {
        "previousStatus": "Pending",
        "direction": "Credit",
        "amount": 2500,
        "available": 500,
        "createdAt": "2020-11-08T18:34:38.533Z",
        "tags": {"tag": "value"},
    },
    "relationships": event_relationships("8", "10009", "10002"),
}

PAYMENT_REJECTED_EVENT = {
    "id": "291",
    "type": "payment.rejected",
    "attributes": {
        "createdAt": "2021-12-08T18:34:38.533Z",
        "reason": "InsufficientFunds",
        "direction": "Credit",
        "amount": 2500,
        "tags": {"tag": "value"},
    },
    "relationships": event_relationships("6", "10009", "10002"),
}

# The documented payment.returned example carries an ACH R-code in reason and returnReason. The docs say neither
# is sent for wire returns, so they are removed here.
PAYMENT_RETURNED_WIRE_EVENT = {
    "id": "295",
    "type": "payment.returned",
    "attributes": {
        "previousStatus": "Sent",
        "createdAt": "2021-01-02T13:38:28.223Z",
        "direction": "Credit",
        "amount": 2500,
        "available": 3000,
        "tags": {"tag": "value"},
    },
    "relationships": event_relationships("10", "10009", "10002"),
}

# The docs describe payment.pendingReview for ACH payments. The wire workflow guide and the cancel endpoint docs
# describe a PendingReview wire status but no wire event for it, so this shape is the general documented one.
PAYMENT_PENDING_REVIEW_EVENT = {
    "id": "295",
    "type": "payment.pendingReview",
    "attributes": {
        "createdAt": "2021-01-02T13:38:28.223Z",
        "direction": "Credit",
        "amount": 2500,
        "tags": {"tag": "value"},
    },
    "relationships": event_relationships("10", "10009", "10002"),
}

ASSIGNMENT_CREATED_EVENT = {
    "id": "260",
    "type": "assignment.created",
    "attributes": {"createdAt": "2025-03-22T21:35:58.898Z", "assignee": "Org"},
    "relationships": {
        "assignment": {"data": {"id": "10000", "type": "generalReviewAssignment"}},
        "payment": {"data": {"id": "10000", "type": "wirePayment"}},
    },
}

ASSIGNMENT_ESCALATED_EVENT = {
    "id": "260",
    "type": "assignment.escalated",
    "attributes": {"createdAt": "2025-03-22T21:35:58.898Z", "assignee": "Org"},
    "relationships": {
        "assignment": {"data": {"id": "10000", "type": "generalReviewAssignment"}},
        "checkDeposit": {"data": {"id": "10000", "type": "checkDeposit"}},
    },
}

# The statuses come from the wirePayment resource page and the list filter, the cancel endpoint, and the wire
# workflow guide. The pages disagree on which statuses exist, so the SDK has to accept all of them.
DOCUMENTED_STATUSES = ["Pending", "PendingReview", "Clearing", "Sent", "Canceled", "Rejected", "Returned"]


def wire_counterparty(street2=None):
    return WireCounterparty(
        routing_number="812345678",
        account_number="1000000001",
        name="April Oniel",
        address=Address(
            street="20 Ingram St",
            street2=street2,
            city="Forest Hills",
            state="CA",
            postal_code="11375",
            country="US",
        ),
    )


def create_request(**kwargs):
    return CreateWirePaymentRequest(
        amount=200,
        description="Wire payment",
        counterparty=wire_counterparty(),
        relationships={"account": Relationship("depositAccount", "10000")},
        **kwargs,
    )


def encode(request):
    return json.loads(json.dumps(request.to_json_api(), cls=UnitEncoder))


def mock_response(status_code, body):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = body
    return response


class TestWirePaymentEncoding(unittest.TestCase):
    def test_create_request_matches_documented_body(self):
        request = create_request(idempotency_key=None, tags=None)

        self.assertEqual(encode(request), CREATE_REQUEST)

    def test_create_request_counterparty_has_no_account_type(self):
        counterparty = encode(create_request())["data"]["attributes"]["counterparty"]

        self.assertEqual(
            set(counterparty), {"name", "routingNumber", "accountNumber", "address"}
        )

    def test_create_request_idempotency_key_and_tags_are_optional(self):
        attributes = encode(create_request())["data"]["attributes"]

        self.assertNotIn("idempotencyKey", attributes)
        self.assertNotIn("tags", attributes)

    def test_create_request_includes_idempotency_key_and_tags(self):
        request = create_request(idempotency_key="key-1", tags={"purpose": "payroll"})

        attributes = encode(request)["data"]["attributes"]

        self.assertEqual(attributes["idempotencyKey"], "key-1")
        self.assertEqual(attributes["tags"], {"purpose": "payroll"})

    def test_create_request_includes_street2_only_when_set(self):
        request = CreateWirePaymentRequest(
            amount=200,
            description="Wire payment",
            counterparty=wire_counterparty(street2="Suite 4"),
            relationships={"account": Relationship("depositAccount", "10000")},
        )

        address = encode(request)["data"]["attributes"]["counterparty"]["address"]

        self.assertEqual(address["street2"], "Suite 4")
        self.assertNotIn(
            "street2", encode(create_request())["data"]["attributes"]["counterparty"]["address"]
        )

    @patch("unit.api.base_resource.requests.post")
    def test_payments_create_posts_documented_body_and_decodes_response(self, mock_post):
        mock_post.return_value = mock_response(201, CREATE_RESPONSE)

        resource = PaymentResource(api_url=API_URL, token="token")
        response = resource.create(create_request(), timeout=5)

        self.assertEqual(mock_post.call_args.args, (f"{API_URL}/payments",))
        self.assertEqual(json.loads(mock_post.call_args.kwargs["data"]), CREATE_REQUEST)
        self.assertEqual(mock_post.call_args.kwargs["timeout"], 5)
        self.assertIsInstance(response, UnitResponse)
        self.assertIsInstance(response.data, WirePaymentDTO)
        self.assertEqual(response.data.id, "1135")

    def test_list_params_filter_wire_payments_by_status(self):
        params = ListPaymentParams(type=["Wire"], status=["Pending", "PendingReview"])

        self.assertEqual(
            params.to_dict(),
            {
                "page[limit]": 100,
                "page[offset]": 0,
                "filter[type][0]": "Wire",
                "filter[status][0]": "Pending",
                "filter[status][1]": "PendingReview",
            },
        )


class TestWirePaymentDecoding(unittest.TestCase):
    def test_create_response_round_trips(self):
        dto = DtoDecoder.decode(CREATE_RESPONSE["data"])

        self.assertIsInstance(dto, WirePaymentDTO)
        self.assertEqual(dto.id, "1135")
        self.assertEqual(dto.type, "wirePayment")
        self.assertEqual(dto.attributes["status"], "Pending")
        self.assertEqual(dto.attributes["amount"], 200)
        self.assertEqual(dto.attributes["direction"], "Credit")
        self.assertEqual(dto.attributes["description"], "Wire payment")
        self.assertEqual(
            dto.attributes["createdAt"],
            datetime(2021, 8, 30, 12, 19, 18, 639000, tzinfo=timezone.utc),
        )
        self.assertIsNone(dto.attributes["tags"])
        self.assertIsNone(dto.attributes["reason"])
        self.assertIsNone(dto.attributes["imadOmad"])

        counterparty = dto.attributes["counterparty"]
        self.assertIsInstance(counterparty, WireCounterparty)
        self.assertEqual(counterparty.name, "April Oniel")
        self.assertEqual(counterparty.routing_number, "812345678")
        self.assertEqual(counterparty.account_number, "1000000001")
        self.assertEqual(counterparty.address.street, "20 Ingram St")
        self.assertEqual(counterparty.address.city, "Forest Hills")
        self.assertEqual(counterparty.address.state, "CA")
        self.assertEqual(counterparty.address.postal_code, "11375")
        self.assertEqual(counterparty.address.country, "US")

        self.assertEqual(dto.relationships["account"].id, "10000")
        self.assertEqual(dto.relationships["customer"].id, "10000")
        self.assertEqual(dto.relationships["transaction"].type, "transaction")
        self.assertEqual(dto.relationships["transaction"].id, "4")

    def test_sent_payment_keeps_imad_omad(self):
        dto = DtoDecoder.decode(SENT_RESOURCE["data"])

        self.assertEqual(dto.attributes["status"], "Sent")
        self.assertEqual(dto.attributes["imadOmad"], {"imad": "123456", "omad": "654321"})

    def test_canceled_payment_with_org_and_bank_relationships(self):
        dto = DtoDecoder.decode(CANCEL_RESPONSE["data"])

        self.assertEqual(dto.attributes["status"], "Canceled")
        self.assertEqual(dto.relationships["org"].id, "1")
        self.assertEqual(dto.relationships["bank"].type, "bank")

    def test_rejected_payment_keeps_reason(self):
        dto = DtoDecoder.decode(REJECTED_WIRE)

        self.assertEqual(dto.attributes["status"], "Rejected")
        self.assertEqual(dto.attributes["reason"], "Invalid Routing Number")

    def test_every_documented_status_decodes(self):
        for status in DOCUMENTED_STATUSES:
            with self.subTest(status=status):
                payload = copy.deepcopy(CREATE_RESPONSE["data"])
                payload["attributes"]["status"] = status

                dto = DtoDecoder.decode(payload)

                self.assertIsInstance(dto, WirePaymentDTO)
                self.assertEqual(dto.attributes["status"], status)

    def test_unknown_status_and_unknown_fields_do_not_raise(self):
        payload = copy.deepcopy(CREATE_RESPONSE["data"])
        payload["attributes"]["status"] = "SomeFutureStatus"
        payload["attributes"]["someFutureField"] = {"nested": [1, 2]}
        payload["attributes"]["counterparty"]["someFutureField"] = "x"
        payload["attributes"]["counterparty"]["address"]["someFutureField"] = "x"
        payload["relationships"]["someFutureRelationship"] = {
            "data": {"type": "future", "id": "9"}
        }

        dto = DtoDecoder.decode(payload)

        self.assertIsInstance(dto, WirePaymentDTO)
        self.assertEqual(dto.attributes["status"], "SomeFutureStatus")
        self.assertEqual(dto.relationships["someFutureRelationship"].id, "9")

    def test_tags_are_decoded(self):
        payload = copy.deepcopy(CREATE_RESPONSE["data"])
        payload["attributes"]["tags"] = {"transaction_id": "abc"}

        dto = DtoDecoder.decode(payload)

        self.assertEqual(dto.attributes["tags"], {"transaction_id": "abc"})

    @patch("unit.api.base_resource.requests.get")
    def test_payments_get_decodes_wire_payment(self, mock_get):
        mock_get.return_value = mock_response(200, SENT_RESOURCE)

        resource = PaymentResource(api_url=API_URL, token="token")
        response = resource.get("3")

        self.assertEqual(mock_get.call_args.args, (f"{API_URL}/payments/3",))
        self.assertIsInstance(response.data, WirePaymentDTO)
        self.assertEqual(response.data.attributes["status"], "Sent")

    @patch("unit.api.base_resource.requests.get")
    def test_payments_list_decodes_wire_payments_beside_ach(self, mock_get):
        mock_get.return_value = mock_response(200, LIST_RESPONSE)

        resource = PaymentResource(api_url=API_URL, token="token")
        response = resource.list(params=ListPaymentParams(type=["Wire"]))

        self.assertEqual(
            [type(item) for item in response.data],
            [AchPaymentDTO, WirePaymentDTO, WirePaymentDTO],
        )
        self.assertEqual(response.data[0].attributes["counterparty"]["accountType"], "Checking")
        self.assertEqual(response.data[1].attributes["status"], "Pending")
        self.assertEqual(response.data[2].attributes["status"], "Rejected")

    @patch("unit.api.base_resource.requests.post")
    def test_payments_cancel_decodes_wire_payment(self, mock_post):
        mock_post.return_value = mock_response(200, CANCEL_RESPONSE)

        resource = PaymentResource(api_url=API_URL, token="token")
        response = resource.cancel("1483")

        self.assertEqual(mock_post.call_args.args, (f"{API_URL}/payments/1483/cancel",))
        self.assertIsInstance(response.data, WirePaymentDTO)
        self.assertEqual(response.data.attributes["status"], "Canceled")


class TestWireTransactionDecoding(unittest.TestCase):
    def test_wire_transaction_without_description_decodes(self):
        dto = DtoDecoder.decode(WIRE_TRANSACTION)

        self.assertIsInstance(dto, WireTransactionDTO)
        self.assertEqual(dto.attributes["amount"], 1000)
        self.assertIsNone(dto.attributes["description"])
        self.assertEqual(dto.attributes["counterparty"].name, "Jane Smith")

    def test_returned_wire_transaction_decodes(self):
        dto = DtoDecoder.decode(RETURNED_WIRE_TRANSACTION["data"])

        self.assertIsInstance(dto, ReturnedWireTransactionDTO)
        self.assertEqual(dto.type, "returnedWireTransaction")
        self.assertEqual(dto.attributes["direction"], "Debit")
        self.assertEqual(dto.attributes["amount"], 200)
        self.assertEqual(dto.attributes["balance"], 3716500)
        self.assertEqual(dto.attributes["reason"], "Insufficient Funds")
        self.assertEqual(dto.attributes["imad"], "123456")
        self.assertEqual(dto.attributes["omad"], "654321")
        self.assertEqual(dto.relationships["payment"].id, "122")

    def test_returned_wire_transaction_without_omad_decodes(self):
        payload = copy.deepcopy(RETURNED_WIRE_TRANSACTION["data"])
        del payload["attributes"]["omad"]

        dto = DtoDecoder.decode(payload)

        self.assertIsNone(dto.attributes["omad"])


class TestWireEventDecoding(unittest.TestCase):
    def test_payment_created_event(self):
        event = DtoDecoder.decode([PAYMENT_CREATED_EVENT])[0]

        self.assertIsInstance(event, PaymentCreatedEvent)
        self.assertEqual(event.attributes["status"], "Pending")
        self.assertEqual(event.attributes["tags"], {"tag": "value"})
        self.assertEqual(event.relationships["payment"].id, "6")

    def test_payment_sent_event(self):
        event = DtoDecoder.decode([PAYMENT_SENT_EVENT])[0]

        self.assertIsInstance(event, PaymentSentEvent)
        self.assertEqual(event.attributes["previousStatus"], "Pending")
        self.assertEqual(event.relationships["payment"].id, "8")

    def test_payment_rejected_event(self):
        event = DtoDecoder.decode([PAYMENT_REJECTED_EVENT])[0]

        self.assertIsInstance(event, PaymentRejectedEvent)
        self.assertEqual(event.attributes["reason"], "InsufficientFunds")

    def test_payment_returned_event_without_reason(self):
        event = DtoDecoder.decode([PAYMENT_RETURNED_WIRE_EVENT])[0]

        self.assertIsInstance(event, PaymentReturnedEvent)
        self.assertEqual(event.attributes["previousStatus"], "Sent")
        self.assertEqual(event.relationships["payment"].id, "10")

    def test_payment_pending_review_event(self):
        event = DtoDecoder.decode([PAYMENT_PENDING_REVIEW_EVENT])[0]

        self.assertIsInstance(event, PaymentPendingReviewEvent)
        self.assertEqual(event.type, "payment.pendingReview")
        self.assertEqual(
            event.attributes["createdAt"],
            datetime(2021, 1, 2, 13, 38, 28, 223000, tzinfo=timezone.utc),
        )
        self.assertEqual(event.attributes["tags"], {"tag": "value"})
        self.assertEqual(event.relationships["payment"].id, "10")
        self.assertEqual(event.relationships["account"].id, "10009")

    def test_assignment_created_event_for_a_wire_payment(self):
        event = DtoDecoder.decode([ASSIGNMENT_CREATED_EVENT])[0]

        self.assertIsInstance(event, AssignmentCreatedEvent)
        self.assertEqual(event.type, "assignment.created")
        self.assertEqual(event.attributes["assignee"], "Org")
        self.assertIsNone(event.attributes["tags"])
        self.assertEqual(event.relationships["assignment"].type, "generalReviewAssignment")
        self.assertEqual(event.relationships["payment"].type, "wirePayment")
        self.assertEqual(event.relationships["payment"].id, "10000")

    def test_assignment_escalated_event(self):
        event = DtoDecoder.decode([ASSIGNMENT_ESCALATED_EVENT])[0]

        self.assertIsInstance(event, AssignmentEscalatedEvent)
        self.assertEqual(event.type, "assignment.escalated")
        self.assertEqual(event.attributes["assignee"], "Org")
        self.assertEqual(event.relationships["assignment"].id, "10000")
        self.assertEqual(event.relationships["checkDeposit"].id, "10000")

    def test_new_events_ignore_unknown_attributes(self):
        for payload in [
            PAYMENT_PENDING_REVIEW_EVENT,
            ASSIGNMENT_CREATED_EVENT,
            ASSIGNMENT_ESCALATED_EVENT,
        ]:
            with self.subTest(type=payload["type"]):
                payload = copy.deepcopy(payload)
                payload["attributes"]["someFutureField"] = "x"

                event = DtoDecoder.decode([payload])[0]

                self.assertEqual(event.type, payload["type"])


class TestWireSandboxSimulations(unittest.TestCase):
    def test_incoming_request_matches_documented_body(self):
        request = SimulateIncomingWireRequest(
            amount=10000,
            description="Wire Payment from Sandbox",
            relationships={"account": Relationship("depositAccount", "10001")},
        )

        self.assertEqual(encode(request), SANDBOX_INCOMING_REQUEST)

    def test_transmit_request_matches_documented_body(self):
        request = SimulateTransmitWireRequest(payment_id="2")

        self.assertEqual(encode(request), SANDBOX_TRANSMIT_REQUEST)

    @patch("unit.api.base_resource.requests.post")
    def test_simulate_incoming_posts_to_sandbox_wire_payments(self, mock_post):
        mock_post.return_value = mock_response(201, SANDBOX_INCOMING_RESPONSE)

        resource = WireResource(api_url=API_URL, token="token")
        response = resource.simulate_incoming(
            SimulateIncomingWireRequest(
                amount=10000,
                description="Wire Payment from Sandbox",
                relationships={"account": Relationship("depositAccount", "10001")},
            ),
            timeout=5,
        )

        self.assertEqual(mock_post.call_args.args, (f"{API_URL}/sandbox/wire-payments",))
        self.assertEqual(
            json.loads(mock_post.call_args.kwargs["data"]), SANDBOX_INCOMING_REQUEST
        )
        self.assertEqual(mock_post.call_args.kwargs["timeout"], 5)
        self.assertIsInstance(response.data, WirePaymentDTO)
        self.assertEqual(response.data.id, "108")
        self.assertEqual(response.data.attributes["amount"], 10000)
        self.assertIsNone(response.data.attributes["status"])
        self.assertIsNone(response.data.attributes["counterparty"])
        self.assertEqual(response.data.relationships["account"].id, "10001")

    @patch("unit.api.base_resource.requests.post")
    def test_simulate_transmit_posts_to_sandbox_wire_transmit(self, mock_post):
        mock_post.return_value = mock_response(200, SANDBOX_TRANSMIT_RESPONSE)

        resource = WireResource(api_url=API_URL, token="token")
        response = resource.simulate_transmit(SimulateTransmitWireRequest(payment_id="2"))

        self.assertEqual(mock_post.call_args.args, (f"{API_URL}/sandbox/wire/transmit",))
        self.assertEqual(
            json.loads(mock_post.call_args.kwargs["data"]), SANDBOX_TRANSMIT_REQUEST
        )
        self.assertIsInstance(response.data, WirePaymentDTO)
        self.assertEqual(response.data.id, "2")

    @patch("unit.api.base_resource.requests.post")
    def test_simulate_transmit_returns_unit_error(self, mock_post):
        mock_post.return_value = mock_response(
            404, {"errors": [{"title": "Not Found", "status": "404"}]}
        )

        resource = WireResource(api_url=API_URL, token="token")
        response = resource.simulate_transmit(SimulateTransmitWireRequest(payment_id="2"))

        self.assertIsInstance(response, UnitError)
        self.assertEqual(response.errors[0].status, "404")
