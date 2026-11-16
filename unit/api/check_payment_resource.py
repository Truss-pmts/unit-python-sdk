from unit.api.base_resource import BaseResource
from unit.models.authorization_request import *
from unit.models.check_payment import (
    ApproveCheckPaymentRequest,
    CheckPaymentDTO,
    CheckPaymentImageKind,
    CheckPaymentImageSide,
    ReturnCheckPaymentRequest,
)
from unit.models.codecs import DtoDecoder
from unit.models.payment import CreateCheckPaymentRequest


class CheckPaymentResource(BaseResource):
    def __init__(self, api_url, token):
        super().__init__(api_url, token)
        self.resource = "check-payments"

    def get(self, check_payment_id: str) -> Union[UnitResponse[CheckPaymentDTO], UnitError]:
        response = super().get(f"{self.resource}/{check_payment_id}")
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[check_payment_id](DtoDecoder.decode(data), None)

    def get_image(
        self,
        check_payment_id: str,
        side: CheckPaymentImageSide,
        image_type: CheckPaymentImageKind,
    ) -> Union[UnitResponse[bytes], UnitError]:
        response = super().get(f"{self.resource}/{check_payment_id}/{side}/{image_type}")
        if response.status_code == 200:
            return UnitResponse[bytes](response.content, None)
        else:
            return UnitError.from_json_api(response.json())

    def approve(self, request: ApproveCheckPaymentRequest) -> Union[UnitResponse[CheckPaymentDTO], UnitError]:
        payload = request.to_json_api()
        response = super().post(f"{self.resource}/{request.check_payment_id}/approve", payload)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CheckPaymentDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def create(self, request: CreateCheckPaymentRequest, timeout: float = None) -> Union[UnitResponse[CheckPaymentDTO], UnitError]:
        payload = request.to_json_api()
        response = super().post(f"{self.resource}", payload, timeout=timeout)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CheckPaymentDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def cancel(self, check_payment_id: str) -> Union[UnitResponse[CheckPaymentDTO], UnitError]:
        response = super().post(f"{self.resource}/{check_payment_id}/cancel")
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CheckPaymentDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def reprocess(self, check_payment_id: str) -> Union[UnitResponse[CheckPaymentDTO], UnitError]:
        # Unit accepts this only while the check is MarkedForReturn for NotSufficientFunds
        # and the account has been funded first (Unit support, Zendesk case 169500).
        response = super().post(f"{self.resource}/{check_payment_id}/reprocess")
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CheckPaymentDTO](data=DtoDecoder.decode(payload=data), included=None)
        else:
            return UnitError.from_json_api(data=response.json())

    def return_check(self, request: ReturnCheckPaymentRequest) -> Union[UnitResponse[CheckPaymentDTO], UnitError]:
        payload = request.to_json_api()
        response = super().post(f"{self.resource}/{request.check_payment_id}/return", payload)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CheckPaymentDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())
