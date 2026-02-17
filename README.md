# unit-python-sdk

This library provides a python wrapper to [Unit's API](https://docs.unit.co/#introduction).

## Documentation
See https://docs.unit.co/

## Installation

    pip install unit-python-sdk

## Usage
Creating Business Application (V2)
```python
    import os
    from unit import Unit
    from unit.models import *
    from unit.models.application import CreateBusinessApplicationRequestV2
    
    token = os.environ.get("token")
    api_url = os.environ.get("api_url")

    unit = Unit(api_url, token)

    request = CreateBusinessApplicationRequestV2(
        name="Acme Inc.",
        address=Address("1600 Pennsylvania Avenue Northwest",
                        "Washington", "CA", "20500", "US"),
        phone=Phone("1", "9294723497"),
        state_of_incorporation="CA",
        entity_type="LLC",
        ein="123456789",
        year_of_incorporation="2020",
        source_of_funds="SalesOfGoods",
        business_industry="OnlineRetailOrECommerce",
        business_description="Online retail store selling electronics",
        is_regulated=False,
        us_nexus=["Employees", "Customers"],
        account_purpose="EcommerceSales",
        transaction_volume="Between50KAnd250K",
        countries_of_operation=["US"],
        website="https://acme.example.com",
        officer=Officer(full_name=FullName("Jone", "Doe"), date_of_birth=date.today() - timedelta(days=20 * 365),
                        address=Address("950 Allerton Street",
                                        "Redwood City", "CA", "94063", "US"),
                        phone=Phone("1", "2025550108"), email="jone.doe@unit-finance.com", ssn="000000005"),
        contact=BusinessContact(full_name=FullName(
            "Jone", "Doe"), email="jone.doe@unit-finance.com", phone=Phone("1", "2025550108")),
        beneficial_owners=[
            BeneficialOwner(
                FullName("James", "Smith"), date.today() -
                timedelta(days=20*365),
                Address("650 Allerton Street",
                        "Redwood City", "CA", "94063", "US"),
                Phone("1", "2025550127"), "james@unit-finance.com", ssn="574567625"),
            BeneficialOwner(FullName("Richard", "Hendricks"), date.today() - timedelta(days=20 * 365),
                            Address("470 Allerton Street",
                                    "Redwood City", "CA", "94063", "US"),
                            Phone("1", "2025550158"), "richard@unit-finance.com", ssn="574572795")
        ]
    )
    
    application = unit.applications.create(request).data
    print(application.id)
```

Fetching a customer

```python
    import os
    from unit import Unit
    from unit.models.customer import *

    token = os.environ.get("token")
    api_url = os.environ.get("api_url")

    unit = Unit(api_url, token)
    customer = unit.customers.list().data[0]
    print(customer.id)
```