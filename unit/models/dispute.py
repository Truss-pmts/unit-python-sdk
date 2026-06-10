import json

from unit.utils import date_utils
from unit.models import *

DisputeStatus = Literal[
    "InvestigationStarted",
    "ProvisionallyCredited",
    "Denied",
    "ResolvedLost",
    "ResolvedWon",
]


class DisputeDTO(object):
    def __init__(
        self,
        id: str,
        source: str,
        status_history: List[Dict[str, str]],
        status: DisputeStatus,
        description: str,
        dispute_type: str,
        created_at: datetime,
        amount: int,
        decision_reason: Optional[str],
        relationships: Optional[Dict[str, Relationship]],
    ):
        self.id = id
        self.type = "dispute"
        self.attributes = {
            "createdAt": created_at,
            "source": source,
            "statusHistory": status_history,
            "status": status,
            "description": description,
            "disputeType": dispute_type,
            "amount": amount,
            "decisionReason": decision_reason,
        }
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return DisputeDTO(
            _id,
            date_utils.to_datetime(attributes["createdAt"]),
            attributes["source"],
            attributes["statusHistory"],
            attributes["status"],
            attributes["description"],
            attributes["disputeType"],
            attributes["amount"],
            attributes.get("decisionReason"),
            relationships,
        )


class SimulateDisputeRequest(UnitRequest):
    def __init__(self, account_id: str, transaction_id: str, amount: Optional[int] = None):
        self.account_id = account_id
        self.transaction_id = transaction_id
        self.amount = amount

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "dispute",
                "attributes": {},
                "relationships": {
                    "account": {
                        "data": {
                            "type": "account",
                            "id": self.account_id
                        }
                    },
                    "transaction": {
                        "data": {
                            "type": "transaction",
                            "id": self.transaction_id
                        }
                    }
                }
            }
        }

        if self.amount is not None:
            payload["data"]["attributes"]["amount"] = self.amount

        return payload

    def __repr__(self):
        return json.dumps(self.to_json_api())
