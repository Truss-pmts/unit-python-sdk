from unit.models.event import (
    AuthorizationDeclinedEvent,
    AuthorizationRequestDeclinedEvent,
)

_CREATED_AT = "2020-05-01T00:00:00.000Z"
_MERCHANT = {"name": "Merchant", "type": 5411}


def test_authorization_declined_event_parses_decline_description():
    attributes = {
        "createdAt": _CREATED_AT,
        "amount": 4000,
        "cardLast4Digits": "0019",
        "reason": "DoNotHonor",
        "declineDescription": "Card expired",
        "recurring": False,
        "merchant": _MERCHANT,
    }
    event = AuthorizationDeclinedEvent.from_json_api(
        "1", "authorization.declined", attributes, {}
    )
    assert event.attributes["declineDescription"] == "Card expired"


def test_authorization_declined_event_decline_description_defaults_to_none():
    attributes = {
        "createdAt": _CREATED_AT,
        "amount": 4000,
        "cardLast4Digits": "0019",
        "reason": "DoNotHonor",
        "recurring": False,
        "merchant": _MERCHANT,
    }
    event = AuthorizationDeclinedEvent.from_json_api(
        "1", "authorization.declined", attributes, {}
    )
    assert event.attributes["declineDescription"] is None


def test_authorization_request_declined_event_parses_decline_description():
    attributes = {
        "createdAt": _CREATED_AT,
        "amount": 4000,
        "status": "Declined",
        "declineReason": "DoNotHonor",
        "declineDescription": "Card not activated",
        "partialApprovalAllowed": False,
        "recurring": False,
        "merchant": _MERCHANT,
    }
    event = AuthorizationRequestDeclinedEvent.from_json_api(
        "1", "authorizationRequest.declined", attributes, {}
    )
    assert event.attributes["declineDescription"] == "Card not activated"
