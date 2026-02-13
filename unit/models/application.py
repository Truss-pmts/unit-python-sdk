from unit.utils import date_utils
from unit.models import *
from typing import IO

ApplicationStatus = Literal["Approved", "Denied", "Pending", "PendingReview"]

DocumentType = Literal[
    "IdDocument",
    "Passport",
    "AddressVerification",
    "CertificateOfIncorporation",
    "EmployerIdentificationNumberConfirmation",
    "SocialSecurityCard",
    "ClientRequested",
    "SelfieVerification",
]

ApplicationDocumentStatus = Literal[
    "Required",
    "ReceivedBack",
    "ReceivedFront",
    "Invalid",
    "Approved",
    "PendingReview"
]

ReasonCode = Literal[
    "PoorQuality",
    "NameMismatch",
    "SSNMismatch",
    "AddressMismatch",
    "DOBMismatch",
    "ExpiredId",
    "EINMismatch",
    "StateMismatch",
    "Other",
]

ApplicationTypes = Literal[
    "individualApplication", "businessApplication", "trustApplication"
]


Industry = Literal[
    "Retail",
    "Wholesale",
    "Restaurants",
    "Hospitals",
    "Construction",
    "Insurance",
    "Unions",
    "RealEstate",
    "FreelanceProfessional",
    "OtherProfessionalServices",
    "OnlineRetailer",
    "OtherEducationServices",
]

AnnualRevenue = Literal[
    "UpTo250k",
    "Between250kAnd500k",
    "Between500kAnd1m",
    "Between1mAnd5m",
    "Over5m",
    "UpTo50k",
    "Between50kAnd100k",
    "Between100kAnd200k",
    "Between200kAnd500k",
    "Over500k",
]

NumberOfEmployees = Literal[
    "One",
    "Between2And5",
    "Between5And10",
    "Over10",
    "UpTo10",
    "Between10And50",
    "Between50And100",
    "Between100And500",
    "Over500",
]

CashFlow = Literal["Unpredictable", "Predictable"]

BusinessVertical = Literal[
    "AdultEntertainmentDatingOrEscortServices",
    "AgricultureForestryFishingOrHunting",
    "ArtsEntertainmentAndRecreation",
    "BusinessSupportOrBuildingServices",
    "Cannabis",
    "Construction",
    "DirectMarketingOrTelemarketing",
    "EducationalServices",
    "FinancialServicesCryptocurrency",
    "FinancialServicesDebitCollectionOrConsolidation",
    "FinancialServicesMoneyServicesBusinessOrCurrencyExchange",
    "FinancialServicesOther",
    "FinancialServicesPaydayLending",
    "GamingOrGambling",
    "HealthCareAndSocialAssistance",
    "HospitalityAccommodationOrFoodServices",
    "LegalAccountingConsultingOrComputerProgramming",
    "Manufacturing",
    "Mining",
    "Nutraceuticals",
    "PersonalCareServices",
    "PublicAdministration",
    "RealEstate",
    "ReligiousCivicAndSocialOrganizations",
    "RepairAndMaintenance",
    "RetailTrade",
    "TechnologyMediaOrTelecom",
    "TransportationOrWarehousing",
    "Utilities",
    "WholesaleTrade",
]

Revocability = Literal["Revocable", "Irrevocable"]
SourceOfFunds = Literal[
    "Inheritance", "Salary", "Savings", "InvestmentReturns", "Gifts"
]

# --- V2 Enum Types ---
# These types are used for v2 application create requests.
# Business and Sole Prop share AccountPurpose and SourceOfFunds enums.
# TransactionVolume has separate enum sets per application type.
# Individual-only enums (individual sourceOfFunds, accountPurpose,
# transactionVolume, profession) are out of scope — Truss only supports
# sole prop and business.

