from unit.api.base_resource import BaseResource
from unit.models import UnitResponse, UnitError, RawUnitObject
from unit.models.codecs import DtoDecoder
from unit.models.payment import CreateAchStopPaymentRequest
from typing import Union


class AchStopPaymentResource(BaseResource):
    def __init__(self, api_url, token):
        super().__init__(api_url, token)
        self.resource = "stop-payments"

    def create(self, request: CreateAchStopPaymentRequest) -> Union[UnitResponse[RawUnitObject], UnitError]:
        payload = request.to_json_api()
        response = super().post(f"{self.resource}", payload)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[RawUnitObject](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def list(self) -> Union[UnitResponse[RawUnitObject], UnitError]:
        response = super().get(f"{self.resource}")
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[RawUnitObject](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def disable(self, stop_payment_id: str) -> Union[UnitResponse[RawUnitObject], UnitError]:
        response = super().post(f"{self.resource}/{stop_payment_id}/disable")
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[RawUnitObject](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())
