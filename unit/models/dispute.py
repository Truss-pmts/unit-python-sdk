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
        dispute_type: Optional[str],
        created_at: datetime,
        amount: int,
        decision_reason: Optional[str],
        relationships: Optional[Dict[str, Relationship]],
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.type = "dispute"
        self.attributes = {
            "createdAt": created_at,
            "updatedAt": updated_at,
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
            id=_id,
            source=attributes["source"],
            status_history=attributes["statusHistory"],
            status=attributes["status"],
            description=attributes["description"],
            dispute_type=attributes.get("disputeType"),
            created_at=date_utils.to_datetime(attributes["createdAt"]),
            amount=attributes["amount"],
            decision_reason=attributes.get("decisionReason"),
            relationships=relationships,
            updated_at=date_utils.to_datetime(attributes.get("updatedAt")) if attributes.get("updatedAt") else None,
        )