AccountPurposeBusinessSoleProp = Literal[
    "RetailSalesInPerson",
    "EcommerceSales",
    "CashHeavyIncomeAndOperations",
    "ImportExportTradeOperations",
    "ProfessionalServicesNotHandlingFunds",
    "ProfessionalServicesHandlingFunds",
    "HoldingOrInvestmentCompanyOperations",
    "PropertyManagementOrRealEstateOperations",
    "CharitableOrNonProfitOrganizationOperations",
    "ConstructionAndContractingOperations",
    "CommercialCashOperations",
    "FreightForwardingOrLogisticsOperations",
    "ThirdPartyPaymentProcessing",
    "TechnologyStartupOperations",
    "WholesaleDistributionOperations",
    "FranchiseOperationOperations",
    "HealthcareProviderOperations",
    "EducationalInstitutionOperations",
]

SourceOfFundsBusinessSoleProp = Literal[
    "SalesOfGoods",
    "SalesOfServices",
    "CustomerPayments",
    "InvestmentCapital",
    "BusinessLoans",
    "OwnerContributions",
    "FranchiseRevenue",
    "RentalIncome",
    "GovernmentContractsOrGrants",
    "DonationsOrFundraising",
    "MembershipFeesOrSubscriptions",
    "LicensingOrRoyalties",
    "CommissionIncome",
    "ImportExportRevenue",
    "CryptocurrencyRelatedActivity",
]

TransactionVolumeBusiness = Literal[
    "LessThan10K",
    "Between10KAnd50K",
    "Between50KAnd250K",
    "Between250KAnd1M",
    "Between1MAnd2M",
    "GreaterThan2M",
]

TransactionVolumeSoleProp = Literal[
    "LessThan5K",
    "Between5KAnd20K",
    "Between20KAnd75K",
    "Between75KAnd150K",
    "Between150KAnd300K",
    "GreaterThan300K",
]

BusinessIndustry = Literal[
    # Retail
    "GroceryStoresOrSupermarkets",
    "ConvenienceStores",
    "SpecialtyFoodRetailers",
    "GasStationsWithRetail",
    "GeneralMerchandiseOrDepartmentStores",
    "OnlineRetailOrECommerce",
    "SubscriptionAndMembershipPlatforms",
    "DirectToConsumerBrands",
    "Cannabis",
    # Financial Services
    "BanksOrCreditUnions",
    "FinTechOrPaymentProcessing",
    "InsuranceProviders",
    "InvestmentAdvisorsOrBrokerDealers",
    "LendingOrMortgageCompanies",
    "TreasuryManagementPlatforms",
    "PersonalFinanceAppsOrAIAssistants",
    "RetirementPlanning",
    "RealEstateInvestmentPlatforms",
    "MoneyServiceBusinesses",
    "Cryptocurrency",
    "DebtCollection",
    "PaydayLending",
    "Gambling",
    # Food & Agriculture
    "FarmsOrAgriculturalProducers",
    "FoodWholesalersOrDistributors",
    "RestaurantsOrCafes",
    "BarsOrNightclubs",
    "CateringServices",
    "FarmersMarkets",
    "RestaurantTechAndPOSProviders",
    # Healthcare
    "HospitalsOrClinics",
    "Pharmacies",
    "MedicalEquipmentSuppliers",
    "BiotechnologyFirms",
    "HomeHealthServices",
    "HealthcareStaffingPlatforms",
    "WellnessAndBenefitsPlatforms",
    "HealthcareAndSocialAssistance",
    # Professional Services
    "LegalServices",
    "AccountingOrAuditingFirms",
    "ConsultingFirms",
    "MarketingOrAdvertisingAgencies",
    "RealEstateAgentsOrPropertyManagers",
    "CorporateServicesAndIncorporation",
    "HRAndWorkforceManagementPlatforms",
    "DirectMarketingOrTelemarketing",
    "LegalAccountingConsultingOrComputerProgramming",
    # Manufacturing
    "ChemicalManufacturing",
    "ElectronicsOrHardwareManufacturing",
    "AutomotiveManufacturing",
    "ConstructionMaterials",
    "TextilesOrApparel",
    "Mining",
    # Real Estate & Construction
    "RealEstate",
    "Construction",
    # Other
    "TransportationOrWarehousing",
    "WholesaleTrade",
    "BusinessSupportOrBuildingServices",
    "EscortServices",
    "DatingOrAdultEntertainment",
]

