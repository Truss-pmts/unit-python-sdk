from unit.api.base_resource import BaseResource
from unit.models.payment import *
from unit.models.codecs import DtoDecoder


class WireResource(BaseResource):
    def __init__(self, api_url, token):
        super().__init__(api_url, token)
        self.resource = "wire"

    def simulate_incoming(self, request: SimulateIncomingWireRequest, timeout: float = None) -> Union[UnitResponse[WirePaymentDTO], UnitError]:
        payload = request.to_json_api()
        response = super().post("sandbox/wire-payments", payload, timeout=timeout)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[WirePaymentDTO](data=DtoDecoder.decode(data), included=None)
        else:
            return UnitError.from_json_api(data=response.json())

    def simulate_transmit(self, request: SimulateTransmitWireRequest, timeout: float = None) -> Union[UnitResponse[WirePaymentDTO], UnitError]:
        payload = request.to_json_api()
        response = super().post(f"sandbox/{self.resource}/transmit", payload, timeout=timeout)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[WirePaymentDTO](data=DtoDecoder.decode(data), included=None)
        else:
            return UnitError.from_json_api(data=response.json())
