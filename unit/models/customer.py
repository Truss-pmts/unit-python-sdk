from unit.utils import date_utils
from unit.models import *

ArchiveReason = Literal["Inactive", "FraudACHActivity", "FraudCardActivity", "FraudCheckActivity",
                        "FraudApplicationHistory", "FraudAccountActivity", "FraudClientIdentified"]

CustomerStatus = Literal["Active", "Archived"]

class IndividualCustomerDTO(object):
    def __init__(self, id: str, created_at: datetime, full_name: FullName, date_of_birth: date, address: Address,
                 phone: Phone, email: str, ssn: Optional[str], passport: Optional[str], nationality: Optional[str],
                 authorized_users: [AuthorizedUser], tags: Optional[Dict[str, str]],
                 relationships: Optional[Dict[str, Relationship]], status: CustomerStatus,
                 archive_reason: Optional[ArchiveReason], eligible_products: Optional[List[str]] = None,
                 ein: Optional[str] = None):
        self.id = id
        self.type = 'individualCustomer'
        self.attributes = {"createdAt": created_at, "fullName": full_name, "dateOfBirth": date_of_birth,
                           "address": address, "phone": phone, "email": email, "ssn": ssn, "passport": passport,
                           "nationality": nationality, "ein": ein, "authorizedUsers": authorized_users,
                           "eligibleProducts": eligible_products, "tags": tags,
                           "status": status, "archiveReason": archive_reason}
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return IndividualCustomerDTO(
            id=_id, created_at=date_utils.to_datetime(attributes["createdAt"]),
            full_name=FullName.from_json_api(attributes["fullName"]),
            date_of_birth=date_utils.to_date(attributes["dateOfBirth"]),
            address=Address.from_json_api(attributes["address"]),
            phone=Phone.from_json_api(attributes["phone"]),
            email=attributes["email"], ssn=attributes.get("ssn"), passport=attributes.get("passport"),
            nationality=attributes.get("nationality"),
            authorized_users=AuthorizedUser.from_json_api(attributes["authorizedUsers"]),
            tags=attributes.get("tags"), relationships=relationships, status=attributes.get("status"),
            archive_reason=attributes.get("archiveReason"),
            eligible_products=attributes.get("eligibleProducts"), ein=attributes.get("ein"),
        )


class BusinessCustomerDTO(object):
    def __init__(self, id: str, created_at: datetime, name: str, address: Address, phone: Phone,
                 state_of_incorporation: str, ein: str, entity_type: EntityType, contact: BusinessContact,
                 authorized_users: [AuthorizedUser], dba: Optional[str], tags: Optional[Dict[str, str]],
                 relationships: Optional[Dict[str, Relationship]], status: CustomerStatus,
                 archive_reason: Optional[ArchiveReason], eligible_products: Optional[List[str]] = None):
        self.id = id
        self.type = 'businessCustomer'
        self.attributes = {"createdAt": created_at, "name": name, "address": address, "phone": phone,
                           "stateOfIncorporation": state_of_incorporation, "ein": ein, "entityType": entity_type,
                           "contact": contact, "authorizedUsers": authorized_users, "dba": dba,
                           "eligibleProducts": eligible_products, "tags": tags,
                           "status": status, "archiveReason": archive_reason}
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return BusinessCustomerDTO(
            id=_id, created_at=date_utils.to_datetime(attributes["createdAt"]), name=attributes["name"],
            address=Address.from_json_api(attributes["address"]),
            phone=Phone.from_json_api(attributes["phone"]),
            state_of_incorporation=attributes["stateOfIncorporation"], ein=attributes["ein"],
            entity_type=attributes["entityType"],
            contact=BusinessContact.from_json_api(attributes["contact"]),
            authorized_users=AuthorizedUser.from_json_api(attributes["authorizedUsers"]),
            dba=attributes.get("dba"), tags=attributes.get("tags"), relationships=relationships,
            status=attributes.get("status"), archive_reason=attributes.get("archiveReason"),
            eligible_products=attributes.get("eligibleProducts"),
        )

CustomerDTO = Union[IndividualCustomerDTO, BusinessCustomerDTO]


class PatchIndividualCustomerRequest(UnitRequest):
    def __init__(self, customer_id: str, address: Optional[Address] = None, phone: Optional[Phone] = None,
                 email: Optional[str] = None, dba: Optional[str] = None,
                 authorized_users: Optional[List[AuthorizedUser]] = None, tags: Optional[Dict[str, str]] = None):
        self.customer_id = customer_id
        self.address = address
        self.phone = phone
        self.email = email
        self.dba = dba
        self.authorized_users = authorized_users
        self.tags = tags

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "individualCustomer",
                "attributes": {}
            }
        }

        if self.address:
            payload["data"]["attributes"]["address"] = self.address

        if self.phone:
            payload["data"]["attributes"]["phone"] = self.phone

        if self.email:
            payload["data"]["attributes"]["email"] = self.email

        if self.dba:
            payload["data"]["attributes"]["dba"] = self.dba

        if self.authorized_users:
            payload["data"]["attributes"]["authorizedUsers"] = self.authorized_users

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())


class PatchBusinessCustomerRequest(UnitRequest):
    def __init__(self, customer_id: str, address: Optional[Address] = None, phone: Optional[Phone] = None,
                 contact: Optional[BusinessContact] = None, authorized_users: Optional[List[AuthorizedUser]] = None,
                 tags: Optional[Dict[str, str]] = None):
        self.customer_id = customer_id
        self.address = address
        self.phone = phone
        self.contact = contact
        self.authorized_users = authorized_users
        self.tags = tags

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "businessCustomer",
                "attributes": {}
            }
        }

        if self.address:
            payload["data"]["attributes"]["address"] = self.address

        if self.phone:
            payload["data"]["attributes"]["phone"] = self.phone

        if self.contact:
            payload["data"]["attributes"]["contact"] = self.contact

        if self.authorized_users:
            payload["data"]["attributes"]["authorizedUsers"] = self.authorized_users

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())


class ListCustomerParams(UnitParams):
    def __init__(self, offset: int = 0, limit: int = 100, query: Optional[str] = None, email: Optional[str] = None,
                 tags: Optional[object] = None, sort: Optional[Literal["createdAt", "-createdAt"]] = None):
        self.offset = offset
        self.limit = limit
        self.query = query
        self.email = email
        self.tags = tags
        self.sort = sort

    def to_dict(self) -> Dict:
        parameters = {"page[limit]": self.limit, "page[offset]": self.offset}
        if self.query:
            parameters["filter[query]"] = self.query
        if self.email:
            parameters["filter[email]"] = self.email
        if self.tags:
            parameters["filter[tags]"] = self.tags
        if self.sort:
            parameters["sort"] = self.sort
        return parameters


class ArchiveCustomerRequest(UnitRequest):
    def __init__(self, customer_id: str, reason: Optional[ArchiveReason] = None):
        self.customer_id = customer_id
        self.reason = reason

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "archiveCustomer",
                "attributes": {}
            }
        }

        if self.reason:
            payload["data"]["attributes"]["reason"] = self.reason

        return payload

    def __repr__(self):
        return json.dumps(self.to_json_api())