EntityTypeV2 = Literal[
    "Estate",
    "Trust",
    "ForeignFinancialInstitution",
    "DomesticFinancialInstitution",
    "GovernmentEntityOrAgency",
    "ReligiousOrganization",
    "Charity",
    "LLC",
    "Partnership",
    "PubliclyTradedCorporation",
    "PrivatelyHeldCorporation",
    "NotForProfitOrganization",
]

UsNexus = Literal[
    "NotAvailable",
    "Employees",
    "Customers",
    "PhysicalOfficeOrFacility",
    "BankingRelationships",
]


class IndividualApplicationDTO(object):
    def __init__(
        self,
        id: str,
        created_at: datetime,
        full_name: FullName,
        address: Address,
        date_of_birth: date,
        email: str,
        phone: Phone,
        status: ApplicationStatus,
        ssn: Optional[str],
        message: Optional[str],
        ip: Optional[str],
        ein: Optional[str],
        dba: Optional[str],
        sole_proprietorship: Optional[bool],
        business_vertical: Optional[BusinessVertical],
        tags: Optional[Dict[str, str]],
        relationships: Optional[Dict[str, Relationship]],
    ):
        self.id = id
        self.type = "individualApplication"
        self.attributes = {
            "createdAt": created_at,
            "fullName": full_name,
            "address": address,
            "dateOfBirth": date_of_birth,
            "email": email,
            "phone": phone,
            "status": status,
            "ssn": ssn,
            "message": message,
            "ip": ip,
            "ein": ein,
            "dba": dba,
            "soleProprietorship": sole_proprietorship,
            "businessVertical": business_vertical,
            "tags": tags,
        }
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return IndividualApplicationDTO(
            _id,
            date_utils.to_datetime(attributes["createdAt"]),
            FullName.from_json_api(attributes["fullName"]),
            Address.from_json_api(attributes["address"]),
            date_utils.to_date(attributes["dateOfBirth"]),
            attributes["email"],
            Phone.from_json_api(attributes["phone"]),
            attributes["status"],
            attributes.get("ssn"),
            attributes.get("message"),
            attributes.get("ip"),
            attributes.get("ein"),
            attributes.get("dba"),
            attributes.get("soleProprietorship"),
            attributes.get("businessVertical"),
            attributes.get("tags"),
            relationships,
        )


