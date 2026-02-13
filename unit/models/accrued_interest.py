from typing import Optional
from unit.models import *


class AccruedInterestTotalDTO(object):
    def __init__(self, id: str, amount: int,
                 relationships: Optional[Dict[str, Relationship]]):
        self.id = id
        self.type = "accruedInterestTotal"
        self.attributes = {"amount": amount}
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return AccruedInterestTotalDTO(_id, attributes["amount"], relationships)


class GetAccruedInterestTotalParams(UnitParams):
    def __init__(self, account_id: Optional[str] = None,
                 since: Optional[str] = None, until: Optional[str] = None,
                 since_interest_month: Optional[str] = None,
                 until_interest_month: Optional[str] = None):
        self.account_id = account_id
        self.since = since
        self.until = until
        self.since_interest_month = since_interest_month
        self.until_interest_month = until_interest_month

    def to_dict(self) -> Dict:
        parameters = {}
        if self.account_id:
            parameters["filter[accountId]"] = self.account_id
        if self.since:
            parameters["filter[since]"] = self.since
        if self.until:
            parameters["filter[until]"] = self.until
        if self.since_interest_month:
            parameters["filter[sinceInterestMonth]"] = self.since_interest_month
        if self.until_interest_month:
            parameters["filter[untilInterestMonth]"] = self.until_interest_month
        return parameters
