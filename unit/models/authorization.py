import json
from typing import Optional
from unit.models import *
from unit.utils import date_utils

AuthorizationStatus = Literal["Authorized", "Completed", "Canceled", "Declined"]


class AuthorizationDTO(object):
    def __init__(
        self,
        id: str,
        created_at: datetime,
        amount: int,
        card_last_4_digits: str,
        status: AuthorizationStatus,
        merchant: Merchant,
        recurring: bool,
        relationships: Optional[Dict[str, Relationship]] = None,
        tags: Optional[Dict[str, str]] = None,
        decline_reason: Optional[str] = None,
        decline_description: Optional[str] = None,
        declined_by: Optional[str] = None,
        payment_method: Optional[str] = None,
        digital_wallet: Optional[str] = None,
        card_verification_data: Optional[CardVerificationData] = None,
        card_network: Optional[str] = None,
        cash_withdrawal_amount: Optional[int] = None,
        summary: Optional[str] = None,
        rich_merchant_data: Optional[RichMerchantData] = None,
        currency_conversion: Optional[CurrencyConversion] = None,
    ):
        self.id = id
        self.type = "authorization"
        self.attributes = {
            "createdAt": created_at,
            "amount": amount,
            "cardLast4Digits": card_last_4_digits,
            "status": status,
            "merchant": merchant,
            "recurring": recurring,
            "tags": tags,
            "declineReason": decline_reason,
            "declineDescription": decline_description,
            "declinedBy": declined_by,
            "paymentMethod": payment_method,
            "digitalWallet": digital_wallet,
            "cardVerificationData": card_verification_data,
            "cardNetwork": card_network,
            "cashWithdrawalAmount": cash_withdrawal_amount,
            "summary": summary,
            "richMerchantData": rich_merchant_data,
            "currencyConversion": currency_conversion,
        }
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return AuthorizationDTO(
            id=_id,
            created_at=date_utils.to_datetime(attributes["createdAt"]),
            amount=attributes["amount"],
            card_last_4_digits=attributes["cardLast4Digits"],
            status=attributes["status"],
            merchant=Merchant.from_json_api(attributes["merchant"]),
            recurring=attributes["recurring"],
            relationships=relationships,
            tags=attributes.get("tags"),
            decline_reason=attributes.get("declineReason"),
            decline_description=attributes.get("declineDescription"),
            declined_by=attributes.get("declinedBy"),
            payment_method=attributes.get("paymentMethod"),
            digital_wallet=attributes.get("digitalWallet"),
            card_verification_data=CardVerificationData.from_json_api(
                attributes.get("cardVerificationData")
            ),
            card_network=attributes.get("cardNetwork"),
            cash_withdrawal_amount=attributes.get("cashWithdrawalAmount"),
            summary=attributes.get("summary"),
            rich_merchant_data=RichMerchantData.from_json_api(
                attributes.get("richMerchantData")
            ),
            currency_conversion=CurrencyConversion.from_json_api(
                attributes.get("currencyConversion")
            ),
        )


class ListAuthorizationParams(UnitParams):
    def __init__(self, limit: int = 100, offset: int = 0, account_id: Optional[str] = None,
                 customer_id: Optional[str] = None, card_id: Optional[str] = None, since: Optional[str] = None,
                 until: Optional[str] = None, include_non_authorized: Optional[bool] = False,
                 status: Optional[str] = None, sort: Optional[Literal["createdAt", "-createdAt"]] = None):
        self.limit = limit
        self.offset = offset
        self.account_id = account_id
        self.customer_id = customer_id
        self.card_id = card_id
        self.since = since
        self.until = until
        self.include_non_authorized = include_non_authorized
        self.status = status
        self.sort = sort

    def to_dict(self) -> Dict:
        parameters = {"page[limit]": self.limit, "page[offset]": self.offset}
        if self.customer_id:
            parameters["filter[customerId]"] = self.customer_id
        if self.account_id:
            parameters["filter[accountId]"] = self.account_id
        if self.card_id:
            parameters["filter[cardId]"] = self.card_id
        if self.include_non_authorized:
            parameters["filter[includeNonAuthorized]"] = self.include_non_authorized
        if self.status:
            parameters["filter[status]"] = self.status
        if self.since:
            parameters["filter[since]"] = self.since
        if self.until:
            parameters["filter[until]"] = self.until
        if self.sort:
            parameters["sort"] = self.sort
        return parameters