class BusinessApplicationDTO(object):
    def __init__(
        self,
        id: str,
        created_at: datetime,
        name: str,
        address: Address,
        phone: Phone,
        status: ApplicationStatus,
        state_of_incorporation: str,
        entity_type: EntityType,
        contact: BusinessContact,
        officer: Officer,
        beneficial_owners: [BeneficialOwner],
        ssn: Optional[str],
        message: Optional[str],
        ip: Optional[str],
        ein: Optional[str],
        dba: Optional[str],
        website: Optional[str],
        year_of_incorporation: Optional[str],
        business_vertical: Optional[BusinessVertical],
        annual_revenue: Optional[AnnualRevenue],
        number_of_employees: Optional[NumberOfEmployees],
        cash_flow: Optional[CashFlow],
        countries_of_operation: Optional[List[str]],
        operating_address: Optional[Address],
        tags: Optional[Dict[str, str]],
        relationships: Optional[Dict[str, Relationship]],
    ):
        self.id = id
        self.type = "businessApplication"
        self.attributes = {
            "createdAt": created_at,
            "name": name,
            "address": address,
            "phone": phone,
            "status": status,
            "ssn": ssn,
            "stateOfIncorporation": state_of_incorporation,
            "message": message,
            "ip": ip,
            "ein": ein,
            "entityType": entity_type,
            "dba": dba,
            "website": website,
            "yearOfIncorporation": year_of_incorporation,
            "businessVertical": business_vertical,
            "annualRevenue": annual_revenue,
            "numberOfEmployees": number_of_employees,
            "cashFlow": cash_flow,
            "countriesOfOperation": countries_of_operation,
            "contact": contact,
            "officer": officer,
            "beneficialOwners": beneficial_owners,
            "operatingAddress": operating_address,
            "tags": tags,
        }
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return BusinessApplicationDTO(
            _id,
            date_utils.to_datetime(attributes["createdAt"]),
            attributes.get("name"),
            Address.from_json_api(attributes["address"]),
            Phone.from_json_api(attributes["phone"]),
            attributes["status"],
            attributes.get("stateOfIncorporation"),
            attributes.get("entityType"),
            BusinessContact.from_json_api(attributes["contact"]),
            Officer.from_json_api(attributes["officer"]),
            BeneficialOwner.from_json_api(attributes["beneficialOwners"]),
            attributes.get("ssn"),
            attributes.get("message"),
            attributes.get("ip"),
            attributes.get("ein"),
            attributes.get("dba"),
            attributes.get("website"),
            attributes.get("year_of_incorporation"),
            attributes.get("business_vertical"),
            attributes.get("annual_revenue"),
            attributes.get("number_of_employees"),
            attributes.get("cash_flow"),
            attributes.get("countries_of_operation"),
            attributes.get("operating_address"),
            attributes.get("tags"),
            relationships,
        )


ApplicationDTO = Union[IndividualApplicationDTO, BusinessApplicationDTO]


class CreateIndividualApplicationRequest(UnitRequest):
    def __init__(
        self,
        full_name: FullName,
        date_of_birth: date,
        address: Address,
        email: str,
        phone: Phone,
        ip: str = None,
        ein: str = None,
        dba: str = None,
        sole_proprietorship: bool = None,
        passport: str = None,
        nationality: str = None,
        ssn=None,
        device_fingerprints: Optional[List[DeviceFingerprint]] = None,
        idempotency_key: str = None,
        tags: Optional[Dict[str, str]] = None,
        website: str = None,
        annual_revenue: Optional[AnnualRevenue] = None,
        number_of_employees: Optional[NumberOfEmployees] = None,
        business_vertical: Optional[BusinessVertical] = None,
    ):
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.address = address
        self.email = email
        self.phone = phone
        self.ip = ip
        self.ein = ein
        self.dba = dba
        self.sole_proprietorship = sole_proprietorship
        self.ssn = ssn
        self.passport = passport
        self.nationality = nationality
        self.device_fingerprints = device_fingerprints
        self.idempotency_key = idempotency_key
        self.tags = tags
        self.annual_revenue = annual_revenue
        self.number_of_employees = number_of_employees
        self.business_vertical = business_vertical
        self.website = website

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "individualApplication",
                "attributes": {
                    "fullName": self.full_name,
                    "dateOfBirth": date_utils.to_date_str(self.date_of_birth),
                    "address": self.address,
                    "email": self.email,
                    "phone": self.phone,
                },
            }
        }

        if self.ip:
            payload["data"]["attributes"]["ip"] = self.ip

        if self.ein:
            payload["data"]["attributes"]["ein"] = self.ein

        if self.dba:
            payload["data"]["attributes"]["dba"] = self.dba

        if self.sole_proprietorship:
            payload["data"]["attributes"][
                "soleProprietorship"
            ] = self.sole_proprietorship

        if self.ssn:
            payload["data"]["attributes"]["ssn"] = self.ssn

        if self.passport:
            payload["data"]["attributes"]["passport"] = self.passport

        if self.nationality:
            payload["data"]["attributes"]["nationality"] = self.nationality

        if self.idempotency_key:
            payload["data"]["attributes"]["idempotencyKey"] = self.idempotency_key

        if self.device_fingerprints:
            payload["data"]["attributes"]["deviceFingerprints"] = [
                e.to_json_api() for e in self.device_fingerprints
            ]

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        if self.website:
            payload["data"]["attributes"]["website"] = self.website

        if self.annual_revenue:
            payload["data"]["attributes"]["annualRevenue"] = self.annual_revenue

        if self.number_of_employees:
            payload["data"]["attributes"]["numberOfEmployees"] = self.number_of_employees

        if self.business_vertical:
            payload["data"]["attributes"]["businessVertical"] = self.business_vertical

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())


