---
name: truss-unit-sdk
description: Guide to the Truss Unit Python SDK fork covering the resource-based API pattern, application DTOs and request types, JSON API codec system, and how the API repo interfaces with the SDK via unit_api_call. Use when updating the Unit SDK, adding new SDK types, modifying application submission, working with Unit API responses, or preparing for Unit API version migrations.
---

# Truss Unit Python SDK

## Overview

Truss maintains a fork of the Unit Python SDK at `unit-python-sdk/`. This is a typed REST client for the [Unit.co](https://www.unit.co) banking API. The Truss API repo (`api/`) imports this SDK and wraps all calls through `unit_api_call()`.

## Project Structure

```
unit-python-sdk/
├── unit/
│   ├── __init__.py                 # Unit client class — exposes resource accessors
│   ├── api/                        # Resource classes (REST endpoint wrappers)
│   │   ├── base_resource.py        # HTTP methods, auth headers, JSON API encoding
│   │   ├── application_resource.py # applications.create(), .get(), .list(), .update()
│   │   └── [30+ other resources]   # payments, accounts, customers, etc.
│   ├── models/                     # DTOs, request types, response types
│   │   ├── application.py          # Application DTOs + Create/Update request types
│   │   ├── codecs.py               # DtoDecoder — JSON API type → DTO class mapping
│   │   └── [30+ other model files]
│   └── utils/                      # Utility functions
├── e2e_tests/
│   └── application_test.py         # Application e2e tests
└── setup.py                        # Package version (currently 0.10.5)
```

## SDK Architecture

### Request → API → Response Flow

```
1. Build Request Object       (e.g., CreateBusinessApplicationRequest)
         │
         ↓ .to_json_api()
2. JSON API Payload            {"data": {"type": "businessApplication", "attributes": {...}}}
         │
         ↓ BaseResource.post(url, payload)
3. HTTP POST                   POST {api_url}/applications
         │                     Headers: Content-Type: application/vnd.api+json
         │                              Authorization: Bearer {token}
         ↓
4. Raw JSON Response           {"data": {"type": "businessApplication", "id": "...", "attributes": {...}}}
         │
         ↓ DtoDecoder.decode(response)
5. Typed DTO                   BusinessApplicationDTO(id=..., attributes=...)
         │
         ↓ UnitResponse(data=dto, included=[...])
6. UnitResponse Wrapper        Final response with typed data + included resources
```

### BaseResource (`unit/api/base_resource.py`)

All resource classes inherit from `BaseResource`. It provides:

- `get(url)`, `post(url, data)`, `patch(url, data)`, `put(url, data)`, `delete(url)`
- Sets `Content-Type: application/vnd.api+json` and `Authorization: Bearer {token}`
- Serializes request objects via `UnitEncoder` (handles `to_json_api()` on request objects)
- Returns raw response dict for decoding

### Unit Client (`unit/__init__.py`)

The main `Unit` class instantiates all resource accessors:

```python
class Unit:
    def __init__(self, api_url, token):
        self.applications = ApplicationResource(api_url, token)
        self.payments = PaymentResource(api_url, token)
        self.accounts = AccountResource(api_url, token)
        # ... 30+ more resources
```

## Application Types

### DTOs (Response Types)

| Class | JSON API Type | Description |
|-------|---------------|-------------|
| `IndividualApplicationDTO` | `"individualApplication"` | Individual/sole prop application (includes `sole_proprietorship` flag) |
| `BusinessApplicationDTO` | `"businessApplication"` | Business application |

Both are dataclass-style objects with an `id` (Unit's application ID) and `attributes` dict containing all application fields.

### Request Types

| Class | Creates | Key Fields |
|-------|---------|------------|
| `CreateIndividualApplicationRequest` | Individual application | full_name, dob, address, email, phone, ssn, sole_proprietorship, ip, tags, idempotency_key |
| `CreateBusinessApplicationRequest` | Business application | name, address, phone, ein, entity_type, state_of_incorporation, contact, officer, beneficial_owners, tags, idempotency_key |

### Sole Prop as Individual

Sole proprietorships are **not** a separate type. They use `CreateIndividualApplicationRequest` with `sole_proprietorship=True` and additional business-related fields:

```python
CreateIndividualApplicationRequest(
    full_name=FullName(first="John", last="Doe"),
    sole_proprietorship=True,
    # ... individual fields plus business fields
)
```

### `to_json_api()` — Serialization

Each request type implements `to_json_api()` which returns the JSON API payload:

```python
def to_json_api(self):
    return {
        "data": {
            "type": "individualApplication",  # or "businessApplication"
            "attributes": {
                # All fields serialized here
            }
        }
    }
```

This is called automatically by `UnitEncoder` during serialization in `BaseResource.post()`.

## Codec System (`unit/models/codecs.py`)

### Type Mapping

`DtoDecoder.decode()` uses a `mappings` dict to route JSON API responses to the correct DTO class:

```python
mappings = {
    "individualApplication": IndividualApplicationDTO,
    "businessApplication": BusinessApplicationDTO,
    # ... 50+ other type mappings
}
```

When a response comes back with `"type": "businessApplication"`, the decoder instantiates `BusinessApplicationDTO` with the response data.

### Adding New Types

To support a new Unit API type:

1. Create the DTO class in the appropriate `unit/models/*.py` file
2. Create the request class with `to_json_api()` method
3. Add the type string → DTO class mapping to `mappings` in `unit/models/codecs.py`
4. If needed, add a new resource method or resource class in `unit/api/`

## Sub-types Used in Applications

### FullName
```python
FullName(first="John", last="Doe")
```

### Phone
```python
Phone(country_code="1", number="5551234567")
```

### Address (UnitAddress in Truss API)
```python
Address(street="123 Main St", city="Austin", state="TX", postal_code="78701", country="US")
```

### Officer
```python
Officer(
    full_name=FullName(...),
    date_of_birth=date(...),
    address=Address(...),
    phone=Phone(...),
    email="...",
    ssn="...",      # or passport/nationality for non-US
    title="CEO",
)
```

### BeneficialOwner
```python
BeneficialOwner(
    full_name=FullName(...),
    date_of_birth=date(...),
    address=Address(...),
    phone=Phone(...),
    email="...",
    ssn="...",
    percentage=50,  # 25-100
)
```

### BusinessContact
```python
BusinessContact(
    full_name=FullName(...),
    phone=Phone(...),
    email="...",
)
```

## How the API Repo Interfaces with the SDK

For the `unit_api_call()` wrapper pattern, error mapping, and client initialization details, see the `architecture` skill at `api/.cursor/skills/architecture/SKILL.md`.

### Model-to-SDK Conversion

The conversion from Django models to SDK request types happens in `api/src/api/operations/account/onboarding/application/submit_onboarding_application.py`. See the `truss-onboarding-architecture` skill for the complete field mapping.

## Subagents

### trace-sdk-application-types: Map SDK application types and fields

**Type:** `explore`
**Model:** *(default)*
**When:** You need to understand the complete structure of Unit SDK application types — every field, sub-type, and serialization detail — typically before modifying the SDK for a new Unit API version.

**Prompt:**

> Map the complete structure of application types in the Truss Unit Python SDK fork at `unit-python-sdk/`.
>
> 1. **Request types**: Read `unit-python-sdk/unit/models/application.py`. For each request class (`CreateIndividualApplicationRequest`, `CreateBusinessApplicationRequest`):
>    - Document every field with its type and whether it's required or optional
>    - Read the `to_json_api()` method to understand exactly how each field is serialized
>    - Note any conditional fields (e.g., sole_proprietorship flag changes which fields are included)
>
> 2. **DTO types**: In the same file, read `IndividualApplicationDTO` and `BusinessApplicationDTO`:
>    - Document the response structure (id, type, attributes)
>    - Document how the DTO is constructed from JSON API responses
>
> 3. **Sub-types**: Find and read the definitions of `FullName`, `Phone`, `Address`, `Officer`, `BeneficialOwner`, `BusinessContact`. These may be in `unit/models/application.py` or imported from other model files. Document their fields.
>
> 4. **Codec mapping**: Read `unit-python-sdk/unit/models/codecs.py`:
>    - Find the `mappings` dict
>    - Document which type strings map to which DTO classes for applications
>    - Understand how `DtoDecoder.decode()` routes responses
>
> 5. **Resource methods**: Read `unit-python-sdk/unit/api/application_resource.py`:
>    - Document each method (create, get, list, update, upload, approve_sb)
>    - Note the URL patterns used for each method
>    - Document return types
>
> Return:
> - Complete field schema for each request type (field name, type, required/optional, serialized JSON key)
> - Complete field schema for each DTO type
> - Sub-type field schemas
> - Codec type string → class mapping for applications
> - Resource method signatures and URL patterns

### audit-sdk-for-v2-migration: Identify SDK changes needed for Unit API v2

**Type:** `explore`
**Model:** *(default)*
**When:** You are preparing to update the Unit SDK fork to support a new version of the Unit applications API and need to identify what must change.

**Prompt:**

> Audit the Truss Unit Python SDK fork for changes needed to support Unit Applications API v2. The SDK is at `unit-python-sdk/`.
>
> 1. **Current application code**: Read these files completely:
>    - `unit-python-sdk/unit/models/application.py` — all DTOs and request types
>    - `unit-python-sdk/unit/api/application_resource.py` — all API methods
>    - `unit-python-sdk/unit/models/codecs.py` — type mappings
>    - `unit-python-sdk/unit/__init__.py` — client resource initialization
>
> 2. **SDK patterns for other resources**: Read 2-3 other resource/model pairs to understand how the SDK handles different resource types. This helps identify reusable patterns:
>    - Pick resources that have complex nested types (like `payment.py` or `account.py`)
>
> 3. **Test patterns**: Read `unit-python-sdk/e2e_tests/application_test.py` to understand how application tests are structured.
>
> 4. **How the API repo consumes the SDK**: Read these files to understand what the API repo depends on:
>    - `api/src/api/operations/account/onboarding/application/submit_onboarding_application.py`
>    - `api/src/api/utils/integrations/unit/unit.py` (unit_api_call wrapper)
>
> Return:
> - List of files that need modification
> - For each file, what specifically needs to change (new classes, modified methods, new mappings)
> - Backward compatibility concerns (can v1 and v2 coexist?)
> - Recommended approach: separate v2 classes vs. version parameter vs. extending existing classes
> - API repo callsites that reference SDK types and would need updating