class CreateBusinessApplicationRequest(UnitRequest):
    def __init__(
        self,
        name: str,
        address: Address,
        phone: Phone,
        state_of_incorporation: str,
        ein: str,
        contact: BusinessContact,
        officer: Officer,
        beneficial_owners: [BeneficialOwner],
        entity_type: EntityType,
        tags: Optional[Dict[str, str]] = None,
        dba: str = None,
        ip: str = None,
        website: str = None,
        industry: Optional[Industry] = None,
        annual_revenue: Optional[AnnualRevenue] = None,
        number_of_employees: Optional[NumberOfEmployees] = None,
        cash_flow: Optional[CashFlow] = None,
        year_of_incorporation: Optional[str] = None,
        countries_of_operation: Optional[List[str]] = None,
        stock_symbol: Optional[str] = None,
        business_vertical: Optional[BusinessVertical] = None,
        device_fingerprints: Optional[List[DeviceFingerprint]] = None,
        operating_address: Optional[Address] = None,
        idempotency_key: Optional[str] = None,
    ):
        self.name = name
        self.address = address
        self.phone = phone
        self.state_of_incorporation = state_of_incorporation
        self.ein = ein
        self.contact = contact
        self.officer = officer
        self.beneficial_owners = beneficial_owners
        self.entity_type = entity_type
        self.dba = dba
        self.ip = ip
        self.website = website
        self.tags = tags
        self.industry = industry
        self.annual_revenue = annual_revenue
        self.number_of_employees = number_of_employees
        self.cash_flow = cash_flow
        self.year_of_incorporation = year_of_incorporation
        self.countries_of_operation = countries_of_operation
        self.stock_symbol = stock_symbol
        self.business_vertical = business_vertical
        self.device_fingerprints = device_fingerprints
        self.operating_address = operating_address
        self.idempotency_key = idempotency_key

    def to_json_api(self) -> dict:
        payload = {
            "data": {
                "type": "businessApplication",
                "attributes": {
                    "name": self.name,
                    "address": self.address,
                    "phone": self.phone,
                    "stateOfIncorporation": self.state_of_incorporation,
                    "ein": self.ein,
                    "contact": self.contact,
                    "officer": self.officer,
                    "beneficialOwners": self.beneficial_owners,
                    "entityType": self.entity_type,
                    "yearOfIncorporation": self.year_of_incorporation,
                    "businessVertical": self.business_vertical,
                },
            }
        }

        if self.dba:
            payload["data"]["attributes"]["dba"] = self.dba

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        if self.ip:
            payload["data"]["attributes"]["ip"] = self.ip

        if self.website:
            payload["data"]["attributes"]["website"] = self.website

        if self.industry:
            payload["data"]["attributes"]["industry"] = self.industry

        if self.annual_revenue:
            payload["data"]["attributes"]["annualRevenue"] = self.annual_revenue

        if self.number_of_employees:
            payload["data"]["attributes"]["numberOfEmployees"] = self.number_of_employees

        if self.cash_flow:
            payload["data"]["attributes"]["cashFlow"] = self.cash_flow

        if self.countries_of_operation:
            payload["data"]["attributes"]["countriesOfOperation"] = self.countries_of_operation

        if self.stock_symbol:
            payload["data"]["attributes"]["stockSymbol"] = self.stock_symbol

        if self.operating_address:
            payload["data"]["attributes"]["operatingAddress"] = self.operating_address
        
        if self.idempotency_key:
            payload["data"]["attributes"]["idempotencyKey"] = self.idempotency_key

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())


class CreateSolePropApplicationRequestV2(UnitRequest):
    """V2 sole proprietor application request.

    Uses individualApplication type with soleProprietorship=True.
    Truss only supports sole prop (not plain individual), so this class
    does not include the 'profession' field (individual-only in v2).
    """

    def __init__(
        self,
        full_name: FullName,
        date_of_birth: date,
        address: Address,
        email: str,
        phone: Phone,
        account_purpose: AccountPurposeBusinessSoleProp,
        source_of_funds: SourceOfFundsBusinessSoleProp,
        transaction_volume: TransactionVolumeSoleProp,
        business_industry: BusinessIndustry,
        is_incorporated: bool,
        countries_of_operation: List[str],
        us_nexus: List[UsNexus],
        website: Optional[str] = None,
        ssn: Optional[str] = None,
        passport: Optional[str] = None,
        nationality: Optional[str] = None,
        ein: Optional[str] = None,
        dba: Optional[str] = None,
        state_of_incorporation: Optional[str] = None,
        year_of_incorporation: Optional[str] = None,
        account_purpose_detail: Optional[str] = None,
        transaction_volume_description: Optional[str] = None,
        source_of_funds_description: Optional[str] = None,
        ip: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
        device_fingerprints: Optional[List[DeviceFingerprint]] = None,
    ):
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.address = address
        self.email = email
        self.phone = phone
        self.account_purpose = account_purpose
        self.source_of_funds = source_of_funds
        self.transaction_volume = transaction_volume
        self.business_industry = business_industry
        self.is_incorporated = is_incorporated
        self.countries_of_operation = countries_of_operation
        self.us_nexus = us_nexus
        self.website = website
        self.ssn = ssn
        self.passport = passport
        self.nationality = nationality
        self.ein = ein
        self.dba = dba
        self.state_of_incorporation = state_of_incorporation
        self.year_of_incorporation = year_of_incorporation
        self.account_purpose_detail = account_purpose_detail
        self.transaction_volume_description = transaction_volume_description
        self.source_of_funds_description = source_of_funds_description
        self.ip = ip
        self.tags = tags
        self.idempotency_key = idempotency_key
        self.device_fingerprints = device_fingerprints

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "individualApplication",
                "attributes": {
                    "fullName": self.full_name,
                    "dateOfBirth": date_utils.to_date_str(self.date_of_birth),
                    "address": self.address,
                    "email": self.email,
                    "phone": self.phone,
                    "soleProprietorship": True,
                    # V2 required fields
                    "accountPurpose": self.account_purpose,
                    "sourceOfFunds": self.source_of_funds,
                    "transactionVolume": self.transaction_volume,
                    "businessIndustry": self.business_industry,
                    "isIncorporated": self.is_incorporated,
                    "countriesOfOperation": self.countries_of_operation,
                    "usNexus": self.us_nexus,
                    "website": self.website,  # Required in v2, null = "no website"
                },
            }
        }

        attrs = payload["data"]["attributes"]

        if self.ssn:
            attrs["ssn"] = self.ssn

        if self.passport:
            attrs["passport"] = self.passport

        if self.nationality:
            attrs["nationality"] = self.nationality

        if self.ein:
            attrs["ein"] = self.ein

        if self.dba:
            attrs["dba"] = self.dba

        if self.ip:
            attrs["ip"] = self.ip

        if self.tags:
            attrs["tags"] = self.tags

        if self.idempotency_key:
            attrs["idempotencyKey"] = self.idempotency_key

        if self.device_fingerprints:
            attrs["deviceFingerprints"] = [
                e.to_json_api() for e in self.device_fingerprints
            ]

        # Conditional v2 fields — only include when not None
        if self.state_of_incorporation is not None:
            attrs["stateOfIncorporation"] = self.state_of_incorporation

        if self.year_of_incorporation is not None:
            attrs["yearOfIncorporation"] = self.year_of_incorporation

        if self.account_purpose_detail is not None:
            attrs["accountPurposeDetail"] = self.account_purpose_detail

        if self.transaction_volume_description is not None:
            attrs["transactionVolumeDescription"] = self.transaction_volume_description

        if self.source_of_funds_description is not None:
            attrs["sourceOfFundsDescription"] = self.source_of_funds_description

        return payload

    def __repr__(self):
        return json.dumps(self.to_json_api())


class CreateBusinessApplicationRequestV2(UnitRequest):
    """V2 business application request with new required fields."""

    def __init__(
        self,
        name: str,
        address: Address,
        phone: Phone,
        state_of_incorporation: str,
        ein: str,
        contact: BusinessContact,
        officer: Officer,
        beneficial_owners: List[BeneficialOwner],
        entity_type: EntityTypeV2,
        year_of_incorporation: str,
        source_of_funds: SourceOfFundsBusinessSoleProp,
        business_industry: BusinessIndustry,
        business_description: str,
        is_regulated: bool,
        us_nexus: List[UsNexus],
        account_purpose: AccountPurposeBusinessSoleProp,
        transaction_volume: TransactionVolumeBusiness,
        countries_of_operation: List[str],
        website: Optional[str] = None,
        dba: Optional[str] = None,
        operating_address: Optional[Address] = None,
        source_of_funds_description: Optional[str] = None,
        regulator_name: Optional[str] = None,
        account_purpose_detail: Optional[str] = None,
        transaction_volume_description: Optional[str] = None,
        stock_exchange_name: Optional[str] = None,
        stock_symbol: Optional[str] = None,
        ip: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ):
        self.name = name
        self.address = address
        self.phone = phone
        self.state_of_incorporation = state_of_incorporation
        self.ein = ein
        self.contact = contact
        self.officer = officer
        self.beneficial_owners = beneficial_owners
        self.entity_type = entity_type
        self.year_of_incorporation = year_of_incorporation
        self.source_of_funds = source_of_funds
        self.business_industry = business_industry
        self.business_description = business_description
        self.is_regulated = is_regulated
        self.us_nexus = us_nexus
        self.account_purpose = account_purpose
        self.transaction_volume = transaction_volume
        self.countries_of_operation = countries_of_operation
        self.website = website
        self.dba = dba
        self.operating_address = operating_address
        self.source_of_funds_description = source_of_funds_description
        self.regulator_name = regulator_name
        self.account_purpose_detail = account_purpose_detail
        self.transaction_volume_description = transaction_volume_description
        self.stock_exchange_name = stock_exchange_name
        self.stock_symbol = stock_symbol
        self.ip = ip
        self.tags = tags
        self.idempotency_key = idempotency_key

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "businessApplication",
                "attributes": {
                    "name": self.name,
                    "address": self.address,
                    "phone": self.phone,
                    "stateOfIncorporation": self.state_of_incorporation,
                    "ein": self.ein,
                    "contact": self.contact,
                    "officer": self.officer,
                    "beneficialOwners": self.beneficial_owners,
                    "entityType": self.entity_type,
                    "yearOfIncorporation": self.year_of_incorporation,
                    # V2 required fields
                    "sourceOfFunds": self.source_of_funds,
                    "businessIndustry": self.business_industry,
                    "businessDescription": self.business_description,
                    "isRegulated": self.is_regulated,
                    "usNexus": self.us_nexus,
                    "accountPurpose": self.account_purpose,
                    "transactionVolume": self.transaction_volume,
                    "countriesOfOperation": self.countries_of_operation,
                    "website": self.website,  # Required in v2, null = "no website"
                },
            }
        }

        attrs = payload["data"]["attributes"]

        if self.dba:
            attrs["dba"] = self.dba

        if self.ip:
            attrs["ip"] = self.ip

        if self.tags:
            attrs["tags"] = self.tags

        if self.idempotency_key:
            attrs["idempotencyKey"] = self.idempotency_key

        if self.operating_address:
            attrs["operatingAddress"] = self.operating_address

        # Conditional v2 fields — only include when not None
        if self.source_of_funds_description is not None:
            attrs["sourceOfFundsDescription"] = self.source_of_funds_description

        if self.regulator_name is not None:
            attrs["regulatorName"] = self.regulator_name

        if self.account_purpose_detail is not None:
            attrs["accountPurposeDetail"] = self.account_purpose_detail

        if self.transaction_volume_description is not None:
            attrs["transactionVolumeDescription"] = self.transaction_volume_description

        if self.stock_exchange_name is not None:
            attrs["stockExchangeName"] = self.stock_exchange_name

        if self.stock_symbol is not None:
            attrs["stockSymbol"] = self.stock_symbol

        return payload

    def __repr__(self):
        return json.dumps(self.to_json_api())


class ApplicationDocumentDTO(object):
    def __init__(
        self,
        id: str,
        status: ApplicationDocumentStatus,
        document_type: DocumentType,
        description: str,
        name: str,
        address: Optional[Address],
        date_of_birth: Optional[date],
        passport: Optional[str],
        ein: Optional[str],
        reason_code: Optional[ReasonCode],
        reason: Optional[str],
    ):
        self.id = id
        self.type = "document"
        self.attributes = {
            "status": status,
            "documentType": document_type,
            "description": description,
            "name": name,
            "address": address,
            "dateOfBirth": date_of_birth,
            "passport": passport,
            "ein": ein,
            "reasonCode": reason_code,
            "reason": reason,
        }

    @staticmethod
    def from_json_api(_id, _type, attributes):
        address = (
            Address.from_json_api(attributes.get("address"))
            if attributes.get("address")
            else None
        )
        return ApplicationDocumentDTO(
            _id,
            attributes["status"],
            attributes["documentType"],
            attributes["description"],
            attributes["name"],
            address,
            attributes.get("dateOfBirth"),
            attributes.get("passport"),
            attributes.get("ein"),
            attributes.get("reasonCode"),
            attributes.get("reason"),
        )


FileType = Literal["jpeg", "png", "pdf"]


class UploadDocumentRequest(object):
    def __init__(
        self,
        application_id: str,
        document_id: str,
        file: IO,
        file_type: FileType,
        is_back_side: Optional[bool] = False,
    ):
        self.application_id = application_id
        self.document_id = document_id
        self.file = file
        self.file_type = file_type
        self.is_back_side = is_back_side


class ListApplicationParams(UnitParams):
    def __init__(
        self,
        offset: int = 0,
        limit: int = 100,
        email: Optional[str] = None,
        tags: Optional[object] = None,
        query: Optional[str] = None,
        sort: Optional[Literal["createdAt", "-createdAt"]] = None,
    ):
        self.offset = offset
        self.limit = limit
        self.email = email
        self.query = query
        self.sort = sort
        self.tags = tags

    def to_dict(self) -> Dict:
        parameters = {"page[limit]": self.limit, "page[offset]": self.offset}
        if self.email:
            parameters["filter[email]"] = self.email
        if self.query:
            parameters["filter[query]"] = self.query
        if self.tags:
            parameters["filter[tags]"] = self.tags
        if self.sort:
            parameters["sort"] = self.sort
        return parameters


class PatchApplicationRequest(UnitRequest):
    def __init__(
        self,
        application_id: str,
        type: ApplicationTypes = "individualApplication",
        tags: Optional[Dict[str, str]] = None,
    ):
        self.application_id = application_id
        self.type = type
        self.tags = tags

    def to_json_api(self) -> Dict:
        payload = {"data": {"type": self.type, "attributes": {}}}

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())


class ApproveApplicationSBRequest(UnitRequest):
    def __init__(self, application_id: str):
        self.application_id = application_id

    def to_json_api(self) -> Dict:
        payload = {
            "data": {"type": "applicationApprove", "attributes": {"reason": "sandbox"}}
        }
        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())
